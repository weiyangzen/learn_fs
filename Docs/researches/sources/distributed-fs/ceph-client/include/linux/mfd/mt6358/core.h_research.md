# sources/distributed-fs/ceph-client/include/linux/mfd/mt6358/core.h

## Purpose

This header defines the MT6358 PMIC interrupt topology contract shared by the MT6397-family MFD core and the `mt6358-irq` implementation. It describes how top-level PMIC interrupt groups map to Linux hardware IRQ numbers and how enable/status registers are generated for each group.

## Important APIs, Types, and Functions

`struct irq_top_t` describes one PMIC interrupt top block with a hardware IRQ base, number of interrupt status registers, enable/status register addresses, shifts between adjacent registers, and the bit offset in the top status register. `struct pmic_irq_data` aggregates all top blocks, the total IRQ count, top status register address, and enable/cache bit arrays. `enum mt6358_irq_top_status_shift` names the top status bits: buck, LDO, PSC, SCK, BM, HK, AUD, and MISC. `enum mt6358_irq_numbers` assigns stable hwirq numbers for regulator over-current, keys, charger, RTC, battery/fuel-gauge, audio/accessory, and SPI alert events. `MT6358_IRQ_*_BASE`, `MT6358_IRQ_*_BITS`, and `MT6358_TOP_GEN(sp)` are macro helpers used to build the top-block table.

## Control Flow

The header has no runtime flow itself. In the IRQ driver, a table built with `MT6358_TOP_GEN(BUCK)` and related groups lets the handler read `top_int_status_reg`, identify asserted top groups, then iterate per-group status registers. Enable/disable paths use `en_reg` plus `en_reg_shift` and cached hwirq booleans to update hardware masks while preserving other PMIC IRQ state.

## State and Persistence Behavior

The structs describe driver-owned runtime state, not persistent storage. `enable_hwirq` and `cache_hwirq` are in-memory bit arrays used to synchronize Linux IRQ state with PMIC enable registers. Actual event latches and mask state live in the PMIC registers named by `mt6358/registers.h` and persist until cleared or reset by hardware/driver flow.

## Dependencies and Integration Points

The macros expect `MTK_PMIC_REG_WIDTH` and register constants such as `MT6358_BUCK_TOP_INT_CON0` to be visible from companion includes in `drivers/mfd/mt6358-irq.c`. The MFD core calls `mt6358_irq_init()` for MT6357, MT6358, and MT6359-like devices, so the topology shape must align with each chip-specific core header and register map. MFD child resources in `mt6397-core.c` refer to hwirq constants such as `MT6358_IRQ_RTC` and key IRQs.

## Risks and Edge Cases

Numbering holes in `enum mt6358_irq_numbers` are intentional because hardware groups are register-aligned; collapsing or reordering them would break resource mappings. `MT6358_TOP_GEN()` assumes fixed register spacing (`0x6` enable, `0x2` status) and a common register width, so any top block with different spacing must not use it unchanged. Off-by-one errors in `*_BITS` change the number of scanned registers and can hide high IRQ bits.

## Test Signals

Compile `drivers/mfd/mt6358-irq.c` with MT6358 enabled, boot an MT6358 platform, verify MFD child resources resolve expected Linux IRQs for RTC and PMIC keys, exercise key press/release, charger detect, RTC alarm, and regulator over-current paths, and inspect `/proc/interrupts` or irqdomain mappings for stable hwirq numbers.
