# sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/Kconfig

## Purpose
This Kconfig file introduces the SpacemiT Ethernet vendor menu and the K1 EMAC driver option.

## Important APIs, Types, And Functions
- `NET_VENDOR_SPACEMIT` is a vendor gate, default `y`, visible on `ARCH_SPACEMIT` or `COMPILE_TEST`.
- `SPACEMIT_K1_EMAC` is a tristate for the SpacemiT K1 Ethernet MAC driver, defaulting to module on `ARCH_SPACEMIT`.
- The driver depends on `MFD_SYSCON` and `OF`, and selects `PHYLIB`.

## Control Flow
When `NET_VENDOR_SPACEMIT` is enabled, the nested `SPACEMIT_K1_EMAC` option becomes available. Selecting it causes the Makefile in the same directory to build `k1_emac.o`.

## State And Persistence
The file affects kernel configuration only. It persists no runtime state.

## Dependencies And Integration Points
It integrates the K1 EMAC into the kernel networking Kconfig hierarchy and ensures required OF/syscon/PHY library dependencies are present before compilation.

## Risks
Dependency coverage is narrow: the driver also uses clocks, reset, runtime PM, timers, DMA mapping, NAPI, and ethtool APIs that are normally available in this build context but are not explicit Kconfig dependencies here. `COMPILE_TEST` helps expose missing include/config dependencies.

## Test Signals
Expected signals are successful `oldconfig/menuconfig` visibility, `CONFIG_SPACEMIT_K1_EMAC=m/y` producing `k1_emac.o`, and compile-test builds outside SpacemiT architectures.
