# sources/distributed-fs/ceph-client/arch/x86/boot/video-vga.c

Purpose: provides baseline CGA/EGA/VGA text mode detection and mode setting.

Important APIs and state: defines static mode tables for VGA, EGA, and CGA; exports `vga_crtc()`; registers `__videocard video_vga`. It updates global adapter type and boot screen flags.

Control flow: `vga_probe()` uses BIOS INT 10h EGA/VGA checks and display combination code to classify adapter, stores original EGA BX in boot params, and selects the appropriate mode list. Mode-setting resets to basic text mode, sets font/scans for requested 80-column text geometry, updates `force_x/force_y`, and uses CRTC register helpers for 480-scanline modes.

Dependencies and integration: must be listed first in the video Makefile because other video backends depend on adapter and CRTC information. Uses BIOS INT 10h and VGA indexed I/O ports.

Risks and test signals: direct CRTC programming is hardware-sensitive. Test CGA/EGA/VGA classification, 80x25/43/50/60 modes, cursor/font sizes, and that later VESA/BIOS probes see initialized adapter state.
