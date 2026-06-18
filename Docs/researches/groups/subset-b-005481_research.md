# subset-b-005481 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/message.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/message.c

## Purpose
Implements the USB core's synchronous message helpers, descriptor/string retrieval, scatter-gather transfer wrapper, endpoint/interface enablement, configuration switching, interface device lifetime, asynchronous driver-requested Set-Configuration, wireless status updates, and CDC functional descriptor parsing. It is a major bridge between exported USB driver APIs and lower-level URB/HCD machinery.

## Important APIs, Types, And Functions
The exported message APIs are `usb_control_msg()`, `usb_control_msg_send()`, `usb_control_msg_recv()`, `usb_interrupt_msg()`, `usb_bulk_msg()`, `usb_bulk_msg_killable()`, `usb_sg_init()`, `usb_sg_wait()`, `usb_sg_cancel()`, `usb_get_descriptor()`, `usb_string()`, `usb_cache_string()`, `usb_get_status()`, and `usb_clear_halt()`. Device and interface state APIs include `usb_reset_endpoint()`, `usb_set_interface()`, `usb_reset_configuration()`, `usb_set_configuration()`, `usb_driver_set_configuration()`, and `usb_set_wireless_status()`. Internal helpers include `usb_start_wait_urb()`, `sg_complete()`, `usb_get_langid()`, `usb_disable_device_endpoints()`, `find_iad()`, `driver_set_config_work()`, and `cancel_async_set_config()`. `struct api_context`, `struct set_config_request`, `struct usb_sg_request`, `struct usb_interface`, `struct usb_host_config`, and `struct usb_cdc_parsed_header` are central data structures.

## Control Flow
Synchronous control/bulk/interrupt helpers allocate/fill URBs, submit them through `usb_submit_urb()`, wait on a completion, kill the URB on timeout or signal, return status/length, and free the URB. Scatter-gather setup builds one URB for HCD SG support or one URB per scatterlist entry, then `usb_sg_wait()` submits queued URBs until completion, error, or cancellation. Descriptor helpers retry flaky devices, handle string language descriptor quirks, convert UTF-16LE strings to UTF-8, and cache strings in trimmed allocations.

Endpoint and interface transitions disable old endpoint queues before reassigning endpoint pointers. `usb_set_interface()` validates the requested altsetting, disables LPM under the HCD bandwidth mutex, asks the HCD to allocate bandwidth, sends SET_INTERFACE unless quirked, rolls back on failure, updates sysfs endpoint files, resets endpoint toggles, and optionally manually clears HALT for single-altsetting devices that stall. `usb_set_configuration()` preallocates new interface objects, resumes the device, tears down old bindings, cancels queued async config changes, allocates HCD bandwidth, initializes interface devices, sends SET_CONFIGURATION, updates device state/LPM/LTM, registers interfaces, and allows driver binding. Async configuration changes are queued to work items guarded by `set_config_lock`.

## State And Persistence
All state is in kernel memory. Key mutations include `udev->actconfig`, `udev->state`, endpoint pointer arrays `ep_in`/`ep_out`, interface `cur_altsetting`, interface `authorized` and `unregistering` flags, cached configuration/interface strings, `string_langid`/`have_langid`, LPM/LTM state, and queued `set_config_request` list entries. There is no filesystem persistence, but device and interface registration creates sysfs-visible state. Reference counts are carefully managed with `usb_get_dev()`, `usb_put_dev()`, `get_device()`, `put_device()`, and interface-cache `kref`.

## Dependencies And Integration Points
Depends on URB core APIs, HCD bandwidth and endpoint operations, runtime PM, ACPI/OF companion lookup, sysfs helpers in `sysfs.c`, endpoint device helpers, hub/LPM/LTM helpers, CDC descriptor definitions, and the driver core. It exports APIs used broadly by USB class/function drivers and participates in enumeration by creating `usb_interface` devices on `usb_bus_type`.

