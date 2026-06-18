# subset-b-001274 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mem_repair.c -->
# sources/distributed-fs/ceph-client/drivers/edac/mem_repair.c

## Purpose
Provides the generic EDAC memory-repair sysfs descriptor builder for RAS feature devices. It exposes a uniform set of attributes for repair technologies such as post-package repair, cacheline sparing, row/bank/rank sparing, address selection, DRAM location fields, and the write-only repair trigger.

## Important APIs, Types, And Functions
- `edac_repair_type[]` maps `enum edac_repair_type` values to stable strings and is exported for provider drivers.
- `struct edac_mem_repair_context` owns one named sysfs group, per-attribute `device_attribute` wrappers, and the attribute pointer array.
- `MR_ATTR_SHOW`, `MR_ATTR_STORE`, and `MR_DO_OP` generate the boilerplate show/store handlers that dispatch through `struct edac_mem_repair_ops`.
- `mem_repair_attr_visible` dynamically hides unsupported attributes or downgrades them to read-only when only the getter exists.
- `edac_mem_repair_get_desc` is the public descriptor API used by EDAC feature clients.

## Control Flow
A client calls `edac_mem_repair_get_desc(dev, attr_groups, instance)`. The helper validates inputs, allocates a devm-managed context, clones the static attribute templates, stamps each wrapper with the feature instance, initializes sysfs attributes, and publishes a group named `mem_repairN`. Runtime sysfs reads and writes recover the instance from the wrapper, fetch `edac_dev_feat_ctx` from the RAS feature device, select `ctx->mem_repair[inst]`, and call the provider's callback with the parent device plus provider-private data. The visibility callback runs before sysfs exposure and only returns a mode for callbacks present in the provider ops table.

## State And Persistence
State is devm-managed and persists for the lifetime of the client device. The file does not store repair parameters itself; it forwards all state to provider callbacks. The only exported static state is `edac_repair_type[]`. Attribute values, persistence mode, selected HPA/DPA, DRAM fields, and repair execution state live in the hardware/provider private data.

## Dependencies And Integration Points
Depends on `linux/edac.h`, `struct edac_dev_feat_ctx`, and `struct edac_mem_repair_ops`. It integrates with EDAC RAS feature devices through sysfs attribute groups and expects the RAS feature device's driver data to point at the feature context. Providers decide which attributes are meaningful by filling the getter/setter/do callbacks.

## Risks And Edge Cases
The generated handlers assume visible attributes always have the callback they call; visibility and ops setup must remain consistent. Numeric stores use base autodetection and perform no range checking beyond conversion, so providers must validate addresses, masks, channels, ranks, rows, and policy values. `sprintf(ctx->name, "mem_repair%d", instance)` relies on `EDAC_FEAT_NAME_LEN` being large enough. The write-only `repair` attribute passes the parsed integer directly to `do_repair`, so provider semantics for trigger values must be documented elsewhere.

## Test Signals
Useful tests instantiate providers with full, read-only, and sparse ops tables; verify only supported sysfs files appear with correct permissions; write invalid and out-of-range numeric values; confirm callback errors propagate as sysfs errors; and exercise multiple instances so each file dispatches to the correct `ctx->mem_repair[inst]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mem_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mpc85xx_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/mpc85xx_edac.c

## Purpose
Implements EDAC support for Freescale/NXP MPC85xx and QorIQ memory-controller families. The file registers three related platform drivers: the shared FSL DDR memory-controller EDAC driver, an MPC85xx L2-cache ECC device, and, when PCI is enabled, a PCI/PCIe error-reporting EDAC device.

## Important APIs, Types, And Functions
- `mpc85xx_pci_err_probe` and `mpc85xx_pci_err_remove` allocate `edac_pci_ctl_info`, map PCI error registers, configure capture/enable registers, and optionally request the PCI error IRQ.
- `mpc85xx_pci_check`, `mpc85xx_pcie_check`, and `mpc85xx_pci_isr` decode and clear PCI or PCIe error status before reporting parity or non-parity errors to EDAC.
- `mpc85xx_l2_err_probe` and `mpc85xx_l2_err_remove` allocate `edac_device_ctl_info`, map L2 error registers, install injection sysfs files, and enable polling or interrupt handling.
- `mpc85xx_l2_check` and `mpc85xx_l2_isr` report single-bit L2 ECC errors as CE and configuration/multibit/tag parity errors as UE.
- `mpc85xx_mc_init` registers the memory-controller, L2, and PCI platform drivers as one module.

## Control Flow
Module initialization normalizes `edac_op_state` to polling or interrupt mode and calls `platform_register_drivers`. The memory-controller driver delegates probe/remove to `fsl_mc_err_probe` and `fsl_mc_err_remove`. The L2 probe opens a devres group, allocates one EDAC device with CPU/L blocks, maps the controller's error window at resource offset `0xe00`, clears pending status, saves `ERRDIS`, enables detection, attaches injection attributes, adds the EDAC device, and requests the IRQ in interrupt mode. L2 checking reads `ERRDET`, dumps captured registers, writes back the detect bits to clear them, and calls CE/UE helpers. The PCI probe follows the same pattern for `edac_pci_ctl_info`, detects PCIe capability, programs PCI or PCIe capture masks, clears status, adds the EDAC PCI device, then either polls or handles shared interrupts.

## State And Persistence
Persistent module state includes allocation indexes and saved hardware registers: `orig_l2_err_disable`, `orig_pci_err_cap_dr`, and `orig_pci_err_en`. Per-device state is held in `struct mpc85xx_l2_pdata` and `struct mpc85xx_pci_pdata`, including mapped register bases, IRQs, EDAC index, and PCIe mode. Remove paths restore saved disable/capture/enable values, dispose IRQ mappings, and free EDAC control structures.

## Dependencies And Integration Points
Depends on Open Firmware resources and IRQs, big-endian MMIO accessors, EDAC core device/PCI APIs, PCI host bridge capability helpers, and shared Freescale DDR EDAC support from `fsl_ddr_edac.h`. Device matching is by OF compatible strings for memory/L2 controllers and by platform device ID for PCI error reporting.

## Risks And Edge Cases
The PCI saved-register variables are module-global, so multiple PCI error devices could overwrite restore state. The probe path uses both devres groups and manual EDAC freeing; error ordering must remain correct to avoid leaked control info. Master aborts are intentionally ignored for PCI config cycles, and PCIe invalid config accesses are masked to avoid noisy boot logs. Injection sysfs stores use `simple_strtoul` guarded only by `isdigit(*data)`, so malformed values can silently no-op.

## Test Signals
Tests should cover poll and interrupt modes, L2 CE/UE bit combinations, PCI parity versus non-parity classification, PCIe capture reset behavior, resource/IRQ acquisition failures, restore of original hardware masks after unload, and visibility/behavior of `inject_data_hi`, `inject_data_lo`, and `inject_ctrl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mpc85xx_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mpc85xx_edac.h -->
# sources/distributed-fs/ceph-client/drivers/edac/mpc85xx_edac.h

