# Group Research: group_448_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_sdt_h_sources_os_bsd__e683f04a32cd

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sdt.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sdt.h

Statically Defined Tracing interface for FreeBSD kernel and userspace DTrace probe sites.

Key responsibilities:
- Defines userspace `DTRACE_PROBE` through `DTRACE_PROBE5` wrappers that call generated `__dtrace_*` symbols with unsigned-long arguments.
- In kernels without `KDTRACE_HOOKS`, compiles all SDT and DTrace macros to no-ops while preserving call-site syntax.
- In kernels with tracing, declares provider/probe/linker-set metadata and emits patchable tracepoints using machine-dependent asm.
- Provides `SDT_PROVIDER_DEFINE`, `SDT_PROBE_DEFINE*`, `SDT_PROBE*`, argument type metadata, translated argument metadata, and MIB probe wrappers.
- Defines SDT runtime structures: `sdt_tracepoint`, `sdt_argtype`, `sdt_probe`, and `sdt_provider`.

Important patterns:
- Probe definitions are registered through linker sets: `sdt_providers_set`, `sdt_probes_set`, and `sdt_argtypes_set`.
- `SDT_PROBE*` call sites use `asm goto` patchpoints so disabled probes are cheap and enabled probes can branch into `sdt_probe`/`sdt_probe6`.
- Argument types are string metadata used by DTrace consumers rather than C type enforcement.
- The public `DTRACE_PROBE*` macros are implemented on top of the SDT provider in kernel builds.

Research relevance:
- Central header for FreeBSD's low-overhead tracing ABI.
- Useful for understanding how kernel instrumentation is compiled in without forcing runtime cost when probes are disabled.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sdt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/select.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/select.h

Public `select(2)`/`pselect(2)` ABI header.

Key responsibilities:
- Defines `__fd_mask`, optional BSD-visible `fd_mask`, `FD_SETSIZE`, `_NFDBITS`, and `fd_set`.
- Provides `FD_CLR`, `FD_COPY`, `FD_ISSET`, `FD_SET`, and `FD_ZERO`.
- Declares `pselect()` and `select()` for userspace.
- Pulls in signal-set and time structures needed by `pselect()` and `select()`.

Important patterns:
- `fd_set` is a fixed-size bitset of descriptor bits stored in `unsigned long` words.
- With `_FORTIFY_SOURCE`, `__fdset_idx()` validates the requested descriptor index and object size before indexing.
- `FD_SETSIZE` is user-overridable before inclusion, defaulting to 1024.

Research relevance:
- Defines the classic descriptor readiness bitmap ABI used by filesystem, socket, pipe, and device readiness paths.
- Pairs with kernel `selinfo`/`selrecord` machinery for readiness notification.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/select.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/selinfo.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/selinfo.h

Kernel readiness notification state for `select(2)`, `poll(2)`, and kqueue-style consumers.

Key responsibilities:
- Defines `struct selinfo`, holding sleeping selector threads, a `knlist`, and a mutex pointer.
- Provides `SEL_WAITING(si)` to test whether selector threads are queued.
- Declares kernel routines `selrecord()`, `selwakeup()`, `selwakeuppri()`, `seldrain()`, and `seltdfini()`.

Important patterns:
- `si_tdlist` tracks threads sleeping for readiness on an object.
- `si_note` integrates the same object with kqueue notifications.
- The object embedding `selinfo` supplies or references the lock used to protect selector state.

Research relevance:
- Small but central bridge between file/socket/device readiness and user-visible multiplexing APIs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/selinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sem.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sem.h

System V semaphore ABI and kernel-private wrapper declarations.

Key responsibilities:
- Defines public SysV semaphore structures: `semid_ds`, `sembuf`, and optionally `semun`.
- Preserves older ABI layouts through `semid_ds_old` and `semun_old` under compatibility options.
- Defines `semctl()` command constants such as `GETVAL`, `SETVAL`, `GETALL`, `SEM_STAT`, and `SEM_INFO`.
- Defines semaphore permission aliases `SEM_A` and `SEM_R`.
- Under kernel/internal visibility, defines `seminfo`, `semid_kernel`, and allocation/destroy mode bits.

