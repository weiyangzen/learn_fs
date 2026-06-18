# subset-b-001305 GPIO Driver Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rcar.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rcar.c

## Purpose
This driver exposes Renesas R-Car GPIO banks as `gpio_chip` instances with GPIO-line IRQ support and sleep/resume restoration. It supports several R-Car hardware generations through `struct gpio_rcar_info`, which records feature differences such as `OUTDTSEL`, both-edge trigger support, always-valid input reads, and the Gen4 `INEN` input-enable register.

## Important APIs, Types, and Functions
Key state lives in `struct gpio_rcar_priv`: MMIO base, raw spinlock, gpio chip, parent IRQ, wakeup-path counter, generation info, and a `struct gpio_rcar_bank_info` register snapshot for suspend. Register helpers `gpio_rcar_read()`, `gpio_rcar_write()`, and `gpio_rcar_modify_bit()` centralize MMIO access. Gpiolib callbacks include request/free, direction, get/set, and multiple-line operations. IRQ callbacks are collected in immutable `gpio_rcar_irq_chip` and include mask/unmask, type configuration, wake control, and a shared parent IRQ handler.

## Control Flow
`gpio_rcar_probe()` allocates private state, parses DT match data and `gpio-ranges` to derive the number of pins, enables runtime PM, maps the resource, registers the GPIO chip, links the IRQ domain to the PM device, and requests the parent IRQ with `gpio_rcar_irq_handler()`. GPIO requests runtime-resume the controller and delegate pin ownership to pinctrl; free returns the line to input mode before dropping runtime PM. Interrupt type selection programs POSNEG, EDGLEVEL, optional BOTHEDGE, and IOINTSEL under the raw spinlock, clearing pending edge interrupts.

## State and Persistence
Runtime state is held in hardware registers plus `wakeup_path`. Suspend snapshots IOINTSEL, INOUTSEL, OUTDT, INTMSK, POSNEG, EDGLEVEL, and optional BOTHEDGE. Resume iterates valid lines and reconstructs either GPIO mode or interrupt mode, then restores unmasked interrupts and enables inputs on Gen4-style hardware. `wakeup_path` is an atomic count incremented by `.irq_set_wake()` and drives `device_set_wakeup_path()`.

## Dependencies and Integration Points
The driver integrates with platform resources, Open Firmware match data, pinctrl GPIO request/free, gpiolib IRQ domains, runtime PM, raw MMIO access, and Linux IRQ wake APIs. `irq_domain_set_pm_device()` binds GPIO IRQs to the device PM lifecycle.

## Risks
IRQ masking uses hardware-specific write-one/clear-style registers and must match the manual precisely. Resume replay can glitch if saved OUTDT/direction/interrupt state is stale or if valid masks exclude lines. Wakeup accounting assumes balanced set_wake calls. Both-edge support is rejected on old hardware, so DT compatibility must select the right generation data.

## Test Signals
Useful tests include GPIO direction/value reads for input and output banks, `get_multiple()` with mixed directions, all supported IRQ trigger types per generation, runtime suspend/resume with GPIOs and IRQs configured, wake-from-suspend with GPIO IRQs, invalid `gpio-ranges`, and Gen4 `INEN` behavior with valid line masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rcar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rda.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rda.c

## Purpose
This platform driver supports RDA Micro GPIO banks. It uses `gpio_generic_chip` for the simple data, set/clear, and direction registers, and adds optional GPIO interrupt support for banks that expose a parent IRQ.

## Important APIs, Types, and Functions
`struct rda_gpio` wraps `struct gpio_generic_chip`, the MMIO base, a spinlock used by read-modify-write register updates, and an optional parent IRQ. `rda_gpio_update()` updates one bit in a register. IRQ support is implemented by `rda_gpio_set_irq()`, `rda_gpio_irq_mask()`, `rda_gpio_irq_unmask()`, `rda_gpio_irq_ack()`, `rda_gpio_irq_set_type()`, and chained handler `rda_gpio_irq_handler()`.

## Control Flow
`rda_gpio_probe()` reads required `ngpios`, obtains an optional IRQ, maps the MMIO resource, initializes the generic GPIO chip with value/set/clear and output-enable set-in/set-out registers, then registers it. If an IRQ exists, the driver configures a `gpio_irq_chip` with one parent IRQ and the chained parent handler. The IRQ handler reads `RDA_GPIO_INT_STATUS`, masks to the low 8 interrupt-capable lines, and dispatches domain IRQs.

## State and Persistence
GPIO state persists in hardware registers only. Trigger type is programmed directly into `RDA_GPIO_INT_CTRL_SET/CLR`; the driver does not keep software shadow copies beyond the generic chip's internal state. There are no suspend/resume hooks.

## Dependencies and Integration Points
The driver depends on platform device resources, firmware property `ngpios`, gpiolib generic helpers, and chained irqchip support. IRQ-capable variants expose only the lower eight lines as interrupt sources.

## Risks
`ngpios` is required and not bounded against the bank width in this file, so bad firmware can expose nonsensical line counts. Level-high and level-low setup writes only the selected rise/fall bit with the level bit; previous opposite-edge configuration relies on hardware clear behavior and mask calls. Optional parent IRQ handling means consumers must tolerate GPIO-only banks.

## Test Signals
Exercise banks with and without parent IRQs, verify lower-eight IRQ routing only, test all five trigger modes, confirm mask/unmask disables both rise/fall sources, and validate GPIO generic direction/value behavior for the configured `ngpios`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rdc321x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rdc321x.c

## Purpose
This legacy platform driver exposes RDC321x southbridge GPIOs backed by PCI configuration-space registers. It supports two 32-bit register groups and uses platform data from the RDC321x MFD layer to find the southbridge PCI device and GPIO count.

## Important APIs, Types, and Functions
`struct rdc321x_gpio` contains the gpio chip, PCI device pointer, cached data registers, register offsets for control/data pairs, and a spinlock. `rdc_gpio_get_value()` reads through PCI config space after writing the cached selector value. `rdc_gpio_set_value_impl()` updates the cached output register and writes it. `rdc_gpio_config()` sets the line as GPIO and then writes the requested output value.

## Control Flow
`rdc321x_gpio_probe()` validates platform data, obtains named IO resources `gpio-reg1` and `gpio-reg2`, initializes register offsets, reads initial data register values into the cache, and registers the gpio chip. Direction input and direction output both call `rdc_gpio_config()`, with input passing a high value by convention.

