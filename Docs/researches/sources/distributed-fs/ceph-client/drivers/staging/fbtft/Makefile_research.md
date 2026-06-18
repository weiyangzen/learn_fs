<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/Makefile

Purpose: builds the FBTFT core library and selected panel/controller modules.

Important APIs/types/functions: `obj-$(CONFIG_FB_TFT) += fbtft.o` combines `fbtft-core.o`, `fbtft-sysfs.o`, `fbtft-bus.o`, and `fbtft-io.o`; subsequent `obj-$(CONFIG_FB_TFT_*)` entries build individual `fb_*.o` drivers.

Control flow: kbuild produces the shared core when the top-level symbol is enabled and adds per-panel objects according to child symbols.

State and persistence: build-only state.

Dependencies and integration: tied to `fbtft/Kconfig` and the source files in this directory.

Risks: `fb_ssd1325.o` is keyed by `CONFIG_FB_TFT_SSD1305` rather than a visible `CONFIG_FB_TFT_SSD1325` symbol in this snapshot, so SSD1325 build selection appears coupled to SSD1305. Any symbol/file mismatch breaks module availability.

Test signals: build each FBTFT option individually, verify module names, and specifically check whether `fb_ssd1325.o` is built when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/Makefile -->
