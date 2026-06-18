# Research: subset-b-001329

Grouped research for AMDGPU DCE 8.x display code, Data Fabric revisions, and small ASIC register-init stubs. Each section is bounded for deterministic reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.c

## Purpose

This file implements the legacy DCE 8.x display engine support used by the AMDGPU driver for CIK/Kaveri/Kabini/Mullins-era ASICs. It wires a DCE IP block into the AMDGPU IP lifecycle, implements DRM CRTC and encoder helpers, handles hotplug, vblank, vline, and page-flip interrupts, programs scanout surfaces, cursors, color LUTs, watermarks, HDMI audio/AFMT packets, pixel PLL selection, and exposes `amdgpu_display_funcs` callbacks for the rest of the driver.

The file is not just a register table. It is the legacy modesetting implementation for this display generation and relies heavily on AtomBIOS helpers for PLLs, encoders, CRTC timing, panel power, backlight, overscan, and scaling.

## Important APIs, Types, and Functions

Key exported API:

- `dce_v8_0_disable_dce()` disables VGA render and enabled CRTCs when firmware/early boot needs DCE quiesced.
- `dce_v8_0_ip_block`, `dce_v8_1_ip_block`, `dce_v8_2_ip_block`, `dce_v8_3_ip_block`, and `dce_v8_5_ip_block` publish DCE IP block versions backed by the same `dce_v8_0_ip_funcs`.

Important local tables and structs:

- `crtc_offsets`, `hpd_offsets`, and `dig_offsets` map logical CRTCs, HPD pins, and DIG/AFMT blocks to register offsets.
- `interrupt_status_offsets` maps each display pipe to its vblank, vline, and HPD status bits.
- `struct dce8_wm_params` packages display timing, memory clock, scaling, line-buffer, and DRAM-channel data for watermark calculations.

Display lifecycle callbacks:

- `dce_v8_0_early_init()` installs audio endpoint register accessors, display funcs, IRQ funcs, and derives CRTC/HPD/DIG counts by ASIC type.
- `dce_v8_0_sw_init()` registers IRQ IDs, initializes DRM mode config, allocates CRTCs, parses AtomBIOS connector data, allocates AFMT blocks, initializes audio pins, initializes vblank, and starts KMS polling.
- `dce_v8_0_hw_init()` disables VGA render, initializes DIG PHYs and display engine PLL, enables HPD, disables all audio pins, and enables pageflip IRQ refs.
- `dce_v8_0_hw_fini()`, `dce_v8_0_suspend()`, and `dce_v8_0_resume()` tear down HPD/pageflip/audio state, save/restore backlight, and invoke common display suspend/resume helpers.
- `dce_v8_0_soft_reset()` detects a hung display by watching CRTC HV counters and toggles `SRBM_SOFT_RESET__SOFT_RESET_DC_MASK` when needed.

CRTC and scanout:

- `dce_v8_0_crtc_init()` allocates `struct amdgpu_crtc`, registers DRM CRTC funcs/helpers, sets cursor dimensions, gamma size, offsets, and primary-plane helpers.
- `dce_v8_0_crtc_do_set_base()` pins the framebuffer in contiguous VRAM, maps DRM formats and tiling flags to GRPH registers, programs surface address, pitch, viewport, GRPH control, LUT bypass for 10-bit scanout, and updates watermarks.
- `dce_v8_0_crtc_mode_fixup()`, `dce_v8_0_crtc_mode_set()`, `dce_v8_0_crtc_dpms()`, `dce_v8_0_crtc_disable()`, and `dce_v8_0_crtc_set_base()` coordinate PLL choice, AtomBIOS timing/scaler programming, DPMS, page blanking, PPLL shutdown, and framebuffer unpinning.
- `dce_v8_0_crtc_load_lut()` programs color pipeline bypasses and the 256-entry DC LUT from `crtc->gamma_store`.
- Cursor handlers `dce_v8_0_crtc_cursor_set2()`, `dce_v8_0_crtc_cursor_move()`, `dce_v8_0_cursor_reset()`, `dce_v8_0_show_cursor()`, and `dce_v8_0_hide_cursor()` pin cursor BOs, program cursor position/hotspot/size/address, and use the hardware cursor update lock.

Watermarks and bandwidth:

