# subset-b-005537 Research

Grouped source research for USB Type-C class, alternate-mode bus, mode-selection, controller, and mux/retimer drivers under `sources/distributed-fs/ceph-client/drivers/usb/typec`. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/anx7411.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/anx7411.c

## Purpose

`anx7411.c` is the Analogix ANX7411 USB Type-C/USB-PD controller driver. It binds the TCPC-facing I2C address, creates a second dummy I2C client for the firmware/SPI register window, registers a Type-C port, optional built-in orientation switch and mode mux, a USB role switch connection, and a power-supply object exposing negotiated source voltage/current.

## Important APIs, Types, and Functions

Core state is split between `struct anx7411_data` and nested `struct typec_params`. The driver uses SMBus byte/block helpers, firmware mailbox messages (`struct fw_msg`), `typec_register_port()`, `typec_register_partner()`, `typec_partner_register_altmode()`, `typec_set_orientation()`, `typec_set_data_role()`, `typec_set_pwr_role()`, `typec_set_pwr_opmode()`, `typec_set_mode()`, `usb_role_switch_set_role()`, `typec_mux_register()`, `typec_switch_register()`, runtime PM hooks, and `power_supply_register()`. Important flows are `anx7411_config()`, `anx7411_work_func()`, `anx7411_process_cmd()`, `anx7411_parse_cmd()`, `anx7411_typec_port_probe()`, `anx7411_typec_check_connection()`, and `anx7411_i2c_probe()`.

## Control Flow

Probe checks I2C block support, allocates state, registers the dummy firmware client, optionally registers local switch/mux devices from `orientation_switch` and `mode_switch` child nodes, parses connector roles/PDOs/sink wattage, registers the Type-C port, obtains IRQ from the I2C client or GPIO, registers a power supply, creates a single-thread workqueue, requests the interrupt, checks initial connection state, and enables runtime PM. IRQ handling only queues `anx7411_work_func()`. The worker reads firmware interrupt status and TCPC alert bytes, clears both, handles power-off detach by unregistering altmodes/partner and resetting power-supply state, handles firmware boot by sending configuration/PDO/identity/DP capability messages, processes received firmware messages, updates data/power roles, and reruns CC detection on CC changes. Firmware messages drive DP mux selection, Discover Modes registration, Enter Mode activation, and PD power readings.

## State and Persistence Behavior

All state is runtime-only: cached firmware versions, current CC/orientation/role/pin assignment, partner and altmode handles, PDO arrays parsed from firmware properties, power-supply online/type/current/voltage values, and workqueue/mutex state. Hardware/firmware owns PD negotiation and mailbox persistence; the Linux driver mirrors it into Type-C and power-supply class state. Removal unregisters partner altmodes, partner, workqueue, dummy I2C client, mux/switch, and port.

## Dependencies and Integration Points

The file integrates I2C/SMBus, TCPCI register definitions, firmware mailbox commands, GPIO IRQs, USB role-switch, Type-C class, Type-C mux/switch, DisplayPort altmode definitions, power-supply class, OF/fwnode connector properties, and runtime PM. Its port altmodes connect with the generic Type-C alternate-mode bus; its local mux/switch registrations can be matched by the port through fwnode graph/property lookup.

## Risks and Test Signals

Risks include CRC/length handling in firmware mailbox messages, `ret |=` aggregation hiding the first failing register write, altmode registration logic around VDM ACK tests, runtime PM enabled without an obvious disable in remove, workqueue destruction ordering versus in-flight IRQs, optional role-switch behavior, sink-voltage selection overwriting per PDO, duplicated `CC1_RD` macro definition, and power-supply state transitions for the private HANG state. Test signals include probe on each supported TCPC/SPI address pair, missing connector and missing IRQ failures, initial attached-device detection, detach power-off cleanup, DP pin assignment C/D/E/U mux results, role-switch changes, power-supply voltage/current updates from `REQUEST_*` registers, suspend/resume reconnection, and invalid mailbox CRC handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/anx7411.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/bus.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/bus.c

## Purpose

`bus.c` implements the USB Type-C alternate-mode bus. It binds partner alternate-mode devices to alternate-mode drivers, creates sysfs cross-links between port and partner altmodes, forwards Enter/Exit/Attention/VDM/cable VDM operations, and coordinates mux/retimer state changes for negotiated alternate-mode configurations.

## Important APIs, Types, and Functions

Exported APIs include `typec_altmode_notify()`, `typec_altmode_enter()`, `typec_altmode_exit()`, `typec_altmode_attention()`, `typec_altmode_vdm()`, cable variants, `typec_altmode_get_partner()`, `typec_altmode_get_plug()`, `typec_altmode_put_plug()`, `__typec_altmode_register_driver()`, `typec_altmode_unregister_driver()`, and `typec_match_altmode()`. Internal helpers convert `struct altmode` to `struct typec_mux_state` and `struct typec_retimer_state` before calling `typec_mux_set()` and `typec_retimer_set()`.

## Control Flow

Alternate-mode entry first moves the associated port mux/retimer to safe state, checks that the paired port altmode supports `enter`, and blocks partner entry when the port mode is inactive. Exit similarly moves to safe state before invoking the peer `exit`. Notifications configure retimer/mux state and optionally call the peer `notify`. Cable helpers dispatch to registered `cable_ops` on either plug or partner endpoints. Bus matching only binds drivers to partner altmode devices by SVID. Probe creates reciprocal sysfs links and calls the altmode driver's `probe`; remove removes links, calls driver `remove`, forces safe state for active modes, clears active state, and clears ops/description.

