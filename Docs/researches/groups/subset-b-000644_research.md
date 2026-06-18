# subset-b-000644 Research

Grouped research report for the exact subset-b-000644 source manifest. Each section preserves the source path and is bracketed for deterministic splitting into source-tree-aligned per-file reports.


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/swp_emulate.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/swp_emulate.c

Purpose: emulates deprecated ARM SWP/SWPB user instructions on ARMv7+ systems where the instruction is disabled or absent, using LDREX/STREX sequences and an undefined-instruction hook. Important entry points are the late init `swp_emulation_init`, the `swp_hook` undef hook, `swp_handler`, `emulate_swpX`, and the `/proc/cpu/swp_emulation` status renderer when procfs is enabled.

Control flow: the undef core calls `swp_handler`, condition codes are checked with `arm_check_condition`, registers are decoded from the faulting instruction, access is validated with `access_ok`, and `emulate_swpX` loops on `-EAGAIN` until exclusive store success or a pending signal. State is limited to counters for SWP/SWPB/aborts and the previous pid for logging. Dependencies include `uaccess_save_and_enable`, exception-table fixups, perf emulation fault events, `arm_notify_die`, and `register_undef_hook`. Risks are instruction decoding mistakes, unaligned SWP word addresses, user access faults, and excessive retry loops under contention. Test signals include SWP/SWPB userspace probes, proc counter changes, SIGSEGV behavior on invalid mappings, and no registration on pre-v7 CPUs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/swp_emulate.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/sys_arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/sys_arm.c

Purpose: contains ARM-specific syscall glue for calls whose register ABI differs from generic Linux argument order. The only function here is `sys_arm_fadvise64_64`, which reorders `fd, advice, offset, len` into the `ksys_fadvise64_64(fd, offset, len, advice)` convention.

Control flow is deliberately thin: syscall entry lands in this wrapper and immediately delegates to the common kernel implementation. There is no local persistent state, locking, or memory ownership. Dependencies are syscall linkage, ARM syscall tables, and the generic fadvise implementation. The main risk is ABI ordering regression, because userspace depends on this nonstandard ARM calling sequence for 64-bit arguments. Test signals are syscall ABI tests that pass nonzero offset/length/advice combinations and compare behavior to expected `posix_fadvise` semantics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/sys_arm.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/sys_oabi-compat.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/sys_oabi-compat.c

Purpose: provides OABI compatibility wrappers used by old ARM ABI binaries on an EABI kernel. It adapts structure layout and argument quirks before forwarding to normal VFS, file-locking, epoll, SysV IPC, and socket syscalls. Key exported syscall wrappers include `sys_oabi_stat64`, `sys_oabi_lstat64`, `sys_oabi_fstat64`, `sys_oabi_fstatat64`, `sys_oabi_fcntl64`, `sys_oabi_epoll_ctl`, `sys_oabi_semtimedop`, `sys_oabi_semop`, `sys_oabi_ipc`, and OABI socket wrappers.

Control flow is copy-in/convert/call/copy-out: packed OABI structs such as `oldabi_stat64`, `oabi_flock64`, `oabi_epoll_event`, and `oabi_sembuf` are translated into kernel or EABI layouts. State is transient heap memory for semaphore arrays; persistence remains in the underlying subsystem. Dependencies include `copy_{to,from}_user`, namespace IPC limits, `security_file_fcntl`, `do_epoll_ctl`, and legacy syscall dispatch. Risks are user-pointer faults, struct padding errors, partial `sendmsg` mutation of `msg_namelen`, and feature-dependent `-ENOSYS`/`-EINVAL` paths. Test signals should cover old stat64 layout, flock64 get/set round trips, OABI epoll event layout, semop arrays with padding, AF_UNIX length 112-to-110 rewriting, and socketcall forwarding.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/sys_oabi-compat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/tcm.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/tcm.c

Purpose: detects, maps, initializes, and exposes ARM Tightly Coupled Memory banks. It relocates linker-marked ITCM/DTCM code/data into CPU TCM windows, registers resources, creates a `gen_pool`, and exports `tcm_alloc`, `tcm_free`, `tcm_dtcm_present`, and `tcm_itcm_present`.

Control flow: `tcm_init` runs early, rejects pre-v5 or unsupported TCMTR formats, temporarily installs an undef hook for inaccessible TrustZone TCM register reads, probes DTCM/ITCM banks with CP15 c9 registers, moves banks to fixed offsets, maps them with `iotable_init`, and copies compiled sections. `setup_tcm_pool` later creates a 4-byte-granularity pool and adds unused TCM ranges after linked code/data. Persistent state includes `tcm_pool`, presence flags, and `dtcm_end`/`itcm_end`. Dependencies include linker symbols, `asm/tcm.h` offsets, CP15 access, `genalloc`, resources, and MMU map descriptors. Risks are incorrect bank sizing, unsupported banks above 32 KiB, secure-world traps, code larger than TCM, and pool setup after failed allocation. Test signals include boot logs for moved banks, exported allocation/free, `/proc/iomem` resources, and systems with no TCM or inaccessible TCM registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/tcm.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/thumbee.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/thumbee.c

Purpose: enables ThumbEE support when the CPU advertises it and preserves the ThumbEE Handler Base Register across thread lifecycle events. Key functions are `teehbr_read`, `teehbr_write`, `thumbee_notifier`, and late init `thumbee_init`.

Control flow: init checks ARMv7+ and CPUID PFR0 ThumbEE bits, sets `HWCAP_THUMBEE`, and registers a thread notifier. On `THREAD_NOTIFY_FLUSH` it clears TEEHBR; on `THREAD_NOTIFY_SWITCH` it saves the outgoing thread's value and restores the incoming thread's `thumbee_state`. State lives in per-thread `thread_info`; the CPU register is transient per context. Dependencies are CP14 register access, `elf_hwcap`, and the ARM thread notifier chain. Risks are unsupported coprocessor access, stale per-thread ThumbEE state, and missing hwcap publication. Test signals include hwcap visibility, context-switch preservation, and no registration on CPUs without ThumbEE.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/thumbee.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/time.c

Purpose: supplies ARM-specific time initialization and persistent-clock registration. It exports `rtc_lock` for legacy CMOS/NVRAM configurations, `profile_pc` on SMP, `read_persistent_clock64`, `register_persistent_clock`, and `time_init`.

Control flow: `register_persistent_clock` installs exactly one platform read callback, otherwise the dummy clock returns zero. `time_init` either calls `machine_desc->init_time` or performs common clock DT initialization, timer probing, and hrtimer broadcast setup. `profile_pc` unwinds out of lock functions before returning a profiling PC. State is the registered persistent-clock function pointer and optional RTC spinlock. Dependencies include machine descriptors, common clock, clocksource/timer probe, stack unwinding, and scheduler profiling. Risks are double registration, missing DT timer setup, and unwind failure in profiling. Test signals include boot timer initialization, persistent clock nonzero values on platforms that register one, and profiler samples not stuck in lock helpers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/time.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/topology.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/topology.c

