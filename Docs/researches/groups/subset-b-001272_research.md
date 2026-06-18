# Research Report: subset-b-001272

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_module.c -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_module.c

## Purpose
This is the EDAC core module entry point. It creates the common EDAC sysfs bus at `/sys/devices/system/edac`, initializes EDAC memory-controller sysfs, debugfs, and the shared EDAC workqueue, and clears pre-existing PCI parity status during startup.

## Important APIs and Functions
`edac_set_debug_level()` validates the optional debug level module parameter when `CONFIG_EDAC_DEBUG` is enabled. `edac_debug_level` is exported for other EDAC code. `edac_op_state_to_string()` translates EDAC runtime states into stable strings for logs. `edac_get_sysfs_subsys()` exports the `edac` `bus_type` to sysfs helpers. `edac_init()` and `edac_exit()` are the module lifecycle gates.

## Control Flow
Initialization prints the EDAC version, registers the EDAC system bus, clears PCI parity errors, initializes memory-controller sysfs, initializes debugfs, then creates the workqueue. Error unwind is ordered in reverse: debugfs and memory-controller sysfs are removed if workqueue setup fails, and the subsystem bus is unregistered if earlier setup fails. Exit tears down the workqueue, memory-controller sysfs, debugfs, and subsystem bus.

## State and Persistence
Persistent module state is the static `edac_subsys` bus and optional exported `edac_debug_level`. No on-disk persistence exists; state is kernel runtime state exposed through sysfs/debugfs and module parameters.

## Dependencies and Integration
The file depends on `linux/edac.h`, `edac_mc.h`, and `edac_module.h`. It integrates with EDAC memory-controller sysfs, EDAC PCI parity helpers, debugfs helpers, and the EDAC workqueue implementation elsewhere in the core.

## Risks
`edac_init()` clears only PCI devices present at module initialization; the source comment notes hotplugged devices are not initially cleared here. The init order means failures in later subsystems must keep unwind symmetry. Debug level validation rejects values above 4 but only exists under debug builds.

## Test Signals
Boot/module-load tests should observe `/sys/devices/system/edac`, EDAC version logging, successful creation/removal of memory-controller sysfs and debugfs, and no leaked workqueue after module unload. PCI parity boot-clearing behavior is visible through parity counters and PCI status registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_module.h -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_module.h

## Purpose
This internal EDAC core header declares cross-file interfaces used within the EDAC subsystem: memory-controller sysfs helpers, device sysfs helpers, core workqueue operations, debugfs wrappers, and PCI parity/sysfs helpers.

## Important APIs and Types
The memory-controller declarations include `edac_mc_sysfs_init()`, `edac_mc_sysfs_exit()`, `edac_create_sysfs_mci_device()`, `edac_remove_sysfs_mci_device()`, logging policy getters, panic policy getters, polling period getters, and DIMM location formatting. Device helpers expose EDAC device sysfs registration and removal. Workqueue helpers include `edac_workqueue_setup()`, `edac_workqueue_teardown()`, `edac_queue_work()`, `edac_stop_work()`, and `edac_mod_work()`.

## Control Flow
The header does not implement runtime flow, but it defines build-time flow through `CONFIG_EDAC_DEBUG` and `CONFIG_PCI`. With debug enabled, debugfs functions are real declarations; otherwise inline no-op stubs are compiled. With PCI enabled, PCI parity functions are declared; otherwise preprocessor no-ops allow non-PCI EDAC builds to compile.

## State and Persistence
No state is owned here. The declarations expose runtime state managed by other translation units: sysfs kobjects, EDAC workqueue delayed work, debugfs dentries, and PCI parity policy/counters.

## Dependencies and Integration
The header includes `acpi/ghes.h`, `edac_mc.h`, `edac_pci.h`, and `edac_device.h`, making it a central private contract among EDAC core files and EDAC PCI/GHES code. It also maps debugfs remove calls directly to kernel `debugfs_remove*` helpers.

## Risks
Because this is an internal umbrella header, adding declarations here expands coupling across EDAC components. The non-PCI macros intentionally erase calls, but several are function-like macros without return values; code using return values must match the macro shapes. Debugfs stubs return `NULL`, so callers must tolerate unavailable debugfs.

## Test Signals
Build coverage is the main signal: EDAC should compile with and without `CONFIG_PCI`, and with and without `CONFIG_EDAC_DEBUG`. Runtime tests should confirm debugfs-dependent drivers degrade cleanly when debugfs support is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_pci.c -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_pci.c

## Purpose
This file implements EDAC's PCI controller abstraction. It allocates `edac_pci_ctl_info` objects, tracks registered PCI EDAC controllers in a global ordered list, schedules polling checks, and provides a generic PCI parity polling controller.

