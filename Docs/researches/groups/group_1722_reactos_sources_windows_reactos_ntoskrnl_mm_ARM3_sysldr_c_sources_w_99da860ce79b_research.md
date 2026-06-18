# Group Research: group_1722_reactos_sources_windows_reactos_ntoskrnl_mm_ARM3_sysldr_c_sources_w_99da860ce79b

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/windows/reactos`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/sysldr.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/sysldr.c

ReactOS ARM3 kernel system loader implementation for loading, relocating, linking, protecting, paging, querying, and unloading kernel PE images.

Key responsibilities:
- Maintains loaded-module globals: `PsLoadedModuleList`, `MmLoadedUserImageList`, `PsLoadedModuleResource`, `PsLoadedModuleSpinLock`, `MmSystemLoadLock`, `PsNtosImageBase`, driver page counters, and kernel section PTE ranges.
- Loads an image section into system space through `MiLoadImageSection()`: maps the SEC_IMAGE view in the system process, reserves system PTEs, allocates PFN-backed pages, copies the mapped image, and unmaps the temporary view.
- Implements PE export lookup with `NameToOrdinal()`, `RtlpFindExportedRoutineByName()`, and `RtlFindExportedRoutineByName()`.
- Handles loader DLL callbacks through `MmCallDllInitialize()` and `MiCallDllUnloadAndUnloadDll()`.
- Tracks dependency references with `MiResolveImageReferences()`, `MiDereferenceImports()`, and `MiClearImports()`.
- Snaps import thunks with `MiSnapThunk()`, including ordinal imports, named imports, and recursive forwarder resolution.
- Initializes boot-loaded module bookkeeping with `MiInitializeLoadedModuleList()`, `MiBuildImportsForBootDrivers()`, `MiReloadBootLoadedDrivers()`, and `MiUpdateThunks()`.
- Frees discardable/init code ranges through `MiFindInitializationCode()`, `MiFreeInitializationCode()`, and `MmFreeDriverInitialization()`.
- Locates and modifies kernel resource/pool/sysPTE sections with `MiLocateKernelSections()`, `MmChangeKernelResourceSectionProtection()`, and `MmMakeKernelResourceSectionWritable()`.
- Applies per-section image protection through `MiWriteProtectSystemImage()` and `MiSetSystemCodeProtection()`.
- Provides public loader-facing APIs: `MmLoadSystemImage()`, `MmUnloadSystemImage()`, `MmCheckSystemImage()`, `MmPageEntireDriver()`, `MmResetDriverPaging()`, and `MmGetSystemRoutineAddress()`.

Important behavior:
- `MmLoadSystemImage()` is the central load path: parses base and directory names, handles optional name prefixes, deduplicates against `PsLoadedModuleList`, opens and validates the file, creates a section, copies it into ARM3 system PTE space, relocates it, creates an `LDR_DATA_TABLE_ENTRY`, resolves imports, write-protects sections, initializes the security cookie, sends image-load notifications, loads symbols when requested, and enables driver paging.
- Import validation rejects user-mode imports such as `ntdll`, `kernel32`, `user32`, `gdi32`, and mixed win32k/non-win32k import patterns for GDI-style drivers.
- Core imports from `ntoskrnl`, `hal`, and `win32k` are treated specially and not reference-counted like normal dependent DLLs.
- Boot import reconstruction scans already-fixed IAT entries to infer dependency ownership and stores either no imports, a tagged single import pointer, or a `LOAD_IMPORTS` array.
- `MiReloadBootLoadedDrivers()` moves eligible boot drivers into ARM3-controlled system PTE space, reuses existing PFNs, relocates the copied image, updates loader entries, and patches thunks in other boot modules.
- `MmUnloadSystemImage()` decrements load counts and cleans loader metadata and imports, but the actual driver image memory free is explicitly marked FIXME and logged as leaked.
- `MmGetSystemRoutineAddress()` searches only `ntoskrnl.exe` and `hal.dll` exports.
- Session image loading, large-page driver mapping, `MmResetDriverPaging()`, and actual driver paging are incomplete or disabled.

Dependencies:
- Heavy PE/COFF dependency: NT headers, section headers, data directories, import/export descriptors, load config, checksums, relocations, IATs, and security cookies.
- Uses ARM3 memory-manager primitives: system PTE reservation, PFN allocation/init, PTE writes, TLB flushes, system pageable VM deletion, PTE-to-address conversion, and physical/session address predicates.
- Uses object manager, section manager, file APIs, loader support, process attach APIs, resources, spin locks, mutants, debug symbol APIs, and image-load notify callbacks.
- Shares module-list and loader-entry semantics with the executive, I/O manager, debugger, and driver initialization paths.

Notable risks:
- `MiLoadImageSection()` maps the section before reserving system PTEs; on `MiReserveSystemPtes()` failure it returns without visibly unmapping the temporary mapped view in this file.
- Several later `MmLoadSystemImage()` failure paths after copying/relocating the image drop to cleanup without visibly releasing the ARM3 system PTE allocation or copied image pages.
- Actual unload still leaks the mapped driver image.
- Session loading is detected in multiple places but not implemented.
- Large-page mapping always returns unsupported after registry/list checks.
- Driver paging is compiled out because the page-fault path is noted as broken.
- Forwarded exports are supported by import snapping but deliberately not by public `RtlFindExportedRoutineByName()`.
- Import-list encoding uses special sentinel pointers and low-bit tagging, so cleanup and reference handling depend on strict pointer interpretation.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/sysldr.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/syspte.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/syspte.c

ReactOS ARM3 system PTE allocator for reserving, releasing, coalescing, and initializing kernel system PTE pools.

Key responsibilities:
- Defines global system PTE state: `MmSystemPteBase`, per-pool start/end arrays, `MmFirstFreeSystemPte`, `MmTotalFreeSystemPtes`, `MmTotalSystemPtes`, `MiNumberOfExtraSystemPdes`, and size-bucket helper tables.
- Stores free system PTEs as singly linked clusters ordered by increasing cluster size.
- Encodes one-PTE clusters with `u.List.OneEntry`; multi-PTE clusters store the cluster size in the second PTE's `NextEntry`.
- Provides `MI_GET_CLUSTER_SIZE()` to decode cluster sizes.
- Provides `MiReserveAlignedSystemPtes()` and `MiReserveSystemPtes()` for allocation.
- Provides `MiReleaseSystemPtes()` for zeroing, coalescing adjacent free clusters, and reinserting them by size.
- Provides `MiInitializeSystemPtes()` for boot-time pool setup.

Important behavior:
- Reservation acquires `LockQueueSystemSpaceLock`, finds the first cluster large enough, unlinks it, and allocates from the tail of the cluster.
- If reservation splits a cluster, the remaining prefix is reinserted into the free list at the size-sorted position.
- Successful reservation decrements `MmTotalFreeSystemPtes[PoolType]`, releases the lock, and flushes the process TLB.
- Release zeroes the PTE range, acquires the same lock, increments the free count, scans the entire free list, merges adjacent clusters on either side, then creates one merged cluster and inserts it by size.
- Initialization creates a single free cluster spanning the given PTE range and records the total system PTE count for `SystemPteSpace`.

Dependencies:
- Uses ARM3 PTE structures and list encoding from `miarm.h`.
- Uses queued spin lock `LockQueueSystemSpaceLock`.
- Uses `MI_SYSTEM_PTE_BASE`, `MM_EMPTY_PTE_LIST`, `MMSYSTEM_PTE_POOL_TYPE`, `MMPTE`, and TLB flush helpers.

Notable risks:
- The `Alignment` parameter to `MiReserveAlignedSystemPtes()` is only asserted to be `<= PAGE_SIZE`; it is not otherwise used to select an aligned run.
- `MiInitializeSystemPtes()` asserts `NumberOfPtes >= 1` but writes the size into the second PTE, so practical callers must provide at least two PTEs.
- Allocation is linear over the free-cluster list and release scans the whole list, so fragmentation and large lists directly affect allocator cost.
- Release does not flush the TLB after zeroing PTEs, unlike reservation.
- Size-bucket globals such as `MmSysPteIndex`, `MmSysPteTables`, and `MmSysPteListBySizeCount` are present but not used by this implementation.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/syspte.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/vadnode.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/vadnode.c

ReactOS ARM3 virtual address descriptor node algorithms built on the memory-manager AVL table support.

Key responsibilities:
- Defines `MmReadWrite`, a protection-mask permission table used for secured VAD checks.
- Imports AVL support through `miavl.h` and `sdk/lib/rtl/avlsupp.c`.
- Provides debug-only lock assertions for process VAD trees, the ReactOS kernel VAD root, and the section-based root.
- Locates VADs by address with `MiLocateVad()` and `MiLocateAddress()`, using `NodeHint` before falling back to AVL search.
- Detects overlap and insertion position with `MiCheckForConflictingNode()`.
- Inserts process VADs and generic address nodes with `MiInsertNode()`, `MiInsertVad()`, and `MiInsertVadEx()`.
- Inserts based sections into `MmSectionBasedRoot` with `MiInsertBasedSection()`.
- Removes nodes with `MiRemoveNode()` and maintains `NodeHint`.
- Walks predecessor/successor links with `MiGetPreviousNode()` and `MiGetNextNode()`.
- Finds free address ranges bottom-up, top-down, and in the section-based tree with `MiFindEmptyAddressRangeInTree()`, `MiFindEmptyAddressRangeDownTree()`, and `MiFindEmptyAddressRangeDownBasedTree()`.
- Enforces secured/no-change VAD rules with `MiCheckSecuredVad()`.

Important behavior:
- Process VAD writes require both the process working-set lock and `AddressCreationLock` in debug builds; kernel VAD writes require system working-set exclusivity and the idle process address creation lock.
- `MiInsertVadEx()` aligns the requested view size, acquires the current process address creation lock, rejects terminating processes, chooses an address by caller-specified base or top-down/bottom-up search, computes VPN bounds, sets commit charge for committed private memory or write-copy mapped memory, handles one-secured long VAD metadata, inserts under the working-set lock, and updates process virtual-size counters.
- Bottom-up range search starts from the lowest relevant user or kernel VPN and walks in-order until it finds a gap.
- Top-down range search starts below a boundary address, walks backward through predecessor nodes, and returns the highest aligned fitting gap.
- Section-based top-down search returns `STATUS_SUCCESS`/`STATUS_NO_MEMORY` instead of AVL insertion results and carries a compatibility branch for pre-Vista behavior.
- `MiCheckSecuredVad()` blocks protection changes that violate `NoChange`/`SecNoChange`, denies decommit-style changes against the secured subrange, and requires read-write-compatible protections for one-secured VAD ranges.

Dependencies:
- Depends on `MM_AVL_TABLE`, `MMADDRESS_NODE`, `MMVAD`, `MMVAD_LONG`, `EPROCESS`, working-set lock state, guarded mutex ownership, and ARM3 address constants.
- Uses RTL AVL primitives: `RtlpFindAvlTableNodeOrParent()`, `RtlpInsertAvlTreeNode()`, `RtlpDeleteAvlTreeNode()`, `RtlLeftChildAvl()`, `RtlRightChildAvl()`, `RtlParentAvl()`, and child-side predicates.
- Uses process globals and locks: `PsGetCurrentProcess()`, `PsGetCurrentThread()`, `PsIdleProcess`, `MiRosKernelVadRoot`, `MmSectionBasedRoot`, and `MmSectionBasedMutex`.

Notable risks:
- Lock enforcement is debug-only; release builds rely on callers honoring the locking contract.
- Several range routines use names like `LowVpn` while switching between byte addresses and VPN/page counts, so alignment/unit correctness is subtle.
- `MiInsertVad()` assumes the caller already proved no conflict; it asserts rather than returning a conflict status.
- `MiCheckSecuredVad()` asserts that multiple secured regions and read-only secured VADs are unsupported.
- Kernel-mode address search is keyed off `Table->Unused == 1`, an implicit table-mode convention that must be preserved by callers.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/vadnode.c -->