# Research: subset-b-000663

Grouped source research for subset B work item `subset-b-000663`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/nommu.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/nommu.c

## Purpose
This file provides the ARM no-MMU memory-management support path. It reserves exception-vector memory, chooses an MPU setup backend, initializes boot memory, supplies no-MMU cache flush helpers, and implements identity-style I/O remapping for systems where physical and kernel virtual addresses are effectively the same.

## Important APIs, Types, and Functions
Important state is `vectors_base`, plus `mpu_rgn_info` when `CONFIG_ARM_MPU` is enabled. `setup_vectors_base()` configures high vectors or VBAR depending on `CONFIG_CPU_HIGH_VECTOR`, `CONFIG_REMAP_VECTORS_TO_RAM`, and security extension availability. `arm_mm_memblock_reserve()` reserves vector pages and address zero. `adjust_lowmem_bounds()` calls the PMSA-specific low-memory adjustment, updates `high_memory`, and caps memblock allocation. `paging_init()` initializes traps, programs the MPU, and calls `bootmem_init()`.

Runtime APIs include `flush_dcache_folio()`, `flush_dcache_page()`, `copy_to_user_page()`, `__arm_ioremap_pfn()`, `__arm_ioremap_caller()`, `ioremap()`, `ioremap_cache()`, `ioremap_wc()`, optional `pci_remap_cfgspace()`, `arch_memremap_wb()`, and `iounmap()`.

## Control Flow
Early boot calls `arm_mm_memblock_reserve()`, which computes vector placement and reserves the vector region before normal allocations. `adjust_lowmem_bounds()` reads `MMFR0.PMSA`, dispatches to `pmsav7_adjust_lowmem_bounds()` or `pmsav8_adjust_lowmem_bounds()`, then aligns the memory allocator's current limit with the usable DRAM end. `paging_init()` installs the trap vectors at `vectors_base`, dispatches MPU programming through `pmsav7_setup()` or `pmsav8_setup()`, and initializes bootmem.

The I/O mapping path does not build page tables. `ioremap*()` delegates to `__arm_ioremap_caller()`, which returns the physical address cast as `__iomem`; `iounmap()` is intentionally empty.

## State and Persistence Behavior
The file mutates boot-time global state only: vector placement, `mpu_rgn_info`, memblock reservations, `high_memory`, and the memblock current limit. There is no persistent storage. Runtime cache functions affect processor cache state, and the remap functions expose stable identity mappings without allocation lifetime tracking.

## Dependencies and Integration Points
It depends on CP15 helpers, memblock, ARM trap setup, ARM MPU helpers from `pmsa-v7.c` and `pmsa-v8.c`, cacheflush hooks from selected `proc-*.S` files, and generic MM/bootmem setup. It integrates with drivers through exported cache flushing and `ioremap*()` APIs, with PCI through `pci_remap_cfgspace()`, and with exception handling through `early_trap_init()`.

## Risks
Vector placement is high risk: missing security extensions while requesting RAM-remapped vectors leaves vectors at zero, and address zero must stay reserved to avoid false successful allocations. Identity ioremap means callers do not get normal MMU permission isolation or unmap semantics. PMSA dispatch depends on correct CPUID feature decoding; unsupported PMSA values silently skip MPU setup. `copy_to_user_page()` only performs I-cache coherency for executable VMAs, so incorrect `VM_EXEC` flags can expose stale instruction fetches.

## Test Signals
Build and boot no-MMU ARM configurations for CP15, non-CP15, high-vector, RAM-remapped-vector, PMSAv7, PMSAv8, and V7-M variants. Check boot logs for vector remap errors and MPU selection messages. Runtime signals include successful exception entry, no allocation of address zero, working driver `ioremap()` access, executable user mapping coherency after writes, and PCI config-space access when `CONFIG_PCI` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/nommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pabort-legacy.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/pabort-legacy.S

## Purpose
This small assembly file implements the legacy ARM prefetch-abort adapter for CPUs that do not provide a useful instruction fault status register in the newer ARMv6/v7 form.

## Important APIs, Types, and Functions
The only exported entry is `legacy_pabort`. It receives the common abort-entry register convention: `r2` points at `pt_regs`, `r4` contains the aborted instruction address, and `r5` contains the parent context PSR. It passes `r0 = r4` and a fixed `r1 = 5` fault status to `do_PrefetchAbort`.

## Control Flow
The vector/abort glue enters `legacy_pabort`, which does no local decoding. It preserves the caller-required register set and tail-branches to the C abort handler. The fixed status value stands in for a legacy prefetch-abort reason.

## State and Persistence Behavior
There is no stored state. The handler only transfers register values to `do_PrefetchAbort`; lasting effects are whatever the generic abort path does, such as signal delivery, fault accounting, or kernel oops handling.

## Dependencies and Integration Points
The file depends on `linux/linkage.h` and `asm/assembler.h` for `ENTRY`/`ENDPROC`. It is wired into CPU processor-function tables by older `proc-*.S` files through `define_processor_functions ... pabort=legacy_pabort`.

## Risks
The fixed status code has less diagnostic precision than IFSR/IFAR-aware handlers. Incorrectly assigning this handler to a CPU that expects architected fault-status handling can degrade fault classification and debugging. Since it tail-branches into C with the abort ABI, any register convention drift would be severe.

## Test Signals
Build CPU configurations whose proc tables reference `legacy_pabort`, then run instruction-prefetch fault tests from user mode and kernel fault-injection paths. Useful signals are correct SIGSEGV/SIGBUS behavior, expected kernel oops reporting, and no register corruption across abort entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pabort-legacy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pabort-v6.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/pabort-v6.S

## Purpose
This file implements the ARMv6 prefetch-abort adapter. It reports the aborted instruction address from the exception glue and reads the architected instruction fault status register.

## Important APIs, Types, and Functions
The entry point is `v6_pabort`. It uses `mrc p15, 0, r1, c5, c0, 1` to read IFSR, leaves `r0` as the aborted instruction address from `r4`, and branches to `do_PrefetchAbort`.

## Control Flow
Abort entry code calls `v6_pabort`. The handler copies `r4` to `r0`, reads IFSR into `r1`, and tail-branches into the generic C prefetch-abort handler. It does not read IFAR, so the faulting address is still the instruction address supplied by the common abort frame.

## State and Persistence Behavior
No state is stored by this file. It consumes CP15 fault-state at abort time and transfers it to generic exception handling. Persistent effects are limited to the generic fault path.

## Dependencies and Integration Points
It is selected from `proc-v6.S` through the processor-function table as `pabort=v6_pabort`. It depends on CP15 availability and on the common ARM abort ABI used by `do_PrefetchAbort`.

## Risks
The risk is CPU mismatch. Using this handler on cores without the expected IFSR register semantics would provide an invalid status. Since IFAR is not read, fault-address precision depends on the exception entry path's instruction address.

## Test Signals
Build ARMv6 MMU configurations and exercise execute faults: user execute on unmapped pages, permission faults, and kernel prefetch faults. Confirm IFSR-derived codes are visible to the generic abort handler and that fault reporting matches ARMv6 expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pabort-v6.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pabort-v7.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/pabort-v7.S

## Purpose
This file implements the ARMv7 prefetch-abort adapter, using both IFAR and IFSR so the generic fault path gets the architected instruction-fault address and status.

## Important APIs, Types, and Functions
The single entry is `v7_pabort`. It reads IFAR with `mrc p15, 0, r0, c6, c0, 2`, reads IFSR with `mrc p15, 0, r1, c5, c0, 1`, and tail-branches to `do_PrefetchAbort`.

## Control Flow
The abort vector enters `v7_pabort`; the handler collects CP15 fault registers and immediately branches to the C handler. Unlike the legacy and ARMv6 handlers, `r0` is not the saved `r4` instruction address but the architected IFAR value.

## State and Persistence Behavior
No local state is kept. The handler consumes transient CP15 exception registers. Downstream persistent effects are managed by `do_PrefetchAbort`.

## Dependencies and Integration Points
This handler is referenced by ARMv7 processor-function tables, including `proc-v7.S` outside this work item. It integrates with the ARM exception path and generic memory-fault logic.

