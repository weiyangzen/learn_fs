# subset-b-009327 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/dm.c -->
# sources/test-tools/strace/src/dm.c

Device-mapper ioctl decoder for `DM_*` commands. It exports `dm_ioctl`, reached from the generic ioctl dispatcher for type `0xfd`, and decodes `struct dm_ioctl` headers plus command-specific payloads such as target specs, dependency lists, name lists, target versions, messages, and geometry strings. Control flow is enter/exit aware: entry stores a copy of the header in `tcb` private data, exit compares mutable fields and suppresses unchanged failed outputs. It depends on `<linux/dm-ioctl.h>`, `dm_flags`, `umove`, `print_array`, and strace truncation helpers. Risks are malformed `data_start/data_size`, ABI-version mismatches, offset wraparound, and kernel quirks around `dm_name_list` event numbers. Tests should cover successful and failed DM ioctls, abbreviation mode, unsupported ABI versions, and misplaced variable-length payloads.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/dup.c -->
# sources/test-tools/strace/src/dup.c

Small syscall decoder for `dup`, `dup2`, and `dup3`. The shared `dup_123` helper prints `oldfd`, conditionally prints `newfd`, conditionally prints `flags`, and returns `RVAL_FD` so strace formats successful return values as file descriptors. State is limited to `tcp->u_arg`; there is no persistence or private data. It depends on `printfd`, `printflags`, and generic syscall entry formatting from `defs.h`. The main risk is argument-position mismatch across the three wrappers or missed flag decoding for `dup3`. Test signals are expected traces for one-, two-, and three-argument dup variants, including invalid fd failures and `O_CLOEXEC` flag rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/dup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/dyxlat.c -->
# sources/test-tools/strace/src/dyxlat.c

Implements dynamically allocated xlat tables used when strace learns numeric-to-string mappings at runtime. `dyxlat_alloc` allocates a header plus `nmemb + 1` `struct xlat` slots and terminates the array; `dyxlat_add_pair` duplicates labels with `xstrndup`, appends values, and keeps the list terminated; `dyxlat_get` exposes the array; `dyxlat_free` frees labels and storage. State persists in heap-owned `struct dyxlat` until freed. Dependencies are `defs.h`, xlat types, and strace allocation wrappers. Risks are caller-supplied capacity overruns, lifetime misuse after `dyxlat_get`, and incomplete cleanup on partially filled tables. Tests should allocate, add pairs, print through xlat lookup paths, and verify valgrind-clean free behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/dyxlat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/empty.h -->
# sources/test-tools/strace/src/empty.h

Intentionally empty header used as a build-system placeholder or include target where generated or optional headers may be absent. It declares no APIs, types, macros, state, or control flow. Its only integration point is the preprocessor: including it must have no side effects. The risk is accidental population changing semantics for users that rely on a no-op include. Test signals are compilation of translation units that include it and repository checks that tolerate zero-byte headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/empty.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/epoll.c -->
# sources/test-tools/strace/src/epoll.c

Decodes epoll syscalls: `epoll_create`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `epoll_pwait`, and `epoll_pwait2`. It prints file descriptors, flags, control operations, `struct epoll_event` arrays, wait timeouts, and optional signal masks. Control flow distinguishes output arrays on syscall exit and suppresses event printing on errors. State is only syscall arguments and return values. Dependencies include `kernel_fcntl.h`, `<linux/eventpoll.h>`, `epollflags`, `epollevents`, `epollctls`, `print_array`, and sigset/timespec decoders. Risks include negative or huge `maxevents`, return-count truncation, and timeout format differences between integer milliseconds and `timespec64`. Tests should cover successful waits, failed waits, `epoll_ctl` add/mod/del, `epoll_pwait` masks, and `epoll_pwait2` timeout decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/epoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/epoll_ioctl.c -->
# sources/test-tools/strace/src/epoll_ioctl.c

Ioctl subdecoder for epoll file descriptors, currently handling `EPIOCSPARAMS` and `EPIOCGPARAMS` style `struct epoll_params` commands. `print_struct_epoll_params` prints busy-poll fields and reserved values; `epoll_ioctl` chooses entry-only, exit-only, or value-changed formatting based on ioctl direction and syscall success. It depends on `<linux/eventpoll.h>`, `<linux/ioctl.h>`, `umove_or_printaddr`, and generic ioctl return flags. State is only tracee memory and enter/exit status. Risks are kernel-header drift in `struct epoll_params`, nonzero reserved fields, and incorrectly printing output on failed read ioctls. Tests should exercise set/get parameters, bad pointers, failed ioctls, and nonzero reserved data.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/epoll_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/error_prints.c -->
# sources/test-tools/strace/src/error_prints.c

Common diagnostic printing implementation for non-trace output. `verror_msg` formats optional errno text, program invocation name, and message bodies to stderr; exported helpers include `error_msg`, `error_msg_and_die`, `error_msg_and_help`, `perror_msg`, and `perror_msg_and_die`. Fatal helpers exit after printing, and `error_msg_and_help` appends usage guidance. State is external process state: `errno`, stderr, program name, and exit status. Dependencies are libc stdio/errno/varargs plus declarations in `error_prints.h`. Risks are clobbering errno before formatting, format-string annotation drift, and inconsistent fatal exit paths. Tests should verify prefixes, errno suffixes, variadic formatting, and death behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/error_prints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/error_prints.h -->
# sources/test-tools/strace/src/error_prints.h

Header declaring strace diagnostic APIs and printf-format attributes for the implementations in `error_prints.c`. It exposes nonfatal and fatal variants for plain and errno-backed messages, with `_and_die` functions marked noreturn through compiler compatibility macros. It has no runtime state, but its attributes are an integration contract with the compiler and callers. Dependencies are `gcc_compat.h`-style attributes pulled through project headers. Risks are mismatched prototypes causing lost format checking or wrong noreturn assumptions. Test signals are successful compilation with `-Wformat` diagnostics, callers using these helpers, and fatal-path tests that observe exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/error_prints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/evdev.c -->
# sources/test-tools/strace/src/evdev.c

