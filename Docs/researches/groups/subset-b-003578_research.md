# Research: subset-b-003578

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_sil164.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_sil164.c

## Purpose
`dvo_sil164.c` is the i915 DVO helper for Silicon Image SIL164 TMDS transmitters attached over I2C. It plugs into the legacy `intel_dvo_device` framework through `sil164_ops`, allowing the broader DVO encoder code to probe the chip, detect hotplug state, set basic transmitter registers, toggle power, read hardware state, dump registers, and release private state.

## Important APIs, Types, and Functions
The file defines register addresses and bit masks for vendor/device ID, frequency, control, hotplug, and PLL registers. `struct sil164_priv` stores only a `quiet` flag used to suppress expected I2C read/write failures during probe. `sil164_readb()` and `sil164_writeb()` are the low-level I2C register accessors using `i2c_transfer()`. `sil164_init()` allocates private state with `kzalloc_obj()`, binds the selected I2C adapter to `dvo->i2c_bus`, checks the low bytes of `SIL164_VID` and `SIL164_DID`, and enables logging after successful detection. `sil164_detect()` reads `SIL164_REG9` and maps `SIL164_9_HTPLG` to DRM connector status. `sil164_mode_set()` writes a minimal enable setup to `REG8`, `REG9`, and `REGC`. `sil164_dpms()` and `sil164_get_hw_state()` use `SIL164_8_PD` as the power-on indicator.

## Control Flow and State
Probe is intentionally quiet: private state is allocated first, `quiet` is set, and ID reads decide whether the chip exists at `dvo->target_addr`. On failure the private object is freed; on success the DVO core later calls detect, mode, power, and debug callbacks through `sil164_ops`. The only persisted software state is `dvo->dev_priv` plus the chosen `dvo->i2c_bus`; hardware state is kept in the transmitter registers and is read back when needed.

## Dependencies and Integration Points
This driver depends on the Linux I2C core, DRM KMS debug logging, `intel_display_types.h`, and `intel_dvo_dev.h`. It is registered externally through `extern const struct intel_dvo_dev_ops sil164_ops` and is referenced by the DVO device table in `intel_dvo.c`. It assumes the surrounding DVO encoder has already selected a target I2C address and adapter.

## Risks and Test Signals
`sil164_detect()` does not check the return value of `sil164_readb()`, so an I2C failure may leave `reg9` undefined in theory. Mode validation accepts all modes, so practical limits are enforced elsewhere or by hardware behavior. Useful test signals include successful DVO probe messages, correct hotplug transitions from `SIL164_9_HTPLG`, DPMS toggling that changes `SIL164_8_PD`, register dumps, and modeset tests on legacy DVO hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_sil164.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_tfp410.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_tfp410.c

## Purpose
`dvo_tfp410.c` implements the legacy i915 DVO bridge driver for TI TFP410 TMDS transmitters. It exposes an `intel_dvo_dev_ops` table named `tfp410_ops` so the DVO core can discover a transmitter on an I2C bus, query sink presence, apply basic modeset/power operations, and dump chip registers.

## Important APIs, Types, and Functions
Register definitions mirror the TFP410 datasheet, including vendor/device IDs, control registers, data-enable timing registers, and resolution readouts. `struct tfp410_priv` carries a `quiet` probe flag. `tfp410_readb()` and `tfp410_writeb()` issue byte register I2C transactions. `tfp410_getid()` reads little-endian 16-bit IDs from adjacent registers. `tfp410_init()` allocates private state, attaches the adapter, suppresses probe noise, validates `TFP410_VID` and `TFP410_DID`, and returns ownership to the DVO framework. `tfp410_detect()` reads `TFP410_CTL_2` and treats `TFP410_CTL_2_RSEN` as connected. `tfp410_dpms()` and `tfp410_get_hw_state()` manipulate/read `TFP410_CTL_1_PD`. `tfp410_dump_regs()` prints revision, control, DE timing, and resolution registers.

## Control Flow and State
The driver follows a probe-then-callback model. Initialization is the only path that allocates memory and persists software state in `dvo->dev_priv`; mode setting is deliberately a no-op because the transmitter is expected to work if basic platform wiring is correct. Power state is not cached in software and is read back from the chip.