## Purpose
Defines the MPC85xx EDAC register offsets, bit masks, logging wrapper, and private data structures shared by the MPC85xx EDAC implementation. It is the hardware contract for the L2-cache and PCI/PCIe error paths in `mpc85xx_edac.c`.

## Important APIs, Types, And Functions
- `MPC85XX_L2_*` offsets identify L2 injection, capture, detect, disable, interrupt-enable, attribute, address, and control registers.
- `L2_EIE_*` and `L2_EDE_*` masks define interrupt-enable bits and CE/UE classification for L2 errors.
- `PCI_EDE_*` masks classify PCI error detect bits, including parity masks and multi-error status.
- `MPC85XX_PCI_*` offsets describe PCI/PCIe error detect, capture, enable, attribute, address, data, timer, and capability capture registers.
- `struct mpc85xx_l2_pdata` and `struct mpc85xx_pci_pdata` hold EDAC-private per-device state.

## Control Flow
The header has no executable control flow. Its constants are consumed during probe to map and program hardware registers, during check/ISR paths to classify errors, and during remove to restore original masks.

## State And Persistence
No state is stored in the header. The declared private structures persist inside EDAC control blocks allocated by the driver and carry mapped base addresses, IRQs, device names, indexes, and PCIe-vs-PCI mode.

## Dependencies And Integration Points
Integrated tightly with `mpc85xx_edac.c`, the EDAC core, and Freescale hardware register layouts. The bit definitions are used with big-endian MMIO accessors and OF-provided resources.

## Risks And Edge Cases
Incorrect masks directly affect whether hardware errors are reported as CE, UE, parity, or non-parity. The header groups L2 configuration, multibit, and tag parity under UE; if hardware semantics differ by SoC revision, the C driver will inherit that classification. The structures store raw `void __iomem *` bases and IRQ integers, so lifetime is controlled entirely by the probe/remove implementation.

## Test Signals
Compile coverage with and without `CONFIG_PCI`, static checks that register offsets match the hardware manual, and runtime tests that injected L2 and PCI status bits map to the expected EDAC handler calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/mpc85xx_edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/npcm_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/npcm_edac.c

## Purpose
Provides EDAC memory-controller support for Nuvoton NPCM7xx and NPCM8xx SoCs. It reports correctable and uncorrectable DDR ECC interrupts, exposes NPCM8xx debugfs error injection when EDAC debug is enabled, and handles chip-specific register offsets through platform data.

## Important APIs, Types, And Functions
- `struct npcm_platform_data` captures per-chip register offsets, masks, and shifts.
- `struct priv_data` stores the MMIO base, platform data, message buffer, debugfs root, and injection settings.
- `handle_ce` and `handle_ue` read captured address/data/source/syndrome registers and call `edac_mc_handle_error`.
- `edac_ecc_isr` dispatches CE or UE status and acknowledges the matching interrupt.
- `force_ecc_error` writes syndrome injection controls on NPCM8xx and triggers a forced write check.
- `edac_probe` maps registers, initializes the regmap, validates ECC enablement, allocates the EDAC MC, requests IRQ, and registers with the EDAC core.

