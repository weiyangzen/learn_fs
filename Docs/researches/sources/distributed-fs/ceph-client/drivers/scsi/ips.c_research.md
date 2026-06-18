# Research: sources/distributed-fs/ceph-client/drivers/scsi/ips.c

## Purpose

`ips.c` is the Linux SCSI low-level driver for IBM/Adaptec ServeRAID PCI RAID controllers. It binds to Copperhead, Morpheus, and Marco-family ServeRAID adapters, initializes controller firmware interfaces, registers a `Scsi_Host`, translates SCSI mid-layer commands into ServeRAID command blocks, and handles interrupts, completions, resets, passthrough management utilities, firmware/BIOS flashing, and cache flushing during shutdown.

The driver exposes logical RAID drives on SCSI channel 0 while also supporting direct-command descriptor blocks (DCDBs) for physical devices on controller backend channels. It contains both generic SCSI-facing logic and hardware-specific register access paths selected at probe time for programmed I/O, memory-mapped I/O, and I2O queue delivery.

## Important APIs, Types, and Entry Points

- Module and PCI integration: `ips_module_init()`, `ips_module_exit()`, `ips_pci_driver`, `ips_pci_table`, `ips_insert_device()`, and `ips_remove_device()` attach the driver to PCI devices and SCSI hosts. Module/boot parameters are parsed by `ips_setup()` for `noi2o`, `nommap`, `ioctlsize`, `cdboot`, and `maxcmds`.
- SCSI host integration: `ips_driver_template` wires `.queuecommand = ips_queue`, `.eh_abort_handler = ips_eh_abort`, `.eh_host_reset_handler = ips_eh_reset`, `.show_info`, `.write_info`, `.sdev_configure`, and `.bios_param`. `ips_register_scsi()` allocates the final `Scsi_Host`, requests IRQs, sets queue limits, and scans.
- Controller state: `ips_ha_t` stores PCI/BAR state, mapped memory pointer, adapter type, queue limits, DMA buffers, NVRAM/config/enquiry/subsystem data, SCB pools, wait/active/passthrough queues, DCDB active bitmaps, flash buffers, FFDC timing, and the selected `ips_hw_func_t` hardware callback table.
- Command state: `ips_scb_t` is the firmware-visible command block wrapper. It contains an `IPS_HOST_COMMAND` union, DCDB table, target/channel/lun, SCSI CDB copy, DMA bus addresses, S/G list pointer, mapped-data flags, completion callback, status bytes, and transfer-splitting fields.
- Firmware ABI types: `IPS_IO_CMD`, `IPS_LD_CMD`, `IPS_DCDB_CMD`, `IPS_FLASHFW_CMD`, `IPS_STATUS`, `IPS_ADAPTER`, `IPS_ENQ`, `IPS_CONF`, `IPS_NVRAM_P5`, and `IPS_SUBSYS` are defined in `ips.h` and populated by this file.
- Queue and completion helpers: `ips_queue_lck()`, `ips_next()`, `ips_send_cmd()`, `ips_done()`, `ips_chkstatus()`, `ips_map_status()`, `ips_getscb()`, `ips_freescb()`, and queue helpers for SCB, SCSI wait, and COPP passthrough queues.
- Hardware dispatch callbacks: `ips_setup_funclist()` chooses `reset`, `issue`, `isinit`, `isintr`, `init`, `statupd`, `statinit`, `intr`, `enableint`, and optional BIOS flash operations for Copperhead PIO, Copperhead MEMIO, or Morpheus/Marco I2O paths.
- Passthrough and utilities: `ips_is_passthru()`, `ips_make_passthru()`, `ips_usrcmd()`, `ips_cleanup_passthru()`, `ips_alloc_passthru_buffer()`, and COPP constants support management commands encoded as SCSI command `0x0d` to channel 0, target `IPS_ADAPTER_ID`.
- Initialization commands: `ips_hainit()`, `ips_read_config()`, `ips_read_adapter_status()`, `ips_read_subsystem_parameters()`, `ips_readwrite_page5()`, `ips_write_driver_status()`, `ips_get_bios_version()`, and `ips_clear_adapter()` read controller metadata and update firmware-visible driver status.
- Reset, shutdown, and FFDC: `ips_eh_abort()`, `__ips_eh_reset()`, `ips_halt()`, `ips_release()`, `ips_flush_and_reset()`, `ips_ffdc_reset()`, `ips_ffdc_time()`, and `ips_fix_ffdc_time()` handle SCSI EH, reboot flushing, and controller diagnostic timestamps.
- Flash support: `ips_flash_copperhead()`, `ips_flash_bios()`, `ips_flash_firmware()`, `ips_erase_bios*()`, `ips_program_bios*()`, `ips_verify_bios*()`, and `ips_free_flash_copperhead()` implement legacy BIOS/firmware update paths.

