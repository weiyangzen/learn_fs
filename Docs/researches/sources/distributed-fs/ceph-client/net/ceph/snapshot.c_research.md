# sources/distributed-fs/ceph-client/net/ceph/snapshot.c

## Purpose
`snapshot.c` implements the reference-counted `ceph_snap_context` helper used by libceph and CephFS to carry snapshot sequence metadata and an inline array of snapshot ids for reads and writes.

## Important APIs, types, and functions
- `ceph_create_snap_context()` allocates one object sized for `struct ceph_snap_context` plus `snap_count` inline snap ids, initializes `nref` to one, and records `num_snaps`.
- `ceph_get_snap_context()` increments the refcount when passed a non-NULL context.
- `ceph_put_snap_context()` decrements the refcount and frees the context when it reaches zero.

## Control flow
Creation computes the variable-length allocation size, uses `kzalloc()` with caller-provided GFP flags, sets the reference count, and leaves sequence and snap array contents for the caller to fill. Get/put are thin refcount wrappers and tolerate NULL in the put path.

## State and persistence behavior
Snapshot context state is entirely in-memory but represents durable Ceph snapshot ordering observed elsewhere. The helper owns only allocation and lifetime; callers own the meaning and initialization of `seq` and `snaps[]`.

## Dependencies and integration points
`osd_client.c` stores a referenced snap context in write requests and encodes `snap_seq` plus snap ids into MOSDOp requests. CephFS address-space and snapshot code also share contexts for dirty pages and writeback.

## Risks and edge cases
- Integer overflow in size computation would be serious if `snap_count` were not bounded by upstream protocol/caller constraints.
- Callers must fill `seq` and `snaps[]`; creation intentionally does not validate semantic ordering.
- Refcount misuse can leak or prematurely free contexts shared by in-flight OSD requests.

## Test signals
Tests should cover zero-snapshot allocation, multi-snapshot allocation, get/put lifetime, NULL get/put behavior where applicable, and request encoding that includes expected snapshot sequence and ids.