## Important APIs and Functions
Exported APIs are `edac_pci_alloc_ctl_info()`, `edac_pci_free_ctl_info()`, `edac_pci_alloc_index()`, `edac_pci_add_device()`, `edac_pci_del_device()`, `edac_pci_create_generic_ctl()`, and `edac_pci_release_generic_ctl()`. Internal helpers include `find_edac_pci_by_dev()`, `add_edac_pci_to_global_list()`, `del_edac_pci_from_global_list()`, and `edac_pci_workq_function()`.

## Control Flow
A low-level driver allocates a controller, fills device/module/check fields, then calls `edac_pci_add_device()`. Add assigns an index, inserts the controller under `edac_pci_ctls_mutex`, creates sysfs, and either schedules delayed polling work or marks the controller interrupt-driven. The work function checks the current op state, calls `edac_check()` when global policy allows, and requeues itself using the sysfs-configured poll interval. Removal marks the controller offline, removes it from the RCU-protected list, stops polling work, and returns the object to the caller for final release.

## State and Persistence
Runtime state is the global `edac_pci_list`, `edac_pci_ctls_mutex`, atomic `pci_indexes`, per-controller counters, op state, delayed work, and private driver data. No state persists beyond kernel runtime.

## Dependencies and Integration
The file depends on `edac_pci.h`, `edac_module.h`, the EDAC workqueue, PCI parity sysfs helpers, and kernel list/RCU/mutex/workqueue APIs. The generic controller bridges old memory-controller drivers to EDAC PCI parity scanning.

## Risks
The list is protected by mutex for mutation and uses RCU deletion to tolerate asynchronous readers such as NMI paths. Allocation stores optional `pvt_info` separately; the visible free path delegates to sysfs/kobject release, so private-data lifetime should be reviewed when adding users. Add failure paths must keep list and sysfs creation balanced.

## Test Signals
Tests should register and remove both polling and interrupt-style controllers, verify `/sys/devices/system/edac/pci/pciN` creation/removal, confirm delayed work stops on removal, and validate duplicate device/index rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_pci.h -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_pci.h

## Purpose
This header defines the EDAC PCI controller data model and public API used by EDAC PCI core code and chipset drivers that want PCI parity/error reporting.

## Important APIs and Types
`struct edac_pci_counter` stores parity and non-parity atomic counters. `struct edac_pci_ctl_info` holds list linkage, numeric index, op state, delayed work, optional polling callback, owning device, module/controller/device names, private data, start time, sysfs name, counters, and kobject. Inline helpers `pci_write_bits8()`, `pci_write_bits16()`, and `pci_write_bits32()` read-modify-write PCI config registers with a mask. Exported constructor/destructor and registration APIs are declared at the bottom.

## Control Flow
The header defines how low-level users interact with the implementation: allocate control info, fill fields, optionally provide `edac_check`, add it to EDAC, later delete and release it. The `to_edac_pci_ctl_work()` macro maps delayed work back to the owning controller.

## State and Persistence
No state is created here, but the struct layout defines all persistent in-kernel controller state for EDAC PCI instances. Counters persist while the kobject-backed controller exists and are exposed through sysfs by `edac_pci_sysfs.c`.

## Dependencies and Integration
The header depends on kernel device, kobject, list, PCI, type, and workqueue headers plus `linux/edac.h`. It is compiled only partly under `CONFIG_PCI`; PCI-specific data structures and write helpers are excluded for non-PCI builds.

## Risks
The masked write helpers do not check return values from PCI config reads or writes, matching common low-level kernel style but hiding transient config access failures. Callers must initialize all naming and device fields before registration because sysfs and logs use them immediately.

## Test Signals
Build tests should cover PCI and non-PCI configurations. Runtime validation should verify masked PCI writes preserve unmasked bits and that controller fields appear correctly in sysfs/log output after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_pci_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_pci_sysfs.c

## Purpose
This file owns EDAC PCI sysfs exposure and generic PCI parity scanning. It creates `/sys/devices/system/edac/pci`, per-instance `pciN` kobjects, global policy attributes, per-controller counters, and helpers to clear/report PCI parity and non-parity errors.

## Important APIs and Functions
Policy getters include `edac_pci_get_check_errors()` and `edac_pci_get_poll_msec()`. Sysfs creation/removal APIs are `edac_pci_create_sysfs()` and `edac_pci_remove_sysfs()`. PCI scanning helpers include `get_pci_parity_status()`, `edac_pci_dev_parity_clear()`, `edac_pci_dev_parity_test()`, `edac_pci_do_parity_check()`, and `edac_pci_clear_parity_errors()`. Exported event handlers are `edac_pci_handle_pe()` and `edac_pci_handle_npe()`.

