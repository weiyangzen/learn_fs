# subset-b-000774 research

Grouped research report for the PowerPC kernel source files in `sources/distributed-fs/ceph-client/arch/powerpc/kernel`. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/exceptions-64e.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/exceptions-64e.S

## Purpose

`exceptions-64e.S` is the low-level exception and early Book3E initialization implementation for 64-bit embedded PowerPC. It defines the interrupt vector base, vector stubs, common exception prologs, special-level return paths, masked interrupt replay, bad-stack handling, initial TLB construction, and IVOR setup for Book3E CPUs. It is architecture-critical code that turns hardware exception state into Linux `pt_regs` frames and then dispatches to C handlers such as `do_IRQ`, `do_page_fault`, `machine_check_exception`, `timer_interrupt`, `program_check_exception`, and facility-unavailable handlers.

## Important APIs, entry points, and macros

Key local routines include `special_reg_save`, `ret_from_level_except`, `ret_from_crit_except`, `ret_from_mc_except`, `storage_fault_common`, `alignment_more`, `bad_stack_book3e`, `initial_tlb_book3e`, `start_initialization_book3e`, `book3e_secondary_core_init`, `book3e_secondary_thread_init`, `init_core_book3e`, `init_thread_book3e`, and IVOR setup helpers such as `__setup_base_ivors`, `setup_altivec_ivors`, `setup_perfmon_ivor`, `setup_doorbell_ivors`, `setup_ehv_ivors`, and `setup_lrat_ivor`.

The main macro layer is `EXCEPTION_PROLOG`, specialized as `NORMAL_EXCEPTION_PROLOG`, `CRIT_EXCEPTION_PROLOG`, `DBG_EXCEPTION_PROLOG`, `MC_EXCEPTION_PROLOG`, and `GDBELL_EXCEPTION_PROLOG`. `EXCEPTION_COMMON_LVL` builds the register frame. `MASKABLE_EXCEPTION` generates external, decrementer, fixed-interval, and doorbell entries. `SEARCH_RESTART_TABLE` and `masked_interrupt_book3e` implement replay for interrupts taken while Linux has them soft-disabled.

## Control flow

Hardware vectors branch through `interrupt_base_book3e` stubs into named handlers. The prolog saves scratch state into PACA exception areas, chooses a normal or special stack, checks for user versus kernel mode, applies branch-target-buffer flushing when configured, and snapshots SRR, CR, LR, CTR, XER, GPRs, trap number, and soft-enable state into the interrupt frame. Synchronous storage and alignment paths collect DEAR/ESR before dispatch. Asynchronous maskable paths test `PACAIRQSOFTMASK`; if masked, they mark `PACAIRQHAPPENED`, optionally clear `MSR_EE`, search restart-table entries, and return without entering the full C handler.

Critical, debug, and machine-check levels use separate stacks and save extra SPR state including SRR, CSRR/MCSRR/DSRR-related state, MAS registers, DEAR, and ESR. Return paths restore that state and use `rfci` or `rfmci`. The debug exception has special handling to suppress single-step or branch-taken exceptions inside exception entry code, otherwise it calls `DebugException` for user-originated events; kernel debug exceptions are marked not yet implemented with a self-loop.

Early boot flow enters `start_initialization_book3e`, calls `initial_tlb_book3e` to construct a PAGE_OFFSET mapping, initializes core and thread state, and returns to common 64-bit boot code. Secondary Book3E CPUs follow similar initialization via `book3e_secondary_core_init` or `book3e_secondary_thread_init`.

## State and persistence behavior

Persistent per-CPU state is centered on PACA fields: exception scratch areas, kernel and special stacks, `PACAIRQSOFTMASK`, `PACAIRQHAPPENED`, `PACA_TRAP_SAVE`, and Book3E TLB exception frame pointers. Hardware persistent state includes IVPR/IVORs, EPCR, TCR/TSR, TLB entries, MAS registers, PID, and SRR/CSRR/MCSRR registers. The code also maintains global labels and TLB init code ranges used by platform bring-up, including the A2 no-branch TLB init window.

## Dependencies and integration points

This file depends on assembly offsets for `pt_regs`, `thread_info`, PACA layout, BookE interrupt numbers, MAS/TLB constants, CPU feature fixups, KVM BookE hooks, IRQ soft-mask definitions, and common return code from `interrupt_64.S`. It calls into Linux C handlers for page faults, IRQs, timers, watchdogs, debug, alignment, program checks, machine checks, and bad stacks. It is included through the 64-bit boot path for Book3E and is tightly coupled to `head_64.S`, `exception-64e.h`, `head_booke.h`, and nohash MMU code that patches entry branches.

