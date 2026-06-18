# Research: subset-b-000849

Grouped research for SPARC kernel signal, SMP, interrupt, sun4v trap, syscall, sysfs, timekeeping, trampoline, and 32-bit trap support. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil_64.c

Purpose: supports sparc64 signal-frame save and restore for floating-point/vector-visible FPU state and register-window spill buffers.

Important APIs/types/functions: `save_fpu_state()`, `restore_fpu_state()`, `save_rwin_state()`, and `restore_rwin_state()` operate on `__siginfo_fpu_t`, `__siginfo_rwin_t`, `pt_regs`, `thread_info->fpregs`, `fpsaved`, `xfsr`, `gsr`, `reg_window`, and `rwbuf_stkptrs`.

Control flow: signal delivery copies only the lower and/or upper FP register halves indicated by `FPRS_DL`/`FPRS_DU`, then stores FSR, GSR, and FPRS. Signal return validates 8-byte alignment, disables live FPU ownership with `fprs_write(0)`, clears `TSTATE_PEF`, copies requested register halves back, and marks the saved FPRS bits. Register windows are copied by `wsaved` count and then forced back to user stack via `set_thread_wsaved()` and `synchronize_user_stack()`.

State and persistence: all state is per-current-thread architectural context; no filesystem persistence exists. Bad user pointers or still-unsynchronized windows produce `-EFAULT`.

Dependencies and integration points: depends on sparc64 signal layout, `thread_info`, user-copy helpers, FPU macros, register-window stack synchronization, and signal return code.

Risks: alignment and `wsaved <= NSWINS` checks protect ABI parsing. Partial FP saves must match FPRS bits or signal frames expose stale/corrupt state. Register-window restore is fragile because unsynchronized windows indicate user stack failure.

Test signals: signal delivery/return across FP users, vector/GSR users, alternate stacks, invalid/misaligned signal frames, forced register-window spills, and faults during user copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/smp_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/smp_32.c

Purpose: provides the generic 32-bit SPARC SMP orchestration layer, delegating platform-specific boot and IPI mechanics to sun4m, sun4d, and LEON backends.

Important APIs/types/functions: shared globals include `cpu_callin_map`, `smp_commenced_mask`, `sparc32_ipi_ops`, and `smp_penguin_ctable`. Entry points include `smp_prepare_cpus()`, `smp_setup_cpu_possible_map()`, `smp_prepare_boot_cpu()`, `__cpu_up()`, `smp_callin()`, `arch_smp_send_reschedule()`, `arch_send_call_function_*_ipi()`, `smp_resched_interrupt()`, `smp_call_function*_interrupt()`, `smp_store_cpu_info()`, and `/proc` helpers `smp_bogo()`/`smp_info()`.

Control flow: boot enumerates PROM CPU instances into possible/present masks, stores boot CPU PROM/MID/frequency data, then calls the platform boot routine. `__cpu_up()` invokes the selected platform `boot_one_cpu()` and waits for `cpu_online()`, while secondary CPUs enter `smp_callin()` and run `sparc_start_secondary()`: cache/TLB flush, platform pre-start, CPU hotplug notify, timer registration, delay calibration, CPU info setup, platform pre-online, set online, enable IRQs, and enter idle.

State and persistence: runtime state is CPU masks, per-CPU `cpu_data`, `current_thread_info()->cpu`, and call-in flags; no persistence.

Dependencies and integration points: integrates with PROM CPU start, SRMMU context-table handoff, clockevents via `register_percpu_ce()`, scheduler IPIs, generic SMP call-function handling, and platform files.

Risks: boot waits rely on cache-coherent visibility of `cpu_callin_map` and `smp_commenced_mask`. Unsupported CPU models deliberately `BUG()`. Wrong PROM MID or platform operation selection breaks IPI routing.

Test signals: boot with multiple sun4m/sun4d/LEON CPUs, CPU possible/present masks, `smp_call_function*`, reschedule IPIs, per-CPU timers, `/proc/cpuinfo` BogoMIPS, and stuck-secondary timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/smp_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/smp_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/smp_64.c

Purpose: implements sparc64 SMP boot, cross-call delivery, TLB/cache shootdowns, CPU topology masks, CPU hotplug, scheduler pokes, CPU capture, and per-CPU allocator setup.

Important APIs/types/functions: exports `cpu_sibling_map`, `cpu_core_map`, `cpu_core_sib_map`, and `cpu_core_sib_cache_map`. Key routines are `smp_callin()`, `__cpu_up()`, `smp_setup_processor_id()`, `xcall_deliver()`, Spitfire/Cheetah/sun4v deliverers, `arch_send_call_function_*_ipi()`, `smp_flush_tlb_*()`, `smp_flush_dcache_folio_impl()`, `flush_dcache_folio_all()`, `smp_tsb_sync()`, `smp_capture()`/`smp_release()`, hotplug hooks, `arch_smp_send_reschedule()`, `smp_init_cpu_poke()`, `smp_send_stop()`, and `setup_per_cpu_areas()`.

Control flow: secondary CPUs register per-CPU offsets and sun4v KTSB data, flush TLBs, initialize timers, enable forced P-cache if needed, set `callin_flag`, attach `init_mm`, notify hotplug, wait in `smp_commenced_mask`, then enter idle. Boot uses OBP or sun4v hypervisor startup, then synchronizes `%tick` on non-hypervisor systems. Cross calls populate the current CPU `trap_block` mondo block and CPU list under local IRQ disable; delivery is selected for Spitfire ASI dispatch, Cheetah pipelined dispatch, or sun4v hypervisor `cpu_mondo_send()` with retry/error handling. TLB/cache functions use xcalls or generic `smp_call_function_many()` plus local flushes.

State and persistence: runtime state spans CPU masks, per-CPU `trap_block`, mondo queues, topology masks, `smp_commenced_mask`, CPU poke flags, capture atomics, and per-CPU offsets. No persistent storage is touched.

Dependencies and integration points: depends on PROM/hypervisor CPU lifecycle, trap-block layout, TLB/cache assembly xcall handlers, MM context IDs, cpumasks, clock/tick code, CPU hotplug, kgdb, Starfire translation, LDOMs, and NUMA-aware percpu allocation.

Risks: mondo delivery runs with interrupts disabled and shares per-CPU buffers, so reentrancy or timeout mistakes can panic or corrupt xcalls. Hypervisor error handling intentionally skips some faulty/offline CPUs but panics on no progress. Hotplug must remove topology and IRQ targeting before offlining. There is a visible missing semicolon in the non-aliasing `__local_flush_dcache_folio()` branch in this snapshot, which is a compile-risk if that branch is built.

