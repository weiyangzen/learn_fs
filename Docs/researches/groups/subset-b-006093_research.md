# Research: subset-b-006093

This grouped report covers the source-tree-aligned work item `subset-b-006093`. Each file section is delimited for deterministic reconciliation into `Docs/researches/<source-path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dynamic_debug.c -->
# sources/distributed-fs/ceph-client/lib/dynamic_debug.c

## Purpose
Implements Linux dynamic debug control for runtime-enabling `pr_debug()`, `dev_dbg()`, network-device debug, and InfiniBand-device debug callsites. It maintains global per-module tables of `_ddebug` descriptors, parses boot/module/control-file commands, applies flag changes to matching callsites, and exposes the configured callsites through `/proc/dynamic_debug/control` and debugfs `dynamic_debug/control`.

## Important APIs, Types, and Functions
Key internal types are `struct ddebug_table` for one module's descriptor range and class maps, `struct ddebug_query` for parsed match criteria, `struct ddebug_iter` for seq-file traversal, and `struct flag_settings` for parsed flag operations. Public/exported APIs include `__dynamic_pr_debug()`, `__dynamic_dev_dbg()`, `__dynamic_netdev_dbg()` under `CONFIG_NET`, `__dynamic_ibdev_dbg()` under InfiniBand, `param_set_dyndbg_classes()`, `param_get_dyndbg_classes()`, and `param_ops_dyndbg_classes`.

The query path is centered on `ddebug_exec_queries()`, `ddebug_exec_query()`, `ddebug_tokenize()`, `ddebug_parse_query()`, `ddebug_parse_flags()`, and `ddebug_change()`. `ddebug_change()` matches module, filename, function, format, line range, and optional class string, then mutates `dp->flags`; when jump labels are enabled it also toggles the descriptor's static branch for `_DPRINTK_FLAGS_PRINT`.

Module lifecycle support comes from `ddebug_add_module()`, `ddebug_attach_module_classes()`, `ddebug_remove_module()`, and `ddebug_module_notify()`. Boot/control setup is in `dynamic_debug_init()`, `dynamic_debug_init_control()`, `dyndbg_setup()`, `ddebug_dyndbg_boot_param_cb()`, and `ddebug_dyndbg_module_param_cb()`.

## Control Flow
At early init, `dynamic_debug_init()` registers the module notifier, walks linker-provided `__dyndbg` and `__dyndbg_classes` sections, groups descriptors by module name, adds a `ddebug_table` per module, and re-parses `saved_command_line` for `dyndbg` parameters after the tables exist. Later `dynamic_debug_init_control()` creates debugfs and procfs control files when initialization succeeded.

Writes to the control file are copied with `memdup_user_nul()`, split on semicolons/newlines, tokenized with simple whitespace/quote handling, parsed into query criteria plus a final flag operation, and applied across all registered tables under `ddebug_lock`. Reads use seq-file callbacks to hold `ddebug_lock`, iterate every descriptor in reverse index order per table, and format `filename:lineno [module]function =flags "format"` plus class metadata.

Class-param updates turn bitmaps or levels into synthesized `class <name> +/-<flags>` dynamic-debug commands. For named maps, comma-separated class names toggle bits or level thresholds; for numeric maps, input is parsed as a bitmask or level number.

## State and Persistence
Persistent runtime state is in static globals: `ddebug_tables`, `ddebug_lock`, `verbose`, and `ddebug_init_success`. Per-callsite state persists in the linker/module `_ddebug` descriptor array through its `flags` field and optional jump-label branch state. Per-class kernel parameters persist in caller-owned `ddebug_class_param` `bits` or `lvl` storage, while `ddebug_table` objects are allocated for built-in/module descriptor ranges and freed on module unload.

The control files are runtime views, not durable storage. Boot parameters and module parameters apply at initialization or load time but subsequent control-file changes live only until reboot/module unload.

## Dependencies and Integration Points
Depends on kernel module metadata, linker sections, debugfs, procfs, seq_file, sysctl/moduleparam parsing, `linux/dynamic_debug.h`, string matching helpers, optional jump labels, and device/net/InfiniBand logging APIs. Integration points include the dynamic-debug macros that emit `_ddebug` descriptors, module notifier hooks, kernel command line parsing, module parameter callbacks, and class maps declared by other modules.

## Risks
The parser is intentionally simple: it supports basic quoting but no escaping inside quotes, caps commands at one page, and accepts a fixed maximum word count. Query operations are global and can touch many descriptors under `ddebug_lock`, so expensive wildcard/format searches may hold the mutex for noticeable time on large systems. Class-map state can drift from direct control-file edits because `param_get_dyndbg_classes()` reports the last parameter state rather than re-deriving all callsite flags. Jump-label toggling must stay synchronized with `_DPRINTK_FLAGS_PRINT`; regressions would affect disabled-callsite fast paths. Module removal compares `dt->mod_name == mod_name`, relying on module-name pointer lifetime/identity described in the allocation comment.

## Test Signals
Useful signals include booting with `dyndbg=` and `$module.dyndbg=`, echoing valid/invalid queries into both debugfs and procfs control files, verifying seq-file output escaping and class display, loading/unloading modules with `_ddebug` descriptors, toggling class parameters for all map types, and checking jump-label/static-branch state changes under `CONFIG_JUMP_LABEL`. Negative tests should cover bad flags, duplicate match-specs, malformed line ranges, unknown class names, too-long writes, and no-match queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dynamic_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dynamic_queue_limits.c -->
# sources/distributed-fs/ceph-client/lib/dynamic_queue_limits.c

## Purpose
Implements Dynamic Queue Limits (DQL), a byte/object queue-limit controller used by networking and similar producer/completion paths to keep queues deep enough to avoid starvation but not so deep that latency grows unnecessarily. It also includes optional stall detection for queues that receive work but stop completing.

## Important APIs, Types, and Functions
The file operates on `struct dql` from `include/linux/dynamic_queue_limits.h`. Exported functions are `dql_completed()`, `dql_reset()`, and `dql_init()`. `dql_check_stall()` is the internal stall detector. Macros `POSDIFF()` and `AFTER_EQ()` implement wrap-tolerant positive-difference and ordering logic for unsigned counters.

## Control Flow
`dql_init()` sets default bounds (`DQL_MAX_LIMIT`, `min_limit = 0`), records the caller's slack hold time, disables stall detection, and calls `dql_reset()`. `dql_reset()` resets counters, limit, slack tracking, last reap timestamp, and history ring state.

`dql_completed()` reads the producer-updated queued count and stall threshold, validates that completions do not exceed queued work, computes current in-progress work, and adjusts the limit. If the queue was over-limit and drained, or the previous over-limit interval may have starved, it increases the limit by completed work and previous over-limit. If the queue stayed busy, it tracks lowest slack and periodically decreases the limit after `slack_hold_time`. The new limit is clamped to `[min_limit, max_limit]`, derived fields are updated, and `dql_check_stall()` inspects the history bitmap for stale queued work without completions.

## State and Persistence
All state lives in the caller-owned `struct dql`: queued/completed counters, current and adjusted limits, previous interval counters, slack state, history ring, stall counters, and jiffy timestamps. There is no allocation or external persistence. Concurrency relies on `READ_ONCE()`, barriers paired with enqueue-side writes, and caller discipline defined by the DQL API.

## Dependencies and Integration Points
Uses jiffies/time helpers, bitmap operations, `trace_dql_stall_detected()`, and exported symbols for drivers or core networking code. It expects enqueue-side code to call the corresponding DQL queue APIs/macros that update `num_queued`, `last_obj_cnt`, `history`, and `history_head`.

## Risks
Counter arithmetic assumes the DQL invariants are respected; `BUG_ON(count > num_queued - num_completed)` turns misuse into a hard failure. Limit adaptation is sensitive to wraparound assumptions and jiffies-based timing. Stall detection depends on correct memory ordering between queue recording and history reads. Incorrect `min_limit`, `max_limit`, or `stall_thrs` settings can hide real stalls or cause unstable queue depth.

## Test Signals
Exercise DQL through network transmit paths and targeted unit-style tests that model bursty, steady, over-limit, and starved queues. Tracepoint output from `dql_stall_detected`, limit convergence, clamp behavior, and reset behavior are key signals. Tests should include wrap-adjacent counter values and stall thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/dynamic_queue_limits.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/earlycpio.c -->
# sources/distributed-fs/ceph-client/lib/earlycpio.c

## Purpose
Provides `find_cpio_data()`, an early-boot helper for locating an uncompressed `newc` cpio member at the head of an initramfs blob before the normal initramfs decompression path runs. It is used for kernel-consumed early data that package tooling places before compressed payloads.

## Important APIs, Types, and Functions
The exported interface is `struct cpio_data find_cpio_data(const char *path, void *data, size_t len, long *nextoff)`. It returns a `cpio_data` with data pointer, size, and a path-relative name, or `{ NULL, 0, "" }` when not found or parsing fails. Internal enum `cpio_fields` names the fixed `newc` header fields.

## Control Flow
The parser walks the buffer while enough bytes remain for a header. It skips zero padding in 4-byte steps, parses the 6-character magic field and subsequent 8-character hex fields, validates magic `070701` or `070702`, aligns the filename and data boundaries, and rejects overruns. Regular-file entries whose name starts with `path` are returned; `nextoff`, when supplied, receives the offset of the next member so callers can iterate.

## State and Persistence
The function is stateless and performs no allocation. It returns direct pointers into the caller's archive buffer and copies only the matched suffix into the fixed-size `cd.name` array with `strscpy()`.

## Dependencies and Integration Points
Depends on `linux/earlycpio.h`, alignment macros, kernel string helpers, and `MAX_CPIO_FILE_NAME`. It integrates with early boot/initramfs consumers that know the archive is uncompressed at the current offset.

## Risks
The parser exits on the first malformed header or overrun, so a bad early member can hide later valid data. It only returns regular files and only supports uncompressed `newc` content. Filename suffixes longer than `MAX_CPIO_FILE_NAME` are warned and truncated. The zero-padding skip always subtracts four bytes; callers must provide correctly aligned remaining lengths.

## Test Signals
Tests should cover exact-file and directory-prefix lookups, repeated iteration with `nextoff`, zero padding, both accepted magic values, truncated headers, invalid hex, oversized names, non-regular entries, and malformed size/name combinations that would overrun the buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/earlycpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/errname.c -->
# sources/distributed-fs/ceph-client/lib/errname.c

## Purpose
Maps Linux errno values to symbolic names such as `"-EIO"` or `"EIO"`, providing a small exported helper for diagnostics that need stable errno names without open-coded tables.

## Important APIs, Types, and Functions
The public API is `const char *errname(int err)`, exported with `EXPORT_SYMBOL`. Internally, `__errname(unsigned err)` searches two sparse static string tables: `names_0[]` for normal errno values up to 300 and `names_512[]` for kernel-internal restart/probe/NFS-style errors in the 512-550 range.

## Control Flow
`errname()` calls `__errname(abs(err))`. If no table entry exists, it returns `NULL`. For positive errno inputs, it strips the leading minus sign from the stored table string; for negative inputs, it returns the stored `"-EXXX"` spelling. The table macros use `BUILD_BUG_ON_ZERO()` to keep entries in expected numeric ranges.

## State and Persistence
The file has only compile-time static const tables. There is no mutable state, allocation, locking, or persistence.

## Dependencies and Integration Points
Depends on architecture errno definitions, `linux/errname.h`, `linux/errno.h`, `BUILD_BUG_ON_ZERO`, and `static_assert`. Architecture-specific aliases and gaps are handled with preprocessor guards, including MIPS `EDQUOT` as a special high-numbered errno and parisc aliases.

## Risks
Coverage depends on maintaining the tables as errno definitions evolve. Unknown or architecture-specific errors return `NULL`, so callers must handle absence. The `abs(err)` conversion relies on normal errno-sized integers rather than arbitrary `INT_MIN`-style inputs. Large table bounds are intentionally limited to avoid huge sparse arrays.

## Test Signals
Validate negative and positive inputs, aliases (`EAGAIN`/`EWOULDBLOCK`, parisc aliases when present), internal 512-range errors, MIPS `EDQUOT`, unknown values, and zero. Build coverage across architectures is important because conditional entries differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/errname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/lib/error-inject.c

## Purpose
Maintains the kernel's whitelist of functions that are safe targets for function-level error injection, such as BPF error injection. It discovers whitelist entries from built-in and module sections, answers address/type queries, and exposes a debugfs listing.

## Important APIs, Types, and Functions
Key public functions are `within_error_injection_list(unsigned long addr)` and `get_injectable_error_type(unsigned long addr)`. Internal state is represented by `struct ei_entry`, which records a function start/end range, error type, and owner pointer. `populate_error_injection_list()`, `populate_kernel_ei_list()`, `module_load_ei_list()`, and `module_unload_ei_list()` manage entries. Seq-file callbacks behind `DEFINE_SEQ_ATTRIBUTE(ei)` implement debugfs `error_injection/list`.

## Control Flow
Late init calls `populate_kernel_ei_list()` to scan the built-in `_error_inject_whitelist` section. With modules enabled, a module notifier adds entries on `MODULE_STATE_COMING` and removes entries belonging to that module on `MODULE_STATE_GOING`. Population resolves symbol descriptors, validates that the target is kernel text, looks up function size through kallsyms, allocates an `ei_entry`, and appends it to the global list.

## State and Persistence
Mutable state is the global `error_injection_list`, protected by `ei_mutex`. Built-in entries live until shutdown; module entries are tagged with `priv = mod` and removed on unload. Debugfs only reflects this live in-memory list.

## Dependencies and Integration Points
Uses `linux/error-injection.h`, kallsyms, kprobes symbol descriptor handling, module notifiers, debugfs, seq_file, and section markers `__start_error_injection_whitelist`/`__stop_error_injection_whitelist`. Consumers such as BPF/kprobe error injection call the query APIs to enforce the whitelist and allowed return type.

## Risks
If kallsyms lookup fails or allocation stops, entries are skipped, reducing injection coverage. Address-range matching depends on accurate function sizes and symbol descriptor dereferencing. The list is linear, which is simple but can become costly if many whitelist entries exist. `init_error_injection()` ignores debugfs init failure when module notifier registration succeeds, so debugfs observability is best-effort.

## Test Signals
Check that built-in whitelist entries appear in debugfs, module load/unload adds and removes entries, address queries match inside but not outside function ranges, and each `EI_ETYPE_*` maps to the expected string. Negative tests should cover invalid section entries and allocation/kallsyms failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/errseq.c -->
# sources/distributed-fs/ceph-client/lib/errseq.c

## Purpose
Implements `errseq_t`, a compact lockless sequence/error word for recording errors in one place and letting many observers detect whether a new error occurred since their sample. It is commonly used for writeback and filesystem error reporting.

## Important APIs, Types, and Functions
Exported APIs are `errseq_set()`, `errseq_sample()`, `errseq_check()`, and `errseq_check_and_advance()`. Internal bit layout macros are `ERRSEQ_SHIFT`, `ERRSEQ_SEEN`, `ERRNO_MASK`, and `ERRSEQ_CTR_INC`. The low bits store a positive errno magnitude, one bit marks whether the value has been seen, and upper bits act as a counter.

## Control Flow
`errseq_set()` validates a nonzero negative errno, clears old errno and seen bits, stores the new errno magnitude, and increments the counter only if a reader had marked the old value seen. It uses `cmpxchg()` loops and treats racing writes to the same value as success. `errseq_sample()` returns zero when an error is still unseen so a new observer will still report it later. `errseq_check()` compares a stored sample with the current value and returns the current error without advancing. `errseq_check_and_advance()` sets the seen bit, updates the caller's sample, and returns the recorded error.

## State and Persistence
All persistent state is the caller-owned `errseq_t` word. There is no allocation or global state. Updates are atomic and usable from any context, but concurrent access to a caller's `since` sample pointer is not serialized by this file.

## Dependencies and Integration Points
Depends on kernel atomics, `MAX_ERRNO`, `linux/errseq.h`, and `linux/log2.h`. Filesystems and writeback code integrate by embedding `errseq_t` fields in shared objects and storing per-file/per-observer samples.

## Risks
The counter has limited width, so very frequent errors can theoretically collide with old samples. `errseq_check()` reports the latest stored errno, not necessarily the first error since the sample. Callers must provide locking if multiple threads advance the same sample. Passing zero, positive, or out-of-range errors to `errseq_set()` only warns and leaves state unchanged.

## Test Signals
Tests should cover initial zero state, unseen error sampling, seen-bit behavior, repeated same-error sets before/after sampling, racing set/check patterns, invalid error inputs, and counter wrap/collision scenarios. Filesystem tests should verify that errors are reported once per observer after advance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/errseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/extable.c -->
# sources/distributed-fs/ceph-client/lib/extable.c

## Purpose
Provides generic exception-table sorting, trimming, and binary search support. Exception tables map faulting instruction addresses to fixup handlers for safe recovery from faults such as user-copy access exceptions.

## Important APIs, Types, and Functions
Public functions are `sort_extable()`, `search_extable()`, and `trim_init_extable()` under `CONFIG_MODULES`. `ex_to_insn()` abstracts absolute versus relative exception-table encodings. `swap_ex()` handles relative-entry swapping while preserving offsets. `cmp_ex_sort()` and `cmp_ex_search()` drive sorting and bsearch.

## Control Flow
`sort_extable()` sorts an exception table by instruction address using the generic kernel `sort()` helper and an architecture-aware swap function. `search_extable()` performs a binary search for a faulting instruction address in an already sorted table. `trim_init_extable()` removes module exception-table entries that point into module init memory after that memory is no longer retained.

## State and Persistence
The file mutates caller-provided exception-table arrays in place and may adjust a module's `extable` pointer and `num_exentries`. It owns no persistent global state.

## Dependencies and Integration Points
Depends on `linux/extable.h`, generic `sort()`/`bsearch()`, module metadata, architecture macros such as `ARCH_HAS_RELATIVE_EXTABLE`, `swap_ex_entry_fixup`, and `within_module_init()`. It is used by core exception handling and module loading.

## Risks
`search_extable()` assumes the table is sorted; unsorted tables cause missed fixups. Relative exception-table swaps are easy to get wrong because offset fields must be adjusted for the new addresses. Trimming assumes sorted order so init references cluster at the beginning or end. Architecture-specific fixup layouts require correct `swap_ex_entry_fixup` support.

## Test Signals
Boot and module-load paths provide broad coverage. Targeted tests should sort synthetic absolute and relative entries, search for present/missing addresses, verify relative offsets after sorting, and trim module init entries from both ends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fault-inject-usercopy.c -->
# sources/distributed-fs/ceph-client/lib/fault-inject-usercopy.c

## Purpose
Defines a usercopy-specific fault-injection attribute and exposes `should_fail_usercopy()` so user-copy paths can be forced to fail under boot-parameter or debugfs control.

## Important APIs, Types, and Functions
The file owns a static `fail_usercopy` object containing `struct fault_attr attr` initialized by `FAULT_ATTR_INITIALIZER`. `setup_fail_usercopy()` parses the `fail_usercopy=` boot parameter. `fail_usercopy_debugfs()` creates debugfs controls when `CONFIG_FAULT_INJECTION_DEBUG_FS` is enabled. `should_fail_usercopy()` is exported GPL-only.

## Control Flow
At boot, `__setup("fail_usercopy=", setup_fail_usercopy)` lets users configure interval, probability, space, and times via the shared fault-attr parser. During late init, optional debugfs setup creates `/sys/kernel/debug/fail_usercopy` style controls through `fault_create_debugfs_attr()`. Runtime callers invoke `should_fail_usercopy()`, which delegates to `should_fail(&fail_usercopy.attr, 1)`.

## State and Persistence
All mutable state is in the static `fault_attr`: probability, interval, counters, remaining failures/space, verbosity, and optional filters. Settings persist only for the running kernel.

## Dependencies and Integration Points
Depends on the generic fault-injection framework in `fault-inject.c`, debugfs when enabled, and usercopy call sites that check `should_fail_usercopy()`. It integrates through a boot parameter and exported symbol.

## Risks
Misconfiguration can cause broad usercopy failures and noisy diagnostics. Debugfs setup is optional and late, so boot parameter coverage is needed for early behavior. A size of `1` means space accounting is per usercopy decision rather than actual copy length.

## Test Signals
Boot with `fail_usercopy=` combinations, toggle debugfs attributes, verify probability/times/interval semantics, and confirm usercopy call sites fail only when the predicate returns true. Disable debugfs builds should still honor boot parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fault-inject-usercopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fault-inject.c -->
# sources/distributed-fs/ceph-client/lib/fault-inject.c

## Purpose
Implements the generic kernel fault-injection decision engine and its debugfs/configfs configuration surfaces. Subsystems embed `struct fault_attr` and call `should_fail()` or `should_fail_ex()` to probabilistically or deterministically force failures for testing.

## Important APIs, Types, and Functions
Exported APIs include `setup_fault_attr()`, `should_fail()`, `fault_create_debugfs_attr()` under debugfs, and `fault_config_init()` under configfs. Core helpers are `fault_prandom_u32_below_100()`, `fail_dump()`, `fail_task()`, optional `fail_stacktrace()`, and the main `should_fail_ex()`. Configfs support defines `struct fault_config` item attributes via generated show/store functions.

## Control Flow
`setup_fault_attr()` parses boot strings as `<interval>,<probability>,<space>,<times>`, initializes per-CPU pseudo-random state, and seeds the attribute. `should_fail_ex()` first handles per-task `current->fail_nth`, then rejects if probability is zero, task filtering fails, times is zero, stacktrace filters fail, space budget remains, interval has not reached a trigger point, or the random percentage test misses. On failure it optionally logs/dumps, decrements `times` unless infinite, and returns true.

Debugfs creation builds one directory per fault attribute with files for probability, interval, times, space, verbosity, rate limit, task filter, and optional stacktrace bounds. Configfs exposes equivalent attributes for dynamically created fault configurations.

## State and Persistence
State is stored in caller-owned `struct fault_attr` fields plus a static per-CPU `rnd_state` array. `times`, `space`, `count`, rate-limit state, stacktrace ranges, and task-filter flags mutate over time. Configuration persists only in memory and in configfs/debugfs live objects.

## Dependencies and Integration Points
Depends on debugfs, configfs, per-CPU pseudo-random state, scheduler task fields (`make_it_fail`, `fail_nth`), stacktrace capture when configured, atomics, and rate limiting. Integrated subsystems pass size values to `should_fail()` and may add their own boot parameters or configfs groups.

## Risks
`attr->count` is not atomic, so concurrent callers can race interval accounting. Debugfs/configfs stores update fields directly, and invalid operational combinations can create aggressive system-wide failures. Stacktrace filtering depends on reliable saved stacks and address bounds. The non-cryptographic PRNG is intentional but unsuitable for security decisions. `setup_fault_attr()` returns `0` on parse error because of `__setup` conventions, which can be surprising to non-boot-parameter callers.

## Test Signals
Verify probability extremes, intervals, finite/infinite `times`, space accounting, task filtering, `fail_nth`, `FAULT_NOWARN`, verbose rate limits, stacktrace require/reject ranges, debugfs/configfs show/store parsing, and concurrent callers. Subsystem tests should assert that injected failures are observable and recoverable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fault-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt.c -->
# sources/distributed-fs/ceph-client/lib/fdt.c

## Purpose
This file is a kernel build wrapper for the common libfdt core implementation. It includes `linux/libfdt_env.h` and then compiles `../scripts/dtc/libfdt/fdt.c` into the kernel tree with the kernel environment definitions.

## Important APIs, Types, and Functions
The wrapper itself declares no functions. The included implementation provides core flattened device tree routines such as `fdt_ro_probe_()`, `fdt_header_size()`, `fdt_check_header()`, `fdt_next_tag()`, `fdt_check_node_offset_()`, `fdt_check_prop_offset_()`, `fdt_next_node()`, `fdt_first_subnode()`, `fdt_next_subnode()`, and `fdt_move()`.

## Control Flow
Compilation substitutes the kernel libfdt environment before including the shared source. At runtime the included routines validate FDT headers, walk structure-block tags, iterate nodes/subnodes, validate offsets, and move an FDT blob into another buffer when size permits.

## State and Persistence
There is no wrapper-owned state. The included libfdt functions operate on caller-provided FDT memory buffers and may copy data in `fdt_move()`.

## Dependencies and Integration Points
Depends on the in-tree `scripts/dtc/libfdt` source and `linux/libfdt_env.h`. It integrates boot, architecture, and device-tree code that uses libfdt APIs from kernel C code while sharing implementation with dtc tooling.

## Risks
Because this is an include wrapper, changes in the shared dtc libfdt file directly affect kernel behavior. Environment mismatches between userspace libfdt assumptions and kernel `libfdt_env.h` can cause build or ABI issues. Header and structure validation are security-sensitive because FDT blobs may be firmware supplied.

## Test Signals
FDT boot tests, malformed-header tests, node iteration tests, and `fdt_move()` buffer-size tests are relevant. Build coverage should ensure the wrapper continues compiling after shared libfdt updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_addresses.c -->
# sources/distributed-fs/ceph-client/lib/fdt_addresses.c

## Purpose
Kernel wrapper for shared libfdt address/size-cell helpers. It includes `linux/libfdt_env.h` and compiles `../scripts/dtc/libfdt/fdt_addresses.c`.

## Important APIs, Types, and Functions
The wrapper itself has no local declarations. The included code provides `fdt_address_cells()`, `fdt_size_cells()`, and `fdt_appendprop_addrrange()`, with an internal `fdt_cells()` helper for reading `#address-cells` and `#size-cells`.

