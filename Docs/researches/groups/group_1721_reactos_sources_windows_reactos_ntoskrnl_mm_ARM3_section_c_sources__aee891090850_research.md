# Group Research: group_1721_reactos_sources_windows_reactos_ntoskrnl_mm_ARM3_section_c_sources__aee891090850

Scope confirmed against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A. All three listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/section.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/section.c

Read status: complete file, 3587 lines.

This file implements ARM3 section-object support for ReactOS: section protection conversion, pagefile-backed section creation, prototype-PTE setup, process VAD insertion/removal, system/session-space section views, and the `NtCreateSection` / `NtMapViewOfSection` / `NtUnmapViewOfSection` syscall surface. It also bridges some calls to the older ReactOS memory manager for legacy section objects.

Key entry points:
- `MiMakeProtectionMask()` converts Win32 `PAGE_*` protection bits into internal MM protection masks, including guard, no-cache, and write-combine validation.
- `MiInitializeSystemSpaceMap()`, `MiInsertInSystemSpace()`, `MiRemoveFromSystemSpace()`, and `MiUnmapViewInSystemSpace()` manage system/session view address allocation through a bitmap plus hash table.
- `MiFillSystemPageDirectory()` and `MiSessionCommitPageTables()` allocate page tables needed for system or session mappings.
- `MiCreatePagingFileMap()` creates pagefile-backed `SEGMENT`, `CONTROL_AREA`, `SUBSECTION`, and prototype PTE state.
- `MiMapViewOfDataSection()` maps a pagefile-backed section into a process by building an `MMVAD_LONG`, optionally committing prototype PTEs, charging process quota, and inserting the VAD.
- `MiRemoveMappedView()`, `MiUnmapViewOfSection()`, and `MiRemoveMappedPtes()` tear down user, system, and session mappings and drop control-area references.
- `MmCreateArm3Section()` builds ARM3 section objects, currently with a working pagefile-backed path and largely unimplemented file-backed/image paths.
- `MmMapViewOfArm3Section()` validates map parameters and delegates to `MiMapViewOfDataSection()`.
- `MmMapViewInSessionSpace()`, `MmUnmapViewInSessionSpace()`, `MmUnmapViewInSystemSpace()`, and `MmCommitSessionMappedView()` expose kernel/session view operations.
- `NtCreateSection()`, `NtOpenSection()`, `NtMapViewOfSection()`, `NtUnmapViewOfSection()`, `NtExtendSection()`, and `NtAreMappedFilesTheSame()` provide syscall wrappers and probing.
- `MmGetFileObjectForSection()`, `MmGetFileNameForSection()`, `MmGetFileNameForAddress()`, and `MiQueryMemorySectionName()` support image/section filename queries.

Important state:
- `MmMakeSectionAccess[]` and `MmMakeFileAccess[]` map protection masks to section/file access rights.
- `MmUserProtectionToMask1[]`, `MmUserProtectionToMask2[]`, and `MmCompatibleProtectionMask[]` encode protection compatibility.
- `MmSession` is the pseudo-session used for global system-space views.
- `MmSectionCommitMutex` serializes prototype-PTE commitment.
- `MmSectionBasedRoot`, `MmSectionBasedMutex`, and `MmHighSectionBase` support `SEC_BASED` section address selection.

Important dependencies:
- ARM3 PFN/PTE primitives: `MiAcquirePfnLock`, `MiInitializePfnForOtherProcess`, `MiInitializePfnAndMakePteValid`, `MiDeleteVirtualAddresses`, `MI_WRITE_INVALID_PTE`, `MI_WRITE_VALID_PDE`.
- VAD helpers: `MiInsertVadEx`, `MiLocateVad`, `MiLocateAddress`, `MiRemoveNode`, `MiCheckSecuredVad`.
- Object and process APIs: `ObCreateObject`, `ObInsertObject`, `ObReferenceObjectByHandle`, `PsChargeProcessNonPagedPoolQuota`, `KeStackAttachProcess`.
- ReactOS legacy MM compatibility: `MiIsRosSectionObject`, `MiRosUnmapViewOfSection`, `MiRosUnmapViewInSystemSpace`, `MmLocateMemoryAreaByAddress`.

