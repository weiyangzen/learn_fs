# sources/distributed-fs/ceph-client/arch/mips/lib/iomap_copy.c

Purpose: provides `__ioread64_copy` for copying MMIO data into memory in 64-bit units.

Important APIs/functions: exports `__ioread64_copy`.

Control flow: on 64-bit kernels, loops from source to end and copies via `__raw_readq`; on 32-bit kernels, delegates to `__ioread32_copy` with doubled count.

State and persistence: writes destination buffer only.

Dependencies and integration: used by generic IO copy helpers and device drivers reading MMIO FIFOs or buffers.

Risks: access order is not guaranteed and no barrier is issued. Caller must provide 64-bit aligned pointers and correct count.

Test signals: driver IO-copy tests, 32/64-bit build coverage, and device-specific data integrity checks.
