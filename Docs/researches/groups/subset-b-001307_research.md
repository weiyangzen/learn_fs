# subset-b-001307 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-viperboard.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-viperboard.c

## Purpose
Implements the gpiolib child driver for Nano River Technologies Viperboard MFD devices. It exposes the board's two 16-line GPIO blocks, GPIO A and GPIO B, as separate sleepable `gpio_chip` instances backed by USB control messages through the parent `struct vprbrd`.

## Important APIs, Types, And Functions
- `struct vprbrd_gpioa_msg` and `struct vprbrd_gpiob_msg` define packed USB payloads for GPIO A and B commands.
- `struct vprbrd_gpio` stores both `gpio_chip` objects, cached output-direction/value bitmaps, and the parent Viperboard pointer.
- `vprbrd_gpioa_get`, `vprbrd_gpioa_set`, `vprbrd_gpioa_direction_input`, and `vprbrd_gpioa_direction_output` implement GPIO A using `VPRBRD_USB_REQUEST_GPIOA`.
- `vprbrd_gpiob_setdir`, `vprbrd_gpiob_get`, `vprbrd_gpiob_set`, `vprbrd_gpiob_direction_input`, and `vprbrd_gpiob_direction_output` implement GPIO B using `VPRBRD_USB_REQUEST_GPIOB`.
- `vprbrd_gpio_probe` allocates private state and registers both chips with dynamic GPIO bases.
- `vprbrd_gpio_init` validates the `gpioa_freq` module parameter and maps it to the firmware sampling-clock code.

## Control Flow
Probe receives the parent MFD's `struct vprbrd`, allocates `struct vprbrd_gpio`, fills GPIO A callbacks and registers it, then fills and registers GPIO B callbacks. GPIO A input reads send a GETIN command and then issue an IN transfer to retrieve the answer bit. GPIO A output setup and value changes send SETOUT messages. GPIO B uses 16-bit big-endian `val` and `mask` fields: direction changes call `vprbrd_gpiob_setdir`, reads fetch the whole input register, and writes update only the addressed masked bit. Output reads are served from cached state for both blocks.

## State And Persistence
The driver keeps runtime-only shadow state in `gpioa_out`, `gpioa_val`, `gpiob_out`, and `gpiob_val`; it does not persist values across unbind or disconnect. USB transfers share the parent `vb->buf` and are serialized by `vb->lock`. GPIO A sampling frequency is module-global, fixed during init, and used when GPIO A pins are switched to input.

## Dependencies And Integration Points
Depends on the Viperboard MFD core for `struct vprbrd`, USB device access, request constants, buffer storage, and locking. Integrates with gpiolib through two sleepable chips and with the platform bus as `viperboard-gpio`. USB endianness helpers are used for GPIO B payload fields.

## Risks And Edge Cases
Shadow state is updated before USB completion in several paths, so failed direction/value transfers can leave software cache ahead of hardware. `vprbrd_gpiob_get` returns the raw short USB return value instead of normalizing to `-EREMOTEIO` on short reads. GPIO A `set` silently ignores writes to pins not marked as outputs. All operations reuse a parent shared transfer buffer, making the parent mutex essential. Invalid `gpioa_freq` only warns and falls back to 1 kHz.

## Test Signals
Exercise both GPIO blocks independently, including input reads through USB, output readback from cached values, direction changes, invalid sampling frequency fallback, short USB transfers, and simultaneous GPIO A/B operations to confirm parent-buffer serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-viperboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-virtio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-virtio.c

## Purpose
Provides a virtio transport driver for virtual GPIO controllers. It exposes virtio GPIO lines through gpiolib and optionally maps virtio GPIO event queues into Linux IRQs when the device advertises `VIRTIO_GPIO_F_IRQ`.

## Important APIs, Types, And Functions
- `struct virtio_gpio_line` owns one preallocated request/response pair, line mutex, completion, and returned length.
- `struct vgpio_irq_line` tracks one interrupt event buffer plus type, disabled/masked, queued, and pending-update flags.
- `_virtio_gpio_req` is the synchronous virtqueue transaction primitive for all request-queue operations.
- `virtio_gpio_get_direction`, `virtio_gpio_direction_input`, `virtio_gpio_direction_output`, `virtio_gpio_get`, `virtio_gpio_set`, and `virtio_gpio_free` implement `gpio_chip` callbacks.
- IRQ support is split across `virtio_gpio_irq_prepare`, mask/unmask/enable/disable/set-type callbacks, `virtio_gpio_irq_bus_sync_unlock`, `ignore_irq`, and `virtio_gpio_event_vq`.
- `virtio_gpio_probe` reads virtio config, allocates line state, initializes optional irqchip state, allocates virtqueues, fetches line names, and registers the GPIO chip.

## Control Flow
GPIO operations lock the per-line buffer, populate a virtio GPIO request, add request and response scatterlists to `requestq` under the virtqueue mutex, kick the queue, wait for completion, then validate status and response length. Direction-output writes the value first, then switches direction. IRQ enable/type changes are staged in per-line flags under the IRQ bus lock; bus sync sends `VIRTIO_GPIO_MSG_IRQ_TYPE` and queues event buffers only after the backend has enabled the line. Event-queue completions validate the response length, derive the GPIO number from the returned buffer pointer, filter disabled or invalid events, and dispatch `generic_handle_domain_irq`.

## State And Persistence
State is entirely live virtio-device state: per-line request buffers, completions, IRQ type/mask/queued flags, and optional line-name strings returned by the device. The virtio backend owns the durable GPIO state. Removal unregisters the gpiochip and resets/deletes virtqueues.

## Dependencies And Integration Points
Depends on the virtio core, `uapi/linux/virtio_gpio.h`, scatterlist DMA semantics, gpiolib, and generic IRQ domains. The driver binds to `VIRTIO_ID_GPIO`, uses `virtio_find_vqs` for `requestq` and optional `eventq`, and publishes line names through `gc.names`.

## Risks And Edge Cases
The synchronous request path can hang if a backend never completes a request. IRQ state transitions are subtle because buffers cannot be queued while masked/disabled and invalid returned buffers must be requeued only when the line is enabled again. `virtio_gpio_get_names` trusts the config size but must guard against truncated name blocks; zero-length names are allowed. Virtqueue API serialization depends on `vgpio->lock`, while interrupt queueing uses a raw spinlock.

## Test Signals
Use a virtio-gpio device with and without IRQ feature support, verify request response status and length checks, line-name parsing with zero-length and truncated entries, direction-output ordering, IRQ enable/mask/unmask/type transitions, invalid event-buffer requeueing, and removal while no event buffers remain live.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-virtio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-virtuser.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-virtuser.c

## Purpose
Implements a configurable virtual GPIO consumer module for testing and exercising GPIO providers. It can bind to GPIO descriptors described by firmware or configfs-created software nodes, then exposes per-line and per-array controls through debugfs.

