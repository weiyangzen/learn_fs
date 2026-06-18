# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_device.h

## Purpose
`intel_display_device.h` defines display platform flags, static and runtime display capability structures, feature query macros, display-version helpers, register-offset helpers, and the public display-device probe/runtime API. It is the main interface for asking what display hardware exists and which capabilities are enabled.

## Important APIs, Types, And Functions
The `INTEL_DISPLAY_PLATFORMS()` macro enumerates platform and subplatform bits used in `struct intel_display_platforms`. `DEV_INFO_DISPLAY_FOR_EACH_FLAG()` defines static feature flags in `struct intel_display_device_info`. The header defines many feature macros such as `HAS_DISPLAY`, `HAS_DDI`, `HAS_DSC`, `HAS_DMC`, `HAS_FBC`, `HAS_PSR`, `HAS_DP_MST`, `HAS_HOTPLUG`, `HAS_GMCH`, `HAS_TRANSCODER`, `HAS_ULTRAJOINER`, and version/step helpers like `DISPLAY_VER()`, `DISPLAY_VERx100()`, `IS_DISPLAY_VER()`, and `IS_DISPLAY_STEP()`. `struct intel_display_runtime_info` carries mutable runtime masks and capabilities; `struct intel_display_device_info` carries static defaults, flags, offsets, DBUF info, and color LUT limits.

## Control Flow And State
The header itself has no runtime flow, but it defines the accessor model: `DISPLAY_INFO(display)` points to immutable static capability data, while `DISPLAY_RUNTIME_INFO(display)` points to mutable runtime data initialized from defaults and then adjusted by fuses/workarounds. Register-offset macros derive pipe/transcoder/cursor MMIO offsets from static arrays plus `DISPLAY_MMIO_BASE()`.

## Dependencies And Integration Points
It depends on `intel_display_limits.h` for stable enum sizes and pipe/port definitions. The APIs are implemented in `intel_display_device.c` and consumed by display driver probe, modeset, IRQ, power, debugfs, and feature-specific modules. The macros encode many policy decisions that downstream code treats as authoritative.

## Risks And Test Signals
Risks include stale feature predicates, mismatched static/runtime capability use, bitfield-size overflows as platform counts grow, and incorrect display-version comparisons for GMD-ID releases. Tests should include allmodconfig/build coverage, platform-specific KMS boot tests, debugfs capability dumps, feature-specific tests for PSR/DSC/FBC/MST/VRR/joiners, and stepping/workaround validation on affected SKUs.