- `dce_v8_0_line_buffer_adjust()` allocates line-buffer partitions and DMIF buffers based on mode width and APU/discrete behavior.
- `cik_get_number_of_dram_channels()` decodes `MC_SHARED_CHMAP`.
- `dce_v8_0_dram_bandwidth()`, `dce_v8_0_dram_bandwidth_for_display()`, `dce_v8_0_data_return_bandwidth()`, `dce_v8_0_dmif_request_bandwidth()`, `dce_v8_0_available_bandwidth()`, `dce_v8_0_average_bandwidth()`, `dce_v8_0_latency_watermark()`, and the check helpers compute DPG urgency watermark values using `fixed20_12` math.
- `dce_v8_0_bandwidth_update()` counts active heads, adjusts line buffers, programs watermarks, and stores DPM-facing line timing.

HDMI/AFMT audio:

- `dce_v8_0_audio_endpt_rreg()` and `_wreg()` serialize endpoint-index/data accesses under `adev->reg.audio_endpt.lock`.
- `dce_v8_0_audio_init()` detects pin count by ASIC, initializes pin metadata, and disables audio pins.
- `dce_v8_0_afmt_init()` allocates `amdgpu_afmt` blocks per DIG encoder, and `_fini()` frees them.
- `dce_v8_0_afmt_enable()` tracks AFMT enabled state and detaches pins on disable.
- `dce_v8_0_afmt_setmode()` selects an audio pin, programs DTO, HDMI control, audio packets, ACR, channel status, EDID-derived speaker allocation/SAD/lipsync fields, AVI infoframes, ramp control, and finally enables audio.

Encoder and connector integration:

- `dce_v8_0_encoder_add()` creates AMDGPU encoders from AtomBIOS object IDs, merges duplicate encoder enums, chooses DRM encoder type, initializes DIG/LCD private data, sets possible CRTCs, and attaches helper funcs.
- `dce_v8_0_encoder_prepare()`, `_mode_set()`, `_commit()`, and `_disable()` perform scratch-locking, I2C router selection, eDP panel power, CRTC source routing, FMT programming, AtomBIOS DPMS, AFMT HDMI setup, and DIG encoder bookkeeping.
- `dce_v8_0_pick_dig_encoder()` and `dce_v8_0_pick_pll()` assign DIG and PPLL resources.

Interrupt handling:

- `dce_v8_0_set_crtc_irq_state()`, `dce_v8_0_set_pageflip_irq_state()`, and `dce_v8_0_set_hpd_irq_state()` manipulate LB, GRPH, and HPD interrupt masks.
- `dce_v8_0_crtc_irq()` acknowledges vblank/vline status and dispatches DRM vblank.
- `dce_v8_0_pageflip_irq()` clears GRPH pflip status, validates flip state, sends the event, drops the vblank ref, and schedules unpin work.
- `dce_v8_0_hpd_irq()` acknowledges HPD and schedules `adev->hotplug_work`.

## Control Flow and State

Driver setup flows from IP discovery into `early_init`, which installs callback tables and derives hardware counts. `sw_init` then creates DRM-facing objects and software state; `hw_init` programs physical display hardware. Modesets flow through DRM helper callbacks: mode fixup caches encoder/connector and chooses a PLL, prepare powers and locks the CRTC path, mode set programs PLL/timing/surface/scaler/cursor, and commit re-enables DPMS and unlocks scratch registers. Shutdown and suspend reverse this ordering and release IRQ references, BO pins, AFMT allocations, and KMS polling state.

Persistent driver state is held in `adev->mode_info`, per-CRTC `struct amdgpu_crtc`, per-encoder DIG private structures, `adev->mode_info.audio.pin[]`, and `adev->mode_info.afmt[]`. Hardware-visible persistence includes VRAM-pinned framebuffer and cursor BOs, CRTC/GRPH/LB/DPG/AFMT registers, HPD polarity and interrupt enables, and saved backlight level across suspend.

## Dependencies and Integration Points

The file depends on DRM core mode configuration, vblank, EDID/HDMI helpers, AMDGPU BO management, AtomBIOS display helpers, AMDGPU IRQ routing, AMDGPU DPM clock APIs, connector helpers, register accessor macros, and generated DCE/GMC/OSS register headers. It integrates with common AMDGPU display code through `adev->mode_info.funcs`, with the IP block manager through `amd_ip_funcs`, with IRQ dispatch through `amdgpu_irq_src_funcs`, and with panic scanout through primary-plane `panic_flush`.

