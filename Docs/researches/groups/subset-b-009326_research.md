# subset-b-009326 research

Grouped research report for the strace BPF, filesystem, process, descriptor, color, delay, and ptrace-helper sources in `sources/test-tools/strace/src`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf.c -->
## sources/test-tools/strace/src/bpf.c

Purpose: Implements the `bpf(2)` syscall decoder. It translates `cmd`, the user-supplied `union bpf_attr` byte buffer, and size-specific command layouts into structured strace output, including newer kernel fields while tolerating older shorter `attr` sizes.

Important APIs and types: The core abstraction is the `BEGIN_BPF_CMD_DECODER`/`END_BPF_CMD_DECODER` macro pair, which copies up to the known command-specific struct size from the syscall buffer, then lets a decoder print fields conditionally by `len`. `SYS_FUNC(bpf)` dispatches through `bpf_cmd_decoders[]`. Helper types include local `struct ebpf_insn`, `struct ebpf_insns_data`, `struct obj_get_info_saved`, `print_bpf_obj_info_fn`, and `union strace_bpf_iter_link_info`.

Control flow: On entry, `SYS_FUNC(bpf)` prints `cmd` and `attr`, validates `size <= get_pagesize()`, fetches the attr into a static page-sized buffer, and invokes the command decoder. The command decoders cover map creation and element operations, program load, object pin/get, attach/detach, test run, id iteration, object info, prog query, raw tracepoint, BTF load/get, task fd query, batch map operations, link create/update/detach, iterator create, token create, program stream read, and struct-ops association. Several decoders intentionally return `0` on entry so exit-time output fields can be printed after the kernel writes them.

State and persistence: Uses `set_tcb_priv_ulong` for counts (`BPF_PROG_QUERY`, batch operations, task fd query) and `set_tcb_priv_data` for `BPF_OBJ_GET_INFO_BY_FD` entry snapshots. `print_boottime` caches the realtime-to-boottime offset in a static `timespec`. Static buffers are allocated once for syscall attr and BPF object info.

Dependencies and integration: Depends on `defs.h`, `bpf_attr.h`, `<linux/bpf.h>`, `<linux/filter.h>`, xlat tables for BPF commands/types/flags, and the generic print/fetch APIs. It integrates with `bpf_filter.c` via `print_bpf_filter_code` for eBPF instruction code decoding.

Risks: Layout drift is the dominant risk; the decoder manually mirrors many kernel UAPI versions and union interpretations. Incorrect `offsetof` gates can mislabel fields for old kernels. Static buffers are page-sized, so oversized attrs deliberately fall back to address printing. Link-create union decoding is partly inferred from `attach_type`, and TODO comments note ambiguous cases.

Test signals: Exercise `bpf` command families with varying attr sizes, including output fields that change across entry/exit. Regression tests should cover `BPF_PROG_LOAD` instruction/log printing, `BPF_OBJ_GET_INFO_BY_FD` map/program object detection, link-create attach types, batch count mutation, and unknown or oversized attr fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_attr.h -->
## sources/test-tools/strace/src/bpf_attr.h

Purpose: Provides strace-local, command-specific mirrors of `union bpf_attr` and BPF object info structs. The file lets `bpf.c` decode kernel BPF UAPI across multiple kernel generations without relying entirely on the build host headers.

Important APIs and types: Defines structs such as `BPF_MAP_CREATE_struct`, `BPF_PROG_LOAD_struct`, `BPF_OBJ_PIN_struct`, `BPF_PROG_ATTACH_struct`, `BPF_PROG_TEST_RUN_struct`, `BPF_OBJ_GET_INFO_BY_FD_struct`, `BPF_PROG_QUERY_struct`, `BPF_BTF_LOAD_struct`, `BPF_LINK_CREATE_struct`, `BPF_TOKEN_CREATE_struct`, `BPF_PROG_STREAM_READ_BY_FD_struct`, and `BPF_PROG_ASSOC_STRUCT_OPS_struct`. It also defines `bpf_map_info_struct`, `bpf_prog_info_struct`, expected size macros, and aliases for commands sharing layouts.

Control flow: Header-only data contract; no executable flow. `bpf.c` uses each `*_struct_size` macro as the maximum known decode length, then gates optional fields with `offsetof` checks.

State and persistence: No runtime state. The meaningful persistence is ABI shape: fixed field order, `ATTRIBUTE_ALIGNED(8)` on all `uint64_t` fields, and expected size constants that should catch unexpected build-time layout changes.

Dependencies and integration: Included by `bpf.c` after kernel BPF headers. Relies on basic integer types, `ATTRIBUTE_ALIGNED`, and `offsetofend` from common strace headers. It intentionally documents kernel UAPI breakage with `skip check` comments where layout quirks are known.

Risks: Any mismatch with current kernel UAPI can corrupt decode output. New fields require both this header and `bpf.c` command decoders to be updated. Union members in `BPF_LINK_CREATE_struct` are especially fragile because the decoder guesses active members from attach type and flags.

Test signals: Build-time size checks and bpf syscall tests should validate every `expected_*_size`. Runtime tests should cover old attr lengths, new trailing fields, and each alias macro such as map batch operations or id iteration commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_attr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_filter.c -->
## sources/test-tools/strace/src/bpf_filter.c

Purpose: Decodes classic BPF filter programs and provides shared code-name printing for classic BPF and eBPF instruction classes.

Important APIs and types: Exports `print_bpf_filter_code`, `print_bpf_fprog`, and `decode_bpf_fprog`. Uses `struct bpf_filter_block_data` to track optional `k` formatting callback and printed instruction count.

