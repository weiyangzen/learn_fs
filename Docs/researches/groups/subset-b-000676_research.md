# subset-b-000676 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kernel-pgtable.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kernel-pgtable.h

### Purpose
`kernel-pgtable.h` calculates the early ARM64 kernel and identity-map page table footprint. It is boot-time compile glue used before the full MM subsystem is available, not Ceph client logic directly.

### Important APIs, Types, And Functions
Key exported constants/macros include `SWAPPER_BLOCK_SHIFT`, `SWAPPER_SKIP_LEVEL`, `SWAPPER_PGTABLE_LEVELS`, `IDMAP_VA_BITS`, `IDMAP_LEVELS`, `IDMAP_ROOT_LEVEL`, `SPAN_NR_ENTRIES`, `EARLY_ENTRIES`, `EARLY_LEVEL`, `EARLY_PAGES`, `INIT_DIR_SIZE`, `INIT_IDMAP_DIR_SIZE`, and FDT/idmap extra-page counts. It depends on `_end`, `kimage_limit`, `KIMAGE_VADDR`, `MAX_FDT_SIZE`, `CONFIG_PGTABLE_LEVELS`, `CONFIG_ARM64_4K_PAGES`, `CONFIG_RELOCATABLE`, and `CONFIG_UNMAP_KERNEL_AT_EL0`.

### Control Flow
There is no runtime control flow. The preprocessor selects page-table levels and sizes, then early assembly/C boot code consumes the constants when allocating initial swapper and idmap page tables.

### State, Persistence, And Dependencies
The header has no persistent state; it describes memory reservations for transient early page tables. It includes `asm/boot.h`, `asm/pgtable-hwdef.h`, and `asm/sparsemem.h`.

### Integration Points
It integrates with ARM64 head/boot page-table construction and the kernel image layout. Ceph is affected indirectly because all later filesystem, networking, and page-cache code depends on these mappings being correct.

### Risks
Wrong sizing causes early boot memory overwrite, missing idmap/FDT coverage, or page-table allocation underrun. Configuration-specific branches create risk around 4K pages, relocation, KASLR, and KPTI.

### Test Signals
Cross-build ARM64 page-size and VA-level combinations; boot with relocation/KASLR/KPTI enabled; validate early page table allocation bounds and boot-time FDT access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kernel-pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kexec.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kexec.h

### Purpose
`kexec.h` defines ARM64 kexec and crash-kernel architecture limits, register capture helpers, restart entry points, and image metadata used to boot a replacement kernel or crash dump kernel.

### Important APIs, Types, And Functions
It exports `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`, `KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`, `crash_setup_regs()`, crash nosave/suspend hooks, `cpu_soft_restart()`, `machine_kexec_post_load()`, `struct kimage_arch`, `kexec_image_ops`, `arch_kimage_file_post_load_cleanup()`, and `load_other_segments()`.

### Control Flow
Normal kexec code prepares `struct kimage`, fills ARM64-specific fields, and later calls the soft restart path with entry, DTB, and boot parameters. Crash paths snapshot current or supplied `pt_regs`, avoid crash-reserved PFNs, and preserve resume/suspend handoff state when crash dump support is enabled.

### State, Persistence, And Dependencies
State is carried in `struct kimage_arch` fields such as DTB memory, EL2 vectors, head buffer, and kernel segment handles. It depends on UAPI kexec constants, `pt_regs`, crash dump configuration, and arm64 restart assembly.

### Integration Points
The generic kexec core, crash dump code, EFI/image loader, and ARM64 CPU reset code consume these declarations. Distributed filesystem workloads depend on this for crash collection rather than normal I/O.

### Risks
Register snapshot mistakes corrupt vmcore diagnostics. Bad segment limits or DTB placement can make the second kernel unbootable. EL2/vector handoff is sensitive to virtualization mode.

### Test Signals
Build `CONFIG_KEXEC`, `CONFIG_KEXEC_FILE`, and `CONFIG_CRASH_DUMP`; perform kexec and kdump boots on VHE/nVHE systems; inspect crash registers and reserved-memory freeing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kfence.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kfence.h

### Purpose
`kfence.h` provides ARM64 KFENCE hooks for protecting guard pages and deciding whether direct-map permissions can be changed early enough for the KFENCE pool.

### Important APIs, Types, And Functions
It exports `kfence_protect_page()`, `arm64_kfence_can_set_direct_map()`, `kfence_early_init`, and `arch_kfence_init_pool()` when KFENCE is enabled. The page protection path wraps `set_memory_valid()`.

### Control Flow
KFENCE calls `kfence_protect_page()` to invalidate or restore a direct-map page. If early direct-map mutation is available, `arch_kfence_init_pool()` initializes protected pool mappings; otherwise the inline fallback reports unsupported.

### State, Persistence, And Dependencies
State is limited to `kfence_early_init` and page-table permissions. It depends on `asm/set_memory.h`, KFENCE configuration, and direct-map page attribute management.

### Integration Points
The generic KFENCE allocator uses this header to install guard pages on ARM64. It is a diagnostic safety layer for kernel allocations used by filesystems, networking, and drivers.

### Risks
Incorrect direct-map permission updates can leave guard pages accessible or break legitimate kernel access. Early boot ordering is sensitive because KFENCE may initialize before full mapping APIs are ready.

### Test Signals
Boot with `CONFIG_KFENCE`; trigger KFENCE allocation faults; verify guard pages fault and unprotect cleanly; test early and non-early initialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kgdb.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kgdb.h

### Purpose
`kgdb.h` defines ARM64 KGDB breakpoint, single-step, fault, and register-packet layout support for kernel remote debugging.

### Important APIs, Types, And Functions
It exports `arch_kgdb_breakpoint()`, `kgdb_handle_bus_error()`, `kgdb_fault_expected`, `kgdb_brk_handler()`, `kgdb_compiled_brk_handler()`, `kgdb_single_step_handler()`, register counts (`_GP_REGS`, `_FP_REGS`, `_EXTRA_REGS`), `DBG_MAX_REG_NUM`, `BUFMAX`, and `NUMREGBYTES`.

### Control Flow
Debug break instructions trap into KGDB handlers. Optional software single-step support routes debug exceptions to `kgdb_single_step_handler()`. Register transfer sizes define how CPU and FP state are serialized to the remote protocol.

### State, Persistence, And Dependencies
The only declared mutable state is `kgdb_fault_expected`; runtime state lives in `pt_regs`, debug monitor state, and KGDB core buffers. It includes `linux/ptrace.h` and `asm/debug-monitors.h`.

### Integration Points
KGDB core, exception handlers, debug monitor code, and architecture register serializers depend on this contract. It helps debug kernel faults that can include Ceph client paths.

### Risks
Register layout drift breaks remote debugging. Incorrect breakpoint encoding or single-step behavior can recurse in exception context. Fault expectation handling must not hide real faults.

### Test Signals
Build and boot with KGDB; connect gdb, set breakpoints, single-step, inspect general/FP registers; test bus-error recovery and compiled breakpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kprobes.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kprobes.h

### Purpose
`kprobes.h` declares ARM64 kprobe and kretprobe control state, trampoline hooks, and breakpoint handlers used for dynamic kernel instrumentation.

### Important APIs, Types, And Functions
Key items are `__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot()`, `kretprobe_blacklist_size`, `struct prev_kprobe`, `struct kprobe_ctlblk`, `arch_remove_kprobe()`, `kprobe_fault_handler()`, `__kretprobe_trampoline()`, `trampoline_probe_handler()`, and BRK handlers for kprobe, single-step, and kretprobe.

### Control Flow
Kprobe insertion copies/patches probed instructions and routes BRK exceptions to architecture handlers. Return probes use the trampoline path to recover saved return state. Fault handling decides whether an exception belongs to an active probe.

### State, Persistence, And Dependencies
Per-CPU probe state lives in `struct kprobe_ctlblk`, including current and previous probes. It depends on generic kprobes, `pt_regs`, `percpu`, and `asm/probes.h`.

