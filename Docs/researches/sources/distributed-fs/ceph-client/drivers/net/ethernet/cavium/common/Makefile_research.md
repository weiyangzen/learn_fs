# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/Makefile

## Purpose
This Makefile builds the shared Cavium PTP clock driver object when `CONFIG_CAVIUM_PTP` is enabled.

## Important APIs, Types, And Functions
The only build artifact is `cavium_ptp.o`, which exports `cavium_ptp_get()` and `cavium_ptp_put()` from `cavium_ptp.c`.

## Control Flow
Kbuild includes `cavium_ptp.o` in the built-in or module object list according to the tristate state of `CONFIG_CAVIUM_PTP`.

## State And Persistence
No runtime state is defined here; it controls object inclusion.

## Dependencies And Integration Points
It is reached through the Cavium top-level Makefile and depends on the Kconfig constraints for `CAVIUM_PTP`.

## Risks
Any Cavium network driver relying on PTP helpers must handle the Kconfig-disabled inline stubs in `cavium_ptp.h`; this Makefile does not force consumers to include the object.

## Test Signals
Build with `CAVIUM_PTP=y`, `m`, and disabled. Confirm module exports are present when enabled and consumers build against header stubs when disabled.
