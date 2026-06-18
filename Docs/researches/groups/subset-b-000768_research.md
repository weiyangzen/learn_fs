# Research: subset-b-000768

Grouped research for PowerPC KVM, MMU, machine-description, interrupt-controller, and board support headers in the Ceph client source tree.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_asm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_asm.h

Purpose: centralizes low-level PowerPC KVM assembly constants shared by BookE, Book3S PR, and Book3S HV entry/exit code. It gives assembly-safe load/store width macros, interrupt vector numbers, interrupt priority indexes, host flags, resume flags, guest-mode state values, and opcode masks used by KVM handlers.

Important APIs/types/functions: assembler macros `PPC_STD` and `PPC_LD` choose 64-bit `std`/`ld` or 32-bit high-word `stw`/`lwz` forms. `BOOKE_INTERRUPT_*` and `BOOK3S_INTERRUPT_*` encode trap vectors, including HV-specific vectors such as `BOOK3S_INTERRUPT_HV_DECREMENTER`, `BOOK3S_INTERRUPT_H_DATA_STORAGE`, and the real-mode passthrough sentinel `BOOK3S_INTERRUPT_HV_RM_HARD`. `BOOK3S_IRQPRIO_*`, `BOOK3S_HFLAG_*`, `RESUME_*`, and `KVM_GUEST_MODE_*` form the contract between assembly trampolines and C state machines. `PO_XOP_OPCODE_MASK` extracts major and extended opcodes.

Control flow: this header has no C control flow, but its constants drive guest exception dispatch. BookE and Book3S assembly handlers compare trap numbers against these definitions, prioritize pending Book3S interrupts using `BOOK3S_IRQPRIO_*`, and return to guest or host by testing `RESUME_*` flags.

State and persistence: no storage is allocated here. The values are ABI-like compile-time state baked into KVM assembly, `struct kvm_vcpu_arch` fields, and guest entry/exit paths. Changing them affects persistent binary compatibility between C, assembly, and generated offsets.

Dependencies and integration points: included by KVM Book3S and BookE handler headers and assembly. It integrates with exception vector layout, guest-mode tracking, resume-state handling, and instruction decode helpers.

Risks: vector values and guest-mode constants must stay synchronized with assembly labels and C switch paths. `VCPU_SIZE_BYTES` assumes a 64 KiB-aligned interrupt-vector page layout. The 32-bit `PPC_STD`/`PPC_LD` high-word behavior is subtle and can corrupt state if used with the wrong offset convention.

Test signals: build BookE and Book3S KVM configurations in 32-bit and 64-bit modes; boot guests that exercise decrementer, external, syscall, program, FP/Altivec/VSX, and HV fault exits; validate KVM tracepoints show expected `KVM_GUEST_MODE_*` transitions and resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s.h

Purpose: declares the main Book3S KVM architecture interface: shadow segment/BAT state, HPTE caches, virtual-core scheduling state, Book3S per-vcpu MMU state, interrupt injection helpers, HPT/radix MMU operations, nested-HV hooks, transactional-memory save/restore, and common register accessors.

Important APIs/types/functions: core types are `struct kvmppc_bat`, `struct kvmppc_sid_map`, `struct hpte_cache`, `struct kvmppc_vcore`, and `struct kvmppc_vcpu_book3s`. Exported operations cover hash and radix translation (`kvmppc_mmu_map_page`, `kvmppc_book3s_radix_page_fault`, `kvmppc_mmu_radix_xlate`), HPTE cache lifecycle, HPT hypercalls (`kvmppc_do_h_enter`, `kvmppc_do_h_remove`), dirty logging, page pinning, interrupt priority queues, BAT/MSR/FSCR updates, nested guest entry and nested TLB invalidation, and accessors for GPR, CR, XER, LR, CTR, PC, FPR, VSX, VMX, VCORE timing, and DEC expiry state.

Control flow: Book3S guest execution enters through PR or HV backends, maps faults through HPT or radix paths, queues pending interrupts by priority, and returns to guest or host using resume flags from `kvm_asm.h`. Accessor macros for nestedv2 reload/dirty tracking conditionally call expensive guest-state-buffer helpers only when `kvmhv_is_nestedv2()` is active; otherwise they collapse to no-ops.

State and persistence: persistent VM state is held in `vcpu->arch.book3s`, `vcpu->arch.vcore`, HPTE hash lists, VSID context arrays, SLB shadows, BAT arrays, LPCR/PCR/timebase fields, and dirty/rmap structures. Virtual-core state persists across runs and coordinates runnable threads, napping threads, stolen/preempted time, and online counts.

Dependencies and integration points: depends on Linux KVM core, `kvm_book3s_asm.h`, guest-state-buffer support, HPTE constants from `kvm_host.h`, radix page-table code, XICS/XIVE interrupt code, pSeries hypercalls, and nested-HV support.

Risks: this is a cross-subsystem contract header; changes can break assembly entry, KVM ioctls, nested virtualization, memory-slot dirty logging, or interrupt delivery. HPTE cache and rmap updates require careful locking/RCU. Nestedv2 dirty tracking must not be skipped for registers that are cached in the guest-state buffer.

Test signals: run Book3S PR and HV guest boot tests, HPT and radix memory-pressure tests, migration dirty-log tests, nested guest entry/TLB invalidation tests, XICS/XIVE interrupt injection, TM emulation tests, and KVM selftests that exercise one-reg access and vcpu run/exit state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_32.h

Purpose: supplies 32-bit Book3S PR KVM shadow-vcpu access and classic segment/PTE constants.

Important APIs/types/functions: `svcpu_get()` returns `vcpu->arch.shadow_vcpu`; `svcpu_put()` is empty. Constants include `PTE_SIZE`, `VSID_ALL`, `SR_INVALID`, `SR_KP`, PTE bits (`PTE_V`, `PTE_SEC`, `PTE_M`, `PTE_R`, `PTE_C`), `SID_SHIFT`, `ESID_MASK`, `VSID_MASK`, and `VPN_SHIFT`.

Control flow: C code obtains the shadow vcpu directly from the vcpu architecture state and performs no preemption manipulation in this 32-bit path. Translation code uses the constants to decode segment registers and PTEs.

State and persistence: the only state touched is the existing `shadow_vcpu` pointer and guest segment/PTE state stored elsewhere. The constants are compile-time MMU layout values.

Dependencies and integration points: included by Book3S PR MMU code and the common Book3S accessor layer; it integrates with 32-bit hash translation and shadow-vcpu save/restore.

Risks: the empty `svcpu_put()` is intentional; adding symmetry with the 64-bit PACA path would be wrong unless the ownership model changes. Segment and PTE bit constants are architectural and must match the classic 32-bit Book3S MMU format.

Test signals: compile 32-bit Book3S KVM, boot a PR guest, exercise segment faults and BAT/segment translation, and verify shadow-vcpu state is not shared across vcpus incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_64.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_64.h

Purpose: provides 64-bit Book3S KVM helpers for nested guests, HPTE locking and decoding, page-size and TLBIE encodings, Linux PTE read/update, rmap locking, radix/HPT page-table lookup, transactional-memory checkpoint copying, and nestedv2 counters/hooks.

Important APIs/types/functions: `struct kvm_nested_guest` tracks L1/L2 ownership, LPIDs, shadow page tables, process table, radix mode, refcount, and TLB flush state. `struct rmap_nested` and `for_each_nest_rmap_safe()` encode nested rmaps. Key helpers include `try_lock_hpte`, `unlock_hpte`, `kvmppc_hpte_page_shifts`, `compute_tlbie_rb`, `hpte_rpn`, `hpte_is_writable`, `hpte_cache_flags_ok`, `kvmppc_read_update_linux_pte`, permission helpers, `lock_rmap`, `slot_is_aligned`, `is_vrma_hpte`, `set_dirty_bits*`, `sanitize_msr`, and checkpoint copy helpers.

Control flow: nested guest code allocates or looks up an L2 object, maps L1 guest real addresses to host real pages, serializes faults/TLB invalidations through `tlb_lock`, and records nested rmaps. HPTE update flow atomically locks HPTE dword 0, decodes page-size and permission fields, updates dirty/reference state, emits TLBIE operands, and unlocks with release ordering.

State and persistence: persistent state lives in nested guest objects, memslot rmap entries, HPT entries, radix page tables, dirty bitmaps, PACA shadow vcpu storage, and transactional-memory checkpoint arrays in `vcpu->arch`. Per-CPU flush masks and previous CPU arrays persist until nested guest release.

Dependencies and integration points: includes hash MMU, bitops, CPU feature checks, PPC opcode macros, and PTE walking. It is used by Book3S HV HPT/radix MMU code, nested virtualization, dirty logging, and pSeries hypercall implementations.

