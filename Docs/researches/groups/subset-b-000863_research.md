# subset-b-000863 research

Grouped research for x86 entry, vDSO/vsyscall, and AMD perf-event sources. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_64.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/entry_64.S

Purpose: this is the primary 64-bit x86 low-level entry assembly for native syscall, exception, interrupt, NMI, task-switch, fork-return, Xen PV, and mitigation paths. It constructs `struct pt_regs`, switches GS/CR3 state, applies entry/exit speculation mitigations, and transfers to C handlers such as `do_syscall_64()`, `ret_from_fork()`, `exc_nmi()`, generated `idtentry` handlers, `fixup_bad_iret()`, and `make_task_dead()`.

Important APIs/functions: `entry_SYSCALL_64`, `__switch_to_asm`, `ret_from_fork_asm`, `idtentry`, `idtentry_mce_db`, `idtentry_vc`, `idtentry_df`, `common_interrupt_return`, `swapgs_restore_regs_and_return_to_usermode`, `restore_regs_and_return_to_kernel`, `asm_load_gs_index`, `paranoid_entry`, `paranoid_exit`, `error_entry`, `error_return`, `asm_exc_nmi`, `entry_SYSCALL32_ignore`, `rewind_stack_and_make_dead`, and `clear_bhb_loop`. The file depends heavily on macros from `calling.h`, `asm/idtentry.h`, speculation headers, and per-CPU TSS/current-stack offsets.

Control flow: syscall entry swaps to kernel GS, saves user RSP in `TSS_sp2`, switches to kernel CR3, builds a syscall-style `pt_regs`, clears caller-saved registers, runs IBRS/untrain/BHB mitigations, calls `do_syscall_64()`, then chooses fast `SYSRETQ` only if the C layer returns true; otherwise it uses the shared IRET exit path. Exception stubs enter through `error_entry()` or `paranoid_entry()` depending on stack/IST sensitivity, then return through `error_return()` or `paranoid_exit()`. NMI handling has a special nested-NMI protocol with an "NMI executing" stack word and repeat frame.

State/persistence: persistent architectural state touched includes per-CPU TSS stack slots, CR3/PCID, GSBASE, SPEC_CTRL/IBRS shadow state, RSB/BHB predictor state, ESPFIX stacks, and pt_regs stack images. It exports `asm_load_gs_index` and KVM-facing `clear_bhb_loop`.

Integration points: scheduler context switch, syscall dispatch, generated IDT vectors, Xen PV callbacks, SEV/VC exception support, FRED alternative fork exit, KVM mitigations, objtool ORC unwind annotations, stackleak, page-table isolation, and x86 speculation mitigations.

Risks: register layout must match `struct pt_regs`, `inactive_task_frame`, and unwinder expectations; any swapgs/CR3 ordering bug can expose user memory or corrupt per-CPU state. Fast SYSRET is security-sensitive for noncanonical RIP/RFLAGS. NMI nesting, ESPFIX, Xen PV, and bad-IRET fixup are fragile corner cases. Test signals include syscall ABI tests, x86 selftests for entry/ptrace/signals, KVM boot tests, objtool validation, lockdep/DEBUG_ENTRY, NMI watchdog/perf stress, Xen PV boot, and PTI/IBRS/BHB mitigation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_64_compat.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/entry_64_compat.S

Purpose: provides 32-bit compatibility syscall assembly entry on a 64-bit kernel for `SYSENTER`, compat `SYSCALL`, and legacy `int $0x80` dispatch. It converts the quirky hardware entry conventions into kernel `pt_regs` and routes to C helpers in `syscall_32.c`.

Important APIs/functions: `entry_SYSENTER_compat`, `entry_SYSCALL_compat`, `sysret32_from_system_call`, `entry_SYSRETL_compat_unsafe_stack`, `int80_emulation`, and labels consumed by unwind/entry validation. Dependencies include `calling.h`, `asm-offsets`, segment constants, `nospec-branch`, CR3 switching macros, and the C functions `do_SYSENTER_32()`, `do_fast_syscall_32()`, and `do_int80_emulation()`.

Control flow: `SYSENTER` swaps GS, switches CR3, creates a partially synthetic frame because hardware did not save RIP/RSP/RFLAGS, clears/fixes flags such as NT/AC/TF, applies branch mitigations, and calls `do_SYSENTER_32()`. Compat `SYSCALL` stashes user ESP, builds a frame with user CS/SS and saved RCX/R11, calls `do_fast_syscall_32()`, then attempts the `SYSRETL` path if C validation succeeds. The `int80_emulation` stub performs BHB clearing before entering C.

State/persistence: it mutates user-visible return register state, saved frame fields, GS, CR3, and trampoline-stack exit state. It intentionally zeroes `r8-r10` before `sysretl` to avoid leaking kernel state.

Integration points: the 32-bit vDSO `__kernel_vsyscall`, IA32 emulation, `syscall_32.c`, PTI, Xen PV, BHI/IBRS mitigations, and the shared 64-bit user-return path in `entry_64.S`.

Risks: compat syscall ABI depends on exact register preservation, especially EBP/ESP for the vDSO path. Returning via `SYSRETL/SYSEXIT` requires strict CS/SS/IP/flag checks; otherwise IRET must be used. Test signals include 32-bit userspace syscall tests on Intel and AMD, ptrace signal restart tests, Android/Bionic compatibility cases, `ia32_emulation` toggles, objtool checks, and Xen PV/compat boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_64_compat.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_64_fred.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/entry_64_fred.S

Purpose: implements the assembly landing points for Flexible Return and Event Delivery (FRED). It builds a register frame for FRED user and kernel event delivery and provides a KVM helper that fabricates a FRED-style frame for VMX-origin IRQ/NMI handling.

Important APIs/functions: `asm_fred_entrypoint_user`, `asm_fred_exit_user`, `asm_fred_entrypoint_kernel`, `asm_fred_entry_from_kvm`, plus `FRED_ENTER`/`FRED_EXIT` macros. It calls `fred_entry_from_user()`, `fred_entry_from_kernel()`, and `__fred_entry_from_kvm()`. It uses `ERETU`, `ERETS`, FRED stack-frame constants, extable recovery for `ERETU`, and exports the KVM helper.

Control flow: the ring-3 entry is 4 KiB aligned because FRED hardware derives the entry RIP from `IA32_FRED_CONFIG`. It pushes/clears GPRs, passes `pt_regs` in `%rdi`, calls the C dispatcher, restores registers, and returns with `ERETU`. Kernel entry is fixed at user entry plus 256 bytes and returns with `ERETS`. The KVM helper emulates FRED redzone/alignment, manually pushes a 64-byte FRED frame, calls the C dispatcher, and either restores the old stack or executes `ERETS` when FRED is active.

State/persistence: no durable kernel data is owned here; it manages transient stack frames, return-state bits, callee-saved registers, and extable metadata.

Integration points: FRED CPU feature enablement, KVM Intel VMX interrupt/NMI exits, C FRED dispatch in `entry_fred.c`, objtool unwind hints, and the generic `pt_regs` layout.

Risks: hardware-mandated alignment and frame layout are exact. A wrong offset in the KVM synthetic frame would confuse C dispatch or return through the wrong FRED instruction. Test signals include FRED boot tests, KVM VMX IRQ/NMI injection tests, objtool validation, nested event tests, and exception-return fault injection around `ERETU`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_64_fred.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_fred.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/entry_fred.c

