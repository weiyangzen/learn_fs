# Group Research: group_1720_reactos_sources_windows_reactos_ntoskrnl_mm_ARM3_pagfault_c_sources_80758fda6cfd

Scope checked against `Docs/research_subset_a.md`: `sources/windows/reactos` is included. Read coverage: all 4 listed source files were read completely.

This group covers ReactOS ARM3 memory-manager internals around page faults, PFN list accounting, pool page allocation, and process address-space support. The files are tightly coupled: `pagfault.c` consumes PFN allocation/reference helpers from `pfnlist.c`; `pool.c` consumes PFN/system-PTE mechanisms to back paged and nonpaged pool; `procsup.c` creates process page directories, hyperspace, working-set pages, stacks, PEBs, and TEBs using the same PFN and fault machinery.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/pagfault.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/pagfault.c

This file implements ARM3 page-fault handling for ReactOS, including user/kernel fault routing, demand-zero faults, transition faults, pagefile faults, prototype PTE faults, copy-on-write, guard-page stack growth, session/paged-pool PDE fixups, and process execute-option APIs.

Core responsibilities:
- `MmArmAccessFault` is the top-level fault handler. It separates high-IRQL faults, kernel faults, page-table/hyperspace faults, and user faults.
- `MiDispatchFault` handles the lower-level PTE state machine after locks and address validity have been established.
- `MiResolveDemandZeroFault`, `MiResolveTransitionFault`, `MiResolvePageFileFault`, and `MiResolveProtoPteFault` implement the major invalid-PTE recovery paths.
- `MiAccessCheck` and `MiIsAccessAllowed` enforce software protection bits before resolving user faults.
- `MiCheckVirtualAddress` maps a virtual address to VAD/protection/prototype-PTE information.
- `MiCheckForUserStackOverflow` consumes guard-page faults to extend user stacks or report stack overflow.
- `MmGetExecuteOptions` and `MmSetExecuteOptions` expose process NX/execute policy flags.

Major control flow:
- High-IRQL faults are only allowed when all required paging structures are already valid. Invalid entries lead to an in-page-style failure or bugcheck diagnostics.
- Kernel faults reject user-mode access to kernel addresses, validate upper paging levels, handle paged-pool/session PDE fixups on 2-level paging, then take the system or session working-set lock and dispatch.
- User faults take the process working-set lock, allocate missing PXE/PPE/PDE page-table pages as demand-zero pages, then handle valid PTE write/COW/NX cases or invalid PTE resolution.
- Empty user PTEs are checked against the VAD tree. If committed private memory, the code creates a software PTE and allocates a zeroed physical page. If section-backed, it creates or follows a prototype PTE.
- Guard pages are converted to non-guard protection and delegated to stack-overflow/stack-extension handling after dropping the working-set lock.

Important data and invariants:
- `HYDRA_PROCESS` is a sentinel process pointer for session-backed faults.
- `UserPdeFault` is only present when PFN tracing is enabled and annotates page-table demand-zero allocation.
- Fault paths assume APCs are disabled and IRQL is at most APC_LEVEL except the special high-IRQL case.
- PFN-lock ownership is central. Some helpers release the PFN lock internally, especially prototype-fault completion.
- Hardware PTE construction is split between user and kernel mappings through `MI_MAKE_HARDWARE_PTE_USER` and `MI_MAKE_HARDWARE_PTE`.

Demand-zero behavior:
- `MiResolveDemandZeroFault` chooses zeroed, free, or any colored page depending on process context, session image/view addresses, and whether the caller already owns the PFN lock.
- It initializes the PFN, updates demand-zero counters, optionally zeroes the page outside the lock, writes a valid PTE, and increments `NumberOfPrivatePages` for real processes.
- User PDE faults are treated as kernel PTE mappings for page tables.

