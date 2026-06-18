# subset-b-001302 research

Grouped research for Linux GPIO drivers and helper libraries under the ceph-client source tree. Each source section preserves the source path in its title and is delimited for deterministic splitting into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-hisi.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-hisi.c

## Purpose
`gpio-hisi.c` registers a HiSilicon/Ascend GPIO controller as a gpiolib chip backed by a memory-mapped register bank. It uses the generic GPIO helper for data, set, clear, and direction operations, then layers debounce and optional cascaded interrupt support on top.

## Important APIs, types, and functions
The main state is `struct hisi_gpio`, which embeds `struct gpio_generic_chip`, the MMIO base, `line_num`, and one parent IRQ. `hisi_gpio_read_reg()`/`hisi_gpio_write_reg()` are the low-level MMIO helpers. `hisi_gpio_set_config()` supports `PIN_CONFIG_INPUT_DEBOUNCE`. IRQ operations are `hisi_gpio_set_ack()`, mask/unmask, type selection, enable/disable, and `hisi_gpio_irq_handler()`. Probe uses `gpio_generic_chip_init()` and `devm_gpiochip_add_data()`.

## Control flow
Probe requires exactly one firmware child node, maps resource 0, reads the child `ngpios`, fetches the matching platform IRQ, initializes a generic chip using the controller's set/clear direction registers, sets dynamic base and line count, installs an irqchip when an IRQ is present, and registers the chip. The chained parent handler reads `INTSTATUS`, iterates active bits, and dispatches child IRQs through the GPIO IRQ domain.

## State and persistence behavior
Driver state is runtime-only and device-managed. Hardware holds output level, direction, debounce, interrupt mask, enable, polarity, type, and dual-edge bits. No software shadow is kept for normal GPIO levels. Firmware `ngpios` bounds the exported lines; the code clamps anything above 32.

## Dependencies and integration points
This integrates with ACPI `HISI0184`, OF compatible `hisilicon,ascend910-gpio`, `gpio-generic`, gpiolib irqchip helpers, chained IRQ handling, and pinconf debounce users. It depends on firmware child nodes for port metadata.

## Risks and edge cases
The probe rejects anything other than one port, so firmware describing multiple ports will fail. Dual-edge configuration has priority over other type registers and must be explicitly cleared when changing to non-both-edge types. `platform_get_irq()` returning 0 or negative disables or skips IRQ setup depending on value, so firmware IRQ numbering bugs can silently remove interrupt support.

## Test signals
Useful signals are probe on ACPI and DT systems, libgpiod line get/set/direction tests, debounce pinconf tests, IRQ type tests for all supported trigger modes including edge-both reconfiguration, and interrupt storm tests verifying EOI/mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-hisi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-hlwd.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-hlwd.c

## Purpose
`gpio-hlwd.c` exposes Nintendo Wii Hollywood GPIO lines through gpiolib. It claims the hardware lines for Broadway CPU access, uses the always-accessible `HW_GPIOB_*` register window, and optionally presents the block as an interrupt controller.

## Important APIs, types, and functions
`struct hlwd_gpio` embeds a `gpio_generic_chip`, the big-endian MMIO base, parent IRQ, and software bitmaps for edge emulation. `hlwd_gpio_irqhandler()` handles cascaded interrupts. IRQ helpers provide ack, mask, unmask, enable, type selection, chip printing, and `hlwd_gpio_irq_setup_emulation()` for edge triggers. Probe is centered around `gpio_generic_chip_init()`.

## Control flow
Probe maps registers, writes all ones to `HW_GPIO_OWNER` before generic initialization, initializes the generic chip with big-endian register access, reads optional `ngpios`, masks and acknowledges all interrupts, and, if the node has `interrupt-controller`, wires a parent IRQ into the gpiochip irqchip. The parent handler reads pending and mask registers under the generic chip lock, emulates edge triggers by toggling inactive levels, acknowledges emulated edges, then dispatches selected child IRQs.

## State and persistence behavior
The hardware stores output, direction, interrupt mask, flags, level sense, and ownership. The driver stores only interrupt emulation state: `edge_emulation`, `rising_edge`, and `falling_edge`. Device-managed allocations cover lifetime; no persistent storage exists across driver unload or reboot.

## Dependencies and integration points
The driver binds to `nintendo,hollywood-gpio`, depends on MMIO big-endian accessors and `gpio-generic`, and integrates with DT `interrupt-controller` bindings. It relies on the Hollywood memory firewall allowing access to owner and GPIO registers.

## Risks and edge cases
Edge interrupts are emulated by changing level polarity, which is sensitive to races with changing input levels. Systems without AHBPROT/firewall access cannot safely claim ownership. The handler reads and modifies interrupt registers while holding the generic chip lock, so incorrect locking could cause lost edge-emulation transitions.

## Test signals
Use libgpiod for get/set/direction, boot tests with and without `interrupt-controller`, level-high/low and rising/falling/both-edge IRQ tests, and platform tests confirming all lines are owned by `HW_GPIOB_*` before generic state is read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-hlwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-htc-egpio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-htc-egpio.c

## Purpose
`gpio-htc-egpio.c` supports legacy HTC phone CPLD GPIO/IRQ expanders described by platform data. It can register several gpiochips over one MMIO region, manage fixed input/output line capabilities, cache output values, and demultiplex a shared parent IRQ.

## Important APIs, types, and functions
`struct egpio_info` holds the shared spinlock, MMIO layout, IRQ bookkeeping, and flexible array of `struct egpio_chip`. `egpio_get()`, `egpio_set()`, direction helpers, `egpio_get_direction()`, and `egpio_write_cache()` implement GPIO behavior. IRQ flow uses `egpio_handler()`, `ack_irqs()`, `egpio_mask()`, and `egpio_unmask()`. PM hooks are `egpio_suspend()` and `egpio_resume()`.

## Control flow
The early `subsys_initcall` registers a platform driver with `platform_driver_probe()`. Probe consumes `struct htc_egpio_platform_data`, maps the memory resource, computes bus/register shifts from platform widths, creates one gpiochip per declared chip, writes cached initial output values, then optionally maps a contiguous legacy IRQ range to a chained parent IRQ. Resume rewrites cached output values after possible CPLD power loss.

## State and persistence behavior
Output state is shadowed in each `egpio_chip.cached_values`; `is_out` marks output-capable lines. IRQ enable state is software-only in `irqs_enabled` because the CPLD cannot proactively mask individual child IRQs. Runtime state persists across suspend in RAM and is reapplied to hardware on resume.

## Dependencies and integration points
This driver depends on board platform data from `linux/platform_data/gpio-htc-egpio.h`, legacy fixed IRQ bases, raw MMIO `readw()`/`writew()`, and chained IRQ APIs. It predates DT/ACPI and managed gpiochip removal patterns.

## Risks and edge cases
The probe path calls `gpiochip_add_data()` without checking its return value inside the loop, so partial registration failures can be hard to detect. Child IRQ masking only filters in software after interrupts arrive. The driver assumes valid platform data; missing `dev_get_platdata()` would dereference null.

## Test signals
Test with HTC board platform data, verify output cache writes on probe and resume, fixed input/output direction errors, chained IRQ demux and software mask filtering, wake enable/disable during suspend, and cleanup behavior under gpiochip registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-htc-egpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.c

## Purpose
`gpio-i8255.c` is a reusable gpio-regmap library for Intel 8255 Programmable Peripheral Interface chips. It registers one or more 24-line PPIs as one gpiochip and translates gpiolib offsets into port and control-register masks.

## Important APIs, types, and functions
The exported API is `devm_i8255_regmap_register()`. Helpers include `i8255_ppi_init()` to set mode 0 and initialize outputs, `i8255_direction_mask()` to map lines to control bits, and `i8255_reg_mask_xlate()` for gpio-regmap register/mask translation.

## Control flow
Callers provide an `i8255_regmap_config` with parent device, regmap, PPI count, optional names, and optional IRQ domain. Registration validates required fields, initializes each PPI at `i * 4`, fills a `gpio_regmap_config`, and calls `devm_gpio_regmap_register()`.

