# subset-b-008296 Research

Grouped research for audit userspace audisp plugin sources under `sources/security-integrity/audit-userspace/audisp/plugins`. Each section is wrapped for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids_config.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/ids_config.c

Purpose: parses `/etc/audit/ids.conf` into the global IDS tuning structure used by the bad-event and behavior models. It supplies defaults for login thresholds, reaction masks, scoring weights, and timed reaction durations.

Important APIs and data: exports `reset_config`, `free_config`, `dump_config`, and `load_config`. Local parser tables map option names to parser callbacks; `reactions[]` maps names such as `block_address`, `term_session`, and `lock_account_timed` onto bit flags from `ids_config.h`.

Control flow: `load_config` resets defaults, opens the fixed config path, verifies root ownership, non-world-writability, and regular-file status, then reads `name = value` lines through `get_line` and `nv_split`. Unknown keywords, malformed lines with values, or parser failures abort loading; missing config is allowed with defaults.

State and persistence: no heap-owned config state is retained after parsing, so `free_config` is empty. Parsed values live in the caller-owned `struct ids_conf`; timed values are converted to seconds and remain process memory only.

Dependencies and integration: depends on `audit_strsplit`, syslog, `time_string_to_seconds`, and the reaction constants consumed by `reactions.c`. The parser must remain aligned with documented `ids.conf` option names and the event model thresholds.

Risks: line length is capped at 160 bytes and overlong lines are skipped, which can silently leave defaults. `reaction_parser` accepts comma-separated names but does not trim whitespace around tokens. `block_address_time_parser` has custom unit parsing while `lock_account_time_parser` uses the shared time parser, so behavior can diverge.

Test signals: useful tests are malformed permission checks, unknown keywords, reaction-mask combinations, numeric range failures, time suffixes, and missing-file default behavior. No direct tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids_config.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/ids_config.h

Purpose: declares the IDS configuration ABI and bitmask values for every supported automated reaction.

Important APIs and data: defines `REACTION_*` flags for ignore/log/email, process/session termination, account actions, address blocking, and system-level termination. Declares `struct ids_conf`, `extern struct ids_conf config`, and config lifecycle functions.

Control flow: no executable flow; this header is included by config parsing, models, and reaction execution code.

State and persistence: `struct ids_conf` is process-local state, with no persistence contract beyond rereading `/etc/audit/ids.conf`.

Dependencies and integration: used by `ids_config.c`, `model_bad_event.c`, `model_behavior.c`, `origin.c`, `session.c`, `reactions.c`, and timer services. Reaction bits are iterated by `do_reaction`, so each flag must remain a unique single-bit value.

Risks: comments list planned but unimplemented defenses, which can be mistaken for available behavior. Adding flags beyond bit 31 would require auditing `do_reaction`'s 32-bit loop.

Test signals: compile-time consumers validate structure layout and constants; runtime tests should confirm each configured reaction string maps to the intended bit.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/model_bad_event.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/model_bad_event.c

Purpose: implements the IDS model that reacts to login and system lifecycle audit events. It creates and tears down sessions, scores origins for failed or forbidden logins, and triggers origin-level reactions.

Important APIs and data: exports `process_bad_event_model`. Local helpers `start_session`, `end_session`, and `terminate_sessions` coordinate origin/session state with auparse-normalized fields.

Control flow: for boot/shutdown, all sessions are destroyed. For `AUDIT_USER_LOGIN`, `start_session` extracts `addr`, subject kind/account, result, and session id; creates/fetches an origin; scores service/root/failed login conditions; and creates a session for successful user logins. For logout, `end_session` removes non-daemon sessions. After event-specific handling, current origin karma is checked against `option_origin_failed_logins_threshold` and `do_reaction` is called if unblocked.

State and persistence: mutates in-memory origin AVL state and session AVL state. System boot/shutdown clear session state, but origin state persists until process restart or explicit destroy.

Dependencies and integration: depends on auparse normalization, libaudit event constants, `origin.c`, `session.c`, global `debug`, and `reactions.c`. It intentionally ignores IDS-generated anomaly events to avoid feeding on its own responses.

Risks: IPv4-only address conversion stores invalid or absent addresses as `-1`, which can aggregate unrelated unknown origins. `inet_pton` return is not checked. Account ownership transfer to `new_session` is subtle and depends on setting `acct = NULL` after successful creation.

Test signals: audit events for successful login, failed login, root/service account login, logout, daemon session, and system boot/shutdown should drive expected session/origin counts and reaction calls.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/model_bad_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/model_bad_event.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/model_bad_event.h

Purpose: declares the bad-event IDS model entry point for complete auparse events.

Important APIs and data: exposes `process_bad_event_model(auparse_state_t *, struct ids_conf *)`.

Control flow: no implementation; callers pass one complete auparse event plus current config.

State and persistence: no state in the header; implementation mutates session/origin state.

Dependencies and integration: includes `auparse.h` and `ids_config.h`, coupling consumers to auparse and the IDS config structure.

Risks: the API assumes auparse state is positioned safely by the implementation; callers should not pass partial events.

Test signals: compile-time inclusion and model dispatch tests through the IDS main event loop.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/model_bad_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/model_behavior.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/model_behavior.c

Purpose: scores user sessions based on suspicious audited behavior, especially IDS-tagged audit rules and anomaly records, then triggers session or origin reactions.

Important APIs and data: exports `process_behavior_model`. Local helpers `process_plain_syscalls` and `process_anomalies` inspect auparse event type, key, and session id.

