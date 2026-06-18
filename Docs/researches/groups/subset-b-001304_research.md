# subset-b-001304 research

Grouped research for `subset-b-001304`. Each section preserves the source path in its title and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-nct6694.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-nct6694.c

## Purpose
`gpio-nct6694.c` exposes the Nuvoton NCT6694 USB-attached GPIO controller as an eight-line `gpio_chip` per hardware GPIO group. It talks through the parent NCT6694 MFD USB command protocol rather than MMIO, and it supports direction control, input/output value access, open-drain versus push-pull output configuration, valid-line masking, and nested edge IRQ delivery.

## Important APIs, types, and functions
The private `struct nct6694_gpio_data` stores the parent `struct nct6694`, `struct gpio_chip`, two mutexes, cached one-byte register values, rising/falling IRQ trigger masks, the allocated GPIO group, and the mapped parent IRQ. GPIO operations are `nct6694_get_direction()`, `nct6694_direction_input()`, `nct6694_direction_output()`, `nct6694_get_value()`, `nct6694_set_value()`, `nct6694_set_config()`, and `nct6694_init_valid_mask()`. IRQ operations are `nct6694_irq_handler()`, `nct6694_irq_set_type()`, `nct6694_irq_mask()`, `nct6694_irq_unmask()`, and the bus-lock/sync pair that writes trigger masks back to hardware. Probe allocates a group through the parent `gpio_ida`, creates line names, maps the group IRQ from the parent irqdomain, requests a threaded shared IRQ, and registers the chip.

## Control flow
All hardware accesses build `struct nct6694_cmd_header` requests using module `NCT6694_GPIO_MOD` and group-offset register addresses. Direction and output changes are read-modify-write sequences under `data->lock`. `get_value()` first reads the output-direction register; output lines read `GPO_DATA`, while input lines read `GPI_DATA`. `set_config()` only accepts `PIN_CONFIG_DRIVE_OPEN_DRAIN` and `PIN_CONFIG_DRIVE_PUSH_PULL`, toggling `GPO_TYPE`.

The threaded parent IRQ reads `GPI_STS`, walks each set bit, dispatches `handle_nested_irq()` for the child mapping, and writes `GPI_CLR` for the serviced bit. IRQ type configuration updates cached rising/falling masks; the bus sync writes those masks to `GPI_FALLING` and `GPI_RISING`.

## State and persistence behavior
Runtime state is one byte of temporary register cache plus persistent cached IRQ trigger masks. The driver does not implement suspend/resume context restore; hardware state is read on demand and trigger masks are initialized from hardware during probe. Group allocation is persistent for the lifetime of the platform device and released through a devm action.

## Dependencies and integration points
The driver depends on the NCT6694 MFD interface (`nct6694_read_msg()`, `nct6694_write_msg()`, parent `gpio_ida`, parent irqdomain, and `NCT6694_IRQ_GPIO0`), gpiolib, pinconf packed configs, IRQ domains, threaded IRQs, and devm cleanup. It binds as platform device `nct6694-gpio`.

## Risks and edge cases
USB command failures propagate directly to GPIO callers, so consumers must handle negative GPIO reads. The chip is marked `can_sleep = false` even though the backend is a USB/MFD command path; if those commands can sleep, atomic GPIO users would be risky. `irq_set_type()` only ever ORs requested trigger bits and does not clear the opposite edge first, so changing an IRQ from both edges to one edge can leave stale trigger state. The IRQ handler ignores clear write failures and returns handled if any status was read.

## Test signals
Useful signals are successful probe with valid line names and valid-mask contents, direction round trips through `GPO_DIR`, input versus output reads hitting the expected data registers, open-drain/push-pull writes to `GPO_TYPE`, edge IRQ delivery for all valid lines, and retesting IRQ type changes to ensure stale rising/falling masks are not retained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-nct6694.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-nomadik.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-nomadik.c

## Purpose
`gpio-nomadik.c` supports the ST-Ericsson Nomadik/STA2X11 GPIO block and the reduced Mobileye EyeQ5-compatible variant. Each controller handles up to 32 GPIOs with direction, data, edge IRQs, wake IRQ masks, sleep-mode policy, debugfs reporting, and optional sharing with `pinctrl-nomadik`.

## Important APIs, types, and functions
State lives in `struct nmk_gpio_chip` from `<linux/gpio/gpio-nomadik.h>`, populated by `nmk_gpio_populate_chip()`. GPIO callbacks include `nmk_gpio_get_dir()`, `nmk_gpio_make_input()`, `nmk_gpio_get_input()`, `nmk_gpio_make_output()`, and `nmk_gpio_set_output()`. Low-level helpers `__nmk_gpio_set_output()`, `__nmk_gpio_make_output()`, and `__nmk_gpio_set_slpm()` are exported for pinctrl cooperation. IRQ support is implemented by `nmk_gpio_irq_ack()`, `nmk_gpio_irq_maskunmask()`, `nmk_gpio_irq_set_type()`, `nmk_gpio_irq_set_wake()`, startup/shutdown, and `nmk_gpio_irq_handler()`.

## Control flow
Probe calls `nmk_gpio_populate_chip()` to locate the platform device by fwnode, read `gpio-bank` and `ngpios`, map MMIO, acquire and prepare an optional clock, deassert a shared reset, and cache the chip for pinctrl builds. Then it wires gpiolib callbacks, installs an immutable IRQ chip, requests the shared parent IRQ, optionally reads `LOWEMI`, and registers the chip.

GPIO operations enable the peripheral clock around register access. Output writes use dedicated set/clear registers; direction changes use `DIRS` and `DIRC`. IRQ type updates disable current normal/wake masks, adjust cached `edge_rising` and `edge_falling`, then re-enable masks for active or wake-enabled lines. The top-level IRQ handler reads `NMK_GPIO_IS`, clears impossible pending bits outside `ngpio`, and dispatches child domain IRQs.

## State and persistence behavior
Cached state includes normal masks (`rimsc`, `fimsc`), wake masks (`rwimsc`, `fwimsc`), real wake requests, edge selection, sleep-mode support, low-EMI state, bank id, and Mobileye compatibility. The driver prepares clocks/reset at population time and never releases them through a remove path because the platform driver suppresses bind attributes and is initialized at subsystem init. Mobileye-compatible devices deliberately skip SLPM, wake, and alternate-function registers.

## Dependencies and integration points
The driver integrates with platform devices, fwnode lookup, optional clocks, reset controls, gpiolib, IRQ domains, and optionally `pinctrl-nomadik`. It uses `subsys_initcall()` so GPIOs are available early. Mobileye EyeQ5 support reuses the core data/direction/IRQ subset but avoids pinctrl sharing and unsupported register writes.