## Control Flow
Creating a controller sysfs instance first bumps/creates the top-level PCI kobject under the EDAC bus, then creates `pciN`, then links the controller kobject to the underlying device. Removal deletes the symlink, drops the instance kobject, and tears down the top-level kobject when the refcount reaches zero. Parity checks iterate all PCI devices, read and clear primary status, inspect bridge secondary status when applicable, increment global counters, and optionally panic if policy requests panic on new parity errors.

## State and Persistence
Static module state includes `check_pci_errors`, logging/panic policy booleans, `edac_pci_poll_msec`, global parity counters, `edac_pci_top_main_kobj`, and `edac_pci_sysfs_refcount`. Per-controller counters live in `struct edac_pci_ctl_info`.

## Dependencies and Integration
The file integrates with the EDAC bus from `edac_module.c`, PCI core iteration/config access, sysfs/kobject APIs, module reference counting, and `edac_pci.c` registration flow.

## Risks
Sysfs integer stores accept only buffers beginning with a digit and use `simple_strtoul`, so negative or malformed writes are silently ignored/partially accepted. PCI config access failures are mostly inferred from `0xffff`/`0xffffffff` sanity reads. Parity scans use `for_each_pci_dev()` and may sleep, so they deliberately do not disable interrupts across the whole scan.

## Test Signals
Signals include global sysfs attributes, `pciN/pe_count`, `pciN/npe_count`, device symlink creation, parity counter increments on injected/configured PCI errors, and panic behavior only when `edac_pci_panic_on_pe` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_pci_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/fsl_ddr_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/fsl_ddr_edac.c

## Purpose
This platform EDAC driver supports Freescale/NXP DDR memory controllers on Power-based and Layerscape/i.MX platforms. It maps controller registers, validates ECC enablement, describes chip-select rows, reports correctable and uncorrectable ECC events, and optionally exposes debug error-injection sysfs attributes.

## Important APIs and Functions
`ddr_reg_addr()`, `ddr_in32()`, and `ddr_out32()` abstract endianness and i.MX9 register layout differences. Debug attributes expose injection data/control registers. `calculate_ecc()`, `syndrome_from_bit()`, and `sbe_ecc_decode()` diagnose single-bit errors on 64-bit data. `fsl_mc_check()` is the polling/IRQ error processor. `fsl_mc_isr()` handles interrupt mode. `fsl_ddr_init_csrows()` populates EDAC DIMM metadata. `fsl_mc_err_probe()` and `fsl_mc_err_remove()` are the platform lifecycle hooks.

## Control Flow
Probe allocates a two-layer EDAC memory controller, reads device-tree match flags and endianness, maps the main register resource and optional i.MX9 injection resource, verifies ECC enablement, sets EDAC capabilities, initializes chip-select rows, clears/reenables error detection, registers with EDAC, and optionally enables IRQ mode. Checks read `ERR_DETECT`, ignore non-ECC bits after clearing, capture syndrome/address/data, locate the csrow by PFN, report CE/UE via `edac_mc_handle_error()`, then clear detected bits.

## State and Persistence
Per-device state is `struct fsl_mc_pdata`: mapped bases, IRQ, saved error-disable/SBE-threshold registers, endianness, and variant flag. Hardware register state is modified while the driver is active and restored on remove.

## Dependencies and Integration
The driver depends on device tree resources/properties, platform IRQs, MMIO accessors, EDAC core memory-controller APIs, and `fsl_ddr_edac.h` register definitions.

## Risks
Register layout differs for i.MX9, so offsets must remain synchronized with hardware manuals. `orig_ddr_err_sbe` is saved only in interrupt mode but restored unconditionally, which should be reviewed for poll-mode behavior. Single-bit decode explicitly lacks 32-bit bus support.

## Test Signals
Useful signals are successful probe only when ECC is enabled, accurate DIMM pages/types in EDAC sysfs, CE/UE reports from hardware or debug injection, IRQ handling in interrupt mode, and restoration of error mask/threshold registers on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/fsl_ddr_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/fsl_ddr_edac.h -->
# sources/distributed-fs/ceph-client/drivers/edac/fsl_ddr_edac.h

## Purpose
This header provides Freescale DDR EDAC register offsets, bit definitions, private per-controller state, and probe/remove declarations shared by the platform glue and the main FSL DDR EDAC implementation.

