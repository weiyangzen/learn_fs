# sources/distributed-fs/ceph-client/drivers/ata/libata-core.c

## Purpose

`libata-core.c` is the central helper library for Linux ATA/SATA low-level drivers. It provides the generic `ata_port_operations` defaults, module parameters, device/link iteration helpers, ATA taskfile construction, IDENTIFY parsing, transfer-mode selection, internal command execution, queued-command issue/completion, reset/revalidation support, power management entry points, host/port allocation and registration, PCI/platform removal helpers, libata.force parsing, and module initialization/exit glue.

The file is not a standalone filesystem component; in this tree it is part of the Ceph client source mirror under `drivers/ata/`, but functionally it integrates the kernel block/SCSI stack with ATA/SATA host-controller drivers.

## Important APIs, Types, and Data

- `ata_base_port_ops` and `ata_dummy_port_ops` provide reusable `struct ata_port_operations` implementations. Base ops wire standard reset/EH callbacks; dummy ops fail command issue with `AC_ERR_SYSTEM`.
- Module parameters control global behavior: `atapi_enabled`, `atapi_dmadir`, `atapi_passthru16`, `libata_fua`, `ata_ignore_hpa`, `libata_dma_mask`, `ata_probe_timeout`, `libata_noacpi`, `libata_allow_tpm`, `atapi_an`, and optional `libata.force`.
- Iteration helpers `ata_link_next()` and `ata_dev_next()` implement the semantics behind `ata_for_each_link()` / `ata_for_each_dev()` across host links, PMP links, slave links, enabled-only devices, and reverse iteration.
- Taskfile helpers include `ata_build_rw_tf()`, `ata_tf_read_block()`, `ata_tf_to_lba()`, `ata_tf_to_lba48()`, `ata_dev_power_init_tf()`, and `ata_dev_set_feature()`.
- Transfer-mode helpers include `ata_pack_xfermask()`, `ata_unpack_xfermask()`, `ata_xfer_mask2mode()`, `ata_xfer_mode2mask()`, `ata_xfer_mode2shift()`, `ata_mode_string()`, `ata_id_xfermask()`, `ata_down_xfermask_limit()`, `ata_dev_xfermask()`, `ata_set_mode()`, and `ata_timing_cycle2mode()` under ACPI.
- Device discovery/configuration centers on `ata_dev_classify()`, `ata_dev_read_id()`, `ata_dev_configure()`, `ata_dev_reread_id()`, and `ata_dev_revalidate()`.
- Runtime command paths are `ata_exec_internal()`, `ata_qc_issue()`, `ata_qc_complete()`, `__ata_qc_complete()`, `ata_std_qc_defer()`, `ata_sg_init()`, DMA map/unmap helpers, and `ata_qc_get_active()`.
- Host lifecycle APIs include `ata_dev_init()`, `ata_link_init()`, `ata_port_alloc()`, `ata_port_free()`, `ata_host_alloc()`, `ata_host_alloc_pinfo()`, `ata_host_start()`, `ata_host_register()`, `ata_host_activate()`, `ata_host_detach()`, and `ata_dev_free_resources()`.
- Quirk data is stored in `__ata_dev_quirks[]`, `ata_quirk_names[]`, and `__ata_dev_max_sec_quirks[]`; matching uses IDENTIFY model/revision strings and `glob_match()`.

## Control Flow

Typical host-controller setup starts with a low-level driver calling `ata_host_alloc()` or `ata_host_alloc_pinfo()`. Ports are allocated with `ata_port_alloc()`, initialized with `ata_link_init()` / `ata_dev_init()`, then started by `ata_host_start()`. Starting finalizes inherited port ops, invokes per-port `port_start()`, freezes ports for EH, and registers a devres stop action when needed. `ata_host_register()` creates ATA transport objects, registers SCSI hosts, initializes SATA speed limits, logs port capabilities, and schedules asynchronous `async_port_probe()` work. `ata_host_activate()` wraps start, IRQ request, and registration.

Probe/reset flows are driven through error handling. `ata_port_probe()` powers on the port, marks all devices for probing, schedules reset, and waits through EH in `async_port_probe()`. `ata_std_prereset()` resumes SATA links unless a hard reset is already planned and suppresses soft reset on offline links. `ata_std_postreset()` clears SError and logs link status.

