# sources/distributed-fs/ceph-client/drivers/mfd/mt6397-core.c

Purpose: Platform MFD core for MediaTek PMICs attached below the SoC PMIC wrapper. It selects chip-specific child device arrays and IRQ initialization routines for MT6323, MT6328, MT6331/MT6332, MT6357, MT6358, MT6359, and MT6397.

Important APIs, types, and functions: numerous resource arrays define RTC, key, power-controller, and accessory-detect resources. Chip-specific `mfd_cell` arrays enumerate child devices. `struct chip_data` ties chip ID register/shift, child cells, and IRQ initializer. `mt6397_probe()` obtains the parent regmap, match data, reads chip ID, gets the platform IRQ, initializes the selected IRQ controller, and registers children via `devm_mfd_add_devices()`.

Control flow: the platform device is created by the PMIC wrapper. Probe uses OF match data to choose the chip profile, reads the hardware ID from the wrapper-provided regmap, stores `struct mt6397_chip`, initializes either legacy `mt6397_irq_init()` or newer `mt6358_irq_init()`, then publishes child devices with the IRQ domain.

State and persistence: `struct mt6397_chip` is parent state, holding dev, regmap, chip_id, irq, irqdomain, and IRQ masks initialized by the selected IRQ file. Child device resources describe hardware register windows and IRQ numbers but are static const data.

Dependencies and integration points: depends on parent PMIC wrapper regmap, MediaTek register/core headers, `mt6397-irq.c`, `mt6358-irq.c`, platform bus, MFD core, and DT compatibles for each chip. Child drivers include RTC, regulator, codec/sound, clock, pinctrl, keys, auxadc, LEDs, power controller, and accdet depending on chip.

Risks: if `devm_mfd_add_devices()` fails, the irqdomain is removed manually, but normal devm removal does not unregister the PM notifier used by `mt6397-irq.c`. Some MT6359 cells reuse MT6358 RTC resources/compatible, which may be intentional compatibility but needs binding awareness. Test signals include all OF match profiles, chip ID extraction shifts, platform IRQ absence, correct IRQ initializer selection, child resource mapping through the domain, and rollback on child add failure.
