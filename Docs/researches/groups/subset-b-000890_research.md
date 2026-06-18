# subset-b-000890 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tsc.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/tsc.c

Purpose: implements x86 Time Stamp Counter discovery, calibration, scheduler-clock conversion, and clocksource registration. It decides whether the TSC can be used as a fast monotonic time source and maintains the global `cpu_khz` and `tsc_khz` values exported to other kernel code.

Important APIs/functions: `tsc_early_init()`, `tsc_init()`, `native_sched_clock()`, `native_sched_clock_from_tsc()`, `native_calibrate_tsc()`, `native_calibrate_cpu_early()`, `mark_tsc_unstable()`, `check_tsc_unstable()`, `unsynchronized_tsc()`, `recalibrate_cpu_khz()`, `tsc_save_sched_clock_state()`, and `tsc_restore_sched_clock_state()`. Internal helpers include PIT/HPET/PMTIMER calibration, CPUID crystal-clock decoding, ART detection, and per-CPU `cyc2ns` scaling.

Control flow: early boot checks for TSC, runs SNP secure TSC setup, derives frequency from CPUID, MSR, or quick PIT calibration, initializes `cyc2ns`, and enables the static branch used by `sched_clock`. Later `tsc_init()` retries calibration if needed, initializes secondary CPU conversion state, evaluates reliability and synchronization, registers an early TSC clocksource, and detects Always Running Timer metadata. `init_tsc_clocksource()` later replaces the early clocksource or schedules delayed refinement against HPET/PMTIMER. Watchdog callbacks can mark both TSC clocksources unstable.

State and persistence: state is mostly boot-lifetime global and per-CPU data: `cpu_khz`, `tsc_khz`, `tsc_unstable`, `tsc_clocksource_reliable`, `clocksource_tsc*`, delayed work state, `cyc2ns` latch data, ART base metadata, and suspend offset `cyc2ns_suspend`. Boot parameters `notsc`, `tsc=...`, and `tsc_early_khz=` influence persistent choices for the boot.

Dependencies and integration: integrates with x86 platform hooks from `x86_platform`, clocksource/timekeeping, sched_clock, vDSO clock mode, cpufreq notifiers, APIC deadline timers, HPET/PIT/PMTIMER, hypervisor and UV checks, TSC_ADJUST synchronization, SNP secure TSC, and topology/package logic.

Risks: calibration is sensitive to firmware, SMI latency, broken PIT/HPET/PM timers, virtualized timers, package topology, TSC_ADJUST firmware writes, cpufreq on SMP, and suspend/resume resets. Incorrect reliability decisions can break timekeeping, vDSO time, scheduler timestamps, and APIC timer calibration.

Test signals: boot logs for detected MHz, fast/refined calibration, watchdog instability, and TSC_ADJUST warnings are primary signals. Relevant validation includes booting SMP and suspend/resume systems, cpufreq changes, virtualized guests, systems without legacy PIC, and clocksource watchdog behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tsc_msr.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/tsc_msr.c

Purpose: provides MSR-based CPU/TSC frequency enumeration for selected Intel Atom-family SoCs where PIT/HPET calibration may be unavailable or unreliable.

Important APIs/functions: exports `cpu_khz_from_msr()`. Key data types are `struct muldiv` and `struct freq_desc`, with per-family descriptors for Penwell, Clovertrail, Bay Trail, Cherry Trail, Merrifield, Moorefield, and Lightning Mountain. Matching is driven by `tsc_msr_cpu_ids[]`.

Control flow: `cpu_khz_from_msr()` matches the boot CPU against supported models, reads either `MSR_PLATFORM_INFO` or `MSR_IA32_PERF_STATUS` for the CPU ratio, reads `MSR_FSB_FREQ` for a frequency selector, computes the reference frequency from a multiplier/divider model or a fixed table, programs `lapic_timer_period` when local APIC support is enabled, and marks the TSC frequency known and reliable.

State and persistence: the function has no private mutable state, but it mutates global CPU feature state with `X86_FEATURE_TSC_KNOWN_FREQ` and `X86_FEATURE_TSC_RELIABLE`, and updates the APIC timer period. These decisions persist for the rest of boot.

