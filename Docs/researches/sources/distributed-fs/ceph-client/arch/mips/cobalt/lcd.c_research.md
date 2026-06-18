# sources/distributed-fs/ceph-client/arch/mips/cobalt/lcd.c

Purpose: registers the Cobalt LCD memory window as a platform device.

Important APIs: `cobalt_lcd_add()` allocates `"cobalt-lcd"` with a single memory resource `0x1f000000..0x1f00001f` and runs as a `device_initcall`.

State and integration: no persistent local state after init; the resource is transferred to the platform device. A matching LCD driver consumes the fixed MMIO region.

Risks and test signals: incorrect resource size or address prevents LCD access. Verify platform-device probe and visible LCD updates on supported hardware.
