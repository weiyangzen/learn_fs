# sources/distributed-fs/ceph-client/drivers/scsi/qlogicpti.c

## Purpose
`qlogicpti.c` is the SBUS platform driver for Performance Technologies and QLogic ISP SCSI adapters on SPARC systems. It loads ISP1000 firmware, initializes adapter mailbox and DMA queues, translates SCSI commands into firmware request entries, handles firmware response entries, and integrates with the SCSI mid-layer and Open Firmware platform probing.

## Important APIs, Types, And Functions
The platform lifecycle is `qpti_sbus_probe()` and `qpti_sbus_remove()` through `module_platform_driver()`. Hardware setup flows through `qpti_map_regs()`, `qpti_register_irq()`, `qpti_get_scsi_id()`, `qpti_get_bursts()`, `qpti_get_clock()`, `qpti_map_queues()`, `qlogicpti_load_firmware()`, `qlogicpti_verify_tmon()`, and `qlogicpti_reset_hardware()`. Mailbox communication is centralized in `qlogicpti_mbox_command()`. SCSI integration is `qpti_template`, with `qlogicpti_queuecommand()`, `qlogicpti_sdev_configure()`, `qlogicpti_abort()`, and `qlogicpti_reset()`.

Command construction helpers are `marker_frob()`, `cmd_frob()`, `load_cmd()`, and `update_can_queue()`. Interrupt completion is handled by `qpti_intr()`, `qlogicpti_intr_handler()`, and `qlogicpti_return_status()`. Global adapter chaining uses `qpti_chain_add()` and `qpti_chain_del()`.

## Control Flow
Probe rejects devices with IRQ zero, allocates a SCSI host plus `struct qlogicpti`, maps registers, requests a shared IRQ, reads Open Firmware initiator ID, burst sizes, and clock, allocates coherent request/response rings, loads firmware from `qlogic/isp1000.bin`, checks PTI environmental status when applicable, resets hardware, initializes firmware queues and target parameters, adds the SCSI host, links the adapter into the global chain, and scans.

Queueing reads the firmware request out pointer from `MBOX4`, reserves request ring entries, optionally emits a `SYNC_ALL` marker after reset events, fills a command entry from the SCSI CDB, maps scatter-gather data, writes continuation entries for more than four SG segments, stores the SCSI command in `cmd_slots[handle]`, increments per-target command count, updates `MBOX4`, and adjusts mid-layer queue/SG limits. Interrupt handling checks `SBUS_STAT_RINT`, reads the response producer pointer from `MBOX5`, acknowledges firmware interrupts, handles async reset/error mailbox events, walks response entries, looks up commands by handle, copies sense data, maps completion status to SCSI result, unmaps DMA, decrements command counts, advances `MBOX5`, chains completions through `host_scribble`, and calls `scsi_done()` after the ring walk.

## State And Persistence
Persistent host-side state is runtime-only: MMIO mappings, coherent request/response queues and DVMA addresses, queue indices, firmware version fields, target parameters, command slots, per-target command counts/tag-age timestamps, Open Firmware-derived IDs and clock/burst settings, PTI status-register shadow, and flags such as `send_marker`, `ultra`, `differential`, and `is_pti`. Firmware is loaded into adapter RAM on probe but not persisted across reset/power cycles. The global `qptichain` records live adapters for module lifetime.

## Dependencies And Integration Points
The driver depends on SPARC SBUS/Open Firmware APIs, platform devices, IRQs, coherent DMA allocation, firmware loading, SCSI mid-layer command and error handling, and register/entry definitions from `qlogicpti.h`. It integrates with firmware through mailbox commands, request/response rings, and async events. Device-tree match names include `ptisp`, `PTI,ptisp`, `QLGC,isp`, and `SUNW,isp`.

## Risks And Edge Cases
Mailbox waits are bounded by loop counts but often only log timeout and continue, so partial hardware failure can cascade. `qlogicpti_mbox_command()` indexes `mbox_param[param[0]]` before an explicit bounds check, so callers must pass valid command codes. `load_cmd()` maps SG data before verifying enough continuation slots for every segment; on queue exhaustion it can return failure after mapping, so DMA-unmap behavior is a risk. The abort path searches all command slots and does not explicitly handle a not-found command before building the cookie. Queue-depth adjustment contains a large workaround subtraction and can affect SG limits under pressure. Firmware load is word-by-word mailbox I/O, making probe slow and sensitive to firmware availability and checksum correctness.

## Test Signals
Signals include platform match/probe for PTI and QLGC names, missing firmware failure, checksum failure, successful firmware version reporting, differential/single-ended and Ultra/Fast messages, coherent queue allocation/free on probe failure and remove, target parameter programming in `sdev_configure()`, marker insertion after bus reset async events, SG continuation handling at 4, 5, and large SG counts, queue-full/toss-command behavior, status mapping for all completion codes, sense copy on `SF_GOT_SENSE`, abort and bus reset mailbox commands, shared IRQ behavior, and clean remove with IRQ, DMA, and MMIO resources released.