Purpose: builds ARM CPU topology and scheduler capacity data from MPIDR and device tree. Key functions are `init_cpu_topology`, `store_cpu_topology`, `parse_dt_topology`, and `update_cpu_capacity`.

Control flow: boot resets topology, parses DT capacity data or legacy compatible/clock-frequency efficiency values, normalizes scheduler CPU scale, then each CPU stores package/core/thread ids from MPIDR and updates sibling masks. Persistent state includes `cpu_topology[]`, optional `__cpu_capacity`, `middle_capacity`, and `cap_from_dt`. Dependencies include OF CPU nodes, `topology_parse_cpu_capacity`, scheduler topology helpers, MPIDR macros, and arch topology scale APIs. Risks are missing CPU DT nodes, bad clock-frequency lengths, heterogeneous capacity normalization mistakes, and hotplug races if called outside the documented locked paths. Test signals include boot topology logs, scheduler capacity values on big.LITTLE systems, correct sibling masks, and fallback defaults on homogeneous systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/topology.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/traps.c

Purpose: central ARM exception, oops, undefined-instruction, legacy syscall, vector-page, and stack diagnostic handling after low-level entry code saves registers. Major APIs include `die`, `arm_notify_die`, `register_undef_hook`, `unregister_undef_hook`, `do_undefinstr`, `arm_syscall`, `baddataabort`, `early_trap_init`, `dump_mem`, `dump_backtrace`, and VMAP stack helpers.

Control flow: exceptions decode context, optionally run notifier/hook chains, signal userspace or panic/oops in kernel mode, and print registers, stack, code bytes, and backtrace under a reentrancy-aware oops lock. Undefined instructions fetch ARM/Thumb opcodes, search registered hooks under `undef_lock`, or deliver SIGILL. `arm_syscall` handles ARM private calls such as cacheflush, TLS, breakpoint, and 26/32-bit personality switching. Persistent state includes `vectors_page`, debug flags, undef hook list, die lock/nesting counters, and per-CPU overflow stacks. Dependencies include low-level vector symbols, uaccess, kprobes, bug reporting, kexec, Spectre BHB vector variants, TLS, and MMU/vmalloc sync. Risks are bad instruction fetches, hook mask conflicts, recursive oops deadlocks, user cacheflush validation, and stack overflow before page-table sync. Test signals include undefined-hook registration tests, bad syscall behavior, cacheflush range validation, vector copying/flush, oops logs, and VMAP stack overflow diagnostics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/traps.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/unwind.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/unwind.c

Purpose: implements ARM EHABI stack unwinding for kernel and module backtraces. It provides dummy AEABI personality symbols, `unwind_frame`, `unwind_backtrace`, `unwind_table_add`, and `unwind_table_del`.

Control flow: `unwind_find_idx` chooses the core or module unwind table, `search_index` locates a function's prel31 unwind row, and `unwind_frame` interprets compact unwind opcodes to update virtual FP/SP/LR/PC registers. The interpreter handles stack pointer adjustments, register pops, finish opcodes, ULEB128 increments, module PLT veneers, prologue edge cases, and special `call_with_stack` stack switching. Persistent state is the core unwind origin cache and a spinlock-protected module table list. Dependencies include linker-provided unwind sections, module load/unload hooks, stacktrace helpers, `call_with_stack`, and kernel text address checks. Risks include corrupt unwind tables, unsupported personality routines, stack-bound violations, infinite unwind loops, and concurrent module table removal. Test signals include reliable `dump_stack`, module backtraces, malformed unwind warnings, and traces crossing `call_with_stack`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/unwind.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/v7m.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/v7m.c

Purpose: supplies ARMv7-M restart support. `armv7m_restart` writes the SCB AIRCR key plus SYSRESETREQ after data synchronization barriers.

Control flow is a short reboot path: flush outstanding memory operations with `dsb`, write `V7M_SCB_AIRCR_VECTKEY | V7M_SCB_AIRCR_SYSRESETREQ` to the system control block, then issue another `dsb`. There is no local state or allocation. Dependencies are the ARMv7-M SCB base definitions, raw MMIO write helpers, and the generic reboot path that installs this restart callback. Risks are wrong SCB base mapping or missing reset response from platform hardware. Test signals are reboot tests on ARM_SINGLE_ARMV7M systems and observation that the CPU resets rather than returning.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/v7m.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/vdso.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/vdso.c

Purpose: initializes and maps the ARM VDSO and VVAR pages into userspace processes, with boot-time symbol patching when the architectural virtual counter is unavailable. Key functions are `vdso_init`, `arm_install_vdso`, `patch_vdso`, `find_section`, and `find_symbol`.

Control flow: init validates the embedded ELF, builds a page list for `vdso_start..vdso_end`, records total pages, and nulls selected dynamic symbol names if DT probing says the virtual counter is not functional or firmware has not configured CPU registers. `arm_install_vdso` maps VVAR first, then installs executable text as a special mapping and tracks `mm->context.vdso`; `vdso_mremap` updates that address after remap. Persistent state includes `vdso_text_pagelist`, `vdso_total_pages`, and per-mm VDSO base. Dependencies include DT timer nodes, arch timer support, ELF section layout, special mappings, VVAR helpers, and cache/page definitions. Risks are malformed VDSO ELF, missing `.dynsym`/`.dynstr`, inaccurate timer usability detection, and mapping failures. Test signals include auxv/VDSO presence, fallback to syscalls when timer symbols are nulled, and process remap behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/vdso.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/vmcore_info.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/vmcore_info.c

Purpose: contributes ARM-specific metadata to crash dump vmcore notes. `arch_crash_save_vmcoreinfo` records `CONFIG_ARM_LPAE` when LPAE is enabled.

Control flow is invoked by the crash dump infrastructure during vmcoreinfo collection. There is no local state; the function conditionally emits configuration metadata through `VMCOREINFO_CONFIG`. Dependencies are `linux/vmcore_info.h` and the crash/kdump vmcoreinfo pipeline. The main risk is missing architecture flags that crash tools need to decode page tables. Test signals are kdump vmcoreinfo contents on LPAE and non-LPAE kernels.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/vmcore_info.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/vmlinux-xip.lds.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/vmlinux-xip.lds.S

Purpose: linker script for execute-in-place ARM kernels. It separates ROM-resident text/rodata/init code from RAM-copied writable data, establishes `_xiprom`, `_exiprom`, `__data_loc`, `_edata_loc`, and adjusted `LOAD_OFFSET`, and keeps XIP-specific MPU constraints.

Control flow is link/load-time: code starts at `XIP_VIRT_ADDR(CONFIG_XIP_PHYS_ADDR)`, ROM sections remain executable in place, then data is assigned RAM VMAs with file LMAs for copy/decompression. It explicitly defines `.data.ro_after_init`, init data, per-CPU data, TCM sections, BSS, and debug metadata. Dependencies include XIP address macros, ARM linker section macros, MPU alignment constants, and optional `CONFIG_XIP_DEFLATED_DATA`. Risks are wrong ROM/RAM split, data copy size errors, MPU-region alignment failures, and BSS too small for decompression stack. Test signals include link ASSERTs, XIP boot, writable data relocation, and strict checks for `_xiprom`/`_exiprom` alignment on MPU builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/vmlinux-xip.lds.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/vmlinux.lds.S

