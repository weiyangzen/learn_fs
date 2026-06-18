# Research: subset-b-000853

Grouped research for SPARC SRMMU/cache/TLB, SPARC BPF JIT, hibernation, PROM, vDSO, video helpers, and UM Kbuild sources. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/srmmu.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/srmmu.c

Purpose: implements the SPARC32 SRMMU memory-management core for sun4m/sun4d/LEON-style systems. It builds kernel mappings, allocates non-cacheable page-table memory, manages hardware MMU contexts, maps I/O ranges, detects SRMMU module variants, and installs CPU-specific cache/TLB operation tables.

Important APIs/types/functions: exported or architecture-visible entry points include `load_mmu()`, `srmmu_paging_init()`, `switch_mm()`, `destroy_context()`, `init_new_context()`, `get_pgd_fast()`, `pte_alloc_one()`, `pte_free()`, `pmd_set()`, `srmmu_get_nocache()`, `srmmu_free_nocache()`, `srmmu_mapiorange()`, `srmmu_unmapiorange()`, `arch_zone_limits_init()`, and `mmu_info()`. Important state includes `srmmu_modtype`, `srmmu_name`, `sparc32_cachetlb_ops`, `local_ops`, `srmmu_context_table`, `srmmu_ctx_table_phys`, the nocache bitmap, context lists, and hardware-bug flags.

Control flow: boot calls `load_mmu()`, which probes the chip with `get_srmmu_type()`, chooses operations for HyperSparc, Swift, TurboSparc, Tsunami, Viking/MXCC, or LEON, then initializes IOMMU/SMP support. `srmmu_paging_init()` discovers context count from PROM, runs bootmem setup, sizes and maps the nocache pool, inherits PROM mappings, maps low memory with large SRMMU PTEs, creates the context table, and preallocates IO/DVMA/fixmap/pkmap page-table skeletons. Runtime `switch_mm()` allocates or reuses contexts and writes context descriptors before setting the SRMMU context register.

State and persistence: all state is runtime kernel state: non-cacheable pools, page tables, context ownership lists, cache/TLB op pointers, chip feature flags, and exported VAC dimensions. No filesystem persistence exists, but the code establishes long-lived boot mappings and hardware context-table state.

Dependencies and integration points: depends on PROM memory/CPU properties, `memblock`, `bootmem_init()`, SPARC page-table helpers, `bit_map_*`, SRMMU accessors in `srmmu_access.S`, CPU-specific assembly files, SMP cross-call helpers, IOMMU/DVMA setup, and `/proc/cpuinfo`-style `mmu_info()` reporting.

Risks: this file sits on the boot and MMU critical path. Alignment errors in nocache allocation, stale context descriptors, missing cache/TLB flushes, or wrong chip detection can corrupt memory. CPU erratum handling is especially fragile for Swift and Viking. SMP wrappers must avoid unnecessary cross-calls while still flushing remote CPUs that ran an address space.

Test signals: boot SPARC32 under each supported CPU family, verify `/proc/cpuinfo` MMU details and nocache usage, stress fork/exec/context recycling, map/unmap SBUS/DVMA devices, run DMA workloads on Viking/Swift, exercise SMP TLB shootdowns, and run memory-management stress with high pkmap/fixmap and page-table churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/srmmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/srmmu_access.S -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/srmmu_access.S

Purpose: provides small assembly accessors for SRMMU control registers that can be runtime-patched between Sun SRMMU and LEON ASI encodings.

Important APIs/functions: defines `srmmu_get_mmureg()`, `srmmu_set_mmureg()`, `srmmu_set_ctable_ptr()`, `srmmu_set_context()`, `srmmu_get_context()`, `srmmu_get_fstatus()`, and `srmmu_get_faddr()`. The `LEON_PI` and `SUN_PI_` macros select the actual load/store ASI instruction sequence.

Control flow: each function performs a single MMU register load or store and returns through `retl`. `srmmu_set_ctable_ptr()` shifts and masks the physical context-table pointer before writing `SRMMU_CTXTBL_PTR`; context and fault accessors use the corresponding SRMMU register offsets.

State and persistence: this file does not own memory state; it reads and mutates CPU MMU registers. Effects persist only in hardware state until the next register write or reset.

Dependencies and integration points: used heavily by `srmmu.c`, trap/fault handling, and CPU-specific setup code. It depends on `pgtsrmmu.h`, `asi.h`, and the LEON one-instruction patch mechanism.

Risks: wrong ASI patching makes every MMU control access hit the wrong register space. Context-table pointer shifting must match SRMMU encoding. These routines are tiny but central to boot and fault handling.

Test signals: boot both LEON and non-LEON SRMMU kernels, confirm context switching, fault status reporting, and context-table installation work, and verify runtime patch sections are applied before normal MMU use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/srmmu_access.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/swift.S -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/swift.S

Purpose: implements MicroSPARC-II/Swift cache, TLB, DMA, and signal-instruction flush routines for the SPARC32 SRMMU operation table.

Important APIs/functions: exports `swift_flush_cache_all()`, `swift_flush_cache_mm()`, `swift_flush_cache_range()`, `swift_flush_cache_page()`, `swift_flush_page_for_dma()`, `swift_flush_page_to_ram()`, `swift_flush_sig_insns()`, `swift_flush_tlb_all()`, `swift_flush_tlb_mm()`, `swift_flush_tlb_range()`, and `swift_flush_tlb_page()`.

Control flow: the active cache path aliases all cache flush variants to a conservative loop that clears data and instruction cache tags. Signal trampoline flushing issues two `flush` instructions. TLB range/mm operations fall back to whole-TLB probe flushes after checking `mm->context`, and page flushes also use a global probe flush in the compiled path.

State and persistence: no owned memory state; all effects are hardware cache/TLB invalidations. The routines observe `mm->context` and VMA `vm_mm` offsets from assembly constants.

Dependencies and integration points: selected by `init_swift()` in `srmmu.c` through `swift_ops`. Depends on SRMMU ASIs, PSR/window macros, page size constants, and `asm-offsets.h` structure offsets.

Risks: Swift has documented cache/TLB coherency errata, so this implementation chooses broad invalidation over fine-grained behavior. Overly narrow flushes could expose stale instructions, stale user mappings, or DMA incoherency; overly broad flushes are performance-costly but safer.

Test signals: run on MicroSPARC-II hardware or emulator with fork/exec, signal delivery, mmap permission changes, packet/DMA I/O, and page-table stress. Validate that no stale executable mappings remain after signal trampoline or text updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/swift.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/tlb.c

Purpose: implements SPARC64 software batching for TLB and TSB invalidations, plus transparent-hugepage PMD accounting and split/deposit helpers.

Important APIs/functions: key functions are `flush_tlb_pending()`, `arch_enter_lazy_mmu_mode()`, `arch_flush_lazy_mmu_mode()`, `arch_leave_lazy_mmu_mode()`, `tlb_batch_add()`, internal `tlb_batch_add_one()`, and THP helpers `set_pmd_at()`, `pmdp_invalidate()`, `pgtable_trans_huge_deposit()`, and `pgtable_trans_huge_withdraw()`. Per-CPU state is `struct tlb_batch tlb_batch`.

Control flow: lazy MMU mode disables preemption and accumulates virtual addresses for one `mm`. When the batch fills, changes `mm`, changes hugepage shift, or leaves lazy mode, `flush_tlb_pending()` flushes matching TSB entries first and then performs local or SMP TLB shootdown. `tlb_batch_add()` also handles D-cache alias flushes for dirty file-backed pages before queuing the TLB invalidation.

State and persistence: state is per-CPU batching metadata: target `mm`, address count, hugepage shift, and address array. THP counters live in `mm->context.thp_pte_count` and `hugetlb_pte_count`.

