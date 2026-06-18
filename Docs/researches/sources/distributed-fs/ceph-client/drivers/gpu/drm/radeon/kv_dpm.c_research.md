# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_dpm.c

## Purpose

`kv_dpm.c` implements dynamic power management for AMD Kaveri/Kabini/Mullins-class Radeon APUs in the legacy radeon driver. It parses ATOM BIOS integrated system and PowerPlay tables, constructs driver-private Kaveri power states, populates SMU7 Fusion DPM tables, uploads those tables to SMC SRAM, controls DPM/CAC/BAPM/ULV/DIDT/thermal features, and power-gates UVD, VCE, SAMU, and ACP blocks. It is the policy and orchestration layer above the lower-level SMC helpers in `kv_smc.c` and the state definitions in `kv_dpm.h`.

## Important APIs, types, and functions

- Private accessors: `kv_get_pi()` returns `struct kv_power_info` from `rdev->pm.dpm.priv`; `kv_get_ps()` returns `struct kv_ps` from a `struct radeon_ps`.
- Enable/disable lifecycle: `kv_dpm_init()`, `kv_dpm_setup_asic()`, `kv_dpm_enable()`, `kv_dpm_late_enable()`, `kv_dpm_disable()`, and `kv_dpm_fini()`.
- Power-state transition API: `kv_dpm_pre_set_power_state()`, `kv_dpm_set_power_state()`, `kv_dpm_post_set_power_state()`, `kv_dpm_force_performance_level()`, `kv_dpm_get_sclk()`, `kv_dpm_get_mclk()`, `kv_dpm_get_current_sclk()`, `kv_dpm_get_current_mclk()`, and debug/print helpers.
- Table builders: `kv_init_graphics_levels()`, `kv_program_bootup_state()`, `kv_calculate_dfs_bypass_settings()`, `kv_upload_dpm_settings()`, `kv_populate_uvd_table()`, `kv_populate_vce_table()`, `kv_populate_samu_table()`, and `kv_populate_acp_table()`.
- Policy adjusters: `kv_apply_state_adjust_rules()`, `kv_set_valid_clock_range()`, `kv_calculate_ds_divider()`, `kv_calculate_nbps_level_settings()`, `kv_calculate_dpm_settings()`, and `kv_program_nbps_index_settings()`.
- SMU/SMC controls: calls into `kv_notify_message_to_smu()`, `kv_send_msg_to_smc_with_parameter()`, `kv_copy_bytes_to_smc()`, `kv_smc_dpm_enable()`, `kv_smc_bapm_enable()`, and `kv_dpm_get_enable_mask()`.
- Media and auxiliary block power gating: `kv_dpm_powergate_uvd()` is exported, while VCE/SAMU/ACP gate functions are static; update helpers set boot levels and masks before enabling block DPM.
- BIOS parsing: `kv_parse_sys_info_table()` reads ATOM `IntegratedSystemInfo` revision 8; `kv_parse_power_table()` reads ATOM PowerPlay state arrays and fills `rdev->pm.dpm.ps`.

## Control flow

Initialization starts in `kv_dpm_init()`. It allocates `struct kv_power_info`, gets platform caps, parses extended power tables, initializes activity thresholds, sets feature capability flags, handles the ASRock subsystem quirk that disables NB DPM, chooses BAPM policy from `radeon_bapm`, parses integrated system info, patches voltage dependency table values from VID indices into voltage units, constructs the boot level, parses PowerPlay states, and sets `pi->enable_dpm`.

ASIC setup in `kv_dpm_setup_asic()` transfers SMU control to the driver through `sumo_take_smu_control()`, initializes local power-gate booleans to false, and clears the low-SCLK interrupt threshold.

`kv_dpm_enable()` is the main SMU table bring-up sequence. It reads firmware header offsets for the DPM and soft-register tables, initializes FPS limits, initializes graphics levels from dependency tables or integrated SCLK mapping, selects the boot graphics level, calculates DFS bypass settings, uploads graphics DPM levels and level counts, builds media/ACP/SAMU tables, programs voltage control, starts activity monitoring, enables thermal throttle policy, enables voltage scaling and DPM interval/boot state fields in SMC SRAM, enables ULV and DPM, optionally enables DIDT and CAC, resets ACP boot level, disables BAPM initially, and records the boot power state as current.

Late enable configures thermal interrupt thresholds only when IRQs are installed and the thermal sensor is internal, then powers down currently unused ACP/SAMU/VCE/UVD blocks. Disable runs the inverse: disable BAPM and NB DPM as needed, power blocks back up, disable CAC/DIDT/DPM/ULV/thermal interrupts, reset activity monitoring, and restore current state to boot.

Power-state transitions are staged. `kv_dpm_pre_set_power_state()` copies the requested radeon state into private storage and applies policy adjustments. `kv_dpm_set_power_state()` enables or disables BAPM based on AC power, computes valid SCLK ranges, updates DFS bypass, recalculates deep-sleep and NBPS settings, then either uses a Kabini/Mullins force-enable-unforce sequence or a freeze-upload-unfreeze sequence for other families. It updates VCE DPM according to encode activity, updates ACP boot level on non-Kabini/Mullins, updates low-SCLK notification thresholds, and enables NB DPM. `kv_dpm_post_set_power_state()` commits requested state as current.

