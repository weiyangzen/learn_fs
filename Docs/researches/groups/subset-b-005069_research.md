# Research: subset-b-005069

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91.h

## Purpose
This header is a register-layout contract for Atmel/Microchip AT91 Parallel I/O Controller pinctrl drivers. It contains no executable code; it centralizes PIO register offsets and bit masks used by AT91 pinctrl/GPIO implementations for muxing, GPIO direction/value, interrupt mode, pull configuration, filtering, Schmitt trigger, drive strength, and slew rate.

## Important APIs, Types, and Definitions
The exported API is a set of preprocessor constants. Core PIO offsets include `PIO_PER`, `PIO_PDR`, and `PIO_PSR` for PIO ownership; `PIO_OER`, `PIO_ODR`, and `PIO_OSR` for direction; `PIO_SODR`, `PIO_CODR`, `PIO_ODSR`, and `PIO_PDSR` for output and input data; `PIO_IER`, `PIO_IDR`, `PIO_IMR`, and `PIO_ISR` for interrupts; `PIO_PUER`, `PIO_PUDR`, `PIO_PPDER`, and `PIO_PPDDR` for pulls; `PIO_ASR`/`PIO_BSR` and `PIO_ABCDSR1`/`PIO_ABCDSR2` for peripheral muxing; and late-generation drive/slew offsets such as `SAM9X60_PIO_SLEWR`, `SAMA5D3_PIO_DRIVER1`, and `AT91SAM9X5_PIO_DRIVER1`. The only bit mask is `PIO_SCDR_DIV` for the slow-clock debounce divider.

## Control Flow and State
There is no runtime control flow or persistent C state. State lives in the hardware registers named by the macros. Downstream drivers choose offsets according to SoC generation and then read/write MMIO to apply pinctrl state. Several offsets are aliases because older PIO blocks use A/B selection while newer blocks use ABCD selection at the same addresses.

## Dependencies and Integration Points
The header is guarded by `__PINCTRL_AT91_H` and is intended for inclusion by AT91 pinctrl implementation files in the same driver family. It depends only on the C preprocessor and Linux kernel coding conventions; hardware access helpers are supplied by consumers.

## Risks
Incorrect offset use can corrupt mux, GPIO, or interrupt setup across an entire PIO bank. The aliasing of `PIO_ASR` with `PIO_ABCDSR1` and `PIO_BSR` with `PIO_ABCDSR2` makes SoC-specific selection logic important. Register names do not encode which silicon generation supports them, so consumers must gate late-generation drive and slew registers correctly.

## Test Signals
Useful validation comes from building AT91 pinctrl drivers that include this header, booting boards with GPIO, mux, pull, debounce, and interrupt DT states, and checking debugfs pinctrl state against expected PIO register values. Regression signals include broken GPIO direction/value operations, failed interrupt trigger configuration, and incorrect peripheral mux selection on SAM9/SAMA5/SAM9X60 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-aw9523.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-aw9523.c

## Purpose
This driver supports the Awinic AW9523B I2C GPIO expander as a combined pinctrl, pinmux, pinconf, GPIO, and optional nested interrupt controller. It exposes 16 pins arranged as two 8-bit ports, with GPIO/PWM muxing, input/output direction and level control, port 0 open-drain versus push-pull configuration, register caching, reset handling, and safe hardware defaults.

## Important APIs, Types, and Functions
`struct aw9523` is the main device state: device pointer, regmap, I2C mutex, reset GPIO, optional `vio` regulator status, pinctrl device, gpio chip, and optional `struct aw9523_irq`. Register macros map port-relative input, output, config, interrupt-disable, chip ID, global control, port mode, and reset registers. Pinctrl callbacks are `aw9523_pinctrl_get_groups_count`, `aw9523_pinctrl_get_group_name`, and `aw9523_pinctrl_get_group_pins`; pinmux callbacks are `aw9523_pmx_get_funcs_count`, `aw9523_pmx_get_fname`, `aw9523_pmx_get_groups`, and `aw9523_pmx_set_mux`. Pinconf is implemented by `aw9523_pconf_get` and `aw9523_pconf_set`. GPIO behavior is provided by direction, get, set, get/set-multiple helpers. IRQ behavior is handled by `aw9523_irq_mask`, `aw9523_irq_unmask`, `aw9523_irq_thread_func`, bus lock/sync, and `aw9523_gpio_irq_type`. Probe/remove are `aw9523_probe` and `aw9523_remove`.

