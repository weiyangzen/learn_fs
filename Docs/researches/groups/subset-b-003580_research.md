# subset-b-003580 Research

Grouped research for ten i915 display files. Each section preserves the original source path and is intended to be split into the mapped source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio.c

## Purpose
`intel_audio.c` implements the display side of HDMI/DP high-definition audio for i915. It participates in modeset sequencing by programming codec-facing audio registers after the transcoder/link is active and before the transcoder/port is disabled, keeps ELD state for the HDA/LPE audio drivers, and exposes the i915 audio component ops consumed by `snd_hda_intel`.

## Important APIs, Types, and Functions
- `struct intel_audio_funcs` is the platform dispatch table for codec enable, disable, and state readout.
- `intel_audio_compute_config()` copies connector ELD into `crtc_state->eld`, validates that ELD exists, and writes AV sync delay into the ELD payload.
- `intel_audio_codec_enable()` and `intel_audio_codec_disable()` are the public modeset hooks. They call platform-specific register programming, update `display->audio.state[cpu_transcoder]`, notify HDA through `pin_eld_notify`, and notify LPE audio.
- `g4x_*`, `ibx_*`, and `hsw_*` paths cover G4X, PCH/VLV/CPT/IBX, and HSW+ register models.
- `hsw_audio_config_update()`, `hsw_hdmi_audio_config_update()`, and `hsw_dp_audio_config_update()` program N/CTS handling and timestamp behavior. HDMI may use fixed N values from HDMI tables keyed by sample rate, port clock, and pipe bpp.
- `intel_audio_cdclk_change_pre/post()` handles display version 13+ audio timestamp CDCLK M/N programming around CDCLK changes.
- Component ops include `get_power`, `put_power`, `codec_wake_override`, `get_cdclk_freq`, `sync_audio_rate`, and `get_eld`.

## Control Flow
Hook setup starts in `intel_audio_hooks_init()`, selecting G4X, IBX/PCH/VLV, or HSW functions based on platform. During atomic check, `intel_audio_compute_config()` snapshots ELD into the CRTC state. During enable, the selected backend programs ELD valid/output-enable/timestamp registers, then common code records `encoder` and ELD in `display->audio.state`, calls HDA `pin_eld_notify`, and calls LPE notification. Disable runs in the reverse modeset phase, invalidates ELD/presence, waits vblanks where required, clears state, and notifies audio consumers that ELD is gone.

HDA component binding is separate: `intel_audio_init()` chooses LPE or component mode, `intel_audio_register()` registers an audio component if LPE is absent, and component bind/unbind installs or removes the ops pointer under modeset locks.

## State and Persistence
Persistent driver state lives in `display->audio`: the per-transcoder `intel_audio_state` with active encoder and ELD bytes, `component`, `component_registered`, `freq_cntrl`, and `power_refcount`. `display->audio.mutex` protects shared ELD/audio state. Hardware-visible state is in audio registers, ELD valid bits, output enable bits, N/CTS controls, SDP split controls, and CDCLK timestamp registers. No disk persistence exists.

## Dependencies and Integration Points
This file integrates DRM ELD helpers, i915 atomic/modeset state, display register helpers (`intel_de_read/write/rmw`), CDCLK global state, display workarounds, LPE audio, Linux component framework, and `drm_audio_component_ops`. It depends on `intel_audio_regs.h` for register fields and on display platform predicates such as `DISPLAY_VER()`, `HAS_DDI()`, `HAS_DP20()`, and PCH/platform checks.

## Risks
Ordering is critical: enable must happen after link training/transcoder enable, and disable must happen before disabling the port/transcoder. Incorrect ELD state or missing notification can leave HDA with stale sink capabilities. N/CTS programming depends on the HDA-reported sample rate; absent or unmatched rates fall back to automatic N. Workarounds such as DSC hblank programming and min-hblank chicken bits are platform-specific and can cause regressions if applied too broadly. Power refcount mismatches during component unbind are explicitly logged.

## Test Signals
Useful signals include KMS debug messages for ELD size, N/CTS choice, pixel clock fallback, audio component bind failures, CDCLK M/N values, and invalid port/transcoder lookups. Exercise HDMI and DP audio across modesets, MST/non-MST, suspend/resume, CDCLK changes, LPE versus HDA component paths, high link-rate DP with audio CDCLK restrictions, and DSC 4K+ DP cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio.h

