# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_device.h

Purpose: Central HNS RoCE driver interface header. It defines hardware constants, capability flags, resource structs, device state, hardware callback tables, inline conversions/helpers, and prototypes shared across the driver.

Important APIs/types/functions: Major structs include `hns_roce_dev`, `hns_roce_caps`, `hns_roce_hw`, `hns_roce_qp`, `hns_roce_cq`, `hns_roce_srq`, `hns_roce_mr`, `hns_roce_mtr`, `hns_roce_hem_table`, `hns_roce_cmdq`, `hns_roce_ucontext`, DB/page structs, EQ structs, and resource tables. Inline helpers convert RDMA core objects to driver objects, compute buffer DMA offsets, convert page sizes to hardware units, map traffic class/DSCP, and fetch netdev/bus data.

Control flow: This header establishes contracts used by object lifecycle files. `hns_roce_dev` aggregates PCI/device handles, MMIO bases, caps, command state, ID allocators, MR/CQ/SRQ/QP/EQ/HEM tables, workqueues, private hardware data, debugfs state, and DFX counters. `hns_roce_hw` is the hardware abstraction vtable used by generic code for mailbox, context programming, HEM set/clear, QP modification, EQ init, queries, counters, and DSCP mapping.

State and persistence: Most persistent runtime state is declared here: per-device caps, resource tables, xarrays, IDAs, doorbell page directories, MTR/HEM lists, QP/CQ/SRQ refcounts and completions, reset/device states, and debug counters.

Dependencies and integration: Includes PCI, RDMA verbs, HNS ABI, and debugfs declarations. It exposes prototypes implemented across allocation, command, AH, MR, CQ, DB, QP, SRQ, restrack, main, and HEM files. It also binds to netdevs for RoCE, congestion control, reset handling, and optional bonding through caps/helpers.

Risks: Because this is the shared contract header, layout or enum changes have broad ABI and hardware effects. Capability flags gate optional resource cleanup and creation behavior. Inline object conversions rely on embedding layout. Test signals include full driver build, sparse/lockdep, uverbs ABI compatibility, hardware capability profile validation, reset teardown coverage, optional cap matrix testing, and resource leak checks across all object types.
