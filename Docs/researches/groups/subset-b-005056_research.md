# Research: subset-b-005056 MediaTek pinctrl source files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8127.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8127.c

## Purpose

This file is the SoC data driver for the MediaTek MT8127 pin controller. It does not implement new pinctrl algorithms; it supplies MT8127-specific pin tables, register offsets, drive-strength classes, special pull-up/down rules, input-enable rules, Schmitt-trigger rules, EINT metadata, and the platform-driver binding used by the shared legacy MediaTek pinctrl core.

## Important APIs, Types, And Functions

The important local objects are `mt8127_drv_grp`, `mt8127_pin_drv`, `mt8127_spec_pupd`, `mt8127_ies_set`, `mt8127_smt_set`, `mt8127_pinctrl_data`, `mt8127_pctrl_match`, `mtk_pinctrl_driver`, and `mtk_pinctrl_init`. The data is expressed through common types from `pinctrl-mtk-common.h`: `struct mtk_drv_group_desc`, `struct mtk_pin_drv_grp`, `struct mtk_pin_spec_pupd_set_samereg`, `struct mtk_pin_ies_smt_set`, and `struct mtk_pinctrl_devdata`. The source depends on `pinctrl-mtk-mt8127.h` for `mtk_pins_mt8127`.

The driver uses `mtk_pctrl_common_probe` directly. The OF match row associates `mediatek,mt8127-pinctrl` with `&mt8127_pinctrl_data`, so the common probe retrieves the data with `device_get_match_data()` and passes it to `mtk_pctrl_init()`.

## Control Flow

At `arch_initcall` time, `mtk_pinctrl_init()` registers the platform driver. When a matching device-tree node appears, the common probe initializes the legacy pinctrl instance from the static `mt8127_pinctrl_data`. That shared initialization obtains the syscon regmap from `mediatek,pctl-regmap`, builds pin groups, registers pinctrl/pinmux/pinconf ops, creates a GPIO chip, maps GPIOs to pinctrl pins, and initializes EINT because `ap_num` is nonzero.

Runtime pin operations are table-driven. GPIO direction, output, input, pull enable/select, and pinmux use the offsets in `mt8127_pinctrl_data`; drive strength uses `mt8127_pin_drv` plus `mt8127_drv_grp`; special pull pins use `mtk_pctrl_spec_pull_set_samereg`; IES/SMT irregular ranges use `mtk_pconf_spec_set_ies_smt_range`.

## State And Persistence

All MT8127 metadata is `static const`; the source owns no mutable software state and no on-disk persistence. Runtime state lives in the shared `struct mtk_pinctrl`, GPIO chip, EINT object, and hardware registers reached through regmap. Register writes persist only as SoC hardware state until reset, power loss, or later pinctrl operations. This driver does not wire explicit PM ops, so suspend/resume behavior relies on the common framework and platform hardware retention.

## Dependencies And Integration Points

The file integrates with Linux platform-driver matching, OF compatible lookup, the generic pinctrl/GPIO subsystems, MediaTek legacy pinctrl helpers, MediaTek EINT support, and DT pin configuration constants from `dt-bindings/pinctrl/mt65xx.h`. The EINT block advertises six ports, 143 AP interrupt numbers, 16 debounce counters, and `debounce_time_mt2701`.

## Risks

The main risk is descriptor accuracy: incorrect pin numbers, offsets, bit positions, or drive-group classes silently program the wrong pad. The special pull table is sparse and covers keypad, EINT, and MSDC pins; pins omitted from `mt8127_spec_pupd` fall back to normal pull handling, so omissions can break board-level pulls. `type1_start`/`type1_end` are set to 143 only, which is a narrow legacy address split and should match the datasheet. EINT `ap_num`, debounce count, and pin descriptor EINT indices must stay consistent with `pinctrl-mtk-mt8127.h`.

## Test Signals

