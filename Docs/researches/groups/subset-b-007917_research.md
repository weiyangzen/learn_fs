# subset-b-007917 research

This grouped report covers the requested XrdCeph OSS/Ceph POSIX adapter files and XrdCks checksum framework files. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVNoOp.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVNoOp.cc

Purpose: implements the passthrough `XrdCephReadVNoOp::convert()` adapter for vectored reads. It accepts one `ExtentHolder` containing the caller's requested extents and returns a vector of `ExtentHolder` objects, each holding exactly one original extent. This preserves XRootD `readv` request granularity while allowing the decorator path to use the same `IXrdCephReadVAdapter` interface as coalescing algorithms.

Important APIs and control flow: `convert(const ExtentHolder&)` pulls the immutable `ExtentContainer` from the input, iterates from `begin()` to `end()`, constructs a temporary holder, pushes the current `Extent`, and appends the holder to the output vector. There is no filtering, sorting, merging, or validation. Empty input returns an empty vector.

State and persistence: the implementation is stateless; it only allocates local `std::vector` and `ExtentHolder` instances. Persistence and data transfer are handled later by `XrdCephOssReadVFile`.

Dependencies and integration points: depends on `BufferUtils.hh` for `Extent`, `ExtentContainer`, and `ExtentHolder`, and implements the virtual adapter contract declared in `IXrdCephReadVAdapter.hh`. It is selected by `XrdCephOssReadVFile` when `ceph.readvalgname passthrough` is configured or when an invalid algorithm falls back to passthrough.

Risks and test signals: behavior should be tested with empty, single-extent, and multi-extent holders to ensure output count and order are unchanged. Because later `ReadV` copy-back assumes converted inner extents remain in original request order, any future change that sorts or merges here would need corresponding request-to-buffer mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVNoOp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVNoOp.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVNoOp.hh

Purpose: declares the no-op ReadV adapter in namespace `XrdCephBuffer`. The class gives the Ceph OSS readv decorator a concrete `IXrdCephReadVAdapter` that does not change the request layout, useful for functional testing, instrumentation, and a conservative default path.

Important APIs and types: `class XrdCephReadVNoOp : virtual public IXrdCephReadVAdapter` exposes a trivial constructor/destructor and overrides `std::vector<ExtentHolder> convert(const ExtentHolder&)`. It includes `<vector>`, `<sys/types.h>`, `BufferUtils.hh`, and `IXrdCephReadVAdapter.hh`.

Control flow and integration: the header participates in the strategy selection performed by `XrdCephOssReadVFile`. The adapter's output type matches the decorator's loop over mapped extent groups, so callers can swap between passthrough and `XrdCephReadVBasic` without changing the file wrapper.

State and persistence: no data members are declared. Instances hold no file descriptors, buffers, or Ceph state.

Risks and test signals: the class name and include guard are stable but the file comments contain typos only. Unit tests can instantiate through `IXrdCephReadVAdapter` and assert polymorphic dispatch, output grouping, and zero state sharing across instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVNoOp.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBulkAioRead.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBulkAioRead.cc

Purpose: implements `bulkAioRead`, a helper that converts one logical file read into parallel librados object reads for non-striper access. It is used by `ceph_posix_nonstriper_pread()` and `ceph_nonstriper_readv()` to read striped object suffixes directly when files have a single stripe.

Important APIs: the constructor stores `librados::IoCtx*`, a variadic log wrapper, and `CephFileRef*`. `read()` decomposes a file offset and request length into object-local chunks using `file_ref->objectSize`; `addRequest()` creates per-object `ObjectReadOperation` entries and `ReadOpData` buffers; `submit_and_wait_for_complete()` issues `aio_operate()` for each object and waits for all completions; `get_results()` copies returned `bufferlist` data into client buffers and clears internal vectors/maps.

Control flow: callers enqueue one or more logical reads, submit all collected operations, then call `get_results()`. Object names are generated as `<file_ref->name>.<16 hex object index>`, matching the RADOS striper object suffix convention. The implementation returns early on allocation failures, suffix formatting overflow, librados return values, or internal length checks.

State and persistence: `operations` groups operations by object index and `buffers` owns output buffer metadata until completion. It does not persist file metadata; it relies on `CephFileRef` for object layout and file name. `clear()` is called by the destructor and after successful result collection.

Dependencies and integration: depends on librados C++ APIs, `CephFileRef` from `XrdCephPosix.hh`, and error constants. It deliberately bypasses `RadosStriper` reads for performance on single-stripe files.

Risks and test signals: request splitting across object boundaries, zero-length reads, sparse object `ENOENT`, allocation failure, and partial result copy should be covered. `submit_and_wait_for_complete()` does not cancel remaining AIOs after a failure, so error-path lifetime and completion cleanup are important integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBulkAioRead.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBulkAioRead.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBulkAioRead.hh

Purpose: declares the non-striper bulk asynchronous read helper and the small RAII wrappers it uses around librados read operations and completions.

Important APIs and types: `CmplPtr` wraps `librados::AioCompletion*`, with `use()`, `wait_for_complete()`, `get_return_value()`, and destructor release behavior. `ReadOp` pairs an `ObjectReadOperation` with a completion. `ReadOpData` stores the caller's output pointer, a `ceph::bufferlist`, and librados return code. `bulkAioRead` exposes `read()`, `submit_and_wait_for_complete()`, `get_results()`, and `clear()`, while `addRequest()` is private.