## State and Persistence
The driver keeps `data_reg[2]` as a software shadow of the output/data register values because writes are done through PCI config space. It initializes the cache from hardware at probe but has no suspend/resume path.

## Dependencies and Integration Points
It depends on `linux/mfd/rdc321x.h` platform data, PCI config read/write APIs, platform named IO resources, and gpiolib. It uses a static GPIO base of 0, which reflects older board expectations.

## Risks
Direction handling is unusual: input configuration still writes a data value, and there is no separate `get_direction()`. PCI config operations are serialized only by the local spinlock, so any other southbridge user touching the same registers must coordinate externally. Fixed base 0 can collide on systems with other non-dynamic chips.

## Test Signals
Test initial cache loading, both register groups above and below GPIO 32, error propagation from PCI config reads/writes, output set/get consistency, and platform data/resource absence paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rdc321x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-realtek-otto.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-realtek-otto.c

## Purpose
This driver supports Realtek Otto-family GPIO controllers with up to 32 GPIOs, optional edge interrupts, port-order quirks, and optional per-CPU IRQ mask registers. It uses `gpio_generic_chip` for normal GPIO operations and custom IRQ state because the interrupt mask register encodes both type and enable state.

## Important APIs, Types, and Functions
`struct realtek_gpio_ctrl` stores generic GPIO state, MMIO bases, CPU mask data, raw spinlock, per-line `intr_mask` and `intr_type` arrays, and function pointers for port-order-specific reads/writes and IMR bit positions. `realtek_gpio_update_line_imr()` is central: it writes the AND of selected type and enable mask into the 2-bit IMR field. IRQ operations include ack, mask/unmask, set_type, parent handler, optional affinity, and `realtek_gpio_irq_init()`.

## Control Flow
Probe reads match flags, validates `ngpios`, maps the base resource, chooses normal or reversed port ordering, initializes the generic chip, and conditionally wires a parent IRQ unless interrupts are disabled by compatibility data. For per-CPU-capable variants, it maps a second resource, derives present CPUs from resource size, and uses that mask in affinity programming. The chained IRQ handler reads ISR and dispatches set bits through the GPIO IRQ domain.

## State and Persistence
GPIO values and directions are hardware-backed through generic helpers. Interrupt type and mask state are persisted in the driver arrays, then materialized to IMR under the raw spinlock. Hardware ISR is cleared by writing a mask to the ISR register. There are no suspend/resume callbacks.

## Dependencies and Integration Points
The driver integrates with DT match data for Realtek variants, generic GPIO MMIO helpers, chained IRQs, cpumask/affinity APIs, and optional per-CPU MMIO ranges. Endianness and port layout are selected by compatibility flags.

## Risks
Incorrect port-order flags can map GPIO lines to the wrong ISR/IMR bits, causing lost or misdelivered interrupts. The hardware supports edge trigger modes only in this driver. Affinity updates assume the secondary resource width exactly represents per-CPU masks. IMR read-modify-write uses raw `ioread32()` regardless of bank read endian helpers, which must match the IMR register layout.

## Test Signals
Test each compatible's port ordering, all edge trigger modes, IRQ mask/type combinations, ISR clear behavior, optional interrupt-disabled compatible, per-CPU affinity programming on rtl9300-style devices, and `ngpios` boundary handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-realtek-otto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-reg.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-reg.c

## Purpose
`gpio-reg.c` is a small exported helper for devices where up to 32 fixed-direction GPIOs share one register. It offers a `gpio_chip` around a single MMIO register with fixed input/output direction, optional names, and optional GPIO-to-IRQ mapping.

## Important APIs, Types, and Functions
`struct gpio_reg` stores the gpio chip, spinlock, fixed direction bitmask, output shadow, MMIO register, optional irq domain, and per-line IRQ mappings. Public entry points are `gpio_reg_init()` and `gpio_reg_resume()`. Gpiolib callbacks include fixed-direction checks, `gpio_reg_set()`, `gpio_reg_get()`, `gpio_reg_set_multiple()`, and `gpio_reg_to_irq()`.

## Control Flow
Callers invoke `gpio_reg_init()` with the register address, line count, direction mask, default output value, optional line names, and optional IRQ mapping. The helper allocates managed or unmanaged state depending on whether a device is supplied, fills the `gpio_chip`, and registers it. Output writes update the software `out` shadow and write the entire register under a spinlock. Input reads perform a double read because some hardware latches input state on first access.

## State and Persistence
Output state persists in `r->out`, not by reading hardware back. `gpio_reg_resume()` rewrites that shadow to hardware after resume. Inputs are read from hardware only when their direction bit is input.

## Dependencies and Integration Points
This helper is exported through `linux/gpio/gpio-reg.h` for other kernel code. It integrates with gpiolib and optionally `irq_domain` via `.to_irq`.

## Risks
The helper assumes fixed directions and cannot model runtime direction changes. Output reads return the shadow, so external hardware changes are invisible. `set_multiple()` uses the caller's first word mask directly and is intended for <=32 lines. Callers must ensure `direction`, `def_out`, and IRQ arrays match `num`.

## Test Signals
Unit-style users should test fixed direction rejection, input double-read behavior on latch-like registers, output shadow restoration via `gpio_reg_resume()`, `set_multiple()` masking, and IRQ translation with both Linux IRQ numbers and domain hardware IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-regmap.c

## Purpose
This file implements the generic regmap-backed GPIO controller core used by MFDs and bus devices whose GPIO registers are accessible through `struct regmap`. It supports data, set, clear, direction-in, direction-out, fixed-direction, custom register/mask translation, and optional IRQ-domain integration.

## Important APIs, Types, and Functions
`struct gpio_regmap` stores parent device, regmap, gpio chip, register bases, stride/packing parameters, fixed output bitmap, optional regmap-irq data, translator callback, and caller driver data. Public APIs are `gpio_regmap_register()`, `gpio_regmap_unregister()`, `devm_gpio_regmap_register()`, and `gpio_regmap_get_drvdata()`. Core callbacks are `gpio_regmap_get()`, `gpio_regmap_set()`, `gpio_regmap_set_with_clear()`, direction getters/setters, and `gpio_regmap_simple_xlate()`.

