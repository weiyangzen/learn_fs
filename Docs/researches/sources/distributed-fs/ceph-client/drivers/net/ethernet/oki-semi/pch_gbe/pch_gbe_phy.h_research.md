# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_phy.h

## Purpose
Private PHY helper interface for the PCH GBE driver.

## Important APIs, Types, And Functions
Defines `PCH_GBE_PHY_REGS_LEN` as 32 and `PCH_GBE_PHY_RESET_DELAY_US` as 10. Declares PHY ID, MIIM read/write, reset, power, RGMII, init, and hibernate-disable helpers.

## Control Flow
Main driver uses these prototypes during probe, open, stop, PM, and reset. Ethtool uses the register length and read helper for dumps.

## State And Persistence
No storage. Constants constrain PHY scan/dump length and reset timing.

## Dependencies And Integration Points
Requires `struct pch_gbe_hw` from `pch_gbe.h`.

## Risks And Edge Cases
The fixed length covers Clause 22 register space only; vendor/extended registers are not part of the generic dump length.

## Test Signals
Compile all PCH GBE objects and verify ethtool dumps include 32 PHY registers.
