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
