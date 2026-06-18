# subset-b-000839 research

This grouped report covers SuperH architecture kernel files under `sources/distributed-fs/ceph-client/arch/sh/kernel`, including SH-Mobile power management, low-level entry code, debugging/tracing, module/perf/ptrace/signal handling, kexec, SMP, syscall, and boot setup glue. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/cpuidle.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/cpuidle.c

Purpose: registers SH-Mobile cpuidle states backed by the architecture standby/sleep implementation. It exposes regular sleep, sleep with RAM self-refresh, and software standby with self-refresh as cpuidle C-states.

Important APIs and control flow: `cpuidle_mode[]` maps cpuidle indexes to `SUSP_SH_*` mode flags. `cpuidle_sleep_enter()` bounds the requested state by an `allowed_mode`-derived state, calls `sh_mobile_call_standby(cpuidle_mode[k])`, and returns the state actually entered. `cpuidle_driver` describes C1/C2/C3 latencies, residency, names, and unusable defaults. `sh_mobile_setup_cpuidle()` enables C2/C3 based on `sh_mobile_sleep_supported` and calls `cpuidle_register()`.

State, dependencies, and risks: persistent state is only the registered cpuidle driver and mutable state flags. It depends on `pm.c`/`sleep.S` for actual standby execution and on platform self-refresh registration to set `sh_mobile_sleep_supported`. `allowed_mode` is currently hard-coded to `SUSP_SH_SLEEP`, so deeper states can be exposed but never selected by this function unless that policy changes. Test signals are platform boot, cpuidle sysfs visibility, and suspend/resume/idle residency validation on SH-Mobile hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/cpuidle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/pm.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/pm.c

Purpose: prepares and invokes SH-Mobile low-power entry code from on-chip RAM, with notifier hooks and board-supplied self-refresh snippets.

Important APIs and control flow: `sh_mobile_call_standby()` calls pre-sleep notifiers, optionally flushes caches for MMU-affecting modes, jumps into copied on-chip standby code, then calls post-sleep notifiers. `sh_mobile_register_self_refresh()` populates a `struct sh_sleep_data` at `RAM_BASE`, copies common enter code, board pre/post self-refresh code, and common resume code, then advertises supported flags. `sh_pm_enter()` selects sleep or standby-self-refresh for suspend-to-mem and calls standby. `sh_pm_init()` registers platform suspend operations.

State, dependencies, and risks: state lives in on-chip memory at `RAM_BASE`, global notifier chains, and `sh_mobile_sleep_supported`. Dependencies include `sleep.S` symbols, board-specific self-refresh code, cache flushing, BL bit handling, and fixed SH-Mobile register addresses. Risks include overrun of the 0x600-byte code/data budget, SoC-specific RAM base mismatch, stale cache/MMU state, and notifier ordering. Test signals are suspend-to-RAM cycles, cpuidle deep-state entry, and board self-refresh resume reliability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/sleep.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/sleep.S

Purpose: self-contained SH-Mobile assembly copied to on-chip memory to enter sleep/standby modes and resume without relying on external memory or normal kernel mappings.

Important APIs and control flow: `sh_mobile_sleep_enter_start` saves mode, VBR, PR, SR, optional banked/general registers, stack pointer, STBCR, and optional MMU/cache registers into `struct sh_sleep_data`. It switches VBR to on-chip memory, invokes board self-refresh pre-code when `SUSP_SH_SF` is set, configures STBCR for sleep/software standby/R-standby/U-standby, then loops on `sleep`. `sh_mobile_sleep_resume_start` reconstructs the data-area base from the vector address, restores SR/SPC/VBR/SP, STBCR, board post-code, MMU/cache registers, optional banked registers, and returns with `rte`.

State, dependencies, and risks: state is the copied code plus `SH_SLEEP_*` data offsets. It depends on assembler offsets, exact banked-register semantics, fixed cache/MMU register addresses supplied by `pm.c`, and interrupt-vector placement at `onchip_mem + 0x600`. Risks are severe: wrong offsets, missing cache invalidation, or unsupported standby mode can hang resume. Test signals require hardware suspend/resume loops with self-refresh, MMU-preserving R-standby, and interrupt-vector recovery checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/crash_dump.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/crash_dump.c

Purpose: provides SH old-memory copying for crash dump readers.

Important APIs and control flow: `copy_oldmem_page()` maps a crash-dump PFN with `ioremap()`, copies `csize` bytes from `offset` into the supplied `iov_iter` with `copy_to_iter()`, unmaps, and returns the bytes copied. A zero-size request returns immediately.

State, dependencies, and risks: it has no persistent state and depends on generic crash dump code, `ioremap()`, `iov_iter`, and old-memory reservation from kexec/crashkernel setup. It does not explicitly validate that `offset + csize` is within a page, so callers must honor the page-sized contract. Test signals are kdump capture reads, `/proc/vmcore` extraction, zero-length reads, and partial iterator-copy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/crash_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/debugtraps.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/debugtraps.S

Purpose: defines the SH debug trap dispatch table for `trapa` values 0x30 through 0x3f.

Important APIs and control flow: `debug_trap_table` is a 16-entry data table consumed by `entry-common.S` `debug_trap`. Most entries point to `debug_trap_handler`, while 0x3c dispatches to `breakpoint_trap_handler`, 0x3d to `singlestep_trap_handler` or debug fallback, 0x3e to `bug_trap_handler`, and 0x3f to `sh_bios_handler` or debug fallback depending on config.

State, dependencies, and risks: state is static table layout; dependencies are trap handler symbols emitted by traps, kgdb, hw-breakpoint, and optional SH BIOS support. The table position and trap-number arithmetic must stay in sync with entry assembly. Test signals are kgdb breakpoint/single-step, BUG trap reporting, BIOS earlyprintk/debug delegation, and fallback debug trap behavior when optional configs are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/debugtraps.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/disassemble.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/disassemble.c

Purpose: prints symbolic SuperH instruction disassembly around a faulting PC for diagnostics.

Important APIs and control flow: the `sh_table[]` opcode table encodes instruction names, argument types, and nibble patterns. `print_sh_insn()` matches a 16-bit instruction, extracts registers/displacements/immediates, formats operands, and resolves PC-relative loads to symbol-like comments when possible. `show_code()` validates even PC alignment, reads three instructions before through five after the current PC with `__get_user()`, marks the current instruction, and prints decoded output.

State, dependencies, and risks: state is static opcode metadata. Dependencies include `pt_regs`, user/kernel fault-safe reads, `%pS` symbolization, and SH instruction encoding knowledge. Risks are stale/incomplete opcode coverage, faulting while dereferencing PC-relative targets, and misleading output for newer extensions. Test signals are oops logs with code dumps, explicit invalid address handling, and table comparisons against known SH encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/disassemble.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/dma-coherent.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/dma-coherent.c