## Control Flow
Calls read cell-count properties from nodes, apply libfdt validation and default/error rules, and append encoded address/size ranges to a property using the writable libfdt property machinery.

## State and Persistence
No persistent state is owned by the wrapper. The included functions read or mutate caller-provided FDT blobs when appending address ranges.

## Dependencies and Integration Points
Depends on libfdt core/read-write helpers and kernel endian/cell definitions from `linux/libfdt_env.h`. It is used by architecture and firmware code that interprets or constructs `reg`-style properties.

## Risks
Wrong cell-count interpretation can corrupt address range encoding. `fdt_appendprop_addrrange()` depends on sufficient FDT buffer space and valid parent/node offsets. Shared-source updates propagate through this wrapper.

## Test Signals
Test default and explicit cell counts, invalid cell properties, 32-bit and 64-bit address/size ranges, no-space errors, and integration with consumers parsing generated `reg` properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_addresses.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_empty_tree.c -->
# sources/distributed-fs/ceph-client/lib/fdt_empty_tree.c

## Purpose
Kernel wrapper for shared libfdt empty-tree creation. It includes the kernel libfdt environment and compiles `../scripts/dtc/libfdt/fdt_empty_tree.c`.

## Important APIs, Types, and Functions
The included implementation provides `fdt_create_empty_tree(void *buf, int bufsize)`. The wrapper has no independent API.

