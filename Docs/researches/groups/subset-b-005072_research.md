# subset-b-005072 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-keembay.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-keembay.c

## Purpose
Implements the Intel Keem Bay SoC pinctrl, pinmux, pin configuration, GPIO, and GPIO IRQ controller. The driver exposes each SoC pin as a one-pin group, builds functions dynamically from the per-pin mux table, programs GPIO mode registers, and bridges up to eight parent interrupt sources into Linux GPIO IRQs.

## Important APIs, Types, and Functions
Key types are `struct keembay_pinctrl`, `struct keembay_mux_desc`, `struct keembay_gpio_irq`, and `struct keembay_pinfunction`. Registration flows through `keembay_pinctrl_probe`, `keembay_pinctrl_reg`, `keembay_build_groups`, `keembay_build_functions`, and `keembay_gpiochip_probe`. Runtime operations are implemented by `keembay_set_mux`, `keembay_request_gpio`, `keembay_pinconf_get`, `keembay_pinconf_set`, `keembay_gpio_get`, `keembay_gpio_set`, direction helpers, `keembay_gpio_irq_handler`, `keembay_gpio_irq_enable`, `keembay_gpio_irq_disable`, and `keembay_gpio_irq_set_type`.

## Control Flow and State
Probe maps two MMIO resources, initializes a raw spinlock, registers pinctrl, derives pin groups and function descriptors from `keembay_pins`, then registers a `gpio_chip` with chained IRQ parents discovered via `platform_get_irq_optional`. Pinmux writes the selected mux mode into `KEEMBAY_GPIO_MODE_SELECT_MASK`; pinconf read-modify-writes pull, drive strength, slew, and Schmitt bits in per-pin mode registers. GPIO values use grouped data registers for input, output, high, and low writes. IRQ state is split between hardware `INT_CFG` slots and software `kpc->irq[]`, `max_gpios_level_type`, and `max_gpios_edge_type`; falling/low trigger support is emulated by input inversion because the IP only supports rising/high semantics directly.

## Dependencies and Integration Points
Depends on Linux pinctrl generic group/function helpers, generic pinconf DT parsing, gpiolib, hierarchical/chained IRQ support, MMIO accessors, OF matching for `intel,keembay-pinctrl`, and platform IRQ/resource discovery. The GPIO range ties GPIO offsets back to the pin controller, and client DT nodes use the generated function/group names from the Keem Bay mux table.

## Risks and Test Signals
Important risks are slot accounting bugs across the eight IRQ sources, mishandling of low/falling emulation through inversion, read-modify-write races outside the raw spinlock, wrong `ngpios` values relative to the static pin table, and dynamic function grouping errors when the same function name appears on many pins. Test signals include pinmux state in debugfs, GPIO direction/value tests across 32-bit register boundaries, pull/drive/slew/Schmitt pinconf reads after writes, IRQ tests for rising/falling/high/low requests, and probe coverage with missing or partial parent IRQ resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-keembay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lantiq.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lantiq.c

## Purpose
Provides the common Lantiq pinctrl/pinmux core used by SoC-specific Lantiq pad-controller drivers. It handles pin groups, mux function exposure, legacy Lantiq DT map parsing, and dispatches actual mux programming to a SoC callback.

## Important APIs, Types, and Functions
The public entry point is `ltq_pinctrl_register`. Pinctrl ops are implemented by `ltq_get_group_count`, `ltq_get_group_name`, `ltq_get_group_pins`, `ltq_pinctrl_dt_node_to_map`, and `ltq_pinctrl_dt_free_map`. Pinmux ops are `ltq_pmx_func_count`, `ltq_pmx_func_name`, `ltq_pmx_get_groups`, `ltq_pmx_set`, and `ltq_pmx_gpio_request_enable`. Validation helpers include `match_mux`, `match_mfp`, and `match_group_mux`.

## Control Flow and State
SoC drivers fill `struct ltq_pinmux_info` and call `ltq_pinctrl_register`, which installs common ops into the supplied descriptor and registers pinctrl. DT parsing walks child nodes, accepts either `lantiq,pins` or `lantiq,groups`, creates mux maps when `lantiq,function` is present, and packs configured Lantiq pinconf properties with `LTQ_PINCONF_PACK`. Mux setting validates that every pin in a group supports the requested mux value, translates logical pins to MFP table entries, then calls `info->apply_mux` per pin.

