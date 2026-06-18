# subset-b-009343 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/strace.c -->
# sources/test-tools/strace/src/strace.c

Purpose: main `strace` executable driver. It parses command-line options, starts or attaches tracees, manages `struct tcb` lifetime, runs the ptrace wait/restart event loop, owns shared/per-PID output streams, and terminates with cleanup, summaries, and optional tips.

Important APIs/types/functions: global flags such as `cflag`, `followfork`, `output_separately`, `ptrace_setoptions`, timestamp flags, `outfname`, `shared_log`, `printing_tcp`, `current_tcp`, `tcbtab`, and `tcb_wait_tab` are the process-wide tracing state. Core functions include `init`, `startup_child`, `startup_attach`, `attach_tcb`, `after_successful_attach`, `alloctcb`, `droptcb`, `printleader`, `next_event`, `dispatch_event`, `trace_syscall`, `cleanup`, and `terminate`. `struct tcb_wait_data` carries a `trace_event`, wait status, ptrace event message, and signal info between wait collection and dispatch.

Control flow: `main` localizes, calls `init`, then loops over `dispatch_event(next_event())`. Initialization sets defaults, parses short/long options, configures qualifiers, ptrace options, output files, signal handling, seccomp, stack tracing, user credentials, path filters, and starts a command or attaches requested PIDs. `next_event` batches `wait4(__WALL)` results into per-TCB wait records, classifies them as syscall, signal, exit, exec, seccomp, group-stop, or restart events, and queues multiple events safely. `dispatch_event` decodes syscalls through `syscall.c`, prints signal/exit/exec messages, handles seccomp stop ordering, delayed injection timers, and restarts tracees with `PTRACE_SYSCALL`, `PTRACE_CONT`, `PTRACE_LISTEN`, or detach.

State and persistence behavior: state is in process memory plus output files or pipe commands. TCBs persist while tracees are live; per-TCB private data, inject vectors, unwind/KVM/mmap caches, delayed wait data, and staged memstreams are released on drop or syscall exit. Output can be shared, per-PID, appended, or piped. No repo data is persisted.

Dependencies and integration points: depends on ptrace, wait, procfs, seccomp filtering, signal and timer handling, output/color helpers, number-set qualifiers, path tracing, SELinux context printing, stack unwind, mmap cache, syscall decoding (`syscall.c`), and `trace_event.h`.

Risks: ptrace stop ordering, disappearing tracees, exec PID switches, NOMMU/vfork paths, seccomp kernel-version differences, partial output lines, attached process permissions, setuid UID swaps, and delayed injection restarts are high-risk. Output filtering relies on memstream support. Signal cleanup must avoid leaving attached processes stopped.

Test signals: exercise starting a command, `-p` attach with threads, `-f/-ff`, `-D/-DD/-DDD`, `-b execve`, status filters, `--seccomp-bpf`, `--syscall-limit`, output pipes/files, signal interruption, stopped tracees, threaded execve PID switching, delayed injection, and summary modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/strace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/strauss.c -->
# sources/test-tools/strace/src/strauss.c

Purpose: implements the optional Strauss mascot and "tip of the day" output used by version/help-adjacent paths and process exit.

Important APIs/types/functions: `strauss[]`, `strauss_lines`, `tips_tricks_tweaks`, `show_tips`, `tip_id`, `print_strauss`, and `print_totd`. Constants in `strauss.h` define verbosity threshold, formatting modes, and random-tip selection.

Control flow: `print_strauss` only prints art when version verbosity reaches `STRAUSS_START_VERBOSITY`, then bounds the number of lines by `strauss_lines`. `print_totd` is idempotent through a static `printed` guard, chooses a tip by configured ID or pseudo-random `gettimeofday` seed, formats a speech bubble, and optionally prints full mascot art.

State and persistence behavior: global `show_tips` and `tip_id` are configured by option parsing in `strace.c`; `print_totd` uses only in-process static state and writes to stderr. No persistent state.

Dependencies and integration points: depends on `defs.h`, `strauss.h`, libc random/time APIs, and `strace.c` option parsing/termination.

Risks: formatting assumes fixed ASCII art widths and non-null tip rows. Random selection is intentionally non-cryptographic. Repeated calls are suppressed, so tests must reset process state.

Test signals: cover no-tip mode, compact/full tips, explicit ID modulo tip count, random ID path, version verbosity below/above threshold, and multiple `print_totd` calls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/strauss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/strauss.h -->
# sources/test-tools/strace/src/strauss.h

