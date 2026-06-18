# Research Report: subset-b-000886

This grouped report covers x86 kernel FPU xstate, boot entry, ftrace, FRED, HPET, legacy timers/PIC/DMA, IDT, I/O permissions, IRQ dispatch, and related low-level helpers under `sources/distributed-fs/ceph-client/arch/x86/kernel/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/xstate.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/xstate.c

## Purpose
Implements x86 XSAVE/XRSTOR state discovery, sizing, initialization, UABI conversion, dynamic xstate permissioning, XFD-driven fpstate growth, and coredump/proc reporting for extended FPU state. It is central to boot-time FPU capability selection and runtime management of AVX, AVX-512, PKRU, CET, AMX tile state, APX, and KVM guest supervisor state.

## Important APIs, Types, And State
Key exported or integration APIs include `cpu_has_xfeatures()`, `fpu__init_cpu_xstate()`, `fpu__init_system_xstate()`, `fpu__resume_cpu()`, `get_xsave_addr()`, `get_xsave_addr_user()`, `copy_xstate_to_uabi_buf()`, `copy_uabi_from_kernel_to_xstate()`, `copy_sigframe_from_user_to_xstate()`, `xsaves()`, `xrstors()`, `fpstate_clear_xstate_component()`, `__xfd_enable_feature()`, `xfd_enable_feature()`, `xstate_get_guest_group_perm()`, `fpu_xstate_prctl()`, and optional `proc_pid_arch_status()` / ELF coredump note writers. Persistent global tables cache `xstate_offsets[]`, `xstate_sizes[]`, `xstate_flags[]`, and `xfeature_uncompact_order[]` after CPUID enumeration. It mutates global FPU configs (`fpu_kernel_cfg`, `fpu_user_cfg`, `guest_default_cfg`) and per-task/group permission and fpstate buffers.

## Control Flow
Boot flow starts in `fpu__init_system_xstate()`: it enumerates CPUID xstate leaves, filters features against normal CPU feature bits and XSAVES/XFD support, computes default host/user/guest masks, enables OSXSAVE via `fpu__init_cpu_xstate()`, caches component layout, validates hardware-reported sizes against C structs, updates ptrace regset sizing, initializes `init_fpstate`, and sets `X86_FEATURE_OSXSAVE`. Per-CPU resume restores XCR0, IA32_XSS, and XFD. UABI output builds uncompacted user buffers from compacted kernel state, filling init or zero state when components are absent; UABI input validates headers, MXCSR reserved bits, user feature masks, copies components back, and preserves supervisor bits. Dynamic permission flow uses `arch_prctl()` through `fpu_xstate_prctl()`, validates signal altstack capacity, updates per-process permission masks, then XFD faults call `__xfd_enable_feature()` to allocate a larger `fpstate`.

## Dependencies And Integration Points
Depends on CPUID leaves `CPUID_LEAF_XSTATE` and tile leaves, CR4 OSXSAVE, XCR0, IA32_XSS, IA32_XFD, x86 signal/ptrace regsets, KVM guest FPU state, pkeys/PKRU, coredump note emission, `/proc/<pid>/arch_status`, and static keys for dynamic state sizing. KVM relies on `get_xsave_addr()`, `fpstate_clear_xstate_component()`, and guest permission export.

## Risks And Test Signals
High-risk areas are ABI layout stability, compacted vs uncompacted offset calculation, stale PKRU handling, XFD/fpstate races, supervisor state masking, and AMX/APX struct-size checks. Test signals include boot logs for enabled xfeatures and context size, ptrace/signal XSAVE round trips, AMX permission and altstack failure cases, XFD fault enablement, KVM guest xstate tests, coredump `NT_X86_XSAVE_LAYOUT`, suspend/resume FPU state restoration, and warnings from `XSTATE_WARN_ON()` or xsave fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/xstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/xstate.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/xstate.h

## Purpose
Provides internal FPU xstate helpers, declarations, and inline assembly wrappers for saving/restoring XSAVE state in kernel and signal-frame contexts. It is the contract between the generic FPU code and `xstate.c`.

## Important APIs, Types, And State
Defines `enum xstate_copy_mode`, declarations for UABI copy helpers, system/per-CPU init functions, and `get_xsave_addr_user()`. Inline helpers include `xstate_init_xcomp_bv()`, `xstate_get_group_perm()`, `xfeatures_mask_supervisor()`, `xfeatures_mask_independent()`, signal-frame PKRU helpers, `xfd_set_state()`, `xfd_update_state()`, `os_xsave()`, `os_xrstor()`, `os_xrstor_supervisor()`, `xsave_to_user_sigframe()`, `xrstor_from_user_sigframe()`, and `os_xrstor_safe()`. On x86-64 it declares per-CPU `xfd_state`.

## Control Flow And State Behavior
Save/restore wrappers choose XSAVE, XSAVEOPT, XSAVEC, XSAVES, XRSTOR, or XRSTORS through alternatives and exception-table fixups. Kernel saves use `fpstate->xfeatures`, validate XFD state under debug builds, and warn on kernel-buffer faults. Signal-frame saves force standard, uncompacted XSAVE ABI format and optionally omit init-optimized dynamic features; they update PKRU in the userspace buffer. Restores from userspace use `stac()`/`clac()` and return trap-derived errors rather than taking raw exceptions. XFD helpers keep the IA32_XFD MSR synchronized with the cached per-CPU value.

## Dependencies And Integration Points
Uses asm xstate definitions, feature alternatives, exception table types, MSR accessors, pkey/PKRU helpers, task FPU state, and signal code. It is included by xstate implementation and lower FPU context-switch paths.

## Risks And Test Signals
Risks include wrong feature masks causing #GP/#PF, signal ABI regressions from compacted-format leakage, stale XFD MSR values, and missing PKRU marking in signal frames. Tests should exercise XSAVE/XRSTOR under multiple CPU feature combinations, signal delivery/return with PKRU and AMX, debug FPU validation, and fault injection for user sigframe copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/xstate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fred.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fred.c

## Purpose
Initializes Flexible Return and Event Delivery (FRED) exception delivery for x86 CPUs and programs FRED stack levels and RSP slots.

## Important APIs, Types, And State
Exports per-CPU `fred_rsp0` and defines `cpu_init_fred_exceptions()` and `cpu_init_fred_rsps()`. Stack level macros assign kernel #DB to level 1, NMI and #MC to level 2, and #DF to level 3. The code programs MSRs `MSR_IA32_FRED_CONFIG`, `MSR_IA32_FRED_STKLVLS`, and `MSR_IA32_FRED_RSP0..3`.

## Control Flow And Persistence
`cpu_init_fred_exceptions()` loads `SS` with `__KERNEL_DS`, writes the user entrypoint and redzone/interrupt-stack config, restores cached RSP0 after offline/online cycles, zeros RSP1-RSP3, enables `X86_CR4_FRED`, invalidates the IDT to catch accidental IDT use, and disables fast 32-bit syscall capabilities. `cpu_init_fred_rsps()` must run after CPU entry areas exist and maps FRED stack levels to the DB/NMI/DF IST top addresses.

## Dependencies And Integration Points
Integrates with descriptor/IDT code, CPU entry area IST helpers, trap vectors, CR4, and syscall capability setup. IRQ init calls `fred_complete_exception_setup()` elsewhere before selecting FRED vs IDT delivery.

## Risks And Test Signals
Risks are wrong stack-level assignment, stale RSP0 after CPU hotplug, invalid SS in early kernel events, and accidental IDT use after FRED activation. Test signals include FRED boot, CPU hotplug, NMI/#DB/#DF/#MC delivery, 32-bit syscall compatibility, and absence of #GP on first return to user mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace.c

## Purpose
Provides x86 dynamic ftrace text patching, ftrace callback target updates, runtime trampoline allocation, and function graph return hook support.

## Important APIs, Types, And State
Implements `ftrace_arch_code_modify_prepare()`, `ftrace_arch_code_modify_post_process()`, `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, `ftrace_replace_code()`, `arch_ftrace_update_code()`, x86-64 trampoline functions (`arch_ftrace_update_trampoline()`, `arch_ftrace_trampoline_func()`, `arch_ftrace_trampoline_free()`), graph toggles, `prepare_ftrace_return()`, and optional `ftrace_graph_func()`. State includes `ftrace_poke_late`, dynamically allocated executable trampolines, and patched call/jump sites.

