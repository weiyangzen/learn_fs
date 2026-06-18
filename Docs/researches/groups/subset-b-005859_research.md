# Group Research: subset-b-005859

This grouped report covers the requested Linux header subset under `sources/distributed-fs/ceph-client/include/linux`. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/driver.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/driver.h

Purpose: This is the main in-kernel provider interface for GPIO controller drivers. It defines `struct gpio_chip`, the optional `struct gpio_irq_chip` interrupt-controller integration, pinctrl range helpers, descriptor ownership helpers, chip registration/removal APIs, and CONFIG-dependent stubs used when gpiolib or pinctrl support is disabled.

Important APIs/types/functions: `struct gpio_chip` supplies the driver callback table for request/free, direction, get/set, multi-bit get/set, pin configuration, IRQ translation, debugfs display, valid-mask initialization, pin-range setup, and hardware timestamp enable/disable. `struct gpio_irq_chip` describes IRQ domain, parent IRQs, hierarchical mapping callbacks, parent fwspec population, validity masks, threaded/nested interrupt handling, static IRQ base, and saved irq_chip callbacks. Registration goes through `gpiochip_add_data_with_key()`, `gpiochip_add_data()`, `devm_gpiochip_add_data_with_key()`, `devm_gpiochip_add_data()`, and `gpiochip_remove()`. Lookup/lifetime helpers include `gpio_device_find()`, `gpio_device_get()/put()`, `gpio_device_to_device()`, `gpio_device_get_chip()`, and descriptor helpers such as `gpiochip_request_own_desc()`.

Control flow, state, and persistence: The header exposes lifecycle rather than implementation. A driver fills persistent chip state in its own enclosing object, embeds `gpio_chip`, registers it, and gpiolib stores an opaque `gpio_device` pointer in `gc->gpiodev`. GPIO line state is delegated to callbacks; IRQ state is coordinated through `gc->irq`, IRQ domains, valid masks, and resource request/release helpers. The iteration macros duplicate line labels and free them through cleanup-style guards, so callers must not persist those temporary labels without copying.

Dependencies/integration: It integrates with irqdomain, generic MSI, lockdep, pinctrl, firmware nodes, device properties, debugfs, and module lifetime. Device tree support adds `of_gpio_n_cells`, `of_node_instance_match`, and `of_xlate`. Pinctrl support adds pin range APIs; without `CONFIG_PINCTRL`, range helpers become no-op success stubs.

Risks and test signals: Drivers must set `ngpio`, callback semantics, sleeping rules via `can_sleep`, and dynamic `base = -1` correctly. IRQ hierarchy callbacks must agree with `valid_mask`; otherwise invalid lines can map to parent IRQs. Tests should cover chip add/remove, devm cleanup, direction/value callbacks, active-low handling through gpiolib, IRQ request/release, `gpiod_to_irq()`, pinctrl ranges, and disabled-CONFIG builds that exercise stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/forwarder.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/forwarder.h

Purpose: This header declares a GPIO forwarding abstraction: a synthetic `gpio_chip` can expose lines that forward operations to existing `gpio_desc` providers.

Important APIs/types/functions: `struct gpiochip_fwd` is opaque. Allocation and composition use `devm_gpiochip_fwd_alloc()`, `gpiochip_fwd_desc_add()`, and `gpiochip_fwd_desc_free()`. Publication uses `gpiochip_fwd_register()`, with `gpiochip_fwd_get_gpiochip()` and `gpiochip_fwd_get_data()` exposing the generated chip and caller data. Forwarded operation helpers mirror `gpio_chip` callbacks: request, get direction, direction input/output, get, get multiple, set, set multiple, set config, and to-IRQ.

Control flow, state, and persistence: Callers allocate a forwarding object for `ngpios`, attach descriptors at offsets, then register it. After registration, the helper callbacks translate chip offsets to stored descriptors and delegate operations to the underlying GPIO consumer/provider APIs. Lifetime is device-managed for allocation, but descriptor attachment/freeing is explicit.

Dependencies/integration: It depends on gpiolib descriptor semantics and the provider interface in `gpio/driver.h`. It is useful for MFD, aggregator, or board glue drivers that need to republish selected GPIO lines under a different controller.

Risks and test signals: Risks are stale descriptors, offset collisions, inconsistent `ngpios`, and forwarding IRQ/config operations to backing lines that do not support them. Tests should register a forwarder with valid and missing descriptors, validate direction/value propagation, error propagation, cleanup, and IRQ mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/forwarder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/generic.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/generic.h

Purpose: This header defines the generic MMIO GPIO chip model used by simple register-backed GPIO controllers. It factors common register layout, endian, direction, set/clear, and shadow-state handling behind `struct gpio_generic_chip`.

Important APIs/types/functions: Flags such as `GPIO_GENERIC_BIG_ENDIAN`, `GPIO_GENERIC_UNREADABLE_REG_SET`, `GPIO_GENERIC_UNREADABLE_REG_DIR`, `GPIO_GENERIC_READ_OUTPUT_REG_SET`, `GPIO_GENERIC_NO_OUTPUT`, `GPIO_GENERIC_PINCTRL_BACKEND`, and `GPIO_GENERIC_NO_INPUT` parameterize hardware behavior. `struct gpio_generic_chip_config` supplies parent device, register size, data/set/clear/direction registers, and flags. `struct gpio_generic_chip` embeds `struct gpio_chip`, read/write callbacks, register pointers, bit order, direction/readability markers, bit count, a raw spinlock, and shadow registers `sdata` and `sdir`.

Control flow, state, and persistence: `gpio_generic_chip_init()` maps the config into a ready `gpio_chip` callback table. Runtime get/set/direction paths use `read_reg`/`write_reg`, shadow data for unreadable or read-modify-write registers, and raw spinlocks to keep hardware writes and shadow state synchronized. Inline wrappers protect against missing function pointers and return `-EOPNOTSUPP` or no-op on invalid setup.

Dependencies/integration: It builds on `gpio/driver.h`, MMIO `__iomem`, raw spinlocks, and optional pinctrl backend direction calls. It is the interface for drivers that otherwise would reimplement basic GPIO register operations.

