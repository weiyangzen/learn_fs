# sources/distributed-fs/ceph-client/drivers/net/phy/mdio_bus.c

## Purpose
`mdio_bus.c` implements the low-level MDIO bus access API exported to PHY and MDIO device drivers. It supplies locked and caller-locked Clause 22 and Clause 45 read/write/modify helpers, device lookup helpers, tracepoint emission, and per-address bus statistics accounting.

## Important APIs, Types, And Functions
- `mdiobus_get_phy()` returns a `struct phy_device` at an address only if the registered MDIO device is flagged as a PHY.
- `mdiobus_is_registered_device()` checks address occupancy through the bus `mdio_map`.
- `__mdiobus_read()/__mdiobus_write()` are unlocked Clause 22 accessors that require `bus->mdio_lock`.
- `__mdiobus_c45_read()/__mdiobus_c45_write()` are unlocked Clause 45 accessors using `read_c45`/`write_c45`.
- `mdiobus_read()/write()`, `mdiobus_c45_read()/write()`, and `_nested` variants take the bus lock around the corresponding unlocked operation.
- `__mdiobus_modify_changed()`, `mdiobus_modify()`, `mdiobus_modify_changed()`, `mdiobus_c45_modify()`, and `mdiobus_c45_modify_changed()` implement read/modify/write with changed/no-change reporting where exposed.
- `mdiobus_stats_acct()` updates transfers, errors, reads, and writes in `struct mdio_bus_stats` using `u64_stats` synchronization.

## Control Flow And State Behavior
Every bus operation validates that `addr < PHY_MAX_ADDR`, checks whether the bus supplies the relevant access method, performs the controller callback, emits `trace_mdio_access`, and updates the per-address stats. Public helpers take `bus->mdio_lock` with either normal or nested lock class; internal `__` helpers assert the lock is held. Modify helpers read first, merge `(old & ~mask) | set`, avoid writes when unchanged, and either return a changed indicator or collapse success to zero.

The file persists no independent state beyond updating `bus->stats[addr]`. It does not register devices or buses; it assumes `struct mii_bus` was initialized by provider code and that `mdio_map` is owned by registration logic.

## Dependencies And Integration Points
The file depends on Linux device, module, mutex/lockdep, tracepoint, MII, PHY, and `u64_stats` APIs. It integrates with hardware MDIO controller drivers through `struct mii_bus` callback pointers, with phylib through exported register accessors, with tracing through `trace/events/mdio.h`, and with sysfs statistics exposed by `mdio_bus_provider.c`.

## Risks And Edge Cases
- The unlocked accessors must not be called without the lock; lockdep assertions catch this in debug builds.
- MDIO callbacks may sleep or wait for interrupts, so the documented no-interrupt-context rule matters.
- Missing read/write callback pairs return `-EOPNOTSUPP`; provider registration also rejects incomplete pairs.
- Address validation guards only upper bound; call sites should not pass negative addresses.
- Stats update paths run with preemption disabled and must remain short.

## Test Signals
Test signals include tracepoint records for reads/writes, stats incrementing per address and globally, changed/no-change modify behavior, nested access under muxed/nested MDIO buses, callback absence returning `-EOPNOTSUPP`, address 32+ returning `-ENXIO`, and lockdep warnings if unlocked helpers are misused.
