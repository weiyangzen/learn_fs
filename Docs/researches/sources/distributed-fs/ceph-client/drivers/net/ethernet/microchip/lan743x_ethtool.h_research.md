# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ethtool.h

## Purpose
This header declares the LAN743x ethtool register-dump ABI used by `lan743x_ethtool.c` and exports the driver's ethtool operations table.

## Important APIs and Types
`LAN743X_ETH_REG_VERSION` identifies the register-dump format. The first enum indexes common Ethernet registers in the dump buffer, ending at `MAX_LAN743X_ETH_COMMON_REGS`. The second enum indexes SGMII registers, ending at `MAX_LAN743X_ETH_SGMII_REGS`. `extern const struct ethtool_ops lan743x_ethtool_ops` is consumed by `lan743x_main.c`.

## Control Flow and State
There is no runtime control flow in the header. Its enum ordering is persistent ABI-like state for ethtool register dump interpretation: `lan743x_get_regs` writes values into a `u32` array at these indexes and advertises version 1.

## Dependencies and Integration Points
The header includes ethtool declarations and is shared between main probe code and ethtool implementation. The enum names map directly to CSR and SGMII MMD reads in `lan743x_ethtool.c`.

## Risks
Adding or reordering enum members changes the register dump layout. The comments require new registers to be added above the max sentinel; tooling that decodes dumps must track `LAN743X_ETH_REG_VERSION`.

## Test Signals
`ethtool -d` should report a buffer length matching common registers plus SGMII registers when `adapter->is_sgmii_en` is true. Build coverage catches missing ethtool ops declarations.