Useful signals are a successful kernel build with this driver enabled, DT probe with `mediatek,mt8127-pinctrl`, absence of `Cannot find pinctrl regmap`/registration errors, GPIO direction/value tests across several banks, pinmux selection for active board peripherals, pull-up/down tests on the listed special pins, IES/SMT configuration tests, and EINT debounce/interrupt tests on keypad, EINT, and MSDC-adjacent pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8127.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8135.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8135.c

## Purpose

This file provides the legacy MediaTek pinctrl data driver for MT8135. It defines the SoC-specific register layout, drive-strength groupings, a custom special pull-up/down implementation, EINT metadata, and the `mediatek,mt8135-pinctrl` platform binding.

## Important APIs, Types, And Functions

Besides the normal legacy tables, this file introduces a local `struct mtk_spec_pull_set` and `SPEC_PULL()` macro because MT8135 special pulls use separate PUPD, R0, and R1 offsets that do not fit the same-register helper used by several neighboring SoCs. Key objects are `mt8135_drv_grp`, `mt8135_pin_drv`, `spec_pupd`, `spec_pull_set()`, `mt8135_pinctrl_data`, and `mt8135_pctrl_match`.

`spec_pull_set()` is the main local function. It searches `spec_pupd` for the requested pin, selects the PUPD set or reset register according to `isup`, writes the PUPD bit, then writes R0 and R1 set/reset registers according to `MTK_PUPD_SET_R1R0_00`, `_01`, `_10`, or `_11`. Unsupported pins or invalid R1/R0 encodings return `-EINVAL`.

## Control Flow

The platform driver is registered at `arch_initcall`. The common probe receives `mt8135_pinctrl_data` from OF match data and calls `mtk_pctrl_init()`. The common path builds pinctrl groups, registers pinctrl/pinmux/pinconf operations, registers the GPIO chip, maps GPIO ranges, and initializes EINT.

At runtime, ordinary pin operations use the legacy register offsets: direction at `0x0000`, IES at `0x0100`, pull enable at `0x0200`, SMT at `0x0300`, pull select at `0x0400`, data out at `0x0800`, data in at `0x0A00`, and mux at `0x0C00`. Drive configuration is looked up through `mt8135_pin_drv` and `mt8135_drv_grp`. Special pull handling is redirected to the local `spec_pull_set()` via `.spec_pull_set`.

## State And Persistence

All pin metadata is static const. `spec_pull_set()` has no persistent local state; it only computes register addresses and writes through the regmap supplied by the common core. MT8135 is notable because `mtk_pctrl_init()` supports a second `mediatek,pctl-regmap` phandle specifically for 8135-style dual base addressing, so board DT correctness is part of the runtime state contract. Hardware register settings persist until reset, power transition, or later pinctrl changes.

## Dependencies And Integration Points

The driver depends on `pinctrl-mtk-common.h`, `pinctrl-mtk-mt8135.h`, Linux platform/OF/regmap APIs, the generic pinctrl and GPIO subsystems, and `dt-bindings/pinctrl/mt65xx.h`. EINT metadata reports six ports, 192 AP interrupt numbers, 16 debounce counters, and `debounce_time_mt2701`.

## Risks

The custom pull routine is order-sensitive and table-sensitive: wrong offsets or bit numbers in `spec_pupd` program PUPD/R0/R1 inconsistently. The code writes raw bit numbers to set/clear aliases, matching the legacy MediaTek register convention; if the regmap does not expose those aliases, pulls fail. Several drive entries cover discontinuous pin ranges and high pin numbers such as 181-202, so pin descriptor alignment with `mtk_pins_mt8135` is critical. Dual-regmap DT setup is another risk because missing or swapped phandles can make only part of the controller usable.

## Test Signals

Good tests include build coverage, OF probe for `mediatek,mt8135-pinctrl`, validation that one or two `mediatek,pctl-regmap` phandles resolve as intended, GPIO direction/value tests, mux tests for peripherals spanning both register bases, drive-strength reads/writes on representative drive classes, pull configuration tests for pins in `spec_pupd`, and EINT interrupt/debounce tests up to the advertised AP interrupt range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8135.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8167.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8167.c

