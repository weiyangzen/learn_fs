# sources/distributed-fs/ceph-client/rust/kernel/pci/irq.rs

## Purpose
Wraps PCI IRQ vector allocation and converts allocated vectors into generic Rust IRQ registration objects.

## APIs, Types, and Functions
`IrqType` maps INTx, MSI, and MSI-X to kernel flags. `IrqTypes` is a bitset builder with `all` and `with`. `IrqVector<'a>` ties a vector index to the bound PCI device that owns it and implements `TryInto<IrqRequest<'a>>`. `Device<Bound>` exposes `alloc_irq_vectors`, `request_irq`, and `request_threaded_irq`.

## Control Flow, State, and Persistence
`IrqVectorRegistration::register` calls `pci_alloc_irq_vectors`, builds an inclusive range from vector 0 to count-1, and registers a guard with devres. The guard holds an `ARef<Device>` and frees all PCI IRQ vectors on drop. Request helpers convert a vector to a concrete IRQ number with `pci_irq_vector` inside a `pin_init_scope`, then construct the generic IRQ registration.

## Dependencies and Integration
Depends on PCI device wrappers, `devres`, generic `irq` request/registration APIs, `CStr`, and PCI IRQ allocation bindings. It integrates with bound PCI drivers that need MSI/MSI-X/INTx allocation before registering interrupt handlers.

## Risks and Test Signals
Risks include allowing `min_vecs == 0` even though range construction assumes `count >= 1`, passing a vector from one allocation after vectors were freed, devres registration failure after allocation, and mismatched handler lifetimes. Test signals include vector allocation failure injection, min/max boundary tests, devres cleanup checks, threaded and non-threaded handler registration smoke tests, and validation that stale vectors cannot be constructed by safe APIs.