Test signals: multi-CPU boot on Spitfire/Cheetah/sun4v, xcall stress, TLB shootdowns under mmap/munmap/fork, D-cache flushes for aliasing mappings, CPU hotplug, LDOM stop/start, scheduler IPI poke fallback, kgdb roundup, CPU capture around PROM calls, and percpu allocator initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/smp_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sparc_ksyms.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sparc_ksyms.c

Purpose: exposes the architecture symbol `saved_command_line` to loadable modules.

Important APIs/types/functions: the file only includes `linux/export.h` and uses `EXPORT_SYMBOL(saved_command_line)`.

Control flow: there is no runtime control flow. The export is consumed by module symbol resolution.

State and persistence: the exported state is the kernel boot command line already maintained elsewhere; this file does not mutate or persist it.

Dependencies and integration points: specifically documents the dependency from `drivers/sbus/char/openprom.c` and any other module requiring the saved boot command line.

Risks: removing or renaming the export can break out-of-tree or modular OpenPROM users. There is no functional logic to test beyond symbol availability.

Test signals: modular builds should link users of `saved_command_line`; `modpost` should not report unresolved symbols for OpenPROM-related modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sparc_ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/spiterrs.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/spiterrs.S

Purpose: provides low-level UltraSPARC Spitfire trap handlers for access errors, correctable ECC events, and instruction/data access exceptions before handing decoded state to C.

Important APIs/symbols: defines `__spitfire_access_error`, `__spitfire_cee_trap`, `__spitfire_data_access_exception_tl1`, `__spitfire_data_access_exception`, `__spitfire_insn_access_exception_tl1`, and `__spitfire_insn_access_exception`. It reads/writes ASIs for `AFSR`, `AFAR`, `UDBH/UDBL_ERROR`, DMMU/IMMU SFSR/SFAR, and calls C handlers such as `spitfire_access_error()`.

Control flow: the access-error path disables error reporting to prevent recursive RED-state traps, captures AFSR/AFAR/trap-level/type, reads and conditionally clears UDB error registers, clears sticky AFSR bits, selects TL0/TL1 trap entry, and calls C with `pt_regs` plus encoded status/address. The CEE path prioritizes uncorrectable errors by branching to the main access-error handler; otherwise it disables only correctable-error reporting and reuses the capture path. Access-exception handlers capture and clear MMU fault status, special-case window spill/fill traps, then enter trap frames and call C.

State and persistence: updates hardware sticky error registers and transient trap registers only; no persistent kernel data is stored here.

Dependencies and integration points: depends on UltraSPARC-I/II ASI semantics, trap entry/return code (`etrap`, `etraptl1`, `rtrap`), window-fixup handlers, and C fault/error reporters.

Risks: ordering and `membar #Sync` are critical to avoid lost or recursive hardware errors. TL1 paths have limited register/state assumptions. Wrong AFSR/UDB clearing can hide ECC or access faults.

Test signals: fault-injection or platform error logs for UE/CE, TL0/TL1 access faults, window spill/fill fault recovery, and confirmation that C handlers see AFAR/SFSR/trap-type data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/spiterrs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sstate.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sstate.c

Purpose: reports Linux soft-state transitions to sun4v hypervisors that support the soft-state API.

Important APIs/types/functions: `do_set_sstate()`, `sstate_reboot_call()`, `sstate_panic_event()`, `sstate_init()`, and `sstate_running()` use `sun4v_hvapi_register()`, `sun4v_mach_set_soft_state()`, `prom_sun4v_guest_soft_state()`, reboot notifiers, and the panic notifier chain.

Control flow: `core_initcall` verifies `tlb_type == hypervisor`, registers HV group `HV_GRP_SOFT_STATE` v1.0, marks support, tells PROM the guest participates, sets "Linux booting", and registers panic/reboot hooks. `late_initcall` moves to normal/running state. Reboot and panic paths set transition state with aligned static message strings.

State and persistence: `hv_supports_soft_state` gates calls; messages are static 32-byte aligned constants. State is externally visible to firmware/hypervisor but not persisted by Linux.

Dependencies and integration points: integrates with sun4v hypervisor APIs, reboot/panic notifier ordering, image virtual-to-real address conversion, and PROM soft-state awareness.

Risks: notifier paths can run during failure; calls must tolerate hypervisor errors. Message buffers must remain static and real-address convertible. Non-sun4v systems must be no-ops.

Test signals: sun4v boot should show hypervisor soft state progressing through booting/running; reboot, halt, poweroff, and panic should set transition messages; non-hypervisor boot should not call the API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/stacktrace.c

Purpose: implements SPARC stack trace collection for current and other tasks.

Important APIs/types/functions: `save_stack_trace()` and `save_stack_trace_tsk()` export the generic stacktrace API. `__save_stack_trace()` walks `sparc_stackf`, `pt_regs`, `thread_info`, `kstack_valid()`, `kstack_is_trap_frame()`, and optional function-graph tracer return stacks.

Control flow: for current task it flushes pending stack-trace/ftrace state and reads `%fp`; for other tasks it starts from saved `thread_info->ksp`. It applies `STACK_BIAS`, validates each frame, distinguishes trap frames from normal frames, stops on user trap frames, records caller PCs after `trace->skip`, optionally skips scheduler functions, and repairs function-graph trampoline PCs to original return addresses.

State and persistence: no owned state; it reads kernel stacks and writes caller addresses into caller-provided `stack_trace`.

Dependencies and integration points: used by generic stacktrace/debug code, ftrace function graph tracing, SPARC trap-frame layout, and `kstack.h` validators.

Risks: stack walking must avoid invalid or user frames. Function graph replacement depends on `return_to_handler` and per-task ret-stack indexing. Other-task traces can race with scheduling unless callers observe expected locking/stop conditions.

Test signals: `save_stack_trace()` from current task, blocked-task stack dumps, traces across trap frames, scheduler frame skipping, and function graph tracer enabled/disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/starfire.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/starfire.c

Purpose: detects Sun Enterprise Starfire/E10000 systems and translates interrupt map entries to Starfire-specific extended UPA interrupt delivery registers.

Important APIs/types/functions: global `this_is_starfire`, `check_if_starfire()`, `starfire_hookup()`, `starfire_translate()`, and `struct starfire_irqinfo` track per-UPAID translation registers and IMAP slots.

Control flow: detection looks for `/ssp-serial`. Hookup allocates an IRQ info record for a UPAID, computes the hardware MID and translation register base, initializes 32 slots, and marks already-programmed registers as reserved. Translation locates the info record by IMAP bus MID, reuses or allocates a slot for the IMAP, maps the requested logical UPAID to real Starfire form, writes the translation register, and returns the slot index.

State and persistence: `sflist` stores runtime translation slots; hardware translation registers are programmed. No disk persistence.

Dependencies and integration points: integrates with sparc64 IRQ delivery, UPA register access, PROM probing, and Starfire checks in SMP mondo delivery.

