# sources/distributed-fs/beegfs/client_module/source/common/toolkit/TimeTk.h

## Purpose
Provides a tiny schedulable-time conversion helper.

## Important APIs and control flow
`TimeTk_msToJiffiesSchedulable` converts milliseconds to jiffies with `msecs_to_jiffies` and caps the result to `MAX_SCHEDULE_TIMEOUT - 1`, avoiding the sentinel infinite-sleep value.

## State, dependencies, integration
No state is stored. `SocketTk_poll` uses it to compute bounded schedule timeouts for poll loops.

## Risks and test signals
Very large millisecond values saturate. Tests should cover zero, small values, and values at or above `MAX_SCHEDULE_TIMEOUT` conversion boundaries.
