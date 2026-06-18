# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v8.h

Purpose: Defines base QMP v8 PCS offsets for common USB/PCIe-style PHY setup. The map includes reset/start, status, power control, lock detect, refgen, signal detect, RX config, alignment, TX/RX config, and equalization.

Important APIs/types/functions: Exports `QPHY_V8_PCS_*` macros, including `SW_RESET`, `PCS_STATUS1`, `POWER_DOWN_CONTROL`, `START_CONTROL`, `LOCK_DETECT_CONFIG*`, `REFGEN_REQ_CONFIG1`, `RX_SIGDET_LVL`, `RX_CONFIG`, `ALIGN_DETECT_CONFIG*`, `TX_RX_CONFIG*`, and `EQ_CONFIG*`. No executable APIs exist.

Control flow: None. Consumers use these offsets in static initialization tables, which the generic QMP path applies before enabling the PHY and polling readiness.

State and persistence: The file stores only constants; register values persist in the PCS block until reset or table rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used alongside v8 QSERDES COM/TXRX/LALB headers and protocol-specific PCS headers.

Risks: v8 has additional specialized headers for USB, PCIe, AON, and LALB blocks. Using the base PCS offset for a protocol-specific PCS register can target the wrong block.

Test signals: Build, probe, PCS status readiness, USB/PCIe link-up, equalization, and suspend/resume.
