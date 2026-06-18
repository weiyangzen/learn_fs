# subset-b-000677 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-prot.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-prot.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-prot.h` Defines arm64 page-protection bit layouts and canonical pgprot values for kernel, user, stage-2, PIE, POE, GCS, BTI, LPA2, realm shared memory, userfaultfd write-protect, dirty/write tracking, device memory, normal memory, tagged memory, and execute-only mappings. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
PTE_WRITE/PTE_DIRTY/PTE_SPECIAL/PTE_PRESENT_INVALID, PROT_* and _PAGE_* constants, PAGE_* pgprot macros, PAGE_S2_MEMATTR(), PTE_MAYBE_NG, PTE_MAYBE_SHARED, PHYS_MASK_SHIFT/PHYS_MASK, PTE_MAYBE_GP, pte_pi_index(), PIE_E0, PIE_E1, _PAGE_GCS, _PAGE_GCS_RO. The file is 191 lines / 8497 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Most behavior is compile-time constant composition, with small runtime conditionals for LPA2, BTI, non-global mappings, and CCA realm shared mappings. Callers receive pgprot_t encodings that are later consumed by pgtable.h setters and TLB/cache maintenance paths.

### State, Persistence, And Dependencies
No owned storage except extern policy variables arm64_use_ng_mappings and prot_ns_shared; state persists in page-table entries, MAIR/PIR/POR interpretation, and CPU feature decisions. Depends on memory.h, pgtable-hwdef.h, cpufeature.h, pgtable-types.h, rsi.h, sysreg PIE/POE encodings; integrates with core-mm mmap/mprotect, KVM stage-2, MTE, BTI, GCS, and Arm CCA realm code.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong bit masks can corrupt permissions, expose executable or writable mappings, break LPA2 physical addressing, or make present-invalid/PROT_NONE entries visible to hardware incorrectly.

### Test Signals
Build 4K/16K/64K, LPA2, BTI, MTE, GCS, userfaultfd, and CCA configs; run page-table permission, mprotect, ptdump, KVM stage-2, and LKDTM W^X checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-prot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-types.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-types.h` Provides the typed arm64 page-table descriptor wrappers used by generic and architecture MM code. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
ptdesc_t, pteval_t, pmdval_t, pudval_t, p4dval_t, pgdval_t; typed structs pte_t/pmd_t/pud_t/p4d_t/pgd_t/pgprot_t; value and constructor macros pte_val/__pte, pmd_val/__pmd, pud_val/__pud, p4d_val/__p4d, pgd_val/__pgd, pgprot_val/__pgprot; generic folded-level includes. The file is 69 lines / 1632 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
There is no runtime control flow. Preprocessor branches include nopmd/nopud/nop4d generic layers according to CONFIG_PGTABLE_LEVELS.

### State, Persistence, And Dependencies
No runtime state. The file establishes compile-time type safety for 64-bit descriptors and folded page-table levels. Depends on asm/types.h and asm-generic folded page-table headers; consumed by pgtable-prot.h, pgtable.h, KVM, ptdump, and generic pgtable helpers.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Changing wrapper layout or folding selection breaks ABI expectations of inline helpers, assembly offsets, and generic MM type checking.

### Test Signals
Compile all CONFIG_PGTABLE_LEVELS combinations and sparse/type-check users of pte/pmd/pud/p4d/pgd values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable.h` Implements the arm64 core page-table API: PTE/PMD/PUD/PGD construction, permission mutation, page-table walking, lazy MMU barriers, MTE tag/cache synchronization, swap encoding, runtime page-table level folding, and contiguous-PTE management. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
VMALLOC_START/END, emit_pte_barriers(), arch_flush_lazy_mmu_mode(), pte_* predicates and mutators, por_el0_allows_pkey(), __set_ptes_anysz(), pgprot_* modifiers, pmd/pud/p4d/pgd offset/fixmap helpers, pte_modify(), ptep_set_access_flags(), ptep_get_and_clear(), wrprotect_ptes(), swap-entry macros, update_mmu_cache_range(), contpte_* wrappers. The file is 1954 lines / 58033 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Setters write entries with WRITE_ONCE/xchg/cmpxchg, run page_table_check, synchronize I-cache/D-cache and MTE tags for user executable/tagged mappings, then queue or emit DSB/ISB barriers. Page-table walking chooses folded or real levels at runtime for LPA2/VA52. Contiguous PTE paths unfold before modifying a contig range and refold when a range becomes aligned and eligible.

### State, Persistence, And Dependencies
Owns no persistent storage but mutates page tables, TIF_LAZY_MMU_PENDING, hardware access/dirty state, MTE tag side effects, and swap/MTE metadata. Extern page directories include swapper_pg_dir, idmap_pg_dir, tramp_pg_dir, reserved_pg_dir. Depends on bug.h, proc-fns.h, memory.h, mte.h, pgtable-hwdef.h, pgtable-prot.h, tlbflush.h, cmpxchg.h, fixmap.h, por.h, mmdebug, mm_types, sched, page_table_check; integrates directly with Linux core-mm, fork/COW, mprotect, fault handling, THP, hugetlb, swap, KVM, perf page-size reporting, and Ceph indirectly through page cache and network memory correctness.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Most risks are ordering and concurrency bugs: missing DSB/ISB can leave walkers using stale entries, unsafe valid-to-valid changes can race hardware AF/DBM updates, wrong contpte unfolding can corrupt adjacent entries, and pkey/POR/MTE handling can expose or lose access rights.

### Test Signals
Run arm64 mm selftests, mprotect/userfaultfd/THP/hugetlb/swap/MTE tests, page_table_check, KASAN/KMSAN configs, fork/COW stress, LKDTM W^X, ptdump, and TLB/cache coherency stress on 4K/16K/64K and LPA2/VA52 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pkeys.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pkeys.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pkeys.h` Implements arm64 protection-key integration for Permission Overlay Extension using VMA flags and mm context allocation state. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
ARCH_VM_PKEY_FLAGS, arch_max_pkey(), arch_set_user_pkey_access(), arch_pkeys_enabled(), vma_pkey(), arch_override_mprotect_pkey(), execute_only_pkey(), mm_pkey_allocation_map(), mm_set_pkey_allocated/free(), mm_pkey_is_allocated(), mm_pkey_alloc(), mm_pkey_free(). The file is 105 lines / 2389 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Allocation checks FEAT_POE availability, verifies the 3-bit key range is not exhausted, finds a free bit with ffz(), and updates mm->context.pkey_allocation_map. mprotect preserves the existing VMA pkey unless an explicit key is supplied.

### State, Persistence, And Dependencies
Persistent state is per-mm pkey_allocation_map and per-thread POR_EL0 access programmed elsewhere. The header itself has no storage. Depends on VM_PKEY flags, mm_struct context, system_supports_poe(), errno, bitops; consumed by generic pkey syscalls, mprotect, pgtable permission checks, and POR helpers.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Allocator trust is central: returning an invalid key would poison later PTE/POR checks; missing POE gating could expose unsupported ABI paths; freeing pkey 0 or out-of-range keys must stay rejected.

### Test Signals
Run pkey_alloc/free/mprotect selftests under POE-capable configs, compat and non-compat builds, and page-fault tests that validate read/write/exec denial through POR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pkeys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pointer_auth.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pointer_auth.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pointer_auth.h` Defines pointer-authentication key structures, masks, install/init helpers, and prctl integration for user and optional kernel PAC keys. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
ptrauth_user_pac_mask(), ptrauth_kernel_pac_mask(), PR_PAC_ENABLED_KEYS_MASK, struct ptrauth_key, struct ptrauth_keys_user, struct ptrauth_keys_kernel, __ptrauth_key_install_nosync(), ptrauth_keys_init/install/switch_user/kernel(), ptrauth_enable(), ptrauth_prctl_reset_keys(), ptrauth_set/get_enabled_keys(), thread init/switch macros. The file is 153 lines / 4789 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
When enabled, fork inherits process keys while exec initializes fresh random keys; context switch installs user keys and optional kernel APIA key, then ISB synchronizes. ptrauth_enable sets SCTLR_EL1 ENIA/ENIB/ENDA/ENDB when hardware supports address auth.

### State, Persistence, And Dependencies
Persistent state lives in thread_struct keys_user and optional keys_kernel, plus SCTLR/sysreg key registers. Disabled configs collapse to no-ops or -EINVAL. Depends on random, prctl, cpufeature, memory, sysreg, task/thread_struct; integrates with processor.h prctl macros, stackprotector boot init, suspend exit, exec, fork, and context switch.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Key installation without ISB or wrong support gating can leave stale PAC keys active; mask calculations depend on VA size/TBI; randomization failures or disabled-key drift can weaken userspace control-flow protection.

