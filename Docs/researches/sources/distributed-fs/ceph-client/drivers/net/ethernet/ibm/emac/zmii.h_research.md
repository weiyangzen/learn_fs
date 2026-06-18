
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/zmii.h

## Purpose
`zmii.h` declares the ZMII bridge register layout, instance state, public API, and disabled-config stubs for the IBM EMAC driver.

## Important APIs, Types, and Functions
`struct zmii_regs` maps function-enable, speed-select, and SMII status registers. `struct zmii_instance` stores mapped registers, mutex, selected PHY mode, user count, saved firmware FER, and platform device. API declarations cover init/exit, attach/detach, MDIO get/put, speed selection, and ethtool register dumping.

## Control Flow
With `CONFIG_IBM_EMAC_ZMII`, EMAC core can register and call the real ZMII helper. Without it, init succeeds, attach returns `-ENXIO`, and the remaining operations are no-ops or zero-length dump helpers.

## State and Persistence
The header defines volatile driver state and MMIO structures only. `fer_save` captures firmware-programmed register state for runtime autodetection but is not persistent across boots.

## Dependencies and Integration Points
The API is called from EMAC probe/remove, MDIO transactions, link speed changes, and ethtool register dumps. Stub behavior ties device-tree use of ZMII to the Kconfig option.

## Risks
Disabled stubs can defer configuration problems to runtime. The single `mode` field means all users of a ZMII instance must be compatible. `users` is simple and relies on implementation locking.

## Test Signals
Builds with/without `CONFIG_IBM_EMAC_ZMII`, runtime probe success for ZMII phandles, invalid mixed-mode rejection, and register dump size correctness are important signals.
