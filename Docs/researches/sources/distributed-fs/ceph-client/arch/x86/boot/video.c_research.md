# sources/distributed-fs/ceph-client/arch/x86/boot/video.c

Purpose: top-level setup video selection, menu interaction, and screen-info capture.

Important APIs and state: exports `set_video()`. Internal state includes `video_segment` and heap-backed `saved_screen` data. Helpers store cursor/current mode/mode params, display interactive mode menus, save/restore text screen contents, and parse user mode entry.

Control flow: `set_video()` resets heap, stores current mode parameters, saves text screen, probes safe cards, resolves `hdr.vid_mode` through current/default/menu loop, retries undefined modes by asking user, stores canonical mode, saves EDID, refreshes mode params, and restores screen when requested. Menu flow waits for Enter/Space/timeout, supports `scan` to run unsafe probes, and accepts hex-like mode input.

Dependencies and integration: called by `main()` before protected mode. Writes `boot_params.screen_info` and `hdr.vid_mode` consumed by the kernel. Integrates all `__videocard` backends and real-mode I/O helpers.

Risks and test signals: heap space limits screen save and probed mode lists. User-visible menu path must work with BIOS keyboard/console and serial mirroring. Test default/current mode, `vga=ask`, `scan`, graphics mode no-restore behavior, screen restore, and geometry overrides from `force_x/force_y`.
