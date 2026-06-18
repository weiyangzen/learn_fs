# Research: subset-b-000918

Grouped research for Xtensa architecture sources under `sources/distributed-fs/ceph-client`. Each source file is represented by one marker-delimited section so reconciliation can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/setup.c

Purpose: Performs early Xtensa architecture setup: boot parameter parsing, device-tree early scan, MMU/KASAN/platform initialization, memory reservation, topology registration, reset/power paths, and `/proc/cpuinfo` reporting.

Important APIs, types, and functions: `init_arch()`, `setup_arch()`, `early_init_devtree()`, `parse_bootparam()`, tag parsers for memory/initrd/FDT/cmdline, `cpu_reset()`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, and `cpuinfo_op`. It exports `xtensa_kio_paddr` when OF-driven KIO remapping is needed.

Control flow: `init_arch()` sets trap support for KASAN/load-store configurations, initializes the MMU and early KASAN shadow, parses boot tags, scans the flattened device tree, applies configured command line fallback, and calls `platform_init()`. `setup_arch()` publishes the command line, lets the platform adjust it, reserves initrd/kernel/vector/XIP/secondary reset memory, parses early params, initializes boot memory/KASAN/DT/SMP/paging/zones, and selects console behavior. `cpu_reset()` disables interrupts, flushes/rebuilds TLB state, resets debug/timer/loop registers, then jumps to `XCHAL_RESET_VECTOR_VADDR`.

State and persistence: Mutates global boot command buffers, memblock reservations, CPU registration state, DT-derived KIO physical base, initrd bounds, and per-CPU `struct cpu` descriptors. `/proc/cpuinfo` state is derived from hardware config macros, `ccount_freq`, and `loops_per_jiffy`.

Dependencies and integration: Depends on `asm/bootparam.h`, `asm/platform.h`, `asm/sysmem.h`, MMU/KASAN/trap helpers, OF flat-tree helpers, memblock, SMP setup, and linker-provided vector section symbols. Platform hooks (`platform_init`, `platform_setup`) are the key board/simulator integration points.

Risks: Boot tag size walking and command-line copying must remain bounded; KIO remapping assumes a simple-bus `ranges` layout; `cpu_reset()` contains delicate MMUv2/MMUv3 assembly and temporary mappings where wrong addresses can cause multihit or unrecoverable reset failures. Memory reservations must match linker sections or vectors/XIP text may be reused.

Test signals: Boot on OF and bootparam paths, verify memblock map/initrd reservation, `/proc/cpuinfo`, restart/poweroff behavior, SMP possible CPU detection, vector reservation, KASAN boot, and mismatched hardware config ID logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/signal.c

Purpose: Implements Xtensa real-time signal delivery and return, preserving user register state, register windows, optional coprocessor state, altstack data, and syscall restart semantics.

Important APIs, types, and functions: `struct rt_sigframe`, `flush_window_regs_user()`, `setup_sigcontext()`, `restore_sigcontext()`, `xtensa_rt_sigreturn()`, `gen_return_code()`, `setup_frame()`, `do_signal()`, and `do_notify_resume()`.

Control flow: Signal setup flushes live register windows to the user stack, copies core/coprocessor/user extension registers into the frame, saves the mask and altstack, installs either a user restorer or generated `rt_sigreturn` instructions, and rewrites `pt_regs` so userspace enters the handler. Return validates the frame, restores the blocked mask, register state, altstack, and returns the saved `a2`. `do_signal()` handles `-ERESTART*` values by either converting to `-EINTR` or rewinding `pc` by the syscall instruction width.

State and persistence: Writes user stack frames, updates current signal mask, `pt_regs`, thread-local Xtensa extension/coprocessor buffers, and restart block function. Generated return code requires explicit I-cache/D-cache synchronization.

Dependencies and integration: Integrates with generic signal core (`get_signal`, `signal_setup_done`), `uaccess`, `resume_user_mode_work`, Xtensa ABI macros, optional FDPIC function descriptors, coprocessor lazy context handling, and cacheflush routines.

Risks: Register-window spill failures become `SIGSEGV`; generated stack code is sensitive to endian encodings and syscall number size; `depc > 64` double-exception paths panic; restoring only selected PS bits is intentional but fragile; FDPIC handler/restorer descriptors must be validated.

Test signals: Exercise SA_SIGINFO, SA_RESTORER, altstack, FDPIC if enabled, syscall restart cases, user stack fault during frame build/return, coprocessor users, windowed and call0 ABIs, and single-step preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/smp.c

Purpose: Provides Xtensa SMP bring-up, CPU hotplug, IPI delivery, IPI accounting, and SMP-wide TLB/cache maintenance wrappers.

Important APIs, types, and functions: `ipi_init()`, `smp_init_cpus()`, `smp_prepare_boot_cpu()`, `secondary_start_kernel()`, `boot_secondary()`, `__cpu_up()`, hotplug methods, `ipi_interrupt()`, `show_ipi_list()`, and exported `flush_icache_range()`.

Control flow: CPU discovery reads `SYSCFGID`; secondary boot writes `start_info.stack`, unstalls the target core through `MPSCORE`, handshakes via `cpu_start_ccount` and `cpu_running`, then the secondary initializes MMU/traps/IRQ/timer and enters idle. IPIs are sent by writing CPU bitmasks to `MIPISET(msg_id)` and drained by reading/clearing `MIPICAUSE(cpu)`. Flush routines wrap local TLB/cache operations in `on_each_cpu()`.

State and persistence: Maintains possible/present/online CPU masks, per-CPU ASID caches, per-CPU IPI counters, boot handshake globals, hotplug `cpu_start_id`, and per-mm CPU masks during teardown.

Dependencies and integration: Requires `S32C1I` for SMP, MX core registers, generic CPU hotplug, scheduler IPIs, `generic_smp_call_function_interrupt`, IRQ mapping, local cache/TLB helpers, and platform secondary IRQ/timer hooks.

Risks: Boot/hotplug handshakes depend on explicit barriers and cross-CPU cache invalidation; timeouts report `-EIO` but may leave a stalled core; IPI bitmask construction assumes CPU index fits an `unsigned long`; global flushes can be expensive; stopping an IPI target calls `machine_halt()`.

Test signals: Boot all cores, online/offline cycles, call-function and reschedule IPIs, `/proc/interrupts` IPI counts, TLB/cache shootdowns under mmap stress, and failure paths for missing IPI IRQ mapping or secondary boot timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/stacktrace.c

Purpose: Walks Xtensa kernel and user call stacks for perf, diagnostics, generic stacktrace, and `return_address()`.

Important APIs, types, and functions: `xtensa_backtrace_user()`, `xtensa_backtrace_kernel()`, `walk_stackframe()`, `save_stack_trace_tsk()`, `save_stack_trace()`, `return_address()`, `struct stackframe`, and callbacks for stack trace collection.

Control flow: User backtrace first emits current PC/SP, walks valid register windows using `windowstart/windowbase`, then follows spilled stack frames with guarded `__get_user()` reads. Kernel backtrace spills registers, walks stack frames inside the thread stack, recognizes `common_exception_return` to transition into user unwinding, and uses callbacks for each frame. Generic `walk_stackframe()` follows saved `a0/a1` pairs until stack progress stops.

State and persistence: Mostly read-only, but `spill_registers()` writes live register windows to the current stack. Stack trace APIs fill caller-provided buffers and return-address state.

Dependencies and integration: Depends on Xtensa window ABI conventions, `MAKE_PC_FROM_RA`, `SPILL_SLOT`, `kernel_text_address`, `common_exception_return`, user access helpers, perf events, and generic `CONFIG_STACKTRACE` interfaces.

Risks: Bad or corrupted `a1` chains terminate early or can skip frames; user unwinding is unavailable for call0-only/probed non-windowed state; stack walking assumes monotonic SP progress; exception-frame detection is tightly coupled to vector return code.

Test signals: Validate perf callchains, `dump_stack`, `/proc` stack users, kernel oops traces, call0 vs windowed userspace, user-stack fault handling, and traces through exception return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/syscall.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/syscall.c

Purpose: Defines the Xtensa syscall table and architecture-specific syscall/mmap helpers.

Important APIs, types, and functions: `sys_call_table[]`, `xtensa_shmat()`, `xtensa_fadvise64_64()`, and `arch_get_unmapped_area()` under MMU builds.

Control flow: The syscall table is generated by expanding `<asm/syscall_table.h>`. `xtensa_shmat()` calls `do_shmat()` with `SHMLBA` coloring and returns the attached address. `xtensa_fadvise64_64()` reorders arguments for the generic implementation. `arch_get_unmapped_area()` honors `MAP_FIXED`, rejects shared fixed mappings that violate cache coloring, aligns shared mappings with `COLOUR_ALIGN()`, scans VMAs with `vma_iterator`, and returns an address or `-ENOMEM/-EINVAL`.

State and persistence: Does not maintain durable state directly; it reads and navigates `current->mm` and VMA state while selecting mapping addresses.

Dependencies and integration: Depends on generated syscall headers, SysV SHM, file/mm/VMA APIs, Xtensa `SHMLBA` cache-alias alignment, and generic syscall implementations.

