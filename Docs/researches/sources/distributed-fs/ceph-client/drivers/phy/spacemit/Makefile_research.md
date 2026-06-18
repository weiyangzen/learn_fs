# sources/distributed-fs/ceph-client/drivers/phy/spacemit/Makefile

Purpose: builds SpacemiT K1 PHY objects.

Important APIs, types, and functions: `CONFIG_PHY_SPACEMIT_K1_PCIE` maps to `phy-k1-pcie.o`; `CONFIG_PHY_SPACEMIT_K1_USB2` maps to `phy-k1-usb2.o`.

Control flow: kernel build only.

State and persistence: none.

Dependencies and integration points: parent PHY make infrastructure.

Risks: none beyond Kconfig/object drift.

Test signals: object inclusion for K1 defconfig, module names, and modpost symbol checks.