## Control Flow
Dynamic ftrace first verifies existing instruction bytes with `copy_from_kernel_nofault()`, then patches either directly during early/module load or through batched SMP text pokes under `text_mutex`. `ftrace_replace_code()` scans ftrace records, verifies all old call/nop encodings, then applies all new encodings and updates record state. Trampoline creation copies assembly caller stubs, appends a return thunk or ret, embeds an ops pointer, patches the callback call, and marks pages ROX. Function graph tracing patches `ftrace_graph_call` between a stub and graph caller, and return preparation replaces the saved return address with `return_to_handler` when graph entry succeeds.

## Dependencies And Integration Points
Depends on x86 text patching, execmem, ftrace core record iteration, module load paths, retpoline/rethunk choices, assembly labels in `ftrace_64.S`, and function graph tracer core.

## Risks And Test Signals
Risks include patching wrong bytes, racing module/livepatch text permission changes, broken trampoline layout if assembly labels move, W^X violations, and return-hook corruption. Tests should enable/disable dynamic ftrace, graph tracer, direct calls, regs callbacks, module tracing, livepatch coexistence, and inspect ftrace bug reports from verification failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace_32.S

## Purpose
Implements 32-bit x86 ftrace assembly entry stubs for fentry/mcount callbacks, regs callbacks, direct trampolines, and function graph return redirection.

## Important APIs And Labels
Exports `__fentry__`; defines `ftrace_caller`, `ftrace_call`, `ftrace_graph_call`, weak `ftrace_stub`, `ftrace_regs_caller`, `ftrace_regs_call`, `ftrace_stub_direct_tramp`, `ftrace_graph_caller`, and `return_to_handler`.

## Control Flow And State
`ftrace_caller` preserves the minimal caller-saved register set, fabricates frame-pointer state when needed, computes traced IP as return address minus `MCOUNT_INSN_SIZE`, loads parent IP and `function_trace_op`, and calls the patched target at `ftrace_call`. `ftrace_regs_caller` builds a pt_regs-like frame, passes it as the fourth argument, permits callback-modified IP/EAX restoration, and returns through the normal stub path. Graph caller invokes `prepare_ftrace_return()`, and `return_to_handler` calls `ftrace_return_to_handler()` then jumps indirectly to the restored return target.

## Dependencies And Integration Points
Tightly coupled to `ftrace.c`, x86 calling conventions, `asm-offsets.h` pt_regs offsets, frame-pointer configuration, retpoline macros, and function graph tracer core.

## Risks And Test Signals
Risks include stack layout drift, wrong frame-pointer emulation, register clobbering, incorrect parent IP extraction, and unsafe indirect return. Test signals are successful 32-bit ftrace callbacks with and without frame pointers, regs callbacks, graph tracing, direct trampolines, and objtool/unwind validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace_64.S

