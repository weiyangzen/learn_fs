# sources/distributed-fs/openafs/src/butc/tcmain.c

## Purpose
`tcmain.c` is the executable entry point for `butc`. It parses command-line and config files, initializes logging, auth/audit, Rx service security, VLDB/BUDB clients, tape/XBSA globals, status/task state, and starts the TC RPC service.

## Important APIs, Types, and Functions
Important globals include log paths/handles, `globalTapeConfig`, `deviceLatch`, `globalCellName`, `dump_namecheck`, `queryoperator`, `autoQuery`, `isafile`, mount/unmount callouts, `restoretofile`, `maxpass`, `groupId`, `statusSize`, `BufferSize`, `rxBind`, `butc_confdir`, and `allow_unauth`. `SafeATOL()` and `atocl()` parse numeric options. `GetDeviceConfig()` reads `tapeconfig`; `GetConfigParams()` reads `CFG_<port>` or `CFG_<device>`. `WorkerBee()` initializes the process and starts Rx. `main()` registers command syntax and dispatches.

## Control Flow
`main()` initializes AFS paths and command syntax. `WorkerBee()` initializes error tables, parses options, chooses tape or XBSA mode, loads config, opens logs, initializes audit and config directories, sets up Rx, initializes VLDB and BUDB clients, initializes task/status/device state, builds server security objects, creates the `BUTC` service, starts the DB watcher, logs startup, and calls `rx_StartServer()`.

## State and Persistence Behavior
It creates/appends tape, error, last-pass, and central logs. It does not write backup media or dump rows, but it initializes every global and client used by workers. `groupId`, `BufferSize`, and `statusSize` directly shape later BUDB/tape behavior.

## Dependencies and Integration Points
Integrates with AFS command/path/config/auth/audit/Rx/VLDB/BUDB/volserver/tape libraries, generated TC RPC dispatch, `list.c`, shared status code, `dbWatcher`, `dump.c`, `lwps.c`, `recoverDb.c`, and optional XBSA libraries.

## Risks and Test Signals
Risks include simple config parsing, unbounded `%s` for `PASSFILE`, size saturation in `atocl()`, secure-start behavior changing legacy deployments, and insecure `allow_unauth` dependence on network controls. Test startup auth modes, config/tapeconfig parsing, XBSA required parameters, Rx bind, log creation, central log `/afs/` rejection, and BUDB permission failure.
