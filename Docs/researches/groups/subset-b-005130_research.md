# Research Report: subset-b-005130

This grouped report covers the requested Surface platform drivers, ACPI-WMI core and tests, and x86/Acer platform-driver files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_dtx.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_dtx.c

Purpose: Implements the Surface Book detachment-system driver for clipboard/tablet detach control. It exposes `/dev/surface/dtx` as a miscdevice so userspace can enable event delivery, request/confirm/cancel/heartbeat latch operations, lock or unlock the latch, and query base, latch, and device-mode state. It also reports tablet-mode state through an input switch.

Important APIs and types: SSAM requests `ssam_bas_latch_*`, `ssam_bas_get_base`, `ssam_bas_get_device_mode`, and `ssam_bas_get_latch_status` are the firmware interface. Main state lives in `struct sdtx_device`; open-file clients use `struct sdtx_client` with a per-client KFIFO, fasync pointer, and event-enabled flag. File operations are `surface_dtx_open`, `surface_dtx_release`, `surface_dtx_read`, `surface_dtx_poll`, `surface_dtx_fasync`, and `surface_dtx_ioctl`. Event and work handlers are `sdtx_notifier`, `sdtx_device_mode_workfn`, and `sdtx_device_state_workfn`.

Control flow: Probe binds to either ACPI `MSHW0133` or the SSAM BAS device, creates an `sdtx_device`, reads initial state, registers the tablet-mode input device, registers the SSAM notifier, and registers the miscdevice. IOCTLs take the device read lock, reject shutdown, then forward commands to SSAM or copy translated state to userspace. SSAM events validate payload size, update cached state under `write_lock`, push binary `sdtx_event` records to all clients with events enabled, wake poll/read waiters, and trigger delayed mode validation after base changes. Resume schedules a delayed full state refresh.

State and persistence: Cached base/device-mode/latch state is in memory only; hardware latch state persists in the Surface Aggregator firmware. Dirty bits coordinate full state queries with concurrent events. The client event queue is transient and can overrun. `kref`, rwsems, client list locking, delayed works, and shutdown flags manage object lifetime across open file descriptors and device removal.

Dependencies and integration points: Depends on Surface Aggregator controller/device/dtx UAPI headers, Linux miscdevice, input, kfifo, fasync, workqueue, platform, and optional SSAM bus support. Userspace consumers are expected to use the documented `surface/dtx` node and the Surface DTX ioctl/event ABI.

Risks: Detach control is safety-sensitive because userspace must coordinate dGPU/base use before confirming detach. Event buffer overrun drops notifications. `__sdtx_device_state_update_latch()` appears to build a base-connection event with `sizeof(struct sdtx_base_info)` instead of a latch-status event, which is a high-value review target. Shutdown/order bugs could expose stale controller pointers, although the locks are designed to prevent this. Firmware timing assumptions around delayed mode rechecks are empirical.

Test signals: Build with and without `CONFIG_SURFACE_AGGREGATOR_BUS`; probe on Surface Book 2/3; open/read/poll/fasync/ioctl tests against `/dev/surface/dtx`; detach request/confirm/cancel flows; base attach/detach event ordering; tablet-mode input events; suspend/resume state refresh; removal while clients block in read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_dtx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_gpe.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_gpe.c

Purpose: Creates a small DMI-driven platform device that enables lid wakeup on Intel-based Microsoft Surface systems whose ACPI lid wake path depends on a specific GPE number.

Important APIs and types: `dmi_lid_device_table` maps Surface models/SKUs to software-node `gpe` properties. `struct surface_lid_device` stores the selected GPE. `surface_lid_enable_wakeup()` wraps `acpi_set_gpe_wake_mask()`. Probe calls `acpi_mark_gpe_for_wake()`, `acpi_enable_gpe()`, and disables the wake mask until suspend.

Control flow: Module init finds the first DMI match, registers the `surface_gpe` platform driver, creates a software fwnode containing the GPE property, allocates a matching platform device, and adds it. Probe reads the property, allocates state, marks/enables the GPE, and leaves wake disabled while running. Suspend enables the GPE wake mask; resume disables it. Exit unregisters the platform device and driver and removes the software node.

State and persistence: Runtime state is just the GPE number in devres-managed memory plus the global platform-device pointer. The ACPI wake mark and enabled GPE are firmware/kernel ACPI state and are restored in remove by disabling wake and the GPE.

