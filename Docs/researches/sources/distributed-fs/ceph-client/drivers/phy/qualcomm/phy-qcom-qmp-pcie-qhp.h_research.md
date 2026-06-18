# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie-qhp.h

## Purpose
This header defines Qualcomm QHP PCIe Gen3 QMP register offsets for COM, lane, and PCS blocks. It supports PCIe Gen3 PHY init tables elsewhere in the Qualcomm QMP PHY drivers.

## Important APIs, Types, and Functions
The constants are grouped into COM PLL/SSC/clock/tuning registers, lane driver/RX equalization/CDR/sigdet/DCC/RSM registers, and PCS TX magnitude/power-state/config registers. There are no functions or structures.

## Control Flow
Drivers include this header to build `qmp_phy_init_tbl` arrays that program Gen3 QHP PCIe COM, lane, and PCS blocks. Runtime sequencing, resets, polling, and clock control are handled by the including driver.

## State and Persistence
The header has no state. It names hardware registers whose state is set by parent driver table writes during PHY initialization and power transitions.

## Dependencies and Integration Points
It is a generation/protocol-specific register map for QMP PCIe drivers and pairs with the common QMP table helpers. The offsets cover analog PLL, TX, RX, equalization, signal detect, and PCS power settings needed for PCIe Gen3.

## Risks and Edge Cases
Because every symbol is a raw offset, incorrect pairing with non-QHP or non-Gen3 hardware can corrupt unrelated registers. Many registers are analog tuning controls, so values using these offsets must be validated through link stability and compliance testing, not just compile coverage.

## Test Signals
Validation comes from successful PCIe Gen3 link training, stable operation under ASPM/power-state transitions, PLL lock, receiver detection/signal-detect behavior, and absence of PHY initialization timeouts in the including driver.