## Risks and Edge Cases

High-risk areas are BO pin/unpin lifetime during base changes and cursor replacement, pageflip state transitions under `event_lock`, AFMT pin allocation when no connected audio pins exist, EDID parsing failures, PPLL sharing decisions, HPD interrupt storms on internal panels, register programming order around CRTC locks, and watermark arithmetic divisions using clocks/bandwidth values. The code also has legacy assumptions: no framebuffer modifiers, hard-coded bytes-per-pixel for watermark calculations, fixed DCE8 hardware limits, and AtomBIOS dependency for many operations.

## Test Signals

Useful validation includes boot and resume on all supported ASIC families; connector hotplug including eDP/LVDS no-storm behavior; vblank/pageflip event tests; cursor movement and replacement tests including oversized rejection; 8/10-bit framebuffer scanout and LUT bypass checks; HDMI audio ELD/SAD/speaker allocation behavior; multi-monitor PLL sharing; DP external-clock paths; suspend/resume backlight restore; panic scanout flush; and fault injection for BO pin failures, missing EDID, no audio pins, and unsupported formats.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.h

## Purpose

This header publishes the DCE 8.x IP block descriptors and the one externally callable helper for disabling the DCE engine. It is the public include boundary for other AMDGPU source files that need to register or quiesce this display generation without depending on the large implementation file.

## Important APIs and Types

- `extern const struct amdgpu_ip_block_version dce_v8_0_ip_block`
- `extern const struct amdgpu_ip_block_version dce_v8_1_ip_block`
- `extern const struct amdgpu_ip_block_version dce_v8_2_ip_block`
- `extern const struct amdgpu_ip_block_version dce_v8_3_ip_block`
- `extern const struct amdgpu_ip_block_version dce_v8_5_ip_block`
- `void dce_v8_0_disable_dce(struct amdgpu_device *adev)`

The declarations assume consumers already have visibility of `struct amdgpu_device` and `struct amdgpu_ip_block_version` through normal AMDGPU include ordering.

## Control Flow and State

The header carries no runtime state. Its declarations let ASIC discovery tables bind a DCE revision to the common DCE8 implementation, and let early ASIC code call `dce_v8_0_disable_dce()` before or outside normal DRM modeset setup.

## Dependencies and Integration Points

The guard macro `__DCE_V8_0_H__` protects inclusion. Integration is with AMDGPU IP block assembly and legacy display initialization. The implementation side is `dce_v8_0.c`.

## Risks and Test Signals

The main risk is declaration drift: any change to IP block symbol names or the disable helper signature must remain synchronized with users and `dce_v8_0.c`. Build coverage across DCE 8.0, 8.1, 8.2, 8.3, and 8.5 ASIC tables is the primary signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v1_7.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v1_7.c

## Purpose

This file implements Data Fabric 1.7 callbacks for AMDGPU. It initializes DF software hash-status defaults, provides broadcast-mode control, decodes framebuffer/HBM channel interleave fields, manages medium-grain clock gating, reports clock-gating state, and exposes an ECC parity write read-modify-write control hook.

## Important APIs and Functions

- `df_v1_7_sw_init()` clears `adev->df.hash_status.hash_64k`, `hash_2m`, and `hash_1g`.
- `df_v1_7_sw_fini()` is a no-op placeholder for the DF callback table.
- `df_v1_7_enable_broadcast_mode()` toggles `FabricConfigAccessControl__CfgRegInstAccEn` or restores `mmFabricConfigAccessControl_DEFAULT`.
- `df_v1_7_get_fb_channel_number()` reads `mmDF_CS_AON0_DramBaseAddress0` and extracts `IntLvNumChan`.
- `df_v1_7_get_hbm_channel_number()` maps the encoded interleave value through `df_v1_7_channel_number[]`.
- `df_v1_7_update_medium_grain_clock_gating()` enters broadcast mode, writes `DF_PIE_AON0_DfGlobalClkGater.MGCGMode`, and exits broadcast mode.
- `df_v1_7_get_clockgating_state()` reports `AMD_CG_SUPPORT_DF_MGCG` if the 15-cycle MGCG mode is present.
- `df_v1_7_enable_ecc_force_par_wr_rmw()` uses `WREG32_FIELD15` to set `ForceParWrRMW`.
- `df_v1_7_funcs` binds these operations into `struct amdgpu_df_funcs`.

