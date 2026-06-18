# sources/distributed-fs/ceph-client/drivers/video/fbdev/controlfb.h

## Purpose

This header defines the hardware register layout, timing register value containers, framebuffer offset, and supported Mac mode/depth table used by `controlfb.c`. The complete 143-line source was read.

## Important APIs, Types, and Functions

`struct cmap_regs` models RADACAL colormap/misc register spacing. `struct preg` represents a padded 32-bit control register, and `struct control_regs` lays out the vertical timing, horizontal timing, control, start address, pitch, monitor sense, VRAM, mode, refresh, and interrupt registers. `struct control_regints` is the unpacked timing view, while `struct control_regvals` stores the 16 timing values plus mode, RADACAL control, and three clock parameters. `CTRLFB_OFF` defines the 16-byte offset of pixel zero in framebuffer memory. `control_mac_modes[]` maps Mac video modes to the maximum supported color mode for 2 MiB and 4 MiB VRAM configurations.

## Control Flow

There is no executable control flow in the header. The layout directly drives `controlfb.c` register writes through `CNTRL_REG()` and determines mode fallback logic in `init_control()`.

## State and Persistence Behavior

The header stores no runtime state, but its static `control_mac_modes[]` table becomes compiled data in each translation unit that includes it. Its register structs define how driver state maps onto hardware-visible MMIO.

## Dependencies and Integration Points

The header is tightly coupled to PowerMac "control" hardware, `macmodes.c` mode IDs, and `controlfb.c` timing calculations. The exact padding values are part of the MMIO ABI between the C structs and the device register spacing.

## Risks and Edge Cases

Because `control_mac_modes[]` is defined `static` in a header, including it from multiple C files would duplicate data; currently it is used by `controlfb.c`. Register layout mistakes would cause broad hardware misprogramming. Comments note uncertainty for horizontal timing units above 1024/1280 pixels, which is relevant for high-resolution modes in the table.

## Test Signals

Validation is mostly build and hardware driven: ensure `controlfb.c` compiles with this header, verify register offsets against known hardware documentation, and exercise every `control_mac_modes[]` entry that claims support for 2 MiB or 4 MiB VRAM.
