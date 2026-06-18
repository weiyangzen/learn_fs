# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos.c

## Purpose
`qos.c` implements TC HTB offload for RVU NIC transmit scheduling. It maintains a software QoS class tree, allocates NIX transmit scheduler queues, programs parent/topology/scheduling/shaping registers, manages extra QoS send queues, and maps class IDs to netdev TX queues.

## Important APIs, Types, and Functions
Public entry points are `otx2_setup_tc_htb()`, `otx2_get_txq_by_classid()`, `otx2_clean_qos_queues()`, and `otx2_qos_config_txschq()`. Important helpers allocate root/leaf nodes, validate priorities/quantum/DWRR, read/prepare/fill scheduler config, allocate/free txschq resources, push mailbox configuration, enable/disable SQs, delete leaves, and convert leaves to inner nodes.

## Control Flow
`otx2_setup_tc_htb()` dispatches HTB commands. Create allocates a root node and scheduler queue. Leaf allocation validates parent, priority, DWRR/static constraints, reserves a QoS qid, creates child scheduler chains down to MDQ, computes new scheduler allocation needs, applies hardware config, enables SQs if the netdev is up, updates real TX queue count, and rolls back on errors. Leaf-to-inner converts an existing leaf into an inner node and adds a child. Delete paths disable SQs, destroy node hardware/software state, compact qid usage, reset qdisc state, or collapse last child back to a leaf.

## State and Persistence
Software state lives in `pfvf->qos`: hash table, root tree, lock, qid-to-SMQ map, QoS SQ bitmap, major/default class, and link config level. Each node records class ID, scheduler level, qid, priority, rate/ceil, quantum, DWRR/static state, children, and allocated scheduler queue. Hardware state persists in NIX scheduler queues and SQ/aura/pool contexts until freed or interface teardown.

## Dependencies and Integration Points
The file depends on Linux TC HTB offload, NIX mailbox scheduler allocation/config, `otx2_tc.c` rate encoding, `qos_sq.c` SQ enable/disable, common queue/resource helpers, netdev real queue APIs, and qdisc reset internals.

## Risks and Edge Cases
Scheduler tree mutation has complex rollback; partial hardware allocation must be freed without losing the old tree. Only one DWRR group per parent is allowed. Static priority collisions and quantum limits differ by platform. VF roots start at TL2 while PF roots use TL1. Deleting a non-last QoS queue compacts qids and resets affected qdiscs. Interface-down configuration stores state for later hardware replay.

## Test Signals
Exercise all HTB commands: create/destroy, leaf alloc, leaf-to-inner, leaf delete, last leaf delete/force, query queue, invalid priorities/quantum, deep trees to MDQ limit, DWRR/static mixtures, PF vs VF roots, interface down/up replay through `otx2_qos_config_txschq()`, SQ flush through `otx2_clean_qos_queues()`, and traffic shaping accuracy.