## Risks
Using the handler on CPUs with incompatible IFAR/IFSR behavior would misreport faults. Correct ordering matters because exception state must be read before any later handler path could disturb it. It also depends on the common abort ABI preserving the registers mentioned in the file comment.

## Test Signals
Build ARMv7 configurations and trigger instruction fetch faults across unmapped, no-execute, and permission-denied pages. Check that reported fault addresses come from IFAR and that status decoding routes to the expected signal or oops path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pabort-v7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pageattr.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/pageattr.c

## Purpose
This file implements ARM kernel mapping attribute changes for vmalloc/module ranges. It is the backend for `set_memory_ro/rw/x/nx/valid` style APIs on ARM MMU builds.

## Important APIs, Types, and Functions
`struct page_change_data` carries PTE set and clear masks. `change_page_range()` rewrites one PTE by clearing and setting Linux PTE bits, then calls `set_pte_ext()`. `__change_memory_common()` applies the callback over `init_mm` with `apply_to_page_range()` and flushes the kernel TLB range. `change_memory_common()` validates page alignment, computes the covered size, and restricts public attribute changes to `[MODULES_VADDR, MODULES_END)` or `[VMALLOC_START, VMALLOC_END)`.

Public APIs are `set_memory_ro()`, `set_memory_rw()`, `set_memory_nx()`, `set_memory_x()`, and `set_memory_valid()`.

## Control Flow
Public callers request an attribute transition for an address and page count. The common wrapper aligns and bounds-checks the range, then walks the page tables. Each PTE is translated through CPU-specific `set_pte_ext()` so the hardware PTE view is updated consistently. Finally, `flush_tlb_kernel_range()` invalidates stale translations.

## State and Persistence Behavior
The file mutates kernel page tables in `init_mm`. Changes persist until another mapping update reverses them or the mapping is torn down. No data is stored outside the page tables and TLB side effects.

## Dependencies and Integration Points
It depends on generic `apply_to_page_range()`, ARM PTE helpers, CPU-specific `set_pte_ext()` from `proc-*.S`, and TLB flushing. It is used by module loading, text patching, strict permissions, and any architecture-independent code calling the `set_memory_*()` APIs.

## Risks
Range validation is central: accidentally allowing linear-map or arbitrary kernel text changes would weaken memory protections. The code assumes the range is mapped by base pages; section or huge mappings are not handled here. Missing TLB flushes would leave old executable/writable permissions active. `set_memory_valid()` bypasses the module/vmalloc wrapper and directly changes validity, so callers must pass precise ranges.

## Test Signals
Build ARM MMU kernels with modules and strict permissions. Load and unload modules, verify module text becomes read-only and executable only when expected, and exercise ftrace/livepatch/BPF text patching if enabled. Negative tests should confirm linear-map addresses return `-EINVAL` for ro/rw/x/nx transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pageattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pgd.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/pgd.c

## Purpose
This file allocates and frees ARM per-mm top-level page tables. It copies kernel mappings into new address spaces, handles low-vector mappings when vectors are not high, and contains LPAE-specific allocation/free handling for module, pkmap, identity, and KASAN shadow tables.

## Important APIs, Types, and Functions
`pgd_alloc(struct mm_struct *mm)` allocates a zeroed PGD through `_pgd_alloc()`, copies kernel PGD entries above `USER_PTRS_PER_PGD`, cleans the PGD cache lines, allocates LPAE module/pkmap PMDs, copies KASAN shadow PMDs when enabled, and optionally allocates the low-vector PTE page. `pgd_free()` unwinds the low-vector page-table hierarchy, then for LPAE walks remaining PGD entries and frees non-swapper PMD/PUD/P4D tables.

## Control Flow
Allocation proceeds top down: PGD allocation, kernel mapping copy, LPAE module table allocation, optional KASAN copy, optional low-vector table allocation, and final low-vector PTE copy from `init_mm`. Error labels free the partially allocated hierarchy in reverse. Freeing validates and clears each level before returning page-table pages to the allocator.

## State and Persistence Behavior
The persistent state is the new `mm_struct` page-table root and page-table pages. Kernel mappings are copied into each new mm and remain shared by convention. The low-vector entries are duplicated into non-high-vector address spaces. Accounting counters such as `mm_dec_nr_pmds()` and `mm_dec_nr_ptes()` are updated during free paths.

## Dependencies and Integration Points
It depends on Linux page-table allocation helpers, ARM vector placement via `vectors_high()`, cache maintenance through `clean_dcache_area()`, and LPAE/KASAN configuration. It integrates with process creation, `mm` teardown, context switching through CPU `switch_mm` hooks, and exception vector mapping.

## Risks
Partial allocation cleanup is delicate; missing one level leaks page-table pages or corrupts mm accounting. Low-vector handling must preserve `DOMAIN_VECTORS` on non-LPAE systems or vectors can be unmapped for user processes. LPAE free logic must avoid freeing swapper-owned tables marked with `L_PGD_SWAPPER`. Cache cleaning is necessary before hardware page-table walks see copied entries.

## Test Signals
Run process fork/exec/exit stress on ARM classic and LPAE builds. Boot with high and low vectors, with and without KASAN. Enable page-table debugging and memory leak checks. Runtime signals include stable exception handling in user processes, no bad page-table warnings on exit, and no LPAE table leaks after process churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pgd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/physaddr.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/physaddr.c

## Purpose
This file provides checked virtual-to-physical conversion helpers for ARM. It validates linear-map and kernel-symbol address assumptions before using the low-level nodebug conversion macros.

## Important APIs, Types, and Functions
`__virt_addr_valid()` accepts early linear-map addresses before `high_memory` is initialized, normal linear-map addresses between `PAGE_OFFSET` and `high_memory`, and the special `MAX_DMA_ADDRESS` value. `__virt_to_phys()` warns when callers pass a non-linear virtual address, then calls `__virt_to_phys_nodebug()`. `__phys_addr_symbol()` validates that a symbol address lies between `KERNEL_START` and `KERNEL_END`, then calls `__pa_symbol_nodebug()`.

## Control Flow
Callers enter `__virt_to_phys()` or `__phys_addr_symbol()`. The functions perform debug checks and always return the nodebug conversion result unless `VIRTUAL_BUG_ON()` halts for a symbol-range violation.

## State and Persistence Behavior
No state is changed. The functions depend on global memory-layout state such as `high_memory` and compile-time/kernel-image section boundaries.

## Dependencies and Integration Points
It depends on ARM section symbols, page-layout macros, DMA address definitions, and MM debug infrastructure. It is exported for in-kernel and module users that need physical addresses for linear mappings or kernel symbols.

## Risks
The main risk is misuse: vmalloc, module, ioremap, stack, or other non-linear addresses passed to `virt_to_phys()` produce warnings and meaningless physical addresses. The `MAX_DMA_ADDRESS` exception is compatibility-oriented and does not prove a real mapping. Symbol conversion is intentionally stricter and can catch out-of-image uses.

## Test Signals
Enable MM debug warnings and exercise DMA and memory-management paths. Positive tests include linear-map page conversions and kernel text/data symbol conversions. Negative tests should pass vmalloc/module addresses under controlled conditions and verify warnings trigger without silent acceptance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/physaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pmsa-v7.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/pmsa-v7.c

## Purpose
This file programs ARM PMSAv7 MPU regions for no-MMU systems. It translates memblock RAM and optional XIP ROM into power-of-two MPU regions with subregion masks, truncating usable RAM when hardware region limits cannot cover the requested memory.

## Important APIs, Types, and Functions
`struct region` records base, size, and disabled subregions. `try_split_region()` finds the smallest aligned power-of-two MPU region that can cover a range and uses subregions when possible. `allocate_region()` decomposes a range into up to `MPU_MAX_REGIONS` regions. `pmsav7_adjust_lowmem_bounds()` probes min region order and max region count, reserves slots for background/vectors/XIP, converts the first contiguous memblock RAM range into MPU regions, and removes unsupported tail memory. `pmsav7_setup()` programs background, XIP, RAM, and vector regions.

