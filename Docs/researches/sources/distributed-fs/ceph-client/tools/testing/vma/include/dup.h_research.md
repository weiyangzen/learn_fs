<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/dup.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/include/dup.h

## Purpose

`dup.h` duplicates a large subset of kernel mm/VMA declarations for userspace VMA testing. It provides the types, flags, and inline helpers needed to compile imported `mm/vma*.c` code outside the kernel.

## Important APIs, Types, and Functions

It defines partial kernel types such as `mm_struct`, `address_space`, `file_operations`, `file`, `anon_vma_chain`, `task_struct`, `kref`, and `anon_vma_name`. It duplicates VMA flag bit definitions, legacy `VM_*` masks, `vma_flags_t` helpers, `vm_flags_*` and `vma_*` accessors, VMA iterator helpers, mapping accounting helpers, `compat_set_desc_from_vma()`, `compat_vma_mmap()`, `vfs_mmap()`, `vma_set_page_prot()`, gap helpers, `mlock_future_ok()`, and file/mapping writable helpers.

## Control Flow and State

The header is mostly inline code. It maps VMA flags to bitmaps, converts between legacy and new VMA flag forms, mutates `vm_refcnt` for attach/detach, initializes VMAs, updates mm accounting counters, drives maple-tree iterators, and mediates file mmap hooks. State lives in caller-owned VMA, mm, file, and mapping structs.

## Dependencies and Integration Points

It depends on local stubs/custom headers, kernel maple-tree/rbtree/list/refcount/bitmap helpers, architecture config macros, and VMA harness globals such as `current`, `stack_guard_gap`, `sysctl_max_map_count`, `rlimit()`, and `vma_dummy_vm_ops`. It is the central compatibility layer for `tools/testing/vma`.

## Risks and Test Signals

Risks are high because duplicated kernel definitions can drift from real mm headers, especially flag bit positions, architecture-specific aliases, `VM_SHADOW_STACK`, pkeys, soft-dirty, and VMA iterator semantics. Passing VMA tests, sanitizer runs, and compile failures after upstream mm changes are the key signals that this duplicate layer remains aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/dup.h -->
