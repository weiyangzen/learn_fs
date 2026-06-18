# subset-b-005969 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/siginfo.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/siginfo.h

## Purpose
Defines the generic Linux UAPI `siginfo_t`, `sigval_t`, signal-specific `si_code` constants, and `sigevent_t` layout used by user space, libc, ptrace, seccomp, POSIX timers, and signal delivery paths. The file is ABI rather than executable logic.

## Important APIs, Types, And Functions
Key exports are `sigval_t`, `union __sifields`, `siginfo_t`, field aliases such as `si_pid`, `si_addr`, `si_syscall`, `si_perf_data`, and constants for `SI_*`, `ILL_*`, `FPE_*`, `SEGV_*`, `BUS_*`, `TRAP_*`, `CLD_*`, `POLL_*`, `SYS_*`, and `SIGEV_*`. `sigevent_t` carries notification mode, signal number, payload value, optional thread function, and thread id.

## Control Flow
There is no runtime control flow. Compile-time conditionals select architecture-specific field order, band/clock types, attributes, padding, and IA64-specific `SEGV` naming. `SI_FROMUSER()` and `SI_FROMKERNEL()` classify origin from `si_code`.

## State, Persistence, And Dependencies
Instances are transient kernel/user ABI payloads copied during signal delivery and timer setup. It depends on `<linux/compiler.h>` and `<linux/types.h>` for `__user`, kernel integer, pid, uid, timer, and clock types.

## Integration Points
Integrated by `asm/siginfo.h`, `signal.h`, syscall implementations for `rt_sigqueueinfo`, `waitid`, POSIX timers, seccomp, perf signal traps, ptrace, and libc signal headers.

## Risks
The 128-byte `siginfo_t` size and 32-bit alignment warning are hard ABI constraints. Adding 64-bit-aligned fields, changing union order, or changing constants breaks user space. Architecture overrides must preserve historical layouts.

## Test Signals
Useful checks include `sizeof(siginfo_t) == 128`, architecture ABI layout tests, signal delivery tests for every `si_code` class, seccomp `SIGSYS`, perf `TRAP_PERF`, POSIX timer `sigevent`, and 32/64-bit compat signal frame tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/siginfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/signal-defs.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/signal-defs.h

## Purpose
Provides generic signal action flag definitions, signal mask operation constants, and handler/restorer pointer typedefs shared by architectures.

## Important APIs, Types, And Functions
Exports `SA_NOCLDSTOP`, `SA_NOCLDWAIT`, `SA_SIGINFO`, `SA_UNSUPPORTED`, `SA_EXPOSE_TAGBITS`, `SA_ONSTACK`, `SA_RESTART`, `SA_NODEFER`, `SA_RESETHAND`, aliases `SA_NOMASK` and `SA_ONESHOT`, `SIG_BLOCK`, `SIG_UNBLOCK`, `SIG_SETMASK`, `__sighandler_t`, `__sigrestore_t`, `SIG_DFL`, `SIG_IGN`, and `SIG_ERR`.

## Control Flow
Only preprocessor guards are present. Architecture headers can define existing flag values before inclusion; otherwise the generic values are used. Handler typedefs are skipped for assembly.

## State, Persistence, And Dependencies
No persistent state. The constants persist as part of the user/kernel ABI for `sigaction` and `rt_sigprocmask`. It depends on `<linux/compiler.h>` for `__user` and `__force`.

## Integration Points
Included by generic `signal.h` and architecture `asm/signal.h` variants. `SA_UNSUPPORTED` is specifically used by userspace probing of `sigaction` flag support.

## Risks
Flag bit reuse is dangerous because several holes are reserved by older architectures. `SA_UNSUPPORTED` semantics rely on old kernels not clearing unknown flags, so changing that value would break feature detection.

## Test Signals
Compile UAPI headers for C and assembly, run `sigaction` flag probing tests, verify `SA_EXPOSE_TAGBITS` address-tag behavior on supporting architectures, and ensure legacy aliases match their modern equivalents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/signal-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/signal.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/signal.h

