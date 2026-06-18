# Group Research: subset-b-000757

Grouped research for PA-RISC Linux architecture headers and kernel entry/cache/bus support in the Ceph client source tree. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/thread_info.h

Source read size: 85 lines, 2981 bytes.

Purpose: defines the PA-RISC `struct thread_info` fields embedded in `task_struct`, kernel stack sizing, thread flags, and the `is_32bit_task()` helper used by syscall, signal, scheduling, and return-to-user paths. Important APIs and types: `struct thread_info`, `INIT_THREAD_INFO`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `THREAD_SHIFT`, the `TIF_*` and `_TIF_*` bit assignments, `_TIF_USER_WORK_MASK`, `_TIF_SYSCALL_TRACE_MASK`, and `is_32bit_task()`. Control flow: this header has no runtime control flow itself, but `entry.S` consumes the exact flag bit numbers when testing need-resched, notify-resume, single-step, block-step, seccomp, audit, and 32-bit compatibility state. State and persistence: per-task mutable flags and preemption count live for the lifetime of each task; SMP builds also cache the CPU number. Dependencies and integration points: includes `asm/processor.h` and `asm/special_insns.h`, feeds assembly offsets through `asm-offsets.c`, and must stay consistent with scheduler, signal, ptrace, seccomp, audit, and syscall entry code. Risks: changing bit numbers or stack size breaks hand-written assembly and exception return logic; stack sizing is architecture-sensitive because PA-RISC requires at least 16 KiB with IRQ stacks and 32 KiB otherwise. Test signals: boot both 32-bit and 64-bit/compat kernels, run syscall tracing/seccomp/audit tests, ptrace single-step and block-step tests, signal-delivery stress, preemption scheduling tests, and stack-depth interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/timex.h

Source read size: 22 lines, 403 bytes.

Purpose: exposes PA-RISC cycle counter support for generic kernel time code. Important APIs: `CLOCK_TICK_RATE`, `cycles_t`, and `get_cycles()` which reads control register 16 through `mfctl(16)`. Control flow: callers inline one register read and receive the current architectural interval timer/cycle value. State and persistence: no persistent state is stored here; the value comes from processor control state. Dependencies and integration points: depends on `asm/special_insns.h` and is used by timing code such as cache/TLB calibration in `cache.c`. Risks: wraparound width follows `unsigned long`, so 32-bit callers must tolerate shorter wrap periods; the register semantics are hardware-specific. Test signals: validate boot-time timing calibration, delay loops, scheduler clock behavior, and monotonic cycle reads on PA-RISC hardware or QEMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/tlb.h

Source read size: 12 lines, 327 bytes.

Purpose: wires PA-RISC page-table freeing into the generic MMU-gather TLB interface. Important APIs: includes `asm-generic/tlb.h`, defines `__pmd_free_tlb()` for three-level page tables, and defines `__pte_free_tlb()`. Control flow: generic MM teardown queues freed page-table descriptors through `tlb_remove_ptdesc()` rather than immediately freeing raw pages. State and persistence: the file does not hold state; it controls deferred freeing lifetime during MMU gather batches. Dependencies and integration points: relies on `virt_to_ptdesc()`, `page_ptdesc()`, and `CONFIG_PGTABLE_LEVELS`. Risks: incorrect ptdesc conversion can corrupt page-table memory reclamation or cause use-after-free with concurrent TLB walkers. Test signals: mm teardown stress, fork/exec/exit loops, high VMA churn, three-level page table builds, and KASAN/KFENCE page-table lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/tlbflush.h

Source read size: 69 lines, 1984 bytes.

Purpose: declares and wraps PA-RISC TLB invalidation primitives. Important APIs: `flush_tlb_all()`, `flush_tlb_all_local()`, `smp_flush_tlb_all()`, `__flush_tlb_range()`, `flush_tlb_range()`, `flush_tlb_kernel_range()`, `flush_tlb_mm()`, and `flush_tlb_page()`. Control flow: range wrappers pass either a process space id or kernel space id into `__flush_tlb_range()`. `flush_tlb_mm()` currently always flushes the whole TLB, with a disabled context-switch optimization kept as a documented broken path. `flush_tlb_page()` purges entries for one VMA address. State and persistence: no owned state, but operations mutate processor and system TLB state across CPUs. Dependencies and integration points: depends on `linux/mm.h`, scheduler state, `asm/mmu_context.h`, `purge_tlb_entries()`, PA-RISC space IDs, and `cache.c` implementation. Risks: PA-RISC space/protection IDs can go out of sync; range flush broadcasts are slow and serialized on some buses; wrong mm/context handling can manifest as userspace access faults. Test signals: fork/exec/mmap/munmap stress, SMP TLB shootdown tests, kernel vmap/ioremap invalidation, page-fault selftests, and compatibility workloads with many short-lived processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/topology.h

Source read size: 19 lines, 402 bytes.

Purpose: selects generic architecture topology support when configured and provides no-op topology hooks otherwise. Important APIs: `init_cpu_topology()`, `store_cpu_topology()`, and `reset_cpu_topology()` in non-generic builds, plus inclusion of `asm-generic/topology.h`. Control flow: boot CPU topology setup either delegates to `linux/arch_topology.h` or compiles to empty inline calls. State and persistence: no state here; topology state is owned by generic topology code when enabled. Dependencies and integration points: integrates with scheduler topology, CPU masks, and optional `arch/parisc/kernel/topology.c`. Risks: no-op fallback means scheduler and sysfs topology may be flat on builds without `CONFIG_GENERIC_ARCH_TOPOLOGY`. Test signals: boot logs, `/sys/devices/system/cpu` topology, scheduler domain debug output, SMP hotplug if supported, and build coverage with topology enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/traps.h

Source read size: 24 lines, 667 bytes.