## Control Flow
Probe maps the memory-controller resource, creates a 32-bit regmap, obtains OF match data, and rejects hardware with ECC disabled. It forces interrupt mode, allocates a single all-memory EDAC layer, fills EDAC capabilities, requests the ECC IRQ, unmasks ECC events, adds the memory controller, and optionally creates debugfs injection files for NPCM8xx. Interrupt handling reads `ctl_int_status`; CE has priority over UE in the `if/else` chain, and each handled interrupt reads captured metadata, reports one event, writes the matching ACK mask, and returns `IRQ_HANDLED`.

## State And Persistence
`npcm_regmap` is a file-scope pointer initialized per probed device. Per-controller state is in `priv_data` attached to `mci->pvt_info`. Hardware interrupt masks and ECC enable bits persist in controller registers; remove deletes debugfs and EDAC MC state, masks master interrupts globally, and clears ECC enable bits.

## Dependencies And Integration Points
Depends on OF match data, platform IRQ resources, MMIO regmap, EDAC MC APIs, EDAC debugfs helpers, and Nuvoton memory-controller register layouts. It integrates with the EDAC core as a `mem_ctl_info` driver with DDR4 and SECDED capability.

## Risks And Edge Cases
The global `npcm_regmap` makes multiple simultaneous controllers unsafe unless the platform has only one instance. The ISR handles CE before UE and does not process both if both status bits are set. Remove disables ECC, which is a strong hardware policy decision. Injection accepts debugfs byte values and performs range checks only inside `force_ecc_error`; invalid requests return `count` after logging rather than an error.

## Test Signals
Exercise NPCM750 and NPCM845 OF matches, ECC-disabled probe rejection, CE and UE interrupts with captured high/low address fields, simultaneous CE/UE status behavior, interrupt masking after setup/remove, and debugfs injection for data and checkcode CE plus UE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/npcm_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-l2c.c -->
# sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-l2c.c

## Purpose
Implements EDAC device support for Cavium Octeon secondary cache ECC. It polls Octeon I tag/data error CSRs and Octeon II per-TAD L2C tag/data/VBF error CSRs, reports CE/UE events, and clears handled hardware bits.

## Important APIs, Types, And Functions
- `octeon_l2c_poll_oct1` handles Octeon I `CVMX_L2T_ERR` and `CVMX_L2D_ERR`.
- `_octeon_l2c_poll_oct2` decodes one Octeon II TAD's `ERR_TDTX` and `ERR_TTGX` registers.
- `octeon_l2c_poll_oct2` iterates all EDAC instances/TADs.
- `octeon_l2c_probe` allocates the EDAC device, chooses the polling function by CPU model, disables Octeon I L2 interrupts, and registers with EDAC.

## Control Flow
The platform probe allocates an EDAC device with one or four TAD instances and two blocks, tag and data. On Octeon I, it disables single/double-error interrupt enable bits because the driver polls and assigns `octeon_l2c_poll_oct1`; otherwise it assigns the Octeon II polling function. Polling reads status registers, builds short diagnostic strings for syndrome/type/way, calls CE handlers for single-bit errors and UE handlers for double-bit errors, then writes a reset mask back to the CSR to re-arm only bits that were seen.

## State And Persistence
No custom private state is stored. EDAC control state persists in `edac_device_ctl_info`, and hardware error state lives in Octeon CSRs until cleared by the poll path. Remove deletes the EDAC device and frees the control info.

## Dependencies And Integration Points
Depends on Octeon model macros, CVMX CSR definitions, EDAC device APIs, and the platform driver named `octeon_l2c_edac`. It integrates as a polling EDAC device rather than an IRQ-driven driver.

## Risks And Edge Cases
The Octeon I path writes `l2d_err` back through `CVMX_L2T_ERR`, which is suspicious and should be checked against upstream or hardware expectations. Polling frequency determines detection latency. Octeon II diagnostic strings are fixed-size and could truncate details if fields grow. A failed `edac_device_add_device` returns `-ENXIO` after freeing state.

## Test Signals
Inject or emulate tag/data SEC/DED bits on Octeon I, TDTX/TTGX SBE/DBE/VBF bits on Octeon II, confirm only observed bits are cleared, verify TAD count on CN68XX, and unload/reload without EDAC device leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-l2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-lmc.c -->
# sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-lmc.c

## Purpose
Provides EDAC memory-controller support for Cavium Octeon LMC DRAM controllers. It polls controller ECC status, reports DIMM/rank/bank/row/column information, and exposes sysfs injection controls for software-driven decode/reporting tests.

## Important APIs, Types, And Functions
- `struct octeon_lmc_pvt` stores injection state and synthetic DIMM address fields.
- `octeon_lmc_edac_poll` handles Octeon I `MEM_CFG0` SEC/DED status and `FADR` capture.
- `octeon_lmc_edac_poll_o2` handles Octeon II `LMCX_INT`, supports synthetic injection, and clears or resets status.
- `TEMPLATE_SHOW` and `TEMPLATE_STORE` generate sysfs controls for injection and address fields.
- `octeon_lmc_edac_probe` checks ECC enablement, allocates the EDAC MC, registers sysfs groups, and disables hardware ECC interrupts because polling is used.