## Important APIs, Types, And Functions
- `struct gpio_virtuser_attr_data`, `gpio_virtuser_line_array_data`, and `gpio_virtuser_line_data` hold debugfs backing data for GPIO arrays and individual lines.
- `struct gpio_virtuser_irq_work_context` bridges debugfs "atomic" operations into hard IRQ work for non-sleeping GPIO APIs.
- Debugfs value/direction/consumer/debounce/interrupt functions expose descriptor operations such as `gpiod_get_array_value_cansleep`, `gpiod_set_value_cansleep`, `gpiod_direction_input`, `gpiod_set_consumer_name`, `gpiod_set_debounce`, `gpiod_to_irq`, and `request_threaded_irq`.
- `gpio_virtuser_probe` discovers GPIO IDs, requests descriptor arrays, and creates the debugfs tree.
- Configfs types `gpio_virtuser_device`, `gpio_virtuser_lookup`, and `gpio_virtuser_lookup_entry` model devices, consumer IDs, and lookup-table entries.
- `gpio_virtuser_device_activate` builds a software node and lookup table, registers a `gpio-virtuser` platform device, waits for probe, and marks it live.

## Control Flow
For firmware-described devices, probe counts IDs from `*-gpios` OF properties or the `gpio-virtuser,ids` property, requests each descriptor array, creates a debugfs directory for the platform device, adds array-level `values` files, and adds per-line files for direction, value, debounce, consumer name, and interrupt counting. For configfs, users create a device group, lookup groups, and lookup-entry groups; attributes configure key, offset, drive, pull, active-low, and transitory flags while the device is offline. Writing `live=1` locks dependent configfs entries, creates a gpiod lookup table and software node, registers a platform device, and relies on normal probe to create the debugfs controls. Writing `live=0` unregisters the platform device and tears down lookup/swnode state.

## State And Persistence
The module holds global ID allocation state in `gpio_virtuser_ida`, a global debugfs root, configfs hierarchy objects, dynamically allocated lookup tables, software nodes, platform device pointers, and per-line debugfs state. IRQ enablement is tracked by `atomic_t irq`; interrupt counts are `atomic_t irq_count`. Debounce and consumer strings are cached in per-line data. State persists only while the module/configfs objects are alive.

## Dependencies And Integration Points
Depends on GPIO consumer APIs, gpiod lookup tables, property/software-node APIs, platform driver binding, configfs, debugfs, IRQ work, threaded IRQs, IDA allocation, and OF property parsing. It is primarily a GPIO test and demonstration consumer rather than a hardware controller.

## Risks And Edge Cases
Debugfs write parsing expects exact lengths for array values and small string buffers. The interrupt disable path calls `free_irq` on the result of `atomic_xchg`; writing `0` before enabling can pass IRQ 0 to `free_irq`. Atomic debugfs paths queue hard IRQ work and wait synchronously, so failures in completion handling would deadlock readers/writers. Configfs live locking must stay balanced on activation failures and deactivation. Lookup-table memory ownership is manual around `dev_id`, table allocation, and `no_free_ptr`.

## Test Signals
Create configfs devices with multiple lookup groups, validate busy errors when editing live objects, activate/deactivate repeatedly, verify software-node IDs drive probe, read/write debugfs scalar and array values in sleepable and atomic modes, change consumer/debounce attributes, request/release IRQ counting, and remove configfs groups while live to confirm deactivation cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-virtuser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-visconti.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-visconti.c

## Purpose
Supports the Toshiba Visconti GPIO controller as a memory-mapped generic GPIO block with hierarchical interrupt forwarding to a parent interrupt controller.

## Important APIs, Types, And Functions
- `struct visconti_gpio` stores MMIO base, spinlock, generic GPIO chip, and device pointer.
- `gpio_generic_chip_init` supplies basic data, set, clear, and direction-output operations using `GPIO_IDATA`, `GPIO_OSET`, `GPIO_OCLR`, and `GPIO_DIR`.
- `visconti_gpio_irq_set_type` programs `GPIO_ODATA` and `GPIO_INTMODE` to model rising, falling, both-edge, and level triggers.
- `visconti_gpio_child_to_parent_hwirq` maps child GPIO IRQs 0-15 to parent hwirqs 24-39.
- `visconti_gpio_populate_parent_fwspec` builds the three-cell parent fwspec.
- `visconti_gpio_mask_irq`, `visconti_gpio_unmask_irq`, and `visconti_gpio_irq_chip` wrap parent IRQ masking with gpiolib IRQ resource tracking.

## Control Flow
Probe maps the GPIO register resource, locates the OF IRQ parent node and domain, initializes a generic GPIO chip, installs an immutable hierarchical irqchip, and registers the chip. IRQ type changes take the controller lock, adjust output-data/intmode bits used by the hardware interrupt logic, set the parent view to level-high where required, then delegate type programming to the parent chip.

## State And Persistence
Only hardware registers persist while powered: direction, output data, interrupt mode, and interrupt polarity emulation state. The driver keeps no software shadow beyond the spinlock and generic-chip structure.

## Dependencies And Integration Points
Uses OF IRQ parent discovery, parent IRQ domains, gpiolib generic MMIO helpers, hierarchical gpio irqchip callbacks, and the platform bus compatible `toshiba,gpio-tmpv7708`.

## Risks And Edge Cases
Only child interrupts 0-15 are mappable; higher GPIOs return `-EINVAL`. The driver maps low-level child interrupts by programming the parent as level-high and inverting controller data bits, so polarity handling is easy to regress. `irq_set_irq_type(offset, intc_type)` uses the offset as an IRQ number, which is a point to scrutinize against hierarchical parent semantics. Concurrent GPIO and IRQ register changes rely on a single spinlock.

## Test Signals
Validate GPIO data/set/clear/direction operations, IRQ mappings for child 0 and 15, failure for child 16, all supported IRQ trigger types, parent fwspec contents, and interrupt masking/unmasking order with `gpiochip_enable_irq` and parent mask calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-visconti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-vx855.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-vx855.c

## Purpose
Exposes the VIA VX855 southbridge GPIO, GPI, and GPO pins through gpiolib using legacy x86 I/O port registers supplied by the VX855 MFD platform device.

## Important APIs, Types, And Functions
- `struct vx855_gpio` stores the `gpio_chip`, spinlock, and input/output I/O port addresses.
- Bit mapping helpers `gpi_i_bit`, `gpo_o_bit`, `gpio_i_bit`, and `gpio_o_bit` translate logical line offsets to sparse southbridge register bits.
- `vx855gpio_direction_input`, `vx855gpio_direction_output`, `vx855gpio_get`, and `vx855gpio_set` implement line operations with special handling for GPI-only, GPO-only, and open-drain GPIO ranges.
- `vx855gpio_set_config` reports push-pull support for GPOs and open-drain support for bidirectional GPIOs.
- `vx855gpio_probe` receives two I/O resources, optionally reserves them, initializes chip metadata and line names, and registers the chip.

## Control Flow
Logical GPIO offsets 0-13 are input-only GPI pins, 14-26 are output-only GPO pins, and 27-41 are open-drain bidirectional GPIO pins. Reads choose either the input register or output register depending on line class. Setting a true GPI fails, setting a GPO or GPIO updates the output port under spinlock, and input direction for open-drain GPIOs writes a high output state.

## State And Persistence
The driver has no shadow state; hardware I/O port registers are the source of truth. Resource reservations are devm-managed and may be skipped if ACPI already owns the region.

## Dependencies And Integration Points
Depends on platform resources from the VX855 MFD driver, legacy `inl`/`outl` I/O port access, gpiolib, pinconf drive-mode constants, and static line names for the 42 logical pins.