Control flow: syscall events are filtered to audit keys beginning with `ids-`; known keys add fixed session score weights: recon 2, archive 5, mkexec 4, and connections 6. Fanotify/AVC/anomaly events add 12 or 2 points to the current session. After scoring, current session and origin thresholds are checked and `do_reaction` is called for session badness or origin failed-login badness.

State and persistence: updates in-memory `session_data_t.score` and may raise origin karma after a session reaction. No disk persistence; session state disappears when removed or on process restart.

Dependencies and integration: depends on audit rules in `rules/*.rules`, auparse normalization, `session.c`, `origin.c`, and `reactions.c`. The configured thresholds and reactions are from `ids_config.c`.

Risks: scoring depends on audit rule key strings staying exactly synchronized. `s->killed` is checked but this file never sets it, so repeated session reactions may occur unless another reaction path mutates it. Daemon or missing sessions are ignored.

Test signals: feed auparse events with keys `ids-recon`, `ids-archive`, `ids-mkexec`, and `ids-connections`; verify score increments and threshold-triggered reactions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/model_behavior.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/model_behavior.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/model_behavior.h

Purpose: declares the behavior model entry point for complete auparse events.

Important APIs and data: exposes `process_behavior_model(auparse_state_t *, struct ids_conf *)`.

Control flow: none in the header; implementation dispatches by audit record type and key.

State and persistence: no header-owned state; the implementation mutates current sessions and origins.

Dependencies and integration: includes auparse and IDS config types, used by the IDS main dispatcher to chain models.

Risks: callers must provide a complete event and a valid config pointer.

Test signals: compile coverage and integration tests through model dispatch.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/model_behavior.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/nvpair.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/nvpair.c

Purpose: provides a minimal singly linked list for delayed timer jobs with an argument string and expiration time.

Important APIs and data: implements `nvpair_list_create`, `nvpair_list_append`, `nvpair_list_find_job`, `nvpair_list_delete_cur`, and `nvpair_list_clear` over `nvlist`/`nvnode`.

Control flow: append copies job metadata and takes ownership of the `arg` pointer from the source node. `find_job` scans from the head for the first expired entry and positions `cur`/`prev`; delete frees the current node and its `arg`; clear frees all nodes.

State and persistence: list state is caller-owned memory. It is used by timer services and is not persisted.

Dependencies and integration: depends on `timer-services.h` for `jobs_t`. `timer-services.c` relies on `find_job` positioning the current item before deletion.

Risks: `nvpair_list_append` assumes `l->cur` is meaningful when appending to a non-empty list; callers must not corrupt cursor state. `delete_cur` does not advance `cur` after deletion, so callers should search again before using it.

Test signals: append/find/delete/clear with head, middle, tail, and empty-list cases; timer services exercise the expired-job path.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/nvpair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/nvpair.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/nvpair.h

Purpose: declares the IDS timer job list types and operations.

Important APIs and data: `nvnode` stores `jobs_t job`, `char *arg`, `time_t expiration`, and `next`; `nvlist` stores `head`, `cur`, `prev`, and `cnt`. Inline helpers expose first/current cursor access.

Control flow: no implementation except inline cursor assignment and getter.

State and persistence: describes in-memory linked list state only.

Dependencies and integration: includes `timer-services.h`, tying nodes to timer job enum values.

Risks: exposed mutable fields let callers break list invariants. Ownership of `arg` is not obvious from the type alone.

Test signals: compile-time users in timer services and behavioral tests for cursor mutation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/nvpair.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/origin.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/origin.c

Purpose: tracks remote IPv4 origins, their accumulated karma score, and whether they are currently blocked.

Important APIs and data: exports initialization, traversal, creation/destruction, add/find/delete/current access, score adjustments, login anomaly helpers, IPv4 conversion helpers, and `unblock_origin`.

Control flow: origins are stored in an AVL tree keyed by integer IPv4 address. Bad service/root login helpers log audit anomaly events and add configured weights. `bad_login_origin` increments by failed-login weight. `unblock_origin` finds by dotted string and clears the blocked flag.

State and persistence: global static AVL tree plus global `cur` pointer are process-local only. Blocking state is mirrored in firewall side effects via `reactions.c` but the origin table itself is not persistent.

Dependencies and integration: depends on `avl`, global debug logging from `ids.h`, audit response logging, config weights, and reaction unblocking. Event models use `current_origin` after lookups/scoring.

Risks: address handling is IPv4-only and byte-order-sensitive; unknown addresses may collapse into `255.255.255.255` or zero-like values depending caller behavior. `sockint_to_ipv4` returns a static buffer. AVL comparator subtracts unsigned addresses through signed int return, which can overflow ordering for far-apart values.

Test signals: add/find/delete duplicates, score increments, audit anomaly logging inputs, dotted conversion round trips, and timed unblock behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/origin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/origin.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/origin.h

Purpose: declares origin tracking structures and APIs.

Important APIs and data: `origin_data_t` embeds `avl_t` first, then `address`, `karma`, and `blocked`. Functions expose lifecycle, lookup, scoring, anomaly helpers, and IPv4 conversions.

Control flow: none in header; callers interact with global origin table in the implementation.

State and persistence: header exposes process-memory fields but no persistence.

Dependencies and integration: includes `avl.h` and `ids_config.h`; used by models, sessions, reactions, and timer services.

Risks: public struct fields allow direct mutation without preserving current-origin semantics. Address type documents an IPv4 hack and should not be assumed to support IPv6.

Test signals: integration tests should verify origin current pointer behavior after `find_origin`, `add_origin`, and scoring.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/origin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/reactions.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/reactions.c

Purpose: executes IDS responses such as killing sessions, changing account state, blocking IPs, scheduling timed undo work, and changing runlevel.