Risks: HPTE locking uses endian-aware load-reserve/store-conditional and must preserve big-endian HPT layout. Nested rmap encodes pointers and single-entry sentinel bits in one word, so alignment and nonzero LPID assumptions are critical. Page-size encoding differs across POWER generations, and wrong TLBIE operands can leave stale translations.

Test signals: run HPT and radix KVM selftests, nested guest boot/migration tests, hugepage and 64K page-size coverage, dirty-log aging tests, concurrent H_ENTER/H_REMOVE stress, TM guest tests, and lockdep/KCSAN coverage around rmap and HPTE update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_asm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_asm.h

Purpose: defines Book3S KVM assembly glue, XICS register offsets, SMT/subcore limits, split-core coordination state, host-state save areas, and shadow-vcpu state used by PR and HV entry/exit handlers.

Important APIs/types/functions: `XICS_XIRR`, `XICS_MFRR`, and `XICS_IPI` define interrupt-controller offsets. `MAX_SMT_THREADS` and `MAX_SUBCORES` size vcore and split-mode arrays. The assembler `DO_KVM` macro branches selected vectors to `kvmppc_trampoline_*` labels when `CONFIG_KVM_BOOK3S_HANDLER` is enabled. C-visible structures include `struct kvm_split_mode`, `struct kvmppc_host_state`, and `struct kvmppc_book3s_shadow_vcpu`.

Control flow: assembly exception prologues expand `DO_KVM` for supported Book3S traps and route guest exits through KVM trampolines. HV entry code saves host registers and per-thread state in the PACA `kvmppc_host_state`; PR code uses the shadow vcpu for volatile guest state not immediately committed to `struct kvm_vcpu`.

State and persistence: host-state fields persist across guest entry until exit restores host MSR, stack, TOC, HID5, XICS/XIVE state, PMU registers, PURR/SPURR/DSCR, and split-mode state. Shadow-vcpu fields hold guest GPRs, CR/XER/CTR/LR/PC, fault DAR/DSISR, last instruction, SLB/SR shadows, and FSCR.

Dependencies and integration points: depends on `kvm_asm.h` in assembler mode and on PACA/Book3S KVM code in C mode. It integrates with XICS/XIVE interrupt delivery, split-core scheduling, guest entry assembly, and save/restore code.

Risks: structure layout is consumed by assembly and generated offsets, so field reordering is high risk. The trampoline vector list must match supported exception handlers. Split-core arrays are bounded by architectural SMT/subcore limits.

Test signals: compile with `CONFIG_KVM_BOOK3S_HANDLER`, run Book3S guest entry/exit tests across interrupt vectors, validate PMU/XICS/XIVE save/restore after guest exits, and boot POWER8 split-core or SMT-heavy configurations where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_uvmem.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_uvmem.h

Purpose: declares Book3S secure virtual machine ultravisor memory operations and provides no-op or unsupported fallbacks when `CONFIG_PPC_UV` is disabled.

Important APIs/types/functions: enabled builds expose `kvmppc_uvmem_init/free/available`, memslot init/free/create/delete hooks, SVM hypercall handlers `kvmppc_h_svm_page_in`, `kvmppc_h_svm_page_out`, `kvmppc_h_svm_init_start/done/abort`, `kvmppc_send_page_to_uv`, and `kvmppc_uvmem_drop_pages`. Disabled builds return success for inert init/slot setup, `false` for availability, `H_UNSUPPORTED` for SVM hypercalls, and `-EFAULT` for page sending.

Control flow: KVM initialization probes ultravisor memory availability, initializes memslot metadata, and services secure-VM hypercalls by moving pages between normal guest memory and ultravisor-protected memory. Memslot deletion/drop paths can page out or discard protected pages.

State and persistence: secure page state is owned by the ultravisor and KVM memslot metadata in implementation files. This header only defines the call surface and fallback behavior.

Dependencies and integration points: depends on KVM memory slots, PPC ultravisor support, SVM hypercall return codes, and Book3S HV memory-management paths.

Risks: fallback return codes are part of guest-visible ABI; changing them can break guests probing secure VM support. Page-in/page-out operations are security-sensitive because they transfer ownership between host-visible and ultravisor-private memory.

Test signals: build with and without `CONFIG_PPC_UV`, run SVM guest initialization/page-in/page-out tests on UV-capable hardware or simulator, verify unsupported hypercalls on non-UV hosts, and test memslot add/remove cleanup of protected pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_uvmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_booke.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_booke.h

Purpose: provides BookE KVM register access helpers, e500 LPID and `ehpriv` constants, fault-address access, floating-point register access, and magic-page capability detection.

Important APIs/types/functions: constants include `KVMPPC_NR_LPIDS`, `KVMPPC_INST_EHPRIV`, `EHPRIV_OC_SHIFT`, and `EHPRIV_OC_DEBUG`. Inline helpers get/set GPRs, CR, XER, CTR, LR, PC, FPRs, fault DAR, byte-swap requirements, and `kvmppc_supports_magic_page()`.

Control flow: KVM BookE code manipulates guest architectural state through these simple inline accessors. Magic-page mapping is only enabled for `CONFIG_KVM_E500V2`; `kvmppc_need_byteswap()` currently returns false with a note that TLB inspection would be needed.

State and persistence: all mutations target `vcpu->arch.regs`, `vcpu->arch.fp`, or `vcpu->arch.fault_dear`. No independent storage is allocated.

Dependencies and integration points: includes Linux KVM host definitions and is consumed by BookE emulation, MMIO, exception injection, and e500 magic-page code.

Risks: accessors assume register indexes are valid. The byte-swap helper is conservative/incomplete for guests using endian-changing mappings. FPR indexing depends on `TS_FPROFFSET`.

Test signals: boot e500/e500v2 guests, exercise MMIO load/store emulation, debug `ehpriv` traps, FP unavailable/save-restore paths, and magic-page setup only on e500v2 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_booke.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_booke_hv_asm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_booke_hv_asm.h

Purpose: defines the assembler-side BookE HV exception redirection macro for guest-state exceptions on embedded hypervisor-capable cores.

Important APIs/types/functions: the assembler macro `DO_KVM intno srr1` checks MSR[GS] through `mtocrf` and branches to `kvmppc_handler_<intno>_<srr1>` inside a CPU feature section when `CONFIG_KVM_BOOKE_HV` and `CPU_FTR_EMB_HV` are enabled.

Control flow: normal exception prologues arrive with scratch registers already populated according to 32-bit or 64-bit entry conventions documented in the header. If the exception came from guest state, the macro branches into KVM; otherwise execution falls through to the host exception handler label.

State and persistence: no C state is stored here. It relies on prologue-saved scratch registers, PACA exception save areas, thread save areas, and bolted TLB miss state.

Dependencies and integration points: includes `feature-fixups.h`; integrates with BookE HV exception vectors, KVM BookE handler labels, MSR[GS] guest-state detection, and CPU feature patching.

Risks: register convention comments are part of the ABI between exception prologues and KVM handlers. A wrong `srr1` variant or missing feature patching can route host exceptions into KVM or miss guest exits.

Test signals: build `CONFIG_KVM_BOOKE_HV`, boot an e500mc/e6500 HV guest, inject normal and critical/debug/machine-check exceptions from guest and host contexts, and verify host-only exceptions fall through.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_booke_hv_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_fpu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_fpu.h

Purpose: declares software floating-point helpers used by KVM instruction emulation for single-precision, double-precision, compare, fused multiply-add/subtract, select, sign, conversion, and square-root/reciprocal operations.

Important APIs/types/functions: single-precision helpers include `fps_fres`, `fps_frsqrte`, `fps_fsqrts`, `fps_fadds`, `fps_fdivs`, `fps_fmuls`, `fps_fsubs`, `fps_fmadds`, `fps_fmsubs`, `fps_fnmadds`, `fps_fnmsubs`, and `fps_fsel`. Macro families declare double-precision `fpd_*` helpers, plus `fpd_fcmpu`, `fpd_fcmpo`, `kvm_cvt_fd`, and `kvm_cvt_df`.

Control flow: instruction emulation decodes an FP instruction, passes FPSCR/CR and source/destination register storage to the matching helper, and the helper updates destination bits plus FPSCR/CR exception/condition state.

State and persistence: helpers mutate caller-provided FPSCR, CR, and FPR storage. This header does not hold state.

Dependencies and integration points: used by PowerPC KVM emulator code and depends on Linux integer types. It bridges guest FP instruction semantics to softfloat-like implementation files.

Risks: bit-exact IEEE/PPC FPSCR behavior is hard to preserve. Passing the wrong 32-bit/64-bit register slice or failing to update CR for compare operations causes guest-visible arithmetic bugs.

Test signals: KVM FP instruction emulation tests, guest libm/compiler FP test suites, FPSCR exception flag checks, compare CR-field validation, and cross-checks against hardware execution for representative operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_guest.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_guest.h