## Purpose

This file is the MT8167 legacy MediaTek pinctrl data driver. It describes the SoC's pin drive groups, special pull-up/down registers, IES and SMT ranges, register offsets, EINT capabilities, OF compatible, and platform-driver registration.

## Important APIs, Types, And Functions

Key objects are `mt8167_drv_grp`, `mt8167_pin_drv`, `mt8167_spec_pupd`, `mt8167_ies_set`, `mt8167_smt_set`, `mt8167_pinctrl_data`, `mt8167_pctrl_match`, and `mtk_pinctrl_driver`. The source uses the common legacy data model: `struct mtk_pinctrl_devdata` points at `mtk_pins_mt8167`, the drive tables, special pull tables, special IES/SMT tables, the shared `mtk_pctrl_spec_pull_set_samereg` helper, and `mtk_pconf_spec_set_ies_smt_range`.

Unlike some older files, this one includes `linux/module.h`, exports a `MODULE_DEVICE_TABLE(of, mt8167_pctrl_match)`, and enables `.pm = pm_sleep_ptr(&mtk_eint_pm_ops)` in the platform-driver struct.

## Control Flow

`mtk_pinctrl_init()` registers the platform driver at `arch_initcall`. On `mediatek,mt8167-pinctrl`, `mtk_pctrl_common_probe()` receives `mt8167_pinctrl_data` and initializes the common legacy pinctrl stack. The resulting callbacks use the static register layout for pinmux, GPIO direction, input, output, pull, drive, IES, SMT, and EINT operations.

MT8167 maps direction at `0x0000`, data out at `0x0100`, data in at `0x0200`, pinmux at `0x0300`, pull enable at `0x0500`, and pull select at `0x0600`. Special PUPD/R0/R1 settings cover selected pins in banks around 14-17, 21-23, 40-43, 68-73, and 104-120. IES/SMT are range-based and include separate higher-offset handling for special pins.

## State And Persistence

The file's own data is immutable after boot. Mutable state is owned by the common pinctrl object, the GPIO chip, the EINT object, and the underlying registers. Hardware pin state can survive within a power state but is not persisted by this file. EINT suspend/resume is integrated through `mtk_eint_pm_ops`, so interrupt-controller state has an explicit PM path compared with MT8127/MT8135.

## Dependencies And Integration Points

The driver depends on `pinctrl-mtk-common.h`, `pinctrl-mtk-mt8167.h`, the Linux platform/OF/regmap/pinctrl stack, and the MT65xx DT pinctrl constants. It advertises six EINT ports, 169 AP interrupt numbers, 64 debounce counters, and `debounce_time_mt6795`.

## Risks

The register tables contain sparse pin coverage. Pins 74-99 are mostly absent from drive and special-pull tables, which may be intentional package/function coverage but should match the SoC datasheet. `mt8167_smt_set` has a `0xA900` offset for pins 34-39 while neighboring SMT offsets are around `0xA00`/`0xA10`; this may be deliberate but is a high-value review point because a typo would misroute SMT control. EINT metadata must align with the pin descriptors in the header and with DT interrupt users. PM behavior relies on `CONFIG_PM_SLEEP` and the `pm_sleep_ptr()` wrapper.

## Test Signals

Useful validation includes build and module alias checks, successful probe with `mediatek,mt8167-pinctrl`, suspend/resume with wake-capable EINT lines, GPIO bank direction/value testing, pinmux tests for peripherals using high pin numbers, pull tests for all `mt8167_spec_pupd` clusters, IES/SMT tests including pins 34-39, and interrupt debounce tests across the expanded 64 debounce counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8167.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8173.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8173.c

## Purpose

This file provides the MT8173 legacy MediaTek pinctrl driver data. It defines special pull, IES, SMT, drive-strength, register-layout, EINT, OF, PM, and probe wiring for the MT8173 pin controller.

## Important APIs, Types, And Functions