## Control Flow and State
Probe allocates state, obtains the mandatory reset GPIO, creates the I2C regmap, enables optional `vio`, initializes the I2C mutex, calls `aw9523_hw_init`, fills a pinctrl descriptor, initializes the gpiochip, optionally wires IRQ support if `client->irq` is present, registers pinctrl, and finally registers the gpiochip. Hardware initialization bypasses cache, tries soft reset then hardware reset with retries, verifies chip ID `0x23`, sets all pins to GPIO, sets port 0 open-drain, sets all pins input, disables interrupts, reads port state to clear setup interrupts, and reinitializes the flat regcache. Remove reinitializes hardware when no controllable regulator exists, leaving pins in defaults.

## State and Persistence Behavior
Persistent state is split between hardware registers and regcache. `i2c_lock` serializes register access because regmap locking is disabled. IRQ bus lock puts regmap in cache-only mode, updates mask bits through irq callbacks, then syncs cache on unlock. `cached_gpio` stores the previous 16-bit input snapshot to synthesize edge handling from changed bits. The `vio_vreg` integer records whether the optional regulator is controllable or absent.

## Dependencies and Integration Points
The driver integrates with the I2C core (`module_i2c_driver`), regmap, regulator, gpiod reset, pinctrl/pinmux/pinconf, gpiolib, and IRQ domains. Firmware binding uses compatible `awinic,aw9523-pinctrl`; optional `interrupt-controller` enables nested GPIO IRQs.

## Risks
Reading input state is precious because it clears interrupt status; wrong regcache policy can lose events. Only port 0 supports open-drain mode, while port 1 is always push-pull, so pinconf must reject unsupported requests. `aw9523_pmx_set_mux` computes the register pin as modulo port width; mux changes depend on matching port-mode register selection. IRQs support only `IRQ_TYPE_NONE` and both-edge semantics, with software change detection rather than hardware per-edge programming. Any missed mutex coverage can race slow I2C operations.

## Test Signals
Build coverage should include I2C, GPIO, pinctrl, pinconf, and IRQ configurations. Runtime signals include successful chip ID read, reset fallback behavior, GPIO get/set and get/set-multiple across both ports, pinconf rejection on unsupported drive modes, PWM/GPIO mux switching, interrupt delivery on input changes, and remove-time reinitialization when `vio` is not controllable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-aw9523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-axp209.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-axp209.c

## Purpose
This platform driver exposes GPIO and pinmux support for X-Powers AXP20x PMIC families, including AXP209, AXP221/22x, and AXP813 variants. It maps PMIC GPIO pins to pinctrl groups and gpiolib lines and supports GPIO input/output, LDO mux membership, and ADC muxing where the specific chip descriptor allows it.

## Important APIs, Types, and Functions
`struct axp20x_pctrl_desc` describes per-chip pins, pin count, LDO-capable mask, ADC-capable mask, GPIO status bit offset, and ADC mux value. `struct axp20x_pctl` stores gpiochip, regmap, pinctrl device, device, descriptor, and four function descriptors. Key helpers include `axp20x_gpio_get_reg`, `axp20x_gpio_get`, `axp20x_gpio_get_direction`, `axp20x_gpio_set`, `axp20x_pmx_set`, `axp20x_pmx_set_mux`, `axp20x_pmx_gpio_set_direction`, `axp20x_funcs_groups_from_mask`, and `axp20x_build_funcs_groups`. Probe is `axp20x_pctl_probe`.

## Control Flow and State
Probe first checks DT availability and retrieves parent `struct axp20x_dev` drvdata. It allocates `struct axp20x_pctl`, initializes the gpiochip callbacks, selects the chip descriptor via OF match data, attaches the parent PMIC regmap, stores drvdata, builds function-to-group lists, allocates a pinctrl descriptor, registers pinctrl, registers the gpiochip, and adds a pin range. GPIO direction and mux paths write PMIC control registers via regmap. GPIO3 on AXP209 uses a special control layout and is handled separately for value, direction, and mux programming.

## State and Persistence Behavior
The driver owns no cache; persistent state is in PMIC registers accessed through the parent MFD regmap. Function membership is generated at probe and stored in devm-managed arrays. LDO mux selection deliberately returns success without writing bits because those mux bits overlap regulator on/off control and are left to the regulator framework. GPIO output path uses `chip->set`, while direction changes from gpiolib go through pinctrl GPIO direction helpers.

## Dependencies and Integration Points
The driver depends on the AXP20x MFD parent (`struct axp20x_dev`), regmap, OF match data, pinctrl, pinmux, pinconf DT map helpers, and gpiolib. Compatible strings are `x-powers,axp209-gpio`, `x-powers,axp221-gpio`, and `x-powers,axp813-gpio`.

