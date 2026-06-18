# sources/distributed-fs/ceph-client/fs/xfs/xfs_extfree_item.h

## Purpose
`xfs_extfree_item.h` declares the in-kernel EFI/EFD log item structures and APIs for deferred extent freeing.

## Important APIs, types, and functions
It defines `XFS_EFI_MAX_FAST_EXTENTS`, `struct xfs_efi_log_item`, `xfs_efi_log_item_sizeof`, `struct xfs_efd_log_item`, `xfs_efd_log_item_sizeof`, `XFS_EFD_MAX_FAST_EXTENTS`, cache externs, `xfs_extent_free_defer_add`, `xfs_efi_log_space`, and `xfs_efd_log_space`.

## Control flow
Allocation code creates `struct xfs_extent_free_item` objects and passes them to `xfs_extent_free_defer_add`; transaction and recovery code use the log item size helpers to allocate variable-length EFI/EFD objects and reserve log space.

## State and persistence
The structures contain the logged EFI/EFD format payloads, in-core log items, EFI reference state, and EFD backpointer to the EFI. Their embedded format records are what reach the journal.

## Dependencies and integration points
It depends on XFS log format definitions, transaction/defer infrastructure, and slab caches initialized elsewhere in XFS.

## Risks and test signals
Risks include variable-size allocation mistakes, fast-cache thresholds diverging from implementation, and misuse of EFI reference ownership documented in the header. Test signals include log-space reservation checks, large batch frees, recovery replay, and transaction cancellation paths.