## Risks And Test Signals
High-risk areas are lifetime and locking during configuration replacement, bandwidth/LPM rollback paths, sync URB timeout handling, scatter-gather cancellation races, string descriptor quirks, partial receive semantics in `usb_control_msg_recv()`, endpoint sysfs recreation when altsettings change, and asynchronous config requests racing direct configuration changes. Test signals include enumeration/configuration switching across composite devices, altsetting changes under xHCI bandwidth checks, SG bulk error injection, timeout and signal behavior for sync I/O, malformed string descriptors, CDC descriptor duplication/malformed-length cases, sysfs endpoint file churn, KASAN/KCSAN/lockdep, and USB fault-injection against disconnect during blocking calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/notify.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/notify.c

## Purpose
Provides the USB core notifier chain used by other kernel components to observe USB bus and device add/remove events. It is a small event fan-out layer around Linux blocking notifier infrastructure.

## Important APIs, Types, And Functions
The public registration APIs are `usb_register_notify()` and `usb_unregister_notify()`, both exported GPL symbols taking a `struct notifier_block`. Internal event emitters are `usb_notify_add_device()`, `usb_notify_remove_device()`, `usb_notify_add_bus()`, and `usb_notify_remove_bus()`. The single persistent object is `usb_notifier_list`, declared with `BLOCKING_NOTIFIER_HEAD`.

## Control Flow
Observers register a notifier block into the blocking chain. USB core callers invoke the add/remove helpers with either `struct usb_device *` or `struct usb_bus *`; the helper calls `blocking_notifier_call_chain()` with event IDs such as `USB_DEVICE_ADD`, `USB_DEVICE_REMOVE`, `USB_BUS_ADD`, and `USB_BUS_REMOVE`.

## State And Persistence
State is limited to the notifier chain list in memory. The blocking notifier implementation owns synchronization for registration and callback dispatch. No event history is persisted, and callbacks receive live object pointers whose lifetime is controlled by the caller's surrounding USB core path.

## Dependencies And Integration Points
Depends on `<linux/notifier.h>`, USB event constants and object types, and the core `usb.h` declarations. It integrates with enumeration/removal paths elsewhere in usbcore and with consumers that need coarse USB topology notifications.

## Risks And Test Signals
Risks are mostly callback context and lifetime assumptions: notifier clients must not sleep or recurse into USB teardown in unsafe ways beyond what a blocking notifier context allows, and unregistering must be paired with prior registration. Test signals include registering multiple callbacks, verifying event order during bus/device add/remove, module unload with notifier unregister, and lockdep checks for callbacks that take USB locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/of.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/of.c

## Purpose
Implements Device Tree helpers for USB devices, interfaces, and hub ports. It maps USB topology concepts such as hub port numbers, connect type, combined device/interface nodes, and interface nodes onto OF child nodes and graph endpoints.

## Important APIs, Types, And Functions
Exported APIs are `usb_of_get_device_node()`, `usb_of_has_combined_node()`, `usb_of_get_connect_type()`, and `usb_of_get_interface_node()`. The internal `usb_of_has_devices_or_graph()` distinguishes hubs with explicit child or graph descriptions from hubs with no OF port modeling. It uses `struct device_node`, `struct usb_device`, `struct usb_device_descriptor`, `struct usb_config_descriptor`, and `enum usb_port_connect_type`.

## Control Flow
`usb_of_get_device_node()` scans hub child nodes for a one-cell `reg` equal to the one-based port number. `usb_of_has_combined_node()` returns true only when a device has an OF node, one configuration, one interface, and device class per-interface or hub. `usb_of_get_connect_type()` first checks whether the hub node has graph or child-port modeling; absent modeling yields `UNKNOWN`, while present modeling defaults unmentioned ports to `NOT_USED`. It treats an available graph remote endpoint as `HOT_PLUG` and an available child node with matching `reg` as `HARD_WIRED`. `usb_of_get_interface_node()` scans child nodes for a two-cell `reg` matching interface number and configuration value.

## State And Persistence
The helpers do not persist state. They return refcounted `device_node` pointers where documented, requiring callers to drop references. Their decisions become persistent only when callers store resulting OF nodes or connect types in USB device/interface/port objects.

## Dependencies And Integration Points
Depends on OF core and OF graph APIs. `message.c` uses combined-node and interface-node helpers while creating interface devices; `port.c` uses connect-type discovery when creating hub port devices. The results influence sysfs `connect_type`, interface firmware companion data, and whether disabled OF nodes suppress interface registration.