## Risks and edge cases
The global `nmk_gpio_slpm_lock` coordinates sleep-mode register updates when pinctrl is absent; cross-driver ordering is important. Clock enable calls are not checked for failure. Both-edge IRQs depend on separate rising/falling mask state and correct reprogramming during type changes. Mobileye paths use WARN guards if wake or alternate-mode helpers are called incorrectly. Device ownership is unusual because population may be triggered by either GPIO or pinctrl using different device pointers for resources and devm allocations.

## Test signals
Test with Nomadik and EyeQ5 compatibles should verify probe, `ngpios`, direction/value operations under clock gating, edge rising/falling/both IRQ delivery, wake enable rejection on EyeQ5, absence of unsupported register writes on EyeQ5, and correct debugfs mode output when pinctrl is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-nomadik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-novalake-events.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-novalake-events.c

## Purpose
`gpio-novalake-events.c` exposes Intel Nova Lake ACPI GPE blocks as GPIO interrupt sources. Its job is not general-purpose output control; it lets ACPI General Purpose Events be handled through GPIO IRQs after the platform has been switched from legacy GPE mode to exposed GPIO interrupt mode through an ACPI `_DSM`.

## Important APIs, types, and functions
`struct nvl_gpio` stores the `gpio_chip`, mapped I/O-port register base, raw spinlock, and GPE block size. `nvl_gpio_get()` reads GPE status bits. IRQ callbacks include `nvl_gpio_irq_set_type()`, `nvl_gpio_irq_mask_unmask()`, `nvl_gpio_irq_mask()`, `nvl_gpio_irq_unmask()`, `nvl_gpio_irq_ack()`, and parent handler `nvl_gpio_irq()`. `nvl_acpi_enable_gpe_mode()` evaluates the Intel GPE mode `_DSM` using GUID `079406e6-bdea-49cf-8563-03e2811901cb`.

## Control flow
Probe validates the first `IORESOURCE_IO` as an even, nonzero GPE block size no larger than 0x20 bytes, maps it with `devm_ioport_map()`, requests the platform IRQ, initializes a GPIO chip with `ngpio` equal to the status half of the block in bits, registers an immutable IRQ chip, and finally calls the ACPI `_DSM` to request exposed mode. Parent IRQ handling scans every status byte, reads the corresponding enable byte, intersects pending and enabled bits, and dispatches each child hwirq through the GPIO irqdomain.

## State and persistence behavior
The only persistent driver state is the block size and MMIO/I/O mapping. IRQ enable state lives in the hardware GPE enable half; pending state lives in the status half and is acknowledged by writing the bit back. The `_DSM` request is made every probe/boot, and the source comment notes the platform mode switch takes effect on the next boot.

## Dependencies and integration points
The driver binds through ACPI HID `INTC1114`, uses ACPI resource-provided I/O ports and platform IRQs, gpiolib IRQ domains, raw spinlocks, and ACPI DSM evaluation. The visible GPIOs are status bits for ACPI events, not normal board GPIO outputs.

## Risks and edge cases
The source explicitly warns that uninstalling the driver while exposed mode is active can leave GPEs unhandled until firmware falls back to legacy mode after two reboots. `nvl_gpio_irq_set_type()` accepts any edge or level sense by selecting a Linux IRQ flow handler; hardware appears to provide status/enable bits rather than independent polarity programming. Parent IRQ scanning loops over `blk_size`, but pin count is only the first half of that size; this relies on `GPE_EN_REG_OFFSET(block_size)` address arithmetic and should be checked for off-by-half mistakes.

## Test signals
Signals include valid probe from ACPI resources, rejection of bad block sizes, successful `_DSM` call, correct `ngpio` for 64/128 pin GPE blocks, mask/unmask writes to enable bytes, ack writes to status bytes, and child IRQ delivery only for status bits that are also enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-novalake-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-npcm-sgpio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-npcm-sgpio.c

## Purpose
`gpio-npcm-sgpio.c` drives Nuvoton NPCM serial GPIO hardware. It presents output SGPIOs followed by input SGPIOs in one GPIO chip, configures the SGPIO shift clock and port counts, supports readback of both ranges, and exposes interrupts only for input SGPIOs.

## Important APIs, types, and functions
`struct npcm_sgpio` stores the chip, peripheral clock, immutable IRQ chip, raw lock, base, parent IRQ, input/output counts, derived port counts, and per-input IRQ type cache. `struct npcm_sgpio_bank` maps the eight 8-bit banks to read, write, event-config, and event-status registers. GPIO callbacks are `npcm_sgpio_dir_in()`, `npcm_sgpio_dir_out()`, `npcm_sgpio_get_direction()`, `npcm_sgpio_set()`, and `npcm_sgpio_get()`. IRQ functions include `npcm_sgpio_irq_init_valid_mask()`, `npcm_sgpio_irq_set_mask()`, `npcm_sgpio_irq_ack()`, `npcm_sgpio_set_type()`, and `npcm_sgpio_irq_handler()`.

## Control flow
Probe maps MMIO, retrieves SoC clock configuration from OF match data, reads `nuvoton,input-ngpios` and `nuvoton,output-ngpios`, validates each against 64, gets the peripheral clock, selects a shift-clock divisor, initializes the GPIO callbacks, programs port counts in `IOXCFG2`, sets up interrupts, registers the chip, and enables periodic SGPIO scanning. Output offsets access `WRITE_DATA`; input offsets subtract `nout_sgpio` and access `READ_DATA`.

IRQ setup disables the SGPIO engine, clears event config/status for all banks, installs a valid mask covering only the input range, and chains the parent IRQ. Type programming converts rising/falling/both and level high/low to the hardware two-bit event configuration, selects Linux level or edge handling, disables the engine while writing event config, and re-enables it afterward.

## State and persistence behavior
Persistent runtime state includes configured input/output counts, port counts, chosen clock divisor, and `int_type[]` for each hardware input. No suspend/resume context save exists in this file, so register state is assumed retained or reset by platform lifecycle. Event masks are hardware state, with status cleared during mask changes and acknowledgements.

## Dependencies and integration points
The driver depends on platform MMIO resources, OF compatibles `nuvoton,npcm750-sgpio` and `nuvoton,npcm845-sgpio`, peripheral clock rates, gpiolib IRQ valid masks, chained IRQs, and raw spinlocks. It integrates with board DT through the input/output GPIO count properties.

## Risks and edge cases
Offsets in IRQ callbacks are child hwirqs in the combined GPIO namespace, so subtracting `nout_sgpio` is critical. `npcm_sgpio_set_type()` ORs new type bits into `EVENT_CFG` instead of clearing the old two-bit field first, while mask/unmask clears when masking; repeated type changes can retain stale bits unless masked first. Clock selection returns `-EINVAL` if no divisor yields the target relation, making probe sensitive to APB clock rate. GPIO output writes are not lock-protected, while IRQ config writes are.