## Control Flow
`fdt_create_empty_tree()` creates a writable FDT in the supplied buffer, finishes the reserve map, opens and closes the root node, and finalizes the blob using libfdt sequential-write helpers.

## State and Persistence
State is entirely in the caller-provided buffer. No globals, allocation, or persistent kernel state are introduced by the wrapper.

## Dependencies and Integration Points
Depends on libfdt sequential-write functions from `fdt_sw.c` and `linux/libfdt_env.h`. It integrates with code that needs a minimal FDT blob as a starting point for later mutation.

## Risks
Failure handling depends on correct propagation of libfdt no-space or bad-state errors. Since the file is only a wrapper, shared libfdt changes alter behavior. Buffer size validation is critical.

## Test Signals
Create empty trees with too-small and sufficient buffers, validate resulting headers and root structure, and mutate the resulting tree with read-write libfdt APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_empty_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_ro.c -->
# sources/distributed-fs/ceph-client/lib/fdt_ro.c

## Purpose
Kernel wrapper for shared libfdt read-only query and traversal routines. It includes `linux/libfdt_env.h` and compiles `../scripts/dtc/libfdt/fdt_ro.c`.

## Important APIs, Types, and Functions
The included implementation provides read-only APIs for memory reservations, node/path lookup, property iteration and lookup, phandle discovery/generation, path construction, parent/depth queries, string-list helpers, and compatible matching. Examples include `fdt_get_mem_rsv()`, `fdt_num_mem_rsv()`, `fdt_subnode_offset()`, `fdt_path_offset()`, `fdt_first_property_offset()`, `fdt_next_property_offset()`, `fdt_get_phandle()`, `fdt_get_path()`, `fdt_parent_offset()`, `fdt_node_offset_by_prop_value()`, `fdt_node_offset_by_phandle()`, `fdt_stringlist_count()`, `fdt_stringlist_search()`, and `fdt_node_offset_by_compatible()`.

