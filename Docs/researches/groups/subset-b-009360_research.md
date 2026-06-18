<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-filesystem.c -->
# sources/test-tools/stress-ng/core-filesystem.c

## Purpose

This implementation is the central filesystem utility layer for stress-ng. It provides temporary path construction and cleanup, filesystem capacity and type reporting, robust file read/write wrappers, descriptor and pipe limit discovery, directory entry utilities, Linux cache-dropping and inode-flag cleanup, and small helpers used by many stressors that interact with `/proc`, `/sys`, temporary files, file descriptors, pipes, and mounted filesystems.

## Important APIs, Types, And Functions

The private `stress_fs_name_t` table maps Linux `statfs` magic values to human-readable filesystem names when `linux/magic.h` and `statfs` are available. The public API surface includes `stress_fs_temp_path_get`, `stress_fs_temp_path_check`, `stress_fs_make_filename`, `stress_fs_size_get`, `stress_fs_available_inodes_get`, `stress_fs_usage_bytes`, `stress_fs_nonblocking_set`, `stress_fs_temp_filename*`, `stress_fs_temp_dir*`, `stress_fs_file_write`, `stress_fs_file_read`, `stress_fs_discard`, `stress_fs_max_file_limit_get`, `stress_fs_file_limit_get`, `stress_fs_bad_fd_get`, `stress_fs_pipe_check`, `stress_fs_max_pipe_size_get`, `stress_fs_dirent_list_free`, `stress_fs_dirent_list_prune`, `stress_fs_read`, `stress_fs_write`, `stress_fs_fdinfo_read`, `stress_fs_extents_get`, `stress_fs_info_get`, `stress_fs_type_get`, `stress_fs_close_fds`, `stress_fs_file_rw_hint_short`, `stress_fs_chattr_flags_unset`, `stress_fs_clean_dir`, and `stress_fs_drop_caches`.

Temp-name generation is intentionally robust against small filesystem name limits: `stress_fs_temp_hash_truncate` checks `statvfs(...).f_namemax` and replaces oversized directory or file names with a base-36 encoding of a 64-bit hash derived from Jenkins and PJW hashes. `stress_fs_temp_filename` and `stress_fs_temp_dir` include program name, stressor name, PID, instance, and optional magic to isolate stressor output.

## Control Flow

Most helpers are direct wrappers around one filesystem operation with validation and fallback. Capacity functions read `statvfs` from the configured temp path. Limit probes combine `getrlimit`, `/proc/sys/fs/file-max`, `sysconf(_SC_OPEN_MAX)`, and `getdtablesize` where available. `stress_fs_max_file_rlimit` uses binary search and temporary `setrlimit` calls to discover the largest possible `RLIMIT_NOFILE`, while `stress_fs_file_limit_get` subtracts open descriptor count using `/proc/self/fd` or a fallback scan.

Directory cleanup is recursive but guarded. `stress_fs_clean_dir` computes the expected temp directory, checks access, then calls `stress_fs_clean_dir_files`. The recursive cleanup refuses null paths, symlinks, paths containing `..`, and paths outside the configured temp root. It uses `scandir` with a dot-entry filter, removes immutable/chattr flags, attempts `swapoff` for names containing `swap`, unlinks regular files and symlinks, and removes directories on unwind.

## State And Persistence Behavior

State is mostly external filesystem state. Temporary directories and files persist until the owning stressor removes them or `stress_fs_clean_dir` reclaims leftovers after abnormal termination. `stress_fs_max_pipe_size_get` caches the discovered maximum pipe size in a static variable. Filesystem type formatting uses static buffers for unknown names and return strings, so these results are not reentrant. `stress_fs_drop_caches` affects global Linux VM cache state through `/proc/sys/vm/drop_caches` after `sync`.

## Dependencies And Integration Points

The file depends on stress-ng globals and helpers such as `g_prog_name`, `stress_setting_get`, `stress_uint64_to_str`, logging functions, hash functions, sort comparison helpers, shim wrappers, and memory helpers. It integrates directly with Linux `/proc`, `/sys`, ioctls such as `FS_IOC_FIEMAP`, `FS_IOC_SETFLAGS`, `F_SET_FILE_RW_HINT`, `F_SETPIPE_SZ`, and cross-platform `statvfs`/`statfs` APIs. It is used by CPU ignition, memory management, process diagnostics, stressor temp-file setup, and option parsing for maximum file descriptors.

## Risks And Test Signals

High-risk paths are recursive cleanup, rlimit probing, and global kernel toggles. Cleanup must never escape the configured temp root or follow symlinks. Rlimit discovery temporarily changes process limits and can behave differently under containers, shells, and restricted users. Linux-only ioctls and `/proc` files must degrade gracefully. Useful test signals include temp-path accessibility failures, hashed long names on constrained filesystems, cleanup of immutable files and swap files, correct dot-entry pruning, short-read/short-write behavior, descriptor closing with `close_range`, `drop_caches` permission failures, and filesystem type strings on Linux and BSD.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-filesystem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-filesystem.h -->
# sources/test-tools/stress-ng/core-filesystem.h

## Purpose

This header declares the filesystem utility contract used by stress-ng core code and stressors. It also defines cache-drop flag constants used to request Linux page-cache, slab-object, or combined cache dropping.

## Important APIs, Types, And Functions

The header exposes temp-path APIs, filename and temp-directory construction, filesystem sizing and inode queries, robust file read/write wrappers, file descriptor and pipe helpers, directory entry utilities, filesystem type reporting, fd closing, write-lifetime hints, chattr cleanup, recursive temp cleanup, and cache dropping. `STRESS_DROP_CACHE_PAGE_CACHE`, `STRESS_DROP_CACHE_SLAB_OBJECTS`, and `STRESS_DROP_CACHE_ALL` define the accepted `stress_fs_drop_caches` mask.

## Control Flow

Consumers include this header to call filesystem helpers without knowing platform-specific implementation details. Return types consistently report byte counts, boolean predicates, or negative errno-style failures depending on the helper. The APIs are intentionally low-level and leave policy decisions, such as whether a failure is fatal, to the caller.

## State And Persistence Behavior

The declarations cover helpers that read and mutate filesystem state, including temporary directory creation/removal and global Linux cache dropping. The header itself owns no state, but callers must account for implementation-side static caches and non-reentrant static return buffers in filesystem type reporting.

## Dependencies And Integration Points

The header includes `stress-ng.h`, so it depends on project-wide types such as `stress_args_t`, `stress_type_id_t`, and shim-visible platform types. It is consumed by memory, CPU ignition, process diagnostics, stressor implementations, and option parsing.

## Risks And Test Signals

The contract is broad and used throughout stress-ng, so signature changes are high blast radius. Tests should compile on Linux and non-Linux targets, verify drop-cache flags are constrained to declared values, and validate callers handle negative returns from Linux-specific operations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-filesystem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-ftrace.c -->
# sources/test-tools/stress-ng/core-ftrace.c

## Purpose

This file implements optional Linux ftrace function profiling for stress-ng runs. When enabled, it finds the debugfs mount, enables kernel function profiling for the stress-ng PID, records start and stop function counts/times, and reports system-call-looking kernel functions invoked during the stress run.

## Important APIs, Types, And Functions