## Risks and invariants

The highest risk is corrupting entry or return state before a full stack frame exists. Scratch SPR selection, PACA offsets, stack choice, and `r13` PACA restoration must remain exact. Masked interrupt replay must keep restart-table semantics and hardware masking consistent or interrupts can be lost or re-enter unsafe code. TLB initialization assumes specific firmware mappings and page size behavior; changing it can strand execution without a valid translation. Special-level exceptions note limitations around nested non-standard levels and kernel debug exceptions, making those paths sensitive to new features.

## Test signals

Useful validation signals include successful boot on Book3E 64-bit systems, secondary CPU bring-up, timer and external interrupt delivery, user and kernel page fault handling, FPU/Altivec unavailable handling, watchdog behavior, KVM guest exits where configured, bad-stack diagnostics, and machine-check recovery or panic behavior. Build coverage should include Book3E, embedded hypervisor feature sections, SMP, KVM BookE, Altivec, and watchdog configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/exceptions-64e.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/exceptions-64s.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/exceptions-64s.S

## Purpose

`exceptions-64s.S` contains the 64-bit Book3S/server PowerPC exception vectors and common handlers. It is included from `head_64.S` because the vector layout is position dependent. The file lays out fixed real-mode vectors, real trampolines, virtual AIL vectors, virtual trampolines, the FWNMI page, common relocated handlers, masked-interrupt return paths, KVM interrupt routing, and mitigation fallback code for entry/RFI flushing.

## Important APIs, entry points, and macros

The macro system begins with fixed-section helpers such as `EXC_REAL_BEGIN`, `EXC_VIRT_BEGIN`, `TRAMP_REAL_BEGIN`, `TRAMP_VIRT_BEGIN`, and `EXC_COMMON_BEGIN`. Interrupt definitions use `INT_DEFINE_BEGIN/END` to declare per-vector attributes, then `GEN_INT_ENTRY`, `GEN_COMMON`, `__GEN_COMMON_ENTRY`, and `__GEN_COMMON_BODY` generate entry and register-frame code. `KVMTEST` routes interrupts taken while a KVM guest is active. `EXCEPTION_RESTORE_REGS`, `MASKED_INTERRUPT`, `SEARCH_RESTART_TABLE`, and `SEARCH_SOFT_MASK_TABLE` implement return and soft-mask behavior.

Named vectors cover system reset, machine check, data and instruction storage, SLB faults, external interrupts, alignment, program check, FP/Altivec/VSX/facility unavailable, decrementer and hdecrementer, doorbells, system calls and hypercalls, trace, hypervisor storage and emulation assists, HMI, virtualization IRQs, PMU, instruction breakpoint, denormal assists, and soft-NMI watchdog. Exported or global helpers include `do_uaccess_flush` and `enable_machine_check`; `disable_machine_check` is local.

## Control flow

The file first defines vector metadata and then opens fixed sections: real vectors at `0x0100..0x18ff`, real trampolines at `0x1900..0x2fff`, virtual vectors at `0x3000..0x58ff`, virtual trampolines at `0x5900..0x6fff`, and the FWNMI page at `0x7000..0x7fff` on pseries/powernv. Real entries save minimal state in PACA, optionally test KVM, collect SRR/HSRR/DAR/DSISR/CFAR/PPR state, switch to kernel MSR or stay in real mode for early handlers, then branch to common handlers. Virtual AIL entries run similar logic with relocation already on.

Machine check and system reset are special NMI-like paths. System reset uses the NMI emergency stack and tracks `PACA_IN_NMI`. Machine check runs an early real-mode handler on the MCE emergency stack, supports limited nesting through `PACA_IN_MCE`, queues recoverable kernel-context events, delivers user/guest events to late handlers, and panics through `unrecoverable_mce` when state is unsafe. HMI uses an early real-mode handler before optionally redelivering to the virtual handler.

Maskable interrupts check soft-mask state and soft-mask tables before normal delivery. If masked, they set `PACAIRQHAPPENED`, adjust DEC or hard-disable bits where needed, search restart entries, restore volatile state, and return through RFI/HRFI without calling the C handler. System call paths include classic `sc`, hypercall routing to KVM, and vectored `scv` entries that are treated as soft-masked because they can enter with interrupts enabled.

## State and persistence behavior

