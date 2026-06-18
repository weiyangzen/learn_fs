# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_cq.c

## Purpose
This file adapts core mlx4 completion queues for the mlx4 Ethernet driver. It allocates Ethernet CQ buffers, activates them with IRQ/EQ/NAPI bindings, sets completion callbacks for TX/RX, and tears them down.

## Important APIs and Functions
- `mlx4_en_create_cq()` allocates the Ethernet CQ structure and hardware queue resources on a requested NUMA node.
- `mlx4_en_activate_cq()` assigns EQ vectors, initializes doorbells and buffers, enables timestamping when configured, calls core `mlx4_cq_alloc()`, and attaches NAPI.
- `mlx4_en_deactivate_cq()` detaches NAPI and frees the core CQ.
- `mlx4_en_destroy_cq()` frees hardware queue resources and releases assigned EQs.
- `mlx4_en_set_cq_moder()` and `mlx4_en_arm_cq()` expose moderation and arming.

## Control Flow
Create only allocates memory and DMA resources. Activate binds the CQ to a netdev and vector, handling RX vector assignment and TX vector reuse from RX CQs. Depending on CQ type, it installs `mlx4_en_tx_irq` or `mlx4_en_rx_irq`, adds NAPI, and links NAPI to netdev queue IDs. Deactivate reverses NAPI and hardware CQ state.

## State and Persistence
State includes `struct mlx4_en_cq` fields for size, buffer, CQ index, ring, type, vector, IRQ affinity mask, NAPI, and embedded core `mcq`. Doorbell and buffer state comes from `mlx4_hwq_resources`.

## Dependencies and Integration Points
It integrates with core CQ allocation in `cq.c`, queue resources from `alloc.c`, EQ assignment, netdev NAPI APIs, TX/RX polling functions, timestamp configuration, and IRQ affinity.

## Risks and Test Signals
Risks include EQ leak on activation errors, TX relying on RX CQ vector availability, NAPI teardown ordering, and timestamp enable mismatches. Test signals include interface open/close, queue count changes, IRQ affinity inspection, NAPI poll activity, CQ moderation changes, and hwtstamp enablement.
