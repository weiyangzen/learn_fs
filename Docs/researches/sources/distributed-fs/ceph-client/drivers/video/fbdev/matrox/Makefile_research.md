## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/Makefile

Purpose: this Makefile wires the Matrox fbdev driver family into Kbuild. It selects the always-required core objects for `CONFIG_FB_MATROX` and conditionally adds G-series, I2C/DDC, MAVEN TV-out, CRTC2, and PLL support.

Important build rules: `my-obj-$(CONFIG_FB_MATROX_G)` adds `g450_pll.o`, `matroxfb_g450.o`, and `matroxfb_crtc2.o` for G-series hardware. `obj-$(CONFIG_FB_MATROX)` builds the main driver objects: `matroxfb_base.o`, `matroxfb_accel.o`, `matroxfb_DAC1064.o`, `matroxfb_Ti3026.o`, `matroxfb_misc.o`, and any enabled `my-obj-y`. `obj-$(CONFIG_FB_MATROX_I2C)` builds `i2c-matroxfb.o`. `obj-$(CONFIG_FB_MATROX_MAVEN)` builds `matroxfb_maven.o` and `matroxfb_crtc2.o`.

Control flow: Kbuild evaluates config-dependent lists and links the selected objects as built-in or module objects according to the parent Kconfig choices. There is no runtime behavior in the Makefile, but it determines which exported symbols and module init functions exist.

State and persistence: no runtime state. The key persistence implication is link composition: enabling MAVEN or G-series can include `matroxfb_crtc2.o`, creating a secondary fbdev extension module/path in addition to the base device.

Dependencies and integration points: the object list reflects internal symbol dependencies: `matroxfb_base.o` needs the low-level switch exports from DAC files, `g450_pll.o` is used by G450/G550 code, `i2c-matroxfb.o` registers through `matroxfb_register_driver()`, and MAVEN/CRTC2 pieces depend on the base Matrox extension-driver API.

Risks: `matroxfb_crtc2.o` appears in both G and MAVEN conditionals; Kbuild normally handles duplicate object names in built-in lists, but configuration changes should be checked for duplicate-link warnings. Missing one of the low-level objects under a config option would surface as unresolved symbols or disabled hardware support.

Test signals: build matrix tests are the main signal: `CONFIG_FB_MATROX` alone, plus combinations with `CONFIG_FB_MATROX_G`, `CONFIG_FB_MATROX_I2C`, and `CONFIG_FB_MATROX_MAVEN` as built-in and modules. Inspect generated modules for expected `matroxfb`, `i2c-matroxfb`, MAVEN, and CRTC2 behavior.
