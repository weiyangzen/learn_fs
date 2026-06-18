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
