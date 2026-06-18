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