## Dependencies and Integration Points
The file depends on I2C transfers, DRM KMS debug logging, and the i915 DVO abstractions. `intel_dvo.c` lists the TFP410 device entry and binds `tfp410_ops`; `intel_dvo_dev.h` declares the ops object. The DVO core supplies the I2C target address, adapter, and lifecycle.

## Risks and Test Signals
The detect path returns disconnected if the CTL2 read fails, which is conservative but can hide transient I2C failures. Mode validation accepts all modes, so unsupported TMDS clocks or board-specific limits are outside this file. Test evidence should include correct VID/DID probing, stable RSEN-based connection status, DPMS bit changes in CTL1, successful register dumps, and display output on systems with TFP410 DVO wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_tfp410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_dp.c

## Purpose
`g4x_dp.c` provides the non-DDI DisplayPort/eDP encoder implementation for G4x, Ironlake, Sandy Bridge, Ivy Bridge, Valleyview, and Cherryview. It handles platform-specific DP register programming, DPLL parameters, link training callbacks, eDP panel power sequencing, HPD handling, audio enablement, signal-level programming, hardware state readout, and encoder/connector initialization through `g4x_dp_init()`.

## Important APIs, Types, and Functions
Static DPLL tables (`g4x_dpll`, `pch_dpll`, `vlv_dpll`, `chv_dpll`) describe supported 162 MHz and 270 MHz link clocks. `vlv_get_dpll()` exports the VLV/CHV table base. `g4x_dp_set_clock()` writes the selected divisor into `intel_crtc_state`. `intel_dp_prepare()` builds the cached `intel_dp->DP` register image, preserving `DP_DETECTED` and selecting sync, pipe, enhanced-framing, color-range, and link-training bits according to platform and port. `g4x_dp_port_enabled()` reads DP enable and pipe routing, including CPT transcoder routing via `cpt_dp_port_selected()`. `intel_dp_get_config()` reconstructs output type, audio, framing, sync flags, lane count, M/N values, port clock, dotclock, and eDP BPP fixups from hardware.

Enable/disable sequencing is split across encoder hooks. `ilk_edp_pll_on/off()` manage the port A eDP PLL. `intel_enable_dp()` powers VLV/CHV PPS resources when needed, enables the DP port, powers the sink to D0, configures protocol converters/PCON features, and runs link training. `intel_disable_dp()` turns off eDP backlight and panel power. `intel_dp_link_down()` disables the port and applies the IBX pipe-A workaround. `g4x_set_link_train()` and `cpt_set_link_train()` translate DPCD training patterns into hardware register bits; corresponding idle functions program idle patterns. Signal-level programming is platform-specific through `g4x_set_signal_levels()`, `snb_cpu_edp_set_signal_levels()`, `ivb_cpu_edp_set_signal_levels()`, `vlv_set_signal_levels()`, and `chv_set_signal_levels()`.

`intel_dp_hotplug()` integrates HPD with link-state checking and retry scheduling. Platform live-status helpers read G4x, ILK, or IBX interrupt/status registers. `g4x_dp_compute_config()` delegates core DP mode computation to `intel_dp_compute_config()` and then fills legacy DPLL state. `g4x_dp_init()` allocates `intel_digital_port` and connector objects, initializes the DRM encoder, assigns encoder hooks, chooses link-training and signal-level callbacks, sets power domains, pipe masks, HPD behavior, AUX channel, and finally calls `intel_dp_init_connector()`.

## Control Flow and State
The central mutable state is the cached `intel_dp->DP` register image plus DP link state in `intel_dp->link`, training state in `intel_dp->train_set`, panel power sequencing state, and atomic `intel_crtc_state` fields such as `port_clock`, `lane_count`, `has_pch_encoder`, `enhanced_framing`, and `dp_m_n`. Atomic commit flow computes config, prepares PLL/PHY, enables the port and link, then enables panel/backlight; disable reverses the path while respecting panel power delays and hardware workarounds. Hardware readout reconstructs the same state after boot or resume.

## Dependencies and Integration Points
This file is tightly coupled to i915 display subsystems: `intel_dp`, AUX, PPS, link training, eDP backlight, audio codec, PCH display, DPIO PHY, hotplug, FIFO underrun suppression, display power domains, and register access through `intel_de_*()`. `intel_display.c` calls `g4x_dp_init()` for relevant ports on G4x/ILK/SNB/IVB/VLV/CHV. The header exposes only `vlv_get_dpll()`, `g4x_dp_port_enabled()`, and `g4x_dp_init()` when `I915` is enabled.