Purpose: exposes a low-overhead runtime predicate for whether the kernel is running as a KVM guest.

Important APIs/types/functions: when pSeries or KVM guest support is built, it declares `DECLARE_STATIC_KEY_FALSE(kvm_guest)`, `is_kvm_guest()`, and `check_kvm_guest()`. Otherwise, `is_kvm_guest()` returns false and `check_kvm_guest()` returns zero.

Control flow: early initialization calls `check_kvm_guest()` to detect KVM and enable the static key. Runtime users call `is_kvm_guest()`, which becomes a static-branch test in enabled configurations and a constant false in disabled ones.

State and persistence: the `kvm_guest` static key persists for the boot lifetime once detection completes. Disabled builds have no stored state.

Dependencies and integration points: depends on Linux jump labels and is included by `kvm_para.h` and paravirtual feature code.

Risks: calling before detection completes can report false. Static-key state must reflect the actual hypervisor to avoid issuing KVM-specific hypercalls on non-KVM systems.

Test signals: boot pSeries under KVM and non-KVM hypervisors, verify static key transitions, and check that `kvm_para_available()` only returns true under KVM guest conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_guest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_host.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_host.h

Purpose: defines the architecture-specific KVM host data model for PowerPC: VM/vCPU stats, exit reasons, memory slots, HPT/rmap structures, vcore states, PAPR TCE tables, interrupt-controller state, BookE debug/MMU fields, nestedv2 IO buffers, and the large `struct kvm_vcpu_arch`.

Important APIs/types/functions: key definitions include `KVM_MAX_VCPUS`, `KVM_MAX_VCPU_IDS`, `KVM_REQ_*`, HPTE cache sizes, `struct kvm_vm_stat`, `struct kvm_vcpu_stat`, `enum kvm_exit_types`, `struct kvmppc_exit_timing`, `struct kvm_arch_memory_slot`, `struct kvm_hpt_info`, `struct kvm_arch`, `struct kvmppc_vpa`, `struct kvmppc_pte`, `struct kvmppc_mmu`, `struct kvmppc_slb`, passthrough IRQ maps, MMIO register encodings, and `struct kvm_vcpu_arch`.

Control flow: this header is mostly declarative, but its fields are walked by KVM core operations during VM creation, vcpu run, memory-slot changes, interrupt routing, dirty logging, MMIO emulation, HPT/radix page faults, and guest entry/exit accounting. Stub hooks such as `kvm_arch_memslots_updated()` are intentionally empty for generic KVM integration.

State and persistence: persistent VM state includes LPID/MMU mode, HPT/radix roots, memory-slot arch data, TCE tables, RTAS tokens, XICS/XIVE/MPIC devices, secure-VM state, nested guest arrays, vcore lists, and dirty/rmap metadata. Per-vcpu state includes registers, timers, interrupt pending bits, BookE TLB/debug state, FPU/VMX/VSX state, MMIO emulation state, VPA/DTL/SLB shadows, and statistics.

Dependencies and integration points: integrates Linux KVM core, PPC MMU headers, XICS/XIVE/MPIC devices, PAPR TCE/IOMMU, pSeries RTAS, nested-HV, BookE, and generic module/device infrastructure.

Risks: structure layout and field semantics are consumed throughout KVM and sometimes by assembly/generated offsets. Mis-sizing ID limits breaks userspace ABI for vcpu IDs. Rmap and memory-slot fields are concurrency-sensitive. Interrupt-controller pointers may be NULL depending on selected irqchip mode.

Test signals: KVM selftests for vcpu creation, one-reg access, dirty logging, memory-slot add/delete, irqchip creation, TCE/IOMMU ioctls, BookE TLB ioctls, nested virtualization, secure VM transitions, and statistics/debugfs visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_para.h

Purpose: implements PowerPC KVM paravirtual feature discovery and availability checks.

Important APIs/types/functions: `kvm_para_available()` checks `CONFIG_KVM_GUEST` and `is_kvm_guest()`. `kvm_arch_para_features()` issues `epapr_hypercall0_1(KVM_HCALL_TOKEN(KVM_HC_FEATURES), &r)` and returns the feature bitmap or zero. `kvm_arch_para_hints()` and `kvm_check_and_clear_guest_paused()` currently return zero/false.

Control flow: callers first test availability, then query KVM features through the ePAPR hypercall. Hypercall failure collapses to no features.

State and persistence: this header stores no state; availability comes from the static key in `kvm_guest.h`, and features are fetched on demand.

Dependencies and integration points: includes `asm/kvm_guest.h` and UAPI KVM para definitions. It integrates guest kernel paravirt setup with hypervisor feature tokens.

Risks: feature queries must not run outside KVM guest mode. The no-hints and no-paused-state behavior is guest ABI behavior for this architecture.

Test signals: boot PowerPC KVM guests with `CONFIG_KVM_GUEST`, validate feature bitmap hypercalls, ensure non-KVM boots see zero features, and check callers handle zero hints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_ppc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_ppc.h

Purpose: declares the broad PowerPC KVM implementation API: vcpu run, instruction emulation, MMIO load/store, MMU translation, BookE and Book3S backend hooks, HPT/radix management, TCE/RTAS/pSeries hypercalls, interrupt-controller APIs, real-mode HV calls, LPID allocation, and shared-register access helpers.

Important APIs/types/functions: enums model emulation results and translation modes. `struct kvmppc_ops` is the backend dispatch table for HV/PR operations. `union kvmppc_one_reg` helps one-reg ioctls. APIs span `kvmppc_vcpu_run`, `kvmppc_handle_load/store`, `kvmppc_emulate_instruction`, `kvmppc_xlate`, core vcpu lifecycle and interrupt queueing, HPT allocation/resizing, PAPR TCE ioctls/hcalls, RTAS, XICS/XIVE/MPIC, real-mode HPT hypercalls, LPID management, and helpers for EPR, SRs, endian state, MMIO register packing, and field extraction.

Control flow: generic KVM core enters PowerPC through `kvmppc_ops`, which dispatches to PR, HV, BookE, or Book3S implementations. Guest exits are decoded into instruction emulation, MMIO, timer, interrupt, TCE, RTAS, or hypercall paths. Optional interrupt-controller blocks compile to real functions or stubs based on XICS/XIVE/MPIC support.

State and persistence: operations mutate `struct kvm`, `struct kvm_vcpu`, HPT/radix page tables, TCE tables, RTAS token maps, interrupt-controller state, LPID pools, vcpu shared pages, and real-mode host operation tables.

Dependencies and integration points: includes KVM host state, OpenPIC/MPIC, XICS/XIVE, pSeries, BookE, Book3S, CMA HPT allocation, and generic userspace ioctl ABI types.

Risks: this header is the public internal contract between many KVM backends; stub return values must match caller expectations. Real-mode functions have restricted locking/memory rules. Endian and shared-register access helpers directly affect guest ABI.

Test signals: full PowerPC KVM selftest suite, guest boot under HV/PR/BookE, MMIO emulation tests, one-reg ioctl tests, TCE/RTAS tests, XICS/XIVE/MPIC interrupt injection, LPID allocation stress, and HPT resize/migration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_ppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_types.h

Purpose: selects module subcomponent names for split PowerPC Book3S KVM module builds.

Important APIs/types/functions: `KVM_SUB_MODULES` is defined as `kvm-pr,kvm-hv`, `kvm-pr`, or `kvm-hv` depending on whether `CONFIG_KVM_BOOK3S_64_PR` and/or `CONFIG_KVM_BOOK3S_64_HV` are modular. Otherwise it is undefined.

Control flow: no runtime flow; build and module metadata consume the macro.

State and persistence: no runtime state.

Dependencies and integration points: depends on Kconfig `IS_MODULE()` and is included by generic KVM type/module plumbing.

Risks: incorrect module naming breaks dependency/autoload handling for split PR/HV modules.

Test signals: build all combinations of built-in and modular Book3S PR/HV KVM, inspect generated module dependencies, and verify module autoload loads the expected submodules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/libata-portmap.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/libata-portmap.h

Purpose: maps legacy ATA primary and secondary IRQ lookups to PowerPC PCI legacy IDE IRQ helpers.

Important APIs/types/functions: `ATA_PRIMARY_IRQ(dev)` expands to `pci_get_legacy_ide_irq(dev, 0)` and `ATA_SECONDARY_IRQ(dev)` expands to `pci_get_legacy_ide_irq(dev, 1)`.

Control flow: libata PCI drivers call the macros while probing legacy IDE compatibility channels.

State and persistence: no state; IRQ routing is queried from PCI/platform firmware.

Dependencies and integration points: depends on PCI legacy IRQ infrastructure and integrates libata with PowerPC PCI host bridges.

Risks: firmware or host bridge bugs in legacy IRQ routing propagate directly to ATA probe. The macro assumes channel indexes 0 and 1 match primary/secondary IDE.