Dependencies and integration: called by `native_calibrate_cpu_early()` in `tsc.c`. It depends on x86 CPU model matching, Intel-family model identifiers, MSR accessors, APIC timer globals, and `HZ`.

Risks: wrong model descriptors, bad MSR values, or unknown FSB selectors yield wrong CPU/TSC and APIC timing. The code deliberately trusts hardware-reported MSR data and disables the need for a watchdog by marking TSC reliable, so descriptor accuracy is critical.

Test signals: boot on each supported Atom family should show correct processor MHz and stable APIC timers. Failure signs include `Error MSR_FSB_FREQ index ... is unknown`, clock drift, bad delay loops, or APIC timer miscalibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tsc_msr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tsc_sync.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/tsc_sync.c

Purpose: validates and repairs TSC synchronization across CPUs, primarily through the `MSR_IA32_TSC_ADJUST` register and a two-CPU warp measurement during CPU bringup.

Important APIs/functions: `mark_tsc_async_resets()`, `tsc_verify_tsc_adjust()`, `tsc_store_and_check_tsc_adjust()`, and `check_tsc_sync_target()`. Internal paths include the periodic `tsc_sync_check_timer`, `check_tsc_warp()`, `check_tsc_sync_source()`, and work item `tsc_sync_work`.

Control flow: boot and CPU bringup record each CPU's TSC_ADJUST value, normalize first-package values where allowed, compare sibling values, and optionally skip expensive sync tests when the package is already fixed. Otherwise the new CPU asks an online CPU to run a synchronized warp test. Both CPUs repeatedly read ordered TSC values under a raw arch spinlock; backward motion increments warp counters. If TSC_ADJUST exists, the target may retry up to three times after compensating its adjust value. Terminal random or persistent warp schedules work to mark the TSC unstable.

State and persistence: per-CPU `struct tsc_adjust` stores boot and adjusted values, next check time, and warning state. Global atomics, warp counters, `sync_lock`, `last_tsc`, timer state, and `tsc_async_resets` coordinate checks. MSR writes persist in hardware until changed or reset.

Dependencies and integration: used by `tsc.c` during `tsc_enable_sched_clock()`, TSC clocksource resume, CPU bringup, idle/periodic checks, and TSC reliability decisions. It depends on SMP, topology core masks, TSC_ADJUST MSR support, timers, workqueues, and NMI watchdog touching during tight loops.

Risks: bad firmware that writes TSC_ADJUST, asynchronous socket resets, hotplugged packages, or unreliable topology can trigger false instability or leave CPUs skewed. The raw lock measurement is intentionally tight; bugs here can affect CPU bringup timing and global clocksource selection.

Test signals: warnings for TSC_ADJUST differences, compensation messages, synchronization pass/fail logs, and TSC unstable logs are the key signals. Exercise CPU hotplug, multi-socket systems, resume, and systems with/without TSC_ADJUST.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tsc_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/umip.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/umip.c

Purpose: emulates a limited set of UMIP-protected user-mode instructions so applications receive safe dummy values instead of kernel address leaks or fatal general-protection faults.

Important APIs/functions: main external entry is `fixup_umip_exception(struct pt_regs *regs)`. Internal helpers are `identify_insn()`, `emulate_umip_insn()`, `force_sig_info_umip_fault()`, and rate-limited `umip_printk()`. Supported instructions are SGDT, SIDT, SMSW, SLDT, and STR.

Control flow: on a user #GP, `fixup_umip_exception()` checks UMIP support, fetches and decodes the faulting user instruction from `regs`, identifies whether it is an emulatable UMIP instruction, builds dummy data, and writes the result either into the saved register image or user memory. Successful emulation advances `regs->ip`; failed memory copy synthesizes a SIGSEGV while reporting the exception as fixed.

State and persistence: there is no durable kernel state except rate-limit state for logging. For SLDT, the code reads the current mm LDT state under `ldt_usr_sem`. It mutates only the faulting task's saved registers or user memory and signal state.

Dependencies and integration: depends on x86 instruction decoding/evaluation helpers, user access helpers, `pt_regs`, signal delivery, GDT/TSS/LDT constants, CR0 boot state, and the #GP handler path that calls this fixup.