## Purpose
Defines generic signal numbers, signal set layout, `struct sigaction`, and alternate signal stack structure for new Linux architectures.

## Important APIs, Types, And Functions
Exports `_NSIG`, `_NSIG_BPW`, `_NSIG_WORDS`, standard signal numbers 1-31, realtime range `SIGRTMIN` to `SIGRTMAX`, `MINSIGSTKSZ`, `SIGSTKSZ`, `sigset_t`, `old_sigset_t`, `struct sigaction`, and `stack_t`.

## Control Flow
Compile-time logic sizes `sigset_t` from `__BITS_PER_LONG`, imports `asm-generic/signal-defs.h`, marks `__ARCH_HAS_SA_RESTORER` if an architecture defines `SA_RESTORER`, and hides user-visible `struct sigaction` inside kernel builds.

## State, Persistence, And Dependencies
No runtime state. The bitset and structure layouts persist in process signal masks, syscall arguments, and signal frames. It depends on `<linux/types.h>` and generic signal definitions.

## Integration Points
Used by `rt_sigaction`, `rt_sigprocmask`, `sigaltstack`, signal frame construction, libc signal APIs, and `ucontext.h` through `stack_t` and `sigset_t`.

## Risks
Signal numbers and `sigset_t` word layout are ABI. Architecture overrides must avoid conflicting with the generic realtime range and stack constants. `sa_mask` being last is an extensibility contract.

## Test Signals
Run signal number ABI checks, `sigset_t` size tests across 32/64-bit builds, `sigaltstack` delivery tests, `SA_RESTORER` architecture smoke tests, and libc header compatibility builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/socket.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/socket.h

## Purpose
Defines generic `SOL_SOCKET` option numbers and related `SCM_*` control-message aliases for socket syscalls.

## Important APIs, Types, And Functions
Exports `SO_*` constants for buffer sizing, credentials, timestamps, BPF filters, reuseport BPF, busy polling, zerocopy, txtime, netns cookies, device memory, priority, pass-rights, and `SO_INQ`. It also maps old/new time64-sensitive options through `SO_TIMESTAMP`, `SO_RCVTIMEO`, and `SO_SNDTIMEO`.

## Control Flow
Preprocessor logic preserves powerpc-specific credential option overrides and chooses old versus new timestamp/timeval option numbers based on `__BITS_PER_LONG`, x32, and `sizeof(time_t)` in user space.

## State, Persistence, And Dependencies
No local state. The constants select per-socket kernel state via `setsockopt`, `getsockopt`, and ancillary data. It depends on `<linux/posix_types.h>` and `<asm/sockios.h>`.

## Integration Points
Consumed by networking stacks, libc socket headers, applications, BPF socket filters, timestamping APIs, ioctls from `sockios.h`, and protocol families that honor socket-level options.

## Risks
Numeric option values are stable ABI. Time option remapping is subtle for 32-bit time64 transitions. `SCM_*` aliases must track their matching `SO_*` options. Privileged options such as force buffers, marks, and priority need kernel-side permission checks.

## Test Signals
Build header tests across 32-bit, 64-bit, and x32; `setsockopt`/`getsockopt` round trips for each option family; timestamp ABI tests with 32-bit time64; ancillary data decoding tests; BPF attach/detach and reuseport tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/sockios.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/sockios.h

## Purpose
Provides generic socket-level ioctl command numbers.

## Important APIs, Types, And Functions
Exports `FIOSETOWN`, `SIOCSPGRP`, `FIOGETOWN`, `SIOCGPGRP`, `SIOCATMARK`, `SIOCGSTAMP_OLD`, and `SIOCGSTAMPNS_OLD`.

## Control Flow
No runtime or compile-time branching beyond the include guard.

## State, Persistence, And Dependencies
No state. The constants address socket ownership, process-group signaling, out-of-band mark detection, and old timeval/timespec timestamp reads in the socket layer.

