# subset-b-001306 research

This grouped report covers the assigned GPIO controller, GPIO expander, PMIC GPO, and platform-specific GPIO support files under `sources/distributed-fs/ceph-client/drivers/gpio`. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-stp-xway.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-stp-xway.c

Purpose: implements the Lantiq XWAY Serial To Parallel controller as a GPIO output provider for external shift-register cascades, with up to three 8-bit groups and optional hardware ownership of selected DSL/PHY bits.

Important APIs, types, and functions: `struct xway_stp` stores the `gpio_chip`, MMIO base, shadow output value, enabled groups, edge mode, and hardware-reserved bit masks. GPIO callbacks are `xway_stp_get()`, `xway_stp_set()`, `xway_stp_dir_out()`, and `xway_stp_request()`. `xway_stp_hw_init()` programs STP registers and `xway_stp_probe()` parses Device Tree properties such as `lantiq,shadow`, `lantiq,groups`, `lantiq,dsl`, `lantiq,phy*`, and `lantiq,rising`.

Control flow: probe maps the register block, configures an output-only dynamic-base chip, reads board properties, enables the clock, initializes the STP hardware, and registers the gpiochip. Set operations update the software shadow and write `XWAY_STP_CPU0`; software update is triggered only when no hardware-driven bits are reserved.

State and persistence behavior: output state is cached in `shadow` and mirrored into MMIO. Hardware-reserved ownership is held in `reserved` for the device lifetime. No suspend/resume or persistent storage is implemented.

Dependencies and integration points: depends on platform Device Tree matching, Lantiq machine compatible checks, clock gating, MMIO access, and gpiolib. It is registered at `subsys_initcall()` for early platform use.

Risks and test signals: request rejects only reserved GPIOs below 8 even though `reserved` can encode higher PHY groups, so board mappings should be reviewed carefully. Group count comes from `fls(groups) * 8`, so sparse group masks expose intermediate GPIOs. Test with DT variants for group count, DSL/PHY reservation, clock failures, rising/falling edge configuration, and writes that update only software-controlled pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-stp-xway.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-syscon.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-syscon.c

Purpose: exposes selected bits in shared syscon registers as GPIO lines for simple SoC control registers that do not justify a full hardware-specific GPIO driver.

Important APIs, types, and functions: `struct syscon_gpio_data` describes capabilities, bit count, data/direction offsets, and optional custom set callback. `struct syscon_gpio_priv` holds the gpiochip, regmap, match data, and per-device register offsets. Core callbacks are `syscon_gpio_get()`, `syscon_gpio_set()`, `syscon_gpio_dir_in()`, and `syscon_gpio_dir_out()`. Special writers are `rockchip_gpio_set()` for write-mask registers and `keystone_gpio_set()` for lock-bit set-only behavior.

Control flow: probe obtains match data, resolves a syscon regmap from `gpio,syscon-dev` or the parent node, optionally reads data/direction offsets from phandle arguments, installs callbacks according to feature flags, and registers the gpiochip. Reads and writes translate a logical offset into 32-bit syscon register index and bit position.

State and persistence behavior: no driver-private runtime state beyond offsets and match data. GPIO values and direction live in the shared syscon registers and survive as hardware state until overwritten by this or another syscon consumer.

Dependencies and integration points: integrates with `regmap`, `mfd/syscon`, Device Tree compatibles for Cirrus EP7209 modem-control GPIO, TI Keystone DSP GPIO, and Rockchip RK3328 mute GPIO.

Risks and test signals: shared syscon registers require correct masks and offsets; incorrect DT offsets can corrupt unrelated control bits. Direction update return values are ignored in `dir_in()` and only the final set result is returned in `dir_out()`. Test read/write bit addressing across 32-bit boundaries, parent-regmap fallback, Rockchip write-mask semantics, Keystone set-only behavior, and feature-flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-syscon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.c

Purpose: provides the reusable Intel Tangier-family GPIO core, including MMIO GPIO direction/value handling, debounce configuration, chained interrupt handling, wake mask programming, pinctrl range registration, and suspend/resume context save.

Important APIs, types, and functions: `struct tng_gpio_context` stores saved per-32-line registers. The exported entry point is `devm_tng_gpio_probe()`, and exported PM ops are `tng_gpio_pm_ops`. GPIO callbacks include `tng_gpio_get()`, `tng_gpio_set()`, direction helpers, `tng_gpio_get_direction()`, and `tng_gpio_set_config()`. IRQ callbacks are `tng_irq_ack()`, `tng_irq_mask()`, `tng_irq_unmask()`, `tng_irq_set_type()`, `tng_irq_set_wake()`, and chained `tng_irq_handler()`.

Control flow: platform wrapper code fills `struct tng_gpio` from `gpio-tangier.h` and calls `devm_tng_gpio_probe()`. The core allocates context storage, initializes gpiochip callbacks and a nested gpio IRQ chip, wires one parent IRQ to `tng_irq_handler()`, then registers the chip. IRQ type programming updates rising/falling/level polarity registers and switches the Linux IRQ flow handler. Suspend snapshots level, direction, edge, mask, and wake registers; resume restores them.

State and persistence behavior: line state lives in MMIO, with register snapshots in `ctx` only across system sleep. `raw_spinlock_t lock` serializes register RMW sequences. Wake status is cleared when wake is configured.

Dependencies and integration points: depends on gpiolib, irqchip helpers, pinconf generic bias delegation, pinctrl ranges from platform data, and namespace export `GPIO_TANGIER` for wrappers.

