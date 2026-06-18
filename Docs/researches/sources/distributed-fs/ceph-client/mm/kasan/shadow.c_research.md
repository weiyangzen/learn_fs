# sources/distributed-fs/ceph-client/mm/kasan/shadow.c

## Purpose

`shadow.c` manages KASAN shadow memory for generic and software tag modes. It provides explicit read/write range checks, instrumented memory intrinsic wrappers, poison/unpoison primitives, memory-hotplug shadow handling, vmalloc/module shadow population, and vmalloc poisoning on allocation/free.

## Important APIs, Types, and Functions

Public entry points include `__kasan_check_read()`, `__kasan_check_write()`, `__asan_memset()`, `__asan_memmove()`, `__asan_memcpy()`, optional `__hwasan_mem*` aliases, `kasan_poison()`, `kasan_poison_last_granule()`, `kasan_unpoison()`, `__kasan_populate_vmalloc()`, `__kasan_release_vmalloc()`, `__kasan_unpoison_vmalloc()`, `__kasan_poison_vmalloc()`, `kasan_alloc_module_shadow()`, and `kasan_free_module_shadow()`. Internal vmalloc helpers include `kasan_populate_vmalloc_pte()`, `__kasan_populate_vmalloc_do()`, and `kasan_depopulate_vmalloc_pte()`.

## Control Flow

Range-check APIs call `kasan_check_range()` with read/write intent. Instrumented memory wrappers validate source and destination before forwarding to `__mem*`. Poisoning strips pointer tags, validates granule alignment, converts memory addresses to shadow addresses, and writes poison/tag bytes. Generic mode additionally records partial-granule accessibility in the last shadow byte. Vmalloc population maps shadow pages for vmalloc/module regions, initializes them to `KASAN_VMALLOC_INVALID`, flushes caches, and relies on vmalloc publication barriers to prevent other CPUs from seeing stale poison after allocation. Release logic frees only shadow pages fully covered by a free vmalloc region, with careful alignment to avoid freeing shadow shared by neighboring allocations.

## State and Persistence Behavior

The persistent runtime state is shadow memory mappings and their poison/tag bytes. Memory-hotplug and vmalloc code allocate or release backing pages for portions of the shadow address space. Module shadow is marked via `VM_KASAN` on the owning `vm_struct` so it can be released when modules unload.

## Dependencies and Integration Points

The file integrates with compiler instrumentation, vmalloc, module allocation, memory hotplug notifiers, memblock/vmalloc page table manipulation, kmemleak, cache/TLB flushing, and architecture address translation helpers. It is disabled or simplified in some UML paths where all shadow is pre-mapped.

## Risks and Edge Cases

Risks are mostly mapping and ordering bugs: freeing a shadow page still shared by another vmalloc allocation, publishing vmalloc memory before shadow is unpoisoned, failing page-table allocations under constrained GFP masks, and recursive checking through instrumented memory functions. The code uses uninstrumented `__mem*` and page-table locks/barriers to reduce those risks.

## Test Signals

Signals include KASAN reports for vmalloc/module OOB, memory hotplug online/offline with KASAN enabled, module load/unload with shadow allocation, compiler intrinsic tests, partial-granule generic poisoning checks, and stress tests for concurrent vmalloc allocate/free.