The code persists exception state in PACA save areas, `pt_regs` stack frames, SRR/HSRR validity flags, soft-mask and pending-interrupt fields, emergency stack counters, KVM host state, and fixed sections copied to low physical memory for relocatable kernels. It also relies on CPU feature fixup sections to patch behavior for PPR, CFAR, HV mode, radix versus hash MMU, transactional memory, denormalization support, and mitigation requirements.

## Dependencies and integration points

Dependencies include `exception-64s.h`, `head-64.h`, PACA and `pt_regs` offsets, IRQ soft-mask constants, KUP/KUAP helpers, CPU/MMU feature fixups, KVM Book3S handlers, and common return code from `interrupt_64.S`. C integration includes `do_IRQ`, `timer_interrupt`, `do_page_fault`, `do_hash_fault`, `do_slb_fault`, `do_bad_segment_interrupt`, `machine_check_early`, `machine_check_exception_async`, `system_reset_exception`, `handle_hmi_exception`, `performance_monitor_exception_*`, `load_up_fpu`, `load_up_altivec`, TM unavailable handlers, and many unknown/facility handlers.

## Risks and invariants

The file is constrained by fixed vector sizes, relocatable branch reach, real-mode addressability, and exact register save order. Any change to entry size can break fixed offsets or branch ranges. KVM tests must run only on vectors that can be taken while guest state is active. MCE, SRESET, and HMI paths must avoid touching unsafe virtual memory too early. Soft-mask replay must not lose edge-triggered doorbells, decrementer events, or hard-mask requirements. Mitigation trampolines must preserve scratch state despite running in extremely constrained contexts.

## Test signals

Signals include successful boot across pseries, powernv, radix and hash MMU builds; correct syscall and scv behavior; external interrupts and timers under irq-disable stress; KVM guest interrupt exits; machine-check and HMI injection tests; PMU and watchdog NMI behavior; FP/Altivec/VSX unavailable lazy-load behavior; and runtime checks from BUG/WARN entries in stack or soft-mask paths. Build coverage should exercise relocatable, KVM HV/PR, transactional memory, denormalization, KUAP, and mitigation configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/exceptions-64s.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/fadump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/fadump.c

## Purpose

`fadump.c` implements PowerPC firmware-assisted dump support. FADump lets firmware preserve memory after a crash and boot a capture kernel without using kexec. The file discovers platform support from device tree, reserves crash-preservation memory, registers and unregisters dump regions with RTAS or OPAL platform operations, builds ELF core headers for `/proc/vmcore`, exposes sysfs/debugfs controls, and triggers firmware dump on panic or system reset paths.

## Important APIs, types, and functions

The central state object is static `struct fw_dump fw_dump`, whose platform callbacks live in `fw_dump.ops`. Public architecture functions include `early_init_dt_scan_fw_dump`, `fadump_reserve_mem`, `fadump_append_bootargs`, `is_fadump_memory_area`, `should_fadump_crash`, `is_fadump_active`, `is_fadump_reserved_mem_contiguous`, `crash_fadump`, `fadump_regs_to_elf_notes`, `fadump_update_elfcore_header`, `fadump_setup_cpu_notes_buf`, `fadump_free_cpu_notes_buf`, `fadump_cleanup`, `fadump_setup_param_area`, and `setup_fadump`.

Important static helpers calculate reservation sizes, split boot memory into firmware-copy regions, locate usable reservation memory while avoiding firmware reserved ranges, populate ELF headers and PT_LOAD segments, initialize crash headers, release preserved memory, process active dumps, and implement sysfs stores. Under `CONFIG_CMA`, `fadump_cma_init` exposes the boot-memory-sized portion of reserved dump memory to CMA when safe. Under `CONFIG_PRESERVE_FA_DUMP`, the file compiles a reduced path that preserves active dump memory for a later kernel.

## Control flow

Early device-tree scan sees root `reserved-ranges`, then `rtas` or `ibm,opal` nodes and delegates platform-specific FADump discovery. Kernel parameters `fadump=` and `fadump_reserve_mem=` set enablement, `nocma`, and legacy reservation size. `fadump_reserve_mem` runs early: if supported and enabled, it calculates boot memory size from `crashkernel=`, legacy parameter, or 5 percent of RAM with platform minimums; records boot memory regions; computes total reserve size; and either reserves all crash data on capture boot or locates and reserves a reusable dump area for normal boot.

At `subsys_initcall_sync`, `setup_fadump` creates sysfs/debugfs files, prints config, processes an active dump if present, or initializes platform memory structures and registers with firmware. On panic, `crash_fadump` wins a `crashing_cpu` cmpxchg, records registers, CPU mask, and vmcoreinfo in the firmware dump header, waits briefly for secondaries after system reset, then calls `fw_dump.ops->fadump_trigger`.