Important APIs and data: implements process/session kill, SELinux role restriction, password reset, account lock/unlock, IP block/unblock, system reboot/single/halt, timed wrappers, and `do_reaction`. Local `safe_exec` forks and execs fixed tools with sanitized file descriptors.

Control flow: `do_reaction` iterates all 32 possible reaction bits and dispatches each set bit. Account reactions use `current_session()->acct`; address reactions use `current_origin()` and mark the origin blocked after firewall success. Timed account/address actions schedule jobs through timer services.

State and persistence: mutates external system state: processes, login/account database, SELinux login mapping, iptables/nftables rules, and runlevel. It also updates process-local origin blocked state and timer queue.

Dependencies and integration: depends on global `config`, current session/origin, `account.h`, timer services, audit response logging, syslog, password database, `/etc/login.defs`, and external binaries including `killall`, `semanage`, `chage`, `passwd`, `iptables`/`nft`, and `init`.

Risks: reactions are high-impact and many are irreversible or system-disruptive. `do_reaction` does not null-check current session before `kill_session(s->session)`. `verify_acct` rejects daemon/system accounts but depends on parsing UID_MIN. Firewall unblock must match the exact rule insertion form.

Test signals: unit tests should mock `safe_exec` and current session/origin; integration tests should isolate account/firewall side effects. Timed block/unblock paths are covered only through timer services behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/reactions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/reactions.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/reactions.h

Purpose: declares executable IDS reaction functions.

Important APIs and data: exposes individual process, session, account, address, and system reaction calls plus `do_reaction(unsigned int answer, const char *reason)`.

Control flow: no header flow; `do_reaction` interprets `REACTION_*` bitmasks.

State and persistence: declared functions may mutate OS state, firewall state, accounts, and process-local IDS state.

Dependencies and integration: consumers must include a `pid_t` definition before using `kill_process`; implementation integrates with `ids_config.h` constants.

Risks: signatures do not communicate side-effect severity or required privileges.

Test signals: compile-time coverage and mocked reaction dispatch by bitmask.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/reactions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-connections.rules -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-connections.rules

Purpose: installs audit rules that tag execution of common network/data movement tools with `ids-connections`.

Important APIs and data: rule lines watch executable paths such as curl, ftp, git, rsync, scp, sftp, ssh, wget, telnet, nc/ncat, nmap/nping, and ping with `auid>=1000`, `auid!=-1`, `perm=x`, and key `ids-connections`.

Control flow: auditd evaluates rules on execution; matching events later reach `model_behavior.c`, which adds six points to the session for `ids-connections`.

State and persistence: rules are installed under the audit rules directory by the IDS rules Makefile; active audit kernel state persists until rules are reloaded.

Dependencies and integration: depends on executable paths existing at `/usr/bin/...` and on behavior model key matching.

Risks: path-specific rules miss alternate locations and may fail if tools are absent. Network tools are legitimate for many users, so scoring can create false positives.

Test signals: `auditctl` rule loading and execution of watched binaries should produce events with key `ids-connections`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-connections.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-make-exec.rules -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-make-exec.rules

Purpose: tags chmod-style operations that create executable files in writable or user-controlled directories.

Important APIs and data: b64 syscall rules cover `chmod`, `fchmod`, and `fchmodat` in `/home`, `/tmp`, `/var/tmp`, and `/dev/shm`, checking execute bits via `a1&0111` or `a2&0111`, `filetype=file`, user auid filters, and key `ids-mkexec`.

Control flow: kernel audit emits matching syscall records; `model_behavior.c` maps `ids-mkexec` to a four-point session score increase.

State and persistence: installed as persistent audit rules when included in audit rule deployment.

Dependencies and integration: architecture-specific to b64 syscalls and behavior model key names.

Risks: lacks b32 coverage and misses executable creation paths not using these syscalls. It may flag legitimate build or install activity under user directories.

Test signals: chmod/fchmodat executable bit changes in the watched directories should emit `ids-mkexec` events.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-make-exec.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-recon.rules -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-recon.rules

Purpose: tags execution of common reconnaissance and system-discovery utilities with `ids-recon`.

Important APIs and data: watches tools such as uname, rpm/yum/dnf, w/who/whoami, netstat/ss/route/ifconfig/ip, mount, lsof, df, dig/host, last/lastlog, getent, history, watch, and sestatus for user audit IDs.

Control flow: matching audit records are scored by `model_behavior.c` as low-weight reconnaissance signals.

State and persistence: audit rules become kernel audit policy after installation.

Dependencies and integration: depends on path-specific binary locations and the key string `ids-recon`.

Risks: reconnaissance tools are also normal admin tools, and some paths may be distribution-specific or missing. The commented `id` rule shows deliberate tuning to reduce noise.

Test signals: executing watched binaries as a non-daemon audited user should produce `ids-recon` keyed records and a two-point session score.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-recon.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-unpacking.rules -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-unpacking.rules

Purpose: tags archive pack/unpack utilities as potential staging behavior.

Important APIs and data: watches unzip, tar, bunzip, zipgrep, gzip, gunzip, zcat, zgrep, and zless with `perm=x`, user auid filters, and key `ids-archive`.

Control flow: behavior model maps `ids-archive` to a five-point session score increase.

State and persistence: persistent only as installed audit rules.

Dependencies and integration: keyed to behavior model string matching and specific `/usr/bin` paths.

Risks: normal file handling can trigger the same key, so thresholds must account for expected user activity.

Test signals: execution of watched archive tools should create `ids-archive` events that are visible to audisp-ids.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-unpacking.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/Makefile.am -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/Makefile.am

Purpose: packages the IDS audit rule files for installation.

