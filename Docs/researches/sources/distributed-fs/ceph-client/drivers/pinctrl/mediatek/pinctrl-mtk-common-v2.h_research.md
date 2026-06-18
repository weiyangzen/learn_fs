# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common-v2.h

## Purpose
`pinctrl-mtk-common-v2.h` declares the data contract for newer MediaTek v2/Paris pinctrl drivers. It defines logical register-field IDs, pull-type flags, field calculation macros, pin/function/EINT descriptors, the SoC descriptor used by v2 probes, runtime controller state, and exported helper prototypes implemented by `pinctrl-mtk-common-v2.c`.

## Important APIs, Types, And Macros
- Pull constants define generic enable/direction values plus pull implementation flags: `MTK_PULL_PU_PD_TYPE`, `MTK_PULL_PULLSEL_TYPE`, `MTK_PULL_PUPD_R1R0_TYPE`, `MTK_PULL_RSEL_TYPE`, `MTK_PULL_PD_TYPE`, and combination masks.
- `PIN_FIELD_CALC()`, `PIN_FIELD()`, and `PINS_FIELD()` construct `struct mtk_pin_field_calc` entries.
- `PIN_RSEL()` constructs `struct mtk_pin_rsel` entries for bias resistance lookup.
- `PINCTRL_PIN_REG_*` enumerates logical pin attributes consumed by SoC `reg_cal` tables and helper calls.
- `struct mtk_pin_field`, `mtk_pin_field_calc`, `mtk_pin_rsel`, and `mtk_pin_reg_calc` form the register lookup model.
- `struct mtk_pin_soc` is the main SoC integration structure with register calculators, pin/group/function arrays, EINT hardware, base names, pull types, RSEL mappings, and callback hooks.
- `struct mtk_pinctrl` captures runtime state for v2 users: pinctrl device, MMIO bases, device, GPIO chip, SoC data, EINT pointer, groups, lock, and RSEL mode.

## Control Flow
SoC drivers populate `struct mtk_pin_soc` using the macros and tables defined here. The probe path consumes `base_names`, maps MMIO resources into `struct mtk_pinctrl`, registers pinctrl/GPIO/EINT, and later calls the declared helpers for field access, bias configuration, drive configuration, advanced controls, and virtual GPIO checks.

## State And Persistence
The header contains static type declarations and one default base-name array. It persists no runtime state by itself. Runtime objects declared here are allocated by probe code, while actual pin state persists in hardware registers.

## Dependencies And Integration Points
The header includes gpiolib declarations and expects other MediaTek headers for EINT structs used by members and prototypes. It is the ABI between SoC data files such as `pinctrl-mt8196.c`, the shared v2 helper implementation, and Paris pinctrl probe code.

## Risks
In the checked-out source, `struct mtk_pin_desc` declares `const char *name;` twice, which is a compile-time struct redefinition issue unless fixed elsewhere. The field enum order is an ABI between SoC `reg_cal` arrays and helper calls. Pull-type flags are bitmasks, so adding pull models requires updating masks and combo helper order. Optional callbacks in `struct mtk_pin_soc` require callers to guard absent functions.

## Test Signals
Compile every v2 SoC driver that includes this header, especially to catch struct layout issues. Static-check `reg_cal` array indexing against `PINCTRL_PIN_REG_*`. Validate pin descriptors initialize EINT and function fields consistently with virtual GPIO expectations. Exercise SoCs with omitted optional callbacks and with combo/advanced callbacks.