Important patterns:
- User ABI is kept separate from kernel metadata by wrapping `semid_ds` in `semid_kernel` with MAC label and creator credentials.
- `_WANT_SYSVSEM_INTERNALS` triggers inclusion of broader SysV IPC internals.
- Kernel exposes `semexit()` for undo cleanup at process exit and `kern_get_sema()` for introspection/export.

Research relevance:
- Defines FreeBSD's SysV semaphore contract and the compatibility surface needed by older binaries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sema.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sema.h

Kernel counting semaphore interface.

Key responsibilities:
- Defines `struct sema` as a mutex, condition variable, waiter count, and semaphore value.
- Declares initialization, destruction, post, wait, timed wait, trywait, and value query functions.
- Wraps internal calls with `LOCK_FILE` and `LOCK_LINE` metadata for lock diagnostics.

Important patterns:
- This is a sleepable synchronization primitive implemented with a mutex and condition variable.
- Public macros preserve simple call sites while passing source location to the underlying implementation.
- Exposed only as a kernel synchronization API, not a userspace semaphore ABI.

Research relevance:
- Useful for kernel subsystems that need bounded resource admission or producer/consumer waits without hand-rolling condition-variable state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sema.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/seqc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/seqc.h

Sequence counter helper API for lockless readers with retry validation.

Key responsibilities:
- Imports public `seqc_t` from `_seqc.h` and defines kernel inline helpers.
- Provides writer entry/exit routines: `seqc_write_begin()` and `seqc_write_end()`.
- Provides reader helpers: `seqc_read_any()`, `seqc_read_notmodify()`, `seqc_read()`, `seqc_consistent()`, and no-fence consistency check.
- Provides sleepable writer variants that omit `critical_enter()`/`critical_exit()`.

Important patterns:
- Odd sequence values mark active modification through `SEQC_MOD`.
- Writers enter a critical section, increment to odd, apply a release fence, mutate, release fence again, then increment to even.
- Readers spin while the sequence is in modification and later verify the value did not change.
- The non-sleepable writer API prevents preemption during updates.

Research relevance:
- Key primitive for fast read-mostly kernel state where readers can tolerate retry but not locking.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/seqc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/serial.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/serial.h

Common serial-port signal and interrupt bit definitions.

Key responsibilities:
- Defines modem control signal bits: `SER_DTR`, `SER_RTS`, `SER_CTS`, `SER_DCD`, `SER_RI`, `SER_DSR`, and related secondary TX/RX bits.
- Defines delta-bit encoding through `SER_DELTA()` and delta masks such as `SER_DCTS`.
- Under kernel visibility, defines common serial interrupt source bits for overrun, break, RX-ready, signal-change, and TX-idle.
- Defines `serdev_intr_t` callback type for serial interrupt handlers.

Important patterns:
- Modem signal bits intentionally match shifted `TIOCMGET` definitions, with consistency asserted elsewhere.
- Low 16 bits are reserved for state/delta signals; high bits describe interrupt sources.

Research relevance:
- Device-driver ABI helper for serial hardware and umbrella serial controller drivers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/serial.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sf_buf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sf_buf.h

Sendfile buffer and temporary physical-page mapping interface.

Key responsibilities:
- Defines `struct sfstat` counters for `sendfile(2)` behavior and sf_buf allocation failures/waits.
- Documents architecture-dependent sf_buf modes: `SFBUF`, `SFBUF_CPUSET`, `SFBUF_NOMD`, `SFBUF_MAP`, and `SFBUF_PROCESS_PAGE`.
- Defines `struct sf_buf` for platforms requiring a mapping hash, including page, KVA, reference count, and optional CPU mask.
- Declares or inlines `sf_buf_alloc()`, `sf_buf_free()`, `sf_buf_ref()`, `sf_buf_kva()`, `sf_buf_page()`, `sf_buf_map()`, and `sf_buf_unmap()`.
- Defines allocation flags `SFB_CATCH`, `SFB_CPUPRIVATE`, `SFB_NOWAIT`, and `SFB_DEFAULT`.

