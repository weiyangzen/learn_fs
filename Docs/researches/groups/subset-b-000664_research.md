# subset-b-000664 Research

Grouped research report for ARM MM processor/TLB support, ARM eBPF JIT, and ARM NWFPE files. Each section is source-tree aligned and delimited for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7.S

## Purpose
Provides the ARMv7-A/R processor backend used by the 32-bit ARM kernel MM layer. It defines low-level processor operations for init/finalize, reset, idle, D-cache cleaning, context switch, PTE writes through included 2-level or LPAE helpers, suspend/resume, CPU errata setup, and `proc_info_list` records for Cortex, Krait, Brahma, and PJ4B cores.

## Important APIs, Types, And Functions
Exports `cpu_v7_proc_init`, `cpu_v7_proc_fin`, `cpu_v7_reset`, `cpu_v7_do_idle`, `cpu_v7_dcache_clean_area`, branch predictor hardening switch variants, `cpu_v7_do_suspend`, `cpu_v7_do_resume`, Cortex-A9/PJ4B-specific suspend hooks, and setup labels such as `__v7_setup`, `__v7_ca9mp_setup`, and `__v7_pj4b_setup`. `define_processor_functions` emits the `struct processor` tables consumed by ARM proc selection.

## Control Flow
Early boot matches MIDR against `.proc.info.init` entries, jumps through the selected `initfn`, invalidates L1 caches, applies errata by CPU part/revision, programs TTBCR/TTBRs, PRRR/NMRR, ThumbEE state, and returns the SCTLR value to `head.S`. Runtime calls enter the function table for idle, reset, `switch_mm`, PTE updates, and suspend/resume. Hardened branch predictor variants wrap `switch_mm` with SMC/HVC, ICIALLU, or BPIALL sequences depending on configuration and CPU family.

## State, Dependencies, And Integration
Persistent state is architectural CP15 state: SCTLR, ACTLR, TTB registers, domain register, PRRR/NMRR, CPACR, context/thread IDs, and CPU-specific diagnostic registers. It depends on `proc-macros.S`, `proc-v7-2level.S` or `proc-v7-3level.S`, alternative patching macros, `asm/pgtable-hwdef.h`, SMCCC constants, and suspend code in the ARM core. Integration points are `proc_info_list`, `v7wbi_tlb_fns`, `v6_user_fns`, cache function tables, CPU suspend, PSCI, and branch predictor hardening.

## Risks And Test Signals
Risks are wrong errata gating, missing barriers around TLB/cache invalidation, incorrect LPAE vs non-LPAE TTBR setup, suspend state size mismatches, and hardening variant mismatch for vulnerable CPUs. Test signals include boot on each matched CPU class, SMP/UP alternative patching, context switch stress, suspend/resume, page-table permission tests, KPTI/speculation-hardening coverage, and kernel selftests that exercise mapping changes and signal delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7m.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7m.S

## Purpose
Implements the ARMv7-M and Cortex-M processor backend for no-MMU ARM systems. It supplies minimal processor functions, vector table setup, fault enablement, SVC-based transition setup, optional Cortex-M7/M55 cache handling, and proc-info records for Cortex-M3/M4/M7/M33/M55 plus a generic ARMv7-M match.

## Important APIs, Types, And Functions
Exports `cpu_v7m_proc_init`, `cpu_v7m_proc_fin`, `cpu_v7m_reset`, `cpu_v7m_do_idle`, `cpu_v7m_dcache_clean_area`, `cpu_v7m_switch_mm`, optional suspend/resume stubs, and Cortex-M7 variants `cpu_cm7_dcache_clean_area` and `cpu_cm7_proc_fin`. Setup flows are `__v7m_setup` and `__v7m_cm7_setup`, with `define_processor_functions v7m` and `cm7`.

## Control Flow
Early setup programs SCB VTOR to `vector_table`, enables UsageFault/BusFault/MemManage, lowers SVC and PendSV priorities, temporarily patches the SVC vector, invokes SVC to enter handler mode, restores the vector, sets `control`, optionally invalidates L1 cache for cache-equipped cores, and returns the CCR bits to apply. There is no MMU context switch; `switch_mm` is a return.

## State, Dependencies, And Integration
State is mostly SCB memory-mapped control registers rather than CP15 MMU state: VTOR, SHCSR, SHPR2/3, CCR, and DCCMVAC. It depends on `asm/v7m.h`, `proc-macros.S`, no-MMU abort handlers, `vector_table`, `init_thread_union`, and cache helper `v7m_invalidate_l1`. It integrates through `.proc.info.init` and no-MMU processor functions.

## Risks And Test Signals
Risks include incorrect exception vector patching, stack assumptions during SVC, cache clean ordering on Cortex-M7/M55, and accidentally treating v7-M as MMU capable. Test signals are boot on supported Cortex-M variants, exception entry/return sanity, cache maintenance tests on M7/M55, no-MMU process switching, and WFI idle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7m.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-xsc3.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-xsc3.S

## Purpose
Provides MMU, cache, DMA, PTE, suspend/resume, and proc-info support for Intel/Marvell XScale3 cores. XSC3 extends original XScale with ARMv6 supersections, LLR pages, 36-bit addressing, L2 cache, and optional coherency.

## Important APIs, Types, And Functions
Exports `cpu_xsc3_proc_init`, `cpu_xsc3_proc_fin`, `cpu_xsc3_reset`, `cpu_xsc3_do_idle`, cache routines such as `xsc3_flush_icache_all`, `xsc3_flush_kern_cache_all`, `xsc3_flush_user_cache_range`, coherent range functions, DMA map/unmap functions, `cpu_xsc3_dcache_clean_area`, `cpu_xsc3_switch_mm`, `cpu_xsc3_set_pte_ext`, suspend/resume hooks, and `__xsc3_setup`.

## Control Flow
Setup disables interrupts, invalidates caches/BTB/TLBs, programs TTBR with L2 page-table caching bits, enables CP6 access, configures auxiliary control for LLR/L2, optionally enables L2, and returns an SCTLR value. Runtime cache and DMA functions either loop over cache lines or fall back to whole-cache cleaning above `MAX_AREA_SIZE`. `switch_mm` cleans D-cache, invalidates I-cache/BTB, loads TTBR, invalidates TLBs, and waits for CP15 completion. PTE writes map Linux memory types through `cpu_xsc3_mt_table`.

