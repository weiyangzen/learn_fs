# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common.h

## Purpose
`pinctrl-mtk-common.h` defines the legacy MediaTek pinctrl data model shared by `pinctrl-mtk-common.c` and older SoC data files. It declares pin/function/EINT descriptors, helper macros for SoC pin tables, drive-strength metadata, special pull and IES/SMT range structures, EINT offset structures, the main `mtk_pinctrl_devdata` contract, runtime state, and common helper prototypes.

## Important APIs, Types, And Macros
- `MTK_PIN()`, `MTK_EINT_FUNCTION()`, and `MTK_FUNCTION()` let SoC headers build `struct mtk_desc_pin` arrays with Linux `PINCTRL_PIN()` entries, EINT mux/number pairs, and function lists.
- `SET_ADDR()` and `CLR_ADDR()` encode MediaTek set/clear register alias offsets.
- Drive macros and structs describe drive-strength encoding and per-pin drive register locations.
- `struct mtk_pin_spec_pupd_set_samereg` describes special PUPD/R1/R0 controls that share one register.
- `struct mtk_pin_ies_smt_set` describes irregular input-enable and Schmitt-trigger ranges.
- `struct mtk_pinctrl_devdata` is the main SoC data contract for the legacy common implementation.
- `struct mtk_pinctrl` is the runtime controller state used by the common implementation.

## Control Flow
SoC headers and C files include this header to define pin arrays and devdata. The common probe uses `mtk_pinctrl_devdata` to build Linux pinctrl groups, parse pinmux functions, calculate register addresses, apply pinconf, register GPIO, and initialize EINT. Optional callback pointers let SoCs override special pull handling, IES/SMT handling, pinmux sideband selection, direction register adjustment, and MT8365 pull update behavior.

## State And Persistence
The header itself has no mutable state. It defines static SoC table shapes and runtime state fields. Actual state is allocated by `mtk_pctrl_init()` and register values persist in hardware.

## Dependencies And Integration Points
It includes Linux pinctrl, regmap, generic pinconf, and `mtk-eint` types. It is used by legacy SoC pin headers such as `pinctrl-mtk-mt2701.h` and by SoC C files such as `pinctrl-mt8365.c` and `pinctrl-mt8516.c`.

## Risks
`NO_EINT_SUPPORT` is `255`, which fits `unsigned char` EINT fields but cannot represent larger sentinel values. Many `mtk_pinctrl_devdata` fields are raw offsets and bit-packing constants, so wrong values compile cleanly but corrupt hardware programming. `type1_start`/`type1_end` semantics are half-open. Optional callbacks must return zero only when they fully handled a special case. `mt8365_set_clr_mode` is named after one SoC but lives in generic devdata.

## Test Signals
Compile all legacy SoC drivers that include this header. Static-check pin arrays whose pin numbers exceed `npins`, missing GPIO function 0, or EINT numbers exceeding sentinel limits. Boot-test representative legacy SoCs for pinmux, pinconf, GPIO, and EINT, including pins inside and outside special callback ranges.
