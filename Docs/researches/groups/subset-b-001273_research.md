# subset-b-001273 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i7300_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i7300_edac.c Research

## Purpose
`i7300_edac.c` is the EDAC memory-controller driver for Intel 7300/Clarksboro chipsets with FB-DIMM memory. It discovers the multi-function MCH PCI topology, enumerates branches/channels/slots, decodes Memory Technology Registers into EDAC DIMM metadata, enables FB-DIMM error reporting, and polls global and FBD error registers to report fatal, uncorrectable, and correctable memory events.

## Important APIs, Types, and Functions
The main private state is `struct i7300_pvt`, which caches the required PCI functions, branch devices, controller settings, MIR/MTR/AMB-present registers, per-slot/channel size data, and a temporary print buffer. `i7300_get_devices()` finds device 16 functions 1 and 2 plus branch devices 21.0 and 22.0; `i7300_put_devices()` drops those references. `i7300_get_mc_regs()` reads AMBASE, TOLM, MC settings, MIR registers, and then calls `i7300_init_csrows()`.

`decode_mtr()` is the central DIMM decoder. It turns MTR bank/row/column/rank/width fields into DIMM size, memory type `MEM_FB_DDR2`, device width, and EDAC mode. Single mode uses SECDED; normal/mirrored lockstep uses S4ECD4ED or S8ECD8ED depending on x4/x8 DRAM. `i7300_process_error_global()` reports global MCH/FSB/PCIe/FBD fatal and non-fatal registers to the kernel log, while `i7300_process_fbd_error()` reads FERR_FAT_FBD/FERR_NF_FBD plus NRECMEM/RECMEM/REDMEM detail registers and reports through `edac_mc_handle_error()`. `i7300_enable_error_reporting()` unmasks FBD errors in `EMASK_FBD`.

## Control Flow
Module init calls `opstate_init()` and registers a PCI driver for the I7300 MCH error device. Probe accepts only function 0, allocates a three-layer EDAC topology of branch, channel, and slot, allocates a page-sized message buffer, gathers companion PCI devices, populates `mem_ctl_info`, decodes memory configuration, optionally enables reporting, registers with EDAC, clears stale errors, and creates generic PCI EDAC control.

During polling, `i7300_check_error()` checks global errors first and then FB-DIMM errors. Fatal FB-DIMM errors use non-recoverable memory address detail registers and are reported as `HW_EVENT_ERR_FATAL`; non-fatal FB-DIMM errors read syndrome/channel/detail registers and are currently reported as corrected errors. Remove releases generic PCI control, unregisters the EDAC MC, drops companion PCI device references, frees the temporary buffer, and frees the MC object.

## State and Persistence
There is no filesystem persistence. Runtime state lives in PCI config registers, `struct mem_ctl_info`, `struct i7300_pvt`, EDAC core registration, and the global `i7300_pci` pointer. Hardware error registers are read-clear/write-one-to-clear; driver-cached MTR/MIR/AMB settings are probe-time snapshots.

## Dependencies and Integration Points
The driver depends on Linux PCI APIs, EDAC MC APIs, generic EDAC PCI control, `edac_module.h`, and Intel PCI IDs for the I7300 MCH/FBD functions. It integrates with EDAC polling/NMI state through the global `edac_op_state` module parameter.

## Risks and Edge Cases
Companion PCI functions are mandatory; hidden or broken BIOS enumeration makes probe fail. Error detail reads are not atomic, so only first set bits are decoded and concurrent errors can be compressed into one report. The corrected-error location uses `branch >> 1`, which makes branch information coarse, and physical page/offset details are not reconstructed for FBD reports. DIMM presence relies on MTR fields rather than AMB-present fields because AMB register semantics are ambiguous.