Low-level helpers write CP15 MPU registers or Cortex-M SCB memory-mapped registers: region number, base, size, access-control, and optional instruction-side equivalents. `mpu_setup_region()` performs barriers, optional cache flush, register writes, and records values in `mpu_rgn_info`.

## Control Flow
Early memory-bound adjustment probes hardware limits, rejects non-contiguous first RAM, ignores later RAM banks, and computes a region plan. Later `pmsav7_setup()` programs regions in priority order: background strongly ordered no-execute, optional XIP ROM, RAM normal RW, and exception vectors. Any setup error panics.

## State and Persistence Behavior
The file uses `__initdata` arrays for planning and stores the final runtime MPU register image in global `mpu_rgn_info`, used by secondary/resume paths. It mutates memblock by removing unsupported memory. Hardware MPU state persists until reset or later MPU reprogramming.

## Dependencies and Integration Points
It is called from `nommu.c` based on `MMFR0.PMSA`. It depends on CP15/MPUIR, V7-M SCB definitions, memblock, cache flushing, `vectors_base`, XIP section symbols, and MPU constants from `asm/mpu.h`.

## Risks
MPU region sizing is constrained and easy to get wrong: base/size alignment, minimum region order, subregion granularity, and fixed slot reservations all affect usable memory. Removing later memblock ranges while iterating must remain broad and intentional. Incorrect region attributes can make RAM uncached, make vectors user-accessible, or permit execution from device/background regions.

## Test Signals
Boot PMSAv7 no-MMU boards with varied RAM sizes, non-power-of-two memory, XIP kernels, V7-M and non-V7-M targets, and separate I/D MPU maps. Confirm log messages for truncation and region independence, inspect `mpu_rgn_info`, and run memory, exception, DMA/cache, and executable-code tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pmsa-v7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pmsa-v8.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/pmsa-v8.c

## Purpose
This file programs ARM PMSAv8 MPU regions for no-MMU systems. It builds RAM and I/O ranges around early fixed kernel/XIP/vector regions and programs PRBAR/PRLAR pairs with normal or device memory attributes.

## Important APIs, Types, and Functions
Static `struct range` arrays `io[]` and `mem[]` hold planned regions. `is_region_fixed()` protects `PMSAv8_XIP_REGION` and `PMSAv8_KERNEL_REGION`. `pmsav8_adjust_lowmem_bounds()` keeps only the first RAM bank contiguous from `PHYS_OFFSET`. `__mpu_max_regions()` reads MPUIR once. `__pmsav8_setup_region()` writes `PRSEL`, `PRBAR`, and `PRLAR` and records values in `mpu_rgn_info`. `pmsav8_setup_ram()`, `pmsav8_setup_io()`, `pmsav8_setup_fixed()`, and `pmsav8_setup_vector()` build region attributes.

## Control Flow
Boot first adjusts memblock to one contiguous RAM bank. Setup then creates a RAM range from the first memblock memory region and an I/O range covering 4 GB. It subtracts kernel, optional XIP, vectors, and RAM from the relevant ranges. It verifies fixed early regions, then programs I/O ranges, RAM ranges, and vectors sequentially. Errors produce a warning rather than a panic.

## State and Persistence Behavior
The file stores planned ranges only in `__initdata`, records final MPU register pairs in `mpu_rgn_info`, and writes persistent hardware MPU state. It mutates memblock by discarding later RAM ranges.

## Dependencies and Integration Points
It is selected from `nommu.c` through `MMFR0.PMSA`. It depends on memblock, generic `range` add/subtract helpers, ARM CP15 or V7-M SCB register accessors, XIP/kernel section symbols, `vectors_base`, and PMSAv8 attribute constants.

## Risks
Region pressure is high because a full 4 GB I/O cover is split by exclusions. If the hardware supports too few regions, setup can fail and only warn, leaving mappings incomplete. Fixed-region verification assumes early assembly programmed kernel/XIP entries exactly. Attribute mistakes can expose executable device memory or non-cacheable RAM.

## Test Signals
Boot PMSAv8 no-MMU targets with and without XIP, with vectors enabled on non-V7-M systems, and with limited MPU region counts. Inspect log messages, `mpu_rgn_info`, and region register dumps. Exercise RAM access, device MMIO, vector faults, and secondary/resume paths that reuse recorded MPU state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pmsa-v8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1020.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1020.S

## Purpose
This assembly file supplies low-level MMU, cache, TLB, reset, idle, DMA, and PTE hooks for ARM1020T processors.

## Important APIs, Types, and Functions
It defines `cpu_arm1020_proc_init/fin/reset/do_idle/dcache_clean_area/switch_mm/set_pte_ext`, cache hooks such as `arm1020_flush_icache_all`, `arm1020_flush_user_cache_range`, coherency helpers, and DMA range helpers. It uses `armv3_set_pte_ext` from `proc-macros.S`, defines `arm1020_crval`, and publishes `arm1020_processor_functions` with `dabort=v4t_early_abort` and `pabort=legacy_pabort`. `__arm1020_proc_info` matches CPUID `0x4104a200` masked by `0xff0ffff0` and advertises ARMv5T capabilities.

## Control Flow
Boot CPU probing matches `__arm1020_proc_info`, calls `__arm1020_setup()` to invalidate caches/TLBs and compute SCTLR bits, then installs the processor function and cache/TLB/user tables. Runtime control flows through indirect function tables for cache flushes, DMA maintenance, `switch_mm()`, and PTE installation.

## State and Persistence Behavior
The file mutates CP15 control, cache, TLB, domain/translation base, and hardware PTE state. The processor-function table and proc-info records are static kernel metadata. There is no disk persistence.

## Dependencies and Integration Points
It depends on ARMv4/v5 CP15 operations, ARM page-table bit definitions, generic abort handlers, `proc-macros.S`, v4 WB cache/TLB helper tables, and the architecture CPU probe path.

## Risks
Cache geometry constants drive whole-cache loops and must match the core. PTE translation must maintain Linux/hardware PTE coherency. `switch_mm()` flushes caches/TLBs broadly, so missing barriers or D-cache cleans can cause stale page tables. Incorrect CPUID masks can bind the wrong low-level hooks.

## Test Signals
Build `CONFIG_CPU_ARM1020` kernels, boot on matching hardware or emulator, run fork/exec/mmap stress, module and DMA tests, instruction-cache coherency tests, and soft-reset/kexec paths. Check CPU name/capability strings and absence of data aborts during page-table churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1020.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1020e.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1020e.S

## Purpose
This file provides ARM1020E/ARM1020TE low-level processor hooks, extending the ARM1020-style implementation for ARMv5TE capability and control-register differences.

## Important APIs, Types, and Functions
It defines the `cpu_arm1020e_*` function family for init, finish, reset, idle, D-cache clean, MM switch, and PTE updates; `arm1020e_*` cache, coherency, and DMA helpers; `arm1020e_crval`; and `arm1020e_processor_functions`. The proc-info entry matches CPUID `0x4105a200`, uses ARMv5TE naming, and advertises `HWCAP_EDSP` in addition to SWP, HALF, and THUMB.

## Control Flow
CPU probe selects `__arm1020e_proc_info`, then `__arm1020e_setup()` invalidates caches/TLBs and computes desired SCTLR bits. The installed function table handles all later cache, TLB, page-table, and reset operations through indirect calls.

## State and Persistence Behavior
Runtime state is CP15 and cache/TLB/PTE state only. Static proc-info and function tables persist in kernel memory.

## Dependencies and Integration Points
The file integrates with the ARM CPU probe path, v4 write-back cache and TLB tables, `legacy_pabort`, `v4t_early_abort`, and the generic MM/page-table code via `set_pte_ext()` and `switch_mm()`.

## Risks
The ARM1020E control mask differs from ARM1020; copying values between files can leave stale SCTLR bits set. Cache-range code depends on 32-byte lines and 16 segments. DMA maintenance must match write-back/write-through configuration.

## Test Signals
Boot ARM1020E builds, confirm the CPU name and EDSP hwcap, stress context switches, page faults, DMA map/unmap operations, and executable mapping updates. Compare behavior under `CONFIG_CPU_DCACHE_WRITETHROUGH` and write-back builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1020e.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1022.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1022.S

