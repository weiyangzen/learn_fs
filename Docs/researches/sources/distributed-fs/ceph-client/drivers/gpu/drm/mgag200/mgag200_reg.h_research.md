# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_reg.h

## Purpose
Defines Matrox MGA/G200 register offsets and bit fields used by the mgag200 DRM driver.

## Important APIs, types, and functions
- Drawing, memory, interrupt, status, OPMODE, VGA sequencer/CRTC, extended CRTC, and PCI option register offsets.
- Bit fields for misc clock selection, sync polarity, sequencer reset/screen-off, CRTC protection/interrupts, CRTCEXT mode/start/offset bits, and PCI option SGRAM bit.
- DAC indirect register addresses for TVP3026 and MGA1064 families.
- MGA1064 pixel clock control, PLL, remote-head, GPIO, display, sync, and power register definitions.
- Variant-specific PLL register aliases for WB, EV, EH, and ER chips.

## Control flow
No runtime control flow. The macros are consumed by register access helpers and chip-specific mode/PLL/BMC/DDC code.

## State and persistence
No C state. The definitions identify hardware registers whose values persist after MMIO or DAC writes.

## Dependencies and integration points
Included by `mgag200_drv.h`, which wraps many of these offsets in read/write macros. It is the low-level register ABI for every mgag200 source file.

## Risks
Many definitions are inherited from older XFree86-era code and include registers unused by the current KMS path. Wrong offsets or bit masks can damage modesetting, PLL, DDC, or BMC behavior. Variant-specific PLL aliases are easy to mix up because register M/N ordering differs by chip.

## Test signals
Compile coverage catches only syntax. Runtime register tracing around PLL programming, sync polarity, CRTC timings, DAC GPIO, and display enable/disable is needed to validate these constants.