Important patterns:
- On platforms with a direct map, an `sf_buf *` can be represented by the `vm_page_t` itself.
- On platforms without universal direct mapping, sf_bufs provide transient kernel virtual mappings for pages.
- Statistics are exposed through a `counter_u64_t` array indexed by `struct sfstat` field offset.

Research relevance:
- Important VM/network/filesystem bridge for zero-copy or low-copy file transmission.
- Shows how FreeBSD abstracts page mapping costs across 32-bit and 64-bit architectures.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sf_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sglist.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sglist.h

Scatter/gather list API for physical address ranges.

Key responsibilities:
- Defines `struct sglist_seg` with physical address and length.
- Defines `struct sglist` with segment array, reference count, current segment count, and capacity.
- Provides inline initialization, reset, and hold/refcount helpers.
- Declares builders and appenders for kernel buffers, physical addresses, bios, mbufs, external-page mbufs, user buffers, uiomove data, and VM pages.
- Declares clone, slice, split, join, consume, count, length, and free helpers.

Important patterns:
- Segment ownership is reference-counted.
- The API can translate many FreeBSD I/O container types into a common physical-range representation.
- Slice/split helpers support passing subranges to DMA or crypto/storage consumers without rebuilding source data.

Research relevance:
- Useful substrate for block I/O, network offload, DMA programming, and zero-copy data paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sglist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/shm.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/shm.h

System V shared memory ABI and kernel-private state.

Key responsibilities:
- Defines shared memory attach flags `SHM_RDONLY`, `SHM_RND`, `SHM_REMAP`, and `SHMLBA`.
- Defines public permission aliases, `shmctl()` commands, and Linux-compatible `SHM_STAT`/`SHM_INFO`.
- Defines `shmid_ds`, compatibility `shmid_ds_old`, `shmatt_t`, and Linux-style `shm_info`.
- Under kernel/internal visibility, defines `shminfo` and `shmid_kernel`.
- Declares userspace `shmat()`, `shmget()`, `shmctl()`, and `shmdt()`.

Important patterns:
- Kernel metadata is stored in `shmid_kernel`, pairing the public descriptor with a VM object, MAC label, and creator credentials.
- Segment state flags distinguish free, removed, and allocated entries.
- Compatibility structures preserve older integer-sized segment and attach-count ABI.

Research relevance:
- Connects SysV IPC semantics with VM objects and per-process VM space lifecycle hooks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/shm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sigio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sigio.h

Async I/O ownership state for `SIGIO` and `SIGURG`.

Key responsibilities:
- Defines `struct sigio`, recording whether notification targets a process or process group.
- Stores linkage into process/process-group sigio lists, a back-reference pointer location, credentials, and target pgid.
- Defines `sigiolst`.
- Declares `fgetown()`, `fsetown()`, `funsetown()`, and `funsetownlst()`.

Important patterns:
- `sio_myref` allows revocation or clearing of the owning file/socket/device reference.
- Credentials are retained with the registration for later signal delivery checks.
- Process and process-group linkage lets the kernel clean up all async notification state when either disappears.

Research relevance:
- Small but important support type for socket/device asynchronous notification.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sigio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/signal.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/signal.h

Public signal ABI header.

