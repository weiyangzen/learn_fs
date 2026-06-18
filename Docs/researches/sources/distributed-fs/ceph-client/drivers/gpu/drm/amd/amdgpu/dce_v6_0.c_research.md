# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.c

## Purpose

`dce_v6_0.c` implements the AMDGPU legacy display backend for Display Controller Engine 6.x hardware, primarily Southern Islands family devices such as Tahiti, Pitcairn, Verde, and Oland. It performs the same broad role as later DCE backends: IP block registration, DRM CRTC/encoder helper setup, HPD/vblank/pageflip IRQs, scanout and cursor programming, watermark/line-buffer allocation, HDMI/DP audio programming, suspend/resume, and soft reset.

This file is register-level code using DCE6/SI-era register definitions and masks. Compared with DCE10, it uses older mask-style register programming in many places, supports fewer resources on Oland, has paired line-buffer allocation, supports DP audio in the AFMT path, and exposes DCE 6.0 and 6.4 IP descriptors through one implementation.

## Important APIs, Types, and Tables

- `const struct amdgpu_ip_block_version dce_v6_0_ip_block` and `dce_v6_4_ip_block` export DCE 6.0/6.4 descriptors with shared `dce_v6_0_ip_funcs`.
- `dce_v6_0_disable_dce(struct amdgpu_device *adev)` is the exported disable helper. It disables VGA render and clears CRTC master enables when ATOM BIOS reports DCE engine info.
- `dce_v6_0_display_funcs` installs display hooks for bandwidth, vblank counter, backlight, HPD, pageflip, scanout position, encoder add, and connector add.
- `dce_v6_0_crtc_funcs`, `dce_v6_0_crtc_helper_funcs`, and `dce_v6_0_drm_primary_plane_helper_funcs` integrate DCE6 CRTCs, cursor, gamma, pageflip, vblank, mode-setting, scanout buffer, and panic flush with DRM.
- `dce_v6_0_dig_helper_funcs`, `dce_v6_0_dac_helper_funcs`, and `dce_v6_0_ext_helper_funcs` cover digital, DAC, and pass-through external encoders.
- `dce_v6_0_crtc_irq_funcs`, `dce_v6_0_pageflip_irq_funcs`, and `dce_v6_0_hpd_irq_funcs` populate AMDGPU IRQ source structures.
- Offset tables include six CRTC offsets, six HPD offsets, seven DIG offsets, and six interrupt status mappings. DCE6 initializes six CRTCs/HPDs/DIGs for Tahiti/Pitcairn/Verde and two for Oland.
- `struct dce6_wm_params` captures display watermark inputs: memory/display clocks, DRAM channels, active/blank time, source width, scaler state, head count, bytes per pixel, line-buffer size, and vertical taps.

## Control Flow

`dce_v6_0_early_init()` installs audio endpoint accessors and display funcs, derives `num_crtc`, sets ASIC-specific topology, and installs IRQ funcs. Tahiti/Pitcairn/Verde get six CRTCs, six HPDs, and six DIG blocks; Oland gets two each. Unsupported ASICs return `-EINVAL`.

`dce_v6_0_sw_init()` registers legacy CRTC IRQ IDs, pageflip IRQ IDs 8..18 step 2, and HPD source ID 42; sets DRM mode_config limits and flags; creates display properties; allocates CRTCs; loads connector info from the ATOM object table; allocates AFMT blocks; initializes audio pins; initializes DRM vblank; creates pre-DCE11 hotplug work; and starts KMS polling. `sw_fini()` frees hardcoded EDID, stops polling, tears down audio/AFMT, cleans DRM mode config, and clears `mode_config_initialized`.

`dce_v6_0_hw_init()` disables VGA render, initializes digital PHYs and display engine PLL through ATOM BIOS helpers, initializes HPD, disables all audio pins, and enables pageflip interrupts. `hw_fini()` disables HPD, audio pins, pageflip interrupts, and flushes hotplug work. Suspend/resume wrap AMDGPU display helpers, save/restore backlight register state, and rebuild hardware state.

CRTC mode setting mirrors the DCE10 path. `mode_fixup()` binds encoder/connector, applies scaling fixups, prepares PLL data, and chooses a PPLL. DCE6 uses PPLL0 for DP when no external DP clock is used, and only PPLL1/PPLL2 are allocated for non-DP modes. `mode_set()` programs PLL/timing, sets scanout base, overscan/scaler, cursor reset, and saved hardware mode. `prepare()` disables powergating and locks the CRTC; `commit()` enables DPMS and unlocks.

`dce_v6_0_crtc_do_set_base()` pins the framebuffer BO in contiguous VRAM, converts DRM formats into DCE6 GRPH format/depth fields, programs tiling and pipe config, disables VGA, writes scanout addresses, format/swap, LUT bypass for 10-bpc formats, viewport and desktop size, enables GRPH, unpins the old framebuffer when required, and triggers bandwidth recalculation.

