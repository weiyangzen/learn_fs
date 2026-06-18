# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_hw.c

## Purpose
`icrdma_hw.c` provides the Gen2/E810-style hardware register map, interrupt operations, statistics layout, masks/shifts, and capability flags for the shared IRDMA core.

## Important APIs, types, and functions
The exported API is `icrdma_init_hw`. Local helpers `icrdma_ena_irq`, `icrdma_disable_irq`, and `icrdma_cfg_ceq` implement interrupt programming. Static arrays map common register, mask, shift, and stat indexes to Gen2 definitions.

## Control flow, state, and persistence
`icrdma_init_hw` populates MMIO pointers, masks, shifts, doorbell addresses, IRQ ops, page-size capabilities, statistics metadata, RDMA read/write limits, push-page limits, minimum WQ size, SQ chunking, and feature flags such as RTS AE and CQ resize. IRQ enable uses CEQ interrupt moderation when configured and handles Gen1-style indexing only as a compatibility branch.

## Dependencies and integration points
The file depends on `icrdma_hw.h`, common register enums in `irdma.h`, CQP/CEQ code in `hw.c`, and Gen2 auxiliary setup in `icrdma_if.c`. It provides hardware attributes later consumed by verbs, queue setup, and HMC sizing.

## Risks and test signals
Risks include incorrect field masks, interrupt moderation interval units, vector indexing, and stat map offsets with mixed 24/32/48/56-bit counters. Tests should validate interrupt enable/disable writes, CEQ mapping, stats reads, feature flag exposure, and behavior with configured `ceq_itr`.
