<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/Kconfig

Purpose: build configuration for the Bluecherry/Softlogic SOLO6x10 capture-card driver.

Important APIs, types, and functions: defines `CONFIG_VIDEO_SOLO6X10` as tristate "Bluecherry / Softlogic 6x10 capture cards (MPEG-4/H.264)". It depends on `PCI`, `VIDEO_DEV`, `SND`, and `I2C`; selects bit reversal, font support, `FONT_8x16`, videobuf2 DMA SG/contig, and `SND_PCM`.

Control flow: controls compilation of the multi-file `solo6x10` module and pulls in subsystems required by display/OSD, V4L2, DMA buffers, and ALSA audio.

State and persistence: no runtime state; only kernel build configuration.

Dependencies and integration points: V4L2, ALSA, PCI, I2C, videobuf2, font rendering, and bit-reversal helpers.

Risks: duplicate `select FONT_8x16` is harmless but redundant. Missing selected helpers would break OSD or buffer paths at build/link time.

Test signals: Kconfig dependency resolution, module build, and availability of V4L2/ALSA/videobuf2/font symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/Kconfig -->