Purpose: C-side FRED event dispatcher. It decodes FRED event type/vector fields in `pt_regs`, calls the appropriate trap, interrupt, NMI, or syscall handler, and maintains the FRED system-vector table.

Important APIs/functions: `fred_entry_from_user()`, `fred_entry_from_kernel()`, `__fred_entry_from_kvm()`, `fred_install_sysvec()`, `fred_complete_exception_setup()`, `fred_bad_type()`, `fred_intx()`, `fred_other()`, `fred_extint()`, `fred_hwexc()`, `fred_swexc()`, and `exc_vmm_communication()` under AMD memory encryption. Key state includes `sysvec_table[]` and `fred_setup_done`.

Control flow: user and kernel entries invalidate `orig_ax`, derive `error_code` from the saved value, then switch on `regs->fred_ss.type`. External interrupts either call a system-vector handler under `irqentry_enter/exit` or `common_interrupt()`. Hardware exceptions prefer the page-fault fast path and otherwise dispatch vector-by-vector. Software INT handles `int3`, overflow, and IA32 `int80` if enabled. FRED `EVENT_TYPE_OTHER` maps long-mode syscall and 32-bit SYSENTER events to `do_syscall_64()` and `do_fast_syscall_32()`.

State/persistence: `sysvec_table` becomes read-only after init and is completed with spurious handlers. `fred_setup_done` blocks late vector installation. Runtime state lives in `pt_regs` and irqentry accounting.

Integration points: IDT/sysvec declarations, APIC vectors, IA32 emulation, syscall dispatch, NMI/debug/machine-check handlers, TDX/SEV/CET trap handlers, and KVM FRED delivery.

Risks: invalid event types on high stack levels can panic; vector/type distinctions replace legacy IDT assumptions, so misrouting SWINT versus EXTINT would be severe. Test signals include FRED-enabled boot, syscall and compat syscall tests under FRED, APIC vector delivery, KVM injection, spurious vector tests, and trap coverage for page fault, debug, machine check, and control protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_fred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/syscall_32.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/syscall_32.c

Purpose: 32-bit syscall dispatch and entry-state management for native i386 and IA32 emulation. It maps syscall numbers to generated `__ia32_*` handlers and implements C-side INT80, SYSENTER, and compat SYSCALL behavior.

Important APIs/functions: `ia32_sys_call()`, `syscall_32_enter()`, `do_syscall_32_irqs_on()`, `do_int80_emulation()`, FRED `int80_emulation`, `do_int80_syscall_32()`, `__do_fast_syscall_32()`, `do_fast_syscall_32()`, and `do_SYSENTER_32()`. State includes optional `sys_call_table[]` for tracing and `__ia32_enabled` controlled by `ia32_emulation=`.

Control flow: syscall numbers are converted to unsigned and guarded with `array_index_nospec()` before dispatch through generated `syscalls_32.h`. INT80 validates user origin, enters kernel context, optionally rejects external vector-0x80 injections, normalizes `orig_ax`, enables IRQs for syscall work, dispatches, and exits to user mode. Fast SYSENTER/SYSCALL fetches the sixth argument from the user stack/vDSO-stashed EBP, then validates whether a fast return is legal.

State/persistence: sets `TS_COMPAT`, updates `regs->orig_ax/ax/ip/sp/bp/flags`, uses `current->mm->context.vdso` and `vdso32_image.sym_int80_landing_pad`, and honors the boot-time IA32 enable flag.

Integration points: assembly stubs in `entry_64_compat.S`, FRED dispatch, generated syscall tables, seccomp/ptrace/syscall entry common code, APIC ISR checks, vDSO32, and KASLR stack offset randomization.

Risks: user-controlled stack reads for EBP can fault and must force IRET. External INT80 injection handling differs under FRED. Fast returns require exact landing-pad, CS/SS, and flag validation. Test signals include 32-bit glibc/vDSO syscall tests, ptrace syscall rewriting, seccomp, `ia32_emulation=false`, FRED INT80, APIC injection hardening, and signal restart through INT80.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/syscall_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/syscall_64.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/syscall_64.c

Purpose: 64-bit and x32 syscall dispatch for x86-64. It maps generated syscall tables to callable functions, runs common syscall-entry/exit work, and decides whether assembly may return with `SYSRET`.

Important APIs/functions: `x64_sys_call()`, `x32_sys_call()`, `do_syscall_x64()`, `do_syscall_x32()`, and `do_syscall_64()`. It exposes `sys_call_table[]` for tracing metadata even though direct syscall dispatch uses switch-generated calls.

Control flow: `do_syscall_64()` receives `pt_regs` and a signed syscall number from assembly, runs `syscall_enter_from_user_mode()`, adds a random kernel-stack offset, attempts native x64 dispatch, then x32 dispatch when `__X32_SYSCALL_BIT` is present, and otherwise returns `ni_syscall` for invalid syscall numbers except `-1`. After `syscall_exit_to_user_mode()`, it validates the saved user frame for `SYSRET`.

State/persistence: updates `regs->ax` with return values and depends on `regs->cx`, `regs->r11`, `regs->ip`, `regs->flags`, `regs->cs`, and `regs->ss` remaining compatible with the architectural `SYSCALL/SYSRET` ABI.

Integration points: `entry_SYSCALL_64`, generated `syscalls_64.h` and `syscalls_x32.h`, tracing, seccomp, ptrace, x32 ABI, Xen PV, and `TASK_SIZE_MAX` user-address validation.

Risks: `SYSRET` is unsafe for noncanonical or kernel-range RIP and cannot restore RF correctly. Any missing `array_index_nospec()` would expose table speculation. Test signals include syscall ABI suites, x32 tests, ptrace/seccomp mutation tests, bad-RIP SYSRET tests, Xen PV boot, and trace_syscalls symbol validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/syscall_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/syscalls/Makefile -->
## sources/distributed-fs/ceph-client/arch/x86/entry/syscalls/Makefile

Purpose: build rules for generated x86 syscall headers and syscall dispatch tables from `syscall_32.tbl`, `syscall_64.tbl`, and Xen hypercall definitions.

Important targets/APIs: `$(uapi)/unistd_32.h`, `$(uapi)/unistd_x32.h`, `$(uapi)/unistd_64.h`, `$(out)/unistd_32_ia32.h`, `$(out)/unistd_64_x32.h`, `$(out)/syscalls_32.h`, `$(out)/syscalls_64.h`, `$(out)/syscalls_x32.h`, and `$(out)/xen-hypercalls.h`. It wraps `scripts/syscallhdr.sh`, `scripts/syscalltbl.sh`, and `scripts/xen-hypercalls.sh`.

Control flow: variables such as `abis`, `offset`, and `prefix` are target-specific, so the same scripts emit ABI-specific UAPI numbers, prefixed internal declarations, and switch-table include files. `all` builds UAPI and internal headers according to `CONFIG_X86_64`, `CONFIG_X86_X32_ABI`, and `CONFIG_XEN`.

State/persistence: generated files land under `arch/$(SRCARCH)/include/generated/...` and are tracked by Kbuild `targets` for rebuild decisions. The Makefile creates generated include directories with `mkdir -p`.

Integration points: syscall dispatch C files, userspace UAPI, Xen code, Kbuild `if_changed`, and ABI table files.

