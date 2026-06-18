# sources/distributed-fs/ceph-client/rust/kernel/platform.rs

## Purpose
Defines Rust platform-bus driver registration, platform device wrappers, memory resource lookup, IRQ request helpers, DMA integration, context conversion, and refcount handling.

## APIs, Types, and Functions
`Adapter<T>` bridges `platform::Driver` to `bindings::platform_driver`. `module_platform_driver!` declares a module. `Driver` supports optional OF and ACPI ID tables plus `probe` and optional `unbind`. `Device<Ctx>` exposes memory `resource_by_index`, `resource_by_name`, bound-only `io_request_by_index/name`, IRQ lookup by index/name with optional variants, and generated request helpers for regular and threaded IRQ registrations.

## Control Flow, State, and Persistence
Registration fills platform driver name, probe/remove callbacks, OF and ACPI match tables, then calls `__platform_driver_register`; unregister calls `platform_driver_unregister`. Probe casts the C platform device, resolves optional sidecar match info through the generic driver adapter, initializes pinned driver state, and stores it in `drvdata`. Remove retrieves pinned state and calls `unbind`. Resource and IRQ helpers query the C platform core and convert negative IRQ returns into `Error`.

## Dependencies and Integration
Depends on `acpi`, `of`, `device`, `driver`, `io::Resource`, `IoRequest`, generic IRQ APIs, `container_of`, generated platform bindings, and `AlwaysRefCounted`. It integrates with OF/ACPI matching, devres-backed MMIO requests, IRQ registration, DMA traits, and module driver macros.

## Risks and Test Signals
Risks include incorrect match-info resolution when both OF and ACPI tables exist, storing/borrowing wrong drvdata type, optional IRQ APIs still surfacing negative errors that callers must interpret, resource pointers outliving the platform device, and context misuse around `Bound`. Test signals include OF and ACPI probe tests, resource-by-name/index tests, optional IRQ absence tests, regular/threaded IRQ registration smoke tests, and refcount checks for `get_device`/`platform_device_put`.
