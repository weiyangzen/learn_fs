# subset-b-008299 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_extra_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/auparse_extra_test.c

Purpose: focused C regression coverage for auparse behaviors that are narrower than the main text-output harness: buffer replacement, feed state, normalization, timestamp-expression validation, escaped path normalization, single-character empty field parsing, and event-level search matching across multi-record events.

Important APIs and functions: `test_new_buffer` validates `auparse_new_buffer`; `test_feed_state` uses `AUSOURCE_FEED`, `auparse_add_callback`, `auparse_feed_has_data`, `auparse_feed`, and `auparse_flush_feed`; `test_normalize` checks `auparse_normalize`, `auparse_normalize_get_event_kind`, subject/object cursor helpers, and `auparse_interpret_realpath`; `test_compare` checks node and timestamp comparison; `test_timestamp_milli` drives `ausearch_add_expression`; `test_path_norm` calls `audit_encode_value` and `auparse_do_interpretation`; `test_cur_event_matches_multirecord_event` exercises `ausearch_cur_event`.

Control flow and state: `main` runs independent assert-based tests, each creating and destroying its own `auparse_state_t` except for local synthetic `idata`. Feed tests rely on callback count as transient global state. The path fuzz test enumerates base-3 strings over `/`, `a`, and `.` to stress normalization without persistent output.

Dependencies and integration: depends on `libaudit.h`, `auparse.h`, and internal `auparse-idata.h`; uses local `test.log`. It is integrated as an auparse test binary, but broader shell harnesses may choose which binaries to run.

Risks and test signals: risks include assert-only diagnostics, dependence on `root`/audit interpretation tables, and a large path-fuzz print stream. Passing prints `extra auparse tests: all passed`; failures abort at the exact invariant that regressed.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_extra_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/auparse_test.c

Purpose: canonical C integration test for libauparse iteration, searching, feed mode, file and buffer sources, interpretation, record/field cursor movement, and long-event handling.

Important APIs and functions: `walk_test` prints every event, record, field, timestamp, line number, and filename, optionally via `auparse_interpret_field`; `light_test` prints record summaries; `simple_search`, `compound_search`, and `regex_search` exercise `ausearch_add_item`, `ausearch_add_regex`, `ausearch_set_stop`, and `ausearch_next_event`; `auparse_callback` mirrors `walk_test` for feed callbacks. `main` drives `AUSOURCE_BUFFER_ARRAY`, `AUSOURCE_BUFFER`, `AUSOURCE_FILE`, `AUSOURCE_FILE_ARRAY`, and `AUSOURCE_FEED`.

Control flow and state: the static `buf` contains two synthetic audit events; `walked_fields` is reset for `test4.log` and compared with `FIELDS_EXPECTED` to catch parser truncation. Feed tests chunk buffers into three-byte pieces and files into four-byte pieces, then flush to force pending events through callbacks.

Dependencies and integration: uses `libaudit.h`, `auparse.h`, locale setup, and fixture files `test.log`, `test2.log`, and `test4.log`. `run_auparse_tests.sh.in` diffs its stdout against `auparse_test.ref`.

Risks and test signals: output is intentionally brittle and therefore strong at detecting behavior drift, but sensitive to formatting, interpretation table changes, locale, and fixture updates. Failure may be a nonzero exit, a diagnostic in stdout, or a later reference diff mismatch.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.py -->
# sources/security-integrity/audit-userspace/auparse/test/auparse_test.py

Purpose: Python binding parity test for the C auparse harness, verifying that `auparse.AuParser` exposes equivalent source modes, cursor traversal, search, feed callbacks, timestamp objects, descriptor sources, and file-object sources.

Important APIs and functions: `walk_test`, `light_test`, `simple_search`, `compound_search`, and `feed_callback` mirror the C helper structure while using Python methods such as `parse_next_event`, `first_record`, `next_record`, `first_field`, `next_field`, `find_field`, `interpret_field`, `get_timestamp`, `search_add_item`, `search_add_regex`, `search_set_stop`, `search_next_event`, `feed`, and `flush_feed`. `none_to_null` normalizes Python `None` display.

Control flow and state: the script executes thirteen named tests. Early tests use buffer and file sources; middle tests exercise search rules and regex; feed tests chunk buffers and files; later tests open a descriptor and a Python file object to ensure wrapper ownership and duplicate descriptor behavior are correct. Output is deterministic and diffed against `auparse_test.ref.py`.

Dependencies and integration: imports the locally built `auparse` module, uses `srcdir` for fixture lookup, and is launched by `run_auparse_tests.sh.in` with `PYTHONPATH`, `LD_LIBRARY_PATH`, and bytecode suppression.

Risks and test signals: reference output is sensitive to binding method names, exception behavior, path normalization, and C library output. Descriptor/file-pointer tests specifically signal ownership regressions by checking the original fd/file remains readable after parser destruction.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.ref.py -->
# sources/security-integrity/audit-userspace/auparse/test/auparse_test.ref.py