### Integration Points
Tracing, perf, ftrace-like diagnostics, and live debugging tools depend on these hooks. Ceph client functions can be instrumented through this architecture layer.

### Risks
Instruction-slot sizing, exception recursion, and return-address restoration are high risk. Probing code that is not kprobe-safe can deadlock or corrupt context.

### Test Signals
Run kprobe/kretprobe selftests on ARM64; probe normal and faulting paths; verify blacklisted/trampoline behavior and nested probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_arm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_arm.h

### Purpose
`kvm_arm.h` centralizes ARM64 KVM architectural register bit definitions and derived constants for EL2 control, stage-2 translation, exception decoding, and hypervisor mode naming.

### Important APIs, Types, And Functions
It defines aliases and masks for `HCR_EL2`, `TCR_EL2`, `VTCR_EL2`, `VTTBR_EL2`, `HSTR_EL2`, `CPTR_EL2`, `HCRX_EL2`, HPFAR/PAR conversion, `HCR_GUEST_FLAGS`, host VHE/nVHE flags, `VTCR_EL2_LVLS_TO_SL0()`, `VTCR_EL2_IPA()`, `ARM64_VTTBR_X()`, `PAR_TO_HPFAR()`, `FAR_TO_FIPA_OFFSET()`, plus `kvm_arm_exception_class` and `kvm_mode_names`.

### Control Flow
The header is compile-time data. KVM initialization builds EL2 control values from these masks; world-switch code programs them before entering or leaving guests; abort handling decodes syndrome/fault addresses through the conversion macros.

### State, Persistence, And Dependencies
No storage is declared. State exists in EL2 system registers programmed by callers. Dependencies are `asm/esr.h`, `asm/memory.h`, `asm/sysreg.h`, and generic bitfield helpers.

### Integration Points
Included by KVM host, hyp assembly, MMU, nested virtualization, and emulation code. It defines the hardware vocabulary for guest execution.

### Risks
Bit drift against architectural definitions can silently misprogram EL2. VTCR/VTTBR sizing mistakes break stage-2 walks or VMID isolation. Feature-gated bits must match CPU capability probing.

### Test Signals
KVM selftests for VM creation, IPA sizes, nested/vhe/nvhe modes, exception exits, and TLB invalidation; compare generated constants against ARM ARM/sysreg definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_asm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_asm.h

### Purpose
`kvm_asm.h` is the ABI between C code and ARM64 KVM hypervisor assembly. It names exception codes, SMCCC hypercalls, hyp symbols, per-CPU hyp data accessors, init parameter blocks, and low-level hyp entry points.

### Important APIs, Types, And Functions
Notable exports include `ARM_EXCEPTION_*`, `KVM_HOST_SMCCC_FUNC()`, `enum __kvm_host_smccc_func`, symbol-selection macros (`DECLARE_KVM_*_SYM`, `CHOOSE_*_SYM`, `kvm_nvhe_sym`), `struct kvm_nvhe_init_params`, `struct kvm_nvhe_stacktrace_info`, `__kvm_flush_*`, `__kvm_tlb_flush_*`, `__kvm_at_*`, `__kvm_vcpu_run()`, `__kvm_adjust_pc()`, hyp panic handlers, PSCI entry points, and CPU context offsets for assembly.

### Control Flow
EL1 uses SMCCC/HVC calls for nVHE hyp services; VHE may call functions directly. Hyp assembly uses the declared symbols and offsets to save/restore CPU context, run vCPUs, perform TLB maintenance, and handle unexpected EL2 traps.

### State, Persistence, And Dependencies
State includes nVHE init params, per-CPU hyp bases, stacktrace info, and hyp-only symbol addresses. It depends on hyp image/linker naming, `asm/insn.h`, `asm/virt.h`, `asm/sysreg.h`, and generated offsets.

### Integration Points
KVM world switch, pKVM, hyp initialization, PSCI, TLB invalidation, GIC virtualization, and backtrace/panic paths all consume this header.

### Risks
C/assembly ABI drift is severe: bad offsets corrupt register state. Symbol choice macros must prevent illegal VHE/nVHE references. SMCCC function numbering is an ABI with hyp code.

### Test Signals
Build VHE, nVHE, and pKVM configs; run KVM selftests, hyp panic/backtrace tests, vCPU run loops, and TLB invalidation stress; inspect generated asm offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_define_hypevents.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_define_hypevents.h

### Purpose
`kvm_define_hypevents.h` adapts KVM hyp event declarations into the remote trace event generator.

### Important APIs, Types, And Functions
It defines `REMOTE_EVENT_INCLUDE_FILE`, `REMOTE_EVENT_SECTION`, `HE_STRUCT`, `HE_PRINTK`, `he_field`, `HYP_EVENT()`, and `HYP_EVENT_MULTI_READ`, then includes `trace/define_remote_events.h`.

### Control Flow
Trace event generation includes this file to transform `HYP_EVENT` declarations in `kvm_hypevents.h` into remote event metadata placed in `_hyp_events`.

### State, Persistence, And Dependencies
There is no runtime state. The persistent output is generated trace metadata in the built kernel image. Dependencies are the trace remote-event generator and `kvm_hypevents.h`.

### Integration Points
Connects ARM64 KVM hyp tracepoints to the Linux trace infrastructure, especially for events emitted from EL2.

### Risks
Macro signature drift breaks trace generation. Section name or include mismatch can make hyp events invisible.

### Test Signals
Build with hyp tracing enabled; inspect generated event formats; enable/read KVM hyp trace events under ftrace/tracefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_define_hypevents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_emulate.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_emulate.h

### Purpose
`kvm_emulate.h` provides inline helpers and prototypes for ARM64 KVM guest instruction emulation, exception injection, syndrome decoding, endian conversion, PC advancement, nested exception handling, and trap-control setup.

### Important APIs, Types, And Functions
It defines vector offsets, `enum exception_type`, exception injection APIs (`kvm_inject_*`, nested variants), `vcpu_reset_hcr()`, register accessors (`vcpu_pc`, `vcpu_cpsr`, `vcpu_get_reg`, `vcpu_set_reg`), context classifiers (`vcpu_is_el2`, `is_hyp_ctxt`, `is_nested_ctxt`), ESR/FAR/HPFAR decoders, data-abort helpers, endian conversion helpers, `kvm_incr_pc()`, `kvm_pend_exception()`, CPTR trap helpers, and `vcpu_set_hcrx()`.

### Control Flow
Exit handlers read `vcpu->arch.fault`, classify the trap, optionally emulate memory/register effects, inject guest exceptions, and set `INCREMENT_PC` or `PENDING_EXCEPTION` flags. Nested virtualization paths translate host-visible traps into virtual EL2 exceptions or state updates.

### State, Persistence, And Dependencies
State is held in `struct kvm_vcpu_arch`: HCR/HCRX, sysregs, flags, fault info, and virtual SError ESR. It depends on ESR/sysreg definitions, `kvm_host.h`, `kvm_nested.h`, debug monitors, and CPU feature predicates.

### Integration Points
Used by MMIO emulation, abort handling, sysreg trapping, nested virtualization, debug paths, and world-switch preparation.

### Risks
Incorrect ESR decoding can misclassify writes, instruction aborts, or permission faults. PC increment and pending-exception flags intentionally conflict and must not be combined. Endian and AArch32 banked register handling are subtle.

### Test Signals
Run KVM selftests for MMIO, sysreg traps, WFI/WFE, SError/SEA injection, AArch32 guests, big-endian guests, and nested EL2 traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_emulate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_host.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_host.h

### Purpose
`kvm_host.h` is the main ARM64 KVM host architecture contract. It defines VM/vCPU architecture state, stage-2 MMU state, hypervisor memory caches, sysreg storage, feature flags, debug/FP ownership, pKVM state, request numbers, and host-facing KVM APIs.

