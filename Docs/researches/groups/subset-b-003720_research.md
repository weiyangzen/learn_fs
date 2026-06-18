# subset-b-003720 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreend.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreend.h

## Purpose

`evergreend.h` is the hardware definition header for Evergreen/Northern Islands-era Radeon ASIC support. It does not implement executable control flow; it supplies register offsets, bit masks, packet constructors, enumerated values, and ASIC-specific constants that C files use to program display, memory controller, graphics, VM, interrupt, DMA, HDMI/audio, thermal, and command processor blocks. The header is included by files such as `evergreen.c`, `evergreen_cs.c`, `evergreen_dma.c`, `evergreen_hdmi.c`, and `cypress_dpm.c`, and many definitions are also conceptually shared with adjacent family headers like `r600d.h`, `rv770d.h`, `nid.h`, `sid.h`, and `cikd.h`.

## Important APIs, types, and macros

- ASIC resource limits and golden values: `EVERGREEN_MAX_*` constants describe shader/GPR/thread/backend/SIMD/pipe limits; `*_GB_ADDR_CONFIG_GOLDEN` constants encode known-good `GB_ADDR_CONFIG` values for Cypress, Barts, Cayman, Juniper, Redwood, Turks, Cedar, Caicos, Sumo, and Sumo2.
- Register field helpers: most definitions follow the local pattern `FIELD(x)`, `FIELD_MASK`, and sometimes `FIELD_SHIFT`, for example `NUM_PIPES(x)`, `PIPE_INTERLEAVE_SIZE(x)`, `DIG_THERM_INTH(x)`, `DC_HPDx_INT_EN`, `ENABLE_CONTEXT`, and `PAGE_TABLE_DEPTH(x)`.
- Command packet helpers: `PACKET0(reg, n)`, `PACKET2(v)`, and `PACKET3(op, n)` construct PM4 command stream packet headers for CP rings; packet opcode constants cover draw, sync, event, register programming, CP DMA, indirect buffer, and clear-state operations.
- DMA helpers: `DMA_PACKET(cmd, sub_cmd, n)`, `GET_DMA_CMD`, `GET_DMA_COUNT`, `GET_DMA_SUB_CMD`, and `DMA_PACKET_*` opcode constants encode Evergreen async DMA packet headers.
- Display/audio definitions: DCE/AFMT/HDMI/AZ register families cover HDMI control/status/infoframes, audio clock DTOs, codec pin capabilities, hotplug status/control, vblank/vline interrupts, FMT dithering/clamping, and graphics page-flip interrupt bits.
- Graphics/VM/memory definitions: `GB_ADDR_CONFIG`, `CC_RB_BACKEND_DISABLE`, `VM_CONTEXT0_CNTL`, `VM_L2_CNTL*`, `MC_VM_*`, `SQ_*`, `DB_*`, `CB_COLOR*`, `SQ_TEX_RESOURCE_*`, and `SQ_VTX_CONSTANT_*` describe tiling, render target, depth, shader, texture, vertex, and virtual memory programming fields.
- Power/clock/thermal definitions: `SMC_MSG`, `GENERAL_PWRMGT`, `SCLK_PWRMGT_CNTL`, `MCLK_PWRMGT_CNTL`, SPLL/MPLL/UPLL registers, `CG_THERMAL_CTRL`, `CG_THERMAL_INT`, `CG_MULT_THERMAL_STATUS`, `TN_CG_THERMAL_INT_CTRL`, and related masks drive power-management and temperature code.

## Control flow

There is no runtime control flow inside the header. Its macros become inline constants and expressions in the caller's control flow. Typical flows using this header are:

1. ASIC initialization chooses a golden `GB_ADDR_CONFIG` value from the family constants and writes it with `WREG32`.
2. VM setup writes `VM_CONTEXT0_CNTL`, page-table base/start/end/default registers, and `VM_L2_CNTL*` bits.
3. Ring setup and command submission build PM4 packets through `PACKET3` and DMA packets through `DMA_PACKET`.
4. Interrupt handling uses status/control offsets such as `DISP_INTERRUPT_STATUS*`, `DC_HPDx_INT_STATUS`, `VBLANK_STATUS`, `GRPH_INT_STATUS`, and CP/IH interrupt registers.
5. Thermal and DPM code reads/writes `CG_THERMAL_*`, clock, and power-management registers.

