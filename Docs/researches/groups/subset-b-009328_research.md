# subset-b-009328 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/iopl.c -->
# sources/test-tools/strace/src/iopl.c

Purpose: minimal decoder for the `iopl` syscall, printing the requested I/O privilege `level`.

Important APIs/types/functions: `SYS_FUNC(iopl)`, `tprints_arg_name`, `PRINT_VAL_D`, and `RVAL_DECODED`.

Control flow: the decoder names argument 0 as `level`, prints it as a signed integer after casting from `tcp->u_arg[0]`, and reports that the syscall is fully decoded.

State and persistence behavior: no persistent state and no tracee memory access; it only formats one register argument.

Dependencies and integration points: depends on `defs.h` syscall-decoder macros and is selected by the strace syscall table for architectures exposing `iopl`.

Risks: the only meaningful risk is argument signedness/width drift if a future ABI changes the representation; there is no entry/exit split to validate return-time state.

Test signals: tests should assert `iopl(level)` prints a named signed `level` argument and does not emit raw undecoded arguments.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/iopl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ioprio.c -->
# sources/test-tools/strace/src/ioprio.c

Purpose: decodes Linux I/O priority syscalls and provides a reusable `print_ioprio` formatter for priority values.

Important APIs/types/functions: `sprint_ioprio`, `print_ioprio`, `ioprio_print_who`, `SYS_FUNC(ioprio_get)`, `SYS_FUNC(ioprio_set)`, `IOPRIO_CLASS_SHIFT`, `IOPRIO_PRIO_CLASS`, `IOPRIO_PRIO_DATA`, and xlat tables `ioprio_who`/`ioprio_class`.

Control flow: `sprint_ioprio` splits a priority word into class and data, formats `IOPRIO_PRIO_VALUE(...)`, and respects xlat lookup fallback. `ioprio_get` prints `which` and PID-like `who` on entry, then on successful exit attaches a decoded return string unless raw xlat mode is active. `ioprio_set` prints `which`, dispatches `who` through process or process-group PID printers, and formats the `ioprio` argument according to xlat verbosity.

State and persistence behavior: no persistent state beyond `tcp->auxstr` for `ioprio_get` return annotation. `sprint_ioprio` uses a static buffer, so callers must consume the string immediately.

Dependencies and integration points: depends on `defs.h`, `xstring.h`, PID namespace-aware `printpid`, xlat verbosity, and the generated priority xlat tables. `print_ioprio` can be reused by other decoders that expose kernel I/O-priority words.

Risks: static formatter storage is not reentrant; xlat verbosity changes output shape substantially; unknown `which` values are intentionally printed numerically and should not be treated as PIDs.

Test signals: cover raw/abbrev/verbose xlat modes, `IOPRIO_WHO_PROCESS`, `IOPRIO_WHO_PGRP`, unknown `which`, successful `ioprio_get` return decoding, and syscall-error exit behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ioprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/iovec.h -->
# sources/test-tools/strace/src/iovec.h

Purpose: defines strace's ABI-sized iovec representation for tracee memory decoding.

Important APIs/types/functions: `strace_iovec`, `kernel_ulong_t`, and the include guard `STRACE_IOVEC_H`.

Control flow: header-only typedef; including code receives a two-field structure with `iov_base` and `iov_len` sized as kernel unsigned longs for the current personality.

State and persistence behavior: no state. The type is used as a stable in-memory layout description for fetched tracee iovec arrays.

Dependencies and integration points: includes `kernel_types.h`; used by decoders such as vector I/O/keyctl helpers that need tracee ABI pointer and length fields rather than host `struct iovec`.

Risks: incorrect `kernel_ulong_t` sizing would corrupt vector decoding across compat personalities. The type intentionally does not include libc's pointer type because host ABI may differ from tracee ABI.

Test signals: iov-based syscall tests should exercise native and compat personalities and confirm base/length pairs are not truncated or widened incorrectly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/iovec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ipc.c -->
# sources/test-tools/strace/src/ipc.c

Purpose: generic decoder for the multiplexed legacy `ipc` syscall.

Important APIs/types/functions: `SYS_FUNC(ipc)`, `ipc_arg_name`, `n_args`, `printxval_u`, `ipccalls`, and flag/shift printing helpers.

Control flow: argument 0 is split into a high 16-bit version and low 16-bit IPC call number. The decoder prints the version as a shifted flag component when nonzero, prints the call xlat, then prints all remaining syscall arguments as hex under generic names `first`, `second`, `third`, `ptr`, and `fifth`.

State and persistence behavior: no persistent state and no tracee memory reads; this decoder does not dispatch to specific SysV IPC decoders.

Dependencies and integration points: depends on `defs.h` and generated `xlat/ipccalls.h`; complements the dedicated `msg*`, `sem*`, and `shm*` decoders used for direct syscalls or architecture-specific paths.

Risks: because this is a generic multiplexor printer, it does not decode pointed-to IPC structures. The argument-name array assumes the maximum argument count after `call` fits five entries.

Test signals: multiplexed IPC tests should verify versioned call rendering, xlat fallback for unknown calls, and hex formatting of each remaining argument.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ipc_defs.h -->
# sources/test-tools/strace/src/ipc_defs.h

Purpose: central compatibility header for SysV IPC decoders, selecting kernel or libc IPC headers and normalizing structure names.

Important APIs/types/functions: `MSG_H_PROVIDER`, `SEM_H_PROVIDER`, `SHM_H_PROVIDER`, `NAME_OF_STRUCT_MSQID_DS`, `NAME_OF_STRUCT_SEMID_DS`, `NAME_OF_STRUCT_SHMID_DS`, `NAME_OF_STRUCT_SHMINFO`, `NAME_OF_STRUCT_IPC_PERM_KEY`, `IPC_64`, and `PRINTCTL`.