Purpose: expected stdout transcript for `auparse_test.py`. It is a golden file, not executable code, but it defines the externally observed behavior of the Python auparse binding tests.

Important content: the file records every test heading, parsed event/record/field summary, interpreted value, search result, feed callback traversal, long-record walk, descriptor-source status, and file-pointer status. It captures the expected Python rendering of `None` as normalized by the test script, event timestamps, type names, line numbers, filenames, and audit field values.

Control flow and state: no runtime state is stored here. The shell harness regenerates current output from `auparse_test.py`, normalizes source paths with `sed`, and diffs the result against this file. The reference therefore persists a snapshot of parser and binding behavior.

Dependencies and integration: tightly coupled to `auparse_test.py`, fixture logs, the C extension, libaudit interpretation tables, and the shell wrapper. Any intended output change requires a coordinated update to both test logic and reference.

Risks and test signals: high signal for regressions in formatting, cursor order, field interpretation, descriptor lifetime, and source path handling; low diagnostic quality because any diff can be large. The risk is false positives from benign output wording changes or platform-specific interpretation differences.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.ref.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparselol_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/auparselol_test.c

Purpose: command-line feed-mode exerciser for auparse, based on manual-page sample code. It can summarize parsed events or reconstruct raw records for comparison with sed-normalized audit logs.

Important APIs and functions: `print_escape` emits strings while escaping selected characters; `auparse_callback` handles `AUPARSE_CB_EVENT_READY`, iterates records and fields, and either prints summaries/verbose interpretations or reconstructs raw audit records in `--check` mode; `main` parses `--stdin`, `-f/--file`, `--verbose`, `--check`, and `--escape`, sets global escape mode, feeds input chunks, flushes, and destroys the parser.

Control flow and state: global `flags` controls behavior. `event_cnt` is heap allocated and registered as callback user data with `free` cleanup through `auparse_add_callback`. Input is read in 2048-byte chunks and streamed to an `AUSOURCE_FEED` parser.

Dependencies and integration: depends on `libaudit.h`, `auparse.h`, stdio/getopt, and fixture logs. The shell wrappers compare `--check` output against `auditd_raw.sed` normalized raw logs.

Risks and test signals: the check mode intentionally ignores synthetic `type` and `node` fields while reconstructing headers from timestamp/type APIs, making it sensitive to parser record assembly. Potential risks include global escape state, limited diagnostics, and typo-prone raw formatting. A clean sorted diff is the primary pass signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparselol_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/databuf_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/databuf_test.c

Purpose: unit test for the auparse `DataBuf` helper, covering append, advance, reset, replace, compaction, and head-preservation semantics.

Important APIs and functions: `test_basic` validates `databuf_init`, `databuf_append`, `databuf_beg`, `databuf_advance`, and `databuf_free`; `test_preserve` adds `DATABUF_FLAG_PRESERVE_HEAD`, `databuf_reset`, and `databuf_replace`.

Control flow and state: tests allocate a local `DataBuf`, mutate it through append/consume cycles, and inspect public `len` and `offset` fields plus memory contents with `memcmp`. No persistent files or global state are used.

Dependencies and integration: includes `data_buf.h` and `config.h`. The script notes this binary is built but not run by `run_auparse_tests.sh.in`, so coverage depends on automake test registration elsewhere or manual execution.

Risks and test signals: strong at catching off-by-one and compaction regressions in buffered parsing. Weaknesses are assert-only failures and lack of allocation-failure simulation. Passing prints `databuf tests: all passed`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/databuf_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/lookup_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/lookup_test.c

Purpose: generated-table integrity test for auparse integer-to-string interpretation tables.

Important APIs and functions: the `TEST_I2S` macro checks every `_S(value,string)` entry from each table header against the corresponding `*_i2s` function, then probes 1000 random absent values for `NULL`. Test functions cover capability, clock, epoll, address family, fcntl, fsconfig, ICMP, netfilter hooks/actions/protocols, ioctl, socket, personality, prctl, ptrace, resource limit, scheduler, seccomp, signal, and normalization maps.

Control flow and state: `main` seeds `rand()` with a fixed value, runs all table-specific functions, and prints a pass banner. The headers are included twice per table family: one include creates the test array and another exposes the lookup function.

Dependencies and integration: depends on `gen_tables.h`, many auparse generated headers, and selected system headers for constants. `run_auparse_tests.sh.in` invokes it after parser golden-file checks.

Risks and test signals: high coverage for table drift and missing generated entries, but it only verifies `i2s`, not string-to-int or flag-composition helpers. Random negative checks are deterministic but collision-prone if future constants equal the sampled values.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/lookup_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/lru_cache_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/lru_cache_test.c

Purpose: small white-box test for auparse LRU cache internals used by uid/name lookup caching.

