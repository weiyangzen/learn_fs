# Research Group: subset-b-005231

This grouped report covers the AIC79xx Linux SCSI host adapter glue, PCI attachment/configuration logic, procfs diagnostics, AIC7xxx shared core definitions, and 93Cx6 serial EEPROM helpers. Each file section is bounded with reconciliation markers so the guard can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_inline.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_inline.h

## Purpose

`aic79xx_inline.h` provides small, OS-neutral inline helpers and forward declarations for the AIC79xx/AHD core. It is included by Linux OSM and PCI glue after the platform header has defined `struct ahd_softc`, register access primitives, SCB structures, and mode constants. The file deliberately keeps only thin helpers here: mode-state packing, name access, scatter/gather sizing, sense-buffer address access, and interrupt/core API declarations.

## Important APIs, Types, and Functions

- `ahd_name(struct ahd_softc *ahd)` returns `ahd->name` for diagnostics.
- `ahd_known_modes()`, `ahd_build_mode_state()`, and `ahd_extract_mode_state()` maintain and encode/decode the controller source/destination register window modes using `SRC_MODE_SHIFT`, `DST_MODE_SHIFT`, `SRC_MODE`, and `DST_MODE`.
- Sequencer-control declarations `ahd_set_modes()`, `ahd_save_modes()`, `ahd_restore_modes()`, `ahd_is_paused()`, `ahd_pause()`, and `ahd_unpause()` are implemented in the core and are used throughout PCI/proc/error-recovery paths before touching mode-dependent registers.
- `ahd_sg_size()` chooses `struct ahd_dma64_seg` when `AHD_64BIT_ADDRESSING` is set, otherwise `struct ahd_dma_seg`.
- `ahd_get_sense_buf()` and `ahd_get_sense_bufaddr()` expose per-SCB autosense storage and bus address.
- Hardware access and queue helpers are declared: `ahd_inw/outw`, `ahd_inl/outl`, `ahd_inq/outq`, `ahd_get_scbptr()`, `ahd_set_scbptr()`, SCB RAM reads, `ahd_lookup_scb()`, `ahd_queue_scb()`, and `ahd_intr()`.

## Control Flow and State

The file has no independent runtime flow. Its inline mode helpers mutate cached fields in `struct ahd_softc` so later core/OS code can avoid redundant mode reads or restore a previously saved mode pair. Sense helpers are pure accessors over `struct scb`. SG sizing depends on the adapter flags selected during PCI DMA mask negotiation.

## Dependencies and Integration Points

This header depends on the AHD core definitions from `aic79xx.h`, Linux platform typedefs from `aic79xx_osm.h`, and generated register constants. It is consumed by `aic79xx_osm.c`, `aic79xx_osm_pci.c`, `aic79xx_pci.c`, and `aic79xx_proc.c` to bridge Linux paths to core routines without duplicating platform-specific logic.

## Risks

- Mode-state helpers assume the encoded mode bit fields and shifts match the hardware/core constants; drift would corrupt register-window restoration.
- `ahd_sg_size()` is only correct if `AHD_64BIT_ADDRESSING` is set consistently with the DMA segment format used when building S/G lists.
- Sense-buffer helpers trust SCB allocation invariants; bad SCB lifetime or partially initialized SCBs will surface as stale sense data or bad DMA addresses elsewhere.

## Test Signals

- Compile coverage from all AIC79xx translation units validates declarations and inline dependencies.
- Runtime signals include successful command completion with autosense, correct mode restoration around procfs SEEPROM writes, and no register access failures during PCI memory-mapped probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm.c

## Purpose

`aic79xx_osm.c` is the Linux operating-system module for the Adaptec AIC790x Ultra320 SCSI driver. It adapts the portable AHD core to the Linux SCSI mid-layer, SPI transport class, PCI config wrappers, DMA allocation model, IRQ handling, module parameters, queue-depth policy, error recovery, and command completion semantics.

## Important APIs, Types, and Functions