Dependencies and integration points: depends on generic MMU-gather/lazy-MMU hooks, SPARC64 TSB code, `global_flush_tlb_page()`, `smp_flush_tlb_pending()`, `__flush_tlb_pending()`, cache alias helpers, and THP page-table APIs.

Risks: batching must not mix address spaces or hugepage granularities. Missing TSB invalidation can repopulate stale TLB entries. D-cache alias handling depends on physical/virtual color checks. THP counter imbalance can prevent correct huge TSB allocation.

Test signals: run KUnit lazy-MMU tests, THP split/collapse stress, hugetlb and huge-zero-page faults, SMP mmap/munmap/mprotect workloads, file-backed dirty-page alias tests, and non-SMP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/tsb.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/tsb.c

Purpose: manages SPARC64 Translation Storage Buffers: kernel/user TSB flushing, per-mm TSB allocation and growth, TSB register setup, slab cache creation, and context destruction.

Important APIs/functions: exports `flush_tsb_kernel_range()`, `flush_tsb_user()`, `flush_tsb_user_page()`, `pgtable_cache_init()`, `tsb_grow()`, `init_new_context()`, and `destroy_context()`. Important helpers include `tsb_hash()`, `tag_compare()`, `setup_tsb_params()`, `tsb_size_to_rss_limit()`, and `tsb_destroy_one()`.

Control flow: flush paths hash virtual addresses to TSB slots and invalidate matching tags, using scan mode for very large kernel ranges. User flushes hold `mm->context.lock`, choose base or huge TSB, convert virtual to physical base for Cheetah+/hypervisor, and invalidate one or multiple hugepage hash entries. `tsb_grow()` selects a power-of-two TSB size from RSS, allocates a physically contiguous slab object, invalidates tags, copies old TSB contents when growing, installs new register parameters, synchronizes remote CPUs, then frees the old TSB.

State and persistence: per-mm context stores TSB pointers, entry counts, register values, map virtual addresses/PTEs, RSS growth limits, hypervisor descriptors, ADI tag storage, and locks. All state is runtime-only.

Dependencies and integration points: depends on TSB assembly helpers (`tsb_flush`, `tsb_init`, `copy_tsb`), `mmu_context`, SPARC TLB type selection, hypervisor TSB descriptors, slab caches, NUMA allocation, SMP TSB sync, hugepage/THP counters, and ADI tag storage teardown.

Risks: TSB growth races with hardware miss handlers and remote CPUs, so the context lock and post-install sync are critical. High-order allocation failures intentionally disable future growth. Wrong page-size register encoding or physical-address conversion can break every user TLB miss.

Test signals: fork/exec under growing RSS, hugepage and THP faults, memory pressure during TSB growth, SMP address-space migration, hypervisor and non-hypervisor machines, kernel range invalidation, and ADI tag storage cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/tsb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/tsunami.S -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/tsunami.S

Purpose: supplies MicroSPARC-I/Tsunami cache and TLB operations plus an optimized page-copy routine that can be patched into the generic SPARC32 block operation.

Important APIs/functions: exports `tsunami_flush_cache_all()`, `tsunami_flush_cache_mm()`, `tsunami_flush_cache_range()`, `tsunami_flush_cache_page()`, `tsunami_flush_page_to_ram()`, `tsunami_flush_page_for_dma()`, `tsunami_flush_sig_insns()`, `tsunami_flush_tlb_all()`, `tsunami_flush_tlb_mm()`, `tsunami_flush_tlb_range()`, `tsunami_flush_tlb_page()`, and `tsunami_setup_blockops()`.

Control flow: cache flushes check `mm->context` for mm/range/page variants and otherwise clear I-cache and D-cache via ASI flush-clear stores. TLB mm/range flushes perform a full probe flush; page flush temporarily switches the SRMMU context, flushes the selected page, and restores the old context. `tsunami_setup_blockops()` copies the local `tsunami_copy_1page` instruction sequence into `__copy_1page` and flushes caches.

State and persistence: no kernel data ownership beyond self-modifying the block-copy routine at setup. Hardware cache/TLB state is invalidated.

Dependencies and integration points: selected by `init_tsunami()` in `srmmu.c`; depends on SRMMU ASIs, `asm-offsets.h`, SPARC register windows, and `__copy_1page`.

Risks: context restore after page TLB flush is mandatory. The block-copy patch depends on exact instruction range and cache coherency. Broad cache flushing is simple but affects performance.

Test signals: boot Tsunami systems, run mmap/munmap and signal tests, verify DMA coherency, compare page-copy correctness under copy-on-write and fork stress, and check that patched `__copy_1page` executes after setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/tsunami.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/ultra.S -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/ultra.S

Purpose: provides SPARC64 low-level TLB/cache flush implementations and SMP cross-call handlers for Spitfire, Cheetah, and sun4v hypervisor systems, with boot-time text patching to select the correct implementation.

Important APIs/functions: public symbols include `__flush_tlb_mm()`, `__flush_tlb_page()`, `__flush_tlb_pending()`, `__flush_tlb_kernel_range()`, `__flush_icache_page()`, optional `__flush_dcache_page()`, SMP handlers `xcall_flush_tlb_mm()`, `xcall_flush_tlb_page()`, `xcall_flush_tlb_kernel_range()`, dcache xcalls, tick/PMU/global-register xcalls, and patchers `cheetah_patch_cachetlbops()` and `hypervisor_patch_cachetlbops()`.

Control flow: generic entry points start as Spitfire demap routines. Cheetah patching replaces fixed instruction windows to use primary context and preserve nucleus page-size fields; hypervisor patching replaces them with fast-trap and unmap-trap calls. Pending/page flushes temporarily install the target context and invalidate D/I MMUs as requested; kernel range flushes demap page-by-page or fall back to full non-locked TLB entry scans/context demap. SMP xcall paths run at trap level and finish with `retry`.

State and persistence: modifies MMU context registers, TLB entries, cache tags, and kernel text instruction sequences. Cross-call snapshot routines write per-CPU diagnostic snapshot arrays.

Dependencies and integration points: used by SPARC64 TLB/cache flush APIs, SMP xcall machinery, hypervisor trap ABI, `tlb.c` batching, dcache alias handling, PMU diagnostics, and tick synchronization.

Risks: instruction counts in patch windows must match callers. PSTATE/TL manipulation, context restore, and hypervisor error handling are correctness-critical. A wrong demap scope can either miss stale translations or evict locked kernel mappings.

Test signals: boot Spitfire, Cheetah, and sun4v systems; run SMP TLB shootdown stress, BPF/JIT text flushes, kernel module load/unload, dcache alias tests, hypervisor trap failure injection, PMU snapshot users, and tick synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/ultra.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/viking.S -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/viking.S

Purpose: implements TI Viking and Viking/MXCC cache/TLB operations for SPARC32 SRMMU systems, including sun4d SMP TLB-flush serialization.

Important APIs/functions: exports `viking_flush_cache_all()`, `viking_flush_cache_mm()`, `viking_flush_cache_range()`, `viking_flush_cache_page()`, `viking_flush_page()`, `viking_mxcc_flush_page()`, `viking_flush_page_for_dma()`, `viking_flush_page_to_ram()`, `viking_flush_sig_insns()`, `viking_flush_tlb_all()`, `viking_flush_tlb_mm()`, `viking_flush_tlb_range()`, `viking_flush_tlb_page()`, and SMP `sun4dsmp_flush_tlb_*()` variants.

Control flow: cache flushes mostly flush register windows and rely on broad behavior selected by `srmmu.c`. `viking_flush_page()` scans D-cache tags by set/block to evict a matching physical page; MXCC uses stream registers to flush cache streams. TLB functions switch to the target context, demap all/mm/range/page, then restore the previous context. sun4d SMP wrappers serialize the same operations with an `ldstub` spin byte to avoid XBUS broadcast FIFO overflow.

State and persistence: only hardware cache/TLB state and the SMP spin byte are mutated. No filesystem or long-lived allocation state exists.

