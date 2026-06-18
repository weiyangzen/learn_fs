# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200er.c

## Purpose
Implements G200ER support with ER-specific register defaults, tag FIFO reset, PLL programming sequence, and a custom CRTC enable path.

## Important APIs, types, and functions
- `mgag200_g200er_init_registers()` writes default DAC state and ER-specific DAC/ECRT registers.
- `mgag200_g200er_reset_tagfifo()` toggles an undocumented `MGAREG_MEMCTL` reset bit.
- `mgag200_g200er_pixpllc_atomic_check()` searches r/n/m/o values for a 48 MHz reference and 1.056-1.488 GHz VCO.
- `mgag200_g200er_pixpllc_atomic_update()` disables pixel/remote clocks, powers the PLL down, writes ER PLL registers, and delays.
- Custom `mgag200_g200er_crtc_helper_atomic_enable()` resets the tag FIFO after PLL programming.

## Control flow
The factory maps and initializes the device, probes VRAM, configures mode limits, creates the pipeline, and starts polling. During atomic enable, the custom helper programs format and mode, updates PIXPLLC, resets the tag FIFO, loads gamma, and enables display.

## State and persistence
Device info caps 2048x2048 and bandwidth 55000 with BMC sync disabled. PLL values persist in CRTC state. ER-specific DAC, ECRT, and MEMCTL state persists in hardware.

## Dependencies and integration points
Uses shared KMS helpers and BMC-aware VGA output. Dispatched for PCI ID 0x534.

## Risks
The tag FIFO reset uses an undocumented magic bit. PLL update does not explicitly re-enable every clock bit it disables in the same way as other variants, relying on later display enable/clock state. A comment in the main driver forces XRGB8888 because 24 bpp is known problematic on G200ER.

## Test signals
G200ER should be tested with XRGB8888 client setup, repeated modesets, tag FIFO reset behavior, EDID/no-EDID paths, and high-bandwidth mode rejection.
