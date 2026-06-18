# subset-b-007703 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_freelance.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_freelance.c

Purpose: implements the Windows OpenAFS "freelance" fake root volume. When `AFS_FREELANCE_CLIENT` is enabled, the cache manager synthesizes `/afs` from local mount point and symlink definitions instead of depending on a real root.afs volume.

Important APIs/types/functions: the file owns `cm_noLocalMountPoints`, `cm_localMountPoints`, `cm_FakeRootDir`, `cm_fakeDirSize`, `cm_Freelance_Lock`, `cm_localMountPointChangeFlag`, `cm_freelanceEnabled`, `cm_freelanceDiscovery`, `cm_freelanceImportCellServDB`, and `FakeFreelanceModTime`. `cm_InitFreelance()` initializes the lock, loads local entries, builds the fake directory, bumps `cm_data.fakeDirVersion`, and starts two registry notification threads. `cm_InitFakeRootDir()` materializes AFS directory pages from `cm_localMountPoint_t` entries. `cm_InitLocalMountPoints()` reads/migrates definitions from `HKLM\...\Freelance`, `HKLM\...\Freelance\Symlinks`, or legacy `afs_freelance.ini`. Add/remove/existence entry points are `cm_FreelanceAddMount`, `cm_FreelanceRemoveMount`, `cm_FreelanceMountPointExists`, `cm_FreelanceAddSymlink`, `cm_FreelanceRemoveSymlink`, and `cm_FreelanceSymlinkExists`. `cm_FreelanceFetchMountPointString()` and `cm_FreelanceFetchFileType()` populate scache metadata for fake-root children.

Control flow: initialization loads registry values, seeds default root-cell entries when empty, then encodes each mount point as `name#cell:volume.` or read/write `name%cell:volume.` and each symlink as `name:target.`. `cm_InitFakeRootDir()` computes the number of AFS directory pages needed, allocates or resizes `cm_FakeRootDir`, emits `.` and `..`, then assigns even vnode numbers and per-generation unique values for every entry. Registry notifier threads use `RegNotifyChangeKeyValue` and call `cm_noteLocalMountPointChange()` when mount or symlink keys change. Reinitialization invalidates old fake-root scaches under `cm_scacheLock` plus `cm_Freelance_Lock`, reloads entries, rebuilds the fake directory, reacquires root callbacks, and invalidates the redirector fake volume.

State and persistence: persistent configuration lives in registry values, with legacy INI import and deletion during migration. Runtime state lives in `cm_localMountPoints`, fake directory memory, fake-root scache state, and the change flag. `FakeFreelanceModTime` is derived from registry last-write time. `cm_data.fakeDirVersion` and `cm_data.fakeUnique` force cache coherency for rebuilt fake objects. Shutdown sets `freelance_ShutdownFlag` and signals notifier events.

Dependencies and integration: integrates with Windows registry APIs, OpenAFS cache-manager locks/scache/dir structures, cell lookup and CellServDB enumeration, redirector invalidation (`RDR_InvalidateVolume`), NLS comparisons (`cm_stricmp_utf8`), and pioctl callers in `cm_ioctl.c` for root mount point/symlink creation and deletion.

Risks: string parsing assumes separators exist in several registry paths; fixed buffers and `sprintf` require bounded registry values; allocation failures are mostly unchecked; lock ordering is subtle (`scache` before `freelance`); registry notifier setup can return silently if keys cannot be opened; fake FID generation depends on `fakeUnique` matching current local-entry indexes.

Test signals: empty registry should create root-cell defaults; registry and symlink key changes should trigger fake volume invalidation; add/remove should reject duplicates across mount points and symlinks; legacy INI migration should preserve entries; fake root directory page layout should survive many and long names; DFS-link symlink targets beginning `msdfs:` should become `CM_SCACHETYPE_DFSLINK`; shutdown should release notifier threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_freelance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_freelance.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_freelance.h

Purpose: declares the public freelance fake-root interface used by Windows cache-manager initialization, pioctl handling, scache metadata fetch, and optional CellServDB import.

