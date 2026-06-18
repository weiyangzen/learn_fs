# subset-b-005236 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr.h

## Purpose
`arcmsr.h` is the shared hardware contract for the Areca ARC11xx/12xx/16xx/188x SCSI RAID driver. It defines driver limits, PCI device IDs, firmware message opcodes, memory-mapped register layouts for adapter generations A through F, command/control data structures, adapter state, CCB state, sense data layout, interrupt bit definitions, and the small exported interface used by `arcmsr_attr.c`.

## Important APIs, types, and constants
- Driver identity and tunables include `ARCMSR_NAME`, `ARCMSR_DRIVER_VERSION`, queue-depth bounds, transfer-size bounds, target/lun limits, and API buffer sizes.
- Management message ABI is represented by `struct CMD_MESSAGE`, `struct CMD_MESSAGE_FIELD`, `ARCMSR_MESSAGE_*` control codes, and `ARCMSR_MESSAGE_RETURNCODE_*` values. These are used by SCSI `READ_BUFFER`/`WRITE_BUFFER` management commands and by sysfs binary attributes.
- DMA scatter/gather descriptors are `struct SG32ENTRY` and `struct SG64ENTRY`; `IS_SG64_ADDR` marks 64-bit SG entries in the firmware CDB stream.
- `struct ARCMSR_CDB` is the firmware command descriptor sent for ordinary SCSI commands. It carries bus/target/lun, CDB bytes, data length, flags, device status, sense data, and variable SG entries.
- Adapter register maps are split by hardware family: `MessageUnit_A`, `MessageUnit_B`, `MessageUnit_C`, `MessageUnit_D`, `MessageUnit_E`, and `MessageUnit_F`. The layouts encode doorbells, message buffers, post/done queues, reset registers, and completion queue indices.
- `struct AdapterControlBlock` is the central per-host state object: adapter type, `pci_dev`, `Scsi_Host`, mapped register union, coherent DMA regions, locks, circular management queues, device map, firmware metadata, timers, work item, interrupt state, queue sizing, CCB pool, completion queue, and optional XOR host-buffer allocation state.
- `struct CommandControlBlock` binds one SCSI command to one firmware CDB, physical address, state flags, and free-list linkage.
- Exported declarations connect this header to implementation files: `arcmsr_write_ioctldata2iop`, `arcmsr_Read_iop_rqbuffer_data`, `arcmsr_clear_iop2drv_rqueue_buffer`, `arcmsr_get_iop_rqbuffer`, `arcmsr_host_groups`, `arcmsr_alloc_sysfs_attr`, and `arcmsr_free_sysfs_attr`.

## Control flow and state model
The header establishes an adapter-type dispatch model. `AdapterControlBlock.adapter_type` selects the proper `MessageUnit_*` register layout and per-generation doorbell/queue protocols in `arcmsr_hba.c`. CCBs live in a coherent DMA pool and cycle through free-list, posted, firmware-owned, done, and completed states via `startdone` and `ccboutstandingcount`. Management traffic uses in-memory circular `rqbuffer`/`wqbuffer` rings with `rqbuf_*` and `wqbuf_*` indices protected by dedicated locks.

## Persistence behavior
The file itself has no persistent storage. Runtime state is volatile kernel memory plus device firmware-visible coherent DMA memory. Firmware metadata copied into `firm_model`, `firm_version`, `device_map`, queue limits, and PIC status persists only for the lifetime of the host instance. Timers periodically refresh firmware device maps and optionally firmware time, but those are not durable driver-side stores.

## Dependencies and integration points
The header depends on Linux interrupt, PCI, DMA, SCSI, timer, workqueue, and sysfs concepts through the structures consumed by `arcmsr_hba.c` and `arcmsr_attr.c`. Its register definitions integrate directly with Areca firmware specs and with the PCI ID table. The exported `arcmsr_host_groups` integrates read-only host attributes into the SCSI host template.

