# Research: subset-b-005058

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8196.c -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8196.c

### Purpose
`pinctrl-mt8196.c` is the SoC data and platform-driver binding for the MediaTek MT8196 pin controller. It does not implement generic pinctrl algorithms itself; instead it describes MT8196 register geometry, pull/drive capabilities, EINT wiring, register base names, and callback choices consumed by the newer MediaTek Paris/v2 pinctrl stack.

### Important APIs, Types, And Data
- `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrap `PIN_FIELD_CALC()` with explicit register-base indexes. They are central because MT8196 has many IO configuration banks, not just one `base`.
- `mt8196_pin_*_range[]` arrays map pin numbers to register fields for mode, direction, input, output, Schmitt trigger, input enable, pull controls, drive strength, advanced drive, and RSEL. These are consumed through `struct mtk_pin_reg_calc`.
- `mt8196_pin_rsel_val_range[]` maps pins and RSEL indexes to pull-up and pull-down resistance values. This lets the combo bias helper accept either encoded RSEL values or SI-unit resistance requests when the core enables that mode.
- `mt8196_pull_type[]` assigns each pin one of the v2 pull-control models such as PU/PD, PUPD/R0/R1, RSEL, or pulldown-only.
- `mt8196_pinctrl_register_base_names[]` declares 16 MMIO base names: `base`, `rt`, `rm1`, `rm2`, `rb`, `bm1`, `bm2`, `bm3`, `lt`, `lm1`, `lm2`, `lb1`, `lb2`, `tm1`, `tm2`, `tm3`.
- `mt8196_eint_hw` describes EINT topology with 3 ports, AP EINT count 293, debounce count 32, and `debounce_time_mt6765`.
- `mt8196_data` is the integration object. It points at `mtk_pins_mt8196`, `eint_pins_mt8196`, the register calculator table, pull type table, RSEL table, and v2 callbacks including `mtk_pinconf_bias_set_combo()`, `mtk_pinconf_bias_get_combo()`, `mtk_pinconf_drive_set_rev1()`, `mtk_pinconf_drive_get_rev1()`, and raw advanced drive helpers.

### Control Flow
At `arch_initcall`, `mt8196_pinctrl_init()` registers `mt8196_pinctrl_driver`. Device-tree matching on `mediatek,mt8196-pinctrl` passes `mt8196_data` to `mtk_paris_pinctrl_probe`. The Paris probe maps named resources, registers pinctrl/GPIO/EINT state, and calls back through the v2 helpers. Runtime pinmux and pinconf operations resolve a pin and field through `mt8196_reg_cals`, then read or update the calculated MMIO bitfield.

### State And Persistence
The file only contains static const SoC descriptions and a platform driver. Runtime state is owned by the Paris/v2 core in `struct mtk_pinctrl`: mapped register bases, group data, GPIO chip, EINT object, and locks. Hardware state persists in pinctrl registers and is not cached here. Suspend/resume is delegated through `mtk_paris_pinctrl_pm_ops`.

### Dependencies And Integration Points
This file depends on `pinctrl-mtk-mt8196.h` for pin descriptors and EINT pin mappings, `pinctrl-paris.h` for the probe and PM implementation, `pinctrl-mtk-common-v2.h` types/macros, the Linux platform-driver/device-tree framework, and the MediaTek EINT support. Board DTS files must provide the compatible string and named register resources in the same order expected by `mt8196_pinctrl_register_base_names`.

### Risks
- Register range tables are dense and hand-maintained. A wrong base index, offset, or bit silently routes pinconf to the wrong IO bank.
- The v2 lookup path assumes each `mt8196_pin_*_range[]` table is ordered by pin range for binary search. Reordering or overlapping ranges would make lookup behavior incorrect.
- Several pins share fixed fields via `PINS_FIELD_BASE()`/fixed range semantics. Incorrect fixed-vs-per-pin encoding changes group-wide controls such as SMT/IES.
- Pull behavior depends on `mt8196_pull_type[]`; a mismatch between pull type and available register ranges will surface as `-ENOTSUPP` or, worse, wrong pull configuration.
- The EINT count is larger than the GPIO pin count, so virtual/non-GPIO EINT mappings must remain consistent with the pin descriptor data.

### Test Signals
- Build with `CONFIG_PINCTRL_MTK_PARIS` and the MT8196 pin header enabled; table/type mismatches usually fail at compile time.
- Boot an MT8196 device tree and verify `mediatek,mt8196-pinctrl` probes, all 16 base resources map, and EINT initializes.
- Exercise pinmux states for representative pins from each base bank and validate mode, direction, input, output, SMT/IES, pull, drive, advanced drive, and RSEL through hardware or debugfs.
- Test GPIO-to-IRQ and debounce on both normal GPIO EINTs and any virtual EINTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8196.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8365.c -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8365.c

### Purpose
`pinctrl-mt8365.c` supplies legacy MediaTek pinctrl SoC data for MT8365. It defines pin drive groups, per-pin drive register fields, special pull-up/down pins, IES/SMT ranges, a small MT8365-specific pull update helper, EINT hardware layout, and the platform driver that binds the generic legacy `pinctrl-mtk-common.c` implementation to `mediatek,mt8365-pinctrl`.

### Important APIs, Types, And Data
- `mt8365_drv_grp[]` describes three drive-strength encoding classes: 4/8/12/16 mA, 2/4/6/8 mA, and 2 through 16 mA in 2 mA steps.
- `mt8365_pin_drv[]` maps pins 0 through 144 to drive registers around offsets `0x710` through `0x770`, bit positions, and drive group classes.
- `mt8365_spec_pupd[]` lists special PUPD/R1/R0 same-register pins, mostly pins 22-25 and 80-109, used by `mtk_pctrl_spec_pull_set_samereg()`.
- `mt8365_ies_set[]` and `mt8365_smt_set[]` map discontinuous input-enable and Schmitt-trigger ranges to set/clear capable registers around `0x410` through `0x480`.
- `mt8365_set_clr_mode()` is a local callback that updates pull-enable and pull-select with `regmap_update_bits()` on the main registers rather than SET/CLR aliases.
- `mt8365_pinctrl_data` is the `struct mtk_pinctrl_devdata` instance consumed by `mtk_pctrl_common_probe()`.

### Control Flow
`mtk_pinctrl_init()` registers a platform driver at `arch_initcall`. A device tree node matching `mediatek,mt8365-pinctrl` supplies `mt8365_pinctrl_data` to `mtk_pctrl_common_probe()`. The generic legacy probe builds one group per pin, registers pinctrl, registers GPIO, adds a pin range, and initializes EINT if `ap_num` is nonzero. Runtime pinconf calls select data from this file: generic pull requests first try `spec_pull_set`, then MT8365-specific `mt8365_set_clr_mode()`, while drive strength and IES/SMT are resolved from the static tables.

### State And Persistence
The source declares static immutable tables and one platform driver. Runtime state is in `struct mtk_pinctrl` allocated by `pinctrl-mtk-common.c`; register changes persist in MMIO/syscon hardware. The group config cache stores only the last applied packed pinconf value per single-pin group and is not a full hardware-state mirror.

### Dependencies And Integration Points
The driver uses `pinctrl-mtk-common.h`, `pinctrl-mtk-mt8365.h`, `dt-bindings/pinctrl/mt65xx.h`, regmap, platform-device matching, and the common MediaTek EINT code. The legacy common driver expects a `mediatek,pctl-regmap` phandle or direct regmap path, plus optional interrupt-controller properties. Power management uses `mtk_eint_pm_ops`.

### Risks
- `mt8365_set_clr_mode()` intentionally bypasses SET/CLR aliases for pull registers. If offsets or bit selection are wrong, read/modify/write may disturb adjacent pull controls.
- `type1_start` and `type1_end` are both 145. In the common helper the second regmap is selected for `pin >= start && pin < end`, so this setting selects no pins. That may be intentional sentinel behavior, but it is fragile and should be verified against MT8365 register layout.
- Drive table coverage ends at pin 144; pin data must not expose unsupported drive-strength configuration for absent pins.
- IES/SMT range tables pack many pins into shared bits. A range typo affects multiple pins at once.
- EINT declares `ap_num = 160` and `db_cnt = 160`; pin descriptors and debounce tables need to remain aligned with that capacity.

### Test Signals
- Compile the MT8365 pinctrl driver with the legacy common implementation and MT8365 pin header.
- Boot with a DTS node using `mediatek,mt8365-pinctrl` and confirm common probe, GPIO registration, and EINT initialization.
- Apply pinctrl states covering generic pulls, special PUPD/R1/R0 pulls, drive strengths from all three drive groups, and IES/SMT toggles.
- Use GPIO libgpiod or kernel consumers to test direction, get/set, GPIO-to-IRQ, and input debounce.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8365.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8516.c -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8516.c

### Purpose
`pinctrl-mt8516.c` is the legacy MediaTek SoC description and platform-driver binding for MT8516. It contributes the MT8516 pin drive-strength map, special pull-register map, input-enable and Schmitt-trigger maps, register offsets, pinmux packing parameters, and EINT hardware description used by `pinctrl-mtk-common.c`.

### Important APIs, Types, And Data
- `mt8516_drv_grp[]` defines the same three drive classes used by several legacy MediaTek drivers: 4-16 mA, 2-8 mA, and 2-16 mA encodings.
- `mt8516_pin_drv[]` maps selected pins to drive register offsets from `0xd00` through `0xd70`. The table is sparse: not every pin has an entry, so unsupported pins reject drive-strength configuration.
- `mt8516_spec_pupd[]` maps special pull pins to PUPD/R1/R0 bit triplets at offsets `0xe00` through `0xe90`.
- `mt8516_ies_set[]` and `mt8516_smt_set[]` describe discontinuous IES and SMT bit ranges, allowing the common helper to use set/clear writes instead of a simple linear offset calculation.
- `mt8516_pinctrl_data` binds `mtk_pins_mt8516`, all table pointers, register offsets, mode packing, and EINT parameters.

### Control Flow
At `arch_initcall`, `mtk_pinctrl_init()` registers the MT8516 platform driver. Device tree matching on `mediatek,mt8516-pinctrl` selects `mt8516_pinctrl_data`, then `mtk_pctrl_common_probe()` performs the common registration path. Pinctrl maps generated from DTS `pinmux` values resolve functions by the MT8516 pin descriptor header. Pin configuration calls use `spec_pull_set` for special PUPD/R1/R0 pins, fall back to generic pull enable/select registers for other pins, and use MT8516 IES/SMT tables for input-enable and Schmitt configuration.

### State And Persistence
This file holds only static SoC metadata. Hardware state lives in register writes performed by the common driver through regmap. The platform driver persists for the life of the device; PM operations for EINT suspend/resume are delegated to `mtk_eint_pm_ops`. The common group cache stores only the last configuration value per pin group.

### Dependencies And Integration Points
It depends on `pinctrl-mtk-common.h`, `pinctrl-mtk-mt8516.h`, Linux OF/platform/regmap/pinctrl APIs, and `mtk-eint`. The data table expects one regmap backing the pin controller and optional interrupt-controller properties for EINT. It exports a module device table for OF autoloading.

### Risks
- The sparse `mt8516_pin_drv[]` means board states that request drive strength on unsupported pins fail with `-EINVAL`; DTS coverage should avoid unsupported pins.
- Special pull pins use shared set/reset registers; incorrect `pupd`, `r1`, or `r0` bit positions will invert bias or set the wrong resistor combination.
- `type1_start` and `type1_end` are both 125, which causes no pin to use `regmap2` under the common helper. Verify this is intentional for MT8516.
- `mode_per_reg = 5`, `mode_shf = 4`, and `mode_mask = 0xf` must match the hardware pinmux packing; bad values corrupt neighboring pin modes.
- EINT declares 169 AP interrupts and only 64 debounce counters, so tests need to cover pins with and without debounce-backed EINTs.

### Test Signals
- Build the MT8516 driver with its pin header and legacy common driver.
- Probe a DT node with `mediatek,mt8516-pinctrl`, verify pinctrl/GPIO registration, and verify EINT setup when `interrupt-controller` is present.
- Test pinmux on representative UART, I2S, MSDC, PWM, and GPIO pins from the MT8516 pin header.
- Exercise bias-disable, pull-up, pull-down, input-enable, Schmitt, output-level, and drive-strength configs, including both generic and special pull pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8516.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common-v2.c -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common-v2.c

### Purpose
`pinctrl-mtk-common-v2.c` is a shared library for newer MediaTek pinctrl drivers. It provides register-field lookup, locked read/modify/write, GPIO-to-EINT translation hooks, EINT construction, bias helpers for multiple MediaTek pull-register designs, drive-strength helpers, advanced pull/drive helpers, and exported symbols consumed by Paris/v2 SoC drivers.

### Important APIs, Types, And Functions
- `mtk_rmw()` performs spinlock-protected read/modify/write on a selected MMIO base and register offset.
- `mtk_hw_pin_field_lookup()` and `mtk_hw_pin_field_get()` translate a pin descriptor plus logical register field enum into `struct mtk_pin_field`. The lookup uses binary search over SoC-provided `struct mtk_pin_field_calc` ranges.
- `mtk_hw_set_value()` and `mtk_hw_get_value()` are exported generic field accessors. They validate field availability and value bounds, then handle single-register and cross-register bitfields.
- `mtk_is_virt_gpio()`, `mtk_xt_get_gpio_n()`, `mtk_xt_get_gpio_state()`, and `mtk_xt_set_gpio_as_eint()` connect the generic `mtk-eint` core to GPIO/pin state, including virtual EINTs that do not have real GPIO muxing.
- `mtk_build_eint()` allocates and initializes the EINT controller object from a device-tree node's register resources and IRQ.
- Bias helpers include revision 0 PU/PD, revision 1 PULLEN/PULLSEL, combo selection for PU/PD, pulldown-only, PUPD/R0/R1, RSEL, and PU/PD+RSEL.
- Drive helpers include old E4/E8 encoding, revision 1 `DRV`, raw `DRV`, advanced pull via R0/R1/PUPD, and advanced drive via `DRV_EN`/`DRV_E0`/`DRV_E1` or raw `DRV_ADV`.

### Control Flow
Runtime SoC drivers pass `struct mtk_pin_soc` tables to a higher-level v2/Paris probe. Pinmux or pinconf operations call exported helpers with a pin descriptor and logical field. The helper validates the enum, finds the relevant range, computes base index, offset, bit position, mask, and cross-register continuation, then applies a locked write or relaxed read. Bias combo setters choose the supported pull model from `soc->pull_type[pin]` or try all known types. EINT setup maps extra EINT register bases after the pinctrl base names and registers GPIO translation callbacks with `mtk_eint_do_init()`.

### State And Persistence
The file maintains no global mutable state. Runtime state is in `struct mtk_pinctrl`: MMIO base pointers, base count, device pointer, GPIO chip, EINT pointer, group arrays, lock, and `rsel_si_unit` interpretation flag. Hardware register writes persist in the SoC pin controller until reset or reconfiguration. EINT bases are ioremap'd during build and manually unmapped on initialization failure.

### Dependencies And Integration Points
The code integrates with Linux MMIO accessors, spinlocks, platform devices, OF address/IRQ parsing, gpiolib, and `mtk-eint`. It relies on SoC files to provide sorted register ranges, valid base-name counts, pin descriptors, pull-type tables, RSEL maps, drive group indexes, and EINT pin maps. It exports functions under GPL for other MediaTek pinctrl modules.

### Risks
- Binary search in `mtk_hw_pin_field_lookup()` assumes sorted non-overlapping ranges. Bad SoC tables produce missed fields or wrong registers.
- `pfd->mask = (1 << c->x_bits) - 1` can overflow if a future table uses 32-bit-wide fields; current tables are small, but the helper is not width-agnostic.
- Error handling in `mtk_pinconf_adv_pull_set()` returns `0` when R0 or R1 writes fail, which can mask partial hardware programming.
- `mtk_rsel_get_si_unit()` returns success even if no matching RSEL index is found, leaving the output unchanged. Callers need reliable SoC RSEL tables.
- EINT base counting assumes DT `reg-names` lists pinctrl bases first, then EINT bases. Resource-order drift breaks EINT mapping.
- Virtual GPIO detection depends on pin function arrays and EINT mux indexes being consistent.

### Test Signals
- Unit-style kernel tests or boot tests should cover field lookup for first, last, fixed, and cross-register fields in each SoC table.
- Exercise bias combo paths for PU/PD, pulldown-only, PULLSEL/PULLEN, PUPD/R0/R1, RSEL encoded values, and SI-unit RSEL requests.
- Verify advanced pull and drive get/set round trips, including unsupported-field fallback behavior.
- Boot with EINT enabled and disabled, with and without `interrupt-controller`, and confirm graceful `-ENODEV`/success behavior.
- Run lockdep or concurrent GPIO/pinconf stress to validate `mtk_rmw()` serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common-v2.h -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common-v2.h

### Purpose
`pinctrl-mtk-common-v2.h` declares the data contract for newer MediaTek v2/Paris pinctrl drivers. It defines logical register-field IDs, pull-type flags, field calculation macros, pin/function/EINT descriptors, the SoC descriptor used by v2 probes, runtime controller state, and exported helper prototypes implemented by `pinctrl-mtk-common-v2.c`.

### Important APIs, Types, And Macros
- Pull constants define generic enable/direction values plus pull implementation flags: `MTK_PULL_PU_PD_TYPE`, `MTK_PULL_PULLSEL_TYPE`, `MTK_PULL_PUPD_R1R0_TYPE`, `MTK_PULL_RSEL_TYPE`, `MTK_PULL_PD_TYPE`, and combination masks.
- `PIN_FIELD_CALC()`, `PIN_FIELD()`, and `PINS_FIELD()` construct `struct mtk_pin_field_calc` entries. SoC files use these to encode pin-to-register geometry.
- `PIN_RSEL()` constructs `struct mtk_pin_rsel` entries for bias resistance lookup.
- `PINCTRL_PIN_REG_*` enumerates logical pin attributes: mode, direction, input/output, SMT, PU/PD, drive fields, PUPD/R0/R1, IES, PULLEN/PULLSEL, advanced drive, RSEL, and maximum count.
- `struct mtk_pin_field`, `mtk_pin_field_calc`, `mtk_pin_rsel`, and `mtk_pin_reg_calc` form the register lookup model.
- `struct mtk_pin_desc` describes each pin, including number, name, EINT descriptor, drive group, and optional function list.
- `struct mtk_pin_soc` is the main SoC integration structure with register calculators, pin/group/function arrays, EINT hardware, base names, pull types, RSEL mappings, and callback hooks.
- `struct mtk_pinctrl` captures runtime state for v2 users: pinctrl device, MMIO bases, device, GPIO chip, SoC data, EINT pointer, groups, lock, and RSEL mode.

### Control Flow
This header is included by v2 common code and SoC drivers. SoC drivers populate `struct mtk_pin_soc` using the macros and tables defined here. The probe path consumes `base_names`, maps MMIO resources into `struct mtk_pinctrl`, registers pinctrl/GPIO/EINT, and later calls the declared helpers for field access, bias configuration, drive configuration, advanced controls, and virtual GPIO checks.

### State And Persistence
The header contains static type declarations and one default base-name array. It persists no runtime state by itself. Runtime objects declared here are allocated by probe code, while actual pin state persists in hardware registers.

### Dependencies And Integration Points
The header includes gpiolib declarations and expects other MediaTek headers for EINT structs used by members and prototypes. It is the ABI between SoC data files such as `pinctrl-mt8196.c`, the shared v2 helper implementation, and Paris pinctrl probe code.

### Risks
- In the checked-out source, `struct mtk_pin_desc` declares `const char *name;` twice. That is a direct compile-time struct redefinition error unless masked by local patches elsewhere. It should be reconciled before relying on this tree for a kernel build.
- The field enum order is an ABI between SoC `reg_cal` arrays and helper calls. Reordering enum values without updating all SoC data breaks field resolution.
- Pull-type flags are used as bitmasks; adding a new pull model requires updating both masks and combo helper order.
- `mtk_default_register_base_names[]` is marked `__maybe_unused`, but SoC drivers with multiple bases must override it correctly.
- Function pointers in `struct mtk_pin_soc` are optional; probe and pinconf users need to guard absent callbacks.

### Test Signals
- Compile every v2 SoC driver that includes this header, especially to catch struct layout and duplicate member issues.
- Static-check that all `reg_cal` arrays are indexed by `PINCTRL_PIN_REG_*` values and have `PINCTRL_PIN_REG_MAX` capacity.
- Validate SoC pin descriptors initialize EINT and function fields consistently with virtual GPIO expectations.
- Exercise pinconf paths for SoCs that omit optional callbacks and for SoCs that provide combo, advanced pull, and advanced drive callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common.c -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common.c

### Purpose
`pinctrl-mtk-common.c` implements the legacy MediaTek pinctrl core used by older SoC drivers such as MT8365 and MT8516. It registers Linux pinctrl, pinmux, pinconf, GPIO, and EINT services, translates device-tree `pinmux` and generic pinconf properties into register writes, and provides common helpers for special MediaTek pull, IES, and SMT layouts.

### Important APIs, Types, And Functions
- `mtk_get_regmap()` chooses `regmap1` or `regmap2` based on the SoC's `type1_start`/`type1_end` interval.
- `mtk_get_port()` calculates port register stride using `mode_shf`, `port_mask`, and `port_shf`.
- `mtk_pmx_gpio_set_direction()`, `mtk_gpio_set()`, `mtk_gpio_get_direction()`, `mtk_gpio_get()`, `mtk_gpio_to_irq()`, and `mtk_gpio_set_config()` implement GPIO-facing behavior.
- `mtk_pconf_spec_set_ies_smt_range()` and `mtk_pctrl_spec_pull_set_samereg()` are exported helpers for SoC-provided special IES/SMT and PUPD/R1/R0 tables.
- `mtk_pconf_parse_conf()` supports generic pin config parameters: bias disable, pull-up, pull-down, input enable, output level, Schmitt enable, and drive strength.
- `mtk_pctrl_dt_node_to_map()` and `mtk_pctrl_dt_subnode_to_map()` parse child nodes containing `pinmux` arrays plus generic pinconf properties into pinctrl maps.
- `mtk_pmx_set_mux()` and `mtk_pmx_gpio_request_enable()` program mux values from per-pin function descriptors.
- `mtk_pctrl_init()` is the main registration entry point, while `mtk_pctrl_common_probe()` retrieves OF match data and calls it.

### Control Flow
SoC platform drivers call `mtk_pctrl_common_probe()` or directly `mtk_pctrl_init()`. Probe obtains a regmap from the `mediatek,pctl-regmap` phandle or caller, optionally obtains a second regmap, stores SoC devdata, builds one pinctrl group per pin, registers the pinctrl device, allocates and registers a GPIO chip, adds a GPIO-to-pin range, and initializes EINT if the SoC advertises AP EINTs. At runtime, DTS pinctrl states are parsed into maps. Mux maps validate function numbers against each pin's function list and write pinmux bits. Config maps invoke `mtk_pconf_parse_conf()`, which writes pull, input, output, SMT, or drive fields through regmap.

### State And Persistence
Runtime state is stored in devm-managed `struct mtk_pinctrl`: regmaps, pinctrl descriptor/device, GPIO chip pointer, generated groups, group names, devdata, and EINT object. GPIO chip registration is explicitly removed on post-registration probe failures. Hardware pin state persists in registers. `group->config` stores the last applied config value for group get operations but does not represent full hardware state across multiple configs.

### Dependencies And Integration Points
The file integrates with Linux pinctrl core, pinconf generic parser, pinmux ops, gpiolib, regmap/syscon, platform devices, OF IRQ parsing, PM sleep ops, and `mtk-eint`. SoC data files must provide `struct mtk_pinctrl_devdata` with pin descriptors, register offsets, packing fields, drive tables, optional special callbacks, and EINT hardware parameters.

### Risks
- `mtk_pconf_set_ies_smt()` computes `bit = BIT(offset & mode_mask)` in the generic path. This depends on offset and port packing conventions and is easy to misconfigure in SoC data.
- `mtk_gpio_get_direction()` and `mtk_gpio_get()` read from `regmap1` directly instead of `mtk_get_regmap()`, which may be wrong for SoCs where some pins use `regmap2`.
- `mtk_pmx_set_mode()` calls `spec_pinmux_set()` but continues with generic programming, so special callbacks must be additive and not expect to replace generic writes.
- Group config get returns only the cached last config, not the live register state and not all configs applied to the pin.
- `gpiochip_add_data()` is not devm-managed here; the chip is removed only on later probe error, with normal lifetime relying on platform teardown behavior.
- Device-tree parsing reserves maps based on simple `pinmux` count and config presence; malformed pinmux values fail late with `-EINVAL`.

### Test Signals
- Build legacy MediaTek SoC drivers against this common file and run sparse/lockdep where possible.
- Boot test with valid and invalid `pinmux` states, including multiple child nodes and generic pinconf properties.
- Exercise GPIO request, direction input/output, get/set, GPIO-to-IRQ, and debounce via gpiolib.
- Test SoCs with special PUPD/R1/R0 tables, special IES/SMT tables, custom `mt8365_set_clr_mode`, and any SoC using `regmap2`.
- Verify suspend/resume of EINT through `mtk_eint_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common.h -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common.h