Purpose: implements SH cache maintenance hooks for coherent DMA allocation and DMA synchronization.

Important APIs and control flow: `arch_dma_prep_coherent()` purges the cache range backing a page allocation. `arch_sync_dma_for_device()` converts a physical address through SH cache-operation virtual addressing and selects invalidate, writeback, or purge based on DMA direction; invalid directions call `BUG()`.

State, dependencies, and risks: there is no persistent state. Dependencies include SH cacheflush primitives, `phys_to_virt()`, `sh_cacheop_vaddr()`, and Linux DMA API direction semantics. Risks are aliasing mistakes on cached/uncached mappings, over/under-flushing for device-visible buffers, and fatal BUGs on bad callers. Test signals are DMA map/unmap stress, bidirectional transfers with cacheline sharing, and driver data-corruption checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/dma-coherent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/dumpstack.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/dumpstack.c

Purpose: provides SH stack, memory, and symbol dump helpers used by oops, warnings, and diagnostics.

Important APIs and control flow: `dump_mem()` prints aligned 32-byte rows with fault-tolerant `__get_user()` reads. `printk_address()` formats reliable or questionable symbols. `stack_reader_dump()` scans a stack range for kernel text addresses and optionally expands function-graph tracer return addresses. `show_trace()` invokes `unwind_stack()` with print callbacks, and `show_stack()` prints task identity, raw stack memory, and trace.

State, dependencies, and risks: state is transient scan position plus function graph ret-stack index. Dependencies include the active unwinder, kallsyms, task stack helpers, ftrace graph tracing, and kernel text address validation. Stack scanning can produce false positives and unreliable callchains when unwind metadata is absent. Test signals are panic/oops readability, function-graph tracing interaction, and stacktrace self-tests if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/dumpstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/dwarf.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/dwarf.c

Purpose: implements a DWARF `.eh_frame` unwinder for SH stack traces, return-address lookup, and module unwind metadata.

Important APIs and control flow: slab/mempool caches allocate `dwarf_frame` and `dwarf_reg` structures. CIEs and FDEs are parsed from `.eh_frame` into rbtrees guarded by spinlocks. `dwarf_cfa_execute_insns()` interprets a subset of DWARF CFA opcodes to derive CFA and saved-register offsets. `dwarf_unwind_stack()` locates an FDE for the PC, executes CIE/FDE instructions, computes the CFA, reads the return address, and stops at unreliable interrupt returns. `module_dwarf_finalize()` and `module_dwarf_cleanup()` add/remove module CIE/FDE entries. `dwarf_unwinder_init()` parses kernel metadata, registers the unwinder, and marks it ready.

State, dependencies, and risks: persistent state includes CIE/FDE rbtrees, cached CIE, pools, and module lists. Dependencies include `.eh_frame` linker symbols, DWARF encoding conventions, ftrace graph return stacks, module ELF sections, and SH register-number mappings. Risks are high: unsupported encodings call `UNWINDER_BUG()`, DWARF64 and some `DWARF_VAL_OFFSET` behavior are called out as incomplete, compiler metadata can be inaccurate around interrupts, and parser/rbtree insertion defects can disable unwinding. Test signals are boot unwinder initialization counts, module load/unload with unwind info, oops stack depth, and function-graph tracer callchain correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/dwarf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/entry-common.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/entry-common.S

Purpose: low-level SH exception, IRQ return, syscall, debug-trap, fork-return, and user-work dispatch code.

Important APIs and control flow: `exception_error` delegates to `do_exception_error`. `ret_from_irq` tests saved SR to choose kernel or user resume. `resume_kernel` handles preemptive rescheduling when safe; `resume_userspace` checks thread flags for schedule, signals, notify-resume, and syscall trace exit. `__restore_all` restores register state through `restore_all`. `debug_trap` indexes `debug_trap_table` from TRA. `system_call` builds the pt_regs frame, decodes trap ranges, handles syscall tracing/seccomp/audit hooks through C helpers, bounds `r3` by `NR_syscalls`, dispatches through `sys_call_table`, stores return values, and exits through work checks.

State, dependencies, and risks: state is the exact pt_regs stack layout, TRA/syscall number convention, and thread flags. Dependencies include generated offsets, `sys_call_table`, ptrace/signal code, scheduler, IRQ tracing, and trap handlers. Any layout drift breaks ptrace, signal restore, kgdb, and syscall tracing. Test signals are syscall ABI tests, ptrace syscall rewrite, signal delivery after syscalls/IRQs, preemption under interrupt, and debug trap handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/entry-common.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/ftrace.c

Purpose: SH dynamic ftrace and function-graph tracing support, including runtime text patching of `_mcount` call sites.

Important APIs and control flow: dynamic ftrace builds replacement memory-table words through `ftrace_nop_replace()` and `ftrace_call_replace()`. `ftrace_modify_code()` reads existing text, verifies expected bytes, writes new bytes through an NMI-aware modification protocol, and flushes icache. `ftrace_make_nop()`, `ftrace_make_call()`, and `ftrace_update_ftrace_func()` patch call sites and the global ftrace call target. Function graph support patches `ftrace_graph_call` between `skip_trace` and `ftrace_graph_caller`, and `prepare_ftrace_return()` replaces a saved return address with `return_to_handler` while recording the real return address.

State, dependencies, and risks: state includes replacement buffers, `nmi_running` modification flag, patch target pointers, and per-task graph ret-stacks. Dependencies include stop-machine/ftrace core sequencing, NMI entry hooks, SH icache flushing, nofault kernel text access, and exception table fixups. Risks include text corruption if expected bytes do not match, NMI races, and graph tracing faults on bad return-address storage. Test signals are dynamic ftrace enable/disable, graph tracer recursion, NMI during patching, and syscall tracepoint registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/head_32.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/head_32.S

Purpose: SH 32-bit boot entry code and boot-parameter page definition.

Important APIs and control flow: `boot_params_page` encodes legacy boot ABI fields such as root flags, loader type, initrd start/size, and 29/32-bit marker. `_stext` initializes SR, stack/thread-info state, optional PMB mappings, BSS clearing, optional early FDT scan, CPU initialization, synchronization, and jumps to `start_kernel`. PMB setup validates bootloader mappings, installs cached/uncached mappings by descending size, clears remaining entries, and updates uncached mapping globals when configured. `stack_start` exports boot/secondary CPU startup data consumed by SMP bring-up.

