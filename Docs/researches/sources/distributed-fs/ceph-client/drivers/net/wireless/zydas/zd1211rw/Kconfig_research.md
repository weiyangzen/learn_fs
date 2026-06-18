# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/Kconfig

Purpose: this Kconfig file defines the build options for the ZyDAS ZD1211/ZD1211B USB wireless driver and its optional debug logging. It controls whether the driver is disabled, built in, or built as a module, and whether extra debug messages are compiled in.

Important APIs, types, and functions: `config ZD1211RW` is a tristate prompt for `ZyDAS ZD1211/ZD1211B USB-wireless support`; it depends on `USB && MAC80211` and selects `FW_LOADER`, reflecting that the device is USB-attached, uses mac80211, and requires firmware loading support. `config ZD1211RW_DEBUG` is a boolean prompt depending on `ZD1211RW`; enabling it causes the Makefile to add `-DDEBUG`.

Control flow: Kconfig only offers `ZD1211RW` when USB and mac80211 are enabled. Selecting it causes kbuild to build the driver through the parent and local Makefiles. `FW_LOADER` is selected automatically. If `ZD1211RW_DEBUG=y`, build flags enable additional debug logging in the driver source.

State and persistence: the choices persist in `.config` as `CONFIG_ZD1211RW` and `CONFIG_ZD1211RW_DEBUG`. Runtime state belongs to the driver objects and firmware loader, not to this file.

Dependencies and integration points: it integrates the driver with the USB subsystem, mac80211 wireless stack, and firmware loader. The help text documents external firmware as a runtime requirement. The debug symbol is consumed by `zd1211rw/Makefile`.

Risks: missing `USB` or `MAC80211` dependencies would allow invalid builds; missing `FW_LOADER` selection would break runtime firmware requests. The firmware URL is informational and may become stale, but the key technical point is that firmware must be installed. Debug builds can increase kernel log volume and expose timing-sensitive behavior.

Test signals: Kconfig should hide the driver when USB or MAC80211 is unavailable, select FW_LOADER when enabled, allow `m` module builds, and define `CONFIG_ZD1211RW_DEBUG` only when the driver itself is enabled.