## Risks And Edge Cases
The chip uses sparse and nonuniform bit mappings, making off-by-one errors likely. The probe tolerates busy I/O regions due to ACPI overlap, so simultaneous firmware/driver access is possible. `gpio_chip.base` is fixed at 0, which can collide on systems with other static GPIO bases. Input/output restrictions differ by logical range and must remain consistent across direction, set, and config callbacks.

## Test Signals
Check all range boundaries: GPI13/GPO0, GPO12/GPIO0, GPIO14, GPI output rejection, GPO input rejection, open-drain input-as-high behavior, set_config return codes, and operation when request_region fails due to ACPI reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-vx855.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wcd934x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wcd934x.c

## Purpose
Adds gpiolib support for the five GPIO pins in Qualcomm WCD9340/WCD9341 audio codec MFDs using the parent regmap.

## Important APIs, Types, And Functions
- `struct wcd_gpio_data` holds the parent `regmap` and embedded `gpio_chip`.
- `wcd_gpio_get_direction`, `wcd_gpio_direction_input`, `wcd_gpio_direction_output`, `wcd_gpio_get`, and `wcd_gpio_set` manipulate direction and value bits in `WCD_REG_DIR_CTL_OFFSET` and `WCD_REG_VAL_CTL_OFFSET`.
- `wcd_gpio_probe` fetches the parent regmap, initializes a sleepable five-line chip, and registers it.

## Control Flow
Probe binds from OF compatibles, obtains the parent regmap, fills gpiolib callbacks, and registers a dynamic-base chip. Direction input clears the pin bit in the direction register. Direction output sets the direction bit first and then writes the requested value bit. Get reads the value-control register and masks the pin bit.

## State And Persistence
The driver keeps no local state beyond the chip/regmap pointer. Direction and value persist in codec registers according to parent device power/reset behavior.

## Dependencies And Integration Points
Integrates with the Qualcomm WCD934x MFD/regmap parent and the platform bus compatibles `qcom,wcd9340-gpio` and `qcom,wcd9341-gpio`. It exposes `can_sleep = true` because regmap access can sleep.

## Risks And Edge Cases
`wcd_gpio_get` ignores a regmap read error and may return a stale/undefined masked value if the read fails. Direction-output is not atomic: a failure after setting direction can leave the pin configured as output with the old value. There is no IRQ support and no pin configuration beyond direction/value.

## Test Signals
Verify parent regmap absence returns `-EINVAL`, all five pin bits map correctly, direction and value writes target the expected registers, read-error injection on get is noticed by tests, and dynamic GPIO base registration succeeds from both compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wcd934x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wcove.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wcove.c

## Purpose
Implements GPIO and nested IRQ support for the Intel Whiskey Cove PMIC. It exposes 94 logical GPIO numbers, with the first 13 backed by physical GPIO control registers and interrupts.

## Important APIs, Types, And Functions
- `struct wcove_gpio` stores regmap, regmap-IRQ data, GPIO chip, bus lock, and pending IRQ update fields.
- `to_reg` and `to_ireg` translate GPIO offsets to PMIC control, IRQ mask, and IRQ status registers.
- `wcove_gpio_dir_in`, `wcove_gpio_dir_out`, `wcove_gpio_get_direction`, `wcove_gpio_get`, `wcove_gpio_set`, and `wcove_gpio_set_config` implement GPIO operations.
- `wcove_irq_type`, `wcove_irq_mask`, `wcove_irq_unmask`, `wcove_bus_lock`, and `wcove_bus_sync_unlock` stage and commit IRQ type/mask changes.
- `wcove_gpio_irq_handler` reads two status registers, dispatches nested GPIO IRQs, and acks each handled bit.
- `wcove_gpio_dbg_show` reports direction, level, IRQ mask/status, and edge configuration.

## Control Flow
Probe obtains the parent `intel_soc_pmic`, platform IRQ, and regmap IRQ virtual IRQ, initializes a sleepable chip, installs an internal irqchip without a parent handler, requests a threaded handler for the PMIC IRQ, registers the gpiochip, and unmasks the PMIC GPIO interrupt groups. GPIO offsets beyond the 13 physical pins are accepted by the chip but most callbacks become no-ops or fixed outputs through `to_reg` returning `-ENOTSUPP`. IRQ type and mask operations record desired changes under the irq bus lock, then commit register writes in `bus_sync_unlock`.

## State And Persistence
Hardware registers hold direction, value, drive mode, interrupt detect mode, mask, and status. Software state in `update`, `intcnt`, and `set_irq_mask` batches one IRQ configuration transaction between lock and unlock. The PMIC parent owns regmap and regmap IRQ state.

## Dependencies And Integration Points
Depends on `intel_soc_pmic`, parent regmap, regmap IRQ mapping, gpiolib nested threaded IRQ support, debugfs seq output, and the platform device name `bxt_wcove_gpio`.

## Risks And Edge Cases
The advertised `ngpio` is 94 while only 13 physical pins have registers; consumers using virtual offsets get silent no-op behavior for many callbacks. `to_ireg` assumes the caller passes a physical GPIO. Pending IRQ batching uses a single set of fields, so only the current bus-locked line should be modified at a time. The threaded IRQ handler loops until status is clear and must avoid storms if ack writes fail.

## Test Signals
Test physical GPIO 0, 6, 7, and 12 register mapping, virtual GPIO offset behavior, drive open-drain/push-pull pinconf, all supported edge IRQ types, nested IRQ dispatch and ack, PMIC IRQ mapping failure, and debugfs output with register read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wcove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-winbond.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-winbond.c

## Purpose
Provides GPIO support for Winbond/Nuvoton Super I/O chips, currently W83627UHG/NCT6627UD, using legacy Super I/O extended function mode. GPIO ports are enabled and exposed according to module parameters.

## Important APIs, Types, And Functions
- `struct winbond_gpio_params` stores module-selected base address, enabled ports, output driver modes, and overrides for firmware-owned pins.
- Super I/O helpers `winbond_sio_enter`, `winbond_sio_leave`, `winbond_sio_select_logical`, `winbond_sio_reg_read/write`, and bit helpers manage the index/data port protocol.
- `struct winbond_gpio_info` describes each GPIO port's logical device, enable bit, output mode bit, direction, inversion, data registers, and possible conflicts.
- `winbond_gpio_get_info` maps a flat gpiolib offset to an enabled eight-pin port and applies GPIO2 safety restrictions.
- `winbond_gpio_get`, `winbond_gpio_direction_in`, `winbond_gpio_direction_out`, and `winbond_gpio_set` implement GPIO operations.
- `winbond_gpio_configure`, `winbond_gpio_check_chip`, `winbond_gpio_imatch`, and `winbond_gpio_iprobe` handle ISA probing, chip detection, port configuration, and chip registration.

## Control Flow
The ISA match path validates module masks, probes the configured or default Super I/O base addresses, and checks the chip ID. Probe enters extended mode, configures selected ports, disables ports with fatal conflicts, chooses push-pull/open-drain mode when requested, computes the total exposed line count, and registers one sleepable gpiochip. Each GPIO operation enters Super I/O mode, selects the relevant logical device, reads or writes direction/data/inversion bits, then exits extended mode.

