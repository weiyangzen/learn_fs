# Group Research: group_1724_reactos_sources_windows_reactos_ntoskrnl_mm_freelist_c_sources_wind_91b2893186bb

Scope confirmed against `Docs/research_subset_a.md`. All ten listed ReactOS memory-manager source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/freelist.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/freelist.c

## Purpose

`freelist.c` implements legacy ReactOS physical-page accounting on top of the ARM3 PFN database. It provides free/in-use PFN predicates, single-page allocation and dereference helpers, MDL-backed physical-page allocation, reverse-map metadata storage, saved swap-entry storage, and a simple LRU list for user pages.

## Main Contents

- Defines global PFN/accounting variables including `MmPfnDatabase`, available page counters, commit counters, and `FirstUserLRUPfn`/`LastUserLRUPfn`.
- Maintains a user-page LRU chain through `MmGetLRUFirstUserPage`, `MmGetLRUNextUserPage`, `MmInsertLRULastUserPage`, and `MmRemoveLRUUserPage`.
- Classifies PFNs with `MiIsPfnFree`, `MiIsPfnInUse`, and public `MmIsPageInUse`.
- Allocates physical pages for MDLs with `MiAllocatePagesForMdl`, including range filtering, zeroed-page preference, MDL sizing fallback, PFN setup, and post-allocation zeroing.
- Stores per-PFN ReactOS metadata with `MmSetRmapListHeadPage`, `MmGetRmapListHeadPage`, `MmSetSavedSwapEntryPage`, and `MmGetSavedSwapEntryPage`.
- Manages legacy PFN references through `MmReferencePage`, `MmGetReferenceCountPage`, `MmDereferencePage`, and `MmAllocPage`.

## Behavior And Data Flow

`MmAllocPage` removes a zeroed page, marks it active, sets the reference count to one, marks it as a ReactOS PFN through `u4.AweAllocation`, clears swap/rmap fields, and optionally inserts user pages into the LRU list. `MmDereferencePage` decrements the PFN reference count and, when it reaches zero, removes cached user pages from the LRU list, clears the ReactOS-PFN marker, and returns the page to the ARM3 free list with `MiInsertPageInFreeList`.

`MiAllocatePagesForMdl` converts address bounds to PFNs, creates the largest MDL it can afford, removes pages either from any free page or from a caller-specified PFN range, initializes each PFN as a locked MDL allocation, zeroes pages not already on the zeroed list, and returns an MDL with `MDL_PAGES_LOCKED`.

## Concurrency And Invariants

- Most PFN mutations require the PFN lock and assert it with `MI_ASSERT_PFN_LOCK_HELD`.
- Reverse-map and swap-entry fields are stored in reused PFN fields and guarded by PFN locking where required.
- ReactOS-owned PFNs are asserted with `MI_IS_ROS_PFN`, encoded through `u4.AweAllocation`.
- User LRU operations assume nonzero PFNs and consistent `NextLRU`/`PreviousLRU` links.

## Notable Details

- The LRU list is explicitly described as a hack for paging-out behavior; `MmGetLRUNextUserPage` can move a still-shared page to the tail to avoid repeatedly selecting early mapped pages.
- `MiAllocatePagesForMdl` warns but does not fully support nonzero `SkipBytes`.
- MDL allocations may return fewer pages than requested, and the MDL byte count is adjusted to the found page count.
- `MiIsPfnFree` treats PFNs on low-numbered page lists with zero references and list links as available, so callers rely on PFN list state rather than only reference count.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/freelist.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/i386/page.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/i386/page.c

## Purpose

`page.c` is the architecture-level page-table manipulation layer used by the newer ReactOS/ARM3 memory manager for x86-family paging configurations selected through `_MI_PAGING_LEVELS`. It translates memory protections to hardware PTE attributes, creates and deletes virtual mappings, handles pagefile PTEs, queries mapping state, and updates PTE protection/dirty state.

## Main Contents