### Test Signals
Build with/without ARM64_PTR_AUTH and ARM64_PTR_AUTH_KERNEL; run PAC prctl selftests, exec/fork key reset checks, context-switch stress, suspend/resume, and invalid-key ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pointer_auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/por.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/por.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/por.h` Provides tiny Permission Overlay Register helpers used by pkey/PTE access checks. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
POR_EL0_INIT, por_elx_allows_read(), por_elx_allows_write(), por_elx_allows_exec(). The file is 34 lines / 612 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Each helper extracts a 4-bit permission field for a pkey with POR_ELx_PERM_GET and tests the relevant R/W/X bit.

### State, Persistence, And Dependencies
No owned state; callers pass a POR register value read from hardware or initialized for a thread. Depends on sysreg POE encodings; integrated by pgtable.h access checks and pkey initialization paths.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Incorrect bit extraction or init permissions could silently allow or deny user memory access.

### Test Signals
Unit-style compile tests for all pkeys, POE selftests for read/write/exec faults, and regression checks around POR_EL0_INIT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/por.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/preempt.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/preempt.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/preempt.h` Defines arm64 preemption-count storage semantics using thread_info fields and a separate need_resched bit encoded in the 64-bit preempt_count word. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
PREEMPT_NEED_RESCHED, PREEMPT_ENABLED, preempt_count(), preempt_count_set(), init_task_preempt_count(), init_idle_preempt_count(), set/clear/test_preempt_need_resched(), __preempt_count_add/sub(), __preempt_count_dec_and_test(), should_resched(), preempt_schedule(), dynamic_preempt_schedule(). The file is 102 lines / 2685 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Fast paths read/write current_thread_info()->preempt fields with READ_ONCE/WRITE_ONCE. decrement-and-test updates count only, then rechecks the full word to catch interrupt-side need_resched changes between non-atomic operations.

### State, Persistence, And Dependencies
State is per-task thread_info preempt_count/need_resched. No persistence outside task lifetime. Depends on linux/thread_info.h and scheduler preemption core; used by interrupt, softirq, scheduler, and low-level entry/exit code.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Non-atomic split-field updates are subtle; endian layout must match assembly; incorrect need_resched polarity can break scheduling or preempt in unsafe regions.

### Test Signals
Run PREEMPT, PREEMPT_DYNAMIC, lockdep, scheduler stress, irq/preempt tracing, and big-endian build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/preempt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/probes.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/probes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/probes.h` Defines the arm64 kprobes instruction handler contract and per-probe architecture storage. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
probes_handler_t, struct arch_probe_insn, kprobe_opcode_t, struct arch_specific_insn with api, xol_insn, xol_restore. The file is 27 lines / 549 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Runtime flow is implemented by kprobes: decode an opcode, choose a handler, run out-of-line instruction slots, then restore execution address.

### State, Persistence, And Dependencies
State is per registered kprobe instruction, especially xol_insn and xol_restore. No independent persistence. Depends on asm/insn.h and pt_regs users; integrates with kprobes, uprobes-like decoding, exception stepping, and tracing.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong opcode endianness or restore address corrupts probed control flow; handler prototype drift breaks kprobe dispatch.

### Test Signals
Run kprobes selftests, single-step probes, probes in exception-sensitive code, and CONFIG_KPROBES off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/probes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/proc-fns.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/proc-fns.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/proc-fns.h` Declares low-level CPU idle, suspend, and resume assembly entry points. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct cpu_suspend_ctx forward declaration, cpu_do_idle(), cpu_do_suspend(), cpu_do_resume(). The file is 25 lines / 564 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Callers enter assembly routines to idle the CPU or save/restore CPU context around suspend/resume; this header only declares the ABI.

### State, Persistence, And Dependencies
State is CPU register/context memory passed by pointer and idmap TTBR values. The header itself owns no storage. Depends on asm/page.h and memory.h; used by cpuidle, PSCI/suspend, hibernation, and early MMU/idmap code.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Prototype mismatch with proc.S corrupts saved state or resume address; incorrect idmap TTBR use can fail resume before normal mappings exist.

### Test Signals
Suspend/resume, CPU hotplug, hibernation, and cross-build checks against assembly symbol prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/proc-fns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/processor.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/processor.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/processor.h` Defines arm64 task address limits, thread CPU state, vector state metadata, TLS helpers, process start helpers, prefetch primitives, and prctl hooks for SVE/SME/PAC/MTE/tagged-address controls. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
TASK_SIZE*, STACK_TOP*, struct cpu_context, struct thread_struct, debug_info, vec_type/fp_type enums, thread/task vector-length helpers, arch_thread_struct_whitelist(), task_user_tls(), start_thread_common(), start_thread(), compat_start_thread(), is_ttbr0_addr(), cpu_switch_to(), task_pt_regs(), prefetch()/prefetchw(), SVE/SME/PAC/TAGGED_ADDR prctl macros. The file is 446 lines / 12743 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
exec/start_thread clears user GPR state, initializes PC/PSTATE/SP, preserves syscallno for tracepoints, sets interrupt priority mask, and validates final stack frame metadata. Vector helpers choose SVE versus SME based on SVCR. Address-limit macros switch between 32-bit compat and 64-bit VA windows.

### State, Persistence, And Dependencies
Persistent per-task state is thread_struct: CPU context, FPSIMD/SVE/SME, TLS, debug registers, PAC keys, MTE control, SCTLR user bits, POR_EL0, GCS state, and fault metadata. Depends on build_bug, cache, string, thread_info, vdso, alternative, cpufeature, hw_breakpoint, kasan, lse, pgtable-hwdef, pointer_auth, ptrace, spectre, fpsimd; integrates with exec, fork, context switch, ptrace, signal, scheduler, perf, MTE/PAC/SVE/SME/GCS, and mmap layout.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
thread_struct layout is ABI-sensitive for hardened usercopy and assembly; wrong compat TASK_SIZE/STACK_TOP can expose invalid userspace; start_thread mistakes can leak registers or break tracepoints; vector/PAC state drift breaks context switch isolation.

### Test Signals
Run exec/ptrace/signal/fork tests, compat 32-bit tests, SVE/SME/MTE/PAC prctl suites, hardened usercopy, context-switch stress, and mmap layout tests across VA_BITS configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptdump.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptdump.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptdump.h` Defines page-table dumping state and callbacks for arm64 debugfs/kernel page-table inspection. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
arm64_ptdump_lock_key, struct addr_marker, ptdump_info, ptdump_prot_bits, ptdump_pg_level, ptdump_pg_state, ptdump_walk(), note_page*(), note_page_flush(), ptdump_debugfs_register(), EFI_RUNTIME_MAP_END. The file is 89 lines / 2846 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
When CONFIG_PTDUMP is enabled, walkers call note_page* callbacks per level; pg_state groups contiguous entries with identical protection and flushes the accumulated range when attributes or markers change. Disabled configs provide empty inline callbacks.

### State, Persistence, And Dependencies
State is temporary walk state in ptdump_pg_state, including current protection, range start, marker, W^X counts, and seq_file output. Debugfs registration persists only if configured. Depends on linux/ptdump.h, mm_types, seq_file, pgtable types; integrates with debugfs, kernel page-table walkers, W^X validation, and EFI runtime map display.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Incorrect grouping or level masks can hide W^X mappings or misreport page sizes; debugfs locking must avoid concurrent page-table mutation races.

### Test Signals
Enable CONFIG_PTDUMP/PTDUMP_DEBUGFS, compare dump output to known mappings, run W^X checks, and build disabled configs to validate stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptdump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptrace.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptrace.h` Defines arm64 exception register layout, processor-state constants, compat ptrace mappings, syscall sentinel state, and register accessor helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
CurrentEL_* and INIT_PSTATE_* constants, AArch32 PSR bits, NO_SYSCALL, struct pt_regs, in_syscall(), forget_syscall(), user/compat mode predicates, regs_irqs_disabled(), user_stack_pointer(), regs_get_register(), pt_regs_read/write_reg(), regs_return_value(), regs_get_kernel_argument(), valid_user_regs(), instruction_pointer(), frame_pointer(), profile_pc(). The file is 365 lines / 9532 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Exception entry stores user_pt_regs as the prefix of pt_regs plus orig_x0, syscallno, PMR, SDEI TTBR, and stackframe metadata. Accessors decode offsets, sign-extend compat returns, and hide architectural register 31 as XZR for instruction emulation.

### State, Persistence, And Dependencies
State is per-exception stack pt_regs. It persists only while handling a trap/syscall/signal/ptrace stop but is user-visible through ptrace and signal frames. Depends on cpufeature, uapi ptrace, GIC priority definitions, stacktrace frame metadata, bug/types; integrates with syscall tracing, audit, seccomp, signal delivery, ptrace, kprobes, traps, stack unwinding, and scheduler register display.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
pt_regs layout is ABI and assembly critical; wrong compat PSR conversion or return sign-extension breaks 32-bit tasks; PMR/IRQ predicates affect lockdep and interrupt state accounting.

### Test Signals
Run ptrace, signal, syscall tracing/audit/seccomp, compat, kprobes, stacktrace, and irq-priority masking tests; verify static_assert alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pvclock-abi.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pvclock-abi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pvclock-abi.h` Defines the Arm paravirtual stolen-time ABI structure. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct pvclock_vcpu_stolen_time with little-endian revision, attributes, stolen_time, and 64-byte padding. The file is 17 lines / 374 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No control flow; producers and consumers share the packed ABI structure.

