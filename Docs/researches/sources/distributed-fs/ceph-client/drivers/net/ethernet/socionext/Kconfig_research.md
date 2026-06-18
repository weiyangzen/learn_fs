<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/Kconfig

## Purpose
`socionext/Kconfig` exposes build configuration for Socionext Ethernet drivers. It creates a vendor menu gate and two driver symbols: UniPhier AVE and SynQuacer NETSEC.

## Important APIs, Types, and Functions
The symbols are `NET_VENDOR_SOCIONEXT`, `SNI_AVE`, and `SNI_NETSEC`. `NET_VENDOR_SOCIONEXT` is a boolean vendor selector defaulting to `y`; choosing `n` hides child questions without directly changing object selection. `SNI_AVE` is a tristate depending on `(ARCH_UNIPHIER || COMPILE_TEST) && OF` and `HAS_IOMEM`, selecting `MFD_SYSCON` and `PHYLIB`. `SNI_NETSEC` is a tristate depending on `(ARCH_SYNQUACER || COMPILE_TEST) && OF`, selecting `PHYLIB`, `PAGE_POOL`, and `MII`.

## Control Flow
Kconfig evaluation first asks the vendor gate. If enabled, the AVE and NETSEC driver prompts become visible when dependency expressions are true. The selected symbols then feed the directory Makefile to compile `sni_ave.o` or `netsec.o` built-in or as modules.

## State and Persistence Behavior
The file stores build-time configuration only in `.config`; it has no runtime state. The choices persist across kernel builds through normal Kconfig configuration storage.

## Dependencies and Integration Points
This file integrates the drivers with the kernel configuration system, architecture gates, OF availability, I/O memory support, phylib, page pool, MII helpers, and the local Makefile. `SNI_NETSEC` also matches capabilities used by `netsec.c`, including page-pool backed RX and MDIO operations.

## Risks
Overly strict dependencies can hide drivers from compile-test coverage; overly loose dependencies can cause build failures on unsupported platforms. Missing `select` lines would surface as unresolved symbols for PHYLIB, PAGE_POOL, or MII functionality. The vendor gate can make a driver appear unavailable even when its direct dependencies are satisfied.

## Test Signals
Run Kconfig/build matrix coverage for `ARCH_UNIPHIER`, `ARCH_SYNQUACER`, and `COMPILE_TEST`; build `SNI_AVE` and `SNI_NETSEC` as built-in and modules; confirm `netsec.ko` naming; and check that disabling `NET_VENDOR_SOCIONEXT` hides prompts without unexpected object builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/Kconfig -->
