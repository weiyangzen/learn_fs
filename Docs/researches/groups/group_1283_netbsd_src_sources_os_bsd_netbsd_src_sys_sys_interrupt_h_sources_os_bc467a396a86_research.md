# Group Research: group_1283_netbsd_src_sources_os_bsd_netbsd_src_sys_sys_interrupt_h_sources_os_bc467a396a86

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/interrupt.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/interrupt.h

Defines the machine-independent interrupt-distribution interface built on `sys/intr.h` and kernel CPU sets. It introduces fixed-size interrupt identifiers via `intrid_t`, a variable-length `intrids_handler`, and APIs for interrupt counters, device names, assigned/available CPUs, interrupt ID construction/destruction, and CPU-affinity distribution.

The file is a declaration-only kernel/user ABI surface for interrupt management tools. Key risks are ABI sizing around `INTRIDBUF`, the flexible one-element `iih_intrids` tail, and correctness of callers passing valid `kcpuset_t` masks for interrupt affinity changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/interrupt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/intr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/intr.h

Defines common interrupt constants and the kernel soft interrupt API. It exports `INTRIDBUF`, `INTRDEVNAMEBUF`, soft interrupt establishment/scheduling/disestablishment routines, MI/MD softint hooks, softint level flags, and legacy IPL/spl aliases.

The header bridges machine-independent soft interrupt code with `machine/intr.h`. User-visible exposure is minimal except `_KMEMUSER` access to `SOFTINT_COUNT`. Risks are mostly contract-related: MD ports must implement compatible softint trigger/dispatch behavior, and historical IPL aliases intentionally collapse old priorities onto modern NetBSD IPL levels.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/intr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/intrio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/intrio.h

Defines ioctl data structures for interrupt affinity and interrupt listing. `intrio_set` carries an interrupt ID plus user CPU set buffer metadata. `intrio_list` describes a variable-sized result buffer containing `intrio_list_line` entries, each with interrupt ID, device name, and per-CPU assignment/count data.

It depends on `sys/intr.h` for identifier sizes and `sys/sched.h` for `cpuset_t`. ABI care is required around `INTRIO_LIST_VERSION`, `il_linesize`, `il_lineoffset`, and the one-element flexible CPU array used for `ncpu`-sized records.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/intrio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/inttypes.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/inttypes.h

Small public compatibility header for C99 integer format conversion macros. It includes `sys/stdint.h` and conditionally includes `machine/int_fmtio.h` for non-C++ consumers, C++ consumers opting into `__STDC_FORMAT_MACROS`, or C++11 and later.

It contains no runtime code. Its main role is ABI/source compatibility for fixed-width integer printing/scanning macros, with the important behavior gated by language mode and feature macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/inttypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ioccom.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ioccom.h

Defines the canonical NetBSD ioctl command encoding. The upper bits encode direction and parameter length, while the lower bits encode command group and number. It exports `IOCPARM_LEN`, `IOCBASECMD`, `IOCGROUP`, direction flags, `_IOC`, `_IO`, `_IOR`, `_IOW`, `_IOWR`, and `IOCSNPRINTF`.

This header is foundational for device, filesystem, network, and compatibility ioctl ABIs. Risks are ABI immutability and size limits: command layouts must remain stable, and encoded argument lengths are limited by `IOCPARM_MASK` and `IOCPARM_MAX`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ioccom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ioctl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ioctl.h

Public ioctl aggregation header. It pulls in terminal, disk, file, and socket ioctl definitions; defines old SunOS terminal-size aliases; declares passthrough ioctl commands for multiple emulations through `struct ioctl_pt`; and declares the userland `ioctl(int, unsigned long, ...)` prototype.

Compatibility handling is intentionally outside the include guard so `ioctl_compat.h` can be conditionally included for old tty APIs under `USE_OLD_TTY`, kernel compatibility options, or modular builds. ABI risks center on passthrough command namespace collisions and legacy terminal compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ioctl_compat.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ioctl_compat.h

Defines legacy BSD tty ioctl compatibility structures and constants. It includes `tchars`, `ltchars`, `sgttyb`, old line-discipline ioctls, local-mode ioctls, historical terminal flags such as `CBREAK`, `RAW`, `CRMOD`, delay masks, and local-mode shifted aliases.

