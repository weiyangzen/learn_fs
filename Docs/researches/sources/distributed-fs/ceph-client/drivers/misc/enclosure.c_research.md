# sources/distributed-fs/ceph-client/drivers/misc/enclosure.c

## Purpose
Generic Linux enclosure-services class implementation. It lets storage/enclosure drivers register an enclosure, publish component devices, link real devices to enclosure slots, and expose component state/control through sysfs.

## Important APIs, Types, And Functions
Exported APIs include `enclosure_find()`, `enclosure_for_each_device()`, `enclosure_register()`, `enclosure_unregister()`, `enclosure_component_alloc()`, `enclosure_component_register()`, `enclosure_add_device()`, and `enclosure_remove_device()`. Internal helpers manage sysfs link names, component name uniqueness, device release, and class/component attributes. Callback operations come from `struct enclosure_component_callbacks` in `linux/enclosure.h`.

## Control Flow
Module init registers the `enclosure` class. A provider calls `enclosure_register()` to allocate an enclosure device with a flexible component array, register it, initialize component sentinel values, and add it to a global list. Components are allocated by number, named uniquely, registered as child devices, and later linked to real devices. Sysfs getters call optional provider callbacks to refresh fields before emitting values. Setters parse userspace values and call optional callbacks. Unregister removes the enclosure from the global list, unregisters components, replaces callbacks with null callbacks, and unregisters the parent class device.

## State, Persistence, And Dependencies
State is in kernel objects only: global enclosure list, each enclosure component array, per-component status/fault/active/locate/power/type/slot fields, and sysfs links. Persistent hardware state lives behind provider callbacks. Dependencies include device core, sysfs, list/mutex primitives, module exports, and callback contracts from enclosure providers.

## Integration Points
The class appears under `/sys/class/enclosure`. Components expose `fault`, `status`, `active`, `locate`, `power_status`, `type`, and `slot`; enclosures expose `components` and optional `id`. Bidirectional sysfs links connect component class devices to real devices.

## Risks
`enclosure_for_each_device()` holds the global mutex across provider callbacks, so sleeping or reentrant callbacks can stall registration/removal. Several setters use `simple_strtoul()` and accept loose numeric input. Status/type arrays assume enum values are valid. Providers must manage callback lifetime carefully; unregister swaps callbacks late to prevent use-after-free after component removal starts. Duplicate component names are handled, but long names are truncated to 64 bytes before suffixing.

## Test Signals
Test duplicate component names, repeated add/remove of linked real devices, callback absence and callback error semantics, sysfs state parsing, reference release through device unregister, `enclosure_find()` iteration with start references, and unregister while userspace reads component attributes.
