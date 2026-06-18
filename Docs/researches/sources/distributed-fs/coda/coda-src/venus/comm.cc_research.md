# sources/distributed-fs/coda/coda-src/venus/comm.cc

## Purpose
This file implements Venus communication setup, server objects, RPC connection caching, server probing helpers, error translation, and test hooks for simulated disconnect/reconnect.

## Important APIs, Types, and Functions
`CommInit()` initializes unset RPC2/SFTP parameters, validates COP modes, initializes connection/server tables, activates SFTP, calls `RPC2_Init`, and starts the probe daemon. `srvent::GetConn()` reuses an idle `connent` or binds through `Connect()`. `PutConn()` releases references and deletes dying idle connections. `connent::CheckResult()` maps Vice/RPC errors to Unix-style errors and marks bad connections. Server functions include `FindServer`, `GetServer`, `PutServer`, `Reset`, `ServerError`, `ServerUp`, `GetLiveness`, and `GetBandwidth`. Probe helpers include `ProbeServers`, `DoProbes`, `MultiBind`, `MultiProbe`, and `HandleProbe`.

## Control Flow
Startup establishes global communication state. File/volume code asks a server for a connection; if an idle matching connection exists it is reused, otherwise `srvent::Connect()` serializes binding with `Xbinding`, asks the realm/user layer to authenticate, and installs a new `connent`. Probing collects eligible servers, binds in parallel with `probeslave` workers, then uses `MRPC_MakeMulti` for `ViceGetTime`.

## State and Persistence Behavior
State is process-local: server table, connection table, callback connection handles, liveness flags, bandwidth estimates, and queue counts. Persistent filesystem state is affected indirectly by RPCs made over these connections.

## Dependencies and Integration Points
It depends on RPC2/SFTP, Vice stubs, realm/user authentication, `VDB` volume events, mariner logging, vproc scheduling, and timing/stat macros from `comm.h`. It is initialized from Venus startup and used throughout fsobj and volume code.

## Risks and Test Signals
Risks include refcount leaks in iterators, stale down/up transitions, binding serialization races, missed reset after RPC errors, and fail hook global side effects. Tests should simulate server up/down/NAK/timeouts, forced binds, parallel probes, bandwidth changes, and connection reuse under concurrent vprocs.
