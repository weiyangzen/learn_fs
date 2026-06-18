# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ptl.c

Purpose: adds Panther Lake PMC support for PCD-H/PCD-P dies using SSRAM discovery and blocker-style PMT substate requirements.

Important APIs/types/functions: `ptl_pcdp_pfear_map`, `ptl_pcdp_ltr_show_map`, `ptl_pcdp_lpm_maps`, and `ptl_pcdp_blk_maps` describe Panther Lake power/debug status. Exports `ptl_pcdp_clocksource_status_map`, `ptl_pcdp_vnn_req_status_3_map`, and `ptl_pcdp_signal_status_map` for WCL reuse. `ptl_pcdp_reg_map` sets `s0ix_blocker_maps`, `num_s0ix_blocker`, `blocker_req_offset`, and `lpm_req_guid`. `ptl_pmc_info_list[]` maps `PMC_DEVID_PTL_PCDH` and `PMC_DEVID_PTL_PCDP`. `ptl_d3_fixup()`, `ptl_core_init()`, and `ptl_resume()` handle unbound IPU/NPU D3.

Control flow: CPU match selects `ptl_pmc_dev`; init runs D3 fixup and generic SSRAM init. Requirement fetching uses `pmc_core_pmt_get_blk_sub_req()` rather than the register-index LPM table function, and debugfs uses `pmc_core_substate_blk_req_fops` for `substate_requirements`.

State and persistence: static platform maps only. Runtime controller mappings, blocker requirement arrays, and enabled modes are owned by `core.c`. D3 fixup alters unbound PCI device power state.

Dependencies and integration points: depends on CNP/TGL/MTL/LNL constants and CNL suspend/resume hooks. WCL reuses exported PTL clocksource, VNN3, and signal maps, so symbol visibility is intentional. SSRAM telemetry must discover one of the PTL device IDs; PMT telemetry must provide `PCDP_LPM_REQ_GUID`.

Risks: blocker requirement path depends on `num_s0ix_blocker`, `blocker_req_offset`, and every map entry's `blk` field; mismatch can shift all rows. Reused maps in WCL mean PTL changes can alter WCL output. As a 2025 platform file, silicon table churn is plausible.

Test signals: Panther Lake systems should expose `s0ix_blocker` and blocker-style `substate_requirements` with PTL labels. PMT reads beginning at `PTL_BLK_REQ_OFFSET` should succeed. Suspend/resume should run NPU/IPU D3 fixups and CNL LTR/MSR handling.
