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