### Important APIs, Types, And Functions
Major types include `enum kvm_mode`, `struct kvm_hyp_memcache`, `struct kvm_s2_mmu`, `struct kvm_arch`, `struct kvm_cpu_context`, `struct kvm_host_data`, `struct kvm_vcpu_arch`, `struct vcpu_reset_state`, `struct kvm_sysreg_masks`, `struct fgt_masks`, `struct kvm_vm_stat`, and `struct kvm_vcpu_stat`. Important helpers cover hyp memcache push/pop/top-up/free, MPIDR indexing, sysreg read/write/masking, vCPU flag accessors, hyp calls, debug ownership, PV time, VMID allocation, SVE/PAuth/MTE feature checks, ID-register access, and FGT grouping.

### Control Flow
VM creation allocates `struct kvm_arch`, initializes stage-2 MMU, VGIC/timer/PMU state, ID registers, and pKVM metadata. vCPU creation initializes `struct kvm_vcpu_arch`, feature flags, sysregs, debug/FP state, and MMU caches. Run paths load host data, select hardware MMU, call VHE directly or nVHE through SMCCC, then handle exits through declared trap handlers.

### State, Persistence, And Dependencies
The file describes durable in-memory VM/vCPU state for the lifetime of a KVM VM, plus per-CPU host data. It has no filesystem persistence. It depends on generic KVM, VGIC, arch timer, PMU, PSCI, maple tree filters, SMCCC, `kvm_asm.h`, FPSIMD/SVE, and CPU feature infrastructure.

### Integration Points
Almost every ARM64 KVM implementation file includes this header. It bridges userspace ioctls, generic KVM core, EL2 hyp code, pKVM, nested virtualization, performance/debug subsystems, and guest memory management.

### Risks
This is a high-blast-radius ABI surface. Flag accessor misuse can race with vCPU load/put. Sysreg enum ordering and VNCR offsets must stay synchronized. Shared/canonical stage-2 MMUs need correct refcount and pending-unmap handling. pKVM state transitions must prevent use-after-teardown.

### Test Signals
Run full ARM64 KVM selftests, nested virtualization tests, pKVM boot tests, VMID rollover stress, SVE/PAuth/MTE feature exposure tests, PMU/debug tests, and userspace register ioctl round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyp.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyp.h

### Purpose
`kvm_hyp.h` declares helpers used inside ARM64 KVM hypervisor code for host context access, timer/sysreg handling, VGIC, debug, FP/SVE, pKVM and hyp memory services.

### Important APIs, Types, And Functions
The file declares hyp entry helpers such as `__host_enter()`, `__guest_enter()`, `__fpsimd_*`, `__debug_*`, `__vgic_*`, `__timer_*`, `__sysreg_*`, `__pkvm_*`, `__hyp_*` helpers, and accessors for host context/sysregs depending on VHE/nVHE build mode.

### Control Flow
World-switch code calls these helpers around guest entry/exit to save host state, restore guest state, program timers/GIC/debug registers, and perform protected hypervisor operations. Many calls are only valid while executing at EL2.

### State, Persistence, And Dependencies
State is CPU register state, per-CPU host data, hyp page tables, and pKVM metadata. It depends on `kvm_host.h`, `kvm_asm.h`, sysreg definitions, VGIC/timer/debug support, and build-time VHE/nVHE separation.

### Integration Points
Used by hyp C and assembly, KVM host wrappers, protected-mode code, and nested virtualization paths.

### Risks
EL1/EL2 context misuse is dangerous. Missing save/restore calls corrupt host or guest registers. pKVM helpers must preserve host/hyp isolation.

### Test Signals
Exercise VHE/nVHE guest entry/exit, timer interrupts, VGIC state, debug register handoff, SVE/FPSIMD ownership, and pKVM memory transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hypevents.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hypevents.h

### Purpose
`kvm_hypevents.h` declares ARM64 KVM hypervisor trace events that can be emitted from hyp context and consumed through the remote event machinery.

### Important APIs, Types, And Functions
It defines trace-event include protection, imports tracepoint helpers, and lists `HYP_EVENT` declarations with field/assignment/print blocks for hyp-visible events.

### Control Flow
At build time, the event declarations are expanded by `kvm_define_hypevents.h`. At runtime, hyp instrumentation writes event records into the remote trace infrastructure when configured.

### State, Persistence, And Dependencies
Runtime state is trace buffers and event metadata, not header-owned storage. It depends on remote event macros and tracepoint infrastructure.

### Integration Points
Links EL2 KVM events to ftrace/tracefs observability and debugging of protected or nVHE paths.

### Risks
Trace field layout must remain compatible with remote readers. Logging from hyp context must be low overhead and safe under restricted mappings.

### Test Signals
Build with tracing; enable KVM hyp events; exercise guest entry/exit or pKVM operations; verify event fields and timestamps appear in tracefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hypevents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyptrace.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyptrace.h

### Purpose
`kvm_hyptrace.h` provides the ARM64 KVM hyp-side trace integration include point.

### Important APIs, Types, And Functions
It defines the include guard and pulls together hyp trace definitions/macros used by EL2 code. The exported surface is intentionally small and macro-driven.

### Control Flow
There is no standalone runtime flow. Hyp code includes this header so trace macros compile to remote event emission or no-op code depending on configuration.

### State, Persistence, And Dependencies
No storage is owned here. State lives in trace buffers and remote-event metadata. Dependencies are KVM hyp trace declarations and generic tracing support.

### Integration Points
Included by ARM64 KVM hyp C files to emit safe trace events from hypervisor context.

### Risks
The main risk is configuration drift where hyp code expects trace macros unavailable in a given build, or trace calls assume mappings not present at EL2.

### Test Signals
Compile KVM with hyp tracing enabled and disabled; run a guest and confirm trace events appear only in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mmu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mmu.h

### Purpose
`kvm_mmu.h` declares ARM64 KVM MMU and hyp mapping helpers, plus inline address-translation, cache-maintenance, VTTBR, stage-2 loading, and fault-lock policies.

### Important APIs, Types, And Functions
Key exports are hyp assembly macros `hyp_pa` and `hyp_kimg_va`, `__kern_hyp_va()`, `kern_hyp_va()`, `KVM_PHYS_SHIFT`, `kvm_phys_shift()`, hyp mapping APIs (`create_hyp_mappings`, `hyp_alloc_private_va_range`, `create_hyp_io_mappings`, `create_hyp_stack`), stage-2 APIs (`kvm_stage2_unmap_range`, `kvm_init_stage2_mmu`, `kvm_handle_guest_abort`), cache helpers, `kvm_get_vttbr()`, `__load_stage2()`, `kvm_fault_lock()`, and cacheable PFNMAP support checks.

### Control Flow
Early KVM setup computes hyp VA layout and creates hyp mappings. Guest fault paths take the appropriate MMU lock, map/unmap/update stage-2 entries, perform cache maintenance when FWB/DIC do not cover it, and load VTCR/VTTBR before guest entry.

### State, Persistence, And Dependencies
State includes hyp VA layout, hyp phys/virt offset, stage-2 page tables, VMIDs, and cache/TLB side effects. It depends on page-table allocation, cacheflush, MMU context, `kvm_pgtable.h`, `stage2_pgtable.h`, and KVM vCPU emulation.

### Integration Points
Connects KVM guest memory management with generic MM, hyp mapping setup, TLB maintenance, pKVM isolation, and abort handling.

### Risks
Incorrect hyp VA conversion breaks nVHE execution. Missing cache maintenance can expose stale instructions/data to guests. VTTBR ordering relies on prior barriers, and fault locking differs in protected mode.

### Test Signals
Run KVM memory faults, dirty logging, MMIO/ioremap, huge-page split, protected-mode tests, VMID rollover, cache aliasing workloads, and guest instruction-cache coherency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mte.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mte.h

### Purpose
`kvm_mte.h` declares ARM64 KVM support for Memory Tagging Extension in guests, including VM enablement, tag copying, fault handling, and page/tag synchronization.

