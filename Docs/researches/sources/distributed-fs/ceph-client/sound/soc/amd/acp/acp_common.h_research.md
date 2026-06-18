# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp_common.h

## Purpose
`acp_common.h` centralizes numeric AMD ACP PCI revision IDs used across PCI, platform, machine, and SoundWire code.

## Important APIs, Types, and Functions
It defines `ACP_RN_PCI_ID`, `ACP_VANGOGH_PCI_ID`, `ACP_RMB_PCI_ID`, `ACP63_PCI_ID`, `ACP70_PCI_ID`, `ACP71_PCI_ID`, and `ACP72_PCI_ID`.

## Control Flow
There is no executable control flow. Other files switch on these constants to select resources, DAI arrays, clock programming, platform component names, and DMA window mappings.

## State and Persistence
The header owns no state.

## Dependencies and Integration Points
It is included by `amd.h`, `acp-mach.h`, and revision-specific platform drivers. The values must match PCI revision values observed in `struct pci_dev->revision` and SoundWire mach params.

## Risks
A wrong constant cascades through platform matching, DMA mapping, and machine selection. Adding a new ACP revision requires updating switch statements and ACPI tables beyond this header.

## Test Signals
Build and runtime probe for each known revision are the main signals. Unsupported-revision logs in PCI/platform drivers help detect missing additions.