- Defines `MmProtectToPteMask[32]` and `MmProtectToValue[32]` conversion tables between internal protection masks, Win32 page protections, and hardware PTE flags.
- Implements `MiIsPageTablePresent`, with separate logic for two-level paging and higher-level paging.
- Exposes `MmGetPfnForProcess` for current-process user mappings.
- Implements mapping deletion through `MmDeleteVirtualMappingEx`, wrapped by `MmDeleteVirtualMapping` and `MmDeletePhysicalMapping`.
- Implements pagefile PTE lifecycle through `MmCreatePageFileMapping`, `MmDeletePageFileMapping`, `MmIsPageSwapEntry`, and `MmGetPageFileMapping`.
- Implements mapping lifecycle through `MmCreateVirtualMappingUnsafeEx`, `MmCreateVirtualMappingUnsafe`, `MmCreatePhysicalMapping`, and checked `MmCreateVirtualMapping`.
- Provides query/update helpers: `MmIsPagePresent`, `MmIsDisabledPage`, `MmGetPageProtect`, `MmSetPageProtect`, and `MmSetDirtyBit`.
- Provides no-op `MmInitGlobalKernelPageDirectory` for this implementation and an i386 helper `Mmi386MakeKernelPageTableGlobal`.

## Behavior And Data Flow

User mappings are restricted to the current process and are protected by process working-set locks. Kernel mappings pass `Process == NULL` and must be in system space. `MmCreateVirtualMappingUnsafeEx` ensures the relevant PDE exists, builds a hardware PTE from the supplied protection and PFN, atomically installs it, increments share count for non-physical mappings, and increments page-table references for user mappings. `MmDeleteVirtualMappingEx` atomically clears the PTE, invalidates the TLB entry, optionally returns dirty/PFN information, decrements page-table references, deletes an empty PDE, and decrements the mapped PFN share count for non-physical mappings.

Pagefile mappings encode the swap entry in an invalid PTE shifted left by one. Deleting a pagefile mapping validates that the old PTE is a swap entry, clears it, releases the page-table reference, and returns the original swap entry.

## Concurrency And Invariants

- User-space operations assert `Process == PsGetCurrentProcess()` and acquire working-set locks.
- Kernel-space operations reject user addresses when `Process == NULL`.
- PTE updates use `InterlockedExchangePte` and flush with `KeInvalidateTlbEntry` when a valid or changed mapping may be cached.
- Page-table reference accounting controls when empty user PDEs can be deleted.
- PFN share-count updates are protected by the PFN lock.

## Notable Details

- `MmSetPageProtect` allows restoring access from `PAGE_NOACCESS` as long as the invalid PTE still contains a PFN and is not a swap entry.
- `MmIsDisabledPage` identifies invalid, non-swap PTEs with a nonzero page frame, representing a protection-disabled resident page.
- Write-copy protections are rejected for legacy kernel mappings in `MmCreateVirtualMappingUnsafeEx`.
- The implementation has strong current-process assumptions and is not a general cross-process page-table editor.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/i386/page.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/i386/pagepae.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/i386/pagepae.c

## Purpose

`pagepae.c` is an older i386 low-level paging implementation that supports both non-PAE and PAE at runtime through `Ke386Pae`. It manages process page directories, hyperspace mappings, page-table allocation/freeing, PTE reads/writes, swap PTEs, dirty bits, protection changes, TLB flushing, and global kernel page-directory snapshots.

## Main Contents

