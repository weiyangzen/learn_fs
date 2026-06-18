# subset-b-008303 Research

Work item `subset-b-008303` covers the audit userspace `aureport`/`ausearch` event assembly, parsing, matching, formatting, checkpoint, and small container modules under `sources/security-integrity/audit-userspace/src`.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-scan.c -->
## sources/security-integrity/audit-userspace/src/aureport-scan.c

Purpose: implements the event classification and accumulation path for `aureport`. `scan()` calls `extract_search_items()` on an assembled `llist`, filters by node, success, and config action, then `per_event_processing()` dispatches to summary or detailed reporting based on globals from `aureport-options.h`.

Important APIs/functions: `reset_counters()` initializes global `summary_data sd`; `destroy_counters()` releases its string and integer lists; `scan()` is the report-side match gate; `per_event_summary()` aggregates by report type; `per_event_detailed()` emits matching events through `print_per_event_item()`; `do_summary_total()` updates cross-report totals. Helper classifiers include `classify_success()`, `classify_conf()`, `aggregate_anom_item()`, `aggregate_resp_item()`, and `aggregate_crypto_item()`.

Control flow: `aureport.c` assembles a complete audit event, loads interpretations for single/SYSCALL events, then calls `scan()` and `per_event_processing()`. Summary mode adds unique users, files, hosts, terminals, keys, pids, syscall names, AVC objects, anomaly classes, crypto classes, virtualization, integrity, and MAC records into `sd`. Detailed mode checks the requested report class and calls the output layer for each matching event.

State/persistence: all state is in process memory, primarily `sd`; no file persistence. List members are owned by `sd` and released at shutdown. The function relies heavily on global filters such as `event_failed`, `event_conf_act`, `event_node_list`, `report_type`, and `report_detail`.

Dependencies/integration: depends on `ausearch-parse.c` for field extraction, `ausearch-llist.h` event structures, `ausearch-string.c`/`ausearch-int.c` containers, `ausearch-lookup.c` for uid/syscall names, `libaudit` message constants, and output functions declared elsewhere.

Risks: `destroy_counters()` calls `ilist_create()` instead of `ilist_clear()` for several lists (`mac_list`, `crypto_list`, `virt_list`, `integ_list`), which looks like a leak/reset bug. Many branches assume `l->head` and parsed sublists exist after `scan()`. Summary counts use `l->head->type` after `list_find_msg_range()` changes `cur`, so type attribution can be first-record-biased. Test signals should cover every `report_type`, success/config filters, node filters, list cleanup under repeated runs, and malformed events from fuzzed audit logs.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-scan.h -->
## sources/security-integrity/audit-userspace/src/aureport-scan.h

Purpose: declares the report scanner contract used by `aureport.c` and report output code. It defines the global aggregation structure for summary report production.

Important APIs/types: `summary_data` owns many `slist` and `ilist` accumulators plus scalar counters for config changes, crypto, account changes, logins, auth, events, AVCs, MAC, failed syscalls, anomalies, responses, virtualization, and integrity. Public functions are `reset_counters()`, `destroy_counters()`, `scan()`, `per_event_processing()`, `print_title()`, `print_per_event_item()`, and `print_wrap_up()`. It exports `summary_data sd`.

Control flow: callers initialize `sd` once, feed each parsed event through `scan()` and `per_event_processing()`, then call output wrap-up after all logs are processed.

State/persistence: exposes a process-global mutable `sd`; no persistence. Ownership of strings stored in its lists is managed by the scanner/list modules.

Dependencies/integration: includes `ausearch-llist.h` for event lists and `ausearch-int.h`, which indirectly relies on string lists through the included llist header.

Risks/test signals: because `sd` is global, tests must reset/destroy it between cases. ABI-sensitive changes to `summary_data` affect report output modules. Tests should validate initialization, cleanup, and that all list fields remain consistent after empty and populated reports.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport-scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport.c -->
## sources/security-integrity/audit-userspace/src/aureport.c

Purpose: main program for `aureport`. It parses report options, locates audit logs or stdin/input files, assembles records into complete audit events, runs report scanning, and prints titles/wrap-up output.

Important APIs/functions: `main()` owns setup and teardown; `process_logs()` enumerates rotated logs using `audit_log_list()` and `audit_log_find_start()`; `process_file()` and `process_stdin()` set `log_fd`; `process_log_fd()` loops over events; `get_event()` feeds raw lines to `lol_add_record()` and pulls ready `llist` events; `process_event()` calls `scan()` and `per_event_processing()`.

