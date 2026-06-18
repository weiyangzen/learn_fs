
# sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/Makefile

## Purpose
Builds IXP4xx queue manager and NPE drivers according to Kconfig.

## Important APIs, Types, and Functions
No runtime APIs. Rules build `ixp4xx-qmgr.o` for `CONFIG_IXP4XX_QMGR` and `ixp4xx-npe.o` for `CONFIG_IXP4XX_NPE`.

## Control Flow
Kernel build links objects as built-in or modules according to tristate symbols.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes directory Kconfig symbols used by dependent IXP4xx networking/HSS drivers.

## Risks
Low build-rule risk; symbol/object mismatch would break shared services.

## Test Signals
Build matrix for each symbol as `m/y`.
