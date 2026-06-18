# Group Research: group_1723_reactos_sources_windows_reactos_ntoskrnl_mm_ARM3_virtual_c_sources__f9c39afdb8d6

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/virtual.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/virtual.c

## Role In Subset

Implements ReactOS ARM3 virtual memory management and the user-facing NT virtual-memory syscalls. This is a central bridge between VAD address-space metadata, page-table/PTE manipulation, PFN accounting, working-set locking, process attach/detach, and user probe/SEH behavior.

## Main Responsibilities

- Counts committed pages over VAD ranges with `MiCalculatePageCommitment`, including multi-level page-table gaps and decommitted PTE detection.
- Ensures page-table pages are resident through `MiMakeSystemAddressValid`, `MiMakeSystemAddressValidPfn`, and `MiMakePdeExistAndMakeValid`.
- Deletes mapped virtual ranges via `MiDeletePte`, `MiDeleteVirtualAddresses`, and `MiDeleteSystemPageableVm`, updating PFN share/reference counts and page-table references.
- Copies memory between processes with `MmCopyVirtualMemory`, selecting MDL-backed mapped copy for larger transfers and pool/stack copy for smaller transfers.
- Implements `NtReadVirtualMemory`, `NtWriteVirtualMemory`, `NtProtectVirtualMemory`, `NtAllocateVirtualMemory`, `NtFreeVirtualMemory`, `NtQueryVirtualMemory`, lock/unlock VM calls, instruction-cache flush, and physical-address lookup.
- Supports private demand-zero allocation, commit, decommit, release, VAD splitting, and basic section commit paths for ARM3 sections.
- Queries memory state/protection by combining VAD metadata, page-table state, prototype PTEs, PFN `OriginalPte`, and special shared-user-data handling.

## Important Internal Flows

- `NtAllocateVirtualMemory` validates flags, probes user outputs, references/attaches to the target process, creates VADs for reserve/blind commit, or commits into an existing VAD by writing demand-zero PTEs and updating commit accounting.
- `NtFreeVirtualMemory` handles `MEM_RELEASE` and `MEM_DECOMMIT`; release can remove an entire VAD, trim from front/back, or split a VAD in the middle before deleting PTEs.
- `MiProtectVirtualMemory` validates VAD range and protection, rejects unsupported VAD types, confirms private ranges are fully committed, then updates valid or invalid PTE protections.
- `MiDecommitPages` batches valid PTE teardown in `MiProcessValidPteList` to reduce repeated TLB flushes.
- `MiLockVirtualMemory` probes every page, faults missing pages in, then marks PFN-embedded WSLE lock bits; `MiUnlockVirtualMemory` validates all requested locks before dropping them.

## Locking And State Assumptions

- VAD operations use process address-space locks.
- PTE/PFN deletion paths require PFN lock and exclusive working-set ownership.
- Query/protection paths frequently assume current-process attachment when touching user page tables.
- Page-table page residency helpers intentionally release/reacquire working-set or PFN locks while faulting kernel page-table addresses back in.
- Several paths assert no clone/fork support and no unsupported prototype/shared-page combinations.

## Notable Limitations

- `MmFlushVirtualMemory` is unimplemented but returns `STATUS_SUCCESS` while reporting `STATUS_NOT_IMPLEMENTED` in the I/O status block.
- `MmGetVirtualForPhysical`, `MmSecureVirtualMemory`, and `MmUnsecureVirtualMemory` are placeholders.
- `NtGetWriteWatch` and `NtResetWriteWatch` are unimplemented but return success-like results after validation.
- Large pages, physical memory VADs, write-watch allocation, many section protection changes, file-backed ARM3 section assumptions, fork/clone, and several prototype-PTE scenarios are unsupported or assertion-only.
- SMP TLB invalidation is incomplete in protection changes involving transition PTEs.
- `MEM_RESET` currently pretends success without doing reset semantics.

## Filesystem-Relevant Notes

Virtual-memory behavior here affects mapped files, section views, cache interaction, paging I/O, and user/kernel buffer copying used by filesystem paths. The section-related code is partial: private memory is the strongest path, while file-backed mapped section behavior has explicit unsupported assertions and delegation to legacy section-view helpers in query/protect cases.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/virtual.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/wslist.cpp -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/wslist.cpp

## Role In Subset

Implements ARM3 working-set list management in C++ for process and system cache working sets. It tracks resident virtual pages through WSLEs, grows/shrinks WSLE backing storage, and trims cold pages under memory pressure.

## Main Responsibilities

