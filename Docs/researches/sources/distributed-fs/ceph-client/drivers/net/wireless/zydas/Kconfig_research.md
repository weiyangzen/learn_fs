# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/Kconfig

Purpose: this Kconfig file introduces the ZyDAS wireless vendor menu and includes the concrete ZD1211/ZD1211B USB wireless driver configuration when the vendor menu is enabled. It is a build-configuration gate rather than runtime code.

Important APIs, types, and functions: `config WLAN_VENDOR_ZYDAS` is a boolean menu symbol titled `ZyDAS devices` and defaults to `y`. The `if WLAN_VENDOR_ZYDAS` block conditionally sources `drivers/net/wireless/zydas/zd1211rw/Kconfig`, making child driver prompts visible only when the vendor category is enabled.

Control flow: during Kconfig evaluation, users who leave or set `WLAN_VENDOR_ZYDAS=y` see the ZD1211RW options. Setting it to `n` hides the subtree prompts. The help text explicitly notes that disabling the vendor symbol skips questions but does not directly change kernel code unless child symbols are thereby unavailable.

State and persistence: selected Kconfig values persist in the kernel `.config`. This file does not create runtime state. Its default `y` preserves visibility of the vendor subtree in normal menuconfig flows.

Dependencies and integration points: it is included from the broader wireless vendor Kconfig hierarchy. It delegates the actual driver dependency checks to `zydas/zd1211rw/Kconfig`.

Risks: incorrect source path or gating would hide the ZD1211RW driver. Changing the default from `y` could surprise configurations that rely on vendor menus being visible by default. Since this symbol is a menu gate, treating it as a hard driver dependency can be misleading.

Test signals: Kconfig/menuconfig should show `ZyDAS devices` under wireless vendors, show the ZD1211RW prompt when enabled, hide it when disabled, and produce no build objects solely from `WLAN_VENDOR_ZYDAS` without `CONFIG_ZD1211RW`.