## State, Dependencies, And Integration
State includes CP15 cache/TLB/control registers, CP14 idle/clock registers, domain and PID registers, L2 configuration, and PTE attributes. It depends on XScale PTE prologue/epilogue macros in `proc-macros.S`, `v4wbi_tlb_fns`, `xsc3_mc_user_fns`, `xsc3_cache_fns`, DMA direction constants, and ARM suspend code.

## Risks And Test Signals
Main risks are cache coherency regressions, L2/LLR attribute mistakes, DMA line-alignment data loss, TTBR caching bit errors, and suspend restore ordering. Test with XSC3/PXA935 boot, DMA streaming tests, user executable mapping coherency, `switch_mm` stress, L2 enabled/disabled configurations, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-xsc3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-xscale.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc-xscale.S

## Purpose
Implements the original Intel XScale processor backend, covering cache maintenance, DMA cache synchronization, page-table switching, PTE attribute construction, suspend/resume, setup, and CPU identification records for 80200, IOP, IXP, and PXA families.

## Important APIs, Types, And Functions
Exports `cpu_xscale_proc_init`, `cpu_xscale_proc_fin`, `cpu_xscale_reset`, `cpu_xscale_do_idle`, `xscale_flush_*`, `xscale_coherent_*`, `xscale_dma_map_area`, `xscale_80200_A0_A1_dma_map_area`, `xscale_dma_unmap_area`, `cpu_xscale_dcache_clean_area`, `cpu_xscale_switch_mm`, `cpu_xscale_set_pte_ext`, suspend/resume hooks, and `__xscale_setup`.

## Control Flow
Initialization re-enables write buffer coalescing and setup invalidates caches/TLBs, grants CP6/CP13 access, and computes SCTLR bits from `xscale_crval`. Whole-cache cleaning uses the alternating `clean_addr` line-allocation workaround. Range operations loop over 32-byte lines and drain write buffers. DMA map chooses clean, invalidate, or flush based on DMA direction, with an 80200 A0/A1 erratum path that flushes instead of invalidating. PTE writes translate Linux memory types through `cpu_xscale_mt_table` and apply erratum 40 by forcing user read-only writeback pages to writethrough.

## State, Dependencies, And Integration
State includes CP15 cache/TLB/SCTLR/ACTLR/domain/TTBR/PID registers, CP14 clock/idle state, and the `clean_addr` data word used to alternate cleaning ranges. Integrates with `v4wbi_tlb_fns`, `xscale_mc_user_fns`, `xscale_cache_fns`, and the CPU proc-info matching table.

## Risks And Test Signals
Risks include subtle dirty-line loss, erratum handling regressions, incorrect endian or PTE memory type encoding, and reset code alignment hazards after MMU disable. Test signals include boot across XScale variants, DMA tests on unaligned buffers, executable mapping coherency, user read-only mapping behavior, suspend/resume, and large cache flush paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc-xscale.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/proc.c

## Purpose
Declares C prototypes and emits `__ADDRESSABLE()` references for low-level ARM processor assembly routines that are called from C but do not have native C definitions. This supports CFI and prevents referenced assembly entry points from being discarded or considered type-missing.

## Important APIs, Types, And Functions
Contains configuration-gated declarations for `cpu_*_proc_init`, `proc_fin`, `reset`, `do_idle`, `dcache_clean_area`, `switch_mm`, `set_pte_ext`, and suspend/resume functions across ARM7/9/10, SA110, XScale, XSC3, Mohawk, Feroceon, v6, v7, and v7-M. It uses `__ADDRESSABLE(symbol)` for each function.

## Control Flow
There is no runtime control flow beyond static references. The preprocessor selects declarations matching enabled CPU families. The function order mirrors `struct processor`, helping CFI see the same callable signatures that the assembly function table exposes.

## State, Dependencies, And Integration
No persistent state is owned. Dependencies are `asm/proc-fns.h`, CPU Kconfig symbols, `phys_addr_t`, `struct mm_struct`, and `pte_t`. Integration is with low-level assembly files under `arch/arm/mm`, CFI, linker reachability, and indirect calls through processor tables.

## Risks And Test Signals
Risks are signature drift between C declarations, `struct processor`, and assembly implementations, especially LPAE `set_pte_ext` arity or reset argument shape. Test signals are CFI-enabled builds for each CPU family, allmodconfig/allyesconfig compile coverage, and boot-time indirect calls through selected processor functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/ptdump_debugfs.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/ptdump_debugfs.c

## Purpose
Exposes ARM page-table dump data through debugfs. It creates read-only debugfs files backed by the generic ptdump walker.

## Important APIs, Types, And Functions
Defines `ptdump_show(struct seq_file *m, void *v)` and `ptdump_debugfs_register(struct ptdump_info *info, const char *name)`. `DEFINE_SHOW_ATTRIBUTE(ptdump)` creates file operations used by debugfs.

## Control Flow
Opening the debugfs file calls the seq-file show routine. `ptdump_show` retrieves `struct ptdump_info` from `m->private` and calls `ptdump_walk_pgd(m, info)`. Registration calls `debugfs_create_file(name, 0400, NULL, info, &ptdump_fops)`.

## State, Dependencies, And Integration
State is external: the passed `ptdump_info` object and the page tables it references. Dependencies are `linux/debugfs.h`, `linux/seq_file.h`, and `asm/ptdump.h`. Integration is with debugfs initialization code that registers kernel or user page-table dump views.

## Risks And Test Signals
Risks include exposing sensitive mapping details to readers with debugfs access, stale `ptdump_info` lifetime, and ptdump walker regressions. Test signals are debugfs mount/read tests, expected permissions, and comparing output against known kernel mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/ptdump_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pv-fixup-asm.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/pv-fixup-asm.S

## Purpose
Safely remaps LPAE page tables by applying a physical-address delta to kernel, boot-data, level-1 table entries, and TTBRs. It is used for Keystone 2 physical address space remapping while running from identity-mapped code.

## Important APIs, Types, And Functions
Exports `lpae_pgtables_remap_asm`. Inputs are a 64-bit delta in `r1:r0` and page-table base in `r2`. It uses constants such as `_end`, `FDT_FIXED_BASE`, `KERNEL_OFFSET`, `SECTION_SHIFT`, `CR_M`, and LPAE table entry widths.