## Control Flow
Registration validates the config, allocates state, copies register addresses, configures the gpio chip, determines `ngpio`, copies fixed output masks, defaults packing/stride/translator values, and registers with gpiolib. Optional `CONFIG_REGMAP_IRQ` support can create a regmap IRQ chip and then attach either that domain or a provided IRQ domain to the gpio chip. Unregister removes optional regmap IRQ state, the gpio chip, the bitmap, and the allocation.

## State and Persistence
The core itself keeps little mutable state except the fixed-direction output bitmap and registration metadata. GPIO state lives in regmap-backed hardware/cache. When data and set registers alias, reads use `regmap_read_bypassed()` and writes use `regmap_write_bits()` to avoid polluting or depending on stale cache state from input values.

## Dependencies and Integration Points
Consumers pass `struct gpio_regmap_config` from `<linux/gpio/regmap.h>`. The driver uses gpiolib, regmap, optional regmap-irq, firmware node data, and gpiolib generic request/free helpers. `chip->can_sleep` is derived from `regmap_might_sleep()`.

## Risks
Configuration validation is strict but caller-supplied register bases and translator callbacks determine correctness. `GPIO_REGMAP_ADDR_ZERO` must be used for a real zero register address because zero otherwise means absent. Direction support requires both data and set registers. Regmap cache semantics are subtle when input and output registers alias.

## Test Signals
Test input-only, output-only, data+set, set+clear, direction-in-base, direction-out-base, fixed-direction-output, custom translator, zero-address sentinel use, regmap-backed IRQ domain attachment, managed unregister cleanup, and sleeping versus non-sleeping regmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rockchip.c

## Purpose
This driver registers GPIO banks that are owned by the Rockchip pinctrl controller. It exposes bank GPIO operations, debounce support, IRQ domains, and interrupt demultiplexing for v1 and v2 register layouts.

## Important APIs, Types, and Functions
The driver operates on `struct rockchip_pin_bank` from the Rockchip pinctrl subsystem rather than defining a separate private bank type. `gpio_regs_v1` and `gpio_regs_v2` describe register offsets. Helpers `rockchip_gpio_writel()`, `rockchip_gpio_readl()`, and bit variants abstract v2 write-enable halfword semantics. Gpiolib callbacks are collected in `rockchip_gpiolib_chip`; IRQ setup uses `rockchip_interrupts_register()` and `irq_alloc_domain_generic_chips()`.

## Control Flow
Probe locates the parent pinctrl device, resolves the bank by DT alias or fallback counter, maps the bank resource, enables the clock, reads version ID, selects register layout, registers the gpio chip, attaches pin ranges when old DT lacks `gpio-ranges`, registers interrupts, then applies deferred pin configurations queued by pinctrl. IRQ demux reads `int_status`, optionally toggles polarity for emulated both-edge mode on v1, and dispatches domain IRQs.

## State and Persistence
Bank state is mostly hardware-backed. Software fields include `toggle_edge_mode`, `saved_masks`, clocks, deferred pin lists, pin range metadata, and debounce clock state. IRQ suspend saves the mask register and masks non-wakeup lines; resume restores it. Debounce can enable/disable a second clock and program shared divider registers on v2.

## Dependencies and Integration Points
This file is tightly coupled to `pinctrl-rockchip.h`, `struct rockchip_pinctrl`, OF address/IRQ parsing, clocks, pinctrl generic config, gpiolib, irqdomain generic chips, and postcore initialization so GPIO banks are available early enough for pinctrl users.

## Risks
Register version detection depends on reading the v2 version register after enabling the clock; unsupported IDs fail probe. V1 both-edge interrupts are emulated by polarity toggling and can miss rapid transitions. Debounce divider is shared and only increased when a larger value is requested, which may affect earlier consumers. Error paths after pin range setup require chip removal.

## Test Signals
Test v1 and v2 banks, deferred output/input configuration, `gpio-ranges` and old pin-range fallback, all IRQ trigger types including v1 both-edge emulation and v2 hardware both-edge, suspend/resume mask behavior, debounce enable/disable and invalid debounce ranges, and clock failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rtd.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rtd.c

## Purpose
This platform driver supports Realtek DHC SoC GPIO controllers, including several ISO and MISC register layouts. It provides GPIO direction/value operations, pinconf debounce support, and edge interrupt handling through separate assert and deassert parent IRQs.

## Important APIs, Types, and Functions
`struct rtd_gpio_info` captures per-compatible register offset arrays, GPIO counts, debounce encodings, and a callback for locating debounce bitfields. `struct rtd_gpio` stores the gpio chip, selected info, base and IRQ-base mappings, two parent IRQs, and a raw spinlock. Important functions include `rtd_gpio_set_debounce()`, `rtd_gpio_set/get/direction_*()`, `rtd_gpio_irq_handle()`, `rtd_gpio_enable_irq()`, `rtd_gpio_disable_irq()`, and `rtd_gpio_irq_set_type()`.

## Control Flow
Probe obtains two parent IRQs, selects match data, maps control and IRQ status resources, fills gpiolib callbacks, wires a two-parent `gpio_irq_chip`, and registers the chip. GPIO get checks the direction register and reads either output data or input data. IRQ handling selects the assert or deassert status register family based on parent IRQ, iterates status registers packed as 31 GPIOs plus a write-enable bit, clears status, checks line enable, and dispatches allowed domain IRQs.

## State and Persistence
Hardware registers hold direction, values, interrupt enable, polarity, status, and debounce configuration. The driver stores no IRQ shadow state beyond the immutable layout data and parent IRQ numbers. There are no PM callbacks.

## Dependencies and Integration Points
The driver uses OF match data, platform MMIO resources, two parent interrupts, pinconf generic bias delegation, gpiolib generic request/free, and raw spinlock guard macros from cleanup helpers.

## Risks
Interrupt status packing is unusual: each status register covers 31 GPIOs because bit 0 is write-enable, making off-by-one errors likely. `rtd_gpio_irq_handle()` assumes only the two known parent IRQs call it; otherwise the register-offset function is uninitialized. For deassert IRQs, non-both-edge lines break out of the loop instead of continuing, which makes trigger-type interactions important to test. Only edge triggers are accepted.

## Test Signals
Test each compatible layout's offsets and GPIO counts, debounce values exactly matching 1/10/100/1000/10000/20000/30000 us, assert and deassert parent IRQ delivery, both-edge versus single-edge behavior, invalid trigger types, bias delegation, and boundary GPIOs around 31/32 and bank transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sa1100.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sa1100.c

