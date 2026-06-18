# subset-b-001301 research

This grouped report covers GPIO controller, GPIO expander, PMIC GPIO, and GPIO/IRQ bridge drivers under `sources/distributed-fs/ceph-client/drivers/gpio`. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-brcmstb.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-brcmstb.c

Purpose: implements the Broadcom BRCMSTB UPG GPIO controller with multiple 32-line register banks, optional GPIO interrupt-controller support, and wake-capable suspend/shutdown behavior.

Important APIs/types/functions: `struct brcmstb_gpio_priv` owns the parent platform device, MMIO base, bank list, IRQ domain/chip, parent IRQs, wake IRQ, and suspend flag. `struct brcmstb_gpio_bank` wraps `struct gpio_generic_chip`, bank id, width, wake mask, and saved registers. Important functions are `brcmstb_gpio_probe()`, `brcmstb_gpio_irq_setup()`, `brcmstb_gpio_irq_bank_handler()`, `brcmstb_gpio_irq_set_type()`, `brcmstb_gpio_irq_set_wake()`, `brcmstb_gpio_suspend_noirq()`, `brcmstb_gpio_resume()`, and `brcmstb_gpio_remove()`.

Control flow: probe maps the register resource, validates the number of banks against `brcm,gpio-bank-widths`, creates one generic gpiochip per non-empty bank, masks stale interrupts, and then builds a linear IRQ domain if the DT node is an interrupt controller. IRQs are demuxed from the chained parent by scanning each bank's `GIO_STAT & GIO_MASK`, then `generic_handle_domain_irq()` is called with the global GPIO offset. Suspend saves all bank registers except status, masks everything except wake-enabled lines, and resume restores the saved bank state.

State and persistence behavior: persistent runtime state is hardware register state plus `wake_active`, `saved_regs`, `num_gpios`, and `suspended`. Shutdown deliberately leaves wake GPIO masks programmed for cold-boot wake. The driver uses generic-chip locking for register read-modify-write paths and stores bank list membership for IRQ mapping and removal.

Dependencies and integration points: integrates with gpiolib generic MMIO helpers, device tree GPIO translation, Linux IRQ domains/chained IRQs, PM wakeup APIs, and platform PM callbacks. It depends on `brcm,gpio-bank-widths`, optional `interrupt-controller`, and optional `wakeup-source`.

Risks: the source tree currently contains duplicated declarations around `brcmstb_gpio_irq_set_wake()` and `brcmstb_gpio_bank_save()`, which is a compile-time risk if not resolved elsewhere. Empty banks consume offset space, so DT bank-width correctness is critical. Wake handling depends on parent IRQ and wake IRQ ordering, and invalid-width banks still expose 32 logical offsets while warning for offsets beyond actual width.

Test signals: build coverage should catch duplicated declarations and type errors. Runtime signals include successful probe for mixed-width banks, correct `gpiod_to_irq()` mapping, interrupt type programming for level/rising/falling/both-edge cases, wake event generation from retained status bits, suspend/resume register restore, and removal disposing all IRQ mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-brcmstb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bt8xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bt8xx.c

Purpose: exposes the 24 GPIO pins of Brooktree/Conexant BT848/849/878/879 PCI framegrabber chips as a generic GPIO controller.

Important APIs/types/functions: `struct bt8xxgpio` stores the spinlock, MMIO base, PCI device, gpiochip, and suspend snapshots of `BT848_GPIO_OUT_EN` and `BT848_GPIO_DATA`. Core GPIO operations are `bt8xxgpio_gpio_direction_input()`, `bt8xxgpio_gpio_direction_output()`, `bt8xxgpio_gpio_get()`, and `bt8xxgpio_gpio_set()`. Driver lifecycle is handled by `bt8xxgpio_probe()`, `bt8xxgpio_remove()`, `bt8xxgpio_suspend()`, and `bt8xxgpio_resume()`.

Control flow: PCI probe enables the device, requests BAR0, maps 0x1000 bytes, disables BT848 interrupts and GPIO DMA/input-register modes, sets all GPIOs input, then registers a 24-line gpiochip. GPIO reads and writes use `BT848_GPIO_DATA`; direction is controlled through `BT848_GPIO_OUT_EN`. Suspend snapshots output-enable/data registers and disables outputs; resume reinitializes interrupt/DMA state and restores only saved output data bits that are still output-enabled.

State and persistence behavior: no software cache is maintained during normal operation; hardware registers are read under `spinlock_irqsave`. Only suspend state persists in `saved_outen` and `saved_data`. `gpiobase` is a module parameter and may force a static GPIO base, otherwise dynamic allocation is used.

Dependencies and integration points: depends on PCI core, legacy BT848 register definitions from the media driver, gpiolib, and PM ops. There is no IRQ support in this GPIO driver; it explicitly disables the device interrupt mask.

Risks: the driver intentionally "abuses" media hardware, so sharing with a real bttv/media function would conflict over BAR registers. Static `gpiobase` can collide with other GPIO controllers. The GPIO input path clears the data bit before disabling output, which matches hardware assumptions but is unusual compared with pure direction registers.

Test signals: compile with BT8xx PCI IDs, probe on matching hardware, GPIO direction/value smoke tests through libgpiod, suspend/resume preserving output pins, and removal disabling outputs/interrupts without leaking the PCI enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-bt8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-by-pinctrl.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-by-pinctrl.c

Purpose: provides a GPIO controller backed entirely by pinctrl/pinconf operations, intended for platforms such as SCMI pinctrl where pin configuration is the GPIO transport.

Important APIs/types/functions: the driver builds a bare `struct gpio_chip` in `pin_control_gpio_probe()`. GPIO callbacks are `pin_control_gpio_get_direction()`, `pinctrl_gpio_direction_input`, `pin_control_gpio_direction_output()`, `pin_control_gpio_get()`, `pin_control_gpio_set()`, and generic request/free/config helpers.

Control flow: probe allocates a gpiochip, sets label/parent/base, hooks GPIO callbacks to pinctrl helper calls, reads `ngpios` from device properties, and registers with `devm_gpiochip_add_data()`. Reads query `PIN_CONFIG_LEVEL`; writes pack `PIN_CONFIG_LEVEL` with the requested value. Direction query reads `PIN_CONFIG_OUTPUT_ENABLE`; output direction delegates to pinctrl's direction-output operation.

State and persistence behavior: the driver holds no private state beyond the gpiochip. All line state persists in the pinctrl provider or underlying firmware. There is no IRQ, suspend, cache, or reset state.

Dependencies and integration points: depends on gpiolib, internal `gpiolib.h` generic helpers, platform bus, device properties, and pinctrl consumer APIs. It matches `scmi-pinctrl-gpio`.

Risks: correctness is entirely dependent on the pinctrl provider supporting `pinctrl_gpio_get_config()` and `pinctrl_gpio_set_config()` for level and output-enable semantics. There is no local validation of `ngpios` beyond property parsing. Latency and error propagation are whatever the pinctrl provider implements.

