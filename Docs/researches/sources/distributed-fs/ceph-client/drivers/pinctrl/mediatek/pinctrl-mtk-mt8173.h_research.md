# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8173.h

Purpose: Defines the MT8173 pin descriptor table for the legacy MediaTek common pinctrl driver. It enumerates 135 pins (`0..134`) with `PINCTRL_PIN()` names, a `NULL` package-pad field, chip tag `"mt8173"`, EINT metadata, and mux-function alternatives. The file provides the per-pin namespace used by MT8173 pinctrl probe, DTS pin groups, GPIO users, and mux selection.

Important APIs, types, and data: The local export is `static const struct mtk_desc_pin mtk_pins_mt8173[]`. Entries expand through `MTK_PIN`, `MTK_EINT_FUNCTION`, and `MTK_FUNCTION` from `pinctrl-mtk-common.h`. The table starts with EINT-labelled pins, includes SPI, UART, I2S/PCM, HDMI/DP-style signals, MSDC0/MSDC1/MSDC2/MSDC3, camera/display signals, keypad rows/columns, I2C pins, `LCM_RST`, and debug-monitor alternatives. Each entry has an EINT function mapping, generally `MTK_EINT_FUNCTION(0, gpio_number)`, and one or more mux values including GPIO mode 0.

Control flow and integration: `pinctrl-mt8173.c` includes this header, passes `mtk_pins_mt8173` and its size into `struct mtk_pinctrl_devdata mt8173_pinctrl_data`, and uses a small `mt8173_pinctrl_probe()` wrapper around `mtk_pctrl_init()`. The OF match compatible is `mediatek,mt8173-pinctrl`. The companion `.c` file provides MT8173-specific special-pull mappings, IES/SMT tables, drive group tables, per-pin drive fields, register offsets, and EINT offsets. This header supplies the logical descriptors consumed by those shared operations.

State and persistence behavior: The header is static descriptor data only. It does not own locks, memory, or mutable state. Runtime pinctrl state is maintained by the common driver and the kernel pinctrl core, while configured electrical state persists in hardware registers.

Dependencies: Depends on `<linux/pinctrl/pinctrl.h>` and `pinctrl-mtk-common.h`. It integrates with `pinctrl-mt8173.c`, the legacy MediaTek pinctrl binding, and MT8173 DTS nodes under `arch/arm64/boot/dts/mediatek/mt8173.dtsi`.

Risks: The high-value risks are declarative mismatches: incorrect mux values, names that diverge from DTS expectations, EINT numbers that do not match hardware, or pin numbers that no longer align with drive/pull/IES/SMT tables. Storage pins have special pull and drive handling in the `.c` file, so MSDC-related descriptors should be reviewed with those tables. Because package pads are absent, wrong logical names are harder to diagnose during board bring-up.

Test signals: Build the MT8173 pinctrl driver, validate and boot MT8173 DTS pinctrl nodes, inspect debugfs for all 135 pins and functions, exercise GPIO and EINT behavior, test MSDC0-3 storage pins including special pulls, and run mux smoke tests for I2C, SPI, UART, I2S/PCM, display, keypad, and camera-related functions.