Purpose: linker script for normal non-XIP ARM kernels. It defines the virtual layout, symbol boundaries, section ordering, special init/discard regions, unwind and exception-table placement, per-CPU data, TCM sections, BSS, debug metadata, and build-time assertions.

Control flow is link-time rather than runtime: `ENTRY(stext)` starts execution, sections begin at `KERNEL_OFFSET + TEXT_OFFSET`, text/rodata/init/data/BSS are aligned according to MMU, MPU, strict RWX, cacheline, and thread constraints. Persistent integration points are exported linker symbols such as `_text`, `_stext`, `_etext`, `__init_begin`, `__init_end`, `_sdata`, `_edata`, `_end`, exception table bounds, arch info bounds, pv table bounds, and unwind sections. Dependencies include `asm/vmlinux.lds.h` macros and many config switches. Risks are section misalignment, discarded unwind data when required, empty CPU or machine records, and RWX boundary regressions. Test signals are successful link, boot, kallsyms/exception/unwind behavior, and linker ASSERT failures when required records are missing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/vmlinux.lds.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/xscale-cp0.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/xscale-cp0.c

Purpose: probes and manages XScale CP0/CP1 DSP or iWMMXt coprocessor support. It detects iWMMXt versus DSP behavior, registers thread notifiers, publishes `HWCAP_IWMMXT` when supported, and sets coprocessor access bits.

Control flow: late init first filters non-XScale CPUs, enables CP0 temporarily, probes by writing/reading a 64-bit coprocessor register, then either installs iWMMXt lazy context/undef handling or keeps DSP access enabled and saves/restores accumulator state on every context switch. Persistent state lives in per-thread CPU context extras or iWMMXt state managed elsewhere. Dependencies include CP15 c15 access control, CP0 instructions, `thread_register_notifier`, `iwmmxt_task_switch/release`, `register_iwmmxt_undef_handler`, and `elf_hwcap`. Risks are probing on unsupported CPUs, missing CONFIG_IWMMXT, stale coprocessor state across switches, and access-control mismatches. Test signals include hwcap presence, context-switch stress using DSP/iWMMXt instructions, and boot warnings when hardware exists without support.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/xscale-cp0.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/lib/Makefile

Purpose: defines the ARM architecture support library objects built into the kernel. It selects generic assembly helpers, MMU-only uaccess helpers, compiler-specific backtrace support, CPU-generation-specific raw 16-bit I/O routines, optional memcpy-backed uaccess, and function error injection support.

Control flow is build-system selection rather than runtime logic. `lib-y` contains bitops, checksums, memory/string helpers, compiler arithmetic helpers, division, raw I/O, stack switching, and byte-swap helpers. `mmu-y` is added only with `CONFIG_MMU`; Clang gets `backtrace-clang.o` while other compilers get `backtrace.o`; ARMv3 gets older readsw/writesw routines. Dependencies are Kconfig symbols and object naming expected by the ARM kernel. Risks are missing required helper symbols, selecting the wrong backtrace ABI, or using raw I/O helpers incompatible with CPU generation. Test signals are successful ARM links across major configs and symbol presence in vmlinux.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/ashldi3.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/ashldi3.S

Purpose: provides the ARM assembly helper entry points `__ashldi3`/`__aeabi_llsl`. It implements 64-bit arithmetic left shift with endian-aware high/low register aliases and ARM/Thumb variants for cross-word shifts.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/ashldi3.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/ashrdi3.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/ashrdi3.S

Purpose: provides the ARM assembly helper entry points `__ashrdi3`/`__aeabi_lasr`. It implements 64-bit signed arithmetic right shift preserving sign in the high word.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/ashrdi3.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/backtrace-clang.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/backtrace-clang.S

Purpose: implements `c_backtrace` for Clang frame-pointer builds, compensating for Clang's frame layout that lacks saved PC/SP in prologues.

Control flow builds a false frame, walks saved frame pointers, treats the current frame LR as saved PC, attempts to recover function starts from BL call instructions, prints entries with `dump_backtrace_entry`, and optionally prints saved registers if the function prologue pattern is recognized. Exception-table entries abort cleanly on bad frame memory. State is transient stack/register state; no persistent storage. Dependencies include CONFIG_FRAME_POINTER, CONFIG_PRINTK, ARM/Thumb mode masks, `_printk`, and trap dump helpers. Risks are inaccurate function-start recovery for indirect calls, bad frame pointers, discontiguous IRQ stacks, and compiler prologue changes. Test signals are readable stack traces from Clang kernels, graceful abort messages on bad frames, and comparison against unwinder output.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/backtrace-clang.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/backtrace.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/backtrace.S

Purpose: implements `c_backtrace` for GCC-style ARM frame-pointer builds. It decodes the classic APCS frame layout containing saved PC, LR, SP, FP, and optional saved registers/arguments.

Control flow validates frame pointers, corrects saved PC for prefetch offset, detects prologue store patterns, calls `dump_backtrace_entry` and `dump_backtrace_stm`, then advances to the previous frame until zero or invalid. Exception-table fixups report aborted backtraces rather than faulting. State is transient. Dependencies include CONFIG_FRAME_POINTER, CONFIG_PRINTK, frame layout emitted by GCC, IRQ stack configuration, and trap dump helpers. Risks are compiler layout drift, corrupted frame chains, 26-bit mode masks, and incomplete traces through nonstandard assembly. Test signals are readable oops/dump_stack traces and bad-frame abort messages rather than secondary faults.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/backtrace.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/bitops.h -->
# sources/distributed-fs/ceph-client/arch/arm/lib/bitops.h

Purpose: macro template for ARM atomic bit operations and test-and-bit operations used by `changebit.S`, `clearbit.S`, `setbit.S`, and test variants.

Control flow differs by architecture: ARMv6+ uses LDREX/STREX retry loops with optional SMP prefetch and barriers, while older CPUs disable IRQs around word load/modify/store. Test operations return the previous bit value and sync variants use stronger barriers. State is the target bit word only; no global state exists. Dependencies include `asm/assembler.h`, unwind annotations, SMP alternatives, and word-aligned bitmaps. Risks are unaligned bitmap pointers, missing memory barriers for synchronization use, exclusive-store livelock under contention, and IRQ masking latency on old CPUs. Test signals include atomic bitop stress under SMP, alignment fault checks, and verifying sync variants order surrounding memory accesses.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/bitops.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/bswapsdi2.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/bswapsdi2.S

Purpose: provides the ARM assembly helper entry points `__bswapsi2` and `__bswapdi2`. It implements 32/64-bit byte swaps using `rev` on ARMv6+ and rotate/xor sequences on older CPUs.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/bswapsdi2.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/call_with_stack.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/call_with_stack.S

Purpose: provides `call_with_stack(fn, arg, sp)`, a helper that switches to a supplied stack, calls a function with one argument, and returns to the original stack with unwind-compatible frame setup.