### Important APIs, Types, And Functions
It exports helpers around `kvm_has_mte()`, MTE VM ioctl support, tag-copy operations, page tag initialization/synchronization, and conditional stubs when `CONFIG_ARM64_MTE` or KVM MTE support is absent.

### Control Flow
Userspace enables guest MTE through VM attributes/ioctls. KVM maps guest memory with tag-aware behavior, synchronizes tags during page faults or migration-like copy operations, and handles tag faults according to guest configuration.

### State, Persistence, And Dependencies
State lives in VM flags, page flags/tag storage, and CPU MTE registers. It depends on `asm/mte.h`, page table attributes, KVM memory slots, and CPU feature detection.

### Integration Points
Connects KVM VM ioctls, guest memory fault handling, ARM64 MTE core, and migration/debug tag copy paths.

### Risks
Missing tag synchronization can leak stale tags or corrupt guest memory semantics. Host/guest tag ownership is subtle around shared pages and migration. Stubs must preserve build compatibility.

### Test Signals
Run KVM MTE selftests, tag copy ioctl tests, guest tag fault tests, migration/save-restore tag checks, and non-MTE config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mte.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_nested.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_nested.h

### Purpose
`kvm_nested.h` defines ARM64 nested virtualization helpers for exposing virtual EL2, translating EL2-style registers, managing nested stage-2 MMUs, walking guest stage-2 tables, validating TLBI operations, and translating virtual addresses.

### Important APIs, Types, And Functions
Important exports include `vcpu_has_nv()`, `translate_tcr_el2_to_tcr_el1()`, `translate_cptr_el2_to_cpacr_el1()`, `translate_sctlr_el2_to_sctlr_el1()`, `translate_ttbr0_el2_to_ttbr0_el1()`, nested init/load/sync functions, `struct kvm_s2_trans`, `kvm_walk_nested_s2()`, `kvm_s2_handle_perm_fault()`, `kvm_inject_s2_fault()`, TLBI support checks, `decode_range_tlbi()`, `struct s1_walk_info`, `struct s1_walk_result`, `__kvm_translate_va()`, VNCR helpers, and `__kvm_at_swap_desc()`.

### Control Flow
When a vCPU has virtual EL2, KVM translates guest hypervisor state into host-manageable EL1/EL2 forms, selects nested or canonical stage-2 MMUs, walks L1-provided stage-2 tables, injects virtual faults, and handles TLBI/VNCR traps.

### State, Persistence, And Dependencies
State lives in nested MMU arrays, VNCR TLBs, vCPU sysregs, stage-1 walk context, and `struct kvm_s2_trans` results. It depends on `kvm_emulate.h`, `kvm_pgtable.h`, sysreg/TLBI definitions, and CPU nested-virt capability.

### Integration Points
Used by sysreg emulation, abort handling, stage-2 MMU management, nested TLB invalidation, and guest AT instruction emulation.

### Risks
Nested translation bugs can grant wrong permissions or inject wrong faults. TLBI range decoding must respect feature exposure. Register translation is sensitive to VHE/nVHE and E2H/TGE semantics.

### Test Signals
Run nested KVM selftests, L1 guest hypervisor boots, TLBI range tests, VNCR abort tests, AT instruction tests, S2 permission fault tests, and ptrauth ERET checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_nested.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pgtable.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pgtable.h

### Purpose
`kvm_pgtable.h` defines the generic ARM64 KVM page-table library interface for hyp stage-1 and guest stage-2 tables, including PTE encoding, walkers, mapping/unmapping, permission changes, aging, flushing, splitting, and pKVM annotations.

### Important APIs, Types, And Functions
It defines `kvm_pte_t`, PTE address/attribute masks, invalid PTE annotation types, `kvm_pte_to_phys()`, `kvm_phys_to_pte()`, granule/block helpers, `struct kvm_pgtable_mm_ops`, `enum kvm_pgtable_prot`, `enum kvm_pgtable_walk_flags`, `struct kvm_pgtable_visit_ctx`, `struct kvm_pgtable_walker`, `struct kvm_pgtable`, and APIs such as `kvm_pgtable_hyp_init/map/unmap/destroy`, `kvm_get_vtcr()`, `kvm_pgtable_stage2_*`, `kvm_pgtable_walk()`, `kvm_pgtable_get_leaf()`, and `kvm_tlb_flush_vmid_range()`.

### Control Flow
Callers initialize a page-table object with memory callbacks, then use map/unmap/walk APIs. Walkers visit leaf and table entries in requested order, using RCU for shared host walks but forbidding shared walks in hyp context. Stage-2 operations coalesce/split mappings, relax permissions, age entries, and issue required TLB/cache maintenance.

### State, Persistence, And Dependencies
State is page-table memory, reference counts in callback-owned pages, stage-2 MMU metadata, and optional pKVM mapping trees. It depends on generic KVM host types, ARM64 page-table hardware definitions, RCU in host context, and CPU LPA2/52-bit PA capabilities.

### Integration Points
Consumed by KVM MMU, pKVM host/guest ownership tracking, nested translation, dirty logging, huge-page splitting, and hyp mapping code.

### Risks
Break-before-make, shared-walker synchronization, LPA2 address encoding, and invalid PTE annotations are high-risk. Caller-provided `mm_ops` must obey refcount/free semantics.

### Test Signals
KVM page-table unit tests, stage-2 map/unmap/relax-perms/young tests, huge-page split tests, pKVM donation/reclaim tests, LPA2/52-bit PA builds, and RCU lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pkvm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pkvm.h

### Purpose
`kvm_pkvm.h` declares protected KVM constants and helpers for memory ownership, host/guest hyp mappings, pKVM initialization, and protected VM lifecycle.

### Important APIs, Types, And Functions
The header defines pKVM memory protection constants, hyp/host memory helpers, handle types, protected VM setup/finalization/teardown declarations, host donation/share/unshare operations, and conditional stubs for non-pKVM builds.

### Control Flow
pKVM initialization reserves hyp memory and transitions the host into a protected mode. VM creation allocates a protected handle, donates pages to hyp/guest ownership, maps required ranges, and later tears them down through protected hypercalls.

### State, Persistence, And Dependencies
State lives in hyp-owned metadata, `struct kvm_protected_vm`, memory ownership annotations, and host/hyp page tables. It depends on `kvm_host.h`, `kvm_pgtable.h`, SMCCC/hyp calls, and protected-mode static keys.

### Integration Points
Connects KVM VM lifecycle, hyp memory management, page-table annotation, and host deprivileging.

### Risks
Ownership transition bugs can violate host/guest isolation or leak pages. Handle lifetime and teardown ordering must prevent reuse while vCPUs run. Stub behavior must keep non-pKVM builds correct.

### Test Signals
Boot pKVM-enabled kernels, create/destroy protected VMs, stress page donation/reclaim/share paths, and run isolation/security regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pkvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_ptrauth.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_ptrauth.h

### Purpose
`kvm_ptrauth.h` provides ARM64 KVM pointer-authentication helpers for saving/restoring guest keys and exposing PAuth state when configured.

### Important APIs, Types, And Functions
It declares or defines helpers for guest PAuth key save/restore, `vcpu_has_ptrauth()` integration, system-register key handling, and no-op stubs when `CONFIG_ARM64_PTR_AUTH` is disabled.

### Control Flow
During vCPU context switch, KVM saves host/guest pointer authentication key registers as required and restores the guest-visible keys before running the vCPU. Nested paths may authenticate ERET targets through `kvm_auth_eretax()`.

### State, Persistence, And Dependencies
State is in vCPU sysreg storage and CPU PAuth key registers. It depends on `kvm_host.h`, pointer-auth CPU features, sysreg definitions, and feature bits exposed to the guest.

### Integration Points
Used by world-switch code, nested virtualization, sysreg ioctl paths, and feature finalization.