Purpose: public interface for Strauss mascot and tip printing.

Important APIs/types/functions: `STRAUSS_START_VERBOSITY`, `enum tips_fmt` (`TIPS_NONE`, `TIPS_COMPACT`, `TIPS_FULL`), `enum tip_ids` (`TIP_ID_RANDOM`), `strauss_lines`, `show_tips`, `tip_id`, `print_strauss`, and `print_totd`.

Control flow: consumers set `show_tips`/`tip_id` during option parsing, pass version verbosity to `print_strauss`, and call `print_totd` at exit or when usage handling wants a tip.

State and persistence behavior: declares mutable process globals; no ownership or persistence beyond process lifetime.

Dependencies and integration points: included by `strace.c` and implemented by `strauss.c`; depends on `size_t` being available through existing include context.

Risks: header exposes globals rather than accessors, so future callers can create inconsistent tip state. Include ordering must provide `size_t`.

Test signals: compile with users of the header, parse `--tips` modes, and verify `-V` repetition increments art verbosity consistently.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/strauss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/string_to_uint.c -->
# sources/test-tools/strace/src/string_to_uint.c

Purpose: shared decimal, non-negative integer parser for command-line and procfs-derived numeric strings.

Important APIs/types/functions: `string_to_uint_ex(str, endptr, max_val, accepted_ending)` wraps `strtoll` and validates non-empty input, conversion progress, non-negative value, upper bound, overflow, and optional accepted trailing delimiter.

Control flow: clear `errno`, parse base 10, reject empty/non-numeric/negative/out-of-range/ERANGE values, reject unexpected trailing characters, optionally return the parsed end pointer, and return the value as `long long` or `-1` on failure.

State and persistence behavior: only uses `errno`; no retained state.

Dependencies and integration points: used by inline wrappers in `string_to_uint.h` and by option parsing/PID parsing in `strace.c`.

Risks: `-1` is both error sentinel and outside accepted domain by design. Accepted-ending validation checks one character only, so callers must inspect `endptr` if more structure matters.

Test signals: empty input, whitespace, negative values, `LLONG_MAX` overflow, value over `max_val`, accepted `:` delimiter, rejected delimiter, and valid zero.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/string_to_uint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/string_to_uint.h -->
# sources/test-tools/strace/src/string_to_uint.h

Purpose: declares the generic parser and supplies typed wrappers for common unsigned-limit command-line conversions.

Important APIs/types/functions: `string_to_uint_ex`, `string_to_uint_upto`, `string_to_uint`, `string_to_ulong`, `string_to_kulong`, and `string_to_ulonglong`.

Control flow: inline wrappers delegate to `string_to_uint_ex` with fixed maximums: `INT_MAX`, `LONG_MAX`, signed kernel-long maximum, or `LLONG_MAX`.

State and persistence behavior: stateless inline conversion helpers.

Dependencies and integration points: includes `<limits.h>` and `kernel_types.h`; used widely by option parsers and procfs numeric parsing.

Risks: wrappers return signed types and use `-1` for invalid input; callers must treat zero/positive values according to their own semantic constraints.

Test signals: compile for different kernel word sizes, parse max boundary values, and verify callers reject `0` where positive-only semantics are required.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/string_to_uint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/swapon.c -->
# sources/test-tools/strace/src/swapon.c

Purpose: decoder for `swapon`.

Important APIs/types/functions: `SYS_FUNC(swapon)`, `SWAP_FLAG_PRIO_MASK`, `swap_flags`, `printpath`, and flag-printing helpers.

Control flow: prints `path`, splits priority bits out of `swapflags`, prints named swap flags if present, then prints the priority numeric component inside the flag expression.

State and persistence behavior: no persistent state; reads only syscall arguments and tracee path memory through `printpath`.

Dependencies and integration points: syscall table maps `swapon` here; depends on `<sys/swap.h>` and generated xlat `swap_flags`.

Risks: priority is always printed even when no explicit priority flag is set, matching the bit-mask representation but potentially surprising for humans.

Test signals: paths valid/invalid, no flags, priority-only, named flags plus priority, and unknown flag bits.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/swapon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sync_file_range.c -->
# sources/test-tools/strace/src/sync_file_range.c

Purpose: decoder for the standard argument order of `sync_file_range`.

Important APIs/types/functions: `SYS_FUNC(sync_file_range)`, `printfd`, `print_arg_lld`, and `sync_file_range_flags`.

Control flow: prints fd, decodes 64-bit `offset` and `nbytes` using `print_arg_lld` because ABI argument slots may vary, then prints flag names.

