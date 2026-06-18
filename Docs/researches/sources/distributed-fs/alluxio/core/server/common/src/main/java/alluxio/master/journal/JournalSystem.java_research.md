# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalSystem.java

## Purpose
`JournalSystem` is the top-level abstraction for creating, applying, formatting, checkpointing, and switching master journals between standby and primary modes.

## Important APIs, Types, And Functions
Core APIs include `createJournal`, `start`, `stop`, `gainPrimacy`, `losePrimacy`, `suspend`, `resume`, `catchup`, `getCurrentSequenceNumbers`, `format`, `isFormatted`, `isEmpty`, `checkpoint`, sink management, and optional journal gRPC services. `Builder` selects `NoopJournalSystem`, `UfsJournalSystem`, or `RaftJournalSystem` from configuration and process type.

## Control Flow, State, Dependencies, Risks, And Tests
The documented flow starts journals in standby, catches up/replays state, then gains primacy to accept writes; losing primacy resets and rebuilds state from the log. `suspend`/`resume` support backup and catch-up operations. Persistent state is journal logs and checkpoints in UFS or embedded Raft storage. Dependencies include configuration, master services, journal sinks, state lock manager, Raft/UFS systems, and network service types. Risks include mode-transition race conditions, creating journals after start, checkpointing without effective state lock, wrong process type selecting the wrong Raft service, and corruption tolerance behavior in implementations. Tests should cover builder selection, mode transitions, catch-up, suspend callbacks, formatting, checkpointing, sink propagation, and empty-state detection for each backend.