## Control Flow and State

Initialization only resets software hash flags. Runtime operations are direct register reads/writes through SOC15 macros. Broadcast mode is used as a temporary register-access mode around MGCG updates, and the code restores the default access-control register afterward. The persistent state is hardware register state plus the hash-status booleans in `adev->df`.

## Dependencies and Integration Points

The file depends on `amdgpu.h`, `df_v1_7.h`, and generated DF 1.7 default/offset/mask headers. It is consumed through `adev->df.funcs`, so higher-level AMDGPU power, memory, RAS, and clock-gating paths can call revision-specific DF behavior without knowing register details.

## Risks and Test Signals

Risks include incorrect interleave-to-channel mapping, leaving broadcast mode enabled after MGCG programming, failing to honor `AMD_CG_SUPPORT_DF_MGCG`, and register field drift against generated headers. Tests should verify reported HBM channel counts, clock-gating enable/disable and state reporting, ECC force-parity write behavior, and suspend/resume or power-management paths that repeatedly toggle DF MGCG.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v1_7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v1_7.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v1_7.h

## Purpose

This header declares the DF 1.7 callback table and defines the MGCG mode enumeration used when programming `DfGlobalClkGater.MGCGMode`.

## Important APIs and Types

- `enum DF_V1_7_MGCG` defines disabled mode and enable delays of 0, 1, 15, 31, and 63 cycles.
- `extern const struct amdgpu_df_funcs df_v1_7_funcs` exposes the implementation table from `df_v1_7.c`.

## Control Flow and State

The header has no runtime state. Its enum constants are written into hardware by `df_v1_7_update_medium_grain_clock_gating()`, and the exported callback table is selected by ASIC setup code.

## Dependencies and Integration Points

It includes `soc15_common.h` for SOC15-oriented types/macros expected by the implementation. Integration is through AMDGPU DF function dispatch.

## Risks and Test Signals

Risks are limited to enum/register encoding mismatch and callback declaration drift. Build coverage plus clock-gating register readback on DF 1.7 hardware are the key signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v1_7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v3_6.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v3_6.c

## Purpose

This file implements Data Fabric 3.6 operations for AMDGPU. In addition to the channel-count and clock-gating helpers seen in earlier DF revisions, it supports DF fabric indirect config access, perfmon counter assignment/start/stop/read flows, a sysfs counter-availability attribute, memory-hash status querying, and RAS poison-mode detection.

## Important APIs and Functions

Fabric indirect config access:

- `df_v3_6_get_fica()` and `df_v3_6_set_fica()` access FICA address/data registers through NBIO-provided PCIe index/data offsets. They serialize the index/data sequence with `adev->reg.pcie.lock`.

Perfmon low/high register access:

- `df_v3_6_perfmon_rreg()` reads paired low/high counter registers atomically under the PCIe register lock.
- `df_v3_6_perfmon_wreg()` writes paired low/high registers atomically.
- `df_v3_6_perfmon_arm_with_status()` writes control registers and verifies readback, returning `-EBUSY` on mismatch.
- `df_v3_6_perfmon_arm_with_retry()` retries arming for up to 1 ms in 100 us intervals and returns `-ETIME` on timeout.

Perfmon allocation and operation:

- Config encoding macros split `config` into event, instance, and unitmask fields.
- `df_v3_6_pmc_add_cntr()` allocates one of four visible counters by filling `adev->df_perfmon_config_assign_mask[]`.
- `df_v3_6_pmc_get_addr()` maps assigned counter indexes 0-3 to SMN perfmon control or counter low/high addresses.
- `df_v3_6_pmc_get_ctrl_settings()` translates config fields into control register values and enable bit state.
- `df_v3_6_pmc_start()` either allocates a counter or arms it for Vega20/Arcturus. Failed arming marks the counter deferred.
- `df_v3_6_pmc_stop()` disables a counter and optionally resets/releases it.
- `df_v3_6_pmc_get_count()` rearms deferred counters when possible, reads the 64-bit count, and suppresses overflow sentinel values.

