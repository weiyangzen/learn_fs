# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-timestamp.c

Purpose: this file converts the Rockchip controller's 32-bit hardware timestamp counter into skb hardware timestamps using Linux cyclecounter/timecounter infrastructure and a delayed wrap-prevention worker.

Important APIs and functions: `rkcanfd_timestamp_init()` programs the timestamp prescaler, configures `struct cyclecounter`, computes safe delayed-work cadence, and initializes the worker. `rkcanfd_timestamp_start()` initializes `struct timecounter` from real time and schedules work. `rkcanfd_timestamp_stop()` and `_stop_sync()` cancel the delayed worker. `rkcanfd_skb_set_timestamp()` converts a raw controller timestamp into `skb_shared_hwtstamps`.

Control flow: start-up chooses the larger of nominal and data bitrate, divides the CAN clock down to at least twice that bitrate subject to the register field maximum, enables the timestamp counter, computes mult/shift with `clocks_calc_mult_shift()`, and schedules periodic reads before the 32-bit counter can wrap unnoticed. RX, TX echo, and error paths pass raw timestamps to `rkcanfd_skb_set_timestamp()`, which uses `timecounter_cyc2time()` and writes `hwtstamp`.

State and persistence: timestamp state lives in `priv->cc`, `priv->tc`, `priv->timestamp`, and `priv->work_delay_jiffies`. It resets on chip start and stops on interface shutdown. It is not persisted. The timecounter base is real time at each start, so timestamps are meaningful for the running interface session.

Dependencies and integration points: depends on `linux/clocksource.h`, delayed work, the controller timestamp register, CAN bit timing already calculated by the CAN core, and ethtool timestamp reporting from `rockchip_canfd-ethtool.c`.

Risks and test signals: `rkcanfd_timestamp_init()` reads data bit timing even when CAN FD is disabled; callers must ensure fields are initialized enough for the max operation. Work delay calculation must remain conservative for high clock rates; missed delayed work can corrupt timestamp extension across wraps. Tests should verify hardware timestamps are monotonic across RX/TX/error skbs, wrap handling at high clock rates, stop vs stop_sync race behavior during close/remove, and ethtool timestamp reporting.