Evdev ioctl decoder for input-device commands under ioctl type `E`. It decodes fixed commands (`EVIOCGVERSION`, IDs, repeat, keycode), variable-length strings and bitsets, ABS info, multitouch slots, write-side grabs/revokes/keymaps, and delegates force-feedback writes to the mpers decoder. Control flow is direction-sensitive: read ioctls print on exit, write ioctls print on entry. State is tracee memory, return length, and verbosity/abbreviation settings. Dependencies include `<linux/input.h>`, ioctl macros, many evdev xlat tables, `print_array`, and `evdev_write_ioctl_mpers`. Risks include `_IOC_SIZE` corner cases, return-length-driven bitset sizing, abbreviation truncation, and architecture-specific force-feedback layout. Tests should cover bitsets, variable strings, ABS v1/v2 sizing, `EVIOCGMTSLOTS`, keymaps, and read failures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/evdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/evdev_mpers.c -->
# sources/test-tools/strace/src/evdev_mpers.c

Mpers-aware decoder for evdev force-feedback structures. It maps the tracee personality's `struct ff_effect` layout into printers for envelopes, trigger/replay, and effect-specific unions (`constant`, `ramp`, `periodic`, `rumble`), exported as `evdev_write_ioctl_mpers` for `EVIOCSFF`. State is only copied tracee memory and current abbreviation mode. Dependencies are `MPERS_DEFS`, `DEF_MPERS_TYPE`, `<linux/input.h>`, and `print_evdev_ff_type` from `evdev.c`. Risks are compat layout drift, union selection by untrusted `type`, and hiding important effect details in abbrev mode. Tests should run native and compat `EVIOCSFF` traces for each supported force-feedback type plus bad pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/evdev_mpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/eventfd.c -->
# sources/test-tools/strace/src/eventfd.c

Decoder for `eventfd` and `eventfd2`. The shared helper prints the initial counter and, when present, flag bits from `efd_flags`; the wrapper returns `RVAL_FD` for fd return formatting. `eventfd` has no flag argument, while `eventfd2` uses the second argument. There is no persistent state beyond syscall arguments. Dependencies are `kernel_fcntl.h`, `xlat/efd_flags.h`, and fd return conventions from `defs.h`. Risks are missing new eventfd flags or accidentally printing a flags argument for the legacy syscall. Tests should verify plain `eventfd`, `eventfd2(EFD_CLOEXEC|EFD_NONBLOCK)`, invalid flags, and successful fd return annotation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/eventfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/execve.c -->
# sources/test-tools/strace/src/execve.c

Exec-family syscall decoder. `printargv` walks argv/envp pointer arrays, `printargc` can print compact argument counts, and `decode_execve` formats pathname, argv, envp, and `execveat` flags. `SYS_FUNC(execve)`, `execveat`, and synthetic `execv` wrappers route through it. Control flow is entry-focused because successful exec does not return normally; failures still use decoded entry arguments. State is tracee memory plus output-configuration choices for argv/env abbreviation. Dependencies include path/string printers, pointer-array iteration, `<linux/fcntl.h>`, and `execveat_flags`. Risks include unterminated vectors, inaccessible pointers, huge environments, and `execveat` dirfd/path flag interactions. Tests should cover argv/env truncation, empty vectors, bad pointers, `AT_EMPTY_PATH`, relative dirfd paths, and failed execs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/execve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/exit.c -->
# sources/test-tools/strace/src/exit.c

Minimal decoder for process termination syscalls. It prints the exit status argument and returns decoded so the generic syscall layer does not add an opaque value. There is no heap, private tcb data, or persisted state. Integration is through `SYS_FUNC(exit)` or equivalent sysent bindings for exit-like calls. Dependencies are just `defs.h` and integer printing helpers. Risks are low; the main concern is preserving conventional status formatting and not expecting a normal syscall exit stop. Tests should trace `_exit`/`exit_group` with representative status values, including high-bit statuses.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/exitkill.c -->
# sources/test-tools/strace/src/exitkill.c

Implements process cleanup helpers that kill tracees when strace exits or when configured exit-kill behavior is needed. It coordinates signal delivery to tracked tasks and preserves errno around kill operations where appropriate. State is external to this file in tracee tables and process IDs; persistence is the kernel-visible signal side effect. Dependencies include `exitkill.h`, process-control helpers, and errno-safe kill wrappers. Risks are killing the wrong pid type, losing errno in cleanup paths, and races with already-exited tracees. Tests should cover detach/exit cleanup with live and already-dead tracees, multi-threaded tracees, and errno preservation around cleanup calls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/exitkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/exitkill.h -->
# sources/test-tools/strace/src/exitkill.h

Header for exit-kill cleanup support. It declares the functions used by strace lifecycle code to arrange or perform killing of tracees during shutdown. It has no local state, but it defines an integration boundary between tracing loop code and cleanup implementation. Dependencies are project base types from `defs.h` or surrounding includes. Risks are prototype drift causing cleanup code not to be called or not preserving expected pid semantics. Test signals are compilation of lifecycle code and integration tests where strace exits while tracees remain alive.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/exitkill.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fadvise.c -->
# sources/test-tools/strace/src/fadvise.c

Decodes `fadvise64` and `fadvise64_64` variants. It prints fd, offset, length, and advisory mode through `xlat/advise.h`, with architecture-aware handling for split 64-bit arguments. State is limited to syscall arguments and personality word size. Dependencies are `<fcntl.h>`, `print_arg_lld`, and xlat advice tables. Risks are wrong low/high argument pairing on 32-bit ABIs and swapped `len`/`advice` positions for architecture variants. Tests should trace both syscall forms on native and compat personalities, including large offsets and unknown advice values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fadvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fallocate.c -->
# sources/test-tools/strace/src/fallocate.c

Decoder for `fallocate`. It prints fd, mode flags from `falloc_flags`, offset, and length using 64-bit argument helpers. There is no persistent state. Dependencies include `<linux/falloc.h>`, xlat tables, and large-argument decoding from `defs.h`. Risks are architecture-specific 64-bit argument splitting and newly added mode flags. Test signals are traces for normal allocation, punch-hole/collapse/zero-range modes, unknown flags, invalid fd failures, and large offset/length values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fallocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fanotify.c -->
# sources/test-tools/strace/src/fanotify.c