## Risks
AXP209 GPIO3 has a different bit layout, making it a likely source of regressions. `axp20x_group_pins` casts a pin descriptor address to `unsigned int *`, so pinctrl core expectations should be watched carefully. LDO mux intentionally does not program hardware; tests must distinguish this from a missing implementation. ADC support varies by descriptor mask and mux value. The probe info message always says "AXP209" even when matching AXP22x/AXP813.

## Test Signals
Expected test signals include PMIC child-device probe through MFD, pinctrl function enumeration for gpio_out/gpio_in/ldo/adc, GPIO read/write and direction for normal pins and GPIO3, pin range registration, rejection of ADC/LDO functions on unsupported pins, and no regulator state changes when selecting LDO mux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-axp209.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-bm1880.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-bm1880.c

## Purpose
This platform driver implements pinctrl, pinmux, and pinconf for the Bitmain BM1880 SoC. It describes 112 MIO pins, a large table of peripheral groups and functions, and packed MMIO register programming for mux selection, pull controls, Schmitt input, slew rate, and drive strength.

## Important APIs, Types, and Functions
`struct bm1880_pinctrl` stores MMIO base, pinctrl device, group table, function table, and per-pin drive-width data. `struct bm1880_pctrl_group` and `struct bm1880_pinmux_function` describe groups/functions. `struct bm1880_pinconf_data` holds the drive strength bit width per pin. The table macros are `BM1880_PINCTRL_GRP`, `BM1880_PINMUX_FUNCTION`, and `BM1880_PINCONF_DAT`. Operational callbacks include group accessors, `bm1880_pinmux_set_mux`, `bm1880_pinconf_drv_set`, `bm1880_pinconf_drv_get`, `bm1880_pinconf_cfg_get`, `bm1880_pinconf_cfg_set`, and `bm1880_pinconf_group_set`. Probe is `bm1880_pinctrl_probe`, registered at `arch_initcall`.

## Control Flow and State
Probe allocates state, maps the platform resource, binds static group/function/pinconf arrays, registers the static pinctrl descriptor, stores drvdata, and logs initialization. Muxing iterates each pin in the selected group; each register word covers two pins, so it calculates `offset = (pin >> 1) << 2` and per-pin mux field offset before clearing and writing a 2-bit selector. Pinconf reads/writes the same register word and uses macros to locate pull, drive, Schmitt, and slew fields for the selected pin. Group pinconf applies the same configs to all pins in the group.

## State and Persistence Behavior
All persistent state is in the BM1880 pinctrl MMIO register block at `BM1880_REG_MUX` plus per-pin offsets. Static tables are immutable. There is no explicit locking around relaxed read/modify/write sequences, so concurrent pinctrl operations could theoretically race if applied to different fields in the same word. Drive strength encoding supports two pin classes: 3-bit fields for 4-32 mA and 2-bit fields for 4-16 mA.

## Dependencies and Integration Points
The driver integrates with platform bus and OF compatible `bitmain,bm1880-pinctrl`, Linux pinctrl core, generic pinconf DT parsing, and pinctrl utils. It does not register a gpiochip; GPIO mode is represented as pinmux functions for pins that can be muxed to GPIO controllers elsewhere.

## Risks
The large hand-maintained static mapping tables are the primary risk. Any wrong pin number, group membership, mux value, or drive-width entry will produce board-level pin failures. `bm1880_pinconf_cfg_get` passes a boolean bit value into `bm1880_pinconf_drv_get`, which cannot recover multi-bit drive strength values for 3-bit fields, so drive-strength get appears lossy. Pull-up, pull-down, and bias-disable set paths only set bits and do not clear mutually exclusive fields, which relies on hardware semantics or may leave conflicting state. Relaxed unlocked RMW can lose adjacent-field updates.

## Test Signals
Validation should cover registration on BM1880 DT, muxing representative peripherals such as NAND, SDIO, Ethernet, I2C, UART, PWM, I2S, SPI, and GPIO groups, pinconf set/get for both drive-width classes, group pinconf propagation, and stress cases where two consumers update different fields in the same register word.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-bm1880.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-cy8c95x0.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-cy8c95x0.c

## Purpose
This I2C driver supports Cypress CY8C95x0 GPIO expander variants with 20, 40, or 60 pins. It provides gpiolib, pinctrl, pinmux between GPIO and PWM, generic pinconf drive/bias/output/input controls, optional reset and regulator handling, ACPI/DMI IRQ quirks, regmap-backed access to paged registers, and nested interrupt delivery.

