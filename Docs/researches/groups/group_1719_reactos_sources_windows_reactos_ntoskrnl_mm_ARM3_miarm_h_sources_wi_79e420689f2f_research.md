# Group Research: group_1719_reactos_sources_windows_reactos_ntoskrnl_mm_ARM3_miarm_h_sources_wi_79e420689f2f

Scope: ReactOS ARM3 memory manager support files under `sources/windows/reactos/ntoskrnl/mm/ARM3`, in Research Subset A.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/miarm.h -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/miarm.h

## Role

`miarm.h` is the central private header for the ReactOS ARM3 memory manager. It defines architecture-sensitive page table protection constants, memory-manager policy constants, internal MM/session/pool/PFN data structures, global state declarations, inline helpers, and cross-file prototypes used by ARM3 initialization, paging, VAD, section, pool, and PFN code. Despite the name, it is not ARM-only; it carries conditionals for x86, AMD64, and ARM.

## Key mechanisms

- Defines internal MM protection values (`MM_READONLY`, `MM_READWRITE`, guard/noaccess/decommit encodings) and maps them to architecture-specific PTE bits for x86, AMD64, and ARM. The PTE bit section distinguishes access flags, valid/accessed/dirty bits, cache-disable/write-combine bits, prototype bits, and a per-architecture `PTE_PROTECT_MASK`.
- Provides address classification macros for session space, session images, session PTEs, page-table ranges, system page-table ranges, and page-table/hyperspace ranges. These are used as cheap assertions and policy checks around PTE manipulation.
- Defines ReactOS/NT-style pool metadata (`POOL_DESCRIPTOR`, `POOL_HEADER`, pool tracker tables, big-page trackers) pending a pool merge into executive headers. The definitions encode 32-bit vs 64-bit layout differences and assert header size/alignment.
- Defines session structures (`MMSESSION`, `MM_SESSION_SPACE_FLAGS`, `MM_SESSION_SPACE`) covering session views, session paged pool, session working set support, image lists, Win32K unload hook, and architecture-specific page-table storage.
- Declares nearly all ARM3 global variables: canonical PTE/PDE templates, pool boundaries, session-space boundaries, physical-memory descriptors, PFN coloring data, working-set state, memory threshold events, system cache state, PFN database metadata, process list, zeroing event, expansion lock state, and section/VAD roots.
- Implements inline PTE constructors: `MI_MAKE_HARDWARE_PTE_KERNEL`, `MI_MAKE_HARDWARE_PTE`, `MI_MAKE_HARDWARE_PTE_USER`, `MI_MAKE_TRANSITION_PTE`, and for non-AMD64 builds, prototype/subsection PTE encoders. The user/global owner selection is centralized in `MiDetermineUserGlobalPteMask`.
- Implements low-level PTE/PDE write helpers (`MI_WRITE_VALID_PTE`, `MI_UPDATE_VALID_PTE`, `MI_WRITE_INVALID_PTE`, `MI_ERASE_PTE`, `MI_WRITE_VALID_PDE`, `MI_WRITE_INVALID_PDE`) with assertions that enforce valid/invalid state transitions and page-frame consistency.
- Implements working-set lock helpers for process, system cache, and session working sets. The helpers track ownership on `ETHREAD`, enter/leave guarded regions for safe acquisitions, support shared/exclusive variants, handle unsafe fault-time acquisitions, and provide conversion from shared to exclusive.
- Implements PFN lock-count/reference helpers used by MDL probing and locked-page accounting: `MiDropLockCount`, `MiDereferencePfnAndDropLockCount`, `MiReferenceProbedPageAndBumpLockCount`, `MiReferenceUsedPageAndBumpLockCount`, and `MiReferenceUnusedPageAndBumpLockCount`.
- Declares the main initialization and subsystem entry points: `MmArmInitSystem`, session-space layout/init, machine-dependent init, PFN database mapping/initialization, color tables, memory events, system PTE reserve/release, MDL page allocation, PFN list manipulation, VAD lookup/insertion/removal, section view unmapping, address validation, pageable VM deletion, system image write-protection, and PDE deletion.
- Provides page-table reference accounting for two-level builds through `MmWorkingSetList->UsedPageTableEntries`, and for three/four-level builds through PFN `OriginalPte.u.Soft.UsedPageTableEntries`. `MiDeletePde` cascades deletion up the paging hierarchy when reference counts hit zero.

