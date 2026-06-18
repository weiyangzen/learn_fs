# Research Group: subset-b-008302

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-config.c -->
# sources/security-integrity/audit-userspace/src/auditd-config.c

## Purpose
`auditd-config.c` owns `auditd.conf` loading, default initialization, validation, and cleanup for `struct daemon_conf`. It is a table-driven parser: `keywords[]` maps config names to small parser functions, while value tables map strings to enum values for log formats, flush techniques, failure actions, size actions, node name formats, yes/no values, overflow actions, and transports.

## Important APIs, Types, And Functions
Public entry points are `set_allow_links`, `set_config_dir`, `clear_config`, `load_config`, `audit_lookup_format`, `create_log_file`, `resolve_node`, `setup_percentages`, `free_config`, and `failure_action_to_str`. Internal helpers include `get_line`, `nv_split`, `kw_lookup`, `replace_string`, `check_exe_name`, `validate_email`, parser functions for every keyword, `calc_percent`, and `sanity_check`.

## Control Flow
`load_config` calls `clear_config`, chooses the config path, opens it with `O_NOFOLLOW` unless links are allowed, checks root ownership/world writability/regular-file status, then reads line by line. Each line is tokenized as `name = value [option]`, looked up in `keywords[]`, checked for option allowance, and dispatched to the keyword parser. Parsers validate ranges, file properties, executable paths, optional compile-time listener/GSS support, and string allocations. A non-empty file ends with `sanity_check`.

## State And Persistence
The file mutates the passed `daemon_conf` and module globals `allow_links`, `config_dir`, `config_file`, and `log_test`. Defaults include `/var/log/audit/audit.log`, `/etc/audit/plugins.d`, enriched logging, root mail, queue depth 2000, TCP disabled, and end-of-event timeout `EOE_TIMEOUT`. `free_config` releases string fields and resets config path globals. `create_log_file` persists a new audit log with owner-only write and group-readable mode under a restrictive umask.

## Dependencies And Integration
It depends on libc, filesystem/stat APIs, name service APIs, `libaudit`, `private.h`, and `common.h`. Runtime consumers are `auditd.c`, `auditd-event.c`, `auditd-listen.c`, `auditd-dispatch.c`, and `auditd-reconfigure.c`. Compile-time flags gate listener and GSS parsing behavior.

## Risks
Most parser branches are security-sensitive because they accept filesystem paths, email addresses, helper executables, and network parameters. Important risks are ownership/permission bypasses, path replacement during validation/open, allocation failure preserving old state, stale string ownership during live reconfiguration, percent threshold calculations on unusual filesystems, and DNS dependency in `validate_email` / `resolve_node`.

## Test Signals
`src/test/auditd_config_alloc_test.c` directly includes this file and tests allocation-failure preservation for `name_parser`, `log_file_parser`, and `set_config_dir`. Additional useful tests would cover malformed tokenization, executable permission matrices, percent thresholds, listener-disabled parsing, and `sanity_check` failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-config.h -->
# sources/security-integrity/audit-userspace/src/auditd-config.h

## Purpose
`auditd-config.h` defines the central audit daemon configuration contract. Its `struct daemon_conf` is the shared state object loaded from configuration and consumed by daemon startup, event logging, network listening, dispatcher setup, and live reconfiguration.

## Important APIs, Types, And Functions
The header declares `CONFIG_FILE`, `MEGABYTE`, `EOE_TIMEOUT`, daemon/log/flush/action/node/overflow/transport enums, `struct daemon_conf`, and configuration functions from `auditd-config.c`. It conditionally exposes `start_config_manager` only after `AUDITD_EVENT_H` is visible, reflecting the circular relationship between config loading and reconfigure events.

## Control Flow
The header itself has no runtime flow, but it encodes the shape of flow between modules. `load_config` fills the struct, `resolve_node` materializes node naming after startup, `setup_percentages` converts percent thresholds once a log fd exists, and `free_config` tears down string ownership. Daemon code passes the same struct pointer through initialization and later reconfiguration.

