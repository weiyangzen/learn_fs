# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/Kconfig

## Purpose
Defines the build-time configuration option for the experimental Rust Nova DRM driver for NVIDIA GSP-based GPUs.

## Important APIs, Types, And Functions
`config DRM_NOVA` is a tristate depending on 64-bit, built-in DRM, PCI, and Rust; it selects `AUXILIARY_BUS` and `NOVA_CORE`.

## Control Flow
When enabled, Kconfig allows building the `nova` module and pulls in the auxiliary bus and Nova core support required by the Rust DRM frontend.

## State, Persistence, And Dependencies
No runtime state exists here; it controls kernel configuration.

## Integration Points
Integrated by the DRM Kconfig hierarchy and Nova Makefile. It constrains the driver to platforms where Rust, PCI, and DRM prerequisites exist.

## Risks
The option depends on `DRM=y`, not module DRM, which limits build combinations. Help text warns the driver is work in progress and may not function.

## Test Signals
Signals are Kconfig dependency resolution and successful `CONFIG_DRM_NOVA=m/y` builds with Rust enabled.
