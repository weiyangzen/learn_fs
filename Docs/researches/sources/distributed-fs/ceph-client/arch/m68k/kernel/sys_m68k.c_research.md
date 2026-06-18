# sources/distributed-fs/ceph-client/arch/m68k/kernel/sys_m68k.c

## Purpose

`sys_m68k.c` implements m68k-specific syscalls and syscall variants with nonstandard calling conventions: `mmap2`, cache flushing, atomic compare-exchange, page size, thread pointer, and a uniprocessor atomic barrier.

## Important APIs, Types, and Functions

Important exported syscall entry points are `sys_mmap2()`, `sys_cacheflush()`, `sys_atomic_cmpxchg_32()`, `sys_getpagesize()`, `sys_get_thread_area()`, `sys_set_thread_area()`, and `sys_atomic_barrier()`. Internal MMU helpers include `cache_flush_040()`, `cache_flush_060()`, `virt_to_phys_040`, and `virt_to_phys_060`.

## Control Flow

`sys_mmap2()` forwards to `ksys_mmap_pgoff()` while noting Sun3 page-size complications. On MMU builds, `sys_cacheflush()` validates scope/cache bits, requires `CAP_SYS_ADMIN` for whole-cache flush, verifies non-global address ranges against the current VMA, then selects 020/030 CACR flush behavior or 040/060 physical-address `cpush*` loops. Long requested line/page flushes are promoted to broader scopes to prevent excessive work. On no-MMU builds it simply calls `flush_cache_all()`.

`sys_atomic_cmpxchg_32()` on MMU builds manually walks page tables under `mmap_read_lock()`, verifies the target PTE is present, dirty, and writable, then performs get/put user operations under the PTE lock. If the page is absent or copy-on-write, it synthesizes a write page fault and retries. No-MMU builds directly compare and update under the mmap read lock.

## State and Persistence Behavior

Cache flush syscalls mutate CPU cache state. Atomic compare-exchange mutates user memory when the old value matches and can fault pages into writable state. Thread-area syscalls read/write `current_thread_info()->tp_value`.

## Dependencies and Integration Points

The file depends on cache-control ABI constants, m68k CPU feature macros, page-table APIs, `do_page_fault()`, generic memory mapping, user access helpers, and syscall table generation.

## Risks and Edge Cases

`sys_cacheflush()` must avoid overflowing `addr + len` and must not flush arbitrary process memory without VMA validation. Physical address translation can skip unmapped pages, so partial ranges may be no-ops. The atomic syscall constructs a `pt_regs *` from syscall arguments to call `do_page_fault()`, a delicate ABI dependency. No-MMU direct `*mem` access assumes flat valid user memory.

## Test Signals

Run cacheflush ABI tests for line/page/all scopes, permission checks for whole-cache flush, mmaped JIT/self-modifying code tests, COW atomic compare-exchange tests, invalid pointer fault tests, and TLS get/set tests.
