# subset-b-008297 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-plugin.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-plugin.c

Purpose: Implements the `audispd-zos-remote` plugin process. It reads audit dispatcher records from stdin, feeds them to libauparse, encodes completed audit events as z/OS remote LDAP/BER requests, and submits them to an ITDS server through the z/OS remote LDAP helper layer.

Important APIs, types, and functions: The file owns global process state (`stop`, `hup`, `zos_remote_inst`, `conf`, `submission_thread`, `mypid`) and uses `plugin_conf_t` from the z/OS remote config layer. `main()` initializes signals, config, queueing, capabilities, nonblocking stdin, auparse, and the submit thread. `push_event()` is the auparse callback that converts an `AUPARSE_CB_EVENT_READY` event into a `BerElement`. `submission_thread_main()` dequeues BER requests and calls `zos_remote_init()`, `submit_request_s()`, and `zos_remote_destroy()`. Signal handlers set global flags and call `nudge_queue()` to wake the submission thread.

Control flow: Startup parses an optional config path or defaults to `/etc/audit/zos-remote.conf`, clears config, initializes the queue, optionally drops capabilities with libcap-ng, and makes stdin nonblocking. The outer loop supports SIGHUP reload: load config, grow the queue if needed, create an `AUSOURCE_FEED` auparse state, block signals around `pthread_create()`, register `push_event()`, and then select/read stdin in 5 second intervals. Input is passed to `auparse_feed()`, idle periods call `auparse_feed_age_events()`, and shutdown/reload flushes auparse, waits up to 10 seconds for the submit thread, destroys auparse, and frees config. The callback builds one BER request containing a sequence of items, one item per audit record in the event, and each item contains timestamp plus field/value relocation entries. The submit thread initializes the server session once per config cycle, blocks in `dequeue()`, submits requests synchronously, drops nonfatal failed events, and aborts on fatal errors.

State and persistence: Runtime state is in process globals plus the in-memory z/OS remote queue. `conf.counter` is incremented per BER item and reset only before the first config load. Config is reloaded on SIGHUP; there is no durable local event persistence in this plugin path. BER objects are owned by the queue after successful `enqueue()` and are freed by the submit thread after submission or by queue destruction if still pending.

Dependencies and integration points: Depends on libauparse, liblber, pthreads, libc signal/select APIs, optional libcap-ng, and local z/OS remote modules (`zos-remote-log.h`, `zos-remote-ldap.h`, `zos-remote-config.h`, `zos-remote-queue.h`). It integrates with audit dispatcher through stdin, with auparse through feed callbacks, and with z/OS ITDS through the LDAP submit helper.

Risks and edge cases: `snprintf(logString, ..., "Linux (%s): ...", node, orig_type)` can receive NULL `node` or `orig_type` if auparse lacks those fields; the code frees `node` by casting away const because `auparse_get_node()` returns allocated memory. `enqueue(ber)` returns void, so if the queue drops a full event the BER is not freed by this file. Signal flags are volatile ints rather than atomics. `pthread_cancel()` from the alarm handler is a last-resort abort that may interrupt library code. BER encoding uses fixed-size buffers for relocation text and truncates long field/value pairs. The SIGTERM handler only accepts signals from the parent process, which avoids external stops but can surprise supervisors that are not the dispatcher parent.

Test signals: No direct test file for this plugin is in this subset. Useful indirect coverage would feed audit events through stdin and assert BER submit calls, SIGHUP reload behavior, full queue handling, and fatal submit shutdown. The auparse feed behavior and generic queue patterns are tested elsewhere, but this BER encoding and LDAP submission path needs integration tests or mocks to cover most failure paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-plugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-queue.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-queue.c

Purpose: Provides the z/OS remote plugin's private producer/consumer queue for `BerElement *` requests. It decouples auparse callback encoding on the main thread from synchronous LDAP submission on the submit thread.

Important APIs, types, and functions: Exports `init_queue()`, `enqueue()`, `dequeue()`, `nudge_queue()`, `increase_queue_depth()`, and `destroy_queue()`. Internal state is a circular array `q`, guarded by `queue_lock` and signaled with `queue_nonempty`; indices are `q_next` and `q_last`, and capacity is `q_depth`.

Control flow: `init_queue()` allocates and NULL-initializes the ring and initializes mutex/condition variables. `enqueue()` tries the next slot up to four attempts, yielding between attempts if the slot is occupied; on success it stores the BER pointer, advances `q_next`, signals the condition, and unlocks. `dequeue()` waits while the next consumer slot is NULL, removes the pointer, clears the slot, advances `q_last`, and returns it. `nudge_queue()` signals the condition without adding data, allowing signal handlers to wake the consumer. `increase_queue_depth()` reallocates only when the requested size is larger and fills new slots with NULL. `destroy_queue()` frees all remaining BER objects with `ber_free(..., 1)`, frees the ring, and destroys synchronization primitives.

State and persistence: State is entirely in memory. Queue contents persist only until submitted, dropped, or process exit. The queue owns any BER remaining in a slot at destruction time, but on full-queue drop `enqueue()` logs and returns without freeing the caller's BER.

Dependencies and integration points: Depends on pthreads, liblber's `BerElement` and `ber_free()`, scheduler yield support, and local logging. It is used by `zos-remote-plugin.c` as the handoff between `push_event()` and `submission_thread_main()`.

Risks and edge cases: `nudge_queue()` can wake `dequeue()`, but `dequeue()` loops until a slot is non-NULL and has no direct stop flag, so a wake with no data will not return NULL unless another mechanism changes the queue state. This can make shutdown/reload depend on pending events or cancellation. `increase_queue_depth()` uses `realloc()` on the ring without preserving FIFO order for wrapped live data and without coordinating with a concurrent enqueue/dequeue beyond the mutex around resize; if only one resizer exists this is likely acceptable, but the wrapped-copy behavior is weaker than the newer generic audisp queue. Full queue drops do not free the BER, creating a leak in the current caller contract.

Test signals: No direct unit tests in this subset. The generic `audisp/queue.c` has much stronger test coverage for resizing and overflow, but this queue has different condition-variable semantics and should be separately tested for shutdown nudges, full queue leaks, and resize-after-wrap behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-queue.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-queue.h

Purpose: Declares the private queue interface used by the z/OS remote audisp plugin to pass BER-encoded audit requests between threads.

Important APIs, types, and functions: Includes `<lber.h>` for `BerElement` and declares `init_queue(unsigned int size)`, `enqueue(BerElement *)`, `dequeue(void)`, `nudge_queue(void)`, `increase_queue_depth(unsigned int size)`, and `destroy_queue(void)`.