Risks: allocation failure or missing board records halt/panic because interrupt delivery would be unreliable. Slot exhaustion indicates inconsistent IMAP handling. Existing register contents are preserved defensively.

Test signals: Starfire boot detection, IRQ routing for devices behind multiple boards, preservation of firmware mappings, and non-Starfire systems leaving `this_is_starfire` clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/starfire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4d_irq.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4d_irq.c

Purpose: implements sun4d SS1000/SC2000 interrupt controller support, including SBUS IRQ demultiplexing, IRQ chip operations, timer setup, and SBI distribution.

Important APIs/types/functions: `sun4d_handler_irq()`, `sun4d_sbus_handler_irq()`, `sun4d_mask_irq()`, `sun4d_unmask_irq()`, `sun4d_build_device_irq()`, `sun4d_init_sbi_irq()`, `sun4d_init_IRQ()`, `sun4d_init_timers()`, `sun4d_distribute_irqs()`, and `sun4d_load_profile_irq()` use `struct sun4d_handler_data`, `board_to_cpu`, `pil_to_sbus`, `sun4d_imsk_lock`, and `sparc_config`.

Control flow: top-level IRQ handling clears the CPU interrupt latch, optionally handles IPI work, enters generic IRQ accounting, and dispatches either CPU-local IRQ buckets or SBUS interrupts. SBUS handling reads BW interrupt masks by SBUS level, acknowledges pending SBI bits, walks pending slots, maps encoded board/level/slot IRQ buckets, invokes `generic_handle_irq()`, and releases SBI bits. Initialization maps bootbus timer registers, registers the L10 timer IRQ, configures clocksource/clockevent features, clears PROM-pending SBI IRQs, and wires `sparc_config` callbacks.

State and persistence: maintains MMIO timer pointer, board-to-CPU routing, IRQ handler data allocations, and controller masks. Hardware interrupt mask state is runtime only.

Dependencies and integration points: depends on Open Firmware `sbi`/`cpu-unit` topology, BW/SBI register helpers, generic IRQ buckets, clocksource/timer code, SMP sun4d IPI code, and trap-table fixups for level-14 timers.

Risks: IRQ encoding must match board/level/slot hardware or devices misroute. SMP mask updates need `sun4d_imsk_lock`. Timer register mapping and trap-table patching happen early and halt on fatal setup failures.

Test signals: device IRQ allocation from OF nodes, SBUS slot interrupt dispatch, timer interrupt delivery, SMP IPI at `SUN4D_IPI_IRQ`, profile timers, SBI pending-IRQ cleanup, and IRQ routing to selected CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4d_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4d_smp.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4d_smp.c

Purpose: supplies sun4d-specific SMP boot, IPI, cross-call, and per-CPU timer handling for the generic sparc32 SMP layer.

Important APIs/types/functions: `sun4d_cpu_pre_starting()`, `sun4d_cpu_pre_online()`, `smp4d_boot_cpus()`, `smp4d_boot_one_cpu()`, `smp4d_smp_done()`, `sun4d_ipi_interrupt()`, `smp4d_cross_call_irq()`, `smp4d_percpu_timer_interrupt()`, and `sun4d_init_smp()` use `cpu_callin_map`, `current_set`, `smp_penguin_ctable`, `sun4d_ipi_work`, `ccall_info`, `cross_call_lock`, LED state, and `sun4d_imsk_lock`.

Control flow: secondary startup lights LEDs, enables level-15 and blocks level-14, swaps its call-in bit, waits for `current_set` and CPU assignment, installs `%g6`, attaches `init_mm`, waits for `smp_commenced_mask`, then enables PIL14. Boot starts PROM CPUs at `sun4d_cpu_startup` and waits for call-in. IPI senders set per-CPU work flags and generate controller messages; the interrupt drains single-call, mask-call, and reschedule work. Cross-calls serialize through `ccall_info`, fire level-15 IPIs, and spin until all targets enter/exit.

State and persistence: runtime-only per-CPU IPI flags, cross-call arguments, LED values, CPU list rotation, and readiness flags.

Dependencies and integration points: uses sun4d bootbus/controller registers, PROM startcpu, SRMMU context table, generic SMP call functions, clockevents, timer profile IRQs, and IRQ trap table patching.

Risks: cross-call spin waits have no timeout. Shared `ccall_info` requires strict serialization. Secondary boot depends on cache/TLB flushes and correct `current_set` visibility. IRQ levels 14/15 are overloaded for timers/IPIs.