Notable behavior and risks:
- ARM3 section support is deliberately narrow: image sections, file-backed data sections, ROM/global-only-per-session sections, large pages, physical-memory sections, write-watch, and `MEM_RESERVE` mappings are asserted or rejected in many paths.
- `MiCreateDataFileMap()` is a stub that asserts false and returns `STATUS_NOT_IMPLEMENTED`, so the apparent file-backed section path in `MmCreateArm3Section()` cannot complete normally.
- `MiCreatePagingFileMap()` appears to free the `Segment` output parameter rather than `NewSegment` on control-area allocation failure.
- `MiQueryMemorySectionName()` references the target process handle but does not attach to that process before resolving `BaseAddress`; the lookup uses the current address space.
- `MmCommitSessionMappedView()` rejects `LastProtoPte` when it equals the subsection end, although the loop treats it as one-past-end.
- `NtExtendSection()` calls `MmExtendSection()` and may copy back the size, but returns `STATUS_NOT_IMPLEMENTED` unconditionally.
- Several failure paths are intentionally guarded by `ASSERT(FALSE)` rather than recoverable cleanup, matching an incomplete ARM3 implementation stage.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/section.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/session.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/session.c

Read status: complete file, 1089 lines.

This file implements ARM3 session-space lifecycle support: session ID allocation, session-space page/table setup, working-set initialization, process membership accounting, session attach/detach, locale storage, and lookup of a process belonging to a session.

Key entry points:
- `MiInitializeSessionWsSupport()` initializes the global session working-set list.
- `MiInitializeSessionIds()` computes per-session data/tag/page charges, initializes `MiSessionIdMutex`, and allocates the initial session-ID bitmap.
- `MmIsSessionAddress()`, `MmGetSessionLocaleId()`, `MmSetSessionLocaleId()`, `MmGetSessionId()`, and `MmGetSessionIdEx()` expose basic session queries.
- `MiSessionLeader()` marks a process as the single session leader under the expansion lock.
- `MiSessionCreateInternal()` allocates a session ID, session data pages, session page-directory page, session tag pages, page-table tracking array on 32-bit builds, and initializes `MM_SESSION_SPACE`.
- `MiSessionInitializeWorkingSetList()` maps and initializes `MiSessionSpaceWs`, assigns session working-set limits, and inserts the session into global working-set lists.
- `MmSessionCreate()` promotes the caller to session leader if needed, creates session space, initializes the working set, and marks the process in-session.
- `MiSessionAddProcess()` adds a new process to the current session and increments session references.
- `MiSessionRemoveProcess()`, `MiDereferenceSession()`, `MiDereferenceSessionFinal()`, and `MiReleaseProcessReferenceToSessionDataPage()` remove process/session references and free session data mappings when the last reference is gone.
- `MmSessionDelete()` lets the session leader drop the leader reference.
- `MmAttachSession()` and `MmDetachSession()` attach to the process backing a target session while maintaining an attach count and delete-pending wait event.
- `MmGetSessionById()` scans the session working-set list and returns a referenced process from the requested session.
- `MmQuitNextSession()` releases the process reference obtained by session iteration.

Important state:
- `MmSessionSpace` is the currently mapped per-process session-space pointer.
- `MiSessionDataPages`, `MiSessionTagPages`, `MiSessionTagSizePages`, `MiSessionBigPoolPages`, and `MiSessionCreateCharge` describe per-session page costs.
- `MiSessionIdBitmap` tracks allocated session IDs.
- `MiSessionLeaderExists` enforces a single session leader in this implementation.
- `MiSessionWsList` and `MmWorkingSetExpansionHead` track session working sets.
- `MmExpansionLock` / `MiAcquireExpansionLock()` protect session lists and attach/delete counters.

Important dependencies:
- PFN and PTE allocation primitives: `MiReserveSystemPtes`, `MiRemoveZeroPageSafe`, `MiRemoveAnyPage`, `MiInitializePfnForOtherProcess`, `MiInitializePfnAndMakePteValid`, `MiReleaseSystemPtes`.
- Session view-map initialization from `section.c`: `MiInitializeSystemSpaceMap()`.
- Process flags and process/session links: `PSF_PROCESS_IN_SESSION_BIT`, `PSF_SESSION_CREATION_UNDERWAY_BIT`, `SessionProcessLinks`.
- Kernel attach and synchronization APIs: `KeStackAttachProcess`, `KeUnstackDetachProcess`, guarded mutexes, events, and interlocked counters.

