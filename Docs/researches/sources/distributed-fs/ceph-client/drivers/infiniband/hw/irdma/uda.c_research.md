# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda.c

## Purpose
This file implements UDA CQP operations for address handles and multicast groups. It writes hardware WQEs for create/destroy AH and create/modify/destroy multicast group contexts, and maintains the software multicast group membership array.

## Important APIs, Types, And Functions
- `irdma_sc_access_ah()` builds and posts a Manage Address Vector CQP WQE from `struct irdma_ah_info`.
- `irdma_access_mcast_grp()` builds and posts a Manage Multicast Group CQP WQE from `struct irdma_mcast_grp_info`.
- `irdma_create_mg_ctx()` serializes valid multicast group entries into the DMA context block consumed by hardware.
- `irdma_sc_add_mcast_grp()` adds or reference-counts a `(dest_port, qp_id)` entry in software context.
- `irdma_sc_del_mcast_grp()` decrements use count, invalidates entries, decrements `no_of_mgs`, and compacts the array when removing a non-last entry.
- `irdma_compare_mgs()` is the equality predicate used by add/delete.

## Control Flow
AH access gets the next CQP SQ WQE, writes destination MAC, PD index, traffic class or hop limit, VLAN, ARP index, flow label, IPv4 or IPv6 source/destination addresses, then publishes the WQE header with valid bit, opcode, loopback, IPv4, AH index, and VLAN insertion flags before posting the CQP SQ.

Multicast access validates `mg_id`, allocates a CQP WQE, rebuilds the DMA multicast context from current valid entries, writes context physical address, VLAN/QS handle, destination MAC, HMC function id, destination IP address, and finally publishes a header containing opcode, multicast group index, VLAN validity, and IP version.

Software add scans for an identical valid entry first and increments `use_cnt` if found; otherwise it records the first free slot and initializes it. Delete scans for a matching valid entry, decrements `use_cnt`, invalidates it when the count reaches zero, and moves the last valid entry into the gap to keep packed context ordering.

## State And Persistence
AH state is held in hardware after the CQP command and described by caller-owned `irdma_ah_info`/`irdma_sc_ah`. Multicast software state is `mg_ctx_info[]`, `valid_entry`, `use_cnt`, and `no_of_mgs`; hardware-facing state is the DMA buffer `dma_mem_mc`. CQP WQEs are transient but posted to persistent hardware queues.

## Dependencies And Integration Points
The file depends on `type.h`, `protos.h`, `uda.h`, `uda_d.h`, CQP WQE allocation/posting, `FIELD_PREP` bitfield macros, DMA ordering, and Ethernet address conversion. It is used by RDMA verbs/CM paths that create AHs and join/leave multicast groups, and by IEQ GEN2+ AH creation in `puda.c`.

## Risks And Edge Cases
The add/delete functions do not lock the multicast context, so callers must serialize membership changes. `irdma_sc_del_mcast_grp()` compaction assumes valid entries are packed in the first `no_of_mgs` slots; external mutation could break that invariant. AH and multicast WQE field placement is generation/hardware-contract sensitive. `mg_id` is range checked, but AH indexes and PD/ARP values are trusted inputs.

## Test Signals
Test AH create/destroy for IPv4, IPv6, VLAN insertion, loopback, and varied PD indexes. Test multicast add/delete duplicate membership, last-entry removal, middle-entry compaction, full context returning `-ENOMEM`, invalid `mg_id`, and emitted CQP completions for create/modify/destroy operations.
