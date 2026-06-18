# sources/distributed-fs/ceph-client/drivers/power/reset/restart-poweroff.c

## Purpose
fallback poweroff driver that restarts instead of powering off.

## Important APIs, Types, and Functions
`restart_poweroff_do_poweroff()` and platform probe.

## Control Flow
probe registers a poweroff handler; callback sets `reboot_mode = REBOOT_HARD` and calls `machine_restart(NULL)`.

## State and Persistence Behavior
no private state; global reboot mode is changed for the final path.

## Dependencies and Integration Points
sys-off poweroff, reboot core, OF compatible `restart-poweroff`.

## Risks and Edge Cases
does not truly power off; depends on bootloader holding or halting after reset; can surprise users expecting power removal.

## Test Signals
poweroff command on supported boards, reboot-mode value, and fallback ordering.