Important APIs/types/functions: `cm_localMountPoint_t` stores a fake-root child name, a mount-point or symlink target string, and a cache-manager file type. Initialization and lifecycle APIs are `cm_InitLocalMountPoints`, `cm_InitFreelance`, `cm_FreelanceShutdown`, `cm_reInitLocalMountPoints`, and `cm_FreelanceImportCellServDB`. Change tracking is exposed with `cm_noteLocalMountPointChange`, `cm_getLocalMountPointChange`, and `cm_clearLocalMountPointChange`. Mutation and query APIs cover mount points and symlinks: `cm_FreelanceAddMount`, `cm_FreelanceRemoveMount`, `cm_FreelanceMountPointExists`, `cm_FreelanceAddSymlink`, `cm_FreelanceRemoveSymlink`, and `cm_FreelanceSymlinkExists`. Scache helpers are `cm_FreelanceFetchMountPointString`, `cm_FreelanceFetchFileType`, and `cm_FakeRootFid`.

State and persistence: exposes `FakeFreelanceModTime`, `cm_freelanceEnabled`, `cm_freelanceImportCellServDB`, and `cm_freelanceDiscovery`. Defines `AFS_FREELANCE_INI` for legacy migration and fake root cell/volume IDs as `0xFFFFFFFF`.

Dependencies and integration: depends on cache-manager types such as `cm_fid_t` and `cm_scache_t` supplied by surrounding headers. The header is consumed by `cm_freelance.c`, pioctl handlers in `cm_ioctl.c`, and fake-root aware cache and redirector paths.

Risks: the API passes mutable `char *` strings and does not encode buffer lengths; callers must honor the implementation's locking assumptions and fake-root FID conventions.

Test signals: compile coverage with `AFS_FREELANCE_CLIENT` enabled, pioctl add/remove flows, fake-root FID comparison, and scache mount-point/file-type fetches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_freelance.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_getaddrs.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_getaddrs.c

Purpose: caches VLDB `VL_GetAddrsU` results that map a file-server UUID and unique value to one or more server IP addresses, then appends those addresses to volume server arrays used by the Windows cache manager.

Important APIs/types/functions: private `uuid2addrsEntry_t` stores queue linkage, UUID, unique value, address count, XDR `bulkaddrs`, refcount, and delete flags. `cm_getaddrsFind()` looks up a usable cached entry where requested unique is not newer than cached unique. `cm_getaddrsAdd()` inserts or updates cache entries and owns/free-transfers the `bulkaddrs` payload. `cm_getaddrsPut()` decrements references. Public `cm_GetAddrsU()` performs cache lookup, VLDB RPC fallback, result caching, and output array population. `cm_getaddrsInit()` initializes `cm_getaddrsLock` once; `cm_getaddrsShutdown()` finalizes it.

Control flow: `cm_GetAddrsU()` first probes the hash table. On miss, it constructs `ListAddrByAttributes` with `VLADDR_UUID`, loops over VL servers through `cm_ConnByMServers`, invokes `VL_GetAddrsU`, and lets `cm_Analyze` retry/rotate servers. RPC errors are mapped with `cm_MapVLRPCError`; failures free the XDR address list and return `CM_ERROR_RETRY`. Successful replies clamp `nentries` to `bulkaddrs_len`, reject empty replies, and pass ownership into `cm_getaddrsAdd()`. The returned cached entry is copied into `serverFlags`, `serverNumber`, `serverUUID`, and `serverUnique` until `NMAXNSERVERS` is reached.

State and persistence: state is an in-memory 128-bucket hash table protected by `cm_getaddrsLock`; it is not persisted. XDR-allocated address arrays are freed when obsolete unreferenced entries are encountered or when duplicate/outdated input is discarded.

Dependencies and integration: integrates with OpenAFS queue helpers, jhash, RX/VL RPC stubs, connection selection and error analysis, `cm_cell_t` VL server lists, and volume-location code that maintains server arrays.