Risks: instruction decoding, operand-size, segmentation, and register-offset handling must match user mode exactly. A wrong copy target could corrupt user state, and excessive fidelity could leak protected kernel layout. LDT locking must be correct under concurrent modify_ldt users.

Test signals: user programs executing SGDT/SIDT/SMSW/SLDT/STR under UMIP should continue with documented dummy results. Negative tests include bad user destinations, register operands, 32-bit compatibility mode, LDT-present and LDT-absent cases, and unsupported encodings that should fall through to normal fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/umip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_frame.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_frame.c

Purpose: implements the frame-pointer based x86 stack unwinder. It walks saved base-pointer chains, validates stack transitions, handles encoded `pt_regs` frames, and exposes return-address iteration to generic stacktrace code.

Important APIs/functions: `unwind_get_return_address()`, `unwind_get_return_address_ptr()`, `unwind_next_frame()`, and `__unwind_start()`. Internal helpers validate final task frames, aligned GCC prologue frames, ftrace frames, encoded frame pointers, and stack bounds.

Control flow: `__unwind_start()` initializes state from task/register inputs, rejects user-mode start states, handles the special IP==0 incomplete-frame case, seeds stack metadata, and advances until the requested first frame. `unwind_next_frame()` stops on user regs or known last task frames, obtains the next frame pointer from saved regs/current BP/queued BP, then calls `update_stack_state()` to validate the new frame and recover the return address. Bad addresses set `state->error` and may dump the current stack once.

State and persistence: state is per-unwind in `struct unwind_state`. Persistent behavior is limited to one-shot dump suppression via static booleans. The unwinder reads task stacks using `READ_ONCE_TASK_STACK` and does not modify task state.

Dependencies and integration: integrates with stack metadata from `get_stack_info()`, task stack layout, entry text boundaries, ftrace graph return recovery, KMSAN annotations, `task_pt_regs()`, and exported stacktrace APIs.

Risks: frame-pointer corruption, stack switching, entry-code interrupts before a frame is established, 32-bit objtool gaps, and concurrent unwinding of running non-current tasks can produce incomplete traces or warnings. Validation must avoid reading outside legitimate task/exception stacks.

Test signals: reliable stack traces from current and sleeping tasks, warnings for intentionally corrupted frame pointers, ftrace graph traces, syscall/interrupt frames, and IP==0 crash scenarios. 32-bit builds intentionally suppress some warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_frame.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_guess.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_guess.c

Purpose: provides a fallback heuristic unwinder that scans stack words for values that look like kernel text addresses when reliable ORC or frame-pointer unwind data is unavailable.

Important APIs/functions: implements the same unwinder surface: `unwind_get_return_address()`, `unwind_get_return_address_ptr()`, `unwind_next_frame()`, and `__unwind_start()`.

Control flow: unwind start aligns the supplied first frame, records stack metadata, and optionally advances until the first plausible text address. Each `unwind_next_frame()` increments the stack pointer through the current stack range, returns when it sees a word passing `__kernel_text_address()`, and follows `stack_info.next_sp` to additional stacks until no valid stack remains.

State and persistence: all active state lives in `struct unwind_state`: task, stack pointer, stack info, and visited stack mask. It reads stack memory without modifying task or global state.

Dependencies and integration: depends on stack bounds from `get_stack_info()`, text-address validation, ftrace/rethook return address recovery, and generic unwind callers expecting the normal unwind API.

Risks: this is intentionally imprecise. It can report false positives from data words that resemble code addresses, miss frames with nonstandard layouts, and cannot provide return-address pointers for patching. It is useful for diagnostics, not correctness-sensitive call-chain reconstruction.

Test signals: stack dumps should contain plausible call chains when other unwinders are disabled. False-positive tolerance and graceful termination on stack boundaries are more important than exact frame counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_guess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_orc.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_orc.c

Purpose: implements the ORC unwinder for x86, using objtool-generated unwind tables to reconstruct call stacks without frame pointers.

Important APIs/functions: `unwind_init()`, `unwind_module_init()`, `unwind_get_return_address()`, `unwind_get_return_address_ptr()`, `unwind_next_frame()`, and `__unwind_start()`. Important helpers include `orc_find()`, `__orc_find()`, module/ftrace/BPF lookup helpers, stack register dereference helpers, and ORC table sorting callbacks.