## Control Flow
The routines validate offsets through core libfdt helpers, walk the structure block, compare node names and properties, decode string lists, and return negative `FDT_ERR_*` values for invalid input or missing data. Search routines usually iterate from a supplied offset so callers can continue scanning.

## State and Persistence
No wrapper-owned state exists. All operations read caller-provided immutable FDT memory. Some functions write outputs to caller buffers or output pointers.

## Dependencies and Integration Points
Depends on libfdt core parsing and kernel environment definitions. It is a major integration point for early boot, platform discovery, driver matching, reserved-memory parsing, and other firmware data consumers.

## Risks
Read-only does not mean low-risk: malformed firmware blobs must be rejected without overread. Path and string-list handling can fail with truncation or malformed NUL termination. Phandle generation must avoid reserved/overflow values. Shared-source updates affect all kernel FDT readers.

## Test Signals
Use valid and malformed FDT blobs to test node/path/property lookup, memory reservation counts, compatible matching, string-list edge cases, phandle searches, parent/depth relationships, and output-buffer truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_ro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_rw.c -->
# sources/distributed-fs/ceph-client/lib/fdt_rw.c

## Purpose
Kernel wrapper for shared libfdt read-write mutation routines. It includes the kernel environment and compiles `../scripts/dtc/libfdt/fdt_rw.c`.

