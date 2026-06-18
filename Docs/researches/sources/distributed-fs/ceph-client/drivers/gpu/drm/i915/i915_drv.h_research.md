# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drv.h

## Purpose
`i915_drv.h` is the central private i915 device header. It defines `struct drm_i915_private`, key driver-wide state containers, platform and feature predicates, and conversion helpers used across GEM, GT, display, PM, perf, error capture, virtualization, and memory-management code.

## Important APIs, Types, and Functions
Major types include `struct i915_dsm`, `struct intel_l3_parity`, `struct i915_gem_mm`, `struct i915_virtual_gpu`, `struct i915_selftest_stash`, and `struct drm_i915_private`. Helper inlines convert `drm_device`, `device`, and `pci_dev` to i915 private state and return the root GT. Macros expose device/runtime info (`INTEL_INFO`, `RUNTIME_INFO`, `DRIVER_CAPS`, `INTEL_DEVID`, `GRAPHICS_VER`, `MEDIA_VER`, stepping accessors), platform checks (`IS_PLATFORM`, `IS_SUBPLATFORM`, specific platform/subplatform macros), and feature checks (`HAS_LLC`, `HAS_EDRAM`, `HAS_EXECLISTS`, `HAS_PPGTT`, `HAS_LMEM`, `HAS_GT_UC`, `HAS_RUNTIME_PM`, `HAS_PXP`, and many others).

## Control Flow
There is no runtime algorithm beyond inline predicates. The macros are used throughout i915 to select platform workarounds, register programming paths, memory behavior, UAPI answers, power features, PPGTT support, GuC/PXP capabilities, and display/GT quirks. `IS_PLATFORM()` and `IS_SUBPLATFORM()` compute bit positions inside runtime platform masks and assert that platform constants are compile-time constants.

## State and Persistence Behavior
`drm_i915_private` persists for the DRM device lifetime. It owns the embedded `drm_device`, display pointer, release flag, parameters, static and runtime device info, stolen memory data, uncore, virtual GPU state, GVT pointer, GMCH bridge/MCHBAR state, user engine containers, IRQ state, sideband locks, ordered and unordered workqueues, GEM memory manager, L3 parity state, eDRAM size, GPU error state, suspend count, runtime PM, perf, hwmon, GT array, media GT quick lookup, GEM context/mmap singleton state, frontbuffer lock, PXP, overlay, PMU, TTM device, and optional selftest stash.

## Dependencies and Integration Points
The header pulls together UAPI, TTM, GEM context/shrinker/stolen types, GT and GuC types, error capture, params, perf, scheduler, runtime PM, uncore, memory regions, and device info. Almost every i915 subsystem depends on this header for feature predicates and root device state.

## Risks
This header is a dependency hub, so additions can create include cycles or widespread rebuild cost. Platform predicates are correctness-critical; a wrong feature macro can select unsafe register sequences or expose unsupported UAPI. `struct drm_i915_private` layout embeds `drm_device` first and display immediately after it, and `i915_driver.c` asserts the display member placement. State fields have subsystem-specific locking rules that are not all enforced locally.

## Test Signals
Build coverage across many config combinations is essential. Runtime signals include correct platform/subplatform names, feature macro behavior in `i915_welcome_messages`, successful probe on old and new platforms, selftests for GEM/GT paths using predicates, suspend/resume behavior, and no sparse/lockdep warnings from state access.
