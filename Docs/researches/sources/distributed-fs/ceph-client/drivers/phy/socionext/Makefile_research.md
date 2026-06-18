# sources/distributed-fs/ceph-client/drivers/phy/socionext/Makefile

Purpose: maps Socionext UniPhier PHY Kconfig symbols to object files.

Important APIs, types, and functions: `obj-$(CONFIG_PHY_UNIPHIER_USB2)` builds `phy-uniphier-usb2.o`; `CONFIG_PHY_UNIPHIER_USB3` builds both `phy-uniphier-usb3hs.o` and `phy-uniphier-usb3ss.o`; `CONFIG_PHY_UNIPHIER_PCIE` builds `phy-uniphier-pcie.o`; `CONFIG_PHY_UNIPHIER_AHCI` builds `phy-uniphier-ahci.o`.

Control flow: kernel build system only. The single USB3 symbol intentionally produces two cooperating but independent modules/objects for high-speed and super-speed PHY blocks.

State and persistence: no runtime state. Build output state follows Kconfig.

Dependencies and integration points: consumed by `drivers/phy/Makefile` inclusion for Socionext platform PHY support.

Risks: USB3 HS and SS cannot be selected independently, which is correct for typical UniPhier USB3 designs but may overbuild in compile-test contexts.

Test signals: verify object inclusion with `make drivers/phy/socionext/`; module names and DT modaliases should match the platform drivers.
