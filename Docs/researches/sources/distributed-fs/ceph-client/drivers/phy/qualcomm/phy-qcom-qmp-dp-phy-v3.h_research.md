# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v3.h

## Purpose
This header defines QMP v3 DisplayPort PHY register offsets used by the combo driver for AUX interrupts, AUX BIST, VCO division, lane control, spare register, and status polling.

## Important APIs, Types, and Functions
The constants include `QSERDES_V3_DP_PHY_AUX_INTERRUPT_MASK`, `AUX_INTERRUPT_CLEAR`, `AUX_BIST_CFG`, `VCO_DIV`, `TX0_TX1_LANE_CTL`, `TX2_TX3_LANE_CTL`, `SPARE0`, and `STATUS`. There are no executable APIs.

## Control Flow
`phy-qcom-qmp-combo.c` uses these offsets through its v3 register layout and v3 AUX/DP configuration functions. DP initialization writes AUX config and lane control, programs VCO division by link rate, then polls the v3 status register.

## State and Persistence
No software state exists in the header. Hardware state persists in the mapped DP PHY register block until reset or power loss.

## Dependencies and Integration Points
The header is paired with `phy-qcom-qmp-dp-phy.h` for common DP PHY offsets/bits and with QSERDES/PCS generation headers in the combo driver. It is selected indirectly through compatible-specific register layout arrays.

## Risks and Edge Cases
Offsets are generation-specific and must not be reused for v4+ hardware where AUX/status locations moved. The header does not define masks for status interpretation; callers must know which bits to poll.

## Test Signals
Successful v3 DP AUX setup, link clock programming, lane-control writes, and status-bit polling during RBR/HBR/HBR2/HBR3 link training validate use of these definitions.