DF feature helpers:

- `df_v3_6_query_hashes()` populates `adev->df.hash_status` for specific Arcturus/Aldebaran interleave encodings.
- `df_v3_6_enable_broadcast_mode()`, `df_v3_6_get_fb_channel_number()`, `df_v3_6_get_hbm_channel_number()`, `df_v3_6_update_medium_grain_clock_gating()`, and `df_v3_6_get_clockgating_state()` mirror revision-specific register handling for broadcast mode, interleave/channel decode, and MGCG.
- `df_v3_6_query_ras_poison_mode()` reads hardware assert mask fields and returns true only when all relevant poison-mode fields are set, warning on inconsistent mixed state.
- `df_v3_6_sw_init()` creates `df_cntr_avail`, clears perfmon assignment masks, and queries hash state.
- `df_v3_6_sw_fini()` removes the sysfs file when the device kobject is live.
- `df_v3_6_funcs` exposes all callbacks.

## Control Flow and State

Software initialization creates a read-only sysfs attribute and initializes `adev->df_perfmon_config_assign_mask[]` to zero. Perfmon flows split into allocation and programming: an add call reserves a logical counter, a start call programs control registers, reads later consult the assignment mask, and stop/remove disables and releases the slot. Deferred arming is persisted by OR-ing `DEFERRED_ARM_MASK` into the assignment mask, so `pmc_get_count()` can retry arming later.

Hardware state is primarily DF registers reached through SOC15 and SMN/PCIe index-data access. Software state includes hash-status booleans and the perfmon assignment mask. Locking around PCIe index/data sequences is essential because low/high register access and indirect FICA access must be atomic with respect to other users of the same index/data aperture.

## Dependencies and Integration Points

The file depends on generated DF 3.6 headers, NBIO funcs for PCIe indirect offsets, Linux device sysfs APIs, AMDGPU DF callback dispatch, RAS code that asks about poison mode, and performance-monitoring users that call `pmc_start`, `pmc_stop`, and `pmc_get_count`. It also branches on ASIC type for Vega20, Arcturus, and Aldebaran-specific behavior.

## Risks and Edge Cases

Key risks are races or corruption if index/data access is not serialized, counter leaks if assignment masks are not released, incorrect handling of deferred arms, overflow sentinel misinterpretation, partial poison-mode settings, mismatched channel-number tables, and sysfs creation/removal lifetime issues. Some callbacks silently do nothing for unsupported ASIC types, so callers must tolerate zero counts or no-op behavior.

## Test Signals

Validation should include sysfs `df_cntr_avail` count changes during perfmon allocation/removal, perfmon start/stop/read on Vega20 and Arcturus, deferred-arm retry behavior under simulated busy hardware, overflow sentinel suppression, FICA read/write serialization, hash-status detection on Arcturus/Aldebaran interleave encodings, RAS poison-mode true/false/inconsistent cases, and MGCG state toggling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v3_6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v3_6.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v3_6.h

## Purpose

This header declares the DF 3.6 callback table and MGCG register encodings used by the implementation. It also declares `df_v3_6_attr_groups`, although the implementation in this source set creates a device attribute directly.

## Important APIs and Types

- `enum DF_V3_6_MGCG` defines disabled mode and enable delays of 0, 1, 15, 31, and 63 cycles.
- `extern const struct attribute_group *df_v3_6_attr_groups[]`
- `extern const struct amdgpu_df_funcs df_v3_6_funcs`

## Control Flow and State

The header carries no mutable state. Its constants are consumed by DF 3.6 clock-gating programming, and its function table declaration lets ASIC setup select DF 3.6 operations.

## Dependencies and Integration Points

It includes `soc15_common.h` and participates in the AMDGPU DF dispatch interface. Consumers must also see Linux sysfs attribute types if they use the attr-group declaration.

## Risks and Test Signals

Risks include stale `df_v3_6_attr_groups` declarations if no matching definition exists in a build configuration, enum encoding drift, and callback table declaration mismatch. Build/link coverage and MGCG register readback are the primary signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v3_6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_15.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_15.c

## Purpose

This compact DF 4.15 implementation provides a hardware-initialization callback that changes Data Fabric atomic-processing behavior when the device reports atomic support.

