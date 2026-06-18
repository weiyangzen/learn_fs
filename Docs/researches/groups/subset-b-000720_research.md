# Research: subset-b-000720

Grouped research for `subset-b-000720`. Each section preserves the source path in its title and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cache.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cache.c

Purpose: implements MicroBlaze cache enable/disable, invalidate, and flush operations selected at boot from the probed/static CPU description. It provides the `mbc` `struct scache` dispatch table consumed by cacheflush helpers, then `microblaze_cache_init()` binds it to write-back/write-through and MSR-instruction/no-MSR variants.

Important APIs and state: low-level inline MSR helpers toggle `MSR_ICE` and `MSR_DCE`; cache loops issue `wic`, `wdc`, `wdc.flush`, and `wdc.clear`; `mbc` is exported through `microblaze_ksyms.c`. The implementation depends on `cpuinfo` sizes, line lengths, `dcache_wb`, `ver_code`, and `PVR2_USE_MSR_INSTR`.

Control flow: range helpers align/limit addresses to one cache footprint, optionally disable interrupts/cache for older write-through paths, loop by cache line, then restore cache/MSR state. Whole-cache helpers sweep `cpuinfo.*cache_size`. `microblaze_cache_init()` chooses one of six static `scache` tables, warns about old write-back hardware, enables dcache, invalidates icache, and enables icache.

State and persistence: persistent state is the global `mbc` function table plus CPU MSR cache bits. No dynamic allocation occurs. Cache operations have hardware-visible side effects and must preserve interrupt and virtual-mode assumptions.

Dependencies and integration: used by DMA, module finalization, ftrace patching, signal trampolines, kgdb, and coherent allocation paths. It relies on correct PVR/DTS data from the CPU-info files.

Risks and test signals: wrong line size or cache mode can lose dirty data or leave stale instructions after text patching. Old write-through paths intentionally disable cache/IRQs. Build and boot with MSR/non-MSR, write-back/write-through configurations; exercise module loading, dynamic ftrace, signal return trampolines, DMA sync, and cache debug prints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo-pvr-full.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo-pvr-full.c

Purpose: overlays full Processor Version Register data onto the architecture `struct cpuinfo`, using DTS/static data as the initial baseline and warning when hardware and device-tree expectations differ.

Important APIs and state: `set_cpuinfo_pvr_full(struct cpuinfo *ci, struct device_node *cpu)` reads all PVR registers via `get_pvr()`. The `CI()` macro copies individual PVR fields into `ci`; `err_printk()` records mismatches for instruction, multiplier/FPU, and write-back cache policy groups.

Control flow: the function first checks `PVR_VERSION`; a zero version is treated as broken PVR and leaves DTS data in place. It then fills instruction, multiply, FPU, exception, cache, bus, FSL, interrupt polarity, debug-breakpoint, user, MMU, endian, and FPGA family fields. Cache line length is converted from PVR words to bytes with `<< 2`.

State and persistence: it mutates only the boot-time global `cpuinfo` instance supplied by caller. That state persists for cache setup, `/proc/cpuinfo`, timers, MMU setup, and debug code.

Dependencies and integration: depends on `asm/pvr.h` extractor macros and `pvr.c`. Called from `setup_cpuinfo()` only when PVR support indicates full CPU PVR use.

Risks and test signals: the mismatch warnings are diagnostic only, so bad DTS can still boot with hardware-derived fields. A broken or partial PVR can poison cache parameters. Test by booting systems with known PVR values, checking `/proc/cpuinfo`, cache line sizes, and mismatch logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo-pvr-full.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo-static.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo-static.c

Purpose: builds `struct cpuinfo` from device-tree properties and Kconfig constants when PVR is missing or as the baseline before full-PVR correction.

Important APIs and state: `set_cpuinfo_static()` consumes `xlnx,*` CPU properties through `fcpu()`, compares selected values with `CONFIG_XILINX_MICROBLAZE0_*`, and maps version/family strings through `cpu_ver_lookup` and `family_string_lookup`.

Control flow: instruction, multiply, FPU, exception, cache, bus, FSL, IRQ, debug, user PVR, MMU, and endian fields are filled from DTS. Missing cache line properties are defaulted using legacy FSL-cache hints. Version and FPGA-family codes are derived from compile-time strings, and a MicroBlaze 3/non-Spartan2 fixup forces hardware multiplier information.

State and persistence: only the supplied `cpuinfo` is updated; there is no allocation. The populated values persist as the architecture-wide hardware contract for cache, exception, clock, and procfs code.

Dependencies and integration: called by `setup_cpuinfo()` for no-PVR and unsupported-PVR cases, and before `set_cpuinfo_pvr_full()` for full-PVR systems. Depends on DTS property naming and Kconfig matching the bitstream.

Risks and test signals: stale DTS or kernel config can select invalid cache/TLB behavior. Missing cache-line properties fall back heuristically. Test with DTBs for old and new MicroBlaze IP, verifying mismatch logs and `/proc/cpuinfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo-static.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo.c

Purpose: owns the global MicroBlaze CPU description, version/family lookup tables, CPU information setup, clock setup, and `/proc/cpuinfo` seq operations.

Important APIs and state: global `struct cpuinfo cpuinfo`; `setup_cpuinfo()` discovers the CPU node and chooses static/full-PVR population; `setup_cpuinfo_clk()` reads the CPU clock via CCF or `timebase-frequency`; `cpuinfo_op` prints hardware capabilities. Lookup tables translate MicroBlaze hardware-version and FPGA-family strings to numeric codes.

Control flow: setup chooses no-PVR, full-PVR, or fallback handling, warns if stream instructions are unprivileged, and releases the CPU OF node. Clock setup must run while `cpu` is still valid and BUGs if no frequency is found. `/proc/cpuinfo` iterates up to `NR_CPUS` but prints global single-CPU data.

State and persistence: `cpuinfo` persists for the lifetime of the kernel. The static `cpu` pointer is retained between CPU info and clock setup. No runtime mutation is expected after boot.

Dependencies and integration: used by setup, cache init, timer fallback, kgdb PVR export, and procfs. Depends on OF CPU nodes and optional clock provider.

Risks and test signals: the `cpu_has_pvr()` return semantics are subtle; comments and switch labels can be confusing. Missing CPU clock causes BUG. Test boot logs, `/proc/cpuinfo`, clock fallback, and systems with no/full/unsupported PVR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/mb.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/mb.c

Purpose: implements `/proc/cpuinfo` display for MicroBlaze by formatting the global `cpuinfo` hardware description into kernel seq-file output.

Important APIs and state: `show_cpuinfo()` formats FPGA family, CPU version, endian, MHz, BogoMips, hardware instruction units, MMU, multiplier/FPU revision, exception capabilities, stream-instruction privilege, cache configuration, hardware debug, PVR user fields, and page size. `cpuinfo_op` exposes seq start/next/stop/show callbacks.

Control flow: family/version strings are found by reverse lookup through the static tables. The iterator returns one logical entry per `NR_CPUS`, although the hardware data is global.

State and persistence: read-only reporting from `cpuinfo` and `loops_per_jiffy`. It does not allocate or mutate kernel state.

Dependencies and integration: procfs core consumes `cpuinfo_op`. It depends on `setup_cpuinfo()` and `setup_cpuinfo_clk()` having populated global state before userspace reads `/proc/cpuinfo`.

Risks and test signals: multi-CPU iteration can duplicate global values on configurations that expose more than one CPU. Unknown version/family codes fall back to "Unknown". Test `/proc/cpuinfo` output after DTS/PVR changes, especially cache policy and endian labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/mb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/pvr.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/pvr.c

Purpose: provides raw access to MicroBlaze Processor Version Registers and probes whether usable PVR support exists.

Important APIs and state: `cpu_has_pvr()` inspects the PVR MSR bit and PVR0 flags, returning the selector used by `setup_cpuinfo()`. `get_pvr(struct pvr_s *p)` reads PVR0 through PVR11 with inline `mfs rpvrN` instructions.

Control flow: `cpu_has_pvr()` first reads saved MSR flags. If no PVR bit is set, it returns no support. Otherwise it reads PVR0 and distinguishes full versus partial support using `PVR0_PVR_FULL_MASK`.

State and persistence: no persistent state; callers store the resulting PVR data. The code only reads special registers.

Dependencies and integration: depends on assembler support for `rpvr` names and `asm/pvr.h` bit definitions. Used by CPU setup and kgdb.

Risks and test signals: return values and comments are easy to misread; setup code interprets `1` as full PVR and `2` as unsupported/partial fallback. Test on old cores without PVR, partial-PVR cores, and full-PVR cores, verifying boot path and `/proc/cpuinfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/pvr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/dma.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/dma.c

