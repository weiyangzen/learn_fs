# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-paris.h

## Purpose
This header is the public interface and macro layer for the MediaTek Paris common pinctrl driver. It lets SoC-specific pin tables describe pins, EINT metadata, functions, register ranges, and pin groups in the `pinctrl-mtk-common-v2.h` schema.

## Important APIs And Types
The header includes kernel pinctrl/pinmux/pinconf dependencies plus internal pinctrl core headers, `mtk-eint.h`, and `pinctrl-mtk-common-v2.h`. Important macros are `MTK_RANGE()` for register range arrays, `MTK_EINT_FUNCTION()` for `struct mtk_eint_desc`, `MTK_FUNCTION()` for `struct mtk_func_desc`, `MTK_PIN()` for `struct mtk_pin_desc`, `MTK_EINT_PIN()` for `struct mtk_eint_pin`, and `PINCTRL_PIN_GROUP()` for groups using pin/function arrays. It declares `mtk_paris_pinctrl_probe()`, `mtk_pctrl_show_one_pin()`, and `mtk_paris_pinctrl_pm_ops`.

## Control Flow And Integration
There is no executable control flow in the header. SoC drivers include it to build static descriptor tables and to reference the common probe function from their platform driver. The macros create compound function arrays terminated by an empty descriptor, which Paris later walks for function validation.

## State And Persistence
This header defines compile-time data construction only. Runtime state is owned by `pinctrl-paris.c` and common-v2 helpers. Compound literals created by `MTK_PIN()` become part of static initializer data when used in static SoC arrays.

## Dependencies
The header depends on macro compatibility with `struct mtk_pin_desc`, `struct mtk_func_desc`, `struct mtk_eint_desc`, and `struct mtk_eint_pin`. Any schema change in common-v2 requires updating these macros and all SoC tables. It also exposes internal pinctrl headers, so it is meant for in-tree driver use rather than a stable external API.

## Risks
Macro-heavy table definitions can hide type or terminator mistakes. `MTK_FUNCTION(0, NULL)` is allowed by current tables for virtual or fixed pins, so function-walking code must treat a `NULL` name as terminator only where intended by macro-generated arrays. Incorrect use of `PINCTRL_PIN_GROUP()` can mismatch pin and function arrays by naming convention.

## Test Signals
Compile all Paris SoC tables after macro edits. Static checks should verify function arrays are terminated, EINT tables are aligned, and SoC tables use the intended schema rather than the legacy `pinctrl-mtk-common.h` schema.