## State and persistence behavior
State is primarily in the regmap cache and hardware control ports. Initialization configures all ports as mode 0 outputs and sets data ports to zero. Direction is represented by cached control-register bits, which is why the header requires the control registers not be marked volatile.

## Dependencies and integration points
This file exports symbol namespace `I8255` and depends on `gpio-regmap` and a caller-supplied regmap implementation. It can attach an IRQ domain supplied by a wrapper driver.

## Risks and edge cases
The 8255 Port C direction is nibble-granular, so requesting a single Port C line direction effectively affects four lines. Marking control registers volatile breaks direction tracking. Initialization forces outputs low, which can be unsafe for boards that need bootloader-preserved states.

## Test signals
Wrapper-driver tests should verify PPI count validation, all three ports per PPI, Port C upper/lower nibble direction behavior, regmap cache direction reads, optional IRQ-domain mapping, and reset-time output-low effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.h

## Purpose
`gpio-i8255.h` defines the public configuration contract for the shared 8255 gpio-regmap helper in `gpio-i8255.c`.

## Important APIs, types, and functions
It declares `struct i8255_regmap_config`, `devm_i8255_regmap_register()`, and the helper macro `i8255_volatile_regmap_range(_base)` for data-port volatile ranges.

## Control flow
Consumers include this header, create a regmap with appropriate volatile/cache policy, populate the config, and call the devm registration helper during probe.

## State and persistence behavior
The header documents that the regmap must have cache enabled and that control registers must not be volatile. That is a persistence contract for software direction state rather than durable storage.

## Dependencies and integration points
The header forward-declares `struct device`, `struct irq_domain`, and `struct regmap`, keeping dependencies light for wrapper drivers. It integrates with regmap and gpio-regmap users that need one-to-many 8255 wrappers.

## Risks and edge cases
Misdeclaring volatile ranges or omitting cache support can make GPIO direction reporting and modification incorrect. `num_ppi` is an `int`, so callers should keep values sane and positive before registration.

## Test signals
Compile tests for consumers, namespace import checks for `I8255`, regmap-cache behavior tests, and wrapper probe tests that pass invalid parent/map/num_ppi values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ich.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ich.c

## Purpose
`gpio-ich.c` exposes GPIO lines in Intel ICH6-10, Series 5/6, Atom C2000, Avoton/Rangeley, and related LPC bridges. It operates on legacy I/O-port resources provided by the LPC ICH MFD layer and handles chipset-specific register layouts and quirks.

## Important APIs, types, and functions
`struct ichx_desc` describes per-chip register offsets, line count, blink support, GPE0 usage, ignored `USE_SEL` bits, and optional request/get overrides. Global `ichx_priv` stores the single active instance. Core helpers are `ichx_write_bit()`, `ichx_read_bit()`, direction/get/set/request functions, `ichx_gpio_request_regions()`, and `ichx_gpio_probe()`.

## Control flow
Probe selects a descriptor from `lpc_ich_info->gpio_version`, requests the usable I/O register regions, optionally requests the PM/GPE0 I/O region, configures a gpiochip, and registers it. Reads and writes compute register group and bit from absolute GPIO offset. ICH6/3100 variants special-case GPIO 0-15 through PM GPE0 status and GPIO 16/17 through alternate `USE_SEL` bits.

## State and persistence behavior
Most state is hardware register state. Avoton uses `outlvl_cache[]` because its output levels cannot be read reliably from `GPIO_LVL`; cached bits are ORed with read hardware values and updated on writes. The global private object means one system-wide instance, not multiple independent devices.

## Dependencies and integration points
The driver is a platform child of `lpc_ich`, consumes `struct lpc_ich_info`, uses `inl()`/`outl()` I/O-port access, and exposes a gpiolib chip with optional module parameter `gpiobase`.

## Risks and edge cases
Global state prevents multiple concurrent ICH GPIO instances. Direction and request operations rely on BIOS `USE_SEL` setup except for known ignored bits. Many pins are input-only or output-only, so write-then-verify can return `-EPERM`. Avoton cache can diverge if firmware or another agent modifies output levels.

## Test signals
Test descriptor selection for each `gpio_version`, region conflicts, ICH6 GPE0 reads, fixed-base and dynamic-base registration, input-only/output-only verification failures, Avoton cached output behavior, and blink-disable on GPIO 0-31 outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ich.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.c

## Purpose
`gpio-idio-16.c` is a reusable gpio-regmap and regmap-irq library for ACCES IDIO-16 family devices. It maps 16 fixed outputs and 16 isolated inputs into a 32-line gpiochip and wires input interrupts through regmap-irq.

## Important APIs, types, and functions
The exported API is `devm_idio_16_regmap_register()`. `struct idio_16_data` stores the regmap and last IRQ mask. `idio_16_handle_mask_sync()` toggles device-level IRQ enable when all child IRQs are masked or unmasked. `idio_16_reg_mask_xlate()` maps offsets to output or input register banks. `idio_16_names` defines stable line names.

## Control flow
Registration validates parent, map, and IRQ descriptors, disables device IRQs, installs a regmap IRQ chip, optionally deactivates input filters, configures gpio-regmap data/set bases and fixed output bitmap for GPIO 0-15, and registers the chip.

## State and persistence behavior
Line state is in device registers and regmap cache. The only software state is `irq_mask`, used to avoid redundant enable/disable transitions. Outputs are fixed-direction; inputs are fixed-direction and interrupt-capable.

## Dependencies and integration points
The helper exports namespace `GPIO_IDIO_16`, depends on regmap, regmap-irq, and gpio-regmap, and is intended for bus-specific IDIO-16 wrapper drivers.

## Risks and edge cases
The whole device IRQ is enabled only when transitioning away from all-masked and disabled when returning to all-masked; incorrect regmap-irq defaults can leave interrupts stuck. Devices without status registers use the `no_status` flag, shifting responsibility to regmap-irq semantics.

## Test signals
Wrapper tests should cover fixed output/input direction, interrupt masking transitions, filter deactivation, no-status variants, line names, and regmap register/mask translation for all 32 offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.h

## Purpose
`gpio-idio-16.h` defines the public configuration structure for the ACCES IDIO-16 gpio-regmap helper.

## Important APIs, types, and functions
It declares `struct idio_16_regmap_config` with parent, regmap, regmap IRQ descriptors, IRQ line, no-status flag, and filter flag, plus `devm_idio_16_regmap_register()`.

## Control flow
Bus-specific drivers include this header, build the regmap and regmap IRQ table, set flags for device variant behavior, and call the devm helper in probe.

## State and persistence behavior
The header itself has no state; its fields control how the C helper initializes hardware and represents IRQ state.

## Dependencies and integration points
Only forward declarations are used, keeping the interface suitable for ISA/PCI/USB wrapper drivers. It integrates with regmap and regmap-irq.

## Risks and edge cases
Supplying a mismatched IRQ table or wrong `no_status`/`filters` flags can make child IRQs unreliable. The helper requires `regmap_irqs`, so wrappers for non-interrupt-capable variants need a different path.

## Test signals
Compile tests for users, invalid config tests, and wrapper probe tests for status/no-status and filter/non-filter devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idt3243x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-idt3243x.c

## Purpose
`gpio-idt3243x.c` supports the GPIO block and optional interrupt controller on IDT/Renesas 79RC3243x SoCs. It uses gpio-generic for GPIO register access and a chained irqchip for level-triggered GPIO interrupts through the SoC PIC.

## Important APIs, types, and functions
`struct idt_gpio_ctrl` embeds `gpio_generic_chip`, stores PIC and GPIO MMIO bases, and caches the interrupt mask. GPIO setup uses `gpio_generic_chip_init()`. IRQ flow uses `idt_gpio_dispatch()`, `idt_gpio_irq_set_type()`, `idt_gpio_ack()`, `idt_gpio_mask()`, `idt_gpio_unmask()`, and `idt_gpio_irq_init_hw()`.