Control flow: `print_bpf_filter_code` decomposes the `code` field into class, size, mode, source, operation, return value, and miscellaneous bits using classic or extended xlat tables. `decode_bpf_fprog` fetches a `struct bpf_fprog`, prints `len`, then delegates array printing to `print_bpf_fprog`. `print_bpf_filter_block` stops at `BPF_MAXINSNS`, chooses `BPF_JUMP` formatting if `jt` or `jf` are non-zero, otherwise prints `BPF_STMT`.

State and persistence: No global state. Per-array state is held in `bpf_filter_block_data.count` to enforce the instruction cap.

Dependencies and integration: Depends on `defs.h`, `bpf_filter.h`, `bpf_fprog.h`, `<linux/filter.h>`, and BPF/eBPF xlat tables. It is reused by seccomp and socket filter decoders, and by `bpf.c` for eBPF instruction code printing.

Risks: Correctness depends on interpreting classic and extended op bits differently in shared code. If kernel BPF macros or xlat tables change, unknown flag bits can be printed as `BPF_???`.

Test signals: Tests should feed statement-only filters, jump filters, max-insn boundary cases, abbrev mode, custom `k` printers from seccomp/socket wrappers, and eBPF code paths through `print_bpf_filter_code(..., true)`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_filter.h -->
## sources/test-tools/strace/src/bpf_filter.h

Purpose: Declares the shared classic BPF filter block representation and filter-program printing entry points.

Important APIs and types: Defines `struct bpf_filter_block` with `code`, `jt`, `jf`, and `k`, plus callback typedef `print_bpf_filter_fn`. Declares `print_bpf_fprog` and `decode_bpf_fprog`.

Control flow: Header-only. Callers pass either a known program address and length to `print_bpf_fprog`, or an address to a `bpf_fprog` wrapper to `decode_bpf_fprog`.

State and persistence: No state; it is a common ABI-like contract for decoder modules.

Dependencies and integration: Requires `struct tcb` and `kernel_ulong_t` from `defs.h` context. Used by `bpf_filter.c`, `bpf_seccomp_filter.c`, and `bpf_sock_filter.c`.

Risks: The struct mirrors classic `sock_filter`; layout assumptions must remain consistent with `<linux/filter.h>`.

Test signals: Compile coverage plus callers that decode seccomp and socket BPF programs validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_fprog.h -->
## sources/test-tools/strace/src/bpf_fprog.h

Purpose: Defines a strace-local BPF program descriptor that can represent a tracee pointer in `kernel_ulong_t` form.

Important APIs and types: `struct bpf_fprog { unsigned short len; kernel_ulong_t filter; }`.

Control flow: Header-only; consumed by `decode_bpf_fprog`.

State and persistence: No runtime state.

Dependencies and integration: Needs `kernel_ulong_t` from `defs.h`. It avoids direct use of host `struct sock_fprog` pointer size so mpers/compat tracing remains stable.

Risks: Incorrect word-size handling would break compat tracees; the explicit `kernel_ulong_t` pointer mitigates that.

Test signals: 32-bit personality and native seccomp/socket filter tests should confirm pointer printing and array fetching remain correct.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_fprog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_seccomp_filter.c -->
## sources/test-tools/strace/src/bpf_seccomp_filter.c

Purpose: Specializes BPF program printing for seccomp filters by decoding `BPF_RET` constants as seccomp return actions.

Important APIs and types: Static `print_seccomp_filter_k` callback, exported `print_seccomp_fprog`, and exported `decode_seccomp_fprog`.

Control flow: The callback checks whether an instruction class is `BPF_RET`. It splits `k` into `SECCOMP_RET_ACTION_FULL` action and data payload, prints the symbolic action from `seccomp_ret_action`, and appends non-zero data bits. Non-return instructions fall back to generic hex `k` printing in `bpf_filter.c`.

State and persistence: No persistent state.

Dependencies and integration: Depends on `bpf_filter.h`, `<linux/filter.h>`, `<linux/seccomp.h>`, and `xlat/seccomp_ret_action.h`. Used by seccomp-related syscall decoders to display loaded filters.

Risks: Only `BPF_RET` gets semantic treatment; malformed or non-standard filters are still printed structurally but may not convey policy intent.

Test signals: Seccomp filter tests should include allow, errno, trap, trace, kill, user-notif actions, action data payloads, and non-return BPF statements.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_seccomp_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_sock_filter.c -->
## sources/test-tools/strace/src/bpf_sock_filter.c

Purpose: Specializes classic BPF program printing for socket filters by decoding socket ancillary load offsets.

Important APIs and types: Static `print_sock_filter_k` callback, exported `print_sock_fprog`, and exported `decode_sock_fprog`.

Control flow: For `BPF_LD | BPF_ABS` instructions, `print_sock_filter_k` recognizes `SKF_AD_OFF`, `SKF_NET_OFF`, and `SKF_LL_OFF` ranges. It prints the base symbolic constant plus offset or ancillary field name; otherwise generic BPF formatting prints the raw `k`.

State and persistence: No persistent state.

Dependencies and integration: Depends on `bpf_filter.h`, `<linux/filter.h>`, `xlat/skf_ad.h`, and `xlat/skf_off.h` constants. Used by socket-option decoders that inspect filter programs.

Risks: Only absolute load offsets receive socket-specific formatting. New kernel socket filter pseudo offsets need xlat updates to avoid `SKF_AD_???`.