## Important APIs, Types, and Functions
The included code provides mutable FDT APIs such as `fdt_add_mem_rsv()`, `fdt_del_mem_rsv()`, `fdt_set_name()`, `fdt_setprop_placeholder_namelen()`, `fdt_setprop_namelen()`, `fdt_appendprop()`, `fdt_delprop()`, `fdt_add_subnode_namelen()`, `fdt_add_subnode()`, `fdt_del_node()`, `fdt_open_into()`, and `fdt_pack()`. Internal helpers splice memory reservation, structure, and string blocks.

## Control Flow
Before mutating, the included implementation probes blob layout and writability. Mutation paths resize or add properties, append strings, splice structure-block data, add/delete nodes, and repack FDT blocks. `fdt_open_into()` can reorganize a blob into a writable buffer, and `fdt_pack()` compacts it.

## State and Persistence
No globals are owned by the wrapper. Persistent effects are direct modifications to the caller's FDT buffer, including header fields, structure block, strings block, and reserve map.

## Dependencies and Integration Points
Depends on core, read-only, and environment libfdt helpers. It integrates with boot/platform code that edits firmware-provided trees or constructs adjusted trees before handing them to later consumers.

## Risks
Mutation is buffer-layout-sensitive. Incorrect splice sizes or no-space handling can corrupt an FDT. String-block deduplication/removal must preserve referenced property names. Shared-source updates are imported wholesale. Callers must not pass read-only or undersized buffers to write APIs.

## Test Signals
Exercise add/delete reservations, rename nodes, set/append/delete properties, add/delete subnodes, open into larger buffers, pack after deletion, no-space paths, and validation with read-only lookup after each mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_strerror.c -->
# sources/distributed-fs/ceph-client/lib/fdt_strerror.c

## Purpose
Kernel wrapper for shared libfdt error-string conversion. It includes `linux/libfdt_env.h` and compiles `../scripts/dtc/libfdt/fdt_strerror.c`.

## Important APIs, Types, and Functions
The included API is `const char *fdt_strerror(int errval)`. It uses a static `fdt_errtable[]` mapping `FDT_ERR_*` numeric values to their symbolic names and returns special strings for positive offsets/lengths and zero.

