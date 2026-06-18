<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5-rx-reg.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5-rx-reg.h

Purpose: Defines register offsets and bitfields for MediaTek MIPI CSI CD-PHY/DPHY receiver v0.5.

Important APIs and types: Provides offsets for ANA00, ANA18, ANA1C, ANA20, ANA24, ANA40, WRAPPER80, and ANAA8 blocks, plus masks for CPHY enable, bandgap, DPHY clock mode/select, equalizer tuning, reserve fields, async options, reset mode, and byte-clock inversion.

Control flow: No executable code. Macros are consumed by `phy-mtk-mipi-csi-0-5.c` during power-on/off and mode setup.

State and persistence: No software state. Definitions map to persistent analog receiver configuration bits in CSI PHY instances.

Dependencies and integration points: Included by the CSI v0.5 PHY implementation and relies on `BIT()`/`GENMASK()` being available through included translation units.

Risks: CSI0 and CSI1/CSI2 have similar but not identical field meanings; wrong macro choice can tune the wrong lane. Header comments clarify shared versus per-CSI naming, which is important when extending lane mappings.

Test signals: Compile coverage, CSI DPHY/CDPHY power-on register readback, camera capture on CSI0/1/2, and lane/equalizer tuning validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5-rx-reg.h -->