Test signals: Socket filter tests should include ancillary, network, link-layer, and ordinary absolute offsets.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_sock_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/btrfs.c -->
## sources/test-tools/strace/src/btrfs.c

Purpose: Implements the mpers-aware Btrfs ioctl decoder, covering Btrfs administrative, device, balance, quota, scrub, search, send, space, and subvolume operations.

Important APIs and types: Exports `MPERS_PRINTER_DECL(int, btrfs_ioctl, ...)`. Helper printers cover balance args, feature flags, qgroup limits/inheritance, data containers, search keys and headers, space info, timespecs, scrub progress, and device replacement start/status parameters. It uses mpers aliases for several Btrfs structs that contain pointers or layout-sensitive fields.

Control flow: `btrfs_ioctl` switches on ioctl code. No-argument commands return decoded immediately. Scalar commands print integer or flag arguments. Read-only commands commonly return `0` on entry and decode on exit. Read/write commands print input on entry, then use `tprint_value_changed()` on successful exit to print output fields. Complex branches decode balance state, defrag ranges, device info/replacement, feature arrays, fs info, device stats arrays, inode lookup/path containers, logical inode containers, quota commands/status, received subvolume timestamps, scrub progress, tree-search buffers, send clone source arrays, space info arrays, and vol args for snapshot/device operations.

State and persistence: Uses `set_tcb_priv_ulong` to remember whether `BTRFS_IOC_INO_LOOKUP` used implicit root tree id. Otherwise state is transient and fetched from tracee memory. Output behavior depends on entry/exit phase and `syserror(tcp)`.

Dependencies and integration: Depends on `defs.h`, `linux/btrfs_tree.h`, `linux/fs.h`, mpers definitions, and many Btrfs xlat tables. Integrated through the generic ioctl dispatcher, returning `RVAL_IOCTL_DECODED` for recognized commands.

Risks: Btrfs ioctl structs are large and version-sensitive; mpers pointer fields and kernel layout drift are high-risk. Array/container printing must respect abbreviation and sequence truncation. Search buffer decoding guards offset overflow but still depends on correct kernel-provided lengths.

Test signals: Btrfs tests should cover entry/exit behavior for read/write ioctls, failed syscalls, short and long arrays, tree-search v1/v2 including `EOVERFLOW`, quota inheritance, scrub/device replacement statuses, feature arrays, and compat personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/btrfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/cacheflush.c -->
## sources/test-tools/strace/src/cacheflush.c

Purpose: Provides architecture-specific decoders for the `cacheflush` syscall variants.

Important APIs and types: Defines `SYS_FUNC(cacheflush)` under mutually exclusive architecture guards: `M68K`, `BFIN || CSKY`, `SH`, and `NIOS2`.

Control flow: Each implementation prints the argument order used by that architecture. M68K prints address, scope, flags, and length. BFIN/CSKY print address, length, and cache flag xlat. SH prints address, length, and flag bitset. NIOS2 prints address and length from argument 3 while ignoring scope/cache-type fields.

State and persistence: No persistent state.

Dependencies and integration: Depends on `defs.h`, optional `<asm/cachectl.h>`, and architecture-specific cacheflush xlat tables.

Risks: Argument positions differ by architecture, so accidental cross-architecture reuse would be wrong. Some fields are intentionally ignored on NIOS2.

Test signals: Architecture-specific syscall tests should verify printed argument names, flag xlat strings, and unsupported-architecture exclusion at build time.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/cacheflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/cachestat.c -->
## sources/test-tools/strace/src/cachestat.c

Purpose: Decodes the `cachestat` syscall, printing the input range on entry and cache statistics on exit.

Important APIs and types: `SYS_FUNC(cachestat)`, `struct cachestat_range`, and `struct cachestat`.

Control flow: On entry, prints `fd` with `printfd` and fetches `cstat_range` from the tracee to print `off` and `len`. On exit, fetches `cstat` and prints `nr_cache`, `nr_dirty`, `nr_writeback`, `nr_evicted`, and `nr_recently_evicted`, then prints raw `flags`.

State and persistence: No stored state; relies on syscall phase to split input and output fields.

Dependencies and integration: Depends on `defs.h` and local `cachestat.h`. Uses generic memory fetch and field print helpers.

Risks: Flags are printed numerically because no xlat table is used. If the kernel extends structures, this decoder will not show new fields until updated.

Test signals: Tests should include valid pointers, null/unreadable pointers, successful exits, failed exits, and non-zero flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/cachestat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/cachestat.h -->
## sources/test-tools/strace/src/cachestat.h

Purpose: Defines tracee-facing layouts for the `cachestat` syscall range and result structures.

Important APIs and types: `struct cachestat_range` has `uint64_t off` and `len`. `struct cachestat` has five `uint64_t` counters.

Control flow: Header-only; consumed by `cachestat.c`.

State and persistence: No state.

Dependencies and integration: Includes `<stdint.h>` and is local to strace's cachestat decoder.

Risks: Layout must track kernel UAPI exactly. Any new fields or type changes require synchronized decoder updates.

Test signals: Compile layout checks and cachestat syscall output tests validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/cachestat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/capability.c -->
## sources/test-tools/strace/src/capability.c

Purpose: Decodes `capget` and `capset` syscall headers and capability bitsets.

Important APIs and types: Local `struct user_cap_header_struct`, `struct user_cap_data_struct`, `get_cap_header`, `print_cap_header`, `print_cap_bits`, `print_cap_data`, `SYS_FUNC(capget)`, and `SYS_FUNC(capset)`.

