# subset-b-000476 research

Grouped research report for the requested Alluxio file master context, metadata sync, and inode metadata files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreateFileContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreateFileContext.java

Purpose: wraps `CreateFilePOptions` for file creation in the master, adding master-only runtime state that is not represented directly in the protobuf. It extends `CreatePathContext`, so it inherits owner/group, ACL, TTL, write type, metadata-load, fingerprint, xattr, mount-point, and operation-time behavior.

Important APIs and types: static factories `create`, `mergeFrom`, `mergeFromDefault`, and `defaults` construct contexts from raw, default-merged, or already-defaulted file options. The nested `CompleteFileInfo` carries container id, final length, and block ids for metadata sync paths that create an already-complete file. `setCacheable`, `isCacheable`, `setCompleteFileInfo`, and `getCompleteFileInfo` expose the extra state.

Control flow: normal RPC paths call `mergeFrom` to merge user options over `FileSystemOptionsUtils.createFileDefaults`; metadata sync can use `mergeFromDefault` with a known defaults object and then mutate fields such as block size, write type, fingerprint, owner, group, and xattrs. `getOperationId` reads the common options operation id before falling back to the base context.

State and persistence behavior: the class itself is transient and not journaled, but its values drive journaled inode creation through file-master internals. `CompleteFileInfo` is a critical persistence signal because it lets metadata sync create completed file metadata with specific container and block identity rather than an open file placeholder.

Dependencies and integration points: depends on gRPC option builders, global configuration defaults, `FileSystemOptionsUtils`, `OperationId`, and the `CreatePathContext` extraction logic. It is consumed by `DefaultFileSystemMaster` creation paths and by `DefaultSyncProcess.createInodeFileMetadata`.

Risks: mutable protobuf builders and mutable context fields are not thread-safe. `mCompleteFileInfo` is nullable but returned without `Optional`, so callers must handle absence. `mergeFromDefault` assumes its input already represents the desired defaults and intentionally skips the normal master-default merge.

Test signals: useful tests should cover default merging, operation-id propagation, cacheable and complete-file metadata sync creation, and behavior when no complete info is supplied. Existing broader metadata-sync and create-file tests are the likely behavioral signal rather than this wrapper having isolated tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreateFileContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreatePathContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreatePathContext.java

Purpose: provides the shared master-side context for creating files and directories. It wraps either `CreateFilePOptions.Builder` or `CreateDirectoryPOptions.Builder` and carries derived fields plus internal-only state needed by `InodeTree.createPath` and file master create operations.

Important APIs and types: generic type parameters bind the protobuf builder type and fluent subtype. Getters extract mode, recursive flag, TTL, TTL action, persisted state, write type, xattrs, xattr propagation, owner, group, ACL, fingerprints, mount-point flag, operation time, metadata-load flag, and parent-directory persistence policy. Setters mutate runtime context state while extracted fields are reloaded from the protobuf builder to keep consistency.

Control flow: the constructor initializes owner/group from authenticated gRPC client configuration when authentication is enabled, converts protobuf write type to `WriteType`, and converts xattr byte strings. `loadExtractedFields` branches on file versus directory builders to pull mode, recursive, TTL, and TTL action from the current builder. `setMetadataLoad` enforces that parent directory persistence may only be disabled during metadata load.

State and persistence behavior: the context is transient, but it determines journaled inode attributes. The operation timestamp becomes inode creation or modification time; `mFingerprint` and `mMissingDirFingerprint` carry UFS fingerprints; write type controls persisted state; and xattrs flow into inode metadata. The missing-directory fingerprint supplier allows lazily computing parent fingerprints during recursive metadata-load creation.

Dependencies and integration points: integrates protobuf create options, `WriteType`, `Mode`, `TtlAction`, `XAttrPropagationStrategy`, authentication/security utilities, and Alluxio constants. `CreateFileContext` and `CreateDirectoryContext` subclass it, and metadata sync relies on its metadata-load, write-through, fingerprint, and xattr hooks.

Risks: fields are mutable and the class is explicitly built on mutable protobuf builders, so sharing across threads would be unsafe. Derived fields are reloaded from protobuf on access, but write type and xattrs are separately mutable context fields, so callers must keep builder and context choices coherent. Incorrect metadata-load flags can cause undesired UFS parent creation or stale fingerprint state.

Test signals: tests should exercise file and directory builders, default owner/group initialization, metadata-load invariant enforcement, TTL/mode extraction after builder mutation, xattr propagation, and parent persistence behavior during metadata sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreatePathContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/DeleteContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/DeleteContext.java

Purpose: wraps `DeletePOptions` for file-master delete operations and adds internal metadata-sync flags. It standardizes construction of delete contexts from raw builders, default master options, or default settings.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct instances. `setMetadataLoad` marks deletes caused by metadata load or sync. `skipNotPersisted` and `isSkipNotPersisted` control whether non-completed or non-persisted files are ignored during recursive sync deletes. `getOperationId` extracts common-option operation ids.

Control flow: `mergeFrom` obtains master delete defaults from `FileSystemOptionsUtils.deleteDefaults(Configuration.global(), false)` and merges user options over them. Metadata sync builds recursive, alluxio-only, unchecked delete options, then sets metadata-load and optional skip-not-persisted behavior before calling `DefaultFileSystemMaster.deleteInternal`.

State and persistence behavior: this class is not persisted itself, but it directly governs whether inode deletion journals are emitted and whether UFS deletion is bypassed. The metadata-load flag lets downstream code distinguish authoritative UFS-driven metadata reconciliation from user deletes.

Dependencies and integration points: depends on `DeletePOptions`, configuration defaults, and `OperationId`. It integrates with `DefaultSyncProcess.deletePath` and standard file-system master delete RPC handling.

Risks: `skipNotPersisted` is a subtle data-preservation flag; using it outside metadata sync could leave unexpected inode state. Because options and flags are mutable, callers should not reuse a context across independent delete requests.

Test signals: high-value tests include recursive metadata-sync deletes, skipped non-persisted files, alluxio-only behavior, operation-id propagation, and default merge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/DeleteContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ExistsContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ExistsContext.java

Purpose: wraps `ExistsPOptions` for master exists checks. It is a thin `OperationContext` specialization that ensures exists calls use configured master defaults.

Important APIs and types: `create` wraps a builder directly, `mergeFrom` merges a caller builder into `FileSystemOptionsUtils.existsDefaults`, and `defaults` creates a default context. The only behavior beyond the base class is diagnostic `toString`.

Control flow: RPC handling can accept user options, call `mergeFrom`, and pass the context through file-master path resolution. The base `OperationContext` can still carry cancellation trackers even though exists has no operation id override here.

State and persistence behavior: no persistent state is owned. Options may influence metadata sync or load behavior for exists depending on the fields in `ExistsPOptions`, but this wrapper does not add state.

Dependencies and integration points: depends on global configuration and file-system option utility defaults. It integrates with the master exists RPC and any call-tracking added through `OperationContext.withTracker`.

Risks: because it is a mutable builder wrapper, later builder mutation affects the context. Tests should detect if future `ExistsPOptions` fields need explicit context-side handling.

Test signals: default merging, string rendering, and behavior of exists calls with sync-related common options are the useful coverage points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ExistsContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/FreeContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/FreeContext.java

Purpose: wraps `FreePOptions` for master free operations, which evict file blocks from Alluxio storage without necessarily deleting namespace metadata.

Important APIs and types: `create`, `mergeFrom`, and `defaults` follow the common context pattern. `mergeFrom` uses `FileSystemOptionsUtils.freeDefaults(Configuration.global())`, and `toString` records the built protobuf options.

Control flow: the master free RPC can construct this context from user options and pass it to internal free logic. No extra state is introduced beyond the protobuf builder and base cancellation trackers.

State and persistence behavior: the context itself is transient. Its protobuf options govern recursive behavior, forced operation semantics, and any fields defined in `FreePOptions`; actual persistence effects occur in file-master block metadata updates and worker commands outside this wrapper.

Dependencies and integration points: depends on gRPC free options, global configuration defaults, and `OperationContext`. It integrates with file-master free paths and can carry call cancellation tracking.

Risks: this class is intentionally thin, so any future free-specific internal flag must be added deliberately. Mutable builder sharing remains a general risk.

Test signals: coverage should focus on default option merging and master free behavior under recursive or forced options rather than isolated wrapper logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/FreeContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/GetStatusContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/GetStatusContext.java

Purpose: wraps `GetStatusPOptions` for retrieving file or directory status from the master. It gives get-status calls the same option-merging and cancellation-tracking pattern as other file RPC contexts.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct the wrapper. `mergeFrom` uses `FileSystemOptionsUtils.getStatusDefaults(Configuration.global())`. `toString` includes the built options for debugging.

Control flow: callers merge request options over master defaults and pass the context through status resolution. Unlike create/delete/rename, it does not override `getOperationId`, so operation ids are not extracted here unless the base class changes.

State and persistence behavior: no direct persistence. Options may influence whether status retrieval triggers metadata loading or sync, but persisted inode and UFS state are handled downstream.

Dependencies and integration points: depends on `GetStatusPOptions`, configuration, option defaults, and base `OperationContext`. It integrates with the master get-status RPC and internal status paths.

Risks: thin wrappers can hide option semantics in downstream code; future status fields that need derived context state would require explicit additions. The mutable options builder must not be reused unsafely.

Test signals: default merging, status with metadata-sync common options, cancellation tracking, and debug rendering are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/GetStatusContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/GrpcCallTracker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/GrpcCallTracker.java