## Risks and edge cases
- Register layouts and bit definitions are hardware ABI; mistakes can cause lost interrupts, firmware hangs, or wrong reset behavior.
- Several adapter generations share helper paths but not identical semantics, especially Type F host buffers and Type E/F toggle doorbells.
- Queue and SG limits are negotiated from firmware configuration; mismatches between `ccbsize`, SG page sizing, and firmware limits can corrupt command DMA.
- `AdapterControlBlock` carries many independent locks and flags. Callers must obey the intended lock ownership for CCB free lists, post/done queues, and management buffers.
- `devstate` is bounded by `ARCMSR_MAX_TARGETID` and `ARCMSR_MAX_TARGETLUN`; command paths must not address outside these limits.

## Test signals
- Build coverage should compile all adapter-type branches and validate packed SG/CDB layout assumptions.
- Probe tests should verify firmware config parsing populates host limits and firmware strings correctly.
- Runtime signals are successful SCSI host registration, sysfs host attributes, interrupt delivery, command completion under load, management buffer read/write behavior, hotplug device-map changes, suspend/resume, abort, and bus reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr_attr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr_attr.c

## Purpose
`arcmsr_attr.c` exposes Areca adapter management and status through sysfs. It provides three privileged binary message-unit files (`mu_read`, `mu_write`, `mu_clear`) under the SCSI host device and a host attribute group with driver, firmware, queue, reset, and abort counters.

## Important APIs and functions
- `arcmsr_sysfs_iop_message_read()` drains bytes from `acb->rqbuffer` into the user buffer, refreshes from the firmware read queue when overflow was recorded, and requires `CAP_SYS_ADMIN`.
- `arcmsr_sysfs_iop_message_write()` accepts up to `ARCMSR_API_DATA_BUFLEN` bytes, stages them in `acb->wqbuffer`, and triggers `arcmsr_write_ioctldata2iop()` when firmware has cleared the previous write buffer.
- `arcmsr_sysfs_iop_message_clear()` clears firmware and driver management queues, resets ring indices, and marks management-buffer flags as cleared/read.
- `arcmsr_alloc_sysfs_attr()` creates `mu_read`, `mu_write`, and `mu_clear`, rolling back already-created files on failure.
- `arcmsr_free_sysfs_attr()` removes the three binary files during teardown.
- Attribute show callbacks expose `ARCMSR_DRIVER_VERSION`, `ccboutstandingcount`, `num_resets`, `num_aborts`, `firm_model`, `firm_version`, `firm_request_len`, `firm_numbers_queue`, `firm_sdram_size`, and `firm_hd_channels`.
- `arcmsr_host_groups` is consumed by the SCSI host template in `arcmsr_hba.c`.

## Control flow and state behavior
Management read uses `rqbuffer_lock`, computes circular-buffer occupancy with `CIRC_CNT`/`CIRC_CNT_TO_END`, copies up to `ARCMSR_API_DATA_BUFLEN`, advances `rqbuf_getIndex`, and then tries to pull more firmware data if `ACB_F_IOPDATA_OVERFLOW` had been set. Management write uses `wqbuffer_lock`; if there is already queued data, it nudges the IOP and returns `0` to ask user space to retry, otherwise it copies data into the circular write queue and posts to firmware when `ACB_F_MESSAGE_WQBUFFER_CLEARED` is set. Clear resets both driver rings and asks the firmware side to clear its read queue.

## Persistence behavior
The sysfs files are dynamic and exist only while the SCSI host is registered and `arcmsr_alloc_sysfs_attr()` succeeds. All message data is transient in adapter memory and driver ring buffers. The status attributes reflect live counters and firmware config captured by probe/config refresh; they do not write persistent state.

## Dependencies and integration points
This file depends on Linux sysfs binary attributes, SCSI host conversion (`class_to_shost`), capability checks, circular-buffer helpers, and the exported buffer helpers implemented in `arcmsr_hba.c`. It integrates with the SCSI host template through `arcmsr_host_groups` and with PCI probe/remove through explicit allocation/free helpers.

## Risks and edge cases
- The binary management channel is privileged but still copies raw firmware management data. Buffer length checks and ring bounds are critical.
- `mu_clear` only zeros `sizeof(struct QBUFFER)` bytes in each driver queue, not the full `ARCMSR_MAX_QBUFFER`; this matches existing code but is a notable partial-clear behavior.
- Write returns `0` when firmware is busy instead of a blocking wait, so user tools must retry.
- Correct behavior depends on `rqbuffer_lock`/`wqbuffer_lock` matching the interrupt handlers that fill and drain management queues.
- Overflow recovery re-enters firmware read-buffer handling while the read lock is held; regressions here could lose management data or keep `ACB_F_IOPDATA_OVERFLOW` set forever.