### State, Persistence, And Dependencies
Persistent state is hypervisor-updated stolen-time memory shared with the guest. Header owns no storage. Used by KVM/paravirt clock code and follows ARM DEN0057A layout.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Packing, endian, or alignment changes would break guest/hypervisor ABI and stolen-time accounting.

### Test Signals
Build KVM/paravirt configs and validate stolen-time updates in guest tests across endian assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pvclock-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/resctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/resctrl.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/resctrl.h` Connects arm64 resource-control plumbing to MPAM support. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
Includes linux/arm_mpam.h as the architecture resctrl surface. The file is 2 lines / 67 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No local control flow; all behavior is delegated to MPAM headers and implementation files.

### State, Persistence, And Dependencies
No local state; MPAM/resctrl state lives in subsystem structures and hardware registers. Integrates scheduler/resctrl policies with Arm Memory Partitioning and Monitoring when enabled.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Risk is mostly include-contract drift: if MPAM header shape changes, resctrl consumers may fail or miscompile.

### Test Signals
Build CONFIG_ARM64_MPAM/resctrl combinations and run resctrl/MPAM allocation tests where hardware or emulation exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/resctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rqspinlock.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/rqspinlock.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/rqspinlock.h` Provides arm64-specific time-bounded acquire polling for resilient qspinlock code, avoiding WFE hangs when timer event streams are unavailable. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
smp_cond_time_check_count, __smp_cond_load_relaxed_spinwait(), __smp_cond_load_acquire_timewait(), smp_cond_load_acquire_timewait(), res_smp_cond_load_acquire(). The file is 93 lines / 2964 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
If arch_timer_evtstrm_available() is true, wait with acquire loads and __cmpwait_relaxed; otherwise spin with cpu_relax, periodically check the timeout expression, then add acquire ordering after control dependency.

### State, Persistence, And Dependencies
No persistent state; loops observe lock words and timer-derived time expressions. Depends on barrier.h, arch timer event-stream availability, asm-generic/rqspinlock.h; integrates with resilient queued spinlocks and scheduler/locking paths.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
A wait loop that sleeps forever can deadlock; relaxed fallback ordering must still provide acquire semantics; timeout amortization can affect latency.

### Test Signals
Run qspinlock/rqspinlock stress with and without event-stream support, lockdep, preemption/RT configs, and timeout-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rqspinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi.h` Defines top-level Arm CCA Realm Services Interface presence and memory-state helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
RSI_PDEV_NAME, static key rsi_present, arm64_rsi_init(), arm64_rsi_is_protected(), is_realm_world(), rsi_set_memory_range(), rsi_set_memory_range_protected(), rsi_set_memory_range_protected_safe(), rsi_set_memory_range_shared(). The file is 70 lines / 1677 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
rsi_set_memory_range loops until the requested physical range reaches end, invoking rsi_set_addr_range_state and validating returned top progression; wrappers select RAM/EMPTY and destroyed-page policy.

### State, Persistence, And Dependencies
Persistent state is the rsi_present static key and RMM-owned RIPAS state for IPA ranges. Header owns no storage beyond declarations. Depends on errno, jump_label, rsi_cmds; integrates with Arm CCA realm boot, mem-encryption/shared-memory handling, pgtable-prot PROT_NS_SHARED, and device exposure.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Bad range progression handling could loop or accept partial conversions; wrong destroyed-page flags can lose data or share protected memory incorrectly.

### Test Signals
Run CCA realm boot, shared/protected memory conversion tests, invalid range tests, and non-realm static-key false-path builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_cmds.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_cmds.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_cmds.h` Implements inline RSI SMC command wrappers for version discovery, realm config, RIPAS state, and attestation token retrieval. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
RSI_GRANULE_SIZE, enum ripas, rsi_request_version(), rsi_get_realm_config(), rsi_ipa_state_get(), rsi_set_addr_range_state(), rsi_attestation_token_init(), rsi_attestation_token_continue(). The file is 162 lines / 3994 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Each helper prepares SMCCC registers, issues SMC, and maps returned registers to status/out parameters. Attestation init validates 32-64 byte challenge size and copies the challenge into SMCCC 1.2 registers; continue retrieves token chunks into a granule buffer.

### State, Persistence, And Dependencies
State lives in RMM/realm firmware: ABI version, realm_config contents, RIPAS state, and attestation-in-progress state bound to CPU by the RSI ABI. Depends on arm-smccc, string, memory, rsi_smc; integrates with CCA guest drivers, memory conversion, and attestation flows.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
SMC argument ordering and physical-address alignment are ABI critical; attestation continue must run after init on the same CPU; accepting RSI_REJECT as success would corrupt memory-state assumptions.

### Test Signals
Test against RMM/CCA emulator or hardware for version negotiation, realm config alignment, RIPAS transitions, malformed challenges, and multi-chunk attestation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_smc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_smc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_smc.h` Defines the Arm CCA RSI SMC ABI constants, statuses, feature IDs, realm_config layout, RIPAS flags, and host-call function IDs. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
RSI_ABI_VERSION*, RSI_SUCCESS/error constants, SMC_RSI_FID(), SMC_RSI_* function IDs, struct realm_config aligned to 4K, RSI_NO_CHANGE_DESTROYED, RSI_CHANGE_DESTROYED, RSI_ACCEPT, RSI_REJECT. The file is 193 lines / 5357 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow in the header; it encodes the ABI consumed by rsi_cmds.h and assembly/C callers.

### State, Persistence, And Dependencies
Persistent ABI state is in firmware and shared buffers such as realm_config. Header owns no runtime state. Depends on linux/arm-smccc.h; integrates with Realm Management Monitor services, CCA memory state, attestation, measurements, and host calls.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Any numeric FID/status/layout change breaks firmware ABI; realm_config alignment and padding must remain exactly as required by RMM.

### Test Signals
Validate with ABI conformance tests, static layout assertions, RMM emulator smoke tests, and endian/packing checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/runtime-const.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/runtime-const.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/runtime-const.h` Provides arm64 runtime-constant patching primitives that replace placeholder instruction immediates after boot-time values are known. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
runtime_const_ptr(), runtime_const_shift_right_32(), runtime_const_init(), __runtime_fixup_16(), __runtime_fixup_caches(), __runtime_fixup_ptr(), __runtime_fixup_shift(), runtime_const_fixup(). The file is 92 lines / 2441 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Macros emit placeholder movz/movk or lsr instructions plus relative offsets in named sections. runtime_const_init walks those offsets, patches instruction immediates through lm_alias(), then cleans/invalidates caches to PoU.

### State, Persistence, And Dependencies
State is encoded in special linker sections runtime_ptr_* and runtime_shift_* plus patched kernel text. Modules are rejected. Depends on cacheflush and byteorder; integrates with boot-time text patching, alternatives-like runtime constants, and low-level code that needs fast patched literals.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Instruction encoding, endian conversion, and cache maintenance must be exact; patching modules or wrong aliases can corrupt executable text.

### Test Signals
Boot tests with runtime constants, objdump validation of patched immediates, big-endian build coverage, and cache coherency stress after patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/runtime-const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rwonce.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/rwonce.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/rwonce.h` Overrides READ_ONCE under LTO to preserve address-dependency ordering with RCpc acquire loads on arm64. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__LOAD_RCPC, __rwonce_typeof_unqual(), __READ_ONCE(), fallback include of asm-generic/rwonce.h. The file is 83 lines / 2399 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
For 1/2/4/8-byte loads under LTO, inline assembly emits ldar or alternative-patched ldapr depending on ARM64_HAS_LDAPR; other sizes fall back to volatile loads. Non-LTO and VDSO builds use the generic definitions.

### State, Persistence, And Dependencies
No persistent state; alternatives patch instruction choice based on CPU capabilities. Depends on compiler_types, alternative-macros, generic rwonce; used across the kernel anywhere READ_ONCE participates in dependency ordering.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Compiler or CPU reordering could break lockless algorithms; type-qualifier workarounds and asm constraints must keep thread-safety and aliasing diagnostics quiet.

### Test Signals
Build LTO/non-LTO, run LKMM/litmus-sensitive lockless tests, RCU stress, and LDAPR alternative patch coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/rwonce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/scs.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/scs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/scs.h` Defines Shadow Call Stack assembly macros and dynamic SCS patching support for arm64. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
Assembler macros scs_load_current_base, scs_load_current, scs_save; dynamic_scs_init(); EDYNSCS_* error codes; __pi_scs_patch(). The file is 68 lines / 1276 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Assembly entry/switch paths load or save x18 SCS pointer from task thread_info when CONFIG_SHADOW_CALL_STACK is enabled. Dynamic SCS can enable a static branch after early patching reports support.

