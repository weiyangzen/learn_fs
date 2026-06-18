# Group Research: group_1848_windows_driver_samples_sources_windows_windows_driver_samples_files_1c2cffd761b9

Scope confirmed against `Docs/research_subset_a.md`. All seven listed NameChanger minifilter source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncfsctrl.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncfsctrl.c

## Purpose

`ncfsctrl.c` handles user-visible filesystem control results that expose paths or file names. Its job is to preserve the NameChanger illusion: when lower filesystem FSCTLs return paths under the real mapping, this file rewrites, filters, or injects records so callers see the configured user mapping.

## Main Areas

- `NcStreamHandleContextFindBySidCreate` / `NcStreamHandleContextFindBySidClose` initialize and tear down the `FSCTL_FIND_FILES_BY_SID` state embedded in each stream-handle context.
- `NcFindFilesBySidTranslateBuffers` rewrites `FILE_NAME_INFORMATION` records from filesystem-relative names to user-relative names. It builds full names from the opened/query root, compares against the real mapping, optionally constructs user-mapping replacements, suppresses real-mapping entries when required, and tracks partial input/output consumption.
- `NcPreFindFilesBySid` decides whether `FSCTL_FIND_FILES_BY_SID` needs filtering, translation, or injected enumeration from the real mapping. It attaches/locks stream-handle context state, drains buffered leftovers, may retarget the request to the real mapping file object, and completes early for buffer or context errors.
- `NcPostFindFilesBySid` copies volatile METHOD_NEITHER output into a stable system buffer, translates returned records, buffers overflow remnants, and when needed opens the real mapping directory to inject additional results via `FltFsControlFile`.
- `NcPostLookupStreamFromCluster` rewrites Win7+ `LOOKUP_STREAM_FROM_CLUSTER_OUTPUT` entries. It translates absolute real-mapping paths to user-mapping paths, preserves match counts, recomputes required buffer size, and may return fewer records if names grow.
- `NcUsnTranslateBuffers` rewrites USN v2.0 records whose parent file reference and final component identify the real mapping. It changes the parent ID to the user mapping parent ID and substitutes the user mapping link name.
- `NcPostReadFileUsnData`, `NcPostEnumUsnData`, `NcPostReadUsnJournalWorker`, and `NcPostReadUsnJournal` apply USN translation to `FSCTL_READ_FILE_USN_DATA`, `FSCTL_ENUM_USN_DATA`, and `FSCTL_READ_USN_JOURNAL`. They open/query both mapping parents for `FileInternalInformation`, copy user buffers into stable storage, then rewrite records after the leading `USN` cursor where applicable.

## Integration

The file is called from the central FSCTL callbacks in `nc.c`. It depends on mapping/path helpers from `ncmapping.c` and `ncpath.c`, generic helpers from `nchelper.c`, and stream-handle context locking/attachment from `nccontext.c`. It uses Filter Manager primitives (`FltGetInstanceContext`, `FltLockUserBuffer`, `FltFsControlFile`, `FltQueueGenericWorkItem`) and kernel object lifetime management (`FltClose`, `ObDereferenceObject`).

## Important Safety Behavior

- Treats METHOD_NEITHER output as volatile and untrusted; it probes, locks MDLs when present, catches access exceptions, and copies filesystem output before parsing.
- Uses safe integer arithmetic before walking variable-length buffers.
- Defers `FSCTL_READ_USN_JOURNAL` post-processing to a generic work item to avoid reentering the filesystem while top-level IRP/filesystem locks may still be held.
- Only understands USN records with major version 2 and minor version 0; incompatible versions return `STATUS_NOT_IMPLEMENTED`.
- Complexity risk is high around concurrent `FSCTL_FIND_FILES_BY_SID` requests sharing one handle: leftover buffers, real mapping handles, and outstanding request counts must remain synchronized under the stream-handle lock.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncfsctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nchelper.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nchelper.c

## Purpose

`nchelper.c` contains small cross-cutting helpers used across the NameChanger minifilter.

## Functions

- `NcGetFileNameInformation` wraps `FltGetFileNameInformation` and `FltGetFileNameInformationUnsafe`, selecting the safe callback-data path when `Data` is available and the unsafe file-object/instance path otherwise.
- `NcAllocateEResource` allocates a nonpaged `ERESOURCE`, initializes it with `ExInitializeResourceLite`, and cleans up correctly on partial failure.
- `NcFreeEResource` deletes and frees an `ERESOURCE` allocated by `NcAllocateEResource`.
- `NcCreateFileHelper` wraps `NcCreateFileEx2`. On Longhorn+ builds it initializes `IO_DRIVER_CREATE_CONTEXT` and propagates transaction parameters from a parent file object so internal creates remain transaction-aware.
- `NcSetCancelCompletion` synchronizes cancellation callback setup with the global cancel spin lock and returns `STATUS_CANCELLED` if the operation was already canceled.
- `NcExceptionFilter` centralizes exception filtering for user-buffer access. Unexpected exceptions continue searching unless the caller explicitly says it was accessing user memory.