## Control Flow
The function saves registers, disables MMU/caches by clearing `CR_M`, updates L2 entries covering the kernel, updates two boot-data entries, updates four L1 entries, adjusts TTBR0 and TTBR1 by the same delta, flushes I-cache/BTB and TLBs, then restores the saved SCTLR to re-enable the MMU.

## State, Dependencies, And Integration
Persistent state changed is page-table physical addresses and CP15 TTBR/SCTLR state. Dependencies include LPAE page-table layout, identity mapping, `asm/cp15.h`, `asm/page.h`, and linker symbols. It integrates with platform physical-address virtualization/fixup code before normal virtual mappings are trusted.

## Risks And Test Signals
Risks are off-by-one L2 coverage, wrong 64-bit carry propagation, disabling MMU outside identity mapping, missing barriers, or stale TLBs. Test signals include Keystone 2 boot, high physical address boot, FDT fixed mapping access, and early page-table dump verification after fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/pv-fixup-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-fa.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-fa.S

## Purpose
Implements Faraday FA520/FA526/FA626 range TLB invalidation for unified TLBs with write buffer and BTB behavior.

## Important APIs, Types, And Functions
Exports `fa_flush_user_tlb_range(start, end, vma)` and `fa_flush_kern_tlb_range(start, end)`. Uses `vma_vm_mm`, `act_mm`, `PAGE_SZ`, CP15 write-buffer drain, and unified TLB invalidate-by-MVA operations.

## Control Flow
User flush first compares the VMA's mm with `current->active_mm`; if it is not active, it returns without flushing. Active ranges drain the write buffer, align the start address to a page boundary, loop by page invalidating UTLB entries, then drain again. Kernel range follows the same loop and also performs a prefetch flush.

## State, Dependencies, And Integration
State is CPU TLB and write buffer state only. Dependencies are `asm/tlbflush.h`, `proc-macros.S`, VM flag/mm access macros, and Faraday proc-info entries that select `fa_tlb_fns` from `tlb.c`.

## Risks And Test Signals
Risks are active-mm comparison mistakes, address alignment errors, missing BTB/prefetch ordering for executable kernel mappings, and stale entries on context switches. Test with mmap/munmap/mprotect stress, kernel module text mapping changes, and Faraday-specific boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-fa.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4.S

## Purpose
Provides ARMv4 write-through/no-write-buffer range TLB invalidation for processors such as ARM720T with split I/D TLBs and no write buffer.

## Important APIs, Types, And Functions
Exports `v4_flush_user_tlb_range` and `v4_flush_kern_tlb_range`. The kernel function is either a CFI-safe branch wrapper or a global equate to the shared internal label.

## Control Flow
User flush compares the target VMA mm to `current->active_mm`; inactive address spaces are skipped. The shared range loop aligns the start address and invalidates TLB entries page by page through CP15 c8 unified-entry invalidation, then returns. No explicit write-buffer drain is needed for this CPU class.

## State, Dependencies, And Integration
State is split TLB contents. Dependencies include `asm/tlbflush.h`, `proc-macros.S`, and CFI macros. Integration occurs through `v4_tlb_fns` in `tlb.c`, which pairs these callbacks with `v4_tlb_flags`.

## Risks And Test Signals
Risks include CFI symbol exposure issues, assuming unified invalidation behavior on unsupported hardware, and missing flushes for inactive but soon-to-run address spaces if context switch behavior changes. Test signals are ARM720T builds, CFI builds, and VM range invalidation stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4wb.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4wb.S

## Purpose
Implements ARMv4 range TLB invalidation for SA110/SA1100/SA1110-style CPUs with split I/D TLBs, no I-TLB entry invalidation by MVA, and a write buffer.

## Important APIs, Types, And Functions
Exports `v4wb_flush_user_tlb_range` and `v4wb_flush_kern_tlb_range`. Uses VM executable flags to decide when to invalidate the whole I-TLB and always invalidates D-TLB entries by page.

## Control Flow
User flush skips inactive mms, drains the write buffer, checks `VM_EXEC`, invalidates the full I-TLB for executable mappings, then loops over aligned pages invalidating D-TLB entries. Kernel flush drains, aligns, invalidates the full I-TLB unconditionally, and loops over D-TLB entries.

## State, Dependencies, And Integration
State is write buffer plus split I/D TLB content. Dependencies are `asm/tlbflush.h`, VM flag helpers, and processor table selection through `v4wb_tlb_fns`.

## Risks And Test Signals
Risks are stale executable translations if `VM_EXEC` detection is wrong, excessive full I-TLB invalidation cost, and missing write-buffer drains before invalidation. Test signals include SA110-class boot, executable mmap permission transitions, fork/exec stress, and kernel text mapping changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4wb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4wbi.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4wbi.S

## Purpose
Implements ARMv4/v5 write-buffered split I/D TLB invalidation with per-entry invalidation for both instruction and data TLBs. Used by ARM920/922/925/926 and XScale-class processors.

## Important APIs, Types, And Functions
Exports `v4wbi_flush_user_tlb_range` and `v4wbi_flush_kern_tlb_range`. Uses CP15 c8 I-TLB and D-TLB invalidate-by-MVA operations and a write-buffer drain.

## Control Flow
User flush verifies the VMA mm is active, drains the write buffer, reads `vm_flags`, aligns start, and loops over pages. For executable VMAs it invalidates the I-TLB entry; it always invalidates the D-TLB entry. Kernel flush drains and invalidates both I and D entries for every page in the range.

## State, Dependencies, And Integration
State changed is local CPU TLB and write buffer state. Dependencies are `proc-macros.S`, VM helpers, and `v4wbi_tlb_flags`. Integration is through `v4wbi_tlb_fns`, also used for some Feroceon configurations.

## Risks And Test Signals
Risks are stale instruction translations, missed inactive-mm handling assumptions, and excessive cost for large ranges. Test signals include ARM9/XScale boot, memory protection changes, executable page remapping, and context switch TLB behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4wbi.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v6.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v6.S

## Purpose
Provides ARMv6 range TLB invalidation for Harvard-style split I/D TLBs, including ASID-aware user invalidation and kernel-range invalidation.

## Important APIs, Types, And Functions
Exports `v6wbi_flush_user_tlb_range` and `v6wbi_flush_kern_tlb_range`. Uses `mmid`, `asid`, `vma_vm_flags`, CP15 write-buffer drains, and CP15 c8 MVA invalidation operations.