State, dependencies, and risks: persistent state is early boot params, PMB hardware state, `stack_start`, and initialized BSS. Dependencies include linker symbols, `cpu_init`, `start_kernel`, MMU/PMB register definitions, optional FDT support, and SMP secondary path. Risks are unrecoverable boot hangs from bad SR/MMU/PMB setup, wrong BSS clearing for secondary CPUs, and stale bootloader mappings. Test signals are early boot on SH2/SH3/SH4 variants, SMP secondary startup, FDT boot, and uncached mapping validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/head_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/hw_breakpoint.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/hw_breakpoint.c

Purpose: adapts the SuperH UBC hardware breakpoint unit to Linux perf/hw_breakpoint and ptrace.

Important APIs and control flow: per-CPU `bp_per_reg[]` tracks perf events assigned to UBC channels. `arch_install_hw_breakpoint()` finds a free channel, enables the UBC clock, and programs hardware via `sh_ubc->enable()`. `arch_uninstall_hw_breakpoint()` disables the channel and clock. `hw_breakpoint_arch_parse()` maps generic length/type to SH encodings and enforces alignment. `hw_breakpoint_handler()` reads triggered channel masks, disables channels, calls `perf_bp_event()`, sends user `SIGTRAP` for user breakpoints, clears trigger bits, and re-enables active channels except ptrace one-shot events. `register_sh_ubc()` installs the platform UBC implementation.

State, dependencies, and risks: state includes global `sh_ubc`, per-CPU channel event arrays, UBC clock state, and ptrace breakpoints in task thread state. Dependencies include perf event core, die notifier trap flow, kprobes-safe handlers, `ptrace_triggered`, and platform UBC ops. Risks include channel exhaustion, clock imbalance, incorrect triggered masks, and ptrace one-shot semantics conflicting with perf watchpoints. Test signals are perf watchpoints, ptrace single-step/watchpoint, concurrent CPU breakpoints, and UBC registration on supported CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/hw_breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/idle.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/idle.c

Purpose: supplies SH architecture idle, CPU-dead idle, idle routine selection, and CPU stop helpers.

Important APIs and control flow: `default_idle()` sets the BL bit, enables interrupts, executes `cpu_sleep()`, disables interrupts, and clears BL. `arch_cpu_idle_dead()` delegates to `play_dead()`. `arch_cpu_idle()` calls the selected `sh_idle` routine and then `raw_local_irq_enable()`. `select_idle_routine()` chooses `default_idle` unless another implementation has been installed. `stop_this_cpu()` marks the CPU offline and sleeps forever with interrupts disabled.

State, dependencies, and risks: state is the global idle function pointer and per-CPU online state. Dependencies include BL bit helpers, CPU sleep instruction, SMP hotplug `play_dead()`, and scheduler idle loop expectations. Risks include races around interrupt enable during idle, BL bit misuse affecting exception masking, and stop paths that never return. Test signals are idle loop boot stability, CPU hotplug/offline, and interrupt wake from idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/io.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/io.c

Purpose: implements architecture-independent SH I/O memory copy and set helpers exported to drivers.

Important APIs and control flow: `memcpy_fromio()` copies from volatile I/O memory to RAM, using a SH4 optimized 32-byte aligned path with `movca.l` when possible, then aligned 32-bit and byte tails, followed by `mb()`. `memcpy_toio()` copies RAM to I/O with aligned longword and byte loops followed by `mb()`. `memset_io()` writes bytes with `writeb()`. All three are exported.

State, dependencies, and risks: no persistent state. Dependencies include SH memory barriers, volatile MMIO semantics, CPU_SH4 inline assembly, and driver I/O mapping conventions. Risks include alignment assumptions, missing endian/device ordering beyond the final barrier, and slow byte `memset_io()`. Test signals are driver MMIO copy correctness, unaligned lengths, SH4 optimized path coverage, and device register ordering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/io_trapped.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/io_trapped.c

Purpose: implements trapped I/O regions where accesses to specially mapped pages fault and are emulated against real I/O or memory resources.

Important APIs and control flow: `register_trapped_io()` validates page-aligned descriptors, checks that resources are all IO or all MEM, maps descriptor pages with `PAGE_NONE`, prints overrides, sets magic, and links into `trapped_io` or `trapped_mem`. `match_trapped_io_handler()` maps resource offsets to virtual trap pages. `lookup_tiop()` walks kernel page tables to identify the owning descriptor for a faulting address. `from_device()` and `to_device()` emulate reads/writes through `copy_word()` using minimum bus width. `handle_trapped_io()` rejects disabled/nonmatching/user faults, reads the faulting instruction, and invokes `handle_unaligned_access()` with custom memory accessors.

State, dependencies, and risks: persistent state is trapped descriptor lists, `trapped_lock`, magic fields, and the `noiotrap` boot option. Dependencies include VM page-table layout, unaligned access emulation, raw I/O accessors, resource flags, and optional I/O-port/IOMEM configs. Risks include fixed `TRAPPED_PAGES_MAX`, exact resource-start matching, page-table assumptions, and emulation bugs for unsupported instruction widths. Test signals are board drivers using trapped I/O, fault emulation on read/write widths, `noiotrap`, and invalid descriptor rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/io_trapped.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/ioport.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/ioport.c

Purpose: provides SH `ioport_map()` and `ioport_unmap()` support for port I/O users.

Important APIs and control flow: with `CONFIG_GENERIC_IOMAP`, `ioport_map()` maps port ranges through `ioremap()` and `ioport_unmap()` delegates to `iounmap()`. The file is intentionally small glue between generic I/O-port APIs and SH MMIO mapping.

State, dependencies, and risks: no persistent state. Dependencies include generic iomap configuration, `ioremap()`, and the architecture’s port-to-address convention. Risks are mostly platform mapping correctness and callers assuming x86-like I/O port semantics on SH. Test signals are PCI/legacy port drivers, map/unmap lifetime checks, and build coverage with and without generic iomap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/ioport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/irq.c

Purpose: implements SH IRQ entry glue, interrupt statistics, optional IRQ/softirq stacks, IRQ initialization, and hotplug IRQ migration.

Important APIs and control flow: `ack_bad_irq()` increments `irq_err_count`. `arch_show_interrupts()` prints NMI and ERR lines for `/proc/interrupts`. With IRQ stacks, `irq_ctx_init()` initializes per-CPU hard/soft IRQ thread-info stacks; `handle_one_irq()` switches to the hardirq stack before `generic_handle_irq()` unless already on it; `do_softirq_own_stack()` runs softirqs on their own stack. `do_IRQ()` sets irq regs, enters irq context, demuxes `irq_lookup()`, handles and finishes the IRQ, exits, and restores regs. `init_IRQ()` calls platform setup, machine-vector setup, `intc_finalize()`, and initializes CPU0 IRQ stacks.