Test signals: secondary CPU boot, LED/progress changes, call-function/reschedule IPIs, cross-call completion on all CPUs, per-CPU timer events, and IRQ distribution after `smp4d_smp_done()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4d_smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4m_irq.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4m_irq.c

Purpose: implements sun4m interrupt register support, IRQ mask mapping, NMI/error reporting, timer registration, and `sparc_config` IRQ callbacks.

Important APIs/types/functions: globals `sun4m_irq_percpu[]` and `sun4m_irq_global` are consumed by entry/SMP code. Key routines are `sun4m_mask_irq()`, `sun4m_unmask_irq()`, `sun4m_build_device_irq()`, `sun4m_clear_clock_irq()`, `sun4m_nmi()`, `sun4m_unmask_profile_irq()`, `sun4m_clear_profile_irq()`, `sun4m_load_profile_irq()`, `sun4m_init_timers()`, and `sun4m_init_IRQ()`.

Control flow: initialization maps interrupt registers from the OF `interrupt` node, masks global sources, clears per-CPU masks, optionally programs interrupt target, then sets `sparc_config` callbacks. Timer init maps per-CPU/global counter addresses from the OF `counter` node, configures timer mode, selects L10 clocksource and L10/L14 event features, registers the timer IRQ, clears per-CPU profile timers, and patches the level-14 trap table under SMP. IRQ build converts OBP priority values into PILs and mask bits from `sun4m_imask`, then attaches a level IRQ chip.

State and persistence: stores MMIO register pointers and per-IRQ handler mask/percpu data. Hardware mask/timer registers are runtime state.

Dependencies and integration points: depends on OF `interrupt`/`counter` properties, SBUS MMIO helpers, generic IRQ buckets, timer/clockevent code, sun4m SMP IPIs, and trap-table patching.

Risks: sun4m IRQ priority encodings are ambiguous without `intr` property class bits. Wrong mask bit enables/disables unrelated devices. NMI path halts after reporting asynchronous errors.

Test signals: device IRQ allocation for onboard/SBUS/VME priorities, masking/unmasking, L10 timer interrupt, L14 profile timer on SMP, NMI error log, and boot on systems with two or four CPU interrupt registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4m_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4m_smp.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4m_smp.c

Purpose: provides sun4m-specific SMP boot, software interrupt IPIs, cross-calls, and per-CPU timer interrupt handling.

Important APIs/types/functions: `sun4m_cpu_pre_online()`, `smp4m_boot_cpus()`, `smp4m_boot_one_cpu()`, `smp4m_smp_done()`, `sun4m_ipi_*()`, `sun4m_cross_call()`, `smp4m_cross_call_irq()`, `smp4m_percpu_timer_interrupt()`, and `sun4m_init_smp()` use `current_set`, `cpu_callin_map`, `smp_penguin_ctable`, `sun4m_irq_percpu`, `ccall_info`, and `cross_call_lock`.

Control flow: boot unblocks profile IRQs, then each CPU is started at a per-CPU trampoline entry and waited on through `cpu_callin_map`. Secondary CPUs swap the call-in bit, flush cache/TLB, load `%g6` from `current_set`, attach `init_mm`, and wait for `smp_commenced_mask`. IPIs are software interrupts at levels 12, 13, and 14 for single, mask, and reschedule; cross-calls use level 15 and a serialized shared call record.

State and persistence: runtime-only cross-call arguments/completion flags and interrupt registers; no persistence.

Dependencies and integration points: integrates with `smp_32.c`, `trampoline_32.S`, PROM `startcpu`, SRMMU context table, sun4m IRQ register mapping, generic SMP call handlers, and per-CPU `sparc32_clockevent`.

Risks: cross-call waits have no timeout and require every targeted CPU to service level-15. `SUN4M_NCPUS` bounds arrays. Secondary startup relies on correct trampoline offset for CPU IDs 1-3.

Test signals: multi-CPU sun4m boot, all IPI classes, cross-call completion, per-CPU periodic/oneshot timers, CPU call-in timeout behavior, and correct active_mm/current thread setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4m_smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_ivec.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_ivec.S

Purpose: handles sun4v hypervisor interrupt queues for CPU mondos, device mondos, resumable errors, and non-resumable errors at trap level.

Important APIs/symbols: defines `sun4v_cpu_mondo`, `sun4v_dev_mondo`, `sun4v_res_mondo`, and `sun4v_nonres_mondo`. It uses ASI queue head/tail registers, `trap_block` queue physical addresses/masks, `cpu_mondo_counter`, `ivector_table_pa`, IRQ work storage, and C callbacks `sun4v_resum_error()`, `sun4v_resum_overflow()`, `sun4v_nonresum_error()`, and `sun4v_nonresum_overflow()`.

Control flow: each handler compares queue head/tail and retries if empty. CPU mondos derive the current CPU from the trap block, increment the mondo counter, load the three-word xcall payload, advance the queue head, and jump to the handler PC encoded in the first word. Device mondos fetch IVEC or VIRQ cookie, link the bucket into IRQ work, and set the device softint. Error mondos copy a 64-byte queue entry into a kernel buffer if free, advance head, enter an IRQ trap frame, and call C; if the kernel buffer slot is full, they collapse head to tail and report overflow.

State and persistence: mutates hypervisor queue heads, CPU mondo counters, IRQ work queues, and per-CPU error buffers; no persistent storage.

Dependencies and integration points: depends on sun4v queue layout, trap-block offsets, CPU xcall ABI from `smp_64.c`, device IRQ softint processing, and error-reporting C code.

Risks: head/tail updates and kernel-buffer overflow handling are critical to avoid repeated traps or lost errors. CPU mondo handler trusts the payload PC. Queue entries are physical loads using ASI_PHYS_USE_EC.

Test signals: CPU xcall delivery, device IVEC/VIRQ interrupts, MSI-like device mondos, resumable/non-resumable error logging, queue-empty retry, and forced overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_ivec.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_mcd.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_mcd.S

Purpose: bridges sun4v precise memory-corruption-detected exceptions from assembly trap context to the C reporter.

Important APIs/symbols: defines `sun4v_mcd_detect_precise`, passes `pt_regs`, `%l4`, and `%l5` to `sun4v_mem_corrupt_detect_precise()`, then returns through `rtrap`.

Control flow: the trap frame has already been established by the trap table. The routine moves saved trap arguments into output registers, calls C with `pt_regs` at `sp + PTREGS_OFF`, and branches to normal trap return.

State and persistence: no owned state; it only forwards transient trap information.

Dependencies and integration points: depends on sun4v trap table setup, SPARC register convention used by etrap, and C MCD handling.

Risks: argument register expectations must match trap-entry code and the C function signature. It is intentionally minimal because memory corruption paths should avoid complex assembly.

Test signals: sun4v MCD fault injection or platform error simulation should invoke `sun4v_mem_corrupt_detect_precise()` with valid regs and return/terminate according to C policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_mcd.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_tlb_miss.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_tlb_miss.S

Purpose: supplies sun4v fast TLB miss, TSB miss, access-exception, unaligned, privileged-action, floating unaligned, and trap-table patch handlers.

Important APIs/symbols: defines `sun4v_itlb_miss`, `sun4v_dtlb_miss`, `sun4v_itlb_load`, `sun4v_dtlb_load`, `sun4v_dtlb_prot`, `sun4v_itsb_miss`, `sun4v_dtsb_miss`, `sun4v_tsb_miss_common`, `sun4v_iacc*`, `sun4v_dacc*`, `sun4v_mna`, `sun4v_privact`, `sun4v_lddfmna`, `sun4v_stdfmna`, and `sun4v_patch_tlb_handlers()`.

Control flow: fast ITLB/DTLB paths read fault address/context from hypervisor scratchpad, compute TSB tag and pointer, load tag/PTE, validate tag and execute permissions, then call hypervisor MMU map traps to install entries. Misses branch to page-table walk code with fault code. Protection and bad real-address paths hand off to real fault handling or C error reporters. Access exceptions build encoded type/context arguments and enter TL0/TL1 trap frames. The patch function rewrites generic trap-table sites into branches to sun4v handlers and flushes the modified instructions.

State and persistence: updates MMU mappings through hypervisor fast traps, temporary trap-block fields for huge TSB, global sun4v error variables, and patched in-memory trap instructions.

Dependencies and integration points: depends on sun4v hypervisor fault-info layout, TSB format, page-table walk assembly, hugepage scratchpad registers, C fault/error functions, and instruction-cache flushing.

Risks: fast path clobber conventions are tight; wrong tag/PTE permission handling can map invalid translations. Hypervisor map failures at TL1 are fatal-report paths. Runtime patching must compute branch displacements correctly.

Test signals: user/kernel ITLB and DTLB misses, executable permission faults, write-protection faults, hugepage TSB paths, bad real-address reports, unaligned/floating unaligned traps, privileged action traps, and post-patch trap-vector behavior on sun4v.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_tlb_miss.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sys32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sys32.S

Purpose: implements a tiny 32-bit compatibility assembly wrapper for `mmap2`.

Important APIs/symbols: defines global `sys32_mmap2`, branches to `sys_mmap`, and shifts `%o5` by 12 to convert mmap2 page units into byte offset units expected by `sys_mmap`.

Control flow: the wrapper loads the `sys_mmap` address, jumps without a normal call/return stack disturbance, and uses the delay slot to scale the sixth argument.

State and persistence: no state is stored; it only transforms syscall arguments.

Dependencies and integration points: used by the 64-bit kernel compat syscall table for 32-bit applications. Depends on SPARC syscall register calling convention and `sys_mmap` semantics.

Risks: offset scaling is ABI-sensitive. The comment notes avoiding call-as-jump because it breaks return-stack behavior.

Test signals: 32-bit `mmap2()` on a 64-bit kernel with nonzero page offsets, large offsets, and tracing enabled should map the same file locations as other architectures' compat mmap2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sys32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc32.c

Purpose: implements sparc64 compat syscall wrappers where 32-bit user ABI argument and structure layouts differ from native 64-bit kernel APIs.

Important APIs/types/functions: defines compat syscalls for `truncate64`, `ftruncate64`, `stat64`, `lstat64`, `fstat64`, `fstatat64`, `sparc_sigaction`, `rt_sigaction`, `pread64`, `pwrite64`, `readahead`, `fadvise64`, `fadvise64_64`, `sync_file_range`, and `fallocate`. `cp_compat_stat64()` converts `struct kstat` to `struct compat_stat64`.

Control flow: most wrappers combine high/low 32-bit words into 64-bit offsets or lengths, then call `ksys_*` helpers. Stat wrappers query VFS into `kstat` then copy fields, encoded devices, munged UID/GID, timestamps, and padding to user memory. Signal-action wrappers convert handler/restorer pointers and compat sigsets before/after `do_sigaction()`.

State and persistence: no owned state. It reads kernel file/stat/signal data and writes user buffers. File size operations persist through VFS helpers, not this conversion layer.

Dependencies and integration points: connects 32-bit syscall table entries to generic VFS, signal, and syscall helper APIs; depends on `compat_stat64`, `compat_sigaction`, and SPARC signal ABI.

Risks: high/low word ordering and sign/zero extension are ABI-critical. `cp_compat_stat64()` must keep padding and timestamp layout compatible with old userspace. Signal numbers are negated for legacy SPARC `sparc_sigaction` convention.

Test signals: 32-bit stat family ABI tests, large-file truncate/ftruncate/pread/pwrite/fallocate, `rt_sigaction` with compat masks/restorer, and fault injection on user-copy failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc_32.c

Purpose: provides 32-bit native SPARC implementations of SPARC-specific or ABI-unusual syscalls and mmap placement checks.

Important APIs/types/functions: `sys_getpagesize()`, `arch_get_unmapped_area()`, `sys_sparc_pipe()`, `sparc_mmap_check()`, `sys_mmap2()`, `sys_mmap()`, `sys_sparc_remap_file_pages()`, `sys_nis_syscall()`, `sparc_breakpoint()`, `sys_sparc_sigaction()`, `sys_rt_sigaction()`, and `sys_getdomainname()`.

Control flow: mmap placement enforces task-size limits and shared-cache aliasing alignment unless hugepage files supply their own mask. `sparc_pipe()` returns the second fd in register `UREG_I1`, matching SPARC ABI. `mmap2()` converts 4KB units to native pages; `mmap()` shifts byte offsets by `PAGE_SHIFT`; remap converts 4KB units. Legacy unsupported syscall logging is rate-limited by a static count. Breakpoints send `SIGTRAP`; signal-action wrappers handle SPARC's negative legacy signal convention and explicit restorer argument.

State and persistence: static `nis_syscall` count limits logs. Syscalls may create mappings, pipes, or VFS effects through generic helpers; the file owns no persistence.

Dependencies and integration points: generic MM/VFS/signal/UTS helpers, `current_pt_regs()`, SPARC register ABI, hugetlb alignment helpers, and syscall tables.

Risks: cache-color alignment is required for shared mappings. Offset conversions differ between `mmap` and `mmap2`. Domain-name copying must release `uts_sem` on all paths.

Test signals: native 32-bit mmap alignment and range failures, pipe register return ABI, signal action/restorer behavior, breakpoints, unsupported syscall logging capped after six messages, and getdomainname length/fault cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc_64.c

Purpose: implements sparc64-specific syscall helpers, mmap layout/range policy, SysV IPC demultiplexing, 32-bit personality handling, time adjustment ABI quirks, user trap installation, and memory-ordering control.

Important APIs/types/functions: `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, `get_fb_unmapped_area()`, `arch_pick_mmap_layout()`, `sys_sparc_pipe()`, `sys_sparc_ipc()`, `sys_sparc64_personality()`, `sparc_mmap_check()`, `sys_mmap()`, `sys64_munmap()`, `sys64_mremap()`, `sys_nis_syscall()`, `sparc_breakpoint()`, `sys_getdomainname()`, `sys_sparc_adjtimex()`, `sys_sparc_clock_adjtime()`, `sys_utrap_install()`, `sys_memory_ordering()`, `sys_rt_sigaction()`, and `sys_kern_features()`.

