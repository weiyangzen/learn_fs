# sources/distributed-fs/ceph-client/include/linux/phy/pcie.h

## Purpose
PCIe PHY mode constants shared by PCIe PHY providers and consumers.

## Important APIs, Types, and Functions
Defines `PHY_MODE_PCIE_RC`, `PHY_MODE_PCIE_EP`, and `PHY_MODE_PCIE_BIFURCATION` numeric mode values for root-complex, endpoint, and bifurcated operation.

## Control Flow
No executable flow. Consumers pass these constants to PHY mode-setting code.

## State and Persistence
No state. Hardware mode persistence is managed by the PHY provider.

## Dependencies and Integration Points
Used with generic PHY configuration paths and PCIe controller/PHY drivers, notably Rockchip-originated mode definitions.

## Risks
Numeric constants must not collide with other provider-specific mode values expected by drivers. Incorrect mode selection can prevent PCIe link training.

## Test Signals
PCIe RC/EP/bifurcation probe tests and compile coverage for drivers using these constants.