Control flow: preprocessor checks reject `<linux/ipc.h>` when configured structure sizes do not match the active mpers ABI. It then includes either Linux or libc IPC headers, maps provider header names and structure identifiers, defines missing `IPC_64`, and exposes `PRINTCTL` for `IPC_64`-aware command formatting.

State and persistence behavior: no runtime state; all behavior is compile-time configuration and macro expansion.

Dependencies and integration points: used by message, semaphore, and shared-memory decoders. It bridges configure-time size probes, mpers personalities, and generated xlat command tables.

Risks: structure-size probes must stay aligned with kernel/libc headers; choosing the wrong provider would make `umove` decode incompatible layouts. `PRINTCTL` masks only `IPC_64`, so old compat IPC calls remain partly decoded elsewhere.

Test signals: build/test matrix should cover native, m32, mx32, and systems with/without Linux IPC headers; SysV `IPC_SET`, `IPC_STAT`, and info commands should print correct structure field names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ipc_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ipc_msg.c -->
# sources/test-tools/strace/src/ipc_msg.c

Purpose: decodes SysV message queue creation, send, and receive syscalls.

Important APIs/types/functions: `SYS_FUNC(msgget)`, `SYS_FUNC(msgsnd)`, `SYS_FUNC(msgrcv)`, `tprint_msgsnd`, `tprint_msgrcv`, `fetch_msgrcv_args`, `tprint_msgbuf`, `indirect_ipccall`, and xlats `ipc_msg_flags`, `ipc_private`, `resource_flags`.

Control flow: `msgget` prints key and resource/permission flags. `msgsnd` prints `msqid`, then chooses argument positions based on `indirect_ipccall`. `msgrcv` prints `msqid` on entry and, on exit, decodes direct arguments or the legacy indirect `ipc_kludge` pair before printing `msgflg`.

State and persistence behavior: no durable state. For receive, decoding intentionally happens on exit so returned message content is available; SPARC64/directness uses `get_tcb_priv_ulong` to disambiguate legacy indirect forms.

Dependencies and integration points: relies on `ipc_defs.h` provider selection, message-header layouts, shared message-buffer printer, tracee memory fetch helpers, and SysV IPC syscall table entries.

Risks: indirect IPC argument order is architecture-sensitive. `fetch_msgrcv_args` must respect current tracee word size or signed `msgtyp` may be decoded incorrectly. Tracee memory failures fall back to addresses.

Test signals: cover direct and indirect `msgsnd`/`msgrcv`, IPC_PRIVATE keys, mode-bit combinations, receive success vs error, inaccessible `ipc_kludge`, and 32-bit word-size receive arguments.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ipc_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ipc_msgctl.c -->
# sources/test-tools/strace/src/ipc_msgctl.c

Purpose: mpers-aware decoder for `msgctl` message queue control operations.

Important APIs/types/functions: `SYS_FUNC(msgctl)`, `print_ipc_perm`, `print_msqid_ds`, `print_msginfo`, `msqid_ds_t`, `DEF_MPERS_TYPE`, `MPERS_DEFS`, `PRINTCTL`, and `msgctl_flags`.

Control flow: the decoder locates `buf` according to direct or indirect IPC calling convention and strips `IPC_64` for command dispatch. On entry it prints `msqid` and `op`; `IPC_SET` decodes `msqid_ds` immediately, status/info commands defer to exit, and unknown commands print the raw buffer address. On exit it decodes queue status structures or `msginfo`.

State and persistence behavior: no persisted private state; the buffer address is recomputed from syscall arguments on both phases. Tracee memory is read only for structure output.

Dependencies and integration points: depends on `ipc_defs.h` layout selection, mpers-generated structure definitions, field-printing helpers, and SysV message queue xlat tables.

Risks: old compat IPC calls are explicitly not fully decoded. `IPC_SET` prints a reduced permission subset while status commands include key/creator fields; tests must not expect identical field sets.

Test signals: exercise `IPC_SET`, `IPC_STAT`, `MSG_STAT`, `MSG_STAT_ANY`, `IPC_INFO`, `MSG_INFO`, unknown commands, inaccessible buffers, and native/compat layouts.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ipc_msgctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ipc_sem.c -->
# sources/test-tools/strace/src/ipc_sem.c

Purpose: decodes SysV semaphore operation and creation syscalls.

Important APIs/types/functions: `SYS_FUNC(semop)`, `SYS_FUNC(semtimedop_time32)`, `SYS_FUNC(semtimedop_time64)`, `SYS_FUNC(semget)`, `print_sembuf`, `tprint_sembuf_array`, `do_semtimedop`, and xlats `semop_flags`, `ipc_private`, `resource_flags`.

Control flow: semaphore operations print `semid`, then decode a `struct sembuf` array from either direct arguments or legacy indirect IPC slots. Timed operations share `do_semtimedop`, selecting `print_timespec32` or `print_timespec64` and using an S390/S390X-specific timeout slot for indirect calls. `semget` prints key, count, and resource/mode flags.

State and persistence behavior: no persistent state. Tracee memory reads are bounded by `nsops` and handled through `print_array`.

Dependencies and integration points: uses provider headers selected by `ipc_defs.h`, generic time printers, SysV IPC flags, and indirect IPC detection.

Risks: argument positions differ between direct, indirect, and S390 legacy paths. Large `nsops` values can produce abbreviated arrays depending on strace settings and memory availability.

Test signals: cover direct and indirect `semop`, timed 32/64 variants, S390-specific argument mapping where applicable, `SEM_UNDO`/`IPC_NOWAIT`, IPC_PRIVATE, and permission mode rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ipc_sem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ipc_semctl.c -->
# sources/test-tools/strace/src/ipc_semctl.c

Purpose: mpers-aware decoder for `semctl` control operations and semaphore information structures.

