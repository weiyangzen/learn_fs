# sources/distributed-fs/ceph-client/include/linux/transport_class.h

## Purpose
Defines the generic transport class abstraction used by bus/storage transports to add class devices and attribute containers around lower-level devices.

## Important APIs, Types, And Functions
Key types are `struct transport_class`, `struct anon_transport_class`, and `struct transport_container`. Macros `DECLARE_TRANSPORT_CLASS()` and `DECLARE_ANON_TRANSPORT_CLASS()` initialize common class/container definitions. APIs include `transport_setup_device()`, `transport_add_device()`, `transport_configure_device()`, `transport_remove_device()`, `transport_destroy_device()`, register/unregister helpers, and class register/unregister functions.

## Control Flow
`transport_register_device()` calls setup, add, and destroys on add failure. `transport_unregister_device()` removes then destroys. Container registration is delegated to `attribute_container_register()` and unregister bugs out if the container cannot be unregistered.

## State, Persistence, And Dependencies
Runtime state is in embedded `struct class` and `attribute_container` objects, plus optional statistics/encryption attribute groups. Dependencies are device model, bug handling, and attribute containers.

## Integration Points
Used by SCSI and other transport-layer class implementations to attach transport-specific sysfs attributes and lifecycle hooks to generic devices.

## Risks And Test Signals
Risks include setup/add failure cleanup gaps, unregistering active attribute containers, incorrect match callbacks for anonymous classes, and sysfs attribute lifetime bugs. Test signals include device add/remove error injection, sysfs attribute presence, class unregister lockdep, and transport-specific hotplug tests.