Risks: Wrong color alignment can create D-cache aliasing bugs for shared mappings; VMA gap scanning must avoid overflow near `TASK_SIZE`; syscall table generation must match ABI numbering.

Test signals: Syscall smoke tests, `shmat()` shared-memory alignment tests, `mmap(MAP_SHARED)` alias-color tests, fixed mapping rejection, and fadvise argument ordering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/syscalls/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/syscalls/Makefile

Purpose: Generates Xtensa syscall UAPI and kernel syscall table headers from `syscall.tbl`.

Important APIs, types, and functions: Defines `uapi`, `kapi`, `syscall`, `syshdr`, `systbl`, `cmd_syshdr`, `cmd_systbl`, targets for `unistd_32.h` and `syscall_table.h`, and an `all` phony target.

Control flow: Ensures generated include directories exist, invokes `scripts/syscallhdr.sh --emit-nr` for UAPI syscall numbers, invokes `scripts/syscalltbl.sh` for the kernel table include, records generated files in `targets`, and makes `all` depend on both outputs.

State and persistence: Writes generated headers under `arch/$(SRCARCH)/include/generated/{uapi/,}asm`; these generated artifacts feed syscall compilation and UAPI exposure.

Dependencies and integration: Kbuild `if_changed`, `FORCE`, `CONFIG_SHELL`, top-level syscall scripts, `syscall.tbl`, and `arch/xtensa/kernel/syscall.c`.

Risks: Path prefix depth in `targets` must stay consistent with kbuild invocation; stale generated headers can desynchronize syscall numbers and table entries; mkdir through `$(shell ...)` runs at parse time.

Test signals: `make headers_install`, clean incremental rebuild after editing `syscall.tbl`, generated `asm/unistd_32.h`, generated `asm/syscall_table.h`, and syscall table compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/time.c

Purpose: Implements Xtensa `ccount` clocksource, per-CPU clockevent timers, sched_clock registration, CPU frequency calibration, and delay calibration.

Important APIs, types, and functions: `ccount_freq`, `ccount_read()`, `ccount_sched_clock_read()`, `struct ccount_timer`, `ccount_timer_set_next_event()`, `ccount_timer_shutdown()`, `ccount_timer_set_oneshot()`, `timer_interrupt()`, `local_timer_setup()`, `calibrate_ccount()`, `time_init()`, and `calibrate_delay()`.

Control flow: `time_init()` initializes clocks, derives `ccount_freq` from OF clock or platform/config, registers the 32-bit `ccount` clocksource, sets up CPU0 clockevent, requests the timer IRQ, registers sched_clock, and calls `timer_probe()`. Per-CPU setup maps `LINUX_TIMER_INT`, configures clockevents, and later enables/disables IRQs using balanced state tracking.

State and persistence: Exports global CPU clock frequency and maintains per-CPU timer device state (`irq_enabled`, IRQ number, cpumask, name). `loops_per_jiffy` is preset from `ccount_freq`.

Dependencies and integration: Depends on `get_ccount()`, `set_linux_timer()`, OF clocks, clocksource/clockevents, IRQ mapping, scheduler clock, platform calibration, SMP local timer setup, and generic timer probing.

Risks: Incorrect or zero `ccount_freq` breaks timekeeping and delay loops; `set_next_event()` detects already-expired deadlines with wrap-sensitive subtraction; timer IRQ cannot be disabled at device level, so nested IRQ enable/disable accounting matters.

Test signals: Boot time calibration logs, clocksource registration, tick delivery on CPU0 and secondary CPUs, high-resolution timer behavior, suspend/tick resume if applicable, and delay-loop sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/traps.c

Purpose: Initializes and handles Xtensa exceptions, interrupts, debug traps, coprocessor traps, fatal oops reporting, and stack/register dumps.

Important APIs, types, and functions: `dispatch_init_table`, per-CPU `exc_table` and `debug_table`, `do_unhandled()`, `do_interrupt()`, `do_illegal_instruction()`, `do_div0()`, `do_load_store()`, `do_unaligned_user()`, `do_coprocessor()`, `do_debug()`, `trap_set_handler()`, `trap_init()`, `secondary_trap_init()`, `show_regs()`, `show_stack()`, and `die()`.

Control flow: `trap_init()` seeds all causes with default user/kernel fast handlers and `do_unhandled`, then overlays configured fast and C handlers from `dispatch_init_table`, and writes per-CPU exception/debug save registers. Interrupt handling loops by priority level, masks previously unhandled bits, dispatches each pending IRQ via `do_IRQ()`, and exits through generic IRQ accounting. Exception handlers kill userspace with appropriate signals or call `die()` for kernel faults.

State and persistence: Per-CPU dispatch tables hold handler pointers; debug table stores debug exception entry; fake NMI path tracks per-CPU `nmi_count`; `die()` updates static `die_counter` and taints the kernel.

Dependencies and integration: Coupled to `vectors.S` table layout, `asm/traps.h`, page-fault handler, fast handlers, PMU NMI handler, hardware breakpoint code, stacktrace support, signal delivery, IRQ core, and coprocessor state management.

Risks: Dispatch table ordering must agree with vector assembly offsets; fake NMI validation can bugcheck if unexpected high-level IRQs fire; illegal divide-by-zero detection relies on the `DIV0` marker after an illegal instruction; `die()` in interrupt context panics.

Test signals: Boot trap initialization, user illegal instruction/div0/unaligned/load-store faults, kernel exception-table fixups, PMU/debug breakpoints, IRQ storms, stack dump format, and SMP secondary trap init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/vectors.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/vectors.S

Purpose: Contains the primary Xtensa exception, interrupt, debug, double-exception, and register window vectors executed directly by the processor.

Important APIs, types, and functions: `_UserExceptionVector`, `_KernelExceptionVector`, `_DoubleExceptionVector`, `window_overflow_restore_a0_fixup`, `_DebugInterruptVector`, generated `_LevelNInterruptVector` entries, `_SimulateUserKernelVectorException`, and `_Window{Overflow,Underflow}{4,8,12}`.

Control flow: User/kernel vectors save minimal registers, choose the fast handler from the per-CPU exception table, and jump without literals. The double-exception vector distinguishes user/window exceptions, kernel TLB miss repair, registered fixups, and unrecoverable conditions. Medium interrupt vectors remap higher-level interrupts to level-1-style exception dispatch. Window overflow/underflow vectors spill/fill register windows at fixed 64-byte spacing.

State and persistence: Uses special registers `excsave1`, `depc`, `exccause`, `ps`, `epcN`, and window registers; reads/writes exception-table scratch fields such as KSTK, FIXUP, and DOUBLE_SAVE; writes user/kernel stack exception frames.

Dependencies and integration: Requires exact offsets from `asm-offsets.h`, table initialization from `traps.c`, linker placement from `vmlinux.lds.S`, page-fault fast paths, TLB refill handling, and Xtensa window ABI conventions.

Risks: Vector code cannot use literals in critical paths; size/alignment contracts are strict; double-exception fixup state is intentionally fragile; any mismatch with `struct exc_table` offsets or linker vector addresses causes early fatal faults.

Test signals: Boot with relocated and merged vectors, user/kernel faults, window overflow/underflow stress, double exceptions from user access and vmalloc TLB misses, debug interrupts, and high interrupt levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/vectors.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/vmlinux.lds.S

Purpose: Xtensa kernel linker script defining image entry, section layout, vector placement/relocation metadata, init/data/BSS layout, XIP layout, and Xtensa-specific metadata sections.

Important APIs, types, and functions: `OUTPUT_ARCH(xtensa)`, `ENTRY(_start)`, `jiffies` aliasing, `MERGED_VECTORS`, `RELOCATE_ENTRY`, `SECTION_VECTOR4`, `SECTION_VECTOR2`, vector section symbols, `__boot_reloc_table_start/end`, `__tagtable_begin/end`, and XIP symbols.

Control flow: Lays out text from `KERNELOFFSET`, optionally merges vectors into `.text` at vector virtual addresses, emits rodata/data/init/percpu sections, records relocation triples for vectors/XIP/secondary reset, emits separate output vector sections when relocation is needed, aligns init end and BSS, and preserves `.xt.prop/.xt.insn/.xt.lit`.

State and persistence: Defines the symbols consumed by boot code, setup memory reservation, vector relocation, KASAN/layout logging, init freeing, and XIP runtime relocation.

Dependencies and integration: Integrates with generic `asm-generic/vmlinux.lds.h`, Xtensa core/vector address macros, `setup.c` section reservations, `vectors.S` input sections, boot relocation code, and XIP configuration.

Risks: Vector address/alignment errors break exception dispatch before diagnostics; relocation table order must match boot copier expectations; XIP `LOAD_OFFSET` arithmetic is sensitive; `jiffies` offset differs by endian.

Test signals: Link successful kernels for merged and relocated vectors, inspect `System.map` vector symbols, boot XIP/non-XIP variants, verify section reservations, and confirm `.taglist` bootparam parser range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/xtensa_ksyms.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/xtensa_ksyms.c

