# subset-b-009341 research

This grouped report covers the requested strace source files. Each section is source-tree-aligned and bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_timespec.h -->
# sources/test-tools/strace/src/print_timespec.h

Purpose: Macro-templated implementation for printing kernel `timespec`-like structures in several generated variants. Including files define `TIMESPEC_T` and macros such as `PRINT_TIMESPEC`, `SPRINT_TIMESPEC`, `PRINT_TIMESPEC_UTIME_PAIR`, or `PRINT_ITIMERSPEC` before including this header.

Important APIs/types/functions: `TIMESPEC_TO_SEC_NSEC` normalizes signed nanoseconds with `zero_extend_signed_to_ull`; `print_timespec_t` emits `{tv_sec, tv_nsec}` or an alternate `TIMESPEC_NSEC` field; optional public wrappers include memory-size decoders, pointer decoders, string formatter, utime-pair printer, and itimerspec printer.

Control flow: all pointer printers fetch tracee memory through `umove_or_printaddr` or `umove`; unavailable or too-short inline buffers print `tprint_unavailable`. `SPRINT_TIMESPEC` returns `NULL`, an address, or decoded text depending on address, verbosity, syscall phase, and read success. Utime pair decoding recognizes `UTIME_NOW` and `UTIME_OMIT` and switches output style according to xlat verbosity.

State and persistence: only the string formatter uses a static buffer, so results are transient and overwritten by the next call. No persistent tracee state is modified.

Dependencies/integration: depends on `defs.h`-style print helpers, `xstring.h`, `sprinttime_nsec`, `print_local_array`, and MPERS/architecture wrappers that define the macro names. It is integrated by `print_timespec32.c` and `print_timespec64.c`.

Risks: as a macro-included implementation, symbol names and struct field aliases must be defined consistently by includers. The static string buffer is not reentrant. `void *` arithmetic in array decoding relies on compiler extensions used by strace. Correct handling of `UTIME_*` depends on kernel constants matching fallback definitions.

Test signals: compare decoded `utimensat`, `clock_gettime`, timer, and itimerspec outputs across abbrev/raw/verbose xlat modes; exercise failed `umove`, null address, short data-size buffers, and 32/64-bit personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_timespec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_timespec32.c -->
# sources/test-tools/strace/src/print_timespec32.c

Purpose: Builds the 32-bit `timespec` printer family by selecting `kernel_timespec32_t` and including `print_timespec.h`.

Important APIs/types/functions: defines `TIMESPEC_T`, `PRINT_TIMESPEC`, `SPRINT_TIMESPEC`, `PRINT_TIMESPEC_UTIME_PAIR`, and `PRINT_ITIMERSPEC` with `32` suffixes, producing `print_timespec32`, `sprint_timespec32`, `print_timespec32_utime_pair`, and `print_itimerspec32`.

Control flow: there is no independent runtime logic; all fetch, printing, utime special-case, and itimerspec behavior comes from `print_timespec.h`.

State and persistence: inherits only the header's formatter static buffer behavior.

Dependencies/integration: includes `defs.h`, `kernel_timespec.h`, sets `TIMESPEC_NSEC` to the 32-bit kernel field `tv_nsec`, and integrates with syscall decoders needing old/compat time ABI layouts.

Risks: ABI correctness depends on `kernel_timespec32_t` exactly matching tracee layout and on the include-time macro set not conflicting with other variants.

Test signals: 32-bit personality tests for `clock_*`, `ppoll_time32`, timer, and `utimensat_time32` style syscalls should show 32-bit seconds/nanoseconds and `UTIME_NOW/OMIT` rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_timespec32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_timespec64.c -->
# sources/test-tools/strace/src/print_timespec64.c

Purpose: Builds the 64-bit kernel `timespec` printer family from the shared macro template.

Important APIs/types/functions: defines `TIMESPEC_T` as `kernel_timespec64_t` and emits `print_timespec64`, `print_timespec64_data_size`, `print_timespec64_array_data_size`, `print_timespec64_utime_pair`, and `print_itimerspec64`.

Control flow: all behavior is supplied by `print_timespec.h`: size validation, tracee-memory fetches, array iteration, utime special cases, and nested itimerspec printing.

State and persistence: stateless except transient stack copies of tracee data.

Dependencies/integration: includes `kernel_timespec.h` and `print_timespec.h`; used by time64 syscall decoders and inline data decoders that pass explicit byte sizes.

Risks: the array data-size API must reject truncated arrays by checking `nmemb > size / sizeof(TIMESPEC_T)`. Any mismatch in kernel typedef layout would produce wrong field boundaries.

Test signals: time64 syscall tests should cover pointer and inline forms, short buffers, arrays, and failed reads.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_timespec64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_timeval.c -->
# sources/test-tools/strace/src/print_timeval.c

Purpose: MPERS-aware printer for `kernel_old_timeval_t` and related timeval arrays/interval structures, with Alpha-specific 32-bit timeval support.

Important APIs/types/functions: `print_timeval_t`, `print_struct_timeval`, `print_struct_timeval_data_size`, `print_timeval`, `print_timeval_utimes`, `sprint_timeval`, and `print_itimerval`; under `ALPHA`, `print_timeval32_t`, `print_timeval32`, `print_timeval32_utimes`, `print_itimerval32`, and `sprint_timeval32`.

Control flow: top-level pointer printers fetch tracee memory and print address on failure. Utime arrays are printed with `print_local_array` and append `sprinttime_usec` comments. String printers return `NULL`, an address, or decoded fields depending on verbosity and syscall error state.

State and persistence: string printers use static buffers; no persistent decoder state. All decoded structs are stack-local copies.

Dependencies/integration: uses `DEF_MPERS_TYPE`, `MPERS_DEFS`, `kernel_timeval.h`, `xstring.h`, print field macros, and time comment helpers. Integrated by resource/rusage, select, utimes, and interval timer decoders.

Risks: MPERS layout must match traced personality. The static string buffer is overwritten on subsequent calls. Alpha conditional code has separate ABI assumptions and needs coverage where available.

Test signals: `gettimeofday`, `select`, `utimes`, `setitimer/getitimer`, rusage, null/invalid pointer, and abbrev/non-verbose modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_timeval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_timeval64.c -->
# sources/test-tools/strace/src/print_timeval64.c

Purpose: Thin constructor for the 64-bit timeval printer variant.

Important APIs/types/functions: defines `timeval_t` as `kernel_timeval64_t` and includes `print_timeval.c` with `MPERS_IS_m32` so the generated names target the 64-bit layout while using the common implementation.

Control flow: delegates entirely to `print_timeval.c`.

State and persistence: inherits static string buffer behavior from the common file.