## Control Flow
Positive inputs are reported as valid offsets/lengths, zero as no error, known negative libfdt errors as their `FDT_ERR_*` names, and unknown values as unknown errors.

## State and Persistence
Only a static error table exists. There is no mutable state or allocation.

## Dependencies and Integration Points
Depends on libfdt error definitions and kernel libfdt environment. It integrates with diagnostics in kernel code that reports libfdt return values.

## Risks
The table must be updated when new `FDT_ERR_*` values are introduced. Positive libfdt returns are not errors, so callers must not treat the returned positive-input string as failure evidence.

## Test Signals
Check zero, positive offsets, each known negative `FDT_ERR_*`, gaps in the table, and unknown negative values. Build tests should catch newly added error constants that lack expected diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_strerror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_sw.c -->
# sources/distributed-fs/ceph-client/lib/fdt_sw.c

## Purpose
Kernel wrapper for shared libfdt sequential-write creation routines. It includes the kernel libfdt environment and compiles `../scripts/dtc/libfdt/fdt_sw.c`.

## Important APIs, Types, and Functions
The included implementation provides `fdt_create_with_flags()`, `fdt_create()`, `fdt_resize()`, `fdt_add_reservemap_entry()`, `fdt_finish_reservemap()`, `fdt_begin_node()`, `fdt_end_node()`, `fdt_property_placeholder()`, `fdt_property()`, and `fdt_finish()`. Internal helpers probe current construction state and manage strings.

## Control Flow
Callers create a sequential-write FDT buffer, optionally add reserve-map entries, finish the reserve map, begin/end nodes, add properties, and finish the blob. The implementation enforces construction state ordering and writes structure/string blocks incrementally.

## State and Persistence
No wrapper-owned state exists. Construction state is encoded in the caller's FDT buffer/header while the tree is being built.

## Dependencies and Integration Points
Depends on libfdt environment definitions and shared libfdt internals. It integrates with architecture/boot code that synthesizes FDT blobs without starting from an existing complete tree.

## Risks
APIs are stateful by buffer contents: calling functions out of order returns bad-state errors or can leave an incomplete blob. Buffer size and alignment are critical. Shared-source updates can change construction behavior across kernel users.

## Test Signals
Create valid trees from scratch, attempt out-of-order operations, test reservation-map sequencing, no-space property insertion, string reuse, resize behavior, and final validation with `fdt_check_header()` plus read-only traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_wip.c -->
# sources/distributed-fs/ceph-client/lib/fdt_wip.c

## Purpose
Kernel wrapper for shared libfdt in-place/work-in-progress mutation helpers. It includes the kernel environment and compiles `../scripts/dtc/libfdt/fdt_wip.c`.

## Important APIs, Types, and Functions
The included implementation provides `fdt_setprop_inplace_namelen_partial()`, `fdt_setprop_inplace()`, `fdt_nop_property()`, `fdt_node_end_offset_()`, and `fdt_nop_node()`. Internal `fdt_nop_region_()` marks structure-block regions as NOP tags.

## Control Flow
In-place property updates locate an existing property and copy bytes into its current value without resizing. NOP operations find the property or node extent and replace the corresponding structure-block region with NOP tags so later pack operations can reclaim space.

## State and Persistence
No wrapper-owned state exists. The caller's mutable FDT buffer is changed in place.

## Dependencies and Integration Points
Depends on core and read-only libfdt helpers for locating nodes/properties and on kernel environment definitions. It integrates with code needing limited mutation of an already laid-out FDT without reallocating or changing block sizes.

## Risks
In-place setters cannot grow properties; callers must supply matching offsets and lengths. NOPing the wrong region can remove required tree data until repacked or rebuilt. Shared-source updates affect kernel behavior directly.

## Test Signals
Test partial/full in-place property replacement, overlength rejection, NOPing properties and nodes, subsequent read-only lookup behavior, and packing after NOP operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fdt_wip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/find_bit.c -->
# sources/distributed-fs/ceph-client/lib/find_bit.c

## Purpose
Provides generic fallback implementations for the kernel `find_*_bit` bitmap search family when an architecture has not supplied optimized versions. It also implements nth-bit, clump, little-endian-on-big-endian, and random-set-bit helpers.

## Important APIs, Types, and Functions
Exported functions include `_find_first_bit()`, `_find_first_and_bit()`, `_find_first_andnot_bit()`, `_find_first_and_and_bit()`, `_find_first_zero_bit()`, `_find_next_bit()`, `__find_nth_bit()`, `__find_nth_and_bit()`, `__find_nth_and_andnot_bit()`, `_find_next_and_bit()`, `_find_next_andnot_bit()`, `_find_next_or_bit()`, `_find_next_zero_bit()`, `_find_last_bit()`, `find_next_clump8()`, endian-specific `_find_*_bit_le()` variants on big-endian builds, and `find_random_bit()`.

The core logic is in macros `FIND_FIRST_BIT`, `FIND_NEXT_BIT`, and `FIND_NTH_BIT`, parameterized by fetch and word-munging expressions.

## Control Flow
First/next search routines scan word by word, mask off bits before the requested start, and use `__ffs()` to return the first matching bit or `size` when none exists. Nth-bit routines count set bits with `hweight_long()` until the requested ordinal is in the current word, then use `fns()`. Last-bit search starts from the final masked word and scans backward with `__fls()`. `find_random_bit()` computes bitmap weight and selects a random ordinal for multi-bit maps.

## State and Persistence
The file is stateless and operates on caller-provided bitmaps. It does not modify input bitmaps except for outputting an 8-bit clump through `find_next_clump8()`.

## Dependencies and Integration Points
Depends on `linux/bitops.h`, `linux/bitmap.h`, endian byte swapping, random helpers, and exported symbols used throughout scheduler, memory-management, filesystem, and driver code. Architecture headers may define optimized variants, in which case guarded fallback functions are not compiled.

## Risks
Boundary handling around `size`, `start`, partial final words, and big-endian little-endian conversions is critical. `find_random_bit()` is O(weight/word scan) and not suitable for cryptographic randomness. Generic fallbacks affect many subsystems on architectures without overrides, so regressions have wide blast radius.

## Test Signals
Boot success is broad coverage, but targeted bitmap tests should verify empty/full maps, one-bit maps, partial final words, all boolean combinations, nth-bit out of range, clump alignment, big-endian LE variants, and random selection constrained to set bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/find_bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/find_bit_benchmark.c -->
# sources/distributed-fs/ceph-client/lib/find_bit_benchmark.c