Important APIs and data: sets `EXTRA_DIST` and `dist_rules_DATA` to the four `25-*.rules` files; installs them under `$(datadir)/audit-rules/ids-rules`.

Control flow: automake uses these variables during dist and install targets.

State and persistence: no runtime state; controls distribution/install artifacts.

Dependencies and integration: integrates with the audit userspace build system and rule deployment location.

Risks: adding a new rule file without updating `EXTRA_DIST` leaves it out of packaged installs.

Test signals: `make distcheck` and install tree inspection should verify all four rules are present.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/session.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/session.c

Purpose: tracks active audit login sessions, their scores, origin address, kill flag, and account name.

Important APIs and data: exports lifecycle, traversal, add/find/delete/current access, and `add_to_score_session`. Sessions are stored in a global AVL tree keyed by session id.

Control flow: `new_session` allocates and initializes a session, then `add_session` inserts it, creates missing origin/account entries, and updates `cur`. Deletion removes the AVL entry and frees the account string. Scoring updates `cur` and increments score.

State and persistence: global process-local AVL tree and current pointer only. Session state is destroyed on logout, system lifecycle events, or process exit.

Dependencies and integration: uses `origin.c` to associate sessions with origins, `account.c` to track accounts, and model files for scoring.

Risks: `new_session` stores `acct ? acct : strdup("")`; when `acct` is NULL this can assign a newly allocated string, but when non-NULL it assumes ownership of a pointer created by the caller. `dump_session` prints `s->acct` directly and would be unsafe if NULL.

Test signals: create/find/delete duplicate sessions, account/origin side effects, and score threshold interactions through behavior model.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/session.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/session.h

Purpose: declares session tracking data and APIs.

Important APIs and data: `session_data_t` embeds `avl_t` first, then `session`, `score`, `killed`, `origin`, and `acct`. Functions expose lifecycle, lookup, current pointer, deletion, traversal, and score changes.

Control flow: no implementation in header.

State and persistence: describes process-local session state only.

Dependencies and integration: includes `avl.h`, `origin.h`, and `ids_config.h`; used by models and reactions.

Risks: public fields can be mutated without maintaining AVL/current invariants. `origin` is IPv4-only by design.

Test signals: compile-time inclusion and integration tests around session lifecycle.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/timer-services.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/timer-services.c

Purpose: schedules and executes delayed IDS undo operations, currently account unlock and IP unblock.

Important APIs and data: implements `init_timer_services`, `do_timer_services`, `add_timer_job`, and `shutdown_timer_services`. Uses a static `nvlist jobs` and monotonic-ish static `now`.

Control flow: initialization creates the list and captures current time. Each service tick handles dump/reload signals, advances `now` by the caller interval with drift correction, then repeatedly finds expired jobs and runs the matching reaction before deleting the job. New jobs store `time(NULL) + length`.

State and persistence: timer jobs are in memory only; a comment notes they should probably be persistent to survive restart.

Dependencies and integration: depends on `nvpair.c`, `reactions.c`, `origin.c`, audit response logging, global signal flags, and IDS output/reload functions.

Risks: delayed undo is lost on process restart, so timed locks/blocks can remain active externally. The internal clock is adjusted by interval and corrected only when drift exceeds the interval.

Test signals: schedule unlock/unblock jobs, advance service intervals, verify action execution and deletion. Restart persistence is explicitly absent.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/timer-services.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/timer-services.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/ids/timer-services.h

Purpose: declares delayed timer services for IDS reactions.

Important APIs and data: defines `jobs_t` enum values `UNLOCK_ACCOUNT` and `UNBLOCK_ADDRESS`; declares init, tick, add, and shutdown functions.

Control flow: no implementation; caller must invoke `do_timer_services` periodically.

State and persistence: describes in-memory timer queue behavior only.

Dependencies and integration: used by timed reaction functions and `nvpair.h`.

Risks: adding a new timed reaction requires updating the enum and the switch in `do_timer_services`.

Test signals: compile-time enum consumers and timed reaction integration.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/timer-services.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/Makefile.am -->
# sources/security-integrity/audit-userspace/audisp/plugins/remote/Makefile.am

Purpose: builds and installs the `audisp-remote` plugin, its configs, man pages, headers, and queue tests.

Important APIs and data: defines `sbin_PROGRAMS = audisp-remote`, `check_PROGRAMS = test-queue`, source lists for the daemon and test, installed config paths, PIE/RELRO flags, and dependencies on libaudit, aucommon, auplugin, optional GSS libs, and cap-ng.

Control flow: automake install hooks create `/etc/audit` and `/etc/audit/plugins.d` targets with mode 0640 config files; uninstall removes them.

State and persistence: no runtime state, but build choices enable persistent queue and remote transport code.

Dependencies and integration: connects source files `audisp-remote.c`, `remote-config.c`, and `queue.c` to the audit userspace build and test system.

Risks: path/install mode assumptions matter for later config permission checks. Missing optional GSS or ASAN flags changes compiled behavior.

Test signals: `make check` runs `test-queue`; install verification should check config locations and modes.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/au-remote.conf -->
# sources/security-integrity/audit-userspace/audisp/plugins/remote/au-remote.conf

Purpose: audisp plugin registration file for the remote audit event logger.

Important APIs and data: sets `active = no`, `path = /sbin/audisp-remote`, `type = always`, and `format = string`.

Control flow: audit dispatcher reads this to decide whether and how to launch `audisp-remote`.

State and persistence: installed under audit plugin config and persists until changed by administrator.

Dependencies and integration: points dispatcher output to the remote plugin, whose own settings are in `audisp-remote.conf`.

Risks: disabled by default; enabling without a valid remote config can stall or stop remote logging depending failure actions.

