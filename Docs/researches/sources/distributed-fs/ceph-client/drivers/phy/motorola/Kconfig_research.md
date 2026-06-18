# sources/distributed-fs/ceph-client/drivers/phy/motorola/Kconfig

Purpose: This Kconfig fragment exposes the Motorola PHY drivers used by older Motorola phones and tablets. It defines build-time configuration for the CPCAP PMIC USB PHY and the Mapphone MDM6600 modem USB PHY.

Important APIs/types/functions: The two symbols are `PHY_CPCAP_USB` and `PHY_MAPPHONE_MDM6600`, both tristate. `PHY_CPCAP_USB` selects `GENERIC_PHY` and `USB_PHY`, depends on `USB_SUPPORT`, `IIO`, and either enabled or absent `USB_MUSB_HDRC`. `PHY_MAPPHONE_MDM6600` selects `GENERIC_PHY` and depends on `OF`, `USB_SUPPORT`, and `GPIOLIB`.

Control flow: Kconfig dependency resolution decides whether these drivers can be built-in, modular, or unavailable. If selected, the corresponding Makefile entries compile `phy-cpcap-usb.o` and `phy-mapphone-mdm6600.o`.

State and persistence: It has no runtime state. It persists build configuration through the kernel `.config`, affecting whether platform devices can bind to Motorola device-tree compatibles.

Dependencies and integration points: It integrates with the PHY, USB/MUSB, IIO, OF, and GPIO subsystems through symbol dependencies. The CPCAP entry explicitly gates against impossible MUSB combinations while still allowing builds when MUSB is disabled.

Risks: Incorrect dependencies can create link failures or drivers that probe without required subsystems. Enabling CPCAP without valid IIO VBUS support or MDM6600 without GPIO descriptors would still compile but fail at runtime probe.

Test signals: `allyesconfig`, `allmodconfig`, and targeted configs for Droid 4 style platforms should show the expected objects. Runtime test signals come from platform-driver binding to `motorola,cpcap-usb-phy`, `motorola,mapphone-cpcap-usb-phy`, and `motorola,mapphone-mdm6600`.
