# sources/distributed-fs/openafs/src/venus/afsio.c

## Purpose
`afsio.c` implements the `afsio` command, a clientless or client-assisted AFS file I/O tool built around `libafscp`. It supports locking, unlocking, reading, directory reading, writing, and appending by pathname or by explicit `volume.vnode.unique` FID, with optional cell/realm selection, clear or encrypted RX behavior, MD5 reporting, synthetic write data, overwrite control, and transfer-rate diagnostics.

## Important APIs, Types, And Functions
The command surface is registered in `main` with `cmd_CreateSyntax` for `lock`, `fidlock`, `unlock`, `fidunlock`, `read`, `fidread`, `readdir`, `fidreaddir`, `write`, `fidwrite`, `append`, and `fidappend`. Shared parsing is handled by `CmdProlog`, `common_parms`, `ScanFid`, `BreakUpPath`, `GetVenusFidByFid`, and `GetVenusFidByPath`. The main operations are `lockFile`, `readFile`, and `writeFile`. Transfer helpers include `time_elapsed`, `printDatarate`, `summarizeDatarate`, and `summarizeMD5`. `struct wbuf` forms a linked list of 64 KiB write buffers, up to a nominal 64 MiB staging window.

## Control Flow
Startup derives the program name, initializes error tables and pthread local state when needed, initializes `libafscp`, registers commands, dispatches through the OpenAFS command parser, and finalizes `libafscp`. `CmdProlog` inspects command name and parameters to set global flags such as FID mode, append mode, directory-read mode, verbosity, clear/encrypted behavior, force, read-lock, MD5, cell, realm, and alternate local auth user.

`lockFile` authenticates anonymously by default, optionally makes RX insecure, resolves a path or FID to an `afscp_venusfid`, polls status while a conflicting lock exists, waits for callbacks if requested, then invokes `afscp_Lock`. `readFile` resolves and type-checks the object, fetches status for length, loops with `afscp_PRead` into a 64 KiB buffer, writes to stdout, updates MD5 and rate counters, and reports final metrics. `writeFile` resolves or creates the target, rejects accidental overwrites unless `-force` or append semantics allow them, buffers stdin or synthesized offset patterns, writes each buffer through `afscp_PWrite`, and frees all staged buffers and FID references.

## State And Persistence
Most state is process-global command state: selected cell, auth mode, append/FID/read-directory flags, rate counters, MD5 context, and timing snapshots. Persistent effects occur on AFS files: locks are modified on fileserver state, reads stream file or directory data to stdout, writes create or overwrite AFS files, append extends existing files, and `-as-user` changes the local authorization context used by `libafscp`. No local configuration files are written.

## Dependencies And Integration Points
The file depends on `libafscp`, RX/auth/VLDB types, OpenAFS command parsing, `hcrypto` MD5, portable roken APIs, and Windows pioctl/path support under `AFS_NT40_ENV`. It integrates directly with fileservers through `libafscp` rather than relying solely on cache-manager pioctls, which is why the FID modes can work on hosts without an AFS client.

## Risks And Test Signals
Risk areas include global mutable command flags reused across subcommands, duplicated statements in argument and synth-length handling, fixed 64 MiB write staging before transfer, partial-read/write error mapping to ad hoc negative codes, FID volume rewriting when forcing RW volume lookup, stdout/stdin binary mode handling on Windows, and unbounded wait/retry behavior when locks contend. Useful test signals are successful path and FID read/write/append, directory read rejection for files and file read rejection for directories, `-force` overwrite behavior, `-synthesize` large writes, MD5 parity with external checksums, lock/unlock against an active fileserver, clear/encrypted RX toggles, and operation without a local cache manager.