Risks and test signals: wrapper-provided `ngpio`, wake register offsets, IRQ number, and pin ranges must match hardware. Level-trigger programming intentionally writes polarity before type to avoid glitches. Test GPIO input/output, debounce enable/disable, each IRQ type, wake mask changes, chained IRQ fan-out, pin range registration, and suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.h

Purpose: declares the private/public contract for Intel Tangier-family GPIO platform wrappers that reuse `gpio-tangier.c`.

Important APIs, types, and functions: defines wake register constants for Elkhart Lake and Merrifield, `struct tng_wake_regs`, `struct tng_gpio_pinrange`, `GPIO_PINRANGE()`, `struct tng_gpio_pin_info`, `struct tng_gpio_info`, and the main `struct tng_gpio`. It declares `devm_tng_gpio_probe()` and `tng_gpio_pm_ops`.

Control flow: no runtime flow is implemented in the header. Platform drivers allocate or embed `struct tng_gpio`, fill MMIO base, IRQ, wake registers, pin information, and GPIO/IRQ numbering, then hand it to the core probe helper.

State and persistence behavior: describes the state owned by the core: gpiochip, MMIO base, raw spinlock, device pointer, suspend context pointer, wake register layout, pinctrl range data, and GPIO count/base metadata. Persistence is runtime-only except for PM snapshots allocated by the C file.

Dependencies and integration points: includes gpiolib, PM, spinlock types, and Linux integer types. The export declaration lets architecture/platform-specific modules reuse the shared implementation without duplicating GPIO logic.

Risks and test signals: the ABI between wrapper and core is structural, so incorrect `ngpio`, `first`, wake offsets, or pin ranges will create hard-to-debug line or IRQ mismatches. Test by building all wrappers that include this header, verifying exported namespace use, and validating that pin range and wake register constants match the target SoC data sheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tb10x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tb10x.c

Purpose: implements the Abilis TB10x GPIO controller using the generic GPIO library, with optional edge-both interrupt-controller support.

Important APIs, types, and functions: `struct tb10x_gpio` holds MMIO base, optional IRQ domain, parent IRQ, and `gpio_generic_chip`. `tb10x_gpio_to_irq()` maps GPIO offsets into a linear IRQ domain. `tb10x_gpio_irq_set_type()` accepts only `IRQ_TYPE_EDGE_BOTH`. `tb10x_gpio_irq_cascade()` dispatches enabled change bits. Probe configures generic GPIO registers for data and direction.

Control flow: probe requires an OF node and `abilis,ngpio`, maps MMIO, initializes a generic chip, overrides `ngpio` and request/free callbacks, registers the gpiochip, and, when `interrupt-controller` is present, requests the parent IRQ, creates a linear domain, allocates a generic IRQ chip, and binds ack/mask registers. Remove tears down the generic IRQ chip and domain.

State and persistence behavior: direction/data state lives in controller registers. IRQ mask and pending bits live in hardware/generic irqchip state. No PM state is saved.

Dependencies and integration points: depends on OF, `gpio_generic_chip_init()`, gpiolib, irqdomain generic-chip helpers, and a parent interrupt line.

Risks and test signals: `BIT(ngpio) - 1` in removal assumes `ngpio` is representable in an unsigned long bit mask; large or invalid DT values are risky. Only both-edge interrupts are supported despite generic Linux IRQ type APIs. Test GPIO register access, DT `ngpio`, no-interrupt mode, parent IRQ sharing, change-register acking, mask behavior, and invalid IRQ type rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tb10x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tc3589x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tc3589x.c

Purpose: exposes Toshiba TC3589x MFD GPIO lines and nested interrupts, including drive-mode configuration for push-pull, open-drain, and open-source modes.

Important APIs, types, and functions: `struct tc3589x_gpio` owns the gpiochip, parent MFD pointer, IRQ mutex, and cached interrupt registers. GPIO callbacks are `tc3589x_gpio_get()`, `tc3589x_gpio_set()`, direction helpers, `tc3589x_gpio_get_direction()`, and `tc3589x_gpio_set_config()`. IRQ callbacks cache `REG_IBE`, `REG_IEV`, `REG_IS`, `REG_IE`, and `REG_DIRECT`, flush them in `tc3589x_gpio_irq_sync_unlock()`, and dispatch nested IRQs in `tc3589x_gpio_irq()`.

Control flow: probe obtains the parent MFD data and parent IRQ, allocates state, brings the GPIO block out of reset, disables direct keyboard interrupts, installs a threaded IRQ handler, configures a threaded nested gpio IRQ chip, and registers the gpiochip. GPIO set uses a two-byte data/mask block write.

State and persistence behavior: hardware registers hold values, directions, drive modes, and interrupt state. Cached IRQ register arrays coalesce bus writes during IRQ bus lock/unlock. No suspend cache is implemented here.

Dependencies and integration points: depends on `linux/mfd/tc3589x.h` register helpers, platform MFD child creation, threaded IRQ handling, gpiolib nested IRQ support, and pinconf drive parameters.

Risks and test signals: failed writes during IRQ cache flush are not propagated. Interrupt cache must remain synchronized with hardware across reset or external modification. Test reset release, direction and get/set paths, open-drain/open-source register programming, IRQ type combinations, mask/unmask cache flushing, threaded nested IRQ dispatch, and status clear after handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tc3589x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra.c

Purpose: implements legacy NVIDIA Tegra20/Tegra30/Tegra210 GPIO controllers with banked MMIO GPIO, optional debounce, chained bank IRQs, hierarchical parent IRQ support, debugfs visibility, and noirq suspend/resume.