Risks: wrong ABI filters or offsets can corrupt syscall numbers across native, IA32, and x32 ABIs. Test signals include clean incremental builds, `make headers_install`, syscall table diff checks, x32/IA32 builds, and build reproducibility after `.tbl` edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/thunk.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/thunk.S

Purpose: defines exported assembly thunks that save/prepare registers before entering scheduler functions from sensitive assembly contexts.

Important APIs/functions: `THUNK preempt_schedule_thunk, preempt_schedule` and `THUNK preempt_schedule_notrace_thunk, preempt_schedule_notrace`, both exported. The actual thunk body comes from `calling.h`.

Control flow: callers branch/call into the thunk symbol, which follows the shared x86 thunk convention to protect register allocation assumptions around inline assembly and then calls the target C scheduler routine.

State/persistence: no file-owned persistent state; it preserves transient register state according to the thunk macro and exports symbols for other kernel code.

Integration points: preemption, scheduler, low-level entry/exit assembly, module symbol resolution, and `calling.h`.

Risks: macro semantics must remain compatible with callers that rely on register preservation in nonstandard contexts. Test signals include preemption stress, objtool validation, module symbol checks, and scheduler tracing around `preempt_schedule_notrace`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/thunk.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/Makefile -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/Makefile

Purpose: top-level Kbuild file for x86 vDSO support. It builds kernel-side vDSO mapping/fixup objects and descends into architecture-width-specific vDSO image directories.

Important build objects: always builds `vma.o` and `extable.o`; conditionally builds `vdso32-setup.o` for `CONFIG_COMPAT_32`, `vdso64/` for `CONFIG_X86_64`, and `vdso32/` for `CONFIG_COMPAT_32`.

Control flow: Kbuild aggregates regular kernel objects separately from the image-producing subdirectories. The per-ABI Makefiles handle actual vDSO shared-object linkage.

State/persistence: produces kernel objects and vDSO image artifacts consumed by `vma.c` and process exec setup. No runtime state is defined in the Makefile.

Integration points: Kbuild, compat settings, vDSO image linker scripts, vDSO exception handling, and process additional-page setup.

Risks: missing subdirectory inclusion removes user-visible ABI symbols or mapping support. Test signals include x86_64, x32, and IA32 compat builds, boot with vDSO enabled/disabled, and ABI symbol checks with readelf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/note.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/note.S

Purpose: common assembly included into vDSO images to emit ELF note metadata and build salt.

Important APIs/macros: `ELFNOTE_START(Linux, 0, "a")`, `LINUX_VERSION_CODE`, `ELFNOTE_END`, and `BUILD_SALT`. It includes `linux/build-salt.h`, `linux/version.h`, and `linux/elfnote.h`.

Control flow: at assembly time it emits a Linux note containing the kernel version code and a build salt note. There is no runtime control flow.

State/persistence: metadata is embedded in the vDSO ELF PT_NOTE segment. It persists in mapped vDSO images visible to userspace tooling.

Integration points: both `vdso32/note.S` and `vdso64/note.S`, the common linker script note sections, ELF loaders, debuggers, and reproducible-build infrastructure.

Risks: note-format breakage can affect tooling that inspects vDSO metadata. Test signals include readelf note inspection on built vDSOs and reproducible-build salt checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vclock_gettime.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vclock_gettime.c

Purpose: common vDSO wrappers for fast user-mode `gettimeofday`, `time`, `clock_gettime`, and `clock_getres` implementations.

Important APIs/functions: `__vdso_gettimeofday`, weak `gettimeofday`, `__vdso_time`, weak `time`, `__vdso_clock_gettime`, weak `clock_gettime`, `__vdso_clock_getres`, weak `clock_getres`, and for i386 `__vdso_clock_gettime64`/`__vdso_clock_getres_time64`. It includes `lib/vdso/gettimeofday.c` to reuse generic vDSO time logic.

Control flow: exported wrappers immediately delegate to `__cvdso_*` helpers. Compile-time conditions select 64-bit/x32 `__kernel_timespec` APIs or i386 `old_timespec32` plus time64 variants.

State/persistence: no writable state here; it reads shared vDSO/VVAR data through the generic vDSO implementation.

Integration points: vDSO linker version scripts, VVAR data pages, timekeeping core, compat 32-bit ABI, libc symbol lookup through weak aliases, and build flags from vDSO Makefiles.

Risks: ABI signatures and symbol names are user-visible and must match version scripts. Time32/time64 selection is sensitive to build defines such as `BUILD_VDSO32_64`. Test signals include vDSO time selftests, libc fallback tests, 32-bit and x32 execution, symbol-version inspection, and time namespace/timekeeping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vclock_gettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vdso-layout.lds.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vdso-layout.lds.S

Purpose: common linker script that defines the ELF layout for x86 vDSO shared objects.

Important symbols/sections: `VDSO_VVAR_SYMS`, `vclock_pages`, `pvclock_page`, `hvclock_page`, dynamic/rodata/note/eh_frame/text sections, `.altinstructions`, `.altinstr_replacement`, `__ex_table`, discard rules, and PHDRs for `PT_LOAD`, `PT_DYNAMIC`, `PT_NOTE`, `PT_GNU_EH_FRAME`, `PT_GNU_STACK`, and `PT_GNU_PROPERTY`.

Control flow: at link time it places shared kernel/user data before vDSO text, emits one RX load segment plus read-only metadata program headers, keeps exception-table entries, and discards kernel-only sections that should not appear in the user mapping.

State/persistence: the resulting ELF layout is persisted in `vdso*.so.dbg` images and later mapped into processes by `vma.c`.

Integration points: `vdso32.lds.S`, `vdso64.lds.S`, `vdsox32.lds.S`, vDSO VVAR definitions, alternative instruction patching, exception fixups for SGX, and userspace ELF loaders/debuggers.

Risks: section ordering affects load permissions, VVAR offsets, and symbol addresses used by kernel mapping code. Test signals include vDSO link success with GNU ld/LLD, readelf segment checks, vvar fault tests, SGX extable fixup tests, and ABI symbol/version validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vdso-layout.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vgetcpu.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vgetcpu.c

Purpose: common vDSO implementation of `getcpu()` for fast userspace CPU/node lookup.

Important APIs/functions: `__vdso_getcpu(unsigned *cpu, unsigned *node, void *unused)` and weak alias `getcpu`. It calls `vdso_read_cpunode()`.

Control flow: the function reads CPU/node values from the vDSO processor data mechanism and returns zero. It ignores the legacy cache argument.

State/persistence: no local persistent state; it consumes kernel-maintained per-task/per-CPU data exposed through vDSO mechanisms.

Integration points: vDSO linker scripts, libc `getcpu`, scheduler CPU/node metadata, and `vdso/processor.h`.

Risks: stale or incorrectly mapped CPU/node data leads to wrong userspace locality decisions. ABI signature must remain stable. Test signals include vDSO getcpu selftests, CPU hotplug/migration stress, NUMA node validation, and symbol-version checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vgetcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/extable.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/extable.c

Purpose: kernel-side fixup logic for exceptions raised inside vDSO code, currently important for SGX vDSO enclave entry.

Important APIs/types: `struct vdso_exception_table_entry` with relative `insn` and `fixup` offsets, and `fixup_vdso_exception(struct pt_regs *regs, int trapnr, unsigned long error_code, unsigned long fault_addr)`.

Control flow: rejects debug and breakpoint traps, verifies the current mm has a vDSO mapping, computes the runtime base from `current->mm->context.vdso + image->extable_base`, scans `image->extable`, and when `regs->ip` matches a protected instruction rewrites RIP to the fixup and passes trap metadata in DI/SI/DX.

