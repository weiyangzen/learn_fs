# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_ah.c

Purpose: implements ocrdma address handle creation, destruction, querying, and basic MAD performance-management processing for RoCE.

Important APIs/functions: internal `ocrdma_hdr_type_to_proto_num` maps RDMA network type to Ethernet protocol; `set_av_attr` fills an ocrdma address vector; exported verbs are `ocrdma_create_ah`, `ocrdma_destroy_ah`, `ocrdma_query_ah`, and `ocrdma_process_mad`.

Control flow: create validates RoCE AH with GRH, refreshes service level if requested, reads VLAN from the SGID attributes, allocates an AV, records the GID network type, and calls `set_av_attr`. AV setup chooses IBoE/IPv4/IPv6 protocol, applies VLAN/PFC service-level tagging, resolves destination MAC, copies Ethernet header, then writes either IPv4 or GRH/IPv6-style fields with SGID/DGID, flow label, traffic class, PD id, next-header, and hop limit. User PDs receive a compact AH id/type/VLAN word in their AH table. Destroy frees the AV. Query reconstructs an `rdma_ah_attr` from the stored AV. MAD processing replies to performance management MADs via `ocrdma_pma_counters`.

State and persistence: AH state lives in `struct ocrdma_ah` and the device AV table; user contexts may get an AH id entry. It persists until AH destroy.

Dependencies and integration: depends on RDMA address/GID helpers, neighbour/netevent headers, `ocrdma_alloc_av/free_av`, service-level init, stats counters, VLAN/PFC state from `ocrdma_dev`, and hardware AV layout from SLI headers.

Risks: protocol and endian handling are critical; `ocrdma_query_ah` infers GRH offset from AV validity/VLAN layout. VLAN 0 with PFC logs warnings but proceeds. Incorrect SGID network type or AH table index can break userspace sends.

Test signals: create/query/destroy AHs for IB GRH, IPv4 RoCEv2, IPv6 RoCEv2, VLAN and non-VLAN paths, multicast and link-local destination MAC resolution, userspace AH table updates, and PMA MAD counter queries.
