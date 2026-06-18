# sources/distributed-fs/ceph-client/arch/x86/boot/video-vesa.c

Purpose: implements VESA BIOS Extension text and optional graphics mode probing/setting for early boot.

Important APIs and state: defines static VBE info buffers `vginfo` and `vminfo`, a `__videocard video_vesa`, and `vesa_store_edid()` when not in wakeup. Helpers store graphics framebuffer parameters, DAC size, and VESA protected-mode info in `boot_params.screen_info`.

Control flow: `vesa_probe()` calls VBE `0x4f00`, validates signature/version, walks the BIOS mode list, queries mode info with `0x4f01`, and records supported text modes or configured linear-framebuffer graphics modes. `vesa_set_mode()` validates the target, sets mode with `0x4f02` and linear framebuffer bit when needed, updates text geometry or graphics framebuffer state. EDID probing uses VBE DDC `0x4f15`.

Dependencies and integration: participates in video card registry and feeds boot protocol `screen_info` for later console/framebuffer setup. Depends on VESA ABI structures, BIOS INT 10h, heap allocation, and config options `CONFIG_BOOT_VESA_SUPPORT` and `CONFIG_FIRMWARE_EDID`.

Risks and test signals: BIOS VBE implementations vary widely; framebuffer metadata must match actual mode or the kernel console will be wrong. Test VBE 1.2+ text modes, VBE 2.0 EDID, graphics LFB modes, DAC size handling, and builds without framebuffer support.