Test signals: boot PowerPC platforms with legacy IDE, verify libata detects both channels and receives interrupts, and test with PCI host bridges that provide nonstandard legacy routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/libata-portmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/linkage.h

Purpose: provides PowerPC linkage overrides for conditional syscalls and syscall aliases on 64-bit ELF ABI v1.

Important APIs/types/functions: under `CONFIG_PPC64_ELF_ABI_V1`, `cond_syscall(x)` emits weak aliases for both descriptor and dot-symbol forms to `sys_ni_syscall`; `SYSCALL_ALIAS(alias, name)` emits global aliases for both forms.

Control flow: no runtime flow; inline assembly affects symbol resolution at link time.

State and persistence: no state, but generated weak/global symbols persist in the kernel image.

Dependencies and integration points: includes `asm/types.h` and integrates with syscall tables, PPC64 ELFv1 function descriptor ABI, and generic linkage macros.

Risks: ELFv1 requires both `name` and `.name`; missing one breaks syscall dispatch or module symbol resolution. These macros must not be generalized to ABI v2 without revisiting symbol semantics.

Test signals: build PPC64 ELFv1 kernels, inspect syscall symbols, verify unimplemented syscalls resolve to `sys_ni_syscall`, and run syscall smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/livepatch.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/livepatch.h

Purpose: initializes PowerPC livepatch per-thread stack metadata.

Important APIs/types/functions: `klp_init_thread_info(struct task_struct *p)` sets `task_thread_info(p)->livepatch_sp` to `end_of_stack(p) + 1` for `CONFIG_LIVEPATCH_64`; otherwise it is an empty inline.

Control flow: task initialization calls the helper so livepatch stack scanning starts with a sentinel-adjusted stack pointer.

State and persistence: writes `thread_info.livepatch_sp` for each task on 64-bit livepatch builds.

Dependencies and integration points: depends on scheduler task stack helpers and integrates with kernel livepatch consistency checking.

Risks: off-by-one stack initialization can make livepatch stack scanning miss or overrun the valid stack region. Disabled builds intentionally carry no metadata.

Test signals: build with `CONFIG_LIVEPATCH_64`, run livepatch transition tests, validate stack scanning across newly forked tasks, and build non-livepatch configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/livepatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/local.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/local.h

Purpose: implements PowerPC Book3S 64-bit `local_t` per-CPU arithmetic using PMU-aware local interrupt masking, and falls back to `asm-generic/local.h` elsewhere.

Important APIs/types/functions: defines `local_t`, `LOCAL_INIT`, `local_read`, `local_set`, add/sub/inc/dec return and test macros, `local_cmpxchg`, `local_try_cmpxchg`, `local_xchg`, `local_add_unless`, `local_inc_not_zero`, and raw `__local_*` helpers.

Control flow: update helpers save PMU/local IRQ state with `powerpc_local_irq_pmu_save`, modify the local counter, and restore state. Compare/exchange variants perform the compare while interrupts are masked.

State and persistence: mutates caller-owned `local_t.v`; no global state. The guarantee is local-CPU atomicity, not inter-CPU atomicity.

Dependencies and integration points: depends on percpu, atomic, irqflags, and `asm/hw_irq.h`; used by per-CPU counters where full atomics are unnecessary.

Risks: callers must not use `local_t` for cross-CPU synchronization. The raw `__local_dec(l)` macro increments rather than decrements in this source, so consumers should avoid raw helpers unless they know the local convention and tests cover it.

Test signals: compile Book3S 64 and generic fallback configs, run per-CPU counter tests, lockdep/irq tracing around PMU interrupt masking, and inspect raw helper users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/lppaca.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/lppaca.h

Purpose: defines the PAPR logical partition per-processor area (VPA/lppaca) and SLB shadow structures shared between pSeries guests and the hypervisor.

Important APIs/types/functions: `struct lppaca` maps the 640-byte architected VPA with fields for descriptor, size, dynamic hardware IDs, VPHN counters, DTL controls, donated CPU hints, wait/yield/dispatch accounting, nested KVM L1/L2 timing counters, and DTL index. `lppaca_of(cpu)`, `LPPACA_OLD_SHARED_PROC`, `lppaca_shared_proc()`, `get_lppaca()`, and `struct slb_shadow` are key interfaces.

Control flow: pSeries setup registers the VPA with the hypervisor; runtime code reads shared-proc status, yield counts, dispatch trace logs, and SLB shadow data. `lppaca_shared_proc()` checks firmware split-partition support and a non-architected old-status bit.

State and persistence: lppaca memory is per-CPU, cacheline-aligned, hypervisor-shared runtime state. It persists while registered and is updated by both OS and hypervisor. SLB shadow buffers persist as hypervisor-maintained SLB save areas.

Dependencies and integration points: depends on Book3S, PACA, firmware feature checks, MMU SLB constants, and pSeries VPA registration hypercalls. KVM and PHYP both consume parts of this layout.

Risks: layout, size, alignment, endianness, and 4 KiB boundary constraints are ABI-sensitive. Pre-v4.14 KVM requires advertising 1 KiB despite the canonical 640-byte structure. The shared-proc test uses a non-architected field and may need replacement.

Test signals: boot pSeries under KVM and PHYP, verify VPA registration, DTL logging, shared/dedicated processor detection, VPHN changes, and SLB shadow restore across context switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/lppaca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/lv1call.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/lv1call.h

Purpose: declares the PlayStation 3 LV1 hypervisor call interface and generates typed wrappers for many argument-count combinations.

Important APIs/types/functions: macro families `LV1_*_IN_ARG_DECL`, `LV1_*_OUT_ARG_DECL`, `LV1_*_IN_*_OUT_ARG_DECL`, and corresponding argument lists generate function signatures. `LV1_CALL(name, in, out, num)` creates a public wrapper and underscored low-level hypercall declaration, with optional instrumentation point. The file also declares numerous PS3 LV1 calls through those macros.

Control flow: callers invoke a typed `lv1_*` wrapper; it forwards fixed register-style arguments and output pointers to the low-level hypervisor call implementation. Return values are hypervisor status codes and outputs are written through pointer arguments.

State and persistence: this header stores no state. LV1 calls manipulate PS3 hypervisor state such as logical partitions, devices, repository entries, memory mappings, interrupts, and storage resources in implementation/hardware.

Dependencies and integration points: depends on `linux/types.h`, export support, and PS3 platform code. It is the ABI bridge between Linux PS3 drivers and the LV1 hypervisor.

Risks: generated signatures must match the hypervisor ABI exactly; argument count or ordering mistakes corrupt register convention. Output pointers must be valid and checked by callers. Hypercalls can have system-wide resource effects.

Test signals: build PS3 platform support, run PS3 device discovery and storage/network drivers, validate representative LV1 calls return expected status codes, and check wrapper symbol exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/lv1call.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/machdep.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/machdep.h

Purpose: defines the PowerPC machine-description callback table used to bind platform-specific boot, IRQ, PCI, time, reset, power management, kexec, suspend, CPU hotplug, and random seed operations.

Important APIs/types/functions: `struct machdep_calls` contains callbacks for probing/setup, exception initialization, time calibration, IRQ discovery, PCI setup and DMA/IOMMU hooks, restart/poweroff/halt, NVRAM access, progress/error logging, CPU die/idle, machine shutdown, kexec, suspend IRQ handling, CPU probe/release, and random seed. `ppc_md`, `machine_id`, `define_machine`, `machine_is`, `log_error`, and `machine_*_initcall` macros form the public interface.

Control flow: early boot selects a machine description, copies it into `ppc_md`, and platform-neutral code dispatches through callbacks. Machine-specific initcall macros gate init functions on `machine_is(mach)`.

State and persistence: `ppc_md` and `machine_id` persist for the boot lifetime. Callback pointers represent platform policy and hardware access paths.

Dependencies and integration points: integrates with boot probing, device tree, PCI, IRQ, DMA/IOMMU, RTC/NVRAM, kexec, suspend, CPU hotplug, and logging subsystems.

Risks: callbacks may be NULL, so callers must respect optional semantics. `machine_is()` warns before `machine_id` initialization. Callback changes can affect all platform code because `ppc_md` is a central dispatch table.

Test signals: boot representative PowerPC platforms, validate machine probe selection, platform-gated initcalls, restart/poweroff/halt, IRQ setup, PCI DMA/IOMMU hooks, suspend/resume, kexec, and error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/macio.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/macio.h

Purpose: declares the Apple MacIO pseudo-bus, MacIO device representation, resource/IRQ accessors, and driver registration API.