Test signals: probe must fail cleanly without `ngpios`. GPIO get/set/direction tests should be run against a pinctrl provider that can report `PIN_CONFIG_LEVEL` and `PIN_CONFIG_OUTPUT_ENABLE`, including negative-provider-error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-by-pinctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-cadence.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-cadence.c

Purpose: supports the Cadence GPIO IP block, including generic MMIO GPIO operations, optional interrupt demultiplexing, bypass-mode handling, and an AX3000 quirk that skips boot-time pinmux initialization.

Important APIs/types/functions: `struct cdns_gpio_chip` embeds `struct gpio_generic_chip`, MMIO base, saved bypass register, and quirk data. Key functions are `cdns_gpio_request()`, `cdns_gpio_free()`, `cdns_gpio_irq_mask()`, `cdns_gpio_irq_unmask()`, `cdns_gpio_irq_set_type()`, `cdns_gpio_irq_handler()`, `cdns_gpio_probe()`, and `cdns_gpio_remove()`.

Control flow: probe maps registers, reads optional `ngpios`, selects quirks by compatible, optionally forces all pins to input before generic-chip init, configures input/output data and direction registers, enables the peripheral clock, optionally attaches a parent IRQ to a gpio_irq_chip, registers the chip, snapshots bypass mode, and optionally enables output and clears bypass. Request clears bypass for a line; free restores that line's original bypass bit.

State and persistence behavior: `bypass_orig` is persistent software state used to restore bypass on free/remove. Generic-chip state tracks directions/values. IRQ type state lives in hardware `IRQ_VALUE`, `IRQ_TYPE`, and `IRQ_ANY_EDGE` registers. Probe reverts direction if initialization fails before registration.

Dependencies and integration points: integrates with gpiolib generic MMIO, clk framework, OF match data, platform IRQs, and hierarchical gpio_irq_chip setup. Compatible strings are `cdns,gpio-r1p02` and `axiado,ax3000-gpio`.

Risks: only up to 32 GPIOs are supported. The AX3000 quirk trusts firmware boot configuration and skips important register initialization. Both-edge IRQs use a dedicated any-edge bit; platforms without that behavior would misfire. Remove only restores bypass mode, not direction/output state.

Test signals: device-tree probe with and without IRQ, `ngpios` > 32 rejection, request/free bypass transitions, GPIO direction/value tests, IRQ type tests for all supported modes, and AX3000 boot-preserved configuration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-cadence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-cgbc.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-cgbc.c

Purpose: exposes 14 GPIO lines controlled through the Congatec Board Controller MFD command interface.

Important APIs/types/functions: `struct cgbc_gpio_data` contains the gpiochip, parent `struct cgbc_device_data`, and mutex. Important routines are `cgbc_gpio_cmd()`, `cgbc_gpio_get()`, `__cgbc_gpio_set()`, `cgbc_gpio_set()`, `cgbc_gpio_direction_set()`, `cgbc_gpio_direction_input()`, `cgbc_gpio_direction_output()`, `cgbc_gpio_get_direction()`, and `cgbc_gpio_probe()`.

Control flow: probe gets the MFD parent driver data, allocates state, initializes the mutex, fills gpiochip callbacks, and registers 14 sleeping GPIOs. Every operation sends a three-byte board-controller command and receives a one-byte result. Offsets 0-7 and 8-13 are addressed as separate command banks. Output direction first sets the desired output value, then changes direction.

State and persistence behavior: there is no value cache; state persists inside the board controller. The mutex serializes command sequences, especially read-modify-write set and direction operations. The driver marks no explicit suspend/resume state.

Dependencies and integration points: depends on the `linux/mfd/cgbc.h` command API, platform MFD child registration, gpiolib, and mutex cleanup through devm. It is a can-sleep controller because all operations cross the controller command transport.

Risks: command failure returns directly to GPIO callers. Read-modify-write behavior can race with other firmware/controller clients outside this driver. Direction bit semantics must remain aligned with board-controller firmware. There is no IRQ support.