## Test Signals
Useful signals include successful probe on I7300 hardware, EDAC sysfs DIMM layout matching physical FB-DIMMs, EMASK_FBD becoming unmasked, poll-time reports for FERR_GLOBAL and FERR_FBD injections, clean module unload with no leaked PCI references, and dmesg debug output for MIR/MTR/AMB decoding under `CONFIG_EDAC_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i7300_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i7core_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i7core_edac.c Research

## Purpose
`i7core_edac.c` supports Intel Nehalem, Lynnfield, Westmere, Xeon 35xx/55xx/56xx, i7/i5 memory controllers. It discovers per-socket non-core and memory-controller PCI functions, registers EDAC memory controllers, decodes DDR3 DIMM geometry, handles memory-controller MCE bank 8 notifications, maintains corrected-error counters, exposes error-injection sysfs controls, and optionally controls hardware patrol scrub rate.

## Important APIs, Types, and Functions
`struct i7core_dev` groups all PCI functions for one socket and links into `i7core_edac_list`. `struct i7core_pvt` binds those PCI functions to one EDAC controller and holds DIMM topology, injection settings, corrected-error counters, scrub state, DCLK frequency, and a generic PCI EDAC control object. PCI discovery is table-driven through `struct pci_id_descr`, `struct pci_id_table`, `i7core_get_all_devices()`, and `mci_bind_devs()`.

`get_dimm_config()` reads MC_CONTROL, MC_STATUS, MC_MAX_DOD, channel mapper, per-channel DIMM init, and DOD registers to populate EDAC DIMM geometry, type (`MEM_DDR3` or `MEM_RDDR3`), x4/x8/x16 device width, labels, grain, and EDAC mode. `i7core_mce_check_error()` filters MCEs to memory-controller bank 8 and socket-local controllers. `i7core_mce_output_error()` decodes operation, syndrome, DIMM, channel, corrected/uncorrected/fatal status and reports via `edac_mc_handle_error()`. `i7core_udimm_check_mc_ecc_err()` and `i7core_rdimm_check_mc_ecc_err()` read corrected-error counters and account wraparound.

The sysfs injection path uses `inject_section`, `inject_type`, `inject_eccmask`, `inject_enable`, and `inject_addrmatch/*` attributes. `i7core_inject_enable_store()` builds address-match and injection masks, unlocks PCI config writes, programs channel error injection registers, and toggles an undocumented non-core control value. Scrub support uses `set_sdram_scrub_rate()` and `get_sdram_scrub_rate()` when the platform exposes RAS function 2.

## Control Flow
Module init initializes EDAC opstate, optionally scans hidden Xeon buses, registers a PCI driver, and registers an MCE decode notifier. The first PCI probe claims all socket devices, allocates one EDAC controller per discovered socket, binds PCI functions, reads DIMM config, enables scrub hooks if available, registers EDAC with attribute groups, creates auxiliary sysfs devices, creates generic PCI EDAC control, and records DCLK from DMI.

Runtime MCE notification looks up the socket, rejects non-memory and non-bank-8 events, reports the MCE, updates CE counters, and marks the MCE handled. Removal unregisters all controllers, releases sysfs devices, releases generic PCI control, disables scrub programming, frees controller names and MC objects, and drops all PCI references.

## State and Persistence
State is entirely in kernel memory, PCI config registers, EDAC sysfs devices, MCE notifier registration, and optional hardware scrub/injection registers. Corrected-error totals persist only while the module is loaded. Injection settings are writable sysfs state and are disabled when parameters change.

## Dependencies and Integration Points
The driver depends on PCI enumeration, DMI walking, EDAC MC and PCI control, Linux MCE notifier APIs, `edac_module.h`, and Intel PCI IDs. It shares the global x86 MCE path with other EDAC decoders and coordinates with `MCE_HANDLED_CEC`/`MCE_HANDLED_EDAC`.

## Risks and Edge Cases
PCI discovery is fragile because hidden non-core buses may require `use_pci_fixup` scanning. Socket numbering derives from bus order. Error injection is privileged and can create real memory errors; mask construction is sensitive to DIMM count and channel selection. Corrected-error counters are 15-bit hardware counters with wraparound. MCE decoding intentionally ignores non-bank-8 or non-memory errors, and RDIMM corrected errors are counted through polling-style registers rather than direct MCE payloads.

## Test Signals
Test with supported Nehalem/Westmere systems should verify all socket PCI functions are claimed, DIMM sysfs geometry matches hardware, MCE bank 8 memory errors are reported once, CE counters increase under injected or scrubbed corrected errors, sysfs injection knobs program and disable registers, scrub rate set/get round-trips, and unload removes auxiliary sysfs devices without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i7core_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i82860_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i82860_edac.c Research

## Purpose
`i82860_edac.c` is a legacy PCI EDAC driver for Intel 82860 RDRAM memory controllers. It models the controller's Rambus groups as EDAC rows/slots, polls PCI error status registers, translates error address pointers to csrows, and reports correctable or uncorrectable ECC events.

## Important APIs, Types, and Functions
`struct i82860_error_info` captures the non-atomic error snapshot: `ERRSTS`, `EAP`, `DERRCTL_STS` syndrome, and a second `ERRSTS` read. `i82860_get_error_info()` reads those registers, clears CE/UE bits with write-one-to-clear, and rereads detail fields if a CE was overwritten by a UE between status reads. `i82860_process_error_info()` filters empty snapshots, maps `EAP` to a page, finds the EDAC csrow, and reports `HW_EVENT_ERR_UNCORRECTED` for UE or `HW_EVENT_ERR_CORRECTED` with syndrome for CE.

`i82860_init_csrows()` reads group boundary address registers (`GBA`) in 16 MiB granularity, derives cumulative page ranges, and populates the one-channel DIMM entries with RDRAM type, page counts, 4 KiB grain, and SECDED/no-EDAC mode based on MCHCFG data-integrity bits. `i82860_probe1()` allocates a virtual two-layer channel/slot EDAC topology and creates generic PCI EDAC control.

## Control Flow
Module init initializes opstate, registers the PCI driver, and includes a fallback manual `pci_get_device()`/`i82860_init_one()` path for cases where another driver may already own the host bridge. Probe enables the PCI device, allocates EDAC state, initializes rows, clears stale counters, registers the MC, and creates generic PCI control. Polling invokes `i82860_check()`, which snapshots and processes error registers. Removal releases generic PCI control, deletes the EDAC MC, and frees it.

## State and Persistence
State is held in EDAC MC structures, a global `mci_pdev` reference, and global generic PCI control pointer `i82860_pci`. Hardware error status is transient and cleared on every snapshot. No state persists outside kernel memory or PCI config space.

## Dependencies and Integration Points
The driver depends on Linux PCI config helpers, EDAC MC APIs, generic EDAC PCI control, `edac_module.h`, and Intel 82860 PCI IDs. Runtime scheduling depends on the EDAC core poll/NMI opstate selected by `edac_op_state`.

## Risks and Edge Cases
The row lookup result is used without checking for `-1`, so an unexpected `EAP` outside configured ranges can lead to invalid csrow access. Register reads are non-atomic and can still lose multi-error detail. The topology is approximate because RDRAM channels do not naturally map to EDAC csrow abstractions. The manual fallback path and global `mci_pdev` assume a single controller.

## Test Signals
Signals include successful probe on 82860 hardware, sysfs row sizes matching GBA boundaries, CE and UE reports from injected or hardware events, correct clearing of `ERRSTS`, no duplicate registration through the fallback path, and clean release of `mci_pdev` and generic PCI control on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i82860_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i82875p_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i82875p_edac.c Research

## Purpose
`i82875p_edac.c` supports Intel 82875P/E7210-style DDR memory hubs. It exposes the hidden overflow device needed for DRB/DRA/MMIO access, maps its BAR, derives single/dual-channel EDAC rows, polls host-bridge ECC status, and reports corrected or uncorrected DRAM errors.

## Important APIs, Types, and Functions
`struct i82875p_pvt` stores the overflow PCI device and mapped overflow MMIO window. `i82875p_setup_overfl_dev()` finds or unhides device 6 function 0, enables it, requests regions when possible, and maps BAR0. `i82875p_get_error_info()` snapshots `ERRSTS`, `EAP`, channel status (`DES`), syndrome, and a second `ERRSTS` read, handling the same CE-overwritten-by-UE race pattern as other legacy Intel drivers. `i82875p_process_error_info()` maps page address to csrow and reports UE or CE, including channel when dual-channel mode is active.

`dual_channel_active()` decodes DRC channel mode. `i82875p_init_csrows()` reads DRB registers from the overflow window, converts cumulative 64 MiB boundaries to page ranges, divides pages across active channels, and fills DIMM metadata with DDR type, SECDED/no-EDAC mode, 4 KiB grain, and unknown device width. `i82875p_probe1()` owns allocation, overflow setup, EDAC registration, stale error clearing, and generic PCI EDAC creation.

## Control Flow
Module init initializes opstate, registers the PCI driver, and uses a fallback host-bridge scan if the probe did not run. Probe enables the device, sets up the overflow MMIO path, reads DRC, allocates a chip-select/channel EDAC topology, initializes rows, clears stale counters, registers the MC, and creates generic PCI control. Polling calls `i82875p_check()`. Removal releases generic PCI control, unregisters the MC, unmaps the overflow window, disables/puts the overflow device, and frees EDAC state.

## State and Persistence
Persistent runtime state is limited to PCI device references, the overflow MMIO mapping, EDAC MC metadata, and the global `mci_pdev`/`i82875p_pci` pointers. Error status is cleared after reads. No disk state exists.

## Dependencies and Integration Points
The driver depends on PCI config and resource APIs, low-level `ioremap`/MMIO access, EDAC MC APIs, generic PCI EDAC, and Intel 82875 PCI IDs. It integrates with EDAC polling through `mci->edac_check`.

## Risks and Edge Cases
Device 6 can be hidden by BIOS and the driver writes a magic config bit to expose it. Region ownership is conditional under `CORRECT_BIOS`, so resource cleanup behavior differs by build. The error-address-to-row path does not validate row before reporting. Register snapshots are racy. The code assumes a single controller and uses fallback registration that can interact awkwardly with normal PCI probing.

## Test Signals
Test by loading on 82875P/E7210 hardware, confirming device 6 exposure and MMIO map, checking row sizes against DRB registers, validating dual-channel channel attribution from `DES`, injecting/observing CE and UE status bits, and unloading with the overflow BAR unmapped and PCI references released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i82875p_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i82975x_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/i82975x_edac.c Research

## Purpose
`i82975x_edac.c` is the EDAC driver for Intel 82975X DDR2 memory controllers. It maps the MCHBAR register space, verifies ECC is enabled, detects symmetric dual-channel configurations, initializes DIMM/csrow metadata from channel DRB registers, and polls PCI ECC status/address/syndrome registers.

## Important APIs, Types, and Functions
`struct i82975x_pvt` holds the mapped MCHBAR window. `struct i82975x_error_info` captures `ERRSTS`, `EAP`, `XEAP`, `DES`, syndrome, second `ERRSTS`, and derived channel data. `i82975x_get_error_info()` snapshots PCI status and detail registers and clears CE/UE bits. `i82975x_process_error_info()` constructs the page from cache-line-granular EAP plus XEAP bit 32, finds the EDAC row, derives channel from EAP bit 0 when dual-channel, calculates offset within the page using DIMM grain, and reports UE or CE.

`dual_channel_active()` compares channel 0 and 1 DRB values to treat only interleaved-symmetric layouts as dual-channel. `i82975x_init_csrows()` reads cumulative DRB boundaries from MCHBAR, scales them by 32 MiB and channel count, labels DIMMs `DIMM A/B`, and fills DDR2/SECDED/x8 metadata. `i82975x_probe1()` maps MCHBAR, checks per-channel DRC ECC state, allocates EDAC topology, initializes rows, marks hardware scrub support, clears stale errors, and registers the MC.

## Control Flow
Module init initializes opstate, registers the PCI driver, and can fallback to a manual host-bridge lookup. Probe enables the PCI device, maps MCHBAR, rejects disabled ECC, registers EDAC, and returns. Polling runs `i82975x_check()`. Remove deletes the EDAC MC, unmaps MCHBAR, and frees the MC object. Module exit unregisters the PCI driver and conditionally calls manual removal when the fallback path was used.

## State and Persistence
State is kernel-only: mapped MCHBAR, EDAC MC/DIMM metadata, global `mci_pdev`, and `i82975x_registered`. Hardware error bits are cleared on every snapshot. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on PCI config space, `ioremap`, EDAC MC APIs, Intel 82975X PCI IDs, and EDAC opstate configuration. It does not create generic EDAC PCI control unlike some older sibling drivers.

## Risks and Edge Cases
The EDAC layer sizing is unusual: it sets chip-select size to all DIMMs and channel size to `I82975X_NR_CSROWS(chans)`, so topology assumptions need hardware validation. Mixed asymmetric memory is treated as single-channel for channel attribution. The driver assumes ECC requires x8 devices and hardcodes SECDED. Error snapshots are racy, and MCHBAR must already be enabled by firmware. Fallback registration state is easy to mishandle.

## Test Signals
Signals include successful MCHBAR mapping, ECC-disabled rejection, DIMM labels and row sizes matching DRB registers, correct CE/UE reports including XEAP high-address cases, correct single-vs-dual-channel detection on asymmetric layouts, and clean unmap/free on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/i82975x_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/ie31200_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/ie31200_edac.c Research

## Purpose
`ie31200_edac.c` supports Intel E3-1200 and related Core/Xeon client/server host-bridge DRAM controllers across Sandy/Ivy/Haswell, Skylake/Kaby/Coffee, Alder/Raptor/Bartlett generations. It maps MCHBAR windows, decodes DIMM geometry from generation-specific MAD_DIMM registers, reads ECC error log registers, and reports errors either by EDAC polling or CMCI/MCE notification.

## Important APIs, Types, and Functions
`struct res_config` describes per-generation register layout: memory type, CMCI usage, number of IMCs, MCHBAR mask/window size, ECC log offsets/masks, optional MSR clear register, and MAD_DIMM size/rank/width masks. `struct ie31200_priv` stores one controller's MMIO window, channel ECC log addresses, config, MC pointer, PCI device, and a unique device object for multi-IMC systems. Global `ie31200_pvt.priv[]` indexes active controllers.

`how_many_channels()` and `ecc_capable()` read CAPID0 feature bits. `ie31200_map_mchbar()` combines low/high MCHBAR config DWORDs, applies the config mask, offsets per IMC, and maps the window. `ie31200_get_dimm_config()` reads MAD_DIMM registers for both channels, uses `populate_dimm_info()` to compute size/ranks/device width, and fills rank-level EDAC DIMM entries. `ie31200_get_and_clear_error_info()` reads MMIO ECC logs with `lo_hi_readq()` and clears either via the legacy PCI ERRSTS path or generation-specific MSR. `ie31200_process_error_info()` reports UE/CE per channel using rank and syndrome masks.

## Control Flow
PCI probe enables the host bridge, checks ECC capability, registers each configured IMC with EDAC, and selects interrupt or polling mode. Non-CMCI configurations set `mci->edac_check = ie31200_check`; CMCI configurations register `ie31200_mce_dec` and set `edac_op_state = EDAC_OPSTATE_INT`. The MCE notifier filters memory-related machine checks, logs diagnostic fields, calls each active controller's check path with the MCE address, and marks the MCE handled.

Remove drops the PCI reference, unregisters the MCE notifier for CMCI configurations, unregisters all MCs, unmaps windows, releases per-controller device objects, and frees EDAC state.

## State and Persistence
Runtime state includes per-IMC MMIO mappings, EDAC MC objects, per-controller device identities, global channel count, global PCI reference, and MCE notifier registration. Error logs are hardware registers that are cleared after snapshot. No persistent state is written.

## Dependencies and Integration Points
The driver depends on PCI, EDAC MC APIs, x86 MCE notifier APIs, MSR writes, `lo_hi_readq()` to obey 32-bit MMIO access restrictions, and generation-specific Intel PCI IDs. It integrates with EDAC opstate and MCE handled flags.

## Risks and Edge Cases
`nr_channels` is global even though multiple IMCs can be registered, so multi-controller platforms assume the same channel count. CMCI error reports rely on MCE address for page reporting, while polling has no address and reports page 0. MSR clearing failures are logged but not fatal. Register mask tables must match each PCI ID exactly; a wrong `res_config` corrupts DIMM sizing and error attribution.

## Test Signals
Validate probe across listed PCI IDs, ECC-capability rejection, MCHBAR mapping above 32-bit resource boundaries, DIMM size/rank/width decoding for DDR3/DDR4/DDR5 configs, legacy polling and CMCI notifier paths, MSR clear success/failure logging, and clean multi-IMC unregister with unique EDAC device names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/ie31200_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/igen6_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/igen6_edac.c Research

## Purpose
`igen6_edac.c` is the EDAC driver for Intel client SoCs with In-Band ECC (IBECC). It detects IBECC-capable PCI host bridges, maps MCHBAR/IMC/IBECC register windows, builds EDAC DIMM topology, decodes IBECC error-log addresses into system/channel/DIMM locations, and handles error notification through polling, SERR NMI, or MCE depending on the SoC generation.

## Important APIs, Types, and Functions
`struct res_config` captures per-generation behavior: machine-check mode, number of IMCs, MCHBAR/TOM masks, ECC log masks, IMC/CMF/IBECC offsets, availability callbacks, optional custom error-address extraction, and address conversion callbacks. Config instances cover EHL, ICL, TGL, ADL/ADL-N/AZB/ASL, RPL-P, Meteor/Arrow/Panther/Wildcat variants. `struct igen6_imc` holds one controller's EDAC MC, PCI device, unique device object, mapped window, channel and DIMM decode sizes/maps. `struct igen6_pvt` holds all IMCs plus memory-slice hash state.

`igen6_pci_setup()` checks IBECC availability, reads TOLUD/TOM/MCHBAR, and initializes global memory bounds. Address translation helpers handle generation differences: EHL low/high hole adjustments, TGL memory-slice hashing, ADL IMC address extraction, and RPL-P ECC-log address masks. `igen6_get_dimm_config()` reads MAD_INTER/MAD_INTRA/MAD_DIMM registers, verifies IBECC activation, and fills DIMM size/type/width/grain/SECDED metadata. `igen6_decode()` decodes channel and sub-channel using hash registers. `igen6_output_error()` reports to EDAC with syndrome and decoded channel/sub-channel.

The error path uses `ecclog_read_and_clear()`, `ecclog_gen_pool_add()`, a lockless `llist`, `irq_work`, and a workqueue. This lets NMI/MCE context snapshot and queue ECC logs while the worker performs printk and EDAC reporting. Debug builds expose `igen6_test/addr` to inject a fake corrected log.

## Control Flow
Probe allocates global state, selects the generation config, validates PCI/MCHBAR, sets EDAC opstate, maps and registers present IMCs, reads memory-slice hash state when needed, creates the NMI-safe pool, initializes work items, registers the proper error handler, enables PCI error reporting, drains pending logs, and sets up debugfs. Polling calls `igen6_check()` per MC. NMI/MCE handlers call `ecclog_handler()` and schedule deferred processing. Remove disables debugfs and reporting, unregisters handlers, synchronizes irq_work/workqueue, destroys the pool, unregisters MCs, unmaps windows, and frees global state.

## State and Persistence
State lives in mapped MMIO, EDAC MC objects, global `res_cfg`/`igen6_pvt`, global TOLUD/TOM, the ECC log gen_pool, lockless list, irq_work/workqueue, and optional debugfs. Error log registers are cleared by write-one-to-clear. No disk persistence is used.

## Dependencies and Integration Points
The driver depends on PCI, EDAC MC/debugfs helpers, x86 MCE and NMI APIs, `genalloc`, lockless lists, irq_work, and GHES/EDAC owner arbitration. It refuses to load when GHES owns error reporting or another EDAC owner is active.

## Risks and Edge Cases
NMI safety is central: allocation uses a prebuilt gen_pool and heavy work is deferred. Pool exhaustion drops detailed reporting for some logs. Address translation is generation-specific and sensitive to hash register semantics. `errcmd_enable_error_reporting()` uses `ERRSTS_UE` in the mask path, which is numerically aligned but semantically surprising. Some SoCs force polling because interrupts are unreliable. Invalid ECC logs of all ones are explicitly skipped to avoid floods.

## Test Signals
Test with supported PCI IDs should verify IBECC availability gating, MCHBAR and IMC absent detection, DIMM geometry and ECC-active checks, polling/NMI/MCE paths, correct decoding of multi-IMC and memory-slice interleaves, debugfs fake error reporting under `CONFIG_EDAC_DEBUG`, clean synchronization on remove, and no reports when GHES owns EDAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/igen6_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/imh_base.c -->
# sources/distributed-fs/ceph-client/drivers/edac/imh_base.c Research

## Purpose
`imh_base.c` is the EDAC base driver for Intel server processors with Integrated Memory/IO Hub-based memory controllers, currently matching Diamond Rapids. It discovers per-package IMH MMIO bases through local package views, enumerates DDR memory-controller units on north/south IMHs, registers them through shared `skx_common` helpers, and wires MCE decode into the SKX-family EDAC reporting path.

## Important APIs, Types, and Functions
`struct local_reg` describes a register in a package-local MMIO view. `read_local_reg()` finds an online CPU in the target package, maps the local physical base, and uses `smp_call_function_single()` to read the register from that package's view. `DEFINE_LOCAL_REG()` constructs these descriptors from the large `struct res_config` layout shared with `skx_common`.

Discovery starts with `imh_get_tolm_tohm()`, `imh_get_imc_num()`, and `imh_get_all_mmio_base_h()`. `__get_ddr_munits()` maps each present DDR IMC's channel MMIO, creates a device object for EDAC identity, and programs physical-to-logical MC mapping with `skx_set_mc_mapping()`. `imh_get_munits()` sets channel/dimm counts and global MC indexes. `imh_get_dimm_config()` reads MCMTR and DIMMMTR registers per channel/DIMM, delegates sizing to `skx_get_dimm_info()`, and rejects populated channels without ECC enabled. `imh_register_mci()` registers each IMC via `skx_register_mci()`.

The `dmr_cfg` resource configuration specifies Diamond Rapids DDR5 parameters, local MMIO bases/sizes, register offsets/widths for Ubox, PCU, SCA, and HA blocks, and channel/DIMM layout. The module uses `skx_mce_check_error` as its MCE notifier callback.

## Control Flow
Module init rejects GHES ownership, other EDAC owners, hypervisors, and non-matching CPUs. It installs the resource config, reads TOLM/TOHM into SKX shared state, discovers present IMCs and MMIO bases, maps memory units, checks 2-level memory mode through HA registers, registers MCs, obtains ADXL address decode support, initializes opstate, registers the MCE notifier, and sets up SKX debug support. Exit tears down debug, MCE notifier, ADXL, and all SKX-managed registrations/mappings.

## State and Persistence
Runtime state is mostly managed through shared `skx_common`: the EDAC list, SKX device/IMC structures, mappings, high/low memory limits, and debug state. This file also creates per-IMC `struct device` instances and MMIO mappings. No persistent storage exists.

## Dependencies and Integration Points
The driver depends heavily on `skx_common.h`/shared SKX EDAC helpers, x86 CPU matching, package topology, SMP cross-calls, IO mapping, x86 MCE notifiers, ADXL decode, GHES and EDAC owner arbitration.

## Risks and Edge Cases
Local-view register reads require at least one online CPU per target package; offline packages fail discovery. North IMH MMIO base is mandatory while south is optional. Allocation failure in `__get_ddr_munits()` after mapping can rely on later `skx_remove()` cleanup. Config register offsets must match hardware exactly. The driver skips virtualized environments, so test coverage requires bare-metal server hardware.

## Test Signals
Signals include CPU match on Diamond Rapids, correct local Ubox/PCU/SCA/HA reads per package, DDR IMC bitmap matching hardware, EDAC MC count and DIMM geometry matching populated DDR5, ECC-disabled rejection, 2LM detection, MCE decode through `skx_mce_check_error`, ADXL acquisition/release, and clean `skx_remove()` cleanup on failed init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/imh_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/layerscape_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/layerscape_edac.c Research

## Purpose
`layerscape_edac.c` is a thin platform-driver wrapper for Freescale/NXP Layerscape and i.MX9 DDR memory-controller EDAC support. It binds device-tree compatible strings to the shared Freescale DDR EDAC probe/remove implementation and selects a sane EDAC reporting mode.

## Important APIs, Types, and Functions
The Open Firmware match table accepts `"fsl,qoriq-memory-controller"` and `"nxp,imx9-memory-controller"`, passing `TYPE_IMX9` for i.MX9-specific handling in shared code. The `platform_driver` named `"fsl_ddr_mc_err"` delegates `.probe` to `fsl_mc_err_probe` and `.remove` to `fsl_mc_err_remove`, both declared in `fsl_ddr_edac.h`.

`fsl_ddr_mc_init()` is the only local setup function. It checks GHES ownership, normalizes `edac_op_state` to polling or interrupt mode, registers the platform driver, and logs registration failure. `fsl_ddr_mc_exit()` unregisters the platform driver.

## Control Flow
Module init runs before platform binding. If GHES devices are present, it returns `-EBUSY` to avoid conflicting firmware-first reporting. Otherwise, it ensures unsupported opstates fall back to interrupt mode, registers the platform driver, and lets the platform bus invoke shared probe for matching DT nodes. Exit simply unregisters the driver.

## State and Persistence
This file has no private persistent state beyond platform-driver registration. Device-specific state is owned by the shared Freescale DDR EDAC implementation. The module parameter `edac_op_state` controls polling vs interrupt behavior.

## Dependencies and Integration Points
It depends on `edac_module.h`, `fsl_ddr_edac.h`, Open Firmware matching, platform bus registration, and GHES arbitration. Its primary integration point is the shared Freescale DDR EDAC driver, not local hardware access.

## Risks and Edge Cases
Most behavioral risk is delegated. Local risks are configuration-level: wrong compatible data would route a platform to the wrong shared behavior, and forcing invalid opstates to interrupt mode may surprise callers expecting NMI or other states. GHES conflict handling prevents duplicate reporting.

## Test Signals
Verify module init returns `-EBUSY` under GHES, DT nodes bind for both compatibles, `TYPE_IMX9` data reaches shared probe, `edac_op_state` normalizes to `EDAC_OPSTATE_INT` for invalid inputs, shared probe/remove run, and platform-driver unregister cleans bindings on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/layerscape_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/loongson_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/loongson_edac.c Research

## Purpose
`loongson_edac.c` is a compact ACPI/platform EDAC driver for a Loongson memory controller. It maps one MMIO resource, reads a cumulative corrected-error counter across chip-select fields, computes deltas between polls, and reports corrected errors to the EDAC core.

## Important APIs, Types, and Functions
`struct loongson_edac_pvt` stores the mapped ECC base and the last observed corrected-error count. `read_ecc()` reads `ECC_CS_COUNT_REG` with `readq()`, sums four 8-bit chip-select count fields, and returns the total. `edac_check()` reads the current total, subtracts `last_ce_count`, updates the baseline, and reports a corrected event count when the delta is positive. `dimm_config_init()` creates a single channel/slot DIMM entry with placeholder full-size pages, label, and grain. `pvt_init()` stores MMIO base and initializes the baseline counter.

`edac_probe()` maps the platform resource through `devm_platform_ioremap_resource()`, allocates a two-layer one-channel/one-slot EDAC topology, fills controller metadata, installs `edac_check`, initializes private and DIMM state, registers the MC, and forces polling mode. `edac_remove()` unregisters and frees the MC.

## Control Flow
The module uses `module_platform_driver()`. ACPI ID `LOON0010` binds the driver. Probe allocates and registers one EDAC controller per platform device. EDAC polling invokes `edac_check()` to turn monotonically increasing hardware counters into event deltas. Remove deletes the EDAC MC by platform device and frees it.

## State and Persistence
The hardware counter cannot be zeroed, so the driver's only persistent runtime state is `last_ce_count`, held in memory. The MMIO mapping is devm-managed. No filesystem state exists.

## Dependencies and Integration Points
The driver depends on ACPI platform enumeration, platform resource mapping, EDAC MC APIs, `io-64-nonatomic-lo-hi`, and Loongson-specific counter layout. It integrates only with EDAC polling, not interrupts or MCE notifiers.

## Risks and Edge Cases
Counter wraparound is not handled: if the summed 8-bit fields wrap, the delta becomes negative and the event is skipped. DIMM size/type data is placeholder rather than decoded from hardware. Only corrected errors are reported; uncorrected/fatal paths are absent. The summed counter loses chip-select attribution.

## Test Signals
Signals include ACPI binding to `LOON0010`, successful resource mapping, initial baseline preventing stale count reports, corrected-error delta reports under polling, no report when counts do not increase, behavior across counter wrap, and clean EDAC unregister on platform removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/loongson_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mce_amd.c -->
# sources/distributed-fs/ceph-client/drivers/edac/mce_amd.c Research

## Purpose
`mce_amd.c` is the in-kernel AMD/Hygon Machine Check Exception decoder used by EDAC. It registers an early MCE notifier, decodes legacy AMD MCA banks by CPU family, decodes Scalable MCA bank types on newer CPUs, prints detailed hardware-error diagnostics, and exposes a callback hook so memory-controller EDAC drivers can add DRAM ECC address/location decoding.

## Important APIs, Types, and Functions
The exported hook pair `amd_register_ecc_decoder()` and `amd_unregister_ecc_decoder()` manages the global `decode_dram_ecc` callback. `pp_msgs` is also exported for other AMD EDAC code. `struct amd_decoder_ops fam_ops` stores family-specific decoders for MC0/MC1/MC2; `mce_amd_init()` selects K8, Family 10h/11h/12h/14h/15h/16h implementations and the extended-error-code mask.

Legacy bank decoders include `decode_mc0_mce()` through `decode_mc6_mce()`, backed by family-specific helpers such as `k8_mc0_mce()`, `f15h_mc1_mce()`, and `f16h_mc2_mce()`. `decode_mc4_mce()` handles northbridge/DRAM ECC errors and invokes `decode_dram_ecc()` for supported DRAM ECC xEC values. `decode_smca_error()` uses `smca_get_bank_type()` and `smca_long_names[]` to report Scalable MCA units and invokes the DRAM ECC callback for UMC/UMC_V2 errors with xEC 0.

`amd_decode_mce()` is the notifier body. It prints severity from `decode_error_status()`, status flags, address/PPIN/IPID/syndrome/FRU text when valid, dispatches SMCA or legacy bank-specific decode, prints generic error-code fields through `amd_decode_err_code()`, marks the MCE handled, and returns `NOTIFY_OK`.

## Control Flow
`early_initcall(mce_amd_init)` runs on boot/module init. It rejects non-AMD/Hygon CPUs and hypervisors, chooses SMCA or legacy family support, logs enablement, and registers `amd_mce_dec_nb` with priority `MCE_PRIO_EDAC`. At MCE time, already-CEC-handled records are ignored. SMCA systems use bank type decoding; older systems switch on `m->bank`. Module builds unregister the notifier on exit.

## State and Persistence
State is global and in-memory: selected decoder ops, `xec_mask`, the optional DRAM ECC callback, and notifier registration. The module writes kernel log diagnostics but no persistent state. It does not clear hardware MCE registers; it decodes records supplied by the x86 MCE core.

## Dependencies and Integration Points
The file depends on x86 CPU feature/family helpers, MCE structures/status bits, SMCA bank-type helpers, MSR reads, kernel notifier APIs, EDAC priority conventions, and `mce_amd.h` macros. Its callback hook is used by AMD memory-controller EDAC drivers to enrich DRAM ECC reports.

## Risks and Edge Cases
The callback pointer is global and not locked; registration order assumes EDAC module lifecycle discipline. Unsupported families 17h/18h without SMCA return `-EINVAL`. Logging uses `pr_emerg()`/`pr_cont()` sequences, so malformed interleaving can affect readability. SMCA FRU text is copied from vendor syndrome fields and treated as a 16-byte string. Incorrect xEC masks or bank-type mappings lead to misleading diagnostics rather than failed handling.

## Test Signals
Test with synthetic MCE records or hardware injection should cover SMCA UMC errors invoking the DRAM callback, legacy family bank 0-6 decode paths, corrected/deferred/uncorrected/fatal status messages, address/IPID/syndrome/FRU printing, ignored `MCE_HANDLED_CEC` records, callback register/unregister warning behavior, and notifier unregister for module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mce_amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mce_amd.h -->
# sources/distributed-fs/ceph-client/drivers/edac/mce_amd.h Research

## Purpose
`mce_amd.h` is the internal/public header for the AMD EDAC MCE decoder. It defines bitfield macros for AMD MCA error-code interpretation, enums for decoded field IDs, the per-family decoder-ops structure, and exported registration APIs for DRAM ECC decoders.

## Important APIs, Types, and Functions
Macros `EC()`, `LOW_SYNDROME()`, and `HIGH_SYNDROME()` extract generic status fields. `TLB_ERROR()`, `MEM_ERROR()`, `BUS_ERROR()`, and `INT_ERROR()` classify MCA error codes. `TT()`, `II()`, `LL()`, `TO()`, `PP()`, `UU()`, and `R4()` extract transaction, memory/IO, cache-level, timeout, participating-processor, internal-error, and memory-transaction fields; the corresponding `_MSG()` macros index message tables defined in `mce_amd.c`.

The enums `tt_ids`, `ll_ids`, `ii_ids`, and `rrrr_ids` name the encoded values used by the decoder logic. `struct amd_decoder_ops` carries function pointers for family-specific MC0/MC1/MC2 decoding. `amd_register_ecc_decoder()` and `amd_unregister_ecc_decoder()` let AMD memory-controller EDAC drivers attach a DRAM ECC decoder callback. `pp_msgs` is declared for external use.

## Control Flow
This header has no runtime control flow. It shapes the control flow in `mce_amd.c` and companion AMD EDAC drivers by providing classification predicates and callback declarations.

## State and Persistence
The header defines no storage except external declarations. State lives in the implementation file and consumers.

## Dependencies and Integration Points
It depends on Linux notifier declarations and `asm/mce.h` for `struct mce` and MCE bit definitions. It integrates the generic AMD MCE decoder with memory-controller-specific DRAM ECC decoding modules.

## Risks and Edge Cases
The macros assume AMD MCA encoding layouts. Using them for non-AMD/Hygon records or future encodings without updates can misclassify errors. `_MSG()` macros do not bounds-check except `R4_MSG()`, so callers rely on masked field widths matching message table lengths. Callback signatures expose only node ID and raw MCE, so richer topology must be derived by consumers.

## Test Signals
Header-level test signals are compile coverage across `mce_amd.c` and AMD EDAC users, correct macro expansion for representative status values, exported symbol availability for callback registration, and static analysis confirming enum/macro values align with decoder tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mce_amd.h -->
