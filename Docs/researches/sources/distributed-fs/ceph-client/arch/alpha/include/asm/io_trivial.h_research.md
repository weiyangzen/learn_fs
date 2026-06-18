# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/io_trivial.h

This header is a reusable template for chipset backends whose I/O mapping is already linear. It may be included multiple times with different `__IO_PREFIX` and `*_trivial_*` feature macros.

When enabled, it emits prefixed `ioread8/16`, `iowrite8/16`, `ioread32/64`, `iowrite32/64`, raw `readb/readw/readl/readq`, `writeb/writew/writel/writeq`, and a no-op `iounmap`. Byte and word operations use Alpha byte/word helper instructions (`__kernel_ldbu`, `__kernel_ldwu`, `__kernel_stb`, `__kernel_stw`); long and quad operations use volatile direct loads/stores. `trivial_rw_bw == 2` routes read/write through ioread/iowrite instead of direct load/store.

State is only the addressed device memory. Integration is with every linear `core_*.h` backend and `asm/io.h` barrier wrappers. Risks are macro hygiene from multiple inclusion, using direct operations for non-linear spaces, and missing force/volatile semantics. Tests are compile coverage for each backend prefix and runtime I/O on linear chipsets.
