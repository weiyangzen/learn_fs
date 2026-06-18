# Research: subset-b-005047

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm2835.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm2835.c

## Purpose
This file implements the combined pinctrl, pinmux, pinconf, GPIO, and GPIO interrupt controller driver for Broadcom BCM2835-family GPIO blocks, including BCM2835, BCM2711, and BCM7211-compatible variants. It exposes every GPIO as a one-pin pinctrl group, maps the hardware function-select values to pinmux functions, handles legacy Raspberry Pi `brcm,pins`/`brcm,function`/`brcm,pull` device-tree bindings as well as generic pinconf bindings, and registers a `gpio_chip` with an irqchip for edge and level GPIO interrupts.

## Important APIs, Types, And Functions
`struct bcm2835_pinctrl` is the central state object. It stores the MMIO base, copied `gpio_chip`, copied `pinctrl_desc`, GPIO range, pinctrl device, optional BCM7211 wake IRQ array, enabled IRQ bitmaps, per-pin IRQ type state, raw IRQ bank locks, and a function-select spinlock.

The hardware accessors are `bcm2835_gpio_rd()`, `bcm2835_gpio_wr()`, `bcm2835_gpio_get_bit()`, `bcm2835_gpio_set_bit()`, `bcm2835_pinctrl_fsel_get()`, and `bcm2835_pinctrl_fsel_set()`. GPIO callbacks include direction, get/set, and get-direction helpers. IRQ callbacks include `bcm2835_gpio_irq_handler()`, `bcm2835_gpio_irq_handle_bank()`, mask/unmask, ack, set-type, and set-wake. Pinctrl and pinmux callbacks are `bcm2835_pctl_*` and `bcm2835_pmx_*`; pinconf callbacks are split between legacy BCM2835 pull programming and BCM2711 pull register programming.

## Control Flow
Probe maps MMIO, selects platform data by OF compatible, initializes locks, clears all event detection enables and latched event bits, registers pinctrl, adds the GPIO range, wires a three-parent hierarchical GPIO irqchip, optionally requests BCM7211 wake IRQs, and finally registers the GPIO chip. Pin requests and DT states then flow through pinctrl: device-tree nodes are translated into mux and config maps, `set_mux` writes the function-select field, pinconf writes pull or level settings, and GPIO requests use generic gpiochip request/free.

For GPIO interrupts, each parent IRQ is chained to the same handler. The handler identifies which parent fired, splits it into hardware GPIO ranges, filters GPEDS status by `enabled_irq_map`, and dispatches each pending line through `generic_handle_domain_irq()`. Type changes update the per-pin `irq_type` array and enable/disable the corresponding rising, falling, high, or low detect register bits.

## State And Persistence
The driver persists software IRQ enable and type state in memory; the hardware persists function-select, output level, pull configuration, and event-detect bits until changed or reset. Probe intentionally clears interrupt detection and pending events. `persist_gpio_outputs` is a module parameter that prevents pinmux free from reverting GPIO outputs to inputs, preserving output drive across pin release. BCM2711 pull settings are readable and stored in dedicated pull registers; BCM2835 pull state cannot be read back.

## Dependencies And Integration Points
The file integrates with Linux pinctrl, pinmux, pinconf-generic, gpiolib, gpio irqchip helpers, OF address/IRQ parsing, and DT binding constants from `dt-bindings/pinctrl/bcm2835.h`. GPIO consumers use the registered `gpio_chip`; peripheral drivers consume pinctrl states through generic or legacy Raspberry Pi bindings.

## Risks
Function-select writes are register-wide read/modify/write operations, so `fsel_lock` is critical. Interrupt type changes are sensitive because edge-both reconfiguration intentionally toggles one detect source at a time. BCM2835 pull programming uses timing delays and a clock-strobe sequence; incorrect ordering can silently misconfigure pulls. The IRQ parent grouping is hard-coded for GPIO ranges 0-27, 28-45, and 46-57, so SoC-compatible data and `ngpio` must stay aligned. Legacy DT parser allocation/unwind must free per-pin config arrays correctly.

## Test Signals
Useful checks are pinctrl state application for generic and legacy DT nodes, GPIO input/output reads and writes, pin release with and without `persist_gpio_outputs`, BCM2711 pull readback, GPIO IRQ rising/falling/both/level behavior across all three parent ranges, wake IRQ enable on BCM7211, and boot logs showing successful pinctrl and GPIO chip registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm2835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm4908.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm4908.c

## Purpose
This file implements a pinmux-only driver for the Broadcom BCM4908 pin controller. It describes 86 pins and the SoC's alternate groups for LEDs, high-speed UART, I2C, I2S, NAND, eMMC control, and USB power pins, then programs the hardware through the BCM4908 test-port command interface.

## Important APIs, Types, And Functions
`struct bcm4908_pinctrl` stores the device, MMIO base, mutex, pinctrl device, and mutable descriptor copy. `struct bcm4908_pinctrl_pin_setup` binds a pin number to the hardware function value required for a group. `struct bcm4908_pinctrl_grp` and `struct bcm4908_pinctrl_function` provide the group/function tables consumed by generic pinctrl and pinmux helpers.

