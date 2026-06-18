# sources/distributed-fs/coda/coda-src/vice/srvproc.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vice/srvproc.cc` implements the core Coda file-server operation helpers and several RPC entry points for object fetch, attribute lookup, batched validation, ACL retrieval, and ACL mutation. It is the server-side bridge between RPC2 request stubs, authentication/client state, volume/vnode locking, ACL and mode checks, SmartFTP side effects, callback invalidation, COP1/COP2 replicated update tracking, recoverable mutation logs, and final commit/abort of vnode/volume state.

## Important APIs, Types, and Functions

Public RPC handlers include `FS_ViceFetch`, `FS_ViceFetchPartial`, `FS_ViceGetAttr`, `FS_ViceGetAttrPlusSHA`, `FS_ViceValidateAttrs`, `FS_ViceValidateAttrsPlusSHA`, `FS_ViceGetACL`, and `FS_ViceSetACL`. Shared operation APIs exported through `operations.h` include `ValidateParms`, `AllocVnode`, `Check*Semantics` routines for fetch/getattr/ACL/store/setattr/create/remove/link/rename/mkdir/rmdir/symlink, `Perform*` routines for metadata mutation, `FetchBulkTransfer`, `StoreBulkTransfer`, and `PutObjects`. Local helpers include `GrabFsObj`, `GetFsoAndParent`, `NormalVCmp`, `CopyOnWrite`, `Check_CLMS_Semantics`, and `Check_RR_Semantics`.

## Control Flow

The file explicitly documents the common operation template: validate parameters, get objects, check semantics, perform the operation, then put objects. Read paths validate `RPCid` and piggybacked COP2 state with `ValidateParms`, translate replicated volume ids through `XlateVid`, lock the target and parent with `GetFsoAndParent` or `GetFsObj`, compute rights through ACLs, perform SmartFTP transfer if needed, fill `ViceStatus`, optionally add callbacks, and release objects with `PutObjects` without an RVM transaction. Mutation helpers run semantic version checks via a `VCP` comparator, enforce type/parent/name/permission constraints, mutate directory handles or vnode fields in VM/RVM-backed structures, break callbacks, schedule replicated COP pending entries, spool resolution log records when required, and rely on `PutObjects(..., TranFlag=1)` to commit or abort.

## State and Persistence Behavior

Persistent state is held in volume headers, vnode disk objects, directory data, inode containers, ACL blocks, version vectors, and resolution logs. `CopyOnWrite` materializes cloned directories or file inodes before mutation. `PerformStore`, `PerformSetAttr`, `PerformSetACL`, `Perform_CLMS`, `Perform_RR`, and `PerformRename` update vnode length, link count, parent fid, data version, author, owner, mode bits, unix mtime, and volume version vectors. `PutObjects` is the commit coordinator: on success it commits dirty directory pages, appends or aborts recoverable log records, writes changed/deleted vnodes, optionally updates the volume header, and only after the RVM transaction drops old or failed inodes. On error it reverses block accounting, aborts dirty directory state, flushes changed vnodes, drops newly created file inodes, and frees VLE/log record state.

## Dependencies and Integration Points

The implementation depends on RPC2/SmartFTP (`RPC2_InitSideEffect`, `RPC2_CheckSideEffect`), RVM transactions (`rvmlib_begin_transaction`, `rvmlib_end_transaction`), volume/vnode APIs (`GetVolObj`, `PutVolObj`, `VGetVnode`, `VPutVnode`, `VFlushVnode`), directory APIs (`VN_SetDirHandle`, `DH_Create`, `DH_Delete`, `DH_IsEmpty`), ACL/PRS APIs (`AL_CheckRights`, `AL_Internalize`, `AL_Externalize`), version-vector utilities, callback APIs (`CodaAddCallBack`, `CodaBreakCallBack`, `DeleteFile`), resolution logging (`rsle`, `SpoolVMLogRecord`, `TruncateLog`, `PurgeLog`), inode operations (`icreate`, `iopen`, `idec`, `ftruncate`), and global counters/timing from `srv.h`.

## Risks and Edge Cases

The code has high concurrency and recovery risk: lock order is partly explicit but rename ancestry traversal may use non-blocking vnode grabs to avoid deadlock; the code comments note known semantic concerns around rename overwriting directories and directory disk-usage accounting. `ValidateParms` applies piggybacked COP2 before mapping the client and volume, so failures there abort the main operation early. SHA generation is lazy and CPU-heavy and only covers files. Side-effect transfer byte counts are checked, but partial fetch uses unsigned/count sentinel logic and resumed fetch rejects version-vector changes with `EAGAIN`. `PutObjects` must coordinate RVM commits with inode reference changes in the right order; mistakes can leak or prematurely drop containers. Many hard failures are `CODA_ASSERT`, so malformed on-disk state or impossible invariants can terminate the server.

## Test Signals

Useful test signals include RPC smoke tests for fetch/getattr/getattr+SHA/validate attrs/get ACL/set ACL, permission matrix tests across system users, owners, anyuser rights, mode bits, and virgin files, version-vector mismatch tests for replicated and non-replicated operations, partial fetch resume tests, SmartFTP byte-count mismatch tests, callback add/break checks after reads and mutations, quota/disk accounting tests for create/remove/rename/COW/truncate, fault-injection around `PutObjects` error paths, and recovery/salvage tests that verify vnode, directory, inode, and resolution-log consistency after aborts and restarts.