Important APIs/types/functions: `struct macio_bus` links a MacIO chip to an optional PCI host device. `struct macio_dev` wraps a platform device, media-bay relation, DMA parameters, resources, and interrupts. Helpers include `to_macio_device`, `of_to_macio_device`, `macio_dev_get/put`, resource and IRQ accessors, `macio_enable_devres`, resource request/release functions, drvdata and OF-node helpers, `macio_get_pci_dev`, `struct macio_driver`, `to_macio_driver`, and driver register/unregister functions.

Control flow: MacIO bus enumeration creates `macio_dev` objects from Open Firmware nodes. Drivers register `struct macio_driver`, probe matching devices, request resources/IRQs, and receive suspend/resume/shutdown/media-bay callbacks.

State and persistence: each `macio_dev` persists as a platform device with resource arrays and driver data. Bus/chip pointers persist for device lifetime.

Dependencies and integration points: depends on OF, platform devices, optional PCI, and optional PMAC media bay support. It integrates old PowerMac onboard devices with Linux driver model.

Risks: resource and IRQ accessors do not bounds-check indexes. Non-PCI machines can have `pdev == NULL`. Media-bay devices require callback coordination during hot-swap.

Test signals: boot PowerMac systems with MacIO devices, verify OF matching, resource request/release, IRQ delivery, suspend/resume, PCI-backed and non-PCI MacIO paths, and media-bay events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/macio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mc146818rtc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mc146818rtc.h

Purpose: supplies PowerPC machine-dependent access macros for MC146818-compatible RTC/CMOS registers.

Important APIs/types/functions: default `RTC_PORT(x)` maps index/data ports to `0x70 + x`, `RTC_ALWAYS_BCD` is set to 1, `CMOS_READ(addr)` writes the index via `outb_p` and reads data via `inb_p`, and `CMOS_WRITE(val, addr)` writes index then data.

Control flow: RTC code selects a CMOS address, performs ISA port I/O with delay semantics, and reads or writes one byte.

State and persistence: state is external RTC CMOS register contents; the header holds no state.

Dependencies and integration points: depends on `asm/io.h` and integrates generic RTC/CMOS code with PowerPC ISA-style port access.

Risks: only valid on machines with ISA-compatible RTC ports or platform overrides. The comment and `RTC_ALWAYS_BCD` value must match generic RTC expectations for conversion.

Test signals: read/set hardware clock on supported systems, verify CMOS alarm/status registers, and build platforms that override `RTC_PORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mce.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mce.h

Purpose: defines PowerPC machine-check event taxonomy, event storage structures, queues, notifier APIs, and Book3S 64 real-mode machine-check hooks.

Important APIs/types/functions: enums describe version, severity, disposition, initiator, error type, error class, and subtype families for UE, SLB, ERAT, TLB, user, RA, and link errors. `struct machine_check_event`, `struct mce_error_info`, and `struct mce_info` carry event data and queues. APIs include `save_mce_event`, `get_mce_event`, `release_mce_event`, `machine_check_queue_event`, `machine_check_print_event_info`, `addr_to_pfn`, `mce_common_process_ue`, notifier registration, IRQ work helpers, SLB/ERAT flush, real-mode P7/P8/P9/P10 handlers, and `mce_init`.

Control flow: early machine-check handlers classify an event, save it into per-CPU queues, possibly recover or mark fatal disposition, queue delayed processing, and notify registered consumers. Book3S 64 can run additional IRQ-context handlers and real-mode recovery paths.

State and persistence: `mce_info` holds bounded per-CPU active and delayed event queues. Event structures persist until released or printed/processed. Hardware recovery may mutate SLB/ERAT and machine-check state.

Dependencies and integration points: depends on bitops, pt_regs, notifier blocks, Book3S 64 exception code, RAS/EDAC style consumers, and KVM guest-aware printing.

Risks: queues are bounded by `MAX_MC_EVT`; overflow loses diagnostic data. Event layout and subtype interpretation affect userspace/kernel diagnostics. Real-mode handlers have strict constraints and must avoid unsafe operations.

Test signals: inject machine checks where platform supports it, test recoverable UE processing, SLB/ERAT flush recovery, notifier registration, delayed IRQ work, queue release semantics, and Book3S 64 real-mode handler coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mediabay.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mediabay.h

Purpose: defines media-bay content constants and PMAC media-bay helper APIs used by PowerBook-style removable bays.

Important APIs/types/functions: content states include `MB_FD`, `MB_FD1`, `MB_SOUND`, `MB_CD`, `MB_PCI`, `MB_POWER`, and `MB_NO`. With `CONFIG_PMAC_MEDIABAY`, it declares `check_media_bay`, `lock_media_bay`, and `unlock_media_bay`; otherwise stubs return `MB_NO` or no-op.

Control flow: drivers query bay contents and lock callbacks while initializing ATA or other bay devices. Disabled builds treat the bay as empty.

State and persistence: bay state is maintained by the media-bay implementation and hardware; this header stores none.

Dependencies and integration points: forward-declares `struct macio_dev` and integrates PMAC MacIO devices with media-bay hotplug/control code.

Risks: callers must handle transition states as `MB_NO`. Forgetting to unlock bay callbacks can block hotplug notifications. Stubs make unsupported configurations silently behave as no device.

Test signals: hot-swap media-bay devices on supported PowerBooks, verify ATA initialization lock/unlock behavior, transition handling, and no-op behavior with PMAC media bay disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mediabay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mem_encrypt.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mem_encrypt.h

Purpose: exposes PowerPC secure-guest memory encryption/decryption hooks and DMA policy.

Important APIs/types/functions: `force_dma_unencrypted(struct device *dev)` returns `is_secure_guest()`. `set_memory_encrypted()` and `set_memory_decrypted()` are declared for changing page encryption state.

Control flow: DMA mapping code can force unencrypted bounce/accessible memory for secure guests, while memory-management code calls encryption/decryption setters for page ranges.

State and persistence: encryption state is page-level platform state changed by implementation files or ultravisor/firmware interactions. This header stores no state.

Dependencies and integration points: includes `asm/svm.h` and Linux types; integrates secure virtual machine support with DMA and memory attribute management.

Risks: returning the wrong DMA policy can expose encrypted memory to devices that cannot access it or leak plaintext. Page encryption transitions must be synchronized with mappings and device access.

Test signals: secure guest boot, DMA to/from devices in secure guests, page encryption/decryption tests, and non-secure guest checks that DMA policy remains unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mem_encrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/membarrier.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/membarrier.h

Purpose: implements the PowerPC architecture hook for membarrier behavior during address-space switches.

Important APIs/types/functions: `membarrier_arch_switch_mm(prev, next, tsk)` conditionally issues `smp_mb()` when switching into an mm that has private or global expedited membarrier state and a previous mm exists.

Control flow: context-switch code calls this hook after storing `rq->curr` and before returning to userspace. Most switches return early on SMP when no expedited membarrier state is set.

State and persistence: reads `next->membarrier_state`; no state is written.

Dependencies and integration points: relies on SMP, atomic membarrier state bits, scheduler context-switch ordering, and generic membarrier syscall semantics.

Risks: missing the barrier can violate userspace membarrier guarantees. Adding unnecessary barriers can hurt context-switch performance. The `prev` check depends on kernel/userspace switch ordering documented in the comment.

Test signals: membarrier selftests, stress context switching between processes with expedited registrations, and memory-order litmus tests on SMP PowerPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/membarrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mman.h

Purpose: adds PowerPC architecture-specific mmap protection validation and VM flag calculation for SAO and memory protection keys.

Important APIs/types/functions: on PPC64 non-vDSO builds, `arch_calc_vm_prot_bits(prot, pkey)` maps `PROT_SAO` to `VM_SAO` and pkeys to VM flags; `arch_validate_prot(prot, addr)` rejects unknown bits and validates `PROT_SAO` against CPU SAO support and LPAR policy.

Control flow: mmap/mprotect paths call validation before installing VMA protections and call flag calculation when building `vm_flags`.

State and persistence: no state is stored. VMA flags persist in `vm_area_struct` after calculation.

Dependencies and integration points: includes UAPI mman, CPU feature checks, firmware features, mm, and pkeys. Integrates PowerPC-specific memory ordering attributes with generic mmap.

Risks: accepting unsupported `PROT_SAO` can create mappings with invalid semantics; rejecting valid pkey or SAO combinations can break userspace ABI. vDSO builds intentionally skip these helpers.

Test signals: mmap/mprotect tests for SAO on supported/unsupported CPUs, LPAR configurations with and without `CONFIG_PPC_PROT_SAO_LPAR`, pkeys selftests, and vDSO build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmiowb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmiowb.h

Purpose: provides PowerPC MMIO write-barrier integration for configurations using `CONFIG_MMIOWB`.

Important APIs/types/functions: `arch_mmiowb_state()` returns `&local_paca->mmiowb_state`, and `mmiowb()` maps to the full memory barrier `mb()`. The generic `mmiowb` header is included for common behavior.

Control flow: drivers or locking paths that need ordered MMIO writes invoke `mmiowb()`, which enforces ordering with a full barrier.

State and persistence: per-CPU MMIO write-barrier state lives in PACA; this header exposes its address but does not mutate it directly.

Dependencies and integration points: depends on compiler attributes, barrier primitives, PACA, and generic MMIO write-barrier infrastructure.

Risks: insufficient barriers can reorder device writes across locks; overly strong barriers can affect performance. PACA state is only available in appropriate kernel contexts.

Test signals: device-driver MMIO ordering tests, lock/unlock paths with MMIO writes, and build coverage with and without `CONFIG_MMIOWB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmiowb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmu.h

