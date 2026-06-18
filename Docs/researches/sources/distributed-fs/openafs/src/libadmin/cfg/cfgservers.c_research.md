# sources/distributed-fs/openafs/src/libadmin/cfg/cfgservers.c

## Purpose
This file implements server-side configuration operations in the cfg admin library: BOS server control, database server setup, fileserver setup, update server setup, update client setup, and quorum checks. It wraps lower-level BOS, VOS, Ubik vote, and service-control APIs into higher-level configuration actions.

## Important APIs, Types, and Functions
- Exported BOS functions: `cfg_BosServerStart`, `cfg_BosServerStop`, and `cfg_BosServerQueryStatus`.
- Database server functions: `cfg_AuthServerStart`, `cfg_DbServersStart`, `cfg_DbServersStop`, `cfg_DbServersQueryStatus`, `cfg_DbServersRestartAll`, `cfg_DbServersWaitForQuorum`, and `cfg_DbServersStopAllBackup`.
- File server functions: `cfg_FileServerStart`, `cfg_FileServerStop`, and `cfg_FileServerQueryStatus`.
- Update server/client functions: `cfg_UpdateServerStart`, `cfg_UpdateServerStop`, `cfg_UpdateServerQueryStatus`, `cfg_SysBinServerStart`, `cfg_UpdateClientStart`, `cfg_UpdateClientStop`, `cfg_UpdateClientStopAll`, `cfg_UpdateClientQueryStatus`, `cfg_SysControlClientStart`, and `cfg_BinDistClientStart`.
- Static helpers `SimpleProcessStart`, `FsProcessStart`, and `BosProcessDelete` create/start/stop/delete BOS instances. `UpdateCommandParse` recognizes configured `etc` and `bin` paths. `UbikQuorumCheck` and `UbikVoteStatusFetch` determine whether Ubik database services have a writable sync site.

## Control Flow and State
All public functions first validate `cfg_host_t` and usually call `cfgutil_HostHandleBosInit`. Start functions create BOS instances if missing and then set execution state to running. Stop functions set instances stopped, wait for transitions, and delete them. Query functions inspect BOS process info, process names, or process command parameters. Database quorum loops call vote debug RPCs repeatedly until all required services are writable or the timeout expires.

## Persistence and Side Effects
The file persistently changes BOS configuration by creating and deleting process instances for `kaserver`, `ptserver`, `vlserver`, `buserver`, `fs`, `upserver`, and `upclient*`. It starts and stops those processes. `cfg_FileServerStop` optionally removes the host's file-server addresses from the VLDB after deleting the fileserver BOS instance. BOS server start/stop on Windows manipulates the local AFS BOS control service.

## Dependencies and Integration Points
The module integrates `cfginternal` host utilities, BOS admin, VOS admin, client admin, util admin, RX, Ubik vote RPCs, OpenAFS directory constants, and Windows registry/service names. It assumes standard canonical server binary paths from `afs/dirpath.h` and standard ports from cellconfig/ubik headers. It is exercised by `cfg/test/cfgtest.c` and linked into `libcfgadmin`.

## Risks
Remote BOS start/stop is explicitly unsupported for some BOS service operations. Many operations use a "try all, last error wins" pattern, which can hide earlier failures. `BosProcessDelete` treats missing instances as success, useful for idempotence but potentially surprising in diagnostics. Command parsing mutates the command string, searches plain text paths, and may be brittle around quoting or unusual path layouts. Quorum checks ignore individual unreachable servers while looking for a writable sync site, which matches availability goals but can mask partial outages. Fileserver readiness is represented by a fixed five-second sleep.

## Test Signals
Tests should cover idempotent start/stop for existing/missing BOS instances, query status with missing/mis-typed process entries, update command parsing for clear/crypt sys/bin path combinations, quorum timeout and old/new vote debug responses, backup server optional behavior, VLDB address cleanup after fileserver stop, and Unix/Windows differences for BOS service start/stop.