Control flow: after `check_params()`, it raises file/cpu limits, loads auditd config, applies `end_of_event_timeout`, initializes `auparse`, counters, and the list-of-lists event assembler. It chooses directory, regular file, stdin pipe, forced logs, or configured logs. For each complete event in time range it scans and accumulates or emits. On EOF of the last file, `terminate_all_events()` flushes incomplete events.

State/persistence: process state includes `log_fd`, `lol lo`, `found`, `files_to_process`, `very_first_event`, `very_last_event`, `config`, and a static `auparse_state_t *au`. No persistent writes. It frees counters, lookup caches, config, and `user_file`.

Dependencies/integration: integrates `aureport-options`, `aureport-scan`, `ausearch-lol`, `ausearch-parse` log enumeration, `auditd-config`, `libaudit`, and internal `auparse` interpretation helpers.

Risks/test signals: rotated log traversal depends on first timestamps and descending numeric suffixes. Error handling around `auparse_init()` and config fallback should be covered. Tests should exercise stdin, directory input, missing logs, time range skipping, last-file incomplete event flushing, and report type `RPT_TIME`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/aureport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-avc.c -->
## sources/security-integrity/audit-userspace/src/ausearch-avc.c

Purpose: minimal linked-list implementation for AVC/SELinux context data attached to parsed audit events.

Important APIs/functions: `alist_create()`, `alist_append()`, `alist_next()`, `alist_clear()`, `anode_init()`, `anode_clear()`, and filtered search/iteration helpers `alist_find_subj()`, `alist_next_subj()`, `alist_find_obj()`, `alist_next_obj()`, `alist_find_avc()`, `alist_next_avc()`.

Control flow: parsers allocate strings into a stack `anode`, call `alist_append()`, and the list takes pointer ownership by shallow-copying fields into a heap node. Matching/reporting routines position `cur` on the first node with subject/object/AVC result and iterate matching nodes.

State/persistence: only caller-owned `alist` state; no static state or persistence. `alist_clear()` frees all node strings through `anode_clear()`.

Dependencies/integration: used by `ausearch-parse.c` for parsed subject/object/AVC info, `ausearch-match.c` for context filters, `aureport-scan.c` for AVC summaries, and `ausearch-lookup.c` for result interpretation.

Risks/test signals: appends transfer raw pointers, so callers must not also free successful fields. Failed append paths can leak caller-allocated fields unless caller clears the temporary node. Cursor state is mutable and reused by find/next APIs. Tests should cover multiple AVC records per event, mixed subject/object-only nodes, clear after partial construction, and OOM behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-avc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-avc.h -->
## sources/security-integrity/audit-userspace/src/ausearch-avc.h

Purpose: defines AVC parsing/storage types used across `ausearch` and `aureport`.

Important APIs/types: `avc_t` has `AVC_UNSET`, `AVC_DENIED`, and `AVC_GRANTED`. `anode` stores `scontext`, `tcontext`, result, permission, class, and next pointer. `alist` stores head/current and count. The header exposes creation, append, clear, initialization, and filtered subject/object/result iteration.

Control flow/state: an `alist` usually hangs off `search_items.avc` inside an `llist`; parsers fill it lazily only when subject/object/context filters or reports need it.

Dependencies/integration: includes `libaudit.h` and is included by `ausearch-llist.h`, making these structures part of the shared event model.

Risks/test signals: comments still mention the string module, but the ABI is AVC-specific. Because `alist_first()` and `alist_get_cur()` are inline cursor helpers, callers must account for destructive cursor movement. Tests should verify that callers can perform repeated subject/object scans by resetting the cursor.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-avc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-checkpt.c -->
## sources/security-integrity/audit-userspace/src/ausearch-checkpt.c

Purpose: implements `ausearch --checkpoint`, persisting enough information to resume after the last complete output event.

Important APIs/functions: `set_ChkPtFileDetails()` records dev/inode of the input log; `set_ChkPtLastEvent()` records the last event timestamp, serial, type, and node; `save_ChkPt()` writes checkpoint text; `load_ChkPt()` reads it; `free_ChkPtMemory()` releases stored node strings. `parse_checkpt_event()` parses the `output=` line.

Control flow: `ausearch.c` loads checkpoint state at startup, compares future events against `chkpt_input_*`, updates `last_event` after processing events, records final file details, and writes the checkpoint if no checkpoint failure occurred.

State/persistence: persistent checkpoint file format is `dev=`, `inode=`, and `output=<node> <sec>.<milli>:<serial> 0x<type>`. Global/static state includes `checkpt_failure`, saved dev/inode, `last_event`, `chkpt_input_dev`, `chkpt_input_ino`, and `chkpt_input_levent`.

