# sources/distributed-fs/ceph-client/drivers/net/phy/davicom.c

## Purpose
`davicom.c` supports Davicom DM9161E/B/C/A and DM9131 10/100 PHYs. It configures MII/RMII mode, scrambler/10BT defaults, isolates the PHY while changing autoneg settings, and implements vendor interrupt handling.

## Important APIs, Types, And Functions
Register definitions cover the DM9161 SCR, interrupt register, and 10BTCSR. `dm9161_config_init()` isolates the PHY, validates `phydev->interface`, writes MII or RMII SCR defaults, restores 10BTCSR, and enables autoneg. `dm9161_config_aneg()` isolates before delegating to `genphy_config_aneg()`. `dm9161_config_intr()`, `dm9161_ack_interrupt()`, and `dm9161_handle_interrupt()` implement link/speed/duplex interrupt handling.

## Control Flow
Initialization starts by writing `BMCR_ISOLATE`, then selects SCR value based on MII versus RMII. Unsupported interfaces return `-EINVAL`. After vendor register setup, BMCR is written with `BMCR_ANENABLE` to reconnect and enable autoneg. Interrupt enable clears pending state, unmasks stop/mask bits, and writes the interrupt register; disable masks all interrupt sources before acknowledging. The handler reads the interrupt register and triggers phylib only when change bits are present.

## State And Persistence
The driver has no private state. Register configuration persists until PHY reset. The DM9131 entry only wires interrupts and does not use the DM9161 config init/aneg paths.

## Dependencies And Integration Points
The file depends on phylib and generic autoneg. It registers four PHY IDs. MAC/platform integration must provide a supported `phydev->interface` for DM9161 variants.

## Risks And Edge Cases
Incorrect interface mode causes init failure. Isolating before autoneg/config changes can briefly remove the PHY from the bus/link path. Interrupt status and enable bits share one register with separate high/low fields. The `DM9161_DELAY` macro is unused.

## Test Signals
Test MII and RMII initialization, unsupported interface failure, autoneg after isolate, link/speed/duplex interrupt handling, and the DM9131 path where generic init is used but vendor interrupts are active.
