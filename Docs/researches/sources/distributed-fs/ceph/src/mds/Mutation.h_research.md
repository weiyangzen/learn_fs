# sources/distributed-fs/ceph/src/mds/Mutation.h

## Purpose

`Mutation.h` declares the common mutation and metadata request state used throughout Ceph MDS. It models cache object pinning, auth pinning, lock ownership, projected metadata updates, peer/client/internal request context, and lock-cache reuse.

## Important APIs, Types, and Members

- `MutationImpl : public TrackedOp` is the base mutation state.
- `ObjectState` tracks per-cache-object request pin, local auth pin, and remote auth pin owner.
- `LockOp` models rdlock, wrlock, xlock, remote wrlock, and state pin flags for a `SimpleLock`.
- `LockOpVec` accumulates ordered lock requests and can sort/merge them.
- `lock_set locks` holds acquired locks; `lock_cache` can contribute cached read/write locks.
- Request lifetime state includes `reqid`, optional `result`, `attempt`, `ls`, `peer_to_mds`, object states, pin counters, sticky dirs, current `locking`, and flags such as `committing`, `aborted`, `killed`, and `dead`.
- Dirty/projected state includes `projected_nodes`, `updated_locks`, `dirty_cow_inodes`, and `dirty_cow_dentries`.
- `MDRequestImpl` extends `MutationImpl` for client, peer, and internal MDS requests.
- `MDRequestImpl::More` stores uncommon fields: peers, witnesses, rename/auth-freeze state, imported sessions/caps, flock/snap data, waiting contexts, export/fragment data, and internal lookup paths.
- `Params` carries construction metadata and message refs.
- `MDPeerUpdate` models peer rollback/waiter cleanup.
- `MDLockCache` caches lock/auth-pin state associated with a client capability and opcode.

## Control Flow

Callers construct `MDRequestImpl` from `Params`, then progressively fill path, lock, pin, peer, and optional `More` fields as request processing advances. Mutation cleanup is explicit; the destructor only verifies that cleanup already happened. The lazy `More` split keeps common request memory smaller while still supporting complex rename, peer update, export, and snap operations.

## State and Persistence Behavior

The header declares state that is later used to mark projected metadata dirty against a log segment. It also stores request identity and op timestamps for tracking/dumps. No persistence occurs in the header itself, but `ls`, projected nodes, COW lists, peer rollback buffers, and imported cap/session maps are central to journaled metadata mutation and replay behavior.

## Dependencies and Integration Points

Dependencies include `TrackedOp`, `Context`, `interval_set`, `elist`, `filepath`, `Capability`, `LogSegmentRef`, `mdstypes`, and `MMDSPeerRequest`. The types are shared by locker code, MDCache request processing, server ops, migrator export/import, batching, and diagnostics.

## Risks

- This is a high-fanout shared header; layout or semantic changes can affect many MDS paths.
- Raw pointers dominate because the cache owns objects; correct pin/auth-pin discipline is mandatory.
- Optional `More` fields require `has_more()` checks before const access.
- The destructor asserts no outstanding locks or pins, so request lifecycle tests must cover every abort path.
- `MDLockCache` ties cached lock validity to cap lifetime and opcode-specific cap bits.

## Test Signals

Useful tests include construction from `Params`, client/peer/internal descriptor output, lock-flag predicates, lock cache eligibility, optional `More` lifecycle, auth pin count invariants, and memory/lifetime behavior for aborted or killed requests. Compile-time users should be checked for direct field access that bypasses helper invariants.
