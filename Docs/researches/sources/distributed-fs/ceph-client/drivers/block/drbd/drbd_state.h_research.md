# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state.h

## Purpose

`drbd_state.h` declares the public state-machine interface and macro language used by DRBD callers to express state changes. It is the small but important contract between administrative paths, receiver/worker code, request code, and the implementation in `drbd_state.c`.

## Important APIs, Types, and Macros

The `NS`, `NS2`, and `NS3` macros build `(mask, value)` pairs for one, two, or three state fields. The `_NS`, `_NS2`, and `_NS3` variants read the current state from a device and produce a full new state suitable for callers already holding state protection. Field-specific masks such as `role_MASK`, `conn_MASK`, `disk_MASK`, `susp_nod_MASK`, and `susp_fen_MASK` connect named state fields to the bit layout of `union drbd_state`.

`enum chg_state_flags` controls transition behavior. `CS_HARD` bypasses soft policy checks for environmental facts; `CS_VERBOSE` logs failures; `CS_WAIT_COMPLETE` waits for queued after-change work; `CS_SERIALIZE` uses `state_mutex`; `CS_ORDERED` combines wait and serialization; `CS_LOCAL_ONLY` suppresses cluster-wide connection handling; the `CS_DC_*` flags control which fields are displayed as connection-level changes; `CS_IGN_OUTD_FAIL` relaxes outdate failure handling; and `CS_INHIBIT_MD_IO` serializes graceful detach with metadata I/O.

`union drbd_dev_state` is a compact device-state bitfield distinct from the wider `union drbd_state`: it tracks role, peer role, connection, local disk, peer disk, and resync pause bits, but excludes some resource-level suspension flags. Public prototypes expose device state requests, connection state requests, detach, aggregate state queries, and `drbd_resume_al()`.

## Control Flow

Typical callers use `drbd_request_state(device, NS(field, value))`, which expands to `_drbd_request_state(..., CS_VERBOSE + CS_ORDERED)`. Lower-level callers can choose flags explicitly through `_drbd_request_state()` or can call `_drbd_set_state()` only when they already satisfy the locking contract. Connection-wide callers use `_conn_request_state()` under `req_lock` or `conn_request_state()` when they need the wrapper to take the lock.

## State and Persistence Behavior

This header does not persist state itself. It defines how state writes are represented and which flags request serialization with metadata I/O. The macros are expression-style GNU C blocks, so they evaluate to typed `union drbd_state` objects rather than raw integers, helping call sites avoid ad hoc bit manipulation.

## Dependencies and Integration Points

The header forward-declares `struct drbd_device` and `struct drbd_connection`, but relies on DRBD enums and `union drbd_state` from included DRBD core headers at users. Its macros are used throughout DRBD code paths that initiate transitions: administration, receiver, worker, request error handling, attach/detach, verify, and resync.

## Risks and Edge Cases

The macros depend on field names matching mask macros exactly. Because they are GNU statement expressions, they are kernel/GCC-specific and must not be reused in plain C tooling without that support. `_NS*` reads live state and should only be used in contexts where callers understand locking and race semantics. Flag combinations matter: omitting `CS_WAIT_COMPLETE` can leave important after-state side effects queued, while incorrectly using `CS_HARD` can skip policy checks.

## Test Signals

Compilation is the first guard for mask/field drift. Runtime tests should verify common macro call sites perform the intended transitions and that `CS_ORDERED`, `CS_WAIT_COMPLETE`, and `CS_INHIBIT_MD_IO` produce observable wait/serialization behavior during detach, promotion, disconnect, and resync start.
