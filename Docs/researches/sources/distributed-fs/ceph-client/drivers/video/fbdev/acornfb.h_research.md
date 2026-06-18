# sources/distributed-fs/ceph-client/drivers/video/fbdev/acornfb.h

## Purpose
`acornfb.h` provides private data structures and VIDC20 register constants for the Acorn framebuffer driver. It defines palette encodings, mode/timing helper records, per-device state, and bitfields used when composing VIDC20 control, external control, and data control register writes.

## Important APIs, Types, and Functions
`struct vidc20_palette`, `struct vidc_palette`, and `union palette` model VIDC20 and older VIDC palette encodings. `struct acornfb_par` is the driver's private state container, holding the device pointer, framebuffer end address, DRAM/VRAM metadata, palette size, monitor type, VRAM/DPMS flags, a 256-entry palette cache, and a 16-entry pseudo-palette. `struct vidc_timing` carries computed horizontal/vertical VIDC register values, control bits, and VIDC20 PLL control. `struct modey_params` and `struct modex_params` describe mode tables used by Acorn-specific timing helpers.

The macro set defines `VIDC_PALETTE_SIZE`, `VIDC_NAME`, `EXTEND8`, `EXTEND4`, and many VIDC20 constants such as `VIDC20_CTRL_*`, `VIDC20_ECTL_*`, and `VIDC20_DCTL_*`.

## Control Flow
The header has no executable control flow. It is included by `acornfb.c`; if `HAS_VIDC20` is defined it pulls in `asm/hardware/iomd.h` and exposes VIDC20-specific constants. The C file fills `struct vidc_timing`, writes fields using the register bit masks, and stores palette entries in the union representation before issuing `vidc_writel()` calls.

## State and Persistence
The header defines layouts for runtime state but does not allocate state itself. Persistent runtime values are stored by `acornfb.c` in `current_par` and `current_vidc`. Register bit definitions persist into compiled code as constants.

## Dependencies and Integration Points
The header depends on Acorn platform compile-time symbols, especially `HAS_VIDC20`, and on type definitions from Linux/architecture headers included before or by the including C file. It is tightly coupled to VIDC/VIDC20 hardware programming and to helper code that computes VIDC20 PLL and default control values.

## Risks and Edge Cases
The palette structs use C bitfields, which are sensitive to compiler and endianness assumptions; this is acceptable only because the code targets the matching Acorn architecture/hardware representation. `struct acornfb_par` statically sizes its palette array to `VIDC_PALETTE_SIZE`, so non-VIDC20 builds must still provide a coherent palette size definition path. Register constants should be updated only with hardware documentation because wrong bit assignments can disable output, change bus width, or alter sync polarity.

## Test Signals
Header-level validation is indirect: compile VIDC20 and non-VIDC20 configurations, confirm register constants generate the expected writes in `acornfb_set_timing()`, and test palette programming for mono, pseudocolor, 16bpp directcolor, and 32bpp directcolor modes on real hardware or a hardware-aware emulator.
