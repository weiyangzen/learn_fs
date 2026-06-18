<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/maple.h -->
# sources/distributed-fs/ceph-client/include/linux/maple.h

## Purpose
This header defines the Sega Dreamcast Maple bus device/driver interface and command constants. It is unrelated to the kernel maple tree data structure.

## Important APIs, types, and functions
`enum maple_code` lists Maple command and response codes; `enum maple_file_errors` defines VMU/file error bits. `struct maple_buffer`, `struct mapleq`, `struct maple_devinfo`, `struct maple_device`, and `struct maple_driver` describe queued packets, device identity, driver binding, callbacks, and wait/busy state. Public APIs include `maple_getcond_callback`, `maple_driver_register`, `maple_driver_unregister`, `maple_add_packet`, and `maple_clear_dev`.

## Control flow
Maple device drivers register a `maple_driver` keyed by function bits. They can queue command packets with `maple_add_packet()` or schedule condition polling through `maple_getcond_callback()`. Completion routes through the device callback or file-error handler.

## State and persistence
State is runtime-only in each `struct maple_device`: current queue item, function mask, product strings, busy atomic, wait queue, polling interval, and embedded device-model object. Hardware state persists only on attached Maple peripherals.

## Dependencies and integration points
It includes platform-specific `<mach/maple.h>`, Linux device-model types, lists, wait queues, and atomics. It integrates with Dreamcast Maple bus core and device drivers for controllers, VMUs, and related peripherals.

## Risks and test signals
Risks include incorrect function matching, fixed-size product string truncation, queue lifetime bugs, unload while busy, and file-error handling for storage devices. Test driver bind/unbind, condition polling intervals, command retries, no-response handling, and file error callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/maple.h -->
