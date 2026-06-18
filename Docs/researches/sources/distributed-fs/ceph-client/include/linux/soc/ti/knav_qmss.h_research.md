# sources/distributed-fs/ceph-client/include/linux/soc/ti/knav_qmss.h

Purpose: This TI Keystone Navigator header exposes Queue Manager Subsystem queue and descriptor-pool APIs.

Important APIs/types/functions: It defines special queue IDs (`QPEND`, `ACC`, `GP`), shared flag, queue control commands, notification callback/config types, queue open/close/control/push APIs, pool create/destroy/count/descriptor get-put/map-unmap/DMA-to-virt APIs, and `knav_qmss_device_ready`.

Control flow: Clients open queues by name or ID, optionally configure notifications, push DMA descriptors, create descriptor pools, map descriptors for DMA, recycle descriptors, and close queues/pools.

State and persistence: QMSS owns queue state, notifications, descriptor pool occupancy, DMA mappings, and hardware accumulator/QPEND behavior.

Dependencies and integration: Integrates with Keystone Navigator DMA, packet networking, DMA mapping, and interrupt notification paths.

Risks and test signals: Queue/pool leaks, wrong descriptor size, and notification races can stall packet flow. Test queue open collisions, shared queue behavior, pool exhaustion, descriptor map/unmap, notifications, and `device_ready` gating.