## Control flow
Probe maps the named `gpio` resource, initializes the generic chip, optionally applies firmware `ngpios`, and, when `interrupt-controller` is present, maps the named `pic` resource, gets a parent IRQ, initializes all interrupts masked, and installs a chained child domain. Dispatch reads PIC pending bits, removes masked bits, and forwards mapped GPIO IRQs.

## State and persistence behavior
GPIO direction and data live in hardware registers. `mask_cache` mirrors PIC mask state so dispatch can filter pending bits and mask/unmask can update registers atomically under the generic lock.

## Dependencies and integration points
The driver binds to `idt,32434-gpio`, depends on named platform resources `gpio` and optionally `pic`, gpiolib, gpio-generic, and chained IRQ support.

## Risks and edge cases
Hardware only supports level-triggered interrupts; edge requests fail. `idt_gpio_ack()` writes `~BIT(hwirq)` to `ISTAT`, which depends on the SoC's write-one/zero-clear semantics and is high risk if reused on variants. Optional IRQ support means DT property/resource mismatches can remove interrupt capability.

## Test signals
Test GPIO get/set/direction, `ngpios` override, level-high/low IRQ type setup, rejection of edge triggers, mask cache behavior, chained dispatch with masked pending bits, and resource-name failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idt3243x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-imx-scu.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-imx-scu.c

## Purpose
`gpio-imx-scu.c` exposes NXP i.MX SCU board resources as output-only GPIOs controlled through the System Controller Unit firmware API.

## Important APIs, types, and functions
`struct scu_gpio_priv` holds a gpiochip, mutex, device pointer, and SCU IPC handle. `scu_rsrc_arr` maps GPIO offsets to `IMX_SC_R_BOARD_R0..R7`. Operations are `imx_scu_gpio_get()`, `imx_scu_gpio_set()`, `imx_scu_gpio_get_direction()`, and `imx_scu_gpio_probe()`.

## Control flow
The driver registers at `subsys_initcall_sync` so board control lines are available early. Probe obtains the SCU handle, initializes a mutex, fills an eight-line dynamic-base gpiochip, and registers it. Get and set serialize calls to `imx_sc_misc_get_control()` and `imx_sc_misc_set_control()`.

## State and persistence behavior
State lives in SCU firmware and the hardware resources it controls. The kernel stores no output cache; get queries firmware every time. The driver always reports output direction and has no input-direction transition.

## Dependencies and integration points
It binds to `fsl,imx8qxp-sc-gpio`, depends on i.MX SCU RM/misc firmware APIs and DT resource constants, and integrates with consumers that need SCU-controlled board pins.

## Risks and edge cases
SCU IPC failures are returned directly and logged. The offset-to-resource map is fixed at eight entries, so firmware must not expose a different line count. Direction is hard-coded output even though `get()` can read current level.

## Test signals
Probe on i.MX8QXP SCU systems, get/set firmware success and error injection, concurrency under multiple consumers, and validation that all eight board resources map to expected physical pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-imx-scu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-it87.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-it87.c

## Purpose
`gpio-it87.c` exposes GPIO banks in ITE IT87xx Super I/O chips through legacy x86 I/O ports. It discovers the chip in Super I/O configuration mode, requests the runtime GPIO I/O window, and registers a dynamic gpiochip.

## Important APIs, types, and functions
`struct it87_gpio` stores the gpiochip, spinlock, runtime I/O base/size, output-enable register base, simple-I/O register base, and simple-I/O size. Low-level helpers enter/exit Super I/O config mode and read/write config registers. GPIO operations are `it87_gpio_request()`, get, direction input/output, and set. Module init/exit perform discovery and cleanup.

## Control flow
Module init reserves ports `0x2e/0x2f`, reads chip ID/revision, selects chip-specific register layout and line count, reads the GPIO base from logical device 7, requests the GPIO I/O region, allocates friendly line names, and registers the gpiochip. Request sets simple-I/O mode where available and defaults the line to input. Direction changes update Super I/O output-enable bits; values are read/written through the runtime GPIO I/O window.

## State and persistence behavior
Configuration persists in Super I/O registers until changed or reset. The driver does not shadow line values; it reads the I/O window. Allocated labels are kept through module lifetime and freed on exit.

## Dependencies and integration points
It uses legacy x86 port I/O, `request_muxed_region()` for Super I/O config access, `request_region()` for the GPIO window, and supports a fixed list of IT8613/8620/8628/8718/8728/8732/8761/8772/8786 IDs.

## Risks and edge cases
This is a singleton global module, not a platform driver. Unsupported chips fail hard. Some chips expose fewer physical lines than the convenient 64-line calculation, so unused exported lines may not behave as real pins. Direction changes require entering Super I/O mode and must be serialized.

## Test signals
Test chip discovery across supported IDs, region conflict handling, line naming, simple-I/O enable on supported chips, direction transitions, runtime I/O value get/set, and module unload freeing labels and regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-it87.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ixp4xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ixp4xx.c

## Purpose
`gpio-ixp4xx.c` implements the Intel IXP4xx SoC GPIO controller, including GPIO access, interrupt-parent translation, and optional clock-output muxing on GPIO14/15.

## Important APIs, types, and functions
`struct ixp4xx_gpio` embeds `gpio_generic_chip`, device/base pointers, and `irq_edge` state. IRQ functions are ack, mask, unmask, set_type, and `ixp4xx_gpio_child_to_parent_hwirq()`. Probe configures clock output bits, initializes gpio-generic, and sets hierarchical IRQ metadata.

## Control flow
Probe maps the MMIO resource, finds the parent IRQ domain, handles DT properties for GPIO14/15 clock outputs and board-specific forced GPIO mode, initializes a generic chip with endian flags based on CPU endianness, registers 16 GPIOs with fixed base 0, and wires a hierarchical irqchip. Type setup writes three-bit trigger style fields in GPIT1/GPIT2, acknowledges status, forces IRQ lines to input, and asks the parent for level-high handling.

## State and persistence behavior
Hardware stores output, direction, input, status, trigger style, debounce select, and clock mux state. `irq_edge` tracks which child IRQs are edge-triggered so unmask can avoid inappropriate level acknowledgements.

## Dependencies and integration points
The driver binds to `intel,ixp4xx-gpio`, depends on DT interrupt parents, gpio-generic, hierarchical irqdomains, and board compatibility strings for special clock mux behavior.

## Risks and edge cases
Only GPIO lines 0-12 map to dedicated parent IRQs; GPIO13-15 cannot become child IRQs. The fixed gpiochip base is a legacy ABI constraint. Endianness must match CPU mode because raw accessors and gpio-generic byte-order flags interact.

## Test signals
Test get/set/direction on big- and little-endian builds, IRQ mapping for lines 0-12 and rejection for 13-15, all trigger styles, GPIO14/15 clock-output DT properties, and board quirks forcing clock mux off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ixp4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-janz-ttl.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-janz-ttl.c

## Purpose
`gpio-janz-ttl.c` supports the Janz MODULbus VMOD-TTL module as a 20-line output-only GPIO controller.

## Important APIs, types, and functions
`struct ttl_module` stores the gpiochip, big-endian control register mapping, software shadows for ports A/B/C, and a spinlock. GPIO operations are `ttl_get_value()` and `ttl_set_value()`. Hardware setup is in `ttl_setup_device()` using `ttl_write_reg()`.

## Control flow
Probe requires `janz_platform_data`, maps module registers, resets the device, configures all ports open-drain outputs, drives zeroes, enables ports, initializes a dynamic gpiochip with get/set only, and registers it. Set operations update the relevant port shadow and write the full 16-bit port register.

## State and persistence behavior
The driver treats values as software shadow state; `get` returns the shadow instead of reading hardware. Shadows are initialized to zero during setup. Hardware state is reset on probe and not persisted across unload/reload.

## Dependencies and integration points
It is a platform child of the Janz MFD/MODULbus stack, depends on big-endian MMIO accessors, and uses platform data to confirm module context.