## Integration

These helpers are used by FSCTL, directory enumeration/notification, file information, mapping, and name-provider paths. The create helper is especially important for internal opens of mapping parents and real-mapping directories.

## Risks and Notes

The file is intentionally low-level. Correct call-site discipline matters: callers must release file-name information, free allocated resources, and only pass user-buffer exceptions through `NcExceptionFilter` when they are intentionally probing or copying user memory.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nchelper.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncinit.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncinit.c

## Purpose

`ncinit.c` initializes global mapping configuration from the driver service registry parameters and validates the assumptions NameChanger requires before the filter starts.

## Functions

- `NcLoadRegistryString` reads a `REG_SZ` value from a registry key, retrying if the value size changes between length query and data query. It rejects non-strings, empty strings, and strings too large for `UNICODE_STRING`, then copies the non-null-terminated content into nonpaged pool.
- `NcIs8DOT3Compatible` validates configured short names using `RtlIsNameLegalDOS8Dot3`, disallows spaces, tildes, path separators, and lowercase characters, and ensures a long name that is also 8.3-compatible matches the configured short name exactly.
- `NcGetIoOpenDriverRegistryKey` dynamically resolves `IoOpenDriverRegistryKey` via `MmGetSystemRoutineAddress` for OS-version compatibility.
- `NcOpenServiceParametersKey` opens the service `Parameters` key using `IoOpenDriverRegistryKey` when available, otherwise falls back to opening the service registry path then the `Parameters` subkey.
- `NcInitializeMapping` zeroes `NcGlobalData`, opens service parameters, loads `UserMapping`, `UserMappingFinalComponentShort`, and `RealMapping`, splits full mapping paths into parent/final components, rejects paths with adjacent backslashes or invalid roots/final components, and validates the strict short-name assumptions.

## Configuration Contract