Prototype and transition behavior:
- `MiCompleteProtoPteFault` converts a valid prototype PTE into a process PTE, updates PFN share counts, applies protection/caching, and releases the PFN lock.
- `MiResolveProtoPteFault` handles valid proto PTEs, reserved section access, COW on write-copy mappings, transition prototype PTEs, and demand-zero prototype backing.
- COW creates a private page with `MiCopyPfn`, deletes the old PTE reference, initializes the new PFN, converts write-copy to read-write, and writes a private valid PTE.
- Transition faults remove standby/free pages from lists, bump references/share counts, restore active-valid state, and may wait on in-progress read/write events.

Pagefile behavior:
- `MiResolvePageFileFault` allocates a replacement page, marks it read-in-progress, writes a transition PTE before dropping the PFN lock, reads from the pagefile, reacquires the lock, then makes the PTE valid and wakes waiters.
- The path asserts a real process context and a held PFN lock, and treats failed paging I/O as an assertion/in-page error path.

Notable limitations and risk points:
- Many Windows-compatible cases are explicitly asserted rather than implemented: AWE VADs, physical-memory VADs, image VADs in some paths, clone PTEs, mapped-file paged-out prototype PTEs, large pages, and some session-space paths.
- Session-space support is incomplete outside the 2-level paging implementation, with an explicit warning.
- Double transition faults are not supported.
- Clustered prototype faults are stubbed to a single PTE.
- Stack guarantee support is asserted to zero, so guaranteed stack bytes are not implemented.
- `MiAccessCheck` ignores the `Execute` argument in callers except through the local helper, and most fault execute checks happen later on valid PTEs.
- Many failure modes are debug assertions or bugchecks rather than recoverable statuses, reflecting ARM3 incompleteness in this ReactOS snapshot.

<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/pagfault.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/pfnlist.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/pfnlist.c

This file implements PFN list manipulation for ARM3: free, zeroed, standby, modified, modified-no-write, bad, ROM-list metadata, colored page queues, available-page accounting, PFN initialization, and share/reference-count transitions.

Core globals:
- `MmZeroedPageListHead`, `MmFreePageListHead`, `MmStandbyPageListHead`, `MmModifiedPageListHead`, `MmModifiedNoWritePageListHead`, `MmBadPageListHead`, and `MmRomPageListHead` are the principal page-list heads.
- `MmStandbyPageListByPriority[8]` and `MmModifiedPageListByColor[1]` provide specialized queues.
- `MmPageLocationList[]` maps page-location enum values to list heads.
- `MmTransitionSharedPages` and `MmTotalPagesForPagingFile` track transition and paging-file-backed modified pages.
- PFN tracing state is stored in `MI_PFN_CURRENT_USAGE` and `MI_PFN_CURRENT_PROCESS_NAME`.

Main list operations:
- `MiIncrementAvailablePages` and `MiDecrementAvailablePages` maintain `MmAvailablePages` and signal/clear low/high memory events.
- `MiZeroPhysicalPage` maps a PFN through hyperspace and zeroes it.
- `MiUnlinkFreeOrZeroedPage` removes a PFN from the free or zeroed list and its colored list.
- `MiUnlinkPageFromList` removes transition pages from standby/modified lists and updates transition counters.
- `MiRemovePageByColor`, `MiRemoveAnyPage`, and `MiRemoveZeroPage` select and remove pages, preferring requested color lists where possible.
- `MiInsertPageInFreeList`, `MiInsertStandbyListAtFront`, and `MiInsertPageInList` insert pages into the appropriate list and auxiliary colored/priority structures.

PFN initialization:
- `MiInitializePfn` binds a physical page to a PTE, copies or synthesizes the original PTE, sets reference/share counts, marks it active and valid, sets modified state, determines the containing page-table PFN, and increments that page-table share count.
- `MiInitializePfnAndMakePteValid` is a combined PFN-init plus valid-PTE write helper.
- `MiInitializeAndChargePfn` allocates a zero page for a PDE, writes it valid, and initializes the PFN for another process/session.
- `MiInitializePfnForOtherProcess` initializes PFNs whose containing page table is supplied explicitly.

