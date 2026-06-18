# sources/distributed-fs/ceph-client/include/linux/mfd/mt6359/core.h

## Purpose

This header defines MT6359 PMIC interrupt numbering and top-level IRQ grouping. It is the MT6359 counterpart to the MT6358 core IRQ header and is consumed by the shared `mt6358-irq` driver path.

## Important APIs, Types, and Functions

`enum mt6359_irq_top_status_shift` names top interrupt groups: BUCK, LDO, PSC, SCK, BM, HK, AUD at bit 7, and MISC. `enum mt6359_irq_numbers` assigns hardware IRQ numbers for buck over-current, LDO over-current, power/home key press and release, charger detect edge, RTC, fuel gauge, battery/thermal/AUXADC, audio/accessory, and SPI alert events. Base and bit-count macros derive group ranges, and `MT6359_TOP_GEN(sp)` constructs a `struct irq_top_t` initializer using MT6359 register constants.

## Control Flow

The header has no direct execution. The IRQ driver uses the generated top descriptors to walk from a top status bit to one or more group status registers and then to Linux nested IRQs. Enable and disable operations use the per-group enable register addresses and fixed register spacing encoded in the `MT6359_TOP_GEN()` macro.

## State and Persistence Behavior

Driver runtime state lives in `struct pmic_irq_data` from the MT6358 header, while hardware state lives in MT6359 registers. The enum values are persistent ABI inside the kernel tree because MFD cell resources and child drivers refer to them by number/name.

## Dependencies and Integration Points

This file relies on `struct irq_top_t`, `MTK_PMIC_REG_WIDTH`, and the MT6359 register map being included by the C file that uses it. It integrates with `drivers/mfd/mt6397-core.c` for child resources such as keys, RTC, and accessory detection, and with `drivers/mfd/mt6358-irq.c` for the actual IRQ domain setup.

## Risks and Edge Cases

The MT6359 top status layout differs from MT6358 because AUD starts at bit 7, leaving a gap. Treating top status bits as a dense sequence would route interrupts incorrectly. Several IRQ numbers are sparse by design; removing gaps changes register indexing. `MT6359_IRQ_BATON_BAT_OU` appears to be a truncated name but is part of the current exported enum spelling and should not be renamed casually without consumer updates.

## Test Signals

Compile `mt6358-irq.c` with MT6359 enabled, boot an MT6359 platform, verify `irq_create_mapping` for `MT6359_IRQ_RTC`, `MT6359_IRQ_PWRKEY`, and ACCDET resources, exercise PMIC key press/release, RTC alarm, charger detect edge, accessory detection, and at least one BM/HK interrupt path.