Dependencies/integration: relies on MPERS machinery, `kernel_timeval.h`, and syscall decoders that need `timeval64`-layout output.

Risks: include-based reuse can be confusing during maintenance; the `MPERS_IS_m32` define must correspond to the intended generated personality.

Test signals: time64 timeval syscalls and rusage consumers should decode 64-bit seconds/useconds without falling back to raw addresses.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_timeval64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_timex.c -->
# sources/test-tools/strace/src/print_timex.c

Purpose: Implements printing for kernel `timex`/`ntptimeval` adjustment data and wraps architecture-specific MPERS output.

Important APIs/types/functions: exposes `print_timex` through `MPERS_PRINTER_DECL`; uses helper declarations from `print_timex.h` and xlat tables for clock adjustment modes/status.

Control flow: tracee `timex` data is fetched from an address, printed as a large struct, and abbreviated when global abbrev mode asks for shorter output. Numeric fields such as modes and status are printed with symbolic xlat tables; time fields are printed using timeval/timespec helpers where appropriate.

State and persistence: no persistent state; all contents are read-only copies of tracee memory.

Dependencies/integration: depends on `kernel_timex.h`-style ABI definitions, MPERS, `print_timex.h`, xlat tables for `adjtimex` constants, and syscall decoders for `adjtimex`, `clock_adjtime`, or related calls.

Risks: `struct timex` has architecture and kernel-version layout differences; missing field guards can break portability. Abbreviated mode may hide tail fields, so tests must distinguish intentional truncation from decoding failure.

Test signals: `adjtimex`, `clock_adjtime`, valid/invalid pointers, abbrev/full modes, and personality variants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_timex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_timex.h -->
# sources/test-tools/strace/src/print_timex.h

Purpose: Declares the timex printer interfaces shared by syscall decoders and MPERS-generated implementations.

Important APIs/types/functions: declares `print_timex`-family entry points and related helper prototypes for printing `timex`-style structures.

Control flow: header only; compile-time integration controls which concrete implementation and personality-specific symbol is visible.

State and persistence: none.

Dependencies/integration: included by `print_timex.c` and syscall decoders using `adjtimex`/`clock_adjtime` output. Depends on `struct tcb` and `kernel_ulong_t` definitions from core strace headers.

Risks: prototype drift between this header and MPERS implementation will break builds across personality configurations.

Test signals: build all configured personalities and run time-adjustment syscall tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_utils.h -->
# sources/test-tools/strace/src/print_utils.h

Purpose: Shared declarations for low-level print helpers used throughout syscall and protocol decoders.

Important APIs/types/functions: groups utility printers for scalar arrays, xlat-backed values, strings, addresses, file descriptors, IDs, and reusable field formatting macros that other files call indirectly.

Control flow: header only; it exposes helper signatures and inline/macro glue so decoders can keep bodies table-driven and concise.

State and persistence: no runtime state in the header; functions it declares may consult global output mode, xlat verbosity, and tracee context.

Dependencies/integration: sits near the core `defs.h`/`print_fields.h` layer and is used by ioctl, netlink, ptrace, time, and resource decoders.

Risks: because it is widely included, incompatible changes propagate broadly. Helper semantics around quoting, verbosity, and unavailable data must stay stable for golden-output tests.

Test signals: broad strace test-suite diffs, especially xlat verbosity, array printing, and invalid pointer cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/printmode.c -->
# sources/test-tools/strace/src/printmode.c

Purpose: Prints file mode bitmasks in symbolic and numeric form.

Important APIs/types/functions: provides mode formatting helpers used by file-related syscall decoders. It maps file type and permission bits through xlat tables and preserves raw numeric output according to verbosity.

Control flow: accepts a mode value, emits file type bits, permissions, and special bits in the style selected by xlat verbosity. Unknown bits are preserved numerically.

State and persistence: stateless; depends only on current output verbosity.

Dependencies/integration: depends on `defs.h`, print flags helpers, and mode xlat tables. Integrated by `open`, `chmod`, `mkdir`, `mknod`, `stat`-style decoders, and anywhere `mode_t` is displayed.

Risks: file type bits overlap with permissions, so order and masks must be correct. Golden tests are sensitive to raw/abbrev/verbose formatting.

Test signals: chmod/open/mkdir tests with normal, special, file-type, unknown, raw, and verbose mode outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/printmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/printrusage.c -->
# sources/test-tools/strace/src/printrusage.c

Purpose: MPERS-aware printer for `struct rusage` returned by `getrusage` and related syscalls.

Important APIs/types/functions: `printrusage` prints user/system time and all resource counters; Alpha additionally defines `printrusage32` with `timeval32_t`.

Control flow: fetches a `kernel_rusage_t` from tracee memory. Always prints `ru_utime` and `ru_stime` through timeval printers; in abbrev mode emits `...` for the remaining counters, otherwise prints RSS, faults, swaps, block I/O, IPC, signals, and context-switch counts.

State and persistence: stateless stack-local decode.

Dependencies/integration: uses `kernel_rusage.h`, MPERS, `print_struct_timeval`, and Alpha timeval32 helpers. Called from `resource.c` getrusage decoders.

Risks: ABI layout differences by personality/Alpha can corrupt field interpretation. Abbrev behavior is intentional and should not be mistaken for incomplete decoding.

Test signals: `getrusage` and `wait4` style tests in full and abbrev modes, invalid pointer behavior, and Alpha personality build coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/printrusage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/printsiginfo.c -->
# sources/test-tools/strace/src/printsiginfo.c

Purpose: Decodes `siginfo_t` instances and arrays into signal-source, code, and signal-specific payload fields.

Important APIs/types/functions: `printsiginfo`, `printsiginfo_at`, and `print_siginfo_array`; helpers include `printsigsource`, `printsigval`, `print_si_code`, and `print_si_info`.

Control flow: prints `si_signo` and xlat-backed `si_code`, skips further details for `SI_NOINFO`, then branches on user-originated vs kernel-originated signals and by signal number. It decodes process/uid sources, timers, SIGIO band/fd, SIGCHLD status/times, fault addresses, SIGTRAP perf metadata, SIGSYS syscall/arch, and optional architecture fields guarded by feature macros.

State and persistence: stateless; all `siginfo_t` data is fetched from tracee memory or array iteration buffers.

Dependencies/integration: uses MPERS, `<signal.h>`, audit arch xlat, many signal code xlat tables, `printsignal`, fd/pid/id helpers, and ptrace/signal syscall decoders.

Risks: `siginfo_t` is union-heavy and libc/kernel fields vary by architecture and feature macros. Wrong `si_code` classification can print invalid union members. Signal-code xlat lookup must prefer generic codes but fall back to signal-specific tables.

