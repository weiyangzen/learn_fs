# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Chown.inc

## Purpose

`Chown.inc` implements internal owner/group changes for EOS directories and files. XRootD OFS has no public chown entry here, so `_chown` is used by EOS command paths and supports no-dereference behavior, ACL/admin permission checks, quota adjustment for files, metadata persistence, audit, and FUSE refresh.

## Important APIs, Types, and Functions

- `XrdMgmOfs::_chown(path, uid, gid, error, vid, ininfo, nodereference)` is the only function.
- Directory path: fetch container, list effective attrs, construct ACL, enforce root/admin/admin-group/`CanChown()` plus mutability, update `CUid`/`CGid`.
- File path: fetch parent, quota node, parent attrs, ACL, then file metadata, subtract/add quota accounting around owner/group changes.
- `0xffffffff` uid or gid means "do not change this field".
- Audit helpers build before/after `CHOWN` stats.

## Control Flow

The function takes a namespace write lock and first attempts to chown the target as a container. It computes effective attributes, removes `user.acl` from permission evaluation if the requested uid differs from the caller uid, and checks ACL/admin rules. On success it updates owner/group, ctime, store, releases lock, sends FUSE refresh, and audits.

If no container is found, it treats the target as a file. It resolves and optionally de-references the parent, gets quota node, evaluates parent ACL, fetches the file, removes the file from quota accounting, applies uid/gid changes according to privilege rules, re-adds the file to quota, updates ctime/store, releases lock, refreshes FUSE, and audits.

## State and Persistence Behavior

The operation persists owner/group and ctime changes to container or file stores. File chown also mutates quota accounting by removing and re-adding the file around metadata changes. It emits audit records and FUSE refreshes after successful mutations.

## Dependencies and Integration Points

Dependencies include `Acl`, `_attr_ls`, `listAttributes`, namespace locks, quota nodes, metadata stores, audit helpers, FUSE xcast, and identity roles (`ADM_UID`, `ADM_GID`, `sudoer`). It is integrated through FSctl command dispatch and internal EOS management paths.

## Risks and Edge Cases

- Directory and file permission rules differ: file ownership changes require root/admin/sudo/ACL, but group changes are more restricted.
- Quota accounting must be balanced even if future edits introduce exceptions between remove and add.
- `nodereference` changes lookup behavior for symlink-like paths; tests need both modes.
- Removing `user.acl` from permission evaluation when changing to another uid prevents self-granted ACL escalation.
- The function ends timing with `"Chmod"` rather than `"Chown"`, a diagnostic inconsistency.

## Test Signals

Tests should cover directory and file chown, root/admin/sudo/ACL permission cases, immutable denial, user ACL self-escalation prevention, `0xffffffff` skip semantics, gid change privilege limits, quota accounting updates, no-dereference lookup, audit records, and FUSE refresh identifiers.