Dependencies/integration: depends on `event` from `ausearch-llist.h`, POSIX `stat()`, file I/O, and the checkpoint decision logic in `ausearch.c`.

Risks/test signals: checkpoint parsing mutates line buffers and uses `strtoull()` with limited end-pointer validation. `save_ChkPt()` overwrites directly rather than atomically. Corrupt or inode-reused files are detected later by event comparison. Tests should cover missing files, malformed lines, null node, node names, time_t size formats, inode reuse, and write failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-checkpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-checkpt.h -->
## sources/security-integrity/audit-userspace/src/ausearch-checkpt.h

Purpose: public checkpoint interface and failure code definitions for `ausearch`.

Important APIs/types: declares `set_ChkPtFileDetails()`, `set_ChkPtLastEvent()`, `free_ChkPtMemory()`, `save_ChkPt()`, and `load_ChkPt()`. Defines failure bits `CP_NOMEM`, `CP_STATFAILED`, `CP_STATUSIO`, `CP_STATUSBAD`, and `CP_CORRUPTED`. Exports `checkpt_failure`, `chkpt_input_dev`, `chkpt_input_ino`, and `chkpt_input_levent`.

Control flow/state: `ausearch.c` treats `load_ChkPt()` return values below `-1` as fatal, `-1` as first run, and `0` as resume data present.

Dependencies/integration: includes `ausearch-llist.h` for `event` and system types for `dev_t`/`ino_t`.

Risks/test signals: consumers can mutate exported checkpoint globals directly. Tests should verify failure-bit propagation through `ausearch` exit codes 10, 11, and 12.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-checkpt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-common.h -->
## sources/security-integrity/audit-userspace/src/ausearch-common.h

Purpose: shared global search/report contract for `ausearch`, `aureport`, and parser modules.

Important APIs/types: declares global criteria such as `start_time`, `end_time`, event id, uid/gid/pid/session/syscall/exit filters, node list, filename/host/terminal/exe/comm/uuid/vm filters, success/config filters, and `escape_mode`. Defines `MAX_EVENT_DELTA_SECS`, `failed_t`, `conf_act_t`, `success_t`, and `report_t`.

Control flow/state: option parsers set these globals; `ausearch-match.c`, `aureport-scan.c`, `ausearch-parse.c`, and output modules read them to decide which fields to parse, match, and render.

Dependencies/integration: includes `ausearch-string.h` for node lists and `auparse-defs.h` for escape modes. This is the central coupling point across the utility cluster.

Risks/test signals: global mutable state makes reentrant or library-style use unsafe. Some parser paths only extract fields when the corresponding global filter/report need is set, so tests must configure globals to exercise fields. Regression tests should isolate each process or reset all globals.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-int.c -->
## sources/security-integrity/audit-userspace/src/ausearch-int.c

Purpose: linked-list container for integer values with hit counts, used for message-type filters and report summaries.

Important APIs/functions: `ilist_create()`, `ilist_append()`, `ilist_next()`, `ilist_clear()`, `ilist_add_if_uniq()`, and `ilist_sort_by_hits()`. `swap_nodes()` supports hit sorting.

Control flow: callers append explicit values or use `ilist_add_if_uniq()` to maintain ascending numeric order while incrementing `hits` for duplicates. Summary output can sort by descending hit count.

State/persistence: caller-owned heap list; no static state. `ilist_clear()` tolerates null list pointers.

Dependencies/integration: used by `ausearch-options.c` for `event_type`, by `aureport-scan.c` for summary counters, and by output code that prints top values.

Risks/test signals: `ilist_append()` assumes `cur` is the tail when appending to a non-empty list. `ilist_add_if_uniq()` changes list order and cursor state. The hit sort is quadratic restart-on-swap. Tests should cover head/middle/tail insertion, duplicate hit increments, sort stability expectations, and clearing empty/null lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-int.h -->
## sources/security-integrity/audit-userspace/src/ausearch-int.h

Purpose: declares the small integer linked-list abstraction used by filters and report aggregators.

Important APIs/types: `int_node` stores `num`, `hits`, `aux1`, and `next`; `ilist` stores head/current/count. Inline helpers reset to first and get current node. Public functions create, append, clear, add unique, iterate, and sort by hits.

Control flow/state: consumers commonly call `ilist_first()`, inspect `ilist_get_cur()`, then advance with `ilist_next()`. Cursor state is mutable and belongs to the list.

Dependencies/integration: included by `ausearch-options.h` and `aureport-scan.h`, exposing it across command parsing and reporting.