The Linux implementation is compiled only when libbsd red-black tree support, BSD `sys/tree.h`, `RB_ENTRY`, and Linux are available. `struct rb_node` stores function name, start/end call counts, and start/end microsecond totals. The red-black tree is ordered by function name via `rb_node_cmp`.

Public APIs are `stress_ftrace_start`, `stress_ftrace_stop`, `stress_ftrace_free`, and `stress_ftrace_add_pid`. Internal helpers include `stress_ftrace_debugfs_path_get`, `stress_ftrace_parse_trace_stat_file`, `stress_ftrace_parse_stat_files`, `strace_ftrace_is_syscall`, and `stress_ftrace_analyze`.

## Control Flow

`stress_ftrace_start` exits unless `OPT_FLAGS_FTRACE` is set, initializes the tree, checks `CAP_SYS_ADMIN`, locates debugfs via mounted filesystem inspection, disables profiling, clears and sets `set_ftrace_pid`, enables `function_profile_enabled`, parses initial trace stats, and marks tracing enabled. `stress_ftrace_stop` clears PIDs, disables profiling, parses final trace stats, and analyzes deltas. `stress_ftrace_analyze` walks the tree, computes positive deltas, filters names that look like syscall wrappers, and logs counts and time.

On unsupported builds, exported functions are stubs; `stress_ftrace_start` logs a not-implemented message when requested.

## State And Persistence Behavior

State is process-global: a static red-black tree, a cached debugfs path, and `tracing_enabled`. Kernel tracing state is external and must be restored by disabling profiling and clearing `set_ftrace_pid`. `stress_ftrace_free` frees all tree nodes and should be called during cleanup to avoid leaks.

## Dependencies And Integration Points

This module depends on capabilities, mount enumeration, filesystem file-write helpers, logging, shim string utilities, debugfs layout, and Linux ftrace files under `debugfs/tracing`. It integrates with the global option flag system and process lifecycle around stressor execution.

## Risks And Test Signals

Risks include leaving ftrace enabled, failing under restricted containers, missing debugfs, changed trace-stat formats, out-of-memory while building the tree, and false syscall classification. Useful signals are graceful no-op behavior without capability/debugfs, correct PID filtering, positive delta reporting after a known workload, and cleanup that empties the tree and disables profiling.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-ftrace.h -->
# sources/test-tools/stress-ng/core-ftrace.h

## Purpose

This header exposes the optional ftrace lifecycle used by stress-ng: start tracing, stop and report, free collected data, and add a PID to the ftrace PID filter.

## Important APIs, Types, And Functions

It declares `stress_ftrace_start`, `stress_ftrace_stop`, `stress_ftrace_free`, and `stress_ftrace_add_pid`. No ftrace-specific structs are exposed; implementation details remain private to `core-ftrace.c`.

## Control Flow

Callers can treat the API as safe on all platforms. Unsupported builds provide stubs, so the normal lifecycle can be called unconditionally when ftrace options are enabled.

## State And Persistence Behavior

The header owns no state. The implementation maintains global ftrace collection state and may mutate kernel tracing controls while active.

## Dependencies And Integration Points

The declarations rely on `pid_t` availability through project includes. The API is integrated with command-line option handling and stress run start/stop hooks.

## Risks And Test Signals

The public contract should remain simple and stub-safe. Compile tests on unsupported platforms and runtime tests with and without `OPT_FLAGS_FTRACE` are the main signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-hash.c -->
# sources/test-tools/stress-ng/core-hash.c

## Purpose

This file implements a collection of non-cryptographic hash algorithms and a small chained hash table used by stress-ng utilities. The hashes support stressor workloads, filename truncation, process-name scrambling, machine-id derivation, warn-once keys, and algorithm benchmarking.

## Important APIs, Types, And Functions

Hash functions include Jenkins, PJW, DJB2a, FNV-1a, SDBM, Exim nhash, Murmur3 32-bit, CRC32C, Adler32, multiply/add variants, K&R, Coffin byte and 32-bit endian variants, lose-lose, Knuth, x17, mid5, mulxror64/32, xorror64/32, Sedgwick, and Sobel. The CRC32C implementation uses a static 256-entry lookup table. Murmur3 uses `stress_hash_murmur_32_scramble`.

The hash table API is `stress_hash_create`, `stress_hash_add`, `stress_hash_get`, and `stress_hash_delete`. `HASH_STR` stores the string payload immediately after a `stress_hash_t` node, and buckets are selected with SDBM modulo table size.

## Control Flow

Most hash functions are straight-line loops over nul-terminated strings or fixed lengths, using shim rotations and `memcpy` for unaligned word loads. `stress_hash_add` validates the table and string, checks for an existing bucket entry, allocates a combined node/string block, prepends it to the bucket, and copies the string. `stress_hash_get` computes the same bucket and scans the linked list. `stress_hash_delete` walks each bucket and frees every node.

## State And Persistence Behavior

The hash functions are stateless and deterministic. The hash table persists in heap allocations owned by the caller until `stress_hash_delete`. Entries are unique by exact `strcmp` within a table. The implementation is not internally synchronized; callers must serialize shared use.

## Dependencies And Integration Points

This module depends on core attributes, builtin shims, pragma unroll macros, rotations, and allocation. It is used by filesystem temp-name truncation, helper process-name scrambling, warn-once hashing, machine ID construction, and likely stressor-specific hash tests.

## Risks And Test Signals

These are non-cryptographic hashes; callers must not use them for security. Some functions accept `len` but still stop at nul bytes, while others use fixed-length block loads, so caller expectations matter. Word-load variants must remain safe on unaligned architectures via `shim_memcpy`. Test signals include stable known-vector outputs, empty-string behavior, endian-specific Coffin variants, table duplicate suppression, collision-chain lookup, zero-sized table rejection, and leak-free deletion.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-hash.h -->
# sources/test-tools/stress-ng/core-hash.h

## Purpose

This header defines the public non-cryptographic hash and hash-table API for stress-ng.

## Important APIs, Types, And Functions

`stress_hash_t` is a minimal linked-list node used as the base of stored hash entries. `stress_hash_table_t` owns a bucket array and the bucket count. The header declares table creation/add/get/delete plus all exported 32-bit hash functions.

## Control Flow

The table API is intentionally opaque enough that callers do not need to know bucket layout, but exposed enough that `stress_hash_t` can be embedded or inspected as a linked list node. Hash functions are standalone utilities.

## State And Persistence Behavior

The table object returned by `stress_hash_create` owns heap memory and must be released with `stress_hash_delete`. Hash function calls have no persistent state.

## Dependencies And Integration Points

The header includes `core-attribute.h` for annotations such as `WARN_UNUSED`. It is included by filesystem and helper code and by stressors needing named hash algorithms.

## Risks And Test Signals

API changes affect broad utility code. Compile tests should verify prototypes match implementation, and runtime tests should verify table ownership and duplicate insertion semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-helper.c -->
# sources/test-tools/stress-ng/core-helper.c

## Purpose

