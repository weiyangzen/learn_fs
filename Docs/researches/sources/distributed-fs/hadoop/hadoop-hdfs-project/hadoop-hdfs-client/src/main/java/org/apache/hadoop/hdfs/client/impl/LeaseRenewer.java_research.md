# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/LeaseRenewer.java

## Purpose
`LeaseRenewer` is the shared background renewer used by `DFSClient` instances that have files open for create or append. It ensures the NameNode sees periodic lease renewals so it does not treat the writer as failed and recover or reassign the lease.

## Important APIs, types, and functions
`getInstance(authority, ugi, dfsc)` returns a shared renewer for a NameNode authority and user, then registers the client. `remove(LeaseRenewer)` removes a renewer from the factory. `put(DFSClient)` starts or refreshes the daemon if the client is running. `closeClient(DFSClient)` unregisters a client and starts the empty grace period. `interruptAndJoin()` stops the daemon for tests/shutdown. `renew()` deduplicates clients by sorted client name and calls `DFSClient.renewLease`. The nested `Factory` and `Factory.Key` maintain the global `(authority, UGI) -> LeaseRenewer` map.

## Control flow
Adding a client updates the renewal period to the shortest half-RPC-timeout among registered clients. `put` starts a new `Daemon` when no daemon is running or the current one has expired, increments `currentId`, and uses `isLSRunning` to avoid multiple simultaneous daemons in one renewer. The daemon loop sleeps for `sleepPeriod`, renews when elapsed time reaches `renewal`, and exits if its id is stale, the renewer expired after being empty beyond `gracePeriod`, or the thread is interrupted. On `SocketTimeoutException`, it removes the renewer and closes all files being written with abort semantics; other `IOException`s log and retry later.

## State and persistence behavior
State is process-local: registered `DFSClient` list, renewal/grace/sleep timings, daemon reference, `currentId`, empty timestamp, factory key, instantiation trace for trace logging, and the static factory map. There is no disk persistence; the durable state being protected is the NameNode lease table.

## Dependencies and integration points
It depends on `DFSClient` methods (`getConf`, `getClientName`, `isClientRunning`, `renewLease`, `closeAllFilesBeingWritten`), `UserGroupInformation`, `HdfsConstants.LEASE_SOFTLIMIT_PERIOD`, `Daemon`, `Time`, `DFSClientFaultInjector`, and Hadoop exceptions/logging. It is called from DFSClient write lifecycle paths.

## Risks and test signals
Concurrency is the main risk: shared factory access, client list mutation, daemon id staleness, `AtomicBoolean` behavior, and empty grace expiry all interact. Tests should cover one renewer per authority/user, duplicate client registration, renewal period recalculation after client removal, daemon expiry and replacement, timeout abort behavior, `IOException` retry behavior, non-running client removal, trace logging, and close/interruption. The `isLSRunning` flag is set when a daemon starts and is not reset in this class, so tests should verify intended interaction with factory removal and creation of fresh renewers after daemon exit.