Risks/test signals: no ownership beyond nodes. Cursor-based iteration is not thread-safe or reentrant. Tests should include multiple independent traversals that reset the cursor before reuse.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-llist.c -->
## sources/security-integrity/audit-userspace/src/ausearch-llist.c

Purpose: event-level linked list for audit records plus parsed searchable fields.

Important APIs/functions: `list_create()` initializes `llist` event/search state; `list_append()` shallow-transfers a record message/interp into a new `lnode`; `list_last()`, `list_next()`, `list_prev()`, `list_find_item()`, `list_find_msg()`, and `list_find_msg_range()` navigate records; `list_clear()` frees record messages and parsed search data; `list_get_event()` copies timestamp identity.

Control flow: `ausearch-lol.c` creates one `llist` per audit event and appends all records with matching timestamp/serial/node. Parser modules fill `l->s` after assembly. Matchers and reporters traverse by record type or item number.

State/persistence: no persistence. `llist` owns `lnode.message`, event node string, parsed strings, nested `slist`/`alist` allocations, and interpreted uid strings.

Dependencies/integration: includes string, AVC, common, and auditd config definitions. Used by nearly every file in this work item.

Risks/test signals: `list_prev()` relies on `item` numbering and calls `list_find_item()`, making reverse traversal O(n^2). `list_get_event()` omits node/type. `list_clear()` frees many optional fields and must remain synchronized with `search_items`. Tests should cover clear after every parser path, reverse output order, empty lists, and mixed enriched/raw records.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-llist.h -->
## sources/security-integrity/audit-userspace/src/ausearch-llist.h

Purpose: defines the central in-memory event model for `ausearch` and `aureport`.

Important APIs/types: `event` identifies an audit event by seconds, milliseconds, serial, node, and first type. `search_items` stores parsed pid/uid/gid/session/syscall/exit, host, files, cwd, exe, keys, terminal, comm, AVCs, account, uuid/vmname, and interpreted uid strings. `lnode` stores one raw/enriched audit record. `llist` owns a linked list of `lnode`, event identity, parsed fields, and log format.

Control flow/state: `lol_add_record()` populates record lists; `extract_search_items()` fills `search_items`; `match()` and report scanners consume it.

Dependencies/integration: includes `ausearch-string.h`, `ausearch-avc.h`, and `ausearch-common.h`, making this header the major dependency hub.

Risks/test signals: changes to `search_items` require updates to `list_create()` and `list_clear()`. Tests should assert default sentinel values, especially `uid=-1`, `loginuid=-2`, `session_id=-2`, `success=S_UNSET`, and `exit_is_set=0`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-llist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-lol.c -->
## sources/security-integrity/audit-userspace/src/ausearch-lol.c

Purpose: “list of lists” assembler that groups audit log lines into complete events and returns ready `llist` instances in chronological order.

Important APIs/functions: `lol_create()`, `lol_clear()`, `lol_add_record()`, `terminate_all_events()`, `complete_all_events()`, `get_ready_event()`, `lol_set_eoe_timeout()`, and `lol_get_eoe_timeout()`. Internal helpers parse timestamps (`extract_timestamp()`, `str2event()`), compare identities, grow the array, and mark events complete.

Control flow: each input line is timestamp-filtered, copied into an `lnode`, split into raw/enriched portions, and appended to an existing building event or a new `llist`. Events become complete when an end-of-event timeout has elapsed or a known last-record type is seen. `get_ready_event()` returns the complete event with lowest timestamp and transfers ownership to the caller.

State/persistence: process-local static `ready`, global `very_first_event`, and static `eoe_timeout`; no persistence. The `lol` array dynamically grows in blocks of 80.

Dependencies/integration: used by both `ausearch.c` and `aureport.c`; depends on `libaudit` helpers, common time filters, auditd log format constants, and `llist`.

Risks/test signals: timestamp extraction skips out-of-range records before assembly; this can affect multi-record events at range boundaries. `ready` is file-static, so multiple `lol` instances would interfere. Tests should cover enriched separator handling, node-prefixed logs, standalone EOE, interleaved events, array growth, stdin timeout completion, and malformed/fuzzer lines.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-lol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-lol.h -->
## sources/security-integrity/audit-userspace/src/ausearch-lol.h

Purpose: public interface for event assembly from raw audit records.

Important APIs/types: `lol_t` states `L_EMPTY`, `L_BUILDING`, and `L_COMPLETE`; `lolnode` stores an `llist *` and status; `lol` stores the dynamic node array, highest used index, and capacity. Public functions create, clear, add records, terminate/complete pending events, fetch ready events, and set EOE timeout.

Control flow/state: callers repeatedly call `lol_add_record()` and then `get_ready_event()`; returned lists must be cleared/freed by the caller.