This broad helper module centralizes miscellaneous platform, process, formatting, diagnostic, and runtime utilities used across stress-ng. It handles CPU counts, load averages, parent-death signaling, dumpability, timer slack, process names, build/run info, compiler and uname strings, size formatting, executable path discovery, warn-once state, unused UID/PID probing, tty sizing, retry decisions, sysctl/MSR access, process diagnostics, machine ID synthesis, metric initialization, zero-buffer tests, and environment preservation.

## Important APIs, Types, And Functions

Public constants `stress_ascii64` and `stress_ascii32` provide character tables for generated names. System information APIs include `stress_cpus_online_get`, `stress_cpus_configured_get`, `stress_ticks_per_second_get`, `stress_load_average_get`, `stress_cpu_get`, `stress_compiler_get`, `stress_uname_info_get`, `stress_kernel_release_get`, `stress_hostname_length_get`, and `stress_machine_id_get`.

Process and runtime APIs include `stress_parent_died_alarm`, `stress_process_dumpable`, `stress_timer_slack_set`, `stress_proc_name_init`, `stress_proc_name_raw_set`, `stress_proc_name_set`, `stress_proc_name_scramble`, `stress_proc_state_set`, `stress_exec_text_addr`, `stress_is_dev_tty`, `stress_redo_fork`, `stress_process_info`, `stress_no_return`, and `stress_make_it_fail_set`.

Formatting and utility APIs include `stress_munge_underscore`, `stress_strcmp_munged`, `stress_uint64_zero_get`, `stress_null_get`, `stress_little_endian`, `stress_buildinfo`, `stress_yaml_buildinfo`, `stress_runinfo`, `stress_yaml_runinfo`, `stress_uint64_to_str`, `stress_const_optdup`, `stress_warn_once_hash`, `stress_unused_uid_get`, `stress_unused_racy_pid_get`, `stress_clear_warn_once`, `stress_flag_permutation`, `stress_exit_status`, `stress_proc_self_exe_get`, BSD sysctl wrappers, `stress_x86_readmsr64`, `stress_random_small_sleep`, `stress_yield_sleep_ms`, `stress_zero_metrics`, `stress_data_is_not_zero`, and `stress_env_ld_library_path_get`.

## Control Flow

Many getters cache successful results in static variables. Process-name functions either preserve names when `OPT_FLAGS_KEEP_NAME` is set, scramble names when `OPT_FLAGS_RANDPROCNAME` is set, or format names from program/stressor state. Build and run info functions are gated by logging flags or YAML output handles. `stress_warn_once_hash` hashes filename plus line, acquires the shared warn-once lock, linearly probes the shared hash array, and records first use. UID discovery enumerates passwd entries, sorts UIDs, and caches a gap. PID discovery optionally forks and reaps a child, then falls back to random PID probes and `/proc/sys/kernel/pid_max`.

## State And Persistence Behavior

State includes cached CPU counts, tick rate, unused UID, warn-once hashes in `g_shared`, global process name side effects, core dump filter settings, timer slack, kernel warn-once clearing, and static buffers returned by compiler, uname, libc, memory, and formatting helpers. Several helpers intentionally affect the process or kernel-visible state rather than returning pure values.

## Dependencies And Integration Points

The module integrates with git version metadata, capabilities, CPU cache/NUMA helpers, hash functions, sorting, filesystem and memory helpers, logging/YAML output, global option flags, shared memory, locks, random number utilities, shim wrappers, BSD sysctl, Linux `/proc`, Linux `/sys`, `prctl`, `procctl`, uname, sysinfo, pwd database access, and x86 MSR devices. It is a foundational dependency for many other core modules.

## Risks And Test Signals

Risks include non-reentrant static buffers, platform-specific stubs returning zeros, racy unused PID/UID guesses, process-name changes affecting external tooling, and shared warn-once lock availability during early startup. Test signals include stable CPU/load fallbacks, valid YAML output, correct underscore/dash comparison, warn-once suppression across repeated calls, sane size formatting, executable path discovery on each supported OS, fork retry behavior near timeout, process diagnostic output on Linux, and no crashes when optional platform features are absent.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-helper.h -->
# sources/test-tools/stress-ng/core-helper.h

## Purpose

This header exposes stress-ng's general helper API and the `stress_warn_once()` macro. It is the shared declaration point for platform facts, process naming, diagnostics, formatting, sysctl/MSR helpers, and small runtime utilities.

## Important APIs, Types, And Functions

The header declares the exported ASCII tables, CPU and load getters, parent-death and dumpability helpers, timer slack, process name APIs, string munging, zero/null getters, endian checks, build/run info emitters, compiler/uname getters, unimplemented marker, size formatting, option duplication, executable text range and self path lookup, warn-once, unused UID/PID, kernel version, tty width, fork retry, flag permutation, exit-status mapping, BSD sysctl wrappers, x86 MSR reads, sleep/yield helpers, process info dump, machine ID, metric zeroing, zero-buffer check, LD library path preservation, and Linux failure-injection activation.

## Control Flow

The API is intentionally flat and used throughout the codebase. Most functions are safe to call on unsupported platforms because implementation stubs return neutral values, but callers must still check return codes where meaningful.

## State And Persistence Behavior

Several functions mutate process state, global shared memory, kernel controls, or static caches. The header does not own state but exposes APIs whose side effects are significant.

## Dependencies And Integration Points

It includes `stress-ng.h` for project types such as `stress_args_t` and `stress_metrics_t`. The macro `stress_warn_once()` binds call sites to `__FILE__` and `__LINE__`, coupling diagnostics to source locations.

## Risks And Test Signals

Because this is a wide utility header, compatibility is sensitive to prototypes and annotations. Compile coverage across supported platforms and call-site tests for side-effect functions are important.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-ignite-cpu.c -->
# sources/test-tools/stress-ng/core-ignite-cpu.c

## Purpose

This module implements the optional CPU ignition feature, which tries to push CPUs into maximum-performance settings during a stress run and then restore original settings. It manipulates Linux CPU frequency, governor, energy-performance-bias, resume-latency, Intel P-state, cpufreq boost, and `/dev/cpu_dma_latency` controls when available.

## Important APIs, Types, And Functions

`stress_settings_t` describes global sysfs controls with default maximizing values and saved originals. `stress_cpu_setting_t` records per-CPU frequency limits, resume latency, governor, energy performance bias, and a flag mask indicating which controls are usable. Public APIs are `stress_ignite_cpu_start` and `stress_ignite_cpu_stop`; `stress_ignite_cpu_set` applies or restores per-CPU settings and clears flag bits for controls that fail.

## Control Flow

`stress_ignite_cpu_start` opens `/dev/cpu_dma_latency` and writes zero latency if possible, discovers configured CPUs, allocates per-CPU setting storage, reads cpufreq and power-control files, applies global maximizing sysfs settings, saves originals, and forks a child daemon. The child sets parent-death alarm and process name, then once per second reapplies global settings and per-CPU max-frequency/performance settings while `stress_continue_flag()` remains true.

`stress_ignite_cpu_stop` closes the latency fd, kills and waits for the child, restores per-CPU settings using saved values, frees CPU state, restores global sysfs settings, and clears `enabled`.

## State And Persistence Behavior

State is global and process-lifetime scoped: `cpu_settings`, `pid`, `enabled`, `max_cpus`, and `latency_fd`. It also temporarily mutates persistent kernel/sysfs tunables and must restore saved values on stop. If start returns early after partial changes or the process is killed without stop, system settings could remain modified.