Control flow: mmap code avoids the sparc64 VA hole, enforces 32-bit `STACK_TOP32` for compat tasks, color-aligns file/shared mappings, supports top-down 32-bit layout fallback, and offers framebuffer-friendly alignment. SysV IPC dispatches old multiplexed subcalls to generic semaphore/message/shared-memory helpers. `utrap_install()` validates trap type, manages per-thread shared/copy-on-write utrap arrays, returns old handlers, and installs new handlers. Time adjustment wrappers compensate for sparc64's 32-bit `tv_usec` field inside `__kernel_timex`.

State and persistence: modifies process mm layout, per-thread utrap pointer/refcount array, current `tstate` memory-model bits, personality flags, and normal syscall side effects. No direct filesystem persistence beyond delegated syscalls.

Dependencies and integration points: generic MM, hugetlb, SysV IPC, signal, POSIX time, personality, UTS, trap, context tracking, and SPARC thread flags.

Risks: `invalid_64bit_range()` is a hard ABI/security guard around the VA hole. Utrap copy-on-write refcounts are subtle. Time ABI overlays require exact structure interpretation. `sparc64_personality()` hides `PER_LINUX32` from userspace return values.

Test signals: 64-bit and 32-bit mmap placement around VA hole, MAP_FIXED shared alias rejection, framebuffer mmap alignment, SysV IPC subcalls, `utrap_install()` old/new/copy-on-write cases, `adjtimex`/`clock_adjtime` timeval layout, memory ordering model changes, and breakpoints from compat/native tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/syscalls.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/syscalls.S

Purpose: provides sparc64 low-level syscall entry wrappers, fork/clone/exec stubs, signal-return stubs, syscall tracing paths, native/compat dispatch, error return protocol, and fork return.

