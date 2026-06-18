# sources/distributed-fs/ceph-client/rust/kernel/device.rs

## Purpose
`device.rs` is the Rust abstraction for Linux `struct device` and device-context typing. It provides reference-counted device handles, driver-private data storage and retrieval, firmware-node access, device logging macros, and helper macros for bus-specific device wrappers.

## Important APIs, Types, and Functions
`Device<Ctx = Normal>` is the transparent wrapper. Context marker types are `Normal`, `Bound`, `Core`, and `CoreInternal`, connected by `DeviceContext`. Key methods include `Device::get_device`, `Device::from_raw`, `Device::as_bound`, `Device<CoreInternal>::set_drvdata`, `drvdata_obtain`, `drvdata_borrow`, `Device<Bound>::drvdata`, `parent`, `fwnode`, and `name`. Macros include `impl_device_context_deref!`, `impl_device_context_into_aref!`, `dev_printk!`, and `dev_emerg!` through `dev_dbg!`.

## Control Flow
Bus abstractions create context-specific references during probe/remove callbacks. Probe stores pinned driver data with `set_drvdata`, which also writes a Rust `TypeId` into `struct device_private.driver_type`. Bound callbacks call `drvdata<T>()`, which checks for a stored pointer and matching `TypeId` before borrowing pinned data. Generic logging macros route to `Device::printk`, which calls `_dev_printk` when `CONFIG_PRINTK` is enabled.

## State and Persistence
The wrapper owns no independent state; it refers to kernel-managed `struct device` memory. Refcounting is delegated to `get_device` and `put_device` through `AlwaysRefCounted`. Driver-private data is a heap allocation stored in `dev_set_drvdata` and reclaimed by bus/driver infrastructure.

## Dependencies and Integration Points
This file integrates with `property::FwNode`, `ARef`, `ForeignOwnable`, `Opaque`, kernel device bindings, and bus abstractions such as PCI, platform, auxiliary, and DRM. The context types are used by DMA and devres APIs to require a bound device where unbind ordering matters.

## Risks
The most important risks are misuse of `from_raw`, selecting a stronger context than the current callback guarantees, and type mismatches in driver data. The `TypeId` storage uses unaligned reads/writes into a C field, so layout assumptions are guarded by a static assertion but still central. `as_bound` is unsafe because the caller must prove binding duration.

## Test Signals
Build bus wrappers using the context macros, probe/remove drivers that store and recover private data, verify wrong `drvdata<T>()` returns `EINVAL`, test parent and fwnode access, exercise logging macros under `CONFIG_PRINTK` and without it, and run refcount leak checks through repeated bind/unbind.
