# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_unsol.h

## Purpose
`efct_unsol.h` declares the unsolicited receive entry points shared between HW RQ completion processing and the SCSI/FCP frame handling implementation.

## Important APIs, Types, and Functions
The header declares `efct_unsolicited_cb`, `efct_dispatch_fcp_cmd`, and `efct_node_recv_abts_frame`. These functions cover generic unsolicited frame dispatch, FCP command dispatch for a resolved target node, and ABTS/BLS abort frame handling for a resolved target node.

## Control Flow
`efct_hw_queues.c` calls `efct_unsolicited_cb` after parsing an RQ completion into an `efc_hw_sequence`. The implementation may call the FCP command or ABTS-specific helpers declared here, then return/repost the sequence through HW APIs.

## State and Persistence Behavior
No state is defined in the header. The declared functions operate on transient `struct efc_hw_sequence` objects and active `struct efct_node` references.

## Dependencies and Integration Points
The declarations depend on `struct efc_hw_sequence` and `struct efct_node` definitions available through including driver headers. The include guard name uses `__OSC_UNSOL_H__`, which differs from the EFCT naming style but is functionally harmless.

## Risks
The small API surface means most risks are ownership conventions: callers and implementations must agree exactly when a sequence is freed/reposted and when node references are held. Any signature change affects HW queue processing and unsolicited frame handling together.

## Test Signals
Build coverage for declarations, RQ-to-unsolicited integration tests, and ownership checks around sequence free/repost are the main validation signals.