Control flow: `get_cap_header` fetches the header only when the pointer is non-null and verbose mode is active. `capget` prints header on entry and, on successful exit, decodes `datap` according to header version. `capset` prints both header and input data on entry. Version 1 uses one capability word; versions 2 and 3 use two.

State and persistence: `get_cap_header` returns a pointer to a static header buffer; it is reused across calls, so callers consume it immediately.

Dependencies and integration: Includes `caps0.h` and `caps1.h` to build enum values, then `xlat/cap_mask0.h`, `xlat/cap_mask1.h`, and `xlat/cap_version.h`. Uses pid translation printing for header pid.

Risks: Static header storage is simple but non-reentrant. Unknown capability versions are treated as one-word data, which may be incomplete for future versions.

Test signals: Tests should cover all three capability versions, null pointers, unreadable pointers, high capability bits, capget errors, and pid rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/capability.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/caps0.h -->
## sources/test-tools/strace/src/caps0.h

Purpose: Lists low capability constants used to define the first capability mask enum.

Important APIs and types: Expands to enum entries from `CAP_CHOWN` through `CAP_SETFCAP`.

Control flow: Header fragment only; it is intended to be included inside an enum definition.

State and persistence: No state.

Dependencies and integration: Included by `capability.c` before `xlat/cap_mask0.h`. The order must match Linux capability numbers 0-31.

Risks: Missing or reordered entries would break symbolic capability decoding.

Test signals: Capability bitmask tests for low bits should print the expected `CAP_*` names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/caps0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/caps1.h -->
## sources/test-tools/strace/src/caps1.h

Purpose: Lists high capability constants used to define the second capability mask enum.

Important APIs and types: Expands to entries `CAP_MAC_OVERRIDE` through `CAP_CHECKPOINT_RESTORE`.

Control flow: Header fragment only; included inside an enum.

State and persistence: No state.

Dependencies and integration: Included by `capability.c` before `xlat/cap_mask1.h`. These entries represent `CAP_TO_INDEX` high-word capability values.

Risks: New kernel capabilities above this list will decode as unknown until this file and xlat data are updated.

Test signals: Capability bitmask tests for high bits should print `CAP_BPF`, `CAP_PERFMON`, and `CAP_CHECKPOINT_RESTORE` correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/caps1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/chdir.c -->
## sources/test-tools/strace/src/chdir.c

Purpose: Decodes the single-argument `chdir` syscall.

Important APIs and types: `SYS_FUNC(chdir)`.

Control flow: Prints argument name `path`, calls `printpath` on `tcp->u_arg[0]`, and returns `RVAL_DECODED`.

State and persistence: No state.

Dependencies and integration: Depends on `defs.h` and generic path-printing support.

Risks: Minimal; behavior is tied to `printpath` handling of unreadable or null tracee strings.

Test signals: Tests should include normal paths, null pointers, and paths requiring truncation or escaping.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/chdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/chmod.c -->
## sources/test-tools/strace/src/chmod.c

Purpose: Decodes mode-changing syscalls: `chmod`, `fchmodat`, `fchmodat2`, and `fchmod`.

Important APIs and types: Shared `decode_chmod`, `decode_fchmodat`, and syscall decoders for the four syscalls.

Control flow: `decode_chmod` prints pathname and numeric mode at a caller-supplied argument offset. `chmod` uses offset 0. `fchmodat` prints `dirfd` then decodes path/mode at offset 1. `fchmodat2` adds `flags` using `fchmodat_flags`. `fchmod` prints fd and numeric mode.

State and persistence: No state.

Dependencies and integration: Uses `defs.h`, `<linux/fcntl.h>`, `xlat/fchmodat_flags.h`, `print_dirfd`, `printfd`, `printpath`, and `print_numeric_umode_t`.

Risks: `fchmodat2` flag xlat must track kernel additions. Mode is intentionally numeric, not symbolic.

Test signals: Tests should cover dirfd variants, `AT_EMPTY_PATH`, invalid flags, fd rendering, and mode formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/chmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/clone.c -->
## sources/test-tools/strace/src/clone.c

Purpose: Decodes process/thread creation and namespace-affecting syscalls: `clone`, `clone3`, `setns`, `unshare`, and `fork`.

Important APIs and types: Argument-position macros per architecture, `namespace_auxstr_init`, `read_namespace_id`, `get_namespace_auxstr`, `print_tls_arg`, `SYS_FUNC(clone)`, `SYS_FUNC(clone3)`, `SYS_FUNC(setns)`, `SYS_FUNC(unshare)`, and `SYS_FUNC(fork)`.

Control flow: `clone` prints stack/flags/signal on entry and defers pointer-output arguments until exit when flags require parent tid, pidfd, tls, child tid, or namespace aux strings. `clone3` fetches `struct clone_args`, prints fields conditionally by flags and provided size, prints tail bytes for oversized structs, and revisits output fields on successful exit. `setns` and `unshare` optionally defer completion so namespace IDs can be printed after success. `fork` returns decoded with TGID return formatting.

State and persistence: Static `show_namespace` is enabled by `namespace_auxstr_init`. Namespace aux strings use static buffers and `/proc/<pid>/ns/*` readlink calls. `clone3` has no tcb private allocation but re-fetches the tracee struct on exit.

Dependencies and integration: Depends on `scno.h`, `<linux/sched.h>`, `xstring.h`, `unistd.h`, clone/setns/unshare xlat tables, pid translation, fd printing, user-desc printing, and auxstr return handling.

