# subset-b-003582 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color.c

## Purpose
Implements i915 display color management across legacy GMCH, ILK/IVB/BDW/HSW/SKL/GLK/ICL/TGL+, and Xe display generations. It validates DRM color properties, assigns degamma/gamma LUTs around CSC blocks, converts DRM CTM blobs into hardware coefficient formats, programs pipe/plane color registers, reads hardware color state back, and selects platform-specific hook tables used by atomic commit and modeset paths.

## Important APIs, types, and functions
`struct intel_color_funcs` is the internal dispatch table for `color_check`, no-arm/arm/post-update programming, LUT load/read/equality, CSC readout, config readout, and newer plane color programming. Public entry points include `intel_color_init_hooks()`, `intel_color_init()`, `intel_color_crtc_init()`, `intel_color_check()`, `intel_color_prepare_commit()`, `intel_color_commit_noarm()`, `intel_color_commit_arm()`, `intel_color_load_luts()`, `intel_color_get_config()`, `intel_color_lut_equal()`, `intel_color_assert_luts()`, `intel_color_plane_program_pipeline()`, and `intel_color_plane_commit_arm()`. Key helpers convert CTM coefficients (`ilk_csc_convert_ctm()`, `ctm_to_twos_complement()`, VLV/CHV CSC converters), resize or synthesize LUT blobs (`create_linear_lut()`, `create_resized_lut()`), and pack/unpack many hardware LUT formats.

## Control flow
Initialization selects a hook table in `intel_color_init_hooks()` based on GMCH/display generation and creates a GLK linear degamma LUT in `intel_color_init()` when required. `intel_color_check()` marks color changes caused by C8 planes, then calls the generation-specific checker (`i9xx_color_check()`, `vlv_color_check()`, `chv_color_check()`, `ilk_color_check()`, `ivb_color_check()`, `glk_color_check()`, `icl_color_check()`). These checkers validate LUT sizes/tests, reject unsupported combinations such as YCbCr+CTM on older hardware, derive enable/mode bits, assign pre/post CSC blobs, convert CSC matrices, and request affected plane updates. Commit is split: LUTs may be preloaded or loaded through DSB in `intel_color_prepare_commit()`, CSC coefficient writes happen in no-arm hooks, mode/control registers are armed in arm hooks, and ICL disarms sticky CSC self-arming in `icl_color_post_update()`.

## State and persistence behavior
Persistent state is stored in `intel_crtc_state`: `gamma_enable`, `csc_enable`, `wgc_enable`, `cgm_mode`, `gamma_mode`, `csc_mode`, `pre_csc_lut`, `post_csc_lut`, CSC matrices, `dsb_color`, `preload_luts`, and plane color blobs. Hardware state persists in MMIO palettes, CSC registers, CGM/WGC blocks, 3D LUT control/data registers, and DSB command buffers until latched or reset. Blob references are managed with `drm_property_replace_blob()` and released after temporary resized blobs are assigned.

## Dependencies and integration points
The file depends on DRM color helpers, i915 display state, `intel_de` MMIO helpers, DSB, VRR push handling, plane register definitions, and display runtime capabilities from `DISPLAY_INFO()`. It integrates with CRTC initialization (`drm_crtc_enable_color_mgmt()`), atomic checking, vblank/DSB commit sequencing, hardware state readout, plane HDR color pipeline programming, and connector/output-format decisions.

## Risks and test signals
Risk concentrates around generation-specific LUT sizes, precision loss, CTM clamping, limited-range handling, C8 palette interactions, single vs double-buffered register latching, PSR/DC5 workarounds on SKL/ICL, DSB posted write behavior, and incomplete hardware readout for ICL multi-segment gamma. Useful tests include DRM atomic color property validation, IGT color/CTM/gamma tests across display generations, suspend/resume and PSR scenarios, C8 plane commits, YCbCr output checks, hardware state checker comparisons through `intel_color_lut_equal()`, and vblank timing tests for LUT loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color.h

## Purpose
Declares the i915 display color management interface used by CRTC, atomic commit, modeset, and plane update code. The header hides generation-specific details behind stable entry points implemented in `intel_color.c`.

