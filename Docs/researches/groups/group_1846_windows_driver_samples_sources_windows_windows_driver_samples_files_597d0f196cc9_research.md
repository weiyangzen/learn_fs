# Group Research: group_1846_windows_driver_samples_sources_windows_windows_driver_samples_files_597d0f196cc9

Scope checked against `Docs/research_subset_a.md`: `sources/windows/windows-driver-samples` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nc.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nc.c

This is the main NameChanger minifilter module. It registers the filter, operation callbacks, context types, and name-provider callbacks, and it owns instance attach validation plus global unload cleanup.

Key responsibilities:
- Defines `Callbacks[]` for create, cleanup, query/set information, directory control, network query open, and filesystem control.
- Defines `contextRegistration[]` for `FLT_INSTANCE_CONTEXT` and `FLT_STREAMHANDLE_CONTEXT`.
- Defines `FilterRegistration`, wiring unload, instance setup/teardown, generated name, and name normalization callbacks.
- Owns global driver state through `NC_GLOBAL_DATA NcGlobalData`.

`DriverEntry` initializes compatibility shims with `NcCompatInit`, loads mapping configuration with `NcInitializeMapping`, registers with Filter Manager, then starts filtering. On failed start it unregisters the filter.

`NcInstanceSetup` is the central attach gate. It refuses ReFS because the sample does not handle ReFS V3 USN records, refuses automatic attachment, and requires initialized registry mapping strings. It builds per-volume user and real mapping paths, verifies the user mapping final component does not already exist in either short or long form, verifies the real mapping parent exists, allocates an instance context, builds normalized/short mapping state with `NcBuildMapping`, rejects overlapping real/user mappings, records filesystem type, and stores the context on the instance.

Create/query/set/directory/fsctl callbacks in this file mostly dispatch into feature-specific modules:
- Create path: `NcPreCreate` in `nccreate.c`.
- Directory enumeration and notifications: `NcEnumerateDirectory`, `NcPreNotifyDirectory`, `NcPostNotifyDirectory`.
- File information name fixups: `NcPreQueryAlternateName`, `NcPostQueryName`, `NcPostQueryHardLinks`, rename/link/disposition/short-name handlers.
- FSCTL name fixups: USN, find-by-SID, stream lookup, read journal handlers.
- Name provider: `NcGenerateFileName`, `NcNormalizeNameComponentEx`.

Cleanup handling is synchronized so post-cleanup can safely tear down per-handle notification state through `NcStreamHandleContextNotCleanup`.

`NcPreNetworkQueryCallback` disallows fast I/O for network query opens; the TODO notes these should eventually flow through create-like processing.

Important dependencies:
- `nc.h` for all shared structures and declarations.
- `nccompat.c` for runtime-selected kernel/FltMgr APIs.
- `ncmapping.c`, `ncpath.c`, `ncinit.c`, `ncnameprov.c`, `ncfileinfo.c`, `ncfsctrl.c`, `ncdirenum.c`, `ncdirnotify.c`.

Notable behavior:
- Real mapping paths are hidden from callers; user mapping paths are virtualized and redirected.
- Instance setup deliberately checks both long and short user final components to avoid collisions.
- Deletes on mapping ancestors are constrained elsewhere, but attach itself documents races with `FILE_DELETE_ON_CLOSE`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nc.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nc.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nc.h

This is the shared interface and data-model header for the NameChanger minifilter. It defines allocation tags, compatibility function pointer types, path/mapping structures, per-instance and per-handle contexts, directory-entry offset helpers, global data, and cross-module function declarations.

Core structures:
- `NC_MAPPING_PATH`: precomputed full, volume, parent, final-component, and volumeless names plus component counts.
- `NC_MAPPING_ENTRY`: long-name and short-name mapping path pair.
- `NC_MAPPING`: real mapping plus user mapping.
- `NC_PATH_OVERLAP`: flags describing whether a path is an ancestor, parent, exact match, inside mapping, or peer.
- `NC_INSTANCE_CONTEXT`: per-volume mapping plus attached filesystem type.
- `NC_DIR_QRY_CONTEXT`: per-handle directory enumeration cache, injection entry, search string, information class, and outstanding flag.
- `NC_DIR_NOT_CONTEXT`: per-handle directory notification forwarding/merge state.
- `NC_FIND_BY_SID_CONTEXT`: state for `FSCTL_FIND_FILES_BY_SID`, including real handle and buffered results.
- `NC_STREAM_HANDLE_CONTEXT`: shared per-handle lock plus directory query, notification, and find-by-SID state.

The header also defines `DIRECTORY_CONTROL_OFFSETS`, used to generically inspect and edit the multiple directory information buffer formats returned by Windows filesystems.

Compatibility declarations abstract OS-version differences:
- `NcReplaceFileObjectName`
- `NcQueryDirectoryFile`
- `NcCreateFileEx2`
- `NcGetNewSystemBufferAddress`

