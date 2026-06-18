# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/Makefile

## Purpose
Connects the Nova DRM Rust module to the kernel build.

## Important APIs, Types, And Functions
`obj-$(CONFIG_DRM_NOVA) += nova.o` builds the Rust module object when the Kconfig option is enabled.

## Control Flow
The kernel build system compiles the Rust crate rooted at `nova.rs` into `nova.o` for enabled configurations.

## State, Persistence, And Dependencies
No runtime state exists here.

## Integration Points
Integrated by the DRM GPU Makefile and Kconfig option `DRM_NOVA`.

## Risks
Any missing Rust module source or symbol errors surface only at build time.

## Test Signals
Build success with `CONFIG_DRM_NOVA` enabled is the main signal.