Reference and share count behavior:
- `MiDecrementShareCount` decrements mapping share count, converts prototype PTEs to transition PTEs when the last share disappears, and either frees deleted PFNs or drops references.
- `MiDecrementReferenceCount` handles ReactOS legacy PFNs via `MmDereferencePage`, validates counts, then puts fully unreferenced pages on the modified or standby list unless the PFN was deleted.
- Deleted PFNs are returned to the free list when their final reference disappears.

Important invariants:
- Most routines require the PFN lock and assert it.
- Free/zero lists are mirrored into per-color queues using `OriginalPte.u.Long` and `u4.PteFrame` as colored-list links.
- Free and zeroed pages must have zero reference and share counts.
- Transition pages are expected to be standby or modified pages, with prototype-PTE constraints in the supported ARM3 paths.
- `ASSERT_LIST_INVARIANT` verifies list heads are either fully empty or fully linked.

Notable limitations and risk points:
- Standby-list fallback in `MiRemoveAnyPage` and `MiRemoveZeroPage` is marked FIXME and not implemented.
- Modified-no-write list insertion/removal asserts false.
- Some modified-page support is limited to pagefile-backed single-prototype assumptions.
- There are several "ReactOS Hack" comments clearing `OriginalPte.u.Long` after unlinking, which shows the colored-list overlay is delicate.
- `MiDecrementReferenceCount` treats very high reference counts as corruption and asserts.
- Low-memory handling calls `MmRebalanceMemoryConsumers`, with comments noting missing modified-page-writer and working-set-manager wakeups.

<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/pfnlist.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/pool.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/pool.c

This file implements ARM3 pool page allocation support: paged-pool virtual allocation through bitmaps and demand-zero PTEs, nonpaged-pool page allocation through free-list descriptors, nonpaged expansion backed by system PTEs and PFNs, protected freed-pool support, pool threshold events, session pool setup, process quota helpers, and mapping-address reservation APIs.

Core globals:
- `MmNonPagedPoolFreeListHead[]` stores nonpaged free blocks bucketed by page count.
- `MmPagedPoolInfo` stores paged-pool PTE bounds, allocation bitmap, end-of-allocation bitmap, hint, and expansion state.
- `MmNumberOfFreeNonPagedPool`, `MmAllocatedNonPagedPool`, and quota totals track pool capacity and accounting.
- `MmProtectFreedNonPagedPool` enables invalidating freed nonpaged pool PTEs to catch use-after-free.
- `MiNonPagedPoolSListHead` and `MiPagedPoolSListHead` cache one-page allocations for fast reuse.

Protected freed-pool support:
- `MiProtectFreeNonPagedPool` invalidates freed pool PTEs and marks them with the prototype bit so faults can be recognized as freed-pool accesses.
- `MiUnProtectFreeNonPagedPool` restores those PTEs when list manipulation needs to touch freed block metadata.
- `MiProtectedPoolUnProtectLinks`, `MiProtectedPoolProtectLinks`, `MiProtectedPoolInsertList`, and `MiProtectedPoolRemoveEntryList` wrap list operations so free-list links remain accessible only while needed.

Initialization:
- `MiInitializeNonPagedPoolThresholds` computes low/high nonpaged-pool thresholds based on maximum pool size.
- `MiInitializePoolEvents` initializes low/high paged and nonpaged pool events from current free capacity.
- `MiInitializeNonPagedPool` initializes S-lists, disables them under freed-pool protection, creates the initial single free block over initial nonpaged pool, marks per-page owners/signatures, records initial pool PFN frame bounds, and initializes nonpaged expansion system PTEs behind guard pages.
- `MiInitializeSessionPool` initializes session paged pool: descriptor, address bounds, PDE/PTE metadata, first page table, allocation bitmap, and end bitmap.

