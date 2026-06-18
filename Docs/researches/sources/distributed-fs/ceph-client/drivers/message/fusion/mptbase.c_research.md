# sources/distributed-fs/ceph-client/drivers/message/fusion/mptbase.c

## Purpose

`mptbase.c` is the common Fusion MPT base driver for LSI/Brocade MPI-1-era adapters. It owns the PCI-facing IOC lifecycle, memory-mapped register access, request/reply frame pools, interrupt dispatch, doorbell handshakes, IOC reset/recovery, configuration page transactions, event notification, firmware upload/download-boot support, procfs summaries, and callback registration used by protocol drivers.

The file is not a standalone SCSI transport driver. It is the shared substrate used by SPI, FC, SAS, LAN, ioctl, and target-mode modules under `drivers/message/fusion`. Those protocol modules register callbacks with this base layer, then obtain and post MPT request frames through it.

## Important APIs, Types, and Globals

- Module parameters: `mpt_msi_enable_spi`, `mpt_msi_enable_fc`, `mpt_msi_enable_sas`, `mpt_channel_mapping`, `mpt_debug_level`, and exported `mpt_fwfault_debug`.
- Global adapter registry: exported `ioc_list` tracks all live `MPT_ADAPTER` instances.
- Callback tables: `MptCallbacks`, `MptDriverClass`, `MptEvHandlers`, `MptResetHandlers`, `MptDeviceDriverHandlers`, plus callback names in `MptCallbacksName`.
- Base callback index: `mpt_base_index` is allocated during `fusion_init()` and used for internal EventNotification, EventAck, Config, and SAS IO Unit Control requests.
- Important header-defined types used throughout:
  - `MPT_ADAPTER`: per-IOC state, PCI mappings, DMA pools, queue state, bus-specific cached config, workqueues, reset flags, and management command mailboxes.
  - `MPT_FRAME_HDR`: union overlay for MPI request/reply headers and frame tracking metadata.
  - `MPT_MGMT`: serialized management command state with mutex, completion, reply buffer, sense buffer, and status bits.
  - `CONFIGPARMS`: generic config page request descriptor consumed by `mpt_config()`.
  - `MPT_CALLBACK`, `MPT_EVHANDLER`, `MPT_RESETHANDLER`, and `struct mpt_pci_driver`: integration contracts for protocol modules.

Exported API surface includes `mpt_attach()`, `mpt_detach()`, PM hooks when enabled, callback registration/deregistration, device-driver hook registration, `mpt_get_msg_frame()`, `mpt_put_msg_frame()`, `mpt_put_msg_frame_hi_pri()`, `mpt_free_msg_frame()`, `mpt_send_handshake_request()`, `mpt_verify_adapter()`, `mpt_GetIocState()`, `mpt_print_ioc_summary()`, reset handlers, `mpt_config()`, firmware memory helpers, RAID discovery helpers, and SAS persistent table operations.

## Control Flow

### Module and Adapter Bring-Up

`fusion_init()` clears all callback tables, registers `mptbase_reply()` as the base callback, registers `mpt_ioc_reset()` as the base reset callback, and creates procfs entries when configured. Protocol modules later call `mpt_register()` and related registration APIs.

`mpt_attach()` is the PCI adapter attach path called by protocol-specific PCI drivers. It allocates `MPT_ADAPTER`, maps PCI MMIO via `mpt_mapresources()`, chooses 32-bit or 64-bit SGE helpers, initializes locks/completions/workqueues, classifies bus type from PCI device ID, sets MSI preference, disables IO access for affected 1064-family errata, inserts the IOC into `ioc_list`, binds dual-function peer ports through `mpt_detect_bound_ports()`, allocates firmware event/reset workqueues, and calls `mpt_do_ioc_recovery(..., MPT_HOSTEVENT_IOC_BRINGUP, ...)`.

`mpt_do_ioc_recovery()` is the central bring-up/recovery state machine:

1. Disable interrupts and mark the IOC inactive.
2. Coordinate with `alt_ioc` for bound dual-port chips.
3. Call `MakeIocReady()` to reach READY, using message-unit reset or diagnostic reset as needed.
4. Fetch IOC/port facts via doorbell handshake.
5. On bring-up, request IRQ/MSI.
6. Allocate/prime request, reply, sense, and chain pools with `PrimeIocFifos()`.
7. Send `IOCInit` and `PortEnable`, then wait for OPERATIONAL.
8. Optionally upload firmware for download-boot capable adapters.
9. Enable event notification.
10. Mark active and enable reply interrupts.
11. Perform bus-specific post-init: SAS persistent table cleanup and RAID discovery, FC LAN config fetch, SPI NVRAM/config page reads, IOC coalescing updates, IO Unit Page 2 BIOS version, and manufacturing page 0 board identity.

Protocol-specific `probe()` hooks registered through `mpt_device_driver_register()` are called after the base IOC is operational.

### Request/Reply Path

Protocol drivers call `mpt_get_msg_frame()` to remove a frame from `ioc->FreeQ`. The function stamps the callback index and request index into `MsgContext`, initializes per-request narrow/buffer metadata, and returns `NULL` if the IOC is inactive or no frames are free.