## Dependencies and Integration Points
Integrates with Lantiq SoC drivers that provide pads, MFP tables, groups, function lists, optional config parameters, memory bases, clocks, external interrupt mappings, and the `apply_mux` callback. It depends on OF properties with `lantiq,*` names, pinctrl core APIs, and dynamic allocation for generated pinctrl maps.

## Risks and Test Signals
Risks include malformed DT nodes producing too few or too many maps, missing allocation checks for per-map config copies, non-linear MFP table lookup mistakes, mux/group table drift in SoC-specific data, and function/group selector bounds assumptions. Test signals are DT parsing for pin-only, group-only, mux-only, and config-only nodes; GPIO request fallback to mux 0; invalid mux diagnostics; and boot tests on each Lantiq SoC using this common layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lantiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lantiq.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lantiq.h

## Purpose
Defines the shared data contract for Lantiq pinctrl implementations: pinconf encodings, multifunction pin descriptors, group/function tables, SoC registration metadata, and the common registration prototype.

## Important APIs, Types, and Functions
Important definitions include `LTQ_MAX_MUX`, `MFPR_FUNC_MASK`, `LTQ_PINCONF_PACK`, `LTQ_PINCONF_UNPACK_PARAM`, and `LTQ_PINCONF_UNPACK_ARG`. Main types are `enum ltq_pinconf_param`, `struct ltq_cfg_param`, `struct ltq_mfp_pin`, `struct ltq_pin_group`, `struct ltq_pmx_func`, and `struct ltq_pinmux_info`. The header also enumerates GPIO pins `GPIO0` through `GPIO88` and declares `ltq_pinctrl_register`.

## Control Flow and State
There is no runtime flow in this header. It declares the persistent state that SoC drivers pass to the common core: pad descriptors, MFP mux capabilities, groups, functions, DT-readable config parameters, external interrupt maps, up to five MMIO bases and clocks, and a callback for applying mux values to hardware.

## Dependencies and Integration Points
Includes Linux pinctrl consumer, machine, pinconf, pinctrl, and pinmux headers plus local `core.h`. It is consumed by `pinctrl-lantiq.c` and by Lantiq SoC-specific pinctrl drivers that populate `struct ltq_pinmux_info`.

## Risks and Test Signals
Because this is a shared ABI inside the driver family, wrong struct fields or pinconf packing break all Lantiq variants. Risks include mismatch between `LTQ_MAX_MUX` and SoC tables, pin enum drift, and callback signature changes. Test signals are compile coverage for every Lantiq pinctrl user and boot-time mux/config application on representative boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lantiq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-loongson2.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-loongson2.c

## Purpose
Implements the Loongson2/LS2K pinmux controller. It exposes SoC pins and peripheral groups, then switches each group between GPIO and peripheral function by setting or clearing a single bit in a mux register.

## Important APIs, Types, and Functions
Key structures are `struct loongson2_pinctrl`, `struct loongson2_pmx_group`, and `struct loongson2_pmx_func`. Static data includes `loongson2_pctrl_pins`, group pin arrays for SDIO, CAN, PWM, I2C, NAND, SATA LED, I2S, and HDA, `loongson2_pmx_groups`, and `loongson2_pmx_functions`. Pinctrl and pinmux callbacks include `loongson2_get_groups_count`, `loongson2_get_group_name`, `loongson2_get_group_pins`, `loongson2_pmx_set_mux`, and function enumeration helpers.

## Control Flow and State
Probe allocates controller state, maps one MMIO resource, initializes a spinlock, fills a `pinctrl_desc`, and registers pinctrl. `loongson2_pmx_set_mux` looks up the selected group register offset and bit, locks, reads the register, clears the bit for function selector 0 (`gpio`) or sets it for peripheral functions, writes it back, and unlocks. Persistent state is the hardware mux register; the driver keeps no software cache beyond static group metadata.

