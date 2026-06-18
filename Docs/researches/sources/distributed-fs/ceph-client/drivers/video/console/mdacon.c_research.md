# sources/distributed-fs/ceph-client/drivers/video/console/mdacon.c

Purpose: low-level text console for secondary MDA/Hercules monochrome adapters, defaulting to virtual consoles 13-16.

Important APIs/types/functions: static `mda_con` implements `struct consw`. Hardware helpers `write_mda_b()`, `write_mda_w()`, `mda_set_cursor()`, and `mda_set_cursor_size()` access CRTC ports under `mda_lock`. `mda_detect()` probes VRAM and status bits; `mda_initialize()` configures Hercules-style cards. Module parameters `mda_first_vc` and `mda_last_vc` select the VC range.

Control flow: module init validates VC range, takes console lock, and calls `do_take_over_console()`. Startup maps MDA memory at `0xb0000`, sets ports, detects card/type, optionally initializes non-MDA hardware, hides boot cursor, and returns the display name. Console methods convert Linux attributes into MDA attributes, write characters to VRAM, clear/scroll VRAM, blank via memory clear or mode-port video disable, and program cursor position/shape.

State and persistence: global hardware geometry, cursor cache, type, mapped VRAM pointer, and foreground VC pointer persist until module exit. Hardware registers and text VRAM persist while the adapter is powered.

Dependencies and integration: ISA/VGA-style I/O, `asm/vga.h`, VT console core, selection/inversion helpers, module params or boot `mdacon=`.

Risks: direct legacy I/O and VRAM probing can disturb real hardware; detection loops rely on vsync timing. Bounds depend on fixed 80x25 geometry. Tests are mostly hardware/boot tests: card detection, VC range takeover, cursor shapes, blank/unblank, scroll up/down, attribute conversion, and module unload.