Risks: Architecture-specific argument order is fragile. Namespace aux strings depend on `/proc`, pid namespace translation, and syscall success. `clone3` size-gating must handle old and future struct layouts without over-reading.

Test signals: Tests should cover architecture personalities, `clone2` stack size, CSIGNAL-only flags, pidfd and parent/child tid outputs, tls printing, `clone3` short/oversized structs, set_tid arrays, cgroup fd, namespace aux output, and failed syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/clone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/close_range.c -->
## sources/test-tools/strace/src/close_range.c

Purpose: Decodes the `close_range` syscall.

Important APIs and types: `SYS_FUNC(close_range)`.

Control flow: Prints `first`, `last`, and `flags`, using unsigned integer formatting for fd bounds and `close_range_flags` for the flags.

State and persistence: No state.

Dependencies and integration: Depends on `defs.h`, `<linux/close_range.h>`, and `xlat/close_range_flags.h`.

Risks: New flags require xlat updates. The decoder casts fd bounds to `unsigned int`, matching syscall semantics.

Test signals: Tests should cover zero flags, `CLOSE_RANGE_UNSHARE`, `CLOSE_RANGE_CLOEXEC`, max fd values, and unknown bits.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/close_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/color.c -->
## sources/test-tools/strace/src/color.c

Purpose: Initializes optional ANSI color output for strace formatting.

Important APIs and types: Globals `color_is_enabled`, `color_mode`, `color_seq_table`; local `struct color_key`; helpers `lookup_color_kind`, `trim_spaces`, `is_sgr_seq`, `make_sgr_seq`, `parse_strace_colors`, `is_no_color`; exported `color_init`.

Control flow: `color_init` disables color by default, exits for `COLOR_NEVER`, evaluates tty/output-separately/NO_COLOR/TERM for `COLOR_AUTO`, initializes the sequence table from defaults, parses `STRACE_COLORS` overrides, then sets `color_is_enabled`. The parser accepts colon-separated `name=sgr` entries and ignores unknown or invalid pieces.

State and persistence: Global color mode and sequence table persist for the process. Custom SGR sequences are heap-allocated by `xasprintf`; replacement frees any prior non-default sequence for that kind.

Dependencies and integration: Depends on `defs.h`, `color.h`, libc string/ctype APIs, optional termcap `tgetent`/`tgetnum`, environment variables `NO_COLOR`, `TERM`, and `STRACE_COLORS`.

Risks: `trim_spaces` computes `strlen(s) - 1`, so empty strings after leading trim need careful reasoning; current parser calls it on token fragments that can be empty. Invalid SGR data is ignored silently. Color escapes must be emitted via uncolored output paths to avoid recursive styling.

Test signals: Tests should cover auto/never/always modes, non-tty and per-pid output, `NO_COLOR`, `TERM=dumb`, valid and invalid `STRACE_COLORS`, case-insensitive keys, and duplicate overrides.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/color.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/color.h -->
## sources/test-tools/strace/src/color.h

Purpose: Declares color mode/kind enums, global color state, initialization, and inline emission helper.

Important APIs and types: `enum color_mode_t`, `enum color_kind_t`, extern `color_mode`, `color_seq_table`, `color_is_enabled`, `color_init`, and `tprint_color_seq`.

Control flow: `tprint_color_seq` emits the sequence for a kind only when colors are enabled.

State and persistence: Exposes global process-wide color configuration owned by `color.c`.

Dependencies and integration: Includes `<stdbool.h>` and uses `tprints_string_uncol` from the output layer.

Risks: Callers must pass valid `COLOR_*` enum values below `COLOR_KIND_MAX`. Color output depends on `color_init` being called before printing.

Test signals: Output tests should verify no escape sequences when disabled and correct kind-specific sequences when enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/color.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/copy_file_range.c -->
## sources/test-tools/strace/src/copy_file_range.c

Purpose: Decodes `copy_file_range`.

Important APIs and types: `SYS_FUNC(copy_file_range)`.

Control flow: Prints input fd, input offset pointer as signed 64-bit value via `printnum_int64`, output fd, output offset pointer, length, and raw unsigned flags.

State and persistence: No state.

Dependencies and integration: Depends on `defs.h`, `printfd`, and integer pointer-print helpers.

Risks: Flags are raw numeric because no symbolic xlat is used. Offset pointers are decoded as values at addresses, so unreadable pointers fall back through `printnum_int64` behavior.

Test signals: Tests should cover null offsets, readable offsets, fd paths, large lengths, non-zero flags, and error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/copy_file_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/count.c -->
## sources/test-tools/strace/src/count.c

Purpose: Maintains and prints strace syscall summary statistics for `-c` style counting, including optional wall-clock columns and unknown syscall buckets.

Important APIs and types: `struct call_counts`, `struct unknown_call_counts`, `struct unknown_call_bucket`, `enum count_summary_columns`, `count_syscall`, `set_sortby`, `set_count_summary_columns`, `set_overhead`, and `call_summary`.

Control flow: `count_syscall` ensures a per-personality count vector exists, inserts unknown syscall buckets when needed, updates call/error counts, computes elapsed syscall time using either wall-clock or system CPU time, subtracts configured overhead, clamps negative durations to zero, and optionally tracks wall-clock stats separately. Sorting functions compare totals, min/max/avg, calls, errors, names, and wall columns. `set_sortby` and `set_count_summary_columns` parse user aliases. `call_summary` iterates personalities, calls `call_summary_pers`, and restores the original personality.