## Risks and Test Signals
Risk is concentrated in hardware sequencing: wrong PLL, pipe select, training pattern, signal level, or PPS ordering can cause blank panels, failed link training, hotplug storms, or underruns. Platform conditionals are dense and sometimes share registers with HDMI, especially IBX/PCH workarounds. Test signals include DP/eDP modeset and suspend/resume on each supported platform, link-training success logs, AUX/EDID detection, HPD retry behavior, audio codec enablement, panel power/backlight timing, FIFO underrun absence, and state readout matching atomic state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_dp.h

## Purpose
`g4x_dp.h` declares the public interface for the legacy G4x through CHV DisplayPort encoder implementation. It hides the implementation behind `#ifdef I915` and provides inert stubs for builds where the i915 display code is not compiled.

## Important APIs, Types, and Functions
The exported functions are `vlv_get_dpll()`, `g4x_dp_port_enabled()`, and `g4x_dp_init()`. `vlv_get_dpll()` lets other display code obtain the VLV/CHV DP DPLL table. `g4x_dp_port_enabled()` reads whether a DP port is enabled and returns the selected pipe. `g4x_dp_init()` creates and wires the encoder/connector for a hardware DP register and port.

## Control Flow and State
The header carries no state. It forward-declares `enum pipe`, `enum port`, and the display/encoder/DP structs used by the C file, keeping consumers independent of the full type definitions unless they include implementation headers.

## Dependencies and Integration Points
It includes `linux/types.h` and `i915_reg_defs.h` for `bool` and `i915_reg_t`. `intel_display.c` and other display initialization/readout code use these declarations. The non-I915 stubs return `NULL`, `false`, or no-op-equivalent values so shared code can compile without linking the DP implementation.

## Risks and Test Signals
The header is low risk, but prototypes must remain synchronized with `g4x_dp.c`. A notable maintenance issue is that the stub versions take `int port` while the real versions use `enum port`, which is ABI-compatible in C but can mask type drift. Build coverage with and without `I915` is the main test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_hdmi.c

## Purpose
`g4x_hdmi.c` implements legacy HDMI encoder support for G4x, ILK, SNB, IVB, VLV, and CHV platforms, while newer HSW+ DDI hardware is handled elsewhere. It configures HDMI/SDVO-style registers, infoframes, audio presence, hotplug behavior, platform-specific PHY/enable sequences, connector atomic checks, and encoder initialization via `g4x_hdmi_init()`.

## Important APIs, Types, and Functions
`intel_hdmi_prepare()` builds and writes the HDMI control value: TMDS output, sync polarity, limited color range, 8/12 bpc format, HDMI/DVI mode, and pipe select. `intel_hdmi_get_hw_state()` asks `intel_sdvo_port_enabled()` under the encoder power domain. `g4x_hdmi_compute_config()` marks PCH encoder usage and computes `has_hdmi_sink`; on G4x, `g4x_compute_has_hdmi_sink()` selects only one active HDMI port to transmit infoframes/audio. `intel_hdmi_get_config()` reconstructs output type, sync flags, HDMI sink state, infoframe state, audio, limited range, dotclock, lane count, GCP, AVI/SPD/vendor infoframes, and audio codec config.

Enable/disable paths are platform-specific. `g4x_hdmi_enable_port()` sets `SDVO_ENABLE`. `ibx_enable_hdmi()` writes the enable bit twice and toggles for a 12bpc pixel-repeat workaround. `cpt_enable_hdmi()` implements `WaEnableHDMI8bpcBefore12bpc` using `TRANS_CHICKEN1`. `intel_disable_hdmi()` clears enable, applies the IBX pipe-A workaround shared with DP-port routing, disables infoframes, and disables dual-mode TMDS output. VLV/CHV pre-enable paths program DPIO PHY signal levels, infoframes, port enable, lane readiness, and CL2 override release.

`g4x_hdmi_audio_enable()` and `_disable()` wrap HDMI audio presence bits and codec callbacks. `intel_hdmi_hotplug()` requests retry detection when live state is unreliable. `g4x_hdmi_connector_atomic_check()` adds all enabled HDMI connectors to the atomic state on G4x so the single infoframe/audio-capable port can be selected consistently. `g4x_hdmi_init()` validates the port, allocates digital port and connector objects, initializes the DRM encoder, installs callbacks, sets power domain, pipe mask, cloneability, HPD pin, infoframe helpers, and calls `intel_hdmi_init_connector()`.