## Risks And Test Signals
Risks include refcount leaks on returned nodes, ambiguity when both graph endpoints and child nodes describe a port, inactive remote endpoints, malformed `reg` properties, and devices with descriptors that do not match firmware topology. Test signals include DT hubs with no port modeling, explicit hotplug connectors, hard-wired child devices, disabled child/remote nodes, combined-node one-interface devices, and multi-configuration/interface devices that must not reuse combined nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/offload.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/offload.c

## Purpose
Tracks active USB transfer offload users on a device tree so runtime power-management paths can detect when another entity is handling USB traffic and avoid unstable PM transitions.

## Important APIs, Types, And Functions
Exports `usb_offload_get()`, `usb_offload_put()`, `usb_offload_check()`, and `usb_offload_set_pm_locked()`. The relevant `struct usb_device` fields are `offload_usage`, `offload_pm_locked`, `offload_lock`, child topology, and the embedded `struct device` runtime PM state.

## Control Flow
`usb_offload_get()` takes a USB device reference, requires the runtime PM device to be active via `pm_runtime_get_if_active()`, checks `offload_pm_locked` under `offload_lock`, increments `offload_usage`, then drops runtime PM and USB references. `usb_offload_put()` follows the same active-device and lock checks, decrementing only if usage is nonzero. `usb_offload_check()` must be called with the device lock held; it returns true for local usage or recursively locks and checks child devices. `usb_offload_set_pm_locked()` flips the lock flag under the spinlock.

## State And Persistence
State is volatile per-device memory. `offload_usage` is a reference-style activity count, while `offload_pm_locked` freezes modifications during PM critical sections. There is no persistent storage or sysfs surface in this file.

## Dependencies And Integration Points
Depends on usbcore device references, hub child iteration, runtime PM, and spinlock/device-lock ordering. It integrates with PM code that must first mark a subtree locked, then call `usb_offload_check()` for a stable view of offload activity.

## Risks And Test Signals
Risks include usage leaks if get/put users are imbalanced, false negatives if callers fail to lock the full subtree before recursive checks, `-EBUSY` behavior for suspended devices, and deadlocks from inconsistent parent/child lock ordering. Test signals include get/put on active vs suspended devices, PM-locked rejection returning `-EAGAIN`, recursive child activity detection, concurrent offload toggling during suspend, and lockdep/KCSAN coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/otg_productlist.h -->
# sources/distributed-fs/ceph-client/drivers/usb/core/otg_productlist.h

## Purpose
Defines the OTG/embedded-host Targeted Peripheral List used to decide whether a connected USB device is supported by a constrained OTG host product.

## Important APIs, Types, And Functions
The file declares `productlist_table[]` of `struct usb_device_id` entries and defines `is_targeted(struct usb_device *dev)`. Entries are conditionally compiled for hubs, printers, CDC Ethernet gadgets, RNDIS gadgets, and USB test gadget zero. It also hard-codes OTG special cases for the HNP test device and OTG PET device.

## Control Flow
`is_targeted()` rejects the HNP test device, accepts the OTG PET device, then manually walks `productlist_table` because interface caches are not available at this point. It checks vendor, product, device revision range, device class, subclass, and protocol match flags. If no entry matches, it logs an unsupported device error and returns false.

## State And Persistence
The product list is static compile-time data. There is no runtime mutation or persistence. Build-time Kconfig options alter the accepted table.

## Dependencies And Integration Points
Depends on USB device ID matching macros and descriptor fields. It is intended to be included by OTG/embedded-host code rather than compiled as a standalone C file. Its result gates whether an OTG host accepts or rejects a peripheral.

## Risks And Test Signals
Risks include stale product policy, incorrect manual matching behavior versus `usb_match_id()`, build-option-dependent acceptance, and noisy rejection logging for products that should be supported. Test signals include matching each conditional entry, HNP/PET special-case behavior, revision-bound entries if added, and negative tests for unsupported devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/otg_productlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/phy.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/phy.c

## Purpose
Wraps one or more generic PHYs associated with a USB root hub and fans out initialization, mode, calibration, connect/disconnect notification, power, suspend, and resume operations. It lets host-controller code keep several PHYs in a consistent lifecycle state.