- Module configuration globals include `aic79xx_no_reset`, `aic79xx_extended`, `aic79xx_pci_parity`, `aic79xx_allow_memio`, `aic79xx_seltime`, `aic79xx_periodic_otag`, `aic79xx_slowcrc`, `aic79xx_verbose`, `aic79xx_tag_info[]`, and per-adapter I/O cell options.
- `aic79xx_setup()` parses boot/module strings, including brace-form `tag_info`, `slewrate`, `precomp`, and `amplitude` lists through `ahd_parse_brace_option()`.
- `aic79xx_driver_template` exports Linux SCSI callbacks: queue command, abort, device reset, bus reset, host info, proc info/write hooks, target and device allocation/configuration, and i386 BIOS geometry.
- Low-level accessors `ahd_inb()`, `ahd_outb()`, `ahd_outw_atomic()`, `ahd_insb()`, `ahd_outsb()`, `ahd_pci_read_config()`, and `ahd_pci_write_config()` abstract memory-mapped versus PIO register access and Linux PCI config APIs.
- DMA shims `ahd_dma_tag_create()`, `ahd_dmamem_alloc()`, `ahd_dmamem_free()`, and `ahd_dmamap_load()` map the BSD-style core DMA contract onto Linux coherent DMA allocation.
- Host/device lifecycle functions include `ahd_linux_register_host()`, `ahd_linux_initialize_scsi_bus()`, `ahd_platform_alloc()`, `ahd_platform_free()`, `ahd_platform_init()`, `ahd_linux_target_alloc()`, `ahd_linux_target_destroy()`, `ahd_linux_sdev_init()`, and `ahd_linux_sdev_configure()`.
- Command path functions include `ahd_linux_queue_lck()`, `ahd_linux_run_command()`, `ahd_done()`, `ahd_linux_handle_scsi_status()`, and `ahd_linux_queue_cmd_complete()`.
- Error recovery functions include `ahd_linux_abort()`, `ahd_linux_queue_abort_cmd()`, `ahd_linux_dev_reset()`, and `ahd_linux_bus_reset()`.
- SPI transport setters `ahd_linux_set_width()`, `ahd_linux_set_period()`, `ahd_linux_set_offset()`, `ahd_linux_set_dt()`, `ahd_linux_set_qas()`, `ahd_linux_set_iu()`, `ahd_linux_set_rd_strm()`, `ahd_linux_set_wr_flow()`, `ahd_linux_set_rti()`, `ahd_linux_set_pcomp_en()`, `ahd_linux_set_hold_mcs()`, and `ahd_linux_get_signalling()` connect sysfs/SPI transport requests to AHD negotiation state.

## Control Flow and State

Module initialization optionally parses `aic79xx`, attaches an SPI transport template, reserves per-device transport storage for `struct ahd_linux_device`, then delegates PCI registration to `ahd_linux_pci_init()`. Probe and core configuration happen in the PCI files, then `ahd_linux_register_host()` allocates a `Scsi_Host`, stores the `ahd_softc` pointer in `hostdata`, sets queue and topology limits, initializes/reset-negotiates the bus, enables interrupts, calls `scsi_add_host()`, and starts scanning.

The normal I/O path starts at `ahd_linux_queue_lck()`, sets the CAM status field in `cmd->result`, and calls `ahd_linux_run_command()`. That routine maps Linux scatterlist DMA, allocates an SCB, fills hardware SCB fields such as `scsiid`, `lun`, CDB, control bits, tag attribute, negotiation flags, and S/G list, updates per-device counters (`openings`, `active`, `commands_issued`, ordered-tag interval), links the SCB into `pending_scbs`, and queues it to the sequencer. Completion enters through `ahd_linux_isr()` -> `ahd_intr()` -> core completion -> `ahd_done()`, which removes the SCB, unmaps DMA, converts transmission or SCSI status into CAM state, adjusts adaptive tag counters, frees the SCB, maps CAM status to Linux `DID_*`, and calls `scsi_done()`.

Error recovery pauses the controller and reasons about whether the timed-out command is queued, active on the bus, or disconnected. Aborts can remove commands from QINFIFO, assert ATN for active commands, or requeue a disconnected SCB with task-management state. Device reset builds a recovery SCB carrying `SIU_TASKMGMT_LUN_RESET` and waits on a completion. Bus reset calls the core channel reset and reports success to the mid-layer.

Queue-depth state is persistent per Linux SCSI device in `struct ahd_linux_device`: active/opening counts, queue-freeze count, max tags, queue-full history, tag success count, and periodic ordered-tag accounting. The driver throttles on `TASK_SET_FULL`, slowly grows openings after successful completions, and can lock a fixed tag depth after repeated queue-full responses at the same depth.

## State and Persistence Behavior

Persistent module/global state comes from kernel config and module parameters. Per-adapter state lives in `struct ahd_platform_data` and `struct ahd_softc`; per-target SPI state is stored in Linux `scsi_target` transport fields and AHD transinfo tables; per-LUN queue state is in transport-reserved `struct ahd_linux_device`. There is no filesystem persistence here, but SEEPROM-backed policy read by PCI code influences target allocation defaults, and procfs write support in `aic79xx_proc.c` can update adapter NVRAM.

## Dependencies and Integration Points

The file integrates Linux SCSI mid-layer headers, SPI transport helpers, PCI config APIs, DMA mapping APIs, IRQ APIs, and core AHD files. It expects PCI attachment from `aic79xx_osm_pci.c`, chip setup from `aic79xx_pci.c`, core SCB/sequencer functions from `aic79xx.c` and generated register definitions, and procfs display/write functions from `aic79xx_proc.c`.

## Risks

