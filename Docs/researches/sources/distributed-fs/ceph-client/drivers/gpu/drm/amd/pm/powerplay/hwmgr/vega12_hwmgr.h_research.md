# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_hwmgr.h

`vega12_hwmgr.h` defines the private data model for the Vega12 PowerPlay backend. Its central type is `struct vega12_hwmgr`, stored in `pp_hwmgr.backend`, with DPM tables, feature state, registry defaults, VBIOS boot values, SMU tables, watermarks, clock ranges, power-gating booleans, gfxoff control, metrics cache, and GPU metrics storage.

Important types are `struct smu_features`, `vega12_dpm_level`, `vega12_dpm_state`, `vega12_single_dpm_table`, `vega12_dpm_table`, `vega12_smc_state_table`, `vega12_registry_data`, `vega12_vbios_boot_state`, ODN tables, fan table, MCLK latency table, and `vega12_clock_range`. It exposes `vega12_enable_disable_vce_dpm()` for media DPM control by other modules.

There is no executable control flow, but this header shapes runtime control: registry defaults populate `registry_data`; SMU feature setup uses `smu_features[]`; DPM setup fills nested DPM tables; display paths use `display_timing`, `clk_range[]`, and `water_marks_table`; metrics paths update `metrics_table` and `gpu_metrics_table`.

All state represented here is volatile kernel memory mirroring firmware and parsed VBIOS inputs. Dependencies include generic hwmgr definitions, SMU9 Vega12 driver interfaces, ATOM firmware control types, and firmware table types such as `PPTable_t`, `Watermarks_t`, and `SmuMetrics_t`.

Risks include structure drift against firmware interfaces, fixed array sizes (`MAX_REGULAR_DPM_NUMBER`, `PPCLK_COUNT`), duplicate default macro names, and misspelled pseudo-count macros. Test signals are compile coverage, successful SMU table upload, correct feature-name mapping, and debug/sanitizer checks around DPM indexing.
