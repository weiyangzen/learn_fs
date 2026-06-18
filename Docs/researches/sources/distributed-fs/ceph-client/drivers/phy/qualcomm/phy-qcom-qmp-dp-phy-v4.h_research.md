# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v4.h

## Purpose
This header defines QMP v4 DisplayPort PHY offsets, reflecting the v4 movement of AUX interrupt and status registers compared with v3.

## Important APIs, Types, and Functions
It exports offsets for v4 AUX interrupt mask/clear/status, `VCO_DIV`, lane-control registers, `SPARE0`, and `STATUS`. There are no functions or types.

## Control Flow
The combo driver's v4/v5/v6-style DP path uses these offsets for AUX initialization, lane control, VCO division, and status polling in `qmp_v456_configure_dp_phy()` and related callbacks when the compatible's register layout points at v4 definitions.

## State and Persistence
The file has no state. The register values are hardware state controlled by the parent PHY driver's init, configure, and power-off paths.

## Dependencies and Integration Points
It integrates with common DP PHY definitions and the QMP combo driver's register layout arrays. The v4 AUX interrupt status offset supports decoding with common AUX error masks from `phy-qcom-qmp-dp-phy.h`.

## Risks and Edge Cases
Because v4 offsets differ from v3, wrong layout selection can break AUX interrupt handling and status polling. The header does not include semantic masks for lane-control values, so correctness depends on the driver's magic constants and hardware documentation.

## Test Signals
DP link bring-up on v4-based SoCs, AUX interrupt/error reporting, and correct status polling after link enable are the primary validation signals.
