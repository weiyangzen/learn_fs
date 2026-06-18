# Group Research: group_1758_spdk_sources_virtualization_spdk_lib_trace_trace_c_sources_virtuali_6f8c230f23df

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/trace/trace.c -->
# File Research: sources/virtualization/spdk/lib/trace/trace.c

This file implements SPDK trace shared-memory initialization, trace event recording, per-core/per-user-thread trace histories, and cleanup.

`_spdk_trace_record()` is the hot path. It selects a per-lcore trace history from the current SPDK env core or from thread-local user-thread registration, fills the next circular trace entry, validates the runtime argument count against the registered tracepoint definition, copies integer/pointer/string arguments across one or more `spdk_trace_entry_buffer` slots, null-terminates truncated strings, issues a write memory barrier, and advances `history->next_entry`.

`spdk_trace_init()` builds the shared-memory file layout. It sizes sections for main metadata, owner records, tracepoint masks, owner types, object types, tracepoint definitions, lcore offsets, and all per-core/user-thread histories. It opens/truncates/mmaps the shm object, mlocks on Linux, zeroes the file, initializes section offsets and counts, assigns histories for each SPDK env core and configured user thread slot, then calls `trace_flags_init()` to register trace definitions and owner-id allocation.

User thread support is managed by `spdk_trace_register_user_thread()` and `spdk_trace_unregister_user_thread()`. They require callers not to be on a dedicated SPDK core, allocate a slot from `g_ut_array`, map it to the trace history index range after dedicated cores, store the pthread name, and keep the selected history in thread-local storage.

`spdk_trace_cleanup()` finalizes trace flags, decides whether to unlink the shm object only when no trace entries were recorded, unmaps/closes the trace file, frees the user-thread bit array, and leaves recorded trace files available for postmortem debugging.

Important invariants are the shared-memory section layout, power-of-two circular trace history indexing, matching tracepoint argument definitions, buffer-continuation entries using `SPDK_TRACE_MAX_TPOINT_ID`, and the memory barrier before advancing `next_entry`. The cleanup path unmaps only `sizeof(struct spdk_trace_file)` rather than the full mapped size as read, which is worth checking if changing trace-file lifetime behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/trace/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/trace/trace_flags.c -->
# File Research: sources/virtualization/spdk/lib/trace/trace_flags.c

This file manages tracepoint group registration, trace masks, tracepoint metadata, owner/object metadata, and owner-id allocation.

Trace masks live in the trace shared-memory tpoint-mask section. `spdk_trace_get_tpoint_mask()`, `spdk_trace_set_tpoints()`, and `spdk_trace_clear_tpoints()` operate on one group; group-mask helpers enable or disable all tracepoints in selected groups. `spdk_trace_create_tpoint_mask()` maps a tracepoint name to its bit inside a group, while `spdk_trace_create_tpoint_group_mask()` maps a group name, or `"all"`, to a group bitmask.

Registration functions are accumulated in `g_reg_fn_head` by `spdk_trace_add_register_fn()`, which rejects missing names, the reserved name `"all"`, duplicate group IDs, and duplicate names, then keeps the list sorted by group ID. `trace_flags_init()` invokes each registered function so modules can populate tracepoint definitions after the trace file exists.

Trace metadata registration writes into shared sections. `spdk_trace_register_owner_type()` and `spdk_trace_register_object()` register display prefixes. `spdk_trace_register_description_ext()` copies tracepoint names, object/owner types, new-object markers, and argument descriptors with type/size validation. The older `spdk_trace_register_description()` wrapper registers a single 64-bit argument. `spdk_trace_tpoint_register_relation()` records relationships between tracepoint arguments and object types for parser correlation.

Owner IDs are allocated from a spinlock-protected ring. IDs start at 256, reserving 0 for no-owner and avoiding collisions with legacy poller IDs. `spdk_trace_register_owner()` stamps type, timestamp, and description; unregister returns the ID to the ring; description setters can replace or append text. These APIs are no-ops in unit-test contexts where the ring is not initialized.