## Dependencies and coupling

- Depends on kernel-wide ReactOS NT structures and macros from `ntoskrnl.h`, including `MMPTE`, `MMPDE`, `MMPFN`, `MMSUPPORT`, `EPROCESS`, `ETHREAD`, page-table address macros, PFN database accessors, push locks, guarded regions, and cache/PTE manipulation macros.
- Serves as the shared private contract for the ARM3 files in this directory. Many `.c` files include it after defining `MODULE_INVOLVED_IN_ARM3`.
- The header is tightly coupled to Windows NT memory-manager layout assumptions: session-space virtual layout, paged/nonpaged pool boundaries, system PTE pools, PFN database representation, VAD AVL tables, and prototype/subsection PTE packing.
- Several areas are explicitly transitional or incomplete, including comments such as `FIXFIX` around pool definitions and commit accounting warnings for prototype PTE lock-count changes.

## Research notes

- This file is high-value architectural glue rather than a standalone implementation. When following behavior in other ARM3 files, most invariants around PTE construction, working-set ownership, and PFN reference accounting are defined here.
- The inline assertions are part of the design: they document assumptions about caller lock ownership, valid page-table state, non-session vs session mappings, and page-frame identity.
- The file includes architecture-sensitive branches; any research using it should note target architecture because prototype PTE encoding, page-table reference accounting, and user PTE/PDE detection differ by paging level.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/miarm.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/miavl.h -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/miavl.h

## Role

`miavl.h` is the glue layer that adapts ReactOS/RTL AVL tree algorithms for ARM3 memory-manager VAD trees. It renames generic RTL AVL routines into `Mi*` symbols and supplies memory-manager-specific node accessors, comparison, parent/balance packing, and child insertion helpers.

## Key mechanisms

- Aliases `PRTL_AVL_TABLE` to `PMM_AVL_TABLE` and `PRTL_BALANCED_LINKS` to `PMMADDRESS_NODE`, allowing generic AVL code to compile against MM VAD structures.
- Renames core AVL routines (`RtlpFindAvlTableNodeOrParent`, promotion, rebalancing, insert, delete) to `Mi*` names to avoid symbol conflicts if not inlined.
- Provides `MiAvlCompareRoutine`, which treats the lookup buffer as a `StartingVpn` and compares it against a node's inclusive `[StartingVpn, EndingVpn]` range. This is the core VAD containment comparison.
- Handles the MM-specific packed parent/balance representation. `MiSetParent` preserves the low two balance bits when replacing the parent pointer; `MiParentAvl` masks those bits off when retrieving the parent.
- Exposes child/relationship helpers (`MiRightChildAvl`, `MiLeftChildAvl`, `MiIsLeftChildAvl`, `MiIsRightChildAvl`) and insertion helpers that set parent links as they attach nodes.

## Dependencies and coupling

- Requires the `MMADDRESS_NODE` layout where `u1.Parent` and `u1.Balance` share storage and where `StartingVpn`/`EndingVpn` live inline in the node.
- Intended to be included before or with the generic AVL implementation so macro renames affect the compiled symbols.
- Used by VAD tree operations declared in `miarm.h`, including lookup, conflict detection, empty-range search, insertion, and removal.

## Research notes

- The low-bit parent packing assumes parent pointers are at least 4-byte aligned; the header comments say at least 8-byte aligned, which is sufficient for the two low balance bits.
- The compare routine returns equality for any VPN inside the node range, not just exact start matches, which is why it is appropriate for VAD interval lookup.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/miavl.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/mmdbg.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/mmdbg.c

## Role

`mmdbg.c` implements ARM3 memory-manager support for kernel debugger memory copies. It provides translation of physical addresses through a reserved debug mapping PTE and implements `MmDbgCopyMemory` for small aligned reads/writes of physical or virtual memory.

## Key mechanisms