The active programming path is `bcm4908_pinctrl_set_mux()`. It resolves the generic group descriptor, locks the controller mutex, and for each pin writes the pin number and function value into the test-port data registers before writing `BCM4908_TEST_PORT_CMD_LOAD_MUX_REG` to the command register.

## Control Flow
Probe allocates private state, maps resource 0, initializes the mutex, copies the static descriptor, dynamically creates 86 `"pin%d"` descriptors, registers the pinctrl device, then registers every static group and function with generic pinctrl/pinmux registries. Device-tree group states are parsed through `pinconf_generic_dt_node_to_map_group()`, so applying a state selects a function and group, then `set_mux` emits one test-port command per pin in that group.

## State And Persistence
The driver maintains almost no runtime software state beyond registration metadata and the mutex. The programmed mux state is persistent in the hardware pinmux registers until changed or reset. There is no GPIO, IRQ, or pinconf state in this file, and no readback path for the selected mux.

## Dependencies And Integration Points
It depends on Linux pinctrl generic group/function infrastructure and OF platform probing for `brcm,bcm4908-pinctrl`. It is normally paired with separate GPIO or peripheral drivers that consume its pinctrl states. It includes pinctrl core and pinmux helper headers from the parent pinctrl subsystem.

## Risks
The test-port command interface is write-only from this driver's perspective, so failures or stale hardware state are hard to observe. The mutex serializes multi-register command sequences; missing it would allow interleaved pin programming. Group table correctness is high risk because each pin carries a numeric function value that must match the SoC datasheet. There is no validation that a requested function selector semantically matches the group data beyond the generic function/group relationship.

## Test Signals
Test by applying DT pinctrl states for all exposed functions, especially alternate LED groups and shared I2C options, then verifying the corresponding peripherals work. Boot should show successful registration, and failed probes should only come from MMIO mapping or allocation failures. Hardware-level validation requires checking pin function on boards with UART, I2C, NAND/eMMC, USB power, and LED routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm4908.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6318.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6318.c

## Purpose
This SoC-specific BCM63xx pinctrl file describes BCM6318 pins, functions, groups, and mux register programming. It supports 50 GPIOs, LED mode for GPIOs 0-23, pinmux-select functions for Ethernet LEDs, serial LEDs, USB, DSL, WPS, and other board signals, and GPIO request fallback that disables alternate functions.

## Important APIs, Types, And Functions
`struct bcm6318_function` maps a function to its groups plus a one-bit mode value and two-bit mux value. Static `bcm6318_pins`, one-pin `bcm6318_groups`, function group arrays, and `bcm6318_funcs` define the hardware matrix. `bcm6318_mux_off()` and `bcm6318_pad_off()` calculate register offsets. `bcm6318_rmw_mux()` updates the mode register and mux selector fields; `bcm6318_set_pad()` controls the pad register for pins whose GPIO mode needs a pad value.

## Control Flow
The platform probe simply calls the shared `bcm63xx_pinctrl_probe()` with `bcm6318_soc`. After common registration, pinctrl callbacks expose group and function counts, names, and pins from static tables. `bcm6318_pinctrl_set_mux()` selects the first pin in the requested group and writes the function's mode and mux values. When gpiolib requests a line, `bcm6318_gpio_request_enable()` clears alternate functions; pins 0-12 use mux 0 as GPIO, while pins 13-41 use mux 3 as GPIO and have pad value cleared.

## State And Persistence
Software state is supplied by the shared `struct bcm63xx_pinctrl`; this file persists no private state. Hardware mux state lives in the shared parent regmap registers. The common helper registers GPIO via `gpio-regmap`, so GPIO data and direction are stored through the parent syscon register map.

## Dependencies And Integration Points
Depends on `pinctrl-bcm63xx.h` for shared probe/state, Linux regmap, pinctrl-utils DT parsing, pinmux strict mode, and the parent syscon node that owns the GPIO/pinmux registers. It is built as a builtin platform driver for `brcm,bcm6318-pinctrl`.

## Risks
The main risk is wrong mux value or register offset per pin. GPIO request handling has SoC-specific split rules for pins below 13 and pins 13-41, so off-by-one errors can leave pins in an alternate function. `strict = true` prevents simultaneous GPIO and mux ownership, but only if pinctrl ranges are correct.

## Test Signals
Validate DT states for LED, Ethernet LED, serial LED, USB, DSL, and WPS functions. Request GPIOs across the split ranges 0-12, 13-41, and 42-49 and verify they return to GPIO mode. GPIO data/direction testing should use the common BCM63xx gpio-regmap chip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6318.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63268.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63268.c

## Purpose
This file provides the BCM63268 pinctrl description and mux programming for the shared BCM63xx pinctrl core. It covers 52 GPIOs, LED control, per-pin mode bits, Wi-Fi control bits, NAND and VDSL/DECT base modes, and GPIO fallback for pins that overlap those base modes.