- The command path is sensitive to lock ordering and pause/unpause correctness; missed locking can corrupt `pending_scbs`, device openings, or sequencer mode state.
- `ahd_delay()` uses `usec % 1024`, so exact delays above 1024 microseconds are chunked in a non-obvious way and should be reviewed if timing-sensitive code changes.
- Error recovery has multiple paths that wait up to five seconds; stale `eh_done` or missed completion can make recovery fail and escalate resets.
- Queue-depth adaptation assumes queue-full semantics reflect target resource pressure; unusual targets can oscillate or underutilize tags.
- Low-level memory-mapped I/O relies on barriers after byte accesses; architecture-specific ordering changes need careful validation.

## Test Signals

- Build with `CONFIG_SCSI_SPI_ATTRS`, PCI, and AIC79xx options enabled.
- Probe an AIC7901/AIC7902 controller and confirm `scsi_add_host()`, `scsi_scan_host()`, IRQ registration, and SPI transport attributes are present.
- Exercise normal reads/writes with S/G DMA and autosense paths, including check-condition sense copying.
- Force `QUEUE FULL`, abort, target reset, and bus reset paths and confirm command completion status maps to Linux `DID_*` values without leaks in `active/openings`.
- Validate module parameter parsing for global tag depth and per-adapter/per-target brace lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm.h

## Purpose

`aic79xx_osm.h` is the Linux platform contract for the portable AIC79xx/AHD core. It imports Linux kernel, PCI, and SCSI headers; defines BSD-style bus/DMA typedefs expected by the core; declares Linux OSM entry points; defines per-device/per-adapter platform state; and provides inline wrappers for status, residual, sense, locking, PCI identity, and queue-freeze behavior.

## Important APIs, Types, and Functions

- Platform typedefs include `ahd_dev_softc_t` as `struct pci_dev *`, `ahd_io_ctx_t` as `struct scsi_cmnd *`, `bus_space_tag_t`, `bus_space_handle_t`, `bus_dma_segment_t`, `bus_dma_tag_t`, and `bus_dmamap_t`.
- `struct ahd_linux_dma_tag` stores the simplified Linux DMA allocation constraints used by the core shims.
- `enum ahd_linux_dev_flags` and `struct ahd_linux_device` track per-LUN queue state, active/opening counts, queue freeze, tag-depth adaptation, and periodic ordered tag behavior.
- `struct scb_platform_data` stores Linux-specific SCB state: device pointer, buffer bus address, transfer length, and autosense residual.
- `struct ahd_platform_data` stores interrupt-safe adapter state: target pointers, spinlock, error-handler completion, `Scsi_Host`, IRQ, BIOS address, and memory BAR bus address.
- Inline locking wrappers `ahd_lockinit()`, `ahd_lock()`, and `ahd_unlock()` use `spin_lock_irqsave()` around core critical sections.
- Transaction wrappers manipulate Linux `scsi_cmnd->result` with CAM status in the upper word and SCSI status in the lower word; residual wrappers use `scsi_set_resid()` and `scsi_get_resid()`.
- PCI helpers expose config register constants, PCI-X status masks, bus/slot/function accessors, and `ahd_flush_device_writes()`.

## Control Flow and State

This header does not implement a standalone flow, but it shapes every Linux AHD path. The SCSI queue path stores CAM state in `cmd->result`, uses `struct scb_platform_data` for per-command transfer metadata, and updates `struct ahd_linux_device` counters. The PCI attach path fills `struct ahd_platform_data`, maps registers using the bus-space fields in `struct ahd_softc`, and stores the IRQ/host for later removal.

## Dependencies and Integration Points

The header depends on Linux SCSI mid-layer, SPI transport, PCI, interrupt, module, byteorder, and I/O APIs. It includes `cam.h`, `queue.h`, `scsi_message.h`, `scsi_iu.h`, `aiclib.h`, and finally the portable `aic79xx.h`, making it the bridge between Linux and the OS-neutral AHD core. It declares functions implemented by `aic79xx_osm.c`, `aic79xx_osm_pci.c`, and `aic79xx_proc.c`.

## Risks

- The `scsi_cmnd->result` encoding must remain consistent with `ahd_linux_queue_cmd_complete()`; any mid-layer API change around result bytes can break status mapping.
- `ahd_dmamap_sync()` is intentionally a no-op for coherent memory, with a comment noting possible architecture uncertainty.
- `ahd_flush_device_writes()` relies on an `INTSTAT` read to flush writes, which may be insufficient on some architectures if I/O ordering assumptions change.
- Per-target indexing assumes channel B, when present, is represented by offset `+8`; wrong topology assumptions would corrupt target state lookup.

## Test Signals

- Full driver compile catches platform/core type-contract drift.
- Runtime tests should verify spinlock-protected queueing/completion, status/result mapping, residual updates, procfs info, PCI resource mapping, and target transport attribute visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm_pci.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm_pci.c

## Purpose