Purpose: declares PA-RISC trap and fault handling entry points shared between assembly, traps, and MM fault code. Important APIs: `PARISC_ITLB_TRAP`, `parisc_terminate()`, `die_if_kernel()`, `parisc_acctyp()`, `trap_name()`, `do_page_fault()`, and `handle_nadtlb_fault()`. Control flow: `entry.S` passes interruption codes into C handlers which use these prototypes to terminate, decode access type, or service page faults. State and persistence: no stored state, but handlers consume and mutate `pt_regs` and task signal/fault state. Dependencies and integration points: integrates with `kernel/traps.c`, `mm/fault.c`, `entry.S`, and ptrace-visible register state. Risks: the ITLB trap code is architecturally fixed; changing prototypes or codes breaks assembly-to-C exception dispatch. Test signals: illegal instruction, page fault, protection fault, non-access TLB fault, kernel oops, and signal-delivery tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/uaccess.h

Source read size: 203 lines, 5409 bytes.

Purpose: implements PA-RISC low-level user memory access macros and declarations. Important APIs: `get_user`, `put_user`, `__get_user_internal()`, `__probe_user_internal()`, `__get_user_asm()`, `__put_user_internal()`, `__put_user_asm()`, 32-bit `__get_user_asm64()` and `__put_user_asm64()`, kernel nofault helpers, `strncpy_from_user()`, `lclear_user()`, `strnlen_user()`, `raw_copy_to_user()`, and `raw_copy_from_user()`. Control flow: size-switching macros emit space-register qualified PA-RISC loads/stores with exception-table fixups; `get_user` performs the load then probes user accessibility; 32-bit kernels split 64-bit transfers into two word operations. State and persistence: no durable state; failures are returned as `-EFAULT` through exception-table variables. Dependencies and integration points: relies on PA-RISC space registers `SR_USER`/`SR_KERNEL`, `asm/extable.h`, generic `access_ok`, page/table sizing, and lib/usercopy assembly. Risks: inline assembly constraints and fixup labels are correctness-critical; misdeclared clobbers can let GCC reorder around faulting accesses; 64-bit split accesses can partially complete; userspace pointer checking depends on both access_ok and probe behavior. Test signals: LKDTM/usercopy tests, copy_{to,from}_user fault injection, `strnlen_user` boundary tests, nofault access tests, 32-bit 64-bit-value get/put tests, and syscall fuzzing with invalid pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ucontext.h

Source read size: 13 lines, 327 bytes.

Purpose: provides the kernel-internal PA-RISC `ucontext` wrapper by including the UAPI signal-context contract. Important APIs and types: `struct ucontext` with flags, link pointer, stack, `struct sigcontext`, and signal mask. Control flow: signal setup and return code populate or consume this layout when building user signal frames. State and persistence: state is transient but user-visible on the signal stack; ABI layout persists across kernel versions. Dependencies and integration points: includes `uapi/asm/sigcontext.h` and `asm/sigmask.h`, and is consumed by `signal.c`, `signal32.c`, and `asm-offsets.c`. Risks: layout changes break signal ABI and unwind/debug tooling. Test signals: signal frame round trips, `sigaltstack`, `rt_sigreturn`, ptrace over signal stops, and compat signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/unistd.h

Source read size: 151 lines, 4895 bytes.

Purpose: connects PA-RISC syscall numbers to kernel code and defines the architecture's inline syscall calling convention. Important APIs/macros: includes UAPI `unistd.h`, `__NR_Linux_syscalls`, `SYS_ify`, `K_INLINE_SYSCALL`, `K_LOAD_ARGS_0..6`, `K_ASM_ARGS_*`, `K_CLOB_ARGS_*`, `syscall0..5`, and `__ARCH_WANT_*` feature selectors. Control flow: inline syscalls load arguments into PA-RISC ABI registers r26..r21, place the syscall number in r20, branch through the gateway at `0x100(%sr2,%r0)`, and preserve PIC register r19 via r4 when needed. State and persistence: no owned state; it defines ABI register effects and generic syscall table inclusion. Dependencies and integration points: used by kernel code that performs internal syscalls and by syscall table generation; paired with `entry.S` gateway/syscall exit behavior. Risks: register clobber lists, PIC save/restore, and `__ARCH_WANT_*` selections are ABI-sensitive; wrong constraints can silently corrupt caller state. Test signals: syscall ABI tests, seccomp/audit syscall classification, 32-bit and 64-bit syscall table builds, and inline syscall smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/unwind.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/unwind.h

Source read size: 85 lines, 2723 bytes.

Purpose: defines PA-RISC unwind table metadata and stack-walking interfaces. Important APIs/types: `MAX_UNWIND_ENTRIES`, `struct unwind_table_entry` with ABI bitfields, `struct unwind_table`, `struct unwind_frame_info`, and functions `unwind_frame_init()`, `unwind_frame_init_from_blocked_task()`, `unwind_once()`, `unwind_to_user()`, and `unwind_init()`. Control flow: unwind code uses ABI table entries to determine saved registers, frame size, and continuation state while walking kernel or blocked-task stacks. State and persistence: unwind tables are linked on a list and persist for core kernel/modules; frame info is per-walk transient. Dependencies and integration points: consumed by `kernel/unwind.c`, stacktrace, oops reporting, ftrace, and module unwind registration. Risks: C bitfield layout must match PA-RISC unwind ABI; bad region bounds or frame rules produce broken stack traces or unsafe unwinds. Test signals: stacktrace selftests, oops/backtrace output, module load/unload unwind coverage, blocked-task traces, and ftrace/function-graph tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/vdso.h

Source read size: 25 lines, 664 bytes.