## Test signals
Validate DT count parsing, port count register readback, shift-clock setup on NPCM750 and NPCM845, output set/get on low offsets, input get on high offsets, IRQ valid-mask exclusion of outputs, rising/falling/both event delivery, and status clearing across mask/ack paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-npcm-sgpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-octeon.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-octeon.c

## Purpose
`gpio-octeon.c` is a small GPIO driver for Cavium OCTEON GPIO registers. It exposes 20 non-sleeping GPIO lines with input/output direction, value readback, and dedicated set/clear writes.

## Important APIs, types, and functions
`struct octeon_gpio` contains the `gpio_chip` and a CSR base address. `bit_cfg_reg()` calculates the per-line configuration register offset, including the hardware discontinuity after GPIO 15. GPIO callbacks are `octeon_gpio_dir_in()`, `octeon_gpio_dir_out()`, `octeon_gpio_get()`, and `octeon_gpio_set()`. Probe maps the platform resource, initializes a fixed-base 20-line chip, and registers it.

## Control flow
Input direction writes zero to the line configuration CSR. Output direction first writes the requested level through `TX_SET` or `TX_CLEAR`, then enables transmit output by writing `tx_oe = 1` to the line config register. Reads use the `RX_DAT` CSR; writes use a 64-bit bit mask to the set or clear CSR.

## State and persistence behavior
There is no software shadow state and no suspend/resume logic. Direction and output levels are entirely hardware-resident. The driver sets `chip->base = 0`, so it uses a fixed legacy GPIO base rather than dynamic numbering.

## Dependencies and integration points
The driver depends on platform MMIO resources, OF compatible `cavium,octeon-3860-gpio`, gpiolib, OCTEON CSR helpers (`cvmx_read_csr()` and `cvmx_write_csr()`), and the OCTEON GPIO CSR definitions.

## Risks and edge cases
The MMIO pointer is cast to `u64` and then used as a CSR base, which is architecture-specific. The fixed global base can conflict with other GPIO providers on mixed systems. No IRQ support, pin configuration, or context restore is provided. The 20-line count is hard-coded.

## Test signals
Useful checks are probe on the compatible DT node, correct config register offsets for lines below and above 16, output-before-direction behavior, reads from `RX_DAT`, and no regressions in fixed GPIO numbering on OCTEON boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-omap.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-omap.c

## Purpose
`gpio-omap.c` is the main GPIO bank driver for OMAP2/3/4 and MPUIO-style GPIO controllers. It provides GPIO direction/value operations, debounce, IRQ type/mask/wake support, runtime PM, CPU cluster PM handling, context save/restore, and silicon-erratum workarounds for lost non-wakeup edge interrupts.

## Important APIs, types, and functions
`struct gpio_bank` is the central state object: MMIO base, register layout, IRQ number, non-wakeup masks, saved context, raw locks, `gpio_chip`, debounce clock, PM flags, usage masks, context-loss tracking, and dataout setter. Register context is represented by `struct gpio_regs`. Major helpers include `omap_set_gpio_direction()`, `omap_set_gpio_triggering()`, `omap_set_gpio_irqenable()`, `omap_gpio_irq_handler()`, GPIO request/free/get/set paths, `omap2_set_gpio_debounce()`, `omap_gpio_idle()`, `omap_gpio_unidle()`, `gpio_omap_cpu_notifier()`, and probe/remove/runtime PM functions.

## Control flow
Probe selects platform data from OF or legacy pdata, maps the bank, gets an optional debounce clock, enables runtime PM, initializes hardware interrupt and debounce state, registers a GPIO chip and irqchip, requests the parent bank IRQ, prints revision once, registers a CPU PM notifier, and releases the runtime PM reference. GPIO request/free track `mod_usage` separately from `irq_usage`; the module is only idled when neither is using the line. Direction and output writes update saved context under the bank lock.

IRQ type programming validates supported senses, configures level and edge detect registers, forces IRQ lines to input, tracks both-edge/toggle cases for old IRQCTRL hardware, and selects level or simple IRQ flow. The bank IRQ handler repeatedly reads enabled pending status, clears edge IRQs before child dispatch, toggles edge programming for hardware that cannot detect both edges simultaneously, and dispatches child IRQs under a workaround lock.

## State and persistence behavior
The driver maintains extensive context: direction, dataout, irqenable, wake, detect registers, debounce registers, saved datain, enabled non-wakeup GPIOs, usage masks, and context-loss count. Runtime suspend and CPU cluster enter call `omap_gpio_idle()` to save datain, apply erratum workarounds, update context-loss counters, and disable debounce clocks. Resume restores context if hardware lost it and synthesizes IRQs for non-wakeup GPIOs whose input changed while context was unavailable.

## Dependencies and integration points
It depends on OMAP platform data/register definitions, OF compatibles `ti,omap2-gpio`, `ti,omap3-gpio`, and `ti,omap4-gpio`, runtime PM, CPU PM notifiers, syscore-like MPUIO device registration, gpiolib, IRQ domains, pinctrl generic config for bias, and optional debounce clocks.

## Risks and edge cases
This file is sensitive to register-layout differences and inverted enable semantics. Debounce requires clock ordering: debounce must be disabled before its clock is cut. Non-wakeup edge synthesis is explicitly racy but needed for silicon behavior. Incorrect usage-mask accounting can idle a bank while GPIO or IRQ users still need it. Level IRQs require different clear ordering than edge IRQs. Context restore must honor context-loss counters to avoid unnecessary writes while still restoring after OFF/RET loss.

## Test signals
High-value tests include GPIO request/free runtime PM balancing, direction/value and set_multiple behavior, debounce conversion and rejection, IRQ type validation for each SoC layout, wake enable wiring, nested IRQ delivery under repeated pending status, suspend/resume context restore after forced context loss, and synthetic IRQ generation for non-wakeup edge lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-palmas.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-palmas.c

## Purpose
`gpio-palmas.c` exposes GPIO lines from TI Palmas-family PMICs. It supports 8-line Palmas/TPS65913/TPS65914 devices and 16-line TPS80036 devices, providing sleeping GPIO operations and mapping PMIC GPIO interrupt numbers to Linux IRQs through the parent MFD.

## Important APIs, types, and functions
`struct palmas_gpio` stores the child `gpio_chip` and parent `struct palmas`. `struct palmas_device_data` provides `ngpio`. GPIO callbacks are `palmas_gpio_get()`, `palmas_gpio_set()`, `palmas_gpio_output()`, `palmas_gpio_input()`, and `palmas_gpio_to_irq()`. Probe reads OF match data, honors legacy `palmas_platform_data.gpio_base`, fills the chip, and registers it with devm.

