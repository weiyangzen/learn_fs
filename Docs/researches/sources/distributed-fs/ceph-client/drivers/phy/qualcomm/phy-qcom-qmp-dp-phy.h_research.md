# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy.h

## Purpose
This common DP PHY header defines generation-independent QMP DisplayPort PHY offsets and bit masks for revision IDs, core config, AUX config, power-down control, TX drive/pre-emphasis muxing, and AUX error handling.

## Important APIs, Types, and Functions
It exports `QSERDES_DP_PHY_*` offsets for revision, config, mode, power-down, and AUX config registers. It also defines common bit masks for QSERDES v3 bias/clock buffer enable fields, DP TX driver and pre-emphasis mux/mask fields, `DP_PHY_PD_CTL_*` power-down bits, and AUX interrupt error masks. There are no functions.

## Control Flow
The combo driver uses these definitions in DP AUX initialization, DP mode/orientation selection, DP power-off, swing/pre-emphasis programming, and AUX error-mask writes. Version-specific headers add the VCO, lane-control, status, and AUX interrupt offsets that vary by generation.

## State and Persistence
This header has no state. The constants describe hardware register state owned by the parent PHY driver.

## Dependencies and Integration Points
It is included by QMP combo DP code and sits alongside `phy-qcom-qmp-dp-phy-v*.h` and `phy-qcom-qmp-dp-com-v3.h`. It is central to Type-C/DP lane power selection because `DP_PHY_PD_CTL_*` bits are used to power down or release lanes depending on lane count and orientation.

## Risks and Edge Cases
The bit names encode shared assumptions about DP PHY power-down polarity and TX mux behavior. Wrong use can leave AUX, PLL, or lane groups powered down when link training expects them active. Since the masks are common, callers must still select the correct generation-specific offsets.

## Test Signals
Useful validation includes correct AUX transaction behavior, DP lane power selection for 1/2/4-lane modes, successful voltage swing/pre-emphasis changes from link training, and reliable power-down on DP off.