State, dependencies, and risks: state includes `irq_err_count`, per-CPU IRQ stack arrays, platform/machine-vector IRQ demux hooks, and interrupt controller setup. Dependencies include generic IRQ core, SH INTC, softirq stack helpers, and CPU hotplug. Risks include stack switching assembly clobbers, demux returning ignored IRQs, affinity migration during hotplug, and missing stack init on secondary CPUs. Test signals are `/proc/interrupts`, nested interrupt load, softirq stress, hotplug migration, and bad-vector logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/irq_32.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/irq_32.c

Purpose: provides 32-bit SH compact IRQ flag save/restore helpers.

Important APIs and control flow: `arch_local_irq_restore()` writes the interrupt mask bits in SR. If passed `ARCH_IRQ_DISABLED`, it sets the IMASK bits with `or #0xf0`; otherwise it clears the disabled mask and, on CPUs with banked SR RB support, merges the saved `r6_bank` value before loading SR. `arch_local_save_flags()` reads SR and returns only the IMASK bits. Both helpers are marked `notrace` and exported for low-level users.

State, dependencies, and risks: state is the processor SR interrupt mask and optional banked register context. Dependencies include `ARCH_IRQ_DISABLED`, `CONFIG_CPU_HAS_SR_RB`, inline assembly constraints, and Linux irqflags semantics. Risks are severe because incorrect SR restoration can leave interrupts permanently masked or restore the wrong bank bit. Test signals are irqflags tracing-free builds, nested local_irq_save/restore behavior, interrupt enable/disable stress, and CPU variants with/without SR.RB banking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/irq_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/kdebugfs.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/kdebugfs.c

Purpose: creates the architecture debugfs root directory for SH.

Important APIs and control flow: global `arch_debugfs_dir` is exported for other SH code to place debugfs entries under. `arch_kdebugfs_init()` calls `debugfs_create_dir("sh", NULL)` and stores the returned dentry. The initializer runs through `arch_initcall()`.

State, dependencies, and risks: persistent state is the exported `arch_debugfs_dir` pointer. Dependencies include debugfs availability and initcall ordering relative to users that create child entries. The code does not check for `ERR_PTR` or NULL, so child users must tolerate unavailable debugfs. Test signals are `/sys/kernel/debug/sh` presence when debugfs is mounted and module/built-in users successfully creating child files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/kdebugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/kgdb.c

Purpose: implements SuperH KGDB register access, breakpoint instruction definition, single-step emulation, and die-notifier integration.

Important APIs and control flow: branch opcode macros support `get_step_address()`, which computes where to plant a temporary trap for single-step. `do_single_step()` overwrites the next-flow instruction with `STEP_OPCODE`; `undo_single_step()` restores it. `dbg_reg_def[]`, `dbg_set_reg()`, and `dbg_get_reg()` map GDB registers to `pt_regs`, including VBR readback. `sleeping_thread_to_gdb_regs()` extracts saved thread state. `kgdb_arch_handle_exception()` handles continue/step/detach/kill packets and optional PC updates. `singlestep_trap_handler` adjusts PC and calls KGDB. A low-priority die notifier forwards breakpoints to KGDB.

State, dependencies, and risks: state includes global `stepped_address`/`stepped_opcode`, KGDB single-step flags, and die notifier registration. Dependencies include SH instruction encoding, icache flushes, trap table entry 0x3d/0x3c, and task register layout. Risks include global single-step state on SMP, delay-slot stepping limitations documented in comments, and unsafe instruction patching if address computation is wrong. Test signals are remote KGDB break/continue/step, sleeping thread register dumps, and delay-slot branch stepping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/kprobes.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/kprobes.c

Purpose: implements SH kprobes and kretprobes by patching trap instructions and planting temporary probes for single-step simulation.

Important APIs and control flow: `arch_prepare_kprobe()` rejects `rte`, copies original instructions, and records opcode. `arch_arm_kprobe()`/`arch_disarm_kprobe()` write or restore `BREAKPOINT_INSTRUCTION` and flush icache. `prepare_singlestep()` disarms the current probe and arms one or two per-CPU temporary probes at the next possible flow targets, handling jumps, branches, returns, and conditional delay-slot forms. `kprobe_handler()` manages active/reentered probes and pre-handlers. `post_kprobe_handler()` restores temporary probes and calls post-handlers. `kprobe_fault_handler()` rewinds or fixups faults. `kprobe_exceptions_notify()` consumes trap die notifications, and `arch_init_kprobes()` registers the kretprobe trampoline probe.

State, dependencies, and risks: per-CPU state includes current probe, control block, and saved current/next opcodes. Dependencies include die notifier flow, exception tables, SH opcode decoding, icache flush, and kretprobe core. Risks include conditional branch displacement sign handling, probes in delay slots, recursion status bugs, and stale temporary probes. Test signals are kprobes/kretprobes on simple functions, branch/delay-slot probes, faulting probed instructions, and concurrent probes on SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/machine_kexec.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/machine_kexec.c

Purpose: implements SH architecture kexec transition, kexec jump context preservation, and crashkernel memory reservation.

Important APIs and control flow: `machine_kexec()` converts generic kexec indirection entries from physical to virtual, optionally saves processor state for kexec jump, disables ftrace and interrupts, copies `relocate_new_kernel` to the control page, prints segment info, flushes caches, reloads BIOS VBR, and jumps to relocation code with page list/control page/start address. On kexec jump return it restores VBR, processor state, page-list physical addresses, and ftrace state. `reserve_crashkernel()` parses `crashkernel=`, reserves or allocates memory through memblock, disables conflicting `memory_limit`, and fills `crashk_res`.

State, dependencies, and risks: state includes transformed `image->head`, control code page contents, ftrace enabled state, crashkernel resource, and memory limit. Dependencies include `relocate_kernel.S`, memblock, cache flushes, BIOS VBR reload, suspend processor state helpers, and generic kexec image format. Risks include no-op SMP crash shutdown, page-list conversion mistakes, irreversible interrupts-off transition, and crashkernel reservation conflicts. Test signals are regular kexec, kexec jump return, crashkernel reservation logs, and `/proc/vmcore` after crash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/machine_kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/machvec.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/machvec.c

Purpose: selects and finalizes the SH machine vector used for board-specific operations.

Important APIs and control flow: `get_mv_byname()` scans the linker-provided `__machvec_start` to `__machvec_end` section. `early_parse_mv()` parses `sh_mv=`, copies the named vector into global `sh_mv`, or panics if unknown. `sh_mv_setup()` selects the first vector when none was specified, validates section alignment, prints the booting vector, and fills missing hooks such as `irq_demux`, `mode_pins`, and `mem_init` with generic implementations.

