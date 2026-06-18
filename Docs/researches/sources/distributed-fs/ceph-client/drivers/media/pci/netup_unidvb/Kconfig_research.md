# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/Kconfig

- Purpose: Kconfig entry for NetUP Universal DVB PCIe card support.
- Important APIs/types/functions: `config DVB_NETUP_UNIDVB` depends on DVB core, V4L2, PCI, I2C, SPI master; selects videobuf2 DVB/vmalloc and optional frontend/tuner/LNB helpers under autoselect.
- Control flow: Controls building a driver for dual-stream DVB-S/S2/T/T2/C/C2 cards with two CI slots.
- State and persistence: No runtime state; build-time only.
- Dependencies and integration points: Integrates PCI DVB bridge code with frontend subdrivers and SPI/I2C support.
- Risks: Autoselect choices must match hardware revisions; missing frontend modules break tuning though core may build.
- Test signals: Kconfig build matrix with `MEDIA_SUBDRV_AUTOSELECT` on/off and module link tests.