Control flow: boot-time `unwind_init()` validates ORC table sizes, builds a block lookup table for fast vmlinux text lookup, and enables the unwinder. Module init sorts module ORC IP/entry pairs. A live unwind starts from regs, current CPU registers, or an inactive task frame, validates stack membership, optionally skips the starting regs frame, and iteratively looks up ORC metadata for `ip - 1`. `unwind_next_frame()` calculates the previous stack pointer from the ORC SP rule, optionally dereferences indirect stack slots, recovers IP/SP from call or regs entries, restores BP according to ORC metadata, and prevents non-progressing stack loops.

State and persistence: boot-persistent state includes ORC table symbols, `orc_init`, `unwind_debug`, `lookup_num_blocks`, and module `arch.orc_*` pointers. Per-walk state lives in `struct unwind_state`, including regs/full-regs/partial-regs tracking and stack masks.

Dependencies and integration: tightly coupled to objtool output, `vmlinux.lds.S` ORC sections, module loader ORC data, dynamic ftrace trampolines, BPF JIT frame-pointer fallback, rethook/fgraph return recovery, RCU module lifetime protection, and x86 stack layouts.

Risks: corrupt or unsorted ORC tables disable or degrade unwinding. Missing ORC entries fall back to a guessed frame-pointer rule and mark the trace unreliable. Incorrect stack register rules can read wrong stack slots, loop, or lose interrupt/NMI frames.

Test signals: boot warnings for bad `.orc_unwind` tables, successful stack traces without frame pointers, module stack traces, ftrace trampoline traces, BPF JIT frames, NULL function pointer crashes, and debug dumps under `unwind_debug`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_orc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/uprobes.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/uprobes.c

Purpose: supplies the x86 architecture backend for uprobes and uretprobes: instruction validation, out-of-line execution fixups, optimized trampoline calls, syscall trampolines, breakpoint/debug exception integration, and return-address hijacking.

Important APIs/functions: `arch_uprobe_analyze_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_abort_xol()`, `arch_uprobe_skip_sstep()`, `arch_uprobe_exception_notify()`, `set_swbp()`, `set_orig_insn()`, `arch_uprobe_optimize()`, `arch_uretprobe_trampoline()`, `arch_uretprobe_hijack_return_addr()`, `arch_uretprobe_is_alive()`, `is_uprobe_at_func_entry()`, and the x86-64 `uprobe`/`uretprobe` syscalls.

Control flow: analysis decodes the copied instruction, rejects unsafe prefixes and exception-masking instructions, checks opcode allow tables, records branch/push/default XOL operations, rewrites RIP-relative memory addressing through a scratch register when needed, and marks eligible 5-byte NOP probes optimizable. Normal probe execution installs an INT3, redirects IP to the XOL slot, sets TF, then post-fixes IP, return addresses, scratch registers, and TF state. Optimized probes patch a CALL to a per-mm special trampoline mapped near the probed address; the trampoline enters `sys_uprobe`, restores user register context, invokes generic uprobe handling, and returns through sysret/iret-safe state. Uretprobes use either a native syscall trampoline or breakpoint fallback and can update shadow stack state.

State and persistence: per-instruction state is stored in `struct arch_uprobe` flags, copied instruction bytes, fixups, branch/push parameters, and ops pointer. Per-task XOL state uses `current->utask->autask` for saved TF, trap number, and scratch registers. Per-mm state stores an hlist of trampoline mappings; trampoline pages persist until mm teardown, while the special VMA is intentionally not unmapped during individual trampoline destruction.

Dependencies and integration: depends on x86 instruction decoder/evaluator, generic uprobes core, user access, mm special mappings, page access helpers, text-poke synchronization, shadow stack helpers, syscall entry semantics, die notifiers for INT3/DEBUG, and Kconfig-controlled 32-bit compatibility.

Risks: instruction classification is conservative but hard to keep complete. Wrong RIP-relative rewrite or stack/IP fixup can corrupt user execution. Multi-byte optimization relies on INT3 synchronization and verification callbacks. Trampoline reachability must stay within CALL rel32 range, and shadow-stack handling must match normal return semantics.