`spdk_trace_mask_usage()` prints CLI usage text listing registered trace groups and mask syntax. `spdk_trace_clear()` records `clear_tsc`, which parsers use to suppress older events.

Key invariants are unique sorted trace groups, valid tracepoint IDs and argument shapes, owner ring balance, and shared-memory initialization before metadata writes. The owner description helper assumes `description` is non-null and formats into a fixed per-owner description region.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/trace/trace_flags.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/trace/trace_internal.h -->
# File Research: sources/virtualization/spdk/lib/trace/trace_internal.h

This private trace header declares the internal functions shared between the trace core, trace flags, and trace RPC layer.

It exposes `trace_get_shm_name()` for reporting the active shared-memory object name, plus `trace_flags_init()` and `trace_flags_fini()` for trace definition registration and owner-id allocator lifecycle.

The header intentionally keeps the internal surface small; public trace data structures and APIs come from `spdk/trace.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/trace/trace_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/trace/trace_rpc.c -->
# File Research: sources/virtualization/spdk/lib/trace/trace_rpc.c

This file exposes JSON-RPC controls for SPDK tracing.

`trace_set_tpoint_mask` and `trace_clear_tpoint_mask` decode a trace group name and 64-bit tracepoint mask, map the group name to a single group bit, convert that bit to a group ID with `spdk_u64log2()`, and update that group’s mask. `trace_enable_tpoint_group` and `trace_disable_tpoint_group` decode a group name and enable or disable all tracepoints for that group, including the special `"all"` group handled by trace flags.

`trace_get_tpoint_group_mask` returns the aggregate enabled group mask plus a per-group object containing whether the group is enabled, the group mask bit, the current tracepoint mask, and all named tracepoints with local IDs and enabled state. It walks registered trace groups and the tracepoint section.

`trace_clear` requires no parameters and records the current clear timestamp through `spdk_trace_clear()`. `trace_get_info` reports the `/dev/shm...` tracepoint shared-memory path, aggregate group mask, and per-group mask data.

All RPCs are registered for runtime use; most are also valid at startup. Parameter validation is strict for missing names and unexpected parameters. The file assumes `g_trace_file` is valid for introspective RPCs; `trace_get_tpoint_group_mask` directly reads the tracepoint section while iterating groups.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/trace/trace_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/trace_parser/Makefile -->
# File Research: sources/virtualization/spdk/lib/trace_parser/Makefile

This Makefile builds the `trace_parser` SPDK library.

It sets `SPDK_ROOT_DIR`, includes common SPDK make rules, declares shared-library version `SO_VER := 8` and `SO_MINOR := 0`, compiles `trace.cpp` as the C++ source, names the library `trace_parser`, links `-lrt`, uses `spdk_trace_parser.map`, and includes the standard SPDK library makefile.

The library is a small standalone parser component for trace shared-memory/files rather than part of the trace writer hot path.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/trace_parser/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/trace_parser/trace.cpp -->
# File Research: sources/virtualization/spdk/lib/trace_parser/trace.cpp

This file implements the C++ backing object for the C trace parser API. It maps a trace file or shm object read-only, reconstructs chronological trace entries, decodes arguments, and tracks object relationships.

`spdk_trace_parser::init()` opens either a regular file or shm object, maps the header to get the full trace-file size, remaps the full file, and populates an ordered `std::map` keyed by timestamp and lcore. It can parse all lcores or one selected lcore. For all-lcore mode, it detects whether any history ring overflowed; if so, it sets `_tsc_offset` to the highest first timestamp among overflowed histories and suppresses older events so output covers a common time window.

`populate_events()` handles circular trace histories. When a ring is full, it finds the earliest and latest timestamp positions; otherwise it walks from entry zero through the filled prefix. Entries with continuation tpoint IDs are skipped, and entries before the trace clear timestamp are ignored.

`next_entry()` returns decoded parser entries in sorted order. It attaches the source trace entry, lcore, thread name, object index/start time for tracepoints tied to object types, and related-object metadata when tracepoint relation descriptors match a previously seen object. New-object tracepoints create stable per-object indexes.

Argument decoding uses `argument_context` to copy argument bytes from the initial trace entry and continuation buffers. `build_arg()` validates continuation buffer markers and timestamps, copies into the fixed parser argument union, and zeroes integer storage before partial-width copies.

The exported C API wraps object construction/destruction and methods: `spdk_trace_parser_init()`, cleanup, file access, TSC offset, next-entry iteration, and per-lcore entry count. Construction failures are caught and converted to `NULL`.

Important invariants are trace-file size validation before full mmap, continuation-buffer integrity, sorted event ordering with duplicate timestamp tie-breaks by lcore, and object correlation state that depends on chronological iteration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/trace_parser/trace.cpp -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ublk/Makefile -->
# File Research: sources/virtualization/spdk/lib/ublk/Makefile

This Makefile builds SPDK’s Linux ublk integration library.

It compiles `ublk.c` and `ublk_rpc.c` into library `ublk`, sets shared-library version `SO_VER := 5` and `SO_MINOR := 0`, links against `liburing`, uses `spdk_ublk.map`, and includes the standard SPDK common and library make fragments.

The `-luring` dependency reflects that both control-plane and I/O queues are driven through io_uring commands.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ublk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ublk/ublk.c -->
# File Research: sources/virtualization/spdk/lib/ublk/ublk.c

This file implements SPDK’s Linux ublk target: it exposes SPDK bdevs as kernel block devices through `/dev/ublk-control`, per-device character devices, io_uring command queues, SPDK threads, and bdev I/O translation.

Global target state is held in `g_ublk_tgt`: control fd, control ring, control poller, feature flags, poll groups, active/destroying state, and device count. Poll groups own SPDK threads, an iobuf channel, and queues assigned for polling. Each `spdk_ublk_dev` tracks the opened bdev, ublk device info/params, queue array, control callback, in-flight control ops, closing/recovery state, and list links. Each queue owns an io_uring, mapped kernel request descriptors, per-tag `ublk_io` structures, and inflight/completed lists.

Target creation parses an optional CPU mask, opens `/dev/ublk-control`, reads kernel `ublks_max`, initializes the control io_uring with SQPOLL and SQE128, reads kernel features, registers the `ublk` iobuf module, creates one SPDK thread per selected core, binds those threads, initializes pollers/iobuf channels, and starts a periodic control poller on the app thread. Feature handling supports ioctl-encoded commands, user-copy I/O, and user recovery, with an RPC option to disable user copy.

The control path submits ublk commands via `UBLK_CMD_ADD_DEV`, `SET_PARAMS`, `START_DEV`, `STOP_DEV`, `DEL_DEV`, `GET_DEV_INFO`, `START_USER_RECOVERY`, and `END_USER_RECOVERY`. Completion handling chains startup from add to params to start, deletes partially created devices on errors, retries `GET_DEV_INFO` while the kernel device is not quiesced, and invokes the caller callback when a logical operation completes.

Disk start opens the named SPDK bdev for write, derives sector/block shifts, clamps queue count and depth to SPDK limits, initializes ublk device info and params from bdev geometry and supported I/O types, allocates queue I/O arrays, registers the device in `g_ublk_devs`, and submits `ADD_DEV`. After `START_DEV`, it opens `/dev/ublkc<ID>`, initializes each queue, and distributes queues round-robin across ublk poll groups.

Queue initialization mmaps kernel request descriptors at the ublk command-buffer offset, initializes each tag as `UBLK_IO_FETCH_REQ`, creates an SQE128 io_uring, registers the device fd as a fixed file, and preposts all fetch commands. A small temporary buffer is used for older kernels that require a buffer even when `NEED_GET_DATA` is set.

The I/O path converts ublk operations into SPDK bdev operations. Reads allocate iobuf payloads and submit `spdk_bdev_read_blocks`; writes either request data from the kernel first or use user-copy read into the payload, then submit `spdk_bdev_write_blocks`; flush maps to full-device flush; discard maps to unmap; write-zeroes maps to write-zeroes. `-ENOMEM` bdev submissions are queued through `spdk_bdev_queue_io_wait()` for resubmission.

Completed bdev I/O is moved from the inflight list to the completed list, marked as `UBLK_IO_COMMIT_AND_FETCH_REQ`, and committed back to the kernel by `ublk_io_xmit()`. For user-copy reads, bdev completion queues a kernel write from the payload into the ublk user-copy buffer before the final commit. For user-copy writes, the kernel read completes before the bdev write is submitted. Buffers are returned to the poll group’s iobuf channel after the kernel has synchronously consumed read data in the submit context.

Shutdown is multi-stage. `ublk_stop_disk()` submits `STOP_DEV`; queue polling detects abort/stop conditions, waits until inflight I/O, completed results, and ring commands are drained, removes queues from poll groups, releases bdev channels, and notifies the app thread. Device deletion closes queue rings, unmaps command buffers, closes cdev fd, submits `DEL_DEV`, frees per-queue buffers on their owning threads, closes the bdev descriptor, unregisters the device, and frees memory. Target fini iterates all devices, waits for the global device list to empty, closes control resources, exits ublk threads, and invokes the final callback.

Recovery support uses `GET_DEV_INFO`, updates queue/depth from kernel state, reinitializes queues and parameters, submits `START_USER_RECOVERY`, restarts queue polling, then sends `END_USER_RECOVERY` after all queues are online.

Key invariants are app-thread ownership of control/device list mutations, poll-group-thread ownership of queue polling and iobuf channels, balanced `cmd_inflight` and control-op counters, draining queues before deletion, correct sector-to-block shifting, and preserving buffer lifetime until kernel ublk has consumed or produced data. The code assumes Linux ublk/io_uring command semantics and contains compatibility paths for older and newer kernel feature sets.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ublk/ublk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ublk/ublk_internal.h -->
# File Research: sources/virtualization/spdk/lib/ublk/ublk_internal.h

This internal header defines ublk compatibility constants and the private control API used by the ublk RPC layer.

It includes Linux `ublk_cmd.h`, supplies fallback definitions for newer kernel features such as `UBLK_F_CMD_IOCTL_ENCODE`, `UBLK_F_USER_COPY`, `UBLK_U_CMD_GET_FEATURES`, and user-copy buffer offset/tag/qid layout constants, then defines default queue depth and queue count.

The declared internal APIs cover target creation/destruction, disk start/stop/recovery, device lookup and iteration, and device metadata accessors for ID, bdev name, queue depth, and queue count.

The header keeps kernel-version compatibility details localized so `ublk.c` can compile against older headers while probing actual runtime features from the kernel.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ublk/ublk_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ublk/ublk_rpc.c -->
# File Research: sources/virtualization/spdk/lib/ublk/ublk_rpc.c

This file exposes JSON-RPC methods for the ublk target and ublk-backed disks.

`ublk_create_target` decodes optional `cpumask` and `disable_user_copy`, calls `ublk_create_target()`, and returns a boolean. `ublk_destroy_target` calls the async destroy helper and sends the response from `ublk_destroy_target_done()` after teardown completes.

`ublk_start_disk` decodes `bdev_name`, `ublk_id`, and optional `num_queues`/`queue_depth` with defaults from `ublk_internal.h`. It heap-allocates request context because disk creation is asynchronous, then returns the ublk ID on completion or a JSON-RPC error on failure.

`ublk_stop_disk` decodes `ublk_id`, calls `ublk_stop_disk()`, and returns from an async completion callback. As read, its completion callback always sends boolean success and ignores the callback `rc`, while immediate start errors are returned as JSON-RPC errors.

`ublk_get_disks` optionally filters by `ublk_id`; otherwise it iterates all ublk devices. Each object reports `/dev/ublkb<ID>`, numeric ID, queue depth, queue count, and backing bdev name.

`ublk_recover_disk` decodes `bdev_name` and `ublk_id` and calls `ublk_start_disk_recovery()`. Unlike normal disk start, it passes no control callback and immediately sends a response based on command submission return code, not final recovery completion.

The file relies on generated RPC context free helpers from `spdk_internal/rpc_autogen.h` and the internal ublk API. All RPCs are runtime-registered.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ublk/ublk_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ut/Makefile -->
# File Research: sources/virtualization/spdk/lib/ut/Makefile

This Makefile builds SPDK’s CUnit-based unit-test helper library.

It compiles `ut.c` into library `ut`, sets shared-library version `SO_VER := 4` and `SO_MINOR := 0`, links `-lcunit`, uses `spdk_ut.map`, and includes standard SPDK make fragments.

The library centralizes common unit-test CLI handling and CUnit execution for SPDK test binaries.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ut/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ut/ut.c -->
# File Research: sources/virtualization/spdk/lib/ut/ut.c

This file implements SPDK’s common unit-test runner around CUnit.

It supports built-in options `--test/-t`, `--suite/-s`, `--list/-l`, and `--help/-h`, and can merge caller-provided long options, short option string, option callback, init callback, and usage callback through `spdk_ut_opts`.

`parse_args()` builds the combined option table and optstring, validates maximum option counts and optstring size, records selected test/suite/action, and dispatches unknown recognized options to the caller callback. Tests run by default.

`run_tests()` validates requested suite and/or test names. If a test is selected without a suite, it allows that only when exactly one suite is registered. It configures CUnit to abort on framework errors and run in verbose basic mode, then runs one test, one suite, or all tests. The return value is the number of CUnit failures.

`list_tests()` prints all registered suites and test cases. `spdk_ut_run_tests()` is the exported entry point: parse arguments, print help/list, call optional init callback before running tests, and return a process-style status.

Key invariants are correct ownership of caller-supplied option arrays, no dynamic allocation, and returning nonzero for invalid CLI usage or test failures. The code uses CUnit’s one-based suite/test positional API.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ut/ut.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ut_mock/Makefile -->
# File Research: sources/virtualization/spdk/lib/ut_mock/Makefile

This Makefile builds SPDK’s unit-test mock helper library.

It compiles `mock.c` into library `ut_mock`, sets shared-library version `SO_VER := 8` and `SO_MINOR := 0`, uses the blank SPDK linker map, and includes common library build rules.

The library is meant to be linked by tests that use linker wrapping and the `spdk_internal/mock.h` wrapper infrastructure.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ut_mock/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ut_mock/mock.c -->
# File Research: sources/virtualization/spdk/lib/ut_mock/mock.c

This file defines generic linker-wrapper hooks for SPDK unit tests.

`DEFINE_WRAPPER` creates wrappers for `calloc`, `pthread_mutex_init`, `pthread_mutexattr_init`, `recvmsg`, `sendmsg`, and `writev`, allowing tests to override or observe those calls through the mock framework.

It also defines a custom `__wrap_unlink()`. The wrapper succeeds only when `g_unlink_path` is set and matches the requested path; otherwise it returns `ENOENT`. If `g_unlink_callback` is set, it is invoked before success.

The notable behavior is that `__wrap_unlink()` returns positive `ENOENT`, not `-1` with `errno` set, so tests using it need to match this mock convention rather than POSIX unlink behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ut_mock/mock.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/Makefile -->
# File Research: sources/virtualization/spdk/lib/util/Makefile

This Makefile builds SPDK’s general-purpose `util` library.

It compiles utility sources including base64, bit arrays, cpuset, CRCs, DIF, fd groups, file helpers, hex/iov/math/net/pipe/string/uuid/xor/zipf/md5, sets shared-library version `SO_VER := 12` and `SO_MINOR := 0`, conditionally links `libuuid`, OpenSSL, and ISA-L, adds `-Wpointer-arith`, uses `spdk_util.map`, and includes standard SPDK build rules.

The listed files in this group are only a subset of the utility library’s source list.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/base64.c -->
# File Research: sources/virtualization/spdk/lib/util/base64.c

This file implements scalar Base64 and URL-safe Base64 encode/decode, with ARM fast paths included at compile time on AArch64.

The encode path validates non-null destination/source and nonzero length, optionally lets NEON or SVE consume large chunks, then encodes remaining input using big-endian 24-bit groups into four Base64 characters. Tail handling emits `=` padding for one- or two-byte leftovers and null-terminates the destination.

The decode path validates the source string, requires input length to be a nonzero multiple of four, strips up to two trailing padding characters, rejects impossible unpadded lengths where `len % 4 == 1`, and optionally reports decoded length through `spdk_base64_get_decoded_len()`. If `dst` is `NULL`, it returns after length calculation. Otherwise, ARM vector code may consume a prefix, and scalar code decodes full groups using lookup tables, rejects invalid characters marked `255`, and carefully handles the final group without overrunning the caller’s output size.

`spdk_base64_encode()` and `spdk_base64_decode()` use the standard `+/` alphabet. `spdk_base64_urlsafe_encode()` and `spdk_base64_urlsafe_decode()` use `-_`.

Important invariants are caller-provided output sizing, padding validation before decode, scalar validation of any vector-unconsumed tail, and the direct inclusion of `base64_neon.c` or `base64_sve.c` only on AArch64.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/base64.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/base64_neon.c -->
# File Research: sources/virtualization/spdk/lib/util/base64_neon.c

This file provides AArch64 NEON acceleration helpers included by `base64.c` when SVE is unavailable.

`base64_encode_neon64()` processes 48 input bytes at a time into 64 output bytes. It deinterleaves input with `vld3q_u8`, shifts three input byte streams into four 6-bit streams, uses a 64-byte table lookup to map values to the selected Base64 alphabet, interleaves with `vst4q_u8`, and advances caller-owned source/destination/length pointers.

`base64_decode_neon64()` processes 64 encoded bytes at a time into 48 decoded bytes. It uses two 64-byte lookup tables and NEON table lookup instructions to classify ASCII ranges, rejects chunks with any value greater than 63, converts four 6-bit streams back to three 8-bit streams, stores with `vst3q_u8`, and advances pointers.

The file defines separate standard and URL-safe decode tables arranged for NEON lookup. It has a compile-time guard rejecting non-AArch64 builds and is not compiled as an independent translation unit in this Makefile path.

Key invariant: on invalid input, the NEON decode loop stops without consuming that chunk, leaving scalar decode in `base64.c` to perform final validation and return `-EINVAL`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/base64_neon.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/base64_sve.c -->
# File Research: sources/virtualization/spdk/lib/util/base64_sve.c

This file provides AArch64 SVE acceleration helpers included by `base64.c` when SVE is available.

It implements generic table-lookup helpers for 2, 3, 4, and 8 SVE vectors, selected based on runtime vector length. These helpers combine `svtbl` lookups across table segments and report invalid decode values marked `255`.

`base64_encode_sve()` computes the largest input prefix divisible by three, then handles vector lengths of 16, 32/48, or at least 64 bytes with different table-loading strategies. For each predicate-sized batch, it loads/deinterleaves three input streams, converts 8-bit input bytes into four 6-bit streams, maps those through the selected encoding table, stores four interleaved output streams, and advances caller-owned source/destination/length pointers.

`base64_decode_sve()` similarly handles vector lengths from 16 through 128+ bytes. It loads four encoded streams, rejects input bytes >= 128, maps characters through the decode table using the vector-length-specific helper, rejects invalid decoded values, converts four 6-bit streams into three output byte streams, stores them, and advances pointers.

The functions are void fast paths; invalid decode data causes an early return with the remaining input left for scalar validation in `base64.c`. The implementation assumes the caller has already done Base64 padding and length sanity checks.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/base64_sve.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/bit_array.c -->
# File Research: sources/virtualization/spdk/lib/util/bit_array.c

This file implements SPDK dynamic bit arrays and a bit-pool allocator built on top of them.

`spdk_bit_array_resize()` uses 64-bit words, rejects `UINT32_MAX` capacity because that sentinel means not-found, and allocates one extra sentinel word. The sentinel is set to `0b10`, allowing `find_first_set` and `find_first_clear` to scan without explicit loop bounds and still detect end-of-array. Growing zeroes new words; shrinking clears now-out-of-range bits in a partial final word.

Bit-array APIs support create/free, capacity, get/set/clear, find-first-set, find-first-clear, count set/clear bits, store/load masks, and clear-mask. Out-of-range get returns false, set returns `-EINVAL`, and clear is a no-op.

`spdk_bit_pool` wraps a bit array with `lowest_free_bit` and `free_count`. It supports create, create from existing array, free, resize, capacity, allocation status, allocate next free bit, mark a specific bit allocated, free a bit, count allocated/free, store/load mask, and free all bits. Allocation updates `lowest_free_bit` by scanning from the allocated position; freeing lowers it when appropriate.

Important invariants are the sentinel extra word, keeping bits past `bit_count` clear, `free_count` matching the underlying mask, and only freeing allocated pool bits. There is a small cleanup issue in `ublk_ios_init` style not here; in this file the main risk is that mask load/store assumes caller-provided buffers are large enough for the bit capacity.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/bit_array.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/cpuset.c -->
# File Research: sources/virtualization/spdk/lib/util/cpuset.c

This file implements fixed-size SPDK CPU-set allocation, mutation, formatting, iteration, and parsing.

Basic operations allocate/free sets, compare, copy, negate, bitwise and/or/xor, zero, set/get individual CPUs, iterate set CPUs, and count CPUs. CPU index setters/getters assert the index is within the fixed `cpus` byte array.

`spdk_cpuset_fmt()` formats the bitmask as a compact lowercase hexadecimal string without leading zero high nibbles, writing into the set’s internal `str` buffer. It scans for the highest set CPU and formats bytes from high to low.

Parsing supports two formats. Hex masks may have optional `0x`/`0X` prefix and may contain comma delimiters like Linux cpumasks; parsing walks the string right-to-left and maps hex nibbles to CPU bits. List masks start with `[` and support comma-separated CPU numbers and ranges with optional blanks, such as `[0,2-4]`; invalid syntax, out-of-range CPUs, reversed ranges, and conversion errors are logged and rejected.

Important invariants are fixed `SPDK_CPUSET_SIZE`, internal formatting buffer ownership, and strict parse rejection. List parsing stops at `]` and does not require trailing text validation beyond that point as read, so callers should pass clean mask strings.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/cpuset.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/crc16.c -->
# File Research: sources/virtualization/spdk/lib/util/crc16.c

This file implements CRC16 T10-DIF update and copy helpers.

When SPDK is built with ISA-L, `spdk_crc16_t10dif()` and `spdk_crc16_t10dif_copy()` directly call ISA-L’s `crc16_t10dif` and `crc16_t10dif_copy` implementations.

Without ISA-L, the file uses a large precomputed 16-by-256 table for a sliced table-driven CRC. `crc_update_fast()` processes 16 bytes per iteration by combining table lookups for the current CRC high/low bytes and the next 14 data bytes, then processes any remaining bytes one at a time. `crc16_table_t10dif()` initializes from the caller-provided CRC and returns the final 16-bit value.

`spdk_crc16_t10dif_copy()` in the non-ISA-L path performs `memcpy(dst, src, len)` before computing the CRC over `src`.

The file’s behavior is deterministic and stateless. Key assumptions are non-null buffers for nonzero lengths and that callers provide a valid destination for the copy variant.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/crc16.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/crc32.c -->
# File Research: sources/virtualization/spdk/lib/util/crc32.c

This file provides shared CRC32 table initialization and generic update routines used by CRC32 IEEE and CRC32C fallback paths.

`crc32_table_init()` fills a 256-entry reflected-polynomial lookup table by shifting each byte through eight polynomial steps.

`crc32_update()` has two implementations. On ARM with CRC instructions, it processes unaligned head bytes, aligned 64-bit middle words via `__crc32d`, and tail bytes via `__crc32b`; the table parameter is unused on this path. Otherwise, it performs the standard byte-at-a-time reflected table update: `(crc >> 8) ^ table[(crc ^ byte) & 0xff]`.

Important invariants are reflected polynomial tables and caller-controlled CRC seed/finalization. The hardware path tries to avoid unaligned 64-bit loads by splitting head/middle/tail.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/crc32_ieee.c -->
# File Research: sources/virtualization/spdk/lib/util/crc32_ieee.c

This small file implements the IEEE CRC32 public update function.

A constructor initializes a static `spdk_crc32_table` with `SPDK_CRC32_POLYNOMIAL_REFLECT`. `spdk_crc32_ieee_update()` then delegates to `crc32_update()` with that table, the caller buffer/length, and caller-provided CRC seed.

The function does not invert the CRC before or after update; callers are responsible for any protocol-specific initialization/finalization.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/crc32_ieee.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/crc32c.c -->
# File Research: sources/virtualization/spdk/lib/util/crc32c.c

This file implements CRC32C update helpers with ISA-L, x86 SSE4.2, ARM CRC, or table fallback dispatch selected at compile time.

With ISA-L, `spdk_crc32c_update()` calls `crc32_iscsi()`. With SSE4.2, it processes unaligned head bytes using `_mm_crc32_u8`, aligned 64-bit words using `_mm_crc32_u64`, and tail bytes using `_mm_crc32_u8`. With ARM CRC instructions, it uses `__crc32cb` for bytes and `__crc32cd` for aligned 64-bit words. Without hardware support, a constructor initializes a reflected Castagnoli table and update delegates to `crc32_update()`.

`spdk_crc32c_iov_update()` folds CRC32C across an iovec array, returning the input CRC unchanged for a null iovec and asserting non-null/nonzero entries otherwise. `spdk_crc32c_nvme()` applies the NVMe-style complement convention: it updates with `~crc` and returns the complement of the result.

Important invariants are caller-provided initial CRC semantics, alignment-aware hardware loops, and compile-time feature selection from `crc_internal.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/crc32c.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/crc64.c -->
# File Research: sources/virtualization/spdk/lib/util/crc64.c