## Control flow
The driver selects first or second GPIO register bank based on `offset / 8`, then uses `offset % 8` within that bank. `get()` reads the direction register to decide whether to read DATA_OUT or DATA_IN. `set()` writes to dedicated set or clear output registers. `direction_output()` sets the initial level before marking the direction bit as output. `direction_input()` clears the direction bit.

## State and persistence behavior
No software shadow state is maintained. Direction, output, and input state live in parent PMIC registers. No suspend/resume hook is provided in this child driver; PMIC register retention or parent MFD handling determines persistence.

## Dependencies and integration points
The driver depends on the Palmas MFD APIs (`palmas_read()`, `palmas_write()`, `palmas_update_bits()`, and `palmas_irq_get_virq()`), platform child device creation, OF compatibles for the PMIC variants, and gpiolib. The chip is `can_sleep = true` because all operations go through the PMIC bus.

## Risks and edge cases
Banked offset handling must be correct for 16-line TPS80036 parts. `palmas_gpio_output()` calls `palmas_gpio_set()` after reducing `offset %= 8`, so the callee recomputes bank zero for offsets in the second bank; that is a subtle bug risk for GPIOs 8-15 because the original bank information is lost. IRQ mapping assumes contiguous parent PMIC IRQ numbers starting at `PALMAS_GPIO_0_IRQ`.

## Test signals
Test both 8- and 16-GPIO variants, especially direction/output/get on GPIOs 8-15 for TPS80036. Verify set/clear register selection, `to_irq()` mappings, legacy base handling, and error propagation from parent PMIC register reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-palmas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca953x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca953x.c

## Purpose
`gpio-pca953x.c` is a broad I2C GPIO expander driver for PCA953x/PCA957x/PCAL/TCA/Maxim/OnSemi-compatible devices from 4 to 40 lines. It provides GPIO direction/value operations, multi-line access, optional PCAL pull configuration, optional interrupt handling, reset GPIO support, regulator power management, ACPI quirks, and suspend/resume regcache restoration.

## Important APIs, types, and functions
`struct pca953x_chip` stores locks, regmap, IRQ bitmaps, wake counter, client, gpio chip, encoded driver data, regulator, register layout, address recalculation, and register-validity callbacks. Register models are represented by `struct pca953x_reg_config`. Key functions include register validators, `pca953x_recalc_addr()`, `pcal6534_recalc_addr()`, `tca6418_recalc_addr()`, `pca953x_read_regs()`, `pca953x_write_regs()`, GPIO direction/get/set/multiple/config callbacks, IRQ setup and pending detection, device initialization, probe, and PM save/restore.

## Control flow
Probe derives encoded match data, enables `vcc`, sets up the GPIO chip, chooses auto-increment regmap mode for larger/PCA957x parts, installs address and register-check callbacks, initializes regmap cache and `i2c_lock`, selects the register layout, initializes device registers, sets up IRQs if compiled and available, and registers the chip. GPIO operations use `i2c_lock` around regmap access and handle special TCA6418 bit order and inverted direction semantics.

IRQ setup snapshots input state masked by direction, creates a threaded parent IRQ, and uses software edge/level bitmaps. The IRQ handler reads PCAL interrupt status before input registers where available, filters by requested rising/falling/level type, updates `irq_stat`, and dispatches nested IRQs. Bus sync writes PCAL latch and interrupt mask registers and forces interrupt lines to input if needed.

## State and persistence behavior
Regmap cache holds output, direction, polarity, pull, latch, and interrupt mask state. IRQ state is maintained in bitmaps for mask, previous input status, requested edge/level types, and wakeup path count. Suspend disables the parent IRQ, switches regmap to cache-only, and disables the regulator unless the device is a wake path. Resume re-enables power, disables cache-only mode, marks cache dirty, syncs direction before output and then the rest of the cache.

## Dependencies and integration points
The driver integrates with I2C, regmap, regulators, GPIO reset lines, ACPI/DMI quirks, OF and ACPI match tables, optional IRQ support, pinconf generic bias parameters, and gpiolib. It registers at `subsys_initcall()` so expanders are available before consumers that rely on early GPIOs.

## Risks and edge cases
The supported chip matrix is complex. PCAL6534 address compaction, TCA6418 reversed bits and inverted direction, and PCAL latched IRQ status are all high-risk areas. Shared I2C mux scenarios require lockdep subclassing but the comment admits it is incomplete. IRQ emulation depends on previous input snapshots, so missed reads or output/input direction changes can affect edge detection. PM restore ordering is critical to avoid output glitches.

## Test signals
Use regmap-backed tests or hardware smoke tests for each register model: PCA953x, PCA957x, PCAL6524/6534, and TCA6418. Verify direction/output ordering, get/set_multiple, PCAL pull configs, ACPI Galileo IRQ quirk, IRQ edge/level behavior including short PCAL pulses, suspend/resume with regulator off, and no output glitches after regcache sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca953x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca9570.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca9570.c

## Purpose
`gpio-pca9570.c` drives simple I2C GPO-only expanders PCA9570, PCA9571, and Dialog/Renesas SLG7XL45106. It exposes all pins as outputs, supports reading current output state, and keeps a software latch for safe read-modify-write output updates.

## Important APIs, types, and functions
`struct pca9570_chip_data` stores line count and optional command/register byte. `struct pca9570` stores the `gpio_chip`, selected chip data, mutex, and cached output byte. `pca9570_read()` and `pca9570_write()` choose SMBus byte or byte-data access depending on the command. GPIO callbacks are `pca9570_get_direction()`, `pca9570_get()`, and `pca9570_set()`.

## Control flow
Probe allocates state, fills a sleeping dynamic-base GPIO chip, obtains match data, initializes the mutex, reads the current output byte into `out`, stores client data, and registers the chip. `set()` locks, updates the software `out` byte, writes it to the device, and only commits the cache after a successful write. `get()` reads the device directly.

## State and persistence behavior
The only persistent software state is `gpio->out`, mirroring the last known output byte. Probe tries to seed it from hardware but ignores read failure, leaving zero-initialized state if the read fails. No PM hooks are implemented.

## Dependencies and integration points
The driver depends on I2C/SMBus transactions, OF and I2C ID match data, gpiolib, and devm-managed mutex/GPIO registration. All operations can sleep.

## Risks and edge cases
Ignoring the initial read failure can cause the first set operation to overwrite unknown output bits with zeros. The driver provides no `direction_output()` callback, only `set()` and fixed output direction, so consumers expecting explicit direction changes rely on gpiolib behavior for output-only chips. Only one byte is supported.