Purpose: adapts a server-side gRPC stream observer to Alluxio's `CallTracker` abstraction so long-running master operations can observe client cancellation.

Important APIs and types: the constructor accepts a `StreamObserver<?>` but requires it to be a `ServerCallStreamObserver<?>`. `isCancelled` delegates to the gRPC observer, and `getType` returns `Type.GRPC_CLIENT_TRACKER`.

Control flow: request handlers attach this tracker to an `OperationContext`; later code calls `getCancelledTrackers` on the context to determine whether work should stop. Construction fails fast with `IllegalStateException` for unsupported observer types.

State and persistence behavior: no persisted state. The only state is the observer reference, which reflects live RPC cancellation status.

Dependencies and integration points: depends on gRPC server stream observer APIs and the local `CallTracker` interface. It integrates with `OperationContext.withTracker`.

Risks: only server stream observers are supported, so unary or client-side observers passed accidentally will fail. The field is mutable only by constructor today, but not final, leaving room for accidental reassignment in future edits.

Test signals: tests should cover accepted server observers, rejection of generic observers, and cancellation status flowing through `OperationContext.getCancelledTrackers`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/GrpcCallTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/InternalOperationContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/InternalOperationContext.java

Purpose: provides an `OperationContext` for non-RPC internal master work, especially paths that need call-tracking or operation-context plumbing without a user protobuf options builder.

Important APIs and types: the constructor calls `super(null)` with `FileSystemMasterCommonPOptions.Builder` as the generic type. It exposes no additional methods and inherits tracker management from `OperationContext`.

Control flow: internal code creates this context when building an `RpcContext` for background or system operations. `DefaultSyncProcess.performSync` uses it when creating a non-merging journal RPC context for metadata sync processing.

State and persistence behavior: the context is transient and has no protobuf options. Persisted effects depend on the `RpcContext` and journal context built around it.

Dependencies and integration points: depends on `FileSystemMasterCommonPOptions` only for generic compatibility. It integrates with `DefaultFileSystemMaster.createNonMergingJournalRpcContext`, `SyncProcessContext`, and call trackers for non-RPC requests.

Risks: `getOptions()` returns null for this context, so generic code that assumes every context has a builder will fail. It should only be used where option access is unnecessary or guarded.

Test signals: tests should cover metadata sync journal context creation and any generic operation code paths that accept null options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/InternalOperationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ListStatusContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ListStatusContext.java

Purpose: wraps `ListStatusPOptions` and partial-listing options while tracking progress through a list-status call. It supports full listings, partial pagination, explicit metadata-sync disabling for tests, and per-call listing counters.

Important APIs and types: `create` and `mergeFrom` are overloaded for `ListStatusPOptions.Builder` and `ListStatusPartialPOptions.Builder`. `getPartialOptions`, `listedItem`, `isDoneListing`, `isPartialListing`, `donePartialListing`, `isTruncated`, `setTotalListings`, and `getTotalListings` expose pagination state. `disableMetadataSync` is visible for testing.

Control flow: partial-listing construction wraps the embedded full `options` from the partial builder while retaining the partial builder separately. Each listed candidate calls `listedItem`, which increments processed count, skips until `offsetCount`, increments listed count for emitted items, and marks truncation/done when listed count exceeds `batchSize`.

State and persistence behavior: no persistence, but its counters and flags determine response shape and whether traversal can stop early. `disableMetadataSync` mutates the underlying options to `LoadMetadataPType.NEVER` and sync interval `-1`.

Dependencies and integration points: depends on list status protobufs, `FileSystemMasterCommonPOptions`, `LoadMetadataPType`, configuration defaults, and `OperationContext`. It integrates with master listing traversal, partial listing RPCs, and metadata-sync policy checks.

Risks: the batch-size check uses `< mListedCount`, so the item that crosses the limit is not listed and truncation is set after incrementing. Misunderstanding offset versus listed counters can cause off-by-one pagination bugs. `disableMetadataSync` is test-visible and mutates options in a way that production code should avoid unless intentional.

Test signals: strong tests should cover offset-only, batch-only, offset-plus-batch, start-after partial listings, recursive total listing count, truncation flags, and disabled metadata sync option mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ListStatusContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/LoadMetadataContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/LoadMetadataContext.java

Purpose: wraps `LoadMetadataPOptions` for explicit metadata loading from UFS into Alluxio namespace and optionally carries a pre-fetched `UfsStatus`.

Important APIs and types: `create`, `mergeFrom`, and `defaults` handle construction. `getUfsStatus` and `setUfsStatus` attach UFS status information to the context.

Control flow: load-metadata callers merge request options over `FileSystemOptionsUtils.loadMetadataDefaults`, optionally set a `UfsStatus`, and pass the context into master metadata loading logic. The context's `toString` includes both proto options and UFS status for diagnostics.

State and persistence behavior: the context is transient, but the attached `UfsStatus` can become source data for persisted inode metadata such as file or directory type, owner, group, mode, length, and fingerprint.

Dependencies and integration points: depends on `LoadMetadataPOptions`, UFS status types, configuration defaults, and `OperationContext`. It integrates with file-master load-metadata paths and overlaps conceptually with metadata sync context classes.

Risks: `mUfsStatus` is nullable; callers that expect preloaded status must check. Stale UFS status attached to a context can lead to incorrect metadata if reused after UFS changes.

Test signals: tests should cover default merging, status propagation, null status behavior, and metadata-load creation from status for both files and directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/LoadMetadataContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/MountContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/MountContext.java

Purpose: wraps `MountPOptions` for mount operations and attaches a `Recorder` for tracing the execution process.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct contexts. `getRecorder` exposes the per-context `Recorder`.

Control flow: the private constructor creates a new recorder for every mount context. `mergeFrom` merges caller options over `FileSystemOptionsUtils.mountDefaults(Configuration.global())`. Mount implementation code can record steps and failures through the recorder while using the merged options.

State and persistence behavior: the recorder is transient diagnostic state. Mount options influence persistent mount table updates and journals elsewhere, but this wrapper does not persist anything directly.

Dependencies and integration points: depends on mount protobuf options, configuration defaults, `Recorder`, and `OperationContext`. It integrates with file master mount RPC handling and mount-table mutation code.

Risks: the recorder can accumulate execution detail for a long mount operation; callers should avoid retaining contexts longer than needed. New mount-specific internal flags should be added here rather than hidden in ad hoc parameters.

Test signals: tests should cover option merging, recorder availability, and mount failure reporting through the recorder in higher-level mount tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/MountContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/OperationContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/OperationContext.java

Purpose: base class for master operation contexts that wrap mutable protobuf builders and carry call-cancellation trackers. It gives all specialized contexts a common `getOptions`, `withTracker`, `getOperationId`, and cancellation query API.

Important APIs and types: generic parameters bind the protobuf builder type and fluent context subtype. `getOptions` returns the wrapped builder, `withTracker` appends a `CallTracker`, `getOperationId` defaults to null, and `getCancelledTrackers` returns only trackers currently reporting cancellation.

Control flow: operation-specific contexts call the constructor with their options builder. RPC handlers add call trackers as needed. Long-running code calls `getCancelledTrackers`; the method first performs a cheap scan for any cancelled tracker, then builds and returns the cancelled subset only when needed.

State and persistence behavior: no persistent state. The mutable options builder drives downstream persistent operations, and cancellation state can stop work before additional journaled changes are made.

Dependencies and integration points: depends on protobuf builders and Alluxio `OperationId`. It is the base for file master contexts and is used by `RpcContext` plumbing.

Risks: annotated `@NotThreadSafe`; both options and tracker list are mutable. Raw generic casts in `withTracker` rely on subclasses using the intended self type. Contexts such as `InternalOperationContext` may pass null options, so generic callers must be defensive.

Test signals: tests should cover cancellation aggregation, empty cancellation fast path, subtype fluent return behavior, and operation-id overrides in specialized contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/OperationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/RenameContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/RenameContext.java

Purpose: wraps `RenamePOptions` for master rename operations and records internal operation time plus whether persistence should follow the rename.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct contexts. `getOperationTimeMs`, `setOperationTimeMs`, `getPersist`, and `getOperationId` expose rename-specific state.

Control flow: construction captures current time and `optionsBuilder.getPersist()`. `mergeFrom` merges caller options over `FileSystemOptionsUtils.renameDefaults(Configuration.global(), false)`. Downstream rename code uses operation time for inode modification timestamps and `getPersist` to determine follow-up persistence behavior.

State and persistence behavior: transient context state influences journaled rename metadata. Operation time can become last modification time, and `mPersist` controls whether renamed content should be persisted to UFS after namespace mutation.

Dependencies and integration points: depends on rename protobufs, configuration defaults, and `OperationId`. It integrates with `DefaultFileSystemMaster` rename internals and operation-id tracking.

Risks: `mPersist` is captured at construction and will not reflect later direct mutations to the options builder. Tests should catch this if builders are mutated after context creation.

Test signals: default merging, persist flag capture, operation-time override, operation-id extraction, and rename timestamp behavior are the important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/RenameContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ScheduleAsyncPersistenceContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ScheduleAsyncPersistenceContext.java

Purpose: wraps `ScheduleAsyncPersistencePOptions` for scheduling asynchronous persistence of an Alluxio file to UFS.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct contexts. `getPersistenceWaitTime` exposes the wait time captured from the options builder.

Control flow: construction copies `optionsBuilder.getPersistenceWaitTime()` into `mPersistenceWaitTime`. `mergeFrom` merges request options over `FileSystemOptionsUtils.scheduleAsyncPersistenceDefaults`.