Risks: `cm_getaddrsPut()` mutates `refCount` under a read lock, which relies on local lock semantics and is easy to regress; delete flags exist but no public invalidation path is in this file; cache growth is only bounded by UUID churn and cleanup during later adds; callers must provide arrays sized for `NMAXNSERVERS` and a valid `index`.

Test signals: cache hit with older/equal unique should avoid RPC; newer unique should replace unused old data; duplicate/outdated RPC result should be freed; VLDB server failover should retry; empty address results should return invalid; output should stop exactly at `NMAXNSERVERS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_getaddrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_getaddrs.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_getaddrs.h

Purpose: declares the Windows cache-manager server-address discovery interface backed by the VLDB `GetAddrsU` RPC cache.

Important APIs/types/functions: `cm_GetAddrsU()` accepts a cell, user, request, server UUID/unique pair, caller-supplied flags, an in/out server-array index, and parallel arrays for server flags, IPv4 addresses, UUIDs, and unique values. `cm_getaddrsInit()` and `cm_getaddrsShutdown()` manage the module lock lifecycle.

Control flow and state: the header exposes no state directly; callers treat `cm_GetAddrsU()` as an append operation into existing server arrays. The implementation performs in-memory caching and VLDB RPC retry internally.

Dependencies and integration: requires OpenAFS cache-manager types (`cm_cell_t`, `cm_user_t`, `cm_req_t`), `afsUUID`, and fixed-size server arrays used by volume/cell discovery.

Risks: the API is array-based and relies on caller discipline for array size and initialized `index`; it returns AFS status codes but also mutates partial output arrays on success.

Test signals: compile users against this header, initialize/shutdown around cache-manager lifecycle, and verify multi-address UUID servers append expected parallel entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_getaddrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_ioctl.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_ioctl.c

Purpose: implements most Windows OpenAFS cache-manager pioctl operations. It parses ioctl buffers, converts path strings between client encodings and AFS filesystem strings, performs RX/fileserver/VLDB operations, mutates cache-manager state, updates the redirector, and serializes output back into `cm_ioctl_t`.

Important APIs/types/functions: initialization is `cm_InitIoctl()`, which creates `cm_Afsdsbmt_Lock` for submount registry writes. Buffer helpers are `cm_SkipIoctlPath`, `cm_ParseIoctlStringAlloc`, `cm_UnparseIoctlString`, `cm_IoctlGetQueryOptions`, `cm_IoctlSkipQueryOptions`, `cm_NormalizeAfsPath`, `cm_NormalizeAfsPathAscii`, and `TranslateExtendedChars`. Cache invalidation helpers are `cm_CleanFile`, `cm_FlushFile`, `cm_FlushParent`, and `cm_FlushVolume`. Functional handlers cover ACLs, volume status, fid/file type/owner/group/mode queries, server and cell management, server preferences, mount points, symlinks, tokens, submounts, RX stats, unicode/UUID controls, memory dumps, path availability, volume-state testing, verify data, and caller access.

Control flow: pioctl dispatch elsewhere enters a handler after path parsing or skipping. Handlers read from `ioctlp->inDatap`, advance input pointers as strings/structures are consumed, call cache-manager or RPC helpers, and append packed structures or NUL-terminated strings to `ioctlp->outDatap`. RPC paths (`FetchACL`, `StoreACL`, `Get/SetVolumeStatus`) use `cm_ConnFromFID`, RX connection acquisition, `cm_Analyze` retry loops, and `cm_MapRPCError`. Metadata reads generally call `cm_SyncOp` with status/callback flags, then copy scache fields. Mutating paths call `cm_SetAttr`, `cm_SymLink`, `cm_Unlink`, or registry functions, then discard affected scache state and notify `RDR_InvalidateObject` or `smb_NotifyChange`.

State and persistence: persistent state touched here includes registry-backed submounts under `HKLM\...\Submounts`, freelance registry data via `cm_FreelanceAdd/Remove*`, cell definitions via `cm_CreateCellWithInfo` and optional registry writes, global RX encryption mode `cryptall`, unicode mode `smb_UseUnicode`, process UUID `cm_data.Uuid`, sysname lists (`cm_sysNameList`, `cm_sysName64List`), verify-data globals, and per-user token state in `cm_user_t`/`cm_ucell_t`. Cache state is aggressively invalidated after ACL, flush, mount, symlink, token, and volume operations.

Dependencies and integration: depends on Windows registry, Win32 string APIs, SMB/redirector integration, RX/RXKAD/RX stats, VL/file-server RPCs, cell/volume/server/scache/buffer subsystems, B+ directory lookup for original names, NLS conversion helpers, and optional freelance fake-root support. Many handlers are public prototypes from `cm_ioctl.h` and are wired to AFS command-line tools through pioctl opcodes.

Risks: this is a large trust boundary around user-controlled ioctl buffers; many handlers use raw pointer advancement, `memcpy`, and variable-length strings, so malformed lengths and missing NULs are important risks. Output bounds rely on `SMB_IOCTL_MAXDATA` calculations but not every structure write preflights space. Several operations have subtle lock release/reacquire sequences around RPCs. Token handlers intentionally suppress session keys on readback, but still manipulate sensitive ticket memory. String conversion differs by UTF-8 flag, ANSI/OEM mode, and legacy translation rules.

Test signals: pioctl tests should cover UTF-8 and legacy encodings, query-option skipping, ACL fetch/store validation, flush behavior for normal and freelance FIDs, volume status RPC fallback/errors, mount point and symlink create/delete both in real directories and freelance root, token set/get/delete side effects on ACL cache, submount registry idempotency, sysname 32/64-bit lists, RX stat flag validation, UUID regeneration forcing new connections, and malformed ioctl buffers near `SMB_IOCTL_MAXDATA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_ioctl.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_ioctl.h