## Risks and edge cases
Inputs and direction changes are not supported even though the physical device is programmable. Returning cached values can hide hardware write failures or external changes. Probe resets all outputs low, which may be externally visible.

## Test signals
Test probe with and without platform data, initial hardware programming sequence, set/get shadow consistency, port A/B/C offset mapping, and behavior around module reset and all-zero output defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-janz-ttl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-kempld.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-kempld.c

## Purpose
`gpio-kempld.c` provides GPIO and optional interrupt support for Kontron PLD devices compatible with KEMPLD spec revision 2.0 or later.

## Important APIs, types, and functions
`struct kempld_gpio_data` stores the gpiochip, parent PLD pointer, selected output-level register, IRQ mutex, and cached IRQ enable/type registers. GPIO helpers include bit operations, get/set multiple, direction, and dynamic pin-count detection. IRQ helpers include mask/unmask, type setup, bus lock/sync, threaded parent handler, and `kempld_gpio_irq_init()`.

## Control flow
Probe validates PLD spec revision, chooses the output register based on spec version, sets platform or dynamic base, detects pin count by probing the event register, initializes optional IRQ support from BIOS-configured or module-overridden IRQ, then registers the gpiochip. IRQ bus sync writes cached edge/level, polarity, and enable registers; the threaded handler reads and clears status then handles nested child IRQs.

## State and persistence behavior
GPIO state lives in PLD registers. IRQ configuration is cached in `ien`, `evt_low_high`, and `evt_lvl_edge` and flushed during irq bus unlock. Pin count is inferred at probe and fixed for runtime.

## Dependencies and integration points
The driver depends on the KEMPLD MFD, its shared mutex helpers and register accessors, optional platform `gpio_base`, and optional module parameter `gpio_irq`.

## Risks and edge cases
Pin-count detection temporarily clears and restores the event register, which can disturb preconfigured events if locking or ordering is wrong. IRQ override can conflict with platform routing. Older PLD specs are rejected; missing IRQ configuration silently disables interrupt support.

## Test signals
Test pin-count detection, spec-version output-register selection, get/set multiple register batching, input/output direction, all four IRQ trigger types, BIOS IRQ and module override paths, and nested threaded IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-kempld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-latch.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-latch.c

## Purpose
`gpio-latch.c` implements a virtual output-only GPIO controller backed by latch hardware driven by GPIO consumers. It multiplexes a set of data GPIOs across one or more latch clock GPIOs.

## Important APIs, types, and functions
`struct gpio_latch_priv` stores the gpiochip, clock GPIO array, latched data GPIO array, timing properties, shadow bitmap, and either a mutex or spinlock. `gpio_latch_set_unlocked()` updates shadowed values, drives all data lines for a latch, delays, pulses the clock, and returns errors from underlying GPIO sets. Probe chooses sleeping or atomic callbacks based on `gpiod_cansleep()`.

## Control flow
Probe gets `clk-gpios` and `latched-gpios`, computes `ngpio = n_latches * n_latched_gpios`, allocates the shadow bitmap, chooses `set` or `set_can_sleep`, clamps optional nanosecond timing properties to 5000 ns, and registers an output-only gpiochip. Setting any virtual line rewrites the full data bus for its latch and pulses that latch's clock.

## State and persistence behavior
The driver maintains `shadow` as the authoritative value for all virtual latch outputs because readback is not available. The physical latch holds values until power loss or the next clock pulse. No input or IRQ state exists.

## Dependencies and integration points
It binds to `gpio-latch`, uses GPIO consumer arrays, gpiolib provider APIs, pinconf-independent timing properties, and can operate in sleeping or non-sleeping contexts depending on underlying GPIO controllers.

## Risks and edge cases
Every set operation rewrites all data inputs for that latch, so concurrent updates require correct locking. Timing above 5 us is truncated because the driver uses `ndelay()`. Underlying GPIO set errors can leave shadow state updated before all hardware lines are driven.

## Test signals
Test multiple latch and data widths, can-sleep and atomic GPIO providers, setup/clock timing clamps, repeated set operations preserving other shadow bits, and failure injection from underlying GPIO descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-latch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-line-mux.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-line-mux.c

## Purpose
`gpio-line-mux.c` creates an input-only virtual gpiochip where each virtual line selects a mux state and reads one shared physical GPIO.

## Important APIs, types, and functions
`struct gpio_lmux` embeds the gpiochip, a `mux_control`, the shared `muxed_gpio`, and the variable-length mux state table. `gpio_lmux_gpio_get()` selects the mux state with a 100 us delay, reads the raw GPIO value, and deselects the mux. Probe reads `gpio-line-mux-states`.

## Control flow
Probe counts `gpio-line-mux-states`, allocates enough storage for the state array, gets the mux controller and `muxed` GPIO input, reads the state array, initializes a can-sleep dynamic-base gpiochip, and registers it. Each get operation performs select/read/deselect serially through the mux framework.

## State and persistence behavior
The driver stores only the static state mapping. It does not cache input values and has no output state. Mux state is temporary and deselected after each read.

## Dependencies and integration points
It binds to `gpio-line-mux`, depends on the Linux mux consumer API and GPIO consumer API, and exposes firmware-node-backed virtual GPIO lines to other consumers.

## Risks and edge cases
If `gpiod_get_raw_value_cansleep()` fails or returns while mux deselect also fails, the deselect return value is ignored. Concurrent reads rely on mux framework serialization. Only input direction is supported.

## Test signals
Test invalid or empty mux-state property, mux select failure, raw input reads for each virtual offset, mux deselect calls, and consumers that require can-sleep GPIO access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-line-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ljca.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ljca.c

## Purpose
`gpio-ljca.c` exposes GPIO lines on Intel La Jolla Cove Adapter USB devices through the LJCA auxiliary bus. It provides GPIO get/set/direction, pin configuration, valid masks, and event-driven child IRQs using LJCA command packets.

## Important APIs, types, and functions
`struct ljca_gpio_dev` stores the LJCA client, gpiochip, firmware GPIO info, bitmaps for IRQ states and output direction, per-line connect modes, transfer buffers, mutexes, and a re-enable work item. Packet helpers are `ljca_gpio_config()`, read, write, and `ljca_enable_irq()`. IRQ flow uses `ljca_gpio_event_cb()`, mask/unmask, type setup, bus lock/unlock, and `ljca_gpio_async()`.

## Control flow
Probe obtains the LJCA client and platform GPIO info, allocates `connect_mode`, initializes mutexes, fills a can-sleep gpiochip with valid-mask callbacks, registers an LJCA event callback, configures a simple child irqchip, initializes work, and registers the gpiochip. GPIO operations serialize USB command transfers. IRQ events from firmware dispatch child IRQs immediately and schedule work to re-enable any still-unmasked lines.

## State and persistence behavior
Software tracks output-enabled state for `get_direction`, desired IRQ mask/enabled state, lines needing re-enable, and per-line pull/interrupt mode in `connect_mode`. Hardware state lives in the LJCA device and is updated by command packets; there is no durable persistence.

## Dependencies and integration points
The driver is an auxiliary driver for `usb_ljca.ljca-gpio`, imports namespace `LJCA`, uses ACPI name fallback for labels, gpiolib valid masks from `ljca_gpio_info`, and simple child IRQ domains.

## Risks and edge cases
`connect_mode` is shared between pin configuration and IRQ type configuration, so a later pinconf operation can overwrite interrupt configuration. Event callback does not validate packet length beyond command type. IRQ re-enable is asynchronous, leaving a small masked window after events.

## Test signals
Test LJCA transfer success/failure, valid pin mask enforcement, direction/output state tracking, pinconf pull-up/down, all IRQ trigger types, event callback demux, re-enable work cancellation on remove, and hot-unplug during pending transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ljca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-logicvc.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-logicvc.c

## Purpose
`gpio-logicvc.c` provides output-only GPIO support for Xylon LogiCVC display-controller GPIO registers. It exposes nine virtual outputs split across the main control register and power-control register.