Important APIs and functions: `init_lru`, `check_lru_name`, `check_lru_uid`, and `destroy_lru` are exercised directly. `free_name` is supplied as the value cleanup callback.

Control flow and state: the test creates a two-entry queue, inserts two names, manually backfills `uid` values and uid hash slots, then verifies uid lookups hit existing nodes and increment `hits`. It then checks a missing uid allocates/returns a node with no name and increments `misses`.

Dependencies and integration: includes private `lru.h`, so it is coupled to internal `Queue`, `QNode`, and hash layout rather than public auparse APIs.

Risks and test signals: useful for catching cache accounting and lookup behavior, but fragile against internal layout refactors because it writes `q->uid_hash->array` directly. Passing is silent except for process exit zero.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/lru_cache_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/run_auparse_tests.sh.in -->
# sources/security-integrity/audit-userspace/auparse/test/run_auparse_tests.sh.in

Purpose: automake-time shell harness for the auparse C and Python test suite.

Important behavior: copies fixture logs when running out of tree, runs `./auparse_test` and diffs stdout against `auparse_test.ref`, runs `./auparselol_test -f test3.log --check` and compares sorted reconstructed raw output with `auditd_raw.sed`, optionally locates and copies the built SWIG `_audit*.so`, then runs `auparse_test.py` with local Python and library paths and diffs against `auparse_test.ref.py`. It finishes with `./lookup_test`.

Control flow and state: `set -e` stops on the first failing command. Generated intermediates are `auparse_test.cur` and `auparse_test.raw`. Python execution is conditional on configured `use_python3`.

Dependencies and integration: uses configured `@srcdir@`, `@top_builddir@`, and `@use_python3@`. It depends on built auparse binaries, SWIG audit module, Python auparse module, fixture logs, sed scripts, and local shared libraries.

Risks and test signals: strong end-to-end diff gate, but path and shared-library discovery can fail before parser behavior is tested. The comment notes `databuf_test` is built but not run here.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/run_auparse_tests.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/run_auparselol_test.sh.in -->
# sources/security-integrity/audit-userspace/auparse/test/run_auparselol_test.sh.in

Purpose: minimal shell harness dedicated to `auparselol_test` raw reconstruction.

Important behavior: runs `./auparselol_test -f "$srcdir"/test3.log --check`, sorts output into `auparse_test.cur`, transforms the fixture with `auditd_raw.sed` into `auparse_test.raw`, and diffs both files.

Control flow and state: `set -e` makes any command failure fatal. It writes two local temporary comparison files and reads only configured `srcdir`.

Dependencies and integration: depends on the compiled `auparselol_test`, fixture `test3.log`, and sed script. It is useful as a narrower check than the full auparse suite.

Risks and test signals: verifies feed parsing and raw output reconstruction, but because both sides are sorted it ignores original event order. Diff success is the pass signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/run_auparselol_test.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/uid_name_wrap_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/uid_name_wrap_test.c

Purpose: regression test for name-to-uid and uid-to-name cache symmetry in auparse internal user lookup.

Important APIs and functions: calls internal `lookup_uid_from_name`, then uses `check_lru_uid` to inspect the uid cache and `destroy_lru` to release it.

Control flow and state: creates a zeroed stack `auparse_state_t`, resolves `"root"` to uid 0, verifies the cache node for uid 0 contains name `"root"`, and destroys the cache created during lookup. No external files are used, but the system user database must resolve root conventionally.

Dependencies and integration: includes private `internal.h`, `lru` structures through that header, and libc user lookup behavior.

Risks and test signals: catches cache population regressions and uid/name wraparound issues. Risk is platform sensitivity if uid 0 is not named root or NSS is unavailable. Success is exit zero.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/uid_name_wrap_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/tty_named_keys.h -->
# sources/security-integrity/audit-userspace/auparse/tty_named_keys.h

Purpose: macro-expanded lookup data mapping terminal byte sequences to human-readable key names for TTY audit data interpretation.

Important APIs and types: the file defines no functions itself; consumers supply macro `E(sequence, name)` before including it. Entries cover control characters, delete/backspace, tab/newline/return, escape, CSI/SS3 function keys, cursor keys, page/home/end/insert/delete, shifted variants, mouse sequences, and keypad aliases.

Control flow and state: none at runtime in this header. Ordering is semantic data: comments state longest sequences should precede shorter ones so consumers can match escape prefixes without prematurely selecting `esc` or shorter CSI aliases.

Dependencies and integration: based on terminal descriptions from ncurses-era data and consumed by auparse TTY interpretation code. It has no include guards because repeated macro inclusion is intentional.

Risks and test signals: risks include ambiguous terminal sequences, alias choices documented in comments, and the need to keep `E("\x1B", "esc")` after longer escape sequences. Test coverage is indirect through TTY interpretation output and any parser golden files that include TTY data.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/tty_named_keys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/typetab.h -->
# sources/security-integrity/audit-userspace/auparse/typetab.h

