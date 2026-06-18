# sources/distributed-fs/ceph-client/drivers/net/phy/swphy.h

## Purpose
`swphy.h` declares the software PHY emulation interface implemented by `swphy.c`. It keeps fixed PHY users independent from the implementation details of synthesized MII registers.

## Important APIs, Types, And Functions
The header forward-declares `struct fixed_phy_status` and declares `swphy_validate_state()` plus `swphy_read_reg()`.

## Control Flow
There is no control flow in the header. Consumers include it to validate a fixed-link status and to request an emulated MII register value.

## State And Persistence
The header owns no state and exposes no globals. All state comes from the caller-supplied `fixed_phy_status`.

## Dependencies And Integration Points
The include guard `SWPHY_H` prevents duplicate declarations. The header is local to the PHY subsystem and is included by `swphy.c` and fixed PHY code that needs these helpers.

## Risks And Edge Cases
The contract does not document exact return conventions for unsupported registers, so consumers must align with `swphy.c`. Any extension to support new speeds or registers requires keeping validation and read emulation synchronized.

## Test Signals
Build coverage for all includers, plus runtime fixed-link tests that call both declared functions through the fixed PHY stack.
