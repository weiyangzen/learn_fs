# Research Group: subset-b-001271

This grouped report covers EDAC memory-controller, EDAC device, debugfs, sysfs, and RAS feature support under `sources/distributed-fs/ceph-client/drivers/edac/`. Each section is delimited for reconciliation into the requested per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/armada_xp_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/armada_xp_edac.c

## Purpose
This file implements EDAC support for Marvell Armada XP-class hardware. It registers two platform drivers: one `mem_ctl_info` memory-controller driver for the Armada XP SDRAM controller and one `edac_device_ctl_info` driver for the Aurora L2/system-cache controller. The memory side reports SDRAM single-bit and double-bit ECC events; the L2 side reports cache correctable and uncorrectable/tag-parity events, with optional debugfs-based injection controls under `CONFIG_EDAC_DEBUG`.

## Important APIs, Types, And Functions
The memory-controller private state is `struct axp_mc_drvdata`, which stores the MMIO base, detected bus width, chip-select address-interleaving flags, and a fixed diagnostic message buffer. The L2 private state is `struct aurora_l2_drvdata`, which stores MMIO base, a message buffer, optional injection fields, and a debugfs dentry.

Key functions are `axp_mc_probe()`, `axp_mc_remove()`, `axp_mc_read_config()`, `axp_mc_check()`, and `axp_mc_calc_address()` for SDRAM EDAC. `aurora_l2_probe()`, `aurora_l2_remove()`, `aurora_l2_poll()`, `aurora_l2_check()`, and `aurora_l2_inject()` cover the cache EDAC path. Module initialization uses `platform_register_drivers()` after rejecting coexistence with GHES via `ghes_get_devices()`.

## Control Flow
`armada_xp_edac_init()` forces polling mode, registers both platform drivers, and exits early with `-EBUSY` if GHES owns error reporting. `axp_mc_probe()` maps SDRAM registers, verifies ECC is enabled, allocates a one-layer chip-select EDAC topology, fills `mci` metadata, reads chip-select/DIMM configuration, programs an SBE threshold, clears stale status/counters, and calls `edac_mc_add_mc()`. During polling, `axp_mc_check()` snapshots the error data, ECC, address, count, and cause registers; clears cause and count state; reports aggregate earlier errors without location; then decodes the most recent error into chip-select/bank/row/column, computes a PFN/offset, and reports CE or UE through `edac_mc_handle_error()`.

For Aurora L2, `aurora_l2_probe()` maps registers, warns if parity/ECC are not enabled, allocates an EDAC device with one `cpu` instance and two `L` blocks, clears counters/capture registers, adds the EDAC device, and optionally exposes injection registers in debugfs. `aurora_l2_poll()` calls `aurora_l2_check()` and then performs debug injection if configured. `aurora_l2_check()` reads counter/capture registers, clears counters, decodes source/transaction/error/address/index/way, emits either `edac_device_handle_ce()` or `edac_device_handle_ue()`, clears capture validity, and reports any remaining count as detail-less events.

## State And Persistence
Persistent runtime state lives in hardware registers and in EDAC core structures. Driver-private state caches bus width and chip-select interleaving because those values are needed to reconstruct addresses during later polling. Error counters are cleared after each poll to prevent duplicate reports. The L2 injection fields persist only while the device is bound and, under debug builds, are user-modifiable through debugfs.

## Dependencies And Integration Points
The driver depends on platform/OF matching (`marvell,armada-xp-sdram-controller` and `marvell,aurora-system-cache`), `devm_platform_ioremap_resource()`, Aurora/L2X0 register definitions, EDAC MC APIs, EDAC device APIs, EDAC module globals, and debugfs wrappers. It integrates with `/sys/devices/system/edac/mc` through `edac_mc_add_mc()` and with generic EDAC device sysfs through `edac_device_add_device()`.

## Risks
Address reconstruction is hardware-specific and sensitive to bus width and interleaving bits; incorrect width adjustments for Armada 380 and 98dx3236 would misattribute errors. The L2 `clear_remaining` loop reports remaining CE counts with `edac_device_handle_ue()` in the final loop, which is worth review because it appears to classify detail-less CEs as UEs. Error messages are assembled into fixed buffers; the code sizes them conservatively but relies on careful formatting. Polling clears hardware status, so races with other firmware or error handlers would lose events, hence the GHES exclusion.

## Test Signals
Useful signals include successful platform binding, EDAC sysfs nodes for `mc0` and the L2 `cpu` device, correct DIMM sizes from `axp_mc_read_config()`, no stale events after probe clears counters, and injected Aurora L2 events under `CONFIG_EDAC_DEBUG`. Hardware tests should cover SBE/DBE count handling, multiple-error aggregation, chip-select mapping, and L2 capture-register valid/invalid paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/armada_xp_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/aspeed_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/aspeed_edac.c

## Purpose
This file implements an interrupt-driven EDAC memory-controller driver for Aspeed AST2400, AST2500, and AST2600 BMC SDRAM controllers. It reports recoverable and unrecoverable ECC events from the memory controller interrupt/status register and derives memory geometry from the device tree `/memory` node.

## Important APIs, Types, And Functions
The driver uses a global `struct regmap *aspeed_regmap` backed by custom `regmap_reg_read()` and `regmap_reg_write()` callbacks. Writes unlock the controller register set with `ASPEED_MCR_PROT_PASSWD`, write the target register, then lock it again. `regmap_is_volatile()` marks protection, interrupt, and error-address registers volatile.

Key functions are `aspeed_probe()`, `aspeed_remove()`, `config_irq()`, `mcr_isr()`, `count_rec()`, `count_un_rec()`, and `init_csrows()`. `count_rec()` reports all but the last recoverable error without address detail and reports the last recoverable address. `count_un_rec()` reports the first unrecoverable error with address detail and any additional unaddressed UEs.

