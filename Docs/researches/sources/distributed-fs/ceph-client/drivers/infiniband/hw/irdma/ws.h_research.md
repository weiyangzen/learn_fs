# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ws.h

## Purpose
`ws.h` defines the software representation and public interface for the irdma work-scheduler tree implemented by `ws.c`.

## Important APIs, Types, And Functions
`enum irdma_ws_node_type` distinguishes parent and leaf nodes. `enum irdma_ws_match_type` selects child lookup by VSI or traffic class. `struct irdma_ws_node` stores list linkage, parent pointer, LAN and RDMA queue-set identifiers, hardware node index, VSI index, traffic class, user priority, relative bandwidth, abstraction-layer metadata, priority type, and leaf/enable bits. The exported functions are `irdma_ws_add()`, `irdma_ws_remove()`, and `irdma_ws_reset()`.

## Control Flow
The header has no runtime control flow. It fixes the data contract used by callers that request scheduler nodes and by `ws.c` helpers that allocate, link, program, and free those nodes.

## State And Persistence
All fields in `struct irdma_ws_node` are runtime-only driver state. Handles such as `lan_qs_handle`, `l2_sched_node_id`, and `qs_handle` mirror resources created in LAN or RDMA hardware, but the header does not define persistence.

## Dependencies And Integration Points
The header includes `osdep.h` for kernel/list types, forward-declares `struct irdma_sc_vsi`, and is included by irdma code that needs scheduler add/remove/reset APIs.

## Risks
Bitfields `type_leaf` and `enable` are compact but require all node initialization paths to set sane defaults. Because the struct is shared between RDMA and LAN qset registration callbacks, changes to field names or semantics can break cross-module scheduler integration.

## Test Signals
Build coverage is the primary signal. Runtime tests should indirectly validate the struct by creating parent and leaf nodes, checking propagated handles, and removing all scheduler levels without leaks.
