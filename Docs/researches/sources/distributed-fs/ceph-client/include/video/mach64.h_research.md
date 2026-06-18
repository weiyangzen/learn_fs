# sources/distributed-fs/ceph-client/include/video/mach64.h

## Purpose
`mach64.h` is a comprehensive ATI Mach64/Rage register and bit definition catalog for framebuffer and acceleration drivers. It maps CRTC, memory, DAC, clock/PLL, GUI engine, overlay/capture, AGP, LCD, power-management, and chip-identification registers.

## Important APIs, Types, and Functions
The file defines macros only. Major register groups include CRTC timing, DSP/memory-buffer controls, cursor, clock/PLL, configuration/status, memory control, DAC, GUI draw engine destination/source/host/pattern/scissor/data-path/color-compare/FIFO/status registers, overlay/capture/scaler, AGP, LCD panel controls, and VGA extended registers. Important field families cover mix/ROP values, engine bounds, bus/test/DSP masks, PLL indices and fields, memory and DAC types, chip IDs for GX/CX/CT/ET/VT/GT/Rage XL/Mobility variants, `IS_XL()` and `IS_MOBILITY()` predicates, destination/source/data-path pixel width fields, GUI status bits, power-management masks, and LCD stretching/LVDS/backlight fields.

## Control Flow
No functions exist, but driver control flow follows the register groups: identify chip and memory/DAC/clock type, program PLL and CRTC timings, configure memory/DSP FIFO thresholds, initialize DAC/palette and cursor state, enable the GUI engine, emit accelerated blit/fill/line operations through draw-engine registers, and manage LCD/power states on mobile chips.

## State and Persistence Behavior
The header owns no state. It names hardware state held in Mach64 registers, including mode timings, FIFO thresholds, engine command state, cursor/palette, panel stretch state, and power-management mode. That state persists until reset, suspend, or driver reprogramming.

## Dependencies and Integration Points
It is consumed by ATI Mach64 framebuffer code and any low-level helper that performs MMIO or port-I/O register access. It integrates PCI chip discovery, VGA compatibility, fbdev acceleration, DAC/PLL setup, LCD panel management, overlay/capture, and suspend/resume power handling.

## Risks and Test Signals
Risks include wrong offsets across chip families, using CT/ET/VT/GT-specific masks on the wrong ASIC, FIFO/engine programming without idle checks, PLL misprogramming, and ABI regressions in accelerated fb operations. Test signals include chip-ID detection on representative Mach64/Rage variants, mode-setting across pixel depths, accelerated copy/fill/text, cursor/palette tests, LCD stretch/backlight on Mobility hardware, suspend/resume restore, and static review of duplicate aliases and family-specific registers.
