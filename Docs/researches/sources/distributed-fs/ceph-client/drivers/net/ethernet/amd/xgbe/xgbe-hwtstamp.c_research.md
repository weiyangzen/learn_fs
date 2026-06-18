# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-hwtstamp.c

## Purpose
`xgbe-hwtstamp.c` implements hardware timestamp register programming, TX/RX timestamp extraction, user timestamp filter configuration, and PTP clock initialization for the AMD XGBE MAC. It bridges Linux hwtstamp/PTP configuration to MAC timestamp control registers.

## Important APIs, Types, And Functions
- `xgbe_update_tstamp_time`, `xgbe_update_tstamp_addend`, and `xgbe_set_tstamp_time` write MAC timestamp update/init registers and poll completion bits.
- `xgbe_get_tstamp_time`, `xgbe_get_tx_tstamp`, and `xgbe_get_rx_tstamp` convert MAC timestamp registers or descriptor context fields into nanoseconds.
- `xgbe_config_tstamp` ORs timestamp control bits into `MAC_TSCR`.
- `xgbe_tx_tstamp` completes deferred TX timestamp delivery for `pdata->tx_tstamp_skb`.
- `xgbe_get_hwtstamp_settings` and `xgbe_set_hwtstamp_settings` implement the netdev hwtstamp get/set path.
- `xgbe_prep_tx_tstamp` marks outbound PTP packets for hardware timestamping and enforces one in-flight TX timestamp SKB.
- `xgbe_init_ptp` programs timestamp increments/addend and initializes system time from `ktime_get_real_ts64`.

## Control Flow
PTP registration is done from `xgbe-main.c`; timestamp hardware setup occurs when the device initializes or timestamping is requested. User hwtstamp settings are validated through the TX type and RX filter switches, translated into `MAC_TSCR` bits, written to hardware, and cached in `pdata->tstamp_config`. TX timestamping is prepared during packet transmit and completed asynchronously through `tx_tstamp_work`. RX timestamps are consumed from receive context descriptors when valid.

## State And Persistence
The file maintains `pdata->tstamp_config`, `pdata->tstamp_addend`, `pdata->tx_tstamp_skb`, and `pdata->tx_tstamp`. All are runtime state. `tstamp_lock` protects timestamp adjustment and TX timestamp SKB ownership. Hardware state lives in MAC timestamp registers and is reinitialized by `xgbe_init_ptp`.

## Dependencies And Integration Points
This code depends on MAC register macros from `xgbe-common.h`, `struct xgbe_prv_data` timestamp fields from `xgbe.h`, Linux hwtstamp/PTP APIs, SKB timestamp helpers, and version data flags such as `tx_tstamp_workaround` and `tstamp_ptp_clock_freq`. It integrates with `xgbe-ptp.c` for PHC operations and `xgbe-ethtool.c` for timestamp capability reporting.

## Risks
The polling loops must not silently miss stuck hardware; most paths log timeout errors but continue. `xgbe_update_tstamp_time` checks `count < 0` after a decrementing loop even though the loop exits at zero, so the timeout diagnostic condition is weaker than the addend/init paths. Only one TX timestamp SKB is tracked, so concurrent timestamp requests can be dropped by clearing the packet PTP attribute. Correct addend calculation depends on `ptpclk_rate` being initialized by platform/PCI probing.

## Test Signals
Test with `hwstamp_ctl`, `phc2sys`, `ptp4l`, and `ethtool -T`. Exercise TX and RX PTP filters, interface restart, link-speed-specific timestamp initialization, and error logs for timestamp init/addend timeouts. Packet capture or application-level PTP tests should confirm monotonic PHC behavior and valid TX/RX hardware timestamps.
