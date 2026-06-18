# sources/distributed-fs/ceph-client/drivers/power/reset/brcm-kona-reset.c

## Purpose
Broadcom Kona reset-manager restart driver.

## Important APIs, Types, and Functions
global `kona_reset_base`, `kona_reset_handler()`, and probe map reset manager MMIO and register a high-priority restart handler.

## Control Flow
probe maps resource 0; restart writes password/access-enable to write-access register and then writes zero to soft-reset register.

## State and Persistence Behavior
global MMIO pointer persists for built-in driver lifetime; hardware reset manager state changes only during restart.

## Dependencies and Integration Points
platform resources, OF compatible `brcm,bcm21664-resetmgr`, MMIO, sys-off.

## Risks and Edge Cases
global singleton and no unregister path; write ordering/password constants are hardware-specific; no post-write failure detection.

## Test Signals
resource mapping failure, OF match, restart register trace, and actual reboot.