Requests are posted with `mpt_put_msg_frame()` to `RequestFifo` or `mpt_put_msg_frame_hi_pri()` to `RequestHiPriFifo`. Both recompute the request index from the frame address before writing the low DMA address and addressing bits into the IOC FIFO.

`mpt_interrupt()` drains `ReplyFifo` until `0xFFFFFFFF`. Replies with `MPI_ADDRESS_REPLY_A_BIT` are normal reply frames processed by `mpt_reply()`. Other values are turbo/context replies processed by `mpt_turbo_reply()`. Both paths recover the original request frame, derive the callback index, log IOC status/log-info when present, call the registered protocol callback, and free the original request frame when the callback asks for it. Normal replies are returned to the IOC by writing the reply DMA token back to `ReplyFifo`.

Internal base-driver completions route through `mptbase_reply()`, which handles EventNotification, EventAck, Config, and SAS IO Unit Control replies. Config and SAS IO Unit Control replies complete `ioc->mptbase_cmds.done`.

### Doorbell Handshake and IOC State

Doorbell handshakes are used before normal queues are live and for some task-management flows. `mpt_handshake_req_reply_wait()` writes a handshake request word by word to the Doorbell register, waits for doorbell ACK/INT transitions, captures a 16-bit-at-a-time reply into `ioc->hs_reply`, then copies the reply out. `mpt_send_handshake_request()` is an exported request-only variant used by task management.

`WaitForDoorbellAck()`, `WaitForDoorbellInt()`, and `WaitForDoorbellReply()` implement the polling loops with either sleepable millisecond sleeps or busy delays. `mpt_GetIocState()` reads the Doorbell register, caches the masked state in `ioc->last_state`, and returns either raw or cooked state.

### Reset and Recovery

`mpt_fault_reset_work()` periodically checks the IOC. If the adapter is non-operational it flushes running SCSI commands and starts a kthread to remove the PCI device. If it is in FAULT it triggers `mpt_HardResetHandler()`. For SAS discovery quiesce, it clears `sas_discovery_quiesce_io` once discovery is complete.

`mpt_SoftResetHandler()` attempts a message-unit reset for non-FC adapters, notifies reset handlers, reprimes FIFOs, reinitializes the IOC, reenables events, and posts `MPT_IOC_POST_RESET` callbacks on success. `mpt_Soft_Hard_ResetHandler()` falls back to `mpt_HardResetHandler()`.

`mpt_HardResetHandler()` serializes through `taskmgmt_lock` and `ioc_reset_in_progress`, notifies protocol reset handlers for setup and post phases, invokes `mpt_do_ioc_recovery(..., MPT_HOSTEVENT_IOC_RECOVER, ...)`, and mirrors reset flags to any `alt_ioc`.

Low-level reset support is split across `MakeIocReady()`, `KickStart()`, `mpt_diag_reset()`, and `SendIocReset()`. Diagnostic reset uses the hardware write-sequence keys, handles SAS1078-specific reset register behavior, optionally reloads cached firmware through `mpt_downloadboot()`, clears reset-history, and resets cached EventState.

### Configuration, Events, and RAID/SAS Support

`mpt_config()` is the generic queued config transaction API. It rejects calls during reset or when the IOC is inactive/non-operational, serializes through `ioc->mptbase_cmds.mutex`, builds a Config request with a DMA SGE, waits for `mptbase_reply()`, updates the supplied page header on success, and triggers reset/retry when a command times out.

`SendEventNotification()` enables or disables firmware events by handshake. `ProcessEventNotification()` normalizes event data, updates cached EventState, logs RAID event information, stores selected events in the optional ioctl event ring, routes events to all registered event handlers, and sends EventAck when firmware requires it.

RAID and SAS helpers read config pages through `mpt_config()`: `mpt_findImVolumes()` caches IOC Page 2 and Page 3, `mpt_inactive_raid_volumes()` records physical disks belonging to inactive/failed volumes, `mpt_raid_phys_disk_pg0()` and `mpt_raid_phys_disk_pg1()` return physical disk pages, and `mpt_raid_phys_disk_get_num_paths()` returns path count. `mptbase_sas_persist_operation()` issues SAS IO Unit Control operations for persistent target-id table cleanup.

## State and Persistence Behavior

The driver persists runtime state in `MPT_ADAPTER`, not on disk. Important cached state includes IOC facts, port facts, firmware version/image size, product name, board manufacturing strings, BIOS version, FC LAN pages, SPI NVRAM/config page data, RAID IOC pages, inactive RAID component list, event log ring, and optional cached firmware image for download-boot recovery.

DMA-coherent allocations are long-lived per adapter: combined reply/request/chain pool in `ioc->alloc`, sense buffer pool, optional host page buffer, optional firmware cache, SPI IOC Page 4 buffer, and temporary buffers for config page reads. Request frames are host-managed through `FreeQ`; chain buffers through `FreeChainQ`.

Persistent hardware/NVRAM effects are possible. `mpt_read_ioc_pg_1()` may write current and NVRAM IOC Page 1 to clamp reply coalescing timeout. `mptbase_sas_persist_operation()` clears SAS persistent target mappings. Firmware download-boot writes firmware into adapter memory through programmed IO. Message-unit and diagnostic resets reset firmware event state and queue contents.

