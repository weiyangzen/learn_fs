# Research: subset-b-007945

Grouped research for XRootD `XrdOfs` filesystem, checkpoint, and configuration sources. Each file section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfs.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfs.cc

## Purpose

`XrdOfs.cc` is the primary implementation of the XRootD OFS layer: it adapts the `XrdSfsFileSystem`, `XrdSfsFile`, and `XrdSfsDirectory` interfaces to the configured `XrdOss` storage plugin, authorization plugin, CMS/finder services, event notification, POSC persistence-on-successful-close, third-party-copy, checksum, page read/write, and checkpoint support. It owns the ordinary runtime control flow for opens, reads, writes, metadata operations, redirects/stalls, and error conversion.

## Important APIs, Types, and Functions

- Globals: `OfsEroute`, `OfsTrace`, `OfsStats`, and `XrdOfsOss` are the error route, trace switch, stats collector, and active storage backend. `XrdOfs::dummyHandle`, `MaxDelay`, and `OSSDelay` provide shared handle/default delay state.
- Local helper `VerPgw()` validates page-write checksum vectors via `XrdOucPgrwUtils::csVer()` and reports offset-specific corruption.
- `XrdOfs::XrdOfs()` establishes defaults for modes, role, POSC, checksum, prepare, xattr, directory redirect, proxy, page-rw, and extended-error behavior.
- `XrdOfsDirectory::open()`, `nextEntry()`, `close()`, and `autoStat()` implement directory lifecycle against `XrdOssDF` directory objects with optional authorization and CMS locating.
- `XrdOfsFile::open()` is the central open/create path. It maps SFS flags to POSIX/OSS flags, authorizes create/read/update/TPC, consults `Finder`, manages POSC queue entries, creates/attaches `XrdOfsHandle`, opens `XrdOssDF`, initializes TPC destination state, sets compressed/raw I/O, emits events, and updates open statistics.
- `XrdOfsFile::close()` retires handles, tears down TPC, completes or unpersists POSC files, restores outstanding checkpoints, emits close events, and updates counters.
- `XrdOfsFile::checkpoint()` dispatches `cpCreate`, `cpDelete`, `cpQuery`, `cpRestore`, `cpTrunc`, and `cpWrite`; `CreateCKP()` chooses proxy-supplied checkpoint objects or local `XrdOfsChkPnt`.
- I/O methods include synchronous and AIO `read`, `write`, `readv`, `pgRead`, `pgWrite`, `sync`, `truncate`, `stat`, `getMmap`, `getCXinfo`, and clone calls. They funnel to `oh->Select()` and translate failures through `Emsg()`.
- Filesystem methods include `chksum`, `chmod`, `Connect`, `Disc`, `exists`, `getStats`, `mkdir`, `prepare`, `remove`, `rename`, two `stat` variants, and path-level `truncate`.
- Helpers `Emsg()`, `EmsgType()`, `fsError()`, `Forward()`, `Stall()`, `Unpersist()`, `WaitTime()`, `Split()`, `Fname()`, and `Reformat()` normalize protocol-visible responses and side effects.

## Control Flow

The open path first rejects reuse of an already-open `XrdOfsFile`, derives open/create/POSC/finder flags, optionally redirects TPC writes, and delegates location to CMS. Creates are authorized separately for normal create versus exclusive create; POSC creates are pre-entered into `poscQ`. After `XrdOfsOss->Create()` and `XrdOfsHandle::Alloc()`, existing active handles can be shared unless the request is a TPC writer. Otherwise a new `XrdOssDF` is opened, the handle is activated, fadvise may be issued for sequential I/O, events/statistics are emitted, and ownership transfers out of the RAII `OpenHelper`.

Read/write control flow is deliberately thin after open: it checks 32-bit offset limits, chooses raw or normal reads for compressed/raw I/O, maps page-rw to OSS-native `pgRead`/`pgWrite` when available or simulates it, and uses AIO only where the backend supports it. POSC writes and syncs are forced synchronous where errors must be detected before the file is made persistent.

Metadata operations all follow a common pattern: build `XrdOucEnv` from opaque/client data, authorize the operation, locate or forward via CMS if this node is remote, emit optional events, call the `XrdOss` operation, update `Balancer` or handle caches, then translate errors or special responses to SFS return codes.

## State and Persistence Behavior

The main state is held in `XrdOfsHandle` instances. Handles track active/inactive state, usage, writer/POSC mode, pending writes, first-write state, compression, and the selected `XrdOssDF`. `ocMutex` protects assignment of the per-file `oh` pointer and open/close transitions.

