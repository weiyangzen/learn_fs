# subset-b-007921 Research

Grouped research for the listed XRootD client file APIs. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClFile.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClFile.hh

## Purpose
`XrdClFile.hh` declares the public `XrdCl::File` facade used by clients to open and operate on XRootD files. It is the high-level, synchronous/asynchronous C++ API for single-file I/O, metadata, vector I/O, extended attributes, server control operations, checkpointed writes, server failover, and range cloning. The header intentionally hides transport/session machinery behind the private `FileImpl` pointer and optional `FilePlugIn`, so consumers interact with stable `XRootDStatus`, `ResponseHandler`, and response-object contracts rather than the internal state machine.

## Important APIs, Types, And Functions
The main type is `XrdCl::File`, with constructors for default plugin-enabled files, virtual-redirector selection through `VirtRedirect`, and plugin initialization from an initial URL. `Open` has async and sync overloads. `OpenUsingTemplate` accepts a reference `File` and is required for `OpenFlags::Dup` or `OpenFlags::Samefs`; the implementation rejects those flags on plain `Open`. `Close`, `Stat`, `Read`, `PgRead`, `Write`, `PgWrite`, `Sync`, `Truncate`, `PreRead`, `VectorRead`, `VectorWrite`, `WriteV`, `ReadV`, `Fcntl`, `Visa`, xattr operations, and `TryOtherServer` make up the public operation surface.

The response contracts are explicit in the declarations. Async `Stat` returns `StatInfo`, `Read` returns `ChunkInfo`, `PgRead` returns `PageInfo`, `VectorRead` and `ReadV` return `VectorReadInfo`, `Fcntl` and `Visa` return `Buffer`, xattr bulk calls return `std::vector<XAttr>` or `std::vector<XAttrStatus>`, and status-only operations return no response object. Sync overloads translate these responses into output parameters such as `bytesRead`, `cksums`, `VectorReadInfo *&`, or result vectors. Ownership is caller-visible: several sync response pointers are documented as user-deleted, while buffer-taking write overloads with `Buffer &&` transfer ownership into the XrdCl runtime.

`ExportedFileTemplate`, `CloneLocation`, and `CloneLocations` provide the template mechanism for clone/open affinity. `CloneLocations::Add` stores a `unique_ptr<ExportedFileTemplate>` produced by the private `File::GetFileTemplate`, plus source offset, source length, and destination offset. `CloneLocations` is declared as a friend so it can capture source-file state without exposing the template extraction method publicly.

## Control Flow
The header declares an async-first API. Async overloads accept a `ResponseHandler *` and timeout, returning an immediate `XRootDStatus` for submission/validation failures. Sync overloads are implemented in `XrdClFile.cc` by creating a `SyncResponseHandler`, calling the async overload, and waiting with `MessageUtils::WaitForStatus` or `WaitForResponse`. This means many failures can surface before blocking begins, while protocol responses arrive through the handler path.

At runtime, operations choose between two execution paths. If plugin support is enabled and a `FilePlugIn` exists for the URL, the operation delegates to the plugin. Otherwise, it delegates to `FileStateHandler` through `FileImpl::pStateHandler`. The implementation initializes plugins lazily in `Open`/`OpenUsingTemplate` and in the URL constructor, using `DefaultEnv::GetPlugInManager()->GetFactory(url)`.

Most calls are thin dispatchers. Notable branch points include `Open` refusing `Dup`/`Samefs` without a template, destructor-triggered close when the postmaster is still running and the file is open, `Close` returning immediately on `suAlreadyDone`, `PreRead` currently returning a default OK status in the non-plugin path with the `FileStateHandler::PreRead` call disabled, and xattr/checkpoint operations returning `errNotSupported` when a plugin is active.

## State And Persistence Behavior
`File` owns `FileImpl *pImpl`, `FilePlugIn *pPlugIn`, and `bool pEnablePlugIns`. `FileImpl` owns a `std::shared_ptr<FileStateHandler>`, which carries open state, connection state, redirect state, protocol handles, cached stat information, and recovery settings outside this header. `IsOpen`, `IsSecure`, `SetProperty`, and `GetProperty` expose selected state. Supported mutable properties are `ReadRecovery`, `WriteRecovery`, `FollowRedirects`, and `BundledClose`; read-only properties include `DataServer` and `LastURL`.

File data and metadata persistence happen on the remote server. `Write`, `PgWrite`, `VectorWrite`, `WriteV`, checkpointed write calls, `Truncate`, `Sync`, and xattr calls mutate remote state. `Sync` commits pending disk writes server-side. `Read`, `PgRead`, `VectorRead`, `ReadV`, `Stat`, `Fcntl`, `Visa`, and property getters are read/control paths, though custom `Fcntl` behavior is server-dependent. The destructor attempts to close an open file only while logging and postmaster infrastructure are still usable, avoiding shutdown hangs in environments such as ROOT or Python finalization.