## State and Persistence Behavior

Persistent storage is limited to in-memory `struct altmode` relationships: `partner`, `plug[]`, cached mux/retimer references, ops, active flag, and sysfs links. No file-backed persistence exists. Device references and module references are maintained by the core class and bus registration paths.

## Dependencies and Integration Points

The bus depends on `bus.h`, `class.h`, `mux.h`, retimer helpers, Linux driver core bus registration, sysfs links, uevents, and USB PD VDO definitions. It is used by DisplayPort, Thunderbolt, USB4, and vendor altmode drivers to communicate with Type-C port controllers and mux/retimer hardware.

## Risks and Test Signals

Risks include incorrect partner linkage, safe-state failures leaving muxes active, cable SOP index handling, module lifetime when active altmode drivers are removed, and a duplicated `if (!adev)` line in `typec_altmode_vdm()` in this source snapshot. Test signals include driver modalias `typec:id%04X`, sysfs `port`/`partner` links, enter/exit ordering with mux safe state, notify propagation into mux/retimer callbacks, cable plug VDM dispatch, and removal of an active altmode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/bus.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/bus.h

## Purpose

`bus.h` is the private Type-C alternate-mode bus header. It defines the wrapper state that the class layer allocates around public `struct typec_altmode` objects.

## Important APIs, Types, and Functions

The key type is `struct altmode`, containing the public `adev`, local ID, mux and retimer handles, supported role flags, custom mode sysfs group storage, and relationships to a port/partner altmode plus up to two cable plug altmodes. `to_altmode()` maps the public object back to this private wrapper.

## Control Flow

The header has no runtime control flow. It shapes control flow by letting `class.c` allocate/link/release alternate-mode devices and letting `bus.c` route operations between paired port, partner, and plug altmodes.

## State and Persistence Behavior

All fields are runtime device state. The relationship pointers are maintained by registration/release paths and cleared on unregister; mux/retimer references are acquired by the port altmode registration path and released on unregister.

## Dependencies and Integration Points

It includes `linux/usb/typec_altmode.h` and forward declares mux/retimer types. Any local change affects both the Type-C class implementation and bus dispatch code.

## Risks and Test Signals

Risks are local ABI coupling across private source files and stale relationship pointers if register/unregister ordering changes. Test signals are compile coverage of `class.c` and `bus.c`, altmode registration/unregistration under partner/cable teardown, and reference-count checks for port altmodes with mux/retimer handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/class.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/class.c

## Purpose

`class.c` implements the USB Type-C connector class and most public Type-C device APIs. It exposes ports, partners, cables, cable plugs, and alternate modes as Linux devices with sysfs attributes, handles identity/product-type reporting, role/state updates, orientation and mode mux calls, USB device-to-partner links, USB Power Delivery object links, and class/bus initialization.

## Important APIs, Types, and Functions

Major exported APIs include `typec_register_port()`, `typec_unregister_port()`, `typec_register_partner()`, `typec_unregister_partner()`, cable/plug register functions, partner/cable identity and PD setters, altmode register/unregister functions, `typec_altmode_set_ops()`, `typec_altmode_update_active()`, `typec_port_register_altmodes()`, role setters/getters, string-to-enum helpers, `typec_set_orientation()`, `typec_set_mode()`, SVDM version helpers, `typec_get_fw_cap()`, and `typec_get_drvdata()`. Device state lives in private `struct typec_port`, `struct typec_partner`, `struct typec_cable`, `struct typec_plug`, and `struct altmode` from the local headers.

## Control Flow

`typec_init()` registers the altmode bus, mux class, retimer class, Type-C class, and USB PD subsystem. Port registration allocates an ID, initializes default power/data/vconn roles from capabilities, initializes mutexes/IDAs, resolves switch/mux/retimer handles, adds the device, links PD, and creates ACPI port links when available. Partner registration allocates mode IDs, sets accessory/PD/USB capability fields, optionally exposes identity attributes, registers a child device, and links already-known USB2/USB3 devices. Alternate-mode registration creates a child device, mode-specific sysfs group, and partner/port relationships. Sysfs stores call port operations for role swaps, default USB mode, PD selection, and altmode activation, then update cached state only after successful callbacks. Removal reverses links and device registration.

## State and Persistence Behavior

State is entirely kernel runtime state exposed through sysfs: role values, orientation, power operation mode, USB mode/capabilities, PD revision, identity pointers, altmode activity/priority, USB device links, and PD links. The class does not persist policy across reboot. Device lifetime is reference-counted through the driver core; IDAs allocate port and altmode IDs. Mutexes protect mutable port type and partner USB-device links.

## Dependencies and Integration Points

The implementation integrates Linux device/class/bus/sysfs/uevent core, USB core connector callbacks, USB PD object helpers from `pd.h`, Type-C mux/switch/retimer lookup APIs, ACPI port linking, firmware properties, and alternate-mode drivers. Controller drivers such as ANX7411 and HD3SS3220 depend on these APIs to expose connector state.

## Risks and Test Signals