## Important APIs, Types, and Functions
`struct cy8c95x0_pinctrl` is the central state: regmap, IRQ and I2C mutexes, interrupt trigger/mask bitmaps, push-pull bitmap, hardware pin map bitmap, port count, gpio chip, pinctrl descriptor, total pin count, and reset GPIO. Register helper families include `cy8c95x0_regmap_update_bits_base`, `cy8c95x0_regmap_write_bits`, `cy8c95x0_regmap_update_bits`, `cy8c95x0_regmap_read_bits`, plus bitmap multi-register helpers `cy8c95x0_write_regs_mask` and `cy8c95x0_read_regs_mask`. GPIO callbacks cover direction, value, multiple get/set, pin ranges, and pinconf. IRQ callbacks include mask/unmask, bus lock/sync, type, shutdown, `cy8c95x0_irq_pending`, and `cy8c95x0_irq_handler`. Probe and detection are `cy8c95x0_probe` and `cy8c95x0_detect`.

## Control Flow and State
Probe allocates state, derives pin count from match data, configures a runtime regmap range sized for the variant, enables `vdd`, toggles optional reset, initializes regmap, clears the push-pull bitmap, builds a bitmap map that skips the four-bit gap in GPort2, initializes the I2C mutex, applies the Galileo ACPI IRQ quirk if matched, optionally initializes IRQ handling, registers pinctrl, and registers the gpiochip. Regmap virtual ranges map muxed registers behind `PORTSEL` into a flat address space; accessors serialize I2C and translate direct, quick-path, and muxed registers. Write-clear drive mode registers update regcache manually to mirror hardware clearing of conflicting modes.

## State and Persistence Behavior
Persistent hardware state is in direct and port-selected CY8C95x0 registers. Driver-side persistent state includes regcache, IRQ masks and trigger bitmaps, the `push_pull` bitmap used to force High-Z when returning push-pull pins to input, and the `map` bitmap used for scatter/gather around the GPort2 gap. IRQ bus sync writes the mask bitmap, forces newly unmasked IRQ lines to input, and unlocks. Level IRQ emulation loops nested IRQ handling while the GPIO remains active.

## Dependencies and Integration Points
The driver integrates with I2C, SMBus detection, regmap ranges/cache, regulator, optional reset GPIO, ACPI, DMI, OF, gpiolib, pinctrl, pinmux, pinconf, and IRQ domains. Compatible strings include `cypress,cy8c9520`, `cypress,cy8c9540`, and `cypress,cy8c9560`; ACPI ID `INT3490` maps to 40 pins.

## Risks
Paged register handling is complex; direct `PORTSEL` writes outside the helpers would desynchronize cache and hardware. Interrupt status registers are precious, so debug or cache reads can clear events. Level-trigger emulation uses while loops that can spin if the input remains asserted and nested handlers do not clear the source. `cy8c95x0_gpio_get_value` returns 0 on read error after logging elsewhere, which can hide I2C failures. The GPort2 gap requires every multi-line bitmap path to use scatter/gather correctly.

## Test Signals
Tests should cover all variants and pin counts, regmap range sizing, reset/regulator sequencing, GPIO single and multiple operations across the GPort2 gap, PWM muxing side effects, pinconf drive/bias/input/output state including push-pull-to-input High-Z behavior, IRQ edge and level delivery, ACPI Galileo IRQ mapping, and SMBus detect names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-cy8c95x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-da850-pupd.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-da850-pupd.c

## Purpose
This small platform driver exposes pull-up and pull-down configuration groups for TI DA850/OMAP-L138/AM18xx hardware. It is a pinconf-only pinctrl provider for 32 named control points `cp0` through `cp31`.

## Important APIs, Types, and Functions
`struct da850_pupd_data` stores the MMIO base, pinctrl descriptor, and pinctrl device. Register offsets are `DA850_PUPD_ENA` and `DA850_PUPD_SEL`. Pinctrl callbacks return the group count, group name, and no concrete pins because these are configuration groups rather than normal pin lists. Pinconf callbacks are `da850_pupd_pin_config_group_get` and `da850_pupd_pin_config_group_set`. Probe is `da850_pupd_probe`.

## Control Flow and State
Probe allocates state, maps the single resource, fills the pinctrl descriptor with group DT mapping and generic pinconf ops, registers pinctrl, and stores drvdata. Config get reads enable state first; disabled bias reports argument 1 for `BIAS_DISABLE`, while pull-up/down checks both enable and selection registers. Config set reads current enable/select values, folds each requested config into local copies, writes selection first, then writes enable.