Purpose: declares PA-RISC vDSO symbol lookup helpers and version/link constants. Important APIs: `VDSO64_SYMBOL()`, `VDSO32_SYMBOL()`, `VDSO_LBASE`, and `VDSO_VERSION_STRING`. Control flow: signal and exec setup code add generated offsets to `mm->context.vdso_base` to locate vDSO trampoline symbols; absent 32-bit support returns zero for `VDSO32_SYMBOL`. State and persistence: per-mm `vdso_base` persists for the process address space. Dependencies and integration points: includes generated `vdso64-offsets.h`/`vdso32-offsets.h`, integrates with `kernel/vdso.c`, `vdso32/`, `vdso64/`, and signal trampolines. Risks: generated offset headers must match the linked vDSO image; version-string changes affect userspace tooling expectations. Test signals: auxv `AT_SYSINFO_EHDR`, signal trampoline execution, restart syscall behavior, 32-bit compat vDSO tests, and vdso symbol inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/video.h

Source read size: 16 lines, 353 bytes.

Purpose: provides the PA-RISC hook for selecting the primary video device when STI core and generic video support are enabled. Important APIs: optional `video_is_primary_device(struct device *)` override plus generic video inclusion. Control flow: generic video helpers call the architecture hook only in enabled configurations; otherwise behavior falls back to `asm-generic/video.h`. State and persistence: no state here. Dependencies and integration points: depends on `CONFIG_STI_CORE`, `CONFIG_VIDEO`, generic video, and PA-RISC STI console/video drivers. Risks: wrong primary-device selection can choose the wrong framebuffer/console on systems with multiple display devices. Test signals: boot console selection, framebuffer registration order, multi-GPU/STI systems, and build coverage with and without STI/video enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/vmalloc.h

Source read size: 4 lines, 96 bytes.

Purpose: placeholder architecture vmalloc header for PA-RISC. Important APIs: none defined directly. Control flow: none. State and persistence: none. Dependencies and integration points: satisfies generic includes that expect `asm/vmalloc.h`; actual vmap/vmalloc cache coherency lives in `kernel/cache.c`. Risks: future additions must coordinate with PA-RISC cache/TLB flushing semantics. Test signals: build coverage and vmalloc/vmap/ioremap cache flush tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/Kbuild

Source read size: 3 lines, 89 bytes.

Purpose: tells Kbuild to generate PA-RISC UAPI syscall number headers. Important outputs: `unistd_32.h` and `unistd_64.h`. Control flow: during headers generation, Kbuild emits the generated headers from syscall tables. State and persistence: generated files become exported UAPI artifacts for userspace builds. Dependencies and integration points: integrates with syscall table generation and `include/uapi/asm/unistd.h`. Risks: omitting a generated header breaks 32-bit or 64-bit userspace header installation. Test signals: `make headers_install`, cross-compile UAPI header checks, and syscall-number consistency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/auxvec.h

Source read size: 8 lines, 213 bytes.

Purpose: defines PA-RISC auxiliary vector keys visible to userspace. Important API: `AT_SYSINFO_EHDR` value 33 identifies the vDSO ELF header base. Control flow: exec setup places this auxv entry when a vDSO is mapped; userspace dynamic linkers read it. State and persistence: per-process auxv persists from exec until process exit. Dependencies and integration points: paired with vDSO mapping and libc/dynamic linker startup. Risks: changing the numeric value breaks userspace ABI. Test signals: inspect `/proc/self/auxv`, libc vdso detection, and signal/vdso startup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/bitsperlong.h

Source read size: 13 lines, 302 bytes.

Purpose: selects userspace word size for PA-RISC headers. Important API: `__BITS_PER_LONG` is 64 under `__LP64__`, otherwise 32, then generic bits-per-long definitions are included. Control flow: preprocessor-only selection. State and persistence: ABI compile-time contract for structure layouts. Dependencies and integration points: used by IPC, signal, socket, and generic UAPI headers. Risks: incorrect LP64 detection changes layout of user-visible structs. Test signals: 32-bit and 64-bit headers_install, libc type-size checks, and ABI structure-size tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/byteorder.h

Source read size: 7 lines, 194 bytes.

Purpose: declares PA-RISC userspace byte order as big-endian. Important API: includes `linux/byteorder/big_endian.h`. Control flow: none beyond preprocessing. State and persistence: compile-time ABI contract. Dependencies and integration points: used by networking, filesystem, and binary interface headers. Risks: any accidental little-endian assumption corrupts userspace protocol and structure interpretation. Test signals: headers_install, endian conversion compile tests, network packet tests, and filesystem image interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/cachectl.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/cachectl.h

Source read size: 12 lines, 354 bytes.

Purpose: exposes PA-RISC `cacheflush` syscall cache selector bits to userspace. Important APIs: `ICACHE`, `DCACHE`, and `BCACHE`. Control flow: userspace passes these bits to `SYSCALL_DEFINE3(cacheflush)` in `cache.c`, which flushes data and/or instruction cache ranges. State and persistence: no persistent header state; syscall mutates CPU cache state. Dependencies and integration points: JITs, dynamic code generators, and libc wrappers depend on these constants. Risks: bit changes break self-modifying code and JIT cache synchronization. Test signals: userspace JIT/self-modifying-code tests and invalid-pointer/range `cacheflush` syscall tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/cachectl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/errno.h

Source read size: 127 lines, 5745 bytes.

Purpose: defines PA-RISC userspace errno numbering, combining generic base errors with HP-UX-compatible and Linux-specific values. Important APIs: constants from `ENOMSG` through `EHWPOISON`, aliases such as `EDEADLOCK`, `EWOULDBLOCK`, `ECANCELED`, and filesystem aliases `EFSBADCRC`/`EFSCORRUPTED`. Control flow: none; syscall return decoding and libc use these numbers. State and persistence: permanent userspace ABI. Dependencies and integration points: libc, strace, audit, network/filesystem syscalls, and compatibility code. Risks: numeric changes are ABI-breaking and can make userspace mis-handle syscall failures; PA-RISC values differ from many other Linux architectures. Test signals: libc errno tables, strace decoding, syscall failure tests, and cross-arch ABI validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/fcntl.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/fcntl.h