Test signals: dispatcher config parsing and plugin activation tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/au-remote.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/audisp-remote.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/remote/audisp-remote.c

Purpose: implements the remote audit dispatcher plugin that queues audit records and forwards them to a central logger over TCP or Kerberos/GSSAPI.

Important APIs and data: main daemon state includes signal flags, socket state, `remote_conf_t config`, persistent/in-memory queue, and max queue depth tracking. Key paths are `init_queue`, `send_one`, `relay_event`, `relay_sock_managed`, `relay_sock_ascii`, `init_transport`, `stop_transport`, `check_message`, and failure-action handlers.

Control flow: main loads `/etc/audit/audisp-remote.conf`, initializes queue, optionally drops capabilities, and enters a `select` loop over stdin and remote socket. Incoming audit lines are stripped of EOE records, appended to the queue, and sent when the socket is writable. Managed format sends headers, waits for matching ACK/status response, retries within configured count/time limits, and handles remote disk/ending/errors. ASCII format writes raw records without ACK protocol.

State and persistence: immediate mode uses memory queue only; store-and-forward uses `queue.c` file storage under configured `queue_file` or `/var/spool/audit/remote.log`. Signal state supports SIGHUP reload, SIGUSR1 state dump to `remote.state`, SIGUSR2 resume, SIGTERM from parent only, and SIGCHLD reaping.

Dependencies and integration: depends on auplugin input, libaudit remote managed wire macros, `remote-config.c`, `queue.c`, syslog, optional cap-ng, optional GSSAPI/Kerberos, and runlevel changes for severe actions.

Risks: failure actions can suspend logging, stop the plugin, switch runlevel, or halt the host. Managed mode correctness relies on sequence numbers and sync recovery. GSS keytab permission checks are strict. Store-and-forward durability depends on queue file semantics and does not sync each entry unless queue flags change.

Test signals: `test-queue` covers queue mechanics; protocol tests should simulate ACKs, remote disk low/full/error, ending messages, retry exhaustion, heartbeat, SIGHUP, overflow, and store-forward restart.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/audisp-remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/audisp-remote.conf -->
# sources/security-integrity/audit-userspace/audisp/plugins/remote/audisp-remote.conf

Purpose: default configuration for remote audit logging.

Important APIs and data: includes remote server/port, transport, queue file/depth, mode, format, retry/heartbeat parameters, failure actions, overflow action, startup action, and optional Kerberos principal/client/key file entries.

Control flow: parsed by `remote-config.c`; `audisp-remote.c` uses the values to select queue mode, transport, retry behavior, and response to errors.

State and persistence: installed under `/etc/audit`, root-owned mode 0640 by the Makefile; values persist across daemon restarts.

Dependencies and integration: must be valid before enabling `au-remote.conf`. `mode = forward` only works with `format = managed`.

Risks: `remote_server` is blank by default, so enabled deployments require administrator configuration. Actions like `stop`, `suspend`, `single`, and `halt` are operationally significant.

Test signals: config parser tests for every option, action keyword, invalid combinations, and GSS-disabled builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/audisp-remote.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/queue.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/remote/queue.c

Purpose: implements a fixed-size string queue with optional in-memory cache, persistent file storage, locking, and resize support.

Important APIs and data: exports `q_open`, `q_close`, `q_append`, `q_peek`, `q_drop_head`, and `q_queue_length`. Persistent files contain a binary header with magic, version, entry count, entry size, queue head, and queue length in network byte order.

Control flow: `q_open` validates flags and sizes, initializes memory cache, opens or creates/validates the file, and performs resize by copying entries into a temporary queue then renaming. Append writes the tail entry and syncs header state; peek returns head from memory or file and drops corrupt unterminated entries; drop advances the circular head and syncs.

State and persistence: memory queue state is volatile; file queue state persists across restart and is protected by `lockf` process locking. Queue entries are fixed-size slots, with string payloads including trailing NUL.

Dependencies and integration: used by `audisp-remote.c` for remote spool. Depends on POSIX file I/O, optional `posix_fallocate`, syslog, and queue constants in `queue.h`.

Risks: `fdatasync` is only used when `Q_SYNC` is set; store-forward path does not set it by default, leaving crash windows. Persistent file format rejects entry-size changes and corrupt headers. The recursive corrupt-entry skip in `q_peek` could recurse through many bad entries.

Test signals: `test-queue.c` covers open flags, locking, empty behavior, data size limits, wraparound, reopen persistence, and resizing.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/queue.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/remote/queue.h

Purpose: declares the audisp-remote queue abstraction and storage flags.

Important APIs and data: opaque `struct queue`; flags `Q_IN_MEMORY`, `Q_IN_FILE`, `Q_CREAT`, `Q_EXCL`, `Q_SYNC`, and `Q_RESIZE`; `QUEUE_ENTRY_SIZE` is 3*4096; public open/close/append/peek/drop/length functions.

Control flow: callers configure storage and durability behavior via flags at `q_open`.

State and persistence: file-backed queues persist when `Q_IN_FILE` is set; memory-only queues do not.

Dependencies and integration: includes common attribute macros and is used by `audisp-remote.c` and `test-queue.c`.

Risks: comments say `q_peek` returns 1 for an entry, but implementation returns the entry byte length; callers should treat positive values as length.

Test signals: `test-queue.c` validates the public API contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/remote-config.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/remote/remote-config.c

Purpose: parses and validates `audisp-remote.conf` into `remote_conf_t`.

Important APIs and data: exports `clear_config`, `load_config`, and `free_config`. Parser tables cover server, ports, transport, mode, queue file/depth, format, retry/heartbeat values, GSS options, failure actions, remote ending action, overflow action, and startup failure action.

