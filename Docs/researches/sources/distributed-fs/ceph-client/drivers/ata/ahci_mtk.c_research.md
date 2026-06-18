# sources/distributed-fs/ceph-client/drivers/ata/ahci_mtk.c

Purpose: MediaTek AHCI platform driver that enables SoC SATA mode via syscon, sequences optional resets, and delegates host activation to `ahci_platform`.

Important APIs/types: `struct mtk_ahci_plat`, `mtk_ahci_platform_resets`, `mtk_ahci_parse_property`, `mtk_ahci_probe`, and generic AHCI port info.

Control flow: probe allocates private state, gets resources, parses optional `mediatek,phy-mode` and sets `SYS_CFG_SATA_EN`, asserts/deasserts `axi`, `sw`, and `reg` resets, enables resources, and activates the host. PM uses generic `ahci_platform` ops.

State/persistence: syscon regmap, reset handles, SATA mode bit, reset line state, and AHCI resource state.

Dependencies/integration: OF compatible `mediatek,mtk-ahci`, syscon/regmap, reset framework, `ahci_platform`, libata/SCSI.

Risks/test signals: optional reset handling relies on reset framework semantics; bad phy-mode phandle prevents mode selection. Test reset sequence, syscon programming, probe deferral, link detection, and PM.