Key responsibilities:
- Defines standard and BSD signal numbers, including real-time signal range `SIGRTMIN` to `SIGRTMAX`.
- Defines handler values `SIG_DFL`, `SIG_IGN`, `SIG_ERR`, and `SIG_HOLD`.
- Defines `__sighandler_t`, `sigset_t`, `sigevent`, `siginfo_t`, and 32-bit siginfo compatibility layout.
- Defines `si_code` values for illegal instruction, bus error, segmentation fault, floating point exception, trap, child, and poll events.
- Defines `struct sigaction`, signal action flags, legacy `sigvec` and `sigstack`, `sigmask()`, `sigprocmask()` operations, and `signal()` declaration.
- Defines ancillary BSD extensions such as `SIGEV_KEVENT`, `SIGEV_THREAD_ID`, `SIGIO`, `SIGINFO`, and socket/queue-related signal metadata.

Important patterns:
- Visibility macros gate POSIX, XSI, and BSD interfaces.
- `siginfo_t` packs generic fields plus a union for fault, timer, message queue, poll, and Capsicum-specific reasons.
- Legacy compatibility remains in the ABI surface through old vector and sockaddr-era APIs.

Research relevance:
- Canonical userspace contract for signal delivery, handlers, masks, and async notification results.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/signal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/signalvar.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/signalvar.h

Kernel-private signal state, queues, and delivery interfaces.

Key responsibilities:
- Defines `struct sigacts`, the per-process signal action table and masks for catch, ignore, reset, on-stack, interrupt, no-defer, and siginfo behavior.
- Provides signal-set manipulation macros such as `SIGADDSET`, `SIGDELSET`, `SIGEMPTYSET`, `SIGFILLSET`, `SIGSETOR`, `SIGSETAND`, and compatibility conversions.
- Defines `ksiginfo_t` and `sigqueue_t` for queued signal metadata and pending signal masks.
- Defines fast signal blocking commands and flags.
- Declares kernel signal delivery, queue, action, trap, ptrace, async I/O, and process-exit routines.

Important patterns:
- `sigacts` has mutex and refcount fields last because `sigacts_copy()` relies on copying the preceding state as a block.
- Pending state is split between thread and process signal queues.
- `SIGPENDING()` checks both thread and process pending sets against the thread mask.
- `KSI_*` flags classify trap, external, sigqueue, ptrace, direct insertion, and exception-generated signals.
- `SIGIO_LOCK()` protects async I/O signal ownership structures.

Research relevance:
- Core map of FreeBSD's in-kernel signal lifecycle: action state, pending queues, delivery selection, and cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/signalvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sleepqueue.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sleepqueue.h

Kernel sleep queue interface for blocked threads.

Key responsibilities:
- Documents the sleep queue protocol used by sleep/wakeup, condition variables, pause, sx locks, and lockmgr.
- Defines sleep queue type and behavior flags: `SLEEPQ_SLEEP`, `SLEEPQ_CONDVAR`, `SLEEPQ_PAUSE`, `SLEEPQ_SX`, `SLEEPQ_LK`, `SLEEPQ_INTERRUPTIBLE`, `SLEEPQ_UNFAIR`, and `SLEEPQ_DROP`.
- Declares allocation, free, lock, add, release, remove, abort, signal, broadcast, timeout, timed wait, wait, type, count, and matching-removal routines.
- Provides `sleepq_set_timeout()` wrapper using hardclock ticks.

Important patterns:
- Sleep queues are keyed by wait channel.
- Threads allocate sleep queue objects at thread creation, but queues are not permanently owned by one thread.
- Wakeups require the sleep queue chain lock for non-racy signal/broadcast/remove operations.
- Interruptible and timed wait variants are separate entry points.

Research relevance:
- Fundamental scheduler blocking API beneath many filesystem, VM, socket, and driver wait paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sleepqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/slicer.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/slicer.h

Flash device slicing interface.

Key responsibilities:
- Defines maximum slice count, label length, read-only flag, and slice naming format.
- Defines `struct flash_slice` with base offset, size, label, and flags.
- Under kernel visibility, defines `flash_slicer_t` callback type.
- Defines flash slice provider types for NAND, CFI, SPI, and MMC.
- Declares `flash_register_slicer()` for registering or deregistering slicing callbacks.