## State And Persistence
Module parameters are global state and determine which hardware ports become visible. Hardware Super I/O registers persist until firmware or another driver changes them. There is no per-line shadow state. The base address is passed to gpiolib as driver data.

## Dependencies And Integration Points
Uses the ISA bus helper, I/O port resource muxing, Super I/O index/data ports at 0x2e or 0x4e, gpiolib, and module parameters for policy. It intentionally protects firmware-owned functions such as Power LED, BEEP, I2C, UARTs, and FDC unless overridden or only warned.

## Risks And Edge Cases
Incorrect module masks can expose or alter pins owned by firmware or serial/FDC/I2C functions. `winbond_gpio_get_info` assumes at least one enabled bit and relies on prior mask cleanup. GPIO2 has special per-pin restrictions that can surprise users with `-EACCES`. Super I/O enter/leave happens on every operation, so balanced release of the muxed region is critical. The module parameter descriptions appear to omit closing parentheses, which is cosmetic but visible.

## Test Signals
Validate chip-ID probing at both default bases, invalid `gpios` bits cleanup, push-pull/open-drain mutual exclusion, conflict disabling for FDC, warn-only UART conflicts, GPIO2 protected pins with and without overrides, inversion-aware get/set, and correct line count when GPIO6 contributes only five pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-winbond.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm831x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm831x.c

## Purpose
Exposes Wolfson WM831x PMIC GPIO pins through gpiolib, including direction/value operations, IRQ mapping, drive-mode pin configuration, debounce selection, and debugfs register reporting.

## Important APIs, Types, And Functions
- `struct wm831x_gpio` stores the parent `struct wm831x` and chip template copy.
- `wm831x_gpio_direction_in`, `wm831x_gpio_direction_out`, `wm831x_gpio_get`, and `wm831x_gpio_set` operate on `WM831X_GPIO1_CONTROL + offset` and `WM831X_GPIO_LEVEL`.
- `wm831x_gpio_to_irq` maps GPIO offsets through the parent IRQ domain.
- `wm831x_gpio_set_debounce` maps requested debounce intervals to GPIO function bits after checking the pin is in GPIO-capable mode.
- `wm831x_set_config` supports open-drain, push-pull, and input debounce pinconf.
- `wm831x_gpio_dbg_show` decodes pull, power-domain, polarity, drive, tristate, and level information.

## Control Flow
Probe inherits the parent fwnode, allocates private state, copies a static chip template, fills `ngpio` and base from parent data/platform data, and registers a sleepable chip. Direction input and output set direction, tristate, and function mask bits according to WM831x semantics; output direction then writes the requested level. Pinconf calls update either open-drain bits or debounce/function selection.

## State And Persistence
The driver keeps no shadowed GPIO state. Parent PMIC registers store levels, control mode, pull configuration, function selection, and IRQ domain mappings. Platform data can persist a legacy fixed GPIO base choice into chip registration.

## Dependencies And Integration Points
Depends on WM831x MFD core, WM831x GPIO/IRQ register definitions, parent IRQ domain, optional platform data, and gpiolib pinconf/debugfs hooks. Registered by `subsys_initcall` as `wm831x-gpio`.

## Risks And Edge Cases
Debounce support is encoded through function bits and only accepts broad 32-64 us or 4-8 ms ranges; other values fail. Pins not in GPIO-capable function modes return `-EBUSY` for debounce. `has_gpio_ena` inverts tristate interpretation, so direction handling differs by chip variant. Debugfs reads all pins including unrequested lines and can emit partial output on register errors.

## Test Signals
Check direction/value operations for multiple offsets, IRQ mapping from `WM831X_IRQ_GPIO_1`, fixed vs dynamic base, open-drain/push-pull pinconf, accepted and rejected debounce values, `has_gpio_ena` variants, and debugfs decoding of pull/power-domain/function fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm831x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm8350.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm8350.c

## Purpose
Provides basic gpiolib support for the 13 GPIO pins on Wolfson WM8350 PMICs using the parent MFD register accessors.

## Important APIs, Types, And Functions
- `struct wm8350_gpio_data` holds the parent `struct wm8350` and chip template copy.
- `wm8350_gpio_direction_in`, `wm8350_gpio_direction_out`, `wm8350_gpio_get`, and `wm8350_gpio_set` manipulate `WM8350_GPIO_CONFIGURATION_I_O` and `WM8350_GPIO_LEVEL`.
- `wm8350_gpio_to_irq` maps offsets to parent IRQ numbers when `wm8350->irq_base` is available.
- `wm8350_gpio_probe` copies the template chip, sets `ngpio = 13`, applies platform GPIO base if present, and registers the chip.

## Control Flow
Direction input sets the corresponding I/O bit. Direction output clears the I/O bit and then writes the requested level because hardware lacks atomic direction/value setup. Set updates the level bit through set/clear helpers. Get reads the shared GPIO level register and masks the requested offset.

## State And Persistence
There is no software shadow state. Direction and level live in WM8350 PMIC registers. Legacy platform data may set a fixed base; otherwise the chip uses dynamic GPIO numbering.

## Dependencies And Integration Points
Depends on WM8350 MFD core, platform data, WM8350 GPIO register definitions, parent IRQ base allocation, and gpiolib. The platform driver registers as `wm8350-gpio` via `subsys_initcall`.

## Risks And Edge Cases
Direction-output has a window where the pin becomes output before the new value is written. `to_irq` fails when the parent has no IRQ base. The driver has no `get_direction`, pinconf, or debugfs support, so consumers cannot query some hardware state through standard callbacks.

## Test Signals
Verify 13-line registration, fixed and dynamic base behavior, direction bit polarity, value read/write paths, output direction ordering, IRQ mapping with and without parent IRQ base, and error propagation from parent register helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm8350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm8994.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm8994.c

## Purpose
Exposes GPIO pins on Wolfson WM8994-family audio devices, including variant-specific request restrictions, direction/value operations, drive-mode pin configuration, IRQ mapping, and debugfs alternate-function reporting.

## Important APIs, Types, And Functions
- `struct wm8994_gpio` stores the parent `struct wm8994` and chip template copy.
- `wm8994_gpio_request` rejects unsupported WM8958 GPIO offsets.
- `wm8994_gpio_direction_in`, `wm8994_gpio_direction_out`, `wm8994_gpio_get`, and `wm8994_gpio_set` access per-pin `WM8994_GPIO_1 + offset` registers.
- `wm8994_gpio_set_config` supports open-drain and push-pull output configuration.
- `wm8994_gpio_to_irq` maps GPIO offsets through the parent's regmap IRQ data.
- `wm8994_gpio_dbg_show` decodes direction, pull, polarity, output type, and GPIO alternate function.

## Control Flow
Probe allocates private data, copies the template, sets `ngpio = WM8994_GPIO_MAX`, applies optional platform GPIO base, and registers a sleepable chip. Request checks reject unavailable WM8958 pins before consumers take them. Direction input sets `WM8994_GPN_DIR`; direction output writes direction and level bits together. Set updates only the level bit. Debugfs walks every pin and decodes the current control register.

## State And Persistence
No local GPIO shadow is kept. Per-pin WM8994 registers retain direction, level, pull, polarity, output configuration, and alternate-function state according to parent device lifetime.

## Dependencies And Integration Points
Depends on WM8994 MFD core, pdata, regmap IRQ support, GPIO and register definitions, gpiolib pinconf/debugfs hooks, and the platform driver `wm8994-gpio`.