Risks and test signals: Misdeclared register readability or endian/bit order corrupts line values. Locking matters because shadow registers and hardware writes must stay atomic relative to IRQ and concurrent GPIO users. Tests should cover set/clear layouts, single-register clear-by-zero layouts, unreadable direction/data registers, big-endian bit numbering, no-input/no-output constraints, and lockdep/atomic context use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/gpio-nomadik.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/gpio-nomadik.h

Purpose: This is the shared private/public interface between Nomadik GPIO and pinctrl drivers. It defines bank geometry, register offsets, sleep/pull/alternate-function encodings, per-bank runtime state, and SoC pinctrl description tables.

Important APIs/types/functions: Register macros cover data, set/clear, pull disable, direction, sleep, alternate-function, low-EMI, interrupt masks/status/clear, wake masks/status, and later edge/level registers. `struct nmk_gpio_chip` embeds `gpio_chip` and stores MMIO base, clock, bank id, `set_ioforce`, lock, sleep mode, Mobileye flag, interrupt edge masks, wake masks, cached mask registers, pull-up, and low-EMI state. Pinctrl data uses `struct prcm_gpiocr_altcx`, `struct prcm_gpiocr_altcx_pin_desc`, `struct nmk_function`, `struct nmk_pingroup`, and `struct nmk_pinctrl_soc_data`. SoC init hooks exist for STN8815, DB8500, and DB8540.

Control flow, state, and persistence: GPIO and pinctrl share bank arrays and sleep-mode locking when `CONFIG_PINCTRL_NOMADIK` is enabled. Driver implementation uses cached fields to preserve interrupt, wake, pull, and low-EMI configuration across transitions. Alternate-C selection may require PRCM GPIOCR register control rather than only the GPIO block.

Dependencies/integration: It depends on gpiolib, pinctrl pin descriptors/groups, platform devices, clocks, debugfs, and SoC-specific Kconfig. Debug support exposes `nmk_gpio_dbg_show_one()` only under `CONFIG_DEBUG_FS`; otherwise it is a no-op inline.

Risks and test signals: Pin numbering must match GPIO numbering for GPIO-backed pins. Cached IRQ and sleep masks can drift from hardware if locking is bypassed. Tests should cover SoC init data selection, alternate function C/C1-C4 encoding, GPIO direction/output transitions, sleep persistence, IRQ edge/wake masks, debugfs formatting, and builds with each SoC CONFIG off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/gpio-nomadik.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/gpio-reg.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/gpio-reg.h

Purpose: This compatibility header exists only to include the generic MMIO GPIO definitions from `linux/gpio/generic.h`.

Important APIs/types/functions: It declares no independent types or functions. Any user including this file receives the `gpio_generic_chip_config`, `gpio_generic_chip`, flags, initialization function, access wrappers, and lock helper macros from `gpio/generic.h`.

Control flow, state, and persistence: There is no runtime control flow in this file. State behavior is inherited entirely from the generic GPIO implementation.

Dependencies/integration: It provides an include path for older or transitional users that still include `gpio-reg.h` rather than `gpio/generic.h`.

