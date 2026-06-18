# sources/distributed-fs/ceph-client/include/rdma/ib_smi.h

Purpose: defines Subnet Management Packet structures, subnet-management attribute IDs, port/node info layouts, notice trap numbers, and helper initialization for basic query SMPs.

Important APIs and types: `struct ib_smp` is the packed SMP wire layout with common fields, hop pointer/count, M_Key, directed-route LIDs, data, initial path, and return path. Attribute constants cover notice, node description/info, switch info, GUID/port/P_Key/SL2VL/VL arbitration/forwarding tables, SM info, vendor diagnostics, LED info, and vendor mask. `struct ib_port_info`, `struct ib_node_info`, and `struct ib_vl_weight_elem` mirror management payloads. `ib_get_smp_direction()` checks the directed-route direction bit. Trap constants define link/local/error/capability/system GUID/bad key notices, and `ib_init_query_mad()` initializes a GET subnet LID-routed query.

Control flow: subnet management users allocate/fill `ib_smp`, initialize common query fields, set attr IDs/modifiers and paths, send through MAD QP0, and interpret returned management payloads. Directed-route responses use the status direction bit and path arrays.

State and persistence: no state is stored. SMP structs are transient wire buffers, while actual subnet state lives in switches, HCAs, and subnet managers.

Dependencies and integration points: depends on `ib_mad.h` for management constants and integrates with SMI agents, subnet managers, fabric discovery, port info reading, and trap handling.

Risks and test signals: risks include packed SMP layout mismatch, path hop overflow, M_Key handling mistakes, wrong endian attr IDs, direction-bit misuse, and stale port/node info field interpretation. Test SMP GET for node/port info, directed-route query/response paths, trap decode, max-hop boundary, M_Key-protected queries, and layout checks against IBTA wire sizes.