Purpose: macro table mapping audit field names to `auparse_type_t` interpretation categories.

Important APIs and types: entries use `_S(AUPARSE_TYPE_*, "field")` for uid/gid, syscall, arch, exit, escaped strings, escaped file paths, keys, permissions, modes, socket addresses, capabilities, success, syscall arguments, signal, session, capability bitmaps, netfilter protocol, ICMP type, protocol/address, AppArmor fields under `WITH_APPARMOR`, seccomp, open/mmap flags, MAC labels, proctitle, hooks, fanotify, trust, and errno.

Control flow and state: no code executes here; the include site defines `_S` to generate lookup records. Conditional AppArmor rows depend on build configuration.

Dependencies and integration: consumed by auparse field-type lookup and interpretation paths, including Python binding `get_field_type` exposure. Any field added here changes how raw audit values are interpreted and searched.

Risks and test signals: incorrect classification can alter user-visible interpretations or break golden tests. Coverage comes from parser references, lookup tests for generated functions, and tests that call `interpret_field`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/typetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/umounttab.h -->
# sources/security-integrity/audit-userspace/auparse/umounttab.h

Purpose: macro table for interpreting `umount` flag bits from Linux `include/linux/fs.h`.

Important APIs and types: `_S` maps `0x1` to `MNT_FORCE`, `0x2` to `MNT_DETACH`, `0x4` to `MNT_EXPIRE`, `0x8` to `UMOUNT_NOFOLLOW`, and `0x80000000` to `UMOUNT_UNUSED`.

Control flow and state: none; consumers define `_S` to build conversion tables.

Dependencies and integration: used by auparse generated flag interpretation logic for unmount-related audit fields. It is source-synchronized with kernel constants rather than computed from system headers.

Risks and test signals: stale constants or missing new flags would produce incomplete interpretation. Signal is indirect through generated lookup/flag tests and audit event interpretation output.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/umounttab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/xattr-atflagtab.h -->
# sources/security-integrity/audit-userspace/auparse/xattr-atflagtab.h

Purpose: macro table for interpreting `*xattrat`/`AT_*` flag bits related to extended attribute operations.

Important APIs and types: `_S` rows map `AT_SYMLINK_NOFOLLOW`, `AT_NO_AUTOMOUNT`, `AT_EMPTY_PATH`, and `AT_RECURSIVE`. A comment notes zero/`LOOKUP_FOLLOW` is handled in code rather than as a table row.

Control flow and state: no executable logic; generated-table consumers provide `_S`.

Dependencies and integration: tied to Linux `include/uapi/linux/fcntl.h` and `fs/xattr.c` semantics and consumed by auparse flag interpretation.

Risks and test signals: missing kernel flag updates can make audit interpretation less useful. The zero-flag special case must remain aligned with code that handles default follow behavior. Tests are generated lookup/interpretation checks and any fixture output that includes xattr flags.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/xattr-atflagtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/Makefile.am -->
# sources/security-integrity/audit-userspace/auplugin/Makefile.am

Purpose: automake definition for building and installing the `libauplugin` library and descending into its test directory.

Important build API: declares `SUBDIRS = test`, `VERSION_INFO = 1:0`, `lib_LTLIBRARIES = libauplugin.la`, installed header `auplugin.h`, sources `auplugin-fgets.c` and `auplugin.c`, and links against `audisp/libqueue.la`, `auparse/libauparse.la`, and pthread.

Control flow and state: automake uses it to compile PIC code with project warning flags and include paths for top-level, lib, common, auparse, auplugin, audisp, and src.

Dependencies and integration: integrates plugin helper APIs with the audit dispatcher queue implementation and auparse feed parser. Header installation exposes the public API to plugin authors.

Risks and test signals: library ABI versioning and link dependencies are the main risk areas. Missing common/lib include paths or queue linkage would fail build. Tests under `auplugin/test` validate exported fgets and stats behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin-fgets.c -->
# sources/security-integrity/audit-userspace/auplugin/auplugin-fgets.c

Purpose: descriptor-based replacement for `fgets`, designed for audit plugin input streams and reusable both as global state and as reentrant state objects.

Important APIs and functions: `auplugin_fgets_init/destroy`, `_clear_r`, `_eof_r`, `_more_r`, `_fgets_r`, and `_setvbuf_r` implement the reentrant API; global wrappers lazily initialize `global_state`. `enum auplugin_mem` controls ownership for internal, malloc, mmap, and read-only mmap-file buffers.

Control flow and state: each state tracks `buffer`, `current`, `eptr`, `orig`, `eof`, memory type, and buffer size. `auplugin_fgets_r` first returns buffered complete lines, reads only when needed, compacts unread data only when out of room, returns partial data at EOF or capacity, and advances permanently for `MEM_MMAP_FILE`.