## State And Persistence
Persistent settings represented here include log path/format/group, rotation limits, disk threshold actions and helper paths, mail recipient and verification flag, TCP/GSS listener settings, dispatcher queue/restart controls, plugin directory, custom config directory, and user-space end-of-event timeout. Several fields are owned heap strings and require disciplined transfer/free behavior.

## Dependencies And Integration
The header depends on `libaudit.h`, `gcc-attributes.h`, and `<grp.h>`. It is included by auditd core, event, listener, dispatcher, and reconfigure modules, making it the ABI-like internal contract for audit daemon behavior.

## Risks
The main risk is ownership ambiguity: many fields are `const char *` but point to heap allocations that are freed or transferred during reconfiguration. Enum ordering is also externally meaningful inside string lookup tables such as `failure_actions`.

## Test Signals
Tests that instantiate `daemon_conf` should verify defaults from `clear_config`, string cleanup from `free_config`, and live reconfiguration ownership transfer. Compile tests should cover both listener/GSS enabled and disabled builds because this header shapes both configurations.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-dispatch.c -->
# sources/security-integrity/audit-userspace/src/auditd-dispatch.c

## Purpose
`auditd-dispatch.c` is the thin adapter between auditd events and the audisp dispatcher library. It initializes, shuts down, reconfigures, and queues events for plugins.

## Important APIs, Types, And Functions
Public functions are `init_dispatcher`, `shutdown_dispatcher`, `reconfigure_dispatcher`, and `dispatch_event`. `dispatch_event` allocates an `event_t`, fills `audit_dispatcher_header` fields, copies event bytes according to protocol version, and calls `libdisp_enqueue`.

## Control Flow
Startup calls `libdisp_init(config)`. Shutdown calls `libdisp_shutdown`. Reconfiguration calls `libdisp_reconfigure(config)`. For each routed audit event, `dispatch_event` first returns success if the dispatcher is inactive, then allocates an event, sets version/header/type/size, copies either `rep->msg.data` for protocol v1 or `rep->message` for protocol v2, rejects unknown protocol versions, and lets libdisp own the queue item.

## State And Persistence
This file keeps no persistent local state. Dispatcher state lives in libdisp and is reached through its API. Each queued event allocation is transient and handed to the dispatcher queue.

## Dependencies And Integration
It depends on `libaudit`, `private.h`, `auditd-dispatch.h`, and `libdisp.h`. It is called from `auditd.c` via `distribute_event` and from `auditd-reconfigure.c` after config changes.

## Risks
The critical risk is copy sizing: `event_t->data` must be large enough for `rep->msg.nlh.nlmsg_len` or `rep->len`. Protocol choice is tied to whether auditd has formatted a message as enriched/node-tagged. If callers pass inconsistent length/message fields, plugins may receive truncated or malformed data.

## Test Signals
Existing `format_event_test` links this file indirectly through auditd event formatting. Focused unit tests could stub libdisp to assert inactive behavior, protocol rejection, v1/v2 size fields, allocation failure, and overflow return propagation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-dispatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-dispatch.h -->
# sources/security-integrity/audit-userspace/src/auditd-dispatch.h

## Purpose
`auditd-dispatch.h` declares auditd's dispatcher facade. It hides libdisp details from the rest of auditd and exposes only lifecycle and event-queue operations.

## Important APIs, Types, And Functions
The API is `init_dispatcher`, `shutdown_dispatcher`, `reconfigure_dispatcher`, and `dispatch_event`. The header imports `auditd-config.h` so lifecycle calls can consume `struct daemon_conf`; `dispatch_event` uses `struct audit_reply` through included audit headers.

## Control Flow
Consumers initialize after event/log setup, call `dispatch_event` as part of normal event distribution, reconfigure after live config changes, and shut down during daemon exit. The header itself has no code paths.

## State And Persistence
No state is defined here. It formalizes the expectation that dispatcher state is managed behind the declared functions.

## Dependencies And Integration
It integrates with `auditd.c` and `auditd-reconfigure.c`. It also couples the daemon to libdisp's protocol constants through `auditd-dispatch.c`.

