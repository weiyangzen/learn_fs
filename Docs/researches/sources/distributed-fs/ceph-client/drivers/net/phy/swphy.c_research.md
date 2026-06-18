# sources/distributed-fs/ceph-client/drivers/net/phy/swphy.c

## Purpose
`swphy.c` emulates a small set of Clause 22 MII registers from `struct fixed_phy_status` for fixed-link software PHYs. It lets code that expects MDIO-like register reads observe link, speed, duplex, pause, and basic gigabit capability without real PHY hardware.

## Important APIs, Types, And Functions
`struct swmii_regs` holds synthesized `bmsr`, `lpa`, `lpagb`, and `estat` fragments. Static tables encode supported bits by speed and duplex. Public exports are `swphy_validate_state()` and `swphy_read_reg()`. `swphy_decode_speed()` maps integer speeds 10/100/1000 to internal table indexes.

## Control Flow
Validation checks only linked states and rejects unknown speeds with `-EINVAL`. Register reads reject register numbers above `MII_REGS_NUM`, decode speed and duplex, combine speed and duplex bit tables with bitwise AND, set link/autoneg-complete and link-partner bits only when `state->link` is true, then returns synthesized values for BMCR, BMSR, PHY IDs, LPA, STAT1000, and ESTATUS. Clause 45-over-Clause 22 control/data registers return an error instead of fake data; unknown supported-range registers return `0xffff`.

## State And Persistence
There is no stored state. Every read is derived from the caller-provided `fixed_phy_status`. The exported functions are pure except for warning logs on invalid speed.

## Dependencies And Integration Points
The file depends on MII bit definitions, phylib/fixed PHY structures, and `swphy.h`. It is used by fixed PHY infrastructure and any consumer needing software MII register emulation.

## Risks And Edge Cases
`swphy_read_reg()` warns and returns zero for invalid speed, so callers should validate state first. Only 10/100/1000 are representable. It always reports BMCR autoneg enabled and does not emulate every MII register. Returning `-1` for unsupported registers follows this local convention but can be ambiguous for callers expecting negative errno values.

## Test Signals
Validate linked and unlinked states for 10/100/1000 half/full duplex, pause/asym-pause propagation, invalid speed rejection, register-boundary behavior, Clause 45 register rejection, and fixed PHY users reading BMCR/BMSR/LPA/STAT1000/ESTATUS.
