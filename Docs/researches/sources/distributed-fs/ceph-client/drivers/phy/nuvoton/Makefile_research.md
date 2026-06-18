# sources/distributed-fs/ceph-client/drivers/phy/nuvoton/Makefile

Purpose: This Makefile adds the Nuvoton MA35 USB2 PHY object when its Kconfig symbol is enabled.

Important APIs/types/functions: It contains one rule: `obj-$(CONFIG_PHY_MA35_USB) += phy-ma35d1-usb2.o`.

Control flow: Kbuild compiles the object as built-in or module based on `CONFIG_PHY_MA35_USB`.

State and persistence: It has no runtime state. It reflects the persistent `.config` selection into build output.

Dependencies and integration points: It integrates the Nuvoton driver into the kernel PHY build hierarchy and must stay synchronized with the Kconfig symbol and source filename.

Risks: A stale object name would make the config option ineffective or fail the build.

Test signals: Targeted builds with `CONFIG_PHY_MA35_USB=m` should produce `phy-ma35d1-usb2.ko`; built-in builds should include the object in the kernel image.
