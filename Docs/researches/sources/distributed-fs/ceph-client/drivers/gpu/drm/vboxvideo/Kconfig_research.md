# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/Kconfig

## Purpose

`vboxvideo/Kconfig` declares the VirtualBox DRM/KMS driver option `DRM_VBOXVIDEO`. It controls whether the virtual graphics card driver is built and records its architectural and helper-library dependencies.

## Important APIs, Types, and Functions

- `config DRM_VBOXVIDEO`: tristate option named "Virtual Box Graphics Card".
- Dependencies: `DRM`, `X86`, and `PCI`.
- Selected helpers: DRM client selection, KMS helper, VRAM helper, TTM, TTM helper, and generic allocator.

## Control Flow

When enabled, Kbuild compiles the `vboxvideo` object listed in the local Makefile. The help text recommends module builds so the VM graphics driver can be updated independently of the kernel.

## State and Persistence Behavior

This file has no runtime state. It persists build-time configuration in `.config`, determining whether the PCI module is available.

## Dependencies and Integration Points

It integrates with the DRM Kconfig tree, PCI/X86 platform selection, and helper libraries used by `vbox_drv.c`, `vbox_ttm.c`, and HGSMI/VBVA allocation code.

## Risks and Edge Cases

Missing selected helpers would surface as build failures. The X86 dependency excludes non-x86 VirtualBox graphics users even if the virtual device could theoretically appear elsewhere.

## Test Signals

Build `CONFIG_DRM_VBOXVIDEO=m` and `=y` in x86 DRM configs, verify helper symbols are selected, and confirm non-x86 configs do not offer the option.
