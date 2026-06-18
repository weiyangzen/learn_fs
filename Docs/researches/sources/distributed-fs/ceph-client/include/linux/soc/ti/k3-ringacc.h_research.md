# sources/distributed-fs/ceph-client/include/linux/soc/ti/k3-ringacc.h

Purpose: This TI K3 header defines the Ring Accelerator API for queue/ring allocation, configuration, push/pop operations, and DMA-ring initialization.

Important APIs/types/functions: It defines `enum k3_ring_mode`, `enum k3_ring_size`, opaque `struct k3_ringacc`/`k3_ring`, `struct k3_ring_cfg`, request flags, ring request/free/reset/config APIs, ring ID/IRQ/size/free/occupancy/full queries, push/pop at head/tail, TISCI device ID query, `struct k3_ringacc_init_data`, and `k3_ringacc_dmarings_init`.

Control flow: A client obtains a ringacc by phandle, requests one or a pair of rings, configures mode/element size/memory, pushes or pops elements, resets as needed, and frees rings at teardown.

State and persistence: Ring hardware tracks occupancy, indices, element memory, proxy use, IRQ routing, and TISCI resource ownership.

Dependencies and integration: Uses device tree, platform devices, TI SCI, DMA devices, and K3 UDMA/ethernet/storage drivers.

Risks and test signals: Ring mode, element size, proxy flag, and shared ownership must match hardware users. Test request collisions, push/pop wraparound, DMA reset occupancy, IRQ retrieval, shared rings, and TISCI resource setup.
