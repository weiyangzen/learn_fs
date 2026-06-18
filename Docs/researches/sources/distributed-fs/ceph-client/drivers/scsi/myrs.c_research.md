# sources/distributed-fs/ceph-client/drivers/scsi/myrs.c

## Purpose

`myrs.c` is the Linux SCSI low-level driver implementation for Mylex DAC960/AcceleRAID/eXtremeRAID controllers that use the newer DAC960 V2 SCSI-based firmware interface. It registers a PCI driver named `myrs`, initializes supported controller families, enables the firmware memory-mailbox interface, exposes RAID logical drives through the SCSI midlayer and RAID class, exposes physical devices as non-ULD-attached SCSI devices, and provides sysfs controls for RAID state, rebuild, consistency check, discovery, cache flush, and enclosure-message filtering.

The implementation is organized around firmware IOCTL mailboxes, a ring of coherent command mailboxes, a ring of coherent status mailboxes, interrupt-driven completion, and a delayed monitor worker that polls health status and controller events.

## Important APIs, Types, and Functions

Name helpers `myrs_devstate_name()` and `myrs_raid_level_name()` translate firmware enums into user-visible strings. `myrs_reset_cmd()`, `myrs_qcmd()`, and `myrs_exec_cmd()` are the core command helpers: reset a command block, copy it into the next memory mailbox, ring the controller, and optionally wait for completion.

Firmware query helpers include `myrs_get_ctlr_info()`, `myrs_get_ldev_info()`, `myrs_get_pdev_info()`, `myrs_translate_pdev()`, `myrs_get_event()`, and `myrs_get_fwstatus()`. Management helpers include `myrs_dev_op()` for controller/device operations, `myrs_enable_mmio_mbox()` for coherent mailbox setup, `myrs_get_config()` for initial controller sizing, and `myrs_log_event()` for event decoding and state update hints.

SCSI and sysfs integration is provided by `myrs_queuecommand()`, `myrs_host_reset()`, `myrs_mode_sense()`, `myrs_sdev_init()`, `myrs_sdev_configure()`, `myrs_sdev_destroy()`, and the `myrs_template` `scsi_host_template`. Per-device sysfs attributes are `raid_state`, `raid_level`, `rebuild`, and `consistency_check`. Per-host attributes are `serial`, `ctlr_num`, `processor`, `model`, `ctlr_type`, `cache_size`, `firmware`, `discovery`, `flush_cache`, and `disable_enclosure_messages`.

RAID class integration uses `myrs_is_raid()`, `myrs_get_resync()`, `myrs_get_state()`, and `myrs_raid_functions`. PCI lifecycle functions are `myrs_alloc_host()`, `myrs_detect()`, `myrs_probe()`, `myrs_remove()`, `myrs_cleanup()`, `myrs_init_module()`, and `myrs_cleanup_module()`.

Completion and monitoring functions are `myrs_handle_scsi()`, `myrs_handle_cmdblk()`, and `myrs_monitor()`. Memory/resource functions are `myrs_create_mempools()`, `myrs_destroy_mempools()`, and `myrs_unmap()`.

Hardware-specific code is split into GEM, BA, and LP blocks. Each block supplies register access helpers, mailbox initialization, hardware init, interrupt handling, and `struct myrs_privdata` records. Supported PCI ids are DAC960 GEM, BA, and LP variants.

## Control Flow

Module load attaches a RAID class template and registers the PCI driver. Probe calls `myrs_detect()`, which allocates a `Scsi_Host`, enables the PCI device, maps BAR 0 into MMIO space, selects the PCI-id-specific hardware initializer, waits for controller initialization to finish, enables the memory mailbox interface, requests the IRQ, and stores the host-private controller state.

`myrs_enable_mmio_mbox()` sets a 64-bit DMA mask with 32-bit fallback, allocates a temporary coherent mailbox, allocates coherent command and status mailbox rings, allocates the firmware health buffer, allocates host-side controller info and event buffers, fills a `MYRS_IOCTL_SET_MEM_MBOX` command, and submits it through the controller-family hardware mailbox initialization callback. The command/status rings are circular; `myrs_qcmd()` advances `next_cmd_mbox` and rings the controller when the previous mailbox slots indicate the controller needs notification.

After low-level detection, `myrs_get_config()` reads controller info, validates that old firmware 6.00-00 is rejected, fills host limits from controller data, caps queue depth to controller `max_tcq - 3` and mailbox capacity, sets `max_sectors` and `sg_tablesize`, and logs model, firmware, channel, memory, queue, and device counts. `myrs_create_mempools()` then creates DMA pools for large S/G lists, sense buffers, long CDB buffers, creates an ordered monitor workqueue, and schedules `myrs_monitor()`. Probe finally calls `scsi_add_host()` and `scsi_scan_host()`.

