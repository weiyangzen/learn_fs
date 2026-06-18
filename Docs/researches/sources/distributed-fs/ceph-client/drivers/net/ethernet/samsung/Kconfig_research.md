# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/Kconfig

Purpose: declares the Samsung Ethernet vendor menu and the SXGBE Ethernet driver option.

Important symbols: `NET_VENDOR_SAMSUNG` is a boolean vendor gate defaulting to `y`; choosing `n` hides Samsung-specific Ethernet options without directly changing built objects. `SXGBE_ETH` is a tristate for the Samsung 10G/2.5G/1G SXGBE Ethernet driver. It depends on `HAS_IOMEM`, `HAS_DMA`, and `PTP_1588_CLOCK_OPTIONAL`, and selects `PHYLIB` and `CRC32`.

Control flow: Kconfig visibility flows from the vendor gate. When `SXGBE_ETH=y` or `m`, the Makefiles include the SXGBE directory and build `samsung-sxgbe`.

State and persistence: only build configuration state in `.config`; no runtime state.

Dependencies and integration: integrates the SXGBE driver into the kernel networking configuration hierarchy under Samsung Ethernet devices and ensures PHY and CRC helpers are selected.

Risks: optional PTP dependency means timestamp support must still be guarded at runtime. Default vendor `y` increases prompt visibility. Missing platform dependencies are deferred to probe/device tree rather than this Kconfig.

Test signals: `allyesconfig`, `allmodconfig`, and minimal configs with `NET_VENDOR_SAMSUNG=n`; module build name `samsung-sxgbe`; dependency checks for I/O memory, DMA, PHYLIB, CRC32, and optional PTP.