Purpose: Exports small Xtensa atomic helper symbols used by compiler-generated code or modules.

Important APIs, types, and functions: `__sync_fetch_and_and_4()` and `__sync_fetch_and_or_4()`, both exported with `EXPORT_SYMBOL`.

Control flow: Each helper casts the pointer to `atomic_t *` and delegates to `atomic_fetch_and()` or `atomic_fetch_or()`, returning the previous value to match GCC `__sync_fetch_and_*` semantics.

State and persistence: Mutates the 32-bit memory word addressed by the caller atomically; no internal state is maintained.

Dependencies and integration: Depends on Linux atomic primitives and module symbol export. Complements Xtensa toolchain code generation for configurations where libgcc-style atomic builtins may be emitted.

Risks: Only 32-bit `and` and `or` helpers are provided here; callers must pass properly aligned atomic-compatible storage. Type punning assumes Linux atomic layout matches an unsigned int word.

Test signals: Module build/load using GCC sync builtins, atomic operation litmus tests, and modpost symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/xtensa_ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/Makefile

Purpose: Selects Xtensa architecture library objects for kernel linking.

Important APIs, types, and functions: `lib-y` includes memory, checksum, compiler helper, usercopy, and string-user routines; `lib-$(CONFIG_ARCH_HAS_STRNCPY_FROM_USER)` adds `strncpy_user.o`; `lib-$(CONFIG_PCI)` adds `pci-auto.o`.

Control flow: Kbuild compiles the listed objects into the architecture library. Optional objects are selected by config symbols so PCI autoconfiguration and `strncpy_from_user` support are only linked when needed.

State and persistence: No runtime state; it controls link-time availability of exported symbols like `memcpy`, `memset`, arithmetic helpers, cache/user copy helpers, and PCI scan helpers.

Dependencies and integration: Integrated by arch kbuild into the kernel image and module symbol namespace; assembly files depend on Xtensa core feature macros.

Risks: Missing helper objects can lead to unresolved compiler-generated symbols; optional string-user coverage must match `asm/uaccess.h` expectations; architecture feature variants must compile across cores with and without hardware multiply/divide/loops.

Test signals: All Xtensa defconfig builds, module link checks for exported helpers, PCI-enabled build, and `CONFIG_ARCH_HAS_STRNCPY_FROM_USER` toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/ashldi3.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/ashldi3.S

Purpose: Implements exported 64-bit arithmetic left shift helper `__ashldi3` for Xtensa.

Important APIs, types, and functions: `__ashldi3`, endian-dependent high/low word register aliases, `ssl`, `src`, `sll`, `abi_entry_default`, `abi_ret_default`, and `EXPORT_SYMBOL`.

Control flow: For shifts below 32, it uses shift-left plus `src` to combine high and low words. For shifts of 32 or more, it shifts the low word into the high word and zeros the low word.

State and persistence: Pure register computation, no memory state.

Dependencies and integration: Used by compiler-generated 64-bit shift operations and modules; depends on Xtensa shift amount register behavior and ABI register conventions.

Risks: Endian word assignment must match C 64-bit argument/return ABI; edge cases around shift counts near 32 are the primary correctness risk.

Test signals: Compiler runtime tests for signed/unsigned 64-bit left shifts at counts 0, 1, 31, 32, 33, and 63 on big- and little-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/ashldi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/ashrdi3.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/ashrdi3.S

Purpose: Implements exported 64-bit arithmetic right shift helper `__ashrdi3`.

Important APIs, types, and functions: `__ashrdi3`, endian-dependent `uh/ul`, `ssr`, `src`, `sra`, `srai`, ABI macros, and `EXPORT_SYMBOL`.

Control flow: For counts below 32, shifts the high word arithmetically and combines high/low with `src`. For counts at least 32, shifts the high word into the low result and sign-fills the high result.

State and persistence: Register-only arithmetic helper.

Dependencies and integration: Provides libgcc-compatible helper behavior for signed 64-bit right shifts emitted by the compiler and used by modules.

Risks: Sign extension and endian high/low mapping are critical; C semantics for large shift counts depend on compiler lowering assumptions.

Test signals: Signed 64-bit shift tests for positive and negative values across counts around 31/32 and endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/ashrdi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/bswapdi2.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/bswapdi2.S

Purpose: Implements exported 64-bit byte swap helper `__bswapdi2`.

Important APIs, types, and functions: `__bswapdi2`, `ssai`, `srli`, repeated `src` byte rotation/extraction sequence, ABI macros, and `EXPORT_SYMBOL`.

Control flow: Reverses byte order within each 32-bit half, then swaps the two halves by moving the transformed original low word to the high return register and vice versa.

State and persistence: Pure register transform.

Dependencies and integration: Used by compiler builtins or kernel byteorder operations when a helper call is emitted.

Risks: Return register order must match endian ABI; no memory fault risk, but subtle byte permutation bugs affect networking/storage data interpretation.

Test signals: `__builtin_bswap64` tests and kernel byteorder self-tests for values with distinct bytes on both endian configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/bswapdi2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/bswapsi2.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/bswapsi2.S

Purpose: Implements exported 32-bit byte swap helper `__bswapsi2`.

Important APIs, types, and functions: `__bswapsi2`, `ssai`, `srli`, `src`, ABI macros, and `EXPORT_SYMBOL`.

Control flow: Uses shift/merge instructions to reverse the four bytes in `a2` and returns the result in `a2`.

State and persistence: Register-only helper.

Dependencies and integration: Supports compiler-generated `bswap32` operations and kernel byteorder helpers.

Risks: Incorrect byte ordering would corrupt protocol and disk metadata conversions; otherwise the routine is small and deterministic.

Test signals: `__builtin_bswap32` and byteorder tests with asymmetric values such as `0x01234567`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/bswapsi2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/checksum.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/checksum.S

Purpose: Provides optimized IP/TCP/UDP checksum routines for Xtensa.

Important APIs, types, and functions: `csum_partial()`, `csum_partial_copy_generic()`, `ONES_ADD`, exception table `EX()` annotations, `.fixup` handler returning zero, and exported symbols.

Control flow: `csum_partial()` handles 4-byte aligned, 2-byte aligned, and odd-address buffers with chunked loops and one's-complement carry folding. `csum_partial_copy_generic()` copies while accumulating checksum, selecting fast 4-byte aligned path, 2-byte path, or byte path, and uses exception fixups for faulting loads/stores.

State and persistence: Reads source buffers, writes destination in copy variant, and returns accumulated checksum. On exception in copy variant, returns zero from fixup rather than partial state.

Dependencies and integration: Used by networking checksum paths and user/kernel copy checksum operations; depends on Xtensa alignment behavior, loop-option macros, endian-specific byte placement, and exception table machinery.

Risks: `csum_partial()` documents that 1-byte alignment is very slow and certain alignments are expected; checksum correctness is endian-sensitive; fault fixup behavior must match callers' error expectations.

Test signals: Network checksum self-tests, packet transmit/receive under TCP/UDP, odd/2/4-byte aligned buffers, fault injection for copy source/destination, and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/checksum.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/divsi3.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/divsi3.S

Purpose: Implements exported signed 32-bit division helper `__divsi3`.

Important APIs, types, and functions: `__divsi3`, hardware `quos` path, software absolute-value/normalize/subtract loop, `do_nsau`, loop-option macros, `ill` plus `DIV0` marker, and `EXPORT_SYMBOL`.

Control flow: Uses hardware divide when available. Otherwise computes sign, converts operands to unsigned magnitudes, handles divisor 0/1 and dividend<divisor special cases, performs shift-subtract division, reapplies sign, and triggers an illegal instruction with a marker for divide-by-zero.

State and persistence: Register-only arithmetic; divide-by-zero transfers control to exception handling.

Dependencies and integration: Compiler-emitted signed division, `traps.c` divide-by-zero recognition, and Xtensa core feature macros for DIV32/NSA/LOOPS.

Risks: Software path correctness across `INT_MIN`, divisor zero, and normalization; marker must remain recognizable by `check_div0()`.

Test signals: Signed division tests including positive/negative pairs, `INT_MIN / -1`, divisor one, divisor zero trap, and builds without DIV32/NSA/LOOPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/divsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/lshrdi3.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/lshrdi3.S

Purpose: Implements exported 64-bit logical right shift helper `__lshrdi3`.

Important APIs, types, and functions: `__lshrdi3`, endian-dependent high/low aliases, `ssr`, `src`, `srl`, ABI macros, and `EXPORT_SYMBOL`.

Control flow: For counts below 32, combines high and low words with a logical shift. For counts of 32 or more, shifts the high word into the low result and zeros the high result.

State and persistence: Register-only helper.

Dependencies and integration: Supports compiler-emitted unsigned 64-bit right shifts in kernel and modules.

Risks: Edge counts around 32 and endian word mapping are the meaningful hazards.

Test signals: Unsigned 64-bit right shift tests at counts 0, 1, 31, 32, 33, 63 with high bits set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/lshrdi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/memcopy.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/memcopy.S