Purpose: public interface and wire-structure definitions for Windows OpenAFS cache-manager pioctl handlers implemented mainly in `cm_ioctl.c`.

Important APIs/types/functions: `cm_ioctl_t` tracks input/output allocation bases, current input/output cursors, copied byte counts, and flags such as `CM_IOCTLFLAG_DATAIN`, `CM_IOCTLFLAG_LOGON`, `CM_IOCTLFLAG_USEUTF8`, and `CM_IOCTLFLAG_DATAOUT`. Server preference structs (`cm_SPref_t`, `cm_SPrefRequest_t`, `cm_SPrefInfo_t`, `cm_SSetPref_t`) define get/set server preference payloads. `cm_cacheParms_t` carries cache metrics. `cm_ioctlQueryOptions_t` is an extensible pioctl option block with `literal` and `fid` fields guarded by `CM_IOCTL_QOPTS_HAVE_*` macros. The header declares sysname globals, UTF-8 pioctl prefix constants, RX stats flags, and a large set of pioctl handler prototypes.

Control flow and integration: pioctl front ends allocate/fill `cm_ioctl_t`, parse paths/query options using the helpers declared here, and dispatch to handlers by opcode. Handler declarations are grouped by functional area: ACLs, cache flushing, volume/cell/server preference operations, mount point/symlink manipulation, token lifecycle, submount creation, RX encryption/stats, UUID/unicode controls, memory dump, path availability, Unix mode, verify data, and caller access.

State and persistence: the header itself stores no data except extern declarations, but it defines ABI-sensitive structures consumed by external tools and third-party pioctl callers. Comments explicitly warn that query option flags must remain consistent across implementations.

Dependencies: includes `cm_user.h` for internal builds, but can expose only pioctl interface structures under `__CM_IOCTL_INTERFACES_ONLY__` with a local `cm_fid_t` definition.

Risks: structure layouts and flag values are public ABI; changing field order, sizes, or macros can break existing clients. Flexible trailing arrays (`servers[1]`) require careful length validation by handlers.

Test signals: ABI size/layout checks, 32/64-bit build coverage, UTF-8 prefix handling, query-option compatibility with older clients, and command-level pioctl coverage for every declared handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_memmap.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_memmap.c