Important APIs, types, and functions: `struct tegra_gpio_bank` stores per-bank locks, debounce counts, and PM snapshots. `struct tegra_gpio_soc_config` describes register layout and debounce support. `struct tegra_gpio_info` holds device, MMIO, bank data, gpiochip, bank count, and parent IRQs. GPIO callbacks cover request/free, direction, get/set, get_direction, and debounce `set_config`. IRQ callbacks include ack, mask, unmask, set_type, shutdown, wake, affinity, resource request/release, and chained `tegra_gpio_irq_handler()`.

Control flow: probe counts platform IRQs as banks, allocates bank/IRQ arrays, initializes locks, optionally finds the Tegra210 PMC parent domain, maps registers, disables all GPIO interrupts, registers the gpiochip, and creates debugfs. IRQ set_type programs `GPIO_INT_LVL`, makes the line input, locks it as IRQ, and optionally forwards type to a parent domain. The chained handler scans ports in the bank associated with the parent IRQ and dispatches pending enabled bits.

State and persistence behavior: hardware registers hold line configuration. Debounce count is cached per port because the register is shared. PM saves CNF, OUT, OE, INT_ENB, INT_LVL, debounce, and wake masks and restores them on resume.

Dependencies and integration points: integrates with pinctrl GPIO request/direction, irqdomain hierarchy, optional PMC wake parent, debugfs, and OF compatibles for Tegra20/30/210.

Risks and test signals: fixed base `0` can collide in systems with multiple static GPIO ranges. Edge handler temporarily exits chained context for edge interrupts, so IRQ ordering should be tested. Test all SoC configs, debounce shared-port maximum behavior, PMC wake routing, suspend wake masks, debugfs output, and pinctrl failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra186.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra186.c

Purpose: implements the newer NVIDIA Tegra186-and-later GPIO controller family, covering many main/AON/UPHY/compute/system instances with data-driven port tables, security/VM accessibility filtering, hierarchical IRQ routing, optional hardware timestamping, and OF/ACPI matching.

Important APIs, types, and functions: `struct tegra_gpio_port` describes hardware bank/port/pin counts, `struct tegra_gpio_soc` describes a controller instance, and `struct tegra_gpio` owns gpiochip, register apertures, IRQ list, and SoC data. GPIO callbacks include base lookup, valid-mask initialization, direction, get/set, debounce `set_config`, pin-range addition, OF xlate, and HTE timestamp enable/disable. IRQ callbacks include ack, mask/unmask, set_type, set_wake, chained `tegra186_gpio_irq()`, translation, parent fwspec population, and child-to-parent mapping.

Control flow: probe counts IRQs, allocates a variable-size state object, maps security and GPIO apertures, validates interrupts-per-bank, records IRQs, builds line names, initializes gpio callbacks and a hierarchical gpio IRQ chip, optionally programs default interrupt route mappings, locates a wakeup/PMC parent domain, builds the per-line parent IRQ map, and registers the gpiochip. Chained IRQ handling scans ports belonging to the triggering bank and dispatches set status bits.

State and persistence behavior: line value, direction, trigger, debounce, interrupt enable, and timestamp enable live in per-pin registers. Valid line masks are derived from security and optional VM registers at registration. No suspend snapshot is implemented in this file.

Dependencies and integration points: depends on DT binding GPIO numbers, ACPI IDs, platform resources named `security` and `gpio`, parent irqdomains, optional HTE support, pinctrl group ranges for selected SoCs, and PMC/wakeup-parent nodes.

Risks and test signals: port tables are large and SoC-specific; any bank/port/pin error corrupts numbering and IRQ routing. Default route programming assumes host ownership when security registers are unlocked. Test each compatible/ACPI ID, VM inaccessible-line masking, multi-IRQ-per-bank route selection, wakeup-parent deferral, HTE edge modes, debounce limits, pin range registration, and line-name numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra186.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-thunderx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-thunderx.c

Purpose: implements the Cavium ThunderX/OCTEON-TX PCI GPIO controller with MMIO GPIO access, per-line MSI-X backed interrupts, open-drain handling, inversion compensation, and debounce/glitch filter configuration.

Important APIs, types, and functions: `struct thunderx_gpio` owns the gpiochip, register base, MSI-X entries, per-line metadata, raw spinlock, invert/open-drain masks, and MSI base. `struct thunderx_line` stores per-line filter bits. GPIO callbacks include request, direction, get/set, set_multiple, get_direction, and set_config. IRQ callbacks include ack, mask, mask_ack, unmask, enable/disable, set_type, parent hwirq translation, and MSI allocation info population.

Control flow: PCI probe enables and maps BAR0, determines GPIO count and base MSI from `GPIO_CONST` or CN88XX fallback, initializes per-line filter/inversion/open-drain state from hardware, enables MSI-X for every line, configures gpiochip callbacks and a hierarchical IRQ chip using the MSI domain, registers the gpiochip, then pushes irq_data/domain state for each MSI vector. Remove pops those IRQs and removes the gpio IRQ domain.

State and persistence behavior: hardware contains line config, output, interrupt, and filter state. Driver bitmaps mirror inversion and open-drain choices so get/set and direction compensate for hardware inversion behavior. No PM persistence is implemented.

Dependencies and integration points: depends on PCI managed resources, MSI-X, gpiolib hierarchical IRQ support, pinconf drive/debounce parameters, and 64-bit MMIO access.

Risks and test signals: `set_multiple()` loops through `chip->ngpio / 64` inclusive, so mask array sizing and partial second banks must be correct. Open-drain causes hardware inversion and requires careful value preservation. Test CN88XX fallback, non-GPIO pin rejection, MSI-X allocation, IRQ type flow-handler selection, debounce bounds, open-drain/push-pull transitions while output, and remove-time domain cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-thunderx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-timberdale.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-timberdale.c

Purpose: supports the Timberdale FPGA GPIO block as a built-in platform driver with legacy platform-data GPIO numbering and optional chained interrupt support.