Test signals: `rt_sigqueueinfo`, `waitid`, ptrace get/set siginfo, seccomp SIGSYS, SIGCHLD status, SIGSEGV/SIGBUS address cases, and xlat modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/printsiginfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/printsiginfo.h -->
# sources/test-tools/strace/src/printsiginfo.h

Purpose: Declares public siginfo printing entry points for decoders outside the MPERS implementation unit.

Important APIs/types/functions: prototypes for `printsiginfo`, `printsiginfo_at`, and `print_siginfo_array` or their MPERS-selected names.

Control flow: header-only; callers pass a `struct tcb`, tracee address, or array length and implementation handles memory fetching.

State and persistence: none.

Dependencies/integration: included by ptrace and signal syscall decoders. Depends on core strace types and MPERS symbol naming.

Risks: declarations must remain consistent with `printsiginfo.c`; missing MPERS guards can create duplicate or hidden symbols.

Test signals: build with MPERS enabled/disabled and run ptrace signal-info syscall tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/printsiginfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/process_vm.c -->
# sources/test-tools/strace/src/process_vm.c

Purpose: Decodes `process_vm_readv` and `process_vm_writev` syscall arguments.

Important APIs/types/functions: `SYS_FUNC(process_vm_readv)` and `SYS_FUNC(process_vm_writev)`.

Control flow: readv prints pid on entry, then on exit prints local iovecs as strings up to return value when successful or addresses on error, remote iovecs as addresses, counts, and flags. writev prints all arguments on entry and returns decoded.

State and persistence: no persistent state; relies on `tcp->u_rval` on read exit to bound local data rendering.

Dependencies/integration: uses `tprint_iov`, `tprint_iov_upto`, `iov_decode_str`, `iov_decode_addr`, and pid helpers.

Risks: successful read output depends on correct return-value clipping; decoding huge iovec counts must be bounded by common iovec helpers. Flags are currently numeric because the syscall defines no meaningful flags.

Test signals: read/write success and failure, partial reads, multiple iovecs, invalid iovec pointers, and nonzero flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/process_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ptp.c -->
# sources/test-tools/strace/src/ptp.c

Purpose: Decodes PTP clock ioctls and their nested time/capability/request structures.

Important APIs/types/functions: `ptp_ioctl`; helpers `print_ptp_clock_time`, array-member callbacks, and `PRINT_RSV` for nonzero reserved arrays.

Control flow: dispatches by ioctl code. Getter ioctls often print input fields on entry and output arrays on exit, skipping output on `syserror`. It decodes caps, external timestamp requests, periodic output requests, PPS enable, system offset sample arrays, pin function get/set, precise/extended offsets, and reserved fields for v2/cycles variants.

State and persistence: stateless; syscall phase determines whether to fetch input or output structures.

Dependencies/integration: `<linux/ptp_clock.h>`, ioctl size checks, xlat tables for flags/functions, `clocknames`, `sprinttime_nsec`, and ioctl dispatch from the generic ioctl decoder.

Risks: struct size assertions must track kernel headers. Output array lengths are bounded with `MIN(n_samples, PTP_MAX_SAMPLES)`. Some unions change meaning based on flags (`phase` vs `start`, `on` vs reserved), so flag handling is critical.

Test signals: PTP ioctl tests for all request variants, get/set phase differences, reserved nonzero fields, failed getters, and precise/extended sample output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ptrace.c -->
# sources/test-tools/strace/src/ptrace.c

Purpose: Main decoder for the `ptrace` syscall, including request-specific formatting and register/regset helpers.

Important APIs/types/functions: `SYS_FUNC(ptrace)`, `decode_ptrace_entering`, `decode_ptrace_exiting`, `decode_peeksiginfo_args`, `decode_seccomp_metadata`, `decode_getregset`, `decode_setregset`, and `print_user_offset_addr`.

Control flow: entry decoding prints request, pid, address, and data according to request semantics. Some requests complete on entry, while output-producing requests defer data printing to exit. Regset requests preserve original `iov_len` in `tcb` private storage and compare it with exit length. Exit decoding prints peek results, event messages, siginfo, sigmasks, seccomp filters/metadata, syscall info, and register blocks.

State and persistence: uses `set_tcb_priv_ulong`/`get_tcb_priv_ulong` to persist regset lengths across syscall entry/exit. Otherwise stateless.

Dependencies/integration: includes ptrace command xlat tables, compat ptrace tables, `printsiginfo`, `ptrace_syscall_info`, `regs.h`, iovec helpers, seccomp filter printers, and architecture register decoders.

Risks: ptrace has architecture-specific argument reversals (SPARC), compat request namespaces, and conditional request availability. Incorrect phase handling can print output before kernel writes it. Regset length mutation must be shown accurately.

Test signals: ptrace peek/poke, get/set siginfo, get/set sigmask, get/set regset, seccomp metadata/filter, syscall info, compat personality, SPARC/IA64 conditional builds, and xlat verbosity modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ptrace.h -->
# sources/test-tools/strace/src/ptrace.h

Purpose: Provides ptrace constants, compatibility definitions, and declarations needed by ptrace-related decoders.

Important APIs/types/functions: defines fallback `PTRACE_*` values and `struct_ptrace_syscall_info` compatibility shape where system headers lack it; exposes capability flags and printer/probe declarations used by `ptrace.c` and `ptrace_syscall_info.c`.

Control flow: compile-time only; preprocessor guards adapt to kernel/libc header support and architecture availability.

State and persistence: declares global support booleans for syscall-info APIs but does not mutate them itself.

Dependencies/integration: included by ptrace syscall decoder, syscall-info feature probe, and architecture code needing stable constants independent of host headers.

Risks: fallback constants must match Linux UAPI. Structure layout compatibility is high risk because printing and feature probes use `offsetof`/`offsetofend` for partial fetches.

Test signals: build against old and new kernel headers, run syscall-info and classic ptrace tests, and verify structure sizes in CI across architectures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ptrace_syscall_info.c -->
# sources/test-tools/strace/src/ptrace_syscall_info.c

Purpose: Detects kernel support for `PTRACE_GET_SYSCALL_INFO`/`PTRACE_SET_SYSCALL_INFO` and prints `struct ptrace_syscall_info` safely for partial kernel/user lengths.

Important APIs/types/functions: globals `ptrace_get_syscall_info_supported` and `ptrace_set_syscall_info_supported`; probes `test_ptrace_get_syscall_info`, `test_ptrace_set_syscall_info`; printer `print_ptrace_syscall_info`; helpers `print_psi_entry`, `print_psi_seccomp`, `print_psi_exit`.