Control flow: The header does not implement control flow; it exposes a minimal lifecycle contract: initialize, enqueue/dequeue between producer and consumer, optionally wake the consumer, grow capacity, and destroy.

State and persistence: The interface implies module-global queue state hidden in the C file. There is no persistence or explicit queue handle, so only one queue instance can exist in a process.

Dependencies and integration points: Integrated only with the z/OS remote plugin implementation. The direct `BerElement *` type couples the queue to liblber and makes it unsuitable as a generic audisp queue abstraction.

Risks and edge cases: Because `enqueue()` is void, callers cannot observe full-queue drops or know whether ownership transferred. `dequeue()` has no timeout or stop argument; callers rely on `nudge_queue()` and external state, but the implementation waits for non-NULL queue slots. These choices matter for clean shutdown and memory ownership.

Test signals: Header coverage should come from queue C tests or plugin integration tests. The absence of a return code on `enqueue()` is a testability limitation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote.conf -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote.conf

Purpose: Sample/default configuration for the z/OS remote audit dispatcher plugin.

Important settings: Defines `server`, `port`, `user`, `password`, `timeout`, and `q_depth`. These correspond to the plugin config consumed by `plugin_load_config()` in `zos-remote-plugin.c`.

Control flow: The file has no executable flow. At runtime, `zos-remote-plugin.c` reads a config file at startup and after SIGHUP, then passes server/session settings to `zos_remote_init()` and queue depth to `increase_queue_depth()`.

State and persistence: This is persistent on-disk configuration. The sample contains placeholder credentials (`RACF_ID`, `racf_password`) and a default LDAP port (`389`).

Dependencies and integration points: Integrated with the z/OS remote config parser and indirectly with the plugin submit thread, LDAP server connection, and queue allocation.

Risks and edge cases: The config includes a plaintext password field. Deployments need file permissions and secret handling guidance. If `q_depth` is too small, events may be dropped by the plugin's queue; if too large, memory use rises. The sample uses unencrypted LDAP port 389 unless the surrounding z/OS remote LDAP layer applies security elsewhere.

Test signals: Config parser tests should confirm all keys parse, defaults apply when omitted, invalid numeric values fail, and SIGHUP reload grows the queue without losing pending BERs.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/queue.c -->
# sources/security-integrity/audit-userspace/audisp/queue.c

Purpose: Implements audisp's main plugin event queue: a single-producer/single-consumer ring buffer that transfers `event_t *` audit dispatcher messages from auditd's main thread to the dispatcher thread, with overflow actions, optional persistent queue file support, runtime depth growth, and metrics.

Important APIs, types, and functions: Public functions match `queue.h`: `init_queue_extended()`, `init_queue()`, `enqueue()`, `dequeue()`, `dequeue_timed()`, `nudge_queue()`, `increase_queue_depth()`, `write_queue_state()`, `resume_queue()`, `reset_suspended()`, `destroy_queue()`, `queue_current_depth()`, `queue_max_depth()`, and `queue_overflowed_p()`. Internal state includes `q`, `queue_nonempty`, atomic or fallback indices `q_next`/`q_last`, `q_depth`, `overflowed`, `processing_suspended`, `enqueue_in_progress`, `currently_used`, `max_used`, warning counters, and persistence file state.

Control flow: Initialization allocates a NULL-filled ring, initializes a semaphore, resets indices and flags, and optionally opens/restores a persistent queue file. `enqueue()` performs a producer/resizer handshake: it sets `enqueue_in_progress`, checks `processing_suspended`, retries occupied slots up to three times with a 2 ms sleep, stores the event, advances `q_next`, updates current/max depth counters, optionally appends event data to the persistence file and `fdatasync()`s, posts the semaphore, and clears `enqueue_in_progress`. On overflow it frees the event and dispatches `do_overflow_action()`. `dequeue()` waits on the semaphore and calls `dequeue_common()`; the common path checks `disp_hup`, removes `q_last`, clears the slot, advances `q_last`, and decrements depth. `increase_queue_depth()` suspends processing, waits for any in-progress enqueue, allocates a new ring, copies live events from the old consumer position in FIFO order, swaps state, clears overflow, and resumes. Destruction frees queued events, destroys the semaphore, truncates the persistence file when empty, closes it, and resets all state.

State and persistence: Queue state is process-global and single-instance. Metrics track current and maximum observed depth plus overflow and suspension flags. Optional persistence uses an append-only file opened by `Q_IN_FILE` with `Q_CREAT`, `Q_EXCL`, and `Q_SYNC` flags; restore reads lines into events up to queue depth and posts semaphore entries. On clean empty destroy, the file is truncated; if events remain, the file is left intact after close.

Dependencies and integration points: Depends on `libdisp.h` for `event_t`, `audispd-config.h` for `struct disp_conf` and overflow action constants, `common.h` for atomic wrappers and `change_runlevel()`, POSIX semaphores, file APIs, and `disp_hup` from the dispatcher. This is central to auditd/audisp backpressure and plugin dispatch behavior.

Risks and edge cases: The producer/resizer handshake depends on C11 atomics when available; the non-atomic fallback is less rigorous under real concurrency. Persistent restore creates protocol v2 events from raw lines and does not replay full dispatcher headers from disk. Persistence writes only `e->data` of `e->hdr.size`, so corruption, partial writes, or missing newlines can affect restore boundaries. Overflow actions can suspend plugin processing, change runlevel to single user, or halt the system, so config errors are high impact. `dequeue_common()` returns NULL on `disp_hup` after semaphore wake, which callers must handle without treating as queue corruption.

Test signals: `audisp/test/test-queue.c` covers FIFO basics, persistence file creation, wrapped-ring resize FIFO preservation, producer/dispatcher resize handshake, depth draining, and a timed dequeue concurrency path. These tests are strong signals for the 2025 resize and accounting behavior, but multi-producer behavior is intentionally not covered because the documented model is single producer.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/queue.h -->
# sources/security-integrity/audit-userspace/audisp/queue.h

Purpose: Defines the public hidden-symbol interface for audisp's dispatcher queue implementation.

Important APIs, types, and functions: Declares queue mode flags `Q_IN_MEMORY`, `Q_IN_FILE`, `Q_CREAT`, `Q_EXCL`, `Q_SYNC`, and `Q_RESIZE`. Exposes lifecycle, producer/consumer, resize, state dump, resume, and metric functions for `event_t *` queues. It includes `dso.h` and wraps declarations in `AUDIT_HIDDEN_START/END`.

