# sources/distributed-fs/ceph-client/drivers/watchdog/pretimeout_panic.c

## Purpose
`pretimeout_panic.c` implements the watchdog pretimeout governor named `panic`. It intentionally panics the kernel when a pretimeout event fires.

## Important APIs, types, and functions
The file defines `pretimeout_panic`, `struct watchdog_governor watchdog_gov_panic`, and module init/exit wrappers for governor registration and unregistration.

## Control flow
Module init registers the governor. If selected, any watchdog pretimeout notification calls `panic("watchdog pretimeout event\n")`. Module exit unregisters the governor if the system has not panicked.

## State and persistence
There is no persistent state except framework registration. The side effect is a kernel panic, which may trigger crash dump/reboot policy outside this file.

## Dependencies and integration points
It depends on watchdog pretimeout governor APIs and kernel panic handling. Drivers such as MediaTek, Qualcomm, PM8916, Orion, and NPCM can feed events into this governor.

## Risks and test signals
Risks are deliberate high-impact behavior: selecting this governor turns a bark interrupt into immediate panic. Test signals include module load/unload, governor selection, forced pretimeout, panic notifier/crashdump integration, and ensuring non-selected governors are unaffected.
