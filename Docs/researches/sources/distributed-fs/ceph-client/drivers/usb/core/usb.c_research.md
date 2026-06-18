<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/usb.c

## Purpose
`usb.c` is the host-side USB core library and module lifecycle file. It is not a hardware driver; it provides exported helpers for endpoint discovery, interface/configuration lookup, USB device/interface references, reset locking, DMA-safe buffer allocation, descriptor parsing, periodic endpoint sizing, USB bus notifications, debugfs exposure, and usbcore initialization/cleanup.

## Important APIs, types, and functions
Important exported APIs include `usb_disabled`, `usb_find_common_endpoints`, `usb_find_common_endpoints_reverse`, `usb_check_bulk_endpoints`, `usb_check_int_endpoints`, `usb_find_alt_setting`, `usb_ifnum_to_if`, `usb_altnum_to_altsetting`, `usb_find_interface`, `usb_for_each_dev`, `usb_alloc_dev`, `usb_get_dev`, `usb_put_dev`, `usb_get_intf`, `usb_put_intf`, `usb_intf_get_dma_device`, `usb_lock_device_for_reset`, `usb_get_current_frame_number`, `__usb_get_extra_descriptor`, coherent/noncoherent DMA allocation helpers, and periodic payload helpers. Internal objects include `usb_device_type`, `usb_bus_nb`, and small callback argument structs used with the driver core bus walkers.

## Control flow
Endpoint helpers clear caller-provided result pointers, scan the active alternate setting, and return success only when every requested endpoint class/direction has been found. Device/interface lookup helpers walk the current configuration or global USB bus. `usb_alloc_dev` allocates and initializes a `struct usb_device`, takes an HCD reference, sets device core type/groups/node/name/topology strings, initializes ep0 and runtime PM fields, derives OF node and route information, applies authorization policy, and returns an attached but not enumerated device. Module initialization gates on `nousb`, initializes pool/debugfs/ACPI/bus notifier/major class/usbfs/devio/hub/generic driver in order, and unwinds in reverse on failure. Exit releases quirks and unregisters generic driver, major, usbfs, devio, hub, class, notifier, bus, ACPI, debugfs, and the bus IDR.

## State and persistence behavior
Persistent runtime state is kernel in-memory state: module parameters `nousb` and `autosuspend`, device references, sysfs/debugfs nodes, PM autosuspend delay, stable `devpath`/route strings, authorization flags, endpoint state, and HCD references. The file does not persist data to disk. It relies on driver-core reference counting for lifetime and on `usb_release_dev` to destroy configurations, BOS descriptors, OF nodes, HCD references, strings, and the device allocation.

## Dependencies and integration points
This file integrates with `hub.h`, `trace.h`, USB HCD APIs, usbfs, sysfs attribute creation/removal, ACPI, OF, debugfs, DMA mapping, runtime/system PM, bus/class registration, and the generic USB device driver. It is the utility surface used by class and interface drivers to avoid open-coding descriptor scans, refcount operations, and DMA buffer management.

## Risks
The main risks are lifetime/refcount mistakes around `bus_find_device` and `put_device`, reset-lock deadlocks if callers ignore `usb_lock_device_for_reset` semantics, descriptor parsing rejecting malformed but present extra descriptors, endpoint matching using first/last semantics that may not match a quirky device, route truncation for deep paths, and init unwinding bugs because many subsystems are registered in sequence. DMA helper callers must pass matching size/address/table/direction values on free.

## Test signals
Useful signals are USB core boot with and without `nousb`, module init failure injection, device enumeration under hubs and root hubs, sysfs add/remove notification coverage, usbfs/debugfs `/sys/kernel/debug/usb/devices`, runtime/system suspend/resume, endpoint helper unit-style coverage with synthetic descriptors, malformed descriptor parsing tests, DMA API debug checks, and hotplug/disconnect stress tests watching for leaks or refcount warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb.c -->