Control flow: The header establishes expected call ordering: initialize, enqueue/dequeue events, optionally nudge or resize, dump state/resume as needed, and destroy. `dequeue_timed()` exposes timed waiting for tests or nonblocking dispatcher patterns.

State and persistence: No state is declared in the header; the implementation uses one global queue. Flags specify whether to use memory only or a file-backed persistent queue and whether file writes should be synchronous.

Dependencies and integration points: Coupled to `event_t` from `libdisp.h` and dispatcher configuration from `audispd-config.h`. It is linked into `libqueue.la` and tested by `audisp-queue-test`.

Risks and edge cases: The queue API transfers ownership of `event_t *` to `enqueue()` even on failure paths that free the event. Callers must not reuse an event after enqueue returns nonzero. Because there is no queue handle, concurrent independent queues cannot be represented.

Test signals: `test-queue.c` is the direct consumer. Build integration is in `audisp/test/Makefile.am`, where `audisp-queue-test` links `libqueue.la` and `libaucommon.la`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/test/Makefile.am -->
# sources/security-integrity/audit-userspace/audisp/test/Makefile.am

Purpose: Automake test definition for audisp unit/integration-style tests.

Important APIs, types, and functions: Sets `AM_CPPFLAGS` to include top-level, audisp, common, src, and lib headers; sets `AM_CFLAGS` with `_GNU_SOURCE`, warning flags, and optional ASAN flags; defines `check_PROGRAMS` and `TESTS` as `audisp-queue-test`, `audisp-llist-test`, and `pconfig-alloc-test`.

Control flow: During `make check`, Automake builds and runs all `check_PROGRAMS`. `audisp_queue_test` compiles `test-queue.c` and links `libqueue.la`, `libaucommon.la`, and pthreads. `audisp_llist_test` compiles `test-audispd-llist.c` and links `libdisp.la` plus common helpers. `pconfig_alloc_test` compiles the allocator-failure parser harness.

State and persistence: No runtime state in this file. It controls build/test graph state through Automake variables and optional ASAN instrumentation.

Dependencies and integration points: Integrates audisp tests with the top-level build. It depends on generated config headers and local libtool libraries from audisp/common.

Risks and edge cases: Tests rely on relative fixture paths such as `../../auparse/test/test3.log` at runtime. If build directories differ, `srcdir` handling must remain correct. ASAN flags apply uniformly to the test programs when `HAVE_ASAN` is set.

Test signals: This file is the authoritative list for the three audisp tests in this subset and provides the build signal that queue, plugin-list, and parser allocation-failure tests are expected to run under `make check`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/test/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/test/pconfig_alloc_test.c -->
# sources/security-integrity/audit-userspace/audisp/test/pconfig_alloc_test.c

Purpose: Tests allocation-failure handling in the audisp plugin configuration parser.

Important APIs, types, and functions: Defines replacement allocators (`test_malloc`, `test_calloc`, `test_realloc`, `test_strdup`) controlled by `reset_allocs()` and `should_fail()`. It stubs `audit_msg` via `test_audit_msg`, then includes `../audispd-pconfig.c` directly with allocator and logging macros remapped. Test functions are `test_path_preserves_old_value()`, `test_args_preserves_old_value()`, and `test_nv_split_realloc_failure()`.

Control flow: Each test initializes parser state, injects a deterministic failure at a specific allocation count, calls a parser helper (`path_parser()`, `args_parser()`, or `nv_split()`), and asserts that old config values or output invariants remain valid. `main()` runs all three tests through plain `assert()`.

State and persistence: Test state is in the global allocation counters. There is no persistence. Parser objects are initialized with `clear_pconfig()` and cleaned with `free_pconfig()` where applicable.

Dependencies and integration points: Direct inclusion of `audispd-pconfig.c` gives access to static parser helpers but tightly couples the test to implementation internals. It uses `plugin_conf_t`, `struct nv_pair`, and parser functions from the included file.

Risks and edge cases: Because failures are triggered by allocation ordinal, implementation changes that add or remove allocations can require test updates even if behavior remains correct. Direct source inclusion can also mask integration issues caused by different compilation units or macros. The test is valuable because it checks that failed updates preserve old live config instead of partially overwriting it.

Test signals: Built as `pconfig-alloc-test` by `audisp/test/Makefile.am`. Passing this test signals that important parser allocation-failure paths are non-destructive and clean their partially built output.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/test/pconfig_alloc_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/test/test-audispd-llist.c -->
# sources/security-integrity/audit-userspace/audisp/test/test-audispd-llist.c

Purpose: Exercises audisp plugin linked-list behavior as used by audispd configuration management, HUP reload reconciliation, startup iteration, and edge-case cleanup.

Important APIs, types, and functions: Uses `conf_llist`, `lnode`, `plugin_conf_t`, `active_t`, and list APIs from `audispd-llist.h`: `plist_create()`, `plist_append()`, `plist_count()`, `plist_count_active()`, `plist_find_name()`, `plist_mark_all_unchecked()`, `plist_find_unchecked()`, `plist_first()`, `plist_next()`, `plist_get_cur()`, `plist_last()`, and `plist_clear()`. Helpers create and free test plugin configs.

Control flow: The file defines a simple macro-based test runner. `test_plugin_configuration_management()` validates append, counts, name lookup, unchecked marking, iteration, and clearing. `test_plugin_hup_signal_handling()` simulates old/new plugin lists during SIGHUP reload: mark old unchecked, match new names, update active state, append new plugins, and identify removed plugins. `test_plugin_iteration_and_startup()` walks mixed active/inactive plugins and simulates assigning PIDs to active entries. `test_memory_management_and_edge_cases()` covers empty operations, NULL plugin append, repeated clear, a 1000-node list, lookup, and active counts. `main()` runs all tests and returns failure if any test did not call `TEST_PASS()`.

State and persistence: All state is process-local test heap data. The linked list stores copies or references according to the implementation under test; the harness frees its original configs after `plist_clear()`, implying `plist_append()` must not leave ownership ambiguity that double-frees caller-owned memory.

Dependencies and integration points: Links against `libdisp.la`, which contains the real audisp linked-list implementation and plugin config helpers. The scenarios are explicitly modeled after audispd's plugin startup and reload logic.

Risks and edge cases: The test expects `plist_append(NULL)` to succeed and create a node with NULL plugin data. It also assumes large list operations remain O(n) but functional. Because it validates behavior through public list APIs, it is less brittle than direct source inclusion tests, though it does not simulate process management or actual plugin child lifecycles.