Dependencies and integration points: selected by `init_viking()` and the sun4d SMP op table in `srmmu.c`; depends on MXCC ASIs, Viking register definitions, SRMMU context registers, and VMA/mm offset constants.

Risks: page cache flush tag comparisons must match physical tag encoding. Context restore after flush is mandatory. sun4d serialization is a hardware workaround; removing it risks lost broadcast invalidations and memory corruption.

Test signals: run Viking with and without MXCC, sun4d SMP TLB shootdown stress, DMA tests on old Viking, page-color alias workloads, mprotect/munmap range invalidations, and fork/exec with many active contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/viking.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/net/Makefile

Purpose: wires SPARC architecture-specific BPF JIT objects into kbuild.

Important APIs/targets: builds `bpf_jit_comp_$(BITS).o` when `CONFIG_BPF_JIT` is enabled. On 32-bit builds it additionally builds `bpf_jit_asm_32.o`.

Control flow: kbuild expands `$(BITS)` to choose `bpf_jit_comp_32.o` or `bpf_jit_comp_64.o`. The 32-bit helper assembly is required only for classic BPF skb load stubs.

State and persistence: no runtime state; it affects build graph composition.

Dependencies and integration points: integrates with the kernel networking/filter subsystem and architecture build variables. It assumes the 64-bit compiler is self-contained and the 32-bit compiler depends on external assembly stubs.

Risks: wrong `BITS` selection or missing 32-bit stub object breaks BPF JIT linkage. Accidentally building assembly on 64-bit would duplicate nonexistent symbols.

Test signals: build sparc32 and sparc64 with `CONFIG_BPF_JIT=y`, and verify generated objects export the expected BPF JIT entry points without unresolved helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_32.h

Purpose: defines the SPARC32 classic BPF JIT register ABI and declares assembly skb load helpers.

Important APIs/types/functions: defines register numbers for C emission and register aliases for assembly. BPF `A`, `X`, skb pointer, saved `%o7`, skb head length, data pointer, temporaries, and offset registers map to `%o0`-`%o5` and `%g1`-`%g3`. Declares helper entry arrays such as `bpf_jit_load_word`, `bpf_jit_load_half`, `bpf_jit_load_byte`, `bpf_jit_load_byte_msh`, and positive/negative-offset variants.

Control flow: no executable flow; the C compiler and assembly stubs include the same header so emitted calls and stub register use agree.

State and persistence: no state. It defines an ABI contract for generated code.

Dependencies and integration points: included by `bpf_jit_comp_32.c` and `bpf_jit_asm_32.S`; integrates with `sk_buff`, classic BPF ancillary loads, and SPARC calling conventions.

Risks: changing register assignments breaks generated code and helper stubs together. The saved `%o7` convention is required because helper calls are made without a normal windowed function prologue.

Test signals: classic BPF filters with direct packet loads, negative ancillary offsets, helper calls, and return paths should pass on sparc32 with JIT enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_64.h

Purpose: provides SPARC64 register-number constants used by the eBPF JIT emitter.

Important APIs/types/functions: defines general, out, local, in, stack, frame, and link register numbers (`G0`-`G7`, `O0`-`O7`, `L0`-`L7`, `I0`-`I7`, `SP`, `FP`) for non-assembly code.

Control flow: no executable logic. `bpf_jit_comp_64.c` uses these constants to encode SPARC64 instructions and map BPF virtual registers.

State and persistence: no runtime state.

Dependencies and integration points: included by the 64-bit BPF JIT compiler. It is tied to the SPARC V9 register file and instruction encoding macros in the compiler.

Risks: incorrect numeric register constants corrupt emitted instructions. Since the compiler uses callee-saved locals for BPF registers, ABI mistakes can leak values across helper calls or break tail calls.

Test signals: eBPF verifier/JIT selftests covering helper calls, stack access, tail calls, and register preservation on sparc64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_asm_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_asm_32.S

Purpose: implements SPARC32 helper stubs used by the classic BPF JIT for packet data loads from linear skb data, paged skb data, and negative ancillary offsets.

Important APIs/functions: exports `bpf_jit_load_word`, `bpf_jit_load_half`, `bpf_jit_load_byte`, `bpf_jit_load_byte_msh`, and specialized positive/negative-offset variants. Slow paths call `skb_copy_bits()` or `bpf_internal_load_pointer_neg_helper()`.

Control flow: positive-offset helpers compare requested offset against skb head length and do direct loads when the bytes are linear. Unaligned word/half paths assemble values byte-by-byte. Slow paths allocate a register window, call `skb_copy_bits()`, load the scratch result, and branch to `bpf_error` on failure. Negative-offset paths reject offsets below `SKF_LL_OFF`, ask the BPF helper for a pointer, then load from it. `bpf_error` returns zero through the saved `%o7`.

State and persistence: no owned state; uses stack scratch space during slow paths and returns values in the BPF accumulator or X register.

Dependencies and integration points: called by `bpf_jit_comp_32.c` generated code. Depends on the register ABI from `bpf_jit_32.h`, skb helpers, and SPARC delay-slot/register-window conventions.

Risks: bounds checks must exactly protect direct loads. Return-through-saved-link handling must match the JIT prologue. Endianness and unaligned load assembly must match classic BPF semantics.

Test signals: JIT classic BPF packet filters reading bytes/halfwords/words at aligned, unaligned, paged, out-of-range, negative, and MSH offsets; failures should return zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_asm_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_comp_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_comp_32.c

Purpose: compiles classic socket BPF filters into SPARC32 machine code.

Important APIs/functions: main entry points are `bpf_jit_compile()` and `bpf_jit_free()`. The file defines SPARC instruction encoders, branch helpers, load/store macros, ALU emitters, skb field loaders, and flags `SEEN_DATAREF`, `SEEN_XREG`, and `SEEN_MEM` that drive prologue/epilogue generation.

Control flow: compilation is multi-pass. An initial rough address table estimates every BPF instruction, then up to 10 passes emit code into a temporary buffer, update instruction end offsets, and converge on a stable length. Once stable, executable memory is allocated and the final pass copies instructions into it. The generated prologue allocates stack memory for BPF scratch, clears X/A when needed to avoid leaks, preloads skb head length/data, and saves `%o7`. Each classic BPF opcode emits SPARC ALU, branch, memory, ancillary load, or helper-call sequences. Returns jump to a cleanup epilogue when needed.

State and persistence: per-compile state includes `addrs`, emitted image, seen flags, cleanup address, and `pc_ret0` optimization. A successful compile stores `fp->bpf_func` and `fp->jited`; free releases execmem.

Dependencies and integration points: depends on classic BPF filter encoding, `bpf_anc_helper()`, skb layout, `execmem_alloc/free`, `bpf_jit_dump()`, `bpf_needs_clear_a()`, SPARC32 helper stubs, and network filter JIT hooks.

Risks: branch offset convergence, delay slots, `%y` register latency for division, and helper-call link handling are all subtle. The code must avoid kernel data leakage by clearing registers and returning zero on invalid loads.

Test signals: classic BPF JIT selftests, tcpdump/socket filters with ALU/jump/memory/ancillary loads, division by zero, out-of-range packet access, JIT dump validation, and execmem free on program teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_comp_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_comp_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_comp_64.c

Purpose: implements the SPARC64 eBPF JIT compiler, translating verifier-accepted BPF instructions into SPARC V9 machine code.

Important APIs/types/functions: key types are `struct jit_ctx` and `struct sparc64_jit_data`. Public hooks are `bpf_int_jit_compile()` and `bpf_jit_needs_zext()`. Important helpers include instruction emitters, 64-bit constant synthesis (`emit_loadimm64()` and analysis helpers), `emit_compare_and_branch()`, `build_prologue()`, `build_epilogue()`, `emit_tail_call()`, `build_insn()`, `build_body()`, `jit_fill_hole()`, and `bpf_flush_icache()`.