## State and Persistence Behavior
Persistent state is two MMIO registers. `DA850_PUPD_ENA` controls whether bias is enabled for each group and `DA850_PUPD_SEL` selects pull-up versus pull-down. There is no locking around read/modify/write, so concurrent group config updates may race if multiple consumers configure separate groups at the same time.

## Dependencies and Integration Points
The driver integrates with platform bus, OF compatible `ti,da850-pupd`, pinctrl group DT mapping, and generic pinconf. It does not expose GPIO or pinmux behavior.

## Risks
No concrete pin list is returned for groups, which is intentional but makes debug output less informative. RMW without locking can lose updates. Unsupported pinconf parameters return `-EINVAL`, so board DT must use only `bias-disable`, `bias-pull-up`, or `bias-pull-down`.

## Test Signals
Validation should include DT group mapping for all `cpN` names, set/get of disable, pull-up, and pull-down, readback of both registers, and concurrent configuration stress if multiple consumers can touch this block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-da850-pupd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-da9062.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-da9062.c

## Purpose
This platform driver exposes the five DA9062 PMIC GPIO pins through gpiolib and limited generic pin configuration. Despite the filename and description mentioning pinctrl, the current implementation registers only a gpiochip; pinmux/pinctrl alternate-mode support is left as a TODO.

## Important APIs, Types, and Functions
`struct da9062_pctl` stores the parent `struct da9062`, a gpiochip, and desired output pin modes in `pin_config`. Mode helpers are `da9062_pctl_get_pin_mode` and `da9062_pctl_set_pin_mode`. GPIO callbacks are `da9062_gpio_get`, `da9062_gpio_set`, `da9062_gpio_get_direction`, `da9062_gpio_direction_input`, `da9062_gpio_direction_output`, `da9062_gpio_set_config`, and `da9062_gpio_to_irq`. Probe is `da9062_pctl_probe`.

## Control Flow and State
Probe sets the child device firmware node to the parent, allocates state, gets parent drvdata, exits successfully without registering GPIO when the parent lacks `gpio-controller`, initializes all desired output modes to push-pull, copies a template gpiochip, fills label and parent, stores drvdata, and registers the gpiochip. Direction input writes GPI mode and programs active-high/active-low type bits according to the gpiod descriptor. Direction output restores the saved output mode from `pin_config` and then writes the output level. Set-config validates PMIC restrictions: pull-down only in input mode and pull-up only in open-drain output mode.

## State and Persistence Behavior
Hardware state lives in DA9062 regmap registers for GPIO mode, status, output level, config, and IRQ mapping. Driver-side `pin_config[]` persists the selected output drive mode so a later direction-output operation can restore open-drain or push-pull instead of always using one mode. The gpiochip is sleeping because all operations go through PMIC regmap I/O.

## Dependencies and Integration Points
The driver depends on the DA9062 MFD parent, regmap, DA9062 register definitions, gpiolib, GPIO descriptors, property APIs, and regmap IRQ mapping. Compatible string is `dlg,da9062-gpio`; platform alias is `da9062-gpio`.

## Risks
No pinctrl device is registered, so consumers expecting pinctrl states from this file will not get them. `da9062_gpio_set` shifts raw `value` into the bit position without boolean normalization, so callers should pass normal 0/1 values as gpiolib does. Bias configuration depends on current mode and can return `-ENOTSUPP` when called in the wrong order. Alternate mode returns `-ENOTSUPP` for get/direction.

## Test Signals
Tests should cover probe with and without parent `gpio-controller`, input and output direction transitions, open-drain/push-pull set_config persistence through direction_output, active-low input type programming, GPIO get from status versus output registers, and `to_irq` mapping for all five GPI IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-da9062.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-digicolor.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-digicolor.c

## Purpose
This built-in platform driver supports the Conexant Digicolor CX92755 general-purpose pin mapping block. It exposes 144 pins as one-pin pinctrl groups, supports muxing each pin between GPIO and three client functions, and registers a simple MMIO gpiochip.

## Important APIs, Types, and Functions
`struct dc_pinmap` stores MMIO base, device, pinctrl device and descriptor, generated pin names, gpiochip, and spinlock. Register macros derive client select, drive, output, and input offsets per 8-pin collection. Pinctrl callbacks expose one group per pin. Pinmux callbacks include `dc_get_functions_count`, `dc_get_fname`, `dc_get_groups`, `dc_set_mux`, and `dc_pmx_request_gpio`. GPIO callbacks include direction input/output, get, set, and `dc_gpiochip_add`. Probe is `dc_pinctrl_probe`.

