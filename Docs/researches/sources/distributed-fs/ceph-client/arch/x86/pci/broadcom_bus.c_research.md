# sources/distributed-fs/ceph-client/arch/x86/pci/broadcom_bus.c

## Purpose
Extracts host bridge bus and resource windows from Broadcom/ServerWorks CNB20LE bridges when ACPI is unavailable. It populates `pci_root_infos` so generic x86 PCI root scanning can use hardware-derived resources.

## Important APIs and functions
- `cnb20le_res()` reads bus range and IO/memory windows for one CNB20LE bridge function and records them in a `pci_root_info`.
- `broadcom_postcore_init()` detects the ServerWorks LE host bridge on bus 0 slot 0 and runs the two-function resource probe.

## Control flow
At postcore init, the code exits if ACPI is enabled and has a root pointer because ACPI should provide host bridge information. Otherwise it reads vendor/device ID from bus 0 slot 0 function 0. On ServerWorks LE, it calls `cnb20le_res()` for functions 0 and 1. Each call reads first/last bus numbers, creates a root info entry, adds legacy IDE IO ranges for bus 0, reads non-prefetchable memory, prefetchable memory, and IO windows from bridge registers, and logs the resulting windows.

## State and persistence
Persistent state is added to the shared `pci_root_infos` list. No teardown path is implemented because these early host bridge records live for the boot lifetime.

## Dependencies and integration points
Depends on early direct PCI reads, DMI/ACPI availability checks, ServerWorks PCI IDs, and `bus_numa.c` allocation/resource helpers. `common.c` or `acpi.c` later consumes the recorded resources through `x86_pci_root_bus_resources()`.

## Risks and edge cases
The code is a hardware quirk for old systems and uses hard-coded assumptions, including undocumented legacy IDE ports and two bridge functions. It deliberately avoids running when ACPI is present. Incorrect register values can create bad root windows, but this only affects the narrow CNB20LE fallback path.

## Test signals
On affected systems without ACPI, boot logs should show CNB20LE host bridge ranges and PCI devices should receive correct IO/MMIO resources. On ACPI systems, this file should be silent and inactive.