## Purpose
This file supplies ARM1022E low-level MMU/cache/TLB operations, closely following the ARM1020E pattern with a distinct CPU ID and name.

## Important APIs, Types, and Functions
The public hooks are `cpu_arm1022_proc_init`, `cpu_arm1022_proc_fin`, `cpu_arm1022_reset`, `cpu_arm1022_do_idle`, `cpu_arm1022_dcache_clean_area`, `cpu_arm1022_switch_mm`, `cpu_arm1022_set_pte_ext`, and the `arm1022_*` cache/DMA/coherency helpers. `arm1022_crval` drives setup. `__arm1022_proc_info` matches `0x4105a220` and advertises ARMv5TE EDSP-capable features.

## Control Flow
After proc-info match, setup invalidates cache/TLB state and derives the SCTLR value. The runtime function table routes generic cacheflush, TLB, page-table, and reset requests to the ARM1022 implementations.

## State and Persistence Behavior
The file changes hardware CPU state: SCTLR, TTB, TLB entries, cache contents, and hardware PTE words. Its tables are static kernel metadata.

## Dependencies and Integration Points
It depends on `proc-macros.S`, v4/v5 CP15 maintenance operations, `legacy_pabort`, `v4t_early_abort`, and v4 write-back helper tables. It integrates with generic ARM MM through `processor_functions`.

## Risks
Its whole-cache and range-cache paths assume the same geometry constants as ARM1020E. Incorrect PTE cleanup or write-buffer drain can expose stale hardware entries. The CPUID mask must not overlap unrelated ARM10 variants.

## Test Signals
Boot on ARM1022E-capable hardware, verify CPU identification and hwcap output, run page-fault, context-switch, cache-coherency, DMA, and reset/kexec tests. Build with cache-disable and write-through options to cover conditional paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1022.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1026.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1026.S

## Purpose
This file implements low-level processor support for ARM1026EJ-S, including ARMv5TEJ/Jazelle capability reporting and CPU-specific cache maintenance.

## Important APIs, Types, and Functions
It defines `cpu_arm1026_*` hooks, `arm1026_*` cache/coherency/DMA helpers, `arm1026_crval`, and `arm1026_processor_functions`. The proc-info entry matches `0x4106a260`, uses `v5t_early_abort` and `legacy_pabort`, and advertises SWP, HALF, THUMB, FAST_MULT, EDSP, and JAVA.

## Control Flow
Setup invalidates caches and TLBs, loads the page-table pointer in MMU builds, optionally disables write-back behavior for write-through configurations, and computes SCTLR bits. Runtime calls use test-clean-invalidate loops for full D-cache operations and direct CP15 operations for TLB/PTE maintenance.

## State and Persistence Behavior
The file persists function/proc metadata in kernel memory and mutates CPU cache, TLB, write-buffer, translation-base, and control-register state during operation.

## Dependencies and Integration Points
It integrates with generic ARM MM, v4 write-back user/cache/TLB tables, abort handling, and `proc-macros.S`. It also depends on configuration options such as `CONFIG_CPU_DCACHE_WRITETHROUGH` and `CONFIG_CPU_CACHE_ROUND_ROBIN`.

## Risks
ARM1026 cache operations differ from the ARM1020 family, so using the wrong table can corrupt coherency. Jazelle/EDSP hwcap reporting must reflect hardware. Loading TTB during setup and context switch must be ordered with TLB/cache invalidation.

## Test Signals
Boot ARM1026EJ-S configurations, validate hwcaps, run process and mmap stress, DMA tests, executable page updates, and write-through/write-back variants. Confirm no stale I-cache after code generation or user-page writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1026.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm720.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm720.S

## Purpose
This file supports ARM710/ARM720T-class MMU processors with writethrough IDC cache behavior.

## Important APIs, Types, and Functions
It defines `cpu_arm720_dcache_clean_area`, `proc_init`, `proc_fin`, `do_idle`, `switch_mm`, `set_pte_ext`, and `reset`. It includes separate setup data for ARM710 and ARM720, `arm720_crval`, a proc-info macro, and `arm720_processor_functions` with `v4t_late_abort` and `legacy_pabort`.

## Control Flow
CPU probe selects one of the generated proc-info records, calls the appropriate setup routine to invalidate caches/TLBs and compute control-register bits, then installs the function table. `switch_mm()` invalidates cache, updates CP15 c2 with the new page table, and flushes TLBs.

## State and Persistence Behavior
The file mutates CP15 control, cache, TLB, and TTB state. It stores only static proc-info metadata.

## Dependencies and Integration Points
It depends on ARMv4T CP15 instructions, the generic processor-function table format, v4 cache/TLB helper tables, and ARM page-table macros. It integrates with legacy ARM MMU boot and context switching.

## Risks
The cache is assumed writethrough, so D-cache clean hooks are mostly no-op. If a variant behaves differently, DMA and page-table coherency can fail. ARM710 and ARM720 control bits are distinct and must remain tied to the right proc-info.

## Test Signals
Build ARM710/720 configs, boot legacy boards, run fork/exec and mmap tests, exercise TLB shootdown and context switching, and verify user/kernel cache flush APIs do not leave stale instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm720.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm740.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm740.S

## Purpose
This file provides no-MMU/MPU-oriented low-level support for ARM740T.

## Important APIs, Types, and Functions
The `cpu_arm740_*` hooks are mostly no-op except `proc_fin()` and `reset()`, which disable caches. `__arm740_setup()` programs protection areas for default 4 GB, RAM, and flash, cacheability/write-buffer registers, access permissions, and control bits. `define_processor_functions arm740` is marked `nommu=1`, so no `set_pte_ext` hook is installed. `__arm740_proc_info` matches `0x41807400`.

## Control Flow
The CPU probe invokes setup, which disables unused areas, computes area register values from `CONFIG_DRAM_BASE`, `CONFIG_DRAM_SIZE`, `CONFIG_FLASH_MEM_BASE`, and `CONFIG_FLASH_SIZE`, configures cache/write-buffer permissions, and returns the control value to early boot code.

## State and Persistence Behavior
The file persists MPU/protection area and cache-control state in CP15 registers. No page-table state exists for this CPU path.

## Dependencies and Integration Points
It depends on no-MMU ARM boot, `proc-macros.S` protection-region macros, compile-time DRAM/flash layout options, `legacy_pabort`, and `v4t_late_abort`.

## Risks
DRAM and flash sizes must be powers/encodings suitable for the protection area calculation. Wrong base/size options can leave RAM uncached or inaccessible. Marking it `nommu=1` means page-table callbacks are absent; generic MMU-only code must not reach this path.

## Test Signals
Boot ARM740T no-MMU configurations with realistic DRAM/flash settings. Verify memory access, flash execution, cache behavior, exceptions, and reset. Build-time tests should cover zero flash size and write-through/write-buffer variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm740.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm7tdmi.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm7tdmi.S

## Purpose
This file supports ARM7TDMI and several compatible no-MMU SoCs by providing minimal processor hooks and proc-info records.

## Important APIs, Types, and Functions
The `cpu_arm7tdmi_*` init, idle, dcache clean, switch-mm, finish, reset, and setup routines are no-ops or direct returns. `define_processor_functions arm7tdmi` is marked `nommu=1` with `v4t_late_abort` and `legacy_pabort`. The `arm7tdmi_proc_info` macro emits records for ARM7TDMI, Triscend-A7x, Atmel AT91M40xxx, Samsung S3C variants, and NETARM-style IDs, with optional THUMB hwcaps.

## Control Flow
CPU identification selects one proc-info record, but setup and runtime hooks intentionally do almost nothing because there is no MMU/cache maintenance surface in this file.

## State and Persistence Behavior
Only static proc-info and function-table metadata is stored. No CPU memory-management state is programmed.

## Dependencies and Integration Points
It integrates with ARM no-MMU boot, CPU probe, legacy abort handlers, and generic cache function tables (`v4_cache_fns`) where appropriate.

## Risks
The proc-info list spans vendor-specific IDs; mask mistakes can misidentify a CPU. Hwcaps such as THUMB differ by variant. Because hooks are no-op, selecting this path for a CPU with caches or protection hardware needing setup would break coherency or access control.

