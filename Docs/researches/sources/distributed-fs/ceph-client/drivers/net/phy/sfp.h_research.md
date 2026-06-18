# sources/distributed-fs/ceph-client/drivers/net/phy/sfp.h

## Purpose
`sfp.h` is the private header shared by the SFP socket driver and bus layer. It defines quirk and socket-operation contracts and declares the socket-to-bus notification functions implemented in `sfp-bus.c`.

## Important APIs, Types, And Functions
`struct sfp_quirk` matches vendor and part strings and can provide a capability adjustment callback plus a runtime fixup callback. `struct sfp_socket_ops` lets the bus call into a socket for attach/detach, start/stop, signal-rate selection, and ethtool module EEPROM access. Function declarations cover PHY attach/detach, link up/down, module insert/remove/start/stop, and socket register/unregister.

## Control Flow
`sfp.c` implements `sfp_socket_ops` and registers a socket with `sfp_register_socket()`. `sfp-bus.c` calls those ops when an upstream appears or changes state, while `sfp.c` calls the declared notification functions to tell the upstream side about module PHYs, link state, and module lifecycle.

## State And Persistence
The header owns no state. It forward-declares `struct sfp` and relies on `struct sfp_bus`, `struct phy_device`, EEPROM IDs, and ethtool structures from included Linux headers.

## Dependencies And Integration Points
The header includes `<linux/ethtool.h>` and `<linux/sfp.h>`. It is private to `drivers/net/phy`, not a UAPI contract, and forms the local integration boundary between `sfp.c` and `sfp-bus.c`.

## Risks And Edge Cases
Callback contracts are implicit: callers must honor RTNL/state-machine locking rules documented in the C files. Adding a socket operation requires updates to both struct initializers and registration logic. Because quirk matching uses fixed-width EEPROM strings, quirk callbacks must be conservative.

## Test Signals
Build coverage should catch signature drift. Runtime coverage comes from SFP registration, module insertion, PHY attachment, link notifications, and ethtool EEPROM operations that traverse every declared callback path.