State and persistence behavior: stateless decoder.

Dependencies and integration points: depends on large-argument helpers in `defs.h`, `<linux/fs.h>`, and generated flag xlats.

Risks: correctness depends on `print_arg_lld` advancing the argument index for architectures that split 64-bit arguments.

Test signals: native and compat ABIs, negative-looking large offsets, zero bytes, all named flags, and unknown flag bits.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sync_file_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sync_file_range2.c -->
# sources/test-tools/strace/src/sync_file_range2.c

Purpose: decoder for architectures whose `sync_file_range2` puts flags before 64-bit range arguments.

Important APIs/types/functions: `SYS_FUNC(sync_file_range2)`, `printfd`, `printflags`, `print_arg_lld`, and `sync_file_range_flags`.

Control flow: prints fd and flags from argument 1, then decodes `offset` starting at argument 2 and `nbytes` from the returned next index.

State and persistence behavior: stateless decoder.

Dependencies and integration points: syscall table selects this variant for affected ABIs; shares xlats and print helpers with `sync_file_range.c`.

Risks: using the wrong decoder for an ABI would swap flags/range interpretation; tests must cover architecture-specific syscall tables.

Test signals: same as `sync_file_range`, plus verification that argument ordering matches the target architecture.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sync_file_range2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/syscall.c -->
# sources/test-tools/strace/src/syscall.c

Purpose: syscall metadata, personality switching, entry/exit decoding, result formatting, injection/tampering, register access, and architecture glue for the trace loop.

Important APIs/types/functions: `sysent0/1/2`, `ioctlent0/1/2`, `printers0/1/2`, `errnoent`, `signalent`, `nsyscalls`, `current_personality`, `current_wordsize`, `set_personality`, `get_scno`, `syscall_entering_decode`, `syscall_entering_trace`, `syscall_entering_finish`, `syscall_exiting_decode`, `syscall_exiting_trace`, `syscall_exiting_finish`, `tamper_with_syscall_entering`, `tamper_with_syscall_exiting`, `get_instruction_pointer`, `get_stack_pointer`, `set_scno`, `set_error`, and `set_success`.

Control flow: generated syscall tables are included, shorthand macros are removed, and active pointers are switched per personality. On entry, `get_scno` obtains syscall info via `PTRACE_GET_SYSCALL_INFO` or arch registers, shuffles/personality-validates the syscall number, installs a stub for unknown syscalls, reads arguments, decodes indirect subcalls, filters paths/status/fds, optionally injects faults/delays/pokes, captures stack traces, and invokes the syscall printer. On exit, it refreshes result registers, updates mmap/comm/personality state, applies exit-side injection, prints return value/error/aux string/time, performs I/O dumps, and clears per-call flags/private data.

State and persistence behavior: holds active syscall/ioctl/printer vectors, current personality and word sizes, global and per-TCB injection vectors, cached `ptrace_sci`, register-error state, saved temporary error, and per-TCB flags. State is in memory and reset at syscall boundaries or TCB drop.

Dependencies and integration points: central dependency of `strace.c`; includes generated syscall/ioctl/error/signal tables, arch-specific `get_scno.c`, `get_error.c`, register files, ptrace syscall-info helpers, qualifiers, mmap notifications, delay/poke/retval injection, and xlat metadata.

Risks: architecture-specific register layouts, personality detection, syscall-number shuffling, seccomp stop order, unknown syscall stubs, compat argument truncation, and tampering register writes are high-risk. `PTRACE_GET_SYSCALL_INFO` fallback paths must remain coherent with older kernels.

Test signals: normal entry/exit on supported personalities, invalid syscall number, syscall restart errors, raw mode, status filtering, path/fd filtering, I/O dump sets, fault/retval/signal/delay/poke injection, seccomp stops, mmap-changing calls, `PR_SET_NAME`, unknown arch fallbacks, and compat syscall argument truncation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/syscall.h -->
# sources/test-tools/strace/src/syscall.h

Purpose: top-level syscall decoder declaration header.

Important APIs/types/functions: includes `syscall_dummy.h` and `sys_func.h`; conditionally declares UID16 syscall printers such as `chown16`, `getuid16`, `setresuid16`, and related group/uid functions.

Control flow: compile-time `HAVE_ARCH_UID16_SYSCALLS` controls whether legacy 16-bit UID function prototypes are exposed.

State and persistence behavior: no state.

Dependencies and integration points: included where generated syscall tables need printer prototypes and dummy aliases.