Purpose: supplies architecture DMA synchronization hooks for directly mapped non-coherent buses.

Important APIs and state: `arch_sync_dma_for_device()` and `arch_sync_dma_for_cpu()` call private `__dma_sync()`. For `DMA_TO_DEVICE` and `DMA_BIDIRECTIONAL`, it flushes dcache over the physical range; for `DMA_FROM_DEVICE`, it invalidates dcache; invalid directions BUG.

Control flow: both CPU and device sync paths share the same operation, assuming explicit cache maintenance is sufficient and physical addresses are accepted by the cacheflush implementation.

State and persistence: no persistent state. Effects are cache-hardware side effects over the requested DMA range.

Dependencies and integration: used by generic DMA mapping code. Depends on `flush_dcache_range()` and `invalidate_dcache_range()` being configured for the current cache policy.

Risks and test signals: wrong direction loses CPU or device writes. Empty or unaligned ranges depend on cache.c range alignment. Test streaming DMA in both directions and coherent versus non-coherent device paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/entry.S

Purpose: contains the central MicroBlaze low-level entry machinery for syscalls, traps, interrupts, debug traps, context switching, reset vectors, MB manager callbacks, and syscall table inclusion.

Important APIs and symbols: exports `_user_exception`, `ret_from_trap`, `ret_from_fork`, `ret_from_kernel_thread`, `full_exception_trap`, `unaligned_data_trap`, `page_fault_*_trap`, `ret_from_exc`, `_interrupt`, `_debug_exception`, `_switch_to`, `_reset`, optional `xmb_inject_err`, and `xmb_manager_register`. Macro blocks save/restore `pt_regs`, toggle BIP/EIP/IE/UMS/VMS, and switch physical/virtual mode.

Control flow: syscall entry builds a `pt_regs`, handles syscall tracing/seccomp/audit through `do_syscall_trace_enter()`, dispatches through `sys_call_table`, and returns through signal/reschedule work. Exception entries save state and call C handlers (`full_exception`, `do_page_fault`, `_unaligned_data_exception`). IRQ entry calls `do_IRQ` then handles user reschedule/signals or preemption. `_switch_to` saves/restores `cpu_context` and current-task state. The `.init.ivt` section emits physical branch vectors.

State and persistence: updates per-CPU `ENTRY_SP`/`CURRENT_SAVE`, `thread_info.cpu_context`, `pt_regs`, MSR bits, and optional MB-manager globals. No heap allocation.

Dependencies and integration: tightly coupled to `asm-offsets`, `thread_info`, `pt_regs`, `hw_exception_handler.S`, signal/ptrace/fault C code, and linker placement of `.init.ivt`.

Risks and test signals: register-save offsets, delay-slot return offsets, and physical/virtual transitions are high-risk. Test syscall tracing, fork/kernel threads, IRQ return to user/kernel, page faults, kgdb, MB manager builds, and boot vector copying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/exceptions.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/exceptions.c

Purpose: maps MicroBlaze hardware and software exceptions from low-level assembly into Linux signals or kernel oops handling.

Important APIs and state: `die()` prints registers under `die_lock` and terminates via `make_task_dead()`. `sw_exception()` handles debug `brki` traps. `_exception()` delivers a signal to user mode or oopses kernel mode. `full_exception()` decodes ESR exception types and chooses SIGILL, SIGBUS, or SIGFPE with architecture-specific si codes.

Control flow: assembly entry passes saved `pt_regs`, ESR/FSR/address context. User-mode faults become `force_sig_fault()`; kernel faults call `die()` except for FPU and privileged cases that still funnel through `_exception()`.

State and persistence: no persistent state beyond the spinlock. It mutates user signal state and may terminate tasks.

Dependencies and integration: called by `entry.S` and `hw_exception_handler.S`; relies on `kernel_mode()`/`user_mode()` and cache flushes for software breakpoints.

Risks and test signals: unexpected exceptions only log without forced termination in the default case. FPU code remaps FSR bits destructively into si_code. Test illegal instruction, divide-by-zero, bus error, FPU exception, user breakpoint, and kernel oops paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/exceptions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/ftrace.c

Purpose: implements MicroBlaze dynamic ftrace and function-graph text patching support.

Important APIs and state: `prepare_ftrace_return()` patches the caller's return address to `return_to_handler`. `ftrace_modify_code()` writes one instruction with exception-table protection and flushes dcache/icache. Dynamic ftrace hooks include `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, and graph caller enable/disable. Static state saves original `imm`, optional `bralid`, and `old_jump` instructions.

Control flow: graph tracing safely reads/replaces the parent return address, stops graph tracing on fault, and registers the original return with ftrace core. Dynamic callsites are disabled by replacing the initial `imm` with `bri 12` (or NOPs under the disabled alternative), then restored from saved instructions.

State and persistence: persistent global saved instruction words affect all patched callsites, so this implementation assumes uniform compiler-generated mcount prologues.

Dependencies and integration: paired with `mcount.S`, cacheflush code, dynamic ftrace core, and MicroBlaze instruction encodings.

Risks and test signals: global saved instruction state is fragile if callsite prologues differ. Missing cache flushes break patched text execution. Test dynamic ftrace enable/disable, graph tracing, fault injection around patched addresses, and module callsites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/head.S

Purpose: defines the earliest MicroBlaze kernel entry path, initial FDT/command-line capture, temporary TLB setup, MMU enable, stack/current initialization, and transition to `start_kernel`.

Important symbols and state: `swapper_pg_dir` reserves one page. `_start`/`real_start` are head entry symbols. `_fdt_start`, `cmd_line`, `tlb_skip`, and `kernel_tlb` are prepared for later C setup.

Control flow: boot disables MSR and stack-limit state, detects MSR instruction support, validates and copies an incoming FDT, optionally copies command line, invalidates all TLBs, creates initial kernel and LMB TLB mappings, enables virtual mode, sets SDA anchors, stack and current register, calls `machine_early_init()` and `mmu_init()`, then drops temporary mappings and jumps to `start_kernel` with MMU enabled.

State and persistence: mutates TLB entries, PID, MSR, boot command line, FDT staging area, `tlb_skip`, stack pointer, and current-task register.

Dependencies and integration: linker script must place head text, FDT space, and symbols correctly. `machine_early_init()` later copies exception vectors and clears BSS; `mmu_init()` replaces temporary mappings with page tables.

