# sources/distributed-fs/coda/coda-src/smon2/smon2.c

Purpose: Coda server monitor that queries `ViceGetStatistics` and emits RRDTool commands for database creation and updates.

Important functions: `RRDCreate` prints the `create <server>.rrd` command with data-source and archive definitions. `RRDUpdate` prints an `update` line using the `ViceStatistics` fields for RPC, fetch/store, CPU, VM, fault, workstation, and disk metrics. `ValidServer` resolves server names for `codasrv/udp`. `GetArgs` parses `-t` interval and `-1` one-shot mode, validates up to `MAXSRV` servers. `InitRPC` starts LWP, SFTP, and RPC2. `DoProbe` lazily binds to each server, calls `ViceGetStatistics`, and resets bindings on failure. `srvlwp` probes in a loop per server and signals the parent on exit.

State/persistence: writes RRDTool commands to stdout, intended to pipe into `rrdtool -`; stores per-server process-local connection/stat state. No direct files are written except by downstream RRDTool.

Dependencies, risks, tests: depends on RPC2/LWP/SFTP, `vice.h`, service lookup, and RRDTool command compatibility with `gensrvstats.py`. Risks include passing address of loop variable `i` into `LWP_CreateProcess`, race-prone global `SrvCount` decrement, no locking around stdout, and no service lookup null check. Test one-shot and looping modes, multiple servers, failed/recovered bindings, missing RRD creation, and RRD data-source count alignment.