## Important APIs and Types
`fsl_mc_printk()` wraps EDAC chipset logging. Register constants cover SDRAM configuration, chip-select bounds, error injection, capture registers, error detect/disable/interrupt enable, captured address, SBE threshold, and i.MX9-specific error-enable/injection offsets. Bit definitions describe memory/ECC enablement, bus width, registered-DIMM mode, memory type, interrupt-enable bits, error-detect bits, and error-disable bits. `struct fsl_mc_pdata` stores MMIO bases, IRQ, saved registers, endianness, and variant flag.

## Control Flow
The header has no runtime flow; `fsl_ddr_edac.c` consumes the constants to decide whether ECC is enabled, which MMIO base to use, how to decode chip-select ranges, and what to restore on removal.

## State and Persistence
The only state definition is `struct fsl_mc_pdata`, which persists for the lifetime of the EDAC memory-controller allocation. It mirrors controller configuration and mutable hardware settings that must be restored later.

## Dependencies and Integration
The header expects platform-device context for `fsl_mc_err_probe()` and `fsl_mc_err_remove()`, and it is tightly coupled to the EDAC memory-controller private data in the C file. It encodes both legacy FSL and i.MX9 register maps.

## Risks
Offsets and masks are hardware contracts. Incorrect values can cause MMIO writes to the wrong control register, especially because i.MX9 remaps injection/error-enable ranges. The `TYPE_IMX9` flag is a simple numeric match-data bit, so future variants need clear flag allocation.

## Test Signals
Compile-time users should include this header without conflicting register names. Runtime validation comes from correct ECC enable detection, proper endianness behavior, correct error capture decoding, and successful i.MX9 versus non-i.MX9 register addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/fsl_ddr_edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/ghes_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/ghes_edac.c

## Purpose
This driver bridges ACPI APEI/GHES firmware memory-error reports into the EDAC memory-controller reporting path. It builds a logical EDAC memory controller from SMBIOS/DMI DIMM data and reports CPER memory error sections through EDAC raw error handling.

## Important APIs and Functions
`assign_dmi_dimm_info()` converts SMBIOS Type 17 fields into EDAC DIMM size/type/mode/label data. `ghes_scan_system()` walks DMI once. `ghes_edac_report_mem_error()` is the notifier callback that translates CPER severity, address, grain, error type, location, and module handle into `edac_raw_error_desc`. `ghes_edac_register()` and `ghes_edac_unregister()` manage a singleton EDAC controller with reference counting across GHES devices.

## Control Flow
Module init obtains the GHES device list and registers each device. The first registration scans DMI, allocates a single all-memory EDAC controller, fills DIMM metadata or a fake fallback DIMM, adds it to EDAC, publishes `ghes_pvt` under a spinlock, and registers the GHES report notifier. Subsequent registrations only increment `ghes_refcount`. Error reports take `ghes_lock`, copy the singleton private pointer, clear shared buffers, fill the raw EDAC descriptor from CPER fields, and call `edac_raw_mc_handle_error()`. Unregister decrements the refcount, nulls `ghes_pvt`, removes the EDAC controller, and unregisters the notifier.

## State and Persistence
State includes `ghes_refcount`, `ghes_pvt`, `ghes_hw` DMI DIMM cache, `system_scanned`, `ghes_devs`, a registration mutex, and a spinlock protecting report-time buffers. State is runtime only and rebuilt on module load.

## Dependencies and Integration
The driver depends on ACPI GHES APIs, DMI helpers, CPER/RAS helpers, notifier chains, EDAC core allocation/reporting, and `edac_module.h`.

## Risks
Firmware data quality is central; missing SMBIOS DIMMs triggers a fake DIMM and explicit caution logs. Report buffers are shared through the singleton private object and require `ghes_lock`. The callback warns if called from NMI because it assumes GHES deferred processing.

## Test Signals
Signals include EDAC controller registration on systems with GHES devices, DMI-derived DIMM labels and SMBIOS handles, CPER corrected/recoverable/panic severity mapping, correct PFN/offset/grain fields, and clean behavior when DMI has no DIMMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/ghes_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/highbank_l2_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/highbank_l2_edac.c

## Purpose
This platform EDAC device driver reports Calxeda Highbank L2 cache ECC events. It registers an EDAC device controller, maps status/clear registers, and handles separate single-bit and double-bit ECC IRQs.

## Important APIs and Functions
`struct hb_l2_drvdata` stores the mapped register base and IRQ numbers. `highbank_l2_err_handler()` clears the relevant interrupt and calls `edac_device_handle_ce()` for single-bit ECC or `edac_device_handle_ue()` for double-bit ECC. `highbank_l2_err_probe()` and `highbank_l2_err_remove()` implement platform lifecycle. The OF match table binds `calxeda,hb-sregs-l2-ecc`.