Important patterns:
- A slicer callback fills an array of slice descriptors for a provider.
- Passing `NULL` with force is documented as the deregistration path.
- The interface abstracts partition-like fixed flash layouts outside conventional disk partition tables.

Research relevance:
- Small storage-adjacent header relevant to embedded flash-backed filesystem layouts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/slicer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/smp.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/smp.h

Kernel SMP topology, CPU iteration, startup, stop, and rendezvous interface.

Key responsibilities:
- Defines topology node types, hardware IDs, CPU IDs, `struct topo_node`, and scheduler `struct cpu_group`.
- Defines cache-sharing levels and CPU group flags for HTT/SMT/thread and NUMA node behavior.
- Declares topology construction, traversal, analysis, and scheduler topology allocation helpers.
- Exposes global CPU counts, CPU sets, domain sets, and SMP startup state.
- Defines CPU iteration macros/functions over non-absent CPUs.
- Declares machine-dependent MP startup/shutdown functions and CPU stop/restart/suspend/resume hooks.
- Declares rendezvous, quiesce, and cross-CPU fencing helpers.

Important patterns:
- Topology is represented both as a general tree (`topo_node`) and scheduler-oriented grouped masks (`cpu_group`).
- `CPU_ABSENT()` tests `all_cpus`, allowing sparse CPU ID maps.
- `smp_rendezvous*()` supports executing coordinated callbacks across selected CPUs.
- SMP-specific declarations are gated so uniprocessor kernels still expose safe common helpers.

Research relevance:
- Important for understanding CPU topology assumptions behind per-CPU data, SMR, scheduler behavior, and cross-CPU synchronization.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/smp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/smr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/smr.h

Safe Memory Reclamation synchronization API.

Key responsibilities:
- Defines modular sequence comparison helpers for wrapping SMR sequence numbers.
- Defines shared SMR state `struct smr_shared` and per-CPU state `struct smr`.
- Defines flags `SMR_LAZY` and `SMR_DEFERRED`.
- Provides inline readers: `smr_enter()`, `smr_exit()`, `smr_lazy_enter()`, and `smr_lazy_exit()`.
- Declares writer/coordination operations: `smr_advance()`, `smr_poll()`, `smr_wait()`, `smr_synchronize()`, `smr_create()`, `smr_destroy()`, and `smr_init()`.

Important patterns:
- Readers record the current write sequence in per-CPU state while in a critical section.
- Writers advance a sequence and wait or poll until all readers have observed the goal.
- Non-lazy SMR uses stronger ordering, including architecture-specific optimization on x86 via locked atomic add.
- Lazy SMR lowers reader overhead in exchange for higher reclamation latency.
- Recursive SMR read sections are explicitly rejected.

Research relevance:
- Core primitive for lockless read-mostly kernel structures that need delayed freeing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/smr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/smr_types.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/smr_types.h

Typed accessor macros for SMR-protected pointers.

Key responsibilities:
- Defines `SMR_POINTER(type)` wrapper to discourage direct pointer access.
- Provides entered-reader load: `smr_entered_load()`.
- Provides serialized writer/reader access: `smr_serialized_load()`, `smr_serialized_store()`, and `smr_serialized_swap()`.
- Provides unserialized load/store helpers for destructor or externally guaranteed safe contexts.
- Provides `smr_kvm_load()` for libkvm access outside the kernel.

Important patterns:
- Every accessor accepts an assertion expression describing the required synchronization.
- In INVARIANTS kernels, these assertions help catch misuse of SMR-protected pointers.
- Stores use release semantics so initialized contents are visible before readers can follow the pointer.
- Swap includes an explicit release fence for concurrent writer cases.

Research relevance:
- Complements `smr.h` by enforcing safer access patterns at pointer field boundaries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/smr_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sndstat.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sndstat.h

Sound device status ioctl and nvlist schema header.

