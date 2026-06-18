# sources/distributed-fs/ceph/src/client/Inode.cc

## Purpose
`Inode.cc` implements client inode cache behavior: debug output, path construction, open/cap ref accounting, cap validity and wanted masks, directory cache opening, permission bit checks, delegation coordination, dirty cap marking, fscrypt context inheritance, and effective encrypted-size helpers.

## Important APIs, Types, and Functions
The destructor asserts no leftover object-cache objects or delegations and unlinks cap/snap lists. `print()` and `dump()` expose inode/cache/cap/snap/open state. Path helpers are `make_long_path()`, `make_short_path()`, `make_path_string()`, and `make_nosnap_relative_path()`. Cap helpers include `get_cap_ref()`, `put_cap_ref()`, `caps_issued()`, `caps_issued_mask()`, `caps_used()`, `caps_file_wanted()`, `caps_wanted()`, `caps_dirty()`, and `get_best_perms()`. Delegation helpers include `recall_deleg()`, `break_deleg()`, `set_deleg()`, and `unset_deleg()`. Dirty state is handled by `mark_caps_dirty()` and `mark_caps_clean()`. Linux fscrypt helpers initialize/inherit contexts and manage effective size.

## Control Flow
Open paths call `get_open_ref()`, update metrics, and break conflicting delegations. Close paths call `put_open_ref()`. Capability checks first prefer valid snap/auth caps, then any valid cap, optionally implemented caps, touching cap LRU and updating hit/miss metrics. Dirty caps pin the inode and enqueue it in the auth session dirty list for later flush. Delegation setup verifies timeout enabled, no recalled delegations, open conflicts, and already-issued needed caps before creating or reinitializing a delegation.

## State and Persistence Behavior
This file manipulates volatile client cache state and dirty capability state that will later be flushed to MDS. Inode fields reflect authoritative metadata snapshots from MDS plus local dirty/flushing overlays. `cap_refs`, `open_by_mode`, `dirty_caps`, `flushing_caps`, `cap_snaps`, object cache set, and delegation list govern local lifetime and consistency. `fscrypt_file` may store the effective plaintext size when `Client::get_fscrypt_as()` is enabled.

## Dependencies and Integration Points
It depends on `Client`, `Dentry`, `Dir`, `Fh`, `MetaSession`, `ClientSnapRealm`, `Delegation`, MDS file lock/cap types, object cacher, and fscrypt on Linux. `Client` drives cap messages, request handling, flushing, and waiting; `MetaSession` owns dirty/flushing xlists.

## Risks and Edge Cases
Cap accounting is correctness-critical: issued versus implemented caps, auth-cap filtering during revocation, snap caps, and write-delegated buffer caps all affect cache validity. Dirty caps without auth cap are ignored with assertions on prior state, which matters during reconnect/rejection. `delegations_broken()` compares delegation type with `CEPH_FILE_MODE_RD`, which deserves scrutiny because delegation constants differ from file mode constants. Path building relies on first parent dentry and can fall back to ino paths for disconnected inodes. Fscrypt effective size uses raw little-endian storage in a byte vector.

## Test Signals
Cap hit/miss and validity tests across TTL/gen changes, open mode wanted caps including fscrypt write-read cap, dirty cap queueing/cleaning/flushing, delegation conflict and wait behavior, inode destruction leak assertions, path construction for linked/snapped/snapdir/disconnected inodes, async error propagation, and fscrypt effective size round trips.