Purpose: defines PowerPC MMU feature bits, CPU-specific feature sets, page-size indexes, runtime feature checks, radix/hash selection helpers, and top-level MMU initialization hooks.

Important APIs/types/functions: feature bits include MMU family bits (`MMU_FTR_HPTE_TABLE`, 8xx, 44x, FSL_E, 47x, radix) and capabilities such as KUAP, KUEP, pkeys, GTSE, 68-bit VA, kernel RO, TLBIE variants, large pages, CI large pages, 1T segments, and NX DSI. `MMU_FTRS_POSSIBLE`, `MMU_FTRS_ALWAYS`, `early_mmu_has_feature`, `mmu_has_feature`, `mmu_clear_feature`, `radix_enabled`, `early_radix_enabled`, strict RWX helpers, page-size constants, and MMU init/cleanup declarations are central.

Control flow: early boot uses CPU specs and compile-time masks for feature detection. With jump-label feature checks, `mmu_has_feature()` becomes a static-branch lookup after initialization and falls back to early checks before that. Runtime code branches between radix and hash behavior with `radix_enabled()`.

State and persistence: active MMU feature state lives in `cur_cpu_spec->mmu_features` and optional `mmu_feature_keys[]`. PPC64 RMA size and partition table entries persist in platform MMU state. Page-size indexes are compile-time ABI within low-level handlers.

Dependencies and integration points: integrates CPU feature tables, jump labels, page table headers, Book3S 64 MMU, Book3S 32 hash MMU, nohash MMUs, kexec cleanup, partition table setup, and strict kernel/module RWX policy.

Risks: feature masks must match Kconfig and CPU specs; wrong `MMU_FTRS_ALWAYS` can remove needed runtime checks. Jump-label checks require constant single-bit arguments. Page-size indexes are used by assembly and must remain stable.

Test signals: boot hash, radix, 8xx, 44x, FSL BookE, and Book3S 32 configs; verify feature keys initialize; run TLB shootdown, hugepage, pkeys, KUAP/KUEP, strict RWX, and kexec MMU cleanup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmu_context.h

Purpose: declares and implements PowerPC mm context lifecycle, context switching, SPAPR TCE IOMMU preregistration, radix/hash switch hooks, copro/VA window accounting, KVM radix invalidation hooks, and pkey duplication/access checks.

Important APIs/types/functions: `init_new_context`, `destroy_context`, SPAPR IOMMU helpers (`mm_iommu_new`, `mm_iommu_lookup`, `mm_iommu_ua_to_hpa`, etc.), `switch_slb`, `radix__switch_mmu_context`, `switch_mmu_context`, hash context allocation/reservation/destruction, `alloc_extended_context`, `need_extra_context`, active CPU and copro counters, VAS window add/remove helpers, `do_h_rpt_invalidate_prt`, `switch_mm`, `activate_mm`, `enter_lazy_tlb` for Book3E 64, `arch_exit_mmap`, pkey hooks, and `arch_dup_mmap`.

Control flow: process creation initializes mm context; scheduler context switches disable interrupts and call `switch_mm_irqs_off`, which selects radix context switching or SLB switching. Coprocessor/VAS users increment counters to force global invalidations and decrement them after flushing on radix.

State and persistence: state lives in `mm->context`: context IDs, extended IDs, active CPU counts, copro and VAS window counters, pkey state, and optional IOMMU preregistration memory. PACA may hold current PGD in Book3E lazy TLB mode.

Dependencies and integration points: depends on scheduler, mm, spinlock, CPU features, MMU headers, SPAPR TCE IOMMU, radix/hash TLB flush, VAS/nest MMU, KVM radix invalidation, and generic mmu context code.

Risks: context switching must run with correct interrupt state. Imbalanced copro/VAS add/remove can force global flushes forever or under-flush nest MMU translations. Extended context allocation is hash-64 specific. Stub behavior must be correct on non-Book3S configurations.

Test signals: fork/exec/mmap stress, context switch with hash and radix, SPAPR VFIO/IOMMU preregistration tests, VAS/copro TLB invalidation tests, pkeys selftests, and KVM H_RPT_INVALIDATE coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmzone.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmzone.h

Purpose: provides PowerPC NUMA and memory-hotplug declarations for memory-zone management.

Important APIs/types/functions: under `CONFIG_NUMA`, declares `numa_cpu_lookup_table`, `node_to_cpumask_map`, and memory hotplug max helpers. With memory hotplug, `memory_hotplug_max()` and `hot_add_drconf_memory_max()` are external; otherwise `memory_hotplug_max()` maps to `memblock_end_of_DRAM()`.

Control flow: NUMA and hotplug code query these helpers to cap addable memory and map CPUs to nodes.

State and persistence: NUMA lookup tables and node CPU masks persist globally after topology setup. Memory hotplug limits reflect boot and dynamic reconfiguration state.

Dependencies and integration points: depends on cpumask and memblock infrastructure; integrates NUMA topology, DR memory hotplug, and memory zone sizing.

Risks: incorrect hotplug maximums can reject valid DR memory or allow invalid ranges. CPU-to-node mapping must be initialized before NUMA users query it.

Test signals: NUMA boot topology checks, CPU-node mapping validation, memory hotplug add/remove, dynamic reconfiguration memory tests, and non-NUMA fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmzone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/module.h

Purpose: defines PowerPC module architecture state, PLT/stub section requirements, TOC/GOT metadata, and dynamic ftrace module hooks.

Important APIs/types/functions: 32-bit `struct ppc_plt_entry` models a four-instruction jump stub. `struct mod_arch_specific` tracks 64-bit stubs, GOT/PCREL or TOC sections, ELFv1 OPD ranges, 32-bit PLT sections, ftrace trampolines, and optional out-of-line ftrace stubs. Module builds create `.stubs`, `.mygot`, `.plt`, or `.init.plt` sections as needed. `module_trampoline_target` and `module_finalize_ftrace` support dynamic ftrace.

Control flow: module loader fills arch-specific fields while resolving relocations and creating stubs/PLTs. Ftrace finalization analyzes or creates trampolines after load.

State and persistence: per-module `mod_arch_specific` persists while the module is loaded. Stub/PLT/GOT/TOC sections are allocated in module memory.

Dependencies and integration points: depends on generic module infrastructure, PowerPC relocation code, ELF ABI v1/v2, PC-relative kernel support, and dynamic ftrace.

Risks: 32-bit relative branch range limitations require correct PLT generation. 64-bit TOC/GOT metadata is ABI-sensitive. Ftrace trampoline target resolution must not misidentify module code.

Test signals: load/unload modules on 32-bit and 64-bit PowerPC, exercise far-call relocations, ELFv1 OPD modules, PCREL builds, dynamic ftrace enable/disable, and module strict RWX checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/module.lds.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/module.lds.h

Purpose: supplies the PowerPC module linker-script fragment that aligns the `.toc` output section.

Important APIs/types/functions: the `SECTIONS` fragment creates `.toc 0 : ALIGN(256)` and collects `*(.got .toc)`.

Control flow: no runtime flow; module linking applies this script fragment.

State and persistence: the module image contains aligned GOT/TOC data used at runtime by relocated code.

Dependencies and integration points: integrates with module linker invocation and PowerPC TOC/GOT relocation ABI.

Risks: incorrect TOC alignment can break TOC-relative addressing or ABI assumptions in module code.

Test signals: build loadable modules, inspect section alignment with `readelf`, and load modules that use TOC/GOT references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/module.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc5121.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc5121.h

Purpose: defines MPC512x reset, clock, local bus, and LPB FIFO register layouts plus LPB FIFO request APIs.

Important APIs/types/functions: register maps include `struct mpc512x_reset_module`, `struct mpc512x_ccm`, `struct mpc512x_lpc`, and `struct mpc512x_lpbfifo`. Macros define SCLPC start, chip-select, flush/read, DAI/BPT, reset, interrupt enable, success, FIFO control, and alarm bits. `enum lpb_dev_portsize`, `enum mpc512x_lpbfifo_req_dir`, `struct mpc512x_lpbfifo_request`, `mpc512x_cs_config`, and `mpc512x_lpbfifo_submit` form the API.