Risks and test signals: FDT copy assumes 64 KiB staging, TLB size selection is hand-coded, and wrong load/virtual offsets prevent boot. Test boot with linked and external DTB, cmdline pointer, MSR-instruction mismatch logs, small/large kernels, and MMU transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/hw_exception_handler.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/hw_exception_handler.S

Purpose: provides the real-mode hardware exception fast path for unaligned accesses, bus/illegal/div/FPU exceptions, storage faults, and data/instruction TLB misses.

Important symbols and state: `_hw_exception_handler`, `_unaligned_data_exception`, `set_context`, `giveup_fpu`, `abort`, `tlb_skip`, `tlb_index`, `pt_pool_space`, load/store jump tables, and `ex_tmp_data_loc_*`. The exception vector table maps ESR exception codes to handler labels.

Control flow: the top handler saves a minimal register set, decodes ESR, and jumps to a handler. TLB miss handlers walk Linux page tables in physical mode, set accessed bits, compose MicroBlaze TLB entries, and return directly if resolved; otherwise they restore state and branch to `page_fault_*_trap` in `entry.S`. Unaligned handlers emulate byte-wise word/halfword loads/stores and use exception-table fixups for bad user pages.

State and persistence: updates hardware TLBs, `tlb_index`, PTE accessed bits, PID, saved register pools, and temporary data bytes. No dynamic allocation.

Dependencies and integration: coupled to PTE bit layout, page-table levels, `entry.S` trap labels, exception table format, and `asm-offsets`.

Risks and test signals: register save omissions, TLB replacement masking, endian-sensitive unaligned stores, and page-table bit assumptions are high risk. Test user/kernel TLB misses, storage faults, unaligned loads/stores across page boundaries, exception-table fixups, and context switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/hw_exception_handler.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/irq.c

Purpose: bridges low-level MicroBlaze interrupt entry to the generic Linux IRQ subsystem.

Important APIs and state: `do_IRQ(struct pt_regs *regs)` is called from `_interrupt`; `init_IRQ()` initializes irqchips from the device tree.

Control flow: `do_IRQ()` installs IRQ regs, marks hard IRQs off, enters IRQ context, calls `handle_arch_irq(regs)`, exits IRQ context, restores prior regs, and marks hard IRQs on. `init_IRQ()` delegates to `irqchip_init()`.

State and persistence: updates per-CPU IRQ context accounting and current IRQ regs; no persistent architecture data is allocated here.

Dependencies and integration: requires `handle_arch_irq` from irqchip initialization and correct assembly-provided `pt_regs`.

Risks and test signals: missing irqchip or bad OF interrupt tree leaves `handle_arch_irq` unusable. Test timer interrupts, nested IRQ accounting, lockdep hardirq state, and DT irqchip probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/kgdb.c

Purpose: implements MicroBlaze KGDB register translation, breakpoint handling, and architecture KGDB operations.

Important APIs and state: `pt_regs_to_gdb_regs()`, `gdb_regs_to_pt_regs()`, `microblaze_kgdb_break()`, `sleeping_thread_to_gdb_regs()`, `kgdb_arch_set_pc()`, `kgdb_arch_handle_exception()`, `kgdb_arch_init()`, and `arch_kgdb_ops`. Static `pvr` snapshots immutable PVR registers for GDB.

Control flow: register export copies `pt_regs`, BTR, PVR, and special MMU registers into GDB slots. Import updates writable `pt_regs` values except r0 and special read-only slots. Break handling invokes KGDB core and skips the architecture breakpoint instruction when needed. Continue packets may set `regs->pc`.

State and persistence: KGDB init stores PVR data. Handlers mutate debugged task registers and PC.

Dependencies and integration: entered from `_debug_exception` in `entry.S`; depends on breakpoint byte order and `get_pvr()`.

Risks and test signals: sleeping-thread helper is marked untested. Wrong GDB register layout breaks remote debugging. Test kernel and user breakpoints, continue-with-address, endian-specific breakpoint encoding, and PVR register visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/mcount.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/mcount.S

Purpose: supplies the assembly `_mcount` trampoline and optional function graph return trampoline used by MicroBlaze ftrace.

Important symbols and state: exports `ftrace_stub`, `_mcount`, `ftrace_caller`, `ftrace_call_graph`, `ftrace_call`, and `return_to_handler`. Macros save/restore most GPRs in a 120-byte frame.

Control flow: `_mcount` optionally jumps over disabled dynamic ftrace, saves registers and original link register, handles function-graph return replacement through `prepare_ftrace_return()`, then calls the current trace function via `r20`. `return_to_handler` calls `ftrace_return_to_handler()` and returns to the address it supplies.

State and persistence: no static storage here; it consumes global ftrace function pointers and mutates stack frames.

Dependencies and integration: dynamic patch sites are modified by `ftrace.c`; module exports are provided through `microblaze_ksyms.c`.

Risks and test signals: save-frame offsets must match ftrace.c expectations for parent/current addresses. Test static and dynamic ftrace, graph tracing, nested tracing, and builds with tracer disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/mcount.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/microblaze_ksyms.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/microblaze_ksyms.c

Purpose: exports selected MicroBlaze architecture helpers and libgcc routines to loadable modules.

Important APIs and state: exports `_mcount` under function tracing, `__copy_tofrom_user`, optional optimized `memcpy`/`memmove`, cache dispatch `mbc`, 32-bit arithmetic helpers (`__divsi3`, `__modsi3`, `__mulsi3`, `__udivsi3`, `__umodsi3`), and optional MB-manager APIs.

Control flow: compile-time configuration gates which symbols are visible. There is no runtime control flow beyond module symbol resolution.

State and persistence: exporting `mbc` exposes the global cache dispatch pointer to modules; other exports are pure functions or assembly service routines.

Dependencies and integration: must match objects selected by kernel/lib Makefiles. Modules relying on compiler-emitted libgcc calls need these symbols.

Risks and test signals: exporting an object not linked for a config breaks build; missing arithmetic exports break module relocation. Test module builds using division/multiplication, uaccess, optimized string routines, and ftrace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/microblaze_ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/misc.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/misc.S

Purpose: implements low-level TLB invalidation helpers for MicroBlaze MMU.

Important symbols and state: `_tlbia` invalidates all non-pinned TLB entries starting at `tlb_skip`; `_tlbie` invalidates a single virtual address by searching with `rtlbsx` and clearing `rtlbhi` if found.

Control flow: `_tlbia` loops over TLB indices through `MICROBLAZE_TLB_SIZE - 1`, skipping entries pinned by boot. `_tlbie` loads the search address into `rtlbsx`, reads the resulting `rtlbx`, and clears valid state for hits.

State and persistence: mutates hardware TLB entries. No memory allocation or data persistence except using `tlb_skip`.

Dependencies and integration: called by MMU/page-table and context code through tlbflush helpers. Depends on `tlb_skip` from hardware exception handling.

Risks and test signals: invalidating pinned entries would unmap the kernel; not invalidating enough leaves stale translations. Test `flush_tlb_all`, `flush_tlb_page`, context stealing, ioremap/unmap, and page permission changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/misc.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/module.c

Purpose: applies MicroBlaze ELF relocations for loadable modules and performs final cache maintenance after module load.

Important APIs and state: `apply_relocate_add()` handles `R_MICROBLAZE_32`, `R_MICROBLAZE_64`, `R_MICROBLAZE_64_PCREL`, and no-op relocation types. `module_finalize()` flushes dcache.