## Purpose
Defines a loadable/init benchmark module for measuring performance of C `find_*_bit` operations over dense random and sparse random bitmaps. It is a performance smoke test, not a correctness suite.

## Important APIs, Types, and Functions
The module uses static initdata bitmaps `bitmap` and `bitmap2` of `BITMAP_LEN` bits and test helpers `test_find_first_bit()`, `test_find_first_and_bit()`, `test_find_next_bit()`, `test_find_next_zero_bit()`, `test_find_last_bit()`, `test_find_nth_bit()`, and `test_find_next_and_bit()`. `find_bit_test()` is registered with `module_init()`.

## Control Flow
On module init, the benchmark fills two bitmaps with random bytes, times several traversal patterns with `ktime_get()`, and prints nanosecond totals plus iteration counts. It then zeros both bitmaps, sets a sparse random subset of bits, repeats the timing tests, and returns `-EINVAL` intentionally so the benchmark can be inserted repeatedly without removing the module.

## State and Persistence
State is limited to static initdata bitmaps during initialization. No long-lived module state is kept because init returns failure by design.

## Dependencies and Integration Points
Depends on bitmap/bitops APIs, kernel random helpers, printk, module initialization, and timing APIs. It benchmarks the implementation selected by the build, including architecture overrides or generic fallbacks.

## Risks
The benchmark mutates copied bitmaps in first-bit tests and can take noticeable CPU time. It prints with `pr_err()` for visibility, which can look like a failure even though the final `-EINVAL` is intentional. Random input means timings vary run to run. It is not a correctness oracle; comments explicitly rely on boot coverage for broad correctness.

## Test Signals
Successful execution prints all benchmark lines for random and sparse phases, with plausible iteration counts. Compare timings across kernel changes or architectures. Confirm that returning `-EINVAL` does not leave the module loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/find_bit_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/find_bit_benchmark_rust.rs -->
# sources/distributed-fs/ceph-client/lib/find_bit_benchmark_rust.rs

## Purpose
Rust benchmark module for measuring `BitmapVec` traversal methods analogous to C `find_next_bit` and `find_next_zero_bit` behavior. It is focused on Rust bitmap API performance.

## Important APIs, Types, and Functions
Defines module type `Benchmark`, constants `BITMAP_LEN` and `SPARSENESS`, helper functions `test_next_bit()`, `test_next_zero_bit()`, and `find_bit_test()`, and a `kernel::Module` implementation whose `init()` runs the benchmark then returns `Err(code::EINVAL)`.

## Control Flow
Initialization allocates a `BitmapVec`, fills it randomly, times `next_bit()` and `next_zero_bit()` loops using `Instant<Monotonic>`, prints results, then allocates a sparse bitmap, sets random bits through the kernel binding `__get_random_u32_below()`, repeats the traversal timings, and returns `EINVAL` so the module can be reloaded for repeated runs.

## State and Persistence
All state is stack/local Rust-owned bitmap allocation during init. Because init returns an error, no module instance persists.

## Dependencies and Integration Points
Depends on Rust-for-Linux kernel prelude, `BitmapVec`, allocation flags, monotonic time, printk macros, `ThisModule`, and a raw binding for random bounded integers. It benchmarks Rust API behavior relative to the C benchmark in the same directory.

## Risks
Allocation failure panics via `expect()`, appropriate for a benchmark but not production style. The unsafe random binding must receive a valid bound, which it does through `BITMAP_LEN.try_into().unwrap()`. Hardened bitmap bounds require explicit loop break when `i == BITMAP_LEN`. Like the C benchmark, timing varies with random data and system load.

## Test Signals
Build with Rust support, insert the module, and verify printed random/sparse timing lines and intentional `EINVAL` init failure. Compare iteration counts with expected bitmap density and watch for hardened-bounds warnings or allocation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/find_bit_benchmark_rust.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/flex_proportions.c -->
# sources/distributed-fs/ceph-client/lib/flex_proportions.c

## Purpose
Implements floating proportions with exponential aging and lazy per-type period reflection. Callers can maintain a global event denominator and local per-type numerators, then query smoothed proportions without iterating all event types every period.

## Important APIs, Types, and Functions
Global APIs are `fprop_global_init()`, `fprop_global_destroy()`, and `fprop_new_period()`. Per-CPU local APIs are `fprop_local_init_percpu()`, `fprop_local_destroy_percpu()`, `__fprop_add_percpu()`, `fprop_fraction_percpu()`, and `__fprop_add_percpu_max()`. Internal `fprop_reflect_period_percpu()` lazily ages one local counter to the current global period. `PROP_BATCH` sizes percpu counter batching by CPU count.

## Control Flow
Global initialization starts the denominator at one to avoid zero-event periods and initializes a seqcount. `fprop_new_period()` sums global events, subtracts the aged-away portion, increments the period under seqcount write protection, and returns whether further aging matters. Local add paths first reflect period changes for that local counter, then add to local and global percpu counters. Fraction queries read under seqcount retry, reflect local aging, read positive local/global counters, and clamp denominator so the fraction remains valid. Max-add computes whether adding `nr` would exceed a configured fraction and truncates or skips the add.

## State and Persistence
State is caller-owned in `struct fprop_global` and `struct fprop_local_percpu`: percpu counters, period numbers, seqcount, and local raw spinlock. No global state or allocation beyond percpu counter initialization is owned here.

## Dependencies and Integration Points
Depends on `linux/flex_proportions.h`, percpu counters, seqcount, raw spinlocks, interrupt save/restore, and 64-bit division helpers. It is used by subsystems that need throttling or proportional accounting with aging, such as writeback-style balancing.

## Risks
Callers must serialize `fprop_new_period()` externally as documented. PerCPU counter approximation can temporarily make numerator exceed denominator; the function clamps output but callers should expect approximate fractions. Period jumps of at least `BITS_PER_LONG` zero local counters. Max-add arithmetic must avoid overflow for large `nr`/denominator combinations.

## Test Signals
Test initialization/destruction, period advancement with no events and many events, lazy local aging, fraction normalization, max-fraction saturation, concurrent readers during period changes, and large period jumps. Integration tests should validate smooth proportional throttling behavior over time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/flex_proportions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/Kconfig -->
# sources/distributed-fs/ceph-client/lib/fonts/Kconfig

## Purpose
Defines Kconfig options for kernel compiled-in console/display fonts under `FONT_SUPPORT`. It lets framebuffer, STI, DRM panic, and DRM client log users select specific bitmap fonts and auto-selects a safe default when none is chosen.

