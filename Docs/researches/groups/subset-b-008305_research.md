# subset-b-008305 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/event.h -->
# sources/security-integrity/audit-userspace/src/libev/event.h

**Purpose**
This is the libev-provided libevent compatibility header used by audit-userspace code that expects classic libevent names. It exposes only core event, timer, signal, and base-loop APIs and maps many names directly onto libev concepts.

**Important APIs, Types, And Functions**
The central type is `struct event`, which embeds a union of `ev_io` and `ev_signal` plus an `ev_timer`. Compatibility fields track `ev_base`, callback, fd, priority, result, flags, and requested event mask. It defines libevent-style helpers such as `event_set`, `event_add`, `event_del`, `event_pending`, `event_once`, `event_loop`, `event_dispatch`, `event_base_new`, `event_base_loop`, and `event_base_once`. Macros alias `EVLOOP_NONBLOCK`, `EVLOOP_ONESHOT`, `EV_TIMEOUT`, `EV_PERSIST`, `EVENT_FD`, and timer/signal helper families.

**Control Flow**
The header declares the API surface; implementation lives in the accompanying libev compatibility source. Callers initialize a base or use the default loop, configure an event object, add it with an optional timeout, and let libev dispatch callbacks.

**State And Persistence**
All state is in memory inside `struct event` and the selected `event_base`; there is no durable persistence. `EVLIST_INIT`, `EVLIST_INSERTED`, `EVLIST_TIMEOUT`, and related flags model lifecycle state.

**Dependencies And Integration Points**
It includes `ev.h` or the configured `EV_H`, plus `time.h`/`sys/time.h` for `timeval`. Audit daemon tests and runtime pieces can use libevent spelling while linking libev.

**Risks**
Only core events are supported; edge-triggered `EV_ET` is a no-op and `event_base_priority_init` has a suspicious `fd` parameter name, reflecting compatibility rather than full libevent parity. Code relying on less-common libevent features may compile but behave differently if only macros exist.

**Test Signals**
Coverage is indirect through auditd event tests linked against `src/libev/libev.la`, especially `format_event_test` in this work item.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/Makefile.am -->
# sources/security-integrity/audit-userspace/src/test/Makefile.am

**Purpose**
This Automake fragment defines the audit-userspace source-level unit and regression tests for list helpers, audit event formatting, and allocation failure handling in auditd configuration parsing.

**Important APIs, Types, And Functions**
It sets shared include paths to the top source tree, `lib`, and `src`, enables `_GNU_SOURCE`, and conditionally adds ASAN flags. `check_PROGRAMS` and `TESTS` contain `ilist_test`, `slist_test`, `format_event_test`, and `auditd_config_alloc_test`. The list tests link prebuilt object files `ausearch-int.o` and `ausearch-string.o`; `format_event_test` compiles several auditd source files directly and links `libaudit`, `libauparse`, `libdisp`, libev, common helpers, pthread, math, GSS, and tcp-wrappers when configured. `auditd_config_alloc_test` is a standalone include-based harness.

**Control Flow**
During `make check`, Automake builds all four programs and executes each as a test. Conditional `ENABLE_LISTENER` adds `auditd-listen.c` to the format-event test source set.

**State And Persistence**
No runtime persistence is introduced by the makefile. It does control build-time state such as object dependencies and ASAN instrumentation.

**Dependencies And Integration Points**
The file integrates test binaries with the larger audit-userspace build graph and shares flags with configured sanitizer support.

**Risks**
The `format_event_test` target depends on many daemon internals, so changes in auditd source dependencies can break linking. The allocation test includes a C implementation file directly, which is intentional but couples the test to static/internal symbols.

**Test Signals**
The file itself is the test registration point; successful `make check` means all four harnesses were compiled and run under the configured feature set.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/auditd_config_alloc_test.c -->
# sources/security-integrity/audit-userspace/src/test/auditd_config_alloc_test.c

**Purpose**
This C test injects allocation failures into selected auditd configuration parser paths and verifies that existing configuration values are preserved when replacement allocation fails.

**Important APIs, Types, And Functions**
The test defines stubs for `audit_msg`, `audit_strsplit`, and `time_string_to_seconds`, then macro-replaces `malloc`, `strdup`, and `asprintf` before including `../auditd-config.c`. `reset_allocs`, `should_fail`, `test_malloc`, `test_strdup`, and `test_asprintf` implement deterministic fail-at-N allocation behavior. Test cases call `name_parser`, `log_file_parser`, and `set_config_dir`.

**Control Flow**
`main` disables failures, then runs three checks. `test_name_preserves_old_value` seeds `daemon_conf.node_name`, fails the first allocation, expects parser failure, and asserts the old name remains. `test_log_file_preserves_old_value` sets `log_test = TEST_SEARCH`, fails the second allocation path, and verifies the original log file path. `test_set_config_dir_preserves_old_value` establishes old global paths, forces a failure on replacing the directory, and checks both globals remain unchanged.

**State And Persistence**
The harness mutates in-memory `daemon_conf` fields plus the global `config_dir` and `config_file` from the included implementation. It cleans those globals at the end to avoid leak reports.

**Dependencies And Integration Points**
It depends directly on auditd-config internals and GNU `vasprintf`. The Makefile compiles it with auditd include paths and no external daemon process.

**Risks**
Macro-replacing allocators only covers allocations in the included translation unit after the defines; helper functions outside that inclusion are not exercised. The test relies on exact allocation ordering, so benign refactors can require fail counter updates.

**Test Signals**
Assertions validate regression behavior for allocation failure atomicity: failed parser updates must not partially replace previous config strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/auditd_config_alloc_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/format_event_test.c -->
# sources/security-integrity/audit-userspace/src/test/format_event_test.c

**Purpose**
This regression test checks that auditd event formatting emits enriched output that is longer than raw output and includes the audit interpretation separator plus an AUID interpretation.

**Important APIs, Types, And Functions**
The test initializes a `daemon_conf`, calls `init_event`, creates `auditd_event` objects with `create_event`, formats them with `format_event`, and releases them with `cleanup_event`. It defines the daemon-global `stop`, a dummy `update_report_timer`, and link stubs for `send_audit_event` and `distribute_event`.

**Control Flow**
The same trusted application audit message is formatted twice. First, `conf.log_format = LF_RAW` records the raw formatted message length. Second, `LF_ENRICHED` formats a fresh event and records the enriched length. The test then checks that enriched output is longer, that byte offset 95 is `AUDIT_INTERP_SEPARATOR`, and that text after that point contains `AUID`.

**State And Persistence**
The test uses only heap-allocated event state and daemon formatting globals initialized by `init_event`; it writes diagnostic output to stdout/stderr but no durable files.

**Dependencies And Integration Points**
It compiles daemon event, reconfigure, config, sendmail, dispatch, optional listen, libaudit, auparse, audisp, libev, and common code together. This makes it a high-integration test rather than a narrow unit test.

