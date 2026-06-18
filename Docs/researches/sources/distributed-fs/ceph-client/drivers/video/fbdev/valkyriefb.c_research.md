# sources/distributed-fs/ceph-client/drivers/video/fbdev/valkyriefb.c

## Purpose
`valkyriefb.c` implements the fbdev driver for Apple's Valkyrie display controller on supported PowerMac and 68k Macintosh systems. It maps the framebuffer, colormap registers, and Valkyrie control registers, chooses a Mac video mode/color mode from boot options, NVRAM, or monitor sense, then exposes a packed-pixel framebuffer.

## Important APIs, Types, And Functions
Key local state is split between `struct fb_par_valkyrie` for selected vmode/cmode geometry and `struct fb_info_valkyrie` for embedded `fb_info`, mapped register pointers, physical addresses, monitor sense, VRAM size, and pseudo palette. `valkyriefb_ops` provides `fb_check_var`, `fb_set_par`, `fb_setcolreg`, and `fb_blank`. Core helpers include `valkyrie_choose_mode()`, `read_valkyrie_sense()`, `valkyrie_var_to_par()`, `valkyrie_par_to_fix()`, `valkyrie_init_info()`, and `set_valkyrie_clock()`.

## Control Flow
Initialization parses `video=valkyriefb:` options, rejects unsupported machines, locates physical addresses either from hardcoded 68k Macintosh addresses or Open Firmware node resources, allocates driver state, reserves/maps memory, chooses the initial mode, initializes `fb_info`, programs hardware through `valkyriefb_set_par()`, and registers the framebuffer. Mode validation converts fbdev `var` into Mac vmode/cmode through `mac_var_to_vmode()`, verifies table support, rejects virtual panning/offsets, and checks VRAM. Setting a mode resets the controller, writes mode/depth registers, sets clock parameters over CUDA IIC when available, delays, then re-enables output.

## State And Persistence
State is held in the singleton allocated `fb_info_valkyrie`. Boot-selected defaults are static globals and may be seeded from NVRAM. The hardware state is programmed directly into memory-mapped registers; colormap writes are sent to the cmap register pair. There is no runtime remove path in this file, so initialization-time cleanup only covers failures before registration.

## Dependencies And Integration Points
The driver depends on fbdev, Mac monitor-mode helpers in `macmodes.h`, register tables in `valkyriefb.h`, NVRAM and Open Firmware support on PowerMac, ADB/CUDA for clock programming when configured, and machine detection on 68k Mac. It integrates with fbcon through the generic framebuffer registration and with boot options `vmode:` and `cmode:`.

## Risks
The hardware support is highly platform-specific. Address discovery differs between CONFIG_MAC and Open Firmware systems, and the 68k path uses fixed physical addresses. Mode support is table-driven and rejects panning/virtual resolutions. `set_valkyrie_clock()` is compiled out without CUDA, which may leave clock programming dependent on firmware defaults. Because the driver uses a module init path rather than a modern platform driver remove path, teardown coverage is limited.

## Test Signals
Signals include correct machine filtering, successful resource mapping, monitor sense logs, selected mode/cmode logs, registered `valkyrie` framebuffer, correct CLUT updates in 8 bpp, pseudo-palette behavior in 16 bpp, blank/powerdown register effects, and failure tests for unsupported modes, insufficient VRAM, missing OF resources, or failed ioremaps.