### Risks
Key leakage between host and guest is security sensitive. Feature gating must match CPU support and VM-visible ID registers. Stubs must not accidentally allow unsupported key access.

### Test Signals
Run PAuth KVM selftests, key save/restore stress across vCPU migration, nested ERET authentication tests, and builds with PAuth disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_ptrauth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_types.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_types.h

### Purpose
`kvm_types.h` supplies ARM64 KVM architecture-specific type aliases needed by generic KVM headers.

### Important APIs, Types, And Functions
The file is intentionally tiny and defines KVM scalar types such as the architecture pfn type used in page-table code.

### Control Flow
There is no runtime flow; the header exists to satisfy include-time type contracts.

### State, Persistence, And Dependencies
It has no state or persistence. It depends on generic integer type definitions already available through the include stack.

### Integration Points
Included indirectly by generic KVM and ARM64 page-table/MMU code.

### Risks
Type width drift would break address translation or pfn math. The small size makes ABI drift the main concern.

### Test Signals
Compile KVM and page-table code across ARM64 configs; run sparse/build checks for type mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/linkage.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/linkage.h

### Purpose
`linkage.h` defines ARM64 assembly linkage macros for symbol alignment, function annotations, and BTI landing-pad handling.

### Important APIs, Types, And Functions
It provides architecture-specific `SYM_FUNC_START*`, alignment, and `BTI_C`/landing-pad style macros used by assembly files and generic linkage helpers.

### Control Flow
The macros expand during assembly preprocessing. They shape symbol boundaries and instruction sequences but do not implement C runtime flow.

### State, Persistence, And Dependencies
No runtime state. The persistent effect is ELF symbol metadata and instruction layout. It depends on generic linkage conventions and ARM64 BTI configuration.

### Integration Points
Used by low-level ARM64 assembly, including exception vectors, entry code, and KVM hyp assembly.

### Risks
Incorrect symbol annotations break unwinding, kallsyms, objtool-like validation, or BTI enforcement. Alignment changes can affect alternative patching.

### Test Signals
Build with BTI and without; inspect symbols/unwind metadata; boot-test exception and hyp paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/lse.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/lse.h

### Purpose
`lse.h` gates ARM64 Large System Extensions support for atomic instructions.

### Important APIs, Types, And Functions
It includes alternative/capability machinery and defines the compile-time hooks used by atomic/percpu/cmpxchg code to select LSE instructions or LL/SC fallbacks.

### Control Flow
Atomic helpers use alternatives to patch in LSE sequences on capable CPUs. This header contributes selection macros rather than standalone control flow.

### State, Persistence, And Dependencies
State is CPU capability detection and patched instruction text. It depends on `asm/alternative.h`, CPU feature bits, and atomic instruction implementations.

### Integration Points
Used by atomic and per-CPU operations that underpin scheduler, locking, MM, networking, and Ceph client concurrency.

### Risks
Incorrect LSE gating can execute unsupported instructions or miss faster atomics. Alternative patching must be safe during boot and CPU hotplug.

### Test Signals
Build/run on LSE and non-LSE ARM64 systems; stress atomics, lock primitives, and CPU hotplug; inspect alternatives patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/lse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/lsui.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/lsui.h

### Purpose
`lsui.h` provides ARM64 Load/Store Unprivileged instruction helpers or feature gating for access patterns that need unprivileged load/store semantics.

### Important APIs, Types, And Functions
It is a small include-time contract defining LSUI-related macros and conditional assembly/compiler hooks.

### Control Flow
Consumers expand the macros inline where unprivileged memory access sequences are needed. Runtime behavior is selected by CPU feature and compiler/assembler support.

### State, Persistence, And Dependencies
There is no owned state. It depends on ARM64 instruction availability and low-level access helper infrastructure.

### Integration Points
Potential consumers include user access, exception-table protected memory access, or architecture-specific probing paths.

### Risks
Executing unsupported unprivileged load/store instructions or missing exception-table coverage can fault in sensitive contexts.

### Test Signals
Cross-build with relevant CPU feature configs; run usercopy and fault-injection tests that exercise unprivileged accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/lsui.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mem_encrypt.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mem_encrypt.h

### Purpose
`mem_encrypt.h` supplies ARM64 stubs or hooks for confidential-computing memory encryption interfaces expected by generic kernel code.

### Important APIs, Types, And Functions
It defines architecture predicates/helpers for encrypted memory, DMA decryption/encryption hooks, and related no-op implementations where ARM64 has no active memory encryption backend in this tree.

### Control Flow
Generic memory-encryption call sites compile against these helpers. On this ARM64 version, most paths are compile-time no-ops or constant false unless a platform feature adds behavior elsewhere.

### State, Persistence, And Dependencies
No header-owned state. It depends on generic memory encryption API shape and DMA/memory-management call sites.

### Integration Points
Allows common kernel code shared with encrypted-memory architectures to build for ARM64. Filesystem I/O is affected indirectly through DMA/page handling call sites.

### Risks
A false no-op is dangerous if platform memory encryption is later introduced without updating this layer. API drift can break generic code.

### Test Signals
Compile all generic memory-encryption consumers on ARM64; run DMA and memory hotplug tests; verify encrypted-memory predicates remain correct for platform configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mem_encrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/memory.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/memory.h

### Purpose
`memory.h` defines ARM64 virtual/physical memory layout constants, translation helpers, KASLR/KASAN layout values, linear-map bounds, phys/virt conversion macros, and memory tagging/top-byte rules.

### Important APIs, Types, And Functions
Key items include `VA_BITS`, `PAGE_OFFSET`, `MODULES_VADDR`, `VMALLOC_START/END`, `VMEMMAP_START`, `KIMAGE_VADDR`, `PHYS_OFFSET`, `PHYS_MASK`, `__pa()`, `__va()`, `virt_to_phys()`, `phys_to_virt()`, `virt_addr_valid()`, `__is_lm_address()`, `lm_alias()`, `untagged_addr()`, memory limit declarations, and KASAN/MTE/TBI-aware address helpers.

### Control Flow
Most behavior is macro/inline expansion. Boot code establishes layout variables such as `memstart_addr`; later MM, DMA, and page-table code use the conversion helpers continuously.

### State, Persistence, And Dependencies
State includes boot-initialized physical offset/memory-limit globals and address-space constants. It depends on page definitions, compiler attributes, KASAN/MTE options, sparsemem, and kernel VA size configuration.

### Integration Points
This is foundational for all ARM64 kernel memory access, including page cache, network buffers, block I/O, DMA, KVM, and Ceph client data paths.

### Risks
Address conversion bugs cause memory corruption. Tagged-address handling must match MTE/TBI and userspace ABI. Layout constants must not overlap modules, vmalloc, vmemmap, fixmap, or kernel image regions.

### Test Signals
Boot page-size/VA-size/KASAN/MTE combinations; run memory hotplug, sparsemem, DMA, KASAN, and high-memory stress; validate `/proc/vmallocinfo` and page-owner diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mman.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mman.h

### Purpose
`mman.h` defines ARM64-specific memory mapping policy helpers, especially executable mapping defaults and memory-tagging mmap flags.

### Important APIs, Types, And Functions
It wraps UAPI `mman` constants, defines `arch_calc_vm_prot_bits()`, `arch_validate_prot()`, `arch_validate_flags()`, and personality/read-implies-exec handling used by mmap/mprotect.

### Control Flow
Generic mmap/mprotect paths call the inline helpers to translate protection flags into `VM_*` bits and reject unsupported combinations. MTE-specific flags are accepted only when the architecture/configuration supports them.

### State, Persistence, And Dependencies
No owned state; policy depends on process personality, CPU MTE support, and VMA flags. It depends on generic MM constants and ARM64 MTE definitions.

### Integration Points
Used by userspace mapping syscalls, ELF loader behavior, JITs, and memory-tagged mappings that can back filesystem pages.

### Risks
Incorrect validation can allow unsupported tagged mappings or break executable mappings for legacy processes. ABI changes affect userspace.