Source read size: 39 lines, 1024 bytes.

Purpose: defines PA-RISC file open and fcntl command constants before including generic fcntl definitions. Important APIs: architecture-specific `O_*` flag values, `F_GETLK64`, `F_SETLK64`, `F_SETLKW64`, socket-owner fcntl commands, and lock-type constants. Control flow: userspace passes these values to open/fcntl syscalls; kernel VFS decodes them. State and persistence: file descriptor flags and locks persist in kernel objects, while constants are ABI. Dependencies and integration points: VFS, libc, POSIX locking, socket ownership, and compat syscall handling. Risks: PA-RISC flag numbers are non-generic; changing or mixing them breaks binaries and wrong-open flag decoding. Test signals: open flag tests, large-file locking tests, socket `F_SETOWN`/`F_SETSIG`, and headers_install ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctl.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctl.h

Source read size: 45 lines, 1710 bytes.

Purpose: defines PA-RISC ioctl command encoding direction bits and includes generic ioctl helpers. Important APIs: `_IOC_NONE`, `_IOC_WRITE`, `_IOC_READ`, and generic `_IOC` macros. Control flow: ioctl numbers encode command, size, and access direction; kernel ioctl handlers and compat layers decode them. State and persistence: ioctl numbers are permanent userspace ABI. Dependencies and integration points: tty, serial, block, network, and driver UAPI headers. Risks: PA-RISC direction-bit ordering differs from common expectations; wrong encoding causes compat failures or user-buffer size mismatches. Test signals: ioctl-number compile tests, tty ioctl tests, strace decode, and 32/64-bit compat ioctl smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctls.h

Source read size: 101 lines, 3752 bytes.

Purpose: declares PA-RISC tty, pty, serial, and file ioctl request numbers. Important APIs: `TCGETS`, `TCSETS*`, `TCGETA`, `TIOCGWINSZ`, `TIOCSWINSZ`, `FIONREAD`, `FIONBIO`, `TIOC*` serial/pty commands, packet-mode bits, and `TIOCSER_TEMT`. Control flow: userspace issues these constants through `ioctl`; tty/serial subsystems interpret them using PA-RISC ioctl encoding. State and persistence: tty settings, pty locks, packet state, and serial settings persist in device state; constants are ABI. Dependencies and integration points: `termbits.h`, tty core, serial drivers, pty, and libc termios. Risks: numeric overlaps or structure-size mismatches break terminal control; several legacy constants are raw numeric values rather than generic macro expansions. Test signals: POSIX terminal tests, pty open/lock tests, serial ioctl tests, `stty` behavior, and compat ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ipcbuf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ipcbuf.h

Source read size: 33 lines, 837 bytes.

Purpose: defines PA-RISC `ipc64_perm` layout for SysV IPC permissions. Important type: `struct ipc64_perm` with key, uid/gid, creator uid/gid, mode, sequence, padding, and unused expansion fields. Control flow: kernel SysV IPC syscalls copy this layout to/from userspace. State and persistence: describes persistent IPC object metadata for message queues, semaphores, and shared memory. Dependencies and integration points: included by `msgbuf.h`, `sembuf.h`, and `shmbuf.h`, with `bitsperlong` affecting padding. Risks: layout must remain stable across 32/64-bit userspace; `seq` is intentionally `unsigned short`/padding-sensitive. Test signals: SysV IPC creation/stat/control tests on 32-bit and 64-bit PA-RISC, structure-size checks, and libc IPC ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ipcbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/mman.h

Source read size: 89 lines, 4003 bytes.

Purpose: defines PA-RISC memory-protection, mapping, msync, mlock, madvise, and pkey constants. Important APIs: `PROT_*`, architecture-specific `MAP_TYPE`, `MAP_FIXED`, `MAP_ANONYMOUS`, `MAP_*` flags, `MS_*`, `MCL_*`, `MLOCK_ONFAULT`, `MADV_*`, `MAP_FILE`, and pkey disable bits. Control flow: mmap/mprotect/msync/mlock/madvise syscalls consume these constants; PA-RISC address-coloring and cache aliasing rules make mapping flags especially visible in MM behavior. State and persistence: mappings and locks persist in VMAs and mm state. Dependencies and integration points: generic mm, PA-RISC `arch_get_unmapped_area`, cache alias flushing in `cache.c`, libc mmap wrappers. Risks: PA-RISC map-type mask includes nonstandard bits; wrong constants break binary mmap behavior and cache-coherency assumptions for executable mappings. Test signals: mmap/mprotect/mremap/munmap tests, executable mapping coherency, shared memory alias tests, mlock/madvise selftests, and 32/64-bit ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/msgbuf.h

Source read size: 40 lines, 1246 bytes.

Purpose: defines PA-RISC `msqid64_ds` layout for SysV message queues. Important type: `struct msqid64_ds` containing `ipc64_perm`, split or native time fields, queue byte/message counters, last sender/receiver PIDs, and padding. Control flow: msgctl IPC_STAT/IPC_SET copies this structure between kernel and userspace. State and persistence: describes persistent message queue state. Dependencies and integration points: depends on `bitsperlong.h` and `ipcbuf.h`; used by SysV IPC and libc. Risks: split high/low time fields on 32-bit builds and padding must remain ABI-compatible. Test signals: msgget/msgsnd/msgrcv/msgctl tests, y2038/time-size checks, and 32-bit compat structure-size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/msgbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/pdc.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/pdc.h

Source read size: 746 lines, 25054 bytes.

