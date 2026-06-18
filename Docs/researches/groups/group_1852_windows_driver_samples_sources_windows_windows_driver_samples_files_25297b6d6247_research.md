# Group Research: group_1852_windows_driver_samples_sources_windows_windows_driver_samples_files_25297b6d6247

Scope confirmed against `Docs/research_subset_a.md`. All 12 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/mspyLib.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/mspyLib.c

Kernel-mode support library for the MiniSpy minifilter’s logging path.

Key responsibilities:
- Allocates, initializes, frees, queues, drains, and returns variable-length `LOG_RECORD` entries.
- Converts transaction notification bit flags into MiniSpy minor-code values with `TxNotificationToMinorCode`.
- Captures pre-operation, post-operation, and transaction-notification metadata into shared `RECORD_DATA`.
- Copies record batches to user buffers in `SpyGetLog`, preserving records if a user-buffer copy faults.
- Reads registry parameters `MaxRecords` and `NameQueryMethod` into `MiniSpyData`.
- On Vista/Win7 builds, parses Extra Create Parameters and formats known ECP details into the log name buffer.

Important behavior:
- Uses a nonpaged lookaside list plus `MiniSpyData.RecordsAllocated` to cap log-buffer allocations.
- Falls back to a single static out-of-memory buffer when dynamic allocation fails or the memory allowance is exceeded.
- Protects `MiniSpyData.OutputBufferList` with a spin lock and releases it before copying records to user mode.
- Ensures variable log record sizes are pointer-aligned to avoid IA64 alignment faults.
- If no file name is present, `SpyGetLog` appends an empty null-terminated name before returning the record.

ECP handling:
- `SpyParseEcps` walks FltMgr ECP lists, counts total ECPs, ignores user-mode-originated known ECP contexts, and records known ECP flags.
- `SpyBuildEcpDataString` formats prefetch, oplock-key, NFS-open, and SRV-open ECP data when supported by build flags.
- Network ECPs format IPv4/IPv6 socket addresses with `RtlIpv4AddressToStringEx` / `RtlIpv6AddressToStringEx`.

Dependencies and risks:
- Depends on global `MiniSpyData`, shared structures from `minispy.h`, kernel filter-manager APIs, and MiniSpy kernel declarations from `mspyKern.h`.
- Allocation-limit checks are intentionally approximate; concurrent callers can transiently exceed the configured maximum.
- The single static fallback buffer is guarded by `InterlockedExchange`, but release sets the flag with a plain store.
- `_snwprintf` truncation is handled manually, and the code relies on the shared record-size macros to keep output bounded.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/mspyLib.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/inc/minispy.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/inc/minispy.h

Shared kernel/user ABI header for MiniSpy.

Key contents:
- Defines MiniSpy-specific FltMgr pseudo-major codes for FSFilter, Fast I/O, volume mount/dismount, and transaction notification logging.
- Defines MiniSpy version `2.0` and communication port name `\\MiniSpyPort`.
- Defines shared scalar aliases, including `FILE_ID` and user-visible `NTSTATUS`.
- Sets fixed record transport size to `RECORD_SIZE` = 1024 bytes.
- Defines record types and flags for normal records, file-tag records, static fallback records, memory-limit records, and out-of-memory records.
- Defines `RECORD_DATA`, the fixed metadata captured for each callback: times, object IDs, process/thread IDs, status/information, flags, callback major/minor IDs, six generic arguments, and ECP summary fields.
- Defines variable-length `LOG_RECORD` and enclosing `RECORD_LIST`.
- Defines `MINISPY_COMMAND` and `COMMAND_MESSAGE` for user/kernel commands.

Important behavior:
- `LOG_RECORD.Name[]` is a flexible trailing string area and is packed into the 1024-byte transport record.
- `MAX_NAME_SPACE`, `MAX_NAME_SPACE_LESS_NULL`, `MAX_NAME_WCHARS_LESS_NULL`, and `MAX_LOG_RECORD_LENGTH` keep names aligned and bounded.
- Helper macros `Add2Ptr`, `ROUND_TO_SIZE`, and `FlagOn` are provided when not already present.

