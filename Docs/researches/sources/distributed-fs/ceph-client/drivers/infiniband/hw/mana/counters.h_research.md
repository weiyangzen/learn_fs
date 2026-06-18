# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/counters.h

## Purpose
`counters.h` defines the MANA RDMA counter enum indexes and prototypes for stat allocation and reading.

## Important APIs, Types, And Functions
`enum mana_ib_port_counters` enumerates requester, responder, NAK, congestion, byte, packet, and request counters. `enum mana_ib_device_counters` enumerates device-wide CNP/ECN/congestion counters. The prototypes expose `mana_ib_alloc_hw_port_stats()`, `mana_ib_alloc_hw_device_stats()`, and `mana_ib_get_hw_stats()`.

## Control Flow
The header has no runtime flow. It provides shared indexes consumed by `counters.c` descriptor arrays and stat population.

## State And Persistence
No state is stored here. Enum values are ABI-significant within the driver because they index `rdma_hw_stats->value`.

## Dependencies And Integration Points
It includes `mana_ib.h`, creating a circular-looking but guarded include relationship because `mana_ib.h` also includes `counters.h`. Header guards avoid duplicate definitions, and `device.c` uses these functions through RDMA ops.

## Risks
Adding, removing, or reordering enum entries requires synchronized changes to descriptors and firmware response mapping. The include relationship should be watched for future type dependencies that could break compilation.

## Test Signals
Build coverage plus runtime stat reads that verify descriptor count equals enum count and user-visible names map to expected firmware values.