## Control Flow
Probe allocates an EDAC device with one instance/block and two counters, opens a devres group, maps the memory resource, fills names from the OF match, registers the EDAC device, then requests double-bit and single-bit IRQs. The IRQ handler compares the IRQ number with stored single/double IRQs, writes to the corresponding clear register, and reports the event. Remove unregisters and frees the EDAC device.

## State and Persistence
Per-device runtime state is limited to mapped MMIO base and IRQ numbers in the EDAC device private area. Hardware interrupt status is cleared by writes during interrupt handling. No persistent state exists.

## Dependencies and Integration
The file depends on platform devices, Open Firmware matching, managed MMIO/IRQ resources, and EDAC device APIs. It integrates with EDAC's device-class reporting rather than memory-controller reporting because the target is L2 cache.

## Risks
The driver assumes IRQ 0 is double-bit and IRQ 1 is single-bit. If `devres_open_group()` fails after EDAC allocation, the visible path returns without freeing the allocation, so that path should be checked. The handler always returns `IRQ_HANDLED`, even if an unexpected IRQ number is passed.

## Test Signals
Probe should create an EDAC device for matching DT nodes. Injected or hardware L2 ECC IRQs should increment CE/UE counters, write the clear registers, and remove cleanly without dangling sysfs entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/highbank_l2_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/highbank_mc_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/highbank_mc_edac.c

## Purpose
This platform EDAC memory-controller driver reports Calxeda Highbank and Midway DDR ECC events. It maps controller ECC/error interrupt registers, registers one logical DIMM, handles CE/UE IRQs, and exposes a sysfs injection control.

## Important APIs and Functions
`struct hb_mc_drvdata` stores error and interrupt register bases. `highbank_mc_err_handler()` reads interrupt status, decodes UE/CE address and syndrome, reports through `edac_mc_handle_error()`, and acknowledges interrupts. `highbank_mc_err_inject()` and `highbank_mc_inject_ctrl()` configure ECC syndrome injection. `hb_mc_settings` selects register offsets for Highbank versus ECX-2000/Midway variants. `highbank_mc_probe()` and `highbank_mc_remove()` manage platform lifecycle.

## Control Flow
Probe matches the DT compatible string, allocates a chip-select/channel EDAC controller, maps the MMIO resource, computes error and interrupt sub-bases from match data, verifies ECC mode, fills EDAC capabilities and a single 4GB DDR3 DIMM, registers sysfs groups, then requests the IRQ. IRQ handling reports uncorrectable errors first, then correctable errors, then writes the observed status to the ACK register.

## State and Persistence
Runtime state is the mapped register sub-bases and EDAC DIMM/controller metadata. Injection writes change controller ECC option bits. No state is persisted outside hardware registers and EDAC sysfs counters.

## Dependencies and Integration
The driver depends on Open Firmware matching, platform resources/IRQs, EDAC memory-controller APIs, and sysfs attribute groups. It integrates corrected/uncorrected DDR events into standard EDAC counters.

## Risks
The model hard-codes a single 4GB DIMM, which may not describe all physical configurations precisely. The IRQ handler does not explicitly test for zero status before returning handled. Injection is writable by root and directly alters ECC option bits, so test environments must isolate it.

## Test Signals
Expected signals are successful probe only when ECC mode is active, EDAC DIMM metadata for DDR3 SECDED, CE/UE reports with PFN/offset/syndrome from registers, ACK writes matching interrupt status, and working `inject_ctrl` sysfs writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/highbank_mc_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i10nm_base.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i10nm_base.c

## Purpose
This is the Intel 10nm server memory-controller EDAC driver for Ice Lake/Tremont, Sapphire/Emerald Rapids, Granite Rapids, and related server CPUs. It discovers socket/IMC PCI resources, maps DDR/HBM memory-controller MMIO windows, registers EDAC memory controllers through `skx_common`, optionally decodes errors from MCA banks, and manages retry-read error log reporting.

## Important APIs and Functions
Resource configuration is encoded in `struct res_config` instances `i10nm_cfg0`, `i10nm_cfg1`, `spr_cfg`, and `gnr_cfg`. Retry-read logging is controlled by `reg_rrl` tables and helpers `enable_rrl()`, `enable_rrls_ddr()`, `enable_rrls_hbm()`, `enable_retry_rd_err_log()`, and `show_retry_rd_err_log()`. Discovery helpers include `pci_get_dev_wrapper()`, `i10nm_get_imc_num()`, `i10nm_check_2lm()`, `get_ddr_munit()`, `i10nm_get_ddr_munits()`, and `i10nm_get_hbm_munits()`. Error decoding uses `i10nm_mc_decode_available()` and `i10nm_mc_decode()`. `i10nm_get_dimm_config()` fills EDAC DIMM metadata.