Detach/suspend paths disable interrupts, mark IOC inactive, free IRQ/MSI, release DMA allocations, clear procfs entries, remove list membership, unmap MMIO, disable PCI resources, and null `pci_set_drvdata()`. `fusion_exit()` only unregisters the base callback/procfs root; live adapters are expected to have been detached by PCI driver teardown.

## Dependencies and Integration Points

- Linux kernel subsystems: PCI, DMA mapping/coherent allocations, interrupts/MSI, workqueues, kthreads, completions, mutexes/spinlocks, procfs/seq_file, delay APIs, SCSI host private data, and optional PM.
- MPI/Fusion headers: `mptbase.h`, generated/LSI MPI message/config structures, `lsi/mpi_log_fc.h`, plus SAS/SPI/FC log/status constants.
- Protocol modules:
  - `mptspi.c`, `mptfc.c`, and `mptsas.c` call `mpt_attach()`/`mpt_detach()` from their PCI driver callbacks and register multiple reply contexts through `mpt_register()`.
  - `mptscsih.c` uses request frame APIs, reset handlers, and summary output for common SCSI host behavior.
  - `mptctl.c` uses config and request APIs for ioctl management.
  - `mptlan.c` registers LAN callbacks and uses frame APIs for LAN traffic.
- Hardware integration: register-level access through `SYSIF_REGS` MMIO/PIO fields: Doorbell, IntStatus, IntMask, RequestFifo, ReplyFifo, RequestHiPriFifo, Diagnostic, WriteSequence, and SAS1078 reset register.

## Risks and Edge Cases

- Reset concurrency is delicate. `ioc_reset_in_progress`, `taskmgmt_in_progress`, `taskmgmt_quiesce_io`, and `wait_on_reset_completion` are shared across normal command paths, config commands, workqueue polling, and protocol callbacks.
- Timeout recovery can recurse into reset while management commands are pending. The code completes pending `mptbase_cmds`/`taskmgmt_cmds` during post-reset to avoid waiters hanging.
- `mpt_config()` frees the message frame manually after a timeout/reset path and retries; callback ownership and `MPT_MGMT_STATUS_FREE_MF` interactions are important to avoid double-free or leaks.
- Request frame double-free prevention relies on the `0xdeadbeaf` marker in `mpt_free_msg_frame()`. Any consumer that modifies linkage fields after freeing can corrupt `FreeQ`.
- Normal reply DMA address mapping uses low 32-bit arithmetic against `reply_frames_low_dma`; the allocation and DMA mask assumptions are critical on 64-bit systems.
- Hardware-specific errata paths matter: SAS1078 36 GB addressing workaround, SAS1078 reset register path, 1064 IO access disable/enable, PCI-X transaction tweaks for FC/SPI chips, and SAS PCIe stale doorbell workaround on resume.
- Firmware download-boot is high risk. A failed `mpt_downloadboot()` can leave the IOC unusable, and shared `cached_fw` between bound IOCs must avoid double-free/download attempts.
- Some config-page copies include comments noting incomplete endianness normalization for LAN pages.
- Procfs removal uses constructed paths and assumes proc entries exist when detach runs.
- `mpt_fault_reset_work()` may remove a dead PCI device from a helper kthread after flushing SCSI commands; this path depends on `schedule_dead_ioc_flush_running_cmds` being valid for SCSI-attached adapters.

## Test Signals

- Build signal: compile the Fusion MPT drivers with SPI, FC, SAS, LAN, ioctl, procfs, PM, and logging combinations enabled to catch exported symbol, config, and conditional compilation issues.
- Probe/bring-up signal: logs showing `fusion_init()`, product name/capabilities, successful IOCFacts/PortFacts, FIFO priming, IOCInit, PortEnable, EventNotification, IRQ/MSI allocation, and protocol `probe()` callbacks.
- Request path signal: protocol I/O completions invoke the correct callback index; `FreeQ` depth recovers after completions; normal replies are returned to `ReplyFifo`; invalid callback index warnings do not appear.
- Config signal: `mpt_config()` page header/read/write operations complete with `MPT_MGMT_STATUS_COMMAND_GOOD` and valid replies; timeout path triggers one reset/retry and does not leave `mptbase_cmds.status` pending.
- Reset signal: injected IOC FAULT or doorbell timeout produces setup/pre/post reset callbacks, pending management completions, reinitialized FIFOs, reenabled interrupts, and resumed I/O.
- SAS/RAID signal: persistent table clear succeeds when IOC exceptions report full table; IOC Page 2/3 caches update after RAID events; inactive volume list is populated and freed correctly.
- PM signal: suspend sends message-unit reset and releases IRQ/resources; resume remaps resources, applies SAS PCIe workaround when needed, and completes bring-up.
- Cleanup signal: detach destroys workqueues, removes procfs entries, disables interrupts, frees DMA allocations, releases PCI regions, removes `ioc_list` entry, and leaves no use-after-free from delayed work or IRQ.
