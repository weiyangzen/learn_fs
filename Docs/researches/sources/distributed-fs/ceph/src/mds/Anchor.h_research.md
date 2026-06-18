# sources/distributed-fs/ceph/src/mds/Anchor.h

## Purpose
This header defines `Anchor` and its recovered/opened variants. An anchor represents the primary parent linkage of an inode and lets the MDS recursively reconstruct paths by following anchored ancestors.

## Important APIs, Types, and Functions
`Anchor` stores `ino`, `dirino`, `d_name`, `d_type`, a set of `frag_t` values, and runtime `omap_idx`. It provides constructors, `encode()`, `decode()`, `dump()`, `generate_test_instances()`, equality, and `WRITE_CLASS_ENCODER`. `RecoveredAnchor` extends `Anchor` with an auth-rank hint. `OpenedAnchor` extends `Anchor` with a mutable child reference count `nref`.

## Control Flow
There is no complex flow in the header. The type is a value container with versioned serialization implemented in `Anchor.cc`.

## State and Persistence Behavior
The durable state is the inode number, parent inode number, dentry name/type, and fragments. `omap_idx`, recovered auth, and opened reference counts are runtime management state. The invariant described in the comment is that adding an inode to the anchor table also requires ancestor anchors, enabling recursive path lookup.

## Dependencies and Integration Points
It depends on Ceph inode, fragment, buffer, MDS rank, and filesystem types. It integrates with MDS anchor table persistence and recovery code, and uses standard Ceph class encoder conventions.

## Risks and Test Signals
Risks are incomplete ancestor maintenance outside this file, stale `frags`, and confusing durable vs runtime fields. Tests should validate equality, encoding, and recovery/opened behavior in anchor-table scenarios where paths cross fragmented directories.
