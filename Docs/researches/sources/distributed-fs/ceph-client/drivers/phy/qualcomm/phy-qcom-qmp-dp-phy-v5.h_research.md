# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v5.h

## Purpose
This compact header defines the QMP v5 DisplayPort PHY offsets needed by common combo code: VCO division, AUX interrupt status, and PHY status.

## Important APIs, Types, and Functions
It exports `QSERDES_V5_DP_PHY_VCO_DIV`, `QSERDES_V5_DP_PHY_AUX_INTERRUPT_STATUS`, and `QSERDES_V5_DP_PHY_STATUS`. There are no functions or structures.

## Control Flow
QMP combo configurations using a v5 DP PHY layout refer to these offsets when setting link-rate VCO division and polling DP PHY readiness/status. AUX status can be paired with the common AUX error masks.

## State and Persistence
The header has no state. The named registers are programmed or observed by the parent driver during DP configure, power-on, calibration, and error handling.

## Dependencies and Integration Points
It is generation-specific glue for the QMP combo driver and common DP PHY bit definitions. It assumes other generation headers provide the SerDes and TX register definitions used alongside these offsets.

## Risks and Edge Cases
Only a minimal register subset is defined, so callers needing v5-specific lane-control or AUX mask/clear offsets must use other layouts or avoid unsupported operations. Incorrect generation selection will affect link-rate setup and status polling.

## Test Signals
Expected validation is successful DP link training on v5 hardware, correct pixel/link clock rates, and status/AUX behavior matching hardware expectations.
