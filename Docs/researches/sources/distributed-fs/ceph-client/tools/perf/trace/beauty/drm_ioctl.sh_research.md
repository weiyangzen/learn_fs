# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/drm_ioctl.sh

## Purpose
This generator builds a DRM ioctl command-name array for perf trace ioctl beautification.

## Important APIs, Types, And Functions
The script takes an optional DRM header directory, reads `drm.h` and `i915_drm.h`, and emits `static const char *drm_ioctl_cmds[]`. It preserves `DRM_COMMAND_BASE` with a guarded preprocessor definition before the array.

## Control Flow
It prints `#ifndef DRM_COMMAND_BASE`, copies the `DRM_COMMAND_BASE` define from `drm.h`, then parses generic `DRM_IOCTL_* DRM_IO*` macros into array entries indexed by the ioctl command number. It separately parses i915 private command macros and indexes them at `DRM_COMMAND_BASE + value` with `I915_` prefixes.

## State, Dependencies, And Integration
Output is redirected by `Makefile.perf` into the generated ioctl table included by `trace/beauty/ioctl.c`. It depends on grep/sed regexes and header macro formatting.

## Risks And Test Signals
Format drift in DRM headers can silently drop commands. Device-specific coverage is limited here to i915. Tests should confirm `perf trace` formats common DRM ioctls as `DRM_*` and i915 private ioctls as `DRM_I915_*` names.
