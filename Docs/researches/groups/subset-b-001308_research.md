# Research: subset-b-001308 GPIO gpiolib ACPI, firmware, cdev, shared, sysfs

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi-core.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi-core.c

## Purpose
`gpiolib-acpi-core.c` is the ACPI integration layer for the GPIO subsystem. It translates ACPI `GpioIo` and `GpioInt` resources into Linux GPIO descriptors, installs ACPI GPIO operation-region handlers, maps ACPI GPIO interrupts to Linux IRQs, manages ACPI event methods (`_Exx`, `_Lxx`, `_EVT`), and exposes ACPI-specific helpers to consumer drivers.

## Important APIs, Types, And Functions
`struct acpi_gpio_event` stores one ACPI event GPIO, including ACPI method handle, pin, IRQ, IRQ flags, wake capability, request state, and the owned descriptor. `struct acpi_gpio_connection` caches descriptors used by GPIO OpRegions. `struct acpi_gpio_chip` is attached to the ACPI controller handle and owns event and OpRegion state. `struct acpi_gpio_info` carries parsed resource metadata back to descriptor lookup callers.

Public/exported entry points include `acpi_gpio_get_irq_resource()`, `acpi_gpio_get_io_resource()`, `acpi_gpiochip_request_interrupts()`, `acpi_gpiochip_free_interrupts()`, `acpi_dev_add_driver_gpios()`, `acpi_dev_remove_driver_gpios()`, `devm_acpi_dev_add_driver_gpios()`, `acpi_find_gpio()`, `acpi_dev_gpio_irq_wake_get_by()`, `acpi_gpiochip_add()`, `acpi_gpiochip_remove()`, and `acpi_gpio_count()`.

Key internal functions are `acpi_get_gpiod()`, `acpi_gpiochip_alloc_event()`, `acpi_gpio_adr_space_handler()`, `acpi_get_gpiod_by_index()`, `acpi_get_gpiod_from_data()`, `acpi_gpio_property_lookup()`, `acpi_gpio_resource_lookup()`, `acpi_gpio_to_gpiod_flags()`, and `acpi_request_own_gpiod()`.

## Control Flow
GPIO chip registration calls `acpi_gpiochip_add()`, which allocates `struct acpi_gpio_chip`, attaches it to the ACPI handle with `acpi_attach_data()`, installs the `ACPI_ADR_SPACE_GPIO` handler, and clears ACPI dependencies. Removal reverses this via `acpi_gpiochip_free_regions()`, `acpi_detach_data()`, and `kfree()`.

Consumer lookup starts in `acpi_find_gpio()`. It tries named `_DSD` GPIO properties using `for_each_gpio_property_name()`, falls back to driver-provided ACPI GPIO mappings if present, then optionally falls back to raw `_CRS` GPIO resources only when the device has no properties and the lookup has no connection ID. Resource walking fills `acpi_gpio_info`, resolves the controller path through `acpi_get_gpiod()`, converts ACPI polarity/pull/direction into gpiod and lookup flags, and applies debounce.

`acpi_gpiochip_request_interrupts()` walks `_AEI` resources. For each `GpioInt`, `acpi_gpiochip_alloc_event()` looks for `_Exx` or `_Lxx` event methods, or `_EVT`, applies interrupt/wake ignore quirks, requests an owned descriptor, locks it as IRQ, resolves `gpiod_to_irq()`, derives IRQ trigger flags, and appends it to the chip event list. Actual `request_threaded_irq()` may be deferred through the ACPI quirks deferred list.

`acpi_gpio_adr_space_handler()` services ACPI OpRegion reads and writes by decoding the connection resource, looking up or caching descriptors per pin under `conn_lock`, borrowing shared event descriptors for read-only shared pins, and using raw GPIO value access to update the ACPI value words.

## State And Persistence
State is kernel-resident and tied to GPIO chip lifetime. `struct acpi_gpio_chip` is attached as ACPI handle data. Event descriptors and OpRegion cached connections live in lists under that object. IRQ wake enablement and requested state are explicit so cleanup can disable wake, free IRQs, unlock IRQ ownership, free owned descriptors, and free event nodes. Driver GPIO mappings are stored on `adev->driver_gpios` until removed or devres cleanup runs.

## Dependencies And Integration Points
This file depends on ACPICA resource walking and address-space handlers, gpiolib descriptor APIs, GPIO chip registration, Linux IRQ APIs, pinctrl-related GPIO configuration, DMI/quirk helpers from `gpiolib-acpi-quirks.c`, and firmware-node property naming helpers. It integrates with consumer APIs through `acpi_find_gpio()` and `acpi_gpio_count()`, with ACPI interrupt users through `acpi_dev_gpio_irq_wake_get_by()`, and with gpiochip lifecycle through `acpi_gpiochip_add/remove()` plus interrupt request/free hooks.

## Risks
Firmware description errors are the main risk: wrong polarity, wake flags, debounce units, resource indices, or missing controller registration can lead to incorrect direction, deferred probe, or unusable interrupts. Event handlers intentionally execute ACPI methods from IRQ thread context, so ordering with OpRegion registration matters. OpRegion descriptor caching must be cleaned exactly once. The code has explicit FIXME comments about descriptor lifetime after putting GPIO device references, which is a long-standing reference model concern.

