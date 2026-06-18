# sources/distributed-fs/ceph-client/drivers/watchdog/pretimeout_noop.c

## Purpose
`pretimeout_noop.c` implements the watchdog pretimeout governor named `noop`. It records a pretimeout event in the kernel log without otherwise changing system state.

## Important APIs, types, and functions
The file defines `pretimeout_noop`, `struct watchdog_governor watchdog_gov_noop`, and module init/exit functions calling `watchdog_register_governor` and `watchdog_unregister_governor`.

## Control flow
Module init registers the governor with the watchdog pretimeout framework. When selected and a driver calls `watchdog_notify_pretimeout`, the governor logs `watchdog%d: pretimeout event`. Module exit unregisters the governor.

## State and persistence
There is no persistent state beyond governor registration. Log output is the only side effect.

## Dependencies and integration points
It depends on `watchdog_pretimeout.h`, watchdog governor APIs, and watchdog devices with pretimeout support.

## Risks and test signals
Risks are minimal, but the module description says "Panic" despite noop behavior, which can confuse users. Test signals include module load/unload, governor selection, pretimeout event logging, and coexistence with other governors.