## Risks
Because return values distinguish success, queue overflow/suspension, and other errors in the implementation, callers need to preserve that semantic if they begin handling dispatch failures more explicitly. The header does not document ownership of queued event memory, so implementation knowledge is required.

## Test Signals
Build tests confirm the header is usable by daemon and reconfigure modules. API tests should validate that all callers include this header rather than depending directly on libdisp.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-dispatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-event.c -->
# sources/security-integrity/audit-userspace/src/auditd-event.c

## Purpose
`auditd-event.c` handles audit event formatting, local log writes, disk space/size actions, log rotation, network acknowledgements, and the bridge into live reconfiguration.

## Important APIs, Types, And Functions
Public APIs include `dispatch_network_events`, `write_logging_state`, `shutdown_events`, `init_event`, `auditd_get_exec_pid`, `auditd_clear_exec_pid`, `resume_logging`, `cleanup_event`, `format_event`, `enqueue_event`, `create_event`, and `handle_event`. Internal hotspots include `format_raw`, `format_enrich`, `write_to_log`, `check_log_file_size`, `check_space_left`, `do_space_left_action`, `do_disk_full_action`, `do_disk_error_action`, `rotate_logs`, `shift_logs`, `open_audit_log`, `safe_exec`, and `reconfigure`.

## Control Flow
`init_event` stores the config, opens stdout or the audit log, applies disk permissions, checks rotation state, allocates the format buffer, and starts an async flush thread. Events are formatted raw/enriched, optionally written to local logs, flushed according to config, acknowledged to remote senders, and routed to disk/rotation/error handlers. `AUDIT_DAEMON_RECONFIG` events invoke `auditd_reconfigure` through a callback context.

## State And Persistence
The file holds global mutable logging state: config pointer, atomic log fd, `FILE *`, disk warning flags, suspension state, known rotated logs, helper child pid, format buffer, log size, flush thread primitives, and auparse state. It persists audit records to the configured log file, rotates files on size/space triggers, changes file ownership/modes, and can close logging until resumed.

## Dependencies And Integration
It depends on pthreads, signals, filesystem APIs, `libaudit`, `auparse`, `common.h`, `private.h`, `auditd-config.h`, and `auditd-reconfigure.h`. `auditd.c` supplies `stop`, `event_is_prealloc`, and `distribute_event`; `auditd-listen.c` uses `create_event` and ack callbacks for remote clients.

## Risks
Risks include global state races between the main loop and flush thread, ownership of `reply.message`, truncation in formatting, disk action side effects (`single`, `halt`, helper exec), reopen failures after rotation/reconfigure, and remote ack correctness when logging is suspended or disk-full. The weak `event_is_prealloc` fallback changes cleanup behavior depending on link target.

## Test Signals
`src/test/format_event_test.c` verifies raw/enriched formatting and interpretation separator behavior. Additional test signals should exercise write failure branches, async flush, rotation naming, suspended/resume paths, network ack types, and reconfigure callback behavior with mocked operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-event.h -->
# sources/security-integrity/audit-userspace/src/auditd-event.h

## Purpose
`auditd-event.h` defines the event object and event-processing API shared by daemon core, listener, reconfiguration, and tests.

## Important APIs, Types, And Functions
It defines `ack_func_type`, `struct auditd_event`, and declarations for event lifecycle, formatting, queueing, handling, distribution, logging state, shutdown, and remote event creation. `struct auditd_event` wraps `struct audit_reply` plus optional ack callback data and a remote sequence id.

## Control Flow
Headers consumers create or receive an event, optionally attach network ack information, call `format_event`, `handle_event`, `enqueue_event`, or `distribute_event`, and then rely on `cleanup_event` to free dynamic message/event storage. Network-originating events are identified by a non-null `ack_func`.

## State And Persistence
No state is stored in the header. It documents the shape of transient event state and exposes logging state writers/resume helpers backed by `auditd-event.c`.

## Dependencies And Integration
The header includes `libaudit.h`, `gcc-attributes.h`, and `auditd-config.h`, creating a mutual dependency that is managed by include guards. It is used by `auditd.c`, `auditd-listen.c`, `auditd-reconfig.c`, `auditd-reconfigure.h`, and tests.

