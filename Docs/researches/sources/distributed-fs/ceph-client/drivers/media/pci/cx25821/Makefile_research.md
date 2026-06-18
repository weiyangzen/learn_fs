# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/Makefile

Purpose: maps cx25821 Kconfig symbols to object files for the base video driver and ALSA companion module.

Important APIs and entries: `cx25821-y` links `cx25821-core.o`, `cx25821-cards.o`, `cx25821-i2c.o`, `cx25821-gpio.o`, `cx25821-medusa-video.o`, and `cx25821-video.o` into `cx25821.o`. `obj-$(CONFIG_VIDEO_CX25821)` builds the base module and `obj-$(CONFIG_VIDEO_CX25821_ALSA)` builds `cx25821-alsa.o`.

Control flow: kbuild compiles the listed implementation files into a single base module, while the ALSA file remains a separate module that late-initializes against the registered PCI driver.

State and persistence: no runtime state. Build output shape is determined by selected Kconfig symbols.

Dependencies and integration points: depends on the Kconfig symbols from `Kconfig` and on the source file boundaries in this directory. The base module must export symbols used by the ALSA module, such as SRAM channel setup and IRQ bit printing.

Risks: adding new implementation files requires updating `cx25821-y`; forgetting to do so can leave declarations unresolved or functionality omitted. ALSA is not linked into the base module, so symbol export and module load ordering matter.

Test signals: `make M=drivers/media/pci/cx25821` style builds with base-only and base-plus-ALSA configurations.