Control flow: when `HAVE_FORK` is available, support tests fork a tracee, use `PTRACE_TRACEME`, `PTRACE_O_TRACESYSGOOD`, and syscall stops to verify NONE/ENTRY/EXIT semantics and, for SET, mutation of syscall numbers, args, and return values. Printing fetches `MIN(user_len, kernel_len, sizeof(info))`, then progressively prints only fields present in the fetched size and dispatches by `info.op`.

State and persistence: maintains global booleans caching feature support for the process. Test tracees and pipes are transient and killed/closed in cleanup paths.

Dependencies/integration: uses ptrace, wait, fork, signal, syscall number definitions, audit arch xlat, `kill_save_errno`, `scno.h`, and `ptrace_syscall_info_op`. Called by startup feature checks and `ptrace.c`.

Risks: probes execute real tracee syscalls and are architecture-sensitive; NOMMU leaves defaults unchanged. Partial-structure printing must avoid reading absent fields. s390 masks syscall numbers to 16 bits. SET probes deliberately rewrite tracee execution, so cleanup paths must reliably kill/wait tracees.

Test signals: startup debug messages, kernels with/without GET/SET support, partial user lengths, seccomp op printing, entry/exit error return rendering, and fork-disabled configurations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ptrace_syscall_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ptrace_syscall_info.h -->
# sources/test-tools/strace/src/ptrace_syscall_info.h

Purpose: Declares ptrace syscall-info feature flags, probes, and printer for use by core ptrace decoding.

Important APIs/types/functions: extern booleans for GET/SET support, `test_ptrace_get_syscall_info`, `test_ptrace_set_syscall_info`, and `print_ptrace_syscall_info`.

Control flow: header-only declarations; implementation handles probing and partial printing.

State and persistence: declares state owned by `ptrace_syscall_info.c`.

Dependencies/integration: included by `ptrace.c` and startup/initialization logic that decides whether to use new ptrace APIs.

Risks: prototypes must match implementation and availability guards in `ptrace.h`; wrong linkage would break optional feature detection.

Test signals: successful full build with and without syscall-info UAPI support and ptrace syscall-info decoder tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ptrace_syscall_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/quota.c -->
# sources/test-tools/strace/src/quota.c

Purpose: Decodes `quotactl` and `quotactl_fd` command arguments and quota data structures, including classic and XFS quota interfaces.

Important APIs/types/functions: `SYS_FUNC(quotactl)`, `SYS_FUNC(quotactl_fd)`, `decode_cmd_data`, `print_qcmd`, and struct definitions `if_dqblk`, `if_nextdqblk`, `if_dqinfo`.

Control flow: command words are split into command and quota type. Entry prints operation and special path/fd; `decode_cmd_data` dispatches by quota subcommand and phase, delaying output-only structures until exit. It decodes quota on paths, quota records, next quota records, XFS disk quota, format, info, quota stat/statv, quota flags, and default raw id/address cases.

State and persistence: stateless; uses syscall phase and return status only.

Dependencies/integration: `<linux/dqblk_xfs.h>`, xlat tables for quota commands/types/formats/flags, fetch helpers including `fetch_struct_quotastat`, UID/path/fd printers.

Risks: structures have alignment/padding hazards, noted by packed `if_dqblk` for 32-bit tracees. Abbrev mode intentionally elides long tails. Low 32-bit masking is required on sign-extending architectures such as s390x.

Test signals: classic and XFS quota commands, get vs set phase behavior, fd variant, packed layout on 32-bit personality, abbrev/full output, and unknown command fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/random_ioctl.c -->
# sources/test-tools/strace/src/random_ioctl.c

Purpose: Decodes random-device ioctls such as entropy count and entropy injection.

Important APIs/types/functions: `random_ioctl` and `struct rand_pool_info` handling.

Control flow: `RNDGETENTCNT` prints output integer on exit; `RNDADDTOENTCNT` prints input integer; `RNDADDENTROPY` fetches `rand_pool_info`, prints entropy count and buffer size, then prints the variable buffer pointer/data according to common string/hex helpers; unhandled commands return generic decoded status.

State and persistence: stateless; does not modify traced data.

Dependencies/integration: `<linux/random.h>`, random ioctl xlat, `printnum_int`, `umove_or_printaddr`, and generic ioctl dispatcher.

Risks: variable-length entropy buffer must be bounded by the struct field and tracee memory availability. `RNDGETPOOL` historical behavior is noted but not deeply decoded.

Test signals: ioctl tests for entropy count get/add, entropy add with short/invalid pointers, and unknown random ioctls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/random_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/readahead.c -->
# sources/test-tools/strace/src/readahead.c

Purpose: Decodes the `readahead` syscall.

Important APIs/types/functions: `SYS_FUNC(readahead)`.

Control flow: prints fd, offset, and count in syscall argument order, with fd formatting and numeric offset/count output, then returns decoded.

State and persistence: stateless.

Dependencies/integration: core syscall argument helpers and fd printer.

Risks: offset type width must match kernel argument packing on all personalities.

Test signals: `readahead(fd, offset, count)` golden output with large offsets and invalid fd cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/readahead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/readlink.c -->
# sources/test-tools/strace/src/readlink.c

Purpose: Decodes `readlink`, `readlinkat`, and variants that return path text into a user buffer.

Important APIs/types/functions: syscall decoder functions for readlink-like syscalls.

Control flow: prints input path arguments on entry. On exit, if successful, prints the output buffer as a string limited by return value and buffer size; on error it prints the buffer address. `readlinkat` also prints directory fd.

State and persistence: stateless; output rendering depends on `tcp->u_rval`.

Dependencies/integration: path printers, fd printers, string-buffer output helpers, and syscall phase/error helpers.

Risks: return value is not NUL-terminated path length, so the decoder must not over-read. Empty successful links and truncated outputs need distinct rendering from errors.

Test signals: readlink/readlinkat success, ENOENT, small buffer truncation, empty target, and invalid output pointer.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/readlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/reboot.c -->
# sources/test-tools/strace/src/reboot.c

Purpose: Decodes Linux `reboot` syscall magic constants and command values.

Important APIs/types/functions: `SYS_FUNC(reboot)`.

Control flow: prints magic1, magic2, command, and optional argument pointer/string according to command semantics, using xlat tables for known magic and reboot commands.

State and persistence: stateless.

Dependencies/integration: reboot xlat tables and standard syscall argument printers.

Risks: command-specific argument meaning is limited; unknown commands should retain raw values. Magic constants are part of user-visible output and golden tests are sensitive to xlat style.

Test signals: common reboot commands, unknown command values, raw/verbose xlat modes, and pointer argument cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/regs.h -->
# sources/test-tools/strace/src/regs.h

Purpose: Declares architecture register-set decoding entry points used by ptrace and related code.