### State, Persistence, And Dependencies
Persistent state is per-task scs_base/scs_sp and dynamic_scs_enabled static branch. Patch state lives in transformed unwind/frame data. Depends on asm-offsets, sysreg, linux/scs, cpufeature; integrates with entry code, context switch, compiler SCS instrumentation, and PAC-to-SCS patching.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
x18 is ABI-reserved for SCS; wrong offsets or save/load omissions break returns. Dynamic patching errors can corrupt EH frame metadata.

### Test Signals
Run SCS-enabled boot, context-switch, stack unwinding, dynamic SCS patch dry-run/error tests, and compiler instrumentation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/scs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sdei.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/sdei.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/sdei.h` Declares arm64 Software Delegated Exception Interface entry, stack, event state, and conduit helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
SDEI_EXIT_HVC/SMC, SDEI_STACK_SIZE, per-CPU active event pointers, sdei_exit_mode, __sdei_asm_handler(), __sdei_asm_entry_trampoline(), __sdei_handler_abort(), __sdei_handler(), do_sdei_event(), sdei_arch_get_entry_point(). The file is 53 lines / 1569 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Firmware enters the assembly handler or trampoline, minimal state is captured into pt_regs, then __sdei_handler/do_sdei_event invoke the registered event. Abort discards a running context.

### State, Persistence, And Dependencies
Persistent state includes per-CPU active normal/critical events and sdei_exit_mode. Handler context is transient on SDEI stacks. Depends on linkage, preempt, types, virt, pt_regs; integrates with firmware SDEI driver, KPTI trampoline, stacktrace SDEI stack detection, and exception entry.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong conduit entrypoint or stack sizing can corrupt exception handling; abort paths must not resume discarded contexts; KPTI trampoline must be mapped correctly.

### Test Signals
Run SDEI firmware/emulation tests, normal/critical nesting, KPTI enabled boots, stack unwinding across SDEI stacks, and HVC/SMC conduit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sdei.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/seccomp.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/seccomp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/seccomp.h` Defines arm64 seccomp audit architecture metadata and compat syscall numbers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__NR_seccomp_*_32 aliases, SECCOMP_ARCH_NATIVE*, SECCOMP_ARCH_COMPAT* constants, generic seccomp include. The file is 31 lines / 891 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow here; generic seccomp uses these constants to validate filter architecture and syscall numbers.

### State, Persistence, And Dependencies
No local state; filters persist in task seccomp state. Depends on unistd_compat_32, asm-generic/seccomp, audit arch constants; integrates with syscall entry, audit, ptrace, and compat tasks.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong audit arch or compat syscall constants could let filters match the wrong ABI or fail open/closed unexpectedly.

### Test Signals
Run seccomp selftests for native and compat tasks, audit arch checks, and CONFIG_COMPAT off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sections.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/sections.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/sections.h` Declares arm64 linker-section boundaries for alternatives, hyp text/data, idmap, init/exit, irq entry, trampoline, relocation, and hibernation text. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
Extern section symbols such as __alt_instructions, __hyp_* ranges, __idmap_text, __entry_tramp_text, __irqentry_text, __relocate_new_kernel; entry_tramp_text_size(). The file is 32 lines / 1221 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Runtime users compare pointers against section ranges or copy/map special sections; this header only exposes boundaries.

### State, Persistence, And Dependencies
State is the kernel image/linker layout. No mutable header state. Depends on asm-generic/sections.h; used by alternatives, KVM/hyp mapping, kexec, hibernation, traps, entry trampoline, and memory protection.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Section-boundary drift can mis-map hyp/idmap code, break W^X, or misclassify trap locations.

### Test Signals
Linker map validation, boot tests with KVM/hyp, hibernation/kexec, alternatives patching, and trap in_entry_text checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/semihost.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/semihost.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/semihost.h` Provides a minimal semihosting UART putc helper for early console/debug output. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
smh_putc(struct uart_port *, unsigned char). The file is 24 lines / 537 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Moves the address of the byte to x1, operation number 3 to x0, then executes hlt 0xf000 for the semihosting monitor.

### State, Persistence, And Dependencies
No kernel state; output side effect is handled by debugger/semihosting environment. Used by semihosting earlycon/UART plumbing; relies on Arm semihosting ABI.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Executing HLT without a semihosting monitor can trap unexpectedly; memory clobber and register constraints must preserve the byte address.

### Test Signals
Boot under semihosting-enabled QEMU/debugger, verify earlycon output, and ensure normal platforms do not select this path accidentally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/semihost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/set_memory.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/set_memory.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/set_memory.h` Declares arm64 memory-attribute and direct-map validity helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
can_set_direct_map(), set_memory_valid(), set_direct_map_invalid_noflush(), set_direct_map_default_noflush(), set_direct_map_valid_noflush(), kernel_page_present(), set_memory_encrypted(), set_memory_decrypted(). The file is 22 lines / 715 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Implementation files change PTE validity/encryption attributes and may defer TLB flushes for noflush variants; this header defines the callable surface.

### State, Persistence, And Dependencies
Persistent effects are page-table attributes and memory encryption/shared state. Header owns no storage. Depends on mem_encrypt and asm-generic/set_memory; integrates with module/text permissions, direct map hardening, memory hotplug, confidential computing, and page allocator/debug code.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Changing direct-map validity without required flushes or encryption coordination can expose stale mappings or corrupt data.

### Test Signals
Run set_memory selftests, rodata/text permission checks, direct-map debug tests, memory hotplug, and encrypted/decrypted transition tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/set_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/setup.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/setup.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/setup.h` Declares early boot FDT/boot argument storage and parses the arm64 debug_rodata mode. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__fdt_pointer, boot_args[4], arch_parse_debug_rodata(). The file is 44 lines / 792 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
arch_parse_debug_rodata accepts on/off/noalias and sets rodata_enabled/rodata_full accordingly; other strings return false for generic parsing.

### State, Persistence, And Dependencies
Persistent boot state includes __fdt_pointer, boot_args, rodata_enabled, and rodata_full. Depends on string and uapi setup; used by head.S, early boot setup, command-line parsing, and rodata permission setup.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Incorrect parsing can weaken rodata protection or reject valid boot arguments; early variables must remain accessible before full init.

### Test Signals
Boot with debug_rodata=on/off/noalias/invalid, inspect rodata permissions and early FDT argument propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/shmparam.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/shmparam.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/shmparam.h` Defines shared-memory low-boundary alignment for arm64 and compat IPC. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
COMPAT_SHMLBA and asm-generic/shmparam include. The file is 17 lines / 425 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow; generic IPC code uses constants during SHM attachment address selection.

### State, Persistence, And Dependencies
No local state; shared memory state is in IPC/mm subsystems. Integrates compat syscalls with generic shmparam behavior and page-size assumptions.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong compat alignment can break legacy 32-bit applications; page-size assumptions must match non-aliasing D-cache behavior.

### Test Signals
Run native and compat SYSV SHM attach tests on 4K/16K/64K configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal.h` Adds arm64 signal-address tag stripping rules before exposing si_addr to userspace. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
arch_untagged_si_addr(). The file is 25 lines / 650 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
For SIGTRAP/TRAP_BRKPT watchpoint-like cases it preserves all address bits for historical ABI; otherwise it returns untagged_addr(addr).

### State, Persistence, And Dependencies
No state; transforms signal metadata during delivery. Depends on memory.h and uapi signal/siginfo; integrates with MTE/tagged-address ABI, signal delivery, ptrace/debug exceptions.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong tag stripping changes userspace ABI or leaks tag bits inconsistently; watchpoint exception compatibility is special-case sensitive.

### Test Signals
Run signal/MTE/tagged-address selftests, watchpoint SIGTRAP tests, and compat signal delivery checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal32.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal32.h` Defines AArch32 compat signal frame layouts and setup entry points for arm64 compat tasks. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct compat_sigcontext, compat_ucontext, compat_sigframe, compat_rt_sigframe, compat_setup_frame(), compat_setup_rt_frame(), compat_setup_restart_syscall(). The file is 81 lines / 1980 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
CONFIG_COMPAT builds populate legacy sigcontext/ucontext and retcode fields for 32-bit signal delivery. Non-compat builds return -ENOSYS stubs.

### State, Persistence, And Dependencies
Signal frame state persists on the user stack and forms a userspace ABI. Header owns no kernel storage. Depends on linux/compat; integrates with signal delivery, rt_sigreturn, ptrace, restart_syscall, and compat syscall ABI.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Struct layout, padding, alignment, and register order are ABI fixed; mistakes break 32-bit signal handlers or restarts.

### Test Signals
Run compat signal, rt_sigreturn, SA_RESTART, ptrace signal injection, and layout compile assertions where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/simd.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/simd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/simd.h` Controls safe use of kernel-mode SIMD/FPSIMD/NEON and provides scoped guard helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
may_use_simd(), DEFINE_LOCK_GUARD_1(ksimd), scoped_ksimd(). The file is 60 lines / 1484 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
may_use_simd checks finalized CPU capabilities, FPSIMD support, and excludes hardirq/NMI context. scoped_ksimd wraps kernel_neon_begin/end around a temporary user_fpsimd_state buffer.