## Dependencies And Integration Points

The module depends on filesystem read/write helpers, configured CPU count, parent-death alarm, process naming, random governor choice, global continue flag, and kill/wait helpers. It is Linux/sysfs oriented, with x86-specific global settings for Intel P-state.

## Risks And Test Signals

Risks are high because it writes power-management controls. Permission failures, missing sysfs files, hotplugged CPUs, malformed sysfs values, and incomplete restoration are key edge cases. Test signals include no-op behavior without writable controls, restoration after start/stop, child death on parent exit, correct cleanup of saved setting allocations, and no repeated logging for expected permission failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-ignite-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-ignite-cpu.h -->
# sources/test-tools/stress-ng/core-ignite-cpu.h

## Purpose

This header exposes the CPU ignition lifecycle for starting and stopping maximum-performance CPU setting maintenance.

## Important APIs, Types, And Functions

It declares `stress_ignite_cpu_start` and `stress_ignite_cpu_stop`. All sysfs-specific data structures and state are private to the implementation.

## Control Flow

Callers start ignition before stress work and stop it during teardown. The API is side-effect focused and returns no status, so failures are intentionally best-effort.

## State And Persistence Behavior

The implementation maintains global state and external sysfs side effects. The header itself owns none.

## Dependencies And Integration Points

Consumers need only include the header and link the implementation. The feature integrates with global stress run lifecycle.

## Risks And Test Signals

The main API risk is failing to pair start and stop. Tests should verify repeated start calls are idempotent and stop restores state after partial starts.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-ignite-cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-interrupts.c -->
# sources/test-tools/stress-ng/core-interrupts.c

## Purpose

This file records and reports selected hardware/kernel interrupt counters before and after stressor execution. It detects failure-indicating interrupts such as machine checks, deferred APIC errors, IO-APIC errors, miscounts, and ARM unhandled interrupt errors, and it can summarize TLB shootdown/IPI activity from `/proc/interrupts`.

## Important APIs, Types, And Functions

`stress_interrupt_info_t` maps interrupt label strings to failure policy, logging function, and description. Public APIs are `stress_interrupts_start`, `stress_interrupts_stop`, `stress_interrupts_check_failure`, `stress_interrupts_dump`, and `stress_interrupts_tlb`. Internal helpers include `stress_interrupts_counter_set`, `stress_interrupts_count`, `stress_interrupt_tolower`, and Linux-only `stress_interrupts_parse_field`.

## Control Flow

Start and stop both call `stress_interrupts_count` with different slots. On x86, SMI count may be read from `MSR_SMI_COUNT` for the current CPU. The module then parses `/proc/interrupts`, finds known labels, sums per-CPU numeric columns, and stores start or stop counters. Failure checking compares deltas for entries marked `check_failure` and sets the caller's return code to `EXIT_FAILURE` when deltas are positive. Dumping walks stressor list items, averages positive deltas across instances, logs via the interrupt-specific logging function, and emits YAML keys derived from descriptions.

## State And Persistence Behavior

Counter state is stored in caller-provided `stress_interrupts_t` arrays, typically per stressor instance. The module has a static interrupt metadata table but no mutable global state. It reads kernel counters and does not reset them.

## Dependencies And Integration Points

It depends on architecture detection, x86 MSR reads from `core-helper.c`, stressor list/stat types, logging/YAML output, and Linux `/proc/interrupts`. `STRESS_INTERRUPTS_MAX` must be large enough for the metadata table.

## Risks And Test Signals

Parsing `/proc/interrupts` is format-sensitive and architecture-dependent. Counter wrap or CPU hotplug can affect deltas. Failure policy can produce false positives on hosts with pre-existing hardware issues. Test signals include correct summing of synthetic interrupt lines, no crash with missing `/proc/interrupts`, x86 MSR failure fallback, YAML output only when deltas exist, and failure return changes only for configured failure labels.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-interrupts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-interrupts.h -->
# sources/test-tools/stress-ng/core-interrupts.h

## Purpose

This header declares interrupt accounting and reporting helpers used around stressor execution.

## Important APIs, Types, And Functions

It exposes start/stop counter collection, failure checking, YAML/report dumping, and TLB/IPI summary collection. It relies on `stress_interrupts_t` and `stress_list_item_t` from project-wide definitions.

## Control Flow

Callers collect counters at run boundaries, check failure status after stopping, and optionally dump aggregate reports.

## State And Persistence Behavior

Counter storage is caller-owned. The implementation reads kernel counters but does not mutate them.

## Dependencies And Integration Points

The header integrates with stressor stats and YAML reporting. It is used by run orchestration to detect system-level interrupt failures.

## Risks And Test Signals

The header contract depends on `STRESS_INTERRUPTS_MAX` matching the implementation metadata. Compile-time assertions and per-instance stat allocation tests are useful.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-interrupts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-io-priority.c -->
# sources/test-tools/stress-ng/core-io-priority.c

## Purpose

This module parses ionice class names and applies Linux I/O priority settings through the `ioprio_set` syscall when available.

## Important APIs, Types, And Functions

`stress_io_priority_ionice_class_get` maps strings such as `idle`, `besteffort`, `be`, `realtime`, and `rt` to `IOPRIO_CLASS_*` constants. `stress_io_priority_set` validates class and level, normalizes defaults, and calls `shim_ioprio_set(IOPRIO_WHO_PROCESS, 0, IOPRIO_PRIO_VALUE(...))` on systems with `__NR_ioprio_set`; otherwise it is a no-op.

## Control Flow

Class parsing exits the process on invalid input after printing available options. Priority setting returns success for `UNDEFINED`, clamps idle to level zero with an informational message, rejects invalid realtime/besteffort levels outside 0-7, and reports syscall failures except `ENOSYS`.

## State And Persistence Behavior

The module changes the current process I/O priority. It owns no persistent internal state. Unsupported systems leave priority unchanged.

## Dependencies And Integration Points

It depends on constants declared in `core-io-priority.h`, logging functions, shim syscall wrappers, and command-line option parsing that supplies class and level values.

## Risks And Test Signals