## Control Flow
`aspeed_probe()` maps MCR registers, initializes the regmap, verifies that firmware configured ECC, sets `edac_op_state` to interrupt mode, allocates a chip-select/channel EDAC topology, fills controller capabilities, initializes csrow and DIMM metadata from `/memory` and `ASPEED_MCR_CONF`, registers the controller with EDAC, and finally requests/enables the IRQ. On interrupt, `mcr_isr()` reads `ASPEED_MCR_INTR_CTRL`, extracts recoverable and unrecoverable counters, reads the stored address registers, toggles the clear bit to clear flags/counters, and dispatches CE/UE reporting helpers.

## State And Persistence
The controller's address and count state is hardware-latched until the ISR clears it. The EDAC core stores per-DIMM and controller counters after `edac_mc_handle_error()` calls. The global regmap assumes one active Aspeed EDAC controller instance. DIMM geometry comes from the device tree memory resource and persists in `mci->csrows[0]` and its first DIMM.

## Dependencies And Integration Points
The driver depends on OF platform matching, memory-node parsing with `of_find_node_by_name()` and `of_address_to_resource()`, Linux regmap, interrupt registration, and EDAC MC APIs. It integrates with EDAC sysfs through `edac_mc_add_mc()` and with platform driver probing through `module_platform_driver()`.

## Risks
The global `aspeed_regmap` is simple but not multi-instance safe. The driver trusts firmware to have enabled ECC and returns `-EPERM` otherwise. Recoverable events only preserve the last address, while unrecoverable events only preserve the first address, so multi-error bursts necessarily lose per-event location detail. IRQ setup occurs after EDAC registration; probe error handling removes the controller if IRQ setup fails.

## Test Signals
Tests should confirm probe refusal when ECC is disabled, correct `/memory` sizing and first-page handling, IRQ handler counter extraction, clear-bit sequencing, and CE/UE count propagation in sysfs. Platform tests should verify AST2400/2500/2600 compatible strings and interrupt polarity/trigger behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/aspeed_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/bluefield_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/bluefield_edac.c

## Purpose
This file implements the Mellanox/NVIDIA BlueField memory EDAC driver. It monitors the External Memory Interface ECC counters, reports single-bit and double-bit ECC events, and initializes DIMM metadata using BlueField SiP SMC calls and ACPI-provided platform properties.

## Important APIs, Types, And Functions
`struct bluefield_edac_priv` holds the parent device, DIMM rank counts, EMI register base, DIMMs-per-controller count, secure-register support state, and secure register table number. `smc_call1()` retrieves DIMM information. `secure_readl()` and `secure_writel()` access secure registers via Arm SMCCC when ACPI provides a `sec_reg_block`; otherwise `bluefield_edac_readl()` and `bluefield_edac_writel()` use direct MMIO.

Key flows are `bluefield_edac_mc_probe()`, `bluefield_edac_mc_remove()`, `bluefield_edac_init_dimms()`, `bluefield_edac_check()`, and `bluefield_gather_report_ecc()`. The ACPI match ID is `MLNXBF08`.

## Control Flow
Probe reads ACPI properties `mss_number` and `dimm_per_mc`, validates the DIMM count, gets the EMI memory resource, allocates a slot-layer EDAC topology, determines whether direct MMIO or secure SMC register access is required, maps or stores the EMI base, fills `mci` metadata, initializes DIMMs by calling `MLXBF_SIP_GET_DIMM_INFO`, registers with EDAC, and selects polling mode. During polling, `bluefield_edac_check()` reads ECC counters, extracts single and double counts, calls `bluefield_gather_report_ecc()` for each nonzero class, then writes `MLXBF_ECC_ERR` bits to clear reported errors.

`bluefield_gather_report_ecc()` starts a latch operation, reads syndrome bits, verifies that the latched type matches the requested CE/UE type, reads rank/additional information and 64-bit error address, chooses a DIMM based on physical rank and stored rank count, and reports to EDAC with PFN, offset, syndrome, and layer coordinates.

## State And Persistence
Hardware ECC counters and latched error information are consumed during polling and cleared after reporting. DIMM population, page counts, type, width, and rank counts are stored in EDAC `dimm_info` structures and the driver's private rank array. If all DIMMs are empty, `mci->edac_cap` is set to `EDAC_FLAG_NONE`, causing later checks to return early.

## Dependencies And Integration Points
The driver depends on ACPI platform devices, device properties, Arm SMCCC, BlueField SiP services, EDAC MC APIs, bitfield helpers, and MMIO mapping. It integrates with EDAC sysfs through `edac_mc_add_mc()` and with firmware-provided DIMM inventory and secure-register policy.

## Risks
SMC service version or access violations make secure-register systems fail probe or skip reports. DIMM selection from physical rank is heuristic and depends on `dimm_ranks[0]`. If the latch returns a different error type than requested, the driver reports only aggregate count without location. Because it is polling-based, delayed polling can collapse multiple events into one count with only one detailed address.

## Test Signals
Important signals include ACPI property validation, both direct-MMIO and secure-SMC access paths, empty-DIMM behavior, ECC counter clearing, correct PFN/offset formation from two address registers, and CE/UE sysfs counter updates. Firmware test coverage should include missing/old SiP service versions and access-denied secure register calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/bluefield_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/cpc925_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/cpc925_edac.c

## Purpose
This file implements EDAC support for the IBM CPC925 bridge and memory controller. It covers three error domains: the memory controller as an EDAC MC, CPU/processor-interface errors as an EDAC device, and HyperTransport link errors as another EDAC device. All reporting is polling-based.

## Important APIs, Types, And Functions
`struct cpc925_mc_pdata` stores MMIO base, total memory, controller name, and EDAC index. `struct cpc925_dev_info` describes the synthetic EDAC devices that share the memory-controller MMIO base. `cpc925_devs[]` defines CPU and HT-link devices with init/exit/check callbacks.