Allocation behavior:
- `MiAllocatePoolPages` handles both paged and nonpaged pool.
- Paged pool uses `RtlFindClearBitsAndSet` over `PagedPoolAllocationMap`, expands by allocating page tables if necessary, writes demand-zero writable PTEs, marks allocation ends in `EndOfPagedPoolBitmap`, and returns virtual space.
- One-page paged-pool allocations may be served from `MiPagedPoolSListHead`.
- Nonpaged pool first tries `MiNonPagedPoolSListHead` for one-page allocations, then searches bucketed free-list entries.
- Nonpaged free blocks are split from the tail of a free entry. PFN flags mark `StartOfAllocation`, `EndOfAllocation`, and optional verifier allocation.
- If initial nonpaged pool has no suitable block, the allocator reserves system PTEs from `NonPagedPoolExpansion`, allocates physical pages, initializes PFNs, writes valid kernel PTEs, and returns the mapped VA.

Free behavior:
- `MiFreePoolPages` handles paged-pool frees by finding allocation length from `EndOfPagedPoolBitmap`, optionally caching one-page frees in the S-list, deleting pageable system VM, and clearing allocation bits.
- Nonpaged frees find the allocation length through PFN `EndOfAllocation`, optionally cache one-page frees, clear PFN allocation flags, and coalesce adjacent free blocks before and after the freed range.
- Free block descriptors use `MM_FREE_POOL_SIGNATURE`, `Size`, `Owner`, and list links on page-aligned chunks.
- Protected-pool mode temporarily unprotects adjacent free descriptors during coalescing and reprotects the final free block.

Quota and mapping-address APIs:
- `MmRaisePoolQuota` raises per-process pool quota under `PspQuotaLock`, with availability checks for nonpaged and paged pool.
- `MmReturnPoolQuota` returns quota to global counters.
- `MmAllocateMappingAddress` reserves system PTEs plus two metadata PTEs storing size and pool tag.
- `MmFreeMappingAddress` validates the tag, size, and that all reserved mapping PTEs are empty before releasing the system PTE range.

Notable limitations and risk points:
- S-list caching returns one-page pool allocations without immediately clearing allocation metadata or deleting backing pages, so correctness depends on callers treating them as same-size page-cache reuse.
- Nonpaged-pool expansion manually initializes PFNs instead of using `MiInitializePfn`, and uses `MI_USAGE_PAGED_POOL` labels even while allocating nonpaged expansion pages.
- Protected freed-pool relies on invalid PTEs marked as prototype; `pagfault.c` recognizes this and bugchecks on freed nonpaged pool modification.
- Paged-pool expansion is constrained by available PDE/PTE range and returns NULL on bitmap/PDE exhaustion.
- Session pool has architecture-specific FIXME behavior around AMD64 page-table recording.
- `MmDeterminePoolType` bugchecks if an address is outside known paged/nonpaged ranges.

<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/pool.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/procsup.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/procsup.c

This file implements ARM3 process-related memory management: PEB/TEB VAD creation and deletion, kernel stack allocation/growth/freeing, memory-priority setting, PEB/TEB initialization, process address-space initialization/cleanup/deletion, hand-built process setup, and unimplemented AWE-style user physical page syscalls.

Core globals:
- `MmProcessColorSeed` seeds per-process page-color selection.
- `MmMaximumDeadKernelStacks` and `MmDeadStackSListHead` implement a small cache of dead non-GUI kernel stacks.
- `MmRotatingUniprocessorNumber` rotates affinity for uniprocessor-only images.

