<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ahci-remap.h -->
# sources/distributed-fs/ceph-client/include/linux/ahci-remap.h

## Purpose
`ahci-remap.h` defines register offsets and small helpers for AHCI remapped devices.

## Important APIs, types, and functions
Constants include `AHCI_VSCAP`, `AHCI_REMAP_CAP`, remap device class base `AHCI_REMAP_N_DCC`, remap MMIO offset/size, and `AHCI_MAX_REMAP`. `ahci_remap_dcc(i)` computes a remapped device class-code register offset. `ahci_remap_base(i)` computes the remapped device MMIO base relative to the AHCI BAR.

## Control flow
AHCI or PCI remap code indexes remap slots and uses these helpers to locate class-code and device windows.

## State and persistence behavior
No state is stored. The helpers interpret fixed hardware layout.

## Dependencies and integration points
It depends on size macros and integrates Intel-style AHCI remapping support with storage/PCI probing.

## Risks and test signals
Risks include out-of-range index use, wrong BAR-relative base assumptions, and class-code offset mismatch. Test signals include remap-capable AHCI hardware probe, slot enumeration, and bounds tests for `AHCI_MAX_REMAP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ahci-remap.h -->
