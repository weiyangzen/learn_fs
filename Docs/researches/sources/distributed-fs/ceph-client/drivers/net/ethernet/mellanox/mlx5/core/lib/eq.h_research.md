# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/eq.h

Purpose: Defines core event queue structures and helper APIs for mlx5 asynchronous and completion EQ handling.

Important APIs and types: Declares tasklet context, CQ radix table, base `mlx5_eq`, async EQ, and completion EQ structures. Inline helpers compute EQ size, locate EQEs in fragmented buffers, check the next software-owned EQE by owner bit, and update the consumer index doorbell. Public APIs cover EQ table lifecycle, CQ add/delete, EQ lookup, IRQ-disabled polling, command recovery, IRQ synchronization, debugfs hooks, IRQ freeing, RFS CPU rmap, and completion IRQ number lookup.

State and dependencies: EQ state includes fragment buffer control, core device, CQ table, MMIO doorbell, consumer index, vector/IRQ numbers, EQ number, debug resource, and IRQ object. Doorbell writes are big-endian raw MMIO followed by `wmb()`.

Risks and test signals: Owner-bit handling and consumer-index doorbells are data-path critical. Tests should cover wraparound, arm versus no-arm doorbell offsets, CQ registration races, IRQ synchronization paths, debugfs lifecycle, and RFS builds.