Important APIs, types, and functions: `struct timbgpio` stores MMIO base, spinlock, gpiochip, legacy IRQ base, and cached interrupt enable register. GPIO callbacks are input/output direction, get, set, and `to_irq()`. IRQ callbacks are enable/disable, set_type, and chained `timbgpio_irq()`.

Control flow: probe requires platform data with `nr_pins <= 32`, maps MMIO, sets gpiochip callbacks and legacy base, registers the gpiochip, disables interrupts, and, if a parent IRQ plus positive IRQ base exist, manually installs per-line IRQ chips and a chained parent handler. The chained handler acknowledges the parent, reads and clears pending bits, temporarily disables IER to avoid hardware corruption with simultaneous IRQs, dispatches each mapped IRQ, and restores the cached enable mask.

State and persistence behavior: direction/value/IRQ mode live in FPGA registers. `last_ier` mirrors enabled IRQ lines to repair IER after the hardware erratum path. No dynamic IRQ domain or PM save exists.

Dependencies and integration points: depends on legacy `timb_gpio_platform_data`, raw I/O access, static IRQ descriptors, and built-in platform registration.

Risks and test signals: manual legacy IRQ setup is fragile compared with modern irqdomains. Direction-output ignores the requested initial value and only changes direction. Both-edge IRQs require hardware version greater than 2. Test platform-data validation, no-IRQ mode, version-dependent both-edge setup, IER erratum workaround, IRQ base mapping, and value behavior when switching to output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-timberdale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tn48m.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tn48m.c

Purpose: exposes Delta TN48M CPLD GPI/GPO register blocks through the generic `gpio-regmap` helper.

Important APIs, types, and functions: `enum tn48m_gpio_type` differentiates GPO and GPI blocks. `struct tn48m_gpio_config` describes line count, lines per register, and type. `tn48m_gpio_probe()` builds a `gpio_regmap_config` from match data and a parent regmap.

Control flow: probe checks for a parent device, fetches match data, reads the `reg` property as the register base, obtains the parent's regmap, fills `gpio_regmap_config`, selects either `reg_set_base` for output-only or `reg_dat_base` for input-only, and registers the gpio-regmap device.

State and persistence behavior: no local mutable state is kept. GPIO values live in the parent CPLD regmap registers.

Dependencies and integration points: depends on parent MFD/regmap creation, OF compatibles `delta,tn48m-gpo` and `delta,tn48m-gpi`, and the `gpio/regmap.h` framework.

Risks and test signals: a wrong `reg` property or compatible swaps input/output semantics. There is no direction register, so capabilities are fixed by compatible. Test both GPI and GPO compatibles, parent-regmap absence, `reg` parsing, four-line numbering, and gpio-regmap read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tn48m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tpic2810.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tpic2810.c

Purpose: exposes the TI TPIC2810 8-bit LED driver as an output-only GPIO expander over I2C.

Important APIs, types, and functions: `struct tpic2810` stores the gpiochip, I2C client, cached output byte, and mutex. GPIO callbacks are output-only get_direction, direction_output, set, and set_multiple. `tpic2810_set_mask_bits()` performs the cached read-modify-write and SMBus write using command `TPIC2810_WS_COMMAND`.

Control flow: I2C probe allocates state, copies a template 8-line output gpiochip, sets the parent and client, initializes the mutex, and registers the gpiochip. Single and multiple set paths update the cached byte under lock and write the whole output register; cache is updated only after a successful transfer.

State and persistence behavior: `buffer` is the driver's shadow of the output latch. It starts at zero, so the driver assumes initial low/off state until users set lines. Hardware output state may differ if boot firmware programmed it before probe.

Dependencies and integration points: depends on I2C SMBus byte-data writes, OF and I2C ID matching, gpiolib, and sleeping GPIO semantics.

Risks and test signals: there is no hardware readback and set returns success even if `tpic2810_set_mask_bits()` logs no error to caller, because it is void. Initial cache may clobber firmware output state on first write. Test single/multiple updates, I2C write failures preserving cache, output-only direction behavior, and probe via OF and I2C IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tpic2810.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65086.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65086.c

Purpose: exposes the four TPS65086 PMIC GPO bits as output-only GPIO lines.

Important APIs, types, and functions: `struct tps65086_gpio` holds a gpiochip and parent `struct tps65086`. GPIO callbacks implement output-only get_direction, reject direction_input, set initial output in direction_output, read back with `tps65086_gpio_get()`, and write with `tps65086_gpio_set()`.

Control flow: platform probe obtains parent MFD data, allocates state, copies a four-line template chip, sets the parent to the PMIC device, and registers it. GPIO writes update bits 4..7 of `TPS65086_GPOCTRL` via regmap.

State and persistence behavior: no driver cache; all state resides in the PMIC register map. GPIO operations sleep because regmap may use I2C/SPI.

Dependencies and integration points: depends on `linux/mfd/tps65086.h`, parent MFD driver setup, platform ID `tps65086-gpio`, regmap, and gpiolib.

Risks and test signals: line offsets are translated by `BIT(4 + offset)`, so any future line count change must revisit bit mapping. Input direction is intentionally unsupported. Test register read/write errors, output initial-value setting, readback of GPOCTRL bits, parent drvdata availability, and output-only direction rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65086.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65218.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65218.c

Purpose: exposes three TPS65218 PMIC GPO lines, enforcing PMIC-specific open-drain and sequencer restrictions.

Important APIs, types, and functions: `struct tps65218_gpio` stores parent PMIC data and gpiochip. GPIO callbacks are request, direction_output, get, set, and set_config. Register writes use protected `tps65218_set_bits()` and `tps65218_clear_bits()` with `TPS65218_PROTECT_L1`.

