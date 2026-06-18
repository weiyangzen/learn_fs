# sources/distributed-fs/coda/coda-src/vice/srv.cc

## Purpose
`srv.cc` is the Coda vice file server main program. It owns process startup, configuration, RVM initialization, RPC2/SFTP setup, volume/callback/resolution subsystem initialization, LWP worker creation, request dispatch loops, shutdown, log rotation, database/key refresh, and runtime counters.

## Important APIs, types, and functions
- Global configuration/state includes authentication, resolution, SHA, polling/yield behavior, RVM devices, vnode cache sizes, callback intervals, worker counts, server host/IP, Smon host/port, counters, and `NullFid`.
- `main` is the full bootstrap sequence: read config, parse args/env, daemonize, initialize RVM/LWP/RPC/SFTP/directories/protection/volumes/callbacks/VRDB/COP/resolution, spawn LWPs, start the daemon parent, and wait for shutdown.
- `AuthLWP` handles new RPC2 connections on `SUBSYS_SRV`, executes the bind/connect request, and unbinds failed or suspicious clients.
- `ServerLWP` handles established client file-system requests, checks private client pointers and token expiry, updates client activity/counters, dispatches via `srv_ExecuteRequest`, and deletes/unbinds clients on fatal errors.
- `ResLWP` dispatches requests for the resolution subsystem through `resolution_ExecuteRequest`.
- `CallBackCheckLWP` periodically runs callback liveness checks and disk usage updates.
- `ShutDown`, `ViceTerminate`, and `SigTerm` coordinate graceful server shutdown and optional salvage-on-shutdown.
- `ViceUpdateDB` reloads protection database and auth keys when mtimes change, then checks VLDB/VRDB state.
- `PrintCounters` emits operation, transfer, RPC/SFTP, callback, host, RVM, and RDS statistics.
- `ReadConfigFile`, `ParseEnvVars`, and `ParseArgs` establish defaults and overrides.
- `InitServerKeys`, `SetupRVM`, `InitializeServerRVM`, `SetupRLimitAndSignals`, `SwapLog`, and `DaemonizeSrv` handle low-level process/runtime setup.

## Control flow
Startup begins with config defaults from `server.conf`, then command-line and environment overrides. The server validates RVM device settings, daemonizes unless disabled, sets signal handlers and resource limits, initializes recoverable memory and thread data, starts Coda core packages, reads auth/protection data, initializes RPC2/SFTP, directory and volume packages, callback state, VRDB, COP pending table, lock queue, resolution communication, and exports both file-server and resolution RPC subsystems. It then creates callback, auth, file-server, resolution, volume utility, resolution checker, and monitor LWPs. The main LWP signals readiness with `gogogo(parent)`, waits on `LWP_QWait`, and calls `ShutDown` when signaled.

Worker flow is split by connection stage. `AuthLWP` receives new connections, extracts peer info, rejects already-known private pointers, and dispatches the connect request. `ServerLWP` only accepts old connections, verifies `ClientEntry`, checks token expiration against packet receive time, tracks current operation/client, updates counters, dispatches generated RPC handlers, and cleans up clients marked for unbind. `ResLWP` handles old-or-new resolution subsystem RPCs independently.

## State and persistence behavior
Persistent server state is primarily RVM/RDS recoverable memory, volume/vnode metadata, protection/auth databases, VRDB/VLDB files, and server logs. `srv.cc` initializes RVM from configured log/data devices and loads the recoverable heap. It tracks nonpersistent process state such as counters, worker current-op arrays, debug levels, key/protection database mtimes, start time, and current connections. Shutdown may salvage volumes and writes a `SHUTDOWN` marker in the server directory.

## Dependencies and integration points
This file is the integration hub for RPC2, SFTP, codatunnel, LWP, IOMGR, RVM/RDS, auth2, protection lists, callbacks, directory cache, volume package, volutil, VRDB/VLDB, resolution communication, COP pending management, monitor daemon, daemonizer, config/env helpers, and generated RPC dispatch (`srv_ExecuteRequest`, `resolution_ExecuteRequest`).

## Risks
Startup ordering is fragile: many packages assume prior RVM, LWP, path, key, and volume initialization. Worker IDs are passed as addresses of the loop variable `i`, which is historically common but can race if LWP startup reads it after the loop advances. Signal handlers call functions that may not be async-signal-safe, though this is legacy LWP server code. `ParseEnvVars` assigns `MapPrivate` from `pathtiming` as the default argument, which looks like a copy/paste bug. Configuration conflicts around RVM mode are fatal, and missing keys intentionally assert. Request dispatch depends on private pointer integrity; stale or corrupted client state leads to unbinds.

## Test signals
High-value tests include startup with config/env/CLI combinations, RVM raw/UFS/VM modes, missing or rotated auth keys, token expiry, new and old RPC connection handling, worker unbind cleanup, shutdown/salvage, SIGHUP log rotation, SIGTERM graceful termination, VRDB/PDB reload via `ViceUpdateDB`, and counters under representative workloads. Operational signals are `SrvLog` startup ordering messages, worker request/failure logs, RVM/RDS statistics, RPC/SFTP counters, and `SHUTDOWN` marker creation.