Risks: missing prototypes can become build failures when generated tables reference legacy functions; overbroad dummy aliases can hide missing real decoders.

Test signals: builds with and without `HAVE_ARCH_UID16_SYSCALLS` and generated tables referencing UID16 calls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/syscall_dummy.h -->
# sources/test-tools/strace/src/syscall_dummy.h

Purpose: compile-time alias map for syscalls that are unfinished, unimplemented, deprecated, structurally equivalent to another decoder, or safely handled by `printargs`.

Important APIs/types/functions: many `#define sys_*` aliases map names to real decoders (`sys_acct` to `sys_chdir`, `sys_connect` to `sys_bind`, etc.) or to `printargs`; conditional definitions account for missing kernel structs and machine-specific support.

Control flow: preprocessor conditions select aliases based on architecture and available structs before syscall table inclusion.

State and persistence behavior: no runtime state; affects compiled dispatch table.

Dependencies and integration points: included by `syscall.h` and therefore by syscall table generation in `syscall.c`.

Risks: aliases encode semantic assumptions; if a syscall diverges from its alias, output becomes misleading. Architecture conditions must track kernel ABI support.

Test signals: generated syscall tables compile on all supported architectures, alias decoders print correct argument shapes, and unimplemented/deprecated calls fall back to raw argument output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/syscall_dummy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/syscall_name.c -->
# sources/test-tools/strace/src/syscall_name.c

Purpose: maps a syscall number plus Linux audit architecture to a syscall name and optional number prefix.

Important APIs/types/functions: `audit_arch_vec`, `syscall_name_arch`, `nr_prefix`, `shuffle_scno_pers`, `scno_pers_is_valid`, `sysent_vec`, and personality audit-arch constants.

Control flow: converts the input to `kernel_ulong_t` only if lossless, scans supported personalities for a matching audit architecture, shuffles the syscall number into that personality's table space, validates it, optionally supplies a prefix for the current personality, and returns the table name.

State and persistence behavior: reads global `current_personality`; no mutation.

Dependencies and integration points: used by filters and user-facing decoding that need architecture-qualified syscall names; depends on generated xlat macro constants and syscall tables.

Risks: audit architecture mismatches and invalid shuffled numbers return NULL; prefix handling differs for current vs non-current personality.

Test signals: native/compat/x32 audit arch lookups, invalid numbers, too-large `ull_nr`, prefix output for current personality, and NULL prefix for non-current matches.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/syscall_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sysctl.c -->
# sources/test-tools/strace/src/sysctl.c

Purpose: decoder for obsolete `_sysctl`.

Important APIs/types/functions: `SYS_FUNC(sysctl)`, mpers type declaration for `struct_sysctl_args`, `umove_or_printaddr`, and field printers for pointers, signed length, and unsigned new length.

Control flow: prints the argument pointer name, fetches the tracee `__sysctl_args` structure, and emits `name`, `nlen`, `oldval`, `oldlenp`, `newval`, and `newlen`.

State and persistence behavior: stateless; reads one tracee structure.

Dependencies and integration points: depends on Linux `sysctl.h`, mpers layout handling, and syscall table entry for old sysctl.

Risks: only prints pointer fields, not nested name arrays or values. Correctness depends on mpers structure layout for compat tracees.

Test signals: NULL/bad pointer, native and compat layouts, read-only sysctl with `oldval`, write sysctl with `newval`, and unusual lengths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sysent.h -->
# sources/test-tools/strace/src/sysent.h

Purpose: defines syscall table entry shape and syscall classification flags.

Important APIs/types/functions: `struct_sysent` fields `nargs`, `sys_flags`, `sen`, `sys_func`, and `sys_name`; flags such as `TRACE_FILE`, `TRACE_NETWORK`, `TRACE_PROCESS`, `SYSCALL_NEVER_FAILS`, `MEMORY_MAPPING_CHANGE`, `TRACE_SECCOMP_DEFAULT`, `COMPAT_SYSCALL_TYPES`, `TRACE_CREDS`, `TRACE_CLOCK`, and `COMM_CHANGE`.

Control flow: no executable control flow; generated syscall tables instantiate this structure and flags drive filtering and side effects in `syscall.c`.

State and persistence behavior: type/constant declarations only.

Dependencies and integration points: consumed by syscall tables, qualifiers, seccomp filtering, mmap cache invalidation, comm cache refresh, and return-error handling.

Risks: flag bit assignments are shared ABI inside strace; accidental overlap or wrong table flags cause filtering/side effects to misbehave.