Capture-kernel processing validates the crash header magic, endianness, and layout sizes, allocates an ELF core header buffer, creates PT_NOTE entries for CPU notes and vmcoreinfo, creates PT_LOAD entries for relocated boot memory and surviving RAM excluding the permanent FADump area, lets platform code add CPU notes, and publishes `elfcorehdr_addr` for `/proc/vmcore`.

## State and persistence behavior

The main persistent state is `fw_dump`, including support flags, enabled state, active/registered state, reserved area start/size, boot memory topology, crash header address, CPU notes buffer, ELF core header buffer, and optional parameter area. Memory reservation state is persisted through memblock reservations and firmware registration. Sysfs state exposes enablement, registration, reserved memory size, hotplug readiness, release controls, and appended capture-kernel boot arguments. `reserved_mrange_info` tracks firmware reserved ranges and dynamically or statically allocated memory range arrays.

## Dependencies and integration points

The file integrates with RTAS and OPAL FADump backends via `rtas_fadump_dt_scan`, `opal_fadump_dt_scan`, and platform callbacks in `fw_dump.ops`. It depends on memblock, crash dump/vmcore infrastructure, ELF core helpers, CPU masks, panic notifier behavior through `crash_kexec_post_notifiers`, sysfs, debugfs, optional CMA, optional HugeTLB disabling in the capture kernel, and `/proc/vmcore` cleanup. It also consumes boot globals such as `boot_command_line`, `saved_command_line_len`, `memory_limit`, `ppc64_rma_size`, and `elfcorehdr_addr`.

## Risks and invariants

Reservation math is high risk: overlap with firmware reserved ranges, memory holes, `memory_limit`, CMA alignment, and firmware maximum copy sizes must be handled correctly or crash capture can corrupt live memory or fail to boot. Header compatibility checks protect against old magic, endian mismatch, and structure-size mismatch. Releasing dump memory invalidates `/proc/vmcore`; ordering around `elfcorehdr_addr = ELFCORE_ADDR_ERR`, CPU notes freeing, and firmware invalidation matters. Sysfs registration changes are mutex-protected, but crash triggering intentionally runs in panic context with minimal synchronization.

## Test signals

Validation includes boots with `fadump=on/off/nocma`, `crashkernel=`, legacy `fadump_reserve_mem=`, active dump capture boots, sysfs registration toggles, `release_mem`, `/proc/vmcore` readability, appended bootargs behavior, CMA initialization, memory hotplug expectations, and RTAS/OPAL backend coverage. Fault-injection signals include allocation failures for CPU notes or ELF core header, incompatible crash headers, too many boot memory holes, no suitable reserve range, and platform register/trigger failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/fadump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/firmware.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/firmware.c

## Purpose

`firmware.c` holds small shared PowerPC firmware feature state. On PPC64 it exports `powerpc_firmware_features`, and on pseries or KVM guest builds it detects whether the kernel is running as a KVM guest by inspecting the device tree `/hypervisor` node. The file is intentionally small but forms a common integration point for firmware capability checks and static-branch optimized guest checks.

## Important APIs, types, and functions

The PPC64 global `unsigned long powerpc_firmware_features __read_mostly` is exported with `EXPORT_SYMBOL_GPL`, allowing other GPL kernel code to check discovered firmware features. With `CONFIG_PPC_PSERIES` or `CONFIG_KVM_GUEST`, `DEFINE_STATIC_KEY_FALSE(kvm_guest)` declares a jump-label static key, also exported GPL. `check_kvm_guest` is a `core_initcall`, scheduled before `kvm_guest_init`, and enables the `kvm_guest` static branch when `/hypervisor` is compatible with `"linux,kvm"`.

## Control flow

Initialization is straightforward. `check_kvm_guest` calls `of_find_node_by_path("/hypervisor")`; if the node is missing it returns without changing state. If present, it calls `of_device_is_compatible` and enables the static branch with `static_branch_enable(&kvm_guest)` for `"linux,kvm"`. It releases the device-node reference with `of_node_put` and returns success. Since it is a core initcall, later KVM guest initialization can use the static key cheaply.

## State and persistence behavior

`powerpc_firmware_features` is read-mostly global state populated elsewhere in the architecture firmware discovery path. `kvm_guest` is a static key: once enabled, patched branch sites in other code can use the optimized true path without repeated device-tree checks. The only persistence handled directly here is the lifetime of the static global state; device-tree node references are not retained.

## Dependencies and integration points

