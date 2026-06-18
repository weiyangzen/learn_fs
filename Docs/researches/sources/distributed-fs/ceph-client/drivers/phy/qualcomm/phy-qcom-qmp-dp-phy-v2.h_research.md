# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v2.h

## Purpose
This header defines QMP v2 DisplayPort PHY register offsets for AUX interrupt handling, AUX BIST, VCO division, lane control, spare register, and status.

## Important APIs, Types, and Functions
It exports `QSERDES_V2_DP_PHY_AUX_INTERRUPT_MASK`, `AUX_INTERRUPT_CLEAR`, `AUX_BIST_CFG`, `VCO_DIV`, `TX0_TX1_LANE_CTL`, `TX2_TX3_LANE_CTL`, `SPARE0`, and `STATUS`. There are no functions.

## Control Flow
Including drivers use these constants when programming DP AUX behavior, lane enable/control state, link-rate VCO division, and status polling. This specific subset is only offsets; sequencing lives in the driver.

## State and Persistence
The header has no software state. Hardware state is in the DP PHY registers that these offsets name.

## Dependencies and Integration Points
It is a generation-specific register map companion to QMP DP PHY code. It should be paired only with QMP v2 DP PHY layouts and compatible-specific config that knows how to use these offsets.

## Risks and Edge Cases
The file contains a commented line beginning with `// /*`, which is harmless in C99-style kernel code but stylistically odd. Misapplying v2 offsets to v3+ hardware would affect AUX, VCO, lane, and status registers incorrectly.

## Test Signals
Useful signals are correct AUX interrupt masking/clearing, valid VCO division for supported link rates, lane enable behavior, and expected DP PHY status bits during link bring-up.