Purpose: exposes the PA-RISC Processor Dependent Code firmware ABI constants and structures used by kernel firmware calls and some tooling. Important APIs/types: PDC status codes, procedure/option constants for chassis, PIM, model, cache, HPA, IODC, TOD, stable storage, memory, system map, PCI, reset, STI, performance and many others; `struct hardware_path`, `pdc_module_path`, `pz_device`, `zeropage`, `pdc_model`, `pdc_cache_info`, `pdc_iodc`, `pdc_btlb_info`, memory/system-map structs, PIM/TOC structs, and CPU-id constants. Control flow: kernel firmware wrappers pass these procedure numbers and structure layouts to firmware; bus discovery, cache initialization, crash/PIM handling, QEMU header generation, and boot code decode returned structures. State and persistence: firmware state includes stable storage, boot paths, chassis status, PDC results, memory error tables, and page-zero boot data. Dependencies and integration points: consumed by `firmware.c`, `drivers.c`, `cache.c`, `setup.c`, crash/HPMC/TOC handlers, and userspace headers. Risks: layout, alignment, bitfield, and numeric stability are critical; LP64 bitfields and page-zero offsets are especially fragile; firmware can return partial/unsupported data. Test signals: boot on multiple PA-RISC machines/QEMU, PDC cache/model/system-map calls, device inventory, PIM/TOC reporting, crash dump prep, and headers_install ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/pdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/perf_regs.h

Source read size: 63 lines, 1427 bytes.

Purpose: enumerates PA-RISC registers exposed through perf sample register masks. Important API: `enum perf_event_parisc_regs` covering general registers, space registers, IAOQ/IASQ, SAR, IIR, ISR, IOR, IPSW, and `PERF_REG_PARISC_MAX`. Control flow: perf core and `perf_regs.c` map enum indices to `pt_regs` fields when collecting samples. State and persistence: sample register state is transient per perf event sample. Dependencies and integration points: must match `struct user_regs_struct` and PA-RISC perf implementation. Risks: enum reordering breaks perf userspace decoding. Test signals: `perf record` with register sampling, DWARF/unwind correlation, and userspace perf header decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/posix_types.h

Source read size: 24 lines, 639 bytes.

Purpose: defines PA-RISC-specific kernel POSIX scalar types before generic type completion. Important APIs: 32-bit `__kernel_mode_t`, `__kernel_ipc_pid_t`, `__kernel_off64_t`, and `__kernel_ino64_t`. Control flow: no runtime flow; headers use these typedefs when compiling userspace interfaces. State and persistence: compile-time ABI type sizes. Dependencies and integration points: generic posix types, stat/IPС/socket headers, libc. Risks: type-size drift changes structure layouts and syscall ABI. Test signals: headers_install, libc type conformance, stat/IPC structure layout tests on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ptrace.h

Source read size: 96 lines, 2820 bytes.

