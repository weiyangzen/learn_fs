# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota-helper.h

## Purpose
This header declares quota helper APIs and macros used by the marker quota implementation.

## Important APIs, Types, And Functions
Macros include `QUOTA_FREE_CONTRIBUTION_NODE`, `QUOTA_SAFE_INCREMENT`, and `QUOTA_SAFE_DECREMENT`. Declared functions cover contribution creation, contribution xattr key insertion, quota inode context creation/retrieval, contribution deletion, inode-to-loc filling, contribution initialization, and contribution lookup.

## Control Flow And State
The header itself has no executable state. The macros mutate shared quota state under locks: contribution deletion removes the list node and drops a ref; increment/decrement macros update counters with a supplied lock.

## Dependencies And Integration Points
It includes `marker.h` and exposes helper contracts to `marker-quota.c`. It depends on `quota_inode_ctx_t` and `inode_contribution_t` definitions being available through included marker quota headers in compilation units.

## Risks And Test Signals
Macro callers must pass valid locks and initialized contribution nodes. `QUOTA_FREE_CONTRIBUTION_NODE` combines list mutation with refcount release, so double-free or double-delete bugs are possible if callers also manipulate the list. Build coverage plus quota forget/rename/unlink tests are useful signals.