Control flow and integration: callers declare file-coordinate reads, then explicitly submit/wait and harvest results. The class is not a general POSIX file object; it is a batch builder used inside `XrdCephPosix.cc` to implement faster `pread` and `readv` against direct RADOS object names.

State and persistence: stores mutable maps/vectors of pending operations and temporary bufferlists. It borrows the `IoCtx`, log function, and `CephFileRef`; those must outlive the helper.

Dependencies: uses `<map>`, `<vector>`, `<memory>`, librados, and `XrdCephPosix.hh`. The log callback uses the same function pointer shape as the POSIX shim.

Risks and test signals: lifetime tests should verify completion release, no use after `CephFileRef` deletion, repeated `read()` calls before submit, and post-`get_results()` reuse. Boundary tests should use offsets at object edges and multi-object reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBulkAioRead.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOss.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOss.cc

Purpose: implements the XRootD OSS plugin entry point and storage-system object for Ceph-backed files. It translates XRootD OSS operations into `ceph_posix_*` calls and optionally wraps file objects with readv and buffering decorators.

Important APIs: `XrdOssGetStorageSystem()` initializes logging, parses default Ceph parameters, installs the POSIX log callback, and returns `XrdCephOss`. `Configure()` parses directives such as `ceph.nbconnections`, `ceph.namelib`, `ceph.usedefaultpreadalg`, `ceph.usedefaultreadvalg`, `ceph.aiowaitthresh`, `ceph.usebuffer`, `ceph.buffersize`, `ceph.buffermaxpersimul`, `ceph.usereadv`, `ceph.readvalgname`, `ceph.bufferiomode`, and `ceph.reportingpools`. File-system methods implement `Stat`, `StatFS`, `StatLS`, `StatVS`, `Truncate`, `Unlink`, and directory/file factories; unsupported mutations like `Create`, `Rename`, and `Chmod` return `-ENOTSUP`, while directory create/remove intentionally return success for POSIX-assuming clients.

Control flow: configuration sets global POSIX knobs and instance decorator options. `Stat()` handles fake root stats, pool-name location for space reporting, and object stat through `ceph_posix_stat()`. `StatLS()` validates configured reporting pools, queries used bytes via pool stats, reads a `total_space` xattr from `<pool>:__spaceinfo__`, and formats OSS spaceinfo fields. `newFile()` creates a base `XrdCephOssFile`, optionally wraps it in `XrdCephOssReadVFile`, then optionally in `XrdCephOssBufferedFile`.

State and persistence: instance fields retain configuration only. Persistent storage state is in Ceph; process-wide connection pools and file descriptors live in `XrdCephPosix.cc`. The destructor calls `ceph_posix_disconnect_all()`.

Dependencies and integration points: integrates with XRootD plugin versioning, `XrdOucStream`, name-to-name loaders, `XrdSysError`, `XrdCephPosix`, and decorator classes. `m_translateFileName()` uses global `g_namelib`.

Risks and test signals: config parsing needs coverage for invalid numbers, missing values, and decorator order. `StatLS()` depends on substring matching in `m_configPoolnames` and a Ceph xattr convention. `ceph.usereadv` logs `m_configBufferEnable` rather than the readv setting, which is a diagnostic risk. Tests should cover root stat, pool stat, object stat, spaceinfo formatting, and all file factory combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOss.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOss.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOss.hh

Purpose: declares the `XrdCephOss` class, the main XRootD OSS implementation for Ceph storage. It documents path parameter precedence for user, pool, and layout defaults.

Important APIs and types: `XrdCephOss : public XrdOss` overrides the storage-system lifecycle and file-system surface: `Configure`, `Init`, `Stat`, `StatFS`, `StatLS`, `StatVS`, `Truncate`, `Unlink`, `Mkdir`, `Remdir`, `newDir`, and `newFile`. Public flags `m_useDefaultPreadAlg` and `m_useDefaultReadvAlg` steer base file read behavior. Private fields hold buffer/readv feature toggles, buffer size/mode, max simultaneous buffers, readv algorithm name, and reporting pool list.

Control flow and integration: the header defines the configuration state consumed in `XrdCephOss.cc` and by wrappers such as `XrdCephOssBufferedFile` and `XrdCephOssFile`. It is included by most Ceph OSS classes to access the parent object and algorithm flags.

State and persistence: only runtime configuration is stored here; Ceph connections, fd maps, and object metadata are external.

Dependencies: includes XRootD `XrdOss.hh` and `XrdSysError.hh`, plus `<string>`.

Risks and test signals: public mutable algorithm flags make behavior dependent on configuration and object sharing. Tests should verify default values, config overrides, and that buffered/readv decorators observe the configured flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOss.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssBufferedFile.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssBufferedFile.cc

Purpose: implements a decorator around `XrdCephOssFile` that adds buffered read/write behavior and summary metrics while delegating metadata and raw operations to the wrapped file object.

Important APIs: `Open()` opens the inner file, stores fd/path/flags, and starts a timer. `Close()` flushes write cache when needed, logs aggregate counters and elapsed time, then closes the inner file. `Read(void*, off_t, size_t)` maintains one read buffer algorithm per calling thread, retries `-EBUSY`, and falls back to the inner file if a new buffer cannot be created. `Read(XrdSfsAio*)`, `Write()`, and `Write(XrdSfsAio*)` route through `IXrdCephBufferAlg`. `ReadV`, `ReadRaw`, `Fstat`, `Fsync`, and `Ftruncate` mostly delegate.

