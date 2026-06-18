# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/dpaa_sys.c

Purpose: shared DPAA helper for initializing QBMan private reserved memory. It locates a reserved-memory node, returns base/size, and patches a missing `reg` property so kexec preserves the same memory placement.

Important APIs and functions: `qbman_init_private_mem(struct device *dev, int idx, const char *compat, dma_addr_t *addr, size_t *size)` first checks the device's `memory-region` phandle at `idx`, then falls back to a compatible search, then calls `of_reserved_mem_lookup()`.

Control flow: after finding reserved memory, it writes base and size to outputs. If the node lacks `reg`, it devm-allocates a `struct property`, four big-endian cells for 64-bit base/size, a `reg` name string, and adds the property to the live OF tree with `of_add_property()`.

State and persistence: no module-global state. It mutates the live device tree by adding `reg` when absent; that mutation persists for the running kernel and supports kexec address preservation.

Dependencies and integration: used by BMan CCSR and likely QMan CCSR. Depends on OF reserved memory, dynamic OF property modification, and device-managed allocation.

Risks and test signals: risks include fallback compatible finding the wrong node, adding properties to immutable or unexpected live tree state, and the DMA API caveat that memory is not backed by `struct page`. Test signals are BMan/QMan private memory base/size logs, kexec retaining FBPR/FQD/PFDR regions, and no `of_add_property()` failures.