**Risks**
The separator check hard-codes offset 95 and the source comment warns the test message must stay in sync with that offset. Changes to audit formatting that are semantically correct can break this brittle index.

**Test Signals**
Failure indicates enriched formatting regressed, audit interpretation placement changed unexpectedly, or required auditd event initialization/link dependencies are broken.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/format_event_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/ilist_test.c -->
# sources/security-integrity/audit-userspace/src/test/ilist_test.c

**Purpose**
This standalone test validates the integer list helper used by ausearch-style code, especially unique insertion order and hit-count sorting.

**Important APIs, Types, And Functions**
The file exercises `ilist_create`, `ilist_add_if_uniq`, `ilist_first`, `ilist_get_cur`, `ilist_next`, `ilist_sort_by_hits`, and `ilist_clear` over `ilist` and `int_node`.

**Control Flow**
The first phase inserts numbers in mixed order and iterates from the first node, expecting `node->num` to increase from 0 through 9. The second phase clears the list, inserts duplicate values with different frequencies, sorts by `hits`, and expects hit counts to descend from 4.

**State And Persistence**
All state is in the in-memory linked list. `ilist_clear` is used between phases and before exit.

**Dependencies And Integration Points**
It includes `ausearch-int.h` and links `${top_builddir}/src/ausearch-int.o` from the Makefile. It is registered as an Automake check program.

**Risks**
The sort test validates hit counts but not the exact associated integer values after sorting, so a bug that preserves count sequence while mixing identities might pass. It also exits immediately on failure and may leak the list on early return.

**Test Signals**
A passing run indicates sorted unique insertion and hit-count sorting retain the expected basic invariants for integer search lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/ilist_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/slist_test.c -->
# sources/security-integrity/audit-userspace/src/test/slist_test.c

**Purpose**
This test validates the string list helper used by audit search code, covering unique insertion, append, clear, and sorting by duplicate hit counts.

**Important APIs, Types, And Functions**
It exercises `slist_create`, `slist_add_if_uniq`, `slist_first`, `slist_get_cur`, `slist_next`, `slist_append`, `slist_clear`, and `slist_sort_by_hits` over `slist`, `snode`, and the global list `s`. `print_list` iterates the list and returns the visible node count.

**Control Flow**
The test inserts three unique strings, checks count and iteration count, appends an explicit fourth node, attempts to add a duplicate `test2`, clears the list, then inserts a deliberate hit-count distribution. After sorting, it expects hit counts to descend from 4 to 1.

**State And Persistence**
State is entirely in process memory. The test allocates `n.str` with `strdup` before appending and relies on `slist_clear` to free list-owned string data.

**Dependencies And Integration Points**
It includes `ausearch-string.h` and links `ausearch-string.o` as configured in `src/test/Makefile.am`.

**Risks**
Like the integer-list test, it checks counts more strongly than string ordering after sort. Manual construction of an `snode` tests ownership transfer but could mask API assumptions if append semantics change.

**Test Signals**
Success means the list count, duplicate-hit increment, clear behavior, and descending hit-count sort all satisfy expected behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/slist_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/Makefile.am

**Purpose**
This top-level Automake file declares the audit-userspace command-line tool subdirectories that are part of the tools build.

**Important APIs, Types, And Functions**
It sets `CONFIG_CLEAN_FILES` for generated or rejected build artifacts and declares `SUBDIRS = aulast aulastlog ausyscall`.

**Control Flow**
Automake recurses into the three subdirectories during build, install, clean, and test phases according to the parent target.

**State And Persistence**
The file has no runtime state. It affects build output and cleanup behavior only.

**Dependencies And Integration Points**
It is integrated into the project’s recursive Automake build. The child directories define the actual programs, man pages, and tests.

**Risks**
Adding a new tool without listing it here means it will not be built through the standard recursive path. Conversely, broken child makefiles stop parent tool builds.

**Test Signals**
There is no direct test logic, but successful recursive `make`/`make check` through this directory confirms the declared tool subtrees are buildable.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/aulast/Makefile.am

**Purpose**
This Automake file builds and installs the `aulast` command, which reports login/logout sessions from audit logs.

**Important APIs, Types, And Functions**
It declares `SUBDIRS = test`, installs `bin_PROGRAMS = aulast`, ships `aulast.8`, and treats `aulast-llist.h` as a non-installed header. `aulast_SOURCES` are `aulast.c` and `aulast-llist.c`. The binary links against `${top_builddir}/auparse/libauparse.la`.

**Control Flow**
The recursive build enters the `test` subdirectory, compiles the two source files with `_GNU_SOURCE` and project include paths, links against auparse, and includes the man page in distribution.

**State And Persistence**
No runtime state is defined here. Build state includes object files, generated artifacts, and clean-file patterns.

**Dependencies And Integration Points**
The tool integrates with the auparse library and the audit-userspace install layout. The test subdirectory provides linked-list tests for the internal list implementation.

**Risks**
The `aulast` binary depends on internal list code rather than a shared utility library. Changes to auparse APIs or include paths can break the tool build.

**Test Signals**
The adjacent test makefile builds `aulast_llist_test`, giving coverage for the list library that `aulast.c` relies on.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.c -->
# sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.c

**Purpose**
This file implements the minimal linked list used by `aulast` to track currently open and completed login sessions while scanning audit events.

**Important APIs, Types, And Functions**
It implements `list_create`, `list_next`, internal `list_append`, `list_clear`, `list_create_session_simple`, `list_create_session`, `list_update_start`, `list_update_logout`, `list_delete_cur`, `list_find_auid`, and `list_find_session`. Nodes are `lnode` records defined in the header.

**Control Flow**
Creation initializes an empty head/current pair. Session creation allocates or accepts an `lnode`, initializes login metadata and proof serials, and appends it at the tail by walking from `cur` when necessary. Find functions scan linearly and set `l->cur` to the matching node. Update functions mutate the current node, duplicating host/terminal strings on login and setting end time/status on logout. Deletion walks from the head, removes the current node, frees owned strings and the node, then positions `cur` at the next node for head deletion or previous node otherwise.

**State And Persistence**
State is process-local heap memory. The list owns duplicated `name`, `term`, and `host` strings for normal allocated nodes. There is no durable persistence; `aulast` output is derived while scanning logs.

**Dependencies And Integration Points**
It depends on C allocation/string functions and the `aulast-llist.h` types. `aulast.c` uses it as its session cache.

**Risks**
`list_update_start` and `list_update_logout` check `l` but not `l->cur`, so callers must first position a current node. `list_create_session_simple` assumes the passed node is heap-owned and clearable, which is safe for `aulast.c` allocated nodes but dangerous for stack nodes.

**Test Signals**
`aulast_llist_test.c` exercises creation, update, deletion, repeated find/remove, and session ID reuse behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.h -->
# sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.h