- Maintains global `MmWorkingSetList` and `MmWorkingSetManagerEvent`.
- Allocates/free WSLE indexes with a compact free-list representation in `GetFreeWsleIndex` and `FreeWsleIndex`.
- Grows the WSLE array by allocating pages and making PTEs valid; shrinks excess backing pages when high indexes are freed.
- Inserts valid pages into a working set through `MiInsertInWorkingSetList`, recording virtual page, protection, direct/hashed flags, lock flags, and age.
- Removes pages with `MiRemoveFromWorkingSetList`.
- Initializes a working set list with fixed entries for paging structure mappings and the WSL itself.
- Implements `MmWorkingSetManager`, iterating `MmWorkingSetExpansionHead` and trimming eligible process working sets.

## Trimming Behavior

- `TrimWsList` scans dynamic entries, resets accessed bits on recently used pages, ages untouched pages, skips locked entries, skips page-table addresses, and converts sufficiently old valid PTEs into transition PTEs.
- When trimming, it marks dirty PFN state from the hardware dirty bit and decrements share count to place the page on standby/modified lists.
- Only direct WSLEs are supported.

## Locking And State Assumptions

- Insert/remove paths require exclusive working-set lock ownership.
- Trim scan requires a working-set lock and upgrades to exclusive before mutation.
- PFN changes use `ntoskrnl::MiPfnLockGuard`.
- Process working-set trimming attaches to the process after acquiring rundown protection, then detaches and releases protection.

## Notable Limitations

- Shared/prototype pages are not supported in this implementation path.
- ReactOS legacy PFNs are explicitly rejected.
- Session and system-space working sets are marked unsupported in the manager.
- Page-table address trimming is skipped because invalidating PDEs breaks legacy memory-manager assumptions.
- There is a temporary hack around PFN-embedded lock flags until fuller WSLIST support exists.

## Filesystem-Relevant Notes

Working-set trimming indirectly affects mapped-file and cache-backed pages by deciding when resident pages become transition pages. The current implementation is conservative and process-focused, with section/shared-page support still limited.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/wslist.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/zeropage.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/zeropage.c

## Role In Subset

Implements the ARM3 zero page thread, which converts free pages into zeroed pages for future fast allocation.

## Main Responsibilities

- Declares global `MmZeroingPageEvent`.
- Frees discardable initialization code once the zero page thread starts, via `MiFindInitializationCode` and `MiFreeInitializationCode`.
- Lowers the thread priority to zero.
- Waits on the zeroing event, removes batches of pages from the free list, maps them into reserved zeroing space, zeroes them, unmaps them, then inserts them into `MmZeroedPageListHead`.

## Important Behavior

- Batches up to `MI_ZERO_PTES` pages per zeroing pass.
- Verifies that the first global free page is also the first page removed for its page color, bugchecking with `PFN_LIST_CORRUPT` if not.
- Uses PFN lock while removing and reinserting pages, but releases it while actually zeroing memory.
- Clears the zeroing event when no free pages are available.

## Notable Limitations

- The intended idle timer wait object is commented out with a FIXME.
- The thread is an infinite kernel worker and has no explicit shutdown path.

## Filesystem-Relevant Notes

Zeroed page availability affects page-cache, mapped-file, and private-memory allocation latency because many kernel and user allocations can be satisfied from zeroed pages instead of synchronously clearing free pages.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/zeropage.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/amd64/init.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/amd64/init.c

## Role In Subset

Provides amd64 machine-dependent memory-manager initialization for ReactOS ARM3: template PTE/PDE setup, session/system VA layout, early page-table construction, nonpaged pool/system PTE layout, PFN database mapping/population, and final machine-dependent initialization.

## Main Responsibilities

- Defines amd64 kernel PTE/PDE templates: valid kernel, local kernel, demand-zero, prototype, and decommitted PTEs.
- Builds session, session image, session working set, session view, session pool, and system view layout in `MiInitializeSessionSpaceLayout`.
- Maps paging hierarchy levels with `MiMapPPEs`, `MiMapPDEs`, and `MiMapPTEs`.
- Initializes the active page table in `MiInitializePageTable`, clears user PXEs, enables global pages, sets hyperspace, debug mapping, mapping range, VAD bitmap, and working-set-list mappings.
- Calculates and maps nonpaged pool in `MiBuildNonPagedPool`.
- Creates system PTE space and reserves zeroing PTEs in `MiBuildSystemPteSpace`.
- Maps and initializes the PFN database with `MiBuildPfnDatabase`, using loader memory descriptors and page-table walks.
- Completes amd64 MM bring-up in `MiInitMachineDependent`.

## PFN Database Details