Test signals: Built as `audisp-llist-test`. Passing signals that plugin list management can support HUP reconciliation, active counting, startup iteration, empty list operations, and repeated cleanup without obvious memory or cursor failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/test/test-audispd-llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/test/test-queue.c -->
# sources/security-integrity/audit-userspace/audisp/test/test-queue.c

Purpose: Unit and stress-style coverage for `audisp/queue.c`, including FIFO order, persistence, wrapped resize, producer/resizer handshakes, and timed dequeue behavior.

Important APIs, types, and functions: Stubs required globals `disp_hup` and `dropped`. Uses `make_event()` to allocate `event_t` objects. Test functions are `basic_test()`, `concurrency_test()`, `persist_test()`, `resize_wrap_test()`, and `resize_handshake_test()`. Producer/consumer thread helpers generate deterministic event strings and verify order.

Control flow: `basic_test()` loads fixture log lines, enqueues them into a 16-slot queue, dequeues them, and compares data. `persist_test()` creates a temp file, initializes `Q_IN_FILE | Q_CREAT | Q_SYNC`, enqueues one event, destroys the queue, and asserts the persisted file size. `resize_wrap_test()` fills a 100-slot ring, drains 80 entries, enqueues 20 more to wrap, grows to 200, and verifies FIFO sequence from 80 through 119. `resize_handshake_test()` runs a producer and dispatcher consumer concurrently; the consumer grows the queue after 128 events and verifies all 2000 ordered logical events arrive. `concurrency_test()` runs one producer and timed dequeue loop until target minus drops is consumed.

State and persistence: Queue state is global inside `queue.c`; each test initializes and destroys it. Persistence uses `/tmp/audisp_qXXXXXX` and unlinks it at the end. The global `dropped` counter is incremented by producer paths that observe enqueue failure.

Dependencies and integration points: Links `libqueue.la` and `libaucommon.la`; uses `../../auparse/test/test3.log` as event data fixture via `srcdir`. Depends on pthreads and queue public APIs.

Risks and edge cases: The `concurrency_test()` has a second producer commented out, reflecting that the queue is documented as single producer. Timed dequeue uses an absolute-looking `timespec` with small values; because `sem_timedwait()` expects an absolute timeout on POSIX, behavior can be platform-sensitive if the call is reached when empty. The tests do not validate all overflow actions such as halt or single-user mode, which would be unsafe in unit tests.

Test signals: This is the direct regression signal for the queue's 2025 race-free resize work, FIFO preservation across wrapped rings, persistence writes, and depth accounting.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/test/test-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/Makefile.am -->
# sources/security-integrity/audit-userspace/auparse/Makefile.am

Purpose: Defines the build graph for `libauparse`, its generated interpretation tables, pkg-config metadata, and auparse tests.

Important APIs, types, and functions: Declares `lib_LTLIBRARIES = libauparse.la`, installs `auparse.h` and `auparse-defs.h`, and sets `pkgconfig_DATA = auparse.pc`. `libauparse_la_SOURCES` includes core parser files (`auparse.c`, `ellist.c`, `nvlist.c`, `interpret.c`, `expression.c`, `auditd-config.c`, `data_buf.c`, normalization files, and headers). `BUILT_SOURCES` and `noinst_PROGRAMS` define many generated lookup-table headers and generator binaries.

Control flow: Automake builds generator programs from `../lib/gen_tables*.c` with `CC_FOR_BUILD`, then runs them with options such as `--i2s`, `--s2i`, `--i2s-transtab`, and `--64bit` to generate headers like `accesstabs.h`, `captabs.h`, `clone-flagtabs.h`, `bpftabs.h`, and normalization maps. `message.c` is copied from `lib/message.c`. The library links against `libaudit.la` and `libaucommon.la` and uses relro linker flags.

State and persistence: Build artifacts include generated headers, copied `message.c`, libtool objects, and installed pkg-config file. `CLEANFILES`, `CONFIG_CLEAN_FILES`, and `DISTCLEANFILES` define cleanup behavior.

Dependencies and integration points: Integrates auparse with the top-level libaudit/common libraries, generated kernel constant translation tables, normalization maps, and the `auparse/test` subdirectory. The small table headers in this subset are data inputs to this file's generator rules.

Risks and edge cases: The generated headers depend on build-host tools and `CC_FOR_BUILD`, so cross-build correctness matters. Many rules use source headers as compile-time macro includes; stale generated headers can misrepresent kernel constants. The file is long and repetitive, making copy/paste naming errors possible between generator target names and output header names.

Test signals: The `SUBDIRS = . test` path includes auparse tests after building the library. Successful `make check` here signals both generated table availability and core library linkability, but functional parser behavior is mostly covered in `auparse/test`, not in this Makefile itself.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/access-flagtab.h -->
# sources/security-integrity/audit-userspace/auparse/access-flagtab.h

Purpose: Source table mapping `faccessat`/access-related AT_* flag bit values to symbolic names for auparse interpretation.

Important APIs, types, and functions: Contains `_S(value, name)` macro rows for `AT_SYMLINK_NOFOLLOW`, `AT_EACCESS`, and `AT_EMPTY_PATH`. It is consumed by `gen_access-flagtabs_h` in `auparse/Makefile.am` to generate `access-flagtabs.h`.

Control flow: No executable flow. Build-time generator includes the file with `_S` defined to emit translation data.

State and persistence: Static build-time data only. Generated output persists in the build tree.

Dependencies and integration points: Values are documented as coming from `fcntl.h`. The generated table feeds auparse field interpretation for access/openat-family flags.

Risks and edge cases: If kernel/libc adds new access flags, interpretations will be incomplete until this table is updated. Duplicate or wrong numeric values would produce misleading audit interpretations.

Test signals: Coverage is indirect through generated table builds and any auparse interpretation tests that inspect access flag names.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/access-flagtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/accesstab.h -->
# sources/security-integrity/audit-userspace/auparse/accesstab.h

Purpose: Build-time table mapping `access(2)` mode bits to symbolic permission tests.

Important APIs, types, and functions: Contains `_S(0x1U, "X_OK")`, `_S(0x2U, "W_OK")`, and `_S(0x4U, "R_OK")`; the comment notes `F_OK` is handled in interpretation code rather than as a table row. Used by `gen_accesstabs_h` to create `accesstabs.h`.

Control flow: No runtime flow. The table is macro-expanded by the generator.

State and persistence: Static input data for a generated header.

Dependencies and integration points: Integrated into auparse's interpretation of access mode fields. Depends on generated table machinery in `../lib/gen_tables.c`.

Risks and edge cases: `F_OK` being special-cased means table users must preserve that separate logic. Missing future permission bits would affect display fidelity.