Important memory-controller functions include `cpc925_probe()`, `cpc925_remove()`, `cpc925_init_csrows()`, `cpc925_mc_init()`, `cpc925_mc_check()`, `cpc925_mc_get_pfn()`, `cpc925_mc_find_channel()`, and `cpc925_get_sdram_scrub_rate()`. Device-side functions include `cpc925_add_edac_devices()`, `cpc925_del_edac_devices()`, `cpc925_cpu_check()`, and `cpc925_htlink_check()`.

## Control Flow
`cpc925_edac_init()` sets polling mode and registers a platform driver. Probe opens a devres group, obtains and maps MMIO, derives channel count from `MBCR`, allocates a chip-select/channel EDAC topology, initializes DIMM/csrow data from OF memory and CPC925 bank registers, enables ECC exception and check bits, registers the memory controller, and then creates synthetic platform devices for CPU and HT-link EDAC devices.

Polling `cpc925_mc_check()` reads the clear-on-read `APIEXCP` register, exits if no ECC exception is present, reads syndrome and address registers, reconstructs PFN/offset from rank/row/bank/column fields, and reports CE or UE through `edac_mc_handle_error()`. CPU polling reads processor-interface exception bits, filters absent CPU interfaces, dumps relevant registers, and reports a UE. HT polling reads bridge/link/error registers, clears write-one-to-clear bits, may initiate secondary bus reset for chain failure, and reports a CE.

## State And Persistence
Hardware exception bits and counters are the source of truth. `cpc925_cpu_mask_disabled()` caches absent-CPU mask in a static variable after inspecting OF CPU nodes. The driver intentionally does not disable memory-controller or CPU error-detection bits on exit because comments warn that re-enabling them on module reload can trigger machine-check exceptions. EDAC core counters persist while devices are registered.

## Dependencies And Integration Points
The driver depends on OF memory and CPU nodes, platform resources, raw MMIO accessors, EDAC MC APIs, EDAC device APIs, and EDAC sysfs. Synthetic platform devices are registered because CPU and HT-link error domains do not have separate firmware nodes.

## Risks
PFN reconstruction is complex and mode-specific, so address attribution is a risk. `APIEXCP` is clear-on-read; multiple polling consumers or careless debug reads could lose state. Some exit callbacks deliberately leave hardware detection enabled, so tests that expect full hardware rollback will be misleading. Error-domain devices share the same MMIO region with the MC, so removal order matters and is correctly handled by deleting EDAC devices before the MC.

## Test Signals
Coverage should include populated and empty bank boundary parsing, single/dual channel configuration, CE/UE exception decoding, CPU-node mask calculation, HT write-one-to-clear behavior, scrub-rate reads, and remove order. Hardware error injection or controlled register emulation is needed to validate the clear-on-read and PFN reconstruction paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/cpc925_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/edac/debugfs.c

## Purpose
This file provides EDAC debugfs support. It creates the top-level `debugfs` directory for EDAC, exposes generic memory-controller fake-error injection controls, and exports helper wrappers for EDAC drivers that need debugfs files or directories.

## Important APIs, Types, And Functions
The top-level state is the static `struct dentry *edac_debugfs`. `edac_debugfs_init()` creates `/sys/kernel/debug/edac`, and `edac_debugfs_exit()` removes it recursively. `edac_create_debugfs_nodes()` creates per-memory-controller injection controls.

`edac_fake_inject_write()` is the write handler for `fake_inject`; it chooses CE or UE from `mci->fake_inject_ue`, defaults count to one if `fake_inject_count` is zero, and calls `edac_mc_handle_error()` with user-selected layer indexes. Exported wrappers include `edac_debugfs_create_dir()`, `edac_debugfs_create_dir_at()`, `edac_debugfs_create_file()`, `edac_debugfs_create_x8()`, `edac_debugfs_create_x16()`, and `edac_debugfs_create_x32()`.

## Control Flow
At EDAC core initialization, `edac_debugfs_init()` creates the root. When a memory controller is added to sysfs, `edac_create_debugfs_nodes()` creates a child directory named after `mci->dev.kobj.name`, creates `fake_inject_<layer-name>` files for each MC hierarchy layer, creates `fake_inject_ue` and `fake_inject_count`, and creates the write-only `fake_inject` trigger file. On removal, callers remove `mci->debugfs`, and final EDAC shutdown removes the top-level tree.

## State And Persistence
Debugfs files directly modify fields embedded in `struct mem_ctl_info`: `fake_inject_layer[]`, `fake_inject_ue`, and `fake_inject_count`. No state is persisted across device removal or module unload. Fake injection increments normal EDAC counters and emits normal EDAC logs/traces, but it does not exercise hardware-specific decoding.

## Dependencies And Integration Points
The file depends on debugfs, simple file operations, `edac_module.h`, `to_mci()`, `edac_layer_name[]`, and `edac_mc_handle_error()`. Several hardware drivers use the exported debugfs wrappers for driver-specific injection controls.

## Risks
Fake injection is for EDAC core handling only; it can create misleading confidence if treated as hardware decode coverage. Layer values are user-controlled and rely on `edac_mc_handle_error()` sanity checks for out-of-range positions. Helper wrappers fall back to the top-level EDAC debugfs directory if a parent is not provided.

## Test Signals
Signals include existence of per-MC fake injection files under debugfs, CE/UE counter increments after writing `fake_inject`, correct layer-name files for each topology, and full cleanup after MC removal and EDAC debugfs exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/dmc520_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/dmc520_edac.c

## Purpose
This file implements an interrupt-driven EDAC driver for the Arm DMC-520 memory controller. It currently handles DRAM ECC correctable and uncorrectable interrupts, initializes rank geometry from DMC registers, and reports errors through the EDAC MC core.

## Important APIs, Types, And Functions
`struct dmc520_edac` stores MMIO base, a spinlock protecting `mci->error_desc`, memory width, and arrays mapping discovered IRQs to interrupt masks. `struct ecc_error_info` carries decoded rank/bank/row/column details. `dmc520_irq_configs[]` maps ten named interrupt lines to status/control bits, although only DRAM ECC CE/UE paths produce EDAC reports.

