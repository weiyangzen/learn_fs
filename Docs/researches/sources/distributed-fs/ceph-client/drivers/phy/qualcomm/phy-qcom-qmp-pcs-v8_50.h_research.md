# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v8_50.h

Purpose: Provides a minimal QMP v8.50 PCS delta for changed status and power-down offsets.

Important APIs/types/functions: Exports `QPHY_V8_50_PCS_PCS_STATUS1`, `QPHY_V8_50_PCS_POWER_DOWN_CONTROL`, and the include guard. No functions, types, or runtime data are present.

Control flow: No code executes. Variant-specific QMP configuration tables use these names when v8.50 layout differs from base v8.

State and persistence: Stateless address constants. Hardware status is read and power-down control is written through these offsets by common QMP code.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v8.50 SoC descriptors.

Risks: The tiny surface makes accidental fallback to base v8 constants likely. Incorrect status offset can make the driver poll a stale or unrelated register, while a wrong power-down offset can prevent PHY enable.

Test signals: Compile of v8.50 tables, probe, power-on/off sequencing, PCS status polling, and link-up on matching silicon.
