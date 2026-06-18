# Group Research: group_1718_reactos_sources_windows_reactos_ntoskrnl_mm_ARM3_expool_c_sources_w_f767cc948cf6

Scope confirmed against `Docs/research_subset_a.md`. All seven listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/expool.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/expool.c

## Purpose

`expool.c` implements ReactOS ARM3 executive pool management: nonpaged and paged pool descriptors, small-block page subdivision, large-page pool allocation tracking, pool tag accounting, quota-aware allocation, debug validation, and public `Ex*Pool*` entry points.

## Main Contents

- Small-pool allocation/free logic with block headers and per-size free lists.
- Large-page pool allocation tracking through `PoolBigPageTable`.
- Pool tag accounting through `PoolTrackTable`.
- Pool descriptor initialization for nonpaged and paged pool.
- Quota-aware allocation wrappers.
- Debug/validation helpers for pool headers, links, tags, IRQL, and allocation ownership.

## Notable Details

- Free-list links are encoded by setting the low bit, and list integrity checks bugcheck on corruption.
- `ExpCheckPoolHeader` and `ExpCheckPoolBlocks` validate page-local block layout and neighbor sizes.
- Large allocations are allocated directly with `MiAllocatePoolPages` and tracked separately from small-pool headers.
- `ExpReallocateBigPageTable` grows/shrinks the large allocation tracker and rehashes live entries.
- The normal tag table does not support expansion in this ReactOS snapshot; overflow is logged and ignored.
- Special pool hooks exist, but driver verifier support is mostly stubbed.
- Session pool and NUMA pool variants are asserted unsupported.
- `ExQueryPoolBlockSize` is unimplemented.

## Integration

This file is the allocator backend used by many kernel subsystems through the exported `ExAllocatePool*` and `ExFreePool*` APIs. It depends on ARM3 page allocation (`MiAllocatePoolPages`, `MiFreePoolPages`), system PFN/pool globals, process quota helpers, and special-pool support.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/expool.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/hypermap.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/hypermap.c

## Purpose

`hypermap.c` implements temporary ARM3 hyperspace and zeroing-space mappings.

## Main Contents

- `MiMapPageInHyperSpace`
  - Maps one physical page into the current process hyperspace.
  - Acquires `Process->HyperSpaceLock`.
  - Uses the first reserved mapping PTE as a descending slot counter.
  - Flushes the process TLB when the hyperspace PTE range wraps.
- `MiUnmapPageInHyperSpace`
  - Clears the mapped PTE.
  - Releases the hyperspace spin lock.
- `MiMapPagesInZeroSpace`
  - Maps a PFN linked list into reserved zeroing PTEs.
  - Requires `PASSIVE_LEVEL`.
  - Uses noncached, write-through PTEs.
- `MiUnmapPagesInZeroSpace`
  - Clears the zeroing PTE range.

## Notable Details

- Hyperspace mapping asserts the target process is the current process.
- Zeroing-space mappings support up to `MI_ZERO_PTES` pages.
- Both mapping pools store their allocation cursor inside the first reserved PTE rather than in a separate variable.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/hypermap.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/i386/init.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/i386/init.c

## Purpose

`i386/init.c` contains x86-specific ARM3 memory-manager initialization.

## Main Contents

- Defines x86 PTE/PDE templates:
  - valid kernel PTE/PDE
  - local valid kernel PTE/PDE
  - demand-zero PTE/PDE
  - prototype PTE
  - decommitted PTE
- `MiInitializeSessionSpaceLayout`
  - Computes session image, view, pool, working-set, and system-view regions.
- `MiComputeNonPagedPoolVa`
  - Tunes initial and maximum nonpaged pool sizes from RAM size and registry-derived globals.
- `MiInitMachineDependent`
  - Clears user-mode PDEs.
  - Places system PTE space, PFN database, and nonpaged pool VA ranges.
  - Allocates page tables for system PTEs, PFN database, nonpaged pool, and expansion space.
  - Maps initial nonpaged pool.
  - Initializes PFN database, color tables, balancer, nonpaged pool, and system PTE allocator.
  - Creates hyperspace and reserved zeroing PTEs.
  - Maps the working set list.
  - Applies the Pentium F00F IDT write-through workaround when needed.
  - Initializes the current process address space.

## Notable Details

- The PFN database is described as a temporary “Shadow PFN Database” placed at `0xB0000000`.
- `MmNonPagedSystemStart` is kept valid for debugger use.
- Percentage-based maximum nonpaged pool sizing is unimplemented.
- The file is specifically the i386 path; PAE/x64 concerns are not implemented here.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/i386/init.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/iosup.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/iosup.c

## Purpose

`iosup.c` implements ARM3 I/O-space mapping helpers.

## Main Contents

- `MiPlatformCacheAttributes`
  - Maps public cache types to ARM3 cache attributes for RAM and device memory.
- `MmMapIoSpace`
  - Validates size and cache type.
  - Computes PFN/page count.
  - Determines whether the mapping is RAM or I/O space.
  - Reserves system PTEs.
  - Configures cached, noncached/write-through, or write-combined PTEs.
  - Installs valid kernel PTEs and returns an offset-adjusted VA.
- `MmUnmapIoSpace`
  - Computes mapped PTE range.
  - Clears PTEs for true I/O-space mappings.
  - Flushes the TLB and releases system PTEs.
- `MmMapVideoDisplay` and `MmUnmapVideoDisplay`
  - Thin wrappers around the I/O-space mapping APIs.
