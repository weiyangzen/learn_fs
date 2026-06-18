# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioctl.c

## Purpose
Hosts small i915 ioctl helpers that do not warrant their own larger subsystem file. Currently it implements whitelisted MMIO register reads for userspace.

## Important APIs, types, and functions
Defines `struct reg_whitelist`, `reg_read_whitelist[]`, and public `i915_reg_read_ioctl()`. The only whitelist entry exposes the render ring timestamp as a 64-bit register across graphics versions 4 through 12.

## Control flow
The ioctl scans the whitelist for an entry matching the requested offset, graphics version range, and alignment. It extracts low offset bits as flags, takes a runtime PM wakeref, then reads using the correct uncore width helper. For 64-bit registers it supports either direct `intel_uncore_read64()` or the `I915_REG_READ_8B_WA` two-32-bit workaround.

## State and persistence
No persistent state is changed. The ioctl returns the sampled MMIO value in the userspace request structure.

## Dependencies and integration points
Depends on DRM ioctl plumbing, i915 runtime PM, uncore MMIO accessors, register definitions for ring timestamps, and graphics-version predicates.

## Risks
The whitelist is a security boundary. Adding registers can expose privileged hardware state or unstable ABI. Alignment and flag validation prevent arbitrary byte-offset reads. Runtime PM coverage is required so timestamp MMIO is valid while the device may be suspended.

## Test signals
Exercise `DRM_IOCTL_I915_REG_READ` for valid timestamp offsets and the 8-byte workaround flag on supported gens; verify unsupported offsets, misaligned flags, and unsupported platforms return `-EINVAL`.