Key functions are `dmc520_edac_probe()`, `dmc520_edac_remove()`, `dmc520_isr()`, `dmc520_edac_dram_all_isr()`, `dmc520_edac_dram_ecc_isr()`, `dmc520_handle_dram_ecc_errors()`, `dmc520_get_dram_ecc_error_count()`, `dmc520_get_dram_ecc_error_info()`, and `dmc520_init_csrow()`.

## Control Flow
Probe enumerates optional named IRQs, requires at least one valid line, maps registers, exits if DRAM ECC is disabled, allocates a chip-select EDAC topology sized by register-derived rank count, initializes private state and controller metadata, switches to interrupt mode, derives memory width/type/device width/rank size, initializes DIMM entries, masks and clears discovered interrupts, requests each IRQ, resets DRAM CE/UE counters, registers with EDAC, and enables the selected interrupt mask.

On interrupt, `dmc520_isr()` finds the matching mask for the Linux IRQ and calls `dmc520_edac_dram_all_isr()`. That function reads interrupt status and dispatches CE and/or UE handling only if both the IRQ's mask and hardware status bit are set. `dmc520_handle_dram_ecc_errors()` reads latched address info, reads and clears per-rank counters, formats rank/bank/row/column detail, takes `error_lock`, and calls `edac_mc_handle_error()`.

## State And Persistence
Hardware error counters are reset after reads. Interrupt enables live in DMC control registers and are modified to preserve unrelated bits. EDAC state persists in `mci` and per-DIMM counters. The global `dmc520_mc_idx` increments for each controller instance. The spinlock prevents concurrent ISR paths from corrupting the shared `mci->error_desc` buffer.

## Dependencies And Integration Points
The driver depends on OF matching (`arm,dmc-520`), platform named IRQs, MMIO, bitfield helpers, spinlocks, EDAC MC APIs, and module platform-driver registration. It exposes standard EDAC MC sysfs and uses `edac_op_state = EDAC_OPSTATE_INT`.

## Risks
`dmc520_edac_remove()` computes `irq_mask_all` only while freeing IRQs but clears interrupt control before accumulating it, so the intended disable mask is zero at the write point; that path is worth review. Non-DRAM interrupt lines can be requested and enabled but do not generate EDAC reports in current handlers. Invalid or zero memory width can lead to zero grain/rank-size-derived metadata. Shared IRQ handling returns `IRQ_NONE` unless relevant status bits are set.

## Test Signals
Tests should cover no-IRQ and ECC-disabled probe failures, named IRQ discovery, CE/UE counter reset, concurrent CE/UE interrupt serialization, rank count/size calculations, sysfs counter increments, and remove-time interrupt disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/dmc520_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/e752x_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/e752x_edac.c

## Purpose
This file implements PCI EDAC support for Intel e7520, e7525, e7320, and i3100 memory controllers. It decodes DRAM ECC errors and optional non-memory chipset errors from PCI configuration space, supports hardware scrub-rate configuration, and creates a generic EDAC PCI controller for broader PCI error reporting.

## Important APIs, Types, And Functions
`struct e752x_pvt` stores PCI devices for controller and error functions, memory remap registers, symmetric mapping state, row map data, map type, and device metadata. `struct e752x_error_info` snapshots global, hub/NSI, system-bus, memory-buffer, and DRAM first/next error registers plus logged addresses and syndromes.

Important functions include `e752x_probe1()`, `e752x_init_one()`, `e752x_remove_one()`, `e752x_get_devs()`, `e752x_init_csrows()`, `e752x_init_mem_map_table()`, `e752x_get_error_info()`, `e752x_process_error_info()`, `e752x_check()`, `do_process_ce()`, `do_process_ue()`, `set_sdram_scrub_rate()`, and `get_sdram_scrub_rate()`.

## Control Flow
Module init calls `opstate_init()` and registers a PCI driver. Probe enables the PCI device, checks whether error function 0:1 is hidden and optionally unhides it if `force_function_unhide` is set, determines channel mode, allocates a chip-select/channel EDAC topology, locates controller and error PCI devices, fills controller metadata and scrub callbacks, determines row mapping, initializes csrows from DRB/DRA/DRC/DDRCSR registers, loads TOLM/remap registers, registers the MC, enables error reporting masks/SMI settings, clears stale errors, and creates a generic PCI EDAC controller.

Polling `e752x_check()` snapshots and clears first/next global and subdomain registers in `e752x_get_error_info()`, then decodes them in `e752x_process_error_info()`. DRAM CE/UE reports include page, offset, syndrome, row, and channel when possible. Non-memory domains log warning text when `report_non_memory_errors` allows it, while DRAM always participates in reporting.

## State And Persistence
PCI config registers hold latched first/next error state and are cleared after readout. Private state caches PCI devices, remap boundaries, and row remap tables. Module parameters control hidden function access, EDAC op state, system-bus parity policy, and non-memory error logging. EDAC counters and DIMM metadata persist while the controller is registered.

## Dependencies And Integration Points
The driver depends on PCI IDs/config-space access, x86 CPU model text for sysbus parity auto-detection, EDAC MC APIs, EDAC PCI generic control APIs, and module parameters. It integrates with `/sys/devices/system/edac/mc` and EDAC PCI reporting.

## Risks
Unhiding device 0 function 1 can conflict with BIOS expectations, and the driver warns accordingly. Hardware address mapping includes several FIXME notes and special symmetric/remap handling, so row/channel attribution is risky on unusual configurations. Non-memory logging is controlled separately from EDAC memory reporting. The code assumes at most one controller instance by using MC index 0 and a single global `e752x_pci`.

