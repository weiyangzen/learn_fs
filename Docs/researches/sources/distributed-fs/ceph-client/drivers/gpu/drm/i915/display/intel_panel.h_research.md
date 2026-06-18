# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_panel.h

Purpose: exposes panel fixed-mode, detection, configuration, backlight/panel lifecycle, and panel follower notification APIs.

Important APIs: fixed mode selectors (`preferred`, `fixed`, `downclock`, `highest`), `intel_panel_get_modes()`, `intel_panel_drrs_type()`, `intel_panel_mode_valid()`, `intel_panel_compute_config()`, EDID/VBT/current fixed-mode adders, init/fini/register/unregister, detect, SSC choice, prepare/unprepare.

Control flow/state: no implementation state. The signatures make callers pass connectors, CRTC state, connector state, and encoders as needed for panel decisions and lifecycle.

Dependencies/integration: used by LVDS/eDP/DSI/backlight/BIOS code. Forward declarations keep compile dependencies low.

Risks/test signals: API behavior is tightly coupled to connector panel ownership and mode-list lifetimes. Header changes require broad display build coverage.