- `MiAddDescriptorToDatabase` adds free memory to the free list, marks XIP ROM specially, asserts on bad memory, and marks other memory active.
- `MiBuildPfnDatabaseFromPageTables` walks valid paging structures and calls `MiSetupPfnForPageTable` so PFN entries reflect existing boot mappings.
- The initializer temporarily consumes boot allocator pages through `MxGetNextPage`, then reconstructs accounting from loader descriptors.

## Notable Limitations

- Nonpaged pool percentage registry cap is unimplemented.
- Some page-zeroing and global-page comments are marked TODO/FIXME.
- Loader bad memory currently asserts.
- Cache attribute setup has a FIXME noting mismatch with Windows expectations.
- Several ref/share counts are manually reset after PFN database construction so process address-space initialization can proceed.

## Filesystem-Relevant Notes

This file establishes the kernel virtual address regions used later by cache manager, system PTE mappings, nonpaged pool allocations, and PFN accounting. Filesystem and block I/O paths depend on these regions being initialized before mapped I/O, MDLs, and cache trimming are reliable.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/amd64/init.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/amd64/procsup.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/amd64/procsup.c

## Role In Subset

Implements amd64 process address-space creation support for ARM3, specifically architecture-specific setup after generic process directory table pages have been allocated.

## Main Responsibilities

- `MiArchCreateProcessAddressSpace` initializes a new process PML4 and hyperspace paging hierarchy.
- Uses provided `DirectoryTableBase` entries for the top-level table and hyperspace root.
- Allocates/zeroes pages for hyperspace PD and PT, preferring zeroed pages and falling back to any page plus `MiZeroPhysicalPage`.
- Reserves a system PTE to temporarily map and edit the new process page tables.
- Clears user half of the top-level table and copies kernel mappings from the current address space.
- Writes self-map, hyperspace, hyperspace PD/PT, and working-set-list mappings.
- Releases temporary system PTEs before returning.

## Locking And State Assumptions

- PFN lock is used while removing pages from zero/free lists.
- The non-architecture code is assumed to have already allocated the top-level and hyperspace pages.
- TLB invalidation is done with `__invlpg` after remapping the temporary system PTE to point at different paging levels.

## Notable Limitations

- Returns `FALSE` only if temporary system PTE reservation fails; allocated hyperspace pages are not visibly unwound in that failure case.
- Depends on amd64 paging constants and ARM3 templates established in `amd64/init.c`.

## Filesystem-Relevant Notes

Every process address space must contain correct kernel and hyperspace mappings before filesystem-facing syscalls can safely copy buffers, fault pages, or access working-set data for mapped files.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/amd64/procsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/arm/page.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/arm/page.c

## Role In Subset

Contains an older ARM page-management file with protection translation tables and mostly placeholder implementations for legacy page mapping APIs.

## Main Responsibilities

- Defines ARM `MmProtectToPteMask` and `MmProtectToValue` arrays mapping internal MM protections to PTE bits and Win32 protection constants.
- Defines `MmGlobalKernelPageDirectory`, kernel/demand-zero/prototype/decommitted PTE templates, and local kernel templates.
- Provides `MmInitGlobalKernelPageDirectory`, which records existing kernel PDEs while skipping recursive PTE and hyperspace slots.
- Provides trivial protection getter/setter behavior, returning read/write and ignoring requested changes.
- Declares stubs for process address-space creation, virtual mapping creation/deletion, pagefile mapping, PFN lookup, dirty state, presence checks, swap entry checks, disabled page checks, and session-space layout.

## Notable Limitations

- Most operational functions call `UNIMPLEMENTED_DBGBREAK`, return false/success placeholders, or assert.
- Page protection is not enforced; pages are treated as RWX/read-write by the exposed helpers.
- `MmGetPageFileMapping`, `MmIsDisabledPage`, and `MiInitializeSessionSpaceLayout` assert false.
- This file is less complete than `arm/stubs.c` and appears to be a placeholder ARM path.

## Filesystem-Relevant Notes

The file does not provide a production-grade ARM memory mapping substrate. Any filesystem or cache behavior requiring ARM pagefile mappings, dirty tracking, or robust virtual mapping would depend on unimplemented functionality here.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/arm/page.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/arm/stubs.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/arm/stubs.c

## Role In Subset

Provides a partial older ARM memory-manager implementation: page-table lookup/creation, kernel virtual mapping creation/deletion, process page-directory creation, basic PFN lookup/presence checks, kernel page-directory initialization, and ARM physical-address lookup.

## Main Responsibilities

