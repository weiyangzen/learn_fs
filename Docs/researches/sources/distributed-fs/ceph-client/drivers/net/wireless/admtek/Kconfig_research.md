# sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/Kconfig

Purpose: Defines ADMtek wireless vendor selection and the ADM8211 PCI 802.11b driver configuration option.

Important APIs and definitions: `config WLAN_VENDOR_ADMTEK` is a bool vendor gate, default y. Under it, `config ADM8211` is a tristate depending on `MAC80211 && PCI`, selecting `CRC32` and `EEPROM_93CX6`. Help text lists supported ADM8211A/B/C cards and notes some model-number chip substitutions.

Control flow: The ADM8211 option is visible only when the vendor gate is enabled. Selecting ADM8211 pulls required CRC and EEPROM helpers and allows built-in or module builds.

State and persistence: Build-time configuration only.

Dependencies and integration points: Controls `drivers/net/wireless/admtek/Makefile`, which builds `adm8211.o`. Runtime driver integrates with PCI and mac80211.

Risks: Missing dependencies would cause link/build failures; inaccurate help text could lead users to select the wrong driver for rebranded cards. Vendor gate set to `n` hides the driver entirely.

Test signals: Kconfig visibility with `MAC80211`/`PCI` on and off, module and built-in builds, and dependency auto-selection for `CRC32` and `EEPROM_93CX6`.