Purpose: defines PA-RISC ptrace-visible register layouts and ptrace request numbers. Important APIs/types: legacy `struct pt_regs`, `struct user_regs_struct`, `struct user_fp_struct`, `PTRACE_SINGLEBLOCK`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETFPREGS`, and `PTRACE_SETFPREGS`. Control flow: ptrace and regset code copy these structures for debuggers, strace, core dumps, and signal inspection. State and persistence: register snapshots are per-task transient but core-file and debugger ABI is stable. Dependencies and integration points: `entry.S`, signal frames, ELF gregset/fpregset, perf register enum, gdb/strace. Risks: comments note gdb/strace depend on size and offsets; changing layouts breaks object compatibility. Test signals: gdb single-step/block-step, ptrace GET/SETREGS/FPREGS, core dump register notes, and strace syscall tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sembuf.h

Source read size: 33 lines, 908 bytes.

Purpose: defines PA-RISC `semid64_ds` for SysV semaphores. Important type: `struct semid64_ds` with `ipc64_perm`, 64-bit or split time fields, semaphore count, and padding. Control flow: semctl IPC_STAT/IPC_SET copies this structure. State and persistence: describes persistent semaphore array metadata. Dependencies and integration points: `bitsperlong.h`, `ipcbuf.h`, SysV semaphore core, libc. Risks: time field order and padding differ by word size and must remain ABI-stable. Test signals: semget/semop/semctl IPC_STAT tests, 32-bit compat layout checks, and y2038 coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sembuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/setup.h

Source read size: 7 lines, 173 bytes.

Purpose: exposes PA-RISC boot command-line size. Important API: `COMMAND_LINE_SIZE` set to 1024. Control flow: boot/setup code uses this bound when copying or parsing kernel command lines. State and persistence: boot command line persists in early boot/init state and procfs. Dependencies and integration points: setup and boot loader handoff. Risks: truncation beyond 1024 bytes can drop boot parameters; changing the value affects boot ABI expectations. Test signals: boot with long command lines and inspect `/proc/cmdline`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/shmbuf.h

Source read size: 53 lines, 1481 bytes.

Purpose: defines PA-RISC SysV shared-memory metadata layouts. Important types: `struct shmid64_ds` and `struct shminfo64`, including permissions, split/native time fields, segment size, creator/last PID, attach count, limits, and padding. Control flow: shmctl IPC_STAT/IPC_INFO/SHM_INFO copies these layouts. State and persistence: describes persistent shared memory segment state and system limits. Dependencies and integration points: `bitsperlong.h`, `ipcbuf.h`, `posix_types.h`, SysV shm core, libc. Risks: 32-bit split time fields and `__kernel_size_t` sizing affect ABI. Test signals: shmget/shmat/shmdt/shmctl tests, 32-bit compat layout checks, and IPC namespace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/shmbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sigcontext.h

Source read size: 21 lines, 557 bytes.

Purpose: defines the PA-RISC user signal context saved in signal frames. Important APIs/types: `PARISC_SC_FLAG_ONSTACK`, `PARISC_SC_FLAG_IN_SYSCALL`, and `struct sigcontext` with flags, general registers, floating-point registers, instruction space/offset queues, and SAR. Control flow: signal delivery fills the structure; `rt_sigreturn` restores user state from it. State and persistence: signal frame state exists on the user stack until consumed and is user-visible ABI. Dependencies and integration points: `signal.c`, `signal32.c`, `entry.S`, ptrace, debuggers, and libc signal trampolines. Risks: incomplete or changed register state corrupts signal return or debugger unwinding; flags encode syscall interruption semantics. Test signals: signal delivery/return, altstack, interrupted syscall restart, FP register preservation, and ptrace over signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/signal.h

Source read size: 84 lines, 1795 bytes.

Purpose: defines PA-RISC signal numbers, signal action flags, stack sizes, and signal set types. Important APIs/types: `SIG*` numbers, `SIGRTMIN`, `SIGRTMAX`, `SA_*`, `MINSIGSTKSZ`, `SIGSTKSZ`, `_NSIG`, `_NSIG_WORDS`, `old_sigset_t`, `sigset_t`, and `stack_t`. Control flow: signal syscalls and libc use these constants to install handlers, block masks, and alt stacks. State and persistence: signal masks and altstack settings persist per task; constants are permanent ABI. Dependencies and integration points: generic signal definitions, `sigcontext.h`, `ucontext.h`, and PA-RISC signal entry/return code. Risks: PA-RISC signal numbering differs from some architectures; changing it breaks all userspace signal handling. Test signals: POSIX signal tests, realtime signal queueing, sigaltstack, mask manipulation, and compat signal ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/socket.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/socket.h

Source read size: 173 lines, 4314 bytes.

Purpose: defines PA-RISC socket option numbers and timestamp/timeval compatibility selection. Important APIs: `SOL_SOCKET`, `SO_*` and `SCM_*` constants through modern options such as BPF, zerocopy, txtime, busy-poll, pidfd, devmem, passrights, and inq; old/new timestamp and timeout aliases selected by word/time size. Control flow: userspace passes constants to getsockopt/setsockopt and receives SCM control messages; preprocessor aliases select old or new time ABI outside the kernel. State and persistence: socket options persist in socket state; timestamp control messages are per packet. Dependencies and integration points: networking core, libc, `sockios.h`, time64 transition code, and compat syscalls. Risks: PA-RISC option values are architecture-specific and time-size aliases are subtle for 32-bit userspace. Test signals: socket option selftests, timestamping tests, BPF attach/detach, zerocopy, pidfd socket options, and 32-bit time64 ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/stat.h

Source read size: 68 lines, 1803 bytes.

Purpose: defines PA-RISC `struct stat` and `struct stat64` layouts. Important types: legacy `struct stat` with 32-bit device/inode/size/time fields plus HP-UX-derived spare fields, `STAT_HAVE_NSEC`, and `struct stat64` with 64-bit dev/rdev/size/blocks/inode and nanosecond fields. Control flow: stat-family syscalls copy these layouts to userspace. State and persistence: describes filesystem metadata snapshots. Dependencies and integration points: VFS stat code, libc, compat stat syscalls, and `asm/unistd.h` feature selectors. Risks: layout is unusual and explicitly intended to avoid wrappers for 32-bit userspace; changing fields breaks libc and old binaries. Test signals: stat/lstat/fstat/statx comparisons, large inode and large file tests, nanosecond timestamp tests, and 32/64-bit ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/statfs.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/statfs.h

Source read size: 8 lines, 181 bytes.

Purpose: selects the PA-RISC word type for `statfs` structures and includes the generic layout. Important API: `__statfs_word` is `long`. Control flow: statfs/fstatfs syscalls use the resulting generic structure layout. State and persistence: filesystem statistics are returned as snapshots. Dependencies and integration points: generic statfs UAPI and VFS statfs implementations. Risks: word-size differences affect 32/64-bit userspace structure layout. Test signals: statfs/fstatfs tests on several filesystem types and compat layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/termbits.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/termbits.h

Source read size: 149 lines, 3628 bytes.

Purpose: defines PA-RISC termios structures, control-character indexes, line discipline flags, baud rates, and tcsetattr action values. Important APIs/types: `tcflag_t`, `NCCS`, `struct termios`, `struct termios2`, `struct ktermios`, `VINTR` through `VEOL2`, `IUCLC`/`IXON`/`IXOFF`, output delay masks, `CBAUD`, `BOTHER`, extended baud constants, local flags, and termios action constants. Control flow: tty ioctl handlers copy these structures and update terminal state. State and persistence: termios settings persist per tty until changed. Dependencies and integration points: `ioctls.h`, tty core, serial drivers, libc `termios`, shells and terminal tools. Risks: `NCCS` and numeric flags are ABI-specific; wrong baud or c_cc indexes break terminal behavior. Test signals: `stty`, pty/tty selftests, serial baud tests, canonical/raw mode tests, and compat ioctl layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/termbits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/unistd.h

Source read size: 13 lines, 292 bytes.

Purpose: provides the exported PA-RISC syscall-number header by including generated 32-bit or 64-bit syscall lists according to `__BITS_PER_LONG`. Important APIs: generated `unistd_32.h`/`unistd_64.h` contents and `__NR_syscalls`. Control flow: preprocessor selects the generated table for userspace compilation. State and persistence: syscall numbers are permanent ABI. Dependencies and integration points: Kbuild generated headers, libc syscall wrappers, seccomp, audit, strace, and kernel syscall table. Risks: wrong word-size selection or generated-header drift breaks every syscall wrapper. Test signals: headers_install, syscall table consistency scripts, seccomp filter tests, strace syscall number decoding, and 32/64-bit userspace smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/install.sh -->
# sources/distributed-fs/ceph-client/arch/parisc/install.sh

Source read size: 41 lines, 900 bytes.

Purpose: architecture install helper for `make install` on PA-RISC. Important behavior: accepts kernel version, image file, System.map, and install path; detects compressed `vmlinuz` by basename, rotates existing image and System.map to `.old`, copies/cats the new artifacts, and exits on errors via `set -e`. Control flow: choose base name, rotate old target if present, write image, rotate old map if present, copy map. State and persistence: mutates files under the requested install path. Dependencies and integration points: invoked by kernel build install targets and boot-loader packaging workflows. Risks: unquoted positional parameters make spaces unsafe; `cat >` can leave partial images on interruption; no permission/disk-space preflight. Test signals: run with temporary install directory for compressed and uncompressed image names, existing-file rotation, missing argument failure, and shellcheck-style quoting review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/Makefile

Source read size: 54 lines, 1818 bytes.

Purpose: builds the PA-RISC kernel object set and optional architecture features. Important targets/variables: `always-$(KBUILD_BUILTIN) := vmlinux.lds`, core `obj-y` list for boot, cache, traps, time, irq, syscall, entry, firmware, hardware, drivers, alternatives, signal, unwind, patching and TOC; conditional objects for SMP, PA11 DMA, PCI, modules, 64-bit compat, stacktrace, audit, perf, topology, ftrace, jump labels, KGDB, kprobes, kexec, and vDSO subdirectories. Control flow: Kbuild includes or excludes objects based on config, and removes ftrace profiling from low-level files. State and persistence: build configuration determines linked kernel contents. Dependencies and integration points: architecture Kconfig, vDSO Makefiles, low-level assembly, and linker script generation. Risks: profiling low-level entry/cache/patch/unwind code can break tracing recursion; missing conditional objects produce unresolved symbols only in specific configs. Test signals: allmodconfig/defconfig builds for 32-bit and 64-bit, ftrace/perf/kexec/kprobes configs, and vDSO build validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/alternative.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/alternative.c

Source read size: 122 lines, 3376 bytes.

Purpose: applies PA-RISC runtime instruction alternatives for CPU/platform-specific optimization and errata handling. Important APIs/functions: boot parameter `no-alternatives`, `apply_alternatives()`, and `apply_alternatives_all()`. Control flow: compute condition mask from CPU count, cache presence, QEMU, split TLB, and IO-PDIR flush capability; iterate alternative entries, skip disabled conditions, rewrite original instructions or copy replacement sequences, special-case PxTLB local/extended-bit replacement, and disable cache static keys when hardware has no caches. State and persistence: patches kernel/module text and toggles static branches; `no_alternatives` persists after boot parameter parsing. Dependencies and integration points: `alt_instr` tables, `set_kernel_text_rw()`, cache flush/static keys, CPU/PDC capability state, modules. Risks: text patching length/sign semantics and instruction encodings are fragile; wrong condition mask can execute unsupported instructions; patching requires writable text window discipline. Test signals: boot with and without `no-alternatives`, QEMU vs hardware, SMP vs UP, no-cache configs, module alternatives, and disassembly/static-key checks after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/alternative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/asm-offsets.c

Source read size: 290 lines, 15657 bytes.

Purpose: generates assembler constants for PA-RISC C structure offsets and sizes. Important outputs: task/thread offsets, full `pt_regs` register offsets, thread-info flags/preempt count, signal frame sizes, PDC cache offsets, TIF bit positions in PA bit numbering, page-table geometry constants, hugepage alignment size, and PDC result buffer size. Control flow: the build compiles and runs this C file through the kernel offset-generation machinery; `DEFINE()` emits assembly-readable constants consumed by hand-written assembly. State and persistence: generated offsets persist in build artifacts and must match the exact compiled C layouts. Dependencies and integration points: consumed heavily by `entry.S`, signal code, pacache/low-level assembly, and linker scripts. Risks: missing a changed structure field or wrong alignment formula breaks trap/syscall save/restore, signal frames, cache loops, or page-table walking in assembly. Test signals: full architecture build, objdump sanity of generated offsets, boot trap/syscall tests, signal-frame tests, and 32/64-bit/compat build matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/audit.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/audit.c

Source read size: 83 lines, 1964 bytes.

Purpose: implements PA-RISC audit syscall and class classification. Important APIs/functions: audit class arrays for write/read/dir-write/chattr/signal, `audit_classify_arch()`, `audit_classify_syscall()`, and `audit_classes_init()`. Control flow: syscall classification recognizes open/openat/execve/openat2 specially, returns compat classification for 32-bit ABI under `CONFIG_COMPAT`, and registers native plus optional 32-bit audit classes at init. State and persistence: audit class registrations persist for audit subsystem lifetime. Dependencies and integration points: generic audit class include lists, `asm/unistd.h`, `compat_audit.c`, audit core. Risks: syscall-number drift or missing compat class registration causes incorrect audit rules and records. Test signals: audit rule tests for open/exec, compat 32-bit syscall audit, openat2 classification, and boot audit class registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/cache.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/cache.c

Source read size: 979 lines, 26672 bytes.

Purpose: implements PA-RISC cache and TLB management, including boot cache discovery, coherency maintenance, page/vmap flushing, TLB range flushing, and userspace `cacheflush`. Important APIs/functions: exported `flush_dcache_page_asm`, `flush_cache_all[_local]`, `__update_cache()`, `show_cache_info()`, `parisc_cache_init()`, `disable_sr_hashing()`, `flush_icache_pages()`, `flush_dcache_folio()`, `parisc_setup_cache_timing()`, `copy_user_highpage()`, `copy_to_user_page()`, `copy_from_user_page()`, `__flush_tlb_range()`, `flush_cache_mm/range/page`, `ptep_clear_flush_young()`, `ptep_clear_flush()`, `flush_cache_vmap/vunmap`, `flush_kernel_vmap_range()`, `invalidate_kernel_vmap_range()`, and `cacheflush` syscall. Control flow: boot reads PDC cache/TLB info, determines split TLB and cache strides, and sets thresholds. Page flushing first purges relevant TLB translations to prevent speculative cache move-in, then uses temporary alias assembly flushes under preemption disable. Range and mm flushes choose whole-cache/TLB flushing versus per-page flushing based on aliasing/coherency and measured thresholds. Vmap/ioremap paths flush kernel TLBs, use physical IO ranges when possible, and otherwise fall back to whole-cache flushing. State and persistence: global cache descriptors, split-TLB flag, stride values, static keys, thresholds, and TLB serialization lock persist after boot; page dirty-cache bits persist on folios until flushed. Dependencies and integration points: PDC firmware, `pacache.S`, MM/VMA/folio APIs, TLB space IDs, vmalloc/ioremap, DMA coherency, user `cacheflush`, and alternative/static-key code. Risks: PA8800/PA8900 aliasing and speculative cache behavior can cause random corruption if TLB/cache order is wrong; IRQ-disabled SMP whole flushes are unsafe; `get_upa()` temporarily switches MM context; threshold timing is heuristic. Test signals: mmap/shared-alias stress, JIT cacheflush tests, fork/exec/mprotect churn, vmalloc/ioremap/DMA tests, SMP TLB shootdown stress, highmem kmap tests, and boot cache-info validation on multiple CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/compat_audit.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/compat_audit.c

Source read size: 28 lines, 524 bytes.

Purpose: provides 32-bit PA-RISC audit syscall class arrays for 64-bit kernels with compat support. Important exports: `parisc32_dir_class`, `parisc32_chattr_class`, `parisc32_write_class`, `parisc32_read_class`, and `parisc32_signal_class`. Control flow: arrays are built from generic audit include lists and registered by `audit.c` during audit class initialization. State and persistence: class tables are static read-mostly data for audit rule matching. Dependencies and integration points: `linux/audit_arch.h`, generated syscall numbers, generic audit class headers, and `audit.c`. Risks: table mismatch with 32-bit syscall numbering produces incorrect audit filtering for compat tasks. Test signals: 32-bit userspace audit tests on a 64-bit kernel, write/read/chattr/signal rule matching, and build coverage with `CONFIG_AUDIT` and `CONFIG_COMPAT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/compat_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/drivers.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/drivers.c

