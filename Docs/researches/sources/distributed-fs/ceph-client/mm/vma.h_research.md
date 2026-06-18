# sources/distributed-fs/ceph-client/mm/vma.h

## Purpose

`vma.h` declares and inlines the core VMA manipulation API implemented by `vma.c`, `vma_init.c`, and `vma_exec.c`. It defines operation-state structures for merge, munmap, preparation, unlink batching, and unmap descriptors, plus helper macros and iterator wrappers used across MM code.

## Important APIs, Types, and Functions

- `struct vma_prepare` describes the VMAs, file mapping, anon_vma, insert/remove targets, and uprobe behavior for a pending VMA mutation.
- `struct unlink_vma_file_batch` batches up to eight file-backed VMAs sharing a mapping for unlinking from `i_mmap`.
- `struct vma_munmap_struct` tracks a munmap operation: iterator, first/prev/next VMAs, userfaultfd list, aligned range, PTE-clearing range, detached counts, accounting totals, and unlock behavior.
- `enum vma_merge_state` and `struct vma_merge_struct` encode a merge attempt and its mutable internal flags.
- `struct unmap_desc`, `unmap_all_init()`, `unmap_pgtable_init()`, and `UNMAP_STATE` parameterize page-table unmap/free operations.
- `VMG_STATE` and `VMG_VMA_STATE` initialize merge state for new ranges and existing VMA modifications.
- Public prototypes cover VMA expand/shrink/modify/merge, munmap, unlink batching, copy, anon-vma lookup, dirty tracking, all-lock collection, mmap/brk/gap search, stack expansion, insertion, allocation/dup/free, and exec stack helpers.
- Inline helpers wrap maple-tree VMA iterator operations and classify mappings as exec/stack/data.
- `map_deny_write_exec()` implements MDWE policy checks for writable-executable or newly executable mappings.

## Control Flow

The header itself does not execute high-level operations, but its initializer macros determine how callers seed merge and munmap state. `VMG_VMA_STATE` snapshots a VMA's flags, pgoff, file, anon_vma, policy, UFFD context, and anon name so modification helpers can compare against neighbors. Iterator helpers normalize maple tree range setup, preallocation, store, clear, load, previous/next range movement, and gap finding.

Mapping classifiers feed accounting code: executable mappings are executable, non-writable, non-stack; stack mappings include `VM_STACK` and shadow stacks; data mappings are private writable non-stack ranges. `map_deny_write_exec()` first exits unless current mm has MDWE, then denies new executable mappings that are writable or transitions from non-executable to executable.

## State and Persistence

The structs in this header are transient operation state, but they reference persistent mm/VMA/file/anon-vma/mapping state. Inline store helpers mark VMAs attached and update maple-tree ranges. MDWE checks read `current->mm` flags but do not mutate state.

## Dependencies and Integration Points

The API is tightly coupled to `struct vm_area_struct`, `struct mm_struct`, `vma_iterator`, maple-tree `ma_state`, mempolicy, anon-vma names, userfaultfd contexts, `struct vm_area_desc`, page-table constants, stack direction configuration, `CONFIG_MMU`, `CONFIG_DEBUG_VM_MAPLE_TREE`, `CONFIG_STACK_GROWSUP`, and `CONFIG_64BIT` sealed VMA support.

## Risks

- Callers must respect comments about iterator position, mmap lock mode, and whether actual flag/name/policy mutations are applied by the caller after split/merge preparation.
- `struct vma_merge_struct` is intentionally mutated during merge; callers cannot rely on fields retaining input values after helper calls.
- Iterator helpers store ranges as `[start, end - 1]`; off-by-one errors in callers can corrupt maple-tree coverage.
- `vma_set_file()` compatibility helper in this header assumes partially established VMA state and should not be treated as a general VMA mutation API.
- MDWE checks rely on old/new VMA flag sets being accurate, especially in mprotect-like flows.

## Test Signals

Signals include compile coverage across MMU/NOMMU, stack grows up/down, 32/64-bit, debug maple tree, and MDWE configs; API consumers that exercise split/merge/munmap/mmap paths; maple-tree validation; and tests verifying mapping accounting classifiers.
