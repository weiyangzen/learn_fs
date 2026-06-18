# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/Makefile

Purpose: this Makefile builds the Rockchip CAN FD driver as a composite object named `rockchip_canfd.o` when `CONFIG_CAN_ROCKCHIP_CANFD` is enabled.

Important build units: `rockchip_canfd-objs` includes `rockchip_canfd-core.o`, `rockchip_canfd-ethtool.o`, `rockchip_canfd-rx.o`, `rockchip_canfd-timestamp.o`, and `rockchip_canfd-tx.o`. The core file owns platform probe/remove, runtime PM, bit timing, interrupts, and netdev operations. The other files provide exported internal helpers declared in `rockchip_canfd.h`.

Control flow and integration: there is no runtime flow. The object list defines link-time integration, so cross-file functions such as `rkcanfd_handle_rx_int()`, `rkcanfd_start_xmit()`, `rkcanfd_timestamp_*()`, and `rkcanfd_ethtool_init()` resolve inside the single module.

State and persistence: only build state is affected. No generated files or runtime state are created by this Makefile.

Risks and test signals: missing any listed object would break link-time symbols or silently drop functionality such as hardware timestamps or ethtool stats. Build tests should compile the driver as a module and built-in, with `W=1` or equivalent to catch missing prototypes and unused symbol drift when implementation files change.
