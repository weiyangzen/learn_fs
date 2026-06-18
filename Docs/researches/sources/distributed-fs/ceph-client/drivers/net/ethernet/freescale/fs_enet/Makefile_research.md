# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/Makefile

## Purpose
Builds the `fs_enet` composite driver and optional FEC/FCC/SCC MAC and MDIO objects according to Kconfig symbols.

## Important APIs, Types, and Functions
Defines `obj-$(CONFIG_FS_ENET) += fs_enet.o`, conditionally adds `mac-scc.o`, `mac-fec.o`, and `mac-fcc.o` to `fs_enet-m`, builds `mii-fec.o` and `mii-bitbang.o` as separate MDIO drivers, and sets `fs_enet-objs := fs_enet-main.o $(fs_enet-m)`.

## Control Flow and State
There is no runtime control flow. The link composition determines which `fs_ops` implementations are available to `fs_enet-main.c` and which MDIO platform drivers are emitted.

## Dependencies and Integration Points
Directly reflects `Kconfig` symbols and the `extern const struct fs_ops` declarations in `fs_enet.h`. Separate MDIO objects register their own platform drivers.

## Risks and Test Signals
Risks include missing backend objects for enabled OF match entries or duplicate symbol/link problems across configurations. Test signals are build checks for each symbol combination and verifying `fs_enet.o` contains only supported backend ops for the chosen platform.
