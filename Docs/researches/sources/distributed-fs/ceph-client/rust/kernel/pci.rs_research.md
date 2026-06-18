# sources/distributed-fs/ceph-client/rust/kernel/pci.rs

## Purpose
Defines Rust PCI bus abstractions: driver registration, PCI ID table construction, basic device metadata/resource helpers, context conversions, DMA-device integration, and refcount handling.

## APIs, Types, and Functions
`Adapter<T>` implements the generic driver registration traits for `bindings::pci_driver`. `module_pci_driver!` declares a PCI module. `DeviceId` provides constructors equivalent to `PCI_DEVICE`, `PCI_DEVICE_CLASS`, and class-plus-vendor matching. `Driver` requires an ID table and `probe`, with optional `unbind`. `Device<Ctx>` exposes vendor/device/revision/subsystem/class identifiers, BDF ID, BAR resource start/length, `enable_device_mem`, and `set_master`.

## Control Flow, State, and Persistence
Registration fills the C driver name, probe/remove callbacks, and ID table before calling `__pci_register_driver`; unregister calls `pci_unregister_driver`. Probe casts the C `pci_dev` to `Device<CoreInternal>`, maps the matched raw ID to sidecar info, runs `T::probe`, and stores pinned driver data in `drvdata`. Remove retrieves that data and calls `T::unbind`. Device references are persisted through C refcounts via `pci_dev_get` and `pci_dev_put`.

## Dependencies and Integration
Depends on `driver`, `device`, `device_id`, `container_of`, `ARef` support through `AlwaysRefCounted`, PCI generated bindings, and submodules `pci::id`, `pci::io`, and `pci::irq`. It integrates with module aliasing, the PCI core, devres-based resources, IRQ helpers, and DMA traits.

## Risks and Test Signals
Risks include mismatched struct offsets, invalid assumptions in casts from C callbacks, probe failures after partial resource setup, ID sidecar index corruption, and context misuse between normal/core/bound devices. Test signals include probe/remove lifecycle tests, modinfo PCI alias checks, `TryFrom<&device::Device>` negative tests, BAR range validation, and refcount/leak instrumentation around `ARef`.