Fanotify syscall decoder. `fanotify_init` prints class/init flags with special class-bit grouping and event fd flags; `fanotify_mark` prints fanotify fd, mark flags, mask/event flags, dirfd, and path. It has no private persistent state. Dependencies are fanotify xlat tables, path/dirfd printers, and fd formatting helpers. Risks include overlapping flag domains, class-bit defaults, `FAN_NOFD`/`AT_FDCWD` handling, and path pointers that are optional depending on flags. Tests should cover init classes, close-on-exec/nonblock flags, mark add/remove/flush, mount/filesystem marks, ignored masks, and null paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fanotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fchownat.c -->
# sources/test-tools/strace/src/fchownat.c

Decoder for `fchownat`. It prints directory fd, pathname, uid, gid, and flags. State is only syscall arguments. Dependencies are path/dirfd printers, uid/gid formatting, and `AT_*` flag decoding from common helpers. Risks are null or inaccessible path handling, `AT_EMPTY_PATH`, `AT_SYMLINK_NOFOLLOW`, and uid/gid values that need namespace-aware rendering. Tests should cover normal paths, `AT_FDCWD`, empty paths, symlink flags, and invalid pointer failures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fchownat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fcntl.c -->
# sources/test-tools/strace/src/fcntl.c

Comprehensive `fcntl`/`fcntl64` decoder. It prints fd and command, then command-specific arguments: fd flags, owner pids, pipe sizes, duplicated fd return semantics, open modes, flock/flock64 structures, OFD locks, owner-ex structures, dnotify flags, leases, seals, signals, rw hints, delegations, and result aux strings for getters. `fcntl64` overrides lock commands before falling back. State is mostly syscall args and return values, plus aux string assignment on exit. Dependencies include `fetch_struct_flock*`, `fcntlcmds`, `fdflags`, `lockfcmds`, `f_seals`, and pid printers. Risks are ABI differences in flock layouts, getter output on failed syscalls, and command-specific return formats. Tests should cover every command family, native/compat locks, unknown commands, and auxstr rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fcntl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_bpf_fprog.c -->
# sources/test-tools/strace/src/fetch_bpf_fprog.c

Mpers helper for fetching `struct sock_fprog` from a tracee. It exports `get_sock_fprog_size` and `fetch_bpf_fprog`, translating compat pointer/length fields into the native `struct sock_fprog` representation without printing on success. State is only the copied structure. Dependencies are `MPERS_DEFS`, `<linux/filter.h>`, and `bpf_fprog.h`. Risks are pointer truncation/extension across personalities and callers expecting no output from a fetch helper. Tests should fetch native and compat filter programs, bad pointers, zero-length filters, and callers that subsequently print BPF instructions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_bpf_fprog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_indirect_syscall_args.c -->
# sources/test-tools/strace/src/fetch_indirect_syscall_args.c

Helper for architectures or multiplexed syscall ABIs where real syscall arguments are stored indirectly in tracee memory. It fetches the pointed argument block into `tcp->u_arg` so normal decoders can run. State mutation is the `tcb` argument array, making it an integration point before syscall-specific decoding. Dependencies are `umove`/tracee memory access and architecture sysent metadata. Risks are fetching the wrong word size, overwriting arguments after partial failure, and incompatibility with syscall restart handling. Tests should use indirect socket/ipc calls or architecture fixtures that verify decoded arguments match the tracee memory block.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_indirect_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_flock.c -->
# sources/test-tools/strace/src/fetch_struct_flock.c

Mpers fetcher for `struct flock` and `struct flock64`. It compares tracee layout with native `struct flock64`; when layouts match it fetches directly, otherwise it copies individual lock fields into a native `flock64` destination. State is only caller-provided destination data. Dependencies are `<linux/fcntl.h>`, `MPERS_DEFS`, and `umove_or_printaddr`. Risks are struct-layout assumptions, signedness of offsets/pids, and printing from a fetch helper on bad pointers. Tests should cover native and compat `F_GETLK`/`F_SETLK`, 32-bit offsets, `flock64`, and bad pointer handling.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_flock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_iovec.c -->
# sources/test-tools/strace/src/fetch_struct_iovec.c

Mpers fetch helper for `struct iovec`. It copies tracee `iov_base` and `iov_len` into the project `iovec` abstraction used by vector IO decoders. State is limited to the destination object. Dependencies are `<sys/uio.h>`, `MPERS_DEFS`, and `iovec.h`. Risks are pointer width conversion and length truncation when tracing compat processes. Tests should cover readv/writev and socket message paths under native and compat personalities, including inaccessible iovec pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_iovec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_keyctl_kdf_params.c -->
# sources/test-tools/strace/src/fetch_struct_keyctl_kdf_params.c

Mpers helper that fetches `struct keyctl_kdf_params` for key-management decoders. It translates tracee pointers and lengths into `strace_keyctl_kdf_params`/native-compatible storage without owning the pointed buffers. Dependencies are `keyctl_kdf_params.h`, `MPERS_DEFS`, and tracee memory fetch helpers. Risks are pointer-size conversion, partial struct availability on older headers, and callers misinterpreting tracee pointers as local memory. Tests should exercise keyctl KDF operations in native and compat modes with good pointers, null optional fields, and bad pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_keyctl_kdf_params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_mmsghdr.c -->
# sources/test-tools/strace/src/fetch_struct_mmsghdr.c

Fetches tracee `struct mmsghdr` for `sendmmsg`/`recvmmsg` and dumpio users. It deliberately uses `umove` rather than printing helpers because callers may need silent failure. If compat size differs, it expands pointer fields and copies message metadata plus `msg_len` into native layout. State is only the caller destination and returned byte count. Dependencies are `msghdr.h` and `MPERS_DEFS`. Risks are silent zero return on failure, pointer truncation bugs, and layout drift. Tests should cover native/compat `mmsghdr` arrays, dumpio behavior, bad pointers, and `sizeof_struct_mmsghdr`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_mmsghdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_msghdr.c -->
# sources/test-tools/strace/src/fetch_struct_msghdr.c

Silent mpers fetcher for `struct msghdr`, used by socket and dumpio decoders. It returns fetched byte count or zero, copying compat pointer fields (`msg_name`, `msg_iov`, `msg_control`) into native pointer-sized slots when necessary. It has no persistent state. Dependencies are `msghdr.h`, `MPERS_DEFS`, and `umove`. Risks are pointer conversion, callers forgetting that failure prints nothing, and mismatched control/iov length widths. Tests should cover sendmsg/recvmsg native and compat traces, dumpio paths, null optional pointers, and invalid message headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_msghdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_stat.c -->
# sources/test-tools/strace/src/fetch_struct_stat.c