## State and persistence behavior

The header itself has no mutable state, allocation, or persistence. It defines the ABI between driver code and hardware MMIO/command-stream layouts. The state affected by its constants lives in GPU registers, ring buffers, writeback memory, and command buffers built by other files. Because these macros encode hardware-visible bit positions, any incorrect value persists until the register is rewritten or the GPU block is reset.

## Dependencies and integration points

- Depends on common Radeon packet type definitions and helpers, including `RADEON_PACKET_TYPE0`, `RADEON_PACKET_TYPE3`, and `REG_SET`, which are provided by broader Radeon headers.
- Integrated by Evergreen core bring-up (`evergreen.c`), command parser validation (`evergreen_cs.c`), DMA engine code (`evergreen_dma.c`), HDMI/audio setup (`evergreen_hdmi.c`), and DPM/thermal paths (`cypress_dpm.c`, plus neighboring family DPM files for shared register concepts).
- Shares naming and register-family conventions with `nid.h`, `sid.h`, and `cikd.h`; callers must include the header matching the active ASIC generation to avoid programming wrong offsets or packet formats.

## Risks and edge cases

- Register drift across ASIC families is the main risk. Some names recur in multiple generation headers with different offsets or packet arities.
- Packet constructors do not validate `n`, register ranges, or opcode legality. Callers and command parsers must enforce packet lengths and register whitelists.
- Bitfield helpers generally shift without masking the input except for generated `S_*/G_*/C_*` style macros. Out-of-range inputs can set adjacent fields.
- Duplicated concepts such as thermal registers, `GB_ADDR_CONFIG`, and DMA packet formats differ between R600/RV770/Evergreen/NI/SI/CIK, so copy-paste changes can silently target the wrong generation.
- The header includes generated-style register macros alongside hand-written aliases. Inconsistent use can obscure whether a field is fully masked, clear-masked, or simply shifted.

## Test signals

- Build coverage: all Radeon files including `evergreend.h` must compile for Evergreen/Northern Islands configs.
- Ring tests: successful CP and DMA ring tests validate `PACKET3`, DMA packet constants, ring control registers, and fence/trap packet encodings.
- Display tests: hotplug, vblank, page-flip, HDMI audio, and mode-setting exercises validate DCE, AFMT, HPD, FMT, and interrupt offsets.
- VM/IB tests: GPU VM enable/disable, indirect buffer submission, and command parser validation exercise `VM_CONTEXT*`, `VM_L2*`, and PM4 packet range constants.
- Thermal/DPM debugfs and temperature reporting validate `CG_THERMAL_*` encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_dpm.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_dpm.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_smc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_smc.c

## Purpose

`kv_smc.c` implements the low-level SMU/SMC communication primitives used by Kaveri DPM. It sends messages to the SMU, reads the current enabled SCLK DPM mask, sends parameterized messages, reads aligned dwords from SMC SRAM, toggles DPM and BAPM, and copies arbitrary byte ranges into SMC SRAM while preserving surrounding bytes for unaligned writes.

## Important APIs and functions

- `kv_notify_message_to_smu(struct radeon_device *rdev, u32 id)`: writes a message ID to `SMC_MESSAGE_0`, polls `SMC_RESP_0` until a response appears or `rdev->usec_timeout` expires, and maps response values `0xff` and `0xfe` to `-EINVAL`.
- `kv_dpm_get_enable_mask(struct radeon_device *rdev, u32 *enable_mask)`: sends `PPSMC_MSG_SCLKDPM_GetEnabledMask` and reads `SMC_SYSCON_MSG_ARG_0` through `RREG32_SMC()` on success.
- `kv_send_msg_to_smc_with_parameter(struct radeon_device *rdev, PPSMC_Msg msg, u32 parameter)`: writes the parameter to `SMC_MSG_ARG_0`, then sends the message.
- `kv_set_smc_sram_address()`: static bounds/alignment helper that rejects unaligned dword addresses and addresses beyond the provided SRAM limit, then programs `SMC_IND_INDEX_0` and clears auto-increment through `SMC_IND_ACCESS_CNTL`.
- `kv_read_smc_sram_dword()`: sets an aligned SRAM address and reads `SMC_IND_DATA_0`.
- `kv_smc_dpm_enable()` and `kv_smc_bapm_enable()`: message wrappers for enabling/disabling DPM and BAPM.
- `kv_copy_bytes_to_smc()`: writes byte buffers into SMC SRAM, handling unaligned leading and trailing bytes with read-modify-write and writing full dwords in big-endian SMC byte order.

