# sources/distributed-fs/ceph-client/include/linux/ceph/osd_client.h

## Purpose

`osd_client.h` declares the libceph OSD client: request construction, object targeting, OSD connection state, sparse-read handling, linger/watch/notify support, backoff tracking, map handling, and request lifecycle APIs.

## Important APIs, Types, and Functions

Key types include `ceph_sparse_extent`, `ceph_sparse_read`, `ceph_osd`, `ceph_osd_data`, `ceph_osd_req_op`, `ceph_osd_request_target`, `ceph_osd_request`, `ceph_osd_linger_request`, `ceph_hobject_id`, `ceph_osd_backoff`, and `ceph_osd_client`. APIs cover setup/init/stop, map handling, aborts, request/op allocation and data attachment, class/xattr/copy/alloc-hint helpers, request start/cancel/wait/sync, class calls, watch/unwatch/notify/list-watchers, and sparse extent helpers.

## Control Flow

Callers allocate a request with one or more ops, initialize target object and op payloads, allocate messages, and start the request. The OSD client maps object locators to PGs and acting OSDs using the current osdmap, sends over per-OSD messenger connections, tracks in-flight requests by tid, handles replies/completions, and remaps/resends across OSD map changes. Linger requests keep watch/notify registrations alive across reconnects.

## State and Persistence Behavior

State spans current `ceph_osdmap`, OSD connection RB trees/LRU, request and linger RB trees, map-check queues, request tid counters, mempools, workqueues, timeout work, sparse-read parse state, and backoff mappings. Persistent effects are RADOS object mutations and watch registrations on OSDs.

## Dependencies and Integration Points

It depends on OSD maps, messenger, msgpool, auth, pagelist, snap contexts, inodes, block APIs, and RADOS op constants. It is the data path used by CephFS, RBD-like users, class-lock helpers, and monitor map updates.

## Risks and Edge Cases

Request lifetime is complex: krefs, completions, callbacks, mempool ownership, snap contexts, and message refs must align. Sparse-read replies can force extent-array reallocation and endian conversion. Map changes, full/paused flags, redirects, backoffs, and linger reconnects can cause duplicate, lost, or indefinitely paused requests if state transitions are wrong.

## Test Signals

Run read/write/truncate/class/xattr/copy ops, map-remap and resend tests, OSD down/up failover, linger watch notify reconnects, sparse-read decoding including realloc, timeout/abort paths, mempool pressure, and race tests around request cancel versus reply.
