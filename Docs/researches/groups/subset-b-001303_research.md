# subset-b-001303 research

This grouped report covers GPIO controller, expander, mock/test, and generic MMIO drivers under `sources/distributed-fs/ceph-client/drivers/gpio/`. Each section is delimited for deterministic splitting into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77759.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77759.c

Purpose: implements the two-line GPIO block exposed by the Maxim MAX77759 MFD. The driver talks to the parent MAXQ mailbox/regmap interface, exposes lines `GPIO5` and `GPIO6` through gpiolib, and maps their edge interrupt status into nested GPIO IRQs.

Important APIs/types/functions: `struct max77759_gpio_chip` holds the parent `struct max77759`, MAXQ regmap, `gpio_chip`, and two mutex-protected software caches for MaxQ GPIO control and IRQ programming. MAXQ helpers `max77759_gpio_maxq_gpio_control_read/write()` and `max77759_gpio_maxq_gpio_trigger_read/write()` issue firmware commands. GPIO callbacks are `max77759_gpio_get_direction()`, `max77759_gpio_direction_input()`, `max77759_gpio_direction_output()`, `max77759_gpio_get_value()`, and `max77759_gpio_set_value()`. IRQ callbacks are in immutable `max77759_gpio_irq_chip`, with mask/unmask/type cached until `max77759_gpio_bus_sync_unlock()`.

Control flow: probe obtains the parent `"maxq"` regmap, named platform IRQ `"GPI"`, parent MFD state, initializes `maxq_lock` and `irq_lock`, fills a sleepable `gpio_chip`, attaches an internal `gpio_irq_chip` with `handle_simple_irq`, registers the chip, then requests a shared threaded IRQ. GPIO get/set operations read the MAXQ GPIO control byte; output direction writes both direction and initial output bit in one read/modify/write. IRQ type selection accepts only rising or falling edge, caches desired trigger bits, and forces the line back to input when the sync-unlock path writes trigger state.

State and persistence behavior: there is no nonvolatile persistence. Runtime state lives in MAXQ control/trigger registers and software shadow fields `irq_mask`, `irq_mask_changed`, `irq_trig`, and `irq_trig_changed`. `maxq_lock` serializes mailbox read/modify/write operations. `irq_lock` covers irqchip bus lock sections so gpiolib mask/type updates are coalesced before touching hardware. The handler loops until the parent UIC status no longer reports GPIO interrupts, acknowledges each line by writing a single bit, and dispatches nested IRQs.

Dependencies and integration points: depends on the MAX77759 MFD headers, parent `dev_get_regmap(..., "maxq")`, `max77759_maxq_command()`, Linux gpiolib, regmap, and nested IRQ mapping. Matching is by OF compatible `maxim,max77759-gpio` and platform id `max77759-gpio`. The driver is sleepable because GPIO operations involve MAXQ mailbox transactions.

Risks: IRQ trigger programming is limited to rising or falling edge; both-edge and level consumers fail with `-EINVAL`. The handler assumes MAXQ UIC bits for GPIO5/6 map to local offsets 0/1, so bit-definition drift would break nested IRQ routing. Errors in bus sync leave changed masks or triggers cached, and the code logs but cannot return an error to the IRQ core from `irq_bus_sync_unlock()`. GPIO state reads rely on the direction bit because MAXQ input status is documented in-code as invalid while the line is configured as output.

Test signals: useful checks are probe with a parent MAX77759 MFD, `gpiod_direction_*()` causing expected MAXQ control writes, output `get()` returning output latch state, rising/falling IRQ type programming forcing input direction, mask/unmask updating `UIC_INT1_M`, and threaded IRQ dispatch acknowledging and delivering only pending GPIO5/GPIO6 nested interrupts. Lockdep should also cover `maxq_lock` assertions in the sync helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77759.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mb86s7x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mb86s7x.c

Purpose: provides a 32-line GPIO controller for Fujitsu MB86S7x/MB86S70 hardware, with optional ACPI interrupt hookup. The controller uses groups of 8 bits spread across PDR, DDR, and PFR register banks.

Important APIs/types/functions: `struct mb86s70_gpio_chip` stores the `gpio_chip`, MMIO base, and spinlock. Register helpers `PDR()`, `DDR()`, `PFR()`, and `OFFSET()` map a GPIO offset to the right 8-bit lane within 32-bit-spaced registers. GPIO callbacks cover request/free, direction, get, set, and `to_irq()`. Probe and remove are `mb86s70_gpio_probe()` and `mb86s70_gpio_remove()`.

Control flow: probe allocates state, maps resource 0, enables an optional clock, initializes the spinlock, fills `gpio_chip` callbacks, registers the chip, then calls `acpi_gpiochip_request_interrupts()`. Request clears the corresponding PFR bit, handing the pin to GPIO mode; free restores that PFR bit. Direction output writes the desired output value into PDR before setting the DDR bit. Direction input clears the DDR bit. `to_irq()` scans platform IRQ resources and returns the IRQ whose irq_data hardware number equals the GPIO offset.

State and persistence behavior: state is hardware-resident in PFR/PDR/DDR. There is no suspend/resume save path; the optional clock is devm-managed and stays enabled while the device is bound. Spinlocks protect read/modify/write sequences on PFR, PDR, and DDR against concurrent gpiolib callers and interrupt context.

Dependencies and integration points: integrates with platform devices, OF compatible `fujitsu,mb86s70-gpio`, ACPI HID `SCX0007`, optional clocks, and `gpiolib-acpi.h` interrupt helpers. The IRQ integration relies on firmware-provided platform IRQs and their `hwirq` values matching GPIO offsets.

Risks: `to_irq()` loops over platform IRQs until `platform_get_irq()` fails; incorrect firmware IRQ metadata can make GPIO-to-IRQ unavailable. `readl()` values are stored in `unsigned char` in several paths, intentionally using only the low 8 bits but losing any unexpected upper-bit state. No PM restore means GPIO mux/direction/value state must survive platform suspend or be restored elsewhere.

Test signals: probe should register 32 GPIOs with dynamic base and set PFR on request/free. Tests should validate output-before-direction ordering, PDR reads for get, ACPI interrupt request/free on bind/unbind, optional clock handling, and `to_irq()` behavior with matching and missing platform IRQ hwirqs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mb86s7x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mc33880.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mc33880.c

Purpose: exposes the Freescale MC33880 high-side/low-side SPI switch as an 8-output GPIO chip. It is a simple output-latch driver with no input, direction, or IRQ support.

Important APIs/types/functions: `struct mc33880` stores a mutex, cached `port_config` byte, `gpio_chip`, and `spi_device`. `mc33880_write_config()` writes the cached byte to SPI, `__mc33880_set()` mutates one bit and writes it, and `mc33880_set()` wraps that with the mutex. Probe and remove are standard SPI driver callbacks.