Mpers fetcher for legacy/native `struct stat`. It conditionally enables layout support per personality, fetches tracee stat data, normalizes device, inode, size, blocks, mode, uid/gid, timestamps, and optional nanoseconds into `struct strace_stat`. State is only the destination structure. Dependencies are `asm_stat.h`, `stat.h`, `MPERS_DEFS`, and compile-time `HAVE_*` probes. Risks are unsupported compat layouts, signed/unsigned timestamp conversion, and missing nanosecond fields. Tests should cover stat-family syscalls on supported personalities, nanosecond-preserving platforms, unsupported-layout fallback, and bad pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_stat64.c -->
# sources/test-tools/strace/src/fetch_struct_stat64.c

Mpers fetcher for `struct stat64`. It mirrors `fetch_struct_stat` but gates support on `HAVE_M32/MX32_STRUCT_STAT64`, copies stat64 fields into `strace_stat`, and records whether nanoseconds are present. It owns no state beyond the destination object. Dependencies are `asm_stat.h`, `stat.h`, and mpers macros. Risks are architecture-specific absence of stat64, timestamp sign extension, and compat padding differences. Tests should cover `stat64`/`fstat64`/`lstat64` paths, native unsupported fallback where applicable, nanosecond fields, and invalid addresses.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_stat64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_statfs.c -->
# sources/test-tools/strace/src/fetch_struct_statfs.c

Mpers fetchers for `statfs` and `statfs64`. They normalize filesystem type, block counts, file counts, fsid, name length, fragment size, and flags into `struct strace_statfs`; `statfs64` validates the size argument and handles ARM OABI padded sizes. State is destination-only. Dependencies are `<asm/statfs.h>`, `statfs.h`, mpers macros, and layout feature defines. Risks are rejecting valid padded sizes on niche ABIs, missing fsid member variants, and integer extension errors. Tests should cover `fstatfs`, `statfs64` with valid/invalid sizes, ARM compat fixtures where available, and bad pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_statfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_xfs_quotastat.c -->
# sources/test-tools/strace/src/fetch_struct_xfs_quotastat.c

Mpers fetcher for XFS quota status structures from `<linux/dqblk_xfs.h>`. It copies tracee `fs_quota_stat_t` into the destination representation for XFS quota ioctl decoding. State is limited to fetched structure contents. Dependencies are mpers macros and XFS quota kernel headers. Risks are kernel header/layout drift and compat word-size differences in quota counters or timers. Tests should cover XFS quota status ioctls under native and compat builds, bad pointers, and representative nonzero quota fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fetch_struct_xfs_quotastat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/file_attr.c -->
# sources/test-tools/strace/src/file_attr.c

Decoder for `file_getattr` and `file_setattr` syscalls. It prints dirfd/path, fetches bounded `struct file_attr` data, decodes xflags, extent size, nextents for get, project id, COW extent size, extra nonzero bytes, size, and `AT_*`-style flags. State is syscall args and fetched tracee memory. Dependencies include `<linux/fcntl.h>`, `<linux/fs.h>`, `file_attr_flags`, `fs_xflags`, `get_pagesize`, and `print_nonzero_bytes`. Risks are user-supplied sizes below version 0, huge sizes, future struct extensions, and output-only fields for getters. Tests should cover get/set, invalid sizes, extension bytes, flags, bad pointers, and path variants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/file_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/file_handle.c -->
# sources/test-tools/strace/src/file_handle.c

Decoder for `name_to_handle_at` and `open_by_handle_at`. It prints dirfd/path or mount fd, `file_handle` header, bounded opaque handle bytes, mount id, flags, and fd-return semantics. `name_to_handle_at` stores initial `handle_bytes` in `tcb` private ulong and prints changed size on exit, including `EOVERFLOW` behavior. Dependencies include `<linux/fcntl.h>`, `name_to_handle_at_flags`, `umove`, and path/fd printers. Risks are handle length overrun, partial output on `EOVERFLOW`, and keeping the opening struct balanced across enter/exit. Tests should cover normal handles, too-small buffers, bad pointers, max/oversized handle bytes, and open-by-handle fd returns.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/file_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/filter.h -->
# sources/test-tools/strace/src/filter.h

Header declaring qualification/filter state used by command-line `-e` options and trace decisions. It exposes global number sets for traced syscalls, fd filters, signal/status/quiet/decode controls, and functions such as `qualify` and `qual_flags`. Runtime state lives in the corresponding globals allocated by `filter_qualify.c`. Dependencies include `number_set` and syscall-personality metadata. Risks are global mutable state ordering, null-set semantics, and external users assuming a set is allocated. Test signals are option-parsing tests for every qualifier plus syscall dispatch observing expected `QUAL_*` bits.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/filter_qualify.c -->
# sources/test-tools/strace/src/filter_qualify.c

Command-line qualifier parser for trace, abbrev, verbose, raw, signal, status, quiet, fd, pid, fault, inject, kvm, namespace, and SELinux context options. It maps strings to number sets, parses injection tokens (`when`, `error`, `retval`, `signal`, delays, pokes, syscall substitution), allocates injection/delay/poke data, and computes `QUAL_*` flags per syscall/personality. State is extensive global number sets, `inject_vec`, update flags, and external decoder mode initialization. Dependencies are `number_set`, `delay`, `poke`, `retval`, errno/syscall tables, secontext, KVM helpers, and static assertions. Risks include invalid token acceptance, duplicate action handling, compat return clipping, memory ownership in failed poke parsing, and global state ordering. Tests should cover every qualifier alias, injection grammar, fatal invalid inputs, compat warnings, and final `qual_flags`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/filter_qualify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/filter_seccomp.c -->
# sources/test-tools/strace/src/filter_seccomp.c