Control flow: `load_config` sets defaults, verifies the config file is root-owned, regular, and not world-writable, then parses `name = value [option]` tokens. Parser callbacks convert enums, duplicate string fields, check absolute queue paths, validate executable action paths and permissions, and perform final sanity checks.

State and persistence: dynamically allocated strings are stored in the caller-owned config and freed by `free_config`. No state persists beyond config files and process memory.

Dependencies and integration: consumed by `audisp-remote.c`; optional GSS options compile differently under `USE_GSSAPI`. Exec failure actions require root-owned 0750 absolute executables.

Risks: tokenization is whitespace-only and does not support quoted values. `remote_server` is not required by sanity check despite being needed for connection. Some enum values exist in the header but are not accepted by parser tables.

Test signals: parser tests should cover defaults, permission failures, every enum value, exec option validation, queue_file absoluteness, GSS disabled behavior, and `mode=forward` with non-managed format.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/remote-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/remote-config.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/remote/remote-config.h

Purpose: declares remote plugin configuration enums and structure.

Important APIs and data: defines modes, transports, formats, failure actions, overflow actions, and `remote_conf_t` fields for endpoint, queue, retry, heartbeat, Kerberos, and action executables.

Control flow: no implementation; enums drive parser and runtime switch statements.

State and persistence: structure holds process-local parsed config with heap-owned strings.

Dependencies and integration: used by both parser and remote daemon. Kerberos principal is mutable because GSS setup rewrites slash to `@`.

Risks: enum values such as TLS/labeled transport are declared but not implemented by current transport initialization. Ownership of `const char *` fields is mixed but freed by `free_config`.

Test signals: compile-time coverage and parser/runtime switch tests for each enum.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/remote-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/test-queue.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/remote/test-queue.c

Purpose: exercises the persistent queue implementation used by audisp-remote.

Important APIs and data: uses `q_open`, `q_append`, `q_peek`, `q_drop_head`, `q_queue_length`, and `q_close` with `NUM_ENTRIES = 7` and `ENTRY_SIZE = 12288`. Generates random NUL-terminated sample entries.

Control flow: tests open flags and locking, empty queue behavior, basic append/peek/drop, maximum entry size rejection, wraparound, reopen persistence for file queues, memory-only non-persistence, and queue resizing up/down constraints.

State and persistence: creates a temporary `/tmp/tqXXXXXX` file and removes it after each file-backed test.

Dependencies and integration: wired into `make check` by remote `Makefile.am`.

Risks: uses random sample contents but not a fixed seed, though comparisons are self-contained. It does not simulate corrupt persistent files or crash windows.

Test signals: this file is the direct automated test signal for `queue.c`; failures abort with line-numbered messages.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/remote/test-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/statsd/Makefile.am -->
# sources/security-integrity/audit-userspace/audisp/plugins/statsd/Makefile.am

Purpose: builds and installs the `audisp-statsd` plugin and configs.

Important APIs and data: defines source `audisp-statsd.c`, plugin/program configs, man page, include paths, libaudit/auparse/aucommon/auplugin dependencies, and optional cap-ng linkage.

Control flow: automake install hook places plugin registration and program config with mode 0640.

State and persistence: no runtime state; controls installed plugin artifacts.

Dependencies and integration: integrates statsd plugin with audit userspace build and dispatcher configuration.

Risks: missing dependency updates can break plugin build or install. Config file mode/location must match runtime expectations.

Test signals: build/install checks and eventual plugin runtime tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/statsd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/statsd/au-statsd.conf -->
# sources/security-integrity/audit-userspace/audisp/plugins/statsd/au-statsd.conf

Purpose: dispatcher registration for the statsd audit metrics plugin.

Important APIs and data: disabled by default, path `/sbin/audisp-statsd`, type `always`, string format.

Control flow: audit dispatcher launches the plugin when active.

State and persistence: persistent admin config under plugins.d.

Dependencies and integration: requires `audisp-statsd.conf` for destination address, port, and interval.

Risks: disabled default prevents metrics until explicitly enabled; wrong path breaks plugin startup.

Test signals: dispatcher config parsing and activation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/statsd/au-statsd.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/statsd/audisp-statsd.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/statsd/audisp-statsd.c

Purpose: collects audit daemon/kernel status plus event counters and emits statsd metrics over UDP.

Important APIs and data: local config holds address, port, interval, socket, and resolved sockaddr. Report struct tracks kernel backlog/lost, auditd state report gauges, memory stats, and event counters. Key functions include `load_config`, `make_socket`, `get_kernel_status`, `get_auditd_status`, `send_statsd`, `statsd_timer`, `main`, and `handle_event`.

Control flow: main requires root, loads config, opens UDP socket, drops to CAP_AUDIT_CONTROL when available, opens audit netlink, initializes auplugin queue, and feeds events with a periodic timer. The timer gathers kernel and auditd state, sends one UDP statsd packet, and clears counters. Event handler increments counters by auparse-normalized result and first record type.

State and persistence: all counters are in memory and reset after each interval. Reads auditd state from `AUDIT_RUN_DIR/auditd.state`; emits no local persistent state.

Dependencies and integration: depends on libaudit status requests, auparse normalization, auplugin event feed, common time parser, and a statsd UDP endpoint.

Risks: config parser is simple first-character dispatch and requires all options. UDP send is best effort. Stats packet is capped at 512 bytes; additions risk truncation. Auditd state parsing depends on exact text labels.

Test signals: simulate config parsing, event types, timer flush, kernel status failures, and state-report parsing. No direct tests are present here.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/statsd/audisp-statsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/statsd/audisp-statsd.conf -->
# sources/security-integrity/audit-userspace/audisp/plugins/statsd/audisp-statsd.conf