Dependencies and risks:
- This file is the contract between `minispy.sys` and `minispy.exe`; layout, alignment, and record-size changes must be coordinated on both sides.
- Several callback major IDs are negative `UCHAR` values, so consumers must treat them consistently with MiniSpy’s definitions rather than standard IRP major-code ranges alone.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/inc/minispy.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyLog.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyLog.c

User-mode MiniSpy log retrieval and formatting implementation.

Key responsibilities:
- `RetrieveLogRecords` runs as the logging thread, sends `GetMiniSpyLog` commands through the filter communication port, validates packed `LOG_RECORD` lengths, and dumps each record to screen and/or file.
- `TranslateFileTag` recognizes mount-point reparse records and moves the substitute name into `LOG_RECORD.Name`.
- `PrintIrpCode` translates logged major/minor operation codes into display strings, including standard IRPs, FltMgr pseudo-operations, Fast I/O style operations, and transaction notifications.
- `FormatSystemTime` formats local system times as `HH:MM:SS:mmm`.
- `FileDump` writes tab-delimited records with object IDs, flags, operation names, status/information, arguments, and name.
- `ScreenDump` prints a console-oriented one-line record plus optional minor-code continuation line.

Important behavior:
- Uses an aligned 4096-byte receive buffer because kernel records are pointer-aligned and packed back-to-back.
- Detects malformed record lengths before advancing through the returned buffer.
- Polls every 200 ms when no records are available or when the driver reports no more items.
- Exits the process if the kernel component unloads and the port handle becomes invalid.
- Prints memory-pressure markers when record flags indicate out-of-memory or exceeded allocation allowance.

Dependencies and risks:
- Depends on `fltUser.h` messaging, `mspyLog.h` constants, and the exact `LOG_RECORD` layout from `minispy.h`.
- File and screen output duplicate much of the same formatting logic, so operation-code mapping mistakes affect both paths.
- The transaction display switch appears to map `TRANSACTION_NOTIFY_PREPARE_COMPLETE_CODE` to the commit-complete string, which is likely a sample typo.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyLog.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyLog.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyLog.h

User-mode MiniSpy logging header.

Key contents:
- Includes `fltUser.h` and shared `minispy.h`.
- Defines `BUFFER_SIZE` = 4096 for batched log retrieval.
- Defines `LOG_CONTEXT`, holding the MiniSpy port, screen/file logging toggles, output file handle, cleanup flag, and shutdown semaphore.
- Declares `RetrieveLogRecords`, `FileDump`, and `ScreenDump`.
- Re-declares user-mode values for `FLT_CALLBACK_DATA_*` operation-type flags.
- Provides string constants for standard IRP major codes, FltMgr pseudo-major codes, Fast I/O-like major codes, IRP minor codes, PnP/power/system-control minors, and transaction notification names.
- Defines local numeric IRP major/minor values needed by the formatter.
- Defines `TRANSACTION_NOTIFICATION_CODES`, aligned with kernel-side `TxNotificationToMinorCode`.
- Defines `FLT_TAG_DATA_BUFFER` so the user utility can interpret file-tag/reparse log records.

Important behavior:
- This header intentionally mirrors kernel/FltMgr constants so the user program can decode logs without including kernel headers.
- Transaction notification code ordering is tied to the bit-position conversion in `mspyLib.c`.

Dependencies and risks:
- Duplicate definitions must stay synchronized with kernel logging behavior and with Windows/FltMgr values.
- The local `FLT_TAG_DATA_BUFFER` is only a display helper for reparse data placed in the log name area.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyLog.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyUser.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyUser.c

Main MiniSpy user-mode control utility.

