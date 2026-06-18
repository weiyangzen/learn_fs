# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_impl.h

## Scope

Private libzfs implementation header shared by the library source files.

## API Surface

Defines internal `libzfs_handle`, `zfs_handle`, and `zpool_handle` layouts; error buffer size; mount namespace property flags; `ZFS_IS_VOLUME`; URI handler structs; changelist flags; and `differ_info_t`.

It declares internal allocation/error helpers, zcmd nvlist helpers, dataset-handle constructors, property parser/list expansion helpers, changelist APIs, namespace/mount helpers, zpool open/name validation helpers, mnttab-related integration points, module loading, disk relabeling, and `find_shares_object()`.

## State And Dependencies

The header ties together libzfs public headers, libzfs_core, nvpair, DMU/ZFS ioctl structures, mutexes, regex, AVL-backed namespace/mnttab state, and libshare integration.

## Risks And Invariants

This is private ABI: struct fields are directly shared across libzfs translation units and must stay consistent with all users. The cached zpool handle list, mnttab AVL, namespace AVL, and zcmd nvlist helpers form library-global state behind a single `libzfs_handle_t`.