Builds and installs seccomp-BPF filters that allow untraced syscalls and trace selected or always-needed syscalls. It generates candidate programs with linear ranges and bitset matching, chooses the shortest valid program, probes kernel seccomp availability/order with a forked tracee, can dump BPF in debug mode, installs with `PR_SET_SECCOMP`, and chooses ptrace restart operators. Persistent module state includes `seccomp_filtering`, `seccomp_before_sysentry`, generated filter arrays, and `bpf_prog`. Dependencies include ptrace, prctl, wait, audit arch/syscall tables, `trace_set`, decode-pid/stack flags, and `<linux/seccomp.h>`. Risks are BPF jump overflows, program length limits, personality arch ambiguity, unsupported kernels, and stop-order assumptions. Tests should cover filtered traces, all-syscalls warning, debug dump, multi-personality builds, unavailable seccomp, and restart behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/filter_seccomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/filter_seccomp.h -->
# sources/test-tools/strace/src/filter_seccomp.h

Header for seccomp filtering integration. It declares global seccomp state and functions used by startup and ptrace-loop code, including filter checking/installation and restart-operator selection. It owns no state itself but exposes mutable state from `filter_seccomp.c`. Dependencies are `struct tcb` and ptrace constants from project headers. Risks are callers reading `seccomp_filtering` before initialization or ignoring `seccomp_before_sysentry` ordering. Tests are compile-time integration plus runtime `--seccomp-bpf` traces that validate initialization and restart decisions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/filter_seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/flock.c -->
# sources/test-tools/strace/src/flock.c

Decoder for BSD `flock`. It prints fd and lock operation flags from `flockcmds`, returning decoded. There is no persistent state. Dependencies are `<sys/file.h>`, `flockcmds`, and fd formatting. Risks are new lock operation bits or confusion between `flock` and fcntl record-lock structures. Tests should cover shared, exclusive, nonblocking, unlock, invalid combinations, and failed fd cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/flock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fs_0x15_ioctl.c -->
# sources/test-tools/strace/src/fs_0x15_ioctl.c

Filesystem ioctl decoder for ioctl type `0x15`. It handles `FS_IOC_GETFSUUID`, `FS_IOC_GETFSSYSFSPATH`, and `FS_IOC_GETLBMD_CAP`, printing output-only `fsuuid2`, sysfs path, and logical block metadata capability structures on exit. State is tracee output memory only. Dependencies are `<linux/fs.h>`, `lbmd_pi_cap_flags`, `lbmd_pi_csum_types`, and `umove_or_printaddr`. Risks are output printing after failed syscalls, bounded string/uuid lengths, and new filesystem capability fields. Tests should cover all three commands, zero and oversized lengths, nonzero metadata flags, unknown commands, and bad pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fs_0x15_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fs_0x94_ioctl.c -->
# sources/test-tools/strace/src/fs_0x94_ioctl.c

Filesystem ioctl decoder for type `0x94`, covering clone, clone-range, dedupe-range, and filesystem label commands, while delegating unknown commands to `btrfs_ioctl`. `FIDEDUPERANGE` is bidirectional: entry prints source and destination requests, exit prints per-destination status/bytes with abbreviation limiting. State is tracee memory and enter/exit status. Dependencies are `<linux/fs.h>`, array printers, fd printers, and Btrfs decoder integration. Risks are large `dest_count`, output after syscall errors, struct layout changes, and label NUL handling. Tests should cover clone variants, dedupe success/failure per target, abbrev mode, get/set labels, and Btrfs fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fs_0x94_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fs_f_ioctl.c -->
# sources/test-tools/strace/src/fs_f_ioctl.c

Decoder for ioctl type `f`, mainly `FS_IOC_FIEMAP` and filesystem inode flags. `decode_fiemap` prints requested range/flags/count on entry and mapped extents on exit; flag get/set commands print indirect `FS_*_FL` values with 32-bit compat cases. State is tracee memory and syscall phase. Dependencies are `<linux/fiemap.h>`, `fiemap_flags`, `fiemap_extent_flags`, `fs_ioc_flags`, and array printers. Risks are huge extent counts, abbrev hiding extent details, compat command aliases, and failed get handling. Tests should cover fiemap entry/exit, mapped extent arrays, errors, `FS_IOC_GETFLAGS`, `SETFLAGS`, compat aliases, and unknown commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fs_f_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fs_x_ioctl.c -->
# sources/test-tools/strace/src/fs_x_ioctl.c

Decoder for ioctl type `X` filesystem commands: `FITRIM`, `FS_IOC_FSGETXATTR`, `FS_IOC_FSSETXATTR`, `FS_IOC_SHUTDOWN`, `FIFREEZE`, and `FITHAW`. It prints trim ranges, fsxattr flags/extents/project/cow fields, shutdown flags, and no-argument freeze/thaw commands. State is tracee memory and syscall phase. Dependencies are `<linux/fs.h>`, `fs_xflags`, `fs_shutdown_flags`, and generic ioctl return flags. Risks are output-only get xattrs, nonzero hidden fields, and new xflags/shutdown flags. Tests should cover get/set xattr, trim, shutdown, freeze/thaw, bad pointers, and unknown command passthrough.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fs_x_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fsconfig.c -->
# sources/test-tools/strace/src/fsconfig.c

Decoder for `fsconfig`. It prints filesystem context fd, command from `fsconfig_cmds`, key string, value string or address depending on command, and auxiliary integer. State is syscall arguments only. Dependencies are `<linux/mount.h>`, key/string printers, fd formatting, and mount API xlat tables. Risks are command-specific value interpretation (`SET_STRING`, `SET_BINARY`, `SET_PATH`, `SET_PATH_EMPTY`, `SET_FD`), null keys/values, and new fsconfig commands. Tests should cover every command class, bad strings, binary pointer printing, fd/path commands, and unknown commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fsconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fsmount.c -->
# sources/test-tools/strace/src/fsmount.c

Decoder for `fsmount`. It prints filesystem context fd, mount flags, and mount attribute flags, returning `RVAL_FD` for the produced mount fd. State is only syscall arguments. Dependencies are `<linux/mount.h>`, `fsmount_flags`, `fsmount_attr_flags`, and fd return formatting. Risks are new mount flags or attribute bits and invalid fd rendering. Tests should cover successful fd returns, common flag combinations, unknown bits, and failed calls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fsmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fsopen.c -->
# sources/test-tools/strace/src/fsopen.c

Decoder for `fsopen`. It prints filesystem name and flags from `fsopen_flags`, returning fd-formatted results. No persistent state is used. Dependencies are `<linux/mount.h>`, string printers, xlat flags, and syscall return flags. Risks are null or inaccessible fs names and new open flags. Tests should cover known filesystems, bad pointers, unknown flags, and success/failure fd returns.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fsopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fspick.c -->
# sources/test-tools/strace/src/fspick.c