## Control Flow
User flush extracts `vma->vm_mm->context.id`, drains the write buffer, aligns start/end to pages, combines ASID with MVA, reads VM flags, then loops invalidating D-TLB entries and I-TLB entries for executable mappings. Kernel flush aligns addresses, loops invalidating both D and I TLBs, drains, and prefetch flushes.

## State, Dependencies, And Integration
State is local TLB and write-buffer contents. Dependencies include ARMv6 architecture mode, ASID layout, `asm/tlbflush.h`, and `v6wbi_tlb_flags`. Integration is through `v6wbi_tlb_fns` in `tlb.c`.

## Risks And Test Signals
Risks include ASID composition mistakes, executable flag handling bugs, missing final synchronization, and unsupported assumptions if non-Harvard builds are introduced. Test signals are ARMv6 boot, ASID wrap tests, mmap/mprotect stress, and executable page coherence tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v6.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v7.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v7.S

## Purpose
Implements ARMv7 range TLB invalidation with SMP-aware shareable operations, UP alternatives, ASID-aware user invalidation, and erratum 720789 handling.

## Important APIs, Types, And Functions
Exports `v7wbi_flush_user_tlb_range` and `v7wbi_flush_kern_tlb_range`. Uses `dsb ish`, `isb`, alternative SMP/UP instruction patching, `mmid`, `asid`, and CP15 c8 TLB invalidate by MVA operations.

## Control Flow
User flush obtains the VMA mm context ID, issues `dsb ish`, aligns addresses, masks ASID, optionally zeros ASID for erratum 720789 on SMP, combines ASID with MVA, and loops issuing SMP shareable or UP local invalidates. Kernel flush performs the same page loop without ASID and finishes with `dsb ish; isb`.

## State, Dependencies, And Integration
State changed is local or broadcast TLB content. Dependencies are ARMv7-A CP15 semantics, alternative patching, `CONFIG_SMP`, `CONFIG_ARM_ERRATA_720789`, and `v7wbi_tlb_flags_smp/up`. Integration is through `v7wbi_tlb_fns` and processor tables in `proc-v7.S`.

## Risks And Test Signals
Risks are stale remote TLBs if SMP alternatives or flags mismatch, too-broad invalidation under erratum handling, missing barriers, and branch-range issues for large loops. Test with SMP ARMv7 boot, mprotect/unmap stress across CPUs, ASID reuse, erratum-configured builds, and kernel text mapping changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/tlb.c

## Purpose
Builds `struct cpu_tlb_fns` instances that bind architecture-specific assembly TLB range callbacks to the TLB flag sets used by the ARM MM subsystem.

## Important APIs, Types, And Functions
Declares assembly functions for v4, v4wb, v4wbi/Feroceon, v6, v7, and Faraday TLB variants. Defines `v4_tlb_fns`, `v4wb_tlb_fns`, `v4wbi_tlb_fns`, `v6wbi_tlb_fns`, `v7wbi_tlb_fns`, and `fa_tlb_fns` as `__initconst`.

## Control Flow
There is no runtime algorithm here beyond table initialization. Kconfig gates which tables are emitted. For v7, `tlb_flags` is selected from SMP or UP flags with `IS_ENABLED(CONFIG_SMP)`, and `CONFIG_SMP_ON_UP` emits alternative-patching metadata to replace the flags at runtime.

## State, Dependencies, And Integration
State is init-time constant function tables. Dependencies are `linux/types.h`, `asm/tlbflush.h`, the assembly symbols, and `offsetof` layout of `struct cpu_tlb_fns`. Integration is with proc-info entries that reference the matching `*_tlb_fns`.

## Risks And Test Signals
Risks include wrong table/function pairing, stale `struct cpu_tlb_fns` offset assumptions for SMP-on-UP patching, and C declaration mismatch with assembly symbols. Test signals are compile coverage for every `CONFIG_CPU_TLB_*`, SMP-on-UP boot, and runtime TLB flush tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/net/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/net/Makefile

## Purpose
Builds ARM-specific networking support objects. In this subset it controls inclusion of the 32-bit ARM BPF JIT.

## Important APIs, Types, And Functions
The sole rule is `obj-$(CONFIG_BPF_JIT) += bpf_jit_32.o`.

## Control Flow
Kbuild includes `bpf_jit_32.o` only when `CONFIG_BPF_JIT` is enabled. If disabled, networking falls back to interpreter or generic non-JIT paths.

## State, Dependencies, And Integration
No runtime state. Depends on Kbuild and `CONFIG_BPF_JIT`. Integrates with `arch/arm/net/bpf_jit_32.c` and the kernel BPF core.

## Risks And Test Signals
Risks are simple build gating mistakes. Test signals are ARM builds with `CONFIG_BPF_JIT=y/m/n` and BPF selftests confirming the arch JIT is present only when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/net/bpf_jit_32.c -->
# sources/distributed-fs/ceph-client/arch/arm/net/bpf_jit_32.c

## Purpose
Implements the eBPF JIT compiler for 32-bit ARM. It translates verifier-approved eBPF instructions into ARM A32 instructions, manages 64-bit BPF registers on a 32-bit register file, emits prologue/epilogue and helper-call ABI glue, allocates executable JIT images, flushes I-cache, and installs `prog->bpf_func`.

## Important APIs, Types, And Functions
Public integration points are `bpf_int_jit_compile(struct bpf_verifier_env *, struct bpf_prog *)` and `bpf_jit_needs_zext()`. Key internals include `struct jit_ctx`, `bpf2a32` register mapping, `_emit`, `emit_mov_i`, literal-pool handling for pre-v7, `arm_bpf_get_reg*`/`put_reg*`, ALU/shift/mul/div emitters, memory load/store emitters, branch comparison emitters, `emit_bpf_tail_call`, `build_prologue`, `build_epilogue`, `build_insn`, `build_body`, and `validate_code`.

## Control Flow
Compilation runs a fake pass to count generated instructions and fill BPF instruction offsets, appends prologue/epilogue sizing, allocates a `bpf_binary_header` initialized with UDF instructions, then performs a real pass that emits the prologue, body, and epilogue. The body switch handles ALU32/ALU64, loads/stores, endian conversions, branches, helper calls, tail calls, and exits. Unsupported pseudo calls, pseudo func immediates, and atomic operations return errors so execution falls back to the interpreter. Final validation rejects any remaining UDF holes, then icache is flushed and the image is locked read-only.

