# sources/distributed-fs/ceph-client/drivers/usb/typec/pd.c

## Purpose

`pd.c` implements the USB Power Delivery class sysfs model. It creates `/sys/class/usb_power_delivery/pdN` devices, optional capability subdevices, and child PDO devices exposing decoded fixed, variable, battery, PPS, and SPR AVS PDO fields.

## Important APIs, Types, and Functions

`struct pdo` wraps each PDO as a device with `object_position` and raw `u32 pdo`. Exported APIs are `usb_power_delivery_register()`, `usb_power_delivery_unregister()`, `usb_power_delivery_find()`, `usb_power_delivery_register_capabilities()`, `usb_power_delivery_unregister_capabilities()`, `usb_power_delivery_link_device()`, and `usb_power_delivery_unlink_device()`. Attribute groups decode PD bitfields via helpers from `<linux/usb/pd.h>`, with separate device types for source/sink fixed, variable, battery, PPS APDO, and SPR AVS APDO.

## Control Flow

Class init registers the `usb_power_delivery` class and exit destroys the IDA then unregisters the class. Registering a PD object allocates an ID, stores revision/version, initializes the class device, and publishes revision/version attributes. Capability registration creates a `source-capabilities` or `sink-capabilities` child, then iterates `desc->pdo[]` until `PDO_MAX_OBJECTS` or zero and calls `add_pdo()` for each supported PDO. Unregister walks child PDO devices before unregistering the capability device. Link/unlink add or remove a `usb_power_delivery` sysfs symlink and hold paired references while the link exists.

## State and Persistence Behavior

The class keeps a global `IDA` for stable runtime names. All PD/capability/PDO objects are device-model allocations released through `.release` callbacks; no negotiated values are persisted across unregister. PDO content is immutable after device registration.

## Dependencies and Integration Points

It depends on Linux device/class/sysfs APIs, USB PD encoding helpers, and Type-C role helpers. TCPM and UCSI use it to expose local and partner PD support, while Type-C class code links PD devices to ports and partners.

## Risks and Test Signals

Risks include only supporting PPS and SPR AVS APDO types, silently skipping unknown APDOs, requiring zero-terminated PDO arrays, link reference leaks if callers do not unlink, and sysfs ABI correctness for units and first-fixed-PDO visibility rules. Test signals include class init/exit, PD object registration with and without version, source and sink capability trees, each PDO type's attributes, unknown APDO warnings, unregister cleanup of children, and symlink reference balancing.