Risks include terminating on parse errors, permission failures for realtime priority, and unsupported kernels. Test signals include correct mapping aliases, invalid class diagnostics, level validation, no-op behavior without syscall support, and preservation of success when syscall returns `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-io-priority.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-io-priority.h -->
# sources/test-tools/stress-ng/core-io-priority.h

## Purpose

This header supplies Linux I/O priority constants when libc does not provide them and declares the ionice parsing and application API.

## Important APIs, Types, And Functions

It defines `IOPRIO_CLASS_RT`, `IOPRIO_CLASS_BE`, `IOPRIO_CLASS_IDLE`, `IOPRIO_WHO_*`, and `IOPRIO_PRIO_VALUE` conditionally. It declares `stress_io_priority_ionice_class_get` and `stress_io_priority_set`.

## Control Flow

Callers parse class names before applying a class/level pair. The macro `IOPRIO_PRIO_VALUE` encodes class and data bits in Linux's expected format.

## State And Persistence Behavior

The header has no state. The implementation mutates process I/O priority where supported.

## Dependencies And Integration Points

It bridges stress-ng option parsing with Linux block scheduler priority APIs.

## Risks And Test Signals

The key compatibility risk is keeping fallback constants aligned with Linux headers. Compile tests against old and new libc/kernel headers are useful.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-io-priority.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-io-uring.c -->
# sources/test-tools/stress-ng/core-io-uring.c

## Purpose

This file is currently a minimal compile-time integration shim for Linux `io_uring` headers. It includes `config.h` and conditionally includes `<linux/io_uring.h>` when building on Linux with header availability.

## Important APIs, Types, And Functions

No functions or exported symbols are implemented in this file. Its role is to make io_uring header availability part of the build and provide a home for future core io_uring helpers.

## Control Flow

The only control flow is preprocessor gating: Linux plus `HAVE_LINUX_IO_URING_H` includes the kernel header, otherwise the translation unit is effectively empty.

## State And Persistence Behavior

There is no runtime state and no side effect.

## Dependencies And Integration Points

It depends on configure-time feature detection. It integrates with the build system rather than runtime stressor control flow.

## Risks And Test Signals

The main risk is build portability when kernel headers are absent or incompatible. Test signals are successful compilation on Linux with and without `linux/io_uring.h` and on non-Linux platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-io-uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-job.c -->
# sources/test-tools/stress-ng/core-job.c

## Purpose

This file parses stress-ng job files into ordinary stress-ng option arguments. Job files can also specify whether contained jobs should run sequentially or in parallel.

## Important APIs, Types, And Functions

`MAX_ARGS` limits parsed tokens per line. `RUN_SEQUENTIAL` and `RUN_PARALLEL` track mutually exclusive job run modes. Internal helpers are `stress_str_chop`, `stress_parse_run`, and `stress_parse_error`. The public API is `stress_job_parse_file`.

## Control Flow

`stress_job_parse_file` opens an explicit jobfile or consumes `argv[optind]`, uses `setjmp(g_error_env)` to catch option parser failures, reads lines, removes newline and comments, tokenizes on blanks, rejects recursive `job` commands, handles `run sequential|seq|sequentially` and `run parallel|par|together`, prefixes the command token with `--`, and calls `stress_opts_parse` in job mode. It returns zero on success and `-1` on parse/open errors.

## State And Persistence Behavior

The parser mutates global option flags for sequential/parallel mode and advances `optind` when consuming an implicit jobfile. It allocates a temporary `--option` string per parsed line and frees it immediately. Parsed options persist through the global stress-ng settings system.

## Dependencies And Integration Points

It depends on global `g_error_env`, `g_opt_flags`, `OPT_FLAGS_SEQUENTIAL`, `OPT_FLAGS_ALL`, `stress_opts_parse`, and libc file/token APIs. It integrates with command-line parsing before stressor execution.

## Risks And Test Signals

The tokenizer does not implement quoting, so paths or arguments containing spaces are not supported. Invalid job recursion and conflicting run modes must remain guarded. Test signals include comments and blank lines, implicit and explicit file opening, sequential/parallel mode toggles, invalid options through `setjmp`, out-of-memory handling, and line-numbered diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-job.h -->
# sources/test-tools/stress-ng/core-job.h

## Purpose

This header declares the stress-ng job-file parser entry point.

## Important APIs, Types, And Functions

It exposes `stress_job_parse_file(const int argc, char **argv, const char *jobfile)`.

## Control Flow

Callers invoke the parser during option processing. Passing `NULL` for `jobfile` allows the implementation to consume the next command-line argument as a job file.

## State And Persistence Behavior

The implementation can update global option state and `optind`. The header owns no state.

## Dependencies And Integration Points

The parser integrates with command-line option handling and job scripts.

## Risks And Test Signals

Signature stability is the main concern. Tests should cover `NULL` and explicit jobfile modes.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-killpid.c -->
# sources/test-tools/stress-ng/core-killpid.c

## Purpose

This module provides safe process termination and reaping helpers for stress-ng child processes. It centralizes SIGKILL memory-release optimization on Linux, guards against killing PID 0/1/self, and provides multi-PID kill/wait flows.

## Important APIs, Types, And Functions

Public functions are `stress_kill_pid`, `stress_kill_pid_wait`, `stress_kill_sig`, `stress_wait_until_reaped`, `stress_kill_and_wait`, `stress_kill_many`, `stress_wait_many`, and `stress_kill_and_wait_many`. On Linux with `process_mrelease`, `stress_kill_pid` opens a pidfd, sends SIGKILL, then calls `process_mrelease` to reclaim memory quickly.

## Control Flow

Single-process termination sends the requested signal, then `stress_wait_until_reaped` loops on `waitpid`, handles interrupted waits, checks process existence with `kill(pid, 0)`, escalates when global continue has stopped, optionally accounts forced-killed bogo ops after repeated failures, and emits process diagnostics after a long unkillable interval. Multi-PID helpers send signals to all valid PIDs first, then reap each child to avoid serial kill delays.

## State And Persistence Behavior

The module owns no static state. It changes child process state and can update stressor metrics via `stress_force_killed_bogo`. It may print process diagnostics for stuck children.

## Dependencies And Integration Points

It depends on shim kill/wait/pidfd/process_mrelease wrappers, global continue flag, sleep/yield helpers, logging, process diagnostics, and `stress_pid_t` arrays used by stressor orchestration.

## Risks And Test Signals

Risks include accidentally targeting protected PIDs, indefinite waits for uninterruptible children, and platform-specific pidfd/process_mrelease behavior. Test signals include self/PID1 guard behavior, SIGTERM and SIGKILL paths, wait return status propagation, EINTR handling, multi-child kill-before-wait ordering, and graceful fallback without Linux pidfd support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-killpid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-killpid.h -->
# sources/test-tools/stress-ng/core-killpid.h

## Purpose

This header declares process kill and wait helpers used by stress-ng lifecycle management.

## Important APIs, Types, And Functions

It exposes single-PID helpers, wait-until-reaped, kill-and-wait, and array-based kill/wait helpers. It references `stress_args_t` and `stress_pid_t` project types.

## Control Flow

Callers can use the combined helpers for normal teardown or separate kill and wait phases for bulk child cleanup.

## State And Persistence Behavior

The implementation mutates process state but owns no persistent internal state.

## Dependencies And Integration Points

The API integrates with stressor child process tracking, failure accounting, and cleanup paths.

## Risks And Test Signals

The most important contract is guarding invalid/sensitive PIDs while still reliably reaping children. Tests should exercise both individual and many-PID functions.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-killpid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-klog.c -->
# sources/test-tools/stress-ng/core-klog.c

## Purpose

This Linux-specific module monitors `/dev/kmsg` during stress runs and reports kernel messages that indicate errors, lockups, OOM events, CPU throttling, hung tasks, or warnings. It can mark the overall run unsuccessful if kernel error messages are observed.

## Important APIs, Types, And Functions

Public APIs are `stress_klog_start` and `stress_klog_stop`. Internal helpers include `stress_klog_err_no_exceptions`, `stress_klog_kernel_cmdline`, and `stress_klog_convert_nl`. The static `err_exceptions` list suppresses known benign or noisy kernel messages.

## Control Flow

`stress_klog_start` resets `g_shared->klog_errors`, checks `OPT_FLAGS_KLOG_CHECK`, opens `/dev/kmsg`, forks a monitor child, seeks to the end, then reads new log messages. The child parses priority, facility, and timestamp, normalizes escaped newlines, classifies messages by content and priority, logs info or errors, dumps kernel command line once, rate-limits process dumps on lockups, increments shared error count for relevant errors, and exits when the kmsg stream ends. `stress_klog_stop` checks error count, marks `*success = false` if errors occurred, kills the monitor child, and resets shared state.

## State And Persistence Behavior

State includes static `klog_pid`, a one-shot kernel cmdline dump flag, and `g_shared->klog_errors`. The monitor child reads global kernel log state but does not mutate kernel logging. The success flag passed to stop is caller-owned.

## Dependencies And Integration Points

It depends on filesystem reads, kill/wait helpers, process naming, parent-death alarm, scheduler policy setting, process dumps, logging, global shared state, and `/dev/kmsg`. Non-Linux builds compile to no-op behavior.

## Risks And Test Signals

Risks include permission-denied access to `/dev/kmsg`, false positives/negatives in string classification, noisy kernel logs from unrelated system activity, and monitor child cleanup. Test signals include no-op without option, graceful open failure, exception filtering, escaped newline conversion, error count propagation to `success`, and child termination on stop.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-klog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-klog.h -->
# sources/test-tools/stress-ng/core-klog.h

## Purpose

This header declares kernel log monitoring lifecycle functions.

## Important APIs, Types, And Functions

It exposes `stress_klog_start` and `stress_klog_stop(bool *success)`.

## Control Flow

Callers start monitoring before stress execution and stop it afterward, allowing the implementation to update the run success flag.

## State And Persistence Behavior

The implementation owns monitor-child and shared error-count state. The header owns no state.

## Dependencies And Integration Points

The API integrates with global option flags, shared memory, and run success reporting.

## Risks And Test Signals

Callers must pass a valid success pointer on Linux when monitoring is enabled. Tests should cover success flag changes when shared error counts are present.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-klog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-limit.c -->
# sources/test-tools/stress-ng/core-limit.c

## Purpose

This module pushes process resource limits toward their maximums, or applies user-specified overrides for selected memory-related limits. It helps stress-ng exercise systems without being constrained by conservative inherited shell limits.

## Important APIs, Types, And Functions

`stress_rlimit_t` maps `RLIMIT_*` resources to optional stress-ng setting names. `stress_limit_set` applies an override from settings when available, rounding down to page size, otherwise sets soft limit equal to hard limit. The public API is `stress_limit_max_set`.

## Control Flow

`stress_limit_max_set` iterates the compile-time `limits` array and calls `stress_limit_set` for each resource. Afterward, it applies an explicit `"max-fd"` setting to `RLIMIT_NOFILE` when configured. All `setrlimit` failures are ignored by design.

## State And Persistence Behavior

The module mutates process resource limits. These changes persist for the process and inherited children. It has no internal mutable state.

## Dependencies And Integration Points

It depends on `stress_setting_get`, page-size lookup, shim resource type definitions, and command-line settings such as `limit-as`, `limit-data`, `limit-stack`, and `max-fd`.

## Risks And Test Signals

Risks include over-tightening limits through user overrides, failures under privilege/container restrictions, and page-size rounding to zero for very small values. Test signals include successful soft-to-hard promotion, override rounding, ignored failures, and `max-fd` application.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-limit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-limit.h -->
# sources/test-tools/stress-ng/core-limit.h

## Purpose

This header declares the resource-limit maximization entry point.

## Important APIs, Types, And Functions

It exposes `stress_limit_max_set`.

## Control Flow

Callers invoke it during setup before launching stress workloads or child processes.

## State And Persistence Behavior

The implementation mutates current process rlimits. The header owns no state.

## Dependencies And Integration Points

It integrates with option settings for resource-limit overrides.

## Risks And Test Signals

The main API signal is that it is best-effort and returns no status, so tests should inspect resulting limits rather than return codes.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-limit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-lock.c -->
# sources/test-tools/stress-ng/core-lock.c

## Purpose

This file implements stress-ng's shared lock abstraction. It selects one available primitive at compile time, maps a shared lock pool, allocates lock handles from that pool, and exposes generic create/destroy/acquire/release functions.

## Important APIs, Types, And Functions

`stress_lock_u_t` stores the selected primitive: atomic spin flag, pthread spinlock, pthread mutex, C11 `mtx_t`, Linux PI futex, POSIX semaphore, or SysV semaphore. `stress_lock_t` wraps a magic value and the union. `stress_lock_funcs_t` holds method name and function pointers. Public APIs are `stress_lock_mem_map`, `stress_lock_mem_unmap`, `stress_lock_create`, `stress_lock_destroy`, `stress_lock_acquire`, `stress_lock_acquire_relax`, and `stress_lock_release`.

`stress_lock_get` and `stress_lock_put` allocate/free entries from the shared array under `stress_lock_big_lock`. Atomic spinlock acquisition includes optional architecture-specific pause/yield backoff and aborts with `EAGAIN` if the global run has stopped for more than five seconds.

## Control Flow

Compile-time `LOCK_METHOD_*` macros select the first supported implementation through `#if/#elif`. `stress_lock_mem_map` allocates an anonymous shared mapping sized for `STRESS_LOCK_MAX`, names it when possible, initializes slot zero as the big lock, and sets its magic. `stress_lock_create` obtains a free slot and initializes the selected primitive. Destroy deinitializes and returns the slot to the pool. Acquire/release validate magic before dispatching to the selected primitive.

