# sources/distributed-fs/ceph-client/include/rdma/opa_smi.h

Purpose: OPA Subnet Management Packet definitions and helpers for LID-routed and directed-route SMPs.

Important APIs/types/functions: `OPA_SMP_LID_DATA_SIZE`, `OPA_SMP_DR_DATA_SIZE`, `OPA_SMP_MAX_PATH_HOPS`, `OPA_MAX_VLS/SLS/SCS`, `OPA_LID_PERMISSIVE`, packed `struct opa_smp`, OPA subnet management attribute IDs, `struct opa_node_description`, `struct opa_node_info`, `opa_get_smp_direction`, `opa_get_smp_data`, `opa_get_smp_data_size`, and `opa_get_smp_header_size`.

Control flow: Helpers branch on `mgmt_class == IB_MGMT_CLASS_SUBN_DIRECTED_ROUTE`: directed-route packets use DR paths and DR data, while LID-routed packets use the larger LID data area. Direction delegates to the IB SMP helper through a cast.

State and persistence behavior: Defines transient management packets. The packet may carry fabric state, but the header owns no durable state.

Dependencies and integration points: Depends on RDMA MAD and IB SMI headers. Integrates with OPA PortInfo, OPA address helpers, subnet managers/agents, and provider MAD processing.

Risks: Cast compatibility with `struct ib_smp` depends on common header layout. Wrong data-size helper use can overrun the smaller directed-route payload. Attribute IDs are big-endian constants.

Test signals: Directed-route versus LID-routed data pointer/size/header-size checks, packed size checks, hop limit handling, attribute ID comparisons, and direction extraction compatibility.