Purpose: Provides optimized `memcpy`/`memmove` implementations for Xtensa and exports both internal and standard symbols.

Important APIs, types, and functions: `__memcpy`, weak `memcpy`, `__memmove`, weak `memmove`, byte-copy paths, aligned word-copy paths, unaligned-source `SRC` paths, backward-copy paths, and exported symbols.

Control flow: `memcpy` aligns destination with byte/halfword copies, then chooses word-aligned fast loops or unaligned-source merge loops, finishing with 8/4/2/1 byte tails. `memmove` detects overlap; non-overlap falls into memcpy logic, while overlap copies backward with analogous aligned and unaligned paths.

State and persistence: Writes destination memory and returns original destination. No exception fixup is used for normal kernel memory copies.

Dependencies and integration: Used broadly by the kernel and modules; depends on Xtensa load/store alignment behavior, optional loop instructions, `__src_b` endian-aware merge macro, and ABI macros.

Risks: Comments note IRAM/IROM special handling is not implemented; overlap detection must be exact; simulator alignment checks force conservative unaligned handling; copying faulting addresses is not protected here.

Test signals: libc-style memcpy/memmove tests across alignments, lengths, overlap directions, zero length, simulator alignment modes, and memory regions with device-like restrictions if relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/memcopy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/memset.S

Purpose: Implements optimized Xtensa `memset` and exports both `__memset` and weak `memset`.

Important APIs, types, and functions: `__memset`, weak `memset`, destination alignment paths, 16-byte word loops, byte fallback loop, exception `EX()` annotations, `.fixup` returning zero, and exported symbols.

Control flow: Replicates the low byte of `c` into a 32-bit word, aligns destination by 1/2 byte stores when large enough, writes 16-byte chunks, and handles 8/4/2/1 byte tails. Short unaligned writes use byte loop.

State and persistence: Writes destination memory and returns original destination on success; fixup path returns zero if an annotated store faults.

Dependencies and integration: Core kernel memory primitive, exception table macros, Xtensa loop support, and ABI conventions.

Risks: Standard `memset` callers may not expect a zero return on fault, but kernel faulting uses should normally be through safe helpers; alignment and tail handling must not overwrite outside range.

Test signals: KUnit/lib string tests, all alignments and lengths, fault-injection on annotated stores, and module symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/modsi3.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/modsi3.S

Purpose: Implements exported signed 32-bit modulo helper `__modsi3` and, when needed, a normalization lookup table.

Important APIs, types, and functions: `__modsi3`, hardware `rems` path, software shift-subtract remainder path, `do_abs`, `do_nsau`, `ill` plus `DIV0`, `__nsau_data` for no-NSA cores, and `EXPORT_SYMBOL`.

Control flow: Uses hardware remainder when present. Software path records dividend sign, operates on absolute magnitudes, handles divisor zero/one and special cases, subtracts shifted divisor until remainder is found, then reapplies dividend sign.

State and persistence: Register-only except optional read-only `__nsau_data`; divide-by-zero traps via illegal instruction marker.

Dependencies and integration: Compiler-emitted modulo operations, trap divide-by-zero detection, core feature macros, and shared `__nsau_data` conventions.

Risks: Remainder sign must follow C semantics; divisor zero marker coupling to traps; table must be present on cores without NSA.

Test signals: Signed modulo tests with negative dividend/divisor, divisor one/zero, small and large values, and no-DIV32/no-NSA builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/modsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/mulsi3.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/mulsi3.S

Purpose: Implements exported signed 32-bit multiply helper `__mulsi3` across Xtensa cores with different multiply capabilities.

Important APIs, types, and functions: `__mulsi3`, hardware `mull`, MUL16 and MAC16 paths, software add/shift loop, `do_addx{2,4,8}` macros, ABI macros, and `EXPORT_SYMBOL`.

Control flow: Selects the best implementation at compile time: direct 32-bit multiply, split 16-bit partial products, MAC16 accumulator sequence, or software nibble-at-a-time multiplication after normalizing signs and choosing smaller multiplier.

State and persistence: Register-only arithmetic.

Dependencies and integration: Compiler-emitted multiplication on cores without full hardware support and module symbols; depends on core feature macros.

Risks: Software sign handling and partial-product carries are correctness hotspots; performance varies sharply by hardware feature set.

Test signals: Multiplication tests for signed extremes, zero, one, negative pairs, overflow wraparound behavior, and builds for MUL32/MUL16/MAC16/no-mul cores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/mulsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/pci-auto.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/pci-auto.c

Purpose: Provides a legacy PCI bus autoconfiguration scanner for Xtensa host controllers.

Important APIs, types, and functions: `pciauto_bus_scan()`, `pciauto_setup_bars()`, `pciauto_setup_irq()`, `pciauto_prescan_setup_bridge()`, `pciauto_postscan_setup_bridge()`, static `pciauto_dev`, `pciauto_bus`, and upper I/O/memory allocation cursors.

Control flow: Initializes allocation cursors from controller resources, scans devfn values, skips host bridge, handles multifunction devices, sizes/writes BARs downward from upper limits, maps IRQ pins, recurses into PCI-to-PCI bridges after temporary bus numbering, then programs bridge windows and command bits.

State and persistence: Writes PCI config space, mutates static allocation cursors and synthetic `pci_dev/pci_bus` objects, and returns highest subordinate bus number.

Dependencies and integration: Depends on `struct pci_controller` config ops/resources/map_irq from Xtensa PCI bridge support, generic PCI config accessors, and PCI class/header constants.

Risks: Static globals make concurrent scans unsafe; 64-bit BARs are forced below 4GB; bridge window arithmetic allocates downward and can underflow if resources are undersized; modern PCI core expectations may differ.

