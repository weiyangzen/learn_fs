# sources/distributed-fs/ceph/src/mds/MDSMetaRequest.h

## Purpose
Defines a minimal base object for MDS-originated metadata requests. It carries an operation code and `ceph_tid_t` transaction id for rank-internal request tracking.

## Important APIs, Types, And Functions
`MDSMetaRequest(int op, ceph_tid_t tid)` initializes private fields. `get_op()` and `get_tid()` expose them. The destructor is virtual so derived request objects can be owned through base pointers.

## Control Flow
There is no active control flow. Callers construct a request, store it, inspect operation/tid during dispatch or completion, and delete it via the virtual destructor.

## State And Persistence Behavior
Purely in-memory; no encoding, journaling, or persistence. Durability and replay are caller responsibilities.

## Dependencies And Integration Points
Depends only on `include/types.h`. In this subset it integrates with `MDSRank::internal_client_requests`, which owns `std::unique_ptr<MDSMetaRequest>` for internal client-like operations.

## Risks
Accessors are not `const`. The class does not represent completion, timeout, or cancellation. Tids must remain unique and be cleaned up by the owner.

## Test Signals
Construction/accessor tests, virtual destruction through base pointer, and indirect tests around internal MDS requests creating, storing, and removing tracked tids.
