# sources/distributed-fs/ceph-client/drivers/iio/potentiostat/Makefile

## Purpose
Kbuild rule for IIO potentiostat drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_LMP91000` to `lmp91000.o`.

## Control Flow
Kbuild includes the object when the Kconfig symbol is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Pairs with the potentiostat Kconfig entry.

## Risks And Test Signals
Compile with `CONFIG_LMP91000=m/y` to verify object inclusion and module naming.