`aic79xx_osm_pci.c` is the Linux PCI-driver glue for AIC790x Ultra320 controllers. It exposes the Linux `pci_driver`, matches supported PCI IDs, handles probe/remove and power management callbacks, negotiates DMA masks, maps device registers, requests interrupts, and delegates hardware-specific configuration to `aic79xx_pci.c`.

## Important APIs, Types, and Functions

- `ahd_linux_pci_id_table[]` lists known adapters and generic AIC7901/AIC7902 probes using ID macros from `aic79xx_pci.h`.
- `aic79xx_pci_driver` provides `.probe`, `.remove`, `.id_table`, and SIMPLE_DEV_PM_OPS.
- `ahd_linux_pci_dev_probe()` performs identity lookup, softc allocation, `pci_enable_device()`, bus mastering, DMA mask selection, core PCI configuration, multi-function BIOS flag inheritance, driver-data storage, and host registration.
- `ahd_linux_pci_dev_remove()` removes the SCSI host, disables interrupts under lock, and frees the softc.
- `ahd_linux_pci_dev_suspend()` and `ahd_linux_pci_dev_resume()` sequence core suspend/resume with PCI state save/restore.
- `ahd_pci_map_registers()` prefers memory-mapped I/O when allowed and safe, validates the mapping with `ahd_pci_test_register_access()`, and falls back to PIO BARs.
- `ahd_pci_map_int()` requests the shared IRQ with `ahd_linux_isr()`.
- `ahd_power_state_change()` maps the core power-state enum to `pci_set_power_state()`.

## Control Flow and State

On module initialization, `ahd_linux_pci_init()` registers the PCI driver. Probe starts by mapping the Linux `pci_dev` to a core identity with `ahd_find_pci_device()`. The softc name encodes bus/slot/function. The driver enables the device, sets bus mastering, chooses 64-bit, 39-bit, or 32-bit DMA based on `dma_get_required_mask()` and `dma_set_mask()`, then calls `ahd_pci_config()`. Multi-function devices on nonzero functions inherit `AHD_BIOS_ENABLED` from function 0. If configuration succeeds, the `pci_dev` driver data receives the softc and the SCSI host is registered.

Register mapping clears memory/port enable bits while probing resources. The memory path reserves BAR1, maps the containing page, sets both AHD register windows to memory space, enables memory access, and tests register access. On failure it unmaps/releases and falls back to PIO, reserving BAR0 and the secondary I/O BAR at index 3. Final command register bits are written after a path is chosen.

## State and Persistence Behavior

The file stores the softc in PCI driver data, records IRQ and memory BAR bus address in `struct ahd_platform_data`, and records DMA addressing capability in `ahd->flags`. It does not persist data across reboot. Suspend saves core and PCI state through functions in other files; resume restores and restarts the controller through the same split.

## Dependencies and Integration Points

This file depends on Linux PCI/device/IRQ/resource APIs, `aic79xx_osm.h` for platform state and locks, `aic79xx_inline.h` for core helpers, and `aic79xx_pci.h` for ID constants. It integrates with `aic79xx_pci.c` for identity and chip configuration and with `aic79xx_osm.c` for ISR and host registration.

## Risks

- In the allocation error path after `kstrdup()` succeeds but `ahd_alloc()` fails, the local name buffer is not explicitly freed unless `ahd_alloc()` assumes ownership only on success; this is worth checking against core allocation behavior.
- The 64-bit BAR comment notes Linux PCI BAR indexing ambiguity; resource assumptions can break on unusual bridges.
- Memory mapping is disabled for `AHD_PCIX_MMAPIO_BUG` and falls back to PIO, so regressions in bug flags can expose broken MMIO behavior.
- Remove assumes `pci_get_drvdata()` is valid and that `ahd_free()` handles all mapped resources and IRQs.

## Test Signals

- PCI ID matching should bind all known AHA-29320/AHA-39320 variants and generic AIC790x devices.
- Probe logs should show successful resource mapping, DMA mask selection, IRQ request, and SCSI host registration.
- Force `aic79xx_allow_memio=0` and MMIO-test failure scenarios to validate PIO fallback.
- Suspend/resume and hot-remove tests should confirm interrupts are disabled and resources are released without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_pci.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_pci.c

## Purpose

`aic79xx_pci.c` contains product-specific probe, setup, and PCI error handling for AIC7901/AIC7902 Ultra320 controllers. It maps PCI IDs to controller descriptions/setup functions, configures chip features and revision workarounds, validates register access, reads SEEPROM/VPD or fallback scratch settings, configures termination, and handles PCI/PCI-X error interrupts.

## Important APIs, Types, and Functions