## Test signals
- `ls`/read of host sysfs attributes should show version, counters, firmware model/version, and firmware queue metadata.
- Non-admin access to `mu_read`, `mu_write`, and `mu_clear` should fail with `-EACCES`.
- Large writes above `ARCMSR_API_DATA_BUFLEN` should fail with `-EINVAL`.
- Management utility tests should verify ring wraparound, retry-on-busy write behavior, clear behavior, and overflow recovery after firmware posts more data than local free space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr_hba.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr_hba.c

## Purpose
`arcmsr_hba.c` is the main Areca ARC11xx/12xx/16xx/188x SCSI RAID host driver. It registers a PCI-backed SCSI host, maps adapter registers, negotiates firmware limits, allocates DMA CCB/completion resources, queues SCSI commands to firmware, handles interrupts and management messages, tracks device-map changes, and implements suspend/resume, shutdown, abort, and bus-reset recovery.

## Important APIs and functions
- Module parameters: `msix_enable`, `msi_enable`, `host_can_queue`, `cmd_per_lun`, `dma_mask_64`, `set_date_time`, and `cmd_timeout`.
- SCSI integration uses `arcmsr_scsi_host_template`, with `queuecommand`, `eh_abort_handler`, `eh_bus_reset_handler`, `bios_param`, `sdev_configure`, `change_queue_depth`, `shost_groups`, and queue limits.
- PCI integration uses `arcmsr_device_id_table`, `arcmsr_pci_driver`, `arcmsr_probe()`, `arcmsr_remove()`, `arcmsr_shutdown()`, `arcmsr_suspend()`, and `arcmsr_resume()`.
- Resource setup includes `arcmsr_set_dma_mask()`, `arcmsr_remap_pciregion()`, `arcmsr_alloc_io_queue()`, `arcmsr_alloc_ccb_pool()`, optional `arcmsr_alloc_xor_buffer()`, `arcmsr_request_irq()`, `arcmsr_iop_init()`, `arcmsr_alloc_sysfs_attr()`, and `scsi_scan_host()`.
- Command path is `arcmsr_queue_command_lck()` -> `arcmsr_get_freeccb()` -> `arcmsr_build_ccb()` -> `arcmsr_post_ccb()`; completion is via adapter-specific postqueue ISR -> `arcmsr_drain_donequeue()` -> `arcmsr_report_ccb_state()` -> `arcmsr_ccb_complete()`.
- Management path is exposed both as SCSI virtual target 16 (`arcmsr_handle_virtual_command()`, `arcmsr_iop_message_xfer()`) and sysfs (`arcmsr_Read_iop_rqbuffer_data()`, `arcmsr_write_ioctldata2iop()`, `arcmsr_clear_iop2drv_rqueue_buffer()`).
- Firmware/config paths include `arcmsr_wait_firmware_ready()`, adapter-specific `*_get_config()`, `arcmsr_get_adapter_config()`, `arcmsr_iop_confirm()`, `arcmsr_request_device_map()`, and `arcmsr_message_isr_bh_fn()`.
- Error handling and recovery include `arcmsr_abort()`, adapter-specific polling completion helpers, `arcmsr_bus_reset()`, `arcmsr_iop_reset()`, `arcmsr_hardware_reset()`, `arcmsr_reset_in_progress()`, `arcmsr_abort_allcmd()`, and `arcmsr_done4abort_postqueue()`.

## Control flow
Probe enables the PCI device, allocates a `Scsi_Host`, initializes `AdapterControlBlock` locks and flags, requests BARs, maps the generation-specific register region, allocates queue resources, asks firmware for config, sizes the CCB pool and SCSI host limits, registers the host, requests IRQ vectors, initializes the IOP, starts the periodic device-map timer, optionally starts the time-sync timer, creates sysfs management files, and scans the host.