Display watermark flow uses paired line buffers. `dce_v6_0_bandwidth_update()` counts enabled heads, then processes CRTCs in pairs. `dce_v6_0_line_buffer_adjust()` assigns half or whole line buffer depending on whether the paired CRTC has a mode and waits for DMIF buffer allocation completion. `dce_v6_0_program_watermarks()` computes high/low clock watermarks, priority marks, and `PRIORITY_A_CNT`/`PRIORITY_B_CNT`, then writes DPG urgency controls.

Audio/AFMT programming supports HDMI and DP. `dce_v6_0_afmt_setmode()` locates the encoder connector, obtains an audio pin, disables audio, mutes HDMI GC, writes speaker allocation/SAD/latency fields, programs DTO/ACR/VBI for HDMI or DTO for DP, writes packet/channel status and AVI infoframe state, unmutes, enables HDMI or DP secondary stream/audio packets, and finally enables the audio pin.

Interrupt handlers acknowledge CRTC vblank/vline status, route enabled vblank events into DRM, clear pageflip status and send pageflip events, schedule BO unpin work, and schedule hotplug work for HPD. Vline IRQ state programming is a stub even though the IRQ type table includes vline entries.

## State and Persistence Behavior

The file mutates `adev->mode_info` topology, display funcs, CRTC pointers, AFMT pointers, audio pin state, mode_config state, and saved backlight level. Per-CRTC persistent state includes offsets, PLL assignment, current encoder/connector, cursor BO/address/dimensions/hotspot/position, line time, line-buffer lead lines, and saved mode.

AFMT state is dynamically allocated per DIG block and persists until `afmt_fini()`. Audio pin state is initialized from ASIC topology and updated by endpoint reads. Framebuffer and cursor BOs are pinned while displayed and explicitly unpinned on replacement or disable. Hardware register state is reconstructed on mode set, resume, or reset rather than stored in a separate software shadow.

## Dependencies and Integration Points

DCE6 depends on DRM mode-setting helpers, AMDGPU display helpers, ATOM BIOS CRTC/encoder/backlight/PLL helpers, AMDGPU BO/GEM APIs, AMDGPU DPM clocks, AMDGPU IRQ registration, EDID/SAD/speaker parsing, HDMI infoframe helpers, and Southern Islands/DCE6 register headers such as `sid.h`, `dce_6_0_*`, `gmc_6_0_*`, `oss_1_0_*`, and `si_enums.h`.

It integrates with AMDGPU through `amd_ip_funcs` and `amdgpu_display_funcs`, with DRM through CRTC/encoder/plane helpers, with KMS polling/hotplug through delayed work, and with display audio through `adev->reg.audio_endpt` index/data register accessors protected by `audio_endpt.lock`.

## Risks and Edge Cases

- `dce_v6_0_pageflip_irq()` reads `adev->mode_info.crtcs[crtc_id]` before validating `crtc_id`, so an unexpected interrupt source can index outside valid CRTC state.
- `dce_v6_0_bandwidth_update()` iterates CRTCs in pairs and dereferences `crtcs[i+1]`. Current supported topologies are even-numbered, but future changes to `num_crtc` would need to preserve that invariant.
- Watermark math divides by available bandwidth, display clock, source width, and head count. Enabled modes with invalid clocks or memory-clock data could produce divide-by-zero or unrealistic urgency/priority marks.
- `dce_v6_0_set_crtc_vline_interrupt_state()` is empty while vline IRQ types are exposed; vline enable/disable requests do not program hardware.
- DCE6 has ASIC-specific resource counts. Oland has two CRTCs/HPDs/DIGs and two audio pins, while other SI devices use six; tests must cover both paths.
- AFMT/audio setup often exits early on missing connector, missing pin, or failed EDID parsing. This avoids crashes but can leave display active without audio.
- `is_idle()` always returns true and clock/power gating callbacks are stubs, so runtime power-management correctness depends on higher-level sequencing and ATOM BIOS helpers.

## Test Signals

Validation should cover probe on Tahiti/Pitcairn/Verde and Oland, connector enumeration from ATOM object tables, six-head and two-head topologies, HPD plug/unplug, vblank enable/disable, vline behavior expectations, async and vblank pageflip completion, suspend/resume with backlight restoration, HDMI audio and DP audio, EDID speaker/SAD/latency parsing, 6/8/10-bpc formats, 10-bpc LUT bypass, tiled framebuffer scanout, cursor set/move/hide/reset, line-buffer pairing with adjacent CRTCs, DPM clock-driven watermark changes, and display soft reset when HV counters stop changing.
