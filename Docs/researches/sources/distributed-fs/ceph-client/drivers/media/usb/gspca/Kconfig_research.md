# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/Kconfig

Purpose: kernel configuration menu for the GSPCA webcam framework and its USB subdrivers. It exposes `USB_GSPCA` as the parent framework option and per-chip/per-camera tristate options for many subdrivers, including the BenQ, Conexant, and CPiA1 files researched in this subset.

Important APIs and entries: `menuconfig USB_GSPCA` depends on `VIDEO_DEV`, allows `INPUT` to be disabled, and selects `VIDEOBUF2_VMALLOC`. Each child `config USB_GSPCA_*` depends on `VIDEO_DEV && USB_GSPCA`, provides help text, and documents the module name. The file also sources nested Kconfig files for `gl860`, `m5602`, and `stv06xx`.

Control flow: Kconfig evaluation first enables the parent menu, then reveals child options only inside `if USB_GSPCA && VIDEO_DEV`. Selected symbols drive object inclusion in the adjacent Makefile.

State and persistence: configuration persists in kernel `.config`, not in driver runtime. The selected tristate values determine whether drivers are built-in, modules, or omitted.

Dependencies and integration points: integrates with media USB Kconfig hierarchy, V4L2 core, input subsystem, VB2 vmalloc memory, and per-subdriver Makefile symbols. It also points users at the GSPCA card list documentation.

Risks and test signals: risks include config/Makefile symbol drift, missing dependency selections for subdrivers that need extra frameworks, stale module names in help, and nested Kconfig source path breakage. Test with `make olddefconfig`, `allmodconfig`, selected built-in/module combinations, and verifying every symbol here has a corresponding Makefile object or intentional directory source.
