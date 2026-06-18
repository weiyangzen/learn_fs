# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.c

## Purpose

`dce_v10_0.c` implements the AMDGPU Display Controller Engine 10.x backend used by the legacy non-DC display stack for Tonga/Fiji-era ASICs. It registers the DCE IP block, wires DRM CRTC/encoder helper callbacks, manages hotplug/vblank/pageflip interrupts, programs scanout surfaces, cursors, gamma/LUT state, display watermarks, HDMI audio/AFMT state, and suspend/resume/reset flows.

The file is hardware-facing code: most behavior is direct MMIO through `RREG32`, `WREG32`, `REG_SET_FIELD`, and register-offset tables from `dce_10_0_*`, `oss_3_0_*`, and `gmc_8_1_*` headers. Higher-level policy comes from DRM core, AMDGPU mode-setting helpers, ATOM BIOS helpers, PLL helpers, and power-management clock queries.

## Important APIs, Types, and Tables

- `const struct amdgpu_ip_block_version dce_v10_0_ip_block` and `dce_v10_1_ip_block` export the DCE 10.0/10.1 IP descriptors. Both use `dce_v10_0_ip_funcs`.
- `dce_v10_0_disable_dce(struct amdgpu_device *adev)` is the exported pre-driver/bring-up helper declared in the header. It disables VGA render and any active CRTC masters if ATOM BIOS reports DCE engine info.
- `dce_v10_0_display_funcs` fills `adev->mode_info.funcs` with display callbacks: bandwidth update, vblank counter, backlight accessors, HPD helpers, page flip, scanout position, encoder creation, and connector creation.
- `dce_v10_0_crtc_funcs`, `dce_v10_0_crtc_helper_funcs`, and `dce_v10_0_drm_primary_plane_helper_funcs` integrate DCE CRTCs with DRM legacy helpers, cursor ioctls, gamma, page flip, vblank, mode set, scanout buffer, and panic flush.
- `dce_v10_0_dig_helper_funcs`, `dce_v10_0_dac_helper_funcs`, and `dce_v10_0_ext_helper_funcs` bind encoder mode-setting behavior for digital, DAC, and external encoders.
- `dce_v10_0_crtc_irq_funcs`, `dce_v10_0_pageflip_irq_funcs`, and `dce_v10_0_hpd_irq_funcs` are installed into `adev->{crtc,pageflip,hpd}_irq`.
- Offset tables define the hardware layout: `crtc_offsets` has seven entries but DCE10 initializes six CRTCs for Fiji/Tonga; `hpd_offsets` has six HPD blocks; `dig_offsets` has seven DIG/AFMT offsets; `interrupt_status_offsets` maps the six display interrupt status registers and masks.
- `struct dce10_wm_params` captures watermark inputs: DRAM channels, memory/engine/display clocks, source width, active/blank time, interlace/scaler state, head count, bytes per pixel, line-buffer size, and vertical taps.

## Control Flow

Initialization starts in `dce_v10_0_early_init()`: it installs audio endpoint register accessors, display funcs, derives `num_crtc`, sets DCE10 topology for `CHIP_FIJI` and `CHIP_TONGA` (`num_crtc = 6`, `num_hpd = 6`, `num_dig = 7`), installs IRQ funcs, and rejects unsupported ASICs with `-EINVAL`.

`dce_v10_0_sw_init()` registers CRTC, pageflip, and HPD interrupt source IDs, configures DRM mode limits and properties, creates all CRTCs, obtains connector info from the ATOM object table, allocates AFMT blocks, initializes audio pins, initializes vblank, creates hotplug work, starts KMS polling, and marks mode config initialized. `sw_fini()` tears down EDID, polling, audio, AFMT allocation, and DRM mode config.

`dce_v10_0_hw_init()` programs golden registers for Fiji/Tonga, disables VGA render, initializes digital PHYs and display engine PLL through ATOM BIOS helpers, initializes HPD, disables all audio pins, and enables pageflip interrupts. `hw_fini()` disables HPD and audio, disables pageflip IRQs, and flushes hotplug work. Suspend wraps `amdgpu_display_suspend_helper()`, saves backlight level, and calls hardware fini; resume restores backlight register state, reinitializes hardware, refreshes panel backlight, then calls `amdgpu_display_resume_helper()`.

Mode setting flows through DRM helpers. `dce_v10_0_crtc_mode_fixup()` finds the bound encoder/connector, applies scaling fixups, prepares PLL data, and picks a PPLL. `dce_v10_0_crtc_mode_set()` programs PLL and DTD timing through ATOM BIOS, calls `dce_v10_0_crtc_do_set_base()`, sets overscan/scaler state, restores cursor state, and saves the adjusted mode for DPM. `prepare()` powergates off and locks the CRTC before DPMS off; `commit()` DPMSes on and unlocks.

`dce_v10_0_crtc_do_set_base()` is the scanout programming core. It pins the target framebuffer BO in contiguous VRAM, derives tiling flags and pipe config, maps DRM fourcc formats to GRPH depth/format/crossbar/endian fields, programs tiling fields for 1D/2D tiled surfaces, disables VGA, writes primary/secondary surface addresses, GRPH control and swap, LUT 10-bit bypass for 10-bpc formats, viewport/desktop/pitch registers, enables GRPH, unpins the old framebuffer if needed, and recomputes bandwidth/watermarks.