## Control Flow and State
Atomic commit computes sink/audio/infoframe decisions first, then pre-enable writes static HDMI register state and infoframes, enable performs platform-specific port activation, and audio hooks set codec state. Disable paths clear the port and infoframes after or during platform-specific post-disable sequencing. Persistent software state lives in `dig_port->hdmi.hdmi_reg`, encoder callback fields, connector state, and atomic `intel_crtc_state` flags; hardware state lives in HDMI/SDVO registers and infoframe storage.

## Dependencies and Integration Points
The file integrates with DRM atomic helpers, i915 audio, infoframe, SDVO, hotplug, PCH display, DPIO PHY, display power, and register access layers. `intel_display.c` calls `g4x_hdmi_init()` for platform-supported HDMI ports. `g4x_hdmi_connector_atomic_check()` is exposed through the header for connector code.

## Risks and Test Signals
Main risks are platform-specific enable ordering, shared DP/HDMI PCH routing workarounds, G4x single-infoframe behavior, unreliable HPD live state, 12bpc and pixel-repeat workarounds, and VLV/CHV PHY constants. Test signals include HDMI and DVI modesets, audio enable/disable, infoframe readback, hotplug retry behavior, cloning on G4x, suspend/resume state readout, absence of FIFO underruns around IBX workarounds, and successful 8bpc/12bpc/pixel-repeat modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_hdmi.h

## Purpose
`g4x_hdmi.h` declares the public entry points for legacy G4x-family HDMI support and provides fallback stubs for builds without `I915`.

## Important APIs, Types, and Functions
The header exports `g4x_hdmi_init()`, which creates an HDMI encoder/connector for a hardware register and port, and `g4x_hdmi_connector_atomic_check()`, which performs connector validation and G4x-specific state expansion for HDMI infoframe/audio selection.

## Control Flow and State
The header contains only declarations and conditional stubs. It forward-declares `enum port`, `struct drm_atomic_state`, `struct drm_connector`, and `struct intel_display`. No state is stored here.

## Dependencies and Integration Points
It includes `linux/types.h` and `i915_reg_defs.h` for basic types and MMIO register identifiers. HDMI initialization in `intel_display.c` consumes `g4x_hdmi_init()`, while connector setup can use the atomic-check helper. Non-I915 stubs return `false` or success (`0`) to keep shared builds linkable.