## Test Signals
Useful tests include ACPI `_DSD` and `_CRS` GPIO lookup on named and unnamed consumers, deferred GPIO controller probe returning `-EPROBE_DEFER`, `GpioInt` IRQ translation and trigger type setup, wake-capable IRQ handling under low-power S0, boot-time `_AEI` event execution toggled by quirks, OpRegion read/write AML tests, debounce conversion from ACPI units, and cleanup paths during gpiochip unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi-quirks.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi-quirks.c

## Purpose
`gpiolib-acpi-quirks.c` contains platform-specific policy for ACPI GPIO event handling. It controls whether edge-triggered ACPI event handlers run at boot, supports module-parameter override lists for ignoring wake or interrupt handling on specific controller/pin pairs, defers early ACPI IRQ registration until late init, and applies DMI-based defaults for machines with broken firmware behavior.

## Important APIs, Types, And Functions
The externally used helpers are `acpi_gpio_add_to_deferred_list()`, `acpi_gpio_remove_from_deferred_list()`, `acpi_gpio_need_run_edge_events_on_boot()`, and `acpi_gpio_in_ignore_list()`. `struct acpi_gpiolib_dmi_quirk` stores the DMI-derived actions: suppress boot edge events, ignore wake, and ignore interrupts. `gpiolib_acpi_quirks[]` is the DMI match table.

## Control Flow
At `postcore_initcall`, `acpi_gpio_setup_params()` finds the first matching DMI quirk and fills unset module parameters. If `run_edge_events_on_boot` remains automatic, it becomes disabled for affected machines and enabled otherwise. `ignore_wake` and `ignore_interrupt` are set from DMI only when the user did not provide module parameters.

GPIO chips that call ACPI interrupt registration too early enter `acpi_gpio_deferred_req_irqs_list` through `acpi_gpio_add_to_deferred_list()`. At `late_initcall_sync`, `acpi_gpio_handle_deferred_request_irqs()` processes the list by calling `acpi_gpio_process_deferred_list()` and then flips `acpi_gpio_deferred_req_irqs_done`, causing later chips to request IRQs immediately.

`acpi_gpio_in_ignore_list()` parses comma-separated `controller@pin` strings and compares controller names and numeric pins against the queried GPIO. Malformed input logs one error and returns false.

## State And Persistence
Global state consists of module parameters, a mutex-protected deferred IRQ list, and a boolean indicating that deferred processing has completed. The settings persist for the boot lifetime. DMI quirk data is `__initconst`; selected strings are installed into global pointers during init.

## Dependencies And Integration Points
The file depends on DMI matching, module parameter handling, list/mutex primitives, and the ACPI GPIO header. It is consumed directly by `gpiolib-acpi-core.c` when deciding whether to request ACPI event IRQs now, whether to synthesize boot edge events, and whether to ignore firmware wake or interrupt declarations.

## Risks
String parsing is intentionally simple and strict; a malformed user parameter disables all matches in that list after logging. DMI quirks are hardware-specific and can become stale as firmware changes. Deferral ordering is sensitive because it exists to let other built-in drivers register OpRegions before ACPI event methods can run.

## Test Signals
Test with module parameters overriding DMI defaults, DMI-matched machines that disable boot edge events, ignore-wake and ignore-interrupt lists with valid and invalid syntax, early gpiochip registration before late init, and late gpiochip registration after the deferred list has been drained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi.h

## Purpose
`gpiolib-acpi.h` is the internal ACPI GPIO interface shared by gpiolib core code and ACPI-specific implementation files. It declares gpiochip lifecycle hooks, ACPI descriptor lookup and counting helpers, deferred IRQ helpers, boot-event policy helpers, and ignore-list helpers.

## Important APIs, Types, And Functions
When `CONFIG_ACPI` is enabled, it declares `acpi_gpiochip_add()`, `acpi_gpiochip_remove()`, `acpi_gpiochip_request_interrupts()`, `acpi_gpiochip_free_interrupts()`, `acpi_find_gpio()`, and `acpi_gpio_count()`. Without ACPI, inline stubs either no-op or return `-ENOENT`/`-ENODEV`.

The header also declares `acpi_gpio_process_deferred_list()`, `acpi_gpio_add_to_deferred_list()`, `acpi_gpio_remove_from_deferred_list()`, `acpi_gpio_need_run_edge_events_on_boot()`, `enum acpi_gpio_ignore_list`, and `acpi_gpio_in_ignore_list()` for coordination between ACPI core and quirks code.

## Control Flow
Including code can call the same API regardless of build configuration. The compile-time branch keeps non-ACPI builds from needing ACPI implementation objects while preserving call sites in generic gpiolib lifecycle paths.

## State And Persistence
The header owns no runtime state. Its main persistence behavior is ABI-like internal contract stability between the ACPI implementation and generic gpiolib callers.