## Control Flow
Probe calls `opstate_init`, builds a one-channel EDAC topology, and branches by Octeon generation. If ECC is disabled, it logs and returns success without registering EDAC. Otherwise it allocates `mem_ctl_info` with private injection state, fills names, chooses the poll function, registers with `edac_mc_add_mc_with_groups`, disables hardware SEC/DED interrupts, and saves the MCI in platform data. The poll path reads hardware or synthetic status, builds an address message from `FADR` fields or sysfs-provided values, reports CE/UE, then clears the hardware interrupt bits or resets `pvt->inject`.

## State And Persistence
Persistent state includes the EDAC MC object and `octeon_lmc_pvt` injection fields. Hardware capture/status registers persist until the poll function writes them back with re-arm bits. Sysfs attribute values persist in memory only for the life of the EDAC MC.

## Dependencies And Integration Points
Depends on Octeon CSR definitions, EDAC MC APIs, generated device attribute groups, and platform devices named `octeon_lmc_edac`. It integrates with EDAC as a memory-controller driver with polling, not interrupts.

## Risks And Edge Cases
The Octeon II interrupt-disable block reads `CVMX_LMCX_MEM_CFG0` into a `union cvmx_lmcx_int_en`, which deserves hardware-layout scrutiny. Sysfs injection stores accept numeric strings only when the first byte is a digit and otherwise return zero. The driver reports unknown page/offset/syndrome and uses the decoded location in the message, so consumers relying on normalized EDAC coordinates get limited data.

## Test Signals
Check ECC-disabled platforms return without registering, Octeon I and II CE/UE polling paths, sysfs injection of single and double errors with selected DIMM/rank/bank/row/col, status clearing/re-arming, and EDAC MC teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-lmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-pc.c -->
# sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-pc.c

## Purpose
Registers an EDAC device for Octeon primary instruction and data cache errors. It receives cache-error notifications from architecture code, reads CP0 cache error registers, reports I-cache and D-cache CE/UE events, and clears the hardware error indication.

## Important APIs, Types, And Functions
- `struct co_cache_error` owns a notifier block and EDAC device pointer.
- `co_cache_error_event` is the notifier callback for recoverable and unrecoverable cache errors.
- `co_cache_error_probe` allocates the EDAC device with one CPU instance per possible CPU and two cache blocks.
- `co_cache_error_remove` unregisters the notifier and frees EDAC state.

## Control Flow
Probe allocates private state with devm, sets the notifier callback, allocates an EDAC device named `octeon-cpu`/`cache`, registers it with the EDAC core, and then registers the architecture cache-error notifier. When notified, the callback reads the I-cache error register and either reads the D-cache error register or consumes the saved unrecoverable D-cache error from `cache_err_dcache[core]`. It logs raw register data and error EPC, reports I-cache errors as CE, reports D-cache errors as CE or UE based on the notifier event, and clears CP0 cache error registers.

## State And Persistence
Driver state persists in `co_cache_error` and the EDAC control object. It also depends on external per-core `cache_err_dcache[]` state for unrecoverable D-cache events. Hardware CP0 error state is cleared in the notifier callback.

## Dependencies And Integration Points
Depends on Octeon architecture notifier registration functions, CP0 cache error accessors, `cache_err_dcache`, SMP CPU/core identification, and EDAC device APIs. It is registered as the `octeon_pc_edac` platform driver.

## Risks And Edge Cases
The callback returns `NOTIFY_STOP`, so notifier ordering matters. It maps I-cache errors only to CE even when the event is unrecoverable, while D-cache uses the event to choose UE. Correct indexing assumes `cvmx_get_core_num()` aligns with `cache_err_dcache[]`. Remove must unregister the notifier before freeing the EDAC device to avoid callbacks into freed memory.

## Test Signals
Trigger recoverable and unrecoverable D-cache notifications, I-cache error register bits, Octeon II D-cache clear semantics, multi-CPU instance indexing, and notifier unregister on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-pc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-pci.c -->
# sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-pci.c

## Purpose
Implements polling EDAC PCI error reporting for Cavium Octeon PCI controllers. It reads the PCI status/config CSR, maps parity and abort/system-error bits to EDAC PCI events, and clears handled bits.

## Important APIs, Types, And Functions
- `octeon_pci_poll` reads `CVMX_NPI_PCI_CFG01`, reports detected parity errors with `edac_pci_handle_pe`, reports non-parity system/abort/parity-master conditions with `edac_pci_handle_npe`, and writes set bits back to clear them.
- `octeon_pci_probe` allocates and registers `edac_pci_ctl_info`.
- `octeon_pci_remove` unregisters and frees EDAC PCI state.

## Control Flow
The platform probe allocates a zero-private EDAC PCI control object, attaches device names and `octeon_pci_poll`, and adds it to the EDAC core. Polling reads `CFG01`, tests each error bit independently, reports the matching EDAC event, sets that status bit to one, and writes the register back after each handled condition.

## State And Persistence
No private driver state is stored beyond the EDAC PCI control object. Hardware error bits persist in `CVMX_NPI_PCI_CFG01` until cleared by the poll function.

