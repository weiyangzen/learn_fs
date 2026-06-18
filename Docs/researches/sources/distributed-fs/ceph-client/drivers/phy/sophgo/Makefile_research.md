# sources/distributed-fs/ceph-client/drivers/phy/sophgo/Makefile

Purpose: builds the Sophgo CV1800 USB2 PHY object when its Kconfig symbol is enabled.

Important APIs, types, and functions: `obj-$(CONFIG_PHY_SOPHGO_CV1800_USB2) += phy-cv1800-usb2.o`.

Control flow: kernel build inclusion only.

State and persistence: none beyond build output.

Dependencies and integration points: consumed by the parent PHY Makefile and matched to the Sophgo platform driver.

Risks: none beyond Kconfig-object mismatch risk.

Test signals: verify module name and object inclusion in `allmodconfig` and Sophgo defconfig builds.