Control flow: probe gets parent MFD data, copies a three-line template, sets the device parent, and registers the gpiochip. Request validates electrical mode: GPO1 and GPO3 must be open-drain, open-source is rejected for all lines, sequencer functions are disabled for GPO1/GPO3, and mux bits are cleared. Set/output update enable bits in `TPS65218_REG_ENABLE2`; set_config supports fixed open-drain on GPO1/GPO3 and push-pull/open-drain selection on GPO2.

State and persistence behavior: no private cache; PMIC registers hold line state, muxing, buffer mode, and sequencer state.

Dependencies and integration points: depends on parent TPS65218 MFD, regmap-backed protected update helpers, gpiolib line open-drain/open-source flags, OF/platform IDs, and pinconf drive parameters.

Risks and test signals: request-time policy depends on consumers declaring open-drain where required; missing flags cause request failure. Protected writes can fail and must be surfaced. Test all three request paths, sequencer disable, GPO2 drive mode toggling, enable-bit get/set, and invalid offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65218.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65219.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65219.c

Purpose: exposes GPIO/GPO pins on TPS65214/TPS65215/TPS65219 PMICs while respecting different line counts and GPIO0 direction rules.

Important APIs, types, and functions: `struct tps65219_gpio` stores a chip-specific `change_dir` callback, gpiochip, and parent PMIC. There are separate templates and get_direction helpers for TPS65214 and TPS65219. Shared callbacks are `tps65219_gpio_get()`, `tps65219_gpio_set()`, `tps65219_gpio_direction_input()`, and `tps65219_gpio_direction_output()`.

Control flow: probe selects the TPS65214 two-line template or TPS65219 three-line template from the platform ID, installs the appropriate direction-change callback, and registers the chip. Nonzero offsets are output-only GPOs. GPIO0 can be input or output depending on PMIC/NVM state; TPS65219 refuses Linux direction changes because the spec says the bit is NVM/initialize-state controlled, while TPS65214 allows direction changes after validating that the multifunction pin is configured as GPIO rather than VSEL.

State and persistence behavior: PMIC registers hold value and direction. No software cache is maintained.

Dependencies and integration points: depends on `linux/mfd/tps65219.h`, parent regmap, platform IDs for TPS65214/TPS65219, and gpiolib.

Risks and test signals: `tps65219_gpio_get()` calls the TPS65219 get_direction helper even for TPS65214, which deserves regression coverage. GPIO0 status is documented as multifunction and logs a warning. Test chip-ID template selection, output-only errors, TPS65219 NVM direction refusal, TPS65214 VSEL rejection, GPIO0 get behavior, and value bit mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65219.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps6586x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps6586x.c

Purpose: exposes four TPS6586x PMIC GPIO-like outputs and maps them to parent PMIC interrupt virtual IRQs.

Important APIs, types, and functions: `struct tps6586x_gpio` stores the gpiochip and parent device. GPIO callbacks are get, set, direction_output, and `to_irq()`. Register helpers are parent MFD functions `tps6586x_read()`, `tps6586x_update()`, and `tps6586x_irq_get_virq()`.

Control flow: subsys init registers the platform driver. Probe inherits the parent's firmware node, reads optional platform data for static GPIO base, configures a four-line sleeping gpiochip, and registers it. Direction_output first sets the output value in `TPS6586X_GPIOSET2`, then programs function/direction bits in `TPS6586X_GPIOSET1`.

State and persistence behavior: no driver cache. PMIC registers store output values and mode. Input direction is not implemented; a FIXME notes missing dedicated-input handling.

Dependencies and integration points: depends on TPS6586x MFD services, parent IRQ mapping, platform data or dynamic GPIO base, and gpiolib.

Risks and test signals: missing input support limits use cases. `to_irq()` assumes a direct offset from `TPS6586X_INT_PLDO_0`. Test output programming, readback, platform-data base selection, firmware-node inheritance, IRQ mapping for all four lines, and behavior if parent MFD operations fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps6586x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65910.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65910.c

Purpose: implements GPIO support for TPS65910/TPS65911 PMICs, including input/output mode, value access, and optional sleep-control setup from board data or Device Tree.

Important APIs, types, and functions: `struct tps65910_gpio` stores gpiochip and parent PMIC. GPIO callbacks are get, set, direction_output, and direction_input. `tps65910_parse_dt_for_gpio()` reads `ti,en-gpio-sleep` into parent board data when OF is enabled.

Control flow: subsys init registers the platform driver. Probe inherits the parent firmware node, allocates state, chooses `ngpio` based on `tps65910_chip_id()` (`TPS65910_NUM_GPIO` or `TPS65911_NUM_GPIO`), sets optional static GPIO base, parses DT board data if needed, programs `GPIO_SLEEP_MASK` for requested lines, then registers the gpiochip. Direction_output sets value before setting `GPIO_CFG_MASK`.

State and persistence behavior: no private line cache. PMIC registers hold value, status, direction, and sleep-control bits.

Dependencies and integration points: depends on TPS65910 MFD structures, regmap, platform data/OF properties, I2C client naming, and gpiolib.

Risks and test signals: `tps65910_gpio_get()` ignores the `regmap_read()` return value, so failed reads can produce stale/uninitialized results. DT parsing assumes `tps65910->of_plat_data` is available. Test chip variants, sleep property arrays, failed regmap operations, direction transitions, and platform-data versus OF base behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65910.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65912.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65912.c

Purpose: exposes five TPS65912 PMIC GPIO lines with input/output direction and value control.