Test signals: Indirect through table generation and interpretation tests for access permission fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/accesstab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/arphooktab.h -->
# sources/security-integrity/audit-userspace/auparse/arphooktab.h

Purpose: Build-time table mapping ARP netfilter hook numbers to names.

Important APIs, types, and functions: Defines `_S(0, "INPUT")`, `_S(1, "OUTPUT")`, and `_S(2, "FORWARD")`. `auparse/Makefile.am` builds `arphooktabs.h` from it with `gen_arphooktabs_h --i2s arphook`.

Control flow: No runtime flow; generator macro expansion only.

State and persistence: Static source data converted into generated lookup code.

Dependencies and integration points: Values are tied to `include/uapi/linux/netfilter_arp.h` and feed auparse interpretation of ARP hook audit fields.

Risks and edge cases: Kernel changes or namespace-specific interpretations could require table updates. Wrong ordering would produce incorrect human-readable audit output.

Test signals: Indirect build-generation coverage and any interpretation tests for ARP hook fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/arphooktab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auditd-config.c -->
# sources/security-integrity/audit-userspace/auparse/auditd-config.c

Purpose: A reduced auditd configuration parser used by libauparse to discover user-space parsing settings, especially the audit log file path and end-of-event timeout.

Important APIs, types, and functions: Public functions are `aup_load_config()` and `aup_free_config()`. Internal helpers include `aup_clear_config()`, `get_line()`, `nv_split()`, `kw_lookup()`, `log_file_parser()`, and `eoe_timeout_parser()`. The parser recognizes `log_file` and `end_of_event_timeout` keywords through `keywords[]`.

Control flow: `aup_load_config()` initializes a `daemon_conf` with broad auditd defaults, opens `CONFIG_FILE` using `O_NOFOLLOW`, wraps it in a `FILE *`, reads non-too-long lines, tokenizes `name = value`, looks up recognized keywords, and dispatches parser functions. Missing config is nonfatal and leaves defaults. `log_file_parser()` validates directory length, directory existence, basename presence, and read-open access to the log file before replacing `config->log_file`. `eoe_timeout_parser()` requires all digits and converts with `strtoul()`. `aup_free_config()` frees the allocated log file path.

State and persistence: Produces an in-memory `daemon_conf`; no persistent writes. It reads `/etc/audit/auditd.conf` or whatever `CONFIG_FILE` expands to. Defaults include `/var/log/audit/audit.log` and `EOE_TIMEOUT`.

Dependencies and integration points: Used by `auparse.c` in `setup_log_file_array()` and `au_setup_userspace_configitems()`. Depends on common audit tokenization/logging helpers, POSIX file/dir APIs, and `internal.h` definitions for `daemon_conf`.

Risks and edge cases: Only two keywords are recognized; other auditd config settings are ignored after token validation. `O_NOFOLLOW` protects the config file open from symlink traversal but log file validation uses plain `open()`. The parser allows one extra token after value but rejects two, matching audit config option patterns. It logs errors through `audit_msg()` with auparse message mode, so silent/default behavior depends on that state.

Test signals: Indirectly tested when `auparse_init(AUSOURCE_LOGS)` discovers audit logs and when end-of-event timeout behavior is exercised. Dedicated tests should cover missing config, unreadable config, bad `log_file`, nonnumeric timeout, and overlong lines.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auditd-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse-defs.h -->
# sources/security-integrity/audit-userspace/auparse/auparse-defs.h

Purpose: Public ABI definitions for libauparse source modes, search modes, event metadata, callback event kinds, field types, escape modes, destroy modes, and normalization options.

Important APIs, types, and functions: Defines `ausource_t`, legacy `ausearch_op_t`, `austop_t`, `ausearch_rule_t`, `au_event_t`, `auparse_cb_event_t`, `auparse_type_t`, `auparse_esc_t`, `auparse_destroy_what_t`, and `normalize_option_t`. `auparse_type_t` carries an explicit "ONLY APPEND" ABI warning.

Control flow: No runtime control flow. These enums and structs shape behavior in `auparse.c`, `expression.c`, interpretation code, and public callers.

State and persistence: No mutable state. ABI persistence is important: enum order and struct layout are part of the installed library contract.

Dependencies and integration points: Included by `auparse.h` and internal auparse files. C++ linkage guards allow use from C++ callers.

Risks and edge cases: Changing or reordering enum values can break ABI or caller assumptions. `au_event_t.host` is a const pointer with ownership dependent on context; callers must follow the accessor contracts in `auparse.h`.

Test signals: ABI checks, compilation of public consumers, and parser tests that classify field types are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse-idata.h -->
# sources/security-integrity/audit-userspace/auparse/auparse-idata.h

Purpose: Internal interpretation data contract between auparse record parsing and field interpretation lookup code.

Important APIs, types, and functions: Defines `idata`, carrying machine type, syscall, syscall arguments `a0`/`a1`, current working directory, field name, and field value. Declares interpretation helpers `auparse_interp_adjust_type()`, `auparse_do_interpretation()`, `_auparse_load_interpretations()`, `_auparse_free_interpretations()`, `_auparse_lookup_interpretation()`, and `_auparse_flush_caches()`. Defines `NEVER_LOADED`.

Control flow: Header-only declarations; implementation flow lives in `interpret.c`, `auparse.c`, and lookup code. The structure is populated from `rnode` data produced by `ellist.c`.

State and persistence: No state in this header. Interpretation caches and lists are stored in `auparse_state_t`.

Dependencies and integration points: Includes `config.h`, `dso.h`, `auparse.h`, and `auparse-defs.h`. Used by internal but exported-hidden interpretation paths.

Risks and edge cases: `idata` contains borrowed pointers (`cwd`, `name`, `val`), so interpretation code must not outlive the record/cursor data. Machine/syscall values may be unknown or sentinel values from parsing failures.

Test signals: Interpretation tests and search tests using interpreted fields exercise this contract indirectly.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse-idata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse.c -->
# sources/security-integrity/audit-userspace/auparse/auparse.c

Purpose: Core libauparse implementation. It initializes parser state, reads audit records from multiple source types, assembles records into complete audit events, supports feed callbacks, applies search expressions, and exposes event/record/field traversal and interpretation accessors.