Control flow: buffer creation is protected by `m_buf_mutex`. `createBuffer()` sizes buffers based on `m_bufsize` unless the per-file buffer count has reached `m_maxCountReadBuffers`, then creates a smaller 1 MiB buffer. It selects `CephIOAdapterAIORaw` for `aio` mode or `CephIOAdapterRaw` for `io` mode; invalid modes close the inner file and return null.

State and persistence: maintains one write buffer (`m_bufferAlg`), a map of per-thread read buffers, file flags/path, counters, and timing. Persistent writes are flushed through the buffer algorithm before close.

Dependencies and integration: depends on buffer interfaces and simple implementations under `XrdCephBuffers`, `XrdSfsAio`, `XrdCephPosix`, and the parent `XrdCephOss` pread flag.

Risks and test signals: tests should cover close-after-flush failure, concurrent reads from multiple threads, maximum buffer behavior, invalid `bufferiomode`, retry exhaustion, and write-cache flush ordering. AIO read creation does not check `createBuffer()` for null before dereference, so invalid mode or allocation failure is a notable crash risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssBufferedFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssBufferedFile.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssBufferedFile.hh

Purpose: declares the buffered file decorator used by `XrdCephOss::newFile()` when `ceph.usebuffer` is enabled.

Important APIs and types: `XrdCephOssBufferedFile : virtual public XrdCephOssFile` overrides the full `XrdOssDF` file API: open/close, sync and async read/write, `ReadV`, `ReadRaw`, `Fstat`, `Fsync`, and `Ftruncate`. `createBuffer()` returns a `std::unique_ptr<IXrdCephBufferAlg>` for raw or async buffer I/O.

State and persistence: stores the wrapped `XrdCephOssFile*` and deletes it in the destructor, so ownership is transferred to the decorator. It tracks per-thread read buffers in a map, a single write buffer, retry policy, buffer size/mode, path, flags, start time, and atomic byte counters.

Dependencies and integration: includes the Ceph OSS base classes and buffer interfaces. It relies on `m_fd` inherited from `XrdCephOssFile` after inner open.

Risks and test signals: ownership tests should ensure no double delete in decorator stacks. Concurrency tests should exercise `m_bufferReadAlgs` map access and read/write counters. Configuration tests should validate buffer sizes, maximum buffer counts, and `aio` versus `io` adapter selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssBufferedFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssDir.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssDir.cc

Purpose: implements the directory side of the Ceph OSS plugin. Because Ceph object pools do not have true POSIX directories, this class delegates to the POSIX shim's object iterator abstraction.

Important APIs: the constructor stores the parent `XrdCephOss*` and initializes `m_dirp`. `Opendir()` calls `ceph_posix_opendir(&env, path)` and maps null to `-errno`, catching parameter syntax exceptions as `-EINVAL`. `Readdir()` calls `ceph_posix_readdir()`. `Close()` calls `ceph_posix_closedir()` and returns success.

Control flow and integration: `XrdCephOss::newDir()` constructs this class. The POSIX layer only accepts root-like paths and returns object names derived from striper object suffixes.

State and persistence: `m_dirp` holds a cast `DirIterator` pointer allocated in `XrdCephPosix.cc`. No directory entries are persisted by this class.

Risks and test signals: `Close()` does not guard null `m_dirp`; tests should cover failed `Opendir()` followed by cleanup behavior. Directory listing tests should verify object suffix filtering and buffer truncation through the POSIX shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssDir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssDir.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssDir.hh

Purpose: declares `XrdCephOssDir`, the `XrdOssDF` directory object returned by the Ceph OSS plugin.

Important APIs: constructor accepts `XrdCephOss*`; virtual methods are `Opendir`, `Readdir`, and `Close`. The class stores `DIR *m_dirp` and a parent pointer.

Control flow and integration: the header allows `XrdCephOss.cc` to instantiate directory handles while hiding the Ceph iterator details behind the standard OSS directory API.

State and persistence: state is a transient directory iterator pointer. Object listing state comes from librados `NObjectIterator` in the POSIX layer.

Risks and test signals: tests should verify that `Opendir("/")` and non-root paths map to the expected success/error behavior, and that `Close()` releases the iterator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssDir.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssFile.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssFile.cc

Purpose: implements the base `XrdOssDF` file object for Ceph. It is the innermost file layer and maps XRootD file operations to the `ceph_posix_*` shim.

Important APIs: `Open()` calls `ceph_posix_open()` and stores the returned synthetic fd. `Close()` calls `ceph_posix_close()`. Synchronous `Read()` uses either striper `ceph_posix_pread()` or direct-object `ceph_posix_nonstriper_pread()` based on `m_useDefaultPreadAlg`, with fallback to striper on sparse or unsupported cases. `ReadV()` similarly chooses `ceph_striper_readv()` or `ceph_nonstriper_readv()`. AIO methods call `ceph_aio_read()` and `ceph_aio_write()` with callbacks that set `aiop->Result` and invoke XRootD completion. `Fstat`, `Write`, `Fsync`, and `Ftruncate` delegate to the POSIX shim.

Control flow: fallback paths log a warning when direct object reads fail with `-ENOENT` or `-ENOTSUP` and striper reads then succeed. `Read(off_t,size_t)` is a stub returning `XrdOssOK`, matching XRootD's optional read-without-buffer signature.

State and persistence: stores only the current synthetic fd and parent OSS pointer. Persistent object content is controlled by `XrdCephPosix.cc`.