## Important APIs, Types, And Functions
`enum bcm63268_pinctrl_reg` classifies functions by the register they program: LED, MODE, CTRL, or BASEMODE. `struct bcm63268_function` records the function name, groups, register type, and base-mode mask. `BCM63268_PIN()` stores base-mode ownership masks in pin descriptor `drv_data`. `bcm63268_set_gpio()` clears all function ownership for a pin, including base-mode bits, LED bits, mode bits, or CTRL Wi-Fi bits. `bcm63268_pinctrl_set_mux()` first returns every pin in a group to GPIO, then enables the requested function register bit or base-mode mask.

## Control Flow
Probe calls `bcm63xx_pinctrl_probe()` with the BCM63268 SoC table. DT parsing uses generic pin config-to-pin mapping via `pinctrl_utils_free_map` and `pinconf_generic_dt_node_to_map_pin`. On mux selection, the driver sanitizes each pin in the target group with `bcm63268_set_gpio()`, chooses the hardware register and value from the function descriptor, then updates the register through regmap.

## State And Persistence
No private state is stored in this file. Hardware state persists in LED, MODE, CTRL, and BASEMODE registers. `drv_data` embedded in the static pin descriptors is used as immutable metadata to know which base-mode bits must be cleared when reclaiming a pin as GPIO.

## Dependencies And Integration Points
It integrates with the common BCM63xx probe/gpio-regmap implementation, pinctrl-utils generic DT mapping, and the parent regmap obtained from the syscon node. It is the platform driver for `brcm,bcm63268-pinctrl`, while the shared common file also detects the corresponding `brcm,bcm63268-gpio` child for GPIO registration.

## Risks
The file coordinates overlapping function domains. A pin can be controlled by base mode, LED mode, normal mode, or Wi-Fi CTRL behavior, and failure to clear old ownership before setting a new function can leave mixed hardware state. For pins 24-27, multiple base-mode masks overlap NAND and VDSL functions, making table accuracy especially important.

## Test Signals
Exercise NAND, DECT, VDSL override, Wi-Fi, LED, UART1, HSSPI chip-select, NTR, ADSL SPI, switch LED, and GPIO fallback states. Verify GPIO requests clear base-mode conflicts and that Wi-Fi pins 32-51 switch through CTRL semantics correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63268.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6328.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6328.c

## Purpose
This BCM63xx SoC file describes BCM6328 pin groups and mux programming. It supports 32 GPIOs plus two pseudo pins for `hsspi_cs1` and `usb_port1`, and exposes functions for LEDs, serial LEDs, internet activity LED, PCIe clock request, Ethernet PHY activity LEDs, HSSPI CS1, and USB host/device port mode.

## Important APIs, Types, And Functions
`struct bcm6328_function` carries group lists plus a mode bit and two-bit mux value. `bcm6328_mux[]` maps pin ranges to mux register offsets. `bcm6328_mux_off()` selects the proper mux register, while `bcm6328_rmw_mux()` updates the mode bit for real GPIO pins and the two-bit mux selector for all defined pins, including the pseudo pins. `bcm6328_pinctrl_set_mux()` and `bcm6328_gpio_request_enable()` are the key pinmux callbacks.

## Control Flow
Probe delegates to `bcm63xx_pinctrl_probe()`. Pinctrl callbacks expose static group/function tables. Mux selection takes the first pin in the selected group and writes the function's mode and mux values. GPIO request enable clears mode and mux selection to zero for the requested GPIO line.

## State And Persistence
All mutable state lives in hardware registers behind the shared regmap. The driver itself is table-only after registration. GPIO direction/value state is provided by the common GPIO regmap chip, while pinmux state persists in MODE and MUX registers until changed or reset.

## Dependencies And Integration Points
Uses the BCM63xx shared core, Linux regmap, pinctrl-utils DT mapping, and strict pinmux semantics. It is registered as a builtin platform driver for `brcm,bcm6328-pinctrl` and expects a parent syscon plus a matching GPIO child for GPIO support.

## Risks
The pseudo pins 36 and 38 are explicitly noted as approximate locations based on mux offsets, so consumers must match the binding expectations rather than assume physical GPIO numbering. `bcm6328_mux_off()` indexes `bcm6328_mux[pin / 16]`; only defined pin numbers should reach it. Incorrect DT pin numbers could otherwise select unintended registers.

## Test Signals
Apply DT states for LED, serial LED, Ethernet LEDs, PCIe clock request, HSSPI CS1, and USB host/device port modes. Request GPIOs 0-31 and confirm alternate function bits are cleared. Validate USB port mode and HSSPI chip-select behavior because they use nonstandard pseudo pin numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6328.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6358.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6358.c

## Purpose
This file implements BCM6358-specific pinmux data and control for the shared BCM63xx framework. Unlike the newer BCM63xx variants, BCM6358 uses overlay mode bits in a single mode register and must sometimes drive GPIO direction when assigning non-GPIO functions.

## Important APIs, Types, And Functions
`struct bcm6358_pingroup` wraps a `pingroup`, the mode bit to enable, and a per-pin direction bitmap for that group. `struct bcm6358_priv` stores a `regmap_field *overlays` covering mode bits 0-15. Static pin descriptors put the set of possible overlay bits for each pin in `drv_data`. `bcm6358_pinctrl_set_mux()` computes a mask of the selected group mode and all conflicting overlay bits, updates the regmap field, then asks the registered GPIO chip to set each pin input or output according to group direction.