Important APIs, types, and functions: Public API implementations include `auparse_init()`, `auparse_destroy()`, `auparse_destroy_ext()`, `auparse_feed()`, `auparse_flush_feed()`, `auparse_new_buffer()`, `auparse_next_event()`, `ausearch_*()` functions, traversal functions (`auparse_first_record()`, `auparse_next_record()`, `auparse_first_field()`, `auparse_next_field()`), data accessors, interpretation helpers, and `auparse_set_eoe_timeout()`. Internal helpers include list-of-lists management (`au_lol_create()`, `au_lol_clear()`, `au_lol_append()`, `au_get_ready_event()`, `au_check_events()`, `au_terminate_all_events()`), input readers (`readline_file()`, `readline_buf()`, `retrieve_next_line()`), timestamp parsing, and event comparison.

Control flow: `auparse_init()` allocates an opaque state, creates the list-of-lists event assembler, initializes source-specific input (`AUSOURCE_LOGS`, file(s), buffers, descriptor, file pointer, or feed), loads user-space config for end-of-event timeout, initializes expression/interpretation/normalizer state, and returns the parser. Input ingestion is driven by `auparse_next_event()` or feed callbacks. `au_auparse_next_event()` first frees processed event lists, returns already complete events if available, otherwise reads lines, extracts audit timestamps, appends records to matching building events by timestamp/milli/serial/host, creates new event lists, ignores standalone EOE records, ages events into complete state based on timeout or last-record type, and returns the lowest ready event. Feed mode appends bytes to `DataBuf`, consumes complete events, and flushes by marking all building events complete. Search APIs build expression trees and scan records, repositioning cursors according to `AUSEARCH_STOP_*`.

State and persistence: `auparse_state_t` owns source file lists, current file pointer, `DataBuf`, current input line, list-of-lists event buffers, current event pointer, expression tree, interpretation list/caches, normalizer state, callback data, and temporary translations. It reads persistent audit logs and auditd config but does not write persistent state. The static `eoe_timeout` is process-global and can be changed by config or `auparse_set_eoe_timeout()`.

Dependencies and integration points: Depends on audit common helpers, `expression.c`, `interpret.c`, `ellist.c`, `data_buf.c`, normalization code, libaudit message/type APIs, and auditd config parsing. It is the public API used by tools and by the z/OS remote plugin's feed callback path.

Risks and edge cases: Event completion depends on timestamp ordering and timeout; delayed records can be split into separate events if they arrive after the timeout. `extract_timestamp()` handles malformed/fuzzer lines by skipping them. `auparse_get_node()` returns a newly allocated string while many other accessors return borrowed pointers, so ownership differences can trip callers. `auparse_feed_has_ready_event()` calls `au_get_ready_event()` in test mode and does not consume, but it still scans internal state. `auparse_reset()` has source-specific fallthrough and does not support feed reset through the default path. The process-global `eoe_timeout` can affect all parser instances.

Test signals: Many behaviors are normally exercised by auparse tests outside this subset. In this subset, the z/OS remote plugin relies heavily on feed/callback APIs, and audisp queue tests use auparse fixture logs. Important direct test areas include multi-record event assembly, EOF/flush behavior, feed partial lines, source arrays, search expression positioning, interpretation ownership, malformed line handling, and timeout changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse.h -->
# sources/security-integrity/audit-userspace/auparse/auparse.h

Purpose: Installed public header for libauparse consumers.

Important APIs, types, and functions: Declares opaque `auparse_state_t`, callback/destroy callback types, lifecycle (`auparse_init()`, `auparse_destroy()`, `auparse_destroy_ext()`), buffer/feed APIs, callback registration, escape mode and metrics, search API, normalization API, event traversal, record traversal, field traversal, raw and interpreted accessors, and socket/realpath interpretation helpers. Uses attribute compatibility macros for allocation/deallocation and access annotations.

Control flow: The header describes library usage flow: initialize with an `ausource_t`, optionally add callbacks or search rules, iterate events/records/fields or feed data, then destroy. Callback users receive `AUPARSE_CB_EVENT_READY`.

State and persistence: Parser state is opaque. Accessor return ownership varies: e.g. `auparse_get_node()` is annotated for free/deallocation, while most strings are borrowed from parser state.

Dependencies and integration points: Includes `auparse-defs.h` and provides C++ linkage guards. This is the API consumed by applications, audisp plugins, and tests.

Risks and edge cases: ABI stability matters for every declaration. Callers must respect cursor semantics; many accessors depend on a current event, current record, and current field. Misunderstanding returned string ownership can cause leaks or invalid frees.

Test signals: Public compilation tests, ABI checks, and behavioral tests using the API are the key signals. The z/OS remote plugin in this subset is a concrete consumer of feed, callback, event timestamp, record, field, and interpretation APIs.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse.pc.in -->
# sources/security-integrity/audit-userspace/auparse/auparse.pc.in

Purpose: pkg-config template for installed libauparse metadata.

Important APIs, types, and functions: Defines `prefix`, `exec_prefix`, `libdir`, and `includedir` substitutions. Exposes package `Name: libauparse`, description, `Version: @VERSION@`, `Libs: -L${libdir} -lauparse`, `Libs.private: -laudit`, and `Cflags: -I${includedir}`.

Control flow: No executable control flow. Configure substitutes variables and `auparse/Makefile.am` installs the generated `auparse.pc`.

State and persistence: Persistent installed metadata used by downstream builds.

Dependencies and integration points: Integrates libauparse with pkg-config consumers and records the private libaudit dependency for static linking.

Risks and edge cases: Incorrect `Libs.private` or include path can break downstream static or cross builds. Version substitution must match the release version.

Test signals: `pkg-config --cflags --libs auparse` in an installed or staged environment verifies the generated file.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/auparse.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/bpftab.h -->
# sources/security-integrity/audit-userspace/auparse/bpftab.h

Purpose: Build-time table mapping Linux `bpf(2)` command numbers to names for auparse interpretation.

Important APIs, types, and functions: Contains `_S(number, "BPF_*")` rows for commands from `BPF_MAP_CREATE` through `BPF_PROG_BIND_MAP`. `auparse/Makefile.am` builds `bpftabs.h` with `gen_bpftabs_h --i2s bpf`.

Control flow: No runtime flow; macro-expanded by a table generator.

State and persistence: Static table source; generated header persists in the build tree.

Dependencies and integration points: Values are tied to `include/uapi/linux/bpf.h` and feed audit field interpretation for BPF command values.

Risks and edge cases: BPF command sets evolve; missing new commands will display as numeric/unknown in interpretations. Wrong values could mislead security investigations.

Test signals: Generated table build plus interpretation tests for `bpf` syscall command fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/bpftab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/captab.h -->
# sources/security-integrity/audit-userspace/auparse/captab.h

Purpose: Build-time table mapping Linux capability numbers to lower-case capability names.

