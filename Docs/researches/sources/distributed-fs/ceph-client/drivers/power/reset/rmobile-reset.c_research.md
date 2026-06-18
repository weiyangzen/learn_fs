# sources/distributed-fs/ceph-client/drivers/power/reset/rmobile-reset.c

## Purpose
Renesas R-Mobile/SH-Mobile reset driver.

## Important APIs, Types, and Functions
global `sysc_base2`, `rmobile_reset_handler()`, and platform probe.

## Control Flow
probe maps resource 1 of the system controller and registers restart; callback writes `RESCNT2_PRES` to request soft power-on reset.

## State and Persistence Behavior
global MMIO pointer persists; reset control bit persists until hardware resets.

## Dependencies and Integration Points
ARCH_RMOBILE/HAS_IOMEM, OF platform, sys-off restart.

## Risks and Edge Cases
uses resource index 1, so DT resource ordering is critical; global singleton; no confirmation beyond delay/log.

## Test Signals
Renesas DT resource mapping, restart register trace, and reboot.