Purpose: creates, validates, reuses, and shuts down the Windows cache-manager memory map that stores persistent cache-manager metadata and data buffers, or an in-memory heap-backed equivalent for virtual cache mode.

Important APIs/types/functions: sizing helpers compute the layout for config data, volumes, cells, ACLs, scaches, name cache, buffer headers/data, and hash tables. `ComputeSizeOfMappingFile()` sums the full layout. `CreateCacheFileSA()` and `FreeCacheFileSA()` build administrator-only security attributes for the cache file. `cm_IsCacheValid()` chains subsystem validators. `cm_ValidateMappedMemory()` opens an existing cache file, checks header size/magic/dirty flag, remaps at the stored base address, copies `cm_data`, validates data structures, and reports reuse viability. `cm_InitMappedMemory()` creates or reuses the mapping/heap, initializes `cm_data` offsets and subsystem bases, detects identity changes, and initializes volume/cell/ACL/scache/dcache subsystems. `cm_ShutdownMappedMemory()` shuts subsystems down, validates optional dirty status, persists `cm_data`, and unmaps/closes or destroys the heap.

Control flow: initialization computes a mapping size from configured stats, max volumes/cells, chunk size, cache blocks, and block size. File-backed mode creates or opens a hidden/system cache file, truncates oversized old files, probes the header to determine whether reuse is possible, then maps the whole file. Reuse requires matching config, clean shutdown, same base address, and optional validation success. New-cache setup zeroes `cm_data`, fills layout pointers sequentially through the mapped region, initializes counts/hash sizes, writes fake-root generation seed, creates a UUID, stores volume serial and machine SID, and touches the final byte to force allocation. Subsystem init calls then populate the mapped structures and the header is marked dirty until clean shutdown.

State and persistence: `cm_config_data_t cm_data` is the central persistent state image. File-backed mode persists embedded pointers and cache metadata across restarts, so it must remap at the previous base address. The dirty flag rejects reuse after crashes. UUID regeneration is triggered when the cache volume serial number or machine SID changes.

Dependencies and integration: integrates with Win32 file mapping, heap, security descriptor, SID, registry/SAM, volume information, and RPC UUID APIs. It calls cache-manager subsystem validators/init/shutdown for dcache, scache, ACL, cell, and volume modules.

Risks: persisted absolute pointers make base-address reuse mandatory; validation must catch stale/corrupt data before subsystem use. Security descriptor creation has minimal error checks. Machine SID extraction reads protected SAM data and may fail, weakening identity-change detection. Several size calculations cast through 32-bit values for hash sizing. Disk-full paths return cache-size errors and need coverage.

Test signals: new file-backed cache creation, clean reuse, dirty-cache rejection, changed configuration rejection, remap-at-different-address rejection, virtual cache mode, disk-full handling, validation failures per subsystem, volume serial/SID change UUID regeneration, and clean shutdown clearing dirty only when validation passes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_memmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_memmap.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_memmap.h

Purpose: defines the persistent mapped-cache header/layout contract and declares memory-map sizing, validation, initialization, and shutdown routines.

Important APIs/types/functions: `CM_CONFIG_DATA_VERSION` and `CM_CONFIG_DATA_MAGIC` identify compatible cache files. `cm_config_data_t` stores configuration, base address, cache sizing, all major subsystem base pointers and list/hash roots, fake-root fields, buffer accounting, UUID, cache volume serial number, and machine SID. Declared helpers include `GranularityAdjustment`, individual `ComputeSizeOf*` routines, `ComputeSizeOfMappingFile`, cache-file security helpers, `cm_ValidateMappedMemory`, `cm_InitMappedMemory`, and `cm_ShutdownMappedMemory`.

State and persistence: this header is the on-disk ABI for the Windows cache file. It persists absolute pointers, counts, hash table sizes, LRU/list heads, fake root state, buffer lists, UUID, and host identity fields. Architecture-specific buffer counters differ for `_M_IX86` versus other builds.