## Control Flow
Probe allocates private state, calls the common BCM63xx probe with that state, fetches the resulting `struct bcm63xx_pinctrl`, and allocates the overlay regmap field. Standard pinctrl callbacks expose the static group and function tables. GPIO request enable reads the pin's `drv_data` overlay mask and clears all function bits that could own that line.

## State And Persistence
The only private software state is the overlay regmap field pointer. The active function state persists in the BCM6358 mode register. GPIO direction changes made during muxing persist in the common GPIO direction register and are intentionally used as part of the alternate-function setup.

## Dependencies And Integration Points
Depends on `pinctrl-bcm63xx.c` for registration and GPIO, Linux regmap fields, pinctrl-utils generic DT parsing, and gpiolib ranges because mux setup looks up the GPIO chip with `pinctrl_find_gpio_range_from_pin()` and invokes direction callbacks.

## Risks
The function/group arrays contain names such as `spi_cs_2_3` and `clkrst` whose group arrays reference group names; table mismatches would break DT state resolution. In the mux and direction loops, code indexes `bcm6358_pins[pin]` using the loop index rather than the group's pin number, which is a notable maintenance risk because it assumes group pin arrays and descriptor ordering are compatible. Direction side effects can also surprise consumers if a function's output bitmap is wrong.

## Test Signals
Test all overlay functions, especially UART1, EBI CS, SPI CS, UTOPIA, modem, serial/legacy LEDs, PWM sync clock, and system IRQ. Confirm GPIO requests clear overlay bits. Verify alternate functions that require output directions drive expected idle levels and that pinctrl strictness prevents concurrent GPIO use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6358.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6362.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6362.c

## Purpose
This BCM63xx SoC file describes and programs BCM6362 pinmux state. It supports 48 GPIOs, LED mode, normal mode bits, Wi-Fi control via the CTRL register, and a NAND base mode spanning a multi-pin group.

## Important APIs, Types, And Functions
`enum bcm6362_pinctrl_reg` identifies LED, MODE, CTRL, and BASEMODE targets. `struct bcm6362_function` maps function names to groups and register type, with optional base-mode mask. `BCM6362_PIN()` annotates NAND-owned pins via descriptor `drv_data`. `bcm6362_set_gpio()` clears NAND base mode, per-pin mode/LED bits, or Wi-Fi CTRL ownership for a pin. `bcm6362_pinctrl_set_mux()` clears all pins in the selected group, then sets the function-specific register bit or base-mode mask.

## Control Flow
Probe delegates to the shared BCM63xx core. Group/function callbacks return static table data. Applying a pinctrl state calls `set_mux`, which first normalizes all group pins to GPIO, then chooses the register and mask based on `bcm6362_funcs[selector].reg`. GPIO request enable also uses `bcm6362_set_gpio()` to reclaim the line.

## State And Persistence
No dynamic private state is kept. Hardware state persists in LED, MODE, CTRL, and BASEMODE registers. The shared common layer supplies `struct bcm63xx_pinctrl`, the regmap, and GPIO state through gpio-regmap.

## Dependencies And Integration Points
Depends on the common BCM63xx core, parent syscon regmap, pinctrl-utils, and Linux pinmux strict ownership. Consumers use `brcm,bcm6362-pinctrl` states for board functions such as LEDs, UART1, ADSL SPI, Ethernet PHY LEDs, external IRQs, Wi-Fi, and NAND.

## Risks
The code computes `mask = bcm63xx_bank_pin(pin)` in `bcm6362_set_gpio()` and then passes that value to `regmap_update_bits()` where other paths use `BIT(...)`; this is a risk area to review against hardware expectations. Base-mode pins need careful table metadata because failing to clear NAND mode can block GPIO or other mode bits. CTRL semantics are inverted for Wi-Fi versus GPIO, so value polarity mistakes are easy.

## Test Signals
Exercise LED, serial LED, RoboSwitch LEDs, internet LED, SPI CS, UART1, ADSL SPI, EPHY LEDs, external IRQs, Wi-Fi pins 32-47, NAND group, and GPIO fallback. Read back regmap traces or hardware pins to confirm NAND base mode clears when individual pins become GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6362.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6368.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6368.c

## Purpose
This file provides BCM6368 pinmux tables and register programming for the BCM63xx common pinctrl core. It covers 38 GPIOs, many one-pin overlay functions, and a UART1 base mode on GPIOs 30-33.

## Important APIs, Types, And Functions
`struct bcm6368_function` maps a function to its groups, output-direction bitmap, and optional base-mode value. `struct bcm6368_priv` stores a regmap field for the BASEMODE register. `BCM6368_BASEMODE_PIN()` marks pins whose function depends on base-mode selection. `bcm6368_pinctrl_set_mux()` handles two paths: base-mode functions clear per-pin mode bits and write the base-mode field, while ordinary functions force base mode back to GPIO if needed and set the per-pin mode bit. It then programs GPIO direction for pins in the selected group.

