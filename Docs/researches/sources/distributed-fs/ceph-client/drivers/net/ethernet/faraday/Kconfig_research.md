## sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/Kconfig

## Purpose
Defines Kconfig menu and driver symbols for Faraday Ethernet controllers, including 10/100 FTMAC100 and gigabit FTGMAC100.

## Important APIs, Types, and Functions
Symbols are `NET_VENDOR_FARADAY`, `FTMAC100`, and `FTGMAC100`. The vendor menu defaults to yes but depends on `ARM || COMPILE_TEST`. `FTMAC100` selects `MII` and is blocked on `64BIT` unless `BROKEN`; `FTGMAC100` selects `PHYLIB`, `FIXED_PHY`, `CRC32`, and `MDIO_ASPEED` on `MACH_ASPEED_G6`, with the same ARM/64-bit constraints.

## Control Flow and State
No runtime control flow. Build-time state controls menu visibility, module/built-in selection, and dependency closure for the Faraday drivers.

## Dependencies and Integration Points
Integrates with the local Makefile entries for `ftmac100.o` and `ftgmac100.o`, and with PHY/fixed-link/Aspeed MDIO support required by the implementation.

## Risks and Test Signals
Risks include overrestrictive `!64BIT || BROKEN` hiding valid compile coverage, missing `NET_NCSI` selection despite optional NCSI runtime support, and dependency drift when driver code adds APIs. Test with disabled/vendor-only/module/built-in configs, ARM and COMPILE_TEST builds, Aspeed G6 builds, and configs with/without NCSI.