State and persistence behavior: the context itself is transient, but the wait time influences when persistence jobs should run. Actual persisted state changes occur in file metadata and persistence job tracking outside this wrapper.

Dependencies and integration points: depends on schedule-async-persistence protobufs, configuration defaults, and `OperationContext`. It integrates with file-master persistence scheduling.

Risks: like `RenameContext`, the derived wait time is captured at construction and can diverge if the builder is mutated later. The defaults comment references `LoadMetadataContext`, which is harmless but misleading documentation.

Test signals: tests should cover default merging, wait-time capture, scheduling behavior for non-default wait times, and no accidental divergence after builder mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ScheduleAsyncPersistenceContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SetAclContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SetAclContext.java

Purpose: wraps `SetAclPOptions` for ACL mutation requests in the file master.

Important APIs and types: `create`, `mergeFrom`, and `defaults` follow the standard operation-context pattern. No extra fields are added beyond the protobuf options builder and base cancellation trackers.

Control flow: request options are merged over `FileSystemOptionsUtils.setAclDefaults(Configuration.global())` and passed to ACL mutation internals. Diagnostic `toString` renders the built protobuf options.

State and persistence behavior: no direct persistence in this class, but the options determine journaled ACL updates to inode metadata downstream.

Dependencies and integration points: depends on ACL protobuf options, configuration defaults, and `OperationContext`. It integrates with `DefaultFileSystemMaster` set-ACL paths and inode ACL structures.

Risks: thin wrapper; future ACL-specific internal state such as metadata-load or audit controls would need explicit additions. Mutable builder reuse remains unsafe.

Test signals: default merging, recursive ACL behavior, action-specific ACL mutations, and cancellation handling are the main coverage points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SetAclContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SetAttributeContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SetAttributeContext.java

Purpose: wraps `SetAttributePOptions` and adds operation time, UFS fingerprint, and metadata-load flag for attribute updates. It is used both for user attribute updates and UFS-driven metadata reconciliation.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct contexts. `getOperationTimeMs`, `setOperationTimeMs`, `setMetadataLoad`, `isMetadataLoad`, `getUfsFingerprint`, and `setUfsFingerprint` expose additional state.

Control flow: construction records current time and initializes fingerprint to `Constants.INVALID_UFS_FINGERPRINT`. Metadata sync builds set-attribute options from UFS mode/owner/group and attaches a serialized fingerprint before calling `setAttributeSingleFile`.

State and persistence behavior: context values can be journaled into inode metadata: operation time may become modification time, and UFS fingerprint becomes the inode fingerprint used for future sync comparisons. Metadata-load marks reconciliation-originated updates.

Dependencies and integration points: depends on set-attribute protobufs, configuration defaults, Alluxio constants, and `OperationContext`. It integrates closely with `DefaultSyncProcess.updateInodeMetadata`.

Risks: a likely bug exists in `DefaultSyncProcess.updateInodeMetadata`, which calls `builder.setOwner(ufsStatus.getGroup())` instead of setting group; this context will faithfully carry whatever builder fields it receives. Fingerprint defaults to invalid, so callers must set it for UFS sync correctness.

Test signals: tests should cover metadata-sync attribute updates, fingerprint persistence, operation-time override, owner/group update behavior, and default invalid fingerprint behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SetAttributeContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SyncMetadataContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SyncMetadataContext.java

Purpose: wraps `SyncMetadataPOptions` for explicit metadata sync requests. It is a thin context used to merge request options with master sync defaults.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct contexts using `FileSystemOptionsUtils.syncMetadataDefaults`. `toString` renders the built protobuf options.

Control flow: RPC handling builds the context, then higher-level metadata-sync code chooses descendant type, directory load type, sync interval, and async behavior from the options. This wrapper does not own task orchestration; that happens in the `mdsync` package.

State and persistence behavior: no direct persistence. Options drive the background task group that may create, update, or delete inode metadata through `DefaultSyncProcess`.

Dependencies and integration points: depends on sync metadata protobufs, configuration, file-system option utilities, and `OperationContext`. It is a front door into `DefaultSyncProcess.syncPath`.

Risks: the Javadoc still references `ExistsPOptions` in `mergeFrom`, which is documentation drift. Any new sync-specific runtime flags need to be added here or in the mdsync task classes.

Test signals: default merging, sync metadata RPC option handling, and end-to-end sync task launch are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SyncMetadataContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/WorkerHeartbeatContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/WorkerHeartbeatContext.java

Purpose: wraps `FileSystemHeartbeatPOptions` for worker heartbeat handling in the file master.

Important APIs and types: `create` wraps a provided heartbeat options builder, and `defaults` creates a new builder through a private no-arg constructor. The context inherits cancellation tracking from `OperationContext`.

Control flow: worker heartbeat handling builds a context and passes it through file-system master heartbeat internals. There is no default merge utility here; `defaults` simply uses `FileSystemHeartbeatPOptions.newBuilder()`.

State and persistence behavior: this wrapper is transient. Heartbeat options may drive persisted or in-memory file block state changes elsewhere, but this class owns none of that behavior.

Dependencies and integration points: depends on heartbeat protobuf options and `OperationContext`. It integrates with worker-to-master heartbeat paths.

Risks: no explicit defaults are merged, so default behavior is whatever the protobuf builder provides. Future heartbeat options requiring configuration defaults would need changes here.

Test signals: heartbeat context creation, option propagation, default empty options, and debug rendering are adequate wrapper-level tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/WorkerHeartbeatContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BaseTask.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BaseTask.java

Purpose: abstract base for a metadata sync task. It combines task identity and stats, UFS path loading through `PathLoaderTask`, wait-for-path semantics through `PathWaiter`, task state transitions, cancellation, completion notification, and final direct-children-loaded updates.

Important APIs and types: `State` maps internal states to `SyncMetadataState`; static `create` selects `DirectoryPathWaiter` for recursive BFS/DFS directory loading and `BatchPathWaiter` otherwise. Public APIs include `getState`, `isCompleted`, `succeeded`, `getTaskInfo`, `waitComplete`, `getSyncDuration`, and `toProtoTask`.

Control flow: a task starts with a `PathLoaderTask`. Load and process callbacks eventually call `onComplete`, `onFailed`, or `cancel`. `waitComplete` blocks until completion or timeout, propagating the failure cause. Completion updates direct-children-loaded flags through the file master and inode tree, marks success, notifies the metadata sync handler, and wakes waiters.

State and persistence behavior: task state is in memory. On success, `updateDirectChildrenLoaded` opens a journal context and persists direct-children-loaded updates for directories recorded in `TaskInfo`. Proto conversion includes exception and stats for reporting.

Dependencies and integration points: integrates `TaskInfo`, `PathLoaderTask`, `MetadataSyncHandler`, `DefaultFileSystemMaster`, `InodeTree`, journal contexts, `SyncMetadataTask`, and Alluxio exception types.

Risks: many methods synchronize on the task object, but callbacks arrive from loader and processor threads, so deadlock and notification correctness matter. `getStartTime` requires completion even though its name suggests simple access. Runtime exceptions in direct-children-loaded updates can turn completion into failure-like behavior outside the task result model.

Test signals: tests should cover success, failure, cancellation, timeout, proto conversion, recursive versus batch waiter selection, and direct-children-loaded journal updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BaseTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BaseTaskResult.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BaseTaskResult.java

Purpose: minimal value object representing final success or failure for a `BaseTask`.

Important APIs and types: constructor accepts a nullable `Throwable`; `succeeded` returns true when no throwable is present; `getThrowable` returns an `Optional<Throwable>`.

Control flow: `BaseTask` creates `BaseTaskResult(null)` on success, with a `CancelledException` on cancellation, or with the failure throwable on error. `getState` interprets the throwable type to distinguish failed versus canceled.

State and persistence behavior: in-memory only. Its value can be serialized into `SyncMetadataTask` reporting through `BaseTask.toProtoTask`, but it is not itself persisted.

Dependencies and integration points: integrates with `BaseTask`, task waiters, and sync task reporting.

Risks: package-private constructor and methods keep usage localized. The success/failure model is binary, so cancellation must remain represented by a specific throwable type.

Test signals: wrapper-level tests are simple; meaningful coverage comes from task completion, cancellation, and proto-reporting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BaseTaskResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BatchPathWaiter.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BatchPathWaiter.java

Purpose: `BaseTask` implementation that lets callers wait until a specific path falls within a completed loaded range. It is used for single-listing and non-directory-recursive sync modes.

Important APIs and types: maintains `mLastCompleted`, a sorted list of `PathSequence` intervals, plus a sentinel `mNoneCompleted`. `waitForSync` blocks until completion or until a path is covered by the first completed interval. `nextCompleted` merges newly completed path ranges into the interval list.

Control flow: every processed `SyncProcessResult` with a loaded sequence is passed to `nextCompleted`. The method detects adjacent intervals on left and right and either inserts, extends, or merges ranges, then notifies waiters. Waiters return task success if the whole task completes before their path is individually covered.

State and persistence behavior: in-memory progress only. It gates client traversal while background sync continues but does not write metadata directly.

Dependencies and integration points: depends on `PathSequence`, `SyncProcessResult`, `AlluxioURI` ordering, and `BaseTask` lifecycle. It is selected by `BaseTask.create`.

Risks: correctness relies on `AlluxioURI.compareTo` matching the ordering used by UFS listings and inode iteration. Interval merge edge cases can cause waiters to block too long or proceed early. The sentinel object is compared by identity, so replacing it would break the initial-state check.