Test signals: compile generated tables, verify `%file/%net/%clock` classes, mmap cache invalidation for mapping-changing syscalls, and no-error handling for never-failing syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sysent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sysent_shorthand_defs.h -->
# sources/test-tools/strace/src/sysent_shorthand_defs.h

Purpose: short macro definitions used to keep generated/manual syscall table rows compact.

Important APIs/types/functions: macros `TD`, `TF`, `TI`, `TN`, `TP`, `TS`, `TM`, `TST`, `TLST`, `TFST`, `TSTA`, `TSF`, `TFSF`, `TSFA`, `PU`, `NF`, `MA`, `SI`, `CST`, `TSD`, `TC`, `TCL`, `CC`, and test-only `SEN(a)`.

Control flow: when `STRACE_TESTS_H` is defined, macros collapse to zero/test placeholders; otherwise they expand to real `sysent.h` flags and `MAX_ARGS`. `SEN(a)` is defined elsewhere in production.

State and persistence behavior: preprocessor-only.

Dependencies and integration points: included before syscall table inclusion in `syscall.c` and paired with `sysent_shorthand_undefs.h`.

Risks: namespace pollution if not undefined; test and production expansion must stay compatible with table row syntax.

Test signals: table preprocessing in production and test builds, and verification that undef header removes all shorthand names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sysent_shorthand_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sysent_shorthand_undefs.h -->
# sources/test-tools/strace/src/sysent_shorthand_undefs.h

Purpose: removes syscall table shorthand macros after table inclusion.

Important APIs/types/functions: `#undef` list for every shorthand macro from `sysent_shorthand_defs.h`, including `SEN`.

Control flow: no runtime flow; preprocessor cleanup.

State and persistence behavior: prevents macro definitions from persisting into later code.

Dependencies and integration points: included immediately after generated syscall tables in `syscall.c`.

Risks: missing an undef can silently affect later identifiers; undefining a macro that was not defined is safe.

Test signals: preprocess `syscall.c` and ensure no shorthand macro remains available after inclusion.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sysent_shorthand_undefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sysinfo.c -->
# sources/test-tools/strace/src/sysinfo.c

Purpose: exit-side decoder for `sysinfo`.

Important APIs/types/functions: `SYS_FUNC(sysinfo)`, mpers `sysinfo_t`, `umove_or_printaddr`, and field printers for uptime, loads, memory totals, swap totals, process count, high memory, and memory unit.

Control flow: entry returns 0 without printing. On exit, prints `info`, fetches the tracee structure if possible, and emits all relevant fields.

State and persistence behavior: no persistent state; reads one output structure after syscall completion.

Dependencies and integration points: depends on `<sys/sysinfo.h>`, mpers layout handling, and array member printer helpers.

Risks: printing on entry would expose uninitialized output buffers, so exit-only behavior is important. Compat layout must match tracee personality.

Test signals: successful call, failed call/bad pointer, native and compat mpers, and non-default memory-unit values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sysinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/syslog.c -->
# sources/test-tools/strace/src/syslog.c

Purpose: decoder for `syslog`/`klogctl` actions.

Important APIs/types/functions: `SYS_FUNC(syslog)`, `syslog_action_type`, `syslog_console_levels`, `printstrn`, and `syserror`.

Control flow: on entry always prints action type. Actions that ignore `bufp` and `len` finish immediately. Read actions defer buffer printing until exit and print returned bytes only on success. Console-level action interprets `len` as log level. Unknown/default actions print raw buffer address and decimal length.

State and persistence behavior: stateless; reads output buffer only after successful read-like actions.

Dependencies and integration points: syscall table maps syslog here; generated xlats provide action/level names.

Risks: action-specific argument meaning is irregular. For failed read actions it must not read tracee buffer.

Test signals: close/open/clear, size queries, read/read_all/read_clear success/failure, console-level names, unknown action, and buffer truncation by return value.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/syslog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sysmips.c -->
# sources/test-tools/strace/src/sysmips.c

Purpose: MIPS-only decoder for `sysmips`.

Important APIs/types/functions: `SYS_FUNC(sysmips)`, `sysmips_operations`, `MIPS_ATOMIC_SET`, and `MIPS_FIXADE`.

Control flow: compiled only under `MIPS`. Prints command name, then special-cases `MIPS_ATOMIC_SET` as address plus hex value and `MIPS_FIXADE` as one hex argument; otherwise prints three hex arguments.

State and persistence behavior: stateless.

Dependencies and integration points: depends on MIPS kernel headers and generated operation xlats; selected by MIPS syscall tables.

