<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/Kconfig

Purpose: build configuration entry for the SMI PCIe DVBSky DVB driver.

Important APIs, types, and functions: defines `CONFIG_DVB_SMIPCIE` as tristate "SMI PCIe DVBSky cards". It depends on `DVB_CORE`, `PCI`, `I2C`, and `RC_CORE`; selects `I2C_ALGOBIT` and, under `MEDIA_SUBDRV_AUTOSELECT`, frontend/tuner helpers `DVB_M88DS3103`, `DVB_SI2168`, `DVB_TS2020`, `MEDIA_TUNER_M88RS6000T`, and `MEDIA_TUNER_SI2157`.

Control flow: Kconfig selection determines whether `smipcie.o` is built and whether common subdrivers are auto-enabled.

State and persistence: no runtime state. It persists kernel build-time configuration.

Dependencies and integration points: media PCI menu, DVB core, I2C bit-banging, RC core, and frontend/tuner modules used by `smipcie-main.c`.

Risks: without `MEDIA_SUBDRV_AUTOSELECT`, users must manually enable compatible frontend/tuner drivers or probe will fail at attach time. `RC_CORE` is a hard dependency because IR support is always initialized.

Test signals: `olddefconfig` dependency resolution, module build as `m` and built-in as `y`, and probe with/without autoselected frontend modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/Kconfig -->
