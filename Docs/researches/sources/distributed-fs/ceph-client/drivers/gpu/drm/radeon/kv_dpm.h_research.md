# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_dpm.h

## Purpose

`kv_dpm.h` defines the private data model and SMC-facing API for Kaveri/Kabini/Mullins DPM support. It bridges `kv_dpm.c` policy code and `kv_smc.c` transport helpers by declaring SMC table capacities, register configuration descriptors, per-level/per-state structures, the large `struct kv_power_info` state block, and prototypes for SMU message and SMC SRAM access functions.

## Important APIs, types, and fields

- Capacity constants: `SMU__NUM_SCLK_DPM_STATE`, `SMU__NUM_MCLK_DPM_LEVELS`, `SMU__NUM_LCLK_DPM_LEVELS`, `SMU__NUM_PCIE_DPM_LEVELS`, and `KV_NUM_NBPSTATES`.
- `enum kv_pt_config_reg_type`: identifies register access paths for power/tuning configuration entries: normal MMR, SMC indirect, DIDT indirect, cache-only, and max sentinel.
- `struct kv_pt_config_reg`: offset/mask/shift/value/type descriptor consumed by `kv_program_pt_config_registers()` in `kv_dpm.c` for DIDT/power-tuning setup.
- `struct kv_lcac_config_values` and `struct kv_lcac_config_reg`: local CAC descriptor shapes. They are defined here but not used by the listed implementation path, suggesting planned or shared support.
- `struct kv_pl`: one logical KV power level, including SCLK, voltage index, deep/light sleep divider indices, GNB slow flag, forced NB state, display watermark, and VCE watermark.
- `struct kv_ps`: per-radeon-power-state KV private payload with up to `SUMO_MAX_HARDWARE_POWERLEVELS`, DFS bypass request, and NB DPM policy indexes.
- `struct kv_sys_info`: BIOS-derived integrated system information: boot UMA/SCLK, NB DPM enable, NB memory/N clock arrays, boot NB voltage, HTC limits, SCLK/VID mapping tables, and UMA channel count.
- `struct kv_power_info`: the persistent DPM private state attached to `rdev->pm.dpm.priv`. It contains thresholds, BIOS/system data, SMU SRAM offsets, SMU7 Fusion DPM table mirrors, boot/current/requested states, power-gate booleans, feature enable flags, and hardware capability booleans.
- SMC helper prototypes: `kv_notify_message_to_smu()`, `kv_dpm_get_enable_mask()`, `kv_send_msg_to_smc_with_parameter()`, `kv_read_smc_sram_dword()`, `kv_smc_dpm_enable()`, `kv_smc_bapm_enable()`, and `kv_copy_bytes_to_smc()`.

## Control flow

The header has no executable control flow. It shapes control flow in the C files by defining which state is available for initialization, transition, upload, power-gating, debugfs reporting, and teardown. `kv_dpm.c` allocates `struct kv_power_info`, stores it in `rdev->pm.dpm.priv`, allocates one `struct kv_ps` per parsed PowerPlay state, and passes SMU table mirrors to `kv_smc.c` helpers through the declared API.

## State and persistence behavior

`struct kv_power_info` is the core persistent state for the DPM implementation. It persists:

- BIOS-derived system configuration in `sys_info`.
- Driver policy and runtime decisions such as `lowest_valid`, `highest_valid`, `battery_state`, `video_start`, `bapm_enable`, `cac_enabled`, `nb_dpm_enabled`, and block power-gate booleans.
- SMC SRAM layout in `sram_end`, `dpm_table_start`, and `soft_regs_start`.
- Host-side mirrors of SMU7 Fusion tables, including graphics, UVD, VCE, ACP, and SAMU levels and boot levels.
- Current and requested radeon/KV power-state copies.

The header embeds SMU table types from `smu7_fusion.h`, so layout compatibility with firmware is part of the contract. Field sizes are intentionally narrow for many SMU table fields (`u8`, `u16`) and callers must perform the correct endian conversion before upload.

## Dependencies and integration points

- Includes `smu7_fusion.h` for firmware table structs, `trinity_dpm.h` for Sumo/Trinity shared DPM structures and constants, and `ppsmc.h` for SMU message enum/types.
- Exposed only inside the radeon driver implementation; it assumes `struct radeon_device`, `struct radeon_ps`, and fixed-width integer types are already available through include order in C files.
- Used by `kv_dpm.c` for all policy/state manipulation and by `kv_smc.c` for function declarations.
- State in this header integrates with `rdev->pm.dpm` ownership, ATOM BIOS dependency tables, and firmware SMC DPM table offsets.

## Risks and edge cases

- `SMU__NUM_PCIE_DPM_LEVELS` is defined as zero with a comment, so code must not assume PCIe DPM table storage exists.
- Several fields are declared but lightly used or unused in the listed implementation (`dentist_vco_freq`, `uma_channel_number`, LCAC structures, `enable_nb_ps_policy`, `graphics_clk_slow_*`), which can lead to stale assumptions if new code starts relying on them.
- `fps_low_t` is a `u8` while `kv_dpm.c` treats the FPS low threshold as a 16-bit value during upload; this mismatch is a maintenance risk even though FPS caps are disabled by default.
- Because this is a private kernel header, there are no runtime bounds checks on array use. Callers must keep table counts within `SMU__NUM_SCLK_DPM_STATE`, `SMU7_MAX_LEVELS_*`, and `SUMO_MAX_HARDWARE_POWERLEVELS`.
- The layout of `struct kv_power_info` is not firmware ABI directly, but its embedded SMU table arrays are firmware ABI mirrors; changes to those dependent structs must match firmware expectations.

## Test signals

- Compile coverage of `kv_dpm.c` and `kv_smc.c` validates prototypes and structure field usage.
- Runtime DPM enable validates that `struct kv_power_info` has all offsets and mirrors initialized before SMC upload.
- Debugfs and power-state transition tests validate that current/requested state copies and `ps_priv` pointers remain coherent.
- Static analysis should check array bounds around graphics/media level counts and flag width mismatches such as the FPS fields.