POSC is persistent state backed by `XrdOfsPoscq`. During create/open, paths can be entered into the POSC queue; on successful close the pending POSC bit is cleared with `Fchmod()`, the queue record is deleted, and the balancer is updated. On write/sync/close failures, `Emsg(..., posChk=true)` or close cleanup calls `Unpersist()`, which deletes the file or queue entry, emits removal/close notifications, and increments `numUnpsist`.

Checkpoint state is per `XrdOfsFile` through `myCKP` and `ckpBad`. Checkpoint failures set `ckpBad`, suppress additional checkpoint write/truncate operations, and may suppress backend access via `oh->Suppress()`. Close automatically attempts `myCKP->Restore()` before deleting the checkpoint object.

Statistics are kept in `OfsStats`, with some counters intentionally updated without locks for redirect/stall/error hot paths. Event state is external in `evsObject`; CMS state is external in `Finder`/`Balancer`.

## Dependencies and Integration Points

This file integrates with `XrdOss` for storage, `XrdCmsClient` for locate/prepare/forward/balancer updates, `XrdAccAuthorize` through the `AUTHORIZE` macro, `XrdOfsEvs` for notifications, `XrdOfsTPC` for third-party-copy source and destination flows, `XrdCks` for checksums, `XrdOfsChkPnt`/`XrdOucChkPnt` for checkpoints, `XrdOfsPoscq` for POSC, `XrdOucEnv` for opaque/environment metadata, and `XrdSfs` protocol return conventions. Proxy backends are detected through OSS features and environment and alter direct-open, checkpoint, checksum, and raw-I/O behavior.

## Risks and Edge Cases

- Open/close correctness depends on `XrdOfsHandle` locking discipline. Existing handles may be reused; TPC write requests are rejected on already-active targets.
- POSC failures intentionally delete data. Any incorrect `posChk` use or async path that hides write errors could cause unexpected unpersist behavior.
- `rename()` has an acknowledged race when emulating no-overwrite authorization by checking destination existence before rename.
- Checkpoint and POSC are mutually exclusive, but the interaction is spread between `CreateCKP()`, open modes, close cleanup, and error handling.
- Remote forwarding can return redirects, stalls, started responses, or errors from different layers; callers must not assume local POSIX semantics.
- `EmsgType()` maps `EBUSY` and `ETIMEDOUT` into stalls rather than hard errors, which is protocol-visible behavior.
- Page-write checksum verification is only simulated when OSS lacks page-rw support; native verification is delegated to the backend.

## Test Signals

Useful tests include create/open mode mapping with authorization combinations, POSC success and failure recovery, close-on-destructor behavior, TPC source/destination opens, Finder redirect/stall/error mapping, checksum `csSize/csGet/csCalc`, pgRead/pgWrite native versus simulated behavior, checkpoint create/write/truncate/restore/delete and failure suppression, first-write/close event delivery, and metadata operations with balancer updates. Fault-injection against `XrdOssDF` return codes should verify `Emsg`, `Stall`, and `fsError` conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfs.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfs.hh

## Purpose

`XrdOfs.hh` declares the public and protected class surface for the OFS filesystem adapter. It defines concrete `XrdSfsDirectory`, `XrdSfsFile`, and `XrdSfsFileSystem` implementations and centralizes configuration members, role flags, forwarding specifications, plugin pointers, POSC state, checksum state, and helper declarations used by implementation files.

## Important APIs, Types, and Functions

- `XrdOfsDirectory` implements the SFS directory interface with `open`, `nextEntry`, `close`, `autoStat`, `copyError`, and `FName`. It owns a path string, `XrdOssDF *dp`, EOF state, and a fixed entry buffer.
- `XrdOfsDirFull` wraps `XrdOfsDirectory` with an owned `XrdOucErrInfo` for normal object allocation.
- `XrdOfsFile` implements the SFS file interface. It exposes open/close, clone, checkpoint, fctl, mmap, page read/write, sync and async read/write, readv, stat, sync, truncate, and compression-info methods.
- `XrdOfsFile` state includes request user identity, current `XrdOfsHandle *oh`, optional `XrdOfsTPC *myTPC`, optional `XrdOucChkPnt *myCKP`, raw-I/O flag, destructor-close marker, and checkpoint-bad flag.
- `XrdOfsFileFull` wraps `XrdOfsFile` with owned `XrdOucErrInfo`.
- `XrdOfs` implements `XrdSfsFileSystem`. Public methods allocate file/directory objects and expose filesystem operations: checksum, chmod, connect/disconnect, exists, file attributes, FSctl/fsctl, stats, version, mkdir, prepare, rem/remdir, rename, stat variants, truncate, and configuration.
- The `Options` bit enum models authorization, xattr plugin, roles, forwarding, TPC, subcluster, and TPC redirect flags.
- `fwdOpt` stores forwarding command, host, and port for metadata operations and owns a `Reset()` method.
- Protected helpers include `ConfigXeq`, `Emsg`, `EmsgType`, `fsError`, `Split`, `Stall`, `Unpersist`, and `WaitTime`.
- Private configuration helpers include POSC, redirection, TPC, role, trace, xattr, notification, forwarding, export, and creation-mode parsers.