Device identification starts with class signatures from `ata_dev_classify()`, then `ata_dev_read_id()` issues ATA or ATAPI IDENTIFY through `ap->ops->read_id()` or `ata_do_dev_read_id()`. It retries with the alternate class on aborted IDENTIFY, handles SEMB-identified disks, byte-swaps IDENTIFY words, spins up standby devices when needed, and runs pre-ATA4 init-device-params if required. `ata_dev_configure()` then clears cached log directory state, applies quirk tables and forced quirks, handles ATAPI disable policy, applies link-speed quirks, invokes ACPI device config, optionally unlocks HPA, computes sector counts and multiple mode, configures LBA/CHS, NCQ, LPM, FUA, DevSlp, sense reporting, ZAC, Trusted Computing, CPR, CDL, and ATAPI-specific flags.

I/O taskfiles are built by `ata_build_rw_tf()`. NCQ commands use `ATA_CMD_FPDMA_READ/WRITE`, LBA48 fields, hardware tags, optional priority, FUA, and CDL. Non-NCQ LBA commands choose LBA28 or LBA48 based on block/count, FUA, and CDL; CHS devices convert LBA to cylinder/head/sector. `ata_set_rwcmd_protocol()` selects PIO, DMA, multi-sector, LBA48, and FUA opcodes.

Queued commands enter via `ata_qc_issue()`. It validates tags and exclusivity, marks NCQ/non-NCQ active state, checks adapter online state, DMA maps SG lists when needed, schedules EH if a sleeping device is accessed, calls optional `qc_prep()`, then calls low-level `qc_issue()`. Completion enters `ata_qc_complete()`, which routes internal commands directly after filling result taskfiles, sends failed commands to EH, handles successful CDL sense-data collection, schedules revalidation after selected SET FEATURES / INIT PARAMS / SET MULTI commands, updates sleeping state, verifies dubious transfers, and finishes with `__ata_qc_complete()` to clear DMA mappings and active tags.

`ata_exec_internal()` is a synchronous internal-command path used heavily by IDENTIFY, SET FEATURES, log reads, HPA, power mode, and mode-setting code. It temporarily preempts normal link/port active state, issues an internal queued command, releases EH ownership while waiting, freezes the port on timeout, runs optional `post_internal_cmd()`, performs minimal error analysis, restores preempted state, and records automatic timeout feedback.

## State and Persistence Behavior

Most state is volatile kernel memory in `struct ata_host`, `struct ata_port`, `struct ata_link`, `struct ata_device`, and `struct ata_queued_cmd`. Persistent hardware/device effects can occur through ATA commands:

- HPA handling can call `SET_MAX`/`SET_MAX_EXT` through `ata_set_max_sectors()` when `ignore_hpa` or `ATA_DFLAG_UNLOCK_HPA` allows unlocking.
- `ata_dev_set_feature()` and `ata_dev_set_xfermode()` modify device feature state such as spin-up, NCQ AA, sense reporting, CDL, DIPM disable, ATAPI AN, or transfer mode.
- `ata_dev_power_set_standby()` sends STANDBY IMMEDIATE, and `ata_dev_power_set_active()` sends VERIFY to spin up a device.
- `sata_link_init_spd()` reads saved SControl and applies forced speed limits into `hw_sata_spd_limit` / `sata_spd_limit`.

Cached runtime state includes IDENTIFY data (`dev->id`), general-purpose log directory cache (`dev->gp_log_dir`), sector scratch buffers, `dev->quirks`, feature flags, `n_sectors`, `n_native_sectors`, transfer masks/modes, CDL resources, CPR log descriptors, link active tags, NCQ `sactive`, port `qc_active`, EH flags/actions, PM message state, and async probe cookies. The file uses devres and kref lifetime management for host/port ownership, while per-device resources such as ZPODD/CDL/CPR allocations are cleaned explicitly.

## Dependencies and Integration Points

