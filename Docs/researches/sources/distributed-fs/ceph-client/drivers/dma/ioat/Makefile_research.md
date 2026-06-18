# sources/distributed-fs/ceph-client/drivers/dma/ioat/Makefile

Purpose: declares how the Intel I/OAT DMA driver objects are built under Kbuild. When `CONFIG_INTEL_IOATDMA` is enabled, it builds one composite module/object named `ioatdma.o` from initialization, DMA engine, prep, DCA, and sysfs implementation files.

Important APIs and entries: `obj-$(CONFIG_INTEL_IOATDMA) += ioatdma.o` connects the driver to the kernel configuration symbol. `ioatdma-y := init.o dma.o prep.o dca.o sysfs.o` lists the mandatory object files linked into the composite target. There are no optional per-feature object fragments in this Makefile; DCA support code is compiled into the I/OAT object, while runtime/module parameters and platform checks decide whether DCA is registered.

Control flow: Kbuild evaluates this file during kernel build. If the config symbol is built-in, all listed objects are linked into vmlinux through the driver subtree; if modular, they become the `ioatdma` module. Link order places `init.o` before operational components, but runtime entry points are driven by module init/PCI driver registration in `init.c`.

State and persistence: no runtime state exists in the Makefile. Its persistent effect is build composition: changes alter which code is present in the driver binary and therefore which symbols are available to `init.c`, `dma.c`, `prep.c`, `dca.c`, and `sysfs.c`.

Dependencies and integration: depends on the parent DMA Kbuild including this directory and on Kconfig defining `CONFIG_INTEL_IOATDMA`. The linked object list corresponds to internal headers such as `dma.h`, `hw.h`, and `registers.h`; removing any listed object would leave unresolved driver functionality.

Risks and test signals: risks are build-only: stale object lists, missing optional guards, or file renames break compilation or silently omit functionality. Test `make drivers/dma/ioat/`, built-in and module configurations for `CONFIG_INTEL_IOATDMA`, `modinfo ioatdma`, and link errors after changing IOAT source file boundaries.