## Purpose
`intel_audio.h` declares the public display-audio interface used by the i915 display modeset, CDCLK, and driver lifecycle code. It hides platform-specific audio register programming behind a small set of hooks implemented in `intel_audio.c`.

## Important APIs, Types, and Functions
The header forward-declares `intel_display`, `intel_encoder`, `intel_crtc_state`, and DRM connector state types. Exports include `intel_audio_hooks_init()`, `intel_audio_compute_config()`, codec enable/disable/get-config helpers, CDCLK pre/post hooks, `intel_audio_min_cdclk()`, and lifecycle functions `intel_audio_init()`, `intel_audio_register()`, and `intel_audio_deinit()`.

## Control Flow
Callers initialize hooks during display setup, compute audio state during atomic check, run enable/disable during modeset sequencing, query config during state readout, invoke CDCLK hooks around clock changes, and initialize/register/deinitialize the audio component during driver lifecycle.

## State and Persistence
The header owns no state. Its prototypes operate on `display`, `encoder`, connector state, and CRTC state objects whose audio fields are persisted by `intel_audio.c` in `display->audio` and `crtc_state->eld`.

## Dependencies and Integration Points
It includes only `linux/types.h` and uses forward declarations to avoid coupling users to audio internals. Integration points are i915 display init, atomic modeset, CDCLK management, and HDA/LPE audio registration.

## Risks
The API assumes callers use the functions at the correct modeset phase. Calling enable/disable out of order can violate hardware sequencing even though this header cannot express that contract. `intel_audio_min_cdclk()` must be included in CDCLK calculations whenever audio is active.

## Test Signals
Compile coverage catches signature drift. Runtime coverage comes from modeset tests with `has_audio`, CDCLK transition tests, and HDA/LPE bind/unbind tests that traverse the declared lifecycle API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio_regs.h

## Purpose
`intel_audio_regs.h` defines the MMIO addresses and bit fields used by i915 display audio programming across G4X, IBX/CPT/VLV, HSW+, DP 2.0, LPE, CDCLK timestamp, and display audio workaround registers.

## Important APIs, Types, and Functions
The file is macro-only. Important groups include G4X ELD control/data registers; IBX/CPT/VLV per-pipe ELD and audio config registers; `AUD_CONFIG_*` N/CTS and HDMI pixel-clock fields; HSW transcoder audio config and M/CTS registers; `HSW_AUD_PIN_ELD_CP_VLD` output/ELD/CP bits; `AUD_DP_2DOT0_CTRL` SDP split enable; `AUD_FREQ_CNTRL`, `AUD_PIN_BUF_CTL`, `AUD_TS_CDCLK_M/N`; DSC/audio hblank workaround fields in `AUD_CONFIG_BE`; and LPE audio base and VLV mute/debug bits.

## Control Flow
The macros are consumed by `intel_audio.c` in codec enable/disable, ELD readout, HDMI/DP audio config, component power restore, wake override, CDCLK post programming, and DP/DSC workaround paths. They do not execute control flow themselves.

## State and Persistence
They describe hardware state encoded in MMIO registers. Persistent software state is kept elsewhere, but incorrect masks or shifts here directly corrupt register programming.