## Dependencies And Integration Points
It depends on `linux/err.h`, `linux/types.h`, and `linux/gpio/consumer.h`, with forward declarations for `gpio_chip`, `gpio_desc`, `gpio_device`, `device`, and `fwnode_handle`. It is integrated by `gpiolib-acpi-core.c`, `gpiolib-acpi-quirks.c`, and generic gpiochip registration paths.

## Risks
Stub return values affect generic fallback behavior in non-ACPI builds; changing them can alter probe deferral or not-found semantics. Any signature change requires coordinated updates across gpiolib and ACPI helpers.

## Test Signals
Build-test both `CONFIG_ACPI=y` and `CONFIG_ACPI=n`, verify non-ACPI builds link with stubs, and run ACPI GPIO lookup and gpiochip lifecycle tests in ACPI-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-cdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-cdev.c

## Purpose
`gpiolib-cdev.c` implements the GPIO character device ABI exposed as `/dev/gpiochipN`. It handles chip information, line information, line watching, v2 line requests, optional v1 handle/event ABI compatibility, edge event delivery, debounce support, hardware timestamp engine support, descriptor request/release, and gpiochip character device registration.

## Important APIs, Types, And Functions
The exported lifecycle functions are `gpiolib_cdev_register()` and `gpiolib_cdev_unregister()`. The main per-open chip state is `struct gpio_chardev_data`, which stores the GPIO device, watched-line bitmap, event FIFO, notifier blocks, wait queue, and file pointer. V2 requested lines use `struct linereq` and per-line `struct line`. V1 compatibility uses `struct linehandle_state` and `struct lineevent_state` under `CONFIG_GPIO_CDEV_V1`.

Important v2 helpers include `gpio_v2_line_config_validate()`, `gpio_v2_line_flags_validate()`, `linereq_create()`, `linereq_ioctl()`, `linereq_get_values()`, `linereq_set_values()`, `linereq_set_config()`, `edge_detector_setup()`, `edge_detector_update()`, `edge_detector_stop()`, `debounce_setup()`, `debounce_work_func()`, `edge_irq_handler()`, and `edge_irq_thread()`. Line info helpers include `gpio_desc_to_lineinfo()`, `lineinfo_get()`, `lineinfo_unwatch()`, `lineinfo_changed_notify()`, and `lineinfo_watch_read()`.

## Control Flow
`gpiolib_cdev_register()` initializes `gdev->chrdev`, assigns `devt`, creates an ordered high-priority workqueue for line-state notifications, and registers the cdev/device pair. Opening `/dev/gpiochipN` allocates `gpio_chardev_data`, creates a watched-line bitmap, registers raw line-state and blocking device-unregister notifiers, stores the file pointer, and returns a nonseekable file.

Chip ioctls dispatch through `gpio_ioctl()`. They return chip info, line info, line watch setup, line unwatch, v2 line request creation, and optional v1 handle/event creation. All ioctl paths guard `gdev->srcu` and fail with `-ENODEV` once the chip disappears.

V2 line requests copy and validate `gpio_v2_line_request`, allocate a flexible `linereq`, request each descriptor, apply flags, set transitory false, configure direction and output values, optionally set up edge detection, notify requested state, register an unregister notifier, and return an anonymous file descriptor. The line fd supports get/set values, reconfiguration, poll, read, and proc fdinfo.

Edge handling uses either IRQ hard/thread handlers, software debounce delayed work, or HTE callbacks. Events enter a kfifo under the waitqueue spinlock and wake poll waiters. Overflow drops the oldest v2 event via `kfifo_skip()` and logs rate-limited debug.

Line-info watching records watched offsets in a bitmap. Descriptor state notifications allocate a context in atomic context, snapshot line info without sleeping, then finish the pinctrl-dependent used-line check and FIFO insertion in the gpio device ordered workqueue.

## State And Persistence
All state is in-memory and scoped by file descriptors or gpiochip registration. Descriptor flags are updated to reflect requested direction, active-low, bias, drive, edge, clock, and debounce state. `linereq` stores sequence numbers, event FIFO, per-line debounce and timestamp fields, and a config mutex. `gpio_chardev_data` stores watch ABI version for v1/v2 compatibility and a watched-line bitmap. Cleanup unregisters notifiers, stops edge detectors, frees IRQs/HTE handles/work, frees descriptors, drops GPIO device refs, and frees FIFOs.

## Dependencies And Integration Points
The file depends on anon inodes, cdev, file descriptor allocation helpers, kfifo, wait queues, poll, mutex/spinlock/SRCU, IRQ APIs, workqueues, timekeeping, uaccess, HTE, pinctrl, and UAPI structures from `uapi/linux/gpio.h`. It integrates with descriptor state notifications emitted elsewhere in gpiolib, gpiochip unregister notification, pinctrl line availability checks, and the userspace libgpiod ABI.

## Risks
This is a concurrency-heavy userspace ABI surface. Risks include descriptor lifetime during gpiochip removal, event FIFO overflow semantics, line reconfiguration racing with IRQ/debounce callbacks, compatibility ABI size differences, HTE sequence accounting, correct active-low inversion for edge triggers, and preserving exact ioctl validation behavior. The code deliberately accepts slightly stale reads for some per-line fields; changing those assumptions can introduce locking regressions.

