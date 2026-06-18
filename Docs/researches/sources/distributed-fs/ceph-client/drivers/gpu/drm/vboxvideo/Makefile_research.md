# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/Makefile

## Purpose

`vboxvideo/Makefile` lists the compilation units that form the VirtualBox DRM driver module and ties them to `CONFIG_DRM_VBOXVIDEO`.

## Important APIs, Types, and Functions

- `vboxvideo-y`: includes HGSMI helpers, modesetting protocol helpers, VBVA ring support, PCI driver glue, IRQ, hardware init, KMS mode code, and VRAM memory manager code.
- `obj-$(CONFIG_DRM_VBOXVIDEO) += vboxvideo.o`: builds the composite object when configured.

## Control Flow

Kbuild compiles each listed object and links them into `vboxvideo.o`. The resulting module registers the PCI DRM driver defined in `vbox_drv.c`.

## State and Persistence Behavior

No runtime state. Ordering here only affects link composition; init order is controlled by driver code.

## Dependencies and Integration Points

It must stay synchronized with function declarations in `vbox_drv.h` and Kconfig selections. Removing any object breaks driver paths such as HGSMI buffer allocation or atomic modesetting.

## Risks and Edge Cases

New source files need explicit addition. The list is small, so omissions become link-time undefined references.

## Test Signals

Build the module and verify all exported internal functions resolve, especially `hgsmi_*`, `vbva_*`, `vbox_mode_init`, `vbox_hw_init`, and `vbox_irq_init`.