- Defines non-PAE and PAE hardware bit masks, address-to-PDE/PTE macros, hyperspace layout macros, and global kernel page-directory arrays.
- Implements SMP-aware TLB flushing through `MiFlushTlbIpiRoutine` and `MiFlushTlb`.
- Converts page protections with `ProtectToPTE`.
- Creates process address spaces in `MmCreateProcessAddressSpace`, allocating page-directory/table pages and wiring PTE base plus hyperspace self-mappings.
- Frees empty page tables through `MmFreePageTable`.
- Locates or creates PTE slots through `MmGetPageTableForProcessForPAE` and `MmGetPageTableForProcess`, including hyperspace access for non-current processes.
- Reads PTEs through `MmGetPageEntryForProcessForPAE` and `MmGetPageEntryForProcess`.
- Implements mapping deletion, pagefile mapping creation/deletion, mapping creation, dirty-bit updates, protection queries/updates, present/swap checks, and PFN lookup.
- Initializes global kernel PDE snapshots through `MmInitGlobalKernelPageDirectory`.

## Behavior And Data Flow

The file has parallel PAE and non-PAE branches for almost every operation. PAE paths operate on 64-bit PTEs and use `Exf*64`/`Exfp*64` interlocked operations; non-PAE paths operate on 32-bit PTEs. Page-table lookup creates missing page tables when requested and, for kernel addresses, first populates a global kernel directory entry and then synchronizes the current process directory from it.

`MmCreateVirtualMappingUnsafe` maps an array of PFNs over a virtual range, creating page tables as needed, marking PFNs mapped, replacing any prior mapped PFN, updating optional per-process page-table reference counts, and flushing stale translations. `MmDeleteVirtualMapping` atomically clears the PTE, marks the PFN unmapped if a page was present, returns dirty/PFN data, decrements page-table reference counts, and frees an empty page table.

## Concurrency And Invariants

- PTE replacement is interlocked; 64-bit PAE operations use explicit compare/exchange or exchange helpers.
- Hyperspace mappings are unmapped with `MmUnmapPageTable`, which distinguishes direct recursive PTE-space addresses from temporary hyperspace mappings.
- Per-address-space `PageTableRefCountTable` entries are incremented/decremented for user mappings and can trigger `MmFreePageTable`.
- Kernel PDEs are cached in global arrays and synchronized into process page directories.
- Nonzero physical bits in an invalid PTE are treated carefully: present pages and swap entries share invalid-PTE encodings.

## Notable Details

- The file has a different public signature for `MmCreateVirtualMappingUnsafe` and `MmCreateVirtualMapping` than `page.c`: it accepts an array of PFNs and a page count.
- NX support is partially encoded with high bits when `Ke386NoExecute` is set.
- Some failures assert instead of returning recoverable errors, reflecting low-level kernel assumptions.
- `Mmi386MakeKernelPageTableGlobal` lazily synchronizes missing kernel page tables and is used by the fault path as a fast recovery for kernel PDE misses.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/i386/pagepae.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/i386/procsup.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/i386/procsup.c

## Purpose

`procsup.c` provides the newer ARM3 i386 process address-space setup helper. It maps the new process page directory and hyperspace page through a temporary system PTE, installs required self-mappings and working-set mappings, copies kernel PDEs, and links the process into the memory-manager process list.

## Main Contents

- `MiArchCreateProcessAddressSpace(Process, DirectoryTableBase)`:
  - Extracts the page-directory PFN and hyperspace PFN from the supplied directory table base.
  - Reserves one system PTE for temporary mappings.
  - Maps the hyperspace page and writes the working-set-list PTE.
  - Remaps the same system PTE to the process page directory.
  - Copies kernel mappings from the current kernel PDE range into the process page directory.
  - Installs hyperspace and recursive PTE-base mappings.
  - Releases the temporary system PTE.
  - Inserts the process into `MmProcessList` under the expansion lock.

## Behavior And Data Flow

The function uses a single reserved system PTE as a temporary window. It first maps the hyperspace page to initialize the process working-set list entry, then remaps the window to the page directory and writes kernel, hyperspace, and recursive page-table entries. The recursive mapping makes the process page directory visible as page tables under `PTE_BASE`.

## Concurrency And Invariants

