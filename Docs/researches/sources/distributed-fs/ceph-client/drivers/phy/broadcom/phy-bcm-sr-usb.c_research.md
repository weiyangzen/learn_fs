# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-sr-usb.c

Purpose: Initializes Broadcom Stingray USB high-speed and SuperSpeed PHYs, including combo PHY instances with separate HS and SS generic PHY handles.

Important APIs and types: `enum bcm_usb_phy_version` distinguishes combo versus HS-only hardware. `struct bcm_usb_phy_cfg` stores type, version, MMIO base, PHY pointer, and register offset table. `bcm_usb_phy_create()` builds either two PHYs for combo hardware or one HS PHY.

Control flow: probe maps the register block, reads compatible match data, creates PHY objects, stores the config as driver data, and registers a custom xlate. SS init programs PHY PCTL, clears suspend, starts PLL sequencing, releases PLL reset, waits 30 ms, then polls PLL lock. HS init toggles PLL reset and polls lock. Reset toggles CORERDY for HS PHYs.

State and persistence: Version/type/offset tables are static after probe. Hardware PLL and PHY control bits persist until reset or power management elsewhere.

Dependencies and integration: It depends on generic PHY, OF phandle args, MMIO, and polling helpers. Compatible strings are `brcm,sr-usb-combo-phy` and `brcm,sr-usb-hs-phy`.

Risks and test signals: Combo xlate supports only indexes 0 and 1. PLL lock polling is the main runtime failure. Test HS-only and combo bindings, invalid xlate index, HS reset, SS PLL lock timeout, and USB host enumeration for both PHYs.
