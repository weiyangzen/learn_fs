# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_znode_os.c

## Read Coverage
Read completely: 1,982 lines, 53,107 bytes.

## Purpose
`zfs_znode_os.c` implements Linux-specific znode/inode lifecycle and ZPL object construction for OpenZFS. It creates, finds, refreshes, updates, deletes, and frees znodes while binding Linux inode state to ZFS DMU objects and SA metadata. It also implements timestamp setup, block-size growth, truncate/free-range helpers, and initial ZPL filesystem creation.

## Major Responsibilities
- Initializes and destroys znode and per-object hold caches.
- Constructs/destructs znode locks, range locks, ACL/xattr cache state, and embedded Linux inode state.
- Implements external per-object znode hold locks used before a znode or SA handle may exist.
- Allocates Linux inodes and initializes ZFS znodes from DMU buffers and SA handles.
- Sets Linux inode operation tables and special inode/device state based on ZFS mode.
- Creates new DMU objects and SA metadata through `zfs_mknode()`.
- Resolves object numbers to live znodes with `zfs_zget()`.
- Rebinds active znodes after rollback/receive with `zfs_rezget()`.
- Deletes DMU objects and external ACL objects and finalizes SA handles.
- Handles inactive znode cleanup and removal of unlinked files.
- Implements relatime checks, timestamp mutation setup, block-size growth, file extension, hole punching, truncation, and `zfs_freesp()`.
- Bootstraps a new ZPL objset in `zfs_create_fs()`.

## Key Data and Interfaces
- `znode_t` embeds or maps to Linux `struct inode` and stores cached ZFS state: object ID, size, block size, mode, pflags, project ID, sync count, SA handle, ACL cache, xattr cache, and range/name/parent locks.
- `znode_hold_t` serializes access to an object number before or while its znode/SA handle is being created, found, refreshed, or destroyed.
- `zfsvfs_t` provides object set, superblock, ZPL feature flags, SA attribute table, znode list, and hold-lock arrays.
- Uses `new_inode()`, `insert_inode_locked()`, `unlock_new_inode()`, `iput()`, `mark_inode_dirty()`, inode operation tables, and page-cache truncation APIs.
- Uses SA operations `sa_handle_get_from_db()`, `sa_replace_all_by_template()`, `sa_bulk_lookup()`, `sa_bulk_update()`, `sa_update()`, `sa_add_projid()`, and `sa_handle_destroy()`.
- Uses DMU/ZAP object creation and deletion APIs, including `zap_create_norm_dnsize()`, `zap_create_claim_norm_dnsize()`, `dmu_object_alloc_dnsize()`, `dmu_object_claim_dnsize()`, `dmu_object_free()`, `dmu_free_long_range()`, and `dmu_object_set_blocksize()`.

## Control Flow Highlights
- `zfs_rangelock_cb()` converts append locks into writer locks at EOF and expands locks to the whole file when a write may trigger block-size growth.
- `zfs_znode_hold_enter()` allocates outside the global hold lock, inserts/fetches a per-object hold in an AVL bucket, increments the refcount, then locks the per-object mutex. `zfs_znode_hold_exit()` reverses that and frees the hold when no waiters remain.
- `zfs_znode_alloc()` creates a Linux inode, initializes znode defaults, attaches an SA handle, bulk-loads metadata, validates generation/project attributes, sets inode mode/owner/timestamps/link count/flags, installs Linux inode ops, hashes linked inodes, and inserts the znode in `z_all_znodes`.
- `zfs_mknode()` creates or claims a DMU object, handles directory versus file object types, chooses old znode layout versus SA layout, writes all base attributes in layout-sensitive order, writes ACL data, allocates an in-core znode for non-root objects, and initializes project inheritance.
- `zfs_zget()` serializes by object number, validates bonus type, reuses an existing SA user znode when possible, retries if Linux eviction is in progress, rejects unlinked objects, or allocates a new znode from the DMU buffer.
- `zfs_rezget()` skips control-directory znodes, clears cached ACL/xattr state, rebuilds the SA handle, reloads metadata, validates generation, updates Linux inode state, and detaches SA state for zero-link received/unlinked files.
- `zfs_zinactive()` serializes against object lookup and either removes an unlinked object through `zfs_rmnode()` or destroys the SA handle while leaving read-only unlinked objects in the unlinked set.
- `zfs_freesp()` dispatches to extend, truncate, or free-range logic, then logs a truncate record and updates timestamps when requested.
- `zfs_create_fs()` creates the master node, ZPL properties, SA registration object, unlinked set, and root object using a minimal temporary `zfsvfs_t`, `super_block`, and root znode.

