# sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/Makefile

Purpose: Builds the ADMtek ADM8211 wireless driver object when its Kconfig symbol is enabled.

Important APIs and definitions: `obj-$(CONFIG_ADM8211) += adm8211.o`.

Control flow: Kbuild compiles and links `adm8211.c` into the kernel or module when `CONFIG_ADM8211=y/m`.

State and persistence: Build-time only.

Dependencies and integration points: Driven by `admtek/Kconfig` and reached via the top-level wireless Makefile.

Risks: Minimal; filename or symbol drift would silently break builds for this driver.

Test signals: `CONFIG_ADM8211=m` produces `adm8211.ko`; `CONFIG_ADM8211=y` links built-in object.
