# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/soc.c

Purpose: Platform-driver frontend for MT7622 integrated WMAC using the mt7615 MMIO core.

Important APIs and functions: `mt7622_wmac_init()` looks up the `mediatek,infracfg` syscon regmap for MT7622 devices. `mt7622_wmac_probe()` obtains platform IRQ and MMIO resource, then calls `mt7615_mmio_probe()` with the MT7615E register map. `mt7622_wmac_remove()` unregisters the common device. `mt7622_wmac_driver` binds the `mediatek,mt7622-wmac` compatible.

Control flow: Platform probe maps SoC resources and delegates almost all device setup to the common MMIO path. During common registration, `mt7622_wmac_init()` is called to acquire infracfg support for HIF wake/interrupt integration.

State and persistence: Stores `dev->infracfg` regmap for MT7622-specific wake/interrupt control. No persistent storage.

Dependencies: Linux platform device, device tree, syscon/regmap, common `mt7615_mmio_probe()`, and firmware declarations for MT7622 N9/ROM patch.

Risks: Device tree must provide a valid IRQ, MMIO resource, and `mediatek,infracfg` phandle. The SoC uses the mt7615e map, so incompatible register layout would break shared MMIO code. Remove assumes platform drvdata is set by common mt76 probe path.

Test signals: Device-tree match/probe, successful infracfg lookup, firmware load, HIF interrupt triggering on MT7622, and platform remove cleanup.
