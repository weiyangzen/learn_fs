# sources/distributed-fs/ceph-client/drivers/net/can/slcan/Makefile

Purpose: build rules for the serial line CAN driver.

Important APIs/types/functions: builds `slcan.o` when `CONFIG_CAN_SLCAN` is enabled, with object components `slcan-core.o` and `slcan-ethtool.o`.

Control flow: no runtime flow. Kbuild links the core tty line discipline/netdev code with ethtool private flag support.

State and persistence: no runtime state. Build-time only.

Dependencies/integration: depends on the parent Kconfig selecting `CONFIG_CAN_SLCAN`; the object split requires symbols in `slcan.h` to connect core and ethtool code.

Risks: omitting either object breaks ethtool ops or the line discipline. Since `slcan-objs` starts empty then appends, later edits must preserve both entries.

Test signals: `CONFIG_CAN_SLCAN=m` should produce one `slcan.ko`; modpost should resolve `slcan_ethtool_ops`, `slcan_err_rst_on_open()`, and `slcan_enable_err_rst_on_open()`.
