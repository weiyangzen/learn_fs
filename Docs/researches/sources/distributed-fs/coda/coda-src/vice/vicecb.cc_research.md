# sources/distributed-fs/coda/coda-src/vice/vicecb.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vice/vicecb.cc` implements the file server's in-memory callback promise table. It records which Venus clients have callbacks for individual fids or whole volumes, sends callback breaks over RPC2 multi-RPC, deletes callback promises when clients disconnect or files disappear, and provides debug/statistical dumps.

## Important APIs, Types, and Functions

Private types are `FileEntry`, `FEBlock`, `CallBackEntry`, `CBEBlock`, and `CBStat`. Public functions include `InitCallBack`, `AddCallBack`, `BreakCallBack`, `DeleteCallBack`, `DeleteVenus`, `DeleteFile`, `CodaAddCallBack`, `CodaBreakCallBack`, `CodaDeleteCallBack`, `PrintCallBackState`, and `PrintCallBacks`. Internal helpers include `VHash`, `GetFEBlock`, `GetFE`, `FreeFE`, `FindEntry`, `DeleteFileStruct`, `GetCBEBlock`, `GetCBE`, `FreeCBE`, `SDeleteCallBack`, `order_helist`, and callback dump helpers.

## Control Flow

Callbacks are keyed by fid in a 256-bucket hash table. `AddCallBack` creates a `FileEntry` if necessary, avoids adding duplicates for the same host, and allocates a `CallBackEntry`. `BreakCallBack` locks the file entry, revalidates it after acquiring the lock, sorts target `HostTable` entries by callback connection id for lock ordering, sends `CallBack_OP` with `MRPC_MakeMulti`, cleans up failed hosts, removes volume callbacks when a file callback breaks, and then removes all non-exempt callback entries. Delete paths either remove a single client's callback, all callbacks for a host, or all callback state for a fid. `Coda*` wrappers translate between replica fids and replicated-group fids and also handle volume-level callbacks.

## State and Persistence Behavior

All callback state is transient server memory: `hashTable`, `FEFree`, `CBEFree`, and counters (`CBEs`, `CBEBlocks`, `FEs`, `FEBlocks`, `VEs`, `VCBEs`). There is no disk persistence; callbacks are rebuilt by clients after reconnect/revalidation. Free-list block allocation uses `malloc` and never returns blocks to the system, only to internal free lists.

## Dependencies and Integration Points

The file integrates with `HostTable` locks from `srv.h`, RPC2 callback stubs (`CallBack_OP`, `CallBack_PTR`, `MRPC_MakeMulti`), `srv_rpc2_timeout`, `CLIENT_CleanUpHost`, VRDB volume translation (`XlateVid`, `ReverseXlateVid`), logging, histograms for debug output, and server object mutation paths that call `CodaBreakCallBack`/`DeleteFile` before or after changes.

## Risks and Edge Cases

Concurrency is delicate. The source comments document a race where a second callback breaker may hold a pointer to a `FileEntry` already returned to the free list; the code re-finds the entry after acquiring its lock to reduce this. `SDeleteCallBack` marks callback entries as dead if the file entry is busy, delaying actual free. `BreakCallBack` allocates arrays sized by `tf->users`, so corrupted counts can cause bad allocations. Volume callbacks use fids with vnode and unique zero, which must not be confused with invalid object fids. Failed callback RPCs trigger host cleanup while host locks are held.

## Test Signals

Run callback set/break/delete tests for file and volume callbacks, same-client exemption on mutation, replicated and non-replicated fid translation, client disconnect cleanup, failed callback connection cleanup, concurrent add/break/delete stress tests, and debug dump consistency checks comparing counted CBEs/FEs with active counters.