Control flow: probe requires legacy `struct mc33880_platform_data` with a nonzero `base`, sets `spi->bits_per_word = 8`, runs `spi_setup()`, allocates state, initializes the mutex, assigns a fixed-base sleepable GPIO chip with only `.set`, writes an all-zero configuration twice, and registers the chip. Remove unregisters the GPIO chip and destroys the mutex.

State and persistence behavior: the output latch state is cached in `port_config` and mirrored to the SPI device on every `set`. No suspend/resume hook exists, so cached state is not explicitly replayed after system power loss. The mutex serializes simultaneous SPI updates and protects the byte cache.

Dependencies and integration points: depends on SPI core, legacy `linux/spi/mc33880.h` platform data, and gpiolib. It uses `subsys_initcall()` so the GPIO chip is available before later subsystem users that may rely on board GPIOs.

Risks: no `.get`, `.direction_output`, or `.get_direction` callbacks means consumers mostly use it as an output-only settable GPIO and cannot read back state through normal callbacks. Requiring platform data and fixed `base` limits firmware-description support. The initial double write is needed by the device behavior; a failed SPI write prevents chip registration.

Test signals: board-level or SPI mock tests should verify `bits_per_word` setup, two zero writes during probe, bit updates for offsets 0-7, mutex-serialized concurrent sets, failure on missing platform data, and successful `gpiochip_add_data()` with `can_sleep = true`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mc33880.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-menz127.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-menz127.c

Purpose: provides GPIO support for MEN Mikroelektronik 16Z127-compatible MCB devices, including 16Z127, Z034, and Z037 variants. It builds on the generic MMIO GPIO helper and adds debounce and open-drain/push-pull pin configuration.

Important APIs/types/functions: `struct men_z127_gpio` wraps `gpio_generic_chip`, the MMIO register base, and the MCB memory resource. `men_z127_debounce()` programs debounce enable/count registers. `men_z127_set_single_ended()` controls open-drain enable. `men_z127_set_config()` accepts `PIN_CONFIG_DRIVE_OPEN_DRAIN`, `PIN_CONFIG_DRIVE_PUSH_PULL`, and `PIN_CONFIG_INPUT_DEBOUNCE`. Probe is `men_z127_probe()`.

Control flow: probe allocates state, requests MCB memory, registers a devm action to release it, maps the memory, chooses access size by MCB id (`sz = 4` for 16Z127 and `sz = 1` for Z034/Z037), initializes a generic chip with data, set, and direction-output registers, installs the set_config callback, then registers the gpiochip. Debounce converts microseconds to 50 us register units, clamps at the hardware max, toggles the debounce enable bit, and writes the per-GPIO count register under the generic chip lock.

State and persistence behavior: GPIO data/direction is managed by `gpio_generic_chip` shadow state and the hardware registers. Debounce and open-drain state live in DBER, per-line debounce count registers, and ODER. No PM save/restore is present; MCB resource lifetime is devm-managed with an explicit release action.

Dependencies and integration points: depends on the MCB bus, `gpio-mmio` generic chip helper, pinconf constants, and the `MCB` namespace import. Device matching is through MCB device IDs, not OF or ACPI.

Risks: debounce rounding uses `fls()`-based heuristics and rejects values outside 50 us to `0xffff * 50 us`; edge cases around zero and upper-bound rounding need coverage. Only model IDs with known register width are accepted. There is no IRQ support even though interrupt registers exist in the block definition. PM loss would drop debounce/open-drain configuration.

Test signals: register-width selection by ID, GPIO get/set/direction through the generic helper, debounce enable/disable and count rounding, open-drain versus push-pull ODER writes, error returns for out-of-range debounce and unsupported pinconf parameters, and MCB memory cleanup on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-menz127.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-merrifield.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-merrifield.c

Purpose: binds Intel Merrifield SoC GPIO hardware as a PCI device and delegates the actual GPIO/IRQ implementation to the shared Tangier GPIO core.

Important APIs/types/functions: `MRFLD_NGPIO` defines 192 lines. `mrfld_gpio_ranges[]` maps GPIO offsets to pinctrl pin numbers. `mrfld_gpio_get_pinctrl_dev_name()` locates ACPI device `INTC1002` and returns its name, falling back to `"pinctrl-merrifield"`. `mrfld_gpio_probe()` sets up `struct tng_gpio` and calls `devm_tng_gpio_probe()`.

Control flow: probe enables the PCI device, maps BAR1 to read the firmware-provided IRQ base and GPIO base, unmaps BAR1, allocates `struct tng_gpio`, maps BAR0 for controller registers, fills pin range metadata and base/ngpio/first IRQ info, allocates one PCI IRQ vector, stores wake-register offsets for Merrifield, then calls the Tangier common probe. The PCI driver matches Intel device ID `0x1199`.

State and persistence behavior: this file owns no line state directly; state is held by the Tangier GPIO core and hardware registers. PCI mappings and IRQ vectors are managed by pcim/devm helpers. Pin-range metadata is static and persistent for the device lifetime.

Dependencies and integration points: depends on PCI, ACPI, `gpio-tangier.h`, the `GPIO_TANGIER` namespace, and the Merrifield pinctrl device. It uses ACPI lookup to avoid hard-coding the pinctrl device instance name when firmware exposes one.

Risks: failure to find or duplicate the ACPI pinctrl name falls back to a string, which may not match all firmware. BAR1 is read only for two base values; incorrect BAR layout breaks IRQ/GPIO numbering. Most behavior and risks are in the shared Tangier core, so this wrapper must keep the Merrifield-specific pin range table and wake offsets accurate.

Test signals: PCI probe with valid BAR0/BAR1, correct extraction of `irq_base` and `gpio_base`, successful IRQ vector allocation, pinctrl range registration via the Tangier core, wake-register offset use, and ACPI lookup/fallback behavior for the pinctrl device name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-merrifield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ml-ioh.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ml-ioh.c

Purpose: supports the OKI/Rohm ML-IOH PCI GPIO controller, which exposes eight GPIO channels with different line counts and per-channel interrupt registers.

Important APIs/types/functions: `struct ioh_regs` models the register block, `struct ioh_gpio_reg_data` stores suspend state, and `struct ioh_gpio` is per-channel state with a `gpio_chip`, register base, IRQ base, and spinlock. GPIO callbacks are `ioh_gpio_get()`, `ioh_gpio_set()`, `ioh_gpio_direction_input()`, and `ioh_gpio_direction_output()`. IRQ callbacks include `ioh_irq_type()`, mask/unmask/enable/disable helpers, `ioh_gpio_handler()`, and `ioh_gpio_alloc_generic_chip()`.

