# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8192.c

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