State/persistence: reads `mm->context.vdso`, `vdso_image`, and image exception-table metadata; mutates only the faulting task's `pt_regs`.

Integration points: vDSO image metadata, `_ASM_VDSO_EXTABLE_HANDLE` from `extable.h`, SGX vDSO assembly, x86 trap handling, and process mm context.

Risks: wrong relative offsets would send user execution to invalid vDSO code. Suppressing DB/BP fixup is intentional because enclave origin cannot be identified. Test signals include SGX enclave exception tests, vDSO extable readelf checks, trap fault injection, and mm/vDSO remap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/extable.h -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/extable.h

Purpose: defines macros to emit vDSO exception-table entries from assembly or inline assembly.

Important APIs/macros: `_ASM_VDSO_EXTABLE_HANDLE(from, to)` for assembler and C-string contexts, and `ASM_VDSO_EXTABLE_HANDLE` assembler macro. Entries are two `.long` relative offsets to `__ex_table`.

Control flow: no runtime execution. At build time, protected instruction/fixup pairs are placed in the `__ex_table` section for later scanning by `extable.c`.

State/persistence: persists relative exception-table metadata inside vDSO images.

Integration points: `vdso64/vsgx.S`, common vDSO linker script retaining `__ex_table`, and kernel fixup handler `fixup_vdso_exception()`.

Risks: relative-offset encoding differs from normal kernel extables; using the wrong macro or section would make vDSO fixups invisible. Test signals include vDSO image section inspection, SGX exception tests, and assembly build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32-setup.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32-setup.c

Purpose: initializes and exposes runtime controls for mapping the 32-bit vDSO.

Important APIs/state: global `vdso32_enabled`, boot parser `vdso32_setup()`, `__setup("vdso32=", ...)`, 32-bit `vdso=` alias, sysctl table for `abi/vsyscall32` on x86_64 or `vm/vdso_enabled` on x86_32, and `ia32_binfmt_init()`.

Control flow: boot parameters parse numeric enablement and clamp unsupported values to disabled. Sysctl registration happens at init when `CONFIG_SYSCTL` is enabled.

State/persistence: `vdso32_enabled` is `__read_mostly` runtime configuration read by `vma.c` during `load_vdso32()`. Sysctl changes persist until reboot and affect subsequent exec mappings.

Integration points: compat vDSO mapping, IA32 binfmt, kernel boot parameters, sysctl, `CONFIG_COMPAT_VDSO`, and `arch_setup_additional_pages()`.

Risks: enabling/disabling changes user ABI availability and libc syscall path behavior. Invalid historical values are intentionally rejected. Test signals include booting with `vdso32=0/1`, sysctl writes, 32-bit exec tests, and compat syscall/vDSO fallback checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/Makefile -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/Makefile

Purpose: builds the 32-bit x86 vDSO image `linux-gate.so.1`.

Important build variables: `vdsos-y := 32`, `vobjs-y := note.o vclock_gettime.o vgetcpu.o system_call.o sigreturn.o`, `flags-y := -DBUILD_VDSO32 -m32 -mregparm=0`, optional include of `fake_32bit_build.h` on x86_64, `flags-remove-y := -m64`, adjusted `CHECKFLAGS`, included `../common/Makefile.include`, and `VDSO_LDFLAGS_32`.

Control flow: Kbuild compiles 32-bit objects, applies fake 32-bit config when cross-building from x86_64, and links `vdso32.so.dbg` from the vDSO objects.

State/persistence: produces the 32-bit vDSO binary consumed by kernel mapping code and exported to 32-bit tasks.

Integration points: common vDSO source files, 32-bit signal/syscall assembly, linker script, sparse checking, and compat execution.

Risks: wrong flags can build ABI-incompatible code or leak x86_64 config into a 32-bit image. Test signals include 32-bit vDSO build under x86_64, sparse checks, readelf class/soname validation, and 32-bit userspace smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/fake_32bit_build.h -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/fake_32bit_build.h

Purpose: adjusts preprocessor configuration so a 32-bit vDSO can be built inside a 64-bit kernel build.

Important definitions: undefines `CONFIG_64BIT`, `CONFIG_X86_64`, `CONFIG_COMPAT`, page-table and memory options, `CONFIG_NR_CPUS`, and `CONFIG_PARAVIRT_XXL`; defines `CONFIG_X86_32`, `CONFIG_PGTABLE_LEVELS 2`, `CONFIG_PAGE_OFFSET 0`, `CONFIG_ILLEGAL_POINTER_VALUE 0`, `CONFIG_NR_CPUS 1`, and `BUILD_VDSO32_64`.

Control flow: header is force-included by the vdso32 Makefile only under `CONFIG_X86_64`. It has no runtime behavior.

State/persistence: affects preprocessor-visible configuration for generated vDSO object files.

Integration points: common vDSO time/getcpu code, asm headers that branch on 32-bit versus 64-bit config, and Kbuild flags.

Risks: stale config overrides can silently change ABI layout or type selection. Test signals include preprocessor/build checks for vdso32 on x86_64, symbol ABI inspection, and comparing native i386 versus compat vDSO behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/fake_32bit_build.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/note.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/note.S

Purpose: includes the common vDSO note metadata source for the 32-bit image.

Important dependency: `#include "common/note.S"` emits Linux version and build-salt notes.

Control flow: no runtime behavior; assembly inclusion only.

State/persistence: embeds PT_NOTE metadata in the 32-bit vDSO.

Integration points: vdso32 build, common note source, and vDSO linker layout.

Risks: include path must resolve through vDSO build rules. Test signals include vdso32 build and readelf note inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/sigreturn.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/sigreturn.S

Purpose: provides 32-bit vDSO signal-return trampolines and unwind CFI for normal and realtime signal frames.

Important APIs/symbols: `__kernel_sigreturn`, `__kernel_rt_sigreturn`, `vdso32_sigreturn_landing_pad`, `vdso32_rt_sigreturn_landing_pad`, and `STARTPROC_SIGNAL_FRAME`. It uses `__NR_sigreturn`, `__NR_rt_sigreturn`, IA32 sigcontext offsets, and DWARF CFI macros.

Control flow: `__kernel_sigreturn` pops the signal frame return code into EAX, loads `sigreturn`, and executes `int $0x80`; `__kernel_rt_sigreturn` loads `rt_sigreturn` and executes `int $0x80`. Both land on `ud2a` pads after the syscall instruction for kernel recognition and unwind/debug behavior.

State/persistence: no owned data; it encodes CFI and fixed instruction bytes in the vDSO ABI. The comments document a libgcc unwinder workaround that requires byte-exact sequences.

Integration points: signal delivery, unwinding libraries, `arch_syscall_is_vdso_sigreturn()`, 32-bit syscall entry, and the vdso32 linker version script.

Risks: instruction sequence changes can break legacy libgcc unwinding and signal return recognition. Test signals include 32-bit signal/unwind tests, gdb backtraces through signal frames, byte-sequence inspection, and syscall restart tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/sigreturn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/system_call.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/system_call.S

Purpose: implements the 32-bit vDSO `__kernel_vsyscall` AT_SYSINFO entry for fast 32-bit syscalls.

