# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v7.h

Purpose: Provides the QSERDES v7 common/PLL offset map for high-speed QMP PHYs. It keeps mode-specific PLL fields while adding v7 common-mode, clock, and ready-status definitions.

Important APIs/types/functions: Exports `QSERDES_V7_COM_*` macros for SSC, clock dividers, charge pump, PLL R/C, core clock, lock compare, divider programming, high-speed clock selection, integration loop, VCO tune, clock enables, reset state machine, common config/mode, VCO DC control, and `C_READY_STATUS`. No runtime code.

Control flow: None. Static QMP init tables write selected offsets and the shared initialization flow later polls lock/ready status.

State and persistence: Header constants only; hardware PLL/common state persists until PHY reset or power collapse.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and used by v7 protocol descriptors.

Risks: v7 is close to v8 but not identical. Copying v8 PLL table entries without checking offsets can misconfigure clock synthesis.

Test signals: Build, PLL lock, C-ready polling, high-rate link-up, SSC behavior, and resume/reinit.