## Important APIs, types, and functions
`struct logicvc_gpio` stores the gpiochip and regmap. `logicvc_gpio_offset()` maps offsets 0-4 into `LOGICVC_CTRL_REG` bits 11-15 and offsets 5-8 into `LOGICVC_POWER_CTRL_REG` bits 0-3. `logicvc_gpio_get()`, `logicvc_gpio_set()`, and `logicvc_gpio_direction_output()` implement the GPIO callbacks. Probe can reuse a parent syscon regmap or create an MMIO regmap for the node.

## Control flow
Probe allocates driver state, first tries `syscon_node_to_regmap()` on the parent, and falls back to mapping resource 0 plus `devm_regmap_init_mmio()`. It then fills a dynamic-base gpiochip with nine lines, get/set callbacks, and output-direction callback, and registers it with `devm_gpiochip_add_data()`. Direction output simply writes the value because the pins are always configured as outputs.

## State and persistence behavior
Line levels live in LogiCVC registers; direction is fixed output-only by hardware/driver contract. The driver keeps no shadow state and no persistent configuration outside the regmap-backed hardware registers.

## Dependencies and integration points
It binds to `xylon,logicvc-3.02.a-gpio`, integrates with parent syscon/regmap when available, and otherwise owns an MMIO regmap for the GPIO register block. Gpiolib consumers see it as a small output-only gpiochip.

## Risks and edge cases
The offset split between the two registers is correctness-critical; off-by-one errors would drive power-control bits instead of main-control bits or the reverse. Parent syscon fallback must match DT layout, and the local regmap `max_register` calculation depends on resource size and stride. No input-direction callback is provided.

## Test signals
Test all nine offsets, especially the transition from offset 4 to 5, parent syscon and standalone MMIO-regmap probe paths, output set/readback through regmap, and rejection of input-direction requests by gpiolib.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-logicvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson-64bit.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson-64bit.c

## Purpose
`gpio-loongson-64bit.c` is the modern Loongson GPIO platform driver for multiple 64-bit Loongson SoCs and chipsets. It supports bit-control and byte-control register layouts, optional reset deassertion, simple `to_irq` mapping, and a full irqchip for LS2K0300.

## Important APIs, types, and functions
`struct loongson_gpio_chip_data` describes label, mode, register offsets, interrupt count, parent handler, and irqchip. `struct loongson_gpio_chip` stores the generic chip wrapper, spinlock, base, and chip data. Byte-control callbacks implement direction/get/set. `loongson_gpio_to_irq()` enables per-line interrupts for simple mapping. LS2K0300 IRQ support uses ack/mask/unmask/set_type and `loongson_gpio_ls2k0300_irq_handler()`.

## Control flow
Probe gets match data, maps the register resource, deasserts optional reset, then initializes either gpio-generic for bit-control mode or custom byte-control callbacks. If chip data provides a real irqchip, parent IRQs are gathered and disabled/cleared before gpiochip registration; otherwise an `inten_offset` installs `to_irq`.

## State and persistence behavior
GPIO state is in MMIO registers. Byte-control mode uses a spinlock around direction and output writes; bit-control mode delegates locking to gpio-generic. Interrupt type is programmed in per-line polarity/edge/dual registers for LS2K0300.

## Dependencies and integration points
The driver binds to many Loongson OF compatibles and ACPI IDs, uses `gpio-generic`, platform IRQs, optional reset controls, and postcore init to make GPIOs available early.

## Risks and edge cases
The same driver name overlaps with older `gpio-loongson.c` on some builds. In simple `to_irq` mode, calling `to_irq` has the side effect of enabling hardware interrupt bits. LS2K0300 status bits may be set spuriously, so the handler must check enable bits too.

## Test signals
Test each OF/ACPI match-data variant, bit vs byte register mode, optional reset failure, simple `to_irq` enable side effects, LS2K0300 all trigger types including edge-both dual register, and spurious status filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson-64bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson.c

## Purpose
`gpio-loongson.c` is a legacy Loongson-2F/3A/3B GPIO driver using architecture-specific global registers. It registers a simple fixed-base gpiochip very early.

## Important APIs, types, and functions
The file uses `LOONGSON_GPIODATA` and `LOONGSON_GPIOIE` macros from architecture headers, protected by global `gpio_lock`. GPIO callbacks implement get, set, direction input, and direction output. `loongson_gpio_setup()` registers both the platform driver and a simple platform device.

## Control flow
Postcore init registers the driver and immediately creates a `loongson-gpio` platform device. Probe allocates a gpiochip, sets fixed base 0, line count based on CPU config, installs callbacks, and calls `gpiochip_add_data()`.

## State and persistence behavior
All state is in architecture GPIO registers. There is no managed remove path and no software cache. Input values are read from the upper half of `GPIODATA`, while output values are written to lower bits.

## Dependencies and integration points
This depends on Loongson architecture headers and CPU configuration. It is for older non-DT platforms and uses fixed GPIO numbering.

## Risks and edge cases
Fixed base 0 can conflict with other gpiochips. Probe uses `gpiochip_add_data()` instead of devm registration, and the created platform device is not retained for cleanup. The line count changes with build configuration.

## Test signals
Test early boot registration, GPIO direction/value operations on 2F and 3A/3B hardware, fixed numbering compatibility, and coexistence rules when the modern Loongson driver is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson1.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson1.c

## Purpose
`gpio-loongson1.c` supports the Loongson 1 SoC GPIO controller using gpio-generic for MMIO data, output, and direction registers.

## Important APIs, types, and functions
`struct ls1x_gpio_chip` embeds `gpio_generic_chip` and the MMIO base. `ls1x_gpio_request()` sets the enable/config bit for a line; `ls1x_gpio_free()` clears it. Probe maps registers, initializes gpio-generic, installs request/free hooks, and registers the chip.

## Control flow
Probe maps resource 0, builds a generic chip config with `GPIO_DATA`, `GPIO_OUTPUT`, and `GPIO_DIR`, initializes it, clears `ngpio` so gpiolib reads the firmware `ngpios` property, and registers the chip. Request/free toggle the `GPIO_CFG` bit under the generic chip lock.

## State and persistence behavior
Hardware stores config, direction, data, and output state. The driver keeps no software shadow. Requested lines are enabled in hardware and disabled on free.

## Dependencies and integration points
The driver binds to `loongson,ls1x-gpio`, depends on gpio-generic and platform MMIO resources, and integrates with DT-provided line count.

## Risks and edge cases
Clearing `ngpio` relies on firmware providing `ngpios`; missing properties can produce registration surprises. Request/free side effects mean consumers that hold descriptors control hardware line enable state.

## Test signals
Test DT `ngpios` parsing, request/free config-bit toggling, direction/input/output operations, and registration failure paths with missing MMIO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp3943.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp3943.c

## Purpose
`gpio-lp3943.c` exposes the 16 GPIO-capable pins of the TI/National LP3943 MFD device. It arbitrates pins shared with other LP3943 functions and tracks direction in software because hardware lacks a direction register.

## Important APIs, types, and functions
`struct lp3943_gpio` stores the gpiochip, parent `struct lp3943`, and `input_mask`. Request/free use `lp3943->pin_used`. `lp3943_gpio_set_mode()` writes mux configuration; get reads either input status registers or mux output state depending on `input_mask`.

## Control flow
Probe gets the parent MFD data, copies a gpiochip template, sets parent, and registers it. Direction input marks the bit in `input_mask` and writes input mux mode. Direction output writes the requested output mode and clears the input bit. Get chooses input or output readback based on the software mask.

## State and persistence behavior
The parent MFD tracks pin ownership in `pin_used`. The GPIO driver tracks direction in `input_mask`; hardware only exposes input and output status. Output levels are encoded through mux mode values rather than a separate output register.

## Dependencies and integration points
It is a platform child of the LP3943 MFD, uses LP3943 reg helpers and mux tables, and binds to `ti,lp3943-gpio`.