Dependencies/integration: includes `ausearch-llist.h`; integrated into `ausearch.c`, `aureport.c`, and `ausearch-report.c` for timeout retrieval.

Risks/test signals: the header exposes array internals, so misuse can corrupt assembler state. Tests should validate ownership transfer and that `lol_clear()` does not double-free returned events.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-lol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-lookup.c -->
## sources/security-integrity/audit-userspace/src/ausearch-lookup.c

Purpose: converts raw audit values into readable or safely escaped output for `ausearch` and report summaries.

Important APIs/functions: `aulookup_result()`, `aulookup_success()`, `aulookup_syscall()`, `aulookup_uid()`, `aulookup_destroy_uid_list()`, `unescape()`, `safe_print_string_n()`, `safe_print_string()`, and `print_tty_data()`. Internal helpers map `socketcall`/`ipc` subcalls, hex-decode strings, escape TTY/shell output, and name TTY control sequences.

Control flow: lookup functions lazily initialize an `auparse` buffer parser for interpretations. UID lookups prefer enriched interpretations, then cache `getpwuid()` results in an `nvlist`. `safe_print_string_n()` chooses escaping based on global `escape_mode`. `print_tty_data()` decodes hex TTY data into printable text and named keys.

State/persistence: static `interp_init`, `au`, `machine`, UID cache, and constant lookup tables. No persistence; cache is destroyed by explicit cleanup.

Dependencies/integration: uses `libaudit`, `ausearch-options` report/escape globals, `ausearch-nvpair`, `auparse-idata`, Linux socket constants, and generated `auparse/tty_named_keys.h`.

Risks/test signals: lazy static parser and UID cache are not thread-safe. `unescape()` accepts both parenthesized and hex strings and returns malloced data that callers own. Output escaping is security-sensitive. Tests should include shell metacharacters, control bytes, malformed hex, abstract UNIX sockets, unknown uids, enriched interpretations, and TTY named key sequences.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-lookup.h -->
## sources/security-integrity/audit-userspace/src/ausearch-lookup.h

Purpose: declares readable lookup and safe output helpers.

Important APIs/types: exposes AVC result/success lookup, syscall and uid lookup with buffer access annotations, UID cache cleanup, audit string `unescape()`, TTY data printing, and safe string output helpers.

Control flow/state: callers pass parsed `llist` context for syscall naming and receive pointers to caller-provided buffers or static strings. `unescape()` returns heap memory and must be freed.

Dependencies/integration: includes `libaudit.h` and `ausearch-llist.h`, connecting lookup behavior to the central event model.

Risks/test signals: callers must honor buffer sizes and ownership. Tests should verify return lifetime expectations for every lookup function and escaping mode behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-lookup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-match.c -->
## sources/security-integrity/audit-userspace/src/ausearch-match.c

Purpose: applies `ausearch` command-line criteria to a parsed `llist` event.

Important APIs/functions: public `match()` returns 1 for events satisfying all requested criteria. Helpers `load_interpretations()`, `strmatch()`, `user_match()`, `group_match()`, and `context_match()` organize expensive work and criteria groups.

Control flow: `match()` first checks time and event serial, optionally loads interpretations for username filters, calls `extract_search_items()`, then short-circuits through node, user, group, ppid/pid, arch, syscall, session, exit, success, message type, filename/cwd, host, terminal, exe, comm, key, vm name, uuid, and SELinux context checks. Most options are ANDed; `--uid-all` and `--gid-all` OR their related ids; `--context` ORs subject/object context.

State/persistence: no own persistence; reads global search criteria and mutates list cursors. It can trigger interpretation state in `ausearch-report.c`.

Dependencies/integration: depends on globals from `ausearch-options.h`, field extraction from `ausearch-parse.c`, AVC lists, integer/string list cursors, and libaudit machine conversion.

Risks/test signals: parser extraction is conditional on global filters, so adding new filters requires parser updates. Cursor mutation means later output should reset list position. Tests should cover exact vs substring matching, username interpretation filters, combined AND/OR semantics, absent fields, multiple message types, context lists with multiple AVCs, and event_id/time boundaries.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-nvpair.c -->
## sources/security-integrity/audit-userspace/src/ausearch-nvpair.c

Purpose: small name/value linked-list cache, primarily for uid-to-name lookup.

Important APIs/functions: `search_list_create()`, `search_list_append()`, `search_list_find_val()`, and `search_list_clear()`.

Control flow: lookup code initializes a list, appends heap-owned names paired with numeric values, scans linearly for cached values, and clears names/nodes at shutdown.

