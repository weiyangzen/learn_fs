# Group Research: group_1849_windows_driver_samples_sources_windows_windows_driver_samples_files_fade0a1bdd9d

Scope checked against `Docs/research_subset_a.md`: these files are within `sources/windows/windows-driver-samples`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/avscan.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/avscan.c

Main kernel minifilter implementation for the AV scan sample. It registers Filter Manager callbacks for create, cleanup, write, set-information, and file-system-control, owns driver initialization/unload, volume instance setup/teardown, scan dispatch, file-state cache synchronization, transaction outcome handling, and policy decisions about when to scan or skip a stream.

Key responsibilities:
- `DriverEntry` initializes `Globals`, scan-context list locking, registry-configured timeouts, Filter Manager registration, and three communication ports.
- `AvUnload` marks unloading, notifies the user-mode scanner, closes communication ports, unregisters the filter, and deletes global resources.
- `AvInstanceSetup` skips network file systems and hidden CSV NTFS volumes, creates an instance context, initializes an AVL file-state cache for NTFS/CSVFS/ReFS, and registers the instance for data scan.
- `AvPreCreate` filters out stack file objects, directories, rename target-directory opens, paging files, DASD opens, CSV downlevel opens, and prefetch opens; it synchronizes post-create processing.
- `AvPostCreate` creates or retrieves stream contexts, loads cached state by file ID, handles transaction context transitions, runs CSVFS revision checks, scans modified streams, and cancels infected opens with `STATUS_VIRUS_INFECTED`.
- `AvPreCleanup` scans modified non-transacted files before cleanup, updates CSVFS revision data after successful scans, and persists clean/infected state to the per-instance cache.
- `AvPreOperationCallback` marks stream state modified for writes, selected FSCTLs, EOF changes, and valid-data-length changes, while respecting transacted writer state.
- `AvPreFsControl` rejects TxF savepoint control and delegates other modifying FSCTLs to the generic pre-operation path.
- `AvKtmNotificationCallback`, `AvProcessPreviousTransaction`, and `AvProcessTransactionOutcome` maintain transaction-isolated `TxState` and propagate it to normal stream state only on commit.
- `AvScan` serializes scans per stream with `ScanSynchronizationEvent`, skips empty files, invokes either user-mode or kernel-mode scan, and handles cancellable waits.

Important data flow:
- A stream starts as `AvFileModified`; after a successful scan it becomes clean or infected.
- NTFS/CSVFS/ReFS file IDs allow volatile cache lookups through `AvLoadFileStateFromCache` and writes through `AvSyncCache`.
- Transacted writers use `TxState`; commit propagates transaction state, rollback discards it.
- CSVFS revision numbers can force rescans when another cluster node may have changed the file.
- User-mode scans are the normal path via `AvScanInUser`; kernel-mode scanning is supported but not the default in the create/cleanup paths.

Concurrency and lifecycle notes:
- `Globals.ScanCtxListLock` protects the global active scan list and unloading flag.
- Per-stream scanning is serialized with a nonpaged event held in the stream context.
- Transaction context lists are protected by per-transaction `ERESOURCE`.
- Instance teardown walks active scans for that instance, asks user mode to abort, and force-finalizes scans if abort messaging fails.
- The file-state cache is unbounded by design; comments explicitly warn production filters should cap it.

Dependencies:
- Internal: `avscan.h`, `context.h`, `scan.h`, `csvfs.h`, `utility.h`, `avlib.h`.
- Windows kernel APIs: Filter Manager, KTM/TxF, ECPs, `ERESOURCE`, generic AVL table, registry APIs, section data scan APIs.

Research notes:
- This is sample-quality AV logic, not a production policy engine. It chooses availability over strict blocking on timeout/failure, with comments noting this may allow a security gap.
- Alternate data streams are skipped deliberately.
- Encrypted backup/raw opens are skipped to avoid NTFS encryption-context assertions.
- Prefetch opens are tagged with stream-handle context and excluded from scan and write-modification tracking to avoid deadlocks.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/avscan.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/avscan.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/avscan.h