## Test Signals
Test with libgpiod v2 requests for input, output, multi-line values, per-line attributes, debounce, realtime and monotonic clocks, HTE-enabled clocks, reconfiguration, and edge polling/reading. Exercise v1 handle and event ioctls when enabled, 32-bit compat ioctls, line-info watch/unwatch mixed ABI rejection, chip unregister while fds are open, FIFO overflow, invalid padding/flags, nonblocking reads, and proc fdinfo output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-cdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-cdev.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-cdev.h

## Purpose
`gpiolib-cdev.h` is the internal declaration header for GPIO character device registration and unregistration.

## Important APIs, Types, And Functions
It forward-declares `struct gpio_device` and declares `gpiolib_cdev_register(struct gpio_chip *gc, dev_t devt)` and `gpiolib_cdev_unregister(struct gpio_device *gdev)`. The header includes `linux/types.h` for `dev_t`.

## Control Flow
Generic gpiochip registration code can include this header and call into the cdev implementation without exposing the cdev internals. Registration takes a `gpio_chip` because it initializes cdev state from `gc->gpiodev`; unregistration takes the `gpio_device` that owns the character device.

## State And Persistence
The header owns no state. It defines the boundary for state created in `gpiolib-cdev.c`, including cdev registration and workqueue lifetime.

## Dependencies And Integration Points
It integrates generic gpiolib chip lifecycle code with the userspace character device implementation.

## Risks
Because this header omits a forward declaration for `struct gpio_chip`, it relies on includers already having that type visible. Signature drift would break gpiochip lifecycle integration.

## Test Signals
Build-test gpiochip registration paths with cdev enabled, and verify `/dev/gpiochipN` devices appear and disappear with gpiochip add/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-cdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-devres.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-devres.c

## Purpose
`gpiolib-devres.c` provides device-managed GPIO descriptor and GPIO chip APIs. It wraps descriptor acquisition, arrays, optional lookups, firmware-node lookup, explicit put/unhinge operations, and gpiochip registration with devres cleanup actions so resources are released automatically on driver detach or probe failure.

## Important APIs, Types, And Functions
Exported descriptor helpers include `devm_gpiod_get()`, `devm_gpiod_get_optional()`, `devm_gpiod_get_index()`, `devm_fwnode_gpiod_get_index()`, `devm_gpiod_get_index_optional()`, `devm_gpiod_get_array()`, `devm_gpiod_get_array_optional()`, `devm_gpiod_put()`, `devm_gpiod_unhinge()`, and `devm_gpiod_put_array()`. Managed chip registration is `devm_gpiochip_add_data_with_key()`.

Internal cleanup callbacks are `devm_gpiod_release()`, `devm_gpiod_release_array()`, and `devm_gpio_chip_release()`.

## Control Flow
Each get function calls the corresponding unmanaged GPIO acquisition helper. On success it registers a devres action with `devm_add_action_or_reset()`. If action registration fails, the reset behavior immediately releases the acquired GPIO. Optional variants convert not-found descriptors into `NULL`.

`devm_gpiod_get_index()` has special handling for nonexclusive descriptors: if the same descriptor is already managed by the device, it returns the existing descriptor without registering a duplicate cleanup action. `devm_gpiod_unhinge()` removes devres management without releasing the descriptor, tolerating `-ENOENT` for nonexclusive repeated calls.

`devm_gpiochip_add_data_with_key()` registers a gpiochip and installs a devres action that calls `gpiochip_remove()` when the owning device is detached.

## State And Persistence
State is tracked in the device core devres stack, not in this file. Each successful managed acquisition persists until explicit devm put/unhinge or device teardown. The GPIO subsystem descriptor state is modified by the underlying unmanaged calls.

## Dependencies And Integration Points
The file depends on Linux devres, GPIO consumer APIs, GPIO chip registration, and exported symbol infrastructure. It is a primary integration point for drivers that want probe-error-safe GPIO resource management.

## Risks
Incorrect action registration or duplicate nonexclusive handling can produce double-free or leaked descriptors. `devm_gpiod_unhinge()` is explicitly deprecated and exists for ownership handoff edge cases; misuse can make descriptor lifetime difficult to reason about.

## Test Signals
Test probe failure cleanup, driver detach cleanup, optional missing GPIO returns, nonexclusive repeated get/unhinge behavior, firmware-node managed lookup, array get/put cleanup, and managed gpiochip removal when the parent device unbinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-legacy.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-legacy.c

## Purpose
`gpiolib-legacy.c` implements deprecated integer-GPIO request/free helpers and their devres wrapper. It preserves older kernel driver APIs while delegating to descriptor-based gpiolib internals.

## Important APIs, Types, And Functions
Exported functions are `gpio_free()`, `gpio_request_one()`, `gpio_request()`, and `devm_gpio_request_one()`. Internal `devm_gpio_release()` releases integer GPIOs through `gpio_free()`.

