# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200se.c

## Purpose
Implements G200SE A/B server variants, including revision detection, revision-specific device limits, two PLL algorithms, high-priority memory arbitration setup, BMC-aware output, and device construction.

## Important APIs, types, and functions
- `mgag200_g200se_init_pci_options()` preserves SGRAM option bit while applying SE PCI options.
- `mgag200_g200se_init_registers()` writes SE DAC defaults.
- `mgag200_g200se_set_hiprilvl()` computes ECRT 0x06 priority by unique revision, mode clock, and format bpp.
- `mgag200_g200se_00_pixpllc_atomic_check/update()` supports older revisions with 160-320 MHz VCO and 25 MHz reference.
- `mgag200_g200se_04_pixpllc_atomic_check/update()` supports revision >= 0x04 with doubled clock and 800-1600 MHz VCO.
- `mgag200_g200se_init_unique_rev_id()` reads model/revision from MMIO 0x1e24.
- `mgag200_g200se_device_create()` selects info and funcs by PCI type and unique revision.

## Control flow
Factory setup initializes PCI options and resources, reads `unique_rev_id`, selects A/B and revision-specific max resolution/bandwidth/bug flags, selects old or rev04 PLL funcs, performs shared init, register init, VRAM probe, mode config, pipeline init, reset, and polling. Atomic enable uses a custom helper that updates PIXPLLC, computes hiprilvl, loads gamma, and enables display.

## State and persistence
`struct mgag200_g200se_device` persists `unique_rev_id`. Device info captures revision-specific max display, bandwidth, DDC bits, and `bug_no_startadd`. CRTC state carries PLL and format. Hardware state includes PCI options, DAC PLL registers, ECRT hiprilvl, and BMC-related mode reset flags.

## Dependencies and integration points
Uses shared mgag200 KMS, mode, DDC, and BMC VGA helpers. Dispatched for G200_SE_A and G200_SE_B PCI IDs.

## Risks
Revision selection is central; a zero or unexpected unique ID aborts probe or may choose conservative limits. Older revision A info sets `bug_no_startadd`, forcing start address zero. PLL algorithms differ significantly, and rev04 update uses a DAC 0x1a toggle plus sleep sequence. Hiprilvl thresholds affect display stability under memory pressure.

## Test signals
Test each known SE revision class, A and B PCI IDs, maximum mode validation, hiprilvl behavior at multiple bpp/clocks, BMC/no-EDID fallback modes, and start-address warnings on affected revisions.