## Control Flow and State
Probe maps the MMIO resource, allocates pin descriptors and names, generates names `GP_A0` through `GP_R7`, fills the pinctrl descriptor, registers pinctrl, then adds the gpiochip and pin range. Mux setup uses `dc_client_sel` to find a 2-bit field in a client-select register and writes the selected function. GPIO request checks that the mux field is zero before allowing GPIO. Direction and output operations update per-collection drive and output registers under a spinlock; input reads the input register directly.

## State and Persistence Behavior
Persistent state is in memory-mapped Digicolor registers. The spinlock protects drive/output RMW operations but not mux RMW operations, so concurrent mux changes could race. Pin names and descriptors are devm-managed for the lifetime of the platform device. No IRQ or pinconf state is implemented.

## Dependencies and Integration Points
The driver integrates with platform bus, OF compatible `cnxt,cx92755-pinctrl`, pinctrl, pinmux, pinctrl utils, and gpiolib. It is registered with `builtin_platform_driver`, so it is built-in rather than module-loaded.

## Risks
The TODOs explicitly call out missing GPIO interrupt support and pad configuration. `dc_set_mux` lacks locking around client-select RMW. `dc_pmx_request_gpio` only checks mux state and does not switch to GPIO itself. All functions list all groups, so invalid board-level combinations are not filtered by the driver.

## Test Signals
Runtime tests should verify 144 generated pin names, mux field programming for all four functions, GPIO request rejection when a pin is muxed to a client, direction/value behavior per collection, pin range registration, and absence of unexpected pinconf/IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-digicolor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-eic7700.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-eic7700.c

## Purpose
This platform driver implements pinctrl, pinmux, and pinconf for the ESWIN EIC7700 SoC. It describes 164 pins, per-pin function slots, generic pin configuration fields, GPIO request/direction integration, and a probe-time RGMII voltage mode setup derived from a `vrgmii` regulator.

## Important APIs, Types, and Functions
`struct eic7700_pin` stores up to eight function selectors per pin. `struct eic7700_pinctrl` stores MMIO base, pinctrl descriptor, and a flexible array of `struct pinfunction` records. Register fields include input enable, pull-up/down, drive strength, Schmitt trigger, and function select in each per-pin 32-bit word. Key callbacks are group accessors, `eic7700_pin_config_get`, `eic7700_pin_config_set`, `eic7700_set_mux`, `eic7700_gpio_request_enable`, `eic7700_gpio_disable_free`, `eic7700_gpio_set_direction`, `eic7700_pinctrl_init_function_groups`, and `eic7700_pinctrl_probe`.

## Control Flow and State
Probe allocates state sized for all functions, maps MMIO, obtains `vrgmii`, reads its voltage, programs both RGMII mode registers for 1.8 V or 3.3 V, fills the pinctrl descriptor, builds function-to-group membership by scanning every pin's function slots, registers and initializes pinctrl, then enables it. Muxing validates that the requested function appears in the selected pin's function slot array, then writes that slot index to the `FUNC_SEL` field. GPIO request selects `F_GPIO`; GPIO free tries to select `F_DISABLED`; GPIO direction toggles the input-enable bit.

## State and Persistence Behavior
All hardware state is MMIO and arranged as one register per pin plus separate RGMII mode registers. Function group arrays are generated once at probe and devm-managed. Pinconf get returns `-EINVAL` when a supported boolean config is currently false, matching common generic-pinconf conventions. Drive strength encoding differs for RGMII/LPDDR reference clock pins versus other pins.

## Dependencies and Integration Points
The driver depends on platform bus, OF compatible `eswin,eic7700-pinctrl`, regulator framework, MMIO helpers, pinctrl, pinmux, and generic pinconf. It does not register a gpiochip; GPIO operation is through pinmux hooks used by a GPIO controller integration.

## Risks
The static per-pin function table is large and board-critical. `eic7700_gpio_disable_free` calls `eic7700_set_mux` with `F_DISABLED`, but many pins do not list disabled as a valid slot, so free can log errors or fail silently through a void callback. The driver accepts only exactly 1.8 V or 3.3 V for `vrgmii`; regulator rounding or unavailable voltage causes probe failure. Relaxed unlocked RMW on per-pin registers can race with concurrent pinconf/mux operations.

## Test Signals
Tests should validate regulator-voltage-dependent RGMII mode writes, pinctrl registration and `pinctrl_enable`, function group counts for each selector, valid and invalid mux requests, GPIO request/free on pins with and without disabled slots, pinconf get/set for bias, drive strength, input enable, and Schmitt, and DT states for major peripherals such as RGMII, I2C, UART, SPI, SDIO, PWM, MIPI CSI, and USB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-eic7700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ep93xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ep93xx.c