**Purpose**
This header declares the session list data model and operations used by the `aulast` audit-log session reporter.

**Important APIs, Types, And Functions**
`status_t` enumerates `LOG_IN`, `SESSION_START`, `LOG_OUT`, `DOWN`, `CRASH`, and `GONE`. `lnode` stores audit session id, start/end times, auid, pid, optional user/terminal/host strings, result, current status, audit proof serials, and next pointer. `llist` stores head and current pointers. The API includes creation, iteration, clearing, session creation/update/logout, current deletion, and lookup by `(auid,pid,session)` or session id.

**Control Flow**
`aulast.c` uses the header to keep a current-node cursor while scanning audit records. Inline helpers set or return the current pointer, while implementation functions maintain ownership and status transitions.

**State And Persistence**
The declared state is in-memory only. Proof serial fields preserve audit event references long enough for optional `--proof` output.

**Dependencies And Integration Points**
The header depends on `sys/types.h` for `uid_t` and `time_t` use via included platform headers. It is included by the tool and the list unit test.

**Risks**
The list exposes mutable structures directly, so callers can violate invariants such as ownership of string fields or valid status transitions. The `list_create_session_simple` API is especially sensitive because it appends an already allocated node.

**Test Signals**
The dedicated `aulast_llist_test` validates a subset of cursor, update, and delete behavior against this API.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast-llist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast.c -->
# sources/security-integrity/audit-userspace/tools/aulast/aulast.c

**Purpose**
`aulast` is a `last`-style command that reconstructs login sessions from Linux audit records instead of traditional wtmp data. It reports successful sessions by default and failed login attempts with `--bad`.

**Important APIs, Types, And Functions**
Key functions are `report_session`, `extract_record`, `create_new_session`, `update_session_login`, `update_session_logout`, `process_bootup`, `process_kernel`, `process_shutdown`, and `main`. It uses auparse APIs such as `auparse_init`, `auparse_next_event`, `auparse_get_type`, `auparse_find_field`, `auparse_get_field_int`, `auparse_interpret_field`, `auparse_get_time`, and `auparse_get_serial`.

**Control Flow**
`main` parses `--bad`, `--debug`, `--stdin`, `--proof`, `--extract`, `-f`, `--user`, and `--tty`; initializes auparse from a file, stdin, or system logs; then iterates events. `AUDIT_LOGIN` creates a preliminary session from auid/pid/session, closing a previous same-session entry as `GONE`. `AUDIT_USER_LOGIN` fills terminal/host/result details or immediately reports failed logins when requested. `AUDIT_USER_END` closes and reports matching sessions. Boot records mark open reboot/session entries as `CRASH` or `DOWN`, clear the list, and start a reboot record; shutdown closes the reboot record. At EOF, remaining sessions are reported.

**State And Persistence**
State is the process-local global `llist l`, optional extraction file `aulast.log`, cached kernel string, and command options. Output is stdout plus optional extracted raw records; no database is written.

**Dependencies And Integration Points**
It integrates with libaudit record constants, auparse log readers, the local linked list, libc locale/time functions, and root-readable audit logs.

**Risks**
Argument parsing increments indexes without consistently checking for missing option values for `-f`, `--user`, and `--tty`. Session correlation depends on audit fields being present and on one-record events. The linear list can be inefficient on large logs, and string duplication failures are not always checked.

**Test Signals**
The list library has direct tests, but this full parser/reporting flow is not directly covered in this subset beyond build/link coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/test/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/aulast/test/Makefile.am

**Purpose**
This Automake file builds and runs the `aulast` linked-list unit test.

**Important APIs, Types, And Functions**
It declares `noinst_PROGRAMS = aulast_llist_test` and `TESTS = aulast_llist_test`. The test sources are the test file plus `${top_srcdir}/tools/aulast/aulast-llist.c`, and include paths point at the `aulast` source directory. If ASAN is enabled, it applies sanitizer flags; otherwise it links statically.

**Control Flow**
During `make check` in the `aulast/test` directory, Automake compiles the list implementation into the test binary and executes it.

**State And Persistence**
No runtime state is defined by the makefile. Build outputs are non-installed.

**Dependencies And Integration Points**
The test intentionally links the production list implementation directly, giving focused coverage without building the entire `aulast` binary.

**Risks**
Static linking in the non-ASAN path can expose platform/toolchain differences. The test only covers the linked-list layer and not auparse-driven session parsing.

**Test Signals**
Successful execution of `aulast_llist_test` indicates key session-list operations remain stable.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/test/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/test/aulast_llist_test.c -->
# sources/security-integrity/audit-userspace/tools/aulast/test/aulast_llist_test.c

**Purpose**
This unit test suite validates advanced behavior of the `aulast` session linked list, focusing on update correctness, deletion, find behavior, and session ID reuse.

**Important APIs, Types, And Functions**
The file uses `TEST_START`, `TEST_PASS`, and `TEST_FAIL` macros for simple reporting. `count_sessions` iterates without permanently changing `l->cur`. Test functions call `list_create`, `list_create_session`, `list_find_auid`, `list_update_start`, `list_update_logout`, `list_delete_cur`, `list_first`, `list_get_cur`, and `list_clear`.

**Control Flow**
`test_update_operations_verification` creates sessions, checks initial state, updates login fields, logs out, and verifies proof serials and NULL host/terminal handling. `test_repeated_add_remove_with_find` creates five sessions, deletes middle entries, reuses session IDs for different users, and removes all sessions while checking counts and absence. `test_complex_session_management` models multiple users, logout/delete, ID reuse, and batch logout checks. `main` runs all three and returns failure if any test did not pass.

**State And Persistence**
State is heap list data and local counters. Each test clears its list on success.

**Dependencies And Integration Points**
It includes the production `aulast-llist.h` and links the production `aulast-llist.c` via the test Makefile.

**Risks**
The tests intentionally continue after function calls without checking allocation failure paths. If a `TEST_FAIL` occurs before `list_clear`, temporary allocations can leak during that failed run.

**Test Signals**
The tests provide strong signals for cursor preservation, deletion semantics, update field mutation, and correct distinction between reused session IDs and old records.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/test/aulast_llist_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/aulastlog/Makefile.am

**Purpose**
This Automake file builds and installs `aulastlog`, a lastlog-like audit-log reporter.

**Important APIs, Types, And Functions**
It sets clean artifacts, distributes `aulastlog.8`, includes project and auparse headers, builds `bin_PROGRAMS = aulastlog`, declares `aulastlog-llist.h` as a non-installed header, and compiles `aulastlog.c` with `aulastlog-llist.c`. The binary links `${top_builddir}/auparse/libauparse.la`.

**Control Flow**
The standard Automake build compiles the list and CLI source files, links auparse, and installs the binary and man page.

**State And Persistence**
No runtime state is represented here. The file controls build artifacts and distribution content.

