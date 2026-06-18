# subset-b-001024 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/ec.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/ec.c

Purpose: `ec.c` is the Linux ACPI Embedded Controller driver. It discovers ECs from ECDT or DSDT, installs the EC address-space handler for AML OpRegions, drives byte-oriented EC transactions over command/data I/O ports, handles EC GPE or GPIO interrupt events, dispatches `_Qxx` query methods, exports the first EC to other kernel users, and coordinates suspend/resume behavior.

Important APIs, types, and functions: the file defines EC protocol constants, `struct transaction`, `struct acpi_ec_query_handler`, and `struct acpi_ec_query`, while `struct acpi_ec` is declared in `internal.h`. Public symbols include `first_ec`, `ec_read()`, `ec_write()`, `ec_transaction()`, `ec_get_handle()`, `acpi_ec_add_query_handler()`, `acpi_ec_remove_query_handler()`, and PM helpers such as `acpi_ec_block_transactions()`, `acpi_ec_unblock_transactions()`, `acpi_ec_flush_work()`, `acpi_ec_dispatch_gpe()`, `acpi_ec_mark_gpe_for_wake()`, and `acpi_ec_set_gpe_wake_mask()`. Core internal paths are `acpi_ec_transaction()`, `advance_transaction()`, `ec_poll()`, `acpi_ec_space_handler()`, `ec_install_handlers()`, `acpi_ec_probe()`, `acpi_ec_dsdt_probe()`, `acpi_ec_ecdt_probe()`, and `acpi_ec_init()`.

Control flow: initialization creates ordered event and query workqueues, registers the `acpi-ec` platform driver, probes boot ECs early via ECDT or DSDT, then finalizes ECDT namespace binding. A transaction is serialized by `ec->mutex`, optionally protected by the ACPI global lock, stored in `ec->curr`, and progressed by `advance_transaction()` whenever polling or interrupts observe IBF/OBF state changes. The same state machine starts with a command write, writes request bytes, reads response bytes, marks completion, and wakes waiters. SCI/GPE events call `acpi_ec_submit_event()`, queue `acpi_ec_event_handler()`, run `ACPI_EC_COMMAND_QUERY`, then schedule `_Qxx` work on `ec_query_wq` up to `ec_max_queries`. The address-space handler translates AML EC OpRegion reads/writes into one or more EC byte transactions, using burst mode for multi-byte or busy-polling cases.

State and persistence: all state is in memory and hardware registers. `first_ec` is the global external EC, `boot_ec` tracks early ECDT/DSDT state, `flags` tracks handler/query/start/stop/event-mask lifecycle, `reference_count` keeps the GPE enabled while transactions or driver references exist, and counters track pending events and queries. Module parameters tune timeouts, busy polling, query concurrency, storm masking, event clearing timing, suspend event freezing, and s2idle wake suppression. DMI tables set quirks for broken ECDT data, DSDT GPE trust, stale event clearing, and EC wakeup behavior.

Dependencies and integration: this file depends on ACPICA namespace/resource/GPE APIs, Linux platform devices, workqueues, wait queues, IRQ/GPIO IRQ helpers, I/O port accessors, DMI, PM sleep hooks, and the ACPI scan/early-device machinery. It is the provider for `ec_sys.c`, EC OpRegion AML, ACPI device dependency clearing, and other drivers registering EC query handlers.

Risks: the code is timing-sensitive and firmware-dependent. Races around SCI_EVT clearing, GPE enable/disable, transaction restart after timeout, and event masking can drop events or create storms if ordering changes. `first_ec` means exported EC access is effectively single-controller. `_Qxx` handlers run asynchronously, so handler lifetime depends on `kref` discipline and query workqueue flushing. Error paths around boot EC deduplication, ECDT quirks, and handler installation are high risk because the EC is needed very early.

Test signals: useful validation includes boot logs for EC port/GPE/IRQ selection, ECDT/DSDT duplicate handling, EC OpRegion access from AML, debug traces for transaction progression under interrupt and polling modes, suspend/resume and s2idle wake tests, DMI quirk machines, stale event clearing on resume, query handler add/remove with concurrent `_Qxx`, GPE storm masking, and module parameter coverage for `ec_event_clearing`, `ec_busy_polling`, and `ec_freeze_events`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/ec_sys.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/ec_sys.c

Purpose: `ec_sys.c` exposes the first ACPI EC through debugfs for diagnostics. It creates `debugfs/ec/ec0/` with read-only metadata and an `io` file that lets privileged users read the 256-byte EC address space, with optional writes behind the dangerous `write_support` module parameter.

