# sources/distributed-fs/ceph-client/mm/secretmem.c

## Purpose
`secretmem.c` implements the `memfd_secret(2)` backing filesystem and file operations. Secret memory creates anonymous file descriptors whose mappings allocate pages removed from the kernel direct map, locked into memory, excluded from core dumps, unevictable, non-migratable, and zeroed/restored to the direct map when freed. It is generic security-sensitive MM infrastructure, not Ceph-specific.

## Important APIs, Types, and Functions
The syscall entry is `SYSCALL_DEFINE1(memfd_secret, unsigned int, flags)`. Public helper `secretmem_active()` reports whether any secretmem users exist, and `vma_is_secretmem()` identifies VMAs using `secretmem_vm_ops`. Fault handling is in `secretmem_fault()`. File and mapping hooks include `secretmem_release()`, `secretmem_mmap_prepare()`, `secretmem_fops`, `secretmem_aops`, `secretmem_migrate_folio()`, `secretmem_free_folio()`, `secretmem_setattr()`, and `secretmem_iops`.

Filesystem setup is handled by `secretmem_init_fs_context()`, `secretmem_fs`, and `secretmem_init()`, which mounts a pseudo filesystem into `secretmem_mnt`. `secretmem_file_create()` creates the secure anonymous inode and pseudo file. Important globals are `secretmem_enable`, a read-only module parameter, `secretmem_users`, and `secretmem_mnt`.

## Control Flow
At init, `secretmem_init()` checks the enable flag and `can_set_direct_map()`, then mounts the pseudo filesystem. The syscall rejects unsupported systems with `-ENOSYS`, rejects unknown flags, checks the user counter, and returns an fd from `secretmem_file_create()` with optional `O_CLOEXEC`. File creation allocates a secure anonymous inode, creates a pseudo file with secretmem fops, sets high-user GFP mask and unevictable mapping state, installs inode and address-space ops, marks the inode as regular with size zero, and increments `secretmem_users`.

Mapping requires shared semantics. `secretmem_mmap_prepare()` rejects mappings that are not shared/may-share, sets `VM_LOCKED` and `VM_DONTDUMP`, checks `mlock_future_ok()`, and installs the fault ops. On a page fault, `secretmem_fault()` rejects offsets beyond file size, takes the mapping invalidate lock shared, looks for an existing locked folio, or allocates a zeroed order-0 folio. New folios are removed from the direct map with `set_direct_map_invalid_noflush()`, marked uptodate, inserted into the filemap, and followed by a kernel TLB flush for the folio address. The fault returns the locked file page.

When a secretmem folio is freed, `secretmem_free_folio()` restores the default direct-map permissions and zeroes the folio contents. Migration is refused with `-EBUSY`. Truncation via setattr is allowed only while the inode size is zero; resizing a non-empty secretmem file returns `-EINVAL` under the invalidate lock. File release decrements the active user count.

## State and Persistence Behavior
State is in memory only. Secretmem files are pseudo files with page-cache folios, but the folios are unevictable and not backed by disk. The important persistence contract is negative: data should not remain accessible through the kernel direct map, should not be migrated or swapped, should not be dumped, and should be zeroed before being returned to normal memory. The user count lets other code observe whether secretmem is active.

## Dependencies and Integration Points
Dependencies include memfd/syscall infrastructure, pseudo filesystems, secure anonymous inode creation, page cache and filemap locks, `set_direct_map_invalid_noflush()`/`set_direct_map_default_noflush()`, TLB flushing, mlock accounting, unevictable mapping state, and simple inode setattr. It integrates with VMA setup through `.mmap_prepare`, with fault handling through `vm_operations_struct`, and with generic reclaim/migration through address-space operations that make secretmem dirty handling a no-op and migration impossible.

## Risks and Edge Cases
Security depends on direct-map manipulation succeeding and being paired on free. Failure after invalidating the direct map but before inserting into the filemap must restore default mapping. Existing folios found by `filemap_lock_folio()` are reused; racing insertion handles `-EEXIST` by retrying. The mapping must be shared and mlock limits must be enforced, otherwise users could create secret memory outside the intended accounting model. Size handling is restrictive: faults beyond `i_size` fail, and resizing after size is nonzero is rejected. Architectures without direct-map control disable the syscall.

## Test Signals
Tests should cover syscall disabled by module parameter or missing direct-map support, invalid flags, `O_CLOEXEC`, mmap mode rejection for private mappings, mlock-limit failure, ftruncate/setattr behavior before and after sizing, first fault allocation and repeated fault reuse, direct-map access prevention where testable, folio zeroing on free, migration refusal, core-dump exclusion, unevictable accounting, user count changes through open/release, and stress with concurrent faults and truncation/invalidation.