Control flow: board or driver code configures chip-select timing, builds an LPB FIFO request with device physical address, RAM virtual address, transfer size, port width, direction, and optional callback, then submits it to the FIFO engine.

State and persistence: hardware register state persists in reset/clock/LPC/FIFO modules until reset or reconfiguration. Request objects are caller-owned until callback/completion.

Dependencies and integration points: integrates MPC512x platform code, local bus devices, FIFO/DMA-like transfers, and clock/reset setup.

Risks: register layout must match the SoC manual exactly. LPB FIFO requests need valid physical/virtual addresses, compatible port width, and lifetime long enough for asynchronous completion.

Test signals: boot MPC512x boards, configure LPC chip selects, perform LPB FIFO read/write transfers for each supported port size, verify callbacks and interrupt paths, and test reset/clock register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc5121.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc52xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc52xx.h

Purpose: provides Freescale MPC5200/MPC52xx SoC constants, register maps, platform setup APIs, interrupt/timer helpers, PCI setup, and suspend hooks.

Important APIs/types/functions: defines SVR values for MPC5200 and MPC5200B; maps memory controller, SDRAM, SDMA, GPT, GPIO, wakeup GPIO, XLB, CDM, and interrupt controller registers. APIs include common device mapping/declaration, XLB arbiter setup, PSC AC97 GPIO reset, PSC clock divider setup, restart, GPT lookup/start/period/stop, IRQ init/get, optional PCI bridge setup, and PM hooks through `struct mpc52xx_suspend`.

Control flow: platform boot maps common devices, configures bus arbitration/clocks/GPIO, initializes IRQ controller and optional PCI, and later drivers use GPT and PSC helpers. PM code calls board-specific suspend prepare/resume finish callbacks.

State and persistence: SoC register values persist in MMIO hardware. GPT private objects, suspend callback table, and saved SRAM buffer persist in platform implementation.

Dependencies and integration points: depends on `mpc5xxx.h`, suspend definitions, device tree nodes, PCI, IRQ, timer, and platform device registration.

Risks: register structs are hardware ABI; padding and widths must be exact. PCI and PM hooks compile conditionally. Clock divider or GPIO misconfiguration can break serial/audio/AC97 devices.

Test signals: boot MPC5200 and MPC5200B boards, verify OF platform devices, GPT timers, IRQ routing, PCI bridge setup, PSC clocking, restart path, and suspend/resume where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc52xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc52xx_psc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc52xx_psc.h

Purpose: defines Programmable Serial Controller register bits and layouts shared by MPC52xx/MPC512x UART, AC97, IR, I2S, SPI, and FIFO drivers.

Important APIs/types/functions: macros cover status, command, FIFO status, interrupt mask/status, input/output port bits, mode register fields, and SICR protocol bits. `struct mpc52xx_psc`, `struct mpc52xx_psc_fifo`, `struct mpc512x_psc_fifo`, and `struct mpc5125_psc` map hardware blocks. `MPC52xx_PSC_MAXNUM` depends on MPC512x support.

Control flow: drivers program mode/command/status/SICR fields for the selected protocol, then move data through typed buffer/FIFO registers and handle interrupt/FIFO status bits.

State and persistence: PSC hardware registers hold protocol, FIFO, interrupt, and port state. This header holds no software state.

Dependencies and integration points: includes PowerPC types and is consumed by serial, audio, infrared, SPI, and platform code for MPC52xx/MPC512x PSCs.

Risks: multiple SoC generations have different FIFO/register layouts; using the wrong struct corrupts register access. Comments note hardware byte-swapping behavior for CCR fields that drivers must respect.

Test signals: UART console, AC97/I2S audio, SPI/IR where available, FIFO underrun/overrun handling, interrupt mask/status tests, and builds for MPC52xx, MPC512x, and MPC5125 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc52xx_psc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc5xxx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc5xxx.h

Purpose: exposes a common MPC5xxx bus-frequency lookup helper for firmware-node and device users.

Important APIs/types/functions: `mpc5xxx_fwnode_get_bus_frequency(struct fwnode_handle *fwnode)` is declared; `mpc5xxx_get_bus_frequency(struct device *dev)` passes `dev_fwnode(dev)` to it.

Control flow: drivers call the device helper, which delegates to firmware-node parsing.

State and persistence: no state; frequency comes from firmware properties or platform implementation.

Dependencies and integration points: depends on Linux property/fwnode APIs and integrates MPC5xxx platform clocks with drivers.

Risks: missing or malformed firmware properties can yield incorrect bus rates and misprogram devices.

Test signals: device tree/fwnode bus-frequency parsing tests, driver probe on MPC5xxx boards, and clock-dependent UART/PSC timing validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc5xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc6xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc6xx.h

Purpose: declares the MPC6xx standby entry routine.

Important APIs/types/functions: `mpc6xx_enter_standby(void)`.

Control flow: platform idle or power-management code calls the routine to place an MPC6xx CPU into standby.

State and persistence: CPU power state changes in hardware; no software state is defined here.

Dependencies and integration points: integrates classic PowerPC 6xx platform power-management code with CPU-specific low-power assembly/C implementation.

Risks: standby entry must preserve enough CPU/platform state for resume; calling it on unsupported processors can hang.

Test signals: suspend/idle tests on MPC6xx-class hardware and build checks for platforms referencing the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc6xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc85xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc85xx.h

Purpose: defines MPC85xx/QorIQ system version register decoding helpers and SoC version constants.

Important APIs/types/functions: `SVR_REV`, `SVR_MAJ`, `SVR_MIN`, and `SVR_SOC_VER` extract revision and SoC identity. Constants enumerate many 85xx, P-series, T-series, C29x, B/G-series, 86xx, and unknown SVR values.

Control flow: platform detection reads the hardware SVR, applies `SVR_SOC_VER()` and revision helpers, and compares against constants to select errata/workarounds or board behavior.

State and persistence: no state; SVR is read from CPU/SoC hardware elsewhere.

Dependencies and integration points: used by Freescale/QorIQ platform setup, CPU detection, errata handling, and device initialization.

Risks: incorrect constants or masks misidentify SoCs and can enable wrong errata workarounds. Some constants use uppercase `0X` but remain valid C constants.

Test signals: boot each supported SoC family where available, verify `/proc/cpuinfo`/platform detection, errata selection, and build-time users of every SVR constant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc85xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic.h

Purpose: defines the OpenPIC/MPIC register map, controller instance state, flags, and public APIs for PowerPC interrupt-controller initialization, masking, EOI, IPI, timer, MSI, and machine-check interrupt handling.

Important APIs/types/functions: register macros cover global, timer, per-CPU, per-source, Freescale, and TSI108 variants. `enum mpic_reg_type`, `struct mpic_reg_bank`, `struct mpic_irq_save`, and `struct mpic` model access type, mapped register banks, saved IRQ state, irq domains/chips, ISUs, vectors, protected sources, MSI bitmap, shadows, and PM save data. APIs include `mpic_alloc`, `mpic_assign_isu`, `mpic_init`, priority setters, CPU setup/teardown, IPI request/send, mask/unmask/EOI, and interrupt fetch helpers.

Control flow: platform code allocates an MPIC object, optionally assigns ISUs, initializes hardware, sets up CPU priority/IPIs, and generic IRQ code calls mask/unmask/end and interrupt fetch routines. SMP paths send IPIs through MPIC dispatch registers.

State and persistence: controller state persists in `struct mpic`, irq domains/chips, mapped MMIO/DCR banks, MSI bitmap, protected-source map, vector arrays, and hardware registers. PM save data persists across suspend.

Dependencies and integration points: depends on Linux IRQ core, DCR, MSI bitmap, device tree, SMP, PCI MSI, PM, and platform-specific weird register sets such as TSI108 and U3 HT fixups.

Risks: register offsets vary by implementation and endianness. Flags such as `MPIC_SECONDARY`, `MPIC_USES_DCR`, `MPIC_FSL`, and `MPIC_ENABLE_COREINT` radically change behavior. Incorrect vector, sense, or destination programming can lose interrupts or route them to wrong CPUs.

Test signals: boot MPIC platforms, verify IRQ domain mapping, external IRQ delivery, IPIs, CPU hotplug setup/teardown, MSI allocation, FSL error interrupts, suspend/resume save/restore, and TSI108/U3 variant coverage where hardware exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic_msgr.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic_msgr.h

Purpose: declares MPIC message-register allocation/control APIs and inline register accessors.

Important APIs/types/functions: `struct mpic_msgr` stores base register pointer, message-enable register pointer, IRQ, in-use flag, lock, and register number. APIs include `mpic_msgr_get`, `mpic_msgr_put`, `mpic_msgr_enable`, `mpic_msgr_disable`, `mpic_msgr_write`, `mpic_msgr_read`, `mpic_msgr_clear`, `mpic_msgr_set_destination`, and `mpic_msgr_get_irq`.