## Control flow

SMU message flow is synchronous: write message or parameter, poll for nonzero response one microsecond at a time up to `rdev->usec_timeout`, then return success unless the final response is one of the explicit error values. Parameterized messages write `SMC_MSG_ARG_0` before entering the same notify flow.

SMC SRAM access first validates a caller-provided firmware limit. Reads require a dword-aligned address. Writes accept arbitrary byte offsets and lengths but reject ranges where `smc_start_address + byte_count` exceeds the limit. For an unaligned start, the function backs up to the containing dword, reads original data, constructs a merged big-endian dword preserving untouched bytes, and writes it back. It then writes full aligned dwords in a loop. If trailing bytes remain, it reads the final dword, shifts the new bytes into the high-order SMC byte lanes, preserves untouched low-order bytes, and writes back.

## State and persistence behavior

This file does not allocate memory or keep driver-private state. It mutates hardware and firmware-visible state by writing SMU mailbox registers and SMC SRAM through indirect access registers. The copied bytes persist in SMC SRAM until overwritten by the driver or firmware reset. Since auto-increment is disabled before each indirect access, callers get deterministic single-address dword writes rather than streaming side effects.

## Dependencies and integration points

- Includes `radeon.h` for `struct radeon_device`, MMIO macros, delays, and timeout fields.
- Includes `cikd.h` for SMC mailbox/indirect register offsets and response masks.
- Includes `kv_dpm.h` for exported prototypes and `PPSMC_Msg` typing.
- Used heavily by `kv_dpm.c` to read firmware header pointers, upload SMU7 Fusion DPM tables, toggle feature bits, set enabled masks, power-gate media blocks, and control DPM/BAPM/CAC/ULV/NB DPM.

## Risks and edge cases

- Timeout handling is weak: if the response never becomes nonzero, the final response is zero and the function returns success. This can mask SMU non-response unless callers detect later state failures.
- Only `0xff` and `0xfe` are treated as errors; other unexpected non-1 response values return success.
- `smc_start_address + byte_count` is checked with 32-bit arithmetic and could theoretically wrap before comparison if impossible values are passed.
- Unaligned copy logic is byte-order sensitive. The code assumes SMC SRAM dword layout is big-endian and manually packs bytes accordingly.
- The helper disables auto-increment on every address set, so future changes that assume bulk auto-increment writes would not work without changing this contract.
- No locking is performed here; callers must serialize SMU mailbox and indirect SRAM access at a higher level if concurrent paths are possible.

## Test signals

- DPM enable success is the primary functional test because it depends on firmware header reads and multiple table uploads.
- Forced performance level changes exercise parameterized SMU messages and enabled-mask reads.
- BAPM toggling across AC/battery transitions validates `kv_smc_bapm_enable()`.
- Boundary tests around `kv_copy_bytes_to_smc()` should include aligned writes, unaligned leading writes, trailing byte writes, zero-length writes, and limit rejection.
- Hardware debug should confirm that SMU response timeouts are not silently accepted in problematic firmware cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/mkregtable.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/mkregtable.c

## Purpose

`mkregtable.c` is a small userspace build utility that converts an authorization/register-list text file into a C static bitmap table named `<gpu_prefix>_reg_safe_bm`. The generated table marks unsafe or disallowed register offsets for Radeon command parser validation. It includes a minimal userspace copy of Linux list helpers so it can collect offsets without depending on kernel headers.

## Important APIs, types, and functions