## Dependencies And Integration Points
Depends on Octeon NPI/PCI CSR helpers and EDAC PCI APIs. The platform driver name is `octeon_pci_edac`, and operation is polling-only.

## Risks And Edge Cases
Writing the register after each bit can race with newly arriving bits depending on hardware write-one-to-clear semantics. Probe initializes `res` to zero and returns it on `edac_pci_add_device` failure, which can report success after a failed add unless the EDAC core failure path is interpreted elsewhere. There is no interrupt support.

## Test Signals
Exercise DPE, SSE, RMA, RTA, STA, and MDPE bits; verify correct CE/non-parity EDAC counters and clear behavior; test add-device failure return handling; and ensure remove deletes the EDAC PCI device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/pasemi_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/pasemi_edac.c

## Purpose
Implements EDAC memory-controller support for PA Semi PWRficient on-chip memory controllers. It probes the controller via PCI, enables ECC error logging/correction bits, builds csrow/channel DIMM geometry, polls error status, and reports SBE/MBE/rank-fail events.

## Important APIs, Types, And Functions
- `pasemi_edac_get_error_info` reads and clears `MCDEBUG_ERRSTA`, and clears SBE overflow through `MCDEBUG_ERRCNT1`.
- `pasemi_edac_process_error_info` reads `MCDEBUG_ERRLOG1A`, extracts chip-select, and reports CE or UE through EDAC.
- `pasemi_edac_check` is the polling callback.
- `pasemi_edac_init_csrows` reads rank configuration registers and fills EDAC csrow/dimm metadata.
- `pasemi_edac_probe` enables logging/correction, allocates `mem_ctl_info`, computes capabilities, initializes rows, clears old status, and registers the MC.

## Control Flow
PCI probe first verifies `MCCFG_MCEN_MMC_EN`. It enables SBE, MBE, and rank-fail logging, creates a two-layer chip-select/channel EDAC topology, reads ECC correction and scrub configuration, fills EDAC capability fields, and initializes present rank sizes from `MCDRAM_RANKCFG`. After clearing stale status, it adds the MC to the EDAC core. Periodic checks read pending status, clear it, decode the chip-select from the error log, and report UE for MBE/rank-fail and CE for SBE.

## State And Persistence
`last_page_in_mmc` and `system_mmc_id` are global counters used while probing controllers. Per-controller state is held in the EDAC MC object; there is no custom private data. Hardware logging/correction/scrub bits persist in PCI config space and are not restored by remove.

## Dependencies And Integration Points
Depends on PCI config access, PA Semi PCI IDs, EDAC MC APIs, and EDAC polling/NMI opstate initialization. It registers as a `pci_driver` for vendor PA Semi device `0xa00a`.

## Risks And Edge Cases
`last_page_in_mmc` is global and monotonically accumulates across controllers, so remove/reprobe or unusual multi-controller ordering can affect page ranges. The driver enables ECC correction/logging without saving previous register state. Only one channel per csrow is modeled. Unknown rank sizes abort probe, and error reporting uses the first page of the chip-select rather than precise captured address data.

## Test Signals
Probe with controller disabled/enabled, each rank size encoding, SECDED versus EC capability bits, scrub flag combinations, SBE overflow clearing, MBE and rank-fail UE reporting, and remove after failed or successful EDAC registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/pasemi_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.c

## Purpose
Implements EDAC support for Intel Atom SoCs using the Pondicherry2 memory controller, covering Apollo Lake and Denverton. It decodes machine-check memory errors from system physical addresses into channel, DIMM, rank, bank, row, and column by reading memory-controller topology registers and registering an MCE decode notifier.

## Important APIs, Types, And Functions
- `struct dunit_ops` abstracts Apollo Lake versus Denverton register access, ECC checks, DIMM discovery, and PMI-to-DRAM decode.
- `_apl_rd_reg`, `apl_rd_reg`, and `dnv_rd_reg` read controller registers through hidden P2SB sideband or MMIO/config-space paths.
- `get_registers` reads static memory layout registers and derives asymmetric, symmetric, MOT, slice, channel, and hash state.
- `sys2pmi` performs first-stage system-address to PMI channel/address translation, including MMIO gap removal and interleave bit removal.
- `apl_pmi2mem` and `dnv_pmi2mem` perform second-stage PMI address to DRAM location decode.
- `pnd2_mce_check_error` filters MCEs, and `pnd2_mce_output_error` reports decoded events through EDAC.
- `pnd2_register_mci`, `pnd2_init`, and `pnd2_exit` manage EDAC MC and MCE notifier lifetime.

## Control Flow
Initialization rejects GHES ownership, other EDAC owners, hypervisors, and unsupported CPU models. It selects `apl_ops` or `dnv_ops`, initializes opstate, reads topology registers, checks ECC is active, registers one EDAC MC, registers the MCE decode notifier, and optionally creates debugfs decode-test files. On an MCE, the notifier ignores already handled and non-memory errors, logs raw machine-check metadata, then calls the output routine. The output routine classifies corrected/uncorrected/fatal status, requires a valid address, calls `get_memory_error_data`, and reports the decoded channel/DIMM/rank/row/bank/column or a decode failure message.