Important APIs/types/functions: `SYS_FUNC(semctl)`, `print_ipc_perm`, `print_semid_ds`, `print_seminfo`, `semun_ptr_t`, `semid_ds_t`, `DEF_MPERS_TYPE`, `PRINTCTL`, `set_tcb_priv_ulong`, and `get_tcb_priv_ulong`.

Control flow: on entry the decoder prints `semid`, `semnum`, command, and resolves `arg`, including the indirect `union semun` pointer form for legacy IPC and SPARC64 personality handling. `IPC_SET` decodes immediately; stat/info commands save the resolved address and decode on exit; unknown commands print the address with indirect markers when needed.

State and persistence behavior: per-syscall private `tcb` storage preserves the resolved buffer address across entry/exit. No durable global state.

Dependencies and integration points: uses mpers type generation, IPC provider macros, semaphore xlat flags, and tracee memory fetch helpers. Integrated with the SysV semaphore syscall decoder table.

Risks: old compat IPC calls are not fully decoded. Indirect pointer handling is subtle and architecture dependent; failing to save the resolved address would break exit-only decoding.

Test signals: cover `IPC_SET`, `IPC_STAT`, `SEM_STAT`, `SEM_STAT_ANY`, `IPC_INFO`, `SEM_INFO`, indirect semun pointers, inaccessible pointers, and native/compat structure sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ipc_semctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ipc_shm.c -->
# sources/test-tools/strace/src/ipc_shm.c

Purpose: decodes SysV shared-memory creation, attach, and detach syscalls.

Important APIs/types/functions: `SYS_FUNC(shmget)`, `SYS_FUNC(shmat)`, `SYS_FUNC(shmdt)`, `print_shmaddr_shmflg`, `SHM_HUGE_SHIFT`, `SHM_HUGE_MASK`, and xlats `shm_resource_flags`/`shm_flags`.

Control flow: `shmget` prints key, size, and flags, specially splitting hugetlb page-size bits from resource flags before printing permission mode bits. `shmat` prints input arguments on entry and on successful exit returns the attached address as hex, reading the indirect return address slot for legacy IPC. `shmdt` prints the address from direct or indirect argument positions.

State and persistence behavior: no persistent state. `shmat` mutates `tcp->u_rval` on indirect successful exits to reflect the real attached address read from tracee memory.

Dependencies and integration points: uses IPC provider selection, shared-memory flag xlat tables, indirect IPC detection, and return-value formatting flags.

Risks: hugepage flag decoding must keep masks in sync with kernel constants. Indirect `shmat` can fail to read the returned address and then suppresses normal return formatting.

Test signals: cover normal and hugetlb `shmget` flags, direct/indirect `shmat`, failed attach, unreadable indirect return slot, `SHM_RDONLY`/`SHM_REMAP`, and `shmdt` argument mapping.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ipc_shm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ipc_shmctl.c -->
# sources/test-tools/strace/src/ipc_shmctl.c

Purpose: mpers-aware decoder for `shmctl` shared-memory control commands.

Important APIs/types/functions: `SYS_FUNC(shmctl)`, `print_ipc_perm`, `print_shmid_ds`, `print_ipc_info`, `print_shm_info`, `shmid_ds_t`, `struct_shm_info_t`, `struct_shm_ipc_info_t`, `DEF_MPERS_TYPE`, and `shmctl_flags`.

Control flow: the decoder picks the buffer argument for direct or indirect IPC, strips `IPC_64` for dispatch, and prints `shmid` plus command on entry. `IPC_SET` decodes `shmid_ds` immediately; status and info commands defer to exit; unknown commands print the buffer address. Exit decodes `shmid_ds`, IPC limits, or runtime shared-memory info depending on command.

State and persistence behavior: no explicit private state; the buffer address is derived from syscall arguments on both phases. Reads only tracee memory structures.

Dependencies and integration points: relies on `ipc_defs.h`, mpers structure sizing, PID-aware field printers for creator/last PID fields, and shared-memory xlat tables.

Risks: old compat IPC is not fully decoded. `IPC_SET` intentionally omits read-only status fields. Kernel/libc structure differences are handled only if configure/mpers probes are correct.

Test signals: cover `IPC_SET`, `IPC_STAT`, `SHM_STAT`, `SHM_STAT_ANY`, `IPC_INFO`, `SHM_INFO`, inaccessible buffers, PID field formatting, and compat layout variants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ipc_shmctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kcmp.c -->
# sources/test-tools/strace/src/kcmp.c

Purpose: decodes `kcmp` process-resource comparison calls.

Important APIs/types/functions: `SYS_FUNC(kcmp)`, `PRINT_FIELD_PIDFD`, `printfd_pid_tracee_ns`, `printpid`, `struct kcmp_epoll_slot`, and `kcmp_types`.

Control flow: prints `pid1`, `pid2`, and comparison `type`. For `KCMP_FILE`, `idx1` and `idx2` are rendered as file descriptors in the respective process namespaces. For `KCMP_EPOLL_TFD`, `idx1` is a fd and `idx2` points to a `kcmp_epoll_slot` whose fds and offset are decoded. Other known resource types omit index printing; unknown types print raw hex indices.

State and persistence behavior: no persistent state. Only `KCMP_EPOLL_TFD` reads tracee memory.

Dependencies and integration points: depends on `<linux/kcmp.h>`, PID/fd namespace-aware printers, and generated `kcmp_types` xlat entries.

Risks: fd rendering must use the PID associated with each index; using the tracer namespace would be misleading. Unknown future `KCMP_*` types fall back to raw indices.

Test signals: cover known resource types, file comparison with two process namespaces, epoll slot decoding and inaccessible slot pointer, and unknown type fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kd_ioctl.c -->
# sources/test-tools/strace/src/kd_ioctl.c

Purpose: decodes non-mpers Linux keyboard, console, and VT ioctl commands.