Dependencies and integration: used directly or wrapped by readv/buffer decorators. Depends on `XrdSfsAio`, `XrdCephPosix`, and parent configuration flags.

Risks and test signals: tests should cover read algorithm fallback, AIO callback results, bad fd handling through POSIX functions, write access errors, and decorator inheritance of `m_fd`. The unbuffered `Read(off_t,size_t)` stub should be verified against XRootD expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssFile.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssFile.hh

Purpose: declares the base Ceph file descriptor object implementing `XrdOssDF`.

Important APIs and types: `XrdCephOssFile : virtual public XrdOssDF` exposes open/close, sync and async reads/writes, `ReadV`, `ReadRaw`, `Fstat`, `Fsync`, `Ftruncate`, and `getFileDescriptor()`. Protected members are `int m_fd` and `XrdCephOss *m_cephOss`.

Control flow and integration: this class is the common base for decorators. `XrdCephOssReadVFile` and `XrdCephOssBufferedFile` inherit virtually and wrap an owned `XrdCephOssFile*` while also using inherited `m_fd` for adapter creation and logging.

State and persistence: tracks a synthetic fd allocated by the POSIX shim. No object data is stored in the class.

Dependencies: includes `XrdOss.hh` and `XrdCephOss.hh`.

Risks and test signals: inheritance and ownership tests should ensure wrappers do not obscure the fd or double-close. API tests should verify direct `ReadV` versus decorated `ReadV` behavior under configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssReadVFile.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssReadVFile.cc

Purpose: implements a readv decorator that can transform many small vectored reads into larger backing reads, then copy useful subranges back to the caller's `XrdOucIOVec` buffers.

Important APIs: the constructor selects `XrdCephReadVNoOp` for `passthrough`, `XrdCephReadVBasic` for `basic`, and falls back to passthrough for invalid names. `Open()` delegates to the wrapped file and mirrors its fd. `Close()` logs aggregate read timing. `ReadV()` builds an `ExtentHolder` from the caller's vectors, converts it with `m_readVAdapter`, reserves a buffer sized to the largest mapped extent, reads each mapped extent through the wrapped file's `Read()`, and copies each inner extent to the corresponding original `readV[counter].data`.

Control flow: the method verifies full reads by comparing returned bytes with mapped extent length; short positive reads return `-ESPIPE`, negative reads propagate. Other file APIs delegate unchanged to the inner object.

State and persistence: owns the wrapped file pointer and deletes it in the destructor. It keeps adapter name, adapter instance, verbose logging flag, and atomic timing counters. No data persists beyond the read buffer.

Dependencies and integration: depends on `BufferUtils`, `IXrdCephReadVAdapter`, `XrdCephReadVBasic`, `XrdCephReadVNoOp`, and the base file API.

Risks and test signals: the implementation uses `buffer.reserve(buffersize)` but not `resize()`, so `buffer.data()` points to storage with size zero; this is a serious correctness risk for backing reads and copy-out. Tests should cover passthrough and coalesced extents, copy-back ordering, short reads, and empty readv input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssReadVFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssReadVFile.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssReadVFile.hh

Purpose: declares the readv decorator used when `ceph.usereadv` is enabled.

Important APIs and types: `XrdCephOssReadVFile : virtual public XrdCephOssFile` overrides `ReadV` and delegates the rest of the file interface. It stores `m_xrdOssDF`, `m_algname`, `std::unique_ptr<IXrdCephReadVAdapter>`, and timing counters for backing Ceph reads.

Control flow and integration: selected by `XrdCephOss::newFile()` before optional buffering. This order means a buffered wrapper delegates `ReadV` to this decorator, while ordinary reads may be buffered outside it.

State and persistence: the decorator owns and deletes the wrapped file. Metrics are process memory only and logged on close.

Dependencies: includes Ceph OSS classes and readv/buffer interfaces, plus `<memory>`.

Risks and test signals: tests should verify algorithm selection, invalid algorithm fallback, destructor ownership, and that decorated write/AIO paths are transparent. Timing counters are atomic but `m_timer_longest` uses load-then-store without compare-exchange, so concurrent reads can under-report longest duration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssReadVFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephPosix.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephPosix.cc

Purpose: provides the POSIX-like shim that backs the Ceph OSS and xattr plugins. It maps path syntax, synthetic file descriptors, reads/writes, xattrs, stats, directory iteration, and connection pooling onto librados and libradosstriper APIs.

Important APIs and state: global vectors `g_radosStripers`, `g_ioCtx`, and `g_cluster` hold per-pool-index connection resources; `g_fds` maps synthetic fds to `CephFileRef`; `g_filesOpenForWrite` tracks in-progress writes for stat behavior; mutexes protect connection and fd maps. Path parsing uses defaults from `g_defaultParams` and optional `XrdOucEnv` entries, with optional name translation through `g_namelib`.

Control flow: `ceph_posix_open()` parses the file, obtains a striper, stats existence, adjusts read layout from object xattrs when possible, and inserts a fd for read or write. Reads can use striper APIs or direct RADOS object reads via `bulkAioRead`; direct reads only support `nbStripes == 1` and fall back elsewhere. Writes use striper write/aio_write and maintain counters. AIO callbacks update stats before invoking XRootD callbacks. Stat methods synthesize POSIX fields; xattr methods call striper get/set/list/remove xattrs; space methods use cluster and pool stats; unlink removes a striper lock xattr on `-EBUSY` and retries. Directory listing exposes top-level objects with `.0000000000000000` suffixes stripped.

