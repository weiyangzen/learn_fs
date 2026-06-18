# sources/distributed-fs/ceph/src/client/MetaRequest.cc

## Purpose
`MetaRequest.cc` implements diagnostics and dentry setters for client metadata requests sent to MDS.

## Important APIs, Types, and Functions
`MetaRequest::dump()` emits request id, op, paths, inode/dentry targets, timestamps, MDS routing, retry/forward counters, unsafe status, caller/owner ids, release counts, flags, and abort code. `set_dentry()`, `dentry()`, `set_old_dentry()`, and `old_dentry()` manage intrusive dentry refs for primary and secondary paths.

## Control Flow
Client operation builders populate a `MetaRequest`, then `make_request()`/`send_request()` route it to an MDS. Admin/debug dumping can inspect live requests. Dentry setters assert they are only called once, making request construction order explicit.

## State and Persistence Behavior
Requests are transient in-memory records. Unsafe requests correspond to operations not yet safe on the MDS journal, but this file only reports that state.

## Dependencies and Integration Points
It depends on client cache types, MDS request/reply messages, and `Formatter`. `Client` owns request maps/lists and lifecycle, while `MetaSession` links active/unsafe requests.

## Risks and Edge Cases
Dumping assumes referenced inode/dentry objects remain alive through intrusive refs. Setter assertions catch accidental replacement but can abort on unexpected rebuild paths. Age uses current coarse clock minus op stamp.

## Test Signals
Request dump/admin output, single-assignment assertions, dentry lifetime across async request completion, abort reporting, and unsafe request visibility.