Important APIs/types/functions: `kd_ioctl`, helpers `kiocsound`, `kd_mk_tone`, `kd_leds`, `kd_get_kb_type`, `kd_io`, `kd_set_mode`, `kd_get_mode`, `kd_screen_map`, `kd_uni_screen_map`, `kd_kbd_entry`, `kd_kbd_str_entry`, `kd_diacr`, `kd_diacr_uc`, `kd_keycode`, `kd_kbdrep`, `kd_font`, `kd_kbmeta`, `kd_unimapclr`, `kd_cmap`, and many `kd_*` xlat tables.

Control flow: `kd_ioctl` truncates the argument to current tracee word size and dispatches by ioctl code. Simple setters print immediate values; getters generally return 0 on entry and decode pointed-to data on exit. Complex commands decode keyboard maps, strings, diacritic arrays, keycodes, repeat settings, font/cmap buffers, and signal values, using entry/exit comparisons where the kernel may update structures.

State and persistence behavior: per-call private state stores original keycode for `KDGETKEYCODE` so exit can report changed values. Other handlers are stateless apart from normal entry/exit phase behavior and tracee memory reads.

Dependencies and integration points: integrates with the tty ioctl dispatcher and falls through to `kd_mpers_ioctl` for personality-dependent font/unimap structures. It depends on Linux KD/keyboard headers, generated xlat tables, `print_fields.h`, and tracee memory/string printers.

Risks: ioctl direction semantics are easy to invert; many commands only decode useful data on exit. Array lengths are kernel constants and must remain bounded. Keyboard value comments depend on xlat verbosity and key type classification.

Test signals: cover sound/tone comments, LED get/set/default LEDs, mode get/set, screen maps, Unicode screen maps, keyboard entries and strings, diacritic truncation above 256 entries, keycode value-change printing, font/cmap error paths, and fallback to mpers handlers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kd_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kd_mpers_ioctl.c -->
# sources/test-tools/strace/src/kd_mpers_ioctl.c

Purpose: decodes personality-dependent VT ioctl commands whose structures contain tracee-sized pointers.

Important APIs/types/functions: `MPERS_PRINTER_DECL(kd_mpers_ioctl)`, `kd_unimap`, `kd_fontx`, `kd_font_op`, `print_unipair_array_member`, `print_consolefontdesc`, `print_console_font_op`, mpers types `struct_unimapdesc`, `struct_consolefontdesc`, `struct_console_font`, and `struct_console_font_op`.

Control flow: the mpers dispatcher handles `GIO_UNIMAP`/`PIO_UNIMAP`, `GIO_FONTX`/`PIO_FONTX`, and `KDFONTOP`. `kd_unimap` prints entry count and decodes entries on set or successful get, preserving original count across phases. `kd_fontx` decodes console font descriptor and either pointer or glyph bytes. `kd_font_op` decodes operation-specific fields and chooses whether to continue to exit based on operation direction.

State and persistence behavior: `kd_unimap` stores `entry_ct` in `tcb` private storage; exit can report changed count and use the original count for returned arrays. No durable global state.

Dependencies and integration points: called by `kd_ioctl.c` fallback. Depends on mpers-generated layouts, KD font operation xlat tables, and tracee string/array printers.

Risks: pointer-sized fields must match tracee personality; using host structures would misdecode compat processes. `KDFONTOP` has operation-specific data semantics, including bounded font-name and glyph buffers.

Test signals: cover get/set unimap, ENOMEM behavior, changed entry counts, `GIO_FONTX` vs `PIO_FONTX`, `KD_FONT_OP_GET`, `SET`, `SET_DEFAULT`, `COPY`, unknown font ops, and compat pointer widths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kd_mpers_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kernel_dirent.h -->
# sources/test-tools/strace/src/kernel_dirent.h

Purpose: defines kernel `getdents` and `getdents64` directory-entry layouts for tracee buffer decoding.

Important APIs/types/functions: `kernel_dirent_t`, `kernel_dirent64_t`, `kernel_ulong_t`, `uint64_t`, `d_ino`, `d_off`, `d_reclen`, `d_type`, and flexible trailing `d_name[1]`.

Control flow: header-only type definitions; consumers iterate variable-length records using `d_reclen` and decode names from the trailing byte array.

State and persistence behavior: no state. Types model tracee buffer records rather than persisted data.

Dependencies and integration points: includes `kernel_types.h`; used by directory-entry syscall decoders where libc `struct dirent` cannot be trusted to match kernel ABI.

Risks: `kernel_dirent_t` uses tracee-sized long fields while `kernel_dirent64_t` fixes inode/offset to 64 bits. Incorrect record sizing can desynchronize directory-buffer iteration.

Test signals: `getdents`/`getdents64` tests should cover multiple records, unknown `d_type`, compat word sizes, and malformed/truncated record lengths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kernel_dirent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kernel_fcntl.h -->
# sources/test-tools/strace/src/kernel_fcntl.h

Purpose: sanitizes userspace fcntl macro/type namespace before including kernel `<asm/fcntl.h>`.

Important APIs/types/functions: temporary renames `f_owner_ex`, `flock`, `flock64`, many `O_*`/`F_*`/`LOCK_*` undefines, inclusion of `<asm/fcntl.h>`, and final `#undef O_NDELAY`.

Control flow: if `_ASM_GENERIC_FCNTL_H` is not already included, the header undefines potentially conflicting libc/generic constants, renames structure tags to kernel-prefixed forms, includes the architecture kernel fcntl header, then removes temporary tag aliases. It always undefines `O_NDELAY` afterward so strace can correct architecture-specific definitions elsewhere.

State and persistence behavior: no runtime state; it mutates preprocessor namespace for later decoder includes.

Dependencies and integration points: used by fcntl/open flag decoders needing kernel ABI constants instead of libc values. It depends on configure/build include ordering and architecture headers.