## Dependencies and Integration Points
Depends on platform resources, OF compatible `loongson,ls2k-pinctrl`, pinctrl generic DT map helpers, local `pinctrl-utils.h`, and MMIO locking through `spin_lock_irqsave`. The driver is registered at `arch_initcall`, making mux control available early for Loongson platform devices.

## Risks and Test Signals
Risks include table consistency issues between pin descriptors and group arrays, single-bit mux assumptions for groups sharing pins, selector semantics where any nonzero function sets the bit, and pin array typos affecting GPIO group coverage. Test signals include debugfs group/function listings, readback of the mux register after selecting GPIO and peripheral states, boot tests for SDIO/I2C/NAND/audio consumers, and compile/DT binding coverage for LS2K boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-loongson2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lpc18xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lpc18xx.c

## Purpose
Implements the NXP LPC18xx/LPC43xx System Control Unit pin controller. It covers a large static pin/function table, pin muxing, analog ADC/DAC enable paths, USB1 and I2C0 special pins, generic pin configuration, and routing GPIO pins to the LPC GPIO pin interrupt selector.

## Important APIs, Types, and Functions
Core types are `struct lpc18xx_scu_data`, `struct lpc18xx_pmx_func`, and `struct lpc18xx_pin_caps`. Static tables define function IDs, function names, per-pin capability records, and `lpc18xx_pins`. Pinconf helpers include `lpc18xx_pconf_get`, `lpc18xx_pconf_set`, `lpc18xx_pconf_get_pin`, `lpc18xx_pconf_set_pin`, `lpc18xx_pconf_get_usb1`, `lpc18xx_pconf_set_usb1`, `lpc18xx_pconf_get_i2c0`, `lpc18xx_pconf_set_i2c0`, and GPIO interrupt selector helpers. Pinmux is handled by `lpc18xx_pmx_set`, and function-to-group maps are built by `lpc18xx_create_group_func_map`.

## Control Flow and State
Probe maps the SCU MMIO resource, obtains and enables the input clock, builds per-function group lists by scanning every pin capability, and registers a built-in platform pinctrl driver. Normal muxing finds the function index within the selected pin capability and writes it into `LPC18XX_SCU_PIN_MODE_MASK`. ADC/DAC functions first write analog-safe pin config and then set ENAIO registers. USB1 and I2C0 pins bypass normal muxing and use special register layouts for power, pull-down, input, slew, glitch filter, and Schmitt settings. Pinconf performs one read of the pin register, applies all requested configs to a local value, and writes once at the end except GPIO pin interrupt routing, which writes PINTSEL registers directly.

## Dependencies and Integration Points
Depends on the platform clock framework, MMIO, pinctrl generic DT parsing for per-pin maps, custom pinconf parameter `nxp,gpio-pin-interrupt`, and GPIO ranges to translate SCU pins to GPIO numbers for PINTSEL routing. The driver binds `nxp,lpc1850-scu` and is built in with `builtin_platform_driver`, so the clock remains enabled for the lifetime of the system.

## Risks and Test Signals
Risks include mistakes in the dense datasheet-derived pin table, special-case divergence for USB1/I2C0/analog pins, unsupported drive-strength or slew requests being accepted on the wrong pin type, PINTSEL bitfield mistakes, and no remove path to disable the clock. Test signals include per-function debugfs group membership, mux attempts for invalid functions producing `-EINVAL`, ADC/DAC enable register readback, pinconf get-after-set for pull/input/slew/Schmitt/drive strength, GPIO interrupt routing for all eight PINTSEL slots, and board boot tests for LPC18xx/LPC43xx peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lpc18xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-max7360.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-max7360.c

## Purpose
Provides pinctrl/pinmux support for the MAX7360 MFD GPIO ports. It exposes eight port pins plus a two-pin rotary group and controls whether ports 6/7 are assigned to the rotary encoder function.

## Important APIs, Types, and Functions
The state container is `struct max7360_pinctrl`. Static data includes `max7360_pins`, single-port groups, `rotary_pins`, `max7360_groups`, and `max7360_functions` for `gpio`, `pwm`, and `rotary`. Pinctrl callbacks enumerate groups, and pinmux callbacks include `max7360_get_functions_count`, `max7360_get_function_name`, `max7360_get_function_groups`, and `max7360_set_mux`.

