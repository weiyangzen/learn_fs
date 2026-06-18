# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-moore.h

Purpose: Declares helper macros and the probe API for MediaTek Moore-binding SoC pinctrl drivers.

Important APIs/types/functions: Defines `MTK_RANGE()`, `MTK_PIN()`, `PINCTRL_PIN_GROUP()`, `PINCTRL_PIN_FUNCTION()`, and `mtk_moore_pinctrl_probe()`. `MTK_PIN()` creates `struct mtk_pin_desc` entries with EINT and drive group metadata. Group/function macros bridge SoC table naming conventions to generic pinctrl descriptors.

Control flow: No executable logic. SoC drivers include this header to define pins, groups, functions, register ranges, and then call `mtk_moore_pinctrl_probe()` from their platform probe.

State and persistence: No direct state. The macros determine static SoC table contents that later control muxing, GPIO, EINT, and pinconf behavior.

Dependencies and integration points: Includes core pinctrl, pinmux, pinconf, OF/platform headers, MediaTek EINT, and common-v2 definitions. It is the SoC-data contract consumed by `pinctrl-moore.c`.

Risks: Macro-generated names require strict table naming consistency. Incorrect EINT metadata in `MTK_PIN()` breaks GPIO-to-IRQ translation. Since `funcs` is initialized to `NULL`, SoC files must provide separate group/function mode data where the Moore core expects it.

Test signals: Compile Moore SoC files, inspect generated group/function arrays, probe a Moore SoC, and verify mux modes plus EINT mappings match DeviceTree binding examples.