State, dependencies, and risks: global `sh_mv` is the central persistent state and is exported. Dependencies include linker sections, early command-line parsing, generic machine-vector functions, and setup/IRQ/memory users. Risks include malformed machvec sections, wrong command-line name, missing hooks hidden by generic fallback, and early lifetime of `__initmv` data. Test signals are boot logs showing expected machvec, command-line override, board IRQ/mode-pin behavior, and panic on bad vector names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/machvec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/module.c

Purpose: applies SH ELF relocations for loadable modules and connects module DWARF unwind metadata.

Important APIs and control flow: `apply_relocate_add()` iterates `Elf32_Rela` entries, resolves each symbol plus addend, and updates target locations for `R_SH_DIR32`, `R_SH_REL32`, and SHmedia immediate relocation forms. Unknown relocations print an error and return `-ENOEXEC`. `module_finalize()` calls `module_dwarf_finalize()`, and `module_arch_cleanup()` removes module unwind metadata through `module_dwarf_cleanup()`.

State, dependencies, and risks: state is modified module text/data and module-owned CIE/FDE lists. Dependencies include ELF32 relocation definitions, unaligned access helpers, module loader, and DWARF unwinder. Risks include unsupported relocation types, immediate field masking mistakes, no icache flush in this file after relocation, and module unwind parser failures blocking load. Test signals are module insertion with each relocation type, unknown relocation rejection, and module unload cleaning unwind entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/nmi_debug.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/nmi_debug.c

Purpose: provides boot-time configurable NMI diagnostics through the die notifier chain.

Important APIs and control flow: `nmi_debug_setup()` registers a notifier and parses `nmi_debug=` comma options: `state`, `regs`, `debounce`, and `die`. `nmi_debug_notify()` handles `DIE_NMI` by optionally calling `show_state()`, `show_regs()`, delaying 10 ms, and returning `NOTIFY_BAD` to force fatal behavior when requested.

State, dependencies, and risks: state is the `nmi_actions` bitmask and registered notifier. Dependencies include die notifier ordering, NMI trap handling, scheduler state dump, and `show_regs()`. Risks include unsafe work in NMI context, debounce delays during critical faults, and notifier side effects when enabled without actions. Test signals are boot-parameter parsing, synthetic/platform NMI, and verifying requested state/regs/die behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/nmi_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/perf_callchain.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/perf_callchain.c

Purpose: records SH kernel perf callchains.

Important APIs and control flow: `callchain_address()` stores only reliable addresses into the perf callchain entry. `perf_callchain_kernel()` records the interrupted PC, then calls `unwind_stack()` with callchain callbacks to append reliable frames.

State, dependencies, and risks: state is the perf callchain entry supplied by the perf core. Dependencies include `pt_regs`, active SH unwinder, and reliability classification. Risks are shallow callchains when the DWARF unwinder is unavailable or marks frames unreliable. Test signals are `perf record -g` kernel callchains, function-graph tracer interaction, and oops/unwinder reliability comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/perf_callchain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/perf_event.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/perf_event.c

Purpose: adapts SH hardware performance counters to Linux perf PMU operations.

Important APIs and control flow: per-CPU `cpu_hw_events` tracks assigned events and used/active masks. `__hw_perf_event_init()` reserves PMU hardware for the first event, maps raw/cache/generic hardware events through `sh_pmu`, sets `event->destroy`, and stores hardware config. `sh_perf_event_update()` reads a raw counter, atomically swaps `prev_count`, computes delta, and adds to perf count. PMU ops add/delete/start/stop/read events, manipulating per-CPU slots and `sh_pmu` enable/disable callbacks. `register_sh_pmu()` installs a platform PMU, marks no-interrupt capability, registers `"cpu"` PMU, and sets a CPU hotplug prepare state.

State, dependencies, and risks: state includes global `sh_pmu`, `num_events`, reservation mutex, and per-CPU masks/events. Dependencies include platform `struct sh_pmu` callbacks/event maps, perf core, CPU hotplug, and hardware counters without overflow interrupts. Risks include sampling limitations, counter wrap width assumptions (`shift` remains zero), event slot conflicts, and incomplete reserve/release stubs. Test signals are `perf stat` raw/hardware/cache events, CPU hotplug reset, concurrent events up to `MAX_HWEVENTS`, and no sampling expectation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/process.c

Purpose: manages architecture task state allocation, FPU/xstate lifetime, and stack protector state.

Important APIs and control flow: `arch_dup_task_struct()` forces lazy FPU state to memory, copies the task struct, and deep-copies `thread.xstate` when present. `free_thread_xstate()` and `arch_release_task_struct()` free per-task FPU/emulation state. `arch_task_cache_init()` creates the `task_xstate` cache when `xstate_size` is nonzero. `init_thread_xstate()` chooses hard FPU, software FPU, or no xstate size based on CPU flags and config. Stack protector guard is exported for non-SMP/global use when configured.

State, dependencies, and risks: persistent state includes `task_xstate_cachep`, `xstate_size`, and optional `__stack_chk_guard`. Dependencies include SH FPU helpers, boot CPU feature detection, slab caches, and task lifecycle hooks. Risks include shallow-copy hazards if xstate allocation fails after task copy, incorrect xstate size for CPU/emulator combination, and stale lazy FPU state. Test signals are fork/clone with FPU state, task exit cleanup, software-FPU builds, and stackprotector boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/process_32.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/process_32.c

Purpose: implements 32-bit SH process register display, user/thread startup, clone setup, context switching, and wait-channel lookup.

Important APIs and control flow: `show_regs()` prints PC/PR/SR/SP, MMU TEA, GPRs, MAC/GBR registers, trace, and decoded code. `start_thread()` initializes user PC/SP/SR/PR and frees old xstate. `flush_thread()` clears ptrace hardware breakpoints and lazy FPU state. `copy_thread()` builds kernel-thread or user-child `pt_regs`, handles DSP copy, TLS in GBR, child return value zero, and fork return trampolines. `__switch_to()` saves previous lazy FPU, restores banked kernel thread-info register, optionally prefetches/restores hot FPU state, and updates stack canary on non-SMP. `__get_wchan()` reports saved PC or frame-pointer-derived scheduler caller.

State, dependencies, and risks: state includes thread registers, ptrace breakpoint array, DSP/FPU state, banked r7, and per-task stack canary. Dependencies include entry trampolines, FPU/DSP helpers, frame-pointer layout, MMU context, and SH switch assembly. Risks include register layout coupling with `entry-common.S`, clone TLS ABI in GBR, and FPU lazy restore heuristics. Test signals are fork/clone/kernel_thread, exec user register setup, ptrace hardware breakpoint cleanup, and context-switch FPU preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/process_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/ptrace.c