## Control Flow and State
Probe obtains the parent MFD regmap, allocates state, fills a `pinctrl_desc`, reuses the parent OF node for pinctrl phandles, and registers the controller. `max7360_set_mux` treats GPIO and PWM as equivalent for pinctrl purposes, only touching hardware when a group starts at port 6 or 7; selecting `rotary` sets `MAX7360_GPIO_CFG_RTR_EN`, while selecting other functions clears it. Persistent state is the parent regmap's `MAX7360_REG_GPIOCFG` bit.

## Dependencies and Integration Points
Depends on the MAX7360 MFD parent, `linux/mfd/max7360.h` register definitions, the parent regmap, platform-device MFD topology, and pinctrl generic OF parsing. `.strict = true` asks pinctrl to avoid conflicting mux/GPIO ownership.

## Risks and Test Signals
Risks include parent-node reuse confusing consumers if the MFD topology changes, GPIO/PWM equivalence hiding PWM ownership conflicts outside this driver, and rotary enable affecting both ports 6 and 7 as a pair. Test signals include selecting rotary and GPIO/PWM states through pinctrl, regmap readback of `MAX7360_GPIO_CFG_RTR_EN`, DT phandle resolution through the parent node, and integration tests with the MAX7360 GPIO/PWM/rotary users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-max7360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-max77620.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-max77620.c

## Purpose
Implements pinmux and pin configuration for MAX77620/MAX20024 PMIC GPIO pins. It selects alternate functions, configures pull-up/pull-down and drive mode, and stores flexible power sequencer settings for active and suspend states.

## Important APIs, Types, and Functions
Important types include `struct max77620_pctrl_info`, `struct max77620_pin_function`, `struct max77620_pingroup`, `struct max77620_pin_info`, and `struct max77620_fps_config`. Custom pinconf parameters map `maxim,active-fps-*` and `maxim,suspend-fps-*` properties. Runtime functions include `max77620_pinctrl_enable`, `max77620_pinconf_get`, `max77620_pinconf_set`, `max77620_get_default_fps`, `max77620_set_fps_param`, `max77620_pinctrl_suspend`, and `max77620_pinctrl_resume`.

## Control Flow and State
Probe inherits the parent firmware node, obtains the PMIC regmap from parent driver data, initializes FPS config caches to `-1`, fills static function/group metadata, and registers pinctrl. Mux setting writes one bit in `MAX77620_REG_AME_GPIO`, allowing GPIO mode or the one alternate function valid for the selected pin. Pinconf updates per-pin GPIO config registers for open-drain/push-pull, updates pull-up and pull-down registers as a mutually exclusive pair, and writes FPS source/power slot fields for GPIO1-GPIO3. Suspend/resume replay cached FPS settings from `fps_config[]`, switching between suspend and active values.

## Dependencies and Integration Points
Depends on the MAX77620 MFD parent, `linux/mfd/max77620.h` register definitions, regmap, platform device IDs `max77620-pinctrl` and `max20024-pinctrl`, generic pinconf DT parsing with custom properties, and PM sleep callbacks.

## Risks and Test Signals
Risks include cached drive type not reflecting hardware defaults until set, FPS cache values being skipped when left at `-1`, invalid FPS settings for pins outside GPIO1-GPIO3, alternate-function selector mismatches, and separate pull-up/pull-down writes leaving transient states on regmap errors. Test signals include muxing each GPIO to its legal alternate function, get-after-set for drive and pull configs, suspend/resume register readback for FPS fields, invalid-pin FPS tests, and PMIC GPIO consumers using both MAX77620 and MAX20024 IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-max77620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08.c

## Purpose
Provides the bus-independent core for Microchip MCP23x08/MCP23x17/MCP23x18 GPIO expanders. It implements GPIO operations, pull-up pinconf, optional nested IRQ controller support, regmap configuration, and shared probe setup used by I2C and SPI frontends.