Important APIs/symbols: defines `sys64_execve`, `sys64_execveat`, compat `sys32_execve*`, `sys32_sigstack`, `sys32_sigreturn`, `sys_rt_sigreturn`, `sys32_rt_sigreturn`, `sys_vfork`, `sys_fork`, `sys_clone`, `__sys_clone3`, `ret_from_fork`, `sparc_exit_group`, `sparc_exit`, `linux_sparc_syscall32`, `linux_sparc_syscall`, trace labels, and `ret_sys_call`.

Control flow: exec/fork/clone stubs flush register windows before jumping/calling C helpers. Signal return calls C restorers and then either returns directly or invokes `syscall_trace_leave()` if flags demand. Syscall dispatch validates `%g1` against `NR_syscalls`, loads function addresses from 32-bit or 64-bit tables, handles tracing/seccomp/audit/tracepoint/NOHZ entry, marshals up to six args from input registers, calls the target, stores return value into `pt_regs`, advances TPC/TNPC, and clears or sets carry bits based on errno unless `TIF_SYS_NOERROR` forces success.

State and persistence: mutates pt_regs, thread flags such as `TI_NEW_CHILD`/`TI_WSAVED`, register-window state, and syscall condition codes. Delegated syscalls perform actual persistent effects.

Dependencies and integration points: depends on `entry.h` offsets, syscall tables, tracing/seccomp hooks, signal restore code, process fork helpers, and SPARC register-window ABI.

Risks: register-window flushing and carry-bit errno convention are ABI-critical. Trace paths can modify registers and must reload args/syscall number. Compat dispatch must zero-extend 32-bit arguments correctly.

Test signals: native and compat syscall smoke tests, ptrace/seccomp/audit tracing, restart/error/success returns, `force_successful_syscall_return()`, fork/vfork/clone/clone3, kernel thread `ret_from_fork`, exec wrappers, and signal return from traced and untraced tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/syscalls.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/syscalls/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/syscalls/Makefile

Purpose: generates SPARC syscall UAPI headers and kernel syscall table include files from `syscall.tbl`.

Important APIs/variables/rules: defines generated directories `arch/$(SRCARCH)/include/generated/{uapi/,}asm`, source `syscall.tbl`, scripts `scripts/syscallhdr.sh` and `scripts/syscalltbl.sh`, commands `cmd_syshdr` and `cmd_systbl`, pattern rules for `unistd_%.h` and `syscall_table_%.h`, targets `unistd_32.h`, `unistd_64.h`, `syscall_table_32.h`, and `syscall_table_64.h`, and the phony `all` target.

Control flow: Make creates output directories via `$(shell mkdir -p ...)`, then pattern rules invoke the generic scripts with ABI filter `common,$*`. `targets` records generated files for Kbuild tracking. `all` depends on all UAPI and KAPI generated headers.

State and persistence: build outputs are generated headers under the architecture generated include tree. No runtime state exists.

Dependencies and integration points: feeds `systbls_32.S`, `systbls_64.S`, and userspace UAPI syscall numbers. Depends on Kbuild `if_changed`, `FORCE`, `CONFIG_SHELL`, and syscall table script semantics.

Risks: ABI filters must match rows in `syscall.tbl`; incorrect generation breaks syscall numbers or table contents. Directory creation at parse time is intentional but can matter for out-of-tree builds.

Test signals: `make arch/sparc/include/generated/uapi/asm/unistd_32.h`, table includes generated with expected native/compat entries, incremental rebuild after `syscall.tbl` changes, and clean build from empty generated tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sysfs.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sysfs.c

Purpose: registers sparc64 CPU topology/sysfs devices, cache/clock attributes, and optional sun4v MMU statistics controls.

Important APIs/types/functions: per-CPU `mmu_stats` and `cpu_devices`; generated `show_*` handlers for MMU and CPU data; `show_mmustat_enable()`, `store_mmustat_enable()`, `register_mmu_stats()`, `unregister_mmu_stats()`, `register_cpu_online()`, `unregister_cpu_online()`, `check_mmu_stats()`, and `topology_init()`.

Control flow: init probes sun4v `sun4v_mmustat_info()` support, registers every possible CPU device, then installs a CPU hotplug online state. Online registration creates per-CPU files for clock tick and cache sizes; when supported, it also creates `mmu_stats/` and `mmustat_enable`. Reads/writes of `mmustat_enable` execute on the target CPU through `work_on_cpu()`, because the hypervisor MMU stats configuration is CPU-local.

State and persistence: per-CPU `hv_mmu_statistics` buffers are hypervisor-filled when enabled. CPU device sysfs files reflect runtime CPU/cache data; no disk persistence.

Dependencies and integration points: depends on `cpu_data`, Linux CPU devices/hotplug, sun4v hypervisor MMU stats APIs, per-CPU storage, and sysfs device attributes.

Risks: MMU stat buffers must be aligned and configured with physical addresses on the correct CPU. File creation errors are not deeply propagated. Hotplug removal must mirror created attributes.

Test signals: `/sys/devices/system/cpu/cpu*/clock_tick` and cache attributes, optional `mmu_stats` group on sun4v, enabling/disabling stats per CPU, CPU online/offline with attribute cleanup, and non-hypervisor systems without MMU stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls.h

Purpose: declares SPARC-specific syscall entry points and compat wrappers used by syscall tables and assembly entry code.

Important APIs/types/functions: declares native helpers such as `sys_getpagesize()`, `sys_sparc_pipe()`, `sys_nis_syscall()`, `sys_getdomainname()`, `do_rt_sigreturn()`, `sys_mmap()`, and `sparc_breakpoint()`. Under `CONFIG_SPARC32` it declares `sys_mmap2()` and `sys_sparc_remap_file_pages()`. Under `CONFIG_SPARC64` it declares `sys_sparc_ipc()`, `sparc64_personality()`, `sys64_munmap()`, `sys64_mremap()`, `sys_utrap_install()`, context functions, and many compat large-file/stat/io wrappers.

Control flow: no runtime flow; it provides prototypes to keep C and assembly-visible syscall symbols consistent.

State and persistence: none.

Dependencies and integration points: included by syscall C files and table assembly, and depends on `asm/utrap.h`, `linux/compat.h`, `linux/signal.h`, and syscall ABI types.

Risks: duplicate or mismatched prototypes can hide ABI/signature bugs until link or runtime. Conditional blocks must match the objects built for 32-bit versus 64-bit kernels.

Test signals: sparse/build warnings for syscall prototype mismatches, successful native/compat table assembly, and no undefined symbols from syscall tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls_32.S

Purpose: materializes the 32-bit native SPARC syscall table from the generated syscall table include.