This file preserves source and binary compatibility with older terminal driver interfaces and emulation layers. It relies on `sys/ioccom.h`, `sys/ttychars.h`, and `sys/ttydev.h`. Risks are compatibility fragility: values intentionally overlap termios-era constants and must not be casually renumbered.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ioctl_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/iostat.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/iostat.h

Defines disk/tape/NFS I/O statistics structures and kernel maintenance APIs. `io_sysctl` is the 64-bit-alignment-safe exported stats format. `io_stats` is the in-kernel TAILQ-linked state with transfer, byte, seek, busy, wait, and timestamp accounting.

Kernel functions initialize, allocate, rename, find, free, mark wait/busy/unbusy, and record seeks. Filesystem and block device drivers interact with this through device activity accounting. Risks include counter consistency, time accounting around busy/wait transitions, and preserving sysctl structure layout for userland tools.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/iostat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ipc.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ipc.h

Provides System V IPC permission and command definitions. `ipc_perm` stores owner/creator IDs, mode, private sequence, and key. NetBSD exposes `ipc_perm_sysctl` for sysctl reporting. It defines permission bits, creation flags, private key, control commands, IPC ID sequence/index helpers, and `ftok`.

In-kernel declarations include `ipcperm`, SysV IPC init/fini, sysctl fill helpers, and COMPAT_50 sysctl setup. ABI risks involve IPC ID encoding, sequence wrap behavior, and matching permission semantics across message queues, semaphores, and shared memory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ipi.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ipi.h

Kernel-only interprocessor interrupt API. It defines asynchronous handler function type `ipi_func_t`, synchronous message structure `ipi_msg_t`, registration limit constants, bitset sizing macros, initialization hooks, CPU handler hooks, and public async/sync trigger APIs.

It depends on kernel CPU and `kcpuset_t` concepts supplied by surrounding includes. The key contracts are registration lifetime, `_pending` synchronization, broadcast/self behavior, and CPU set correctness. It is not exposed to userland except `_KMEMUSER` inspection.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ipi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ipmi.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ipmi.h

Defines the user/kernel ioctl ABI for IPMI device messaging. It declares IPMI address limits, BMC defaults, address type constants, message/request/receive structures, command registration structures, address variants, and ioctl commands for send, receive, register/unregister, event enablement, address, and LUN access.

The ABI uses embedded user pointers for message data and addresses, so ioctl handlers must validate lengths and copy buffers carefully. Compatibility risk is high for structure layout and command numbers because IPMI tooling expects stable Linux-like semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ipmi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/joystick.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/joystick.h

Small joystick device ioctl header. It defines `struct joystick` with X/Y axis and two button fields, plus ioctls to set/get timeout and X/Y offsets.

The interface is simple and depends on `sys/ioctl.h` command encoding. Main risks are legacy ABI expectations and the comment typo on `JOY_SET_Y_OFFSET`; behavior is determined by the device driver implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/joystick.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kauth.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kauth.h

Defines NetBSD’s kernel authorization framework: scopes, listeners, action IDs, vnode action bitmasks, credential APIs, and authorization wrappers. It covers generic, system, process, network, machdep, device, credential, and vnode policy spaces. Under `__KAUTH_PRIVATE`, it exposes the credential layout used by debugger/kvm consumers.

Filesystem relevance is substantial: vnode actions encode read/write/execute/delete/attribute/extattr/security/flag/link operations, and system requests include mount, quota, LFS, extattr, snapshots, reserved space, and interrupt affinity. Risks are policy bypass from wrong action/subaction pairing, vnode remote-filesystem semantics via `KAUTH_VNODE_REMOTEFS`, credential reference lifetime, and ABI synchronization of private credential layout with kvm consumers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kauth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kcore.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kcore.h

Defines NetBSD kernel crash dump/core file header structures. It provides `KCORE_MAGIC`, `KCORESEG_MAGIC`, physical RAM segment descriptors, a main `kcore_hdr_t`, and per-segment `kcore_seg_t`.

The format is intentionally architecture-shareable by using wide address/size fields. Consumers include crash dump readers and kernel memory inspection tools. Risks are binary format stability, alignment assumptions, and consistent interpretation of `c_midmag` with regular core-file conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kcore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kcov.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kcov.h

