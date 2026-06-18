<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/lxt.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/lxt.c

## Purpose
`lxt.c` supports Intel/Level One LXT970, LXT971, and LXT973 PHYs. It supplies interrupt handling for LXT970/971, reset/config setup for LXT970, an LXT973 fibre-mode probe path, and a special read-status implementation for the LXT973-A2 erratum where odd register reads can return stale even-register contents.

## Important APIs, Types, And Functions
Important functions are `lxt970_ack_interrupt()`, `lxt970_config_intr()`, `lxt970_handle_interrupt()`, `lxt970_config_init()`, `lxt971_ack_interrupt()`, `lxt971_config_intr()`, `lxt971_handle_interrupt()`, `lxt973a2_update_link()`, `lxt973a2_read_status()`, `lxt973_probe()`, and `lxt973_config_aneg()`. The registered `phy_driver` table has separate entries for LXT970, LXT971, LXT973-A2, and generic LXT973.

## Control Flow
LXT970 interrupt ack reads BMSR then ISR because status clears in that order. Interrupt enable acks before writing IER and acks after disabling. The handler repeats the BMSR/ISR read sequence and triggers the PHY state machine if the MINT bit is set. LXT971 uses its own ISR/IER registers and status mask.

LXT973-A2 status uses `lxt973a2_update_link()` to fake-read BMSR, read BMCR, and retry BMSR reads when the returned status equals the control value, avoiding the documented stale-read erratum. Autoneg status then reads advertisement and LPA, retries once if they are suspiciously equal, resolves 10/100 speed/duplex and pause, or uses fixed-status generic helpers when autoneg is disabled.

`lxt973_probe()` checks the port configuration register for fibre mode. Fibre mode forces 100 Mbps full duplex, disables autoneg, stores a non-NULL sentinel in `phydev->priv`, and sets `phydev->port = PORT_FIBRE`. `lxt973_config_aneg()` is a no-op for fibre mode.

## State And Persistence
The only software state is the `phydev->priv` sentinel used to remember LXT973 fibre mode. Hardware state includes interrupt masks/status, LXT970 config register, LXT973 PCR, and BMCR fibre forced mode.

## Dependencies And Integration Points
The file depends on PHYLIB generic suspend/resume, generic fixed status helper, MII conversion helpers, and PHY interrupt machinery. It integrates with MACs through normal PHYLIB speed/duplex/link reporting and through `phydev->port` for fibre mode.

## Risks
The LXT973 fibre sentinel uses a function pointer value in `phydev->priv`, which is opaque and easy to misuse if future code expects allocated private data. The A2 erratum workaround uses equality heuristics and limited retries; unusual valid register equality could still confuse status. LXT970 interrupt clearing depends on strict read ordering.

## Test Signals
Test LXT970/LXT971 IRQ enable/disable and handler paths, LXT970 config register zeroing, LXT973 copper autoneg, LXT973 fibre forced mode and autoneg no-op, LXT973-A2 stale-read retry behavior, fixed-speed status, pause resolution, and suspend/resume on supported entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/lxt.c -->