## Test Signals
Signals include PCI probe for each supported ID, hidden function refusal/forced unhide behavior, csrow population from DRB boundaries, SECDED versus S4ECD4ED mode selection, scrub-rate set/get mapping for e752x and i3100 tables, stale error clearing, and CE/UE sysfs counter changes after induced PCI error bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/e752x_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/e7xxx_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/e7xxx_edac.c

## Purpose
This file implements PCI EDAC support for older Intel E7500, E7501, E7505, and E7205 memory controllers. It decodes DRAM first/next correctable and uncorrectable ECC log registers and exposes memory-controller reporting through the EDAC MC core.

## Important APIs, Types, And Functions
`struct e7xxx_pvt` stores the error-reporting bridge device and memory remap boundaries. `struct e7xxx_error_info` snapshots DRAM first/next error bits, CE log address/syndrome, and UE log address. Device metadata is stored in `e7xxx_devs[]`.

Primary functions are `e7xxx_probe1()`, `e7xxx_init_one()`, `e7xxx_remove_one()`, `e7xxx_init_csrows()`, `e7xxx_get_error_info()`, `e7xxx_process_error_info()`, `e7xxx_check()`, `process_ce()`, `process_ue()`, `process_ce_no_info()`, `process_ue_no_info()`, `e7xxx_find_channel()`, and `ctl_page_to_phys()`.

## Control Flow
Module init calls `opstate_init()` and registers a PCI driver. Probe reads DRC channel/granularity/configuration, allocates a chip-select/channel EDAC topology, finds the error-reporting function with `pci_get_device()`, fills metadata and page-remap callback, initializes csrows from DRB/DRA/DRC, reads TOLM/remap base/remap limit, clears stale error info, registers with EDAC, and creates a generic PCI EDAC controller.

During polling, `e7xxx_check()` snapshots DRAM first/next error registers. If CE or UE bits are set, the driver reads the associated log address and syndrome registers, clears the first/next bits with `pci_write_bits8()`, and reports CE/UE events. If both first and next entries contain the same class, only one address is available and the second report is emitted as no-info overflow.

## State And Persistence
PCI configuration registers hold latched error state and are cleared by polling. Private state caches bridge device and remap limits for `ctl_page_to_phys()`. EDAC stores row/channel/DIMM metadata and counters for the lifetime of the registered controller. A single global `e7xxx_pci` tracks the generic PCI control object.

## Dependencies And Integration Points
The driver depends on PCI config access, supported Intel PCI IDs, EDAC MC APIs, EDAC PCI generic control, and the module parameter `edac_op_state`. It integrates with EDAC polling or NMI mode as initialized by `opstate_init()`.

## Risks
The driver assumes at most one instance and hardcodes MC index 0. Address conversion has FIXME comments and uses legacy register-specific shifts. Channel detection from syndrome is heuristic. If first and next logs overflow, detailed location is unavailable for later events. The error-reporting PCI function must exist and be accessible.

## Test Signals
Tests should validate all PCI IDs, channel/granularity handling, csrow sizing, remap callback behavior, CE/UE log decoding, no-info overflow reporting, stale error clearing before registration, and generic PCI EDAC creation/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/e7xxx_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/ecs.c -->
# sources/distributed-fs/ceph-client/drivers/edac/ecs.c

## Purpose
This file implements the generic EDAC Error Check Scrub (ECS) sysfs descriptor builder. It is intended for on-die memory error-check scrub controls such as DDR5 ECS and creates per-FRU attribute groups that driver-specific ECS operations can service.

## Important APIs, Types, And Functions
`enum edac_ecs_attributes` defines `log_entry_type`, `mode`, `reset`, and `threshold`. `struct edac_ecs_dev_attr` wraps a `device_attribute` with a FRU id. `struct edac_ecs_fru_context` stores per-FRU name, attributes, attribute pointer array, and group. `struct edac_ecs_context` stores all FRU contexts.

Macro-generated show/store functions call `struct edac_ecs_ops` callbacks from `struct edac_dev_feat_ctx`. `ecs_attr_visible()` hides unsupported attributes or downgrades attributes to read-only when a getter exists without a setter. `edac_ecs_get_desc()` validates inputs and calls `ecs_create_desc()`.

## Control Flow
Consumers call `edac_ecs_get_desc(ecs_dev, attr_groups, num_media_frus)` while registering EDAC RAS features. The code allocates context with device-managed memory, allocates one FRU context per media FRU, initializes four attributes with the correct FRU id, initializes sysfs attributes, names each group `ecs_fruN`, attaches the attribute list and visibility callback, and stores each group into the caller-provided `attr_groups` array.

At sysfs access time, show functions find the FRU id from the attribute wrapper, look up ECS ops through device driver data, call the driver getter, and print the value. Store functions parse an unsigned long and call the corresponding setter or reset callback.

## State And Persistence
The file owns no hardware state. It allocates descriptor state with `devm_kzalloc()` and `devm_kcalloc()`, so it follows the client device lifetime. Actual ECS values are owned by the provider driver through `edac_ecs_ops` and its private context pointer.

## Dependencies And Integration Points
It depends on `linux/edac.h`, EDAC RAS feature context structures, sysfs attribute groups, and provider implementations of `edac_ecs_ops`. It is integrated by `edac_dev_register()` in `edac_device.c` when a feature entry has `RAS_FEAT_ECS`.

## Risks
The caller must provide enough `attr_groups` slots for all media FRUs; `edac_dev_register()` does this accounting. Store macros parse into `unsigned long` even when callbacks conceptually consume narrower values, so providers must validate ranges. Visibility is callback-based; missing ops silently hide files, which is intended but can obscure provider registration mistakes.

## Test Signals
Tests should cover invalid arguments, multiple FRUs, visibility with getter-only, setter-only, full read/write, and absent callbacks. Sysfs access tests should verify that the correct FRU id reaches each callback and that device-managed cleanup removes groups with the parent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/ecs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_device.c -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_device.c