**Dependencies And Integration Points**
`aulastlog` is integrated with auparse and the audit-userspace tool install path.

**Risks**
There is no listed local test subdirectory for `aulastlog`, so the list implementation and CLI behavior rely on broader build/test coverage or manual testing.

**Test Signals**
A successful build confirms source/link compatibility with auparse; this file does not register runtime tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.c -->
# sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.c

**Purpose**
This file implements a small linked list of users and their latest successful login metadata for `aulastlog`.

**Important APIs, Types, And Functions**
It implements `list_create`, `list_next`, `list_append`, `list_clear`, `list_update_login`, `list_update_host`, `list_update_term`, and `list_find_uid`. `list_append` copies an input `lnode` into newly allocated storage, duplicates strings, assigns item order from `cnt`, and increments the count.

**Control Flow**
The CLI prepopulates the list from passwd entries. As audit login events are found, `list_find_uid` positions `cur`, then update functions mutate timestamp, host, and terminal for that user. Iteration for output uses `list_first`, `list_get_cur`, and `list_next`.

**State And Persistence**
State is process-local heap memory. The list owns duplicated `name`, `host`, and `term` strings and frees them in `list_clear`. There is no persistent state.

**Dependencies And Integration Points**
The implementation depends on libc allocation/string APIs and `aulastlog-llist.h`. `aulastlog.c` uses it as a fixed list of local users plus last-login data.

**Risks**
Allocation failures in `strdup` are not checked, so later reporting may see NULL fields unexpectedly. `list_update_host` and `list_update_term` set fields to NULL without freeing old values when passed NULL, which would leak if those paths are used after a value exists. The update helpers assume `l->cur` is valid.

**Test Signals**
No dedicated test in this subset covers this list; behavior is indirectly build-covered by `aulastlog` compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.h -->
# sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.h

**Purpose**
This header declares the user last-login list used by `aulastlog`.

**Important APIs, Types, And Functions**
`lnode` stores last login seconds, uid, username, host, terminal, an item index, and next pointer. `llist` stores head/current pointers and a count. The API provides list creation, iteration, count access, append, clear, login/host/terminal updates, and lookup by uid.

**Control Flow**
`aulastlog.c` appends one node per passwd entry, scans audit records, uses uid lookup to position the current node, and updates the found node with newer login data.

**State And Persistence**
The represented state is in-memory summary data for one command invocation. It models a report table rather than a durable lastlog database.

**Dependencies And Integration Points**
It depends on `sys/types.h` for uid-related types and is included by the CLI and list implementation.

**Risks**
The structures are public and mutable, so callers can bypass count and ownership invariants. The API does not encode whether string pointers are borrowed or owned at input time; the implementation duplicates on append and update.

**Test Signals**
There is no direct unit test registered for this header in the listed files; build coverage comes from `aulastlog`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog-llist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog.c -->
# sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog.c

**Purpose**
`aulastlog` reports each local user’s most recent successful login based on audit logs rather than traditional lastlog storage.

**Important APIs, Types, And Functions**
The main function uses libc password APIs `getpwent`/`endpwent`, auparse search APIs `ausearch_add_item`, `ausearch_set_stop`, `ausearch_next_event`, `auparse_get_timestamp`, `auparse_find_field`, and `auparse_get_field_int`, plus the local linked-list API.

**Control Flow**
Arguments accept `--stdin` and `--user`/`-u`. The program first builds a list of all passwd users or a single named user, failing if the requested user is unknown. It initializes auparse from stdin or system logs, adds search filters for `type = USER_LOGIN` and `res = success`, and scans matching events. For each event with an `auid`, it finds the user node and updates login time, hostname, and terminal. Finally it prints a fixed-width table with `**Never logged in**` for users with no matched event.

**State And Persistence**
State is the in-memory user list. It reads local passwd and audit logs but writes only stdout diagnostics/reporting.

**Dependencies And Integration Points**
It depends on auparse, audit log access, local account data, locale/time formatting, and the `aulastlog` list implementation.

**Risks**
The loop calls `ausearch_next_event` again at the end of each body, which advances an extra event and may skip matches depending on auparse semantics. The code only preserves the last matching record encountered, assuming log traversal order corresponds to increasing time. It has no root warning for log access failure.

**Test Signals**
No direct runtime test is registered in this subset; build and manual audit-log tests are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/ausyscall/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/ausyscall/Makefile.am

**Purpose**
This Automake file builds and installs the `ausyscall` syscall name/number lookup utility.

**Important APIs, Types, And Functions**
It configures project and lib include paths, `_GNU_SOURCE`, `bin_PROGRAMS = ausyscall`, distributes `ausyscall.8`, and compiles `ausyscall.c`. The binary links against `${top_builddir}/lib/libaudit.la`.

**Control Flow**
Automake compiles the single C file and links it with libaudit during the tools build.

**State And Persistence**
The makefile defines build state only. The resulting tool is a pure lookup/reporting command.

**Dependencies And Integration Points**
It integrates with the libaudit syscall translation tables and the audit-userspace installation layout.

**Risks**
Feature-dependent architecture support is controlled by configure macros in the C file; the makefile itself does not express those variants.

**Test Signals**
There is no explicit test target here. Successful compile/link verifies libaudit API compatibility.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/ausyscall/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/ausyscall/ausyscall.c -->
# sources/security-integrity/audit-userspace/tools/ausyscall/ausyscall.c

**Purpose**
`ausyscall` maps syscall names to numbers and numbers to names for a selected or detected audit machine architecture, with optional table dumping and exact lookup.

**Important APIs, Types, And Functions**
`usage` exits with command help. `main` parses command-line tokens and calls libaudit APIs `audit_determine_machine`, `audit_detect_machine`, `audit_machine_to_name`, `audit_syscall_to_name`, and `audit_name_to_syscall`. `LAST_SYSCALL` bounds substring lookup to 1400, while `--dump` scans 0..8191.

**Control Flow**
Arguments can include an architecture, syscall number, syscall name, `--dump`, and `--exact`. Numeric tokens become `syscall_num`; architecture names are resolved by libaudit; unsupported/deprecated architecture strings produce explicit messages. If only `uring` is supplied and parsed as `MACH_IO_URING`, it is treated as a syscall name. The tool detects machine type if none was supplied, dumps the table when requested, otherwise performs exact or substring name lookup or number lookup.

**State And Persistence**
The program is stateless and writes results to stdout or errors to stderr.

**Dependencies And Integration Points**
It depends on libaudit’s compiled syscall tables and configured architecture macros such as `WITH_ARM`, `WITH_AARCH64`, and `WITH_RISCV`.

**Risks**
Substring lookup only searches to `LAST_SYSCALL`, so architectures with higher syscall numbers may be incomplete outside dump mode. `strtol` results are not range-validated and non-digit suffixes are not rejected after the leading digit.