Kernel-private umbrella header for the AV minifilter. It enables AVL tables, includes Filter Manager and all local AV modules, defines the global driver state, declares scan-context lifecycle helpers, and provides an inline create-cancellation helper.

Key definitions:
- `AV_SCAN_CONTEXT` tracks one active scan: refcount, instance, file object, completion event, global-list entry, section context, scan ID, user scan thread ID, triggering IRP major function, transaction-writer flag, and abort state.
- `AV_SCANNER_GLOBAL_DATA` stores process-wide minifilter state: scan ID counter, filter pointer, server/client communication ports, active scan list and lock, local/network scan timeouts, debug level, and unloading flag.
- `Globals` is declared as the global instance of `AV_SCANNER_GLOBAL_DATA`.
- Debug trace flags and `AV_DBG_PRINT` wrap `DbgPrint` in checked builds.
- `AvCancelFileOpen` wraps `FltCancelFileOpen`, sets the callback status, and clears information.

Declared interfaces:
- Communication setup and abort notification: `AvPrepareServerPort`, `AvSendAbortToUser`.
- Scan context lifecycle: `AvAllocateScanContext`, `AvReferenceScanContext`, `AvReleaseScanContext`.
- Finalization wrappers: `AvFinalizeScanAndSection`, `AvFinalizeSectionContext`, `AvFinalizeScanContext`.

Dependencies:
- Includes `utility.h`, `context.h`, `scan.h`, `csvfs.h`, and shared protocol header `avlib.h`.
- Requires Filter Manager kernel headers.

Research notes:
- The scan context is intentionally separated from the section context to reduce coupling between I/O request threads and scanner implementation details.
- Global scan-context tracking is central to user-mode command validation: scan IDs sent from user mode are accepted only if found in `Globals.ScanCtxListHead`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/avscan.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/communication.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/communication.c

Kernel/user communication implementation for the AV minifilter. It creates and manages Filter Manager communication ports, handles client connect/disconnect callbacks, validates user messages, dispatches scan commands, and maps user-provided file handles back to stream contexts for query operations.

Key responsibilities:
- `AvPrepareServerPort` creates one named server port for scan, abort, or query traffic using names from `avlib.h`.
- `AvConnectNotifyCallback` accepts exactly one connection per type, copies the connection type into a cookie, and records the client port in `Globals`.
- `AvDisconnectNotifyCallback` closes the matching client port and frees the connection cookie.
- `AvMessageNotifyCallback` handles `AvCmdCreateSectionForDataScan`, `AvCmdCloseSectionForDataScan`, and `AvIsFileModified`.
- `AvGetScanCtxSynchronized` validates scan IDs by searching the global active scan list under `Globals.ScanCtxListLock` and references the scan context while in use.
- `AvHandleCmdCreateSectionForDataScan` creates a section context and Filter Manager data-scan section, marks stream state as scanning, stores the section context in the scan context, and returns a user-mode section handle.
- `AvHandleCmdCloseSectionForDataScan` records the scanner’s result, finalizes scan/section state, and releases waiting I/O.
- `AvUpdateStreamContextWithScanResult` transitions stream or transaction state from scanning to infected/clean, or back to modified if undetermined.
- `AvGetInstanceContextByFileHandle` and `AvGetStreamContextByHandle` support query-port file-handle lookups.

Protocol behavior:
- User mode starts from a scan notification sent by `scan.c`, then sends create-section and close-section commands back to this callback.
- Output buffers are checked for size and alignment before handle/boolean writes.
- User buffers are accessed inside exception handling using `AvExceptionFilter`.
- If writing the section handle back to user mode fails, the kernel closes the handle with `NtClose` and finalizes the scan to avoid leaks and blocked I/O.

Concurrency and lifecycle notes:
- Section finalization uses interlocked pointer exchange so only one racing thread tears down the section.
- `AvFinalizeScanContext` always signals `ScanCompleteNotification`.
- Section finalization calls `AvCloseSectionForDataScan` and releases the Filter Manager section context reference.
- `AvHandleCmdCreateSectionForDataScan` handles cancellation both before and after section creation.