- `ahd_pci_ident_table[]` maps full PCI/subsystem IDs to names and setup functions.
- `ahd_compose_id()` builds the 64-bit identity from device/vendor/subdevice/subvendor.
- `ahd_find_pci_device()` reads PCI config identity, masks HostRAID/IROC bits, and returns a matching identity table entry.
- `ahd_pci_config()` is the main attach sequence after Linux PCI enablement: setup entry, bus mode detection, power D0, register mapping, DAC enable, bus mastering, softc init, reset, SEEPROM/termination check, core init, and IRQ mapping.
- `ahd_pci_suspend()` and `ahd_pci_resume()` save/restore PCI config fields used after resets and power transitions.
- `ahd_pci_test_register_access()` verifies the selected register mapping by pausing, clearing PCI errors, writing/reading SRAM, and checking PCI error status.
- `ahd_check_extport()` reads VPD and SEEPROM, verifies checksum, falls back to BIOS scratch SCB settings, or applies defaults.
- `ahd_configure_termination()` programs termination and STPWLEVEL from adapter control bits and flexport state.
- `ahd_pci_intr()` and `ahd_pci_split_intr()` dump/clear PCI and PCI-X split completion errors.
- `ahd_aic7901_setup()`, `ahd_aic7901A_setup()`, `ahd_aic7902_setup()`, and `ahd_aic790X_setup()` set chip/features/bugs and revision-specific I/O cell defaults.

## Control Flow and State

Attach starts with `ahd_find_pci_device()` and then `ahd_pci_config()`. The selected identity names the adapter and supplies the setup function. Setup sets `ahd->chip`, feature bits, channel letter from PCI function, and revision-dependent bug/workaround flags. `ahd_pci_config()` then classifies PCI versus PCI-X bus mode from `DEVCONFIG`, powers the device to D0, maps registers through the Linux OSM, enables dual-address cycles for high DMA addressing, enables bus mastering, initializes the softc, resets the chip, caches PCI cacheline size, switches to SCSI mode, reads NVRAM/configuration, initializes the core, increments `init_level`, and maps the interrupt.

SEEPROM flow first tries external port acquisition. If present, it reads VPD for the current function, parses it, reads the function-specific `struct seeprom_config`, verifies checksum, and releases the SEEPROM. If unavailable, it looks for BIOS signatures in SCB scratch RAM and reconstructs config words. If neither path succeeds, it sets `AHD_USEDEFAULTS`, runs default config, frees `seep_config`, and configures auto-termination defaults.

PCI error flow enters through the core bus interrupt hook. Split interrupts read and clear per-mode DCH/SG split status registers plus PCI-X status. PCI errors read and clear per-source PCI status registers, dump card state, clear conventional PCI status, restore modes, clear `PCIINT`, and unpause.

## State and Persistence Behavior

The file sets long-lived hardware state in `ahd->chip`, `ahd->features`, `ahd->bugs`, `ahd->flags`, `ahd->bus_description`, `ahd->pci_cachesize`, `ahd->channel`, termination flags, and `ahd->seep_config`. SEEPROM reads are persistent hardware configuration; writes are handled in `aic79xx_proc.c`. Suspend state is saved in `ahd->suspend_state.pci_state`.

## Dependencies and Integration Points

It depends on platform register and PCI config wrappers from `aic79xx_osm.c`, ID macros from `aic79xx_pci.h`, core initialization/reset/config parsing functions, flexport/SEEPROM helpers, and register definitions. It is called by `aic79xx_osm_pci.c` during probe and by the core interrupt path for PCI-specific errors.

## Risks

- Identity matching masks HostRAID/IROC bits; incorrect masks could bind unsupported RAID-mode devices or miss supported OEM devices.
- Revision workaround flags are dense and hardware-specific; removing or misapplying one can cause data corruption, failed aborts, or broken packetized transfers.
- `ahd_pci_test_register_access()` deliberately writes SRAM and manipulates error status; changes here need real hardware validation.
- SEEPROM fallback to scratch RAM trusts legacy BIOS signatures and word layout; endian or offset mistakes would apply wrong target/termination policy.
- Termination programming affects physical bus stability; bad flexport detection can cause device discovery or data integrity failures.

## Test Signals

- Probe known AIC7901/AIC7902 revisions and confirm the correct features, bug flags, bus mode description, DMA addressing, and channel letter.
- Validate SEEPROM present, checksum-failure, and no-SEEPROM fallback cases.
- Exercise MMIO register access test and PIO fallback.
- Inject or observe PCI/PCI-X errors and confirm interrupts are logged, latched status bits are cleared, and normal interrupts resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_pci.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_pci.h

## Purpose

`aic79xx_pci.h` defines the 64-bit PCI/subsystem identity constants and masks used by the AIC79xx PCI OS glue and hardware configuration code. It is a small data header that keeps known adapter IDs separate from attach logic.

## Important APIs, Types, and Functions

- Mask constants include `ID_ALL_MASK`, `ID_ALL_IROC_MASK`, `ID_DEV_VENDOR_MASK`, `ID_9005_GENERIC_MASK`, and `ID_9005_GENERIC_IROC_MASK`.
- Device identity constants cover AIC7901, AIC7901A, AIC7902, AIC7902_B, and retail/OEM AHA-29320/AHA-39320 variants, including Dell and HP subsystem IDs.
- No functions or types are declared in this file.