## Purpose
Implements 64-bit x86 ftrace assembly stubs for dynamic and non-dynamic fentry, regs-aware tracing, graph tracing, direct call handling, return thunks, and IBT/retpoline-safe control transfer.

## Important APIs And Labels
Exports `__fentry__`; defines typed `ftrace_stub`, `ftrace_stub_graph`, `ftrace_caller`, `ftrace_caller_op_ptr`, `ftrace_call`, `ftrace_caller_end`, `ftrace_regs_caller`, `ftrace_regs_caller_op_ptr`, `ftrace_regs_call`, `ftrace_regs_caller_jmp`, `ftrace_regs_caller_end`, `ftrace_stub_direct_tramp`, and `return_to_handler`.

## Control Flow And State
Macros `save_mcount_regs` and `restore_mcount_regs` create the stack and pt_regs-compatible layout expected by C callbacks. Dynamic mode routes `__fentry__` to a cheap return until ftrace patches sites. `ftrace_caller` saves volatile registers, computes `ip` and parent IP, loads `function_trace_op`, supplies a regs pointer, and permits callback-modified RIP. `ftrace_regs_caller` saves full pt_regs state and uses `ORIG_RAX` to encode direct-call behavior. `return_to_handler` builds exit regs, calls `ftrace_return_to_handler()`, then returns via a retpoline/RSB-balanced pattern.

## Dependencies And Integration Points
Coupled with trampoline cloning in `ftrace.c`; label offsets are copied into executable trampolines. Depends on CFI/IBT annotations, call-depth accounting, unwind hints, pt_regs offsets, retpoline alternatives, and function graph tracer core.

## Risks And Test Signals
Risks include breaking trampoline layout, incorrect unwind metadata, missed ENDBR/no-ENDBR annotations, direct-call stack imbalance, and handler-modified RIP corruption. Tests should exercise dynamic ftrace with args, regs and non-regs callbacks, graph tracer, direct trampoline calls, IBT-enabled kernels, retbleed/call-depth mitigations, and objtool checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/head32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/head32.c

## Purpose
Prepares 32-bit x86 C boot flow after early assembly: sets early platform hooks, installs early IDT, loads microcode, sanitizes boot parameters, and builds early page tables.

## Important APIs And State
Defines `i386_start_kernel()`, `mk_early_pgtbl_32()`, and helper `init_map()`. With `CONFIG_MICROCODE_INITRD32`, tracks `initrd_start_early`, `initrd_pl2p_start`, and `initrd_pl2p_end` so temporary initrd mappings can be removed after microcode loading.

## Control Flow
`i386_start_kernel()` installs early handlers, loads BSP microcode, zaps early initrd mappings, initializes CR4 shadow, sanitizes boot params, runs early platform quirks, selects subarchitecture setup, then calls `start_kernel()`. `mk_early_pgtbl_32()` creates identity and PAGE_OFFSET mappings for the kernel and lowmem page tables, records `max_pfn_mapped` and `_brk_end`, and optionally maps the initrd early enough for 32-bit microcode loading.

## Dependencies And Integration Points
Depends on boot params from assembly, IDT setup, microcode loader, x86 platform init hooks, IO-APIC/APIC setup callbacks, memblock/brk space, PAE vs non-PAE page table formats, and subarch setup.