Dependencies and integration: requires cache-manager structure types for volumes, cells, ACL entries, scaches, name cache entries, buffers, FIDs, and UUIDs. All mapped-cache subsystems read/write through the global `cm_data` declared here.

Risks: any structure layout/version mismatch invalidates old cache files; adding fields requires version/magic coordination. Persisting pointers means ASLR/base-address changes can force rebuild. Counter width differs by architecture and can affect file compatibility.

Test signals: compile on 32-bit and 64-bit Windows, verify `CM_CONFIG_DATA_MAGIC` changes with version, validate size calculations after structure changes, and exercise cache reuse/rebuild across upgrades.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_memmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_nls.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_nls.c

Purpose: provides Windows NLS, Unicode normalization, UTF-8/UTF-16 conversion, sanitization, case-insensitive comparison, case mapping, and character navigation helpers for OpenAFS path and name handling.

Important APIs/types/functions: `cm_InitNormalization()` lazily loads `Normaliz.dll` and resolves `NormalizeString`/`IsNormalizedString`, selecting an English US LCID workaround on Windows 2000. `NormalizeUtf16String()` is the core internal normalization helper. Public conversion helpers include `cm_NormalizeStringAlloc`, `cm_NormalizeString`, `cm_Utf16ToUtf8Alloc`, `cm_Utf16ToUtf8`, `cm_Utf16ToUtf16`, `cm_NormalizeUtf16StringToUtf8`, `cm_NormalizeUtf8StringToUtf16`, `cm_NormalizeUtf8StringToUtf16Alloc`, `cm_Utf8ToUtf16`, `cm_Utf8ToUtf16Alloc`, and `cm_NormalizeUtf8String`. Comparison/case helpers include `cm_strnicmp_utf8`, `cm_strnicmp_utf16`, `cm_stricmp_utf16`, `cm_stricmp_utf8`, `cm_strlwr_utf16`, `cm_strupr_utf16`, and `strupr_utf8`. Navigation/validation helpers are `char_next_utf8`, `char_prev_utf8`, `char_next_utf16`, `char_prev_utf16`, `char_this_utf16`, and `cm_is_valid_utf16`.

Control flow: most public functions lazily initialize normalization, handle NULL/empty inputs, convert through Win32 `MultiByteToWideChar` or `WideCharToMultiByte`, normalize to NFC (`NormalizationC`), and either write caller buffers or allocate new ones. Invalid UTF-8 falls back to CP-1252 after `sanitize_bytestring()` percent-escapes bytes that are illegal in Windows names or undefined in CP-1252. Converted UTF-16 is checked for dangling surrogates; invalid surrogate code units are percent-escaped by `sanitize_utf16string()`. Case-insensitive compares convert UTF-8 to wide strings and call `CompareStringW`.

State and persistence: module-global state is limited to resolved function pointers, `nls_lcid`, and `nls_init`; no persistent storage is written. Returned allocated strings are caller-owned.

Dependencies and integration: used by ioctl parsing, freelance name comparisons, SMB/redirector path handling, and any cache-manager path logic that must bridge filesystem strings and Windows client strings. Depends on Win32 NLS APIs, `Normaliz.dll`, `strsafe`, and OpenAFS `cm_nls.h` typedefs.

Risks: several fixed `NLSMAXCCH` stack buffers cap conversion size; comments note TODOs around guaranteed NUL termination. Some `MultiByteToWideChar` calls pass `cch_src * sizeof(char)`, harmless for single-byte `char` but easy to cargo-cult incorrectly. `char_prev_utf8` contains pointer-decrement logic that should be tested carefully. CP-1252 fallback may preserve otherwise invalid input as percent escapes, which is intentional but security-sensitive for path matching.

Test signals: normalized and already-normalized UTF-16; valid UTF-8, invalid UTF-8 CP-1252 fallback, invalid bytes requiring percent escape, dangling surrogate input, insufficient caller buffers, empty and non-NUL-terminated inputs, case-insensitive comparisons under invariant/Win2K LCID, upper/lower mapping, and UTF-8/UTF-16 character stepping across multibyte and surrogate-pair boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_nls.c -->
