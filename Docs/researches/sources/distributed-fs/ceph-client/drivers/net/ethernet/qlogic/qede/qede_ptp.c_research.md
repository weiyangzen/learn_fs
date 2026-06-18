# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ptp.c

## Purpose
This file implements qede hardware timestamping and PHC support. It wraps the lower-layer `qed_eth_ptp_ops` in Linux PTP clock, hwtstamp ioctl, cyclecounter/timecounter, Tx timestamp work, and Rx timestamp attachment APIs used by the fastpath.

## Important APIs, Types, and Functions
The private `struct qede_ptp` stores `qed_eth_ptp_ops`, `ptp_clock_info`, `cyclecounter`, `timecounter`, registered `ptp_clock`, Tx timestamp work, one pending Tx skb, timestamp filter settings, and a spinlock protecting PTP hardware operations and timecounter state.

PHC callbacks are `qede_ptp_adjfine()`, `qede_ptp_adjtime()`, `qede_ptp_gettime()`, `qede_ptp_settime()`, and `qede_ptp_ancillary_feature_enable()`. Netdev timestamp APIs are `qede_hwtstamp_set()`, `qede_hwtstamp_get()`, and `qede_ptp_get_ts_info()`. Lifecycle/data-path APIs are `qede_ptp_enable()`, `qede_ptp_disable()`, `qede_ptp_tx_ts()`, and `qede_ptp_rx_ts()`.

## Control Flow
PTP enable allocates `struct qede_ptp`, binds it to `edev`, validates `edev->ops->ptp`, enables PTP in hardware, initializes Tx timestamp work, initializes a 64-bit cyclecounter/timecounter seeded with real time, configures any prior filters, fills `ptp_clock_info`, and registers the PHC. PTP disable unregisters the clock, cancels Tx timestamp work, frees any held Tx skb, clears the in-progress bit, disables hardware PTP, frees state, and clears `edev->ptp`.

`qede_hwtstamp_set()` requires the netdev to be running, rejects unsupported Tx modes, records requested Tx/Rx filters, calls `qede_ptp_cfg_filters()`, and returns the normalized Rx filter to the caller. Filter configuration maps Linux `HWTSTAMP_FILTER_*` values to qed firmware filter enums, normalizes narrow sync/delay filters to event filters, updates `QEDE_FLAGS_TX_TIMESTAMPING_EN`, and serializes the hardware call with the PTP spinlock.

Tx timestamping is single-outstanding. `qede_ptp_tx_ts()` is called from `qede_start_xmit()` for `SKBTX_HW_TSTAMP` skbs, sets `SKBTX_IN_PROGRESS`, takes an skb reference, records `jiffies`, and schedules work. `qede_ptp_task()` polls `read_tx_ts()` until a timestamp is available or a two-second timeout expires, then converts cycles through the timecounter, reports the timestamp with `skb_tstamp_tx()`, frees the held skb, and clears the in-progress bit. Rx timestamping is called from Rx CQE processing when the hardware records a timestamp for a timesync packet; it reads hardware Rx cycles, converts to ns, and writes `skb_hwtstamps(skb)->hwtstamp`.

## State and Persistence Behavior
PTP state is in-memory and bound to the PF netdev lifetime. Timestamp configuration (`tx_type`, `rx_filter`, `hw_ts_ioctl_called`) persists across filter reconfiguration while `edev->ptp` exists, but not across full driver removal. `timecounter` state persists across PHC reads and software time adjustments; frequency adjustment is delegated to hardware through `adjfreq`. `edev->ptp_skip_txts` records skipped or timed-out Tx timestamp requests and is reported through qede statistics.

## Dependencies and Integration Points
The file depends on Linux PHC/PTP, `net_tstamp`, `timecounter`, skb timestamp APIs, qede device locking, and `qed_eth_ptp_ops` methods: `enable`, `disable`, `read_cc`, `adjfreq`, `cfg_filters`, `read_tx_ts`, and `read_rx_ts`. It integrates with `qede_main.c` for PF-only enable/disable and netdev hwtstamp operations, and with `qede_fp.c` for Tx and Rx timestamp data-path calls.

## Risks
The PTP spinlock serializes hardware PTP operations and timecounter access, so long-running lower-layer operations under the spinlock would affect softirq latency. Tx timestamp work reschedules immediately while waiting for hardware, which can churn workqueue CPU until timeout. Only one Tx timestamp can be in progress, so concurrent requests are skipped. `qede_ptp_adjfine()` refuses to operate unless the interface is open, but other PHC operations mostly manipulate software timecounter state independent of netdev state. Filter normalization must remain aligned with firmware capabilities or users may see broader timestamping than requested. Disable ordering must cancel work after Tx queues are drained to avoid new scheduling while freeing `ptp`.

## Test Signals
Test with `ethtool -T`, `SIOCSHWTSTAMP`/netlink hwtstamp set/get, PHC reads and adjustments, `phc2sys`/`ptp4l`, Tx timestamp bursts, Rx PTP event traffic for v1/v2 L2 and UDP filters, interface close while timestamps are pending, driver remove/reprobe, and firmware paths where Tx timestamp read times out. Check `ptp_skip_txts`, no lingering `QEDE_FLAGS_PTP_TX_IN_PRORGESS`, valid PHC index, and no use-after-free after PTP disable.