### Test Signals
Run mmap/mprotect selftests, MTE userspace tests, READ_IMPLIES_EXEC tests, and compatibility-process mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu.h

### Purpose
`mmu.h` defines ARM64 MM context state and ASID/TCR-related helpers used by process address spaces and kernel page-table management.

### Important APIs, Types, And Functions
It declares `mm_context_t`, ASID/id fields, flags for 52-bit VA or CnP-style behavior, and architecture MMU helper prototypes/macros used by context switching and page-table setup.

### Control Flow
Context-switch and MM initialization code read/write the context fields to select the active ASID and translation regime. Page-table setup uses flags to choose address-space sizing.

### State, Persistence, And Dependencies
State persists in each `mm_struct` context for the lifetime of a process address space. It depends on atomic counters, CPU feature flags, and ARM64 translation control definitions.

### Integration Points
Used by `mmu_context.h`, scheduler context switch, TLB flushing, exec/fork, KVM interactions with process memory, and filesystem page-fault paths.

### Risks
ASID reuse and context flag mistakes can create stale TLB access across processes. 52-bit VA support must stay synchronized with page-table layout.

### Test Signals
Run fork/exec stress, ASID rollover tests, TLB shootdown tests, 52-bit VA builds, and memory-management selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu_context.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu_context.h

### Purpose
`mmu_context.h` implements ARM64 address-space activation, ASID allocation hooks, TCR programming, TTBR switching, CnP behavior, reserved TTBR0 handling, and PAN/UAO-related context helpers.

### Important APIs, Types, And Functions
Important exports include context init/destroy/switch helpers, `cpu_set_reserved_ttbr0()`, `cpu_switch_mm()`, `cpu_replace_ttbr1()`, `init_new_context()`, `destroy_context()`, `activate_mm()`, `switch_mm()`, TCR/TTBR helpers, and ASID generation interfaces.

### Control Flow
On context switch, ARM64 selects or allocates an ASID, writes TTBR/TCR state, performs required barriers, and may install reserved TTBR0 when no userspace table should be active. Exec/fork paths initialize or destroy per-mm context.

### State, Persistence, And Dependencies
State persists in `mm_context_t`, CPU-local active context, ASID allocator state, TTBR registers, and TLBs. It depends on `mmu.h`, `pgtable.h`, CPU capabilities, barriers, and scheduler/MM core.

### Integration Points
Used by scheduler, process creation/destruction, page faults, KPTI, PAN, and any subsystem that switches between user address spaces.

### Risks
Missing barriers around TTBR/TCR updates can expose stale translations. ASID rollover and CnP are concurrency sensitive. Reserved TTBR0 mistakes can expose user mappings in kernel context.

### Test Signals
Run context-switch stress, ASID rollover, KPTI/PAN tests, fork/exec workloads, CPU hotplug, and TLB invalidation selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.h

### Purpose
`module.h` defines ARM64 module architecture metadata, PLT/GOT relocation support, and module allocation/layout declarations.

### Important APIs, Types, And Functions
It declares `struct mod_arch_specific`, PLT/GOT section metadata, module flags for BTI/PAuth/MTE-like features where present, and architecture module init/finalize hooks consumed by the module loader.

### Control Flow
When a module loads, the module loader allocates architecture sections, applies relocations, builds veneers/PLTs where branch ranges require them, and records module properties.

### State, Persistence, And Dependencies
State lives in each loaded `struct module` architecture extension and generated module sections. It depends on ELF relocation handling, module loader core, alternatives, and ARM64 instruction encoding.

### Integration Points
Used by loadable kernel modules, including filesystem/networking modules that may include Ceph-related code.

### Risks
Relocation or PLT sizing mistakes produce invalid branches. Feature flags such as BTI must match module text attributes. Module memory must respect executable permissions.

### Test Signals
Build/load modules with long branches, alternatives, BTI configs, and unload/reload cycles; run module relocation selftests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.lds.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.lds.h

### Purpose
`module.lds.h` supplies ARM64 module linker-script fragments for architecture-specific sections.

### Important APIs, Types, And Functions
It defines section layout snippets for PLT/GOT, alternatives, unwind/metadata, or architecture note sections needed by ARM64 modules.

### Control Flow
There is no runtime flow. The linker consumes these macros while building modules, and the module loader later relies on the resulting section layout.

### State, Persistence, And Dependencies
The persistent output is ELF section placement in `.ko` files. It depends on the kernel module linker script and ARM64 module loader expectations.

### Integration Points
Used by Kbuild/module linking for ARM64 loadable modules.

### Risks
Misplaced sections break relocation, alternatives patching, or security metadata. Linker-script drift can be hard to diagnose until module load time.

### Test Signals
Build external and in-tree modules, inspect section tables, load/unload modules with alternatives and PLTs enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mpam.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mpam.h

### Purpose
`mpam.h` defines ARM64 MPAM register helpers and feature hooks for Memory Partitioning and Monitoring.

### Important APIs, Types, And Functions
It declares MPAM enablement predicates, system-register access helpers, CPU setup hooks, and fallback no-ops when MPAM is disabled or unavailable.

### Control Flow
CPU feature detection enables MPAM support; setup code programs MPAM system registers; subsystems can later use partition/monitoring controls if the platform exposes them.

### State, Persistence, And Dependencies
State is in CPU MPAM registers and platform resource-control data. It depends on sysreg definitions, CPU feature probing, and configuration flags.

### Integration Points
Interacts with scheduler/resource-control or platform QoS code. Filesystem workloads are affected indirectly through memory/cache/bandwidth partitioning.

### Risks
Improper register programming can affect system-wide QoS or trap behavior. Feature stubs must keep non-MPAM builds correct.

### Test Signals
Compile MPAM and non-MPAM configs; boot on MPAM-capable hardware; validate register programming and resource partition behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mpam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mshyperv.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mshyperv.h

### Purpose
`mshyperv.h` provides ARM64 Microsoft Hyper-V paravirtualization hooks and hypercall interfaces.

### Important APIs, Types, And Functions
It declares Hyper-V detection/init helpers, hypercall page interfaces, VP assist or synthetic interrupt helpers where supported, and no-op stubs for non-Hyper-V builds.

### Control Flow
Platform init detects Hyper-V, sets up hypercall mechanisms, and later paravirtualized drivers or time/interrupt paths use the helpers to communicate with the hypervisor.

### State, Persistence, And Dependencies
State includes hypercall page address, discovered feature bits, and per-CPU/VP data. It depends on `linux/hyperv.h`, SMCCC/firmware call conventions, and ARM64 paravirt infrastructure.

### Integration Points
Used by Hyper-V guest support, synthetic devices, clocks, interrupts, and potentially storage/network paths used by Ceph deployments in Hyper-V guests.

### Risks
Calling hypercalls before initialization or with wrong calling convention can fail or corrupt registers. Feature detection must match host-advertised capabilities.

### Test Signals
Boot ARM64 under Hyper-V, run Hyper-V device drivers, validate time/interrupt behavior, and build non-Hyper-V configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mshyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-def.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-def.h

### Purpose
`mte-def.h` defines common ARM64 Memory Tagging Extension constants used by MTE, KASAN, and KVM tag code.

### Important APIs, Types, And Functions
It exports constants such as `MTE_GRANULE_SIZE`, `MTE_GRANULE_MASK`, `MTE_TAG_SHIFT`, `MTE_TAG_SIZE`, `MTE_TAG_MASK`, `MTE_PAGE_TAG_STORAGE`, and `__MTE_PREAMBLE`.

### Control Flow
There is no runtime control flow. Inline asm and tag-management helpers include these constants to size granules, masks, and tag-storage buffers.

### State, Persistence, And Dependencies
No state is owned. It depends on generic bit macros and ARM64 assembler support for the memtag extension.

### Integration Points
Used by `mte.h`, `mte-kasan.h`, KVM MTE, and memory-management code handling tagged pages.