- `MmIsIoSpaceActive`
  - Unimplemented, always returns `FALSE`.

## Notable Details

- Non-AMD64 builds assert the physical address high part is zero.
- Cache/TLB flushing is conservative for noncached and write-combined mappings.
- The file comments note PAE is not respected by the current high-address check.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/iosup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/kdbg.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/kdbg.c

## Purpose

`kdbg.c` provides ARM3 kernel-debugger extensions for pool and IRP inspection. Active code is compiled only under `DBG && KDBG`.

## Main Contents

- `ExpKdbgExtPool`
  - Dumps pool entries for the page containing a given address.
  - Reports paged/nonpaged pool region membership.
  - Can dump payload words for entries.
- `ExpKdbgExtPoolUsed`
  - Parses optional flags/tag filters and calls `MiDumpPoolConsumers`.
- `ExpKdbgExtPoolFind`
  - Searches for allocations by tag.
  - Scans large pool through `PoolBigPageTable`.
  - Scans paged pool through `MmPagedPoolInfo.PagedPoolAllocationMap`.
  - Scans nonpaged pool by brute force.
- `ExpKdbgExtValidatePoolHeader`
  - Filters plausible small-pool headers while scanning.
- `ExpKdbgExtIrpFind`
  - Finds IRP allocations by `TAG_IRP`.
  - Supports filters for device, file object, MDL process, thread, user event, or all argument-style criteria.

## Notable Details

- The file duplicates pool layout macros from `expool.c`.
- Tag parsing supports `?` wildcards through a byte mask.
- Large allocations are found independently of small-pool page headers.
- Heap-wide dumping without an address is explicitly unimplemented.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/kdbg.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/largepag.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/largepag.c

## Purpose

`largepag.c` contains ARM3 large-page support scaffolding. Large-page support is mostly unimplemented in this snapshot.

## Main Contents

- Global state for process tracking, large-page ranges, large-page driver configuration, and a reserved large-page hyperspace PTE.
- `MiInitializeLargePageSupport`
  - On two-level paging, reserves one system PTE, initializes `MmProcessList`, and inserts the current process.
  - On paging levels above two, prints that PAE/x64 large-page support is not implemented.
- `MiSyncCachedRanges`
  - Iterates configured large-page ranges but triggers an unimplemented debug break.
- `MiInitializeDriverLargePageList`
  - Initializes the driver list.
  - Accepts `*` to enable large pages for all drivers.
  - Asserts for explicit driver names because they are unsupported.

## Notable Details

- The only fully successful path is basic state initialization.
- Explicit large-page driver lists are not supported.
- Cached range synchronization is a stub.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/largepag.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/mdlsup.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/mdlsup.c

## Purpose

`mdlsup.c` implements ARM3 Memory Descriptor List support: MDL creation, sizing, page allocation/freeing, page probing/locking, kernel/user mapping, reserved mapping, and process-specific probe-and-lock helpers.

## Main Contents

- `MiMapLockedPagesInUserSpace`
  - Allocates and inserts a `VadDevicePhysicalMemory` VAD.
  - Maps locked MDL PFNs into the current process.
  - Creates valid user PTEs and page-table references.
  - Applies cache attributes and records cache override cases.
- `MiUnmapLockedPagesInUserSpace`
  - Removes the VAD.
  - Clears PTEs.
  - Decrements page-table references and deletes empty PDEs.
- `MmCreateMdl` and `MmSizeOfMdl`
  - Allocate/initialize MDLs and compute required MDL storage.
- `MmBuildMdlForNonPagedPool`
  - Fills an MDL PFN array from existing nonpaged pool PTEs.
- `MmAllocatePagesForMdl` and `MmAllocatePagesForMdlEx`
  - Delegate page allocation to `MiAllocatePagesForMdl`.
- `MmFreePagesFromMdl`
  - Frees pages allocated for an MDL and validates PFN state.
- `MmMapLockedPagesSpecifyCache`
  - Maps MDLs into system PTEs for kernel mode.
  - Delegates user-mode mappings to `MiMapLockedPagesInUserSpace`.
- `MmUnmapLockedPages`
  - Releases kernel system PTE mappings or user VAD mappings.
- `MmProbeAndLockPages`
  - Probes access, faults pages in, resolves user COW when needed, references PFNs, and fills the MDL PFN array.
- `MmUnlockPages`
  - Unmaps mapped MDLs, drops locked-page accounting, and dereferences PFNs.
- `MmMapLockedPagesWithReservedMapping` and `MmUnmapReservedMapping`
  - Use reserved system PTE ranges with two helper PTEs for size/tag metadata.
- `MmProbeAndLockProcessPages`
  - Temporarily attaches to a target process before calling `MmProbeAndLockPages`.

## Unimplemented APIs

- `MmAdvanceMdl`
- `MmPrefetchPages`
- `MmProtectMdlSystemAddress`
- `MmProbeAndLockSelectedPages`
- `MmMapMemoryDumpMdl`

## Notable Details

- User mappings allocate VAD metadata from nonpaged pool and charge process nonpaged-pool quota.
- Kernel mappings consume system PTEs.
- Reserved mappings validate pool-tag ownership and bugcheck with `SYSTEM_PTE_MISUSE` on misuse.
- `MmProbeAndLockPages` uses SEH for probing and raises status on failure.
- AWE, selected pages, memory dump MDLs, and some protection/prefetch paths are unsupported.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/mdlsup.c -->