Source read size: 1108 lines, 29636 bytes.

Purpose: implements the PA-RISC bus type, firmware-driven device inventory, driver registration, hardware-path conversion, native bus probing, and optional QEMU header dumping. Important APIs/functions: exported `hppa_dma_ops`, `register_parisc_driver()`, `unregister_parisc_driver()`, `count_parisc_driver()`, `find_pa_parent_type()`, `print_pa_hwpath()`, `get_pci_node_path()`, `print_pci_hwpath()`, `alloc_pa_dev()`, `hwpath_to_device()`, `device_to_hwpath()`, `walk_central_bus()`, `init_parisc_bus()`, and `print_parisc_devices()`. Control flow: boot registers the `parisc` bus and root device, inventory code creates tree nodes from firmware hardware paths, reads IODC bytes to identify devices, claims HPA resources, recursively walks native/lower buses for devices firmware omitted, and normal driver-core matching uses hversion/sversion/hw_type tables. State and persistence: global root device, device tree nodes, HPA resources, DMA ops pointer, registered bus/drivers, and sysfs attributes persist for boot lifetime. Dependencies and integration points: Linux driver core, PCI, PDC/IODC firmware, hardware descriptions, GSC reads, IO resources, IOMMU sizing, sysfs uevents/modalias, and QEMU machine data generation. Risks: firmware may report devices out of parent order or omit them; hardware paths have PA and PCI quirks; duplicate paths or HPA resource conflicts can hide devices; native probing can find ghost ports. Test signals: boot inventory on real PA-RISC models and QEMU, sysfs modalias/device attributes, driver autoload/probe/remove, PCI path conversion, central-bus scan, IOMMU count sizing, and duplicate/disabled device scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/drivers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/entry.S

