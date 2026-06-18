# sources/distributed-fs/ceph-client/rust/kernel/mm/virt.rs

Purpose: models access capabilities for `struct vm_area_struct`: read access (`VmaRef`), read access with `VM_MIXEDMAP` (`VmaMixedMap`), and mmap-initialization access (`VmaNew`). It also exports VMA flag constants.

Important APIs/types/functions: `VmaRef`, `VmaMixedMap`, `VmaNew`, `vm_flags_t`, `flags`, `VmaRef::mm`, `flags`, `start`, `end`, `zap_vma_range`, `as_mixedmap_vma`, `VmaMixedMap::vm_insert_page`, and VMA setup methods such as `set_mixedmap`, `set_io`, `set_dontexpand`, `set_dontcopy`, `set_dontdump`, `try_clear_mayread`, `try_clear_maywrite`, and `try_clear_mayexec`.

Control flow: raw constructors create references only under externally-proven lock or mmap-setup conditions. Read methods access fields under the read-lock invariant. `zap_vma_range` validates the requested range lies within the VMA and returns early on overflow/out-of-bounds. `VmaNew` mutates flags during mmap setup through `update_flags`; specific setters encode valid transitions and `try_clear_may*` rejects clearing a permission while it is actively enabled.

State and persistence behavior: state is the live VMA fields in kernel memory. `VmaNew` mutates the VMA before it is fully published. Page insertion and zap operations affect process mappings but do not persist outside kernel memory/page tables.

Dependencies and integration points: depends on `MmWithUser`, `Page`, MM bindings, kernel error codes, and miscdevice mmap callbacks. It integrates with the mmap path and page-table manipulation helpers.

Risks: capability separation is the safety boundary. Constructing `VmaRef` without the required lock or `VmaNew` outside mmap setup would allow races. `update_flags` must not create invalid flag combinations; currently `set_mixedmap` notes no `VM_PFNMAP` setter exists, limiting one invalid combination. `zap_vma_range` silently returns on invalid ranges pending a future warning.

Test signals: tests should verify flag setters/clearers, permission-clear failure when active, `set_mixedmap` enabling `vm_insert_page`, `as_mixedmap_vma` behavior, range validation in `zap_vma_range`, and integration from miscdevice `mmap`.
