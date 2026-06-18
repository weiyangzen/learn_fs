# Research Group subset-b-005057

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8189.c -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8189.c

### Purpose
This Linux kernel platform driver supplies the MediaTek Paris pinctrl core with all MT8189-specific pin register geometry, pull/bias encoding, drive-strength metadata, EINT capability, and device-tree binding data. It is almost entirely declarative: the executable path is only platform-driver registration and reuse of `mtk_paris_pinctrl_probe()`, while the long static tables describe how GPIO0 through GPIO182 map onto MT8189's split IOCFG register banks. The companion header `pinctrl-mtk-mt8189.h` provides the `mtk_pins_mt8189` pin/function descriptors and the `eint_pins_mt8189` table that this file attaches to the SoC descriptor.

### Important APIs, Types, And Data
- `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrap `PIN_FIELD_CALC()` with a 32-bit register stride and select single-pin versus multi-pin field interpretation. The extra `i_base` argument is the register-bank index into `mt8189_pinctrl_register_base_names`.
- `mt8189_pin_mode_range`, `mt8189_pin_dir_range`, `mt8189_pin_di_range`, and `mt8189_pin_do_range` describe the contiguous core GPIO register layout for mode, direction, input, and output values.
- `mt8189_pin_smt_range`, `mt8189_pin_ies_range`, `mt8189_pin_tdsel_range`, `mt8189_pin_rdsel_range`, `mt8189_pin_pu_range`, `mt8189_pin_pd_range`, `mt8189_pin_pupd_range`, `mt8189_pin_r0_range`, `mt8189_pin_r1_range`, `mt8189_pin_drv_range`, `mt8189_pin_drv_adv_range`, and `mt8189_pin_rsel_range` are per-pin or grouped `struct mtk_pin_field_calc` tables for Schmitt trigger, input enable, transmit/receive delay select, pull-up/down enable, PUPD/R0/R1 bias encoding, drive strength, raw advanced drive, and selectable pull resistance.
- `mt8189_pin_rsel_val_range` maps the 3-bit RSEL fields for pins 51-68 and 180-181 to concrete pull-up/pull-down resistance pairs.
- `mt8189_pull_type` selects the common bias handling algorithm per pin, mixing `MTK_PULL_PU_PD_TYPE`, `MTK_PULL_PUPD_R1R0_TYPE`, and `MTK_PULL_PU_PD_RSEL_TYPE`.
- `mt8189_reg_cals` is the dispatch table consumed by common helpers when pinctrl, gpiolib, or pinconf code asks for a register class such as `PINCTRL_PIN_REG_MODE`, `PINCTRL_PIN_REG_DRV_ADV`, or `PINCTRL_PIN_REG_RSEL`.
- `mt8189_eint_hw` declares the interrupt-controller geometry: 3 EINT ports, AP interrupt count 210, 32 debounce counters, and `debounce_time_mt6765`.
- `mt8189_data` is the exported SoC contract for the Paris core: pin descriptors, EINT pin remap table, register calculators, base names, function count, GPIO mux value, bias callbacks, drive callbacks, pull types, and RSEL value table.
- `mt8189_pinctrl_of_match`, `mt8189_pinctrl_driver`, and `mt8189_pinctrl_init()` provide the platform binding for `mediatek,mt8189-pinctrl`.

### Control Flow
At `arch_initcall` time, `mt8189_pinctrl_init()` registers `mt8189_pinctrl_driver`. Device-tree matching on `mediatek,mt8189-pinctrl` returns `&mt8189_data` to the shared Paris probe path. `mtk_paris_pinctrl_probe()` then maps the named register bases, registers pinctrl/gpio/EINT services, and uses `mt8189_reg_cals` for all later register address calculations.

Runtime operations are table-driven. A mux request for a pin indexes `mt8189_pin_mode_range` and writes a 4-bit mode field. GPIO direction and value operations use the DIR/DI/DO ranges. Pin configuration requests such as bias enable, pull strength, Schmitt trigger, input enable, drive strength, TDSEL/RDSEL, or advanced drive call common MediaTek helpers through the callback pointers in `mt8189_data`; those helpers locate the correct `mtk_pin_field_calc` entry, choose the appropriate register bank by base index, and update the field. EINT setup uses both `mt8189_eint_hw` and `eint_pins_mt8189` because the hardware EINT numbering does not map as a simple one-to-one sequence for every pad.

### State And Persistence
The file owns no mutable software state. All arrays are `static const` except the EINT pin table imported from the header, and there are no runtime allocations in this source file. Persistent effects are hardware register writes performed by the shared pinctrl core using this metadata. Pin mux, GPIO output, bias, drive, input-enable, and interrupt debounce state can therefore persist in MMIO registers across low-power transitions according to the broader platform power domain behavior. Software-visible state is reconstructed at probe from device tree and these static tables; suspend/resume hooks are shared through `pm_sleep_ptr(&mtk_paris_pinctrl_pm_ops)`.

### Dependencies And Integration Points
This file depends on `pinctrl-mtk-mt8189.h` for pin/function and EINT pin descriptors, and on `pinctrl-paris.h` plus `pinctrl-mtk-common-v2` for `struct mtk_pin_soc`, `struct mtk_pin_field_calc`, `struct mtk_pin_rsel`, `MTK_RANGE()`, register-class indexes, bias helpers, drive helpers, EINT debounce data, and `mtk_paris_pinctrl_probe()`. It integrates with the platform bus, device tree, Linux pinctrl, gpiolib, pinconf, GPIO interrupt, and system suspend/resume paths. The base-name array must match the register resources supplied by the MT8189 devicetree node: `"base"`, `"bm0"`, `"bm1"`, `"bm2"`, `"lm"`, `"lt0"`, `"lt1"`, `"rb0"`, `"rb1"`, and `"rt"`.

### Risks
The largest risk is register-table accuracy. An incorrect bank index, offset, bit position, or width can silently make pinconf operations change the wrong pad or wrong IOCFG bank. The MT8189 file is especially sensitive because it includes TDSEL/RDSEL tables in addition to the common mode, bias, drive, and RSEL categories. `mt8189_pull_type` must stay aligned with both the pin descriptor count and the available PU/PD or PUPD/R0/R1/RSEL tables; a mismatch can make bias configuration fail or program an electrical setting different from the requested pull. RSEL value ranges are sparse, so adding new RSEL-capable pins requires both field and value-table updates. EINT risk is also high because `.ap_num = 210` and the explicit `eint_pins_mt8189` mapping must match the interrupt controller's view of the SoC.

### Test Signals
Useful build signals include successful compilation of the MT8189 pinctrl driver and no missing `PINCTRL_PIN_REG_*` table references from common helpers. Probe-time validation should show the `mt8189-pinctrl` platform device binding, all ten named register bases mapped, and pinctrl/gpiochip/EINT registration without resource errors. Hardware signals include correct GPIO input/output on representative pins from every bank, mux validation for peripherals named in `mtk_pins_mt8189`, EINT delivery and debounce on pins with non-linear EINT mapping, suspend/resume retention through `mtk_paris_pinctrl_pm_ops`, and electrical tests for pull-up/down, RSEL resistance, TDSEL/RDSEL delay, Schmitt trigger, and drive-strength settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8189.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8192.c -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8192.c

### Purpose
This Linux kernel platform driver provides the MT8192-specific data layer for the MediaTek Paris pinctrl framework. It describes how GPIO0 through GPIO227 are controlled across ten IOCFG register bases, supplies per-pin field tables for mux, GPIO, input-enable, Schmitt trigger, bias, drive strength, advanced drive, and RSEL, and binds that data to the `mediatek,mt8192-pinctrl` devicetree compatible. The common Paris core performs the actual pinctrl, GPIO, pinconf, and EINT operations by interpreting these tables.

### Important APIs, Types, And Data
- `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` adapt `PIN_FIELD_CALC()` for MT8192's multi-base IOCFG layout. `PIN_FIELD_BASE` is used for individual pin fields, while `PINS_FIELD_BASE` marks field records covering multiple pins that share a register field.
- `mt8192_pin_mode_range`, `mt8192_pin_dir_range`, `mt8192_pin_di_range`, and `mt8192_pin_do_range` cover the contiguous base GPIO register classes for mux mode, direction, input, and output values.
- `mt8192_pin_smt_range`, `mt8192_pin_ies_range`, `mt8192_pin_pu_range`, `mt8192_pin_pd_range`, `mt8192_pin_drv_range`, `mt8192_pin_pupd_range`, `mt8192_pin_r0_range`, `mt8192_pin_r1_range`, `mt8192_pin_drv_adv_range`, and `mt8192_pin_rsel_range` define the SoC-specific register fields for pin configuration. RSEL fields are 2-bit fields on selected pins rather than the 3-bit/value-table style used by MT8189 and MT8195.
- `mt8192_pull_type` gives the bias helper a per-pin encoding choice. The table mixes regular PU/PD pins with PUPD/R0/R1 pins and selected PU/PD/RSEL pins.
- `mt8192_pinctrl_register_base_names` names the ten register resources expected from devicetree: `"iocfg0"`, `"iocfg_rm"`, `"iocfg_bm"`, `"iocfg_bl"`, `"iocfg_br"`, `"iocfg_lm"`, `"iocfg_lb"`, `"iocfg_rt"`, `"iocfg_lt"`, and `"iocfg_tl"`.
- `mt8192_eint_hw` describes the EINT controller view: 7 ports, AP interrupt count 224, 32 debounce counters, and `debounce_time_mt6765`.
- `mt8192_reg_cals` connects common register-class indexes to the MT8192 field tables.
- `mt8192_data` is the `struct mtk_pin_soc` instance passed to the Paris core, including `mtk_pins_mt8192`, register calculators, base names, pull types, common bias helpers, drive helpers, and raw advanced-drive helpers.
- `mt8192_pinctrl_of_match`, `mt8192_pinctrl_driver`, and `mt8192_pinctrl_init()` expose the platform driver and device-tree match table.

### Control Flow
The file registers its platform driver from `arch_initcall(mt8192_pinctrl_init)`. During probe, the platform bus matches `mediatek,mt8192-pinctrl`, the common Paris driver receives `&mt8192_data`, maps the named register bases, initializes pinctrl/gpio support from `mtk_pins_mt8192`, and configures EINT support from `mt8192_eint_hw`.

After probe, all meaningful behavior is dispatched through common code. Pin mux changes write 4-bit mode fields. GPIO direction and value requests use the DIR/DI/DO calculators. Pinconf bias requests call `mtk_pinconf_bias_set_combo()` or `mtk_pinconf_bias_get_combo()`, which interpret `mt8192_pull_type` and then use the PU/PD, PUPD, R0/R1, or RSEL register classes. Drive-strength operations call the rev1 drive helpers for normal drive and raw advanced-drive helpers for the `PINCTRL_PIN_REG_DRV_ADV` class. EINT operation is driven by the pin descriptors in `pinctrl-mtk-mt8192.h` plus `mt8192_eint_hw`; this C file does not provide a separate `.eint_pin` remap table.

### State And Persistence
This source file declares only static data and has no private runtime state machine. The platform driver registration persists as kernel driver-core state after `arch_initcall`, and hardware pin state persists only in the mapped pinctrl/IOCFG registers that the common helpers write. There is no file-local allocation, no firmware loading, and no durable storage. Runtime pinctrl state is reconstructed from devicetree resources and the static `mt8192_data` descriptor on every probe. Suspend/resume behavior is delegated to `mtk_paris_pinctrl_pm_ops`.

### Dependencies And Integration Points
The driver depends on `pinctrl-mtk-mt8192.h` for pin descriptors and mux-function names, `pinctrl-paris.h` for the Paris probe and PM hooks, and the common MediaTek v2 pinctrl definitions for field calculation, pull-type constants, bias helpers, drive helpers, and EINT metadata. It integrates with devicetree through the compatible string and named MMIO resources, with Linux pinctrl and pinconf through common callbacks, with gpiolib for GPIO operations, and with EINT/IRQ code through `struct mtk_eint_hw`. The comments document the physical MMIO base addresses represented by the named resource list, making devicetree resource ordering and naming part of the functional contract.

### Risks
The primary risk is silent electrical or mux misconfiguration from table drift. MT8192 has 228 GPIO descriptors and ten IOCFG banks; wrong `i_base` values or bit offsets can affect unrelated banks. Shared fields created with `PINS_FIELD_BASE()` are especially review-sensitive because multiple pins intentionally share one field. Bias handling must stay consistent across `mt8192_pull_type`, PU/PD ranges, PUPD/R0/R1 ranges, and sparse 2-bit RSEL ranges; any mismatch can cause unsupported pull-strength requests or wrong pull direction/resistance. Because the file has no explicit `.eint_pin` remap table, the EINT mapping depends on the header pin descriptors and the hardware descriptor being sufficient for this SoC. New pin additions must update both the header and the register tables together.

### Test Signals
Compile-time signals include successful resolution of `mtk_pins_mt8192`, all `PINCTRL_PIN_REG_*` entries used by `mt8192_reg_cals`, and the shared Paris symbols. Probe-time signals include successful match on `mediatek,mt8192-pinctrl`, mapping all ten IOCFG resources, and registering pinctrl, GPIO, and EINT support. Hardware validation should cover GPIO input/output across all IOCFG banks, muxing of representative SPI/I2S/PWM/TDM/audio pins from the header, EINT delivery for descriptors with `MTK_EINT_FUNCTION`, suspend/resume behavior, and pinconf reads/writes for PU/PD, PUPD/R0/R1, 2-bit RSEL, drive strength, advanced drive, IES, and SMT fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8192.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8195.c -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8195.c

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8195.c -->
