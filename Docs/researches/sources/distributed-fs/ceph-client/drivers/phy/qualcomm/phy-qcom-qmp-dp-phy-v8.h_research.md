# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v8.h

## Purpose
This header defines QMP v8 DisplayPort PHY offsets, including newer AUX-less timing and lane-drive registers used by v8/n3 combo PHY configurations.

## Important APIs, Types, and Functions
It exports offsets for `VCO_DIV`, `AUX_INTERRUPT_STATUS`, `TSYNC_OVRD`, lane-control registers, AUX-less config/timing registers, LFPS timing, lane drive levels, and `STATUS`. There are no functions.

## Control Flow
`qmp_v8_configure_dp_clocks()` and `qmp_v8_configure_dp_phy()` in the combo driver write the v8 AUX-less timing, LFPS, TSYNC override, lane-control, and lane-drive offsets, then poll the v8 status register during bring-up.

## State and Persistence
The header itself has no state. The values written to these registers are established during DP power-on and reset by the common block or platform power transitions.

## Dependencies and Integration Points
It is used with v8 DP QSERDES COM definitions and v8/n3 USB43DP combo configs. It complements the common DP PHY offsets for base config and power-down control.

## Risks and Edge Cases
`QSERDES_V8_DP_PHY_AUXLESS_SETUP_CYC` and `QSERDES_V8_DP_PHY_AUXLESS_SILENCE_CYC` are both defined as `0x0d8`; if this is not intentional for the hardware, one timing write overwrites the other. V8 offsets are not compatible with earlier QMP DP PHY generations. AUX-less and TSYNC programming are sensitive to hardware revision.

## Test Signals
Validation should include v8 DP link training at RBR/HBR/HBR2/HBR3, Type-C orientation changes, AUX/AUX-less behavior, and inspection of timeout-free status polling on Glymur/v8-class hardware.