Important APIs/types/functions: prototypes such as `decode_pt_regs`, `decode_pt_fpregs`, and regset decoders for `NT_PRSTATUS`/`NT_FPREGSET`.

Control flow: header-only; architecture-specific `.c` files provide concrete decoders.

State and persistence: none.

Dependencies/integration: included by `ptrace.c` and regset code; depends on `struct tcb` and address/length types.

Risks: architecture conditional availability must match build configuration. Prototype drift breaks ptrace register decoding.

Test signals: ptrace get/set regs and get/set regset tests on supported architectures plus compile-only coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/regset.c -->
# sources/test-tools/strace/src/regset.c

Purpose: Provides generic wrappers for decoding ELF note regsets, delegating to architecture register printers.

Important APIs/types/functions: functions for `decode_prstatus_regset` and `decode_fpregset`-style entry points.

Control flow: accepts tracee address and length, validates/fetches expected register-set layouts where possible, and prints raw address or unavailable output when decoding is not supported.

State and persistence: stateless.

Dependencies/integration: `regs.h`, architecture-specific register definitions, ptrace regset decoder in `ptrace.c`, and iovec length handling.

Risks: regset layouts are architecture-specific and variable-length; overly strict size checks can hide valid partial data, while loose checks can misdecode.

Test signals: `PTRACE_GETREGSET` for `NT_PRSTATUS` and `NT_FPREGSET`, invalid iovec base, changed iovec length, and unsupported note types.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/renameat.c -->
# sources/test-tools/strace/src/renameat.c

Purpose: Decodes `renameat` and `renameat2` syscall arguments.

Important APIs/types/functions: syscall decoder functions for rename-at variants and flag xlat handling for `renameat2`.

Control flow: prints old directory fd/path and new directory fd/path; `renameat2` additionally prints flags symbolically. Returns decoded on entry because outputs are not produced.

State and persistence: stateless.

Dependencies/integration: fd/path printers and rename flag xlat tables.

Risks: `AT_FDCWD` and path pointer failures must render consistently with other *at syscalls. Unknown flags should be preserved.