## Risks And Edge Cases
Variant restrictions are hard-coded in `request`; unsupported WM8958 offsets must stay aligned with silicon capabilities. Debugfs reports alternate functions even for unrequested pins and must handle read failures. `wm8994_gpio_fn` labels `WM8994_GP_FN_FLL2_OUT` as "FLL1 output", which looks like a diagnostic string bug. IRQ mapping assumes parent regmap IRQ data is valid.

## Test Signals
Test WM8958 request rejection offsets, direction/value register bit updates, open-drain/push-pull pinconf, IRQ virq mapping, fixed/dynamic base handling, and debugfs alternate-function output including unsupported register read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-wm8994.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ws16c48.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ws16c48.c

## Purpose
Supports WinSystems WS16C48 ISA GPIO cards using `gpio-regmap` for 48 I/O-port-backed GPIOs and `regmap-irq` for edge interrupts on the first 24 lines.

## Important APIs, Types, And Functions
- Module parameters `base[]` and `irq[]` define ISA card instances and interrupt lines.
- `ws16c48_regmap_config` defines an 8-bit I/O-port regmap with access and volatility tables plus flat cache.
- `struct ws16c48_gpio` stores regmap, raw spinlock, and cached IRQ masks.
- `ws16c48_handle_pre_irq`, `ws16c48_handle_post_irq`, `ws16c48_handle_mask_sync`, and `ws16c48_set_type_config` implement page-lock-safe regmap-IRQ callbacks.
- `ws16c48_irq_init_hw` disables interrupts and selects the interrupt-ID page.
- `ws16c48_probe` requests/maps the I/O port range, creates regmap and regmap IRQ chip, then registers a gpio-regmap chip.

## Control Flow
Probe reserves the ISA I/O range, maps it, initializes a regmap, configures the regmap IRQ chip with status/mask/ack bases on paged registers, disables all interrupts, adds the IRQ chip for the supplied IRQ line, and registers a 48-line `gpio_regmap`. Direction and value operations are delegated to gpio-regmap with the data register used for data, set, and output-direction semantics; writing a 0 allows a line to be used as input. IRQ mask sync and type configuration temporarily select ENAB or POL pages, update registers, and return to INT_ID page under the raw spinlock.

## State And Persistence
Hardware page, data, polarity, enable, and interrupt-ID registers are the source of truth. The driver caches the last IRQ mask per register in `irq_mask` to avoid redundant page writes. Module parameters define instance identity for the module lifetime.

## Dependencies And Integration Points
Depends on ISA helper macros, ioport mapping, regmap MMIO over I/O ports, regmap-IRQ, gpio-regmap, module hardware parameter arrays, and raw spin locking to coordinate page selection between GPIO and IRQ flows.

## Risks And Edge Cases
The card uses a page/lock register shared by interrupt polarity, enable, and ID registers; missing lock coverage can target the wrong page. Only rising and falling edge types are supported despite regmap IRQ entries allowing edge-both support. `base[]` and `irq[]` module arrays must have matching instances. Direction semantics are unusual because output data also controls whether a line can float as input.

## Test Signals
Probe with multiple base/IRQ pairs, region-busy failure, regmap access-table enforcement, initial interrupt-disable programming, rising/falling IRQ polarity writes, mask sync cache behavior, page restoration to INT_ID, and gpio-regmap get/set/direction behavior across all six 8-bit ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ws16c48.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgene-sb.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgene-sb.c

## Purpose
Implements the AppliedMicro X-Gene standby GPIO controller. It exposes a small MMIO GPIO block with a hierarchical IRQ domain for a configurable subset of pins and supports OF and ACPI-described systems.

## Important APIs, Types, And Functions
- `struct xgene_gpio_sb` stores a generic GPIO chip, register base, IRQ domain, IRQ-capable pin range, and parent IRQ base.
- `xgene_gpio_set_bit` performs read-modify-write bit updates via generic GPIO register helpers.
- `xgene_gpio_sb_irq_set_type`, `xgene_gpio_sb_irq_mask`, and `xgene_gpio_sb_irq_unmask` implement child irqchip operations.
- `xgene_gpio_sb_to_irq` builds an IRQ fwspec for GPIO-to-IRQ mapping.
- Domain callbacks `xgene_gpio_sb_domain_translate`, `xgene_gpio_sb_domain_alloc`, `xgene_gpio_sb_domain_activate`, and `xgene_gpio_sb_domain_deactivate` bridge child hwirqs to parent interrupts and lock GPIOs as IRQs.
- `xgene_gpio_sb_probe` initializes generic GPIO operations, property defaults, hierarchical domain, and ACPI GPIO event interrupts.

## Control Flow
Probe maps registers, obtains the platform IRQ's parent domain and hwirq as the parent base, initializes a generic chip for input/output/direction registers, reads optional `apm,irq-start`, `apm,nr-irqs`, and `apm,nr-gpios`, creates a hierarchical domain, registers the gpiochip, and requests ACPI GPIO event interrupts. GPIO-to-IRQ mapping is allowed only in the configured IRQ-capable range. Domain allocation maps child hwirqs to parent fwspecs with OF GIC or fwnode irqchip formatting.

## State And Persistence
Hardware registers store GPIO output, output enable, input, interrupt level, and select bits. Software state stores the IRQ-capable window and hierarchical IRQ domain. Remove frees ACPI interrupts and removes the domain.

## Dependencies And Integration Points
Depends on gpiolib generic MMIO, irqdomain hierarchy APIs, parent IRQ chip support, ACPI GPIO event helpers from `gpiolib-acpi.h`, OF/ACPI matching, and platform properties.

## Risks And Edge Cases
`xgene_gpio_sb_to_irq` uses `gpio > HWIRQ_TO_GPIO(priv, priv->nirq)`, which appears off by one because valid hwirq values are 0 to `nirq - 1`. IRQ type support collapses both-edge child requests to parent rising-edge and all non-both requests to parent level-high, relying on local level selection. Parent fwspec construction differs for OF and fwnode irqchips and can fail on unexpected parent domains. GPIO select bits use `gpio * 2`, making bit indexing important.

## Test Signals
Check default and property-specified IRQ windows, GPIO-to-IRQ boundaries, OF and ACPI matches, hierarchical allocation parent fwspecs, activation/deactivation GPIO lock behavior, interrupt type propagation for edge/level cases, and ACPI event request/free on probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgene-sb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgene.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgene.c

## Purpose
Provides the main AppliedMicro X-Gene SoC GPIO controller driver for up to 48 GPIOs in three banks, with simple MMIO direction/value handling and suspend/resume context save.

## Important APIs, Types, And Functions
- `struct xgene_gpio` stores the gpiochip, MMIO base, spinlock, and saved `SET_DR` register values for three banks.
- `xgene_gpio_get`, `xgene_gpio_set`, `xgene_gpio_get_direction`, `xgene_gpio_dir_in`, and `xgene_gpio_dir_out` implement gpiolib operations using bank and bit macros.
- `__xgene_gpio_set` updates the output bit portion of the `GPIO_SET_DR_OFFSET` register.
- `xgene_gpio_suspend` and `xgene_gpio_resume` save and restore the three direction/output registers.
- `xgene_gpio_probe` maps the resource, initializes callbacks, and registers the chip.