Test signals: PCI-enabled board boot, endpoint BAR assignment, bridge recursion, multifunction devices, IRQ line programming, resource exhaustion cases, and comparison with `lspci -vv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/pci-auto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/strncpy_user.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/strncpy_user.S

Purpose: Copies a NUL-terminated string from userspace into kernel memory with bounded length and fault handling.

Important APIs, types, and functions: `__strncpy_user`, endian byte masks, aligned and unaligned copy paths, exception fixup labels `10`/`11`, and `EXPORT_SYMBOL`.

Control flow: Handles zero length, aligns source with initial byte copies, chooses fast word path when destination is word-aligned, scans each word for zero bytes while storing only up to the terminator, and falls back to byte copy for unaligned destinations. On fault, returns `-EFAULT`.

State and persistence: Writes destination bytes until NUL, length exhaustion, or fault. Returns copied string length excluding NUL per code comments, `len` when full, or `-EFAULT`.

Dependencies and integration: Used by `strncpy_from_user` architecture support; depends on exception table macros, endian masks, and user access fault fixups.

Risks: Partial destination contents remain on fault; zero-byte detection is endian-specific; destination unaligned path is simpler but slower; comments mention possible future clearing behavior not implemented.

Test signals: Usercopy string tests with aligned/unaligned source and destination, NUL at each byte position, exact-length truncation, zero length, and faulting user pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/strncpy_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/strnlen_user.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/strnlen_user.S

Purpose: Computes bounded userspace string length including the trailing NUL, returning zero on fault.

Important APIs, types, and functions: `__strnlen_user`, endian masks, alignment prologue, word scanning loop, byte-position zero handlers, fault fixup returning zero, and `EXPORT_SYMBOL`.

Control flow: Adjusts pointer bookkeeping to use word loads, handles odd and halfword-aligned starts, scans full words for zero bytes, checks remaining bytes, and returns distance from original pointer including NUL when found or bounded length when exhausted.

State and persistence: Read-only userspace access; no internal state.

Dependencies and integration: User access exception table, string/usercopy APIs, Xtensa endian and alignment behavior.

Risks: The aligned loop performs a word load for remaining checks, so exception fixup must protect boundary cases; return convention differs from plain `strlen` by including NUL and using zero for fault.

Test signals: `strnlen_user` tests for all alignments, NUL positions, no NUL within bound, faulting page at first byte and at boundary, and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/strnlen_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/udivsi3.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/udivsi3.S

Purpose: Implements exported unsigned 32-bit division helper `__udivsi3`.

Important APIs, types, and functions: `__udivsi3`, hardware `quou` path, software normalization and shift-subtract quotient loop, `do_nsau`, divide-by-zero `ill`/`DIV0` marker, and `EXPORT_SYMBOL`.

Control flow: Uses hardware divide if available. Otherwise handles divisor zero/one, normalizes dividend and divisor by leading-zero count, shifts divisor, accumulates quotient bits through subtract/shift loop, and returns 0/1 special cases when dividend is smaller or comparable.

State and persistence: Register-only, except divide-by-zero trap side effect.

Dependencies and integration: Compiler-emitted unsigned division and trap handler marker recognition.

Risks: Divide-by-zero handling depends on illegal instruction trap marker; no-DIV32 performance and loop correctness are feature-sensitive.

Test signals: Unsigned division tests for zero divisor trap, divisor one, dividend<divisor, powers of two, high-bit operands, and no-DIV32 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/udivsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/umodsi3.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/umodsi3.S

Purpose: Implements exported unsigned 32-bit modulo helper `__umodsi3`.

Important APIs, types, and functions: `__umodsi3`, hardware `remu` path, software normalization/subtract loop, `do_nsau`, divide-by-zero marker, and `EXPORT_SYMBOL`.

Control flow: Uses hardware remainder if available. Software path handles divisor zero/one, normalizes divisor to dividend, repeatedly subtracts shifted divisor where possible, performs final subtraction if needed, and returns the remainder.

State and persistence: Register-only arithmetic; divisor zero raises an illegal instruction for trap conversion.

Dependencies and integration: Compiler-emitted unsigned remainder and `traps.c` DIV0 recognition.

Risks: Boundary cases around divisor zero, divisor one, and high-bit operands; performance on cores lacking divide and loop instructions.

Test signals: Unsigned modulo tests for edge operands, divisor zero trap, powers of two, dividend<divisor, and no-DIV32/no-LOOPS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/umodsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/umulsidi3.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/umulsidi3.S

Purpose: Implements exported unsigned 32x32-to-64 multiply helper `__umulsidi3`.

Important APIs, types, and functions: `__umulsidi3`, endian-dependent high/low return words, `mull/muluh` fast path, MUL16/MUL32/MAC16 partial-product paths, no-multiply helper `.Lmul_mulsi3`, CALL0 and windowed ABI save/restore, and `EXPORT_SYMBOL`.

Control flow: With `MUL32_HIGH`, computes low and high directly. Otherwise splits inputs into 16-bit halves, computes partial products, accumulates carries, and returns 64-bit product. On cores without multiply hardware, calls an internal nibble-at-a-time helper with ABI-specific calling conventions.

State and persistence: Register and stack save/restore only; no global state.

Dependencies and integration: Compiler-generated widening multiplication, floating-point/helper code, core feature macros, and ABI conventions.

Risks: Carry propagation and ABI register preservation are complex; no-multiply CALL0 path is not a normal leaf and uses custom helper conventions; endian return ordering must be correct.

Test signals: Widening multiply tests for high/low halves, overflow products, zero/max operands, CALL0/windowed builds, and cores with each multiply feature combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/umulsidi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/usercopy.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/lib/usercopy.S

Purpose: Implements low-level `__xtensa_copy_user()` for copying between kernel and user address spaces with exception fixups.

Important APIs, types, and functions: `__xtensa_copy_user`, aligned/unaligned destination paths, unaligned-source merge path, byte-copy fallback, exception fixup label `10`, and `EXPORT_SYMBOL`.

Control flow: Saves original length, aligns destination if profitable, uses fast 16-byte loops for aligned source/destination, uses `SRC` merge after aligning unaligned source, handles 8/4/2/1 byte tails, and returns zero on success. On fault, fixup computes `bytes_not_copied = original_len - (current_dst - original_dst)`.

State and persistence: Writes destination memory partially or completely; returns residual byte count. It intentionally remains separate from HAL `memcopy.S` so user fault behavior is not lost during HAL replacement.

Dependencies and integration: Used by Xtensa `copy_{to,from}_user` wrappers, exception tables, ABI macros, loop feature macros, and user access fault handling.

Risks: Partial copies must report precise residual bytes; unaligned-source path adjusts pointers for simulator warnings; CALL0/no-loop path uses a small stack slot for saved offset; combining with normal memcpy would break fault semantics.

Test signals: Usercopy tests over all alignments/lengths, fault at each segment, residual byte correctness, hardened usercopy, and no-loop/CALL0 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/lib/usercopy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/Makefile

Purpose: Selects Xtensa memory-management objects and disables KASAN instrumentation for sensitive early/fault/MMU files.

Important APIs, types, and functions: `obj-y := init.o misc.o`, `obj-$(CONFIG_PFAULT)`, `obj-$(CONFIG_MMU)`, `obj-$(CONFIG_HIGHMEM)`, `obj-$(CONFIG_KASAN)`, and `KASAN_SANITIZE_* := n`.

Control flow: Always builds memory init and assembly helpers; conditionally builds page fault, cache/ioremap/mmu/tlb, highmem, and KASAN initialization objects based on configuration.

State and persistence: No runtime state; controls which MM symbols exist in the final image.

Dependencies and integration: Kbuild, architecture config symbols, and early boot/fault code that must run before KASAN is fully initialized.

Risks: Instrumenting page-fault or MMU setup with KASAN could recurse before shadow mappings are ready; missing optional objects would break config-specific APIs.

Test signals: Build matrix for MMU/noMMU, PFAULT, HIGHMEM, KASAN, and fault-path boot tests with KASAN enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/cache.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/cache.c

Purpose: Maintains Xtensa D-cache aliasing and I-cache/D-cache coherency for user pages, page cache pages, MMU updates, and user-page copying.

Important APIs, types, and functions: `clear_user_highpage()`, `copy_user_highpage()`, `flush_dcache_folio()`, `local_flush_cache_range()`, `local_flush_cache_page()`, `update_mmu_cache_range()`, `copy_to_user_page()`, `copy_from_user_page()`, `PG_arch_1`, and alias helper functions.

Control flow: For aliasing caches, highpage clear/copy maps pages at color-matched temporary aliases, invalidates conflicting kernel mappings, marks folio cache state, and uses assembly alias helpers. `flush_dcache_folio()` either defers flushing with `PG_arch_1` for unmapped page-cache pages or flushes/invalidate aliases immediately. `update_mmu_cache_range()` flushes stale TLB entries and resolves pending cache coherency before mapping a folio.

State and persistence: Uses `PG_arch_1` differently depending on aliasing mode: dirty/deferred flush for aliasing, clean I/D coherence marker for non-aliasing executable pages. Temporarily disables preemption around TLB temporary alias use.

Dependencies and integration: Depends on `mm/misc.S` cache/TLB alias routines, folio/page cache state, TLB flush API, VM flags, highmem mapping, and SMP wrappers in `smp.c`.

Risks: Misinterpreting `PG_arch_1` causes stale instruction fetches or D-cache alias corruption; preemption must be disabled while temporary TLB aliases are active; whole-cache range flushes are blunt and expensive.

Test signals: Executable mmap after writes, page-cache mmap sharing, highmem user pages, alias-color stress with `SHMLBA`, SMP cache flushes, and self-modifying/user text tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/fault.c

Purpose: Handles Xtensa page faults, vmalloc page-table synchronization, signal delivery for bad user accesses, and kernel fault fixups/oops.

Important APIs, types, and functions: `do_page_fault()`, `vmalloc_fault()`, `bad_page_fault()`, `lock_mm_and_find_vma()`, `handle_mm_fault()`, and exception-table lookup.

Control flow: Kernel faults above `TASK_SIZE` attempt `vmalloc_fault()` to copy top-level kernel page table entries from `init_mm`. Faults without context or with disabled handlers go to `bad_page_fault()`. User/kernel faults are classified as write/execute/read from `exccause`, VMA permissions are checked, `handle_mm_fault()` is invoked with retry handling, and failures generate `SIGSEGV`, `SIGBUS`, OOM handling, or kernel oops. Kernel faults first search exception tables and redirect PC to fixup if found.

State and persistence: Updates current MM page tables for vmalloc synchronization, may install PTEs via generic MM fault handling, and may mutate `regs->pc` for exception fixup.

Dependencies and integration: Tied to exception causes from traps/vectors, generic MM fault APIs, perf page-fault events, `uaccess` exception tables, and cache/TLB update callbacks.

Risks: Fault classification is architecture-cause dependent; vmalloc synchronization must validate every page-table level; retry path relies on lock release semantics; kernel bad faults terminate the task or panic through `die()`.

Test signals: User read/write/exec faults, COW, VM_FAULT_RETRY, OOM, SIGBUS mappings, vmalloc access from kernel, uaccess exception fixups, and kernel NULL/bad address oops output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/highmem.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/highmem.c

Purpose: Initializes highmem/kmap support and cache-color-aware local kmap fixmap indices for aliasing D-caches.

Important APIs, types, and functions: `last_pkmap_nr_arr`, `pkmap_map_wait_arr`, `kmap_waitqueues_init()`, `kmap_local_map_idx()`, `kmap_local_unmap_idx()`, and `kmap_init()`.

Control flow: For aliasing D-caches, initializes per-color wait queues and maps kmap types/CPU/color to reversed fixmap indices because fixmap grows top-down. `kmap_init()` verifies PKMAP does not overlap temporary TLB mapping space and initializes wait queues.

State and persistence: Global per-color pkmap cursor/waitqueue arrays persist for highmem mapping management.

Dependencies and integration: Depends on `DCACHE_WAY_SIZE`, `DCACHE_N_COLORS`, `DCACHE_ALIAS`, highmem/fixmap constants, and `mmu.c` fixedrange initialization.

Risks: Wrong color-to-index mapping can create D-cache aliases; layout overlap with `TLBTEMP_BASE_1` is fatal at build time; CPU/type indexing must match generic kmap local expectations.

Test signals: HIGHMEM builds, kmap/kunmap local stress with different PFN colors, page cache highmem I/O, and build-time overlap checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/highmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/init.c

Purpose: Initializes physical memory accounting, zones, VM layout reporting, `memmap=` parsing, and MMU protection mappings.

Important APIs, types, and functions: `bootmem_init()`, `print_vm_layout()`, `arch_zone_limits_init()`, `zones_init()`, `parse_memmap_one()`, `parse_memmap_opt()`, `protection_map`, and `DECLARE_VM_GET_PAGE_PROT`.

Control flow: `bootmem_init()` reserves unusable low memory/page zero, scans reserved FDT memory, validates DRAM, computes PFN bounds, runs early memtest, sets memblock allocation limit, reserves CMA, and dumps memblock. `memmap=` parsing adds or reserves regions with `size@addr`, `size$addr`, or reserves from `size` to the end. Zone setup reports layout and sets normal/highmem limits.

State and persistence: Mutates memblock reservations and memory regions, global PFN bounds, zone limits, and page protection lookup table.

Dependencies and integration: Called from `setup_arch()`, uses FDT reserved memory, DMA contiguous reservation, early params, section symbols, highmem constants, and generic VM protection APIs.

Risks: Bad memmap syntax can silently leave memory unchanged except warnings; reserving `mem_size, -mem_size` depends on unsigned wrap semantics; PFN calculations must respect `PHYS_OFFSET` and `MAX_LOW_PFN`.

Test signals: Boot memory map logs, `memmap=` add/reserve cases, no-memory panic path, highmem zone setup, CMA reservation, and executable/non-executable mmap protection bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/ioremap.c

Purpose: Provides Xtensa `ioremap_prot()` and `iounmap()` wrappers around generic ioremap while preserving fixed KIO mappings.

Important APIs, types, and functions: `ioremap_prot()`, `iounmap()`, `generic_ioremap_prot()`, `generic_iounmap()`, `XCHAL_KIO_CACHED_VADDR`, `XCHAL_KIO_BYPASS_VADDR`, and `XCHAL_KIO_SIZE`.

Control flow: `ioremap_prot()` converts physical address to PFN, warns if it is normal RAM, and delegates to generic ioremap. `iounmap()` checks whether the address lies inside Xtensa's statically mapped cached/bypass KIO windows and returns without unmapping those; other addresses go to generic unmap.

State and persistence: Creates and destroys generic vmalloc/ioremap mappings; static KIO mappings persist and are intentionally not unmapped.

Dependencies and integration: Linux I/O mapping APIs, Xtensa KIO virtual windows, page table support, and cache attributes in `asm/io.h`.

Risks: Mapping normal RAM as I/O is warned but not blocked; address arithmetic must avoid false positives in KIO range checks; callers must choose correct cache attributes.

Test signals: Device driver ioremap/iounmap, warning on RAM PFNs, repeated iounmap of KIO window, and access to cached/bypass KIO addresses after attempted unmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/kasan_init.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/kasan_init.c

Purpose: Initializes Xtensa KASAN shadow mappings during early boot and switches from shared early shadow to real writable shadow pages.

Important APIs, types, and functions: `kasan_early_init()`, `populate()`, `kasan_init()`, `kasan_early_shadow_pte`, `kasan_early_shadow_page`, and `kasan_init_generic()`.

Control flow: Early init maps the entire shadow range through the shared early shadow page. Full init validates address constants, allocates page-table entries and backing pages for VMALLOC-to-KSEG shadow coverage, flushes TLBs, zeroes the new shadow, write-protects the early shadow page, resets it, clears current task KASAN depth, and enables generic KASAN reporting.

State and persistence: Allocates permanent shadow page tables/pages via memblock, updates PMD/PTE entries, changes early shadow PTE protections, flushes TLBs, and initializes task KASAN depth.

Dependencies and integration: Requires early MMU/page table setup, memblock allocation, KASAN generic code, Xtensa shadow address constants, and disabled KASAN instrumentation for this file.

Risks: Any shadow range mismatch breaks memory instrumentation; allocation failures panic; this code must not be KASAN-instrumented before KASAN is ready; TLB flushes are required after remapping.

Test signals: KASAN-enabled boot, intentional out-of-bounds report after boot, VMALLOC shadow coverage, and early boot without recursive KASAN faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/kasan_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/misc.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/misc.S

Purpose: Provides page clear/copy and low-level cache/TLB maintenance assembly helpers, including temporary alias mappings for cache-color handling.

Important APIs, types, and functions: `clear_page`, `copy_page`, `clear_page_alias`, `copy_page_alias`, `__flush_invalidate_dcache_page_alias`, `__invalidate_dcache_page_alias`, `__invalidate_icache_page_alias`, `__invalidate_icache_page`, `__invalidate_dcache_page`, `__flush_invalidate_dcache_page`, `__flush_dcache_page`, range/all-cache helpers, and exported range/page symbols.

Control flow: Page clear/copy routines loop over `PAGE_SIZE` in 32-byte chunks. Alias routines create temporary DTLB/ITLB entries for color-matched virtual aliases, perform page or cache operations, then invalidate the temporary entries. Non-alias cache helpers wrap macro-generated cache operations with required `dsync`/`isync`.

State and persistence: Temporarily mutates TLB entries and cache state; writes page memory for clear/copy; exports selected helpers to modules.

Dependencies and integration: Called by `cache.c`, highmem/page-copy paths, SMP cache wrappers, and signal generated-code flushing. Special labels `__tlbtemp_mapping_start/end` identify regions handled specially by TLB miss logic.

Risks: Temporary TLB entries must not survive or be preempted unexpectedly; comments note fast miss handlers reestablish mappings using registers `a6/a7`; sync instructions are required for coherency; label placement matters.

Test signals: Page allocator clear/copy tests, aliasing cache stress, executable page update tests, cache range helpers from modules, and faults inside temporary mapping regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/misc.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/mmu.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/mmu.c

Purpose: Initializes Xtensa MMU state, ASID caches, highmem/fixmap page tables, PKMAP page table, and KIO TLB mappings.

Important APIs, types, and functions: per-CPU `asid_cache`, `init_pmd()`, `fixedrange_init()`, `paging_init()`, `init_mmu()`, and `init_kio()`.

Control flow: Highmem builds allocate low-memory PTE pages for fixmap and pkmap PMDs, clear PTEs, and install PMD entries. `init_mmu()` resets TLBCFG where applicable, initializes KIO, flushes all local TLBs, initializes RASID to first user ASID, and sets PTEVADDR. `init_kio()` writes cached and bypass KIO mappings for spanning-way PTP MMU when DT may update physical base.

State and persistence: Per-CPU ASID cache starts at `ASID_USER_FIRST`; page tables are allocated by memblock; special MMU registers and TLB entries are initialized.

Dependencies and integration: Called from early `init_arch()` and secondary CPU bring-up; depends on TLB helpers, highmem, fixed map constants, DT-derived `xtensa_kio_paddr`, and `initialize_mmu` register helpers.

Risks: Early memblock PTE allocation failure panics; KIO mapping offsets are architecture-specific; failing to reset RASID/PTEVADDR leaves undefined MMU state; highmem layout must avoid temporary mapping overlap.

Test signals: MMU boot on primary and secondary CPUs, highmem/fixmap use, KIO device access, ASID rollover/context tests, and DT KIO base override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/mm/tlb.c

Purpose: Implements local Xtensa TLB flush/update operations and optional debug sanity checking.

Important APIs, types, and functions: `local_flush_tlb_all()`, `local_flush_tlb_mm()`, `local_flush_tlb_range()`, `local_flush_tlb_page()`, `local_flush_tlb_kernel_range()`, `update_mmu_tlb_range()`, `get_pte_for_vaddr()`, `check_tlb_entry()`, and `check_tlb_sanity()`.

Control flow: Full flush iterates all auto-refill ways/entries for I- and D-TLB. MM flush invalidates or reassigns ASIDs depending on whether the mm is active. Range/page flush temporarily switches RASID to the target ASID, invalidates ITLB for executable mappings and DTLB for all, then restores RASID. Kernel range flush either invalidates individual mappings or falls back to full flush.

State and persistence: Mutates TLB entries, per-mm per-CPU ASID state, `mm->context.cpu`, and RASID register. Debug code inspects TLB virtual/translation registers and PTEs.

Dependencies and integration: Used by cache/MM/fault/SMP paths; relies on ASID management in `mmu_context`, Xtensa TLB register helpers, VM flags, and folio refcount/mapcount checks for sanity diagnostics.

Risks: Incorrect RASID switching can invalidate wrong address spaces; range threshold must reflect total TLB entries; debug sanity can BUG on serious inconsistencies; kernel range bounds are architecture-specific.

Test signals: mmap/munmap/mprotect stress, ASID rollover, executable mapping flushes, SMP shootdowns through `smp.c`, DEBUG_TLB_SANITY runs, and kernel vmalloc TLB invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/mm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/Makefile

Purpose: Selects Xtensa platform subdirectories for the build.

Important APIs, types, and functions: `obj-$(CONFIG_XTENSA_PLATFORM_XT2000)`, `obj-$(CONFIG_XTENSA_PLATFORM_ISS)`, and `obj-$(CONFIG_XTENSA_PLATFORM_XTFPGA)`.

Control flow: Kbuild descends into exactly the platform directories enabled by configuration, making their setup and device code available to `platform_setup()`/platform headers.

State and persistence: No runtime state; controls platform object inclusion.

Dependencies and integration: Architecture platform Kconfig, platform-specific `Makefile`s, and generic Xtensa setup hooks.

Risks: Multiple enabled platforms may create duplicate platform symbols if not intended; missing platform selection leaves required hooks unresolved.

Test signals: Build each platform defconfig and verify the expected subdirectory objects are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/Makefile

Purpose: Builds platform support for the Xtensa Instruction Set Simulator.

Important APIs, types, and functions: Always builds `setup.o`; conditionally builds `console.o` for TTY, `network.o` for NET, and `simdisk.o` for simulated block devices.

Control flow: Kbuild includes simulator platform setup unconditionally for ISS and adds optional simulated devices based on kernel features.

State and persistence: No runtime state; controls inclusion of simulator exit/restart, console, network, and block-device support.

Dependencies and integration: ISS platform Kconfig, simulator `simcall` host services, TTY, network, and block subsystems.

Risks: Optional drivers depend on host simcall service availability; enabling devices without simulator support can produce runtime failures even if build succeeds.

Test signals: ISS boot with minimal config, serial console config, `ethX=` tuntap config, and simdisk module/built-in config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/console.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/console.c

Purpose: Provides a single-line ISS serial TTY and optional console backed by simulator host I/O simcalls.

Important APIs, types, and functions: `rs_open()`, `rs_close()`, `rs_write()`, `rs_poll()`, `rs_write_room()`, `rs_init()`, `rs_exit()`, `iss_console_write()`, `iss_console_device()`, `iss_console_init()`, `serial_driver`, `serial_port`, and `serial_timer`.

Control flow: Late init allocates/registers a raw tty driver named `ttyS`, links one port, and starts polling when opened. The poll timer repeatedly calls `simc_poll()`/`simc_read()` on fd 0, pushes received chars into the TTY flip buffer, and reschedules while reads remain valid. Writes call `simc_write()` on fd 1. Console init registers a `ttyS` console if enabled.

State and persistence: Maintains global tty driver/port and polling timer. No hardware FIFO state; host stdio is the backend.

Dependencies and integration: TTY core, console core, timers, ISS `simcall.h`, and simulator host read/write/poll services.

Risks: Polling is timer-driven rather than interrupt-driven; console `device` returns `serial_driver`, which must be initialized for later console use; write path assumes host accepts all bytes.

Test signals: ISS console output during boot, login/input on `ttyS0`, close/open timer behavior, and serial console registration with `CONFIG_SERIAL_CONSOLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/serial.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/serial.h

