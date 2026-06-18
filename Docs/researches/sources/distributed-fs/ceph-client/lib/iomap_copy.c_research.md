# sources/distributed-fs/ceph-client/lib/iomap_copy.c

Purpose: supplies generic raw copy helpers between normal memory and MMIO address space, in fixed-width units, for architectures that do not override them.

Important APIs: `__iowrite32_copy()` writes 32-bit quantities to MMIO; `__ioread32_copy()` reads 32-bit quantities from MMIO; `__iowrite64_copy()` writes 64-bit quantities on 64-bit builds or delegates to the 32-bit copy helper on 32-bit builds. All are GPL-exported where compiled.

Control flow: each helper casts source and destination to unit pointers, computes an end pointer from `count`, and loops with `__raw_writel`, `__raw_readl`, or `__raw_writeq`. No byte swapping, ordering barrier, or alignment repair is performed.

State and persistence: no persistent state. Progress exists only in local source/destination pointers.

Dependencies and integration: depends on `linux/io.h` raw MMIO accessors and export infrastructure. It backs driver helpers that need fast bulk register/window access while leaving ordering to callers.

Risks: callers must pass correctly aligned buffers and counts in units, not bytes. Raw access means no endian conversion and no memory barrier, so device protocols that need ordering must add barriers externally. The 32-bit fallback for 64-bit writes doubles the 32-bit count, which assumes the device accepts equivalent 32-bit sequencing.

Test signals: compile on 32-bit and 64-bit; architecture override coverage; driver tests that compare expected FIFO/window contents; sparse `__iomem` checks.