## Integration Points
Included by architecture `asm/sockios.h` and indirectly by socket headers. Used by `ioctl(2)` on sockets and compatibility paths that still expose old timestamp commands.

## Risks
These hexadecimal ioctl values are ABI. Old timestamp commands are time-size-sensitive and must remain distinct from newer time64 mechanisms.

## Test Signals
Socket `ioctl` tests for owner and process group, `SIOCATMARK` tests with urgent data, and compat timestamp tests on 32-bit user space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/sockios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/stat.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/stat.h

## Purpose
Defines generic `struct stat` and conditional `struct stat64` layouts for file metadata syscalls.

## Important APIs, Types, And Functions
Exports `STAT_HAVE_NSEC`, `struct stat`, and `struct stat64` when `__BITS_PER_LONG != 64` or `__ARCH_WANT_STAT64`. Fields cover device, inode, mode, link count, uid/gid, rdev, size, block size, blocks, and nanosecond timestamps.

## Control Flow
Preprocessor selection includes `stat64` only for 32-bit or opt-in architectures. There are no functions.

## State, Persistence, And Dependencies
The structs are copied across syscall boundaries and encode persistent filesystem metadata snapshots. It depends on `<asm/bitsperlong.h>`.

## Integration Points
Used by `stat`, `fstat`, `newfstatat`, `stat64`, libc metadata APIs, and filesystem implementations including Ceph client paths that fill generic inode metadata.

## Risks
Layout, signedness, padding, and timestamp field width are ABI. Time fields based on `long` or `int` interact with 32-bit time limits. New architectures should avoid inheriting old layout mistakes.

## Test Signals
ABI size/offset checks, stat syscall round trips on regular files/devices/symlinks, nanosecond timestamp verification, large inode and large file tests, and 32-bit compat stat64 tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/statfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/statfs.h

## Purpose
Defines generic filesystem statistics structures returned by `statfs` and `fstatfs`.

## Important APIs, Types, And Functions
Exports `__statfs_word`, `struct statfs`, `struct statfs64`, `struct compat_statfs64`, and optional packing macros `ARCH_PACK_STATFS64` and `ARCH_PACK_COMPAT_STATFS64`.

## Control Flow
Compile-time selection chooses `__kernel_long_t` on 64-bit and `__u32` on 32-bit unless an architecture overrides `__statfs_word`. Packing attributes may be supplied by architectures.

## State, Persistence, And Dependencies
No internal state. The structs are snapshots of filesystem capacity, free blocks, free inodes, filesystem id, name length, fragment size, and mount flags. It depends on `<linux/types.h>`.

## Integration Points
Used by `statfs`, `fstatfs`, compat syscall handlers, libc filesystem APIs, and filesystem clients such as Ceph that report cluster-backed capacity through VFS.

## Risks
Signedness and size vary by word type. Padding differs on ARM, IA64, x86_64 compat, S390x, and MIPS cases. Overflows are possible when 32-bit `statfs` reports large distributed filesystems.

## Test Signals
Size/offset ABI tests per architecture, `statfs64` large-capacity tests, compat syscall tests, mount flag reporting tests, and filesystem-specific capacity/inode accounting comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/swab.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/swab.h

## Purpose
Defines generic byte-swap configuration for user and kernel builds.

## Important APIs, Types, And Functions
The main export is `__SWAB_64_THRU_32__` for 32-bit architectures that should implement 64-bit byte swaps through two 32-bit operations when supported.

## Control Flow
If `__BITS_PER_LONG == 32` and either GNU C non-strict mode or kernel build is active, the macro is enabled. No functions are defined.

## State, Persistence, And Dependencies
No state. It influences inline byte-order helpers included elsewhere. It depends on `<asm/bitsperlong.h>`.

## Integration Points
Used by generic Linux byteorder/swab headers and indirectly by UAPI structures requiring endian conversion.

