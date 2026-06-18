# subset-b-001300 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpio/Makefile

## Purpose
This Makefile is the kernel build manifest for the GPIO subsystem under `drivers/gpio`. It selects core gpiolib objects, optional userspace and firmware integration layers, and a long alphabetized list of concrete GPIO controller and expander drivers.

## Important APIs, types, and functions
The file is Kbuild data rather than C code. Important build variables are `ccflags-$(CONFIG_DEBUG_GPIO) += -DDEBUG`, `obj-$(CONFIG_GPIOLIB)`, `obj-$(CONFIG_GPIO_CDEV)`, `obj-$(CONFIG_GPIO_REGMAP)`, `obj-$(CONFIG_GPIO_GENERIC)`, and per-driver `obj-$(CONFIG_GPIO_*) += gpio-*.o` entries. `gpiolib-acpi-y` composes the ACPI support object from core and quirks files, while `gpio-generic-$(CONFIG_GPIO_GENERIC) += gpio-mmio.o` folds `gpio-mmio.o` into the generic GPIO object.

## Control flow
Kbuild evaluates the `CONFIG_*` symbols chosen by Kconfig and appends matching objects into the directory build. Core gpiolib objects are listed first, followed by helper frameworks and individual device drivers sorted mostly alphabetically. There is no runtime control flow in this file.

## State and persistence behavior
The Makefile persists no runtime state. Its state effect is build-time: changing an `obj-*` line changes which modules or built-in objects exist in the produced kernel tree. `CONFIG_DEBUG_GPIO` also changes compilation by defining `DEBUG`.

## Dependencies and integration points
The file integrates all drivers in this directory with the kernel Kbuild system and with Kconfig symbols defined elsewhere. It also encodes helper relationships, notably `gpio-generic` including `gpio-mmio.o` and `gpiolib-acpi` including both ACPI core and quirk objects.

## Risks and edge cases
The main risks are omitted object mappings for new Kconfig symbols, typoed object names, and ordering/duplication mistakes that make a driver unavailable despite a visible Kconfig option. Since many entries build platform-specific code, accidental broad enablement can expose compile errors on unrelated architectures.

## Test signals
Useful signals are successful `make drivers/gpio/` or allmodconfig builds, module presence for enabled `CONFIG_GPIO_*` symbols, and no unresolved symbols from split helper objects such as `gpio-mmio.o`, `gpiolib-acpi-core.o`, or imported helper namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-dio-48e.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-dio-48e.c

## Purpose
This ISA driver supports ACCES 104-DIO-48E and 104-DIO-24E boards. It exposes two i8255 PPI blocks as 48 GPIO lines, wires the board interrupt sources into a regmap IRQ domain, and registers the on-board i8254 counter/timer through the i8254 regmap helper.

## Important APIs, types, and functions
Key module parameters are `base[]` and `irq[]`, registered with `module_param_hw_array()`. `struct dio48e_gpio` stores the shared raw spinlock, main regmap, MMIO/ioport mapping, saved IRQ flags, and current IRQ mask. Important helpers are `dio48e_regmap_lock()`, `pit_regmap_lock()`, `dio48e_handle_mask_sync()`, `dio48e_irq_init_hw()`, and `dio48e_probe()`. Integration hinges on `devm_regmap_init_mmio()`, `devm_regmap_add_irq_chip()`, `devm_i8254_regmap_register()`, and `devm_i8255_regmap_register()`.

## Control flow
`module_isa_driver_with_irq()` instantiates one device per configured base/IRQ pair. Probe reserves the I/O region, maps 16 ports, initializes a regmap with explicit readable/writable/volatile/precious ranges, initializes a second regmap view for the i8254, creates a regmap IRQ chip, disables interrupts before registration, registers the IRQ chip, registers the timer, and finally registers the i8255 GPIO block with line names and the IRQ domain.

## State and persistence behavior
State is hardware register state plus runtime driver state. The regmap uses `REGCACHE_FLAT`, the device interrupt enable state is mirrored in `irq_mask`, and the i8254 access window is enabled and disabled in the PIT regmap lock/unlock path. No filesystem state is persisted.

## Dependencies and integration points
The driver depends on ISA probing, I/O port resources, regmap, regmap-irq, raw spinlocks, the local `gpio-i8255.h` helper, and the i8254 helper namespace. It imports the `I8255` and `I8254` namespaces and publishes child GPIO IRQs only for bit 3 of Port C on each PPI.

## Risks and edge cases
The interrupt enable/disable register is accessed by writes and reads to the same offset, so precious regmap treatment matters. The shared lock also gates PIT address-window changes; a bug there could corrupt normal GPIO register accesses. Probe requires valid module base/IRQ arrays, and interrupt support is limited to rising edges on two PPI lines.

## Test signals
Test by loading with known `base=` and `irq=` values, verifying 48 named GPIO lines, toggling i8255 outputs, reading inputs, exercising the i8254 registration, and confirming the two supported GPIO IRQs enable, clear, and disable without spurious interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-dio-48e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-idi-48.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-idi-48.c

## Purpose
This ISA driver supports ACCES 104-IDI-48 input boards. It exposes 48 input-only GPIO lines through `gpio-regmap` and maps the board interrupt/status register into per-line IRQs.

## Important APIs, types, and functions
The module parameters `base[]` and `irq[]` define ISA instances. `idi_48_reg_mask_xlate()` maps logical GPIO offsets to sparse hardware port registers. `idi48_regmap_config` defines an 8-bit I/O-port regmap with read-only data ranges and precious IRQ status. `idi48_regmap_irqs[]` maps all 48 lines to six status bits by byte group. Probe uses `devm_regmap_add_irq_chip()` and `devm_gpio_regmap_register()`.

## Control flow
Probe reserves an 8-port ISA range, maps it, initializes regmap access, allocates a regmap IRQ chip with status/unmask at register `0x7`, registers the shared IRQ, then creates a `gpio_regmap_config` with `reg_dat_base = 0`, 8 GPIOs per register, custom mask translation, line names, and the regmap IRQ domain.

## State and persistence behavior
The driver keeps no private mutable state beyond devres-managed objects. GPIO values and interrupt status are read from hardware. The regmap is raw-spinlocked and treats the IRQ status register as precious to avoid accidental destructive reads.

## Dependencies and integration points
It depends on ISA, I/O port resources, regmap, regmap-irq, and `gpio-regmap`. It integrates with gpiolib as a sleeping-safe regmap GPIO provider and with the IRQ subsystem through a regmap IRQ domain.