## Control Flow
`gpio_request()` translates an integer GPIO to a descriptor with `gpio_to_desc()` and returns `-EPROBE_DEFER` if no descriptor exists, preserving legacy compatibility for GPIOs that may appear later. `gpio_request_one()` requests the GPIO, configures it as input or output according to `GPIOF_*` flags, and frees it on configuration failure. `devm_gpio_request_one()` performs the same setup and installs a devres cleanup action.

## State And Persistence
Runtime state is descriptor request ownership and direction state in core gpiolib. Managed legacy requests persist until the device devres action runs or explicit cleanup occurs.

## Dependencies And Integration Points
The file depends on legacy `linux/gpio.h`, descriptor consumer and driver APIs, and devres. It bridges old integer-based callers to descriptor APIs such as `gpiod_request()`, `gpiod_free()`, and direction setters.

## Risks
The APIs are deprecated and less expressive than descriptor-based APIs. Integer GPIO lookup can obscure firmware mapping errors, and `-EPROBE_DEFER` for missing descriptors is compatibility behavior that may surprise new code.

## Test Signals
Build and runtime tests should cover valid and invalid integer GPIOs, input/output initial direction flags, failure cleanup, devm cleanup on detach, and probe deferral compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-of.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-of.c

## Purpose
`gpiolib-of.c` implements Device Tree GPIO integration. It counts GPIO properties, parses GPIO phandles, maps controller-specific GPIO specifiers to descriptors and Linux lookup flags, applies legacy naming and polarity quirks, manages dynamic gpio-hog additions/removals, provides default two-cell and three-cell translators, and registers pinctrl GPIO ranges from DT.

## Important APIs, Types, And Functions
Externally used functions include `of_gpio_count()`, `of_find_gpio()`, `of_gpiochip_get_lflags()`, `of_gpiochip_add()`, `of_gpiochip_remove()`, and `of_gpiochip_instance_match()`. With dynamic OF enabled, `gpio_of_notifier` handles reconfiguration events.

Important internal helpers are `of_get_named_gpiod_flags()`, `of_find_gpio_device_by_xlate()`, `of_xlate_and_get_gpiod_flags()`, `of_convert_gpio_flags()`, `of_gpio_flags_quirks()`, `of_find_gpio_rename()`, `of_find_trigger_gpio()`, `of_gpio_twocell_xlate()`, `of_gpio_threecell_xlate()`, and `of_gpiochip_add_pin_range()`.

## Control Flow
Consumer lookup through `of_find_gpio()` first tries standard property names produced by `for_each_gpio_property_name()`, such as `foo-gpios` and `foo-gpio`. If not found, it tries compatibility quirks for legacy names and trigger-source handling. Successful parsing uses `of_parse_phandle_with_args_map()`, finds a registered GPIO device whose chip node and `.of_xlate()` can translate the specifier, gets the descriptor, applies quirks, and converts OF flags into gpiolib lookup flags.

Counting uses `of_gpio_count()`, including a special SPI chip-select fallback for old Freescale/PPC bindings that used plain `gpios`. GPIO chip add sets default `.of_xlate` if the driver did not provide one, validates `of_gpio_n_cells`, adds pin ranges, takes a reference on the DT node, and marks gpio-hog children populated. Removal clears hog populated flags and puts the node.

With `CONFIG_OF_DYNAMIC`, `of_gpio_notify()` responds to added or removed gpio-hog nodes by finding the parent gpiochip and adding or removing hog descriptors.

## State And Persistence
The file mostly operates statelessly on DT data and gpiochip state. Persistent effects include node references held while a gpiochip is registered, populated flags on gpio-hog child nodes, pin ranges installed on gpiochips, and descriptor hog ownership created from DT.

## Dependencies And Integration Points
It depends on OF core parsing, OF dynamic reconfiguration, GPIO descriptor/chip APIs, pinctrl range APIs, firmware-node helpers, and numerous optional subsystem config symbols that enable compatibility quirks. It integrates DT bindings with generic `gpiod_get()` lookup paths and gpiochip registration.

## Risks
The compatibility quirk matrix is broad and config-dependent. Incorrect polarity override can invert hardware behavior. Dynamic hog handling only supports whole-node add/remove, not arbitrary modification. Three-cell translation depends on correct `of_node_instance_match()`. Pinctrl range parsing can defer probe if the pinctrl provider is not ready.

## Test Signals
Test standard `*-gpios` lookup, legacy renamed properties, SPI chip-select quirks, regulator and reset polarity overrides, trigger-source lookup, two-cell and three-cell controllers, invalid phandle args, deferred gpiochip registration, dynamic gpio-hog add/remove, pinctrl numeric and group ranges, and gpiochip unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-of.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-of.h

## Purpose
`gpiolib-of.h` is the internal Device Tree GPIO interface. It declares descriptor lookup, gpiochip registration/removal, instance matching, GPIO counting, and lookup-flag translation for OF-backed GPIO controllers and consumers.

## Important APIs, Types, And Functions
With `CONFIG_OF_GPIO`, it declares `of_find_gpio()`, `of_gpiochip_add()`, `of_gpiochip_remove()`, `of_gpiochip_instance_match()`, `of_gpio_count()`, and `of_gpiochip_get_lflags()`. Without OF GPIO, inline stubs return no-op success or not-found values. It also declares `extern struct notifier_block gpio_of_notifier`.

