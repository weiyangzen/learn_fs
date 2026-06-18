# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display.h

Purpose: declares GVT virtual display data structures, constants, helper macros, and display emulation entry points.

Important APIs/types/functions: defines `SBI_REG_MAX`, `DPCD_SIZE`, `INTEL_GVT_MAX_UEVENT_VARS`, AUX constants, plane and port enums, `enum intel_vgpu_edid`, `struct intel_vgpu_sbi`, `struct intel_vgpu_dpcd_data`, `struct intel_vgpu_port`, and `struct intel_vgpu_vblank_timer`. Inline helpers provide EDID labels and x/y resolution. Macros include `intel_vgpu_port()`, `intel_vgpu_has_monitor_on_port()`, and `intel_vgpu_port_is_dp()`.

Control flow and state: no complex runtime flow in the header. It defines the persistent per-vGPU display state consumed by `display.c`: EDID and DPCD validity, port type/id, refresh rate in millihertz, and hrtimer period.

Dependencies and integration points: depends on Linux hrtimer/types and GVT structs. Included by display, EDID, framebuffer decoder, and other GVT paths that need to query ports or trigger display events.

Risks and test signals: enum values must stay consistent with array sizes such as `GVT_EDID_NUM` and `GVT_PORT_MAX`. The EDID helper defaults return zero or empty string for invalid IDs, so callers must validate resolution before use. Test signals are compile coverage across GVT display users, correct resolution helper values, monitor detection macros, and hrtimer state carried in `struct intel_vgpu_vblank_timer`.