## Important APIs, Types, and Functions
This is configuration data rather than C code. Key symbols are `FONT_SUPPORT`, `FONTS`, individual font booleans such as `FONT_8x8`, `FONT_8x16`, `FONT_10x18`, Terminus and Sun font options, and `FONT_AUTOSELECT`, which selects `FONT_8x16` when no explicit font option is enabled.

## Control Flow
Kconfig visibility and defaults depend on console/display symbols and architecture predicates. `FONTS` gates most user-visible choices. Several fonts have architecture/platform defaults when `FONTS` is not selected. `FONT_AUTOSELECT` is a derived bool that depends negatively on every explicit font choice and selects `FONT_8x16`.

## State and Persistence
The state is build-time `.config` symbol selection. It persists in kernel configuration and controls which font objects are compiled.

## Dependencies and Integration Points
Integrates with `lib/fonts/Makefile`, framebuffer console, STI console, DRM panic/log paths, SPARC, ARM/Acorn, Amiga/Mac defaults, BOOTX text, and early framebuffer support. Selected symbols determine available `font_desc` objects for `font.c`.

## Risks
Dependency expressions must match driver capabilities; selecting an unsupported font can waste space or fail display expectations. `FONT_AUTOSELECT` must be kept in sync with every individual font option. Some options are hidden unless `FONTS` is enabled, so defaults are important for noninteractive configs.

## Test Signals
Run Kconfig builds for framebuffer, DRM panic, SPARC, ARM Acorn, Mac, and minimal configurations. Verify `FONT_AUTOSELECT` selects `FONT_8x16` only when no other font is selected and that Makefile object inclusion matches selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/Makefile -->
# sources/distributed-fs/ceph-client/lib/fonts/Makefile

## Purpose
Build rules for the kernel font library. It composes the font support object from common font handling code, optional rotation support, and selected built-in bitmap font objects.

## Important APIs, Types, and Functions
This is kbuild data. `font-y` starts with `fonts.o`, conditionally adds `font_rotate.o` for `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION`, conditionally adds `font_*.o` objects for each `CONFIG_FONT_*`, and finally adds `font.o` to `obj-*` when `CONFIG_FONT_SUPPORT` is enabled.

## Control Flow
Kbuild expands `font-y` based on configuration and links the selected objects into the composite `font.o`. The top-level `obj-$(CONFIG_FONT_SUPPORT)` controls whether the composite is built at all.

## State and Persistence
No runtime state exists. Build outputs are determined by `.config`.

## Dependencies and Integration Points
Depends on symbols defined in `lib/fonts/Kconfig` and source files in the same directory. It integrates with kernel kbuild composite-object semantics and the console font selection code that expects selected `font_desc` objects to be linked.

## Risks
Kconfig/Makefile drift can produce selectable fonts that are never linked, or linked objects that cannot be selected. Object order is documented as sorted by family-size, which should remain stable if consumers depend on predictable built-in ordering.

## Test Signals
Build with each `CONFIG_FONT_*` symbol enabled individually and in combinations, check that expected objects appear in build logs, and verify rotation object inclusion with `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font.h -->
# sources/distributed-fs/ceph-client/lib/fonts/font.h

## Purpose
Private font-library header defining the storage wrapper for compiled bitmap font data and stable indices for built-in fonts.

## Important APIs, Types, and Functions
Defines `FONT_EXTRA_WORDS`, `struct font_data` with `extra[4]` metadata and a flexible `data[]` byte array, and numeric index macros such as `VGA8x8_IDX`, `FONT10x18_IDX`, `TER16x32_IDX`, and `TER10x18_IDX`. It includes public `linux/font.h` for `struct font_desc`.

## Control Flow
No executable control flow. Font source files include this header to wrap glyph bytes and assign `font_desc.idx` values.

## State and Persistence
No mutable state. The macros and packed struct define compile-time data layout.

## Dependencies and Integration Points
Integrates with all `font_*.c` files and common font handling code. The `struct font_data` layout lets font blobs carry extra metadata before raw glyph bytes while still exposing `data` to `struct font_desc`.

## Risks
Index values must stay aligned with font registration/lookup expectations. Changing `struct font_data` packing or `FONT_EXTRA_WORDS` would affect every compiled font object. New fonts require coordinated Kconfig, Makefile, index, and descriptor updates.

## Test Signals
Compile all font objects, verify `font_desc.idx` uniqueness, and test font lookup/selection paths for each index. Static review should confirm new fonts update this header consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_10x18.c -->
# sources/distributed-fs/ceph-client/lib/fonts/font_10x18.c

## Purpose
Defines the built-in 10x18 bitmap console font. The file is mostly static glyph data adapted from `font_sun12x22.c`, plus a `struct font_desc` that registers the font with the kernel font library.

## Important APIs, Types, and Functions
The main data object is `static const struct font_data fontdata_10x18`, with `FONTDATAMAX` set to 9216 bytes. It stores 256 glyphs, each 10 pixels wide by 18 rows high, encoded as two bytes per row with comments showing the 10-bit bitmap. The exported descriptor is `const struct font_desc font_10x18` with `.idx = FONT10x18_IDX`, `.name = "10x18"`, `.width = 10`, `.height = 18`, `.charcount = 256`, `.data = fontdata_10x18.data`, and `.pref` of `5` on SPARC or `-1` elsewhere.

## Control Flow
There is no executable control flow. When `CONFIG_FONT_10x18` is selected, kbuild links this object, and the font library can discover/use `font_10x18` through compiled-in font descriptors.

## State and Persistence
All state is read-only compiled data in the kernel image or module object. No allocation, mutation, locking, or persistence beyond the selected kernel build exists.

## Dependencies and Integration Points
Depends on `font.h`, `struct font_desc` from `linux/font.h`, the `FONT10x18_IDX` index, Kconfig symbol `FONT_10x18`, and Makefile object selection. Consumers are framebuffer/DRM panic console font paths that render fixed-width bitmap glyphs.

## Risks
Data-size consistency is the main risk: 256 glyphs * 18 rows * 2 bytes = 9216 bytes, matching `FONTDATAMAX`. Any glyph-data truncation, row-count drift, or width/height mismatch would corrupt rendering. The SPARC preference affects default font selection. Because most of the file is literal bitmap data, accidental edits are hard to review visually.

## Test Signals
Build with `CONFIG_FONT_10x18`, verify `font_10x18` is linked and selectable, render representative ASCII/control/high-half glyphs on framebuffer or DRM panic paths, and check that glyph stride matches width/height. Static checks should confirm data length equals `FONTDATAMAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_10x18.c -->