## Important APIs, Types, and Functions
Exports `mcp23x08_regmap`, `mcp23x17_regmap`, and `mcp23s08_probe_one`. Internal helpers wrap regmap access through shifted addresses: `mcp_read`, `mcp_write`, `mcp_update_bits`, and `mcp_set_bit`. GPIO operations include `mcp23s08_direction_input`, `mcp23s08_direction_output`, `mcp23s08_get`, `mcp23s08_get_multiple`, `mcp23s08_set`, and `mcp23s08_set_multiple`. IRQ paths are handled by `mcp23s08_irq`, mask/unmask/type callbacks, bus lock/sync callbacks, and `mcp23s08_irq_setup`.

## Control Flow and State
`mcp23s08_probe_one` initializes the mutex, GPIO chip, optional reset GPIO, verifies and normalizes `IOCON`, applies IRQ polarity/mirror/open-drain properties, disables interrupts before registering nested IRQs, registers the GPIO chip, registers a small pinctrl device, then requests the parent threaded IRQ when present. GPIO direction and output state are persisted in `IODIR` and `OLAT`; pull-ups live in `GPPU`. The IRQ handler reads `INTF`, `INTCON`, `GPINTEN`, `DEFVAL`, `INTCAP`, and `GPIO`, updates `cached_gpio`, masks level interrupts while handling, and synthesizes nested child IRQs using cached previous GPIO state plus captured/current input values.

## Dependencies and Integration Points
Depends on regmap with cache disabled locking because `mcp->lock` serializes access, gpiolib, pinctrl pinconf, threaded IRQs, firmware properties `interrupt-controller`, `microchip,irq-active-high`, `microchip,irq-mirror`, and `drive-open-drain`, and the I2C/SPI frontends that allocate `struct mcp23s08` and initialize regmap.

## Risks and Test Signals
Risks include IRQ-clearing side effects when reading `GPIO`, cache-only IRQ bus locking mistakes, incorrect 8-bit versus 16-bit register shifting, level IRQ reactivation if GPINTEN is not restored, and `cached_gpio` drift after failed reads. Test signals include GPIO direction/value/multiple operations on 8- and 16-bit parts, pull-up pinconf set/get, IRQ tests for rising/falling/both/level modes, active-high/mirror/open-drain property combinations, regcache sync error injection, and both I2C and SPI probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08.h

## Purpose
Defines the shared interface and state structures for the MCP23S08/MCP230xx GPIO expander driver family, used by the common core and I2C/SPI transport frontends.

## Important APIs, Types, and Functions
Defines device type constants `MCP_TYPE_S08`, `MCP_TYPE_S17`, `MCP_TYPE_008`, `MCP_TYPE_017`, `MCP_TYPE_S18`, and `MCP_TYPE_018`. `struct mcp23s08_info` describes a variant's regmap config, label, type, GPIO count, and register shift. `struct mcp23s08` carries per-chip runtime state including address, IRQ polarity, rise/fall masks, parent IRQ, cached GPIO value, mutex, `gpio_chip`, regmap, pinctrl descriptor/device, and optional reset GPIO. It declares exported regmap configs and `mcp23s08_probe_one`.

## Control Flow and State
The header has no runtime control flow. It defines the state shared across transports and the core: bus frontends fill variant fields and regmap, while the core fills GPIO/pinctrl/IRQ callbacks and maintains cached state.

## Dependencies and Integration Points
Includes GPIO, IRQ, mutex, pinctrl, and type headers. It is included by `pinctrl-mcp23s08.c`, `pinctrl-mcp23s08_i2c.c`, and `pinctrl-mcp23s08_spi.c`, making it the contract between transport-specific probe code and common GPIO/pinctrl/IRQ behavior.

## Risks and Test Signals
Risks are interface drift between core and transports, wrong `reg_shift` or `ngpio` metadata per variant, and missing state initialization before `mcp23s08_probe_one`. Test signals are compile coverage for both transports, probing every listed variant, and runtime confirmation that 8-bit parts expose 8 pins while 16-bit parts expose 16 pins with correct register addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08_i2c.c

## Purpose
Implements the I2C transport frontend for MCP23008, MCP23017, and MCP23018 GPIO expanders, wiring I2C match data and regmap initialization into the shared MCP23S08 core.