## Dependencies and Integration Points
The header depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_MMIO_TRANS`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. It is tightly integrated with i915 display/audio register access helpers and platform register layouts.

## Risks
Register definitions are platform-sensitive. Reusing G4X/PCH/VLV/HSW fields on the wrong generation can touch reserved or unrelated bits. Some macros use non-`REG_*` literal shifts for historical fields, so review must verify signedness and mask width when changing them. HDMI N/CTS fields split upper/lower N values and must remain consistent with hardware documentation.

## Test Signals
Primary signals are successful compile, register read/write traces under KMS debug, HDMI/DP audio functional tests, DP 2.0 SDP split tests, CDCLK transition tests on display version 13+, and workaround-specific validation on DSC/high-resolution modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight.c

## Purpose
`intel_backlight.c` implements i915 panel backlight control. It maps user brightness to hardware PWM ranges, abstracts multiple native PWM register layouts and external PWM chips, initializes panel backlight parameters from VBT/hardware, exposes a Linux backlight class device when enabled, and coordinates enable/disable/update with display modesets.

## Important APIs, Types, and Functions
- Scaling helpers `scale()`, `clamp_user_to_hw()`, `scale_hw_to_user()`, `intel_backlight_level_to_pwm()`, and `intel_backlight_level_from_pwm()` translate between user, logical hardware, and raw PWM levels.
- Platform get/set/enable/disable/setup callbacks exist for LPT/SPT PCH PWM, earlier PCH split PWM, i9xx/i965, VLV/CHV, BXT/GLK, CNP+, and external PWM.
- `intel_backlight_setup()` initializes `panel->backlight` state and marks the backlight present.
- `intel_backlight_enable()`, `intel_backlight_disable()`, and `intel_backlight_update()` are modeset-facing operations.
- `intel_backlight_set_acpi()` handles firmware/ACPI brightness requests.
- Backlight class functions register `intel_backlight`, update status, and read brightness when `CONFIG_BACKLIGHT_CLASS_DEVICE` is enabled.
- `intel_backlight_init_funcs()` chooses DSI DCS, DP AUX, native PWM, or external PWM implementations.

## Control Flow
Initialization selects backlight function tables based on connector type, platform, PCH type, and quirks. Setup reads existing PWM registers or external PWM state, falls back to VBT-derived PWM periods when registers are uninitialized, calculates minimum levels, reads current brightness, and stores logical level/enabled state. Modeset enable clamps the saved level to minimum and invokes platform enable. Disable updates the class device power state, marks disabled, and calls the platform disable path. User or ACPI updates lock `display->backlight.lock`, scale brightness, update cached level, and write hardware only when enabled.

## State and Persistence
State is stored in `connector->panel.backlight`: function pointers, PWM function pointers, min/max/current logical levels, PWM min/max, active-low and inversion attributes, controller index, combination mode, enabled/present flags, external `pwm_state`, class device pointer, and optional power hook. VBT-derived fields in `connector->panel.vbt.backlight` provide frequency, minimum brightness, controller, and backlight type. Hardware state lives in PWM duty/frequency/control registers or Linux PWM framework state.

## Dependencies and Integration Points
The file integrates Linux PWM, Linux backlight class, ACPI video policy, DRM modeset locking, i915 VBT data, panel power sequencing (`intel_pps_backlight_power`), DP AUX backlight, DSI DCS backlight, display RPM, quirks, PCI config LBPC on legacy combination mode, and register definitions from `intel_backlight_regs.h`.

## Risks
Brightness inversion combines module parameter and quirk behavior; off-by-one or min/max mistakes can make controls reversed or clamp to unusable brightness. Platform callbacks use different register units and enable ordering; writes before PWM enable intentionally do or do not stick depending on platform. VBT PWM frequency/minimum values may be bogus and are partially clamped. External PWM setup depends on VBT DSI PMIC/SoC selection. Backlight class callbacks lock the DRM connection mutex and display backlight mutex, so lock ordering must remain stable.

## Test Signals
KMS debug logs show selected backlight backend, initialized brightness, PWM frequency, controller, active-low state, and failed setup. Test native PWM platforms from gen2 through CNP+, VLV/CHV DSI external PWM, eDP AUX backlight fallback, ACPI brightness events during driver init, suspend/resume, vga_switcheroo skip path, class device reads/writes, inversion quirks, and VBT min/frequency edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight.h

## Purpose
`intel_backlight.h` declares the i915 display backlight API used by panel setup, modeset, ACPI/native brightness controls, and optional Linux backlight class registration.

## Important APIs, Types, and Functions
The API exposes function-table initialization, setup/destroy, enable/update/disable, ACPI and raw PWM setters, brightness inversion/scaling helpers, and conditional `intel_backlight_device_register/unregister()` wrappers. It forward-declares display, connector, panel, encoder, atomic, and CRTC state types.

## Control Flow
Panel code calls `intel_backlight_init_funcs()` before `intel_backlight_setup()`. Modeset paths call enable/update/disable around panel power transitions. User/firmware brightness updates enter through class device callbacks or `intel_backlight_set_acpi()`. Cleanup calls destroy and unregister functions.

## State and Persistence
The header stores no state. Implementations mutate `intel_panel.backlight` fields and hardware PWM state.

## Dependencies and Integration Points
It depends only on `linux/types.h` plus forward declarations, making it a stable interface for display code. `CONFIG_BACKLIGHT_CLASS_DEVICE` controls whether registration functions are real or no-op inline stubs.

## Risks
Callers must ensure `intel_panel` has initialized backlight function pointers before setup. The header exposes low-level PWM conversion helpers, so misuse outside established locking or range contracts can bypass normal clamping.

## Test Signals
Compile tests cover configuration with and without `CONFIG_BACKLIGHT_CLASS_DEVICE`. Runtime signals come from panel initialization, modeset backlight enable/disable, ACPI brightness updates, and class-device registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight_regs.h

## Purpose
`intel_backlight_regs.h` defines MMIO registers and bit masks for i915 native backlight PWM control across legacy CPU PWM, PCH split PWM, VLV/CHV pipe PWM, BXT/CNP PWM controllers, and utility-pin PWM output.

## Important APIs, Types, and Functions
The file is macro-only. Key definitions include `BLC_PWM_CTL2`, `BLC_PWM_CTL`, duty/frequency masks, legacy and polarity bits, PCH `BLC_PWM_PCH_CTL1/2`, CPU `BLC_PWM_CPU_CTL/2`, BXT `BXT_BLC_PWM_CTL/FREQ/DUTY`, VLV pipe-specific controls, histogram enable, and `UTIL_PIN_CTL` mode/polarity/pipe fields.

## Control Flow
The macros are consumed by `intel_backlight.c` platform callback tables. Setup paths read control/frequency/duty registers, enable paths program periods and enable bits, disable paths clear enable bits, and set paths update duty-cycle fields.

## State and Persistence
The header describes hardware state only. Register values persist until display power loss, BIOS/firmware changes, or driver writes. Software mirrors are in `panel->backlight`.

## Dependencies and Integration Points
It depends on `intel_display_reg_defs.h` and platform display base macros. It integrates with PCH/platform conditionals and register access helpers in the implementation.

## Risks
Many fields share similar names but differ by generation; for example PCH CTL1 is not layout-compatible with CTL2, while BXT controllers have separate duty/frequency registers. Incorrect mask selection can overwrite frequency while updating duty or enable the wrong pipe/controller. Utility pin programming affects controller 1 on BXT-style hardware.

## Test Signals
Coverage should include register dumps before/after enable/disable, brightness ramp tests, active-low panels, BXT controller 1 utility pin use, PCH override mode, VLV pipe A/B validation, and legacy combination mode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bios.c

## Purpose
`intel_bios.c` parses Intel VBT/BDB firmware data into sanitized i915 display configuration. It discovers the VBT from firmware override, ACPI OpRegion, SPI flash, or PCI ROM, caches selected BDB blocks, extracts child display device data, panel timing/backlight/power/eDP/PSR/MIPI/DSC settings, maps VBT ports/AUX/DDC pins to driver enums, and exposes query helpers for connector/encoder initialization.

## Important APIs, Types, and Functions
- `struct intel_bios_encoder_data` wraps a parsed `child_device_config`, optional DSC parameters, and list linkage.
- BDB block helpers include `find_raw_section()`, `bdb_find_section()`, `init_bdb_blocks()`, LFP pointer validation/fixup/generation helpers, and `get_blocksize()`.
- Panel parsing includes `get_panel_type()`, `parse_panel_options()`, `parse_generic_dtd()`, `parse_lfp_data()`, `parse_lfp_backlight()`, `parse_edp()`, `parse_psr()`, `parse_mipi_config()`, and `parse_mipi_sequence()`.
- Device parsing includes `parse_general_features()`, `parse_general_definitions()`, `parse_driver_features()`, `parse_compression_parameters()`, `parse_sdvo_device_mapping()`, and `parse_ddi_ports()`.
- Public lifecycle/query APIs include `intel_bios_init()`, early/late panel init, `intel_bios_driver_remove()`, `intel_bios_fini_panel()`, VBT validity check, TV/LVDS/port/DSI presence checks, encoder capability helpers, AUX/DDC/boost/link-rate helpers, DSC parameter lookup, encoder iteration, and debugfs registration.

## Control Flow
`intel_bios_init()` initializes VBT lists and defaults, locates a valid VBT, records BDB version, copies selected BDB blocks into `display->vbt.bdb_blocks`, parses general features and child devices, attaches DSC data to child devices, then performs SDVO/DDI parsing. If no VBT is found, it generates limited default child devices for non-Type-C DDI ports on relevant platforms.

Panel initialization is split into early and late paths. `intel_bios_init_panel_early()` selects a panel type without EDID fallback, while `intel_bios_init_panel_late()` can use EDID/PNPID and fallback. Once a panel type is known, parsing populates fixed modes, backlight data, SDVO LVDS mode, DRRS/PSR/VRR/HOBL, eDP link parameters, MIPI config/PPS/sequences, and DSI backlight ports.

## State and Persistence
Persistent parsed state lives in `display->vbt`, including default/general flags, BDB version, child device list, copied BDB block list, SDVO mappings, and CRT DDC pin. Per-panel persistent state lives in `panel->vbt`, including panel type, fixed modes, backlight config, eDP/PSR/DSI settings, and allocated MIPI sequence/config/PPS buffers. Cleanup frees child devices, DSC entries, BDB block entries, panel modes, and MIPI buffers.

## Dependencies and Integration Points
The file depends on VBT structure definitions from `intel_vbt_defs.h`, display core/runtime info, OpRegion, ROM helpers, GMBUS pin validation, DSC helpers, DP constants, DRM EDID/product ID helpers, firmware loading, debugfs, and display RPM for ROM access. Query helpers feed connector probing, DDI port initialization, eDP/DSI panel setup, AUX/DDC selection, HDMI/DP limits, and DSC CRTC configuration.

## Risks
VBT is firmware-provided and often malformed. The parser performs many size/version checks, but changes can still cause out-of-bounds reads if block sizes, child device sizes, or MIPI sequence sizes are mishandled. Version-gated fields must not be read on older BDB versions. Port, DDC, and AUX mappings vary by platform and PCH generation; mistakes can initialize nonexistent ports or choose wrong AUX/DDC channels. Panel type selection may differ between OpRegion, VBT, EDID PNPID, and fallback. MIPI sequence fixups intentionally compensate for broken real systems and are regression-prone.

## Test Signals
Important signals are KMS debug logs for VBT source, BDB version, block sizes, malformed LFP pointers, panel type source, mode/backlight/eDP/PSR/MIPI details, child device parsing, DDI port capabilities, and ignored invalid pins/ports. Test with valid VBT, no VBT, firmware override VBT, OpRegion VBT, PCI/SPI ROM VBT, old and new BDB versions, dual-LFP panel types, eDP/DSI panels, DSC-enabled child devices, Type-C/TBT/dedicated external ports, and `i915_vbt` debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bios.h

## Purpose
`intel_bios.h` declares the public VBT/BIOS parsing interface for i915 display code. It exposes parsed VBT queries while keeping raw VBT structures private to `intel_bios.c` and `intel_vbt_defs.h`.

## Important APIs, Types, and Functions
The header defines `enum intel_backlight_type` values used by parsed VBT backlight data. It declares VBT lifecycle functions, early/late panel initialization and finalization, VBT validation, display presence queries, DSC parameter lookup, encoder data lookup/iteration, encoder capability predicates, lane/HPD properties, DP AUX/link/boost helpers, HDMI DDC/boost/level-shift/TMDS helpers, and debugfs registration.

## Control Flow
Display initialization calls `intel_bios_init()`, connector/panel setup calls early and late panel init around EDID availability, encoder setup queries `intel_bios_encoder_data_lookup()` and capability helpers, and driver removal calls panel/display cleanup functions. Debugfs registration exposes raw VBT reads.

## State and Persistence
The header owns no state. It references opaque `intel_bios_encoder_data` objects stored in `display->vbt.display_devices` and panel data stored in `panel->vbt`.

## Dependencies and Integration Points
It depends on `linux/types.h` and forward declarations for DRM EDID, display, encoder, CRTC state, panel, `enum port`, and `enum aux_ch`. It is consumed broadly by display connector/encoder initialization, panel code, backlight code, DP/HDMI setup, and debugfs.

## Risks
The API returns parsed firmware data that may be absent or sanitized. Callers must handle zero, false, `PORT_NONE`, `AUX_CH_NONE`, and null encoder data returns. Version-dependent behavior is hidden in the implementation, so new users should not infer that every helper is meaningful on every platform.

## Test Signals
Compile coverage catches signature changes. Runtime coverage comes from connector initialization across VBT/no-VBT systems, eDP/DSI panels, HDMI/DP ports, debugfs `i915_vbt`, and module parameter firmware override cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bo.c

## Purpose
`intel_bo.c` is a display-side buffer-object adapter. It forwards framebuffer/GEM object operations from display code to the parent driver’s `display_parent_interface` BO callbacks, keeping display code independent of the underlying memory-manager implementation.

## Important APIs, Types, and Functions
Exported wrappers include `intel_bo_is_tiled()`, `intel_bo_is_userptr()`, `intel_bo_is_shmem()`, `intel_bo_is_protected()`, `intel_bo_key_check()`, `intel_bo_fb_mmap()`, `intel_bo_read_from_page()`, `intel_bo_describe()`, `intel_bo_framebuffer_init()`, `intel_bo_framebuffer_fini()`, and `intel_bo_framebuffer_lookup()`.

## Control Flow
Each function derives `struct intel_display *` from the DRM device or receives it directly, then dispatches to `display->parent->bo`. Some optional predicates (`is_tiled`, `is_userptr`, `is_shmem`) and `describe` are null-checked; required operations such as protected check, key check, mmap, page read, framebuffer init/fini, and lookup are called directly.

## State and Persistence
The file owns no persistent state. It operates on DRM GEM objects and framebuffer creation data while relying on parent BO callbacks for actual memory-object state.

## Dependencies and Integration Points
It depends on DRM GEM and framebuffer command types, `display_parent_interface.h`, and i915 display core/type helpers. It integrates with framebuffer creation, mmap, debugfs/seq reporting, display scanout validation, and protected-content checks.

## Risks
Required parent callbacks must be populated before display code uses these wrappers; otherwise null dereferences occur. Optional callbacks default to false/no-op, which is safe but may hide unsupported feature reporting. Since this is a thin adapter, correctness depends on parent BO callback semantics matching display expectations.

## Test Signals
Compile/link coverage verifies the parent interface contract. Runtime signals include framebuffer creation/destruction, mmap tests, userptr/shmem/tiled/protected object handling, key checks for protected content, debug object descriptions, and readback paths using `intel_bo_read_from_page()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bo.h