Important APIs, types, and functions: Defines `_S()` rows for capabilities 0 through 40, including newer names such as `perfmon`, `bpf`, and `checkpoint_restore`. `Makefile.am` generates `captabs.h` with `gen_captabs_h --i2s cap`.

Control flow: No runtime control flow in this file.

State and persistence: Static input to generated interpretation tables.

Dependencies and integration points: Values are tied to `include/uapi/linux/capability.h` and used by auparse interpretation of capability fields and bitmaps.

Risks and edge cases: Kernel capability additions require updates. Names are lower-case without `CAP_` prefix, so callers expecting kernel macro names need to account for auparse display format.

Test signals: Capability interpretation tests and generated table build coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/captab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/clocktab.h -->
# sources/security-integrity/audit-userspace/auparse/clocktab.h

Purpose: Build-time table mapping Linux clock IDs to symbolic clock names.

Important APIs, types, and functions: `_S()` rows cover `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, CPU-time clocks, raw/coarse clocks, boottime/alarm clocks, `CLOCK_SGI_CYCLE`, and `CLOCK_TAI`. `Makefile.am` generates `clocktabs.h` with `gen_clock_h --i2s clock`.

Control flow: No runtime flow.

State and persistence: Static table source for generated lookup code.

Dependencies and integration points: Based on `include/uapi/linux/time.h`; used by auparse interpretation of clock-related syscall fields.

Risks and edge cases: New clock IDs need table updates. Platform-specific IDs may not be represented.

Test signals: Generated table build and field interpretation tests for clock IDs.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/clocktab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/clone-flagtab.h -->
# sources/security-integrity/audit-userspace/auparse/clone-flagtab.h

Purpose: Build-time 64-bit table mapping Linux `clone`/`clone3` flag bits to symbolic names.

Important APIs, types, and functions: Contains `_S(ULL, "CLONE_*")` rows for process/thread namespace and behavior flags, including `CLONE_CLEAR_SIGHAND` and `CLONE_INTO_CGROUP`. `Makefile.am` uses `gen_tables64.c` and `--64bit --i2s-transtab clone_flag` to generate `clone-flagtabs.h`.

Control flow: No runtime flow.

State and persistence: Static source for generated 64-bit translation data.

Dependencies and integration points: Values are tied to `include/uapi/linux/sched.h` and used by auparse interpretation of clone flags.

Risks and edge cases: Clone flag values include high bits, so 64-bit generation is necessary; using 32-bit table machinery would truncate newer flags. Kernel changes require updates.

Test signals: Generated table build and interpretation tests for clone flag bitmasks.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/clone-flagtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/data_buf.c -->
# sources/security-integrity/audit-userspace/auparse/data_buf.c

Purpose: Implements the `DataBuf` helper used by auparse to store and consume buffer/feed input with efficient append, advance, optional head preservation, and reset behavior.

Important APIs, types, and functions: Implements `databuf_print()`, `databuf_init()`, `databuf_free()`, `databuf_append()`, `databuf_replace()`, `databuf_advance()`, and `databuf_reset()`. Internal helpers include `databuf_end()`, `databuf_tail_size()`, `databuf_tail_available()`, and `databuf_shift_data_to_beginning()`.

Control flow: `databuf_init()` zeroes state and optionally allocates an initial buffer. `databuf_append()` ignores NULL/zero input, shifts data to the start when allowed and tail space is insufficient, grows allocation by doubling or required size, copies new bytes to the end, updates length and `max_len`, and returns status. `databuf_replace()` clears length then appends. `databuf_advance()` moves the logical beginning forward by up to available length and returns `ESPIPE` if asked to advance too far. `databuf_reset()` only works with `DATABUF_FLAG_PRESERVE_HEAD`, restoring offset to zero and length to the maximum length previously seen.

State and persistence: `DataBuf` owns heap memory via `alloc_ptr`, tracks allocated size, logical offset/length, maximum length, and flags. No persistence beyond the owning parser state.

Dependencies and integration points: Used by `auparse.c` for `AUSOURCE_BUFFER`, `AUSOURCE_BUFFER_ARRAY`, and `AUSOURCE_FEED`. It depends only on libc and `data_buf.h`.

Risks and edge cases: `databuf_append()` uses `memmove(databuf_end(db), src, src_size)`, which handles overlap but relies on correct logical bounds. `databuf_reset()` reconstructs preserved buffers by `max_len`, so callers using preserve-head must ensure `max_len` reflects the intended original input. Integer overflow is partially handled by required-size comparisons but not with explicit `SIZE_MAX` guards for all additions. `databuf_print()` writes to stdout and is diagnostic-only.

Test signals: There is an optional `#ifdef TEST` harness in the file, but normal coverage is indirect through auparse buffer/feed tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/data_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/data_buf.h -->
# sources/security-integrity/audit-userspace/auparse/data_buf.h

Purpose: Declares the `DataBuf` structure and helper API for auparse input buffering.

Important APIs, types, and functions: Defines `DATABUF_FLAG_PRESERVE_HEAD`, `DataBuf` fields (`flags`, `alloc_size`, `alloc_ptr`, `offset`, `len`, `max_len`), inline `databuf_beg()`, and hidden functions for print/init/free/append/replace/advance/reset.

Control flow: Header-only inline `databuf_beg()` returns NULL for unallocated buffers or the logical beginning pointer. Other flow is implemented in `data_buf.c`.

State and persistence: The struct is mutable state embedded in `auparse_state_t`; ownership of `alloc_ptr` belongs to the `DataBuf`.

Dependencies and integration points: Includes `config.h` and `private.h` for build and visibility macros. Used by auparse core input source handling.

Risks and edge cases: External code that manipulates fields directly can violate invariants (`offset + len <= alloc_size`). The preserve-head flag changes append/advance/reset semantics and must match source type.

Test signals: Indirect through auparse buffer and feed parsing; direct tests would validate append/grow/advance/reset invariants.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/data_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ellist.c -->
# sources/security-integrity/audit-userspace/auparse/ellist.c

Purpose: Implements the event record linked list used by auparse to store all records belonging to one audit event and parse each raw record into name/value fields.

Important APIs, types, and functions: Public hidden functions include `aup_list_create()`, `aup_list_clear()`, `aup_list_next()`, `aup_list_append()`, `aup_list_set_event()`, `aup_list_goto_rec()`, and `aup_list_first_field()`. Internal helpers include `aup_list_last()`, `_audit_c2x()`, `escape()`, and `parse_up_record()`.

