# sources/distributed-fs/openafs/src/WINNT/afsclass/worker.h

## Purpose
`worker.h` defines the typed request contract for the `afsclass` worker dispatcher. It enumerates every supported admin operation as a `WORKERTASK`, describes the corresponding input/output packet shape in `WORKERPACKET`, and declares the worker initialization and execution APIs.

## Important APIs, types, and functions
The key constants are `NO_PARTITION` and `NO_VOLUME`, used as sentinels for optional partition/volume parameters. `WORKERTASK` enumerates vos backup, partition, server, VLDB, volume, and quota tasks; bos server, process, admin, key, cell, host, executable, log, auth, command, and salvage tasks; kas server/principal/key tasks; pts group/user/membership tasks; client token/cell/server tasks; and util database-server enumeration tasks.

`WORKERPACKET` is a large union whose member structs are named after tasks and annotate `[in]`, `[out]`, or `[in out]` fields. Public functions are `Worker_Initialize` and `Worker_DoTask`.

## Control flow
The header encodes a synchronous request/response pattern: caller fills the union member matching the selected `WORKERTASK`, calls `Worker_DoTask`, then reads status and any output fields. Enumeration tasks follow explicit begin/next/done token lifecycles. Open/close tasks expose server, cell, and credentials handles as opaque `PVOID` tokens.

## State and persistence behavior
The header does not allocate state itself. It defines packet fields that can carry handles to long-lived admin objects and fields for persistent AFS mutations: volume creation/deletion/move/release, VLDB lock/site changes, BOS process/key/cell/host/executable/auth changes, kas principal changes, and pts user/group changes.

## Dependencies and integration points
The header includes AFS admin headers for vos, bos, kas, pts, client, util, protection errors, and Kerberos admin error constants. It bridges Windows C++ callers using `LPTSTR`, `SOCKADDR_IN`, `SYSTEMTIME`, `BOOL`, and OpenAFS admin structures such as `vos_partitionEntry_t`, `vos_vldbEntry_t`, `bos_RestartTime_t`, `kas_principalEntry_t`, `pts_GroupEntry_t`, and `afs_serverEntry_t`.

## Risks and edge cases
The union contract is not type-safe at runtime: passing a task with the wrong active packet member will reinterpret memory. Many string output fields are raw `LPTSTR` buffers with sizes implied by the caller rather than encoded in the type. Opaque `PVOID` handles require strict open/close/enumeration discipline. The enum and union must remain in exact sync with `worker.cpp`; the `ADD HERE` comments show the intended extension points but do not enforce completeness.

## Test signals
Compile-time tests should catch ABI drift with the admin headers. Runtime tests should exercise one task from each family, verify begin/next/done cleanup, assert sentinel handling for optional values, and validate that output buffers are populated or cleared consistently. Static analysis should flag switch coverage in `worker.cpp` whenever a `WORKERTASK` value is added.