## Control Flow and State

The header contributes no runtime flow. Its constants are consumed by the Linux `pci_device_id` table in `aic79xx_osm_pci.c` and the core identity table in `aic79xx_pci.c`. The constants encode device/vendor/subdevice/subvendor in the ordering expected by `ahd_compose_id()` and ID table macros.

## Dependencies and Integration Points

The file depends only on integer literal support. It integrates with PCI matching, hardware identity lookup, and generic probe masks. Consistency between these constants and Linux `ID()`, `ID16()`, `ID2C()`, and `IDIROC()` macros elsewhere is required.

## Risks

- A malformed 64-bit ID silently prevents binding or binds the wrong setup routine.
- Generic masks can match devices broader than intended, especially when HostRAID/IROC bits are masked.
- Adding new OEM IDs requires updates in both the Linux PCI table and the core identity table if the device needs a specific name or setup path.

## Test Signals

- Build-time use in both ID tables.
- Runtime `lspci`-matched devices should bind to the expected adapter name in driver logs.
- Generic ID fallback should bind unknown but compatible AIC790x devices without stealing unrelated Adaptec devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_proc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_proc.c

## Purpose

`aic79xx_proc.c` implements procfs-style reporting and SEEPROM write support for the AIC79xx Linux driver. It formats controller, SEEPROM, target negotiation, and per-device queue state into a `seq_file`, and it accepts a full `struct seeprom_config` image for NVRAM updates.

## Important APIs, Types, and Functions

- `ahd_calc_syncsrate()` converts SCSI sync period factors to kHz, using exception entries for FAST-160/80/40/20 and a standard factor fallback.
- `ahd_format_transinfo()` formats `struct ahd_transinfo` as transfer speed, frequency, width, and PPR options.
- `ahd_dump_target_state()` prints user/goal/current negotiation state for one target and iterates LUN devices under the Linux `scsi_target`.
- `ahd_dump_device_state()` prints per-LUN queue counters from `struct ahd_linux_device`.
- `ahd_proc_write_seeprom()` validates size and checksum, pauses the controller, switches to SCSI mode, acquires SEEPROM access, writes the provided config, rereads it into `ahd->seep_config`, and restores mode/pause/lock state.
- `ahd_linux_show_info()` prints driver version, adapter description/controller info, allocated SCBs, S/G length, raw SEEPROM words, and target state for all targets.

## Control Flow and State

Read/display flow starts from Linux SCSI host info callback `show_info`, retrieves `ahd_softc` from `shost->hostdata`, emits high-level adapter data, dumps NVRAM if available, then loops through 8 or 16 targets depending on `AHD_WIDE`. Each target report fetches AHD transinfo and, when Linux target state exists, reports goal/current negotiation and all attached LUN queue counters.

Write flow is conservative: it locks the adapter, pauses if needed, saves register modes, switches to SCSI mode, validates the exact buffer length and checksum, acquires SEEPROM, ensures `seep_config` storage exists, writes the words at the channel-specific offset, rereads the data, releases SEEPROM, restores modes, resumes if this function paused the card, and unlocks.

## State and Persistence Behavior

`ahd_linux_show_info()` is read-only. `ahd_proc_write_seeprom()` is persistent: it writes serial EEPROM hardware, updates the in-memory `ahd->seep_config`, and affects future boots/probes. It returns either the byte count written or `-EINVAL` for validation/access failures.

## Dependencies and Integration Points

The file depends on Linux `seq_file`, SCSI target/device lookup, AHD core transinfo/SEEPROM helpers, `aic79xx_osm.h` platform structures, and `aic79xx_inline.h` pause/mode helpers. Its entry points are referenced by `aic79xx_osm.h` and installed in `aic79xx_driver_template`.

## Risks

- SEEPROM writes require a complete valid image; partial or wrong-sized writes are rejected, but a valid checksum with semantically bad settings can persist bad bus policy.
- The code uses atomic allocation while the adapter is locked/paused; allocation failure leaves the write rejected.
- Device lookup in the target dump must be balanced by the SCSI core semantics; if kernel APIs change, reference handling should be reviewed.
- Reporting assumes `struct ahd_linux_device` exists for each found `scsi_device`.

## Test Signals

- `/proc` or host show-info output should include driver version, controller info, SEEPROM words, and target transfer settings.
- Valid SEEPROM write should return exactly `sizeof(struct seeprom_config)` and reread matching data.
- Invalid length/checksum/no-SEEPROM writes should fail with diagnostic logs and restore controller pause/mode state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx.h

## Purpose

`aic7xxx.h` is the OS-neutral core header for the older AHC/AIC7xxx SCSI controller family. It defines hardware constants, chip/feature/bug/flag enums, SCB layouts, scatter/gather formats, target-mode structures, negotiation state, SEEPROM layout, `struct ahc_softc`, PCI/EISA identity structures, and public core function prototypes.