Risks include role/mode sysfs stores diverging from hardware callbacks, reference leaks across partner/cable/altmode unregister, priority overflow and duplicate priority adjustment, visibility updates after ops changes, missing validation for identity VDO array contents, `sysfs_emit_at(buf, len - 1, "\n")` style paths when no modes are printable, and complex teardown ordering with linked USB devices. Test signals include sysfs attributes and visibility for every port capability permutation, role swap error propagation, port/partner/cable/plug lifecycle tests, identity and product-type uevents, mode priority reordering, active altmode module reference changes, mux/switch calls from `typec_set_orientation()` and `typec_set_mode()`, and init/exit ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/class.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/class.h

## Purpose

`class.h` is the private state header for the USB Type-C class implementation. It defines the concrete device wrappers behind the public Type-C handles.

## Important APIs, Types, and Functions

It declares `struct typec_plug`, `struct typec_cable`, `struct typec_partner`, and `struct typec_port`, plus `to_typec_*()` container macros, device type externs, class externs, and ACPI port-link helpers. Fields include device objects, IDAs, PD identity/revision/SVDM state, USB mode/capability state, role state, mutexes, mux/switch/retimer handles, capabilities, operations, and linked USB2/USB3 devices.

## Control Flow

The header has no executable flow. It constrains registration, teardown, sysfs, and altmode-bus flow in `class.c`, `bus.c`, and mode-selection code by defining where state is cached and how device types are recognized.

## State and Persistence Behavior

All structures are runtime-only and released through device-type release callbacks. `struct typec_port` owns its duplicated capability block and mux/switch/retimer references; partner/cable/plug structures own mode IDAs and identity pointers supplied by controller drivers.

## Dependencies and Integration Points

It depends on Linux device core and public USB Type-C definitions. It is the private integration point among Type-C class, altmode bus, mux/retimer framework, ACPI helpers, and USB core connector links.

## Risks and Test Signals

Risks are broad because field layout changes affect many local files. Test signals are compile coverage for all Type-C class users, hotplug registration/unregistration, USB device attach/deattach callbacks, and ACPI/non-ACPI builds where `typec_link_ports()` becomes an inline no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/hd3ss3220.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/hd3ss3220.c

## Purpose

`hd3ss3220.c` is the TI HD3SS3220 dual-role Type-C port controller driver. It configures port type, preferred source/sink role, advertised current, data role, USB role-switch state, and optional VBUS regulator control from I2C registers and firmware connector properties.

## Important APIs, Types, and Functions

`struct hd3ss3220` stores the regmap, role switch, Type-C port, optional polling work, cached USB role, optional ID GPIO/IRQ, and optional VBUS regulator. Important functions are `hd3ss3220_set_power_opmode()`, `hd3ss3220_set_port_type()`, `hd3ss3220_set_source_pref()`, `hd3ss3220_get_attached_state()`, Type-C ops `try_role`/`port_type_set`, `hd3ss3220_set_role()`, IRQ/poll handlers, connector configuration helpers, `hd3ss3220_probe()`, and `hd3ss3220_remove()`.

## Control Flow

Probe creates an I2C regmap, finds the connector via child node or graph endpoint, gets a role switch, optional VBUS regulator and ID GPIO, configures default DRP/DRD Type-C capability, applies preferred role and port type properties, registers the Type-C port, applies power opmode, reads current attachment state, clears pending interrupt status, and either requests the chip IRQ or starts a one-second polling loop. Interrupts and polling call `hd3ss3220_set_role()`, which reads attached state, updates USB role switch and Type-C data role, and controls VBUS for host mode unless an ID GPIO is present.

## State and Persistence Behavior

The driver caches current role for polling comparisons and uses hardware registers for mode/preference/current advertisement. Type-C state is mirrored into class devices. There is no persistence beyond chip registers and runtime driver state. Remove cancels polling if active, unregisters the Type-C port, and releases the role switch.

## Dependencies and Integration Points

Dependencies include I2C/regmap, firmware graph/child connector nodes, USB role-switch, Type-C class, GPIO descriptors, IRQs, delayed work, and regulators. The Type-C class calls back into this driver for preferred-role and port-type sysfs writes.

## Risks and Test Signals

Risks include the `regulator_control()` error message using reversed enable/disable text, negative I2C errors stored in an enum-returning `hd3ss3220_get_attached_state()`, polling work continuing after error paths unless cancelled, optional regulator behavior with/without ID GPIO, and mode changes requiring termination disable/re-enable sequencing. Test signals include IRQ and polling variants, connector graph and child-node discovery, source/sink/DRP mode changes, advertised current settings, attach as DFP/UFP/none, VBUS regulator transitions, ID GPIO interrupt behavior, and failed role-switch or port registration unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/hd3ss3220.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mode_selection.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mode_selection.c

## Purpose

`mode_selection.c` implements priority-based automatic Type-C alternate-mode activation for a partner. It builds a prioritized list of partner altmodes with activation callbacks, attempts entry in order, handles timeout/error callbacks, exits an already-active lower-priority mode, and cleans up when a mode succeeds or all candidates fail.

## Important APIs, Types, and Functions