Dependencies:
- Filter Manager communication ports, section data scan APIs, object handle referencing, active scan context helpers from `avscan.h`, stream/instance context helpers from `context.c`, and shared command structures from `avlib.h`.

Research notes:
- The file-modified query reports only `IS_FILE_MODIFIED(streamContext)`, not infected or transaction-modified state.
- The design assumes one client connection per port type.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/communication.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/context.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/context.c

Filter Manager context implementation for stream, stream-handle, transaction, section, and instance contexts, plus manual allocation/refcounting for scan contexts. It registers all minifilter context types and owns cleanup for auxiliary allocations inside those contexts.

Key responsibilities:
- `ContextRegistration` registers stream, stream-handle, transaction, section, and instance contexts with Filter Manager.
- `AvCreateStreamContext` allocates a stream context, allocates a nonpaged scan synchronization event, initializes the event signaled, and marks both normal and transaction state as modified.
- `AvCreateStreamHandleContext` allocates a small per-handle context used primarily for prefetch tracking.
- `AvFindOrCreateTransactionContext` retrieves or allocates a transaction context, references the KTM transaction object, initializes its resource/list, and sets the Filter Manager transaction context.
- `AvCreateSectionContext` allocates a section context and records current file size when available.
- `AvEnumerateInstances` and `AvFreeInstances` enumerate all instances for volume-to-instance lookup in the communication path.
- `AvAllocateScanContext`, `AvReferenceScanContext`, and `AvReleaseScanContext` manage non-Filter-Manager scan contexts with an interlocked refcount, instance reference, and file-object reference.

Cleanup behavior:
- `AvStreamContextCleanup` asserts the stream is no longer linked to a transaction context and frees its scan synchronization event.
- `AvTransactionContextCleanup` deletes/frees its resource and dereferences the transaction object.
- `AvSectionContextCleanup` asserts section handle/object have already been cleared.
- `AvInstanceContextCleanup` asserts the file-state cache is empty and deletes the instance resource when the filesystem supports caching.

Dependencies:
- Filter Manager context APIs, KTM transaction objects, `ERESOURCE`, stream/transaction structures from `context.h`, scan context structure from `avscan.h`, and allocation wrappers from `utility.h`.

Research notes:
- Transaction context resources are separately allocated from nonpaged pool because `ERESOURCE` cannot live in paged memory.
- Scan contexts are not Filter Manager contexts; they are pool allocations tracked by the AV driver and global scan list.
- `AvReleaseScanContext` comments note the simple refcount assumes references/releases are not raced beyond intended usage.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/context.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/context.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/context.h

Kernel-private context model for the AV minifilter. It defines infection-state enums, pool tags, state transition macros, stream/transaction/section/instance context layouts, and prototypes for context creation/enumeration helpers.

Key definitions:
- `AV_FILE_INFECTED_STATE`: `AvFileUnknown`, `AvFileInfected`, `AvFileNotInfected`, `AvFileModified`, `AvFileScanning`.
- State macros distinguish normal state from transaction-isolated `TxState`.
- `IS_FILE_NEED_SCAN` requires scanning when a non-transacted file is modified or a transacted file’s `TxState` is modified.
- `AV_TRANSACTION_CONTEXT` stores the transaction pointer, list of associated stream contexts, synchronization resource, and flags for enlisted/list-drained state.
- `AV_STREAMHANDLE_CONTEXT` stores per-handle flags, currently `AV_FLAG_PREFETCH`.
- `AV_STREAM_CONTEXT` stores flags, file ID, transaction context pointer, transaction-list entry, scan synchronization event, normal and transaction infection states, and CSVFS revision numbers.
- `AV_SECTION_CONTEXT` stores data-scan section handle/object, abort state, file size, conflict-cancelability, and backpointer to scan context.
- `AV_INSTANCE_CONTEXT` stores volume/instance pointers, filesystem type, volatile file-state cache table, cache resource, and CSV hidden-volume flag.

Declared interfaces:
- Transaction context: `AvFindOrCreateTransactionContext`.
- Section, stream-handle, and stream context creation.
- Instance enumeration/free helpers.

