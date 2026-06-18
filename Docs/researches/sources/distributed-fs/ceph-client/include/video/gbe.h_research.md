# sources/distributed-fs/ceph-client/include/video/gbe.h

## Purpose
`gbe.h` describes the SGI GBE (Graphics Back End) hardware register aperture and timing metadata used by the SGI framebuffer driver. It is a low-level MMIO contract: `struct sgi_gbe` lays out control, timing, framebuffer, WID, color/gamma map, cursor, and video-capture registers with padding chosen to match the hardware address map.

## Important APIs, Types, and Functions
The central type is `struct sgi_gbe`, a volatile register map with fields such as `ctrlstat`, `dotclock`, `i2c`, `sysclk`, video timing registers `vt_*`, flat-panel controls `fp_*`, frame/overlay/DID DMA controls, `mode_regs[32]`, `cmap[6144]`, `gmap`, `gmap10`, cursor registers, and `vc_0` through `vc_8`. Helper macros `MASK`, `GET`, `SET`, `GET_GBE_FIELD`, and `SET_GBE_FIELD` encode register bitfield manipulation from the many `GBE_*_MSB/LSB` constants. `struct gbe_timing_info` carries mode geometry, sync/blanking positions, refresh/pixel-clock values, and PLL parameters.

## Control Flow
The header has no executable driver flow, but it dictates the programming sequence: choose timing data, program PLL fields in `dotclock`, set VT sync/blank/pixel-enable windows, configure frame size/depth/tile pointer/DMA enable bits, load WID/color/gamma/cursor state, then enable scanout DMA. Drivers use the bitfield macros to assemble register values before writing the volatile MMIO struct.

## State and Persistence Behavior
All persistent state represented here is hardware state in the GBE register block and display tables. Color maps, gamma tables, cursor glyphs, timing registers, and DMA enables live until reset, power loss, or driver reprogramming; the header itself owns no software lifetime or file-backed persistence.

## Dependencies and Integration Points
The header depends on fixed-width integer types and Linux-style `u32` definitions from including code. It integrates SGI framebuffer mode setup, palette/gamma programming, cursor support, I2C display probing, flat-panel signaling, and DMA frame buffer management with the GBE MMIO aperture.

## Risks and Test Signals
Risks include incorrect padding or volatile register width breaking the MMIO map, bitfield off-by-one errors, programming invalid timing/PLL values, FIFO reset sequencing mistakes, and confusion between shadow/in-hardware DMA control registers. Test signals include booting SGI hardware or emulation through mode set, palette/gamma updates, cursor movement, flat-panel and CRT timing validation, DMA enable/disable transitions, and static checks that register offsets in `struct sgi_gbe` match hardware documentation.
