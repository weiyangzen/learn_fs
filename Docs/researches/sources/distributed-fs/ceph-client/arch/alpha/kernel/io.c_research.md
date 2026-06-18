# sources/distributed-fs/ceph-client/arch/alpha/kernel/io.c

**Purpose:** Provides out-of-line Alpha I/O accessors and exported I/O memory helpers. It wraps platform-specific `__IO_PREFIX` operations with required memory barriers, implements port I/O helpers, raw and ordered MMIO helpers, repeated string I/O, `memcpy_fromio()`, `memcpy_toio()`, I/O memset, VGA screen copy/move helpers, and `ioport_map()`.

**Important APIs/types/functions:** Exports `ioread8/16/32/64`, `iowrite8/16/32/64`, `inb/inw/inl`, `outb/outw/outl`, `__raw_read*`, `__raw_write*`, `read*`, `write*`, `read*_relaxed`, `ioread*_rep`, `iowrite*_rep`, `ins*`, `outs*`, `memcpy_fromio()`, `memcpy_toio()`, `_memset_c_io()`, `scr_memcpyw()`, `scr_memmovew()`, `ioport_map()`, and `ioport_unmap()`.

**Control flow:** All generic accessors delegate through `IO_CONCAT(__IO_PREFIX, ...)`, where compile/machine-vector setup supplies the backend. Ordered reads use barriers before and after; ordered writes use a leading barrier; relaxed reads still use a barrier to order against each other. Repeated I/O functions coalesce aligned byte/word transfers where possible and handle unaligned 32-bit buffers with packed temporary structs. Copy/memset functions widen transfers when source/destination I/O and memory addresses are co-aligned, then finish tails bytewise. VGA helpers choose raw I/O, `memcpy_fromio()`, `memcpy_toio()`, or normal `memcpy()` based on `__is_ioaddr()`.

**State and persistence behavior:** No persistent state. The functions mutate device-visible I/O memory/ports and enforce ordering through Alpha memory barriers. `ioport_unmap()` is a no-op because mapped port tokens are direct machine-vector translations.

**Dependencies and integration points:** Depends on `<asm/io.h>` inline backends and machine-vector-selected `__IO_PREFIX`. Drivers and subsystems use this exported ABI for all Alpha I/O, including PCI sysfs legacy reads/writes and ISA helper code.

**Risks:** Ordering is architecture-critical; removing barriers can break drivers. The `ioread64()` implementation stores into `unsigned int ret` before returning `u64`, which is a suspicious truncation risk if the backend returns true 64-bit values. Repeated access alignment assumptions and packed struct use must match Alpha unaligned-access behavior.

**Test signals:** Build drivers that use every exported width and repeated I/O path; run MMIO ordering tests, IDE/PIO transfer tests, framebuffer/VGA console operations, unaligned buffer tests, and module symbol resolution. Static analysis should flag the `ioread64()` local type mismatch for review.