**Test Signals**
No direct test is registered here; behavior is usually validated by manual command use and libaudit table tests elsewhere.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/ausyscall/ausyscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.cargo/config.toml -->
# sources/security-integrity/cryfs/.cargo/config.toml

**Purpose**
This Cargo configuration improves developer debug-build performance for CPU-heavy cryptographic dependencies.

**Important APIs, Types, And Functions**
It sets `[profile.dev.package.<name>] opt-level = 3` for `scrypt`, `aead`, `aes-gcm`, `chacha20poly1305`, and `openssl`.

**Control Flow**
Cargo applies these package-specific optimization levels when compiling in the dev profile. Project crates remain at the normal dev profile settings while selected dependencies are optimized.

**State And Persistence**
The file affects local and CI build artifacts in Cargo target directories. It stores no runtime state.

**Dependencies And Integration Points**
It integrates with the root Cargo workspace and the crypto dependency set declared in `Cargo.toml`.

**Risks**
Optimized dependencies can make debug stepping into those crates harder and may hide performance issues in project code. Keeping this list in sync with active crypto dependencies is manual.

**Test Signals**
CI and local `cargo test`/`cargo build` exercise this config implicitly when Cargo reads the workspace.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.cargo/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.claude/settings.json -->
# sources/security-integrity/cryfs/.claude/settings.json

**Purpose**
This file configures Claude Code behavior for the CryFS repository.

**Important APIs, Types, And Functions**
It enables `alwaysThinkingEnabled` and allows only `Bash(cargo test *)`, `Bash(cargo build *)`, and `Bash(cargo check *)`.

**Control Flow**
Claude Code reads this JSON and restricts tool execution according to the allowed command patterns.

**State And Persistence**
It is persistent repository configuration for AI tooling, not application state.

**Dependencies And Integration Points**
It integrates with Claude Code rather than Cargo or CryFS runtime code.

**Risks**
The repo-level allowlist is narrower than the devcontainer user-level Claude setup, so behavior can differ inside and outside the container. It also allows broad cargo command suffixes but not formatting or lint commands.

**Test Signals**
There are no code tests. Valid JSON parsing and expected Claude Code behavior are the practical signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.claude/settings.json -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/devcontainer.json -->
# sources/security-integrity/cryfs/.devcontainer/devcontainer.json

**Purpose**
This file defines a Rust-based VS Code devcontainer for CryFS development.

**Important APIs, Types, And Functions**
It uses `mcr.microsoft.com/devcontainers/rust:1`, adds Rust and GitHub CLI features, installs apt packages `fuse3`, `libfuse3-dev`, and `fish`, runs `.devcontainer/setup.sh` after creation, and `.devcontainer/setup_claude.sh` after each start. VS Code customization sets fish as the default terminal, requests a Hack Nerd Font, and installs DependI, JJK, and Claude Code extensions.

**Control Flow**
Container creation installs features and packages, then setup scripts configure jj and fish. Each start refreshes Claude permissions.

**State And Persistence**
The container stores installed tools, shell configuration, fonts, jj metadata, and user-level Claude settings inside the devcontainer environment.

**Dependencies And Integration Points**
It integrates Docker/devcontainers, VS Code, FUSE/macFUSE-adjacent development dependencies, fish, jj, and Claude Code.

**Risks**
Setup scripts download from the network without pinned hashes. `setup_claude.sh` deliberately grants broad tool permissions in the container. FUSE behavior may still require host capabilities not provided by all container runtimes.

**Test Signals**
Opening the repository in a devcontainer and running Cargo/FUSE tests is the validation path.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup.sh -->
# sources/security-integrity/cryfs/.devcontainer/setup.sh

**Purpose**
This post-create script orchestrates one-time devcontainer setup.

**Important APIs, Types, And Functions**
It resolves `SCRIPT_DIR` from `BASH_SOURCE[0]` and executes `setup_jj.sh` and `setup_fish.sh`.

**Control Flow**
With `set -e`, the script stops on the first failing setup step. Claude setup is intentionally excluded and runs on container start instead.

**State And Persistence**
It persists whatever the child scripts install: jj tooling/config, fish shell setup, fonts, and aliases.

**Dependencies And Integration Points**
It integrates with `devcontainer.json` as `postCreateCommand`.

**Risks**
A failure in either child script aborts the whole post-create flow. Since the child scripts use network downloads, container creation depends on external availability.

**Test Signals**
A successful devcontainer creation is the main signal; no unit tests exist.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_claude.sh -->
# sources/security-integrity/cryfs/.devcontainer/setup_claude.sh

**Purpose**
This post-start script configures Claude Code inside the devcontainer to auto-accept broad tool execution.

**Important APIs, Types, And Functions**
It writes a JSON `PERMISSIONS` object allowing `Bash(*)`, `Edit(*)`, `Write(*)`, `Read(*)`, `WebFetch(*)`, and `NotebookEdit(*)` to `~/.claude/settings.json`, then removes `~/.claude.json`.

**Control Flow**
`set -e` aborts on errors. The script creates the user settings directory, overwrites settings every container start, and clears cached denials.

**State And Persistence**
It mutates user-level Claude configuration in the container home directory, not repository source.

**Dependencies And Integration Points**
It is invoked by devcontainer `postStartCommand` and affects Claude Code behavior in the development environment.

**Risks**
The permission set is intentionally broad and should be limited to trusted container contexts. It overwrites any previous user-level Claude settings in the container.

**Test Signals**
Validation is manual: Claude Code should no longer prompt for the allowed tool categories after container start.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_claude.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_fish.sh -->
# sources/security-integrity/cryfs/.devcontainer/setup_fish.sh

**Purpose**
This script installs and configures the fish shell experience for the CryFS devcontainer.

**Important APIs, Types, And Functions**
It downloads the Oh My Fish installer with `curl`, runs it with fish, installs `bobthefish`, downloads Hack Nerd Font v3.0.1 with `wget`, extracts it into `~/.local/share/fonts`, and enables nerd font theming.

**Control Flow**
`set -e` and `set -v` make failures fatal and verbose. The script performs network downloads, installation, font extraction, cleanup, and fish universal variable configuration.

**State And Persistence**
It mutates the container user’s fish configuration and local font directory.

**Dependencies And Integration Points**
It depends on fish, curl, wget, tar, GitHub availability, and the devcontainer VS Code terminal font setting.

**Risks**
Network downloads are unpinned by checksum and the script is not idempotent for all Oh My Fish states. Verbose output may expose command details in logs.

**Test Signals**
Opening a fish terminal with the expected theme and font glyphs is the practical validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_fish.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_jj.sh -->
# sources/security-integrity/cryfs/.devcontainer/setup_jj.sh

**Purpose**
This script installs and configures Jujutsu (`jj`) in the CryFS devcontainer.