The function declaration sections define the module boundaries:
- `nchelper.c`: name querying, resource allocation, create helper, cancel completion, exception filter.
- `ncmapping.c`: mapping initialization, build, teardown.
- `ncinit.c`: registry mapping initialization.
- `ncpath.c`: path comparison, construction, final-component parsing.
- `nccontext.c`: context allocation/close routines.
- `nccreate.c`: create redirection.
- `ncnameprov.c`: generated and normalized names.
- `ncoffsets.c`: directory information buffer accessors/mutators.
- `ncdirenum.c`: directory enumeration injection/filtering.
- `ncdirnotify.c`: directory notification forwarding.
- `ncfileinfo.c`: file information name fixups and set-information guards.
- `ncfsctrl.c`: FSCTL result/name fixups.

Notable details:
- The driver relies on precomputed mapping paths rather than reparsing mapping configuration for every operation.
- Per-handle locking uses an `ERESOURCE` allocated in the stream handle context.
- Directory enumeration and notifications share the stream handle context but keep separate subcontexts.
- Some declarations are duplicated for `NcIsMappingZeroed` and `NcInitMapping`; this is harmless but redundant.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccompat.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccompat.c

This file provides runtime compatibility shims so the sample can run across multiple Windows/FltMgr versions. It resolves newer APIs dynamically and falls back to local implementations when unavailable.

Global function pointers initialized here:
- `NcReplaceFileObjectName`
- `NcQueryDirectoryFile`
- `NcCreateFileEx2`
- `NcGetNewSystemBufferAddress`
- Internal fallback pointer `NcCreateFileEx`

`NcReplaceFileObjectNameAlternate` replaces `FileObject->FileName` on systems without `IoReplaceFileObjectName`. If the existing buffer is large enough it zeroes and reuses it; otherwise it allocates a new paged-pool buffer and frees the old one. The comments note verifier can report false pool leaks on older systems because this bypasses the newer kernel helper.

`NcQueryDirectoryFileAlternate` emulates `FltQueryDirectoryFile` by allocating callback data, setting up an `IRP_MJ_DIRECTORY_CONTROL / IRP_MN_QUERY_DIRECTORY` operation, applying `SL_RESTART_SCAN` and `SL_RETURN_SINGLE_ENTRY` as needed, performing synchronous I/O, optionally returning bytes read, then freeing callback data.

`NcCreateFileEx2Alternate` emulates `FltCreateFileEx2`. It rejects transaction/create-context support by assertion, uses `FltCreateFileEx` if available, otherwise falls back to `FltCreateFile` and optionally references the returned file object by handle. On failure it closes/dereferences partial outputs.

`NcCompatInit` opts into NX nonpaged pool where supported, resolves `IoReplaceFileObjectName` through `MmGetSystemRoutineAddress`, resolves FltMgr routines through `FltGetRoutineAddress`, and installs fallbacks as needed.

Important dependencies:
- Used by `DriverEntry` before mapping initialization and filter registration.
- The rest of the driver calls the function pointers directly, avoiding scattered OS-version checks.

Notable behavior:
- Transaction/ECP support depends on real `FltCreateFileEx2`; fallback asserts that `DriverContext == NULL`.
- `NcGetNewSystemBufferAddress` may remain `NULL` if unavailable; callers must tolerate that.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccompat.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccontext.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccontext.c

This file manages lifetime for instance contexts and stream handle contexts.

`NcInstanceContextClose` is the `FLT_INSTANCE_CONTEXT` cleanup callback. It asserts the context type and tears down the mapping with `NcTeardownMapping`.

`NcStreamHandleContextClose` is the `FLT_STREAMHANDLE_CONTEXT` cleanup callback. It tears down all per-handle feature state:
- Directory enumeration context via `NcStreamHandleContextEnumClose`.
- Directory notification context via `NcStreamHandleContextNotClose`.
- Find-by-SID context via `NcStreamHandleContextFindBySidClose`.
- Shared `ERESOURCE` lock via `NcFreeEResource`.

`NcStreamHandleContextAllocAndAttach` allocates or retrieves a stream handle context for a file object. It first tries `FltGetStreamHandleContext`; if one exists, it returns that referenced context. Otherwise it allocates a paged-pool stream handle context, zeroes it, allocates the shared lock, initializes notification/enumeration/find-by-SID subcontexts, and attaches it with `FLT_SET_CONTEXT_KEEP_IF_EXISTS`.

Race handling:
- If another thread attaches a context first, `FltSetStreamHandleContext` returns `STATUS_FLT_CONTEXT_ALREADY_DEFINED`; the function converts this to success, returns the existing context, and releases the newly allocated one.
- The function guarantees the returned context has one reference that the caller must release.

Important dependencies:
- Used by directory enumeration, directory notifications, and find-by-SID handling whenever per-handle state is needed.
- Cleanup callbacks depend on each submodule’s close routine being idempotent on zeroed/empty state.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccontext.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccreate.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccreate.c

This file implements pre-create namespace redirection. Its job is to hide the real mapping and redirect opens under the user mapping to the real backing location.

`NcPreCreate` early-passes operations that are name-agnostic or unsupported for virtualization:
- Paging file opens.
- Volume opens.
- Opens by file ID.