## State And Persistence Behavior

The shared lock pool persists in an anonymous shared mapping across forked processes until `stress_lock_mem_unmap`. Slot magic values track allocation state. SysV semaphore locks may create kernel semaphore IDs that must be removed during deinit. The big lock serializes lock pool allocation and free operations.

## Dependencies And Integration Points

The module depends on architecture pause helpers, pthread/semaphore/futex/C11 thread availability, mmap helpers, memory anon naming, global continue flag, scheduler yield, and logging. The warn-once system and many shared stress-ng structures depend on this lock abstraction.

## Risks And Test Signals

Risks include no available lock primitive, process-shared semantics not actually supported by the selected primitive, deadlocks in the big lock, stale magic after unmap, semaphore leaks, and unfair atomic spin behavior. Test signals include map/unmap lifecycle, create/destroy pool reuse, invalid-handle errors, cross-process lock exclusion, relaxed acquire backoff under contention, and fallback failure when no primitive is compiled.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-lock.h -->
# sources/test-tools/stress-ng/core-lock.h

## Purpose

This header exposes the generic lock pool and lock-handle API.

## Important APIs, Types, And Functions

It declares shared lock memory map/unmap plus create, destroy, acquire, relaxed acquire, and release functions. Lock handles are opaque `void *` values.

## Control Flow

Callers must map lock memory before creating locks, then create handles, use acquire/release around shared state, destroy handles, and unmap during shutdown.

## State And Persistence Behavior

The implementation stores locks in shared anonymous memory and may create kernel semaphore state depending on selected primitive.

## Dependencies And Integration Points

The API supports shared-memory subsystems such as warn-once and metrics synchronization.

