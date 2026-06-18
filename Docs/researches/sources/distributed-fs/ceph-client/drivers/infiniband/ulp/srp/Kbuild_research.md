# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/Kbuild

## Purpose
Defines the kernel build object for the InfiniBand SRP upper-layer protocol driver.

## Important APIs, Types, And Functions
Contains one build rule: `obj-$(CONFIG_INFINIBAND_SRP) += ib_srp.o`. No C APIs or runtime types are defined here.

## Control Flow
Kbuild includes `ib_srp.o` in the build when `CONFIG_INFINIBAND_SRP` is enabled as built-in or module. The actual source aggregation is handled by surrounding kernel build conventions and the `ib_srp` source file(s).

## State And Persistence
No runtime state. Its only persistent effect is build graph selection.

## Dependencies And Integration Points
Tied directly to the `INFINIBAND_SRP` Kconfig symbol declared in the adjacent `Kconfig`. Integrates with the kernel's `obj-y`/`obj-m` mechanism.

## Risks
Renaming the object or mismatching the Kconfig symbol would silently drop or misbuild SRP support. This file is intentionally minimal, so risk is mostly build configuration drift.

## Test Signals
Run kernel config builds with `CONFIG_INFINIBAND_SRP=y`, `m`, and unset; verify `ib_srp.o` is built only in enabled cases and module packaging names remain expected.