Key responsibilities:
- Defines `struct sndstioc_nv_arg` for passing packed nvlist buffers through ioctl.
- Defines common nvlist keys for device lists, playback/recording info, provider data, and sound(4)-specific channel/buffer fields.
- Defines maximum user nvlist buffer size `SNDST_UNVLBUF_MAX`.
- Defines ioctls `SNDSTIOC_REFRESH_DEVS`, `SNDSTIOC_GET_DEVS`, `SNDSTIOC_ADD_USER_DEVS`, and `SNDSTIOC_FLUSH_USER_DEVS`.
- Under 32-bit compatibility, defines `sndstioc_nv_arg32` and ioctl type substitutions.

Important patterns:
- The ABI exports structured sound status as packed nvlists rather than fixed C structs.
- Key names are centralized to keep kernel producers and userspace consumers aligned.
- Compatibility handles pointer-size differences in ioctl payloads.

Research relevance:
- Device-status ABI example using nvlists for extensible kernel/userspace reporting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sndstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/snoop.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/snoop.h

Snoop device ioctl constants.

Key responsibilities:
- Defines `SNPSTTY` to attach/set a snooped TTY using a file descriptor.
- Defines `SNPGTTY` to retrieve the associated TTY device.
- Defines special negative `FIONREAD` return values for snoop errors: overflow, TTY close, and detach.

Important patterns:
- Uses tty ioctl command group `'T'`.
- Error states are multiplexed through `FIONREAD` rather than a separate status ioctl.

Research relevance:
- Small legacy character-device ABI for TTY snooping behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/snoop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sockbuf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sockbuf.h

Socket buffer state and kernel manipulation API.

Key responsibilities:
- Defines socket buffer flags for TLS RX, wait/select/async/upcall/AIO/kqueue state, coalescing, autosizing, TOE, splice, and TLS resync behavior.
- Defines socket buffer shutdown/mark state bits.
- Defines `struct sockbuf`, including readiness state, accounting fields, watermarks, timeout, upcall, AIO queue, and protocol-specific buffer unions.
- Supports classic BSD mbuf-chain buffers, PF_UNIX stream/seqpacket buffers, PF_UNIX datagram buffers, and netlink queues.
- Declares append, drop, flush, reserve, release, wait, accounting, send pointer, control-message, TLS RX accounting, and readiness helpers.
- Provides inline `sbavail()`, `sbused()`, and `sbspace()`.

Important patterns:
- Readiness-facing fields are at the start of `struct sockbuf` and protected by the owning socket's send/receive buffer locks.
- Classic buffers track mbuf chains, record boundaries, send pointers, not-ready sendfile data, and KTLS state.
- UNIX-domain sockets use specialized queue structures instead of only the classic mbuf chain.
- `sbspace()` returns the limiting space from byte high-water and mbuf memory limits.

Research relevance:
- Main buffer accounting and queueing contract for FreeBSD sockets, including sendfile and KTLS interactions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sockbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/socket.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/socket.h

Primary public socket ABI header.

Key responsibilities:
- Defines socket types, creation flags, socket options, timestamp modes, and option levels.
- Defines address families, protocol family aliases, routing sysctl constants, and vendor-reserved AF ranges.
- Defines `sockaddr`, `sockproto`, `sockaddr_storage`, `msghdr`, `cmsghdr`, credential control-message structures, and ancillary data macros.
- Defines message flags for send/receive operations, including BSD, POSIX, and kernel-only extensions.
- Defines control-message types such as `SCM_RIGHTS`, timestamps, credentials, and timestamp info.
- Defines shutdown modes, `sendfile(2)` header/trailer structures and flags, `mmsghdr`, and splice option structure.
- Declares userspace socket syscalls and FreeBSD extensions such as `accept4()`, `bindat()`, `connectat()`, `sendfile()`, `sendmmsg()`, and `recvmmsg()`.

Important patterns:
- Visibility macros separate POSIX, BSD, and kernel-only constants.
- Ancillary data layout uses `_ALIGN()` for portable control-message traversal.
- Socket options are split between bit flags stored in `so_options` and numbered get/set options.
- `MSG_NBIO` is explicitly noted as used by fifofs, linking socket flags to filesystem FIFO behavior.