Purpose: provides generic SH helpers for mapping register names to `struct pt_regs` offsets and back.

Important APIs and control flow: `regs_query_register_offset()` linearly searches `regoffset_table` for a name and returns the offset or `-EINVAL`. `regs_query_register_name()` searches for an offset and returns the name or `NULL`.

State, dependencies, and risks: state is the `regoffset_table` defined in the 32-bit ptrace implementation. Dependencies include exact `pt_regs` field offsets and Linux register query APIs used by tracing/kprobes/perf tooling. Risks are stale table entries when `pt_regs` changes and linear lookup cost is trivial but unindexed. Test signals are kprobe/ftrace register-name queries and ptrace/debugger register offset validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/ptrace_32.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/ptrace_32.c

Purpose: implements 32-bit SH ptrace, user regsets, hardware single-step via UBC, and syscall trace hooks.

Important APIs and control flow: stack helpers read/write child `pt_regs`. `ptrace_triggered()` disables one-shot ptrace breakpoints. `set_single_step()`, `user_enable_single_step()`, and `user_disable_single_step()` use a UBC breakpoint on the child PC to implement single-step. General, FPU, and DSP regset callbacks expose `pt_regs`, xstate, and DSP state. `arch_ptrace()` handles legacy PEEK/POKEUSR, register get/set requests, FPU/DSP requests, and delegates unknown operations to `ptrace_request()`. `do_syscall_trace_enter()` runs ptrace entry, seccomp, tracepoint, and audit entry logic; `do_syscall_trace_leave()` runs audit, tracepoint exit, and ptrace syscall-exit/step reporting.

State, dependencies, and risks: state includes child thread ptrace breakpoints, xstate used-math flags, regset view metadata, and syscall trace flags. Dependencies include `entry-common.S` syscall frame layout, perf/hw_breakpoint, audit, seccomp, trace events, FPU/DSP helpers, and `struct user` ABI offsets. Risks include unrestricted POKEUSR corruption of sensitive saved registers, single-step depending on UBC availability, and ABI breakage if `pt_regs` changes. Test signals are gdb ptrace register access, syscall tracing/rewrite, seccomp deny, FPU regsets, and single-step over syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/ptrace_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/reboot.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/reboot.c

Purpose: supplies SH machine poweroff, restart, halt, shutdown, and crash-shutdown dispatch.

Important APIs and control flow: `machine_ops` defaults to native handlers. Restart disables interrupts, globally flushes TLBs, tries an address-error reset path, then triggers the watchdog and sleeps forever if reset fails. Shutdown stops other CPUs. Poweroff calls `do_kernel_power_off()`. Halt shuts down then stops the current CPU. Public `machine_power_off()`, `machine_shutdown()`, `machine_restart()`, `machine_halt()`, and optional `machine_crash_shutdown()` delegate through `machine_ops`.

State, dependencies, and risks: state includes exported `pm_power_off` and mutable `machine_ops`. Dependencies include watchdog registers, TLB flush, trap reset trigger, SMP stop, kernel poweroff core, and optional kexec crash shutdown. Risks are platform reset methods that hang, machine_ops override mistakes, and crash shutdown doing too little on SMP unless platform code supplies more. Test signals are reboot/poweroff/halt on boards, watchdog reset fallback, and kexec crash path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/relocate_kernel.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/relocate_kernel.S

Purpose: assembly relocation engine copied to the kexec control page to move/swap pages and branch to a new kernel.

Important APIs and control flow: `relocate_new_kernel` saves caller, special, and banked registers onto a control-page stack; calls `swap_pages`; stores stack pointer; jumps to the new kernel start; and, for kexec jump return, restores pages and all saved registers. `swap_pages` walks the generic kexec indirection list, tracks destination/indirection/source commands, and swaps 16-byte chunks for each page so both normal kexec and kexec jump use one mechanism. `relocate_new_kernel_size` exports the copy size.

State, dependencies, and risks: state is the control-page stack, indirection list, and page contents being swapped. Dependencies include generic kexec indirection flag encoding, `PAGE_SIZE`, banked-register bit, and `machine_kexec()` address conversion. Risks are catastrophic if page-list commands are malformed, bank selection is not restored, or source/destination overlap assumptions fail. Test signals are kexec boot, kexec jump round-trip, register preservation checks, and large multi-segment images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/relocate_kernel.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/return_address.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/return_address.c

Purpose: implements `return_address()` for SH when the DWARF unwinder is available.

Important APIs and control flow: `return_address(depth)` repeatedly calls `dwarf_unwind_stack()` up to the requested depth, frees the previous frame each iteration, stops when no frame or return address exists, frees the final frame, and returns the resolved return address as a pointer. The symbol is exported GPL.

State, dependencies, and risks: state is transient DWARF frame allocations. Dependencies include DWARF unwinder readiness and frame reliability; without `CONFIG_DWARF_UNWINDER` the implementation is absent. Risks include returning NULL for assembly/unwinder gaps and relying on interrupt/ftrace graph handling in `dwarf.c`. Test signals are callers such as tracing/debug helpers requesting shallow/deep return addresses and behavior with/without DWARF unwinder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/return_address.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/setup.c

Purpose: performs SH architecture boot setup: CPU/machine globals, command line, initrd, memory resources, FDT, paging, machine vector, platform setup, and CPU identity finalization.

Important APIs and control flow: global `cpu_data`, `sh_mv`, memory bounds, cache-shape variables, and resources are initialized/exported. `early_parse_mem()` sets `memory_limit`. `check_for_initrd()` validates boot ABI initrd fields, reserves memblock space, and sets `ROOT_DEV`. `calibrate_delay()` derives LPJ from `cpu_clk` when generic calibration is absent. `__add_active_range()` registers RAM resources, reserves kernel/crash ranges, bolts PMB mapping, and assigns memblock NUMA node. `sh_fdt_init()` scans early FDT once. `setup_arch()` enables MMU, decodes boot params, builds command line, parses early params, runs platform/machvec/earlyprintk/FDT/paging setup, calls machine setup, and initializes SMP. `arch_cpu_finalize_init()` selects idle, records LPJ, updates `utsname()->machine`, and prints CPU subtype.

State, dependencies, and risks: persistent state includes boot command lines, memory resources, memblock reservations, CPU data, machine vector, root/initrd fields, and UTS machine string. Dependencies include boot ABI macros, memblock, PMB, clock framework, FDT, machine vectors, paging, SMP, and early platform drivers. Risks include invalid initrd disabling, memory-limit/crashkernel interaction, missing CPU clock panic, and early command-line overwrite/extend behavior. Test signals are boot logs, `/proc/iomem`, initrd boot, `mem=`, FDT boot, crashkernel reservation, and machine string correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/sh_bios.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/sh_bios.c

