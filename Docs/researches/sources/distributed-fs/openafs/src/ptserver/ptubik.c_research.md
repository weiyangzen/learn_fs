# sources/distributed-fs/openafs/src/ptserver/ptubik.c research

## Purpose
`ptubik.c` is a lightweight Ubik compatibility shim for standalone protection-database tooling. It provides enough Ubik, Rx, and configuration globals/functions for ptserver database code to operate against a local file descriptor instead of a live replicated Ubik server.

## Important APIs, types, and functions
Stubbed transaction and server functions include `ubik_ServerInit`, `ubik_BeginTrans`, `ubik_BeginTransReadAny`, `ubik_AbortTrans`, `ubik_EndTrans`, `ubik_Tell`, `ubik_Truncate`, `ubik_SetLock`, and `ubik_CheckCache`. Real local file I/O is handled by `ubik_Seek`, `ubik_Write`, and `ubik_Read`, which address the backing file at `pos + HDRSIZE`. `panic` prints and aborts. `afsconf_GetNoAuthFlag` always returns true for local tooling.

The file defines Ubik globals (`ubik_quorum`, `ubik_dbase`, `ubik_stats`, `ubik_host`, `ubik_epochTime`, `urecovery_state`, `ubik_sc`), ptserver globals (`dbase`, `cheader`), and a placeholder `prdir`.

## Control flow, state, and persistence
On first `ubik_BeginTrans`, the shim writes a minimal Ubik header with magic/version/size to `dbase_fd` and fsyncs it. Subsequent transaction functions are no-ops, so local pt database operations rely on direct seek/read/write and do not get real locking, replication, quorum, abort, or rollback semantics. `ubik_Read` zero-fills short reads, matching expectations for initializing empty database regions.

## Dependencies and integration points
This file is used by local utilities that reuse ptserver database code without linking the full Ubik server stack. It includes `ptint.h` and `ptserver.h` and expects an external `dbase_fd`. It intentionally makes `pr_noAuth`-style paths succeed by returning noauth from `afsconf_GetNoAuthFlag`.

## Risks and test signals
The shim is not equivalent to production Ubik. It has no transactional rollback, no concurrency control, and only coarse write error checks, so it should stay confined to offline tools and tests. Any ptutils change that assumes real Ubik transaction side effects may break standalone utilities. Tests should exercise database initialization on an empty file, read/write offset correctness relative to `HDRSIZE`, short-read zero filling, and compatibility with tools that import/export or repair protection databases.