## Control Flow
Module init rejects GHES-owned systems, conflicting EDAC owners, hypervisors, and unsupported CPUs. It selects a CPU resource config, obtains memory bounds, builds socket bus mappings, adjusts Granite Rapids IMC count when needed, detects 2-level memory, maps DDR and optional HBM munits, registers each present IMC with EDAC, obtains ADXL support, registers the MCE decode chain, sets debug hooks, and configures optional retry-read log handling. Exit reverses retry-read control, debug, MCE notifier, ADXL, and `skx_remove()`.

## State and Persistence
Static state includes `i10nm_edac_list`, selected `res_cfg`, module parameters `retry_rd_err_log` and `decoding_via_mca`, and `mem_cfg_2lm`. Per-socket/per-IMC state lives in `skx_dev` and `skx_imc` structures from `skx_common`, including PCI references, MMIO mappings, channel sizes, and saved retry-log controls.

## Dependencies and Integration
The driver is tightly integrated with `skx_common.h`, x86 CPU matching, PCI config space, MCE notifier chains, Intel-family IDs, ADXL decoding, EDAC core registration, and optional debug hooks.

## Risks
Hardware topology discovery is complex and generation-specific. Granite Rapids mutates the selected resource config based on runtime channel count and rebuilds bus mappings. MCA decoding is disabled for 2LM and DDRT cases. Retry-read log mode `2` actively changes hardware control bits and must restore them on exit. Many PCI/MMIO reads assume valid mapped resources after discovery.

## Test Signals
Signals include probe rejection under GHES/hypervisor/conflicting owner, correct IMC/channel/DIMM enumeration for each CPU family, CE/UE decoding from MCEs, retry-read log output/clearing in configured modes, HBM detection on SPR, and clean unmap/reference release through `skx_remove()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i10nm_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i3000_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i3000_edac.c

## Purpose
This PCI EDAC driver supports Intel 3000/3010 memory hub controllers. It maps MCHBAR rank-boundary registers, determines channel interleaving, registers DDR2 DIMM/rank topology with EDAC, polls ECC status, and reports CE/UE events.

## Important APIs and Functions
`deap_pfn()`, `deap_offset()`, and `deap_channel()` decode the hardware DRAM Error Address Pointer registers. `i3000_get_error_info()` reads status, address, and syndrome registers with a second status read to detect CE/UE overwrite races. `i3000_process_error_info()` reports EDAC errors. `i3000_is_interleaved()` compares channel rank attributes/boundaries. `i3000_probe1()`, `i3000_init_one()`, and `i3000_remove_one()` manage device lifecycle.

## Control Flow
Init calls `opstate_init()` and registers a PCI driver, with fallback manual `pci_get_device()` probing when normal registration did not bind. Probe enables the PCI device, maps MCHBAR, reads channel DRA/DRB registers, determines one- versus two-channel EDAC layout, allocates an EDAC memory controller, fills csrow/channel DIMMs from cumulative rank boundaries, clears stale errors, registers EDAC, and creates a generic PCI parity controller. Polling reads error registers, clears status by writing ones, and reports UE or CE with PFN/offset/syndrome/channel.

## State and Persistence
Static state includes `mci_pdev`, `i3000_registered`, and optional `i3000_pci`. Per-controller EDAC state has no private allocation. Hardware state includes error-status bits and rank-boundary configuration.

## Dependencies and Integration
The driver depends on PCI config access, MMIO `ioremap`, EDAC memory-controller APIs, EDAC PCI generic parity support, and Intel PCI IDs.

## Risks
The source notes non-atomic register capture: CE can be overwritten by UE between reads, handled by emitting a synthetic "UE overwrote CE" report. The fallback registration path and static globals assume a narrow device model. `mci_pdev` reference handling must remain balanced across driver-registered and manually probed modes.

## Test Signals
Signals include correct DDR2 csrow/channel sizing from DRB values, interleaved versus asymmetric channel detection, CE/UE reports with decoded DEAP address fields, status clearing, generic PCI parity sysfs creation, and clean unload in both normal and fallback probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i3000_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i3200_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i3200_edac.c

## Purpose
This PCI EDAC driver supports Intel 3200/3210 memory hub controllers. It maps a 64-bit MCHBAR, discovers channel count and rank boundaries, registers DDR2 DIMM topology, polls ECC error logs, and reports CE/UE events.

## Important APIs and Functions
`how_many_channels()` reads CAPID0 to detect single/dual channel mode. `eccerrlog_syndrome()` and `eccerrlog_row()` decode ECC error log fields. `i3200_get_and_clear_error_info()` captures status and channel ECC logs while guarding against CE/UE overwrite races. `i3200_map_mchbar()`, `i3200_get_drbs()`, `i3200_is_stacked()`, and `drb_to_nr_pages()` implement topology discovery. `i3200_probe1()` and remove/init functions handle lifecycle.

## Control Flow
Module init initializes op state and registers the PCI driver, with a manual fallback probe if needed. Probe enables PCI, maps MCHBAR, reads DRBs, determines channel count, allocates EDAC layers of DIMM and channel, records the MCHBAR window in private state, detects stacked memory layout, fills DIMM sizes, clears stale errors, and registers EDAC. Polling captures ERRSTS and channel ECC logs, clears ERRSTS, reports an overwrite UE if status changed, then emits CE/UE reports for each channel log.

## State and Persistence
Per-controller private state is `struct i3200_priv` with the mapped MCHBAR window. Static state includes global `nr_channels`, `mci_pdev`, and `i3200_registered`. Hardware error logs are cleared on each poll.

## Dependencies and Integration
The driver uses PCI config space, `readq()` for ECC logs, `ioremap`/`iounmap`, EDAC memory-controller APIs, and Intel PCI IDs. It does not create a generic EDAC PCI parity controller unlike i3000/i5000/i5400.

## Risks
`nr_channels` is global, so the code assumes only one active controller instance. Error log capture is non-atomic and uses the same overwrite mitigation pattern as i3000. Stacked-memory page calculation is register-layout sensitive.

## Test Signals
Validation should check MCHBAR mapping including high address rejection, CAPID channel mode, DIMM page counts from DRBs, CE/UE reports from ECCERRLOG bits, status clearing, and unload unmapping plus `pci_disable_device()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i3200_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i5000_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i5000_edac.c