**Important APIs, Types, And Functions**
It installs `cargo-binstall` when missing, runs `cargo binstall --no-confirm jj-cli`, writes fish completions and aliases, initializes jj in colocated mode under `/workspaces/cryfs`, tracks `main@origin`, and copies git user name/email into jj config.

**Control Flow**
The script is verbose and fail-fast. It installs tools, writes shell integration files, initializes the repository, then conditionally propagates identity settings.

**State And Persistence**
It mutates user cargo binaries, fish config, repository jj metadata, bookmark tracking, and user jj config.

**Dependencies And Integration Points**
It depends on cargo, cargo-binstall installer network access, jj, fish, git, and the devcontainer path `/workspaces/cryfs`.

**Risks**
The hard-coded workspace path can fail if the container mounts elsewhere. Re-running `jj git init --colocate` may fail or be noisy on already initialized workspaces. Network installers are not checksum-pinned.

**Test Signals**
`jj st` and fish completions/aliases working inside the devcontainer validate the setup.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_jj.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.github/FUNDING.yml -->
# sources/security-integrity/cryfs/.github/FUNDING.yml

**Purpose**
This GitHub metadata file declares sponsorship links for the CryFS project.

**Important APIs, Types, And Functions**
It sets `github: smessmer cryfs`, advertising GitHub Sponsors accounts.

**Control Flow**
GitHub reads this YAML and renders funding links in repository UI.

**State And Persistence**
It is repository metadata only and has no build or runtime state.

**Dependencies And Integration Points**
It integrates with GitHub’s funding UI.

**Risks**
Incorrect account names would produce broken or misleading funding links.

**Test Signals**
The repository’s GitHub Sponsor button rendering is the validation signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.github/FUNDING.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.github/workflows/ci.yml -->
# sources/security-integrity/cryfs/.github/workflows/ci.yml

**Purpose**
This workflow defines CryFS continuous integration across operating systems, toolchains, feature modes, formatting, documentation, and coverage.

**Important APIs, Types, And Functions**
The `test` job runs `cargo test` over macOS 14/15/15-intel/26 and Ubuntu 22.04/24.04, debug/release, default/no-default features, and stable/nightly/MSRV 1.95. `crates_individually_testable` runs `cargo check` per crate over targets and feature modes. Additional jobs run rustfmt check, `cargo doc` with warnings denied, and `cargo llvm-cov` upload to Codecov. Concurrency cancels superseded runs.

**Control Flow**
Each job checks out the repository, installs OS dependencies such as FUSE packages or macFUSE, installs a Rust toolchain via a pinned `dtolnay/rust-toolchain` action, then runs cargo commands. macOS test commands skip FUSE mount tests and flaky example.com reqwest smoke tests.

**State And Persistence**
CI state includes build caches/artifacts and Codecov upload output; no project runtime state is persisted.

**Dependencies And Integration Points**
The workflow depends on GitHub Actions runners, apt/brew, macFUSE, rustup toolchains, `cargo-llvm-cov`, Codecov, and all workspace crates.

**Risks**
The matrix is large and expensive. Comments note disabled clippy/readme sync jobs and missing release coverage in per-crate checks. Network and FUSE behavior on hosted macOS are explicitly fragile.

**Test Signals**
This is the primary quality gate: workspace tests, per-crate compilability, formatting, dead doc links, and coverage all feed CI status.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/Cargo.toml -->
# sources/security-integrity/cryfs/Cargo.toml

**Purpose**
This root manifest defines the CryFS Rust workspace, shared package metadata, and centralized dependency versions.

**Important APIs, Types, And Functions**
It declares `members = ["crates/*"]`, resolver 3, workspace package metadata such as edition 2024, rust-version 1.95, LGPL license, repository/homepage, and version `2.0.0-alpha3`. `[workspace.dependencies]` centralizes crypto, async, CLI, FUSE, testing, serialization, logging, compression, and utility crates.

**Control Flow**
Cargo uses this manifest to resolve all workspace crates and dependency versions. Member crates can inherit package metadata and dependency versions from the workspace.

**State And Persistence**
The file controls build dependency resolution and package metadata. It does not define runtime state.

**Dependencies And Integration Points**
Every `crates/*` member integrates through this workspace. CI uses the workspace root for broad `cargo test`, `cargo doc`, and coverage runs.

**Risks**
Centralized versions reduce drift but make upgrades affect many crates at once. Several TODOs indicate metadata and dependency feature trimming are not complete. The MSRV is high and enforced in CI.

**Test Signals**
The CI matrix validates that the workspace resolves and builds/tests under stable, nightly, and Rust 1.95.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/archive.sh -->
# sources/security-integrity/cryfs/archive.sh

**Purpose**
This small release-helper script creates a compressed source archive from the current git HEAD.

**Important APIs, Types, And Functions**
It runs `git archive --format=tar.gz --prefix=cryfs/ HEAD -o cryfs.tar.gz`.

**Control Flow**
The script is fail-fast via `set -e` and directly invokes git archive with a fixed output name.

**State And Persistence**
It writes `cryfs.tar.gz` in the current working directory. It does not modify repository history.

**Dependencies And Integration Points**
It depends on git and the repository being in a valid state. It likely supports manual release packaging.

**Risks**
The output name is fixed and can overwrite an existing archive without prompting. Uncommitted changes are not included because the archive source is `HEAD`.

**Test Signals**
Successful script execution and inspection/extraction of `cryfs.tar.gz` validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/archive.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/Cargo.toml -->
# sources/security-integrity/cryfs/crates/blobstore/Cargo.toml

**Purpose**
This manifest defines the CryFS `blobstore` crate, which exposes blob storage abstractions and block-backed implementations.

**Important APIs, Types, And Functions**
The crate inherits workspace package metadata. It has a `testutils` feature that enables `cryfs-blockstore/testutils`, and depends on async/error/data libraries including `anyhow`, `async-trait`, `byte-unit`, `futures`, `binary-layout`, `cryfs-blockstore`, `cryfs-utils`, `cryfs-version`, and `log`. Dev dependencies include `mockall`, `rstest`, `tokio`, and blockstore test utilities.

**Control Flow**
Cargo builds the crate as part of the workspace and enables feature-dependent test helpers when requested.

**State And Persistence**
The manifest defines dependency/build state only. Runtime persistence is implemented by the crate’s blockstore-backed code.

**Dependencies And Integration Points**
It is tightly coupled to `cryfs-blockstore` for block IDs, block lifecycle, and remove results; to `cryfs-utils` for `AsyncDropGuard` and `Data`; and to workspace CI for feature checks.

**Risks**
The public `testutils` feature exposes tracking/test helper internals and must stay compatible with blockstore test features. Async trait bounds and workspace version coupling can cause broad compile failures when dependency APIs change.

**Test Signals**
Workspace CI runs this crate under default, no-default, and all-features modes, plus tests and target checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/blob_id.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/blob_id.rs

