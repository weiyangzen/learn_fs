# sources/distributed-fs/ceph-client/mm/nommu.c

## Purpose

`nommu.c` supplies the memory-management implementation used on Linux targets without an MMU. Since there is no page-table-backed virtual address space, it replaces VM facilities with directly allocated memory, tracks process mappings as real address ranges, and rejects or stubs operations that require arbitrary virtual remapping. It is a compatibility layer for syscalls and MM APIs expected by filesystems, drivers, BPF/proc accessors, and generic kernel code while enforcing NOMMU constraints.

For the Ceph-client source tree, this is not Ceph-specific code, but it defines the kernel behavior a Ceph-enabled build inherits on NOMMU systems: mmap semantics are restricted, vmalloc is physically/logically contiguous allocation, page-fault helpers are unavailable, and remote process memory reads/writes operate directly over VMA address ranges.

## Important APIs, Types, And Functions

- Global state: `highest_memmap_pfn`, `heap_stack_gap`, `mmap_pages_allocated`, `nommu_region_tree`, `nommu_region_sem`, and the `vm_region_jar` slab cache hold NOMMU memory-region accounting.
- Exported allocation shims: `vfree()`, `__vmalloc_noprof()`, `vmalloc_noprof()`, `vzalloc_noprof()`, `vmalloc_user_noprof()`, `vmalloc_node_noprof()`, `vmalloc_32_noprof()`, `vmalloc_to_page()`, and `vmalloc_to_pfn()` map vmalloc-style callers onto `kmalloc`, `krealloc`, or direct address translation.
- Unsupported remapping APIs: `vmap()`, `vunmap()`, `vm_map_ram()`, `vm_unmap_ram()`, `free_vm_area()`, `filemap_fault()`, and `filemap_map_pages()` deliberately `BUG()` or fail because NOMMU cannot synthesize arbitrary virtual mappings or normal page faults.
- User mapping syscalls: `brk`, `mmap_pgoff`, optional `old_mmap`, `munmap`, and `mremap` are implemented with NOMMU-specific validation and region accounting.
- Mapping helpers: `validate_mmap_request()`, `determine_vm_flags()`, `do_mmap_shared_file()`, `do_mmap_private()`, `do_mmap()`, `do_munmap()`, `split_vma()`, and `vmi_shrink_vma()` form the core mmap/munmap path.
- VMA/region helpers: `add_nommu_region()`, `delete_nommu_region()`, `put_nommu_region()`, `setup_vma_to_mm()`, `cleanup_vma_from_mm()`, `delete_vma_from_mm()`, `delete_vma()`, `find_vma()`, and `find_vma_intersection()`.
- Device/file mapping adapters: `remap_pfn_range()`, `vm_iomap_memory()`, `remap_vmalloc_range()`, and `nommu_shrink_inode_mappings()`.
- Remote memory helpers: `access_remote_vm()`, `access_process_vm()`, and, under `CONFIG_BPF_SYSCALL`, `copy_remote_vm_str()`.

## Control Flow

Initialization starts in `mmap_init()`, which initializes `vm_committed_as`, creates the `vm_region` slab cache, registers `vm.nr_trim_pages`, and initializes VMA state. `init_user_reserve()` and `init_admin_reserve()` later seed overcommit reserve sysctls from free memory.

The vmalloc path is intentionally simple. Calls such as `vmalloc()` and `vzalloc()` eventually use `__vmalloc_noprof()`, which allocates with `kmalloc_noprof()` plus `__GFP_COMP` and strips `__GFP_HIGHMEM`. `vmalloc_user_noprof()` additionally searches the caller's mm for the allocated VMA and sets `VM_USERMAP`, allowing `remap_vmalloc_range()` to expose that region later. APIs requiring a virtual remap table are either no-ops, return `-EINVAL`, or crash via `BUG()` to catch impossible use on NOMMU.

`do_mmap()` first delegates policy checks to `validate_mmap_request()`. That function rejects `MAP_FIXED`, invalid `MAP_TYPE`, zero length, overflow, missing file mmap support, incompatible file permissions, noexec violations, and unsupported shared/private combinations. It computes NOMMU capabilities from file operations, file type, read/write mode, and direct-map support. `determine_vm_flags()` converts the request and capability set into `vm_flags`, including `VM_SHARED`, `VM_MAYOVERLAY`, and direct-map flags.