Control flow: relocation iteration computes `value = sym->st_value + addend`, finds the target section address, and patches either full 32-bit words or split high/low immediate instruction pairs. Unknown relocation types return `-ENOEXEC`.

State and persistence: mutates module text/data in memory. No persistent module-private state is kept here.

Dependencies and integration: used by the kernel module loader; depends on MicroBlaze ELF relocation encodings and cache flush routines.

Risks and test signals: split relocations must preserve opcode high halves and correctly compute PC-relative offsets from `location + 4`. Test module loading with absolute, long-call, and PC-relative references; verify executable module text after cache flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/process.c

Purpose: implements process/thread architecture hooks: register dumps, thread creation, exec-thread setup, idle, and minimal FPU core-dump handling.

Important APIs and state: `show_regs()`, exported `pm_power_off`, `flush_thread()`, `copy_thread()`, `__get_wchan()`, `start_thread()`, `elf_core_copy_task_fpregs()`, and `arch_cpu_idle()`.

Control flow: kernel-thread clone initializes empty regs/context, stores function and argument in r20/r19, and returns through `ret_from_kernel_thread`. User clone copies current regs, sets child stack/TLS, adjusts MSR for return-to-user, and returns through `ret_from_fork`. `start_thread()` installs PC/SP and user-mode MSR state for exec.

State and persistence: mutates child `pt_regs` and `thread_info.cpu_context`; `pm_power_off` is global hook state. No allocation.

Dependencies and integration: context fields are restored in `_switch_to` from `entry.S`. Signal/ptrace code consumes `pt_regs` layout.

Risks and test signals: MSR bit composition is delicate for VM/UMS/IE/EIP. `__get_wchan()` is unimplemented. Test fork, clone with TLS, kernel threads, exec, core dumps, and register dumps after exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/prom.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/prom.c

Purpose: performs early device-tree scanning for MicroBlaze boot.

Important APIs and state: `early_init_devtree(void *params)` calls `early_init_dt_scan(params, __pa(params))`, copies `cmd_line` into `boot_command_line` when needed, and enables memblock resizing.

Control flow: called after early BSS clearing and FDT staging. It logs entry/exit and physical memory size for debugging.

State and persistence: initializes global OF/memblock boot state and possibly `boot_command_line`.

Dependencies and integration: called from `machine_early_init()` in setup; depends on `_fdt_start` or a bootloader-provided FDT having been copied by `head.S`.

Risks and test signals: invalid FDT pointer breaks memory discovery and all OF probing. Test external and linked DTB boot, boot command line fallback, and memblock memory region discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/ptrace.c

Purpose: implements MicroBlaze-specific ptrace register access and syscall tracing hooks.

Important APIs and state: `arch_ptrace()` handles `PTRACE_PEEKUSR`/`PTRACE_POKEUSR` for `pt_regs` offsets and text/data pseudo-offsets. `do_syscall_trace_enter()` handles seccomp, ptrace syscall-entry notification, and audit entry. `do_syscall_trace_leave()` handles audit exit and syscall-exit tracing. `ptrace_disable()` is a no-op.

Control flow: register offsets below `PT_SIZE` map directly into `task_pt_regs()`. Invalid or unaligned offsets return `-EIO`. Syscall entry can return `-1` to force ENOSYS dispatch while preserving original number in saved regs.

State and persistence: ptrace writes mutate saved user registers. Syscall tracing interacts with audit and seccomp state.

Dependencies and integration: entry.S calls tracing hooks on `_TIF_WORK_SYSCALL_MASK`; signal and fork paths depend on compatible `pt_regs`.

Risks and test signals: no validation prevents changing sensitive MSR/PC values beyond offset bounds. The disabled cache-maintenance alternative hints at write-back concerns. Test PEEK/POKE of every register, syscall tracing, seccomp strict, audit records, and single-step exit notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/reset.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/reset.c

Purpose: supplies MicroBlaze machine shutdown, halt, poweroff, and restart hooks.

Important APIs and state: `machine_shutdown()`, `machine_halt()`, and `machine_power_off()` log and spin forever. `machine_restart(char *cmd)` calls restart notifiers via `do_kernel_restart()`, waits one second, then logs failure and spins.

Control flow: there is no hardware reset sequence here; restart depends entirely on registered restart handlers.

State and persistence: no persistent state, but successful restart is delegated to notifier infrastructure.

Dependencies and integration: used by reboot/poweroff core and by MMU init fatal checks that call `machine_restart(NULL)`.

Risks and test signals: without a platform restart handler, reboot hangs after emergency log. Test reboot with and without a registered restart notifier and ensure watchdog/platform reset drivers integrate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/setup.c

Purpose: coordinates MicroBlaze architecture boot setup after early head code: memory setup, device-tree unflattening, CPU/cache setup, PCI init, vector copying, early clock/timer setup, and debugfs support.

Important APIs and state: per-CPU entry variables `KSP`, `KM`, `ENTRY_SP`, `R11_SAVE`, and `CURRENT_SAVE`; data-section `cmd_line`; `setup_arch()`, `machine_early_init()`, `time_init()`, optional `get_romfs_len()`, `kernel_tlb`, and debugfs initcalls.

Control flow: `setup_arch()` sets cmdline pointer, initializes memory, unflattens DT, populates CPU info, initializes caches, and probes PCI. `machine_early_init()` preserves optional romfs, clears BSS, scans DT, records kernel TLB footprint, validates MSR-instruction config, copies exception vectors from `.init.ivt` to BRAM, and initializes current per-CPU state. `time_init()` initializes OF clocks, CPU clock, and timer probe.

State and persistence: mutates boot memory limits, BSS, `klimit`, exception vector memory, per-CPU current state, and debugfs entries.

Dependencies and integration: called from `head.S`; uses `mmu_init()`, CPU-info/cache/timer/PCI subsystems, and linker symbols.

Risks and test signals: vector copy offsets and BSS clearing order are critical. ROMFS relocation can shift `klimit`. Test boot with MTD uClinux, manual reset vectors, debugfs, PCI, and MSR-instruction mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/signal.c

Purpose: implements MicroBlaze signal delivery, rt sigreturn, syscall restart, and user-mode resume work.

Important APIs and state: signal frame types `sigframe` and `rt_sigframe`; `sys_rt_sigreturn()`, `setup_rt_frame()`, `handle_restart()`, `do_notify_resume()`. Signal contexts save full `pt_regs` plus old mask; trampolines contain `__NR_rt_sigreturn` load and `brki r14, 0x8`.

Control flow: delivery selects the alt stack, writes `rt_sigframe`, emits user trampoline instructions, flushes trampoline cache lines by walking the user PTE, sets handler arguments in r5-r7, sets r15 to trampoline minus 8, and sets PC to handler. Return restores mask, altstack, registers, and syscall return value. Restart logic rewinds PC by 4 to re-execute the syscall trap.

State and persistence: mutates user stack, user signal mask, altstack state, and saved registers.

Dependencies and integration: called from entry return paths; depends on uaccess, page tables, cacheflush, syscall numbers, and MicroBlaze return-delay conventions.

Risks and test signals: cache flushing user trampoline must handle unmapped or migrated pages safely. Restart PC adjustment must match syscall trap size. Test signals on normal/alt stacks, SA_SIGINFO, rt_sigreturn tampering, interrupted syscalls, and write-back cache systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/stacktrace.c

Purpose: exposes generic stacktrace collection hooks on top of the MicroBlaze unwinder.

