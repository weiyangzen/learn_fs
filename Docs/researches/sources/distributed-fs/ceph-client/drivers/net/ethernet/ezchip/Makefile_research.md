## sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/Makefile

## Purpose
Builds the EZchip NPS management Ethernet driver object when its Kconfig symbol is enabled.

## Important APIs, Types, and Functions
Contains the single build rule `obj-$(CONFIG_EZCHIP_NPS_MANAGEMENT_ENET) += nps_enet.o`.

## Control Flow and State
No runtime control flow. Kbuild expands this line into built-in or module output depending on the tristate value of `CONFIG_EZCHIP_NPS_MANAGEMENT_ENET`.

## Dependencies and Integration Points
Depends on `drivers/net/ethernet/ezchip/Kconfig` defining the symbol and on `nps_enet.c`/`nps_enet.h` providing the implementation.

## Risks and Test Signals
Risks are limited to symbol drift or missing object additions if the driver is split. Test by building with the config disabled, built-in, and module-enabled and checking that only `nps_enet.o` is selected.
