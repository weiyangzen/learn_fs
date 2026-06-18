# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/main.c

## Purpose
`main.c` contains core MANA RDMA resource management: protection domains, user contexts and doorbells, queue and DMA-region creation, user mmap, device/port queries, capability queries, EQs, RNIC adapter lifecycle, GID/MAC configuration, and firmware CQ/QP commands.

## Important APIs, Types, And Functions
PD APIs are `mana_ib_alloc_pd()` and `mana_ib_dealloc_pd()`. Ucontext APIs are `mana_ib_alloc_ucontext()`, `mana_ib_dealloc_ucontext()`, and `mana_ib_mmap()`. Queue helpers are `mana_ib_create_kernel_queue()`, `mana_ib_create_queue()`, and `mana_ib_destroy_queue()`. DMA helpers are `mana_ib_create_dma_region()`, `mana_ib_create_zero_offset_dma_region()`, `mana_ib_gd_create_dma_region()`, and `mana_ib_gd_destroy_dma_region()`. Query/config APIs include `mana_ib_query_device()`, `mana_ib_query_port()`, `mana_ib_query_pkey()`, `mana_ib_get_port_immutable()`, `mana_ib_gd_query_adapter_caps()`, `mana_eth_query_adapter_caps()`, `mana_ib_gd_add_gid()`, `mana_ib_gd_del_gid()`, and `mana_ib_gd_config_mac()`. Firmware object APIs cover EQs, adapter, CQ, RC QP, and UD QP create/destroy.

## Control Flow
PD allocation sends `GDMA_CREATE_PD`, allowing GPA MRs for kernel PDs. Ucontext allocation obtains one doorbell page resource and mmap maps that page write-combined. Queue creation either allocates kernel GDMA queues or pins user memory and registers it as a zero-offset DMA region. DMA-region creation chooses the best supported page size, sends an initial create request with as many DMA block addresses as fit, then sends add-pages requests until all pages are registered. Query paths translate firmware caps and netdev state into RDMA attributes. RNIC setup creates one fatal EQ plus per-vector EQs, creates an adapter handle, configures GIDs/MACs through GDMA commands, and passes queue DMA regions to firmware CQ/QP creation commands, which then take ownership of those regions.

## State And Persistence
PDs store firmware handles and vport use counts. Ucontexts store doorbell page indexes. Queues own either user umem or kernel GDMA queue memory plus a DMA-region handle until firmware object creation consumes it. `adapter_caps` caches firmware limits and feature flags. EQs and adapter handles live in `mana_ib_dev`. Firmware owns DMA regions after successful CQ/QP/MR creation, so local handles are set invalid to avoid double free.

## Dependencies And Integration Points
The file is tightly coupled to MANA GDMA command ABI, MANA Ethernet port/vport APIs, RDMA umem/page-size helpers, PCI device attributes, netdev carrier/MTU state, RDMA core port immutable/query callbacks, and QP/CQ/MR setup in other MANA files.

## Risks
DMA-region multi-message creation has several edge cases around request sizing, partial failure, and expected `MORE_ENTRIES` statuses. `mana_ib_uncfg_vport()` assumes `mana_ib_get_netdev()` succeeds. `mana_ib_query_gid()` is a stub that returns success without filling a GID, relying on RDMA core GID table behavior elsewhere. Firmware ownership transitions require every failure path to know whether a DMA region is still locally owned. Doorbell page allocation/deallocation errors are logged but cannot always be recovered.

## Test Signals
Test PD kernel/user flags, vport reference counting, doorbell allocation and mmap offset validation, user and kernel queue creation/destruction, DMA region creation across one and multiple GDMA messages, supported page-size selection, port query under link up/down, RNIC and Ethernet capability translation, EQ creation unwind, adapter create/destroy, GID/MAC add/remove for IPv4/IPv6, and CQ/QP firmware ownership of DMA regions.