Risks: the list of undefines must track kernel `asm-generic/fcntl.h`; missing a macro can cause redefinition warnings or wrong constants. The `O_NDELAY` correction is architecture-sensitive, especially sparc32.

Test signals: build across multiple architectures, validate open/fcntl flag numeric values, and specifically check `O_NDELAY` rendering on sparc-like and generic platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kernel_fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kernel_rusage.h -->
# sources/test-tools/strace/src/kernel_rusage.h

Purpose: defines strace's kernel ABI layout for `struct rusage`.

Important APIs/types/functions: `kernel_rusage_t`, `kernel_old_timeval_t`, and `kernel_long_t` fields for CPU times, RSS, faults, swaps, block I/O, messages, signals, and context switches.

Control flow: header-only typedef consumed by resource-usage decoders.

State and persistence behavior: no state; it describes fetched tracee memory layout.

Dependencies and integration points: includes `kernel_timeval.h`; used by `getrusage`, wait-family, and similar decoders that need kernel-sized long fields.

Risks: all non-time fields depend on `kernel_long_t`, so compat personality sizing is critical. Time fields use `kernel_old_timeval_t`, including sparc64-specific microsecond layout.

Test signals: cover native and compat `getrusage` output, sparc64 layout if available, negative/large counters, and syscall failures with inaccessible result buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kernel_rusage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kernel_time_types.h -->
# sources/test-tools/strace/src/kernel_time_types.h

Purpose: provides fallback kernel time type definitions when system headers lack modern Linux time structs.

Important APIs/types/functions: `struct __kernel_sock_timeval`, `__kernel_timespec`, `kernel_timespec64_t`, and feature macros `HAVE_STRUCT___KERNEL_SOCK_TIMEVAL`/`HAVE_STRUCT___KERNEL_TIMESPEC`.

Control flow: includes `kernel_timespec.h`, then includes `<linux/time_types.h>` when it provides needed structs; otherwise includes `<stdint.h>`. Missing `__kernel_sock_timeval` is defined with 64-bit seconds/useconds, and missing `__kernel_timespec` is aliased to `kernel_timespec64_t`.

State and persistence behavior: no runtime state; compile-time compatibility only.

Dependencies and integration points: used by decoders and generated ioctl definitions needing modern kernel socket/time layouts independent of host header vintage.

Risks: fallback definitions must match Linux UAPI exactly. Incorrect feature detection could conflict with system headers or mis-size timeout structures.

Test signals: build on old and new kernel headers, compile users of socket timeval and timespec ioctls, and verify decoded 64-bit time fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kernel_time_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kernel_timespec.h -->
# sources/test-tools/strace/src/kernel_timespec.h

Purpose: defines 64-bit and conditional 32-bit kernel timespec layouts.

Important APIs/types/functions: `kernel_timespec64_t`, `kernel_timespec32_t`, `HAVE_ARCH_TIME32_SYSCALLS`, `HAVE_ARCH_TIMESPEC32`, and `arch_defs.h`.

Control flow: always defines `kernel_timespec64_t` with `long long` seconds/nanoseconds. Defines `kernel_timespec32_t` only when the target architecture has time32 syscalls or timespec32 structures.

State and persistence behavior: no state; types are used for tracee-memory decoding.

Dependencies and integration points: included by time, timeout, futex, socket, and ioctl decoders that must distinguish y2038-safe and legacy layouts.

Risks: conditional availability must match syscall tables; decoding a 32-bit time syscall with the 64-bit type would misread both fields.

Test signals: cover time32 and time64 syscall variants, architectures without time32 support, negative seconds, and nanosecond boundary values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kernel_timespec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kernel_timeval.h -->
# sources/test-tools/strace/src/kernel_timeval.h

Purpose: defines kernel timeval layouts used by old and 64-bit time APIs.

Important APIs/types/functions: `kernel_timeval64_t`, `kernel_old_timeval_t`, `kernel_long_t`, and sparc64-specific `tv_usec` sizing.

Control flow: header-only definitions; 64-bit timeval uses two `long long` fields, while old timeval uses `kernel_long_t` seconds and either `kernel_long_t` or sparc64 `int` microseconds.

State and persistence behavior: no state.

Dependencies and integration points: includes `kernel_types.h`; consumed by rusage, timex, v4l2, select/time, and other decoders needing kernel timeval ABI layouts.

Risks: sparc64 old timeval is a special case and can be misdecoded if treated as two kernel longs. Host libc `struct timeval` is not interchangeable with these types.

Test signals: timeval-decoding tests should cover native/compat personalities, sparc64 layout where available, and both old and 64-bit timeval users.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kernel_timeval.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kernel_timex.h -->
# sources/test-tools/strace/src/kernel_timex.h

Purpose: defines kernel `timex` layouts for time adjustment syscalls across 64-bit, sparc64, and time32 ABIs.

Important APIs/types/functions: `kernel_timex64_t`, `kernel_sparc64_timex_t`, `kernel_timex32_t`, embedded `kernel_timeval64_t`, and `HAVE_ARCH_TIME32_SYSCALLS`.

Control flow: always defines the y2038-safe 64-bit layout, conditionally defines sparc64's special layout with `int tv_usec`, and conditionally defines the legacy time32 layout using 32-bit scalar fields.

State and persistence behavior: no state; structure definitions only.

Dependencies and integration points: includes `kernel_timeval.h`; used by `adjtimex`/`clock_adjtime` decoders and any tests validating `struct timex` tracee layouts.

Risks: padding fields and architecture-specific timeval layout preserve ABI size; removing or reordering them would break mpers-independent decoding.

Test signals: cover time64 and time32 `timex` decoding, nonzero padding arrays, TAI/status fields, and sparc64-specific structure if available.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kernel_timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kernel_types.h -->
# sources/test-tools/strace/src/kernel_types.h