Important symbols: `__kernel_vsyscall`, `int80_landing_pad`, `SYSENTER_SEQUENCE`, `SYSCALL_SEQUENCE`, and alternatives controlled by `X86_FEATURE_SYSFAST32` and `X86_FEATURE_SYSCALL32`.

Control flow: if fast 32-bit syscall support is absent, the patched path uses `int $0x80; ret`. Otherwise it saves ECX/EDX/EBP with CFI, reshuffles stack/register state so SYSENTER/SYSCALL can preserve enough information, executes the selected fast instruction, falls back through `int $0x80` at `int80_landing_pad`, then restores registers and returns.

State/persistence: no writable state; the text is patched by alternatives and its landing-pad offset is used by kernel validation.

Integration points: `entry_64_compat.S`, `syscall_32.c` fast return validation, AT_SYSINFO auxv, Android legacy compatibility, and vdso32 symbol versioning.

Risks: user code historically hardcoded this sequence, so instruction layout is ABI-sensitive. Kernel fast-return validation assumes the landing pad symbol. Test signals include 32-bit syscall benchmarks, old Android/Bionic compatibility, CPU feature alternative patch checks, and ptrace/signal restart through the landing pad.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/system_call.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vclock_gettime.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vclock_gettime.c

Purpose: includes the common vDSO time implementation for the 32-bit image.

Important dependency: `#include "common/vclock_gettime.c"`. Under vdso32 build flags this selects i386 time32 plus time64 wrapper variants.

Control flow: all exported behavior comes from the included common source and delegates to generic `__cvdso_*` helpers.

State/persistence: reads VVAR time data through the common implementation; no local state.

Integration points: vdso32 Makefile fake 32-bit config, vDSO version script, libc time calls, and kernel VVAR mappings.

Risks: inclusion relies on build defines to select correct ABI types. Test signals include 32-bit `clock_gettime`, `clock_gettime64`, `gettimeofday`, and symbol-version checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vclock_gettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vdso32.lds.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vdso32.lds.S

Purpose: 32-bit vDSO linker/version script.

Important declarations: defines `BUILD_VDSO32`, includes `common/vdso-layout.lds.S`, sets `ENTRY(__kernel_vsyscall)`, and exports symbols under `LINUX_2.6` and legacy `LINUX_2.5`.

Control flow: link-time only. It combines common layout with 32-bit ABI symbol visibility, including time/getcpu symbols plus syscall and sigreturn trampolines.

State/persistence: produces a 32-bit ELF shared object whose entry point is used for AT_SYSINFO and whose symbols are user ABI.

Integration points: vdso32 objects, libc symbol lookup, process auxv setup, and kernel signal/syscall recognition.

Risks: removing or renaming versioned symbols breaks old 32-bit userspace. Test signals include readelf symbol/version checks, AT_SYSINFO validation, and 32-bit process startup/signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vdso32.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vgetcpu.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vgetcpu.c

Purpose: includes the common vDSO `getcpu()` implementation for the 32-bit image.

Important dependency: `#include "common/vgetcpu.c"` provides `__vdso_getcpu` and weak `getcpu`.

Control flow: runtime behavior is the common implementation: read CPU/node and return zero.

State/persistence: no local state; uses shared vDSO CPU/node data.

Integration points: vdso32 linker script, libc `getcpu`, scheduler/NUMA data, and fake 32-bit build configuration.

Risks: ABI signature must match 32-bit callers. Test signals include 32-bit getcpu selftests and CPU migration/NUMA checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vgetcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/Makefile -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/Makefile

Purpose: builds 64-bit and optional x32 vDSO images.

Important build variables: `vdsos-y := 64`, optional `x32`, `vobjs-y := note.o vclock_gettime.o vgetcpu.o vgetrandom.o vgetrandom-chacha.o`, optional `vsgx.o`, `flags-y := -DBUILD_VDSO64 -m64 -mcmodel=small`, common Makefile include, x32 objcopy rule, `VDSO_LDFLAGS_64`, and `VDSO_LDFLAGS_x32`.

Control flow: 64-bit objects are linked directly into `vdso64.so.dbg`; x32 builds reuse 64-bit code objects converted to `elf32-x86-64` before linking `vdsox32.so.dbg`.

State/persistence: creates vDSO image blobs referenced by `vdso64_image` and `vdsox32_image`.

Integration points: vDSO random, SGX, time/getcpu wrappers, linker scripts, Kbuild objcopy, and process exec mapping.

Risks: x32 conversion and symbol selection are ABI-sensitive. Test signals include x86_64 and x32 vDSO builds, readelf class/soname checks, getrandom/time/getcpu selftests, and SGX-enabled build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/note.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/note.S

Purpose: includes common vDSO note metadata for the 64-bit image.

Important dependency: `#include "common/note.S"`.

Control flow: assembly inclusion emits version and build-salt notes.

State/persistence: embeds PT_NOTE metadata into 64-bit and x32-derived vDSO artifacts.

Integration points: vdso64 Makefile, common layout script, and ELF tooling.

Risks: include/layout errors affect vDSO metadata visibility. Test signals include readelf notes on `vdso64.so.dbg` and `vdsox32.so.dbg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vclock_gettime.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vclock_gettime.c

Purpose: includes common vDSO time wrappers for 64-bit and x32 images.

Important dependency: `#include "common/vclock_gettime.c"`, with `BUILD_VDSO64` selecting 64-bit/x32 signatures.

Control flow: exported functions call generic `__cvdso_*` helpers through the common source.

State/persistence: no local state; reads VVAR timekeeping data.

Integration points: 64-bit version script, libc time APIs, vDSO VVAR mapping, timekeeping core, and x32 conversion.

Risks: type/signature mismatches are ABI regressions. Test signals include `clock_gettime`, `gettimeofday`, `time`, `clock_getres` vDSO selftests on x86_64 and x32, plus symbol-version checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vclock_gettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vdso64.lds.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vdso64.lds.S

Purpose: 64-bit vDSO linker/version script.

Important declarations: defines `BUILD_VDSO64`, includes the common layout, and exports `clock_gettime`, `__vdso_clock_gettime`, `gettimeofday`, `__vdso_gettimeofday`, `getcpu`, `__vdso_getcpu`, `time`, `__vdso_time`, `clock_getres`, `__vdso_clock_getres`, optional `__vdso_sgx_enter_enclave`, `getrandom`, and `__vdso_getrandom` under `LINUX_2.6`.

Control flow: link-time symbol versioning only.

State/persistence: defines the user-visible dynamic symbol surface for the 64-bit vDSO image.

Integration points: vDSO objects, libc symbol resolution, SGX and getrandom vDSO implementations, and process mapping.

Risks: symbol-version changes break userspace ABI. Test signals include readelf version checks, vDSO selftests, SGX and getrandom availability checks under relevant configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vdso64.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vdsox32.lds.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vdsox32.lds.S

Purpose: x32 vDSO linker/version script.

Important declarations: defines `BUILD_VDSOX32`, includes common layout, and exports the x32 vDSO set: `__vdso_clock_gettime`, `__vdso_gettimeofday`, `__vdso_getcpu`, `__vdso_time`, and `__vdso_clock_getres`.

Control flow: link-time only; visibility is narrower than the native 64-bit script.

State/persistence: defines the x32 ABI vDSO symbol table in an ELF32-x86-64 image containing 64-bit code.

Integration points: vdso64 Makefile x32 objcopy/link path, x32 process setup, and common vDSO layout.

