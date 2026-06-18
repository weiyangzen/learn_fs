# Research: subset-b-001328

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.h

## Purpose

`dce_v10_0.h` is the public interface for the DCE10 AMDGPU display backend. It exposes the IP block descriptors used by device discovery/ASIC setup code and the early DCE disable helper used to quiesce display hardware before or during driver initialization.

## Important APIs and Types

- Include guard: `__DCE_V10_0_H__`.
- `extern const struct amdgpu_ip_block_version dce_v10_0_ip_block;` declares the DCE 10.0 IP descriptor implemented in `dce_v10_0.c`.
- `extern const struct amdgpu_ip_block_version dce_v10_1_ip_block;` declares the DCE 10.1 IP descriptor. In the implementation it shares the same function table as DCE 10.0 while advertising minor version 1.
- `void dce_v10_0_disable_dce(struct amdgpu_device *adev);` declares the display-engine disable routine that disables VGA render and active CRTC masters when the ATOM BIOS DCE engine info table is present.

## Control Flow and Integration

The header has no executable control flow; it allows other AMDGPU compilation units to reference DCE10 IP block versions and call the disable helper without including the full implementation. The concrete IP block functions are installed through `dce_v10_0_ip_block`/`dce_v10_1_ip_block`, whose `.funcs` member points to the DCE10 `amd_ip_funcs` table in the C file.

## State and Persistence Behavior

The header owns no state. The declared IP block objects are immutable `const` descriptors in the C file. The declared disable function mutates hardware display registers and depends on `amdgpu_device` runtime state, but those side effects are outside this header.

## Dependencies

This header intentionally relies on forward-visible AMDGPU core type declarations from includers: `struct amdgpu_ip_block_version` and `struct amdgpu_device`. It does not include other headers itself, keeping it lightweight but requiring callers to include AMDGPU core definitions in the right order.

## Risks and Test Signals

The main risk is interface drift: any change to the implementation exports, IP block naming, or disable-helper signature must be reflected here or callers will fail to compile. Test signals are build coverage for ASIC tables that reference DCE10/DCE10.1, plus boot validation that the selected IP block calls the DCE10 init/fini hooks and that any pre-init disable path links and executes correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.h

## Purpose

`dce_v6_0.h` is the public interface for the DCE6 AMDGPU display backend. It exposes the IP block descriptors for DCE 6.0 and 6.4 hardware and declares the early display-engine disable helper.

## Important APIs and Types

- Include guard: `__DCE_V6_0_H__`.
- `extern const struct amdgpu_ip_block_version dce_v6_0_ip_block;` declares the DCE 6.0 IP descriptor implemented in `dce_v6_0.c`.
- `extern const struct amdgpu_ip_block_version dce_v6_4_ip_block;` declares the DCE 6.4 descriptor, which uses the same function table as DCE 6.0 in the implementation.
- `void dce_v6_0_disable_dce(struct amdgpu_device *adev);` declares the helper that disables VGA render and active CRTC masters when ATOM BIOS reports DCE engine information.

## Control Flow and Integration

There is no executable logic in the header. Other AMDGPU source files include it to select DCE6/DCE6.4 IP blocks during ASIC setup or to call `dce_v6_0_disable_dce()` during low-level display quiescing. The implementation behind the descriptors installs the DCE6 `amd_ip_funcs` table and its DRM display callbacks.

## State and Persistence Behavior

The header owns no runtime state. The declared IP block descriptors are immutable constants in the C file. The declared disable function mutates device registers and depends on `struct amdgpu_device` state, but those side effects are in the implementation.

## Dependencies

The header assumes includers already have declarations for `struct amdgpu_ip_block_version` and `struct amdgpu_device`. It deliberately avoids local includes and exists as a narrow linkage boundary between ASIC setup code and the DCE6 display implementation.

## Risks and Test Signals

The risk surface is small and mostly compile/link oriented: declarations must stay synchronized with implementation symbols, and ASIC setup code must use the correct DCE6 or DCE6.4 descriptor. Test signals are build coverage for both descriptors and boot/probe validation on hardware paths that select DCE6.x, including any path that calls the disable helper before full mode-setting initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.h -->
