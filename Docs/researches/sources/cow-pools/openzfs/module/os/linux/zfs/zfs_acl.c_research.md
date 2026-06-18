# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_acl.c

## Purpose

Core Linux ZFS ACL implementation. It handles ZFS/NFSv4 ACL storage formats, old-to-new ACL conversion, FUID mapping, ACL inheritance and chmod behavior, POSIX-mode derivation, ACL get/set operations, and permission checks for access, delete, and rename.

## ACL Formats And Operations

The file defines two `acl_ops_t` implementations:

- `zfs_acl_v0_ops` for old fixed `zfs_oldace_t` entries.
- `zfs_acl_fuid_ops` for newer FUID-aware ACEs, including compact owner/group/everyone ACEs and larger object ACEs.

The ops table abstracts get/set of type, flags, mask, who, entry size, abstract size, mask offset, and optional object ACE data. This allows generic ACL walking and transformation code to work over both on-disk formats.

`zfs_external_acl()`, `zfs_acl_znode_info()`, and `zfs_znode_acl_version()` handle legacy external ACL objects and races with SA upgrades. `zfs_acl_version()` maps ZPL version to initial versus FUID ACL format.

## Allocation, Walking, And Conversion

- `zfs_acl_alloc()`, `zfs_acl_node_alloc()`, `zfs_acl_node_free()`, `zfs_acl_release_nodes()`, and `zfs_acl_free()` manage ACL containers and list nodes.
- `zfs_acl_valid_ace_type()` and `zfs_ace_valid()` validate ACE type, owner/group/everyone flags, object ACE eligibility, and inheritance flag combinations while updating ACL hints.
- `zfs_acl_next_ace()` walks ACL nodes safely, validating per-entry bounds using the active ops table.
- `zfs_copy_ace_2_fuid()` converts user ACE buffers to ZFS FUID ACL entries and creates FUIDs for named users/groups.
- `zfs_copy_fuid_2_ace()` maps ZFS FUID ACLs back to exported `ace_t`/`ace_object_t` buffers.
- `zfs_copy_ace_2_oldace()` converts user ACE buffers to legacy format.
- `zfs_acl_xform()` transforms an old ACL into FUID format, allocating a new node, converting entries, replacing old nodes, and updating version/count/byte totals.

## Mode And Trivial ACL Logic

`zfs_unix_to_v4()` and `zfs_v4_to_unix()` translate between Unix mode bits and NFSv4-style ACE masks. `zfs_mode_compute()` derives inode mode bits from ACL entries and updates `ZFS_NO_EXECS_DENIED` depending on whether execute was denied or absent.

`acl_trivial_access_masks()` builds canonical owner/group/everyone masks for a Unix mode. `ace_trivial_common()` detects ACLs that are representable as trivial mode-derived ACLs by rejecting named users/groups, inheritance flags, read-attribute denies, delete permission, malformed delete-child grants, and non-owner administrative allows.

## ACL Storage Updates

`zfs_acl_node_read()` reads a znode ACL under `z_acl_lock`, using cached ACLs when possible unless modification is requested. It reads SA-stored ACLs directly or legacy ACL data from embedded `z_ace_data` / external DMU objects. Checksum errors are translated to `EIO`.

`zfs_aclset_common()` is the shared writer used by chmod, creation, and explicit setacl paths. It recomputes mode/pflags, clears cached ACLs, upgrades old ACLs when needed, writes SA ACL attributes or legacy embedded/external ACL objects, updates ACL-wide pflags and trivial hints, updates ctime, and commits via `sa_bulk_update()`.

`zfs_acl_chmod()` rewrites ACLs to match a new mode while respecting `aclmode`: it may split inheritable owner/group/everyone ACEs into inherit-only entries, trim allows to group permissions, preserve audit/object/inherit-only entries, add canonical mode ACEs, and rebuild count/byte totals.

