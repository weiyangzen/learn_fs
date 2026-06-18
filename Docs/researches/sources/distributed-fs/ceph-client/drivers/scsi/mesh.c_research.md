# sources/distributed-fs/ceph-client/drivers/scsi/mesh.c

## Purpose
`mesh.c` is the Linux SCSI low-level driver for the Macintosh Enhanced SCSI Hardware controller found in old Power Macintosh systems. It binds a `macio` Open Firmware device, maps the MESH register block and its DBDMA engine, initializes and optionally resets the SCSI bus, queues SCSI mid-layer commands, drives a SCSI phase/message state machine, builds DBDMA descriptor lists for data transfer, handles reselection and synchronous-transfer negotiation, and exposes suspend/resume, shutdown, remove, and module registration paths.

## Important APIs, Types, And Functions
The driver-private runtime model is `struct mesh_state`, which stores MMIO register pointers, IRQs, the owning `Scsi_Host`, request queue links, current bus phase, message buffers, current target, DMA command memory, per-target state, and `macio`/PCI device pointers. Per-target state is in `struct mesh_target`, with SDTR state, negotiated sync parameters, saved data pointer, direction guess, and disconnected command pointer.

SCSI mid-layer entry points are collected in `mesh_template`: `mesh_queue`, `mesh_abort`, and `mesh_host_reset`, with `can_queue = 20`, host ID 7, `SG_ALL`, `cmd_per_lun = 2`, `max_segment_size = 65535`, and `cmd_size = sizeof(struct mesh_cmd_priv)`.

Lifecycle and platform integration are handled by `mesh_probe()`, `mesh_remove()`, `mesh_shutdown()`, optional `mesh_suspend()`/`mesh_resume()`, `set_mesh_power()`, `init_mesh()`, `exit_mesh()`, `mesh_match`, and `mesh_driver`.

Core command flow is split across `mesh_queue_lck()`, `mesh_start()`, `mesh_start_cmd()`, `start_phase()`, `mesh_interrupt()`, `cmd_complete()`, `phase_mismatch()`, `handle_error()`, `handle_exception()`, `handle_msgin()`, `reselected()`, `mesh_done()`, and reset/recovery helpers `handle_reset()`, `do_abort()`, and `mesh_host_reset()`.

DMA setup and teardown are implemented by `set_dma_cmds()` and `halt_dma()`. Sync-transfer negotiation is implemented by `add_sdtr_msg()` and `set_sdtr()`. Diagnostics are provided by `mesh_dump_regs()` and conditional `MESH_DBG` logging helpers.

## Control Flow
Module initialization clamps `sync_rate`, translates it into `mesh_sync_period` and `mesh_sync_offset`, then registers `mesh_driver` with the macio bus. Probe validates two resources and two IRQs, requests resources, allocates a SCSI host with `struct mesh_state` hostdata, maps controller and DBDMA register windows, allocates coherent DBDMA command memory, initializes all target negotiation state to asynchronous/`do_sdtr`, reads `clock-frequency` from the device tree or assumes 50 MHz, powers up the chip, calls `mesh_init()`, requests the MESH interrupt, registers the SCSI host, and scans.

`mesh_init()` stops DBDMA, clears hardware exception/error bits, resets the controller, programs interrupt masks, source ID, selection timeout, and async sync parameters, optionally asserts SCSI RST for `init_reset_delay`, flushes the FIFO, enables reselection, and returns the software phase machine to idle.

Command submission enters `mesh_queue_lck()` with the SCSI host lock held. The command is appended to the driver's singly linked `request_q` through `cmd->host_scribble`; if the bus is idle, `mesh_start()` chooses the first queued command whose target has no active/disconnected request. `mesh_start_cmd()` initializes transfer counters and message state, records target direction and current request, handles a busy bus or pending reselection, disables reselection around arbitration to avoid a known MESH race, starts `SEQ_ARBITRATE`, and applies a controller reset workaround if arbitration appears hung during a target reselection.

The phase machine starts at selection and advances through message-out, command, data, status, message-in, bus-free, and disconnect states. `start_phase()` translates the current software phase into MESH sequence commands and register writes: select with ATN, push CDB bytes into the FIFO, build and run DBDMA descriptors for data phases, fetch status, send or receive messages, or wait for bus free. `cmd_complete()` consumes command-done interrupts and either continues fragmented message I/O, records status from the FIFO, halts DMA when a data chunk finishes, moves to the next phase, completes disconnected commands, or starts the next queued command after bus free.

`phase_mismatch()` is the adaptive branch of the state machine. It samples SCSI bus phase bits, drains message-in bytes when needed, halts DMA on phase change, flushes residual FIFO data, updates direction on data phases, sends pending messages, and restarts the appropriate hardware sequence. Message handling supports command complete, SDTR negotiation and reject fallback, save/restore pointers, disconnect, abort, NOP, and identify messages on reselection.