**Purpose**
This file defines `BlobId`, the blobstore-level identifier wrapper around a blockstore `BlockId`. In the block-backed implementation, a blob ID is the root data-tree block ID.

**Important APIs, Types, And Functions**
`BlobId` derives copy, ordering, hashing, and binary read/write traits. Constructors and conversions include `new_random`, `zero`, `to_root_block_id`, `from_root_block_id`, `from_slice`, `from_array`, `data`, `from_hex`, and `to_hex`. Display delegates to the root block ID; Debug formats as `BlobId(<hex>)`.

**Control Flow**
All conversion methods delegate validation and byte/hex parsing to `BlockId`. The block-backed store constructs blob IDs from root nodes and uses the `root` field internally.

**State And Persistence**
The only state is the embedded 16-byte block ID. Through `BinRead`/`BinWrite`, it can be serialized in binary formats alongside block IDs.

**Dependencies And Integration Points**
It depends on `cryfs_blockstore::{BlockId, BLOCKID_LEN}` and `binrw`. Public blobstore traits and implementations use `BlobId` for create/load/remove operations.

**Risks**
`root` remains `pub(super)` with a TODO to hide it behind `to_root_block_id`, so sibling modules can still couple to internal representation. Any future blob ID format change must preserve or migrate root-block semantics.

**Test Signals**
Unit tests cover Display and Debug formatting from a fixed hex ID; broader conversion and serialization behavior is not directly covered in this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/blob_id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/mod.rs

**Purpose**
This module collects and re-exports concrete blobstore implementations.

**Important APIs, Types, And Functions**
It declares `mod on_blocks;` and re-exports `BlobOnBlocks`, `BlobStoreOnBlocks`, `DataInnerNode`, `DataLeafNode`, `DataNode`, `DataNodeStore`, `DataTree`, `DataTreeStore`, and `LoadNodeError`. It also declares `mod shared;`. Under tests or the `testutils` feature, it exposes the `tracking` implementation and re-exports `BlobStoreActionCounts` and `TrackingBlobStore`.

**Control Flow**
Consumers import concrete types from `crate::implementations` or from the crate root, which itself re-exports these symbols.

**State And Persistence**
The module has no state. It shapes the public module boundary for implementation types.

**Dependencies And Integration Points**
It integrates the on-blocks storage stack with optional test tracking utilities.

**Risks**
Re-exporting internal data-node/tree types exposes implementation details, making later refactors more compatibility-sensitive. The conditional tracking exports must match feature gates in `Cargo.toml`.

**Test Signals**
Compilation under test, default, no-default, and all-features modes validates the feature gating and public export graph.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blob_on_blocks.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blob_on_blocks.rs

**Purpose**
`BlobOnBlocks` adapts a `DataTree` into the public `Blob` trait, making a block-backed data tree look like a byte-addressable blob.

**Important APIs, Types, And Functions**
The struct stores `tree: AsyncDropGuard<DataTree<B>>`. `new` wraps a tree. `_tree` and `_tree_mut` expose references internally. `into_data_tree` is available for tests/testutils. The `Blob` implementation provides `id`, `num_bytes`, `resize`, `read_all`, `read`, `try_read`, `write`, `flush`, `num_nodes`, `remove`, and `all_blocks`.

**Control Flow**
Every blob operation delegates to the underlying `DataTree`. `id` returns a `BlobId` whose root is `tree.root_node_id()`. `remove` consumes the async-drop guard, extracts the tree without dropping it, and calls `DataTree::remove`. `AsyncDrop` delegates to the guarded tree.

**State And Persistence**
State is the guarded tree, which may include cached dirty nodes and references to the underlying blockstore. Persistence happens when the tree flushes or removes blocks through lower layers.

**Dependencies And Integration Points**
It depends on the public `Blob` trait, `BlobId`, `BlockStore`, `BlockId`, `AsyncDropGuard`, `Data`, and futures streams. `BlobStoreOnBlocks` creates and loads these objects.

**Risks**
The consume-without-drop path in `remove` relies on `DataTree::remove` handling cleanup completely. The trait requires `&mut self` for read-only operations, which simplifies cache mutation but constrains callers.

**Test Signals**
The broader blobstore tests exercise this adapter via public blob operations; `into_data_tree` supports lower-level test inspection.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blob_on_blocks.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blobstore_on_blocks.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blobstore_on_blocks.rs

**Purpose**
`BlobStoreOnBlocks` adapts a `DataTreeStore` over a `BlockStore` into the public `BlobStore` trait.

**Important APIs, Types, And Functions**
The struct owns `tree_store: AsyncDropGuard<DataTreeStore<B>>`. `new` constructs a `DataTreeStore` from an async-drop blockstore and physical block size. `load_block_depth` exposes tree-store depth loading. `into_inner_tree_store` supports consuming the wrapper. The `BlobStore` implementation maps create/load/try-create/remove/flush/all-blobs operations to tree-store operations and wraps trees as `BlobOnBlocks`.

**Control Flow**
`create` calls `create_tree`; `try_create` and `load` pass root `BlockId`s from `BlobId`; `remove_by_id` calls `remove_tree_by_id`; cache and size methods delegate unchanged. `AsyncDrop` drops the tree store.

**State And Persistence**
State is the guarded tree store and its underlying blockstore/cache. Persistence semantics are delegated to tree/node/blockstore flush and remove behavior.

**Dependencies And Integration Points**
It bridges the public `BlobStore` trait, `BlobId`, `RemoveResult`, `DataTreeStore`, `BlockStore`, and `AsyncDropGuard`. It is the main concrete blobstore exported by the crate.

**Risks**
It accesses `BlobId.root` directly, so representation changes in `BlobId` require coordinated updates. Debug output is intentionally generic and does not expose the inner store.

**Test Signals**
Workspace blobstore tests and blockstore-adapter tests validate this implementation through trait-level behavior and feature-gated helpers.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/blobstore_on_blocks.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_inner_node.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_inner_node.rs

**Purpose**
This file implements `DataInnerNode`, the serialized tree node that stores child block IDs for non-leaf levels in the block-backed blob data tree.

**Important APIs, Types, And Functions**
`MAX_DEPTH` is 10. `DataInnerNode::new` validates format version, nonzero depth, exact block size, maximum depth, and child count range. Accessors include `depth`, `block_id`, `raw_blockdata`, `into_block`, `flush`, `num_children`, `children`, and `upcast`. Mutation APIs include test-only `update_child`, `add_child`, and `shrink_num_children`. Serialization helpers are `serialize_inner_node`, `initialize_inner_node`, and `_serialize_children`.

**Control Flow**
Loading constructs a binary-layout view over block data and enforces invariants before wrapping the block. Child iteration slices the data region into `BLOCKID_LEN` chunks and converts each used chunk to a `BlockId`. Adding a child checks the child depth is exactly one lower, writes the new child ID into the next slot, and increments `size`. Shrinking validates the new count is not larger, zeroes freed child slots, and writes the smaller size.