Decoder for `fspick`. It prints directory fd, pathname, and `fspick_flags`, returning a filesystem context fd. State is only arguments. Dependencies are `<linux/mount.h>`, dirfd/path printers, and xlat flags. Risks include `AT_EMPTY_PATH`-like semantics, null paths, and newly added flags. Tests should cover path and fd-based picking, empty paths, unknown flags, bad pointers, and fd-return formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fspick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fstatfs.c -->
# sources/test-tools/strace/src/fstatfs.c

Decoder for `fstatfs`. It prints fd on entry, then on successful exit fetches and prints `struct statfs` through shared statfs formatting helpers. State is syscall phase and output memory. Dependencies are fd printers and `fetch_struct_statfs`/statfs printers from the statfs subsystem. Risks are printing output after failures and architecture-specific statfs layout support. Tests should cover success, error, bad output pointer, and representative filesystem flag/type values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fstatfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/fstatfs64.c -->
# sources/test-tools/strace/src/fstatfs64.c

Decoder for `fstatfs64`. It prints fd, size, and output statfs64 structure, validating the user-supplied size through `fetch_struct_statfs64`. State is syscall phase and output memory. Dependencies are statfs64 fetch/print helpers and fd formatting. Risks are accepting or rejecting ABI-specific padded sizes, output after errors, and size argument mismatches. Tests should cover valid sizes, invalid sizes, bad pointers, compat personalities, and successful filesystem stats.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/fstatfs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/futex.c -->
# sources/test-tools/strace/src/futex.c

Decoder for classic `futex_time32` and `futex_time64`. The shared `do_futex` prints `uaddr`, operation flags, and command-specific arguments for wait, wake, bitset, requeue, PI locks, wake-op bitfields, and fallback unknown forms, using the appropriate timespec printer. State is syscall arguments only. Dependencies are futex xlat tables, bitset/wake-op tables, and time32/time64 printers. Risks are op masking with private/realtime flags, complicated `FUTEX_WAKE_OP` bitfield formatting, time ABI differences, and new futex commands. Tests should cover each command family, private/realtime flags, wake-op encoding, unknown ops, and time32/time64 timeout rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/futex2.c -->
# sources/test-tools/strace/src/futex2.c

Decoder for futex2 syscalls: `futex_waitv`, `futex_wake`, `futex_wait`, and `futex_requeue`. It prints futex2 size/flag combinations, waiter arrays capped by `FUTEX_WAITV_MAX`, masks, counts, timeouts, and clock ids. State is syscall arguments and local array-print count. Dependencies are `<linux/futex.h>`, `futex2_sizes`, `futex2_flags`, classic `futexbitset`, timespec64, and clock xlat tables. Risks are waiter-array overrun/truncation, flag-size mask composition, and new futex2 ABI changes. Tests should cover waitv arrays, excessive waiter counts, wake masks, wait timeouts, requeue two-waiter inputs, unknown flags, and bad waiter pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/futex2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/gcc_compat.h -->
# sources/test-tools/strace/src/gcc_compat.h

Compiler-compatibility header defining attributes and feature fallbacks used across strace, such as format checking, noreturn, fallthrough, packed/aligned, printf-like declarations, and diagnostic helpers. It has no runtime control flow or state, but it strongly affects compile-time checking and generated code assumptions. Dependencies are compiler feature macros and project portability conventions. Risks are incorrect feature detection across GCC/Clang versions, attributes changing ABI/layout, and fallthrough/noreturn annotations hiding real bugs. Test signals are warning-clean builds across supported compilers, configure-feature matrix builds, and code paths relying on the declared attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/gcc_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/gen/gen_hdio.c -->
# sources/test-tools/strace/src/gen/gen_hdio.c

Generated HDIO variable ioctl decoder included by `hdio.c` through `gen/generated.h`. It contains one leaf decoder per generated HDIO command, printing scalar pointers, arrays, strings, and xlat-backed values, then dispatches via generated `var_ioctl_HDIO`. State is only tracee memory and enter/exit phase. Dependencies are generated metadata, `<linux/hdreg.h>`, xlat tables like `hdio_ide_nice`/`hdio_busstates`, and generic array/string printers. Risks are editing generated code manually, stale generation against kernel headers, and unsupported compat HDIO behavior. Tests should regenerate from `maint/gen/defs/hdio.def`, compile, and trace representative HDIO get/set commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/gen/gen_hdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/gen/generated.h -->
# sources/test-tools/strace/src/gen/generated.h

Generated umbrella header for generated decoder fragments. It includes `defs.h` and exposes generated declarations needed by generated source such as `gen_hdio.c` and consumers like `hdio.c`. It owns no runtime state or control flow. Dependencies are the generator pipeline and the generated C files staying synchronized. Risks are stale declarations after regeneration or manual edits breaking generated include order. Test signals are clean builds after running generator scripts and successful inclusion by generated decoder translation units.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/gen/generated.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/gen_bpf_attr_check.sh -->
# sources/test-tools/strace/src/gen_bpf_attr_check.sh

Shell generator that emits C compile-time checks for BPF attribute structure sizes and offsets. It uses project headers and generated `bpf_attr` definitions to produce assertions that catch kernel UAPI drift. State is generated output only; the script itself has no persistent runtime state. Dependencies are the shell, C preprocessor/compiler context, `defs.h`, and BPF attr metadata. Risks are host shell portability, header-version skew, and generated checks becoming stale when BPF structs change. Tests should run the script in the build, compile the generated check, and verify failures occur for intentional size mismatches.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/gen_bpf_attr_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/generate_mpers_am.sh -->
# sources/test-tools/strace/src/generate_mpers_am.sh

Build helper script that generates Automake fragments for mpers personality-specific sources. It enumerates mpers inputs and emits make rules/variables used to build native and compat printer objects. Persistent output is generated makefile text. Dependencies are POSIX shell, repository layout, and mpers naming conventions. Risks are quoting/path issues, stale generated automake fragments, and missing new mpers files. Tests should run the script during maintainer regeneration, compare generated output, and build all supported personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/generate_mpers_am.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/generate_sen.sh -->
# sources/test-tools/strace/src/generate_sen.sh

