# sources/distributed-fs/ceph/src/mds/CInode.h

## Purpose
`CInode.h` declares the backing store and cached runtime interface for CephFS MDS inodes. `InodeStoreBase` holds serializable inode data without full cache behavior. `InodeStore` and `InodeStoreBare` support encoded standalone and embedded inode forms. `CInode` adds MDS cache-object behavior: lock objects, dirfrags, parent links, snaprealms, caps, freezing, persistence, validation, import/export, and policy controls.

## Important APIs, Types, And State
`InodeStoreBase` defines mempool-backed pointer types for `inode_t`, xattrs, and old inode maps, plus allocators, encode/decode helpers, JSON decode, dentry hash selection, and dirfrag picking. `CInodeCommitOperation` and `CInodeCommitOperations` package objecter mutations for backtrace and layout/symlink xattrs.

`CInode::validated_data` captures scrub validation results for backtrace, inode data, and raw stats. `CInode::scrub_info_t` tracks scrub/uninline progress, queued fragments, scrub headers, and dirty scrub stamps. `projected_inode` and private `projected_const_node` represent copy-on-write projected metadata used between mutation start and journal completion.

The class declares many pins (`PIN_DIRFRAG`, `PIN_CAPS`, `PIN_FREEZING`, `PIN_FROZEN`, `PIN_DIRTYRSTAT`, `PIN_EXPORTINGCAPS`, etc.), state bits (`STATE_FREEZING`, `STATE_FROZEN`, `STATE_AMBIGUOUSAUTH`, `STATE_DIRTYPARENT`, `STATE_DIRTYRSTAT`, `STATE_REPAIRSTATS`, `STATE_CLIENTWRITEABLE`, ephemeral pin bits, and others), export masks, and wait masks. Lock members include `quiescelock`, `versionlock`, `authlock`, `linklock`, `dirfragtreelock`, `filelock`, `xattrlock`, `snaplock`, `nestlock`, `flocklock`, and `policylock`.

## Control Flow And Persistence
The declaration exposes the complete lifecycle: construct with `MDCache`, open or add dirfrags, project inode/xattr/snaprealm state, journal and pop projections, mark dirty and clean, store/fetch base inode objects, store/fetch backtraces, flush pending state, encode/decode stores, encode/decode lock state, export/import cache state, and validate on-disk state.

Directory behavior is expressed through `dirfrags`, `dirfragtree`, subtree root counters, sticky dir refs, nested dirfrag queries, fragment verification, and split/merge support through `CDir`. Snapshot behavior is expressed through `first`, `last`, `old_inodes`, `oldest_snap`, snaprealm open/close/project methods, old inode copy-on-write, and stale snap data purge.

Client capability behavior is declared through the `client_caps` map, MDS cap wants, loner cap selection, add/remove/reconnect/export cap operations, allowed/issued/wanted cap calculations, client writeable tracking, and reply/message encoders. Freeze/auth behavior is declared through `can_auth_pin`, `auth_pin`, `auth_unpin`, `freeze_inode`, `unfreeze_inode`, and frozen auth-pin helpers.

## Dependencies And Integration Points
This header is a central MDS include. It depends on Ceph metadata types, lock classes, `Capability`, `ScrubHeader`, `inode_backtrace_t`, `flock`, `MDSCacheObject`, `Context`, `Counter`, mempool containers, and `LogSegmentRef`. It forward-declares many peers to reduce include pressure: `CDir`, `CDentry`, `MDCache`, `Session`, `SnapRealm`, `MutationImpl`, `MDRequestImpl`, `EMetaBlob`, and message/object operation classes.

## Risks
`CInode.h` exposes many friend classes and mutable state containers, so invariants are distributed across MDS subsystems. The RCU-like immutable pointer model requires callers to project before mutation and pop in journal order. State masks must match migration semantics. Cap counters must stay aligned with `OpenFileTable` and `SnapRealm` membership. Raw pointers to parents, dirfrags, snaprealms, and file-lock state require careful ownership and teardown.

## Test Signals
Header-level coverage should be reflected in dencoder tests for `InodeStore`/`InodeStoreBare`, compile coverage for lock type arrays, unit or integration tests around projection and dirty marking, cap add/remove accounting, snap old-inode interval lookup, dirfrag leaf verification, freeze/auth-pin behavior, and scrub validation result dumping. Static assertions are absent, so runtime assertions and MDS integration tests are the main guardrail.