State and persistence: Global `countv[]`, `unknown_countv[]`, `overhead`, column configuration, wall-column flags, and `sortfun` persist for the process. Unknown syscall buckets grow dynamically and store synthetic names.

Dependencies and integration: Depends on `defs.h`, `xstring.h`, timespec helpers, personality/sysent tables, `count_wallclock`, syscall entry/exit timestamps in `tcb`, and output `FILE *`.

Risks: Summary output assumes at least one call when printing totals; empty vectors are skipped. Column parsing rejects duplicates and unknown names. Unknown syscall indices combine known syscall count with bucket index, so helper lookup must distinguish real scno from synthetic positions.

Test signals: Tests should cover sorting by every alias family, duplicate/unknown columns, wall columns with and without `count_wallclock`, overhead subtraction, negative elapsed clamp, unknown syscall naming, multi-personality summaries, and zero-error rows.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/count.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/counter_ioctl.c -->
## sources/test-tools/strace/src/counter_ioctl.c

Purpose: Decodes Linux Counter subsystem ioctl arguments.

Important APIs and types: `print_struct_counter_component`, `print_struct_counter_watch`, and exported `counter_ioctl`.

Control flow: For `COUNTER_ADD_WATCH_IOCTL`, prints `argp`, fetches `struct counter_watch`, and prints nested component type/scope/parent/id plus event and channel. `COUNTER_ENABLE_EVENTS_IOCTL` and `COUNTER_DISABLE_EVENTS_IOCTL` take no decoded argument but return `RVAL_IOCTL_DECODED`. Unknown counter ioctls return `RVAL_DECODED`.

State and persistence: No state.

Dependencies and integration: Depends on `defs.h`, `<linux/ioctl.h>`, `<linux/counter.h>`, and counter xlat tables. Integrated into the generic ioctl decoder.

Risks: Uses `CHECK_IOCTL_SIZE` and `CHECK_TYPE_SIZE` for expected layout; kernel UAPI changes require updates. Nested component decoding depends on host header availability.

Test signals: Tests should cover add-watch with each xlat field, enable/disable events, unreadable pointers, and unknown ioctl fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/counter_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/defs.h -->
## sources/test-tools/strace/src/defs.h

Purpose: Central strace internal header. It defines global configuration, core trace-control structures, result flags, syscall/personality abstractions, decoder declarations, printing helpers, fetch helpers, and common inline utilities used across syscall decoders.

Important APIs and types: Defines `MAX_ARGS`, personality word-size macros, `struct_ioctlent`, injection flags and `struct inject_data`/`struct inject_opts`, `struct tcb`, TCB and qualifier flags, `entering`/`exiting`/`syserror`/`verbose`/`abbrev` predicates, `RVAL_*` return formatting flags, pid/socket enums, many external xlat tables, decoder helper typedefs, mpers macros, `SYS_FUNC`, syscall range helpers, integer truncation helpers, `popcount32`, `ilog2_64`, `ilog2_32`, `printflags`/`printxval` wrappers, and `print_big_u64_addr`.

Control flow: Header-only but controls most decoder behavior through macros and inline functions. `SYS_FUNC(name)` establishes decoder signatures. Return-value flags steer the main syscall output machinery. Predicate macros read `struct tcb` flags to decide entry/exit, raw/verbose/abbrev handling, filtering, tampering, and delay state.

State and persistence: Declares process-global state such as current personality, word sizes, sysent/ioctl tables, inject vectors, `printing_tcp`, and personality names. `struct tcb` stores per-tracee syscall args, return/error state, timestamps, injection config, private decoder data, output streams, pid namespace metadata, delay state, seccomp/KVM/stacktrace fields, and command name cache.

Dependencies and integration: Includes architecture/config, kernel type, sysent, mpers, xlat, malloc, print-field, and syscall headers. Nearly every source in this subset depends on it directly or indirectly.

Risks: Extremely high blast radius. Small macro or struct changes can affect all decoders, mpers builds, multiple personalities, and output formatting. Word-size dispatch and pointer truncation must remain correct for compat tracing. TCB flag semantics are coupled to the tracing loop outside this file.

Test signals: Whole-suite build/test coverage is required after changes. Focused tests should include native and compat personalities, syscall entry/exit transitions, injected failures/delays/pokes, raw/abbrev/verbose qualifiers, return formatting, fd/pid/path printing, and mpers decoder compilation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/delay.c -->
## sources/test-tools/strace/src/delay.c

Purpose: Implements syscall delay injection storage and timer management.

Important APIs and types: `struct inject_delay_data`, globals `delay_data_vec`, capacity/size counters, `delay_timer`, `delay_timer_is_armed`, and functions `alloc_delay_data`, `fill_delay_data`, `is_delay_timer_armed`, `delay_timer_expired`, `arm_delay_timer`, `delay_tcb`.

Control flow: Delay specs are allocated in a growable vector. `fill_delay_data` stores enter or exit delay durations. `delay_tcb` marks a tracee delayed/tampered, computes absolute expiration from `CLOCK_MONOTONIC`, creates the POSIX timer on first use, compares against the currently armed timer, and arms the timer for the chosen tracee.

State and persistence: Process-global vector stores configured delays. A single process-global POSIX timer and boolean track active delay wakeups. Each delayed `tcb` stores its own absolute expiration time and flags.

Dependencies and integration: Depends on `defs.h`, `delay.h`, timespec helpers, `xgrowarray`, `timer_create`, `timer_settime`, and tracing-loop handling of `TCB_DELAYED`.

