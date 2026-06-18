# sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFs.c

## Purpose
Creates, removes, and dispatches BeeGFS procfs entries under `/proc/fs/<module>/<session>`, exposing configuration, status, node lists, target state, and selected runtime toggles.

## Important APIs and Functions
`ProcFs_createGeneralDir()`/`removeGeneralDir()` manage the global parent. `ProcFs_createEntries()`/`removeEntries()` manage per-mount directories. `__ProcFs_open()` binds a seq-file show callback and mount `App`. Read wrappers call `ProcFsHelper_readV2_*`; write wrappers validate user buffers and call `ProcFsHelper_write_*`. Compatibility helpers access proc entry data across kernel APIs.

## Control Flow
Creation builds a session-specific directory from the local node alias and then iterates static tables for read-only and read-write files. Each proc entry stores its show function as data, while the parent directory stores `App*`. Opening a file uses entry data to choose `single_open()` callback and parent data as private app state. Write handlers recover `App*`, run `access_ok`, and delegate parsing/action.

## State and Persistence
Proc entries are runtime kernel objects tied to a mounted `App`. Writes change in-memory runtime flags such as connection retries, netbench mode, remap-connection-failure status, dropped connections, and log levels. No proc data is durable across mount.

## Dependencies and Integration Points
Depends on Linux procfs and seq_file APIs, `ProcFsHelper`, node alias state, and `App` lifecycle from `FhgfsOpsSuper.c`.

## Risks
Creation failure only logs and falls through to cleanup label without removing already-created entries in this function, so partial proc directories can remain until unmount cleanup attempts explicit removals. Removal is manually enumerated; adding an entry to creation tables requires updating removal. Write permissions are owner/group writable; deployment permissions should be intentional.

## Test Signals
Mount/unmount proc tree creation/removal, partial creation failure injection, open/read all entries, write each mutable entry with valid/invalid userspace buffers, and kernel-version coverage for `proc_ops`, `PDE_DATA`, and parent-data access.