Important APIs and state: `save_stack_trace()` increments skip count to hide helper frames and calls `microblaze_unwind(NULL, trace, "")`; `save_stack_trace_tsk()` unwinds a specific task. Both are GPL-exported.

Control flow: all logic delegates to `unwind.c`; this file only adjusts the caller skip for current-task traces.

State and persistence: mutates the provided `struct stack_trace` counters and entries.

Dependencies and integration: used by generic stacktrace consumers; requires `CONFIG_STACKTRACE` behavior in `microblaze_unwind()`.

Risks and test signals: inaccurate unwinder output propagates to all consumers. Test stack traces for current and sleeping tasks, max entry limits, and skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/sys_microblaze.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/sys_microblaze.c

Purpose: implements MicroBlaze-specific mmap syscall wrappers.

Important APIs and state: `SYSCALL_DEFINE6(mmap, ...)` and `SYSCALL_DEFINE6(mmap2, ...)` validate offset alignment and call `ksys_mmap_pgoff()`.

Control flow: `mmap` expects byte offset in `pgoff` and rejects offsets not page aligned, then shifts by `PAGE_SHIFT`. `mmap2` expects 4 KiB units and rejects bits outside the page-granular range before shifting by `PAGE_SHIFT - 12`.

State and persistence: no architecture state; successful calls create VMAs through common mm code.

Dependencies and integration: entries are referenced by generated syscall table and invoked by `entry.S` syscall dispatch.

Risks and test signals: offset validation must match userspace ABI. Test mmap/mmap2 with aligned and misaligned offsets, large files, and 4 KiB page assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/sys_microblaze.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/syscall_table.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/syscall_table.S

Purpose: defines the MicroBlaze syscall dispatch table consumed by assembly syscall entry.

Important symbols and state: `ENTRY(sys_call_table)` emits `.long entry` for each generated `__SYSCALL(nr, entry)` line from `<asm/syscall_table.h>`.

Control flow: no executable code except data generation. `_user_exception` indexes this table by syscall number after range checking.

State and persistence: read-only table in the kernel image.

Dependencies and integration: generated header is built by `kernel/syscalls/Makefile`; syscall numbers must match `unistd_32.h` and userspace ABI.

Risks and test signals: stale generated headers or table width mismatch breaks syscall dispatch. Test syscall generation, table size symbol in `entry.S`, and representative syscalls including arch-specific mmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/syscall_table.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/syscalls/Makefile -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/syscalls/Makefile

Purpose: generates MicroBlaze syscall number and syscall table headers from `syscall.tbl`.

Important build rules and state: creates generated uapi and kapi directories, runs `scripts/syscallhdr.sh --emit-nr` to produce `unistd_32.h`, and runs `scripts/syscalltbl.sh` to produce `syscall_table.h`. Targets are recorded for Kbuild cleanup/tracking.

Control flow: the `all` phony target depends on both generated headers. Generation is guarded by Kbuild `if_changed`.

State and persistence: writes generated headers under `arch/$(SRCARCH)/include/generated/{uapi,}asm`.

Dependencies and integration: `syscall_table.S` includes the generated table; userspace headers use generated syscall numbers.

Risks and test signals: mkdir via `$(shell ...)` runs during Makefile parsing; missing scripts or malformed table breaks arch build. Test clean builds, incremental rebuild after syscall.tbl change, and generated header contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/timer.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/timer.c

Purpose: implements the Xilinx timer as MicroBlaze clockevent, clocksource, timecounter, and sched_clock provider.

Important APIs and state: static `timer_baseaddr`, `freq_div_hz`, `timer_clock_freq`, endian-sensitive `read_fn`/`write_fn`, `clockevent_xilinx_timer`, `clocksource_microblaze`, `xilinx_tc`, and OF declaration for `"xlnx,xps-timer-1.00.a"`.

Control flow: init ignores PWM nodes, maps timer registers, probes register endian by writing `TCSR_MDT`, parses IRQ, requires a two-timer device, gets timer clock or falls back to CPU clock, requests IRQ, starts timer1 as continuous clocksource, registers clockevent, and registers sched_clock. Timer0 handles periodic/oneshot events and acks interrupts by rewriting TCSR0.

State and persistence: maps MMIO, stores global timer function pointers, registers IRQ/clock devices, and keeps timer1 running.

Dependencies and integration: called by `timer_probe()` in `time_init()`, depends on OF address/IRQ/clock data and CPU clock fallback.

Risks and test signals: one-timer hardware is rejected; endian detection depends on writable MDT bit; oneshot currently uses ARHT like periodic. Test timer IRQs, clocksource stability, big/little-endian registers, missing clock fallback, and PWM-node exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/traps.c

Purpose: initializes hardware exceptions and prints kernel stack/call traces for trap diagnostics.

Important APIs and state: `trap_init()` calls `__enable_hw_exceptions()`. `show_stack()` prints stack words and delegates call-trace decoding to `microblaze_unwind()`. Boot parameter `kstack=` limits stack words printed through `kstack_depth_to_print`.

Control flow: show_stack selects an SP from an explicit argument, sleeping task context, or current stack, computes remaining words in `THREAD_SIZE`, aligns the first hex dump line, prints stack bytes, then prints call trace and held locks.

State and persistence: only boot parameter state persists. Diagnostic output reads kernel stack memory.

Dependencies and integration: used by generic dump_stack/oops paths; depends on exception enable helper and unwinder.

Risks and test signals: invalid SP can dump bad memory; depth limiting is useful for noisy logs. Test oops output, `kstack=` parameter, current and non-current task stack dumps, and trap initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/unwind.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/unwind.c

Purpose: implements best-effort MicroBlaze stack unwinding without reliable frame-pointer support.

Important APIs and state: `microblaze_unwind()` is exported. Helpers find stack-frame prologue instructions (`addik r1,r1,-FRAME_SIZE`), compute frame sizes, locate previous frame/PC, and recognize trap-handler address ranges from `microblaze_trap_handlers`.

Control flow: for current tasks it starts from current regs or inline PC/SP; for sleeping tasks it starts at `_switch_to` and saved CPU context. The inner loop prints or records PCs, stops on invalid/unmapped text, and advances using inferred frame size or leaf return address. Trap unwinding is mostly a stub, with a special stop for hardware exception handler ranges.

State and persistence: mutates only the supplied stack_trace. It reads kernel text and stacks.

Dependencies and integration: used by traps and stacktrace wrappers; depends on compiler prologue shape and linker-visible trap handler table from `entry.S`.

Risks and test signals: arbitrary backward scanning can miss large/prologue-less functions or misidentify instructions. Trap unwinding is incomplete. Test current/sleeping task traces, leaf functions, large functions, exception/IRQ frames, and stacktrace limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/vmlinux.lds.S

Purpose: defines the MicroBlaze kernel image layout, entry symbol, section placement, FDT staging area, init vector table, small-data anchors, and BSS boundaries.

Important symbols and state: `ENTRY(microblaze_start)`, `_text/_stext/_etext`, `_fdt_start/_fdt_end`, `_KERNEL_SDA2_BASE_`, `_KERNEL_SDA_BASE_`, `__ivt_start/__ivt_end`, `__bss_start/__bss_stop`, `_end`, and endian-dependent `jiffies` alias.

Control flow: linker script only. Runtime code in `head.S` and `setup.c` relies on these addresses for early FDT copy, BSS clearing, vector copying, SDA setup, and kernel mapping.

State and persistence: determines final persistent memory layout of the kernel image.

Dependencies and integration: includes generic vmlinux linker macros and architecture cache/page/thread constants.