Control flow: PCI probe enables the device, maps BAR1, allocates an array of eight `ioh_gpio` structures, initializes each channel's GPIO chip and registers it, then allocates a Linux IRQ range and generic irq_chip for each channel. A shared device IRQ dispatches through `ioh_gpio_handler()`, which scans all eight channels' status registers, clears active bits, and calls `generic_handle_irq()` on `irq_base + line`. Direction output sets the PM bit and writes PO; direction input clears the PM bit. IRQ type programming writes the packed mode fields in IM_0 or IM_1, clears pending status, unmasks, and enables the interrupt.

State and persistence behavior: runtime GPIO state lives in PO/PI/PM and interrupt registers. Suspend saves PO, PM, IEN, IMASK, IM_0, IM_1, and use-select registers for all channels, then resume resets the block via `srst` and restores those registers. Each channel has a spinlock, but suspend locks only the first channel's lock while saving/restoring the whole array.

Dependencies and integration points: integrates with PCI ID `PCI_VENDOR_ID_ROHM, 0x802E`, gpiolib, generic IRQ chips, and the PCI-managed MMIO helpers. `to_irq()` returns the preallocated per-channel Linux IRQ number.

Risks: eight GPIO chips share one MMIO block and parent IRQ; array-pointer arithmetic is used in save/restore and interrupt scanning, so allocation/layout assumptions are important. The interrupt handler calls `generic_handle_irq()` directly from a shared IRQ context. IRQ mode supports rising, falling, both, high, low, and probe but has no explicit validation for channel line bounds beyond generic chip masks. PM locking may not serialize against all per-channel locks.

Test signals: PCI probe should register eight chips with line counts `{6,12,16,16,15,16,16,12}`, allocate irq descriptors for each, program interrupt mode registers for each trigger type, dispatch shared IRQs by status bit, save/restore all channel registers across suspend/resume, and reject/handle probe failures in BAR mapping or IRQ allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ml-ioh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf.c

Purpose: provides GPIO support for first-generation Mellanox/NVIDIA BlueField platforms using a simple 64-bit memory-mapped register model.

Important APIs/types/functions: `struct mlxbf_gpio_state` wraps a `gpio_generic_chip`, MMIO base, and optional PM save area. Register constants cover pin state, input/output direction, scratchpad, and pad control words. `mlxbf_gpio_probe()` initializes the generic chip. `mlxbf_gpio_suspend()` and `mlxbf_gpio_resume()` save and restore scratchpad, four pad-control words, and direction registers when PM is enabled.

Control flow: probe allocates state, maps resource 0, configures `gpio_generic_chip_init()` with 8-byte accesses, data at `PIN_STATE`, output direction at `PIN_DIR_O`, and input direction at `PIN_DIR_I`, sets `ngpio = 54`, registers the chip, and stores drvdata. GPIO operations are handled entirely by the generic MMIO callbacks selected by the helper.

State and persistence behavior: hardware registers hold value and direction. Generic chip initialization snapshots data and direction shadow state. PM suspend stores selected 64-bit registers in `csave_regs`; resume writes them back. There is no IRQ support in this generation.

Dependencies and integration points: depends on platform resources, ACPI HID `MLNXBF02`, `gpio-mmio` generic chip helper, and 64-bit MMIO accessors. The driver is a module platform driver.

Risks: only a fixed set of pad-control registers is saved despite `pad_control[MLXBF_GPIO_NR]` being sized for 54 entries, so the array is larger than actual use. Any GPIO state outside the saved scratchpad/pad/direction registers is not restored. Generic helper constraints mean 8-byte width requires a 64-bit-capable build.

Test signals: ACPI/platform probe, 54-line registration, generic get/set/direction behavior against 64-bit registers, PM save/restore of scratchpad/pad control/direction registers, and no IRQ exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf2.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf2.c

Purpose: supports NVIDIA/Mellanox BlueField-2 YU GPIO blocks, including GPIO value control, protected direction changes through a shared ARM GPIO lock register, optional interrupt support, and sleep PM hooks.

Important APIs/types/functions: `struct mlxbf2_gpio_context` holds a `gpio_generic_chip`, GPIO MMIO base, device pointer, and suspend context pointer. `struct mlxbf2_gpio_param` stores the shared `yu_arm_gpio_lock` mapping and mutex. Lock helpers `mlxbf2_gpio_get_lock_res()`, `mlxbf2_gpio_lock_acquire()`, and `mlxbf2_gpio_lock_release()` serialize protected mode changes. Direction callbacks program `YU_GPIO_MODE0/1` clear/set registers. IRQ callbacks implement enable/disable, type selection, handler, and print-chip.

Control flow: probe maps the GPIO block, maps the global lock resource once, reads optional `npins`, initializes a generic chip with DATAIN/DATASET/DATACLEAR, replaces direction callbacks with BlueField-specific lock-aware versions, optionally requests a shared parent IRQ, registers an immutable nested IRQ chip, then adds the gpiochip. Direction input acquires the global lock and generic chip lock, clears both MODE0 and MODE1 bits, and releases. Direction output clears MODE1 and sets MODE0. The IRQ handler reads cause/event-enable status, clears pending bits, and dispatches domain IRQs.

State and persistence behavior: GPIO data is in hardware data registers; direction mode is in MODE0/MODE1. IRQ desired trigger state is not shadowed except by hardware rise/fall enable registers. Sleep suspend/resume intends to save MODE0/MODE1 in `gs->csave_regs`.

Dependencies and integration points: depends on platform firmware with ACPI HID `MLNXBF22`, `gpio-mmio` generic helper, shared memory resource at `0x2801088`, gpiolib IRQ helpers, and optional `npins` device property for the last partial bank.

Risks: in this snapshot `gs->csave_regs` is dereferenced in suspend/resume but is not allocated in probe, so enabling PM can lead to a null-pointer crash. The lock acquire path returns `-EINVAL` if the hardware lock active bit is already set, which can make direction changes fail under firmware contention. `irq_set_type()` only ever sets requested rise/fall bits and does not clear disabled senses when changing type, so stale hardware enables should be checked. Direction output ignores the requested initial `value`; it only configures mode, relying on the generic output latch path elsewhere.

Test signals: probe on each GPIO block with and without IRQ, global lock mapping reuse across blocks, direction changes failing/succeeding based on lock state, edge IRQ configuration and dispatch, `npins` limiting the last bank, and PM suspend/resume with attention to the missing `csave_regs` allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf3.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf3.c

Purpose: supports NVIDIA BlueField-3 GPIO blocks with separate read, set, clear, output-enable, and interrupt-cause register regions, plus pinctrl range registration.

Important APIs/types/functions: `struct mlxbf3_gpio_context` stores one `gpio_generic_chip` and four mapped register windows: main GPIO, cause, set, and clear. GPIO is handled by `gpio_generic_chip_init()`. IRQ functions are `mlxbf3_gpio_irq_enable()`, `mlxbf3_gpio_irq_disable()`, `mlxbf3_gpio_irq_handler()`, `mlxbf3_gpio_irq_set_type()`, and a no-op ack required by `handle_edge_irq()`. `mlxbf3_gpio_add_pin_ranges()` maps block sizes to pinctrl device `MLNXBF34:00`.