Dependencies:
- Uses types from Filter Manager, KTM, Windows lists/events/resources, and `AV_FILE_REFERENCE` from `utility.h`.

Research notes:
- The state macros use `InterlockedExchange`, making state transitions atomic but not full compound-state protocols.
- CSVFS revision fields are part of the generic stream context so core scan logic can update them after CSV-specific checks.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/context.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/csvfs.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/csvfs.c

CSVFS-specific support for the AV minifilter. It explains CSVFS architecture, avoids scanning internal CSV downlevel opens, detects hidden CSV NTFS disks, and uses CSVFS revision numbers to decide when a stream may have changed on another cluster node.

Key responsibilities:
- `AvIsVolumeOnCsvDisk` sends `IOCTL_DISK_GET_CLUSTER_INFO` to the disk stack and returns true when the disk is CSV and not in maintenance mode.
- `AvIsCsvDlEcpPresent` detects `GUID_ECP_CSV_DOWN_LEVEL_OPEN` and is used by create filtering to skip CSVFS internal opens.
- `AvPreCreateCsvfs` adds a `GUID_ECP_CSV_QUERY_FILE_REVISION` ECP on CSVFS creates so CSVFS can return revision numbers.
- `AvPostCreateCsvfs` reads acknowledged revision ECP data, compares volume/cache/file revision numbers with the stream context, and marks the stream modified when a rescan is needed.
- `AvPreCleanupCsvfs` queries current revision numbers via `FSCTL_CSV_CONTROL` and applies the same rescan/update decision before cleanup.
- `AvAddCsvRevisionECP`, `AvFindAckedECP`, `AvReadCsvRevisionECP`, and `AvQueryCsvRevisionNumbers` implement ECP and FSCTL plumbing.

Rescan policy:
- Rescan is forced if any revision number is zero, unavailable, or differs from the stream context’s stored revision.
- Revision mismatch is intentionally pessimistic because another node can change the file without this filter instance seeing ordinary write I/O.
- Valid new revisions are returned to the caller for storage after a successful scan.

Dependencies:
- Filter Manager ECP APIs, CSVFS ECP GUIDs, `FSCTL_CSV_CONTROL`, `CSV_CONTROL_PARAM`, `CSV_QUERY_FILE_REVISION`, disk cluster IOCTLs from `ntdddisk.h`, and stream/instance contexts.

Research notes:
- The top comment is important design guidance: filters on hidden NTFS/MUP stacks must avoid CSVFS downlevel opens, and hidden NTFS filters can cause cache coherency or corruption issues.
- The code intentionally treats missing instance context as a reason to rescan rather than trust stale state.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/csvfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/csvfs.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/csvfs.h

Kernel-private CSVFS interface header for the AV minifilter. It declares the CSVFS hooks used by `avscan.c` and the helper predicates for CSV downlevel opens and CSV disk detection.

Declared interfaces:
- `AvPreCleanupCsvfs`: checks CSVFS revision numbers before cleanup and returns whether stream revision fields should be updated after a successful scan.
- `AvPostCreateCsvfs`: consumes create-time CSVFS revision ECP results and decides whether a rescan is needed.
- `AvPreCreateCsvfs`: adds the CSV revision query ECP during pre-create on CSVFS volumes.
- `AvIsCsvDlEcpPresent`: detects internal CSVFS downlevel-open ECPs.
- `AvIsVolumeOnCsvDisk`: checks whether a volume’s disk is a CSV disk outside maintenance mode.

Dependencies:
- Requires `PFLT_CALLBACK_DATA`, `PCFLT_RELATED_OBJECTS`, `PAV_STREAM_CONTEXT`, and `PFLT_VOLUME` from the kernel AV and Filter Manager context.

Research notes:
- The revision-number out-parameters let generic create/cleanup logic stay mostly filesystem-neutral while still updating CSV-specific coherence metadata after scans.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/csvfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/scan.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/scan.c

Scan execution module for both kernel-mode and user-mode scanning. It implements the toy signature scanner, section mapping for kernel scans, user-mode scan notification/wait/abort handling, and section cleanup wrappers.

