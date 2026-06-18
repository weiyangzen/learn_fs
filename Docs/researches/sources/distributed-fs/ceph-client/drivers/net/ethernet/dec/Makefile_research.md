# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/Makefile

## Purpose
Routes DEC Ethernet build output into the Tulip-family subdirectory when the Tulip vendor family is enabled.

## Important APIs, Types, and Functions
Contains one build rule: `obj-$(CONFIG_NET_TULIP) += tulip/`.

## Control Flow and State
No runtime flow. Build-time state is controlled by `CONFIG_NET_TULIP`; enabling it descends into `drivers/net/ethernet/dec/tulip/`.

## Dependencies and Integration Points
Integrated with Kbuild. It expects the child `tulip/Makefile` to select individual object files for DE2104X, Tulip, DMFE, Winbond, ULi, and Xircom drivers.

## Risks and Test Signals
Risks are limited to build routing: a wrong symbol or path prevents all DEC Tulip-family drivers from compiling. Test signals are allmodconfig/allyesconfig object generation and that disabling `NET_TULIP` skips the subdirectory.
