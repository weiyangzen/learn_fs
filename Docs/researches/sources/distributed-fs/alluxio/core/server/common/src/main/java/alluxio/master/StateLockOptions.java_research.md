# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/StateLockOptions.java

## Purpose
`StateLockOptions` carries the timing and mode parameters for exclusive state-lock acquisition.

## Important APIs, Types, And Functions
It stores `GraceMode`, grace try duration, sleep duration, and total timeout. Factory methods provide defaults for shell backups, daily backups, and immediate forced locking by reading configuration keys.

## Control Flow, State, Dependencies, Risks, And Tests
The options are immutable after construction and have no persistence. `StateLockManager` consumes them to decide whether to timeout or force after the grace cycle. Dependencies are `Configuration`, `PropertyKey`, Java lock documentation, and the `GraceMode` enum. Risks include zero-duration defaults changing lock behavior dramatically, misconfigured durations causing long backup stalls, and no local validation of negative values. Tests should validate config-driven factories, forced default behavior, and manager integration for timeout versus forced modes.