## Risks
The public struct exposes internal ownership-sensitive fields directly. Duplicate declarations of `auditd_get_exec_pid` and `auditd_clear_exec_pid` are harmless but noisy. Any caller that sets `ack_func` changes formatting/length semantics for network-originating events.

## Test Signals
Compile and link tests around `format_event_test` validate the header contract. Unit tests should cover `create_event` / `cleanup_event` ownership combinations for network and local events.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-listen.c -->
# sources/security-integrity/audit-userspace/src/auditd-listen.c

## Purpose
`auditd-listen.c` implements auditd's remote aggregation TCP listener. It accepts remote audit records, optionally negotiates Kerberos/GSSAPI security, turns received messages into `auditd_event` objects, and sends protocol acknowledgements after local handling.

## Important APIs, Types, And Functions
Public functions are `auditd_tcp_listen_init`, `auditd_tcp_listen_uninit`, `auditd_tcp_listen_reconfigure`, and `write_connection_state`. Key internal pieces are `ev_tcp`, socket/address helpers, `client_ack`, `client_message`, `auditd_tcp_client_handler`, `auditd_tcp_listen_handler`, `check_num_connections`, idle `periodic_handler`, and GSS token/credential helpers under `USE_GSSAPI`.

## Control Flow
Initialization resolves wildcard bind addresses, creates up to four listener sockets, chooses IPv6 preference when appropriate, binds/listens, registers libev IO watchers, starts idle timers, applies configured source port and per-address limits, and acquires GSS credentials if needed. Accept flow applies libwrap, source port range, duplicate connection limits, socket options, optional GSS negotiation, nonblocking mode, and list insertion. Read flow handles GSS tokens, RMW framed messages, or newline-delimited messages, then creates remote events or responds to heartbeats.

## State And Persistence
Module globals track listener sockets, count, libev watchers, allowed ports, libwrap flag, transport mode, receive buffer, linked client list, and GSS server credentials. No on-disk persistence is owned here, but accepted/closed connections emit audit daemon events and remote events may be persisted by `auditd-event.c`.

## Dependencies And Integration
It depends on sockets, netdb, libev, optional libwrap, optional GSSAPI/Kerberos, `libaudit`, `auditd-event.h`, and `auditd-config.h`. It calls `send_audit_event`, `create_event`, `distribute_event`, and network ack callbacks.

## Risks
Risks include blocking GSS negotiation inside an otherwise nonblocking listener, buffer/length handling for mixed protocols, remote event type extraction later in `auditd.c`, trust assumptions around firewall plus source port checks, per-address IPv4/IPv6 comparison correctness, and partial live reconfigure behavior for listener port/transport changes that require restart.

## Test Signals
No focused listener unit test appears in `src/test`, though `format_event_test` can link `auditd-listen.c` when listener support is enabled. Useful tests would simulate framed/newline/GSS message parsing, heartbeat ack, idle timeout, libwrap rejection, port range rejection, and reconfigure of queue/port settings.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-listen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-listen.h -->
# sources/security-integrity/audit-userspace/src/auditd-listen.h

## Purpose
`auditd-listen.h` exposes the listener lifecycle and state-reporting API while compiling to no-op inline functions when listener support is disabled.

## Important APIs, Types, And Functions
When `USE_LISTENER` is defined, it declares `auditd_tcp_listen_init`, `auditd_tcp_listen_uninit`, `auditd_tcp_listen_reconfigure`, and `write_connection_state`. Otherwise it supplies inline stubs for init/uninit/reconfigure, allowing callers to avoid compile-time conditionals.

## Control Flow
Daemon startup calls init after libev setup; shutdown calls uninit; live reconfigure calls reconfigure; state dump calls `write_connection_state` only under listener-enabled builds. The stubbed disabled path returns success and performs no work.

## State And Persistence
The header owns no state. It abstracts whether listener state exists in `auditd-listen.c`.