## Control Flow
GPIO offsets are split into 16-line banks. Direction state lives in the low 16 bits of each bank's set/direction register, where set means input and clear means output. Output state uses the corresponding bit shifted by 16. Direction-output clears the direction bit and writes the value while holding the spinlock. Suspend copies each bank's `SET_DR` register into `set_dr_val`; resume writes them back.

## State And Persistence
The only software state beyond the spinlock is the suspend context array. Hardware registers hold live direction and output state. The driver is built in via `builtin_platform_driver` and has no remove path.

## Dependencies And Integration Points
Depends on platform MMIO resources, OF compatible `apm,xgene-gpio`, optional ACPI ID `APMC0D14`, gpiolib, and system sleep PM hooks.

## Risks And Edge Cases
No IRQ support is provided in this main controller. The set/direction register packs direction and output bits, so careless read-modify-write can corrupt direction while changing value. `ngpio` is fixed at 48 with no property override. Suspend/resume assumes all three banks exist and remain powered consistently.

## Test Signals
Verify bank/bit calculations at offsets 15/16/31/32/47, direction bit polarity, output value bit shift by 16, spinlocked RMW sequences, ACPI and OF binding, and suspend/resume restoration of all bank registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgene.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgs-iproc.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgs-iproc.c

## Purpose
Supports Broadcom XGS iProc CCA GPIO controllers using generic MMIO GPIO helpers plus an optional shared parent interrupt line for level and edge GPIO interrupts.

## Important APIs, Types, And Functions
- `struct iproc_gpio_chip` embeds `gpio_generic_chip`, lock, device pointer, GPIO register base, and interrupt-controller register base.
- `iproc_gpio_irq_ack`, `iproc_gpio_irq_mask`, `iproc_gpio_irq_unmask`, and `iproc_gpio_irq_set_type` manipulate event, level, polarity, and mask registers.
- `iproc_gpio_irq_handler` services the shared parent IRQ and dispatches child GPIO IRQs.
- `iproc_gpio_probe` initializes the generic GPIO chip, optional IRQ support, and registers the chip.
- `iproc_gpio_remove` disables the CCA GPIO interrupt bit when the interrupt block was mapped.

## Control Flow
Probe maps the GPIO resource, initializes generic data/output/direction registers, optionally overrides `ngpio`, and if a platform IRQ exists maps the interrupt resource, enables the CCA GPIO interrupt bit, requests a shared IRQ, and installs a simple child irqchip. The handler checks the top-level CCA status bit, combines enabled edge-event bits and active level bits, and dispatches all pending child interrupts through the gpio IRQ domain.

## State And Persistence
Hardware registers hold data, output enable, event/level polarity, masks, and top-level interrupt enable. The driver keeps no shadow state; it uses the spinlock for interrupt register RMW operations. Remove clears the top-level GPIO interrupt enable bit.

## Dependencies And Integration Points
Uses gpiolib generic MMIO, shared IRQ registration, simple child IRQ domains, OF compatible `brcm,iproc-gpio-cca`, and optional `ngpios` device-tree property.

## Risks And Edge Cases
The parent IRQ is shared and requested directly, so the handler must return `IRQ_NONE` when no GPIO status is present. Edge ack writes to the event status register only for edge-triggered lines. Level status is synthesized from input data XOR polarity and mask bits. Concurrent type/mask/ack changes are protected by a spinlock but normal GPIO generic operations may also touch nearby registers.

## Test Signals
Probe with and without IRQ resource, custom `ngpios`, shared IRQ no-status path, edge rising/falling ack and polarity programming, level high/low status synthesis, mask/unmask register changes, and top-level interrupt disable on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgs-iproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xilinx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xilinx.c

## Purpose
Implements gpiolib and optional interrupt support for Xilinx XPS/AXI GPIO IP. It handles one or two channels, configurable widths, default output/direction state, runtime PM/clock management, and software edge detection for per-line IRQs.

## Important APIs, Types, And Functions
- `struct xgpio_instance` stores the gpiochip, MMIO base, logical-to-hardware bitmap map, shadow state/direction/IRQ bitmaps, raw spinlock, optional parent IRQ, and clock.
- Channel helpers `xgpio_read_ch`, `xgpio_write_ch`, `xgpio_read_ch_all`, and `xgpio_write_ch_all` abstract 32-bit channel register accesses.
- GPIO callbacks `xgpio_get`, `xgpio_set`, `xgpio_set_multiple`, `xgpio_dir_in`, and `xgpio_dir_out` translate software offsets through the sparse hardware bitmap.
- PM callbacks `xgpio_request`, `xgpio_free`, runtime suspend/resume, and system suspend/resume manage clock/runtime PM.
- IRQ callbacks `xgpio_irq_mask`, `xgpio_irq_unmask`, `xgpio_set_irq_type`, and `xgpio_irqhandler` implement per-line edge detection from channel-change interrupts.
- `xgpio_probe` parses properties, initializes shadows and hardware, configures optional IRQ, and registers the chip.

## Control Flow
Probe reads `xlnx,is-dual`, default output and tristate properties, channel widths, builds a 64-bit hardware map, maps registers, enables the optional clock, starts runtime PM, writes initial data and direction registers, and optionally initializes interrupt registers and a chained irqchip. GPIO set/direction operations update shadow bitmaps under the raw spinlock and write the corresponding channel register. The interrupt handler acks per-channel status, reads current hardware values, compares them with `last_irq_read`, filters by enabled/rising/falling bitmaps, gathers hardware bits back into logical GPIO offsets, and dispatches child IRQs.

## State And Persistence
The driver maintains shadow output `state`, direction `dir`, last IRQ sample, enabled IRQs, and requested rising/falling edges. These shadows are rewritten to hardware on probe and used for RMW safety. Runtime PM disables/enables the clock; system sleep may force runtime suspend unless the parent IRQ is configured as a wake source.

## Dependencies And Integration Points
Depends on device properties from Xilinx IP, optional clock provider, platform MMIO/IRQ resources, PM runtime, gpiolib irqchip integration, and OF compatible `xlnx,xps-gpio-1.00.a`.

## Risks And Edge Cases
The hardware only reports channel-level changes, so per-line IRQs are synthesized by comparing snapshots; missed changes are possible if a line toggles back between samples. Width and bitmap mapping are critical for dual-channel devices and sparse logical numbering. `xgpio_request` returns a negative PM error but does not undo a failed `pm_runtime_get_sync`. Clock state and GPIO access depend on correct request/free and IRQ-resource PM balancing. Only edge triggers are supported.

## Test Signals
Cover single and dual channel widths, invalid widths over 32, default state/tri properties, set_multiple mapping, runtime PM request/free clock behavior, IRQ type rejection for level triggers, rising/falling/both edge detection from `last_irq_read`, channel interrupt enable/disable transitions, and suspend behavior with and without wake IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xilinx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xlp.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xlp.c

## Purpose
Provides GPIO and chained interrupt support for Broadcom/Netlogic XLP GPIO controllers, exposing 70 GPIOs out of a register layout capable of up to 96 lines.