Source read size: 2354 lines, 55746 bytes.

Purpose: contains PA-RISC low-level exception vectors, TLB miss fast paths, interrupt/syscall return paths, context switching, ftrace trampolines, IRQ-stack calls, and register access helpers. Important entry points/macros: `fault_vector_20`, `fault_vector_11`, `_switch_to`, `ret_from_kernel_thread`, `syscall_exit_rfi`, `intr_return`, `intr_extint`, `intr_save`, TLB handlers for ITLB/DTLB/non-access/dirty traps on PA1.1/PA2.0/64-bit, syscall wrappers for fork-like calls and `rt_sigreturn`, `syscall_exit`, `_mcount`, `ftrace_caller`, `ftrace_regs_caller`, `parisc_return_to_handler`, `call_on_stack`, `get_register`, and `set_register`. Control flow: architectural vectors either handle TLB misses in shadow registers or branch to common save paths; fast TLB handlers validate space, walk page tables using generated offsets, update accessed/dirty bits, insert TLB entries, and `rfir`; slow faults save full `pt_regs` and call C handlers. Return paths check thread flags for reschedule, signal/notify work, ptrace single/block-step, restore registers/space registers/PSW, and branch or RFI back to userspace. State and persistence: manipulates task saved registers, kernel/user stacks, control registers, space registers, page-table locks, TIF flags, ftrace frames, and TLB state. Dependencies and integration points: depends on `asm-offsets.c` constants, thread flag numbers, PTE encoding, `handle_interruption`, `do_cpu_irq_mask`, scheduler, signal code, ptrace, ftrace, function graph tracing, cache/TLB locking, and PA-RISC calling conventions. Risks: any offset, flag, register-save, pipeline-nop, or space-ID error causes unrecoverable boot, trap, or silent memory corruption; 32/64-bit and PA1.1/PA2.0 paths differ substantially; gateway-page signal deferral is subtle. Test signals: boot smoke, syscall ABI tests, ptrace single/block-step, signal delivery and syscall restart, SMP preemption/IRQ return, TLB miss/page-fault stress, ftrace/function-graph tracing, kernel thread creation, and register get/set fault emulation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/entry.S -->