## Control Flow
Generic gpiolib code can call OF hooks unconditionally. Build-time stubs keep non-OF configurations from linking OF implementation code while preserving generic control flow.

## State And Persistence
The header owns no runtime state. The external notifier declaration represents dynamic OF state handled in `gpiolib-of.c` when that support is built.

## Dependencies And Integration Points
It depends on `linux/err.h`, `linux/types.h`, and `linux/notifier.h`, and forward-declares OF, fwnode, GPIO chip, descriptor, and device types. It integrates generic gpiochip and consumer lookup paths with OF-specific implementation.

## Risks
Stub return choices influence fallback behavior in non-OF builds. The unconditional notifier declaration must remain consistent with implementation and build configuration.

## Test Signals
Build-test `CONFIG_OF_GPIO=y` and disabled configurations, and verify generic gpiolib registration and lookup call sites link and behave as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-shared.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-shared.c

## Purpose
`gpiolib-shared.c` implements infrastructure for GPIO lines intentionally shared by multiple firmware-described consumers. It scans firmware nodes, identifies shared OF GPIO references, claims the real descriptor, creates auxiliary proxy devices for each consumer, installs machine lookup tables for proxy access, and exposes managed shared descriptors with sleep-aware locking.

## Important APIs, Types, And Functions
Externally used functions are `gpiochip_setup_shared()`, `gpio_device_teardown_shared()`, `gpio_shared_add_proxy_lookup()`, and `devm_gpiod_shared_get()`. Core data structures are `struct gpio_shared_entry`, representing one physical GPIO pin, `struct gpio_shared_ref`, representing one consumer reference, and `struct gpio_shared_desc`, declared in the header for shared descriptor users.

Key internal helpers include `gpio_shared_of_scan()`, `gpio_shared_of_traverse()`, `gpio_shared_find_entry()`, `gpio_shared_make_ref()`, `gpio_shared_setup_reset_proxy()`, `gpio_shared_make_adev()`, `gpio_shared_dev_is_reset_gpio()`, `gpio_shared_remove_adev()`, `gpiod_shared_desc_create()`, `gpio_shared_release()`, `gpio_shared_free_exclusive()`, and teardown helpers.

## Control Flow
At `postcore_initcall`, the code scans the OF tree. It ignores disabled nodes, `__symbols__`, and gpio hogs, then inspects GPIO-like properties (`*-gpios`, `*-gpio`, `gpios`, `gpio`) with two-cell GPIO specifiers. References to the same controller fwnode and offset are grouped into one `gpio_shared_entry`. Entries that are not really shared are discarded.

When a gpiochip registers, `gpiochip_setup_shared()` first detects whether it is itself a proxy chip and marks its only descriptor as `GPIOD_FLAG_SHARED_PROXY`. Otherwise, if the chip matches a shared entry, it translates the OF offset if needed, marks the real descriptor `GPIOD_FLAG_SHARED`, requests it with label `shared` before normal consumers can take it, and creates one auxiliary proxy device per reference.

When a consumer requests a shared GPIO through a proxy path, `gpio_shared_add_proxy_lookup()` matches the consumer fwnode and connection ID, creates a `gpiod_lookup_table` keyed to the proxy device, and registers it. `devm_gpiod_shared_get()` retrieves the shared entry from auxiliary device platform data, creates or reuses a refcounted `gpio_shared_desc`, and installs a devres put action.

## State And Persistence
Global state is `gpio_shared_list` and `gpio_shared_ida`. Each shared entry holds a controller fwnode reference, offset, ref list, mutex, optional shared descriptor, and kref. Each ref owns an auxiliary device, optional lookup table, copied connection ID, optional fwnode ref, and lockdep key. Teardown removes lookup tables, auxiliary devices, descriptor reservations, fwnode refs, IDA IDs, and locks.

## Dependencies And Integration Points
The file depends on OF scanning, auxiliary bus, GPIO machine lookup tables, GPIO descriptor internals, device properties, fwnode refs, reset-gpio special handling, IDA, kref, lockdep, and devres. It integrates with gpiochip registration, auxiliary proxy drivers, reset-gpio, and consumers that need coordinated shared-line access.

## Risks
The scanner currently supports only OF and predominantly two-cell GPIO bindings. Incorrect sharing detection could either reserve a line unnecessarily or allow unsafe concurrent consumers. Lifetime is complex because auxiliary devices, lookup tables, fwnode references, and descriptor reservations must be torn down in the right order. The reset-gpio special case mutates a proxy ref's fwnode after matching, so tests need to cover that path.

## Test Signals
Test OF systems with one, two, and more than two consumers referencing the same GPIO, exclusive single-reference entries being discarded, reset-gpio proxy creation, gpiochip registration before and after scan, proxy lookup table creation, managed shared descriptor refcounting, sleep-capable and atomic locks, gpiochip teardown, and failure injection in auxiliary device or lookup allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-shared.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-shared.h

