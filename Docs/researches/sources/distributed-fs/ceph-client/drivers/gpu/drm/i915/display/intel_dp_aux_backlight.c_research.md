# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_backlight.c

## Purpose
Implements eDP backlight control over DisplayPort AUX for i915. It selects between Intel's proprietary HDR/nits AUX backlight interface, the standard VESA eDP AUX backlight interface, and PWM fallback paths when AUX controls only part of the panel backlight behavior.

## Important APIs, types, and functions
- `intel_dp_aux_init_backlight_funcs()` is the exported initializer used by the backlight core to install either `intel_dp_hdr_bl_funcs` or `intel_dp_vesa_bl_funcs` in `panel->backlight.funcs`.
- `enum intel_dp_aux_backlight_modparam` mirrors `i915.enable_dpcd_backlight` modes: auto, off, on, force VESA, and force Intel.
- Intel HDR path: `intel_dp_aux_supports_hdr_backlight()`, `intel_dp_aux_hdr_setup_backlight()`, `intel_dp_aux_hdr_enable_backlight()`, `intel_dp_aux_hdr_set_backlight()`, `intel_dp_aux_hdr_get_backlight()`, `intel_dp_aux_hdr_disable_backlight()`.
- VESA path: `intel_dp_aux_supports_vesa_backlight()`, `check_if_vesa_backlight_possible()`, `intel_dp_aux_vesa_setup_backlight()`, `intel_dp_aux_vesa_enable_backlight()`, `intel_dp_aux_vesa_set_backlight()`, `intel_dp_aux_vesa_get_backlight()`, `intel_dp_aux_vesa_disable_backlight()`.
- Uses `struct intel_panel` state including `panel->backlight.edp.intel_cap`, `panel->backlight.edp.vesa.info`, luminance min/max/level, PWM helper callbacks, and VBT backlight type.

## Control flow
Initialization first evaluates the module parameter and VBT backlight type. In auto mode it probes Intel AUX only when VBT says the panel uses Display DDI/PWM style backlight and probes VESA directly when VBT advertises the VESA eDP AUX interface. Forced modes override this. The Intel proprietary interface is probed first because writing Intel OUI state can make broken VESA implementations stop responding correctly.

The Intel HDR probe waits for Intel source OUI, reads four bytes at the proprietary TCON capability block, checks interface version and nits brightness capability, and usually requires HDR static metadata from EDID unless the user forced the Intel path. Setup configures PWM when SDR brightness is not AUX-driven, sets min/max luminance from EDID luminance range or a default 0..512 range, writes panel luminance override, and snapshots the current level. Enable reads the current TCON control byte, chooses AUX or PWM brightness for the current HDR/SDR mode, fills HDR TCON bits, writes the control byte only if it changed, and writes content luminance metadata in HDR mode.

The VESA probe first accepts luminance-plus-smooth-brightness capable panels, otherwise requires both AUX enable and AUX brightness set support plus sane PWM bit count capability. Setup calls `drm_edp_backlight_init()`, initializes PWM if AUX does not cover enable or set operations, then derives user-facing brightness range and current enabled/level state from VESA info and current mode. Set/enable/disable combine DRM eDP AUX helpers with PWM fallback where needed.

## State and persistence
Runtime state is kept on the connector panel: chosen function table, Intel capability bits, VESA helper info, luminance support flag, min/max/level/enabled, and PWM state. It persists while the connector object lives and is refreshed by setup and enable calls. The file also writes sink-side DPCD registers that persist in the panel until changed or reset: Intel TCON control, brightness nits, content luminance, panel luminance override, and VESA backlight registers through DRM helpers.

## Dependencies and integration points
Depends on DRM DP AUX/DPCD helpers, DRM eDP backlight helpers, i915 panel/PWM helpers, EDID HDR/luminance metadata, VBT backlight type, `intel_dp_wait_source_oui()`, `intel_dp_in_hdr_mode()`, and connector color space/HDR metadata. Integrated through `intel_backlight.c`, which calls `intel_dp_aux_init_backlight_funcs()` before falling back to other backlight implementations.

## Risks
Panel firmware is known to misadvertise VESA support; the probe order and module parameter handling are compatibility-sensitive. Intel HDR nits control without EDID HDR metadata is intentionally disabled unless forced, so unknown panels can lose AUX backlight support without the module override. Several operations rely on short DPCD reads/writes where partial positive lengths are treated as failure in most but not all debug paths. Mixed PWM/AUX operation has edge cases around current mode detection, inversion, and min brightness semantics.

## Test signals
Useful signals include `drm_dbg_kms()` logs announcing Intel or VESA interface selection, DPCD/PWM control mode messages, range messages, and explicit DPCD read/write errors. Manual validation should cover panels with Intel-only AUX, VESA AUX, mixed AUX/PWM enable/set, HDR metadata present/missing, forced module parameters, suspend/resume, and brightness reads before enabling AUX brightness.