## Test Signals
Build no-MMU ARM7TDMI board configurations and verify CPU identification, userspace startup, exception handling, and reset. Confirm THUMB-capable variants advertise THUMB only when specified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm7tdmi.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm920.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm920.S

## Purpose
This file implements MMU, cache, DMA, context-switch, and suspend/resume hooks for ARM920T.

## Important APIs, Types, and Functions
It defines `cpu_arm920_*` hooks, `arm920_*` cache/coherency/DMA helpers, `cpu_arm920_do_suspend()`, `cpu_arm920_do_resume()`, `arm920_crval`, and `arm920_processor_functions` with suspend support. The proc-info entry matches `0x41009200`, advertises ARMv4T SWP/HALF/THUMB, and chooses `arm920_cache_fns` or `v4wt_cache_fns` depending on D-cache mode.

## Control Flow
Setup invalidates caches/TLBs and computes control bits. Cache operations either walk cache index geometry or use write-through helper paths. `switch_mm()` cleans/invalidates caches, loads CP15 c2, and invalidates TLBs. Suspend saves PID/domain/control registers; resume restores them and branches to `cpu_resume_mmu`.

## State and Persistence Behavior
The file mutates CPU control, cache, TLB, TTB, PID/domain, and PTE state. Suspend buffers supplied by callers persist a small CP15 register snapshot.

## Dependencies and Integration Points
It depends on v4 MMU/TLB/cache helper tables, generic CPU suspend, `legacy_pabort`, `v4t_early_abort`, and ARM page-table macros. It integrates with S3C24xx-style sleep support and generic ARM MM.

## Risks
Cache geometry constants and write-through conditionals must match hardware. Suspend/resume must restore CP15 state in the right order or resume with invalid mappings. Whole-cache flushes are broad and can hide performance regressions.

## Test Signals
Boot ARM920T boards, run suspend/resume, DMA, fork/exec, mmap, module, and executable-page coherency tests. Verify both write-back and write-through builds if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm920.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm922.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm922.S

## Purpose
This file provides ARM922T processor hooks, mirroring the ARM920T MMU/cache model with ARM922-specific cache geometry and CPU ID.

## Important APIs, Types, and Functions
It defines `cpu_arm922_*`, `arm922_*` cache/coherency/DMA functions, `arm922_crval`, and `arm922_processor_functions`. The proc-info entry matches `0x41009220`, uses `v4t_early_abort` and `legacy_pabort`, and publishes ARMv4T hwcaps.

## Control Flow
Setup invalidates caches/TLBs and returns the desired SCTLR value. Runtime cache and DMA calls operate through the installed cache function table; `switch_mm()` cleans/invalidates cache state, writes the new page-table base, and flushes TLBs.

## State and Persistence Behavior
Hardware state changed includes cache contents, write buffer, TLB, CP15 c1/c2, and hardware PTE cache lines. Static proc/function tables remain in kernel memory.

## Dependencies and Integration Points
The file integrates with ARM CPU probing, generic cacheflush and DMA APIs, v4 TLB/user helper tables, and `proc-macros.S`.

## Risks
The comments and constants must align with actual cache segment counts. A wrong D-cache limit or line size can skip required maintenance. Context switching depends on complete cache/TLB invalidation for correctness.

## Test Signals
Boot ARM922T builds, run process/context switch stress, DMA mapping tests, executable mapping changes, and cache flush API tests. Confirm proc-info identifies the CPU and uses the expected cache function table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm922.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm925.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm925.S

## Purpose
This file implements ARM925T/ARM915 low-level support, including OMAP/TI925-specific reset and cache-workaround behavior.

## Important APIs, Types, and Functions
It defines `cpu_arm925_*`, `arm925_*` cache/coherency/DMA hooks, `arm925_crval`, and `arm925_processor_functions`. Setup enables a TI configuration "transparent mode", invalidates caches/TLBs, optionally disables write-back, and computes control bits. The proc-info macro emits ARM925 and ARM915 entries and uses `v4t_early_abort` plus `legacy_pabort`.

## Control Flow
CPU probe calls `__arm925_setup()`. Runtime cache maintenance handles a 16-byte line, 2-segment, 256-entry D-cache and contains write-through/workaround conditionals. Reset first writes a platform-specific software reset halfword before falling through to generic cache/TLB disable operations. Idle temporarily disables I-cache around WFI.

## State and Persistence Behavior
The file mutates TI config registers, CP15 control, cache/TLB state, TTB, and hardware PTEs. Static proc-info records identify the core variants.

## Dependencies and Integration Points
It depends on OMAP/TI925 assumptions, ARMv4T helper tables, generic DMA/cache APIs, and ARM CPU suspend/idle conventions. It integrates through processor and cache function tables.

## Risks
The file documents known write-back flakiness with DMA, making `CONFIG_CPU_DCACHE_WRITETHROUGH` an important operational setting. Platform reset writes a hard-coded address. Transparent-mode and cache-clean mode assumptions are hardware-specific and risky to alter.

## Test Signals
Boot OMAP/ARM925/ARM915 systems, run DMA-heavy USB/storage tests, validate reset behavior, stress page-table updates, and compare write-through versus write-back builds. Check executable coherency after user-page writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm925.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm926.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm926.S

## Purpose
This file implements ARM926EJ-S MMU/cache/TLB, DMA, idle, and suspend/resume hooks.

## Important APIs, Types, and Functions
It defines `cpu_arm926_*`, `arm926_*` cache/coherency/DMA helpers, `cpu_arm926_do_suspend()`, `cpu_arm926_do_resume()`, `arm926_crval`, and `arm926_processor_functions`. The proc-info entry matches `0x41069260`, uses `v5tj_early_abort` and `legacy_pabort`, and advertises FAST_MULT, EDSP, and JAVA.

## Control Flow
Setup invalidates caches/TLBs, optionally disables write-back, and computes SCTLR bits. Idle drains the write buffer, disables I-cache with FIQs masked, waits for interrupt, then restores I-cache and FIQ state. `switch_mm()` performs full D/I cache maintenance, writes the page-table base, and invalidates TLBs. Suspend/resume saves and restores PID/domain/control state.

## State and Persistence Behavior
The file persists CPU metadata and mutates CP15 state, caches, TLBs, translation base, and hardware PTE cache lines. Suspend state is stored in caller-provided memory.

## Dependencies and Integration Points
It integrates with generic ARM MM, v4 write-back helper tables, suspend code, abort handlers, DMA/cache APIs, and `proc-macros.S`.

## Risks
Idle temporarily disables I-cache and masks FIQs; ordering is important. Cache maintenance differs for write-through and write-back builds. Incorrect JAVA/EDSP hwcaps or abort handler selection can mislead userland or fault handling.

## Test Signals
Boot ARM926EJ-S systems, run suspend/resume, WFI idle, DMA, mmap, fork/exec, and JIT/executable-page tests. Verify CPU capability output and no stale instruction fetches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm926.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm940.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm940.S

## Purpose
This file provides no-MMU MPU/cache support for ARM940T.

## Important APIs, Types, and Functions
It defines `cpu_arm940_*` hooks, `arm940_*` cache/coherency/DMA functions, and a `nommu=1` processor-function table using `nommu_early_abort` and `legacy_pabort`. `__arm940_setup()` programs separate data and instruction protection areas, RAM and flash regions, cacheability, write-buffer, access permissions, and control bits.

## Control Flow
After proc-info match, setup invalidates I/D caches, disables unused protection areas, establishes area 0 as a 4 GB default, area 1 as RAM, and area 2 as flash, then enables I-cache, D-cache, and the MPU. Runtime cache APIs perform whole-cache or range operations over ARM940 geometry.

## State and Persistence Behavior
The file mutates CP15 protection region, access permission, cacheability, write-buffer, and control registers. It stores static proc-info and cache function metadata.

## Dependencies and Integration Points
It depends on compile-time DRAM/flash layout, protection region macros, no-MMU CPU probe, cacheflush and DMA APIs, and legacy abort handling.