## Purpose
This PCI EDAC driver supports Intel 5000P/V/X-class FB-DIMM memory controllers. It discovers the multi-function MCH and branch devices, decodes FB-DIMM topology, enables FBD error reporting, polls fatal/nonfatal error registers, and reports memory and optional miscellaneous errors through EDAC.

## Important APIs and Functions
`struct i5000_pvt` caches PCI devices, memory-map registers, MTR/AMB-present registers, and a DIMM size matrix. `i5000_get_error_info()` reads and clears first/next fatal and nonfatal FBD error registers plus recoverable/nonrecoverable address logs. `i5000_process_fatal_error_info()` and `i5000_process_nonfatal_error_info()` decode masks into EDAC fatal/UE/CE reports. Topology helpers include `i5000_get_devices()`, `i5000_get_mc_regs()`, `determine_mtr()`, `handle_channel()`, `calculate_dimm_size()`, and `i5000_init_csrows()`.

## Control Flow
Probe accepts only device 16 function 0, reads advertised channels and DIMMs per channel, allocates branch/channel/slot EDAC layers, obtains function 1/function 2 and branch 0/1 PCI devices, caches memory-technology registers, computes DIMM sizes, fills EDAC DIMM metadata, enables error reporting when memory exists, adds the controller, clears stale errors, and creates a generic PCI parity controller. Polling reads/clears hardware status, processes fatal first, then nonfatal CE/UE/misc categories.

## State and Persistence
Runtime state is the EDAC controller private `i5000_pvt`, global `i5000_pci`, and module parameter `misc_messages`. Hardware masks are changed to enable error reporting; fatal/nonfatal status registers are cleared by writing back observed bits.

## Dependencies and Integration
The driver depends on PCI config access, Intel FBD device IDs, EDAC memory-controller APIs, EDAC PCI generic parity support, and Linux memory-zone definitions for page counts.

## Risks
The register model spans several PCI functions and branch devices, so missing/broken BIOS enumeration prevents probe. Some comments note topology mapping is awkward and could be simplified. Miscellaneous nonfatal messages are suppressed unless `misc_messages` is set. Error-reporting masks are enabled without an explicit restore path.

## Test Signals
Signals include correct branch/channel/slot EDAC topology, DIMM sizes from MTR/AMB-present bits, FBD mask changes, CE/UE/fatal reports with decoded bank/rank/RAS/CAS, optional misc reports, generic PCI parity controller creation, and balanced `pci_dev_put()` on removal/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i5000_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i5100_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i5100_edac.c

## Purpose
This PCI EDAC driver supports Intel 5100 memory controllers. It models two independent channels as EDAC channel/slot layers, decodes memory technology and interleave registers, reports nonfatal memory errors, maintains periodic hardware scrubbing, and provides debugfs error injection.