Private state includes `struct mode_state`, `struct mode_selection`, and `struct mode_order`. Exported APIs are `typec_mode_selection_start()`, `typec_altmode_state_update()`, and `typec_mode_selection_delete()`. Core helpers are `activate_altmode()`, `mode_selection_activate()`, `mode_selection_work_fn()`, `altmode_add_to_list()`, `compare_priorities()`, and `mode_list_clean()`.

## Control Flow

Start refuses USB4 partners and duplicate selection sessions, collects partner altmode children that have a paired port altmode and an `activate` op, sorts them by port priority, stores delay/timeout, and schedules delayed work. Work examines the first candidate: if already active it cleans the list; if another SVID is active it exits that mode first; if the current candidate has an error it deactivates/removes it; otherwise it calls activate-enter and marks the candidate as timed out until a callback arrives. `typec_altmode_state_update()` updates the head candidate result, cancels/reschedules work immediately, and records the active SVID.

## State and Persistence Behavior

State is a per-partner heap allocation referenced by `partner->sel`. It contains a mutex-protected list, active SVID, delayed work, timeout and delay. No state persists after delete, success cleanup, or partner teardown.

## Dependencies and Integration Points

The code depends on the private Type-C partner structure, child alternate-mode devices, `typec_altmode_get_partner()`, altmode `activate` ops, Linux delayed work, list sorting, and mutexes. Port alternate-mode priority from `class.c` controls ordering.

## Risks and Test Signals

Risks include deadlock avoidance relying on the mode list remaining stable while the mutex is dropped, timeout/error races with delayed work cancellation, USB4 exclusion policy, memory cleanup on partial list construction, and a duplicated `struct mode_state *ms;` declaration in `typec_altmode_state_update()` in this source snapshot. Test signals include sorted activation order, failed first mode falling through to the next, timeout behavior, successful callback cleanup, active-mode exit before entering another mode, delete while work is pending, and no activation for partners without suitable altmode ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mode_selection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux.c

## Purpose

`mux.c` implements the generic USB Type-C orientation switch and mode mux framework. It lets port/controller drivers find one or more fwnode-linked switch/mux devices and lets hardware drivers register switch or mux devices under the `typec_mux` class.

## Important APIs, Types, and Functions

Exported APIs include `fwnode_typec_switch_get()`, `typec_switch_get()` via public wrappers, `typec_switch_put()`, `typec_switch_register()`, `typec_switch_unregister()`, `typec_switch_set()`, switch drvdata accessors, and equivalent mux APIs `fwnode_typec_mux_get()`, `typec_mux_put()`, `typec_mux_register()`, `typec_mux_unregister()`, `typec_mux_set()`, and mux drvdata accessors. Private aggregate handles store up to `TYPEC_MUX_MAX_DEVS` underlying devices.

## Control Flow

Lookup uses `fwnode_connection_find_matches()` and class searches. Graph endpoints are filtered by `orientation-switch` or `mode-switch` properties, duplicates are skipped, missing but referenced devices return `-EPROBE_DEFER`, and matched parent modules are pinned. Set calls fan out to all devices and ignores `-EOPNOTSUPP` so composite paths can tolerate devices that do not implement a specific mode. Registration allocates a device, assigns parent/fwnode/class/type/driver data/name, and calls `device_add()`. Put reverses module and device references.

## State and Persistence Behavior

Aggregate `struct typec_switch`/`struct typec_mux` handles are heap allocations containing referenced switch/mux device pointers. Registered device state lives in `struct typec_switch_dev` and `struct typec_mux_dev` until device unregister/release. No persistent state exists.

## Dependencies and Integration Points

The file integrates Linux class/device core, fwnode graph connections, module refcounts, Type-C class private device-type checks, and public Type-C mux APIs. It is used by `class.c`, controller drivers, and all chip-specific mux/retimer drivers in this subset.

## Risks and Test Signals

Risks include duplicate-skip logic dereferencing a NULL `dev` in this snapshot, duplicated `IS_ERR_OR_NULL(sw)` check in `typec_switch_set()`, module owner assumptions through parent driver pointers, max-device truncation at three entries, and handling of mixed devices returning `-EOPNOTSUPP`. Test signals include fwnode lookup with no connection, deferred probe, duplicate graph edges, multiple chained muxes, unregister/put module ref balancing, and registration failure after device initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux.h

## Purpose

`mux.h` is the private header for registered Type-C switch and mux device wrappers.

## Important APIs, Types, and Functions

It defines `struct typec_switch_dev` with a device and orientation `set` callback, `struct typec_mux_dev` with a device and mode `set` callback, container macros, device type externs, and type-test macros.

## Control Flow

There is no executable control flow. The definitions are consumed by `mux.c` and hardware drivers through the public registration APIs.

## State and Persistence Behavior

The wrappers are runtime device objects allocated in `typec_switch_register()` or `typec_mux_register()` and freed by their release callbacks. Driver-private state is stored through device driver data.

## Dependencies and Integration Points

It includes `linux/usb/typec_mux.h` and integrates the public Type-C mux API with local class/device implementation details.

## Risks and Test Signals

Risks are local API coupling between chip drivers and the core mux implementation. Test signals are compile coverage for all switch/mux drivers and runtime registration/unregistration with drvdata retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/Kconfig

## Purpose

`mux/Kconfig` declares the configuration menu for USB Type-C mux, switch, redriver, and retimer drivers.

## Important APIs, Types, and Functions