Risks and test signals: section alignment affects MMU mappings, percpu layout, exception table alignment, and small-data ABI. The FDT area is fixed at 64 KiB. Test link map, boot with linked DTB, BSS clearing, initramfs placement, and exception vector copy boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/Makefile

Purpose: selects MicroBlaze architecture library objects for string routines, user copy, and libgcc-style arithmetic helpers.

Important build rules and state: removes `-pg` from 64-bit shift helper objects under function tracing, always builds `memset.o`, selects `fastcopy.o` when `CONFIG_OPT_LIB_ASM=y` or C `memcpy.o memmove.o` otherwise, always builds `uaccess_old.o`, and links arithmetic helper objects through `obj-y`.

Control flow: build-time only.

State and persistence: controls which symbols become part of the kernel image and available for module exports.

Dependencies and integration: paired with `microblaze_ksyms.c`, compiler-emitted libgcc calls, and optimized string Kconfig.

Risks and test signals: profiling arithmetic helpers can recurse through ftrace, hence `CFLAGS_REMOVE`. Test build matrix for function tracer and optimized assembly/C libraries, plus module symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/ashldi3.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/ashldi3.c

Purpose: implements the libgcc ABI helper `__ashldi3` for 64-bit arithmetic left shifts on 32-bit MicroBlaze.

Important APIs and state: `__ashldi3(long long u, word_type b)` uses `DWunion` from `libgcc.h` and is exported to modules.

Control flow: zero shifts return unchanged. Shifts >=32 move the low word into the high word and clear low; smaller shifts combine shifted high word with carry bits from low.

State and persistence: pure arithmetic, no persistent state.

Dependencies and integration: compiler-generated 64-bit shifts and modules may call it; endian layout comes from `libgcc.h`.

Risks and test signals: shift counts outside compiler-expected ranges are not specially masked. Test 0, 1, 31, 32, 63-bit shifts on both endian configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/ashldi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/ashrdi3.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/ashrdi3.c

Purpose: implements signed 64-bit arithmetic right shift helper `__ashrdi3`.

Important APIs and state: exported `__ashrdi3(long long u, word_type b)` uses the high word sign bit for sign extension.

Control flow: zero shifts return input. Shifts >=32 fill high with sign bits and shift the old high word into low; smaller shifts shift high arithmetically and carry low bits from high.

State and persistence: pure arithmetic.

Dependencies and integration: used for compiler-generated signed 64-bit shifts in core and modules; depends on endian-aware `DWunion`.

Risks and test signals: sign-extension correctness is critical around negative values. Test positive/negative values and boundaries 0, 31, 32, 63.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/ashrdi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/cmpdi2.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/cmpdi2.c

Purpose: implements signed 64-bit comparison helper `__cmpdi2`.

Important APIs and state: exported `__cmpdi2(long long a, long long b)` returns libgcc-style 0 for less, 1 for equal, and 2 for greater.

Control flow: compares signed high words first, then unsigned low words if highs match.

State and persistence: pure arithmetic.

Dependencies and integration: compiler and modules use it for 64-bit signed comparisons when no native sequence is emitted.

Risks and test signals: return values are not normal C comparison signs. Test negative/positive crossings, equal values, and low-word ordering with equal high words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/cmpdi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/divsi3.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/divsi3.S

Purpose: provides signed 32-bit division helper `__divsi3` for MicroBlaze cores or builds lacking hardware divide.

Important APIs and state: arguments are dividend r5 and divisor r6; result is r3. It saves r28-r31.

Control flow: zero divisor or zero dividend returns 0. Negative operands are made positive while saving result sign. A shift/subtract loop builds quotient bit by bit, then negates the result if needed.

State and persistence: pure arithmetic aside from callee-saved register preservation.

Dependencies and integration: exported to modules and used by compiler-generated division. Paired with `modsi3.S` and unsigned variants.

Risks and test signals: division by zero silently returns 0 instead of trapping. Edge case `INT_MIN / -1` follows two's-complement behavior of the routine. Test signed sign combinations, zero, INT_MIN, and builds without hardware div.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/divsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/fastcopy.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/fastcopy.S

Purpose: optimized assembly implementation of `memcpy` and `memmove` for MicroBlaze when `CONFIG_OPT_LIB_ASM` is enabled.

Important APIs and state: exports `memcpy` and `memmove`. Arguments use r5 destination, r6 source, r7 byte count; r3 returns original destination.

Control flow: ascending copy handles small byte tail, aligns destination, copies 32-byte blocks, handles aligned and 1/2/3-byte unaligned source cases with shifts, copies word remainder, then byte tail. `memmove` chooses ascending path when destination is below source; otherwise it performs a mirrored descending copy to preserve overlapping regions.

State and persistence: mutates destination memory only. No exception table protection, so it is for trusted kernel memory copies.

Dependencies and integration: selected instead of C string routines by Makefile and exported for modules under optimized assembly config.

Risks and test signals: endian and unaligned-source shift paths are complex; comments contain some stale typo offsets but code drives behavior. Test overlapping and non-overlapping copies, all source/dest alignments, small sizes 0-64, large blocks, and both endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/fastcopy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/libgcc.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/libgcc.h

Purpose: shared local header for MicroBlaze libgcc-compatible 64-bit helper implementations.

Important APIs and state: defines `word_type`, endian-dependent `struct DWstruct` with high/low 32-bit halves, `DWunion`, and prototypes for 64-bit shift/compare/multiply helpers.

Control flow: preprocessor selects structure field order by `__BIG_ENDIAN` or `__LITTLE_ENDIAN`; otherwise compilation fails.

State and persistence: no runtime state.

Dependencies and integration: included by C libgcc helper files; must match ABI endian layout and compiler helper names.

Risks and test signals: wrong field order corrupts every 64-bit helper. Test helper behavior in big/little endian builds and ensure prototypes match exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/libgcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/lshrdi3.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/lshrdi3.c

Purpose: implements unsigned/logical 64-bit right shift helper `__lshrdi3`.

Important APIs and state: exported `__lshrdi3(long long u, word_type b)` treats both halves as unsigned when shifting.

Control flow: zero shifts return input. Shifts >=32 zero the high word and move shifted old high into low; smaller shifts shift high logically and carry low bits from high.

State and persistence: pure arithmetic.

Dependencies and integration: used by compiler-generated unsigned 64-bit shifts; endian layout comes from `DWunion`.

Risks and test signals: high word must be zero-filled, not sign-extended. Test values with top bit set and shift counts 0, 31, 32, 63.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/lshrdi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/memcpy.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/memcpy.c

Purpose: C optimized `memcpy` implementation used when `CONFIG_OPT_LIB_FUNCTION` is enabled and assembly fastcopy is not selected.

Important APIs and state: exported `memcpy(void *dst, const void *src, __kernel_size_t c)`.

Control flow: aligns destination byte by byte, then chooses a word-copy path based on source alignment. Aligned sources copy words directly; unaligned sources assemble each word from adjacent aligned loads with endian-specific shifts. Remaining 1-3 bytes are copied individually.

State and persistence: mutates destination memory only.

Dependencies and integration: selected by lib Makefile when not using assembly fastcopy; module export is conditional through ksyms.

Risks and test signals: it is not overlap-safe; callers needing overlap must use memmove. Unaligned paths may be slow without barrel shifter. Test all alignments, endian builds, small counts, and non-overlap assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/memmove.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/memmove.c

Purpose: C optimized overlap-safe `memmove` implementation for MicroBlaze.

Important APIs and state: exported `memmove(void *dst, const void *src, __kernel_size_t c)` under `CONFIG_OPT_LIB_FUNCTION`.

