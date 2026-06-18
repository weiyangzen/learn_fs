# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/Kconfig

Purpose: defines kernel configuration options for the Conexant cx25821 video driver and its optional ALSA DMA audio companion.

Important APIs and symbols: `VIDEO_CX25821` is a tristate depending on `VIDEO_DEV`, `PCI`, and `I2C`, selecting `I2C_ALGOBIT` and `VIDEOBUF2_DMA_SG`. `VIDEO_CX25821_ALSA` is a tristate depending on `VIDEO_CX25821` and `SND`, selecting `SND_PCM`.

Control flow: Kconfig selection determines whether `cx25821.o` and `cx25821-alsa.o` are built by the Makefile. Help text names the produced modules and explains the ALSA function-01 hardware requirement.

State and persistence: no runtime state. Configuration values persist in the kernel build configuration and control module availability.

Dependencies and integration points: integrates with the media PCI driver Kconfig tree, V4L2 core, PCI, I2C, videobuf2 DMA-SG, and ALSA PCM. The ALSA option depends on the base video driver because the audio module attaches to devices owned by the cx25821 PCI driver.

Risks: help text mentions audio PCI IDs `14f1:8801` or `14f1:8811`, while the ALSA source table in this snapshot contains `14f1:0920`; that mismatch can confuse users. Selecting `I2C_ALGOBIT` is conservative even though this implementation uses a custom register-backed `i2c_algorithm`.

Test signals: menuconfig visibility, allmodconfig builds, module load tests for `cx25821`, and optional `cx25821-alsa` load after a base device is present.
