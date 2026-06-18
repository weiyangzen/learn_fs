# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-com-v3.h

## Purpose
This header defines DP COM block offsets for QMP v3 and v4 combo PHY common-control registers. The combo driver uses these offsets to reset, power, switch Type-C polarity, and choose USB/DP operating modes.

## Important APIs, Types, and Functions
It exports preprocessor constants for `QPHY_V3_DP_COM_PHY_MODE_CTRL`, `SW_RESET`, `POWER_DOWN_CTRL`, `SWI_CTRL`, `TYPEC_CTRL`, `TYPEC_PWRDN_CTRL`, and `RESET_OVRD_CTRL`. There are no functions or data structures.

## Control Flow
The constants are consumed by `phy-qcom-qmp-combo.c`, especially in common init/exit and Type-C switching paths. Writes to these offsets establish software reset overrides, common power state, selected PHY mode, and Type-C lane orientation.

## State and Persistence
The header has no state. It names hardware registers whose values persist according to the PHY common-block power/reset domain.

## Dependencies and Integration Points
It is integrated by inclusion in QMP DP combo code and is specific to QMP v3/v4-style DP COM register layouts. It complements bit definitions local to the combo driver, such as `USB3_MODE`, `DP_MODE`, and reset override bits.

## Risks and Edge Cases
Using these offsets with an incompatible QMP generation can misprogram common reset or Type-C control registers. Since offsets are plain constants, version selection must be enforced by the including driver's compatible-specific config.

## Test Signals
Signals include successful common-block bring-up, correct Type-C orientation behavior, and successful USB/DP mode selection on v3/v4-based platforms.