## Important Functions
- `zfs_znode_init()` and `zfs_znode_fini()` manage znode allocation caches.
- `zfs_znode_hold_enter()` and `zfs_znode_hold_exit()` provide per-object serialization outside the znode itself.
- `zfs_inode_alloc()`, `zfs_inode_free()`, and `zfs_inode_destroy()` bind Linux inode allocation/destruction to the znode cache and cleanup state.
- `zfs_inode_set_ops()` installs Linux inode/file/address-space operations for regular files, directories, symlinks, devices, FIFOs, and sockets.
- `zfs_znode_update_vfs()` refreshes Linux inode mode, block count, and size from ZFS state.
- `zfs_znode_alloc()` constructs an in-core znode/inode from an existing DMU object.
- `zfs_mknode()` constructs a new on-disk ZPL object and its in-core znode.
- `zfs_xvattr_set()` applies optional ZFS attributes and updates Linux immutable/append flags when needed.
- `zfs_zget()` resolves object IDs to held znodes.
- `zfs_rezget()` refreshes znodes after objset changes.
- `zfs_znode_delete()` and `zfs_zinactive()` implement object deletion and final inactive behavior.
- `zfs_tstamp_update_setup()`, `zfs_grow_blocksize()`, `zfs_extend()`, `zfs_free_range()`, `zfs_trunc()`, and `zfs_freesp()` manage file size, block ranges, timestamps, and page-cache truncation.
- `zfs_create_fs()` initializes a new ZPL filesystem.

## Invariants and Assumptions
- Object-number hold locks must protect znode/SA creation, lookup, refresh, and deletion when the znode itself may not yet be reliable.
- A znode with a live SA handle must not be freed or rediscovered concurrently outside the hold-lock protocol.
- Existing SA user data must point to a znode for the same object number; Linux `igrab()` decides whether it can be safely reused.
- Linked znodes are inserted into the Linux inode hash; unlinked znodes are deliberately not hashed to avoid rollback/unlinked-drain collisions.
- Old `DMU_OT_ZNODE` layout has strict SA attribute ordering to preserve historical `znode_phys_t` format.
- Root filesystem creation uses a temporary minimal mount/inode environment so `zfs_mknode()` can be reused.
- File block-size growth is allowed only under whole-file range locking and only while file layout constraints permit it.
- Truncate and free-range operations must keep DMU data, znode size, Linux inode size, and page cache coherent.

## Risks and Edge Cases
- `zfs_zget()` must handle Linux inode eviction races; incorrect handling can return a dying inode or block eviction completion.
- `zfs_rezget()` after rollback/receive must reject generation mismatches and stale object identities without corrupting active dentries.
- Project quota support depends on presence and layout of `SA_ZPL_PROJID`; old objects may need SA layout upgrades elsewhere.
- `zfs_mknode()` is format-sensitive across SA and old znode layouts, replay-claimed objects, ACL spill data, device files, tmpfiles, xattrs, and root creation.
- Inactive cleanup can leave unlinked files in the unlinked set on read-only filesystems or when debug suspension is enabled.
- Hole punching and truncation must coordinate full-page invalidation with partial-page zeroing under range locks.
- Temporary root creation in `zfs_create_fs()` manually initializes enough `zfsvfs_t`, hold locks, list state, and superblock state to satisfy shared constructors; missing one field can break bootstrap.
- Cache cleanup must release ACL and xattr caches on inode destruction and rollback refresh without racing users.

## Testing Signals
Useful coverage should include:
- Znode cache init/fini and inode allocation/free under reclaim.
- `zfs_zget()` for cached znodes, newly loaded znodes, invalid bonus types, unlinked objects, eviction-in-progress retry, and low-memory allocation retry through `zfs_mknode()`.
- `zfs_znode_alloc()` metadata loading for regular files, directories, symlinks, devices, FIFOs/sockets, xattr znodes, old znode layout, SA layout, and project-ID attributes.
- `zfs_mknode()` for root, normal files, directories, symlinks, devices, xattrs, tmpfiles, replay object claims, ACL spill objects, FUIDs, and project inheritance.
- `zfs_rezget()` after rollback/receive with changed size, changed timestamps, generation mismatch, zero links, missing project ID, and control-directory znodes.
- Inactive/delete behavior for linked files, unlinked open files, read-only unlinked files, files with external ACLs, and debug-suspended unlink progress.
- File extension, truncation to zero, truncation to nonzero, hole punching within one page, hole punching across pages, sparse flag clearing, page-cache truncation, and ZIL truncate logging via `zfs_freesp()`.
- New filesystem creation with different ZPL versions, SA enabled/disabled, case/normalization properties, root object creation, and unlinked set creation.

## Overall Assessment
This file is the Linux znode lifecycle and object-construction foundation for OpenZFS. It sits below the operation layer and determines whether Linux inodes, ZFS object numbers, SA handles, page-cache size, and on-disk metadata remain consistent across creation, lookup, deletion, rollback, receive, and truncation. Bugs here are likely to surface as stale inode reuse, incorrect metadata layout, leaked or prematurely freed objects, page-cache incoherency, or broken freshly created datasets.
