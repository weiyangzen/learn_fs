# sources/distributed-fs/ceph-client/arch/s390/include/asm/maccess.h

Purpose: This header declares real-memory copy helpers used when normal virtual mappings are unavailable or old memory must be read after crash.

Important APIs/types/functions: `MEMCPY_REAL_SIZE`, `MEMCPY_REAL_MASK`, external `__memcpy_real_area`, `memcpy_real_ptep`, `memcpy_real_iter()`, `memcpy_real()`, and crash-dump `copy_oldmem_kernel()` are exposed.

Control flow: Implementation code maps a real physical source through a special PTE-sized window, copies into a destination or iov iterator, and in crash-dump mode reads memory from the old kernel.

State and persistence: Persistent state includes the special memcpy-real mapping area and PTE pointer; per-copy mapping changes are transient.

Dependencies and integration points: It depends on PTE types, iov_iter, crash dump configuration, and low-level memory mapping code.

Risks and test signals: Incorrect real-address mapping can read wrong memory or fault in dump paths. Tests should include `/proc/vmcore` reads, crash dump oldmem copying, page-boundary copies, and invalid physical ranges.