- Fails early if `MiReserveSystemPtes` cannot allocate a temporary PTE.
- Marks temporary kernel PTEs dirty and invalidates the temporary mapping after changing it.
- Uses `MiAcquireExpansionLock`/`MiReleaseExpansionLock` to update `MmProcessList`.
- Assumes `DirectoryTableBase[0]` and `[1]` already contain valid page-directory and hyperspace page frame addresses.

## Notable Details

- This file is short but important glue between architecture-specific address-space layout and generic ARM3 process management.
- Unlike `pagepae.c`, it does not allocate the page-directory pages itself; it consumes the directory-table base passed in by higher-level setup code.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/i386/procsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/marea.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/marea.c

## Purpose

`marea.c` implements legacy ReactOS memory areas backed by VAD-like AVL nodes. It creates, locates, inserts, frees, and cleans up `MEMORY_AREA` objects for section views, cache views, and static ARM3-owned kernel ranges while coexisting with newer ARM3 VADs.

## Main Contents

- Defines static memory-area storage and the legacy kernel VAD root `MiRosKernelVadRoot`.
- Locates areas by address or range with `MmLocateMemoryAreaByAddress` and `MmLocateMemoryAreaByRegion`.
- Checks address availability with `MmIsAddressRangeFree`.
- Inserts memory areas into process VAD roots or the legacy kernel VAD root through `MmInsertMemoryArea`.
- Finds free address gaps with `MmFindGap`.
- Frees mappings and VAD nodes through `MmFreeMemoryArea`.
- Creates memory areas through `MmCreateMemoryArea`.
- Cleans up process-exit legacy areas with `MiRosCleanupMemoryArea`.

## Behavior And Data Flow

`MmCreateMemoryArea` allocates either from a static array or nonpaged pool, initializes the object as a memory-area VAD, optionally finds a gap, validates user/kernel boundaries, checks conflicts for non-ARM3-owned areas, and inserts the VAD into the appropriate AVL table. User memory areas are inserted into the owning process VAD root; kernel areas are inserted into `MiRosKernelVadRoot`, initialized lazily.

`MmFreeMemoryArea` walks every page in the area. It removes swap mappings, physical mappings, or virtual mappings depending on page state and callback usage, invokes an optional page-free callback, removes the VAD node from the appropriate tree, detaches if it had attached to another process, poisons the magic in debug builds, and frees the area.

## Concurrency And Invariants

- Callers must hold the address-space creation lock; `MmFreeMemoryArea` asserts ownership.
- Process VAD operations use process working-set locks; kernel legacy VAD operations use `MmSystemCacheWs`.
- User memory areas must not cross `MmSystemRangeStart`; kernel address spaces must not allocate below it.
- ARM3-owned memory areas bypass some legacy conflict checks because their ranges are assumed prevalidated.

## Notable Details

- `MmLocateMemoryAreaByRegion` filters out ARM3 VADs by checking `MI_IS_MEMORY_AREA_VAD`; it returns only legacy memory areas.
- `MiRosCleanupMemoryArea` is explicitly constrained to process teardown and supports section views plus optional NEWCC cache areas.
- Static ARM3 memory areas are used during initialization to reserve important kernel ranges while still representing them in the legacy memory-area tree.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/marea.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/mmfault.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/mmfault.c

## Purpose

`mmfault.c` routes page faults between legacy ReactOS memory-area handlers and the newer ARM3 fault handler. It handles access faults, not-present faults, kernel/user permission checks, address-space locking, retry-on-memory-pressure behavior, and special cases such as shared user data and page-table addresses.

## Main Contents

- `MmpAccessFault` handles protection/access faults for legacy memory areas.
- `MmNotPresentFault` handles demand faults for legacy memory areas.
- `MmAccessFault` is the public dispatcher that decides whether a fault belongs to ARM3 or legacy ROSMM.
- Uses section-view handlers `MmAccessFaultSectionView` and `MmNotPresentFaultSectionView`.
- Under `NEWCC`, can dispatch cache-section faults to `MmAccessFaultCacheSection` or `MmNotPresentFaultCacheSection`.
- Calls `MmRebalanceMemoryConsumersAndWait` and retries when legacy handling returns `STATUS_NO_MEMORY`.