Important APIs, types, and functions: the file uses `ec_read()` and `ec_write()` exported by `ec.c`, debugfs helpers, and user-copy helpers. Main functions are `acpi_ec_read_io()`, `acpi_ec_write_io()`, `acpi_ec_add_debugfs()`, `acpi_ec_sys_init()`, and `acpi_ec_sys_exit()`. `EC_SPACE_SIZE` fixes the exposed EC range at 256 bytes.

Control flow: module init checks `first_ec` and creates the debugfs tree. Reads clamp the requested range to EC address space, loop byte-by-byte from `*off`, call `ec_read()`, copy each byte to userspace, and update the file offset. Writes are rejected unless `write_support` is set, then similarly clamp and loop through `get_user()` plus `ec_write()`. Exit recursively removes the debugfs root.

State and persistence: persistent state is limited to the debugfs dentry pointer and the module parameter. EC contents are hardware state owned by firmware. The implementation currently uses `first_ec` even though `acpi_ec_add_debugfs()` accepts an EC pointer; comments note future multi-EC support.

Dependencies and integration: this is a debug companion to the EC driver, not the primary ACPI EC path. It integrates with debugfs and the `ec.c` global EC exports, so it only works after the core driver has found `first_ec`.

Risks: writes can corrupt firmware-controlled EC state and are intentionally gated. The read/write loops return partial lengths on user-copy failures but return EC errors immediately, so tooling must handle short I/O. Use of `first_ec` in debugfs metadata and operations means multi-EC systems are not represented accurately.

Test signals: verify debugfs creation when an EC exists, absence or harmless init when no EC exists, offset clamping at 256 bytes, partial read/write behavior, permissions with and without `write_support`, and that EC access errors propagate to userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/ec_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/event.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/event.c

Purpose: `event.c` provides kernel ACPI event fan-out. It maintains a blocking notifier chain for in-kernel consumers and, when networking is enabled, registers a generic netlink family named `acpi_event` to multicast ACPI events to userspace.

Important APIs, types, and functions: exported notifier APIs are `acpi_notifier_call_chain()`, `register_acpi_notifier()`, and `unregister_acpi_notifier()`. Exported userspace event API is `acpi_bus_generate_netlink_event()`. The netlink payload type is `struct acpi_genl_event`; family constants describe the `ACPI_GENL_ATTR_EVENT` attribute and `ACPI_GENL_CMD_EVENT` command.

Control flow: ACPI event producers call `acpi_notifier_call_chain()` with a device class, bus id, type, and data, which fills `struct acpi_bus_event` and invokes the blocking chain. For netlink, producers allocate an skb in atomic context, add a genetlink header, reserve a payload attribute, fill event fields, close the message, and multicast it to the ACPI multicast group. `fs_initcall(acpi_event_init)` registers the genetlink family unless ACPI is disabled.

State and persistence: state is process lifetime only: the notifier chain head, a monotonically increasing `acpi_event_seqnum`, and the registered genetlink family. Events are not stored or replayed.

Dependencies and integration: this file integrates ACPI bus events with both kernel notifiers and userspace generic netlink. It is used by drivers such as the ACPI fan driver to emit state-change events.

Risks: netlink allocation uses `GFP_ATOMIC` and can fail under pressure, losing events. `bus_id` is fixed at 15 bytes in the netlink payload, so identifiers may be truncated. Notifier callbacks run in a blocking notifier context and can delay the event source.

Test signals: verify genetlink family registration, multicast receive from userspace, event field truncation behavior, no-op stub behavior without `CONFIG_NET`, notifier registration/unregistration, and event generation while ACPI is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/evged.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/evged.c

Purpose: `evged.c` implements the ACPI Generic Event Device driver for `ACPI0013`. GED lets firmware describe interrupt resources in `_CRS` and handle them in AML methods such as `_EVT`, `_Exx`, or `_Lxx`.

Important APIs, types, and functions: key structures are `struct acpi_ged_device` and `struct acpi_ged_event`. Core functions are `acpi_ged_request_interrupt()`, `acpi_ged_irq_handler()`, `ged_probe()`, `ged_shutdown()`, and `ged_remove()`. The driver is registered as a built-in platform driver.

