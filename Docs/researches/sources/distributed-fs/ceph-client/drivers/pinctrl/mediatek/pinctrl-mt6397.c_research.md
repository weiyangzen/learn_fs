# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6397.c

Purpose: Provides the MT6397 PMIC pinctrl driver data and probe wrapper. It reuses the older MediaTek common pinctrl framework with the parent PMIC regmap rather than MMIO resources.

Important APIs/types/functions: `mt6397_pinctrl_data` defines pins, register offsets under `MT6397_PIN_REG_BASE`, unsupported IES/SMT offsets, pull/data/mux offsets, port layout, and mux encoding. `mt6397_pinctrl_probe()` obtains the parent `struct mt6397_chip` and calls `mtk_pctrl_init()` with the PMIC regmap.

Control flow: The built-in platform driver matches `mediatek,mt6397-pinctrl`, gets parent driver data, and initializes common pinctrl directly against `mt6397->regmap`. No module init function is needed because `builtin_platform_driver()` registers it.

State and persistence: Runtime state is managed by the common framework and parent MFD regmap. Hardware state persists in PMIC register space for direction, pull enable/select, data out/in, and mux settings. IES and SMT are explicitly unsupported.

Dependencies and integration points: Depends on the MT6397 MFD core, `pinctrl-mtk-common.h`, generated `pinctrl-mtk-mt6397.h`, OF platform matching, and generic pinconf constants. Kconfig ties it to `MFD_MT6397` or `COMPILE_TEST`.

Risks: Parent driver data must be present and must contain a valid regmap. Register offsets are absolute PMIC offsets starting at `0xc000`; a base error affects every pin. Unsupported IES/SMT must be handled cleanly by common pinconf code. Since this is a PMIC pinctrl, probe ordering relative to the MFD parent matters.

Test signals: Build with MT6397 MFD, probe from a PMIC child node, enumerate PMIC pins, set GPIO direction/value through regmap, configure pull and mux modes, confirm IES/SMT return unsupported, and run suspend/resume scenarios that exercise parent regmap availability.