Test signals: uprobe selftests for single-step and optimized probes, branch/call/push instructions, RIP-relative loads/stores, native and compat tasks, uretprobe return hijacking, shadow stack enabled tasks, concurrent probe install/remove, and invalid opcode/prefix rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/verify_cpu.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/verify_cpu.S

Purpose: assembly helper included by early boot and trampoline code to verify that a CPU supports the minimum features needed for long mode and SSE.

Important APIs/functions: local symbol `verify_cpu` returns `0` in `%eax` for success and `1` for failure. It consumes required feature masks from `cpufeatures.h`/`cpufeaturemasks.h` and MSR constants for Intel and AMD feature enabling.

Control flow: the routine saves flags, clears dangerous flags, optionally verifies CPUID availability on 32-bit, checks CPUID leaf 1 and extended leaf `0x80000001` against required masks, detects AMD and Intel vendors, clears Intel `IA32_MISC_ENABLE_XD_DISABLE` when safe, and attempts to enable SSE on AMD via `MSR_K7_HWCR` before one retry. It restores flags before returning.

State and persistence: normally only registers and flags are temporary. Side effects can include clearing Intel XD disable and enabling AMD SSE through MSR writes; those hardware state changes persist after return.

Dependencies and integration: included by compressed boot, secondary CPU trampoline, and 32-bit startup paths, so it must run in 32-bit code and avoid normal C runtime assumptions. It depends on CPUID, RDMSR/WRMSR, required feature masks, and caller-side error handling.

Risks: this code executes very early with limited diagnostics. Incorrect masks or unsafe MSR access can prevent boot or secondary CPU bringup. Vendor/model checks around XD disable are deliberately narrow to avoid touching unsupported Intel MSRs.

Test signals: successful 64-bit boot and AP bringup on supported CPUs, expected halt/error path on unsupported CPUs, and no early #GP from MSR access. CPU feature mask changes should be validated in boot and trampoline contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/verify_cpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vm86_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/vm86_32.c

Purpose: implements the 32-bit `vm86` and `vm86old` system calls, allowing legacy virtual-8086 execution for DOS/BIOS-style userspace while emulating privileged instructions and optional IRQ handoff.

Important APIs/functions: `save_v86_state()`, `SYSCALL_DEFINE1(vm86old)`, `SYSCALL_DEFINE2(vm86)`, `handle_vm86_trap()`, `handle_vm86_fault()`, `release_vm86_irqs()`, and internal IRQ helpers. The per-task state is `current->thread.vm86`.

Control flow: syscall entry validates that low address mapping is allowed, allocates per-task vm86 state, copies user register and revectored interrupt data, rejects unsupported screen bitmap mode, saves protected-mode regs, prepares virtual flags, adjusts kernel stack/sysenter state, and returns through modified regs into VM86 mode. Fault handling decodes selected real-mode opcodes such as pushf, popf, int, iret, cli, and sti, emulates virtual flags and interrupt vectors, or saves state back to userspace with a VM86 reason. IRQ requests install real IRQ handlers that signal or wake the owning task and keep per-IRQ pending bits.

State and persistence: persistent state includes per-task vm86 saved regs, user pointer, virtual flags, CPU type, revectored bitmaps, saved `sp0`, and sysenter state. Global `vm86_irqs[16]`, `irqbits`, and `irqbits_lock` track legacy IRQ ownership and pending state.

Dependencies and integration: depends on 32-bit x86 task/thread layout, signal delivery, low-memory mapping policy, LSM `security_mmap_addr()`, user access helpers, segment save/load, IDT-style interrupt vector data at low memory, and IRQ request/free APIs.

Risks: this is a compatibility surface with low-memory access, user-provided segment/register state, manual stack emulation, and historical corner cases around STI/MOV SS interrupt windows. IRQ ownership and task exit cleanup must be correct to avoid dangling task pointers or disabled IRQs.

Test signals: vm86 users such as DOS emulators and vbetool, syscall permission behavior when `mmap_min_addr` blocks page zero, emulated pushf/popf/int/iret/cli/sti flows, debug trap returns, IRQ request/free/get-and-reset behavior, and task exit releasing IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vm86_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vmcore_info_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/vmcore_info_32.c