It obtains the opened name with `FLT_FILE_NAME_OPENED | FLT_FILE_NAME_QUERY_DEFAULT | FLT_FILE_NAME_DO_NOT_CACHE`, parses it, retrieves the instance context, and compares the opened path against both real and user mappings.

Real mapping behavior:
- Exact open of the real mapping is completed without reaching the filesystem.
- `FILE_OPEN` and `FILE_OVERWRITE` get `STATUS_OBJECT_NAME_NOT_FOUND`.
- Create-like dispositions get `STATUS_ACCESS_DENIED`.
- Descendants under the real mapping get `STATUS_OBJECT_PATH_NOT_FOUND`.
This preserves the illusion that the real location is not visible.

Delete protection:
- If `FILE_DELETE_ON_CLOSE` is used on an ancestor of either mapping, the open is denied. This prevents users from deleting/renaming mapping ancestors and invalidating cached long/short-name assumptions.

User mapping behavior:
- If the opened path is inside the user mapping, the remainder under the user mapping is calculated.
- For `SL_OPEN_TARGET_DIRECTORY`, the code temporarily clears the flag and requeries the full opened name including the final component, then restores the flag.
- It constructs the corresponding real path with `NcConstructPath`.
- It replaces the file object name through `NcReplaceFileObjectName`.
- It clears `RelatedFileObject` because the new name is already full.
- It lets the create continue to the filesystem with the munged real name.

Important dependencies:
- `NcComparePath` determines mapping overlap.
- `NcConstructPath` builds the redirected real path.
- `NcReplaceFileObjectName` is supplied by `nccompat.c`.
- Instance mapping state is built during `NcInstanceSetup`.

Notable behavior:
- The opened name is intentionally queried without going through the filter’s own name provider to avoid converting real names back to user names and poisoning lower name caches.
- No post-create callback is required; the visible name illusion is maintained by name-provider and information-query paths elsewhere.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccreate.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncdirenum.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncdirenum.c

This file implements directory enumeration virtualization. It suppresses the real mapping from listings and injects a synthetic user mapping entry when enumerating relevant parent directories.

`NcEnumerateDirectory` handles `IRP_MN_QUERY_DIRECTORY` in pre-operation. It:
- Determines structure offsets for the requested directory information class.
- Gets the instance context and opened directory name.
- Compares the directory against user and real mappings.
- Passes through unless the enumerated directory is the parent of either mapping.
- Allocates/attaches a stream handle context.
- Serializes per-handle enumeration with `EnumerationOutstanding`.
- Sets up or resets enumeration state through `NcStreamHandleContextEnumSetup`.
- Populates an internal cache from the filesystem using `NcPopulateCacheEntry`.
- Chooses between cached filesystem entries and a synthetic injection entry with `NcDirEnumSelectNextEntry`.
- Skips real mapping entries with `NcSkipName`.
- Copies selected entries into the caller’s buffer with `NcCopyDirEnumEntry`.
- Completes the query itself with success, `STATUS_NO_SUCH_FILE` on first empty query, or `STATUS_NO_MORE_FILES` later.

`NcEnumerateDirectorySetupInjection` builds the synthetic user mapping entry. It checks the caller’s search pattern first; if neither the long nor short user final component matches, no injection is needed. Otherwise it opens the real mapping parent, queries the real mapping entry, rewrites the entry’s long and short names to the user mapping names, and stores the result as `InjectionEntry`.

`NcPopulateCacheEntry` reads ahead from the underlying filesystem into a paged-pool buffer. Empty filesystem statuses are converted to success with an empty cache so the merge logic can still return an injection entry if present.

`NcDirEnumSelectNextEntry` preserves approximate sort order by comparing the current cached filesystem entry name with the injection entry name and returning whichever sorts first.

`NcSkipName` suppresses the real mapping final component when enumerating the real mapping parent. It advances or frees the cache entry as needed.

`NcCopyDirEnumEntry` copies one entry into the user buffer, advances the source cache, and fixes `NextEntryOffset` when an entry becomes the last visible entry.

`NcStreamHandleContextEnumSetup` records the first search string and information class for a handle, enforces consistent information class on later queries, resets caches on first use or restart, and prepares injection when enumerating the user mapping parent.

`NcStreamHandleContextEnumClose` frees cached directory-entry buffers and saved search string.

Important dependencies:
- Offset accessors/mutators from `ncoffsets.c` let the code work across multiple directory information classes.
- `NcQueryDirectoryFile` comes from `nccompat.c`.
- Stream handle context allocation and locking come from `nccontext.c`.
- Search matching uses `FsRtlIsNameInExpression`.

Notable behavior:
- Multiple outstanding enumeration requests on the same handle are rejected with `STATUS_UNSUCCESSFUL`; the file has a TODO to improve this.
- The implementation is pre-operation and completes user queries itself rather than post-processing filesystem output.
- The code tries to preserve enumeration ordering while merging a single virtual entry.
- Pool tag usage is inconsistent in a few free paths: some buffers allocated with directory-query tags are freed with `NC_TAG`, while other paths use the specific tags.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncdirenum.c -->