Encoder setup uses ATOM BIOS for low-level transmitter work. `dce_v10_0_encoder_prepare()` selects DIG/AFMT mapping, locks scratch regs, selects I2C router ports, powers eDP panels when needed, sets CRTC source, and programs FMT dithering/truncation. `dce_v10_0_encoder_mode_set()` stores pixel clock, disables the encoder for setup, restores interlace formatting, and for HDMI enables AFMT and programs audio/infoframes. `commit()` turns DPMS on and unlocks scratch regs. `disable()` turns DPMS off, disables HDMI AFMT, clears the DIG encoder selection, and drops `active_device`.

Interrupt control is split by source. CRTC vblank/vline enable bits are written in `LB_INTERRUPT_MASK`. HPD enable bits are written in `DC_HPD_INT_CONTROL`. Pageflip IRQ masking uses `GRPH_INTERRUPT_CONTROL`. Handlers acknowledge asserted hardware status, feed DRM vblank with `drm_handle_vblank()`, complete pending pageflip work under `event_lock`, schedule BO unpin work, and schedule delayed hotplug work for HPD.

## State and Persistence Behavior

The file mutates long-lived state in `adev->mode_info`: topology counts, `funcs`, `crtcs[]`, `afmt[]`, audio pin metadata, `mode_config_initialized`, hotplug work, saved backlight level, and display priority data. Per-CRTC state includes `crtc_offset`, `pll_id`, `adjusted_clock`, bound encoder/connector, current cursor BO/address/size/hotspot/position, `line_time`, `lb_vblank_lead_lines`, and saved `hw_mode`.

Framebuffer and cursor BOs are pinned in VRAM while used for scanout/cursor display and unpinned during replacement or CRTC disable. Pageflip completion state is held in `amdgpu_crtc->pflip_status` and `pflip_works`, protected by the DRM event lock. AFMT state persists in allocated `struct amdgpu_afmt` entries and attached audio pins until disabled or freed.

Hardware state persists in DCE registers across normal execution and is reconstructed on resume or mode set. The code relies on ATOM BIOS helpers for persistent platform details such as connector object tables, panel backlight, PLL/transmitter setup, spread spectrum, and eDP power sequencing.

## Dependencies and Integration Points

Primary dependencies are DRM core/helper APIs, AMDGPU display abstractions, ATOM BIOS CRTC/encoder helpers, AMDGPU PLL helpers, AMDGPU BO/GEM memory management, DPM clock queries, EDID/SAD/speaker allocation parsing, IRQ source registration, and DCE10 register headers. The file is integrated into the AMDGPU IP block framework through `amd_ip_funcs`, and into DRM KMS through mode_config, CRTC, plane, and encoder callbacks.

The audio path depends on `adev->reg.audio_endpt` indirection and the global `amdgpu_audio` option. Audio endpoint MMIO index/data pairs are protected by `adev->reg.audio_endpt.lock`. HDMI audio setup depends on EDID-derived SAD/speaker/latency data and DRM HDMI infoframe packing.

## Risks and Edge Cases

- `dce_v10_0_pageflip_irq()` computes `amdgpu_crtc = adev->mode_info.crtcs[crtc_id]` before checking whether `crtc_id >= num_crtc`; malformed or unexpected interrupt source IDs could index outside valid CRTC state.
- Watermark math divides by `available_bandwidth`, `disp_clk`, `num_heads`, and `src_width` in several paths. Most callers only enter the full path for enabled CRTCs and nonzero head count, but zero or corrupt clock/bandwidth inputs would be dangerous.
- The DCE10 topology has six CRTCs but seven DIG/AFMT offsets. DIG encoder selection can return 6 for `UNIPHY3`; consumers must ensure `num_dig` and AFMT allocation match this.
- `dce_v10_0_crtc_do_set_base()` pins the new framebuffer before unpinning the old framebuffer and returns `-EINVAL` for pin failures. Repeated failures or unusual BO reservation ordering could leave memory pressure symptoms visible as modeset failures.
- Several audio paths return early when no connector, no pin, failed infoframe packing, or missing EDID data exists; this prevents crashes but may leave audio disabled while video still works.
- HPD intentionally disables HPD interrupts on eDP/LVDS to avoid AUX breakage and interrupt storms. Regression tests need to account for polling/fixed-panel behavior rather than expecting hotplug IRQs there.
- Reset support detects display hang by sampling HV counters and toggling `SRBM_SOFT_RESET__SOFT_RESET_DC_MASK`, but `is_idle()` always returns true and clock/power gating callbacks are stubs.

## Test Signals

Useful validation should include boot/probe on Tonga/Fiji devices, connector enumeration from ATOM object tables, HPD plug/unplug on non-panel connectors, eDP/LVDS no-storm behavior, vblank enable/disable and timestamp tests, pageflip completion including async flip, suspend/resume with backlight restoration, HDMI audio with SAD/speaker allocation/latency EDID data, 6/8/10/12-bpc modes, 10-bpc framebuffer LUT bypass, tiled and linear framebuffer scanout, cursor set/move/hide/reset, multi-head watermark behavior under DPM clock changes, and GPU reset recovery when a CRTC is deliberately wedged.
