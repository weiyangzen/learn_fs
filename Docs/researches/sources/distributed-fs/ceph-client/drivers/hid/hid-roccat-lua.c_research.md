# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-lua.c

## Purpose

`hid-roccat-lua.c` is a minimal Roccat Lua mouse driver exposing a single control binary sysfs file for CPI, button, and light settings.

## Important APIs, Types, and Functions

- `lua_sysfs_read()` and `lua_sysfs_write()`: exact-size feature-report helpers for the Lua sysfs file.
- `LUA_BIN_ATTRIBUTE_RW(control, CONTROL)`: generates the eight-byte `control` binary attribute.
- `lua_create_sysfs_attributes()` and `lua_remove_sysfs_attributes()`: create/remove the attribute directly on the USB interface device.
- `lua_init_specials()` and `lua_remove_specials()`: allocate/free `struct lua_device` and initialize its mutex.
- `lua_probe()` and `lua_remove()`: parse/start/stop HID and install/remove sysfs state.

## Control Flow

Probe requires USB, parses and starts HID, allocates Lua state, initializes the lock, and creates `control` on the USB interface kobject rather than via a Roccat class. Reads and writes require offset zero and count exactly eight bytes; reads use `roccat_common2_receive()` while writes use `roccat_common2_send()` without status polling.

## State and Persistence Behavior

Only a mutex persists in `struct lua_device`. All device configuration is firmware state accessed through the eight-byte control report. No Roccat char device is created and no raw events are handled.

## Dependencies and Integration Points

The file uses HID/USB, Roccat common feature-report receive/send helpers, direct sysfs bin file creation, and Lua constants from `hid-roccat-lua.h`.

## Risks and Edge Cases

- Sysfs files are created directly on the USB interface, so the kobject traversal differs from class-backed Roccat drivers.
- Writes do not use common status polling.
- Failure after `hid_hw_start()` is handled by `hid_hw_stop()`, but sysfs creation failure must ensure allocated state is freed, which this file does.
- Exact-size access may surprise generic sysfs readers.

## Test Signals

Test creation/removal of the interface `control` bin file, exact eight-byte read/write behavior, concurrent accesses through `lua_lock`, write failure propagation, and probe cleanup after sysfs creation failure.