- Maintains `MiDebugMapping` initialized to `MI_DEBUG_MAPPING` and `MmDebugPte`, which is set during memory initialization once debugger physical-memory support is ready.
- `MiDbgTranslatePhysicalAddress` rejects early calls before `MmDebugPte` is initialized, rejects cache-mode flags because cached/uncached/write-combined debug mappings are not implemented, rejects I/O-space PFNs with no PFN database entry, then writes a temporary valid kernel PTE for the requested PFN and invalidates the mapping TLB entry.
- `MiDbgUnTranslatePhysicalAddress` clears the debug PTE and invalidates the TLB entry after a physical copy.
- `MmDbgCopyMemory` supports only 1-, 2-, 4-, and 8-byte transfers, enforced by `MMDBG_COPY_MAX_SIZE == 8`, and rejects unaligned requests.
- For `MMDBG_COPY_PHYSICAL`, it maps the physical address through the debug PTE. For virtual copies, it checks `MmIsAddressValid`, notes session-space handling as a FIXME, and if a write targets a non-writable PTE, falls back to a physical write through the page frame.
- Performs typed scalar copies rather than arbitrary `memcpy`, matching the limited debugger transfer sizes.

## Dependencies and coupling

- Depends on `miarm.h` for `ValidKernelPte`, `MiPteToAddress`, `MiAddressToPte`, `MiGetPfnEntry`, `MI_IS_PAGE_WRITEABLE`, and page/TLB helpers.
- Depends on `MmDebugPte` being initialized by `MmArmInitSystem` in `mminit.c`.
- Uses `MmIsAddressValid`, declared elsewhere and implemented in `mmsup.c`, for virtual and debug mapping validation.

## Limitations and risks

- Debug cache flags are explicitly unsupported.
- Physical I/O space is explicitly unsupported because `MiDbgTranslatePhysicalAddress` requires a PFN database entry.
- Local kernel-debugger locking is not implemented; missing `MMDBG_COPY_UNSAFE` only logs once and does not change behavior.
- Session-space handling is marked incomplete.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/mmdbg.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/mminit.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/mminit.c

## Role

`mminit.c` is the ARM3 memory-manager initialization implementation. It sizes and initializes physical-memory metadata, the PFN database, color tables, pool and system PTE regions, session-space layout, memory threshold events, system cache parameters, boot-loader memory release, and global tuning values used by later MM subsystems.

## Key mechanisms