## Important APIs and types
It forward-declares display, CRTC, atomic, DSB, plane-state, property-blob, and pipe types. APIs cover lifecycle (`intel_color_init_hooks()`, `intel_color_init()`, `intel_color_crtc_init()`), atomic validation (`intel_color_check()`), commit sequencing (`prepare`, `cleanup`, `wait`, `commit_noarm`, `commit_arm`, `post_update`, `modeset`, `load_luts`), state readout/equality (`get_config`, `lut_equal`, `assert_luts`), and plane color programming (`intel_color_plane_program_pipeline()`, `intel_color_plane_commit_arm()`, `intel_color_crtc_has_3dlut()`).

## Control flow and integration
Callers first initialize display hooks and per-CRTC color properties, then use the check and commit helpers during atomic modesets and fast updates. Plane color code queries `intel_color_crtc_has_3dlut()` before binding 3D LUT state.

## State, dependencies, risks, and tests
The header owns no state, but its functions mutate `intel_crtc_state`, `intel_plane_state`, display hook tables, and hardware registers through implementation code. Risks are API-ordering mistakes: callers must pair prepare/wait/cleanup and respect no-arm/arm split. Tests should compile all display paths and exercise atomic color updates with and without DSB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_pipeline.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_pipeline.c

## Purpose
Exposes DRM plane color pipeline objects for HDR-capable i915 planes. It builds a chain of DRM colorops representing pre-CSC 1D LUT, 3x4 CSC, optional 3D LUT, and post-CSC 1D LUT blocks.

## Important APIs and functions
`intel_color_pipeline_plane_init()` is the exported initializer. Internal helpers include `plane_has_3dlut()`, `_intel_color_pipeline_plane_init()`, and `intel_color_pipeline_plane_add_colorop()`. Static pipeline arrays define the HDR plane chain and the Xe3/PLPD primary-plane chain with 3D LUT. The file uses `intel_colorop_create()` and `intel_colorop_destroy()` for object lifetime and DRM helpers such as `drm_plane_colorop_curve_1d_lut_init()`, `drm_plane_colorop_ctm_3x4_init()`, `drm_plane_colorop_3dlut_init()`, and `drm_plane_create_color_pipeline_property()`.

## Control flow
Initialization skips non-HDR planes. For HDR planes it selects a pipeline based on display version, pipe 3D LUT capability, and primary-plane type, allocates each colorop in order, links adjacent colorops through the `next` property, creates a named pipeline enum entry, then publishes the plane color pipeline property. On failure it walks back and destroys already-created colorops.

## State and integration
The persistent state is DRM object state attached to the plane: colorop objects, their next links, and the color pipeline property. It integrates new DRM color pipeline UAPI with hardware programming in `intel_color_plane_program_pipeline()`.

## Risks and test signals
Risks include exposing unsupported 3D LUT sharing, leaking allocated pipeline names or colorops on partial failure, and mismatches between exposed pipeline order and actual hardware programming. Tests should cover property enumeration on HDR/non-HDR planes, primary vs non-primary Xe3 pipelines, object cleanup, and atomic commits using each colorop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_pipeline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_pipeline.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_pipeline.h

## Purpose
Declares the single color pipeline initializer used when setting up DRM planes.

## APIs and integration
`intel_color_pipeline_plane_init(struct drm_plane *plane, enum pipe pipe)` attaches supported color pipeline/colorop properties to a plane. It is consumed by plane initialization code and implemented in `intel_color_pipeline.c`.

## State, dependencies, risks, and tests
The header owns no state. It depends only on `struct drm_plane` and `enum pipe` declarations. The main risk is missing initialization from plane setup, which would leave HDR color UAPI unavailable. Compile tests and plane property enumeration tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_pipeline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_regs.h

## Purpose
Defines i915 display color-management MMIO registers and bit fields used by `intel_color.c` and plane color code. It covers legacy palettes, precision palettes, pipe CSC, output CSC, pre/post CSC LUTs, Cherryview CGM, Skylake bottom color, and 3D LUT registers.