State/persistence: caller-owned list only; no static state in this module. `search_list_append()` shallow-transfers `node->name` into a heap node.

Dependencies/integration: used by `ausearch-lookup.c` and `ausearch-parse.c` UID lookup caches.

Risks/test signals: append walks from `cur` to the end, so a stale `cur` must still be valid. No duplicate prevention is built in. Tests should cover cache hit/miss, clear after empty and populated lists, and ownership of appended names.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-nvpair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-nvpair.h -->
## sources/security-integrity/audit-userspace/src/ausearch-nvpair.h

Purpose: declares the name/value list used for lookup caches.

Important APIs/types: `nvnode` stores `name`, `val`, and `next`; `nvlist` stores head/current/count. Public APIs create, append, clear, get current, and find by value.

Control flow/state: list users rely on `cur` being positioned on a found or newly appended node.

Dependencies/integration: included by lookup/parser modules; only requires system types.

Risks/test signals: no const ownership annotation for `name`, but clear frees it. Tests should catch accidental use of string literals with `search_list_append()`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-nvpair.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-options.c -->
## sources/security-integrity/audit-userspace/src/ausearch-options.c

Purpose: parses `ausearch` CLI options and populates global search, output, checkpoint, and formatting state.

Important APIs/functions: `check_params()` is the public parser. Helpers `audit_lookup_option()`, `usage()`, `convert_str_to_msg()`, and `parse_msg()` map option strings and message type lists. It defines globals consumed throughout the cluster: `user_file`, `force_logs`, `checkpt_filename`, `report_format`, all `event_*` filters, CSV extra flags, `escape_mode`, and `arg_eoe_timeout`.

Control flow: manual argument scanning determines whether the next argv is an argument, switches on a table-driven option id, validates and converts numbers/names, allocates strings/lists, and performs final consistency checks such as requiring CSV for `--extra-*`.

State/persistence: process-global mutable state; no persistence. Allocations are partially freed by `ausearch.c` and related cleanup paths.

Dependencies/integration: uses libaudit message/syscall/machine helpers, passwd/group lookup, `ausearch-time.c`, `ausearch-int.c`, and `auparse-defs` escape modes.

Risks/test signals: the custom parser treats any next argument beginning with `-` as absent except for special negative numeric handlers, so option ordering and negative values need coverage. `--escape` checks `strncmp(optarg, "shell", 6)` before exact `shell_quote`, making `shell_quote` select shell mode rather than shell-quote mode. Globals duplicate `event_type` declaration. Tests should cover every option, invalid/missing args, conflicting formats, negative login/session/exit values, arch before syscall, node list allocation, CSV extra validation, and checkpoint time-only interaction.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-options.h -->
## sources/security-integrity/audit-userspace/src/ausearch-options.h

Purpose: exports `ausearch` option-derived globals and the command-line parsing entry point.

Important APIs/types: declares `event_key`, `event_subject`, `event_object`, `event_se`, `just_one`, `line_buffered`, `event_debug`, `event_ppid`, `event_session_id`, `event_type`, `report_format`, and `check_params()`.

Control flow/state: after `check_params()` succeeds, consumers read these globals directly rather than receiving a criteria object.

Dependencies/integration: includes `ausearch-common.h` and `ausearch-int.h`, linking option state to shared search enums and integer lists.

Risks/test signals: this header only exposes a subset of globals defined in the `.c`; other modules use additional `extern` declarations. Tests should guard against missing cleanup and conflicting duplicate declarations when adding options.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-parse.c -->
## sources/security-integrity/audit-userspace/src/ausearch-parse.c

Purpose: extracts searchable fields from assembled audit events and provides rotated-log timestamp discovery shared by `ausearch` and `aureport`.

Important APIs/functions: `extract_search_items()` dispatches per-record parsers; `lookup_uid_destroy_list()` clears parser uid cache; `audit_log_list()`, `audit_log_find_start()`, and `audit_log_free()` support rotated log traversal. Internal parsers cover syscall/uring, cwd/path/AVC path, user/login/daemon/kernel/integrity/anomaly/TTY/netfilter/socket records, AVCs, virtual machine fields, keys, hostnames, SELinux contexts, and success/session/exit data.

Control flow: extraction iterates every `lnode` in an `llist`, switches by audit message type, and fills `l->s`. Most parsers only do expensive extraction when the corresponding global filter or report need is set. Many parse routines temporarily NUL-terminate fields inside `n->message`, convert/unescape values, then restore delimiters.

State/persistence: parsed state is stored in `search_items`; cached uid names are in static `nvlist uid_nvl`; a static auparse buffer supports enriched interpretations. Log enumeration allocates an array of `audit_log_info` and reads first timestamps from files.

