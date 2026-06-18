# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/clock.h

Purpose: Declares mlx5 clock, timer, and PPS state plus timestamp conversion helpers and PTP lifecycle APIs.

Important APIs and types: `struct mlx5_pps` stores pin capabilities, scheduled output starts, enable state, minimum NPPS parameters, and armed pins. `struct mlx5_timer` stores cyclecounter/timecounter conversion data and overflow period. `struct mlx5_clock` contains a seqlock, PTP handle/info, PPS info, timer, and shared-clock flag. Public APIs include init/cleanup/load/unload, PTP index lookup, `mlx5_timecounter_cyc2time()`, `mlx5_real_time_cyc2time()`, and RQ/SQ timestamp translator selectors.

State and dependencies: The header depends on `CONFIG_PTP_1588_CLOCK`; without it, APIs are stubs. Real-time support is inferred from device timestamp format capabilities for RQ/SQ and `REAL_TIME_TO_NS` maps firmware high/low fields to nanoseconds.

Risks and test signals: Consumers must choose the correct translator for real-time versus free-running CQE timestamps. Build tests need PTP enabled/disabled, and runtime tests should verify seqlock conversion stability and `ptp_clock_index()` behavior when registration fails.