## Dependencies And Integration Points
This header depends on `XrdClFileSystem.hh` for file-system API types such as `OpenFlags`, `Access`, `QueryCode`, `ChunkList`, `TractList`, xattr types, and response declarations; `XrdClXRootDResponses.hh` for protocol response objects; `XrdClOptional.hh` for optional file-descriptor offsets; `XrdOucCompiler.hh` for warning attributes; and `<sys/uio.h>` for scatter/gather I/O. The implementation integrates with `XrdClFileStateHandler`, `XrdClPlugInInterface`, `XrdClPlugInManager`, `DefaultEnv`, `MessageUtils`, and `SyncResponseHandler`.

Higher-level XrdCl components consume this API directly. Copy and third-party-copy code creates `File` objects, often with `DisableVirtRedirect`, to manage data-server access. `XrdClFileOperations.hh` wraps these methods into pipelineable operation objects. `XrdClFileStateHandler.hh` provides the concrete state machine and exports `FileStateHandlerTemplate` through `ExportedFileTemplate` for template-based open and clone workflows.

## Risks And Edge Cases
The API is pointer-heavy. Async callers must keep buffers, iovec arrays, handlers, and referenced files alive until callbacks complete. `CloneLocations::Add` captures a source template, but the comments still require the source file to remain open until after `Clone()`. Sync callers receiving raw response pointers must delete them as documented.

Plugin and non-plugin behavior is intentionally not identical. `IsSecure` returns false for plugins, xattr and checkpoint operations are not supported through plugins in the implementation, and plugin implementations may define custom semantics for normal file calls. The non-plugin `PreRead` path appears stubbed, returning a default status without issuing a state-handler request; tests should treat preread behavior as suspicious unless a plugin supplies it.

Timeouts are per-call and default to environment values when zero. Because sync calls are wrappers around async calls, a submission status that is OK does not mean the operation succeeded; the wait result must also be checked. Destructor-driven close is best-effort and depends on global environment lifetime, so explicit `Close` remains the reliable cleanup signal.

## Test Signals
Useful tests exercise both sync and async forms for open/close, read/write, stat cache force/non-force behavior, page reads and checksum propagation, vector read/write with separate and aggregate buffers, scatter/gather `ReadV`/`WriteV`, truncation and sync durability, xattr success and old-server/not-supported paths, `OpenUsingTemplate` with `Dup`/`Samefs`, clone range validation, and `TryOtherServer` recovery. Integration tests should cover plugin-enabled and plugin-disabled files, virtual redirect enabled/disabled construction, timeout propagation, and callbacks receiving the documented response type. Regression tests should specifically lock down `PreRead` non-plugin behavior and destructor shutdown behavior where the postmaster is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClFileOperations.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileOperations.hh

## Purpose
`XrdClFileOperations.hh` adapts the `XrdCl::File` facade into the XrdCl operation/pipeline framework. It provides small CRTP operation classes and factory functions so file operations can be composed with the workflow operators implemented in `XrdClOperations.hh`, streamed into handlers with `operator>>`, run asynchronously, and chained with common timeout handling. The file is a header-only bridge between user-friendly file pipeline syntax and the concrete async methods in `File`.

## Important APIs, Types, And Functions
`FileOperation<Derived, HasHndl, Response, Arguments...>` is the shared base. It derives from `ConcreteOperation`, stores `Ctx<File> file`, forwards argument wrappers to the concrete operation base, and provides a move constructor that converts between handled and unhandled operation states. The `Ctx<File>` wrapper keeps the target file object accessible across pipeline movement.

The header defines operation implementations for `Open`, `Read`, `PgRead`, `PgWrite`, `Close`, `Stat`, `Write`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `Fcntl`, `Visa`, and extended attributes. Each implementation defines argument indexes, `ToString()`, and a protected `RunImpl(PipelineHandler *, time_t)` that extracts `Arg<T>` values from `this->args`, computes the effective timeout, and delegates to the matching async `File` method.

Factory functions return unhandled operations, typically with `.Timeout(timeout)` applied: `Open`, `Read`, `PgRead`, `RdWithRsp<ChunkInfo/PageInfo>`, `PgWrite`, `Close`, `Stat`, `Write`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, and `WriteV`. `Fcntl` and `Visa` are exposed as typedefs to their unhandled implementation types. Xattr factories overload `SetXAttr`, `GetXAttr`, and `DelXAttr` for single-name and bulk vector forms, and `ListXAttr` creates the list operation.

`OpenImpl` has an extended response factory, `ExResp`, that adds handler creation for `std::function<void(XRootDStatus&, StatInfo&)>` while retaining the base `Resp<void>` overloads. It wraps such callbacks in `ExOpenFuncWrapper`, allowing open pipelines to observe the opened file's stat information. Single-xattr operations use `UnpackXAttrStatus` and `UnpackXAttr` from `XrdClOperationHandlers.hh` to convert vector/bulk file responses into scalar pipeline responses.