PEB and TEB support:
- `MiCreatePebOrTeb` allocates an `MMVAD_LONG`, charges nonpaged quota, initializes a private committed read-write no-change VAD, and inserts it top-down. PEB placement adds a small randomized offset near the highest VAD address.
- `MmCreatePeb` attaches to the target process, maps NLS data, creates the PEB VAD, initializes PEB fields, reads image headers/config under SEH, applies version, CSD, affinity, subsystem, and debugging fields, then returns the PEB address.
- `MmCreateTeb` attaches to the target process, creates the TEB VAD, initializes TIB/TEB identity, stack bounds, client IDs, locale, PEB pointer, and static Unicode string.
- `MmDeleteTeb` attaches to the process, locks address creation and working set, removes the TEB VAD, deletes the virtual address range, frees the VAD, and returns VAD quota.

Kernel stack support:
- `MmCreateKernelStack` reserves system PTEs plus a guard page, allocates and maps committed stack pages, initializes PFNs, and returns the top of stack. GUI stacks reserve a larger range but initially commit only `KERNEL_LARGE_STACK_COMMIT`.
- Non-GUI stacks can be reused from `MmDeadStackSListHead`.
- `MmDeleteKernelStack` pushes small non-GUI stacks to the dead-stack S-list when possible; otherwise it walks stack PTEs, marks PFNs deleted, decrements page-table and page share counts, and releases system PTEs.
- `MmGrowKernelStackEx` validates growth against reserved stack space, allocates pages down to the requested new limit, writes valid stack PTEs, and updates `Thread->StackLimit`.
- `MmGrowKernelStack` calls the extended version with the large-stack commit size.

Process address-space creation:
- `MmCreateProcessAddressSpace` allocates zeroed pages for the process directory table, hyperspace, and working-set list, records them in `DirectoryTableBase` and `WorkingSetPage`, calls architecture-specific setup, moves initialization to phase 1, and adds the process to session tracking.
- `MmInitializeProcessAddressSpace` attaches to the process, initializes locks and VAD root, initializes PFNs for the process page-directory/hyperspace/working-set pages, initializes the working-set list, records the owning process in the page-directory PFN, optionally inserts an AMD64 shared-user-page VAD, maps the executable section, stores image name/audit name, and completes phase 2.
- `MmInitializeHandBuiltProcess` shares directory bases and working-set data with the idle/current process for bootstrapped processes.
- `MmInitializeHandBuiltProcess2` is a placeholder that currently returns success.

Cleanup and deletion:
- `MmCleanProcessAddressSpace` removes the process from its session, skips incomplete address spaces with a warning, marks VM deleted, walks all VADs, delegates legacy ReactOS memory areas to RosMm, removes ARM3 VADs, unmaps section views or deletes private ranges, frees VADs, returns quota, deletes shared user data, and unlocks the address space.
- `MmDeleteProcessAddressSpace` removes the process from memory-manager lists, deletes working-set, hyperspace, and directory-table PFNs for fully initialized processes, releases session references, and clears directory table bases.
- Partially initialized address spaces are warned as possible leaks.

Other APIs:
- `MmSetMemoryPriorityProcess` stores process memory priority, forcing background priority on very small systems.
- `MiInsertSharedUserPageVad` exists only for AMD64 and inserts a read-only VAD for `MM_SHARED_USER_DATA_VA`.
- `NtAllocateUserPhysicalPages`, `NtMapUserPhysicalPages`, `NtMapUserPhysicalPagesScatter`, and `NtFreeUserPhysicalPages` are explicit `UNIMPLEMENTED` stubs returning `STATUS_NOT_IMPLEMENTED`.

Notable limitations and risk points:
- Cleanup has explicit legacy interop with RosMm VADs, so address-space teardown depends on mixed ARM3/RosMm ownership checks.
- Partially initialized address spaces may leak resources by design.
- Stack caching avoids freeing small non-GUI stacks until the dead-stack cache fills.
- `MmCreatePeb` and `MmCreateTeb` may return after SEH failures without fully undoing all earlier allocations or mappings in every branch.
- AWE/user physical pages are not implemented.
- Several process initialization routines depend on architecture-specific page-table layout and `MiArchCreateProcessAddressSpace`.

<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/procsup.c -->