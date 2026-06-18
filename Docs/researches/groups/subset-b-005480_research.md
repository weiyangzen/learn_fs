# subset-b-005480 Research

Grouped source research for USB core hub handling under `sources/distributed-fs/ceph-client/drivers/usb/core`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/hub.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/hub.c

## Purpose

`hub.c` is the central Linux USB hub driver and USB device-enumeration engine. It binds USB hub interfaces, configures hub descriptors and interrupt status URBs, creates per-port devices, handles port-change events, powers and resets ports, enumerates newly attached devices, disconnects removed devices, implements device reset/re-enumeration, and coordinates runtime/system power management for hub trees. It also exports helper APIs used by host controller drivers, usbfs, PM code, and USB class/device drivers.

## Important APIs, Types, and Functions

The file is built around `struct usb_hub` and `struct usb_port` from `hub.h`. Public and exported entry points include `usb_hub_to_struct_hub()`, `usb_hub_set_port_power()`, `usb_hub_clear_tt_buffer()`, `usb_remove_device()`, `usb_set_device_state()`, `usb_new_device()`, `usb_deauthorize_device()`, `usb_authorize_device()`, `usb_port_suspend()`, `usb_port_resume()`, `usb_remote_wakeup()`, `usb_root_hub_lost_power()`, `usb_disable_lpm()`, `usb_enable_lpm()`, `usb_unlocked_disable_lpm()`, `usb_unlocked_enable_lpm()`, `usb_disable_ltm()`, `usb_enable_ltm()`, `usb_port_disable()`, `hub_port_debounce()`, `usb_ep0_reinit()`, `usb_reset_device()`, `usb_queue_reset_device()`, `usb_hub_find_child()`, `usb_hub_adjust_deviceremovable()`, and, under ACPI, `usb_get_hub_port_acpi_handle()`.

Major internal routines are `hub_probe()`, `hub_configure()`, `hub_activate()`, `hub_quiesce()`, `hub_irq()`, `hub_event()`, `port_event()`, `hub_port_connect_change()`, `hub_port_connect()`, `hub_port_init()`, `hub_port_reset()`, `hub_port_wait_reset()`, `usb_reset_and_verify_device()`, `descriptors_changed()`, LPM helpers such as `usb_set_lpm_parameters()`, `usb_req_set_sel()`, `usb_enable_link_state()`, and PM helpers such as `hub_suspend()`, `hub_resume()`, `hub_reset_resume()`, `check_port_resume_type()`, and `finish_port_resume()`. The driver table `hub_driver` binds `USB_CLASS_HUB` devices and selected quirk IDs for SMSC, Cypress, Genesys Logic, Texas Instruments, and Microchip hubs.

## Control Flow

Initialization enters through `usb_hub_init()`, which registers `hub_driver` and allocates the freezable per-CPU `usb_hub_wq`. `hub_probe()` validates that the hub has one configuration/interface and one interrupt-IN endpoint, enables autosuspend where possible, applies quirk flags, allocates a `struct usb_hub`, stores it in interface data, and calls `hub_configure()`. `hub_configure()` reads the hub descriptor, validates port count, computes SuperSpeed delay data, initializes TT clearing state, records power-budget and indicator capabilities, allocates the interrupt URB, creates `usb_port` children, updates the HCD's hub representation, adjusts DeviceRemovable with platform port data, and starts `hub_activate(HUB_INIT)`.

`hub_activate()` powers ports, optionally delays initial power-good and debounce work through `init_work`, clears stale change bits, marks ports needing attention, submits the hub interrupt URB, and schedules `hub_event()`. `hub_irq()` decodes the interrupt bitmap into `event_bits`, tracks repeated interrupt errors, and kicks the workqueue. `hub_event()` locks and autoresumes the hub, resets the hub after repeated interrupt errors, then iterates ports whose `event_bits`, `change_bits`, or `wakeup_bits` are set. For each port it takes the port runtime-PM reference, waits for pending PM work, locks `status_lock`, and calls `port_event()`.