State and persistence: persistent state is Ceph object content, xattrs, and pool stats. Process state includes open fds, counters, connection pools, layout defaults, and pending AIO bookkeeping.

Dependencies and integration: depends on librados, libradosstriper, XRootD AIO/OSS/platform types, `XrdCephBulkAioRead`, and checksum/xattr users through exported functions in `XrdCephPosix.hh`.

Risks and test signals: critical tests include multi-connection initialization, concurrent open/close/read/write, AIO completion after close assumptions, direct-read fallback, xattr list allocation/free, path parsing, name translation, pool stats, and unlink lock retry. Notable risks include synthetic fd wraparound, borrowed `CephFileRef*` lifetime, `ceph_posix_internal_listxattrs()` copying the name with `Vlen+1` instead of name length, and `ceph_posix_freexattrlist()` freeing `aPL->Name` even though entries are allocated as one block with embedded names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephPosix.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephPosix.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephPosix.hh

Purpose: declares the Ceph POSIX facade used by the OSS, buffering, readv, bulk read, and xattr layers.

Important APIs: exposes setup functions (`ceph_posix_set_defaults`, `ceph_posix_disconnect_all`, `ceph_posix_set_logfunc`), file operations (`open`, `close`, seek, read, pread variants, write, pwrite, AIO read/write, fstat, stat, fsync, fcntl, truncate, unlink), readv helpers, xattr operations, stats, and directory iteration. It also declares `ceph_posix_maybestriper_pread()` for code that wants direct-object reads with optional striper fallback.

Important types: `CephFile` stores parsed object name, pool, user, stripe count, stripe unit, and object size. `CephFileRef` extends it with flags, mode, offset, stats mutex, byte counters, operation counters, and AIO timing fields. `AioCB` is the callback signature for XRootD AIO completion.

State and persistence: the header describes transient file-reference state, not persistent storage. The implementation persists through Ceph object and xattr operations.

Dependencies and integration: includes `XrdOucEnv`, `XrdSysXAttr`, `XrdSysPthread`, and `XrdOucIOVec`. `LOGCEPH` is a simple logging macro used by buffer and readv code.

Risks and test signals: interface tests should cover return-value conventions and negative errno mapping. Because `CephFileRef` contains mutable stats protected by `XrdSysMutex`, concurrent AIO and close tests are especially important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephPosix.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephXAttr.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephXAttr.cc

Purpose: implements the XRootD `XrdSysXAttr` plugin for Ceph objects using the same POSIX shim defaults and path syntax as the OSS plugin.

Important APIs: `XrdSysGetXAttrObject()` sets the log prefix, logger, and default Ceph parameters, then returns `XrdCephXAttr`. `Del`, `Get`, `List`, and `Set` dispatch to fd-based POSIX xattr calls when an fd is supplied and path-based calls otherwise. `Free()` delegates list cleanup to `ceph_posix_freexattrlist()`.

Control flow: path-based methods catch syntax exceptions from path parsing and return `-EINVAL`. `Set()` ignores the `isNew` creation-only flag and always passes flags `0` to Ceph.

State and persistence: the class has no members. Persistent checksum or metadata values are Ceph xattrs on objects.

Dependencies and integration: uses XRootD plugin versioning, `XrdSysError`, `XrdOucTrace`, and `XrdCephPosix` xattr functions. It can share global Ceph defaults with the OSS plugin when loaded in the same process.

Risks and test signals: tests should cover fd 0 handling (`List()` uses `fd > 0` while `Get`/`Set` use `fd >= 0`), ignored `isNew`, binary xattr values, path syntax errors, and list/free memory correctness through the POSIX shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephXAttr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephXAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephXAttr.hh

Purpose: declares `XrdCephXAttr`, the Ceph-backed implementation of XRootD's extended attribute interface.

Important APIs: overrides `Del`, `Free`, `Get`, `List`, and `Set` from `XrdSysXAttr`. Comments document path/default precedence and return conventions for each xattr operation.

Control flow and integration: the class is instantiated by the `XrdSysGetXAttrObject` plugin entry point in the implementation file. It delegates all real work to the POSIX facade.

State and persistence: no member state; xattrs are persistent Ceph object metadata.

Dependencies: includes `XrdSys/XrdSysXAttr.hh`.

Risks and test signals: tests should validate behavior with open fds versus paths, absent attributes, binary values, and list memory ownership. The same default-parameter conflict noted in comments applies when OSS and xattr plugins are both configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephXAttr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdCks/CMakeLists.txt

Purpose: adds XrdCks checksum framework sources to `XrdUtils` and builds the zlib-compatible CRC32 checksum calculator as a loadable module.

Important build APIs: `target_sources(XrdUtils PRIVATE ...)` lists manager, loader, algorithm, assist, data, wrapper, and xattr helper files. `set(XrdClsCalczcrc32 XrdCksCalczcrc32-${PLUGIN_VERSION})` names the plugin module. `add_library(... MODULE XrdCksCalczcrc32.cc)`, `target_link_libraries(... PRIVATE XrdUtils ZLIB::ZLIB)`, and `install(TARGETS ... LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})` define build and install behavior.

Control flow and integration: most checksum code is compiled into `XrdUtils`; the zlib CRC32 implementation remains a plugin that exports `XrdCksCalcInit`.

State and persistence: build metadata only. Runtime checksum state lives in calculator and manager classes.