## Purpose
This file implements the EDAC generic device core for non-memory-controller error domains such as caches, CPU interfaces, fabrics, DMA engines, and other ECC-capable blocks. It manages allocation, global registration, polling work, sysfs lifecycle, CE/UE counter propagation, and newer EDAC RAS feature device registration.

## Important APIs, Types, And Functions
Global state is `device_ctls_mutex` plus `edac_device_list`. Allocation and lifecycle APIs are `edac_device_alloc_ctl_info()`, `edac_device_free_ctl_info()`, `edac_device_add_device()`, `edac_device_del_device()`, and `edac_device_alloc_index()`. Error reporting APIs are `edac_device_handle_ce_count()` and `edac_device_handle_ue_count()`, with inline single-error wrappers declared in the header.

Polling is handled by `edac_device_workq_function()`, `edac_device_workq_setup()`, `edac_device_workq_teardown()`, and `edac_device_reset_delay_period()`. `edac_dev_register()` registers modern EDAC RAS feature devices with scrub, ECS, and memory-repair attribute groups.

## Control Flow
`edac_device_alloc_ctl_info()` allocates the controller, instances, blocks, optional private data, initializes names/counters/default logging, marks `OP_ALLOC`, and creates the main sysfs kobject. `edac_device_add_device()` locks the global list, inserts by unique `dev_idx`, records start time, creates sysfs instance/block hierarchy, and either starts delayed polling work or marks interrupt mode. `edac_device_del_device()` finds by parent device, marks offline, removes it from the RCU-protected list, tears down work, removes sysfs, and returns the control structure to the caller for freeing.

Error handlers validate instance/block indexes, update block, instance, and controller counters, log CE/UE messages according to per-device flags, and panic on UE if configured. `edac_dev_register()` builds an independent sysfs device under the EDAC bus for RAS feature controls by gathering attribute groups from scrub/ECS/mem-repair descriptor helpers.

## State And Persistence
The global list is protected by a mutex and RCU deletion synchronization. Each EDAC device keeps counters at block, instance, and controller levels. Poll scheduling state lives in `delayed_work`, `poll_msec`, and `delay`. Sysfs object lifetime is reference-counted through kobjects and module references. Feature devices store private provider context in `struct edac_dev_feat_ctx` and free it through a device release callback.

## Dependencies And Integration Points
The file depends on `edac_device.h`, `edac_module.h`, workqueue helpers, sysfs functions implemented in `edac_device_sysfs.c`, and RAS feature descriptor helpers such as `edac_scrub_get_desc()`, `edac_ecs_get_desc()`, and `edac_mem_repair_get_desc()`. Hardware drivers call its APIs to expose non-MC error domains.

## Risks
Index uniqueness is delegated to callers unless they use `edac_device_alloc_index()`. `edac_device_reset_delay_period()` does not reject zero even though the sysfs comment says nonzero, so invalid poll periods should be considered. Error reporting drops invalid instance/block events after logging an internal error. RAS feature registration has multi-stage allocation paths that must unwind correctly on descriptor failure.

## Test Signals
Tests should validate allocation/free under failures, duplicate `dev_idx` and duplicate device rejection, poll work start/stop, sysfs hierarchy creation/removal, CE/UE counter propagation, panic-on-UE configuration, RAS feature attr-group accounting, and RCU-safe removal while readers might traverse the list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_device.h -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_device.h

## Purpose
This header defines the public and internal data model for EDAC generic devices, which represent ECC/error-reporting blocks that are not memory controllers. It declares the allocation, registration, deletion, index allocation, and error reporting APIs used by low-level EDAC device drivers.

## Important APIs, Types, And Functions
Core types include `struct edac_device_counter`, `struct edac_dev_sysfs_attribute`, `struct edac_dev_sysfs_block_attribute`, `struct edac_device_block`, `struct edac_device_instance`, and `struct edac_device_ctl_info`. The hierarchy is controller -> instances -> blocks, with CE/UE counters at every level.

Public APIs are `edac_device_alloc_ctl_info()`, `edac_device_free_ctl_info()`, `edac_device_add_device()`, `edac_device_del_device()`, `edac_device_handle_ce_count()`, `edac_device_handle_ue_count()`, `edac_device_handle_ce()`, `edac_device_handle_ue()`, and `edac_device_alloc_index()`. The header also declares `edac_layer_name[]` and sysfs helper structures used by `edac_device_sysfs.c`.

## Control Flow
Low-level drivers allocate a populated `edac_device_ctl_info`, fill device/module/controller metadata and optionally `edac_check`, register it with `edac_device_add_device()`, report errors through handle helpers, unregister with `edac_device_del_device()`, and free with `edac_device_free_ctl_info()`. Inline wrappers convert single CE/UE reports into count-based calls.

## State And Persistence
`struct edac_device_ctl_info` contains list linkage, owner module, index, logging/panic flags, poll interval/delay, driver sysfs attributes, EDAC bus pointer, op state, delayed work, parent device pointer, names, private data, start time, instances/blocks, counters, and main kobject. Instances and blocks embed their own kobjects and counters.

## Dependencies And Integration Points
The header depends on Linux device, kobject, list, sysfs, workqueue, and EDAC types. It is included by EDAC core code and by hardware drivers such as Armada Aurora L2 and CPC925 CPU/HT-link support.

## Risks
The header exposes many fields for direct low-level driver mutation, so lifecycle ordering and field initialization are caller-sensitive. The `BLOCK_OFFSET_VALUE_OFF` sentinel casts `-1` to unsigned, which makes generated block names dependent on caller intent. The private free helper frees `pvt_info`, `blocks`, `instances`, and controller memory and should only be reached through the intended kobject/free path.

## Test Signals
Compile-time coverage should ensure drivers can allocate expected topologies. Runtime tests should check instance/block naming, counter hierarchy behavior, inline CE/UE wrappers, and safe free after sysfs unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_device_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_device_sysfs.c