Control flow: probe maps four resources, initializes a generic chip with data input from the main region, set/clear output registers, and output-enable set/clear registers for direction. It installs generic request/free and pin-range callbacks, optionally requests a shared IRQ and creates an internal domain-backed IRQ chip, stores drvdata, and registers the gpiochip. IRQ enable clears stale cause and sets event-enable. IRQ disable clears event-enable and pending cause. IRQ type sets rise/fall enable bits and switches the child handler to `handle_edge_irq`.

State and persistence behavior: output value/direction live in the firmware GPIO set/clear regions. Interrupt enable and pending state live in the cause region. No suspend/resume save path is present. Shutdown disables and clears all interrupts in the cause block.

Dependencies and integration points: depends on ACPI HID `MLNXBF33`, soft dependency on `pinctrl-mlxbf3`, generic MMIO GPIO helper, gpiolib IRQ helpers, and a platform IRQ if interrupt support is present. Pin ranges assume either a 32-line block or a 24-line second block.

Risks: `mlxbf3_gpio_add_pin_ranges()` infers block id from `chip->ngpio`; unexpected firmware `ngpios` values fail pin-range registration. IRQ type programming sets requested senses but does not clear unrequested opposite edges, so type changes can leave stale enable bits. There is no PM restore. Probe logs but returns the result from `devm_gpiochip_add_data()` even after `dev_err_probe()`, so error propagation is direct but the branch is terse.

Test signals: resource mapping order, 32-line and 24-line block pin ranges, generic value/direction operations through set/clear windows, IRQ enable/disable cause clearing, edge type programming, shared parent IRQ dispatch, and shutdown interrupt clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mm-lantiq.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mm-lantiq.c

Purpose: exposes output-only GPIO lines implemented by external latches attached to the Lantiq EBU memory bus.

Important APIs/types/functions: `struct ltq_mm` holds the `gpio_chip`, mapped latch address, and 16-bit shadow latch value. `ltq_mm_apply()` programs EBU timing/write-protect registers and writes the shadow value to the latch under the global `ebu_lock`. `ltq_mm_set()` updates one bit and applies it. `ltq_mm_dir_out()` aliases direction-output to set. `ltq_mm_save_regs()` configures the EBU address-select register.

Control flow: probe allocates state, initializes a 16-line dynamic-base GPIO chip with only output direction and set callbacks, maps the OF MMIO resource, programs EBU address selection, applies the initial zero shadow, then reads optional `lantiq,shadow` and stores it. Registration uses `devm_gpiochip_add_data()`.

State and persistence behavior: software shadow is the authoritative latch image; the hardware is write-only from the driver's perspective. The current code calls `ltq_mm_save_regs()` and applies before reading the optional shadow property, so a devicetree-provided shadow initializes the software cache after the first hardware write rather than being immediately applied. There is no suspend/resume hook.

Dependencies and integration points: depends on Lantiq SoC EBU helpers, global `ebu_lock`, OF compatible `lantiq,gpio-mm`, and memory-mapped latch wiring. It uses `subsys_initcall()` so latch GPIOs are available early.

Risks: no input/get support and no validation that consumers only request output behavior beyond missing callbacks. The optional shadow ordering may surprise boards expecting the property to set initial physical latch values at probe. EBU lock and timing writes can interfere with other EBU users if not kept serialized.

Test signals: OF probe, 16 output-only lines, latch writes under `ebu_lock`, EBU write-protect restore, `lantiq,shadow` behavior, and consumer attempts to use unsupported input/read operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mm-lantiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mmio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mmio.c

Purpose: implements the reusable generic memory-mapped GPIO helper and, when `CONFIG_GPIO_GENERIC_PLATFORM` is enabled, a `basic-mmio-gpio` platform driver. It supports simple data registers, set/clear register pairs, direction registers, endian variations, pinctrl-backed request/free, and batched get/set.

Important APIs/types/functions: exported `gpio_generic_chip_init()` configures a `struct gpio_generic_chip` from `struct gpio_generic_chip_config`. Accessors include 8/16/32/64-bit native and 16/32-bit big-endian byte-order reads/writes. `gpio_mmio_line2mask()` handles mirrored big-endian bit numbering. Setup helpers are `gpio_mmio_setup_io()`, `gpio_mmio_setup_direction()`, and `gpio_mmio_setup_accessors()`. Runtime callbacks cover get, get_multiple, set, set_multiple, direction input/output, get_direction, request, and platform probe helpers.

Control flow: chip init validates register width, initializes the raw spinlock, fills core gpio metadata, detects `ngpios`, selects output semantics from `dat`, `set`, `clr`, and no-output flags, selects byte-order accessors, selects direction callbacks, optionally enables pinctrl-backed request/free, snapshots initial data and direction registers, and synchronizes paired direction registers. The platform probe maps named resources `dat`, `set`, `clr`, `dirout`, and `dirin`, translates firmware flags such as `big-endian` and `no-output`, initializes the generic chip, applies optional `label` and board-file-only `gpio-mmio,base`, and registers it.

State and persistence behavior: `sdata` shadows output register state for read/modify/write paths and unreadable/set-only output registers. `sdir` shadows direction state and is authoritative when direction registers are unreadable. The helper itself has no PM save/restore; callers that need suspend persistence must save hardware and/or generic shadows externally. Raw spinlocks protect `sdata` and `sdir` updates.

Dependencies and integration points: many drivers in this batch call `gpio_generic_chip_init()`. The platform driver matches several simple OF compatibles including `brcm,bcm6345-gpio`, `wd,mbl-gpio`, `ni,169445-nand-gpio`, `intel,ixp4xx-expansion-bus-mmio-gpio`, and `opencores,gpio`. It integrates optionally with pinctrl through `GPIO_GENERIC_PINCTRL_BACKEND`.

Risks: `cfg->sz` must be a power of two and no wider than `BITS_PER_LONG`; 64-bit big-endian byte order is unsupported. Big-endian mirrored bit order disables some bulk output-read optimizations because translating both register bit order and output-register reflection is complex. The platform driver requires all present named resources to have exactly the same size as `dat`. Board-file-only `gpio-mmio,base` must not leak into devicetree sources.

