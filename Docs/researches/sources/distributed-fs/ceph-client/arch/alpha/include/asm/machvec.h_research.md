# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/machvec.h

This header defines `struct alpha_machine_vector`, the generic-kernel dispatch table for platform-specific I/O, IRQ, PCI, AGP, machine-check, SMP, RTC, and shutdown behavior. The first fields are HAE cache/register for assembly convenience, followed by platform limits and many function pointers.

Important vector fields include IRQ counts, RTC settings, max ASN, ISA DMA limit, IACK address, minimum I/O/MEM addresses, PCI DAC offset, PCI TBI, ioread/iowrite/read/write families, map/unmap/classification hooks, interrupt update/ack/device handlers, machine check handler, init hooks, PCI swizzle/map_irq/ops, AGP info, vector name, and small platform-specific parameter union.

State is the global `alpha_mv`, plus generic flags `alpha_using_srm` and `alpha_using_qemu`. Integration is central for `CONFIG_ALPHA_GENERIC`; `asm/io.h`, DMA, IRQ, PCI, cache/TB, and platform init all depend on it. Risks are uninitialized function pointers, vector mismatch with detected hardware, and keeping the first two fields stable for assembly. Tests are generic Alpha boot on multiple platforms and QEMU/SRM detection.