Control flow saves FP/LR using either frame-pointer APCS or EHABI unwind annotations, moves `sp` to the caller-supplied stack, branches through the function pointer, restores the old stack/frame, and returns. State is the live stack pointer only. Dependencies include `asm/assembler.h`, unwind metadata, and `unwind.c`, which has special handling for this known stack transition. Risks are invalid stack pointers, broken unwinding across the stack switch, and callee assumptions about stack alignment. Test signals include stack-switch users executing successfully and backtraces crossing `call_with_stack` without false stack overflow failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/call_with_stack.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/changebit.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/changebit.S

Purpose: provides the ARM assembly helper entry points `_change_bit`. It implements atomic bit toggle generated by the shared bitop macro.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/changebit.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/clear_user.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/clear_user.S

Purpose: implements `arm_clear_user`/`__clear_user_std`, clearing a user memory range and returning the number of bytes not cleared.

Control flow aligns the destination, writes zero by bytes and words through user-access store macros, and uses exception-table fixup `9001` to return the remaining byte count on a fault. State is only the user memory range. Dependencies include uaccess assembler macros, exception table support, and optional override by `uaccess_with_memcpy.c`. Risks are incorrect remaining-count calculation, user access enable/disable context, and alignment edge cases. Test signals include fault-injection on partially mapped ranges, small and unaligned clears, and full zeroing on valid user buffers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/clear_user.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/clearbit.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/clearbit.S

Purpose: provides the ARM assembly helper entry points `_clear_bit`. It implements atomic bit clear generated by the shared bitop macro.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/clearbit.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/copy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/copy_from_user.S

Purpose: implements `arm_copy_from_user`, copying user memory into kernel memory and returning bytes not copied.

Control flow selects domain or normal user load macros, optionally masks speculative user ranges under `CONFIG_CPU_SPECTRE`, then includes `copy_template.S` for optimized forward copying. Fixup code unwinds saved registers and computes the remaining byte count after a fault. State is only copied memory and transient registers. Dependencies include uaccess helpers, exception tables, PAN/domain configuration, and the shared copy template. Risks are speculative range masking bugs, partial-copy accounting, unaligned source handling, and user faults. Test signals include copy tests over page boundaries, invalid user ranges, and Spectre-config builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/copy_from_user.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/copy_page.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/copy_page.S

Purpose: optimized `copy_page` routine for copying one kernel page using cacheline-sized blocks and prefetch hints.

Control flow saves minimal registers, prefetches source cachelines, loops over `PAGE_SZ / (2 * L1_CACHE_BYTES)` chunks, and copies four registers at a time with `ldmia/stmia`. There is no fault handling because both addresses are kernel page mappings. Dependencies include page/cache constants and PLD assembler macros. Risks are cacheline-size assumptions, register clobber mistakes, and use on overlapping ranges, which this API does not support. Test signals are page-copy correctness, highmem/page allocator users, and architecture build coverage with and without PLD.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/copy_page.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/copy_template.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/copy_template.S

Purpose: shared optimized forward-copy assembly template included by `memcpy`, `copy_to_user`, and `copy_from_user`. Including files provide load/store, entry/exit, and fault-abort macros.

Control flow handles small copies, destination alignment, source alignment, 32-byte and larger unrolled loops, prefetching, byte tails, and three unaligned-source shift cases. It also defines abort-preamble/end macros that including uaccess files use to unwind registers. State is entirely caller-provided registers/memory. Dependencies are include-time macros such as `ldr1w`, `str8w`, `enter`, `exit`, `LDR1W_SHIFT`, `STR1W_SHIFT`, and optional `CALGN`/`PLD`. Risks are any include macro mismatch, PC-relative computed branches, and subtle off-by-one tail handling. Test signals include memcpy and uaccess copy suites across all alignments, sizes around 0..128, and faulting user pages.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/copy_template.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/copy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/copy_to_user.S

Purpose: implements `arm_copy_to_user`/`__copy_to_user_std`, copying kernel memory to user memory and returning bytes not copied.

Control flow mirrors `copy_from_user` with kernel loads and user stores, optional Spectre range masking, and `copy_template.S` for aligned/unaligned forward copies. Exception-table fixups compute the remaining byte count. State is the destination user memory only. Dependencies include user store assembler macros, exception tables, PAN/domain configuration, and possible replacement by `uaccess_with_memcpy.c`. Risks are partial-copy accounting, stale user access permissions, unaligned destination paths, and faults after some bytes were stored. Test signals include valid/invalid user copies, page-boundary faults, and small/large copy thresholds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/copy_to_user.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumipv6.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/csumipv6.S

Purpose: implements `__csum_ipv6_magic`, folding IPv6 source/destination addresses, length, protocol, and starting sum into the transport pseudo-header checksum.

Control flow loads four words from each IPv6 address, adds them with carry along with length/protocol inputs and the stack-passed argument, then returns the accumulated 32-bit checksum for later folding. There is no persistent state or fault handling; callers provide kernel-accessible addresses. Dependencies are ARM calling convention and networking checksum users. Risks are endian/carry handling errors and stack argument position assumptions. Test signals include IPv6 TCP/UDP checksum selftests and packet validation against generic checksum implementations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumipv6.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumpartial.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/csumpartial.S

Purpose: implements `csum_partial`, the core Internet checksum accumulator over an arbitrary byte buffer.

Control flow aligns odd and halfword addresses, processes 32-byte blocks with carry propagation, handles word/halfword/byte tails, and rotates the result when the original buffer was odd-aligned. State is transient checksum/register state. Dependencies include endian-specific byte placement macros and kernel networking checksum callers. Risks are carry loss, odd-address rotation mistakes, and older CPU halfword-load fallbacks. Test signals include checksum selftests over random buffers and alignments, comparing with generic C implementation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumpartial.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumpartialcopy.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/csumpartialcopy.S

Purpose: instantiates `csumpartialcopygeneric.S` as `csum_partial_copy_nocheck`, copying kernel memory while computing an Internet checksum without user fault handling.

Control flow supplies plain load/store macros and register save/restore wrappers, then delegates all alignment, copy, and checksum logic to the generic template. State is destination memory plus checksum return value. Dependencies are the generic checksum-copy template and networking stack callers. Risks are include macro mismatch, checksum rotation on unaligned destination, and lack of fault handling by design. Test signals include checksum-copy comparisons against separate memcpy plus checksum across alignments.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumpartialcopy.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumpartialcopygeneric.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/csumpartialcopygeneric.S

Purpose: shared checksum-copy template used by checked and unchecked checksum copy routines. It copies bytes from source to destination while computing a partial Internet checksum.

Control flow aligns destination, handles short copies, then chooses aligned or three unaligned-source shift paths, processing 16-byte blocks and byte tails while updating carry. It rotates the final checksum if the original destination was odd-aligned. State is only destination memory and the checksum accumulator. Dependencies are include-time macros for loads, stores, register save/restore, and entry/exit symbol definitions. Risks are carry propagation, unaligned byte lane assembly, destination-odd final rotation, and user fault behavior supplied by includers. Test signals are randomized checksum-copy tests over every source/destination alignment and length class.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumpartialcopygeneric.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumpartialcopyuser.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/csumpartialcopyuser.S