## Important APIs, Types, And Functions
The private `struct usb_phy_roothub` is both the list head and per-PHY list entry, containing a `struct phy *` and `list_head`. Exported APIs are `usb_phy_roothub_alloc()`, `usb_phy_roothub_alloc_usb3_phy()`, `usb_phy_roothub_init()`, `usb_phy_roothub_exit()`, `usb_phy_roothub_set_mode()`, `usb_phy_roothub_calibrate()`, `usb_phy_roothub_notify_connect()`, `usb_phy_roothub_notify_disconnect()`, `usb_phy_roothub_power_on()`, `usb_phy_roothub_power_off()`, `usb_phy_roothub_suspend()`, and `usb_phy_roothub_resume()`.

## Control Flow
Allocation is skipped when `CONFIG_GENERIC_PHY` is disabled or no `phys` phandles exist. `usb_phy_roothub_alloc()` prefers a named `usb2-phy`; if present it returns a roothub with that PHY, otherwise it adds all PHYs by index. `usb_phy_roothub_alloc_usb3_phy()` only allocates a separate USB3 PHY wrapper when `usb2-phy` is present, avoiding duplicate ownership when the primary wrapper already took all PHYs. Lifecycle methods iterate the list and call matching generic PHY operations. Init and power-on roll back already-processed entries in reverse order on failure. Suspend powers off PHYs and exits them only if the controller cannot wake the system; resume re-inits when needed, powers on, and rolls back init on power failure.

## State And Persistence
PHY wrapper state is devm-managed memory attached to the controller device. It stores only the list of PHY handles; actual PHY hardware state lives in PHY providers. There is no filesystem persistence.

## Dependencies And Integration Points
Depends on OF `phys`/`phy-names`, generic PHY APIs, device wakeup policy, and host-controller probe/suspend/resume paths. It is a service layer for HCD drivers that need to operate root-hub PHYs as a unit.

## Risks And Test Signals
Risks include double-claiming PHYs when naming conventions are wrong, partial rollback correctness, differing wakeup requirements across controllers, error propagation from one PHY blocking later PHYs, and ordering-sensitive power-off. Test signals include DT with named usb2/usb3 PHYs, indexed PHY fallback, init/power failure injection verifying reverse rollback, system suspend with wakeup enabled and disabled, and connect/disconnect notification propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/phy.h -->
# sources/distributed-fs/ceph-client/drivers/usb/core/phy.h

## Purpose
Declares the USB root-hub generic PHY wrapper interface implemented by `phy.c` for use by USB host-controller/core code.

## Important APIs, Types, And Functions
Forward-declares `struct device` and opaque `struct usb_phy_roothub`. Prototypes cover allocation for all/root USB2 PHYs and separate USB3 PHYs, lifecycle (`init`, `exit`), mode and calibration, port connect/disconnect notifications, power on/off, and controller-aware suspend/resume. The header uses `enum phy_mode` in a prototype but relies on included context for the enum declaration.

## Control Flow
This header has no runtime control flow. It establishes the callable contract: users allocate a roothub wrapper, initialize it, set mode/calibrate as needed, power it on, notify connect/disconnect events, and pair suspend/resume and exit/power-off operations according to HCD lifecycle.

## State And Persistence
The header exposes only an opaque pointer, intentionally hiding list layout and per-PHY state. Persistence and ownership are controlled by the implementation's devm allocation and generic PHY providers.

## Dependencies And Integration Points
Integrated by host-controller code and `phy.c`. It forms the compile-time boundary between USB core users and the generic PHY subsystem fan-out implementation.

## Risks And Test Signals
Risks are ABI/API drift with `phy.c`, missing enum visibility if included without generic PHY declarations, and misuse of lifecycle ordering by callers. Test signals are compile coverage across configurations with and without `CONFIG_GENERIC_PHY`, and HCD suspend/resume paths that exercise every declared method.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/port.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/port.c

## Purpose
Implements the `usb_port` device model for hub downstream ports, including sysfs attributes, port power control, runtime PM, USB2/USB3 peer-port linking, Type-C connector component binding, and port device create/remove lifecycle.