## Dependencies And Integration
It includes `config.h`, `ev.h`, and `<stdio.h>`, and is used by `auditd.c` and `auditd-reconfigure.c`. The API consumes `struct daemon_conf`, provided by transitive includes in normal builds.

## Risks
The disabled inline `auditd_tcp_listen_reconfigure` signature lacks `const` symmetry with the enabled declaration, which can produce warnings or hide const-correctness issues. Consumers must remember `write_connection_state` only exists in listener builds.

## Test Signals
Build matrix tests with listener enabled and disabled are the main signal. Reconfigure compile coverage is important because this header intentionally changes behavior by preprocessor path.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-listen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-reconfig.c -->
# sources/security-integrity/audit-userspace/src/auditd-reconfig.c

## Purpose
`auditd-reconfig.c` manages asynchronous configuration reload loading after SIGHUP. It isolates slow file parsing and DNS/name lookups from the main libev loop, then signals readiness back to `auditd.c`.

## Important APIs, Types, And Functions
Public APIs are `init_config_manager` and `start_config_manager`. Internals are `config_thread`, `config_lock`, and `config_thread_main`. It relies on external `reconfig_ready` and `send_audit_event`.

## Control Flow
`init_config_manager` initializes a mutex. `start_config_manager` attempts a nonblocking mutex lock; if no reload is active, it creates a detached thread with the incoming signal-info event; otherwise it logs failure, cleans the event, and returns an error. The thread blocks daemon signals, calls `load_config`, copies sender uid/pid/context from the original signal info into the new config, stores the config bytes inside the event's netlink buffer, sets `reply.conf`, changes the event type to `AUDIT_DAEMON_RECONFIG`, and calls `reconfig_ready`. On load failure it emits a failed config event, frees the temporary config, and cleans up.

## State And Persistence
The only persistent state is the reload mutex/thread handle. The new `daemon_conf` is transient until copied into the event buffer and later consumed by `auditd-reconfigure.c`.

## Dependencies And Integration
It depends on pthreads, signals, `libaudit`, `auditd-event.h`, `auditd-config.h`, and `private.h`. `auditd.c` starts it after receiving `AUDIT_SIGNAL_INFO` and later consumes readiness through a socketpair.

## Risks
Packing `struct daemon_conf` into `reply.msg.data` assumes the buffer can hold it and that pointer fields remain valid until the applier transfers/frees them. The mutex prevents concurrent reloads but rejected reloads become failed audit events. Ownership of `sender_ctx` and other strings crosses thread boundaries.

## Test Signals
No direct unit test exists. Tests should cover concurrent `start_config_manager`, load failure event emission, signal masking, event buffer layout, and cleanup when thread creation fails.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-reconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-reconfigure.c -->
# sources/security-integrity/audit-userspace/src/auditd-reconfigure.c

## Purpose
`auditd-reconfigure.c` applies a loaded `daemon_conf` to a running daemon. It was separated from `auditd-event.c` and uses a context object to update logging state via explicit callbacks.

## Important APIs, Types, And Functions
Public API is `auditd_reconfigure`. Internal phases are `reconfigure_general_options`, `reconfigure_network_options`, `reconfigure_dispatcher_options`, `reopen_log_file`, `reconfigure_log_file_options`, `reconfigure_disk_space_options`, and `emit_reconfigure_event`.

## Control Flow
`auditd_reconfigure` logs requester identity, then applies changes from least to most invasive: general daemon options, network listener options, dispatcher/plugin options, log file/rotation options, disk space thresholds/actions, dispatcher reconfigure, and final success event emission. Log changes set flags for reopen, size check, or space check; `reopen_log_file` uses callbacks supplied by `auditd-event.c`.

## State And Persistence
It mutates the live `daemon_conf`, transfers or frees string fields from the new config, resets disk warning flags, may reopen persistent log files, recalculates percentage thresholds against the current log fd, restarts/reconfigures listener pieces, and emits a final `AUDIT_DAEMON_CONFIG` record.