## Behavior And Data Flow

For legacy access and not-present faults, the code rejects high-IRQL faults, rejects user-mode access to kernel addresses, selects either the current process address space or kernel address space, locks the address space unless handling an MDL-style fault, locates the memory area, rejects missing/deleting areas, dispatches by memory-area type, and repeats if a handler requests `STATUS_MM_RESTART_OPERATION`.

The top-level `MmAccessFault` first gives i386 kernel PDE misses a chance to be repaired by `Mmi386MakeKernelPageTableGlobal`. It then immediately routes shared user data and page-table-address faults to ARM3. Once address spaces exist, it probes the relevant VAD tree; non-ROSMM VADs and paged-pool/no-address-space cases are routed to `MmArmAccessFault`. Remaining faults use the legacy access/not-present path.

## Concurrency And Invariants

- Fault handling below `DISPATCH_LEVEL` is required for both access and not-present legacy paths.
- Legacy memory-area lookup is protected by address-space locks except when `FromMdl` indicates the caller already controls locking.
- ARM3/legacy dispatch relies on VAD markers: ROSMM VADs are handled here, ARM3 VADs by `MmArmAccessFault`.
- Instruction-fetch faults on present pages are treated as NX violations and return `STATUS_ACCESS_VIOLATION`.

## Notable Details

- The `TrapInformation ? FALSE : TRUE` expression means absent trap information is treated as an MDL-originated fault for legacy handlers.
- Paged-pool faults can be routed to ARM3 even if no VAD was located.
- The file is a compatibility bridge: it preserves old ROSMM section/cache behavior while letting ARM3 own newer memory ranges.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/mmfault.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/mminit.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/mminit.c

## Purpose

`mminit.c` performs phase-1 memory-manager initialization for the ReactOS kernel. It creates static memory areas for important kernel virtual ranges, initializes legacy and ARM3 memory-manager subsystems, sets up shared user data mapping support, starts memory-management system threads, initializes memory events/session support, and write-protects loaded system images.

## Main Contents

- Defines globals such as `Mm64BitPhysicalAddress`, `MmReadClusterSize`, `MmDisablePagingExecutive`, `MmSharedUserDataPte`, and `MmKernelAddressSpace`.
- `MiCreateArm3StaticMemoryArea` creates a static `MEMORY_AREA_OWNED_BY_ARM3` reservation.
- `MiInitSystemMemoryAreas` reserves loader image, PTE base, hyperspace, PFN database, nonpaged pool, system PTEs, nonpaged expansion, system views, session space, paged pool, debugger mapping, and architecture-specific HAL/KPCR/shared-data ranges.
- `MiDbgDumpAddressSpace` prints the initialized kernel memory layout.
- `MmInitBsmThread` starts the balance set manager thread.
- `MmInitSystem` wires together all phase-1 initialization steps.

## Behavior And Data Flow

`MmInitSystem` asserts phase 1, initializes cache/section synchronization primitives, sets the kernel address space to the idle process VM, builds static kernel memory areas, dumps the layout, initializes global kernel page directories, memory consumers, reverse maps, section implementation, and pagefile support. It allocates a paged-pool PTE template for `KI_USER_SHARED_DATA`, initializes session working-set and session ID support, initializes memory threshold events, starts balancer and balance-set-manager threads, and finally walks loaded modules to apply system image write protection.

## Concurrency And Invariants

- Static memory-area creation runs under the kernel address-space lock.
- Each static area is asserted to create successfully; the helper notes that a bugcheck might be more appropriate than assertion-only handling.
- `MmSharedUserDataPte` is allocated from paged pool because the fault handler can already handle paged-pool addresses before it is used.
- Loaded module write-protection runs under `PsLoadedModuleResource`.

## Notable Details