## Risks and edge cases
Direction state can become stale if another function changes mux state outside this driver. Requesting a pin already assigned to another LP3943 subfunction returns `-EBUSY`. Output get returns `-EINVAL` for unexpected mux states.

## Test signals
Test pin ownership conflicts, input and output direction transitions, reads from GPIO A/B input registers, output readback from mux registers, and coexistence with LP3943 LED/PWM functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp3943.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp873x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp873x.c

## Purpose
`gpio-lp873x.c` exposes the two output-only GPO pins on TI LP873x PMICs.

## Important APIs, types, and functions
`struct lp873x_gpio` stores a gpiochip and parent LP873x pointer. GPIO callbacks include output-only direction reporting, `lp873x_gpio_request()` for GPO2 mux setup, get/set via `LP873X_REG_GPO_CTRL`, and `lp873x_gpio_set_config()` for open-drain/push-pull.

## Control flow
Probe copies a template chip, gets parent MFD data, sets the gpiochip parent, and registers it. Request for offset 1 changes `CLKIN_PIN_SEL` to route the pin to GPO2; offset 0 needs no muxing. Direction output and set update the value bit at `offset * 4`.

## State and persistence behavior
State is in PMIC regmap registers. The driver has no shadow and no input state. Both lines are always reported as outputs.

## Dependencies and integration points
It is a platform child named `lp873x-gpio`, depends on the LP873x MFD regmap, and exposes pinconf drive mode through gpiolib.

## Risks and edge cases
GPO2 request changes a shared pin mux and can affect clock input users. Direction input always fails. Register bit positions are spaced by four bits, so offset math must stay aligned with PMIC definitions.

## Test signals
Test request for offsets 0/1 and invalid offsets, GPO2 mux update, output get/set, open-drain/push-pull config, and PMIC regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp873x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp87565.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp87565.c

## Purpose
`gpio-lp87565.c` exposes three GPIO pins on TI LP87565-Q1 PMIC variants using the parent regmap.

## Important APIs, types, and functions
`struct lp87565_gpio` holds a gpiochip and regmap. Request configures each pin's function mux to GPIO mode. Direction, get, set, and drive-mode configuration operate on `LP87565_REG_GPIO_IN`, `OUT`, `CONFIG`, and `PIN_FUNCTION`.

## Control flow
Probe copies a gpiochip template, obtains the parent MFD regmap, and registers three can-sleep lines. Request for offsets 0-2 sets the corresponding `GPIO*_SEL` bit. Direction output writes the value first, then sets the direction bit.

## State and persistence behavior
All state is in PMIC registers; no software cache is kept. Direction is read from `GPIO_CONFIG`, input values from `GPIO_IN`, and output values from `GPIO_OUT`.

## Dependencies and integration points
It is a platform child `lp87565-gpio`, depends on `linux/mfd/lp87565.h` register definitions and regmap, and exposes pinconf open-drain/push-pull.

## Risks and edge cases
Requesting a line changes pin function away from EN pin mode. The open-drain bit offset is derived from `LP87565_GPIO1_OD`, so header definition changes directly affect all offsets. Invalid offsets fail only in request, while gpiolib normally bounds operation offsets.

## Test signals
Test mux request for each pin, input/output direction and value, drive config, regmap error paths, and interaction with PMIC enable-pin functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp87565.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc18xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc18xx.c

## Purpose
`gpio-lpc18xx.c` supports NXP LPC18xx/LPC43xx GPIO ports and their optional eight-line GPIO pin interrupt controller.

## Important APIs, types, and functions
`struct lpc18xx_gpio_chip` holds the gpiochip, main MMIO base, optional pin interrupt controller, and direction lock. `struct lpc18xx_gpio_pin_ic` holds interrupt-controller MMIO, irqdomain, raw lock, and backpointer. GPIO callbacks read/write byte-addressed line data and direction port registers. IRQ domain callbacks allocate parent NVIC IRQs 32-39.

## Control flow
Probe maps the main `gpio` resource by name or legacy index, enables the clock, registers a 256-line gpiochip, then attempts optional pin-IC setup. Pin-IC probe finds the parent IRQ domain, maps the `gpio-pin-ic` resource, creates a hierarchical domain, and stores it for removal. IRQ mask/unmask update rising/falling enable registers and parent masking; EOI clears edge status.

## State and persistence behavior
GPIO line values and direction are in MMIO. Pin interrupt trigger mode is in pin-IC registers. The optional irqdomain persists until remove, where it is explicitly removed.

## Dependencies and integration points
The driver binds to `nxp,lpc1850-gpio`, depends on DT `reg-names`, clocks, pinctrl generic request/free, irqdomain hierarchy, and the parent Cortex-M NVIC domain.

## Risks and edge cases
Pin-IC registration failure is intentionally non-fatal, so GPIO works without IRQs. The `lpc18xx_gpio_pin_ic_isel()` helper has inverted naming around set/clear semantics and must match hardware. Byte-addressed line data writes assume the hardware exposes one byte per GPIO offset.

## Test signals
Test legacy and named resource mapping, clock failure, 256-line get/set/direction, optional pin-IC absent/present cases, IRQ allocation bounds, rising/falling/both/level type behavior, and domain removal on driver remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc18xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc32xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc32xx.c

## Purpose
`gpio-lpc32xx.c` exposes the LPC32xx SoC's mixed GPIO/GPI/GPO banks as six separate gpiochips with legacy fixed numbering and bank-specific register mappings.

## Important APIs, types, and functions
`struct gpio_regs` describes per-bank register offsets. `struct lpc32xx_gpio_chip` combines gpiochip, register mapping, and MMIO base. Static gpiochip entries cover `gpio_p0`, `gpio_p1`, `gpio_p2`, `gpio_p3`, `gpi_p3`, and `gpo_p3`. Bank-specific helpers handle direction, level set, and input state mapping.

## Control flow
Probe maps the shared GPIO register resource, assigns the base to each static chip, installs OF xlate for three-cell GPIO specifiers, and registers all six chips. P0/P1/P2 use contiguous bit mappings; P3 GPIO uses non-contiguous input bits; GPI and GPO P3 are input-only and output-only banks.

## State and persistence behavior
All state is in SoC registers. The static `lpc32xx_gpiochip[]` array is process-wide driver state and each entry persists for module lifetime. No software output cache is kept except hardware outp_state readback for GPO.

## Dependencies and integration points
It binds to `nxp,lpc3220-gpio`, uses raw MMIO accessors, fixed gpio bases matching historical numbering, OF three-cell translation, and gpiolib.

## Risks and edge cases
The probe ignores return values from each `devm_gpiochip_add_data()` call, so partial registration failures are not propagated. Static chip objects mean only one controller instance is supported. Several `to_irq` callbacks return `-ENXIO`, explicitly documenting no IRQ mapping.

## Test signals
Test all six banks, fixed base numbering, P3 non-contiguous input mapping including GPIO5, OF xlate bank validation, input-only/output-only behavior, and failure injection around per-chip registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc32xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-macsmc.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-macsmc.c

## Purpose
`gpio-macsmc.c` exposes Apple Silicon SMC PMU GPIO keys as a can-sleep gpiochip. It supports reading inputs and writing outputs but does not yet implement mode changes or IRQ configuration.

## Important APIs, types, and functions
`struct macsmc_gpio` stores the Apple SMC pointer, gpiochip, device, and first SMC key index. `macsmc_gpio_key()` builds `gPxx` keys, `macsmc_gpio_nr()` decodes key names, and `macsmc_gpio_find_first_gpio_index()` binary-searches the SMC key table. Operations are get_direction, get, set, and valid-mask initialization.

## Control flow
Probe gets the parent `apple_smc`, finds the first GPIO key, validates that at least one key lies in range, initializes a 64-line dynamic gpiochip, and registers it. Valid-mask initialization walks SMC keys from the first GPIO key until `gPff` or count limit and marks decoded GPIO numbers. Get determines direction, then reads either `CMD_OUTPUT` or `CMD_INPUT`; set writes `CMD_OUTPUT`.

