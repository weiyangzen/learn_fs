# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/pci.c

## Purpose
Wraps libpci initialization and filtering for cpupower AMD hardware helpers and monitors.

## Important APIs, Types, and Functions
Exports `pci_acc_init` and `pci_slot_func_init`. `pci_acc_init` allocates a `pci_access`, configures a filter for domain/bus/slot/function/vendor/device where -1 means wildcard, initializes/scans the bus, and returns the first matching `pci_dev`. `pci_slot_func_init` targets root domain/bus by slot/function.

## Control Flow, State, and Persistence
The returned `pci_dev` remains owned by the `pci_access` object returned through `pacc`; callers must call `pci_cleanup`. If no device matches, the helper cleans up and returns NULL. No persistent data is written.

## Dependencies and Integration Points
Depends on libpci and x86-only compilation. Used by AMD boost-state and family 12h/14h idle monitor code.

## Risks and Test Signals
Only the first matching device is returned. The root-domain helper assumes domain 0/bus 0, which is not universal. Test systems with missing PCI access, nonzero domains, multiple matching devices, and callers correctly cleaning up `pci_access`.