## Important definitions
Legacy GMCH palette macros include `PALETTE()`, palette RGB masks, 10-bit slope fields, and `PIPEGCMAX()`. ILK+ definitions include `LGC_PALETTE()`, `PREC_PALETTE()`, `GAMMA_MODE()`, CSC coefficient/offset registers, `PIPE_CSC_MODE()`, and ICL output CSC macros. Indexed LUT registers include `PREC_PAL_INDEX/DATA`, multi-segment palette registers, and `PRE_CSC_GAMC_INDEX/DATA`. VLV/CHV color blocks include WGC CSC and `CGM_PIPE_*` degamma/gamma/CSC/mode macros. 3D LUT support is defined by `LUT_3D_CTL`, `LUT_3D_INDEX`, `LUT_3D_DATA`, enable/ready/binding bits, and component masks.

## Control flow and state
The header has no executable control flow. Its macro layout determines which MMIO address and bit encoding each color path writes or reads. Hardware state persists in the addressed registers and is latched according to generation-specific behavior in `intel_color.c`.

## Dependencies, risks, and tests
It depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_PIPE`, masks, and field helpers. Risks are incorrect offsets, pipe selection, field widths, or reused enum values that silently corrupt color programming. Test signals include successful color IGTs, hardware state readout, register trace comparison, and build coverage for all generation-specific paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_colorop.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_colorop.c

## Purpose
Provides the small i915 wrapper around DRM colorop objects used by the plane color pipeline UAPI.

## Important APIs and control flow
`to_intel_colorop()` converts a `struct drm_colorop` to the embedding `struct intel_colorop`. `intel_colorop_alloc()` zero-allocates the wrapper and returns `ERR_PTR(-ENOMEM)` on failure. `intel_colorop_create()` allocates and records the `enum intel_color_block` id. `intel_colorop_destroy()` calls `drm_colorop_cleanup()` and frees the wrapper.

## State and integration
Persistent state is the allocated `struct intel_colorop`, especially its embedded DRM colorop base and i915 color-block id. The file integrates with `intel_color_pipeline.c`, which creates colorops and passes `intel_colorop_destroy` as the DRM destroy callback.

## Risks and test signals
Risks are mostly lifetime related: destroying before DRM init completion, failing to cleanup DRM object state, or double-freeing through pipeline rollback paths. Tests should cover failed pipeline initialization, plane teardown, and KASAN/KMEMLEAK runs around DRM colorop object lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_colorop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_colorop.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_colorop.h

## Purpose
Declares i915 colorop wrapper helpers for the DRM plane color pipeline implementation.

## APIs and integration
The header forward-declares `enum intel_color_block`, `struct drm_colorop`, and `struct intel_colorop`, then exposes conversion, allocation, creation, and destruction helpers. `intel_color_pipeline.c` uses these declarations to create typed i915 colorop objects and register the destroy callback with DRM.

## State, dependencies, risks, and tests
It owns no state. Its declarations are a narrow boundary between generic DRM colorop code and i915 display types. Risks are signature drift with DRM helper callbacks or missing declarations when new color block types are introduced. Build coverage and plane pipeline property teardown tests are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_colorop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy.c

## Purpose
Initializes, verifies, powers lane subsets, and uninitializes Intel combo PHYs used by display ports. It handles process/voltage compensation programming, PHY master/slave quirks, platform-specific PHY_MISC availability, and lane power masks for DSI and non-DSI links.

## Important APIs and functions
Public APIs are `intel_combo_phy_init()`, `intel_combo_phy_uninit()`, and `intel_combo_phy_power_up_lanes()`. Internal logic includes `icl_get_procmon_ref_values()`, `icl_set_procmon_ref_values()`, `icl_verify_procmon_ref_values()`, `has_phy_misc()`, `icl_combo_phy_enabled()`, `ehl_vbt_ddi_d_present()`, `phy_is_master()`, `icl_combo_phy_verify_state()`, `icl_combo_phys_init()`, and `icl_combo_phys_uninit()`.

## Control flow
Init iterates all combo PHYs, skips already-verified PHYs, programs PHY_MISC/mux state when present, applies display version 12+ ODCC/DCC settings, writes process-monitor reference values, enables IREFGEN on master PHYs, sets `COMP_INIT`, and enables common-lane power-down control. Lane power updates compute a `PWR_DOWN_LN_*` mask from lane count, DSI status, and reversal before updating `ICL_PORT_CL_DW10`. Uninit walks PHYs in reverse, warns if PHY A state changed unexpectedly, powers down DE IO compensation where available, and clears `COMP_INIT`.

## State and integration
State persists entirely in combo PHY MMIO registers: COMP, CL, PCS, TX, and PHY_MISC. It depends on VBT port/DSI presence, platform flags, `intel_phy_is_combo()`, `intel_de` MMIO helpers, and register definitions. Encoders call the lane power API as link configuration changes.

## Risks and test signals
Risks include wrong process/voltage tables, incorrect VBT DDI-D mux choice on EHL/JSL, powering the wrong lanes under reversal, missing PHY_MISC quirks, and stale firmware-initialized PHY state. Test signals include boot/display bring-up on ICL/TGL/RKL/DG1/ADL-S/EHL/JSL, register state verification logs, link training stability, and suspend/resume uninit/init cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy.h

## Purpose
Declares the combo PHY lifecycle and lane power interface used by i915 display encoder code.

## APIs and integration
`intel_combo_phy_init()` and `intel_combo_phy_uninit()` manage global PHY setup/teardown. `intel_combo_phy_power_up_lanes()` adjusts active lane masks for a PHY using DSI flag, lane count, and lane reversal. The header depends on `enum phy`, `struct intel_display`, and `bool`.

## State, risks, and tests
The header owns no state but exposes functions that mutate PHY MMIO registers. Risks are misuse with non-combo PHYs or unsupported lane counts; the implementation emits missing-case diagnostics. Tests should cover link bring-up with 1/2/4 lane and DSI configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy_regs.h

## Purpose
Defines combo PHY MMIO address calculations and bit fields for ICL-era and later display PHY programming.

## Important definitions
The file maps PHY base addresses for ICL A/B, EHL C, RKL D, and ADL E through `_ICL_COMBOPHY()`. It defines CL registers (`ICL_PORT_CL_DW5`, `DW10`, `DW12`) with lane power masks, COMP registers with `COMP_INIT`, process/voltage fields, `IREFGEN`, and reference-value DWords, PCS registers with DCC/common keeper/latency fields, TX registers for swing, RCOMP, tap/cursor, LDO override, scalar, and ODCC clock settings, plus `ICL_DPHY_CHKN()`.

## Control flow and state
There is no executable flow. These macros are consumed by combo PHY init and link-training code to read/write persistent PHY hardware state.

## Dependencies, risks, and tests
It depends on `intel_display_reg_defs.h` for register/mask helpers. Incorrect offsets or masks can break every encoder using combo PHYs, often as link-training failures or blank displays. Tests should include compile coverage, PHY state verification, link training across PHYs A-E, and platform-specific register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_connector.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_connector.c

## Purpose
Provides connector-generic allocation, cleanup, registration, encoder attachment, mode retrieval, retry work, and common DRM connector property helpers for the i915 display driver.

## Important APIs and functions
Lifecycle functions include `intel_connector_alloc()`, `intel_connector_free()`, `intel_connector_destroy()`, `intel_connector_register()`, and `intel_connector_unregister()`. Runtime helpers include `intel_connector_attach_encoder()`, `intel_connector_get_hw_state()`, `intel_connector_get_pipe()`, `intel_connector_update_modes()`, `intel_ddc_get_modes()`, and modeset retry work queue/cancel helpers. Property attachers create or attach force-audio, Broadcast RGB, aspect ratio, HDMI/DP colorspace, and scaling mode properties.

## Control flow
Allocation zeroes the connector, allocates an oversized digital connector state, resets DRM atomic state, initializes panel allocation, and sets retry work. Retry work takes a connector ref, marks link status BAD under the mode config mutex, sends a hotplug event, then drops the ref. Destroy frees EDID, HDCP, panel, DRM connector state, MST port refs, and the connector object. Mode helpers read EDID over DDC, update connector EDID state, and add modes.

## State and integration
State includes connector DRM state, panel data, `detect_edid`, HDCP state, MST port reference, attached encoder pointer, polled mode, and display-wide cached property objects. Dependencies include DRM EDID/probe helpers, i2c, panel, HDCP, debugfs, and connector state types.

## Risks and test signals
Risks include refcount imbalance around retry work, connector state size assumptions, missed work cancellation during destroy, stale shared property objects, and mode_config locking mistakes. Test signals include hotplug retry tests, connector registration/unregistration, EDID mode enumeration, MST teardown, and KASAN/refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_connector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_connector.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_connector.h

## Purpose
Declares connector-generic i915 helpers for lifecycle, encoder association, EDID/mode handling, common properties, and modeset retry work.

## APIs and integration
It exposes allocation/free/destroy/register/unregister helpers, `intel_connector_attach_encoder()`, hardware-state and pipe queries, EDID update/DDC mode helpers, property attachers, and retry work queue/cancel routines. Connector implementations such as CRT, HDMI, DP, LVDS, and eDP use this shared interface.

## State, risks, and tests
The header owns no state, but declared functions manipulate DRM connector state, i915 connector fields, shared properties, and workqueue references. Risks are incorrect callback wiring or missing cancellation before teardown. Compile coverage plus connector hotplug/mode enumeration tests exercise the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_connector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt.c

## Purpose
Implements analog VGA/CRT encoder and connector support for i915. It controls ADPA/PCH_ADPA/VLV_ADPA programming, mode validation, compute config, enable/disable sequencing, hotplug/DDC/load detection, DMI quirks, and connector/encoder initialization.

## Important APIs and functions
Public functions are `intel_crt_port_enabled()`, `intel_crt_init()`, and `intel_crt_reset()`. `struct intel_crt` embeds `struct intel_encoder`, tracks whether forced hotplug is required, and stores the ADPA register. Important internal paths include `intel_crt_get_hw_state()`, `intel_crt_get_config()`, `hsw_crt_get_config()`, `intel_crt_set_dpms()`, enable/disable hooks for native/PCH/HSW, `intel_crt_mode_valid()`, compute-config variants, hotplug detectors (`ilk_crt_detect_hotplug()`, `valleyview_crt_detect_hotplug()`, `intel_crt_detect_hotplug()`), EDID/DDC helpers, legacy `intel_crt_load_detect()`, and `intel_crt_detect()`.

## Control flow
`intel_crt_init()` chooses the ADPA register, probes whether the DAC can be enabled, allocates connector/encoder objects, initializes DRM connector and encoder callbacks, sets pipe masks/hotplug polling, installs DDI or legacy encoder hooks, optionally records LPT FDI polarity state, and resets hotplug bits. Detection first checks display availability/access and DMI skip quirks, powers the CRT domain, tries HPD where available, then analog EDID/DDC, and only uses load detect for forced pre-gen4 cases. Enable/disable sequences differ for simple ADPA programming, PCH split, and HSW DDI/PCH/FDI paths.

## State and persistence behavior
Persistent state includes ADPA register bits for DAC enable, pipe select, sync polarity, DPMS, hotplug configuration, `force_hotplug_required`, connector polling state, FDI RX config, and DRM connector/encoder state. Load detection temporarily mutates border color, vblank, and transcoder config, then restores them.

## Dependencies and integration points
The file depends on connector helpers, CRTC vblank helpers, DDI, FDI, PCH, GMBUS, hotplug IRQ, load detect, VGA sense, underrun reporting, panel fitting, and link bandwidth helpers. It integrates with DRM connector helper callbacks, encoder hooks, power domains, and atomic modeset sequencing.

## Risks and test signals
Risks include false-positive VGA detection, HPD polling loops on VLV, broken DDC behind KVM/DVI-I adapters, load-detect flicker and register restore failures, platform-specific FDI limits, and incorrect underrun reporting order around HSW enable/disable. Tests should include VGA hotplug/DDC, DVI-I shared DDC cases, forced load-detect, DMI skip machines, HSW/BDW FDI CRT modes, suspend/resume reset, and DPMS transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt.h

## Purpose
Declares the CRT/VGA encoder interface and provides no-op stubs when the i915-specific build path is disabled.

## APIs and integration
Under `I915`, it exposes `intel_crt_port_enabled()`, `intel_crt_init()`, and `intel_crt_reset()`. Without `I915`, inline stubs return disconnected/no-op behavior. Consumers use these helpers for CRT setup, hardware-state queries, and encoder reset callbacks.

## State, risks, and tests
The header owns no state but controls whether CRT support is compiled in. Risks are mismatched stub behavior in non-i915 builds or missing include dependencies for `i915_reg_t`. Build matrix coverage and basic CRT init/reset tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt_regs.h

## Purpose
Defines ADPA register addresses and bit fields for analog CRT/VGA output programming.

## Important definitions
The file defines `ADPA`, `PCH_ADPA`, and `VLV_ADPA`, plus fields for DAC enable, pipe select, hotplug monitor result, hotplug enable/period/warmup/sample/voltage/reference/force-trigger, VGA polarity source, sync disable bits, and sync active-high bits.

## Control flow and state
There is no executable code. These definitions encode persistent hardware state used by `intel_crt.c` for DPMS, detection, reset, and pipe selection.

## Dependencies, risks, and tests
It depends on display register helper macros. Risks are field-mask mistakes causing wrong pipe routing, hotplug mis-detection, or sync polarity errors. Tests include CRT mode set, DPMS, hotplug force trigger, and register readback on native, PCH, and VLV paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc.c

## Purpose
Implements i915 CRTC allocation, initialization, vblank handling, pipe update timing, event delivery, pipe lookup, bandwidth helpers, and CRTC state reset. It is the bridge between DRM CRTC core callbacks and generation-specific i915 display hardware.

## Important APIs and functions
Public APIs include `intel_crtc_init()`, `intel_crtc_state_alloc()`, `intel_crtc_state_reset()`, `intel_crtc_for_pipe()`, `intel_first_crtc()`, vblank on/off/counter/wait helpers, `intel_pipe_update_start()`, `intel_pipe_update_end()`, `intel_wait_for_vblank_workers()`, event helpers, change-detection helpers, scanline/usec converters, and bandwidth helpers. Internal code defines DRM CRTC function tables per generation, CRTC allocation/free/destroy, pipe-list insertion, pipe reordering for discrete graphics, vblank work initialization, and vblank work execution.

## Control flow
`intel_crtc_init()` logs available pipes and creates each CRTC through `__intel_crtc_init()`. That path allocates state, creates primary/sprite/cursor planes, selects a DRM CRTC func table by platform, initializes DRM CRTC with planes, attaches scaling/color/DRRS/CRC/debug/QoS properties, and inserts the CRTC into the pipe list. Atomic fast updates call `intel_pipe_update_start()` to lock PSR, prepare events/work, initialize cursor vblank work, compute vblank evasion, get vblank refs, wait out the unsafe window, and disable IRQs. `intel_pipe_update_end()` schedules LUT/cursor vblank work or arms the event, sends DSI frame updates and VRR/PSR pushes, reenables IRQs, and detects missed vblank deadlines.

## State and persistence behavior
CRTC persistent software state includes `pipe`, `pipe_head`, `config`, `plane_ids_mask`, `num_scalers`, vblank PM QoS request, debug timing fields, vblank PSR notification flag, and the embedded DRM CRTC state. Hardware-facing state includes vblank counters, active pipe/transcoder state, and plane data-rate accounting.

## Dependencies and integration points
The file integrates with DRM atomic helpers, vblank core, pipe CRC, color management, PSR/VRR/DRRS/DSI, cursor and plane code, FIFO underrun reporting, debugfs, display IRQs, and platform runtime info. Encoder code calls its vblank helpers during enable/disable and detection.

## Risks and test signals
Risks include vblank event leaks, missed vblank evasion causing atomic update failure, IRQs left disabled on error paths, incorrect pipe ordering, stale PM QoS after vblank work, and bandwidth underestimation. Test signals include IGT kms_flip/atomic/vblank/CRC tests, PSR/VRR commits, legacy cursor updates, DSI command mode commits, hotplug/modeset stress, and debug logs for atomic update failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc.h

## Purpose
Declares the i915 CRTC interface used by display initialization, atomic commit, vblank management, event delivery, and bandwidth calculations.

## Important APIs and integration
The header exposes scanline/time conversion helpers, vblank event helpers, max counter/query/on/off/wait functions, CRTC initialization and state allocation/reset, pipe update start/end, worker flush, CRTC lookup helpers, active/enable change detection, and bandwidth helpers. It also defines `VBLANK_EVASION_TIME_US`, widened when lock proving is enabled.

## State, dependencies, risks, and tests
The header owns no state but exposes functions that mutate CRTC state, vblank refs, event pointers, worker state, and pipe update timing. Risks are incorrect call ordering around `intel_pipe_update_start/end()` and vblank work flushing. Build coverage plus atomic/vblank/flip tests exercise the API contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc.h -->