This file implements NVMe CRC64 using either ISA-L or a table-driven Rocksoft reflected algorithm.

With ISA-L enabled, `spdk_crc64_nvme()` delegates to `crc64_rocksoft_refl()`. Otherwise, it uses a 256-entry precomputed `crc64_rocksoft_refl_table`. `crc64_rocksoft_refl_base()` complements the seed, updates one byte at a time with table lookup indexed by low CRC byte XOR input byte, shifts right by eight, and complements the final value.

`spdk_crc64_nvme()` is the exported function and passes the caller buffer, length, and CRC seed to the selected implementation.

The implementation is stateless. Callers control seed chaining, and non-ISA-L performance is byte-at-a-time rather than sliced or vectorized.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/crc64.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/crc_internal.h -->
# File Research: sources/virtualization/spdk/lib/util/crc_internal.h

This private header centralizes CRC acceleration feature selection.

It includes `spdk/config.h`, then chooses one acceleration path: ISA-L headers when `SPDK_CONFIG_ISAL` is set, ARM CRC intrinsics and `SPDK_HAVE_ARM_CRC` on AArch64 with `__ARM_FEATURE_CRC32`, or x86 intrinsics and `SPDK_HAVE_SSE4_2` on x86_64 with `__SSE4_2__`.

CRC implementation files include this header to decide whether to compile ISA-L, ARM hardware, SSE4.2, or table fallback code.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/crc_internal.h -->