## Purpose
This auxiliary driver implements a group-only pinmux controller for Cirrus EP93xx SoC variants. It exposes package-specific pin lists and mux groups for EP9301/9302, EP9307, and EP9312/EP9315 models, and programs the shared Syscon `DeviceCfg` register through the EP93xx auxiliary regmap device.

## Important APIs, Types, and Functions
`struct ep93xx_pmx` stores device, pinctrl device, auxiliary regmap device, regmap, and model. `struct ep93xx_pin_group` wraps a `struct pingroup` with a `DeviceCfg` mask/value pair. Static pin tables describe package pins for the three models. Group arrays use `PMX_GROUP` to map named groups to pin arrays and bit programming. Pinctrl callbacks are model-switching group count/name/pin accessors. Pinmux callbacks use `ep93xx_pmx_functions` and `ep93xx_pmx_set_mux`. Probe is `ep93xx_pmx_probe`; registration uses `module_auxiliary_driver`.

## Control Flow and State
The auxiliary ID selects the EP93xx model. Probe allocates state, stores the parent regmap and update callback, switches the global pinctrl descriptor to the matching pin table and pin count, sets the child firmware node to the parent node for pinctrl lookup, and registers pinctrl. Setting mux chooses the model-specific group entry, writes the group's mask/value to `EP93XX_SYSCON_DEVCFG` using the auxiliary locked update function, then reads back the register and compares changed pad bits against the expected result. Any mismatch is logged as a probable hardware limitation and returns `-EINVAL`.

## State and Persistence Behavior
Persistent state is the shared EP93xx `DeviceCfg` register. The driver itself stores only model selection and pointers. Because `ep93xx_pmx_desc` is a static global mutated at probe with model-specific pins/npins, it assumes only one compatible auxiliary instance or no conflicting concurrent probes. Register updates are serialized by the auxiliary device's `update_bits` helper and lock, not by this driver.

## Dependencies and Integration Points
The driver integrates with the EP93xx SoC auxiliary-device framework (`soc_ep93xx.pinctrl-*` IDs), `struct ep93xx_regmap_adev`, syscon/regmap, pinctrl, pinmux, generic DT mapping, and pinctrl utils. It provides mux functions such as spi, ac97, i2s, pwm, keypad, pata, lcd, and gpio depending on group support.

## Risks
Large static package pin tables and model-specific group masks are easy to desynchronize from hardware docs. The static mutable descriptor can be unsafe if multiple model instances exist. Some group definitions in the EP9307 section reference `ac97_ep9301_pins` for `i2s_on_ac97`, which deserves scrutiny. Hardware may reject writes to some DeviceCfg bits; the readback check catches this but means mux requests can fail at runtime.

## Test Signals
Validation should cover auxiliary probe for each model ID, pin count and group enumeration per model, every function-to-group mapping, successful and failing `DeviceCfg` readback verification, parent firmware-node matching for DT pinctrl states, and board boot tests for SPI/AC97/I2S/PWM/keypad/PATA/LCD/GPIO muxes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ep93xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-equilibrium.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-equilibrium.c

## Purpose
This platform driver implements Intel LGM/Equilibrium SoC pinctrl, pinmux, pinconf, GPIO, and GPIO IRQ support. Unlike table-only SoC drivers, it discovers GPIO child nodes and pin groups/functions from firmware, builds generic pinctrl groups/functions dynamically, and registers generic gpiochips for each bank.

## Important APIs, Types, and Functions
The driver uses private types from `pinctrl-equilibrium.h`: pin banks, GPIO controllers, IRQ type descriptors, and driver data. IRQ helpers include mask/unmask/ack/mask_ack, `eqbr_irq_set_type`, and `eqbr_irq_handler`. GPIO setup is split across `gpiochip_setup` and `gpiolib_reg`. Pinctrl and mux helpers include `find_pinbank_via_pin`, `eqbr_set_pin_mux`, `eqbr_pinmux_set_mux`, and `eqbr_pinmux_gpio_request`. Pinconf is handled by `eqbr_pinconf_get`, `eqbr_pinconf_set`, and group wrappers. Dynamic DT construction uses `funcs_utils`, `eqbr_build_functions`, and `eqbr_build_groups`. Discovery/registration paths are `pinbank_init`, `pinbank_probe`, `pinctrl_reg`, and `eqbr_pinctrl_probe`.