Defines the KCOV kernel coverage interface and ioctl ABI. It includes commands for buffer sizing, enable/disable, remote attach/detach, remote VHCI identifiers, coverage modes, and coverage entry type. Kernel prototypes are compiled when `KCOV` is enabled; otherwise macros collapse to `__nothing`.

This header supports fuzzing/instrumentation paths. Risks include exposing coverage only when correctly configured, matching buffer entry size with userland tooling, and avoiding coverage recursion through silence enter/leave.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kcov.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kcpuset.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kcpuset.h

Declares opaque kernel CPU-set operations. It supports allocation, cloning, destruction, copyin/copyout from user `cpuset_t`, bit operations, set comparisons, intersection/merge/remove, first-set queries, atomic variants, and export to 32-bit word arrays.

It is used by affinity-sensitive subsystems including scheduling, interrupt distribution, and IPIs. Key risks are correct lifetime management with `kcpuset_use/unuse`, atomic vs non-atomic operation selection, and validation of user buffer sizes during copyin/copyout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kcpuset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kern_ctf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kern_ctf.h

Defines kernel Compact C Type Format metadata plumbing for modules. `mod_ctf_t` records decompressed CTF data, symbol/string tables, symbol name maps, CTF/type offsets, allocation ownership, FBT provider status, and enabled count. `mod_ctf_get` retrieves CTF metadata for a module.

It integrates module loading, ksyms, DTrace/FBT-style tracing, and type introspection. Risks are lifetime ownership of decompressed tables and keeping symbol/string table counts synchronized with module object state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kern_ctf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kernel.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kernel.h

Declares core kernel globals for `_KERNEL` or standalone builds: host/domain names, RTC offset, boot/shutdown state, clock tick variables, statistics/profiling frequencies, profiling source, and `getticks()`.

This is a low-level coordination header used broadly by kernel subsystems. It has no structures or algorithms, but its globals are timing and boot-state contracts. Risks involve initialization order and consumers assuming valid values before `cold` clears.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kernhist.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kernhist.h

Defines optional kernel history tracing. It provides event/history structures, sysctl export formats, history category bitmasks, and macros that compile away when `KERNHIST` is disabled. When enabled, `KERNHIST_LOG` atomically reserves ring entries, timestamps them, records CPU/function/call/format/four values, and optionally prints immediately.

This is diagnostic infrastructure used by UVM, USB, bio, and other subsystems. Risks are ring overwrite behavior, format string lifetime, performance overhead when enabled, and ABI versioning for sysctl history export.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kernhist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kgdb.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kgdb.h

Defines the KGDB remote serial debugging protocol constants and kernel stub interface. It names GDB remote packet operations, frame markers, acknowledgment bytes, exported KGDB state variables, attach/connect/panic/trap routines, and MD hooks for signal mapping, memory access validation, register transfer, and entry notification.

The header connects DDB, machine register definitions, and serial remote debugging. Risks are machine-dependent register format compatibility and trap recovery safety while the kernel is already faulting or panicking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kgdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kmem.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kmem.h

Declares NetBSD’s kernel memory allocation API. It provides general and interrupt-context allocation/free routines, zeroing variants, formatted string allocation, string duplication/free helpers, temporary-buffer helpers, and sleep/non-sleep allocation flags.

This is a core allocator interface used throughout kernel code. Risks are matching free sizes with original allocations, choosing `KM_SLEEP` only where sleeping is legal, and using interrupt allocation paths in contexts that cannot block.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kobj.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kobj.h

Declares the external kernel object loader interface for ELF modules. It supports loading from VFS or memory, affixing symbols, unloading, querying text address/size, finding sections, symbol lookup, relocation, machine-dependent handling, and namespace rewriting.

It is a key dependency of the module loader. Risks include ELF size selection through `ELFSIZE`, relocation correctness across architectures, object lifetime after unload, and section/symbol table consistency.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kobj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kobj_impl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kobj_impl.h

Private implementation header for kernel object loading. It defines program/relocation entry descriptors, object source type, read/close callbacks, and the full `struct kobj` containing ELF headers, segment addresses/sizes, symbol/string/section tables, relocation tables, load state, and source callbacks.

