## sources/distributed-fs/ceph-client/arch/s390/mm/maccess.c

Purpose: implements s390-specific safe kernel memory access helpers: writing protected kernel memory via real-address stores, copying from real memory through a temporary mapping, and translating `/dev/mem` lowcore/prefix pages into safe bounce buffers.

Important APIs, types, and functions: globals `__memcpy_real_area` and `memcpy_real_ptep` identify the reserved real-memory copy mapping. `__s390_kernel_write()` is the protected write primitive, using `s390_kernel_write_odd()` and a spinlock. `memcpy_real_iter()` and `memcpy_real()` copy from physical memory. `xlate_dev_mem_ptr()` and `unxlate_dev_mem_ptr()` implement `/dev/mem` physical pointer translation. `get_swapped_owner()` locates a CPU owning a swapped prefix page.

Control flow: kernel writes are serialized with `s390_kernel_write_lock` and update up to 8 bytes at a time with read-modify-write and `sturg`, bypassing DAT and page-table write protection. Real-memory copy maps one physical page at a time into `__memcpy_real_area`, invalidates the old PTE when the physical page changes, copies to an iterator, and stops on short copy. `/dev/mem` translation handles absolute lowcore and swapped prefix pages by allocating an atomic bounce page and copying the relevant lowcore view.

State and persistence: persistent state is the reserved mapping address/PTE and locks. The mapping PTE is updated under `memcpy_real_mutex`. Bounce pages allocated by `xlate_dev_mem_ptr()` must be freed by `unxlate_dev_mem_ptr()` when not a direct physical mapping.

Dependencies and integration points: depends on s390 lowcore, absolute lowcore helpers, PTE invalidation, no-fault/real-address assembly, CPU hotplug read locking, and generic iov_iter. It integrates with text patching, memory access debug helpers, and `/dev/mem`.

Risks: protected writes are byte-range read-modify-write operations and must stay serialized to avoid lost updates. `unxlate_dev_mem_ptr()` distinguishes bounce vs direct by comparing physical address and pointer; wrong translation would leak or free the wrong page. Real-memory mapping is single-slot global state, so missing the mutex would race.

Test signals: kernel text/static key patching paths using `s390_kernel_write()`, real-memory copy across page boundaries, short iterator behavior, `/dev/mem` reads of absolute lowcore and per-CPU prefix pages, and CPU hotplug races.
