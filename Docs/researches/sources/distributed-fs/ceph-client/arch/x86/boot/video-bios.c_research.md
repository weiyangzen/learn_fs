# sources/distributed-fs/ceph-client/arch/x86/boot/video-bios.c

Purpose: registers and probes conventional BIOS text modes as a video backend.

Important APIs and state: defines a `__videocard video_bios` with `bios_probe()` and `bios_set_mode()`. Probe allocates mode descriptors on the boot heap and marks this backend `unsafe`, so it only scans after explicit user request.

Control flow: `bios_probe()` iterates BIOS modes `0x14..0x7f`, skips already-defined modes, sets each mode, verifies text-mode characteristics through VGA registers, records geometry from BIOS data area, then restores the saved mode. `set_bios_mode()` sets INT 10h mode, verifies current mode, and attempts revert if setting failed to a different mode.

Dependencies and integration: used by `probe_cards()`/`set_mode()` in video selection. Depends on VGA adapter detection, heap allocation, BIOS INT 10h, and indexed VGA register access.

Risks and test signals: probing is unsafe because real BIOS mode switches can blank or wedge displays; it is gated behind the menu scan path. Test manual `scan`, successful restore, duplicate mode filtering, and fallback/revert on failed mode set.
