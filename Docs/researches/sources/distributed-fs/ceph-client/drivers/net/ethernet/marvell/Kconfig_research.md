# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/Kconfig

## Purpose
This Kconfig file defines the Marvell Ethernet vendor menu and configuration symbols for multiple Marvell wired Ethernet families: MV643XX/Orion, MVMDIO, MVNETA and its buffer manager, MVPP2 and PTP support, PXA168, SKGE, SKY2, and sourced subtrees for Octeon and Prestera drivers.

## Important Symbols
`NET_VENDOR_MARVELL` gates the menu and defaults to `y` when broad platform dependencies are met. `MV643XX_ETH` depends on older PPC/Orion platforms or compile testing plus `INET`, and selects `PHYLIB` and `MVMDIO`. `MVMDIO` depends on `HAS_IOMEM` and selects `PHYLIB`. `MVNETA` depends on `ARCH_MVEBU || COMPILE_TEST` and selects `MVMDIO`, `PHYLINK`, `PAGE_POOL`, and `PAGE_POOL_STATS`. `MVNETA_BM_ENABLE` and hidden `MVNETA_BM` coordinate buffer-manager support with 32-bit-only constraints and module/built-in compatibility. `MVPP2` selects `MVMDIO`, `PHYLINK`, and `PAGE_POOL`; `MVPP2_PTP` gates PTP support on compatible built-in/module combinations. `PXA168_ETH`, `SKGE`, `SKGE_DEBUG`, `SKGE_GENESIS`, `SKY2`, and `SKY2_DEBUG` configure additional Marvell PCI/SoC adapters.

## Control Flow
Kconfig first evaluates the vendor menu. If enabled, each driver symbol becomes visible according to architecture, bus, debugfs, PTP, and compile-test conditions. Several symbols select shared infrastructure instead of requiring the user to pick it manually. The file then sources Kconfig files for `octeontx2`, `octeon_ep`, `octeon_ep_vf`, and `prestera`, extending the same vendor menu with subtree-specific options.

## State And Persistence
Selections persist in `.config` and determine which Marvell objects and subdirectories the sibling Makefile builds. Hidden `MVNETA_BM` encodes policy so buffer-manager support is built in a form compatible with `MVNETA`.

## Dependencies And Integration Points
This file integrates with the parent Ethernet Kconfig, Marvell Makefile, phylib/phylink, page-pool infrastructure, debugfs, PTP clock infrastructure, architecture symbols, and sourced child Kconfig files. It is a dependency hub: incorrect selects or depends clauses can break randconfig builds in unrelated Marvell drivers.

## Risks
The mixed use of `select` and architecture dependencies can hide missing lower-level dependencies in randconfig. `MVPP2_PTP` has a nuanced built-in/module expression that must stay aligned with both `PTP_1588_CLOCK` and `MVPP2` link modes. `MVNETA_BM` must not become modular when `MVNETA=y`; the hidden symbol enforces this and is easy to regress. Sourced subtree paths must match directory structure or Kconfig parsing fails.

## Test Signals
Use `allmodconfig`, `allyesconfig`, `randconfig`, and platform-specific configs for MVEBU, Orion, PPC32, PCI-only, and COMPILE_TEST. Verify that selected symbols produce expected objects, PTP combinations link correctly, debug options require DEBUG_FS, and sourced Octeon/Prestera menus remain reachable.