## State And Persistence
The driver uses substantial file-scope topology state: TOLUD/TOUUD-derived `top_lm`/`top_hm`, region descriptors `mot`, `as0`, `as1`, `as2`, channel masks, selectors, hash masks, and cached Apollo Lake/Denverton register structures. `pnd2_mci` is the active EDAC controller. Debugfs state stores a fake address and last decode result. Hardware topology is read once at probe and assumed stable.

## Dependencies And Integration Points
Depends on x86 CPU matching, MCE notifier chain, EDAC MC APIs, GHES/EDAC ownership arbitration, PCI config access, P2SB sideband helpers, MMIO mapping, and register bitfield definitions from `pnd2_edac.h`. It integrates with the kernel MCE path by marking handled memory errors with `MCE_HANDLED_EDAC`.

## Risks And Edge Cases
Address decode is sensitive to firmware-provided interleave registers, MOT masks, asymmetric regions, hash masks, and DIMM geometry tables. Apollo Lake P2SB access temporarily unhides a hidden PCI device and must restore hide state. Register and topology state is global, so multiple controllers are not modeled. Debugfs decode calls the normal output path with synthetic MCE fields. Error classification ignores MCEs without `ADDRV`; decode failures still emit EDAC events with unknown coordinates.

## Test Signals
Test Apollo Lake and Denverton CPU matches, GHES/owner/hypervisor rejection, P2SB busy and timeout paths, invalid MOT mask/base validation, addresses in MMIO gaps and above TOHM, symmetric/asymmetric/MOT interleaves, APL and DNV DIMM geometries, ECC-disabled channels, MCE filtering, debugfs fake-address decode, and notifier unregister on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.h -->
# sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.h

## Purpose
Defines Pondicherry2 memory-controller register bitfield layouts and access metadata used by `pnd2_edac.c`. It covers top-of-memory PCI registers, slice/channel hash and asymmetric region registers, MOT range registers, and Apollo Lake/Denverton D-unit geometry registers.

## Important APIs, Types, And Functions
- `b_cr_touud_*`, `b_cr_tolud_pci`, and MCHBAR structs describe memory limits and MCHBAR base enablement.
- `b_cr_slice_channel_hash`, asymmetric region structs, and MOT structs describe first-stage interleave and region decode controls.
- `d_cr_drp0` describes Apollo Lake DIMM presence, ECC, address map, bank/rank hash, density, width, and DRAM type.
- `d_cr_dsch`, `d_cr_ecc_ctrl`, `d_cr_drp`, and `d_cr_dmap*` describe Denverton channel, ECC, DIMM rank, and address-bit mapping.
- The `*_port`, `*_offset`, and `*_r_opcode` macros provide register-access metadata consumed by `RD_REG` and `RD_REGP`.

## Control Flow
The header has no executable control flow. Its bitfields are populated by the active `dunit_ops->rd_reg` implementation and then consumed by topology construction, ECC checks, DIMM configuration, and address decoding.

## State And Persistence
No runtime state is stored in the header. Instances of these structures are cached as static globals in `pnd2_edac.c` after probe and treated as stable hardware configuration.

## Dependencies And Integration Points
The structures rely on Linux fixed-width integer types and compiler bitfield layout matching the target little-endian register interpretation. The metadata macros are tightly coupled to the sideband/MMIO/config-space access helpers in `pnd2_edac.c`.

## Risks And Edge Cases
C bitfield layout is compiler and endian sensitive, so this header is appropriate only for the intended kernel/architecture ABI. Register fields differ between Apollo Lake and Denverton, which is why separate structs exist; using the wrong struct or opcode would corrupt decode. Reserved sentinel values such as `31` and `0x3f` in DNV maps must be interpreted carefully by the decoder.

## Test Signals
Compile on the intended x86 configs, compare decoded struct fields against raw register dumps, validate APL and DNV register metadata, and run address-decode tests for every mapped row/column/bank/rank field combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/qcom_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/qcom_edac.c

## Purpose
Implements EDAC device reporting for Qualcomm LLCC ECC errors. It configures LLCC ECC interrupt propagation, dumps DRAM and tag RAM syndrome/count/way registers per bank, clears error status, and reports LLCC data/tag RAM CE and UE events.

## Important APIs, Types, And Functions
- `edac_reg_data[]` describes the syndrome register count, count masks, way masks, and shifts for DRAM/TRAM CE/UE classes.
- `qcom_llcc_core_setup` enables TRP/DRP interrupt paths and sets the single-bit threshold.
- `qcom_llcc_clear_error_status` clears DRP or TRP interrupt and counter registers.
- `dump_syn_reg_values` reads syndrome, count, and way registers for a bank and error type.
- `dump_syn_reg` maps dumped error types to EDAC CE/UE handlers.
- `llcc_ecc_irq_handler` scans all LLCC banks for DRP/TRP single- or double-bit status.
- `qcom_llcc_edac_probe` allocates the EDAC device and selects interrupt or polling mode.