## Dependencies And Integration
It depends on `auditd-reconfigure.h`, `auditd-dispatch.h`, `auditd-listen.h`, and `private.h`, plus external `update_report_timer`. The context is built in `auditd-event.c` and the event originates from `auditd-reconfig.c`.

## Risks
String ownership is subtle: some nconf pointers are transferred into oconf, some are duplicated, some freed, and some can alias after listener reconfigure. Null handling is incomplete in comparisons like `strcmp(oconf->action_mail_acct, nconf->action_mail_acct)` if future defaults change. Reopen/space checks can suspend logging. Random sequence generation for the emitted event is not security-critical but non-deterministic.

## Test Signals
No focused reconfigure unit test is present. The linked `format_event_test` includes this file for integration. Valuable tests would use a fake context and callbacks to verify ownership, reopen flags, size/space check ordering, listener restart decisions, and emitted event contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-reconfigure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-reconfigure.h -->
# sources/security-integrity/audit-userspace/src/auditd-reconfigure.h

## Purpose
`auditd-reconfigure.h` defines the context boundary used to apply a live configuration update without hard-linking all logging internals into the reconfigure implementation.

## Important APIs, Types, And Functions
It defines `struct auditd_reconfigure_state` for pointers to mutable logging flags and `FILE *`, `struct auditd_reconfigure_ops` for callbacks back into the event/logging layer, `struct auditd_reconfigure_context` for event/config/state/ops plus change flags, and `auditd_reconfigure`.

## Control Flow
`auditd-event.c` constructs the context, filling pointers and callbacks, then calls `auditd_reconfigure`. The applier toggles `need_size_check`, `need_reopen`, and `need_space_check` while mutating config and invoking callbacks.

## State And Persistence
The header describes borrowed pointers into `auditd-event.c` state rather than owning state itself. It enables reconfigure code to close/reopen persistent log files and reset warning flags through controlled indirection.

## Dependencies And Integration
It includes `<stdio.h>` and `auditd-event.h`, which brings in `struct daemon_conf`. It is included by `auditd-event.c` and `auditd-reconfigure.c`.

## Risks
Callback pointers are trusted and not null-checked by the implementation. Because the state fields are raw pointers, incorrect context construction could corrupt daemon logging state. The context is synchronous, so callers must not outlive borrowed event/config pointers.

## Test Signals
Compile coverage exists via `format_event_test`. Unit tests should build mock contexts with instrumented callbacks to verify call ordering and guard against null or invalid callback regressions if the API expands.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-reconfigure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-sendmail.c -->
# sources/security-integrity/audit-userspace/src/auditd-sendmail.c

## Purpose
`auditd-sendmail.c` sends email alerts for audit daemon disk-space actions. It wraps `/usr/lib/sendmail` execution and writes a simple message to the child's stdin.

## Important APIs, Types, And Functions
Public API is `sendmail(subject, content, mail_acct)`. Internal helper `safe_popen` creates a pipe, forks, redirects child stdin, builds `sendmail -t -f<acct>`, and execs the configured `email_command`.

## Control Flow
`sendmail` checks that `email_command` is executable, calls `safe_popen`, converts the returned write fd to a `FILE *`, writes To/From/Subject headers plus content and SMTP terminator, then closes the stream. On `fdopen` failure it kills the child and logs an error.

## State And Persistence
No local persistent state exists. It reads global `email_command` from `auditd-config.c`. It creates a child process and writes email content over a pipe; actual delivery persistence is delegated to the mailer.

## Dependencies And Integration
It depends on libc process/pipe APIs, signals, `libaudit`, `private.h`, and `auditd-config.h`. It is called from `auditd-event.c` for `FA_EMAIL` disk space warnings.

## Risks
The sender account is included in `-f%s`; parser validation limits characters but this helper still trusts the value. The child inherits most file descriptors except stdin adjustment because it does not close descriptors broadly. The parent does not wait here, relying on daemon SIGCHLD handling. Delivery failures after `fclose` are not inspected.

## Test Signals
`format_event_test` links this file, but no mail-specific tests exist. Useful tests would override `email_command`, simulate pipe/fork/fdopen failures, validate argv construction, and verify no descriptor leaks in the child path.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd-sendmail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd.c -->
# sources/security-integrity/audit-userspace/src/auditd.c