Important objects are `mt8173_spec_pupd`, `mt8173_smt_set`, `mt8173_ies_set`, `mt8173_drv_grp`, `mt8173_pin_drv`, `mt8173_pinctrl_data`, `mt8173_pinctrl_probe()`, `mt8173_pctrl_match`, and `mtk_pinctrl_driver`. The file uses `struct mtk_pinctrl_devdata` from the legacy common layer and `mtk_pins_mt8173` from `pinctrl-mtk-mt8173.h`.

`mt8173_pinctrl_probe()` is a small local wrapper that calls `mtk_pctrl_init(pdev, &mt8173_pinctrl_data, NULL)`. Unlike drivers that use `.data` in the OF match and `mtk_pctrl_common_probe`, the compatible row here only lists `mediatek,mt8173-pinctrl`; the probe supplies the data directly.

## Control Flow

The driver registers at `arch_initcall`. Device-tree matching invokes `mt8173_pinctrl_probe()`, which enters the same legacy `mtk_pctrl_init()` path used by the common probe. The common path resolves the pinctrl regmap, builds groups, registers pinctrl and GPIO operations, creates the GPIO-to-pin range, and initializes EINT.

Pin configuration is table-driven. Standard register offsets are direction `0x0000`, pull enable `0x0100`, pull select `0x0200`, data out `0x0400`, data in `0x0500`, and pinmux `0x0600`. Special pulls mostly cover keypad and MSDC pins. IES and SMT ranges cover normal pads and several MSDC-specific register blocks. Drive strength uses three drive classes and a large `mt8173_pin_drv` table rooted at `DRV_BASE` plus peripheral-specific offsets.

## State And Persistence

All local data is static const. The wrapper probe has no extra state. Runtime state is allocated and owned by `mtk_pctrl_init()`, including `struct mtk_pinctrl`, GPIO chip, pinctrl device, and EINT state. Register values persist only as hardware state. The driver enables `.pm = pm_sleep_ptr(&mtk_eint_pm_ops)`, so EINT suspend/resume is integrated with the device PM path.

## Dependencies And Integration Points

Dependencies include the legacy MediaTek common pinctrl core, regmap/syscon DT plumbing, generic pinctrl/GPIO, EINT support, `pinctrl-mtk-mt8173.h`, and `dt-bindings/pinctrl/mt65xx.h`. EINT metadata advertises six ports, 224 AP interrupt numbers, 16 debounce counters, and `debounce_time_mt2701`.

## Risks

Because the OF match row does not carry `.data`, switching this file to `mtk_pctrl_common_probe` without adding match data would break probing. The drive table includes a repeated pin 85 entry with different offsets, which may represent hardware-specific overlapping control but should be treated as a review hot spot. MSDC and keypad special pull entries must match board electrical requirements; wrong R0/R1/PUPD bit positions can cause boot-media instability. EINT `ap_num` is larger than the pin count, so header EINT mapping and interrupt-controller assumptions need explicit validation.

## Test Signals

Signals include successful compile, probe on `mediatek,mt8173-pinctrl`, GPIO/pinmux registration, EINT suspend/resume testing, keypad row/column pull tests, MSDC0-3 signal pull and drive tests, drive-strength tests around the duplicated pin 85 entry, GPIO direction/value tests across low and high banks, and interrupt debounce validation on representative EINT-capable pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8173.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8183.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8183.c

## Purpose

This file is the MT8183 pinctrl data driver for the newer MediaTek "Paris" pinctrl framework. It describes how each pin property maps to one of nine named MMIO bases and how generic Paris pinctrl callbacks should handle mode, GPIO, IES, SMT, pull, drive, advanced drive, and EINT operations.

## Important APIs, Types, And Functions