Dependencies and integration points: Uses ACPI GPE APIs, DMI matching, platform-device creation, and software fwnodes. The module alias is broad for Surface systems and the DMI table narrows actual binding.

Risks: GPE numbers are hard-coded from DSDT inspection, so firmware revisions or new SKUs can need table updates. A wrong GPE can break lid wake or enable unrelated wake sources. Failure after `acpi_enable_gpe()` is cleaned only on the final wake-disable error path, so new error paths must preserve cleanup.

Test signals: DMI autoload on listed Surface models; successful probe logs; `/proc/acpi/wakeup` or ACPI debug showing correct wake mask changes; lid-open wake from suspend; no wake enable on unsupported Surface/AMD variants; module unload disabling the GPE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_gpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_hotplug.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_hotplug.c

Purpose: Provides out-of-band hot-plug signaling for Surface Book dGPU/base hardware, especially when the PCIe device is in D3cold and cannot generate normal PCIe hot-plug events.

Important APIs and types: ACPI GPIO mappings expose base presence, device power, and device presence interrupt/status GPIOs. `_DSM` GUID `5515a847-ed55-4b27-8352-cd320e10360a` accepts per-IRQ notifications. `struct shps_device` stores per-IRQ mutexes, GPIO descriptors, and Linux IRQ numbers. Key functions are `shps_setup_irq()`, `shps_handle_irq()`, and `shps_dsm_notify_irq()`.

Control flow: Probe filters out ACPI `MSHW0153` instances that have no GPIOs, adds driver GPIO mappings, allocates state, initializes IRQ slots, and conditionally sets up each IRQ only if the corresponding DSM function exists. Each threaded IRQ identifies its type, reads the status GPIO, calls the DSM function with that value, and lets ACPI emit device-check notifications for downstream PCIe hotplug. Probe also sends initial DSM notifications for present IRQs to synchronize firmware state.

State and persistence: The driver keeps no persistent policy; it mirrors current GPIO states into ACPI via DSM calls. IRQ registrations and GPIO descriptors are devm-managed; remove disables active IRQs and destroys locks.

Dependencies and integration points: Integrates ACPI, GPIO descriptor mapping, IRQ threading, and platform-driver matching on `MSHW0153`. It is indirectly coupled to ACPI firmware and PCIe hotplug handling that consumes the resulting ACPI notifications.

Risks: DSM function numbering and `enum shps_irq_type` order must remain synchronized. GPIO mapping indexes are firmware-contract sensitive. `surface_hotplug_remove()` is called on partial probe failures, so initialization order of mutexes/IRQ sentinel values matters. Missing DSM functions are valid on Surface Book 3 and must not be treated as fatal.

Test signals: Probe on Surface Book 2/3; IRQ setup count matching DSM availability; attach/detach or dGPU power transitions causing DSM debug logs and PCIe hotplug rescans; no binding on Surface Laptop 3 `MSHW0153`; clean module unload with IRQs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_hotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_platform_profile.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_platform_profile.c

Purpose: Registers Linux platform-profile support for Surface devices through the Surface Aggregator thermal/fan subsystem, letting userspace select low-power, balanced, balanced-performance, or performance modes.

Important APIs and types: `enum ssam_tmp_profile` and `enum ssam_fan_profile` define firmware values. `struct ssam_tmp_profile_info` parses the TMP response. `struct ssam_platform_profile_device` stores the SSAM device, registered profile device, and `has_fan`. Core operations are `ssam_tmp_profile_get/set()`, `ssam_fan_profile_set()`, conversion helpers, and `ssam_platform_profile_get/set()`.

Control flow: The SSAM device driver matches `SSAM_SDEV(TMP, SAM, 0x00, 0x01)`. Probe allocates state, reads the optional `has_fan` property, and registers `platform_profile_ops`. The platform-profile core calls `probe` to advertise supported choices, `profile_get` to query TMP mode, and `profile_set` to set TMP mode and, when present, the FAN profile.

State and persistence: Driver state is devm-managed and minimal. Selected performance/fan profiles persist in EC/SSAM firmware until changed, reset, or power state transitions. No local cache is maintained, so reads always query firmware.

Dependencies and integration points: Depends on `linux/platform_profile.h`, Surface Aggregator SSAM device APIs, and firmware properties that indicate fan support. It integrates with userspace through the common platform-profile sysfs ABI.

