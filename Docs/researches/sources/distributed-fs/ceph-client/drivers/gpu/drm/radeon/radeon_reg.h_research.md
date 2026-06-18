# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_reg.h

## Purpose

`radeon_reg.h` is a large legacy Radeon register and bitfield map. It provides symbolic constants for MMIO, PLL, PCI config, VGA, display, overlay/video, capture, 2D, 3D/TCL, command processor, PCIe GART, TV-out, scratch, and packet formats used by Radeon driver code. It also includes newer generation register headers (`r300_reg.h`, `r500_reg.h`, `r600_reg.h`, `evergreen_reg.h`, `ni_reg.h`, `si_reg.h`, `cik_reg.h`) so one legacy include can expose a broad Radeon register namespace.

## Important APIs, Types, And Definitions

This file defines no functions or C types. Its API is preprocessor constants. Major groups include:

- Memory controller and aperture registers: `RADEON_MC_AGP_LOCATION`, `RADEON_MC_FB_LOCATION`, `RADEON_CONFIG_APER_*`, `RADEON_CONFIG_MEMSIZE`, `RADEON_MEM_*`, `R300_MC_*`.
- PCI/AGP/PCIe constants: `RADEON_AGP_*`, `RADEON_CAP_*`, `RADEON_BUS_CNTL`, `RV370_BUS_CNTL`, MSI rearm bits, `RADEON_PCIE_LC_LINK_WIDTH_CNTL`, `RADEON_PCIE_TX_GART_*`.
- PLL and clock/power bits: `RADEON_CLOCK_CNTL_INDEX/DATA`, `RADEON_CLK_PWRMGT_CNTL`, `RADEON_MCLK_CNTL`, `RADEON_SCLK_CNTL`, `RADEON_SPLL_CNTL`, `RADEON_PPLL_*`, `RADEON_P2PLL_*`, `RADEON_PIXCLKS_CNTL`, `RADEON_TV_PLL_*`.
- Display/CRTC/LVDS/DAC/TMDS registers: `RADEON_CRTC*`, `RADEON_FP*`, `RADEON_LVDS*`, `RADEON_DAC*`, `RADEON_DISP_*`, BIOS scratch registers and display attach/DPMS bits.
- 2D engine and drawing registers: brush data, destination/source offsets and pitches, scissor registers, ROP constants, color compare, host data, GUI scratch, and wait/idle bits.
- Video/overlay/capture/TV-out blocks: `RADEON_OV0_*`, `RADEON_CAP0_*`, `RADEON_CAP1_*`, `RADEON_TV_*`, VIP bus registers.
- 3D/TCL/R200 registers: texture formats/filters/offsets, blend state, z/stencil state, viewport, vertex format, TCL matrices/materials/lights, R200 texture combiners and VAP state.
- Command processor and packet macros: ring buffer registers, indirect buffer registers, CSQ registers, CP packet type constants, packet3 opcodes, and decoding helpers such as `RADEON_CP_PACKET_GET_TYPE()`, `RADEON_CP_PACKET_GET_COUNT()`, `R100_CP_PACKET0_GET_REG()`, and `R600_CP_PACKET0_GET_REG()`.

## Control Flow

There is no runtime control flow. The file affects compiled code by substituting register offsets, masks, shifts, and packet encodings wherever included. The final decoding helper macros do perform compile-time expression expansion for packet parsing.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware state locations and bit meanings. State changes happen in driver code that reads or writes the registers named here. Because many constants correspond to hardware registers with side effects, incorrect use by callers can persist in GPU hardware state until reset, modeset, suspend/resume, or explicit reprogramming.

## Dependencies And Integration Points

This header is a shared contract between low-level Radeon subsystems: memory controller setup, display modesetting, PLL programming, acceleration command emission, CP/ring setup, IRQ/vblank handling, overlay/video paths, TV-out support, GART setup, and legacy 3D state. It integrates with generation-specific headers by including them at the top. Consumers typically pair these constants with register accessors/macros in Radeon core code, ASIC-specific files, and command submission parsing.

## Risks And Edge Cases

- The file begins with a warning that it was converted from `r128_reg.h` and contains definitions not fully audited for Radeon. That historical warning is still relevant: register names may be legacy, duplicated, or only valid on specific ASICs.
- Several constants intentionally alias the same numeric offsets across access spaces or generations, such as PCI config vs MMIO/PLL naming and repeated scratch/register names. Callers must know the correct register aperture and ASIC family.
- Duplicate names and overlapping concepts exist (`RADEON_AGP_BASE` appears in the early memory section and the AGP section; `RADEON_GUI_SCRATCH_REG*` and `RADEON_SCRATCH_REG*` share offsets). Refactors must avoid assuming uniqueness implies distinct hardware.
- Bit masks and shifts encode hardware ABI. A one-bit error can cause display corruption, GPU hangs, bad memory-controller setup, broken command parsing, or unsafe power/clock behavior.
- Newer generation headers are included into this namespace, increasing the chance of macro collisions and making include-order effects important.
- Some comments mark guesses, unknowns, or FIXME material. These should be treated as hardware documentation debt, not authoritative high-level behavior.

## Test Signals

The main validation signals are compile coverage of all consumers, command submission parser tests for packet decoding macros, modeset and vblank tests for CRTC/display constants, ring/CP initialization on affected ASIC generations, suspend/resume after PLL or memory-controller programming, IGT or similar display/PRIME/GEM workloads that exercise register programming, and hardware smoke tests across R100/R200/R300/R500/R600+ families because the same header spans many ASIC-specific register layouts.