The file defines `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrappers around `PIN_FIELD_CALC()` for single-pin and shared-field register calculations. Key data arrays are `mt8183_pin_mode_range`, `mt8183_pin_dir_range`, `mt8183_pin_di_range`, `mt8183_pin_do_range`, `mt8183_pin_ies_range`, `mt8183_pin_smt_range`, `mt8183_pin_pullen_range`, `mt8183_pin_pullsel_range`, `mt8183_pin_drv_range`, `mt8183_pin_pupd_range`, `mt8183_pin_r0_range`, `mt8183_pin_r1_range`, `mt8183_pin_e1e0en_range`, `mt8183_pin_e0_range`, and `mt8183_pin_e1_range`.

`mt8183_reg_cals` maps those arrays to `PINCTRL_PIN_REG_*` indices. `mt8183_data` is the `struct mtk_pin_soc` consumed by `mtk_paris_pinctrl_probe`. It points to `mtk_pins_mt8183`, nine base names, EINT metadata, and generic callbacks such as `mtk_pinconf_bias_set_combo`, `mtk_pinconf_drive_set_rev1`, and advanced drive get/set helpers.

## Control Flow

The platform driver registers at `arch_initcall`. On `mediatek,mt8183-pinctrl`, the Paris probe obtains `mt8183_data` through OF match data, ioremaps every named base resource, builds pinctrl state, registers the pinctrl device, enables it, initializes EINT if possible, and creates the GPIO chip.

Runtime control is completely table-driven. Mode/dir/DI/DO use the primary base style. IES and SMT use per-pin and shared fields over bases `iocfg0` through `iocfg8`. Pull enable and pull select cover normal pull pins. PUPD/R0/R1 arrays support advanced pull pins, and E1/E0/DRV_EN arrays support advanced drive controls.

## State And Persistence

The local data is immutable. Paris runtime state is allocated in `struct mtk_pinctrl`, including the base pointer array, lock, pinctrl state, EINT, and GPIO chip. Register writes persist in hardware until reset, sleep-state loss, or later reconfiguration. The driver uses `.pm = pm_sleep_ptr(&mtk_paris_pinctrl_pm_ops)`, so Paris EINT suspend/resume hooks participate in PM.

## Dependencies And Integration Points

The source depends on `pinctrl-mtk-mt8183.h` for pin/function descriptors and on `pinctrl-paris.h`/`pinctrl-mtk-common-v2.h` for the range-calculation model. Device tree must provide named resources `iocfg0`, `iocfg1`, `iocfg2`, `iocfg3`, `iocfg4`, `iocfg5`, `iocfg6`, `iocfg7`, and `iocfg8`. EINT metadata advertises six ports, 212 AP interrupt numbers, 13 debounce counters, and `debounce_time_mt6765`.

## Risks

The major risk is base-name and field-table correctness. A wrong `i_base`, offset, bit, or shared-field flag can redirect configuration to another IO configuration block. Some pins have shared fields via `PINS_FIELD_BASE`, so treating them as independent in tests can produce surprising coupled behavior. Advanced pull/drive coverage is sparse and must match the `pull_type` behavior implied by the common Paris code even though this file does not define a pull-type array. Missing any of the nine named resources makes probe fail.

## Test Signals

Test signals include successful build, DT probe with all nine resources mapped, pinmux and GPIO tests across pins 0-192, IES/SMT tests on pins from each `iocfg` base, pull enable/select tests for normal pins, PUPD/R0/R1 tests for advanced-pull pins, advanced drive tests on pins in the E0/E1/DRV_EN tables, EINT debounce tests, and suspend/resume coverage through `mtk_paris_pinctrl_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8183.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8186.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8186.c

## Purpose

This file is the MT8186 Paris pinctrl data driver. It maps 185 pins to seven named IO configuration bases and supplies register calculators for mode, GPIO, IES, SMT, pull-up/pull-down, PUPD/R0/R1 pulls, standard drive, advanced drive, resistor selection, and EINT handling.

## Important APIs, Types, And Functions

