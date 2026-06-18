# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/Kconfig

Purpose: Kconfig entry for the Atheros AR5523 USB wireless driver.

Important APIs/types/functions: Defines `AR5523` as a tristate option labeled "Atheros AR5523 wireless driver support". It depends on `MAC80211` and `USB`, selects `ATH_COMMON`, and selects `FW_LOADER` for runtime firmware loading.

Control flow: When enabled as built-in or module, the adjacent Makefile builds `ar5523.o`. The selected firmware loader is required because pre-firmware devices receive `ar5523.bin` over USB before they re-enumerate as operational devices.

State/persistence: The selection persists only in kernel configuration and build outputs. Runtime state is in the driver, not Kconfig.

Dependencies/integration: Integrates the AR5523 driver with mac80211, USB core, shared Atheros helpers, and firmware loading infrastructure.

Risks: Without firmware loader support or the external firmware blob, supported pre-firmware USB IDs cannot transition to the usable post-firmware IDs. Incorrect dependency weakening would allow impossible builds without USB or mac80211.

Test signals: Configuring `CONFIG_AR5523=m` should build the module and select `ATH_COMMON` and `FW_LOADER`. Runtime probe logs should request `ar5523.bin` for pre-firmware devices.