## Purpose
This ARM SA-1100 GPIO implementation is board/SoC initialization code rather than a discoverable platform driver. It registers one fixed GPIO chip, maps GPIOs to legacy IRQ numbers, handles edge-detect IRQs, and participates in syscore suspend/resume.

## Important APIs, Types, and Functions
`struct sa1100_gpio_chip` stores the gpio chip, register base, IRQ base, and software masks for enabled, rising, falling, and wake IRQs. Gpiolib callbacks are `sa1100_gpio_get/set()`, direction functions, direction query, and `.to_irq`. IRQ functions include `sa1100_gpio_type()`, ack/mask/unmask/wake operations, IRQ domain mapping, and `sa1100_gpio_handler()`.

## Control Flow
`sa1100_init_gpio()` clears edge detect and pending status, registers the gpio chip, creates a simple IRQ domain for 28 GPIO IRQs starting at `IRQ_GPIO0`, and installs chained handlers for GPIO0-10 and GPIO11-27 summary IRQs. The chained handler repeatedly reads GEDR, clears active bits, and calls `generic_handle_irq()` for each set bit.

## State and Persistence
The driver maintains software copies of IRQ rising/falling/mask/wake state and writes GRER/GFER from their intersections. Syscore suspend limits edge detection to wake-enabled lines and clears pending events; resume restores normal edge registers from software state.

## Dependencies and Integration Points
It depends on SA-1100 architecture headers, hard-coded register symbols like `GPLR`, legacy IRQ constants, `sa11x0_gpio_set_wake()`, syscore ops, and gpiolib/irqdomain. The gpio chip uses base 0 and `GPIO_MAX + 1`.

## Risks
There is no dynamic resource management or platform removal path. Direction updates use local IRQ disabling rather than a per-chip spinlock. IRQ type setup accepts any combination with rising/falling bits and does not reject level triggers explicitly. Fixed GPIO numbering and legacy IRQ assumptions must match the platform.

## Test Signals
Validate GPIO get/set/direction against SA-1100 registers, GPIO-to-IRQ mapping, edge-rising/falling/both programming, chained IRQ delivery for individual and grouped parent IRQs, wake enable/disable interactions, and syscore suspend/resume edge restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sa1100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sama5d2-piobu.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sama5d2-piobu.c

## Purpose
This driver exposes the SAMA5D2 SECUMOD PIOBU pins as an eight-line GPIO controller. It uses a syscon regmap for secure-module registers and disables tamper/wakeup detection so pins can be used as ordinary GPIOs.

## Important APIs, Types, and Functions
`struct sama5d2_piobu` contains the gpio chip and syscon regmap. `sama5d2_piobu_setup_pin()` clears the pin's tamper detection bits in backup and normal mode protection registers and clears wakeup participation. `sama5d2_piobu_write_value()` and `sama5d2_piobu_read_value()` access per-pin PIOBU registers. Direction and get/set callbacks translate gpiolib semantics to PIOBU direction, SOD, and PDS bits.

## Control Flow
Probe allocates state, fills an eight-line gpio chip, obtains the regmap from the device node, registers the chip, and then calls setup for every PIOBU line. Direction output writes direction and output state together; get reads PDS for inputs and SOD for outputs.

## State and Persistence
All state is stored in SECUMOD registers through regmap. The driver performs no suspend/resume handling. Initial setup mutates tamper and wakeup configuration persistently for all eight pins.

## Dependencies and Integration Points
The file depends on syscon, regmap, platform DT matching with `atmel,sama5d2-secumod`, and gpiolib. It exposes only GPIO behavior, not IRQ handling.

## Risks
Register setup deliberately disables security/tamper functionality for these pins, so firmware/DT must only bind the driver when GPIO ownership is intended. The chip is registered before per-pin setup; a setup failure returns probe failure but the devm chip registration will unwind. `can_sleep` is set to 0 even though regmap access characteristics depend on the syscon backend.

## Test Signals
Test syscon regmap lookup, all eight per-pin register offsets, input versus output reads, output high/low programming, tamper/wakeup bit clearing, and probe unwind on regmap/setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sama5d2-piobu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sch.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sch.c

## Purpose
This driver supports Intel Poulsbo SCH, Tunnel Creek, Centerton, and Quark-style GPIO blocks behind LPC/iLB platform devices. It handles core and resume-powered banks, GPIO direction/value operations, and optional IRQ delivery via ACPI GPE.

## Important APIs, Types, and Functions
`struct sch_gpio` stores the gpio chip, mapped I/O registers, spinlock, resume-bank base, GPE number, and GPE handler. `sch_gpio_offset()` and `sch_gpio_bit()` map logical GPIO numbers to banked 8-bit registers. GPIO callbacks operate on GEN/GIO/GLV. IRQ support includes `sch_irq_type()`, ack, mask/unmask, immutable `sch_irqchip`, and `sch_gpio_gpe_handler()`.

## Control Flow
Probe maps an IORESOURCE_IO range, copies the template gpio chip, selects GPIO count and resume-bank split from `pdev->id`, performs model-specific enable writes, configures a GPIO IRQ chip without a direct parent handler, installs an ACPI GPE handler if possible, and registers the chip. The GPE handler reads core and resume status registers, merges them into logical pending bits, dispatches domain IRQs, and asks ACPICA to re-enable the GPE.

## State and Persistence
GPIO and IRQ configuration live in I/O registers. The driver has no explicit suspend/resume hooks. GPE installation is devm-managed and removed by disabling/removing the ACPI handler.

## Dependencies and Integration Points
It uses platform devices identified by Intel PCI IDs, ACPI GPE APIs, I/O port mapping, gpiolib IRQ domains, and immutable irqchip helpers. IRQ delivery depends on ACPI GPE0E GPIO bit 14.

## Risks
If ACPI GPE setup fails, the driver still registers GPIOs but warns that IRQ support is unavailable. Direction-output cannot preset the output value before switching direction because hardware makes GLV read-only for inputs, so a short low pulse is documented. Logical-to-bank mapping depends on correct `resume_base` per device ID.

## Test Signals
Test all supported `pdev->id` variants, core/resume bank offset mapping, model-specific enable writes, direction-output pulse-sensitive consumers, edge rising/falling/both programming, GPE failure fallback, and pending status dispatch across both banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sch311x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sch311x.c

## Purpose
This driver detects SMSC SCH3112/SCH3114/SCH3116 Super-I/O chips, creates a platform device for the runtime register base, and registers six eight-line GPIO blocks with per-line configuration registers.

