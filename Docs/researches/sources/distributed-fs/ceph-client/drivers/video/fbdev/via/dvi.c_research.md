# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/dvi.c

## Purpose
`dvi.c` handles VIA DVI/TMDS transmitter identification, connector sensing, EDID-based panel limits, DVI timing setup, and DVI output enable/disable register programming.

## Important APIs, Types, And Functions
Public VIA-driver functions are `viafb_init_dvi_size()`, `viafb_tmds_trasmitter_identify()`, `viafb_dvi_set_mode()`, `viafb_dvi_sense()`, `viafb_dvi_disable()`, and `viafb_dvi_enable()`. Internal helpers wrap TMDS I2C access, query EDID, parse EDID monitor descriptor pixel-clock limits, and apply chip-specific skew patches for DVP0/DFP-low outputs.

## Control Flow
TMDS identification temporarily enables output pads, probes VT1632 over candidate I2C ports, initializes it when found, otherwise treats CX700 DVI layouts as integrated TMDS or restores pad registers and marks no transmitter. DVI sensing powers/controls pads, reads VT1632 hotplug status, falls back to EDID probing, then restores saved registers. Mode setup optionally switches to a reduced-blanking mode if EDID-derived max pixel clock would be exceeded, then delegates CRTC timing programming to `viafb_fill_crtc_timing()`. Enable/disable branches by output interface and chip family to power TMDS, route pads, clear direct-display-period bits, and apply skew fixes.

## State And Persistence
State is stored in global/shared VIA structures reachable through `viaparinfo`: TMDS chip name, target I2C address, I2C port, output interface, active timing, max pixel clock, and IGA path. Hardware register changes persist until restored or overwritten by later modeset/output changes.

## Dependencies And Integration Points
It depends on `linux/via-core.h`, `linux/via_i2c.h`, VIA register helpers from `global.h`, chip definitions from `chip.h`, DVI constants from `dvi.h`, mode helpers from `viamode.h`, and timing programming in `hw.c`. It is called during chip initialization, hotplug/sense paths, and full modesets.

## Risks
The code is global-state-heavy and assumes `viaparinfo` and nested pointers are initialized. EDID probing temporarily changes the TMDS I2C target to `0xA0`; one failure path in `viafb_dvi_query_EDID()` returns false without restoring the saved target, which can poison later TMDS register accesses. Many register sequences are chip-specific and magic-number based. The function name `viafb_tmds_trasmitter_identify` carries the historical typo and must be matched by callers.

## Test Signals
Signals include VT1632 detection on both I2C ports, integrated TMDS detection on CX700 DVI layouts, EDID max-pixel-clock extraction, DVI sense hotplug state, reduced-blanking fallback when pixel clock is too high, correct enable/disable register traces per interface, and regression coverage for restoring TMDS target address after failed EDID reads.