## Risks
Compiler capability assumptions matter in strict ANSI user-space builds. Misdefining the macro can produce inefficient or invalid 64-bit byte-swap code on 32-bit targets.

## Test Signals
Compile byteorder headers with GCC strict/non-strict modes, 32/64-bit builds, endian conversion unit tests, and generated assembly inspection for 64-bit swaps on 32-bit architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/termbits-common.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/termbits-common.h

## Purpose
Provides generic terminal flag and speed constants shared by terminal ABI headers.

## Important APIs, Types, And Functions
Exports `cc_t`, `speed_t`, input flags such as `IGNBRK`, `ICRNL`, and `IXANY`, output flags such as `OPOST` and `OCRNL`, base baud constants `B0` through `B38400`, aliases `EXTA`/`EXTB`, control flags `ADDRB`, `CMSPAR`, `CRTSCTS`, `IBSHIFT`, `tcflow` actions, and `tcflush` selectors.

## Control Flow
No runtime flow. The header only defines constants.

## State, Persistence, And Dependencies
Terminal drivers persist these values in termios state associated with tty devices. No includes are required.

## Integration Points
Included by `termbits.h`, consumed by `termios.h`, tty line disciplines, libc terminal APIs, shells, serial tools, and pseudo-terminal implementations.

## Risks
Flag values are ABI and must stay compatible with legacy ioctl encodings. Baud and input-speed bit placement is shared with `CBAUD`/`CIBAUD` logic in `termbits.h`.

## Test Signals
`tcgetattr`/`tcsetattr` round trips, serial baud programming tests, flow-control tests, `tcflush`/`tcflow` behavior, and compile comparison against libc-exported termios constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/termbits-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/termbits.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/termbits.h

## Purpose
Defines generic `termios`, `termios2`, and `ktermios` layouts plus terminal control-character indexes and mode flags.

## Important APIs, Types, And Functions
Exports `tcflag_t`, `NCCS`, `struct termios`, `struct termios2`, `struct ktermios`, `VINTR` through `VEOL2`, input/output/control/local mode flags, high baud constants through `B4000000`, `BOTHER`, `CBAUD`, `CIBAUD`, and `TCSANOW`/`TCSADRAIN`/`TCSAFLUSH`.

## Control Flow
No runtime control flow. It imports common term bits and declares ABI layouts.

## State, Persistence, And Dependencies
These structures persist tty configuration in kernel tty state and are copied through terminal ioctls. It depends on `<asm-generic/termbits-common.h>`.

## Integration Points
Used by `termios.h`, `ioctls.h` commands such as `TCGETS`, `TCSETS`, `TCGETS2`, tty drivers, pty devices, libc, shells, terminal emulators, and serial configuration tools.

## Risks
`NCCS`, flag values, and speed encodings are fixed ABI. `termios2` custom speeds depend on `BOTHER` and explicit `c_ispeed`/`c_ospeed`. User/kernel `ktermios` exposure must stay layout-compatible here.

## Test Signals
Terminal ioctl ABI tests, custom baud `TCGETS2`/`TCSETS2`, pty canonical/raw mode tests, control character behavior, and comparison with architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/termbits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/termios.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/termios.h

## Purpose
Provides generic higher-level terminal ABI definitions, legacy `termio`, window size, and modem-control bits.

## Important APIs, Types, And Functions
Exports `struct winsize`, `NCC`, `struct termio`, modem line bits `TIOCM_LE`, `TIOCM_DTR`, `TIOCM_RTS`, `TIOCM_CTS`, `TIOCM_CAR`, `TIOCM_RNG`, `TIOCM_DSR`, aliases `TIOCM_CD`/`TIOCM_RI`, and output/loop bits.

## Control Flow
No runtime logic. It includes architecture `termbits.h` and `ioctls.h`.

## State, Persistence, And Dependencies
Window size and terminal settings persist per tty and are exchanged via ioctls. Dependencies are `<asm/termbits.h>` and `<asm/ioctls.h>`.

