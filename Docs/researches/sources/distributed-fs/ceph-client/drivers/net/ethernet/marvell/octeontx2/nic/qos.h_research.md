# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos.h

## Purpose
`qos.h` defines the RVU NIC QoS/HTB data model and public helpers shared by TC, scheduler-tree, and QoS send-queue code.

## Important APIs, Types, and Definitions
Constants set maximum QoS levels, priorities, and leaf nodes. `enum qos_smq_operations` distinguishes SQ configuration from SMQ flush. Public prototypes cover scheduler rate encoding, HTB setup, QoS qid allocation/free, and QoS SQ enable/disable. `struct otx2_qos_cfg` carries requested/allocated scheduler queues and index bookkeeping. `struct otx2_qos` stores global QoS state. `struct otx2_qos_node` models each class/scheduler node.

## Control Flow
This header has no runtime control flow. It provides the state containers used by `qos.c` to construct and mutate HTB trees and by `qos_sq.c` to allocate/release SQ backing resources.

## State and Persistence
`otx2_qos` persists for the device lifetime and tracks the active tree, bitmap of QoS SQs, class hash table, and queue-to-SMQ mapping. `otx2_qos_node` instances persist while TC HTB classes exist.

## Dependencies and Integration Points
The header depends on Linux netdevice and rhashtable/list/bitmap support, NIX scheduler constants from common headers, and `struct otx2_nic`. It is included by `otx2_tc.c`, `qos.c`, and related common code.

## Risks and Edge Cases
Array sizes are bounded by `OTX2_QOS_MAX_LEAF_NODES` and `MAX_TXSCHQ_PER_FUNC`; mismatches with hardware queue counts can cause allocation failures. `qos_lock` protects child lists but readers using RCU/hash paths need matching lifetime discipline. Public constants duplicate a local define in `qos_sq.c`, so future changes should stay synchronized.

## Test Signals
Build coverage for QoS-enabled code, HTB tree mutation tests, queue bitmap exhaustion, class lookup by qid/classid, and lockdep under concurrent TC updates are the main signals.