## Test signals
Verify PCA9570/PCA9571 byte access and SLG7XL45106 command-register access, fixed output direction reporting, cache preservation across single-bit updates, behavior after initial read failure, and error propagation from SMBus writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca9570.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcf857x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcf857x.c

## Purpose
`gpio-pcf857x.c` supports PCF857x/PCA857x/PCA967x/MAX7328/MAX7329 I2C quasi-bidirectional GPIO expanders. These chips have one read and one write latch, so the driver models input direction by writing a high bit and maintains a software output latch.

## Important APIs, types, and functions
`struct pcf857x` stores the chip, client, latch mutex, software `out`, current `status`, enabled IRQ bitmap, and 8- or 16-bit read/write function pointers. GPIO callbacks are `pcf857x_input()`, `pcf857x_output()`, `pcf857x_get()`, `pcf857x_get_multiple()`, `pcf857x_set()`, and `pcf857x_set_multiple()`. Optional IRQ support uses `pcf857x_irq()`, enable/disable callbacks, wake forwarding, and bus lock/unlock.

## Control flow
Probe chooses 8-bit SMBus or 16-bit I2C transfer helpers based on match data, optionally resets the chip, reads `lines-initial-states` when no reset GPIO is present, verifies the device by reading it, initializes `out = ~n_latch`, snapshots `status`, optionally requests a falling-edge threaded shared parent IRQ, wires an IRQ chip, and registers the GPIO chip. Direction input sets the latch bit high; output writes the requested latch bit.

The parent IRQ reads current status, computes changed enabled bits against the previous status under the mutex, updates status, and dispatches nested IRQs for changed lines. There is no hardware per-line mask; IRQ enable state is software-filtered.

## State and persistence behavior
The latch `out` is the key persistent software state because hardware cannot report the output latch separately from pin level. `status` holds the previous input sample for change detection. On shutdown, the driver writes all lines high. No suspend/resume context handling exists.

## Dependencies and integration points
The driver depends on I2C functionality checks, optional reset GPIOs, DT `lines-initial-states`, gpiolib, optional parent IRQs, and nested IRQ domains. Registration occurs at `subsys_initcall()` for early availability.

## Risks and edge cases
Quasi-bidirectional semantics mean direction cannot be known independently; explicit setup is needed to avoid glitches. IRQs are change-based and software-filtered, so changes while disabled or between reads can be missed or coalesced. The parent IRQ is requested with falling-edge trigger regardless of child line type because the expander only signals a generic change. Initial latch assumptions are critical when no reset is performed.

## Test signals
Test 8- and 16-bit devices, reset GPIO timing, `lines-initial-states`, direction-input high-latch behavior, get/set_multiple, shutdown high write, IRQ change detection for enabled lines only, and wake forwarding to the I2C client IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcf857x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pch.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pch.c

## Purpose
`gpio-pch.c` supports Intel EG20T and ROHM/LAPIS ML7223 PCH/IOH PCI GPIO blocks. It provides MMIO GPIO direction/value operations, per-line IRQs through generic IRQ chips, and suspend/resume register save/restore.

## Important APIs, types, and functions
`struct pch_regs` maps hardware registers. `struct pch_gpio` stores MMIO base, register pointer, device, gpio chip, saved register context, allocated IRQ base, device type, and spinlock. GPIO callbacks include `pch_gpio_direction_input()`, `pch_gpio_direction_output()`, `pch_gpio_get()`, `pch_gpio_set()`, and `pch_gpio_to_irq()`. IRQ callbacks are `pch_irq_type()`, `pch_irq_mask()`, `pch_irq_unmask()`, `pch_irq_ack()`, and `pch_gpio_handler()`.

## Control flow
Probe enables the PCI device, maps BAR 1, selects the GPIO count by PCI ID, registers the GPIO chip, allocates Linux IRQ descriptors, masks and enables hardware interrupts, requests the shared PCI IRQ, and creates a generic IRQ chip. GPIO direction output writes PO first then sets the PM direction bit; direction input clears the PM bit. IRQ type programming writes four-bit mode fields in `im0` or `im1` and installs level or edge handlers.

## State and persistence behavior
The driver saves `ien`, `imask`, `po`, `pm`, `im0`, optional `im1`, and optional `gpio_use_sel` on suspend. Resume pulses the reset register and restores saved context. Runtime GPIO state is otherwise hardware-resident.

## Dependencies and integration points
It depends on PCI managed enable/iomap helpers, generic IRQ chip allocation, gpiolib, MMIO accessors, and simple PM ops. Supported IDs cover Intel EG20T and ROHM ML7223m/n variants with different pin counts and saved registers.

## Risks and edge cases
`to_irq()` returns `irq_base + offset`; if IRQ descriptor allocation fails, `irq_base` is set to `-1` after the GPIO chip has already been registered, making `to_irq()` invalid. IRQ mode programming returns 0 for unsupported types instead of `-EINVAL`. Register masks assume `BIT(gpio_pins) - 1`, so pin counts must stay below word width. Restore after reset must preserve device-specific `gpio_use_sel` for ML7223n.

## Test signals
Validate probe on each PCI ID, GPIO count, direction/value operations, allocated IRQ mappings, all supported IRQ trigger modes, suspend/resume register restoration, and the no-IRQ-descriptor path so consumers do not receive bogus IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pci-idio-16.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pci-idio-16.c

## Purpose
`gpio-pci-idio-16.c` is a PCI wrapper for ACCES PCI-IDIO-16 boards. It maps the board I/O registers into a regmap, describes readable/writeable/precious ranges, defines input-line IRQs, and delegates GPIO registration to the shared `gpio-idio-16` helper.

## Important APIs, types, and functions
The file defines `idio_16_regmap_config` with 8-bit I/O-port registers, flat cache, volatile read ranges, and a precious interrupt/status register. `idio_16_regmap_irqs[]` defines IRQs only for GPIOs 16-31, each supporting both edges through the shared status bit. `idio_16_probe()` enables PCI, maps BAR 2, initializes regmap, fills `struct idio_16_regmap_config`, and calls `devm_idio_16_regmap_register()`.

## Control flow
Probe is linear: enable device, map I/O BAR, create regmap, populate helper config with parent device, map, regmap IRQ table, parent PCI IRQ, and `filters = true`, then hand off to the helper. GPIO semantics are not open-coded here; they are determined by `gpio-idio-16.h` and its implementation.

## State and persistence behavior
No local mutable state persists beyond regmap and helper-owned state. Regmap cache is flat, while input/status ranges are volatile and the status register is precious to avoid accidental reads clearing or consuming hardware state.

## Dependencies and integration points
The driver depends on PCI vendor/device `0x494F:0x0DC8`, managed PCI I/O mapping, regmap MMIO over I/O ports, regmap IRQ support through the helper, and namespace import `GPIO_IDIO_16`.