## Integration Points
Used by terminal ioctls, `SIGWINCH` generation, serial modem-control operations, libc termios compatibility, shells, terminal emulators, and pty stacks.

## Risks
Legacy `termio` uses 16-bit flags and only `NCC == 8`, so compat handling must not confuse it with `termios`. Modem bit values are fixed for existing serial tooling.

## Test Signals
`TIOCGWINSZ`/`TIOCSWINSZ`, `SIGWINCH` delivery, `TCGETA`/`TCSETA` legacy termio tests, modem status ioctl tests, and architecture header compatibility builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/termios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/types.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/types.h

## Purpose
Selects the generic fixed-width integer ABI type model.

## Important APIs, Types, And Functions
This header exports the type definitions from `<asm-generic/int-ll64.h>`, including the `__s*` and `__u*` integer types used by UAPI headers.

## Control Flow
No branching beyond the include guard.

## State, Persistence, And Dependencies
No state. It establishes the integer widths used in all dependent user/kernel ABI structs.

## Integration Points
Included by architecture `asm/types.h` and widely by Linux UAPI headers, including signal, statfs, CXL, and DRM headers in this work item.

## Risks
Changing the included type model would alter ABI layout for nearly every structure using `__u64`, `__u32`, and related types.

## Test Signals
Compile-time type-width checks, UAPI structure size checks, libc header compatibility, and cross-architecture build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/ucontext.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/ucontext.h

## Purpose
Defines generic `struct ucontext` used to describe user execution context around signal handling.

## Important APIs, Types, And Functions
Exports `struct ucontext` with `uc_flags`, `uc_link`, `uc_stack`, architecture `sigcontext`, and `uc_sigmask`.

## Control Flow
No runtime flow or conditionals beyond the include guard.

## State, Persistence, And Dependencies
Instances are transient signal-frame and user context payloads. The mask is deliberately last for extensibility. It depends on prior definitions of `stack_t`, `struct sigcontext`, and `sigset_t` from architecture signal context headers.

## Integration Points
Used by signal frame setup/restore, `getcontext`-style libc APIs where available, debuggers, unwinders, checkpoint/restore tools, and architecture-specific signal return paths.

## Risks
Field order is ABI. `struct sigcontext` is architecture-owned, so this generic wrapper must be included only after appropriate architecture definitions. Changing `uc_sigmask` placement could break signal-frame parsing.

## Test Signals
Signal handler `ucontext_t` inspection, `sigreturn` restore tests, alternate stack interaction, ptrace/unwind checks, and per-architecture structure offset checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/unistd.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/unistd.h

## Purpose
Defines the generic Linux syscall number table and maps numbers to kernel syscall entry symbols for architectures that use the generic ABI.

## Important APIs, Types, And Functions
Exports `__NR_*` numbers from `io_setup` through `rseq_slice_yield`, `__NR_syscalls 472`, helper macros `__SC_3264`, `__SC_COMP`, `__SC_COMP_3264`, architecture-reserved range `__NR_arch_specific_syscall`, and aliases such as `__NR_fcntl`/`__NR_fcntl64` depending on word size.

## Control Flow
Preprocessor logic selects 32-bit versus 64-bit entry points, compat handlers, time32/time64 syscall exposure, optional legacy syscalls requested by `__ARCH_WANT_*`, and MMU-only calls skipped under `__ARCH_NOMMU`.

## State, Persistence, And Dependencies
No runtime state. The table is persistent ABI: numbers are embedded in libc, seccomp filters, tracers, audit, and applications. It depends on `<asm/bitsperlong.h>`.

## Integration Points
Used by architecture syscall tables, generated syscall wrappers, libc, seccomp BPF policies, audit, ptrace, strace, and all kernel syscall dispatch paths. Filesystem-relevant entries include xattrs, open, statfs, syncfs, statx, mount APIs, file attribute syscalls, and namespace listing.

## Risks
Numbers cannot be reused or reordered. Time32/time64 and compat mappings are subtle. Optional holes and architecture ranges must be preserved. `__NR_syscalls` must track the highest assigned generic number plus one.