## Purpose
`auditd.c` is the audit daemon main program. It parses CLI options, loads config, daemonizes, registers with the kernel audit subsystem, starts logging/dispatcher/listener subsystems, runs the libev event loop, handles signals, routes netlink events, and performs orderly shutdown.

## Important APIs, Types, And Functions
Important functions include signal handlers for TERM/HUP/USR1/USR2/CHLD/CONT, `update_report_timer`, `distribute_event`, `send_audit_event`, `become_daemon`, `alloc_pool_event`, `event_is_prealloc`, `netlink_handler`, `pipe_handler`, `reconfig_ready`, `main`, `clean_exit`, `get_reply`, and `getsubj`.

## Control Flow
`main` parses `-f/-l/-n/-s/-c`, sets foreground/background mode, ignores signals until libev owns them, loads config, checks capabilities, daemonizes if needed, opens netlink, creates runtime dir/pidfile, initializes events, libev, dispatcher, node name, reconfigure socketpair, start event, OOM adjustment, config manager, startup audit enablement, audit pid registration, signal/io/timer watchers, optional TCP listener, then enters `ev_loop`. Shutdown stops listener/watchers, emits end event, tears down dispatcher/events/config, and destroys libev.

## State And Persistence
Global state includes audit netlink fd, config, pid/state file paths, daemonization pipe, event pool, signal request atomics, subject buffer, audit session, report timer, and libev loop. It persists pid and state report files under `AUDIT_RUN_DIR`, emits audit daemon lifecycle records, and registers/unregisters the audit pid with the kernel.

## Dependencies And Integration
It integrates every major local subsystem: config, event, dispatch, listener, reconfig manager, libdisp, libaudit, libev, and common/private helpers. Kernel audit interaction uses `audit_open`, `audit_set_pid`, `audit_get_reply`, `audit_request_signal_info`, and related libaudit APIs.

## Risks
Risks include startup ordering failures leaving partial state, preallocated event pool exhaustion causing daemon abort, signal-info request races, using a socketpair to transfer reload readiness, daemon parent/child synchronization, cleanup via `atexit`, and aggregate-only mode changing kernel registration/listener behavior. `extract_type` must parse network-originated formatted events correctly for plugin routing.

## Test Signals
There is no direct daemon main unit test. Integration/system tests should cover foreground/background startup, no-fork mode, aggregate-only remote logging, SIGHUP reload, USR1 rotation, USR2 resume, SIGCONT state dump, netlink event filtering, pidfile cleanup, and listener startup failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-options.c -->
# sources/security-integrity/audit-userspace/src/aureport-options.c

## Purpose
`aureport-options.c` parses `aureport` command-line options and initializes global report and search-selector state used by the scanner and output layers.

## Important APIs, Types, And Functions
Public API is `check_params`. Global outputs include `user_file`, `force_logs`, `no_config`, parser-compatible `event_*` filters, `arg_eoe_timeout`, `report_type`, `report_detail`, `report_format`, `event_failed`, `event_conf_act`, `event_success`, and `escape_mode`. Internals include `optiontab`, `audit_lookup_option`, `usage`, `set_report`, and `set_detail`.

## Control Flow
`check_params` walks argv manually, infers optional arguments by checking whether the next token begins with `-`, maps option strings to enum values, enforces one report type, sets detailed/summary modes, primes scanner filters with dummy sentinels, parses time windows through `ausearch_time_start/end`, appends node filters, parses escape mode and EOE timeout, handles help/version exits, and defaults to summary report if no report was selected.

## State And Persistence
The file is almost entirely global mutable state. It does not persist to disk, but it determines which audit records are scanned and how output is interpreted. Some allocated state, such as `user_file` and node strings, is handed to later program lifetime cleanup.

## Dependencies And Integration
It depends on `aureport-options.h`, `ausearch-time.h`, `libaudit.h`, `auparse-defs.h`, passwd/group/time headers, and scanner-compatible globals declared elsewhere. `aureport.c` calls `check_params`, and `aureport-output.c` consumes `report_type`, `report_detail`, `report_format`, and filters.