`port_event()` reads and clears hardware change bits, reports over-current events, handles remote wakeup and USB3 warm-reset recovery, and dispatches logical or physical connect changes to `hub_port_connect_change()`. `hub_port_connect_change()` either revalidates an existing enabled connection by comparing descriptors or calls `hub_port_connect()`. `hub_port_connect()` disconnects any old child, debounces, checks removed/powered status, then retries enumeration: allocate `usb_device`, choose a device number, reset and address via `hub_port_init()`, reject unsupported bus-powered hub chains, publish `port_dev->child`, call `usb_new_device()`, and update PHY/power-budget signals. Failed attempts release address/HCD state, may power-cycle the port halfway through, and finally disable the port.

Reset paths reuse the same machinery. `usb_reset_device()` notifies or unbinds interface drivers, locks the port, invokes `usb_reset_and_verify_device()`, restores interfaces, and rebinds where needed. `usb_reset_and_verify_device()` resets/re-addresses through `hub_port_init()`, compares device/BOS/configuration/serial descriptors with `descriptors_changed()`, restores the prior configuration and alternate settings, then re-enables LTM/LPM. Descriptor or restoration mismatch triggers `hub_port_logical_disconnect()` so the device is rediscovered.

## State and Persistence Behavior

Runtime state is in-memory only. Hub-level state includes the interrupt URB, status buffers, descriptor, TT clearing queue, event/change/removed/wakeup/power/child-usage/warm-reset bitmaps, port array, delayed works, quirk flags, power budget, and onboard-device list. Port-level state includes the current child pointer, owner pointer for usbfs claims, peer/Type-C connector data, runtime-PM QoS, connection type, mirrored device state, over-current counter, quirk flags, and LPM permission bits. Global state includes `hub_wq`, `device_state_lock`, `usb_port_peer_mutex`, `highspeed_hubs`, module parameters for LEDs and enumeration scheme selection, and the EHCI companion-controller reset rwsem.

The driver does not persist configuration to disk. Durable external state is represented by hardware hub features, device addresses until disconnect/reset, HCD-owned state, sysfs-visible USB device/port objects, PM state, wakeup capability, and optional onboard platform devices. `usb_set_device_state()` is the central protected state transition API and mirrors device state into the containing `usb_port` sysfs attribute.

## Dependencies and Integration Points

The file integrates with the USB core (`usb_device`, configurations, descriptors, usbfs ioctls, notifier side effects via `device_add()`/`device_del()`), HCD operations (`update_hub_device`, `address_device`, `enable_device`, `update_device`, LPM timeout callbacks, port handoff/relinquish, `reset_device`, resuming-port reporting), runtime/system PM, USB PHY roothub notifications, Type-C attach/detach, ACPI handles, platform firmware port-removable/connect-type data, onboard USB platform-device helpers, kobject uevents for over-current notifications, KCOV USB remote coverage, and the Linux driver core. It consumes hub-class Chapter 11 requests (`GET_DESCRIPTOR`, hub/port `GET_STATUS`, clear/set hub and port features), USB2/USB3/USB3.1 link-power-management descriptors, BOS and SSP capability data, and USB OTG product/role helpers.

## Risks and Test Signals

High-risk areas are concurrency and lifecycle ordering: `event_bits` from IRQ context feed workqueue processing, `device_state_lock` protects recursive NOTATTACHED transitions and child publication, `usb_port_peer_mutex` protects port add/remove and peer operations, `status_lock` serializes port events with port suspend/resume, and PM references must balance across delayed activation, queued hub events, and child usage. Enumeration is intentionally tolerant of broken devices and has many quirk-driven retries; changes here can regress devices that need old/new scheme ordering, power cycling, longer descriptor timeouts, or strict reset timing. USB3 warm reset, LPM/LTM enabling, persist/reset-resume, and descriptor-change detection are also regression-prone because they mix HCD state, hub link state, and driver binding.