Notable behavior and risks:
- The implementation effectively supports a single session leader globally through `MiSessionLeaderExists`; bitmap expansion for additional session IDs is explicitly not implemented.
- `MiSessionCreateInternal()` has incomplete cleanup on failure. If no session ID is available, it returns while still holding `MiSessionIdMutex` and without clearing `PSF_SESSION_CREATION_UNDERWAY_BIT`.
- Many allocation failures are handled by assertions rather than unwind paths, including page-table and system-PTE allocation.
- Session pool initialization is commented out, so only the data/tag page setup and system-view map are initialized here.
- `MmSessionDelete()` does not reset `MiSessionLeaderExists`, so leader reuse after deletion is not represented in this file.
- `MmGetSessionById()` returns a referenced `EPROCESS`, not an `MM_SESSION_SPACE`, despite its name.
- Several teardown paths flush TLBs or rely on commented-out PDE clearing, showing the session teardown implementation is incomplete.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/session.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/special.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/special.c

Read status: complete file, 694 lines.

This file implements ARM3 special pool support for ReactOS. Special pool routes selected pool allocations to a dedicated one-page allocation with a neighboring guard PTE, fills unused bytes with a pattern, and bugchecks on detected underruns, overruns, invalid frees, or invalid IRQL use.

Key entry points:
- `MmUseSpecialPool()` decides whether a request should use special pool based on allocation size and `MmSpecialPoolTag`, including wildcard tag support.
- `MmIsSpecialPoolAddress()` checks whether an address lies inside the reserved special-pool VA range.
- `MmIsSpecialPoolAddressFree()` checks whether the corresponding PTE is a free special-pool PTE rather than a guard marker.
- `MiInitializeSpecialPool()` reserves aligned system PTEs, builds a free list of PTE pairs, records extra reserve PTEs, sets nonpaged usage limits, and enables `POOL_FLAG_SPECIAL_POOL`.
- `MmExpandSpecialPool()` links another page worth of reserved PTE pairs into the free list when the active list is exhausted.
- `MmAllocateSpecialPool()` validates IRQL and limits, removes a PTE pair from the free list, allocates a physical page, maps it, chooses overrun or underrun layout, writes a `POOL_HEADER`, marks the guard PTE, fills the page with a tick-count byte pattern, and updates counters.
- `MiSpecialPoolCheckPattern()` verifies the post-buffer fill pattern.
- `MmFreeSpecialPool()` derives the header from the pointer layout, validates IRQL and guard markers, checks fill patterns, records freed-allocation metadata, unmaps or deletes the backing page, returns the PTE pair to the free list, and updates counters.
- `MiTestSpecialPool()` is a local stress/test helper for allocation/free and optional corruption tests.

Important state:
- `MmSpecialPoolStart` and `MmSpecialPoolEnd` define the reserved VA range.
- `MiSpecialPoolFirstPte`, `MiSpecialPoolLastPte`, `MiSpecialPoolExtra`, and `MiSpecialPoolExtraCount` manage the free PTE-pair list and reserves.
- `MmSpecialPagesInUse`, paged/nonpaged counters, and peak counters track special-pool consumption.
- `MiSpecialPagesNonPagedMaximum` caps nonpaged special-pool usage.
- `MmSpecialPoolCatchOverruns` chooses the default detection layout.
- PTE `PageFileHigh` values `SPECIAL_POOL_PAGED_PTE` and `SPECIAL_POOL_NONPAGED_PTE` mark guard PTEs.

Important dependencies:
- System PTE reservation through `MiReserveAlignedSystemPtes`.
- PFN allocation and mapping through `MiRemoveAnyPage`, `MiInitializePfnAndMakePteValid`, `MiDecrementShareCount`, and PFN lock helpers.
- Pool integration through `ExpPoolFlags`, `MmSpecialPoolTag`, and normal pool fallback when `MmAllocateSpecialPool()` returns `NULL`.
- Pageable-system-VM deletion through `MiDeleteSystemPageableVm()` for paged special-pool frees.

Notable behavior and risks:
- The special-pool VA range check uses `P <= MmSpecialPoolEnd`; `MmSpecialPoolEnd` is computed from the last PTE plus one, so this appears to include a one-past-end address.
- Special pool deliberately rejects allocations larger than one page minus `POOL_HEADER` and rejects the segment tag `'tSmM'` to avoid recursion with section prototype-PTE allocation.
- Alignment in `MiInitializeSpecialPool()` is disabled with a `FIXME`, so the reserved region may not honor the intended large alignment.
- Freed allocation records have placeholders for stack capture; `StackPointer` and `StackBytes` are not populated.
- Nonpaged free currently flushes the entire TLB with a `FIXME` to use single-address flushing.
- The verifier overlay header mentioned in `MI_FREED_SPECIAL_POOL` is still a TODO.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/special.c -->