## Important APIs, Types, and Functions

- Target/path macros derive target, channel, LUN, target masks, and TCL values from SCB fields and controller features.
- Constants define target/LUN limits, maximum transfer size, SCB limits, target-mode command FIFO size, and reset delays.
- Enums `ahc_chip`, `ahc_feature`, `ahc_bug`, and `ahc_flag` describe controller model, capabilities, silicon workarounds, and runtime configuration flags.
- `struct hardware_scb` mirrors the controller SCB layout, including CDB/status/target-mode shared area, data pointer/count, S/G pointer, control, SCSI ID, LUN, tag, rate/offset, and long CDB storage.
- `struct ahc_dma_seg`, `struct sg_map_node`, `enum scb_flag`, `struct scb`, and `struct scb_data` define host-side SCB and DMA/S/G state.
- Target-mode structures include `struct target_cmd`, `struct ahc_tmode_event`, and `struct ahc_tmode_tstate`.
- Negotiation structures include `struct ahc_transinfo`, `struct ahc_initiator_tinfo`, `struct ahc_syncrate`, and `struct ahc_phase_table_entry`.
- `struct seeprom_config` defines the 32-word serial EEPROM layout and many bit fields for per-target and adapter policy.
- `struct ahc_softc` is the central controller state object, combining bus handles, SCB queues, bus-specific/platform data, target state, features/bugs/flags, message buffers, DMA maps, init level, PCI cacheline, identity/name, and user negotiation masks.
- Prototypes cover PCI/EISA attach, SCB management, initialization, reset, error recovery searches, transfer negotiation, target mode, debug, and SEEPROM acquisition.

## Control Flow and State

The file itself has no executable flow, but it documents the core state machine used by AHC implementations. Commands are represented as host SCBs pointing at DMA-safe hardware SCBs. SCBs move through free, pending, queued, disconnected, active, recovery, sense, target, and completion states, with hardware firmware updating shared SCB fields for residuals and status. The `ahc_softc` aggregates queue pointers, sequencer state, message buffers, target negotiation tables, and bus/platform hooks so OS-specific files can attach the same core to PCI, EISA, or VL hardware.

The residual comments are an important behavioral contract: the sequencer and host interpret `sgptr`, `residual_sg_ptr`, `datacnt`, `SG_FULL_RESID`, `SG_LAST_SEG`, and `SG_RESID_VALID` together. This affects how completions calculate underflow and residual data.

## State and Persistence Behavior

Runtime state is in `struct ahc_softc`, `struct scb_data`, and per-target negotiation tables. Persistent adapter policy is represented by `struct seeprom_config`, which is loaded from serial EEPROM or BIOS scratch by bus-specific code and influences transfer width, sync, disconnect, tagging, termination, BIOS, and reset behavior.

## Dependencies and Integration Points

The header depends on generated `aic7xxx_reg.h` and OS-supplied platform typedefs for bus space, DMA, platform data, and I/O context. It integrates with AHC core C files, PCI/EISA front ends, Linux/BSD OSM layers, and the 93Cx6 SEEPROM helper. It is related to but distinct from AIC79xx/AHD headers; this subset includes it because the EEPROM helper is for the older AHC path.

## Risks

- Hardware SCB layout is byte-position sensitive; field reordering or packing changes would break DMA communication with firmware.
- Many feature and bug flags are silicon-specific; incorrect combinations can cause data corruption or failed recovery.
- Target/channel macros assume specific bit layouts from register definitions and twin-channel feature flags.
- `struct seeprom_config` bit definitions overlap between adapter generations/cards; consumers must apply the right interpretation.
- Public prototypes form a broad ABI within the driver; platform/core drift can compile but fail at runtime if state invariants change.

## Test Signals

- Compile the AHC driver variants using this header with target mode enabled and disabled.
- Exercise SCB allocation/queue/completion, residual calculation, S/G DMA, transfer negotiation, bus reset, and SEEPROM read/parse flows.
- Validate generated register headers match the structure and macro assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_93cx6.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_93cx6.c

## Purpose

`aic7xxx_93cx6.c` implements bit-banged access to 93C46/56/66-style serial EEPROM chips used by AIC7xxx adapters for BIOS and controller settings. It supports read, write, write-enable/disable sequencing, chip reset, and checksum verification for `struct seeprom_config`.

## Important APIs, Types, and Functions