## Control Flow and State
Probe allocates driver data, maps the parent pinctrl MMIO resource, discovers available GPIO nodes named `gpio`, initializes pin banks from each node's `gpio-ranges` and `REG_AVAIL`, registers the pinctrl device, builds groups from child node `groups`, `pins`, and `pinmux` properties, builds functions from child node `function` properties, enables pinctrl, registers each gpiochip, and stores drvdata. Muxing resolves each pin to a bank, validates availability using `aval_pinmap`, and writes the mux value to the per-pin register. GPIO request forces mux value `EQBR_GPIO_MODE`.

## State and Persistence Behavior
Pinctrl state persists in parent pinpad registers spaced by `PAD_REG_OFF`; GPIO state persists in each child GPIO MMIO block. Driver state records bank base pins, bank widths, availability bitmaps, GPIO controller mappings, and fwnodes. Raw spinlocks protect pinpad and GPIO register writes. Pinconf supports pull-up, pull-down, open-drain, drive strength, slew rate, and output enable. Output-enable pinconf delegates to the associated gpiochip direction-output callback.

## Dependencies and Integration Points
The driver depends on OF child nodes, `gpio-ranges`, MMIO resources, IRQ mapping, generic gpio-chip helpers, pinctrl generic group/function APIs, pinmux generic APIs, pinconf DT mapping, and compatible `intel,lgm-io`. GPIO child nodes can opt into interrupt-controller behavior.

## Risks
`pinbank_probe` ignores the return value from `pinbank_init`, so a malformed GPIO child can leave partially initialized bank data and fail later less clearly. It iterates all available nodes named `gpio` globally rather than restricting to children of the pinctrl node, which can over-count unrelated GPIO nodes in a broader DT. `eqbr_pinmux_set_mux` does not propagate errors from `eqbr_set_pin_mux` inside its loop. Group/function parsing stores property value pointers as names and assumes property lifetimes remain valid. Drive-strength set masks two-bit values but does not validate the requested argument range.

## Test Signals
Validation should include DTs with multiple GPIO child banks, correct `gpio-ranges`, unavailable pins in `REG_AVAIL`, dynamic group/function construction from child properties, GPIO request muxing, pinconf read/write for all supported configs, GPIO direction/output behavior through generic chips, chained IRQ delivery for edge and level types, and malformed DT cases for missing ranges or bad pin IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-equilibrium.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-equilibrium.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-equilibrium.h

## Purpose
This private header defines the register offsets, constants, and shared data structures used by the Equilibrium/LGM pinctrl implementation. It is tightly coupled to `pinctrl-equilibrium.c` and describes both the pinpad register block and per-bank GPIO register block.

## Important APIs, Types, and Definitions
Pinpad offsets include mux base, pull-up/down enable, slew, drive-current registers, open-drain, and availability. GPIO offsets include input/output, direction, external interrupt control, interrupt capture/control/enable/configuration, and set/clear direction/output registers. Constants define drive-current packing, GPIO interrupt trigger encodings, and `EQBR_GPIO_MODE`. `funcs_util_ops` enumerates phases of dynamic function construction. Structs are `gpio_irq_type`, `eqbr_pin_bank`, `eqbr_gpio_ctrl`, and `eqbr_pinctrl_drv_data`.

## Control Flow and State
The header contains no executable control flow. It defines the state layout consumed by the C file. `eqbr_pin_bank` persists per-bank pinpad base, ID, global pin base, pin count, and availability bitmap. `eqbr_gpio_ctrl` connects a generic gpiochip to a firmware node, pin bank, GPIO MMIO base, parent IRQ, and raw spinlock. `eqbr_pinctrl_drv_data` aggregates the pinctrl descriptor/device, parent base, bank array, GPIO controller array, and pinpad lock.

## Dependencies and Integration Points
The header assumes Linux kernel types from gpio, pinctrl, fwnode, and I/O headers included by the C file. It is not a public UAPI. The register macros are used directly by IRQ, GPIO, mux, pinconf, and bank-discovery paths in `pinctrl-equilibrium.c`.

## Risks
Because register offsets and structure fields are shared across all Equilibrium operations, any incorrect offset affects muxing, pad configuration, GPIO, and IRQ behavior. `PARSE_DRV_CURRENT` assumes two bits per pin and must stay aligned with `DRV_CUR_PINS` and `REG_DRCC`. Comments contain minor typos but no semantic issue. Structure layout changes must remain synchronized with generic gpiochip and pinctrl registration code.

## Test Signals
The header is validated indirectly by building and running `pinctrl-equilibrium.c`. Useful signals include correct pin bank discovery, availability bitmap enforcement, pinconf drive-current get/set, GPIO generic chip operation, IRQ trigger programming, and no sparse/compiler warnings for type use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-equilibrium.h -->