**State And Persistence**
State is the mutable block payload owned by the node. Mutations update the in-memory block; persistence requires `flush` through the blockstore or higher-level tree flushing.

**Dependencies And Integration Points**
It depends on `binary_layout`, `NodeLayout`, `BlockId`, `BlockStore`, `Data`, and `ZeroedData`. `DataNode` dispatches to it for parse/upcast behavior; `DataNodeStore` creates and flushes it.

**Risks**
Some invariant violations are `assert!` panics rather than recoverable errors, especially wrong node kind or invalid serialization parameters. Callers must avoid adding children to full nodes and must flush dirty changes for durable persistence.

**Test Signals**
Extensive tests cover loading failures, serialization, child addition at multiple depths, full-node failure, shrinking and zeroing, child iteration, depth, raw block conversion, and upcast behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_inner_node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_leaf_node.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_leaf_node.rs

**Purpose**
This file implements `DataLeafNode`, the serialized tree node that stores actual blob bytes in the block-backed blob data tree.

**Important APIs, Types, And Functions**
`DataLeafNode::new` validates format version, depth zero, exact block size, and stored byte count not exceeding layout capacity. Accessors and mutators include `block_id`, `raw_blockdata`, `into_block`, `flush`, `num_bytes`, `max_bytes_per_leaf`, `resize`, `data`, `data_mut`, and `upcast`. `serialize_leaf_node_optimized` writes the node header around a preallocated data region.

**Control Flow**
Loading reads the binary layout header and wraps the block only after validation. `resize` changes the logical size and zeroes bytes that become unused when shrinking, so shrinking then growing does not expose old data. `data` and `data_mut` return slices limited to the current logical size. Serialization grows the `Data` region backward to include the header, writes format/depth/size fields, and leaves the data region in place.

**State And Persistence**
The node owns a mutable block payload. In-memory mutations are not necessarily durable until `flush` is called through the blockstore stack.

**Dependencies And Integration Points**
It depends on `binary_layout`, `byte_unit`, `NodeLayout`, `BlockStore`, `BlockId`, and CryFS `Data`. `DataNodeStore` uses it for leaf creation, overwrite, and load.

**Risks**
Oversized writes and invalid serialization preconditions panic. `serialize_leaf_node_optimized` has a TODO to assert unused bytes are zeroed; callers currently ensure this by allocating/zeroing or by resize zeroing.

**Test Signals**
Tests cover valid/invalid loads, wrong format/depth/size, serialization fields, resize growth/shrink zeroing, mutable data access, block size behavior, byte count, into-block, and upcast behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_leaf_node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_node.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_node.rs

**Purpose**
`DataNode` is the enum wrapper that dispatches between inner and leaf node representations for block-backed blob trees.

**Important APIs, Types, And Functions**
The enum variants are `Inner(DataInnerNode<B>)` and `Leaf(DataLeafNode<B>)`. `parse` validates loaded block size and format version, then chooses leaf vs inner based on depth. Other APIs include `depth`, `block_id`, `raw_blockdata`, `_into_block`, `flush`, `convert_to_new_inner_node`, `overwrite_node_with`, `into_inner_node`, and `into_leaf_node`.

**Control Flow**
Parsing creates a binary-layout view, verifies the configured block size and supported format header, then delegates to `DataLeafNode::new` for depth 0 or `DataInnerNode::new` otherwise. `convert_to_new_inner_node` consumes an existing node’s block, zeroes the full payload, initializes it as a new inner node whose first child is the provided node, and returns a validated inner node. `overwrite_node_with` copies raw bytes from a source node into the destination block, preserving the destination block ID, then reparses the block.

**State And Persistence**
The enum owns the underlying block through the variant. Conversion and overwrite mutate block contents in memory; flush is required to push dirty data down to the blockstore when using cached/shared stores.

**Dependencies And Integration Points**
It depends on both node variants, `NodeLayout`, `binary_layout`, `BlockStore`, `BlockId`, `Data`, and `ZeroedData`. Higher tree and node-store code use it for generic node handling.

**Risks**
Wrong source or destination layouts trigger asserts. Overwrite can intentionally change a block from leaf to inner or inner to leaf, so callers must maintain tree invariants around references and depth.

**Test Signals**
Tests cover parse success/failure, invalid block sizes, wrong format, too-deep/too-many/too-few nodes, conversion zeroing, removal through node store, depth, overwrite combinations, and layout mismatch panics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/data_node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/mod.rs

**Purpose**
This module groups the concrete data-node variants and exposes their public wrapper types to the parent data-node store.

**Important APIs, Types, And Functions**
It declares `mod data_inner_node`, `mod data_leaf_node`, and `mod data_node`, then re-exports `DataInnerNode`, `DataLeafNode`, and `DataNode`.

**Control Flow**
Parent modules import node types through this module rather than addressing each file directly.

**State And Persistence**
The module has no state. Persistence behavior lives in the re-exported node implementations.

**Dependencies And Integration Points**
It is the integration point between `data_node_store` and the separate inner/leaf/enum implementation files.

**Risks**
No direct logic risk. Re-export shape determines which node internals become visible to sibling modules and crate users through higher-level re-exports.

**Test Signals**
Compilation of `data_node_store` and its tests validates this module wiring.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/data_node/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/layout.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/layout.rs

**Purpose**
This file defines the on-disk/in-block binary layout for data-tree nodes and helper calculations for leaf and inner-node capacity.

**Important APIs, Types, And Functions**
`FORMAT_VERSION_HEADER` is currently 0. The `binary_layout!` macro defines `node` fields: `format_version_header: u16`, `unused: u8`, `depth: u8`, `size: u32`, and variable `data: [u8]`. `NodeLayout` stores `block_size: Byte` and provides `header_len` in tests, `max_bytes_per_leaf`, `max_children_per_inner_node`, and `num_leaves_per_full_subtree`.

**Control Flow**
Capacity calculations subtract the header offset from usable block size. Inner-node fanout divides that data capacity by `BLOCKID_LEN`. Full-subtree leaf capacity raises fanout to the requested depth with checked overflow and returns `NonZeroU64`.

**State And Persistence**
The layout defines persisted bytes in every data node. The unused byte is reserved for alignment/future use. Format version guards compatibility.

**Dependencies And Integration Points**
It depends on `binary_layout`, `byte_unit`, `anyhow`, and `cryfs_blockstore::BLOCKID_LEN`. Inner and leaf node code use the generated view accessors for serialization and validation.

**Risks**
Several conversions use casts/TODOs rather than fully checked conversions. Layout changes require migration logic because old nodes validate against `FORMAT_VERSION_HEADER`.

**Test Signals**
Unit tests cover header offset, maximum leaf bytes, maximum children, and subtree leaf-count exponentiation for representative depths.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/layout.rs -->
