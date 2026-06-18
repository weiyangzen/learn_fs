# sources/distributed-fs/ceph-client/tools/cgroup/memcg_slabinfo.py

Purpose: drgn script that prints slab cache statistics for a memory cgroup and can emulate cgroup v1 `memory.kmem.slabinfo` behavior.

Important APIs, types, and functions: `find_memcg_ids()` maps cgroup ids to `struct mem_cgroup`. `detect_kernel_config()` detects SLUB/SLAB and shared slab page support. `slub_get_slabinfo()` aggregates node slab counters and partial free objects. `for_each_slab()` scans pages for slab folios. `cache_show()` prints slabinfo-format rows.

Control flow: Parses target cgroup path, resolves its inode to a memcg, detects allocator config, prints header, then either scans all slab pages and object cgroup vectors for shared slab pages or iterates the memcg's `kmem_caches` list for older per-memcg caches.

State and persistence: Read-only against live kernel memory. Uses global `MEMCGS` mapping.

Dependencies and integration points: Requires drgn, kernel symbols/debug info, cgroup memory controller, SLUB support, and kernel layouts for slab, obj_cgroup, mem_cgroup, and kmem_cache.

Risks: SLAB allocator is detected but not supported. Whole-memory page scanning can be expensive. Structure layout and page type constants are kernel-version sensitive. Faults while scanning pages are ignored only in `for_each_slab()`.

Test signals: Run against root and non-root cgroups on shared-slab and older kernels, verify output resembles slabinfo, and confirm graceful error on unsupported allocator or unknown cgroup.