Dependencies/integration: depends on `libaudit`, `ausearch-options` globals, `ausearch-lookup` unescape, `ausearch-nvpair`, `auparse-idata`, sockets, passwd, and `llist` ownership semantics.

Risks/test signals: this is the highest-risk module. Parsers mutate message buffers, have many format-specific offsets (`NAME_OFFSET`), and can leak or overwrite fields on duplicate records. Conditional parsing means reports may miss fields unless the right globals are set. `audit_log_find_start()` assumes rotated log ordering by first timestamp. Tests should use real audit fixtures plus fuzzed malformed records for every parser return path, hex/unquoted/quoted strings, relative path rebuild with cwd, UNIX/IPv4/IPv6 sockaddr, USER_AVC, multiple AVCs, io_uring, config keys, virtual machine UUID/name, and rotated log start selection.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-parse.h -->
## sources/security-integrity/audit-userspace/src/ausearch-parse.h

Purpose: public parse/log-enumeration interface for `ausearch` and `aureport`.

Important APIs/types: declares `extract_search_items()`, `lookup_uid_destroy_list()`, `struct audit_log_info { name, sec, milli }`, `audit_log_list()`, `audit_log_find_start()`, and `audit_log_free()`.

Control flow/state: callers assemble an `llist`, call extraction before matching/reporting, and use log enumeration before reading rotated audit log files.

Dependencies/integration: includes `ausearch-llist.h`, so parse output is directly tied to `search_items`.

Risks/test signals: callers must free `audit_log_info` arrays through `audit_log_free()`. Tests should validate zero-log behavior, unreadable logs, empty logs, and timestamp parsing of first records.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-report.c -->
## sources/security-integrity/audit-userspace/src/ausearch-report.c

Purpose: formats matched `ausearch` events as raw, default, interpreted, CSV, or normalized text output.

Important APIs/functions: `output_event()` dispatches by `report_format`; `ausearch_load_interpretations()` and `ausearch_free_interpretations()` manage enriched interpretation state; `output_raw()`, `output_default()`, and `output_interpreted()` render record-oriented formats; `report_interpret()` interprets individual fields; `feed_auparse()` feeds complete events to auparse callbacks; `csv_event()` and `text_event()` produce normalized one-line outputs; `output_auparse_finish()` destroys feed parser state.

Control flow: default/interpreted modes output records in reverse item order except daemon messages. Interpreted mode rewrites type names, human time, field names/values, syscall context, and keys. CSV/text modes use `AUSOURCE_FEED`, set escape and EOE timeout, feed each record with restored separators/newlines, then flush to trigger callbacks.

State/persistence: static auparse parser for interpretations, static feed parser, loaded flag, syscall/machine/a0/a1 state, and CSV header flag. No persistence.

Dependencies/integration: depends on `ausearch-options`, `ausearch-parse`, `ausearch-lookup`, `auparse`, `auparse-idata`, normalization internals, and `lol_get_eoe_timeout()`.

Risks/test signals: functions temporarily mutate record messages to restore enriched separators/newlines and must restore them correctly. CSV output is not visibly quoting fields here, so comma/newline-containing interpretations need tests. Static parser state means multiple independent output streams are not isolated. Tests should cover all formats, enriched and raw events, key separator expansion, TTY data, normalized CSV extra flags, text normalization failures, and cleanup via `output_auparse_finish()`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-report.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-string.c -->
## sources/security-integrity/audit-userspace/src/ausearch-string.c

Purpose: linked-list container for strings with hit counts, used by report aggregators and parsed field lists.

Important APIs/functions: `slist_create()`, `slist_append()`, `slist_next()`, `slist_clear()`, `slist_add_if_uniq()`, and `slist_sort_by_hits()`. Sorting uses a small-list bubble-style algorithm and merge sort for lists of 200 or more.

Control flow: callers append preallocated `snode` strings or call `slist_add_if_uniq()` to deduplicate and count hits. `slist_sort_by_hits()` reorders nodes descending by hit count and resets `cur`.

State/persistence: caller-owned list; no module-static state. `slist_clear()` frees both `str` and `key` in every node.

Dependencies/integration: used by `search_items` filename/key lists, node filters, and `summary_data` report lists.

Risks/test signals: `slist_append()` shallow-transfers `str` and `key`; callers must allocate or otherwise ensure freeable ownership. Merge sort does not update `last`, which can break subsequent appends after sorting. Tests should cover append after sort, duplicate hit increments, key ownership, clear, and large summary lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-string.h -->
## sources/security-integrity/audit-userspace/src/ausearch-string.h

