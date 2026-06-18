# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_main.c

## Purpose

`stub_main.c` owns the USB/IP host module lifecycle, bus-id matching table, driver sysfs controls for selecting/rebinding devices, and common cleanup of host-side URB private data.

## Important APIs, Types, and Functions

`busid_table` holds up to 16 `struct bus_id_priv` entries protected by a global table lock and per-entry locks. `match_busid_store()` parses `add ` and `del ` commands. `rebind_store()` releases an exported device back to normal driver matching. `stub_free_priv_and_urb()` frees setup packets, buffers, SG lists, URBs, and `stub_priv` cache entries. `stub_device_cleanup_urbs()` kills and frees all pending/completed/free URB state. Module init creates the `stub_priv` slab cache, registers `stub_driver`, and creates sysfs files.

## Control Flow

Userspace writes bus IDs into `match_busid`; later USB core probing consults this table in `stub_dev.c`. Deleting a busid either clears an idle entry or marks active entries for removal. During module exit, the USB device driver is deregistered, causing disconnect callbacks, then selected devices may be rebound to ordinary drivers.

## State and Persistence Behavior

Bus-id selections, shutdown flags, device pointers, and interface counts are module-resident only. The slab cache persists while the module is loaded and backs all remote submit state.

## Dependencies and Integration Points

It depends on USB device-driver registration, sysfs driver attributes, device attach/rebind, scatterlist freeing, the `stub.h` contract, and the common USB/IP core.

## Risks and Test Signals

Risks include fixed `MAX_BUSID` capacity, newline/termination handling in busid parsing, lock ordering between table and entry locks, rebind behavior differing for built-in versus module builds, and cleanup of split SG requests. Test signals include add/del/rebind sysfs operations, table full handling, module unload with active exports, and leak checks around `stub_priv_cache`.