Control flow: probe allocates a GED device container, initializes an event list, and walks `_CRS`. Each IRQ resource is translated to a Linux IRQ using ACPI resource helpers, then the driver chooses a handler method: for GSI 0-255 it first looks for `_E##` or `_L##` based on trigger mode, otherwise it falls back to `_EVT`. It allocates an event object, requests a threaded IRQ, and stores it in the list. The IRQ thread executes the selected AML method, passing the GSI as the argument. Shutdown/remove frees all registered IRQs and clears the list.

State and persistence: state is devm-managed per platform device plus a list of event records containing GSI, IRQ, ACPI handle, and device pointer. There is no persistent storage.

Dependencies and integration: GED depends on ACPI `_CRS` interrupt parsing, Linux IRQ request/free APIs, platform-driver matching, and AML method execution. It bridges platform interrupts into firmware-owned ASL event handlers.

Risks: if firmware advertises an interrupt without a matching method, probe fails for that resource walk. Requesting threaded IRQs with AML execution means handler latency and AML failures matter; failures are logged once. Shutdown must free IRQs before firmware or platform teardown to avoid callbacks into removed state.

Test signals: validate `_EVT`, `_Exx`, and `_Lxx` method selection, shared interrupt flags, IRQ resource parse failures, threaded IRQ execution, shutdown cleanup, and probe behavior with multiple interrupt descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/evged.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/fan.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/fan.h

Purpose: `fan.h` is the shared ACPI fan driver interface. It centralizes ACPI fan device IDs, ACPI 4.0 fan data structures, driver state, validation helpers, and cross-file function declarations used by the core, sysfs-attribute, and hwmon fan files.

Important APIs, types, and functions: `ACPI_FAN_DEVICE_IDS` lists Intel thermal fan HIDs and generic `PNP0C0B`. Data models include `struct acpi_fan_fps` for `_FPS` performance states, `struct acpi_fan_fif` for `_FIF` capabilities, `struct acpi_fan_fst` for `_FST` current state, and `struct acpi_fan` for per-device driver data. Inline helpers `acpi_fan_speed_valid()` and `acpi_fan_power_valid()` reject `U32_MAX` and larger placeholder values. Declared functions include `acpi_fan_get_fst()`, attribute create/delete helpers, and hwmon hooks with stubs when hwmon is unavailable.

Control flow: the header itself has no runtime flow, but it defines the shared contracts followed by `fan_core.c`, `fan_attr.c`, and `fan_hwmon.c`.

State and persistence: `struct acpi_fan` stores per-device ACPI handle, ACPI 4.0 capability flags, `_FIF` data, `_FPS` array, optional Microsoft DSM trip granularity, optional hwmon device, thermal cooling device, and sysfs attributes. All state is in-memory and regenerated on probe.

Dependencies and integration: the header integrates ACPI, thermal cooling, optional hwmon, and device sysfs attribute code. The ID macro is intentionally shared with ACPI power-management code.

Risks: the speed/power validity helpers encode firmware placeholder behavior; callers that bypass them may expose invalid values. `ACPI_FPS_NAME_LEN` bounds generated sysfs names such as `stateN`, so large state counts rely on sane formatting.

Test signals: compile coverage with and without `CONFIG_HWMON`, ACPI 4.0 and legacy fan probe paths, validation of `U32_MAX` placeholder values, and HID matching for new fan IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/fan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/fan_attr.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/fan_attr.c

Purpose: `fan_attr.c` creates extra sysfs attributes for ACPI fans with `_FST`, especially ACPI 4.0 fans with `_FIF/_FPS/_FSL`. It exposes current RPM, fine-grain control capability, and one read-only `stateN` file per fan performance state.

Important APIs, types, and functions: the main exported helpers are `acpi_fan_create_attributes()` and `acpi_fan_delete_attributes()`. Attribute show functions are `show_fan_speed()`, `show_fine_grain_control()`, and `show_state()`.

Control flow: creation always adds `fan_speed_rpm` for `_FST` fans. If the fan is not ACPI 4.0, it stops there. For ACPI 4.0, it adds `fine_grain_control`, then iterates `_FPS` entries to create `state0`, `state1`, etc. Each `stateN` line reports control, trip point, speed, noise level scaled by 100, and power, replacing invalid sentinel values with `not-defined`. Error handling unwinds already-created files. Deletion removes the same files in reverse logical scope.

State and persistence: the file stores sysfs `device_attribute` objects inside `struct acpi_fan` and each `struct acpi_fan_fps`. It does not persist values; reads evaluate current `_FST` only for `fan_speed_rpm`, while `stateN` shows cached `_FPS` data parsed during probe.