Test signals: renameat/renameat2 with `AT_FDCWD`, relative paths, invalid paths, `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, unknown flags, and xlat modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/renameat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/resource.c -->
# sources/test-tools/strace/src/resource.c

Purpose: Decodes resource-limit, rusage, and priority syscalls.

Important APIs/types/functions: `getrlimit`, `setrlimit`, `prlimit64`, `getrusage`, Alpha `osf_getrusage`, `getpriority`, `setpriority`; helpers `print_rlim64_t`, `print_rlim32_t`, `decode_rlimit`, and `priority_print_who`.

Control flow: limit syscalls print resource on entry and output structures on exit for getters. `decode_rlimit` chooses 32-bit vs 64-bit layout by kernel long size/personality. `prlimit64` prints new limit on entry and old limit on exit. Priority syscalls print `who` as pid/process group depending on `which`.

State and persistence: stateless; output phase decides old-limit/rusage fetches.

Dependencies/integration: `<sys/resource.h>`, resources/usagewho/priorities xlat, rusage printer, pid helpers, and xlat verbosity for infinity and `*1024` formatting.

Risks: rlim_t width differs on i386/x32/64-bit. Static buffers in rlim helper are transient. Alpha has separate rusage ABI. Return-value decoding for `getpriority` is handled elsewhere, so argument decoder must not confuse negative priorities with errors.

Test signals: get/set/prlimit64 on 32- and 64-bit personalities, infinity values, multiples of 1024, getrusage abbrev/full, priority process/pgrp/user cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/retval.c -->
# sources/test-tools/strace/src/retval.c

Purpose: Centralizes syscall return-value formatting helpers.

Important APIs/types/functions: return-value printing functions declared in `retval.h`, including numeric, hex, fd, address, decoded/verbose style helpers, and error-aware formatting paths.

Control flow: chooses output representation based on decoder return flags, syscall error state, and global formatting settings. It prints raw return values, symbolic auxiliary text, and error names/comments consistently for all syscall decoders.

State and persistence: consults `struct tcb` syscall result fields and global output options; does not own persistent state.

Dependencies/integration: core syscall dispatch, errno/xlat helpers, fd/path caches where applicable, and all `SYS_FUNC` return flag conventions.

Risks: any change affects every syscall line. Signedness, hex formatting, and error-vs-valid-negative handling are high-risk for regressions.

Test signals: broad syscall golden tests, especially negative valid returns, `RVAL_HEX`, `RVAL_FD`, `RVAL_DECODED`, injected errors, and raw mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/retval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/retval.h -->
# sources/test-tools/strace/src/retval.h

Purpose: Declares return-value formatting APIs and flag conventions shared between syscall decoders and the syscall dispatch layer.

Important APIs/types/functions: prototypes and flag definitions for return-value handling.

Control flow: header-only; decoders communicate desired result style by returning flags declared here.

State and persistence: none.

Dependencies/integration: included widely by core decoding code and syscall implementations through `defs.h`.

Risks: flag value changes would break decoder semantics globally.

Test signals: full strace test suite build and output comparison for all return-value styles.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/retval.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/riscv.c -->
# sources/test-tools/strace/src/riscv.c

Purpose: RISC-V architecture-specific syscall/register support.

Important APIs/types/functions: architecture hooks for syscall number, argument, or return-value extraction and register printing as required by the strace core.

Control flow: reads RISC-V tracee register state through architecture-specific ptrace APIs and maps registers into strace's generic `tcp->u_arg`/syscall number fields.

State and persistence: updates per-tracee syscall context, not durable global state.

Dependencies/integration: core arch hooks, ptrace register definitions, and syscall dispatch.

Risks: ABI differences for 32/64-bit RISC-V and syscall restart/error conventions can cause wrong arguments or return values.

Test signals: RISC-V architecture CI or cross tests for syscall argument decoding, restart handling, and ptrace register fetch failures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rseq.c -->
# sources/test-tools/strace/src/rseq.c

Purpose: Decodes the `rseq` syscall and `struct rseq` registration fields.

Important APIs/types/functions: `SYS_FUNC(rseq)` plus helpers for CPU-id, flags, signature, and structure-size rendering.

Control flow: prints the user rseq pointer, length, flags, and signature; when appropriate it fetches and decodes the pointed structure with field-level output.

State and persistence: stateless with respect to strace; kernel registration state belongs to the tracee.

Dependencies/integration: Linux rseq UAPI definitions, xlat tables for rseq flags, and tracee memory fetch helpers.

Risks: rseq is ABI-size-sensitive; future struct extensions and user-specified length must be handled without over-reading. Signature is architecture-specific.

Test signals: `rseq` register/unregister calls, different lengths, invalid pointers, unknown flags, and raw/verbose xlat modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rt_sigframe.c -->
# sources/test-tools/strace/src/rt_sigframe.c

Purpose: Architecture hook for decoding real-time signal frames when a traced task is in signal-return context.

Important APIs/types/functions: signal-frame decoder entry points used by `rt_sigreturn.c`.

Control flow: fetches architecture-specific frame data from the tracee stack/register state and prints or makes available saved signal context fields.

State and persistence: reads per-tracee register/stack state; no global persistence.

Dependencies/integration: architecture signal frame layouts, `rt_sigreturn` decoder, ptrace register access, and sigset/siginfo printers.

Risks: signal-frame layout is highly architecture and libc/kernel dependent; invalid stack pointers must fail gracefully.

Test signals: rt_sigreturn tests on supported architectures, invalid/restored stack frames, and signal mask/context output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rt_sigreturn.c -->
# sources/test-tools/strace/src/rt_sigreturn.c

Purpose: Decodes `rt_sigreturn` syscall context, usually by delegating to signal-frame helpers.

Important APIs/types/functions: `SYS_FUNC(rt_sigreturn)` and architecture-specific frame decode integration.

Control flow: on syscall entry/exit, obtains the tracee's signal frame context and prints restored signal mask/context where implemented; return-value handling is special because sigreturn restores user context rather than returning normally.

State and persistence: uses per-tracee register/stack state only.

Dependencies/integration: `rt_sigframe.c`, signal mask printers, architecture register hooks, and core syscall restart/return handling.

Risks: wrong frame interpretation can confuse syscall state around signal returns. Some architectures may intentionally print minimal output.

Test signals: signal delivery/return integration tests, interrupted syscalls, invalid frame pointers, and architecture build coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rt_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtc.c -->
# sources/test-tools/strace/src/rtc.c

Purpose: Decodes RTC ioctls and nested time/alarm/PLL/parameter structures.

Important APIs/types/functions: `rtc_ioctl`; helpers for `rtc_time`, `rtc_wkalrm`, `rtc_pll_info`, voltage-low flags, and RTC parameter get/set.

Control flow: dispatches by ioctl code. Pure enable/disable commands have no argument; read commands print output on exit; set commands print input on entry. Alarm, PLL, and param commands decode structs, with `RTC_PARAM_GET` showing value changes between entry and exit.

State and persistence: stateless; phase-sensitive output only.

Dependencies/integration: Linux RTC UAPI, ioctl xlat tables, time struct printers, flag/value xlat tables, and generic ioctl dispatcher.

Risks: ioctl structure layouts and param IDs evolve. GET commands must avoid printing output before success; SET commands must not rely on exit memory.

Test signals: RTC time read/set, alarm read/set, IRQ/epoch read, PLL get/set, voltage low read/clear, param get/set, invalid pointers, and no-arg commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_addr.c -->
# sources/test-tools/strace/src/rtnl_addr.c

Purpose: Decodes route-netlink address messages (`ifaddrmsg`) and their attributes.

Important APIs/types/functions: `decode_ifaddrmsg`, `decode_ifa_address`, `decode_ifa_cacheinfo`, `decode_ifa_flags`, and `ifaddrmsg_nla_decoders`.

Control flow: prints fixed `ifaddrmsg` fields after fetching all but the already-known family byte. If the fixed header is complete, it decodes aligned `IFA_*` attributes, using the message family to decode address payloads.

State and persistence: stateless; passes the decoded header as opaque context for address attribute decoding.

Dependencies/integration: `netlink_route.h`, `nlattr.h`, Linux `if_addr.h`, xlat tables for flags/scopes/attrs, and inet address decoders.

Risks: short messages must show more-data rather than reading past bounds. Address attributes depend on `ifa_family`; bad family values should still preserve raw output.

Test signals: IPv4/IPv6 address add/delete/get messages, cacheinfo, flags attr, target netns id, short headers, and malformed attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_addrlabel.c -->
# sources/test-tools/strace/src/rtnl_addrlabel.c

Purpose: Decodes route-netlink address-label messages.

Important APIs/types/functions: `decode_ifaddrlblmsg`, `decode_ifal_address`, and `ifaddrlblmsg_nla_decoders`.

Control flow: decodes the fixed `ifaddrlblmsg` header, then aligned `IFAL_*` attributes. Address payloads use `ifal_family` from the header.

State and persistence: stateless.

Dependencies/integration: Linux `if_addrlabel.h`, netlink route/nlattr helpers, addrfam xlat, and rtnl address-label attrs.

Risks: only complete headers enable attribute decode; short messages must not over-read. Attribute table is small, so unknown attrs fall to generic parser.

Test signals: IPv6 addrlabel list/add/delete messages, label attr, malformed short payloads.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_addrlabel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_cachereport.c -->
# sources/test-tools/strace/src/rtnl_cachereport.c

Purpose: Decodes multicast routing cache-report netlink messages for IPv4 and IPv6.

Important APIs/types/functions: decoders for `IPMRA_CREPORT_*` and `IP6MRA_CREPORT_*` attributes, message type xlat helpers, and route decoder entry points.

Control flow: chooses attribute tables by address family/message type and decodes message type, VIF id, source/destination addresses, raw packet payload placeholders, and routing table IDs.

State and persistence: stateless.

Dependencies/integration: Linux mroute/mroute6/rtnetlink headers, netlink attribute helpers, xlat tables for IPMRA/IP6MRA message types and attrs.

Risks: raw packet data is intentionally not decoded; malformed lengths must fall back safely. Family selection determines whether in_addr or in6_addr decoders are used.

Test signals: IPv4 and IPv6 cache report messages with source/destination attrs, table attr, packet payload, and unknown attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_cachereport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_dcb.c -->
# sources/test-tools/strace/src/rtnl_dcb.c

Purpose: Decodes DCB route-netlink messages.

Important APIs/types/functions: route decoder for DCB family messages and DCB attribute decoder table.

Control flow: prints the fixed DCB message fields, then delegates aligned DCB attributes to `decode_nlattr` using DCB xlat names and simple scalar/string decoders where known.

State and persistence: stateless.

Dependencies/integration: DCB Linux UAPI headers, route-netlink dispatcher, and nlattr helpers.

Risks: DCB has many nested/vendor-specific attributes that may remain generic. Short headers and unknown attrs must remain robust.

Test signals: DCB get/set messages with known attrs, nested unknown payload, and malformed lengths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_link.c -->
# sources/test-tools/strace/src/rtnl_link.c

Purpose: Large route-netlink decoder for link messages (`ifinfomsg`) and many nested `IFLA_*` attribute families.

Important APIs/types/functions: `decode_ifinfomsg`; decoders for hardware addresses, 32/64-bit link stats, bridge IDs/options, inet/inet6 config/stats, linkinfo kind/data/xstats, VF info, XDP, AF_SPEC, bridge VLAN/tunnel info, property lists, and proto-down reasons.

Control flow: fixed header decoding prints family, hardware type, ifindex, flags, and change mask, then decodes aligned attributes. Many nested decoders are table-driven. `IFLA_LINKINFO` stores `kind` and `slave_kind` strings in a context so later DATA/XSTATS attributes can dispatch to bridge/tun/can-specific decoders. `IFLA_AF_SPEC` has a special AF_BRIDGE path because bridge payloads do not follow the generic address-family nesting shape.

State and persistence: per-message local context only (`ifla_linkinfo_ctx`); no global state. Several decoders pass the fixed `ifinfomsg` as opaque context for family-aware hardware/AF decoding.

Dependencies/integration: broad Linux networking UAPI (`if_link.h`, `if_bridge.h`, rtnetlink), netlink/nlattr framework, xlat tables for link attrs, bridge, VF, XDP, SNMP stats, device config indices, hardware/address-family names, and generic stat decoders exported to other files.

Risks: high churn with kernel UAPI additions. Variable struct sizes are handled for stats and ifmap; VF GUID alignment is explicitly worked around with packed/aligned union cases. Linkinfo DATA ordering depends on KIND being decoded before DATA in the same nested stream; missing or long kind strings fall back to generic parsing. Several attrs are marked unimplemented or default parser.

Test signals: link get/set/new/del messages with stats32/64, bridge AF_SPEC, inet/inet6 config/stats, XDP, VF info, prop list alt names, bridge/tun linkinfo, CAN xstats, short headers, variable stat sizes, and malformed nested attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_mdb.c -->
# sources/test-tools/strace/src/rtnl_mdb.c

Purpose: Decodes bridge multicast database route-netlink messages.

Important APIs/types/functions: `decode_br_port_msg`, `decode_mdba_mdb_entry_info`, `decode_mdba_router_port`, and nested MDB/router decoder tables.

Control flow: fixed `br_port_msg` prints family and ifindex, then `MDBA_*` attrs. MDB entries decode `br_mdb_entry`, flags/state/vid, protocol/address union, and optional extended attrs. Router ports decode ifindex and optional timer/type nested attrs.

State and persistence: stateless.

Dependencies/integration: Linux bridge UAPI, netlink helpers, xlat tables for MDB attrs, states, flags, multicast router types, and address-family printers.

Risks: comment notes ABI ambiguity/breakage around flags/vid presence on some architectures. Address decoding depends on embedded protocol. Nested payloads can contain aligned data after fixed structs.

Test signals: MDB entries for IPv4/IPv6, router port attrs, timers, flags/vid fields, short payloads, and malformed nested attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_mdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_neigh.c -->
# sources/test-tools/strace/src/rtnl_neigh.c

Purpose: Decodes neighbor table route-netlink messages (`ndmsg`) and neighbor attributes.

Important APIs/types/functions: `decode_ndmsg`, neighbor address/cacheinfo decoders, and attr tables for `NDA_*` plus FDB extended attrs.

Control flow: prints fixed neighbor header fields including family, ifindex, state, flags, and type, then decodes attrs. Address decoding uses `ndm_family`; cacheinfo and probes/config attrs decode fixed structs/scalars.

State and persistence: stateless with fixed header passed as opaque context.

Dependencies/integration: Linux `neighbour.h`, netlink/nlattr helpers, neighbor state/flag/type xlat tables, FDB notify/extended flag xlat.

Risks: neighbor attrs vary by address family and bridge/FDB context. Unknown or short attrs must be rejected to generic output without corrupting array formatting.

Test signals: IPv4/IPv6 neighbor entries, bridge FDB entries, cacheinfo, protocol/vlan attrs, extended flags, malformed attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_neigh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_neightbl.c -->
# sources/test-tools/strace/src/rtnl_neightbl.c

Purpose: Decodes neighbor table configuration/statistics route-netlink messages (`ndtmsg`).

Important APIs/types/functions: `decode_ndtmsg`, `decode_ndta_parms`, `decode_ndt_config`, `decode_ndt_stats`, and `ndt_parms_nla_decoders`.

Control flow: prints family, then decodes `NDTA_*` attrs. Parameters and stats are nested/fixed structures with many timing/count fields; stats accept either minimum or full struct size.

State and persistence: stateless.

Dependencies/integration: Linux neighbor table UAPI, xlat tables for `NDTA_*`/`NDTPA_*`, nlattr helpers.

Risks: variable stats size needs exact min/full handling. Timer units are printed as raw u64 by current decoders, so semantic conversions depend on shared helpers where used.

Test signals: neighbor table dump with config, parms, stats min/full lengths, GC interval, and malformed short stats.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_neightbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_netconf.c -->
# sources/test-tools/strace/src/rtnl_netconf.c

Purpose: Decodes network configuration route-netlink messages.

Important APIs/types/functions: `decode_netconfmsg` and `netconfmsg_nla_decoders`.

Control flow: prints family then decodes aligned `NETCONFA_*` attributes as ifindex or signed 32-bit config values.

State and persistence: stateless.

Dependencies/integration: Linux `netconf.h`, route-netlink dispatcher, nlattr helpers, netconf attr xlat.

Risks: table must track new kernel attrs; all current scalar attrs are signed, so type mismatches would affect output.

Test signals: IPv4/IPv6 netconf dumps with forwarding/rp_filter/proxy/input attrs and short headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_netconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_nh.c -->
# sources/test-tools/strace/src/rtnl_nh.c

Purpose: Decodes nexthop route-netlink messages and resilient group/bucket attrs.

Important APIs/types/functions: `decode_nhmsg`, `decode_nha_nh_grp`, `decode_nha_addr`, resilient group/bucket decoders, and `print_nh_grp`.

Control flow: fixed `nhmsg` prints family/scope/protocol/flags, then attrs. Group attrs are arrays of `struct nexthop_grp`; gateway/address attrs use `nh_family`; resilient attrs decode nested groups and buckets with clock/scalar fields.

State and persistence: stateless; fixed header is passed as opaque context for family-aware address decoding.

Dependencies/integration: Linux nexthop/rtnetlink UAPI, nlattr helpers, xlat tables for nexthop attrs and group types, route scope/protocol flags.

Risks: group arrays require exact element-size division; resilient attr support depends on newer kernel headers. Unknown nested attrs must remain generic.

Test signals: single nexthop, group nexthop, resilient groups/buckets, IPv4/IPv6 gateways, malformed group payload lengths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_nh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_nsid.c -->
# sources/test-tools/strace/src/rtnl_nsid.c

Purpose: Decodes network namespace ID route-netlink messages.

Important APIs/types/functions: nsid route decoder and attr table for namespace id/fd/target ids.

Control flow: prints family or minimal fixed message context, then delegates attrs to scalar/fd decoders.

State and persistence: stateless.

Dependencies/integration: netlink route dispatcher, Linux rtnetlink namespace attrs, fd and s32 decoders.

Risks: small file with mostly table-driven behavior; future attrs need table updates.

Test signals: RTM_GETNSID/NEWNSID messages with fd, nsid, target nsid, and malformed attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_nsid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_route.c -->
# sources/test-tools/strace/src/rtnl_route.c

Purpose: Decodes route messages (`rtmsg`) and route attributes, including metrics and multipath nexthops.

Important APIs/types/functions: `decode_rtmsg`, `decode_route_addr`, `decode_rta_metrics`, `decode_rta_multipath`, `decode_rtvia`, and xlat-backed `rt_class`, `rt_proto`, `lwt_encap_type` decoders.

Control flow: prints fixed route header fields, then `RTA_*` attrs. Multipath payloads are iterated as aligned `struct rtnexthop` records with nested route attrs after each header. Address attrs use `rtm_family`, and `RTA_VIA` carries its own family.

State and persistence: stateless; fixed `rtmsg` context is passed to attrs.

Dependencies/integration: Linux routing UAPI, nlattr helpers, xlat tables for route attrs/metrics/protocols/scopes/types/flags/tables, inet address decoders.

Risks: `rtnh_len` controls nested iteration and must be bounded by remaining payload. Multipath arrays and nested attrs have complex bracket formatting. Some attrs such as `RTA_ENCAP` are unimplemented.

Test signals: IPv4/IPv6 route add/del/get, metrics, multipath with multiple nexthops, via/newdst, lwt encap type, malformed `rtnh_len`, and unknown attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_rule.c -->
# sources/test-tools/strace/src/rtnl_rule.c

Purpose: Decodes FIB rule route-netlink messages and attributes.

Important APIs/types/functions: `decode_fib_rule_hdr`, `decode_rule_addr`, `decode_fib_rule_uid_range`, `decode_rule_port_range`, and rule attr decoder table.

Control flow: fixed header prints family, dst/src lengths, tos, table, action, and flags, then attrs. Address attrs use header family; UID and port ranges decode fixed start/end structs.

State and persistence: stateless.

Dependencies/integration: Linux `fib_rules.h`, netlink/nlattr helpers, xlat tables for rule attrs/actions/flags, routing table IDs.

Risks: field names and action/table semantics overlap with route headers but use distinct xlat tables. Short range attrs must be rejected safely.

Test signals: IPv4/IPv6 rule messages with src/dst, fwmark, table, uid range, sport/dport ranges, action/flags, malformed attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_rule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_stats.c -->
# sources/test-tools/strace/src/rtnl_stats.c

Purpose: Decodes route-netlink interface statistics messages and nested xstats/offload/AF-specific stats.

Important APIs/types/functions: `decode_ifstatsmsg`, bridge VLAN/mcast/STP xstats decoders, bond 802.3ad stats decoders, offload stats, MPLS link stats, and `ifstatsmsg_nla_decoders`.

Control flow: fixed `if_stats_msg` prints family, optional padding if nonzero, ifindex, and filter mask. Attributes dispatch to link stats64, bridge/bond xstats, offload stats, or AF_SPEC; nested bridge/bond/MPLS tables decode fixed structs and append hex tail data when payload is larger than known struct.

State and persistence: stateless.

Dependencies/integration: Linux bonding/bridge/MPLS/rtnetlink headers, nlattr helpers, shared `decode_nla_rtnl_link_stats64` from link decoder, and many stats xlat tables.

Risks: stats structs can grow; code preserves tail bytes for several fixed structs. Array-indexed multicast stats depend on index xlat table alignment.

Test signals: RTM_GETSTATS with link64, bridge VLAN/mcast/STP xstats, bond 3ad, offload CPU hit, MPLS stats, nonzero padding, and extended payload tails.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_tc.c -->
# sources/test-tools/strace/src/rtnl_tc.c

Purpose: Decodes traffic-control route-netlink messages (`tcmsg`) and common qdisc/class/filter stats attributes.

Important APIs/types/functions: `decode_tcmsg`, exported `decode_nla_tc_stats`, `decode_tc_stats`, `decode_tc_estimator`, `decode_gnet_stats_*`, and `decode_tca_stab`.

Control flow: fixed `tcmsg` prints family, ifindex, handle, parent, and info, then attributes. `TCA_STATS` decodes old `tc_stats`; `TCA_STATS2` decodes nested gnet stats; `TCA_STAB` decodes size spec and uint16 table arrays.

State and persistence: stateless.

Dependencies/integration: Linux `gen_stats.h`, `pkt_sched.h`, rtnetlink, nlattr helpers, xlat tables for TC attrs/stats/stab. `rtnl_tc_action.c` reuses the `decode_nla_tc_stats` exported decoder.

Risks: many `TCA_OPTIONS`/`TCA_XSTATS` payloads are subsystem-specific and intentionally unimplemented here. Length validation for old stats uses `offsetofend` for portable minimums.

Test signals: qdisc/class/filter netlink messages with kind, old stats, stats2 basic/rate/queue/rate64, stab data, chain/block attrs, malformed short stats.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_tc_action.c -->
# sources/test-tools/strace/src/rtnl_tc_action.c

Purpose: Decodes traffic-control action route-netlink messages and root/action nested attributes.

Important APIs/types/functions: action attr decoders `decode_tca_action`, `decode_tca_root_act_tab`, `decode_tca_act_flags`, `decode_tca_act_hw_stats`, `decode_tca_msecs`, and root attr tables.

Control flow: root action tables misuse nesting as an array, so the decoder invokes `decode_nlattr` with a single action decoder and no xlat table. Each action decodes kind, index, stats, cookie/default payload, flags, hardware stats, and in-hardware count. Root attrs decode flags and optional time intervals as milliseconds.

State and persistence: stateless.

Dependencies/integration: Linux `pkt_cls.h`/rtnetlink, `rtnl_tc.c` stats decoder, xlat tables for action attrs/root flags/hw stats, and nlattr framework.

Risks: `TCA_ACT_OPTIONS` is action-specific and unimplemented here. Root table's nonstandard nesting requires careful generic decoder setup. Millisecond values can be shorter than u64 and are widened by helper.

Test signals: TC action dump/new/del messages with multiple actions, stats, flags, hardware stats, cookie payloads, root flags, msecs attrs, and malformed nested arrays.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/rtnl_tc_action.c -->
