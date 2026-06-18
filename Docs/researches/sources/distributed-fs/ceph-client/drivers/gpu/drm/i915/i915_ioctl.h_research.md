# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioctl.h

## Purpose
Declares the small ioctl helper implemented by `i915_ioctl.c`.

## Important APIs, types, and functions
Forward declares `struct drm_device` and `struct drm_file`; exports `i915_reg_read_ioctl()`.

## Control flow
No runtime flow exists in the header. DRM ioctl tables call the declared function.

## State and persistence
No state is defined.

## Dependencies and integration points
Connects the i915 ioctl dispatch table to the register-read implementation.

## Risks
API drift is compile-time visible. The header intentionally avoids exposing whitelist internals.

## Test signals
Build coverage and ioctl table registration validate the declaration.
