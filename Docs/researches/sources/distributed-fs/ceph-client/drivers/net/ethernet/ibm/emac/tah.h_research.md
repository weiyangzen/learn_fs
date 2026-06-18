
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/tah.h

## Purpose
`tah.h` declares TAH register layout, instance state, mode-register bit definitions, public APIs, and no-op stubs when TAH support is disabled.

## Important APIs, Types, and Functions
`struct tah_regs` maps revision, mode, status, and transmit status registers. `struct tah_instance` stores mapped MMIO, lock, user count, and platform device. Bitfields such as `TAH_MR_SR`, `TAH_MR_CVR`, `TAH_MR_ST_*`, `TAH_MR_TFS_*`, `TAH_MR_DTFP`, and `TAH_MR_DIG` drive reset/configuration. Public functions cover init/exit, attach/detach, reset, and register dump.

## Control Flow
When `CONFIG_IBM_EMAC_TAH` is enabled, EMAC module init registers the TAH platform driver and EMAC probe/configuration can call the real functions. When disabled, init succeeds, attach returns `-ENXIO`, reset/detach are no-ops, and register dump helpers report no length.

## State and Persistence
The header defines volatile driver/MMIO state only. Register values persist only as hardware configuration during driver runtime.

## Dependencies and Integration Points
It integrates with EMAC core feature detection and ethtool register dumping. Its stubs let `core.c` compile without TAH, but device trees that declare TAH require the Kconfig option.

## Risks
Stub behavior means a missing config becomes a runtime probe/config failure. The mode bit definitions are hardware-specific and have no type checking. User count is simple and relies on implementation locking.

## Test Signals
Builds with/without `CONFIG_IBM_EMAC_TAH`, EMAC probe behavior for TAH device-tree phandles, and correct ethtool register dump sizing validate this header.