### State, Persistence, And Dependencies
State affected is current task/kernel FPSIMD save area while inside guarded SIMD sections. Header owns no storage. Depends on cleanup, irqflags, percpu, preempt, neon; integrates crypto, RAID/checksum, compression, and other kernel NEON users.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Using SIMD in hardirq/NMI or before capability finalization can corrupt user FPSIMD state; callers must not assume may_use_simd remains true after preemption changes.

### Test Signals
Run kernel NEON users under preemption/softirq stress, crypto selftests, FPSIMD context-switch tests, and CONFIG_KERNEL_MODE_NEON off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/simd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp.h` Defines arm64 SMP boot status values, logical CPU mapping, IPI types, secondary entry declarations, CPU hotplug/death helpers, and crash-stop hooks. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
CPU_* status constants, raw_smp_processor_id(), __cpu_logical_map, cpu_logical_map(), set_cpu_logical_map(), smp_init_cpus(), enum ipi_msg_type, set_smp_ipi_range*(), secondary_start_kernel(), struct secondary_data, secondary_data, __early_cpu_boot_status, secondary_entry(), arch_send_call_function_*(), arch_send_wakeup_ipi(), __cpu_disable(), cpu_die(), cpu_park_loop(), update_cpu_boot_status(), cpu_panic_kernel(), cpus_are_stuck_in_kernel(), crash_smp_send_stop(). The file is 160 lines / 3924 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Boot CPU populates secondary_data and releases secondary_entry; secondaries update status with WRITE_ONCE plus DSB, then either come online, request kill, panic, or park in WFE/WFI loops. IPI helpers route scheduler/call-function/timer/irq-work/crash messages.

### State, Persistence, And Dependencies
Persistent state includes per-task thread_info->cpu, __cpu_logical_map, secondary_data, boot status, and stuck CPU tracking. Depends on threads, cpumask, thread_info, const; integrates with CPU bring-up, hotplug, GIC IPIs, ACPI parking protocol, crash/kexec, scheduler, and topology.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Boot status values are consumed by assembly/firmware paths; missing DSB can hide failures; stuck CPUs inhibit kexec/hibernate and must not run freed memory.

### Test Signals
Run SMP boot/hotplug stress, crash stop tests, ACPI parking protocol builds, feature-mismatch secondary failure tests, and IPI tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp_plat.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp_plat.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp_plat.h` Provides platform SMP helpers for MPIDR hashing and logical CPU lookup. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct mpidr_hash, extern mpidr_hash, mpidr_hash_size(), get_logical_index(). The file is 44 lines / 824 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
get_logical_index linearly scans possible CPUs and compares cpu_logical_map(cpu) to the requested MPIDR.

### State, Persistence, And Dependencies
Persistent state is global mpidr_hash and __cpu_logical_map from smp.h. Depends on cpumask, smp, types; used by CPU topology, boot CPU discovery, and platform CPU operations.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
MPIDR map collisions or stale logical maps break CPU bring-up and affinity reporting; linear lookup assumes nr_cpu_ids is initialized.

### Test Signals
Boot multi-cluster systems, validate logical map against firmware tables, CPU hotplug, and topology dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp_plat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sparsemem.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/sparsemem.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/sparsemem.h` Defines arm64 sparsemem physical-memory and section-size limits. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
MAX_PHYSMEM_BITS, MAX_POSSIBLE_PHYSMEM_BITS, SECTION_SIZE_BITS. The file is 32 lines / 747 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow; memory model code consumes constants at build time and early boot.

### State, Persistence, And Dependencies
No local state; affects mem_section layout and vmemmap sizing. Depends on pgtable-prot PHYS_MASK_SHIFT; integrates sparsemem, memory hotplug, vmemmap, huge vmemmap mappings, and page allocator.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong section size can fail builds or prevent PMD vmemmap mappings; physical-bit limit must match LPA2/PA configuration.

### Test Signals
Build 4K/16K/64K sparsemem and memory-hotplug configs, boot with high memory, inspect vmemmap layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/spectre.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/spectre.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/spectre.h` Declares arm64 Spectre/Meltdown mitigation state, branch predictor hardening hooks, hyp vector slot choices, and alternative patch callbacks. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
enum mitigation_state, enum arm64_hyp_spectre_vector, bp_hardening_cb_t, struct bp_hardening_data, per-CPU bp_hardening_data, arm64_apply_bp_hardening(), arm64_get_spectre_*_state(), has_spectre_*(), spectre_*_enable_mitigation(), spectre_v4_enable_task_mitigation(), BHB patch callbacks, try_emulate_el1_ssbs(), spectre_print_disabled_mitigations(). The file is 123 lines / 3890 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Entry code calls arm64_apply_bp_hardening; if ARM64_SPECTRE_V2 alternative cap is present, it fetches per-CPU hardening data and invokes the callback. Other functions are implemented elsewhere to detect CPU vulnerability and patch mitigation sequences.

### State, Persistence, And Dependencies
Persistent state is per-CPU bp_hardening_data and alternative/static CPU capability state; per-task SSBS mitigation state is managed through task flags. Depends on smp, percpu, cpufeature, virt; integrates exception entry, KVM hyp vectors, SMCCC firmware workarounds, alternatives, scheduler task mitigation, and sysfs vulnerability reporting.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Mitigation ordering and vector-slot enum order are security critical; missing callbacks or wrong patching can leave speculation vulnerabilities exposed or crash exception entry.

### Test Signals
Run spectre selftests, CPU capability matrix boots, KVM hyp vector tests, SMCCC conduit tests, sysfs vulnerability checks, and alternative patch validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/spectre.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/spinlock.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/spinlock.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/spinlock.h` Selects arm64 queued spinlock/rwlock implementations and defines post-spinlock ordering and vCPU preemption reporting. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
Includes qspinlock/qrwlock, smp_mb__after_spinlock(), vcpu_is_preempted(). The file is 27 lines / 601 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Lock algorithms live in included headers; this file adds a full memory barrier after spinlock and reports vCPU preemption as false for osq_lock expectations.

### State, Persistence, And Dependencies
No local state. Depends on qspinlock, qrwlock, barrier; integrates with generic locking, osq_lock, scheduler, and virtualization-sensitive spin paths.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Changing vcpu_is_preempted semantics can break optimistic spinning assumptions; barrier weakening can expose lock-protected memory reordering.

### Test Signals
Run locktorture, qspinlock/qrwlock stress, osq mutex tests, virtualization builds, and LKMM barrier tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/spinlock_types.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/spinlock_types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/spinlock_types.h` Provides arm64 raw spinlock/rwlock type definitions by including generic qspinlock and qrwlock types under the expected include guard discipline. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
Include guard check, asm-generic/qspinlock_types.h, asm-generic/qrwlock_types.h. The file is 15 lines / 366 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow.

### State, Persistence, And Dependencies
No local state; lock words are defined by generic queued lock types. Integrated with linux spinlock type declarations and arm64 spinlock.h.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Direct inclusion is rejected to preserve type-definition ordering; changing generic type selection breaks ABI of lock structures.

### Test Signals
Compile locking headers, lockdep configs, and direct-include negative coverage through normal kernel builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stack_pointer.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stack_pointer.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stack_pointer.h` Exposes the current stack pointer register to C code. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
register unsigned long current_stack_pointer asm("sp"). The file is 10 lines / 247 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No flow; reads of current_stack_pointer compile to use the architectural SP register.

### State, Persistence, And Dependencies
No storage beyond compiler register binding. Used by stacktrace, entry checks, and diagnostics requiring current SP.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Compiler assumptions around fixed register variables are delicate; use must avoid taking persistent addresses or expecting normal variable storage.

### Test Signals
Build with supported compilers and run stacktrace/on_thread_stack checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stack_pointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stackprotector.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stackprotector.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stackprotector.h` Initializes stack canary state and pointer-auth kernel state during early boot paths that never return. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__stack_chk_guard, boot_init_stack_canary(). The file is 40 lines / 1181 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
When stack protector is enabled, it gets a random canary, stores current->stack_canary, optionally updates global __stack_chk_guard, then initializes/switches kernel PAC keys and enables pointer auth.

### State, Persistence, And Dependencies
Persistent state is current task stack_canary, optional global canary, and PAC key/sysreg state. Depends on pointer_auth; integrates with compiler stack protector, init task setup, and PAC enablement.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Must run only in non-returning paths; global canary on SMP is weaker than per-task; PAC enable ordering must match key initialization.

