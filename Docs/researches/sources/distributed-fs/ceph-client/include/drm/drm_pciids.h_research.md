# sources/distributed-fs/ceph-client/include/drm/drm_pciids.h

## Purpose
`drm_pciids.h` provides a large macro, `radeon_PCI_IDS`, containing legacy AMD/ATI Radeon PCI device IDs and associated driver chip-family flags. It is a data include used to build Radeon PCI ID tables.

## Important APIs, types, and functions
There are no functions or structs. The file defines `radeon_PCI_IDS` as a comma-separated list of PCI table initializer rows ending in `{0, 0, 0}`. Each row supplies vendor ID `0x1002`, device ID, wildcard subsystem IDs, class fields, and flag combinations such as `CHIP_R100`, `CHIP_RV380`, `CHIP_KAVERI`, `RADEON_IS_MOBILITY`, `RADEON_IS_IGP`, `RADEON_NEW_MEMMAP`, `RADEON_SINGLE_CRTC`, and `RADEON_IS_IGPGART`.

## Control flow
At compile time, Radeon driver code includes this macro inside a PCI device table definition. Runtime probe matching is then handled by the PCI core. Matching entries communicate chip family and quirks through the `driver_data` flag field used by the Radeon driver after probe.

## State and persistence
State is static build-time table data. It persists only as compiled module/kernel PCI match metadata and has no mutable runtime state in this header.

## Dependencies and integration points
The including source must define or include `PCI_ANY_ID`, chip-family constants, and Radeon flag constants. The resulting table integrates with PCI module aliases, device probing, and Radeon family-specific initialization paths.

## Risks and test signals
Risks include wrong chip family flags, missing mobile/IGP/new-memmap quirks, duplicate or stale IDs, macro syntax errors from trailing commas or line continuations, and table drift against upstream PCI IDs. Test signals include Radeon module alias generation, builds of the including driver, representative probe on old desktop/mobile/IGP families, comparison against known PCI ID databases, and regression checks that sentinel termination remains intact.