Purpose: Provides ISS platform serial constants needed by generic serial code.

Important APIs, types, and functions: Header guard `__ASM_XTENSA_ISS_SERIAL_H` and `BASE_BAUD`.

Control flow: No executable control flow; defines `BASE_BAUD 0` because real 8250 baud rates have no meaning on ISS but generic early serial code expects the macro.

State and persistence: No runtime state.

Dependencies and integration: Included by serial/8250 early code or platform serial consumers for ISS builds.

Risks: `BASE_BAUD` being zero is intentional for ISS but would be invalid for real UART programming if reused outside simulator context.

Test signals: ISS builds with 8250 early serial code and no divide-by-zero or missing macro warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall-gdbio.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall-gdbio.h

Purpose: Defines simulator host service numbers and inline call ABI for GDBIO-backed ISS simcalls.

Important APIs, types, and functions: `SYS_open`, `SYS_close`, `SYS_read`, `SYS_write`, `SYS_lseek`, static `errno`, and `__simc()`.

Control flow: `__simc()` loads arguments into specific Xtensa registers (`a2`, `a6`, `a3`, `a4`), executes `break 1, 14`, captures return and errno registers, stores errno, and returns the host result.

State and persistence: Updates a header-local static `errno` variable in each translation unit including it.

Dependencies and integration: Selected by `CONFIG_XTENSA_SIMCALL_GDBIO` through `simcall.h`; used by ISS console/network/simdisk/setup wrappers.

