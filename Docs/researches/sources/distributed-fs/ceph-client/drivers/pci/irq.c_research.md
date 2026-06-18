# sources/distributed-fs/ceph-client/drivers/pci/irq.c

## Purpose
Provides generic PCI IRQ utility functions: request/free wrappers around PCI interrupt vectors, INTx swizzling/mapping, runtime IRQ assignment, and shared INTx mask/unmask helpers.

## Important APIs, Types, and Functions
Exported APIs are `pci_request_irq()`, `pci_free_irq()`, `pci_common_swizzle()`, `pci_check_and_mask_intx()`, and `pci_check_and_unmask_intx()`. Other core functions include `pci_swizzle_interrupt_pin()`, `pci_get_interrupt_pin()`, `pci_assign_irq()`, and weak arch hooks `pcibios_penalize_isa_irq()`, `pcibios_alloc_irq()`, and `pcibios_free_irq()`.

## Control Flow
`pci_request_irq()` formats a device IRQ name, gets the Linux IRQ through `pci_irq_vector()`, and installs a shared threaded IRQ, adding `IRQF_ONESHOT` when only a thread handler is supplied. `pci_free_irq()` frees the IRQ and the allocated name. Swizzling walks bridges to root, applying slot-based INTx rotation unless ARI forces slot zero. `pci_assign_irq()` asks the host bridge's swizzle/map callbacks for a platform IRQ and writes it to `PCI_INTERRUPT_LINE`. INTx masking does one locked config dword read of Command+Status, checks pending state, and only toggles `PCI_COMMAND_INTX_DISABLE` when pending state matches the requested mask/unmask operation.

## State and Persistence Behavior
IRQ assignment writes `dev->irq` and the device's Interrupt Line config byte. `pci_request_irq()` allocates a persistent handler name freed by `pci_free_irq()`. INTx mask state persists in PCI Command until changed again.

## Dependencies and Integration Points
Depends on IRQ core, MSI/vector helper `pci_irq_vector()`, PCI host bridge `map_irq`/`swizzle_irq`, config-space bus ops, and the global raw `pci_lock`.

## Risks
`dev_id` must be unique and non-NULL for shared IRQs. The INTx check/mask helper assumes Command and Status can be read atomically as one dword at aligned offsets, enforced by build checks. Swizzling correctness depends on bridge topology and ARI state. Drivers must disable device interrupt generation before `pci_free_irq()`.

## Test Signals
Request/free MSI, MSI-X, and INTx vectors; threaded-only handlers; IRQ name allocation failure; INTx swizzle behind multiple bridges with and without ARI; platform IRQ assignment; shared INTx mask/unmask with pending and non-pending status.