Purpose: exports 32-bit x86 architecture metadata needed by crash dump tooling to interpret vmcore memory after a kernel crash.

Important APIs/functions: implements `arch_crash_save_vmcoreinfo()`.

Control flow: when crash vmcore metadata is generated, the function conditionally records the `node_data` symbol and `MAX_NUMNODES` length for NUMA builds and records the `X86_PAE` config flag for PAE builds.

State and persistence: it does not maintain local state. It appends key/value and symbol metadata into the global vmcoreinfo note consumed by kdump/crash utilities.

Dependencies and integration: depends on `linux/vmcore_info.h`, page-table configuration, `asm/setup.h`, NUMA globals, and the generic crash dump path that invokes `arch_crash_save_vmcoreinfo()`.

Risks: missing or stale metadata can prevent dump analyzers from locating per-node memory structures or selecting the correct 32-bit page-table format. Conditional compilation must match the actual built kernel configuration.

Test signals: kdump vmcoreinfo notes from 32-bit NUMA and PAE/non-PAE kernels should contain the expected symbols and config markers, and crash analysis tools should parse memory topology correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vmcore_info_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vmcore_info_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/vmcore_info_64.c

Purpose: exports 64-bit x86 crash dump metadata so vmcore analysis tools can translate addresses, page tables, NUMA data, KASLR offsets, and memory encryption masks.

Important APIs/functions: implements `arch_crash_save_vmcoreinfo()`.

Control flow: the function records `phys_base`, `init_top_pgt`, five-level paging enablement, optional NUMA `node_data` symbol and length, `KERNELOFFSET`, `KERNEL_IMAGE_SIZE`, and SME mask value. It snapshots `sme_me_mask` locally before emitting it.

State and persistence: no private state is retained. The function appends architecture values into the vmcoreinfo note for later crash dump consumers.

Dependencies and integration: depends on vmcoreinfo infrastructure, x86 setup symbols, page-table helpers such as `pgtable_l5_enabled()`, KASLR offset reporting, NUMA globals, and SME memory encryption state.

Risks: incorrect metadata causes post-mortem tools to misinterpret virtual-to-physical mappings, encrypted memory bits, KASLR relocation, or node topology. Five-level paging and SME values are especially important for modern 64-bit dumps.

Test signals: generated vmcoreinfo from kdump should include these numbers and symbols. Crash utility validation across 4-level/5-level paging, KASLR on/off, SME on/off, and NUMA/non-NUMA configurations is the main coverage signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vmcore_info_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/vmlinux.lds.S

Purpose: defines the x86 kernel linker script, including image entry points, load segments, section ordering, alignment, runtime symbols, special metadata sections, discard rules, and build-time assertions.

Important APIs/types/functions: this is linker-script/preprocessor logic rather than C APIs. Important symbols include `phys_startup_32/64`, `_text`, `_stext`, `_etext`, `_sdata`, `_edata`, `__init_begin`, `__init_end`, `__bss_start`, `__bss_stop`, `__end_of_kernel_reserve`, `__brk_base`, `__brk_limit`, `_end`, ORC unwind table symbols, mitigation site symbols, and architecture-specific ELF note values.

Control flow: the script selects output format/architecture/entry by config, lays out `.text`, rodata, `.data`, bug table, ORC unwind tables, init text/data, CPU device tables, retpoline/IBT/FineIBT/alternative sections, APIC drivers, exit sections, percpu data, runtime constants, nosave data, BSS, brk, optional SME scratch, debug/modinfo/ELF details, and final discards. It then asserts image size, GOT/PLT/relocation emptiness, mitigation alignment, SRSO aliasing, and thunk placement properties.

State and persistence: the produced ELF layout is persistent boot ABI. Symbols exported here are consumed by early boot, memory reservation, alternatives, ORC unwinder, kexec, module/debug tooling, and mitigation patching.

Dependencies and integration: depends on generic linker-script macros, x86 page sizes, ORC lookup definitions, boot constants, kexec limits, retpoline/IBT/FineIBT/SRSO/ITS configs, SME, Xen/PVH notes, and exported startup symbols.

