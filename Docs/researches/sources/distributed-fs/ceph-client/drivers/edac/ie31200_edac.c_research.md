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