## Risks And Test Signals
Risks include early mapping limits, incorrect physical/virtual pointer writes before paging is fully stable, leaked initrd mappings, and wrong subarch resource callbacks. Test signals include 32-bit boot across PAE/non-PAE, microcode-in-initrd boot, kexec boot params, early page faults, and successful transition to `start_kernel()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/head32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/head64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/head64.c

## Purpose
Implements early 64-bit C boot setup: dynamic early page table creation, early exception handling, BSS clearing, bootdata copying, SME/TDX/KASAN ordering, and handoff to generic kernel startup.

## Important APIs And State
Defines early page table globals (`early_dynamic_pgts`, `next_early_pgt`, `early_pmd_flags`, `__pgtable_l5_enabled`, `pgdir_shift`, `ptrs_per_p4d`, `page_offset_base`, `vmalloc_base`, `vmemmap_base`) plus `__early_make_pgtable()`, `do_early_exception()`, `clear_bss()`, `x86_64_start_kernel()`, `x86_64_start_reservations()`, and `early_setup_idt()`.

## Control Flow
`x86_64_start_kernel()` resets early page tables, adjusts L5 paging bases, clears BSS/brk, clears `init_top_pgt`, initializes SME before page faults can occur, initializes KASAN, flushes global TLBs, installs early IDT, initializes TDX, copies boot params and command line, loads microcode, seeds the top-level kernel mapping, and calls reservations. Early page faults call `do_early_exception()`, which can lazily build PMD mappings, handle SEV #VC or TDX #VE, or fall back to exception fixups.

## Dependencies And Integration Points
Integrates with assembly `head_64.S`, SME/SEV/TDX early code, KASAN, fixmap, boot params, microcode, early IDT, mem encryption mapping helpers, and exported virtual address base symbols used by the rest of the kernel.

## Risks And Test Signals
Risks include early page table exhaustion/reset behavior, SME decrypted bootdata mapping lifetime, CR3 assumptions, L5 address base selection, and exception handling before full IDT. Tests include 4-level and 5-level paging boots, KASAN boots, SME/SEV/TDX guests, early #PF mapping, kexec bootdata copy, and microcode loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/head64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/head_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/head_32.S

## Purpose
Provides the 32-bit x86 assembly boot entry for BSP and APs, establishes initial GDT/segments, copies boot parameters, creates early page tables, enables paging, detects basic CPU properties, and supplies early exception/IRQ handlers.

## Important Labels And State
Defines `startup_32`, `startup_32_smp`, `early_idt_handler_array`, `early_idt_handler_common`, `early_ignore_irq`, `early_recursion_flag`, `initial_code`, early page tables (`initial_pg_pmd` or `initial_page_table`, `initial_pg_fixmap`, `swapper_pg_dir`), `initial_stack`, `boot_gdt_descr`, `early_gdt_descr`, and `boot_gdt`.

## Control Flow And Persistence
BSP entry loads a temporary GDT, normalizes segments and stack, clears BSS, copies boot params and command line, saves OLPC page directory if configured, calls `mk_early_pgtbl_32()`, initializes fixmap mapping, then joins `.Ldefault_entry`. SMP entry reuses boot GDT assumptions. Common path configures CR0/CR4, detects CPUID and NX under PAE, enables paging, switches to virtual stack, records CPU vendor/model/caps, loads kernel GDT, sets percpu segment, clears LDT, and calls `initial_code`. Early IDT stubs create uniform trap frames and call `early_fixup_exception()`.

## Dependencies And Integration Points
Depends on boot protocol register conventions, `verify_cpu.S`, early page tables from `head32.c`, segment constants, per-CPU descriptors, printk for early ignored IRQs, Xen head inclusion, and later `i386_start_kernel()`.

## Risks And Test Signals
Risks include fragile stack/segment state, wrong PAE/NX setup, boot param copy before mappings cover memory, early exception recursion, and page table alignment/PTI layout. Tests include 32-bit BSP/AP boot, old CPUs without CPUID/CR4, PAE+NX, PTI, OLPC, kexec, early fault handling, and objtool/entry validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/head_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/head_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/head_64.S

## Purpose
Provides 64-bit x86 assembly startup for boot CPU, secondary CPUs, early IDT handlers, SEV/SME support, CR3/GDT/GS setup, and static initial page table definitions.

## Important Labels And State
Defines `startup_64`, `secondary_startup_64`, `secondary_startup_64_no_verify`, `common_startup_64`, optional `soft_restart_cpu`, `vc_boot_ghcb`, `early_idt_handler_array`, `early_idt_handler_common`, optional `vc_no_ghcb`, `initial_code`, `initial_vc_handler`, `trampoline_lock`, `early_top_pgt`, `early_dynamic_pgts`, `init_top_pgt`, `level4_kernel_pgt`, `level3_kernel_pgt`, `level2_kernel_pgt`, fixmap tables, `smpboot_control`, and exported `phys_base`.

## Control Flow And State
Boot CPU entry preserves `boot_params`, sets stack and GSBASE, loads temporary GDT/IDT, switches to kernel CS, enables SME/SEV if configured, verifies CPU, computes physical relocation delta, fixes page tables and encryption mask, switches CR3 to `early_top_pgt`, then jumps to `common_startup_64`. Secondary startup verifies CPU unless SEV-ES no-verify path, switches to `init_top_pgt`, preserves CR4 bits needed for PAE/LA57/MCE, resolves CPU number from APIC ID or `smpboot_control`, sets per-CPU stack and GSBASE, loads GDT, calls `early_setup_idt()`, enables EFER SCE/NX, sets CR0, and calls `initial_code`.

## Dependencies And Integration Points
Depends on compressed boot handoff, trampoline code, APIC/x2APIC, per-CPU offsets, SME/SEV/TDX helpers, restore_regs entry code, verify_cpu, initial page table constants, PTI layout, and `head64.c`.

## Risks And Test Signals
Risks include relocation/encryption mask mistakes, bad CR3 switch, stale real-mode stacks, APIC ID lookup failure, unsafe early #VC/#VE handling, and table alignment. Tests include direct 64-bit boot, compressed boot, SMP/parallel AP startup, CPU hotplug/soft restart, LA57, PTI, SEV/SEV-ES/SNP, TDX, and NX/EFER setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/head_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/hpet.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/hpet.c

## Purpose
Implements x86 HPET discovery, MMIO mapping, clocksource registration, legacy replacement clockevent, MSI per-CPU clockevents, hotplug handling, optional `/dev/hpet` reservation, suspend/resume restoration, and RTC interrupt emulation.

## Important APIs, Types, And State
Defines `struct hpet_channel`, `struct hpet_base`, globals `hpet_address`, `hpet_blockid`, `hpet_msi_disable`, `boot_hpet_disable`, `hpet_force_user`, and exported `is_hpet_enabled()` plus many RTC-emulation exports under `CONFIG_HPET_EMULATE_RTC`. Core APIs include `hpet_enable()`, `hpet_late_init()`, `hpet_disable()`, clockevent state callbacks, MSI domain helpers, and `read_hpet()`.

## Control Flow
Command-line parsing handles `hpet=disable,force,verbose` and `nohpet`. `hpet_enable()` checks capability and PC10 damage, maps MMIO, validates config register and period, computes frequency, allocates channel records, sanitizes global/channel config, validates counting, registers the clocksource, and if legacy routing is supported registers channel 0 as global clockevent. Late init optionally force-enables HPET, reserves a device channel, selects MSI clockevent channels, reserves platform timers, and registers CPU hotplug callbacks. MSI channels use an IRQ domain, allocate vectors, request IRQs, set affinity, and register per-CPU clockevents. RTC emulation uses channel 1 one-shot compares to synthesize UIE/AIE/PIE events.

## Dependencies And Integration Points
Depends on ACPI/quirk-provided `hpet_address`, clocksource/clockevents, generic MSI IRQ domains, x86 vector domain, APIC affinity, CPU hotplug state machine, `/dev/hpet` platform code, RTC core, PM suspend/resume, MWAIT/PC10 CPUID/MSR heuristics, and legacy IRQ replacement.

## Risks And Test Signals
Risks include unreliable HPET hardware, comparator programming races, forced HPET on PC10-damaged systems, incorrect channel reservation conflicts, MSI domain allocation failures, stale RTC emulation state, and slow HPET reads under high CPU counts. Tests include boot with/without HPET, `nohpet`/force/verbose, legacy IRQ mode, MSI per-CPU timers, CPU hotplug, suspend/resume, RTC alarm/update/periodic emulation, clocksource selection, and warnings for invalid config/counting/period.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/hpet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/hw_breakpoint.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/hw_breakpoint.c

## Purpose
Implements x86 perf hardware breakpoints using debug registers DR0-DR7, including validation, install/uninstall, ptrace cleanup, KVM restore support, and #DB notifier handling.

## Important APIs, Types, And State
Exports per-CPU `cpu_dr7`, `encode_dr7()`, `decode_dr7()`, `arch_install_hw_breakpoint()`, `arch_uninstall_hw_breakpoint()`, `arch_bp_generic_fields()`, `arch_check_bp_in_kernelspace()`, `hw_breakpoint_arch_parse()`, `flush_ptrace_hw_breakpoint()`, `hw_breakpoint_restore()`, `hw_breakpoint_exceptions_notify()`, and stub `hw_breakpoint_pmu_read()`. Per-CPU state tracks debug address registers in `cpu_debugreg[]` and occupying perf events in `bp_per_reg[]`.

## Control Flow
Parsing validates address range, excludes CPU entry/GDT/TSS/TLB/debug-register-sensitive ranges, enforces kprobe blacklist for kernel execute breakpoints, maps generic breakpoint types/lengths to x86 encodings, supports AMD range masks, and checks alignment. Installation finds a free DR slot with IRQs disabled, writes DRn, updates cached DR7 before hardware DR7, and applies AMD address masks. Uninstall clears the slot, writes hardware DR7 before cache, and clears masks. #DB notifier reads DR6, dispatches matching perf breakpoint events, clears handled trap bits, sets RF for execute breakpoints, and leaves user or multi-cause debug exceptions to generic debug handling.

## Dependencies And Integration Points
Integrates with perf events, ptrace debug registers, kprobes blacklist, KVM debug-register restore, die notifier `DIE_DEBUG`, CPU entry area definitions, AMD BPEXT masks, and x86 debug register helpers.

## Risks And Test Signals
Risks include debug-register cache/hardware ordering during NMIs, breakpoints on entry-critical memory causing recursive #DB, incorrect DR6 cause handling, AMD range mask validation, and ptrace/perf slot conflicts. Tests include perf user/kernel breakpoints, ptrace DR use, KVM guest switching, NMI-heavy scenarios, kprobe blacklisted addresses, CPU hotplug/restore, AMD range breakpoints, and alignment/error return cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/hw_breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/i8237.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/i8237.c

## Purpose
Registers syscore resume handling for the legacy 8237A ISA/LPC DMA controller when present.

## Important APIs And State
Defines `i8237A_resume()`, `i8237_syscore_ops`, `i8237_syscore`, and initcall `i8237A_init_ops()`. It does not allocate DMA channels; normal DMA use lives in generic DMA code and `asm/dma.h`.

## Control Flow And Persistence
Init probes for controller presence by checking DMA page port behavior and skips modern systems without legacy support based on PnP BIOS/BIOS year heuristics. If accepted, it registers a syscore resume callback. Resume claims the DMA lock, resets both DMA controllers, zeros all channel addresses, sets counts to one because of hardware count semantics, enables cascade channel 4, and releases the lock.

## Dependencies And Integration Points
Depends on legacy DMA I/O helpers, DMI BIOS year, x86 legacy-device policy, and syscore suspend/resume ordering.

## Risks And Test Signals
Risks include false-positive detection on systems decoding LPC POST ports, touching removed legacy ports, and failing to restore cascade DMA. Tests include suspend/resume on ISA/LPC DMA systems, modern SKL+ systems returning `-ENODEV`, and drivers using legacy DMA after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/i8237.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/i8253.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/i8253.c

## Purpose
Chooses and initializes the legacy PIT/i8253 as a clockevent or optional 32-bit clocksource when modern timers are unavailable or require PIT calibration.

## Important APIs And State
Defines global `struct clock_event_device *global_clock_event`, helper `use_pit()`, boot function `pit_timer_init()`, and 32-bit-only `init_pit_clocksource()`.

## Control Flow And Persistence
`use_pit()` returns true when TSC is absent or APIC setup needs PIT calibration. `pit_timer_init()` disables the PIT clockevent when unnecessary to avoid VMM overhead, or initializes `i8253_clockevent` and publishes it as `global_clock_event`. On non-64-bit builds, `init_pit_clocksource()` registers the PIT clocksource only when UP, HPET is not enabled, and the i8253 clockevent is still periodic.

## Dependencies And Integration Points
Depends on generic i8253 clockevent/clocksource code, APIC timer calibration policy, HPET status, hypervisor/platform timer behavior, and early time initialization.

## Risks And Test Signals
Risks include disabling PIT when APIC calibration still needs it, VMM CPU waste if PIT is left running, and poor clocksource scaling on SMP. Tests include boot with/without TSC, APIC disabled, HPET enabled, 32-bit UP PIT clocksource registration, and timer interrupt delivery during early boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/i8253.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/i8259.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/i8259.c

## Purpose
Implements the legacy 8259A Programmable Interrupt Controller abstraction for PC-compatible systems, including masking, acking, probing, ELCR save/restore, syscore power hooks, and a null PIC fallback.

## Important APIs, Types, And State
Exports `i8259A_lock`, `cached_irq_mask`, `io_apic_irqs`, `i8259A_chip`, `null_legacy_pic`, and global `legacy_pic`. Defines `legacy_pic_pcat_compat()`. Internal state includes `pcat_compat`, `i8259A_auto_eoi`, and saved `irq_trigger[]` ELCR values.

## Control Flow
Mask/unmask update `cached_irq_mask` under raw spinlock and write master/slave IMRs. `mask_and_ack_8259A()` masks first, detects likely spurious IRQ7/15 via ISR reads when masked, accounts errors, then sends specific EOIs in required slave/master order. `probe_8259A()` either trusts PCAT_COMPAT or writes/readbacks masks; failure switches `legacy_pic` to the null implementation. `init_8259A()` sends ICWs, maps vectors with `ISA_IRQ_VECTOR()`, configures AEOI behavior, waits, and restores masks. Syscore callbacks save/restore ELCR across suspend/resume and mask all on shutdown.

## Dependencies And Integration Points
Integrates with ISA IRQ setup, IO-APIC mixed routing, LAPIC legacy vector assignment, ACPI MADT PCAT_COMPAT, generic IRQ chips, syscore suspend, and low-level port I/O.

## Risks And Test Signals
Risks include fragile PIC programming order, spurious IRQ misclassification, systems without real PIC but legacy assumptions, incorrect AEOI behavior, and ELCR loss across suspend. Tests include legacy IRQ boot, IO-APIC mixed mode, ACPI PCAT_COMPAT, suspend/resume, spurious IRQ7/15 logging, cascade IRQ2 request, and modern no-PIC platforms using `null_legacy_pic`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/i8259.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ibt_selftest.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/ibt_selftest.S

## Purpose
Provides a tiny Indirect Branch Tracking selftest target that intentionally jumps indirectly to a function without ENDBR annotation.

## Important APIs And Labels
Defines `ibt_selftest_noendbr` with `ANNOTATE_NOENDBR` and `ibt_selftest`, which loads the no-ENDBR target address and performs an indirect jump marked retpoline-safe.

## Control Flow And State
The no-ENDBR target returns normally only if IBT is not enforcing or the #CP handler has made the expected adjustment; the comment notes the #CP handler sets `%ax` to zero. There is no persistent state in this file.

## Dependencies And Integration Points
Depends on objtool annotations, IBT/#CP exception handling, and nospec branch annotations. It is consumed by x86 CET/IBT selftest code elsewhere.

## Risks And Test Signals
Risks are annotation drift, jumping to a symbol that accidentally gets ENDBR, or #CP handler behavior changing. Test signals include CET/IBT boot selftests, expected control-protection exception handling, and objtool validation of unwind/no-ENDBR metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ibt_selftest.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/idt.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/idt.c

## Purpose
Builds and installs x86 IDT entries for early traps, default exceptions, IA32 syscall vector, APIC/SMP system vectors, normal external interrupt gates, spurious gates, and late read-only CPU-entry-area mapping.

## Important APIs And State
Defines IDT descriptor tables (`early_idts`, `def_idts`, `ia32_idt`, `apic_idts`), page-aligned `idt_table`, `idt_descr`, and `idt_setup_done`. Public functions include `load_current_idt()`, optional `idt_is_f00f_address()`, `idt_setup_early_traps()`, `idt_setup_traps()`, `idt_setup_early_pf()`, `idt_setup_apic_and_irq_gates()`, `idt_setup_early_handler()`, `idt_invalidate()`, and `idt_install_sysvec()`.

## Control Flow
Early boot can install generic early handler array entries for all exception vectors. Later trap setup installs explicit exception gates, with IST variants on 64-bit after TSS/CPU init, and IA32 syscall gates when enabled. `idt_setup_apic_and_irq_gates()` installs APIC/SMP vectors, fills remaining external vectors from `irq_entries_start`, fills remaining system vectors with spurious handlers, maps the IDT read-only into the CPU entry area, reloads it, marks backing memory RO, and freezes further sysvec installation. `idt_install_sysvec()` permits early dynamic system-vector reservation before final setup.

## Dependencies And Integration Points
Depends on descriptor helpers, trap assembly labels, APIC vector definitions, `system_vectors` bitmap, CPU entry area, set_memory RO, IA32 emulation, FRED invalidation use, and interrupt entry stubs.

## Risks And Test Signals
Risks include wrong DPL/IST/segment selection, missing system vector bitmap bits, late sysvec installation after IDT lock-down, leaking kernel IDT address, and F00F compatibility. Tests include early exception delivery, page fault transition, APIC/SMP vectors, IA32 int80, read-only IDT mapping, sysvec installation warnings, and FRED mode invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/idt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/io_delay.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/io_delay.c

## Purpose
Selects and implements the delay operation used by legacy `inb_p/outb_p` style I/O, with command-line and DMI quirks for systems that cannot tolerate port `0x80`.

## Important APIs And State
Exports `native_io_delay()` and global `io_delay_type`. Defines delay modes `0x80`, `0xed`, `udelay`, and `none`; `io_delay_override`; DMI quirk callback `dmi_io_delay_0xed_port()`; `io_delay_init()`; and early parameter parser `io_delay_param()`.

## Control Flow And Persistence
At boot the default mode is selected by Kconfig. `io_delay=` can force a mode and suppress DMI override. Without override, `io_delay_init()` scans known affected HP/Compaq/Quanta systems and switches from `0x80` to `0xed`. `native_io_delay()` performs the selected outb, a calibrated-ish `udelay(2)`, or nothing.

## Dependencies And Integration Points
Used by native/paravirt I/O delay paths and legacy port I/O helpers. Depends on DMI, early params, Kconfig defaults, and low-level port I/O.

## Risks And Test Signals
Risks include lockups from port `0x80`, inadequate delay timing before calibration, and removing bus side effects by using `udelay` or `none`. Tests include booting quirked laptop DMI profiles, `io_delay=` modes, legacy ISA/PIC/PIT access stability, and no regressions in paravirt native delay assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/io_delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ioport.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/ioport.c

## Purpose
Implements x86 user I/O port permission syscalls `ioperm` and `iopl` using task I/O bitmaps rather than CPU IOPL interrupt-disable privileges.

## Important APIs And State
Under `CONFIG_X86_IOPL_IOPERM`, defines `io_bitmap_sequence`, `io_bitmap_share()`, `io_bitmap_exit()`, `ksys_ioperm()`, `SYSCALL_DEFINE3(ioperm)`, and `SYSCALL_DEFINE1(iopl)`. Without support, the syscalls return `-ENOSYS`.

## Control Flow And Persistence
`ioperm()` validates range, enforces `CAP_SYS_RAWIO` and lockdown for enabling access, lazily allocates an all-denied bitmap, copy-on-writes shared bitmaps inherited by fork, clears bits to permit ports or sets bits to deny, computes active max size, frees the bitmap when all permissions are denied, and increments a sequence to force TSS update on return to user mode. `iopl()` emulates only level 3 as all-ports permission and never grants CLI/STI behavior; it updates per-thread `iopl_emul` and TIF_IO_BITMAP/TSS state.

## Dependencies And Integration Points
Depends on task `thread_struct` I/O bitmap fields, TSS update code, fork/exit hooks, capabilities, lockdown LSM, bitmap helpers, and syscall ABI.

## Risks And Test Signals
Risks include stale TSS bitmap after permission changes, refcount/copy-on-write mistakes across fork, privilege bypass under lockdown, and semantic differences from hardware IOPL. Tests include `ioperm()` ranges and overflow, fork inheritance, permission drop/free, `iopl(3)` all-port behavior, lockdown denial, and context-switch/user-return TSS updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ioport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/irq.c

## Purpose
Provides common x86 interrupt accounting, normal device IRQ dispatch, bad IRQ acknowledgement, platform/KVM/perf/posted-MSI system-vector handlers, `/proc/interrupts` reporting, and CPU-hotplug IRQ migration cleanup.

## Important APIs And State
Exports per-CPU `irq_stat`, `__softirq_pending`, `hardirq_stack_ptr`, and atomic `irq_err_count`. Key functions include `ack_bad_irq()`, `arch_show_interrupts()`, `arch_irq_stat_cpu()`, `arch_irq_stat()`, `common_interrupt`, `sysvec_x86_platform_ipi`, optional KVM posted-interrupt handlers and setter, posted-MSI helpers, `fixup_irqs()`, and thermal vector handling.

## Control Flow
`common_interrupt` sets irq regs, verifies RCU watching, dispatches by vector through per-CPU `vector_irq[]`, and EOIs bad vectors. Dispatch reevaluates shutdown/unused vectors under vector lock to close races with free/request IRQ. `/proc` and `/proc/stat` helpers aggregate arch counters. Posted MSI notification marks handler active, enters IRQ context, harvests PIR bits up to a bounded coalescing loop plus a final post-ON-clear pass, handles each pending vector, EOIs, and leaves IRQ context. CPU hotplug migrates off-CPU IRQs, retriggers pending vectors if possible, and clears vector slots.

## Dependencies And Integration Points
Depends on APIC EOI, vector allocator state from `irqinit.c`, generic IRQ descriptors, RCU/irq entry code, tracepoints, KVM posted interrupts, Intel posted MSI descriptors, irq remapping, thermal/MCE/perf modules, and CPU hotplug.

## Risks And Test Signals
Risks include vector shutdown races, missing APIC EOI on bad/retriggered vectors, posted-MSI lost notifications, incorrect irq context nesting, and stale counters. Tests include high-rate MSI, IRQ free/request races, CPU hotplug with pending IRQs, KVM posted interrupts, posted MSI coalescing, `/proc/interrupts` counters, thermal/perf vectors, and spurious vector handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irq_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/irq_32.c

## Purpose
Implements 32-bit x86 hardirq and softirq stack allocation/switching and low-stack overflow diagnostics before calling generic IRQ handling.

## Important APIs And State
Defines optional `sysctl_panic_on_stackoverflow`, per-CPU `softirq_stack_ptr`, `irq_init_percpu_irqstack()`, optional `do_softirq_own_stack()`, and `__handle_irq()`. It uses per-CPU `hardirq_stack_ptr` from common IRQ code.

## Control Flow
`irq_init_percpu_irqstack()` allocates per-CPU hardirq and softirq stacks with `THREAD_SIZE_ORDER`. `execute_on_irq_stack()` detects whether already on the hardirq stack, saves previous ESP at the bottom of the IRQ stack, optionally prints overflow diagnostics, switches stacks via inline asm and calls the IRQ descriptor handler. `__handle_irq()` checks low kernel stack, uses IRQ stack for kernel-mode interrupts when possible, otherwise handles directly. Softirq own-stack support similarly switches to per-CPU softirq stack for `__do_softirq()`.

## Dependencies And Integration Points
Depends on 32-bit stack layout, generic IRQ descriptors, `CALL_NOSPEC`, per-CPU stack pointers, softirq core, and debug stack overflow config.

## Risks And Test Signals
Risks include incorrect ESP switching/restoration, nested hardirq stack detection failure, stack overflow false negatives, and allocation failure during CPU bringup. Tests include 32-bit IRQ storms, nested interrupts, softirq-on-own-stack, CPU hotplug stack allocation, debug stack overflow panic mode, and nospec thunk correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irq_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irq_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/irq_64.c

## Purpose
Initializes 64-bit x86 per-CPU hardirq stacks, optionally mapping them with guard pages when VMAP_STACK is enabled.

## Important APIs And State
Defines per-CPU `hardirq_stack_inuse`, visible page-aligned `irq_stack_backing_store`, and `irq_init_percpu_irqstack()`. Internal `map_irq_stack()` either vmap-maps the backing pages or uses direct per-CPU storage.

## Control Flow And Persistence
For VMAP_STACK, `map_irq_stack()` gathers the physical pages backing the per-CPU irq stack, maps them with `vmap()` as kernel pages, and stores the actual top-of-stack in `hardirq_stack_ptr` to avoid hot-path adjustment. Without VMAP_STACK it points directly at the per-CPU backing store top. Initialization is idempotent per CPU.

## Dependencies And Integration Points
Depends on per-CPU allocation, vmalloc/vmap, IRQ stack definitions, KASAN/VMAP_STACK configuration, and common interrupt entry code that consumes `hardirq_stack_ptr`.

## Risks And Test Signals
Risks include vmap allocation failure, missing guard pages when disabled, wrong top-of-stack offset, and reuse during CPU hotplug. Tests include 64-bit boot with VMAP_STACK on/off, KASAN configurations, interrupt stack overflow detection elsewhere, CPU hotplug, and high interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irq_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irq_work.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/irq_work.c

## Purpose
Provides x86 APIC-backed irq_work delivery using a self-IPI and system-vector handler.

## Important APIs And State
Under `CONFIG_X86_LOCAL_APIC`, defines `sysvec_irq_work` and `arch_irq_work_raise()`. It updates `apic_irq_work_irqs` in per-CPU IRQ stats and emits irq vector tracepoints.

## Control Flow
`arch_irq_work_raise()` checks whether the architecture has an interrupt delivery mechanism, sends `IRQ_WORK_VECTOR` to self with `__apic_send_IPI_self()`, and waits for the APIC ICR to become idle. The vector handler EOIs the APIC, traces entry/exit, increments stats, and runs queued irq_work callbacks with `irq_work_run()`.

## Dependencies And Integration Points
Depends on local APIC, IDT system vector setup, irq_work core, tracepoints, and common IRQ stats.

## Risks And Test Signals
Risks include self-IPI unavailable or delayed, missed EOI, and deadlocks if irq_work callbacks assume wrong context. Tests include irq_work queueing from NMI/IRQ/process contexts, APIC disabled cases, tracepoint visibility, and `/proc/interrupts` IWI counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irq_work.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irqflags.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/irqflags.S

## Purpose
Provides the noinstr assembly implementation of `native_save_fl()`, returning current x86 flags.

## Important APIs And State
Exports `native_save_fl`. The function is placed in `.noinstr.text`, begins with ENDBR, executes `pushf`, pops into the return register, and returns. It has no persistent state.

## Control Flow And Dependencies
This is a minimal helper used by low-level interrupt flag APIs. It depends on asm register-width macros and linkage/export annotations so the same source works for 32-bit and 64-bit builds.

## Risks And Test Signals
Risks are limited but important: instrumentation must not be inserted, flags width must match ABI, and ENDBR/IBT annotations must be valid. Test signals include objtool noinstr validation, native irq flag save/restore tests, and successful exports for modules or paravirt users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irqflags.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irqinit.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/irqinit.c

## Purpose
Initializes x86 interrupt vector mappings, ISA IRQ chip setup, per-CPU IRQ stacks, and final architecture IRQ gate/vector setup.

## Important APIs And State
Defines per-CPU `vector_irq` initialized to `VECTOR_UNUSED`; functions `init_ISA_irqs()`, `init_IRQ()`, and `native_init_IRQ()`.

## Control Flow
`init_ISA_irqs()` initializes BSP APIC virtual wire mode, initializes the legacy PIC, and assigns legacy IRQ descriptors to the PIC chip and level handler. `init_IRQ()` seeds CPU0 vector slots for ISA IRQ vectors, initializes this CPU's IRQ stack, and calls `x86_init.irqs.intr_init()`. `native_init_IRQ()` runs pre-vector quirks, completes FRED exception setup when configured, installs IDT APIC/IRQ gates if not using FRED, assigns LAPIC system vectors, and requests cascade IRQ2 when no IO-APIC/OpenFirmware IO-APIC is present.

## Dependencies And Integration Points
Depends on `legacy_pic`, APIC/LAPIC setup, IDT/FRED setup, `x86_init` platform hooks, IRQ stack initialization from arch-specific files, ACPI/OF IO-APIC discovery, generic IRQ descriptors, and vector allocator state consumed by `irq.c`.

## Risks And Test Signals
Risks include wrong legacy vector seeding, missing IRQ stack, FRED/IDT split mistakes, cascade IRQ request failure, and platform quirk ordering. Tests include boot on PIC-only, IO-APIC, OF IO-APIC, FRED and non-FRED systems, CPU0 ISA IRQ delivery, cascade IRQ2 presence, and early interrupt vector handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/irqinit.c -->