Risks: layout or alignment mistakes can break boot, large-page permissions, alternative patching, unwinding, kexec relocation, SME encryption, mitigation correctness, or module/debug metadata. Assertions intentionally fail the build for unexpected runtime relocations or unsafe thunk placement.

Test signals: successful x86 builds across 32-bit/64-bit and mitigation configs, `vmlinux` section inspection, ORC unwinder function, boot on KASLR/SME/kexec/Xen/PVH configs, and linker assertion failures when invariants are violated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vsmp_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/vsmp_64.c

Purpose: performs early initialization for ScaleMP vSMPowered x86-64 systems, including detection, optional CPU count capping, and control-register programming.

Important APIs/functions: public entry is `vsmp_init()`. Internal helpers are `detect_vsmp_box()`, `is_vsmp_box()`, `vsmp_cap_cpus()`, and `set_vsmp_ctl()`.

Control flow: `vsmp_init()` probes PCI bus 0 device 0x1f function 0 for ScaleMP vendor/device IDs when early PCI is allowed. If detected, it optionally caps `setup_max_cpus` to the first-board topology when `CONFIG_X86_VSMP` is unset, then maps the vSMP control BAR, logs capabilities/control values, clears the interrupt routing bit when the foundation can route interrupts optimally, disables user IRQ affinity changes via procfs where applicable, writes the updated control register, and unmaps.

State and persistence: `is_vsmp` caches detection state. `setup_max_cpus` and `no_irq_affinity` may be changed during early boot. The vSMP control register write persists in platform firmware/hardware behavior for the running kernel.

Dependencies and integration: depends on CONFIG_PCI, early PCI config access, early ioremap, SMP setup globals, procfs IRQ affinity flag, PCI IDs, and x86 setup ordering before full PCI/resource initialization.

Risks: incorrect detection or BAR mapping can touch wrong MMIO. CPU capping is a functional limitation when the kernel lacks full vSMP support. IRQ affinity disabling changes administrative behavior but is required for platform-routed interrupts.

Test signals: boot logs showing vSMP CTL capabilities/control and optional CPU cap, correct CPU count on unsupported/full-support builds, and stable interrupt routing on ScaleMP hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/vsmp_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/x86_init.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/x86_init.c

Purpose: defines default x86 initialization, CPU-init, platform, and APIC operation tables. These tables provide standard PC behavior while allowing platform, hypervisor, or vendor code to override hooks during boot.

Important APIs/functions: exports `x86_platform`. Defines noop helpers, `x86_wallclock_init()`, `x86_init`, `x86_cpuinit`, `x86_platform`, and `x86_apic_ops`. Default hooks cover resources, MP parsing, IRQ setup, OEM setup, paging, timers, IOMMU, PCI, hypervisor hooks, ACPI root pointer handling, RTC access, sched_clock suspend/restore, real mode, memory encryption transitions, and IO-APIC access.

Control flow: static table initialization wires defaults such as ROM probing, E820 memory setup, DMI setup, IOAPIC/native IRQ init, HPET timer init, APIC clock setup, native page-table init, CMOS wallclock, native CPU/TSC calibration, and real-mode reservation. `x86_wallclock_init()` checks a device-tree CMOS node and replaces RTC hooks with noops when disabled.

State and persistence: the operation tables are global boot-time state. `x86_platform` and `x86_apic_ops` are `__ro_after_init`, so overrides must happen before the read-only-after-init transition. Noop functions avoid null checks for absent platform capabilities.

Dependencies and integration: central integration point for architecture setup code, `tsc.c`, HPET/RTC, ACPI, PCI, APIC/IOAPIC, DMI, E820, paravirt/hypervisor hooks, memory encryption guest operations, realmode setup, and IOMMU shutdown.

Risks: wrong defaults or late overrides can route core boot operations to invalid handlers. Because many subsystems call through these tables, ABI compatibility of hook signatures and init ordering is critical.

Test signals: boot on standard PC, ACPI, devicetree RTC-disabled, hypervisor, encrypted guest, and PCI/IOAPIC configurations. TSC calibration should use the native hooks unless a platform overrides them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/x86_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/Kconfig

Purpose: declares x86 KVM virtualization configuration options, dependencies, selected common capabilities, processor vendor modules, confidential-computing features, emulation features, and debug/proof options.