## State, Dependencies, And Integration
Persistent result state is `prog->bpf_func`, `prog->jited`, and `prog->jited_len`. Temporary state includes `ctx->offsets`, optional pre-v7 literal pool `imms`, `ctx->idx`, prologue/epilogue offsets, stack size, CPU architecture, and overflow flags. Dependencies are the BPF core, verifier metadata, `bpf_jit_binary_alloc/free/lock_ro`, `bpf_jit_dump`, ARM opcode helpers, `elf_hwcap`, `cpu_architecture()`, `flush_icache_range`, and math helpers for 64-bit division.

## Risks And Test Signals
Risks are incorrect 64-bit emulation over 32-bit register pairs, stack-frame or ABI misalignment, helper-call register preservation bugs, branch offset miscalculation, literal-pool overflow, unsupported opcode fallback regressions, tail-call count mishandling, and security issues if UDF validation or RO locking fails. Test signals include upstream BPF selftests on ARM, JIT on/off comparison, verifier zext tests, tail-call chains, helper calls with stack arguments, ALU64 division/modulo, big/little endian load/store coverage, pre-v7 literal-pool builds, and `bpf_jit_enable > 1` dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/net/bpf_jit_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/net/bpf_jit_32.h -->
# sources/distributed-fs/ceph-client/arch/arm/net/bpf_jit_32.h

## Purpose
Defines the ARM A32 register numbers, condition codes, instruction encodings, and macro constructors used by the 32-bit ARM eBPF JIT emitter.

## Important APIs, Types, And Functions
Defines register constants `ARM_R0` through `ARM_PC`, condition constants `ARM_COND_*`, shift types, base instruction constants such as `ARM_INST_ADD_R`, `ARM_INST_LDR_I`, `ARM_INST_BLX_R`, `ARM_INST_UDF`, and constructor macros such as `ARM_ADD_R`, `ARM_B`, `ARM_LDR_R_SI`, `ARM_MOVW`, `ARM_UMULL`, `ARM_MLS`, and `ARM_UXTH`.

## Control Flow
The file has no runtime flow. Its macros are pure bitfield encoders that assemble ARM instructions from register, immediate, shift, and condition inputs. `ARM_INST_UDF` supplies the faulting fill instruction used for JIT image holes.

## State, Dependencies, And Integration
No persistent state. It is included by `bpf_jit_32.c` and depends on ARM instruction encoding stability. Integration is tight: any macro bug produces invalid JIT machine code.

## Risks And Test Signals
Risks are bitfield mistakes, wrong immediate placement for MOVW/MOVT or load/store forms, UDF conflicts with kernel undefined-instruction hooks, and register-number mismatch with AAPCS expectations. Test signals are BPF JIT selftests, disassembly of `bpf_jit_dump` output, and compile-time coverage of each macro path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/net/bpf_jit_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/ARM-gcc.h -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/ARM-gcc.h

## Purpose
Provides compiler and integer-type adaptation for the SoftFloat code used by the NetWinder Floating Point Emulator. It defines exact-width and convenient-width integer aliases, 64-bit literal handling, inlining, and optional libfloat symbol remapping.

## Important APIs, Types, And Functions
Defines `flag`, `uint8`, `int8`, `uint16`, `int16`, `uint32`, `int32`, `bits8/16/32/64`, `sbits*`, `uint64`, `int64`, `LIT64(a)`, and `INLINE`. Under `__LIBFLOAT__`, it maps SoftFloat function names to GCC runtime helper names or private glue names.

## Control Flow
No runtime control flow. The preprocessor configures SoftFloat compilation for GCC/ARM and optionally for soft-float library symbol compatibility.

## State, Dependencies, And Integration
No state. Included by `milieu.h`, which is included by NWFPE and SoftFloat sources. Integration risk is broad because these typedefs determine the representation used by all emulator arithmetic.

## Risks And Test Signals
Risks include type-width mismatch on unusual compilers, wrong literal suffixes, and symbol collisions when `__LIBFLOAT__` is used. Test signals are compile coverage, structure-size checks in `fpmodule.c`, and floating-point emulator arithmetic tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/ARM-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/Makefile

## Purpose
Builds the NetWinder Floating Point Emulator object when `CONFIG_FPE_NWFPE` is enabled and adds optional extended-precision support.

## Important APIs, Types, And Functions
Defines `obj-$(CONFIG_FPE_NWFPE) += nwfpe.o`, the `nwfpe-y` object list, and `nwfpe-$(CONFIG_FPE_NWFPE_XP) += extended_cpdo.o`. Adds a Clang-specific flag for `softfloat.o` to avoid generating `__aeabi_uldivmod()` from `float64_rem()`.

## Control Flow
Kbuild links emulator core files into `nwfpe.o`; extended precision is conditionally linked. Compiler flags are conditionally applied for Clang.

## State, Dependencies, And Integration
No runtime state. Dependencies are Kconfig, Kbuild, compiler identity, and all listed NWFPE/SoftFloat sources. Integration is with ARM undefined-instruction handling and module init.

## Risks And Test Signals
Risks are missing object files, extended-precision link failures, and compiler optimization generating unavailable helper calls. Test signals are GCC and Clang ARM builds with and without `CONFIG_FPE_NWFPE_XP`, plus boot/module load of NWFPE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/double_cpdo.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/double_cpdo.c

## Purpose
Implements FPA11 CPDO arithmetic for double-precision operations and mixed single/double operands in NWFPE.

## Important APIs, Types, And Functions
Exports `DoubleCPDO(struct roundingData *, unsigned int opcode, FPREG *rFd)`. Defines `dyadic_double` and `monadic_double` dispatch tables plus helpers for reverse subtract/divide, move, negate, and absolute value. Uses SoftFloat functions such as `float64_add`, `float64_mul`, `float64_div`, `float64_rem`, `float64_round_to_int`, and `float64_sqrt`.

## Control Flow
`DoubleCPDO` resolves `Fm` from a constant, single register converted to double, or double register. For dyadic operations it resolves `Fn` similarly. It indexes the opcode dispatch table by `(opcode & MASK_ARITHMETIC_OPCODE) >> 20`; missing table entries cause failure. Successful operations write `rFd->fDouble`.

## State, Dependencies, And Integration
State is the current thread's `FPA11` register file and type tags. Dependencies are `fpa11.h`, `fpopcode.h`, and SoftFloat. Integrated through `EmulateCPDO`, which handles destination-size conversion and exception raising.