Risks and test signals: The main risk is accidental divergence if future code expects this header to contain definitions of its own. Build tests should ensure legacy include users compile and that include guards do not conflict with `gpio/generic.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/gpio-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/machine.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/machine.h

Purpose: This header declares the machine/board lookup table interface for mapping consumer device/function names to GPIO controller labels and line offsets on non-firmware or board-file platforms.

Important APIs/types/functions: `struct gpiod_lookup` records chip label, hardware index, connection id, index within a connection, lookup flags, and optional key/transitory flags. `GPIO_LOOKUP()` and `GPIO_LOOKUP_IDX()` build entries. `struct gpiod_lookup_table` associates a device id with a list of lookups. APIs include `gpiod_add_lookup_table()`, `gpiod_add_lookup_tables()`, `gpiod_remove_lookup_table()`, `gpiod_remove_lookup_tables()`, and managed variants. `struct gpiod_hog` and `GPIO_HOG()` describe boot-time/request-time hogged GPIOs.

Control flow, state, and persistence: Lookup tables are registered globally so later consumer lookups can resolve `(dev_id, con_id, idx)` to a chip line and flags. Device-managed APIs tie table lifetime to a parent device. Hog entries persist as requested lines until the provider or table is removed.

Dependencies/integration: It connects board data to gpiolib descriptors. It coexists with firmware-node mappings but is especially relevant for legacy platform data.

Risks and test signals: Static chip labels and offsets are fragile when providers move to dynamic GPIO bases; labels must match registered chips. Incorrect flags invert semantics or create open-drain/source mismatches. Tests should cover table add/remove ordering, duplicate entries, managed cleanup, hog direction/value setup, and consumer lookup by indexed connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/property.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/property.h

Purpose: This small header declares helper APIs for firmware-property backed GPIO lookups.

Important APIs/types/functions: It forward-declares `struct fwnode_handle` and `struct gpio_desc`, and declares `fwnode_gpiod_get_index()` for fetching a GPIO descriptor from a firmware node by property name/index plus descriptor flags and label.

Control flow, state, and persistence: The implementation performs firmware property parsing and returns a referenced GPIO descriptor according to the requested index and flags. The header itself holds no state.

Dependencies/integration: It bridges the generic firmware-node property API and gpiolib descriptor API, covering device tree, ACPI, or software nodes through `fwnode_handle`.

Risks and test signals: Callers must handle `ERR_PTR` failures, missing properties, and index bounds. Tests should cover active-low/open-drain flags, absent properties, named and indexed GPIO lists, and descriptor release by the consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/property.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/regmap.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/regmap.h

Purpose: This header describes a generic GPIO controller backed by Linux regmap. It lets MFD/regmap devices expose GPIO lines without hand-writing a full `gpio_chip`.

Important APIs/types/functions: `GPIO_REGMAP_ADDR_ZERO` and `GPIO_REGMAP_ADDR()` encode optional register base zero. `struct gpio_regmap_config` supplies parent, regmap, optional firmware node/label/names, GPIO count, data/set/clear/direction register bases, stride, GPIOs per register, optional IRQ domain, optional `fixed_direction_output` bitmap, optional regmap-IRQ chip/line/flags under `CONFIG_REGMAP_IRQ`, `reg_mask_xlate()` for base/offset-to-register/mask translation, `init_valid_mask()`, and `drvdata`. Lifecycle APIs are `gpio_regmap_register()`, `gpio_regmap_unregister()`, `devm_gpio_regmap_register()`, and `gpio_regmap_get_drvdata()`.

Control flow, state, and persistence: Callers describe register layout once, then the implementation creates a `gpio_chip` whose get/set/direction callbacks issue regmap reads/updates. Optional regmap-IRQ support creates a regmap IRQ device and connects its domain to GPIO IRQ handling. Driver-private `drvdata` persists inside the opaque `gpio_regmap`.

Dependencies/integration: It integrates gpiolib, regmap, optional regmap-irq, firmware nodes, and IRQ domains. The documented register-base rules define valid input-only, output-only, and bidirectional configurations.

Risks and test signals: Invalid combinations of register bases lead to nonsensical direction/value behavior. `reg_mask_xlate()` must honor stride and `ngpio_per_reg`, and fixed-output masks must align with `ngpio`. Tests should cover input-only, output-only, split set/clear, direction-in vs direction-out layouts, custom translation, IRQ domain setup, managed unregister, and regmap failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/regmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio_keys.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio_keys.h

Purpose: This header defines platform data for the GPIO keys and GPIO keys polled input drivers.

Important APIs/types/functions: `struct gpio_keys_button` describes each button or switch: input code, optional legacy GPIO number, active-low polarity, descriptor label, event type, wakeup settings, debounce interval, user-disable permission, ABS value, IRQ, and optional wake IRQ. `struct gpio_keys_platform_data` supplies the button array, count, poll interval, autorepeat flag, platform enable/disable hooks, and input device name.

Control flow, state, and persistence: The platform data is consumed by the gpio-keys driver at probe time. The driver requests GPIOs/IRQs, configures debounce and wake behavior, reports input events, and may call platform enable/disable hooks across suspend/resume or open/close.

Dependencies/integration: It integrates with the input subsystem, gpiolib, IRQ wake handling, and legacy board/platform data paths.

Risks and test signals: Mixing `gpio`, `irq`, and `wakeirq` fields incorrectly can double-request or miss wake events. Active-low and wakeup action must match hardware. Tests should cover key and switch events, debounce, poll mode, suspend wake, sysfs disable for `can_disable`, enable/disable hook errors, and legacy GPIO-less IRQ buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio_keys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpu_buddy.h -->
# sources/distributed-fs/ceph-client/include/linux/gpu_buddy.h

Purpose: This header defines a GPU-oriented binary buddy allocator for managing device address ranges or memory regions with power-of-two block splitting, optional top-down/range allocation, contiguous-only requests, and clear/dirty free trees.

Important APIs/types/functions: Allocation flags include range, top-down, contiguous, clear-preferred, cleared-on-free, and trim-disable. `struct gpu_buddy_block` stores offset, state, clear bit, and order in a packed `header`, tree links, user `private`, and a union of free-tree rb node or allocated-list link. `struct gpu_buddy` stores per-order free red-black trees for clear/dirty blocks, root blocks, root count, max order, chunk size, total size, available bytes, and clear-available bytes. Inline helpers expose block offset, order, free/clear state, and size. Public APIs include init/fini, `gpu_buddy_alloc_blocks()`, trim, reset clear state, free block/list, and print/debug functions.

Control flow, state, and persistence: `gpu_buddy_init()` builds root blocks for the address space. Allocation chooses blocks from rb trees, splits as needed, appends allocated blocks to caller-owned lists, and may trim excess unless disabled. Freeing returns ownership of `link` to the allocator, merges buddies when possible, and accounts clear vs dirty availability. Locking is explicitly caller-owned.

Dependencies/integration: It uses Linux lists, slab allocation, rbtrees, bit operations, and scheduler types. GPU drivers wrap this allocator with their own mutexes and memory object metadata.

Risks and test signals: Header bit packing assumes offsets/order fit masks and chunk size is at least 4 KiB. Missing external locking corrupts rbtrees. Clear/dirty accounting can mislead callers if `GPU_BUDDY_CLEARED` is wrong. Tests should cover non-power-of-two sizes, top-down and ranged allocations, contiguous failures, trimming, merge behavior, clear-tree preference/fallback, reset clear state, and concurrent caller locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpu_buddy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus.h

Purpose: This is the umbrella kernel Greybus API header. It includes the Greybus manifest, protocol, host-device, SVC, control, module, interface, bundle, connection, and operation headers and defines the bus-driver interface.

Important APIs/types/functions: `struct greybus_driver` contains name, bundle `probe`, `disconnect`, id table, and embedded `device_driver`. Matching helpers include `GREYBUS_DEVICE()`, `GREYBUS_DEVICE_CLASS()`, and `GREYBUS_ID_MATCH_DEVICE`. Driver registration uses `greybus_register_driver()`, `greybus_deregister_driver()`, `greybus_register()`, `greybus_deregister()`, and `module_greybus_driver()`. Runtime helpers set/get bundle driver data. Constants define Greybus version and CPort limits. `cport_id_valid()` checks CPort IDs against the host device.

Control flow, state, and persistence: Greybus drivers bind to `gb_bundle` devices via the Linux driver core. Probe typically creates protocol connections and stores driver state in bundle drvdata; disconnect tears those resources down. Core objects persist as Linux devices linked by host, module, interface, bundle, connection, and operation lifetimes.

Dependencies/integration: This header is kernel-only and integrates with Linux modules, driver core, PM runtime, IDR/IDA, debugfs, and all Greybus subheaders.

Risks and test signals: Bundle matching must use correct class/vendor/product flags. CPort validation relies on host `num_cports`. Tests should cover module registration/unregistration, driver probe/disconnect paths, disabled Greybus handling, debugfs init/cleanup, and invalid CPort IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/bundle.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/bundle.h

Purpose: This header defines Greybus bundles, the logical function units within an interface that drivers bind to.

Important APIs/types/functions: `struct gb_bundle` embeds a device, points to its interface, stores bundle id/class/version, CPort descriptors, connection list, state byte array, and interface list links. Lifecycle APIs are `gb_bundle_create()`, `gb_bundle_add()`, and `gb_bundle_destroy()`. Runtime PM wrappers include `gb_pm_runtime_get_sync()`, `gb_pm_runtime_put_autosuspend()`, `gb_pm_runtime_get_noresume()`, and `gb_pm_runtime_put_noidle()`, with no-op stubs when `CONFIG_PM` is off.

Control flow, state, and persistence: The manifest parser creates bundles from descriptors and attaches CPort descriptors. Adding a bundle publishes it to the driver core; protocol drivers create connections from its CPorts. Runtime PM wrappers increment/decrement the bundle device usage count and handle autosuspend bookkeeping.

Dependencies/integration: Bundles are children of Greybus interfaces and integrate with Linux devices, lists, PM runtime, manifest CPort descriptors, and Greybus driver matching.

Risks and test signals: Runtime PM get failures must be balanced with `pm_runtime_put_noidle()`, which the helper does. Tests should cover bundle creation from manifests, version/class matching, connection list cleanup, PM enabled/disabled builds, autosuspend behavior, and destroy after failed add.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/bundle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/connection.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/connection.h

Purpose: This header defines Greybus CPort connections, which are the transport endpoints over which protocol operations are exchanged.

Important APIs/types/functions: Connection flags cover CSD/e2efc behavior, no flow control, offload, CDSI1, control, and high priority. `enum gb_connection_state` tracks disabled, TX-enabled, enabled, and disconnecting. `struct gb_connection` stores host/interface/bundle pointers, refcount, host/interface CPort IDs, link nodes, request handler, flags, mutex/spinlock, state, operation list, name, workqueue, operation cycle counter, private data, and mode-switch flag. Creation APIs support static, control, normal, flagged, and offloaded connections. Enable/disable, forced disable, RX disable, mode-switch prepare/complete, received-data dispatch, latency tag, and data get/set APIs are declared.

Control flow, state, and persistence: A driver creates a connection, enables TX or full RX/TX, sends operations, and disables/destroys it during disconnect. Incoming data is demultiplexed from host device and CPort into a connection, then into operations or request handlers. State is protected by mutex/spinlock and refcounting.

Dependencies/integration: It integrates host controller CPort operations, bundles/interfaces, workqueues, krefs, kfifo infrastructure, and `gb_operation`.

Risks and test signals: State transitions during mode switch and disconnect are race-prone. Flow-control flags must match SVC/APBridge setup. Tests should cover create/destroy variants, enable failure unwinding, incoming request dispatch, operation cancellation on disable, offloaded/control flags, latency tag enable/disable, and CPort ID mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/connection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/control.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/control.h

Purpose: This header declares the Greybus control-protocol object for an interface. Control handles version negotiation, manifest retrieval, CPort connected/disconnected notifications, mode switching, bundle PM, and interface PM preparation.

Important APIs/types/functions: `struct gb_control` embeds a device, points to its interface and control connection, stores protocol version, capability booleans for bundle activation/version, and vendor/product strings. Lifecycle APIs are create, enable/disable, suspend/resume, add/del, get/put. Operation helpers cover bundle version discovery, connected/disconnected/disconnecting notifications, mode switch, manifest size/data retrieval, bundle suspend/resume/deactivate/activate, and interface suspend/deactivate/hibernate-abort preparations.

Control flow, state, and persistence: Interface activation creates/enables control, negotiates versions, fetches manifest data, and later uses control operations to notify CPort and power-management changes. Vendor/product strings persist as parsed interface metadata.

Dependencies/integration: It sits between `gb_interface`, `gb_connection`, Greybus control wire structs in `greybus_protocols.h`, runtime PM, and manifest parsing.

Risks and test signals: Version/capability checks must gate newer operations such as bundle activate/version. Manifest size must be trusted only after bounds checks. Tests should cover older peer capabilities, manifest size/data failures, connected/disconnected sequencing, suspend/resume status handling, mode switch, and reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_id.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/greybus_id.h

Purpose: This header defines Greybus bundle-driver match records and match flag bits.

Important APIs/types/functions: `struct greybus_bundle_id` contains `match_flags`, vendor, product, class, class major/minor, and driver-private data. Match bits distinguish vendor, product, class, class major, and class minor. `GREYBUS_DEVICE()` and `GREYBUS_DEVICE_CLASS()` in the umbrella header populate this structure for common matches.

Control flow, state, and persistence: Greybus bus matching scans a driver's id table and compares only fields selected by `match_flags`. Matched entries provide optional `driver_info` to the probing driver.

Dependencies/integration: It integrates with Greybus bus registration and Linux module device table generation for Greybus drivers.

Risks and test signals: Under-specified flags can overmatch unrelated bundles; over-specified version fields can prevent binding. Tests should cover vendor/product match, class-only match, class-version match, sentinel termination, and `driver_info` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_manifest.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/greybus_manifest.h

Purpose: This header defines the packed Greybus manifest wire format. A manifest describes strings, interfaces, bundles, and CPorts exposed by a module/interface.

Important APIs/types/functions: Enums define descriptor types, protocol IDs, class IDs, and interface feature bits. Packed structs include string descriptors with flexible strings, interface descriptor, bundle descriptor, CPort descriptor, descriptor header/union, manifest header, and manifest with flexible descriptor array. Protocol IDs cover control, GPIO, I2C, UART, HID, USB, SDIO, power supply, PWM, SPI, display, camera, sensor, lights, vibrator, loopback, audio, SVC, bootrom, firmware download/management, authentication, log, raw, and vendor.

Control flow, state, and persistence: Control protocol fetches the manifest bytes, then parser code walks descriptor headers, validates sizes/types, creates interface metadata, bundles, and CPort descriptors. The manifest itself is transient input; parsed objects persist in Greybus devices/lists.

Dependencies/integration: It is consumed by `manifest.h` parser APIs and the Greybus control/interface/bundle creation path. All numeric wire fields use explicit fixed-width endian types.

Risks and test signals: Descriptor sizes and flexible arrays must be bounds-checked to avoid malformed manifest reads. String descriptors are not NUL-terminated and are padded to 4 bytes. Tests should include truncated descriptors, unknown types/protocols, duplicate bundle IDs, invalid CPort bundle references, string padding, and feature bit parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_manifest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_protocols.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/greybus_protocols.h

Purpose: This large header is the Greybus protocol wire-format catalog. It defines operation headers, operation type numbers, status values, flags, constants, and packed request/response payload structs for control, APBridge, firmware, authentication, bootrom, power supply, HID, I2C, GPIO, PWM, SPI, SVC, raw, UART, loopback, SDIO, camera, lights, audio, and log protocols.

Important APIs/types/functions: `struct gb_operation_msg_hdr` is the common little-endian message header: size, operation id, type, result, and zero padding. The high bit of type marks responses via `GB_MESSAGE_TYPE_RESPONSE` in `operation.h`. Protocol groups then define `GB_*_TYPE_*` operation IDs and packed payloads. Notable families include control manifest/PM/mode-switch messages, firmware download/management, CAP challenge/certificate/authentication, bootrom firmware fetching, power-supply property descriptors, HID report operations, I2C transfer arrays, GPIO line/IRQ operations, SPI transfer descriptions, SVC route/connection/power-mode/DME/pwrmon/module events, UART data/line state/credits, SDIO command/transfer/event payloads, camera stream configuration and metadata, lights channel configuration/events, audio topology/control/PCM/streaming payloads, and log send requests.

Control flow, state, and persistence: This file has no executable code; it is the ABI contract consumed by Greybus protocol drivers and firmware peers. Operation code fills packed request structs, sends them through `gb_operation`, validates response result and payload size, then converts little-endian fields to host values. Flexible-array payloads carry variable-length data and must be sized from the message header.

Dependencies/integration: It depends only on fixed Linux types but is central to all Greybus core and protocol drivers. Many constants intentionally mirror Linux subsystem concepts such as power_supply properties, SPI modes, SDIO capabilities, ALSA PCM/control/topology fields, and jack types.

Risks and test signals: ABI drift is the primary risk: changing packing, field order, numeric values, or endian annotations breaks peers. Variable-length structs require strict bounds validation. Tests should include wire encode/decode golden vectors, short/oversized payload rejection, endian conversion, operation result handling, unsupported operation IDs, flexible-array length checks, and compatibility with older protocol versions/capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_protocols.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/hd.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/hd.h

Purpose: This header defines Greybus host devices and the host-controller driver operations needed to allocate CPorts, send messages, and control transport state.

Important APIs/types/functions: `struct gb_hd_driver` supplies host private size and callbacks for CPort allocate/release/enable/disable/connected/flush/shutdown/quiesce/clear, message send/cancel, latency tag enable/disable, and low-level output. `struct gb_host_device` embeds a device, bus id, driver pointer, module and connection lists, CPort IDA, CPort count, max buffer size, SVC pointer, and aligned private data. APIs reserve, allocate, release CPorts; create/add/delete/shutdown/put host devices; output messages; and init/exit host support.

Control flow, state, and persistence: Host controller drivers create a `gb_host_device`, add it to the Greybus core, and service message send/cancel callbacks from connections/operations. The host keeps persistent module/connection lists and CPort allocation state.

Dependencies/integration: It integrates Greybus core, Linux device model, IDA allocation, host-controller hardware drivers, SVC, and operation/message transport.

Risks and test signals: Buffer size, CPort count, and CPort allocation must match hardware. Send completion/cancel races affect operation lifetime. Tests should cover host add/delete, CPort reserve/allocate/release conflicts, message send errors, shutdown/quiesce phases, output from IRQ context, and host private data alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/hd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/interface.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/interface.h

Purpose: This header defines Greybus interfaces, the per-module physical/logical attachment points that own control connections, manifests, bundles, identity fields, quirks, and activation state.

Important APIs/types/functions: `enum gb_interface_type` covers invalid, unknown, dummy, UniPro, and Greybus. Quirk bits disable CPort features, init status, GMP IDs, bundle activate, PM, or force disable/legacy mode switch. `struct gb_interface` embeds a device and stores control, bundle list, module linkage, manifest descriptors, interface/device IDs, features, DDBL/vendor/product IDs, serial, host/module pointers, quirks, mutex, disconnected/ejected/removed/active/enabled/mode-switch/DME flags, mode-switch work, and completion. APIs create, activate/deactivate, enable/disable, add/del/put, handle mailbox events, and request mode switch.

Control flow, state, and persistence: A module creates interfaces; activation/control reads identity and manifest, creates bundles, and enables transport. Mode switching uses work/completion state. Flags distinguish physical removal, logical ejection, active control, and enabled runtime state.

Dependencies/integration: It coordinates host devices, modules, control, bundles, manifests, workqueues, completions, and device core.

Risks and test signals: Interface state transitions are complex around ejection, mode switch, forced disable, and PM quirks. Tests should cover activation failure unwind, manifest descriptor list cleanup, enable/disable idempotency, mailbox event handling, mode-switch timeout/completion, quirk behavior, and removal during active operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/manifest.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/manifest.h

Purpose: This header declares Greybus manifest parsing entry points.

Important APIs/types/functions: `gb_manifest_parse()` parses a raw manifest buffer of known size for a given interface, and `gb_manifest_free()` releases parsed manifest descriptor state from the interface.

Control flow, state, and persistence: Control retrieves raw bytes, `gb_manifest_parse()` validates/deserializes them into interface descriptors, bundle devices, and CPort descriptors, and `gb_manifest_free()` tears down descriptor lists on interface cleanup or parse failure.

Dependencies/integration: It consumes packed definitions from `greybus_manifest.h` and mutates `struct gb_interface` state from `interface.h`.

Risks and test signals: Parser correctness depends on size validation, descriptor ordering rules, string handling, and cleanup after partial parse. Tests should cover malformed sizes, duplicate descriptors, unknown descriptor types, missing interface descriptor, invalid bundle/CPort references, and repeated parse/free cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/manifest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/module.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/module.h

Purpose: This header defines Greybus modules, each representing a physical module with one or more interfaces attached to a host device.

Important APIs/types/functions: `struct gb_module` embeds a device, points to host, links into the host module list, records module id, interface count, disconnected flag, and a flexible array of interface pointers. Lifecycle APIs are `gb_module_create()`, `gb_module_add()`, `gb_module_del()`, and `gb_module_put()`.

Control flow, state, and persistence: SVC module-inserted events create modules with known interface counts. Adding publishes the module device and later creates interfaces. Deletion marks/removes interfaces and host links; put releases final references.

Dependencies/integration: It integrates with host devices, interfaces, Linux device model, and SVC module insertion/removal events.

Risks and test signals: Flexible-array allocation must match `num_interfaces`; removal must handle partially created interfaces. Tests should cover create/add/del lifecycle, interface pointer initialization, host list linkage, disconnected state, and reference cleanup after failed interface creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/operation.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/operation.h

Purpose: This header defines Greybus operations: request/response RPC objects sent over a connection.

Important APIs/types/functions: `enum gb_operation_result` maps Greybus result codes. `struct gb_message` stores operation pointer, wire header, payload pointer/size, backing buffer, and host-controller private pointer. Operation flags mark incoming, unidirectional, short-response allowed, and core. `struct gb_operation` stores connection, request/response messages, flags, type, id, errno result, work, callback, completion, timeout timer, kref, waiter count, active marker, connection list links, and private data. APIs create operations, allocate responses, send async/sync with timeout, cancel, receive on a connection, handle message-sent callbacks, perform one-shot sync/unidirectional operations, and init/exit operation core.

Control flow, state, and persistence: Outgoing calls create an operation, fill request payload, send via host driver, wait for completion or callback, then drop references. Incoming messages create incoming operations and dispatch work to handlers. Timers convert missing responses to timeout errors; cancellation wakes waiters and detaches active operations.

Dependencies/integration: It sits on `gb_connection`, host `gb_message` transport, workqueues, timers, completions, krefs, and packed message headers from `greybus_protocols.h`.

Risks and test signals: Races among send completion, timeout, cancel, incoming response, and connection disable are the main risk. Tests should cover sync success/error/timeout, short responses, unidirectional operations, incoming request dispatch, malformed headers, reference lifetime, and operation-core init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/operation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/svc.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/svc.h

Purpose: This header defines the Greybus SVC object and APIs for switch/control-plane operations such as routing, connection creation, interface power, DME access, pwrmon, ping, and watchdog.

Important APIs/types/functions: CPort flags encode E2EFC, CSD_N, and CSV_N. `enum gb_svc_state` tracks reset, protocol-version, and hello phases. `enum gb_svc_watchdog_bite` selects reset or panic action. `struct gb_svc` embeds a device, host, SVC connection, state, device IDA, workqueue, Endo/AP IDs, protocol version, watchdog/action, debugfs, and pwrmon rails. APIs create/add/delete/put SVC, sample pwrmon, assign interface device IDs, create/destroy routes and connections, eject and power interfaces, DME peer get/set, set power modes/hibernate, ping, and manage watchdog.

Control flow, state, and persistence: Host initialization creates SVC, negotiates version/hello, then SVC APIs issue Greybus SVC operations to configure topology and interface power. Device IDs, watchdog state, debugfs rail state, and protocol version persist in `gb_svc`.

Dependencies/integration: It integrates host devices, Greybus operations, SVC protocol payloads, IDA, workqueues, debugfs, and interface lifecycle.

Risks and test signals: Route/connection creation must be paired with destruction; DME/power-mode operations are topology- and quirk-sensitive. Tests should cover protocol negotiation, connection create/destroy failure unwind, route cleanup, interface power toggles, DME endian values, pwrmon bounds, ping timeout, watchdog enable/disable and bite action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/group_cpus.h -->
# sources/distributed-fs/ceph-client/include/linux/group_cpus.h

Purpose: This header declares a helper for dividing CPUs evenly across groups.

Important APIs/types/functions: `group_cpus_evenly(unsigned int numgrps, unsigned int *nummasks)` returns an array of `struct cpumask` entries and reports the number of masks. It includes CPU and kernel helpers.

Control flow, state, and persistence: The implementation allocates and fills cpumasks so callers can distribute interrupts, queues, or workers across CPU groups. The header itself has no state.

Dependencies/integration: It depends on Linux CPU masks and CPU topology data through `linux/cpu.h`.

Risks and test signals: Callers must handle allocation failure and free returned masks according to implementation contract. Tests should cover zero/one/many groups, more groups than CPUs, offline CPUs, NUMA/topology distribution expectations, and `nummasks` reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/group_cpus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/habanalabs/cpucp_if.h -->
# sources/distributed-fs/ceph-client/include/linux/habanalabs/cpucp_if.h

Purpose: This header defines the host-driver to HabanaLabs CpuCP firmware ABI for event queues, primary queue packets, sensor/hwmon requests, NIC data, memory-error reports, security attestation, and device information.

Important APIs/types/functions: It includes `hl_boot_if.h` and defines event IDs, EQ entry layouts, ECC/HBM/RAZWI/SEI/ARC/address-decoder event payloads, EQ control bit masks, PQ init statuses, a large `enum cpucp_packet_id`, packet control/result masks, `struct cpucp_packet` and variable-length packet wrappers, packet return codes, hwmon-aligned enums for temperature/voltage/current/fan/pwm/power, MSI/PLL/RL/PVT indexes, `struct cpucp_info`, NIC info/status structures, HBM row replacement data, security attestation structures, monitor dump structures, and generic passthrough subcommands.

Control flow, state, and persistence: The host writes one CpuCP packet in device memory, clears the fence, interrupts firmware, polls the fence, and reads result/output fields. EQ entries flow asynchronously from firmware to host with ready/type/index bits and fixed payload union. Device information and NIC/security data are returned into host-provided buffers sized by `data_max_size` to tolerate firmware/driver version mismatch.

Dependencies/integration: It is tightly coupled to the HabanaLabs PCI driver, firmware, hwmon, NIC management, security/TPM attestation, event queue interrupt handling, and boot interface definitions. Fields use fixed endian types because data crosses host/firmware boundaries.

Risks and test signals: ABI stability is critical: enum order comments explicitly forbid reordering MSI/PLL values. Flexible arrays and host-provided sizes must be validated to prevent firmware/driver mismatch corruption. Tests should cover packet encode/decode, fence timeout/error return codes, EQ ready/index handling, endian conversion, event payload sizing, NIC mask lengths, security buffer length fields, and compatibility with older firmware lacking newer packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/habanalabs/cpucp_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/habanalabs/hl_boot_if.h -->
# sources/distributed-fs/ceph-client/include/linux/habanalabs/hl_boot_if.h

Purpose: This header defines the HabanaLabs boot-loader/firmware communication ABI shared between the Linux kernel driver and device firmware across preboot, U-Boot/Linux firmware, component loading, reset, status, errors, and version reporting.

Important APIs/types/functions: It defines boot magic values, FIT SRAM offset, version length, `enum cpu_boot_err` with fatal mask and bit macros, `enum cpu_boot_dev_sts` with feature/status bit macros, `enum cpu_boot_status`, KMD messages, CPU message status, `struct cpu_dyn_regs` register map, communication descriptor/message magics and validation macros, message types, `struct lkd_fw_binning_info`, descriptor/message headers with CRC/size/version/type, ASCII firmware messages, `struct lkd_fw_comms_desc`, reset causes, `struct lkd_fw_comms_msg`, command/status enums and bitfield wrappers, module/version structures, and FIT version size limit.

Control flow, state, and persistence: The host and firmware exchange commands through registers: host writes a `comms_command`, firmware acknowledges and later writes a `comms_status` containing status plus SRAM/DRAM offset. Descriptor/message headers carry magic, CRC, size, and version so the host can validate data. Boot status/error/device-status registers persist the current firmware stage and capabilities.

Dependencies/integration: It feeds `cpucp_if.h` and the HabanaLabs driver boot path. It assumes firmware-side bitfield producers but host-side code should use masks and endian-aware fields.

Risks and test signals: Many comments warn to consider ABI before changing structures and counts. Bit shifts such as `1 << CPU_BOOT_ERR_SCND_EN` exceed 32-bit masks if used incorrectly; the header separates register 0/1 enabled bits. Tests should cover magic/version validation, CRC/size checks, command/status packing, boot error fatal classification, status feature gating, descriptor compatibility versions, and reset/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/habanalabs/hl_boot_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hardirq.h -->
# sources/distributed-fs/ceph-client/include/linux/hardirq.h

Purpose: This header defines generic hard IRQ and NMI context entry/exit helpers used by architecture IRQ paths and low-level kernel code.

Important APIs/types/functions: It declares `synchronize_irq()` and `synchronize_hardirq()`, optional NO_HZ_FULL `__rcu_irq_enter_check_tick()`, and inline `rcu_irq_enter_check_tick()`. Macros `__irq_enter()`, `__irq_enter_raw()`, `__irq_exit()`, and `__irq_exit_raw()` adjust preempt count, lockdep state, and hardirq accounting. Functions `irq_enter()`, `irq_enter_rcu()`, `irq_exit()`, and `irq_exit_rcu()` provide higher-level paths. NMI helpers `__nmi_enter()`, `nmi_enter()`, `__nmi_exit()`, and `nmi_exit()` manage lockdep, arch hooks, preempt count, context tracking, instrumentation, and ftrace.

Control flow, state, and persistence: IRQ entry increments hardirq preempt count before code runs in hardirq context; exit decrements and may process softirqs through implementation. NMI entry disables lockdep, adds NMI plus hardirq offsets, enters context tracking/tracing, and exit reverses the sequence. These helpers rely on strictly balanced entry/exit calls.

Dependencies/integration: It integrates preempt accounting, lockdep, ftrace IRQ/NMI tracing, context tracking, scheduler hardirq time accounting, vtime, and architecture hardirq definitions.

Risks and test signals: Incorrect ordering can make tracing observe inconsistent `in_nmi()`/preempt state. Unbalanced entry/exit corrupts preempt count and lockdep state. Tests/signals include lockdep IRQ state validation, ftrace NMI tracing, NO_HZ full tick checks, softirq processing after IRQ exit, and architecture build coverage for arch NMI hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hash.h -->
# sources/distributed-fs/ceph-client/include/linux/hash.h

Purpose: This header provides fast integer and pointer hashing helpers for kernel hash tables and subsystems.

Important APIs/types/functions: It defines `GOLDEN_RATIO_32`, `GOLDEN_RATIO_64`, word-size-dependent `GOLDEN_RATIO_PRIME`, and `hash_long()`. Generic helpers include `__hash_32_generic()`, `hash_32()`, `hash_64_generic()`, `hash_ptr()`, and `hash32_ptr()`. Architecture overrides can supply `<asm/hash.h>` and `HAVE_ARCH_*` definitions under `CONFIG_HAVE_ARCH_HASH`.

Control flow, state, and persistence: Hashing multiplies by an odd golden-ratio-derived constant and uses the high bits of the product. There is no persistent state. `hash32_ptr()` only folds a pointer to 32 bits and intentionally does not perform full hashing.

Dependencies/integration: It depends on architecture types, compiler helpers, word size, and optional arch-optimized hash functions. `hashtable.h` uses these helpers through `hash_min()`.

Risks and test signals: Passing invalid `bits` values can shift incorrectly or create poor bucket selection. Architecture overrides must match generic behavior expectations or update self-test markers. Tests should use `lib/test_hash.c`, compare arch and generic variants, exercise 32/64-bit builds, pointer folding, and distribution for typical key sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hashtable.h -->
# sources/distributed-fs/ceph-client/include/linux/hashtable.h

Purpose: This header implements statically sized kernel hash tables using arrays of `hlist_head` buckets.

Important APIs/types/functions: Definition macros include `DEFINE_HASHTABLE()`, `DEFINE_READ_MOSTLY_HASHTABLE()`, and `DECLARE_HASHTABLE()`. Sizing macros are `HASH_SIZE()` and `HASH_BITS()`. `hash_min()` selects `hash_32()` for small keys or `hash_long()` otherwise. Helpers include `hash_init()`, `hash_add()`, `hash_add_rcu()`, `hash_hashed()`, `hash_empty()`, `hash_del()`, `hash_del_rcu()`, and iteration macros for all buckets, RCU, safe removal, possible matching bucket, possible RCU/notrace, and possible safe removal.

Control flow, state, and persistence: A table is an in-place bucket array owned by the caller. Objects embed `hlist_node` members and are inserted into bucket heads based on the hashed key. The macros do not compare keys; callers must compare object keys inside `hash_for_each_possible*` loops. RCU variants rely on caller-side RCU read-side locking and deferred freeing.

Dependencies/integration: It depends on list/hlist, kernel array helpers, `hash.h`, and RCU list primitives.

Risks and test signals: `HASH_BITS()` only works on actual arrays, not pointers, so `hash_init()` and macros require compile-time arrays. Missing key comparison after bucket iteration causes false matches. Tests should cover table init, add/delete, empty state, safe deletion while iterating, RCU insertion/deletion under readers, bucket distribution, and pointer-vs-array misuse caught at build time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hashtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hashtable_api.h -->
# sources/distributed-fs/ceph-client/include/linux/hashtable_api.h

Purpose: This one-line compatibility/export header includes `linux/hashtable.h`.

Important APIs/types/functions: It declares no independent API. Including it exposes the static hash table macros and helpers from `hashtable.h`.

Control flow, state, and persistence: None in this file; all behavior is inherited from `hashtable.h`.

Dependencies/integration: It exists for include-path compatibility with users expecting a separate hashtable API header.

Risks and test signals: The only practical risk is stale includes masking direct dependency cleanup. Build tests should ensure consumers compile and no include recursion or guard conflict occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hashtable_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hdlc.h -->
# sources/distributed-fs/ceph-client/include/linux/hdlc.h

Purpose: This header defines the generic HDLC network-device support interface between HDLC hardware drivers and protocol modules.

Important APIs/types/functions: `struct hdlc_proto` defines protocol callbacks for open/close, carrier start/stop, detach, ioctl, type translation, RX, transmit, module owner, and linked-list membership. `hdlc_device` is stored in `netdev_priv()` and contains hardware `attach` and `xmit` callbacks plus internal protocol pointer, carrier/open flags, state lock, protocol state, and hardware private pointer. APIs include `hdlc_ioctl()`, `register_hdlc_device()`, `unregister_hdlc_device()`, protocol register/unregister, `alloc_hdlcdev()`, `dev_to_hdlc()`, `debug_frame()`, `hdlc_open()`, `hdlc_close()`, `hdlc_start_xmit()`, `attach_hdlc_protocol()`, `detach_hdlc_protocol()`, and `hdlc_type_trans()`.

Control flow, state, and persistence: Hardware drivers allocate/register an HDLC netdev and route `ndo_start_xmit` to `hdlc_start_xmit()`. User ioctls attach protocol modules. Open/close and carrier changes call protocol start/stop hooks while state is protected by `state_lock`. `hdlc_type_trans()` lets protocol override packet type or defaults to `ETH_P_HDLC`.

Dependencies/integration: It integrates Linux netdevice, skbuff, HDLC ioctl/uapi definitions, modules, spinlocks, and protocol plugins.

Risks and test signals: Protocol attach/detach must respect module lifetime and open/carrier state. `debug_frame()` prints up to 100 bytes and should not be used on hot paths. Tests should cover protocol registration, ioctl attach, open/close, carrier transitions, TX/RX delegation, detach while open, and default/custom type translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hdlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hdmi.h -->
# sources/distributed-fs/ceph-client/include/linux/hdmi.h

Purpose: This header defines common HDMI InfoFrame, HDR metadata, and packet helper interfaces used by DRM/display drivers and related display code.

Important APIs/types/functions: It enumerates HDMI packet/infoframe types, colorspaces, scan modes, colorimetry, aspect ratios, quantization ranges, content types, HDR EOTF/metadata types, audio coding/sample sizes/rates, 3D structures, and SPD source device info. Structures include `hdmi_any_infoframe`, `hdmi_avi_infoframe`, `hdmi_drm_infoframe`, `hdmi_spd_infoframe`, `hdmi_audio_infoframe`, `hdmi_vendor_infoframe`, `hdr_static_metadata`, `hdr_sink_metadata`, `union hdmi_vendor_any_infoframe`, and `union hdmi_infoframe`. APIs initialize, check, pack, pack-only, unpack, log, and DP-pack audio infoframes.

Control flow, state, and persistence: Callers fill a typed infoframe, run init/check helpers, then pack it into the HDMI wire buffer with header/checksum. `pack()` variants may validate/update frame state; `pack_only()` assumes validation requirements are met. The union pack/unpack path dispatches based on the common `type` header.

Dependencies/integration: It depends on Linux device/types and `struct dp_sdp` for DisplayPort audio SDP packing. It mirrors CTA/CEA/HDMI field definitions and is used by display bridge/encoder drivers.

Risks and test signals: Buffer sizing must account for header plus payload. Enum values must match standards. HDR and vendor infoframes require correct OUI and length. Tests should include golden byte encodings for AVI/SPD/audio/vendor/DRM frames, invalid enum rejection, short buffer handling, checksum validation, unpack round trips, and DP audio conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hex.h -->
# sources/distributed-fs/ceph-client/include/linux/hex.h

Purpose: This header declares common hex conversion helpers.

Important APIs/types/functions: It exposes hex character tables, `hex_to_bin()`, `hex2bin()`, `bin2hex()`, `hex_dump_to_buffer()`, `print_hex_dump()`, `print_hex_dump_bytes()`, and related row/group/prefix constants. These helpers convert ASCII hex to bytes, bytes to ASCII hex, and binary buffers to formatted diagnostic output.

Control flow, state, and persistence: Conversion helpers are stateless. `hex2bin()` validates pairs of hex characters and returns an error for invalid input. Dump helpers format rows with configurable row size, group size, ASCII inclusion, and prefix style before printing or returning text.

Dependencies/integration: It integrates with kernel logging/printk and is used widely by protocol, driver, crypto, and debug paths.

Risks and test signals: Invalid hex input, odd lengths, insufficient output buffers, and formatting expectations are the main concerns. Tests should cover upper/lowercase digits, invalid characters, zero-length buffers, every grouping mode, ASCII column formatting, prefix address/offset modes, and output truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hex.h -->