## Important APIs, Types, and Functions
Detection uses `sch311x_sio_enter/exit/inb/outb()` to access Super-I/O config space at known ports. `struct sch311x_gpio_block_def` describes each block's data register, per-line config registers, and static GPIO base. `struct sch311x_gpio_block` contains the gpio chip, register addresses, runtime base, and lock. GPIO callbacks implement request/free, get/set, direction, direction query, and open-drain/push-pull config.

## Control Flow
Module init scans four Super-I/O config ports, enters config mode, checks device ID, selects logical device 0x0a, reads the runtime base, registers the platform driver, then adds a platform device. Probe reserves the contiguous GP1-GP6 data registers, allocates private state, and registers six gpio chips. Per-line request reserves its config byte and rejects unavailable lines with zero config register entries.

## State and Persistence
GPIO direction, value, and open-drain state live in Super-I/O runtime registers. The driver stores static register tables and no PM state. Platform device lifetime is managed manually at module init/exit.

## Dependencies and Integration Points
It depends on x86 I/O port APIs, Super-I/O config conventions, platform devices with private data, gpiolib, pinconf config parameters for drive mode, and static GPIO bases 10/20/30/40/50/60.

## Risks
Static base numbering and six separate chips reflect older userspace expectations but can conflict with dynamic allocation assumptions. Missing config-register entries are only rejected in `.request()`, so direct internal use before request would be unsafe. The init path must unregister the platform driver if platform device creation fails. There is no IRQ support.

## Test Signals
Test detection for all three device IDs, inactive logical-device warning, runtime-base absence, unavailable GPIO request rejection, per-block data register reservation, direction get/set, open-drain and push-pull config, and module exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sch311x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-shared-proxy.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-shared-proxy.c

## Purpose
This auxiliary-bus driver presents a shared physical GPIO descriptor as a one-line proxy gpio chip. Multiple users can vote for a high output while the proxy keeps the effective line high until the last high vote is released.

## Important APIs, Types, and Functions
`struct gpio_shared_proxy_data` stores the one-line gpio chip, shared descriptor, device, and this proxy's `voted_high` state. It relies on `struct gpio_shared_desc` and lock helpers from `gpiolib-shared.h`, including shared `usecnt`, `highcnt`, `cfg`, `can_sleep`, and underlying `desc`. The core voting logic is `gpio_shared_proxy_set_unlocked()`.

## Control Flow
Probe obtains a shared descriptor with `devm_gpiod_shared_get()`, creates a one-line gpio chip, chooses sleep-capable or atomic get/set callbacks based on the underlying descriptor, and registers it. Requests/free update shared use count. Direction changes are allowed freely for a single user, but multiple users cannot change an already-output line to input or an already-input line to output. Output set/direction-output use vote accounting so high is shared OR semantics and low removes this proxy's vote.

## State and Persistence
State persists in the underlying GPIO descriptor plus shared descriptor counters protected by a shared lock. This proxy stores whether it currently contributed a high vote. There is no PM state.

## Dependencies and Integration Points
It integrates with the auxiliary bus name `gpiolib_shared.proxy`, GPIO consumer APIs, gpiolib provider APIs, IRQ conversion through `gpiod_to_irq()`, and shared GPIO internals.

## Risks
Configuration changes with multiple users are accepted even when different from existing config, with only debug logging, so users can conflict electrically. Vote accounting assumes request/free and set paths are balanced and serialized by the shared descriptor lock. Direction semantics are intentionally conservative when multiple users exist and may return `-EPERM` for consumers expecting normal GPIO ownership.

## Test Signals
Test single-user direction/value pass-through, multi-user high vote aggregation, repeated high/low votes by the same proxy, final low transition when `highcnt` reaches zero, conflicting direction attempts, set_config conflicts, can-sleep callback selection, and IRQ passthrough.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-shared-proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sifive.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sifive.c

## Purpose
This driver exposes SiFive GPIO controllers using generic GPIO MMIO helpers and hierarchical IRQ domains. Each GPIO line may have a distinct parent IRQ, and the driver programs SiFive rise/fall/high/low interrupt-enable and pending registers through regmap.

## Important APIs, Types, and Functions
`struct sifive_gpio` stores MMIO base, `gpio_generic_chip`, regmap, per-line IRQ enable state, trigger type, and parent Linux IRQ numbers. `sifive_gpio_set_ie()` maps software trigger/enable state to four interrupt-enable registers. IRQ operations include type, enable/disable, EOI, affinity, parent mask/unmask, wake passthrough, and child-to-parent hwirq translation.

## Control Flow
Probe maps MMIO, creates a no-lock regmap, collects optional IRQs until the first missing one, derives the parent IRQ domain from the first IRQ, initializes the generic GPIO chip, disables all GPIO interrupt enables, fills gpio chip metadata, configures hierarchical `gpio_irq_chip`, and registers the chip. IRQ enable forces the line to input, clears all sticky pending bits, marks the line enabled in `irq_state`, and programs IE bits.

## State and Persistence
`trigger[]` and `irq_state` are the software source of truth for IE programming. Pending bits are cleared on enable and EOI. GPIO direction/value state lives in hardware. There is no suspend/resume handling.

## Dependencies and Integration Points
The driver uses platform IRQ arrays, regmap over MMIO, `gpio_generic_chip`, hierarchical irqchip parent operations, firmware nodes, and generic GPIO locking guards. It assumes all parent IRQs share one parent domain.

## Risks
At least one IRQ is mandatory, so GPIO-only use without interrupts fails probe. Parent IRQ collection stops at the first missing IRQ and sets `ngpio` to the number found, tying GPIO count to IRQ count. `sifive_gpio_irq_set_type()` stores any trigger bits without rejecting unsupported combinations. Regmap locking is disabled because the generic chip lock is expected to serialize updates.

## Test Signals
Test parent IRQ enumeration, GPIO count equal to parent IRQ count, all trigger combinations, enable clears pending registers and switches to input, hierarchical IRQ mapping, affinity/wake propagation, and failure with zero IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sifive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sim.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sim.c

## Purpose
`gpio-sim.c` is a GPIO simulator for testing. It exposes a configfs hierarchy for defining simulated devices, banks, lines, and GPIO hogs, then instantiates platform devices backed by software nodes. The platform side registers simulated gpio chips with sysfs controls and an `irq_sim` domain.

