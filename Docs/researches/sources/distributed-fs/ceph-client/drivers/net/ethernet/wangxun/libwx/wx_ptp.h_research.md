# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ptp.h

## Purpose
`wx_ptp.h` declares the libwx PTP and hardware timestamp API implemented by `wx_ptp.c`. It lets datapath, ethtool, interrupt, suspend/resume, and device lifecycle code interact with PHC support without depending on implementation internals.

## Important APIs, types, and functions
The header declares PPS interrupt handling, cyclecounter reset, full PTP reset/init/suspend/stop, RX hardware timestamp attachment, and netdev hwtstamp get/set operations. It uses `struct wx`, `struct sk_buff`, `struct net_device`, `struct kernel_hwtstamp_config`, and `struct netlink_ext_ack`.

## Control flow and behavior
There is no executable flow. The declarations imply lifecycle order: initialize PTP after device state is ready, reset the cyclecounter on init/reset/link-speed change, call RX timestamp helper from packet receive, call PPS event helper from interrupt handling, suspend or stop PTP during power/device teardown, and expose hwtstamp get/set through netdev timestamp operations.

## State and persistence
The header owns no state. The implementation stores PHC, timestamp config, cyclecounter/timecounter, PPS, and TX/RX timestamp state in `struct wx`.

## Dependencies and integration points
Consumers need Linux networking and timestamping types. `wx_lib.c` calls `wx_ptp_rx_hwtstamp()` and schedules TX timestamp work through the registered PTP clock; ethtool code reports capabilities based on `wx->ptp_clock`; hardware code supplies PPS firmware programming.

## Risks and edge cases
Consumers must guard calls with correct device state. For example, hwtstamp get/set expects the netdev to be running, RX timestamp helper is meaningful only when descriptor timestamp bits are present, and stop/suspend must run before freeing resources that PTP work might touch. Prototype drift with kernel hwtstamp APIs would break netdev operation wiring.

## Test signals
Build tests should cover all includers. Runtime tests should validate PTP init/stop across open/close, hwtstamp configuration while up and rejection while down, RX timestamp delivery from the datapath, and PPS event handling from interrupt paths on capable hardware.
