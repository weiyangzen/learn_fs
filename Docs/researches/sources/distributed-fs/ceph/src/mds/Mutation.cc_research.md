# sources/distributed-fs/ceph/src/mds/Mutation.cc

## Purpose

`Mutation.cc` implements request/mutation lifetime helpers for Ceph MDS operations. It manages cache pins, auth pins, held lock descriptors, projected dirty metadata, request-specific extension state, diagnostics, and lock-cache attachment.

## Important APIs, Types, and Functions

- `MutationImpl::pin()`, `unpin()`, `drop_pins()` manage `MDSCacheObject::PIN_REQUEST`.
- `set_stickydirs()` and `put_stickydirs()` protect directory-fragment state on an inode.
- `start_locking()` and `finish_locking()` track the current lock acquisition attempt.
- `is_rdlocked()` and `is_wrlocked()` also consult an attached `MDLockCache`.
- `LockOp::print()`, `LockOpVec::erase_rdlock()`, and `sort_and_merge()` normalize lock acquisition vectors.
- Auth pin helpers are `auth_pin()`, `auth_unpin()`, `drop_local_auth_pins()`, `set_remote_auth_pinned()`, and `_clear_remote_auth_pinned()`.
- `add_updated_lock()`, `add_cow_inode()`, `add_cow_dentry()`, `apply()`, and `cleanup()` commit projected metadata state and release local pins.
- `MDRequestImpl` implements lazy `More` allocation, freeze/ambiguous-auth helpers, path helpers, batching checks, peer/client request reset/release, printing, and formatter dump output.
- `MDLockCache` attaches cached lock and dirfrag references to locks/caps for create/unlink style operations.

## Control Flow

Mutation users pin cache objects before operations that must keep them alive, auth-pin objects before mutating authority-owned state, and collect locks in `locks`. When metadata projections are ready, `apply()` pops projected inode/fnode state, marks copy-on-write inodes/dentries dirty, and marks scatter locks dirty. `cleanup()` releases local auth pins and normal pins; the destructor asserts that no locks, lock cache, pins, or auth pins remain.

`MDRequestImpl::more()` lazily allocates a large optional state block for uncommon peer, rename, snap, flock, export, and internal lookup data. Freeze auth pin paths set `rename_inode`, auth-pin it, freeze the inode, then convert to a frozen auth pin. Drop-local-auth-pins unfreezes when needed before delegating to `MutationImpl`.

`can_batch()` allows only simple root `GETATTR` and one-component non-snap `LOOKUP` requests with no auth pins, remote pins, lock cache, or locks. `MDLockCache` attaches itself to cached locks and auth-pinned dirfrags, then detaches symmetrically.

## State and Persistence Behavior

This file does not journal by itself, but it controls which metadata becomes dirty and associated with a `LogSegmentRef`. `apply()` uses `ls` while popping projected state and marking dirty objects. Request state includes `reqid`, attempt, peer target, `object_states`, lock sets, updated locks, dirty COW lists, and optional `More` fields.

## Dependencies and Integration Points

Dependencies include `ScatterLock`, `SimpleLock`, `BatchOp`, `CDentry`, `CInode`, `CDir`, `MClientRequest`, `MMDSPeerRequest`, `TrackedOp`, and formatter/dump infrastructure. It is a foundational type for `Migrator`, `MDCache`, locker paths, server request handling, and op tracking.

## Risks

- Destructor assertions make cleanup bugs fatal, which is desirable but means every error path must release pins/locks.
- `LockOpVec::sort_and_merge()` assumes same-object grouping and non-empty vectors in its iterator logic.
- Remote auth pins are counted separately and must be cleared by the distributed request protocol.
- Freeze auth pin state lives in optional `More`, so callers must not bypass the specialized drop/unfreeze path.
- `release_client_request()` and `reset_peer_request()` use the inherited tracked-op mutex; ownership changes should be reviewed carefully.
- `MDLockCache::get_cap_bit_for_lock_cache()` aborts for unsupported opcodes.

## Test Signals

Tests should cover pin/auth-pin reference counts, apply/cleanup ordering, lock vector merge semantics, lazy `More` allocation, freeze/unfreeze auth pin paths, batching eligibility, formatter dump for client/peer/internal ops, and `MDLockCache` attach/detach symmetry. Fault tests should verify cleanup after aborted requests.