## Risks and edge cases
The hardware is input-only, so write access is explicitly denied for data registers. The IRQ model groups lines behind byte-level status bits; wrong mask translation would report the wrong line or miss an edge. `IRQF_SHARED` is used, so shared interrupt behavior should be considered during board bring-up.

## Test signals
Expected signals are a 48-line GPIO chip with names for groups A and B, correct reads across the sparse register layout, no output direction support, and edge-both IRQ delivery for all lines when the configured ISA IRQ is asserted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-idi-48.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-idio-16.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-idio-16.c

## Purpose
This driver supports ACCES 104-IDIO-16 family ISA boards and related 8/16-channel variants. It delegates the common IDIO-16 GPIO behavior to `gpio-idio-16.h` while providing the board-specific I/O range, regmap layout, and IRQ descriptions.

## Important APIs, types, and functions
Module parameters `base[]` and `irq[]` enumerate boards. `idio_16_regmap_config` defines writable output/control ranges, readable input/status ranges, volatile reads, and precious interrupt status. `idio_16_regmap_irqs[]` describes edge-both IRQs for input GPIOs 16 through 31. `idio_16_probe()` wires these into `devm_idio_16_regmap_register()`.

## Control flow
The ISA driver claims an 8-port region, maps it, initializes the regmap, fills `struct idio_16_regmap_config` with the regmap, IRQ table, hardware IRQ, and `no_status = true`, then registers the common IDIO-16 regmap GPIO implementation.

## State and persistence behavior
State is held in the board registers and in regmap cache. The driver itself has no long-lived private structure beyond devres-managed objects. Output register values may be cached by regmap; input and status registers are volatile.

## Dependencies and integration points
Dependencies are ISA, ioport mapping, regmap, and the local `GPIO_IDIO_16` helper namespace. The helper owns most GPIO operations, while this file supplies the ACCES 104-IDIO-16 register access contract.

## Risks and edge cases
Only input lines support IRQs, so consumers must not expect interrupts for output lines. The status register is precious and can be side-effectful. Incorrect base/IRQ module parameters or conflicting I/O regions will fail probe.

## Test signals
Load with valid base/IRQ parameters, confirm the helper exposes the expected output/input split, verify writes affect output lines only, reads work for input lines, and edge-both interrupts are delivered for GPIOs 16-31.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-idio-16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-74x164.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-74x164.c

## Purpose
This SPI driver exposes chained 74HC595/74LVC594-style serial-in parallel-out shift registers as output-only GPIO lines. It maintains a software image of the shift-register chain and writes the whole chain over SPI on updates.

## Important APIs, types, and functions
`struct gen_74x164_chip` contains the `gpio_chip`, mutex, optional output-enable GPIO descriptor, register count, and reversed byte buffer. Core callbacks are `gen_74x164_get_value()`, `gen_74x164_set_value()`, `gen_74x164_set_multiple()`, and `gen_74x164_direction_output()`. Probe uses `device_property_read_u32("registers-number")`, `spi_setup()`, `spi_write()`, `devm_gpiod_get_optional()`, and `devm_gpiochip_add_data()`.

## Control flow
Probe forces 8-bit SPI words, reads the number of chained registers, allocates the variable-size chip object, optionally gets the enable line, initializes the GPIO chip, writes the all-zero initial buffer, asserts output enable through a devm cleanup action, and registers the chip. Set operations update the software buffer under a mutex and then shift out all bytes.

## State and persistence behavior
The authoritative software state is `buffer[]`; the hardware shift registers only hold the last successfully shifted image and cannot be read back. Byte order is reversed so logical GPIO numbering stays intuitive across chained devices. The optional enable line is deasserted automatically on teardown.

## Dependencies and integration points
The driver depends on SPI, gpiolib, firmware properties, optional GPIO consumers for output enable, and mutex locking because SPI transfers can sleep. Compatible IDs include `fairchild,74hc595` and `nxp,74lvc594`.

## Risks and edge cases
Failed SPI writes can leave `buffer[]` ahead of hardware state. Direction input is unsupported by omission, so consumers must treat the chip as output-only. Incorrect `registers-number` changes line count and shift order. Output-enable polarity is controlled by the GPIO descriptor binding.

## Test signals
A good test checks `ngpio == registers-number * 8`, initial all-low SPI write, single-line and `set_multiple` byte ordering across multiple registers, `get` returning the cached state, and enable GPIO assertion/deassertion at probe/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-74x164.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-74xx-mmio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-74xx-mmio.c

## Purpose
This platform driver exposes simple memory-mapped 74xx logic devices as GPIO chips. Device-tree compatible data describes whether the device is input-only or output-only and how many bits it provides.

## Important APIs, types, and functions
`struct mmio_74xx_gpio_priv` wraps `struct gpio_generic_chip` plus encoded flags. Match data combines `MMIO_74XX_DIR_IN` or `MMIO_74XX_DIR_OUT` with a bit count. GPIO callbacks are `mmio_74xx_get_direction()`, `mmio_74xx_dir_in()`, and `mmio_74xx_dir_out()`. Probe uses `devm_platform_ioremap_resource()`, `gpio_generic_chip_init()`, and `devm_gpiochip_add_data()`.

## Control flow
Probe reads match data, maps one MMIO data register region, initializes a generic GPIO chip with byte size derived from the bit count, then overrides direction callbacks to enforce fixed hardware direction. Output direction writes the requested value through the generic set path.

## State and persistence behavior
There is no private persistent state beyond match flags. Values live in the external latch or buffer hardware and generic GPIO state. Direction is fixed by compatible string and never changed in hardware.

## Dependencies and integration points
The driver depends on OF matching, platform MMIO resources, and `gpio-generic`. It integrates a family of TI 74xx-compatible parts into gpiolib without per-chip C implementations.

## Risks and edge cases
Using the wrong compatible can expose the wrong line count or direction. Input attempts on output-only parts and output attempts on input-only parts return `-ENOTSUPP`. The generic chip assumes a simple contiguous data register sized by the encoded bit count.

## Test signals
Verify each compatible reports the expected `ngpio` and fixed direction, input-only devices reject output direction, output-only devices reject input direction, and MMIO writes/readbacks match the external latch wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-74xx-mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-adnp.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-adnp.c

## Purpose
This I2C driver supports Avionic Design N-bit GPIO expanders. It exposes configurable GPIO lines over SMBus byte registers and can emulate nested GPIO IRQs using the expander's interrupt status, enable, and sampled level registers.

