# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/events.h

Purpose: Declares mlx5 event utility types for port-module events and the driver notifier chain.

Important APIs and types: Defines masks for module status/error fields, enumerates module plugged/unplugged/error/disabled statuses and detailed module error causes, and defines `struct mlx5_pme_stats` counters indexed by those enums. Exports `mlx5_get_pme_stats()` and `mlx5_notifier_call_chain()`.

State and dependencies: The header depends on `mlx5_core.h` and is consumed by LAG/MPESW and other event producers to notify device subsystems.

Risks and test signals: Counter arrays are sized by enum sentinels, so new statuses/errors must update bounds consistently. Tests should check notifier fanout, PME counter indexing, and masks used when decoding raw module events.
