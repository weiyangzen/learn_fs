# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8167.h

Purpose: Defines the MT8167 pin descriptor table for the legacy MediaTek common pinctrl driver. It enumerates 125 pins (`0..124`) using `struct mtk_desc_pin`, with pinctrl names, a mostly `NULL` package-pad field, chip tag `"mt8167"`, EINT metadata, and mux-function lists. The table covers the logical pin/function namespace used by MT8167 device-tree pin groups.

Important APIs, types, and data: The local export is `static const struct mtk_desc_pin mtk_pins_mt8167[]`. Entries use the older `MTK_PIN(PINCTRL_PIN(...), pad, chip, eint, functions...)` form from `pinctrl-mtk-common.h`. The pin set starts with EINT pins, then covers keypad, UART, SPI, I2S/PCM, PWM, I2C, camera/display-related pins, CMDAT pins, storage pins, CEC/hotplug/HDMI clock/data pins, and NAND-style alternate names such as `NALE`, `NWEB`, `NLD*`, and `WATCHDOG`. In this file every pin has an `MTK_EINT_FUNCTION(0, pin_number)` style mapping; there are no `NO_EINT_SUPPORT` markers in the source.

Control flow and integration: `pinctrl-mt8167.c` includes this header and passes `mtk_pins_mt8167` into `struct mtk_pinctrl_devdata mt8167_pinctrl_data`. The platform driver matches `mediatek,mt8167-pinctrl` and probes through `mtk_pctrl_common_probe()`. The `.c` file supplies the operational maps: drive groups, per-pin drive-register fields, special PUPD/R0/R1 settings, IES/SMT ranges, register offsets, EINT offsets, and GPIO mode. The header provides the descriptor array consumed by the generic common-driver enumeration and mux lookup code.

State and persistence behavior: No mutable state lives in the header. It is compile-time descriptor data. Persistent effects of pin configuration are hardware register values written by the common driver through the data tables in `pinctrl-mt8167.c`.

Dependencies: Depends on `<linux/pinctrl/pinctrl.h>` and `pinctrl-mtk-common.h`. It must remain consistent with MT8167 register tables in `pinctrl-mt8167.c`, the `mediatek,mt65xx-pinctrl.yaml` compatible list, and MT8167 DTS pinctrl nodes.

Risks: Because the package-pad field is `NULL`, board-level debugging relies heavily on the logical pin names and DTS references. A wrong mux value or signal string can break peripheral bring-up without any compile-time failure. Since every pin has an EINT descriptor, interrupt-capability assumptions should be verified against actual silicon and the EINT hardware map. The table also needs careful alignment with special pull and drive maps for storage and keypad-style pins.

Test signals: Targeted build of `pinctrl-mt8167.c`, DT schema validation for MT8167 pinctrl nodes, boot-time probe of `mediatek,mt8167-pinctrl`, debugfs inspection for all 125 pins, GPIO/EINT tests across representative pins, storage tests for MSDC0-related pins, HDMI/CEC hotplug checks, and mux smoke tests for I2C/SPI/UART/I2S/PWM/keypad functions.