## Test Signals
Generated syscall table comparison, libc syscall-number tests, seccomp allowlist tests, 32-bit compat and time64 syscall tests, `__NR_syscalls` bounds checks, and smoke tests for newly added numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/cxl/features.h -->
# sources/distributed-fs/ceph-client/include/uapi/cxl/features.h

## Purpose
Defines UAPI payloads for CXL mailbox feature discovery, feature reads, and feature writes following CXL 3.2 command definitions.

## Important APIs, Types, And Functions
Exports `__uapi_uuid_t`, `struct cxl_mbox_get_sup_feats_in`, feature effect flags, `struct cxl_feat_entry`, feature flags, `struct cxl_mbox_get_sup_feats_out`, `struct cxl_mbox_get_feat_in`, `enum cxl_get_feat_selection`, `struct cxl_mbox_set_feat_in`, `enum cxl_set_feat_flag_data_transfer`, and set-feature masks.

## Control Flow
No runtime flow. Kernel builds replace `__uapi_uuid_t` with `uuid_t` after a size assertion. Structures use packed layout, flexible arrays, `__struct_group`, and counted-by annotations.

## State, Persistence, And Dependencies
Mailbox payloads represent device feature state. Set-feature flags describe whether changes are current, default, saved, reset-persistent, or require reset/background effects. It depends on `<linux/types.h>` plus kernel-only `<linux/uuid.h>`.

## Integration Points
Used by CXL memory-device mailbox command handling, user tools issuing CXL ioctl/mailbox commands, firmware feature negotiation, and management daemons.

## Risks
Packed layout and UUID alignment are critical. Reserved fields must be zero. Multi-part set transfers need offset/version/abort semantics handled carefully. Effects flags inform reset and persistence behavior, so misreporting them can cause unsafe configuration changes.

## Test Signals
UAPI size/offset tests, mailbox encode/decode tests against CXL 3.2 tables, reserved-zero validation, UUID alignment checks, multi-transfer set-feature tests, and feature persistence/reset behavior tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/cxl/features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/amdgpu_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/amdgpu_drm.h

## Purpose
Defines the public AMDGPU DRM ioctl ABI for buffer management, virtual memory, command submission, synchronization, scheduling, user queues, metadata, and device information.

## Important APIs, Types, And Functions
Key exports include `DRM_IOCTL_AMDGPU_*`, GEM create/mmap/wait/userptr/op/list structs, BO list structs, context operations and reset state, user queue create/signal/wait/MQD metadata, VM reserve and VA map/unmap structures, scheduler priority override, CS chunk structures, fence/syncobj conversion, tiling helpers, info query IDs, memory/device/HW IP/video/VBIOS/GPUVM fault structs, VRAM type constants, and GPU family constants.

## Control Flow
The header contains no executable control flow, but it encodes ioctl workflows: create GEM, map VA, create context or user queue, submit CS chunks with fences and dependencies, wait or convert fences, query device state, and update metadata. Unions split in/out payloads for bidirectional ioctls.

## State, Persistence, And Dependencies
Kernel state addressed by this ABI includes GEM BOs, BO lists, GPU VMs, contexts, scheduler priority overrides, syncobjs, fences, user queues, doorbells, and device telemetry. It depends on `drm.h`.

## Integration Points
Used by Mesa/RADV/RadeonSI, ROCm components, libdrm_amdgpu, window systems, compute runtimes, kernel AMDGPU ioctl handlers, TTM memory management, DRM syncobj, PRIME/GEM, and firmware discovery paths.

## Risks
Every ioctl number, flag, and struct layout is ABI. User pointers and counts require validation. Userptr is explicitly unreliable and needs fallbacks. VM mapping flags interact with cache coherence, encryption, DCC, and PTE memory types. High-priority queues and secure queues require authorization.

