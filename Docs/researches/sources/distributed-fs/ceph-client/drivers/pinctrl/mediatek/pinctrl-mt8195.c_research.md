# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8195.c

### Purpose
This Linux kernel platform driver is the MT8195 SoC data provider for the MediaTek Paris pinctrl core. It maps GPIO0 through GPIO144 into MT8195's seven IOCFG register banks, describes every supported pin configuration register class, supplies pull-type and RSEL resistance metadata, and registers a platform driver for `mediatek,mt8195-pinctrl`. The source contains no custom pinctrl algorithms; it relies on shared Paris and common-v2 helpers to interpret the SoC tables at runtime.

### Important APIs, Types, And Data
- `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrap `PIN_FIELD_CALC()` with MT8195's banked register model. The comments document seven physical IOCFG regions represented by base indexes 0 through 6.
- `mt8195_pin_mode_range`, `mt8195_pin_dir_range`, `mt8195_pin_di_range`, and `mt8195_pin_do_range` define the core mux, direction, input, and output register classes for pins 0-144.
- `mt8195_pin_ies_range`, `mt8195_pin_smt_range`, `mt8195_pin_pu_range`, `mt8195_pin_pd_range`, `mt8195_pin_pupd_range`, `mt8195_pin_r0_range`, `mt8195_pin_r1_range`, `mt8195_pin_drv_range`, `mt8195_pin_drv_adv_range`, and `mt8195_pin_rsel_range` provide the field calculators for input enable, Schmitt trigger, pull enable, PUPD/R0/R1 bias, normal drive strength, raw advanced drive, and selectable resistance.
- `mt8195_pin_rsel_val_range` maps 3-bit RSEL values for pins 8-17, 29-30, 34-35, and 44-45 to specific pull-up/pull-down resistance pairs.
- `mt8195_pull_type` selects the appropriate bias algorithm per pin, mixing PUPD/R1/R0, simple PU/PD, and PU/PD/RSEL-capable pins.
- `mt8195_reg_cals` is the common-helper lookup table for `PINCTRL_PIN_REG_MODE`, `DIR`, `DI`, `DO`, `SMT`, `IES`, `PU`, `PD`, `DRV`, `PUPD`, `R0`, `R1`, `DRV_ADV`, and `RSEL`.
- `mt8195_pinctrl_register_base_names` names the expected devicetree MMIO resources: `"iocfg0"`, `"iocfg_bm"`, `"iocfg_bl"`, `"iocfg_br"`, `"iocfg_lm"`, `"iocfg_rb"`, and `"iocfg_tl"`.
- `mt8195_eint_hw` defines EINT geometry with 7 ports, AP interrupt count 225, 32 debounce counters, and `debounce_time_mt6765`.
- `mt8195_data` binds all of the above to `mtk_pins_mt8195`, common bias callbacks, rev1 drive callbacks, and raw advanced-drive callbacks.
- `mt8195_pinctrl_of_match`, `mt8195_pinctrl_driver`, and `mt8195_pinctrl_init()` provide the platform-driver entry point.

### Control Flow
`mt8195_pinctrl_init()` runs at `arch_initcall` and calls `platform_driver_register()`. The platform driver binds to `mediatek,mt8195-pinctrl`; the of-match `.data` pointer gives the shared Paris probe function the `mt8195_data` descriptor. The common probe maps the named IOCFG resources, registers pinctrl and GPIO interfaces using `mtk_pins_mt8195`, and wires EINT support using `mt8195_eint_hw`.

Runtime control flow is the common MediaTek pinctrl flow. Mux selection writes the 4-bit mode field. GPIO direction and value paths write or read DIR/DO/DI fields. Pinconf operations locate a pin's calculator entry through `mt8195_reg_cals`, choose the correct MMIO base, and update bias, input-enable, Schmitt, drive, advanced-drive, or RSEL fields. Bias handling is delegated to combo helpers that use both `mt8195_pull_type` and, where available, `mt8195_pin_rsel_val_range` to translate requested pulls into register encodings.

### State And Persistence
This file has no mutable file-local state and no custom persistence. Static const descriptors are compiled into the driver and consumed by the common framework. The only lasting effects are hardware register values written by common pinctrl/gpio/pinconf/EINT code. Those values may survive some SoC low-power states depending on IOCFG power retention, but this driver itself does not save them. Suspend/resume handling is shared through `mtk_paris_pinctrl_pm_ops` referenced in the platform-driver `.pm` field.

### Dependencies And Integration Points
The source depends on `pinctrl-mtk-mt8195.h` for the pin descriptors and function names, and on `pinctrl-paris.h` plus common-v2 pinctrl code for data types, field macros, the Paris probe, PM hooks, debounce timing, bias helpers, drive helpers, and raw advanced-drive helpers. It integrates with device tree through the compatible string and seven named register bases, with the Linux pinctrl subsystem for mux/function selection, with pinconf for electrical settings, with gpiolib for GPIO mode, and with MediaTek EINT support for GPIO-backed interrupts. Unlike MT8189, this C file does not attach an explicit `.eint_pin` remap table; EINT numbering is inferred from the pin descriptors and `mt8195_eint_hw`.

### Risks
MT8195's risk profile is dominated by hardware metadata correctness. The seven-bank IOCFG layout means a wrong base index can redirect writes into a different regional register block. Bias configuration is mixed: some pins use PUPD/R1/R0, many use simple PU/PD, and only selected pins use 3-bit RSEL with a value table. The `mt8195_pull_type`, RSEL field ranges, and RSEL value ranges must therefore be updated as a unit. Several later pins in the header use fixed or null-function descriptors, so table ranges should not assume every GPIO has the same electrical capabilities. As with other Paris drivers, bad drive-strength or advanced-drive widths can damage signal integrity without producing an obvious software error.

### Test Signals
Build signals include successful compilation against the shared Paris/common-v2 symbols and the MT8195 pin descriptor header. Probe signals include binding to `mediatek,mt8195-pinctrl`, mapping all seven IOCFG bases, and successful pinctrl/gpio/EINT registration. Hardware tests should cover GPIO input/output and muxing across all seven banks, EINT interrupts for pins with `MTK_EINT_FUNCTION`, suspend/resume through the shared PM ops, and pinconf round trips for IES, SMT, PU/PD, PUPD/R0/R1, RSEL resistance, normal drive, and raw advanced drive. Electrical validation should include representative RSEL-capable pins 8-17, 29-30, 34-35, and 44-45.
