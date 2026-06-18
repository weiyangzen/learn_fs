# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/Kconfig

Purpose: Defines the `DVB_NGENE` kernel configuration option for Micronas nGene PCIe bridge cards.

Important APIs, types, and functions: This is Kconfig metadata rather than C code. `config DVB_NGENE` is a tristate option named "Micronas nGene support". It depends on `DVB_CORE`, `PCI`, and `I2C`, and conditionally selects many DVB frontend, tuner, LNB, and CI helper drivers under `MEDIA_SUBDRV_AUTOSELECT`.

Control flow: Build-time only. When enabled as built-in or module, Kbuild compiles the nGene composite object from the local Makefile. Autoselected dependencies ensure common supported card frontends are available when the media subsystem is configured to autoselect subdrivers.

State and persistence: No runtime state. The selected value persists in the kernel configuration and controls whether `ngene.o` is built.

Dependencies and integration points: Integration is with the media Kconfig tree. The selected symbols match attach paths in `ngene-cards.c`, including STV090x/STV6110x, LGDT330x, DRXK, TDA18271/TDA18212, STV0367, CXD2841ER, STV0910/STV6111, LNB controllers, and CXD2099 CI.

Risks: If `MEDIA_SUBDRV_AUTOSELECT` is disabled, users must manually enable the exact demod/tuner modules required by their PCI subsystem ID. Dependency coverage must stay aligned with new card-info entries; missing `select`s cause runtime attach failures that look like absent hardware.

Test signals: Kconfig tests should verify `DVB_NGENE=m` builds `ngene.ko`, dependencies prevent invalid configurations without PCI/I2C/DVB core, and all attach targets referenced in `ngene-cards.c` are either selected automatically or documented for manual selection.