Risks: Timer comparison uses the selected delay interval rather than the stored absolute expiration, so changes here need careful review. Delay index overflow is fatal. A single timer must serve all delayed tracees correctly.

Test signals: Tests should cover enter and exit delays, multiple configured delay indices, timer re-arming order, invalid index death paths, and interaction with injected syscall tampering flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/delay.h -->
## sources/test-tools/strace/src/delay.h

Purpose: Declares the delay-injection API shared between qualifier parsing and the tracing loop.

Important APIs and types: `alloc_delay_data`, `fill_delay_data`, `is_delay_timer_armed`, `delay_timer_expired`, `arm_delay_timer`, and `delay_tcb`.

Control flow: Header-only declarations; callers allocate/fill delay slots and later arm or clear the timer as tracees are delayed and resumed.

State and persistence: State is implemented in `delay.c`.

Dependencies and integration: Requires `struct tcb`, `struct timespec`, `uint16_t`, and `bool` from common headers.

Risks: Callers must use valid delay indices returned by `alloc_delay_data`.

Test signals: Compile coverage plus delay injection tests validate this contract.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/desc.c -->
## sources/test-tools/strace/src/desc.c

Purpose: Decodes descriptor-related syscalls in this file: `close`, `select`, old indirect `select`, Alpha `osf_select`, and `pselect6` time32/time64 variants.

Important APIs and types: `fd_set_arg_name`, `SYS_FUNC(close)`, `decode_select`, `SYS_FUNC(oldselect)`, `SYS_FUNC(osf_select)`, `SYS_FUNC(select)`, `do_pselect6`, `SYS_FUNC(pselect6_time32)`, and `SYS_FUNC(pselect6_time64)`.

Control flow: `close` prints fd. `decode_select` normalizes `nfds`, caps very large values to avoid excessive memory, computes fdset byte size from `current_wordsize`, prints fd bitsets and timeout on entry, then on successful exit builds an aux string describing ready input/output/exception fds and remaining timeout. `do_pselect6` appends the sigmask argument after select decoding.

State and persistence: Uses a static `outstr[1024]` for select aux strings. No per-tcb private state.

Dependencies and integration: Depends on `defs.h`, `xstring.h`, fd printing, bitset scanning, time/time32/time64 printers, and indirect syscall argument fetching.

Risks: Select fdset decoding is sensitive to `nfds`, word size, malloc failures, and output truncation. The static aux buffer is overwritten by subsequent calls.

Test signals: Tests should include negative and huge `nfds`, null fdsets, ready fd output, timeout output, abbrev/verbose behavior, pselect sigmask, oldselect indirect args, and compat word sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/dirent.c -->
## sources/test-tools/strace/src/dirent.c

Purpose: Decodes legacy `getdents` and `readdir` directory entry syscalls.

Important APIs and types: `kernel_dirent_t` via mpers, `header_size`, `print_dentry_head`, `decode_dentry_head`, `decode_dentry_tail`, `SYS_FUNC(getdents)`, `print_old_dirent`, and `SYS_FUNC(readdir)`.

Control flow: `getdents` delegates to `xgetdents` with callbacks. The head callback returns each record length and optionally prints `d_ino`, `d_off`, and `d_reclen`. The tail callback prints capped `d_name` and the trailing `d_type` byte. `readdir` prints fd on entry and, on exit, prints either the raw pointer for zero return or one decoded old dirent.

State and persistence: No persistent state, except optional `tcp->last_dirfd` when SELinux context support is enabled.

Dependencies and integration: Depends on `defs.h`, `kernel_dirent.h`, mpers, `xgetdents.h`, `dirent_types`, path printing, and fd printing.

Risks: Record length and name/type packing are kernel ABI-sensitive. Tail decoding caps names at 256 bytes and must avoid overreading malformed records.

Test signals: Tests should include multiple entries, abbreviated output, long names, d_type decoding, malformed/truncated records, zero-return `readdir`, and mpers personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/dirent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/dirent64.c -->
## sources/test-tools/strace/src/dirent64.c

Purpose: Decodes `getdents64`.

Important APIs and types: `kernel_dirent64_t`, `print_dentry_head`, `decode_dentry_head`, `decode_dentry_tail`, and `SYS_FUNC(getdents64)`.

Control flow: `getdents64` delegates to `xgetdents` with a header size ending at `d_name`. The head callback prints inode, offset, and record length outside abbrev mode. The tail callback prints symbolic `d_type`, then a capped directory name.

State and persistence: No persistent state.

Dependencies and integration: Depends on `xgetdents.h`, `kernel_dirent.h`, `dirent_types`, path printing, and generic memory fetches.

Risks: Name length is bounded to 256 for output, so unusually long or malformed entries are abbreviated. Correctness relies on `xgetdents` record traversal.

Test signals: Tests should include ordinary and long filenames, all common `DT_*` types, abbrev mode, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/dirent64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/dirent_types.c -->
## sources/test-tools/strace/src/dirent_types.c

Purpose: Materializes the `dirent_types` xlat table for directory entry type names.

Important APIs and types: Includes `xlat/dirent_types.h` after `<dirent.h>`.

Control flow: No executable flow in this file.

State and persistence: Defines static/generated xlat data through the included header.

Dependencies and integration: Used by `dirent.c`, `dirent64.c`, and any decoder that prints `DT_*` values.

Risks: Depends on platform `dirent.h` constants and generated xlat content.

Test signals: Directory-entry tests should verify numeric d_type values print symbolic `DT_*` names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/dirent_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace.c -->
## sources/test-tools/strace/src/disable_ptrace.c