## Purpose
`gpiolib-shared.h` declares the internal and consumer-facing pieces of the shared GPIO infrastructure. It provides gpiochip setup/teardown hooks, proxy lookup installation, the shared descriptor object, a managed getter, and lock helpers for safe shared access.

## Important APIs, Types, And Functions
When `CONFIG_GPIO_SHARED` is enabled, it declares `gpiochip_setup_shared()`, `gpio_device_teardown_shared()`, and `gpio_shared_add_proxy_lookup()`. Otherwise these are inline no-ops returning success. `struct gpio_shared_desc` contains the real descriptor, sleep capability, cached config/use counters, high counter, and either a mutex or spinlock. `devm_gpiod_shared_get()` returns a managed shared descriptor. `DEFINE_LOCK_GUARD_1(gpio_shared_desc_lock, ...)` provides scoped locking, and `gpio_shared_lockdep_assert()` verifies the correct lock is held.

## Control Flow
Generic gpiochip code can call setup and teardown regardless of configuration. Shared GPIO consumers acquire `struct gpio_shared_desc` through devres and use the guard macro to take either the mutex or spinlock depending on `can_sleep`.

## State And Persistence
The header-defined `struct gpio_shared_desc` is persistent per shared entry while references exist. The lock union is initialized by implementation code according to whether the GPIO can sleep.

## Dependencies And Integration Points
It depends on cleanup guards, lockdep, mutexes, spinlocks, and GPIO/device forward declarations. It integrates shared GPIO implementation with gpiochip lifecycle code and proxy consumers.

## Risks
Consumers must use the correct shared lock before modifying shared descriptor counters or configuration. No-op stubs mean callers must not assume proxy behavior when `CONFIG_GPIO_SHARED` is disabled.

## Test Signals
Build-test enabled and disabled configurations, lockdep assertions for sleep and non-sleep GPIOs, managed get/put lifetime, and gpiochip setup/teardown calls in generic registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-swnode.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-swnode.c

## Purpose
`gpiolib-swnode.c` implements GPIO lookup and counting for software-node firmware descriptions. It lets software nodes reference GPIO controllers and line flags using generic property APIs, including a special undefined GPIO node for bindings such as internal SPI chip selects.

## Important APIs, Types, And Functions
The main exported-to-gpiolib helpers are `swnode_find_gpio()` and `swnode_gpio_count()`. Internal helpers are `swnode_get_gpio_device()` and `swnode_gpio_get_reference()`. When `CONFIG_GPIO_SWNODE_UNDEFINED` is enabled, it exports `swnode_gpio_undefined` in the `GPIO_SWNODE` namespace and registers/unregisters it at subsystem init/exit.

## Control Flow
`swnode_find_gpio()` verifies the consumer fwnode is a software node, tries standard GPIO property names, handles `-ENOTCONN` as `-EPROBE_DEFER` for not-yet-registered remote software nodes, resolves the referenced GPIO device by fwnode or legacy label fallback, retrieves the descriptor by offset, and returns native GPIO flags from the second argument.

`swnode_gpio_count()` loops over standard property names and counts references by repeatedly calling `fwnode_property_get_reference_args()` with two expected arguments.

## State And Persistence
The file owns little runtime state beyond the optional globally registered `swnode_gpio_undefined`. Lookup uses temporary fwnode references and drops them after descriptor resolution. The code has a FIXME noting that the GPIO device ref is put while returning a descriptor, mirroring lifetime concerns in other firmware lookup paths.

## Dependencies And Integration Points
It depends on software nodes, generic property APIs, GPIO consumer/driver/property interfaces, fwnode matching, and gpiolib descriptor lookup. It integrates software-node-described devices with the generic `gpiod_get()` firmware lookup path.

## Risks
The label fallback is explicitly a compatibility workaround for software nodes not actually attached to GPIO controllers, so it can mask bad modeling. Reference lifetime is subtle because descriptors outlive the local GPIO device reference. The code assumes software-node GPIO references use exactly two args: offset and native flags.

## Test Signals
Test valid software-node GPIO lookups, missing properties, undefined GPIO sentinel returning not-found, remote node not registered returning probe defer, label fallback, multi-GPIO counting, and native flag propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-swnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-swnode.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-swnode.h

## Purpose
`gpiolib-swnode.h` declares the software-node GPIO lookup interface used by generic GPIO consumer code.

## Important APIs, Types, And Functions
It forward-declares `struct fwnode_handle` and `struct gpio_desc`, then declares `swnode_find_gpio()` and `swnode_gpio_count()`.

## Control Flow
Generic firmware lookup code can call these helpers when a consumer fwnode is backed by a software node. The implementation resolves references and counts GPIOs from software-node properties.

## State And Persistence
The header has no state. It defines the internal contract between generic gpiolib lookup and `gpiolib-swnode.c`.

## Dependencies And Integration Points
It integrates software-node property descriptions with the gpiolib consumer API.

## Risks
Signatures must remain aligned with generic gpiolib lookup expectations, particularly native lookup flag output and index handling.

## Test Signals
Build-test software-node GPIO support and run lookup/count tests for software-node-backed consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-swnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-sysfs.c