## Control Flow
A typical operation is built by a factory, optionally gets a timeout, then is converted to a handled operation by `operator>>` or another pipeline composition primitive. When the workflow engine runs it, `ConcreteOperation` calls the operation's `RunImpl`. `RunImpl` extracts stable values from the stored tuple and invokes the corresponding async `File` call with the pipeline handler. The pipeline handler receives the eventual XRootD callback and advances the workflow or completes the final promise.

Timeout control is consistent throughout the file: `RunImpl` sets `timeout` to the smaller of `pipelineTimeout` and the operation timeout. That embeds operation-level deadlines under an outer pipeline budget. Operations that return data use response template types such as `Resp<ChunkInfo>`, `Resp<PageInfo>`, `Resp<VectorReadInfo>`, `Resp<Buffer>`, `Resp<std::vector<XAttr>>`, or `Resp<std::vector<XAttrStatus>>`; status-only operations use `Resp<void>`.

The xattr single-item flow is slightly more involved. `SetXAttrImpl` wraps a name/value pair in a `std::vector<xattr_t>`, allocates `UnpackXAttrStatus`, and deletes the wrapper if submission fails. `GetXAttrImpl` wraps a single name in a vector, allocates `UnpackXAttr`, and deletes it on immediate failure. `DelXAttrImpl` follows the same pattern as set. Bulk xattr operations pass the vectors directly and return bulk response types.

## State And Persistence Behavior
Operation objects are transient and once-use-only by inheritance from `Operation`. They persist only enough state to run: a `Ctx<File>`, a tuple of `Arg<T>` values, an optional timeout, and, after handler binding, a pipeline handler. Moving an operation invalidates the source operation in the base framework. No file data is stored in this layer; all durable effects happen through the underlying `File` methods.

The operation layer does affect lifetime expectations. Buffer and argument wrappers must remain valid according to how `Arg<T>` stores them, and `Ctx<File>` must refer to a usable file. `WriteVImpl` copies a `std::vector<iovec>` into a stack array before invoking `File::WriteV`; the underlying async write must not depend on that stack array after the call unless the deeper `FileStateHandler` copies it immediately. Xattr unpack wrappers allocate helper handlers and hand ownership to the async response path on successful submission.

## Dependencies And Integration Points
This header includes `XrdClFile.hh`, `XrdClOperations.hh`, `XrdClOperationHandlers.hh`, and `XrdClCtx.hh`. It depends on the operation framework for `Operation`, `ConcreteOperation`, `PipelineHandler`, `Resp`, `Arg`, timeout propagation, move-only operation validity, and stream/pipeline composition. It depends on `File` for the actual network/protocol work and on response wrapper helpers for scalar xattr callback adaptation.

It is the pipeline counterpart of the public `File` API. Any signature mismatch with `XrdClFile.hh` or behavior change in `File` propagates here. `RdWithRsp` integrates page and chunk reads through a response-type trait, allowing generic code to select `ReadImpl` or `PgReadImpl` by expected response type. Name clashes with filesystem operations are handled by comments and specific factory names, while operation `ToString()` values are used for workflow diagnostics.

## Risks And Edge Cases
The effective timeout expression uses `pipelineTimeout < this->timeout ? pipelineTimeout : this->timeout`; if either value can be zero to mean "default/no explicit timeout", this min operation may accidentally choose zero instead of a nonzero bound, depending on framework semantics. That should be verified against `XrdClOperationTimeout.hh`.

`WriteVImpl` uses a variable-length stack array `iovec iov[iovcnt]`, which is not standard C++ and can be risky for empty or very large vectors. It also passes a stack-backed array into an async API. This is only safe if the callee copies synchronously before returning. `PgWriteImpl` uses `Arg<void*>` while `File::PgWrite` expects `const void *`; the implicit conversion is fine for non-const buffers but weakens const-correctness at the pipeline API. Several `ToString()` methods return implementation names such as `SetXAttrImpl`, which may be less stable for user-facing diagnostics than operation names.

Single-xattr unpack handlers assume response shapes produced by bulk xattr file calls. Old servers may return non-OK statuses or no response, and the wrappers must avoid leaks and null dereferences. Handler ownership is subtle: helpers are deleted only on immediate submission failure; on success the callback path must eventually delete or own them according to pipeline conventions.

## Test Signals
Tests should construct each factory and verify `ToString`, argument forwarding, timeout propagation, and handler response type. Pipeline tests should cover normal chaining, `operator>>` conversion from unhandled to handled operations, moving operations once, and rejection of using moved-from operations via the base framework. File-level integration tests should assert that each `RunImpl` invokes the expected async `File` method with the extracted arguments.

Specific regression tests should cover `OpenImpl` custom callback overloads, `RdWithRsp<ChunkInfo>` versus `RdWithRsp<PageInfo>`, single and bulk xattr success/error paths, deletion of unpack wrappers on immediate failure, zero and nonzero pipeline/operation timeout combinations, empty and large `WriteV` vectors, and async safety of iovec lifetimes. Compile tests should run under strict standard C++ flags to catch the variable-length array and constness issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClFileOperations.hh -->