The file uses local `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` macros to create `struct mtk_pin_field_calc` rows. Important arrays include `mt8186_pin_mode_range`, `mt8186_pin_dir_range`, `mt8186_pin_di_range`, `mt8186_pin_do_range`, `mt8186_pin_ies_range`, `mt8186_pin_smt_range`, `mt8186_pin_pu_range`, `mt8186_pin_pd_range`, `mt8186_pin_pupd_range`, `mt8186_pin_r0_range`, `mt8186_pin_r1_range`, `mt8186_pin_drv_range`, `mt8186_pin_drv_adv_range`, `mt8186_pin_rsel_range`, `mt8186_pin_rsel_val_range`, and `mt8186_pull_type`.

`mt8186_reg_cals` connects those arrays to `PINCTRL_PIN_REG_*` slots, including `PU`, `PD`, `PUPD`, `R0`, `R1`, `DRV_ADV`, and `RSEL`. `mt8186_data` provides the `struct mtk_pin_soc` for `mtk_paris_pinctrl_probe`, with callbacks for combo bias handling, rev1 drive handling, raw advanced drive handling, and pin resistance lookup.

## Control Flow

The driver registers at `arch_initcall` and matches `mediatek,mt8186-pinctrl`. The Paris probe retrieves `mt8186_data`, ioremaps the seven base resources, builds the pinctrl state, registers and enables pinctrl, attempts EINT setup, then registers the GPIO chip.

Runtime operations use the generic Paris pinctrl and pinconf code. Basic GPIO and mux operations use mode/dir/DI/DO ranges. Bias configuration dispatches according to `mt8186_pull_type`: pins 0-66 and many later pins use PU/PD, pins 67-82 and 84-89 use PUPD/R0/R1, and pins 127-146 use PU/PD plus RSEL resistance selection. Drive uses standard 3-bit fields, while advanced drive and RSEL are defined for a narrower high-speed pin subset.

## State And Persistence

Local data is static const, including a complete per-pin pull-type array. Runtime state lives in the Paris core allocation, ioremapped base array, lock, pinctrl device, EINT object, and GPIO chip. Hardware settings are register state, not software persistence. The driver uses `mtk_paris_pinctrl_pm_ops` for suspend/resume of EINT-related state.

## Dependencies And Integration Points

Dependencies include `pinctrl-mtk-mt8186.h`, `pinctrl-paris.h`, common v2 MediaTek pinctrl definitions, Linux platform/OF resource mapping, pinctrl/GPIO, and EINT. Device tree must provide `iocfg0`, `iocfg_lt`, `iocfg_lm`, `iocfg_lb`, `iocfg_bl`, `iocfg_rb`, and `iocfg_rt`. EINT metadata reports seven ports, 217 AP interrupt numbers, 32 debounce counters, and `debounce_time_mt6765`.

## Risks

The large one-entry-per-pin IES/SMT/PU/PD/drive tables create high risk for transcription errors. `mt8186_pull_type` must have exactly one entry per pin and must agree with the presence or absence of PU/PD, PUPD/R0/R1, and RSEL ranges. RSEL values are exposed in ohms-like pairs through `PIN_RSEL`; wrong values affect electrical bias, not just register readability. Named base ordering must match DT resource names because all table `i_base` values are positional.

## Test Signals

Useful tests include build/probe with all seven named resources, pinctrl debugfs inspection, GPIO/mux tests across all 185 pins, bias tests for each pull type cluster, RSEL tests on pins 127-146 including the optional `mediatek,rsel-resistance-in-si-unit` behavior in the Paris core, drive and advanced-drive tests on high-speed pins, EINT interrupt/debounce tests across seven ports, and suspend/resume wake tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8186.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8188.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8188.c

## Purpose

This file is the MT8188 Paris pinctrl data driver. It describes 178 pins across five named IO configuration bases and supplies register calculators for mux, GPIO, IES, SMT, transmit/receive select, PU/PD, PUPD/R0/R1, drive, advanced drive, RSEL resistance selection, EINT, and module metadata.

## Important APIs, Types, And Functions