Purpose: instantiates the checksum-copy template as `csum_partial_copy_from_user`, copying from user memory while computing a checksum and returning zero on fault.

Control flow saves registers and, depending on PAN mode, enables user access before including the generic copy/checksum logic with `ldrusr` user loads. A `.text.fixup` handler returns checksum 0, which is impossible for the initialized accumulator in normal success. State is destination memory and transient PAN/domain register state. Dependencies include uaccess assembler macros, exception tables, PAN/domain configuration, and networking users. Risks are ambiguous zero return handling, user faults after partial destination writes, and access-permission restore. Test signals include faulting user-source checksum copies, PAN configs, and alignment comparisons with generic code.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/csumpartialcopyuser.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/delay-loop.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/delay-loop.S

Purpose: provides loop-based delay primitives `__loop_delay`, `__loop_const_udelay`, and `__loop_udelay` used before or instead of timer-backed delay.

Control flow converts microseconds or constant delay units through `UDELAY_MULT` and `loops_per_jiffy`, rounds up, and spins decrementing a loop counter until elapsed. Persistent state is external `loops_per_jiffy`; this file owns none. Dependencies include calibration code and `asm/delay.h`. Risks are inaccurate delays before calibration, CPU frequency changes, and zero/overflow edge cases. Test signals include delay calibration, timer fallback absence, and timing sanity under early boot.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/delay-loop.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/arm/lib/delay.c

Purpose: chooses between loop-based and timer-based ARM delay operations and exports `read_current_timer`.

Control flow starts with `arm_delay_ops` pointing to loop routines. `register_current_timer_delay` evaluates a candidate timer's frequency/resolution, installs it if it is the best pre-calibration timer, updates `lpj_fine` and private ticks-per-jiffy, and replaces delay callbacks with cycle-based loops. `calibrate_delay_is_known` and `calibration_delay_done` freeze late replacement. Persistent state includes `arm_delay_ops`, `delay_timer`, `delay_calibrated`, and `delay_res`. Dependencies are clocksource delay timers, `clocks_calc_mult_shift`, and timer calibration. Risks are accepting low-resolution timers, late duplicate registration, cpufreq interaction, and no timer available for `read_current_timer`. Test signals include boot log selection, udelay accuracy, duplicate registration logs, and `read_current_timer` returning `-ENXIO` without a timer.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/delay.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/div64.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/div64.S

Purpose: implements `__do_div64`, an optimized nonstandard ABI helper for 64-bit dividend divided by 32-bit divisor used by ARM `do_div`.

Control flow handles divisor 0/1 and power-of-two fast paths, computes upper quotient bits when needed, then shifts remainder bits through a lower quotient loop. Division by zero calls `__div0` and returns zeroed outputs. State is only register state: quotient in `yh:yl` and remainder in `xh`. Dependencies include ARM endian register aliases, CLZ availability on ARMv5+, and `__div0` diagnostics. Risks are nonstandard calling convention misuse, divide-by-zero behavior, and edge cases where upper quotient is required. Test signals include arithmetic selftests comparing `do_div` against compiler/runtime division for random 64/32 pairs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/div64.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/arch/arm/lib/error-inject.c

Purpose: supports function error injection by redirecting execution to the caller return address. `override_function_with_return` sets the saved instruction pointer to `regs->ARM_lr`.

Control flow is invoked by kprobe/error-injection infrastructure for an intercepted function; it mutates pt_regs so execution returns immediately. There is no persistent state. Dependencies are `linux/error-injection.h`, kprobes, ARM pt_regs layout, and `instruction_pointer_set`. Risks are using it on functions where LR is not a valid return address or where skipped side effects are unsafe. Test signals include CONFIG_FUNCTION_ERROR_INJECTION tests and kprobe-based override behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/error-inject.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/findbit.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/findbit.S

Purpose: implements little-endian and, on big-endian builds, big-endian find-first/find-next set and zero bit helpers. Entry points include `_find_first_zero_bit_le`, `_find_next_zero_bit_le`, `_find_first_bit_le`, `_find_next_bit_le`, and BE variants.

Control flow scans words until a candidate nonzero word is found, adjusts for start offset in next-bit calls, reverses bytes where endian semantics require, then uses `rbit/clz`, `clz` tricks, or manual bit tests depending on CPU generation. State is none beyond input bitmap reads. Dependencies include endian macros and bitops API naming. Risks are off-by-one exclusive size handling, endian bit order confusion, and CPU instruction availability. Test signals include bitmap selftests over all sizes, offsets, zero-size calls, and BE/LE configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/findbit.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/getuser.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/getuser.S

Purpose: implements low-level `__get_user_1/2/4/8` helpers, plus big-endian transfer variants, returning an error code in r0 and loaded value in r2/r3.

Control flow validates address limits with `check_uaccess`, performs user loads with size-appropriate instructions or byte assembly on older CPUs, and uses exception-table fixups to zero outputs and return `-EFAULT`. State is none besides loaded registers. Dependencies include uaccess macros, domain/PAN configuration, exception tables, and `asm/uaccess.h` register conventions. Risks are preserving required registers, endian assembly for subword values, and fault handling for the high word of 64-bit loads. Test signals include get_user tests for each size, invalid pointers, boundary crossings, and BE-specific variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/getuser.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-readsb.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/io-readsb.S

Purpose: provides the ARM assembly helper entry points `__raw_readsb`. It implements read repeated bytes from an I/O address into memory, packing into aligned word stores where possible.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-readsb.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-readsl.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/io-readsl.S

Purpose: provides the ARM assembly helper entry points `__raw_readsl`. It implements read repeated 32-bit words from I/O into possibly unaligned memory.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-readsl.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-readsw-armv3.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/io-readsw-armv3.S

Purpose: provides the ARM assembly helper entry points `__raw_readsw` for ARMv3. It implements read repeated 16-bit I/O values using word loads and byte packing, panicking on impossible bad alignment.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-readsw-armv3.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-readsw-armv4.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/io-readsw-armv4.S

Purpose: provides the ARM assembly helper entry points `__raw_readsw` for ARMv4+. It implements read repeated 16-bit I/O values using halfword loads with endian-aware packing and unaligned buffer support.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-readsw-armv4.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-writesb.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/io-writesb.S

Purpose: provides the ARM assembly helper entry points `__raw_writesb`. It implements write repeated bytes from memory to an I/O address, unpacking aligned words.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-writesb.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-writesl.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/io-writesl.S

Purpose: provides the ARM assembly helper entry points `__raw_writesl`. It implements write repeated 32-bit words to an I/O address from possibly unaligned memory.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-writesl.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-writesw-armv3.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/io-writesw-armv3.S

Purpose: provides the ARM assembly helper entry points `__raw_writesw` for ARMv3. It implements write repeated 16-bit I/O values using word loads and duplicated halfword stores, panicking on bad alignment.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-writesw-armv3.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-writesw-armv4.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/io-writesw-armv4.S