## Important APIs, Types, And Functions
- `struct xlp_gpio_priv` stores the gpiochip, enabled IRQ bitmap, pointers to interrupt/output/pad-drive register groups, and spinlock.
- `xlp_gpio_get_reg` and `xlp_gpio_set_reg` access bit positions across 32-bit register banks.
- IRQ callbacks `xlp_gpio_irq_enable`, `xlp_gpio_irq_disable`, `xlp_gpio_irq_mask_ack`, `xlp_gpio_irq_unmask`, and `xlp_gpio_set_irq_type` control interrupt enable, status ack, type, and polarity.
- `xlp_gpio_generic_handler` walks enabled GPIOs, reads status registers by bank, and dispatches pending child IRQs.
- GPIO callbacks `xlp_gpio_dir_output`, `xlp_gpio_dir_input`, `xlp_gpio_get`, and `xlp_gpio_set` manage output-enable and pad-drive bits.

## Control Flow
Probe maps the controller, gets the parent IRQ, sets register pointers from the base, initializes a 70-line gpiochip, attaches a chained irqchip to the parent, and registers the chip. Direction output enables output drive but ignores the requested initial state; value changes are handled separately through the pad-drive register. IRQ unmask enables the hardware bit and records it in `gpio_enabled_mask`; the chained handler only scans enabled GPIOs and dispatches those with status set.

## State And Persistence
Hardware registers retain output-enable, pad-drive, interrupt enable, type, polarity, and status. Software tracks enabled child IRQs in `gpio_enabled_mask` so the chained handler can avoid scanning disabled lines.

## Dependencies And Integration Points
Depends on platform MMIO and IRQ resources, gpiolib chained irqchip APIs, ACPI IDs `BRCM9006` and `CAV9006`, and fixed XLP register layout constants.

## Risks And Edge Cases
`direction_output` does not apply the requested initial output value, which may surprise consumers expecting gpiolib semantics. `gpio_chip.base` is fixed at 0. IRQ enable only calls `gpiochip_enable_irq`; hardware enabling happens in unmask, so handler setup must follow the expected core order. Only 70 GPIOs are exposed although the register layout supports 96.

## Test Signals
Check output direction plus initial value behavior, get/set on pad-drive bits, direction input/output register bits, IRQ type/polarity for all four trigger modes, mask-ack status clearing, enabled-mask scanning across 32-bit register boundaries, ACPI binding, and parent chained handler dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xlp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xra1403.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xra1403.c

## Purpose
Supports the EXAR XRA1403 16-bit SPI GPIO expander using regmap-backed direction and value registers, with optional reset GPIO handling and debugfs register dumping.

## Important APIs, Types, And Functions
- `struct xra1403` stores the `gpio_chip` and SPI regmap.
- `xra1403_regmap_cfg` defines the 7-bit register plus pad-bit SPI format.
- `to_reg` maps a 16-bit line offset to low or high byte register addresses.
- `xra1403_direction_input`, `xra1403_direction_output`, `xra1403_get_direction`, `xra1403_get`, and `xra1403_set` implement gpiolib callbacks.
- `xra1403_dbg_show` dumps raw registers and requested line state when debugfs is enabled.
- `xra1403_probe` optionally deasserts reset, initializes regmap, and registers the chip.

## Control Flow
Probe allocates state, requests an optional active-low reset GPIO as output-low to bring the expander out of reset, initializes chip callbacks and metadata, creates an SPI regmap, and registers a 16-line sleepable chip. Direction input sets the bit in `XRA_GCR`; direction output clears the bit and writes the output-control register. Get reads `XRA_GSR`; set updates `XRA_OCR`.

## State And Persistence
No software shadow is maintained. XRA1403 registers store direction, output control, input polarity, pull-ups, interrupt settings, and input filter state. The driver only manipulates direction and output/value registers, while debugfs reads the broader register file.

## Dependencies And Integration Points
Depends on SPI, regmap, optional GPIO descriptor named `reset`, gpiolib, OF compatible `exar,xra1403`, and SPI ID `xra1403`.

## Risks And Edge Cases
If reset GPIO acquisition returns an error, probe only warns and continues, which may leave the expander held in reset on boards where reset is required. Direction-output is non-atomic between direction and value writes. IRQ registers exist but this driver does not wire them into Linux IRQs. Debugfs ignores regmap read errors while building the raw dump.

## Test Signals
Validate low/high byte mapping for offsets 7 and 8, direction bit polarity, output register writes, reset GPIO present/absent/error cases, SPI regmap format, debugfs dump output, and probe from both SPI ID and OF compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xra1403.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xtensa.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xtensa.c

## Purpose
Exposes the Xtensa LX4 GPIO32 optional TIE extension as two gpiolib chips: `impwire` for 32 input-only wires and `expstate` for 32 output-only state bits.

## Important APIs, Types, And Functions
- `enable_cp` and `disable_cp` save/restore interrupt state and CPENABLE access to the Xtensa GPIO32 coprocessor when needed.
- `xtensa_impwire_get_direction` and `xtensa_impwire_get_value` expose input direction and the `read_impwire` instruction.
- `xtensa_expstate_get_direction`, `xtensa_expstate_get_value`, and `xtensa_expstate_set_value` expose output direction, `rur.expstate`, and `wrmsk_expstate`.
- Static `impwire_chip` and `expstate_chip` define the two 32-line gpiochips.
- `xtensa_gpio_init` creates a simple platform device and registers the platform driver.

## Control Flow
At init, the driver registers a synthetic `xtensa-gpio` platform device and then the matching driver. Probe registers the input chip first, then the output chip. Each hardware access temporarily enables the required coprocessor bit, executes the TIE instruction, and restores CPENABLE and interrupts.

## State And Persistence
The driver has no heap-allocated private state and no software shadow. `IMPWIRE` and `EXPSTATE` are CPU/core architectural states. The static chips persist for the module/built-in lifetime.

## Dependencies And Integration Points
Depends on Xtensa architecture support, `asm/coprocessor.h`, compile-time `XCHAL_CP_ID_XTIOP`, platform-device helpers, and gpiolib. The source explicitly notes it is incompatible with SMP because GPIO32 availability and wires can be core-local.

## Risks And Edge Cases
If registering `expstate_chip` fails after `impwire_chip` succeeds, the first chip is not removed. The driver registers a platform device before registering the driver and has no cleanup path for failure after device creation. Static gpiochips and core-local coprocessor state make SMP unsafe. Access depends on correct CPENABLE save/restore under local IRQ disable.

## Test Signals
Build for Xtensa variants with and without `XCHAL_HAVE_CP`, read input bits via `read_impwire`, read/write output bits via `EXPSTATE`, verify direction reporting, inject second-chip registration failure, and confirm the driver is not enabled on SMP configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-xtensa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-zevio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-zevio.c

## Purpose
Implements GPIO support for the LSI ZEVIO SoC's four-section, 32-line memory-mapped GPIO controller. Interrupts are intentionally disabled and not exposed due to known lockups.

## Important APIs, Types, And Functions
- `struct zevio_gpio` stores the gpiochip, spinlock, and MMIO base.
- `zevio_gpio_port_get` and `zevio_gpio_port_set` calculate the eight-line section offset and access per-section registers.
- `zevio_gpio_get`, `zevio_gpio_set`, `zevio_gpio_direction_input`, and `zevio_gpio_direction_output` implement gpiolib callbacks.
- `zevio_gpio_to_irq` returns `-ENXIO` because IRQ support is not implemented.
- `zevio_gpio_probe` maps registers, registers the chip, initializes locking, and masks interrupts in all sections.