Small shell generator for syscall entry-name (`SEN`) related generated data. It transforms syscall decoder names into generated definitions consumed by sysent tables. State is generated text only. Dependencies are POSIX shell, expected input ordering, and sysent shorthand conventions. Risks are name parsing drift and generated data falling out of sync with decoder functions. Tests should run regeneration, compile sysent tables, and verify new syscall decoders are represented.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/generate_sen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/get_personality.c -->
# sources/test-tools/strace/src/get_personality.c

Implements architecture/personality detection helper used to choose syscall tables and word sizes for tracees. It returns the active personality index from process state and platform-specific personality bits. State is not persisted here, but its result drives global `current_personality` decisions elsewhere. Dependencies include `get_personality.h`, platform macros, and process/personality APIs. Risks are wrong mapping on multi-ABI architectures such as x86_64/x32/i386 and stale personality after exec. Tests should trace native and compat binaries and verify syscall names/argument sizes match the detected personality.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/get_personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/get_personality.h -->
# sources/test-tools/strace/src/get_personality.h

Header declaring personality detection support. It exposes the function contract used by trace setup and syscall decoding to select personality-specific syscall tables. It has no state itself. Dependencies are project personality constants and platform headers included by the implementation. Risks are prototype drift or callers using personality values before initialization. Test signals are clean compilation and runtime traces for supported ABI personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/get_personality.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/get_robust_list.c -->
# sources/test-tools/strace/src/get_robust_list.c

Decoder for `get_robust_list`. It prints pid on entry and, on exit, prints the robust-list head pointer and length pointer outputs. State is syscall phase and output memory. Dependencies are pid printers, pointer/number fetch helpers, and process-id type handling. Risks are output pointers on failed syscalls, pid namespace rendering, and pointer-size differences. Tests should cover self pid, other pid, null/bad output pointers, failure cases, and compat pointer widths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/get_robust_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/getcpu.c -->
# sources/test-tools/strace/src/getcpu.c

Decoder for `getcpu`. It prints CPU and node output pointers on exit and the unused cache argument/address as appropriate. State is only syscall phase and tracee memory. Dependencies are integer pointer printers and generic syscall formatting. Risks include output after failure, null pointers, and historical third-argument behavior. Tests should cover successful calls with both outputs, null outputs, bad pointers, and failed calls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/getcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/getcwd.c -->
# sources/test-tools/strace/src/getcwd.c

Decoder for `getcwd`. It prints the output buffer as a string on successful exit, prints the raw address on failure, and always prints the size argument. State is syscall phase and return length. Dependencies are string printers and syscall result handling. Risks are off-by-one use of returned length, non-NUL output, and output after errors. Tests should cover success, `ERANGE`, bad pointers, zero size, and paths containing unusual bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/getcwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/getpagesize.c -->
# sources/test-tools/strace/src/getpagesize.c

Decoder for `getpagesize`, a no-argument pure syscall/library-entry style decoder. It prints no arguments and relies on the generic return value for the page size. There is no state or dependency beyond `defs.h`. Risks are minimal; the decoder must not invent arguments or mark the return incorrectly. Tests should verify traces show an empty argument list and decimal return value.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/getpagesize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/getpid.c -->
# sources/test-tools/strace/src/getpid.c

Decoders for pid/session/process-group syscalls: `getpid`, `gettid`, `getpgrp`, `getpgid`, `getsid`, and `setpgid`. Pure getters return typed return-value flags (`RVAL_TGID`, `RVAL_TID`, `RVAL_PGID`, `RVAL_SID`) so pid namespace/comm rendering can apply; argumented calls print pid/pgid values. State is syscall arguments and return formatting. Dependencies are pid-type printers and return-value flags. Risks are wrong pid type tagging and namespace translation mismatches. Tests should cover all getters, `getpgid`/`getsid` with target pids, `setpgid`, failures, and pid namespace decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/getpid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/getrandom.c -->
# sources/test-tools/strace/src/getrandom.c

Decoder for `getrandom`. It prints the buffer on successful exit using the returned byte count, the requested count, and flags from `getrandom_flags`; on failure it prints the buffer address. State is syscall phase and return value. Dependencies are buffer/string byte printers and xlat flag table. Risks are leaking large random buffers without truncation controls, output after failure, and new flags. Tests should cover successful short reads, zero length, `GRND_NONBLOCK`/`GRND_RANDOM`, bad buffers, and unknown flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/getrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/gpio_ioctl.c -->
# sources/test-tools/strace/src/gpio_ioctl.c

GPIO ioctl decoder for v1 and v2 character-device APIs. It decodes chip info, line info/watch/unwatch, handle/event requests, get/set values, v1 config, v2 line attributes/config/request/value operations, and returned fds. Control flow is direction-sensitive with value-changed output on successful exits. State is tracee memory and syscall phase. Dependencies include `<linux/gpio.h>`, v1/v2 GPIO xlat tables, fd printers, array printers, and ioctl return flags. Risks are `num_lines`/`num_attrs` bounds, nonzero padding, ABI evolution in v2 attributes, and output-only fd fields. Tests should cover all ioctl cases, v2 attr ids, bad pointers, failed exits, padding, and unknown commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/gpio_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/hdio.c -->
# sources/test-tools/strace/src/hdio.c

HDIO ioctl decoder. It handles `HDIO_GETGEO`, `HDIO_DRIVE_CMD`, and delegates many generated variable HDIO commands to `var_ioctl_HDIO` when native word size matches; compat HDIO is intentionally unsupported because the kernel lacks it. `HDIO_DRIVE_CMD` prints command header on entry and status/error/data buffer on exit, including `EIO` status behavior. State is tracee memory and phase. Dependencies include `<linux/hdreg.h>`, mpers geometry type, `hdio_drive_cmds`, and `gen/generated.h`. Risks are generated decoder staleness, 512-byte sector buffer sizing, and error-specific output. Tests should cover getgeo, drive command success/EIO/other errors, generated HDIO commands, and compat skip behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/hdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/hostname.c -->
# sources/test-tools/strace/src/hostname.c

Decoders for hostname syscalls. `sethostname` prints the input buffer with the supplied length; `gethostname` prints the output buffer on successful exit or address on failure plus size. State is syscall phase and tracee string memory. Dependencies are string printers and `<linux/utsname.h>` where needed. Risks are non-NUL buffers, length truncation, output after failure, and libc/kernel semantic differences. Tests should cover set/get, too-small buffers, non-NUL data, bad pointers, and zero sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/hostname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/inotify.c -->
# sources/test-tools/strace/src/inotify.c