## Important APIs, Types, and Functions
The main function is `mcp230xx_probe`. Variant descriptors are `mcp23008_i2c`, `mcp23017_i2c`, and `mcp23018_i2c`. Device matching is provided by `mcp230xx_id` and `mcp23s08_i2c_of_match`, including deprecated `mcp,*` compatibles. Driver lifecycle uses `mcp23s08_i2c_init` with `subsys_initcall` and `mcp23s08_i2c_exit`.

## Control Flow and State
Probe allocates one `struct mcp23s08`, retrieves I2C match data, copies variant GPIO count, label, and register-shift metadata into the chip, creates an I2C regmap, stores `client->irq`, names the pinctrl descriptor, and calls `mcp23s08_probe_one` with dynamic GPIO base `-1`. After successful common probe, it stores client data.

## Dependencies and Integration Points
Depends on I2C core matching, OF matching, `devm_regmap_init_i2c`, the shared header/core, and optional client IRQ wiring from board firmware. The `subsys_initcall` timing registers the driver before many consumers that may request expander GPIOs.

## Risks and Test Signals
Risks include missing/incorrect match data, wrong variant regmap config, deprecated compatible handling, and devices needing GPIOs before this subsys initcall runs. Test signals include I2C probe for all three variants, GPIO count and label validation, interrupt-controller operation via `client->irq`, and OF/module alias autoloading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08_spi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08_spi.c

## Purpose
Implements the SPI transport frontend for MCP23S08, MCP23S17, and MCP23S18 GPIO expanders. It supports up to eight addressed chips sharing one SPI chip select and instantiates the shared MCP23S08 core once per populated address.

## Important APIs, Types, and Functions
Key type is `struct mcp23s08_driver_data`, which stores per-address chip pointers and a flexible array of chip state. SPI regmap transport callbacks are `mcp23sxx_spi_write`, `mcp23sxx_spi_gather_write`, and `mcp23sxx_spi_read`, collected in `mcp23sxx_spi_regmap`. Probe helpers are `mcp23s08_spi_regmap_init` and `mcp23s08_probe`. Variant descriptors are `mcp23s08_spi`, `mcp23s17_spi`, and `mcp23s18_spi`.

## Control Flow and State
Probe reads `microchip,spi-present-mask` or deprecated `mcp,spi-present-mask`, validates it against eight possible addresses, allocates enough `struct mcp23s08` objects for populated chips, and iterates set bits. For each address it assigns the shared parent IRQ, creates a per-chip regmap config copy with a unique name, initializes SPI regmap with opcode/address handling, names the pinctrl descriptor, and calls `mcp23s08_probe_one` with hardware address `0x40 | (addr << 1)`. It accumulates total GPIO count in driver data.

## Dependencies and Integration Points
Depends on SPI core, custom regmap bus callbacks, firmware property parsing, shared MCP23S08 core, and match tables for SPI IDs and OF compatibles. Like the I2C frontend, it registers at `subsys_initcall` to make expander GPIOs available early.

## Risks and Test Signals
Risks include invalid present-mask handling, address/opcode mistakes in SPI reads and writes, shared parent IRQ behavior across multiple chips on one chip select, per-chip regmap name collisions, and sparse address population. Test signals include probing masks with one and multiple chips, SPI transfer traces for read/write/gather-write opcodes, GPIO and IRQ tests on each populated address, and validation for deprecated and current OF properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-microchip-sgpio.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-microchip-sgpio.c

## Purpose
Implements Microchip/Microsemi serial GPIO pinctrl and GPIO support for Luton, Ocelot, and Sparx5-family SoCs. It registers separate input and output banks, configures the serial bitstream and clock, maps two-cell port/bit GPIO specifiers to linear pins, and optionally exposes input-bank IRQs on Sparx5.

## Important APIs, Types, and Functions
Key types are `struct sgpio_properties`, `struct sgpio_priv`, `struct sgpio_bank`, and `struct sgpio_port_addr`. Hardware helpers include `sgpio_pin_to_addr`, `sgpio_addr_to_pin`, `sgpio_get_addr`, `sgpio_readl`, `sgpio_writel`, `sgpio_clrsetbits`, `sgpio_configure_bitstream`, `sgpio_configure_clock`, and `sgpio_single_shot`. GPIO/pinconf paths include `sgpio_output_set`, `sgpio_output_get`, `sgpio_input_get`, `sgpio_pinconf_get`, `sgpio_pinconf_set`, `microchip_sgpio_direction_input`, `microchip_sgpio_direction_output`, `microchip_sgpio_get_value`, and `microchip_sgpio_of_xlate`. IRQ logic is in `microchip_sgpio_irq_set_type`, mask/unmask/ack helpers, and `sgpio_irq_handler`.