Risks: command-specific argument schemas are sparse; unknown commands are raw hex. Non-MIPS builds omit the decoder body.

Test signals: MIPS build, known operations, unknown operation, and syscall table compile on non-MIPS.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sysmips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/tee.c -->
# sources/test-tools/strace/src/tee.c

Purpose: ioctl decoder for Linux TEE devices.

Important APIs/types/functions: `tee_ioctl`, `tee_fetch_buf_data`, `tee_print_param_fn`, `tee_print_params`, and decoders for `TEE_IOC_VERSION`, `OPEN_SESSION`, `INVOKE`, `CANCEL`, `CLOSE_SESSION`, `SUPPL_RECV`, `SUPPL_SEND`, `SHM_ALLOC`, `SHM_REGISTER_FD`, and `SHM_REGISTER`. Uses TEE xlat tables for implementation IDs, capabilities, login types, origins, parameter attributes, and shared-memory flags.

Control flow: dispatches by ioctl code. Buffer-based calls first fetch `tee_ioctl_buf_data`, validate `buf_len` against fixed header size and `TEE_MAX_ARG_SIZE`, fetch the pointed argument header, validate parameter array size on entry, and print parameter arrays. Many ioctls print input fields on entry and changed output fields on exit using nested structs and `tprint_value_changed`.

State and persistence behavior: stateless decoder; reads tracee structures and parameter arrays, no persistent cache.

Dependencies and integration points: called from the generic ioctl decoder for TEE device commands; depends on `<linux/tee.h>` and generic tracee memory fetch/array printers.

Risks: `buf_len`, `num_params`, and `buf_ptr` validation protects against decoding buffers the kernel will reject. Pointer arithmetic uses fixed kernel ABI layouts; malformed tracee memory should fall back to printing the buffer descriptor.

Test signals: version for OP-TEE and unknown implementations, open/invoke success/failure, group login GID interpretation, every param attr family, supplier recv/send output updates, shared memory allocation/register, invalid `buf_len`, bad `buf_ptr`, and zero params.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/tee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/term.c -->
# sources/test-tools/strace/src/term.c

Purpose: ioctl decoder for terminal/TTY command arguments and command-number disambiguation.

Important APIs/types/functions: `term_ioctl`, `term_ioctl_decode_command_number`, `decode_termios2`, `decode_termios`, `decode_termio`, `decode_winsize`, `decode_ttysize`, `decode_modem_flags`, `decode_oflag`, `decode_cflag`, and numerous terminal xlat tables.

Control flow: `term_ioctl` switches on ioctl code. Output ioctls (`TCGETS`, `TIOCGWINSZ`, etc.) defer decoding until exit; setter ioctls decode on entry. Termios decoders print flag fields and, unless abbreviated, line discipline, control characters, and speed fields. Direct numeric commands print decoded values or integers. `term_ioctl_decode_command_number` resolves overlapping TTY/sound command numbers by checking character-device major ranges.

State and persistence behavior: stateless; reads pointed terminal structs or integers from tracee memory.

Dependencies and integration points: called by ioctl dispatch; depends on kernel `<linux/termios.h>`, fd metadata (`struct finfo`), and generated terminal xlat tables.

Risks: libc termios layout is intentionally avoided. Architecture differences in `NCCS`, optional `termios2`, and overlapping ioctl numbers are main compatibility risks.

Test signals: get/set termios and termio, abbreviated and verbose output, winsize/ttysize, modem flag get/set, direct `TCXONC`/`TCFLSH`, int pointer ioctls, `TIOCSTI`, no-arg ioctls, and overlapping command numbers on TTY vs non-TTY fds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/term.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/time.c -->
# sources/test-tools/strace/src/time.c

Purpose: decoders for time, timer, clock, nanosleep, adjtimex, and timerfd syscalls across time32/time64 and special architectures.

Important APIs/types/functions: `print_timezone`, `do_nanosleep`, `do_adjtimex`, `printclockname`, `do_clock_settime`, `do_clock_gettime`, `do_clock_nanosleep`, `do_clock_adjtime`, `timer_create`, `timer_delete`, `do_timer_settime`, `do_timer_gettime`, `timerfd_create`, `do_timerfd_settime`, and `do_timerfd_gettime`.

Control flow: setter calls print input structures on entry and return `RVAL_DECODED`; getter calls usually print scalar selectors on entry and output structures on exit. Sleep decoders print remaining time only when syscall is interrupted/restartable and temporarily clear syscall error so output structures can be fetched. `printclockname` handles ordinary clocks plus negative FD/cpu clock encodings when supported. Adjtimex decoders attach state text through `tcp->auxstr`.