Normal command flow begins in `arcmsr_queue_command_lck()`. Commands to target 16 are treated as virtual management commands; all other commands acquire a free CCB, build an Areca firmware CDB with SG entries from `scsi_dma_map()`, increment the outstanding count, mark the CCB started, and post it using the adapter-specific queue protocol. Interrupt handlers dispatch by adapter type and drain doorbell events, postqueue completions, and message completions. Completion maps firmware device status to SCSI results, copies sense data when needed, unmaps DMA, returns the CCB to the free list, decrements the outstanding counter, and calls `scsi_done()`.

Device-map refresh is timer-driven. Every six seconds, unless a get-config, bus reset, or abort is active, the driver posts a get-config message. The message ISR schedules bottom-half work, which compares the firmware device map against `acb->device_map` and calls `scsi_add_device()` or `scsi_remove_device()` for changed target/lun slots.

Suspend and shutdown disable interrupts, stop timers/work, stop background rebuild, and flush adapter cache. Resume restores DMA mask/IRQs, resets generation-specific queue pointers/doorbells, reinitializes the IOP, and restarts timers. Remove has a hot-unplug path when PCI device ID reads `0xffff`, and otherwise drains outstanding commands before freeing IRQs, DMA, mappings, regions, and host state.

## State and persistence behavior
Persistent disk state is not owned by this file; it controls live controller state and firmware-visible DMA state. The important volatile state is `AdapterControlBlock`: firmware config, device map, free CCB list, outstanding counter, queue indices, ring buffers, interrupt masks, doorbell toggle shadows, timers, work item, and reset/abort flags. Firmware may persist controller cache and RAID state; the driver explicitly flushes cache and starts/stops background rebuild around lifecycle and management operations. Optional date/time sync writes current system time to firmware periodically when enabled.

## Dependencies and integration points
This file depends heavily on Linux PCI, DMA mapping/coherent allocation, interrupt vector allocation, SCSI midlayer APIs, block queue timeout configuration, timers, workqueues, spinlocks, circular buffers, and I/O memory accessors. It integrates with `arcmsr.h` for all hardware ABI details and with `arcmsr_attr.c` for sysfs management endpoints. It also references SCSI CAM geometry (`scsi_partsize`) and exposes `MODULE_DEVICE_TABLE` for hotplug/autoload.

## Risks and edge cases
- The driver has many adapter-specific branches. Type E and Type F share several helpers by layout compatibility, but Type F uses host memory for message buffers and completion sentinels; misrouting can corrupt DMA state.
- CCB address conversion relies on `vir2phy_offset`, CDB physical address high parts, and firmware-specific encoded completion flags. Address-high/page-boundary mistakes can complete the wrong CCB.
- `arcmsr_build_ccb()` returns `FAILED` after `scsi_dma_map()` errors, but the queue path does not return the acquired CCB to the free list in that failure branch; this is a leak risk in error paths.
- `arcmsr_hbaE_polling_ccbdone()` advances `doneq_index` before reading `cmdFlag`, then checks `acb->pCompletionQ[doneq_index].cmdFlag`, which may refer to the next entry. That is a subtle abort-polling correctness risk.
- Bus reset has long sleeps and retry loops and sets `FW_DEADLOCK` on timeout; user management commands reflect this state with `ARCMSR_MESSAGE_RETURNCODE_BUS_HANG_ON`.
- Hotplug scans are derived from firmware device-map bytes and limited target/lun loops. Bad firmware data or stale flags could add/remove the wrong SCSI devices.
- Management buffers are shared between sysfs, SCSI virtual commands, and interrupt handlers. Locking and overflow flags are critical to avoid lost or duplicated management payloads.
- Remove path includes a comment noting `arcmsr_interrupt(acb)` polling needs a spinlock, indicating a known concurrency risk during teardown with outstanding commands.

## Test signals
- Compile with all relevant configs and exercise probe for each adapter type where hardware or emulation exists.
- Verify MSI-X/MSI/INTx fallback and interrupt-driven completions under parallel I/O.
- Run SCSI read/write, queue-depth changes, SG-heavy commands, check-condition sense propagation, and target 16 management commands.
- Exercise sysfs `mu_read`, `mu_write`, `mu_clear`, and host attributes together with firmware utility tools.
- Test periodic hotplug: firmware device-map additions/removals should trigger `scsi_add_device()` and `scsi_remove_device()`.
- Exercise suspend/resume, shutdown, module remove, surprise removal, abort, and bus reset while I/O is outstanding.
- Watch `host_driver_posted_cmd`, `num_resets`, `num_aborts`, kernel logs, and SCSI error-handler return values for regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr_hba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/Kconfig

