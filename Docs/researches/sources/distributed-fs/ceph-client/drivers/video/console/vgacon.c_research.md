# sources/distributed-fs/ceph-client/drivers/video/console/vgacon.c

Purpose: low-level VGA/EGA/CGA/MDA text console driver and common early console backend for architectures with VGA-compatible text mode.

Important APIs/types/functions: exports `const struct consw vga_con` and `vgacon_register_screen()`. Global hardware state tracks VRAM base/end/size, CRTC ports, geometry, font height, card type, blanking state, 512-character mode, hardscroll, and a shared unicode pagedir. Key functions include `vgacon_startup()`, `vgacon_init/deinit()`, `vgacon_cursor()`, `vgacon_scroll()`, `vgacon_switch()`, `vgacon_blank()`, font set/get helpers, resize, palette handling, and VESA blank/unblank.

Control flow: registered screen info installs `vga_con`. Startup rejects framebuffer/EFI/VGA16 or invalid geometry, chooses mono/color memory and ports, requests I/O resources, normalizes VGA palette, maps VRAM, probes text memory, enables hardscroll on EGA/VGA, and derives resolution. Console methods mostly rely on the generic VT buffer for characters while manipulating CRTC origin, cursor registers, palette/DAC, font planes in VGA memory, and scrollback origin. Blank supports palette blanking, memory clear, or VESA sync suspension.

State and persistence: extensive static globals mirror hardware and console state. VGA registers, palette, font planes, and text VRAM persist until reprogrammed. The shared unicode mapping refcount is maintained across bound VCs.

Dependencies and integration: `screen_info`, VT core, VGA register helpers, I/O port resources, dummy console fallback, boot `no-scroll`, font/palette/io primitives.

Risks: direct register programming is hardware-sensitive. Font loading switches VGA planes and clears attributes across all VGA consoles. Hardscroll relies on careful VRAM wrap math. Tests include boot fallback paths, card type detection, palette blank/unblank, font 256/512 transitions, resize constraints, scrollback deltas, graphics-mode blanking, and unicode pagedir refcount.
