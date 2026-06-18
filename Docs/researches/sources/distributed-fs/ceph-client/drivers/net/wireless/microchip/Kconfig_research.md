# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/Kconfig

Purpose: Adds the top-level wireless vendor menu for Microchip devices and includes the WILC1000 driver Kconfig when the vendor category is enabled.

Important APIs and entries: `config WLAN_VENDOR_MICROCHIP` is a boolean menu gate defaulting to `y`. It sources `drivers/net/wireless/microchip/wilc1000/Kconfig` inside the `if WLAN_VENDOR_MICROCHIP` block.

Control flow: Kconfig evaluation presents Microchip wireless options only when the vendor selector is enabled. The selector itself does not build code; it controls visibility of child symbols.

State and persistence: The selected Kconfig values persist in the kernel `.config`. `WLAN_VENDOR_MICROCHIP=n` hides child prompts and prevents selecting WILC symbols through this menu.

Dependencies and integration points: Integrated from the parent wireless driver Kconfig tree. Child WILC1000 options define actual module/object inclusion.

Risks: If the source path is wrong, WILC1000 options disappear. Default `y` improves discoverability but still leaves actual driver tristates dependent on child selections.

Test signals: `menuconfig` visibility, `scripts/kconfig/conf` generation, and builds with vendor enabled/disabled validate this file.
