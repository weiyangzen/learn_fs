# sources/distributed-fs/ceph-client/arch/x86/boot/video.h

Purpose: declares the real-mode video probing contract, mode-number namespace, and shared video state.

Important APIs and state: defines mode ranges for BIOS, VESA, Video7, special modes, resolution modes, and `VIDEO_RECALC`; structs `mode_info` and `card_info`; `__videocard` linker-section registration; externs for `video_cards`, `adapter`, `force_x`, `force_y`, `do_restore`, and `graphic_mode`; helpers for VGA indexed registers and `vga_crtc()`.

Control flow: no standalone runtime, but macros and structs define how video backends are discovered and invoked.

Dependencies and integration: included by all boot video files and by wakeup-shared mode code.

Risks and test signals: mode namespace collisions or struct layout changes break backend dispatch. Build and boot test all video backends and menu display.
