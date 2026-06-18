# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/Makefile

## Purpose
Connects the OKI vendor directory to the PCH GBE module directory.

## Important APIs, Types, And Functions
The build rule is `obj-$(CONFIG_PCH_GBE) += pch_gbe/`.

## Control Flow
When `CONFIG_PCH_GBE` is built-in or module, kbuild descends into `oki-semi/pch_gbe/`.

## State And Persistence
No runtime state; build graph only.

## Dependencies And Integration Points
Depends on `CONFIG_PCH_GBE` from nested Kconfig and the parent Ethernet make hierarchy.

## Risks And Edge Cases
Vendor selection alone does not enter the directory. A path typo drops the driver from builds.

## Test Signals
`CONFIG_PCH_GBE=m` should build the nested `pch_gbe` module; disabling it should skip the directory.