Useful test signals include hub probe/remove with root, bus-powered, self-powered, high-speed TT, SuperSpeed, and SuperSpeedPlus hubs; port connect/disconnect debounce; repeated interrupt URB errors causing hub reset; over-current sysfs notification and power restore; USB2 and USB3 device enumeration including new and old schemes; failed descriptor reads, bad ep0 max packet values, and retry/power-cycle paths; usbfs port claiming; runtime suspend/resume and remote wakeup; system suspend with USB-PERSIST and root-hub lost power; USB3 U1/U2 and USB2 hardware LPM enable/disable paths; TT buffer clear completion callbacks; device reset with interface `pre_reset`/`post_reset`; descriptor-morphing firmware download that forces re-enumeration; ACPI handle lookup; and quirk table behavior for autosuspend and interrupt interval reduction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/hub.h -->
# sources/distributed-fs/ceph-client/drivers/usb/core/hub.h

## Purpose

`hub.h` defines the private USB hub and USB port data structures shared by USB core hub-related source files. It captures the runtime state needed by `hub.c`, port-device code, Type-C integration, power management, status polling, event dispatch, and port-level sysfs state.

## Important APIs, Types, and Functions

`struct usb_hub` stores the hub interface device, hub USB device, reference count, interrupt URB, interrupt/status buffers, status mutex, consecutive error tracking, event/change/removed/wakeup/power/child-usage/warm-reset bitmaps, hub descriptor, transaction translator state, power budget, PM wake descendant count, lifecycle flags, hub quirk flags, indicator LED state/work, initialization and post-resume delayed work, hub event work, interrupt URB retry state, per-port pointer array, and onboard-device list.

`struct usb_port` represents one downstream port as a device. It stores the attached child `usb_device`, generic device, usbfs port owner, peer port, Type-C connector, PM QoS request, firmware/platform connection type, mirrored child device state and kernfs notification node, physical location token, status mutex, over-current count, port number, quirks, early-stop/ignore-event flags, SuperSpeed marker, and per-port USB3 LPM permission bits.

The header declares hub/port helpers implemented elsewhere: port device create/remove, port power control, hub lookup/refcounting, debounce, clear port feature, get port status, and port-power decoding. Inline helpers provide `to_usb_port()`, `hub_is_port_power_switchable()`, `hub_is_superspeed()`, `hub_is_superspeedplus()`, `hub_power_on_good_delay()`, and debounce variants for connected versus stable states.

## Control Flow

The header has no standalone runtime flow, but it fixes the call contract for hub lifecycle and event handling. `hub.c` allocates `struct usb_hub` during probe, fills descriptor and port arrays during configuration, schedules the declared work items during activation/resume/event processing, and releases the object through `hub_put()`. Port-device code allocates and registers `struct usb_port` objects and stores them in `hub->ports`, while `hub.c` updates `child`, `state`, PM references, and event counters as devices appear and disappear.

## State and Persistence Behavior

All state described here is runtime kernel memory. `struct usb_hub` persists for the bound lifetime of a hub interface and is kref-managed because work items can hold references after the interface path queues them. `struct usb_port` persists as a child device for each physical/logical hub port until hub disconnect. Bitmaps use one-based port numbers and assume `USB_MAXCHILDREN` fits in the single `unsigned long` storage, guarded by a preprocessor check. No file-backed persistence is defined; visible state is projected through devices, sysfs attributes, PM state, and connector/ACPI associations.

## Dependencies and Integration Points

The header depends on USB core declarations, Chapter 11 hub definitions, HCD types, Type-C connector types, and local `usb.h`. It is the shared structure boundary between `hub.c`, port-device implementation, USB Type-C attachment, ACPI/firmware port metadata, LED/indicator handling, onboard-device helpers, and runtime PM. The inline speed and power helpers embed descriptor interpretation that callers rely on for USB2 versus USB3 behavior.

## Risks and Test Signals