SCSI discovery uses `myrs_sdev_init()`. Channels below `ctlr_info->physchan_present` are physical devices; the driver allocates `struct myrs_pdev_info`, queries firmware, stores it in `sdev->hostdata`, and later prevents upper-layer driver attachment except for skipping the HBA device. Channels at or above `physchan_present` are logical drives; the driver translates channel/id to logical-drive number, queries `struct myrs_ldev_info`, stores it in `hostdata`, maps firmware RAID levels to RAID class levels, and logs non-online states. `myrs_sdev_configure()` marks logical devices as tagged-capable and sets write-cache default when firmware reports write cache enabled.

Normal I/O enters `myrs_queuecommand()`. The function rejects devices without `hostdata`, synthesizes an illegal-request response for `REPORT_LUNS`, and handles `MODE_SENSE` locally for logical drives by building caching and block-descriptor data. Other commands allocate a DMA sense buffer and, for CDBs longer than 10 bytes, a DMA DCDB buffer. Logical drives use `MYRS_CMD_OP_SCSI_10` or `MYRS_CMD_OP_SCSI_256` addressed to the firmware-provided logical backing pdev fields; physical devices use passthrough opcodes. Request tags are offset by 3 because ids 1 and 2 are reserved for direct and monitor commands. Data buffers are mapped with `scsi_dma_map()`. Up to two S/G entries fit in the mailbox; larger lists allocate an S/G DMA-pool block and set `add_sge_mem`. The command is submitted under `queue_lock`.

Interrupt handlers for GEM, BA, and LP are structurally identical after register-specific acknowledge. They walk status mailboxes while `id > 0`, map ids 1 and 2 to the direct and monitor command blocks, map other ids back to SCSI commands with `scsi_host_find_tag(host, id - 3)`, copy status, sense length, and residual into the command block, clear the status mailbox, advance the status ring, and dispatch either `myrs_handle_cmdblk()` for synchronous firmware commands or `myrs_handle_scsi()` for SCSI I/O. SCSI completion unmaps DMA, copies sense data on `MYRS_STATUS_FAILED`, frees sense/DCDB/SGL pool objects, sets residual, maps nonresponsive statuses to `DID_BAD_TARGET`, otherwise returns `DID_OK | firmware_status`, and calls `scsi_done()`.

The monitor worker first issues `GET_HEALTH_STATUS`. If `needs_update` is set, it refreshes controller info under `cinfo_mutex`. If firmware's next event sequence is ahead of `cs->next_evseq`, it fetches one event, logs it, increments the sequence, and reschedules quickly. It also refreshes every logical device when controller info reports long-running operations such as background initialization, logical/physical init, consistency check, rebuild, or expansion. If there is no new epoch, event, or urgent update, it falls back to the secondary interval.

Sysfs write paths are firmware command frontends. `raid_state_store()` accepts `offline`, `kill`, `online`, or `standby`, translates physical devices to logical devices when needed, and sends `MYRS_IOCTL_SET_DEVICE_STATE`. `rebuild_store()` starts or stops rebuild with `MYRS_IOCTL_RBLD_DEVICE_START/STOP` after checking current logical-device state. `consistency_check_store()` starts or stops consistency check with `MYRS_IOCTL_CC_START/STOP`. `discovery_store()` sends `START_DISCOVERY`, resets event sequence tracking, forces monitor work, and waits for it. `flush_cache_store()` sends `FLUSH_DEVICE_DATA`.

Remove flushes controller cache, cancels and destroys monitor/mempool resources, frees coherent mailbox and firmware buffers, disables interrupts, unmaps MMIO, frees IRQ, disables the PCI device, and drops the SCSI host. Module unload unregisters PCI and releases the RAID class template.

## State and Persistence Behavior

Persistent kernel state lives in `struct myrs_hba`, defined in `myrs.h` and filled here. It includes MMIO pointers, PCI/SCSI objects, model and firmware strings, event epoch/sequence tracking, monitor flags, workqueue, DMA pools, command/status mailbox rings, direct and monitor command blocks, firmware health buffer, controller info cache, event buffer, and mutexes.

Per-SCSI-device state is stored in `sdev->hostdata`: physical devices own a dynamically allocated `struct myrs_pdev_info`, logical drives own a dynamically allocated `struct myrs_ldev_info`. These caches are refreshed by discovery, sysfs show/store operations, event handling, and monitor updates. They are freed by `myrs_sdev_destroy()`.

The driver itself has no file-backed persistence. However, sysfs writes can change controller-persistent or disk-visible RAID state: setting devices online/offline/standby, starting or canceling rebuild, starting or canceling consistency checks, triggering discovery, and flushing controller cache. Firmware configuration and rebuild/check progress survive in the controller and arrays according to firmware behavior, not in driver-owned storage.

The coherent command/status mailbox rings and firmware health buffer persist for the life of the controller. Their DMA addresses are programmed into firmware by `SET_MEM_MBOX`; losing or freeing them before disabling the controller interface would break completion delivery.

## Dependencies and Integration Points