This is shared only with kernel grovellers and implementation code. Risks are internal layout coupling, architecture-specific ELF assumptions via `ARCH_ELFSIZE`, and correct cleanup of partially loaded VFS or memory-backed objects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kobj_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kprintf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kprintf.h

Defines kernel printf internals. It provides buffer sizing, output destination flags for console/tty/log/buffer/DDB, lock and initialization routines, the core `kprintf` formatter entry point, and log priority control.

Other kernel subsystems can reuse exact kernel formatting semantics. Important contracts are that `kprintf` and `klogpri` require the kprintf mutex where documented, and flags control locking/timestamp/output behavior. Risks are lock recursion and printing from panic/debug contexts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kprintf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ksem.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ksem.h

Defines kernel and libc-facing POSIX semaphore internals. In-kernel `ksem_t` tracks global list entry, pshared owner/id/fd, mutex, condition variable, references, value, waiters, name, flags, mode, uid, and gid. Kernel helper declarations cover init/open/wait paths; libc private syscall wrappers are declared under `_LIBC`.

Risks include pshared marker compatibility, reference/lifetime handling, named semaphore permissions, wait interruption/timeouts, and matching libc/kernel opaque handle semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ksem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ksyms.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ksyms.h

Defines kernel symbol table interfaces and ioctls. Private mode exposes active symbol table descriptors, ELF export header construction, CTF attachment fields, and pslist integration. Public structures support old and current symbol/value lookup ioctls. Kernel APIs provide name/value lookup, module symbol iteration, add/delete symbol tables, initialization, ELF symbol ingestion, availability, and module load/unload notifications.

This integrates debugging, module loading, DDB, and `/dev/ksyms`. Risks include ELF-size compatibility, user ABI differences between old/new symbol ioctls, symbol table lifetime while open, and safe exposure of kernel addresses.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ksyms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kthread.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/kthread.h

Kernel-only kernel-thread API. It defines creation flags for idle creation, MPSAFE behavior, interrupt handlers, time-sharing priority, and must-join lifecycle. It declares system initialization, formatted-name creation, exit, join, and FPU enter/exit routines with MD hooks.

The header depends on `sys/proc.h` and is not user-visible. Risks include join obligations for `KTHREAD_MUSTJOIN`, choosing correct locking/kernel-lock behavior, and FPU state handling in kernel threads.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/kthread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ktrace.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ktrace.h

Defines the ktrace system call ABI and in-kernel trace record machinery. It includes operation flags, versioned `ktr_header`, record structures for syscall, sysret, namei, genio, signals, context switches, emulation, user records, exec args/env/fd, MIB, and signal masks. It defines trace facility bits, persistent/inherit/emulation/version flags, and user prototypes for `ktrace`, `fktrace`, and `utrace`.

Kernel code gets initialization, reference management, trace emitters, guarded inline wrappers, recursion prevention via `LP_KTRACTIVE`, and entry allocation/addition APIs. Filesystem relevance appears through `KTR_NAMEI`, I/O tracing, and exec argument/environment tracing. Risks include record-version compatibility, trace recursion, data-size limits, and locking around `ktrace_lock`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ktrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/localcount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/localcount.h

Kernel-only local reference count API using per-CPU counters plus a total pointer and debug refcount. It declares init, acquire, release, drain, fini, and debug refcount access.

It is used where modules or hooks need to prevent teardown while concurrent users are inside a protected region. Callers provide condition variable and mutex during drain/release coordination. Risks are missed release paths causing unload/drain hangs and incorrect use after finalization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/localcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/localedef.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/localedef.h

Defines internal locale category structures for messages, monetary formatting, numeric formatting, and time formatting. Structures mostly hold string pointers plus POSIX locale formatting fields.

There is no runtime logic. The header supports libc/localedef consumers that need structured locale data. Risks are layout compatibility and pointer lifetime of locale backing strings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/localedef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lock.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/lock.h

Defines common spinlock backoff and kernel lock declarations around machine lock primitives. It imports `machine/lock.h`, supplies default spin hook/backoff hook/min/max values, the `SPINLOCK_BACKOFF` macro, optional LOCKDEBUG spinout behavior, and `kernel_lock[]`.

This is low-level synchronization infrastructure. Risks are architecture hook correctness, backoff behavior under contention, and LOCKDEBUG-only spinout diagnostics changing failure visibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lockdebug.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/lockdebug.h