Purpose: normalizes kernel long and 64-bit printf formatting types across architectures and personalities.

Important APIs/types/functions: `kernel_long_t`, `kernel_ulong_t`, fallback `__kernel_long_t`/`__kernel_ulong_t`, `PRI_kl*`, and `PRI__*64` format macros.

Control flow: preprocessor selects 64-bit kernel longs for MIPS n32 and x32, uses `<asm/posix_types.h>` when kernel typedefs are available, otherwise falls back to C `long`. It then derives printf length modifiers for kernel longs and kernel-exported 64-bit integer types.

State and persistence behavior: no runtime state; compile-time type/format contract.

Dependencies and integration points: foundational header for many ABI structs and numeric printers. The `PRI__64` selection matches Linux UAPI choices for ALPHA, IA64, powerpc64, MIPS64, Android exceptions, and 32-bit hosts.

Risks: wrong kernel-long sizing breaks pointer, length, and structure decoding across the tree. Format macros must match typedef choices to avoid undefined behavior in printf calls.

Test signals: build and run formatting tests on native 64-bit, 32-bit, x32, MIPS n32, and architectures using unsigned long for UAPI 64-bit fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kernel_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kernel_v4l2_types.h -->
# sources/test-tools/strace/src/kernel_v4l2_types.h

Purpose: defines stable V4L2 kernel buffer/event layouts and ioctl numbers independent of libc/kernel header time type drift.

Important APIs/types/functions: `kernel_v4l2_timeval_t`, `kernel_v4l2_buffer_t`, `kernel_v4l2_buffer_time32_t`, `kernel_v4l2_event_t`, `KERNEL_V4L2_HAVE_TIME32`, redefined `VIDIOC_QUERYBUF`, `VIDIOC_QBUF`, `VIDIOC_DQBUF`, `VIDIOC_PREPARE_BUF`, time32 variants, and `VIDIOC_DQEVENT`.

Control flow: includes Linux V4L2 UAPI and kernel time headers, defines sparc64-specific timeval layout, defines normal and optional time32 buffer structs, restores removed constants, and undefines/redefines ioctl request numbers using the controlled kernel layouts.

State and persistence behavior: no runtime state; it controls compile-time structure and ioctl encodings.

Dependencies and integration points: used by V4L2 ioctl decoders so request numbers and decoded buffers match tracee kernel ABI rather than host libc `struct timeval`/`timespec`.

Risks: V4L2 structs contain unions and pointer-like members, so time32/64 and sparc64 differences can alter ioctl numbers. Removed constants are retained for decoding older traces.

Test signals: cover V4L2 buffer ioctls on time32 and time64 ABIs, event dequeue, request-fd union field, sparc64 timeval layout, and constants removed from newer kernel headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kernel_v4l2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kexec.c -->
# sources/test-tools/strace/src/kexec.c

Purpose: decodes `kexec_load` and `kexec_file_load` syscalls.

Important APIs/types/functions: `SYS_FUNC(kexec_load)`, `SYS_FUNC(kexec_file_load)`, `print_seg`, `print_kexec_segments`, `KEXEC_SEGMENT_MAX`, `KEXEC_ARCH_MASK`, and xlats `kexec_load_flags`, `kexec_arch_values`, `kexec_file_load_flags`.

Control flow: `kexec_load` prints entry address, segment count, bounded segment array, and flags split into architecture mask plus remaining load flags. `print_seg` adapts fetched segment elements for compat word sizes. `kexec_file_load` prints kernel/initrd fds, command-line length and string, and file-load flags.

State and persistence behavior: no persistent state. Reads tracee memory for segment arrays and command line strings only.

Dependencies and integration points: depends on `<linux/kexec.h>`, fd/path string printers, current tracee word size, and generated xlat tables.

Risks: segment arrays are trusted only up to `KEXEC_SEGMENT_MAX`; larger counts fall back to an address. Compat segment element sizing must match current word size.

Test signals: cover native and compat segment arrays, oversized segment count fallback, architecture flags combined with load flags, command-line truncation by length, and invalid fds/pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/keyctl.c -->
# sources/test-tools/strace/src/keyctl.c

Purpose: decodes key-management syscalls `add_key`, `request_key`, and the multiplexed `keyctl` command set.

Important APIs/types/functions: `SYS_FUNC(add_key)`, `SYS_FUNC(request_key)`, `SYS_FUNC(keyctl)`, `print_keyring_serial_number`, `keyctl_read_key`, `keyctl_dh_compute`, `keyctl_pkey_query`, `keyctl_pkey_op`, `keyctl_capabilities`, `fetch_keyctl_kdf_params`, `tprint_iov`, and xlats for key specs, permissions, commands, reqkey defaults, pkey ops, move flags, and capabilities.

Control flow: simple add/request syscalls print strings, payloads, lengths, and destination keyrings. `keyctl` prints the operation on entry and dispatches by command. Some commands are entry-only, read-like commands print buffers on exit, DH compute prints parameters on entry and output/KDF parameters on exit, pkey operations save output length for exit decoding, and capabilities are decoded as returned byte arrays.

State and persistence behavior: uses `tcp->aux`/private ulong for pkey output lengths and normal syscall phase state. No durable global state. Tracee memory reads include strings, payload buffers, KDF params, pkey params, and returned capability/output buffers.

Dependencies and integration points: integrates with `fetch_struct_keyctl_kdf_params.c` via `keyctl_kdf_params.h`, generic iovec decoding for `KEYCTL_INSTANTIATE_IOV`, uid/error printers, and generated key xlat tables.

Risks: `keyctl` is multiplexed and new commands must be added carefully to preserve entry/exit returns. Buffer output length is capped by syscall return or user length; KDF `otherinfo` is only valid when `otherinfolen` is nonzero. Pkey encrypt/decrypt/sign differ from verify in `op2` direction.

