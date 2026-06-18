# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_regs.h

## Purpose

`rcar_du_regs.h` is the register map for the Renesas R-Car Display Unit (DU) driver. It provides offsets and bitfield macros for display control, timing generation, planes, palettes, capture, external sync, dual-output routing, PLLs, and color conversion blocks used by the rest of the R-Car DU KMS implementation.

## Important APIs, Types, and Functions

This file has no functions or persistent state. Its important API is the macro namespace: `DU0_REG_OFFSET` through `DU3_REG_OFFSET` locate DU channels; `DSYSR`, `DSMR`, `DSSR`, `DSRCR`, `DIER`, `DEFR*`, `DIDSR`, `DPLLCR`, and `DPLLC2R` describe global display control and SoC-specific routing; `HDSR` through `DEWR` describe timing; `Pn*` and `APn*` describe primary/additional plane programming; `ESCR*`, `OTAR*`, `DORCR`, `DPTSR`, and `DAPTSR` describe external/dual-output routing; `YNCR` through `BCBCR` are color conversion coefficients.

## Control Flow

Control flow is indirect: C files include the header and compose register writes from these macros during CRTC setup, plane setup, interrupt handling, clock routing, and output selection. The header encodes hardware constraints such as protected write codes (`DEFR_CODE`, `DAPCR_CODE`, `DCPCR_CODE`) and bit masks used to preserve unrelated register fields.

## State and Persistence Behavior

The macros describe hardware state that persists in MMIO registers until reset, suspend, or subsequent programming. There is no software state in the header; correctness depends on callers writing the right register block for the active DU channel and SoC generation.

## Dependencies and Integration Points

The macros are consumed by the R-Car DU CRTC, plane, group, encoder, LVDS, DSI, and writeback paths. Integration points include Linux bit operations where `BIT()` is used for newer fields, DRM pixel/plane state code that selects register values, and DT/SoC data that chooses which channel offsets and routing fields are valid.

## Risks and Edge Cases

- Register macros are hardware ABI. Incorrect shifts, masks, or protected codes can silently misprogram display output.
- Several fields are generation-specific or SoC-specific; callers must avoid using Gen3/Gen4 fields on older DU blocks.
- `DD1SRCR_FRM` is defined twice with the same value, which is harmless for preprocessing but is a maintenance warning.
- Plane address masks such as `PnDSA_MASK` assume caller alignment validation.

## Test Signals

Build coverage should include all R-Car DU configurations that include this header. Runtime signals are correct CRTC timing, plane positioning, interrupt clearing, LVDS/DSI clock routing, dual-output behavior, and no unexpected reserved-bit writes under register tracing.
