<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Makefile

Purpose: Makefile object composition for mt76x2 drivers.

Important APIs/types/functions: builds `mt76x2-common.o`, `mt76x2e.o`, and `mt76x2u.o`. Common objects are EEPROM, MAC, init, PHY, and MCU; PCIe adds probe/main/init/MCU/PHY; USB adds USB probe/init/main/MAC/MCU/PHY.

Control flow: build-system declarative file; Kconfig symbols decide which composite objects are linked.

State and persistence: no runtime state.

Dependencies/integration: Linux kbuild, `CONFIG_MT76x2_COMMON`, `CONFIG_MT76x2E`, and `CONFIG_MT76x2U`; mirrors header/API boundaries in source.

Risks: object omissions cause link failures or missing module init; wrong split can pull USB-only code into PCI builds or vice versa. Test signals include PCI-only, USB-only, and both-enabled module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Makefile -->