Test signals: probe as `cgbc-gpio`, value get/set across both banks, direction transitions with set-before-output ordering, concurrent GPIO operations serialized by lock, and command-error propagation from mocked or real `cgbc_command()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-cgbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-clps711x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-clps711x.c

Purpose: implements Cirrus Logic CLPS711X/EP7209 GPIO banks using the generic MMIO GPIO helper.

Important APIs/types/functions: the file is centered on `clps711x_gpio_probe()`, with `struct gpio_generic_chip_config` and `struct gpio_generic_chip` carrying almost all behavior. The OF match table accepts `cirrus,ep7209-gpio`.

Control flow: probe requires an OF node and uses the `gpio` alias id to identify the bank. It maps two resources, one data and one direction register, initializes a one-byte generic GPIO chip, handles Port D's inverted direction semantics by using `dirin`, and sets Port E to three lines. It then assigns dynamic base/owner and registers the chip.

State and persistence behavior: no private runtime state exists after registration. Hardware data and direction registers are accessed through generic-chip callbacks. The only persistent configuration is bank id from OF alias and the generated gpiochip fields.

Dependencies and integration points: depends on OF aliases, platform resources, and `gpio_generic_chip_init()`. The driver assumes platform data/DT describes each port as a separate device with two MMIO resources.

Risks: invalid or missing alias ids reject probe, so DT alias numbering is part of the ABI. Direction polarity differs for Port D, making bank id correctness critical. No IRQ, pinctrl, or PM state is implemented.

Test signals: DT probe for aliases 0-4, Port D direction polarity, Port E exposing exactly three GPIOs, generic get/set/direction behavior, and failure for missing OF node or bad alias id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-clps711x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-creg-snps.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-creg-snps.c

Purpose: exposes selected Synopsys CREG control-register bitfields as output-only GPIOs, mainly chip-select control lines on ARC boards.

Important APIs/types/functions: `struct creg_layout` describes per-GPIO shift, on/off values, and bit width; `struct creg_gpio` stores the gpiochip, MMIO register, spinlock, and layout. Key functions are `creg_gpio_set()`, `creg_gpio_dir_out()`, `creg_gpio_validate_pg()`, `creg_gpio_validate()`, and `creg_gpio_probe()`.

Control flow: probe maps one register, selects a layout from OF match data, reads `ngpios`, validates that all bitfield definitions fit in a 32-bit register and have distinct on/off values, initializes the spinlock, and registers a dynamic-base gpiochip with only set and direction-output callbacks. `creg_gpio_set()` computes cumulative bit shifts for the target field, masks that field, writes either layout `on` or `off`, and updates the register under lock.

State and persistence behavior: the only software state is layout and spinlock; output state persists in the shared CREG register. There is no input, IRQ, or PM context. Because all GPIOs share one register, every set is a read-modify-write.

Dependencies and integration points: depends on OF match data for `snps,creg-gpio-axs10x` and `snps,creg-gpio-hsdk`, MMIO, platform bus, and gpiolib. It is built in via `builtin_platform_driver()`.

Risks: `creg_gpio_set()` uses `layout->bit_per_gpio[i]` after a loop where `i == offset`; this relies on offset being in range and is correct only if gpiolib enforces bounds. Shared-register RMW races with non-driver writers are not prevented. It cannot report input state or high-impedance.

Test signals: probe validation failures for impossible layouts, correct register field packing for HSDK and AXS10x layouts, output-only GPIO behavior, and concurrent set operations preserving neighboring fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-creg-snps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-cros-ec.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-cros-ec.c

Purpose: exposes ChromeOS EC GPIOs to Linux through EC commands, with named lines and read/set/get-direction support but no local direction control.

Important APIs/types/functions: callbacks are `cros_ec_gpio_set()`, `cros_ec_gpio_get()`, `cros_ec_gpio_get_direction()`, `cros_ec_gpio_init_names()`, `cros_ec_gpio_ngpios()`, and `cros_ec_gpio_probe()`. It uses EC command structs `ec_params_gpio_set`, `ec_params_gpio_get`, `ec_params_gpio_get_v1`, and `ec_response_gpio_get_v1`.

Control flow: probe adopts the EC transport device fwnode, queries GPIO count via `EC_GPIO_GET_COUNT`, allocates a gpiochip, queries every GPIO name through `EC_GPIO_GET_INFO`, prefixes names with `EC:`, then registers a can-sleep gpiochip. Get and set strip the prefix and issue name-based EC commands. Direction query uses indexed v1 EC GPIO info and interprets input/output flags.

State and persistence behavior: line names are cached in devm memory; values, direction, lock/unlock policy, and persistence live in EC firmware. There is no IRQ, PM state, or local shadow cache.

Dependencies and integration points: depends on ChromeOS EC core/platform data, EC command protocol, platform child device id `cros-ec-gpio`, gpiolib, and firmware-node propagation from the EC transport.

Risks: set operations are allowed only when system policy/EC firmware permits them; failures propagate from `cros_ec_cmd()`. Name buffers depend on EC-provided names fitting command structs. There is no direction setter, so consumers expecting ordinary bidirectional GPIOs may fail. EC latency makes `can_sleep` mandatory.

Test signals: EC command mocking for count/info/get/set, line-name prefix correctness, direction flag interpretation, locked-system set rejection, and probe behavior when EC count or a single info query fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-cros-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-crystalcove.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-crystalcove.c

Purpose: supports Intel Crystal Cove PMIC GPIOs, including 16 physical GPIOs, selected virtual ACPI GPIOs, nested interrupt handling, and debugfs GPIO state display.

Important APIs/types/functions: `struct crystalcove_gpio` stores the gpiochip, PMIC regmap, IRQ bus mutex, deferred IRQ update flags, trigger value, and mask flag. Key functions are `to_reg()`, `crystalcove_gpio_dir_in()`, `crystalcove_gpio_dir_out()`, `crystalcove_gpio_get()`, `crystalcove_gpio_set()`, `crystalcove_irq_type()`, `crystalcove_bus_sync_unlock()`, `crystalcove_gpio_irq_handler()`, `crystalcove_gpio_dbg_show()`, and `crystalcove_gpio_probe()`.

Control flow: probe gets the MFD parent regmap and IRQ, initializes a 95-line can-sleep gpiochip, configures a threaded gpio_irq_chip with no automatic parent handler, requests the PMIC IRQ, and registers the chip. GPIO operations translate a logical line to control/input registers; physical GPIOs map to per-port registers and virtual GPIO 0x5e maps to panel control. IRQ type/mask changes are staged under bus lock and committed in bus-sync-unlock, while the threaded parent reads/acks PMIC IRQ status and dispatches nested IRQs for physical GPIOs.

State and persistence behavior: PMIC registers hold GPIO and IRQ state. Software staging fields `update`, `intcnt_value`, and `set_irq_mask` persist only across genirq bus-lock windows. Virtual GPIOs outside supported mapping return success/zero for direction/set/get paths rather than hard errors.

Dependencies and integration points: depends on Intel SoC PMIC MFD, regmap, gpiolib, nested threaded IRQ handling, and `DOMAIN_BUS_WIRED` to distinguish its IRQ domain on a shared MFD fwnode.

Risks: `to_reg()` silently ignores unsupported virtual GPIO operations in several callbacks. IRQ state staging uses single fields, so it relies on genirq bus locking serializing one IRQ update at a time. Only edge triggers are supported for physical GPIO IRQs.

Test signals: physical GPIO get/set/direction, virtual panel GPIO access, threaded IRQ dispatch for both GPIO IRQ status registers, mask/type bus-lock batching, debug output fields, and shared-fwnode IRQ-domain token behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-crystalcove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-cs5535.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-cs5535.c

Purpose: supports AMD CS5535/CS5536 GPIOs, exposing a gpiochip plus exported helper functions for hardware-specific GPIO event and register manipulation.

Important APIs/types/functions: `struct cs5535_gpio_chip` stores gpiochip, I/O base, platform device, and spinlock. Exported symbols include `cs5535_gpio_set()`, `cs5535_gpio_clear()`, `cs5535_gpio_isset()`, `cs5535_gpio_set_irq()`, and `cs5535_gpio_setup_event()`. Gpiolib callbacks are `chip_gpio_request()`, `chip_gpio_get()`, `chip_gpio_set()`, `chip_direction_input()`, and `chip_direction_output()`.

Control flow: probe requests the I/O resource, initializes a 32-line gpiochip with named pins, masks out reserved pins and the power button from the module `mask`, and registers the chip. GPIO request validates availability and clears auxiliary functions. Set/clear operations write lower-bank or high-bank registers, with `errata_outl()` applying the CS5536 high-bank read-modify-write workaround. Direction-output enables both input and output and sets output value.

State and persistence behavior: hardware registers hold all GPIO state. The global module `mask` is modified at probe to remove unsafe pins. A spinlock serializes exported and gpiochip register access. There is no PM callback; the erratum helper specifically accounts for post-suspend high-bank behavior.

Dependencies and integration points: depends on platform I/O resources, `include/linux/cs5535.h` register definitions, x86 MSR access for IRQ routing, and external drivers that may call the exported CS5535 helper symbols.

Risks: global state and exported helpers imply only one effective controller instance. The mask parameter is security/safety critical because some pins are reserved or power-management-related. Direct I/O port and MSR access make this architecture/platform specific.

Test signals: detection of reserved pin rejection, GPIO value/direction operations on low and high banks, errata path after suspend scenarios, exported event/IRQ helper behavior, and module parameter mask adjustment logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-cs5535.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-da9052.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-da9052.c

Purpose: exposes the 16 GPIO pins of Dialog DA9052 PMICs through the DA9052 MFD register API and regmap IRQ framework.

Important APIs/types/functions: `struct da9052_gpio` stores the parent `struct da9052` and gpiochip. Callbacks are `da9052_gpio_get()`, `da9052_gpio_set()`, `da9052_gpio_direction_input()`, `da9052_gpio_direction_output()`, and `da9052_gpio_to_irq()`. `reference_gp` is the template gpiochip copied in probe.

Control flow: probe gets parent MFD state and optional platform data, copies `reference_gp`, applies a legacy base if supplied, and registers the gpiochip. Get first reads the GPIO configuration nibble to determine input or push-pull output; input reads `STATUS_C` or `STATUS_D`, while output reads the mode bit from the GPIO config register. Direction functions update the correct lower or upper nibble in paired GPIO config registers. IRQ mapping offsets from `DA9052_IRQ_GPI0`.

State and persistence behavior: PMIC registers hold direction, output level, debounce, and active polarity. The driver has no shadow cache or PM state. Operations sleep through the MFD/regmap transport and `can_sleep` is set.

Dependencies and integration points: depends on DA9052 MFD core, DA9052 register definitions/platform data, regmap IRQ data, platform children, and gpiolib.

Risks: `get()` only handles input and push-pull output; open-drain or unexpected modes return `-EINVAL`. Legacy `gpio_base` support can conflict with dynamic GPIO numbering. Direction input hardcodes active-low with debounce enabled.

Test signals: nibble updates for odd/even pins, input status reads across both status registers, push-pull output readback, IRQ mapping for all 16 lines, and platform-data base handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-da9052.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-da9055.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-da9055.c

Purpose: supports the three GPIO pins of Dialog DA9055 PMICs using MFD register access and regmap IRQ mapping.

Important APIs/types/functions: `struct da9055_gpio` contains the DA9055 parent and gpiochip. Important functions are `da9055_gpio_get()`, `da9055_gpio_set()`, `da9055_gpio_direction_input()`, `da9055_gpio_direction_output()`, `da9055_gpio_to_irq()`, and `da9055_gpio_probe()`. `reference_gp` is the gpiochip template.

Control flow: probe obtains parent `struct da9055`, optional platform data, copies the template, applies legacy base if present, and registers the chip. Direction bits are stored as two-bit fields in paired GPIO registers. Output direction programs VDD_IO/push-pull mode and then writes the requested level through `DA9055_REG_GPIO_MODE0_2`. Get reads GPIO direction, then reads either status or output-mode register before returning the target bit.

State and persistence behavior: all state persists in PMIC registers. The driver has no cache, locking, IRQ state, or suspend/resume implementation. It is a can-sleep controller.

Dependencies and integration points: depends on DA9055 MFD core, register definitions, platform data, regmap IRQ data, and platform driver registration through `subsys_initcall()`.

Risks: only three lines are exposed. Unexpected direction encoding falls through to returning a bit from the last read register, so invalid hardware state may not be clearly reported. Legacy fixed base can collide with other controllers.

Test signals: direction field programming for all three pins, output write/readback, input status reads, IRQ virq mapping from `DA9055_IRQ_GPI0`, and early registration ordering for MFD consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-da9055.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-davinci.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-davinci.c

Purpose: implements TI DaVinci/Keystone GPIO with MMIO GPIO operations, direct or banked IRQ modes, runtime clock acquisition, and system suspend/resume context preservation.

Important APIs/types/functions: `struct davinci_gpio_controller` stores the gpiochip, IRQ domain, lock, register-bank pointers, direct IRQ count, parent IRQs, register contexts, and `BINTEN` context. Key functions are `davinci_gpio_probe()`, `__davinci_direction()`, `davinci_gpio_irq_setup()`, `gpio_irq_handler()`, `gpio_irq_type_unbanked()`, `davinci_gpio_save_context()`, and `davinci_gpio_restore_context()`.

Control flow: probe reads `ti,ngpio` and `ti,davinci-gpio-unbanked`, maps registers, collects parent IRQs, initializes callbacks, and registers the gpiochip before IRQ setup. Banked mode allocates a legacy IRQ domain and chains each 16-GPIO bank parent to `gpio_irq_handler()`. Unbanked mode reuses existing parent IRQ chips and changes only trigger programming. GPIO set uses dedicated set/clear registers; direction uses the `dir` bitmap where set means input.

State and persistence behavior: register state is protected by a spinlock for direction reads/writes. Suspend saves direction, set-data, rising/falling trigger, and `BINTEN`; resume restores changed values. The global `gpio_base` points at the mapped controller base and is used for `BINTEN`.

Dependencies and integration points: depends on platform properties, clk framework, gpiolib, irqdomain/chained IRQs, OF match data selecting DaVinci versus Keystone irq-chip copying, and postcore initcall ordering for board code.

Risks: maximum register-bank assumptions are fixed by `MAX_REGS_BANKS` and `offset_array`. Unbanked mode mutates copied parent irq-chip structures, which is sensitive to irqchip internals. The context save clears only the last bank's `intstat` after the loop, which is a possible maintenance hazard.

Test signals: DT property validation, banked and unbanked IRQ paths, rising/falling-only trigger rejection, direct IRQ type programming, GPIO suspend/resume restoration, and early-boot GPIO availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-davinci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-dln2.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-dln2.c

Purpose: supports Diolan DLN-2 USB GPIO adapters using DLN-2 MFD command transfers and asynchronous event callbacks for GPIO IRQs.

Important APIs/types/functions: `struct dln2_gpio` stores the platform device, gpiochip, output-direction bitmap, unmasked/enabled IRQ bitmaps, IRQ type array, and IRQ mutex. Core functions are `dln2_gpio_request()`, `dln2_gpio_set_direction()`, `dln2_gpio_get()`, `dln2_gpio_set_config()`, `dln2_irq_set_type()`, `dln2_irq_bus_unlock()`, `dln2_gpio_event()`, `dln2_gpio_probe()`, and `dln2_gpio_remove()`.

Control flow: probe queries pin count, clamps to 32, initializes gpiochip callbacks and a child IRQ domain without parent handler, registers the gpiochip, then registers a DLN-2 event callback. GPIO request enables the hardware pin and caches its current direction; free disables it. IRQ mask/unmask only changes software bitmaps, while bus-sync-unlock sends event configuration commands to hardware when enabled state changes. Events validate message length/pin, filter synthetic rising/falling edge variants, and dispatch through the GPIO IRQ domain.

State and persistence behavior: direction is cached to avoid USB transfers when deciding whether `get()` should read input or output value. IRQ state is split into requested/unmasked and hardware-enabled bitmaps. Debounce is programmed globally through `DLN2_GPIO_SET_DEBOUNCE`, not per pin.

Dependencies and integration points: depends on DLN-2 MFD transfer APIs, gpiolib, irqdomain, platform child devices, and asynchronous USB-originated events.

Risks: USB/firmware transfer errors surface directly. The debounce API ignores the offset in the command payload. Cached direction can become stale if firmware or another client changes pin direction. IRQ event filtering relies on stored `irq_type` and event value semantics.

Test signals: pin-count query and clamp, request/free enable/disable commands, input/output get behavior based on cached direction, event configuration on mask/unmask, rising/falling event filtering, short/out-of-range event rejection, and callback unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-dln2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ds4520.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ds4520.c

Purpose: registers an Analog Devices DS4520 I2C I/O expander as a gpio-regmap-backed GPIO controller.

Important APIs/types/functions: the file uses `ds4520_gpio_probe()`, `ds4520_regmap_config`, and `struct gpio_regmap_config`. Register offsets are `DS4520_PULLUP0`, `DS4520_IO_CONTROL0`, and `DS4520_IO_STATUS0`.

Control flow: probe reads the device `reg` property as a base offset, initializes an 8-bit I2C regmap, points gpio-regmap data, set, and output-direction bases at the DS4520 register windows, and registers the GPIO controller through `devm_gpio_regmap_register()`.

State and persistence behavior: state is entirely in DS4520 registers and regmap internals. There is no private cache, IRQ support, PM callback, or manual locking.

Dependencies and integration points: depends on I2C core, device properties, regmap, gpio-regmap, OF match `adi,ds4520-gpio`, and I2C id `ds4520-gpio`.

Risks: correct operation depends on the `reg` property because all register bases are computed from it. The driver relies on gpio-regmap default width/stride assumptions; any DS4520 variant with different line count or register layout would need explicit config. There is no device-id verification.

Test signals: probe with and without `reg`, I2C regmap initialization failures, GPIO input status reads, output/pullup writes, direction writes, and gpio-regmap registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ds4520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-dwapb.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-dwapb.c

Purpose: implements Synopsys DesignWare APB GPIO for OF and ACPI systems, supporting multiple ports, optional shared or chained IRQ handling, debounce on port A, resets/clocks, register-layout variants, and suspend/resume context.

Important APIs/types/functions: `struct dwapb_gpio` owns the device, MMIO base, flags, reset, clocks, and flexible array of `struct dwapb_gpio_port`. `struct dwapb_context` stores suspend state. Important functions include `dwapb_gpio_get_pdata()`, `dwapb_gpio_add_port()`, `dwapb_configure_irqs()`, `dwapb_irq_set_type()`, `dwapb_do_irq()`, `dwapb_gpio_probe()`, `dwapb_gpio_suspend()`, and `dwapb_gpio_resume()`.

Control flow: probe parses child nodes into per-port properties, deasserts reset, maps registers, enables optional clocks, chooses v1/v2 register offsets, and registers each port through `gpio_generic_chip_init()`. Port A can configure IRQs; ACPI uses a shared requested IRQ while OF uses gpio_irq_chip parent handlers. The IRQ worker reads status, handles mapped GPIO IRQs, and toggles polarity for both-edge emulation. Suspend saves per-port data/direction/external and port-A IRQ/debounce state, masks non-wake IRQs, and disables clocks; resume reenables clocks and restores state.

State and persistence behavior: per-port contexts persist across system sleep. `ctx->wake_en` is updated by `irq_set_wake` and used during suspend masking. Generic-chip registers hold live GPIO state. Reset and clocks are devm-managed with cleanup actions.

Dependencies and integration points: depends on OF/ACPI firmware properties, gpiolib generic MMIO, reset framework, clk bulk APIs, IRQ core, and ACPI shared interrupt conventions. Compatible and ACPI IDs select register offset layout.

Risks: only port A supports interrupts/debounce. Both-edge handling toggles polarity based on current GPIO value and can miss rapid transitions. Child-node property correctness is critical. Shared ACPI IRQ handling must coexist with other devices on the line.

Test signals: multi-port DT parsing, v1/v2 register conversion, chained and shared IRQ modes, all supported trigger types, wake masking through suspend, debounce config on port A only, reset/clock error paths, and resume state restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-dwapb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-eic-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-eic-sprd.c

Purpose: supports Spreadtrum digital-chip External Interrupt Controller GPIO-like inputs across debounce, latch, async, and sync EIC submodules.

Important APIs/types/functions: `enum sprd_eic_type`, `struct sprd_eic`, and `struct sprd_eic_variant_data` describe each controller. Important functions are `sprd_eic_update()`, `sprd_eic_get()`, `sprd_eic_set_debounce()`, `sprd_eic_irq_mask()`, `sprd_eic_irq_unmask()`, `sprd_eic_irq_set_type()`, `sprd_eic_toggle_trigger()`, `sprd_eic_handle_one_type()`, `sprd_eic_irq_handler()`, and `sprd_eic_probe()`.

Control flow: probe selects the EIC type by compatible, maps up to three banks, configures GPIO operations appropriate to the type, attaches a gpio_irq_chip to one parent IRQ, registers the gpiochip, and registers an atomic notifier. Because all EIC submodules share one interrupt line, the parent chained handler calls a notifier chain so each instance scans its masked interrupt status. Debounce/latch modules emulate edge triggers by programming the opposite level after observing stable state; async/sync modules program native edge/level registers.

State and persistence behavior: the driver stores bank MMIO bases, type, IRQ, and spinlock. Hardware registers hold debounce, masks, polarity, and pending status. No suspend/resume context is present. Debounce request/free toggles debounce mask only for debounce EIC instances.

Dependencies and integration points: depends on OF compatibles for SC9860 EIC types, gpiolib IRQ helpers, chained IRQs, atomic notifier chains, and MMIO resources per bank.

Risks: notifier-chain dispatch means every EIC instance scans on every shared interrupt. Debounce/latch edge emulation can race with signal changes and loops until state is stable. Latch EIC exposes no `get()` callback. Debounce values are truncated to 12-bit millisecond units.

Test signals: probe for all four compatibles, bank-count-derived `ngpio`, trigger programming for level/edge/both on each type, shared-parent notifier dispatch, debounce config, and edge emulation when input changes during reprogramming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-eic-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-elkhartlake.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-elkhartlake.c

Purpose: provides an auxiliary-bus wrapper that instantiates Intel Elkhart Lake PSE GPIO using the shared Tangier GPIO implementation.

Important APIs/types/functions: `ehl_gpio_probe()` consumes `struct ehl_pse_io_data`, allocates `struct tng_gpio`, fills register base, IRQ, GPIO info, and wake-register offsets, then calls `devm_tng_gpio_probe()`. It imports the `GPIO_TANGIER` namespace and reuses `tng_gpio_pm_ops`.

Control flow: auxiliary probe validates platform data, maps the memory resource carried by the auxiliary device, sets fixed `ngpio` to 30, assigns EHL-specific wake registers (`GWMR_EHL`, `GWSR_EHL`, `GSIR_EHL`), calls the common Tangier probe helper, and stores driver data on the auxiliary device.

State and persistence behavior: this file owns no independent GPIO state after handoff; Tangier common code owns GPIO, IRQ, and PM state. The wrapper persists only the initialized `struct tng_gpio` allocated with devm.

Dependencies and integration points: depends on the Intel PSE auxiliary device model, `linux/ehl_pse_io_aux.h`, `gpio-tangier.h`, and Tangier helper APIs. The auxiliary id is `EHL_PSE_IO_NAME "." EHL_PSE_GPIO_NAME`.

Risks: all behavior depends on platform data being populated by the parent PSE driver. Fixed line count and wake-register constants must match the hardware block. Errors in Tangier common code surface through this wrapper.

Test signals: auxiliary device binding, missing platform-data failure, MMIO mapping failure, Tangier probe success, 30-line gpiochip exposure, wake register behavior through shared PM ops, and namespace import/build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-elkhartlake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-em.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-em.c

Purpose: implements Renesas Emma Mobile GIO GPIO and interrupt support, including two MMIO windows, pinctrl integration, and an IRQ domain.

Important APIs/types/functions: `struct em_gio_priv` stores two bases, sense lock, platform device, gpiochip, irqchip, and IRQ domain. Key functions are `em_gio_irq_set_type()`, `em_gio_irq_handler()`, `em_gio_direction_input()`, `em_gio_direction_output()`, `em_gio_set()`, `em_gio_to_irq()`, `em_gio_free()`, `em_gio_irq_domain_map()`, and `em_gio_probe()`.

Control flow: probe obtains two parent IRQs and two MMIO resources, reads `ngpios`, sets GPIO callbacks and pinctrl request/free, builds an IRQ domain, requests low and high parent IRQs with the same handler, and registers the gpiochip. IRQ type programming disables a line in `GIO_IIA`, updates its 4-bit sense field in one of four `GIO_IDT` registers, clears pending state, and reenables it. Parent IRQ handling drains `GIO_MST`, clears each bit in `GIO_IIR`, and dispatches through the domain.

State and persistence behavior: no suspend context is saved. Sense programming is serialized by `sense_lock`. `em_gio_free()` returns the line to input after freeing pinctrl, avoiding stale output drive on later requests. Output values are written through low/high masked registers.

Dependencies and integration points: depends on OF property `ngpios`, pinctrl GPIO helpers, platform IRQs/resources, gpiolib, irqdomain, and postcore initcall ordering.

Risks: no PM restore means sleep states that reset GIO hardware would lose configuration. The IRQ domain handler uses level handling by default while type-specific sense is programmed separately. Both parent IRQs use the same status register and handler, so hardware status semantics must be correct.

Test signals: two-resource/two-IRQ probe, pinctrl request/free, input-on-free behavior, all supported trigger types, low/high output register writes, domain mapping, and draining multiple pending IRQ bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-em.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-en7523.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-en7523.c

Purpose: implements the Airoha EN7523 GPIO controller using generic GPIO data access plus custom direction/output-enable registers.

Important APIs/types/functions: `struct airoha_gpio_ctrl` stores a generic chip, data register, two direction registers, and output-enable register. Key functions are `airoha_dir_set()`, `airoha_dir_out()`, `airoha_dir_in()`, `airoha_get_dir()`, and `airoha_gpio_probe()`.

Control flow: probe maps four resources, initializes a 32-line generic GPIO chip using the data register, then overrides direction callbacks. Direction uses one bit per pin in an output-enable register and one direction bit every two bits in two 16-pin direction registers. Output direction writes the direction register, writes the requested output value through generic-chip set, then updates output enable.

State and persistence behavior: hardware registers hold all state. There is no lock around direction/output register read-modify-write, no IRQ support, and no PM context. Generic-chip handles basic data reads/writes.

Dependencies and integration points: depends on platform MMIO resources, OF compatible `airoha,en7523-gpio`, gpiolib generic helpers, and device-managed registration.

Risks: direction read-modify-write is unlocked and could race with concurrent GPIO operations. Resource order is part of the ABI. The two-bit direction spacing is hardware-specific and easy to misconfigure if offsets change.

Test signals: probe resource ordering, 32-line exposure, direction transitions across lower and upper 16-pin banks, output-enable bit updates, generic value get/set, and concurrent direction stress testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-en7523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ep93xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ep93xx.c

Purpose: supports Cirrus EP93xx GPIO blocks with generic MMIO data/direction handling and optional per-port interrupt support.

Important APIs/types/functions: `struct ep93xx_gpio_chip` wraps MMIO base, generic chip, and optional `struct ep93xx_gpio_irq_chip`. Important functions include `ep93xx_gpio_update_int_params()`, `ep93xx_gpio_irq_type()`, `ep93xx_gpio_irq_ack()`, `ep93xx_gpio_set_config()`, `ep93xx_setup_irqs()`, and `ep93xx_gpio_probe()`.

Control flow: probe maps named `data` and `dir` resources, initializes a byte-wide generic gpiochip, and if IRQ resources exist, maps the named `intr` resource and configures a gpio_irq_chip. A/B ports request one shared parent IRQ and scan an 8-bit status register. F-port style configurations use multiple parent IRQs and a chained handler that maps parent index to GPIO offset. IRQ type sets type/polarity shadow fields, forces the line input, selects edge or level handler, and updates hardware by disabling then rewriting registers.

State and persistence behavior: interrupt configuration is shadowed in `int_unmasked`, `int_enabled`, `int_type1`, `int_type2`, and `int_debounce`. GPIO state is in generic MMIO registers. There is no PM context. Debounce state is one byte per IRQ chip and is updated immediately.

Dependencies and integration points: depends on named platform resources, gpiolib generic helpers, gpio_irq_chip, OF compatible `cirrus,ep9301-gpio`, and postcore initcall registration.

Risks: both-edge IRQs are emulated by toggling polarity on ack and can miss rapid transitions. F-port parent mapping assumes parent IRQ order equals line order. IRQ setup logs but does not abort registration if `ep93xx_setup_irqs()` returns an error before final gpiochip add.

Test signals: data/dir-only probe, A/B shared IRQ dispatch, F-port multi-parent dispatch, all trigger types including both-edge toggling, debounce config, and generic byte-wide GPIO value/direction behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ep93xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-exar.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-exar.c

Purpose: exposes Exar XR17V35x UART MPIO pins as GPIOs through a platform child of a PCI UART driver.

Important APIs/types/functions: `struct exar_gpio_chip` stores gpiochip, MMIO regmap, IDA index/name, first pin, and optional cascaded-device register offset. Important functions are `exar_offset_to_sel_addr()`, `exar_offset_to_lvl_addr()`, `exar_get_direction()`, `exar_get_value()`, `exar_set_value()`, `exar_direction_output()`, `exar_direction_input()`, and `gpio_exar_probe()`.

Control flow: probe gets the parent PCI device's already-mapped BAR0, reads `exar,first-pin` and `ngpios`, doubles `ngpios` and computes a cascaded register offset for cascaded device IDs, creates an MMIO regmap, allocates a unique gpiochip label using IDA, fills callbacks, and registers the chip. Direction is controlled by MPIOSEL bits; level is read/written through MPIOLVL registers. Output direction writes the requested level before clearing the select bit to output.

State and persistence behavior: hardware registers hold direction and value. The IDA index is freed by a devm action. There is no IRQ support, PM context, or software value cache.

Dependencies and integration points: depends on the Exar UART parent having mapped BAR0 with `pcim_iomap_table()`, platform device properties, regmap MMIO, PCI core, gpiolib, and IDA allocation.

Risks: parent driver ordering is required; without mapped BAR0 probe fails. Cascaded detection interprets PCI device-id bitfields, so new variants may need updates. The driver assumes regmap MMIO operations cannot fail after initialization.

Test signals: platform child probe under Exar PCI UART, first-pin and ngpios property validation, cascaded ID behavior, direction/value operations across low/high and cascaded registers, IDA label allocation/free, and regmap initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-exar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-f7188x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-f7188x.c

Purpose: supports GPIO banks in several Fintek and Nuvoton Super-I/O chips by probing legacy Super-I/O configuration ports and registering one gpiochip per bank.

Important APIs/types/functions: `struct f7188x_sio` stores Super-I/O address, logical device, and chip type. `struct f7188x_gpio_bank` and `struct f7188x_gpio_data` describe bank layout. Key functions are `superio_enter()`, `f7188x_gpio_get_direction()`, `f7188x_gpio_direction_in()`, `f7188x_gpio_direction_out()`, `f7188x_gpio_get()`, `f7188x_gpio_set()`, `f7188x_gpio_set_config()`, `f7188x_find()`, and `f7188x_gpio_init()`.

Control flow: init probes Super-I/O ports 0x2e and 0x4e, unlocks with the double key, reads device/manufacturer IDs, chooses chip type and bank table, registers the platform driver, and creates a platform device with copied SIO data. Probe selects the static bank array for the chip and registers each bank as a separate can-sleep gpiochip. Each GPIO operation re-enters Super-I/O config mode, selects the GPIO logical device, reads/modifies/writes bank registers, then exits.

State and persistence behavior: static bank tables describe immutable layout. Hardware registers hold direction, data, and output mode. No mutex protects repeated Super-I/O access beyond `request_muxed_region()` inside `superio_enter()`. The platform device pointer is global for module exit.

Dependencies and integration points: depends on legacy I/O port access, Super-I/O IDs, platform device self-registration, gpiolib, and pinconf drive open-drain/push-pull config support.

Risks: static bank arrays are shared objects mutated with parent/data pointers at probe, making multi-instance assumptions weak. Super-I/O config access is slow and can conflict with firmware or other drivers if muxing is inadequate. Device list in module description lags supported Nuvoton/F81865 variants.

Test signals: chip detection at both standard ports, manufacturer validation, bank count/ngpio for each supported ID, direction inversion for NCT6126D, single data-register behavior for NCT6126D, drive mode config, and platform device cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-f7188x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ftgpio010.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ftgpio010.c

Purpose: implements Faraday FTGPIO010-compatible controllers, including generic GPIO operations, interrupt demultiplexing, and optional debounce programming based on clock rate.

Important APIs/types/functions: `struct ftgpio_gpio` stores device, generic chip, MMIO base, and optional clock. Key functions are `ftgpio_gpio_ack_irq()`, `ftgpio_gpio_mask_irq()`, `ftgpio_gpio_unmask_irq()`, `ftgpio_gpio_set_irq_type()`, `ftgpio_gpio_irq_handler()`, `ftgpio_gpio_set_config()`, and `ftgpio_gpio_probe()`.

Control flow: probe maps MMIO, gets parent IRQ, optionally enables the clock, initializes a generic GPIO chip using input, set, clear, and direction-output registers, adds debounce config only if a clock is available, configures gpio_irq_chip with a chained parent handler, disables/unmasks/clears all interrupts, clears debounce enable, and registers the chip. IRQ type programs type, level/polarity, both-edge registers, selects edge/level handler, and acks pending state.

State and persistence behavior: no software state beyond MMIO base and clock pointer. Debounce has one shared prescaler register; the first nonmatching debounce user wins, while later users need the same divisor or receive `-ENOTSUPP`. No PM context is saved.

Dependencies and integration points: depends on OF compatibles for Cortina Gemini, Moxa Moxart, and Faraday FTGPIO010, gpiolib generic MMIO, clk framework, and IRQ core.

Risks: debounce calculation uses the requested microsecond argument as a divisor target and returns unsupported for divisors beyond 24 bits or conflicting existing users. IRQ status uses raw status and relies on individual ack callbacks. No locking protects interrupt register RMW paths.

Test signals: GPIO direction/value operations, interrupt type programming for all supported modes, parent IRQ demux, debounce same/divergent intervals, operation with missing non-deferred clock, and reset of interrupt/debounce registers at probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ftgpio010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-fxl6408.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-fxl6408.c

Purpose: supports Fairchild/ON FXL6408 8-bit I2C GPIO expanders using regmap and gpio-regmap.

Important APIs/types/functions: `fxl6408_identify()` verifies the manufacturer bits in `FXL6408_REG_DEVICE_ID`; `fxl6408_probe()` creates the I2C regmap, disables output high-Z, and registers gpio-regmap; `fxl6408_resume()` dirties and syncs regcache. Register access tables constrain readable, writable, and volatile registers.

Control flow: probe initializes an 8-bit regmap with MAPLE cache and access tables, reads device ID, stores regmap as client data, writes zero to `OUTPUT_HIGH_Z` so output values drive pins, then registers an 8-line gpio-regmap with input status, output, and output-direction bases. Resume marks regcache dirty and syncs it to hardware.

State and persistence behavior: regmap cache stores nonvolatile output/direction/high-Z state; input status and device ID are volatile. No private state exists outside the regmap pointer. Resume restores cached state after power loss or suspend.

Dependencies and integration points: depends on I2C, regmap, gpio-regmap, OF compatible `fcs,fxl6408`, and I2C id `fxl6408`.

Risks: interrupt status register is defined but not exposed for IRQ support. Output high-Z is globally disabled at probe; boards relying on high-Z defaults need explicit GPIO direction management. Device ID only checks manufacturer bits, not a full part revision.

Test signals: invalid ID rejection, access-table enforcement, output high-Z write, 8-line gpio-regmap operations, regcache sync on resume, and I2C error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-fxl6408.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ge.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ge.c

Purpose: supports GE FPGA-based GPIO blocks on several GE boards with a simple big-endian generic MMIO gpiochip.

Important APIs/types/functions: `gef_gpio_probe()` is the only substantive function. It uses `struct gpio_generic_chip_config`, `struct gpio_generic_chip`, and OF match data to set the number of GPIO lines for `gef,sbc610-gpio`, `gef,sbc310-gpio`, and `ge,imp3a-gpio`.

Control flow: probe allocates a generic chip, maps one MMIO resource, initializes generic GPIO with input data, output set, and direction-input registers using big-endian byte order, labels the chip from the fwnode, sets dynamic base, applies match-data `ngpio`, and registers the chip. Registration uses `module_platform_driver_probe()` for one-shot probe behavior.

State and persistence behavior: the driver has no private state after registration; GPIO state persists in FPGA registers. There is no IRQ configuration in this driver even though the hardware has trigger/polarity/status registers.

Dependencies and integration points: depends on OF match data, platform MMIO resources, gpiolib generic helpers, and big-endian register access.

Risks: interrupt support is explicitly left as TODO; hardware interrupts may be generated but masking is delegated to external interrupt controllers. Output mode configuration is also unsupported. Register semantics depend on the generic helper matching GE FPGA layout.

Test signals: compatible-specific line counts, big-endian generic register access, input/output/direction operation, probe failure on missing resource, and absence of IRQ chip registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-gpio-mm.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-gpio-mm.c

Purpose: supports Diamond Systems GPIO-MM ISA boards by adapting two Intel 8255 PPIs through the shared `gpio-i8255` regmap helper.

Important APIs/types/functions: `gpiomm_probe()` requests the I/O port region, maps it, creates an I/O-port regmap, fills `struct i8255_regmap_config`, and calls `devm_i8255_regmap_register()`. Module parameter `base[]` supplies board I/O base addresses.

Control flow: the ISA driver is instantiated for each configured base address. Probe reserves eight I/O ports, maps them, creates an 8-bit flat-cache regmap with volatile ranges for both PPIs, sets parent, PPI count, and line names, then delegates GPIO registration to the i8255 helper.

State and persistence behavior: GPIO direction/value state is managed by the shared i8255 regmap layer and hardware. The local file maintains only module parameter arrays. Regcache is flat with volatile tables for PPI register windows.

Dependencies and integration points: depends on ISA driver infrastructure, I/O port access, regmap, and the `I8255` namespace/helper from `gpio-i8255.h`. It exposes 48 named GPIO lines across two PPIs.

Risks: no automatic hardware discovery exists; users must provide correct `base` parameters. I/O port conflicts reject probe. There is no IRQ or PM support. Incorrect base values can target unrelated legacy hardware.

Test signals: module parameter parsing for one or more base addresses, region conflict handling, 48 GPIO names, i8255 direction/value behavior across both PPIs, and namespace/build linkage to the i8255 helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-gpio-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-graniterapids.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-graniterapids.c

Purpose: supports Intel Granite Rapids-D virtual GPIO, exposing 128 pad-configuration-backed GPIOs and a shared interrupt handler.

Important APIs/types/functions: `struct gnr_gpio` stores gpiochip, register bases, read-only bitmap, raw spinlock, and PM pad backup. Important functions are `gnr_gpio_configure_line()`, `gnr_gpio_request()`, `gnr_gpio_get()`, `gnr_gpio_direction_input()`, `gnr_gpio_direction_output()`, `gnr_gpio_irq_set_type()`, `gnr_gpio_irq()`, `gnr_gpio_probe()`, `gnr_gpio_suspend()`, and `gnr_gpio_resume()`.

Control flow: probe maps the register resource, reads `GNR_CFG_PADBAR` to locate pad configuration registers, requests a shared non-threaded IRQ, loads read-only pin bits from lock registers, initializes a 128-line gpiochip, attaches a non-parent gpio_irq_chip, and registers. Requests require host software ownership. Set/direction/type changes modify pad config bits under raw spinlock, rejecting read-only pins. IRQ handling scans four status/enable register pairs and dispatches enabled pending bits to the GPIO IRQ domain.

State and persistence behavior: read-only pins are represented by `ro_bitmap`; writable pad config words are saved on suspend and restored on resume. Hardware pad config holds value, direction, ownership, RX mode, and IRQ select. Raw spinlock protects pad and IRQ register RMW operations.

Dependencies and integration points: depends on ACPI ID `INTC1109`, platform IRQ/resources, gpiolib, shared IRQ core, bitmap helpers, and PM sleep ops.

Risks: only rising-edge and high-level IRQ types are supported; falling/low requests fail. IRQs require nonzero `INTSEL`. Read-only lock bits prevent writes but still allow reads. Shared IRQ handling must return accurate handled status to avoid interrupt storms.

Test signals: ACPI binding, host-ownership request rejection, read-only pin write rejection, direction/value programming, rising/high IRQ handling, status ack and enable masking, shared IRQ return behavior, and suspend/resume pad restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-graniterapids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-grgpio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-grgpio.c

Purpose: supports Aeroflex/Gaisler GRGPIO cores with generic MMIO GPIO operations and optional per-line IRQ mapping to one of several underlying IRQ inputs.

Important APIs/types/functions: `struct grgpio_priv` stores generic chip, registers, device, interrupt-mask shadow, IRQ domain, underlying IRQ records, and line IRQ records. Important functions are `grgpio_to_irq()`, `grgpio_irq_set_type()`, `grgpio_irq_mask()`, `grgpio_irq_unmask()`, `grgpio_irq_handler()`, `grgpio_irq_map()`, `grgpio_irq_unmap()`, and `grgpio_probe()`.

Control flow: probe maps registers, initializes a big-endian generic GPIO chip, reads current interrupt mask, sets line count from `nbits`, and optionally parses an `irqmap` property. If `irqmap` exists, it creates a linear IRQ domain and records each line's underlying IRQ index. `gpiod_to_irq()` creates mappings only for lines with valid indices. Mapping lazily requests the underlying IRQ and increments its refcount; unmapping masks the line and frees the underlying IRQ when the last mapped line using it disappears.

State and persistence behavior: `imask` shadows the hardware mask register and is updated under generic-chip lock. `uirqs[].refcnt` tracks shared underlying IRQ requests. GPIO values/directions persist in hardware. There is no PM context.

Dependencies and integration points: depends on OF GRLIB-compatible names, `nbits`/`irqmap` properties, platform IRQ resources, gpiolib generic helpers, irqdomain, and big-endian MMIO access.

Risks: the `irqmap` size check compares bytes to `ngpio`, so malformed properties may be undervalidated or overaccepted depending on endianness/encoding. IRQ handling scans every GPIO line for each underlying IRQ. Both-edge IRQs are unsupported.

Test signals: GPIO operation with and without IRQ map, line count fallback, invalid `irqmap` handling, lazy underlying IRQ request/free refcounts, mask shadow correctness, trigger type programming, and big-endian register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-grgpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-gw-pld.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-gw-pld.c

Purpose: supports Gateworks I2C PLD GPIO expanders with a simple open-drain 8-bit register model.

Important APIs/types/functions: `struct gw_pld` stores gpiochip, I2C client, and `out` shadow byte. GPIO callbacks are `gw_pld_input8()`, `gw_pld_get8()`, `gw_pld_output8()`, `gw_pld_set8()`, and `gw_pld_probe()`.

Control flow: probe allocates state, initializes an 8-line can-sleep gpiochip, sets the I2C client, enables `I2C_M_IGNORE_NAK` because the PLD does not reliably acknowledge, initializes `out` to `0xff`, stores client data, and registers the gpiochip. Direction input sets the corresponding output-shadow bit to one and writes the byte; output updates the shadow bit according to requested value and writes it. Get reads one byte and returns the target bit.

State and persistence behavior: `out` is the only software state and shadows the last written open-drain output byte. Hardware state persists in the PLD register. There is no IRQ, PM, locking, or regmap cache.

Dependencies and integration points: depends on I2C SMBus byte operations, gpiolib, I2C id `gw-pld`, and OF compatible `gateworks,pld-gpio`.

Risks: reads returning an I2C error are converted to GPIO value 0 instead of propagating the error. No lock protects `out`, so concurrent set/direction calls can lose updates. Ignoring NAK is necessary for hardware but can hide bus problems.

Test signals: probe with OF/I2C IDs, open-drain input-as-one behavior, output shadow writes, readback through SMBus byte, I2C error handling behavior, and concurrent GPIO set stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-gw-pld.c -->