Important APIs/symbols: defines `sys_call_table` in `.data` with `.long` entries and maps both `__SYSCALL()` and `__SYSCALL_WITH_COMPAT()` to native entries for a 32-bit kernel.

Control flow: no executable logic; the generated `<asm/syscall_table_32.h>` expands into table entries.

State and persistence: creates a kernel data table of syscall function addresses.

Dependencies and integration points: consumed by 32-bit syscall entry assembly and generated by `syscalls/Makefile` from `syscall.tbl`.

Risks: table entry width and alignment must match 32-bit assembly lookup. Generated include contents must be available before assembly.

Test signals: 32-bit SPARC build, syscall number dispatch correctness, table symbol visibility, and generated include rebuilds after `syscall.tbl` edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls_64.S

Purpose: materializes sparc64 native and optional compat syscall tables from generated include files.

Important APIs/symbols: defines `sys_call_table32` under `CONFIG_COMPAT`, and aliases `sys_call_table64` and `sys_call_table` for native 64-bit syscalls. Entries are emitted with `.word`. `__SYSCALL_WITH_COMPAT()` resolves to compat handlers for the 32-bit table and native handlers for the 64-bit table.

Control flow: no executable flow; assembly syscall dispatch loads table entries indexed by syscall number.

State and persistence: creates read-only/text-section syscall address tables used at runtime.

Dependencies and integration points: depends on generated `syscall_table_32.h` and `syscall_table_64.h`, `CONFIG_COMPAT`, and `syscalls.S` dispatch code.

Risks: entry size and symbol alignment must match dispatch's `lduw` table loads. Compat/native macro definitions must be reset correctly around includes.

Test signals: native and compat syscall table lookup, builds with and without `CONFIG_COMPAT`, generated table content inspection, and syscall ABI smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/termios.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/termios.c

Purpose: converts between SPARC user `termio`/`termios`/`termios2` ABI layouts and kernel `ktermios`.

Important APIs/types/functions: `kernel_termios_to_user_termio()`, `user_termios_to_kernel_termios()`, `kernel_termios_to_user_termios()`, `user_termios_to_kernel_termios_1()`, and `kernel_termios_to_user_termios_1()` use `_VMIN` and `_VTIME` compatibility indexes plus canonical `VEOF`/`VEOL`, `VMIN`, and `VTIME`.

Control flow: conversion copies flags, line discipline, control-character arrays, and for `termios2` input/output speeds. The special SPARC/SysV compatibility rule maps character slots 4 and 5 as `VEOF`/`VEOL` when `ICANON` is set, otherwise as `VMIN`/`VTIME`.

State and persistence: no owned state. It reads/writes user termios buffers and kernel terminal settings; terminal driver state is maintained elsewhere.

Dependencies and integration points: used by generic tty ioctl conversion hooks through `linux/termios_internal.h` and SPARC UAPI layouts.

Risks: control-character index remapping is ABI-sensitive and differs by canonical mode. Partial user-copy failures return accumulated nonzero errors. `NCC` versus `NCCS` sizes must match target ABI structures.

Test signals: tty ioctl round trips for `TCGETS`, `TCSETS`, `TCGETS2`, old `termio`, canonical and noncanonical mode VMIN/VTIME behavior, speed fields in `termios2`, and user-copy fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/termios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/time_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/time_32.c

Purpose: implements sparc32 timer interrupt handling, clocksource/clockevent setup, per-CPU SMP clockevents, profile-PC correction, RTC platform registration, and time initialization.

Important APIs/types/functions: `profile_pc()`, `timer_interrupt()`, `setup_timer_ce()`, `timer_cs_read()`, `setup_timer_cs()`, `register_percpu_ce()`, Mostek RTC accessors, `clock_probe()`, `clock_init()`, `sparc32_late_time_init()`, `sbus_time_init()`, and `time_init()`. Globals include `timer_cs_lock`, `timer_cs_internal_counter`, `timer_ce`, `sparc32_clockevent`, `rtc_lock`, and `master_l10_counter`.

Control flow: platform IRQ code sets `sparc_config`; `time_init()` chooses PCI or SBUS timer setup and installs late init. Timer interrupts clear the platform clock IRQ, increment the software clocksource counter under seqlock when enabled, and invoke the global clockevent handler if enabled. Clocksource reads combine the interrupt count with the current L10 counter offset. SMP per-CPU clockevents program profile/L14 timers for periodic or oneshot events.

State and persistence: maintains in-memory clocksource counter, clockevent enabled flags, per-CPU clockevent devices, and RTC platform devices. RTC persistence is delegated to the RTC driver.

Dependencies and integration points: depends on platform `sparc_config` callbacks from sun4m/sun4d/PCI code, SBUS counters, clocksource/clockevents frameworks, M48T59 RTC driver, OF platform devices, and profiling.

Risks: timer counter read races are protected by seqlock; wrong offset calculation loses time around limit hits. SMP timer feature flags must match hardware. RTC probe only accepts primary address-bearing EEPROM.

Test signals: clocksource monotonicity, periodic tick delivery, per-CPU timer registration on SMP, oneshot profile timers where available, `udelay`/timekeeping stability, RTC registration for `mk48t02`/`mk48t08`, and profiling PC adjustment inside copy/zero/lock functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/time_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/time_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/time_64.c

Purpose: implements sparc64 tick/STICK/Hummingbird timer operations, clocksource and clockevent registration, scheduler clock, delay loops, RTC platform registration, CPU-frequency clock tick scaling, and timer IRQ handling.

Important APIs/types/functions: `tick_ops`, operation sets `tick_operations`, `stick_operations`, and `hbtick_operations`; `time_init_early()`, `time_init()`, `setup_sparc64_timer()`, `timer_interrupt()`, `sparc64_next_event()`, `sched_clock()`, `read_current_timer()`, `__delay()`, `udelay()`, `sparc64_get_clock_tick()`, cpufreq notifier, and RTC probes for CMOS, BQ4802, Mostek, sun4v, and Starfire.

Control flow: early init chooses `%tick`, `%stick`, or Hummingbird I/O STICK based on `tlb_type` and CPU version, initializes frequency, offset, and VDSO mode, then patches `get_tick` instruction sequences. Full init registers the clocksource, computes clockevent limits, and initializes this CPU's tick hardware. Per-CPU timer setup disables interrupt/protection bits with interrupts masked, copies the template clockevent, and registers it. Timer IRQ clears the appropriate softint, accounts IRQ0, and calls the per-CPU event handler. RTC init chooses Starfire or sun4v synthetic RTCs, otherwise probes OF RTC/Mostek/BQ4802 devices.

State and persistence: runtime state includes `tick_operations`, `sparc64_events`, `tb_ticks_per_usec`, `cmos_regs`, RTC platform resources, per-CPU frequency reference tables, and CPU `clock_tick` scaling. Persistent clock contents are handled by RTC drivers.