## Purpose
This file implements sysfs exposure for EDAC generic devices. It creates the controller kobject, common controller attributes, symlink to the physical device, instance directories, block directories, and optional driver-supplied attributes.

## Important APIs, Types, And Functions
Controller attributes include `log_ue`, `log_ce`, `panic_on_ue`, and `poll_msec`. Instance and block attributes expose `ce_count` and `ue_count`. Key exported lifecycle functions are `edac_device_register_sysfs_main_kobj()`, `edac_device_unregister_sysfs_main_kobj()`, `edac_device_create_sysfs()`, and `edac_device_remove_sysfs()`.

Internal helpers include `edac_device_create_instance()`, `edac_device_delete_instance()`, `edac_device_create_block()`, `edac_device_delete_block()`, `edac_device_add_main_sysfs_attributes()`, and their removal counterparts. Kobject types provide release callbacks that drop references on the main controller object.

## Control Flow
Allocation calls `edac_device_register_sysfs_main_kobj()` to create the top-level `.../edac/<name>` kobject and hold a module reference. Registration then calls `edac_device_create_sysfs()`, which creates driver-supplied main attributes, creates the `device` symlink to the parent device, and recursively creates instance and block kobjects. Removal deletes main attributes, removes the symlink, and walks the instance/block tree releasing kobjects. Final controller release calls `__edac_device_free_ctl_info()`.

## State And Persistence
Sysfs state mirrors `struct edac_device_ctl_info`, its instance array, and block array. Store operations mutate live flags such as `log_ue`, `log_ce`, `panic_on_ue`, and polling delay. Kobject reference counts tie child instance/block lifetime to the controller's main kobject and module reference.

## Dependencies And Integration Points
The file depends on `edac_device.h`, `edac_module.h`, sysfs/kobject APIs, and the EDAC bus returned by `edac_get_sysfs_subsys()`. It is invoked by `edac_device.c`; low-level drivers indirectly use it through EDAC device registration APIs.

## Risks
The `poll_msec` store path uses `simple_strtoul()` and does not enforce the comment's nonzero minimum. Partial sysfs creation paths must unwind child kobjects and attributes in order; the code does this but is sensitive to future changes. Driver-supplied block attributes are manually created and removed, so invalid attr arrays can break registration.

