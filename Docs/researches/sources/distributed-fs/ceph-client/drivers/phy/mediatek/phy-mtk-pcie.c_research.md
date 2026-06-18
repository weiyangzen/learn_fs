<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-pcie.c

Purpose: Implements MediaTek PCIe PHY initialization for MT8195, focused on software loading of eFuse impedance calibration values into PHY SIF registers.

Important APIs and types: `struct mtk_pcie_lane_efuse` stores per-lane TX PMOS/NMOS and RX data. `struct mtk_pcie_phy_data` describes lane count and eFuse support. `struct mtk_pcie_phy` stores device, PHY, SIF base, SoC data, global eFuse value, and per-lane eFuse array. Main callbacks/helpers are `mtk_pcie_phy_init()`, `mtk_pcie_read_efuse()`, and `mtk_pcie_efuse_set_lane()`.

Control flow: Probe maps the named `sif` resource, creates a PHY, loads match data, optionally attempts to read nvmem eFuse data, and registers a simple provider. eFuse read is optional; non-defer/non-ENOMEM failures are ignored by probe. When enabled, it reads `glb_intr` and three cells per lane (`tx_ln%d_pmos`, `tx_ln%d_nmos`, `rx_ln%d`) and validates nonzero lane data. `phy_init()` writes the global internal resistor selection and each supported lane's TX/RX impedance fields. The comment notes hardware resets these settings during suspend, so consumers should call init again on resume.

State and persistence: eFuse values are cached in memory after probe. Hardware SIF fields persist until reset or suspend-induced loss and are restored by `phy_init()`.

Dependencies and integration points: Uses generic PHY, named platform MMIO, OF match data, nvmem cells, and MediaTek IO field helpers. The PCIe controller is the PHY consumer.

Risks: Optional eFuse failures can silently leave default hardware calibration. Cell names must match lane count exactly. Only MT8195 data is present with two lanes. No power-on/off handling is provided.

Test signals: Probe with and without nvmem cells, defer behavior for missing nvmem provider, lane eFuse write readback, PCIe Gen3 link quality, suspend/resume re-init, and invalid all-zero lane data handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-pcie.c -->
