# sources/distributed-fs/ceph-client/drivers/power/reset/ocelot-reset.c

## Purpose
Microsemi Ocelot/Sparx5 syscon restart driver.

## Important APIs, Types, and Functions
restart context with regmap/mask/offset data and sys-off restart handler.

## Control Flow
probe resolves syscon registers from DT, registers restart, and callback writes reset bits then delays/logs if reset does not happen.

## State and Persistence Behavior
context is device-managed; syscon reset bit persists until reset.

## Dependencies and Integration Points
MFD_SYSCON, MSCC_OCELOT/ARCH_SPARX5, OF, sys-off.

## Risks and Edge Cases
generic syscon writes rely on binding-provided offsets/masks; no hardware completion detection beyond timeout.

## Test Signals
Ocelot/Sparx5 DT, mask/offset validation, and reboot.
