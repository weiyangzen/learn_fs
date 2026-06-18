# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_abi.h

Purpose: kernel/userspace ABI definitions for usNIC uverbs.

Important APIs/types: defines `USNIC_UVERBS_ABI_VERSION` 4, maximum WQ/RQ/CQ counts returned per QP group, `enum usnic_transport_type`, `struct usnic_transport_spec`, `struct usnic_ib_create_qp_cmd`, and `struct usnic_ib_create_qp_resp`.

Control flow: userspace passes a create-QP command with either a custom RoCE port or UDP socket FD. Kernel responds with VF ID, QP group ID, BAR bus address/length, resource indices, selected transport, and reserved padding.

State and persistence: no kernel state, but this file is a persistent ABI contract with user libraries.

Dependencies and integration: consumed by verbs, QP group, transport, and forwarding code. It determines the uverbs ABI version advertised in `usnic_dev_ops`.

Risks: layout, enum, and version changes can break existing userspace. The response exposes BAR mapping details and fixed-size arrays, so resource-count bounds must match kernel allocation. Reserved fields should remain zeroed for forward compatibility.

Test signals: rdma-core/usNIC user library create-QP compatibility, ABI size checks across 32/64-bit builds, and mmap tests using returned BAR metadata.