### Risks
Wrong granule or tag size breaks tag storage layout and address tag extraction. Assembler preamble mismatch breaks inline MTE instructions.

### Test Signals
Build MTE/KASAN configs; run MTE userspace, KASAN HW tags, and KVM MTE tag-storage tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-kasan.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-kasan.h

### Purpose
`mte-kasan.h` implements low-level ARM64 MTE primitives used by hardware-tag KASAN: tag check override control, random tag generation, tag load/store, range tagging, and kernel MTE modes.

### Important APIs, Types, And Functions
It exports `system_uses_mte_async_or_asymm_mode()`, `mte_disable_tco()`, `mte_enable_tco()`, async TCO helpers, `mte_get_ptr_tag()`, `mte_get_mem_tag()`, `mte_get_random_tag()`, `mte_set_mem_tag_range()`, `SET_MEMTAG_RANGE`, and kernel mode functions `mte_enable_kernel_sync/async/asymm/store_only()`, with non-MTE stubs.

### Control Flow
KASAN and MTE setup enable kernel tag-check modes, then allocation/free/page operations call inline assembly helpers to set or read allocation tags over memory ranges.

### State, Persistence, And Dependencies
State is CPU MTE control registers, tags stored in memory tag storage, and the static key `mte_async_or_asymm_mode`. It depends on `asm/compiler.h`, `asm/cputype.h`, `asm/mte-def.h`, and MTE CPU support.

### Integration Points
Used by hardware-tag KASAN, allocator tagging, page clearing, and kernel entry/exit tag-check control.

### Risks
Tag range loops must align and size ranges correctly. TCO toggling affects whether faults are detected. Async/asymm modes change fault timing and diagnostics.

### Test Signals
Run KASAN HW_TAGS tests, MTE sync/async/asymm boot modes, allocator fault injection, and tag range stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte.h

### Purpose
`mte.h` declares ARM64 Memory Tagging Extension page, thread, ptrace, suspend, and fault-check integration.

### Important APIs, Types, And Functions
Key APIs are `mte_clear_page_tags()`, tag copy to/from user, `mte_save_tags()`, `mte_restore_tags()`, tag storage allocation/free, `PG_mte_tagged`, page/folio tagging helpers, `mte_zero_clear_page_tags()`, `mte_sync_tags()`, `mte_copy_page_tags()`, thread init/switch, CPU setup, suspend enter/exit, `set_mte_ctrl()`, `get_mte_ctrl()`, `mte_ptrace_copy_tags()`, and TFSR check helpers.

### Control Flow
MM paths mark pages/folios tagged, synchronize tags when PTEs are installed, save/restore tags for swap or migration, and update task MTE state on context switch. Entry/exit paths check deferred tag faults when async modes are active.

### State, Persistence, And Dependencies
State includes page flags, tag storage buffers, task controls, CPU MTE registers, TFSR fault status, and swap-associated tag records. It depends on page flags, scheduler, KASAN enablement, PTE types, and `mte-def.h`.

### Integration Points
Used by memory management, swap, ptrace, KVM MTE, KASAN, and userspace ABI for tagged addresses.

### Risks
Tag storage lifetime must match page/swap lifetime. Page flag locking prevents double tagging. Deferred fault checks must not lose faults across context switch or suspend.

### Test Signals
Run MTE selftests, ptrace tag copy tests, swap/migration tag preservation, hugepage tagging, suspend/resume, and non-MTE config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon-intrinsics.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon-intrinsics.h

### Purpose
`neon-intrinsics.h` prepares compiler type definitions and includes `<arm_neon.h>` for kernel code that uses ARM64 NEON intrinsics.

### Important APIs, Types, And Functions
It adjusts `__INT64_TYPE__` and `__UINT64_TYPE__` around the compiler intrinsic header so kernel integer type expectations remain compatible.

### Control Flow
There is no runtime flow. It is include-time compatibility glue for C code compiled with NEON enabled.

### State, Persistence, And Dependencies
No state. It depends on compiler-provided `arm_neon.h` and kernel integer type definitions.

### Integration Points
Used by optimized crypto/checksum/SIMD routines that may serve networking and storage paths.

### Risks
Compiler intrinsic ABI drift can break builds. Kernel code must still bracket NEON use with proper FPSIMD ownership helpers.

### Test Signals
Build SIMD-using objects with GCC/Clang; run crypto/checksum tests; ensure no NEON use without `kernel_neon_begin/end`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon-intrinsics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon.h

### Purpose
`neon.h` declares the safe kernel NEON/FPSIMD entry and exit API.

### Important APIs, Types, And Functions
It defines `cpu_has_neon()` as `system_supports_fpsimd()` and declares `kernel_neon_begin()` and `kernel_neon_end()`.

### Control Flow
Kernel code calls `kernel_neon_begin()` before using NEON registers and `kernel_neon_end()` afterward, allowing the FPSIMD subsystem to save/restore task state and manage preemption constraints.

### State, Persistence, And Dependencies
State is FPSIMD/NEON register ownership and optional saved `user_fpsimd_state`. It depends on `asm/fpsimd.h` and CPU feature detection.

### Integration Points
Used by crypto, RAID/checksum, compression, and other optimized routines that can affect filesystem/network throughput.

### Risks
Using NEON without bracketing corrupts user or guest FP state. Calling in invalid contexts can violate preemption/interrupt assumptions.

### Test Signals
Run crypto SIMD tests, preemption stress with NEON users, and KVM/FPSIMD state-switch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/numa.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/numa.h

### Purpose
`numa.h` connects ARM64 topology definitions to the generic NUMA interface.

### Important APIs, Types, And Functions
It includes `asm/topology.h` and `asm-generic/numa.h`; it has no additional ARM64-specific API surface in this file.

### Control Flow
Generic NUMA initialization and memory policy code use the included definitions. This header itself has no runtime flow.

### State, Persistence, And Dependencies
NUMA state lives in generic node, distance, and memory topology data. Dependencies are ARM64 topology parsing and generic NUMA code.

### Integration Points
Affects page allocation locality for page cache, networking, block I/O, and Ceph client memory.

### Risks
The risk is include/API drift; real NUMA behavior is in the included topology/generic files.

### Test Signals
Boot NUMA ARM64 systems, inspect node topology, run memory policy and page allocation locality tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/page-def.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/page-def.h

### Purpose
`page-def.h` exposes ARM64 page-size constants through the VDSO-compatible page definition layer.

### Important APIs, Types, And Functions
It includes `linux/const.h` and `vdso/page.h`, making page size/shift constants available to architecture headers.

### Control Flow
No runtime flow; it is a small include bridge.

### State, Persistence, And Dependencies
No state. It depends on VDSO page definitions and kernel constant macros.

### Integration Points
Used by `page.h`, page-table code, memory layout, and any subsystem needing `PAGE_SIZE`/`PAGE_SHIFT`.

### Risks
Page-size constant drift breaks ABI, page-table math, and userspace VDSO assumptions.

### Test Signals
Cross-build 4K/16K/64K page configs; run boot and VDSO selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/page-def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/page.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/page.h

### Purpose
`page.h` declares ARM64 page operations and page-level MM helpers, including copy/clear page, highpage handling, MTE tag clearing, pfn validation, and default VMA data flags.

### Important APIs, Types, And Functions
Exports include `copy_page()`, `clear_page()`, `copy_user_highpage()`, `copy_highpage()`, `vma_alloc_zeroed_movable_folio()`, `tag_clear_highpages()`, `copy_user_page()`, `pgtable_t`, `pfn_is_map_memory()`, and `VMA_DATA_DEFAULT_FLAGS`.

### Control Flow
MM and filesystem paths call page copy/clear helpers during allocation, COW, page cache operations, and highpage handling. MTE-aware paths clear tags for user pages when needed.

### State, Persistence, And Dependencies
State is page contents, page tags, and VMA flags. It depends on page definitions, pgtable types, memory layout, personality flags, and generic getorder.