## Important APIs, types, and functions
`struct adnp` stores the I2C client, GPIO chip, register shift, I2C and IRQ locks, and six per-register IRQ state arrays. GPIO operations include `adnp_gpio_get()`, `adnp_gpio_set()`, `adnp_gpio_direction_input()`, `adnp_gpio_direction_output()`, and optional `adnp_gpio_dbg_show()`. IRQ support is implemented by `adnp_irq()`, `adnp_irq_mask()`, `adnp_irq_unmask()`, `adnp_irq_set_type()`, bus-lock callbacks, and `adnp_irq_setup()`.

## Control flow
Probe reads `nr-gpios`, allocates state, initializes the I2C lock, computes register layout from GPIO count, fills the GPIO chip, optionally initializes IRQ state when `interrupt-controller` is present, and registers the GPIO chip. GPIO direction and value operations perform locked SMBus reads and writes. The threaded IRQ reads level/status/enable registers, computes edge and level pending bits from cached trigger configuration, and invokes nested child IRQs.

## State and persistence behavior
Direction, level, IRQ enable, and status live on the expander. Runtime IRQ policy is mirrored in `irq_enable`, `irq_level`, `irq_rise`, `irq_fall`, `irq_high`, and `irq_low`; these arrays are synchronized to hardware during IRQ bus unlock. No nonvolatile state is written.

## Dependencies and integration points
The driver depends on I2C SMBus byte access, gpiolib, threaded IRQs, firmware properties, debugfs sequence output, and nested IRQ handling. It integrates as an I2C driver with ID `gpio-adnp` and OF compatible `ad,gpio-adnp`.

## Risks and edge cases
I2C failures are propagated and can make GPIO reads or IRQ processing incomplete. Edge detection depends on the initial and later cached levels, but the handler as written computes `changed` against `irq_level` without updating it in the loop, so maintainers should verify whether repeated edges are expected to refresh cached state elsewhere. Direction changes read back DDR bits and return `-EPERM` if hardware refuses the change.

## Test signals
Test GPIO direction/value over I2C, debugfs register display, invalid `nr-gpios`, interrupt-controller setup with edge and level trigger types, nested IRQ delivery, and IER writes after mask/unmask bus synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-adnp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-adp5520.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-adp5520.c

## Purpose
This platform driver exposes the GPIO pins of the Analog Devices ADP5520 MFD PMIC. It maps enabled PMIC pins from platform data into a compact GPIO chip.

## Important APIs, types, and functions
`struct adp5520_gpio` stores the parent MFD device, `gpio_chip`, a logical-to-register-bit lookup table, and an `output` bitmap. Callbacks are `adp5520_gpio_get_value()`, `adp5520_gpio_set_value()`, `adp5520_gpio_direction_input()`, and `adp5520_gpio_direction_output()`. Probe consumes `struct adp5520_gpio_platform_data` and MFD helpers `adp5520_read()`, `adp5520_set_bits()`, and `adp5520_clr_bits()`.

## Control flow
Probe requires platform data and `pdev->id == ID_ADP5520`, builds the LUT from `gpio_en_mask`, initializes the GPIO chip, disables alternate GPIO config bits, enables C3/R3 GPIO modes when needed, applies pullups, and registers the chip. Get reads either GPIO_OUT or GPIO_IN depending on cached direction.

## State and persistence behavior
The driver stores logical output direction in `output`; PMIC registers store output values, direction bits, GPIO/LED mux mode, and pullups. Runtime changes persist in PMIC registers until changed by another PMIC consumer or reset.

## Dependencies and integration points
It depends on the ADP5520 MFD core, legacy platform data, and gpiolib. The GPIO chip uses the platform-supplied base when provided and can sleep because parent MFD register access may sleep.

## Risks and edge cases
The driver is platform-data only and rejects non-ADP5520 IDs. It uses bitwise OR accumulation for multi-step register writes, so the first failing MFD operation must still be noticed. The `output` bitmap is local state and may become stale if another function changes direction outside this driver.