Key responsibilities:
- `AvScanMemoryStream` decodes the XOR-obfuscated default signature from `avlib.h` and linearly searches a memory range, returning infected, clean, or undetermined if canceled.
- `AvMapSectionAndScan` opens the current process, maps the data-scan section read-only, scans up to the lesser of mapped size and file size, then unmaps/closes.
- `AvScanInKernel` creates a section context and data-scan section, maps/scans it in kernel path, updates stream state, and finalizes the section.
- `AvScanInUser` allocates a scan context, inserts it into the global scan list, sends an `AvMsgStartScanning` notification, waits for the user service to create/scan/close the section, handles timeout/cancellation, sends abort messages, and removes/releases the scan context.
- `AvCloseSectionForDataScan` clears the scan-context backpointer, dereferences the section object, nulls section fields, and calls `FltCloseSectionForDataScan`.

Timeout behavior:
- User-mode scans use `Globals.LocalScanTimeout` or `Globals.NetworkScanTimeout` based on volume device type.
- If the scan wait fails or times out, the kernel asks user mode to abort and waits briefly for cleanup.
- If abort communication fails or times out, the kernel marks the wait aborted and finalizes scan/section state itself.
- For canceled create scans, the file open is canceled via `AvCancelFileOpen`.

Dependencies:
- Filter Manager data scan APIs, shared protocol types from `avlib.h`, scan context lifecycle from `context.c`, abort messaging from `avscan.c`, and stream state macros from `context.h`.

Research notes:
- The scanner is intentionally simple: a single decoded byte-pattern search.
- `AvScanInKernel` leaks the allocated section context if `FltCreateSectionForDataScan` fails before finalization; this is sample code but noteworthy from a production review perspective.
- `AvScanInUser` is the main path used by `avscan.c`; kernel scan support is present for demonstration.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/scan.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/scan.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/scan.h

Kernel-private scan interface header. It defines scan mode and declares the scan entry points used by the main minifilter.

Key definitions:
- `AV_SCAN_MODE`: `AvKernelMode` and `AvUserMode`.

Declared interfaces:
- `AvScanInKernel`: performs scan using a kernel-created data-scan section and kernel memory search.
- `AvScanInUser`: coordinates user-mode scanner work through Filter Manager messaging.
- `AvCreateSectionForDataScan`: declared but not implemented in the listed `scan.c`; section creation is implemented through `FltCreateSectionForDataScan` in `scan.c` and `communication.c`.
- `AvCloseSectionForDataScan`: wraps section close/cleanup.

Dependencies:
- Includes `avlib.h` and relies on Filter Manager and AV context types included before or through `avscan.h`.

Research notes:
- The exposed abstraction is small: callers choose kernel/user scan and section lifecycle helpers stay hidden behind this interface.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/scan.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/utility.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/utility.c

Utility implementation for generic table callbacks and file metadata queries. It backs the per-instance file-state cache and provides helpers used by create/scan logic.

Key responsibilities:
- `AvCompareEntry` compares cached file-state entries by 128-bit file reference, lower 64 bits first and upper 64 bits second.
- `AvAllocateGenericTableEntry` and `AvFreeGenericTableEntry` allocate/free AVL table entries from paged pool.
- `AvGetFileId` queries ReFS file IDs with `FileIdInformation` and other file systems with `FileInternalInformation`, normalizing into `AV_FILE_REFERENCE`.
- `AvGetFileSize` queries `FileStandardInformation.EndOfFile`.
- `AvGetFileEncrypted` queries `FileBasicInformation.FileAttributes`.
- `AvExceptionFilter` allows expected NTSTATUS exceptions, especially while touching user buffers.

Dependencies:
- Filter Manager `FltQueryInformationFile`, `FltGetFileSystemType`, generic table callbacks, file-information classes, and structures from `utility.h`.

Research notes:
- ReFS support is handled explicitly because ReFS uses 128-bit file IDs.
- The compare function does not implement a bytewise 128-bit order, but it is self-consistent, which is sufficient for the AVL table.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/utility.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/utility.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/utility.h