## Risks
The code contains hardware-specific region programming and must keep data and instruction side registers consistent. Incorrect DRAM/flash sizing can break all memory access. A suspicious flash-size path uses registers that must be reviewed carefully on changes. No page-table hooks exist.

## Test Signals
Boot ARM940T no-MMU builds, verify RAM and flash access, cache flush and DMA behavior, exceptions, and reset. Exercise write-through and write-back variants and inspect MPU/protection register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm940.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm946.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm946.S

## Purpose
This file supplies no-MMU MPU/cache support for ARM946E-S, including configurable D-cache sizing.

## Important APIs, Types, and Functions
It defines `cpu_arm946_*`, `arm946_*` cache/coherency/DMA helpers, and `arm946_processor_functions` with `nommu=1`. Cache geometry comes from `CONFIG_CPU_DCACHE_SIZE` with fixed 32-byte lines and 4 segments. `__arm946_setup()` programs RAM/flash protection regions, cacheability for data and instruction sides, access permissions, and control bits.

## Control Flow
Setup invalidates caches, disables unused memory regions, establishes default/RAM/flash regions, configures cacheable and write-buffer attributes, grants access permissions, and enables I-cache, D-cache, MPU, and optional round-robin cache replacement. Runtime range flushes either clean/invalidate each D-cache line or fall back to whole-cache maintenance.

## State and Persistence Behavior
The file changes CP15 protection-region and cache state and exposes static CPU metadata. No page tables are used.

## Dependencies and Integration Points
It depends on ARM946 CP15 MPU behavior, compile-time memory layout, cacheflush/DMA APIs, `proc-macros.S`, no-MMU boot, and legacy abort handlers.

## Risks
`CONFIG_CPU_DCACHE_SIZE` must match synthesized hardware. Region-size programming depends on valid DRAM/flash sizes. Cache and DMA correctness depends on line alignment and write-through conditionals. Since the processor table is no-MMU, generic MMU paths must stay unreachable.

## Test Signals
Boot ARM946E-S targets for multiple D-cache sizes, run memory and DMA tests, verify flash execution and access permissions, check cache coherency after code writes, and inspect configured protection regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm946.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm9tdmi.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm9tdmi.S

## Purpose
This file provides minimal no-MMU processor support for ARM9TDMI and P2001 cores.

## Important APIs, Types, and Functions
All `cpu_arm9tdmi_*` hooks are no-op returns except reset, which branches to the supplied reset address. `define_processor_functions arm9tdmi` is marked `nommu=1` with `nommu_early_abort` and `legacy_pabort`. The proc-info macro emits entries for ARM9TDMI and P2001, advertising SWP, THUMB, and 26-bit capability.

## Control Flow
CPU probe matches one of the proc-info records. Setup returns immediately, and runtime memory-management calls do not perform cache/TLB work because this path has no MMU surface.

## State and Persistence Behavior
No mutable CPU memory-management state is programmed. Static proc-info records persist in kernel memory.

## Dependencies and Integration Points
It integrates with no-MMU ARM boot, CPU probe, generic cache function selection (`v4_cache_fns`), and legacy abort handling.

## Risks
Selecting this no-op implementation for a CPU with real cache/protection requirements would break coherency. CPUID mask overlap and 26-bit capability reporting are the main metadata risks.

## Test Signals
Build ARM9TDMI/P2001 no-MMU configs, validate boot, exception handling, CPU identification, THUMB operation, and reset vector transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm9tdmi.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-fa526.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-fa526.S

## Purpose
This file implements low-level MMU/cache/TLB support for the Faraday FA526 core.

## Important APIs, Types, and Functions
It defines `cpu_fa526_proc_init/fin/reset/do_idle/dcache_clean_area/switch_mm/set_pte_ext`, `fa526_cr1_clear`, `fa526_cr1_set`, and `fa526_processor_functions`. The proc-info entry matches `0x66015261` masked by `0xff01fff1`, uses `v4_early_abort` and `legacy_pabort`, and advertises SWP and HALF.

## Control Flow
Setup invalidates caches/TLBs, reads CP15 control, applies clear/set masks, and returns to early boot. Runtime context switch and PTE paths use ARMv3-style PTE translation plus D-cache clean/write-buffer drain.

## State and Persistence Behavior
The file mutates CP15 control, cache, TLB, page-table base, and hardware PTE state. It stores static proc/function metadata.

## Dependencies and Integration Points
It depends on FA526 CP15 behavior, ARMv4-style page tables, `proc-macros.S`, abort handlers, and generic MM cache/TLB APIs.

## Risks
The reset path notes a TODO around CP8 and may not use all available reset mechanisms. FA526-specific control masks and cache behavior must not be mixed with ARM9/ARM10 files. Incorrect PTE clean ordering can cause stale translations.

## Test Signals
Boot FA526 hardware, run fork/exec/mmap, page-fault, DMA, and cache coherency tests. Verify CPU ID match and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-fa526.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-feroceon.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-feroceon.S

## Purpose
This file provides Marvell Feroceon low-level MMU/cache/TLB/DMA support, including optional Feroceon L2 cache maintenance and multiple CPU ID variants.

## Important APIs, Types, and Functions
It defines `cpu_feroceon_*` hooks, `feroceon_*` cache/coherency/DMA helpers, range-specific L2 helpers, suspend/resume hooks, `feroceon_crval`, and `feroceon_processor_functions`. The proc-info macro emits entries for old Feroceon IDs and 88FR531/88FR571/88FR131 variants, with ARMv5TE hwcaps.

## Control Flow
Setup invalidates caches/TLBs and computes SCTLR bits. Runtime cache/DMA operations maintain L1 and, when configured, Feroceon L2 lines. `switch_mm()` cleans relevant caches, writes TTB, and invalidates TLBs. Suspend/resume saves and restores CP15 state.

## State and Persistence Behavior
The file mutates L1/L2 cache state, CP15 control/TTB/TLB/PTE state, and stores suspend snapshots in caller memory. Processor metadata remains static.

## Dependencies and Integration Points
It depends on Marvell Feroceon cache extensions, optional `CONFIG_CACHE_FEROCEON_L2`, ARMv5TE helper tables, generic DMA/cache APIs, and legacy abort handling.

## Risks
L2 write-through/write-back configuration changes which operations are needed. Missing range L2 maintenance can corrupt DMA. Multiple CPUID entries increase match-order risk. Suspend/resume and switch-mm paths must keep L1, L2, TLB, and TTB ordering correct.

## Test Signals
Boot Feroceon variants with L2 enabled/disabled and write-through/write-back settings. Run network/storage DMA stress, page-table churn, suspend/resume, and executable coherency tests. Inspect CPU name and cache function selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-feroceon.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-macros.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-macros.S

## Purpose
This shared assembly include defines macros used by ARM processor support files. It centralizes access to common kernel structure offsets, ASID extraction, control-register value selection, cache-line-size decoding, Linux-to-hardware PTE translation, processor-function table construction, and MPU protection-region value generation.

## Important APIs, Types, and Functions
Key macros include `vma_vm_mm`, `vma_vm_flags`, `act_mm`, `mmid`, `asid`, `crval`, `dcache_line_size`, `icache_line_size`, `armv6_mt_table`, `armv6_set_pte_ext`, `armv3_set_pte_ext`, `xscale_set_pte_ext_prologue`, `xscale_set_pte_ext_epilogue`, `define_processor_functions`, `globl_equ`, `initfn`, `pr_sz`, and `pr_val`.

`define_processor_functions` emits the table consumed through `struct processor`, including data abort, prefetch abort, init, bugs, finish, reset, idle, D-cache clean, switch-mm, set-PTE, and optional suspend/resume entries.

## Control Flow
This file has no standalone execution. Including assembly files expand these macros into actual CPU-specific functions or tables. The PTE macros implement the branch-heavy Linux PTE to hardware descriptor translation used by several CPU files.

## State and Persistence Behavior
It creates no state directly, but macro expansion writes persistent `.proc.info.init`, `__INITDATA`, or `.rodata` function tables and generates instructions that mutate page tables and cache state.

## Dependencies and Integration Points
It depends on `asm-offsets.h`, page-table bit definitions, thread/task offsets, and V7-M constants when configured. Every proc file in this work item depends on it for table layout or PTE/control-register helpers.