## Test signals
Useful tests cover missing platform data, zero enabled GPIOs, C3/R3 mode setup, pullup mask writes, input versus output reads using the proper register, and correct logical line mapping through `lut[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-adp5520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-adp5585.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-adp5585.c

## Purpose
This platform driver exposes GPIO support for ADP5585 and ADP5589 MFD devices. It handles variant-specific bank layouts, pin configuration, shared pin ownership, and optional GPIO IRQs sourced from the parent key/event notifier.

## Important APIs, types, and functions
`struct adp5585_gpio_chip` describes variant register bases, bank/bit mapping, event ranges, and bias layout. `struct adp5585_gpio_dev` stores the GPIO chip, notifier, regmap, and IRQ masks. GPIO callbacks include direction, get/set, `adp5585_gpio_set_config()`, `adp5585_gpio_request()`, and `adp5585_gpio_free()`. IRQ paths include `adp5585_gpio_key_event()`, `adp5585_irq_mask()`, `adp5585_irq_unmask()`, `adp5585_irq_set_type()`, and bus sync.

## Control flow
Probe gets the parent `struct adp5585_dev`, chooses ADP5585 or ADP5589 chip info from platform ID, inherits the parent's OF node, initializes GPIO callbacks, and optionally sets up an immutable irqchip when the parent advertises `interrupt-controller`. For IRQs it registers a blocking notifier on the parent event chain; key events in the GPIO event range are translated to child IRQs after active-high and edge-type checks.

## State and persistence behavior
Pin direction, output data, pull configuration, drive mode, debounce, and event enable state live in regmap registers. Runtime driver state includes parent `pin_usage`, `irq_mask`, `irq_en`, and `irq_active_high`. All IRQs start masked; bus sync writes changed enable and active-level bits.

## Dependencies and integration points
The driver depends on the ADP5585 MFD core, regmap, gpiolib, pinconf packed configs, and the parent event notifier. It integrates with shared keypad/GPIO pin muxing by claiming bits in `adp5585->pin_usage` and clearing parent pin config to GPIO mode.

## Risks and edge cases
Variant bank/bit math differs between ADP5585 and ADP5589, and ADP5585 has a pull-config bitfield hole after R5. GPIO IRQs are edge-only and rely on parent key-event delivery rather than a direct chained interrupt. Consumers must request pins to avoid conflicts with keypad or other parent functions.

## Test signals
Test pin request conflicts, reserved/missing pins, direction and output register writes by bank, bias/drive/debounce pinconf operations, notifier registration cleanup, edge-rising/falling IRQ delivery from parent events, and ADP5585 versus ADP5589 register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-adp5585.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-aggregator.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-aggregator.c

## Purpose
This module creates virtual GPIO chips by aggregating existing GPIO descriptors. It provides a modern configfs interface, a legacy sysfs `new_device`/`delete_device` interface, a platform driver that consumes generated lookup tables, and exported GPIO forwarder APIs for other drivers.

## Important APIs, types, and functions
User-facing state is represented by `struct gpio_aggregator` and `struct gpio_aggregator_line`; forwarding state is `struct gpiochip_fwd`. Important lifecycle helpers are `gpio_aggregator_alloc()`, `gpio_aggregator_activate()`, `gpio_aggregator_deactivate()`, `gpio_aggregator_parse()`, `gpio_aggregator_probe()`, and module init/exit. Exported forwarder APIs include `devm_gpiochip_fwd_alloc()`, `gpiochip_fwd_desc_add()`, `gpiochip_fwd_register()`, and directional/get/set/config/IRQ helpers in the `GPIO_FORWARDER` namespace.

## Control flow
Configfs users create an aggregator group, create sequential `lineN` groups, set `key`, `offset`, and optional `name`, then write `live=1`. Activation builds a software node with line names, creates a lookup table, registers a platform device, waits for probing, and locks configfs entries while live. Legacy sysfs parses a flat argument string into the same line structures and immediately registers the platform device. The platform probe resolves all GPIO descriptors and registers a forwarding gpiochip.

## State and persistence behavior
State lives in configfs/sysfs-created kernel objects, an IDR, lookup tables, platform devices, GPIO descriptors, valid masks, and optional per-line delay timings. It is runtime-only and removed on deactivation or module unload. Forwarded GPIO values remain owned by the original GPIO providers.

## Dependencies and integration points
The file integrates configfs, platform devices, software nodes, gpiod lookup tables, gpiolib descriptor consumers, optional OF GPIO translation for `gpio-delay`, IDR allocation, and exported symbols for external forwarder users. It forwards operations to `gpiod_*` APIs and preserves sleep semantics for descriptor arrays.

## Risks and edge cases
Major risks are lifetime and locking bugs between configfs, sysfs, module references, and platform device probing. Configfs activation rejects nonsequential or incomplete line definitions, and config entries become busy while live. Forwarders with any sleeping or not-yet-populated line mark the whole chip `can_sleep`. The delay feature mutates per-line timing during OF translation and sleeps or busy-waits after set operations.

## Test signals
Test configfs creation, invalid line names/order, live activation/deactivation, legacy sysfs parsing for chip+offset lists and named lines, deferred probe handling, forwarded get/set/get_multiple/set_multiple/config/to_irq behavior, active-low delay timing, and module unload cleanup of legacy aggregators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-aggregator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-altera-a10sr.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-altera-a10sr.c

## Purpose
This platform driver exposes GPIO lines on the Altera Arria10 MAX5 System Resource Chip through the parent MFD regmap. It represents LED/output and pushbutton/DIP-switch input functions as one 12-line GPIO chip.

## Important APIs, types, and functions
`struct altr_a10sr_gpio` stores a `gpio_chip` and parent regmap. Callbacks are `altr_a10sr_gpio_get()`, `altr_a10sr_gpio_set()`, `altr_a10sr_gpio_direction_input()`, and `altr_a10sr_gpio_direction_output()`. Probe clones `altr_a10sr_gc`, sets parent/fwnode, and registers with `devm_gpiochip_add_data()`.

## Control flow
Probe obtains the parent `struct altr_a10sr`, stores its regmap, copies the static chip template, and registers the chip. Input direction is accepted only for offsets in the input-valid range; output direction is accepted only for offsets in the output-valid range and writes the initial value.

## State and persistence behavior
GPIO state lives in the parent chip registers: reads use `ALTR_A10SR_PBDSW_REG`, writes update `ALTR_A10SR_LED_REG`. The driver stores no cache and relies on regmap for access serialization.

## Dependencies and integration points
The driver depends on the `altera-a10sr` MFD core, regmap, gpiolib, and OF compatible `altr,a10sr-gpio`. It uses the platform device fwnode for GPIO firmware bindings while setting the chip parent to the MFD parent.

## Risks and edge cases
Offset arithmetic is tied to `ALTR_A10SR_LED_VALID_SHIFT` and valid-range constants. The `get` path uses `BIT(offset - shift)`, so invalid output offsets should be filtered by direction/consumer usage to avoid nonsensical bit positions. The chip is sleeping because parent register access may sleep.

## Test signals
Check `ngpio == 12`, valid input/output range enforcement, LED register updates for outputs, pushbutton/DIP reads for inputs, and probe through an Arria10 system-resource MFD child node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-altera-a10sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-altera.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-altera.c

## Purpose
This platform driver supports Altera PIO memory-mapped GPIO controllers. It exposes up to 32 software-controlled GPIOs and optionally wires a parent interrupt into child GPIO IRQs.

## Important APIs, types, and functions
`struct altera_gpio_chip` stores the `gpio_chip`, MMIO base, raw spinlock, and configured interrupt trigger. GPIO callbacks are `altera_gpio_get()`, `altera_gpio_set()`, `altera_gpio_direction_input()`, and `altera_gpio_direction_output()`. IRQ callbacks include mask/unmask, set type, startup, edge handler, level-high handler, and `altera_gpio_irq_chip`.

## Control flow
Probe allocates state, reads `altr,ngpio` with a 32-line maximum, maps MMIO, sets GPIO callbacks, and optionally sets up an irqchip if a parent IRQ exists. Interrupt setup requires `altr,interrupt-type`; the parent handler is chosen based on level-high versus edge capture behavior. The driver registers during `subsys_initcall`.

## State and persistence behavior
Direction, data, interrupt mask, and edge-capture state are hardware MMIO registers. The raw spinlock serializes read-modify-write sequences for data, direction, and IRQ masks. The configured interrupt trigger is stored in driver memory and treated as immutable hardware synthesis.

## Dependencies and integration points
Dependencies are platform MMIO resources, OF compatible `altr,pio-1.0`, gpiolib, generic IRQ domains via `gpio_irq_chip`, and chained interrupt handling. It integrates with gpiolib as a normal memory-mapped controller.

## Risks and edge cases
The hardware supports only one synthesized IRQ trigger type, so `irq_set_type()` rejects mismatches. Edge handling loops until no masked edge status remains, while level-high handling samples data once. Overlarge `altr,ngpio` is capped with a warning. Missing `altr,interrupt-type` with an IRQ present fails probe.

## Test signals
Test GPIO direction/value RMW under concurrent access, ngpio default/cap behavior, no-IRQ probe path, each supported interrupt trigger type, edge capture clearing, and level-high child IRQ dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-altera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-amd-fch.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-amd-fch.c

## Purpose
This platform driver exposes GPIO pins on AMD G-series FCH hardware such as GX-412TC. It uses platform data to map logical GPIO lines to registers in the fixed FCH MMIO GPIO bank.

## Important APIs, types, and functions
`struct amd_fch_gpio_priv` stores the `gpio_chip`, MMIO base, platform data, and spinlock. `amd_fch_gpio_addr()` translates logical offsets through `pdata->gpio_reg[]`. GPIO operations are direction input/output, get direction, get, set, and a no-op request callback. Probe maps the fixed resource at `0xFED81500`.

## Control flow
Probe requires `struct amd_fch_gpio_pdata`, allocates state, fills line count and names from platform data, initializes callbacks and lock, maps the global MMIO resource, stores drvdata, and registers the chip. Each GPIO operation locks, reads the selected register, updates direction/write bits as needed, and writes it back.

## State and persistence behavior
State is in FCH MMIO registers. Direction uses bit 23, output write state uses bit 22, and input read state uses bit 16. No cache is maintained, and register changes persist until hardware reset or another agent modifies them.

## Dependencies and integration points
The driver depends on platform data from `gpio-amd-fch.h`, platform devices, fixed MMIO mapping, and gpiolib. It has no IRQ support in this file.

## Risks and edge cases
The fixed MMIO base assumes the platform data/device is created only for compatible systems. Incorrect `gpio_reg[]` mapping can access the wrong FCH registers. The request callback does not reserve or mux pins, so board code must ensure pins are safe for GPIO use.

## Test signals
Validate probe with platform data, correct line names/count, direction bit transitions, output bit writes, input read bit extraction via `FIELD_GET`, and rejection when platform data is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-amd-fch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-amd8111.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-amd8111.c

## Purpose
This module exposes the 32 GPIO pins in AMD 8111 south bridge PM I/O space. It discovers the chipset by scanning PCI devices rather than binding a PCI driver, then registers a single global gpiochip.

## Important APIs, types, and functions
`struct amd_gpio` contains the gpiochip, PM base, mapped PM I/O region, PCI device reference, spinlock, and `orig[32]` saved per-pin modes. Callbacks are `amd_gpio_request()`, `amd_gpio_free()`, `amd_gpio_set()`, `amd_gpio_get()`, `amd_gpio_dirout()`, and `amd_gpio_dirin()`. Module lifecycle is `amd_gpio_init()` and `amd_gpio_exit()`.

## Control flow
Init scans all PCI devices for AMD 8111 SMBus ID, reads PM base from config offset `0x58`, reserves and maps PM I/O ports, initializes the global chip, and registers it. Request saves each pin's debounce/mode/output-control bits; free restores the saved bits. Direction and set callbacks rewrite the mode and output state.

## State and persistence behavior
Hardware state is PM I/O register state. Driver state includes the global PCI device reference, mapping, lock, and original per-pin configuration captured on request. Free restores the captured mode, making request/free boundaries stateful.

## Dependencies and integration points
The driver depends on PCI enumeration, I/O port resources, legacy ioport mapping, gpiolib, and spinlock protection. It deliberately avoids registering a PCI driver so other functions can own the same multifunction PCI ID.

## Risks and edge cases
Only one south bridge is assumed. Global static state prevents multiple instances. Restoring `orig[]` on free is useful but can overwrite changes by other firmware/drivers after request. `devm_request_region()` is used with the PCI device in a module-init flow, while `ioport_unmap()` and `pci_dev_put()` are handled manually.

## Test signals
Test on AMD 8111 hardware for PM base discovery, gpiochip registration, request/free restoration, input and output modes, debug messages, and clean module unload with region unmap and PCI reference release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-amd8111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-amdpt.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-amdpt.c

## Purpose
This ACPI platform driver supports AMD Promontory GPIO controllers. It wraps a small MMIO register block with `gpio-generic` and adds request/free ownership tracking through a sync register.

## Important APIs, types, and functions
`struct pt_gpio_chip` contains a `gpio_generic_chip` and MMIO base. `pt_gpio_request()` checks and sets `PT_SYNC_REG` bits, while `pt_gpio_free()` clears them. Probe initializes generic GPIO registers for input, output, direction, and read-output behavior. ACPI IDs map to either 8 or 24 GPIOs.

## Control flow
Probe requires an ACPI companion, allocates and maps the resource, initializes `gpio_generic_chip_config`, sets request/free and line count, registers the chip, clears sync state, and initializes clock-rate register to zero.

## State and persistence behavior
GPIO direction/value state is MMIO hardware state. The driver also uses `PT_SYNC_REG` as an ownership bitmap to reject pins already marked in use, clearing it at probe. No persistent storage is used.

## Dependencies and integration points
It depends on ACPI matching, platform MMIO resources, and `gpio-generic`. Supported ACPI IDs are `AMDF030`, `AMDIF030`, and `AMDIF031`.

## Risks and edge cases
Probe refuses non-ACPI devices. Clearing `PT_SYNC_REG` at probe assumes no other live firmware user needs existing ownership state. Request returning `-EINVAL` for an already marked pin protects against reconfiguration but can surprise consumers that do not request explicitly.

## Test signals
Verify ACPI match line counts, MMIO generic get/set/direction behavior, sync register set/clear on request/free, rejection of already-used pins, and initialization writes to sync and clock-rate registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-amdpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-arizona.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-arizona.c

## Purpose
This platform driver exposes GPIO lines on Wolfson/Cirrus Arizona class MFD audio devices. It uses the parent regmap and runtime PM to handle cached register reads and persistent GPIO lines correctly.

## Important APIs, types, and functions
`struct arizona_gpio` stores the parent `struct arizona` and `gpio_chip`. Callbacks are `arizona_gpio_direction_in()`, `arizona_gpio_get()`, `arizona_gpio_direction_out()`, and `arizona_gpio_set()`. Probe selects `ngpio` from the parent chip type and uses optional pdata `gpio_base`.

## Control flow
Probe inherits the parent fwnode, allocates state, copies the chip template, chooses 5 or 2 GPIO lines based on Arizona variant, enables runtime PM, and registers the gpiochip. Input reads first check direction; for input pins they resume the parent, drop the regcache region, physically read the GPIO control register, and autosuspend again.

## State and persistence behavior
Direction and level are stored in parent GPIO control registers. Runtime PM state is adjusted for persistent lines: switching a persistent line to input releases runtime PM, while switching from input to output may resume the device. Regcache is explicitly dropped for live input reads.

## Dependencies and integration points
The driver depends on the Arizona MFD core, regmap/regcache, runtime PM, gpiolib persistent-line support, platform data, and platform device binding `arizona-gpio`.

## Risks and edge cases
Runtime PM failure paths must put references correctly. Cached registers cannot be trusted for input levels, hence the cache drop; missing this would report stale values. Unknown parent chip variants fail probe. Direction semantics depend on `ARIZONA_GPN_DIR` polarity.

## Test signals
Test variant-specific line counts, runtime PM reference behavior on persistent lines, cache-drop live input reads, output set/direction writes, gpio_base handling, and unknown variant rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-arizona.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-aspeed-sgpio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-aspeed-sgpio.c

## Purpose
This platform driver supports Aspeed serial GPIO masters on AST2400/2500, AST2600 SGPIOM, and AST2700 SGPIOM. It exposes paired input/output logical lines for serial GPIO pins and provides IRQ support on input lines.

## Important APIs, types, and functions
`struct aspeed_sgpio` stores the gpiochip, device, clock, raw spinlock, MMIO base, parent IRQ, and SoC pdata. `struct aspeed_sgpio_llops` abstracts generation-specific register access. GPIO callbacks include `aspeed_sgpio_get()`, `aspeed_sgpio_set()`, direction helpers, and `aspeed_sgpio_set_config()`. IRQ callbacks include ack, mask/unmask, type setup, handler, and valid-mask initialization.

## Control flow
Probe reads `ngpios` and `bus-frequency`, calculates the SGPIO clock divider from APB clock, writes the enable/config register, initializes callbacks, calls `aspeed_sgpio_setup_irqs()`, and registers the chip with `ngpio = nr_gpios * 2`. Even offsets are inputs and odd offsets are outputs. IRQ setup disables and clears all input IRQs, configures default falling/level-low style bits, and attaches a chained parent handler.

## State and persistence behavior
State is MMIO hardware state: data, output latch, IRQ enable/type/status, reset tolerance, and generation-specific control registers. The raw spinlock serializes register bit operations. Persistent-state pinconf toggles reset tolerance bits.

## Dependencies and integration points
The driver depends on platform MMIO resources, OF match data, a clock provider, gpiolib, pinconf packed configs, and chained IRQ handling. Generation-specific integration is through `aspeed_sgpio_g4_llops` for AST2400/2600 and `aspeed_sgpio_g7_llops` for AST2700.

## Risks and edge cases
The logical offset model is unusual: input GPIOs are even, output GPIOs are odd, and IRQs are valid only on inputs. `ngpios` must be a multiple of 8 and the divider must fit 16 bits. AST2700 uses per-pin control registers unlike earlier banked registers, so low-level ops must match the compatible.

## Test signals
Test invalid `ngpios` and zero/too-low bus frequencies, divider programming, input/output direction rejection on wrong parity, IRQ valid mask, IRQ type programming, status dispatch to even offsets, and reset-tolerance pinconf on each supported compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-aspeed-sgpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-aspeed.c

## Purpose
This is the main Aspeed parallel GPIO controller driver for AST2400, AST2500, AST2600, and AST2700 SoCs. It supports GPIO direction/value operations, IRQs, debounce timers, reset tolerance, pinctrl interaction, and optional coprocessor ownership handshaking.

## Important APIs, types, and functions
`struct aspeed_gpio` stores the gpiochip, MMIO base, lock, IRQ, SoC config, debounce timer accounting, optional clock, output data cache, and coprocessor bank map. `struct aspeed_gpio_llops` abstracts generation-specific register access and coprocessor privilege control. Exported coprocessor APIs are `aspeed_gpio_copro_set_ops()`, `aspeed_gpio_copro_grab_gpio()`, and `aspeed_gpio_copro_release_gpio()`.

## Control flow
Probe maps MMIO, obtains config and optional clock, sets line count from `ngpios` or config fallback, initializes GPIO callbacks and optional data cache, initializes coprocessor privilege to ARM where supported, wires a chained IRQ chip, allocates debounce accounting, and registers the chip. GPIO operations check bank capability masks, optionally request coprocessor access, update registers, and release access. IRQ handling reads status banks and dispatches child IRQs.

## State and persistence behavior
Hardware registers store value, direction, IRQ type/status/enable, debounce selector bits, reset tolerance, and command source. Runtime state includes debounce timer allocation (`offset_timer`, `timer_users`), optional `dcache` for output registers on G4-style hardware, global coprocessor callbacks, and per-bank coprocessor reference counts.

## Dependencies and integration points
The driver depends on OF platform resources, clocks, gpiolib, irqchip chaining, pinctrl GPIO request/free/config, packed pinconf, and internal Aspeed GPIO consumer APIs. AST2400/2500/2600 use banked G4-style ops; AST2700 uses G7 per-line control registers and no coprocessor callbacks.

## Risks and edge cases
Debounce has only three usable hardware timers; exhaustion disables the line's timer selection and returns an error. Coprocessor ownership is global and bank-counted, so imbalance returns errors and can leave command source ownership wrong. Bank property masks expose holes as unavailable lines. Missing clocks disable debounce. G4 output writes depend on a synchronized `dcache`.

## Test signals
Test line availability masks for each SoC, pinctrl request/free, direction and output cache behavior, all IRQ trigger types and valid masks, debounce timer reuse/exhaustion/disable, reset tolerance config, coprocessor grab/release balance, and AST2700 G7 register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ath79.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ath79.c

## Purpose
This platform driver supports GPIO controllers in Atheros/QCA AR71xx, AR724x, AR913x, and related ath79 SoCs. It uses `gpio-generic` for basic MMIO GPIO operations and implements optional interrupt-controller support.

## Important APIs, types, and functions
`struct ath79_gpio_ctrl` wraps a `gpio_generic_chip`, MMIO base, and `both_edges` bitmap. IRQ functions include mask/unmask, enable/disable, set type, and `ath79_gpio_irq_handler()`. Probe reads `ngpios`, detects AR9340 output-enable polarity, initializes generic GPIO registers, and optionally fills `gpio_irq_chip`.

## Control flow
Probe validates `ngpios < 32`, maps MMIO, configures generic GPIO data/set/clear/direction registers, and registers the chip. If `interrupt-controller` is present, it allocates a parent IRQ array and uses a chained handler. Edge-both interrupts are emulated by flipping polarity based on the current input state whenever pending status is handled.

## State and persistence behavior
GPIO and IRQ state is hardware register state. The driver keeps only the `both_edges` bitmap to remember which lines need polarity toggling. Generic GPIO locking protects register read-modify-write sequences.

## Dependencies and integration points
Dependencies are OF platform binding, `gpio-generic`, gpiolib irqchip helpers, and chained interrupt handling. Compatible strings include `qca,ar7100-gpio` and `qca,ar9340-gpio`.

## Risks and edge cases
Both-edge emulation can miss very fast toggles if polarity cannot be updated between edges. Direction register polarity differs for AR9340. The driver rejects 32 or more GPIOs because bit operations assume a sub-32-bit controller. Parent IRQ retrieval is stored directly without checking for negative values in the optional branch.

## Test signals
Test both compatible variants, `ngpios` validation, generic get/set/direction operations, interrupt-controller presence/absence, rising/falling/level trigger programming, both-edge polarity updates, and child IRQ dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ath79.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bcm-kona.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bcm-kona.c

## Purpose
This built-in platform driver supports Broadcom Kona GPIO controllers. It exposes banked GPIO lines, per-bank parent IRQs, GPIO lock/unlock protection registers, debounce configuration, and an irqdomain for GPIO interrupts.

## Important APIs, types, and functions
`struct bcm_kona_gpio` stores MMIO base, bank count, raw spinlock, gpiochip, irqdomain, and flexible bank array. `struct bcm_kona_gpio_bank` stores bank ID, parent IRQ, unlock counts, and back pointer. GPIO callbacks cover request/free, direction, get/set, debounce config, and `to_irq`. IRQ support uses `bcm_gpio_irq_chip`, custom irqdomain ops, chained bank handlers, and request/release resource hooks.

## Control flow
Probe counts platform IRQs to determine bank count, allocates state, creates a linear IRQ domain, maps MMIO, records each bank parent IRQ, resets hardware by unlocking banks, masking/clearing interrupts, and relocking, registers the gpiochip, installs chained handlers for each bank, and initializes the lock. GPIO and IRQ resource requests unlock per-pin registers; releases relock them when both GPIO and IRQ users are gone.

## State and persistence behavior
Hardware stores direction, output/input status, interrupt mask/status, debounce, and lock state. The driver maintains per-pin `gpio_unlock_count[]` to handle overlapping GPIO and IRQ ownership safely. IRQ mappings live in the irqdomain until removal.

## Dependencies and integration points
The driver depends on platform IRQ resources, OF compatible `brcm,kona-gpio`, irqdomain APIs, chained IRQs, gpiolib, and pinconf debounce. It uses lockdep classes for child IRQs to avoid false recursion reports.

## Risks and edge cases
Balanced lock/unlock accounting is critical; unbalanced locks log errors and can leave pins writable or locked unexpectedly. Level IRQs are unsupported. The driver manually removes the irqdomain on probe failure but is built-in, so teardown paths are minimal. Debounce accepts only 0 or 1-128 ms.

## Test signals
Test bank-count detection, max-bank rejection, reset masking/clearing, GPIO request/free lock counts, direction/value operations, debounce rounding, `to_irq` mapping, edge IRQ types, bank chained handlers, and simultaneous GPIO plus IRQ consumers on one line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bcm-kona.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd71815.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd71815.c

## Purpose
This platform driver exposes BD71815/BD71817 PMIC GPO pins as gpiolib lines. The hardware is output-only, with an optional hidden second GPO that is disabled unless explicitly enabled by device property.

## Important APIs, types, and functions
`struct bd71815_gpio` stores the gpiochip, device, and parent regmap. Operations are `bd71815gpo_get()`, `bd71815gpo_set()`, `bd71815_gpio_set_config()`, `bd71815gpo_direction_get()`, and `bd71815_init_valid_mask()`. Probe uses `dev_get_regmap()` from the parent MFD and registers a template gpiochip.

## Control flow
Probe copies the output-only chip template, sets `ngpio` to 1 by default or 2 when `rohm,enable-hidden-gpo` is present, installs the valid-mask callback, assigns the parent regmap, and registers the chip. Set/get operate on `BD71815_REG_GPO`; pin config selects open-drain or CMOS drive.

## State and persistence behavior
The GPO output and drive state live in the PMIC GPO register. The driver keeps no cache. The valid mask/line count is derived from firmware property at probe.

## Dependencies and integration points
The driver depends on the ROHM BD71815 MFD regmap, platform device creation, gpiolib, and pinconf drive-mode configs. The GPIO chip parent is the MFD parent so firmware properties are read from the PMIC node.

## Risks and edge cases
The hidden GPO may be physically tied to ground, so enabling it can be unsafe on boards not designed for it. The driver sets `ngpio` to 1 by default because legacy sysfs may ignore `valid_mask`. There is no input or IRQ support.

## Test signals
Test default one-line exposure, hidden GPO opt-in, output-only direction reporting, set/get register bits, open-drain/push-pull pinconf writes, and missing parent regmap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd71815.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd71828.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd71828.c

## Purpose
This platform driver exposes four BD71828 PMIC GPIO-related pins, including a special HALL input pin. Most pins are treated as output-only because their OTP-selected roles cannot be read at runtime.

## Important APIs, types, and functions
`struct bd71828_gpio` stores regmap, device, and gpiochip. Operations are `bd71828_gpio_set()`, `bd71828_gpio_get()`, `bd71828_gpio_set_config()`, and `bd71828_get_direction()`. `GPIO_OUT_REG(off)` maps logical pins to consecutive GPIO control registers, and `HALL_GPIO_OFFSET` identifies the input-only pin.

## Control flow
Probe allocates state, initializes a 4-line sleeping gpiochip with parent MFD device and callbacks, obtains the parent regmap, and registers. Set/config are no-ops or unsupported for the HALL input; other pins update output and drive bits.

## State and persistence behavior
Pin output and drive state live in PMIC GPIO control registers. HALL input state is read from `BD71828_REG_IO_STAT`. Direction is inferred from fixed pin semantics and board-reserved ranges, not dynamic hardware state.

## Dependencies and integration points
The driver depends on the BD71828 MFD regmap, platform device binding `bd71828-gpio`, gpiolib, and pinconf drive config. Board firmware is expected to use `gpio-reserved-ranges` for pins not configured by OTP as GPIO outputs.

## Risks and edge cases
OTP pin usage cannot be verified at runtime, so incorrect device-tree exposure can let software drive pins with non-GPIO board functions. `get()` returns the masked register field rather than normalized boolean for non-HALL pins, so callers get nonzero truth but not necessarily `1`.

## Test signals
Test HALL input reads and output rejection, output pins set/get, drive mode pinconf, regmap absence failure, and board reserved-range behavior in gpiolib.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd71828.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd72720.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd72720.c

## Purpose
This platform driver exposes GPIO-capable pins on ROHM BD72720 and BD73900 PMICs. Because many pin functions are OTP-selected and unreadable at runtime, device-tree properties declare which pins are valid GPIO inputs or outputs.

## Important APIs, types, and functions
`struct bd72720_gpio` stores the gpiochip, device, regmap, and `gpio_is_input` bitmap. GPIO operations are `bd72720gpio_get()`, `bd72720gpo_set()`, `bd72720_gpio_set_config()`, and `bd72720gpo_direction_get()`. `bd72720_valid_mask()` parses `rohm,pin-dvs0`, `rohm,pin-dvs1`, `rohm,pin-exten0`, `rohm,pin-exten1`, and `rohm,pin-fault_b`.

## Control flow
Probe copies the 6-line chip template, gets the parent regmap, and registers. During valid-mask initialization, EPDEN is always exposed, optional properties add DVS/EXTEN/FAULT_B pins as GPI or GPO where supported, and GPI pins are recorded in `gpio_is_input`. Get reads either interrupt source bits for inputs or per-pin control registers for outputs.

## State and persistence behavior
Output value and drive state live in per-pin PMIC control registers. Input state is read from `BD72720_REG_INT_ETC1_SRC`. The driver's `gpio_is_input` bitmap and valid mask are runtime interpretations of firmware-declared OTP configuration.

## Dependencies and integration points
The driver depends on the BD72720 MFD regmap, firmware node string properties, gpiolib, and pinconf drive configs. It is registered as `bd72720-gpio` with asynchronous preferred probing.

## Risks and edge cases
Device-tree must match OTP programming; the driver cannot verify it. Only DVS0/DVS1 support GPI mode; other properties set to `gpi` are warned and ignored. Setting or configuring input pins fails. The module description mentions BD73900 while IDs expose `bd72720-gpio`.

## Test signals
Test valid-mask parsing for missing, `gpi`, `gpo`, and invalid properties, input/output direction reporting, EPDEN availability, output set/get registers, input source reads, and drive open-drain/CMOS config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd72720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd9571mwv.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd9571mwv.c

## Purpose
This platform driver exposes the two GPIOs of ROHM BD9571MWV-M and BD9574MWF-M PMICs. Interrupt support is explicitly not implemented.

## Important APIs, types, and functions
`struct bd9571mwv_gpio` stores a parent regmap and gpiochip. Callbacks are `bd9571mwv_gpio_get_direction()`, `bd9571mwv_gpio_direction_input()`, `bd9571mwv_gpio_direction_output()`, `bd9571mwv_gpio_get()`, and `bd9571mwv_gpio_set()`. Probe copies a 2-line chip template and registers it.

## Control flow
Probe allocates state, gets the parent MFD regmap, sets the chip parent to the MFD device, and registers the gpiochip. Direction output writes the initial output value first, then sets the direction bit. Direction input clears the direction bit.

## State and persistence behavior
Direction, input, and output state are stored in PMIC registers `BD9571MWV_GPIO_DIR`, `BD9571MWV_GPIO_IN`, and `BD9571MWV_GPIO_OUT`. The driver holds no cache and uses regmap for all operations.

## Dependencies and integration points
It depends on ROHM generic MFD platform IDs, BD9571 register definitions, regmap, and gpiolib. Platform IDs cover both BD9571 and BD9574 variants.

## Risks and edge cases
The direction bit convention must match hardware: the code reports set bits as input but sets the bit after configuring output, which should be verified against the PMIC datasheet. Return values from direction setters ignore `regmap_update_bits()` failures, so write errors may be hidden. No IRQ support exists.

## Test signals
Test both platform IDs, parent regmap presence, direction get/set semantics against hardware, input and output reads, output value writes, and behavior under injected regmap write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd9571mwv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-blzp1600.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-blzp1600.c

## Purpose
This platform driver supports the Blaize BLZP1600 memory-mapped GPIO controller. It uses `gpio-generic` for basic GPIO operations and adds debounce and optional interrupt-controller support.

## Important APIs, types, and functions
`struct blzp1600_gpio` stores the MMIO base, generic GPIO chip, and parent IRQ. Helpers wrap relaxed read/write and read-modify-write. IRQ callbacks are mask/unmask, ack, enable/disable, set type, and `blzp1600_gpio_irqhandler()`. Pinconf support is `blzp1600_gpio_set_config()` for `PIN_CONFIG_INPUT_DEBOUNCE`.

## Control flow
Probe maps the MMIO resource, initializes a generic GPIO chip using input, set, clear, and direction registers, attaches debounce config, and if `interrupt-controller` is present, gets the parent IRQ and fills `gpio_irq_chip`. IRQ enable forces the line to input and enables it; the chained handler reads raw interrupt status and dispatches each pending child IRQ.

## State and persistence behavior
GPIO direction/value, interrupt enable/mask/type/status, and debounce bits live in MMIO registers. The generic chip lock protects RMW operations. No cache or nonvolatile storage is maintained.

## Dependencies and integration points
The driver depends on OF compatible `blaize,blzp1600-gpio`, platform MMIO and IRQ resources, `gpio-generic`, gpiolib irqchip helpers, and chained IRQ handling.

## Risks and edge cases
The mask register semantics are inverted relative to some controllers: mask writes set bits and unmask clears them. Debounce config treats any nonzero debounce argument as enabling one bit and does not scale time. The IRQ handler reads raw status, while ack clears through `GPIO_IC_REG`; ordering should be verified under level interrupts.

## Test signals
Test generic GPIO set/clear/direction, interrupt-controller absent/present paths, all IRQ trigger types and handler selection, mask/unmask semantics, IRQ enable forcing input direction, debounce config, and pending status dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-blzp1600.c -->