## Important APIs, Types, and Functions
Runtime chip state is `struct gpio_sim_chip`: gpio chip, request/direction/value/pull bitmaps, irq simulation domain, mutex, and per-line sysfs attribute groups. Configfs state is represented by `gpio_sim_device`, `gpio_sim_bank`, `gpio_sim_line`, and `gpio_sim_hog`. Important functions include GPIO callbacks, `gpio_sim_apply_pull()`, `gpio_sim_add_bank()`, software-node construction helpers, configfs live activation/deactivation, and configfs item/group operations.

## Control Flow
Module init registers the platform driver and the `gpio-sim` configfs subsystem. Users create configfs device groups, bank groups, optional line groups, and hog items, then write `live=1`. Activation validates that banks exist and labels are unique, creates a root software node, creates bank software nodes with `ngpios`, line names, and reserved ranges, adds hog child nodes, registers a `gpio-sim` platform device, waits for binding, and freezes dependent configfs items. Platform probe iterates child software nodes and creates a chip per bank.

## State and Persistence
Simulated line state is held in bitmaps. `direction_map` defaults to input, `value_map` changes through GPIO set and pull simulation, `pull_map` records pull-up/down, and `request_map` tracks active consumers. Configfs objects persist until removed; live platform devices hold software nodes and gpio chips until deactivated or released. Sysfs per-line `pull` writes can synthesize edge IRQs by setting irqchip pending state when an input value changes.

## Dependencies and Integration Points
The simulator depends on configfs, platform devices, software nodes/property entries, gpiolib provider and consumer semantics, gpio hog parsing, sysfs, `irq_sim`, IDA allocation, and debugfs when enabled.

## Risks
Configfs lifetime is complex: parent pointers are stored explicitly because configfs clears parent fields before release. Activation must unwind software nodes and platform devices correctly on partial failure. Pull changes only synthesize edge interrupts when the line is requested and configured as input. `valid` can be changed while live, but reserved ranges are built only during activation. Duplicate labels are rejected to avoid hogging ambiguity.

## Test Signals
Test configfs creation/removal for devices, banks, lines, and hogs; activation/deactivation; duplicate-label rejection; software-node properties for line names and reserved ranges; sysfs value/pull attributes; pull-triggered rising/falling IRQs; request/free effects; bitmap get/set multiple operations; invalid line counts above 1024; and cleanup on probe or activation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-siox.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-siox.c

## Purpose
This SIOX GPIO driver exposes a 20-line GPIO device over a SIOX cyclic I/O device: 12 input lines from received data and 8 output lines staged for the next SIOX transfer cycle. It also synthesizes nested interrupts from input level changes.

## Important APIs, Types, and Functions
`struct gpio_siox_ddata` contains the gpio chip, mutex-protected set/get data buffers, IRQ spinlock, enable/status masks, and per-input IRQ types. SIOX callbacks `gpio_siox_set_data()` and `gpio_siox_get_data()` exchange data with the bus. Gpiolib callbacks enforce fixed input/output line ranges. IRQ callbacks manage software status/type/enable bits.

## Control Flow
Probe allocates state, initializes locks, fills a sleep-capable 20-line gpio chip, configures an immutable threaded IRQ chip, and registers it. During each SIOX receive cycle, `gpio_siox_get_data()` compares new 12-bit input data against previous data, sets software IRQ status for matching level/edge triggers, updates cached input bytes, and calls `handle_nested_irq()` for enabled triggered inputs after dropping the mutex.

## State and Persistence
Outputs are staged in `setdata[0]` and only become visible to hardware in the next `set_data` cycle. Inputs are cached in `getdata[3]`. IRQ status/type/enable state is purely software. No suspend/resume hooks are present.

## Dependencies and Integration Points
The driver integrates with the SIOX bus, gpiolib, nested threaded IRQ handling, and OF module matching through the SIOX device infrastructure.

## Risks
Output `set()` does not immediately drive hardware; consumers must tolerate cycle latency. IRQs exist only for the first 12 input lines; direction callbacks reject invalid ranges. `gpio_siox_irq_set_type()` accepts arbitrary type bit combinations without validation. There is careful lock ordering between mutex and raw spinlock in receive processing.

## Test Signals
Test fixed direction boundaries at line 12, delayed output staging, input cache updates, rising/falling/high/low trigger generation, mask/unmask behavior, nested IRQ handling, and SIOX cycle concurrency with GPIO get/set calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-siox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sl28cpld.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sl28cpld.c

## Purpose
This driver exposes Kontron SL28 CPLD GPIO, input-only, and output-only blocks through the generic `gpio-regmap` core. The full GPIO flavor can also expose an interrupt controller via regmap-irq.

## Important APIs, Types, and Functions
The compatible data maps to `enum sl28cpld_gpio_type` values `SL28CPLD_GPIO`, `SL28CPLD_GPI`, and `SL28CPLD_GPO`. `sl28cpld_gpio_irq_init()` builds a one-register `regmap_irq_chip` with status, unmask, and ack bases. Probe fills `struct gpio_regmap_config` with register bases derived from the child `reg` property.

## Control Flow
Probe validates a parent device, obtains match data, reads the child register base, obtains the parent's regmap, fills common config with eight GPIOs, then switches on type. Full GPIO sets input, output, and direction register bases and optionally initializes IRQs if `interrupt-controller` is present. GPO sets only output; GPI sets only input. Finally it calls `devm_gpio_regmap_register()`.

## State and Persistence
The driver keeps no runtime state beyond the managed regmap-gpio registration. GPIO and IRQ state live in CPLD registers and regmap-irq state.

## Dependencies and Integration Points
It depends on a parent MFD regmap, DT child `reg`, optional platform IRQ, `gpio-regmap`, `regmap_irq`, and Open Firmware compatibles for the three block types.

## Risks
A real direction register at offset zero requires `GPIO_REGMAP_ADDR()` so the generic core does not treat zero as absent; the driver handles this for full GPIO. Interrupt support is conditional on the firmware `interrupt-controller` property and requires a parent IRQ. GPI/GPO variants intentionally lack direction changes.

## Test Signals
Test all three compatibles, child `reg` parsing, missing parent regmap, full GPIO direction/value operations, input-only/output-only limitations, optional interrupt-controller path, regmap IRQ domain attachment, and shared IRQ/oneshot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sl28cpld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sloppy-logic-analyzer.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sloppy-logic-analyzer.c