Control flow: zero length returns immediately. If destination is below source, it delegates to `memcpy`; otherwise it copies descending from the end, aligns destination, then performs direct or endian-specific unaligned word assembly before copying remaining bytes backward.

State and persistence: mutates destination memory.

Dependencies and integration: selected by lib Makefile when assembly fastcopy is off.

Risks and test signals: descending unaligned cases are explicitly marked as needing more testing. Test overlapping ranges where dst starts inside src, all alignments, counts near word boundaries, and both endian configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/memmove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/memset.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/memset.c

Purpose: C optimized `memset` implementation for MicroBlaze.

Important APIs and state: exported `memset(void *v_src, int c, __kernel_size_t n)` under `CONFIG_OPT_LIB_FUNCTION`.

Control flow: truncates fill byte, expands it to a 32-bit repeated word, aligns destination to a word boundary, writes full words, then writes remaining 1-3 bytes.

State and persistence: mutates the target memory region only.

Dependencies and integration: always selected by lib Makefile; export depends on function config.

Risks and test signals: alignment switch intentionally falls through. Test zero and nonzero fills, all destination alignments, small sizes, and large word fills.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/memset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/modsi3.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/modsi3.S

Purpose: provides signed 32-bit modulo helper `__modsi3`.

Important APIs and state: arguments are r5 dividend and r6 divisor; remainder is returned in r3. Saves r28-r31.

Control flow: zero divisor or dividend returns 0. The routine normalizes signs, performs shift/subtract division while keeping the remainder, then applies the dividend sign to the result.

State and persistence: pure arithmetic.

Dependencies and integration: used by compiler-generated `%` operations and exported to modules.

Risks and test signals: division by zero returns 0. Test sign rules (`-a % b`), zero cases, INT_MIN, and no-hardware-div builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/modsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/muldi3.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/muldi3.c

Purpose: implements 64-bit multiply helper `__muldi3` using 16-bit partial products.

Important APIs and state: exported `__muldi3(long long u, long long v)`. Macros split 32-bit words into 16-bit halves and assemble a 64-bit product in `DWunion`.

Control flow: computes low-word product with `__umulsidi3`, then adds cross products of low/high 32-bit halves into the high word.

State and persistence: pure arithmetic.

Dependencies and integration: compiler-generated 64-bit multiply and modules use it; endian layout is from `libgcc.h`.

Risks and test signals: carry handling in partial products is critical. Test signed/unsigned bit patterns, high-half overflow, zero/one/m negative values, and module use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/muldi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/mulsi3.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/mulsi3.S

Purpose: provides signed 32-bit multiply helper `__mulsi3` for cores/builds without hardware multiply.

Important APIs and state: operands are r5/r6, result r3. The routine uses shift/add multiplication and sign correction.

Control flow: zero operands return 0. Negative operands are made positive while saving result sign; loop shifts the multiplier and conditionally accumulates multiplicand; negative result is negated before return.

State and persistence: pure arithmetic.

Dependencies and integration: exported to modules and used by compiler-generated multiplication when needed.

Risks and test signals: overflow follows low 32-bit two's-complement behavior. Test sign combinations, zero, one, high-bit operands, and no-hardware-mul builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/mulsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/uaccess_old.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/uaccess_old.S

Purpose: assembly implementation of `__copy_tofrom_user`, returning the number of bytes not copied on user access fault.

Important APIs and state: global `__copy_tofrom_user(char *to, char *from, int len)` uses r5/r6/r7 and returns r3. Large page-sized aligned copies use unrolled 512-byte chunks and save r19-r25.

Control flow: zero length returns 0. If addresses or count are unaligned, it copies byte-by-byte with exception-table fixups. Aligned non-page copies use a word loop. Exactly page-sized aligned copies use heavily unrolled load/store macros. Fault fixups return the remaining byte count.

State and persistence: mutates destination memory; exception table entries persist in `__ex_table`.

Dependencies and integration: exported through ksyms and consumed by uaccess helpers.

Risks and test signals: the page-sized fast path assumes count equals `PAGE_SIZE` and stack save/restore correctness. Test copy_to/from_user success/fault at every instruction group, unaligned addresses, zero length, and full-page copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/uaccess_old.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/ucmpdi2.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/ucmpdi2.c

Purpose: implements unsigned 64-bit comparison helper `__ucmpdi2`.

Important APIs and state: exported `__ucmpdi2(unsigned long long a, unsigned long long b)` returns 0, 1, or 2 for less, equal, or greater.

Control flow: compares unsigned high words first, then unsigned low words.

State and persistence: pure arithmetic.

Dependencies and integration: used by compiler-generated unsigned 64-bit comparisons and modules.

Risks and test signals: return convention differs from normal compare. Test values around 2^32, top-bit-set highs, equal values, and endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/ucmpdi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/udivsi3.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/udivsi3.S

Purpose: provides unsigned 32-bit divide helper `__udivsi3`.

Important APIs and state: arguments are r5 dividend and r6 divisor despite a misleading comment; result is r3. Saves r29-r31.

Control flow: zero divisor/dividend returns 0. Equal operands return 1. If divisor is greater than dividend, returns 0. Otherwise a shift/subtract loop builds quotient.

State and persistence: pure arithmetic.

Dependencies and integration: used by compiler-generated unsigned division and exported to modules.

Risks and test signals: comments are inconsistent; behavior should be verified against ABI. Division by zero returns 0. Test 0, equal, divisor larger, high-bit unsigned operands, and random comparisons against C division.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/udivsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/umodsi3.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/lib/umodsi3.S

Purpose: provides unsigned 32-bit modulo helper `__umodsi3`.

Important APIs and state: operands are r5 dividend and r6 divisor; remainder r3. Saves r29-r31.

Control flow: zero divisor/dividend returns 0. Equal operands return 0. If divisor exceeds dividend, returns dividend. Otherwise it performs unsigned shift/subtract division and keeps the remainder.

State and persistence: pure arithmetic.

Dependencies and integration: compiler `%` operations and modules use it when hardware support is absent.

Risks and test signals: special high-bit path manually masks sign bits for one case and should be covered. Test divisor larger/equal, high-bit operands, random unsigned modulo, and zero divisor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/lib/umodsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/microblaze/mm/Makefile

Purpose: selects the MicroBlaze MMU/memory-management objects.

Important build rules and state: `obj-y := consistent.o init.o pgtable.o mmu_context.o fault.o` unconditionally links coherent DMA prep, boot memory/MMU init, page-table/ioremap helpers, context allocator, and page-fault handling.

Control flow: build-time only.

State and persistence: determines which memory-management implementation is present in every MicroBlaze kernel build represented by this tree.

Dependencies and integration: linked with low-level assembly TLB handlers and setup/head code.

Risks and test signals: no config gating means these files must build across MMU-related options present in this architecture. Test all MicroBlaze defconfigs and highmem/CMA/initrd variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/consistent.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/mm/consistent.c

Purpose: prepares coherent DMA allocations by flushing cache lines backing the allocated pages.

Important APIs and state: `arch_dma_prep_coherent(struct page *page, size_t size)` converts the page to a physical address and calls `flush_dcache_range()`.

Control flow: single straight-line operation over `[page_to_phys(page), +size)`.

State and persistence: no persistent state; cache side effects make memory coherent for device use.

Dependencies and integration: called by generic DMA allocation code; depends on `cache.c` implementation and valid page-to-phys mapping.

