# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_compat.h

Purpose: provides small architecture-compatibility helpers for copying between host memory and the adapter SLI memory window. The driver notes that HBA SLI memory stores little-endian longwords, so big-endian hosts must access it a word at a time while little-endian hosts can use normal I/O copy helpers.

Important APIs/functions: `lpfc_memcpy_to_slim(void __iomem *dest, void *src, unsigned int bytes)` writes host data to SLI memory. `lpfc_memcpy_from_slim(void *dest, void __iomem *src, unsigned int bytes)` reads SLI memory into host data. On big-endian builds these functions loop over `uint32_t` words using `writel()`/`readl()`, with a read flush after each write. On other builds they call `__iowrite32_copy()` and `memcpy_fromio()`.

Control flow: compile-time `#ifdef __BIG_ENDIAN` selects the implementation. Both variants convert the byte count into 32-bit word operations for writes; the big-endian read path also operates in 32-bit units. There is no runtime branching, allocation, locking, or error handling.

State and persistence: these helpers persist no state. They perform immediate MMIO or I/O-memory copies and rely on callers to pass valid SLI memory addresses, aligned buffers, and byte counts that make sense as 32-bit word counts.

Dependencies and integration: depends on `<asm/byteorder.h>` for endian detection and on Linux I/O accessors (`writel`, `readl`, `__iowrite32_copy`, `memcpy_fromio`). Integrated by lpfc low-level SLI/mailbox paths that copy to or from the adapter's SLIM region, especially on pre-SLI4 or memory-window interactions.

Risks: callers passing byte counts not divisible by four will silently ignore tail bytes in the word-loop and write-copy paths. The big-endian code casts `void *` to `uint32_t *`, so unaligned source/destination buffers would be unsafe on strict-alignment architectures. There is no bounds checking for the MMIO region. Ordering relies on `readl()` flushes in the big-endian write path and the semantics of the architecture I/O helpers elsewhere.

Test signals: compile both big-endian and little-endian configurations, including sparse checking of `__iomem` casts. Unit or hardware-in-loop tests should copy known multiword patterns to/from a mock or real SLIM region, include non-cacheable I/O memory ordering checks, and assert behavior for lengths that are exact multiples of four. Static analysis should flag any callers that pass non-word-aligned sizes.