Dependencies and integration points: depends on SPARC tick/STICK registers, sun4v restrictions, Open Firmware frequencies/resources, clocksource/clockevents, VDSO clock modes, cpufreq, RTC drivers, Starfire detection, and SMP setup in `smp_64.c`.

Risks: tick compare writes have CPU errata workarounds and must execute at aligned sites. sun4v forbids writing tick/STICK. Hummingbird I/O STICK reads/writes need rollover-safe sequences. `sparc64_next_event()` currently calls `tick_operations.add_compare` instead of `tick_ops`, so alternate operation selection should be reviewed carefully.

Test signals: boot on Spitfire, Hummingbird, Cheetah/STICK, and sun4v; clocksource/VDSO mode selection; timer interrupt delivery on all CPUs; cpufreq transitions scaling `clock_tick`; `udelay` accuracy; RTC device registration; sched_clock monotonicity; and oneshot timer programming near minimum/maximum deltas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/time_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/trampoline_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/trampoline_32.S

Purpose: contains 32-bit SPARC secondary CPU startup trampolines for sun4m, sun4d, and LEON.

Important APIs/symbols: exports `sun4m_cpu_startup`, `sun4d_cpu_startup`, and `leon_smp_cpu_startup`; uses `current_set`, `smp_penguin_ctable`, `poke_srmmu`, `smp_callin()`, and `cpu_panic()`.

Control flow: sun4m entries select CPU-specific trap bases, set PSR/WIM/TBR, derive current thread from `current_set`, set stack, enable traps, call SRMMU initialization, and enter `smp_callin()`. sun4d sets a common trap table, reads CPU ID from bootbus, stores Viking tmp CPU ID, establishes stack/current, initializes SRMMU, and calls in. LEON loads the SRMMU context-table pointer from `smp_penguin_ctable`, reads CPU ID from ASR17, then follows the same stack/trap/MMU/call-in pattern.

State and persistence: initializes CPU architectural registers, MMU context register, `%g6` current pointer, and stack pointer. No persistence.

Dependencies and integration points: called by PROM CPU startup from sun4m/sun4d/LEON SMP code; depends on trap tables, thread layout, SRMMU poke routine, and current-set setup by the boot CPU.

Risks: each path runs before normal kernel services and must avoid invalid mappings. CPU ID derivation and stack indexing must match platform hardware. Returning from `smp_callin()` is fatal.

Test signals: secondary boot on sun4m CPUs 1-3, sun4d bootbus CPU ID path, LEON SMP startup, correct `%g6`/stack in `smp_callin()`, and panic path if call-in returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/trampoline_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/trampoline_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/trampoline_64.S

Purpose: implements sparc64 secondary CPU startup from firmware/hypervisor state to normal kernel `smp_callin()`.

Important APIs/symbols: exports `sparc64_cpu_startup` and `sparc64_cpu_startup_end`; uses PROM `call-method` for TLB locking, hypervisor fast MMU map traps on sun4v, `prom_entry_lock`, `tramp_stack`, `kern_locked_tte_data`, `num_kernel_image_mappings`, `init_irqwork_curcpu()`, `sun4v_register_mondo_queues()`, `init_cur_cpu_trap()`, PROM trap-table setup, and `smp_callin()`.

Control flow: startup branches by CPU family, programs Cheetah/Spitfire/Niagara cache and tick interrupt controls, locks kernel image mappings into I/D TLBs via OBP or hypervisor calls, sets privileged state and MMU contexts, switches to a temporary stack, initializes IRQ work and per-CPU trap state, optionally registers sun4v mondo queues, sets the firmware trap table to the kernel trap table, releases the PROM lock, loads the idle thread from the cookie pointer into `%g6/%g4`, sets the real kernel stack, enables interrupts, and calls `smp_callin()`.

State and persistence: mutates CPU MMU/TLB, cache-control, tick compare, trap-table, context, FPRS, ASI, stack, and current-task registers. No persistent storage.

Dependencies and integration points: invoked by `smp_64.c` CPU boot through PROM or sun4v hypervisor. Depends on locked kernel mappings, trap-block layout, firmware client interface buffers, and processor-family detection macros.

Risks: early code cannot touch `%g4/%g5/%g6` until trap table ownership is correct. PROM/hypervisor calls are serialized by `prom_entry_lock`. Mapping or trap-table mistakes strand the CPU before C code.

Test signals: secondary boot on Spitfire, Cheetah/Cheetah+, Niagara/sun4v, LDOM CPU start, mondo queue registration, TLB lock coverage for multiple kernel image mappings, and `sparc64_cpu_startup_end` length users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/trampoline_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/traps_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/traps_32.c

Purpose: handles 32-bit SPARC traps for illegal/privileged instructions, hardware traps, unaligned accesses, FPU disabled/exceptions, tag overflow, watchpoints, coprocessor traps, divide-by-zero, BUG reporting, and trap initialization.

Important APIs/types/functions: `die_if_kernel()`, `do_hw_interrupt()`, `do_illegal_instruction()`, `do_priv_instruction()`, `do_memaccess_unaligned()`, `do_fpd_trap()`, `do_fpe_trap()`, `handle_tag_overflow()`, `handle_watchpoint()`, `handle_reg_access()`, `handle_cp_disabled()`, `handle_cp_exception()`, `handle_hw_divzero()`, optional `do_BUG()`, and `trap_init()`.

Control flow: kernel-mode fatal traps print registers, walk register-window callers with bounds/alignment checks, dump nearby instructions, taint, and terminate. User traps translate to `SIGILL`, `SIGBUS`, `SIGFPE`, `SIGEMT`, or `SIGTRAP` style faults. FPU-disabled traps enable EF, lazily save/load FPU ownership on UP or per-task FPU state on SMP, and initialize first-use registers. FPU exception traps save FPU state, optionally emulate unfinished/unimplemented operations via `do_mathemu()`, otherwise decode FSR exception bits into signal codes.

State and persistence: mutates per-task FPU registers/FSR/queue/depth, `last_task_used_math` on UP, `TIF_USEDFPU` on SMP, `used_math`, active_mm in `trap_init()`, and static fake FPU buffers used to clear stray errors.

Dependencies and integration points: depends on SPARC trap/register layouts, FPU save/load helpers, math emulation, signal delivery, `init_mm`, and assembly offset constants.

Risks: lazy FPU ownership is subtle across UP/SMP. Kernel FPU exceptions are tolerated only a limited number of times. `trap_init()` includes compile-time offset checks via an undefined symbol to catch assembly/C layout drift.

Test signals: user illegal/privileged/unaligned/FPU/divzero traps, FPU first-use and context switching, math emulation for unfinished FP ops, kernel fatal trap diagnostics, BUG verbose export, and boot-time `trap_init()` offset consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/traps_32.c -->