It provides tristate symbols for FSA4480, GPIO SBU mux, PI3USB30532, Intel PMC, IT5205, NB7VPQ904M, PS883X, PTN36502, TUSB1046, and WCD939X USBSS. Dependencies select I2C, ACPI, Intel SCU IPC, USB role-switch, USB common, REGMAP_I2C, and optional DRM AUX bridge support as needed.

## Control Flow

Kconfig has build-selection flow only. Enabling a symbol controls whether the matching object is built by the Makefile and whether helper dependencies are selected.

## State and Persistence Behavior

Configuration state is build-time kernel configuration. No runtime state is defined here.

## Dependencies and Integration Points

This menu integrates the chip drivers with the kernel build system and the Type-C mux framework. Optional DRM constraints ensure AUX bridge registration is only selected when the DRM bridge stack is present.

## Risks and Test Signals

Risks include missing dependency declarations causing build failures in unusual configs, symbols selectable without required firmware bindings, and optional `DRM || DRM=n` combinations. Test signals are allyesconfig/allmodconfig, targeted builds for each tristate as built-in and module, and dependency-disabled negative builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/Makefile

## Purpose

`mux/Makefile` maps Type-C mux Kconfig symbols to object files.

## Important APIs, Types, and Functions

Each `obj-$(CONFIG_...) += ...o` entry corresponds to a chip or platform driver: `fsa4480.o`, `gpio-sbu-mux.o`, `pi3usb30532.o`, `intel_pmc_mux.o`, `it5205.o`, `nb7vpq904m.o`, `ps883x.o`, `ptn36502.o`, `tusb1046.o`, and `wcd939x-usbss.o`.

## Control Flow

The build system includes an object only when the associated config is enabled. There is no runtime logic.

## State and Persistence Behavior

No runtime state or persistence exists. The file only controls build artifacts.

## Dependencies and Integration Points

It integrates the Kconfig menu with kbuild and module generation for the Type-C mux directory.

## Risks and Test Signals

Risks are stale object mappings when Kconfig symbols or filenames change. Test signals are successful built-in and module builds for each symbol and confirming module names match Kconfig help text where documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/fsa4480.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/fsa4480.c

## Purpose

`fsa4480.c` drives the ON Semiconductor/Fairchild FSA4480 analog audio, USB, and SBU switch for Type-C connectors. It registers both an orientation switch and a mode mux, handles USB, DP, DP+USB, and audio accessory routing, and supports optional SBU lane inversion from `data-lanes`.

## Important APIs, Types, and Functions

`struct fsa4480` stores client, lock, switch/mux devices, regmap, cached orientation/mode/SVID/current enable, and `swap_sbu_lanes`. Important functions are `fsa4480_set()`, `fsa4480_switch_set()`, `fsa4480_mux_set()`, `fsa4480_parse_data_lanes_mapping()`, `fsa4480_probe()`, and `fsa4480_remove()`.

## Control Flow

Probe parses optional graph lane mapping, initializes an I2C regmap, enables optional `vcc`, reads the device ID, programs default delay/slew registers and USB safe state, then registers switch and mux devices on the same fwnode. Switch callbacks update orientation and rerun routing. Mux callbacks update mode/SVID and rerun routing. `fsa4480_set()` computes enable and select bits, temporarily disables SBU outputs before changing SBU routing, writes select/enable registers, and starts automatic jack detection for audio mode.

## State and Persistence Behavior

The driver caches the last requested mode/orientation/SVID and current enable register to avoid unnecessary operations and sequence SBU disabling. Hardware registers hold the active routing until changed or reset. No file-backed persistence exists.

## Dependencies and Integration Points

Dependencies include I2C, regmap, regulator, fwnode graph properties, Type-C mux/switch APIs, and DisplayPort Type-C state definitions.

## Risks and Test Signals

Risks include unsupported modal SVIDs returning `-EOPNOTSUPP`, audio mode sharing USB/AGND enables, SBU timing delays, lane mapping limited to normal/inverted two-lane cases, and writes not checking individual regmap errors in the main set path. Test signals include device ID read, optional regulator enable, USB/DP C/D/E/F/audio mode routing, normal/reverse and swapped SBU orientation, duplicate set suppression, mux registration failure unwind, and removal unregistering mux before switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/fsa4480.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/gpio-sbu-mux.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/gpio-sbu-mux.c

## Purpose

`gpio-sbu-mux.c` implements a simple platform Type-C SBU mux using GPIOs for enable and lane select.

## Important APIs, Types, and Functions

`struct gpio_sbu_mux` stores optional enable GPIO, required select GPIO, switch/mux devices, mutex, and cached enabled/swapped booleans. Key functions are `gpio_sbu_switch_set()`, `gpio_sbu_mux_set()`, `gpio_sbu_mux_probe()`, and `gpio_sbu_mux_remove()`.

## Control Flow

Probe obtains GPIOs, registers a Type-C orientation switch and mode mux on the platform device fwnode, and stores drvdata. Orientation NONE disables, NORMAL clears swap, and REVERSE sets swap. Mux state enables SBU only for DP C/D/E and disables for safe/USB. Remove forces enable low and unregisters mux/switch devices.

## State and Persistence Behavior

Cached `enabled` and `swapped` mirror GPIO outputs and are protected by a mutex. Hardware state is the GPIO output levels; no persistent storage exists.