Control flow: `aup_list_append()` allocates an `rnode`, links it at the tail, initializes record metadata and `nvlist`, then calls `parse_up_record()`. Parsing separates raw record text from an optional interpretation suffix, duplicates the record into `nv.record`, tokenizes fields, handles `msg=audit` and `msg='...'` forms, trims punctuation, expands audit keys into virtual repeated `key` fields, parses SELinux AVC unlabeled fields, and records type, machine, syscall, syscall args, and CWD for later interpretation. `aup_list_set_event()` transfers host pointer ownership from an `au_event_t` into the list. `aup_list_clear()` frees all records, nvlists, raw record strings, event host, and stored CWD.

State and persistence: `event_list_t` stores head/current record pointers, count, event timestamp/serial/host, and event-level CWD. Each `rnode` owns raw record text and parsed nvlist state. No persistence.

Dependencies and integration points: Depends on `libaudit.h`, `interpret.h`, `common.h`, `nvlist`, `rnode`, and audit tokenization helpers. `auparse.c` uses this module for event assembly and cursor traversal; `expression.c` evaluates search expressions over `rnode` and its nvlist.

Risks and edge cases: Record parsing is intentionally tolerant of malformed/fuzzer data but can skip records with no fields. Key expansion allocates duplicate names/values and must match `nvlist_clear()` ownership rules. Special AVC parsing uses a fixed 256-byte temporary context and fails if permission text is too long. `parse_up_record()` mutates `r->record` by splitting at the interpretation separator. CWD ownership moves from records to the event list and must not double-free.

Test signals: Direct auparse parser tests should validate field extraction, key splitting, AVC parsing, CWD/realpath behavior, and malformed records. This subset's z/OS plugin uses field traversal and interpreted values, making this module part of that integration path.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ellist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ellist.h -->
# sources/security-integrity/audit-userspace/auparse/ellist.h

Purpose: Declares the auparse event record linked-list type and hidden list operations.

Important APIs, types, and functions: Defines `event_list_t` with `rnode *head`, `rnode *cur`, `cnt`, `au_event_t e`, and event-level `cwd`. Provides inline `aup_list_get_cnt()`, `aup_list_first()`, and `aup_list_get_cur()`. Declares create/clear/next/append/set-event/goto-record/first-field functions.

Control flow: Header controls cursor access patterns through inlines; implementation flow is in `ellist.c`.

State and persistence: `event_list_t` is mutable in-memory parser state for one event. It owns event host and CWD pointers after setup/append.

Dependencies and integration points: Includes `auparse-defs.h`, `nvlist.h`, and private visibility macros. Used by `auparse.c`, `expression.c`, and interpretation code.

Risks and edge cases: Cursor state is embedded in the list, so nested iteration or concurrent use of the same parser state can disturb callers. Ownership is not obvious from the struct alone; callers must use `aup_list_clear()`.

Test signals: Parser traversal tests covering `auparse_first_record()`, `auparse_next_record()`, and field iteration indirectly validate this interface.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ellist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/epoll_ctl.h -->
# sources/security-integrity/audit-userspace/auparse/epoll_ctl.h

Purpose: Build-time table mapping `epoll_ctl(2)` operation values to names.

Important APIs, types, and functions: Defines `_S(1, "EPOLL_CTL_ADD")`, `_S(2, "EPOLL_CTL_DEL")`, and `_S(3, "EPOLL_CTL_MOD")`. `Makefile.am` generates `epoll_ctls.h` with `gen_epoll_ctls_h --i2s epoll_ctl`.

Control flow: No runtime flow.

State and persistence: Static table source and generated lookup output.

Dependencies and integration points: Values are tied to `include/uapi/linux/eventpoll.h`; auparse interpretation uses generated output for epoll control fields.

Risks and edge cases: Small stable table, but incorrect values would mislabel epoll audit events.

Test signals: Generated table build and interpretation tests for epoll operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/epoll_ctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/expression.c -->
# sources/security-integrity/audit-userspace/auparse/expression.c

Purpose: Implements auparse search expression parsing, expression tree construction, freeing, and evaluation against audit event records.

Important APIs, types, and functions: Public functions include `expr_parse()`, `expr_free()`, `expr_create_comparison()`, `expr_create_timestamp_comparison_ex()`, `expr_create_timestamp_comparison()`, `expr_create_field_exists()`, `expr_create_regexp_expression()`, `expr_create_binary()`, and `expr_eval()`. Internal parser helpers include `lex()`, `parse_comparison()`, `parse_primary()`, `parse_and()`, and `parse_or()`. Evaluation helpers include `eval_raw_value()`, `eval_unsigned_value()`, `eval_interpreted_value()`, `compare_unsigned_values()`, and `compare_values()`.

Control flow: `expr_parse()` initializes a parser state, lexes the first token, parses the recursive grammar (`||` over `&&` over primary expressions), rejects trailing tokens, and returns an expression tree or an allocated error string. `lex()` recognizes operators, field escapes, quoted strings, slash-delimited regexes, raw/interpreted comparison tokens (`r=`, `r!=`, `i=`, `i!=`), value comparisons, parentheses, boolean not, and unquoted strings. `parse_comparison()` handles normal fields, escaped virtual fields (`timestamp`, `timestamp_ex`, `record_type`), and `\regexp`. Numeric comparisons are limited to UID/GID fields and virtual fields. `expr_eval()` recursively evaluates boolean nodes, raw/interpreted string comparisons, numeric/value comparisons, field existence, and regex matches against the current `rnode`.

State and persistence: Expression trees own allocated field names, string values, regex objects, and subexpressions. No persistence. Parser error strings are allocated for callers to free. Evaluation may move the record nvlist cursor while searching field names.

Dependencies and integration points: Depends on `expression.h`, `interpret.h`, libaudit message type lookup, POSIX regex, auparse state/event data, `rnode`, and `nvlist`. `auparse.c` uses these trees for `ausearch_*()` APIs.

Risks and edge cases: Deeply nested expressions can recurse through parser/evaluator stack. `parser_realloc()` frees the old pointer on failure, which is intentional for parser-owned buffers but differs from normal `realloc()` expectations. `parse_timestamp_value()` manually advances the lexer source and must stay synchronized with accepted timestamp formats; the `strspn()` character set omits colon after serial parsing, which can leave unexpected trailing tokens for extended timestamp strings if not fully consumed. Invalid terms evaluate false rather than surfacing runtime errors, so search mistakes can silently miss records. Regex compilation errors are reported at parse time.

Test signals: Search expression tests should cover raw vs interpreted comparisons, field existence, boolean precedence, parentheses, escaped virtual fields, timestamp with milliseconds and serial, regex syntax errors, UID/GID numeric comparisons, and malformed expressions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/expression.c -->
