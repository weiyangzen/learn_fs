# sources/distributed-fs/ceph-client/drivers/phy/rockchip/Makefile

## Purpose
This Makefile maps Rockchip PHY Kconfig symbols to the object files built by Kbuild.

## Important APIs, Types, And Functions
The file uses standard `obj-$(CONFIG_SYMBOL) += object.o` assignments. In this subset, `CONFIG_PHY_ROCKCHIP_DP`, `DPHY_RX0`, `EMMC`, `INNO_CSIDPHY`, `INNO_DSIDPHY`, `INNO_HDMI`, and `INNO_USB2` map directly to their respective `phy-rockchip-*.o` objects.

## Control Flow
There is no runtime control flow. Kbuild expands each `obj-y` or `obj-m` entry according to the resolved configuration. The ordering is mostly folder-local and does not express runtime dependencies.

## State And Persistence
The only persistent effect is build output selection: enabled built-in objects are linked into the kernel image, and modular objects become loadable modules.

## Dependencies And Integration Points
This file integrates the Kconfig choices with Linux Kbuild. It must stay synchronized with filenames and Kconfig symbol names in the same folder.

## Risks And Test Signals
Risks are mechanical: stale object names cause missing builds, and missing rows make Kconfig-visible drivers unbuildable. Test signals are `make drivers/phy/rockchip/` and randconfig builds that enable each symbol.
