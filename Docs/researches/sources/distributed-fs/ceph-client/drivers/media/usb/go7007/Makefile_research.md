# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/Makefile

Purpose: maps GO7007 Kconfig symbols to module objects and declares composite object membership.

Important APIs/types/functions: `obj-$(CONFIG_VIDEO_GO7007)` builds `go7007.o`; USB, loader, and Sensoray configs build `go7007-usb.o`, `go7007-loader.o`, and `s2250.o`. `go7007-y` links `go7007-v4l2.o`, `go7007-driver.o`, `go7007-i2c.o`, `go7007-fw.o`, and `snd-go7007.o` into the core module. `s2250-y` links `s2250-board.o`. A conditional `ccflags` include path is added for loader-as-built-in with common media firmware headers.

Control flow: build-system only. Kbuild uses these assignments to decide which translation units become module components.

State and persistence: none at runtime. Build products and module composition are controlled here.

Dependencies and integration points: ties the researched `go7007-driver.c` into the core `go7007` module with V4L2, I2C, firmware-construction, and ALSA support. It also coordinates with USB transport and board-specific modules controlled by Kconfig.

Risks: object membership must match exported symbols and Kconfig dependencies. The conditional include path is narrow and could break if loader/common headers move. Tests should include clean builds for built-in and module permutations, especially `CONFIG_VIDEO_GO7007_LOADER=m/y`, and modpost symbol checks for `go7007-usb`/`s2250` consumers.