Purpose: configures the statsd destination and report interval.

Important APIs and data: default `address = localhost`, `port = 8125`, and `interval = 15s`; comments document accepted time suffixes.

Control flow: parsed by `audisp-statsd.c` and converted into UDP socket target plus timer interval.

State and persistence: persistent local config under `/etc/audit`.

Dependencies and integration: depends on `time_string_to_seconds` syntax for interval and DNS/address resolution for address.

Risks: parser requires all three settings and does not support quoting or inline comments after values.

Test signals: parser tests for valid suffixes, missing keys, unknown options, and invalid intervals.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/statsd/audisp-statsd.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/syslog/Makefile.am -->
# sources/security-integrity/audit-userspace/audisp/plugins/syslog/Makefile.am

Purpose: builds and installs the `audisp-syslog` plugin and plugin config.

Important APIs and data: defines `audisp_syslog_SOURCES = audisp-syslog.c`, PIE/RELRO flags, libaudit/auparse/auplugin dependencies, installed `syslog.conf`, and man page.

Control flow: automake install hook creates plugins.d and installs config with mode 0640.

State and persistence: build/install metadata only.

Dependencies and integration: integrates syslog plugin with audit dispatcher and build system.

Risks: command-line args are supplied by config, so packaging must keep config and binary behavior aligned.

Test signals: build/install checks and dispatcher startup tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/syslog/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/syslog/audisp-syslog.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/syslog/audisp-syslog.c

Purpose: reads audit records from audisp stdin and writes them to syslog, optionally interpreting fields through auparse.

Important APIs and data: local state includes stop/hup flags, syslog priority, interpret mode, and reusable record buffer. Key functions are `init_syslog`, `write_syslog`, and `main`.

Control flow: command-line args select syslog priority, facility, and optional `interpret`. Main installs signal handlers, drops capabilities, then waits on stdin with `select` and drains auplugin lines. Non-interpreted mode replaces the audit interpretation separator with a space and syslogs raw text. Interpreted mode creates an auparse buffer, drops EOE-like empty records, formats interpreted `name=value` fields, and adds a human-readable timestamp header.

State and persistence: only in-memory buffer and flags; output persistence is delegated to syslog.

Dependencies and integration: depends on auplugin line input, auparse interpretation helpers, libaudit constants, syslog facilities, and dispatcher `syslog.conf` args.

Risks: interpreted formatting truncates when near `MAX_AUDIT_MESSAGE_LENGTH - 128`. `reload_config` only clears hup and does not reread args. Signal termination honors only parent SIGTERM.

Test signals: feed raw and interpreted audit records, EOE records, unknown args, facility/priority args, HUP/TERM behavior, and separator replacement.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/syslog/audisp-syslog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/syslog/syslog.conf -->
# sources/security-integrity/audit-userspace/audisp/plugins/syslog/syslog.conf

Purpose: dispatcher registration for forwarding audit events to syslog.

Important APIs and data: disabled by default, path `/sbin/audisp-syslog`, type `always`, args `LOG_INFO`, and string format. Comments document valid priority/facility arguments and optional behavior.

Control flow: audit dispatcher passes args to `audisp-syslog`, which parses them in `init_syslog`.

State and persistence: persistent plugin configuration.

Dependencies and integration: relies on syslog plugin accepting the configured priority token.

Risks: disabled by default; invalid args cause plugin startup failure.

Test signals: dispatcher config parse and syslog plugin arg parsing.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/syslog/syslog.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/Makefile.am -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/Makefile.am

Purpose: builds and installs the z/OS remote audit dispatcher plugin.

Important APIs and data: defines `audispd-zos-remote` sources (`zos-remote-plugin.c`, log, LDAP, config, queue), headers, LDAP/LBER/pthread dependencies, PIE/RELRO flags, and config files `zos-remote.conf` and `audispd-zos-remote.conf`.

Control flow: install hook creates `/etc/audit` and plugins.d destinations and installs both configs with mode 0640.

State and persistence: build/install metadata; runtime queue/config state lives in other zOS plugin files.

Dependencies and integration: integrates with auparse and LDAP libraries; dispatcher registration points to this binary with config path arg.

Risks: this subset does not include the main plugin/queue source, so behavior research here depends on referenced files. LDAP library availability controls build.

Test signals: build/link tests and install artifact checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/audispd-zos-remote.conf -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/audispd-zos-remote.conf

Purpose: dispatcher registration for the z/OS remote audit plugin.

Important APIs and data: disabled by default, path `/sbin/audispd-zos-remote`, type `always`, args `/etc/audit/zos-remote.conf`, and string format.

Control flow: dispatcher launches the plugin and passes the zOS-specific config path as an argument.

State and persistence: persistent plugin config under plugins.d.

Dependencies and integration: depends on installed `zos-remote.conf` and the zOS plugin binary.

Risks: enabling without valid LDAP/RACF config will fail startup or event submission.

Test signals: dispatcher config parse and startup with missing/valid args.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/audispd-zos-remote.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-config.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-config.c

Purpose: parses the z/OS remote plugin's LDAP/RACF configuration file.

Important APIs and data: exports `plugin_clear_config`, `plugin_load_config`, and `plugin_free_config`. Supported keywords are `server`, `port`, `timeout`, `user`, `password`, and `q_depth`.

Control flow: loader resets defaults, opens the provided file, verifies root ownership, exact 0640-style permissions, and regular-file status, parses whitespace-delimited `name = value`, dispatches keyword parsers, records basename as config name, then runs sanity checks for required server/user/password and nonzero timeout.