## Control Flow

Module load registers the PCI driver, orders probed controllers, registers each adapter with the SCSI mid-layer, and registers a reboot notifier. PCI probe begins in `ips_insert_device()`: it enables the device, requests BARs, calls `ips_init_phase1()` to allocate temporary `ips_ha_t` state and DMA buffers, then calls `ips_init_phase2()` to install an IRQ, allocate a temporary SCB, run controller initialization, and allocate the final SCB pool. During initial non-hotplug load, `ips_detect()` later turns initialized controller records into real SCSI hosts; on hotplug, probe registers the SCSI host immediately.

`ips_init_phase1()` finds a controller slot, discovers IO and memory BARs, maps memory BARs when present, allocates `ha`, sets DMA masks, allocates coherent enquiry, adapter-status, logical-drive, and ioctl buffers, allocates heap config/NVRAM/subsystem buffers, selects hardware callbacks, and initializes the adapter if firmware is not already initialized. `ips_hainit()` then initializes status queues and interrupts, sends initial FFDC, reads config/enquiry/subsystem data, identifies adapter type, writes Linux driver status into NVRAM page 5, clears stripe locks if reset state requires it, and derives bus, target, lun, max transfer, max command, and initiator-ID limits.

SCSI I/O enters through `ips_queue_lck()`. Commands are rejected when the host adapter is missing or inactive, when wait queues are full, or when the request targets the controller's initiator ID on a physical channel. Normal commands are queued on `ha->scb_waitlist`; COPP passthrough commands are queued on `ha->copp_waitlist`. A special passthrough reset command can synchronously trigger `__ips_eh_reset()` if no commands are active.

`ips_next()` drains queued work. Passthrough has priority and is throttled to `IPS_MAX_IOCTL`; it obtains an SCB, copies the user COPP packet from the SCSI scatterlist into `ha->ioctl_data`, builds the requested firmware command, and either completes immediately or posts it. Normal I/O obtains SCBs from `ha->scb_freelist`, maps the SCSI scatterlist with `scsi_dma_map()`, fills standard or enhanced ServeRAID SG entries, handles adapter transfer-size splitting, sets DCDB direction attributes from `ips_command_direction[]`, and calls `ips_send_cmd()`. Physical-channel DCDBs are serialized per channel/target using `ha->dcdb_active[]`.

`ips_send_cmd()` is the main SCSI-to-firmware translator. For logical drives on channel 0 it handles simple commands locally or builds controller commands: read/write 6/10 become `IPS_CMD_READ`, `IPS_CMD_WRITE`, or SG variants; inquiry, mode sense, read capacity, and test-unit-ready fetch logical-drive info or enquiry data so completion can synthesize SCSI responses; unsupported logical commands receive a check condition with invalid opcode sense. For physical devices, it builds old or extended DCDB/DCDB_SG packets, including timeout attributes, CDB bytes, sense buffers, transfer length, and data or SG DMA pointer. The final post goes through `ha->func.issue`.

Interrupts enter `do_ipsintr()`. Before final SCSI registration, it lets the temporary `ha` service initialization completions directly. After registration it locks the host, checks active state, calls the selected interrupt handler, unlocks, and invokes `ips_next()` again to submit queued work. Copperhead handlers consume status entries from the host status queue; Morpheus reads I2O outbound messages. Both call `ips_chkstatus()` to associate firmware status with an SCB and then dispatch the SCB callback.

Completion uses two callbacks. `ipsintr_blocking()` completes internal synchronous commands by clearing `ha->waitflag`; `ipsintr_done()` calls `ips_done()` for SCSI and passthrough commands. `ips_done()` copies passthrough results back to the caller, frees flash buffers when needed, handles continued chunks for transfer-split commands, clears DCDB active bits, calls `scsi_done()`, and returns SCBs to the free list. `ips_chkstatus()` maps successful logical-drive commands into emulated SCSI inquiry, capacity, mode sense, and request sense data, restricts direct physical DASD exposure, and delegates failures to `ips_map_status()` for Linux SCSI result and sense-buffer mapping.

