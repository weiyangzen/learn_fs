# sources/distributed-fs/ceph-client/include/uapi/drm/nova_drm.h

## Purpose

`nova_drm.h` is an explicitly unstable testing UAPI for the in-development Nova driver. It currently exposes a VRAM BAR size getparam and minimal GEM create/info operations. The complete 101-line header was read.

## Important APIs, Types, and Functions

The header defines `NOVA_GETPARAM_VRAM_BAR_SIZE`, `drm_nova_getparam`, `drm_nova_gem_create`, and `drm_nova_gem_info`. Ioctl IDs are `DRM_NOVA_GETPARAM`, `DRM_NOVA_GEM_CREATE`, and `DRM_NOVA_GEM_INFO`; ioctl numbers are emitted via an anonymous enum for Rust bindgen compatibility.

## Control Flow

Userspace can query metadata with `GETPARAM`, create a GEM object by size with `GEM_CREATE`, and query a GEM object's size with `GEM_INFO`. No submission, synchronization, mmap offset, VM, or queue ABI is present.

## State and Persistence Behavior

GEM handles persist under standard DRM lifetime. The header explicitly says the ABI is not stable and is only for driver infrastructure testing while Nova is under development.

## Dependencies and Integration Points

Depends on `drm.h`. Integrates with early Nova kernel infrastructure, GEM allocation, and C/Rust userspace binding generation.

## Risks and Edge Cases

External reliance is unsafe because fields and ioctl semantics may change. The driver still must validate sizes, zero padding, unknown parameters, invalid handles, and the enum-based ioctl values for C and Rust consumers.

## Test Signals

Cover bindgen resolution, VRAM BAR getparam, GEM create size alignment and failure cases, GEM info valid/invalid handles, padding rejection, and C/Rust build coverage.
