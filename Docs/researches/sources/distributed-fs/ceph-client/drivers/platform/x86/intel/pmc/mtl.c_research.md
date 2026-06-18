# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/mtl.c

Purpose: supplies Meteor Lake PMC data for SSRAM-discovered SOC-M and IOE variants. It defines reusable maps later consumed by ARL and exports `mtl_pmc_dev` for Meteor Lake CPU matching.

Important APIs/types/functions: exports `mtl_socm_pfear_map`, several SOC-M D3/VNN/signal maps, `mtl_socm_reg_map`, and `mtl_ioep_reg_map`. Defines private IOE-P/IOE-M PFET, LTR, LPM, D3, VNN, and misc maps plus `mtl_ioem_reg_map`. `mtl_pmc_info_list[]` maps `PMC_DEVID_MTL_SOCM`, `PMC_DEVID_MTL_IOEP`, and `PMC_DEVID_MTL_IOEM` to regmaps. `mtl_d3_fixup()` sets unbound GNA/IPU/VPU devices to D3. `mtl_core_init()` and `mtl_resume()` wrap generic init/resume. `MTL_PMT_DMU_GUIDS` supports die C6 telemetry.

Control flow: `core.c` matches Meteor Lake-L to `mtl_pmc_dev`. Init performs D3 fixups, SSRAM discovery maps available SOC/IOE PMCs, reads enabled LPM modes, registers PUNIT DMU telemetry, and fetches LPM requirement registers using `pmc_core_pmt_get_lpm_req()`. Debugfs then iterates all available PMCs for PPFEAR, LTR, substate, and requirement views. Resume repeats D3 fixups then runs the CNL resume path.

State and persistence: maps are static and exported where later platform files reuse them. Runtime state is in `core.c`; `punit_ep` persists until driver removal and is used by `die_c6_us_show`.

Dependencies and integration points: depends on CNP offsets, ADL/TGL/MTL core constants, SSRAM telemetry device IDs, PMT telemetry GUIDs (`SOCP_LPM_REQ_GUID`, `IOEM_LPM_REQ_GUID`, `IOEP_LPM_REQ_GUID`, `MTL_PMT_DMU_GUID`), and the CNL suspend/resume quirk. ARL depends on several non-static maps from this file.

Risks: exported map reuse means MTL changes can affect ARL. Multi-PMC discovery must match silicon device IDs and GUIDs or requirement debugfs will be absent/fail. D3 fixups can change power state for devices without drivers and should remain targeted. IOE-M and IOE-P maps are similar but not identical; accidental consolidation would lose labels.

Test signals: Meteor Lake systems should show multiple PMC sections in `ltr_show`/PPFEAR when IOE is present, `die_c6_us_show` when DMU telemetry registers, and valid `substate_requirements`. Suspend/resume should show CNL quirk behavior plus MTL device D3 fixups.