Test signals: cover add/request, all common keyctl commands, read/describe/security success and error paths, instantiate iov, DH compute with and without KDF otherinfo, pkey query/encrypt/decrypt/sign/verify, move flags, capabilities arrays, and unknown command fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/keyctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/keyctl_kdf_params.h -->
# sources/test-tools/strace/src/keyctl_kdf_params.h

Purpose: defines strace's personality-neutral view of keyctl KDF parameters for Diffie-Hellman key computation decoding.

Important APIs/types/functions: `struct strace_keyctl_kdf_params`, `CRYPTO_MAX_ALG_NAME`, `KEYCTL_KDF_MAX_OI_LEN`, `kernel_ulong_t hashname`, `kernel_ulong_t otherinfo`, `otherinfolen`, and `__spare`.

Control flow: header-only constants and structure definition. Pointer fields use `kernel_ulong_t` so the mpers fetch helper can copy tracee pointers into a stable host-side representation.

State and persistence behavior: no state; instances are temporary decoded copies of tracee KDF parameter structs.

Dependencies and integration points: includes `<linux/keyctl.h>` and `kernel_types.h`; used by `keyctl.c` and `fetch_struct_keyctl_kdf_params.c`.

Risks: the structure must match the kernel `keyctl_kdf_params` ABI, including spare fields. Pointer size mismatch would break KDF string/otherinfo decoding.

Test signals: DH compute tests should cover null KDF pointer, valid hash name, zero and nonzero `otherinfolen`, nonzero spare array, and compat pointer widths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/keyctl_kdf_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kill_save_errno.h -->
# sources/test-tools/strace/src/kill_save_errno.h

Purpose: provides a tiny helper that sends a signal without clobbering the caller's `errno`.

Important APIs/types/functions: `kill_save_errno(pid_t pid, int sig)`, `kill`, `errno`, `<sys/types.h>`, and `<signal.h>`.

Control flow: saves current `errno`, calls `kill(pid, sig)`, restores saved `errno`, and returns the `kill` result code.

State and persistence behavior: temporarily observes and restores thread-local `errno`; no persistent state.

Dependencies and integration points: used in code paths where strace must signal processes while preserving an earlier syscall/diagnostic error.

Risks: callers must inspect the returned `kill` status because `errno` will not describe `kill` failure afterward. This is intentional but easy to misuse.

Test signals: unit or integration checks should set `errno`, call success and failure cases, assert `errno` is unchanged, and verify the return code is propagated.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kill_save_errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/kvm.c -->
# sources/test-tools/strace/src/kvm.c

Purpose: decodes KVM ioctls, tracks vCPU file descriptors, and optionally prints `struct kvm_run` exit state.

Important APIs/types/functions: `kvm_ioctl`, `kvm_vcpu_info_free`, `vcpu_find`, `vcpu_register`, `vcpu_get_info`, `kvm_ioctl_create_vcpu`, decoders for memory regions, regs, sregs, CPUID, check-extension, run, `kvm_run_structure_decode`, `kvm_run_structure_decoder_init`, `decode_kvm_run_structure`, and arch hooks from `arch_kvm.c`.

Control flow: `kvm_ioctl` dispatches by ioctl code. Creating a vCPU prints cpuid and, on successful exit, records returned fd. Memory, register, sreg, and CPUID ioctls decode pointed-to structures with get/set entry/exit direction. `KVM_RUN` optionally snapshots the `kvm_run` mmap on entry, decodes exit reason on successful exit, and later prints before/after run structures including IO/MMIO union details.

State and persistence behavior: maintains a per-tracee linked list of `vcpu_info` records in `tcb`, including fd, cpuid, mmap address/length, and resolution status. Uses mmap cache to find anon-inode vCPU mappings and stores entering/leaving run snapshots. `kvm_vcpu_info_free` releases this state.

Dependencies and integration points: compiled under `HAVE_LINUX_KVM_H`; depends on Linux KVM headers, architecture-specific KVM printers, mmap cache, fd path resolution, xlat tables for exits, IO directions, caps, CPUID flags, and memory flags.

Risks: vCPU mapping discovery depends on anon-inode path names and mmap cache freshness. `struct kvm_run` decoding is gated by runtime mode and may be unavailable if mmap cannot be resolved. Static storage in exit auxiliary decoding is reused per call.

Test signals: cover KVM_CREATE_VM/CREATE_VCPU fd returns, vCPU registration, KVM_SET_USER_MEMORY_REGION, regs/sregs get/set phase behavior, CPUID arrays with abbrev/non-abbrev output, KVM_CHECK_EXTENSION xlat, KVM_RUN exit reason, IO/MMIO union decoding, mmap remap handling, and cleanup of tracked vCPUs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/kvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/landlock.c -->
# sources/test-tools/strace/src/landlock.c

Purpose: decodes Landlock ruleset creation, rule addition, and self-restriction syscalls.

Important APIs/types/functions: `SYS_FUNC(landlock_create_ruleset)`, `SYS_FUNC(landlock_add_rule)`, `SYS_FUNC(landlock_restrict_self)`, `print_landlock_ruleset_attr`, `print_landlock_path_beneath_attr`, `print_landlock_net_port_attr`, and xlats for create flags, rule types, filesystem access, network access, and scope flags.

Control flow: ruleset creation decodes only fields present in the supplied size, from mandatory filesystem access through newer network and scope fields, and returns fd status unless version/errata flags mean no fd. `landlock_add_rule` prints the ruleset fd, dispatches the rule attribute by rule type, then prints raw flags. Restrict self prints fd and raw flags.

State and persistence behavior: no persistent state. Reads tracee memory for ruleset and rule attribute structures with size-aware bounds.

Dependencies and integration points: depends on `<linux/landlock.h>`, fd printers, and generated Landlock xlat tables. Integrated as syscall decoders for Landlock's dedicated syscalls.

