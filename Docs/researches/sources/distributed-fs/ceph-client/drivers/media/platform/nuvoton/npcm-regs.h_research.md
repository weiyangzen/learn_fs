# sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/npcm-regs.h

## Purpose
`npcm-regs.h` defines register offsets, bit masks, field encodings, sizes, and timeouts for the Nuvoton NPCM Video Capture/Differentiation Engine, Encoding Compression Engine, GCR, and GFXI blocks.

## Important APIs, Types, and Functions
The VCD section defines frame-buffer addresses, line pitch, capture resolution, mode, command, status, interrupts, resolution-change timing, FIFO threshold, buffer size, bandwidth threshold, and timeout constants. The ECE section defines DDA control/status, framebuffer and encoded-data base addresses, rectangle position/dimension, line-pitch encoding, HEXTILE control, rectangle offset, tile size, and timeout. GCR/GFXI definitions cover display interface reset, mode, resolution counters, and graphics PLL fields.

## Control Flow
`npcm-video.c` uses these constants to reset hardware, detect resolution and pixel clock, configure line pitch, trigger capture or compare operations, process interrupts, and drive optional HEXTILE rectangle encoding.

## State and Persistence
The header defines no software state. The hardware registers are volatile state that the driver initializes on open/start and clears on stop/remove.

## Dependencies and Integration Points
It relies on bitfield macros from included kernel headers in the C file context. It is tightly coupled to the `npcm-video.c` register programming model and NPCM DT syscon resources.

## Risks and Edge Cases
Incorrect field widths can corrupt capture dimensions, line pitch, or rectangle offsets. `VCD_FB_SIZE` fixes support to 1920x1200 RGB565-sized buffers; future higher resolutions require coordinated memory and timing changes. Timeout constants affect IRQ recovery and encode polling behavior.

## Test Signals
Validate VCD capture at min/max resolutions, line-pitch selections 512 through 4096, interrupt status clear behavior, ECE HEXTILE rectangle offsets, GFXI resolution/pixel-clock reads, and reset sequencing.