## Risks
This is a high-blast-radius file. A bit-layout change can break many CPU families. The sanity checks around Linux PTE bits protect assumptions but only for compile-time constants. Table ordering in `define_processor_functions` must match C declarations in `<asm/proc-fns.h>`.

## Test Signals
Build a matrix of ARMv3/v4/v5/v6/v7, MMU/no-MMU, LPAE/non-LPAE, SMP/UP, and big-endian/little-endian configurations. Runtime tests should stress `set_pte_ext()`, context switching, cache flushes, suspend/resume table entries, and CPU probing for every proc file using these macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-macros.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-mohawk.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-mohawk.S

## Purpose
This file implements low-level support for Marvell PJ1/Mohawk 88SV331x cores, described as a hybrid of XScale3 and Marvell core behavior.

## Important APIs, Types, and Functions
It defines `cpu_mohawk_*` init/finish/reset/idle/dcache/switch-mm/set-PTE/suspend/resume hooks, `mohawk_*` cache/coherency/DMA helpers, `mohawk_crval`, and `mohawk_processor_functions`. `__88sv331x_proc_info` matches CPUID `0x56158000` masked by `0xfffff000` and advertises ARMv5TE features.

## Control Flow
Setup invalidates caches/TLBs, computes SCTLR bits, and returns to boot. Runtime cache and DMA paths use 32-byte cache-line loops. `switch_mm()` performs cache/TLB maintenance around TTB changes. Suspend/resume saves/restores CP15 state.

## State and Persistence Behavior
The file changes cache, TLB, TTB, control-register, and PTE state and stores static CPU metadata. Suspend snapshots persist in caller-provided memory.

## Dependencies and Integration Points
It depends on XScale-like PTE/cache behavior, ARMv5TE helper tables, abort handling, CPU suspend, and generic ARM cache/DMA APIs.

## Risks
Hybrid core behavior makes copying from either XScale or Feroceon risky. Control-register clear/set masks, PTE format, and cache maintenance must stay Mohawk-specific. CPUID matching is narrow and should not collide with other Marvell cores.

## Test Signals
Boot 88SV331x/PJ1 systems, run DMA and executable-coherency tests, stress process switching and PTE updates, and validate suspend/resume. Check CPU identification and hwcap output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-mohawk.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-sa110.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-sa110.S

## Purpose
This file provides low-level MMU/cache support for StrongARM SA-110.

## Important APIs, Types, and Functions
It defines `cpu_sa110_proc_init`, `proc_fin`, `reset`, `do_idle`, `dcache_clean_area`, `switch_mm`, `set_pte_ext`, `sa110_crval`, and `sa110_processor_functions`. The proc-info entry matches `0x4401a100`, uses `v4_early_abort` and `legacy_pabort`, and advertises SWP, HALF, 26BIT, and FAST_MULT.

## Control Flow
Setup invalidates cache/TLB state and computes control bits. Idle loads from an uncacheable address to enter low-power behavior. Context switch writes the TTB and flushes TLB/cache state. PTE installation uses ARMv3 translation and cache cleaning.

## State and Persistence Behavior
The file changes CP15 control, cache, TLB, TTB, and PTE state. Static CPU metadata remains in kernel sections.

## Dependencies and Integration Points
It depends on StrongARM CP15 behavior, an `UNCACHEABLE_ADDR` idle mechanism, ARMv4 page-table format, and generic ARM MM/cache APIs.

## Risks
SA-110 idle is hardware-specific and depends on an uncacheable access. 26-bit capability metadata is legacy-sensitive. Cache line size and control masks must match SA-110 exactly.

## Test Signals
Boot SA-110 platforms, verify idle wakeup, process switching, DMA/cache coherency, page faults, and reset. Confirm `/proc/cpuinfo` style capabilities match expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-sa110.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-sa1100.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-sa1100.S

## Purpose
This file implements StrongARM SA-1100/SA-1110 low-level MMU/cache and suspend/resume support.

## Important APIs, Types, and Functions
It defines `cpu_sa1100_*` init/finish/reset/idle/dcache/switch-mm/set-PTE/suspend/resume hooks, `sa1100_crval`, and `sa1100_processor_functions`. The proc-info macro emits SA1100 (`0x4401a110`) and SA1110 (`0x6901b110`) records with shared function calls and ARMv4 hwcaps.

## Control Flow
Setup invalidates caches/TLBs and computes control bits. Idle drains the write buffer and performs an uncacheable load. `switch_mm()` updates the page-table base and invalidates TLB/cache state. Suspend/resume saves and restores PID/domain/control registers and resumes via `cpu_resume_mmu`.

## State and Persistence Behavior
It mutates CP15 control, cache, TLB, TTB, and PTE state, plus caller-provided suspend buffers. Static proc-info metadata identifies SA1100 and SA1110.

## Dependencies and Integration Points
It depends on StrongARM memory-management behavior, generic CPU suspend, ARMv4 page tables, abort handling, and cacheflush/DMA APIs.

## Risks
SA1100 and SA1110 share hooks but differ by CPU ID/name. Idle and suspend/resume are order-sensitive. Incorrect control masks can leave caches or MMU state inconsistent across reset or resume.

## Test Signals
Boot SA1100 and SA1110 boards, run suspend/resume and idle tests, stress fork/exec/mmap and DMA, and verify CPU identification. Include reset/kexec paths if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-sa1100.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-syms.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-syms.c

## Purpose
This file exports selected ARM processor, cache, user-page, and TLB function symbols for loadable modules.

## Important APIs, Types, and Functions
Depending on `MULTI_CPU`, `MULTI_CACHE`, `MULTI_USER`, `MULTI_TLB`, and `CONFIG_MMU`, it exports either direct functions such as `cpu_dcache_clean_area`, `cpu_set_pte_ext`, `__cpuc_flush_kern_all`, `__cpuc_flush_user_all`, `__cpuc_flush_user_range`, `__cpuc_coherent_kern_range`, `__cpuc_flush_dcache_area`, `__cpu_clear_user_highpage`, and `__cpu_copy_user_highpage`, or dispatch tables such as `processor`, `cpu_cache`, `cpu_user`, and `cpu_tlb`.

## Control Flow
There is no runtime control flow beyond module symbol resolution. Compile-time conditionals select which symbols appear in the module export table.

## State and Persistence Behavior
The file does not mutate runtime state. It affects the persistent kernel module ABI for the built kernel image.

## Dependencies and Integration Points
It depends on ARM cacheflush, proc-fns, TLB flush, and user-page APIs. It integrates with module loading and with special users such as loadkernel/kexec support needing TLB vectors.

## Risks
Exporting too little breaks existing modules; exporting too much exposes low-level CPU internals. Conditional export choices must match whether the kernel uses single-CPU direct functions or multi-CPU dispatch tables. TLB exports are explicitly discouraged for ordinary modules.

## Test Signals
Build single and multi CPU/cache/user/TLB configurations with modules enabled. Run `modpost`, inspect exported symbols, and load modules that require cache flush or page-copy symbols. Confirm no unresolved symbols in representative ARM module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-syms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v6.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v6.S

## Purpose
This file provides ARMv6 generic low-level processor support: MMU context switching, PTE translation, cache maintenance, reset/idle, and suspend/resume.

## Important APIs, Types, and Functions
It defines `cpu_v6_proc_init/fin/reset/do_idle/dcache_clean_area/switch_mm/set_pte_ext/do_suspend/do_resume`, uses `armv6_mt_table` and `armv6_set_pte_ext`, defines `v6_crval`, and publishes `v6_processor_functions` with `v6_early_abort`, `v6_pabort`, and suspend support. `__v6_proc_info` matches ARMv6 by architecture bits and advertises SWP, HALF, THUMB, FAST_MULT, EDSP, JAVA, and TLS.

## Control Flow
Setup invalidates caches/TLBs, programs auxiliary control and TTB attributes, and returns control bits. `switch_mm()` extracts `mm->context.id`, applies SMP/UP TTB flags, flushes BTB, drains writes, writes TTBR0, and updates CONTEXTIDR. PTE writes generate both Linux and hardware PTE words. Suspend/resume saves and restores FCSE/PID, domain, TTBR1, auxiliary control, coprocessor access, and SCTLR state.

