# sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan-ethtool.c

Purpose: ethtool integration for SLCAN private flags and timestamp info.

Important APIs/types/functions: defines private flag string `err-rst-on-open`, maps it to bit 0, implements `get_strings`, `get_priv_flags`, `set_priv_flags`, and `get_sset_count`, and exports `slcan_ethtool_ops` with generic timestamp info.

Control flow: ethtool queries copy the private flag name for `ETH_SS_PRIV_FLAGS`; get/set forwards to `slcan_err_rst_on_open()` and `slcan_enable_err_rst_on_open()` implemented in core. Set converts the bit to a boolean and returns core validation, including `-EBUSY` while the device is running.

State and persistence: no local state. It reads and writes `sl->cmd_flags` through core helpers. The setting lasts only for the netdev/ldisc lifetime.

Dependencies/integration: depends on `slcan.h`, netdevice, ethtool, and SocketCAN core includes. It is linked into `slcan.o` by the Makefile.

Risks: private flag bit layout must match the string array. Unknown stringsets fall through without action for `get_strings`; unsupported count returns `-EOPNOTSUPP`.

Test signals: `ethtool --show-priv-flags slcanX` exposes one flag; toggling it while down changes open behavior; toggling while up returns busy; `ethtool -T` returns generic software timestamp capabilities.