- Kernel infrastructure: module parameters, IDA allocation, kref, devres, async work, workqueues, timers, completions, spinlocks, mutexes, wait queues, DMA mapping, PCI/platform APIs, PM runtime/system sleep, sysfs device types, ratelimit, tracepoints, LEDs, and endian/unaligned helpers.
- SCSI/block integration: `scsi_host_template`, `Scsi_Host`, `scsi_remove_device()`, `scsi_remove_host()`, `ata_scsi_add_hosts()`, `ata_scsi_scan_host()`, deferred qc work, and SCSI command flags for CDL successful-sense EH.
- libata internal modules: EH helpers (`ata_port_schedule_eh()`, `ata_qc_schedule_eh()`, `ata_eh_freeze_port()`, ownership acquire/release), SFF helpers (`ata_sff_init()`, `ata_sff_flush_pio_task()`), ACPI helpers, transport helpers (`ata_tport_add/delete`, `ata_tlink_delete`), SATA SCR access, PMP support, ZPODD, and trace events from `trace/events/libata.h`.
- Low-level driver callbacks are central: `read_id`, `dev_config`, `mode_filter`, `set_piomode`, `set_dmamode`, `qc_prep`, `qc_issue`, `qc_fill_rtf`, `check_atapi_dma`, `freeze`, `port_start`, `port_stop`, `host_stop`, and `post_internal_cmd`.

## Risks and Edge Cases

- Command-state corruption is high impact. `ata_exec_internal()` intentionally overrides and restores `active_tag`, `sactive`, `qc_active`, and active-link counts; mistakes here can cause double completion, lost commands, or broken EH recovery.
- IDENTIFY parsing is defensive because many devices report wrong class, bad signatures, incomplete data, standby-only data, bogus HPA, broken logs, or firmware-specific quirks. Changes can regress old hardware.
- Quirk matching order matters because `ata_dev_quirks()` returns the first matching entry. Broad glob entries can shadow later specific entries.
- Transfer-mode decisions combine host masks, device masks, IDENTIFY masks, quirk masks, global DMA policy, cable detection, simplex DMA ownership, IORDY, ACPI timing, and low-level `mode_filter()`. A small mask bug can silently force PIO or select unsafe UDMA.
- HPA unlock and revalidation alter visible capacity. The code preserves original sector counts when revalidation fails and has special handling for late HPA lock/unlock, but this remains data-loss-sensitive behavior.
- PM paths rely on EH as the executor. Runtime suspend is deliberately blocked for non-ZPODD ATAPI optical devices because polling media changes would repeatedly reset them.
- DMA and SG setup must maintain `orig_n_elem`, `n_elem`, and `ATA_QCFLAG_DMAMAP`; cleanup assumes mapped SG state is coherent.
- CDL successful completion with ATA sense data deliberately routes an otherwise-good command through EH and sets SCSI flags to preserve success semantics. This path is easy to break with generic completion refactors.
- `libata.force` parsing supports abbreviations plus exact `name=value` forms; ambiguous abbreviations are rejected. Incorrect parsing could force unsafe link speeds, quirks, transfer modes, or device disablement.

## Test Signals

Useful validation signals include:

- Kernel/libata build coverage with configurations toggling `CONFIG_ATA_FORCE`, `CONFIG_HAS_DMA`, `CONFIG_PM`, `CONFIG_PCI`, `CONFIG_ATA_ACPI`, and SATA host support.
- Boot/probe logs for SATA/PATA devices showing expected port registration, link status, IDENTIFY model/revision, transfer mode, NCQ depth, and feature list.
- Error-injection or emulator tests for IDENTIFY abort fallback, SEMB mis-signature, standby spin-up, HPA read/set failures, missing/bad log directories, and device disappearance during revalidation.
- I/O tests covering NCQ and non-NCQ reads/writes, FUA, CDL, command priority, ATAPI DMA filtering, PIO fallback, and command timeout recovery.
- Hotplug, suspend/resume, runtime PM, PCI remove/shutdown, platform remove, and SAS suspend/resume paths, with checks that EH completes and SCSI devices are removed/rescanned in order.
- Quirk regression checks using representative IDENTIFY model/revision strings, especially broad glob entries for Samsung, Crucial/Micron, Intel, WD, Pioneer, and max-sector-specific devices.
- DMA mapping tests or fault injection around `ata_sg_setup()` / `ata_sg_clean()` to confirm error paths do not leak mappings or leave qcs active.
- Tracepoints (`ata_qc_issue`, `ata_qc_complete_*`, taskfile load/exec, BMDMA events) and dmesg warnings are practical observability for command lifecycle and EH behavior.