## Risks and edge cases
Correctness depends heavily on the shared IDIO-16 helper and the accuracy of register access tables. Only input lines can interrupt; output-line IRQ requests must be rejected by the helper. The precious register declaration is important because generic debug or cache reads could otherwise disturb interrupt state.

## Test signals
Probe should confirm BAR 2 mapping, regmap range enforcement, registration of the expected 32 GPIOs by the helper, output/input direction semantics from the helper, and both-edge IRQ delivery only on GPIOs 16-31 with filter handling enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pci-idio-16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcie-idio-24.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcie-idio-24.c

## Purpose
`gpio-pcie-idio-24.c` supports the ACCES PCIe-IDIO-24 family, including 24 FET outputs, 24 isolated inputs, and 8 TTL/CMOS configurable lines. It uses `gpio-regmap` for GPIO operations and `regmap_irq` for change-of-state interrupts.

## Important APIs, types, and functions
`struct idio_24_gpio` stores the device regmap, raw spinlock, and cached COS IRQ type bits. Two regmap configs describe the PLX PEX8311 interrupt CSR and the board registers. `idio_24_regmap_irqs[]` maps 24 isolated inputs and 8 TTL lines to COS status registers. `idio_24_handle_mask_sync()` updates hardware COS enable bits when regmap IRQ masks change, `idio_24_set_type_config()` handles rising/falling/both selection, and `idio_24_reg_mask_xlate()` maps GPIO offsets to data, set, and direction registers.

## Control flow
Probe enables PCI, maps the PLX BAR and board BAR, creates both regmaps, initializes all IRQ types to both edges, constructs a `regmap_irq_chip`, soft-resets the board, enables PLX internal/local interrupt forwarding, registers the regmap IRQ chip on the PCI IRQ, then registers a 56-line gpio-regmap chip using the regmap IRQ domain. Offsets 0-23 are FET outputs, 24-47 isolated inputs, and 48-55 TTL/CMOS lines whose data register depends on the output-mode control bit.

## State and persistence behavior
Runtime state is mostly hardware/regmap state plus `irq_type`, an 8-bit cache for COS edge enable bits per status register. There is no suspend/resume hook; reset is performed at probe. GPIO direction is configurable only for TTL/CMOS lines through `CONTROL_REG_OUT_MODE`.

## Dependencies and integration points
The driver depends on PCI managed resources, regmap over I/O-port MMIO, `gpio-regmap`, `regmap_irq`, and the PLX PEX8311 interrupt-control register. It supports several ACCES PCI IDs in the same family.

## Risks and edge cases
The TTL direction bit controls the whole TTL/CMOS group rather than individual lines, but gpio-regmap exposes direction per offset; consumers may assume finer granularity than hardware provides. `irq_type` is shared by register offset groups and protected by a raw spinlock. Correct COS masking relies on custom regmap_irq callbacks distinguishing all-masked versus enabled states. A failed PLX interrupt enable leaves GPIO usable but no interrupt path.

## Test signals
Validate all supported PCI IDs, board soft reset, PLX interrupt enable bits, fixed names and 56-line layout, FET output writes, isolated input reads, TTL group direction/data switching, regmap IRQ domain mapping for inputs/TTL lines, and rising/falling/both COS configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcie-idio-24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pisosr.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pisosr.c

## Purpose
`gpio-pisosr.c` exposes SPI-compatible parallel-in serial-out shift registers as input-only GPIO chips. It optionally toggles a load GPIO before reading, then shifts the captured input state over SPI.

## Important APIs, types, and functions
`struct pisosr_gpio` stores the chip, SPI device, read buffer, buffer size, optional load GPIO, and mutex. `pisosr_gpio_refresh()` performs the optional load pulse and SPI read. GPIO callbacks are fixed input direction, `pisosr_gpio_get()`, and `pisosr_gpio_get_multiple()`. `template_chip` defines the default 8-line sleeping input-only chip.

## Control flow
Probe copies the template, sets the parent, optionally reads `ngpios`, allocates a byte buffer sized for the line count, gets an optional `load` GPIO initialized low, initializes the mutex, and registers the chip. Each get refreshes the whole shift register before returning the requested bit. `get_multiple()` refreshes once, then copies selected clumps from the buffer into the bitmap result.

## State and persistence behavior
The buffer stores only the most recent SPI sample and is overwritten on each refresh. There is no output or direction state and no suspend/resume handling. The optional load GPIO state is pulsed high then low for each sample.

## Dependencies and integration points
The driver depends on SPI, optional GPIO consumer `load`, DT compatible `pisosr-gpio`, gpiolib, and sleeping GPIO semantics. It can represent arbitrary `ngpios`, rounded to whole bytes for SPI reads.

## Risks and edge cases
`pisosr_gpio_get()` ignores the return value from `pisosr_gpio_refresh()`, so SPI read failures can return stale buffer data. Bit order is assumed to match the register chain's byte/bit order. The load pulse delays are fixed microsecond delays despite comments describing nanosecond hardware timings. Partial final bytes are not masked beyond `ngpio` except by gpiolib callers' offsets/masks.

## Test signals
Verify configurable `ngpios`, buffer sizing, optional load pulse timing, SPI read length, get/get_multiple bit order, stale-data behavior on SPI failure, and input-only direction handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pisosr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pl061.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pl061.c

## Purpose
`gpio-pl061.c` supports the ARM PrimeCell PL061 8-bit GPIO block on AMBA. It provides GPIO direction/value operations, chained parent IRQ handling with edge/level configuration, wake forwarding, and suspend/resume context save/restore.

## Important APIs, types, and functions
`struct pl061` stores the raw lock, MMIO base, gpio chip, parent IRQ, and saved context registers. GPIO callbacks are `pl061_get_direction()`, `pl061_direction_input()`, `pl061_direction_output()`, `pl061_get_value()`, and `pl061_set_value()`. IRQ support is handled by `pl061_irq_type()`, `pl061_irq_handler()`, mask/unmask/ack/wake callbacks, and immutable `pl061_irq_chip`. Probe binds through AMBA ID `0x00041061`.

## Control flow
Probe maps the AMBA resource, initializes GPIO callbacks, disables interrupts, sets up a chained GPIO irqchip with the AMBA IRQ as parent, registers the chip, and stores drvdata. Output direction writes the value, sets the direction bit, then writes the value again because PL061 cannot reliably set output data before output mode is enabled. IRQ type programming edits `GPIOIS`, `GPIOIBE`, and `GPIOIEV` to select level, both-edge, or single-edge behavior and changes the Linux flow handler accordingly.