## Risks And Test Signals
Risks include endian-specific sign-bit manipulation, unsupported deprecated opcodes, type-tag mismatches, and precision/rounding regressions. Test signals are FPA double arithmetic instruction tests, mixed single/double operands, NaN/exception cases, and endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/double_cpdo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/entry.S -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/entry.S

## Purpose
Provides the assembly entry path from ARM undefined-instruction handling into NWFPE. It dispatches coprocessor 1/2 FPA instructions, invokes the emulator, chains consecutive FP instructions to amortize trap overhead, and returns either to normal exception return or undefined-instruction failure.

## Important APIs, Types, And Functions
Exports `nwfpe_enter`, `call_fpe`, `fp_enter`, and `no_fp`. Uses `EmulateAll`, `arm_check_condition`, user access macros, exception-table fixups, `TI_FPSTATE`, `TI_FLAGS`, optional iWMMXt enabling, and return addresses passed in `r9` and `lr`.

## Control Flow
`call_fpe` loads the faulting user opcode, rejects non-coprocessor or non-FPE coprocessors, handles optional iWMMXt CP0/1 access, and branches to `fp_enter`. `nwfpe_enter` checks ARM condition codes, calls `EmulateAll`, and on success fetches the next user instruction. If the next instruction still looks like FP, it updates saved PC and emulates again; otherwise it returns via `r9`.

## State, Dependencies, And Integration
State modified includes saved user PC/CPSR in `pt_regs`, current thread FP workspace, and user access state. Dependencies include `asm/assembler.h`, opcode endian conversion, exception table machinery, and `fpmodule.c` patching `fp_enter` to `nwfpe_enter`.

## Risks And Test Signals
Risks are incorrect PC advancement, user memory fault fixup bugs, condition-code mis-evaluation, chained instruction overrun, and conflicts with VFP/iWMMXt dispatch. Test signals are undefined-instruction FP traps, conditional FP instructions, faulting instruction fetch, chained FP sequences, big-endian instruction fetch, and iWMMXt coexistence builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/extended_cpdo.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/extended_cpdo.c

## Purpose
Implements extended-precision CPDO arithmetic for NWFPE when `CONFIG_FPE_NWFPE_XP` is enabled.

## Important APIs, Types, And Functions
Exports `ExtendedCPDO`. Defines `dyadic_extended` and `monadic_extended` tables for add, multiply, subtract, reverse subtract, divide, reverse divide, remainder, move, negate, absolute, round, square root, and normalize. Uses `floatx80_*` SoftFloat operations.

## Control Flow
The function resolves `Fm` from a constant or from single/double/extended FPA register values converted to `floatx80`. Dyadic operations similarly resolve `Fn`. It dispatches by arithmetic opcode table and writes the extended result to `rFd->fExtended`, returning 0 for unsupported opcodes or invalid source types.

## State, Dependencies, And Integration
State is the FPA11 register file and type tags. Dependencies include `CONFIG_FPE_NWFPE_XP`, `softfloat.h`, `fpopcode.h`, and constants from `fpopcode.c`. Integrated through `EmulateCPDO`, which chooses extended mode based on operand/destination type and later converts destination size if required.

## Risks And Test Signals
Risks are extended format ABI mismatch, sign-bit handling, unsupported opcode behavior, and conversion/rounding regressions. Test signals include extended precision arithmetic, mixed precision conversions, NaN and exception behavior, and build coverage with XP enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/extended_cpdo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11.c

## Purpose
Owns FPA11 emulator initialization, rounding mode/precision decoding, and top-level opcode dispatch for NWFPE.

## Important APIs, Types, And Functions
Defines `nwfpe_init_fpa`, `SetRoundingMode`, `SetRoundingPrecision`, and `EmulateAll`. Internal `resetFPA11` initializes register type tags and FPSR system ID/AC bit.

## Control Flow
`nwfpe_init_fpa` clears the per-thread `FPA11` state, resets FPSR/type tags, and marks `initflag`. `EmulateAll` checks the coprocessor field for FPA11 CP1/CP2, then distinguishes CPDO/CPRT versus CPDT by opcode class and dispatches to `EmulateCPDO`, `EmulateCPRT`, or `EmulateCPDT`. Unknown opcodes return 0 for undefined-instruction handling.

## State, Dependencies, And Integration
State is `current_thread_info()->fpstate`, including register values, FPSR, FPCR, type tags, and init flag. Dependencies are `fpa11.h`, `fpopcode.h`, `fpmodule.inl`, and SoftFloat rounding constants. Integrated with `entry.S` and thread flush notifier initialization.

## Risks And Test Signals
Risks are opcode misclassification, incorrect initial FPSR compatibility, stale per-thread state, and rounding mode mismatch. Test signals are first-use FP traps, thread flush/exec state reset, CPDO/CPRT/CPDT dispatch tests, and invalid opcode fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11.h -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11.h

## Purpose
Defines the FPA11 emulator state model, register representation, type tags, rounding data, and public emulator entry points.

## Important APIs, Types, And Functions
Defines `GET_FPA11()`, `GET_USERREG()`, `struct roundingData`, type tags `typeNone`, `typeSingle`, `typeDouble`, `typeExtended`, union `FPREG`, and packed struct `FPA11`. Declares initialization, dispatch, CPDT/CPDO/CPRT, precision-specific CPDO, and transfer helpers.

## Control Flow
No runtime control flow. The macros compute current-thread FPA state and saved user register access; functions declared here are implemented across the NWFPE sources.

## State, Dependencies, And Integration
`FPA11` is exported to user space through the ARM user FP state ABI and must match `struct user_fp`. Its layout contains eight 12-byte FP registers, FPSR, FPCR, eight type tags, and `initflag`. Dependencies include `linux/thread_info.h`, `fpsr.h`, `milieu.h`, and `softfloat.h`.

## Risks And Test Signals
Risks are ABI-breaking layout changes, wrong packing/alignment, incorrect `GET_USERREG()` stack assumptions, and type-tag misuse. Test signals include size checks in `fpmodule.c`, ptrace/core-dump FP state compatibility, first-use initialization, and all NWFPE arithmetic/transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cpdo.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cpdo.c

## Purpose
Dispatches FPA11 coprocessor data operation instructions to the correct precision-specific arithmetic implementation and normalizes the result to the instruction's destination size.

