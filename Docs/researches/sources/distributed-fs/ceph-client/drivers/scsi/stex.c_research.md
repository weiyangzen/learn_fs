<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/stex.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/stex.c

## Purpose
`stex.c` implements the PCI SCSI host driver for Promise SuperTrak EX and related Promise/SymplyStor RAID controllers. It exposes logical arrays through the Linux SCSI mid-layer, owns controller handshake/reset/power-management paths, and translates SCSI commands into Promise request/status queue messages.

## Important APIs, Types, And Functions
The core state is `struct st_hba`, which holds MMIO mappings, coherent request/status memory, queue indices, card type, CCB table, reset workqueue, waitqueue, and Promise-specific callbacks. `struct st_ccb` binds a SCSI command to a firmware request, sense buffer, SG count, and returned SRB/SCSI status. `struct req_msg`, `struct status_msg`, `struct st_msg_header`, and `struct handshake_frame` are the firmware wire formats.

The SCSI-facing entry points are `stex_queuecommand()`, `stex_sdev_configure()`, `stex_abort()`, `stex_reset()`, and `stex_biosparam()` in `driver_template`. PCI lifecycle is handled by `stex_probe()`, `stex_remove()`, `stex_shutdown()`, `stex_suspend()`, and `stex_resume()`. Interrupt paths split between legacy/common controllers (`stex_intr()`, `stex_mu_intr()`) and SS/Yel/P3-style controllers (`stex_ss_intr()`, `stex_ss_mu_intr()`). Firmware setup/reset flows are `stex_common_handshake()`, `stex_ss_handshake()`, `stex_handshake()`, `stex_do_reset()`, `stex_yos_reset()`, `stex_hard_reset()`, `stex_ss_reset()`, and `stex_p3_reset()`.

## Control Flow
Module init registers `stex_pci_driver`. Probe enables PCI, maps BAR0, sets a 64-bit or 32-bit DMA mask, chooses `st_card_info`, allocates one coherent DMA region containing request slots, optional scratch space, status slots, and copy buffers, allocates CCBs, requests IRQ/MSI, performs the firmware handshake, then registers and scans a SCSI host.

`stex_queuecommand_lck()` rejects commands while disconnected or reset, locally emulates some management-visible commands (`MODE_SENSE_10` caching page, console-device `INQUIRY`/`TEST_UNIT_READY`, driver-version passthrough), allocates the next request ring slot, maps SG entries, stores the SCSI command in the tag-indexed CCB, and rings the appropriate controller doorbell. Interrupt handlers drain status entries, validate tags/payload sizes, copy sense or data payloads, unmap DMA, translate SRB/SCSI status through `stex_scsi_done()`, and complete the SCSI command. Reset work may be queued from firmware reset-request bits or SCSI EH; it serializes through `mu_status` and `reset_waitq`, fails outstanding commands with `DID_RESET`, re-handshakes, and wakes waiters.

## State And Persistence Behavior
Runtime state is volatile driver/controller state: coherent request/status queues, queue head/tail indices, `out_req_cnt`, CCB slots, `mu_status`, MSI state, PM support, and `S6flag` from the reboot notifier. No disk persistence is maintained by the driver; durable storage state is owned by the RAID firmware. Suspend/shutdown paths send management CDBs (`CTLR_SHUTDOWN`, `PMIC_SHUTDOWN`, or power-state commands) and set `MU_STATE_STOP`.

## Dependencies And Integration Points
The driver integrates with PCI, DMA mapping, the SCSI host template, block queue timeouts, SCSI EH, MSI/IRQ APIs, reboot notifiers, and Promise firmware MMIO doorbells. It depends on card-specific register layouts and request formats selected by `st_card_info`. It also exposes a synthetic Promise RAID console target at `host->max_id - 1`.

## Risks
Important risks include tag/ring corruption, invalid firmware status heads, completion for stale CCBs, reset races while interrupts return pending commands, coherent DMA sizing for large controller families, and different semantics between legacy and SS/P3 doorbells. `scsi_dma_map()` failures are guarded with `BUG_ON(nseg < 0)`, so unexpected DMA map failures are fatal. Abort tries to poll pending interrupts before failing, which can race with normal interrupt completion. Reboot notifier registration is global while the driver can bind multiple devices.

## Test Signals
Useful signals include probe failure injection at each allocation/mapping/IRQ/handshake step, 32-bit and 64-bit DMA mask coverage, MSI and shared IRQ paths, command completion with valid and invalid tags, passthrough driver-version and adapter-info commands, console target behavior, lost-interrupt abort handling, firmware-requested reset, SCSI EH host reset, remove with outstanding I/O, suspend/resume/shutdown PM commands for PM-capable and non-PM cards, and queue-depth/tag boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/stex.c -->