Risks: TMP and FAN firmware profile numbering intentionally differs, so conversion helpers must not be merged casually. If TMP set succeeds and FAN set fails, profile state can become partially applied. Unknown firmware profile values return `-EINVAL` and may hide new modes until mapped.

Test signals: Probe on supported Surface devices; platform-profile sysfs shows four choices; set/get round trips for all modes; fan-equipped devices issue both TMP and FAN commands; non-fan devices do not attempt FAN writes; error injection for SSAM command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_platform_profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surfacepro3_button.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surfacepro3_button.c

Purpose: Handles nonstandard ACPI button notifications for Surface Pro 3/4 era devices using `MSHW0028` or selected `MSHW0040` nodes, reporting power, Windows/home, and volume keys through the input subsystem.

Important APIs and types: ACPI ids are `MSHW0028` and `MSHW0040`; valid object basename is `VGBI`. `surface_button_notify()` maps ACPI notify codes to `KEY_POWER`, `KEY_LEFTMETA`, `KEY_VOLUMEUP`, and `KEY_VOLUMEDOWN`. `surface_button_check_MSHW0040()` evaluates a DSM method to avoid binding newer incompatible `MSHW0040` devices.

Control flow: Platform probe verifies ACPI object name and DSM/platform revision, allocates `struct surface_button` and an input device, registers key capabilities, enables wakeup, and installs an ACPI device notify handler. Notifications report wakeup events on press while suspended, suppress normal input reports while suspended, and emit press/release events when active. PM callbacks toggle the `suspended` flag. Remove unregisters the handler, disables wake, unregisters input, and frees state.

State and persistence: Runtime state tracks the input device, phys string, and suspend flag. Wake capability is registered with the PM core. No event state persists beyond input reports.

Dependencies and integration points: Uses ACPI notify/DSM APIs, platform ACPI matching, input, and PM wakeup helpers. It complements generic `soc_button_array` for older Surface systems that do not follow the standard button-array model.

Risks: `MSHW0040` is shared by newer systems, so the DSM filter is essential to prevent duplicate or wrong drivers. The `pushed` field is unused. Tablet-mode notify `0xc8` is intentionally unsupported. Press events during suspend wake the device but are not replayed to input after resume.

Test signals: Probe only on `VGBI` companion nodes; input events for all four buttons; wake from suspended power-button press; no binding on MSHW0040 systems with nonzero OEM platform revision; handler removal under module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surfacepro3_button.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/Kconfig

Purpose: Defines the ACPI-WMI core Kconfig menu and test inclusion point. It gates the shared WMI bus/mapper used by vendor platform drivers.

Important APIs and types: `menuconfig ACPI_WMI` is a tristate depending on `ACPI && X86` and selecting `NLS`. `ACPI_WMI_LEGACY_DEVICE_NAMES` preserves old WMI device naming behavior. The file sources `drivers/platform/wmi/tests/Kconfig` under the `ACPI_WMI` menu.

Control flow: Kconfig selection controls whether `wmi.o` is built and whether WMI client drivers can depend on the core. The legacy naming option influences runtime device names through `wmi_dev_set_name()` in `core.c`.

State and persistence: No runtime state is present. The selected configuration persists in the kernel build and affects module availability, symbol exports, and WMI bus naming.

Dependencies and integration points: Integrates with platform/x86 vendor Kconfig entries that depend on `ACPI_WMI`. Selecting `NLS` supports WMI string conversion helpers.

Risks: The help text contains a typo, "Acer, Dell an HP". The legacy naming option can keep userspace compatibility but may cause duplicate-GUID registration conflicts in corner cases. Test Kconfig is only visible when the core is enabled.

Test signals: `CONFIG_ACPI_WMI=m/y` builds `drivers/platform/wmi/wmi.o`; disabling ACPI or X86 hides it; enabling legacy naming changes WMI device names; KUnit test options appear under the menu.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/Makefile

Purpose: Builds the ACPI-WMI core module and descends into the WMI KUnit test directory.

Important APIs and types: `wmi-y := core.o marshalling.o string.o` composes the module from the bus core, ACPI-object marshalling, and WMI string helpers. `obj-$(CONFIG_ACPI_WMI) += wmi.o` gates the module. `obj-y += tests/` lets test Makefiles decide what to build.

Control flow: Kbuild links the listed objects into `wmi.o` when ACPI-WMI is enabled, then evaluates the tests subdirectory independently.