- The loader image is the only static memory area marked executable by this file; other reserved ranges are read/write.
- The file initializes both old ROSMM pieces and newer ARM3 infrastructure, mirroring the hybrid design visible in `marea.c` and `mmfault.c`.
- `MmDisablePagingExecutive` is hard-coded to `1`, with comments noting paging executive states.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/mminit.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/pagefile.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/pagefile.c

## Purpose

`pagefile.c` implements ReactOS paging-file management and swap I/O. It validates and creates paging files, tracks paging-file slots with bitmaps, allocates/frees swap entries, reads and writes pages through MDL-based paging I/O, and exposes helper state for pagefile detection and out-of-swap reporting.

## Main Contents

- Defines minimum and architecture-specific maximum pagefile sizes.
- Maintains `MmPagingFile[MAX_PAGING_FILES]`, `MmPageFileCreationLock`, `MmNumberOfPagingFiles`, `MiFreeSwapPages`, `MiUsedSwapPages`, and reserved swap counters.
- Encodes swap entries with file index and page offset using `FILE_FROM_ENTRY`, `OFFSET_FROM_ENTRY`, and `ENTRY_FROM_FILE_OFFSET`.
- Builds one-page MDLs with `MmBuildMdlFromPages`.
- Detects paging files with `MmIsFileObjectAPagingFile`.
- Reports swap exhaustion once with `MmShowOutOfSpaceMessagePagingFile`.
- Performs swap I/O through `MmWriteToSwapPage`, `MmReadFromSwapPage`, and `MiReadPageFile`.
- Initializes globals in `MmInitPagingFile`.
- Allocates and frees swap slots with `MmAllocSwapPage` and `MmFreeSwapPage`.
- Implements the system call `NtCreatePagingFile`.

## Behavior And Data Flow

Swap entries reserve low bits for the paging-file index and store a one-based page offset. The first page of each pagefile is reserved as a header and never allocated. `MmAllocSwapPage` scans paging files for free space, marks one clear bitmap bit, updates global and per-file accounting, and returns an encoded entry. `MmFreeSwapPage` clears the corresponding bit and reverses the accounting.

`NtCreatePagingFile` validates caller privilege and user buffers, copies the name into paged pool, builds a DACL allowing SYSTEM and administrators, creates or opens the file with paging-file flags, validates size limits and device type, rejects floppy media, allocates the nonpaged `MMPAGING_FILE` descriptor and bitmap, initializes free-space accounting, inserts it into `MmPagingFile`, and initializes crash-dump support if the pagefile is on the boot partition.

## Concurrency And Invariants

- Pagefile list and slot accounting are guarded by `MmPageFileCreationLock`.
- Swap slot allocation assumes bitmap and free-space counters agree; unexpected bitmap failures bugcheck.
- Swap I/O validates that the target paging file and its device object exist before issuing paging I/O.
- User-mode creation requires `SeCreatePagefilePrivilege` and probes all user-supplied inputs.

## Notable Details

- Pagefile extension is recognized but not implemented; reopening an existing matching pagefile returns `STATUS_NOT_IMPLEMENTED` after validation.
- Several Windows-compatible validation steps are documented as TODOs, including section-object checks and notifying drivers to prepare for paging I/O.
- `MmZeroPageFile` and `MiReservedSwapPages` exist in this file but are not materially used by the shown logic.
- The device-type rejection path returns the current `Status` value rather than a newly assigned device-type-specific error, which is worth checking if this code is maintained.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/pagefile.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/region.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/region.c

## Purpose

`region.c` manages per-memory-area region lists. A region records a contiguous subrange's type and protection. The file supports initialization, lookup, and alteration of region lists, splitting and merging entries as ranges change.

## Main Contents