`zfs_acl_chmod_setattr()` obtains or creates the ACL for chmod according to `z_acl_mode`, applies `zfs_acl_chmod()`, and returns the modified ACL to the caller.

## Inheritance And Creation

`zfs_ace_can_use()` decides whether an ACE should inherit to the new object. `zfs_acl_inherit()` builds a child ACL according to `aclinherit`, object type, requested mode, and parent ACE flags. It handles `discard`, symlink exclusion, `noallow`, `passthrough`, `passthrough-x`, `restricted`, no-propagate, inherit-only conversion, and hint updates.

`zfs_acl_ids_create()` builds initial ACL IDs for new znodes. It converts explicit ACLs when provided, creates owner/group FUIDs, applies setgid inheritance and setgid clearing policy, inherits parent ACLs when appropriate, falls back to trivial ACLs, applies chmod-style mode ACLs when needed, computes resulting mode, and marks trivial ACLs. `zfs_acl_ids_free()` releases ACL/FUID data, and `zfs_acl_ids_overquota()` checks user/group/project quota before create.

## Get/Set ACL Interfaces

- `zfs_getacl()` checks `ACE_READ_ACL`, reads/caches the ACL, counts or filters object ACEs depending on `VSA_ACE_ALLTYPES`, allocates the output ACE buffer, converts entries to user-visible layout, and returns ACL flags.
- `zfs_vsec_2_aclp()` validates user ACL count, allocates a ZFS ACL, converts old/FUID entries, installs ACL-wide flags, and returns the internal ACL.
- `zfs_setacl()` checks immutable state and `ACE_WRITE_ACL`, converts the user ACL, preserves existing wide flags when not explicitly provided, creates a DMU transaction with holds for SA/FUID/external ACL changes, retries on `ERESTART`, writes via `zfs_aclset_common()`, caches the new ACL, syncs FUIDs, logs the ACL change, and commits.

## Access Checks

`zfs_zaccess_dataset_check()` rejects writes on readonly datasets, writes to immutable files, delete/unlink on nounlink files, and read/execute on quarantined files.

`zfs_zaccess_aces_check()` is the main non-trivial ACL evaluator. It walks ACEs in order, skips inherit-only directory ACEs, matches owner/group/everyone/named-user entries against credentials and idmaps, removes covered bits from the working mask, accumulates deny bits, supports "any access" short-circuit mode, and returns `EACCES`, `0`, or `-1` for unresolved requested bits.

`zfs_zaccess_trivial()` delegates mode-like checks to Linux `generic_permission()` for trivial ACLs while rejecting unmappable special permissions such as write-owner/write-ACL/delete.

`zfs_zaccess_common()` combines empty/replay short-circuits, dataset checks, skip-ACL handling, DOS readonly handling, trivial ACL path, and ACE evaluator path.

`zfs_zaccess()` is the public fine-grained permission check. It remaps xattr directory access to base-file named-attribute permissions, maps requested ACE bits to Unix mode bits for privilege checks, invokes ACL checks, handles append fallback, and consults Linux/SPL secpolicy helpers for owner, DAC, chown, remove, and residual special bits.

`zfs_fastaccesschk_execute()` provides a fast execute check for common non-xattr cases using mode bits and `ZFS_NO_EXECS_DENIED`, falling back to full `zfs_zaccess()`.

`zfs_has_access()`, `zfs_zaccess_rwx()`, and `zfs_zaccess_unix()` are wrappers for "any access" and Unix mode-derived requests.

## Delete And Rename

`zfs_zaccess_delete()` implements Windows-like delete semantics: target `ACE_DELETE` is checked first, target denies win, otherwise parent `ACE_DELETE_CHILD` or optionally `ACE_WRITE_DATA` can grant deletion, privilege fallbacks are attempted, and sticky-bit restrictions are enforced via `zfs_sticky_remove_access()`.

`zfs_zaccess_rename()` requires delete permission on the source, delete permission on an overwritten target if any, and add-file/add-subdirectory permission on the target directory. It also rejects quarantined source znodes.
