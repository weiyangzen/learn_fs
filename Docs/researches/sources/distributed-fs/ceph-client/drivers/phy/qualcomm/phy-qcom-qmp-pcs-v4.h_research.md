# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v4.h

Purpose: Supplies the QMP v4 USB/PCIe PCS register map. Compared with v3, the layout starts with revision/status and debug registers, then covers power control, in/out signal muxing, FLL, lock detect, test/BIST, Gen1/2 and Gen3/2 TX settings, receiver detect, alignment, RX idle, DCC, and equalization.

Important APIs/types/functions: Exports `QPHY_V4_PCS_*` macros, including `PCS_STATUS*`, `POWER_DOWN_CONTROL`, `START_CONTROL`, `INSIG_*`, `OUTSIG_*`, `LOCK_DETECT_CONFIG*`, `G12S1_*`, `G3S2_*`, `RX_SIGDET_*`, `ALIGN_DETECT_CONFIG*`, and `EQ_CONFIG*`. No functions or types.

Control flow: No direct flow. QMP init tables select offsets appropriate for each SoC and the shared PHY code applies them during bring-up.

State and persistence: Register writes program PCS link timing and equalization state in hardware until PHY reset or reinitialization.

Dependencies and integration points: Included by `phy-qcom-qmp.h` for common QMP users.

Risks: v4 changed offsets relative to older maps; reusing v3 constants or choosing v4_20 deltas incorrectly can program the wrong PCS fields.

Test signals: Compile coverage, probe, status polling, PCIe/USB link training, receiver-detect, equalization, suspend/resume, and debug status reads.
