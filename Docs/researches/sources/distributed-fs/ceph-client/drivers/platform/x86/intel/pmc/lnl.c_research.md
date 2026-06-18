# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/lnl.c

Purpose: provides Lunar Lake PMC platform data for an SSRAM-discovered SoC-M controller, including LPM status maps, blocker maps, PPFEAR maps, LTR maps, and D3 fixups for unbound IPU/NPU devices.

Important APIs/types/functions: `LNL_LPM_REG_INDEX` maps PMT LPM table registers into debugfs requirement columns. `lnl_ltr_show_map`, `lnl_lpm_maps`, `lnl_blk_maps`, and `ext_lnl_pfear_map` feed `lnl_socm_reg_map`. Many `pmc_bit_map` entries populate the `blk` field, which `pmc_core_s0ix_blocker_show()` and `pmc_core_pmt_get_blk_sub_req()` use for blocker counters and requirement offsets. `lnl_d3_fixup()`, `lnl_core_init()`, and `lnl_resume()` wrap generic init/resume. `lnl_pmc_dev` is the exported platform descriptor.

Control flow: `core.c` matches `INTEL_LUNARLAKE_M` to `lnl_pmc_dev`. Init sets IPU/NPU to D3 if unbound, then `generic_core_init()` uses SSRAM telemetry to discover `PMC_DEVID_LNL_SOCM`, maps the controller, reads enabled LPM modes, and reads PMT LPM requirements with `pmc_core_pmt_get_lpm_req()`. Resume repeats the D3 fixup then uses `cnl_resume()`.

State and persistence: all maps are static. D3 fixup mutates PCI power state. Requirement buffers and LPM mode state are allocated/managed by `core.c` during probe.

Dependencies and integration points: depends on SSRAM telemetry, PMT telemetry GUID `SOCM_LPM_REQ_GUID`, CNP/ADL/TGL/MTL offsets, and `cnl_suspend`/`cnl_resume`. The `s0ix_blocker_maps` path integrates with the `s0ix_blocker` debugfs file and with blocker-style requirements only if the regmap supplies blocker metadata.

Risks: the `blk` metadata is easy to misalign with hardware counter spacing, producing wrong blocker counts even when bit displays look correct. The LNL PPFEAR map includes repeated or reserved labels, so consumers should treat it as hardware diagnostic labeling rather than a stable userspace ABI. D3 fixups depend on device IDs and driver binding status.

Test signals: Lunar Lake boot should expose `s0ix_blocker`, `substate_requirements`, `substate_status_registers`, and `ltr_show` with LNL labels. PMT endpoint discovery failures should defer or fail probe through `generic_core_init()`. Suspend/resume should maintain IPU/NPU D3 when unbound and restore LTR/MSR state through CNL hooks.