Risks: x32 symbol ABI is distinct from both i386 and x86_64; exporting the wrong surface can confuse libc. Test signals include x32 build/readelf checks and x32 userspace time/getcpu tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vdsox32.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetcpu.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetcpu.c

Purpose: includes common vDSO `getcpu()` for 64-bit and x32 images.

Important dependency: `#include "common/vgetcpu.c"`.

Control flow: runtime behavior reads CPU/node via `vdso_read_cpunode()` and returns zero.

State/persistence: no local state; consumes vDSO CPU/node data.

Integration points: 64-bit/x32 linker scripts, libc `getcpu`, scheduler/NUMA metadata, and vDSO mapping.

Risks: wrong symbol export or data mapping causes userspace locality errors. Test signals include x86_64/x32 getcpu tests and CPU hotplug/migration stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetrandom-chacha.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetrandom-chacha.S

Purpose: stackless SSE2 ChaCha20 block generator used by the 64-bit vDSO getrandom implementation.

Important API/function: `__arch_chacha20_blocks_nostack(output, key, counter, nblocks)`. Inputs are output buffer in RDI, 32-byte key in RSI, 8-byte counter in RDX, and number of 64-byte blocks in RCX.

Control flow: loads the ChaCha constant, key, and counter into XMM registers, runs 10 double-round iterations per block using SSE2 vector arithmetic/rotates, writes 64 bytes, increments the counter, loops for `nblocks`, stores the final counter, clears sensitive vector registers, and returns without stack spills.

State/persistence: updates the caller-provided counter in memory and output buffer. It intentionally avoids stack state and clears key/state-bearing XMM registers at exit.

Integration points: generic `lib/vdso/getrandom.c`, vdso64 Makefile, SSE2 baseline x86-64 ABI, and user-facing `__vdso_getrandom`.

Risks: cryptographic correctness, counter handling, and register clearing are security-sensitive. The routine assumes positive block count and caller-managed buffer sizes. Test signals include vDSO getrandom selftests, ChaCha20 known-answer tests, register/stack audit, objtool/unwind sanity, and sanitizer-style memory bounds tests outside vDSO where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetrandom-chacha.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetrandom.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetrandom.c

Purpose: 64-bit vDSO wrapper for `getrandom`.

Important APIs/functions: `__vdso_getrandom(void *buffer, size_t len, unsigned int flags, void *opaque_state, size_t opaque_len)` and weak alias `getrandom`. It includes `lib/vdso/getrandom.c`.

Control flow: wrapper delegates to `__cvdso_getrandom()`, passing caller buffer, length, flags, and opaque userspace state used by the generic vDSO random implementation.

State/persistence: no local state; state is managed by generic vDSO getrandom code and caller-provided opaque state.

Integration points: ChaCha block assembly, random subsystem vDSO data contract, 64-bit linker script, libc getrandom lookup, and fallback syscall behavior.

Risks: ABI signature and opaque-state size handling are security-sensitive. Test signals include getrandom vDSO selftests, fallback behavior for unsupported flags/state, entropy reseed tests, and symbol version checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vsgx.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vsgx.S

Purpose: vDSO helper for entering or resuming Intel SGX enclaves from userspace.

Important API/function: `__vdso_sgx_enter_enclave`. It interprets `struct sgx_enclave_run` fields by fixed offsets, validates `EENTER..ERESUME`, uses `ENCLU`, records exit/exception information, optionally calls a userspace handler, and emits a vDSO exception-table entry around ENCLU.

Control flow: prologue saves RBP/RBX, validates input leaf and reserved fields, loads TCS and asynchronous-exit pointer, executes ENCLU, records normal EEXIT, and either returns zero or invokes the userspace callback. Exception fixup lands at `.Lhandle_exception`, stores vector/error/address fields passed by `extable.c`, and follows the same exit-handler path. Positive callback return values request another ENCLU attempt.

State/persistence: writes into caller-provided `sgx_enclave_run`, including leaf/exit reason, exception vector, error code, and address. It preserves ABI stack alignment and clears DF before callback.

Integration points: SGX UAPI, vDSO extable, x86 trap fixup, linker symbol export under `CONFIG_X86_SGX`, and userspace enclave runtimes.

Risks: reserved-field validation, LVI `lfence`, callback stack alignment, and exception metadata are security-sensitive. Test signals include SGX selftests, enclave exception handling, callback retry behavior, invalid input tests, readelf extable checks, and LVI mitigation inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vsgx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vma.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vma.c

Purpose: kernel-side vDSO/VVAR mapping, fault, remap, and setup logic for x86 processes.

Important APIs/functions/state: `vclocks_used`, `vdso64_enabled`, `init_vdso_image()`, `vdso_fault()`, `vdso_mremap()`, `vvar_vclock_fault()`, `map_vdso()`, `map_vdso_once()`, `arch_setup_additional_pages()`, `compat_arch_setup_additional_pages()`, `arch_syscall_is_vdso_sigreturn()`, and `vdso_setup()`.

Control flow: init patches alternatives in image text. Mapping chooses an unmapped range for VVAR pages plus vDSO text, installs special mappings for `[vdso]`, main VVAR via helper, and `[vvar_vclock]`, then stores `mm->context.vdso` and `vdso_image`. Fault handlers map vDSO image pages or pvclock/hvclock PFNs if those clock modes are in use. Exec setup maps native, x32, or ia32 images depending on task ABI and enable flags.

State/persistence: per-mm `context.vdso` and `context.vdso_image` persist for the process lifetime or mremap. Global enable flags and `vclocks_used` guide mapping/fault behavior.

Integration points: exec, mm special mappings, VVAR/vclock pages, Hyper-V and pvclock, vDSO image symbols, compat vDSO setup, sigreturn detection, and boot parameter `vdso=`.