## Risks And Test Signals

The lifecycle order is critical. Tests should verify create fails before mapping and that destroy/release reject invalid handles.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-log.c -->
# sources/test-tools/stress-ng/core-log.c

## Purpose

This module implements stress-ng logging: stdout/stderr/log-file/syslog routing, severity filtering, timestamping, brief output, skip-message handling, per-process block buffering, and failure-count driven abort behavior.

## Important APIs, Types, And Functions

Static state includes `abort_fails`, `abort_msg_emitted`, `log_fd`, and a per-process `pr_msg_buf_t` that accumulates block-buffered messages. Public APIs are `pr_fd`, `pr_block_begin`, `pr_block_end`, `pr_fail_check`, `pr_yaml`, `pr_closelog`, `pr_openlog`, and severity functions `pr_dbg`, `pr_dbg_skip`, `pr_inf`, `pr_inf_skip`, `pr_err`, `pr_err_skip`, `pr_fail`, `pr_tidy`, `pr_warn`, `pr_warn_skip`, and `pr_metrics`. Internal helpers include `pr_log_write_buf_fd`, `pr_log_write_buf`, `pr_log_write`, and `pr_msg`.

## Control Flow

Severity wrappers build a `va_list` and call `pr_msg`. `pr_msg` checks `g_pr_log_flags`, optional skip suppression in the wrapper functions, formats the message with optional timestamp and prefix, writes to the log file and selected stdout/stderr fd, and mirrors non-debug messages to syslog where enabled. `pr_fail` increments `abort_fails`; after `ABORT_FAILURES` failures, one abort message is emitted and the global continue flag is cleared. `pr_block_begin/end` buffer messages for a matching process and flush them as one write unless lockless logging is enabled. `pr_yaml` writes formatted YAML to a specific file handle.

## State And Persistence Behavior

State includes global log flags, optional log file descriptor, failure abort counters, a per-process block buffer, and syslog use through libc. Log file output persists to the configured file until `pr_closelog`. Five `pr_fail` messages can alter global run state by clearing the continue flag, and `pr_fail_check` converts a successful return code to failure if the abort threshold was reached.

## Dependencies And Integration Points

It depends on core logging flags from `core-log.h`, global program/log state, builtin shims, syslog support, time formatting, and shared interrupt state for `pr_tidy` signal-aware severity selection. It is used by nearly every other module for diagnostics and result reporting.

## Risks And Test Signals

Risks include large buffered blocks consuming memory, partial writes to terminal or log files, timestamp formatting errors, unintended run cancellation after repeated `pr_fail`, and stdout/stderr routing mistakes. Test signals include flag filtering, skip-silent behavior, brief mode prefixes, timestamp output, file open/close and fsync, syslog calls under enabled flags, YAML formatting, block buffering, and abort threshold propagation through `pr_fail_check`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-log.h -->
# sources/test-tools/stress-ng/core-log.h

## Purpose

This header defines logging flag bits and declares stress-ng logging functions.

## Important APIs, Types, And Functions

`PR_LOG_FLAGS_*` constants control error, info, debug, fail, warn, metrics, stdout/stderr, brief, lockless, skip-silent, timestamp, and syslog behavior. `PR_LOG_FLAGS_ALL` groups the normal message classes. The header declares file descriptor lookup, block locking, failure checking, YAML output, log open/close, and severity-specific printf-style logging functions.

## Control Flow

Callers use severity functions rather than writing directly. The implementation applies global filters and output routing.

## State And Persistence Behavior

The implementation uses global flags, optional log file state, shared failure state, and log locks. The header owns no state.

## Dependencies And Integration Points

It includes `core-attribute.h` for printf-format annotations and is included throughout stress-ng.

## Risks And Test Signals

Changing flag values can break option semantics. Compile checks for format annotations and runtime checks for each flag class are useful.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-madvise.c -->
# sources/test-tools/stress-ng/core-madvise.c

## Purpose

This file centralizes `madvise` option lists and helper calls for applying memory advice to mappings or to every mapping of a process. It supports random advice stress, common hint wrappers, THP collapse, no-hugepage behavior, KSM mergeability, and process-wide page advice on Linux.

## Important APIs, Types, And Functions

When `HAVE_MADVISE` is set, `madvise_options` and `madvise_options_elements` expose the supported advice constants. `madvise_random_options` is a safer random subset that excludes advice likely to zero or invalidate data used for checksum validation. Public functions are `stress_advice_check`, `stress_madvise_randomize`, `stress_madvise_random`, `stress_madvise_mergeable`, `stress_madvise_collapse`, `stress_madvise_willneed`, `stress_madvise_nohugepage`, and `stress_madvise_pid_all_pages`.

## Control Flow

Simple wrappers call `madvise` only when both `HAVE_MADVISE` and the target `MADV_*` constant are available; otherwise they return success. `stress_madvise_randomize` is gated by `OPT_FLAGS_MMAP_MADVISE`, selects a random safe advice, sanitizes it through `stress_advice_check`, and applies it. `stress_madvise_pid_all_pages` parses `/proc/$pid/maps`, applies one or random advice values to each mapping or page, and touches readable file-backed pages to pull them in.

## State And Persistence Behavior

The module owns no mutable state. It changes kernel VM advice for mappings in the current or target process. Process-wide advice can affect page residency, huge page behavior, fork inheritance, dump behavior, and reclaim behavior depending on advice.

## Dependencies And Integration Points

It depends on option flags, random utilities, memory page-size lookup, Linux `/proc/$pid/maps`, and platform `MADV_*` availability. It is used by mmap and memory stressors to vary kernel VM paths.

## Risks And Test Signals

Risks include destructive advice zeroing pages, SIGSEGV-inducing guard advice, parsing maps with unusual path fields, and advising ranges not valid in the current process. Test signals include no-op behavior without `OPT_FLAGS_MMAP_MADVISE`, wrapper success on unsupported advice, correct exclusion of dangerous random advice, and safe handling of inaccessible process maps.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-madvise.h -->
# sources/test-tools/stress-ng/core-madvise.h

## Purpose

This header exposes stress-ng's memory-advice option arrays and helper APIs.

## Important APIs, Types, And Functions

It declares `madvise_options`, `madvise_options_elements`, advice sanitization, random advice, common advice wrappers, and process-wide page advice.

## Control Flow

Callers can enumerate available advice values or apply named helpers without duplicating platform preprocessor checks.

## State And Persistence Behavior

The implementation mutates VM advice on mappings but owns no persistent state.

## Dependencies And Integration Points

The API integrates with mmap/memory stressors and option flags controlling madvise behavior.

## Risks And Test Signals

Callers must understand which advice may alter data or mapping behavior. Tests should cover array availability only when `HAVE_MADVISE` is defined and wrapper no-op behavior otherwise.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-madvise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-memory.c -->
# sources/test-tools/stress-ng/core-memory.c

## Purpose

This file provides cross-platform memory information and memory-management helpers for stress-ng. It reports page size, free/total memory and swap, SHMALL, low-memory conditions, physical memory size, allocation usage, anonymous VMA names, swapoff, address readability, per-PID memory usage, KSM toggling, and kernel memory compaction.

## Important APIs, Types, And Functions

