# sources/distributed-fs/ceph-client/drivers/char/agp/intel-agp.h

## Purpose

`intel-agp.h` is the shared Intel AGP/GTT register and PCI ID definition header used by `intel-agp.c` and `intel-gtt.c`. It centralizes chipset-specific PCI config offsets, MMIO offsets, stolen-memory bitfields, PGETBL controls, GTT PTE flags, and older Intel host/GPU device IDs.

## Important APIs, Types, And Functions

The file defines no functions or structs. Its important definitions include:

- AGP config offsets: `INTEL_APSIZE`, `INTEL_ATTBASE`, `INTEL_AGPCTRL`, `INTEL_NBXCFG`, and chipset-specific error/status registers.
- i810/i830/i915/G33/G4x/i965 GTT and memory control bits: `I810_PGETBL_CTL`, `I810_PTE_*`, `I830_GMCH_*`, `I855_GMCH_GMS_*`, `I965_PGETBL_*`, `G33_GMCH_SIZE_*`, `G4x_GMCH_SIZE_*`, and `GFX_FLSH_CNTL`.
- BAR indexes: `I810_GMADR_BAR`, `I810_MMADR_BAR`, `I915_MMADR_BAR`, and `I915_PTE_BAR`.
- Intel PCI device IDs not supplied by generic PCI headers for host bridges and integrated graphics.

## Control Flow

There is no runtime control flow. `intel-agp.c` uses the PCI config offsets and IDs while probing/configuring legacy AGP host bridges. `intel-gtt.c` uses the MMIO offsets, PTE flags, stolen memory masks, and integrated graphics IDs to choose GTT drivers and program/read global GTT entries.

## State And Persistence Behavior

The header stores no state. Its constants describe persistent hardware registers and ABI-level device IDs. Incorrect constants would cause runtime state in PCI config space or MMIO GTT tables to be read or written incorrectly.

## Dependencies And Integration Points

The header is included after `agp.h` in both Intel implementation files. It integrates with Linux PCI ID matching, AGP bridge setup, DRM Intel GTT exports, stolen-memory detection, chipset flush setup, and PGETBL restoration on resume.

## Risks And Edge Cases

Several values encode hardware quirks, such as i815 ATTBASE reserved bits, G33/G4x VT-enabled GTT sizes, and i965 high-address PTE packing. A wrong bit mask can produce silent aperture size misdetection or GTT corruption. The header mixes host bridge IDs and graphics device IDs, so additions must preserve which table consumes each macro.

## Test Signals

Compile both Intel AGP and GTT paths. Validate probe tables resolve the intended host/GPU pairs, GTT size detection matches hardware documentation, stolen-memory logs match BIOS setup, and PTE read/write helpers round-trip expected physical addresses on i830 and i965-style entries.