## Control Flow and State
Probe resets the switch block if available, reads the input clock and desired bus frequency, creates an Ocelot regmap, reads enabled port ranges from `microchip,sgpio-port-ranges`, requires exactly two child banks, registers each bank as both pinctrl and gpiochip, validates matching bank sizes, then programs bitstream width, clock divider, clears all port config registers, and enables the selected ports. Output changes update a three-bit source field for the selected port/bit and trigger a single-shot burst on architectures that need manual refresh. Input values are read from `REG_INPUT_DATA` indexed by bit. IRQ state is hardware-resident in polarity, trigger, ack, enable, and ident registers and protected by a spinlock while reprogramming type.

## Dependencies and Integration Points
Depends on platform resources, clocks, optional reset controls, Ocelot regmap helper, firmware child nodes for input/output banks, generic pinconf DT parsing, gpiolib, and IRQ chaining for Sparx5. OF compatibles select architecture-specific register offsets and bitfield layouts: `microchip,sparx5-sgpio`, `mscc,luton-sgpio`, and `mscc,ocelot-sgpio`.

## Risks and Test Signals
Risks include architecture-specific bitfield mistakes, invalid port-range parsing, bank child ordering assumptions, output single-shot timeout at slow bus frequencies, off-by-one validation in OF GPIO translation, and IRQ enable/type races. Test signals include input/output bank registration with expected names and GPIO counts, GPIO specifier translation for boundary ports/bits, output readback plus visible serial update, clock divider validation, Sparx5 IRQ tests for rising/falling/both/high/low, and boot tests on all three architecture property sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-microchip-sgpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mlxbf3.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mlxbf3.c

## Purpose
Implements NVIDIA BlueField-3 pinctrl for 56 GPIO-capable pins. It switches pins between firmware/hardware control and software GPIO control by writing set/clear firmware-control registers and exposes ACPI-described GPIO ranges.

## Important APIs, Types, and Functions
Key state is `struct mlxbf3_pinctrl`, which stores four MMIO windows for set/clear control of two GPIO banks. Static data includes `mlxbf3_pinctrl_gpio_ranges`, `mlxbf3_pins`, one-pin group names, and two functions `hwfunc` and `gpiofunc`. Runtime callbacks are `mlxbf3_get_groups_count`, `mlxbf3_get_group_name`, `mlxbf3_get_group_pins`, `mlxbf3_pmx_get_funcs_count`, `mlxbf3_pmx_get_func_name`, `mlxbf3_pmx_get_groups`, `mlxbf3_pmx_set`, and `mlxbf3_gpio_request_enable`.

## Control Flow and State
Probe maps four resources, registers and enables pinctrl, then adds two GPIO ranges mapping pin 0-31 to GPIO base 480 and pin 32-55 to GPIO base 456. Mux setting writes a bit to a clear register for hardware mode or to a set register for software GPIO mode, choosing bank 0 or bank 1 by pin number. GPIO requests force the requested pin into software-controlled mode. Persistent state lives in firmware-control hardware registers; there is no software cache or readback path.

## Dependencies and Integration Points
Depends on ACPI match ID `MLNXBF34`, platform MMIO resources, pinctrl core registration with explicit `pinctrl_enable`, and gpiolib range association. This driver is a pinmux companion to the BlueField GPIO controller rather than a full GPIO provider itself.

## Risks and Test Signals
Risks include unusual function/group metadata where functions advertise one group array but return all pins as group count, incorrect GPIO base mapping for the two ranges, no selector validation beyond two known enum values, and write-only control with no state verification. Test signals include ACPI probe, pinctrl debugfs group/function enumeration, GPIO request forcing software mode, MMIO trace/readback from adjacent firmware registers if available, and exercising pins on both sides of the 32-pin bank boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mlxbf3.c -->