Public APIs are `stress_memory_page_size_get`, `stress_memory_info_get`, `stress_memory_limits_get`, `stress_memory_free_get`, `stress_memory_ksm_merge`, `stress_memory_low_check`, `stress_memory_phys_size_get`, `stress_memory_usage_get`, `stress_memory_address_align`, `stress_memory_anon_name_set`, `stress_memory_swap_off`, `stress_memory_readable`, `stress_memory_usage_by_pid_get`, and `stress_memory_compact`.

## Control Flow

`stress_memory_info_get` tries Linux `sysinfo`, then FreeBSD sysctl counters, NetBSD `uvmexp2`, and macOS Mach VM stats, falling back to zeros and `-1`. `stress_memory_low_check` lazily computes an OOM avoidance threshold, compares current and previous free memory/swap, checks requested allocation headroom, and if low memory is detected drops caches and enables KSM merge. `stress_memory_compact` writes to `/proc/sys/vm/compact_memory` only when the option is enabled, and disables repeated attempts after failure.

## State And Persistence Behavior

Static state caches page size, previous free memory/swap, low-memory threshold, KSM previous flag, and compaction skip status. External side effects include KSM enabling, cache dropping, VM compaction, swapoff, anonymous VMA naming, and pipe-based memory readability probes.

## Dependencies And Integration Points

The module depends on filesystem helpers for `/proc` and `/sys` reads/writes, BSD sysctl helpers, formatting/logging, option settings (`oom-avoid-bytes`, `compact-memory`), page-size consumers, and platform APIs such as sysinfo, Mach host statistics, prctl `PR_SET_VMA`, and swapoff.

## Risks And Test Signals

Risks include overflow in memory unit multiplication, platform counters with different semantics, low-memory false positives, global side effects from cache dropping/KSM/compaction, and pipe writes with very large readable checks. Test signals include page-size fallback, Linux/BSD/macOS memory info paths, low-memory threshold behavior, KSM write suppression when flag unchanged, per-PID statm conversion, swapoff EINTR retry, and compaction failure suppression.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-memory.h -->
# sources/test-tools/stress-ng/core-memory.h

## Purpose

This header declares memory information, accounting, and VM helper functions.

## Important APIs, Types, And Functions

It exposes page-size, memory/swap info, memory limit info, free-memory string, KSM, low-memory check, physical size, usage logging, address alignment, anonymous VMA naming, swapoff, readability, per-PID memory usage, and compaction APIs.

## Control Flow

Callers use these helpers to size stress workloads, avoid OOM, label mappings, and invoke optional kernel VM maintenance.

## State And Persistence Behavior

The implementation uses static caches and may mutate kernel VM controls. The header owns no state.

## Dependencies And Integration Points

It includes `stress-ng.h` for project types and is consumed by filesystem, mmap, shared-memory, and stressor code.

## Risks And Test Signals

The include guard is named `CORE_MEMORY_H_H`; changing it could affect duplicate-include behavior. Tests should compile broad consumers and validate no-op behavior for unsupported VM APIs.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mincore.c -->
# sources/test-tools/stress-ng/core-mincore.c

## Purpose

This module ensures memory ranges are resident by touching pages, preferably using `madvise(MADV_POPULATE_READ/WRITE)` or `mincore` to avoid unnecessary writes. It supports interruptible and non-interruptible page touching.

## Important APIs, Types, And Functions

Public APIs are `stress_mincore_touch_pages` and `stress_mincore_touch_pages_interruptible`. Internal helpers are `stress_mincore_touch_pages_slow` and `stress_mincore_touch_pages_generic`.

## Control Flow

Both public functions are gated by `OPT_FLAGS_MMAP_MINCORE`. The non-interruptible path first tries `MADV_POPULATE_READ` followed by `MADV_POPULATE_WRITE` where available. The generic path computes page count, allocates a residency vector, calls `shim_mincore` on a page-aligned start, and only increments/decrements pages not already resident. If `mincore` is absent or fails, it falls back to touching all pages. Interruptible variants stop loops when `stress_continue_flag()` clears.

## State And Persistence Behavior

The module has no persistent state. It temporarily modifies bytes by incrementing and then decrementing them to fault pages in, preserving original values if no concurrent modification occurs.

## Dependencies And Integration Points

It depends on page-size lookup, global mmap-mincore option flag, global continue flag, shim mincore, and optional `madvise` population constants. It is used by mmap/memory stressors that need deterministic page residency.

## Risks And Test Signals

Risks include touching read-only mappings, races with concurrent writers, `mincore` range alignment mistakes, and allocation failure for the vector. Test signals include no-op without flag, fallback when `mincore` fails, interruptible early exit, unchanged buffer contents after touch, and behavior on non-page-aligned buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mincore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mincore.h -->
# sources/test-tools/stress-ng/core-mincore.h

## Purpose

This header declares page-residency touch helpers.

## Important APIs, Types, And Functions

It exposes `stress_mincore_touch_pages` and `stress_mincore_touch_pages_interruptible`.

## Control Flow

Callers request residency for a buffer, choosing whether the operation should stop when the global continue flag clears.

## State And Persistence Behavior

The implementation may temporarily write to pages but owns no persistent state.

## Dependencies And Integration Points

The API is consumed by mmap and memory stressors controlled by mmap-mincore options.

## Risks And Test Signals

Callers must pass writable memory if fallback touching may occur. Tests should verify buffer contents are restored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mincore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mlock.c -->
# sources/test-tools/stress-ng/core-mlock.c

## Purpose

This file provides a helper to `mlock` an address range after expanding it to page boundaries. It is intended for locking sensitive or latency-critical regions such as signal-handler code/data into RAM.

## Important APIs, Types, And Functions

The single public function is `stress_mlock_region`. It computes page-aligned start and end using `stress_memory_page_size_get`, calculates length, and calls `shim_mlock` when `HAVE_MLOCK` is available.

## Control Flow

If the aligned end is not after the aligned start, the function returns success without calling `mlock`. Unsupported builds return success after marking the path unexpected.

## State And Persistence Behavior

The module owns no state. Successful `mlock` changes process memory locking state until unlock or process exit and is constrained by `RLIMIT_MEMLOCK` and privileges.

## Dependencies And Integration Points

It depends on page-size lookup and shim `mlock`. It integrates with code paths that want reduced paging latency.

## Risks And Test Signals

Risks include permission or limit failures, incorrect alignment, and assuming unsupported platforms actually lock memory. Test signals include aligned ranges, zero-length ranges, failure under low `RLIMIT_MEMLOCK`, and no-op compile behavior without `mlock`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mlock.h -->
# sources/test-tools/stress-ng/core-mlock.h

## Purpose

This header declares the memory-locking region helper.

## Important APIs, Types, And Functions

It exposes `stress_mlock_region(const void *addr_start, const void *addr_end)`.

## Control Flow

Callers pass a half-open address range and receive the `mlock` result or success for empty/unsupported cases.

## State And Persistence Behavior

The implementation can change process memory residency/lock state. The header owns no state.

## Dependencies And Integration Points

It integrates with signal and memory subsystems that need pages locked in RAM.

## Risks And Test Signals

Callers should handle nonzero returns caused by limits or permissions. Alignment tests are the key signal.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mlock.h -->
