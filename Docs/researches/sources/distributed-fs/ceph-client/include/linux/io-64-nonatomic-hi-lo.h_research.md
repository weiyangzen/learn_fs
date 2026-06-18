# sources/distributed-fs/ceph-client/include/linux/io-64-nonatomic-hi-lo.h

Purpose: This header supplies fallback non-atomic 64-bit MMIO accessors for hardware that requires the high 32-bit half to be accessed before the low half.

Important APIs, types, and functions: It defines `hi_lo_readq`, `hi_lo_writeq`, relaxed variants, `ioread64_hi_lo`, `iowrite64_hi_lo`, big-endian variants, and conditional aliases for `readq`, `writeq`, `ioread64`, and `iowrite64` when the architecture has not already defined them.

Control flow: Reads perform two 32-bit accesses in high-then-low order and combine as `low + ((u64)high << 32)`. Writes split the 64-bit value and emit high then low. Big-endian helpers reverse address interpretation appropriately. Generic iomap plus 64-bit builds can redirect to `__ioread64_hi_lo`/`__iowrite64_hi_lo`.

State and persistence: No persistent state is held; behavior is entirely compile-time aliasing and inline MMIO operations.

Dependencies and integration points: Depends on `linux/io.h` and `asm-generic/int-ll64.h`. Device drivers include this when register semantics mandate high-low ordering and native 64-bit accessors are absent.

Risks: Accesses are explicitly non-atomic, so hardware registers that change between halves can return torn values. Using this for devices that require low-high order can trigger side effects or wrong latching. Relaxed variants omit normal ordering guarantees.

Test signals: Build tests should verify alias selection across arch/native/generic-iomap combinations. Driver tests should validate hardware register ordering, endian behavior, relaxed-vs-ordered barriers, and read consistency for counters or latch registers.