## Control Flow
Probe allocates private state, invokes `bcm63xx_pinctrl_probe()`, retrieves the common state, and allocates the base-mode regmap field. Mux selection resolves the static group/function entry, updates MODE and BASEMODE registers as needed, and uses the pinctrl GPIO range to call GPIO direction callbacks. GPIO request enable clears per-pin mode bits and restores base-mode GPIO for marked pins.

## State And Persistence
Private state is limited to the base-mode regmap field. Hardware state persists in the MODE register, BASEMODE field, and GPIO direction registers. The common BCM63xx core owns pinctrl registration and GPIO regmap state.

## Dependencies And Integration Points
Depends on the shared BCM63xx helper, regmap fields, pinctrl-utils, gpiolib direction callbacks, and strict pinmux ownership. It binds to `brcm,bcm6368-pinctrl`.

## Risks
As with BCM6358, the mux code loops over group pin count but indexes `bcm6368_pins[pin]` by loop index in direction handling, which is risky for groups whose pin numbers differ from descriptor indexes. Base-mode restoration must be paired with any function on pins 30-33. The direction bitmap is part of function semantics; an incorrect bit can configure a peripheral pin as input when hardware expects output.

## Test Signals
Validate analog AFE, system IRQ, serial LED, internet LED, EPHY/RoboSwitch LEDs, USB LED, PCI/PCMCIA, EBI, SPI CS, UART1, and GPIO fallback. Confirm UART1 base mode switches all four pins and that GPIO requests on pins 30-33 restore base mode to GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm6368.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.c

## Purpose
This is the shared support file for the BCM63xx pinctrl family. It registers the SoC-specific pinctrl descriptor supplied by each BCM63xx variant and creates a GPIO controller through `gpio-regmap` for matching child GPIO nodes.

## Important APIs, Types, And Functions
`bcm63xx_reg_mask_xlate()` translates a GPIO offset into a register offset and bit mask for gpio-regmap. BCM63xx banks are 32 GPIOs wide, and bank register addresses count backwards from the base value using `BCM63XX_BANK_SIZE`. `bcm63xx_gpio_probe()` fills `struct gpio_regmap_config` with data, direction, set, ngpio, and translation settings. `bcm63xx_pinctrl_probe()` allocates `struct bcm63xx_pinctrl`, obtains the parent syscon regmap, fills `pinctrl_desc`, registers pinctrl, and scans sibling child nodes for compatible GPIO controllers.

## Control Flow
Each SoC-specific file calls `bcm63xx_pinctrl_probe(pdev, &soc, driver_data)`. The common function stores optional driver data for the SoC file, registers pinctrl operations from the `soc` descriptor, then iterates children of the parent OF node. If a child matches any BCM63xx GPIO compatible string, the common code registers a gpio-regmap chip using the same regmap.

## State And Persistence
Software state is `struct bcm63xx_pinctrl`: device, parent regmap, pinctrl descriptor/device, and opaque SoC driver data. GPIO data/direction and mux state persist in shared syscon registers rather than in this file. Device-managed allocation and registration control lifetime.

## Dependencies And Integration Points
Depends on `linux/gpio/regmap.h`, MFD syscon regmaps, OF child node scanning, and SoC-specific descriptors from `pinctrl-bcm6318.c`, `pinctrl-bcm6328.c`, `pinctrl-bcm6358.c`, `pinctrl-bcm6362.c`, `pinctrl-bcm6368.c`, and `pinctrl-bcm63268.c`.

## Risks
The register translation uses a negative bank stride from `base - stride * 4`, which must match the hardware register layout for all supported chips. The common GPIO registration assumes the pinctrl device's parent node contains the GPIO child nodes. If board DT hierarchy differs, pinctrl can register but GPIO support will not appear.

## Test Signals
For every BCM63xx SoC, confirm pinctrl registration, GPIO child discovery, gpiochip creation, GPIO data/direction operation across bank 0 and bank 1, and successful mux ownership through the SoC-specific operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.h

## Purpose
This header defines the shared data contract between the BCM63xx common pinctrl implementation and the SoC-specific BCM6318/6328/6358/6362/6368/63268 files.

## Important APIs, Types, And Functions
`struct bcm63xx_pinctrl_soc` packages the pinctrl and pinmux operation tables, pin descriptor array, pin count, and GPIO count that each SoC file passes into the common probe. `struct bcm63xx_pinctrl` is the common runtime state: device, regmap, descriptor, registered pinctrl device, and opaque SoC `driver_data`. `BCM_PIN_GROUP(n)` creates a one-line `pingroup` from a `n_pins` array. `bcm63xx_bank_pin()` maps a global pin to a 0-31 bank bit. `bcm63xx_pinctrl_probe()` is the exported common probe entry.

## Control Flow
SoC files include this header, build static `bcm63xx_pinctrl_soc` descriptors, and call `bcm63xx_pinctrl_probe()` from their platform probe. Their callbacks later retrieve `struct bcm63xx_pinctrl` with `pinctrl_dev_get_drvdata()`.

## State And Persistence
The header itself stores no state. It defines how common state and optional SoC-private state are linked for the life of the platform device.