### Test Signals
Boot stackprotector and per-task canary configs, stack-smash LKDTM tests, PAC kernel configs, and suspend/resume sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace.h` Defines arm64 stack discovery helpers for task, IRQ, overflow, SDEI, and EFI runtime stacks plus backtrace entry points. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
dump_backtrace(), irq_stack_ptr, stackinfo_get_irq(), on_irq_stack(), stackinfo_get_task(), on_task_stack(), on_thread_stack(), overflow_stack, stackinfo_get_overflow(), SDEI stack helpers, efi_rt_stack_top, stackinfo_get_efi(). The file is 120 lines / 2905 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Helpers compute low/high stack bounds from per-CPU pointers or task stack base and call common stackinfo_on_stack. Unwinder code uses these stack_info ranges to validate frame records and legal stack transitions.

### State, Persistence, And Dependencies
Persistent state includes per-CPU IRQ/overflow/SDEI stack pointers and EFI runtime stack top. Header functions are read-only. Depends on percpu, sched/task_stack, llist, memory, pointer_auth, ptrace, sdei, stacktrace/common; integrates with dump_backtrace, perf/ftrace, oops reporting, SDEI, EFI runtime, and overflow handling.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong stack bounds can hide frames or permit invalid unwinds; per-CPU pointer reads must match active stack context.

### Test Signals
Run stacktrace selftests, oops/backtrace paths, IRQ/SDEI/EFI stack unwinds, overflow stack tests, and KASAN stack checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/common.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/common.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/common.h` Provides common robust stack-unwinder state and frame-record consumption helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct stack_info, struct unwind_state, stackinfo_get_unknown(), stackinfo_on_stack(), unwind_init_common(), unwind_find_stack(), unwind_consume_stack(), unwind_next_frame_record(). The file is 171 lines / 4137 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Unwind steps verify alignment, find a stack containing the next frame_record, consume that record by moving the active low bound above it, then READ_ONCE the next fp/lr. Stack transitions destroy old stack ranges so unwinding cannot move backward.

### State, Persistence, And Dependencies
State is the mutable unwind_state used during a backtrace; no global storage. Depends on linux/types and frame_record definition from users; shared by kernel and nVHE stacktrace code.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Bounds arithmetic overflow or accepting backward transitions can create infinite or unsafe unwinds; incorrect frame metadata can truncate valid traces.

### Test Signals
Run unwinder tests with nested task/IRQ/overflow/SDEI/HYP stacks, corrupted-frame tests, and READ_ONCE/KASAN instrumentation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/frame.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/frame.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/frame.h` Defines standard and metadata frame-record layouts for arm64 unwinding. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
FRAME_META_TYPE_NONE/FINAL/PT_REGS, struct frame_record, struct frame_record_meta. The file is 48 lines / 1116 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow; unwinders interpret zero fp/lr plus metadata type to terminate or consume pt_regs frames.

### State, Persistence, And Dependencies
Frame records persist on kernel stacks while functions/traps are active. Used by ptrace pt_regs stackframe field, stacktrace/common, entry assembly, and unwinder implementation.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Layout is ABI with assembly and compiler frame generation; wrong metadata handling breaks backtrace termination or pt_regs unwinds.

### Test Signals
Compile with frame pointers, run oops/backtrace and pt_regs unwind tests, verify final frame records in start_thread_common.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/frame.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/nvhe.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/nvhe.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/nvhe.h` Adds KVM nVHE hypervisor stack-unwind initialization and host-side declarations. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
kvm_nvhe_unwind_init(), DECLARE_KVM_NVHE_PER_CPU overflow_stack and kvm_stacktrace_info, kvm_arm_hyp_stack_base, kvm_nvhe_dump_backtrace(). The file is 55 lines / 1730 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Initialization seeds unwind_state with HYP fp/pc. In non-protected nVHE, the host can unwind HYP stack directly; protected nVHE dumps through shared buffers handled elsewhere.

### State, Persistence, And Dependencies
State is HYP per-CPU stacktrace data, overflow stack, and host hyp stack base. Depends on stacktrace/common and KVM nVHE per-CPU declarations; integrates with KVM hyp diagnostics and protected KVM stack dumping.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Host/protected mode memory visibility differs; direct HYP stack access in pKVM would violate isolation; wrong offset can decode bad frames.

### Test Signals
Run KVM nVHE/pKVM backtrace tests, hyp fault injection, and host dump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/nvhe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stage2_pgtable.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stage2_pgtable.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stage2_pgtable.h` Defines KVM stage-2 page-table level and cache-preallocation calculations for arm64. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
stage2_pgtable_levels(ipa), kvm_stage2_levels(mmu), kvm_mmu_cache_min_pages(mmu). The file is 33 lines / 1055 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Calculations account for hardware concatenation of up to 16 entry tables by applying stage-1 level math to IPA_SHIFT minus four bits.

### State, Persistence, And Dependencies
No local state; consumes mmu->vtcr and KVM MMU cache state elsewhere. Depends on linux/pgtable.h and VTCR helpers; integrates with KVM stage-2 page-table allocation and IPA size support.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong level counts under-allocate page-table pages or program invalid VTCR levels, breaking guest memory translation.

### Test Signals
Run KVM guests across IPA sizes, LPA2 stage-2 configs, dirty-log/memslot stress, and allocation failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stage2_pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stat.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stat.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stat.h` Defines arm64 compat stat64 layout while delegating native stat ABI to UAPI. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
uapi stat include, struct stat64 under CONFIG_COMPAT, STAT64_HAS_BROKEN_ST_INO. The file is 51 lines / 947 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow; compat syscall implementations copy to/from this fixed layout.

### State, Persistence, And Dependencies
State persists in userspace ABI buffers only. Depends on linux/time and asm/compat for compat types; integrates with stat/newfstatat compat syscalls and filesystem VFS copyout.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Layout and padding are ABI fixed; broken st_ino handling must match historical userspace expectations.

### Test Signals
Run compat stat syscall tests, structure-size checks, and filesystem metadata round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/static_call.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/static_call.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/static_call.h` Defines arm64 static-call trampolines as executable stubs that branch through a rodata target pointer. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__ARCH_DEFINE_STATIC_CALL_TRAMP(), ARCH_DEFINE_STATIC_CALL_TRAMP(), ARCH_DEFINE_STATIC_CALL_NULL_TRAMP(), ARCH_DEFINE_STATIC_CALL_RET0_TRAMP(). The file is 31 lines / 1050 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
The macro emits a BTI-compatible function in .static_call.text that adrp/ldr loads a nearby rodata quad and br x16 to the target.

### State, Persistence, And Dependencies
Persistent state is generated text and rodata target pointer patched/managed by static call core. Integrates with linux static_call infrastructure, BTI, text patching, and return0 fallback.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Instruction sequence, alignment, symbol sizing, and BTI hint must be valid for alternatives/static-call patching; rodata indirection must remain reachable.

### Test Signals
Build static_call users, objdump trampolines, run static_call selftests, and BTI-enabled boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/static_call.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/string.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/string.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/string.h` Declares arm64 optimized string/memory routines and selects uninstrumented variants for KASAN-sensitive files. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__HAVE_ARCH_STRRCHR/STRCHR/STRCMP/STRNCMP/STRLEN/STRNLEN/MEMCMP/MEMCHR, memcpy/__memcpy, memmove/__memmove, memset/__memset, memcpy_flushcache(), KASAN remaps for memcpy/memmove/memset, __NO_FORTIFY. The file is 69 lines / 1936 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
At compile time, generic code is redirected to arch routines unless KASAN instrumentation requires generic or uninstrumented variants. Runtime behavior is in assembly/C implementations elsewhere.

### State, Persistence, And Dependencies
No local state; side effects are memory copies/sets and optional flushcache behavior. Depends on KASAN/FORTIFY configs and uaccess flushcache; used across all kernel subsystems including Ceph data paths, networking, and page cache.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
String routines are security and performance critical; KASAN remapping must avoid recursive instrumentation; flushcache copy must preserve persistence/cache ordering.

### Test Signals
Run lib/string tests, KASAN/KMSAN/FORTIFY builds, memcpy overlap tests, and persistent-memory flushcache tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/suspend.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/suspend.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/suspend.h` Defines CPU suspend/hibernate saved-state layouts and resume entry declarations. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
NR_CTX_REGS, NR_CALLEE_SAVED_REGS, struct cpu_suspend_ctx, struct sleep_stack_data, sleep_save_stash, cpu_suspend(), cpu_resume(), __cpu_suspend_enter/exit(), _cpu_resume(), swsusp_arch_suspend/resume(), hibernation header save/restore, hibernate_resume_nonboot_cpu_disable(). The file is 54 lines / 1695 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Suspend callers allocate sleep_stack_data on a valid stack, __cpu_suspend_enter saves system and callee-saved registers, firmware finisher powers down, and resume paths restore state before returning. Hibernation saves architecture headers and may resume on the original CPU.

### State, Persistence, And Dependencies
Persistent suspend state lives in stack-allocated sleep_stack_data until resume, sleep_save_stash, and hibernation image metadata. Depends on proc.S layout and PM/hibernation core; integrates PSCI/cpuidle suspend, CPU hotplug, hibernation, and low-level MMU resume.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Struct layout must match assembly exactly and remain 16-byte aligned; stack lifetime assumptions are critical across powerdown; wrong CPU resume can corrupt state.

### Test Signals
Run suspend-to-RAM, CPU idle deep states, hibernation, nonboot CPU resume, and objdump/layout checks against assembly offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/suspend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sync_bitops.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/sync_bitops.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/sync_bitops.h` Maps synchronized bit operations to SMP-safe arm64 bitops even for UP kernels communicating with external entities such as Xen. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
sync_set/clear/change_bit(), sync_test_and_*(), sync_test_bit(), arch_sync_cmpxchg. The file is 27 lines / 1085 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No local flow; macros alias to atomic/SMP-safe bitops and cmpxchg implementations.

