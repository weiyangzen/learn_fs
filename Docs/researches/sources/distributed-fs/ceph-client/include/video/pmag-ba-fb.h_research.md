# sources/distributed-fs/ceph-client/include/video/pmag-ba-fb.h

## Purpose
`pmag-ba-fb.h` defines memory-resource offsets and Bt459 RAMDAC register offsets for the TURBOchannel PMAG-BA Color Frame Buffer card.

## Important APIs, Types, and Functions
Resource offsets identify framebuffer memory, Bt459 RAMDAC, IRQ acknowledge, option ROM, Bt438 clock-chip reset, and total address-space size. Bt459 byte-wide register offsets include low/high address, data window, and color-map window. There are no functions or structs.

## Control Flow
The PMAG-BA driver maps the TURBOchannel resource, adds these offsets to reach framebuffer, RAMDAC, IRQ ack, ROM, and clock reset regions, then programs the Bt459 through address/data/cmap byte windows.

## State and Persistence Behavior
State is hardware state in framebuffer memory, Bt459 palette/control registers, IRQ latch, and clock chip. The header owns no runtime data.

## Dependencies and Integration Points
It integrates DEC TURBOchannel framebuffer probing with resource mapping, interrupt acknowledgment, RAMDAC palette setup, and option ROM access.

## Risks and Test Signals
Risks include overlapping ROM/Bt438 offset interpretation, byte-wide RAMDAC access alignment, missed IRQ acknowledgments, and mapping the wrong address-space size. Test signals include TURBOchannel resource probing, palette writes, IRQ ack behavior, framebuffer console output, and ROM/clock reset access sanity.
