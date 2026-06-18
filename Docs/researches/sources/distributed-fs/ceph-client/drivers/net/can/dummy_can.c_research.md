# sources/distributed-fs/ceph-client/drivers/net/can/dummy_can.c

Purpose: dummy CAN network driver primarily used to exercise the CAN netlink interface without hardware.

Important APIs and functions: module init allocates one CAN device with one echo slot, registers generous nominal, FD, and XL timing constants, FD/XL TDC constants, PWM constants, supported ctrlmodes, 160 MHz clock, and 20 Mbps bitrate limit. `dummy_can_netdev_open()` prints current timing/control settings, calls `open_candev()`, and starts the queue. `dummy_can_start_xmit()` validates SKBs, stores them in echo slot 0, immediately completes local echo, and updates TX stats.

Control flow and state: the module keeps a single global `dummy_can` pointer. Runtime state is almost entirely `struct can_priv` configured through netlink; no hardware state exists. Close stops queue and calls `close_candev()`. Dependencies include shared CAN dev, bit timing, TDC/PWM, skb echo helpers, ethtool timestamp info, and string choice helpers. Risks are single-instance limitation, no real bus-off/error behavior, immediate echo not modeling hardware latency, and use mainly as a configuration smoke test. Test signals are successful `ip link` FD/XL/TDC/PWM mode changes, debug timing output on open, immediate echo of transmitted frames, and clean module unload.