The main local macros are `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()`. Major arrays are `mt8188_pin_mode_range`, `mt8188_pin_dir_range`, `mt8188_pin_di_range`, `mt8188_pin_do_range`, `mt8188_pin_smt_range`, `mt8188_pin_ies_range`, `mt8188_pin_tdsel_range`, `mt8188_pin_rdsel_range`, `mt8188_pin_pupd_range`, `mt8188_pin_r0_range`, `mt8188_pin_r1_range`, `mt8188_pin_pu_range`, `mt8188_pin_pd_range`, `mt8188_pin_drv_range`, `mt8188_pin_drv_adv_range`, `mt8188_pin_rsel_range`, `mt8188_pin_rsel_val_range`, and `mt8188_pull_type`.

`mt8188_reg_cals` wires those arrays to the Paris register enum, notably including `PINCTRL_PIN_REG_TDSEL` and `PINCTRL_PIN_REG_RDSEL` in addition to pull and drive registers. `mt8188_data` supplies `struct mtk_pin_soc` fields, pin descriptors, five base names, pull type and RSEL lookup data, rev1 drive callbacks, raw advanced-drive callbacks, and combo bias callbacks.

## Control Flow

At `arch_initcall`, the platform driver is registered. OF matching on `mediatek,mt8188-pinctrl` passes `mt8188_data` to `mtk_paris_pinctrl_probe`. The probe maps `iocfg0`, `iocfg_rm`, `iocfg_lt`, `iocfg_lm`, and `iocfg_rt`, builds pin state, registers and enables the pinctrl device, initializes EINT if possible, and adds the GPIO chip.

Runtime pin operations are handled by the Paris core. Basic mux and GPIO operations use contiguous mode/dir/DI/DO ranges. Pinconf uses IES/SMT tables, TDSEL/RDSEL tables for timing-related custom configs, PU/PD tables for most pins, PUPD/R0/R1 tables for R1/R0-style pins, and RSEL/advanced-drive tables for selected high-speed pins.

## State And Persistence

This file contributes static const SoC metadata only. Runtime state is held by the Paris core and hardware registers. The `pull_type` table is per-pin policy state compiled into the driver; it determines how generic bias operations select register families. Hardware register settings persist until reset, power-domain loss, suspend restoration behavior, or later pinctrl calls. The driver uses `mtk_paris_pinctrl_pm_ops` and declares `MODULE_DESCRIPTION`.

## Dependencies And Integration Points

Dependencies include `linux/module.h`, `pinctrl-mtk-mt8188.h`, `pinctrl-paris.h`, common v2 pinctrl definitions, Linux OF/platform resource mapping, pinctrl/GPIO, and EINT. EINT metadata advertises seven ports, 225 AP interrupt numbers, 32 debounce counters, and `debounce_time_mt6765`. Device tree must provide the five named IO configuration resources in the expected order.

## Risks

MT8188 has dense, long field tables and several shared register fields, so bit-position mistakes are likely to produce subtle electrical or mux failures. The TDSEL/RDSEL tables add timing-sensitive surface area beyond basic GPIO and bias; tests need to cover these custom configs. `mt8188_pull_type` mixes PU/PD, PUPD/R1R0, and PU/PD/RSEL behavior; mismatch with the register ranges causes generic bias operations to fail or program incomplete state. RSEL supports 3-bit values with several resistance pairs for pins 53-68 and 175-176, so wrong lookup values can affect signal integrity. The driver lacks `MODULE_DEVICE_TABLE(of, ...)`, which is worth checking if module autoloading matters in this tree.

## Test Signals

Signals include build/probe success, all five resources mapped, pinctrl debugfs visibility, GPIO direction/value tests across pins 0-177, pinmux tests for board peripherals, IES/SMT tests across each base, TDSEL/RDSEL custom pinconf tests, bias tests for each pull-type cluster, RSEL tests on pins 53-68 and 175-176, drive and advanced-drive tests, EINT debounce/wake tests, suspend/resume coverage, and module metadata/autoload checks if built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8188.c -->