## Important APIs and Functions
Many inline accessors decode MC/SPD/MIR/DMIR/MTR/VALIDLOG/REC/NREC fields. `struct i5100_priv` stores DIMM rank maps, interleave maps, MTR data, PCI devices, scrubbing work, injection settings, and debugfs directory. Error flow is handled by `i5100_check_error()`, `i5100_read_log()`, `i5100_handle_ce()`, and `i5100_handle_ue()`. Scrubbing is managed by `i5100_refresh_scrubbing()`, `i5100_set_scrub_rate()`, and `i5100_get_scrub_rate()`. Injection uses `i5100_do_inject()` and debugfs file operations.

## Control Flow
Probe binds device 16 function 1, enables ECC error detection, unmasks nonfatal memory errors, obtains channel memory-map devices and the injection device, allocates EDAC layers, starts scrub maintenance if BIOS already enabled it, reads SPD-derived DIMM rank layout, reads interleave/MTR state, initializes DIMMs, normalizes op state, registers EDAC, and sets up debugfs. Polling reads first/next nonfatal memory registers, selects the channel, reads valid logs from the channel device, reports CE/UE records, then clears logs and status.

## State and Persistence
Per-controller state includes PCI references, scrubbing delayed work, DIMM/interleave topology, injection masks, and debugfs dentries. Scrubbing state is maintained periodically while enabled. Hardware error masks and injection registers are modified at runtime.

## Dependencies and Integration
The driver uses PCI config access, EDAC memory-controller APIs, EDAC core work/debugfs helpers, delayed work, SPD-over-chipset commands, and Intel 5100 PCI IDs.

## Risks
The file explicitly notes that EDAC cannot fully represent the two independent channels, so csrows are laid out channel-by-channel. SPD access is polling-based and waits until not busy without a bounded loop after command issue. Debug injection directly writes hardware injection control. Scrubbing cancellation must use sync cancellation on removal/failure.

## Test Signals
Signals include ECC-disabled probe rejection, DIMM labels and sizes from SPD/MTR data, CE/UE reports from channel valid logs, scrub rate get/set behavior and delayed work requeueing, debugfs injection files, and balanced PCI disable/put paths on all failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i5100_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i5400_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i5400_edac.c

## Purpose
This PCI EDAC driver supports Intel 5400 "Seaburg" FB-DIMM memory controllers. It is derived from i5000 but adapts register layouts, error masks, topology, and EDAC reporting for the i5400 two-branch/two-channel lockstep architecture.

## Important APIs and Functions
`enum error_mask` and `error_name[]` define i5400 fatal/nonfatal error classes. `to_nf_mask()` and `from_nf_ferr()` translate between EMASK and FERR nonfatal bit layouts. `struct i5400_pvt` stores PCI devices, map registers, MTR/AMB-present state, and DIMM sizes. `i5400_get_error_info()` reads and clears fatal/nonfatal registers. `i5400_proccess_non_recoverable_info()` handles fatal, unrecoverable, and recoverable nonfatal events; `i5400_process_nonfatal_error_info()` handles CE and misc categories. Topology uses `i5400_get_devices()`, `i5400_get_mc_regs()`, `calculate_dimm_size()`, and `i5400_init_dimms()`.

## Control Flow
Probe accepts device 16 function 0, allocates branch/channel/slot EDAC layers, obtains the branchmap/error and FBD branch devices, reads topology registers, computes DIMM size matrix, fills EDAC DIMM metadata with FB-DDR2 and SDDC/Chipkill-like modes, enables error masks if memory exists, registers the controller, clears stale errors, and creates a generic PCI parity controller. Polling reads hardware error state, processes fatal first, then nonfatal CE/UE/recoverable/misc errors.

## State and Persistence
Runtime state is the EDAC private `i5400_pvt`, global `i5400_pci`, PCI device references, and modified FBD error mask registers. Error status is cleared by writing back observed bits. No on-disk persistence exists.

## Dependencies and Integration
The driver depends on Intel 5400 PCI IDs, PCI config access, EDAC memory-controller APIs, EDAC PCI generic parity support, and common kernel helpers such as `find_first_bit()` and string choice helpers.

## Risks
The function name `i5400_proccess_non_recoverable_info` has a spelling error but is internally consistent. Error-name lookup assumes a valid bit within `error_name[]`; unsupported/reserved bits may produce sparse-array nulls if masks change. Like i5000, error reporting is enabled without restoring original masks on remove. Multi-function PCI enumeration must match firmware exposure.

## Test Signals
Signals include correct branch/channel/slot DIMM topology, FB-DDR2 EDAC modes including single-DIMM SECDED downgrade, CE/UE/fatal/recoverable reports with decoded bank/rank/buffer/RAS/CAS, mask enablement, generic PCI parity controller creation, and balanced PCI references on remove/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i5400_edac.c -->