## Important APIs, Types, And Functions
External entry points are `usb_hub_create_port_device()` and `usb_hub_remove_port_device()`. Important internal functions include sysfs handlers for `disable`, `early_stop`, `location`, `connect_type`, `state`, `over_current_count`, `quirks`, and `usb3_lpm_permit`; runtime PM callbacks `usb_port_runtime_suspend()` and `usb_port_runtime_resume()`; peer helpers `link_peers()`, `unlink_peers()`, `find_and_link_peer()`, and `match_location()`; connector component callbacks `connector_bind()` and `connector_unbind()`. Main state is in `struct usb_port`, `struct usb_hub`, `struct usb_device`, PM QoS request storage, and optional Type-C connector handle.

## Control Flow
Port creation allocates `usb_port` plus PM QoS request, derives OF connect type, stores it in the hub's port array, sets default power bits, configures sysfs groups including SuperSpeed LPM policy attributes, registers the device, obtains the `state` kernfs node, installs a default no-power-off PM QoS request, adds Type-C component matching, links peer ports, enables runtime PM, and optionally exposes PM QoS flags when hub or ACPI can power-manage the port. Removal unlinks peers, removes component binding, drops the sysfs node reference, and unregisters the device.

The `disable` attribute breaks sysfs active protection before taking the hub device lock, optionally disconnects a child, toggles hub port power, waits the power-good delay, and clears change bits. Runtime suspend checks hub reset state, PM QoS no-power-off policy, global peer-link failure block, then turns port power off and queues peer PM changes. Runtime resume powers the peer SuperSpeed side before USB2 when needed, powers on the port, debounces reconnect, may request warm reset recovery, and wakes the child device for revalidation.

## State And Persistence
Port state is kernel memory exposed through sysfs. Mutated fields include `child`, `peer`, `connector`, `connect_type`, `location`, `state`, `over_current_count`, `quirks`, USB3 LPM permit bits, `early_stop`, PM QoS request, runtime PM usage, and hub bitmaps such as `power_bits`, `warm_reset_bits`, and `child_usage_bits`. Peer links and connector links are sysfs links, not persistent storage.

## Dependencies And Integration Points
Depends on hub control helpers, runtime PM, PM QoS, sysfs/kernfs, Type-C component framework, OF connect-type discovery, ACPI power manageability, HCD shared-HCD topology, and USB LPM helpers. It integrates with hub configuration/removal and user-space power policy through sysfs.

## Risks And Test Signals
High-risk areas include deadlocks between sysfs active protection and device unregister, peer-link races with runtime suspend/resume, global `usb_port_block_power_off` fallback after peer failures, child disconnect while toggling power, ACPI/OF mismatches in connect type or location, PM QoS ownership transfer, and Type-C attach notifications when a child already exists. Test signals include hub port sysfs reads/writes during unregister, USB2/USB3 peer pairing by location and default topology, runtime suspend/resume with connected devices, disabled port behavior, SuperSpeed LPM permit updates, Type-C connector binding, and lockdep/PM runtime traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/quirks.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/quirks.c

## Purpose
Maintains USB device, interface, endpoint-ignore, and platform-specific quirk detection. It combines static device ID tables with a runtime module parameter so usbcore can adjust enumeration, power management, descriptors, endpoint parsing, reset behavior, and LPM decisions for known-broken devices.

## Important APIs, Types, And Functions
The dynamic parameter is `quirks=` implemented by `quirks_param_set()` with `device_param_cb()`. Static tables include `usb_quirk_list`, `usb_interface_quirk_list`, `usb_amd_resume_quirk_list`, and `usb_endpoint_ignore`. Exported/internal detection APIs are `usb_endpoint_is_ignored()`, `usb_detect_quirks()`, `usb_detect_interface_quirks()`, and `usb_release_quirk_list()`. Helper functions include `usb_match_any_interface()`, `usb_amd_resume_quirk()`, `usb_detect_static_quirks()`, and `usb_detect_dynamic_quirks()`. The private `struct quirk_entry` stores VID/PID/flags for the runtime list.

## Control Flow
Writing `quirks=` parses comma-separated `VID:PID:flags` entries, reallocates `quirk_list` under `quirk_mutex`, and maps flag characters to `USB_QUIRK_*` bits. Static quirk detection walks ordered USB ID tables, matching device fields and optionally any interface's first altsetting. AMD resume quirks apply only for level-1 devices on HCDs marked with the AMD resume bug. Dynamic quirks are XORed with static quirks, allowing runtime toggling of bits. Endpoint-ignore matching checks device, interface, and endpoint address when a device has `USB_QUIRK_ENDPOINT_IGNORE`.

