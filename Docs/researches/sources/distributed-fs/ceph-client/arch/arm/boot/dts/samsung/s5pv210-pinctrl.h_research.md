# sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/s5pv210-pinctrl.h

Purpose: this binding header defines S5PV210 pinctrl constants for DTS files.

Important API surface: it exports pull constants, power-down mode constants, drive-strength levels `S5PV210_PIN_DRV_LV1` through `LV4`, mux function constants input/output/function 2 through 6, and external interrupt alias `S5PV210_PIN_FUNC_F` equal to `S5PV210_PIN_FUNC_EINT` (`0xf`).

Control flow: none. The preprocessor turns symbolic pinctrl values into numeric cells in generated DTBs.

State and persistence: constants only. Values persist in board DTBs and are applied during pinctrl state configuration, including power-down modes.

Dependencies and integration: used by S5PV210 board DTS files listed in the Samsung Makefile and by the Samsung pinctrl binding/parser for that SoC family.

Risks and test signals: drive-strength encodings are not monotonic in source order (`LV2` is 2 and `LV3` is 1), so casual edits can invert electrical behavior. Test DTB builds, schema validation, and board checks for external interrupts, sleep pin states, and bus signal integrity.