Purpose: provides the ARM assembly helper entry points `__raw_writesw` for ARMv4+. It implements write repeated 16-bit I/O values using halfword stores with endian-aware unaligned handling.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/io-writesw-armv4.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/lib1funcs.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/lib1funcs.S

Purpose: provides optimized compiler helper routines for 32-bit signed/unsigned division and modulo, including AEABI variants `__aeabi_uidiv`, `__aeabi_idiv`, `__aeabi_uidivmod`, and `__aeabi_idivmod`.

Control flow handles divisor 0/1, dividend-divisor comparisons, power-of-two fast paths, and unrolled restoring division/modulo loops using CLZ when available. Signed helpers normalize signs and restore the result or remainder sign. Divide-by-zero calls `__div0` and returns zero. State is register-only; no persistence. Dependencies include compiler-generated helper calls, optional IDIV patching alignment, and `__div0`. Risks are ABI return conventions for quotient/remainder, signed overflow edge cases, and patching assumptions. Test signals include compiler runtime arithmetic selftests across signed/unsigned random inputs and divide-by-zero diagnostics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/lib1funcs.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/lshrdi3.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/lshrdi3.S

Purpose: provides the ARM assembly helper entry points `__lshrdi3`/`__aeabi_llsr`. It implements 64-bit logical right shift filling high bits with zero.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/lshrdi3.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/memchr.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/memchr.S

Purpose: provides the ARM assembly helper entry points `memchr`. It implements byte scan returning the first matching address or NULL.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/memchr.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/memcpy.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/memcpy.S

Purpose: implements `__memcpy`, weak `memcpy`, and `mmiocpy` using the shared optimized forward-copy template.

Control flow supplies plain kernel load/store macros to `copy_template.S`, which handles alignment, unrolled copies, and tails. It preserves the original destination pointer as the return value. There is no fault handling or overlap support; callers must use `memmove` for overlaps. Dependencies include `copy_template.S`, assembler helpers, and weak symbol resolution. Risks are overlap misuse, alignment path bugs, and template macro regressions affecting multiple copy APIs. Test signals include memcpy tests over lengths and alignments and mmiocpy users on MMIO-like mappings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/memcpy.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/memmove.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/memmove.S

Purpose: implements `__memmove` and weak `memmove`, supporting overlapping memory ranges.

Control flow compares destination/source distance; non-overlapping or safe forward cases branch to `__memcpy`, while overlapping destructive cases copy backward from the end with alignment, unrolled 32-byte loops, source-shift paths, and byte tails. State is only destination memory and registers. Dependencies include assembler endian byte-lane macros, PLD/CALGN options, and `__memcpy`. Risks are off-by-one overlap detection, backward unaligned source reconstruction, and return-value preservation. Test signals include memmove overlap matrices, all alignments, and small tail sizes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/memmove.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/memset.S

Purpose: implements `__memset`, weak `memset`, `mmioset`, `__memset32`, and `__memset64`.

Control flow aligns the destination, expands an 8-bit value to words, stores 64-byte/32-byte/16-byte blocks with optional cacheline alignment strategy, then writes byte tails. `__memset32`/`__memset64` enter the shared word-fill path. State is the target memory only. Dependencies include assembler macros, unwind annotations, and optional CALGN configuration. Risks are alignment tail mistakes, MMIO ordering assumptions for `mmioset`, and preserving the destination return value. Test signals include memset tests for every length/alignment, 32/64-bit fill helpers, and boot memory initialization paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/memset.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/muldi3.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/muldi3.S

Purpose: provides the ARM assembly helper entry points `__muldi3`/`__aeabi_lmul`. It implements 64-bit multiply using 32-bit partial products and carry propagation.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/muldi3.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/putuser.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/putuser.S

Purpose: implements low-level `__put_user_1/2/4/8` helpers, storing r2/r3 values to user memory and returning an error code in r0.

Control flow validates address limits with `check_uaccess`, performs user stores with size-appropriate instructions or byte splitting on older CPUs, and uses exception-table fixups to return `-EFAULT`. State is user memory only. Dependencies include uaccess/domain macros, exception tables, and register conventions from `asm/uaccess.h`. Risks include partial stores on faults, endian handling for 16-bit stores on pre-v6 CPUs, and preserving required registers. Test signals include put_user tests for each size, invalid pointers, page-boundary faults, and BE/LE builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/putuser.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/setbit.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/setbit.S

Purpose: provides the ARM assembly helper entry points `_set_bit`. It implements atomic bit set generated by the shared bitop macro.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/setbit.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/strchr.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/strchr.S

Purpose: provides the ARM assembly helper entry points `strchr`. It implements NUL-terminated string scan for a byte value.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/strchr.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/strrchr.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/strrchr.S

Purpose: provides the ARM assembly helper entry points `strrchr`. It implements NUL-terminated string scan tracking the last matching byte.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/strrchr.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/testchangebit.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/testchangebit.S

Purpose: provides the ARM assembly helper entry points `_test_and_change_bit` and `_sync_test_and_change_bit` on ARMv6+. It implements test-and-toggle returning the previous bit value with ordering barriers for sync variants.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/testchangebit.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/testclearbit.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/testclearbit.S

Purpose: provides the ARM assembly helper entry points `_test_and_clear_bit` and `_sync_test_and_clear_bit` on ARMv6+. It implements test-and-clear returning the previous bit value with conditional stores.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/testclearbit.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/testsetbit.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/testsetbit.S

Purpose: provides the ARM assembly helper entry points `_test_and_set_bit` and `_sync_test_and_set_bit` on ARMv6+. It implements test-and-set returning the previous bit value with conditional stores.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/testsetbit.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/uaccess_with_memcpy.c -->
# sources/distributed-fs/ceph-client/arch/arm/lib/uaccess_with_memcpy.c

Purpose: optional large-copy acceleration for `arm_copy_to_user` and `arm_clear_user` using direct `__memcpy`/`__memset` after pinning writable user pages, while keeping standard assembly helpers for small copies.

Control flow: `pin_page_for_write` walks current mm page tables, handles huge/THP PMD leaves, locks the PTE or page-table lock, and verifies present/young/write/dirty status. Large copy/clear loops pin one page at a time, enable user access, call `__memcpy` or `__memset`, release the lock, and fault in pages with `__put_user` when pinning fails. State is page-table locks and destination user memory; no persistent globals. Dependencies include mm locks, PTE APIs, highmem/hugetlb awareness, uaccess enable/restore, and standard assembly fallbacks. Risks are races with page table changes, atomic-context mmap locking, huge page handling, threshold validity, and partial-copy accounting. Test signals include large user copies over page boundaries, COW/write-fault paths, huge/THP pages, atomic contexts, and comparison with standard uaccess behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/uaccess_with_memcpy.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/ucmpdi2.S -->
# sources/distributed-fs/ceph-client/arch/arm/lib/ucmpdi2.S

Purpose: provides the ARM assembly helper entry points `__ucmpdi2` and `__aeabi_ulcmp`. It implements unsigned 64-bit comparison returning libgcc or AEABI comparison conventions.