Purpose: exposes C helpers and optional early console support for trapping into the standard LinuxSH BIOS/GDB vector.

Important APIs and control flow: `sh_bios_call()` loads function and arguments into SH registers and executes `trapa #0x3f` if `gdb_vbr_vector` is known. Helpers wrap console write, GDB detach, Ethernet node address, and shutdown BIOS calls. `sh_bios_vbr_init()` reads the old VBR and records the BIOS trap vector at `vbr + 0x100`; `sh_bios_vbr_reload()` restores VBR from that vector, used around kexec/restore paths. With early printk, a `bios` console writes through BIOS calls and `earlyprintk=bios[,keep]` registers it.

State, dependencies, and risks: state is global `gdb_vbr_vector` and optional `early_console`. Dependencies include debug trap table entry 0x3f, BIOS calling convention, VBR register access, console core, and kexec VBR reload. Risks include trapping when firmware is absent, bogus BIOS cflags, VBR restoration conflicts, and early console lifetime. Test signals are `earlyprintk=bios`, BIOS node address users, KGDB detach through BIOS, and kexec with BIOS VBR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/sh_bios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/sh_ksyms_32.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/sh_ksyms_32.c

Purpose: exports 32-bit SH low-level symbols needed by modules.

Important APIs and control flow: the file exports common memory/string routines, user copy/clear helpers, delay routines, checksumming, page copy, flatmem PFN bounds, and compiler/libgcc arithmetic helper symbols declared through `DECLARE_EXPORT()`.

State, dependencies, and risks: no runtime state beyond the module symbol table. Dependencies are assembly/compiler helper implementations elsewhere and module ABI expectations. Risks include missing exports causing module link failures, over-exporting internal helpers, or config-dependent PFN symbol availability. Test signals are building/loading modules that use memcpy/checksum/delay/division helpers and modpost unresolved-symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/sh_ksyms_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/signal_32.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/signal_32.c

Purpose: implements 32-bit SH signal frame setup, signal return, syscall restart, altstack, FPU state save/restore, and user-mode notification.

Important APIs and control flow: `restore_sigcontext()` restores GPRs, GBR/MAC/PR/SR/PC, preserves kernel SR bits, restores optional FPU state, disables syscall restart checks, and returns saved r0. `sys_sigreturn()` and `sys_rt_sigreturn()` validate user frames, restore signal masks, context, and altstack, or force SIGSEGV on bad frames. `setup_sigcontext()` writes register/FPU state to user frames. `get_sigframe()` selects normal or altstack and adds `UNWINDGUARD`. `setup_frame()` and `setup_rt_frame()` copy siginfo/ucontext, choose SA_RESTORER, VDSO, or generated trampoline code, flush trampoline icache, and set handler args/PC/PR including FDPIC descriptors. `do_signal()` handles syscall restart rules and signal delivery; `do_notify_resume()` dispatches signal and resume-user-mode work.

State, dependencies, and risks: state is user stack frames, blocked masks, restart block, FPU/xstate, and pt_regs. Dependencies include entry work flags, VDSO symbols, FPU helpers, FDPIC ABI, signal core, altstack, and SH instruction size decoding. Risks include user-frame ABI breakage, generated trampoline cache coherency, syscall PC rewind errors, and FPU ownership mistakes. Test signals are POSIX signal/rt-signal tests, altstack, SA_RESTORER/VDSO fallback, syscall restart, FDPIC handler calls, and bad-frame SIGSEGV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/signal_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/smp.c

Purpose: implements SuperH SMP boot, CPU hotplug, IPI dispatch, and SMP TLB shootdowns.

Important APIs and control flow: `register_smp_ops()` installs platform SMP operations. Boot prep initializes MM context and calls `mp_ops->prepare_cpus()`. `smp_prepare_boot_cpu()` maps logical/physical CPU0 and marks it online/possible. Hotplug paths disable CPUs, migrate IRQs, flush cache/TLB, clear mm CPU masks, and mark dead state. `start_secondary()` enables MMU, attaches `init_mm`, initializes traps, notifies CPU start, calibrates delay, stores CPU info, marks online, and enters idle. `__cpu_up()` patches `stack_start`, flushes icache, calls `mp_ops->start_cpu()`, and waits for online. IPI helpers send reschedule, call-function, single-call, and timer messages; `smp_message_recv()` dispatches them. MMU TLB flush functions use local flushes, context invalidation, or synchronous IPIs based on mm sharing.

State, dependencies, and risks: state includes CPU maps, `mp_ops`, per-CPU `cpu_state`, `cpu_data`, `stack_start`, and mm context ASIDs. Dependencies include platform SMP ops, head startup code, IRQ migration, clockevents broadcast, cache/TLB local primitives, and generic SMP call functions. Risks include start timeout, missing `mp_ops`, CPU0 hotplug prohibition, TLB shootdown races, and stack_start shared data requiring icache/wmb ordering. Test signals are SMP boot, CPU hotplug, IPI stress, TLB shootdown under multithreaded mmap/munmap, and clockevent broadcast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/stacktrace.c

Purpose: implements SH `save_stack_trace()` APIs using the architecture unwinder.

Important APIs and control flow: `save_stack_address()` stores only reliable addresses, honors `trace->skip`, and stops at `max_entries`. `save_stack_trace()` skips itself, unwinds the current task, and appends `ULONG_MAX` if space remains. `save_stack_trace_tsk()` handles current and other tasks, selects saved SP for blocked tasks, unwinds, and also appends `ULONG_MAX`.

State, dependencies, and risks: state is the caller-provided `struct stack_trace`. Dependencies include `unwind_stack()`, task stack access, pt_regs for current tasks, and reliable-frame tagging. Risks are incomplete traces when the unwinder is unavailable/unreliable and stale saved SP for running remote tasks. Test signals are stacktrace API users, lockdep/debug objects, and comparing traces from current versus sleeping tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/swsusp.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/swsusp.c

Purpose: supplies SH hibernation architecture hooks.

Important APIs and control flow: global `swsusp_arch_regs_cpu0` stores CPU0 suspend registers. `pfn_is_nosave()` excludes the `__nosave` section from hibernation images. `save_processor_state()` initializes/saves current FPU state, and `restore_processor_state()` flushes all local TLB entries after resume.

State, dependencies, and risks: state includes saved arch registers, nosave linker section bounds, FPU state, and TLB contents. Dependencies include hibernation core, linker sections, SH FPU helpers, and TLB flush primitives. Risks include missing CPU state beyond FPU/TLB, SMP limitations, and incorrect nosave PFN calculation. Test signals are suspend-to-disk/resume, FPU-using workload across hibernate, and memory image excluding nosave pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/swsusp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/sys_sh.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/sys_sh.c

