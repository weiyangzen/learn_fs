# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/Kconfig

## Purpose
This file declares the DPAA1 Ethernet driver configuration symbol.

## Important APIs, Types, and Functions
`FSL_DPAA_ETH` is a tristate menuconfig named "DPAA Ethernet". It depends on `FSL_DPAA` and `FSL_FMAN`, and selects `PHYLINK` and `PCS_LYNX`.

## Control Flow
When enabled, Kbuild enters `freescale/dpaa/Makefile` through the parent Makefile and builds the `fsl_dpa` composite module or built-in object. The help text documents that it supports Freescale QorIQ DPAA chips and requires Buffer Manager, Queue Manager, and Frame Manager support.

## State and Persistence
The only state is the kernel configuration choice.

## Dependencies and Integration Points
The symbol integrates DPAA Ethernet with the FMan MAC/port stack, QMan/BMan platform support, phylink, and Lynx PCS support.

## Risks
Missing dependency coverage can lead to build failures because `dpaa_eth.c` calls many FMan, QMan, BMan, phylink, and PCS APIs. Selecting PHYLINK/PCS here helps prevent incomplete configs.

## Test Signals
Config tests should check built-in and module builds with `FSL_DPAA`, `FSL_FMAN`, phylink, and Lynx PCS enabled; disabled dependencies should hide the option.