State and persistence behavior: no persistent module state; temporarily uses `tcp->auxstr` and the syscall error-clear helpers from `syscall.c`.

Dependencies and integration points: depends on time structure printers, `kernel_fcntl.h`, signal event printing, timex xlats, clock/timer flag xlats, and syscall table variants for time32/time64/Alpha/SPARC.

Risks: output buffers must be decoded only when the kernel writes them. Restart errno handling is subtle for nanosleep and clock_nanosleep. Negative clock IDs encode multiple namespaces and need correct bit macros.

Test signals: get/settimeofday, nanosleep interrupted vs success, get/setitimer, adjtimex return strings, clock get/set/adjtime, CPU and fd clock IDs, absolute vs relative clock_nanosleep, timer create/delete/set/get, timerfd create/set/get, time32/time64 variants, and Alpha/SPARC special printers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/times.c -->
# sources/test-tools/strace/src/times.c

Purpose: exit-side decoder for `times`.

Important APIs/types/functions: `SYS_FUNC(times)`, mpers `tms_t`, `umove_or_printaddr`, and `PRINT_FIELD_CLOCK_T`.

Control flow: always prints `buf`; on syscall exit, fetches `struct tms` and prints user/system CPU time for process and children.

State and persistence behavior: stateless; reads one output structure only after exit.

Dependencies and integration points: depends on `<sys/times.h>`, mpers handling, and syscall table mapping.

Risks: entry-side buffer contents are not meaningful; compat `clock_t` size must match tracee.

Test signals: successful call, bad pointer/failure, native and compat layouts, and large clock values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/times.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/trace_event.h -->
# sources/test-tools/strace/src/trace_event.h

Purpose: declares the internal event enum passed from wait classification to trace dispatch.

Important APIs/types/functions: `enum trace_event` values `TE_BREAK`, `TE_NEXT`, `TE_RESTART`, `TE_SYSCALL_STOP`, `TE_SIGNAL_DELIVERY_STOP`, `TE_SIGNALLED`, `TE_GROUP_STOP`, `TE_EXITED`, `TE_STOP_BEFORE_EXECVE`, `TE_STOP_BEFORE_EXIT`, and `TE_SECCOMP`.

Control flow: `strace.c:next_event` creates these values and `dispatch_event` interprets them as break, continue, restart, syscall decode, signal print/delivery, exit/drop, exec handling, or seccomp handling.

State and persistence behavior: type-only header; no state.

Dependencies and integration points: shared by the main trace loop and wait-data structures.

Risks: enum ordering is not externally serialized, but adding values requires updating all dispatch switches.

Test signals: wait-status classification for every enum value and compiler warnings for unhandled enum cases where enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/trace_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/trie.c -->
# sources/test-tools/strace/src/trie.c

Purpose: compact sparse trie mapping from up-to-64-bit integer keys to fixed-width values.

Important APIs/types/functions: `trie_create`, `trie_set`, `trie_get`, `trie_iterate_keys`, `trie_free`, `trie_get_node_size`, `trie_get_node_bit_offs`, `trie_get_node`, and packed data-block helpers.

Control flow: creation validates sizes, computes fill/empty values and depth. Lookup walks pointer nodes based on high-to-low key bit segments and optionally allocates nodes/data blocks. Leaf data blocks pack 1/2/4/8/16/32/64-bit values into `uint64_t` words. Iteration recursively visits existing nodes over an inclusive key range and invokes a callback for values.

State and persistence behavior: heap-allocated trie owns pointer nodes and data blocks; `trie_free` recursively frees all allocated nodes. No persistence outside memory.

Dependencies and integration points: depends on `macros.h` bit masks and `xmalloc.h`; useful for sparse maps inside strace subsystems.

Risks: bit arithmetic around 64-bit masks, inclusive range loops at `UINT64_MAX`, and value packing require careful boundary tests. `trie_set` masks stored values to item width.

Test signals: invalid create parameters, every item width, key size 64 and smaller, out-of-range keys, default empty value, overwrites, sparse allocation, iteration over empty/populated ranges, and freeing partially populated tries.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/trie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/trie.h -->
# sources/test-tools/strace/src/trie.h

Purpose: public interface and configuration structure for the sparse trie.

Important APIs/types/functions: `struct trie` fields for empty/fill value, root data pointer, key size, item width log2, node key bits, data-block key bits, and max depth; `trie_create`, `trie_set`, `trie_get`, `trie_iterate_fn`, `trie_iterate_keys`, and `trie_free`.

