
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_reg.h

## Purpose
`psb_intel_reg.h` is the main display register map for the GMA500/Poulsbo Intel-derived display block. It names MMIO offsets and bitfields for GPIO/GMBUS, backlight PWM, panel power sequencing, CRTC timing, DPLL programming, analog/SDVO/LVDS/MIPI/DP ports, pipe status/vblank accounting, planes, cursors, palettes, hotplug, sideband DPIO, and Cedarview DisplayPort AUX/M/N timing.

## Important APIs, Types, And Functions
The file exports preprocessor constants rather than C functions. Important register families include `GPIOA` through `GPIOH`, `GMBUS0` through `GMBUS5`, `BLC_PWM_CTL*`, `PP_STATUS`, `PP_CONTROL`, `PFIT_CONTROL`, `DPLL_A/B`, `DPLL_A_MD`, `DPLL_B_MD`, `ADPA`, `PORT_HOTPLUG_EN`, `PORT_HOTPLUG_STAT`, `SDVOB`, `SDVOC`, `LVDS`, `PIPEACONF`/`PIPEBCONF`/`PIPECCONF`, `PIPEASTAT`/`PIPEBSTAT`/`PIPECSTAT`, framebuffer counter registers, plane registers such as `DSPACNTR` and `DSPASURF`, cursor registers, interrupt registers `IER/IIR/IMR/ISR`, MIPI DSI registers, and DP registers such as `DP_B`, `DP_C`, `DPB_AUX_CH_CTL`, and `PIPE_GMCH_DATA_M(pipe)`.

It also defines utility macros such as `PSB_MASK`, `SET_FIELD`, `GET_FIELD`, and `_PIPE(pipe, a, b)` for bitfield and per-pipe address construction.

## Control Flow
There is no runtime control flow in this header. Driver code includes it, reads/writes the named MMIO registers through GMA500 accessors, and uses the bit masks to compose values for display bring-up, mode setting, hotplug handling, vblank interrupts, panel power sequencing, and link training.

## State And Persistence
All state represented here is hardware state. Writes can alter I2C pin direction, GMBUS transaction state, backlight PWM duty cycle, panel power timing, DPLL clocking, port enablement, pipe timing, plane base/stride/surface state, interrupt enables/status bits, MIPI DSI FIFOs, and DisplayPort link state. Those values persist in the device until reset or overwritten.

## Dependencies And Integration Points
The header is used by GMA500 display, IRQ, SDVO, LVDS, MIPI, DP, GMBUS, and power-management code. `psb_irq.c` uses the pipe status, pipe frame, hotplug, and interrupt constants. `psb_intel_sdvo.c` uses `SDVOB`, `SDVOC`, `SDVO_*`, `GMBUS_*`, and hotplug bits. The DP/MIPI constants integrate with other GMA500 display paths not in this work item.

## Risks
This file is chip-generation sensitive. Several definitions share names across Poulsbo, Moorestown, Medfield, and Cedarview with different semantics or comments, so using the wrong constant on the wrong platform can program reserved bits. Interrupt status bits are generally write-one-to-clear or sticky, which requires careful masking. The macro `_PIPE` assumes regular pipe register spacing and only fits the paired registers for which it was written.

## Test Signals
Useful validation is successful mode setting across VGA, SDVO, LVDS, MIPI, and DP paths; stable GMBUS/DDC transactions; correct backlight and panel power sequencing; hotplug status bits clearing and re-firing correctly; vblank counters increasing only on enabled pipes; no FIFO underrun or HDMI audio underrun bits during modesets; and DP AUX/link training operating with the expected M/N and lane settings.