## Important APIs, Types, And Functions
Exports `EmulateCPDO`. Calls `SingleCPDO`, `DoubleCPDO`, and optionally `ExtendedCPDO`. Uses `roundingData`, `SetRoundingMode`, `SetRoundingPrecision`, `getDestinationSize`, `getFn`, `getFm`, `getFd`, `MONADIC_INSTRUCTION`, `CONSTANT_FM`, and `float_raise`.

## Control Flow
It validates destination size, initializes rounding state, chooses working precision from destination for monadic operations or from the largest source operand type for dyadic operations, calls the matching precision handler, updates destination type, converts the result if working and destination precision differ, raises SoftFloat exceptions, and returns success/failure to the undefined-instruction path.

## State, Dependencies, And Integration
State is FPA11 registers and type tags. Dependencies include precision-specific CPDO files, SoftFloat conversions, and opcode macros. Integration is from `EmulateAll` and back to `entry.S` via success/failure.

## Risks And Test Signals
Risks include incorrect working precision selection, destination conversion bugs, missing extended paths under XP, and exception propagation mistakes. Test signals are mixed-precision arithmetic, monadic/dyadic opcode coverage, unsupported precision traps, and exception flag/trap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cpdo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cpdt.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cpdt.c

## Purpose
Implements FPA11 coprocessor data transfer instructions: load/store single, double, extended, and multiple-register formats between user memory and the emulator register file.

## Important APIs, Types, And Functions
Exports `PerformLDF`, `PerformSTF`, `PerformLFM`, `PerformSFM`, and `EmulateCPDT`. Internal helpers include `loadSingle`, `loadDouble`, `loadExtended`, `loadMultiple`, `storeSingle`, `storeDouble`, `storeExtended`, and `storeMultiple`.

## Control Flow
Transfer functions compute base, final, and effective addresses from `Rn`, pre/post-index, up/down, writeback, and offset fields. PC-relative base uses adjusted PC and disables writeback. Loads update register value and type tag. Stores convert from the current register type to requested transfer precision, write user memory, and raise pending rounding exceptions. Multiple-register transfers wrap Fd modulo 8 and move 3-word internal register formats.

## State, Dependencies, And Integration
State includes user memory, saved user general registers for writeback, FPA11 register values/type tags, and FPSR exception state. Dependencies are `get_user`, `put_user`, `fpmodule.inl`, endian handling, SoftFloat conversions, and opcode macros. Integrated via `EmulateAll` CPDT dispatch.

## Risks And Test Signals
Risks include unchecked `get_user`/`put_user` return handling, endian word-order mistakes, PC-relative address errors, writeback bugs, multiple-register wrap errors, and user fault behavior. Test with LDF/STF/LFM/SFM instruction suites, bad user pointers, endian builds, PC-relative transfers, and writeback cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cpdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cprt.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cprt.c

## Purpose
Implements FPA11 coprocessor register transfer, integer/float conversion, FPSR access, and comparison instructions.

## Important APIs, Types, And Functions
Exports `EmulateCPRT`, `PerformFLT`, and `PerformFIX`; internal `PerformComparison` handles CMF/CNF/CMFE/CNFE variants. Uses `readRegister`, `writeRegister`, `readFPSR`, `writeFPSR`, `writeConditionCodes`, SoftFloat conversion/comparison helpers, and opcode decode macros.

## Control Flow
`EmulateCPRT` fast-paths comparison opcodes, otherwise dispatches FLT, FIX, WFS, or RFS. `PerformFLT` converts an integer ARM register to requested FPA precision. `PerformFIX` converts an FPA register to a 32-bit integer ARM register. Comparisons resolve constants or registers, promote as needed, handle optional negated comparison, set N/Z/C/V flags, and raise invalid exceptions for unordered extended comparisons when required.

## State, Dependencies, And Integration
State includes FPA11 registers/type tags/FPSR and saved user ARM registers/CPSR. Dependencies are `fpa11.inl`, `fpmodule.inl`, SoftFloat, and `fpopcode.h`. Integrated via `EmulateAll` and `entry.S`.

## Risks And Test Signals
Risks are condition-code compatibility, NaN/unordered behavior, FPSR sysid preservation, conversion rounding exceptions, and unsupported FPCR operations. Test signals are FLT/FIX tests, FPSR read/write, all compare variants including NaNs, and CPSR flag validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cprt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpmodule.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpmodule.c

## Purpose
Initializes and tears down the NWFPE module/built-in handler, patches the kernel FP entry pointer, resets per-thread FP state on thread flush, and maps SoftFloat exceptions to FPSR flags or SIGFPE.

## Important APIs, Types, And Functions
Defines `fpe_init`, `fpe_exit`, `nwfpe_notify`, notifier block `nwfpe_notifier_block`, and `float_raise`. It references `kern_fp_enter`/`fp_enter`, `nwfpe_enter`, `fpe_type`, `thread_register_notifier`, and `fp_send_sig`/`send_sig`.

## Control Flow
At init, it validates `FPA11` and `FPREG` sizes, honors `fpe_type`, logs precision mode, registers a thread notifier, saves the old FP handler, and installs `nwfpe_enter`. Exit unregisters and restores the original handler. `float_raise` checks trap-enable bits, sets cumulative exception flags for untrapped exceptions, and sends `SIGFPE` when enabled traps match raised flags.

## State, Dependencies, And Integration
Persistent state includes `orig_fp_enter`, patched `kern_fp_enter`, thread notifier registration, and per-thread FPA state initialized on `THREAD_NOTIFY_FLUSH`. Dependencies are Linux module/init/signal/thread-notify APIs, `fpa11.inl`, SoftFloat flags, and FPSR bit definitions.

## Risks And Test Signals
Risks are handler pointer races, ABI size mismatches, notifier ordering, incorrect SIGFPE routing, and failure to restore handlers on unload. Test signals are module load/unload, built-in boot with `fpe_type`, thread exec/flush state reset, floating-point exception trap tests, and debug-user exception logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpmodule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpmodule.h -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpmodule.h

## Purpose
Defines numeric indices for ARM saved user registers used by NWFPE helper code.

## Important APIs, Types, And Functions
Defines `REG_R0` through `REG_R10`, `REG_FP`, `REG_IP`, `REG_SP`, `REG_LR`, `REG_PC`, `REG_CPSR`, and `REG_ORIG_R0`. `REG_R9` is duplicated with the same value.