Control flow is straight-line or tight-loop assembly selected by architecture, endian, and Thumb/ARM configuration. There is no heap allocation or persistent state; all behavior is register and memory side effects defined by the ABI. Dependencies include `linux/linkage.h`, `asm/assembler.h`, unwind annotations where present, and callers generated by the compiler or generic kernel helpers. Integration points are the ARM lib build in `arch/arm/lib/Makefile` and symbol names expected by libgcc/AEABI, string, bit, or raw I/O APIs. Risks are register clobber mistakes, endian lane errors, misalignment behavior, and architecture-specific instruction availability. Test signals include targeted helper unit tests or boot/runtime paths that exercise the symbol, objdump checks for expected entry names, and stress tests under both ARM and Thumb2/endian configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/lib/ucmpdi2.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-actions/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-actions/Kconfig

Purpose: declares `ARCH_ACTIONS`, enabling Actions Semi S500 SoC support under `ARCH_MULTI_V7`. It selects the platform dependencies needed for AMBA, GIC, global timer, L2X0 cache, IRQ chip support, SCU/TWD for SMP, OWL power-domain helper, and OWL timer.

Control flow is Kconfig dependency resolution. No runtime state exists here; selected symbols determine which drivers and platform code are compiled. Integration points are the ARM multi-platform build and device-tree platform support. Risks are missing selects causing link or boot failures, and over-selecting features not present on future Actions variants. Test signals are randconfig/build coverage and booting an S500 DT with expected timer, interrupt, cache, and SMP components.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-actions/Kconfig -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-actions/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-actions/Makefile

Purpose: builds Actions platform SMP support. It adds `platsmp.o` when `CONFIG_SMP` is enabled.

Control flow is build-time only. There is no runtime state in the file. Dependencies are `ARCH_ACTIONS`, `CONFIG_SMP`, and the matching CPU method declared in `platsmp.c`. Risks are missing SMP object for SMP-capable DTs or compiling it without required selected drivers. Test signals are ARM Actions SMP builds and secondary CPU boot on S500.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-actions/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-actions/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-actions/platsmp.c

Purpose: implements SMP bring-up for Actions S500 systems. Key routines are `s500_smp_prepare_cpus`, `s500_smp_boot_secondary`, `s500_wakeup_secondary`, and the `CPU_METHOD_OF_DECLARE` binding for `actions,s500-smp`.

Control flow maps timer and SPS registers from DT, optionally maps/enables Cortex-A9 SCU, powers CPU2/CPU3 through `owl_sps_set_pg`, writes `secondary_startup` physical addresses and boot flags into timer scratch registers, sends `sev`, pokes reschedule IPI, then clears scratch values. Persistent state is mapped base pointers and SCU core count. Dependencies include DT compatible nodes, SPS helper, SCU support, `secondary_startup`, barriers, and IPI tracing. Risks are missing DT nodes, invalid CPU ids above 3, power-domain ack failures, and scratch-register protocol mismatches. Test signals include secondary CPU online logs, SCU enablement, and failure logs for missing timer/SPS/SCU nodes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-actions/platsmp.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/Kconfig

Purpose: declares `ARCH_ALPINE` support for Annapurna Labs Alpine V1 under ARM multi-v7 and selects interrupt, timer, syscon, PCI, MSI, and AMBA dependencies.

Control flow is Kconfig selection. It has no runtime state, but it controls compilation of machine declaration, SMP, and CPU power-management files. Risks are dependency drift for PCI/MSI or syscon services required by CPU wakeup. Test signals are Alpine defconfig/randconfig builds and DT boot with selected GIC/timer/PCI support.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/Kconfig -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/Makefile

Purpose: builds Alpine machine support. `alpine_machine.o` is always built for the platform, while `platsmp.o` and `alpine_cpu_pm.o` are added for SMP.

Control flow is build-time only. Integration depends on Kconfig and the CPU method used by Alpine DT. Risks are leaving CPU PM out of SMP builds, which would break secondary wakeup. Test signals are successful ARCH_ALPINE SMP and non-SMP links.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_pm.c

Purpose: low-level Alpine CPU power-management and wakeup service. It initializes sysfabric and CPU-resume register access and exposes `alpine_cpu_wakeup`.

Control flow: `alpine_cpu_pm_init` finds a syscon regmap and maps `al,alpine-cpu-resume`, then validates a magic watermark. `alpine_cpu_wakeup` writes a physical resume address into the per-CPU resume structure and clears the sysfabric power-control register for that CPU. Persistent state includes `al_sysfabric`, `al_cpu_resume_regs`, and `wakeup_supported`. Dependencies are DT compatible nodes, syscon/regmap, memory-mapped resume registers, and firmware that honors the resume structure. Risks are missing or invalid watermark, 32-bit resume address assumptions, and no wakeup support returning `-ENOSYS`. Test signals include SMP secondary boot, watermark validation logs/behavior, and regmap write success.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_pm.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_pm.h

Purpose: declares Alpine CPU PM interfaces `alpine_cpu_pm_init` and `alpine_cpu_wakeup`.

Control flow and state are implemented in `alpine_cpu_pm.c`; this header defines the integration contract consumed by `platsmp.c`. Dependencies are `uint32_t` availability through including C files and `__init` annotation context. Risks are signature drift between the header and implementation. Test signals are compile coverage for SMP Alpine builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_pm.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_resume.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_resume.h

Purpose: defines the memory-mapped CPU resume register layout used by Alpine firmware: global watermark/flags and a flexible per-CPU array containing flags and resume addresses.

Control flow is structural only. Runtime users validate `AL_CPU_RESUME_MAGIC_NUM_MASK` against `AL_CPU_RESUME_MAGIC_NUM` before writing resume addresses. Persistent state is the firmware-owned MMIO block. Dependencies are firmware ABI and `alpine_cpu_pm.c`. Risks are layout mismatch with firmware, missing flexible-array bounds checks, and magic-number changes. Test signals include successful watermark validation and secondary CPUs jumping to the programmed resume address.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_resume.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_machine.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_machine.c

Purpose: declares the DT machine descriptor for Annapurna Labs Alpine systems. It matches `al,alpine` and registers `DT_MACHINE_START(AL_DT, "Annapurna Labs Alpine")`.

Control flow is ARM machine selection during boot; there is no local state beyond the compatible table. Dependencies are `asm/mach/arch.h` and a matching root DT compatible. Risks are DT compatible mismatches causing no machine record to match. Test signals are boot selecting the Alpine machine descriptor.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_machine.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/platsmp.c

Purpose: implements Alpine SMP CPU boot. It initializes CPU PM in `alpine_smp_prepare_cpus` and starts secondaries in `alpine_boot_secondary` via `alpine_cpu_wakeup`.

Control flow computes the physical address of `secondary_startup`, rejects addresses above 32 bits, maps logical CPU to physical CPU, and asks firmware/sysfabric to wake it. State is delegated to `alpine_cpu_pm.c`. Dependencies include CPU logical map, firmware resume ABI, and `CPU_METHOD_OF_DECLARE("al,alpine-smp")`. Risks are 32-bit resume address overflow, missing CPU PM initialization, and firmware wakeup failure. Test signals are secondary CPU online events and error log on oversized resume address.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-alpine/platsmp.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-artpec/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-artpec/Kconfig