## State And Persistence
Static quirk tables are compile-time data. Dynamic state is the in-memory `quirk_list`, `quirk_count`, and copied `quirks_param` string, protected by `quirk_mutex`. Detected result bits persist for the lifetime of each `usb_device` in `udev->quirks`; `usb_detect_quirks()` may also initialize `persist_enabled`.

## Dependencies And Integration Points
Depends on USB matching helpers, module parameter infrastructure, HCD flags, descriptor parsing, and USB persist configuration. Quirk bits are consumed by enumeration (`message.c` string/config/interface handling), hub reset/LPM code, descriptor parsing, endpoint ignore logic, and sysfs visibility of quirk state.

## Risks And Test Signals
Risks include dynamic XOR semantics surprising users, malformed parameter parsing truncating the parsed list, stale static entries, incorrect interface matching before all altsettings are considered, endpoint-ignore overreach, and persist policy side effects. Test signals include parameter parsing for every flag letter, clearing the list with an empty string, static plus dynamic quirk combination, AMD root-port mouse cases, endpoint-ignore descriptor parsing, and enumeration behavior for devices using string, LPM, reset, BOS, or SetInterface quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/sysfs.c

## Purpose
Defines sysfs attributes and binary attributes for USB devices, root hubs, interfaces, interface association descriptors, wireless status, power-management controls, authorization controls, and raw descriptor exposure.

## Important APIs, Types, And Functions
Exported-to-core functions are `usb_create_sysfs_dev_files()`, `usb_remove_sysfs_dev_files()`, `usb_update_wireless_status_attr()`, `usb_create_sysfs_intf_files()`, and `usb_remove_sysfs_intf_files()`. Global attribute group arrays are `usb_device_groups[]` and `usb_interface_groups[]`. Major attributes include configuration fields, descriptor fields, product/manufacturer/serial, speed/lanes/path/version, quirks, avoid-reset quirk, authorization, remove, LTM capability, runtime PM `power/*` controls, persist, USB2/USB3 LPM status and tuning, root-hub authorization defaults, IAD fields, interface modalias, supports_autosuspend, interface authorization, and wireless status. Binary attributes expose raw configuration descriptors and BOS descriptors.

## Control Flow
Most show handlers format fields from `struct usb_device` or `struct usb_interface`; mutable handlers parse text, lock devices where required, and call core operations such as `usb_set_configuration()`, `usb_authorize_device()`, `usb_deauthorize_device()`, `usb_remove_device()`, `usb_enable_autosuspend()`, `usb_disable_autosuspend()`, USB2 LPM helpers, and interface authorization helpers. Power and persist attributes are merged into the `power` group after device creation. Root hubs receive authorization default attributes. Device string and BOS binary groups use visibility callbacks to hide missing data. Interface sysfs file creation optionally fetches/caches the interface string and creates the `interface` file; removal deletes it. Wireless status updates refresh the group, notify sysfs, and emit a uevent.

## State And Persistence
Sysfs files reflect live kernel memory, not durable storage. Writes mutate `udev->actconfig`, `udev->quirks`, `persist_enabled`, runtime autosuspend delay, `usb2_hw_lpm_allowed`, L1 timeout/BESL, HCD authorization policy flags, interface `authorized`, and related PM state. Binary descriptor files read from `udev->descriptor`, `rawdescriptors`, config descriptors, and optional BOS memory.

## Dependencies And Integration Points
Depends on USB device/interface locking, runtime PM, sysfs groups and binary attributes, OF `devspec`, HCD authorization flags, LPM helpers, descriptor caches, and configuration/message APIs. It is the primary user-space management surface for usbcore.

## Risks And Test Signals
High-risk areas include lock ordering for sysfs writes that call into device removal/configuration, hiding attributes correctly when optional data is absent, deprecated `power/level` compatibility, raw descriptor offset/count arithmetic, LPM tuning without full locking for simple fields, interface deauthorization during unregister, and root-hub policy propagation. Test signals include sysfs attribute presence by speed/capability/root-hub status, concurrent reads/writes during disconnect, configuration changes through `bConfigurationValue`, safe remove, authorization toggles, descriptor binary reads with offsets, PM attribute behavior, wireless status uevents, and lockdep/KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/trace.c

