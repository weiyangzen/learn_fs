# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/Makefile

## Purpose
Routes Atheros Ethernet Kconfig symbols to their driver object directories or objects.

## Important APIs, Types, and Functions
`obj-$(CONFIG_AG71XX) += ag71xx.o` builds the platform MAC driver. `obj-$(CONFIG_ALX) += alx/` descends into the ALX PCI driver subdirectory. Other ATL driver directories are also conditionally included.

## Control Flow and State
No runtime behavior. This is build-system composition only.

## Dependencies and Integration Points
Depends on Kbuild and the Kconfig symbols declared in the same folder. It integrates the local `alx/Makefile`, which combines `main.o`, `ethtool.o`, and `hw.o` into `alx.o`.

## Risks and Test Signals
Build tests should confirm that enabling only AG71XX does not build ALX and vice versa. Any object rename or missing subdirectory would fail during Kbuild.
