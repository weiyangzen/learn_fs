<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sq.h

Purpose: defines SH-4 store-queue geometry and control register addresses.

Important APIs/types/functions: `SQ_SIZE`, `SQ_ALIGN_MASK`, `SQ_ALIGN()`, `SQ_QACR0`, `SQ_QACR1`, and `SQ_ADDRMAX`.

Control flow: callers align addresses and program QACR registers before issuing store-queue writes.

State and persistence: state lives in CPU store-queue/QACR registers, not in this header.

Dependencies/integration: used by cache/DMA/memcpy-style optimized SH-4 paths needing store queues.

Risks: bad alignment or address-range assumptions can corrupt uncached/write-combining accesses.

Test signals: compile users and exercise store-queue copy paths with aligned and unaligned buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sq.h -->