Test signals: tests should cover disjoint interval insertion, left/right/both-side merge, waiting for covered and uncovered paths, interrupted waits, and final completion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BatchPathWaiter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/DefaultSyncProcess.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/DefaultSyncProcess.java

Purpose: main metadata sync engine that reconciles UFS listings with Alluxio inode metadata. It launches sync task groups, maps UFS paths to Alluxio paths through the mount table, diffs UFS statuses against inode iteration, and applies creates, deletes, recreates, metadata updates, skips, and metrics.

Important APIs and types: constructor wires `DefaultFileSystemMaster`, `ReadOnlyInodeStore`, `MountTable`, `InodeTree`, `UfsSyncPathCache`, `UfsAbsentPathCache`, `TaskTracker`, and `MetadataSyncHandler`. Public `syncPath` methods create `TaskGroup`s. `performSync` implements `SyncProcess`. Helpers include `ufsPathToAlluxioPath`, `reverseResolve`, `performSyncOne`, `deletePath`, `updateInodeMetadata`, `createInodeFileMetadata`, and `createInodeDirectoryMetadata`.

Control flow: `syncPath` resolves the Alluxio path, launches a task for the primary mount, and for recursive sync also launches tasks for nested mount points. `performSync` opens a metadata-sync journal RPC context, reverse-resolves the UFS load path, streams `UfsStatus` objects into `UfsItem`s, schedules nested directory loads for BFS/DFS modes, locks the Alluxio sync root, verifies mount stability, creates a skippable inode iterator, and repeatedly compares the current inode and current UFS item. Missing inode creates metadata; missing UFS item deletes metadata unless skipped; matching items compute a fingerprint-based sync plan to update, recreate, or no-op.

State and persistence behavior: this class performs journaled namespace mutations through file-master internals. File creation uses `CreateFileContext` with write-through, metadata-load, UFS fingerprint, xattrs, content hash xattr, block size, owner/group/mode, and completion. Directory creation uses `CreateDirectoryContext` with metadata-load, write-through, mount-point flag, fingerprint, xattrs, and direct UFS status. Deletes are alluxio-only metadata-load deletes. Attribute updates set mode, owner/group intent, and fingerprint. It also updates absent-path cache and direct-children-loaded state indirectly through task completion.

Dependencies and integration points: central integration point for file master, inode store/tree, mount table, UFS clients, UFS statuses, fingerprint comparison through `UfsSyncUtils`, sync path cache, absent cache, task tracking, journal contexts, and context wrappers. Metrics flow through `SyncProcessContext` and `SyncOperation`.

Risks: high concurrency and mount-table races are managed by reverse-resolution checks and locks but remain subtle. UFS listing order must align with inode iteration order. There appears to be a bug in `updateInodeMetadata` where non-empty UFS group is assigned via `builder.setOwner(ufsStatus.getGroup())` rather than setting group. Unknown UFS file block size throws. Recreate of directories on metadata-change delete/load is rejected as internal error. StartAfter is rejected for BFS/DFS recursive and nested mount cases.

Test signals: needs end-to-end metadata sync tests for create/update/delete/recreate/noop, nested mounts, mount removal races, BFS/DFS/single listing, truncation, startAfter, skipped non-persisted files, concurrent modification handling, TTL ignore behavior, shared mount mode changes, xattrs/content hash, absent cache updates, and operation counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/DefaultSyncProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/DirectoryPathWaiter.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/DirectoryPathWaiter.java

Purpose: `BaseTask` implementation for recursive directory syncs loaded by directory, where progress is tracked by completed directory roots rather than lexicographic item intervals.

Important APIs and types: maintains a `TrieNode<AlluxioURI>` of completed directories. `waitForSync` blocks until the requested path or its parent is covered by a completed trie entry or until task completion. `nextCompleted` inserts the base load path for non-truncated results.

Control flow: as each directory load finishes without truncation, `nextCompleted` records that directory and notifies waiters. Waiters use `getClosestTerminal` so a completed ancestor can satisfy descendants according to the path/parent check.

State and persistence behavior: in-memory progress coordination only. It does not mutate file-system metadata; mutation happens in `DefaultSyncProcess`.

Dependencies and integration points: depends on `BaseTask`, `TrieNode`, `SyncProcessResult`, `AlluxioURI`, and UFS client supplier construction. It is selected for recursive non-single-listing directory load tasks.

Risks: truncated directory results are not marked complete until a later non-truncated result, so bugs in truncation handling can block waiters. The parent-or-exact check must match traversal semantics for when a listed child is safe to expose.

Test signals: tests should cover completed exact path, completed parent, truncated batches, interruption, and final task success/failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/DirectoryPathWaiter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadRequest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadRequest.java

Purpose: represents one batch request to load UFS metadata for a path. It carries task identity, load id, batch-set id, continuation token, previous item, descendant type for this specific load, and retry policy.

Important APIs and types: getters expose task info, load path, base task id, load request id, batch set id, previous last item, continuation token, descendant type, and first-load flag. `attempt` uses `CountingRetry(2)`. `compareTo` orders requests differently for single listing, DFS, and BFS/default directory loading.

Control flow: `PathLoaderTask` creates initial and continuation requests. `LoadRequestExecutor` polls requests, performs async UFS listings, and reports errors through `onError`. The constructor increments task load-request stats.

State and persistence behavior: in-memory scheduling state only. Continuation and previous-last fields influence the persisted metadata range processed by `DefaultSyncProcess`.

Dependencies and integration points: integrates `TaskInfo`, `AlluxioURI`, `DescendantType`, `DirectoryLoadType`, retry policy, `PathLoaderTask`, and `LoadRequestExecutor`.

Risks: `equals` delegates to `compareTo` while `hashCode` uses object identity, which is inconsistent for hash collections; currently these objects are primarily queue elements. Retry count semantics must be understood: repeated load errors eventually fail the whole task.

Test signals: tests should cover BFS/DFS/single ordering, retry behavior, stat increments, continuation token propagation, and error callback routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadRequestExecutor.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadRequestExecutor.java

Purpose: schedules and executes UFS metadata load requests across active `PathLoaderTask`s with concurrency limits, per-UFS rate limiting, fair task polling, and handoff to result processing.

Important APIs and types: constructor starts a `LoadRequestRunner` thread. `addPathLoaderTask`, `hasNewLoadTask`, `onTaskComplete`, and `close` are the main lifecycle methods. Internal queues include active tasks map, task ids with pending loads, task id deque, load request queue, rate-limited priority queue, and ticket counter.

Control flow: the runner repeatedly waits until a load request is available and a ticket is free, pulls pending loads from path loader tasks, handles rate-limited permits, and calls `performListingAsync` on a UFS client. Successful UFS callbacks create `LoadResult`s and submit them to `LoadResultExecutor`; failures release tickets, record fail reasons, and ask the original request to retry or fail.

State and persistence behavior: in-memory concurrency and scheduling state only. It protects downstream persistence by limiting running or completed-but-not-processed UFS loads through `mRemainingTickets`.

Dependencies and integration points: depends on `PathLoaderTask`, `LoadRequest`, `LoadResultExecutor`, UFS client async listing API, `RateLimiter`, metrics gauges, `SamplingLogger`, and sync failure reasons.

Risks: the class mixes synchronized state with concurrent collections, so missed notifications or ticket leaks can stall sync. Rate-limited requests are removed outside the synchronized block after readiness checks, which depends on single runner thread safety. UFS callbacks must always release tickets through success or error paths.

Test signals: tests should cover concurrency cap, rate limiter delays, retryable load errors, task completion cleanup, queued-load metrics, runner shutdown, and result executor handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadRequestExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadResult.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadResult.java

Purpose: packages one completed UFS load batch with the originating `LoadRequest`, base load path, task info, previous last item, raw `UfsLoadResult`, and first-load flag.

Important APIs and types: getters expose first-load state, previous last item, base load path, UFS load result, task info, and original load request. `onProcessComplete` and `onProcessError` route processing outcomes back through `MetadataSyncHandler`. `compareTo` orders by task id then load request ordering.

Control flow: `PathLoaderTask.createLoadResult` creates it after receiving UFS output. `LoadResultExecutor` processes it by calling `SyncProcess.performSync`, then invokes its completion or error callback.

State and persistence behavior: transient result object. Its previous-last, last-item, truncation, and base path information determine the inode range that `DefaultSyncProcess` updates in persistent metadata.

Dependencies and integration points: depends on `UfsLoadResult`, `TaskInfo`, `LoadRequest`, `AlluxioURI`, and metadata sync callback plumbing.

Risks: like `LoadRequest`, `equals` is based on compare ordering while `hashCode` remains identity-based. Correct previous-last propagation is essential for chunked listing reconciliation.

Test signals: tests should cover ordering, callback routing, previous-last behavior, first-load flag, and truncated versus complete UFS result handling through `DefaultSyncProcess`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadResultExecutor.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadResultExecutor.java

Purpose: fixed-thread-pool executor for processing `LoadResult`s into metadata sync mutations. It separates UFS listing concurrency from metadata-processing concurrency.

Important APIs and types: constructor accepts a `SyncProcess`, executor thread count, and `UfsSyncPathCache`. `processLoadResult` accepts callbacks for before-processing, completion, and error. `close` shuts down the executor.

Control flow: submitted work calls `beforeProcessing`, invokes `mSyncProcess.performSync(result, mSyncPathCache)`, and routes success to `onComplete`. Mount-point-not-found and generic exceptions are caught separately to record appropriate `SyncFailReason`s before calling `onError`.