## Purpose
This debug-oriented platform driver samples an array of GPIO inputs as a simple software logic analyzer. It exposes debugfs controls for sampling delay, buffer size, trigger pattern, capture start, metadata, and captured sample data.

## Important APIs, Types, and Functions
`struct gpio_la_poll_priv` stores the GPIO descriptor array, sample buffer blob, metadata blob, trigger data, measured acquisition delay, requested delay, and debugfs dentries. `gpio_la_get_array()` reads all probe GPIOs and treats fatal signals as interruption. `fops_capture_set()` performs the capture. Other debugfs handlers manage buffer size and trigger data.

## Control Flow
Late init creates the top-level debugfs directory and registers the platform driver. Probe allocates state, initializes the default 256 KiB buffer, obtains `probe` GPIO array as inputs, rejects sleep-capable lines and more than eight probes, reads `probe-names`, sets consumer names, builds metadata, and creates debugfs files. Writing nonzero to `capture` removes prior data, disables local IRQs and preemption, measures GPIO-read overhead, waits for trigger mask/value pairs, samples one byte per state into the buffer, then recreates the `sample_data` blob.

## State and Persistence
The sample buffer is vmalloc-backed and resized through debugfs. Trigger data is allocated from userspace writes and freed after capture. Captured data persists as a debugfs blob until the next capture/removal. There is no PM state.

## Dependencies and Integration Points
The driver depends on GPIO consumer arrays, debugfs, platform DT compatible `gpio-sloppy-logic-analyzer`, property `probe-names`, and non-sleeping GPIO providers. It uses `late_initcall()` to claim GPIOs early enough for non-strict pinctrl cases.

## Risks
Capture disables local IRQs and preemption for the full buffer duration, so large buffers or small delays can harm system latency. Sampling is explicitly non-deterministic and unsuitable for precise timing. Trigger writes accept raw byte pairs and replace prior trigger data without a lock. Buffer data stores only up to eight probes because each sample is one byte.