Decoder for inotify syscalls. It prints fd/path/mask for `inotify_add_watch`, fd/watch descriptor for removal, and flags for `inotify_init1`; `inotify_init` returns fd-formatted output. State is syscall arguments only. Dependencies are `kernel_fcntl.h`, inotify mask/init xlat tables, path printers, and fd return flags. Risks are new mask bits, path pointer failures, and return-value formatting. Tests should cover add/remove, init/init1 flags, unknown masks, bad paths, and failed fd cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/inotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/inotify_ioctl.c -->
# sources/test-tools/strace/src/inotify_ioctl.c

Ioctl decoder for inotify fds. It handles inotify-specific commands such as `INOTIFY_IOC_SETNEXTWD` when available, printing the next watch descriptor integer from tracee memory. State is tracee memory only. Dependencies are `<linux/ioctl.h>`, inotify ioctl definitions, and generic ioctl return flags. Risks are conditional kernel-header availability and bad pointer behavior. Tests should cover set-next-watch-descriptor ioctl, unknown commands, and invalid pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/inotify_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/io.c -->
# sources/test-tools/strace/src/io.c

Core IO syscall decoders for `read`, `write`, vector IO, positional IO, `preadv2`/`pwritev2`, `tee`, `splice`, and `vmsplice`. It provides public iovec printers (`iov_decode_addr`, `iov_decode_str`, `tprint_iov_upto`) that handle word-size differences and cumulative data limits. Control flow prints read buffers on exit using return counts and write buffers on entry using requested counts. State is syscall phase, return value, current word size, and local cumulative iovec budget. Dependencies include `<sys/uio.h>`, `rwf_flags`, `splice_flags`, print-array helpers, and 64-bit arg utilities. Risks include compat iovec layout, large output truncation, split offset arguments, x32 preadv2 flag position, and read error handling. Tests should cover scalar/vector read-write success/failure, compat vectors, flags, splice offsets, and vmsplice.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/io_uring.c -->
# sources/test-tools/strace/src/io_uring.c

Large decoder for `io_uring_setup`, `io_uring_enter`, and `io_uring_register`. It prints setup params and ring offsets, enter flags with traditional/extended/registered wait arguments, and many register op payloads: buffers/files, updates, probes, restrictions, resource tags, IOWQ, ring fds, pbuf rings/status, sync cancel, NAPI, clock, clone buffers, SQE/msg-ring, ZCRX, resize, memory regions, and query lists. State includes `tcb` private ulong for probe entry/exit printing and syscall phase; most data is tracee memory. Dependencies are `<linux/io_uring.h>`, query headers, many `uring_*` xlat tables, iovec/fd/affinity/timespec/sigset helpers, and compile-time size checks. Risks are fast-moving kernel ABI drift, union decoding by opcode, 128-byte SQEs, bounded query-list traversal, reserved fields, and nargs semantics. Tests should cover each register opcode family, bad pointers, failed exits, extended enter args, setup outputs, and new-kernel fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/io_uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ioctl.c -->
# sources/test-tools/strace/src/ioctl.c

Generic `ioctl` syscall decoder and dispatcher. It prints fd with optional device finfo for overlapping commands, formats command numbers through xlat lookup or synthesized `_IOC`, decodes special command-number families (evdev, hid, mixer, term, uinput, joystick, SPI), dispatches by `_IOC_TYPE` to subsystem decoders, and hex-dumps unknown typed payloads when safe. State is syscall phase plus optional fd path/finfo; subsystem decoders may use tcb private data. Dependencies are generated `ioctlent`, many `DECL_IOCTL` decoders, ioctl macros, fd path lookup, and xlat verbosity. Risks are command-number overlaps, architecture-specific `_IOC_SIZE` quirks, unknown-payload privacy/size handling, and dispatcher coverage drift. Tests should cover known/unknown ioctls, overlapping tty/sound cases, raw/verbose modes, bad pointers, subsystem dispatch, and duplicate symbols.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ioctl_iocdef.c -->
# sources/test-tools/strace/src/ioctl_iocdef.c

Tiny compile/generation support file that includes ioctl definitions so build scripts can derive or validate `_IOC_*` constants for the target architecture. It has no runtime state or exported decoder logic. Dependencies are `<linux/ioctl.h>` and the build system that compiles or preprocesses it. Risks are host/target header mismatch and architecture-specific ioctl encoding differences. Test signals are successful generation/build on each supported architecture and correct `_IOC` formatting in `ioctl.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ioctl_iocdef.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ioctls_zfs.h -->
# sources/test-tools/strace/src/ioctls_zfs.h

Header containing ZFS ioctl command definitions or table fragments used by strace ioctl lookup/decoding. It has no runtime control flow but contributes constants/symbol names to ioctl command rendering. Dependencies are generated ioctl-table build code and ZFS ioctl numbering conventions. Risks are stale constants relative to OpenZFS, symbol collisions, and platform-specific availability. Tests should verify ioctl table generation includes these commands and traces render expected ZFS names rather than raw `_IOC` values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ioctls_zfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ioctlsort.c -->
# sources/test-tools/strace/src/ioctlsort.c

Build utility that sorts ioctl table entries for efficient lookup by `ioctl.c`. It reads generated ioctl entries, orders them by numeric code while preserving duplicate-symbol handling, and emits sorted data for compilation. Persistent state is generated output. Dependencies are libc sorting/io, ioctl entry structure definitions, and build scripts. Risks are unstable ordering for duplicate codes, malformed input handling, and mismatch with `ioctl_lookup` expectations. Tests should run the utility on fixture tables with duplicates and verify generated tables are sorted and bsearch-compatible.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ioctlsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ioperm.c -->
# sources/test-tools/strace/src/ioperm.c

Decoder for `ioperm`. It prints starting port, number of ports, and enable flag, returning decoded. State is syscall arguments only. Dependencies are integer printers and `defs.h`. Risks are minimal; the main concern is unsigned range formatting for port/count and boolean enable readability. Tests should cover enabling/disabling ranges, zero length, large port ranges, and permission failures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ioperm.c -->