State and persistence behavior: executor state is in memory, but `performSync` carries out journaled metadata mutations. It increments process-started and process-completed counters through callbacks supplied by `LoadRequestExecutor`.

Dependencies and integration points: depends on `SyncProcess`, `LoadResult`, `SyncProcessResult`, `UfsSyncPathCache`, thread factory utilities, and sync failure reporting.

Risks: `close` uses `shutdown` without awaiting termination, so callers may need external lifecycle guarantees. Exceptions in `beforeProcessing` are not explicitly caught before `performSync`.

Test signals: tests should cover successful processing, mount-point failure classification, generic failure classification, callback ordering, thread pool shutdown, and process counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadResultExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/MetadataSyncHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/MetadataSyncHandler.java

Purpose: callback facade connecting task tracking, path loading, result processing, and file-master completion actions. It centralizes interactions among metadata sync components so the orchestration can be changed later.

Important APIs and types: methods route load errors, task failures, processing errors, per-result progress, task errors, task completion, path-load completion, nested-directory loads, load outputs, and process completion. It holds `TaskTracker`, `DefaultFileSystemMaster`, and `InodeTree`.

Control flow: UFS and processing callbacks call into this handler with task ids. It looks up active tasks in `TaskTracker` and invokes the relevant `BaseTask` or `PathLoaderTask` method. Path-load completion calls `BaseTask.onComplete`, which persists direct-children-loaded changes and then reports task completion.

State and persistence behavior: no independent persisted state. It triggers task completion paths that may update inode direct-children-loaded state and sync caches.

Dependencies and integration points: integrates `TaskTracker`, `BaseTask`, `PathLoaderTask`, `DefaultFileSystemMaster`, `InodeTree`, `LoadResult`, `UfsLoadResult`, and `SyncProcessResult`.

Risks: callbacks for missing or already-completed tasks are silently ignored through `Optional.ifPresent`, which is appropriate for races but can hide unexpected callback loss. Correct task id and load id routing is critical.

Test signals: tests should cover every callback route, missing task behavior, nested directory load scheduling, and final completion/error cleanup through `TaskTracker`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/MetadataSyncHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathLoaderTask.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathLoaderTask.java

Purpose: manages all UFS load requests for one metadata sync task. It creates initial, continuation, retry, and nested-directory load requests; tracks running loads and truncated batch sets; emits `LoadResult`s; and determines when path loading is complete.

Important APIs and types: key methods include `createLoadResult`, `loadNestedDirectory`, `onProcessComplete`, `onProcessError`, `onLoadRequestError`, `cancel`, `getNext`, and `runOnPendingLoad`. State includes ready priority queue, running load map, truncated load set, next load id, rate limiter, task info, and UFS client supplier.

Control flow: construction enqueues a first request against the base path. UFS output updates stats, records whether the first load was a file, creates continuation requests when truncated, and returns a `LoadResult`. Processing completion removes the load request, clears batch-set tracking for final batches, notifies per-result progress, and marks the whole task complete when no running or truncated loads remain.

State and persistence behavior: in-memory load orchestration only. Its completion callback triggers `MetadataSyncHandler.onPathLoadComplete`, which eventually persists direct-children-loaded updates and updates sync/absent caches.

Dependencies and integration points: depends on `LoadRequest`, `LoadResult`, `TaskInfo`, `TaskStats`, `RateLimiter`, UFS client, `UfsLoadResult`, `MetadataSyncHandler`, and directory load options.

Risks: `addLoadRequest` mutates `mRunningLoads` and queues but is not always called under this object's synchronized lock, so thread-safety relies on caller discipline and queue concurrency. Truncated batch-set accounting must be exact or tasks may complete too early or never complete. Retry exhaustion fails the entire task.

Test signals: tests should cover first load, continuation, truncated batch completion, nested directory loads, retry success/failure, cancellation, process error, and completion notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathLoaderTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathSequence.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathSequence.java

Purpose: immutable value object representing a loaded half-open path range from start to end.

Important APIs and types: constructor accepts start and end `AlluxioURI`s. Package-private `getStart` and `getEnd` expose bounds. `equals` and `hashCode` compare both endpoints.

Control flow: `DefaultSyncProcess` returns loaded ranges in `SyncProcessResult`; `BatchPathWaiter` merges them and uses them to decide when a path has been synced far enough for callers to proceed.

State and persistence behavior: in-memory coordination state only. It represents progress through persistent metadata reconciliation but is not itself stored.

Dependencies and integration points: depends on `AlluxioURI` ordering and equality. Integrates with `SyncProcessResult` and `BatchPathWaiter`.

Risks: bounds semantics are implicit; callers treat start inclusive and end exclusive. If URI ordering differs from UFS listing order, range coverage can be wrong.

Test signals: tests should cover equality, hash code, range merge behavior in `BatchPathWaiter`, and boundary path wait decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathSequence.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathWaiter.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathWaiter.java

Purpose: interface for task implementations that can block until a path is synchronized and receive progress notifications.

Important APIs and types: `waitForSync(AlluxioURI path)` returns whether the requested path became synced successfully. `nextCompleted(SyncProcessResult completed)` informs the waiter about a processed load result.

Control flow: `BaseTask` implements this interface through concrete subclasses. Traversal or sync-check code can call `waitForSync`; `MetadataSyncHandler.onEachResult` calls `nextCompleted` after each processed load.

State and persistence behavior: no state or persistence in the interface. Implementations maintain in-memory progress and coordinate with persistent metadata sync operations.

Dependencies and integration points: depends on `AlluxioURI` and `SyncProcessResult`. Implemented by `BatchPathWaiter` and `DirectoryPathWaiter`.

Risks: interface semantics require implementations to handle task completion, failure, and interruption consistently. Inconsistent coverage semantics between implementations could affect user-visible traversal.

Test signals: conformance tests should verify both implementations unblock on progress, unblock on task completion, and return false on failure/interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathWaiter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/RateLimitedRequest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/RateLimitedRequest.java

Purpose: pairs a `PathLoaderTask`, `LoadRequest`, and rate limiter permit so delayed UFS load requests can be ordered by readiness.

Important APIs and types: constructor checks non-null task and request. `isReady` and `getWaitTime` query the task's `RateLimiter` for the stored permit. `compareTo` orders by permit value; `equals` and `hashCode` include permit, task, and load request.

Control flow: `LoadRequestExecutor` creates this when `RateLimiter.acquire` returns a delay permit instead of immediate execution. The runner keeps instances in a priority queue and later executes the request when `isReady` becomes true.

State and persistence behavior: in-memory scheduling state only; no direct metadata changes.

Dependencies and integration points: depends on `PathLoaderTask`, `LoadRequest`, Guava preconditions, and Alluxio rate limiter semantics.

Risks: ordering by permit assumes permit values are comparable by readiness time. If a task's rate limiter behavior changes, the priority queue may no longer wake requests in optimal order.

Test signals: tests should cover ready/not-ready transitions, wait time, priority ordering, equality, and integration with `LoadRequestExecutor`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/RateLimitedRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncFailReason.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncFailReason.java

Purpose: enumerates categories of metadata sync failure for reporting and diagnostics.

Important APIs and types: values include generic `UNKNOWN` and `UNSUPPORTED`, load-stage failures for UFS IO and missing mount point, and processing-stage failures for unknown errors, concurrent updates, missing files, and missing mount point.

Control flow: `LoadRequestExecutor` records load failures, `LoadResultExecutor` records processing failures, and `SyncProcessContext` records failures discovered inside sync logic. Reasons are stored in `TaskStats.SyncFailure`.

State and persistence behavior: no persistence itself. Values appear in task reports and metrics/debug output and can be surfaced to CLI/API users.

Dependencies and integration points: integrates with `TaskStats`, `LoadRequestExecutor`, `LoadResultExecutor`, and `DefaultSyncProcess`.

Risks: enum lacks numeric stable ids, so serialized text consumers should not assume ordinal stability. Some values are broad, so overuse of `PROCESSING_UNKNOWN` can reduce debuggability.

Test signals: tests should verify correct classification for load IO failures, mount-point missing in load versus process stage, and concurrent modification failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncFailReason.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncOperation.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncOperation.java

Purpose: enumerates successful metadata sync operation outcomes and binds each to a metric counter.

Important APIs and types: operations include `NOOP`, `CREATE`, `DELETE`, `RECREATE`, `UPDATE`, `SKIPPED_DUE_TO_CONCURRENT_MODIFICATION`, `SKIPPED_ON_MOUNT_POINT`, and `SKIPPED_NON_PERSISTED`. Each has an integer value and a `Counter`. `fromInteger`, `getValue`, and `getCounter` expose mapping.

Control flow: `DefaultSyncProcess` reports operations through `SyncProcessContext.reportSyncOperationSuccess`, which increments both the operation counter and task stats. `TaskStats` uses integer values to index an array of counts and formats reports using `fromInteger`.

State and persistence behavior: no persistent state. Metrics counters and task reports are in-memory/observability state.

Dependencies and integration points: depends on `SyncOperationMetrics` counters and integrates with `TaskStats`, `SyncProcessContext`, and sync CLI reporting.

Risks: integer values are array indexes; inserting new enum values or changing values can break stats indexing and report interpretation. `fromInteger` must be updated with any new operation.

Test signals: tests should cover every enum's value/counter mapping, invalid integer rejection, and task stats reporting for non-zero operation counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncOperationMetrics.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncOperationMetrics.java