Dependencies and integration: depends on ACPI device driver data from `fan_core.c`, `acpi_fan_get_fst()`, and sysfs APIs. The attributes are created and removed by fan probe/remove and error paths.

Risks: invalid firmware values are partly normalized for display but `show_fan_speed()` prints `_FST` speed directly, relying on lower layers or users to interpret placeholders. Partial sysfs creation must unwind correctly to avoid dangling attributes. The `stateN` format is ABI-like and should not change casually.

Test signals: verify sysfs files for legacy `_FST` fans and ACPI 4.0 fans, invalid sentinel formatting, creation unwind after injected sysfs failures, removal after probe failure and driver remove, and live `_FST` read error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/fan_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/fan_core.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/fan_core.c

Purpose: `fan_core.c` is the ACPI fan platform driver. It supports both legacy fans controlled through ACPI power states and ACPI 4.0 fans controlled through `_FST`, `_FIF`, `_FPS`, and `_FSL`, registers thermal cooling devices, optionally exposes hwmon data, and supports Microsoft fan DSM trip-point extensions.

Important APIs, types, and functions: the externally used function is `acpi_fan_get_fst()`. Cooling callbacks are `fan_get_max_state()`, `fan_get_cur_state()`, and `fan_set_cur_state()`. ACPI parsers include `acpi_fan_get_fif()` and `acpi_fan_get_fps()`. DSM helpers include `acpi_fan_dsm_init()`, `acpi_fan_dsm_start()`, `acpi_fan_dsm_set_trip_points()`, and `acpi_fan_dsm_update_trips_points()`. Lifecycle functions are `acpi_fan_probe()`, `acpi_fan_remove()`, and PM callbacks.

Control flow: probe allocates `struct acpi_fan`, detects `_FST`, and decides ACPI 4.0 support by checking `_FIF`, `_FPS`, and `_FSL`. ACPI 4.0 fans parse capabilities, parse and sort performance states by speed, initialize Microsoft DSM support if present, register hwmon, install an ACPI notify handler, prime DSM trip notifications, and create extra sysfs attributes. Legacy fans update initial ACPI power state. All fans register a thermal cooling device and create reciprocal sysfs links. Runtime cooling callbacks map thermal states to either ACPI power state or `_FSL` control values. Notify event `0x80` evaluates `_FST`, updates DSM trip points, notifies hwmon, and generates a netlink ACPI event.

State and persistence: per-device state includes parsed `_FIF`, sorted `_FPS`, current hwmon and cooling device pointers, DSM trip granularity, and sysfs attributes. Firmware remains the source of current control and speed through `_FST`. The only tunable is `min_trip_distance`, controlling DSM trip-point spacing.

Dependencies and integration: integrates with ACPI method evaluation and `_DSD` notifications, thermal framework cooling devices, optional hwmon via `fan_hwmon.c`, sysfs attributes via `fan_attr.c`, ACPI netlink events from `event.c`, and platform-driver ACPI HID matching from `fan.h`.

Risks: firmware data validation is critical. `_FIF` step size is clamped to 1-9, but `_FPS` values can still contain sentinel or extreme numbers. `acpi_fan_speed_cmp()` subtracts speeds as `int`, so unusually large firmware speed deltas can overflow comparison semantics. DSM notification priming relies on firmware behavior outside the base ACPI fan spec. Probe error paths must remove attributes only after they have been created.

Test signals: test legacy power-state fans, ACPI 4.0 discrete and fine-grain fans, `_FST` parse errors, `_FPS` invalid packages, thermal cooling state mapping, `_FSL` failures, ACPI notify event `0x80`, DSM-capable systems, resume reinitialization, sysfs link cleanup, and hwmon registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/fan_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/fan_hwmon.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/fan_hwmon.c

Purpose: `fan_hwmon.c` exposes ACPI fan telemetry through the Linux hwmon subsystem. It maps current `_FST` values and the current `_FPS` entry to standard fan and power sensor attributes.

Important APIs, types, and functions: public hooks are `devm_acpi_fan_create_hwmon()` and `acpi_fan_notify_hwmon()`. Internal helpers are `acpi_fan_get_current_fps()`, `acpi_fan_hwmon_is_visible()`, and `acpi_fan_hwmon_read()`. The hwmon chip exposes `fan_input`, optional `fan_target`, and optional `power_input`.

