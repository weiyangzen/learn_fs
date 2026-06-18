# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_hwmgr.h

## Purpose
This header defines the Vega10 PowerPlay backend data model used by `vega10_hwmgr.c`. It names SMU feature indexes, DPM table shapes, PowerPlay hardware power-state records, voltage and leakage caches, registry/configuration knobs, OverDrive state, and the top-level `struct vega10_hwmgr` stored in `hwmgr->backend`.

## Important APIs, Types, and Functions
- `enum GNLD_*`: indexes logical SMU features such as GFX/UCLK/SOCCLK DPM, UVD/VCE DPM, ULV, AVFS, thermal, fan control, ACG, DIDT, and PCC limiting. `GNLD_DPM_MAX` bounds the DPM feature subset, while `GNLD_FEATURES_MAX` bounds the whole feature array.
- `struct smu_features`: per-feature support/enabled state plus SMU feature id and bitmap.
- `struct vega10_power_state`: hardware power-state payload embedded in `pp_power_state`, including UVD/VCE clocks, performance levels, DC compatibility, and SCLK threshold.
- `struct vega10_dpm_table` and related `vega10_single_dpm_table`, `vega10_dpm_level`, `vega10_dpm_state`, `vega10_pcie_table`: software representation of clock/link DPM levels before they are converted to firmware PPTable fields.
- `struct vega10_smc_state_table`: caches firmware-facing `PPTable_t`, watermark table, AVFS table, and boot/max DPM indexes.
- `struct vega10_registry_data`: runtime policy flags derived from feature masks or registry-like defaults, controlling DPM enablement, power containment, AVFS, DIDT, thermal/fan behavior, watermarks, PCIe overrides, OD support, and GPIO features.
- `struct vega10_hwmgr`: top-level backend state with DPM tables, golden defaults, voltage tables, leakage data, BACO flags, OD state, display timing, feature array, SMU tables, and custom profile fields.
- Exported declarations: media DPM update helpers, `vega10_enable_disable_vce_dpm()`, and `vega10_hwmgr_init()`.

## Control Flow and Integration
The header itself has no executable flow, but its structures define the control data used throughout the Vega10 manager. The common hardware manager stores a `struct vega10_hwmgr` pointer in `hwmgr->backend`; implementation functions mutate this state and then issue SMC messages or table uploads. The `vega10_power_state` shape determines how PowerPlay table entries are parsed and compared during state transitions.

## State and Persistence
The key persistent runtime state is `struct vega10_hwmgr`. It keeps both desired software configuration and mirrors of firmware state: DPM levels, soft min/max indexes, enabled features, watermarks, power-gating flags, voltage tables, OD edits, and custom workload profile data. `golden_dpm_table` is a reset baseline for OD restore and range reporting. None of this is disk-persistent; it is reconstructed on driver load and adjusted at runtime.

## Dependencies
- Core PowerPlay types from `hwmgr.h`, `ppatomctrl.h`, `ppatomfwctrl.h`.
- SMU firmware ABI types from `smu9_driver_if.h` and `vega10_ppsmc.h`.
- PowerTune constants/types from `vega10_powertune.h`.
- Legacy Tonga declarations remain at the bottom, suggesting shared or migrated code paths from earlier ASIC support.

## Risks
- Many arrays use fixed firmware limits such as `MAX_REGULAR_DPM_NUMBER`, `MAX_PCIE_CONF`, and `VEGA10_MAX_HARDWARE_POWERLEVELS`. Implementation code must validate VBIOS counts before filling them.
- `struct vega10_hwmgr` is broad and mutable; feature toggles, OD edits, display changes, and SMC table contents share the same object, increasing stale-state risk.
- The header exposes several Tonga-named externs in a Vega10 header. If unused, they are harmless but confusing; if used, they signal tight legacy coupling.
- Boolean registry fields are compact but numerous. Default initialization must remain comprehensive or new fields can silently default to unsupported behavior.

## Test Signals
- Compile tests catch struct and callback signature drift across `vega10_hwmgr.c` and companion modules.
- Runtime tests should observe that backend state mirrors firmware state after DPM enable/disable, OD restore, feature toggles, watermarks, and media power gating.
- ABI-sensitive changes should be tested against SMU table layout expectations because `PPTable_t`, `Watermarks_t`, and AVFS structures are firmware-facing.