## Dependencies and Integration Points

The driver depends on platform devices, GPIO descriptors, Type-C mux/switch core, and DP state constants. It is useful for boards where SBU routing is implemented by discrete GPIO-controlled analog switches.

## Risks and Test Signals

Risks include returning `-EOPNOTSUPP` from mux set when no enable GPIO exists even though switch routing can still work, no validation that selected modes are DP altmodes by SVID, and ordering between orientation and mux calls affecting when enable/select outputs change. Test signals include probe with and without optional enable GPIO, normal/reverse orientation toggling select, safe/USB disabling, DP C/D/E enabling, removal disabling output, and concurrent orientation/mode updates under the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/gpio-sbu-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/intel_pmc_mux.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/intel_pmc_mux.c

## Purpose

`intel_pmc_mux.c` exposes Intel PMC firmware-controlled USB Type-C routing as Type-C switch, mux, and USB role-switch devices. It sends PMC USBC IPC commands for connect, disconnect, safe mode, DisplayPort, Thunderbolt, USB4, and DP HPD routing and reads IOM port status through ACPI-discovered MMIO.

## Important APIs, Types, and Functions

State is in `struct pmc_usb` and per-port `struct pmc_usb_port`. Key functions include `pmc_usb_send_command()`, `pmc_usb_command()`, `update_port_status()`, `pmc_usb_connect()`, `pmc_usb_disconnect()`, `pmc_usb_mux_safe_state()`, `pmc_usb_mux_dp()`, `pmc_usb_mux_dp_hpd()`, `pmc_usb_mux_tbt()`, `pmc_usb_mux_usb4()`, `pmc_usb_mux_set()`, `pmc_usb_set_orientation()`, `pmc_usb_set_role()`, `pmc_usb_register_port()`, `pmc_usb_probe_iom()`, and debugfs status support.

## Control Flow

Probe counts child ACPI/fwnode port nodes, limits to four ports, obtains Intel SCU IPC, discovers an IOM ACPI device and maps its port-status MMIO, creates debugfs, and registers switch/mux/role-switch devices for each child using `usb2-port-number`, `usb3-port-number`, and optional orientation overrides. Role-switch calls connect or disconnect. Mux calls refresh IOM status, skip work if orientation/role is absent, send safe/USB/DP/TBT/USB4 commands according to mode and altmode SVID, and handle DP HPD updates when already in DP mode. Commands retry PMC busy responses up to three times.

## State and Persistence Behavior

The driver caches per-port orientation, role, port numbers, optional SBU/HSL orientation overrides, and last IOM status. The authoritative routing state lives in PMC firmware/IOM and is queried through MMIO. Debugfs exposes current `iom_status`. No state is persisted by the driver.

## Dependencies and Integration Points

Dependencies include ACPI, Intel SCU IPC, USB role-switch, Type-C mux/switch, DP/TBT/USB4 data structures, debugfs, USB debug root, and IOM ACPI IDs for several Intel platforms. It integrates firmware-controlled routing with generic Type-C class consumers.

## Risks and Test Signals

Risks include subtle platform-specific bit packing, incorrect active/retimer cable flags for TBT/USB4, an apparent `||`/`&&` logic hazard in USB4 retimer-cable ACPI ID checks, role stored after command even if connect/disconnect failed, unregister loops that may touch unregistered devices on partial probe failure, and stale status if IOM layout data is wrong. Test signals include ACPI child parsing, Tiger/Alder/Meteor/Lunar IOM offsets, role swaps causing disconnect/reconnect, safe-state no-op conditions, DP HPD level/IRQ sequencing, TBT and USB4 cable-type permutations, PMC busy retry behavior, and debugfs `iom_status`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/intel_pmc_mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/it5205.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/it5205.c

## Purpose

`it5205.c` drives the ITE IT5205 passive Type-C USB/DisplayPort alternate-mode mux. It registers an orientation switch and mux, verifies chip ID, configures USB/DP/DP+USB routing, and optionally enables CSBU over-voltage protection.

## Important APIs, Types, and Functions

`struct it5205` stores I2C client, regmap, switch, and mux handles. Important functions are `it5205_switch_set()`, `it5205_mux_set()`, `it5205_irq_handler()`, `it5205_enable_ovp()`, `it5205_probe()`, and `it5205_remove()`.

## Control Flow

Probe enables required `vcc`, initializes regmap, waits for power-up, clears power-down, reads the four-byte chip ID, initializes USB mode, registers switch and mux devices, and if `ite,ovp-enable` and IRQ are present, programs OVP thresholds/unmasking and requests a threaded IRQ. Orientation callbacks toggle the polarity bit or clear the mux control register on NONE. Mux callbacks accept USB, DP C/E, DP D, and safe states, rejecting non-DP modal SVIDs. OVP IRQ reads ISR, warns on overvoltage, and toggles the CSBU switch bit to reset.

## State and Persistence Behavior

The driver keeps no software mode cache beyond handles. Hardware registers store current mux mode, polarity, Vref, OVP threshold, and CSBU interrupt state. No persistence exists across reset.

## Dependencies and Integration Points

It depends on I2C, regmap, a regulator, optional IRQ, OF property `ite,ovp-enable`, Type-C mux/switch APIs, and DP mode constants.

## Risks and Test Signals