Control flow: registration attaches an `acpi_fan` hwmon device using `devm_hwmon_device_register_with_info()`. Visibility always allows current fan RPM, but only exposes target RPM and power for ACPI 4.0 non-fine-grain fans, and only exposes power if at least one `_FPS` state has valid power. Reads evaluate `_FST`, validate current speed, locate the `_FPS` entry whose control matches current control, and return speed or power converted from milliwatts to microwatts. Notify integration emits a hwmon event for `fan_input`.

State and persistence: the hwmon device pointer is stored in `struct acpi_fan`. Sensor values are not cached; reads query firmware through `acpi_fan_get_fst()` and use parsed `_FPS` state data from probe.

Dependencies and integration: depends on the hwmon core, ACPI fan core parser/state, unit conversion constants, and validity helpers in `fan.h`. It is conditionally compiled through the header's `IS_REACHABLE(CONFIG_HWMON)` hooks.

Risks: if `_FST` control does not match any parsed `_FPS` state, target and power reads fail with `-EIO`. Invalid or oversized firmware values become `-ENODEV` or `-EOVERFLOW`. Fine-grain fans hide target and power because not every control value maps to a performance state.

Test signals: verify hwmon file visibility for legacy, ACPI 4.0 discrete, and ACPI 4.0 fine-grain fans; validate unit conversion for power; exercise invalid speed/power sentinels; test no matching current FPS; and confirm notify events reach hwmon listeners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/fan_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/glue.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/glue.c

Purpose: `glue.c` links Linux physical devices with ACPI namespace devices. It lets bus integrations register matching logic, finds ACPI child devices by address, binds/unbinds `struct device` instances to `struct acpi_device`, creates sysfs firmware/physical-node links, and invokes bus-specific setup or ACPI scan-handler bind callbacks.

Important APIs, types, and functions: exported bus registration APIs are `register_acpi_bus_type()` and `unregister_acpi_bus_type()`. Child lookup exports are `acpi_find_child_device()` and `acpi_find_child_by_adr()`. Binding exports are `acpi_bind_one()` and `acpi_unbind_one()`. Device core entry points are `acpi_device_notify()` and `acpi_device_notify_remove()`.

Control flow: bus types are stored in a global list under an rwsem. Child lookup walks ACPI children matching `_ADR`, optionally requiring children and `_STA`, and scores ambiguous matches. Binding takes references on both devices, allocates a physical-node record, assigns the first free node id, optionally sets `ACPI_COMPANION`, creates `physical_node*` and `firmware_node` sysfs links, and propagates wake capability. Device notification first tries to bind an already-known companion; if none, it asks registered bus types to find one. It then performs PCI ACPI setup, platform MSI setup, custom bus setup, or scan-handler bind. Removal performs matching cleanup and unbinds.

State and persistence: state is in-memory: the registered bus-type list and each ACPI device's physical-node list. Sysfs links persist only while the binding exists.

Dependencies and integration: this file sits at the boundary of the generic device core, ACPI scan core, PCI ACPI support, platform MSI configuration, wakeup capability, sysfs, and custom ACPI scan handlers.

Risks: binding has multiple side effects and partial sysfs link failures are logged but do not abort the bind. Duplicate or ambiguous `_ADR` namespace entries are handled by heuristics, so firmware violations can still attach the wrong companion. Reference counting must remain paired across duplicate-bind and error paths. Bus-type registration order can affect matching if multiple types match one device.

Test signals: cover duplicate bind attempts, unbind with and without a companion, sysfs link failure injection, ambiguous child `_ADR` scoring, PCI and platform-device paths, handler bind/unbind callbacks, wake-capable propagation, and bus registration while ACPI is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/hed.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/hed.c

Purpose: `hed.c` implements the ACPI Hardware Error Device driver for `PNP0C33`. It receives ACPI device notifications used for hardware error signaling and forwards them to registered HED notifier clients, mainly for SCI-notified HEST Generic Hardware Error Sources.

Important APIs, types, and functions: exported APIs are `register_acpi_hed_notifier()` and `unregister_acpi_hed_notifier()`. Core functions are `acpi_hed_notify()`, `acpi_hed_probe()`, and `acpi_hed_remove()`. `hed_handle` enforces a single HED instance.

Control flow: subsystem init registers a platform driver matched on `PNP0C33`. Probe obtains the ACPI companion, rejects additional HED instances, records the handle, and installs an ACPI device notify handler. When firmware notifies the device, the handler calls the blocking notifier chain. Remove unregisters the ACPI notify handler and clears the global handle.