## Control Flow and Contracts

The header shows the intended layering: protocol-facing `XrdSfs*` methods are public; common error and stall behavior is protected; parser/configuration helpers and plugin state are private. `XrdOfs` grants friendship to file and directory objects so they can use configured authorization, OSS, finder, event, POSC, checksum, and error helpers without a large public API.

Object allocation is split between calls that allocate an owned error-info object (`newDir(char*, int)`, `newFile(char*, int)`) and calls that bind to an existing `XrdOucErrInfo`. This distinction matters for lifetime and monitoring IDs.

## State and Persistence Behavior

The declaration captures persistent runtime state rather than on-disk formats. POSC state is represented by `poscQ`, `poscLog`, `poscHold`, `poscSync`, and `poscAuto`; checkpoint state is only per-file (`myCKP`/`ckpBad`) and configured elsewhere. Creation masks `dMask` and `fMask` persist after configuration and are used by mkdir/chmod/open. `dummyHandle` is a sentinel shared by unopened files. `ocMutex` serializes handle assignment and close/open transitions.

`ConfigFN`, `myRole`, redirect hosts, plugin pointers, and CMS pointers are owned as process-lifetime configuration state. The destructor is intentionally empty because deleting the full plugin graph is considered too complex.

## Dependencies and Integration Points

The header depends on `XrdSfsInterface`, `XrdCmsClient`, `XrdOfsHandle`, `XrdOfsEvr`, `XrdOucCloneSeg`, and `XrdSysPthread`, while forward-declaring most plugin classes. It is the central include for `XrdOfs.cc`, `XrdOfsConfig.cc`, FSctl/file-attribute implementations, and any code that needs the concrete OFS filesystem class.

## Risks and Edge Cases

- Many members are raw pointers with process-lifetime ownership; configuration failure paths must avoid leaks that affect later startup attempts.
- `XrdOfsFile` destructor closes if `oh` is set, so code must handle close side effects during object destruction.
- `fwdOpt::~fwdOpt()` does not free `Host`; cleanup is explicit through `Reset()` or replacement in parsers.
- Role flags use overlapping bit masks (`isPeer`, `isProxy`, `isManager`, `isServer`, `isSuper`, `isMeta`), so parser and role-display logic must preserve intended combinations.
- The class exposes configuration fields publicly for historical/implementation convenience, increasing coupling across files.

## Test Signals