Purpose: declares Axis ARTPEC ARM SoC support and `MACH_ARTPEC6`. ARTPEC-6 selects AMBA, GIC, global/arch timers, PSCI, SCU/TWD, and syscon support.

Control flow is Kconfig selection. The file determines whether `board-artpec6.o` participates in the build and whether secure/cache/timer dependencies are present. Risks are incomplete selects for PSCI or cache controller integration. Test signals are ARTPEC6 build coverage and boot with expected interrupt/timer/PSCI support.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-artpec/Kconfig -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-artpec/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-artpec/Makefile

Purpose: builds `board-artpec6.o` when `CONFIG_MACH_ARTPEC6` is enabled.

Control flow is build-time only. Dependencies are the ARTPEC6 Kconfig symbol and the machine descriptor in `board-artpec6.c`. Risks are missing board object causing DT machine match failure. Test signals are successful ARTPEC6 links and machine descriptor presence in vmlinux.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-artpec/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-artpec/board-artpec6.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-artpec/board-artpec6.c

Purpose: ARTPEC-6 board/machine support. It configures a syscon DMA request mode for PL011 UARTs and supplies a secure L2C310 register write callback using SMCCC SMC calls.

Control flow: `artpec6_init_machine` looks up `axis,artpec6-syscon` and writes `ARTPEC6_DMACFG_UARTS_BURST` to the DMA config register. `artpec6_l2c310_write_sec` calls secure monitor operation `SECURE_OP_L2C_WRITEREG` and warns on failure. The machine descriptor sets L2C aux value/mask, secure write callback, init hook, and DT match `axis,artpec6`. State is only external syscon/L2C hardware. Dependencies include syscon/regmap, SMCCC, L2C platform hooks, and DT root compatible. Risks are secure firmware call failure, syscon absence, and UART DMA mode mismatch. Test signals include boot without WARN_ON, UART DMA operation, and L2 cache initialization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-artpec/board-artpec6.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/Kconfig

Purpose: declares Aspeed BMC platform support and generation-specific machine symbols for AST2400, AST2500, and AST2600 families. It selects watchdog, syscon, pinctrl, timers, CPU generation, GIC, and arch timer support as appropriate.

Control flow is Kconfig dependency selection across ARMv5/v6/v7 multi-platform builds. No runtime state exists here. Risks are selecting wrong CPU generation or missing timer/pinctrl dependencies for a SoC generation. Test signals are build coverage for G4/G5/G6 and boot on representative Aspeed DTs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/Kconfig -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/Makefile

Purpose: builds Aspeed SMP support by adding `platsmp.o` when `CONFIG_SMP` is enabled.

Control flow is build-time only. Dependencies are AST2600 SMP DT using the declared CPU method. Risks are compiling SMP support without the expected secure boot memory node or missing SMP object in AST2600 SMP builds. Test signals are successful SMP build and AST2600 secondary CPU bring-up.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/platsmp.c

Purpose: implements AST2600 SMP secondary boot through a shared secure boot memory region. Key functions are `aspeed_g6_smp_prepare_cpus`, `aspeed_g6_boot_secondary`, and the CPU method for `aspeed,ast2600-smp`.

Control flow caches the DT node `aspeed,ast2600-smpmem`, initializes the boot signature to `0xBADABABA`, and on boot maps the region, writes `secondary_startup_arm` physical address and a CPU-specific `0xABBAABxx` signature, sends `sev`, and unmaps. Persistent state is the retained DT node pointer. Dependencies include DT node mapping, secondary startup symbol, barriers, and Aspeed boot ROM/firmware polling protocol. Risks are missing node, mapping failures, stale node lifetime assumptions, and signature/address protocol mismatch. Test signals include CPU1 online on AST2600 and diagnostic logs for missing/mapping failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/platsmp.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/Kconfig

Purpose: declares AT91/Microchip SoC family selection across ARMv4T/v5/v7/v7-M, including SAMA5, SAMA7, SAM9, SAMV7, LAN966, clocksource choices, PM, clock feature flags, and shared family symbols.

Control flow is Kconfig dependency/selection logic. It drives compilation of machine, PM, timer, clock, memory, pinctrl, interrupt, and secure PM support. Persistent runtime state is outside this file; this file defines which subsystems exist. Risks include dependency mismatches between SoC families, default clocksource choices with lower resolution, and feature flags not matching hardware blocks. Test signals are randconfig/defconfig build coverage, expected object selection in `mach-at91/Makefile`, and boot on representative AT91, SAM9, SAMA5, SAMA7, and SAMV7 DTs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/Kconfig -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/Makefile

Purpose: selects AT91/Microchip platform objects based on SoC and PM Kconfig symbols, and generates PM data offset headers needed by suspend assembly/C code.

Control flow is build-time: SoC objects such as `at91rm9200.o`, `at91sam9.o`, `sam9x60.o`, `sam9x7.o`, `sama5.o`, `sama7.o`, and `samv7.o` are conditionally added; PM builds include `pm.o` and `pm_suspend.o`; `pm_data-offsets.h` is generated from `pm_data-offsets.s`. Dependencies are Kbuild `filechk`, FORCE rules, and PM code including the generated header. Risks are stale generated offsets, missing clean-files, and SoC object omissions. Test signals are clean rebuilds with PM on/off and each SoC selected.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/at91rm9200.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/at91rm9200.c

Purpose: declares the DT machine descriptor for Atmel AT91RM9200 systems. It matches `atmel,at91rm9200` and installs `at91rm9200_pm_init` as the late init hook.

Control flow is machine selection during boot followed by late PM initialization when enabled. State lives in PM code; this file holds only the compatible table and descriptor. Dependencies include `generic.h` for PM init stubs or externs and `asm/mach/arch.h`. Risks are incompatible DT root strings or missing PM support when selected. Test signals include machine match and late PM init on AT91RM9200 boot.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/at91rm9200.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/at91sam9.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/at91sam9.c

Purpose: declares the DT machine descriptor for Atmel AT91SAM9 systems. It matches `atmel,at91sam9` and installs `at91sam9_pm_init` as late init.

Control flow is ARM DT machine matching and deferred PM setup; no local persistent state exists. Dependencies include `generic.h`, system misc headers, and a matching root DT compatible. Risks are compatible mismatch and PM init being stubbed when CONFIG_PM is off. Test signals include AT91SAM9 DT boot selecting this descriptor and PM initialization behavior when enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/at91sam9.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/generic.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/generic.h

Purpose: shared AT91 header declaring SoC-specific PM initialization hooks, with no-op inline stubs when `CONFIG_PM` is disabled.

Control flow is compile-time abstraction: machine files can call late PM init unconditionally without surrounding `#ifdef CONFIG_PM`. State and implementation live in PM source files. Dependencies are matching PM function definitions for enabled SoC families. Risks are declaration/definition drift and silently no-op PM init on non-PM builds. Test signals are compile coverage with CONFIG_PM enabled and disabled for each AT91 machine descriptor.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/generic.h -->
