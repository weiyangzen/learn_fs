# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_common_pkt_hdr.h

Purpose: packet header constants for usNIC custom RoCE-style filtering.

Important data: defines `USNIC_ROCE_GRH_VER`, `USNIC_PROTO_VER`, and `USNIC_ROCE_GRH_VER_SHIFT`.

Control flow: `usnic_fwd_init_usnic_filter()` combines these constants into the filter's protocol-version field when steering custom usNIC/RoCE traffic.

State and persistence: no runtime state; constants encode wire/filter semantics.

Dependencies and integration: included by forwarding code and paired with ENIC `FILTER_USNIC_ID` command formats.

Risks: values must match firmware and userspace packet construction. A protocol-version mismatch would prevent filters from matching traffic.

Test signals: successful custom RoCE QP group creation, ENIC filter installation, and traffic steering to the expected RQ.