Risks and test signals: only flushes, not invalidates, so coherency assumptions must match DMA API expectations. Test coherent DMA allocations, write-back cache systems, and multi-page size ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/consistent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/mm/fault.c

Purpose: handles heavyweight MicroBlaze page faults that assembly TLB miss handlers cannot resolve.

Important APIs and state: `do_page_fault()`, `bad_page_fault()`, private counters `pte_misses` and `pte_errors`, and `store_updates_sp()` for stack-growth validation.

Control flow: the handler stores EAR/ESR into regs, derives write/read fault state, handles disabled fault contexts, raises perf events, locks `mmap_lock`, locates/expands VMAs including stack guard checks, validates access permissions, calls `handle_mm_fault()`, handles retry/completed/error cases, and sends SIGSEGV/SIGBUS or calls kernel fixups/oops. `bad_page_fault()` uses exception tables before dying.

State and persistence: updates fault counters, `pt_regs`, VMA/page-table state through common mm, and user signals.

Dependencies and integration: called from `entry.S`; fast-path TLB handlers in `hw_exception_handler.S` fall back here.

Risks and test signals: instruction-fault write detection uses ESR bit patterns; stack growth has architecture-specific allowances. Test user read/write/exec faults, stack expansion, kernel uaccess fixups, OOM, SIGBUS mappings, and retry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/mm/init.c

Purpose: initializes MicroBlaze physical memory, zones, MMU hardware, kernel mappings, memblock reservations, fixmaps, highmem, and page protection map.

Important APIs and state: globals `mem_init_done`, `klimit`, `memory_start`, `memory_size`, `lowmem_size`, exported PFN bounds, `setup_memory()`, `mem_init()`, `page_is_ram()`, `mmu_init()`, and `protection_map`.

Control flow: `mmu_init()` validates minimum memory and kernel footprint, derives memory bounds from memblock, applies `mem=`, reserves kernel/initrd, sets ZPR, maps RAM, initializes ioremap bounds, initializes MMU contexts, constrains memblock allocation, parses early params, scans reserved memory, reserves CMA, and dumps memblock. `setup_memory()` computes PFN ranges and clears fixmaps.

State and persistence: boot-time globals and page tables persist; `mem_init_done` changes ioremap behavior after memory init.

Dependencies and integration: called from `head.S`; uses `mapin_ram()`, `map_page()`, `mmu_context_init()`, and setup-provided `kernel_tlb`.

Risks and test signals: low memory > `CONFIG_LOWMEM_SIZE` truncation, highmem behavior, and kernel TLB size checks can prevent boot. Test small memory rejection, initrd reservation, `mem=`, CMA, highmem, fixmap clearing, and protection bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/mmu_context.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/mm/mmu_context.c

Purpose: manages MicroBlaze MMU address-space context IDs.

Important APIs and state: global `next_mmu_context`, `context_map`, `nr_free_contexts`, and `context_mm[]`; `mmu_context_init()` initializes reserved/free contexts; `steal_context()` reclaims one context.

Control flow: context zero is reserved for kernel. On exhaustion, `steal_context()` selects `next_mmu_context`, flushes that mm's TLB entries, and destroys its context.

State and persistence: persistent allocator state maps context IDs to `mm_struct` owners.

Dependencies and integration: used by `asm/mmu_context.h` helpers and TLB switch paths; `set_context` in assembly writes PID.

Risks and test signals: no LRU, so reclaim is pseudo-random and depends on `next_mmu_context` maintenance outside this file. Test many-process context rollover, TLB flush correctness, and kernel context reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/mmu_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/pgtable.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/mm/pgtable.c

Purpose: builds and manipulates MicroBlaze kernel page tables, ioremap mappings, physical-address lookup, RAM linear mapping, early PTE allocation, and fixmaps.

Important APIs and state: exported `ioremap_bot`; globals `ioremap_base`, `ioremap_bot`; functions `ioremap()`, `iounmap()`, `map_page()`, `mapin_ram()`, `iopa()`, `pte_alloc_one_kernel()`, and `__set_fixmap()`.

Control flow: `__ioremap()` rejects remapping normal RAM after `mem_init_done`, allocates vmalloc or early downward ioremap space, maps pages with guarded/no-cache flags, and returns offset-adjusted virtual address. `map_page()` allocates kernel PTEs and invalidates TLB after boot. `mapin_ram()` maps lowmem with write permissions outside kernel text. `iopa()` walks page tables for current or init mm.

State and persistence: mutates kernel page tables, ioremap virtual allocation state, and TLB entries.

Dependencies and integration: used by MMU init, drivers, PCI, fixmap, and DMA translation paths.

Risks and test signals: `iounmap()` range check appears unusual and may skip some vmalloc areas. Early PTE allocation is bounded by `memory_start + kernel_tlb`. Test early/late ioremap, RAM remap rejection, fixmaps, iopa for user/kernel addresses, and text page permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/mm/pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/pci/Makefile -->
# sources/distributed-fs/ceph-client/arch/microblaze/pci/Makefile

Purpose: selects MicroBlaze PCI iomap support when PCI is enabled.

Important build rules and state: `obj-$(CONFIG_PCI) += iomap.o`.

Control flow: build-time only.

State and persistence: determines whether MicroBlaze PCI I/O unmap helpers and controller list state are linked.

Dependencies and integration: used with architecture PCI setup from `setup_arch()` and generic PCI code.

Risks and test signals: PCI builds without `iomap.o` would lack `pci_iounmap` behavior. Test `CONFIG_PCI=y/n` build matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/pci/iomap.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/pci/iomap.c

Purpose: implements MicroBlaze PCI I/O mapping helpers and controller tracking used by generic PCI unmap paths.

Important APIs and state: `hose_list`, `hose_spinlock`, exported `isa_io_base`, `pcibios_vaddr_is_ioport()`, `pci_proc_domain()`, and exported `pci_iounmap()`.

Control flow: `pcibios_vaddr_is_ioport()` scans registered PCI controllers under spinlock and checks whether a virtual address lies inside a hose I/O window. `pci_iounmap()` skips ISA and PCI I/O-port virtual ranges, otherwise calls generic `iounmap()`.

State and persistence: global controller list and ISA base persist for PCI subsystem lifetime.

Dependencies and integration: relies on platform PCI code populating `hose_list` and `io_base_virt`. Used by drivers calling `pci_iounmap()`.

Risks and test signals: bad hose resource sizes or missing list entries can iounmap I/O-port cookies incorrectly. Test PCI domain display, MMIO unmap, I/O port unmap skip, and multi-controller setups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/pci/iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/Kbuild -->
# sources/distributed-fs/ceph-client/arch/mips/Kbuild

Purpose: top-level Kbuild composition for the MIPS architecture subtree.

Important build rules and state: includes `arch/mips/Kbuild.platforms`, assigns `obj-y` and `obj-` from `platform-y`, then adds generic architecture directories `generic/`, `kernel/`, `mm/`, `net/`, and `vdso/`; adds `kvm/` under `CONFIG_KVM`; includes `boot` as a clean subdir.

Control flow: build-time only. The `obj- := $(platform-y)` line exists so make clean traverses platform objects before `.config` has been included.

State and persistence: determines linked MIPS architecture object directories and clean traversal.

Dependencies and integration: consumed by top-level Kbuild for MIPS builds; depends on platform definitions from `Kbuild.platforms`.

Risks and test signals: directory ordering affects link composition. Missing `obj-` clean behavior can leave platform artifacts. Test MIPS allnoconfig/defconfig builds, KVM on/off, and `make ARCH=mips clean`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/Kbuild -->