## Control Flow
No runtime flow. Constants are consumed by inline register accessors and CPDT/CPRT logic.

## State, Dependencies, And Integration
No state. Integrates with `struct pt_regs::uregs[]` layout expected by ARM ptrace/register conventions and with `fpmodule.inl` read/write helpers.

## Risks And Test Signals
Risks are index drift from ARM `pt_regs` layout, duplicated constants hiding edits, and PC/CPSR confusion. Test signals are conversion/transfer tests that read/write general registers, PC-relative FP transfers, and CPSR condition-code comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpmodule.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpopcode.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpopcode.c

## Purpose
Provides FPA11 floating-point constant tables used when an opcode encodes `Fm` as one of the architected constants rather than a register.

## Important APIs, Types, And Functions
Defines `float64Constant[8]`, `float32Constant[8]`, and under `CONFIG_FPE_NWFPE_XP`, `floatx80Constant[8]`. Values are 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 0.5, and 10.0 in each precision.

## Control Flow
No runtime flow beyond indexed table lookup through inline accessors in `fpopcode.h`.

## State, Dependencies, And Integration
The constant arrays are read-only global data. Dependencies are `fpa11.h`, `softfloat.h`, `fpopcode.h`, and the precision type definitions. Integrated by CPDO and comparison code through `getSingleConstant`, `getDoubleConstant`, and `getExtendedConstant`.

## Risks And Test Signals
Risks are wrong bit patterns, index-order mismatches with opcode encoding, and extended precision conditional build issues. Test signals are constant-operand arithmetic/comparison tests across single/double/extended precision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpopcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpopcode.h -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpopcode.h

## Purpose
Documents and encodes the FPA11 instruction formats and provides opcode masks, tests, field extractors, condition-code constants, rounding decoders, and constant accessors for the emulator.

## Important APIs, Types, And Functions
Defines CPDT, CPDO, CPRT masks and opcode constants; transfer flags such as `BIT_PREINDEX`, `BIT_UP`, `BIT_WRITE_BACK`, `BIT_LOAD`; arithmetic codes like `ADF_CODE`, `MUF_CODE`, `MVF_CODE`, `SQT_CODE`; CPRT codes like `FLT_CODE`, `FIX_CODE`, `WFS_CODE`, `CMF_CODE`; field getters `getRn`, `getFd`, `getFn`, `getFm`, `getRd`; and inline decoders `getTransferLength`, `getRegisterCount`, `getRoundingPrecision`, `getDestinationSize`.

## Control Flow
No runtime stateful flow. Inline helper functions switch on masked opcode fields and return compact enum-like values consumed by emulator dispatch.

## State, Dependencies, And Integration
No writable state. Depends on `CONFIG_FPE_NWFPE_XP` for extended constants and on type tags from `fpa11.h`. Integrated across all NWFPE instruction decode paths.

## Risks And Test Signals
Risks are mask mistakes causing wrong instruction class, undefined opcodes incorrectly accepted, transfer length/count mismatch, and condition-code incompatibility. Test signals are decode unit tests or instruction suites covering every CPDT/CPDO/CPRT format and invalid encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpopcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpsr.h -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpsr.h

## Purpose
Defines the FPA11 floating-point status register and control register bit layout used by NWFPE.

## Important APIs, Types, And Functions
Defines `FPSR`, `FPCR`, system ID bits, trap-enable bits `BIT_IXE` through `BIT_IOE`, system-control bits including `BIT_AC`, exception flags `BIT_IXC` through `BIT_IOC`, FPCR bits, operation/precision/source/destination masks, and write/read masks `MASK_WFC` and `MASK_RFC`.

## Control Flow
No runtime flow. Constants drive `fpa11.inl`, `fpmodule.c`, CPDO rounding, and CPRT FPSR/FPCR behavior.

## State, Dependencies, And Integration
No state itself, but it defines the bit contract for `FPA11.fpsr` and `FPA11.fpcr`. Integrated with user-visible FP state, SoftFloat exception mapping, and comparison condition behavior.

## Risks And Test Signals
Risks are ABI-visible bit mistakes, incorrect trap-enable mapping to cumulative flags, and read/write mask regressions. Test signals are FPSR/FPCR read/write instructions, exception flag tests, SIGFPE trap-enable tests, and user ABI inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/milieu.h -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/milieu.h

## Purpose
Adapts the SoftFloat milieu layer for NWFPE by including the ARM/GCC type definitions and defining boolean constants.

## Important APIs, Types, And Functions
Includes `ARM-gcc.h` and defines enum values `FALSE = 0` and `TRUE = 1`.

## Control Flow
No runtime flow. It is a portability header used by SoftFloat and NWFPE code.

## State, Dependencies, And Integration
No state. Depends on `ARM-gcc.h`. Integrated through `fpa11.h` and SoftFloat headers to provide shared integer and flag types.

## Risks And Test Signals
Risks are minimal but include accidental type environment drift if `ARM-gcc.h` changes. Test signals are full NWFPE compile coverage and SoftFloat arithmetic tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/milieu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/single_cpdo.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/single_cpdo.c

## Purpose
Implements FPA11 CPDO arithmetic for single-precision operands and results in NWFPE.

## Important APIs, Types, And Functions
Exports `SingleCPDO`. Defines `dyadic_single` and `monadic_single` tables for add, multiply, subtract, reverse subtract, divide, reverse divide, remainder, move, negate, absolute, round, square root, and normalize. Uses `float32_*` SoftFloat functions and single-precision constants.

## Control Flow
`SingleCPDO` resolves `Fm` from a constant or a single-precision register. For dyadic instructions it requires `Fn` to also be single precision. It indexes the opcode dispatch table and writes `rFd->fSingle` on success; unsupported opcodes or incompatible source types return 0.

## State, Dependencies, And Integration
State is FPA11 single registers and type tags. Dependencies are `fpa11.h`, `softfloat.h`, and `fpopcode.h`. Integrated through `EmulateCPDO`, which selects precision, converts destinations when necessary, and raises exceptions.

## Risks And Test Signals
Risks include rejecting valid promoted operands too early, unsupported deprecated functions, incorrect sign manipulation for negate/abs, and exception/rounding regressions. Test signals are single-precision FPA arithmetic, constant operands, invalid type handling, NaN/exception cases, and destination conversion via `EmulateCPDO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/single_cpdo.c -->
