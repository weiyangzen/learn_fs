
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Ramdac.c

Purpose: configures the STG4000 RAMDAC for primary display mode, pixel format, stride, pixel PLL, cursor defaults, video window defaults, burst control, CRC trigger, digital video port, and stream output enable/disable.

Important APIs: `InitialiseRamdac()` accepts display depth, width, height, sync polarities, and an in/out pixel clock pointer. It supports 16 and 32 bpp, computes physical pixel depth, primary surface size using a 128-bit pixel bus, calls `ProgramClock()` to choose DAC PLL fields, writes `DACPLLMode`, clears primary/cursor/video-window/border/CRC/video-port registers, and sets burst control. `DisableRamdacOutput()` and `EnableRamdacOutput()` clear/set graphics stream bit 0 in `DACStreamCtrl`.

Control flow: mode setting in `fbdev.c` stops VTG/output, disables VGA, calls `InitialiseRamdac()`, sets VTG timings, resets overlay, then enables RAMDAC and starts VTG.

State and persistence: changes persistent DAC pixel format, primary size/address, PLL mode, cursor address/control, video window, border color, burst control, CRC trigger, digital video port, and stream control. `*pixelClock` is overwritten with the actual clock returned by PLL search.

Dependencies and integration: depends on `ProgramClock()` from `STG4000InitDevice.c`, register layout/macros in `STG4000Reg.h`, and `kyrofb_info` timing flow in `fbdev.c`.

Risks: only 16/32 bpp are accepted; callers must reject other depths. Width must be compatible with bus-divisor math or primary size fields can underflow/truncate. Sync polarity arguments are accepted but not used in this function; polarity is handled in VTG setup. PLL failure handling depends on `ProgramClock()` returning nonzero valid fields.

Test signals: mode set at all accepted depths and common widths, actual pixel clock feedback, stream disable/enable state, cursor disabled by default, and failure for unsupported bpp.
