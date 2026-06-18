# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-work-area.c

Purpose: Provides RTAS-addressable temporary work-area allocation with an early-boot fallback and a bounded runtime gen_pool/mempool allocator.

Important APIs/types/functions: Defines allocation constants, global `rwa_state`, early static work area, `__rtas_work_area_alloc()`, `rtas_work_area_free()`, `rtas_work_area_allocator_init()`, and `rtas_work_area_reserve_arena()`.

Control flow: Early callers get a single aligned static 4 KiB buffer. Early boot reserves a low-memory arena if relevant RTAS functions exist. Later arch init creates a gen_pool over that arena plus a descriptor mempool, marks the allocator available, and regular allocations queue under a mutex then wait on a waitqueue for first-fit aligned space. Frees return space and wake waiters.

State and persistence: Runtime state includes the reserved arena pointer, gen_pool, descriptor mempool, availability flag, mutex, waitqueue, and early in-use flag.

Dependencies and integration points: Used by PAPR sysparm, VPD, and other RTAS call wrappers needing firmware-accessible buffers. Depends on memblock, genalloc, mempool, RTAS token discovery, and pseries init ordering.

Risks: Requests larger than `RTAS_WORK_AREA_MAX_ALLOC_SZ` warn but could block indefinitely if bypassing wrapper checks. Early work area supports only one in-flight allocation. Allocation fairness relies on serializing waiters with the mutex.

Test signals: Early sysparm calls before allocator init, concurrent runtime allocations of mixed sizes, allocation/free wakeups, exhausted pool behavior, RTAS work-area physical address validity, and warning paths for oversize or double-free early use.

Source read size: 210 lines, 6524 bytes.