State and persistence: state consists of the single global `hed_handle` and the blocking notifier chain. No event payload is persisted; notifications simply wake registered clients.

Dependencies and integration: integrates ACPI platform-device probing, ACPI notify handlers, Linux blocking notifiers, and external HED users declared through `<acpi/hed.h>`.

Risks: only one HED is supported; systems exposing multiple matching devices will reject later probes. The notifier has no event details, so consumers must discover error state elsewhere. Blocking notifier callbacks can delay notification processing.

Test signals: verify single-instance enforcement, notify handler install/remove, notifier registration and callback delivery, remove cleanup, and behavior when no ACPI companion exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/hed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/internal.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/internal.h

Purpose: `internal.h` is the private ACPI subsystem header for infrastructure code, not general drivers. It declares cross-file initialization hooks, scan/hotplug helpers, power-resource APIs, EC internals, sleep hooks, property parsing, watchdog/LPIT hooks, and MIPI CSI-2 graph helpers.

Important APIs, types, and functions: notable declarations include ACPI init functions (`acpi_scan_init()`, `acpi_processor_init()`, `acpi_platform_init()`), PCI/IOAPIC hooks, hotplug scheduling functions, device-object setup/removal functions, power-resource operations, EC definitions (`enum acpi_ec_event_state`, `struct acpi_ec`, `first_ec`, EC helper prototypes), sleep/NVS hooks, property helpers, and MIPI helpers such as `acpi_mipi_check_crs_csi2()` and `acpi_graph_ignore_port()`.

Control flow: the header has no runtime flow, but conditional compilation selects real declarations or inline stubs based on configuration. This lets ACPI core files call optional subsystem hooks without scattering ifdefs through call sites.

State and persistence: it exposes internal shared state such as `acpi_root`, `acpi_bus_id_list`, `first_ec`, and per-device structures managed elsewhere. `struct acpi_ec` defines the EC driver's mutex, spinlock, waitqueue, current transaction pointer, work item, event counters, query counters, and polling state.

Dependencies and integration: this file is the internal contract among ACPI scan, PCI, processor, EC, thermal, sleep, property, watchdog, LPIT, IOAPIC, and MIPI DisCo code. It depends on kernel ACPI and ID allocator definitions.

Risks: because it is private but widely included, changes can silently affect many ACPI compilation units. Stub behavior must match real behavior enough that callers remain correct across configs. The EC struct couples `ec.c` tightly to declarations here, so layout changes need full EC lifecycle review.

Test signals: build matrix coverage across ACPI feature configs, especially `CONFIG_ACPI_EC`, `CONFIG_PM_SLEEP`, `CONFIG_PCI`, `CONFIG_X86`, `CONFIG_ACPI_HOTPLUG_IOAPIC`, and MIPI-related paths. Static analysis should catch stale prototypes and mismatched stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/ioapic.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/ioapic.c

Purpose: `ioapic.c` manages ACPI-described IOAPIC/IOxAPIC/IOSAPIC devices added through PCI root hotplug after boot. Boot IOAPICs are registered from MADT elsewhere; this file discovers additional ACPI devices, reserves resources, registers IOAPICs, and removes them on root teardown.

Important APIs, types, and functions: `struct acpi_pci_ioapic` records the root handle, device handle, GSI base, resource, optional PCI device, and list entry. Public functions are `acpi_ioapic_add()`, `pci_ioapic_remove()`, and `acpi_ioapic_remove()`. Internal helpers include `setup_res()`, `acpi_is_ioapic()`, and `handle_ioapic_add()`.

Control flow: `acpi_ioapic_add()` walks ACPI devices under a root. Each candidate must have `_GSB` and HID `ACPI0009` or `ACPI000A`. The add handler skips already-tracked handles, evaluates `_GSB`, allocates state, skips hardware already registered, optionally enables and claims PCI BAR0, walks `_CRS` for a memory resource, inserts it into `iomem_resource`, selects PCI resource or `_CRS`, and calls `acpi_register_ioapic()`. Removal first releases PCI resources in `pci_ioapic_remove()`, then `acpi_ioapic_remove()` unregisters IOAPICs, releases inserted resources, removes list entries, and frees state.

State and persistence: tracked hotplug IOAPICs live in the global `ioapic_list` protected by `ioapic_list_lock`. The driver also owns inserted iomem resources and PCI device references for tracked entries.