Interrupt handling loops while the MESH interrupt register is nonzero. Error interrupts take precedence, then exceptions, then command-done. SCSI reset errors complete all active and queued commands with `DID_RESET` and reset target negotiation. Unexpected disconnect maps to `DID_ABORT` unless it is actually a reselection. Parity errors either request message parity retry or set `DID_PARITY`. Sequence errors can be converted into reselection or phase-mismatch handling when hardware reports those conditions. Exceptions handle reselection, arbitration loss, selection timeout, phase mismatch, and unknown conditions by aborting.

Reselection can happen from idle, arbitration, bus-free, or disconnecting states. The driver may requeue the command that lost arbitration, extracts the target ID from FIFO reselection data, restores the target's current command and saved data pointer, programs negotiated sync parameters, then resumes with message-in. Bogus reselection data or missing commands force an abort message path.

## State And Persistence
The driver has no filesystem persistence. Module parameters (`sync_rate`, `sync_targets`, `resel_targets`, `debug_targets`, and `init_reset_delay`) tune runtime behavior at load time. Hardware state is programmed into volatile MESH, DBDMA, and SCSI-bus registers; sync negotiation and target state are rebuilt after reset, resume, or module reload.

`struct mesh_state` persists for the lifetime of the macio device binding and owns the command queue, current request, phase machine, message buffers, DMA command allocation, and target array. `struct mesh_target` persists per target and keeps a disconnected command pointer plus `saved_ptr` for save/restore pointer messages. `struct mesh_cmd_priv` is allocated by the SCSI core per command and records residual, status, and message values that are copied into the final `scsi_cmnd` result in `mesh_done()`.

The request queue reuses `scsi_cmnd.host_scribble`; this means no other layer may depend on that field while the command is queued in this driver. DMA state is transient: `set_dma_cmds()` maps the SCSI SG list with `scsi_dma_map()`, writes DBDMA descriptors, and `halt_dma()` updates `data_ptr` and unmaps with `scsi_dma_unmap()`.

## Dependencies And Integration Points
The file depends on Linux SCSI mid-layer APIs, macio/Open Firmware device matching, PowerMac feature control, PCI DMA coherent allocation, DBDMA register definitions from `<asm/dbdma.h>`, I/O accessors (`in_8`, `out_8`, `in_le32`, `out_le32`), IRQ handling, spinlocks, sleep/delay helpers, and PowerMac platform detection. It includes `mesh.h` for register layout, sequence bits, bus phase constants, interrupt/error bits, and command-private state.

The macio core calls probe/remove/shutdown and power-management callbacks. The SCSI core calls queue, abort, and host reset handlers and owns host locking around queued commands. The IRQ core calls `do_mesh_interrupt()`, which takes `host_lock` before running the phase machine. Platform firmware provides `clock-frequency` and resources/IRQs through the OF node.

## Risks And Edge Cases
The driver has many hardware-specific timing loops and microsecond waits. Arbitration, message-out ATN timing, reselection, FIFO drain, and SCSI reset behavior rely on old MESH quirks and fixed delays; small ordering changes can break legacy hardware.

`set_dma_cmds()` uses `BUG_ON(nseg < 0)` for DMA mapping failure and panics if any SG element is at least 64 KiB, so resource pressure or unexpected SG geometry can crash the kernel instead of failing a command. The DBDMA descriptors store 32-bit physical addresses and use `virt_to_phys()` for command pointer programming and the static overrun buffer, making architecture/DMA assumptions important.

Queueing relies on `cmd->host_scribble` and host-lock serialization. Any future path touching the queue without the SCSI host lock risks list corruption. Abort handling is explicitly incomplete and always returns `FAILED`, so recovery escalates to host reset.

The data pointer can be modified by target messages, halted DMA residue, and overrun fallback buffers. Incorrect accounting can produce wrong residuals, duplicate unmaps, or resumed disconnected transfers at the wrong SG offset.

Shutdown and probe-error paths reset the SCSI bus to avoid leaving devices in synchronous mode for MacOS. This is intentional but disruptive; error injection around probe can reset shared devices on the bus.

## Test Signals
Build coverage should include `CONFIG_SCSI_MESH`, `CONFIG_PM`, and PowerPC/macintosh platform headers to validate macio, DBDMA, and SCSI API compatibility. Probe tests on supported Open Firmware nodes should verify two resources/two IRQs, register mapping, coherent DBDMA allocation, IRQ request, SCSI host registration, and resource cleanup at every failure label.

I/O testing should cover no-data commands, reads, writes, multi-segment SG lists under 64 KiB per element, residual accounting, disconnect/reselection with save/restore pointer messages, and selection timeouts. Negotiation tests should cover async mode, successful SDTR, rejected SDTR, target masks from `sync_targets` and `resel_targets`, and bus reset resetting all target sync state. Recovery tests should induce parity errors, unexpected disconnects, sequence errors, phase mismatches, arbitration loss, host reset, suspend/resume, shutdown, and module unload.