Important APIs/types/functions: Kconfig symbols include `VIRTUALIZATION`, `KVM_X86`, `KVM`, `KVM_WERROR`, `KVM_SW_PROTECTED_VM`, `KVM_INTEL`, `KVM_INTEL_PROVE_VE`, `X86_SGX_KVM`, `KVM_INTEL_TDX`, `KVM_AMD`, `KVM_AMD_SEV`, `KVM_IOAPIC`, `KVM_SMM`, `KVM_HYPERV`, `KVM_XEN`, `KVM_PROVE_MMU`, `KVM_EXTERNAL_WRITE_TRACKING`, and `KVM_MAX_NR_VCPUS`.

Control flow: enabling `VIRTUALIZATION` exposes the submenu. `KVM_X86` is auto-selected when either vendor backend may be built and selects common KVM capabilities. `KVM` depends on local APIC support and provides `/dev/kvm`. Vendor options select VMX or SVM support, with optional SGX, TDX, SEV/SEV-ES/SEV-SNP, Hyper-V, Xen, SMM, IOAPIC/PIC/PIT, and proof/debug features layered by dependency.

State and persistence: Kconfig choices persist into `.config` and drive compiled objects, module availability, selected generic KVM features, maximum vCPU range, and whether warning builds are fatal.

Dependencies and integration: sources generic `virt/kvm/Kconfig`, ties x86 KVM into APIC, PM, performance events, guest memory fd, memory attributes, VFIO, async page faults, IRQ routing, dirty logging, and vendor CPU support.

Risks: dependency mistakes can expose unsupported feature combinations or hide required infrastructure. Defaults for confidential-computing options are enabled when their host prerequisites are met, so build and runtime testing must cover those paths. `KVM_WERROR` can break randomized or sanitizer builds if selected too broadly.

Test signals: `olddefconfig` and randconfig coverage, module build matrix for `kvm`, `kvm-intel`, and `kvm-amd`, feature-specific configs for TDX/SEV/SGX/Hyper-V/Xen/SMM/IOAPIC, and validation of `KVM_MAX_NR_VCPUS` bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/Makefile

Purpose: builds the x86 KVM core and vendor modules, wires shared KVM make logic, generates assembly offsets, and enforces KVM export-symbol policy.

Important APIs/types/functions: build variables include `ccflags-y`, `kvm-y`, `kvm-intel-y`, `kvm-amd-y`, conditional object additions for feature configs, `obj-$(CONFIG_KVM_X86)`, `obj-$(CONFIG_KVM_INTEL)`, `obj-$(CONFIG_KVM_AMD)`, `AFLAGS_*`, `targets`, `clean-files`, and make macros `get_kvm_exports`/`check_kvm_exports`.

Control flow: the file adds the local include path and optional `-Werror`, includes `virt/kvm/Makefile.kvm`, lists core x86 KVM objects, conditionally adds TDP MMU, IOAPIC/PIC/PIT, Hyper-V, Xen, SMM, SGX, TDX, SEV, and on-Hyper-V objects, then registers the core/vendor modules. It declares dependencies from VMX/SVM assembly entry objects to generated `kvm-asm-offsets.h`, generated from `kvm-asm-offsets.s`. When KVM_X86 is enabled, recursive grep checks fail the build if unwanted `EXPORT_SYMBOL_GPL` or `EXPORT_SYMBOL` usages appear outside an allowlist.

State and persistence: no runtime state. Persistent outputs are built objects/modules and generated offset headers; clean rules remove generated headers.

Dependencies and integration: depends on Kbuild, generic KVM make fragments, arch/x86/kvm and virt/kvm source trees, vendor subdirectories, config symbols from Kconfig, and assembly offset generation for vmenter code.

Risks: missing object gating can produce unresolved symbols or absent feature code. Offset header dependencies are critical for assembly/C ABI sync. Export policy grep can be brittle but protects KVM-internal symbol hygiene.

Test signals: successful builds for built-in and module KVM, Intel-only, AMD-only, Hyper-V host, TDX, SEV, SGX, IOAPIC/SMM/Xen combinations, clean rebuilds regenerating `kvm-asm-offsets.h`, and intentional forbidden exports causing the expected make error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/Makefile -->