## Purpose
`intel_bo.h` declares the display buffer-object adapter API implemented by `intel_bo.c`. It lets display code query and operate on DRM GEM objects without including parent memory-manager internals.

## Important APIs, Types, and Functions
The header declares BO property predicates, protected key check, framebuffer mmap, page read, object description, framebuffer init/fini, and framebuffer GEM lookup. It forward-declares DRM and i915 display types used in those signatures.

## Control Flow
Display framebuffer and debug paths include this header and call wrappers when they need parent BO behavior. Actual dispatch occurs in `intel_bo.c`.

## State and Persistence
No state is stored here. State belongs to DRM GEM objects, framebuffer data, and the parent BO implementation.

## Dependencies and Integration Points
It includes `linux/types.h` for fixed-width integer types and forward-declares `drm_file`, `drm_gem_object`, `drm_mode_fb_cmd2`, `seq_file`, `vm_area_struct`, and display/framebuffer structs. It integrates with framebuffer setup, mmap, diagnostics, and scanout object validation.

## Risks
The API assumes parent callbacks exist where the implementation does not guard them. Header users must pass objects associated with an i915 display DRM device so `to_intel_display()` resolves correctly in the implementation.

## Test Signals
Compile coverage detects signature drift. Runtime tests should cover framebuffer lookup/init/fini, mmap, protected object checks, tiled/userptr/shmem object predicates, and debug description output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bo.h -->