The file depends on Linux PCI, coherent and streaming DMA, DMA pools, interrupts, SCSI midlayer, block request tags and timeouts, RAID class, workqueues, completions, spinlocks, mutexes, sysfs attributes, unaligned access helpers, and sense-data helpers.

Firmware integration is through the DAC960 V2 mailbox ABI from `myrs.h`: IOCTL opcodes, SCSI 10/256 and passthrough opcodes, 64-byte command mailboxes, 8-byte status mailboxes, controller info, logical/physical device info, health status, and event records.

Hardware integration is controller-family-specific. GEM uses shifted 32-bit register accesses, BA and LP use byte doorbell/mask registers, and all families provide operations for hardware mailbox submission, memory-mailbox notification, interrupt masking, reset, initialization polling, error-status reading, and command-status reading.

User-space integration is mostly sysfs through SCSI host and device attributes, plus standard SCSI block devices for logical drives and RAID class state/resync reporting. Physical devices are discovered but `no_uld_attach` prevents normal upper-layer storage attachment.

## Risks and Edge Cases

`myrs_translate_pdev()` does not call `myrs_reset_cmd()` before filling the shared direct command block, unlike most other direct-command helpers. If previous direct-command mailbox fields survive and are relevant to the reused union view, this can submit stale bits. The call is protected by `dcmd_mutex`, but not by a reset.

`myrs_get_event()` uses the monitor command block without a visible `myrs_reset_cmd()` before filling the get-event mailbox. It overwrites many fields, but stale control bits or DMA fields could be a risk if previous monitor commands used a different union view.

`myrs_get_fwstatus()` sets `sgl->sge[0].sge_count = mbox->ctlr_info.dma_size` even though it filled the `common` union view. The overlapping layout likely makes this the same low 24-bit DMA size field, but it is fragile and confusing.

`myrs_cleanup()` calls `cs->disable_intr(cs)` even though the callback type expects `void __iomem *base`; the hardware helpers expect an MMIO base, not `struct myrs_hba *`. This is a strong bug signal in the visible code path.

`disable_enclosure_messages_store()` uses `to_scsi_device(dev)` even though the attribute is installed as a SCSI host attribute, while the show path uses `class_to_shost(dev)`. That mismatch is a likely sysfs store crash or invalid cast risk.

Interrupt handlers hold `queue_lock` while completing SCSI commands through `scsi_done()`. If any completion path re-enters driver locking in an unexpected way, lock-order problems are possible. Existing code may rely on SCSI midlayer expectations for low-level driver completion context.

`myrs_queuecommand()` handles `scsi_dma_map()` returning zero by falling through the multi-SG path with `nsge == 0`, leaving no S/G entries but still submitting a command with nonzero `dma_size` if `scsi_bufflen()` was nonzero. Negative mapping errors also fall into the same path because only `nsge == 1` and `nsge > 2` are special-cased. This needs careful review against SCSI DMA API semantics.

Timeout conversion stores `rq->timeout` directly in firmware seconds/minutes fields, but Linux request timeouts are normally in jiffies. If this code expects seconds, command timeout programming may be wrong unless the surrounding API changed or normalizes the field.

The driver caps queue depth by reserving ids 1 and 2, then uses `rq->tag + 3`. Correctness depends on all SCSI requests having valid tags below the configured queue depth and on no firmware completion returning id 0 for a real command.

Probe error handling is staged but split across `myrs_detect()`, `myrs_get_config()`, `myrs_create_mempools()`, and `scsi_add_host()`. Fault-injection testing should confirm every partial allocation path releases coherent memory, IRQ, MMIO, workqueue, and DMA pools exactly once.

## Test Signals

Build tests should include this driver and `myrs.h` with warnings enabled. Static analysis should flag the callback argument mismatch in `myrs_cleanup()`, the host/sysfs cast mismatch in `disable_enclosure_messages_store()`, direct-command mailbox reset inconsistencies, and DMA-map return handling in `myrs_queuecommand()`.

Probe validation should cover GEM, BA, and LP hardware paths; DMA mask fallback from 64-bit to 32-bit; mailbox enable failure; firmware initialization timeout; firmware 6.00-00 rejection; and IRQ request failure. Runtime I/O tests should cover logical-drive reads/writes with no data, one S/G entry, two inline S/G entries, and more-than-two S/G entries requiring `sg_pool`.

SCSI behavior tests should cover local `REPORT_LUNS` rejection, logical-drive `MODE_SENSE` with and without block descriptors, write-cache reporting, FUA propagation, long CDB allocation via `dcdb_pool`, residual reporting, sense copying on firmware failure, nonresponsive-device status mapping, and host reset.

Management tests should exercise all sysfs attributes: state changes for physical and logical devices, rebuild start/stop, consistency check start/stop, discovery, cache flush, enclosure-message filtering, RAID class state/resync, and show paths after device removal. Monitor tests should inject health status changes, event sequence increments, logical-drive state transitions, enclosure events, sense events, and long-running operation progress.
