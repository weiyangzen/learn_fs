# sources/distributed-fs/ceph-client/kernel/bpf/arena.c

Purpose: implements `BPF_MAP_TYPE_ARENA`, a sparse shared virtual memory arena visible to userspace through mmap and to BPF programs through JIT-supported arena addressing and kfunc page allocation.

Important APIs/types/functions: `struct bpf_arena` embeds `struct bpf_map`, user and kernel VM ranges, a `range_tree`, locks, tracked VMAs, and deferred free queues. Map ops include `arena_map_alloc`, `arena_map_free`, `arena_map_mmap`, `arena_get_unmapped_area`, and `arena_map_direct_value_addr`. Page lifecycle is handled by `arena_alloc_pages`, `arena_free_pages`, `arena_reserve_pages`, `arena_free_worker`, and `arena_free_irq`. BPF kfuncs are `bpf_arena_alloc_pages`, `bpf_arena_free_pages`, and `bpf_arena_reserve_pages`, plus non-sleepable internal variants. `bpf_prog_report_arena_violation` reports JIT arena faults.

Control flow: map creation validates mmapable 64-bit/MMU/JIT support, address range, flags, and 32-bit user address window, reserves a guarded 4GB-ish kernel vmalloc area, initializes the free range tree, and pre-populates upper page tables except PTEs. mmap fixes a single shared userspace range and records VMAs. User faults either map an already allocated kernel page or allocate one unless `BPF_F_SEGV_ON_FAULT` requests SIGSEGV. BPF kfunc allocation clears range-tree availability, allocates pages in batches, maps them into kernel vmalloc PTEs, and returns the userspace address. Freeing clears kernel PTEs, flushes TLB/cache, zaps user VMAs, and frees pages; non-sleepable failures defer through irq_work/workqueue.

State and persistence: arena state lives for the BPF map lifetime. Allocated pages persist until explicitly freed or map destruction. `range_tree` records unallocated/reserved ranges; VMA list tracks active mmaps; `free_spans` persists deferred frees until workqueue drain. It does not support ordinary lookup/update/delete semantics.

Dependencies and integration: depends on BPF map memory accounting, JIT arena support hooks, BTF kfunc registration, vmalloc/page-table APIs, TLB/cache flushing, range-tree support, memcg charging, user VMA fault handling, irq_work, workqueues, and BPF stream diagnostics.

Risks: page table manipulation, TLB lifetime, and shared user/kernel mappings are high risk. Address calculations intentionally use lower 32 bits; validation must prevent crossing boundaries. Failed non-sleepable deferred-free allocation intentionally leaks until arena destruction. Incorrect VMA tracking can free a map with active mappings or leave stale user mappings. JITs must match the addressing contract.

Test signals: BPF arena selftests should cover mmap address selection, `BPF_F_SEGV_ON_FAULT`, kfunc allocation/free/reserve, non-sleepable paths, user faults after BPF allocation, map teardown with no VMAs, and arena violation reports. KASAN/KCSAN, memcg, and TLB stress are especially relevant.