Risks: Register ABI differs from ISS native `simcall`; static header `errno` has translation-unit scope, which is acceptable for simple simulator drivers but not a global libc-style errno; only a small syscall set is defined.

Test signals: GDBIO ISS boot, host open/read/write/lseek/close behavior, and errno reporting on failed host operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall-gdbio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall-iss.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall-iss.h

Purpose: Defines native ISS host service numbers, select constants, argument query calls, and inline `simcall` ABI.

Important APIs, types, and functions: `SYS_*` constants for file, process, socket, select, ioctl, and argv services; `XTISS_SELECT_ONE_*`; static `errno`; and `__simc()`.

Control flow: `__simc()` places arguments in `a2`-`a5`, executes the `simcall` instruction, records errno from `a3`, and returns result from `a2`.

State and persistence: Updates translation-unit-local `errno` after every simcall.

Dependencies and integration: Included by `simcall.h` under `CONFIG_XTENSA_SIMCALL_ISS`; consumed by ISS setup, console, net, and simdisk code.

Risks: Host service numbers are simulator ABI, not Linux syscall numbers; static header `errno` is per C file; some service constants are documented as unavailable or not fully compatible.

Test signals: Native ISS boot, command-line argv import, file I/O, tuntap ioctl/poll if supported, and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall-iss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall.h

Purpose: Provides common inline wrappers for ISS simulator host services independent of the selected backend ABI.

Important APIs, types, and functions: Includes `simcall-iss.h` or `simcall-gdbio.h`; wrappers `simc_exit`, `simc_open`, `simc_close`, `simc_ioctl`, `simc_read`, `simc_write`, `simc_poll`, `simc_lseek`, `simc_argc`, `simc_argv_size`, and `simc_argv`.

Control flow: Each wrapper invokes `__simc()` with backend-defined service numbers. Optional services compile to `WARN_ONCE()` plus failure defaults when the selected backend lacks the service.

State and persistence: Wrapper calls may update backend-local `errno` and host-side file/device state.

Dependencies and integration: Central dependency for ISS platform setup, console, network, and simdisk. Requires exactly one compatible simcall backend config for useful operation.

Risks: Pointer arguments are cast to `int`, matching 32-bit Xtensa assumptions; unsupported wrappers fail at runtime with warnings; backend differences affect register ABI and service availability.

Test signals: Build both simcall backend variants, run ISS console/file/network/simdisk operations, and verify warnings for unsupported services.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/network.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/network.c

Purpose: Implements ISS virtual Ethernet devices backed by host tuntap interfaces through simulator simcalls.

Important APIs, types, and functions: `struct iss_net_private`, `struct iss_net_ops`, `tuntap_probe/open/close/read/write/poll`, `iss_net_rx()`, `iss_net_poll()`, `iss_net_open()`, `iss_net_close()`, `iss_net_start_xmit()`, `iss_net_configure()`, `iss_net_setup()`, and `iss_net_init()`.

Control flow: Early `ethX=` command-line parsing records requested devices in a memblock list. Device init allocates `net_device`, parses `tuntap,[mac],dev`, registers a platform device and netdev. Open attaches host `/dev/net/tun`, drains pending RX, and starts a poll timer. RX polls host fd, allocates skb, reads packet, sets protocol, updates stats, and injects with `netif_rx()`. TX writes skb data to host fd and updates stats.

State and persistence: Maintains per-device host fd, timers, net stats under spinlock, platform device, and command-line init list.

Dependencies and integration: Linux netdev/platform/timer APIs, host TUN/TAP via simcall open/ioctl/read/write/poll, command-line `__setup`, and MAC address helpers.

Risks: Polling rather than interrupts limits performance; MTU changes are rejected; host read errors close the device; command-line parser mutates strings and uses memblock allocations; simcall backend must support ioctl/select/open.

Test signals: Boot with `eth0=tuntap,<mac>,tap0`, interface registration, ping/DHCP on host tap, RX/TX stats, invalid MAC/device args, host fd failure, and close/reopen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/network.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/setup.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/setup.c

Purpose: Provides ISS platform setup, command-line import from simulator argv, panic exit, restart, and power-off handlers.

Important APIs, types, and functions: `iss_power_off()`, `iss_restart()`, `iss_panic_event()`, `iss_panic_block`, and `platform_setup()`.

Control flow: `platform_setup()` queries simulator argc/argv size, imports argv into static buffers when more than one argument is present, joins argv[1..] into the kernel command line, registers a panic notifier that exits host with status 1, and registers restart/poweroff sys_off handlers. Restart calls `cpu_reset()`, poweroff calls `simc_exit(0)`.

State and persistence: Static initdata argv/cmdline buffers hold imported command line during boot; panic notifier and sys_off handlers persist after setup.

Dependencies and integration: Xtensa generic setup calls `platform_setup()`, ISS `simcall.h`, panic notifier chain, and sys-off framework.