Control flow: the compiler allocates or resumes per-program JIT data, iterates until instruction offsets converge, allocates a BPF binary image, emits a final pass, checks size convergence, flushes I-cache on Spitfire, marks the image read-only, records line info, and sets `prog->bpf_func`. `build_insn()` covers ALU32/ALU64 operations, endian swaps, jumps with optional CBCOND, helper calls, tail calls, loads/stores, stack frame use, and atomic add via CAS/CASX.

State and persistence: compile state tracks offsets, image pointer, temporary register usage, frame-pointer/call/tail-call observations, and epilogue offset. Program state is updated in `prog->bpf_func`, `jited`, `jited_len`, and temporary `prog->aux->jit_data` for subprogram extra passes.

Dependencies and integration points: depends on the eBPF verifier contract, BPF binary allocator/locking, helper-call base, BPF array tail-call layout, SPARC64 HWCAP `AV_SPARC_CBCOND`, cacheflush/TLB type, and register constants from `bpf_jit_64.h`.

Risks: constant materialization and branch displacement selection are complex. Tail-call prologue skip must match emitted prologue length. Atomic loops, stack offsets, zero-extension semantics, and helper ABI register preservation are security-sensitive.

Test signals: upstream BPF JIT selftests, verifier zext tests, tail-call chains and limit handling, subprogram JIT passes, atomics, endian conversions, helper calls, stack access, CBCOND-capable and non-CBCOND CPUs, and W^X image locking failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_comp_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/power/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/power/Makefile

Purpose: adds SPARC hibernation objects to the build.

Important APIs/targets: when `CONFIG_HIBERNATION` is enabled, builds `hibernate.o` and `hibernate_asm.o`.

Control flow: kbuild conditionally includes the C state hooks and assembly suspend/resume paths.

State and persistence: no runtime state; affects build composition.

Dependencies and integration points: integrates SPARC64 hibernation support with the generic suspend/hibernate subsystem.

Risks: missing either object leaves unresolved architecture hibernation symbols or incomplete resume support.

Test signals: sparc64 builds with and without `CONFIG_HIBERNATION`, plus link checks for `swsusp_arch_suspend` and `swsusp_arch_resume`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/power/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/power/hibernate.c -->
# sources/distributed-fs/ceph-client/arch/sparc/power/hibernate.c

Purpose: supplies SPARC64 C hooks for hibernation state save/restore and nosave-page detection.

Important APIs/types/functions: defines global `struct saved_context saved_context`, `pfn_is_nosave()`, `save_processor_state()`, and `restore_processor_state()`.

Control flow: `pfn_is_nosave()` converts `__nosave_begin`/`__nosave_end` to PFNs and tests whether a page belongs to the nosave section. `save_processor_state()` saves and clears FPU/VIS state. `restore_processor_state()` reloads TSB context state for `current->active_mm` using hardware context bits after image restore.

State and persistence: `saved_context` is populated by assembly suspend code. FPU state is saved in task/thread state, and TSB hardware state is restored after resume. Hibernation image persistence is handled by generic swsusp, not this file.

Dependencies and integration points: depends on generic suspend, `__nosave_*` section markers, VIS/FPU save helpers, `tsb_context_switch_ctx()`, and `mm->context` encoding.

Risks: failing to exclude nosave pages can corrupt restore. Missing FPU clear/save or TSB reload can resume with stale CPU/MMU state.

Test signals: hibernate/resume on sparc64 with active FPU users, validate nosave PFN exclusion, run memory checks after resume, and exercise processes with populated TSBs across hibernation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/power/hibernate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/power/hibernate_asm.S -->
# sources/distributed-fs/ceph-client/arch/sparc/power/hibernate_asm.S

Purpose: implements SPARC64 low-level swsusp suspend and resume assembly paths.

Important APIs/functions: exports `swsusp_arch_suspend()` and `swsusp_arch_resume()`. Uses `saved_context` offsets for CWP, WSTATE, frame pointer, TICK, PSTATE, and selected global registers, and consumes `restore_pblist`.

Control flow: suspend saves register windows, current window state, tick/pstate, and global registers into `saved_context`, then calls `swsusp_save()` and unwinds two register windows. Resume flushes all TLBs, switches to physical ASI, walks the page backup list copying saved pages back to original physical addresses, restores saved register/window state, restores ASI, raises PIL, and returns zero.

State and persistence: writes CPU architectural state into `saved_context` and restores physical memory from the hibernation page list. No filesystem writes occur here.

Dependencies and integration points: depends on generic swsusp page lists, `__flush_tlb_all`, SPARC physical ASI operations, `asm-offsets.h`, and the C `saved_context` object.

Risks: the resume copy loop runs with special ASI/PIL settings and must use physical addresses correctly. Register-window restore ordering is critical. Wrong offsets corrupt CPU state after resume.

Test signals: hibernate/resume with register-window pressure, FPU/VIS users, memory checksum validation, TLB flush verification, and resume under different page-list lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/power/hibernate_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/Makefile

Purpose: defines the SPARC PROM library object set for 32-bit and 64-bit builds.

Important APIs/targets: always includes bitness-specific `bootstr`, `init`, `misc`, `console`, `printf`, and `tree` objects. SPARC32 adds `memory.o`, `mp.o`, and `ranges.o`; SPARC64 adds IEEE-1275 `p1275.o` and `cif.o`.

Control flow: kbuild selects implementation variants through `$(BITS)` and `CONFIG_SPARC32`/`CONFIG_SPARC64`.

State and persistence: no runtime state; controls which PROM library symbols are linked.

Dependencies and integration points: integrates early boot, device-tree access, console, PROM calls, and architecture setup code.

Risks: wrong bitness object selection breaks boot-time PROM access. Missing 64-bit CIF or 32-bit ROM vector support prevents early console and device-tree discovery.

Test signals: build sparc32 and sparc64 defconfigs, check PROM symbol resolution, early boot console output, and device-tree probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/bootstr_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/bootstr_32.c

Purpose: retrieves SPARC32 boot arguments from legacy Sun PROM interfaces.

Important APIs/functions: exposes `prom_getbootargs()`. Internal state is static `barg_buf[256]` and `fetched`.

Control flow: the first call gathers arguments based on `prom_vers`. PROM V0 concatenates `argv[1..7]` from the ROM vector with spaces, preserving buffer bounds. PROM V2/V3 copies the bootargs string from `pv_v2bootargs`. Later calls return the cached buffer to tolerate boot loader patches.

State and persistence: boot arguments are cached in a static buffer for the lifetime of boot. No external persistence.

Dependencies and integration points: depends on `romvec`, `prom_vers`, and early command-line setup. The result feeds generic kernel command-line parsing.

Risks: fixed 256-byte buffer can truncate long command lines. PROM V0 concatenation can leave a trailing space. Calling before `prom_init()` would dereference unset ROM state.

Test signals: boot PROM V0, V2, and V3 paths with empty, normal, and long arguments; verify command-line parsing and cached repeated calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/bootstr_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/bootstr_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/bootstr_64.c

Purpose: retrieves SPARC64 boot arguments from SILO-provided data or IEEE-1275 `/chosen` bootargs.

Important APIs/types/functions: defines `bootstr_info` containing `bootstr_len`, `bootstr_valid`, and a 1024-byte buffer, and exposes `prom_getbootargs()`.

Control flow: if `bootstr_valid` is already set, including via `CONFIG_CMDLINE` or bootloader-filled data, the cached buffer is returned. Otherwise the function reads `/chosen` property `bootargs` through `prom_getstring()`, marks the buffer valid, and returns it.

State and persistence: command line is cached in `bootstr_info`. Placement in `.data` is ABI-visible to the boot loader and must not move to `.bss`.

Dependencies and integration points: depends on `prom_chosen_node`, PROM property access, SILO bootloader expectations, and generic kernel command-line setup.