Purpose: implements SH-specific syscall wrappers with nonstandard ABI details.

Important APIs and control flow: `old_mmap()` validates page-aligned byte offset and delegates to `ksys_mmap_pgoff()`. `sys_mmap2()` delegates using page-offset units. `sys_cacheflush()` validates the requested range with `access_ok()` and calls `cacheflush_user_range()` for user-visible cache maintenance.

State, dependencies, and risks: no persistent state. Dependencies include syscall table entries, user access validation, mmap core, SH cacheflush operations, and cachectl ABI constants. Risks include offset overflow/ABI compatibility, user range validation gaps, and cacheflush semantics expected by JIT/self-modifying code. Test signals are mmap/mmap2 ABI tests, invalid offset/range errors, and user cacheflush correctness for generated code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/sys_sh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/sys_sh32.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/sys_sh32.c

Purpose: provides 32-bit SH syscall wrappers for ABI return/register conventions and split 64-bit arguments.

Important APIs and control flow: `sys_sh_pipe()` calls `do_pipe_flags()`, returns the first fd in r0 and writes the second fd to saved r1. `sys_pread_wrapper()` and `sys_pwrite_wrapper()` reconstruct 64-bit file offsets from split 32-bit registers and call `ksys_pread64()`/`ksys_pwrite64()`. `sys_fadvise64_64_wrapper()` reconstructs split offset and length arguments for `ksys_fadvise64_64()`.

State, dependencies, and risks: state is only the current syscall `pt_regs` return registers. Dependencies include 32-bit syscall argument ordering, VFS helpers, and entry code preserving r1. Risks include wrong high/low word ordering and pipe ABI compatibility. Test signals are libc pipe convention, pread/pwrite/fadvise with offsets above 4 GiB, and syscall table argument ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/sys_sh32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/syscalls/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/syscalls/Makefile

Purpose: generates SH syscall number and syscall table headers from `syscall.tbl`.

Important APIs and control flow: it defines generated UAPI and kernel include directories, creates them with `$(shell mkdir -p ...)`, points to `scripts/syscallhdr.sh` and `scripts/syscalltbl.sh`, and defines `if_changed` rules for `unistd_32.h` and `syscall_table.h`. `uapisyshdr-y`, `kapisyshdr-y`, and `targets` register generated files with kbuild, and `all` depends on both generated headers.

State, dependencies, and risks: persistent build outputs are `arch/$(SRCARCH)/include/generated/uapi/asm/unistd_32.h` and `arch/$(SRCARCH)/include/generated/asm/syscall_table.h`. Dependencies include `syscall.tbl`, kbuild `if_changed`, shell config, and generic syscall generation scripts. Risks include stale generated headers if dependencies are wrong and source-tree path prefix mistakes. Test signals are clean builds, syscall table regeneration after `syscall.tbl` edits, and generated `NR_syscalls` matching `entry-common.S`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/syscalls_32.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/syscalls_32.S

Purpose: emits the 32-bit SH syscall dispatch table.

Important APIs and control flow: `__SYSCALL(nr, entry)` expands to a `.long entry`; `sys_call_table` includes generated `<asm/syscall_table.h>` in `.data`, so table contents are generated from `syscall.tbl`.

State, dependencies, and risks: persistent state is the linker-visible `sys_call_table` consumed by `entry-common.S`. Dependencies include generated syscall table header, syscall symbols, and `NR_syscalls`. Risks are table/header mismatch, missing syscall symbol references, and data-section placement assumptions. Test signals are boot syscall dispatch, invalid syscall returning `-ENOSYS`, and kbuild regeneration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/syscalls_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/time.c

Purpose: initializes SH clocksource/clockevent infrastructure and late earlytimer probing.

Important APIs and control flow: `time_init()` calls generic `timer_probe()`, initializes SH clocks with `clk_init()`, and assigns `late_time_init` to `sh_late_time_init()`. The late function registers all `earlytimer` platform drivers and probes two devices, allowing clockevent and clocksource devices to appear while tolerating a missing clocksource by falling back to jiffies.

State, dependencies, and risks: state includes clock framework registration and the `late_time_init` callback pointer. Dependencies include early platform driver infrastructure, SH clock code, RTC/timex integration, and generic timer probing. Risks include timer init ordering, only probing two earlytimers, and clocksource fallback hiding platform timer failures. Test signals are boot timer logs, clocksource selection, tick delivery, and earlytimer driver probe counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/topology.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/topology.c

Purpose: registers SH CPU topology devices and core-sibling masks.

Important APIs and control flow: per-CPU `cpu_devices` backs sysfs CPU devices. `cpu_coregroup_map()` currently returns all possible CPUs for simple SH-X3-style multicore topology. `cpu_coregroup_mask()` returns `cpu_core_map[cpu]`. `arch_update_cpu_topology()` recomputes core maps. `topology_init()` registers one CPU device per possible CPU, sets core maps, and runs as a `subsys_initcall`.

State, dependencies, and risks: state includes per-CPU `struct cpu` devices and exported `cpu_core_map`. Dependencies include cpu masks, device registration, topology core, and CPU possible map. Risks include oversimplified topology for heterogeneous/non-SH-X3 systems and stale masks after hotplug if updates are incomplete. Test signals are `/sys/devices/system/cpu` topology files, CPU hotplug, and scheduler topology behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/traps.c

Purpose: implements SH die/oops handling and trap handlers for debug, BUG, and NMI events.

Important APIs and control flow: `die()` serializes with `die_lock`, enters oops state, prints error/module/register information, notifies die notifiers, runs crash_kexec, updates taint and oops state, and exits or panics as appropriate. `die_if_kernel()` and `die_if_no_fixup()` convert kernel faults without fixups into fatal oopses. `handle_BUG()` decodes BUG table entries, reports warnings or BUGs, advances PC past the trap, and signals handled status. `is_valid_bugaddr()` validates trap instruction addresses. `debug_trap_handler`, `bug_trap_handler`, and `nmi_trap_handler` are generated by `BUILD_TRAP_HANDLER` and feed the notifier/oops paths.

State, dependencies, and risks: state includes `die_lock`, static die counter, taint/oops global state, exception tables, BUG table metadata, and notifier side effects. Dependencies include trap entry macros, `debugtraps.S`, kexec crash handling, module printing, unwinder, and signal delivery. Risks include recursive oops handling, notifier ordering conflicts with kgdb/kprobes/hw-breakpoint/NMI debug, and wrong PC advance after BUG. Test signals are WARN/BUG traps, kgdb/kprobe coexistence, crash_kexec on panic, and invalid bug address handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/traps.c -->