Risks: mapping order and VVAR offsets are ABI-sensitive; duplicate mapping prevention avoids abuse. Mremap must keep landing pads coherent. Test signals include vDSO mapping selftests, mremap tests, timekeeping with pvclock/hvclock, 32-bit/x32 exec, signal-return recognition, and boot `vdso=0/1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/Makefile -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/Makefile

Purpose: Kbuild rules for legacy x86-64 vsyscall support.

Important build object: `obj-$(CONFIG_X86_VSYSCALL_EMULATION) += vsyscall_64.o vsyscall_emu_64.o`.

Control flow: builds the C emulator and assembly emulation page only when legacy vsyscall emulation support is configured.

State/persistence: produces kernel objects that map/emulate the fixed vsyscall ABI page.

Integration points: x86 entry page-fault/general-protection handling, fixed mappings, legacy userspace ABI, and Kconfig selection.

Risks: omitting either object breaks configured emulation. Test signals include builds with vsyscall enabled/disabled and runtime `vsyscall=` boot mode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_64.c -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_64.c

Purpose: emulates or exposes the legacy fixed-address x86-64 vsyscall ABI for `gettimeofday`, `time`, and `getcpu`.

Important APIs/state: `vsyscall_mode` (`EMULATE`, `XONLY`, `NONE`), `vsyscall_setup()`, `warn_bad_vsyscall()`, `addr_to_vsyscall_nr()`, `write_ok_or_segv()`, `__emulate_vsyscall()`, `emulate_vsyscall_pf()`, `emulate_vsyscall_gp()`, `get_gate_vma()`, `in_gate_area()`, `in_gate_area_no_mm()`, `set_vsyscall_pgtable_user_bits()`, and `map_vsyscall()`.

Control flow: boot parameter parsing selects mode and disables LASS if necessary for emulation. Fault handlers admit only user instruction-fetch faults to vsyscall addresses, map the fixed address to a vsyscall number, validate return stack and output pointers, run seccomp checks, call the corresponding native syscall implementation, and emulate `ret` by popping the caller from user stack into RIP.

State/persistence: `vsyscall_mode` is read-only after init; `gate_vma` models the pseudo mapping; page-table user bits and fixmap state persist globally when emulation is enabled.

Integration points: page fault and GP handlers, seccomp, signal delivery, fixed mappings, ptrace gate VMA, LASS, and `vsyscall_trace.h`.

Risks: fixed-address ABI weakens ASLR, so mode handling and fault filtering are security-sensitive. Pointer faults intentionally become SIGSEGV to match hardware behavior. Test signals include `vsyscall=none/xonly/emulate`, seccomp mutation tests, bad stack/pointer tests, LASS behavior, ptrace gate-area checks, and legacy glibc workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_emu_64.S -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_emu_64.S

Purpose: defines the physical contents of the legacy vsyscall emulation page.

Important symbol: global object `__vsyscall_page`, exactly one page in size. It contains three 1024-byte slots corresponding to vsyscall functions and places `ret` instructions at the expected call targets, with padding to 4096 bytes.

Control flow: in emulate mode the page can be mapped execute-only/read semantics according to the C mode; executing at a valid slot traps/emulates via fault handling or returns depending on mapping mode details. The code content mainly preserves fixed offsets.

State/persistence: page text is mapped through `map_vsyscall()` and fixed at `VSYSCALL_ADDR`.

Integration points: `vsyscall_64.c`, fixmap, legacy user ABI, and linker symbols.

Risks: page size and offsets are ABI-critical. Test signals include map address checks, readelf/nm symbol size checks, and legacy calls to all three vsyscall slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_emu_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_trace.h -->
## sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_trace.h

Purpose: tracepoint definition for vsyscall emulation events.

Important API: `TRACE_EVENT(emulate_vsyscall, TP_PROTO(int nr), TP_ARGS(nr), ...)`, recording the vsyscall number.

Control flow: tracepoint is invoked from `__emulate_vsyscall()` after address-to-number decoding. It has no independent runtime path.

State/persistence: trace events are emitted to ftrace/perf tracing buffers when enabled.

Integration points: `CREATE_TRACE_POINTS` in `vsyscall_64.c`, Linux tracepoint infrastructure, and perf/ftrace users.

Risks: trace ABI is small but user-observable. Test signals include enabling the tracepoint while running legacy vsyscall callers and confirming recorded numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/Kconfig -->
## sources/distributed-fs/ceph-client/arch/x86/events/Kconfig

Purpose: Kconfig menu for x86 performance monitoring drivers.

Important configs: `PERF_EVENTS_INTEL_UNCORE`, `PERF_EVENTS_INTEL_RAPL`, `PERF_EVENTS_INTEL_CSTATE`, `PERF_EVENTS_AMD_POWER`, `PERF_EVENTS_AMD_UNCORE`, and `PERF_EVENTS_AMD_BRS`. Dependencies gate options on `PERF_EVENTS`, CPU vendor support, PCI, and AMD/Intel features.

Control flow: menu choices determine which perf-event modules/objects are compiled, including AMD BRS branch sampling.

State/persistence: selected config becomes compile-time state stored in `.config` and affects available PMUs and sysfs events.

Integration points: `arch/x86/events/Makefile`, AMD and Intel event drivers, perf userspace, and CPU feature detection.

Risks: incorrect dependencies can expose unsupported build combinations or hide supported PMUs. Test signals include allmodconfig/allyesconfig, vendor-specific builds, and perf PMU enumeration on Intel/AMD systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/Makefile -->
## sources/distributed-fs/ceph-client/arch/x86/events/Makefile

Purpose: top-level Kbuild aggregation for x86 perf-event support.

Important build objects: core `core.o probe.o utils.o`, optional `rapl.o`, AMD subdirectory, `msr.o` under local APIC, Intel subdirectory, and Zhaoxin/Centaur support.

Control flow: object inclusion follows architecture perf configuration and CPU vendor options.

State/persistence: produces perf-event kernel objects and subdirectory builds.

Integration points: Kconfig options, AMD/Intel event drivers, local APIC perf interrupt support, and generic perf core.

Risks: missing object inclusion breaks PMU registration. Test signals include vendor-specific builds, perf list on boot, and local APIC enabled/disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/Makefile -->
## sources/distributed-fs/ceph-client/arch/x86/events/amd/Makefile

Purpose: Kbuild rules for AMD-specific x86 performance monitoring support.

Important build objects: `core.o lbr.o` for AMD CPU support, `brs.o` for `CONFIG_PERF_EVENTS_AMD_BRS`, `power.o`, `ibs.o` with local APIC, `amd-uncore.o` from `uncore.o`, and `iommu.o` when `CONFIG_AMD_IOMMU` is set.

Control flow: compile-time selections combine CPU vendor support, PMU features, local APIC, uncore, and IOMMU availability.

State/persistence: produces AMD PMU drivers and modules/objects registered at init.

Integration points: AMD core PMU, branch stack mechanisms, IBS, power, uncore, IOMMU perf, and Kconfig.

Risks: dependencies must match hardware and exported helper availability. Test signals include AMD allmodconfig builds, perf PMU registration logs, IBS/BRS configurations, and IOMMU-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/brs.c -->
## sources/distributed-fs/ceph-client/arch/x86/events/amd/brs.c

Purpose: implements AMD Family 19h Branch Sampling (BRS), a branch-stack sampling mechanism using debug-extension MSRs.

Important APIs/types: `union amd_debug_extn_cfg`, `amd_brs_hw_config()`, `amd_brs_reset()`, `amd_brs_init()`, `amd_brs_enable/disable[_all]()`, `amd_brs_drain()`, `amd_pmu_brs_sched_task()`, `perf_amd_brs_lopwr_cb()`, and `amd_brs_lopwr_init()`. It uses `BRS_POISON` to mark stale branch records.

Control flow: init detects `X86_FEATURE_BRS` on supported AMD family, sets `x86_pmu.lbr_nr` to 16, and disables hardware filtering. Event config permits only sampling, retired-taken-branch BRS events, non-frequency periods larger than BRS depth, and branch-stack type without fine filtering. Runtime enable toggles `brsmen`; interrupt handling disables/drains BRS, reads saturated branch records from `MSR_AMD_SAMP_BR_*`, sign-extends targets, applies PLM filtering, and fills `cpuc->lbr_entries`.

State/persistence: per-CPU `brs_active`, `lbr_users`, branch entries, MSR `MSR_AMD_DBG_EXTN_CFG`, and poisoned MSR entries protect against cross-task reuse.

Integration points: AMD core PMU static calls, perf branch stack sampling, context switch hooks, ACPI low-power callbacks, and sysfs event exposure from `core.c`.

Risks: BRS records are not PID-tagged, so poisoning on context switch is critical. Low-power states can hold NMIs too long unless BRS is disabled. Test signals include `perf record -j any -e branch-brs`, context-switch leakage tests, low-power idle tests, NMI handling, and branch-stack PLM filtering checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/brs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/core.c -->
## sources/distributed-fs/ceph-client/arch/x86/events/amd/core.c

Purpose: AMD core PMU implementation for generic perf events, hardware cache event mappings, constraints, counter programming, overflow handling, branch-stack integration, and KVM virtualization controls.

Important APIs/state: `amd_pmu_init()`, `amd_core_pmu_init()`, `amd_pmu_hw_config()`, `amd_core_hw_config()`, NB constraint helpers, CPU hotplug callbacks, `amd_pmu_handle_irq()`, `amd_pmu_v2_handle_irq()`, `amd_pmu_v2_snapshot_branch_stack()`, event sysfs attributes, `amd_pmu_enable_virt()`, and `amd_pmu_disable_virt()`. Key state includes `x86_pmu`, hardware event maps, `event_offsets/count_offsets`, `amd_pmu_global_cntr_mask`, per-CPU `amd_nb`, and `perf_nmi_tstamp`.

Control flow: init selects event maps by Zen/family, chooses legacy or core PerfCtr MSRs, detects PerfMonV2 global-control/status support, installs constraint callbacks for Fam15h, Fam17h pair events, and Fam19h BRS, then chooses LBR or BRS branch support. Event config handles host/guest exclude bits, precise-event forwarding to IBS, raw masks, pair constraints, and branch-stack setup. IRQ handlers stop counting, read overflow status or top-bit state, update event counts, save branch stacks, signal perf overflow, acknowledge status, and claim latent NMIs within a bounded window.

State/persistence: programs PMU MSRs, global status/control bits, per-CPU active masks/events, NB owner arrays, branch stacks, and virtualization masks exported for KVM.

Integration points: generic x86 perf core, AMD LBR/BRS/IBS/uncore, KVM mediated vPMU, CPU hotplug, sysfs PMU format/events/caps, APIC NMI handling, and hardware cache event translation.

Risks: counter constraints and NB sharing are race-sensitive across cores. NMI latency handling prevents unknown-NMI storms. PerfMonV2 status reserved bits depend on microcode. Test signals include `perf stat/record` on AMD families 15h/17h/19h/Zen4+, branch-stack sampling, CPU hotplug, KVM guest/host exclude tests, NMI stress, sysfs format checks, and IBS precise forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/ibs.c -->
## sources/distributed-fs/ceph-client/arch/x86/events/amd/ibs.c

Purpose: AMD Instruction-Based Sampling (IBS) PMU support for fetch and op sampling, precise-event forwarding, APIC EILVT setup, NMI handling, memory data-source decoding, and power-management recovery.

Important APIs/types/state: `ibs_caps`, `struct cpu_perf_ibs`, `struct perf_ibs`, `forward_event_to_ibs()`, `perf_ibs_init()`, `perf_ibs_start/stop/add/del()`, `perf_ibs_handle_irq()`, `perf_ibs_nmi_handler()`, `perf_event_ibs_init()`, `get_ibs_caps()`, APIC setup helpers, and `amd_ibs_init()`. Two PMUs are registered as `ibs_fetch` and `ibs_op`.

Control flow: core precise CPU-cycle/uop events can be redirected to IBS op. Event init validates PMU type, grouping, config masks, filters, periods, LD latency/fetch latency/streaming-store filters, and hardware capability bits. Start programs period and enable MSRs while maintaining a four-state bit protocol (`ENABLED`, `STARTED`, `STOPPING`, `STOPPED`) to consume late NMIs. NMI handling reads valid IBS MSRs, updates counts, applies software/hardware filters, builds raw data and memory attributes, saves callchain from interrupt regs, reports overflow, and re-enables hardware unless throttled.

State/persistence: per-CPU active IBS event pointers and state bits, IBS MSRs, APIC EILVT configuration, registered PMUs, syscore PM suspend/resume hooks, and exported `ibs_caps`.

Integration points: AMD core PMU precise forwarding, generic perf PMU API, APIC/NMI infrastructure, PCI northbridge setup for family 10h EILVT, sysfs PMU formats/caps, power management, and CPU hotplug.

Risks: late NMI races are explicitly managed; changing state-bit ordering can create unhandled NMI storms or nested stop warnings. Raw samples can leak physical/kernel addresses, so privilege filtering and clearing matter. Test signals include `perf record -e ibs_fetch/.../` and `ibs_op/.../`, precise CPU-cycle forwarding, LD latency filters, exclude_user/kernel tests, raw sample privilege tests, suspend/resume, CPU hotplug, and APIC EILVT firmware fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/ibs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/iommu.c -->
## sources/distributed-fs/ceph-client/arch/x86/events/amd/iommu.c

Purpose: registers one perf PMU per AMD IOMMU performance-counter block and implements counting-mode events for IOMMU memory/translation/interrupt command counters.

Important APIs/types/state: `struct perf_amd_iommu`, `perf_iommu_event_init()`, `perf_iommu_add/del/start/stop/read()`, `perf_iommu_enable_event()`, `perf_iommu_disable_event()`, `_init_events_attrs()`, `init_one_iommu()`, and `amd_iommu_pc_init()`. It defines sysfs format fields for `csource`, `devid`, `domid`, `pasid`, and masks, plus named v2 events.

Control flow: init checks `amd_iommu_pc_supported()`, builds event attributes, iterates all IOMMUs, allocates a PMU wrapper, discovers bank/counter counts, and registers `amd_iommu_N`. Event init rejects sampling and per-task attach because counters are shared and counting-only. Add allocates a free bank/counter under spinlock; start enables source/match registers and optionally zeroes the counter; stop reads before disabling to avoid power-gating zeros; read masks the 48-bit counter and accumulates into `event->count`.

State/persistence: per-IOMMU PMU list, assignment bitmask, raw spinlock, global cpumask showing CPU0, MMIO/PC registers in the AMD IOMMU, and dynamically allocated sysfs event attribute array.

Integration points: AMD IOMMU driver APIs, generic perf PMU API, sysfs PMU enumeration, Kconfig/Makefile AMD IOMMU gating, and hardware power-gating behavior.

Risks: bank/counter bit indexing must match hardware limits; the bounds check uses max values and should be reviewed for `>=` semantics. Because counts restart from zero and are accumulated on read, missed stop/read ordering loses data. Test signals include `perf stat -e amd_iommu_0/.../`, concurrent counter allocation exhaustion, IOMMU power-state tests, sysfs event/format inspection, and multi-IOMMU systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/iommu.h -->
## sources/distributed-fs/ceph-client/arch/x86/events/amd/iommu.h

Purpose: local header for AMD IOMMU performance-counter register indexes and hardware maximum constants.

Important definitions: `IOMMU_PC_COUNTER_REG`, `IOMMU_PC_COUNTER_SRC_REG`, `IOMMU_PC_PASID_MATCH_REG`, `IOMMU_PC_DOMID_MATCH_REG`, `IOMMU_PC_DEVID_MATCH_REG`, `IOMMU_PC_COUNTER_REPORT_REG`, `PC_MAX_SPEC_BNKS`, and `PC_MAX_SPEC_CNTRS`.

Control flow: no runtime logic; constants are consumed by `iommu.c` when programming AMD IOMMU PC registers.

State/persistence: none locally; defines the offsets used to access persistent hardware registers.

Integration points: AMD IOMMU perf driver and `linux/amd-iommu.h` register access helpers.

Risks: offset mistakes program the wrong IOMMU registers. Test signals include IOMMU perf counter programming tests, hardware register trace/debug, and build coverage for `CONFIG_AMD_IOMMU`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/amd/iommu.h -->
