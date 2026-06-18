<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sstfb.h -->
# sources/distributed-fs/ceph-client/include/video/sstfb.h

## Purpose
This header defines the 3Dfx Voodoo SST framebuffer driver's debug macros, PCI/register bit definitions, DAC/PLL constants, ioctls, and driver-private structures.

## Important APIs, Types, And Functions
- `dprintk`, `r_dprintk`, `f_dprintk`, and `v_dprintk` expand based on `SST_DEBUG`.
- Register offsets and bits describe PCI init, LFB/FBZ mode, clipping, FIFO/reset, video timing, DAC access, BitBLT, and hardware status.
- Default register macros (`FBIINIT*_DEFAULT`) encode baseline initialization.
- `SSTFB_SET_VGAPASS` and `SSTFB_GET_VGAPASS` are framebuffer ioctls for VGA passthrough.
- `struct pll_timing` stores PLL `m/n/p`.
- `struct dac_switch` abstracts DAC detection, PLL programming, and video-mode setup.
- `struct sst_spec` describes board default/max clocks.
- `struct sstfb_par` stores palette, timing-derived values, PLL, tile count, MMIO base, DAC operations, PCI device, card type/revision, and VGA passthrough state.

## Control Flow
Driver flow detects the DAC through `dac_switch.detect`, computes PLL timing, programs DAC/video registers using the constants here, configures FBI init registers, sets LFB format, and uses BitBLT commands for acceleration. The VGA passthrough ioctl toggles passthrough state through `vgapass` and related registers.

## State And Persistence
Persistent runtime state is in `sstfb_par`, MMIO registers, DAC registers, and the VGA passthrough setting. Palette and mode timing fields are cached in software while actual display behavior is hardware-resident.

## Dependencies And Integration Points
It integrates with fbdev, PCI devices, kernel ioctl encoding, DAC-specific helpers, register accessors in the implementation, and optional debugging.

## Risks And Edge Cases
Some registers are write-sensitive: the comment on `FBIINIT6_DEFAULT` warns that writing back read values can alter DAC pin drivers. Incorrect FIFO/reset/video sequencing can hang the card. Endian swizzle bits, 16/24bpp selection, and Voodoo1/Voodoo2 clock differences are common failure points.

## Test Signals
Test signals include DAC detection, stable PLL/mode programming, working VGA passthrough ioctls, correct 16/24bpp LFB output, BitBLT copy/fill success, no FIFO busy timeouts, and debug logs that align with register writes when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sstfb.h -->
