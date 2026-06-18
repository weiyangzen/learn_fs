<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/percpu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/percpu.h

## Purpose
This header defines PowerPC percpu access plumbing, especially the PPC64 fast path using PACA `data_offset`, and first-chunk paged detection.

## Important APIs, Types, And Functions
On PPC64 SMP it defines `__my_cpu_offset` as `local_paca->data_offset`. With `CONFIG_NEED_PER_CPU_PAGE_FIRST_CHUNK` and SMP it declares `__percpu_first_chunk_is_paged` and defines `percpu_first_chunk_is_paged` through a static key; otherwise it is false. It includes generic percpu support and PACA as needed.

## Control Flow
Per-CPU access code reads the current CPU offset from PACA. Static-key logic lets callers branch cheaply on whether the first percpu chunk is paged.

## State And Persistence Behavior
Per-CPU offsets are persistent per CPU in PACA. The first-chunk static key reflects allocator setup state after boot.

## Dependencies And Integration Points
It depends on PPC64 PACA, generic percpu, SMP, and jump labels. It integrates with all per-CPU variable access and percpu allocator setup.

## Risks And Edge Cases
`local_paca` must be valid before percpu fast paths execute. Incorrect `data_offset` corrupts per-CPU storage. Static-key state must match the actual first-chunk mapping.

## Test Signals
Boot PPC64 SMP and UP, run CPU hotplug, percpu allocator tests, and debug per-CPU access checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/percpu.h -->
