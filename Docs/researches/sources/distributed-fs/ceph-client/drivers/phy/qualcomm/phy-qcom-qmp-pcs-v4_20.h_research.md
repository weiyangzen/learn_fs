# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v4_20.h

Purpose: Captures the small PCS offset differences for QMP v4.20 hardware, mainly signal-detect and equalization registers whose addresses differ from base v4.

Important APIs/types/functions: Exports `QPHY_V4_20_PCS_RX_SIGDET_LVL`, `QPHY_V4_20_PCS_EQ_CONFIG2`, `QPHY_V4_20_PCS_EQ_CONFIG4`, and `QPHY_V4_20_PCS_EQ_CONFIG5`. There are no functions or types.

Control flow: No direct flow. SoC-specific init tables choose these macros instead of the base v4 names when the PCS layout is v4.20.

State and persistence: Only identifies hardware offsets. Programmed values persist in PCS equalization and signal-detect logic until reset or rewrite.

Dependencies and integration points: Included through `phy-qcom-qmp.h` and paired with v4/v4.20 QMP configuration tables.

Risks: Because this is a delta header, missing a v4.20-specific constant may lead developers to accidentally use a base v4 offset that writes the wrong register.

Test signals: Build of v4.20 users, link training on affected SoCs, receiver-detect threshold behavior, and stable equalization at target rates.