Purpose: centralizes Dropwizard counters for metadata sync operation outcomes.

Important APIs and types: static counters cover files created, deleted, recreated, updated, skipped due to concurrent update, skipped on mount point, no-op, and skipped non-persisted. Each counter is created through `MetricsSystem.counter` using a `MetricKey`.

Control flow: counters are initialized when the class loads. `SyncOperation` references these counters, and `SyncProcessContext.reportSyncOperationSuccess` increments the appropriate counter.

State and persistence behavior: metrics state is process-local and exported through Alluxio metrics infrastructure. No journaled metadata is owned.

Dependencies and integration points: depends on `MetricKey`, `MetricsSystem`, and `Counter`. It integrates with `SyncOperation` and the metrics backend.

Risks: static initialization can register counters early; metric key names must remain stable for dashboards and alerts. Adding a sync operation requires adding a counter and wiring it through `SyncOperation`.

Test signals: tests can verify counter registration names and operation-to-counter increments through `SyncProcessContext` or metrics registry assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncOperationMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcess.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcess.java

Purpose: interface for the component that applies one loaded UFS batch to Alluxio metadata.

Important APIs and types: single method `performSync(LoadResult loadResult, UfsSyncPathCache syncPathCache)` returns a `SyncProcessResult` and can throw any `Throwable`.

Control flow: `LoadResultExecutor` calls this interface for each `LoadResult`, allowing execution and error classification to be separated from the sync implementation. `DefaultSyncProcess` is the production implementation.

State and persistence behavior: interface has no state. Implementations are expected to perform journaled metadata changes and update sync path cache as needed.

Dependencies and integration points: depends on `LoadResult`, `SyncProcessResult`, and `UfsSyncPathCache`. Integrates with `LoadResultExecutor` and `DefaultSyncProcess`.

Risks: broad `throws Throwable` gives implementations and callers flexibility but requires careful error classification. Implementations must define transactional boundaries and cache updates clearly.

Test signals: executor tests can use fake `SyncProcess` implementations for success and failure; production behavior is covered through `DefaultSyncProcess` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcessContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcessContext.java

Purpose: per-load metadata sync processing context. It wraps journal/RPC context state, descendant type, common TTL options, concurrent-modification policy, task info, load result, operation metrics, and absent-cache updates.

Important APIs and types: main getters expose descendant type, recursive status, metadata sync RPC context, metadata sync journal context, common options, concurrent-modification flag, and task info. Mutators record directories for direct-children-loaded and absent-cache updates, report operation success, and report failure reasons. Nested `MetadataSyncRpcContext` narrows journal context type, and `Builder` constructs the wrapped journal context.

Control flow: `DefaultSyncProcess.performSync` builds this context around a non-merging journal RPC context. The builder wraps the base journal context in `MetadataSyncMergeJournalContext` with a `FileSystemJournalEntryMerger`, so many inode updates are merged and submitted asynchronously rather than hard-flushed one by one.

State and persistence behavior: owns no durable state, but mediates durable journal writes through `MetadataSyncMergeJournalContext`. On close it closes both metadata-sync and base RPC contexts. Recorded absent-cache directories are applied to `UfsAbsentPathCache` after processing.

Dependencies and integration points: integrates `RpcContext`, `BlockDeletionContext`, journal context types, `OperationContext`, `TaskInfo`, `TaskStats`, `SyncOperation`, `SyncFailReason`, `UfsAbsentPathCache`, and `DefaultSyncProcess`.

Risks: double context wrapping must be closed correctly to avoid losing or prematurely flushing journals. The builder asserts the base context is not already a `FileSystemMergeJournalContext`. Concurrent modification policy defaults to allowed, which affects whether races are skipped or fail the sync.

Test signals: tests should cover journal context wrapping, close behavior, operation counter/report updates, failure reason recording, absent-cache directory updates, and allow-modification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcessContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcessResult.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcessResult.java

Purpose: result object returned after applying one UFS load batch to Alluxio metadata.

Important APIs and types: stores task info, base load path, optional loaded `PathSequence`, truncation flag, and whether the root path is a file. Getters expose these fields via direct values and `Optional`.

Control flow: `DefaultSyncProcess.performSync` creates this result after processing a load batch. `PathLoaderTask.onProcessComplete` uses `isTruncated` to manage batch-set completion and passes it to waiters. `BaseTask.onComplete` receives `rootPathIsFile` to update sync path cache.

State and persistence behavior: in-memory processing result only. It reflects persistent metadata changes already attempted by the sync process.

Dependencies and integration points: depends on `AlluxioURI`, `TaskInfo`, and `PathSequence`. Integrates with `LoadResult`, waiters, path loader completion, and task tracker sync cache updates.

Risks: a null loaded sequence is valid, so waiters must handle absence. Incorrect truncation or root-file flags affect task completion and cache semantics.

Test signals: tests should cover optional loaded range, truncated and non-truncated completion, root-file behavior, and waiter reactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcessResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskGroup.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskGroup.java

Purpose: groups one or more `BaseTask`s created for a single user metadata-sync request, especially recursive syncs that include nested mount points.

Important APIs and types: constructor requires at least one task and stores a group id. `getBaseTask`, `getTasks`, `getTaskCount`, `allSucceeded`, `toProtoTasks`, `getGroupId`, and `waitAllComplete` expose group behavior.

Control flow: `DefaultSyncProcess.syncPath` creates a group with the primary task plus nested mount tasks. `waitAllComplete` waits sequentially on each task, computing remaining timeout with a stopwatch and propagating the first task failure or timeout.

State and persistence behavior: in-memory grouping only. The tasks in the group perform persistence and cache updates.

Dependencies and integration points: depends on `BaseTask`, `SyncMetadataTask`, `DeadlineExceededRuntimeException`, Guava `Stopwatch`, and `DefaultSyncProcess` group cache.

Risks: waits are sequential, so a later task may get little or no timeout budget if earlier tasks consume it. `getBaseTask` assumes the first task is semantically primary.

Test signals: tests should cover empty-constructor rejection, allSucceeded aggregation, proto conversion, timeout budget handling, and failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskInfo.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskInfo.java

Purpose: immutable descriptor for one metadata sync task, plus mutable task stats and a synchronized set of directories whose direct-children-loaded flag should be updated.

Important APIs and types: fields include UFS base path, Alluxio path, optional startAfter, descendant type, task id, directory load type, sync interval, metadata sync handler, and `TaskStats`. Getters expose these fields, `hasDirLoadTasks` identifies recursive BFS/DFS style tasks, and `addPathToUpdateDirectChildrenLoaded` records directories in a trie.

Control flow: `TaskTracker.launchTaskAsync` creates `TaskInfo` for each new task. `PathLoaderTask`, `DefaultSyncProcess`, `BaseTask`, and report generation repeatedly consult it for path mapping, policy, stats, callbacks, and direct-children-loaded updates.

State and persistence behavior: task info is in-memory. Recorded directories are later journaled as direct-children-loaded updates by `BaseTask.updateDirectChildrenLoaded`.

Dependencies and integration points: depends on `AlluxioURI`, `DescendantType`, `DirectoryLoadType`, `TrieNode`, `TaskStats`, and `MetadataSyncHandler`. It is the common context object across mdsync.

Risks: `startAfter` is package-private and may be null. Direct-children-loaded trie access is synchronized, but returned stream consumers must not assume concurrent modification immunity beyond the synchronized method's creation of the stream.

Test signals: tests should cover descriptor fields, `hasDirLoadTasks`, direct-children-loaded insertion and streaming, and `toString` usefulness for task reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskStats.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskStats.java

Purpose: thread-safe counters and diagnostics for one metadata sync task. It records UFS load batches, loaded object count, load requests, load errors, processing starts/completions, operation success counts, fail reasons, and terminal failure flags.

Important APIs and types: atomic counters track batches/statuses/load requests/load errors/processing. `mSuccessOperationCount` is an array indexed by `SyncOperation.getValue`. `toReportString` returns total successful operation count plus formatted details. Nested `SyncFailure` records one load or processing failure with request, optional result, reason, and throwable.

Control flow: `LoadRequest`, `PathLoaderTask`, `LoadRequestExecutor`, `LoadResultExecutor`, and `SyncProcessContext` update stats during the task lifecycle. `BaseTask.toProtoTask` embeds a report string and success operation count in the task proto.

State and persistence behavior: in-memory observability state. It may be included in task status RPC output but is not journaled.

Dependencies and integration points: depends on `SyncOperation`, `SyncFailReason`, `LoadRequest`, `LoadResult`, atomics, and concurrent maps. Integrates with task reporting and metrics.

Risks: operation count array depends on stable enum integer values. Failure map uses load request id as key and `putIfAbsent`, so later failures for the same request do not replace earlier diagnostics. `SyncFailure.toString` labels `LoadPath` with load request id, likely a diagnostic typo.

Test signals: tests should cover concurrent increments, report formatting, operation count totals, failure reason insertion, first-load-file flag, and load/process failure flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskTracker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskTracker.java

Purpose: tracks active and recently finished metadata sync tasks, prevents conflicting tasks through trie indexes, launches path loaders, handles completion/error/cancel cleanup, and updates sync/absent caches.

Important APIs and types: active task indexes are split by descendant type into recursive, list, and status tries, with configuration controlling whether non-recursive list/get-status can run concurrently with recursive tasks. Public methods include `getActiveTask`, `getTaskProto`, `cancelTaskById`, `launchTaskAsync`, test-visible `checkTask`, and `close`.

