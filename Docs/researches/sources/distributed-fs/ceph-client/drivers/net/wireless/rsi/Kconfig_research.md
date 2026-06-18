# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/Kconfig

Purpose: Kconfig menu for Redpine Signals/RSI wireless drivers.

Important symbols: `WLAN_VENDOR_RSI` gates the vendor menu. `RSI_91X` enables the common 91x WLAN driver and selects `BT_HCIRSI` when coexistence is enabled. `RSI_DEBUGFS` adds debugfs support. `RSI_SDIO` and `RSI_USB` enable bus-specific modules. `RSI_COEX` enables WLAN/BT coexistence and has a dependency guard against built-in RSI with modular Bluetooth.

Control flow/integration: kernel configuration uses this file to expose options under the wireless vendor tree. The Makefile consumes these symbols to include core, bus, coexistence, and debugfs objects.

State and persistence: configuration-time only; choices persist in the kernel `.config`.

Dependencies: mac80211 for core, MMC for SDIO, USB for USB, BT for coexistence.

Risks: default `m` for bus support and default `y` for debug/coex influence build coverage. Typos in help text do not affect behavior, but dependency mistakes can create invalid built-in/module link combinations.

Test signals: `allyesconfig`, `allmodconfig`, and combinations with BT built-in/modular/disabled; verify expected modules `rsi_91x`, `rsi_usb`, and `rsi_sdio`.
