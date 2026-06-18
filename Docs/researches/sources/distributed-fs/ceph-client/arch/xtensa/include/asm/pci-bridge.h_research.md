<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci-bridge.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci-bridge.h

## Purpose
Defines legacy Xtensa PCI host-bridge data structures and helper declarations.

## Important APIs, Types, And Functions
Declares `pciauto_bus_scan`, defines `struct pci_space`, `struct pci_controller`, and inline `pcibios_init_resource`.

## Control Flow
PCI platform code fills `pci_controller` with ops, config address/data pointers, IO/memory resources, resource placement windows, and IRQ mapping callback. `pcibios_init_resource` initializes resource fields.

## State And Persistence
Runtime state is host bridge controller structures and resource windows maintained by PCI platform code.

## Dependencies And Integration Points
Depends on Linux PCI core types, OF/platform PCI setup, and architecture-specific PCI host drivers.

## Risks And Edge Cases
The controller model supports one IO range and three memory ranges; more complex host bridges need extensions. IRQ mapping callback must match board wiring.

## Test Signals
PCI enumeration on Xtensa platforms, BAR assignment, IRQ routing, and resource conflict checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci-bridge.h -->
