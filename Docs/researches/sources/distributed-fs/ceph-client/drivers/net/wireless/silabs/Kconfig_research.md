# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/Kconfig

Purpose: Adds the Silicon Labs wireless vendor menu to Kconfig and gates the nested WFx driver options.

Important APIs and types: `config WLAN_VENDOR_SILABS` is a boolean menu selector defaulting to `y`. When enabled, it sources `drivers/net/wireless/silabs/wfx/Kconfig`.

Control flow and integration: Kernel configuration uses this file only at config time. Selecting the vendor does not build code by itself; it exposes the WFx driver prompt beneath the wireless vendor subtree.

State and persistence: The only persistent state is the generated kernel `.config` value for `WLAN_VENDOR_SILABS`.

Dependencies: Integrated from the parent wireless Kconfig hierarchy and delegates the real driver dependencies to `wfx/Kconfig`.

Risks and test signals: Risks are minimal but include hiding WFx options if the vendor menu is disabled. Test with menuconfig/allmodconfig fragments that toggle `WLAN_VENDOR_SILABS` and confirm `CONFIG_WFX` visibility.

Test signals: Source read size: 18 lines, 537 bytes.