Kernel-private utility header for allocation tags, file references, generic table entries, filesystem-cache support checks, allocation wrappers, metadata helper prototypes, resource wrappers, and a safe list iteration macro.

Key definitions:
- Pool tags for strings, resources, events, and table entries.
- `AV_FILE_REFERENCE`: union supporting NTFS-style 64-bit IDs and ReFS 128-bit IDs.
- `AV_INVALID_FILE_REFERENCE` and `AV_SET_INVALID_FILE_REFERENCE`.
- `AV_GENERIC_TABLE_ENTRY`: file ID, infected state, and CSVFS revision numbers cached per instance.
- `FS_SUPPORTS_FILE_STATE_CACHE`: true for NTFS, CSVFS, and ReFS.
- Inline alloc/free helpers for nonpaged `ERESOURCE` and `KEVENT`.
- Inline resource acquire/release wrappers that enter/leave critical regions and assert IRQL/resource state.
- `LIST_FOR_EACH_SAFE` for deletion-safe list traversal.

Declared interfaces:
- Generic table callbacks: `AvCompareEntry`, `AvAllocateGenericTableEntry`, `AvFreeGenericTableEntry`.
- Metadata helpers: `AvGetFileId`, `AvGetFileSize`, `AvGetFileEncrypted`.
- `AvExceptionFilter`.

Dependencies:
- Windows kernel pool/resource/list/generic table APIs and file ID types.

Research notes:
- The resource wrappers enforce passive/APC-level usage assumptions made by the pageable callback paths.
- The cache entry stores CSVFS revision numbers alongside infection state so cache hits can remain coherent across CSVFS revision checks.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/utility.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/inc/avlib.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/inc/avlib.h

Shared kernel/user protocol header for the AV scan sample. It defines port names, command/message enums, message payload structures, connection context, invalid section handle sentinel, and the toy signature pattern.

Key definitions:
- Port names: scan, abort, and query Filter Manager communication ports.
- `AVSCAN_COMMAND`: query file modified, create section for data scan, close section for data scan.
- `AVSCAN_MESSAGE`: start scanning, abort scanning, filter unloading.
- `AVSCAN_REASON`: scan on open or cleanup.
- `AVSCAN_RESULT`: undetermined, infected, clean.
- `COMMAND_MESSAGE`: user-to-kernel command with scan ID, scan thread ID, and union for file handle or scan result.
- `AV_SCANNER_NOTIFICATION`: kernel-to-user notification with message, reason, scan ID, and scan thread ID.
- `AVSCAN_CONNECTION_TYPE` and `AV_CONNECTION_CONTEXT`: identify scan/abort/query client connections.
- `AV_DEFAULT_SEARCH_PATTERN`, size, and XOR key for the sample signature string.

Dependencies:
- Designed to compile in both user and kernel mode; uses Windows handle-sized types and suppresses MSVC nameless union warning.

Research notes:
- This header is the protocol contract between `filter/communication.c`, `filter/scan.c`, and user-mode scanner code.
- The default pattern is obfuscated with XOR key `90`; scan code decodes it before searching.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/inc/avlib.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/avscan.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/avscan.c

User-mode scanner entry point. It initializes user scan worker state, waits for interactive quit input, finalizes scanner resources, and exits.

Key behavior:
- Includes Windows, Filter Manager user API, shared AV protocol, user utility, and `userscan.h`.
- `main` ignores command-line arguments, zero-initializes `USER_SCAN_CONTEXT`, and calls `UserScanInit`.
- On initialization failure, it prints an error, calls `DisplayError`, and returns `255`.
- It loops prompting `press 'q' to quit:` and exits only when the user enters `q`.
- On exit, it calls `UserScanFinalize`; finalize failure is reported but does not change the returned status.
- Successful program exit returns `0`.

Dependencies:
- `UserScanInit`, `UserScanFinalize`, and `USER_SCAN_CONTEXT` are declared outside this file.
- Uses `fltUser.h` for user-mode Filter Manager communication support and `avlib.h` for shared protocol definitions.

Research notes:
- This file is only the console harness; scan worker behavior and message handling live in other user-mode files not included in this group.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/avscan.c -->