Risks: moving or reordering `bootstr_info` fields breaks bootloader patching. Long bootargs beyond 1024 bytes are truncated by design.

Test signals: boot with SILO-provided args, `CONFIG_CMDLINE`, and raw PROM `/chosen/bootargs`; verify repeated calls and command-line truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/bootstr_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/cif.S -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/cif.S

Purpose: provides SPARC64 assembly trampolines for calling IEEE-1275 Client Interface Firmware and handling PROM callbacks.

Important APIs/functions: exports `prom_cif_direct()` and `prom_cif_callback()`. Uses `p1275buf.prom_cif_handler` and `p1275buf.prom_callback`.

Control flow: `prom_cif_direct()` creates a register window, loads the CIF handler from `p1275buf`, preserves `%g4`-`%g6`, calls firmware with the argument array, restores globals, and returns. `prom_cif_callback()` reconstructs kernel thread/per-CPU globals, enters PROM world, calls the callback function pointer, exits PROM world, and returns the firmware callback result.

State and persistence: no owned memory state, but preserves/restores global registers and switches PROM/kernel world state.

Dependencies and integration points: used by `p1275.c`; depends on thread-info/per-CPU macros, PROM world switching, and the IEEE-1275 argument array convention.

Risks: global register preservation is critical because SPARC64 uses globals for kernel state. Callback path must reload thread/per-CPU bases before calling C code.

Test signals: early PROM calls, PROM callbacks, SMP boot with PROM access, and stress of PROM console/device-tree calls while interrupts and globals are sensitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/cif.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/console_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/console_32.c

Purpose: writes early console output through SPARC32 PROM services.

Important APIs/functions: exports `prom_console_write_buf()`. Internal helper `prom_nbputchar()` serializes a single-character write through PROM V0 or V2/V3 ROM vector operations.

Control flow: `prom_console_write_buf()` loops until all characters are accepted. `prom_nbputchar()` takes `prom_lock`, dispatches to the correct PROM write method, calls `restore_current()`, releases the lock, and reports success/failure.

State and persistence: no data persistence; output is sent to PROM stdout. Uses global PROM lock state.

Dependencies and integration points: called by `prom_write()`/`prom_printf()` for early printk. Depends on `romvec`, `prom_vers`, `prom_lock`, and `restore_current()`.

Risks: unsupported PROM versions can make the caller spin forever. PROM calls require locking and current-task restoration to avoid corrupting kernel state.

Test signals: early boot console on PROM V0/V2/V3, concurrent early printk paths, and failure behavior when PROM write returns no progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/console_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/console_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/console_64.c

Purpose: writes SPARC64 early console output through IEEE-1275 `write`.

Important APIs/functions: exports `prom_console_write_buf()`. Internal `__prom_console_write_buf()` builds a P1275 argument array for service `"write"` with `prom_stdout`, buffer, and length.

Control flow: the public writer repeatedly calls the direct PROM write until the requested length is consumed. The helper invokes `p1275_cmd_direct()` and treats negative firmware return as no progress.

State and persistence: no owned state; sends bytes to PROM stdout.

Dependencies and integration points: used by PROM printf/early console; depends on `prom_stdout` initialized by `prom_init()` and P1275 CIF support.

Risks: the loop must handle partial writes. The current code advances `buf` by the remaining length after subtracting `n`, which is a subtle area to test for multi-chunk writes. Firmware errors can spin.