- `struct seeprom_cmd` stores opcode length and bit sequence.
- Static command definitions cover short C46 and long C56/C66 write-enable/write-disable opcodes plus common read/write opcodes.
- `CLOCK_PULSE(sd, rdy)` waits for SEEPROM ready and clears the clock by reading the control port.
- `send_seeprom_cmd()` asserts chip select and clocks command bits through descriptor-provided `CS`, `CK`, and `DO` masks.
- `reset_seeprom()` drops chip select and clocks the device back to idle/reset state.
- `ahc_read_seeprom()` sends read opcode/address cycles and reads 16-bit words, including the leading zero bit specified by the chip protocol.
- `ahc_write_seeprom()` selects the correct EWEN/EWDS opcode width, writes each addressed 16-bit word, waits for write completion by polling data-in, and returns the chip to write-protect mode.
- `ahc_verify_cksum()` sums all config words except the checksum and compares the low 16 bits to `sc->checksum`, rejecting zero checksums.

## Control Flow and State

Reads iterate from `start_addr` through `start_addr + count - 1`. For each word the code sends the read opcode, clocks the 6- or 8-bit address MSB first based on `sd_chip`, reads 17 cycles to discard the initial zero and collect 16 bits, stores the word, and resets chip select. Writes first enable programming, then for each word send write opcode, address, data bits MSB first, poll until the chip reports completion, reset chip select, and finally disable programming.

All hardware state is external to the file and accessed through the `seeprom_descriptor` macros in the header. The functions assume the caller has already acquired exclusive SEEPROM access and configured the descriptor offsets/masks.

## State and Persistence Behavior

Reads are non-mutating except for control-line toggling. Writes persist new 16-bit words into serial EEPROM hardware. Checksum verification is pure over a `struct seeprom_config` memory image.

## Dependencies and Integration Points

The file includes `aic7xxx_osm.h`, `aic7xxx_inline.h`, and `aic7xxx_93cx6.h`. It depends on `ahc_inb()`, `ahc_outb()`, and `ahc_flush_device_writes()` via macros. Bus attach/config code uses these functions to load or update adapter NVRAM before applying target and termination settings.

## Risks

- The polling loops have no timeout. Broken hardware or an incorrect ready/data mask can hang the caller.
- Write support persists hardware settings; callers must validate length, checksum, and exclusive access before invoking it.
- Descriptor bit masks must match the specific adapter wiring; swapped DO/DI/CK/CS masks would corrupt reads or writes.
- Checksum logic treats checksum zero as invalid even if the arithmetic comparison would otherwise pass.

## Test Signals

- Read known-good EEPROM contents and verify expected signature/checksum.
- Write a test image only on disposable hardware or emulator, then reread and verify exact word match.
- Test both C46 6-bit and C56/C66 8-bit address modes.
- Fault-inject invalid ready/data masks to ensure higher layers avoid unbounded hangs where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_93cx6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_93cx6.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_93cx6.h

## Purpose

`aic7xxx_93cx6.h` declares the descriptor, chip-type enum, register access macros, and public functions for AIC7xxx 93Cx6 serial EEPROM access. It isolates board-specific control/status/data offsets and bit masks from the generic bit-banging implementation.

## Important APIs, Types, and Functions

- `enum seeprom_chip_t` uses `C46 = 6` and `C56_66 = 8`, representing the number of address bits.
- `struct seeprom_descriptor` carries the owning `ahc_softc`, control/status/dataout register offsets, chip type, and masks for memory-select, ready, chip-select, clock, data-out, and data-in lines.
- Macros `SEEPROM_INB()`, `SEEPROM_OUTB()`, `SEEPROM_STATUS_INB()`, and `SEEPROM_DATA_INB()` route descriptor-relative access through AHC register I/O and flush posted writes.
- Public functions are `ahc_read_seeprom()`, `ahc_write_seeprom()`, and `ahc_verify_cksum()`.

## Control Flow and State

The header has no standalone flow. It defines how implementation code toggles board lines and reads status. A caller fills `struct seeprom_descriptor` for a specific adapter, acquires the SEEPROM using bus/core code, then passes it to read/write helpers.

## State and Persistence Behavior

The descriptor is transient runtime state. `SEEPROM_OUTB()` mutates adapter control registers and flushes writes; `ahc_write_seeprom()` persists changes to serial EEPROM hardware. `ahc_verify_cksum()` validates in-memory persistent configuration images.

## Dependencies and Integration Points

The header depends on `struct ahc_softc`, `struct seeprom_config`, and AHC register access helpers from the OS/core headers. It is used by AIC7xxx bus attach/config code and `aic7xxx_93cx6.c`.

## Risks

- The enum values double as address-bit counts; changing them would break command/address shifting.
- Register offsets and masks are not validated by the helper, so incorrect descriptors can hang or corrupt EEPROM operations.
- The write macro relies on `ahc_flush_device_writes()` semantics for hardware ordering.

## Test Signals

- Compile with all AHC bus front ends that construct `seeprom_descriptor`.
- Confirm descriptor settings can read expected EEPROM contents and checksum on supported C46 and C56/C66 parts.
- Verify write-protect enable/disable sequencing with hardware documentation or a bus analyzer when changing macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_93cx6.h -->
