# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v6.h

## Purpose
This header defines the QMP v6 DisplayPort PHY offsets used by combo PHY configurations for VCO division, AUX interrupt status, and PHY status.

## Important APIs, Types, and Functions
It provides `QSERDES_V6_DP_PHY_VCO_DIV`, `QSERDES_V6_DP_PHY_AUX_INTERRUPT_STATUS`, and `QSERDES_V6_DP_PHY_STATUS`. It contains no executable code.

## Control Flow
The combo driver uses these offsets through v6 register layout arrays while configuring DP link rates, checking AUX errors, and polling for PHY readiness during v6-class DP bring-up.

## State and Persistence
No software state exists. Hardware state is controlled by the parent QMP combo driver's power and configure callbacks.

## Dependencies and Integration Points
This file integrates with `phy-qcom-qmp-combo.c`, common DP PHY definitions, and v6 QSERDES/PCS headers. SoC configs such as SM8550/SM8650/SAR2130P use v6-era DP tables and layouts.

## Risks and Edge Cases
The v6 status offsets differ from v5/v4; wrong layout pairing can produce false timeouts or missed AUX error reporting. The header intentionally does not validate link rates or lane counts.

## Test Signals
DP link training at all supported rates, AUX read/write reliability, and absence of configure timeouts are the main signals that these offsets are correct.