Test signals: early boot output with short and long buffers, partial-write PROM behavior, and newline conversion through `prom_write()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/console_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/init_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/init_32.c

Purpose: initializes the SPARC32 PROM library from the ROM vector.

Important APIs/state/functions: exports `romvec` and `prom_root_node`; defines `prom_vers`, `prom_rev`, `prom_prev`, `prom_nodeops`, and `prom_init()`.

Control flow: `prom_init()` stores the ROM vector, decodes PROM major version, validates node operations and root node, initializes memory bank data and OBIO ranges, and logs the PROM version. Unsupported PROM versions or invalid essential pointers halt the machine.

State and persistence: global PROM library pointers and version fields persist for the boot lifetime. No filesystem persistence.

Dependencies and integration points: called during early SPARC32 boot before PROM library users. Integrates with `prom_meminit()`, `prom_ranges_init()`, early console, and device-tree traversal code.

Risks: root node and nodeops validation is fatal. Misclassifying PROM version sends later calls through the wrong ROM vector layout.

Test signals: boot PROM V0/V2/V3 systems, verify memory bank discovery, OBIO ranges, early console, and exported `romvec` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/init_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/init_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/init_64.c

Purpose: initializes the SPARC64 IEEE-1275 PROM library.

Important APIs/state/functions: defines `prom_version[80]`, `prom_stdout`, `prom_chosen_node`, `prom_init()`, and `prom_init_report()`.

Control flow: `prom_init()` installs the CIF handler, finds `/chosen`, reads stdout instance handle, finds `/openprom`, reads the firmware version string, and emits an initial PROM newline. `prom_init_report()` later logs the PROM version and root compatibility.

State and persistence: caches `/chosen`, stdout handle, and firmware version for boot lifetime.

Dependencies and integration points: depends on P1275 CIF initialization, PROM path constants, device-tree property access, early console, and root compatibility discovery elsewhere.

Risks: failure to find `/chosen` or `/openprom` halts the machine. `prom_stdout` must be valid before console writes.

Test signals: sparc64 boot on physical and sun4v firmware, early console output, `/chosen` stdout parsing, and report logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/init_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/memory.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/memory.c

Purpose: gathers SPARC32 physical memory availability from PROM and populates `sp_banks`.

Important APIs/functions: exposes `prom_meminit()`. Helpers are `prom_meminit_v0()`, `prom_meminit_v2()`, and `sp_banks_cmp()`.

Control flow: V0 walks the ROM vector available-memory linked list; V2/V3 finds the `memory` node and reads its `available` property into register entries. `prom_meminit()` sorts discovered banks by base address, writes a sentinel with zero size, and page-aligns bank sizes downward.

State and persistence: writes global boot-time `sp_banks` memory-bank array used by early MM setup. No persistent storage.

Dependencies and integration points: called by SPARC32 `prom_init()` before `srmmu_paging_init()` uses `sp_banks` to compute memory and create mappings.

Risks: fixed local register array limits parsed entries. Incorrect sorting or missing sentinel can make boot memory setup overrun or mis-map RAM. Page-size truncation discards unaligned tail bytes.

Test signals: boot PROM V0/V2/V3 with multiple banks, out-of-order banks, small unaligned bank tails, and no/invalid memory node behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/misc_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/misc_32.c

Purpose: provides SPARC32 miscellaneous PROM operations: reboot, Forth evaluation, entering PROM command line, halt, sync hook, IDPROM, and version queries.

Important APIs/functions: defines `prom_lock` and functions `prom_reboot()`, `prom_feval()`, `prom_cmdline()`, `prom_halt()`, `prom_setsync()`, `prom_get_idprom()`, `prom_version()`, `prom_getrev()`, and `prom_getprev()`.

Control flow: PROM entry points serialize with `prom_lock`, invoke the appropriate ROM vector operation, call `restore_current()`, and release the lock. Halt loops forever because firmware might return. IDPROM reads the root `idprom` property after checking length.

State and persistence: maintains only the global PROM spinlock. Reboot/halt/power state is delegated to firmware.

Dependencies and integration points: used by architecture restart/poweroff paths, early debug code, IDPROM consumers, and exported `prom_feval()`. Depends on ROM vector layout and PROM tree property helpers.

Risks: PROM calls can return unexpectedly or alter kernel register/current state. Locking with interrupts disabled is necessary, but misuse can deadlock if called from unsafe contexts.

Test signals: PROM command entry and resume, reboot/halt paths, Forth command execution, IDPROM reads with varying buffer sizes, and version query consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/misc_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/misc_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/misc_64.c

Purpose: provides SPARC64 miscellaneous IEEE-1275 PROM services for reboot/power, firmware command entry, MMU/memory methods, power management, CPU control, and diagnostic memory lookup.

Important APIs/functions: includes `prom_reboot()`, `prom_feval()`, `prom_cmdline()`, `prom_halt()`, `prom_halt_power_off()`, `prom_get_idprom()`, `prom_itlb_load()`, `prom_dtlb_load()`, `prom_map()`, `prom_unmap()`, `prom_retain()`, `prom_getunumber()`, sleep/wakeup calls, and SMP CPU start/stop/idle/resume helpers. Internal helpers cache MMU and memory ihandles.

Control flow: each service builds a P1275 argument array and calls `p1275_cmd_direct()`. LDOM builds may delegate reboot or poweroff to LDOM hypervisor paths. `prom_cmdline()` captures other CPUs and disables interrupts around PROM entry.

State and persistence: caches ihandles for MMU and memory package methods. Firmware calls can retain memory across soft reset or change platform power/CPU state.

Dependencies and integration points: integrates with restart/poweroff, early MMU mapping, CPU bring-up, sun4v soft state, LDOM services, ECC unumber reporting, and suspend/power-management code.

Risks: P1275 argument counts and return slots must match firmware methods. PROM entry under SMP requires capture/release. Firmware errors are often weakly typed and can leave cached handles invalid.

Test signals: reboot/poweroff on bare metal and LDOM, PROM enter/continue with SMP, TLB load/map/unmap calls during boot, retained memory allocation, CPU start/stop paths, and unumber lookup after memory errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/misc_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/mp.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/mp.c

Purpose: exposes SPARC32 PROM support for starting secondary CPUs on PROM V3 systems.

Important APIs/functions: defines `prom_startcpu(int cpunode, struct linux_prom_registers *ctable_reg, int ctx, char *pc)`.

Control flow: under `prom_lock`, the function checks `prom_vers`. PROM V3 calls `romvec->v3_cpustart()` with CPU node, context-table register, context number, and start PC. Other PROM versions return `-1`. `restore_current()` is called after firmware returns.

State and persistence: no owned state; starts firmware CPU execution state.

Dependencies and integration points: used by SPARC32 SMP boot code. Depends on PROM V3 ROM vector CPU-start method, context-table setup, and PROM locking.

Risks: wrong context-table or PC arguments prevent secondary CPU boot. Calling on unsupported PROM versions cannot work. Firmware may disturb current-task state unless restored.

Test signals: SMP boot on PROM V3 sun4m/sun4d, unsupported PROM fallback, and secondary CPU entry validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/mp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/p1275.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/p1275.c

Purpose: implements the low-level serialized SPARC64 IEEE-1275 PROM command path.

Important APIs/types/functions: defines `p1275buf` with callback and CIF handler fields, raw spinlock `prom_entry_lock`, `p1275_cmd_direct()`, and `prom_cif_init()`. Assembly entry points `prom_cif_direct()` and `prom_cif_callback()` are external.

Control flow: `prom_cif_init()` stores the firmware CIF handler. `p1275_cmd_direct()` saves interrupt flags, raises interrupt priority to NMI, takes the raw PROM entry lock, switches into PROM world, calls the assembly direct CIF trampoline, switches back to kernel world, releases the lock, and restores interrupt flags.

State and persistence: caches CIF handler and protects a single global PROM argument/call context. No disk persistence.

Dependencies and integration points: all SPARC64 PROM tree, console, reboot, MMU, and CPU service wrappers call through this file. Depends on `prom_world()` and SPARC interrupt priority semantics.

Risks: PROM firmware is not reentrant, so lock and interrupt handling are essential. Entering PROM with wrong world state or globals can corrupt kernel execution.

Test signals: concurrent PROM service callers during boot, early console, device-tree property scans, PROM callbacks, and SMP paths that need serialized firmware entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/p1275.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/printf.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/printf.c

Purpose: implements PROM-backed early formatted output for SPARC.

Important APIs/functions: exposes `prom_write()` and `prom_printf()`. Uses static buffers `ppbuf` and `console_write_buf`, protected by `console_write_lock`.

Control flow: `prom_printf()` formats into `ppbuf` with `vscnprintf()` and calls `prom_write()`. `prom_write()` serializes output, inserts carriage returns before newlines, batches up to 1024 bytes, and writes chunks through `prom_console_write_buf()`.

State and persistence: only static formatting/output buffers and a raw spinlock. Output is transient console I/O.

Dependencies and integration points: used by early boot, fatal PROM halt paths, and low-level diagnostics before normal console availability. Depends on bitness-specific PROM console writers.

Risks: fixed global buffers require serialization. Calling in tracing-sensitive contexts uses `notrace`. PROM output can be slow or blocking, so it should remain early/debug-only.

Test signals: early printk with `\n` conversion, long messages over buffer boundary, concurrent early messages, and use before normal console registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/printf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/ranges.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/ranges.c

Purpose: applies SPARC32 OpenPROM `ranges` translations to device register addresses, especially OBIO and nested bus ranges.

Important APIs/functions: exports `prom_apply_obio_ranges()` and `prom_apply_generic_ranges()`. Initialization entry is `prom_ranges_init()`. Internal helpers are `prom_adjust_regs()` and `prom_adjust_ranges()`.

Control flow: `prom_ranges_init()` finds the root `obio` node and caches its ranges. `prom_apply_obio_ranges()` translates register tuples through cached OBIO ranges. `prom_apply_generic_ranges()` reads a node's ranges, optionally composes them with parent ranges, and adjusts each register's bus space and physical address.

State and persistence: caches OBIO ranges and count in static arrays for boot lifetime.

Dependencies and integration points: called by SPARC32 PROM init and device probing code that consumes PROM `reg` properties for SBUS/OBIO devices.

Risks: range matching lacks hard failure after warning, so malformed firmware ranges can still index unexpected entries. Arithmetic overflow or wrong parent composition maps devices to incorrect physical addresses.

Test signals: probe OBIO/SBUS devices with simple and nested ranges, missing ranges, malformed ranges, and verify translated resource addresses match firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/ranges.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/tree_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/tree_32.c

Purpose: implements SPARC32 PROM device-tree traversal, property access, path lookup, property setting, and instance-to-package conversion through ROM vector node operations.

Important APIs/functions: exports `prom_getchild()`, `prom_getsibling()`, `prom_getproplen()`, `prom_getproperty()`, `prom_getint()`, `prom_getintdefault()`, `prom_getbool()`, `prom_getstring()`, `prom_searchsiblings()`, `prom_nextprop()`, `prom_finddevice()`, `prom_setprop()`, and `prom_inst2pkg()`.

Control flow: public node/property routines validate handles, take `prom_lock`, call the appropriate `prom_nodeops` or ROM vector function, call `restore_current()`, and normalize PROM `-1` handles to zero. `prom_finddevice()` parses path components and optional `@bus,addr` selectors, scanning siblings by name and matching `reg` properties.

State and persistence: uses a static 128-byte scratch buffer for sibling name search. PROM property changes through `prom_setprop()` persist in firmware-visible runtime state, not disk.

Dependencies and integration points: core dependency for SPARC32 boot, memory/ranges init, device discovery, IDPROM reads, and module users of PROM tree exports.

Risks: static buffer and path parser assume small node names. PROM calls are serialized but can be slow. `prom_nextprop()` ignores its output buffer argument and returns firmware storage, so callers must match historical expectations.

Test signals: traverse root/child/sibling trees, read integer/string/bool properties, find devices with and without unit addresses, set properties, convert instances, and handle invalid nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/tree_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/tree_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/prom/tree_64.c

Purpose: implements SPARC64 IEEE-1275 device-tree traversal, property access, property enumeration, path lookup, property setting, and ihandle conversion.

Important APIs/functions: exports `prom_getchild()`, `prom_getparent()`, `prom_getsibling()`, `prom_getproplen()`, `prom_getproperty()`, `prom_getint()`, `prom_getintdefault()`, `prom_getbool()`, `prom_getstring()`, `prom_nodematch()`, `prom_searchsiblings()`, `prom_firstprop()`, `prom_nextprop()`, `prom_finddevice()`, `prom_node_has_property()`, `prom_setprop()`, `prom_inst2pkg()`, and `prom_ihandle2path()`.

Control flow: traversal wrappers build P1275 argument arrays for `child`, `parent`, and peer services. Property routines preflight lengths, call `getprop` or `nextprop`, and normalize `-1` handles. `prom_setprop()` delegates to LDOM variable setting when domaining is enabled; otherwise it calls P1275 `setprop`.

State and persistence: no owned tree copy; every operation queries firmware. Property writes can change firmware/LDOM runtime variables.

Dependencies and integration points: all SPARC64 boot and device discovery code depends on these wrappers. Integrates with LDOM services, `p1275_cmd_direct()`, and Open Firmware naming conventions.

Risks: P1275 argument slots are ABI-sensitive. `prom_nextprop()` must copy `oprop` when input and output buffers alias. LDOM setprop behavior intentionally bypasses firmware.

Test signals: enumerate properties, find devices, get/set properties under LDOM and non-LDOM, invalid handle handling, ihandle-to-path conversion, and sibling traversal across large firmware trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/prom/tree_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/Makefile

Purpose: builds SPARC vDSO shared objects, converts them into kernel-embedded images, and builds vDSO VMA setup code.

Important APIs/targets: builds `vma.o`, `vdso-image-64.o` for `CONFIG_SPARC64`, and `vdso-image-32.o` for compat. Links `vdso64.so.dbg` and `vdso32.so.dbg`, strips `.so` files, and runs host tool `vdso2c`.

Control flow: kbuild compiles vDSO objects with PIC, no stack protector, no branch profiling, frame pointers kept, and SPARC register flags filtered out. It links with `vdso.lds` or `vdso32.lds`, validates through generic vDSO checks, strips, then embeds via generated C.

State and persistence: build-time only; generated images are compiled into the kernel.

Dependencies and integration points: depends on generic `lib/vdso/Makefile.include`, host `vdso2c`, SPARC linker emulations, compat toolchain flags, and vDSO source/linker scripts.

Risks: vDSO must be relocation-free and use correct page size/ELF ABI. Toolchain flags are delicate because vDSO runs in userspace but is built inside the kernel tree.

Test signals: sparc64 and compat builds, `readelf` checks for no relocations and expected symbols, vDSO selftests for `clock_gettime`, `gettimeofday`, and mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vclock_gettime.c -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vclock_gettime.c

Purpose: provides SPARC vDSO user-visible fast time functions by wrapping the generic vDSO gettimeofday implementation.

Important APIs/functions: defines `__vdso_gettimeofday()` and weak alias `gettimeofday()`. For 64-bit builds it defines `__vdso_clock_gettime()` and `clock_gettime()` using `__kernel_timespec`; for 32-bit builds it also defines 32-bit `clock_gettime()` and time64 `__vdso_clock_gettime64()`.

Control flow: each exported function delegates directly to `__cvdso_gettimeofday()`, `__cvdso_clock_gettime()`, or `__cvdso_clock_gettime32()`. The file includes `lib/vdso/gettimeofday.c` into the vDSO object.

State and persistence: reads kernel-provided vvar/vdso data pages through generic vDSO code; owns no persistent state.

Dependencies and integration points: depends on `vdso/gettime.h`, SPARC `asm/vdso/gettimeofday.h`, vvar mapping, and symbol version scripts.

Risks: vDSO code must have no unresolved relocations and cannot rely on kernel-only instrumentation. 32-bit/time64 ABI symbol selection must match userspace expectations.

Test signals: vDSO `clock_gettime`, `clock_gettime64`, `gettimeofday`, and `time` tests on 64-bit and compat tasks; compare against syscall fallback under clocksource changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vclock_gettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso-layout.lds.S -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso-layout.lds.S

Purpose: defines the common ELF section and program-header layout for SPARC vDSO images.

Important APIs/sections: emits vvar symbols with `VDSO_VVAR_SYMS`, then lays out hash, dynamic symbol/string/version sections, dynamic table, read-only data, notes, unwind frames, and text. Defines PHDRs for one read/execute `PT_LOAD`, read-only `PT_DYNAMIC`, `PT_NOTE`, and GNU EH frame header.

Control flow: this is a linker script include used by both 64-bit and 32-bit vDSO scripts. It discards bug/discard sections and fills text padding with `0x90909090`.

State and persistence: build-time layout only; controls in-memory vDSO segment shape.

Dependencies and integration points: included by `vdso.lds.S` and `vdso32.lds.S`; depends on vDSO datapage/page headers and SPARC vvar/vsyscall constants.

Risks: vDSO requires a single load segment with no dangling non-allocatable runtime content. Wrong PHDR flags, page size, or vvar placement breaks mapping or userspace dynamic tools.

Test signals: `readelf -lS` should show one PT_LOAD, read-only data/text layout, notes/build-id, unwind sections, exported vvar symbols, and no unexpected writable segment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso-layout.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso-note.S -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso-note.S

Purpose: adds a Linux version note to the SPARC vDSO.

Important APIs/sections: uses `ELFNOTE_START(Linux, 0, "a")`, emits `LINUX_VERSION_CODE`, and closes with `ELFNOTE_END`.

Control flow: assembled into the vDSO so the linker script places it in the PT_NOTE segment.

State and persistence: no runtime state; embeds build-time kernel version metadata into the vDSO image.

Dependencies and integration points: included in the vDSO object list from the Makefile and consumed by userspace/debug tools inspecting PT_NOTE.

Risks: note formatting must match ELF note expectations. Missing notes can affect tooling that identifies the in-memory vDSO.

Test signals: inspect built `vdso64.so.dbg` notes with `readelf -n` and confirm Linux version note is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso-note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso.lds.S -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso.lds.S

Purpose: defines the SPARC64 vDSO linker/version script.

Important APIs/sections: sets `BUILD_VDSO64`, includes the common layout script, and exports version `LINUX_2.6` symbols `clock_gettime`, `__vdso_clock_gettime`, `gettimeofday`, and `__vdso_gettimeofday`; all other symbols are local.

Control flow: used by the Makefile as the linker script for `vdso64.so.dbg`.

State and persistence: build-time symbol versioning only.

Dependencies and integration points: depends on `vdso-layout.lds.S` and function names emitted by `vclock_gettime.c`. Userland dynamic linkers resolve these symbols through the mapped vDSO.

Risks: missing or extra global symbols are ABI changes. Symbol names must match libc probing conventions.

Test signals: `readelf --dyn-syms --version-info` on the 64-bit vDSO should show only the intended `LINUX_2.6` globals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso2c.c -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso2c.c

Purpose: host tool that converts stripped/unstripped SPARC vDSO ELF files into either raw output or a kernel C `vdso_image` object.

Important APIs/functions: main flow is `main()`, `map_input()`, `go()`, and `fail()`. It includes `vdso2c.h` twice to generate `go64()` and `go32()`. Big-endian `GET_BE`/`PUT_BE` helper macros read ELF fields.

Control flow: the tool maps raw and stripped input files, derives an output object name from the output filename unless writing a `.so`, dispatches by ELF class, and lets the bitness-specific generated function validate and emit data. `fail()` unlinks partial output and exits.

State and persistence: writes the requested output file at build time. No kernel runtime state.

Dependencies and integration points: run by the vDSO Makefile after linking/stripping. Depends on Linux ELF headers, tools big-endian byte helpers, mmap, and the validation/emission logic in `vdso2c.h`.

Risks: SPARC vDSO is big-endian, so unaligned BE field reads must be correct. Output naming controls generated C symbol names. Validation failures should remove partial outputs.

Test signals: build both 32-bit and 64-bit vDSO images, run usage/error paths, feed malformed ELF with missing PT_LOAD/relocations, and inspect generated C object names/data alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso2c.h -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso2c.h

Purpose: template included by `vdso2c.c` to generate 32-bit and 64-bit ELF validation and C image emission logic.

Important APIs/functions: defines bitness-specific `go32()`/`go64()` through `BITSFUNC(go)`. It walks program headers, dynamic table, and section headers, validates a single load segment and no dynamic relocations, finds the symbol table, optionally writes raw stripped output, or emits a `struct vdso_image` C definition with aligned `raw_data`.

Control flow: it checks exactly one `PT_LOAD` at file offset and virtual address zero with equal file/memory size, records `PT_DYNAMIC`, rejects nonzero relocation sizes, requires `SHT_SYMTAB`, rounds stripped length to 8192-byte mapping size, and prints generated C.

State and persistence: writes build artifacts only. Generated `raw_data` is `__ro_after_init` and 8192-byte aligned for runtime mapping.

Dependencies and integration points: relies on `ELF_BITS`, `GET_BE`, `fail()`, and output stream state from `vdso2c.c`; produced C is consumed by `vma.c`.

Risks: validation protects runtime vDSO from unsupported relocation/layout shapes. Mapping-size rounding must match SPARC vDSO page size. Omitted dynamic symbols are intentional but section table presence is for debugger compatibility.

Test signals: run on valid 32/64 vDSOs, check generated `vdso_image` size/alignment, and confirm malformed ELF cases fail with clear errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vclock_gettime.c -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vclock_gettime.c

Purpose: builds the 32-bit SPARC vDSO time implementation, including compat 32-bit vDSO on a 64-bit kernel.

Important APIs/macros: defines `BUILD_VDSO32`; under `CONFIG_SPARC64` it undefines 64-bit config macros, defines `BUILD_VDSO32_64` and `CONFIG_32BIT`, and disables queued lock config macros before including `../vclock_gettime.c`.

Control flow: no independent functions; inclusion reuses the common vclock source under a faked 32-bit compile environment.

State and persistence: no owned state; generated symbols come from the included common file.

Dependencies and integration points: used by the vDSO Makefile for `vdso32.so.dbg`, depends on generic vDSO time code and compat ABI expectations.

Risks: macro environment must not leak incompatible 64-bit assumptions into 32-bit userspace code. Symbol set must include both legacy and time64 clock entry points.

Test signals: compat tasks calling `clock_gettime`, `clock_gettime64`, and `gettimeofday`; build with `CONFIG_COMPAT`; inspect 32-bit ELF class and symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vclock_gettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vdso-note.S -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vdso-note.S

Purpose: adds a Linux version note to the SPARC32 vDSO image.

Important APIs/sections: emits an allocatable Linux ELF note containing `LINUX_VERSION_CODE`.

Control flow: assembled into the 32-bit vDSO and placed into PT_NOTE by the common layout script.

State and persistence: build-time metadata only.

Dependencies and integration points: included by the vDSO32 link target and used by userspace/debug tooling.

Risks: malformed notes can confuse tools that identify/debug the in-memory vDSO.

Test signals: inspect `vdso32.so.dbg` with `readelf -n` and verify the Linux note exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vdso-note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vdso32.lds.S -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vdso32.lds.S

Purpose: defines the SPARC32 vDSO linker/version script.

Important APIs/sections: sets `BUILD_VDSO32`, includes the common layout, and exports `clock_gettime`, `__vdso_clock_gettime`, `clock_gettime64`, `__vdso_clock_gettime64`, `gettimeofday`, and `__vdso_gettimeofday` in version `LINUX_2.6`.

Control flow: used by the Makefile when linking `vdso32.so.dbg`.

State and persistence: build-time symbol ABI only.

Dependencies and integration points: depends on symbols emitted by the 32-bit vclock source and dynamic linker/libc vDSO probing.

Risks: omitting `clock_gettime64` would break modern 32-bit time64 users. Extra globals would expand ABI unintentionally.

Test signals: `readelf --dyn-syms --version-info` on the 32-bit vDSO and compat time syscall/vDSO selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vdso32.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vma.c -->
# sources/distributed-fs/ceph-client/arch/sparc/vdso/vma.c

Purpose: allocates, initializes, and maps SPARC vDSO and vvar pages into user processes.

Important APIs/functions/state: defines `vdso_enabled`, special mappings `vdso_mapping64` and `vdso_mapping32`, initcall `init_vdso()`, `init_vdso_image()`, `map_vdso()`, `arch_setup_additional_pages()`, and boot option parser `vdso_setup()`.

Control flow: `init_vdso()` copies built-in vDSO image bytes into freshly allocated pages and attaches them to special mappings. On exec, `arch_setup_additional_pages()` selects 64-bit or compat image, finds an unmapped area, optionally randomizes it, installs executable `[vdso]` text mapping after the vvar pages, maps vvar with `vdso_install_vvar_mapping()`, and records `mm->context.vdso`.

State and persistence: vDSO page arrays persist after init. Per-mm `context.vdso` records the user address. `vdso_enabled` is boot-option mutable.

Dependencies and integration points: depends on generated `vdso_image_*_builtin`, special mapping APIs, mmap locking, ASLR, vvar datapage constants, compat task detection, and ELF exec setup.

Risks: allocation failures disable vDSO globally. Mapping order and size must match vvar/vDSO page constants. Partial mapping failure must unmap text and clear `mm->context.vdso`.

Test signals: process exec with ASLR on/off, `vdso=0`, 64-bit and compat tasks, `/proc/<pid>/maps` `[vdso]` and vvar placement, GDB breakpoint COW behavior, and vDSO time selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/vdso/vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/video/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/video/Makefile

Purpose: builds common SPARC video helper code.

Important APIs/targets: unconditionally adds `video-common.o` to `obj-y`.

Control flow: kbuild compiles the helper into the architecture video support.

State and persistence: no runtime state in this file.

Dependencies and integration points: integrates the primary-console device helper with SPARC video/framebuffer drivers.

Risks: omitting the object prevents drivers from resolving `video_is_primary_device()`.

Test signals: SPARC builds with framebuffer/video drivers and link checks for exported video helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/video/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/video/video-common.c -->
# sources/distributed-fs/ceph-client/arch/sparc/video/video-common.c

Purpose: identifies whether a SPARC video device is the firmware-selected primary console device.

Important APIs/functions: exports `video_is_primary_device(struct device *dev)`.

Control flow: if the user set console explicitly on the command line, the function returns false. Otherwise it compares the device's OF node with global `of_console_device` and returns true on a match.

State and persistence: no owned state; reads `console_set_on_cmdline` and `of_console_device`.

Dependencies and integration points: used by SPARC framebuffer/video drivers to decide primary device behavior. Depends on Open Firmware device nodes and console core state.

Risks: incorrect primary detection can select the wrong framebuffer as console or override an explicit user console choice.

Test signals: boot with and without `console=`, multiple framebuffer devices, firmware console node matching, and module users of the exported symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/video/video-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Kbuild -->
# sources/distributed-fs/ceph-client/arch/um/Kbuild

Purpose: top-level Kbuild fragment for User-Mode Linux architecture subdirectories.

Important APIs/targets: adds `kernel/`, `drivers/`, and `os-Linux/` to `obj-y`.

Control flow: kbuild descends into those UML subdirectories when building the architecture.

State and persistence: no runtime state.

Dependencies and integration points: integrates UML architecture core, drivers, and Linux-host OS support into the build.

Risks: removing or renaming a subdirectory entry drops large parts of UML from the build or causes unresolved symbols.

Test signals: UML `ARCH=um` build, link of kernel/driver/os-Linux objects, and booting a UML kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Kbuild -->