Dependencies: requires `ZLIB::ZLIB` for the zcrc32 plugin and the project-defined `PLUGIN_VERSION`, `XrdUtils`, and install directory variables.

Risks and test signals: build tests should verify plugin naming, module install path, and zlib discovery. ABI tests should ensure sources added to `XrdUtils` match headers exported to plugin users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCks.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCks.hh

Purpose: defines the abstract checksum manager interface used by XRootD and checksum plugins.

Important APIs and types: `XrdCksPCB` provides progress callback `Info(fsize, csbytes)`. `XrdCks` declares pure virtual methods `Calc`, `Del`, `Get`, `Config`, `Init`, `List`, `Name`, `Object`, `Size`, `Set`, and `Ver`, with overloads accepting a progress callback. The header also defines `XRDCKSINITPARMS` and documents the external `XrdCksInit()` plugin entry point and version-info convention.

Control flow and integration: managers may compute checksums, persist them in xattrs, retrieve and validate them, or delegate to plugin calculators. The interface supports both physical and logical filenames depending on manager configuration and OSS integration.

State and persistence: base class stores `XrdSysError *eDest` for diagnostics. Persistent checksum values are managed by concrete implementations, often in extended attributes.

Dependencies: includes `XrdCksData.hh` and forward-declares stream, plugin, and error classes.

Risks and test signals: implementation tests should verify negative errno contracts (`-EDOM`, `-ENOTSUP`, `-ESRCH`, `-ESTALE`), default checksum selection, progress callback invocation, and logical/physical filename routing with OSS-backed managers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCks.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksAssist.cc -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksAssist.cc

Purpose: implements helper functions for encoding and decoding XRootD checksum extended attributes.

Important APIs: `XrdCksAttrData(cstype, csval, mtime)` validates checksum type/name length and known hex-string lengths, fills an `XrdCksData` object, sets file mtime and checksum age, and returns its raw bytes as `std::vector<char>`. `XrdCksAttrName(cstype, nspfx)` lowercases the type and returns names like `XrdCks.adler32`, optionally prefixed. `XrdCksAttrValue(cstype, csbuff, csblen)` validates a raw `XrdCksData` blob and returns the checksum value as hex.

Control flow: a static checksum table maps known algorithms to hex and binary lengths. `LowerCase()` bounds-checks against destination length. Errors are reported by setting `errno` and returning an empty vector/string.

State and persistence: helpers are stateless, but their serialized `XrdCksData` layout is the persistent xattr value format.

Dependencies and integration: depends on `XrdCksData.hh` and standard string/time utilities. Used by checksum xattr consumers to maintain consistent xattr names and binary values.