Dependencies and integration: used by `auplugin.c` inbound handling to frame audit records from a nonblocking fd. Relies on `read`, `munmap`, libaudit size constants through `auplugin.h`.

Risks and test signals: risks are off-by-one NUL handling, EOF semantics, ownership mismatch, and global API non-reentrancy. Dedicated `fgets_test` and `fgets_r_test` cover line, partial, long, custom-buffer, and mmap-file paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin-fgets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin.c -->
# sources/security-integrity/audit-userspace/auplugin/auplugin.c

Purpose: main runtime library for auditd plugins, moving inbound audit dispatcher records through an internal queue to either string callbacks or auparse feed callbacks.

Important APIs and functions: `auplugin_init` configures fd, queue depth/flags, nonblocking mode, and queue storage; `auplugin_stop` sets the atomic stop flag; `auplugin_event_loop` starts a dequeue-to-string worker; `auplugin_event_feed` starts a dequeue-to-auparse worker with optional timer aging; stats functions expose queue depth/max/overflow. `common_inbound` reads framed records with `auplugin_fgets` and enqueues `event_t` objects.

Control flow and state: global single-instance state includes inbound fd, queue config, worker thread, timer callback, stats callback, and atomic stop/dispatcher hup flags. Inbound runs on the caller thread until stop/EOF/error; outbound worker owns queue destruction after draining/stopping.

Dependencies and integration: uses pthreads, signals, syslog, `common.h` atomics, `libdisp.h` event headers, hidden `queue.h`, auparse feed APIs, and `auplugin-fgets`.

Risks and test signals: concurrency and lifecycle are core risks: only one plugin instance is supported, outbound string loop detaches while feed loop joins, and queue destruction is worker-owned. Stats and fgets tests give partial coverage; full event-loop behavior needs integration tests with dispatcher-style input.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin.h -->
# sources/security-integrity/audit-userspace/auplugin/auplugin.h

Purpose: installed public C API for audit plugin helper library.

Important APIs and types: defines `MAX_AUDIT_EVENT_FRAME_SIZE`, opaque `auplugin_fgets_state_t`, `enum auplugin_mem`, queue flag constants, callback typedefs, global and reentrant `auplugin_fgets` APIs, `auplugin_setvbuf`, plugin lifecycle functions, event loop/feed functions, stats registration/reporting, and queue metric accessors. Attribute fallbacks keep headers usable across compilers.

Control flow and state: header only; runtime state is in `auplugin.c` and `auplugin-fgets.c`. API design exposes one global fgets instance and explicit reentrant state instances.

Dependencies and integration: includes `libaudit.h` and `auparse.h`, making plugin users compile against both audit message constants and parser callback types.

Risks and test signals: public ABI risk from enum/function changes, buffer-size contract changes, and ownership semantics for `auplugin_setvbuf_r`. Tests compile against this header and validate exported functions, but broader ABI compatibility is build/package policy.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/Makefile.am -->
# sources/security-integrity/audit-userspace/auplugin/test/Makefile.am

Purpose: automake test definition for `libauplugin`.

Important build API: builds `fgets_test`, `metrics_test`, and `fgets_r_test`, registers all as `TESTS`, includes auplugin/lib/auparse headers, and links each program against `../libauplugin.la`. ASAN flags are conditionally appended.

Control flow and state: no runtime logic; automake compiles and runs the three binaries during `make check`.

Dependencies and integration: depends on the local auplugin library and project warning flags. `fgets_r_test` also uses fixture data from the auparse test tree at runtime through `srcdir`.

Risks and test signals: missing `srcdir` propagation or link dependencies can break tests. ASAN integration increases memory-error signal when configured.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/fgets_r_test.c -->
# sources/security-integrity/audit-userspace/auplugin/test/fgets_r_test.c

Purpose: unit test for the reentrant `auplugin_fgets_state_t` API, including custom buffer ownership and mmap-file mode.

Important APIs and functions: `test_basic_state` covers init/more/eof/read/clear/destroy; `test_deferred_compaction` uses `auplugin_setvbuf_r` with `MEM_MALLOC`; `test_reject_self_managed_override` validates invalid ownership rejection; `test_mmap_file` maps auparse `test.log` and reads it through `MEM_MMAP_FILE`.

Control flow and state: tests use pipes for synthetic streams, a heap custom buffer, and a private mmap of a fixture file. Each test owns and destroys its state object, preventing cross-test global contamination.

Dependencies and integration: includes `auplugin.h`, POSIX pipe/read/write, mmap/stat/open, and fixture path resolution via `srcdir`.

Risks and test signals: catches reentrant EOF semantics, compaction, buffer ownership, and mmap traversal. It assumes `test.log` has 14 lines and starts with `type=AVC`, so fixture drift requires test updates. Passing prints `audit-fgets_r tests: all passed`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/fgets_r_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/fgets_test.c -->
# sources/security-integrity/audit-userspace/auplugin/test/fgets_test.c