### Purpose
`pinctrl-mtk-common.h` defines the legacy MediaTek pinctrl data model shared by `pinctrl-mtk-common.c` and older SoC data files. It declares pin/function/EINT descriptors, helper macros for SoC pin tables, drive-strength metadata, special pull and IES/SMT range structures, EINT offset structures, the main `mtk_pinctrl_devdata` contract, runtime state, and common helper prototypes.

### Important APIs, Types, And Macros
- `MTK_PIN()`, `MTK_EINT_FUNCTION()`, and `MTK_FUNCTION()` let SoC headers build `struct mtk_desc_pin` arrays with Linux `PINCTRL_PIN()` entries, EINT mux/number pairs, and function lists.
- `SET_ADDR()` and `CLR_ADDR()` encode MediaTek set/clear register alias offsets from a base register and `port_align`.
- `struct mtk_drv_group_desc`, `MTK_DRV_GRP()`, `struct mtk_pin_drv_grp`, and `MTK_PIN_DRV_GRP()` describe drive-strength encoding and per-pin drive register locations.
- `struct mtk_pin_spec_pupd_set_samereg` plus `MTK_PIN_PUPD_SPEC_SR()` describe special PUPD/R1/R0 controls that share one register.
- `struct mtk_pin_ies_smt_set` plus `MTK_PIN_IES_SMT_SPEC()` describe irregular input-enable and Schmitt-trigger ranges.
- `struct mtk_eint_offsets` allows SoCs to override generic EINT register layouts.
- `struct mtk_pinctrl_devdata` is the main SoC data contract for the legacy common implementation.
- `struct mtk_pinctrl` is the runtime controller state used by the common implementation.