Important APIs, types, and functions: `struct tps65912_gpio` stores gpiochip and parent PMIC pointer. GPIO callbacks are get_direction, direction_input, direction_output, get, and set. The template chip is five lines, dynamic base, sleeping.

Control flow: platform probe gets parent MFD data, allocates state, copies the template, points the chip parent at the PMIC device, and registers it. Direction_output writes the initial `GPIO_SET_MASK` value before setting `GPIO_CFG_MASK`; direction_input clears the config bit. Get reads `GPIO_STS_MASK`; set updates `GPIO_SET_MASK`.

State and persistence behavior: line state is fully in PMIC registers, with no software cache.

Dependencies and integration points: depends on `linux/mfd/tps65912.h`, parent regmap, platform ID `tps65912-gpio`, and gpiolib.

Risks and test signals: operations assume offset maps directly to `TPS65912_GPIO1 + offset`; line count must match hardware. Test direction read/write, initial output level ordering, get/set regmap failures, parent drvdata availability, and all five offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65912.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps68470.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps68470.c

Purpose: exposes seven regular TPS68470 GPIOs plus three logic outputs used by camera/power sequencing, with optional I2C daisy-chain setup.

Important APIs, types, and functions: `struct tps68470_gpio_data` stores the parent regmap and gpiochip. GPIO callbacks are get, get_direction, set, direction_output, and direction_input. `tps68470_enable_i2c_daisy_chain()` configures GPIO1 and GPIO2 as inputs when the `daisy-chain-enable` property is present. Line names identify `gpio.0`..`gpio.6`, `s_enable`, `s_idle`, and `s_resetn`.

Control flow: probe obtains the parent regmap from drvdata, fills a ten-line sleeping gpiochip, registers it, then applies optional daisy-chain mode. Regular GPIOs use `TPS68470_REG_GPDO` and per-line control registers for direction; logic outputs use `TPS68470_REG_SGPO` and are always outputs.

State and persistence behavior: no cache is used. Direction, data, and special output state live in PMIC registers.

Dependencies and integration points: depends on TPS68470 MFD register definitions, regmap, platform child creation, device properties, and gpiolib.

Risks and test signals: error messages in `tps68470_gpio_get()` always print `TPS68470_REG_SGPO` even when reading regular GPIO data. Daisy-chain setup runs after gpiochip registration, so failure leaves a registered chip with probe failure unwind. Test regular versus logic-output offsets, direction rejection for logic outputs as inputs, daisy-chain property behavior, line names, and regmap error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps68470.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tqmx86.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tqmx86.c

Purpose: implements GPIO for the TQ-Systems TQMx86 PLD, exposing four output lines and four input lines, with optional chained edge interrupts on input lines.

Important APIs, types, and functions: `struct tqmx86_gpio_data` stores gpiochip, I/O port mapping, parent IRQ, raw spinlock, output shadow bitmap, and per-line IRQ type state. GPIO callbacks are get, set, direction_input, direction_output, and get_direction. IRQ callbacks are mask, unmask, set_type, chained `tqmx86_gpio_irq_handler()`, valid-mask initialization, and chip printing.

Control flow: probe maps an I/O resource, initializes outputs as outputs and inputs as inputs, clears output shadow to zero because hardware cannot read previous output state, enables runtime PM, optionally masks/clears interrupts and wires a one-parent gpio IRQ chip, then registers the gpiochip. Both-edge interrupt mode is emulated by flipping the configured edge after each interrupt based on current input level.

State and persistence behavior: output shadow is authoritative for output register writes. `irq_type[]` stores trigger and unmasked state. Runtime PM callbacks are no-ops but provide a PM device for IRQ-domain use.

Dependencies and integration points: depends on platform I/O resources, optional parent IRQ, gpiolib irqchip helpers, raw port I/O, runtime PM, and fixed PLD register layout.

Risks and test signals: output lines can technically be reconfigured by callbacks even though hardware naming implies fixed outputs/inputs; interrupt valid mask clears only outputs. Probe zeroes all outputs, which may alter board state. Test input/output directions, output shadow consistency, optional no-IRQ probe, IRQ valid-mask, both-edge emulation, runtime PM domain attachment, and cleanup after registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tqmx86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4800.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4800.c

Purpose: supports the Technologic Systems TS-4800 FPGA GPIO block through the generic GPIO MMIO helper.

Important APIs, types, and functions: `ts4800_gpio_probe()` is the only substantive function. It configures `gpio_generic_chip_config` with 16-bit register width, separate input, output, and direction-output registers.

Control flow: probe allocates a generic chip, maps the MMIO resource, initializes generic GPIO with `dat`, `set`, and `dirout` offsets, then registers the gpiochip. The platform driver uses `module_platform_driver_probe()`.

State and persistence behavior: no private state beyond the generic chip; GPIO value and direction are in FPGA registers. No IRQ or PM support is implemented.

Dependencies and integration points: depends on OF compatible `technologic,ts4800-gpio`, platform MMIO resource mapping, and `gpio_generic_chip_init()`.

Risks and test signals: `dat` points at the input register while `set` points at output; readback behavior depends on generic GPIO semantics and hardware mirroring. The static driver struct also sets `.probe`, while the macro supplies probe registration. Test resource mapping failure, generic-chip initialization, 16-bit register access, direction-output register polarity, and OF match loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4900.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4900.c

Purpose: exposes Technologic Systems I2C FPGA digital I/O lines, including TS-4900 style separate input bits and TS-7970 style input-on-output-bit variants.

Important APIs, types, and functions: `struct ts4900_gpio_priv` stores regmap, gpiochip, and selected input bit. GPIO callbacks are get_direction, direction_input, direction_output, get, and set. The regmap uses 16-bit register addresses and 8-bit values.