## Dependencies And Integration Points
Depends on Linux pinctrl type definitions and platform device declarations. It provides the ABI-like local interface that keeps SoC tables separate from common GPIO/regmap setup.

## Risks
Because the structure is shared across multiple SoC files, field changes must be coordinated across all users. `BCM_PIN_GROUP` assumes a matching `n_pins` symbol exists, so table naming consistency matters.

## Test Signals
Build coverage across all BCM63xx drivers is the main signal. Runtime signals are successful retrieval of `driver_data`, correct GPIO counts, and expected group tables in debugfs pinctrl output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm63xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb-bcm2712.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb-bcm2712.c

## Purpose
This file supplies BCM2712-specific data for the generic Broadcom STB pinctrl core. It describes C0 and D0 silicon variants, normal and always-on pin banks, register bit locations, GPIO ranges, function names, and per-pin alternate-function tables.

## Important APIs, Types, And Functions
`enum bcm2712_funcs` defines the symbolic function IDs used by the shared brcmstb core. `BRCMSTB_PIN()` builds per-pin arrays of up to eight alternate functions plus mask metadata. `bcm2712_*_pin_regs` map each pin number to mux and pad bits through macros from `pinctrl-brcmstb.h`. `bcm2712_*_pins` define normal GPIO, eMMC, AON GPIO, and AON SGPIO pin descriptors. Four `struct brcmstb_pdata` instances bind descriptors, ranges, register maps, function maps, and function-name arrays for C0, C0 AON, D0, and D0 AON variants.

## Control Flow
The local probe is a thin wrapper around `brcmstb_pinctrl_probe()`. OF match data selects the correct `brcmstb_pdata` for `brcm,bcm2712c0-pinctrl`, `brcm,bcm2712c0-aon-pinctrl`, `brcm,bcm2712d0-pinctrl`, or `brcm,bcm2712d0-aon-pinctrl`. The shared brcmstb core then uses the tables here to register pinctrl and program mux or bias bits.

## State And Persistence
This data file stores no mutable runtime state. Its tables are immutable descriptions of hardware layout. The actual mux and pull state persists in BCM2712 pin controller registers handled by `pinctrl-brcmstb.c`.

## Dependencies And Integration Points
Depends on `pinctrl-brcmstb.h` macros and `brcmstb_pinctrl_probe()`. It integrates BCM2712 board DT compatible strings with the shared brcmstb pinctrl logic and exposes function names for peripherals including SD/eMMC, Ethernet, UART, SPI, I2C, PWM, HDMI, I2S, PDM, JTAG, USB power/vbus, and AON functions.

## Risks
The risk is table accuracy. Each pin has independent mux and pad bit locations, and D0 removes or shifts several pins relative to C0. A wrong function ID, register bit, or range count can route a peripheral to the wrong pad or expose a non-existent pin. eMMC pins have no mux bit and only pad control, which the core treats specially.

## Test Signals
Validate pinctrl states on BCM2712 C0 and D0 boards for normal and AON controllers. Check eMMC pad bias, GPIO and SGPIO function selection, UART/I2C/SPI/SD/Ethernet alternate routes, and debugfs pin function names. Probe should bind separately for normal and AON compatible nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb-bcm2712.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.c

## Purpose
This is the shared pinctrl implementation for Broadcom STB-style pin controllers used by BCM2712 data in this subset. It registers pinctrl, pinmux, and generic bias pinconf operations, with one pin per group and per-pin function tables supplied as match data.

## Important APIs, Types, And Functions
`struct brcmstb_pinctrl` stores MMIO base, copied descriptor, pin register metadata, per-pin function mappings, function names, GPIO group names, GPIO range, and a spinlock. `brcmstb_pinctrl_fsel_get()` reads a pin's mux field and maps hardware fsel to logical function ID. `brcmstb_pinctrl_fsel_set()` maps a logical function back to an fsel value and writes the mux bits. `brcmstb_pull_config_get()` and `brcmstb_pull_config_set()` read/write two-bit pad pull fields. `brcmstb_pinctrl_probe()` is exported for SoC data files.

## Control Flow
Probe gets match data, maps MMIO, copies the SoC descriptor, installs common pctl/pmx/pinconf ops, builds a list of one-pin group names from pin descriptors, stores SoC register/function tables, registers pinctrl, and adds the GPIO range. Runtime mux selection calls `brcmstb_pmx_set()`, which validates the group, resolves the pin descriptor number, and writes fsel. GPIO request/free paths set the pin back to the SoC's GPIO function. Pinconf generic bias operations read and write pad bits when a pad bit exists.

## State And Persistence
Runtime software state is the `brcmstb_pinctrl` object and generated group-name array. Hardware persists mux and pull state. The core does not manage GPIO data or interrupts; it only exposes mux and bias control. Pins without mux bits, such as eMMC-only pads, cannot be muxed but may still have pull configuration.

## Dependencies And Integration Points
Depends on OF match data supplied by a SoC-specific file, Linux pinctrl/pinmux/pinconf-generic, MMIO helpers, and `pinctrl-brcmstb.h`. It exports `brcmstb_pinctrl_probe()` to module users.

