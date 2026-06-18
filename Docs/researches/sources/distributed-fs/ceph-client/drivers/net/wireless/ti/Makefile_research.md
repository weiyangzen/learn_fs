# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/Makefile

Purpose: Routes enabled TI wireless driver families into their subdirectories.

Important APIs, types, and functions: Uses `obj-$(CONFIG_WLCORE) += wlcore/`, `obj-$(CONFIG_WL12XX) += wl12xx/`, `obj-$(CONFIG_WL1251) += wl1251/`, and `obj-$(CONFIG_WL18XX) += wl18xx/`.

Control flow: Kbuild descends only into subdirectories whose config symbol is enabled as built-in or module.

State and persistence: Build-time only.

Dependencies and integration points: Depends on Kconfig symbols defined by included TI Kconfig files.

Risks: Missing or mismatched config symbol names would silently omit driver directories. No special ordering beyond listing.

Test signals: Kernel builds for each TI driver as built-in/module and clean omission when disabled.