### Control Flow
SoC headers and C files include this header to define pin arrays and devdata. The common probe uses `mtk_pinctrl_devdata` to build Linux pinctrl groups, parse pinmux functions, calculate register addresses, apply pinconf, register GPIO, and initialize EINT. Optional callback pointers let SoCs override special pull handling, IES/SMT handling, pinmux sideband selection, direction register adjustment, and MT8365 pull update behavior.

### State And Persistence
The header itself has no mutable state. It defines static SoC table shapes and runtime state fields. Actual state is allocated by `mtk_pctrl_init()` and register values persist in hardware.

### Dependencies And Integration Points
It includes Linux pinctrl, regmap, generic pinconf, and `mtk-eint` types. It is used by legacy SoC pin headers such as `pinctrl-mtk-mt2701.h` and by SoC C files such as `pinctrl-mt8365.c` and `pinctrl-mt8516.c`.

### Risks
- `NO_EINT_SUPPORT` is `255`, which fits `unsigned char` EINT fields but cannot represent larger sentinel values. SoCs with more than 255 EINTs need the v2 model or a wider field.
- Many fields in `mtk_pinctrl_devdata` are raw offsets and bit-packing constants. Wrong values compile cleanly but corrupt hardware programming.
- `type1_start`/`type1_end` interval semantics are half-open; using equal values disables `regmap2`.
- Optional callbacks must match common-code expectations: return zero only when they fully handled a special case, and nonzero to fall back.
- `mt8365_set_clr_mode` is named after one SoC but lives in generic devdata, which can confuse reuse and maintenance.