## Purpose
This Kconfig file defines build-time options for legacy Acorn ARM SCSI host drivers under `drivers/scsi/arm`. It gates each card driver on `ARCH_ACORN && SCSI` and selects SPI transport attributes for drivers that expose traditional parallel SCSI parameters.

## Important configuration symbols
- `SCSI_ACORNSCSI_3`: tristate support for the Acorn SCSI card (`aka30`), depends on `ARCH_ACORN && SCSI`, selects `SCSI_SPI_ATTRS`.
- `SCSI_ACORNSCSI_SYNC`: bool enabling SCSI-2 synchronous transfer negotiation for `SCSI_ACORNSCSI_3`.
- `SCSI_ARXESCSI`: tristate support for an ARXE NCR53c94-based controller on Acorn Archimedes systems.
- `SCSI_CUMANA_2`: tristate support for Cumana SCSI II.
- `SCSI_EESOXSCSI`: tristate support for EESOX SCSI.
- `SCSI_POWERTECSCSI`: tristate support for PowerTec SCSI.
- `SCSI_CUMANA_1` and `SCSI_OAK1`: marked after a comment as not fully supported; both depend on `ARCH_ACORN && SCSI`, and `SCSI_OAK1`/`SCSI_CUMANA_1` select `SCSI_SPI_ATTRS`.

## Control flow and state behavior
Kconfig has declarative build control rather than runtime flow. User selections determine which object lists in the adjacent Makefile become built-in or modules. `SCSI_ACORNSCSI_SYNC` is a feature flag consumed by the Acorn SCSI implementation for synchronous negotiation behavior.

## Persistence behavior
Selections persist in the kernel `.config`, not in runtime driver state. The file does not store data or affect runtime persistence directly.

## Dependencies and integration points
The file integrates with the kernel Kconfig menu for SCSI drivers and the `drivers/scsi/arm/Makefile`. It depends on architecture support (`ARCH_ACORN`), the SCSI core, and, for selected drivers, `SCSI_SPI_ATTRS`.

## Risks and edge cases
- These drivers are architecture-specific and legacy; enabling them outside Acorn ARM hardware is prevented by dependency checks.
- The "not fully supported" comment covers CumanaSCSI I and Oak SCSI, signalling higher maintenance and runtime risk.
- `SCSI_ACORNSCSI_SYNC` can improve performance but the help text warns that some devices mishandle synchronous transfer negotiation.

## Test signals
- Kconfig tests should verify symbols appear only for `ARCH_ACORN && SCSI`.
- Build tests should cover `y` and `m` selections for each tristate and synchronous negotiation enabled/disabled for Acorn SCSI.
- Runtime tests require real or emulated Acorn SCSI hardware, with special attention to synchronous negotiation compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/Makefile

## Purpose
This Makefile maps the ARM/Acorn SCSI Kconfig symbols to the object files built into the kernel or loadable modules.

## Important build rules
- `acornscsi_mod-objs := acornscsi.o acornscsi-io.o` builds the Acorn SCSI driver from its C implementation and ARM assembly I/O helper.
- `obj-$(CONFIG_SCSI_ACORNSCSI_3) += acornscsi_mod.o queue.o msgqueue.o`
- `obj-$(CONFIG_SCSI_ARXESCSI) += arxescsi.o fas216.o queue.o msgqueue.o`
- `obj-$(CONFIG_SCSI_CUMANA_1) += cumana_1.o`
- `obj-$(CONFIG_SCSI_CUMANA_2) += cumana_2.o fas216.o queue.o msgqueue.o`
- `obj-$(CONFIG_SCSI_OAK1) += oak.o`
- `obj-$(CONFIG_SCSI_POWERTECSCSI) += powertec.o fas216.o queue.o msgqueue.o`
- `obj-$(CONFIG_SCSI_EESOXSCSI) += eesox.o fas216.o queue.o msgqueue.o`