### State, Persistence, And Dependencies
No local state; callers mutate target bitmaps atomically. Depends on bitops and cmpxchg; integrates Xen grant/event-channel paths and generic sync_bitops consumers.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Using non-SMP-safe operations under virtualization can race external CPUs/hosts; aliasing must retain barriers/atomicity.

### Test Signals
Run Xen/event-channel/grant tests, bitops atomic tests, UP and SMP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sync_bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall.h` Defines arm64 syscall table ABI and helpers for syscall tracing, argument access, rollback, return values, and audit architecture. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
syscall_fn_t, sys_call_table, compat_sys_call_table, syscall_get_nr(), syscall_rollback(), syscall_get_return_value(), syscall_get_error(), syscall_set_return_value(), syscall_set_nr(), syscall_get/set_arguments(), syscall_get_arch(), syscall_trace_enter/exit(). The file is 126 lines / 2967 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Helpers read syscallno, orig_x0, and regs[1..5]; rollback restores x0 from orig_x0; compat return values are sign-extended or truncated as required. Setting nr to -1 skips the syscall and returns -ENOSYS explicitly.

### State, Persistence, And Dependencies
State is pt_regs syscall fields and task thread compatibility flags. Tables are global const dispatch arrays. Depends on audit, compat, err; integrates syscall entry/exit, ptrace, seccomp, audit, tracing, and compat syscalls.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
orig_x0 handling affects restart/rollback and tracing; compat sign extension is ABI critical; wrong audit arch breaks seccomp/audit filters.

### Test Signals
Run syscall selftests, ptrace syscall emulation, seccomp/audit, compat syscall return tests, and tracepoint checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall_wrapper.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall_wrapper.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall_wrapper.h` Defines arm64 syscall definition wrappers that marshal pt_regs into typed syscall arguments and generate compat/native entry symbols. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
SC_ARM64_REGS_TO_ARGS, COMPAT_SYSCALL_DEFINEx/DEFINE0, COND_SYSCALL_COMPAT, __SYSCALL_DEFINEx, SYSCALL_DEFINE0, COND_SYSCALL, __arm64_sys_ni_syscall(). The file is 82 lines / 3163 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Wrapper macros create __arm64_sys* entry points taking pt_regs, call sign-extension/de-lousing shim functions, run argument tests/protection, then call __do_sys* typed implementations. Conditional syscalls weakly return sys_ni_syscall.

### State, Persistence, And Dependencies
No runtime state beyond generated functions and syscall table references. Depends on ptrace and generic syscall macro infrastructure; integrated by syscall implementation files and build-generated tables.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Macro argument order must match AAPCS syscall register convention; compat wrappers must de-louse 32-bit args; weak fallback symbols must match table names.

### Test Signals
Build syscall tables, run syscall ABI tests, compat syscalls, error injection metadata checks, and sparse/compile coverage for generated wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sysreg.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/sysreg.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/sysreg.h` Central arm64 system-register dictionary and access layer, including encodings, PSTATE helpers, cache/TLBI/AT instruction IDs, debug/trace/GIC/timer/perf registers, SCTLR/MAIR/feature bits, PIE/POE/GCS encodings, and read/write helper macros for named and encoded registers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
sys_reg()/sys_insn(), sys_reg_* extractors, __emit_inst(), SET_PSTATE_* and set_pstate_*(), many SYS_* and OP_* register/instruction encodings, INIT_SCTLR_EL1/EL2 values, MAIR_ATTR*, ID_AA64MMFR0 granule/PARANGE helpers, CPACR/GCR/RGSR/TFSR/GIC/PIE/POE/GCS fields, gicr_insn/gic_insn, mrs_s/msr_s, read_sysreg(), write_sysreg(), read_sysreg_s(), write_sysreg_s(), sysreg_clear_set*(), write_sysreg_hcr(), read_sysreg_par(), SYS_FIELD_* helpers. The file is 1271 lines / 49261 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Most control flow is macro expansion into inline assembly. Encoded-register helpers synthesize mrs/msr instructions for old binutils; HCR writes conditionally insert DSB/ISB for Ampere erratum; PAR reads optionally fence around reads for ARM64_WORKAROUND_1508412.

### State, Persistence, And Dependencies
No high-level storage. Side effects are direct CPU system-register writes, instruction execution, and alternative-patched instruction sequences. Depends on bits, stringify, kasan-tags, kconfig, gpr-num, generated sysreg-defs.h, alternative, bitfield, build_bug, types; every low-level arm64 subsystem consumes it: MMU, cache/TLB, KVM, perf, debug, timers, GIC, PAC, MTE, SME/SVE, GCS, CCA, and exception entry.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Numeric encodings are architecture ABI; a wrong field can write the wrong system register. Inline asm constraints and old-binutils fallbacks must be exact. Erratum fences and alternative patching are correctness and security critical.

### Test Signals
Cross-build with old/new binutils, objdump generated mrs/msr/tlbi/at instructions, boot diverse CPUs, run KVM/perf/timer/GIC/MTE/PAC/GCS tests, and validate generated sysreg-defs synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/sysreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/system_misc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/system_misc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/system_misc.h` Declares arm64 fatal exception reporting and register display helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
die(), arm64_notify_die(), __show_regs(). The file is 33 lines / 733 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Implementation paths print or signal fatal exceptions using pt_regs, signal metadata, FAR/ESR-like error values, and reboot/ratelimit policy. Header only declares interfaces.

### State, Persistence, And Dependencies
No local state; implementations affect logs, signals, oops/panic state, and reboot handling. Depends on compiler, linkage, irqflags, signal, ratelimit, reboot; integrates traps, die notifier paths, oops reporting, and signal injection.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Incorrect prototypes or signal metadata can break fatal fault reporting or userspace signal delivery.

### Test Signals
Trigger WARN/oops/LKDTM traps, signal fault paths, and register dump tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/system_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/text-patching.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/text-patching.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/text-patching.h` Declares arm64 instruction read/write/copy/set and synchronized text patching helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
aarch64_insn_read(), aarch64_insn_write(), aarch64_insn_write_literal_u64(), aarch64_insn_set(), aarch64_insn_copy(), aarch64_insn_patch_text_nosync(), aarch64_insn_patch_text(). The file is 17 lines / 544 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Implementations patch instructions directly and optionally coordinate synchronization/cache maintenance for live text changes; this header defines the API.

### State, Persistence, And Dependencies
Persistent effects are modified kernel text and literal data. Header owns no storage. Depends on linux/types; integrates alternatives, ftrace, kprobes, static calls, livepatch, and runtime-const patching.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Text patching must preserve instruction atomicity, cache coherency, W^X policy, and stop-machine/synchronization rules.

### Test Signals
Run alternatives/ftrace/kprobe/static_call/livepatch tests, instruction patch failure tests, and I-cache coherency validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/text-patching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/thread_info.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/thread_info.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/thread_info.h` Defines low-level arm64 thread_info layout and TIF flag assignments consumed by entry assembly, scheduler, preemption, syscall, FP, MTE, SCS, and livepatch paths. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct thread_info, thread_saved_pc/sp/fp(), arch_setup_new_exec(), TIF_* flags, _TIF_* masks, _TIF_SYSCALL_WORK, INIT_SCS, INIT_THREAD_INFO(). The file is 130 lines / 4243 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Entry and scheduler code read flags and preempt_count directly from current_thread_info; syscall exit tests _TIF_SYSCALL_WORK; init macros seed foreign FP state, preempt count, and optional SCS pointers.

### State, Persistence, And Dependencies
Persistent per-task state includes flags, saved ttbr0 under SW PAN, preempt_count/need_resched, SCS pointers, MPAM partid/pmg, and cpu id. Depends on compiler, memory, stack_pointer, types; integrates with entry.S, preempt.h, processor.h, scheduler, FP/SVE/SME, MTE, seccomp, ptrace, livepatch, freezer, and MPAM.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Bit numbers and layout are assembly ABI; moving fields or flags breaks entry code. TIF_LAZY_MMU_PENDING coordinates pgtable barriers and must match pgtable.h.

