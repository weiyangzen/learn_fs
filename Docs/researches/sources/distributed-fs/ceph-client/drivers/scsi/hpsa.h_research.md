# sources/distributed-fs/ceph-client/drivers/scsi/hpsa.h

## Purpose

`hpsa.h` is the private controller and host-state header for the HP Smart Array SAS driver. It defines the `ctlr_info` controller object, discovered-device records, SAS transport helper structures, reply queue buffers, BMIC controller-parameter payloads, controller event flags, reset constants, MMIO register offsets, and inline access-method implementations for simple, performant, and I/O accelerator controller modes.

## Important APIs, Types, and Functions

- `struct access_method` abstracts hardware submission, interrupt masking, pending-interrupt detection, and completion retrieval through `submit_command`, `set_intr_mask`, `intr_pending`, and `command_completed`.
- `struct hpsa_scsi_dev_t` is the driver's discovered-device model. It carries OS-visible bus/target/LUN, hardware SCSI-3 address, VPD/device ID data, SAS address, RAID level/offline status, queue-depth counters, reset state, I/O accelerator handles and offload flags, RAID map data, physical-disk backpointers for logical volumes, abort support, SAS port linkage, and external-array status.
- `struct ctlr_info` is the main per-controller state. It stores PCI/MMIO identity, command limits, interrupt mode, SCSI host pointer, device table protected by `devlock`, command/error DMA pools, scan wait state, performant-mode transition tables, reply queues, block-fetch tables, accelerator support, heartbeat/lockup monitoring fields, delayed work items, IRQ names/queue IDs, task-management support bits, event flags, offline-device list, reset locks, SAS host, and workqueues.
- `struct reply_queue_buffer` tracks a DMA-visible reply queue head, bus address, current index, size, and wrap bit.
- Static access methods include `SA5_submit_command*()`, `SA5_intr_mask()`, `SA5B_intr_mask()`, `SA5_performant_intr_mask()`, `SA5_completed()`, `SA5_performant_completed()`, `SA5_ioaccel_mode1_completed()`, and interrupt-pending helpers.
- Prebuilt `struct access_method` instances (`SA5_access`, `SA5B_access`, `SA5_performant_access`, `SA5_ioaccel_mode1_access`, `SA5_ioaccel_mode2_access`, etc.) bind board families or transport modes to the proper register protocol.
- `struct board_type` maps PCI board IDs to product names and access methods.

## Control Flow and State

The header's inline control flow is the low-level command/completion path. Submission writes a command bus address to the request port, sometimes followed by a scratchpad read to flush posted writes. Interrupt mask functions invert the controller-specific semantics where zero enables and mode-specific bits disable interrupts. Simple completion reads the reply port and decrements `commands_outstanding` for non-empty entries. Performant completion consumes entries from `reply_queue[q]`, validates the wrap bit in the low reply word, clears outbound doorbell state for non-MSI/MSI-X use, advances `current_entry`, toggles `wraparound` at the queue end, and decrements outstanding commands. I/O accelerator mode 1 completion uses a ring entry value of `IOACCEL_MODE1_REPLY_UNUSED`, clears consumed entries, writes the consumer index, and maintains the same outstanding-command accounting.

Persistent runtime state is memory resident in `ctlr_info` and `hpsa_scsi_dev_t`; it is rebuilt during probe and discovery rather than persisted to disk. The driver does cache controller firmware capabilities, task-management flags, event bits, heartbeat samples, device offload configuration, offline-device entries, and SAS topology structures across workqueue ticks while the controller is bound.

## Dependencies and Integration Points

`hpsa.h` depends on Linux SCSI/SAS, PCI, DMA, workqueue, waitqueue, atomic, spinlock, and MMIO primitives supplied by surrounding driver includes, plus command ABI definitions from `hpsa_cmd.h`. It integrates with the HPSA C implementation that allocates command pools, fills CISS command records, handles SCSI mid-layer callbacks, drives SAS transport registration, monitors controller events, performs rescans, handles resets, and chooses an `access_method` from the board table.

## Risks

- The inline MMIO functions encode hardware-specific ordering requirements; removing readbacks or write memory barriers can create lost commands or stale completions on posted-write architectures.
- Completion accounting relies on every non-empty completion decrementing `commands_outstanding`; mismatches can break lockup detection, reset waits, or queue throttling.
- `hpsa_scsi_dev_t` mixes logical-volume, physical-disk, SAS, and I/O accelerator state, so discovery/rescan changes must preserve lock discipline around `devlock`, reset flags, and physical-disk reference arrays.
- Reply queue wrap handling assumes `h->max_commands` matches the allocated performant queue depth, while I/O accelerator mode 1 uses `rq->size`; mode confusion would corrupt ring traversal.
- Controller event flags trigger rescans and offload reconfiguration. Missed event bits can leave stale topology or accelerator maps.

## Test Signals

- Build coverage with HPSA enabled verifies that command ABI types and controller fields match the implementation.
- Probe tests should exercise simple, performant, and I/O accelerator-capable boards, confirming interrupt enable/disable and command completion under MSI-X and non-MSI modes.
- Runtime signals include stable `commands_outstanding`, no reply queue wrap stalls, successful discovery of logical/physical devices, SAS transport objects, rescan on event bits, and clean controller reset/abort behavior.
- Fault-injection or hardware tests should cover controller lockup detection, offline-device handling, I/O accelerator disable/config-change events, and task-management support flag parsing.