Reset flow first tries to avoid a physical reset. `__ips_eh_reset()` sends a cache flush unless the reset came from an ioctl; if that succeeds, the SCSI EH reset returns success without disrupting outstanding I/O. Otherwise it invokes the hardware reset callback, clears adapter state, sends FFDC if supported, fails active commands with `DID_RESET`, clears DCDB and ioctl counters, and restarts queue draining. If reset or clear fails, all active and pending commands are failed and the adapter is marked inactive.

Remove and reboot paths flush controller cache. `ips_release()` removes the SCSI host, sends `IPS_CMD_FLUSH`, frees driver memory, releases IRQ, and drops the host reference. `ips_halt()` is registered as a reboot notifier and sends the same flush command to each active controller on restart, halt, or poweroff.

## State and Persistence Behavior

Most driver state is in kernel memory and coherent DMA areas. `ips_ha[]` and `ips_sh[]` keep global controller/host slots; `ips_next_controller`, `ips_num_controllers`, and `ips_released_controllers` track lifecycle. Each `ips_ha_t` owns its SCB pool, S/G pool, status queue, enquiry/config/subsystem copies, logical-drive info, ioctl buffer, flash buffer, and queues.

Firmware-visible state is updated through command packets and MMIO/PIO registers. `ips_statinit()` and `ips_statinit_memio()` program status queue addresses. `ips_write_driver_status()` reads NVRAM page 5, writes OS type Linux, driver version, BIOS version, adapter type, and disables versioning support before writing the page back. This is persistent controller NVRAM state, not merely in-memory driver state.

Logical-drive state is refreshed from controller enquiry/config/logical-drive-info commands. The driver uses this state to decide which logical targets are online, how to answer inquiry/capacity/mode sense, and how to choose geometry in `ips_biosparam()`. Physical-device presence is read from `ha->conf->dev[][]`; devices known absent are not sent DCDB commands.

Command lifetime is queue-based. Free SCBs live on `ha->scb_freelist`; pending normal SCSI commands use `struct scsi_cmnd::host_scribble`; pending passthrough commands use separately allocated `ips_copp_wait_item_t` nodes; active firmware commands live on `ha->scb_activelist`. The last SCB slot is reserved as a special internal command block and is not returned to the free list.

Passthrough state is serialized through one coherent ioctl buffer per controller. `ips_alloc_passthru_buffer()` grows that buffer when user commands exceed the configured size, and `ips_cleanup_passthru()` copies status, adapter type, DCDB sense, and data back into the original SCSI scatterlist. Copperhead flash state may use a global CD-boot flash buffer guarded by `ips_FlashDataInUse`, or a per-controller coherent allocation.

FFDC state is tracked by `ha->reset_count` and `ha->last_ffdc`. On initialization, reset, and roughly every eight hours when the adapter is idle and subsystem parameters advertise FFDC, the driver sends a timestamp/reset record to the controller.

## Dependencies and Integration Points

- Linux PCI core: device matching, `pci_enable_device()`, BAR/resource claims, `ioremap()`, IRQ assignment, config reads after reset, driver data storage, and remove teardown.
- Linux SCSI mid-layer: `Scsi_Host`, `scsi_host_template`, queuecommand locking wrapper, SCSI EH abort/reset, `scsi_add_host()`, `scsi_scan_host()`, `scsi_remove_host()`, device queue-depth configuration, SG mapping/copy helpers, result codes, and sense buffers.
- Linux DMA API: coherent allocations for firmware-visible command/status/data buffers, DMA masks for 32-bit or enhanced 64-bit S/G support, `scsi_dma_map()`, `scsi_dma_unmap()`, and single-buffer mappings for flash firmware downloads.
- Register-level controller ABI: Copperhead uses command channel/status queue registers through PIO or MEMIO; Morpheus/Marco use I2O inbound/outbound queues and i960 doorbell/message registers. Callback selection isolates these register differences.
- Firmware command ABI: ServeRAID command opcodes such as enquiry, read config, NVRAM page read/write, logical-drive info, DCDB, config sync, error table, flush, FFDC, download, BIOS/firmware read-write, and reset channel.
- Userspace management ABI: COPP passthrough packets are carried through SCSI generic-style commands to channel 0 target `IPS_ADAPTER_ID`. The path supports controller count queries, user commands, ioctl commands, resets, and firmware/BIOS flashing.
- Proc-style host information: `.show_info` and `.write_info` expose `/proc/scsi/ips` style controller information, including adapter type, IO/MEM regions, IRQ, BIOS/firmware/boot block versions, driver version/build, max devices, command limits, and current queue counts.
- Reboot notifier: cache flushes are integrated with system restart/halt/poweroff events.

## Risks and Edge Cases