## Control Flow
Probe receives `llcc_drv_data` through platform data. If firmware/LLCC has not configured ECC IRQ routing, it programs the broadcast regmap. It allocates one EDAC device with one logical `qcom-llcc` instance and one block per bank, sets `panic_on_ue`, tries to request the provided IRQ, and falls back to five-second polling when no IRQ is usable. The IRQ/poll handler iterates banks, reads DRP status then TRP status, dumps and clears the first matching CE or UE class for each, and marks the interrupt handled when register operations succeed.

## State And Persistence
Driver-private state is the EDAC device; LLCC topology and register maps live in `llcc_drv_data` supplied by the LLCC core. Hardware interrupt enables, thresholds, syndrome registers, counters, and clear registers persist in LLCC hardware. Remove deletes and frees the EDAC device but does not undo LLCC interrupt configuration.

## Dependencies And Integration Points
Depends on `linux/soc/qcom/llcc-qcom.h`, LLCC-provided regmaps and register offsets, EDAC device APIs, and platform device ID `qcom_llcc_edac`. It integrates with either IRQ delivery or EDAC polling.

## Risks And Edge Cases
The handler uses `else if`, so if a bank reports both CE and UE for DRP or TRP, only the CE path is handled first. It sets `irq_rc = IRQ_HANDLED` whenever the status read succeeds, even if no error bit was set, after each DRP/TRP read. `panic_on_ue` is enabled, so uncorrectable LLCC errors can intentionally panic depending on EDAC policy. Clear-on-dump means syndrome data is lost after reporting.

## Test Signals
Validate core setup writes, IRQ and polling fallback paths, each DRAM/TRAM CE/UE status bit, multi-bank iteration, simultaneous CE/UE behavior, syndrome/count/way prints, clear-register writes, and remove without LLCC state leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/qcom_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/sb_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/sb_edac.c

## Purpose
Implements EDAC memory-controller support for Intel Sandy Bridge-EP, Ivy Bridge-EP, Haswell-EP, Broadwell-EP/D, and Knights Landing/Knights Mill server platforms. It discovers the many PCI functions that expose IMC/SAD/TAD/RIR registers, builds EDAC DIMM topology, decodes memory machine-check events, and reports corrected, uncorrected, or fatal memory errors.

## Important APIs, Types, And Functions
- `struct sbridge_info`, `struct sbridge_dev`, `struct sbridge_pvt`, and `struct knl_pvt` model generation-specific callbacks, PCI devices, EDAC-private topology, and KNL-specific device arrays.
- PCI ID descriptor tables define the required and optional PCI functions for each CPU generation.
- `sbridge_get_all_devices`, `sbridge_get_onedevice`, and bind helpers collect PCI devices and attach them to the private structure.
- `get_dimm_config`, `__populate_dimms`, and `knl_get_dimm_capacity` fill EDAC DIMM sizes, labels, memory type, width, rank, row/column, mirroring, lockstep, and page-mode state.
- `get_memory_layout` logs TOLM/TOHM, SAD, TAD, offsets, and RIR layout.
- `get_memory_error_data` decodes a physical address through SAD, TAD, channel, RIR, and Broadwell row/column logic.
- `get_memory_error_data_from_mce` uses MCE-provided channel data when the address granularity is too coarse.
- `sbridge_mce_check_error` and `sbridge_mce_output_error` filter MCEs, classify severity, decode location, and call `edac_mc_handle_error`.
- `sbridge_register_mci`, `sbridge_probe`, `sbridge_init`, and `sbridge_exit` manage EDAC and MCE notifier lifetime.

## Control Flow
Module init rejects GHES ownership, other EDAC owners, hypervisors, and unsupported CPU models, then initializes EDAC opstate and probes the generation's PCI table. Probe gathers all required PCI functions, creates one EDAC MC per discovered IMC/domain, binds generation-specific devices, fills `sbridge_info` callbacks, obtains source/node IDs, reads DIMM and memory-layout state, and registers each MC. When an MCE arrives, the notifier filters non-memory errors, missing address/misc validity, and non-physical-address reports. Output classification derives CE/UE/fatal, handles KNL specially, otherwise decodes by physical address or MCE channel bits, adjusts for mirroring/lockstep/channel masks, and reports the event.

## State And Persistence
Global state includes `sbridge_edac_list` and static message buffers. Each `sbridge_dev` owns PCI device references and the associated `mem_ctl_info`; each `sbridge_pvt` caches PCI function pointers, generation callbacks, channel/DIMM metadata, memory limits, mirroring/lockstep state, and KNL route devices. Hardware topology is read at probe and used for all later MCE decodes. Exit unregisters MCs, releases PCI references, and unregisters the MCE notifier.

## Dependencies And Integration Points
Depends on x86 CPU model matching, PCI config space, Intel machine-check records, EDAC MC APIs, GHES/EDAC ownership arbitration, and generation-specific Intel IMC register layouts. It integrates with the MCE decode chain at `MCE_PRIO_EDAC` and marks handled records with `MCE_HANDLED_EDAC`.

## Risks And Edge Cases
The decode logic is highly generation-specific and includes documented FIXME areas for channel index offsets, lockstep row/column decode, DDR3 row/column decode, and channel-mask support in EDAC reporting. KNL capacity is inferred from SAD/TAD/route tables and can underreport if BIOS maps less than installed memory. PCI discovery must balance references across optional, shared, duplicated, and multi-bus devices. Static message buffers are shared by notifier execution. Mirroring and lockstep can make a single-DIMM report ambiguous.

