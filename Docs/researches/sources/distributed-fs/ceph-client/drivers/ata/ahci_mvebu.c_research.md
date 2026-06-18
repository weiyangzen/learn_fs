# sources/distributed-fs/ceph-client/drivers/ata/ahci_mvebu.c

Purpose: Marvell EBU AHCI driver for Armada 380/3700 configuring MBUS/vendor registers and preserving FBS state during engine stop for a PMP hot-swap erratum.

Important APIs/types: `struct ahci_mvebu_plat_data`, `ahci_mvebu_mbus_config`, `ahci_mvebu_regret_option`, `ahci_mvebu_armada_380_config`, `ahci_mvebu_armada_3700_config`, `ahci_mvebu_stop_engine`, `ahci_mvebu_probe`, and PM callbacks.

Control flow: probe selects OF platform data, gets/enables resources, installs custom `stop_engine`, runs SoC config, and activates. Armada 380 programs MBUS windows and regret bit; Armada 3700 sets a vendor bit and requests PHY suspend handling. Resume reruns platform config before host resume.

State/persistence: static platform data in `hpriv->plat_data`, MBUS windows, vendor bits, PHY suspend flag, and saved/restored `PORT_FBS` during engine stop.

Dependencies/integration: OF compatibles, Marvell MBUS API, `ahci_platform`, libahci engine hooks, and libata PM.

Risks/test signals: missing MBUS info fails Armada 380; engine-stop workaround is required for PMP/FBS hot-swap. Test MBUS programming, PMP/FBS hot-swap, resume recovery, and both Armada compatibles.
