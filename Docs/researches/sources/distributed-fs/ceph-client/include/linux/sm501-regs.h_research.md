<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sm501-regs.h -->
# sources/distributed-fs/ceph-client/include/linux/sm501-regs.h

## Purpose
`sm501-regs.h` is a register map for the Silicon Motion SM501 multifunction graphics/IO controller. It defines offsets and bit fields for system control, GPIO, I2C, UART, USB, display controller, video overlays, hardware cursors, DMA, color-space conversion, and 2D engine blocks.

## Important APIs, Types, and Functions
This file contains preprocessor constants only. Important register base offsets include `SM501_SYS_CONFIG`, `SM501_GPIO`, `SM501_I2C`, `SM501_SSP`, `SM501_UART0`, `SM501_UART1`, `SM501_USB_HOST`, `SM501_USB_GADGET`, `SM501_DC`, `SM501_ZVPORT`, `SM501_AC97`, `SM501_UCONTROLLER`, `SM501_DMA`, `SM501_2D_ENGINE`, and `SM501_2D_ENGINE_DATA`. Important system registers include `SM501_SYSTEM_CONTROL`, `SM501_MISC_CONTROL`, GPIO control/data/DDR/IRQ registers, power gate/clock registers, endian/device-id registers, and programmable PLL control.

Display constants cover panel and CRT control bits, frame-buffer address/offset/width/height registers, timing registers, current line, hardware cursor registers, palette bases, video overlay registers, alpha plane registers, and monitor detect. 2D constants cover source/destination/dimension/control/pitch/color/clip/pattern/window/base/alpha/status registers plus CSC source/destination/pitch/scale/control registers.

## Control Flow
There is no executable control flow. SM501 drivers use these constants to compute MMIO addresses from mapped register bases and to set/clear bit fields. Typical flow is device initialization reading `SM501_DEVICEID`, configuring `SM501_MISC_CONTROL`, enabling unit gates/clocks through power mode registers, setting GPIO/display/USB/UART block registers, and programming display/2D engine registers for framebuffer operations.

## State and Persistence Behavior
The persistent state is hardware register state in the SM501 device, not C state in this header. Register writes persist until reset, suspend/resume restore, firmware/bootloader reconfiguration, or driver changes. Some offsets alias clear/status behavior, such as raw IRQ status/clear and GPIO IRQ status/reset.

## Dependencies and Integration Points
The constants are consumed by SM501 platform, MFD, framebuffer, GPIO, I2C, USB, UART, and acceleration drivers. They pair with `sm501.h` helper APIs for shared register modification and unit power/clock control. Endianness-sensitive accessors are provided in `sm501.h`, not here.

## Risks and Test Signals
Risks are incorrect bit masks, register alias confusion, endian mistakes, programming disabled clock gates, timing values that produce invalid video output, and conflicting writes by multiple child drivers. Test signals include successful device-id detection, framebuffer mode set, GPIO/I2C/UART smoke tests, suspend/resume restore, interrupt clear behavior, 2D engine status transitions, and MMIO tracing around shared registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sm501-regs.h -->