## State and persistence behavior
Suspend saves direction, interrupt sense, both-edge, event, enable, and output data for lines configured as outputs. Resume restores each line's direction/value first, then restores IRQ configuration registers. No runtime PM is present.

## Dependencies and integration points
The driver depends on the AMBA bus, gpiolib, chained IRQ helpers, raw spinlocks, optional pinctrl generic request/free, and simple PM ops. Wake is forwarded to the parent IRQ with `irq_set_irq_wake()`.

## Risks and edge cases
Probe warns when AMBA IRQ 0 is absent but still configures one parent IRQ entry with that value, so no-IRQ platforms need careful behavior checks. `pl061_irq_type()` rejects mixed level and edge requests but allows no-trigger configuration by installing `handle_bad_irq`. Output restore calls direction operations and may briefly rewrite values. All data registers use PL061 masked-address semantics via `base + BIT(offset + 2)`.

## Test signals
Validate masked data register addressing, output double-write behavior, all IRQ trigger modes, chained dispatch from `GPIOMIS`, ack only for edge IRQs, wake forwarding, and suspend/resume preserving output values and IRQ registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pl061.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pmic-eic-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pmic-eic-sprd.c

## Purpose
`gpio-pmic-eic-sprd.c` exposes the Spreadtrum/Unisoc PMIC EIC block as 16 input-only GPIOs with debounce and IRQ support. The hardware is fundamentally level-triggered, so the driver emulates edge behavior by changing the programmed active level after each interrupt.

## Important APIs, types, and functions
`struct sprd_pmic_eic` stores the chip, parent regmap, register offset, cached IEV/IE/TRIG bytes, buslock mutex, and parent IRQ. Helpers `sprd_pmic_eic_update()` and `sprd_pmic_eic_read()` access parent PMIC registers. GPIO callbacks request/free data mask bits, fixed input direction, get, and input debounce config. IRQ callbacks include mask/unmask, set_type, bus_lock/sync_unlock, `sprd_pmic_eic_toggle_trigger()`, and threaded `sprd_pmic_eic_irq_handler()`.

## Control flow
Probe gets the parent IRQ, parent regmap, DT `reg` offset, requests a no-suspend threaded IRQ, fills the 16-line sleeping input-only gpio chip, installs a threaded immutable irqchip, and registers it. Request/free toggles `DMSK`. Debounce writes per-line `CTRL0 + line * 4` using milliseconds from the pinconf microsecond argument. IRQ sync programs active level, enable, and trigger pulse from cached state; for edge-both it samples the current level and arms the opposite level.

## State and persistence behavior
The cached `reg[]` array stores desired interrupt polarity, enable, and trigger bits while under irq bus lock. Hardware registers hold data mask, debounce, active level, enable, status, clear, and trigger pulse state. There is no suspend/resume context restore in this file, but the IRQ is requested with `IRQF_NO_SUSPEND`.

## Dependencies and integration points
The driver depends on a parent PMIC regmap, platform IRQ, OF compatible `sprd,sc2731-eic`, gpiolib nested threaded IRQs, pinconf debounce, and PMIC register layout from the `reg` DT property.

## Risks and edge cases
Edge emulation is race-prone: the line can change between sampling and reprogramming, so the driver retries if the post-program state differs. Debounce conversion truncates microseconds to milliseconds and masks to 12 bits. `sprd_pmic_eic_irq_handler()` returns `IRQ_RETVAL(ret)` on regmap read failure, which maps negative errors oddly for IRQ return semantics. Wake is skipped by irqchip flags.

## Test signals
Verify input-only GPIO requests toggle `DMSK`, debounce register programming, level-high/low IRQs, rising/falling/both edge emulation across rapid level changes, interrupt clear writes, trigger pulse writes, and no-suspend behavior through system sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pmic-eic-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pxa.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pxa.c

## Purpose
`gpio-pxa.c` provides GPIO support for Intel/Marvell PXA and MMP SoCs. It manages banked MMIO GPIO registers, pinctrl handoff for older PXA variants, direct IRQs for GPIO0/GPIO1, muxed IRQ demultiplexing for all lines, wake forwarding, OF/legacy platform registration, and syscore suspend/resume.

## Important APIs, types, and functions
`struct pxa_gpio_chip` stores the device, gpiolib chip, bank array, irqdomain, direct IRQs, and platform wake callback. `struct pxa_gpio_bank` stores register base, IRQ mask and edge masks, plus PM saved registers. Key functions include `pxa_init_gpio_chip()`, `pxa_gpio_direction_input()`, `pxa_gpio_direction_output()`, `pxa_gpio_get()`, `pxa_gpio_set()`, `pxa_gpio_irq_type()`, `pxa_gpio_demux_handler()`, direct handler, mask/unmask/ack callbacks, `pxa_gpio_probe()`, DT/legacy initcalls, and syscore PM operations.

## Control flow
Probe determines the SoC type and GPIO count from legacy platform data or OF match data, creates a legacy irqdomain with preallocated IRQ descriptors, validates direct and mux IRQ resources, maps registers, enables the clock, registers the GPIO chip, clears all edge-detect registers/status, unmasks MMP AP-side edge detection where needed, requests direct GPIO0/GPIO1 IRQs if present, requests the mux IRQ, and stores the global chip pointer. Direction output writes set/clear first, calls pinctrl direction when applicable, then updates GPDR with inverted semantics for PXA26x GPIO86-89.

IRQ type programming forces the line to input, updates per-bank rising/falling masks, and writes GRER/GFER only for unmasked IRQs. The mux handler loops until no banks have pending enabled GEDR bits, clears detected bits, and dispatches child domain IRQs. Direct handler maps parent IRQs to child GPIO0/1.

## State and persistence behavior
Global state includes `pxa_last_gpio`, `irq_base`, `pxa_gpio_chip`, and `gpio_type`. Each bank tracks IRQ masks and edge polarity masks; PM builds also save GPLR, GPDR, GRER, and GFER. Syscore suspend saves registers and clears transition detect bits. Resume restores output levels via GPSR/GPCR, then restores edge and direction registers.

## Dependencies and integration points
The driver depends on platform devices, OF compatibles for PXA/MMP variants, legacy platform data, clocks, pinctrl direction helpers for PXA variants that need them, irqdomain legacy mapping, gpiolib, and syscore PM. It registers differently for DT and non-DT boots using postcore/device initcalls.

## Risks and edge cases
Several globals make the driver effectively singleton. PXA26x inverted GPIOs and occupied alternate-function checks are subtle. IRQ probe type avoids disturbing occupied or already configured lines. MMP AP-side edge mask handling is SoC-specific. Syscore resume writes `~saved_gplr` to GPCR, so register width and bank mask assumptions matter. Probe returns `-EINVAL` for several missing IRQ combinations, which can make partial hardware descriptions fail.