## Purpose
Instantiates usbcore tracepoints declared in `trace.h` by defining `CREATE_TRACE_POINTS` and including the trace header.

## Important APIs, Types, And Functions
There are no runtime functions in this file. Its important symbol-level effect is generating tracepoint definitions for events declared in `trace.h`, currently `usb_set_device_state` and `usb_alloc_dev` from the `usb_core_log_usb_device` event class.

## Control Flow
At compile time, the tracepoint macros expand into storage and registration metadata. Runtime control flow occurs in call sites elsewhere that invoke the generated trace events.

## State And Persistence
Tracepoint state is managed by the kernel tracing subsystem. This file does not maintain local state or persistence.

## Dependencies And Integration Points
Depends on `trace.h` and Linux tracepoint infrastructure. It must be compiled exactly once for the declared usbcore trace events.

## Risks And Test Signals
Risks are build/link issues if tracepoints are instantiated more than once or not at all. Test signals include successful usbcore build with tracing enabled, visible events under tracing facilities, and event activation while device allocation/state changes occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/core/trace.h

## Purpose
Declares usbcore trace events for logging key `struct usb_device` state snapshots during device allocation and state transitions.

## Important APIs, Types, And Functions
Defines trace system `usbcore`, event class `usb_core_log_usb_device`, and events `usb_set_device_state` and `usb_alloc_dev`. The event captures device name, `enum usb_device_speed`, `enum usb_device_state`, `bus_mA`, and authorization state, and prints speed/state strings using usbcore formatting helpers.