Dependencies include `<asm/firmware.h>` for firmware feature declarations, `<asm/kvm_guest.h>` for the static key declaration, Linux OF helpers, jump-label static keys, and module export infrastructure. Integration points are pseries and generic KVM guest code that check `kvm_guest`, plus any PPC64 code reading `powerpc_firmware_features`.

## Risks and invariants

The main invariant is init ordering: the static key must be enabled before guest-specific initialization uses it, which is why the file uses `core_initcall(check_kvm_guest)`. Device-tree compatibility string accuracy determines detection. If firmware describes a KVM guest differently, this path will leave the key disabled. The node reference is correctly dropped; changes should preserve that ownership.

## Test signals

Useful signals are pseries/KVM guest boots where `/hypervisor` exists with `linux,kvm`, non-KVM pseries boots where it does not, and module or built-in users of `kvm_guest` seeing patched static-branch behavior. Build coverage should include PPC64, pseries, KVM guest, and configurations where the KVM guest block is not compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/fpu.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/fpu.S

## Purpose

`fpu.S` implements low-level floating-point register save, restore, and lazy-load support shared by PowerPC kernel entry code. It was split out from head code so chips using different `head-*.S` files can share the same FPU state operations. The file handles plain FP registers and, when `CONFIG_VSX` and CPU features allow, the corresponding VSX register state.

## Important APIs, entry points, and macros

Exported routines are `load_fp_state` and `store_fp_state`. Entry code also calls `_GLOBAL(load_up_fpu)` for lazy user FPU enablement, and C/assembly code calls `_GLOBAL(save_fpu)` to save a task's FPU state. `load_fp_state` and `load_up_fpu` are marked NOKPROBE where required because restore paths must not be instrumented.

Macros `REST_1FPVSR`, `REST_32FPVSRS`, and `SAVE_32FPVSRS` select either FPR or VSR operations. With VSX enabled, feature-fixup sections branch around FPR-only operations when `CPU_FTR_VSX` is present and use `REST_VSR`, `REST_32VSRS`, or `SAVE_32VSRS`; otherwise they use `REST_FPR`, `REST_32FPRS`, and `SAVE_32FPRS`.

## Control flow

`load_fp_state(r3)` assumes FP is already enabled in MSR, restores FPSCR from `FPSTATE_FPSCR(r3)`, then restores all FP or VSR registers from the supplied state area. `store_fp_state(r3)` saves all registers, reads FPSCR with `mffs`, stores it, restores register 0 from memory to undo the scratch use, and returns.

`load_up_fpu` is entered from FP-unavailable exceptions. It reads MSR, sets `MSR_FP`, sets `MSR_RI` on Book3S 64 to allow recovery while accessing current state, and conditionally sets `MSR_VSX`. It updates the saved return MSR in the exception frame to enable FP after return, ORs in the task `THREAD_FPEXC_MODE`, marks `THREAD_LOAD_FP`, restores the task FP state, and returns through the exception return path. The 32-bit and 64-bit paths differ in where current thread and saved MSR live.

`save_fpu(tsk)` computes the task thread pointer, chooses either `THREAD_FPSAVEAREA` or `THREAD_FPSTATE`, saves all registers and FPSCR, restores register 0, and returns with FPU usable by the kernel.

## State and persistence behavior

Persistent state lives in `thread_struct` fields such as `THREAD_FPSTATE`, `THREAD_FPSAVEAREA`, `THREAD_FPEXC_MODE`, `THREAD_LOAD_FP`, and `PT_REGS`. On 64-bit, `PACACURRENT`, saved `_MSR`, and `PACASRR_VALID` are involved in exception return consistency. Hardware state includes MSR FP/VSX bits, FPSCR, and the FP/VSR register file.

## Dependencies and integration points

The file depends on register offsets from `asm-offsets.h`, `ptrace` frame layout, thread and PACA conventions, CPU feature fixup infrastructure, `ppc_asm` register-save macros, and exception handlers in `exceptions-64e.S`, `exceptions-64s.S`, and 32-bit exception code. It integrates with lazy FPU management, restore-math paths, task switching, transactional memory/facility exception paths indirectly, and exported users that need explicit FP state save/restore.

## Risks and invariants

Callers must enable FP before using `load_fp_state` or `store_fp_state`. Register 0 is used as FPSCR scratch and must be restored to avoid corrupting task state. `load_up_fpu` is constrained by exception-return clobber rules, especially on 32-bit where only selected registers are safe. Book3S 64 sets RI because HPT can fault on current access; removing that risks unrecoverable faults. VSX feature patching must match state layout or VSR/FPR halves can be corrupted.