Dependencies and integration: integrates ACPI namespace/resource evaluation, PCI device acquisition and resource management, global iomem resource insertion, and architecture ACPI IOAPIC registration callbacks.

Risks: error unwinding spans PCI enable/request, `_CRS` insertion, and IOAPIC registration. Duplicate detection is by ACPI handle and `acpi_ioapic_registered()`; mismatched firmware handles or GSI bases can cause skipped or duplicated registration. Remove ordering matters because IRQ users can keep IOAPICs busy, causing `-EBUSY`.

Test signals: test hot-add under PCI root, duplicate add, PCI BAR and pure `_CRS` resources, prefetch/disabled resource filtering, registration failure unwind, root removal with busy IOAPIC, and resource release after PCI disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/ioapic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/irq.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/irq.c

Purpose: `irq.c` is the ACPI GSI-to-Linux-IRQ mapping layer. It tracks the active ACPI IRQ model, maps and unmaps GSIs through irqdomains, parses IRQ resources from `_CRS`, exposes IRQ resource lookup to drivers, and creates child IRQ hierarchies for GIC systems.

Important APIs, types, and functions: exported APIs include `acpi_gsi_to_irq()`, `acpi_register_gsi()`, `acpi_unregister_gsi()`, `acpi_irq_get()`, `acpi_get_gsi_dispatcher()`, and `acpi_irq_create_hierarchy()`. Init-time setters are `acpi_set_irq_model()` and `acpi_set_gsi_to_irq_fallback()`. Internal parsing revolves around `struct acpi_irq_parse_one_ctx`, `acpi_irq_parse_one_cb()`, and `acpi_irq_parse_one()`.

Control flow: architecture setup calls `acpi_set_irq_model()` with a dispatcher returning the fwnode for a GSI. GSI registration builds an `irq_fwspec` with hardware GSI and trigger/polarity type, then creates an irqdomain mapping. `_CRS` lookup walks IRQ and Extended IRQ resources, skips producer Extended IRQs, counts through interrupt arrays by index, resolves resource-source fwnodes, fills Linux resource flags, and creates a mapping for the selected interrupt. Affinity lookup reuses the same parse path and asks irq core for fwspec affinity metadata.

State and persistence: global state is `acpi_irq_model`, the GSI-domain dispatcher, and an optional arch fallback from GSI to IRQ. IRQ mappings persist in the irqdomain core until unregistered or disposed.

Dependencies and integration: depends on ACPI resource descriptors, fwnode handles, irqdomain APIs, architecture interrupt-controller setup, and device resource consumers such as platform and GED drivers.

Risks: callers rely on dispatcher initialization before mapping; otherwise registration fails. Extended IRQ resource-source lookup can fail if firmware names are wrong. `acpi_unregister_gsi()` refuses to dispose GIC SGIs below 16 but other incorrect unmaps can still disrupt shared mappings. Missing irqdomains return `-EPROBE_DEFER` from `acpi_irq_get()`, so drivers need retry-safe probe paths.

Test signals: verify GSI mapping for IRQ and Extended IRQ resources, resource-source fwnode lookup, index handling across multi-interrupt resources, trigger/polarity/share/wake flags, fallback GSI mapping, GIC hierarchy creation, affinity extraction, and unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/mipi-disco-img.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/mipi-disco-img.c

Purpose: `mipi-disco-img.c` implements ACPI MIPI DisCo for Imaging support. It parses ACPI 6.5 `_CRS` CSI-2 serial-bus descriptors and MIPI imaging `_DSD` properties, then constructs Linux software-node graph endpoints compatible with the generic fwnode graph model used by V4L2.

Important APIs, types, and functions: exported internal ACPI helpers are `acpi_mipi_check_crs_csi2()`, `acpi_mipi_scan_crs_csi2()`, `acpi_mipi_init_crs_csi2_swnodes()`, `acpi_mipi_crs_csi2_cleanup()`, and x86-only `acpi_graph_ignore_port()`. Key structures are `struct crs_csi2_connection`, `struct crs_csi2`, and `struct csi2_resources_walk_data`. Core helpers parse resources, allocate software-node storage, connect local/remote endpoints, copy MIPI properties, and register node groups.

