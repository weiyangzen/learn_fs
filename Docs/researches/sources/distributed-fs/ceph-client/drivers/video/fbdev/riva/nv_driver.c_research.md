# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nv_driver.c

## Purpose
`nv_driver.c` is the RIVA driver's chip setup helper. It translates PCI/chipset state into initialized `RIVA_HW_INST` register-window pointers and display-head selection, detects VRAM size and maximum dot clock, and invokes the low-level RIVA configuration layer.

## Important APIs, types, and functions
- `riva_common_setup()` initializes MMIO sub-block pointers (`PRAMDAC0`, `PFB`, `PFIFO`, `PGRAPH`, `PEXTDEV`, `PTIMER`, `PMC`, `FIFO`, VGA I/O windows), selects CRTC/DAC register bases, autodetects flat panel/second CRTC where possible, and calls `RivaGetConfig()`.
- `riva_get_memlen()` returns VRAM size in KiB for NV3/NV4/NV10+ families, including integrated GeForce/nForce special cases that read host bridge PCI config.
- `riva_get_maxdclk()` derives a safe maximum dclk from memory/register characteristics.
- `riva_is_connected()`, `riva_is_second()`, and `riva_override_CRTC()` probe analog outputs and resolve second-head/forced CRTC decisions.

## Control flow
`fbdev.c` maps BARs and architecture-specific PRAMIN/PCRTC bases, then calls `riva_common_setup()`. This file fills the remaining register base pointers, determines VGA color/mono base from `MISCin()`, applies laptop flat-panel defaults, probes or forces second CRTC, selects active `PCIO`, `PCRTC`, `PRAMDAC`, and `PDIO` aliases, finalizes `flatPanel`, and lets `RivaGetConfig()` install architecture callbacks and FIFO object pointers.

## State and persistence behavior
The code mutates `struct riva_par` and embedded `RIVA_HW_INST`: MMIO pointers, `FlatPanel`, `SecondCRTC`, `forceCRTC`, chip memory/dclk characteristics, and two-head flags. No disk persistence exists. The output-detection routines temporarily write PRAMDAC probe registers, restore saved values, and delay for hardware settling.

## Dependencies and integration points
It includes `nv_type.h`, `rivafb.h`, and `nvreg.h`, uses PCI helper APIs for integrated chipset configuration, and depends on mapped control registers from `fbdev.c`. Its initialized pointers and callbacks are consumed by mode setting, acceleration, cursor, and state-save paths.

## Risks and test signals
Risks include brittle chipset ID heuristics, possible NULL PCI device results for integrated bridge lookups, invasive analog-output probing, forced CRTC misconfiguration, and divergent flat-panel defaults by platform. Test signals include correct VRAM reporting, correct framebuffer size, successful mode set on single-head and laptop panels, module parameter `forceCRTC` behavior, nForce/integrated memory sizing, and no register corruption after failed connector probes.