Control flow: I2C probe reads optional `ngpios` defaulting to 32, selects the input bit from OF match data, initializes an I2C regmap, and registers a sleeping gpiochip. Direction_input clears OE with a read-modify-write to avoid racing output data. Direction_output preloads the output bit before enabling OE when transitioning from input to output to avoid line glitches.

State and persistence behavior: no software cache. Each GPIO offset is a separate FPGA register containing OE, OUT, and IN/status bits.

Dependencies and integration points: depends on I2C, regmap, OF compatibles `technologic,ts4900-gpio` and `technologic,ts7970-gpio`, optional `ngpios`, and gpiolib.

Risks and test signals: several regmap reads ignore return status before using `reg`, so bus failures can produce undefined decisions. Direction_output writes whole register values rather than masked updates in the final step. Test both compatible input-bit modes, glitchless transition ordering, ngpio override, regmap error injection, and per-offset register addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4900.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts5500.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts5500.c

Purpose: supports Technologic Systems TS-5500/TS-5600 DIO blocks and LCD-as-DIO blocks using legacy x86 I/O ports, with per-block pinout tables and limited hardware IRQ routing.

Important APIs, types, and functions: `struct ts5500_dio` describes each line's value port, control port, direction capability, and optional IRQ. `struct ts5500_priv` stores the pinout, gpiochip, spinlock, strap mode, and hardware IRQ. GPIO callbacks are input, output, get, set, and `to_irq()`. `ts5500_enable_irq()` and `ts5500_disable_irq()` toggle board-specific IRQ enable bits.

Control flow: probe selects a pinout from platform ID, requests the relevant I/O port regions, arbitrates shared port `0x7d` with global `hex7d_reserved`, forces LCD mode when needed, registers the gpiochip, and enables the block's hardware IRQ. Direction and value operations use locked `inb()`/`outb()` read-modify-write cycles. Remove disables the IRQ enable bit.

State and persistence behavior: no per-line software value cache. Hardware port registers hold direction and values. Global `hex7d_reserved` persists across device instances and prevents duplicate region requests.

Dependencies and integration points: depends on platform IDs, legacy I/O port resources, board wiring tables, gpiolib, and fixed ISA IRQ numbers.

Risks and test signals: `hex7d_reserved` is never cleared on remove, so unload/rebind behavior can differ. IRQs are not represented as a modern irqdomain; `to_irq()` returns fixed hardware IRQs or strapped IRQs. Test all block IDs, shared 0x7d ordering, input-only/output-only rejection, LCD DIO mode, IRQ enable/disable bits, and multi-instance probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts5500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-twl4030.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-twl4030.c

Purpose: implements GPIO and optional LED-as-GPIO support for TWL4030/TPS659x0 MFD chips, including pull/debounce configuration, module power gating by usage, GPIO IRQ setup, and an OMAP3 WLAN power quirk.

Important APIs, types, and functions: `struct gpio_twl4030_priv` stores gpiochip, mutex, IRQ base, usage bitmask, direction cache, and output-state cache. GPIO callbacks are request, free, direction_input, direction_output, get_direction, get, set, and `to_irq()`. Helpers program TWL GPIO registers, LED PWM/output registers, pullups/pulldowns, debounce, and OF platform data.

Control flow: probe allocates state, creates legacy IRQ descriptors and a simple domain when built-in, calls `twl4030_sih_setup()`, parses OF properties, configures pulls and debounce, optionally adds two LED output GPIOs, registers the chip, and applies a Compulab OMAP3 WLAN power hog/export quirk. Request powers the GPIO module on for first GPIO use and initializes LED outputs when requested. Free powers the module off after last GPIO use.

State and persistence behavior: driver caches usage, direction, output state, and LEDEN. Hardware registers hold actual values, pulls, debounce, and module power. No suspend/resume is in this file.

Dependencies and integration points: depends on TWL MFD I2C helpers, SIH IRQ setup, OF properties `ti,use-leds`, `ti,debounce`, `ti,mmc-cd`, `ti,pullups`, `ti,pulldowns`, and gpiolib descriptors.

Risks and test signals: IRQ dispatch is refused for loadable module builds because genirq setup needs built-in availability. `twl_get()` rejects unrequested lines. LED GPIOs invert drive semantics through open-drain LED registers. Test module power usage counts, OF pull/debounce programming, LED request/free, IRQ mapping, OMAP3 quirk cleanup, and I2C failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-twl4030.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-twl6040.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-twl6040.c

Purpose: exposes TWL6040/TWL6041 MFD GPO pins as output-only GPIO lines.

Important APIs, types, and functions: a static `gpio_chip` named `twl6040gpo_chip` provides get, set, get_direction, and direction_output callbacks. The callbacks access `TWL6040_REG_GPOCTL` via parent MFD `twl6040_reg_read()` and `twl6040_reg_write()`.

Control flow: platform probe inherits the parent firmware node, reads the parent revision, sets dynamic base, chooses three GPOs for TWL6040 revisions before TWL6041 ES2.0 or one GPO for newer TWL6041, sets the parent device, and registers the gpiochip with parent `struct twl6040` as chip data.

State and persistence behavior: no local cache. Output state lives in the GPO control register. The static gpiochip's `ngpio` field is changed at probe time.

Dependencies and integration points: depends on TWL6040 MFD revision and register helpers, platform child creation, and gpiolib.

Risks and test signals: using a static gpiochip object makes multiple simultaneous instances unsafe. Set performs read-modify-write without an explicit driver lock, relying on MFD serialization if any. Test revision-dependent line count, output-only direction, register read/write failures, firmware-node inheritance, and multi-instance assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-twl6040.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-uniphier.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-uniphier.c