- The driver is tightly coupled to legacy firmware layouts and endian expectations. Command structures, status entries, NVRAM page 5, DCDB tables, and enhanced S/G entries must match controller ABI exactly.
- Locking is subtle. Queue helpers assume host-adapter locking; `ips_next()` deliberately drops and reacquires the host lock around passthrough construction and SCSI DMA mapping, then resumes queue work. Error handling and interrupt paths also share active/wait/free queues.
- `ips_next()` stores the next normal command pointer in `p = p->host_scribble` after removing and possibly reusing `p`; this code relies on the command-list manipulation order and should be regression-tested around skipped DCDB-active entries.
- Passthrough commands are privileged by convention but dangerous in behavior. They can issue raw firmware commands, controller resets, and flash updates. Size checks exist, but command contents and timeout semantics come from userspace.
- BIOS and firmware flashing paths perform long polling loops and direct flash register writes. Failures can leave a controller in an unusable state, and the code has special Trombone timing delays and CD-boot shared-buffer behavior.
- Physical-device access is intentionally restricted. The driver blocks physical DASD inquiry exposure by converting it to timeout-like results, but still passes other physical commands through DCDB for tape and utility support.
- Reset paths can fail all outstanding I/O and mark the adapter inactive. If cache flush succeeds, reset returns success without physical reset, so tests must distinguish communication failures from recoverable target errors.
- Transfer splitting around `ha->max_xfer` and `IPS_MAX_XFER` is fragile. Scatterlist entries may be partially consumed, `breakup`/`sg_break` state must advance correctly, and residual completion must not double-unmap or leak DMA mappings.
- `ips_wait()` busy-polls with microsecond sleeps during initialization and while the request lock may be held. Long firmware timeouts can stall probe/reset paths.
- Some resource cleanup ordering is delicate. `ips_release()` calls `ips_free(ha)` before `free_irq(ha->pcidev->irq, ha)`, but the IRQ path uses `ha`; teardown depends on host removal and inactive state preventing new interrupts.

## Test Signals

- Build signals: compile with PCI, SCSI, DMA mapping, procfs, reboot notifier, highmem SG, and module parameter support enabled; watch for warnings in old-style PIO/MEMIO access and pointer-to-DMA conversions.
- Probe signals: matching PCI IDs `0x1014:0x002e`, `0x1014:0x01bd`, and `0x9005:0x0250`; successful BAR request/map; DMA mask selection; IRQ request; adapter init POST/config waits; `ips_hainit()` reading config, enquiry, subsystem parameters, and NVRAM page 5.
- SCSI scan signals: `scsi_add_host()` and `scsi_scan_host()` expose channel 0 logical targets according to logical-drive state; `ips_sdev_configure()` sets tagged disk queue depth based on `ha->max_cmds` and logical-drive count.
- Normal I/O signals: READ/WRITE 6 and 10 produce correct ServeRAID opcodes, SG counts, LBA, sector count, enhanced-SG flag, and completion result. Oversized requests should split and continue until complete without double completion.
- Logical command emulation signals: inquiry returns IBM SERVERAID DASD data for online logical drives and processor data for adapter target; read capacity uses logical-drive sectors minus one and 512-byte blocks; mode sense pages 3, 4, and 8 reflect geometry decisions.
- Physical DCDB signals: only one command per physical channel/target is active; absent devices return `DID_NO_CONNECT`; tape-capable subsystem parameters select extended DCDB formats; check-condition sense data is copied to `sense_buffer`.
- Passthrough signals: COPP magic detection works through SCSI SG data; controller-count commands complete immediately; raw commands copy status/data back; queue limit `IPS_MAX_IOCTL_QUEUE` and active limit `IPS_MAX_IOCTL` are enforced; passthrough reset refuses when active I/O exists.
- Interrupt signals: shared/spurious interrupts return `IRQ_NONE` or are ignored; Copperhead status queues and Morpheus I2O outbound queues drain all completions; active list entries are removed before callbacks.
- Reset/shutdown signals: SCSI EH abort removes queued but unsent work; reset first attempts cache flush, otherwise hardware reset and adapter clear; failed reset marks inactive and fails active/pending commands; reboot and remove issue `IPS_CMD_FLUSH`.
- NVRAM/FFDC signals: page 5 signature repair, driver/BIOS version writes, slot-number update, reset FFDC, and idle eight-hour FFDC timestamp paths all complete or fail with clear kernel warnings.
- Flash signals: BIOS erase/program/verify and firmware download reject unsupported combinations, enforce accumulated packet size, free flash buffers on success/failure, and handle the global CD-boot flash buffer exclusion bit.