- Defines the global memory layout state declared in `miarm.h`: nonpaged pool/system PTE boundaries, paged pool start/end/size, session-space boundaries, system view space, system cache, physical-memory descriptors, highest/lowest physical pages, user/kernel address split, PFN bitmap, memory threshold events, page coloring data, and system sizing/tuning variables.
- `MiScanMemoryDescriptors` walks the loader memory descriptor list, counts descriptors, excludes invisible memory from physical-page totals, finds lowest/highest physical PFNs, counts free pages, and selects the largest free descriptor for early contiguous boot allocations. `MxGetNextPage` then consumes pages from that descriptor and bugchecks if it runs dry.
- `MiComputeColorInformation` derives secondary page colors from L2 cache size/associativity, bounds the value to allowed min/max/default values, requires power-of-two colors, and publishes the mask to the current PRCB.
- `MiInitializeColorTables` maps and zeros the color-table storage immediately after the PFN database, then initializes zeroed/free page-color list heads for each color.
- Non-AMD64 PFN setup maps only regular physical memory into the PFN database. `MiMapPfnDatabase` maps PFN database pages using early free pages, `MiBuildPfnDatabaseFromPages` records already-valid startup PDE/PTE mappings, `MiBuildPfnDatabaseZeroPage` protects PFN 0 when appropriate, `MiBuildPfnDatabaseFromLoaderBlock` classifies free, bad, invisible, boot, and ROM loader pages, and `MiBuildPfnDatabaseSelf` accounts for pages backing the PFN database itself.
- `MmFreeLoaderBlock` gathers reclaimable loader ranges for registry, loader heap, and NLS data; under the PFN lock it either inserts unreferenced pages into the free list or clears/deletes referenced mappings and decrements share counts, then flushes the current TLB.
- `MiNotifyMemoryEvents`, `MiCreateMemoryEvent`, and `MiInitializeMemoryEvents` establish the public kernel memory condition events (`LowMemoryCondition`, `HighMemoryCondition`, paged-pool and nonpaged-pool variants), with ACLs that allow query rights to everyone and full access to administrators/system. Threshold defaults scale with physical memory.
- `MiAddHalIoMappings` scans HAL virtual address mappings and warns for valid HAL I/O mappings that lack PFN database entries, noting missing cache coherency/PAT tracking.
- `MmDumpArmPfnDatabase` is a diagnostic routine that raises IRQL, scans the PFN database, reports active/free/other pages, and when `MI_TRACE_PFNS` is enabled, buckets pages by usage class.
- `MmInitializeMemoryLimits` compacts included loader descriptors into a `PHYSICAL_MEMORY_DESCRIPTOR`, merging contiguous descriptors and resizing the allocation if the initial run estimate was too large.
- `MiBuildPagedPool` sizes paged pool, handles x86 VA constraints, initializes the shadow/double-mapped system page directory on two-level paging, allocates the first paged-pool PDE, initializes paged-pool allocation/end bitmaps, initializes paged pool and special pool, sets paged-pool thresholds, and initializes the global session-space map.
- `MmArmInitSystem` is the main phase-driven entry point. Phase 0 scans loader descriptors, initializes temporary event pointers, user/kernel address split, session layout, global lists/locks/events, system PTE sizing, heap and stack tuning, color information, PFN allocation sizing, machine-dependent setup, physical memory block and PFN bitmap, cached-range/HAL mapping checks, resident-page counts, large-page/driver lists, boot-driver relocation, system-size/product-type tuning, system cache bounds, commit limit, paged pool, debugger PTE, and loaded-module list.

## Dependencies and coupling

- Includes `miarm.h` and depends heavily on all ARM3 inline helpers, especially page-table address translation, PTE/PDE write helpers, PFN lock/list helpers, and system PTE reservation.
- Depends on loader-provided `LOADER_PARAMETER_BLOCK` and `MEMORY_ALLOCATION_DESCRIPTOR` ordering and type values.
- Calls machine- and subsystem-specific routines declared in `miarm.h`, including `MiInitMachineDependent`, `MiInitializeSessionSpaceLayout`, `MiInitializeLargePageSupport`, `MiInitializeDriverLargePageList`, `MiReloadBootLoadedDrivers`, `MiInitializeSystemPtes`, `MiInitializeSystemSpaceMap`, and pool initialization routines.
- Establishes globals consumed by later files in this group: `MmDebugPte` in `mmdbg.c`, working-set limits in `mmsup.c`, and cache/PTE templates used by `ncache.c`.

## Limitations and risks

- Several comments document incomplete or temporary behavior: registry configurability is not fully supported, system cache initialization is commented out, HAL I/O mapping cache coherency tracking is incomplete, driver verifier initialization is a FIXME, and many values are hardcoded NT-like defaults.
- Physical-memory initialization is architecture-conditional. The non-AMD64 path contains substantial PFN database construction that is not compiled on AMD64.
- Early allocation relies on the largest free loader descriptor and bugchecks if it cannot satisfy required PFN/color-table mappings.
- `MmArmInitSystem` returns success unconditionally outside explicit failure paths and contains a large amount of policy in one initializer, making order dependencies important.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/mminit.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/mmsup.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/mmsup.c

## Role

`mmsup.c` contains small ARM3 memory-manager support routines exposed through NT MM APIs. It mixes implemented query/validation helpers with several unimplemented public stubs.

## Key mechanisms