## Control Flow
Call sites pass a `struct usb_device *` to the trace event. `TP_fast_assign` copies fields from the live device into the ring buffer, and `TP_printk` formats them for trace readers. The include tail sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` before including `<trace/define_trace.h>`.

## State And Persistence
The header does not store state itself. Captured event records live in tracing buffers according to ftrace/perf configuration.

## Dependencies And Integration Points
Depends on Linux tracepoint macros, USB type definitions, `dev_name()`, `usb_speed_string()`, and `usb_state_string()`. `trace.c` instantiates the declarations; usbcore state-management code can include and call the generated trace hooks.

## Risks And Test Signals
Risks include trace header include-path mistakes, stale field types if `struct usb_device` changes, dereferencing devices outside valid lifetime at call sites, and trace format changes affecting tools. Test signals include compiling with `TRACE_HEADER_MULTI_READ`, enabling both events, and confirming output during device allocation and state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/urb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/urb.c

## Purpose
Implements USB Request Block allocation, reference counting, anchoring, validation, submission, cancellation, poisoning, and wait helpers. It is the central policy layer between USB drivers and HCD transfer queues.

## Important APIs, Types, And Functions
URB lifetime APIs are `usb_init_urb()`, `usb_alloc_urb()`, `usb_free_urb()`, and `usb_get_urb()`. Anchor APIs include `usb_anchor_urb()`, `usb_unanchor_urb()`, `usb_kill_anchored_urbs()`, `usb_poison_anchored_urbs()`, `usb_unpoison_anchored_urbs()`, `usb_anchor_suspend_wakeups()`, `usb_anchor_resume_wakeups()`, `usb_wait_anchor_empty_timeout()`, `usb_get_from_anchor()`, `usb_scuttle_anchored_urbs()`, and `usb_anchor_empty()`. Transfer APIs include `usb_pipe_type_check()`, `usb_urb_ep_type_check()`, `usb_submit_urb()`, `usb_unlink_urb()`, `usb_kill_urb()`, `usb_poison_urb()`, `usb_unpoison_urb()`, and `usb_block_urb()`.

## Control Flow
Allocation creates flexible URBs with optional isochronous frame descriptors and initializes krefs/lists. Submission validates the URB, rejects active or disconnected devices, resolves the endpoint from the pipe, checks control setup direction/length, clears internal transfer flags, records direction, calls KMSAN handling, rejects non-control transfers before configuration, validates max packet and isochronous packet sizes including SuperSpeed/SuperSpeedPlus/eUSB2 rules, checks SG segment alignment, clamps/validates transfer length, warns about pipe type and illegal flags, normalizes periodic intervals, then delegates to `usb_hcd_submit_urb()`.

Unlinking delegates asynchronously to the HCD with `-ECONNRESET`. `usb_kill_urb()` and `usb_poison_urb()` increment `reject`, use memory barriers to block resubmission, unlink with `-ENOENT`, and wait for `use_count` to drop. Anchors hold references to grouped URBs; kill/poison helpers repeatedly take a reference to the newest anchored URB, kill or poison it outside the anchor lock, and loop until the list is empty and wakeups are no longer suspended.

## State And Persistence
All state is memory-only. URBs carry krefs, transfer buffers, endpoint pointers, status, actual length, flags, interval, reject count, use count, and anchor linkage. Anchors maintain a spinlocked list, poison state, wait queue, and suspended wakeup count. There is no persistent storage.

## Dependencies And Integration Points
Depends on HCD submit/unlink/giveback APIs, endpoint descriptors, USB pipe macros, scatterlist, KMSAN, wait queues, krefs, atomics, and memory barriers. It is used by virtually every USB class driver and by synchronous wrappers in `message.c`.

## Risks And Test Signals
High-risk areas include URB lifetime during completion, resubmission races with kill/poison, anchor wakeup suppression, illegal flag sanitization that warns but still masks, periodic interval normalization, isochronous packet size calculations, SG alignment constraints, and control setup/pipe direction mismatches. Test signals include invalid URB submissions, disconnect during active URBs, completion handlers that resubmit while kill/poison runs, anchor empty waits, isochronous boundary cases across speeds, SG bulk submissions, KMSAN/sanitizer runs, and HCD fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/urb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/usb-acpi.c

## Purpose
Provides USB-to-ACPI glue for port power resources, port LPM capability quirks, USB4 tunneled-device PM links, firmware-derived port connect type/location, and ACPI companion discovery for USB devices and port devices.

## Important APIs, Types, And Functions
Exported APIs are `usb_acpi_power_manageable()`, `usb_acpi_port_lpm_incapable()`, and `usb_acpi_set_power_state()`. Bus registration APIs are `usb_acpi_register()` and `usb_acpi_unregister()`. Internal helpers include `usb_acpi_add_usb4_devlink()`, `usb_acpi_get_connect_type()`, `usb_acpi_get_companion_for_port()`, `usb_acpi_find_companion_for_port()`, `usb_acpi_find_companion_for_device()`, `usb_acpi_find_companion()`, and `usb_acpi_bus_match()`.

## Control Flow
Power-manageability and power-state setters find a hub port ACPI handle and call ACPI power-resource APIs. `usb_acpi_port_lpm_incapable()` parses the USB controller DSM UUID, checks function 5 availability on the port, evaluates it as an integer, and returns `1` when U1/U2 should be disabled. USB4 devlink setup applies only to tunneled SuperSpeed devices connected to a root hub; it reads the port fwnode `usb4-host-interface` reference and creates a runtime-PM device link from the USB child to the NHI device. Companion discovery maps root hubs via the HCD firmware device, maps ports by raw root port or parent port ACPI handle, derives connect type and location from `_UPC` and `_PLD`, and maps embedded devices to their port companion.

## State And Persistence
The file mutates `port_dev->connect_type`, `port_dev->location`, and `udev->usb4_link`. ACPI power state is external firmware/platform state. There is no local persistent storage.

## Dependencies And Integration Points
Depends on ACPI core, PCI/HCD raw port numbering, USB hub/port structures, firmware node references, device links, runtime PM flags, and USB link tunnel mode. It integrates with port creation, hub power control, LPM policy, and driver-core companion matching through `struct acpi_bus_type`.

## Risks And Test Signals
Risks include incorrect root-port numbering, missing or malformed `_UPC`/`_PLD`, DSM return type/value ambiguity, USB4 device-link lifetime, hard-wired device companion sharing, and unhandled per-interface ACPI function companions. Test signals include ACPI platforms with visible/connectable, hidden/connectable, and unused ports; ports with power resources; DSM LPM-disable cases; USB4 tunneled device suspend/resume ordering; root hub and nested hub companion lookup; and device removal with `udev->usb4_link`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb-acpi.c -->