Purpose: Builds a helper executable that runs a program with the entire `ptrace` syscall rejected with `EPERM`.

Important APIs and types: Defines `DISABLE_PTRACE_ERRNO EPERM`, `DEFAULT_PROGRAM_INVOCATION_NAME`, then includes `disable_ptrace_request.c`.

Control flow: All runtime flow comes from the included template: initialize program name, install a seccomp filter rejecting ptrace, then `execvp` the target.

State and persistence: No separate state beyond the included template.

Dependencies and integration: This is a specialization wrapper for strace tests that need ptrace unavailable.

Risks: Macro-driven include style means changes in `disable_ptrace_request.c` affect this helper directly.

Test signals: Tests should assert ptrace fails with `EPERM` while non-ptrace syscalls and exec of target continue.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_get_syscall_info.c -->
## sources/test-tools/strace/src/disable_ptrace_get_syscall_info.c

Purpose: Specializes the ptrace-disabling helper to reject only `PTRACE_GET_SYSCALL_INFO`.

Important APIs and types: Defines `DISABLE_PTRACE_REQUEST PTRACE_GET_SYSCALL_INFO` and helper invocation name before including `disable_ptrace_request.c`.

Control flow: Runtime flow is inherited from the template; its seccomp filter compares ptrace request argument against `PTRACE_GET_SYSCALL_INFO` and returns errno only for that request.

State and persistence: No local state.

Dependencies and integration: Used by tests for fallback behavior when `PTRACE_GET_SYSCALL_INFO` is unavailable or blocked.

Risks: Requires the target platform to define the request value through included ptrace headers.

Test signals: Tests should show `PTRACE_GET_SYSCALL_INFO` fails while other ptrace requests can still pass the filter.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_get_syscall_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_getregset.c -->
## sources/test-tools/strace/src/disable_ptrace_getregset.c

Purpose: Specializes the ptrace-disabling helper to reject register-fetch requests used by strace, choosing `PTRACE_GETREGSET` on x86_64 when old getregs support exists.

Important APIs and types: Includes `defs.h`, temporarily redefines `static` to expose `getregs_old.h` configuration, conditionally defines `DISABLE_PTRACE_REQUEST PTRACE_GETREGSET`, then includes `disable_ptrace_request.c`.

Control flow: Compile-time logic chooses the request macro. Runtime flow is inherited from the seccomp template.

State and persistence: No local runtime state.

Dependencies and integration: Supports tests for register-fetch fallback paths, especially around old vs regset APIs.

Risks: The `#define static` include trick is delicate and can be affected by changes in `getregs_old.h`.

Test signals: Tests should confirm the built helper blocks the intended register request on supported architectures and reports unsupported otherwise.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_getregset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_request.c -->
## sources/test-tools/strace/src/disable_ptrace_request.c

Purpose: Template implementation for helper executables that run a target program under a seccomp filter rejecting `ptrace` or a specific ptrace request.

Important APIs and types: `die`, `init`, optional `get_arch`, and `main`. Uses `struct sock_filter`, `struct sock_fprog`, `struct seccomp_data`, ptrace request macros, and `DISABLE_PTRACE_REQUEST`/`DISABLE_PTRACE_ERRNO` specialization macros.

Control flow: `init` sets `program_invocation_name`. When required kernel features are present, `main` validates arguments, enables `PR_SET_NO_NEW_PRIVS`, builds a classic BPF filter that matches architecture, syscall number `__NR_ptrace`, and optionally first ptrace argument, returns `SECCOMP_RET_ERRNO | errno` for the rejected case, installs the filter with `PR_SET_SECCOMP`, then `execvp`s the target. `get_arch` forks and traces a child to discover the audit architecture via `PTRACE_GET_SYSCALL_INFO`. Unsupported builds compile a `main` that errors out.

State and persistence: No long-lived state after exec. Uses forked child only during architecture discovery.

Dependencies and integration: Depends on `defs.h`, `ptrace.h`, `scno.h`, signal/wait/prctl headers, Linux filter/seccomp headers, and wrapper macros from including files.

Risks: The helper itself uses ptrace before installing seccomp; if `PTRACE_GET_SYSCALL_INFO` is unavailable, it exits. BPF argument endianness handling for `args[0]` is critical. Macro inclusion makes each wrapper a separate compiled program.

Test signals: Tests should cover no-argument failure, unsupported-feature build, full ptrace rejection, single-request rejection, errno selection, successful target exec, and architecture mismatch allow path.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_set_syscall_info.c -->
## sources/test-tools/strace/src/disable_ptrace_set_syscall_info.c

Purpose: Specializes the ptrace-disabling helper to reject only `PTRACE_SET_SYSCALL_INFO`.

Important APIs and types: Defines `DISABLE_PTRACE_REQUEST PTRACE_SET_SYSCALL_INFO` and helper invocation name before including `disable_ptrace_request.c`.

Control flow: Runtime behavior is the shared seccomp-template flow: install a filter that blocks ptrace when the first argument matches `PTRACE_SET_SYSCALL_INFO`, then exec the requested program.

State and persistence: No local state.

Dependencies and integration: Used by tests that verify strace behavior when syscall-info setting is unavailable.

Risks: Depends on platform request macro availability and the shared template's BPF argument matching.

Test signals: Tests should show only `PTRACE_SET_SYSCALL_INFO` receives the configured errno and other ptrace requests are not rejected by this helper.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_set_syscall_info.c -->
