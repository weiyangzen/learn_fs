# sources/distributed-fs/ceph-client/drivers/char/agp/agp.h

## Purpose
This private AGPGART header defines the backend's internal bridge structures, driver callback table, aperture-size descriptors, register constants, helper prototypes, and shared globals used by generic and chipset-specific AGP drivers.

## Important APIs, Types, and Functions
Important types are `enum aper_size_type`, `struct gatt_mask`, aperture-size structs, `struct agp_bridge_driver`, `struct agp_bridge_data`, and `struct agp_device_ids`. The driver callback table covers size fetch, configure/cleanup, AGP enable, TLB flush, memory masking, cache flush, GATT creation/free, insertion/removal, type allocation, page allocation/destruction, and memory type conversion.

Exports/prototypes include bridge lifecycle (`agp_alloc_bridge`, `agp_add_bridge`, `agp_remove_bridge`, `agp_put_bridge`), generic memory/GATT operations, AGP enable helpers, version/mode helpers, cache flush, user memory allocation helpers, AGP3 helpers, and globals `agp_bridge`, `agp_off`, and `agp_try_unsupported_boot`.

## Control Flow
Chipset drivers allocate and fill `struct agp_bridge_data` with a `struct agp_bridge_driver`; backend initialization calls the callback table in a generic sequence. Generic ioctl/memory code uses the same callbacks for per-chipset operations.

## State and Persistence Behavior
The header describes persistent bridge state: current/previous aperture size, PCI device, GATT pointers and bus addresses, scratch page, mode, key list, memory counters, capability offsets, mapped memory list/lock, and chipset private data.

## Dependencies and Integration Points
It depends on architecture AGP cache helpers and Linux PCI/AGP public headers. It is the central integration point between `backend.c`, generic AGP code, and all chipset drivers.

## Risks
The shared global `agp_bridge` is a legacy singleton shortcut even though a list of bridges exists; drivers using it can misbehave with multiple bridges. Callback contracts are implicit and easy to violate, especially scratch-page masking, GATT address ownership, cache flushing, and aperture-size pointer types. Register constants must match AGP specs/chipsets.

## Test Signals
Compile all chipset drivers, verify callback tables populate required methods, and run AGP memory allocation/bind/unbind tests on each bridge class with debug options to catch type/size mismatches.