- `InsertAfterEntry` inserts a list entry after another list entry.
- `MmSplitRegion` splits one region into before/changed/after portions and invokes an alteration callback for the changed range.
- `MmAlterRegion` changes a range to a new type/protection, frees fully covered regions, splits a trailing partial region, and merges adjacent equal regions.
- `MmInitializeRegion` creates a single initial region covering the full length.
- `MmFindRegion` finds the region containing a given address and optionally returns that region's base address.

## Behavior And Data Flow

`MmAlterRegion` first finds the region that contains the start address. If that region differs from the requested type/protection, `MmSplitRegion` allocates replacement nodes and calls the supplied `AlterFunc` over the affected initial span. The main loop then absorbs complete following regions into the new region, invoking `AlterFunc` for each region whose attributes actually change. A final partial region is shortened if the requested range ends inside it. The result is normalized by merging adjacent regions with matching type and protection.

## Concurrency And Invariants

- The file assumes callers provide any needed synchronization around the region list.
- Region lengths are byte counts and are interpreted relative to a supplied base address.
- Allocation failures during initial splitting return `STATUS_NO_MEMORY`.
- `AlterFunc` is the hook that updates the actual mappings or metadata represented by the logical region change.

## Notable Details

- The merge-with-previous branch adds the old previous region's length to `NewRegion` and removes the previous entry, but does not relink or replace `NewRegion`; callers currently only need success/failure, not the merged node pointer.
- `MmFindRegion` is linear over the region list, which is acceptable for the small per-area lists this legacy subsystem uses.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/region.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/rmap.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/rmap.c

## Purpose

`rmap.c` implements reverse mappings from physical pages back to process virtual addresses or section segment page-table associations. It supports page-out decisions, insertion/deletion of reverse-map entries, segment association lookup, and section-association removal.

## Main Contents

- Initializes an NPaged lookaside list for `MM_RMAP_ENTRY` objects in `MmInitializeRmapList`.
- Pages out a physical page with `MmPageOutPhysicalAddress`.
- Adds mappings with `MmInsertRmap`.
- Removes mappings with `MmDeleteRmap`.
- Looks up section segment reverse maps with `MmGetSegmentRmap`.
- Deletes section associations with `MmDeleteSectionAssociation`.

## Behavior And Data Flow

`MmInsertRmap` allocates a reverse-map entry, normalizes non-segment addresses to page boundaries, verifies that the process PTE maps the expected PFN, and inserts the entry into the PFN's sorted rmap list under the PFN lock. Non-segment entries also increase the process working-set size and update the peak.

`MmPageOutPhysicalAddress` first finds a non-segment rmap entry for the page. It protects the target process from rundown, references it, locks the address space, attaches if needed, verifies the mapping still points to the target PFN, and handles section-view page-out. Private dirty pages may receive a newly allocated swap entry, be temporarily replaced with `MM_WAIT_ENTRY`, written to the paging file, and then replaced with a pagefile mapping. If swap allocation or writeback fails, the mapping is restored and marked dirty. Shared section-backed pages are released through section-segment accounting. If no process rmap can release the page, the code checks segment association and dirty segment state.

## Concurrency And Invariants

- PFN rmap list head access is guarded by the PFN lock through `MmGetRmapListHeadPage` and `MmSetRmapListHeadPage`.
- Process lifetime is protected with rundown protection plus object referencing during page-out.
- Address-space locks and process attach are used before process PTE inspection or mutation.
- Duplicate reverse-map entries for the same process/address are fatal.
- `MmGetSegmentRmap` requires the PFN lock and specifically checks for segment deletion state.

## Notable Details

- Segment reverse maps encode a page-table slice pointer in the `Process` field and a low-byte page index in a special masked address value.
- `MmPageOutPhysicalAddress` has several restore-on-failure paths to avoid losing dirty private pages when swap allocation or writeback fails.
- The `NEWCC` cache-area branch references `Type` rather than `MemoryArea->Type`, which appears suspicious in the shown code and should be checked if that conditional path is enabled.
- Working-set size is adjusted only for process virtual-address rmaps, not segment association entries.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/rmap.c -->