Control flow: `launchTaskAsync` finds an existing covering task or inserts a new trie node, allocates an id, creates `BaseTask`, records sync start time, stores it in maps, and submits its `PathLoaderTask` to `LoadRequestExecutor`. Completion removes active state, optionally caches task proto, increments counters, notifies sync path cache, updates absent cache based on status count, and removes trie entry. Error and cancel paths remove task state and clean load executor state.

State and persistence behavior: in-memory task registry and finished-task cache. It updates `UfsSyncPathCache` and `UfsAbsentPathCache`, which influence future sync decisions, but does not directly journal inode changes.

Dependencies and integration points: integrates `LoadRequestExecutor`, `LoadResultExecutor`, `UfsSyncPathCache`, `UfsAbsentPathCache`, `MetadataSyncHandler`, `TaskInfo`, `BaseTask`, tries, metrics counters/gauges, and UFS client suppliers.

Risks: concurrency correctness depends on synchronized methods around trie and map state. `cancelTasksUnderPath` removes active map entries but does not appear to remove trie nodes or notify load executor, making it a path to inspect carefully. Finished task cache is fixed at 1000 and may evict task status.

Test signals: tests should cover duplicate/covered task reuse, concurrency configuration, completion cleanup, error cleanup, cancellation by id, cache updates for absent versus existing paths, metrics gauges, and executor shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/AsyncUfsAbsentPathCache.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/AsyncUfsAbsentPathCache.java

Purpose: asynchronous implementation of `UfsAbsentPathCache` that caches Alluxio paths known to be absent in the mounted UFS. It avoids repeated expensive UFS existence checks for missing paths while handling invalidation races when paths are created.

Important APIs and types: constructor wires mount table, thread pool, clock, Guava cache, in-flight path locks, and metrics. Public methods are `processAsync`, `addSinglePath`, `processExisting`, and `isAbsentSince`. Internal `processPathSync`, `processSinglePath`, `getMountInfo`, `getNestedPaths`, and `PathLock` implement traversal and locking.

Control flow: `processAsync` submits a path check. `processPathSync` finds the first non-persisted component under the mount and checks nested paths one by one. `processSinglePath` ensures one processor per path, resolves the path against the original mount id, calls `ufs.exists`, caches the first absent component, and stops traversal. `processExisting` marks in-flight locks for invalidation and removes cache entries for nested components.

State and persistence behavior: in-memory cache mapping path string to `(sync time, mount id)`. No journaled state. `isAbsentSince` walks ancestors until mount base and returns true only when a cached entry is newer than the requested timestamp and belongs to the same mount id.

Dependencies and integration points: integrates `MountTable`, `MountInfo`, `UnderFileSystem.exists`, `Inode` persistence state, configuration capacities/thread counts, metrics gauges, and sync/load code that updates absent cache.

Risks: asynchronous races are subtle; invalidation intent must be set before cache removal to avoid stale absent entries after creation. Mount changes invalidate by mount id check. Unbounded task submission to the thread pool queue could lag under heavy missing-path traffic. UFS existence errors are logged and stop traversal.

Test signals: tests should cover absent hit/miss, ancestor lookup, timestamp and mount id filtering, processExisting race invalidation, duplicate in-flight path processing, mount changes, persisted-prefix base index, and metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/AsyncUfsAbsentPathCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/CheckpointedIdHashSet.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/CheckpointedIdHashSet.java

Purpose: abstract concurrent `Set<Long>` implementation that can write and restore itself using Alluxio checkpoint streams.

Important APIs and types: extends `DelegatingSet<Long>` backed by `ConcurrentHashMap.newKeySet()` and implements `Checkpointed`. `writeToCheckpoint` writes a `CheckpointType.LONGS` stream. `restoreFromCheckpoint` clears existing entries and reads longs with `LongsCheckpointReader`.

Control flow: concrete subclasses provide checkpoint identity through `getCheckpointName`. During checkpoint creation, each id is written as a long. During restore, the set is rebuilt from the checkpoint stream.

State and persistence behavior: in-memory concurrent set with checkpoint persistence. Checkpoint ordering is not guaranteed because the backing set is concurrent and unordered, but membership is preserved.

Dependencies and integration points: depends on Alluxio checkpoint stream formats and `DelegatingSet`. It is intended for master metadata sets that need lightweight checkpoint/restore behavior.

Risks: restore clears first, so malformed input can leave a partially restored set if an exception occurs mid-stream. Iteration during write is weakly consistent for concurrent hash sets; callers should coordinate checkpointing if exact point-in-time membership matters.

Test signals: tests should cover round-trip checkpoint/restore, clearing old state, empty set, concurrent modifications if supported, and concrete checkpoint name behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/CheckpointedIdHashSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/CompositeInodeLockList.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/CompositeInodeLockList.java

Purpose: temporary extension of an existing `InodeLockList` without closing or mutating the base list. It lets code lock descendants relative to an already locked path and then release only the added locks.

Important APIs and types: wraps a base lock list and a new `SimpleInodeLockList`, storing the base inode count. Implements all `InodeLockList` methods except `lockRootEdge`, which is unsupported. `nextLockMode` forces added locks to write mode if the base currently ends in a write lock.

Control flow: the first edge lock verifies that it extends from the base list's last inode. Unlock and downgrade operations affect only the sub-list. `pushWriteLockedEdge` either delegates to the sub-list when the last write lock can be downgraded, or acquires additional write locks when the base write lock cannot be modified.

State and persistence behavior: lock state only, no persistence. Correct locking protects inode metadata mutations and reads elsewhere.

Dependencies and integration points: depends on `InodeLockList`, `SimpleInodeLockList`, `InodeLockManager`, `LockMode`, and inode tree traversal/locking code such as locked path descendant operations.

Risks: base lock list is not closed by `close`; callers must manage both lifetimes. Downgrade cannot affect base locks, so write scopes may remain wider than expected. Incorrect extension parent checks could allow inconsistent lock ordering.

Test signals: tests should cover extension from inode and edge, base write mode forcing, downgrade behavior, push write locked edge behavior, close releasing only sub-locks, and index/getLockedInodes composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/CompositeInodeLockList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/Edge.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/Edge.java

Purpose: immutable key representing an inode tree edge from a parent inode id to a child name.

Important APIs and types: constructor stores parent id and child name. `getId`, `getName`, `equals`, `hashCode`, and `toString` expose key behavior; `toString` formats `parent->name`.

Control flow: inode stores and lock managers can use `Edge` as a map/set key for child relationships and edge locks. Equality requires both parent id and child name to match.

State and persistence behavior: value object only. It represents persisted inode relationships but does not write them.

Dependencies and integration points: depends on Guava `Objects`. Integrates with inode tree edge lookup, edge locks, and child mapping code elsewhere in the meta package.

Risks: child name is not validated here; callers must ensure normalized names. Null names would be accepted by equality/hash code but likely invalid semantically.

Test signals: tests should cover equality, hash code, string formatting, and behavior as a map key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/Edge.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/EdgeEntry.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/EdgeEntry.java

Purpose: simple immutable representation of a resolved inode edge and the child inode id it points to.

Important APIs and types: constructor stores parent id, child name, and child id. Getters expose each field.

Control flow: edge iteration or lookup code can return `EdgeEntry` to provide both the edge key and the target inode id without loading a full inode object.

State and persistence behavior: value object only. It mirrors persisted edge/inode-store relationships but owns no persistence.

Dependencies and integration points: no external dependencies beyond core Java. Integrates with inode store and traversal code that need compact edge records.

Risks: no equality/hash code or validation, so it is best suited as a transport record rather than a set key. Callers must ensure parent/child ids and names are consistent with the inode store.

Test signals: getter tests are enough at unit level; meaningful coverage comes from inode store edge iteration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/EdgeEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/FileSystemMasterView.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/FileSystemMasterView.java

Purpose: synchronized read-only facade over `FileSystemMaster`, used by other master components that need file metadata and worker information without exposing mutation APIs.

Important APIs and types: constructor requires a non-null `FileSystemMaster`. Synchronized methods include `getFileInfo`, `getFileId`, `getFileBlockInfoList`, `getPath`, and `getWorkerInfoList`.

Control flow: each method simply delegates to the underlying master while serializing access on the view object. Exceptions from the underlying master are propagated.

State and persistence behavior: no state beyond the delegate reference. Read methods may trigger metadata load depending on underlying master behavior, but this facade does not persist data itself.

Dependencies and integration points: depends on `FileSystemMaster`, `AlluxioURI`, wire types, and Alluxio exception types. It integrates with block master or other components needing read-only file-system master access.

Risks: synchronization here serializes only calls through this view, not all access to the underlying master. Long-running delegated calls can block other view users.

Test signals: tests should cover delegation, null delegate rejection, exception propagation, and synchronization if concurrent use matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/FileSystemMasterView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/Inode.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/Inode.java

Purpose: read-only wrapper base class for inode views. It delegates all common inode accessors to an underlying `InodeView` while providing convenient typed casts and wrapping logic.

Important APIs and types: implements common getters for timestamps, owner/group, id, TTL, mode, persistence state, parent id, xattrs, deleted/directory/file/pinned/persisted flags, UFS fingerprint, ACLs, medium types, client info, permissions, proto, and journal entry. `asDirectory`, `asFile`, and static `wrap` provide typed access.

Control flow: `wrap` returns existing `Inode` instances unchanged, otherwise checks `isFile` and wraps `InodeFileView` as `InodeFile` or `InodeDirectoryView` as `InodeDirectory`. `asDirectory` and `asFile` validate type before casting.