Compilation tests should cover inclusion order and forward declarations. Runtime tests should allocate both owned-error and external-error file/dir objects, verify sentinel handle behavior before open, exercise destructor close, validate configuration masks/role bits after parser directives, and ensure private helper declarations remain consistent with implementations in `XrdOfs.cc` and `XrdOfsConfig.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfs.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsCPFile.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsCPFile.cc

## Purpose

`XrdOfsCPFile.cc` implements the on-disk checkpoint record format used by `XrdOfsChkPnt`. It creates checkpoint files under the configured checkpoint path, stores the source logical filename in both an xattr and a CRC-protected header, appends CRC-protected original-data segments, reserves space before mutation, validates/restores metadata for recovery, and destroys or renames checkpoint files after success or failure.

## Important APIs, Types, and Functions

- Local `cpHdr` is the checkpoint header: CRC32C, header length, source-LFN length, original file size, original mtime, reserved fields, and `" file://"` marker followed by the source LFN.
- Local `cpSeg` is an appended data segment: CRC32C, data length, and original file offset followed by the original bytes.
- `XrdOfsCPFile::Create()` generates a unique `.ckp` path, creates it exclusively, stores xattr `xrdckp_srclfn`, writes a CRC-protected header, and fsyncs it.
- `Append()` writes a segment header plus data via `writev()`, maintaining `ckpDLen` and `ckpSize`.
- `Reserve()` uses `posix_fallocate()` or Darwin `F_PREALLOCATE`, truncating back on failure.
- `RestoreInfo()` opens the checkpoint, reads it whole, validates header and segment CRCs, extracts source filename/size/mtime, builds restore vectors in reverse order, and reports corruption causes.
- `Destroy()` tries `unlink()`, falling back to truncate plus `ErrState()` when unlink fails.
- `ErrState()` renames the checkpoint by appending `err` to leave a failure trail.
- `Target()` recovers the source filename from xattr first, then from the header.
- Static `genCkpPath()` uses a process-time hex prefix and mutex-protected sequence number to build names beneath `XrdOfsConfigCP::Path`.

## Control Flow

Create begins by rejecting an already-active object, generating a path, opening it with `O_CREAT|O_EXCL|O_WRONLY`, setting xattr metadata, then writing and syncing the header. Append is intentionally append-only: callers reserve space first, then append original data segments, then call `Sync()`.

Restore reads the full checkpoint into memory and validates before exposing any restore vector. Segment iteration stops either at a zero-filled allocated tail marker or at EOF. Accepted segments are returned in reverse order so later writes are restored first, preventing overlapping writes from corrupting earlier original data.

## State and Persistence Behavior

The persistent file layout is self-validating through CRC32C over the header excluding its CRC field and each segment excluding its CRC field plus data. The xattr is a fast source-name lookup and a fallback when the header or open path fails. Zero-length checkpoints mean the checkpoint was not committed and should be ignored by the restore layer.

In-memory state is `ckpFN`, `ckpFD`, `ckpDLen`, and `ckpSize`. The destructor closes the fd and frees the filename; it does not delete the checkpoint file. Deletion is explicit through `Destroy()` so crash recovery can find outstanding records.

## Dependencies and Integration Points

This file depends on `XrdOfsConfigCP::Path`, native xattrs through `XrdSysXAttrNative`, `XrdOucCRC` for CRC32C, `XrdOucIOVec` for restore vectors, and low-level POSIX calls (`open`, `writev`, `fsync`, `fstat`, `read`, `unlink`, `rename`, `posix_fallocate`). It is used by `XrdOfsChkPnt` and startup recovery in `XrdOfsConfigCP`.

## Risks and Edge Cases

- `RestoreInfo()` reads the entire checkpoint file into memory; `MaxSZ` limits normal generation, but corrupted or externally injected files could be large.
- `Destroy()` returns `errno` as a positive value on unlink failure, while most other methods return `-errno`; callers mostly treat nonzero as failure but sign consistency is a risk.
- `ErrState()` appends `err`, producing names like `.ckperr`; recovery logic specifically recognizes that suffix.
- A comment says zero-length files are "not committed"; this relies on create/truncate failure paths preserving that convention.
- `Reserve()` increases allocated space but not `ckpSize` until `Append()`; restore accepts zero-filled preallocated tails.
- The checkpoint filename sequence is process-local, seeded by seconds; `O_EXCL` protects collisions but high concurrency after restart still depends on sequence uniqueness and retry behavior outside this class.

## Test Signals

Tests should create a checkpoint, validate xattr/header source lookup, append multiple overlapping segments, ensure restore vectors are reversed, simulate CRC corruption, truncated headers, truncated segments, zero-length files, and preallocated zero tails. Space-reservation failure and unlink/rename failure should be fault-injected. Recovery tests should verify `Target()` works with and without xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsCPFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsCPFile.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsCPFile.hh

## Purpose

`XrdOfsCPFile.hh` declares `XrdOfsCPFile`, the low-level checkpoint-file abstraction that owns a checkpoint filename/file descriptor and exposes create, append, reserve, restore-info, sync, target lookup, deletion, and error-state operations.

## Important APIs, Types, and Functions

- `Append(const char *data, off_t offset, int dlen)` records original bytes for a source-file offset. Callers are expected to call `Sync()` after appends.
- `Create(const char *lfn, struct stat &Stat)` creates a checkpoint bound to a source LFN and original stat metadata.
- `Destroy()` removes the checkpoint; `ErrState()` marks it as a failed checkpoint.
- `FName(bool trim=false)` returns the checkpoint path or basename.
- `isActive()` reports whether a checkpoint filename is established.
- `Reserve(int dlen, int nseg)` preallocates space for data and segment records.
- Nested `rInfo` carries restore output: `srcLFN`, original `fSize`, original `mTime`, `DataVec`, `DataNum`, `DataLen`, and private backing buffer.
- `RestoreInfo(rInfo&, const char *&ewhy)` validates and extracts all restore data from the checkpoint.
- Static `Target(const char *ckpfn)` returns a heap-allocated source filename or explanatory text for a checkpoint path.
- Private static helpers generate checkpoint paths and recover source LFN from xattrs.

## Control Flow and Contracts

The class separates checkpoint lifecycle into explicit phases: `Create()` establishes the file and header; `Reserve()` prepares for upcoming mutations; `Append()` records original data; `Sync()` commits; `RestoreInfo()` reads a checkpoint after a crash or explicit restore; `Destroy()` or `ErrState()` ends lifecycle. Constructors can also bind to a preexisting checkpoint filename, which is used by startup recovery.

Return values are mostly `0` or negative errno. Callers must treat `rInfo`'s pointers as owned by the `rInfo` instance and avoid using them after destruction.

## State and Persistence Behavior

`ckpFN` is heap-owned and identifies the persistent checkpoint. `ckpFD` is held open during creation/append. `ckpDLen` and `ckpSize` track logical checkpoint bytes for quota/reservation. The persistent format and validation are implemented in the `.cc` file; this header defines the stable restore contract.

## Dependencies and Integration Points

The header depends only on standard integer/time types and forward declarations for `stat` and `XrdOucIOVec`, keeping it usable by checkpoint management code without pulling in OSS internals. `XrdOfsChkPnt.hh` includes it directly and composes an `XrdOfsCPFile`.

## Risks and Edge Cases

- `Target()` returns allocated memory; every caller must free it.
- `isActive()` is filename-based, not fd-based. A preexisting recovery object is active before opening the file.
- `FName()` returns a static literal `"???"` when inactive, so callers must not free its result.
- The public comments use `off_t` and `struct stat` but the header only includes `<ctime>`/`<cstdint>`; inclusion order must supply `off_t` through platform headers in consumers.

## Test Signals

Header-level tests are mostly integration tests: instantiate active and inactive objects, verify `rInfo` destructor frees restore buffers without leaks, compile consumers that include only this header plus needed system headers, and validate return-value conventions through the implementation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsCPFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsChkPnt.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsChkPnt.cc

## Purpose

`XrdOfsChkPnt.cc` implements the `XrdOucChkPnt` interface for local OFS files by using `XrdOfsCPFile` to save original data before destructive writes/truncates and to restore the file after cancellation, client failure, close cleanup, or startup recovery.

## Important APIs, Types, and Functions

- `Create()` snapshots the current file size and creates the underlying `XrdOfsCPFile`.
- `Delete()` destroys the checkpoint file if active.
- `Failed()` handles restore failure by chmoding the source file either inaccessible (`000`) or read-only, renaming the checkpoint to error state, logging, and setting `readok`.
- `Query()` reports current checkpoint bytes used and maximum configured size.
- `Restore()` parses checkpoint restore info, opens the source file when running startup recovery, truncates to original size, writes saved data back in reverse order, syncs, restores modification time through `Fctl_utimes`, deletes the checkpoint, and logs success.
- `Truncate()` checkpoints bytes that would be lost by truncating below the original size.
- `Write()` checkpoints original bytes overlapped by one or more write ranges.
- Local RAII `cUp` closes an OSS file pointer, frees temporary buffers, and closes an fd.

## Control Flow

Normal runtime flow is: `Create()` records original file size; each `cpTrunc` or `cpWrite` request calls `Truncate()` or `Write()` before the destructive operation; close or explicit restore calls `Restore()` if needed; `Delete()` removes checkpoint state when the operation commits. Startup recovery constructs `XrdOfsChkPnt` with no `lFN` and a preexisting checkpoint path, then `Restore()` derives the source path from `RestoreInfo()` and opens the file before applying recovery.

`Write()` scans all ranges, marks only ranges overlapping the original file size, reserves space, reads original data from the OSS file, appends those bytes to the checkpoint, and syncs. `Truncate()` uses the same strategy for the tail that would be discarded.

## State and Persistence Behavior

`fSize` is the original/current protected size and is reduced after checkpointing a truncate. `cpUsed` tracks total checkpointed data and is compared with `XrdOfsConfigCP::MaxSZ`. `cpFile` owns the persistent `.ckp` record; successful restore deletes it, while failure renames it to an error state and changes source-file permissions according to `cprErrNA`.

The restore path is conservative: any corruption or write failure leaves the checkpoint in an error state and makes the affected file read-only or inaccessible to avoid silent data loss.

## Dependencies and Integration Points

This file depends on `XrdOssDF` operations (`Fstat`, `Read`, `WriteV`, `Ftruncate`, `Fsync`, `Fctl`, `Open`), global `XrdOfsOss`, global `OfsEroute`, `XrdOfsConfigCP` settings, `XrdOfsCPFile`, and `XrdOucIOVec`. It is instantiated from `XrdOfsFile::CreateCKP()` and from `XrdOfsConfigCP::Recover()`.

## Risks and Edge Cases

- `Write()` appears to compare `dlen + cpUsed` after the loop using the last computed `dlen`, not the sum across all checkpointed ranges; multi-vector quota accounting may undercount. `Reserve(dlen, numVS)` also reserves only that last `dlen`, not total data length.
- `Truncate()` uses `int dlen = fSize - offset`; very large files/truncates could overflow `int` even though `fSize` is `int64_t`.
- `Restore()` calls `Fsync()` but does not check its return value.
- `Failed()` may not be able to chmod or rename, but still returns the original error and logs secondary failures.
- Startup recovery relies on `XrdOfsOss->newFile("checkpoint")`; if that returns null, `Recover()` would dereference null before reaching this class.

## Test Signals

Tests should cover checkpoint create/delete, truncating below and above original size, writes wholly before/after original EOF, multi-range writes, quota enforcement, reserve/read/append/sync failures, restore with no changed data, restore with overlapping changed data, corrupted checkpoint records, startup recovery with `lFN == 0`, and both `cprErrNA` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsChkPnt.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsChkPnt.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsChkPnt.hh

## Purpose

`XrdOfsChkPnt.hh` declares the local OFS checkpoint implementation, `XrdOfsChkPnt`, as a concrete `XrdOucChkPnt` that coordinates a source `XrdOssDF` file and an `XrdOfsCPFile` record.

## Important APIs, Types, and Functions

- Public checkpoint interface: `Create`, `Delete`, `Finished`, `Query`, `Restore`, `Truncate`, and `Write`.
- Constructor accepts an OSS file reference, source LFN, and optional preexisting checkpoint filename. Passing a checkpoint filename is how recovery binds to an existing record.
- `Finished()` deletes `this`, so callers must not use the object after invoking it.
- Private `Failed()` centralizes recovery-failure handling.
- State members are `lFN`, `cpFile`, `ossFile`, `fSize`, and `cpUsed`.

## Control Flow and Contracts

The class is designed for ownership by `XrdOfsFile::myCKP` through the abstract `XrdOucChkPnt` pointer. The caller creates a checkpoint object, calls lifecycle methods, and finally calls `Finished()`. Runtime methods operate on an already-open `ossFile`; recovery mode can be constructed with `lFN == 0` and uses the checkpoint metadata to identify/open the source.

`Truncate()` and `Write()` accept `struct iov` ranges by reference-to-pointer. The implementation writes checkpoint bookkeeping into `range[i].info`, so callers must not treat `info` as immutable across checkpoint calls.

## State and Persistence Behavior

Persistent state is delegated to `XrdOfsCPFile`. `fSize` stores the protected file size used to decide what bytes need checkpointing, and `cpUsed` tracks configured quota consumption. The object itself is heap-lifetime only and self-deletes through `Finished()`.

## Dependencies and Integration Points

The header includes `XrdOfsCPFile.hh` and `XrdOucChkPnt.hh`, forward-declares `iov` and `XrdOssDF`, and is included by `XrdOfs.cc`, `XrdOfsChkPnt.cc`, and `XrdOfsConfigCP.cc`.

## Risks and Edge Cases

- Self-deleting `Finished()` makes ownership simple for callers but dangerous if any caller keeps aliases.
- `lFN` is a raw pointer and can be changed to point inside `XrdOfsCPFile::rInfo` during restore; implementation must not outlive backing restore info in that path.
- The interface does not expose whether a checkpoint is active; callers infer from return codes.
- Range mutation through `info` is implicit in the header contract.

## Test Signals

Tests should verify object lifecycle through `Finished()`, recovery constructor behavior with a preexisting checkpoint filename, query output before and after writes, and that range `info` side effects do not conflict with callers using `struct iov`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsChkPnt.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfig.cc

## Purpose

`XrdOfsConfig.cc` implements configuration for the OFS filesystem. It parses `ofs.*`, `all.role`, `all.subcluster`, `all.export`, and `oss.defaults` directives; loads and configures plugins; establishes roles, CMS redirection, authorization, checksums, prepare handlers, event notification, TPC, POSC, checkpointing, xattrs, forwarding, trace settings, and effective mode masks.

## Important APIs, Types, and Functions

- `getVersion()` returns the compiled XRootD version string.
- `Configure()` is the startup coordinator. It reads the config file, invokes directive parsers through `ConfigXeq()`, loads plugins with `XrdOfsConfigPI`, initializes CMS/finder/balancer, event receivers, TPC, checkpointing, POSC, stats role, and displays the effective configuration.
- `Config_Display()` prints effective config, plugin display output, forwarding setup, and notify settings.
- `ConfigPosc()` builds the POSC recovery log path, creates `XrdOfsPoscq`, rehydrates pending POSC records, either holds incomplete files through retired handles or unpersists them.
- `ConfigRedir()` creates CMS finder/balancer objects depending on manager/server/proxy/subcluster role.
- `ConfigTPC()` phase 1 prepares credential/reproxy paths and monitors; phase 2 resolves OSS reproxy support and starts `XrdOfsTPC`.
- `ConfigTPCDir()` creates/protects TPC credential/reproxy directories and clears stale files.
- `ConfigXeq()` dispatches directives to parser functions or plugin parser entries.
- Parser methods: `xcrds`, `xcrm`, `xdirl`, `xexp`, `xforward`, `xmaxd`, `xnmsg`, `xnot`, `xpers`, `xrole`, `xtpc`, `xtpcal`, `xtpcr`, `xtrace`, `xatr`.
- `theRole()` maps role option bits to a human-readable role.

## Control Flow

Startup begins by requiring `XrdNetIF` and scheduler pointers from `EnvInfo`, setting defaults, and creating the plugin configurator. The config file is scanned once; recognized OFS and role directives are parsed, while export/default directives are pre-scanned to infer writable/read-only OSS capability. After parsing, the code exports role/redirect environment variables, defaults proxy plugins to `libXrdPss.so` when appropriate, and runs early TPC/event-receiver setup before plugin loading.

Plugin loading establishes `XrdOfsOss`, OSS feature flags, checksum manager, prepare handler, authorization, and optional FSctl handlers. Then redirection, FSctl, event notification, forwarding validation, proxy detection, checkpoint initialization, POSC recovery, stats, and display occur in that order. POSC is intentionally last because it needs a working filesystem.

Directive parsers are mostly single-purpose and return `0`/nonzero for success/failure. Some parsers are cumulative (`trace`, `forward`, `notify` event masks), while others replace previous state (`xattr`, `role`, redirect targets).

## State and Persistence Behavior

Configuration mutates long-lived `XrdOfs` members: role bits, mode masks, plugin pointers, event object, forwarding targets, POSC settings, TPC redirect hosts, xattr limits, and checksum behavior. It also exports environment variables used by other components (`XRDROLE`, `XRDREDIRECT`, `XRDOFS_FWD`, `XrdOss*`, authorization pointer, cache marker).

Persistent startup recovery happens in `ConfigPosc()` for POSC logs and in `XrdOfsConfigCP::Init()` for checkpoints, called from `Configure()`. TPC credential/reproxy directories are created and cleaned. Checkpointing is skipped for managers and disabled for proxy OSS backends.

## Dependencies and Integration Points

This file integrates with `XrdOfsConfigPI` for plugin loading/configuring, `XrdOss` features, `XrdCmsFinderRMT/TRG` or CMS plugin constructors, `XrdOfsTPCConfig`, `XrdOfsTPC`, `XrdOfsEvs`, `XrdOfsEvr`, `XrdOfsPoscq`, `XrdOfsStats`, `XrdAccAuthorize`, `XrdOucStream`, `XrdOuca2x`, `XrdOucUtils`, `XrdOucNSWalk`, and network utilities. It is the bridge between text config and the runtime behavior implemented in `XrdOfs.cc`.

## Risks and Edge Cases

- Configuration ordering is critical: TPC phase 1 happens before plugin load, TPC phase 2 after OSS features, POSC last, checkpoint skipped for managers/proxies.
- Several parser branches contain subtle logic hazards: `xtpc require` has a `break` before reading the auth token, making subsequent `Require()` code unreachable; `xtpcal` uses `if (i > numopts)` instead of `i >= numopts` and then immediately enters an error block, which appears to reject even valid options.
- `xnot()` allocates a new `XrdOfsEvs` after deleting any previous one; errors after partial parse can leave old state intact until replacement.
- `ConfigTPCDir()` deletes all files and links in the chosen directory at startup; path construction and permissions are safety-critical.
- POSC recovery may unpersist files on startup depending on hold time and queue records.
- If `EnvInfo` is null, later uses such as `EnvInfo->GetPtr("XrdFSCtl_PC*")` rely on earlier setup; startup environments must supply expected pointers.
- `umask` is set globally from creation masks, affecting process-wide file creation.

## Test Signals

Configuration tests should parse each directive and invalid option, verify mode-mask transformations, role combinations, forwarding display and disable conditions, notify and notifymsg setup, xattr limits, TPC redirect parsing including IPv6/localhost/cgi, TPC directory cleanup permissions, plugin feature flags, proxy behavior, checkpoint/POSC enablement, and startup POSC recovery. Regression tests should specifically cover `xtpc require` and `xtpcal allow` parsing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigCP.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigCP.cc

## Purpose

`XrdOfsConfigCP.cc` implements configuration and startup recovery for OFS checkpoint files. It owns the static checkpoint settings, parses the `ofs.chkpnt` directive, initializes the checkpoint directory, restores outstanding `.ckp` files, reports unresolved `.ckperr` failures, and disables checkpointing for unsafe default `/tmp` paths unless explicitly enabled.

## Important APIs, Types, and Functions

- Static settings: `Path`, `MaxSZ`, `MaxVZ`, `cprErrNA`, `Enabled`, `isProxy`, and `EnForce`.
- `Init()` resolves the checkpoint directory, creates it, rejects or warns about `/tmp`, scans files with `XrdOucNSWalk`, calls `Recover()` for each entry, reports restore counts, and finalizes enablement.
- `Parse()` handles `disable`, `enable`, `cprerr`, `maxsz`, and `path` options for the `chkpnt` directive.
- Private `Stats` counts files, recovered checkpoints, errors, skipped entries, and unresolved error files.
- `Recover()` classifies `.ckperr`, `.ckp`, and unknown files; unresolved errors are reported with `XrdOfsCPFile::Target()`, valid checkpoints are restored through `XrdOfsChkPnt`.

## Control Flow

During OFS configure, non-manager non-proxy servers call `XrdOfsConfigCP::Init()`. If checkpointing is disabled or proxy mode is set, initialization returns success without work. Otherwise, `Path` is either derived from a configured absolute path plus instance/chkpnt suffix or from `XRDADMINPATH/chkpnt/`. The directory is created, scanned, and each file is recovered or reported. If the resolved path is rooted in `/tmp/` and the user did not explicitly `enable`, checkpointing is auto-disabled after recovery.

`Parse()` is invoked from `XrdOfs::ConfigXeq()` for `ofs.chkpnt`. It updates static settings as tokens are read.

## State and Persistence Behavior

Checkpoint state is persisted as files in `Path`. On startup, `.ckp` files are treated as recoverable in-progress checkpoints and are applied to their target files. `.ckperr` files are treated as unresolved restore failures requiring operator attention. Other files are skipped with a warning. `MaxSZ` limits per-checkpoint saved data during runtime, and `cprErrNA` controls whether restore failures make the source inaccessible or read-only.

## Dependencies and Integration Points

This file depends on global `XrdOfsOss` to allocate recovery file objects, global `OfsEroute` for logging, `XrdOfsChkPnt` for actual restore, `XrdOfsCPFile::Target()` for unresolved error reporting, `XrdOuca2x` for size parsing, `XrdOucUtils` for path construction/creation, `XrdOucNSWalk` for directory scans, and `XrdOucString` for normalized path strings.

## Risks and Edge Cases

- In `Parse()`, the `cprerr` branch compares the current token `val` to `makero`/`stopio` without first reading the option token after `cprerr`; as written, `ofs.chkpnt cprerr makero` appears to fail. This should be tested or corrected.
- `Recover()` does not check whether `XrdOfsOss->newFile("checkpoint")` returns null before constructing `XrdOfsChkPnt`.
- `MaxVZ` is declared and initialized but not used in this file or the visible checkpoint implementation.
- `/tmp` auto-disable happens after scanning/recovery; explicit `enable` only warns.
- `Path` construction differs depending on whether `Path` was explicitly configured; configured paths get instance plus `chkpnt/` appended by `Init()`, even though `Parse()` already ensures a trailing slash.

## Test Signals

Tests should cover default path resolution with and without `XRDADMINPATH`, absolute path parsing and normalization, `/tmp` auto-disable versus explicit enable, directory creation failure, scan failure, recovery of valid `.ckp`, unresolved `.ckperr`, skipped unknown files, restore failure counts, and all parser options including the suspected `cprerr` token bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigCP.cc -->
