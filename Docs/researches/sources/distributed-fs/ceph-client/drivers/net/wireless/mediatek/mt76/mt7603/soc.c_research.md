# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/soc.c

Purpose: platform/SoC bus glue for the MT7628 integrated WMAC variant of the MT7603 driver.

Important APIs/functions: defines `mt76_wmac_probe()`, `mt76_wmac_remove()`, OF match table for `"mediatek,mt7628-wmac"`, and exported `struct platform_driver mt76_wmac_driver`. Uses `platform_get_irq`, `devm_platform_ioremap_resource`, `mt76_alloc_device`, `mt76_mmio_init`, `devm_request_irq`, `mt7603_register_device`, and `mt7603_unregister_device`.

Control flow: probe retrieves the platform IRQ and MMIO resource, allocates an mt76-backed `mt7603_dev`, initializes MMIO, reads chip ID/revision, masks interrupts, registers the shared IRQ handler, then calls common device registration. Failures after allocation free the mt76 device. Remove obtains driver data from platform state and unregisters the common device.

State and persistence: initializes only runtime state: mapped SoC MMIO, IRQ registration, ASIC revision, and common driver registration state. Firmware blobs `mt7628_e1.bin` and `mt7628_e2.bin` are advertised for later MCU loading.

Dependencies and integration: depends on Linux platform device and OF matching. Shares almost all common code with the PCI variant through `mt7603.h`, making the bus layer intentionally thin.

Risks: probe assumes a single IRQ and a single MMIO resource in device tree. If common registration does not set platform drvdata, remove cannot locate `mt76_dev`. IRQ is requested as shared; interrupt masking before common init is important to avoid early spurious handling.

Test signals: device-tree match on `mediatek,mt7628-wmac`, successful ASIC revision log, firmware load for MT7628 blobs, interface bring-up on SoC targets, and clean driver unbind/rebind.