Risks include switch and mux callbacks ignoring regmap update errors in orientation paths, no mutex around register read/modify/write while orientation and mode may race, optional OVP silently disabled without IRQ, and fixed OVP threshold. Test signals include chip-ID mismatch failure, regulator and 50 ms power-up timing, USB/DP C/D/E/safe routing, normal/reverse/NONE orientation, OVP interrupt reset behavior, and cleanup after IRQ request failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/it5205.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/nb7vpq904m.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/nb7vpq904m.c

## Purpose

`nb7vpq904m.c` drives the OnSemi NB7VPQ904M Type-C redriver. It registers a local orientation switch and retimer, chains orientation and mode changes to downstream Type-C switch/mux handles, configures channel equalization/output/gain/loss settings, and supports DP, DP+USB, USB, and safe states.

## Important APIs, Types, and Functions

`struct nb7vpq904m` contains GPIO/regulator/regmap handles, local switch/retimer, downstream switch/mux handles, lane-swap flag, mutex, orientation, mode, and SVID. Key functions are `nb7vpq904m_set_channel()`, `nb7vpq904m_set()`, `nb7vpq904m_sw_set()`, `nb7vpq904m_retimer_set()`, `nb7vpq904m_parse_data_lanes_mapping()`, `nb7vpq904m_probe()`, and `nb7vpq904m_remove()`.

## Control Flow

Probe initializes regmap and default state, obtains optional enable GPIO and VCC regulator, resolves downstream orientation switch and mode mux, parses endpoint `data-lanes` for normal or inverted mapping, powers/enables the chip, registers a DRM AUX bridge, then registers its switch and retimer. Switch set first forwards orientation downstream, then updates local routing under a mutex. Retimer set updates local mode/SVID, applies register programming, then forwards equivalent mux state downstream. Safe and USB states configure USB activity and AUX/CC defaults; DP states program all channels and AUX selection.

## State and Persistence Behavior

The driver caches mode/orientation/SVID and whether data lanes are inverted. Hardware register state persists only while the redriver is powered/enabled. Remove unregisters retimer/switch, disables GPIO/regulator, and drops downstream references.

## Dependencies and Integration Points

Dependencies include I2C, regmap, optional GPIO/regulator, OF graph endpoint lane mapping, DRM AUX bridge, Type-C switch/mux lookup, Type-C retimer registration, and DP altmode constants.

## Risks and Test Signals

Risks include continuing after regulator enable failure with only a warning, no chip-ID verification, fixed redriver tuning values, lane-mapping limited to exact four-lane normal/reversed arrays, and needing correct order when forwarding switch/mux state downstream. Test signals include inverted lane mapping, normal/reverse USB routing, DP C/E four-lane, DP D/F multi-function routing, downstream mux propagation, enable GPIO and regulator cleanup, and probe deferral for downstream switch/mux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/nb7vpq904m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/pi3usb30532.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/pi3usb30532.c

## Purpose

`pi3usb30532.c` drives the Pericom PI3USB30532 Type-C cross switch/mux. It exposes one orientation switch and one mode mux that both update a single configuration register.

## Important APIs, Types, and Functions

`struct pi3usb30532` stores I2C client, mutex, switch/mux handles, and cached config byte. Functions are `pi3usb30532_set_conf()`, `pi3usb30532_sw_set()`, `pi3usb30532_mux_set()`, `pi3usb30532_probe()`, and `pi3usb30532_remove()`.

## Control Flow

Probe reads the existing config register, registers switch and mux devices on the device fwnode, and stores drvdata. Orientation NONE opens the switch, NORMAL clears the swap bit, and REVERSE sets it. Mux set preserves swap while selecting open/safe, USB3, four-lane DP for C/E, or USB3 plus two-lane DP for D.

## State and Persistence Behavior

The cached config register avoids redundant I2C writes and is protected by a mutex. Hardware state is the single config byte. No persistent state exists.

## Dependencies and Integration Points

Dependencies are I2C SMBus, Type-C switch/mux core, and DP state constants. It integrates simple crossbar hardware with generic Type-C orientation and mux requests.

## Risks and Test Signals

Risks include unsupported modes silently preserving the old config, no SVID validation for DP states, single-register coupling between orientation and mode, and no regulator/reset handling. Test signals include initial register read, normal/reverse/NONE orientation, safe/USB/DP C/D/E mux transitions preserving swap, write failure propagation, and mux registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/pi3usb30532.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/ps883x.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/ps883x.c

## Purpose

`ps883x.c` drives Parade PS883x Type-C retimers. It powers and resets the chip, registers a Type-C orientation switch and retimer, forwards switch/mux state to downstream handles, and writes connection-status registers representing USB3, DP, Thunderbolt, USB4, active-cable, orientation, and HPD-related state.

## Important APIs, Types, and Functions

`struct ps883x_retimer` stores reset GPIO, regmap, local switch/retimer, clock, six regulators, downstream Type-C switch/mux, mutex, orientation, and cached three status bytes. Important functions are `ps883x_configure()`, `ps883x_set()`, `ps883x_sw_set()`, `ps883x_retimer_set()`, regulator enable/disable/get helpers, `ps883x_retimer_probe()`, and `ps883x_retimer_remove()`.

## Control Flow

