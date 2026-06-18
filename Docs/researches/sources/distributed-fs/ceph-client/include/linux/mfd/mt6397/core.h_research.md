# sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/core.h

## Purpose

This header defines the common core data structure and chip ID/IRQ contracts for the MediaTek MT6397-family PMIC MFD driver. It is shared by the parent MFD core, IRQ implementations, and child drivers that need the parent regmap or chip identity.

## Important APIs, Types, and Functions

`enum chip_id` lists supported PMIC IDs: MT6323, MT6328, MT6331, MT6332, MT6357, MT6358, MT6359, MT6366, MT6391, and MT6397. `enum mt6397_irq_numbers` defines legacy MT6397 IRQ hwirqs for speaker, battery, watchdog, keys, charger, over-voltage, LDO, audio, RTC, HDMI, and regulator events. `struct mt6397_chip` is the central parent object with `dev`, `regmap`, notifier block, parent IRQ, irqdomain, `irqlock`, wake/current/cache mask arrays, interrupt control/status register arrays, `chip_id`, and opaque `irq_data`. The exported prototypes are `mt6358_irq_init()` and `mt6397_irq_init()`.

## Control Flow

The MFD probe allocates and fills `struct mt6397_chip`, reads chip ID using a chip-specific address, calls the selected IRQ initializer, and then registers child `mfd_cell`s. Child drivers call `dev_get_drvdata(pdev->dev.parent)` to recover this structure and use the shared regmap. IRQ init functions populate irqdomain and mask state before child resources are mapped.

## State and Persistence Behavior

`struct mt6397_chip` holds runtime kernel state for IRQ masking, wake masks, cached masks, and chip metadata. It does not persist across reboot. The regmap points to PMIC hardware registers whose state may persist across AP resets depending on PMIC power domains. The notifier block supports power-management integration for wake/mask handling.

## Dependencies and Integration Points

The header includes mutex and notifier declarations and relies on forward declarations from included Linux headers for devices, regmap, and irqdomain in consumers. It integrates with `drivers/mfd/mt6397-core.c`, `mt6397-irq.c`, `mt6358-irq.c`, regulator drivers, `rtc-mt6397.c`, PMIC key drivers, pinctrl, LED, poweroff, AUXADC, and MediaTek codec drivers.

## Risks and Edge Cases

The fixed-size IRQ arrays of length 3 match legacy MT6397 interrupt register layout; newer chips use `irq_data` for richer topology, so code must not assume every chip uses only the arrays. `chip_id` is a 16-bit field while `enum chip_id` values are short IDs; callers must compare the same representation. Locking around mask caches is critical because parent IRQ handling and child enable/disable paths can race.

## Test Signals

Build all MT6397-family MFD variants, boot on at least one legacy MT6397 and one MT6358/MT6359-family board, verify child devices probe from the parent, inspect irqdomain mappings, exercise suspend/resume wake masks, and run regulator, RTC, key, and pinctrl smoke tests using the shared parent regmap.