Risks: Command-line concatenation relies on prior argv-size bound but still uses `strcat`; oversized argv logs an error and leaves original command line; panic exits simulator immediately, which may bypass normal shutdown.

Test signals: ISS boot with simulator arguments, long command-line rejection, panic exit status, `reboot`, and `poweroff`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/simdisk.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/simdisk.c

Purpose: Implements ISS simulated block disks backed by host files accessed through simcalls.

Important APIs, types, and functions: `struct simdisk`, module params `simdisk_count` and `filename`, `simdisk_transfer()`, `simdisk_submit_bio()`, `simdisk_open()`, `simdisk_release()`, `simdisk_attach()`, `simdisk_detach()`, proc read/write handlers, `simdisk_setup()`, `simdisk_init()`, and `simdisk_exit()`.

Control flow: Module init registers major 240, clamps disk count, allocates devices, creates `/proc/simdisk`, creates `gendisk`s, and attaches configured host files. BIO submission iterates segments, maps each bvec locally, and calls `simdisk_transfer()` to lseek/read/write host file sectors. Proc writes detach current file and attach a new one when not in use.

State and persistence: Per-disk state tracks filename, host fd, capacity, users, spinlock, gendisk, and proc entry. Host file contents persist outside the simulator.

Dependencies and integration: Block layer `submit_bio`, procfs, module params, bvec local mapping, ISS simcall file operations, and static major alias.

Risks: Transfer silently returns on beyond-end without failing the BIO; partial host I/O loops until bytes consumed but only checks `-1`; proc attach/detach is blocked by open users; host file size determines capacity.

Test signals: Create/read/write filesystem on simdisk, proc attach/detach, concurrent opens blocking detach, beyond-end I/O, host file open failure, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/simdisk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/Makefile

Purpose: Builds XT2000 emulation board platform setup.

Important APIs, types, and functions: `obj-y = setup.o`.

Control flow: When XT2000 platform is selected, kbuild links `setup.o` to provide `platform_setup()` and device registration for the board.

State and persistence: No runtime state in the Makefile; it controls inclusion of board support.

Dependencies and integration: XT2000 Kconfig selection, platform headers for hardware/serial, and generic Xtensa platform hooks.

Risks: Missing `setup.o` would leave board devices and power handlers unavailable.

Test signals: XT2000 platform build and boot with serial/SONIC device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/include/platform/hardware.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/include/platform/hardware.h

Purpose: Defines XT2000 board hardware addresses and IRQ assignments.

Important APIs, types, and functions: `SONIC83934_INTNUM`, `SONIC83934_ADDR`, `IRQ_PCI_A/B/C`, and `XT2000_LED_ADDR`.

Control flow: Header-only constants used at compile time by platform setup and drivers.

State and persistence: No runtime state; maps physical board devices into `IOADDR()` virtual address space.

Dependencies and integration: `asm/core.h`, board setup, serial/SONIC devices, PCI interrupt wiring, and LED power/heartbeat code.

Risks: Hard-coded addresses/interrupts must match board memory map; `IOADDR()` assumptions depend on KIO mapping; incorrect IRQs break devices.

Test signals: XT2000 boot, LED writes, SONIC network interrupt, and PCI interrupt routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/include/platform/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/include/platform/serial.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/include/platform/serial.h

Purpose: Defines XT2000 DUART addresses, IRQs, crystal frequency, and base baud.

Important APIs, types, and functions: `DUART16552_1_INTNUM`, `DUART16552_2_INTNUM`, `DUART16552_1_ADDR`, `DUART16552_2_ADDR`, `DUART16552_XTAL_FREQ`, and `BASE_BAUD`.

Control flow: Header-only constants used by 8250 platform device setup and generic serial code.

State and persistence: No runtime state.

Dependencies and integration: `asm/core.h`, `asm/io.h`, XT2000 setup's `plat_serial8250_port` table, and 8250 serial driver.

Risks: Endian-specific address adjustment happens in setup, so these base addresses must remain raw channel bases; wrong crystal frequency produces incorrect baud.

Test signals: 8250 serial probe, console baud correctness, and interrupts from both DUART channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/include/platform/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/setup.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/setup.c

Purpose: Initializes XT2000 board LEDs, serial ports, SONIC network device, heartbeat, restart, and power-off behavior.

Important APIs, types, and functions: `led_print()`, `xt2000_power_off()`, `xt2000_restart()`, `platform_setup()`, `xt2000_heartbeat()`, serial port table, `xt2000_serial8250_device`, `xt2000_sonic_device`, and `xt2000_setup_devinit()`.

Control flow: Early platform setup writes `LINUX` to the LED display. Device init registers 8250 platform serial ports and SONIC resources, starts a half-second LED heartbeat timer, and registers sys-off handlers. Poweroff writes `POWEROFF`, disables interrupts, and spins; restart calls `cpu_reset()`.

State and persistence: Heartbeat timer toggles LED position 7; platform devices persist; sys-off handlers persist. LED writes go to memory-mapped board registers.

Dependencies and integration: Board hardware/serial headers, platform device core, serial8250, `xtsonic` driver, timers, and generic reboot/sys-off paths.

Risks: `led_print()` assumes an 8-character non-NULL string; poweroff never returns; endian serial port offsets differ; platform_device_register return values are ignored.

Test signals: LED boot/power/heartbeat display, ttyS device probe, SONIC resource probe, reboot path, and poweroff spin behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/Makefile

Purpose: Builds XTENSA XTFPGA/XTAVNET board support and optional LCD support.

Important APIs, types, and functions: `obj-y += setup.o` and `obj-$(CONFIG_XTFPGA_LCD) += lcd.o`.

Control flow: Kbuild always includes platform setup for XTFPGA and conditionally includes LCD driver support.

State and persistence: No runtime state in the Makefile; controls board object inclusion.

Dependencies and integration: XTFPGA platform Kconfig, hardware/serial/LCD headers, setup and optional LCD implementation.

Risks: Optional LCD declarations in `lcd.h` must match this object selection; missing setup object breaks platform hooks.

Test signals: XTFPGA builds with and without `CONFIG_XTFPGA_LCD`, link symbol resolution for LCD APIs, and board boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/hardware.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/hardware.h

Purpose: Defines XTFPGA/XTAVNET board interrupt assignments, device physical addresses, register virtual addresses, and device sizes.

Important APIs, types, and functions: `DUART16552_INTNUM`, `OETH_IRQ`, `C67X00_IRQ`, `DUART16552_PADDR`, `XTFPGA_FPGAREGS_VADDR`, `XTFPGA_CLKFRQ_VADDR`, `DIP_SWITCHES_VADDR`, `XTFPGA_SWRST_VADDR`, `OETH_*`, and `C67X00_*`.

Control flow: Header-only constants; conditional IRQ assignments differ for `CONFIG_XTENSA_MX`.

State and persistence: No runtime state, but constants refer to memory-mapped FPGA registers such as clock frequency, DIP switches, and reset.

Dependencies and integration: `asm/types.h`, core interrupt macros, serial baud calculation, board setup, OpenCores Ethernet, USB C67X00, and reset/clock code.

Risks: Hard-coded offsets assume a specific FPGA memory map; clock register is read directly through virtual address; MX vs non-MX interrupt mapping must match bitstream.

Test signals: XTFPGA boot, UART clock read, Ethernet/USB IRQ delivery, software reset register, and MX/non-MX configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/lcd.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/lcd.h

Purpose: Declares optional XTFPGA LCD display helpers or provides no-op stubs when LCD support is disabled.

Important APIs, types, and functions: `lcd_disp_at_pos()`, `lcd_shiftleft()`, and `lcd_shiftright()`.

Control flow: With `CONFIG_XTFPGA_LCD`, declares external functions implemented by LCD support. Without it, inline stubs do nothing so callers can compile unconditionally.

State and persistence: Real implementation would mutate LCD display state; stub implementation has no state.

Dependencies and integration: `CONFIG_XTFPGA_LCD`, optional `lcd.o` from platform Makefile, and board UI/status code.

Risks: Stubbed calls can hide missing LCD support in tests; function prototypes use mutable `char *` for display text.

Test signals: Build with LCD disabled and enabled, call sites link correctly, and LCD display operations work on board when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/lcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/serial.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/serial.h

Purpose: Provides XTFPGA serial base baud derived from the FPGA clock-frequency register.

Important APIs, types, and functions: Includes `platform/hardware.h` and defines `BASE_BAUD (*(long *)XTFPGA_CLKFRQ_VADDR / 16)`.

Control flow: Header-only; consumers read the memory-mapped clock register at runtime when evaluating `BASE_BAUD`.

State and persistence: Reads FPGA register state; does not write state.

Dependencies and integration: XTFPGA hardware clock register, generic serial/8250 code, and KIO mapping for the FPGA register virtual address.

Risks: Direct volatile-less pointer dereference may be sensitive to compiler assumptions; a bad or unmapped clock register breaks baud calculation; value changes at runtime would affect computed baud.

Test signals: Serial console baud correctness on XTFPGA, clock register accessibility early in boot, and comparison with board oscillator/FPGA-reported frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/serial.h -->