State and persistence: No runtime state. The file defines build composition and object ordering.

Dependencies and integration points: Tied to `drivers/platform/wmi/Kconfig`, `tests/Makefile`, and public symbols used by WMI client drivers.

Risks: Omitting `marshalling.o` or `string.o` would break newer WMI buffer/string APIs. The tests subdirectory comment says `drivers/platform/x86/wmi/tests`, which is stale relative to this path.

Test signals: `make drivers/platform/wmi/` builds `core.o`, `marshalling.o`, `string.o`, and optional KUnit modules; `modinfo wmi` shows the core module metadata from `core.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/core.c

Purpose: Implements the ACPI-WMI mapper, WMI bus, WMI device creation from `_WDG`, legacy GUID-string helper APIs, newer `wmi_device` helper APIs, WMI event dispatch, sysfs attributes, module registration, and platform binding to ACPI mapper devices `PNP0C14`.

Important APIs and types: Firmware entries are parsed as packed `struct guid_block`; each becomes `struct wmi_block` containing `struct wmi_device`, ACPI companion, notify lock, legacy handler, readiness flag, and flags for duplicate GUIDs/read-with-no-args/no-event-data. Exported APIs include `wmi_instance_count`, `wmidev_instance_count`, `wmi_evaluate_method`, `wmidev_evaluate_method`, `wmidev_invoke_method`, `wmidev_invoke_procedure`, `wmi_query_block`, `wmidev_query_block`, `wmidev_set_block`, `wmi_install_notify_handler`, `wmi_remove_notify_handler`, `wmi_has_guid`, `wmi_get_acpi_device_uid`, `__wmi_driver_register`, and `wmi_driver_unregister`.

Control flow: `subsys_initcall_sync()` registers class, bus, and platform driver. Probe creates a child `wmi_bus-*` class device, installs an ACPI notify handler, evaluates `_WDG`, and registers one WMI bus device for each valid GUID block. `wmi_create_device()` classifies blocks as event/method/data, verifies required ACPI methods, detects duplicate GUIDs, assigns IDs/names, and initializes sysfs groups. Bus probe enables expensive/event devices, calls client probe, and only then marks the driver ready for notifications. ACPI notifications iterate child devices by notify id, evaluate `_WED` when available, dispatch to bound WMI drivers and legacy handlers under `notify_lock`, and emit netlink events.

State and persistence: Runtime WMI devices persist while the ACPI mapper platform device exists. Expensive data blocks and events are enabled/disabled around legacy access or during device lifetime. Driver readiness and handler pointers are protected by an rwsem. IDA IDs and device links manage identity and ordering. No firmware state is cached except parsed `_WDG` metadata.

Dependencies and integration points: Depends on ACPI evaluate/notify APIs, Linux driver core bus/class/device links, sysfs, IDA, GUID helpers, and local marshalling/string helpers. It is the substrate for `drivers/platform/x86/*-wmi.c` client drivers and legacy users of `wmi_*` GUID helpers.

Risks: ACPI firmware is inconsistent: missing enable methods, no-arg WQ methods, duplicated GUIDs, absent `_WED`, and malformed return objects all require defensive behavior. Legacy singleton drivers are blocked on duplicated GUIDs unless `no_singleton` is set. Some APIs return coarse `AE_ERROR`/`-EIO`, hiding detailed firmware failures. Event dispatch must keep `_WED` draining even without consumers to avoid firmware queues filling. Lifetime depends on correct `put_device()`/IDA cleanup on partial registration failures.

Test signals: Boot/probe on systems with `PNP0C14`; sysfs `modalias`, `guid`, `instance_count`, `expensive`, `notify_id`, `object_id`, and `setable`; module autoload via `MODALIAS=wmi:*`; duplicate-GUID behavior; WMI client probe/remove/shutdown; legacy helper compatibility; event delivery with and without `_WED`; KUnit coverage for marshalling used by `wmidev_*` APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/internal.h -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/internal.h

Purpose: Declares private helper interfaces shared by WMI core implementation files.

Important APIs and types: Forward declares `union acpi_object` and `struct wmi_buffer`. Declares `wmi_unmarshal_acpi_object()` for converting ACPI return objects into WMI byte buffers, and `wmi_marshal_string()` for converting a WMI UTF-16LE string buffer into an ACPI string buffer.

Control flow: No executable control flow. `core.c` calls these helpers for newer typed WMI APIs; `marshalling.c` implements them; KUnit tests include the header.

State and persistence: No state. The header defines internal ABI between compilation units.

Dependencies and integration points: Included by `core.c`, `marshalling.c`, and `tests/marshalling_kunit.c`. It avoids exposing these helpers as normal public kernel APIs while still allowing KUnit visibility exports.

Risks: Signature changes must be synchronized across core, implementation, and tests. Because the helpers allocate output buffers, callers must keep ownership/freeing contracts consistent.

Test signals: Compile coverage of `wmi.o` and `wmi_marshalling_kunit`; namespace import for KUnit-only exports; callers freeing returned buffer data with `kfree()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/marshalling.c -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/marshalling.c

Purpose: Converts ACPI WMI method/data/event return objects into packed WMI buffers and marshals WMI UTF-16LE string buffers into ACPI ASCII strings for firmware calls.

Important APIs and types: `wmi_unmarshal_acpi_object()` is exported for KUnit and used by `core.c`; it supports ACPI integer, string, buffer, and one-level package objects. `wmi_marshal_string()` converts `struct wmi_string` input to `struct acpi_buffer`. Internal helpers compute aligned output sizes and copy simple objects.

Control flow: Unmarshal first computes total output length, aligning integers to 4 bytes and strings to 2 bytes, rejects unsupported/nested object types, enforces `min_size`, allocates zeroed memory with 8-byte-safe allocation sizing when needed, and transforms each object. Integers are emitted as little-endian 32-bit values, strings as WMI UTF-16LE strings with length and NUL terminator, and buffers as raw bytes. Marshal validates the WMI string header and length, requires an even byte count, rejects non-ASCII code units, stops at the first NUL to avoid copying padding, and returns an allocated ACPI string.

State and persistence: Stateless except for allocated output buffers. Callers own `buffer->data` or `out->pointer` and must free them.

Dependencies and integration points: Uses ACPI object types, WMI buffer/string definitions, overflow-safe size helpers, alignment macros, unaligned little-endian helpers, and KUnit visibility. It is central to `wmidev_invoke_method`, `wmidev_query_block`, event `notify_new`, and string-backed WMI methods.

Risks: ACPI integers are intentionally truncated to 32 bits despite possible 64-bit DSDT integers. Only ASCII strings can be marshalled into ACPI strings. Package handling is one-level only; nested packages fail. Size arithmetic and string length limits are security-sensitive because firmware controls return object shape.

Test signals: `wmi_marshalling` KUnit suite covers integer/string/buffer/package transforms, alignment, min-size rejection, nested/unsupported object rejection, invalid WMI string rejection, padded strings, and 8-byte allocation alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/marshalling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/string.c -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/string.c

Purpose: Provides public WMI string conversion helpers between `struct wmi_string` UTF-16LE buffers and UTF-8 byte strings.

Important APIs and types: `wmi_string_to_utf8s()` converts a WMI string to a NUL-terminated UTF-8 destination. `wmi_string_from_utf8s()` converts UTF-8 source bytes into a NUL-terminated WMI string with a little-endian byte-length field.

Control flow: To-UTF8 computes input code-point count from the little-endian length field, requires destination capacity for at least a NUL byte, calls `utf16s_to_utf8s()`, and appends NUL. From-UTF8 requires at least one UTF-16 slot, calls `utf8s_to_utf16s()` leaving room for NUL, verifies the byte length fits in `u16`, writes length, and appends the UTF-16 NUL.

State and persistence: Stateless; callers provide all storage. Resulting WMI strings can be persisted only if a caller sends them to firmware or stores them.

Dependencies and integration points: Depends on NLS UTF conversion helpers, endian helpers, and public `linux/wmi.h`. `ACPI_WMI` selects `NLS` in Kconfig to satisfy this.

Risks: The helpers trust the source `struct wmi_string` storage to be large enough for its length field; callers must validate buffer bounds. Invalid UTF-16 is ignored by conversion behavior rather than surfaced as a hard failure in all cases. Destination truncation is possible by design when buffers are too small.

Test signals: `wmi_string` KUnit suite covers ASCII, non-ASCII BMP characters, surrogate pairs, padded/oversized WMI strings, truncation behavior, invalid UTF-16 handling, invalid UTF-8 rejection, and required NUL termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/Kconfig

Purpose: Adds KUnit configuration options for WMI marshalling and WMI string conversion tests.

Important APIs and types: `ACPI_WMI_MARSHALLING_KUNIT_TEST` and `ACPI_WMI_STRING_KUNIT_TEST` are tristate options depending on `KUNIT`, defaulting to `KUNIT_ALL_TESTS`, and hidden when all KUnit tests are enabled.

Control flow: When selected, the corresponding objects in `tests/Makefile` build and register KUnit suites at module/init time.

State and persistence: No runtime state. The file influences build/test configuration only.

Dependencies and integration points: Sourced from `drivers/platform/wmi/Kconfig` under `if ACPI_WMI`, so tests are tied to the WMI core menu. Help text points to kernel KUnit documentation.

Risks: Tests are unavailable if ACPI-WMI is disabled even though parts of the helper logic are mostly pure conversion code. Maintaining default `KUNIT_ALL_TESTS` keeps broad CI coverage but can increase build time.

Test signals: Enabling each config builds `wmi_marshalling_kunit` or `wmi_string_kunit`; KUnit output contains suites named `wmi_marshalling` and `wmi_string`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/Makefile

Purpose: Builds optional KUnit test modules for the WMI helper code.

Important APIs and types: `wmi_marshalling_kunit-y := marshalling_kunit.o` and `wmi_string_kunit-y := string_kunit.o` define test module objects. Config-gated `obj-*` entries add each module.

Control flow: Kbuild includes the test objects when their Kconfig symbols are enabled.

State and persistence: No runtime state. It is build metadata only.

Dependencies and integration points: Linked from the parent WMI Makefile via `obj-y += tests/`. The comment path is stale and says `drivers/platform/x86/wmi/tests`.

Risks: If the object names or config symbols drift from Kconfig, tests silently stop building. Test modules depend on internal helper visibility and namespace imports.

Test signals: `make ... CONFIG_ACPI_WMI_MARSHALLING_KUNIT_TEST=m CONFIG_ACPI_WMI_STRING_KUNIT_TEST=m` produces the two KUnit modules and their suites run under KUnit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/marshalling_kunit.c -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/marshalling_kunit.c

Purpose: KUnit suite validating ACPI-object to WMI-buffer unmarshalling and WMI-string to ACPI-string marshalling.

Important APIs and types: Parameter structures describe valid ACPI object cases, valid string cases, invalid ACPI object cases, and invalid string cases. Tests call `wmi_unmarshal_acpi_object()` and `wmi_marshal_string()` through `../internal.h`; `KUNIT_ARRAY_PARAM` supplies named cases.

Control flow: Valid unmarshal tests transform integer, string, buffer, simple package, and complex package objects and compare exact bytes plus 8-byte data alignment. Valid marshal tests convert normal and padded WMI strings and compare ACPI string length/content. Failure tests assert rejection of nested packages, reference/processor/power objects, empty/oversized/undersized/non-ASCII WMI strings, and undersized `min_size` results.

State and persistence: Test data is static. Allocated results are registered with KUnit cleanup actions or freed on failure. No persistent state leaves the suite.

Dependencies and integration points: Depends on KUnit, ACPI object definitions, WMI structures, KUnit resource cleanup, and the KUnit export namespace from `marshalling.c`.

Risks: The suite exercises exact layout, so it is sensitive to intentional ABI changes. It does not cover allocation failure or every ACPI object type. Test source includes one non-ASCII-free path only by rejecting a sample above 0x7f.

Test signals: Suite name `wmi_marshalling`; all parameter descriptions identify the failing conversion case; failures indicate regressions in alignment, length accounting, byte order, padding, or validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/marshalling_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/string_kunit.c -->
# sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/string_kunit.c

Purpose: KUnit suite validating public WMI UTF-16LE string conversion helpers.

Important APIs and types: Static `struct wmi_string` fixtures cover ASCII, special BMP characters, a surrogate-pair string, padded strings, oversized length fields, and invalid surrogate input. Tests call `wmi_string_to_utf8s()` and `wmi_string_from_utf8s()`.

Control flow: Parameterized round-trip tests convert WMI to UTF-8 and UTF-8 to WMI for representative strings. Focused tests ensure padded WMI strings stop at NUL, UTF-8 input with embedded NUL/padding converts to canonical WMI length, oversized WMI length does not over-read intended content, too-long UTF-8 input truncates to available WMI space, invalid UTF-16 is ignored into the expected output, and invalid UTF-8 returns `-EINVAL`.

State and persistence: Test fixtures are static. Output buffers are KUnit stack or KUnit-allocated memory. No state persists after the suite.

Dependencies and integration points: Depends on KUnit, WMI public string helpers, endian macros, and NLS conversion behavior.

Risks: The source uses non-ASCII literals and a surrogate-pair character, so compiler/source encoding must be correct. Tests encode current behavior for invalid UTF-16 being ignored; changing helper semantics to hard-fail would require test updates.

Test signals: Suite name `wmi_string`; failures identify UTF conversion, NUL termination, truncation, length-field, or invalid-input regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/string_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/Kconfig

Purpose: Defines the top-level x86 platform-device driver menu and a large set of vendor/platform driver build options, including the Acer drivers in this work item.

Important APIs and types: `menuconfig X86_PLATFORM_DEVICES` gates the submenu on `X86`. Local entries include `ACER_WIRELESS` and `ACER_WMI`; many vendor submenus are sourced for AMD, Dell, HP, Intel, Lenovo, Siemens, Tuxedo, Uniwill, and Android tablets. Several options select helper frameworks such as `INPUT_SPARSEKMAP`, `LEDS_CLASS`, `ACPI_PLATFORM_PROFILE`, `FW_ATTR_CLASS`, or hwmon/backlight/rfkill dependencies.

Control flow: Kconfig dependencies decide which platform drivers can be built. `ACER_WIRELESS` depends on ACPI and INPUT; `ACER_WMI` depends on backlight, i8042, input, optional rfkill/video, ACPI EC/WMI, and hwmon, and selects sparse keymap, LED class, and platform profile support.

State and persistence: No runtime state. Kernel `.config` selections persist build decisions and module availability.

Dependencies and integration points: Closely coupled to `drivers/platform/x86/Makefile` object entries and subsystem Kconfig symbols for ACPI, WMI, backlight, input, rfkill, hwmon, watchdog, GPIO, PCI, and vendor subdirectories.

Risks: This file is broad and dependency-sensitive; wrong dependencies can create link failures or expose drivers without required subsystems. `ACER_WMI` has many hard dependencies because the single driver can expose rfkill, backlight, LED, input, hwmon, and platform-profile features.

Test signals: Kconfig visibility for Acer and other platform drivers; allmodconfig/build coverage; dependency checks when toggling ACPI_WMI, RFKILL, ACPI_VIDEO, HWMON, and X86; generated modules matching Makefile object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/Makefile

Purpose: Maps x86 platform-driver Kconfig symbols to objects and subdirectories.

Important APIs and types: Acer entries build `acerhdf.o`, `acer-wireless.o`, and `acer-wmi.o`. The file also adds WMI drivers, vendor subdirectories, firmware attributes, platform-specific drivers, Intel helpers, and miscellaneous laptop drivers through `obj-*` assignments.

Control flow: Kbuild compiles each object or descends into subdirectories according to the resolved configuration. Object ordering matters for comments such as linking `toshiba_acpi` after WMI-related support.

State and persistence: Build metadata only; no runtime state.

Dependencies and integration points: Must stay synchronized with `drivers/platform/x86/Kconfig` symbols and actual source filenames. Subdirectory entries integrate vendor-specific Makefiles.

Risks: Stale object names or missing entries cause selected Kconfig options to produce no module or link failure. Because this directory has many subsystems, accidental ordering or unconditional `obj-y` changes can bloat builds.

Test signals: `make drivers/platform/x86/` with selected configs; module filenames match help text; `CONFIG_ACER_WIRELESS` builds `acer-wireless.o`; `CONFIG_ACER_WMI` builds `acer-wmi.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/acer-wireless.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/acer-wireless.c

Purpose: Minimal Acer airplane-mode hotkey driver that turns ACPI notifications from device `10251229` into `KEY_RFKILL` input events.

Important APIs and types: ACPI match table `acer_wireless_acpi_ids` binds HID `10251229`. `acer_wireless_notify()` handles ACPI device notifications. Probe creates a devm-managed input device named "Acer Wireless Radio Control" with `KEY_RFKILL`.

Control flow: Platform probe allocates/registers the input device and installs an ACPI notify handler. Notify accepts event `0x80`, emits a press and release of `KEY_RFKILL`, and logs unknown events. Remove unregisters the ACPI notify handler; devm handles input cleanup.

State and persistence: The input device pointer is stored as platform driver data. There is no rfkill state cache; the driver reports a hotkey event and leaves policy/action to input consumers.

Dependencies and integration points: Depends on ACPI platform enumeration and input subsystem. Uses PCI vendor ID constants only for input identity. Complements, rather than replaces, full Acer WMI/rfkill drivers.

Risks: Only event `0x80` is recognized; firmware variants with different event codes only log notices. It emits a key event without querying actual radio state, so userspace must decide how to toggle airplane mode. Handler installation after input registration means an install failure leaves probe failing cleanly via devm.

Test signals: ACPI modalias autoload for `10251229`; input device appears with `KEY_RFKILL`; pressing airplane hotkey emits one press/release pair; unknown events are logged; module unload removes notify handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/acer-wireless.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/acer-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/acer-wmi.c

Purpose: Large Acer/Wistron laptop extras driver exposing firmware controls for wireless/Bluetooth/WWAN rfkill, mail LED, vendor backlight, hotkeys, keyboard-dock tablet mode, accelerometer, Predator/Nitro gaming turbo/profile controls, fan/sensor hwmon, debugfs, and suspend/resume restoration.

Important APIs and types: GUIDs `AMW0_GUID1/2`, `WMID_GUID1/2/3/4`, and `ACERWMID_EVENT_GUID` select firmware interfaces. `struct wmi_interface` describes active interface type and capabilities; `struct quirk_entry` adds DMI-specific capabilities and EC behavior. Key helpers are `AMW0_get/set_u32`, `WMID_get/set_u32`, `wmid_v2_get/set_u32`, `WMI_gaming_execute_*`, rfkill/backlight/LED/hwmon/platform-profile operations, `acer_wmi_notify`, and `acer_wmi_init/exit`.

Control flow: Module init rejects blacklisted Aspire One systems, finds DMI quirks, detects the available AMW0/WMID/WMIDv2 interface via `wmi_has_guid()`, discovers capabilities from WMI blocks or SMBIOS type `0xAA`, applies quirks/forced caps, selects vendor backlight only when ACPI video says vendor backlight is appropriate, enables RF button and Launch Manager or EC raw mode, registers WMI event input handling and optional accelerometer, then creates an `acer-wmi` platform device. Platform probe registers mail LED, backlight, rfkill devices, platform profile, and hwmon depending on capabilities. WMI notifications update rfkill states, report sparse keymap events, update keyboard-dock tablet mode, read accelerometer values, and handle gaming turbo/profile keys.

State and persistence: Global `interface`, `quirks`, capability bits, module parameters, rfkill handles, input devices, platform device, debugfs root, supported sensor bitmap, and last non-turbo profile hold runtime state. Firmware settings for radio devices, LED, brightness, fan mode, fan speed, overclock, and platform profile persist in EC/WMI state. Suspend saves mail LED and brightness and restores them on resume; shutdown turns mail LED off.

Dependencies and integration points: Depends on ACPI/WMI legacy helpers, ACPI EC, i8042, sparse keymap, input, rfkill, backlight, LED class, platform-profile, hwmon, debugfs, DMI, and ACPI video backlight policy. It integrates with userspace through input, rfkill, backlight, LED, hwmon, platform-profile, and debugfs ABIs.

Risks: The driver is global-state-heavy and supports several incompatible firmware protocols; wrong interface or DMI quirk selection can expose unsafe controls. Many firmware calls accept/return loosely validated buffers or integers. `acer_platform_remove()` does not explicitly unregister hwmon/platform-profile devm resources because they are tied to the platform device, so cleanup ordering depends on device-managed semantics. `acer_wmi_exit()` calls `remove_debugfs()` unconditionally, but `interface` must have been initialized for successful module load. Fan/PWM writes directly affect thermals and must validate mode/speed mapping carefully.

Test signals: Build with `CONFIG_ACER_WMI`; probe on AMW0, WMID, and WMIDv2 machines; DMI quirk coverage for Nitro/Predator/Switch systems; rfkill state read/write and WMI event updates; hotkey sparse-keymap events; vendor backlight only under vendor policy; mail LED suspend/resume/shutdown behavior; keyboard dock SW_TABLET_MODE; Predator platform-profile get/set and turbo key; hwmon temp/fan/PWM reads/writes; debugfs `acer-wmi/devices`; unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/acer-wmi.c -->