### Test Signals
- Compile all legacy SoC drivers that include this header.
- Use Coccinelle or static checks for pin arrays whose pin numbers exceed `npins`, missing GPIO function 0, or EINT numbers exceeding sentinel limits.
- Boot-test representative legacy SoCs for pinmux, pinconf, GPIO, and EINT.
- Validate special callback behavior with pins inside and outside each special range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt2701.h -->
## sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt2701.h

### Purpose
`pinctrl-mtk-mt2701.h` is a legacy SoC pin descriptor header for MT2701. It declares `mtk_pins_mt2701[]`, a 280-entry array mapping each physical pin number to a name, EINT mux/number pair, and alternate function list. The legacy common driver consumes this table through an MT2701 devdata file to expose pin groups and validate device-tree pinmux requests.

### Important APIs, Types, And Data
- The file includes `pinctrl-mtk-common.h` and uses `MTK_PIN()`, `PINCTRL_PIN()`, `MTK_EINT_FUNCTION()`, and `MTK_FUNCTION()` for all entries.
- `mtk_pins_mt2701[]` covers pins 0 through 279.
- Function 0 is generally GPIO/GPI mode. Alternate functions cover PWRAP, SPI, UART, I2S/PCM, JTAG, NAND, IR, I2C, display/HDMI/MHL, MSDC, PWM, Ethernet/ESW, PCIe reset/wake/clock request aliases, debug monitor functions, antenna selection, and RAM buffer/internal interface pins.
- EINT mappings are mixed: many user-visible GPIO pins map to EINT numbers, while internal RAM buffer, AP/DSP, DVP, host/slave, Ethernet, and other pins use `NO_EINT_SUPPORT`.
- Comments document MT7623-specific alternate function aliases for some PCIe reset pins, preserving compatibility with closely related SoCs.