### Test Signals
Build with SCS, SW_TTBR0_PAN, MPAM, compat, MTE, SVE/SME; run syscall-work, preemption, FP context, and entry/exit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/timex.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/timex.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/timex.h` Defines the arm64 cycle counter source for generic timing code. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
get_cycles() maps to arch_timer_read_counter(), then includes asm-generic/timex.h. The file is 18 lines / 343 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No local flow; calls read the architected timer counter used by delay loops.

### State, Persistence, And Dependencies
No local state; timer counter is hardware state. Depends on arch_timer; integrates scheduler/timekeeping profiling and generic timex users.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Counter accessibility and frequency assumptions must match arch timer setup; using a non-monotonic source would break profiling/delays.

### Test Signals
Run timekeeping, delay calibration, clocksource, and suspend/resume timer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlb.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlb.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlb.h` Connects arm64 TLB invalidation to the generic mmu_gather API and page-table page freeing. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
tlb_flush(), tlb_get_level(), __pte_free_tlb(), __pmd_free_tlb(), __pud_free_tlb(), __p4d_free_tlb(). The file is 119 lines / 2741 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
tlb_flush decides TTL level from mmu_gather cleared_* fields, handles fullmm teardown specially, chooses NOWALKCACHE unless tables were freed, and calls __flush_tlb_range. Free helpers convert page-table pages to ptdesc and enqueue them for RCU/freeing, respecting runtime folded levels.

### State, Persistence, And Dependencies
State is mmu_gather batching state and queued page-table descriptors. No local global storage. Depends on pagemap, asm-generic/tlb, pgtable folding helpers, tlbflush.h; integrates munmap, mprotect, exit_mmap, page-table freeing, and KVM/mmu notifier secondary TLB invalidation indirectly.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong TTL hints can miss invalidations; freeing folded levels would corrupt top-level tables; fullmm logic relies on ASID allocator behavior.

### Test Signals
Run mmu_gather stress, munmap/mprotect/exit tests, page-table RCU debug, KVM notifier tests, and folded-level configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbbatch.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbbatch.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbbatch.h` Defines arm64 per-batch state for deferred TLB unmap flushing. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct arch_tlbflush_unmap_batch with optional cpumask_var_t cpumask under ARM64_ERRATUM_4193714. The file is 18 lines / 452 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No local flow; tlbflush.h populates and flushes the cpumask when SME DVMSync erratum handling is required.

### State, Persistence, And Dependencies
Persistent only during an unmap batch; optional cpumask tracks CPUs needing DVMSync. Depends on cpumask; integrates with arch_tlbbatch_add_pending/flush and generic batched unmap paths.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Missing cpumask allocation/clear can lose erratum synchronization or leak batch state.

### Test Signals
Run batched unmap stress with erratum config, cpumask allocation failure injection, and normal configs without the field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbbatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbflush.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbflush.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbflush.h` Implements arm64 TLB invalidation primitives, TLBI instruction wrappers, range invalidation, TTL hints, KPTI user-ASID invalidation, batched unmap synchronization, and erratum-specific SME DVMSync handling. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__tlbi(), __tlbi_user(), __TLBI_VADDR(), get_trans_granule(), sme_dvmsync*(), TLBI_TTL_* and tlbi_op, vae*/vale*/ipas* helpers, __tlbi_level_asid(), TLBIR_* range fields, __flush_tlb_range_op(), TLBF_* flags, local_flush_tlb_all(), flush_tlb_all(), flush_tlb_mm(), arch_tlbbatch_should_defer(), arch_tlbbatch_flush(), __flush_tlb_range(), flush_tlb_range(), __flush_tlb_page(), flush_tlb_kernel_range(), __flush_tlb_kernel_pgtable(), arch_tlbbatch_add_pending(), pte_needs_flush(), huge_pmd_needs_flush(). The file is 758 lines / 21398 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Flushes follow DSB-before, TLBI, DSB-after, and optional ISB. Range flushing uses FEAT_TLBIRANGE when available, handles LPA2 64K alignment, falls back to per-entry operations, and escalates excessive ranges to full ASID/global flushes. Flags select walk-cache invalidation, notifier calls, sync elision, and local-only invalidation.

### State, Persistence, And Dependencies
No owned storage except optional batch cpumask managed elsewhere. Side effects are architectural TLB and walk-cache invalidations, mmu notifier secondary invalidations, and erratum DVMSync IPIs. Depends on bitfield, mm_types, sched, mmu_notifier, cputype, mmu, stage2/KVM LPA2 helpers, cpufeature alternatives; integrates with pgtable.h, tlb.h, KVM stage-2, mmu_gather, KPTI, MTE/SME errata, and secondary TLB notifiers.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Ordering bugs cause stale translations; wrong TTL/range/LPA2 encoding can miss invalidations; TLBF_NOSYNC must only be used when later synchronization is guaranteed; notifier suppression can break IOMMU/KVM secondary TLBs.

### Test Signals
Run TLB shootdown stress, munmap/mprotect/THP collapse, KVM/IOMMU notifier tests, LPA2 and TLBIRANGE hardware/emulation, KPTI configs, erratum configs, and pte_needs_flush permission-transition tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/topology.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/topology.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/topology.h` Connects arm64 CPU topology, NUMA PCI locality, scheduler frequency invariance, CPU capacity, and hardware pressure hooks to generic topology code. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
pcibus_to_node(), cpumask_of_pcibus(), update_freq_counters_refs(), arch_scale_freq_tick, arch_set_freq_scale, arch_scale_freq_capacity, arch_scale_freq_invariant, arch_scale_freq_ref, arch_scale_cpu_capacity, arch_update_cpu_topology, arch_scale/update_hw_pressure, arch_cpu_is_threaded(). The file is 44 lines / 1354 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Scheduler calls the mapped topology_* functions for frequency/capacity/hardware pressure accounting; NUMA builds map PCI buses to node cpumasks; arch_cpu_is_threaded checks MPIDR_MT_BITMASK.

### State, Persistence, And Dependencies
Persistent state is generic arch_topology data and NUMA node maps, not this header. Depends on cpumask, numa, arch_topology, read_cpuid_mpidr; integrates scheduler load balancing, EAS, cpufreq/AMU counters, NUMA, PCI locality, and generic topology.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Incorrect capacity/frequency hooks skew scheduling and performance; wrong threaded detection affects SMT/core scheduling policy.

### Test Signals
Run scheduler topology tests, cpufreq/AMU frequency invariance validation, NUMA PCI locality tests, and topology sysfs inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/trans_pgd.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/trans_pgd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/trans_pgd.h` Declares temporary page-table construction helpers used for transitions such as hibernation/kexec/idmap/vector copying. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct trans_pgd_info, trans_pgd_create_copy(), trans_pgd_idmap_page(), trans_pgd_copy_el2_vectors(), trans_pgd_stub_vectors[]. The file is 41 lines / 1041 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Callers supply an allocator returning zeroed pages; implementations copy a virtual range, create an idmap page and TTBR0/T0SZ, or copy EL2 vectors for temporary execution contexts.

### State, Persistence, And Dependencies
Persistent state is allocated temporary page tables and copied vector pages until the transition completes. Depends on bits, types, pgtable-types; integrates hibernation resume, kexec/relocation, EL2 vector handling, and low-level MMU transitions.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Allocator must return exactly one zeroed page; temporary mappings must not omit required executable/vector pages; physical TTBR values must match active granule and VA config.

### Test Signals
Run hibernation/kexec tests, allocation failure injection, EL2 vector copy validation, and page-table dump of temporary mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/trans_pgd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/traps.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/traps.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/traps.h` Declares arm64 trap, breakpoint, signal-injection, RAS SError severity, and MOPS register-repair helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
try_emulate_armv8_deprecated(), force_signal_inject(), arm64_notify_segfault(), arm64_force_sig_fault*(), arm64_force_sig_mceerr(), arm64_force_sig_ptrace_errno_trap(), bug/cfi/reserved/kasan/ubsan brk handlers, early_brk64(), dump_kernel_instr(), arm64_skip_faulting_instruction(), __in_irqentry_text(), in_entry_text(), arm64_is_ras_serror(), arm64_ras_serror_get_severity(), arm64_is_fatal_ras_serror(), arm64_serror_panic(), arm64_mops_reset_regs(). The file is 162 lines / 4850 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Trap handlers inspect ESR/pt_regs, may emulate deprecated instructions, deliver signals, skip faulting instructions, or panic on fatal RAS errors. MOPS reset decodes ESR option bits and rewinds PC/registers to a canonical prologue state after a fault in memory copy/set instructions.

### State, Persistence, And Dependencies
State is pt_regs/user_pt_regs mutated during exception handling and section-boundary symbols used for entry text checks. No independent persistent storage. Depends on list, esr, ptrace, sections, CPU RAS capabilities; integrates exception entry, signal delivery, BUG/CFI/KASAN/UBSAN breakpoints, MTE/MOPS, RAS, and oops handling.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
ESR decoding is security and reliability critical; wrong MOPS repair can resume with corrupted registers; preemptible RAS checks are forbidden because CPU capability is per-CPU.

### Test Signals
Run trap/signal selftests, deprecated instruction emulation, BUG/KASAN/UBSAN/LKDTM breakpoints, RAS SError injection, MOPS fault tests, and entry-text classification checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/traps.h -->