Defines lock debugging operations and macros. It describes lock operation classes, printer callbacks, abort/dismiss/show functions, and when `LOCKDEBUG` is enabled, allocation/free/want/locked/unlocked/barrier/memory-check functions wrapped with function/line metadata. Without `LOCKDEBUG`, macros compile to no-ops or false.

It is kernel/KMEMUSER-only diagnostic infrastructure. Risks include relying on debug-only checks in production paths, ensuring locks register/free correctly, and avoiding stale lockdebug metadata for freed memory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lockdebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lockf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/lockf.h

Small kernel header for advisory file locking support. It forward-declares `struct lockf` and declares `lf_advlock` and `lf_init`.

Filesystem relevance is direct: vnode operations delegate POSIX/BSD advisory byte-range lock work through this API. Risks are lock state ownership through `struct lockf **`, offset handling, and vnode operation integration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lockf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lua.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/lua.h

Defines kernel Lua device ioctl ABI and kernel Lua state helpers. It provides limits for state/module names, state info/list/create/require/load structures, ioctls for listing, creating, destroying, requiring modules, and loading scripts. Kernel code gets module registration functions, `klua_State` with Lua pointer, mutex, and user-created marker, plus lock/unlock/close/newstate helpers.

Risks include ioctl buffer validation, script path handling, module lifecycle, and serialization around Lua state access.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lua.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lwp.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/lwp.h

Defines the central lightweight process structure and LWP lifecycle/scheduling API. `struct lwp` contains CPU/scheduler state, run queue links, PCB/MD state, timing, priorities, affinity, sleep and synchronization state, futex robust-list pointer, PCU state, process linkage, select/poll state, signal state, private subsystem data, credentials/filedesc caches, tracing/preemption/lockdebug/accounting fields, and optional KMSAN/KCOV data.

It also defines LWP status values, public/private flags, user-return work mask, PCB accessor, kernel APIs for locking, priority, refs, wait/suspend/create/exit/migrate/userret/specificdata/syscalls, `curlwp`/`curproc`, preemption disable/enable, and CPU binding. This is a core scheduler/process ABI for kernel consumers and crash tools. Risks are lock discipline for marked fields, structure layout coupling, reference draining, migration/preemption invariants, and flag semantics reused by tracing, signals, and reboot/core paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lwp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lwpctl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/lwpctl.h

Defines the user-visible per-LWP control block layout and kernel allocation structures. `lwpctl_t` exposes current CPU and performance counter fields with fixed 32/64-bit-compatible size constraints. Feature bits advertise supported fields. Kernel-only `lcpage` and `lcproc` manage mapped pages of control blocks with bitmaps and UVM objects.

Risks are ABI layout stability, page bitmap sizing, and correct cleanup on LWP exit. This supports fast userland access to LWP CPU/counter information.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/lwpctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/malloc.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/malloc.h

Kernel compatibility wrapper for traditional BSD `malloc/free/realloc`. It defines `M_WAITOK`, `M_NOWAIT`, and `M_ZERO`, includes `mallocvar.h`, declares `kern_malloc`, `kern_realloc`, and `kern_free`, and maps the old typed allocator macros to the modern untyped functions.

It preserves old source patterns while allocation types are currently diagnostic stubs. Risks are sleeping allocation in invalid contexts and legacy code assuming type-specific accounting that this header no longer provides.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/malloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mallocvar.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/mallocvar.h

Defines the placeholder malloc type interface. It forward-declares `struct malloc_type`; in kernel builds, `MALLOC_DECLARE` creates an unused static null pointer and define/attach/detach macros are no-ops.

This preserves compile-time compatibility with older typed malloc call sites. Risks are mainly expectations mismatch: consumers cannot rely on per-type allocation statistics or runtime registration from these macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mallocvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mbuf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/mbuf.h

Defines NetBSD’s network mbuf data model and APIs. It covers packet tags, optional mbuf ownership tracing, mbuf headers, packet headers, checksum/offload flags, external storage descriptors, canonical `struct mbuf`, data-size macros, flags/types, allocation macros, cluster/external-storage helpers, read-only/space calculations, prepend/type-change/region helpers, mbuf queues, statistics/sysctl IDs, and kernel mbuf manipulation routines.