## State and Persistence Behavior
The file mutates CP15 control, auxiliary, TTB, context ID, domain, cache/TLB, and PTE state. It stores static CPU metadata and caller-provided suspend state.

## Dependencies and Integration Points
It depends on ARMv6 CP15 operations, SMP alternatives, PID-in-CONTEXTIDR options, `proc-macros.S`, `pabort-v6.S`, and generic CPU suspend/MM paths.

## Risks
ASID/context ID handling must preserve optional PID bits. SMP versus UP TTB flags affect page-table walk cacheability/shareability. PTE bit translation is security-critical for user/kernel, readonly, dirty, executable, and memory type semantics.

## Test Signals
Boot ARMv6 UP and SMP-like configurations, run context switch and ASID rollover stress, mmap permission tests, JIT/executable coherency tests, suspend/resume, and page-table debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v6.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-2level.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-2level.S

## Purpose
This file contains the ARMv7 non-LPAE, two-level page-table implementation pieces shared by the main ARMv7 processor support: context switching, PTE installation, memory attribute constants, TTB setup macro, and control-register values.

## Important APIs, Types, and Functions
It defines `cpu_v7_switch_mm()` for 32-bit TTBR0 updates and `cpu_v7_set_pte_ext()` for Linux-to-hardware small-page PTE conversion. It defines TTB flag constants for UP/SMP, PRRR/NMRR values for TEX remap attributes, `v7_ttb_setup`, and `v7_crval`.

## Control Flow
`switch_mm()` reads `mm->context.id`, applies page-table walk cacheability/shareability flags, optionally preserves PID bits in CONTEXTIDR, applies erratum barriers, writes CONTEXTIDR, then writes TTBR0. `set_pte_ext()` stores the Linux PTE, constructs a hardware PTE with permissions, TEX, XN, valid/young/none checks, stores the hardware copy at the expected offset, and cleans the PTE cache line on UP.

## State and Persistence Behavior
The file mutates TTBR0, CONTEXTIDR, hardware PTE words, and possibly PTE cache state. Constants and macros are assembled into the ARMv7 proc setup path.

## Dependencies and Integration Points
It is included/paired with `proc-v7.S` for non-LPAE builds. It depends on ARMv7 CP15, SMP alternatives, ARM errata options, page-table bit definitions, and `proc-macros.S` helpers.

## Risks
PTE bit translation controls executable, user, readonly, dirty, and valid semantics. TTB flags affect page-table walk coherency on SMP. CONTEXTIDR/PID insertion must preserve ASID bits. LPAE builds must use `proc-v7-3level.S` instead.

## Test Signals
Build ARMv7 non-LPAE UP and SMP kernels, run ASID/context-switch stress, permission and NX tests, module/vmalloc `set_memory_*()` tests, and page-table debug checks. Exercise configurations with `CONFIG_PID_IN_CONTEXTIDR` and erratum 754322.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-2level.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-3level.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-3level.S

## Purpose
This file provides the ARMv7 LPAE, three-level page-table implementation pieces: 64-bit TTBR updates, 64-bit PTE installation, MAIR constants, TTBCR/TTBR1 setup macro, and control-register values.

## Important APIs, Types, and Functions
It defines `cpu_v7_switch_mm()` for LPAE TTBR0 writes via `mcrr`, `cpu_v7_set_pte_ext()` for 64-bit L3 PTE updates, endian-dependent register aliases, MAIR-equivalent `PRRR`/`NMRR` constants, `v7_ttb_setup`, and `v7_crval`.

## Control Flow
`switch_mm()` extracts the ASID from `mm->context.id`, folds it into the high TTBR bits, writes TTBR0 as a 64-bit register pair, and issues an ISB. `set_pte_ext()` validates the low PTE word, clears valid for `L_PTE_NONE`, adjusts AP2 based on dirty/readonly state, stores the 64-bit PTE with `strd`, and cleans the PTE line on UP. `v7_ttb_setup` programs TTBCR with EAE and optionally split TTBR sizing, then writes TTBR1.

## State and Persistence Behavior
It mutates TTBR0/TTBR1, TTBCR, LPAE PTE memory, and PTE cache state. Static constants are consumed by ARMv7 setup.

## Dependencies and Integration Points
It integrates with ARMv7 LPAE builds, page-table definitions from `pgtable-3level.h`, SMP alternatives, endian configuration, and the main `proc-v7.S` setup path.

## Risks
Endian register pairing is critical for `mcrr` and `strd`. TTBR split logic depends on the relationship between `PHYS_OFFSET` and `PAGE_OFFSET`; wrong split setup can break secondary CPU identity mappings. 64-bit PTE permission updates must preserve all high attribute bits.

## Test Signals
Build ARMv7 LPAE kernels in UP/SMP and little/big endian where supported. Run high-memory, process, ASID, permission/NX, huge vmalloc/module, and secondary CPU boot tests. Inspect TTBR/TTBCR values when debugging early boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-3level.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-bugs.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-bugs.c

## Purpose
This file initializes ARMv7 CPU vulnerability mitigations for Spectre v2 and Spectre BHB, choosing branch predictor hardening, firmware calls, vector updates, and CPU-specific auxiliary-control checks.

## Important APIs, Types, and Functions
`spectre_v2_get_cpu_fw_mitigation_state()` queries SMCCC `ARCH_WORKAROUND_1` when PSCI is available. Under `CONFIG_HARDEN_BRANCH_PREDICTOR`, `harden_branch_predictor_fn` stores a per-CPU mitigation function and `spectre_v2_install_workaround()` selects BPIALL, ICIALLU, HVC, or SMC methods, also replacing `cpu_do_switch_mm` for firmware conduits. `cpu_v7_spectre_v2_init()` maps CPU parts to mitigation methods and updates global Spectre state.

For BHB, `spectre_bhb_method`, `spectre_bhb_install_workaround()`, and `cpu_v7_spectre_bhb_init()` select loop, BPIALL, ICIALLU, or firmware-style methods and update vectors through `spectre_bhb_update_vectors()`. Public entry points are `cpu_v7_ca8_ibe()`, `cpu_v7_ca15_ibe()`, and `cpu_v7_bugs_init()`.

## Control Flow
ARMv7 proc-info tables call a bugs-init hook during CPU bring-up. The hook reads CPUID implementor/part, decides whether the CPU is unaffected, locally mitigated, or firmware-dependent, installs per-CPU or global hooks, checks required AUXCR IBE bits for Cortex-A8/A15 paths, updates Spectre state, and logs selected methods.

## State and Persistence Behavior
The file mutates per-CPU `harden_branch_predictor_fn`, global `cpu_do_switch_mm`, BHB vector state, `spectre_bhb_method`, per-CPU warning state, and global Spectre reporting state. These choices persist for the running kernel.

## Dependencies and Integration Points
It depends on SMCCC/PSCI, CP15 system-register helpers, CPU part IDs, SMP per-CPU state, `asm/spectre.h`, `asm/proc-fns.h`, and ARMv7 switch-mm hardening stubs from `proc-v7.S`. It integrates with CPU bring-up, context switching, exception vectors, and sysfs/proc vulnerability reporting.

## Risks
Mitigation selection is security-sensitive. Firmware conduit detection must be correct for Cortex-A57/A72. Mixed CPUs can disagree on BHB method; the code marks the system vulnerable on disagreement. If branch predictor hardening is disabled, affected systems remain vulnerable by configuration. AUXCR checks rely on firmware setting IBE bits.

## Test Signals
Build with and without `CONFIG_ARM_PSCI`, `CONFIG_HARDEN_BRANCH_PREDICTOR`, and `CONFIG_HARDEN_BRANCH_HISTORY`. Boot affected Cortex-A8/A9/A15/A57/A72/A73/A75 and Broadcom Brahma variants where available. Check vulnerability reporting, boot logs for selected methods, SMCCC return handling, CPU hotplug behavior, and that context-switch hardening stubs are used for firmware methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-bugs.c -->
