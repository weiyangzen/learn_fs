# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_alloc.h

Purpose: provides a simple page-fragment allocator for BPF arena selftests, with no-op user-space stubs.

Important APIs and functions: defines `bpf_alloc(size)` and `bpf_free(addr)` under `__BPF__`; uses per-CPU `page_frag_cur_page` and `page_frag_cur_offset`; calls `bpf_arena_alloc_pages()` and `bpf_arena_free_pages()` from `bpf_arena_common.h`.

Control flow: allocation rounds size to 8 bytes, rejects near-page-size requests, refills a per-CPU arena page when needed, stores an object count in the last 8 bytes, and returns space from the end downward. Free masks the object pointer to page base and decrements the page object count, freeing the page when it reaches zero.

State and persistence: allocator state lives in arena-address-space global arrays and per-page object counters. User-space builds return NULL/do nothing.

Dependencies and integration points: depends on `struct cpumask`, `PAGE_SIZE`, arena map symbol `arena`, address-space casting, and BPF kfuncs declared by `bpf_arena_common.h`.

Risks: no individual allocation metadata beyond page object count, so invalid/double frees corrupt state; no cross-CPU ownership checks; allocations larger than `PAGE_SIZE - 8` fail; object count is not atomic.

Test signals: arena data-structure tests can validate successful allocation/free, page reuse, and failure on oversized allocations.
