# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-qserdes-com-v8.h

## Purpose
This header defines QSERDES COM register offsets for QMP v8 DisplayPort PLL/SerDes programming. It supports v8 DP link-rate tables in the combo driver.

## Important APIs, Types, and Functions
The constants cover v8 COM registers for HS clock selection, VCO calibration compare codes, SSC step/per settings, charge pump/R/C controls, core clock division, lock compare, divider fractions, loop gains, VCO tune, bias/clock enables, sysclk controls, resets, lock enable, clock select, common config, clock forwarding, and ready/status registers. There are no functions.

## Control Flow
`phy-qcom-qmp-combo.c` uses these offsets in v8 DP SerDes init tables and link-rate-specific RBR/HBR/HBR2/HBR3 tables. During DP power-on, the driver writes the base v8 SerDes table, applies the selected link-rate table, then polls COM ready/status registers through the configured layout.

## State and Persistence
No software state is stored here. Hardware state is the v8 DP PLL/SerDes programming established by the parent driver's table writes.

## Dependencies and Integration Points
This header is paired with v8 DP PHY offsets and QMP combo configs such as Glymur USB43DP. It is consumed through `QMP_PHY_INIT_CFG()` tables from `phy-qcom-qmp-common.h`.

## Risks and Edge Cases
The offsets are highly hardware-generation-specific and mostly analog PLL tuning registers. Incorrect values or accidental use on non-v8 hardware can prevent PLL lock or create marginal DP signal behavior. Because table writes are not read back, errors usually surface only as link-training or status-poll failures.

## Test Signals
Signals include successful COM ready status, stable PLL lock at all supported DP link rates, correct DP link/pixel clock rates, and no timeout in v8 DP configure paths.