Kernel APIs include copy/dup/get/prepend/pulldown/pullup/split/defrag/apply/cat/copyback/makewritable/free/init/tag operations, packet examination/debug helpers, receive-interface access via pserialize or psref, and alignment helpers. Filesystem scope relevance is indirect through network filesystems and kernel buffer-management patterns. Risks are severe if contracts are violated: external storage refcounts, packet-header length consistency, checksum metadata semantics, writable/read-only checks, interface lifetime protection, and ABI-visible mbuf stats/owner structures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/md4.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/md4.h

Declares the MD4 digest context and API. It defines digest/string/block lengths, `MD4_CTX`, and init/update/final functions, with userland convenience helpers for ending, hashing files, and hashing data omitted in kernel builds.

This is a legacy cryptographic hash interface. Risks are security misuse: MD4 is obsolete for collision-resistant purposes and should only be used for compatibility protocols requiring MD4.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/md4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/md5.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/md5.h

Declares the MD5 digest context and API. It defines digest/string/block lengths, `MD5_CTX`, init/update/final routines, and userland convenience functions for string, file, and memory hashing.

Like MD4, this is a compatibility hash interface rather than a modern security primitive. Risks are misuse for integrity/security decisions requiring collision resistance.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/md5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/memfd.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/memfd.h

Defines the kernel `struct memfd` backing `memfd_create`. It stores a name, UVM object pointer, size, seals, and birth/access/modify timestamps.

Filesystem relevance is direct: memfd represents anonymous file-like memory objects with seal state and metadata. Risks include seal enforcement, UVM object lifetime, size synchronization, and timestamp updates across file operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/memfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/midiio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/midiio.h

Defines MIDI and sequencer ioctl/event ABI compatible with OSS at the byte level. It includes MPU command records, `/dev/midi` ioctls, sequencer/timer ioctls, synth info structures, MIDI controller/status constants, RPN and pitch constants, old sequencer command values, native 8-byte `seq_event_t` union layouts, event-construction macros, sysex/instrument patch structures, and userland/kernel pitch-to-frequency conversion helpers.

The header is mostly ABI and macro logic. Risks are binary compatibility with OSS event byte layouts, endian-dependent patch/time-signature fields, packed union layout, and documented quirks around controller changes and partially unimplemented sequencer events.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/midiio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mman.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/mman.h

Public memory-mapping API header. It defines protection bits, PaX `PROT_MPROTECT` helpers, mapping sharing/options/type/alignment flags, `MAP_FMT`, `MAP_FAILED`, msync/mlockall flags, POSIX and NetBSD madvise values, minherit modes, memfd flags, and userland prototypes for mmap/munmap/mprotect/msync/mlock/munlock/mlockall/munlockall/madvise/mincore/minherit/mremap/memfd_create/posix_madvise/shm_open/shm_unlink.

Filesystem relevance is high through file-backed mappings, shared memory, memfd, and UVM integration. Risks include flag ABI stability, alignment encoding, PaX protection semantics, and feature-test conditional exposure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mman.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/module.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/module.h

Defines NetBSD kernel module metadata, registration, runtime state, and `modctl` ABI. It declares module classes, sources, command types, `modinfo_t`, kernel `module_t` state, link-set or rump constructor registration machinery, the `MODULE` macro, module lists/globals, load/unload/autoload/builtin/specificdata/callback APIs, VFS loading hooks, module base/machine strings, and userland `modctl` load/stat structures.

It integrates with `kobj`, VFS loading, properties, sysctl cleanup, dependencies, and compatibility stubs. Risks are module dependency/refcount correctness, forced unload policy, built-in vs loadable registration differences, user pointer validation in `modctl_load_t`, and ABI stability of `modstat_t`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/module.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/module_hook.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/module_hook.h

Defines MP-safe module hook plumbing for vectored function calls whose implementation may live in unloadable modules. It uses a cacheline-aligned hook structure containing `localcount`, function pointer, and hooked flag, plus set/unset/call macros around `module_hook_tryenter` and `module_hook_exit`.

The design uses pserialize barriers during hook set/unset and localcount draining to prevent unload while calls are active. Risks are missing `MODULE_HOOK_UNSET` before unload, default-return correctness, function pointer lifetime, and always pairing successful tryenter with exit.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/module_hook.h -->