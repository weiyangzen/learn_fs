# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6_n4.h

Purpose: Defines QSERDES v6 N4 TX/RX lane offsets for newer N4 PHY layouts. It includes TX drive/emphasis, resistance, bias/high-Z/polarity, lane mode, band/interface, VMODE, and RX UCDR, IVCM, DFE, VGA/GM, signal detect, QPI, DFE DAC, mode tables, summer calibration, and backup control.

Important APIs/types/functions: Exports `QSERDES_V6_N4_TX_*` and `QSERDES_V6_N4_RX_*` macros. No functions or structures.

Control flow: No local flow. QMP init tables write these offsets using the common PHY register abstraction.

State and persistence: The header is stateless; writes affect persistent lane hardware state until reset/rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v6 N4 PCS maps and v6 common block definitions.

Risks: N4-specific RX mode offsets are not interchangeable with base v6/v6.20. Mistakes may only show up under one lane rate or signal condition.

Test signals: Build, N4 platform probe, link training at all supported rates, CDR/signal detect, equalization, and resume.