Expected registry values are volume-relative absolute paths for user and real mappings plus a user short final component. Paths must start with `\`, include a parent and final component, have no trailing slash final component, and avoid empty path components.

## Integration

The parsed global strings are later used during instance setup in `nc.c`, where volume-specific `NC_MAPPING` structures are built from the configured parent/final component strings.

## Risks and Notes

The sample assumes the real mapping final component is 8.3-compatible and has only one configured real component form. That is explicitly called out as a sample simplification, not a general product-ready mapping model.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncinit.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncmapping.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncmapping.c

## Purpose

`ncmapping.c` builds, initializes, validates, and tears down runtime mapping structures. A mapping path stores multiple `UNICODE_STRING` views over one allocated full-path buffer: full path, volume path, parent path, final component, and volume-less path.

## Functions

- `NcIsMappingPathZeroed`, `NcInitMappingPath`, and `NcTeardownMappingPath` manage a single `NC_MAPPING_PATH`.
- `NcBuildMappingPath` combines a volume name, mapping parent path, and final component into one full path allocation. It sets all string slices and counts backslash components in volume and full path for later overlap tests.
- `NcBuildMappingPathFromVolume` queries a `PFLT_VOLUME` name with `FltGetVolumeName` and builds a mapping path from that volume plus configured parent/final strings.
- `NcBuildMappingPathFromFile` queries a parent `FILE_OBJECT` name, chooses opened or normalized form, parses it, then builds the mapping path with a supplied final component.
- `NcIsMappingEntryZeroed`, `NcInitMappingEntry`, and `NcTeardownMappingEntry` manage long/short path pairs. Teardown avoids double-freeing when long and short entries share the same buffer.
- `NcIsMappingZeroed`, `NcInitMapping`, `NcTeardownMapping`, and `NcBuildMapping` manage a complete real/user mapping pair. `NcBuildMapping` builds the real normalized path, aliases real short to real long, then builds user short opened and user long normalized paths.

## Integration

The component counts and string slices built here are consumed by `NcComparePath`, name generation, create redirection, directory enumeration, notification merging, file information rewriting, and FSCTL result rewriting.

## Risks and Notes

The implementation relies on ownership invariants: each `NC_MAPPING_PATH.FullPath.Buffer` owns the allocation, and other fields are slices. Accidental independent freeing of slice fields would be invalid. Real long and short paths can intentionally alias the same buffer.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncmapping.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncnameprov.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncnameprov.c

## Purpose

`ncnameprov.c` implements NameChanger’s Filter Manager name-provider callbacks. It rewrites generated names and normalized path components so callers above the filter receive user-mapping names even when the underlying filesystem object lives under the real mapping.

## Functions

- `NcGenerateFileName` handles opened, normalized, and short name generation. It queries lower providers without requesting from the current provider to avoid recursion, parses the lower name, determines pre-open vs opened case sensitivity, compares the lower name against the real mapping, and returns either the lower name or a constructed user-mapping name.
- For opened/normalized names, opened objects inside the real mapping are translated to the user mapping with `NcConstructPath`.
- For short-name requests, an exact real-mapping match returns the configured user short final component directly; otherwise the function queries the lower provider’s short name.
- `NcNormalizeNameComponentEx` supports normalized-name component expansion. It translates parent directories inside the user mapping to the real mapping before opening/enumerating, handles the user mapping’s parent plus mapping final component specially, calls `NcQueryDirectoryFile`, and if the real component was queried returns the user long final component in the expansion buffer.

## Integration

The callbacks are registered through `nc.c` name-provider glue. They depend on instance mapping context, path overlap classification, internal create helper, and directory-query support.

## Risks and Notes

Pre-open name generation is deliberately marked `FLT_FILE_NAME_DO_NOT_CACHE` to avoid poisoning lower name caches before NameChanger’s create redirection has run. The component-normalization path has comments noting that only specific return codes should be used if name construction should continue.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncnameprov.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncoffsets.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncoffsets.c

## Purpose

`ncoffsets.c` provides a generic access layer over several directory-query and directory-notification record formats. NameChanger uses it to rewrite directory entries without duplicating structure-specific pointer arithmetic.

## Functions

- `NcDetermineStructureOffsets` fills `DIRECTORY_CONTROL_OFFSETS` for supported directory information classes: `FileBothDirectoryInformation`, `FileDirectoryInformation`, `FileFullDirectoryInformation`, `FileIdBothDirectoryInformation`, `FileIdFullDirectoryInformation`, and `FileNamesInformation`. It records offsets for `NextEntryOffset`, file-name length, file-name buffer, and optional short-name fields.
- `NcCalculateDirectoryNotificationOffsets` creates equivalent offsets for `FILE_NOTIFY_INFORMATION`.
- `NcGetNextEntryOffset`, `NcGetNextEntry`, `NcGetFileNameLength`, `NcGetEntrySize`, `NcGetFileName`, `NcGetShortName`, and `NcGetShortNameLength` read common fields using the offset table.
- `NcSetNextEntryOffset`, `NcSetFileName`, and `NcSetShortName` update records after munging names. `NcSetNextEntryOffset` can force a record to become the last entry.

## Integration

Directory enumeration and notification code use this file to parse, filter, inject, and rewrite entries for the user/real mapping relationship. It is not a validator; callers are responsible for ensuring buffers are large and well-formed enough before using these helpers.

## Risks and Notes

Record size calculation for the last entry depends on `FileNameDist + FileNameLength`, while non-last entries trust `NextEntryOffset`. Bad or malicious buffers must be handled before or around these helpers.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncoffsets.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncpath.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncpath.c

## Purpose

`ncpath.c` is the core path comparison and construction module for NameChanger. It determines how a candidate name overlaps a mapping and constructs rewritten paths from a mapping plus remainder.

## Functions

- `NcComparePath` compares an input name against a mapping entry’s long and short paths. It can compare full device-qualified paths or volume-relative paths. It classifies overlap into flags such as `InMapping`, `Match`, `Peer`, `Parent`, and `Ancestor`, and optionally returns the unmatched remainder after the mapping.
- The comparison is component-based, honors case sensitivity, treats `\` and `:` as terminators for input components, compares both long and short mapping components in parallel, and uses component counts from `NC_MAPPING_PATH` to decide final relationship.
- `NcConstructPath` builds a new path from a mapping entry and a remainder. It can include or omit the volume prefix, inserts a separator only when the remainder is non-empty, checks the `MAXUSHORT` `UNICODE_STRING` limit, and allocates the result from paged pool with `NC_GENERATE_NAME_TAG`.
- `NcParseFinalComponent` splits a configured volume-relative absolute path into parent path and final component. It keeps root parent paths as `\`, rejects paths without separators or with empty final components, and allocates both returned strings from nonpaged pool.

## Integration

Nearly every NameChanger behavior depends on this file: create redirection, name generation, directory enumeration, notifications, hard links, renames, set-link operations, and FSCTL result rewriting.

## Risks and Notes

`NcComparePath` is intentionally semantic rather than a simple prefix check. Its correctness depends on valid mapping component counts and on callers choosing the correct `ContainsDevice` setting. `NcConstructPath` may make otherwise valid on-disk names inaccessible if mapping expansion pushes the generated path beyond `UNICODE_STRING` length limits.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncpath.c -->