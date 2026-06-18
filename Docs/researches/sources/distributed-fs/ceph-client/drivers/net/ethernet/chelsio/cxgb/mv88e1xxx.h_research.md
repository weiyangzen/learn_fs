# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88e1xxx.h

## Purpose
`mv88e1xxx.h` provides register numbers and bit definitions for Marvell 88E1xxx copper PHYs. It supplements Linux MII definitions with gigabit control/status registers, Marvell-specific interrupt bits, vendor register addresses, crossover/downshift controls, and PHY-specific status decoding helpers.

## Important APIs, Types, and Functions
The header exports no functions. It defines fallback constants for `BMCR_SPEED1000`, `ADVERTISE_PAUSE`, and `ADVERTISE_PAUSE_ASYM`; gigabit registers `MII_GBCR` and `MII_GBSR`; gigabit advertisement/status bits; Marvell interrupt causes such as link change, autoneg done, speed/duplex change, FIFO events, symbol errors, and autoneg errors; vendor register numbers 16 through 30; and bitfield helpers for MDI crossover mode, downshift enable/count, and PHY specific status fields for pause, link, resolved status, duplex, speed, cable length, and related state.

## Control Flow
There is no control flow in the header. `mv88e1xxx.c` uses these definitions to compose MDIO register writes for advertisement, speed/duplex, crossover, downshift, loopback, and interrupts, and to decode link status during interrupt handling and `get_link_status()`.

## State and Persistence
The state represented is PHY hardware state: advertisement registers, interrupt masks/status, vendor-specific control/status, LED controls, downshift configuration, and extended registers. The header owns no software state.

## Dependencies and Integration Points
It integrates with `mv88e1xxx.c`, `cphy.h` MDIO wrappers, Linux MII register definitions, and cxgb board initialization. Constants such as `V_PSSR_LINK`, `G_PSSR_SPEED()`, `V_DOWNSHIFT_ENABLE`, and `V_PSCR_MDI_XOVER_MODE()` are central to link management and ethtool link-setting behavior.

## Risks
Incorrect bit definitions cause misreported link status, wrong advertised capabilities, missed link-change interrupts, or bad crossover/downshift programming. Fallback definitions can diverge from newer kernel headers if assumptions change. The header does not encode which Marvell PHY revisions support each vendor register, so callers must keep board/chip checks in implementation code.

## Test Signals
Signals include correct `get_link_status()` speed/duplex/pause decoding, interrupt masks matching expected hardware events, advertisement register contents for ethtool-requested modes, downshift enable and count fields, crossover auto/manual behavior, and compatibility with kernel MII definitions on all configured builds.
