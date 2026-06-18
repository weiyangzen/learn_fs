# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-ln-shrd-v5.h

Purpose: Defines the minimal QSERDES v5 lane-shared RX PI controls needed by some QMP configurations.

Important APIs/types/functions: Exports `QSERDES_v5_LN_SHRD_UCDR_PI_CTRL1` and `QSERDES_v5_LN_SHRD_UCDR_PI_CTRL2`. There are no functions, structures, or data objects.

Control flow: None. Init tables write these lane-shared offsets through normal QMP register write helpers when a PHY layout exposes UCDR PI controls in a shared lane block.

State and persistence: Stateless address definitions. Hardware CDR/PI settings persist until reset or reconfiguration.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used with QMP v5/v6 generation lane-shared descriptors.

Risks: The macro prefix uses lowercase `v5`, unlike most QSERDES headers. Renaming for style would break consumers unless all tables are updated.

Test signals: Build, lane initialization on matching SoCs, clock-data recovery stability, and link-up across supported rates.