## Risks
Function mapping is subtle because callers can pass either logical function IDs or fsel-like values; invalid function IDs return `-EINVAL`. Debug messages index `func_names` with current fsel in some paths, so table consistency matters. Bias writes share the same spinlock as mux writes, protecting MMIO read/modify/write but coupling unrelated register domains.

## Test Signals
Use pinctrl debugfs to inspect group names, function names, and pin states. Apply mux and bias states for pins with and without mux bits. Confirm GPIO requests return pins to GPIO function and that invalid functions or pads without pull bits fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.h

## Purpose
This header defines the table format and helper macros for Broadcom STB pinctrl drivers, especially BCM2712 in this subset. It lets data files describe mux bit positions, pad pull bit positions, GPIO and AON pin descriptors, per-pin alternate functions, and probe match data.

## Important APIs, Types, And Functions
`BRCMSTB_FUNC()` maps enum function identifiers to names. `MUX_BIT()`, `PAD_BIT()`, `GPIO_REGS()`, `EMMC_REGS()`, `AON_GPIO_REGS()`, and `AON_SGPIO_REGS()` encode mux and pad register/shift values into compact `struct pin_regs` entries. `GPIO_PIN()`, `AON_GPIO_PIN()`, and `AON_SGPIO_PIN()` build pin descriptors. `struct brcmstb_pin_funcs` describes each pin's fsel mask, function array, and function count. `struct brcmstb_pdata` packages all SoC data consumed by `brcmstb_pinctrl_probe()`.

## Control Flow
SoC data files include this header to construct static tables. At probe, the OF match `.data` points to `struct brcmstb_pdata`, and the common core interprets the encoded mux/pad fields for reads and writes.

## State And Persistence
The header stores no runtime state. It defines immutable metadata structures that determine how hardware state is accessed by the common core.

## Dependencies And Integration Points
Depends on Linux type definitions, platform device declarations, and pinctrl pin descriptor macros. It is the local interface between brcmstb data files and the shared brcmstb implementation.

## Risks
The bit encoding macros are compact and easy to misuse: shifts are scaled to hardware field positions, `MUX_BIT_VALID` distinguishes no-mux pins from register bit zero, and `PAD_BIT_INVALID` marks pins without pull control. Any mismatch corrupts the common core's register math.

## Test Signals
Compile all brcmstb users and validate debugfs/function output. Runtime tests should cover pins with mux and pad bits, eMMC pads with no mux bit, and AON SGPIO pins with invalid pad bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-cygnus-mux.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-cygnus-mux.c

## Purpose
This file implements the Broadcom Cygnus group-based IOMUX driver. It exposes a large static pin/group/function matrix, programs group mux fields, and supports per-pin GPIO override for pins whose GPIO function is controlled through a second register block.

## Important APIs, Types, And Functions
`struct cygnus_pinctrl` stores the pinctrl device, two MMIO bases, group/function tables, a `mux_log`, and a spinlock. `struct cygnus_pin_group` ties a group to pins and a mux field described by `struct cygnus_mux`. `struct cygnus_mux_log` records whether an IOMUX field was configured and with which alternate value. `cygnus_pinmux_set()` detects conflicting double configuration and writes group mux bits. `cygnus_gpio_request_enable()` and `cygnus_gpio_disable_free()` set or clear per-pin GPIO override bits in `base1`.

## Control Flow
The arch initcall registers the platform driver early. Probe maps two resources, initializes the mux log for 8 registers times 8 mux fields, allocates pin descriptors with each pin's GPIO override metadata in `drv_data`, assigns static groups/functions, and registers pinctrl. Applying a state calls `cygnus_pinmux_set_mux()`, which logs and writes the group mux. GPIO requests call the GPIO override path if the pin supports it.

## State And Persistence
The key software state is `mux_log`, which prevents two groups from programming the same IOMUX field to different alternate values. Hardware mux state persists in `base0` group mux registers and `base1` GPIO override registers. The driver does not restore state across suspend/resume itself; it relies on normal pinctrl reapplication if needed.

## Dependencies And Integration Points
Depends on Linux pinctrl, pinmux, pinconf-generic group DT mapping, pinctrl-utils, platform MMIO resources, and any ASIU GPIO controller that requests GPIO override through pinctrl GPIO ranges. It binds to `brcm,cygnus-pinmux`.

## Risks
The conflict detection only tracks IOMUX field reuse after this driver starts; it does not read initial hardware state. `CYGNUS_NUM_IOMUX` must cover every static mux field. GPIO override supports only selected pins and returns `-ENOTSUPP` otherwise. `cygnus_gpio_disable_free()` logs with `dev_err`, which may be noisy for normal free paths.

## Test Signals
Apply DT states for shared mux fields with same and conflicting alternates to verify conflict handling. Test major groups: SPI, UART, SDIO, NAND, LCD, camera, smartcard, PWM, key, CAN, USB overcurrent, and GPIO override-capable pins. Confirm two MMIO resources are present and pinctrl registers at arch init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-cygnus-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-iproc-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-iproc-gpio.c