Key responsibilities:
- Connects to `\\MiniSpyPort`.
- Creates shared `LOG_CONTEXT`, a shutdown semaphore, and the log retrieval thread.
- Supports startup and interactive commands for attach, detach, list, screen logging, file logging, and exit.
- Lists current filter attachments across volumes.
- Translates Win32 and fltlib error codes into readable messages.

Command behavior:
- `/a <drive>` attaches the `MiniSpy` filter with `FilterAttach` and prints the created instance name.
- `/d <drive> [instance id]` detaches one instance with `FilterDetach`.
- `/l` lists volumes and attachment status.
- `/s` toggles screen logging after command mode exits.
- `/f <file>` toggles file logging.
- `go` / `g` exits command mode; `exit` terminates the program.

Important behavior:
- Logging to screen is disabled while in command mode, then restored according to `NextLogToScreen`.
- `ListDevices` enumerates filter volumes, maps volume names to DOS names, and calls `IsAttachedToVolume` for each.
- `IsAttachedToVolume` enumerates instances per volume and counts those whose filter name equals `MiniSpy`.
- Cleanup sets `CleaningUp`, waits for the logging thread to release the shutdown semaphore, closes file/port/thread/semaphore handles.

Dependencies and risks:
- Depends on `fltUser.h` volume/instance APIs and `mspyLog.c` for log retrieval.
- Command parsing is space-delimited and fixed-buffer based; there is no quoting support for file names with spaces.
- The `/f` path sets `LogToFile` after `fopen_s` even if the open fails in non-debug builds, which is sample-quality error handling.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyUser.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/nullFilter/nullFilter.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/nullFilter/nullFilter.c

Minimal null minifilter sample.

Key responsibilities:
- Defines `NULL_FILTER_DATA` with only the registered filter handle.
- Registers a `FLT_REGISTRATION` with no operation callbacks and no context registrations.
- Starts filtering in `DriverEntry`.
- Unregisters in `NullUnload`.
- Allows explicit/manual instance teardown in `NullQueryTeardown`.

Important behavior:
- Because `Operation callbacks` is `NULL`, this filter observes no I/O operations.
- The sample is primarily a skeleton for registration, start, unload, and instance-teardown plumbing.
- `DriverEntry` unregisters the filter if `FltStartFiltering` fails.

Dependencies and risks:
- Depends only on standard FltMgr kernel APIs.
- The code asserts registration success but also handles failure through status returns.
- There is no per-instance or per-operation state.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/nullFilter/nullFilter.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/passThrough/passThrough.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/passThrough/passThrough.c

Pass-through minifilter sample that registers broad pre/post callbacks without changing I/O.

Key responsibilities:
- Registers callbacks for most standard IRP operations, FSFilter callbacks, Fast I/O-style operations, network query open, MDL operations, and volume mount/dismount.
- Uses `PtPreOperationPassThrough` and `PtPostOperationPassThrough` for normal pass-through operations.
- Uses `PtPreOperationNoPostOperationPassThrough` for shutdown, where post callbacks are unsupported.
- Registers instance setup, query teardown, teardown start, teardown complete, and unload routines.
- Optionally requests operation-status callbacks for oplock and directory-change notification operations.

