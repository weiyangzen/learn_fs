# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/reporter_tx.c

Purpose: Implements the mlx5e devlink health reporter for TX-side failures, including TX SQ ERR CQEs, watchdog timeouts, and unhealthy PTP timestamp queues.

Important APIs and functions: `mlx5e_reporter_tx_create()`/`destroy()` own the `"tx"` reporter. `mlx5e_reporter_tx_err_cqe()`, `mlx5e_reporter_tx_timeout()`, and `mlx5e_reporter_tx_ptpsq_unhealthy()` publish health events. Recovery is handled by `mlx5e_tx_reporter_err_cqe_recover()`, `mlx5e_tx_reporter_timeout_recover()`, and `mlx5e_tx_reporter_ptpsq_unhealthy_recover()`. Diagnose and dump functions enumerate SQs, TIS config, CQ/EQ state, and hardware QPC/send buffer dumps.

Control flow: ERR CQE recovery verifies the SQ is in recovering state, obtains the netdev instance lock without blocking close flows forever, checks hardware SQ state, stops the netdev TXQ, waits for SQ flush, moves the hardware SQ to ready, resets `cc/pc`, clears recovering, activates SQ, and schedules NAPI. Timeout recovery first tries channel EQ recovery, then falls back to `mlx5e_safe_reopen_channels()`. PTP SQ recovery closes and reopens the PTP channel while toggling carrier state around channel deactivation/reactivation.

State and persistence: State is live in SQ bitfields, TXQ stopped state, SQ counters, recovery stats, PTP channel pointers, and `priv->tx_reporter`. `mlx5e_tx_timeout_ctx.status` communicates whether a single SQ or all channels recovered. The SQ state string table is compile-time checked against `MLX5E_NUM_SQ_STATES`.

Dependencies and integration: Uses devlink health reporter ops, mlx5 SQ query/ready helpers, `health.h` dump helpers, `ptp.h`, DCB TC count, profile TIS getters, NAPI triggers, and netdev instance locking. Entry points are called by TX completion, watchdog, and PTP timestamp-health paths.

Risks: Recovery ordering is subtle because netdev locks overlap with channel close/reopen. SQ flush timeouts leave the queue unrecovered. Timeout recovery can escalate from local EQ recovery to full channel reopen. PTP recovery temporarily drops carrier and must restore it correctly. Tests should cover ERR CQE, watchdog timeout fallback, PTP unhealthy recovery, multiple TCs, PTP enabled/disabled, and devlink dump without opened channels.