Risks include layout coupling across USB core files, one-based bitmap indexing mistakes, insufficient bitmap size if `USB_MAXCHILDREN` grows, stale `child` pointers across disconnect and runtime resume, unbalanced krefs around delayed work, and mismatched assumptions about when `descriptor` or `ports` are initialized. Test signals are compile coverage of all hub/port users, probe/disconnect under concurrent queued work, port sysfs state notifications, Type-C attach/detach on port child changes, USB3 LPM policy through per-port permit bits, and hubs with maximum port counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/hub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/ledtrig-usbport.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/ledtrig-usbport.c

## Purpose

`ledtrig-usbport.c` implements the `usbport` LED trigger. It lets an LED turn on when at least one USB device is connected to a selected set of USB hub ports, with per-port sysfs toggles and optional device-tree `trigger-sources` defaults.

## Important APIs, Types, and Functions

`struct usbport_trig_data` stores the bound LED class device, list of known ports, USB notifier block, and count of connected devices on observed ports. `struct usbport_trig_port` stores one observed-capable port entry: trigger data, hub USB device, port number, generated sysfs attribute name, observed flag, device attribute, and list node.

Core helpers are `usbport_trig_usb_dev_observed()`, which checks whether a connected USB device sits below an observed port; `usbport_trig_update_count()`, which scans all USB devices and sets LED brightness to `LED_FULL` or `LED_OFF`; sysfs callbacks `usbport_trig_port_show()` and `usbport_trig_port_store()`; `usbport_trig_port_observed()`, which reads OF `trigger-sources`; add/remove helpers for ports; `usbport_trig_notify()`, which reacts to `USB_DEVICE_ADD` and `USB_DEVICE_REMOVE`; and trigger lifecycle callbacks `usbport_trig_activate()` and `usbport_trig_deactivate()`. The file registers `usbport_led_trigger` with `module_led_trigger()`.

## Control Flow

Activation allocates trigger data, creates a `ports` sysfs group under the LED device, enumerates all current USB devices with `usb_for_each_dev()` and creates an attribute for every hub port, recalculates the connected observed-device count, stores trigger data on the LED, and registers a USB notifier. A user can write `0` or `1` to each generated `ports/<hub>-portN` attribute, which updates `observed` and recomputes the count.

On `USB_DEVICE_ADD`, the notifier first adds sysfs entries for the new device's child ports if it is a hub, then turns the LED on if the newly added device is connected to an observed port and the previous count was zero. On `USB_DEVICE_REMOVE`, it removes any port entries belonging to the removed hub and decrements the count if the removed device was connected to an observed port, turning the LED off when the count reaches zero. Deactivation removes all port attributes, removes the group, unregisters the USB notifier, and frees trigger data.

## State and Persistence Behavior

Observed-port selection and connected-device count are in-memory state tied to a specific LED trigger activation. Per-port sysfs files expose and mutate `observed`; values are not persisted by this file. Device-tree `trigger-sources` only seed the initial `observed` value. The LED brightness is derived state: nonzero matching device count maps to `LED_FULL`, zero maps to `LED_OFF`.

## Dependencies and Integration Points

The file depends on the LED trigger framework, USB device iteration and notifier APIs, sysfs groups and attributes, OF helpers, USB OF node lookup, and slab allocation. It integrates externally through LED trigger selection, per-LED sysfs `ports` attributes, `trigger-sources` phandles in firmware, and USB add/remove notifications emitted by the USB core.

## Risks and Test Signals

Risks include notifier/list/sysfs lifetime races during device removal and trigger deactivation, lack of explicit locking around the ports list and count, unchecked failures from `usbport_trig_add_port()` while bulk-adding existing or newly added hub ports, count underflow if notifications and observed state get out of sync, and the noted OF FIXME where `usb_of_get_device_node()` may return the connected device node rather than the physical port node. The show callback also returns `sysfs_emit(...) + 1`, which is unusual because `sysfs_emit()` already returns the number of bytes written. Test signals include activating/deactivating the trigger while USB devices are present, toggling generated port attributes, OF default matching through `trigger-sources`, connecting/removing devices on observed and unobserved ports, adding/removing hubs so nested port attributes appear/disappear, and stress testing concurrent USB hotplug while changing LED trigger state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/ledtrig-usbport.c -->
