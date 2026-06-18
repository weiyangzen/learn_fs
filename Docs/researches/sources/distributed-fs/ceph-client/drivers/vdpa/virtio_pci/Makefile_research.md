# sources/distributed-fs/ceph-client/drivers/vdpa/virtio_pci/Makefile

## Purpose

This Makefile builds the virtio-pci vDPA bridge driver. When `CONFIG_VP_VDPA` is enabled, it adds `vp_vdpa.o` to the kernel build.

## Important APIs, Types, and Functions

There are no functions or types. The only build rule is `obj-$(CONFIG_VP_VDPA) += vp_vdpa.o`, which connects the Kconfig option to `vp_vdpa.c`.

## Control Flow

Kbuild evaluates the `obj-*` assignment while descending into `drivers/vdpa/virtio_pci`. If `CONFIG_VP_VDPA=y`, the object is built into the kernel; if `m`, it becomes a module; if unset, the file is not compiled.

## State and Persistence Behavior

The file has no runtime state or persistence. Its only persistent effect is on the generated kernel or module artifact.

## Dependencies and Integration Points

It depends on the surrounding Kbuild tree selecting this directory and on the `CONFIG_VP_VDPA` option being defined elsewhere. Its integration target is the `vp_vdpa.c` module.

## Risks and Edge Cases

The main risk is build drift: if the source filename or Kconfig symbol changes, this Makefile must change with it. Since the directory contains a single object, there is little ordering risk.

## Test Signals

Build with `CONFIG_VP_VDPA=y`, `m`, and unset to verify built-in, module, and excluded outcomes.