## Test signals
Test each SoC match count, DT and legacy init paths, PXA26x inverted GPIOs, pinctrl handoff, direct GPIO0/1 IRQs, mux IRQ looping under multiple banks, edge type changes, wake callback forwarding, MMP edge mask writes, and syscore suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pxa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-qixis-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-qixis-fpga.c

## Purpose
`gpio-qixis-fpga.c` exposes selected NXP Layerscape QIXIS FPGA/CPLD registers as 8-bit GPIO chips using `gpio-regmap`. It supports board-specific fixed-output masks, with all other lines treated as input-only/status-style bits.

## Important APIs, types, and functions
`struct qixis_cpld_gpio_config` stores a bitmask of output-capable lines. Two match configs cover LX2160ARDB SFP and LS1046AQDS status/presence registers. Probe reads the register offset from `reg`, obtains a parent regmap or creates an MMIO regmap from its own resource, fills `struct gpio_regmap_config`, converts the output mask to a bitmap, and registers the gpio-regmap chip.

## Control flow
Probe requires a parent device and match data. If the parent already exposes a regmap, the DT `reg` value is used as the gpio-regmap data/set register base. If no parent regmap exists, the driver maps its own MMIO resource, creates an 8-bit regmap, and resets base to zero. `fixed_direction_output` tells gpio-regmap which lines can be driven.

## State and persistence behavior
The driver has no private mutable state after registration. Direction capabilities are fixed by match data, and values are held in the underlying FPGA/CPLD register. No PM handling is present.

## Dependencies and integration points
It depends on platform devices, OF match data, optional parent regmap, optional direct MMIO resource, regmap, and gpio-regmap. It is a thin board-description adapter rather than a custom GPIO implementation.

## Risks and edge cases
The DT `reg` property is mandatory even if an MMIO resource is also present. The local `fixed_direction_output` bitmap is stack-allocated but consumed during registration; correctness depends on gpio-regmap copying or only using it during registration. Incorrect board match data can expose status bits as outputs or prevent driving required control bits.

## Test signals
Verify both compatibles, parent-regmap and fallback-MMIO paths, correct register offset selection, fixed output direction for only configured lines, and read/write behavior through gpio-regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-qixis-fpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-raspberrypi-exp.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-raspberrypi-exp.c

## Purpose
`gpio-raspberrypi-exp.c` exposes the Raspberry Pi firmware-managed expander GPIOs as an 8-line sleeping GPIO chip. Instead of MMIO, it uses Raspberry Pi firmware mailbox property calls for direction, polarity, and state.

## Important APIs, types, and functions
`struct rpi_exp_gpio` stores the chip and firmware handle. Mailbox payloads are `struct gpio_set_config`, `struct gpio_get_config`, and `struct gpio_get_set_state`. GPIO callbacks are `rpi_exp_gpio_dir_in()`, `rpi_exp_gpio_dir_out()`, `rpi_exp_gpio_get_direction()`, `rpi_exp_gpio_get()`, and `rpi_exp_gpio_set()`. `rpi_exp_gpio_get_polarity()` preserves the existing polarity when changing direction.

## Control flow
Probe locates the parent firmware node, obtains an `rpi_firmware` handle, allocates state, fills an 8-line dynamic-base `gpio_chip`, marks it sleeping, and registers it. Direction changes first query existing polarity, then call `RPI_FIRMWARE_SET_GPIO_CONFIG` with GPIO number `128 + offset`. Get/set state use `RPI_FIRMWARE_GET_GPIO_STATE` and `SET_GPIO_STATE`.

## State and persistence behavior
No software state is cached. Direction, polarity, termination, and state are owned by firmware. Each operation performs a synchronous firmware transaction and validates that firmware returns `gpio == 0` to indicate success.

## Dependencies and integration points
The driver depends on the Raspberry Pi firmware interface, platform/OF compatible `raspberrypi,firmware-gpio`, gpiolib, and the parent firmware DT node. It uses the firmware's expander GPIO base of 128 internally, but exposes a local 0-7 chip.

## Risks and edge cases
Every operation can fail due to firmware communication. Direction changes disable termination unconditionally and preserve only polarity. There is no IRQ support. If the firmware protocol changes or returns nonzero status in the `gpio` field, GPIO operations fail with `-EIO`.

## Test signals
Test probe deferral until firmware is available, direction input/output preserving polarity, get/set state mailbox calls, error handling for firmware return codes, and correct local-to-firmware GPIO numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-raspberrypi-exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rc5t583.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rc5t583.c

## Purpose
`gpio-rc5t583.c` exposes GPIOs from the Ricoh RC5T583 PMIC. It provides sleeping GPIO direction/value operations, returns PMIC IRQ numbers for GPIO lines, and returns pins to alternate/PG mode when freed.

## Important APIs, types, and functions
`struct rc5t583_gpio` stores the gpio chip and parent `struct rc5t583`. GPIO callbacks are `rc5t583_gpio_get()`, `rc5t583_gpio_set()`, `rc5t583_gpio_dir_input()`, `rc5t583_gpio_dir_output()`, `rc5t583_gpio_to_irq()`, and `rc5t583_gpio_free()`. Probe obtains parent MFD data and optional platform GPIO base, then registers `RC5T583_MAX_GPIO` lines.

## Control flow
Input reads `RC5T583_GPIO_MON_IOIN`. Set/clear writes `RC5T583_GPIO_IOOUT`. Direction input clears `GPIO_IOSEL` and then clears `GPIO_PGSEL` to force GPIO mode. Direction output writes the initial output value, sets `GPIO_IOSEL`, and clears `GPIO_PGSEL`. Free sets `GPIO_PGSEL`, returning the pin away from GPIO mode. `to_irq()` maps line offsets to parent `irq_base + RC5T583_IRQ_GPIO0 + offset`.

## State and persistence behavior
The driver keeps no shadow state. GPIO mode, direction, and output values are PMIC register state. No suspend/resume handling is implemented locally.

## Dependencies and integration points
It depends on the RC5T583 MFD register helpers, parent platform data for optional legacy base, parent IRQ base, platform child device creation, and gpiolib. Operations can sleep because they go through the PMIC bus.

## Risks and edge cases
The probe uses comma operators while assigning chip fields; it works but is unusual and easy to misread. `to_irq()` assumes a valid parent `irq_base`. Freeing a line changes `PGSEL`, which may surprise consumers if they expect GPIO mode to remain. There is no OF match table in this child driver.

## Test signals
Validate direction and mode register sequences, initial output-before-direction behavior, monitor reads, IRQ number mapping for all valid offsets, free returning pins to PG mode, and legacy GPIO base handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rc5t583.c -->