## Risks
Manual option parsing can misclassify negative values as options. Many report filters are set by sentinel values like `dummy`, which requires scanner code to interpret presence rather than actual value. Several specific report options are still `UNIMPLEMENTED` and exit immediately. Global state makes repeated invocations in one process unsafe unless reinitialized.

## Test Signals
No focused option tests are present. Tests should exercise every report selector, conflicting report types, default summary mode, time parsing permutations, node list allocation, escape mode parsing, EOE timeout validation, and unsupported option error paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-options.h -->
# sources/security-integrity/audit-userspace/src/aureport-options.h

## Purpose
`aureport-options.h` defines the report mode contract for `aureport`. It exposes report type/detail enums, global option state, and the command-line parser entry point.

## Important APIs, Types, And Functions
It defines `report_type_t` with summary, AVC, MAC, config, event, file, host, login, account modification, PID, syscall, terminal, user, executable, anomaly, response, crypto, auth, key, TTY, command, virtualization, and integrity reports. It defines `report_det_t` for summary/detailed/specific output and declares `report_type`, `report_detail`, `report_format`, and `check_params`. It also defines the `UNIMPLEMENTED` exit macro.

## Control Flow
No runtime flow exists in the header. It lets `aureport-options.c` set modes and lets scan/output modules branch on those modes.

## State And Persistence
The declared globals are process-wide state. They persist for the lifetime of one `aureport` run and shape scan and output behavior.

## Dependencies And Integration
It includes `ausearch-common.h`, tying report formatting to common ausearch/aureport types such as `report_t`. It is used by option parsing and output code.

## Risks
The `UNIMPLEMENTED` macro prints and exits from wherever invoked, making partial option paths abrupt and hard to unit test. New report types require synchronized changes in option parsing, scanning, titles, detailed output, and summaries.

## Test Signals
Compile coverage is necessary whenever adding enum values. Behavioral tests should verify every enum has parser and output handling and that `UNIMPLEMENTED` paths are intentional.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-output.c -->
# sources/security-integrity/audit-userspace/src/aureport-output.c

## Purpose
`aureport-output.c` prints report titles, per-event detailed rows, and summary wrap-up tables for `aureport` based on scanner results and option globals.

## Important APIs, Types, And Functions
Public functions are `print_title`, `print_per_event_item`, and `print_wrap_up`. Internal functions include `print_title_summary`, `print_title_detailed`, `do_summary_output`, and summary printers for file/string/user/int/syscall/type lists.

## Control Flow
`print_title` resets line numbering and selects summary or detailed title output. `print_per_event_item` formats one `llist` event according to `report_type`, using lookup helpers for syscall, uid, success, message type, TTY data, AVC lists, and safe string printing. `print_wrap_up` runs only for summary mode, sorts the relevant aggregate list in `sd`, then prints the appropriate summary. `do_summary_output` prints global ranges and aggregate counters.

## State And Persistence
Local state is only `line_item`. It consumes global `report_type`, `report_detail`, `report_format`, filter flags, scanner summary `sd`, `start_time/end_time`, and first/last event globals. It writes to stdout and does not persist files.

## Dependencies And Integration
It depends on `aureport-scan.h`, `aureport-options.h`, and `ausearch-lookup.h`. The scanner calls `print_per_event_item` while walking events and `print_wrap_up` after aggregation.

## Risks
Output paths assume many fields are non-null for specific reports; some branches guard with `?`, others pass values directly. `RPT_AVC` can emit multiple rows per event. `RPT_TTY` mutates the message buffer by replacing a trailing space with NUL before printing. Summary output depends on scanner-maintained aggregate lists and event range globals being initialized.

## Test Signals
No output-specific unit tests are present. Golden-output tests should cover each report type in detailed and summary modes, interpreted/default type formatting, empty aggregates, safe printing of spaces/control characters, AVC multi-row output, TTY data decoding, and null field handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-output.c -->