## Control Flow
Probe copies a static chip template, assigns parent and fwnode-derived label, maps the MMIO resource, registers the 32-line chip, initializes the spinlock, and writes `0xFF` to each section's interrupt-mask register. Reads choose the input register for pins whose direction bit is set and the output register otherwise. Direction output writes the requested output value first, then clears the direction bit.

## State And Persistence
Hardware registers store direction, output, input, and interrupt mask/status state. The driver has no shadow state. Interrupts are masked at probe and remain unsupported through gpiolib.

## Dependencies And Integration Points
Depends on platform MMIO resources, OF compatible `lsi,zevio-gpio`, gpiolib, fwnode labeling, and built-in platform driver registration.

## Risks And Edge Cases
The spinlock is initialized after `devm_gpiochip_add_data`, leaving a small theoretical window if callbacks could run immediately during registration. IRQ-related registers are present but intentionally disabled, so consumers requiring interrupts will fail. The section math assumes exactly four sections and 32 lines.

## Test Signals
Check section/bit mapping at pins 7, 8, 15, 16, 31, direction bit polarity, output-before-direction behavior, interrupt mask writes for each section, `to_irq` failure, and callback safety around probe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-zevio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-zynq.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-zynq.c

## Purpose
Implements the Xilinx Zynq, ZynqMP, Versal, and PMC GPIO controller driver. It supports banked MMIO GPIO, per-bank interrupt handling, variant-specific bank layouts and quirks, runtime PM/clock management, wakeup, and suspend/resume context save.

## Important APIs, Types, And Functions
- `struct zynq_gpio` stores the gpiochip, MMIO base, clock, parent IRQ, platform data, saved register context, and direction spinlock.
- `struct zynq_platform_data` describes label, quirks, total line count, max bank, and logical bank min/max ranges.
- `zynq_gpio_get_bank_pin` maps logical GPIO numbers to hardware bank and bank-local pin, with Versal unused-bank skipping.
- GPIO callbacks `zynq_gpio_get_value`, `zynq_gpio_set_value`, `zynq_gpio_dir_in`, `zynq_gpio_dir_out`, and `zynq_gpio_get_direction` handle register access and variant quirks.
- IRQ callbacks `zynq_gpio_irq_mask`, `zynq_gpio_irq_unmask`, `zynq_gpio_irq_ack`, `zynq_gpio_irq_enable`, `zynq_gpio_set_irq_type`, `zynq_gpio_set_wake`, `zynq_gpio_irq_reqres`, and `zynq_gpio_irq_relres` implement per-line interrupt behavior.
- `zynq_gpio_irqhandler` scans bank interrupt status/mask registers and dispatches child IRQs.
- `zynq_gpio_save_context` and `zynq_gpio_restore_context` preserve data, direction, and interrupt configuration around suspend.

## Control Flow
Probe selects platform data from OF match, maps registers, obtains the parent IRQ and clock, initializes runtime PM, disables all interrupts in each active bank, sets up a chained gpio irqchip, registers the gpiochip, marks the parent IRQ disable-unlazy, enables device wakeup, and drops the runtime PM reference. GPIO set uses mask/data LSW/MSW write-only registers so only one pin changes. Direction-output sets direction and output-enable bits under lock before writing the value. IRQ type programming updates INT_TYPE, INT_POLARITY, and INT_ANY and switches the child irqchip/handler between level and edge descriptors. The chained handler reads each bank's pending enabled bits and dispatches child IRQs using logical bank offsets.

## State And Persistence
Hardware registers store data, direction, output enable, interrupt mask/status/type/polarity/any-edge state. Software context arrays save data mask registers, direction, interrupt mask, type, polarity, and any-edge state across non-wakeup suspend. Runtime PM manages the clock, and each requested GPIO/IRQ holds runtime PM references through request/free or IRQ resource callbacks.

## Dependencies And Integration Points
Depends on OF compatibles for Zynq, ZynqMP, Versal, and PMC variants, platform MMIO/IRQ/clock resources, gpiolib chained IRQ support, runtime PM, wakeup APIs, and Xilinx-specific bank-layout quirks including the data read-only bug.

## Risks And Edge Cases
Bank mapping is variant-specific and Versal skips unused hardware banks by mutating the loop index inside loops. Zynq bank 0 pins 7 and 8 cannot be inputs. The data read path has a quirk-dependent choice between DATA_RO and DATA registers. Suspend stores `INTMASK` but restore writes the complement to `INTEN`, so mask semantics must stay understood. Runtime PM references are held from both GPIO requests and IRQ resources. Edge interrupts use `handle_level_irq` after type setup, which is intentional for this controller but easy to misread.

## Test Signals
Validate every variant's total lines and bank min/max mapping, pins at bank boundaries, Zynq bank0 pin 7/8 input rejection, mask/data writes for lower and upper half pins, DATA_RO bug paths, all IRQ trigger types and handler switching, wake-enabled suspend paths, context save/restore, runtime PM request/free and IRQ resource balancing, and Versal unused-bank loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-zynq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-zynqmp-modepin.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-zynqmp-modepin.c

## Purpose
Exposes the four ZynqMP PS_MODE boot configuration pins as a small gpiolib controller using Xilinx firmware calls to read and write the boot-mode register.

## Important APIs, Types, And Functions
- `MODE_PINS` defines the four GPIO lines.
- `modepin_gpio_get_value` calls `zynqmp_pm_bootmode_read` and decodes direction, input, and output bit fields.
- `modepin_gpio_set_value` reads the current boot-mode value, marks the pin as output, updates the output bit, and writes it with `zynqmp_pm_bootmode_write`.
- `modepin_gpio_dir_in` is a no-op that reports success.
- `modepin_gpio_dir_out` delegates to `modepin_gpio_set_value`.
- `modepin_gpio_probe` allocates and registers the four-line gpiochip.

## Control Flow
Probe fills a dynamic-base gpiochip with get/set/direction callbacks and registers it for compatible `xlnx,zynqmp-gpio-modepin`. Reads inspect bit `pin` to decide whether the output bit field `[8:11]` or input status field `[4:7]` reflects the current value. Writes always set bit `pin` to configure output mode and then update bit `pin + 8`.

## State And Persistence
The driver has no private state beyond the gpiochip. State resides in the firmware-managed boot-mode register. Because writes go through platform firmware, persistence and side effects follow ZynqMP firmware policy.

## Dependencies And Integration Points
Depends on the Xilinx ZynqMP firmware interface, platform bus/OF compatible matching, and gpiolib. It is distinct from the main Zynq GPIO controller and only covers PS_MODE pins.

## Risks And Edge Cases
`modepin_gpio_set_value` ignores the return value of the initial bootmode read, so a failed read can lead to writing a zero-based register value. `direction_input` does not clear the output-enable bit and is effectively a no-op. There is no `get_direction` callback. Firmware call failures are returned for writes and reads but only writes log an error.

## Test Signals
Verify get decoding for input and output modes, set preserving unrelated boot-mode bits after a successful read, read-failure behavior before write, direction-input no-op semantics, four-line bounds through gpiolib, firmware write failure propagation, and OF compatible probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-zynqmp-modepin.c -->
