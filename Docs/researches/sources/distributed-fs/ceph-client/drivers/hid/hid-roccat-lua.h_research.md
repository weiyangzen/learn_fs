# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-lua.h

## Purpose

`hid-roccat-lua.h` defines the Lua control report size, command ID, and per-device mutex state.

## Important APIs, Types, and Functions

- `LUA_SIZE_CONTROL = 8`: fixed binary sysfs payload size.
- `LUA_COMMAND_CONTROL = 3`: feature report command ID.
- `struct lua_device`: contains `lua_lock` for serialized USB transfers.

## Control Flow

The C file's generated sysfs callbacks use the size and command constants to issue feature-report transfers.

## State and Persistence Behavior

The header defines only the in-memory lock; actual Lua settings persist in device firmware.

## Dependencies and Integration Points

It depends on Linux types and is consumed only by `hid-roccat-lua.c`.

## Risks and Edge Cases

The ABI has no named packed payload fields, so validation and documentation of the eight-byte control report are limited.

## Test Signals

Tests should assert the sysfs file size is eight bytes and that reads/writes use command ID 3.