## Purpose
This file implements Broadcom iProc GPIO controllers with optional GPIO IRQ support and a local pinconf provider for pull-up/down and drive-strength settings. It supports generic iProc, Cygnus CCM/ASIU/CRMU, NSP, and Stingray-compatible GPIO blocks.

## Important APIs, Types, And Functions
`struct iproc_gpio` stores MMIO bases, optional external IO-control base, IO-control type, raw spinlock, gpiochip, bank count, pinmux support flag, disabled pinconf parameters, and local pinctrl descriptor/device. GPIO callbacks are `iproc_gpio_request()`, `iproc_gpio_free()`, direction, get/set, and get-direction. IRQ paths include `iproc_gpio_irq_handler()`, ack, mask/unmask, and `iproc_gpio_irq_set_type()`. Pinconf paths include `iproc_gpio_set_pull()`, `iproc_gpio_get_pull()`, drive-strength get/set helpers, and `iproc_pin_config_get()/set()`.

## Control Flow
The driver is registered by `arch_initcall_sync()`. Probe maps the GPIO MMIO resource and optional IO-control resource, reads `ngpios`, configures the gpiochip, detects whether GPIO pinmux requests are supported through `gpio-ranges`, optionally wires a chained parent IRQ, registers the gpiochip, and unless disabled creates a local pinctrl device with one pin per GPIO for pinconf. NSP disables drive-strength pinconf; Stingray disables pinconf entirely.

## State And Persistence
Software state includes the spinlock-protected chip object, disabled pinconf list, bank count, and optional local pinctrl registration. Hardware persists data in/out, output enable, IRQ type/dual-edge/edge/mask/status registers, pull registers, resistor enable/pad resistance registers, and drive-strength control registers. Interrupt state is not mirrored in software beyond gpiolib irqchip state.

## Dependencies And Integration Points
Depends on gpiolib, GPIO irqchip helpers, pinctrl consumer APIs for `pinctrl_gpio_request/free`, pinconf-generic, OF platform data, and `gpio-ranges` integration with SoC IOMUX drivers such as Cygnus. GPIO consumers use this as a normal `gpio_chip`; pinconf consumers use the local pinctrl provider.

## Risks
IRQ handling iterates all banks and clears each interrupt before dispatch, which is intentional but sensitive for level interrupts. Drive-strength encoding differs for AON, CDRU, and ASIU controllers through `DRV_STRENGTH_OFFSET()`. Pinconf disable masks must match hardware capabilities. Probe removes the gpiochip on pinconf registration failure, so ordering and error paths matter.

## Test Signals
Test GPIO input/output across multiple banks, optional parent IRQ handling for rising/falling/both/high/low, pull-up/down/disable on CDRU and non-CDRU controllers, drive strengths from 2 to 16 mA, NSP drive-strength rejection, Stingray no-pinconf behavior, and `gpio-ranges` pinmux requests into the owning IOMUX controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-iproc-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns.c

## Purpose
This file implements the Broadcom Northstar pinmux driver for BCM4708, BCM4709, and BCM53012. It filters the static pin/group/function tables by chipset compatible and programs the CRU GPIO control register to enable peripheral functions.

## Important APIs, Types, And Functions
`struct ns_pinctrl` stores the device, chipset flag, pinctrl device, mapped CRU register base, and descriptor copy. `ns_pinctrl_pins`, `ns_pinctrl_groups`, and `ns_pinctrl_functions` carry chipset masks in descriptor or table metadata. `ns_pinctrl_set_mux()` resolves the generic group and clears bits for all pins in the group in the control register.

## Control Flow
Probe determines the chipset flag from OF match data, maps the named `cru_gpio_control` resource, copies the base descriptor, filters supported pins into a device-managed descriptor array, registers pinctrl, and then adds only supported groups and functions to the generic registries. Applying a pinctrl state calls the generic function/group flow and then `ns_pinctrl_set_mux()`, which clears the relevant pin bits in the CRU GPIO control register.

## State And Persistence
The runtime state is the chipset flag, descriptor copy, pinctrl device, and MMIO base. Hardware mux state persists in the CRU GPIO control register. There is no GPIO, IRQ, or pinconf state in this driver.

## Dependencies And Integration Points
Depends on generic pinctrl/pinmux helpers, OF match data, named MMIO resources, and DT group mapping through `pinconf_generic_dt_node_to_map_group()`. It binds to `brcm,bcm4708-pinmux`, `brcm,bcm4709-pinmux`, and `brcm,bcm53012-pinmux`.

## Risks
The driver only clears bits for selected groups; the register's polarity and reset state must match the hardware contract. Chipset filtering must remain consistent between pins, groups, and functions or generic pinmux may expose a function whose pins were filtered out. There is no lock around the single read/modify/write register update, which is acceptable only if pinctrl state changes are serialized by higher layers.

## Test Signals
Test each compatible variant to ensure unsupported MDIO/UART2/SDIO pins are absent on BCM4708 and present on BCM4709/BCM53012. Apply SPI, I2C, MDIO, PWM, UART1, UART2, and SDIO states and verify CRU register bits and peripheral operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns.c -->
