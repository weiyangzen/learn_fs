<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/legacy.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/legacy.c

## Purpose
`legacy.c` handles traditional PCI bus probing for x86 systems that do not use ACPI root scanning or another platform-specific method. It scans bus 0, discovers peer root buses from `pcibios_last_bus`, initializes IRQ routing, and calls the generic pcibios init path.

## Important APIs, types, and functions
`pci_legacy_init()` probes primary PCI hardware. `pcibios_scan_specific_bus()` tests a bus for any valid vendor ID and scans it as a root bus. `pcibios_fixup_peer_bridges()` iterates up to `pcibios_last_bus`. `pci_subsys_init()` is the `subsys_initcall()` that invokes `x86_init.pci.init()`, legacy fallback, peer scanning, `x86_init.pci.init_irq()`, and `pcibios_init()`.

## Control flow
At subsystem init, platform PCI init is tried first. A nonzero return requests legacy probing. Legacy probing scans root bus 0 using `pcibios_scan_root()`. If BIOS last-bus data indicates possible peer bridges, each bus is probed by reading vendor ID at device/function strides; Jailhouse paravirtual systems scan every function instead of every slot. IRQ initialization and final PCI BIOS setup run after bus discovery.

## State and persistence behavior
The file holds no private persistent state. It consumes `pcibios_last_bus` and mutates global PCI bus lists through root-bus scans. `raw_pci_ops` availability gates whether any probing can happen.

## Dependencies and integration points
It integrates with `x86_init.pci`, Jailhouse paravirtual detection, raw PCI config access, `pcibios_scan_root()`, IRQ initialization, and generic PCI subsystem startup.

## Risks and edge cases
Peer-bus discovery is heuristic and depends on reliable `pcibios_last_bus`. Reading config space on absent devices must be safe for the installed access mechanism. Jailhouse changes scan stride because virtual PCI topologies may expose functions in ways normal slot-based scanning would miss.

## Test signals
Validate with legacy BIOS systems, Jailhouse guests, systems with peer host bridges, and no-PCI systems. Logs should show primary probing, discovered peer buses, or a clear "does not support PCI" message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/legacy.c -->