Purpose: implements Socionext UniPhier GPIO with banked MMIO GPIO operations, hierarchical IRQs through the parent AIDET interrupt controller, both-edge support via noise filter hardware, and late suspend/resume state save.

Important APIs, types, and functions: `struct uniphier_gpio_priv` contains gpiochip, irq_chip, child irqdomain, MMIO base, spinlock, and flexible saved register array. GPIO callbacks are get_direction, direction_input, direction_output, get, set, set_multiple, and `to_irq()`. IRQ domain callbacks allocate parent IRQs using `socionext,interrupt-ranges`, activate/deactivate gpiochip IRQ locks, and translate fwspecs.

Control flow: probe locates the parent IRQ domain, reads `ngpios`, allocates enough saved-register slots, maps MMIO, fills gpiochip and irq_chip operations, initializes filter cycle count, registers the gpiochip, creates a hierarchical IRQ domain, and stores drvdata. `to_irq()` only maps offsets at or above `UNIPHIER_GPIO_IRQ_OFFSET`. IRQ set_type enables both-edge mode and filter bits locally, then programs the parent as falling-edge for both-edge mode.

State and persistence behavior: hardware stores data, direction, IRQ enable/mode/filter. Suspend saves per-bank data/direction plus IRQ control registers; resume restores them and reinitializes filter cycle count.

Dependencies and integration points: depends on DT binding constants, parent OF IRQ domain, `socionext,interrupt-ranges`, gpiolib, irqdomain hierarchy, and late system sleep PM ops.

Risks and test signals: interrupt range parsing is mandatory for IRQ allocation; incorrect ranges break `to_irq()`. Both-edge mode depends on a shared noise filter period, not per-line debounce. Test ngpio bank calculations, non-contiguous register offsets, set_multiple clumps, IRQ offset gating, parent mapping ranges, both-edge/filter behavior, and suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-uniphier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-usbio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-usbio.c

Purpose: implements Intel USBIO GPIO support as an auxiliary-bus client, exposing firmware-described USBIO GPIO banks through gpiolib and USBIO control messages.

Important APIs, types, and functions: `struct usbio_gpio_bank` stores per-pin cached config bytes and a firmware bitmap. `struct usbio_gpio` stores the config mutex, bank array, gpiochip, and auxiliary device. GPIO callbacks are get_direction, direction_input, direction_output, get, set, and set_config. `usbio_gpio_update_config()` serializes config cache updates and sends `USBIO_GPIOCMD_INIT`.

Control flow: auxiliary probe obtains bank descriptors from platform data, allocates state, initializes a mutex, binds ACPI companion IDs, copies bank bitmaps until an empty descriptor, fills a sleeping gpiochip with `ngpio = bank_count * USBIO_GPIOSPERBANK`, registers it, then clears ACPI dependencies. Read/write operations send `USBIO_GPIOCMD_READ` and `USBIO_GPIOCMD_WRITE`; direction and bias/drive configuration send INIT messages.

State and persistence behavior: per-pin config bytes are cached in memory and updated under `config_mutex`. Actual GPIO state and config live behind USBIO firmware/control messages. Firmware bitmaps are advisory; invalid bitmap bits warn once but do not block access.

Dependencies and integration points: depends on auxiliary bus, Intel USBIO namespace APIs, ACPI IDs, USBIO platform data, pinconf bias/drive parameters, and gpiolib.

Risks and test signals: config cache starts zeroed rather than read from hardware, so first config update may clear firmware defaults outside the masked field only if masks are wrong. Control message short transfers are protocol errors on read but write return values are passed through directly. Test ACPI binding, bank bitmap warnings, read short-transfer handling, direction/value commands, bias configuration, dependency clearing, and namespace import.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-usbio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-vf610.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-vf610.c

Purpose: supports Freescale/NXP VF610, i.MX7ULP, and i.MX8ULP GPIO/PORT blocks using generic GPIO data registers plus PORT interrupt configuration.

Important APIs, types, and functions: `struct fsl_gpio_soc_data` records whether a SoC has PDDR and dual register bases. `struct vf610_gpio_port` owns the generic gpio chip, PORT base, GPIO base, saved IRQ config per pin, optional clocks, and parent IRQ. IRQ callbacks include chained handler, ack, set_type, mask, unmask, and wake. Probe configures `gpio_generic_chip_config`.

Control flow: probe selects SoC data, handles legacy compatible combinations for dual-base mapping, maps PORT/GPIO resources, obtains the parent IRQ, enables optional `port` and `gpio` clocks with devm cleanup, initializes generic GPIO using PDIR/PDOR/PDDR as available, masks all pin interrupts by clearing PCRs, clears ISFR, wires a one-parent gpio IRQ chip, and registers the chip. IRQ set_type stores the PORT IRQC mode and switches Linux flow handler; unmask writes the stored IRQC to the pin PCR.

State and persistence behavior: GPIO data/direction live in GPIO registers. `irqc[32]` caches requested interrupt modes while masked. Clock enable state is managed by devm actions. No suspend register snapshot is included; IRQ chip flags handle wake/mask behavior during suspend.

Dependencies and integration points: depends on OF compatibles, optional clocks, pinctrl-backed generic GPIO, chained IRQs, irqchip wake flags, and platform MMIO resources.

Risks and test signals: masking writes zero to the whole PCR, which may clear pin configuration bits if pinctrl has not restored them separately. Dual-base compatible handling must match DT resource layouts. Test all compatible data paths, optional/deferred clocks, generic GPIO direction with/without PDDR, IRQ type mapping, wake enable/disable, initial interrupt masking, and pinctrl interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-vf610.c -->
