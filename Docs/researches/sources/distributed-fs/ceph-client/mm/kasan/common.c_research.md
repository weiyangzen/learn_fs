## sources/distributed-fs/ceph-client/mm/kasan/common.c

Purpose: implements mode-independent KASAN runtime integration with page allocation, slab allocation, kmalloc redzones, mempools, stack tracking, task stack unpoisoning, and vmalloc resize handling.

Important APIs and functions: key entry points include `kasan_addr_to_slab()`, `kasan_save_stack()`, `kasan_set_track()`, `kasan_save_track()`, `__kasan_unpoison_pages()`, `__kasan_poison_pages()`, `__kasan_poison_slab()`, `__kasan_init_slab_obj()`, `__kasan_slab_pre_free()`, `__kasan_slab_free()`, `__kasan_slab_alloc()`, `__kasan_kmalloc()`, `__kasan_kmalloc_large()`, `__kasan_krealloc()`, mempool poison/unpoison helpers, `__kasan_check_byte()`, and vmalloc helpers under `CONFIG_KASAN_VMALLOC`.

Control flow: allocation paths assign or reuse tags, unpoison accessible bytes, poison redzones, and save allocation stack data when enabled. Free paths validate object identity and byte accessibility, report invalid or double frees, poison the object as freed, save free stack information, and optionally divert it into quarantine. Page alloc paths skip highmem, respect hardware-tag sampling, set per-page tags, and poison freed pages. Vmalloc paths coordinate tags across multiple `vm_struct`s and handle `vrealloc()` shrink/grow poisoning.

State and persistence: state is stored in page tags, slab object shadow/tag metadata, stack depot handles, current task KASAN depth for generic/SW tags, quarantine state, and static key `kasan_flag_enabled` for deferred/hardware tag modes.

Dependencies and integration: integrates with slab internals, KFENCE bypasses, page allocator hooks, mempool hooks, stackdepot, scheduler/task stacks, vmalloc, and mode-specific poison primitives.

Risks and test signals: risks include poisoning memory that must remain RCU-accessible, losing allocation/free stack metadata, tag reuse hiding UAFs, sampling false negatives, and mishandling KFENCE or highmem. Tests should cover slab, kmalloc, large kmalloc, krealloc, page alloc, mempool, vmalloc, invalid-free, double-free, RCU slab, and stack-trace reporting.