### Integration Points
Used by generic MM, page cache, file I/O, networking buffers, and memory-mapped files.

### Risks
Copy/clear routines must preserve alignment and tagging semantics. Wrong executable default flags affect W^X/security and legacy behavior.

### Test Signals
Run MM selftests, page cache stress, MTE tag-clearing tests, COW/fork workloads, and page-size config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/paravirt.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/paravirt.h

### Purpose
`paravirt.h` declares ARM64 paravirtualized time initialization.

### Important APIs, Types, And Functions
It exports `pv_time_init()` when paravirtual time is enabled and a no-op macro otherwise.

### Control Flow
Boot code calls `pv_time_init()` to initialize paravirtual clock support when configured.

### State, Persistence, And Dependencies
State lives in paravirtual clock data and hypervisor-provided time structures. It depends on `CONFIG_PARAVIRT` and platform/hypervisor support.

### Integration Points
Used by ARM64 timekeeping under virtualized environments, affecting scheduler timing and I/O latency accounting.

### Risks
Incorrect initialization can skew timekeeping in guests. The no-op path must keep bare-metal and unsupported configs clean.

### Test Signals
Boot under supported hypervisors with paravirt time; compare clock stability; build with paravirt disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/paravirt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pci.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pci.h

### Purpose
`pci.h` provides ARM64 PCI architecture policy and includes generic PCI support.

### Important APIs, Types, And Functions
It defines `PCIBIOS_MIN_IO`, `pcibios_assign_all_busses()`, `arch_can_pci_mmap_wc()`, includes DMA mapping/I/O helpers, and delegates most behavior to `asm-generic/pci.h`.

### Control Flow
PCI core uses these macros during bus/resource setup and mmap validation. Device drivers use the generic PCI APIs backed by this architecture policy.

### State, Persistence, And Dependencies
PCI state lives in device/resource structures and DMA mappings. Dependencies include `linux/dma-mapping.h`, `asm/io.h`, and generic PCI.

### Integration Points
Affects network/storage adapters used by distributed filesystems and Ceph deployments.

### Risks
Resource window policy or write-combine mmap support must match platform capabilities. DMA mapping assumptions must stay coherent with IOMMU/cache behavior.

### Test Signals
Boot PCIe ARM64 systems, enumerate devices, test WC mmaps, DMA, IOMMU, and hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/percpu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/percpu.h

### Purpose
`percpu.h` implements ARM64 optimized per-CPU accessors using TPIDR-based offsets, hyp/kernel variants, LSE/LLSC operations, and fallback generic per-CPU support.

### Important APIs, Types, And Functions
Exports include `set_my_cpu_offset()`, `__hyp_my_cpu_offset()`, `__kern_my_cpu_offset()`, `__my_cpu_offset`, generated `__percpu_read/write_*`, per-CPU add/and/or/xchg/cmpxchg helpers, `this_cpu_*` operations for 1/2/4/8/128-byte sizes, `__hyp_per_cpu_offset()`, `per_cpu_offset()`, and raw aliases for some configurations.

### Control Flow
Per-CPU operations compute the current CPU base from a system register or hyp offset, then perform inline loads/stores or atomic updates. Alternative/LSE machinery chooses the instruction sequence where supported.

### State, Persistence, And Dependencies
State is per-CPU storage and CPU-local offset registers. It depends on preemption control, `asm/alternative.h`, `cmpxchg`, stack pointer helpers, sysregs, and LSE support.

### Integration Points
Used pervasively by scheduler, counters, locks, networking, KVM host data, and filesystem statistics.

### Risks
Preemption safety is critical: using current-CPU access across migration corrupts another CPU's slot. LSE/LLSC constraints and 128-bit cmpxchg must match CPU support.

### Test Signals
Run percpu selftests, preemption and CPU hotplug stress, KVM hyp per-CPU access tests, and atomic operation stress on LSE/non-LSE hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/perf_event.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/perf_event.h

### Purpose
`perf_event.h` defines ARM64 perf register access helpers for BPF/perf callchain sampling.

### Important APIs, Types, And Functions
It provides `perf_arch_bpf_user_pt_regs(regs)` and `perf_arch_fetch_caller_regs(regs, __ip)` to populate `pt_regs` snapshots with caller IP and stack pointer.

### Control Flow
Perf/BPF sampling code calls these macros when preparing architecture register views for events or BPF programs.

### State, Persistence, And Dependencies
State is transient `pt_regs` sample data. It depends on stack pointer helpers and `asm/ptrace.h`.

### Integration Points
Used by perf, eBPF tracing/profiling, and observability of filesystem/network workloads.

### Risks
Incorrect register snapshots degrade profiling accuracy or BPF helper behavior. Stack pointer choice must match the sampled context.

### Test Signals
Run perf record/report, BPF perf-event tests, callchain sampling, and interrupt/NMI-like sampling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgalloc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgalloc.h

### Purpose
`pgalloc.h` defines ARM64 page-table allocation/population helpers for PGD/P4D/PUD/PMD/PTE levels.

### Important APIs, Types, And Functions
Key exports include `PGD_SIZE`, `__pud_populate()`, `pud_populate()`, `pud_free()`, `__p4d_populate()`, `p4d_populate()`, `__pgd_populate()`, `pgd_populate()`, `pgd_alloc()`, `pgd_free()`, and `__pmd_populate()`/PMD population helpers. It also declares architecture-specific PGD/PUD free support.

### Control Flow
MM code allocates page-table pages, then population helpers install table descriptors with physical addresses and protections. Free helpers release unused levels, with compile-time folding depending on configured page-table levels.

### State, Persistence, And Dependencies
State is process/kernel page-table memory. It depends on hardware page-table definitions, processor/cacheflush/TLB flush helpers, and generic pgalloc.

### Integration Points
Used by process address-space creation, vmalloc/module mappings, page faults, and KVM-related page-table code indirectly.

### Risks
Population helpers must use correct descriptor types and barriers/cache maintenance. Folded-level configurations must not free nonexistent tables.

### Test Signals
Cross-build all page-table levels/page sizes; run fork/exec, vmalloc, memory hotplug, page fault, and TLB flush tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-hwdef.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-hwdef.h

### Purpose
`pgtable-hwdef.h` defines ARM64 hardware page-table geometry, descriptor bit layouts, contiguous-entry sizing, address masks, memory attributes, permission bits, and TCR/TTBR field aliases.

### Important APIs, Types, And Functions
It exports `ARM64_HW_PGTABLE_LEVELS()`, `ARM64_HW_PGTABLE_LEVEL_SHIFT()`, `PTRS_PER_*`, `PMD/PUD/P4D/PGDIR_SHIFT/SIZE/MASK`, contiguous PTE/PMD constants, descriptor type bits, table UXN/PXN bits, PMD/PTE access/dirty/contiguous/XN/user bits, `PHYS_TO_PTE_ADDR_MASK`, `PTE_ATTRINDX()`, permission indirection/overlay bits, stage-2 memory attributes, TCR field aliases, TTBR masks, and 52-bit VA offset constants.

### Control Flow
There is no runtime flow. All page-table manipulation code consumes these masks and shifts when encoding or decoding descriptors and translation-control registers.

### State, Persistence, And Dependencies
No owned state; it defines the binary format of persistent in-memory page tables and CPU register fields. It depends on `asm/memory.h`, page size, VA bits, LPA2/52-bit PA options, and sysreg definitions.

### Integration Points
Foundational for kernel MM, KVM page tables, boot page tables, vmalloc/module mappings, and user page-table operations.

### Risks
Any incorrect bit definition can corrupt translation, permissions, dirty/access flags, or TLB behavior. 52-bit PA/VA and contiguous mappings are especially configuration-sensitive.

### Test Signals
Cross-build 4K/16K/64K, 48/52-bit VA/PA configs; run MM, KVM, dirty-bit, contiguous mapping, and permission fault tests; compare against architectural sysreg specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-hwdef.h -->