## Test Signals
Use per-generation PCI discovery tests, missing optional/required device paths, ECC-disabled DIMM rejection, TOLM/TOHM/SAD/TAD/RIR layout dumps, MCE filtering for ADDRV/MISCV/address type, address decodes across SAD/TAD/RIR boundaries, Haswell/Broadwell channel hashing and mirroring, Broadwell DDR4 row/column decode, KNL EDRAM and DRAM channel reports, and notifier cleanup on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/sb_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/scrub.c -->
# sources/distributed-fs/ceph-client/drivers/edac/scrub.c

## Purpose
Provides the generic EDAC scrub sysfs descriptor builder for RAS feature devices. It exposes a uniform interface for scrub address, size, background enablement, and cycle-duration limits/current setting while delegating actual scrub control to provider callbacks.

## Important APIs, Types, And Functions
- `struct edac_scrub_context` owns one named scrub sysfs group and per-attribute wrappers.
- `EDAC_SCRUB_ATTR_SHOW` and `EDAC_SCRUB_ATTR_STORE` generate callback-backed sysfs handlers.
- `scrub_attr_visible` hides unsupported scrub attributes and makes getter-only attributes read-only.
- `scrub_create_desc` allocates and initializes the attribute group named `scrubN`.
- `edac_scrub_get_desc` is the public descriptor API for feature clients.

## Control Flow
Clients call `edac_scrub_get_desc(scrub_dev, attr_groups, instance)`. The helper validates inputs and creates a devm-managed context. `scrub_create_desc` builds local attribute templates for the requested instance, copies them into persistent context storage, initializes sysfs metadata, assigns group name/attrs/visibility, and writes the group into `attr_groups[0]`. Sysfs handlers recover the instance, fetch `edac_dev_feat_ctx`, select `ctx->scrub[inst]`, and call the provider's `edac_scrub_ops`.

## State And Persistence
The file persists only devm-managed descriptor state. Scrub configuration and progress are provider-owned. The generated sysfs files simply pass values through to parent-device callbacks with provider-private data.

## Dependencies And Integration Points
Depends on `linux/edac.h`, `struct edac_dev_feat_ctx`, `struct edac_scrub_ops`, sysfs attribute groups, and devm allocation. It integrates with the EDAC RAS feature framework rather than registering a standalone platform driver.

## Risks And Edge Cases
Visibility must match callbacks because generated handlers dereference provider ops directly. Conversion uses base autodetection and performs no generic range validation, so providers must validate address/size alignment, cycle bounds, and enable values. The descriptor writes only `attr_groups[0]`, so callers must provide storage and chain additional groups themselves.

## Test Signals
Instantiate providers with full, read-only, and sparse scrub ops; verify sysfs permissions; test invalid numeric stores and provider error propagation; confirm multiple instances dispatch correctly; and verify min/max/current cycle attributes appear according to callback availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/scrub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/sifive_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/sifive_edac.c

## Purpose
Registers a small EDAC device for SiFive platform cache/ECC errors delivered by the SiFive ccache notifier. It translates notifier event types into EDAC CE and UE device events.

## Important APIs, Types, And Functions
- `struct sifive_edac_priv` stores the notifier block and EDAC device control pointer.
- `ecc_err_event` maps `SIFIVE_CCACHE_ERR_TYPE_UE` to `edac_device_handle_ue` and `SIFIVE_CCACHE_ERR_TYPE_CE` to `edac_device_handle_ce`.
- `ecc_register` allocates private state and EDAC device state, registers the EDAC device, then registers the ccache notifier.
- `ecc_unregister` reverses notifier and EDAC registration.
- `sifive_edac_init` creates a synthetic platform device and registers the EDAC notifier path.

## Control Flow
Module init creates a simple platform device named `sifive_edac`, calls `ecc_register`, and unregisters the platform device if registration fails. Registration allocates state, creates one EDAC device instance/block, fills names, adds it to EDAC, and subscribes to ccache errors. Notifier callbacks pass the ccache-provided message directly to EDAC. Exit unregisters the notifier, removes the EDAC device, frees control info, and unregisters the platform device.

## State And Persistence
Persistent module state is the global `sifive_pdev`. Per-device state is `sifive_edac_priv`, devm-allocated against the synthetic platform device. Hardware error state is owned by the SiFive ccache subsystem, not this driver.

## Dependencies And Integration Points
Depends on `soc/sifive/sifive_ccache.h` notifier APIs, EDAC device APIs, and platform-device registration. It has no OF match table; it creates its own platform device during module init.

## Risks And Edge Cases
Notifier registration happens after EDAC device registration and must be undone before freeing EDAC state. Unknown event values are ignored but still return `NOTIFY_OK`. Because the platform device is synthetic, module load depends on the ccache notifier symbols being meaningful on the running platform.

## Test Signals
Trigger CE and UE ccache notifier events, unknown event values, EDAC add failure cleanup, module unload ordering, and message propagation into EDAC event text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/sifive_edac.c -->
