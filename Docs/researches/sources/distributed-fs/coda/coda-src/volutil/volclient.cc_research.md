# sources/distributed-fs/coda/coda-src/volutil/volclient.cc

## Purpose

`volclient.cc` is the command-line client for Coda volume utility administration. The complete 2083-line file was read. It parses global options, binds to the fileserver's volutil RPC subsystem with either the shared volutil key or Coda tokens, dispatches many administrative subcommands, and implements the client-side dump/restore side-channel service.

## Important APIs, Types, and Functions

Important functions include `main()`, `ReadConfigFile()`, `V_InitRPC()`, `V_BindToServer()`, `VolDumpLWP()`, `S_WriteDump()`, `S_ReadDump()`, and command handlers such as `create()`, `create_rep()`, `clone()`, `backup()`, `dump()`, `restorefromback()`, `makevldb()`, `makevrdb()`, `dumpvrdb()`, `info()`, `showvnode()`, `setvv()`, `purge()`, `lock()`, `unlock()`, `updatedb()`, `timing()`, `tracerpc()`, `printstats()`, `showcallbacks()`, `rvmsize()`, `setlogparms()`, `getmaxvol()`, and `setmaxvol()`. `rockInfo` tracks dump file descriptors, target volume id, and byte offsets.

## Control Flow

`main()` loads `server.conf`, resolves `-h`, `-r`, `-t`, and `-d`, initializes LWP/RPC2/SFTP, binds to the server, stores `argv` in globals, and dispatches by subcommand name. Most command handlers parse positional arguments, build optional SMARTFTP descriptors for output files, call the matching generated RPC stub, print result text, and exit. Dump and restore create a local `VolDumpLWP` that exports `VOLDUMP_SUBSYSTEMID`; the server calls back into `S_WriteDump()` for dumping or `S_ReadDump()` for restore file streaming.

## State and Persistence Behavior

The client owns no Coda server persistence directly. It can request destructive server mutations such as purge, restore, setvv, setlogparms, shutdown, database rebuilds, and max-volume-id changes. Local state includes RPC binding handles, selected host/realm, the process-wide argument globals, temporary output file descriptors, and dump byte counters.

## Dependencies and Integration Points

Dependencies include LWP, RPC2, SFTP, auth token helpers, `codaconf`, `vice_file`, generated volutil/voldump stubs, partition/volume headers, and service lookup via `coda_getservbyname("codasrv", "udp")`. It integrates with server handlers in this directory and with external admin scripts such as `createvol_rep`, `bldvldb`, and clone/backup workflows.

## Risks and Test Signals

Risks include global argument and RPC state, many `exit()` paths, sparse file-open error checks, dump/restore side-channel loops that run forever, host-endian dump assumptions, typo-prone manual parsing, and highly privileged operations protected by local key/token availability. Tests should cover command usage errors, auth selection, binding failures, each RPC argument marshalling path, SMARTFTP output descriptors, dump/restore offset accounting, large dump transfer, and failure messages for server-side errors.