Important behavior:
- `DriverEntry` registers the filter and starts filtering; failure after registration unregisters the filter.
- Instance setup and detach query always return success.
- Pre-operation callback returns `FLT_PREOP_SUCCESS_WITH_CALLBACK` for registered post operations.
- Post-operation callback simply returns `FLT_POSTOP_FINISHED_PROCESSING`.
- `PtDoRequestOperationStatus` requests status callbacks for oplock FSCTLs and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`.

Dependencies and risks:
- Depends on `fltKernel.h` and FltMgr callback semantics.
- `gTraceFlags` defaults to zero, so debug tracing is silent unless changed.
- `OperationStatusCtx` is incremented without synchronization; it is only diagnostic context in this sample.
- The file is useful as a callback-coverage template, not as a policy filter.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/passThrough/passThrough.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/filter/scanner.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/filter/scanner.c

Kernel-mode scanner minifilter sample that asks a user-mode service whether scanned data is safe.

Key responsibilities:
- Registers create, cleanup, write, and Win8+ file-system-control callbacks.
- Registers a stream-handle context containing `RescanRequired`.
- Creates secured communication port `\\ScannerPort`, limited to one client.
- Reads the `Extensions` registry multi-string from the service `Parameters` key and falls back to scanning `.doc` if unavailable.
- Scans target files on open, scans write buffers before regular writes complete, rescans write-opened files on cleanup, and blocks offload writes for interested handles.

Initialization and configuration:
- `DriverEntry` opts into `NonPagedPoolNx`, registers with FltMgr, initializes scanned extensions, builds a default admin/system security descriptor, creates the communication port, then starts filtering.
- `ScannerOpenServiceParametersKey` prefers `IoOpenDriverRegistryKey` when available and falls back to manually opening the service `Parameters` subkey.
- `ScannerInitializeScannedExtensions` reads `Extensions`, counts REG_MULTI_SZ entries, allocates an array of `UNICODE_STRING`s, and copies each extension.
- `ScannerFreeExtensions` releases configured extension strings and handles the static default extension specially.

I/O behavior:
- `ScannerPreCreate` skips post-create scanning for the trusted connected user process.
- `ScannerPostCreate` ignores failed/reparse creates, gets normalized name info, checks extension match, reads/scans the file through user mode, denies open with `FltCancelFileOpen` on unsafe content, and marks write-access handles for cleanup rescan.
- `ScannerPreCleanup` rescans handles whose stream-handle context requires it and logs unsafe detection.
- `ScannerPreWrite` sends up to `SCANNER_READ_BUFFER_SIZE` bytes from the write buffer to user mode; unsafe nonpaging writes are completed with `STATUS_ACCESS_DENIED`.
- `ScannerPreFileSystemControl` blocks `FSCTL_OFFLOAD_WRITE` for interested handles because the sample cannot inspect offloaded data.
- `ScannerpScanFileInUserMode` reads the beginning of the file with noncached aligned I/O and sends it to the user service.

Communication model:
- `ScannerPortConnect` stores the client port and current process as trusted `UserProcess`.
- `ScannerPortDisconnect` closes the client port and clears `UserProcess`.
- `FltSendMessage` uses the same notification buffer as the reply storage; reply length is `sizeof(SCANNER_REPLY)`.

Dependencies and risks:
- Depends on `scanuk.h` shared messages, `scanner.h` globals/context, FltMgr communication ports, stream-handle contexts, and file-name parsing.
- Failing to contact user mode generally allows opens/writes, avoiding bootstrapping failures but weakening enforcement.
- The sample explicitly notes that large nonpaged allocations and scanning only the first chunk are not production-quality.
- Memory-mapped writes are not blocked in the write path; cleanup scanning can only detect after the fact.
- Registry parsing does not deeply validate the value type/format beyond query success.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/filter/scanner.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/filter/scanner.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/filter/scanner.h

Kernel-only scanner minifilter header.

Key contents:
- Defines `SCANNER_DATA`, the global driver state: driver object, filter handle, server port, trusted user process, and client port.
- Declares external global `ScannerData`.
- Defines `SCANNER_STREAM_HANDLE_CONTEXT` with `BOOLEAN RescanRequired`.
- Defines unused/placeholder `SCANNER_CREATE_PARAMS` with a zero-length `WCHAR String[0]`.
- Declares `DriverEntry`, unload, teardown query, create/post-create, cleanup, write, Win8+ file-system-control, and instance setup routines.

Important behavior:
- The stream-handle context is the driver’s main per-open state and controls cleanup rescanning.
- Function prototypes match the FltMgr callback signatures used in `scanner.c`.

Dependencies and risks:
- The module comment says `scrubber.h`, but the guard and file role are scanner-specific.
- `SCANNER_DATA.DriverObject` is defined here, though this source file does not use it meaningfully.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/filter/scanner.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/inc/scanuk.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/inc/scanuk.h

Shared scanner kernel/user communication header.

Key contents:
- Defines communication port name `\\ScannerPort`.
- Sets `SCANNER_READ_BUFFER_SIZE` to 1024 bytes.
- Defines `SCANNER_NOTIFICATION`, containing `BytesToScan`, padding/reserved space, and a 1024-byte `Contents` buffer.
- Defines `SCANNER_REPLY`, containing `BOOLEAN SafeToOpen`.

Important behavior:
- The kernel sends `SCANNER_NOTIFICATION` to user mode and expects `SCANNER_REPLY` indicating whether the content is safe.
- The fixed 1024-byte payload bounds both file-start scanning and write-buffer scanning.

Dependencies and risks:
- This is an ABI header shared by both `scanner.sys` and `scanuser.exe`; field layout and packing expectations must remain synchronized.
- The port-name definition is included in separate kernel/user binaries, so duplicate definition is not an issue in this sample layout.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/inc/scanuk.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/user/scanUser.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/user/scanUser.c

User-mode scanner service sample that receives scan requests and replies to the minifilter.

Key responsibilities:
- Connects to `\\ScannerPort`.
- Associates the filter communication port with an I/O completion port.
- Starts configurable worker threads and posts configurable outstanding `FilterGetMessage` requests per thread.
- Scans received buffers for the literal byte string `"foul"`.
- Replies with `SafeToOpen = FALSE` when the string is found.

Important behavior:
- Defaults to 5 outstanding requests per thread and 2 worker threads; allows 1 to 64 threads.
- `ScannerWorker` dequeues overlapped completions, identifies the containing `SCANNER_MESSAGE`, scans `Notification.Contents`, replies with `FilterReplyMessage`, clears the `OVERLAPPED`, and reposts `FilterGetMessage`.
- Multiple outstanding messages can complete in any order, so each message embeds its own `OVERLAPPED`.
- The main thread waits for workers and exits when workers fail or the port disconnects, commonly because the filter unloaded.

Dependencies and risks:
- Depends on `fltuser.h`, `scanuk.h`, and `scanuser.h`.
- `ScanBuffer` is an intentionally simple sample search algorithm, not production malware scanning.
- If `BufferSize` is smaller than the search string length, the pointer arithmetic in the loop condition is fragile sample code.
- There is no explicit graceful shutdown command; normal termination depends on port closure/error.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/user/scanUser.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/user/scanuser.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/user/scanuser.h

User-mode scanner messaging header.

Key contents:
- Applies `#pragma pack(1)` for message structures.
- Defines `SCANNER_MESSAGE`:
  - `FILTER_MESSAGE_HEADER MessageHeader`
  - `SCANNER_NOTIFICATION Notification`
  - embedded `OVERLAPPED Ovlp`
- Defines `SCANNER_REPLY_MESSAGE`:
  - `FILTER_REPLY_HEADER ReplyHeader`
  - `SCANNER_REPLY Reply`

Important behavior:
- `SCANNER_MESSAGE` embeds `OVERLAPPED` for asynchronous `FilterGetMessage` calls but excludes it from the message length by passing `FIELD_OFFSET(SCANNER_MESSAGE, Ovlp)`.
- `SCANNER_REPLY_MESSAGE` wraps the scanner-specific reply in the required filter-manager reply header.

Dependencies and risks:
- Depends on `scanuk.h` for scanner payload structures and `fltuser.h` for filter-manager message headers.
- Packing affects structure layout; kernel/user communication must use the same expected header and payload sizes.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/user/scanuser.h -->