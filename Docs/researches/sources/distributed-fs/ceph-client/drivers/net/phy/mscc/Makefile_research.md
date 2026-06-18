# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/Makefile

## Purpose
Defines how the Microsemi/Microchip VSC85xx PHY driver objects are built.

## Important APIs, Types, And Functions
This Kbuild fragment builds the composite `mscc.o` when `CONFIG_MICROSEMI_PHY` is enabled. The object always includes `mscc_main.o` and `mscc_serdes.o`, conditionally adds `mscc_macsec.o` for `CONFIG_MACSEC`, and conditionally adds `mscc_ptp.o` for `CONFIG_NETWORK_PHY_TIMESTAMPING`.

## Control Flow
Build-time control flow is Kconfig-driven. The base PHY option selects core and SerDes code; MACsec and PTP are compiled into the same composite object only when enabled.

## State And Persistence
No runtime state. The persistent effect is selected object composition.

## Dependencies And Integration Points
Integrates with Linux Kbuild and feature guards in `mscc.h` and related implementation files.

## Risks
The object list must stay aligned with preprocessor guards. Wrong combinations surface as compile or link failures.

## Test Signals
Build `CONFIG_MICROSEMI_PHY=y/m` with MACsec and timestamping disabled, each enabled alone, and both enabled together.