Risks and test signals: tests should cover known and unknown algorithms, uppercase input normalization, namespace prefixes with/without trailing dots, malformed binary blobs, stale length fields, and errno values (`ENAMETOOLONG`, `EINVAL`, `EOVERFLOW`, `EMSGSIZE`, `ENOENT`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksAssist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksAssist.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksAssist.hh

Purpose: declares checksum xattr helper functions that convert between external algorithm/value strings and the serialized `XrdCksData` xattr representation.

Important APIs: `XrdCksAttrData()` returns raw bytes suitable for setting an xattr. `XrdCksAttrName()` returns the xattr key name. `XrdCksAttrValue()` converts a raw xattr payload back into a hex checksum string.

Control flow and integration: callers use these helpers around xattr operations, usually with `XrdSysXAttr` or OSS-backed checksum managers. The header documents expected inputs and error reporting through `errno`.

State and persistence: no state, but the helpers define the persistent wire/storage format for XRootD checksum metadata.

Dependencies: includes `<ctime>`, `<string>`, and `<vector>`.

Risks and test signals: API tests should verify buffer length expectations and that callers handle empty return values by consulting `errno`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksAssist.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalc.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalc.hh

Purpose: defines the abstract interface for checksum calculation algorithms and plugin calculators.

Important APIs: `Calc()` provides a default one-shot implementation over `Init`, `Update`, and `Final`. `Combinable()` and `Combine()` support algorithms that can combine adjacent block checksums. `Current()` defaults to `Final()`. Pure virtual methods are `Final`, `Init`, `New`, `Type`, and `Update`; `Recycle()` deletes by default. The header documents the external `XrdCksCalcInit()` plugin factory.

Control flow and integration: managers request new calculator instances via `New()` or plugin factory entry points, stream file data through `Update()`, then call `Final()` for binary checksum bytes.

State and persistence: base class stores no state. Concrete calculators own algorithm state and return pointers valid until object deletion or reuse.

Dependencies: none beyond C++ class declarations.

Risks and test signals: algorithm implementations should be tested for repeated `Init()` reuse, one-shot versus incremental equality, `Current()` side effects, correct `Type()` byte sizes, and plugin ABI/version declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcadler32.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcadler32.hh

Purpose: implements the built-in Adler-32 checksum calculator as a header-only `XrdCksCalc` subclass.

Important APIs: `Init()` sets sum1 to 1 and sum2 to 0. `Update()` processes the buffer in chunks up to `AdlerNMax`, using unrolled `DO1/DO2/DO4/DO8/DO16` macros and modulo `AdlerBase`. `Final()` combines sums into a 32-bit value and converts to network order on little-endian platforms. `Type()` returns `"adler32"` and a 4-byte size; `New()` clones the calculator type.

Control flow and integration: managers can instantiate the calculator directly or through the loader's built-in registry. The returned binary checksum can be stored in `XrdCksData`.

State and persistence: mutable state is `unSum1`, `unSum2`, and `AdlerValue`. No persistence beyond final checksum bytes.

Dependencies: includes `XrdCksCalc.hh`, endian/platform headers, and networking byte-order support.

Risks and test signals: test vectors should compare one-shot and segmented updates, empty buffer behavior, endian output, and large buffers crossing `AdlerNMax`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcadler32.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32.cc -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32.cc

Purpose: contains the lookup table and streaming update routine for XRootD's built-in non-reflected CRC-32 calculator.

Important APIs: defines static `XrdCksCalccrc32::crctable[256]` and implements `Update(const char*, int)`, which increments total length and updates `C32Result` byte by byte with a table lookup based on the high byte of the current CRC and input byte.

Control flow: `Final()` in the header later folds total-length bytes into the CRC before xor/output conversion. This source only handles incremental data ingestion.

State and persistence: mutates the calculator instance fields `TotLen` and `C32Result`; final binary checksum may be persisted through manager/xattr layers.

Dependencies: includes `XrdCksCalccrc32.hh`.

Risks and test signals: tests should compare against established XRootD CRC32 vectors, verify segmented updates equal one-shot calculation, and exercise zero-length data because length folding happens in `Final()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32.hh

Purpose: declares and partly implements the built-in CRC-32 checksum calculator.

Important APIs: `Init()` resets `C32Result` and `TotLen`. `Update()` is implemented in the `.cc`. `Final()` appends the encoded total length to the CRC calculation, xors with `CRC32_XOROT`, converts to network order on little-endian platforms, and returns a pointer to `TheResult`. `Type()` returns `"crc32"` and 4-byte size.

Control flow and integration: designed for incremental manager-driven updates. `New()` creates a fresh calculator for loader/manager use.

State and persistence: stores the static table, current CRC, final result, and total bytes processed. Persistent representation is only the final binary checksum.

Dependencies: includes `XrdCksCalc.hh`, platform/endian support, and byte-order headers.

Risks and test signals: test vectors must account for XRootD's length-finalization behavior rather than generic reflected CRC-32. Tests should verify endian output and repeated reuse after `Init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32C.cc -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32C.cc

Purpose: implements the CRC-32C checksum calculator using `XrdOucCRC::Calc32C`.

Important APIs: `Update()` feeds each buffer into `Calc32C` with the current CRC seed. `Type()` returns `"crc32c"` and 4-byte size. `New()`, `Init()`, `Final()`, constructor, and destructor provide the standard `XrdCksCalc` lifecycle.

Control flow: the calculator keeps an accumulated CRC in `C32CResult`; `Final()` returns it as `TheResult`, converted to network order on little-endian platforms.

State and persistence: transient calculator state only. Final bytes may be stored in `XrdCksData`.

Dependencies: includes `XrdCksCalccrc32C.hh`, which pulls in `XrdOucCRC`.

Risks and test signals: tests should compare known CRC-32C vectors, segmented versus one-shot updates, endian conversion, and object reuse. Because no length finalization is applied, vectors differ from `XrdCksCalccrc32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32C.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32C.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32C.hh

Purpose: declares the CRC-32C `XrdCksCalc` subclass.

Important APIs: declares `Final`, `Init`, `New`, `Update`, `Type`, constructor, and destructor. Private members are initial constant `C32C_XINIT`, current result, and final output word.

Control flow and integration: used as a built-in checksum calculator through the manager/loader stack, with the implementation delegating arithmetic to `XrdOucCRC::Calc32C`.

State and persistence: no persistent state beyond returned checksum bytes.

Dependencies: includes `XrdCksCalc.hh`, platform/endian headers, byte-order support, and `XrdOucCRC.hh`.

Risks and test signals: ABI and type-name tests should ensure `"crc32c"` is registered and reports the correct size. Algorithm tests should verify output byte order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32C.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcmd5.cc -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcmd5.cc

Purpose: implements the MD5 checksum calculator for XRootD using Colin Plumb's public-domain MD5 algorithm adapted into `XrdCksCalcmd5`.

Important APIs: `Init()` initializes the MD5 context constants and bit counters. `MD5Update()` accumulates bytes, processes complete 64-byte blocks, and buffers trailing data. `Final()` pads the message, appends bit length, transforms the final block, byte-reverses digest words as needed, and returns 16 digest bytes. `MD5Transform()` performs the four MD5 rounds through `MD5STEP` macros. `byteReverse()` is a no-op on little-endian and swaps words on big-endian.

Control flow: public `Update()` in the header calls `MD5Update()`. `Current()` saves and restores the context around `Final()` to inspect the digest without consuming state.

State and persistence: mutates `myContext` and `myDigest`. Persistent data is the final 16-byte checksum stored by manager/xattr code.

Dependencies: includes `XrdCksCalcmd5.hh` and platform endian support.

Risks and test signals: MD5 test vectors, segmented updates, `Current()` no-side-effect behavior, endian behavior, and repeated `Init()` reuse are key. Security-sensitive consumers should remember MD5 is not collision-resistant; here it is used as a legacy checksum, not authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcmd5.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcmd5.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcmd5.hh

Purpose: declares the MD5 `XrdCksCalc` subclass and its internal context.

Important APIs and types: public methods are `Current`, `Init`, `New`, `Final`, `Update`, and `Type`. `Type()` returns `"md5"` and a 16-byte size. Private `MD5Context` stores four state words, bit counters, and a 64-byte input block through unions; helper methods are `byteReverse`, `MD5Update`, and `MD5Transform`.

Control flow and integration: managers stream file data through `Update()`, then call `Final()` or `Current()`. `New()` supports calculator cloning.

State and persistence: mutable MD5 context and digest buffer are per instance. Final digest bytes may be serialized in `XrdCksData`.

Dependencies: includes `XrdCksCalc.hh` and `<cstdio>`.

Risks and test signals: tests should verify `Current()` preserves state, `Type()` reports correct length, and incremental hashing matches known MD5 vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcmd5.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalczcrc32.cc -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalczcrc32.cc

Purpose: implements a loadable zlib-compatible CRC32 calculator plugin named `zcrc32`.

Important APIs: class `XrdCksCalczcrc32 : public XrdCksCalc` implements `Init()` with `crc32(0L, Z_NULL, 0)`, `Update()` with zlib `crc32`, `Final()` returning the current `uint32_t`, `New()`, and `Type()` returning `"zcrc32"` with 4-byte size. The extern "C" `XrdCksCalcInit()` factory returns a new calculator, and `XrdVERSIONINFO` declares plugin version metadata.

Control flow and integration: built as a module by `XrdCks/CMakeLists.txt` and loaded by the checksum loader when configured. It provides zlib semantics separately from XRootD's built-in CRC32 algorithm.

State and persistence: `pCheckSum` is per-instance transient state. Final bytes may be stored by a checksum manager.

Dependencies: depends on zlib, `XrdCksCalc.hh`, `XrdSysError.hh`, and `XrdVersion.hh`.

Risks and test signals: plugin load tests should validate the factory symbol and version info. Algorithm tests should compare standard zlib CRC32 vectors, incremental updates, and byte-order expectations of consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalczcrc32.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksConfig.cc

Purpose: implements checksum manager configuration, including default manager creation, manager override loading, calculator library directive parsing, and stackable checksum plugins.

Important APIs: the constructor verifies version compatibility. `Configure()` obtains a manager with `getCks()`, stacks `XrdCksAdd2` plugins via `addCks()`, applies queued `ckslib` config lines, and calls `Init()`. `getCks()` returns `XrdCksManOss` when an OSS object is supplied, `XrdCksManager` otherwise, or loads a custom manager library with `XrdCksInit`. `Manager()` replaces custom manager path/parameters. `ParseLib()` parses `ckslib <digest> <path> [parms]`, with `*` for manager override, `=` for default manager selection, and `++` for stackable plugins. `ParseOpt()` accepts default manager option `nomtchk`.

Control flow: configuration directives are accumulated in linked lists, then consumed when `Configure()` creates the manager. Pin loaders intentionally keep shared libraries open while discarding loader objects.

State and persistence: stores config filename, custom manager path/parameters, digest config list, stackable library list, version info, and checksum manager options. No checksum values are persisted here.

Dependencies and integration: depends on `XrdCksManager`, `XrdCksManOss`, `XrdCksWrapper`, `XrdOucPinLoader`, `XrdOucStream`, plugin version APIs, and XRootD utility lists.

Risks and test signals: directive parsing tests should cover missing digest/path, too-long fields, `default` restrictions, manager replacement, `++` stack order, invalid options, and plugin symbol failures. Memory ownership for `strdup` paths and linked lists should be leak-checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksConfig.hh

Purpose: declares `XrdCksConfig`, the object that parses and materializes checksum manager configuration.

Important APIs: public `Configure()`, `Manager()`, `ParseLib()`, and `ParseOpt()` create or configure checksum managers. `Manager()` also reports whether a custom manager path is set. Private helpers are `addCks()` and `getCks()`.

State and persistence: stores the config filename, manager library path and parameters, linked lists for checksum and stackable libraries, last-list pointers, plugin version info, and option flags. This state is runtime configuration only.

Dependencies and integration: includes `XrdOucTList.hh` and forward-declares `XrdCks`, `XrdOss`, `XrdOucEnv`, `XrdOucStream`, `XrdSysError`, and `XrdVersionInfo`.

Risks and test signals: API tests should verify constructor version acceptance/rejection, `Manager()` state transitions, and `Configure()` behavior with OSS-backed versus native managers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksData.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksData.hh

Purpose: defines `XrdCksData`, the fixed-size checksum record passed through manager APIs and serialized into xattrs.

Important APIs and fields: constants `NameSize` and `ValuSize` bound algorithm names and binary values. Fields store `Name`, unioned `fmTime`/`envP`, `csTime`, reserved bytes, `Length`, and `Value`. Operators compare name, length, and value. `Get()` renders the binary value as lowercase hex. `Set(const char*)` sets the algorithm name; `Set(const void*, int)` sets binary value; `Set(const char*, int)` parses hex text. `Reset()` clears the record and constructor calls it. `HasValue()` checks whether the value buffer begins with a nonzero byte.

Control flow and integration: manager calls use `Name` as input and fill `Value`/time fields as output. Assist helpers serialize the whole struct to xattrs, so layout compatibility matters.

State and persistence: the object is both in-memory API state and persistent xattr payload. The `fmTime`/`envP` union means the same storage has different meanings depending on operation direction.

Dependencies: includes `<cstring>` and forward-declares `XrdOucEnv`.

Risks and test signals: tests should cover max name/value lengths, invalid hex, odd-length hex rejection, zero-valued valid checksums versus `HasValue()`, struct-size compatibility, and comparison semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksData.hh -->