Control flow: clients acquire a message register, set destination CPU, enable it, write a 32-bit message to trigger an interrupt, read/clear it in the handler, then disable and release it.

State and persistence: message-register allocation state is tracked by `in_use` and protected by `lock` in implementation. Hardware message, enable, destination, and IRQ state persists in MPIC registers.

Dependencies and integration points: depends on spinlocks, SMP hard CPU IDs, big-endian MMIO accessors, and MPIC interrupt routing.

Risks: destination uses hardware CPU numbering derived from Linux CPU IDs; wrong mapping misroutes messages. Reading clears interrupts, so handlers must preserve message values before acknowledging.

Test signals: allocate all valid message registers, verify busy/error paths, send messages between CPUs, confirm IRQ clearing on read, and test hotplug destination remapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic_msgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic_timer.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic_timer.h

Purpose: declares MPIC global timer request, start/stop, remaining-time, and free APIs with stubs when timer support is disabled.

Important APIs/types/functions: `struct mpic_timer` stores client device pointer, cascade handle, timer number, and IRQ. Enabled builds declare `mpic_request_timer`, `mpic_start_timer`, `mpic_stop_timer`, `mpic_get_remain_time`, and `mpic_free_timer`; disabled builds return `NULL` or no-op.

Control flow: clients request a timer with an IRQ handler and period, start/stop it, query remaining time, and free it when done.

State and persistence: timer allocation and cascade state live in implementation and MPIC hardware registers. The handle persists while the timer is reserved.

Dependencies and integration points: depends on interrupt handlers and `time64_t`; integrates drivers with MPIC global timer hardware.

Risks: the disabled stubs are non-static function definitions in the header, so duplicate-definition risk depends on inclusion/build context. Clients must handle `NULL` request results.

Test signals: build with and without `CONFIG_MPIC_TIMER`, request timers, validate interrupt firing and remaining-time calculations, and confirm clients tolerate disabled support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/msi_bitmap.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/msi_bitmap.h

Purpose: defines a bitmap allocator for PowerPC hardware MSI interrupt numbers.

Important APIs/types/functions: `struct msi_bitmap` contains an OF node, bitmap pointer, spinlock, IRQ count, and ownership flag. APIs allocate/free hardware IRQ ranges, reserve individual hwirqs, reserve device-tree-described hwirqs, allocate/init the bitmap, and free it.

Control flow: MSI controller setup initializes the bitmap, reserves unavailable or firmware-described interrupts, then drivers allocate/free contiguous hwirq ranges for MSI vectors under lock.

State and persistence: bitmap bits persist as allocation state for the controller lifetime. `bitmap_from_slab` records whether the bitmap memory should be freed.

Dependencies and integration points: depends on OF and PowerPC IRQ types; used by MPIC and other MSI-capable interrupt controllers.

Risks: allocation/free range errors can double-allocate MSI vectors or leak them. Device-tree reservations must be applied before drivers allocate vectors.

Test signals: MSI allocation/free stress, multi-vector allocation, device-tree reservation tests, lockdep under concurrent MSI users, and MPIC MSI interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/msi_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nmi.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nmi.h

Purpose: declares PowerPC NMI/watchdog hooks and hypervisor nonrecoverable NMI checking.

Important APIs/types/functions: with `CONFIG_PPC_WATCHDOG`, declares `soft_nmi_interrupt(struct pt_regs *regs)` and `watchdog_hardlockup_set_timeout_pct(u64 pct)`; otherwise the timeout setter is a no-op. `hv_nmi_check_nonrecoverable(struct pt_regs *regs)` is always declared.

Control flow: watchdog/NMI exception code calls the soft NMI handler and hypervisor nonrecoverable checker from NMI context.

State and persistence: watchdog timeout percentage is maintained by implementation; this header has no storage.

Dependencies and integration points: integrates PowerPC exception code, hardlockup watchdog, and hypervisor NMI handling.

Risks: NMI context has severe locking and reentrancy constraints. Disabled watchdog builds must not assume `soft_nmi_interrupt` exists.

Test signals: hardlockup watchdog tests, injected soft NMI paths, hypervisor nonrecoverable NMI handling, and builds with/without `CONFIG_PPC_WATCHDOG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/hugetlb-8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/hugetlb-8xx.h

Purpose: implements 32-bit 8xx nohash hugepage architecture hooks.

Important APIs/types/functions: `PAGE_SHIFT_8M` defines 8 MiB hugepage shift. Helpers include `flush_hugetlb_page`, `check_and_get_huge_psize`, `set_huge_pte_at`, `huge_ptep_get`, `huge_pte_clear`, `huge_ptep_set_wrprotect`, and 4K-page-only `arch_make_huge_pte`.

Control flow: hugetlb code flushes TLBs through normal page flush, maps shifts to MMU page sizes, sets/gets/clears huge PTEs, write-protects entries through `pte_update`, and for 4K base pages marks 16K or larger huge PTEs with `_PAGE_SPS`/`_PAGE_HUGE`.

State and persistence: mutates page-table entries for huge mappings; no independent state.

Dependencies and integration points: depends on 8xx page-table helpers such as `ptep_is_8m_pmdp`, `pte_offset_kernel`, `ptep_get`, `pte_update`, and hugepage MMU page-size conversion.

Risks: 8 MiB huge PTEs may be represented at PMD-like locations, so `huge_ptep_get()` must adjust for aligned addresses. Wrong `_PAGE_SPS`/`_PAGE_HUGE` selection breaks 8xx TLB loading.

Test signals: hugetlbfs tests on PPC 8xx, 16K and 8M hugepage mappings, write-protect/COW behavior, TLB flush correctness, and 4K base-page build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/hugetlb-8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/kup-8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/kup-8xx.h

Purpose: implements 8xx kernel user access protection (KUAP) helpers using the MD_AP special-purpose register.

Important APIs/types/functions: when `CONFIG_PPC_KUAP` is enabled, helpers include `__kuap_save_and_lock`, `kuap_user_restore`, `__kuap_kernel_restore`, optional debug `__kuap_get_and_assert_locked`, `uaccess_begin_8xx`, `uaccess_end_8xx`, `allow_user_access`, `prevent_user_access`, `prevent_user_access_return`, `restore_user_access`, and `__bad_kuap_fault`.

Control flow: exception entry saves current MD_AP and locks user access; explicit uaccess windows write MD_AP to allow or prevent access; fault handling checks saved KUAP bits to classify protection faults.

State and persistence: KUAP state is the hardware `SPRN_MD_AP` register plus saved `regs->kuap` in exception frames.

Dependencies and integration points: depends on bug/WARN helpers, MMU feature patching, `asm/reg.h`, 8xx MD_AP constants, and user access/fault code.

Risks: incorrect MD_AP writes can leave user memory accessible in kernel or block legitimate copy_to/from_user. Debug assertions only check upper access-protection bits. Inline assembly is patched by MMU feature bits and must match register constraints.

Test signals: KUAP selftests, copy_to/from_user under enabled/disabled windows, bad user access fault tests, debug assertion coverage, and 8xx builds without KUAP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/kup-8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-44x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-44x.h

Purpose: defines 44x/47x software-loaded TLB bit fields, context type, early TLB reservations, page-size selections, and patch-site symbols for nohash 32-bit MMU code.

Important APIs/types/functions: macros cover MMUCR TID/STS, 44x TLB word indexes and EPN/RPN/ERPN/attribute/permission/page-size bits, 47x TLB0/TLB1/TLB2 equivalents, `PPC44x_TLB_SIZE`, `mm_context_t`, `tlb_44x_hwater`, `tlb_44x_index`, patch symbols, early debug TLB constants, `PPC_PIN_SIZE`, selected `PPC44x_TLBE_SIZE`, `PPC47x_TLBE_SIZE`, `mmu_virtual_psize`, `mmu_linear_psize`, and PGD/PTE assembly offset masks.

Control flow: low-level TLB miss/refill and setup code uses these constants to compose TLB entries, track high-water/index state, reserve early debug mappings, and pin lowmem mappings.

State and persistence: runtime state includes TLB entries, software high-water/index variables, mm context IDs, active flags, and vDSO pointer. Hardware TLB state persists until invalidated or overwritten.

Dependencies and integration points: depends on `asm-const.h`, selected page-size Kconfig, nohash MMU handlers, early debug, and vDSO context management.

Risks: bit definitions are hardware ABI; mismatched 44x/47x formats cause translation faults. Unsupported `PAGE_SIZE` triggers a build error. Early debug consumes an extra TLB entry and changes available pinned mappings.

Test signals: boot 44x and 47x kernels with supported page sizes, run TLB miss/refill stress, early debug mapping tests, vDSO mapping checks, and lowmem pinning validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-44x.h -->