Probe initializes regmap, gets required regulators, clock, reset GPIO, downstream switch and mux, registers a DRM AUX bridge, enables regulators in sequence, enables the XO clock, resets the chip unless already configured, verifies register access, then registers local switch and retimer. Switch set forwards orientation downstream and updates the orientation bit. Retimer set builds three config bytes from altmode SVID/mode or non-alt USB/USB4 state, writes changed bytes, then forwards mux state downstream.

## State and Persistence Behavior

Cached `cfg0..cfg2` prevent duplicate register writes. Hardware routing/status registers persist while powered. Runtime driver state is cleared on remove, which unregisters devices, asserts reset, disables clock/regulators, and releases downstream handles.

## Dependencies and Integration Points

Dependencies include I2C/regmap, GPIO reset, clocks, regulators, DRM AUX bridge, Type-C switch/mux/retimer APIs, DP altmode, Thunderbolt altmode, and Enter USB data.

## Risks and Test Signals

Risks include complex regulator unwinding, reset-skip behavior based on `CONNECTION_PRESENT`, unsupported SVID/mode errors, assuming `state->data` shape for USB4/TBT/DP, and status-register semantics standing in for actual link policy. Test signals include power sequencing failures at each rail, clock failure unwind, reset and no-reset probe paths, USB2 safe no-op, USB3, USB4 passive/active cable, DP C/D/E, TBT active cable/LSRX flags, orientation updates, downstream mux propagation, and remove power-down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/ps883x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/ptn36502.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/ptn36502.c

## Purpose

`ptn36502.c` drives the NXP PTN36502 Type-C redriver. It registers a Type-C orientation switch and retimer, chains state to downstream switch/mux handles, verifies chip ID/revision, and configures USB-only, DP-only, and USB+DP routing with fixed DP link/lane tuning.

## Important APIs, Types, and Functions

`struct ptn36502` stores client, optional `vdd18` regulator, regmap, local switch/retimer, downstream switch/mux handles, mutex, orientation, mode, and SVID. Key functions are `ptn36502_set()`, `ptn36502_sw_set()`, `ptn36502_retimer_set()`, `ptn36502_detect()`, `ptn36502_probe()`, and `ptn36502_remove()`.

## Control Flow

Probe initializes regmap, default state, mutex, optional regulator, downstream switch and mux references, enables regulator, reads chip ID/revision, registers a DRM AUX bridge, registers local orientation switch, then registers local retimer. Switch set forwards orientation downstream, updates local orientation, and reapplies mode. Retimer set updates local mode/SVID, applies local registers, then forwards mux state downstream. Safe mode powers down, USB mode sets USB-only with orientation, DP modes enable AUX monitoring/crossbar, set two or four lanes, HBR2 link rate, and lane control values.

## State and Persistence Behavior

Mode/orientation/SVID are cached under a mutex. Hardware register state persists only while powered. Remove unregisters retimer and switch, disables regulator, and drops downstream handles.

## Dependencies and Integration Points

Dependencies include I2C, regmap, optional regulator, DRM AUX bridge, Type-C switch/mux/retimer APIs, and DP altmode constants. It is designed to sit in a chain with another mux/switch device.

## Risks and Test Signals

Risks include optional regulator retrieval returning errors for absent supplies, fixed HBR2/lane-tuning values, non-DP modal states rejected by SVID check, and no explicit `i2c_set_clientdata()` visible before remove uses `i2c_get_clientdata()` in this snapshot. Test signals include chip-ID mismatch, revision read, safe/USB/DP C/D/E/F routing, normal/reverse orientation, downstream switch/mux propagation, regulator enable/disable, and retimer registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/ptn36502.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/tusb1046.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/tusb1046.c

## Purpose

`tusb1046.c` drives the TI TUSB1046-DCI Type-C crosspoint switch. It registers an orientation switch and mux that update mode and lane-flip bits in the chip's general register.

## Important APIs, Types, and Functions

`struct tusb1046_priv` stores I2C client, switch/mux handles, and a mutex protecting the general register. Main functions are `tusb1046_mux_set()`, `tusb1046_switch_set()`, `tusb1046_i2c_probe()`, and `tusb1046_i2c_remove()`.

## Control Flow

Probe allocates state, initializes the mutex, registers a Type-C switch and mux on the device fwnode, and stores client data. Mux set rejects non-DP modal SVIDs, reads the general register, replaces CTLSEL bits for USB3, four-lane DP, USB3 plus two-lane DP, or disabled safe/default state, and writes back. Switch set reads the same register, sets or clears FLIPSEL for reverse orientation, and writes back. Remove unregisters switch/mux and destroys the mutex.

## State and Persistence Behavior

The driver does not cache mode/orientation. The chip register holds current state, and a mutex serializes read-modify-write sequences. No persistent storage exists.

## Dependencies and Integration Points

Dependencies include I2C SMBus, Type-C switch/mux APIs, DP altmode constants, and OF matching through `ti,tusb1046`.

## Risks and Test Signals

Risks include dereferencing `state->alt` when `state->mode >= TYPEC_STATE_MODAL` but no alt pointer is supplied, no regulator/reset handling, and unregister order differing from several other drivers. Test signals include switch and mux registration, general-register read/write failures, USB3/DP C/E/DP D/safe modes, reverse orientation FLIPSEL, unsupported modal SVID rejection, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/tusb1046.c -->