- Embedded list primitives: `struct list_head`, `INIT_LIST_HEAD()`, `__list_add()`, `list_add_tail()`, `list_entry()`, and `list_for_each_entry()` provide just enough doubly linked list behavior for offset collection.
- `struct offset`: stores one parsed register offset and a list node.
- `struct table`: owns the offset list, maximum offset, bitmap entry count, allocated bitmap pointer, and GPU prefix used in generated symbol names.
- `offset_new()`: allocates and initializes one offset node.
- `table_offset_add()`: appends a parsed offset to the table list.
- `table_init()`: initializes an empty table.
- `table_build()`: allocates the bitmap, initializes all entries to `0xffffffff`, and toggles bits corresponding to listed offsets using `t->table[i] ^= m`.
- `table_print()`: emits the generated static `unsigned` array to stdout, four entries per line.
- `parser_auth()`: opens and parses the auth file, extracts the first-line GPU name and last-register value, scans subsequent lines with a POSIX regex, records offsets, updates `offset_max`, and builds the bitmap.
- `main()`: validates the single input argument, runs parser/build, prints generated output, and returns nonzero on failure.

## Control flow

The program expects exactly one argument: an auth file path. It initializes a `struct table`, then `parser_auth()` compiles a regex matching a hex offset followed by a symbolic name, opens the file, reads its first line as `<gpu_name> <last_reg>`, stores the GPU name in a global buffer, and converts the last-register string to an integer. It then loops through the rest of the file until `ftell(file) == end`, applies the regex to each line, parses matching offsets with `strtol()`, allocates `struct offset` entries, appends them, and tracks the maximum offset seen. After parsing, it ensures `offset_max` is at least the declared last register and calls `table_build()`. Finally, `table_print()` writes a C initializer to stdout.

The bitmap size is computed as `((offset_max >> 2) + 31) / 32`, meaning one bit per 4-byte register slot. Starting from all ones, each listed offset flips one bit to zero. The generated table therefore encodes allowed/blocked status by bit position according to the command parser's expected convention.

## State and persistence behavior

Program state is in heap allocations for the offset list and table bitmap plus the global `gpu_name[10]` buffer. No output file is written directly; generated C is printed to stdout for the build system or caller to redirect. The program does not free allocations before exit, which is acceptable for a short-lived generator but relevant for leak checkers.

## Dependencies and integration points

- Uses userspace C/POSIX headers: `sys/types.h`, `stdlib.h`, `string.h`, `stdio.h`, `regex.h`, and `libgen.h` (`libgen.h` appears unused).
- Intended to run during driver source generation/build workflows that transform register auth files into command-parser safe-bitmask tables.
- The generated symbol name depends on the first token of the auth file, so downstream C code must reference the matching `<gpu_prefix>_reg_safe_bm` name.
- Register offset semantics align with Radeon command parser validation, where packet parsers need fast tests for safe register writes.

## Risks and edge cases

- `table_build()` uses XOR to clear bits. Duplicate offsets toggle the same bit twice, turning it back to one, so duplicate auth entries can corrupt the generated safety table.
- Offset nodes and bitmap memory are never freed. This is harmless for normal one-shot use but noisy under sanitizers.
- `regcomp()` resources are not released with `regfree()`, and several failure paths do not close all resources consistently after regex compilation.
- The parser uses a fixed 1024-byte input buffer and simple regex; long lines are truncated and malformed first lines can produce misleading GPU prefix or last-register values.
- `gpu_name[10]` and `%9s` limit the generated prefix to nine characters, which may truncate longer GPU names and change symbol names.
- Error handling after `offset_new()` is missing. A failed allocation is passed to `table_offset_add()` and would dereference NULL.
- `argc` failures call `exit(1)`, while parse failures return `-1` from `main()`, resulting in shell status 255.

## Test signals

- Compile the utility with host CFLAGS and regex library support.
- Run it on representative auth files and compare generated arrays against checked-in expected tables.
- Include duplicate-offset, empty-file, malformed-header, long-line, and high-last-register fixtures to validate parser and bitmap behavior.
- Downstream command parser tests should reject unsafe register writes and accept known-safe writes using the generated bitmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/mkregtable.c -->
