# sources/distributed-fs/ceph-client/drivers/net/phy/ste10Xp.c

## Purpose
`ste10Xp.c` is a phylib driver for STMicroelectronics STe101p and STe100p PHYs. It performs a software reset during initialization and provides vendor interrupt mask/status handling for autoneg-complete, remote-fault, and link-down events.

## Important APIs, Types, And Functions
The key functions are `ste10Xp_config_init()`, `ste10Xp_ack_interrupt()`, `ste10Xp_config_intr()`, and `ste10Xp_handle_interrupt()`. The `ste10xp_pdriver[]` table registers STe101p and STe100p IDs with generic suspend/resume and the driver-specific init/interrupt callbacks.

## Control Flow
Config init reads `MII_BMCR`, sets `BMCR_RESET`, writes it back, then busy-waits reading `MII_BMCR` until reset clears. Interrupt enable first clears pending status by reading `MII_XCIIS`, then writes `MII_XIE_DEFAULT_MASK` to `MII_XIE`; disable writes zero and acks afterward. The interrupt handler reads `MII_XCIIS`, checks the same mask, and triggers the phylib state machine when a relevant event occurred.

## State And Persistence
The driver has no private state. Runtime state lives in standard BMCR plus vendor interrupt registers. Interrupt configuration persists in PHY registers until changed, reset, suspend, or power loss.

## Dependencies And Integration Points
It depends on phylib, MII constants, module registration, and generic suspend/resume. It integrates only through `struct phy_driver` callbacks and MDIO device ID matching.

## Risks And Edge Cases
The reset wait loop has no timeout and could spin forever if the PHY never clears `BMCR_RESET` or MDIO reads fail after the initial write. The loop does not handle negative reads during polling. Interrupt mask comments mention STe101P but the logic is shared with STe100p.

## Test Signals
Probe both PHY IDs, verify reset completion, inject MDIO read/write failures, exercise interrupt enable/disable order, trigger each masked interrupt source, and test behavior when reset never clears.
