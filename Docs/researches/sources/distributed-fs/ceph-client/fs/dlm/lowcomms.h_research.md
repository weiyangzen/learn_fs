# sources/distributed-fs/ceph-client/fs/dlm/lowcomms.h

## Purpose
`lowcomms.h` declares the DLM low-level communications interface and the node-id hash shared with midcomms. It defines the maximum DLM application payload size after reserving space for the midcomms options header.

## Important APIs, Types, And Functions
The header exposes lifecycle functions, address registration, node close/connect helpers, message allocation and commit helpers, retransmit helpers, and slab cache constructors. `CONN_HASH_SIZE` is fixed at 32 and `nodeid_hash()` assumes common cluster node ids are small/sequential.

## Control Flow
Callers initialize lowcomms once, start it when DLM communications should listen/connect, allocate messages by node id, commit or drop message handles, close specific nodes during recovery/fencing, and stop/shutdown transport on lockspace teardown.

## State And Persistence
The header itself owns no state. Its constants shape the in-memory connection hash and payload limits used by `lowcomms.c` and `midcomms.c`.

## Dependencies And Integration Points
It includes `dlm_internal.h` for DLM core types and exposes `struct dlm_msg` handles to midcomms/rcom users without requiring callers to know the writequeue internals. `DLM_MAX_APP_BUFSIZE` depends on `DLM_MAX_SOCKET_BUFSIZE` from config and `struct dlm_opts`.

## Risks
One declaration, `dlm_lowcomms_shutdown_node(int nodeid, bool force)`, has no implementation in the inspected source set, so users must verify tree-wide build status before depending on it. Payload-size constants must stay consistent with wire format changes.

## Test Signals
Compile coverage should catch declaration/definition mismatches. Runtime tests should cover max-size message allocation and correct behavior when callers pass invalid node ids or oversized messages.