- Defines working-set global counters: `MmMinimumWorkingSetSize`, `MmMaximumWorkingSetSize`, and `MmPagesAboveWsMinimum`.
- `MmAdjustWorkingSetSize` handles the normal resizing path for the current process working set. It locks the process `Vm` working set, derives requested min/max page counts, clamps to global min/max, rejects min greater than max, checks privilege/resource conditions for increases, updates resident available pages and global pages-above-minimum accounting, and writes the new process working-set bounds.
- `MmIsAddressValid` walks the paging hierarchy according to `_MI_PAGING_LEVELS`: PXE, PPE, PDE, then PTE. It returns false on any invalid level and true only when the final PTE is valid. The comment warns the result remains stable only if the caller holds the PFN lock.
- `MmIsNonPagedSystemAddressValid` warns that it returns a bogus result and delegates to `MmIsAddressValid`.
- `MmIsRecursiveIoFault` checks thread flags `DisablePageFaultClustering` and `ForwardClusterOnly`.
- `MmIsThisAnNtAsSystem` returns whether `MmProductType` indicates a server system; `MmQuerySystemSize` returns `MmSystemSize`.
- Stubbed/unimplemented routines include `MmMapUserAddressesToPage`, the working-set emptying special case in `MmAdjustWorkingSetSize`, `MmSetAddressRangeModified`, `MmSetBankedSection`, and `MmCreateMirror`.

## Dependencies and coupling

- Includes `miarm.h` for working-set lock helpers and page-table address helpers.
- Uses `PsGetCurrentProcess`, `PsGetCurrentThread`, thread flags, process `Vm`, and global available/resident/system-lock page counters initialized or tuned elsewhere.
- Uses `MmProductType` and `MmSystemSize` initialized in `mminit.c`.

## Limitations and risks

- Multiple public APIs are stubs returning `STATUS_NOT_IMPLEMENTED` or `FALSE`.
- `MmIsNonPagedSystemAddressValid` explicitly logs that its result is not trustworthy.
- `MmIsAddressValid` is a snapshot check; callers that need stability must hold the PFN lock or otherwise prevent invalidation.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/mmsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/ncache.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/ncache.c

## Role

`ncache.c` implements the noncached memory allocation and free APIs for ARM3: `MmAllocateNonCachedMemory` and `MmFreeNonCachedMemory`.

## Key mechanisms

- `MmAllocateNonCachedMemory` validates a nonzero byte count, computes the required page count, chooses the platform noncached cache attribute through `MiPlatformCacheAttributes[0][MmNonCached]`, and delegates physical page allocation to `MiAllocatePagesForMdl`.
- Rejects partial MDL allocations: it computes the pages spanned by the MDL virtual address and byte count and frees the MDL/pages if the returned page count is less than requested.
- Reserves system PTEs for the allocation plus one extra PTE. The extra PTE slot stores the MDL pointer so `MmFreeNonCachedMemory` can recover it from only the returned base address and size.
- Builds a valid kernel PTE template and adjusts cache bits for `MiNonCached` (`MI_PAGE_DISABLE_CACHE`, `MI_PAGE_WRITE_THROUGH`) or `MiWriteCombined` (`MI_PAGE_DISABLE_CACHE`, `MI_PAGE_WRITE_COMBINED`).
- Iterates the MDL PFN array and writes one valid PTE per page with `MI_WRITE_VALID_PTE`, returning the virtual address corresponding to the first real reserved PTE.
- `MmFreeNonCachedMemory` asserts nonzero size and page-aligned base, computes page count, finds the first mapping PTE, steps back to the hidden MDL pointer slot, frees pages and the MDL, then releases the full system PTE range including the extra slot.

## Dependencies and coupling

- Uses `miarm.h` for `MiAllocatePagesForMdl`, `MiReserveSystemPtes`, `MiReleaseSystemPtes`, `MiPteToAddress`, `MiAddressToPte`, `ValidKernelPte`, cache attribute tables, and PTE write/cache macros.
- Depends on MDL layout where PFN entries begin immediately after the `MDL` structure.
- Uses system PTE space as the virtual mapping substrate, so availability of system PTEs directly limits allocations.

## Limitations and risks

- The MDL pointer is hidden in the PTE immediately before the returned mapping. This is compact but makes correctness depend on freeing only exact addresses returned by `MmAllocateNonCachedMemory`.
- No runtime handling is present for a zero size or unaligned free address beyond assertions.
- Cache policy depends on `MiPlatformCacheAttributes`; the allocator itself only handles noncached/write-combined/silent default cases.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/ncache.c -->