## State and persistence behavior
The SMC owns actual GPIO state and modes. The driver stores only the key-table starting index and derives valid pins at registration. No mode or IRQ state is changed by the driver.

## Dependencies and integration points
It binds to `apple,smc-gpio`, depends on the Apple SMC MFD, SMC key enumeration and u32 read/write commands, and gpiolib valid masks.

## Risks and edge cases
SMC command semantics vary across PMU hardware, especially detailed config bits. Direction detection falls back from pin mode to IRQ mode and treats failure as output. `macsmc_gpio_set()` ORs the command into the value before writing, so command/value encoding must match SMC expectations.

## Test signals
Test key-table binary search on different SMC key layouts, valid-mask decoding for sparse keys, input/output reads, output writes, failure of `CMD_PINMODE` fallback behavior, and absence of unsupported mode/IRQ operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-macsmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-madera.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-madera.c

## Purpose
`gpio-madera.c` exposes GPIOs on Cirrus Logic Madera codec MFD devices and registers an explicit fixed pin range to the Madera pinctrl driver.

## Important APIs, types, and functions
`struct madera_gpio` stores the parent `struct madera` and gpiochip. GPIO callbacks use per-pin register pairs at `MADERA_GPIO1_CTRL_1/2 + 2 * offset` for level and direction. Probe selects `ngpio` based on codec type and calls `gpiochip_add_pin_range()`.

## Control flow
Probe obtains parent MFD state and pdata, copies a gpiochip template, sets parent and base, switches on codec type for line count, registers the chip, then maps all GPIOs to the `madera-pinctrl` pinctrl range. Direction output clears the direction bit first and then sets the level bit.

## State and persistence behavior
GPIO state is in codec regmap registers. Platform data can preserve a legacy fixed gpio base; otherwise dynamic numbering is used. No software shadow is kept.

## Dependencies and integration points
It is a platform child `madera-gpio`, depends on Madera MFD register definitions, regmap, pdata, and the `pinctrl-madera` driver, declared with a soft dependency.

## Risks and edge cases
Unknown codec variants fail probe. Pin range registration failure aborts after gpiochip registration through devm cleanup. The driver assumes fixed silicon mapping between GPIOs and pinctrl pins.

## Test signals
Test each Madera variant line count, fixed and dynamic bases, direction/value register updates, generic pinconf routing to pinctrl, pin range registration, and load ordering with pinctrl-madera.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-madera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max3191x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max3191x.c

## Purpose
`gpio-max3191x.c` exposes Maxim MAX3191x industrial digital-input serializers as input-only GPIOs over SPI. It supports daisy-chains, optional status-byte diagnostics with CRC, fault GPIOs, and debounce control GPIOs.

## Important APIs, types, and functions
`struct max3191x_chip` stores the gpiochip, mutex, chip count, mode, optional GPIO descriptor arrays, SPI message/transfer, diagnostic bitmaps, and undervoltage policy. Core functions are `max3191x_readout_locked()`, `max3191x_chip_is_faulting()`, get/get_multiple, `max3191x_set_config()` for debounce, optional GPIO array acquisition, probe, and remove.

## Control flow
Probe reads daisy-chain count and mode properties, allocates diagnostic bitmaps and RX buffer, gets optional modesel/fault/db0/db1 GPIO arrays with either one shared descriptor or per-chip descriptors, drives modesel, validates debounce arrays, prepares the SPI transfer length, registers an input-only can-sleep gpiochip, and initializes the CRC table before driver registration. Reads serialize a full-chain SPI transfer, update diagnostics, reject faulting chips, and return requested bits.

## State and persistence behavior
Input values are sampled on each SPI read and not cached for later get. Diagnostic bitmaps persist between reads and are overwritten each readout. Debounce and mode pins are external GPIO state driven by this driver.

## Dependencies and integration points
It binds to `maxim,max31910/11/12/13/53/63`, depends on SPI, GPIO consumer descriptors for optional sideband pins, crc8, gpiolib get_multiple, and pinconf input debounce.

## Risks and edge cases
Status-byte mode rejects data on CRC, overtemperature, undervoltage, or fault conditions, but `maxim,ignore-undervoltage` suppresses undervoltage/fault handling. Optional GPIO array count mismatch is logged and ignored, possibly leaving hardware strapped incorrectly. A faulting chip makes only its eight lines return `-EIO`.

## Test signals
Test 8-bit and 16-bit modes, CRC error detection, undervoltage ignore policy, shared vs per-chip fault/debounce/modesel GPIOs, get_multiple across chip boundaries, invalid debounce values, and SPI error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max3191x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7300.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7300.c

## Purpose
`gpio-max7300.c` is the I2C bus wrapper for the shared MAX7300/MAX7301 GPIO expander core in `gpio-max730x.c`.

## Important APIs, types, and functions
It defines I2C `read` and `write` callbacks using SMBus byte-data operations, `max7300_probe()`, `max7300_remove()`, and a `max7300` I2C driver registered at subsys init.

## Control flow
Probe verifies `I2C_FUNC_SMBUS_BYTE_DATA`, allocates `struct max7301`, fills bus callbacks and device pointer, and delegates to `__max730x_probe()`. Remove delegates to `__max730x_remove()`.

## State and persistence behavior
All GPIO state lives in the shared core's `struct max7301` and device registers. This wrapper only provides bus access and driver lifetime.

## Dependencies and integration points
It depends on I2C SMBus byte-data support and the exported MAX730x core helpers from `linux/spi/max7301.h`/`gpio-max730x.c`.

## Risks and edge cases
Adapters without SMBus byte-data support fail probe. Register semantics are inherited from the core; wrapper bugs would manifest as wrong byte register accesses.

## Test signals
Test adapter functionality rejection, probe delegation, read/write SMBus transactions, remove power-down delegation, and early subsys registration for GPIO consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7301.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7301.c

## Purpose
`gpio-max7301.c` is the SPI bus wrapper for the shared MAX7300/MAX7301 GPIO expander core.

## Important APIs, types, and functions
It defines `max7301_spi_write()` and `max7301_spi_read()` for 16-bit command words, `max7301_probe()`, `max7301_remove()`, and a SPI driver registered at subsys init.

## Control flow
Probe forces `bits_per_word = 16`, calls `spi_setup()`, allocates `struct max7301`, fills read/write callbacks and device pointer, then delegates to `__max730x_probe()`. Reads use a write/read command cycle; writes send one 16-bit word.

## State and persistence behavior
The wrapper stores no GPIO state. Shared core fields and device registers hold pin config, output levels, and power state.

## Dependencies and integration points
It depends on SPI devices named `max7301`, the shared MAX730x core, and early subsys registration after SPI postcore init so GPIO consumers can probe early.

## Risks and edge cases
Changing `bits_per_word` can fail on controllers that do not support 16-bit transfers. Endianness of the 16-bit command word must match SPI controller expectations and chip protocol.

## Test signals
Test SPI setup failure, 16-bit read/write transactions, delegation to shared core, remove power-down, and early availability to dependent devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7301.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max730x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max730x.c

## Purpose
`gpio-max730x.c` contains the shared GPIO implementation for Maxim MAX7300/MAX7301 28-line expanders, independent of whether the bus is I2C or SPI.

## Important APIs, types, and functions
The public helpers are `__max730x_probe()` and `__max730x_remove()`. GPIO callbacks include `max7301_direction_input()`, `max7301_direction_output()`, `max7301_get()`, `max7301_set()`, and internal `__max7301_set()`. State is stored in `struct max7301` fields such as `port_config`, `out_level`, `input_pullup_active`, callbacks, and mutex.

## Control flow
The bus wrapper allocates `struct max7301` and supplies read/write callbacks. Probe initializes the mutex, powers up the chip, applies platform base and pull-up mask, configures all 28 exported pins as inputs with default pull-up disabled unless requested, caches port configuration bytes, and registers the gpiochip. Remove powers down the chip.

## State and persistence behavior
`port_config[]` mirrors four pins per config register. `out_level` caches output values because output reads return the cached level. Hardware power state is changed on probe/remove.