Purpose: unit test for the global `auplugin_fgets` API.

Important APIs and functions: `test_simple_line`, `test_multiple_lines`, `test_partial_line`, and `test_long_line` cover `auplugin_fgets_clear`, `auplugin_fgets_more`, `auplugin_fgets_eof`, and `auplugin_fgets`.

Control flow and state: each test creates a pipe, clears global state, writes known input, closes the writer, reads expected chunks, and closes the reader. Long-line testing verifies that output is clamped to `blen - 1`, leftover data remains detectable, and EOF is only set after an additional read.

Dependencies and integration: depends on POSIX pipes and the installed auplugin header. It is run by the auplugin test Makefile.

Risks and test signals: valuable for global-state regressions but cannot validate concurrent use because the global API is intentionally single-state. Passing prints `audit-fgets tests: all passed`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/fgets_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/metrics_test.c -->
# sources/security-integrity/audit-userspace/auplugin/test/metrics_test.c

Purpose: smoke test for auplugin stats callback registration and reporting.

Important APIs and functions: registers `cb` with `auplugin_register_stats_callback`, then calls `auplugin_report_stats`, which should invoke the callback with current queue depth, max depth, and overflow flag.

Control flow and state: no plugin initialization or queue traffic is created here; it checks that reporting safely calls through the registered function and prints the metric tuple.

Dependencies and integration: includes `auplugin.h` and links against `libauplugin`. Queue metric functions are supplied by the dispatcher queue dependency.

Risks and test signals: shallow coverage; it may expose uninitialized queue metric behavior depending on queue implementation defaults. Output `depth=... max=... ovf=...` is the visible signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/metrics_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/Makefile.am

Purpose: top-level automake dispatcher for language bindings.

Important build API: sets cleanup patterns and declares `SUBDIRS = python golang swig`.

Control flow and state: automake descends into each binding implementation during build, install, dist, and check phases according to each subdirectory's conditions.

Dependencies and integration: links the project binding surface into the main build without itself compiling code. It coordinates the handwritten Python auparse binding, Go libaudit wrapper, and SWIG audit binding.

Risks and test signals: build failure in any enabled binding subdirectory can fail the aggregate binding step. There is no direct runtime test signal in this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/golang/Makefile.am

Purpose: automake packaging/install rules for Go libaudit bindings.

Important build API: distributes `audit.go`, marks `test.go` as a dist check script, and under `HAVE_GOLANG` installs `audit.go` under `$(prefix)/lib/golang/src/pkg/redhat.com/audit`. The `check` target stages files but leaves actual `go run` disabled due to Go path limitations.

Control flow and state: install/uninstall are hand-written shell recipes. Check creates and removes a temporary `audit` directory.

Dependencies and integration: depends on top source `bindings/golang/audit.go` and `lib/libaudit.h`; runtime cgo uses `pkg-config: audit`.

Risks and test signals: test coverage is effectively disabled, so build/package regressions can slip through. The old GOPATH-style install path may be incompatible with modern Go module workflows.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/audit.go -->
# sources/security-integrity/audit-userspace/bindings/golang/audit.go

Purpose: small cgo package exposing a limited libaudit logging API to Go.

Important APIs and functions: exports constants for virtualization audit event types and functions `AuditValueNeedsEncoding`, `AuditEncodeNVString`, and `AuditLogUserEvent`. C bindings include `libaudit.h`, `unistd.h`, `stdlib.h`, `string.h`, and use `pkg-config: audit`.

Control flow and state: each function converts Go strings to C strings and frees them. `AuditLogUserEvent` opens an audit fd, logs a user message with boolean result mapped to 1/0, closes the fd, and returns the cgo error; if `audit_open` fails it returns nil.

Dependencies and integration: relies on libaudit C APIs `audit_value_needs_encoding`, `audit_encode_nv_string`, `audit_open`, and `audit_log_user_message`.

Risks and test signals: `AuditLogUserEvent` swallowing `audit_open` failure as nil can hide logging failure. cgo allocation/free correctness is central; `AuditEncodeNVString` assumes libaudit returns malloc-owned memory. Only the disabled Go test covers encoding behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/audit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/test.go -->
# sources/security-integrity/audit-userspace/bindings/golang/test.go

Purpose: minimal executable test for the Go audit binding's encoding predicate.

Important APIs and functions: imports local `./audit`, calls `AuditValueNeedsEncoding("test")` expecting false and `AuditValueNeedsEncoding("test test")` expecting true, prints failure messages or `Success`.

Control flow and state: exits by returning from `main` after printing on failure; no explicit nonzero exit is used.

Dependencies and integration: intended to run after staging `audit.go` into a local package, but the Makefile currently disables actual execution.

Risks and test signals: because failures do not call `os.Exit(1)` and the check is disabled, this is weak as automated coverage. It still documents expected encoding behavior for whitespace-containing values.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/python/Makefile.am