## State and persistence behavior

Persistent runtime state is held in `struct kv_power_info` attached to `rdev->pm.dpm.priv`. It includes BIOS-derived system info, current/requested radeon and KV power states, valid DPM bounds, high-voltage and threshold limits, SMU SRAM offsets, graphics/media/ACP/SAMU tables, boot levels, intervals, power-gate booleans, NB DPM state, and feature caps. Per-power-state private data is allocated as `struct kv_ps` and stored in `rdev->pm.dpm.ps[i].ps_priv`.

The code persists hardware-visible state by writing SMC SRAM table fields and by issuing SMU messages. Endianness is explicit for SMC table structures: many fields are converted through `cpu_to_be16()` and `cpu_to_be32()` before upload because SMC SRAM is treated as big-endian. BIOS table data is read little-endian through `le16_to_cpu()` and `le32_to_cpu()`.

Power-gate booleans (`uvd_power_gated`, `vce_power_gated`, `samu_power_gated`, `acp_power_gated`) prevent duplicate gate transitions. Current/requested power-state copies are value copies with `ps_priv` redirected to embedded `current_ps` and `requested_ps` storage, avoiding dangling pointers to temporary stack states.

## Dependencies and integration points

- Includes `cikd.h` for Kaveri/CIK-family register and message definitions, `kv_dpm.h` for state layout and SMC prototypes, `r600_dpm.h` for common DPM helpers, and core Radeon headers.
- Calls ATOM BIOS helpers: `atom_parse_data_header()`, `GetIndexIntoMasterTable()`, `radeon_atom_get_clock_dividers()`, `sumo_construct_sclk_voltage_mapping_table()`, and `sumo_construct_vid_mapping_table()`.
- Integrates with common DPM state in `rdev->pm.dpm`, including dependency tables, VCE states, requested/current power states, AC power, display CRTC count, thermal state, and debugfs printing.
- Uses media block helpers: `uvd_v1_0_stop()`, `uvd_v4_2_resume()`, `uvd_v1_0_start()`, `vce_v2_0_resume()`, `vce_v1_0_start()`, and `cik_update_cg()`.
- Uses RLC safe mode around DIDT register programming via external `cik_enter_rlc_safe_mode()` and `cik_exit_rlc_safe_mode()`.
- Delegates SMC message and SRAM access to `kv_smc.c`.

## Risks and edge cases

- BIOS assumptions are strict. `kv_parse_sys_info_table()` accepts integrated system info content revision 8 and returns `-EINVAL` otherwise; malformed table counts can affect loops that assume dependency table lengths match `SMU7_MAX_LEVELS_*`.
- Several places index fixed graphics levels directly, for example NBPS logic writes levels 1 through 4 on Kabini/Mullins; correctness relies on enough graphics levels being initialized.
- Error handling is inconsistent after some non-fatal operations. For example `kv_calculate_nbps_level_settings()`, `kv_calculate_dpm_settings()`, `kv_upload_dpm_settings()`, and SMC mask-setting calls are sometimes invoked without checking the returned status.
- The stable-p-state block in `kv_apply_state_adjust_rules()` appears suspicious: after finding a matching table entry, `if (i > 0) stable_p_state_sclk = table->entries[0].clk;` collapses to the lowest entry rather than the selected 75 percent target.
- Some feature flags are disabled or marked uncertain (`enable_didt = false`, `caps_fps = false /* true? */`, `caps_vce_pg = false /* XXX true */`, ACP boot-level comparison against `clk >= 0 /* XXX */`), so hardware support may be conservative or incomplete.
- SMC table uploads depend on `pi->dpm_table_start` and `pi->sram_end` from firmware; invalid offsets are mostly caught by `kv_copy_bytes_to_smc()`, but bad firmware can still prevent DPM enable.
- Power-gating order is hardware-sensitive, especially UVD/VCE clock gating and resume/start sequencing.

## Test signals

- Kernel build with radeon DPM enabled validates type and prototype integration.
- Successful `kv_dpm_init()` and `kv_dpm_enable()` on Kaveri/Kabini/Mullins hardware is the primary integration signal; failures log `DRM_ERROR()` messages naming the failed stage.
- Debugfs `kv_dpm_debugfs_print_current_performance_level()` should show valid SCLK, VDDC, and UVD/VCE gate states instead of an invalid profile.
- Runtime transitions between battery/AC, low/high/auto forced performance, display-count changes, video playback, VCE encode, UVD decode, and ACP/SAMU use should exercise valid-mask, NB DPM, media DPM, and power-gating paths.
- Thermal interrupt behavior should be validated by internal sensor events and by checking `rdev->pm.dpm.thermal` min/max fields after late enable.
- Suspend/resume and driver unload should verify `kv_dpm_disable()` and `kv_dpm_fini()` free private state and leave media blocks powered for reset/shutdown.