## Important APIs and Functions

- `df_v4_15_hw_init()` checks `adev->have_atomics_support`, reads `regNCSConfigurationRegister1`, sets selected `DisIntAtomicsLclProcessing` bits, and writes the register back.
- `df_v4_15_funcs` exposes only `.hw_init`.

The bit mask disables local processing for bit positions 1, 2, and 13 before shifting into the `NCSConfigurationRegister1__DisIntAtomicsLclProcessing` field.

## Control Flow and State

The callback is intended to run during DF hardware initialization. If atomics are not supported, it leaves hardware untouched. If atomics are supported, persistent state is the modified DF register, not software state.

## Dependencies and Integration Points

The file depends on `amdgpu.h`, `df_v4_15.h`, and generated DF 4.15 offset/mask headers. It integrates with ASIC setup through `struct amdgpu_df_funcs`.

## Risks and Test Signals

Risks are wrong bit selection, applying the workaround on unsupported hardware, and register field drift. Test signals include hardware init register readback on DF 4.15 ASICs with and without `have_atomics_support`, plus atomic-operation correctness and regression checks around peer/local atomic routing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_15.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_15.h

## Purpose

This header declares the DF 4.15 function table used by ASIC setup code to attach the revision-specific hardware initialization callback.

## Important APIs and Types

- `extern const struct amdgpu_df_funcs df_v4_15_funcs`

## Control Flow and State

The header has no state. It provides the compile-time symbol used to select the DF 4.15 implementation.

## Dependencies and Integration Points

Unlike older DF headers in this set, it does not include `soc15_common.h`; it only needs a visible `struct amdgpu_df_funcs` declaration from surrounding include context. Integration is with AMDGPU DF callback dispatch.

## Risks and Test Signals

Risks are declaration drift and missing prerequisite type visibility in consumers. Build coverage for DF 4.15 ASIC support is the key signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_3.c

## Purpose

This file implements the DF 4.3 RAS poison-mode query callback. It determines whether Data Fabric poison handling is enabled by checking selected hardware assert mask fields.

## Important APIs and Functions

- `df_v4_3_query_ras_poison_mode()` reads `regDF_CS_UMC_AON0_HardwareAssertMaskLow` and `regDF_NCS_PG0_HardwareAssertMaskHigh`, extracts `HWAssertMsk0`, `HWAssertMsk1`, `HWAssertMsk28`, and `HWAssertMsk31`, and returns true only if all four are set.
- It returns false when all four are clear.
- It warns and returns false when the fields are inconsistent.
- `df_v4_3_funcs` exposes `.query_ras_poison_mode`.

## Control Flow and State

The callback is a read-only hardware query. It maintains no software state and persists nothing. Its only side effect is `dev_warn()` on inconsistent hardware configuration.

## Dependencies and Integration Points

The file depends on generated DF 4.3 register headers and AMDGPU SOC15 register macros. It integrates with AMDGPU RAS paths through the DF callback table.

## Risks and Test Signals

Risks include interpreting mixed hardware assert masks incorrectly, stale register names/fields, and treating inaccessible or transient fields as disabled poison mode. Tests should cover all-set, all-clear, and mixed mask states, plus RAS behavior that depends on poison-mode reporting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_3.h

## Purpose

This header declares the DF 4.3 callback table for AMDGPU Data Fabric dispatch.

## Important APIs and Types

- `extern const struct amdgpu_df_funcs df_v4_3_funcs`

## Control Flow and State

No runtime state is stored here. ASIC setup code uses the declaration to bind DF 4.3 RAS poison-mode behavior.

## Dependencies and Integration Points

It includes `soc15_common.h`, matching the SOC15 register-access style used in `df_v4_3.c`. Integration is through `adev->df.funcs`.

## Risks and Test Signals

Risks are declaration mismatch or missing selection in ASIC setup. Build coverage and a RAS poison-mode query smoke test are useful signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_6_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_6_2.c

## Purpose

This file provides the DF 4.6.2 RAS poison-mode callback. Because the relevant registers are inaccessible on this revision, the implementation reports poison mode as enabled unconditionally.

## Important APIs and Functions

- `df_v4_6_2_query_ras_poison_mode()` returns `true` with an inline note that related registers are inaccessible.
- `df_v4_6_2_funcs` exposes `.query_ras_poison_mode`.

