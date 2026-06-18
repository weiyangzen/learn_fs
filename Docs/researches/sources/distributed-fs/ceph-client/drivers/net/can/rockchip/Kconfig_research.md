# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/Kconfig

Purpose: this Kconfig fragment declares the Rockchip CAN FD controller option, `CONFIG_CAN_ROCKCHIP_CANFD`. It makes the driver available as built-in or module code and places it under the CAN driver configuration hierarchy.

Important symbols and dependencies: `CAN_ROCKCHIP_CANFD` is a tristate labeled "Rockchip CAN-FD controller". It depends on device tree support (`OF`) and either `ARCH_ROCKCHIP` or `COMPILE_TEST`. It selects `CAN_RX_OFFLOAD`, matching the implementation's use of `struct can_rx_offload`, timestamp-ordered RX queuing, and echo skb timestamp handling.

Control flow and integration: the file has no runtime control flow. At build-configuration time, selecting the symbol allows `Makefile` to compile the multi-object `rockchip_canfd.o` module from core, ethtool, RX, timestamp, and TX source files. The help text identifies Rockchip SoC CAN FD controllers as the hardware target.

State and persistence: Kconfig state persists only in the kernel configuration. It indirectly controls whether OF matching for `rockchip,rk3568v2-canfd` and `rockchip,rk3568v3-canfd` can register a runtime platform driver.

Risks and test signals: because the implementation currently disables CAN FD mode when `RKCANFD_QUIRK_CANFD_BROKEN` is present, the Kconfig help's CAN-FD wording can overstate usable functionality on affected RK3568 revisions. Configuration tests should verify `CAN_RX_OFFLOAD` is selected, compilation works under `COMPILE_TEST`, and module/built-in builds include all listed object files.