### Control Flow
This header does not execute code. During probe, the legacy common driver copies each `pin.pin` descriptor into the Linux pinctrl descriptor and builds one group per pin with the pin name as the group name. During DTS parsing, `MTK_GET_PIN_NO()` and `MTK_GET_PIN_FUNC()` extract a requested pin/function pair; the common driver validates that the function number appears in the selected pin's `functions` list before programming the pinmux register. EINT translation walks this pin array to find a matching EINT number.

### State And Persistence
The array is static const metadata. It persists in kernel memory as SoC description data. Runtime mux, GPIO, and EINT state is maintained by the common driver and hardware registers, not by this header.

### Dependencies And Integration Points
The header depends on the legacy common data model. It must be paired with an MT2701 C driver that provides register offsets, drive tables, pull tables, and EINT hardware parameters. DTS pinmux definitions rely on the exact pin numbers and function mux values listed here.

### Risks
- The table is large and manually maintained; off-by-one pin numbers or wrong mux values cause DTS states to validate but select the wrong hardware function.
- `NO_EINT_SUPPORT` appears frequently; consumers must not request IRQs for those pins.
- Some pins use `GPIxx` rather than `GPIOxx` for function 0, reflecting input-only or special behavior. Generic GPIO assumptions need board-level verification.
- Compatibility aliases for MT7623 PCIe functions use duplicate function names at different mux values; validation allows them, but board DTS must select the correct mux value for the target SoC.
- EINT fields are `unsigned char` in the legacy header, so sentinel and EINT values depend on the 0-255 range.

### Test Signals
- Compile the MT2701 pinctrl driver that includes this header and verify `ARRAY_SIZE(mtk_pins_mt2701)` matches the devdata `npins`.
- Boot with MT2701/related DTS pinctrl states for each major peripheral group: PWRAP, UART, SPI, I2C, I2S/PCM, MSDC, HDMI, PWM, Ethernet, and GPIO.
- Test GPIO request and EINT mapping for supported pins, and confirm unsupported pins reject GPIO-to-IRQ.
- Validate any MT7623-specific PCIe aliases on actual target hardware or with register readback after pinmux selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt2701.h -->