## Test Signals
libdrm_amdgpu ioctl tests, Mesa/ROCm conformance, GEM create/map/free stress, CS submission and fence waits, VM bind/unbind fault tests, 32/64-bit struct checks, userptr fallback tests, syncobj timeline tests, GPU reset/RAS query tests, and info query compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/amdgpu_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/amdxdna_accel.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/amdxdna_accel.h

## Purpose
Defines the AMD XDNA accelerator DRM UAPI for NPU hardware contexts, BOs, command execution, telemetry, resource queries, and power/preemption state.

## Important APIs, Types, And Functions
Exports invalid-handle constants, QoS priorities, device and ioctl enums, `amdxdna_qos_info`, hardware-context create/destroy/config payloads, CU configuration arrays, BO type/create/info/sync structures, command submit payloads, AIE status/version/metadata structs, clock/sensor/context/power/firmware/resource telemetry structs, `amdxdna_drm_get_info`, array-query structures, state-setting structures, and `DRM_IOCTL_AMDXDNA_*`.

## Control Flow
Ioctl workflows are declarative: create BOs, create a hardware context with QoS and UMQ/log buffers, configure CUs or debug buffers, submit commands or dependencies/signals, query metadata/telemetry/arrays, set power or preemption state, and destroy resources.

## State, Persistence, And Dependencies
Persistent kernel state includes hardware contexts, command queues, syncobjs, BO handles, device heap allocations, context telemetry counters, async errors, power mode, and preemption attributes. It depends on `<linux/stddef.h>` and `drm.h`.

## Integration Points
Used by AMD XDNA kernel driver, NPU runtime/shim layers, XRT-style management tools, DRM syncobj infrastructure, dma-buf-backed BO flows, and telemetry consumers.

## Risks
Variable-length arrays and user pointers need strict size validation. Many fields are MBZ and should reject nonzero values for forward compatibility. Command handle arrays, QoS hints, and device memory BO accounting are security and robustness sensitive. Power/preemption setters affect global device behavior.

## Test Signals
Ioctl ABI size tests, create/config/destroy context lifecycle tests, BO mmap/sync/import tests, command completion syncobj tests, telemetry buffer sizing tests, MBZ rejection tests, power mode permission tests, and async error query tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/amdxdna_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/armada_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/armada_drm.h

## Purpose
Defines the small Armada DRM driver ioctl ABI for GEM buffer creation, mmap offset lookup, and CPU writes.

## Important APIs, Types, And Functions
Exports command IDs `DRM_ARMADA_GEM_CREATE`, `DRM_ARMADA_GEM_MMAP`, `DRM_ARMADA_GEM_PWRITE`, macro `ARMADA_IOCTL`, structs `drm_armada_gem_create`, `drm_armada_gem_mmap`, `drm_armada_gem_pwrite`, and matching `DRM_IOCTL_ARMADA_*` values.

## Control Flow
No executable flow. The intended sequence is create GEM, request mmap information, map or write buffer contents, and hand the GEM object to KMS/driver paths.

## State, Persistence, And Dependencies
Kernel state consists of GEM objects and mmap offsets associated with a DRM file. `pwrite` copies user memory into a GEM buffer at a byte offset. It depends on `drm.h`.

## Integration Points
Used by Armada userspace drivers/tools and the Armada kernel DRM ioctl handlers. It relies on generic DRM command numbering and GEM handle lifetime rules.

## Risks
The `pwrite` payload has a user pointer, handle, offset, and size, so bounds checking and overflow handling are essential. The simple 32-bit size/offset fields limit maximum operation sizes.

## Test Signals
GEM create/mmap/pwrite ioctl tests, invalid handle tests, out-of-bounds pwrite rejection, mmap offset mapping tests, and 32/64-bit userspace pointer compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/armada_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/asahi_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/asahi_drm.h

## Purpose
Defines the Asahi Apple GPU DRM UAPI for parameter discovery, GPU VM management, GEM allocation and binding, queue creation, sync objects, command submission, timestamps, render and compute command payloads.