## Control Flow and State

The callback has no register accesses, no software state, and no side effects. Every caller receives the same enabled answer.

## Dependencies and Integration Points

The file depends on `amdgpu.h` and `df_v4_6_2.h`, and integrates with RAS code through `struct amdgpu_df_funcs`.

## Risks and Test Signals

The main risk is semantic: unconditionally returning true may mask hardware or firmware changes where poison mode becomes observable or disabled. Test signals should focus on DF 4.6.2 RAS flows accepting the forced-enabled behavior and on future hardware documentation updates that might require replacing the stub with register reads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_6_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_6_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_6_2.h

## Purpose

This header declares the DF 4.6.2 callback table for AMDGPU Data Fabric dispatch.

## Important APIs and Types

- `extern const struct amdgpu_df_funcs df_v4_6_2_funcs`

## Control Flow and State

The header contains no state. It lets ASIC setup select the DF 4.6.2 RAS poison-mode stub.

## Dependencies and Integration Points

It includes `soc15_common.h` for consistency with SOC15 DF headers, though the implementation does not access registers. Integration is through `adev->df.funcs`.

## Risks and Test Signals

Risks are declaration drift and stale forced-enabled poison-mode semantics. Build coverage and RAS callback smoke tests are sufficient for this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_6_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dimgrey_cavefish_reg_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dimgrey_cavefish_reg_init.c

## Purpose

This file initializes register base offset pointers for the Dimgrey Cavefish ASIC. It maps AMDGPU hardware IP IDs to generated per-instance base-address arrays so SOC15 register access macros can compute the correct offsets.

## Important APIs and Functions

- `dimgrey_cavefish_reg_base_init(struct amdgpu_device *adev)` loops over `MAX_INSTANCE` and fills `adev->reg_offset[HWIP][i]` for GC, HDP, MMHUB, ATHUB, NBIO, MP0, MP1, VCN, DF, DCE/DCN, OSSSYS, SDMA0-3, SMUIO, and THM.
- SDMA0-3 are mapped to `GC_BASE.instance[i]`, which reflects this ASIC's generated offset organization.
- DCE hardware IP is mapped to `DCN_BASE.instance[i]`, indicating display register offsets come from DCN-named generated data for this ASIC.

## Control Flow and State

The function performs deterministic pointer assignment and returns 0. Its persistent effect is `adev->reg_offset`, which later register macros rely on for all per-IP register access. It does not allocate memory or touch hardware registers directly.

## Dependencies and Integration Points

It depends on `amdgpu.h`, `nv.h`, SOC15 common/hardware-IP definitions, and `dimgrey_cavefish_ip_offset.h`. It is called by ASIC initialization before IP blocks use SOC15 register macros.

## Risks and Test Signals

Risks include assigning the wrong generated base array to a HWIP, missing a HWIP used later by the driver, or changing `MAX_INSTANCE` assumptions. Test signals are early boot register access success, absence of invalid offset faults, IP block init success for all mapped hardware blocks, and comparing assigned bases against generated offset headers for this ASIC.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dimgrey_cavefish_reg_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/emu_soc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/emu_soc.c

## Purpose

This file is a minimal emulation-ASIC initialization stub. It provides the `emu_soc_asic_init()` symbol expected by the surrounding AMDGPU ASIC initialization code but performs no setup.

## Important APIs and Functions

- `emu_soc_asic_init(struct amdgpu_device *adev)` returns 0 unconditionally.

## Control Flow and State

There is no control flow beyond immediate success. The function does not inspect `adev`, allocate resources, initialize register offsets, or program hardware. It persists no state.

## Dependencies and Integration Points

The file includes `amdgpu.h`, `soc15.h`, `soc15_common.h`, and `soc15_hw_ip.h`, which indicates it is part of the SOC15 ASIC initialization family even though it currently does nothing. Integration is by symbol call from emulation-platform setup.

## Risks and Test Signals

The risk is that callers may assume this function performed ASIC setup when it did not. It is safe only if emulation paths initialize required state elsewhere or do not need it. Test signals are emulation boot success, absence of later null/zero register-offset usage, and call-site review to confirm a no-op init is intentional.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/emu_soc.c -->