Purpose: automake coordinator for the handwritten Python auparse binding.

Important build API: distributes `auparse_python.c`, sets cleanup patterns, and conditionally descends into `python3` when `USE_PYTHON3` is enabled.

Control flow and state: no direct compilation here; build work is delegated to `bindings/python/python3/Makefile.am`.

Dependencies and integration: connects the source file to the Python 3 extension build. It intentionally has no Python 2 subdir in this tree.

Risks and test signals: risk is configuration mismatch where Python support is expected but `USE_PYTHON3` is false. Direct test signal comes from the python3 subdir and auparse shell harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/auparse_python.c -->
# sources/security-integrity/audit-userspace/bindings/python/auparse_python.c

Purpose: CPython extension module `auparse` wrapping libauparse parser, search, feed, normalization, timestamp, and interpretation APIs.

Important APIs and types: defines `AuEvent` with lazy properties `sec`, `milli`, `serial`, `host`, string formatting, and rich timestamp comparison. Defines `AuParser` owning `auparse_state_t *`, initialized from logs, file, file array, buffer, buffer array, duplicated descriptor, duplicated file object, or feed source. Methods expose feed lifecycle, callbacks, escape and EOE timeout, reset, metrics, search expression/item/timestamp/regex APIs, event and record traversal, field traversal, field lookup, field values/types, interpretation, realpath, socket family/port/address, and normalization cursor helpers.

Control flow and state: object deallocation destroys the parser. Callback registration stores a `CallbackData` with Python function/user data and reconstructs Python calls from the C callback. Descriptor and file-object sources duplicate fd with `F_DUPFD_CLOEXEC` so parser destruction does not close caller-owned descriptors. Module init registers types, `NoParser`, source/search/stop/rule/type/escape constants.

Dependencies and integration: includes Python C API and `auparse.h`; links against libauparse/libaudit. Test coverage comes from `auparse_test.py` and the python3 Makefile no-undefined check.

Risks and test signals: risks include GIL assumptions in callbacks, reference ownership, stale Python-version conditionals, static buffers in event formatting, return-code mapping differences, and missing constants for newer C enum values. Descriptor/file-pointer tests directly validate ownership fixes.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/auparse_python.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/python3/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/python/python3/Makefile.am

Purpose: automake/libtool recipe for building the Python 3 `auparse` extension module.

Important build API: builds `auparse.la` from shared source `bindings/python/auparse_python.c`, with Python 3 CFLAGS/includes/libs, `-module -avoid-version`, relro linker flag, and dependencies on `libauparse.la` and `libaudit.la`.

Control flow and state: `check-local` probes `python3-config --embed --libs`, skips with code 77 if unavailable, then rebuilds with `-Wl,--no-undefined` to catch missing symbols.

Dependencies and integration: uses configured `PYTHON3_*` variables and top build libraries. Installed under Python `pyexec` extension location.

Risks and test signals: linking against the correct embed libs is platform-sensitive. The no-undefined check is a strong build-time signal for CPython/libaudit/libauparse linkage regressions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/python3/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/swig/Makefile.am

Purpose: top-level automake coordinator for SWIG-generated audit bindings.

Important build API: distributes `src/auditswig.i`, always descends into `src`, and conditionally descends into `python3` when `USE_PYTHON3` is enabled.

Control flow and state: no direct build logic besides subdirectory selection and cleanup patterns.

Dependencies and integration: ties the SWIG interface file to language-specific generated bindings. The Python auparse shell test also locates the built SWIG `_audit*.so` module.

Risks and test signals: stale SWIG interface distribution or disabled Python 3 condition can break downstream binding tests. Actual compile/test signals live in `swig/python3`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/python3/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/swig/python3/Makefile.am

Purpose: automake/libtool recipe for generating and building the Python 3 SWIG `_audit` module plus `audit.py`.

Important build API: sets SWIG flags/includes, builds `_audit.la` from generated `audit_wrap.c`, installs `audit.py`, links against `libaudit.la` and Python libs, and regenerates outputs from `../src/auditswig.i`.

Control flow and state: `check-local` performs the same `python3-config --embed --libs` probe/skip and no-undefined rebuild pattern as the handwritten Python binding. `CLEANFILES` removes generated SWIG artifacts.

Dependencies and integration: depends on SWIG, Python headers/libs, libaudit, and `audit_logging.h`. Its built shared object is copied by the auparse shell harness so Python tests can import audit support.

Risks and test signals: generated-file drift, SWIG version differences, and Python embed linker flags are main risks. No-undefined check gives symbol coverage; Python harness import gives runtime packaging coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/python3/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/src/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/swig/src/Makefile.am

Purpose: distribution-only automake file for the SWIG interface source directory.

Important build API: lists `auditswig.i` in `EXTRA_DIST` and cleanup patterns.

Control flow and state: no compiled targets are declared here. The language-specific subdir references this interface file to generate wrappers.

