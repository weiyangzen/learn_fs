<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/st/Makefile

## Purpose
Kbuild mapping for ux500 PM domain support.

## Important APIs, Types, And Functions
Maps `CONFIG_UX500_PM_DOMAIN` to `ste-ux500-pm-domain.o`.

## Control Flow
Kbuild includes the driver when configured.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the ST Kconfig symbol.

## Risks
A stale mapping would remove ux500 provider support.

## Test Signals
Compile with `CONFIG_UX500_PM_DOMAIN=y`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/Makefile -->