Control flow: during ACPI scan, `acpi_mipi_check_crs_csi2()` walks each device `_CRS`, collects CSI-2 descriptors, resolves remote handles, and attaches per-handle data. `acpi_mipi_scan_crs_csi2()` counts local and remote port needs, creates placeholder entries for remote endpoints lacking descriptors, allocates software-node arrays for every participant, then wires endpoint `remote-endpoint`, `bus-type`, and `reg` properties. After ACPI devices exist, `acpi_mipi_init_crs_csi2_swnodes()` fetches each `struct acpi_device`, derives device properties such as rotation, clock frequency, LED/flash limits, reads per-port MIPI lane properties from `_DSD`, registers software nodes, and attaches them as secondary fwnodes. Cleanup releases temporary entries and unattached software-node memory.

State and persistence: temporary scan state is kept in the global `acpi_mipi_crs_csi2_list` and per-handle attached data. Successfully registered software nodes are transferred to `adev->swnodes` and the ACPI fwnode secondary pointer; temporary ownership is cleared to avoid premature freeing.

Dependencies and integration: depends on ACPI resource parsing, ACPI per-handle data attachment, Linux software nodes, generic property/fwnode APIs, V4L2 fwnode bus type constants, ACPI scan locking, and x86 DMI/CPU matching for Dell broken graph quirks.

Risks: this is allocation- and firmware-data-heavy. Overflow checks protect software-node allocation, but malformed remote references, unsupported PHY types, missing port data nodes, and too many lane/frequency entries can silently omit graph details. The lifecycle is split across early scan, device enumeration, and cleanup, so ownership transfer bugs can leak or double-free. The Dell x86 quirk intentionally ignores some firmware graph nodes based on DMI and CPU generation.

Test signals: validate two-endpoint CSI-2 graph creation, remote placeholder devices, C-PHY and D-PHY bus types, lane and polarity property translation, link-frequency limits, `_PLD` rotation fallback, software-node registration failure, cleanup before and after ownership transfer, and Dell IPU/LNK port-ignore matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/mipi-disco-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/acpi/nfit/Kconfig

Purpose: this Kconfig file declares build options for the ACPI NFIT driver and its security debug mode. NFIT support discovers ACPI 6 NVDIMM Firmware Interface Tables and registers libnvdimm topology and platform/DIMM DSM access.

Important APIs, types, and functions: `config ACPI_NFIT` is a tristate option named "ACPI NVDIMM Firmware Interface Table (NFIT)" and selects `LIBNVDIMM`. It depends on `PHYS_ADDR_T_64BIT`, `BLK_DEV`, and `ARCH_HAS_PMEM_API`. `config NFIT_SECURITY_DEBUG` is a boolean gated by `ACPI_NFIT`.

Control flow: there is no runtime control flow; the file controls compilation. Selecting `ACPI_NFIT=m` builds a module named `nfit`. Enabling security debug changes debug visibility for NVDIMM security command payloads in the driver implementation.

State and persistence: Kconfig choices persist in kernel configuration and determine whether NFIT code is built in, modular, or absent.

Dependencies and integration: integrates ACPI NFIT with persistent memory architecture support, block device infrastructure, and libnvdimm. Security debug is intentionally opt-in because command payloads may contain sensitive clear-text material.

Risks: enabling security debug on non-development systems can expose sensitive material in logs. Missing dependency selections prevent NFIT from appearing even on ACPI systems with NVDIMMs.

Test signals: verify menu visibility under supported architectures, built-in and module builds, dependency exclusion when persistent-memory APIs are unavailable, and that `NFIT_SECURITY_DEBUG` only appears with `ACPI_NFIT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/Makefile -->
## sources/distributed-fs/ceph-client/drivers/acpi/nfit/Makefile

Purpose: this Makefile defines how the ACPI NFIT driver is built from its implementation objects.

Important APIs, types, and functions: the build target is `obj-$(CONFIG_ACPI_NFIT) := nfit.o`. The composite object always includes `core.o` and `intel.o`, and conditionally includes `mce.o` when `CONFIG_X86_MCE` is enabled.

Control flow: there is no runtime flow. Kbuild assembles `nfit.o` from the listed objects when `CONFIG_ACPI_NFIT` is enabled as built-in or module.

State and persistence: build composition is determined by kernel configuration. No runtime state is defined here.

Dependencies and integration: integrates NFIT core and Intel-specific support with optional x86 machine-check handling. It relies on the Kconfig option declared in the adjacent `Kconfig`.

Risks: object ordering is simple but meaningful for link inclusion. Conditional MCE support means x86 error-handling features are absent when `CONFIG_X86_MCE` is off, which tests must account for.

Test signals: verify built-in and module builds, `CONFIG_X86_MCE` on/off object composition, and that the resulting module name remains `nfit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/Makefile -->