Risks: Landlock structures are extensible; size checks must avoid reading beyond known fields while showing trailing data. New rule types currently fall back to raw addresses.

Test signals: cover minimal and extended ruleset sizes, version/errata no-fd return behavior, filesystem and network rule attributes, unknown rule type fallback, scope flags, and inaccessible attribute pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/landlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/largefile_wrappers.h -->
# sources/test-tools/strace/src/largefile_wrappers.h

Purpose: abstracts libc large-file API name differences behind strace-local wrapper names.

Important APIs/types/functions: `open_file`, `fopen_stream`, `fcntl_fd`, `fstat_fd`, `strace_stat_t`, `lstat_file`, `stat_file`, `struct_dirent`, `read_dir`, `struct_rlimit`, and `set_rlimit`.

Control flow: if `_LARGEFILE64_SOURCE` is enabled, wrapper macros select `*64` variants when available or appropriate; otherwise they map to regular libc calls and types.

State and persistence behavior: no state; compile-time macro aliases only.

Dependencies and integration points: includes `defs.h` for configure macros such as `HAVE_OPEN64`, `HAVE_FOPEN64`, and `HAVE_FCNTL64`. Used by host-side strace code that needs large-file-capable filesystem and resource-limit APIs.

Risks: availability differs by libc and architecture, so wrappers must avoid referencing missing symbols. Mixing wrapper and raw libc names can reintroduce large-file bugs.

Test signals: build with and without `_LARGEFILE64_SOURCE`, run host filesystem operations on large files, and compile on libcs lacking selected `*64` entry points.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/largefile_wrappers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ldt.c -->
# sources/test-tools/strace/src/ldt.c

Purpose: decodes architecture-specific LDT/thread-area syscalls, especially x86 `struct user_desc`.

Important APIs/types/functions: `print_user_desc`, `SYS_FUNC(modify_ldt)`, `SYS_FUNC(set_thread_area)`, `SYS_FUNC(get_thread_area)`, `USER_DESC_ENTERING`, `USER_DESC_EXITING`, `USER_DESC_BOTH`, `set_tcb_priv_data`, and `tcp->auxstr`.

Control flow: when `HAVE_STRUCT_USER_DESC` is available, `print_user_desc` can print entry number on entry, full descriptor on exit, or the whole structure at once. `modify_ldt` prints function, pointer/descriptor, bytecount, and adjusts x86_64 clipped negative return values into syscall errors. `set_thread_area` prints the descriptor and on successful exit attaches returned entry number. `get_thread_area` splits descriptor printing across entry and exit. M68K/MIPS provide simple address decoders.

State and persistence behavior: `get_thread_area` stores the original `entry_number` in `tcb` private data for exit comparison. `set_thread_area` uses static `outstr` for the auxiliary return string. No durable global state.

Dependencies and integration points: depends on `<asm/ldt.h>`, `xstring.h`, architecture macros, verbose/syserror state, and syscall table selection for thread-area APIs.

Risks: field availability differs by architecture and `lm` is only meaningful for 64-bit kernel-long size. `modify_ldt` return-error rewriting is x86 ABI-specific and easy to regress.

Test signals: cover `modify_ldt` with descriptor-sized and non-descriptor buffers, clipped negative return values, `set_thread_area` returned entry number, `get_thread_area` value changes, missing/inaccessible descriptors, and M68K/MIPS simple decoders.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ldt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/link.c -->
# sources/test-tools/strace/src/link.c

Purpose: decodes hard-link, unlink-at, and symlink-at pathname syscalls.

Important APIs/types/functions: `SYS_FUNC(link)`, `SYS_FUNC(linkat)`, `SYS_FUNC(unlinkat)`, `SYS_FUNC(symlinkat)`, `printpath`, `print_dirfd`, `printflags`, and `at_flags`.

Control flow: each decoder prints named path and dirfd arguments in syscall order. `linkat` and `unlinkat` append `AT_*` flag decoding; `symlinkat` prints target, destination directory fd, and link path.

State and persistence behavior: no persistent state. Reads tracee strings through `printpath`.

Dependencies and integration points: depends on `<linux/fcntl.h>` for `AT_*` constants and the generated `at_flags` xlat table. Integrated with filesystem syscall decoders.

Risks: path memory can be inaccessible; dirfd semantics must preserve source vs destination naming. `at_flags` includes flags that are syscall-specific, so tests should allow unknown/future flags.

Test signals: cover absolute/relative paths, `AT_FDCWD`, nonstandard dirfds, `AT_SYMLINK_FOLLOW`, `AT_REMOVEDIR`, inaccessible paths, and unknown flag bits.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/32/ioctls_inc.h -->
# sources/test-tools/strace/src/linux/32/ioctls_inc.h

Purpose: selects the correct generated 32-bit ioctl table include based on architecture alignment rules.

Important APIs/types/functions: preprocessor branches for `M68K`, `X86_64`, `X32`, `SIZEOF_STRUCT_I64_I32`, and includes `ioctls_inc_align16.h`, `ioctls_inc_align32.h`, or `ioctls_inc_align64.h`.

Control flow: M68K uses 16-bit alignment table; x86_64/x32 and architectures where `struct { i64; i32; }` is smaller than two long longs use 32-bit alignment; all others use 64-bit alignment.

State and persistence behavior: no runtime state; compile-time include selection only.

Dependencies and integration points: consumed by ioctl decoding table generation for 32-bit personalities. Depends on configure-probed structure size macros and architecture defines.

Risks: wrong alignment table maps ioctl numbers to wrong symbolic commands. The size heuristic must match kernel UAPI packing for each supported architecture.

Test signals: build ioctl tables for m68k, x86_64 compat/x32, and an align64 32-bit target; verify known ioctl numbers resolve to expected names in each configuration.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/32/ioctls_inc.h -->
