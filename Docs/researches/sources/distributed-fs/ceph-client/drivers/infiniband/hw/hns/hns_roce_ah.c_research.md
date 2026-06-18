# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_ah.c

Purpose: Implements address handle creation and query for HNS RoCE, translating RDMA core AH attributes into the driver's hardware address vector.

Important APIs/types/functions: `hns_roce_create_ah()` fills `struct hns_roce_ah.av`; `hns_roce_query_ah()` reconstructs `rdma_ah_attr` from that vector. `get_ah_udp_sport()` derives a RoCE UDP source port from the GRH flow label or a valid random port when no flow label is supplied.

Control flow: Creation reads GRH, port, SGID index, static rate, hop limit, flow label, UDP source port, traffic class, and SL. For RoCEv2 GIDs it asks hardware for DSCP-to-priority mapping and may replace SL with the mapped priority when the NIC uses DSCP TC mapping. It validates SL, copies destination GID and DMAC, records HIP08 VLAN fields, and optionally returns priority, TC mode, and DMAC to userspace.

State and persistence: AH state is stored in the in-memory `hns_roce_av` embedded in the AH. There is no firmware context allocation in this file; AH destruction is inline no-op in the header.

Dependencies and integration: Uses RDMA core AH/GRH helpers, `rdma_read_gid_l2_fields()`, HNS hardware `get_dscp`, `check_sl_valid()`, PCI revision checks, and DFX error counters. It depends on `hns_roce_hw_v2.h` ABI structures for userspace response shape.

Risks: HIP08 rejects userspace AH creation, so ABI behavior differs by revision. DSCP priority mapping failures other than `-EOPNOTSUPP` abort creation. VLAN extraction, SGID attributes, and SL validation are correctness-critical for packet routing. Test signals include RoCEv1/RoCEv2 AH creation, DSCP mode mapping, HIP08 VLAN cases, invalid SL rejection, and userspace response compatibility by `udata->outlen`.
