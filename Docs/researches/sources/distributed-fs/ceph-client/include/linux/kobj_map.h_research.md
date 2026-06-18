# sources/distributed-fs/ceph-client/include/linux/kobj_map.h

## Purpose

`kobj_map.h` declares the device-number-to-kobject mapping API used by character and block device lookup code. It lets subsystems register probe ranges and resolve `dev_t` values to kobjects. The source was read as a complete 20-line file.

## Important APIs, Types, and Functions

The header defines `kobj_probe_t`, opaque `struct kobj_map`, and APIs `kobj_map()`, `kobj_unmap()`, `kobj_lookup()`, and `kobj_map_init()`.

## Control Flow

Subsystems initialize a map, register a range with a module pointer, probe callback, optional lock callback, and private data, then lookup paths call `kobj_lookup()` with a device number and receive a kobject plus partition/index information through the integer pointer.

## State and Persistence Behavior

Map state lives in an allocated `struct kobj_map` implementation. Registered ranges persist until explicitly unmapped. The module pointer participates in owner lifetime management in the implementation.

## Dependencies and Integration Points

It depends on mutex declarations, kobjects, device numbers, and modules. It integrates with block/char device open paths and sysfs object lookup.

## Risks and Edge Cases

Overlapping ranges and stale module/private pointers are primary risks. Probe callbacks must be safe under lookup locking and handle missing devices. Unmap must exactly match registered ranges.

## Test Signals

Device lookup tests, register/unregister range tests, overlapping range handling, module unload races, and invalid `dev_t` lookup tests are useful.