## Control flow and state behavior
The file has no runtime control flow. Kbuild expands each `obj-$()` assignment according to `.config` and links common helper objects (`fas216.o`, `queue.o`, `msgqueue.o`) into each selected module or built-in target as required.

## Persistence behavior
There is no runtime persistence. Build output depends on the persistent kernel configuration and Kbuild's generated artifacts.

## Dependencies and integration points
This Makefile integrates with the Kconfig symbols in the same directory and with the kernel SCSI build. Several drivers share `fas216`, queue, and message-queue helper modules, while the Acorn SCSI card additionally uses the assembly file researched in this work item.

## Risks and edge cases
- Shared objects listed under multiple `obj-$()` lines can be linked into multiple modules depending on Kbuild composition; changes to helper names or module grouping must preserve Kbuild semantics.
- `acornscsi-io.o` is architecture assembly and must only be built in compatible ARM/Acorn configurations.
- Misaligning object lists with Kconfig options can cause unresolved symbols or missing low-level transfer helpers.

## Test signals
- Build each configured driver as module and built-in where supported.
- Confirm `acornscsi_mod.o` includes both `acornscsi.o` and `acornscsi-io.o`.
- Verify helper object dependencies remain satisfied for ARXE, Cumana II, PowerTec, and EESOX builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi-io.S -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi-io.S

## Purpose
`acornscsi-io.S` provides low-level ARM assembly block transfer routines for the Acorn SCSI card. It converts between the card's memory-mapped data presentation and normal byte streams in system memory, optimized for 16-, 8-, 4-, and 2-byte tails.

## Important APIs and routines
- `ENTRY(__acornscsi_in)`: prototype comment says `void acornscsi_in(unsigned int addr_start, char *buffer, int length)`. It reads from the SCSI card address in `r0` into the destination buffer in `r1` for `r2` bytes.
- `ENTRY(__acornscsi_out)`: prototype comment appears to repeat `acornscsi_in`, but the routine writes from memory buffer `r1` to card address `r0` for `r2` bytes.
- `LOADREGS` abstracts APCS-32 vs APCS-26 return register restoration, using `ldm...` with `^` for 26-bit APCS.

## Control flow and data transformation
Both routines align the card address down to a word boundary with `bic r0, r0, #3`. The input path loads words from the card, masks low 16-bit data using `0xffff`, combines pairs into normal 32-bit words, and stores to the destination buffer. It loops in 16-byte chunks, then handles 8-byte, 4-byte, and 1/2-byte residual cases. The output path performs the inverse transformation: it loads normal 32-bit words from memory, duplicates/shifts halfwords into the form expected by the card, stores them to the memory-mapped address, and then handles smaller residual lengths.

## State and persistence behavior
The routines are stateless aside from register saves/restores and the direct memory side effects of reading or writing the device-mapped address range and system buffer. They do not allocate memory, sleep, or maintain persistent data.

## Dependencies and integration points
The file depends on ARM assembler conventions, `<linux/linkage.h>`, `<asm/assembler.h>`, and Acorn machine hardware definitions. It is linked into `acornscsi_mod.o` by `drivers/scsi/arm/Makefile` and is called by the Acorn SCSI C driver for PIO-style data transfers.

## Risks and edge cases
- The routines assume ARM mode/register ABI and Acorn-specific bus layout; they are not portable across architectures.
- Address alignment is forced downward, so callers must pass an address compatible with the card's data window semantics.
- Residual handling uses condition flags from arithmetic on `r2`; off-by-one length bugs would corrupt trailing bytes.
- The input path uses low 16-bit masking, and the output path mirrors halfwords into words; any hardware change in data-lane layout would require assembly changes.
- The comment above `__acornscsi_out` names `acornscsi_in`, likely a copy/paste documentation error.

## Test signals
- Build should assemble this file for the intended ARM/APCS configuration.
- Functional testing should transfer buffers of lengths covering 0/1/2/3/4/8/16 and non-multiple tails, verifying byte-exact round trips where hardware permits.
- Runtime stress should cover unaligned card-window starts, high transfer lengths, and integration with the Acorn SCSI command data phase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi-io.S -->
