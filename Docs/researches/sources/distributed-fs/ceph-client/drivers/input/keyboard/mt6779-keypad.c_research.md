## sources/distributed-fs/ceph-client/drivers/input/keyboard/mt6779-keypad.c

Purpose: MediaTek MT6779/MT6873 keypad driver. It reads hardware memory registers representing key states and maps them to matrix key events.

Important APIs/types/functions: `struct mt6779_keypad` stores regmap, input, clock, matrix dimensions, row/column calculation function, and previous bitmap state. `mt6779_keypad_irq_handler()` bulk reads state registers and reports changed bits. `mt6779_keypad_calc_row_col_single()` and `_double()` decode key numbers for one or two keys per group.

Control flow: probe maps MMIO through regmap, initializes previous state to all released, parses matrix dimensions, debounce, and `mediatek,keys-per-group`, builds keymap, writes debounce and row/column selection registers, enables the `kpd` clock, requests a threaded IRQ, registers input, and initializes wakeup. IRQ reads five memory registers, compares with prior bitmap, skips unused upper halfwords, converts each changed bit to row/column/scancode, reports active-low press state, syncs, and saves the new bitmap.

State/dependencies/integration: state is bitmap keymap_state and hardware configuration registers. Dependencies are platform MMIO, regmap, clock, matrix keypad properties, input core, and optional wakeup-source.

Risks and test signals: row/column decode is SoC-layout-specific; invalid `keys-per-group` is fatal. `regmap_bulk_read()` return value is not checked in the IRQ path. Test single/double group mappings, debounce max, active-low bit interpretation, sparse keymap, clock availability, and bulk-read error behavior.