Dependencies and integration: ensures `auditswig.i` is included in release tarballs for downstream SWIG wrapper generation.

Risks and test signals: low runtime risk, but omitting the interface would break distributed builds. Test signal is packaging/build success in `swig/python3`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/Makefile.am -->
# sources/security-integrity/audit-userspace/common/Makefile.am

Purpose: automake file for the internal common utility library.

Important build API: builds noinst `libaucommon.la` from `strsplit.c`, `common.c`, and `message.c`; declares `common.h`; sets PIC/GNU source/debug CFLAGS and include paths for project root and lib.

Control flow and state: no runtime logic; automake compiles utilities for internal linkage.

Dependencies and integration: `common.h` exposes hidden symbols and atomics used by auditd, audisp, auplugin, and related components.

Risks and test signals: because the library is internal and shared by privileged daemons, small utility regressions can have broad blast radius. Build success and downstream tests are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/common.c -->
# sources/security-integrity/audit-userspace/common/common.c

Purpose: shared utility implementations for audit userspace components.

Important APIs and functions: `audit_is_last_record` classifies event-ending audit record types; `write_to_console` writes formatted messages to `/dev/console`; `wall_message` broadcasts to active utmpx user terminals with nonblocking partial-write handling; `time_string_to_seconds` parses numeric durations with units; `get_progname` caches basename from `/proc/self/exe`; `change_runlevel` forks and execs `/sbin/init` with target level and reports failures through `audit_msg`.

Control flow and state: static cached `progname` persists after first lookup. `SINGLE` and `HALT` are global string constants. `change_runlevel` parent waits for child; child unblocks signals and execs init.

Dependencies and integration: uses libaudit constants, syslog, utmpx, procfs, signals, wait, and private `audit_msg`. Event assembly elsewhere depends on `audit_is_last_record`.

Risks and test signals: risks include stale audit type ranges, blocking or failed terminal writes, unsafe assumptions about `/sbin/init`, static buffer truncation, and time-unit overflow. Coverage is mostly indirect through daemon behavior and event parsing tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/common.h -->
# sources/security-integrity/audit-userspace/common/common.h

Purpose: internal common header for audit userspace utilities, visibility, atomic wrappers, constants, and message APIs.

Important APIs and types: defines `AUDIT_ATOMIC_STORE/LOAD`, `FORMAT_BUF_LEN`, fallback `strndupa`, hidden declarations for string splitting, event-ending classification, runlevel helpers, program name lookup, time conversion constants/functions, console/wall messaging, `message_t`, `debug_message_t`, and `_set_aumessage_mode`.

Control flow and state: header-only macros choose C11 atomics when configured, otherwise direct volatile-compatible access. Visibility macros hide internal symbols from public ABI.

Dependencies and integration: includes `config.h`, `dso.h`, `gcc-attributes.h`, and system limits/types. Used across common, auplugin, and daemon code.

Risks and test signals: atomics use relaxed ordering, sufficient only for simple flags if callers do not require stronger synchronization. Macro fallback and hidden visibility must stay compatible with all consumers. Build coverage across components is the main signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/message.c -->
# sources/security-integrity/audit-userspace/common/message.c

Purpose: centralized internal logging helper for audit userspace libraries and daemons.

Important APIs and functions: `_set_aumessage_mode` configures destination and debug enablement; `audit_msg` sends formatted messages to syslog or stderr unless quiet, suppressing debug messages unless enabled.

Control flow and state: two static globals hold current mode and debug policy. `audit_msg` saves and restores `errno` around logging, preserving caller error context.

Dependencies and integration: uses syslog priorities, stdarg formatting, `common.h`, and private declaration in `private.h`. `common.c` runlevel failures call into it.

Risks and test signals: global mode is process-wide and not synchronized, so concurrent reconfiguration is unsafe. Quiet default can hide diagnostics if callers forget configuration. Tests are indirect through components that assert log side effects or preserve errno.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/strsplit.c -->
# sources/security-integrity/audit-userspace/common/strsplit.c

Purpose: lightweight space-delimited tokenizer variants for audit userspace.

Important APIs and functions: `audit_strsplit_r` is reentrant and similar to `strtok_r` but splits only on literal space characters, skips leading spaces, writes NUL terminators into the source string, and updates caller save pointer. `audit_strsplit` stores static state and delegates to the reentrant version.

Control flow and state: the reentrant function is caller-state driven; the non-reentrant wrapper uses a static `char *str`. `#pragma GCC optimize("O3")` requests optimized code for this tokenizer.

Dependencies and integration: declared in `common.h` and compiled into `libaucommon.la`. Used by parsers/config readers that want shell-light splitting rather than full whitespace tokenization.

Risks and test signals: it does not split tabs or other whitespace, mutates input, and the non-reentrant wrapper is not thread-safe. Tests are indirect unless dedicated tokenizer tests exist elsewhere.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/strsplit.c -->