## Dependencies and integration points
This core depends on wrapper-provided bus callbacks and optional `max7301_platform_data`. It exports GPL symbols used by MAX7300 I2C and MAX7301 SPI wrappers.

## Risks and edge cases
The first four chip pins are unused, so all GPIO offsets are shifted by four. Initialization writes every pin to input mode; board defaults can change at probe. The driver avoids forbidden zero config writes by seeding config bytes with `0xAA`; changing that can violate datasheet constraints.

## Test signals
Test all 28 offsets with +4 mapping, input pull-up platform mask, output cached get, direction register packing, power up/down register writes, and error propagation from bus callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max730x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max732x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max732x.c

## Purpose
`gpio-max732x.c` supports Maxim MAX7319/MAX7320-7327 I2C port expanders with differing combinations of push-pull outputs, inputs, open-drain I/O, and optional interrupt support.

## Important APIs, types, and functions
`max732x_features[]` encodes per-model port layout and interrupt capability. `struct max732x_chip` stores clients for group A/B I2C addresses, direction masks, output shadows, locks, and optional IRQ state. GPIO callbacks implement get, set, set_multiple, direction input/output. Optional IRQ helpers support mask/unmask, type, wake, pending calculation, and threaded handling.

## Control flow
Probe obtains platform/OF pdata, derives port layout from device ID, creates a dummy I2C client for the second group when needed, initializes output shadows by reading hardware, sets up optional IRQ support if compiled and wired, and registers the gpiochip. Port operations choose group A or B based on masks and update shadow registers before writing. IRQ pending reads two bytes from group A, computes changed bits against configured rising/falling triggers, and handles nested child IRQs.

## State and persistence behavior
`reg_out[2]` shadows output bytes and is the basis for set_multiple and masked updates. Direction capability masks are static per chip model. Optional IRQ masks and trigger bitmaps are cached in software and synced to hardware mask schemes that differ by model.

## Dependencies and integration points
The driver binds to I2C IDs and OF compatibles for MAX7319/MAX7320-7327, uses optional platform data for base, optional threaded parent IRQ, and gpiolib nested IRQ support.

## Risks and edge cases
The OF helper only supplies gpio base, so richer platform settings are unavailable in DT. Some models have no interrupt mask or merged masks, making IRQ behavior model-specific. Address group handling depends on the client's high address bits and can fail if board data uses the wrong address.

## Test signals
Test every model's port count/direction masks, group A/B dummy-client creation, get/set/set_multiple, open-drain input-as-high behavior, IRQ edge type rejection/acceptance, mask sync for independent/merged/no-mask models, and wake propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max732x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7360.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7360.c

## Purpose
`gpio-max7360.c` exposes two GPIO-style functions of the Maxim MAX7360 MFD: normal port GPIOs and keypad-column pins reused as general-purpose outputs.

## Important APIs, types, and functions
Match data selects `MAX7360_GPIO_PORT` or `MAX7360_GPIO_COL`. Helpers include `max7360_get_available_gpos()`, `max7360_gpo_init_valid_mask()`, `max7360_set_gpos_count()`, `max7360_gpio_reg_mask_xlate()`, regmap IRQ descriptors, and `max7360_handle_mask_sync()`. Probe builds a `gpio_regmap_config`.

## Control flow
Probe gets the parent regmap and match data. For port GPIOs it optionally creates a custom regmap IRQ chip when `interrupt-controller` is present, enables interrupt edge configuration on all port pins, and applies optional constant-current output configuration. For column GPOs it calculates how many columns are not used by the keypad, updates the debounce register's GPO/keypad split, and installs a valid mask. It then registers through gpio-regmap.

## State and persistence behavior
State is in the parent MAX7360 regmap. Port outputs use PWM duty-cycle registers with 0 or 255 values, requiring custom mask translation. Column GPO availability is derived from the parent keypad column count and stays fixed after probe.

## Dependencies and integration points
It is an MFD child binding to `maxim,max7360-gpio` or `maxim,max7360-gpo`, depends on parent properties such as `keypad,num-columns`, named IRQ `inti`, gpio-regmap, and regmap-irq.

## Risks and edge cases
Column GPO valid-mask math must match keypad column allocation, or keypad pins could be exposed as GPIO outputs. Interrupt-controller setup requires parent IRQ lookup and writes edge bits for all lines. PWM registers as GPIO outputs need the custom full-byte mask translator.

## Test signals
Test both compatibles, keypad column counts and valid masks, output via PWM registers, constant-current property writes, optional interrupt-controller setup, mask sync to `PWMCFG`, and missing parent regmap/IRQ/property failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77620.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77620.c

## Purpose
`gpio-max77620.c` provides GPIO and nested IRQ support for MAX77620 and MAX20024 PMIC GPIO blocks.

## Important APIs, types, and functions
`struct max77620_gpio` stores the gpiochip, regmap, device, IRQ bus mutex, per-line IRQ type, and enabled flags. GPIO callbacks manage direction, get, set, drive config, and debounce. IRQ callbacks include parent threaded handler, mask/unmask, set_type, bus lock/sync, and hardware initialization that disables bootloader-left interrupts.

## Control flow
Probe obtains the parent PMIC data and platform IRQ, allocates state, initializes the gpiochip, configures a threaded simple child irqchip, registers the gpiochip, then requests the parent threaded IRQ. The parent handler reads `IRQ_LVL2_GPIO`, iterates pending bits, and handles nested IRQs. Bus sync writes either the cached trigger type or zero into each GPIO config interrupt mask.

## State and persistence behavior
GPIO direction/value/drive/debounce live in per-GPIO PMIC config registers. IRQ enable and type are cached in arrays until bus sync writes them. Hardware IRQ masks are reset to disabled during gpiochip IRQ init.

## Dependencies and integration points
It is a platform child of the MAX77620 MFD, supports platform IDs `max77620-gpio` and `max20024-gpio`, uses regmap, gpiolib nested threaded IRQs, and pinconf drive/debounce.

## Risks and edge cases
Only edge triggers are supported; level requests fail. Parent IRQ is requested after gpiochip registration, so error cleanup relies on devm. Debounce values are bucketed to hardware-supported 0/8/16/32 ms choices, not exact requested values.

## Test signals
Test get/set/direction, open-drain/push-pull, debounce bucket boundaries, IRQ mask initialization, rising/falling/both edge types, nested parent IRQ handling, and regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77650.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77650.c

## Purpose
`gpio-max77650.c` exposes the single GPIO/GPI pin on MAX77650/MAX77651 charger/power-supply MFD devices.

## Important APIs, types, and functions
`struct max77650_gpio_chip` stores the parent regmap, gpiochip, and GPI IRQ number. GPIO callbacks implement direction input/output, set/get, get_direction, pinconf drive/debounce, and `max77650_gpio_to_irq()`.

## Control flow
Probe gets the parent I2C device and regmap, obtains the named `GPI` IRQ, initializes a one-line can-sleep gpiochip with dynamic base and the parent I2C name as label, and registers it. Direction output updates direction and output bits together; get reads input-value bits; `to_irq` returns the pre-fetched parent IRQ.

## State and persistence behavior
All state lives in `MAX77650_REG_CNFG_GPIO`. The driver keeps only the IRQ number. Debounce config is a single enable bit, not a duration.

## Dependencies and integration points
It is a platform child `max77650-gpio`, depends on MAX77650 MFD regmap and named IRQ resource `GPI`, and exposes pinconf open-drain/push-pull and debounce.

## Risks and edge cases
`get_direction()` returns the raw direction bit values, relying on gpiolib's convention that input is nonzero. `set_config(PIN_CONFIG_INPUT_DEBOUNCE)` ignores the requested debounce argument and simply enables debounce. Only one GPIO exists, so consumers must not expect per-offset IRQ variation.

## Test signals
Test one-line get/set/direction, `to_irq` mapping to named GPI IRQ, drive mode config, debounce enable behavior, and missing regmap or IRQ probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77650.c -->