## Purpose
`gpiolib-sysfs.c` implements the GPIO sysfs interface. It supports chip-level sysfs devices, per-line export/unexport, per-line `direction` and `value` attributes, and, when legacy sysfs is enabled, `/sys/class/gpio/export`, `/sys/class/gpio/unexport`, per-line `edge` polling, `active_low`, and links to exported GPIO class devices.

## Important APIs, Types, And Functions
Exported functions are `gpiod_export()`, `gpiod_export_link()`, `gpiod_unexport()`, `gpiochip_sysfs_register()`, and `gpiochip_sysfs_unregister()`. Core state structures are `struct gpiod_data` for one exported line and `struct gpiodev_data` for one gpiochip sysfs device set.

Important helpers include `direction_show/store()`, `value_show/store()`, `gpio_sysfs_request_irq()`, `gpio_sysfs_free_irq()`, `edge_show/store()`, `gpio_sysfs_set_active_low()`, `active_low_show/store()`, `gpio_is_visible()`, `export_gpio_desc()`, `unexport_gpio_desc()`, `do_chip_export_store()`, `gdev_get_data()`, `gpiod_unexport_unlocked()`, `gpiofind_sysfs_register()`, and `gpiolib_sysfs_init()`.

## Control Flow
At `postcore_initcall`, `gpiolib_sysfs_init()` registers the `gpio` class and scans already-registered gpiochips to create sysfs devices. Later gpiochip registration calls `gpiochip_sysfs_register()` directly. Each chip gets a modern `chipN` class device with `label`, `ngpio`, `export`, and `unexport`; legacy builds also create `gpiochip<base>` and class-wide export/unexport files.

Exporting a descriptor requires the gpio class to exist, the descriptor to be valid and requested, and the `GPIOD_FLAG_EXPORT` bit to be acquired. `gpiod_export()` allocates per-line data, initializes attributes, optionally creates a legacy `gpioN` class device, adds a per-chip `gpio<offset>` attribute group, and records the exported line under `gpiodev_data`. `gpiod_unexport()` removes the same state under `sysfs_lock`.

Legacy edge support configures an IRQ for polling the `value` file. `edge_store()` maps string triggers to flags, frees old IRQ state, requests a new IRQ when needed, and emits line state notifications. `active_low_store()` flips descriptor polarity and reconfigures single-edge IRQs so poll semantics remain logical.

## State And Persistence
`sysfs_lock` serializes export/unexport and unregister. Per-line state stores the descriptor, device, attribute objects, parent kobject, direction permission, optional kernfs node, IRQ number, and IRQ flags. Per-chip state stores exported line list and sysfs devices. Descriptor flags track export, sysfs ownership, active-low, and edge bits. All state is removed when lines are unexported or gpiochips unregister.

## Dependencies And Integration Points
The file depends on sysfs/class device APIs, kernfs notification, GPIO descriptor and chip APIs, IRQ APIs, SRCU/chip guards, kstrtox, and UAPI GPIO naming. It integrates with cdev line-state notifications through `gpiod_line_state_notify()` and with legacy userspace that still relies on `/sys/class/gpio`.

## Risks
Sysfs GPIO is legacy and has broad compatibility constraints. Risks include races between edge reconfiguration and device deregistration, stale exported-line state during gpiochip unregister, active-low changes while an IRQ is active, and ensuring `GPIOD_FLAG_EXPORT`/`GPIOD_FLAG_SYSFS` are cleared in all error paths. Legacy global GPIO numbers depend on stable bases, while modern chip devices use gpio device IDs and offsets.

## Test Signals
Test early gpiochip registration before class init, chip add/remove after class init, per-chip export/unexport by offset, legacy global export/unexport by GPIO number, direction/value reads and writes, hidden direction when not changeable, edge polling and sysfs notifications, active_low IRQ reconfiguration, export error cleanup, `gpiod_export_link()`, and gpiochip unregister with exported sysfs-owned lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-sysfs.h

## Purpose
`gpiolib-sysfs.h` declares the internal gpiochip sysfs registration hooks for the GPIO subsystem.

## Important APIs, Types, And Functions
With `CONFIG_GPIO_SYSFS`, it declares `gpiochip_sysfs_register(struct gpio_chip *gc)` and `gpiochip_sysfs_unregister(struct gpio_chip *gc)`. Without sysfs support, inline stubs no-op and return success.

## Control Flow
Generic gpiochip lifecycle code can call sysfs hooks unconditionally. The implementation registers or unregisters chip-level sysfs devices and manages exported lines when sysfs is enabled.

## State And Persistence
The header owns no state. It controls whether sysfs state from `gpiolib-sysfs.c` exists for a build.

## Dependencies And Integration Points
It forward-declares `struct gpio_device` and relies on includers for `struct gpio_chip`. It integrates generic gpiochip lifecycle with optional sysfs compatibility support.

## Risks
Stub behavior means builds without `CONFIG_GPIO_SYSFS` silently skip sysfs registration. Callers must not rely on sysfs-visible side effects unless the config is enabled.

## Test Signals
Build-test with `CONFIG_GPIO_SYSFS=y` and disabled, and verify gpiochip add/remove paths work in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-sysfs.h -->