After validation, `do_mmap()` allocates one `vm_region` and one `vm_area_struct`, records file references, and takes `nommu_region_sem`. If a shared mapping is possible, it searches `nommu_region_tree` for an already compatible mapping of the same inode and pgoff range. Exact or superset matches share the existing `vm_region` and bump `vm_usage`; mismatched sharing is rejected unless the backing file handles direct mapping itself. If no existing region is reusable, direct maps ask the file's `get_unmapped_area()` for a real address; otherwise `do_mmap_private()` allocates pages with `alloc_pages_exact()`, optionally reads file contents into the copy, records `VM_MAPPED_COPY`, and updates `mmap_pages_allocated`.

Successful mappings are inserted into the global `nommu_region_tree` and the process `mm->mm_mt` maple tree. File-backed VMAs are also inserted into the inode mapping interval tree under `i_mmap_lock_write()`. Executable regions are flushed once with `flush_icache_user_range()`.

`do_munmap()` is stricter than MMU Linux. File-backed mappings must be unmapped as whole VMAs. Anonymous mappings may be unmapped wholly, shrunk from one end, or split once then shrunk; arbitrary middle removal is only handled through `split_vma()` plus `vmi_shrink_vma()`. Shrinking adjusts both the VMA and its private `vm_region`, removes and reinserts region rb-tree entries, and releases the abandoned pages through `free_page_series()`.

`exit_mmap()` walks all VMAs, unlinks file interval-tree state, drops file refs and region refs, destroys the maple tree, and resets `total_vm`. `do_mremap()` can only resize an exact anonymous/private mapping in place within its originally allocated region; moving and fixed remap are rejected.

`nommu_shrink_inode_mappings()` protects truncate. It rejects truncation if any shared VMA overlaps the removed range, then trims shared region tops that extend past the new file size.

## State And Persistence Behavior

State is in-memory kernel state only. Persistent backing file contents are copied into private mappings with `kernel_read()` during mmap and are not automatically written back by this file. Region lifetime is reference-counted by `vm_region->vm_usage`; when usage hits zero, file refs are dropped, copied page ranges are released, and the `vm_region` object returns to the slab.

The global rb-tree serializes shareable real-address regions across processes through `nommu_region_sem`. Per-process VMAs live in `mm->mm_mt`; file mappings also persist in `mapping->i_mmap` interval trees for truncate coordination. `mmap_pages_allocated` accounts exact page-series allocations for copied mappings.

## Dependencies And Integration Points

This file integrates with the syscall layer, Linux VMA maple-tree iteration, inode address-space interval trees, LSM `security_mmap_addr()`, audit, sysctl, file operation hooks (`mmap`, `mmap_capabilities`, `get_unmapped_area`), memblock/page allocation via normal allocators, and architecture hooks for cache flushing and I/O remapping.

Ceph and other filesystems interact indirectly through generic mmap, writeback, truncate, and remote-access paths. Any Ceph file mapping on a NOMMU target must satisfy these direct/copy mapping constraints; normal page-fault-based cache population is unavailable because `filemap_fault()` is a `BUG()` stub here.

## Risks And Edge Cases

- `MAP_FIXED`, most VMA movement, arbitrary virtual remapping, and page-fault-driven file mappings are unavailable; callers assuming MMU behavior can fail or hit `BUG()`.
- Shared mapping correctness depends on file capability reporting and overlap checks. Incorrect `mmap_capabilities()` or `get_unmapped_area()` behavior in a driver/filesystem can expose invalid direct mappings.
- Private file mappings read file contents once; subsequent file changes do not behave like normal page-cache-backed private mmap.
- Unmap restrictions are stricter for file-backed mappings. Partial unmaps that are common on MMU systems may return `-EINVAL`.
- Region rb-tree invariants are critical; debug validation catches overlap/order bugs only under `CONFIG_DEBUG_NOMMU_REGIONS`.
- `__access_remote_vm()` copies directly from target virtual addresses after VMA permission checks; VMA bounds and overflow handling are essential because there is no GUP/page-table walk.

## Test Signals

- NOMMU boot smoke tests should verify `mmap_init()` sysctl registration and absence of region-tree validation failures.
- Syscall tests should cover anonymous/private mmap, shared direct mmap through a capable chardev or memory filesystem, invalid `MAP_FIXED`, permission failures, partial anonymous munmap, rejected partial file munmap, and in-place `mremap`.
- Truncate tests should exercise `nommu_shrink_inode_mappings()` with shared and private file mappings.
- BPF/proc-style tests should cover `access_process_vm()` and `copy_remote_vm_str()` permission and boundary behavior.
- Filesystem tests for Ceph on NOMMU, if supported, should avoid assuming page-fault mmap behavior and should validate expected `mmap` failure modes.
