# sources/distributed-fs/ceph-client/arch/x86/boot/video-mode.c

Purpose: shared video-mode selection engine used by setup code and ACPI wakeup code.

Important APIs and state: exports globals `adapter`, `force_x`, `force_y`, `do_restore`, and `graphic_mode`; functions `probe_cards()`, `mode_defined()`, and `set_mode()`.

Control flow: `probe_cards()` runs each registered `__videocard` probe once per safe/unsafe class. `raw_set_mode()` resolves a requested mode by menu index, exact mode id, resolution encoding, or exceptional unprobed range and calls the owning backend. `set_mode()` handles aliases (`NORMAL_VGA`, `EXTENDED_VGA`, current mode), optionally recalculates VGA vertical timing, and stores the canonical mode in boot params.

Dependencies and integration: central dispatcher for `video.c`, `video-vga.c`, `video-vesa.c`, and `video-bios.c`. Relies on linker-collected `.videocards` records.

Risks and test signals: mode-number compatibility can change if visible mode ordering changes, hence exact IDs are safer than menu indexes. Test aliases, resolution selections, VESA/BIOs exceptional modes, `VIDEO_RECALC`, and wakeup build path.