Test signals: unit or hardware tests should cover all output modes (`dat`, `set`, `set/clear`, no-output), both direction register conventions, unreadable direction/data flags, big-endian bit mirroring, byte-order accessors, get/set_multiple correctness, pinctrl callbacks, invalid widths, platform resource size mismatch, and consumers such as `gpio-menz127`, `gpio-mlxbf*`, `gpio-mpc8xxx`, `gpio-mt7621`, `gpio-mxc`, and `gpio-mxs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mockup.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mockup.c

Purpose: provides a synthetic GPIO controller for testing GPIO consumers, libgpiod behavior, line naming, pull simulation, and IRQ/event handling without real hardware.

Important APIs/types/functions: `struct gpio_mockup_line_status` stores direction, value, pull, and requested state. `struct gpio_mockup_chip` stores the gpiochip, line array, irq simulation domain, debugfs directory, and mutex. Module parameters `gpio_mockup_ranges` and `gpio_mockup_named_lines` define synthetic chips. GPIO callbacks include get/set, get_multiple/set_multiple, direction, get_direction, set_config, to_irq, request, and free. Debugfs callbacks expose per-line read/write. Init helpers register software-node-backed platform devices.

Control flow: module init validates range pairs, creates `/sys/kernel/debug/gpio-mockup`, registers a platform driver, then registers one platform device per range with software-node properties for chip label, optional base, `nr-gpios`, and optional line names. Probe reads those properties, initializes all lines as input, creates an irq simulation domain, registers cleanup actions, adds the gpiochip, and creates debugfs line files. Debugfs writes change the simulated pull; if a requested input line changes and its IRQ mapping/type matches the edge, the code sets the simulated IRQ pending state.

State and persistence behavior: all state is memory-resident and protected by `chip->lock`. Line value differs from pull while a line is requested as output; freeing a line restores value to the pull. IRQ mappings are created lazily in `to_irq()` and disposed by a devm action. No state persists across module unload.

Dependencies and integration points: depends on platform devices, software nodes, debugfs, irq_sim, gpiolib, pinconf bias constants, and module parameters. It is directly useful for GPIO selftests and userspace ABI testing because it can synthesize chips and line events.

Risks: `gpio_mockup_range_ngpio()` is interpreted as an end value when base is nonnegative and as a count when base is negative, which is easy to misuse. Debugfs setup depends on finding a child GPIO device after registration. IRQ event delivery only models edge changes caused by pull writes on requested input lines; it is not a full electrical simulator. The per-line debugfs file changes pull, not necessarily currently driven output value.

Test signals: module parameter validation, generated chip count/base/ngpio, optional line names, get/set_multiple, output value versus pull restoration on free, pinconf pull-up/pull-down, debugfs read/write, irq_sim pending events for rising/falling/both edges, and teardown of platform devices, fwnodes, debugfs, and IRQ mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mockup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-moxtet.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-moxtet.c

Purpose: exposes fixed GPIO-like input/output signals on Turris MOX modules connected over the Moxtet bus. The current descriptor supports the SFP module.

Important APIs/types/functions: `struct moxtet_gpio_desc` defines valid input and output bitmasks. `struct moxtet_gpio_chip` holds the parent device, `gpio_chip`, and descriptor. GPIO callbacks implement get, set, get_direction, direction_input, and direction_output. The driver is a `struct moxtet_driver` with an OF table and module-id table.

Control flow: probe reads the Moxtet module id, rejects unsupported ids, allocates state, assigns the descriptor, fills a sleepable dynamic-base gpiochip, and registers it. Get reads either current input state via `moxtet_device_read()` or last written output state via `moxtet_device_written()`, shifting output state by `MOXTET_GPIO_INPUTS` to align with public offsets. Set reads the last written state, adjusts the output bit after subtracting the input offset, and writes it back.

State and persistence behavior: fixed direction is derived from descriptor masks, not mutable hardware configuration. Output state persists in the Moxtet device's written-state cache and hardware. The driver keeps no extra shadow besides the descriptor pointer. There is no PM hook.

Dependencies and integration points: depends on the Moxtet bus API, module id `TURRIS_MOX_MODULE_SFP`, OF compatible `cznic,moxtet-gpio`, and gpiolib. It marks the chip `can_sleep` because bus transactions can sleep.

Risks: only bits listed in descriptor masks are valid; all other offsets return `-EINVAL`. Direction attempts on hard-wired opposite-direction lines return `-ENOTSUPP`. Output bit shifting is subtle because public offsets include the four input slots while the written state stores outputs from bit 0.

Test signals: SFP module probe, unsupported module rejection, fixed-direction reporting, input reads, output write/readback through Moxtet cache, invalid offset behavior, and expected sleepable GPIO semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-moxtet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpc5200.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpc5200.c

Purpose: provides two GPIO controller drivers for Freescale MPC52xx: an 8-line wakeup GPIO block and a 32-line simple GPIO block.

Important APIs/types/functions: shared `struct mpc52xx_gpiochip` stores `gpio_chip`, mapped registers, and shadow copies of data output, GPIO enable, and direction. A global `gpio_lock` serializes register updates. Wakeup callbacks are `mpc52xx_wkup_gpio_*`; simple callbacks are `mpc52xx_simple_gpio_*`. Two platform drivers match `fsl,mpc5200-gpio-wkup` and `fsl,mpc5200-gpio`.

Control flow: each probe allocates a chip, initializes dynamic-base callbacks and `ngpio`, creates an OF-derived label, maps resource 0, registers the gpiochip, then snapshots enable/direction/output registers into shadows. Direction output writes the requested value first, sets the direction bit, and enables the pin. Direction input clears the direction bit and enables the pin. Wakeup GPIO bit numbering maps line 0 to bit 7; simple GPIO maps line 0 to bit 31.

State and persistence behavior: output, enable, and direction are tracked in software shadows to avoid losing other bits during write-only style updates. Hardware register state is read once after chip registration. There is no suspend/resume handler, so shadows are not automatically restored after power loss.

Dependencies and integration points: depends on OF platform devices, PowerPC MPC52xx register layouts from `<asm/mpc52xx.h>`, and big-endian I/O helpers for the simple block. The driver registers both platform drivers at `subsys_initcall()` so board users can acquire GPIOs early.

Risks: no IRQ support is provided despite wakeup naming. Fixed bit-number reversals are easy to break in refactors. The global lock serializes both controllers, which is conservative but can hide per-chip contention. The author string has a missing `>` in metadata but no runtime impact.

Test signals: OF probe for both compatibles, 8/32-line registration, initial shadow loading, bit-reversed get/set/direction behavior, enable-bit writes on direction changes, and early initcall availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpc5200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpc8xxx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpc8xxx.c

Purpose: supports 32-line GPIO blocks on Freescale/NXP MPC512x, MPC8xxx, QorIQ, and compatible ACPI-described controllers, including generic MMIO GPIO operations, cascaded IRQ domains, and wakeup handling.

Important APIs/types/functions: `struct mpc8xxx_gpio_chip` wraps a `gpio_generic_chip`, MMIO base, raw spinlock, saved direction-output callback, IRQ domain, and parent IRQ number. `mpc_pin2mask()` maps GPIO line 0 to bit 31. Variant hooks in `struct mpc8xxx_gpio_devtype` override direction output, get, or irq_set_type for MPC512x/5125/8572. IRQ flow is implemented by `mpc8xxx_gpio_irq_cascade()`, mask/unmask/ack helpers, `mpc8xxx_irq_set_type()`, and `mpc512x_irq_set_type()`.

Control flow: probe maps registers, initializes a big-endian-bit generic chip over GPIO_DAT and GPIO_DIR, applies little-endian byte-order override when requested, installs variant callbacks, enables QorIQ/ACPI input buffers, registers the gpiochip, obtains the parent IRQ, creates a linear IRQ domain, clears/masks all hardware IRQs, requests a shared cascade IRQ, and enables device wakeup. The cascade handler intersects pending status `IER` with mask `IMR`, then dispatches domain IRQs using reversed bit numbering.

State and persistence behavior: generic chip shadows output data and direction. For MPC8572 errata, output reads use `sdata` for output pins and hardware DAT for input pins. Suspend/resume only toggles parent IRQ wake when device wakeup is enabled; it does not save GPIO register state.

Dependencies and integration points: integrates with OF compatibles for many Freescale/NXP SoCs, ACPI HID `NXP0031`, `gpio-mmio`, generic IRQ domains/chips, runtime PM macros, and gpiolib IRQ resource helpers. It uses `arch_initcall()` for early availability.

Risks: `mpc8xxx_irq_chip.irq_set_type` is a global mutable struct overwritten by probe based on devtype, relying on the assumption that only one controller type exists per machine. `mpc8xxx_remove()` clears a chained handler even though probe used `devm_request_irq()`, suggesting stale cleanup style. IRQ trigger support differs by variant; default accepts falling/low and both-edge only, while MPC512x supports more modes through two-bit fields. No register PM restore is present.

Test signals: variant matching, big-endian bit mapping, QorIQ input buffer enable, MPC5121/5125 input-only restrictions, MPC8572 shadow get behavior, IRQ domain mapping and cascade dispatch, mask/unmask/ack register writes, wakeup enable/disable on suspend/resume, and ACPI probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpc8xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpfs.c

Purpose: supports Microchip PolarFire SoC GPIO and CoreGPIO RTL v3 blocks, exposing up to 32 GPIOs with regmap-backed value/direction and optional parent IRQs.

Important APIs/types/functions: `struct mpfs_gpio_reg_offsets` selects input/output register offsets for MPFS versus CoreGPIO. `struct mpfs_gpio_chip` stores the regmap, offsets, and gpiochip. GPIO callbacks are direction_input/output, get_direction, get, and set. IRQ callbacks are `mpfs_gpio_irq_set_type()`, mask/unmask, and chained parent `mpfs_gpio_irq_handler()`.

Control flow: probe selects offset data from the OF match, maps resource 0, creates a raw-spinlock regmap, enables the clock, reads optional `ngpios` clamped to 32, fills the gpiochip, counts OF IRQs, and if any exist configures a gpio_irq_chip with one parent per IRQ. Direction input writes `EN_IN` into per-line control. Direction output enables output and output buffer, then updates the output register. IRQ unmask forces the line to input and sets `EN_INT`; the handler reads `MPFS_IRQ_REG`, clears each pending bit by writing it back, and dispatches the domain IRQ.

State and persistence behavior: per-line control registers hold direction and interrupt type/enable. Output and input registers are selected by match data. No explicit PM save/restore exists; the clock is devm-enabled for the device lifetime.

Dependencies and integration points: depends on OF compatibles `microchip,mpfs-gpio` and `microchip,coregpio-rtl-v3`, regmap MMIO, clock framework, OF IRQ counting, and gpiolib hierarchical parent IRQ support.

Risks: `mpfs_gpio_irq_set_type()` lacks a default case that initializes `interrupt_type` for unsupported trigger values, so invalid types can use an uninitialized value rather than returning `-EINVAL`. `mpfs_gpio_set()` calls `mpfs_gpio_get()` before and after updating output but ignores the results, likely leftover debugging or readback flushing. Multiple parent IRQs all share the same handler data and status register scan, so firmware IRQ topology must match hardware expectations.

Test signals: both compatible offset maps, ngpio clamping, direction and value register writes, get using output register for outputs and input register for inputs, IRQ type programming for all supported modes, invalid type behavior, chained IRQ status clear/dispatch, and clock/regmap probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpsse.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpsse.c

Purpose: exposes FTDI MPSSE-capable USB interfaces as 16-line GPIO chips and synthesizes edge IRQs by polling input pins. It includes a quirk for a Bryx device with named, direction-limited pins.

Important APIs/types/functions: `struct mpsse_priv` stores the gpiochip, USB device/interface, endpoint descriptors, output/direction bytes for low/high banks, direction masks, IRQ worker list, atomics for IRQ type/enabled masks, and I/O/IRQ locks. `mpsse_bulk_xfer()`, `mpsse_write()`, and `mpsse_read()` wrap USB bulk transfers. GPIO bank helpers use FTDI `SET_BITS` and `GET_BITS` commands. IRQ polling is implemented by `struct mpsse_worker`, `gpio_mpsse_poll()`, and irqchip enable/disable/type callbacks.

Control flow: USB probe allocates state and an IDA id, initializes locks, builds a unique label from VID/PID/interface/id/serial, applies optional direction/name quirk, finds bulk endpoints, allocates a receive buffer, resets the FTDI bitmode, enters MPSSE mode, configures an internal IRQ chip with valid IRQ mask restricted to input-capable pins, and registers the gpiochip. Set/get_multiple operate per 8-bit bank under `io_mutex`. Direction output sets the MPSSE direction bit then writes value; direction input clears the direction bit and writes the bank. IRQ enable starts a polling work item when transitioning from no enabled IRQs to some enabled IRQs; the worker polls selected input pins, compares against old values, and calls `generic_handle_irq()` on matching edges.

State and persistence behavior: `gpio_outputs[2]` and `gpio_dir[2]` are software shadows mirrored to MPSSE bank state. IRQ type and enabled state are atomics; worker lifetime is tracked in a raw-spinlock-protected list and coordinated with `irq_race` to avoid double-free between self-teardown and disconnect. No hardware state persists after USB disconnect or reset.

Dependencies and integration points: depends on USB core, FTDI vendor bitmode requests, gpiolib, IRQ domains, workqueues, IDA allocation, and optional product quirks. GPIO operations can sleep because they perform USB control/bulk transfers.

Risks: IRQs are polling based with a 1 ms interval, so fast pulses can be missed and latency is not deterministic. `gpio_mpsse_disconnect()` sets `priv->intf = NULL` after stopping workers, but ordinary GPIO I/O paths rely on the interface while the gpiochip is devm-managed, so disconnect ordering is important. Worker allocation happens in irqchip enable with `GFP_NOWAIT` and silently gives no polling worker on allocation failure. Quirk direction masks must be correct or valid pins become inaccessible.

Test signals: USB probe/reset/MPSSE mode commands, bulk status-byte stripping, banked get/set and direction bytes, quirk valid-mask enforcement and line names, polling IRQ delivery for rising/falling/both edges, worker teardown on IRQ disable and disconnect, and behavior under USB transfer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpsse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-msc313.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-msc313.c

Purpose: supports GPIO pads on MStar/SigmaStar MSC313 and SSD20x-family SoCs. It maps SoC-specific named pad lists to sparse register offsets, exposes GPIO operations, saves output-enable/value state across suspend, and delegates selected GPIO interrupts to the parent interrupt controller.

Important APIs/types/functions: `struct msc313_gpio_data` contains per-SoC line names, register offsets, and count. Large static name/offset tables describe functional pads and SSD20x GPIO/TTL/UART/SD variants. `struct msc313_gpio` stores the base, matched data, and suspend save array. GPIO callbacks are set/get/direction_input/direction_output. IRQ integration uses `msc313_gpio_irqchip`, `msc313_gpio_populate_parent_fwspec()`, and `msc313e_gpio_child_to_parent_hwirq()`.

Control flow: probe obtains match data, finds the parent IRQ domain, allocates state and the save array, maps MMIO, allocates and fills a gpiochip with names and callbacks, configures hierarchical IRQ mapping to the parent domain, and registers the chip. Direction input sets the OEN bit; direction output clears OEN and updates OUT. Interrupt child-to-parent mapping only accepts offsets in the SPI0 pad range and maps them to parent SPI interrupts 28-31 with the requested type.

State and persistence behavior: each pad register contains IN, OUT, and OEN bits. Suspend saves only OUT and OEN bits (`MSC313_GPIO_BITSTOSAVE`) for every configured line; resume writes those bits back to each sparse register. Input state is hardware sampled and not persisted.

Dependencies and integration points: depends on OF match data gated by `CONFIG_MACH_INFINITY`, parent interrupt controller domain discovery, ARM GIC fwspec format, gpiolib, and generic pin request/free. The IRQ chip forwards EOI, mask, unmask, type, and affinity operations to the parent.

Risks: only SPI0 pins support parent IRQ mapping; IRQ requests on other GPIOs fail. Writing saved OUT/OEN bits on resume overwrites only the saved byte value and may drop any unrelated bits in those registers if future hardware adds them. The match table is empty unless `CONFIG_MACH_INFINITY` is enabled. Sparse offset/name tables are large and prone to ordering mistakes.

Test signals: compatible-specific line count/names, sparse offset get/set/direction behavior, suspend/resume preservation of OUT/OEN, parent fwspec creation with `GIC_SPI`, SPI0 IRQ mapping to parent hwirqs 28-31, and rejection of unsupported IRQ-capable lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-msc313.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mt7621.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mt7621.c

Purpose: supports the MediaTek/Ralink MT7621 GPIO controller as three 32-line banks, each exposed as a separate gpiochip with shared parent IRQ support.

Important APIs/types/functions: `struct mtk` stores the device, MMIO base, parent IRQ, and three `struct mtk_gc` bank structures. `struct mtk_gc` wraps `gpio_generic_chip`, per-bank IRQ chip, bank id, and software trigger masks for rising/falling/high/low. Helpers `mtk_gpio_r32()` and `mtk_gpio_w32()` add bank stride to register offsets. GPIO setup uses `gpio_generic_chip_init()`. IRQ callbacks handle status scanning, mask/unmask, type, and OF translation.

Control flow: platform probe maps resource 0, gets the parent IRQ, stores drvdata, then probes banks 0-2. Each bank initializes a generic chip over DATA/DSET/DCLR/CTRL registers with `GPIO_GENERIC_NO_SET_ON_INPUT`, sets OF two-cell translation, labels and offsets the bank, requests the shared parent IRQ with bank-specific data, configures an internal IRQ chip, registers the gpiochip, and sets polarity low. The IRQ handler reads bank status, dispatches each pending bit through the bank's IRQ domain, then clears that bit.

State and persistence behavior: hardware registers hold direction/data/polarity/status. Desired trigger modes are cached in `rising`, `falling`, `hlevel`, and `llevel`; unmask writes those cached masks to hardware enable registers. There is no suspend/resume save path.

Dependencies and integration points: depends on OF compatible `mediatek,mt7621-gpio`, shared parent IRQ, generic MMIO GPIO helper, and OF GPIO translation where global GPIO numbers are mapped to bank-local offsets.

Risks: `mediatek_gpio_irq_type()` does not reject unsupported trigger types; if no case matches, it clears all cached trigger bits and returns success. Shared parent IRQ is requested once per bank with `IRQF_SHARED`, so status isolation by bank register offset must be correct. No PM restore may lose trigger caches versus hardware after suspend.

Test signals: three bank registration, OF xlate rejecting wrong-bank GPIO specifiers, generic get/set/direction behavior, IRQ type cache updates, mask/unmask programming of edge/level registers, status dispatch and clearing per bank, and invalid trigger handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mt7621.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mvebu.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mvebu.c

Purpose: implements GPIO, IRQ, debugfs, PM, and optional PWM support for Marvell EBU GPIO controllers across Orion, Dove, Kirkwood, Armada 370/XP, MV78200, and Armada 8k variants.

Important APIs/types/functions: `struct mvebu_gpio_chip` stores gpiochip, regmaps, register offset, per-CPU regmap, IRQ domain, SoC variant, clock, optional PWM state, and PM save registers. `struct mvebu_pwm` stores PWM regmap, offset, clock rate, owned GPIO descriptor, lock, and saved PWM registers. Register selection helpers abstract variant-specific edge-cause, edge-mask, and level-mask locations. GPIO callbacks cover get/set, blink, direction, get_direction, and to_irq. IRQ callbacks implement ack, edge/level mask/unmask, set_type, and chained handling. PWM callbacks implement request/free/get_state/apply.

Control flow: probe reads `ngpios` and OF alias id, enables an optional clock, fills the gpiochip, creates either raw MMIO regmaps or syscon/offset-backed A8K mapping, clears and masks interrupts according to variant, registers the gpiochip, optionally registers a PWM chip, then if parent IRQs exist creates an IRQ domain with two generic chip types for level and edge triggers and installs up to four chained parent handlers. GPIO direction asks pinctrl to validate direction before updating IO_CONF. IRQ set_type requires the line be configured as input, switches generic chip type when needed, and programs input polarity. The chained handler combines level cause from DATA_IN with level mask and latched edge cause with edge mask, flips polarity for both-edge emulation, and dispatches child IRQs.

State and persistence behavior: GPIO output, IO configuration, blink enable, input polarity, and variant-specific interrupt masks are saved on suspend and restored on resume. PWM blink-counter selection and on/off durations are also saved when PWM support is reachable. Both-edge IRQ behavior is stateful because it toggles polarity after each interrupt to catch the next edge.

Dependencies and integration points: depends on OF compatibles for Marvell variants, regmap, syscon for Armada 8k, pinctrl, optional clocks, generic IRQ domains/chips, optional PWM framework, and gpiolib descriptor ownership for PWM lines. Debug output is provided under CONFIG_DEBUG_FS through `dbg_show`.

Risks: both-edge emulation has an acknowledged race with GPIO line changes while polarity is being swapped. `devm_gpiochip_add_data()` return is not checked in probe, so a registration failure could be missed before PWM/IRQ setup continues. Variant register selection uses `smp_processor_id()` for per-CPU masks, so CPU affinity and interrupt routing matter. PWM support reserves GPIO lines through own descriptors and only some banks/register layouts support blink counters.

Test signals: variant probe for raw and syscon mappings, GPIO direction validation through pinctrl, get using input polarity for inputs and OUT for outputs, IRQ set_type rejection on output lines, level/edge/both-edge interrupt dispatch and polarity flipping, per-CPU mask register selection, suspend/resume register restoration, PWM request/apply/get_state/free, and debugfs display of requested lines and IRQ state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mvebu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mxc.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mxc.c

Purpose: implements GPIO and interrupt support for Freescale/NXP i.MX MXC GPIO controllers across older i.MX1/i.MX21/i.MX31 and newer i.MX35/i.MX7/i.MX8-family layouts, including runtime PM, syscore save/restore, and SCU pad wakeup configuration.

Important APIs/types/functions: `struct mxc_gpio_hwdata` describes variant register offsets and IRQ encoding values. `struct mxc_gpio_port` stores MMIO base, clock, parent IRQs, IRQ domain, generic MMIO chip, wake/power state, saved registers, pad wake metadata, and variant hwdata. Key functions include `gpio_set_irq_type()`, `mxc_flip_edge()`, `mxc_gpio_irq_handler()`, MX2/MX3 chained handlers, `gpio_set_wake_irq()`, `mxc_gpio_init_gc()`, request/free PM wrappers, runtime suspend/resume, noirq suspend/resume, and syscore suspend/resume.

Control flow: probe maps registers, discovers one or two parent IRQs, enables optional clock and runtime PM, disables/clears interrupts, selects shared MX2 or per-port MX3-style chained handler, initializes a generic chip over PSR/DR/GDIR, registers the gpiochip, creates a legacy 32-line IRQ domain and generic irq_chip, adds the port to the global list, and autosuspends. IRQ type programming supports rising, falling, both, level high, and level low. Hardware with EDGE_SEL can do both-edge directly; older hardware emulates both-edge by programming the opposite level based on current value and flipping after each interrupt.

State and persistence behavior: generic chip shadows data/direction; `mxc_gpio_save_regs()` preserves ICR1/2, IMR, GDIR, EDGE_SEL, and DR only on variants marked `power_off`. Runtime suspend saves registers, disables the clock, and disconnects chained IRQ handlers; runtime resume reconnects handlers, enables the clock, and restores registers. Syscore ops walk all ports to save/restore around low-level system suspend. Wakeup pads are tracked in `wakeup_pads` and `pad_type[]`; noirq suspend programs SCU wake config for i.MX8 variants.

Dependencies and integration points: depends on OF match data, optional clocks, runtime PM, syscore, `gpio-mmio`, generic IRQ chips, irq domains, pinctrl generic config for SCU wake-capable i.MX8, and legacy sysfs base preservation when GPIO sysfs is enabled.

Risks: both-edge emulation on older hardware can race with line changes. Global `mxc_gpio_ports` is used for MX2 shared IRQ and syscore PM, so list management order matters. `gpio_set_irq_type()` forces the line to input after configuring IRQ type, which can surprise consumers that had it as output. Power-off save/restore reads EDGE_SEL unconditionally when `power_off` is true, relying on matching hwdata with a valid edge-select register.

Test signals: probe for each compatible hwdata layout, one-parent and two-parent IRQ flows, direct versus emulated both-edge interrupts, request/free runtime PM refcounting, wake IRQ parent selection for high bank, i.MX8 SCU pad wake config including i.MX8QM falling-edge warning, runtime/syscore save/restore, and GPIO sysfs base alias behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mxc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mxs.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mxs.c

Purpose: supports Freescale MXS/i.MX23/i.MX28 GPIO ports that share a parent pinctrl register block, with GPIO value/direction and per-port IRQ domains.

Important APIs/types/functions: `struct mxs_gpio_port` stores shared MMIO base, alias id, parent IRQ, IRQ domain, generic MMIO chip, device id, and both-edge mask. Register macros compute per-port offsets differently for i.MX23 and i.MX28. IRQ functions are `mxs_gpio_set_irq_type()`, `mxs_flip_edge()`, `mxs_gpio_irq_handler()`, `mxs_gpio_set_wake_irq()`, and `mxs_gpio_init_gc()`. GPIO-specific callbacks include `mxs_gpio_to_irq()` and `mxs_gpio_get_direction()`.

Control flow: probe reads the `gpio` alias id, match data, and parent IRQ. It maps the parent node's register region only once through a static `base`, disables interrupts for the port, clears IRQ status, allocates a 32-line legacy IRQ domain, initializes a generic irq_chip with separate level and edge chip types, installs the chained handler, initializes a generic GPIO chip over DIN/DOUT set/clear/DOE registers, assigns fixed base `id * 32`, and registers the chip. IRQ type programming selects level/edge, polarity, and enables either `PIN2IRQ` or `IRQEN`; both-edge is emulated by selecting the opposite edge of the current input and flipping polarity after dispatch.

State and persistence behavior: hardware registers hold GPIO data, direction, IRQ enable, polarity, and status. Both-edge emulation state is tracked in `both_edges`. No suspend/resume save path exists, but wake IRQ support toggles parent IRQ wake.

Dependencies and integration points: depends on OF compatibles `fsl,imx23-gpio` and `fsl,imx28-gpio`, parent OF MMIO mapping, `gpio-mmio`, generic IRQ chips, chained IRQ handling, and legacy fixed GPIO bases.

Risks: the shared static `base` is mapped once and `iounmap(port->base)` is called on probe failure, which can affect later ports if partial initialization fails. Both-edge emulation has the usual polarity-toggle race. Fixed base `id * 32` is legacy and can collide if aliases are wrong. No PM restore means suspend behavior relies on pinctrl block retention.

Test signals: i.MX23 versus i.MX28 register offsets, shared base mapping across multiple ports, generic GPIO get/set/direction, level and edge IRQ chip types, both-edge polarity flipping, parent wake enable/disable, and failure paths around IRQ domain/chip setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-mxs.c -->