State and persistence: heap-owned strings are stored in `plugin_conf_t` and freed by `plugin_free_config`. Config values are process-local after load.

Dependencies and integration: used by the zOS plugin main path and `zos-remote-ldap.c`. Logging goes through `zos-remote-log.c`.

Risks: `port` is not range-checked; `server`, `user`, and `password` are unquoted single tokens only. Permission check requires the root read/write and group read bits but does not explicitly reject all extra bits as the comment suggests.

Test signals: tests should cover missing file, bad owner/mode/type, required-field failures, q_depth range, zero timeout, and token parse errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-config.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-config.h

Purpose: declares z/OS remote plugin configuration structure and lifecycle functions.

Important APIs and data: `plugin_conf_t` includes config filename, server, port, user, password, timeout, queue depth, and a counter. Declares clear/load/free functions.

Control flow: no implementation; loaded values drive plugin startup and LDAP session initialization.

State and persistence: holds process-local config with heap-owned string fields.

Dependencies and integration: consumed by the zOS remote plugin and LDAP wrapper.

Risks: password is stored in process memory as plain text. `counter` is not reset by clear according to implementation comment, so callers need to understand its lifecycle.

Test signals: parser and plugin startup tests validating field propagation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-ldap.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-ldap.c

Purpose: implements LDAP extended-operation submission to z/OS Remote-services for audit events.

Important APIs and data: exports `zos_remote_init`, `zos_remote_destroy`, `submit_request_s`, and `zos_remote_err2string`. Internal response structs capture overall and per-item major/minor codes. The core send path is `submit_xop_s`, with BER decoding in `decode_response`.

Control flow: initialization duplicates connection settings, creates an LDAP handle, and ensures LDAPv3. Submission flattens a BER request, connects/binds if necessary, sends the ICTX audit request extended operation, waits with configured timeout, validates the LDAP result and response OID, decodes BER response, logs per-item warnings/errors, and retries once on retryable connection failure.

State and persistence: `ZOS_REMOTE` stores server/user/password, LDAP handle, timeout, and connected flag. No disk persistence; connection state is recreated on retry or destroy.

Dependencies and integration: depends on OpenLDAP/liblber, OIDs and constants from `zos-remote-ldap.h`, config from `zos-remote-config.c`, and logging/debug helpers. It is called by the zOS plugin event submission thread.

Risks: LDAP simple bind uses plaintext password unless protected externally. Response allocation paths are complex; a `realloc` failure check uses `errno` rather than the returned pointer. Deprecated LDAP path contains a likely missing comma in `ldap_init` call under `LDAP_DEPRECATED`.

Test signals: LDAP integration tests should cover bind success/failure, timeout, server-down retry, bad OID, invalid BER version, per-item major code logging, and memory cleanup on errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-ldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-ldap.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-ldap.h

Purpose: declares the z/OS Remote-services LDAP wire contract, constants, return codes, session struct, and API.

Important APIs and data: defines audit request/response OIDs, request version, ASN.1 tag constants, event and qualifier codes, relocation field constants, z/OS major response codes, standard field sizes, ICTX error codes, `ZOS_REMOTE`, and LDAP submit/init/destroy APIs.

Control flow: no implementation; comments document the ASN.1 request/response structures and meaning of major/minor codes.

State and persistence: `ZOS_REMOTE` holds mutable connection/session state and plaintext credentials in memory.

Dependencies and integration: includes `lber.h` and `ldap.h`; consumed by LDAP implementation, logging helpers, and zOS plugin code that builds BER requests.

Risks: constants are protocol contracts; changing them breaks compatibility with z/OS Remote-services. Typo in "Reguestor" comment is harmless but field meanings must remain exact.

Test signals: compile tests plus BER construction/decoding tests against expected OIDs, version, field sizes, and return-code mapping.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-ldap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-log.c -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-log.c

Purpose: centralizes z/OS remote plugin syslog logging and optional BER debug dumps.

Important APIs and data: implements `log_err`, `log_warn`, `log_info`, `_log_debug`, `_debug_ber`, and `_debug_bv`. `vlog_prio` prefixes messages with `pid=<mypid>`.

Control flow: variadic public log functions delegate to `vlog_prio`. Debug BER helpers flatten BER or iterate berval bytes into a hex dump and log it through debug logging.

State and persistence: no owned persistent state; uses external `mypid` and syslog.

Dependencies and integration: depends on `zos-remote-log.h`, auparse/lber BER types, and syslog. Debug macros in the header compile debug calls away unless `DEBUG` is defined.

Risks: `_debug_bv` calls `log_debug(out)` with the hex string as a format string, so percent bytes in debug output would be interpreted if present; hex output only uses digits/spaces in current construction. `asprintf` failures drop log messages silently.

Test signals: debug-enabled builds should verify prefixing and BER hex output; non-debug builds should compile out debug macros.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-log.h -->
# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-log.h

Purpose: declares z/OS remote logging helpers and debug macros.

Important APIs and data: declares external `pid_t mypid`, log functions, debug BER functions, and `DEBUG`-controlled macros `log_debug`, `debug_bv`, and `debug_ber`.

Control flow: macro control either routes debug calls to real functions or removes them.

State and persistence: relies on process-global `mypid`; no local state.

Dependencies and integration: includes zOS LDAP types, syslog, unistd, and lber, so consumers get BER type declarations.

Risks: including `zos-remote-ldap.h` here creates a broad dependency from logging to LDAP headers. Debug macros with empty replacement can hide side effects in arguments if callers rely on them.

Test signals: compile with and without `DEBUG`, and verify callers define `mypid`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-log.h -->
