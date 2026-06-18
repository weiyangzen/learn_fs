# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200ev.c

## Purpose
Implements G200EV support with EV-specific register initialization, 50 MHz reference PLL search/programming, high-priority level setup, custom CRTC enable, and device factory.

## Important APIs, types, and functions
- `mgag200_g200ev_init_registers()` writes EV default DAC values and shared VGA registers.
- `mgag200_g200ev_set_hiprilvl()` clears ECRT 0x06.
- `mgag200_g200ev_pixpllc_atomic_check()` searches n/m/p values for a 150-550 MHz VCO.
- `mgag200_g200ev_pixpllc_atomic_update()` disables the pixel clock, toggles PLL status/power, writes EV PLL registers, selects PLL, and re-enables output.
- Custom `mgag200_g200ev_crtc_helper_atomic_enable()` inserts hiprilvl setup after PLL update.

## Control flow
Factory setup uses fixed PCI options, shared resource/init code, EV register defaults, VRAM probe, mode config, pipeline init, reset, and polling. Atomic enable follows common register/gamma/display sequencing with an EV-specific high-priority register write.

## State and persistence
Device info sets max 2048x2048, bandwidth 32700, BMC sync false, and DDC bits 0/1. PLL and ECRT state persist in hardware.

## Dependencies and integration points
Uses shared mgag200 mode, DDC, and BMC-aware VGA helpers. Dispatched for PCI ID 0x530.

## Risks
PLL update relies on ordered delays and status-bit manipulation. No delta threshold is enforced in PLL search. Incorrect hiprilvl setup can affect memory arbitration and scanout stability.

## Test signals
Stable EV output across common modes, PLL frequency accuracy, no flicker after mode changes, EDID reads using data bit 0/clock bit 1, and bandwidth validation are useful signals.