## Test signals

Signals include user floating-point programs after context switches, lazy FP unavailable faults, VSX-enabled workloads, kernel warnings for illegal kernel FP use, suspend/resume or signal restore paths that call FP save/restore, and stress tests with preemption and SMP. Build coverage should include PPC32, PPC64 Book3S, VSX and non-VSX CPUs, and configurations without `CONFIG_VSX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/fpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_32.h

## Purpose

`head_32.h` defines shared 32-bit PowerPC exception-entry macros used by 32-bit head assembly files. It constructs the physical-mode exception prolog, switches to virtual execution, builds `pt_regs`, handles syscall entry, supports KVM vector hooks on Book3S, and provides a VMAP stack overflow emergency path.

## Important APIs, entry points, and macros

The main macros are `EXCEPTION_PROLOG`, `EXCEPTION_PROLOG_0`, `EXCEPTION_PROLOG_1`, `EXCEPTION_PROLOG_2`, `COMMON_EXCEPTION_PROLOG_END`, `prepare_transfer_to_handler`, `SYSCALL_ENTRY`, `START_EXCEPTION`, `EXCEPTION`, and `vmap_stack_overflow_exception`. They are not C APIs; they are included by 32-bit PowerPC assembly files to generate vector-specific handlers. The macros rely on SPR scratch registers, `SPRN_SPRG_THREAD`, SRR0/SRR1, DAR/DSISR, and stack layout offsets.

## Control flow

`EXCEPTION_PROLOG_0` saves scratch GPRs in SPRGs, loads the physical thread pointer, optionally saves DAR/DSISR, saves SRR0/SRR1 into the thread area, captures CR, and determines user versus kernel mode from `MSR_PR`. `EXCEPTION_PROLOG_1` saves the original stack pointer, chooses the interrupted kernel stack or the current task's kernel stack for user exceptions, and checks for VMAP stack overflow when configured. `EXCEPTION_PROLOG_2` programs SRR0/SRR1 to return to a virtual-mode continuation, executes `rfi`, then saves registers into the new interrupt frame and enables recoverable kernel MSR state.

`COMMON_EXCEPTION_PROLOG_END` marks the frame, stores trap number, saves volatile and nonvolatile registers, records NIP/MSR/CTR/XER, sets `r2` to current task, and passes a `pt_regs` pointer in `r3`. `prepare_transfer_to_handler` invokes 32-bit Book3S transfer preparation and optional KUEP locking for user-originated exceptions. `SYSCALL_ENTRY` is a syscall-specific fast path that builds only the needed frame state before branching to `transfer_to_syscall`.

## State and persistence behavior

The macros use physical `thread_struct` storage for SRR0/SRR1 and optional DAR/DSISR before translation is restored, then store the canonical state in the interrupt frame on the kernel stack. SPRG scratch registers temporarily hold original GPRs and stack pointer. For VMAP stack overflow, the code switches to per-CPU `emergency_ctx` storage before building the frame.

## Dependencies and integration points

Dependencies include `asm/ptrace.h` for `STACK_FRAME_REGS_MARKER`, thread and stack offsets, `SAVE_GPRS`/`SAVE_NVGPRS`, KVM `DO_KVM` hooks on Book3S, KUEP helpers, 8xx special handling, and the surrounding head files that define concrete vectors. Generated paths dispatch to C handlers and then branch to `interrupt_return`; syscall paths branch to `transfer_to_syscall`.

## Risks and invariants

The code runs with address translation off at entry, so physical versus virtual address transitions must remain exact. Register ordering matters because only scratch SPRs are available before a stack is selected. The VMAP overflow check relies on stack alignment bits in CR fields. `EXCEPTION_PROLOG_2` must set a recoverable MSR at the correct point; enabling exceptions too early or too late can break machine-check and page-fault behavior. Any change to `pt_regs` offsets must be reflected in assembly offsets.

## Test signals

Signals include booting 32-bit Book3S/BookE/8xx configurations, syscall ABI tests, page fault and alignment exception tests, KVM Book3S interrupt handling, VMAP stack overflow diagnostics, KUEP behavior on user transitions, and interrupt-return stress under preemption and SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_44x.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_44x.S

## Purpose

`head_44x.S` is the 32-bit PowerPC 44x/47x kernel entry and exception head. It handles initial CPU state, early relocation and dynamic memory-start calculations, stack and current-task setup, transition into `start_kernel`, BookE vector definitions, fast-path 44x and 47x TLB miss handlers, IVOR/IVPR setup, machine-check fixups, and secondary 47x CPU entry.

## Important APIs, entry points, and labels

Global entry labels include `_stext`, `_start`, `__fixup_440A_mcheck`, `init_cpu_state`, and, under SMP 47x, `start_secondary_47x`. Important internal labels include `interrupt_base`, `finish_tlb_load_44x`, `finish_tlb_load_47x`, `head_start_47x`, `clear_all_utlb_entries`, `clear_utlb_entry`, `head_start_common`, and `temp_boot_stack`. The file uses macros from `head_booke.h`, including `CRITICAL_EXCEPTION`, `MCHECK_EXCEPTION`, `DATA_STORAGE_EXCEPTION`, `INSTRUCTION_STORAGE_EXCEPTION`, `EXCEPTION`, `ALIGNMENT_EXCEPTION`, `PROGRAM_EXCEPTION`, `FP_UNAVAILABLE_EXCEPTION`, `SYSCALL_ENTRY`, `DECREMENTER_EXCEPTION`, and `DEBUG_CRIT_EXCEPTION`.

## Control flow

Boot starts at `_start`, preserves the device tree pointer in `r31`, sets CPU number zero, optionally relocates a relocatable kernel, and calls `init_cpu_state`. It then initializes current task/thread pointers in `r2` and SPRG thread state, sets the initial stack, calls `early_init`, records physical/virtual offsets for relocatable or dynamic memory-start builds, optionally runs KASAN early init, calls `machine_init` and `MMU_init`, stores Abatron debug PTE pointers, clears MCSR, and jumps via SRR0/SRR1/RFI to `start_kernel`.

`interrupt_base` defines BookE vectors. Most vectors delegate to common macros, but data and instruction TLB errors are hand-coded fast paths. For 44x, TLB miss code saves scratch registers, determines kernel versus user address, selects `swapper_pg_dir` or current `PGDIR`, sets MMUCR TID from PID, rejects KUAP faults when PID is zero, loads PTE high/low words, checks permissions, rotates `tlb_44x_index` with patched high-water marks, and branches to `finish_tlb_load_44x` to write TLB words and return with `rfi`. On bailout it restores registers and branches to `DataStorage` or `InstructionStorage`.

47x TLB paths are similar but use 47x word formats, UTLB way handling, ordering barriers for SMP, and `finish_tlb_load_47x`. `init_cpu_state` distinguishes 44x from 476-class cores using PVR, invalidates old translations while preserving the executing entry, bolts a kernel mapping, optionally maps early debug UART, configures IVORs, and sets IVPR in `head_start_common`.

## State and persistence behavior

The file persists CPU state in SPRs: PID, MMUCR, IVPR/IVORs, CCR0, MCSR, SRR0/SRR1, and TLB entries. Kernel globals updated include `kernstart_addr`, `virt_phys_offset`, `abatron_pteptrs`, and `tlb_44x_index`. Secondary 47x startup uses `secondary_current` and a small static `temp_boot_stack` until normal stacks are reachable.

## Dependencies and integration points

Dependencies include BookE head macros, 44x/47x TLB constants, page table formats, patch sites for TLB high-water marks, KASAN, machine and MMU initialization C code, early debug configuration, secondary CPU C entry `start_secondary`, and generic handlers for exceptions not satisfied by fast TLB insertion. It is the root assembly entry for 44x platform builds.

## Risks and invariants

Fast TLB miss handlers are extremely sensitive to PTE format, permission bit mapping, PID/MMUCR setup, and scratch SPR use. A wrong bailout path can corrupt interrupted state. Boot mapping assumes firmware has provided a usable initial translation, and early relocation assumes 256 MB alignment constraints. IVOR offsets must match vector labels. On 47x, clearing UTLB entries and restoring the original entry must avoid invalidating the executing mapping too early.

## Test signals

Signals include boot on 44x and 476/47x systems, early serial debug, instruction and data TLB miss stress, user versus kernel page faults, KUAP fault behavior, SMP secondary 47x bring-up, machine-check vector fixup on 440A, syscall and decrementer tests, and builds with relocatable, dynamic memory-start, KASAN, early debug, FPU, watchdog, and SMP options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_44x.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_64.S

## Purpose

`head_64.S` is the common 64-bit PowerPC kernel entry file. It contains the first 256 bytes of real-mode entry and secondary hold code, includes Book3S exception vectors or opens Book3E text, includes common interrupt return code, handles Book3E thread start/stop helpers, initializes secondary CPUs, manages Open Firmware and kexec/OPAL entry paths, relocates or copies the kernel, turns on 64-bit mode and relocation, clears BSS, calls early setup, and finally enters `start_kernel`.

## Important APIs, entry points, and labels

Primary global entry is `__start`. Fixed low-memory secondary coordination labels are `__secondary_hold_spinloop`, `__secondary_hold_acknowledge`, optional `__run_at_load`, and `__secondary_hold`. Book3E helpers include `book3e_start_thread`, `book3e_stop_thread`, `fsl_secondary_thread_init`, and use of `book3e_secondary_core_init` and `book3e_secondary_thread_init` from the Book3E exception file. SMP entries include `generic_secondary_smp_init`, `pmac_secondary_start`, `__secondary_start`, and `start_secondary_resume`. Other important routines are `copy_and_flush`, `enable_64b_mode`, `relative_toc`, and local Book3S helpers `__mmu_off` and `start_initialization_book3s`.

## Control flow

Execution begins at `__start`, fixes endian state, and branches to `__start_initialization_multiplatform`. Secondary CPUs can enter the low-address `__secondary_hold` loop, write their hardware CPU id to the acknowledge slot, and wait for a real address in `__secondary_hold_spinloop`. The common initialization path enables 64-bit mode, poisons PACA/TOC until initialized, distinguishes Open Firmware entry from kexec-style entry by `r5`, saves boot parameters, computes a runtime TOC, runs Book3E or Book3S early initialization, and derives the current runtime base.

For Open Firmware trampoline builds, `__boot_from_prom` runs at physical address, optionally relocates to the current address, calls `prom_init`, and does not return. After prom or kexec entry, `__after_prom_start` processes relocatable mode, optionally runs `relocate`, updates Book3E IVPR after relocation, copies the kernel from runtime base to `PAGE_OFFSET` or only copies interrupt regions for run-at-load cases, flushes dcache and icache through `copy_and_flush`, and branches to `start_here_multiplatform`.

At `start_here_multiplatform`, the file recomputes TOC, clears BSS, records OPAL debug entry when enabled, sets RI on Book3S, records `kernstart_addr` for relocatable kernels, builds the initial stack, optionally runs KASAN early init, calls C `early_setup`, then uses SRR0/SRR1 and RFI to enter `start_here_common` with relocation enabled. `start_here_common` stores the kernel stack in PACA, loads TOC, marks interrupts soft and hard disabled, and calls `start_kernel`.

Secondary CPU flow maps physical IDs to PACA entries, uses emergency stacks until normal stacks are safe, optionally restores CPU state, waits on `PACAPROCSTART`, calls `early_setup_secondary`, enables relocation, and enters `start_secondary`.

## State and persistence behavior

The file owns fixed low-memory state used by bootloaders and secondary CPUs: spinloop target, acknowledge word, and `__run_at_load`. It initializes PACA (`SPRG_PACA`, `r13`), `PACAKSAVE`, IRQ soft-mask fields, `kernstart_addr`, optional OPAL entry storage, and Book3E `booting_thread_hwid`. It also manipulates MSR, SRR0/SRR1, HID4 on PowerMac, PIR/TIR/TENS/TENC on Book3E threaded cores, and cache state during copying.

## Dependencies and integration points

`head_64.S` includes `exceptions-64s.S` for Book3S and `interrupt_64.S` for common interrupt return code. It calls C functions `prom_init`, `early_setup`, `early_setup_secondary`, `start_kernel`, and `start_secondary`, plus platform CPU restore callbacks through `cur_cpu_spec`. It integrates with relocatable kernel support, kexec, OPAL, Open Firmware, pseries secondary startup, PowerMac secondary startup, Book3E initialization, KASAN, and PACA allocation.

## Risks and invariants

This code executes before normal C runtime exists. TOC, PACA, stack, endian mode, relocation state, and cache coherency must be handled in the right order. The first 256-byte section has fixed offsets known to external tools and boot protocols. Secondary hold code must fit below the first exception vector. Kernel copying must avoid executing stale icache lines. Relocatable `__run_at_load` behavior is known to kexec tools and must not move unexpectedly. Branches before relocation must remain position-safe.

## Test signals

Signals include successful pseries, powernv/OPAL, kexec, Open Firmware trampoline, relocatable and run-at-load boots; SMP secondary bring-up and hotplug; PowerMac secondary starts; Book3E threaded core selection; KASAN early boot; correct `kernstart_addr`; and absence of early traps before `start_kernel`. Build coverage should include Book3S, Book3E, SMP, kexec, relocatable, PPC_OF_BOOT_TRAMPOLINE, OPAL early debug, and PowerMac options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_64.S -->
