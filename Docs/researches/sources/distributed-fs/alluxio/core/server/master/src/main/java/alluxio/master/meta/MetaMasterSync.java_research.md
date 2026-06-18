# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterSync.java

## Purpose
`MetaMasterSync` is a heartbeat executor used by standby masters to synchronize with the leader meta master. It registers the standby, sends periodic master heartbeats, and obeys leader commands such as re-registration.

## Important APIs and Types
- Implements `HeartbeatExecutor`.
- Holds the standby `Address`, a `RetryHandlingMetaMasterMasterClient`, and an `AtomicReference<Long>` master ID initialized to `-1`.
- `heartbeat(long)` performs registration if needed, sends heartbeat, and handles `MetaCommand`.
- `close()` closes the retrying meta-master client.

## Control Flow
On each heartbeat, if no ID is assigned, `setIdAndRegister` calls `getId` and `register` with `Configuration.getConfiguration(Scope.MASTER)`. It then calls `mMasterClient.heartbeat`. `handleCommand` ignores `MetaCommand_Nothing`, re-registers for `MetaCommand_Register`, logs `MetaCommand_Unknown`, and throws for unrecognized values. IO failures are logged and force client disconnect so the next heartbeat reconnects.

## State and Persistence
Local state is the assigned standby master ID. Cluster state is maintained on the leader via registration and heartbeat records. No journal writes happen here directly.

## Dependencies and Integration Points
Depends on heartbeat scheduling, Alluxio configuration scoped to `MASTER`, leader RPC client, and `MetaCommand` gRPC enum. It is part of HA standby master lifecycle.

## Risks and Edge Cases
- The class is `NotThreadSafe`; heartbeat scheduling should avoid concurrent `heartbeat` calls.
- A failed command after a heartbeat causes disconnect but keeps the local ID; subsequent command handling may re-register if asked.
- Unknown commands are logged without re-registration, while default enum cases throw.

## Test Signals
Tests should simulate first heartbeat registration, command-driven re-registration, IO exception disconnects, and close propagation to the client.
