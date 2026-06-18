# sources/distributed-fs/ceph-client/arch/arm64/kernel/io.c

Purpose: Implements optimized aligned MMIO copy helpers for 64-bit and 32-bit full-width writes.

Important APIs: `__iowrite64_copy_full()` and `__iowrite32_copy_full()` are exported. The `memcpy_toio_aligned()` macro batches copies in groups of eight, four, two, and one element and calls constant-sized aligned MMIO helper routines.

Control flow and state: functions copy a caller-provided count of 64-bit or 32-bit quantities to an I/O memory address, then issue `dgh()` to provide a data gathering hint barrier. No persistent state exists.

Dependencies and integration: integrates with generic Linux I/O helpers and drivers that need posted/write-combining-friendly bulk MMIO writes. Requires aligned source/destination expectations implied by the full-copy helper name.

Risks and test signals: risks include callers passing unaligned addresses, incorrect count units, or devices requiring stricter barriers. Test with driver MMIO copy users, sparse `__iomem` checks, KASAN/KMSAN where applicable, and device-level DMA/MMIO functional tests.