Research relevance:
- Canonical userspace/kernel ABI for socket I/O, ancillary data, sendfile, and local descriptor passing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/socket.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/socketvar.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/socketvar.h

Kernel socket object definition and socket operation API.

Key responsibilities:
- Defines `so_gen_t`, socket accept queue state, splice state, and `struct socket`.
- `struct socket` includes locks, reference count, select state, options, state, PCB, vnet/protocol, errors, SIGIO state, credentials, MAC label, generation count, OSD, FIB/user metadata, timestamp mode, pacing, splice state, I/O locks, and dataflow/listen unions.
- Defines socket state bits, socket/listen/buffer locking macros, and helpers for choosing receive/send buffers.
- Defines socket I/O lock flags, readable/writeable tests, reference-count helpers, wakeup wrappers, and accept-filter registration macro.
- Declares core socket operations: create, bind, connect, listen, accept, receive, send, shutdown, close, reserve, wakeup, AIO, splice dispatch, upcalls, state transitions, and sockopt helpers.
- Defines exported `struct xsocket` and `xsockbuf` for sysctl/libprocstat-style socket inspection.

Important patterns:
- The locking comment is a compact map of which fields are protected by socket lock, buffer locks, listen lock, I/O locks, global lock, or protocol-specific locks.
- Listening sockets reuse the union storage for incomplete/complete accept queues instead of data buffers.
- Send and receive I/O are serialized by separate `sx` locks outside the sockbufs.
- `sorele()` avoids taking the socket lock unless the reference being dropped may be the last one.
- Wakeup macros lock the relevant sockbuf to avoid test-and-wakeup races.

Research relevance:
- Main kernel socket lifecycle and synchronization contract.
- Important for file-descriptor, VFS, FIFO, sendfile, and network interaction research.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/socketvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sockio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sockio.h

Socket and network-interface ioctl command definitions.

Key responsibilities:
- Defines socket ioctls for high/low watermarks, out-of-band mark, and process-group ownership.
- Defines multicast routing counter ioctls.
- Defines many interface ioctls for addresses, flags, broadcast/destination/netmask, metrics, capabilities, index, MAC label, name, description, aliases, multicast membership, MTU, media, generic driver data, status, link-layer address, physical tunnel addresses, private data, vnet movement, FIB, tunnel FIB, clone creation/destruction, interface groups, RSS, VLAN PCP, down reason, capability nvlists, and MBIM/UMB data.
- Preserves comments for obsolete or historical ioctl slots.

Important patterns:
- The command namespace is split primarily by ioctl group letters `'s'`, `'r'`, and `'i'`.
- Some values preserve old ABI numbering while newer replacement commands use later numbers.
- `SIOCSDRVSPEC` and `SIOCGDRVSPEC` intentionally share a command number with different direction bits.

Research relevance:
- Public network configuration ABI used by sockets and interface management tooling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sockio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sockopt.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sockopt.h

Kernel-only socket option request wrapper.

Key responsibilities:
- Rejects non-kernel inclusion.
- Defines `enum sopt_dir` for get versus set operations.
- Defines `struct sockopt`, carrying direction, level, option name, value pointer, value size, Capsicum rights, and calling thread.
- Declares `sosetopt()`, `sogetopt()`, copyin/copyout helpers, mbuf copy helpers, accept-filter get/set handlers, and `so_setsockopt()` convenience wrapper.

Important patterns:
- `sockopt` abstracts both userspace-originated and kernel-originated socket option handling.
- Copy helpers centralize length validation and transfer between user/kernel buffers or mbufs.
- Capsicum rights are carried with the option operation for descriptor-sensitive options.

Research relevance:
- Kernel-internal boundary for implementing `getsockopt(2)` and `setsockopt(2)` safely and consistently.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sockopt.h -->