- Maintains `MmGlobalKernelPageDirectory`, `MiArmTemplatePte`, and `MiArmTemplatePde`.
- `MiGetPageTableForProcess` locates or creates coarse page tables for addresses, allocating nonpaged-pool pages as needed.
- `MmCreateProcessAddressSpace` allocates page-directory/hyperspace pages, copies kernel PDEs, and sets recursive/hyperspace PDEs.
- `MmCreateVirtualMappingInternal` writes ARM PTEs over a range, creating page tables when crossing PDE boundaries.
- `MmCreateVirtualMapping` validates pages are in use, then delegates to the unsafe/internal mapping path.
- `MmDeleteVirtualMapping` clears a PTE, flushes TLB, returns PFN, and reports dirty state as false.
- `MmGetPfnForProcess`, `MmIsPagePresent`, and `MmIsPageSwapEntry` inspect captured PTEs.
- `MmInitGlobalKernelPageDirectory` captures template PTE/PDE values from a known-good kernel mapping and records kernel PDEs.
- `MmGetPhysicalAddress` handles a special early PCR section mapping and normal valid PTE lookup.

## Locking And Architecture Behavior

- Uses ARM-specific `KeArmInvalidateTlbEntry`.
- Uses hyperspace mappings while constructing a process page directory.
- Kernel mappings are supported more directly than user mappings.
- Page table unmapping for user-mode paths is effectively fatal/unsupported.

## Notable Limitations

- User-mode memory support is explicitly marked unsupported in several paths.
- Some control flow uses a `kernelHack` path for page-table creation.
- Dirty page operations and pagefile mapping operations are unimplemented.
- `MmDeleteVirtualMapping` reports `WasDirty = FALSE` with an explicit “LIE” comment.
- The code references `FreePage` in deletion logic, implying reliance on external/global behavior not visible in this file.
- Protection is not enforced and returns read/write behavior.

## Filesystem-Relevant Notes

This partial ARM implementation could support simple kernel mappings but is not sufficient for full filesystem paging behavior: dirty tracking, pagefile mappings, user mapped views, and protection enforcement are incomplete.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/arm/stubs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/balance.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/balance.c

## Role In Subset

Implements ReactOS memory balancing: per-consumer page accounting, page release/request helpers, consumer trimming, user-page aging/pageout, cache trimming integration, and the balancer system thread.

## Main Responsibilities

- Initializes `MiMemoryConsumers`, minimum available-page thresholds, and user consumer target in `MmInitializeBalancer`.
- Registers per-consumer trim callbacks with `MmInitializeMemoryConsumer`.
- Releases consumer pages with `MmReleasePageMemoryConsumer`, decrementing page usage and total committed pages before dereferencing PFNs.
- Trims a consumer with `MiTrimMemoryConsumer`, calculating targets from global pressure and per-consumer page targets.
- Implements `MmTrimUserMemory`, which either aggressively pages out LRU user pages or first clears accessed bits and later pages out cold pages.
- Triggers memory balancing through `MmRebalanceMemoryConsumers` and synchronous `MmRebalanceMemoryConsumersAndWait`.
- Allocates pages through `MmRequestPageMemoryConsumer`, updating consumer usage and total committed pages.
- Runs `MiBalancerThread`, which waits on an event or periodic timer, trims memory consumers, trims cache via `CcRosTrimCache`, and bugchecks if no progress is possible.
- Creates and prioritizes the balancer thread in `MiInitBalancerThread`.

## Important Behavior

- User trimming uses reverse-map entries to find process/address mappings for a physical page.
- To avoid PFN/address-space lock ordering problems, it repeatedly snapshots rmap entries under PFN lock, then references/attaches to processes and takes working-set locks before touching PTE accessed bits.
- The balancer timer fires every two seconds.
- `PageOutThreadActive` prevents concurrent event-triggered balancing runs.

## Notable Limitations

- `CanWait` in `MmRequestPageMemoryConsumer` is not meaningfully used; failure returns `STATUS_NO_MEMORY`.
- A static delay hack throttles every 100 page requests to give the memory manager recovery time.
- `MmTrimUserMemory` has a circular LRU detection abort path if it returns to the first page.
- Failure to trim when target remains unchanged causes `NO_PAGES_AVAILABLE` bugcheck.
- Some logic is tuned with fixed thresholds (`256` pages) and comments indicate suboptimal behavior.

## Filesystem-Relevant Notes

This file directly affects filesystem/cache pressure. It invokes cache trimming through `CcRosTrimCache`, pages out user pages, and manages page availability for memory consumers such as nonpaged pool and user memory, all of which influence filesystem buffering, mapped-file residency, and paging reliability.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/balance.c -->