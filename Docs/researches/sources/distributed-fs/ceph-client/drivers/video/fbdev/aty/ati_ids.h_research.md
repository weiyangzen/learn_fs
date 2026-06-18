# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/ati_ids.h

## Purpose
`ati_ids.h` is a local list of ATI PCI chip ID constants, historically kept in sync with XFree86. The comment says this list is currently only used by `radeonfb`.

## Important APIs, types, and functions
The file defines many `PCI_CHIP_*` macros mapping ATI ASIC and board identifiers to 16-bit device IDs. Families include RV/Radeon variants, RS integrated chipsets, R200/R300/R350/R360/R420/R423, Rage128, Mach32, and Mach64 IDs.

## Control flow
There is no executable control flow. Other source files include the header and use the constants in PCI ID tables, chip-family matching, or feature dispatch.

## State and persistence behavior
No runtime state is stored. The constants are compile-time identifiers.

## Dependencies and integration points
The integration point is compile-time use by ATI fbdev drivers, especially Radeon. Values must match PCI device IDs expected by the kernel PCI subsystem and hardware documentation.

## Risks and edge cases
The primary risk is stale or incorrect device ID definitions causing unsupported hardware to be missed or misclassified. Some macro names encode older naming conventions and letter suffixes, so maintainers must avoid duplicate or inconsistent constants when adding IDs.

## Test signals
Build users of the header, inspect generated PCI tables, and test device binding on representative ATI/Radeon/Mach64/Rage128 hardware IDs. Static checks can compare constants against authoritative PCI ID tables.
