## sources/distributed-fs/ceph-client/net/ieee802154/Kconfig

Purpose: top-level Kconfig menu for IEEE 802.15.4 low-rate wireless PAN support.

Important APIs/types/functions: `menuconfig IEEE802154` is a tristate symbol controlling the core LR-WPAN subsystem. `IEEE802154_NL802154_EXPERIMENTAL` gates experimental nl802154 low-level security support. `IEEE802154_SOCKET` controls the socket interface and defaults to `y` when the parent is enabled. The file also sources `net/ieee802154/6lowpan/Kconfig`.

Control flow and state: no runtime behavior. The selected symbols determine whether core cfg802154/nl802154/sysfs/pan/header code, socket support, experimental LLSEC netlink blocks, and 6LoWPAN support are compiled.

Dependencies and integration points: integrates with the kernel networking Kconfig tree and child 6LoWPAN configuration. Its options are referenced by Makefiles and C preprocessor conditionals such as `CONFIG_IEEE802154_NL802154_EXPERIMENTAL`.

Risks: enabling experimental netlink changes ABI surface and exposes security table manipulation code guarded by compile-time conditionals. Defaulting socket support to enabled increases build/runtime surface whenever IEEE802154 is selected.

Test signals: config matrix for core built-in/module, socket disabled/enabled, experimental disabled/enabled, and 6LoWPAN dependency behavior.
