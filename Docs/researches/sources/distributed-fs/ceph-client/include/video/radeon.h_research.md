<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/radeon.h -->
# sources/distributed-fs/ceph-client/include/video/radeon.h

## Purpose
This header is a Radeon register map for old Radeon framebuffer/display support. It defines MMIO aperture size, PCI/config offsets, display controller registers, overlay registers, command processor and 2D engine registers, PLL indices, memory-controller indirect indices, and many bit masks for clock, power, CRTC, panel, DAC, surface, blitter, AGP, and memory programming.

## Important APIs, Types, And Functions
- `RADEON_REGSIZE` declares the expected 16 KiB register aperture.
- Register offsets include config/PCI registers (`BUS_CNTL`, `CNFG_MEMSIZE`, `REG_MEM_BASE`), display and CRTC registers (`CRTC_GEN_CNTL`, `CRTC_H_TOTAL_DISP`, `CRTC_OFFSET`, `CRTC2_GEN_CNTL`), flat-panel/LVDS/TMDS registers, overlay/subpicture registers, command processor ring registers, scratch registers, and 2D blitter registers.
- Bit definitions cover enable/disable, reset, idle, endian, pixel-format, ROP, PLL, power-management, AGP, memory-controller, surface translation, and cursor/display state.
- PLL and indirect register names are exported both as simple indices (`pllPPLL_CNTL`, `pllSCLK_CNTL`, `ixR300_MC_*`) and detailed field masks (`PIXCLKS_CNTL__*`, `SCLK_CNTL__*`, `MCLK_CNTL__*`).

## Control Flow
There is no executable control flow in the header. Driver control flow is implied: map the Radeon MMIO region, compute mode/clock/memory values, write offsets with the masks here, poll idle/status bits such as `RBBM_STATUS`, `CRTC_VBLANK`, `GUI_ACTIVE`, and `RB2D_DC_BUSY`, and sequence display/PLL/power changes carefully. PLL access is indirect through `CLOCK_CNTL_INDEX`/`CLOCK_CNTL_DATA` with `PLL_WR_EN`.

## State And Persistence
State is hardware-resident in Radeon registers and survives until overwritten, reset, suspend, or device power loss. The header exposes no software persistence, but many masks control persistent display routing, panel power, clocks, memory timings, AGP behavior, cursor state, palette access, framebuffer offsets, and scratch registers used by firmware or drivers.

## Dependencies And Integration Points
Consumers are low-level Radeon fb/DRM code that uses Linux MMIO accessors and PCI resource mapping. Integration points include display mode setting, DPMS/power management, DDC/GPIO probing, PLL programming, 2D acceleration, video overlay, LVDS/TMDS/TV output, AGP/PCI bus setup, and suspend/resume restore tables.

## Risks And Edge Cases
Incorrect bit masks or write ordering can blank displays, lock the 2D engine, corrupt memory-controller timing, or hang the GPU. Several names alias the same offsets for different chip families, so code must select the right generation. Some constants are marked broken or duplicate (`RB2D_DSTCACHE_CTLSTAT_broken`, duplicate `SRC_PITCH_OFFSET`/`AGP_PLL_CNTL`), and read-modify-write must avoid reserved/write-sensitive bits.

## Test Signals
Useful signals are successful mode set on CRT/LVDS/TMDS outputs, correct pixel clock, stable suspend/resume, working palette/cursor, clean 2D acceleration with cache flushes, no GPU idle timeouts, valid DDC reads through GPIO registers, and no display corruption across endian and bpp modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/radeon.h -->