Purpose: declares the string list abstraction used for filters, parsed fields, and report summaries.

Important APIs/types: `snode` stores `str`, optional `key`, hit count, and next pointer; `slist` stores head/current/last/count. Public APIs create, iterate, append, clear, add unique, and sort by hits.

Control flow/state: cursor-based iteration starts with `slist_first()` and advances with `slist_next()`. `last` accelerates append.

Dependencies/integration: included by common/search/list/report headers, making it a core utility type.

Risks/test signals: ownership is implicit but `slist_clear()` frees node strings. Tests should include lists where `key` is populated by path parsing and appends after sorting.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-time.c -->
## sources/security-integrity/audit-userspace/src/ausearch-time.c

Purpose: parses absolute and relative time expressions for `ausearch`/`aureport` start and end filters.

Important APIs/functions: `lookup_time()`, `ausearch_time_start()`, and `ausearch_time_end()`. Internal setters handle `now`, `recent`, `this-hour`, `boot`, `today`, `yesterday`, `this-week`, `week-ago`, `this-month`, and `this-year`; helpers clear/replace `struct tm` fields.

Control flow: option parsing passes date/time strings. Date keywords fill a `struct tm`; otherwise localized `strptime("%x")` parses dates and `strptime("%X")` parses times, adding seconds when only hour/minute is provided. `boot` reads `/proc/uptime`. Results are converted with `mktime()` into global `start_time` or `end_time`.

State/persistence: defines global `time_t start_time` and `end_time`; no persistence. Uses current local time and locale-sensitive date/time parsing.

Dependencies/integration: consumed by `ausearch-options.c`, `ausearch-common.h`, `ausearch-lol.c` filtering, `ausearch-match.c`, and `aureport.c`.

Risks/test signals: locale-sensitive `%x/%X` means CLI date format varies. DST handling is partly acknowledged by comments. End time for `today` special-cases current time; start `today` uses midnight. Tests should freeze time where possible and cover every keyword, boot failure, invalid years before 2004, partial time, DST boundaries, and start/end inclusivity.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-time.h -->
## sources/security-integrity/audit-userspace/src/ausearch-time.h

Purpose: public interface for time keyword lookup and filter parsing.

Important APIs/types: enum constants for recognized relative time keywords and declarations for `lookup_time()`, `ausearch_time_start()`, and `ausearch_time_end()`.

Control flow/state: successful parse writes shared `start_time`/`end_time` globals declared through `ausearch-common.h`.

Dependencies/integration: includes `ausearch-common.h`; used by option parsing.

Risks/test signals: enum values are internal contract with `timetab`; adding keywords requires updating both header and implementation. Tests should assert unknown keyword returns `-1` and all declared keywords parse.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch.c -->
## sources/security-integrity/audit-userspace/src/ausearch.c

Purpose: main program for `ausearch`. It parses search options, reads audit logs/stdin/input files, assembles events, filters them, outputs matches, and manages checkpoints.

Important APIs/functions: `main()` coordinates lifecycle; `process_logs()` locates log files and checkpoint start positions; `process_file()`, `process_stdin()`, and `process_log_fd()` read events; `get_next_event()` feeds lines to the `lol` assembler with pipe timeout support; `chkpt_output_decision()` decides when checkpointed output may resume.

Control flow: after `check_params()`, it loads auditd config, sets EOE timeout, loads checkpoint data if requested, creates the assembler, chooses input source, processes complete events through `match()` and `output_event()`, updates last checkpoint event, saves checkpoint if clean, and frees lookup/parser/output state. Rotated logs are processed oldest-needed to newest by numeric suffix countdown.

State/persistence: process state includes `log_fd`, `lol lo`, `found`, `input_is_pipe`, timeout interval, `files_to_process`, auditd `config`, checkpoint flags, `userfile_is_dir`, and CLI globals. Persistence occurs only through checkpoint files via `ausearch-checkpt.c`.

Dependencies/integration: integrates `ausearch-options`, `ausearch-lol`, `ausearch-match`, `ausearch-report`, `ausearch-checkpt`, `ausearch-parse` log enumeration, `auditd-config`, `libaudit`, and `auparse`.

Risks/test signals: checkpoint correctness is subtle around inode reuse, partial events, `--start checkpoint`, and last-file flushing. `get_next_event()` uses SIGALRM to break pipe reads and shares static assembler ready state. Tests should cover no matches exit status, raw no-match silence, `--just-one`, stdin without checkpoint save, forced logs while stdin is pipe, directory input, rotated logs with checkpoint, corrupted checkpoint detection, EINTR/EOF handling, and cleanup paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/ausearch.c -->