Control flow: callers create a configured trie, set/get key values, iterate inclusive ranges with a callback, and free ownership.

State and persistence behavior: documents heap-owned mutable trie state. No thread-safety guarantees.

Dependencies and integration points: includes `<stdbool.h>` and `<stdint.h>`; implemented by `trie.c`.

Risks: API does not expose allocation failures from `trie_set` beyond `false`; no resizing or defragmentation; caller must call `trie_free`.

Test signals: compile API users, ownership/free behavior, callback invocation count, and documented unsupported resizing behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/trie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/truncate.c -->
# sources/test-tools/strace/src/truncate.c

Purpose: decoders for `truncate`, `truncate64`, `ftruncate`, and `ftruncate64`.

Important APIs/types/functions: four `SYS_FUNC` implementations, `printpath`, `printfd`, `PRINT_VAL_U`, and `print_arg_llu`.

Control flow: path-based calls print path then length; fd-based calls print fd then length. 64-bit variants use `print_arg_llu` to account for ABI argument splitting.

State and persistence behavior: stateless; may read path string from tracee memory.

Dependencies and integration points: selected by syscall tables for file truncation calls.

Risks: non-64 variants print length as unsigned long argument; 64-bit variants rely on correct ABI index handling.

Test signals: valid/bad paths, decoded fd paths with `-y`, zero length, large 64-bit length, and compat ABI argument splitting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ubi.c -->
# sources/test-tools/strace/src/ubi.c

Purpose: ioctl decoder for Linux UBI and UBI volume operations.

Important APIs/types/functions: `ubi_ioctl`, decoders for `UBI_IOCMKVOL`, `IOCRSVOL`, `IOCRNVOL`, `IOCEBCH`, `IOCATT`, `IOCEBMAP`, and `IOCSETVOLPROP`, plus xlat tables for volume types, flags, properties, and data types.

Control flow: structured ioctls fetch request structs and print relevant fields. Create volume and attach decode input on entry and, on successful exit, print changed integer fields using `tprint_value_changed`. Rename volume prints an array of rename entries bounded by requested count. Simpler ioctls print int/int64 pointed values or no arguments.

State and persistence behavior: stateless; reads tracee ioctl argument structures.

Dependencies and integration points: called by generic ioctl dispatch for UBI command numbers; depends on `<mtd/ubi-user.h>`, Linux ioctl definitions, and tracee memory printers.

Risks: name lengths from tracee structures must be clamped to fixed array sizes. Entry/exit split matters for commands that kernel mutates. Unknown commands fall back as decoded without argument details.

Test signals: make/resize/rename/change/attach/map/set-property, volume update int64, detach/remove/erase/map checks with int pointers, no-arg block create/remove, bad pointers, excessive name lengths, and successful exit value changes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ubi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ucopy.c -->
# sources/test-tools/strace/src/ucopy.c

Purpose: low-level tracee memory read/write helpers used by decoders and injection.

Important APIs/types/functions: `umoven`, `umovestr`, `upoken`, `invalidate_umove_cache`, `process_read_mem`, `vm_read_mem`, `vm_write_mem`, `umoven_peekdata`, `umovestr_peekdata`, `upoken_pokedata`, and page cache helpers.

Control flow: read paths prefer `process_vm_readv`, cache up to four tracee pages for small same-page reads, and fall back to `PTRACE_PEEKDATA` on `ENOSYS` or permission failures. String reads avoid crossing pages so a NUL before an inaccessible page is still found. Write paths prefer `process_vm_writev` and fall back to `PTRACE_POKEDATA`, using read-modify-write for unaligned partial words.

State and persistence behavior: static booleans remember unsupported process_vm syscalls; a small static page cache stores recent remote page starts and buffers until `invalidate_umove_cache` is called before each new event.

Dependencies and integration points: core dependency for almost every syscall/ioctl decoder and injection poke logic; uses ptrace, process_vm syscalls, current word-size globals, page-size helper, and scno definitions.

Risks: stale memory cache must be invalidated at event boundaries. Partial reads/writes, tracee exit, inaccessible pages, compat address truncation, and unaligned pokes are high-risk. Fallbacks must distinguish expected tracee disappearance from real tracer errors.

Test signals: successful process_vm read/write, ENOSYS fallback, EPERM fallback, short read diagnostics, string NUL before page boundary, invalid compat address, unaligned write at beginning/end, tracee death (`ESRCH`), and cache invalidation across events.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ucopy.c -->