## Important APIs, Types, And Functions
Exports ioctl IDs and `DRM_IOCTL_ASAHI_*`, global parameter struct, feature bits, VM create/destroy/bind, GEM create/mmap/bind-object, command types, priorities, queue create/destroy, sync item structs, submit command-buffer format, attachment hints, render flags, ZLS buffers, timestamp objects, helper/background/end-of-tile program descriptors, render/compute command structs, and GPU time query.

## Control Flow
The ABI defines an explicit userspace flow: query parameters, create VM with kernel VA reservation, create and bind GEM objects, optionally bind special timestamp objects, create a queue, submit a flat command buffer containing headers and typed payloads with barriers and sync arrays, then destroy queues/VMs.

## State, Persistence, And Dependencies
Persistent kernel state includes GPU VMs, GEM BOs, special bound objects, queues, sync dependencies, and submitted firmware jobs. Command payloads describe transient render/compute state and firmware-visible control register values. It depends on `drm.h`.

## Integration Points
Used by Asahi Mesa drivers, Asahi DRM kernel driver, DRM syncobj, GEM/dma-buf, firmware scheduling, and virtgpu-friendly command transport because submit buffers avoid CPU pointers.

## Risks
The header documents strict extensibility rules: 64-bit alignment, zeroed padding, append-only ioctl IDs, flag preservation, size-tagged indirect objects, and driver-version updates for new fields. Violating these breaks old userspace or old kernels. VM ranges, barriers, and command sizes need strong validation.

## Test Signals
UAPI struct size/offset tests, zero-padding rejection tests, old/new struct size compatibility, VM range validation, GEM bind/unbind tests, queue lifecycle, command-buffer parser tests, barrier ordering tests, syncobj timeline tests, render/compute conformance, and timestamp frequency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/asahi_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/drm.h

## Purpose
Defines the common Direct Rendering Manager UAPI foundation: base types, legacy DRM ioctls, GEM, PRIME dma-buf sharing, client and device capabilities, sync objects, CRTC sequence events, mode-setting ioctl numbers, command ranges, and event formats.

## Important APIs, Types, And Functions
Exports base DRM types, legacy map/lock/DMA/context/auth/AGP structs, `drm_version`, GEM close/flink/open/change-handle structs, capability constants, client capability constants, PRIME handle conversion, syncobj binary/timeline/eventfd structs, CRTC sequence structs, ioctl construction macros, generic `DRM_IOCTL_*` numbers, `DRM_COMMAND_BASE`/`END`, and event structs `drm_event`, `drm_event_vblank`, `drm_event_crtc_sequence`.

## Control Flow
No executable logic. The header encodes ioctl flows for version/capability negotiation, GEM handle lifetime, PRIME import/export, syncobj create/wait/signal/timeline operations, KMS mode ioctls imported from `drm_mode.h`, and event reads from DRM fds.

## State, Persistence, And Dependencies
Kernel state includes DRM file clients, master/auth state, GEM handles, dma-buf FDs, syncobjs and timeline points, KMS objects, vblank counters, leases, and queued events. It depends on Linux or BSD integer/ioctl headers and includes `drm_mode.h`.

## Integration Points
Included by nearly every DRM driver UAPI header, including amdgpu, amdxdna, armada, and asahi. Used by libdrm, Mesa, compositors, display servers, games, compute runtimes, PRIME/dma-buf sharing, and KMS tools.

## Risks
This is core ABI. Legacy structs contain native `long`, pointers, and historical layouts, so compat handling is fragile. GEM handles are not refcounted per handle and duplicate imports can return the same handle. Event reads must be complete-event aligned. Device-specific ioctls must stay inside `0x40..0x9f`.

## Test Signals
libdrm test suite, KMS/modetest coverage, GEM handle lifetime and duplicate-import tests, PRIME import/export tests, syncobj binary/timeline/eventfd tests, vblank and CRTC sequence event tests, 32-bit compat ioctl tests, and ABI size checks for every exported struct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm.h -->