## Test Signals
Test non-sleeping GPIO enforcement, max-probe rejection, `probe-names` count validation, buffer resize and allocation failure, delay below acquisition returning `-ERANGE`, trigger matching, fatal signal interruption, sample blob recreation, and debugfs removal while serialized by `blob_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sloppy-logic-analyzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sodaville.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sodaville.c

## Purpose
This built-in PCI driver supports Intel Sodaville public GPIOs. It exposes 12 GPIOs through `gpio_generic_chip` and provides level interrupt support with a legacy IRQ domain and generic irqchip.

## Important APIs, Types, and Functions
`struct sdv_gpio_chip_data` stores the MMIO base, legacy IRQ base, IRQ domain, generic IRQ chip, and generic GPIO chip. `sdv_gpio_pub_set_type()` programs level high/low in GPIT registers. `sdv_gpio_pub_irq_handler()` masks status with interrupt-enable bits and dispatches domain IRQs. `sdv_register_irqsupport()` allocates descriptors, requests the shared PCI IRQ, initializes a generic irqchip, and creates the legacy domain.

## Control Flow
PCI probe enables the device, maps BAR0, optionally writes `intel,muxctl`, initializes the generic chip with input, output, and output-enable registers, registers the gpio chip, then registers IRQ support. IRQ setup masks and acknowledges all sources, requests the PCI IRQ, configures fast-EOI handling with mask/eoi registers, and maps 12 legacy IRQs.

## State and Persistence
GPIO state is hardware-backed. IRQ controller state is held in generic irqchip mask cache and hardware registers. There is no suspend/resume handling in this file.

## Dependencies and Integration Points
The driver is a built-in PCI driver for Intel device ID `0x2e67`, uses managed PCI resource mapping, gpiolib generic helpers, OF property parsing on PCI device nodes, and irqdomain/generic-chip APIs.

## Risks
Only level-high and level-low IRQs are supported. The hardware latches level IRQs, so the comment notes that unmask/ACK ordering matters; fast-EOI handling is chosen accordingly. GPIO registration occurs before IRQ support; if IRQ setup fails, probe fails and managed cleanup unwinds. Legacy IRQ domains and descriptor allocation are older patterns.

## Test Signals
Test PCI enable/BAR mapping, optional mux control write, GPIO direction/value operations, level-high/low type setup for lines below/above 8, IRQ status masking, EOI behavior while level remains active, and failure paths in descriptor allocation/request_irq/domain creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sodaville.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-spacemit-k1.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-spacemit-k1.c

## Purpose
This driver supports SpacemiT K1/K3 GPIO controllers with four 32-line banks. It uses generic GPIO MMIO helpers for data/direction and custom nested IRQ handling for edge-detect interrupts.

## Important APIs, Types, and Functions
`struct spacemit_gpio_data` describes per-SoC register offsets and bank offsets. `struct spacemit_gpio_bank` contains a generic GPIO chip, parent controller pointer, bank base, and software IRQ masks for enabled/rising/falling edges. `spacemit_gpio_add_bank()` initializes one bank. IRQ callbacks include handler, ack, mask/unmask, set_type, and print_chip.

## Control Flow
Probe selects match data, maps the shared register resource, gets the shared parent IRQ, enables core and bus clocks, and registers four banks. Each bank initializes a `gpio_generic_chip` with data/set/clear/direction registers, configures a threaded simple IRQ chip, resets interrupt mask and edge-detect registers, requests the shared threaded parent IRQ, registers the gpio chip, and marks the IRQ domain as wired for three-cell selection.

## State and Persistence
GPIO values/directions live in hardware. IRQ enable and selected edge types are shadowed in `irq_mask`, `irq_rising_edge`, and `irq_falling_edge`; mask/unmask materializes those shadows into GAPMASK and edge set/clear registers. There are no PM callbacks.

## Dependencies and Integration Points
The driver uses platform DT compatibles, two clocks named `core` and `bus`, one shared IRQ, gpiolib generic helpers, GPIO OF three-cell matching through `of_node_instance_match`, nested threaded IRQ handling, and seq_file chip printing.

## Risks
All four banks request the same shared IRQ and clear per-bank status; incorrect bank offsets would cause cross-bank interference. `irq_set_type()` accepts any type bits and only considers rising/falling, so level types effectively disable both edge masks without returning `-EINVAL`. The K1 bank offsets are nonuniform, making table correctness critical.

## Test Signals
Test K1 and K3 offset tables, four-bank registration, shared IRQ dispatch to the correct bank/domain, rising/falling/both edge enable and mask interactions, invalid or level trigger behavior, three-cell OF GPIO selection, clock failure paths, and boundary lines around each 32-line bank.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-spacemit-k1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-spear-spics.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-spear-spics.c

## Purpose
This driver presents SPEAr SoC PL022 SPI chip-select control bits as a four-line GPIO controller. It lets SPI chip selects be controlled through system registers outside the SPI controller's own MMIO space.

## Important APIs, Types, and Functions
`struct spear_spics` holds the system-register base, DT-provided register/bit fields, use count, cached last selected chip-select offset, and gpio chip. `spics_set_value()` selects a chip-select index and writes its value bit. `spics_request()` enables software control on the first user; `spics_free()` disables software control after the last user.

## Control Flow
Probe maps the system register resource, reads required DT properties for the peripheral config register and bit fields, fills a four-line output-only gpio chip, and registers it. Consumers request a line, which enables software control and defaults the chip-select value high. Direction output and set both call `spics_set_value()`.

## State and Persistence
Hardware state lives in the peripheral configuration register. Software state is limited to `use_count` and `last_off`, used to avoid rewriting selection fields when the same chip select is toggled repeatedly. There is no locking and no PM handling.

## Dependencies and Integration Points
The driver depends on platform DT properties with `st-spics,*` names, MMIO system registers, gpiolib, and early `subsys_initcall()` registration so chip-select GPIOs are available to SPI controllers.

## Risks
`use_count` and register updates are not locked, so concurrent users can race. Only output semantics are implemented; there is no get or direction_input. Shared hardware appears to select one chip-select at a time, so simultaneous use of multiple lines depends on SPI core serialization. Missing DT properties fail probe.

## Test Signals
Test DT property validation, first request enabling software control, last free disabling it, selection field updates when switching offsets, value bit high/low toggling, repeated set on same offset, and concurrent SPI chip-select consumers if applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-spear-spics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sprd.c

## Purpose
This driver supports Spreadtrum GPIO controllers with 16 banks of 16 lines for 256 total GPIOs. It provides GPIO request/direction/value operations and chained parent IRQ demultiplexing.

## Important APIs, Types, and Functions
`struct sprd_gpio` stores the gpio chip, MMIO base, raw spinlock, and parent IRQ. `sprd_gpio_bank_base()` maps a bank number to its register block. `sprd_gpio_update()` performs locked per-bit updates. GPIO callbacks use DMSK, DIR, INEN, and DATA registers. IRQ callbacks manage IE, IC, IS, IBE, and IEV registers and dispatch from MIS.

## Control Flow
Probe obtains the parent IRQ, maps the resource, initializes the lock, fills a 256-line gpio chip, configures a one-parent `gpio_irq_chip`, and registers it. GPIO request sets DMSK and free clears it. Input clears DIR and enables input; output sets DIR, disables input, and writes DATA. The chained IRQ handler scans every bank's masked interrupt status and dispatches set bits.

## State and Persistence
GPIO and IRQ state live in hardware registers. The driver keeps no software trigger shadow and has no suspend/resume hooks.

## Dependencies and Integration Points
It uses platform DT compatible `sprd,sc9860-gpio`, gpiolib, chained IRQ handling, raw spinlocks, and immutable irqchip resource helpers.

## Risks
`sprd_gpio_get()` reads DATA for both input and output; correctness depends on hardware DATA reflecting input state. Direction output programs direction before data, which may produce a transient output level. The handler scans all 16 banks on every interrupt. Wake is skipped by irqchip flags.

## Test Signals
Test all trigger modes, request/free DMSK behavior, direction input/output and INEN transitions, bank boundary offsets, chained IRQ dispatch across all 16 banks, interrupt clear on edge types, and bad parent IRQ/resource paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-stmpe.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-stmpe.c

## Purpose
This MFD child driver exposes STMPE GPIO expander blocks as gpiolib chips with optional threaded IRQ support. It handles multiple STMPE variants with different register maps, interrupt capabilities, and GPIO counts up to 24.

## Important APIs, Types, and Functions
`struct stmpe_gpio` stores the gpio chip, parent `struct stmpe`, IRQ mutex, no-request mask, and cached interrupt control registers (`regs` and `oldregs`) for rising, falling, and enable bits. GPIO callbacks read/write STMPE registers, set directions, and request GPIO alternate function ownership. IRQ callbacks implement bus lock/sync unlock, mask/unmask, type selection, and threaded IRQ demux. Debugfs output is provided by `stmpe_dbg_show()`.

## Control Flow
Probe obtains the parent STMPE object, validates GPIO count, initializes state, copies the template chip, reads optional `st,norequest-mask`, enables the GPIO block through the MFD core, optionally requests a threaded parent IRQ, configures a threaded gpio IRQ chip with valid-mask filtering, and registers the gpio chip. IRQ type/mask changes update cached arrays under `irq_lock`; `irq_bus_sync_unlock()` writes only changed registers to the bus. The threaded IRQ handler block-reads status banks, masks by cached IE bits, handles nested child IRQs, and clears status/edge-detect registers on variants where writes clear them.

## State and Persistence
GPIO state is in the STMPE device. Interrupt control state is cached in software until sync unlock to reduce bus writes and maintain atomic-looking irqchip operations over slow buses. `norequest_mask` prevents unavailable pins from GPIO and IRQ use. Managed cleanup disables the GPIO block on detach.

## Dependencies and Integration Points
The driver depends on the STMPE MFD core register map/index table, platform child devices, gpiolib, threaded IRQs, pinctrl-like STMPE alternate-function control, firmware properties, and debugfs when enabled.

## Risks
Variant differences are substantial: STMPE801 and STMPE1600 lack rising/falling-edge registers, STMPE1600 requires GPMR reads to get pin IRQs, and status register order differs by variant. The valid-mask loop checks `sizeof(u32)` iterations rather than `ngpios`, which effectively covers 32 bits but is visually easy to misread. IRQ cache correctness depends on bus lock/unlock pairing.

## Test Signals
Test each supported STMPE variant's register order and IRQ feature set, no-request mask enforcement for GPIO and IRQ, set/clear variants with shared or separate registers, bus-sync cache writes, threaded IRQ status dispatch and clear behavior, debugfs output, GPIO block enable/disable cleanup, and parent IRQ absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-stmpe.c -->