## Test Signals
Signals include correct top-level kobject creation, module reference release, common attribute read/write behavior, `device` symlink existence, instance/block count files, optional driver attributes, recursive cleanup on mid-creation failures, and poll delay changes reaching `edac_device_reset_delay_period()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_device_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_mc.c -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_mc.c

## Purpose
This file implements the EDAC memory-controller core. It allocates and frees `mem_ctl_info` topologies, manages the global memory-controller list and owner arbitration, schedules polling, maps errors to DIMMs/csrows, increments counters, emits logs and RAS trace events, and performs optional software scrubbing for correctable errors.

## Important APIs, Types, And Functions
Global state includes exported `edac_op_state`, `mem_ctls_mutex`, `mc_devices`, and `edac_mc_owner`. Allocation/lifecycle APIs are `edac_mc_alloc()`, `edac_mc_free()`, `edac_mc_add_mc_with_groups()`, `edac_mc_del_mc()`, `edac_has_mcs()`, `find_mci_by_dev()`, and `edac_mc_find()`. Error APIs are `edac_mc_handle_error()` and `edac_raw_mc_handle_error()`.

Internal support functions allocate csrow/channel structures (`edac_mc_alloc_csrows()`), allocate DIMMs (`edac_mc_alloc_dimms()`), run polling work (`edac_mc_workq_function()`), reset poll delay (`edac_mc_reset_delay_period()`), find csrow by page (`edac_mc_find_csrow_by_page()`), increment counters, print/log CE/UE events, and scrub memory (`edac_mc_scrub_block()`).

## Control Flow
Low-level MC drivers call `edac_mc_alloc()` with a layer topology. The core computes total DIMMs, virtual csrows, channels, initializes a `struct device`, allocates private data, csrows, channels, and DIMMs, links DIMMs to legacy csrow/channel objects, and returns an `OP_ALLOC` controller. `edac_mc_add_mc_with_groups()` enforces single-owner policy, inserts into the global list, creates sysfs, starts polling work if `mci->edac_check` exists, or marks interrupt mode otherwise. `edac_mc_del_mc()` marks offline, removes from the list, clears owner when last MC is removed, stops work, and removes sysfs.

`edac_mc_handle_error()` normalizes driver-supplied layer coordinates, finds matching DIMMs, builds label and location strings, derives a maximum grain, increments legacy csrow/channel counters, and delegates to `edac_raw_mc_handle_error()`. The raw handler emits a RAS trace event and then logs/increments CE or UE paths. CE handling optionally maps controller pages to CPU physical pages and scrubs the affected block for `SCRUB_SW_SRC`.

## State And Persistence
The global MC list is mutex-protected and RCU-synchronized on deletion. `edac_mc_owner` prevents concurrent ownership by incompatible modules such as GHES and chipset-specific drivers. `mem_ctl_info` owns topology, counters, error descriptor buffer, sysfs device, delayed work, and private data. `edac_raw_error_desc` inside `mci` is reused for each report, which is why interrupt drivers with concurrent paths may need external locking.

## Dependencies And Integration Points
The file depends on EDAC public types, EDAC sysfs helpers, EDAC workqueue helpers, RAS tracepoints, kmap/highmem helpers, optional architecture atomic scrub support, and `edac_module.h`. Every memory-controller driver in this subset integrates through this file's allocation, registration, and reporting APIs.

## Risks
`edac_has_mcs()` returns the inverse of `list_empty()` but uses a local named `ret`, which can confuse readers. The owner check compares string pointers (`edac_mc_owner != mci->mod_name`), so low-level drivers must use stable module-name pointers. `mci->error_desc` is shared mutable state; concurrent interrupt handlers need serialization. Layer coordinates outside configured bounds are corrected to unknown but still reported, preventing crashes at the cost of precision.

## Test Signals
Tests should cover topology allocation for virtual and non-virtual csrows, allocation failure unwind, duplicate MC index/device rejection, owner arbitration, polling start/stop, sysfs creation/removal, layer-coordinate validation, multi-label DIMM matching, no-info counters, CE software scrub invocation, UE panic configuration, and RAS trace emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_mc.h -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_mc.h

## Purpose
This header declares the EDAC memory-controller core API and common logging/debug helpers used by low-level EDAC drivers. It defines page/MiB conversion macros, EDAC printk macros, debug logging, PCI ID convenience macros, `to_mci()`, and all exported MC lifecycle and error-reporting function prototypes.

## Important APIs, Types, And Functions
Important declarations include `edac_mc_alloc()`, `edac_mc_free()`, `edac_get_owner()`, `edac_mc_add_mc_with_groups()`, `edac_mc_add_mc()`, `edac_has_mcs()`, `edac_mc_find()`, `find_mci_by_dev()`, `edac_mc_del_mc()`, `edac_mc_find_csrow_by_page()`, `edac_raw_mc_handle_error()`, `edac_mc_handle_error()`, and `edac_op_state_to_string()`.

The header also declares `edac_mem_types[]`, `edac_debug_level`, and the shared `edac_layer_name[]` indirectly used by debugfs and error formatting.

## Control Flow
Low-level drivers include this header to allocate a `mem_ctl_info`, register it, optionally provide polling and scrub callbacks, report errors with layer coordinates, and unregister/free on remove. The `edac_mc_add_mc()` macro uses the grouped variant with no extra sysfs attribute groups.

## State And Persistence
The header itself owns no runtime state but exposes access to global EDAC state through extern declarations and macros. It codifies that `struct mem_ctl_info` embeds a `struct device` addressable by `to_mci()`.

## Dependencies And Integration Points
It depends on kernel module, PCI, platform, time, NMI, RCU, completion, kobject, workqueue, and EDAC headers. It is the central integration point between hardware EDAC drivers and the MC core in `edac_mc.c` and `edac_mc_sysfs.c`.

## Risks
Logging macros use raw `printk()` formatting and require valid `mci`/controller pointers. `edac_dbg()` compiles away when debug is disabled, so side effects must not be placed in its arguments. The API allows drivers to supply arbitrary layer indexes to `edac_mc_handle_error()`, relying on runtime validation in the core.

## Test Signals
Compile coverage is the main signal for this header. Runtime validation comes from all low-level MC drivers successfully allocating, adding, reporting errors, exposing sysfs, and deleting controllers through the declared APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_mc_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/edac/edac_mc_sysfs.c

## Purpose
This file implements sysfs support for EDAC memory controllers and DIMM/rank devices. It exposes global module parameters, per-DIMM metadata/counters, per-controller counters, reset controls, optional scrub-rate controls, and the parent `mc` device under the EDAC bus.

## Important APIs, Types, And Functions
Global tunables are `edac_mc_log_ue`, `edac_mc_log_ce`, `edac_mc_panic_on_ue`, and `edac_mc_poll_msec`, with getters `edac_mc_get_log_ue()`, `edac_mc_get_log_ce()`, `edac_mc_get_panic_on_ue()`, and `edac_mc_get_poll_msec()`. `edac_set_poll_msec()` validates new polling intervals and calls `edac_mc_reset_delay_period()`.

DIMM helpers include `edac_create_dimm_object()`, label/location/size/type/mode/count show functions, and label store. MC helpers include `edac_create_sysfs_mci_device()`, `edac_remove_sysfs_mci_device()`, `edac_mc_sysfs_init()`, and `edac_mc_sysfs_exit()`.

## Control Flow
EDAC module initialization calls `edac_mc_sysfs_init()`, which creates the parent `mc` device on the EDAC bus. When a controller is registered, `edac_create_sysfs_mci_device()` configures `mci->dev` as `mcN`, attaches optional driver groups, adds the device, creates populated DIMM/rank child devices, and creates debugfs nodes. Removal unregisters debugfs, unregisters DIMM devices, and deletes the MC device. Module exit unregisters the parent `mc` device.

Sysfs reads format live EDAC state such as DIMM labels, locations, memory type, device width, EDAC mode, CE/UE counts, controller size, no-info counters, max location, and seconds since reset. `reset_counters` clears controller, csrow/channel, and DIMM counters. `sdram_scrub_rate` appears only when driver callbacks exist and delegates set/get operations to the low-level MC driver.

## State And Persistence
Global module parameters persist for the EDAC module lifetime and affect logging, panic behavior, and polling interval. Per-DIMM labels are mutable through sysfs and persist while the DIMM object exists. Counter reset changes live in-memory EDAC counters only. The `mci_pdev` parent device persists from EDAC sysfs init to exit.

## Dependencies And Integration Points
The file depends on EDAC MC core structures, the EDAC bus, Linux device/sysfs APIs, runtime PM calls, and debugfs creation. Low-level drivers indirectly use this file when they call `edac_mc_add_mc()` and expose optional scrub callbacks.

## Risks
`edac_set_poll_msec()` rejects intervals under 1000 ms, while generic EDAC device sysfs has looser behavior, so MC and device polling policies differ. `dimmdev_label_store()` rejects empty or oversized labels but allows arbitrary non-newline bytes copied from sysfs input. Only populated DIMMs are exposed as child devices, so missing expected DIMM nodes may mean zero `nr_pages` rather than allocation failure.

## Test Signals
Signals include module parameter read/write behavior, poll-period reset for active controllers, MC device creation under the EDAC bus, child DIMM/rank creation only for populated DIMMs, label store validation, reset counter coverage, conditional scrub-rate permissions, debugfs node creation/removal, and clean parent `mc` unregister at exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/edac_mc_sysfs.c -->