State and persistence behavior: wrapper owns no persistence but exposes `toProto` and `toJournalEntry` delegated from the underlying inode. Modifications to the delegate are visible through the wrapper, so it is read-only by interface, not immutable by snapshot.

Dependencies and integration points: depends on `InodeView`, inode file/directory views, ACL classes, journal/proto types, and client `FileInfo`. It is widely used by inode tree traversal, metadata sync, locks, and store APIs.

Risks: equality compares wrapped delegates only when the other object is also `Inode`, so equality with raw `InodeView` delegates is not symmetric. The read-only wrapper can reflect concurrent delegate mutation if underlying objects are mutable.

Test signals: tests should cover wrapping file and directory views, invalid casts, delegated values, equality/hash code, and journal/proto delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/Inode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeCounter.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeCounter.java

Purpose: `LongAdder`-based inode counter that supports master checkpointing.

Important APIs and types: extends `LongAdder` and implements `Checkpointed`. `getCheckpointName` returns `CheckpointName.INODE_COUNTER`; `writeToCheckpoint` writes the current sum as a long; `restoreFromCheckpoint` resets then adds the checkpointed long.

Control flow: checkpointing serializes a single count. Restore rebuilds the counter from the checkpoint stream.

State and persistence behavior: in-memory adder with checkpoint persistence. The counter is not journaled per increment here; checkpointing captures aggregate state.

Dependencies and integration points: depends on Alluxio checkpoint stream APIs and `LongAdder`. Used by file master metadata components tracking inode counts.

Risks: `LongAdder.sum()` is weakly consistent under concurrent updates, so checkpoint callers should coordinate if exact counts are required. Restore assumes the input is a long checkpoint.

Test signals: tests should cover increment/checkpoint/restore, reset behavior, empty/default count, and checkpoint name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeCounter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectory.java

Purpose: read-only forwarding wrapper for directory-specific inode view behavior.

Important APIs and types: extends `Inode` and implements `InodeDirectoryView`. Delegates `isMountPoint`, `isDirectChildrenLoaded`, and `getChildCount` to the wrapped directory view.

Control flow: created by `Inode.wrap` when the delegate is a non-file `InodeDirectoryView`. Callers use it after `asDirectory` or direct wrapping to access directory-only fields.

State and persistence behavior: no owned persistence. Delegated fields reflect persisted inode metadata such as mount-point flag, direct-children-loaded flag, and child count.

Dependencies and integration points: depends on `InodeDirectoryView` and base `Inode`. Used by metadata sync, inode traversal, and file master directory logic.

Risks: wrapper is read-only but not necessarily immutable if delegate changes. It assumes delegate is a directory view; construction does not independently validate `isDirectory`.

Test signals: tests should cover delegated directory fields, wrapping through `Inode.wrap`, and invalid `asDirectory` behavior in base class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectoryIdGenerator.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectoryIdGenerator.java

Purpose: thread-safe generator for directory inode ids, using block container ids plus sequence numbers and journaling the next id state.

Important APIs and types: constructor accepts a `ContainerIdGenerable`. `getNewDirectoryId` initializes if needed, returns current block id, advances sequence or obtains a new container, and journals the next state. `peekDirectoryId` reads the next id. Journaled methods process, reset, and iterate `InodeDirectoryIdGeneratorEntry`; checkpoint name is `INODE_DIRECTORY_ID_GENERATOR`.

Control flow: first id allocation journals a new container id with sequence 0. Each allocation returns `BlockId.createBlockId(containerId, sequenceNumber)` and journals the next pair. When max sequence is reached, it gets a new container id and resets sequence to 0.

State and persistence behavior: durable state is the next container id and sequence number, represented by `DirectoryId` and journal entries. On replay, `processJournalEntry` restores that next-id state.

Dependencies and integration points: depends on block id utilities, container id generation, journal context, journaled interface, directory id state, and checkpoint name. Used by inode tree/directory creation paths.

Risks: `resetState` does not reset `mInitialized`, so after reset in some lifecycle scenarios initialization semantics need scrutiny. `peekDirectoryId` is not synchronized, while writes are synchronized; visibility relies on `DirectoryId` internals or external discipline.

Test signals: tests should cover first initialization, sequence increment, sequence rollover to new container, journal replay, reset, iterator output, unavailable container id generation, and concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectoryIdGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectoryView.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectoryView.java

Purpose: read-only interface for directory-specific inode metadata.

Important APIs and types: extends `InodeView` and adds `isMountPoint`, `isDirectChildrenLoaded`, and `getChildCount`.

Control flow: concrete inode implementations expose directory fields through this interface. `Inode.wrap` requires non-file delegates to implement it and wraps them in `InodeDirectory`.

State and persistence behavior: interface only. The fields represent persisted or derived directory metadata used for mount behavior, listing completeness, and child accounting.

Dependencies and integration points: depends on `InodeView`. Integrated across inode store, inode tree, listing, metadata sync, and mount handling.

Risks: implementations must keep `isDirectory` from `InodeView` consistent with directory-specific methods. Incorrect direct-children-loaded state affects metadata sync and listing behavior.

Test signals: implementation tests should verify mount point, direct children loaded, and child count survive journal/proto/checkpoint round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectoryView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeFile.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeFile.java

Purpose: read-only forwarding wrapper for file-specific inode view behavior.

Important APIs and types: extends `Inode` and implements `InodeFileView`. Delegates persist job id, should-persist time, replication durable/max/min, temporary UFS path, block ids, block size, length, block container id, block id by index, cacheable flag, and completed flag.

Control flow: created by `Inode.wrap` when the delegate is a file view. Callers access file-only metadata through `asFile` or direct file wrapper references.

State and persistence behavior: no owned persistence. Delegated fields reflect persisted inode-file metadata and runtime persistence state.

Dependencies and integration points: depends on `InodeFileView`, base `Inode`, and `BlockInfoException`. Used by metadata sync to skip non-completed/non-persisted files and by file master/block metadata paths.

Risks: wrapper reflects delegate mutations and does not snapshot block id lists unless the delegate does. Construction assumes a valid file view.

Test signals: tests should cover delegated file fields, block id error propagation, wrapping through `Inode.wrap`, and base `asFile` validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeFileView.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeFileView.java

Purpose: read-only interface for file-specific inode metadata.

Important APIs and types: extends `InodeView` and adds persist job timing/id, replication durable/max/min, temporary UFS path, block ids, block size, file length, block container id, indexed block lookup, cacheable flag, and completed flag.

Control flow: concrete file inode implementations expose file fields through this interface. `Inode.wrap` uses it to create `InodeFile`, and file-master code uses it for block and persistence decisions.

State and persistence behavior: interface only. Exposed fields represent persisted inode-file metadata and persistence scheduling state.

Dependencies and integration points: depends on `BlockInfoException` and base inode view. Integrated with block master, file completion, async persistence, metadata sync, and client file-info generation.

Risks: implementations must define whether `getBlockIds` returns a defensive copy; the interface documentation says duplication is expected. Length is not accurate before file close, so callers must check `isCompleted` when correctness matters.

Test signals: implementation tests should verify block id lookup bounds, defensive block list behavior, completion state, persistence fields, replication fields, and journal/proto round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeFileView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeIterationResult.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeIterationResult.java

Purpose: pairs an `Inode` with the `LockedInodePath` used to reach it during inode tree iteration.

Important APIs and types: constructor stores inode and locked path. `getInode`, `getLockedPath`, and `toString` expose the pair.

Control flow: `DefaultSyncProcess.SyncProcessState.getNextInode` returns iteration results from a `SkippableInodeIterator`. Sync logic compares the result's locked path URI with current UFS item and may traverse, delete, update, or skip children.

State and persistence behavior: value object only. The locked path manages live locks protecting persistent metadata operations.

Dependencies and integration points: depends on `Inode` and `LockedInodePath`. Integrates with inode iteration, lock management, and metadata sync diffing.

Risks: consumers must close or manage the underlying locked path according to iterator semantics; this wrapper does not own lifecycle beyond holding the reference. `toString` only includes the path, not inode id.

Test signals: tests should cover getter behavior and integration with skippable inode iteration and lock lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeIterationResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeLockList.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeLockList.java

Purpose: interface describing a locked inode path as an ordered list of inode and edge locks. It formalizes lock ordering, downgrade, extension, and release behavior for inode tree concurrency control.

Important APIs and types: methods lock root edge, inode, and child edge; unlock last inode or edge; downgrade all locks or last edge; push a write-locked edge forward; inspect lock mode, locked inodes, indexed inode, inode count, whether the list ends in an inode, emptiness, and the associated `InodeLockManager`; and close all locks.

Control flow: implementations build paths with read locks followed by write locks. `pushWriteLockedEdge` supports traversal patterns that hold a write edge only at the frontier while downgrading prior locks to read. Composite implementations can extend existing lock lists.

State and persistence behavior: in-memory lock state only, but it protects all persistent inode metadata operations. Correct use prevents concurrent create/delete/update races.

Dependencies and integration points: depends on `LockMode`, `Inode`, `InodeView`, and `InodeLockManager`. Used by locked inode paths, inode tree traversal, metadata sync, create/delete/rename, and mount handling.

Risks: annotated not thread-safe; each lock list should be owned by one thread. Implementations must maintain strict lock ordering to avoid deadlocks. Callers must always close lists to release locks.

Test signals: tests should cover root edge locking, inode/edge order, downgrade semantics, push-write behavior, composite behavior, close idempotence if promised by implementation, and deadlock-sensitive traversal patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeLockList.java -->