## Risks and Test Signals
Risk is mainly declaration drift between the header and implementation. Build tests with `I915` enabled and disabled verify the conditional interface. Runtime coverage belongs to `g4x_hdmi.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/hsw_ips.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/hsw_ips.c

## Purpose
`hsw_ips.c` manages Intermediate Pixel Storage (IPS) power-saving behavior on Haswell/Broadwell ULT systems, where IPS is tied to pipe A. It decides when IPS can be enabled, handles atomic pre/post update transitions, applies Haswell versus Broadwell programming paths, exposes debugfs controls, and contributes minimum CDCLK requirements.

## Important APIs, Types, and Functions
`hsw_ips_enable()` programs `IPS_CTL` or the Broadwell PCODE mailbox (`DISPLAY_IPS_CONTROL`) if `crtc_state->ips_enabled` is true, optionally adding `IPS_FALSE_COLOR`. `hsw_ips_disable()` clears IPS and returns whether callers must wait for vblank before disabling a plane. `hsw_ips_need_disable()` and `hsw_ips_need_enable()` compare old/new atomic CRTC state to handle modesets, IPS flag changes, inherited Broadwell state, and the Haswell split-gamma palette workaround. `hsw_ips_pre_update()` and `hsw_ips_post_update()` are the public atomic sequencing hooks.

Capability and config functions include `hsw_crtc_supports_ips()` for pipe/platform filtering, `hsw_crtc_state_ips_capable()` for pipe BPP restrictions, `_hsw_ips_min_cdclk()` and `hsw_ips_min_cdclk()` for Broadwell CDCLK constraints, `hsw_ips_compute_config()` for enabling IPS only when policy, CRC, active planes, and CDCLK allow it, and `hsw_ips_get_config()` for hardware readout. Debugfs helpers expose `i915_ips_false_color` and `i915_ips_status`.

## Control Flow and State
Atomic check first clears and conditionally sets `crtc_state->ips_enabled`. During commits, pre-update may disable IPS before modesets, color LUT updates, or transitions away from IPS; post-update may re-enable it after plane updates and a vblank wait. Persistent software state is in `display->ips.false_color`, module/display params (`enable_ips`), and atomic CRTC state. Hardware state is in `IPS_CTL` on Haswell and mediated through PCODE on Broadwell, where readout is not reliable and inherited state is handled conservatively.

## Dependencies and Integration Points
The file depends on debugfs, DRM logging, PCODE registers, color registers, display RPM, parent PCODE access, and core display atomic state. `intel_display.c` calls IPS disable/pre/post/get/compute hooks during modeset and update flows. `intel_cdclk.c` incorporates `hsw_ips_min_cdclk()`, and `intel_display_debugfs.c` registers the debugfs files.

## Risks and Test Signals
Risks include vblank ordering around plane enable/disable, Broadwell PCODE timeout behavior, unreliable Broadwell state readout, interaction with CRC capture, and Haswell split-gamma palette hazards. Test signals include atomic modesets with IPS enabled/disabled, color LUT updates in split gamma mode, CRC tests confirming IPS is disabled when CRC is active, Broadwell PCODE timeout logs, debugfs false-color behavior, and CDCLK selection when IPS would require more than the max clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/hsw_ips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/hsw_ips.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/hsw_ips.h

## Purpose
`hsw_ips.h` declares the IPS interface used by i915 display atomic, CDCLK, readout, and debugfs code. It also provides no-op stubs for non-I915 builds.

## Important APIs, Types, and Functions
The public API covers lifecycle and policy: `hsw_ips_disable()`, `hsw_ips_pre_update()`, `hsw_ips_post_update()`, `hsw_crtc_supports_ips()`, `hsw_ips_min_cdclk()`, `hsw_ips_compute_config()`, `hsw_ips_get_config()`, and `hsw_ips_crtc_debugfs_add()`. The types are forward declarations for `intel_atomic_state`, `intel_crtc`, and `intel_crtc_state`.

## Control Flow and State
The header stores no state. Its declarations encode that IPS participates in atomic update sequencing before and after plane updates, in CDCLK computation, in hardware readout, and in debugfs registration.

## Dependencies and Integration Points
It includes `linux/types.h` for `bool`. `intel_display.c`, `intel_cdclk.c`, and `intel_display_debugfs.c` are the main consumers. Stub behavior returns false or zero and performs no action when the implementation is excluded.

## Risks and Test Signals
The interface is low risk but important because incorrect stub behavior could change display decisions in non-I915 builds. Compile testing both conditional paths and runtime IPS tests through the implementation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/hsw_ips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_display_sr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_display_sr.c

## Purpose
`i9xx_display_sr.c` saves and restores legacy display registers across suspend/resume or display reset paths for i9xx-era hardware. It focuses on display arbitration, GMBUS clock gating config, and SWF scratch registers.

## Important APIs, Types, and Functions
`i9xx_display_save_swf()` reads SWF scratch register banks into `display->restore.saveSWF*` arrays with platform-specific counts: mobile gen2 saves SWF0/SWF1/SWF3, desktop gen2 saves SWF1, and GMCH platforms save larger SWF0/SWF1 plus SWF3 sets. `i9xx_display_restore_swf()` writes those arrays back. `i9xx_display_sr_save()` guards on `HAS_DISPLAY()`, saves `DSPARB` for display versions up to 4, saves PCI config `GCDGMBUS` on gen4, then saves SWF. `i9xx_display_sr_restore()` restores SWF first, then gen4 `GCDGMBUS`, then `DSPARB`.

## Control Flow and State
The module has no local private allocation. It persists hardware snapshots in `display->restore`, which must survive the suspend/resume interval. The save path captures MMIO and PCI config state; the restore path replays them in a conservative order.

## Dependencies and Integration Points
The file depends on DRM device access for `display->drm->dev`, PCI config helpers, GMBUS and watermark/arbitration register definitions, and `intel_de_*()` MMIO access. The header exposes `i9xx_display_sr_save()` and `_restore()` to higher-level power-management code.

## Risks and Test Signals
The main risk is incomplete platform coverage or wrong register counts, which can produce resume regressions on older chipsets. Because it touches PCI config and display arbitration, ordering matters. Test signals include suspend/resume on gen2-gen4 and GMCH systems, preserved GMBUS behavior, no display FIFO/arbitration regressions after resume, and debug comparison of saved/restored SWF values where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_display_sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_display_sr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_display_sr.h

## Purpose
`i9xx_display_sr.h` is the small public header for legacy i9xx display save/restore helpers.

## Important APIs, Types, and Functions
It forward-declares `struct intel_display` and declares `i9xx_display_sr_save()` and `i9xx_display_sr_restore()`. These functions snapshot and replay legacy display register state in the C file.

## Control Flow and State
No state is stored in the header. The function pair implies a caller-managed lifecycle: call save before suspend/reset state loss and restore after display MMIO/PCI config can be programmed again.

## Dependencies and Integration Points
The header has no includes beyond the guard and is intended for higher-level display power-management code. The implementation depends on `display->restore` storage in `struct intel_display`.

## Risks and Test Signals
Risk is limited to declaration drift and misuse of save/restore ordering by callers. Build coverage and suspend/resume tests of the implementation provide validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_display_sr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane.c

## Purpose
`i9xx_plane.c` implements primary-plane support for legacy i915 display hardware from gen2 through Broadwell-era primary planes and VLV/CHV variants. It defines supported formats/modifiers, validates scanout surfaces, programs plane registers, handles async flips and flip-done interrupts, attaches FBC, creates DRM primary planes, reads BIOS-initial plane configuration, and fixes up plane base addresses after framebuffer relocation.

## Important APIs, Types, and Functions
Format arrays describe per-platform primary-plane formats: `i8xx_primary_formats`, `ivb_primary_formats`, `i965_primary_formats`, and `vlv_primary_formats`. `i8xx_plane_format_mod_supported()` and `i965_plane_format_mod_supported()` validate format/modifier pairs against plane capabilities. `i9xx_plane_has_fbc()` and `i9xx_plane_fbc()` map eligible primary planes to FBC. `i9xx_plane_has_windowing()` captures old hardware windowing limitations.

`i9xx_plane_ctl()` translates framebuffer format, tiling, rotation, reflection, and platform trickle-feed behavior into `DSPCNTR` bits. `i9xx_check_plane_surface()` computes GTT placement, source offsets, alignment, X-tile constraints, 64bpp width restrictions, and final scanout coordinates. `i9xx_plane_check()` combines CHV rotation validation, clipping, surface validation, source-coordinate checks, and control-word generation. `i8xx_plane_surf_offset()` and `i965_plane_surf_offset()` expose surface offset calculations.

Programming is split between `i9xx_plane_update_noarm()` for stride/window registers and `i9xx_plane_update_arm()` for offset/control/surface arming. `i830_plane_update_arm()` handles self-arming i830/i845 behavior. `i9xx_plane_disable_arm()` disables the plane while preserving pipe gamma/CSC bits needed for bottom color and state readout. Capture-error helpers read control/surface/live registers by generation. Async flip support uses `g4x_primary_async_flip()` or `vlv_primary_async_flip()` plus generation-specific flip-done IRQ enable/disable functions.

Stride/alignment callbacks (`hsw_primary_max_stride()`, `ilk_primary_max_stride()`, `i965_plane_max_stride()`, `i915_plane_max_stride()`, `i8xx_plane_max_stride()`, `vlv_plane_min_alignment()`, `g4x_primary_min_alignment()`, `i965_plane_min_alignment()`) encode hardware limits and VTD/async-flip alignment needs. `intel_primary_plane_create()` allocates and initializes a primary plane, chooses formats, callbacks, modifiers, rotations, FBC, zpos, and DRM plane registration names. `i9xx_get_initial_plane_config()` reads current hardware state into an `intel_initial_plane_config`, and `i9xx_fixup_initial_plane_config()` writes a relocated surface address if takeover moved the framebuffer.

## Control Flow and State
Atomic plane checking computes derived state into `intel_plane_state`: GTT view offsets, x/y scanout coordinates, `ctl`, and `surf`. Commit code then calls no-arm and arm callbacks to write MMIO in the correct order. Initial boot readout allocates an `intel_framebuffer`, infers format/modifier/rotation/size from hardware, and stores it in `plane_config`. Plane objects persist callbacks, platform-specific `i9xx_plane` identity, pipe, FBC association, frontbuffer bit, min/max stride and alignment policies, async flip hooks, and tiling-disable behavior.

## Dependencies and Integration Points
The file depends on DRM atomic helpers, format/modifier definitions, i915 register definitions, display IRQ control, framebuffer/GTT helpers, FBC, frontbuffer tracking, sprite/plane helpers, and platform display state. `intel_crtc.c` calls `intel_primary_plane_create()`. Initial framebuffer takeover paths call `i9xx_get_initial_plane_config()` and `i9xx_fixup_initial_plane_config()`. Other plane code can use exported helpers such as `i965_plane_max_stride()`, `vlv_plane_min_alignment()`, `i9xx_check_plane_surface()`, and `i965_plane_surf_offset()`.

## Risks and Test Signals
Risk is high because this code directly controls scanout addresses, tiling offsets, pipe routing, and atomic arming. Bugs can cause underruns, wrong colors/formats, memory scanout outside the intended framebuffer, failed async flips, broken FBC, or boot takeover failures. Important tests include IGT plane format/modifier coverage, rotation/reflection tests, X-tiled offset edge cases, 64bpp width/CDCLK constraints, async flip and flip-done IRQ tests, suspend/resume and BIOS framebuffer takeover, FBC eligibility checks, VTD alignment scenarios, and underrun monitoring across gen2 through BDW/VLV/CHV hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane.h

## Purpose
`i9xx_plane.h` declares the public primary-plane helpers implemented in `i9xx_plane.c` and supplies stubs for non-I915 builds.

## Important APIs, Types, and Functions
The header exports stride/alignment and surface helpers (`i965_plane_max_stride()`, `vlv_plane_min_alignment()`, `i9xx_check_plane_surface()`, `i965_plane_surf_offset()`), primary-plane construction (`intel_primary_plane_create()`), and initial-plane takeover helpers (`i9xx_get_initial_plane_config()`, `i9xx_fixup_initial_plane_config()`). It forward-declares CRTC, display, framebuffer, format, plane, and plane-state types.

## Control Flow and State
No state is stored here. The declarations expose two key flows: atomic primary-plane validation/programming support and initial hardware framebuffer readout/fixup.

## Dependencies and Integration Points
It includes `linux/types.h` for fixed-width types and conditionally exposes the implementation under `I915`. `intel_crtc.c` and initial configuration code consume these declarations. The stubs return conservative no-op values when the implementation is not present.

## Risks and Test Signals
The non-I915 stub for `i965_plane_max_stride()` has a signature that differs from the real prototype (`u32 pixel_format` versus `const struct drm_format_info *info`), which can hide type drift only when that branch is compiled. Build tests for both branches and runtime plane tests through `i9xx_plane.c` are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane_regs.h

## Purpose
`i9xx_plane_regs.h` defines MMIO register addresses and bitfield helpers for legacy i9xx primary/display plane registers, including VLV/CHV address variants and CHV pipe B primary-plane window registers.

## Important APIs, Types, and Functions
The header defines register macros such as `DSPCNTR()`, `DSPADDR()`, `DSPLINOFF()`, `DSPSTRIDE()`, `DSPPOS()`, `DSPSIZE()`, `DSPSURF()`, `DSPTILEOFF()`, `DSPOFFSET()`, `DSPSURFLIVE()`, `DSPGAMC()`, `PRIMPOS()`, `PRIMSIZE()`, and `PRIMCNSTALPHA()`. Bitfields include plane enable, pipe gamma/CSC, pixel format encodings, pipe select, color key, line double, alpha, rotation, trickle-feed disable, tiling, async flip, CHV mirror, offsets, sizes, surface address mask, and constant alpha.

## Control Flow and State
The header has no runtime control flow. Its macros are used by C code to calculate platform/plane-specific MMIO addresses and to pack or extract register fields. State is hardware register state represented symbolically.

## Dependencies and Integration Points
It includes `intel_display_reg_defs.h` for `_MMIO_PIPE2`, `_MMIO_TRANS2`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. `i9xx_plane.c` is the primary consumer, but other low-level display code can use these definitions for readout, capture, and programming.

## Risks and Test Signals
Incorrect addresses or bit encodings directly corrupt plane programming. Overloaded bit positions across generations, such as rotation versus alpha-transparency or pipe CSC versus pipe select, require careful platform gating by users. Test signals include register read/write traces during modeset, IGT plane programming tests, async flip coverage, CHV pipe B reflection/window tests, and hardware state readout matching expected `DSPCNTR`/surface fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane_regs.h -->
