# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/wcl.c

Purpose: adds Wildcat Lake PMC support for PCD-N using SSRAM discovery and blocker-style PMT substate requirements.

Important APIs/types/functions: `wcl_pcdn_pfear_map`, `wcl_pcdn_ltr_show_map`, `wcl_pcdn_lpm_maps`, and `wcl_pcdn_blk_maps` define the WCL diagnostic layout. `wcl_pcdn_reg_map` sets WCL MMIO length, blocker count/offset, LPM status offsets, and `PCDN_LPM_REQ_GUID`. `wcl_pmc_info_list[]` maps `PMC_DEVID_WCL_PCDN`. `wcl_d3_fixup()`, `wcl_core_init()`, and `wcl_resume()` handle unbound NPU D3.

Control flow: `core.c` matches Wildcat Lake-L to `wcl_pmc_dev`. Init runs NPU D3 fixup then generic SSRAM init. Requirement fetching uses `pmc_core_pmt_get_blk_sub_req()`, and debugfs uses `pmc_core_substate_blk_req_fops`.

State and persistence: static maps plus runtime PMC state in `core.c`. WCL reuses exported PTL maps for clocksource, VNN3, and signal status, so those symbols must remain available.

Dependencies and integration points: depends on PTL exported maps, CNP/TGL/MTL/LNL offsets, SSRAM telemetry, PMT telemetry GUID `PCDN_LPM_REQ_GUID`, and CNL suspend/resume. Debugfs consumers include PPFEAR, LTR, S0ix blocker, LPM status, and blocker requirements.

Risks: blocker count and offset are platform-specific; any mismatch with the PMT telemetry table shifts requirements. PTL map reuse is a cross-platform dependency. As with other D3 fixups, behavior depends on whether the NPU has a bound driver.

Test signals: Wildcat Lake systems should expose WCL labels in `ltr_show`, `s0ix_blocker`, and `substate_requirements`. PMT reads at `WCL_BLK_REQ_OFFSET` should succeed. NPU D3 state and suspend/resume S0ix residency are practical integration signals.
