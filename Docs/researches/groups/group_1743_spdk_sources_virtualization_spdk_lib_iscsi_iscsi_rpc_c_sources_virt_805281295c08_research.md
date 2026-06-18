# Group Research: group_1743_spdk_sources_virtualization_spdk_lib_iscsi_iscsi_rpc_c_sources_virt_805281295c08

Scope verified against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/iscsi_rpc.c -->
# File Research: sources/virtualization/spdk/lib/iscsi/iscsi_rpc.c

Full-file read: 1600 lines.

This file registers and implements SPDK JSON-RPC methods for the iSCSI subsystem. It is mostly RPC glue: decode request objects, validate parameters, call iSCSI subsystem helpers, free generated RPC context allocations, and send JSON-RPC boolean/result/error responses.

Main responsibilities:
- Initiator group RPCs: get/create/delete groups and add/remove initiators/netmasks.
- Target node RPCs: get/create/delete targets, add/remove portal-group/initiator-group maps, add LUNs, configure auth, configure redirection, request logout, enable/read histograms.
- Portal group RPCs: get/create/delete/start portal groups and set portal-group CHAP auth.
- Auth group RPCs: create/delete CHAP groups and add/remove secrets.
- Option/stat RPCs: get/set iSCSI options, set discovery auth, enumerate connections, and aggregate connection states.

Important control flow:
- `SPDK_RPC_REGISTER` exposes methods with either `SPDK_RPC_RUNTIME` or `SPDK_RPC_STARTUP`.
- Most handlers use generated decoder/free helpers from `spdk_internal/rpc_autogen.h`.
- Target deletion is asynchronous: it heap-allocates context, calls `iscsi_shutdown_tgt_node_by_name`, and responds from `rpc_iscsi_delete_target_node_done`.
- `iscsi_get_connections` and `iscsi_get_stats` use `spdk_for_each_channel(&g_iscsi, ...)` to inspect every iSCSI poll group.
- Histogram enablement may run on the target poll-group thread and uses `target->num_active_conns` as a temporary lifetime guard.

Integration points:
- Depends heavily on `iscsi_subsystem.c`, `portal_grp.c`, `init_grp.c`, `tgt_node.c`, `conn.c`, SPDK JSON, RPC, base64, and histogram APIs.
- `iscsi_set_options` initializes `g_spdk_iscsi_opts` before subsystem startup and is intentionally single-use.
- JSON config dumping elsewhere must match these method names and parameter shapes.

Risks and review notes:
- Many invalid states collapse to generic `SPDK_JSONRPC_ERROR_INVALID_PARAMS`, so client diagnostics are limited.
- Several mutations find global objects without consistently holding `g_iscsi.mutex`; correctness depends on RPC/threading assumptions in the broader subsystem.
- `iscsi_get_histogram` reads `target->histogram` without the same target mutex choreography used by enablement.
- `iscsi_set_options` relies on `spdk_json_decode_string` freeing pre-existing default strings before reassignment; this is documented in-line and should be preserved carefully.

Testing focus:
- RPC decode failures, duplicate/missing required fields, and optional defaults.
- Target deletion while connections are active.
- Portal creation rollback on partial failure.
- Histogram enable/get/disable across active and inactive targets.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/iscsi_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/iscsi_subsystem.c -->
# File Research: sources/virtualization/spdk/lib/iscsi/iscsi_subsystem.c

Full-file read: 1356 lines.

This file owns iSCSI subsystem lifecycle, global option defaults/validation, mempool allocation, poll-group thread setup, CHAP auth group storage, and JSON config emission.

Main responsibilities:
- Defines global startup options pointer `g_spdk_iscsi_opts`.
- Allocates PDU, immediate-data, data-out, session, and task mempools.
- Allocates and validates `spdk_iscsi_opts`, then copies values into `g_iscsi`.
- Maintains CHAP auth groups and secrets, including config-file parsing.
- Initializes per-core iSCSI poll-group threads and socket pollers.
- Coordinates shutdown: closes portals, drains connections, releases channels, unregisters the I/O device, destroys pools and global lists.
- Emits iSCSI options and auth groups as JSON and contributes to `spdk_iscsi_config_json`.

Important control flow:
- `spdk_iscsi_init` stores callback state, parses globals, creates poll groups on every SPDK core, then completes after all poll groups report back.
- `iscsi_poll_group_poll` polls socket groups and destructs connections in `ISCSI_CONN_STATE_EXITING`.
- `shutdown_iscsi_conns_done` walks all channels and tears down poll groups.
- `iscsi_initialize_global_params` consumes `g_spdk_iscsi_opts` or creates defaults, then frees the options object.
- `iscsi_chap_get_authinfo` locks `g_iscsi.mutex` while copying auth secret material.

Integration points:
- Uses SPDK mempool, thread, I/O channel, poller, socket, conf, SCSI, and JSON writer APIs.
- Calls into `conn.c` for connection pools/shutdown, `portal_grp.c` for listener shutdown, `tgt_node.c` for target cleanup, and `init_grp.c` for initiator group destruction.
- Auth data created here is consumed during CHAP login.

Risks and review notes:
- Mempool initialization failure paths do not always free earlier pools immediately; final cleanup may rely on later shutdown paths.
- `iscsi_auth_group_info_json` writes CHAP secrets back into JSON output, so callers must treat config dumps as sensitive.
- `iscsi_parse_auth_info` destroys all auth groups on parse error, which is correct for atomic config loading but important operationally.
- `iscsi_poll_group_destroy` calls `spdk_thread_exit(thread)`, so lifecycle assumptions around SPDK thread ownership are tight.

Testing focus:
- Invalid option bounds and CHAP combinations.
- Auth file parse success/failure and duplicate users.
- Init/fini callback ordering across multiple cores.
- Pool leak detection via `iscsi_check_pools`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/iscsi_subsystem.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/param.c -->
# File Research: sources/virtualization/spdk/lib/iscsi/param.c

Full-file read: 1199 lines.

This file implements iSCSI text parameter parsing, linked-list parameter storage, negotiation rules, and copying negotiated values into connection/session runtime fields.

Main responsibilities:
- Manage `struct iscsi_param` linked lists: add, delete, set, find, free, compare, and fetch values.
- Parse NUL-delimited `KEY=VAL` text buffers, including fragmented parameters across PDUs when the C bit is used.
- Initialize default connection and session parameter tables.
- Negotiate list, numeric min/max/declarative, boolean OR/AND, declarative, discovery, CHAP, extension, and unsupported keys.
- Enforce one-time negotiation state for most connection/session parameters.
- Copy negotiated values into `spdk_iscsi_conn` and `spdk_iscsi_sess`.

Important control flow:
- `iscsi_parse_param` validates key/value lengths, duplicates, `=`, and simple-value limits.
- `iscsi_parse_params` stitches a previous partial parameter to the current buffer, then optionally saves a new trailing partial when C bit is set.
- `iscsi_negotiate_params` checks discovery mode, ignores CHAP keys, handles `SendTargets` specially, reorders `FirstBurstLength` after `MaxBurstLength`, negotiates values, updates persistent params, and appends response text.
- `iscsi_special_param_construction` emits target-side declarative `MaxRecvDataSegmentLength` and fixes `FirstBurstLength <= MaxBurstLength`.
- `iscsi_copy_param2var` applies negotiated digest, burst, R2T, connection, and immediate-data values.

Integration points:
- Used by login/text handling in the iSCSI connection layer.
- Depends on constants and connection/session fields from `iscsi/iscsi.h` and `iscsi/conn.h`.
- Negotiation results influence later SCSI transfer sizing, digest behavior, and data-out/data-in sequencing.

Risks and review notes:
- The code mutates temporary comma-separated strings in place during list negotiation.
- Partial parameter handling is subtle and should be fuzzed with boundary-length buffers and C-bit splits.
- Numeric parsing uses `strtol` after parser validation but without full range revalidation in every path.
- Unknown non-extension keys produce `NotUnderstood`; `NotUnderstood` for understood keys is treated as login error.

Testing focus:
- C-bit fragmentation across every possible split position.
- Duplicate key rejection and max key/value lengths.
- Negotiation once-only errors.
- Discovery-session ignored parameters.
- `FirstBurstLength`/`MaxBurstLength` ordering and clamping.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/param.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/param.h -->
# File Research: sources/virtualization/spdk/lib/iscsi/param.h

Full-file read: 58 lines.

This header declares the iSCSI text parameter model and negotiation API.

Main contents:
- `enum iscsi_param_type` covers invalid, unspecified, list, numerical min/max/declarative, declarative, boolean OR, and boolean AND parameter semantics.
- `struct iscsi_param` is a singly-linked node with key, value, valid-list string, type, and negotiation state index.
- Declares parse, lookup, mutation, negotiation, copy-to-runtime, and default initialization functions.

Integration points:
- Included by login/text processing and `param.c`.
- Forward-declares `struct spdk_iscsi_conn` to avoid exposing connection internals.

Risks and review notes:
- The API exposes mutable linked-list nodes and string pointers; callers must respect ownership rules from `param.c`.
- `state_index` couples runtime arrays in connection/session objects to the static parameter tables.

Testing focus:
- Compile-time coverage through consumers.
- ABI/API stability if parameter tables are extended.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/param.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/portal_grp.c -->
# File Research: sources/virtualization/spdk/lib/iscsi/portal_grp.c

Full-file read: 514 lines.

This file implements iSCSI portal and portal-group management, including listener sockets, accept polling, CHAP defaults, redirect address parsing, and JSON output.

Main responsibilities:
- Create/destroy portals and portal groups.
- Normalize wildcard portal addresses: `[*]` to `[::]`, `*` to `0.0.0.0`.
- Prevent duplicate global portal address/port pairs.
- Open listener sockets, add them to SPDK socket groups, accept incoming sockets, and construct iSCSI connections.
- Register/unregister portal groups in `g_iscsi.pg_head`.
- Close/release all portal resources.
- Store portal-group CHAP policy and serialize portal groups to JSON/config JSON.

Important control flow:
- `iscsi_portal_accept` loops on `spdk_sock_accept` until no socket is available; each accepted socket is passed to `iscsi_conn_construct`.
- `iscsi_portal_grp_open` creates a socket group, registers an acceptor poller, optionally pauses it, then opens every portal.
- `iscsi_portal_grp_release` closes sockets/poller/socket group and destroys portals/group.
- `iscsi_parse_redirect_addr` validates numeric host/port with `getaddrinfo`.

Integration points:
- Called by iSCSI RPCs and subsystem shutdown.
- New accepted connections enter the connection layer via `iscsi_conn_construct`.
- Portal groups are mapped into targets by `tgt_node.c`.

Risks and review notes:
- If one portal fails during `iscsi_portal_grp_open`, cleanup is left to caller release paths.
- Duplicate detection compares the input host/port, while wildcard normalization changes stored host strings; edge cases around `*` versus `0.0.0.0` matter.
- `iscsi_portal_grp_close_all` holds `g_iscsi.mutex` while closing groups, which calls socket APIs.

Testing focus:
- Duplicate and wildcard portal creation.
- Partial portal open failure and release.
- Paused portal group start behavior.
- IPv4/IPv6 redirect address validation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/portal_grp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/portal_grp.h -->
# File Research: sources/virtualization/spdk/lib/iscsi/portal_grp.h

Full-file read: 78 lines.

This header defines portal and portal-group data structures and management APIs.

Main contents:
- `struct spdk_iscsi_portal`: group pointer, bounded host/port buffers, listener socket, per-group/global queue links.
- `struct spdk_iscsi_portal_grp`: refcount, tag, public/private flag, CHAP settings, socket group, acceptor poller, and portal list.
- Public/private semantics for login redirection are documented in the structure comments.
- Declares create/destroy/register/unregister/find/open/close/info/config APIs and redirect address parsing.

Integration points:
- Consumed by RPC, target-node mapping, subsystem lifecycle, and connection accept paths.

Risks and review notes:
- Refcount is an integer field managed manually by target-node mappings.
- Public/private redirect behavior depends on target-node code honoring `is_private`.

Testing focus:
- Structure lifecycle through portal group create/map/delete.
- Refcount behavior when portal groups are removed while targets reference them.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/portal_grp.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/task.c -->
# File Research: sources/virtualization/spdk/lib/iscsi/task.c

Full-file read: 82 lines.

This file allocates and frees iSCSI task objects backed by the global task mempool.

Main responsibilities:
- `iscsi_task_get` obtains a task from `g_iscsi.task_pool`, zeroes it, timestamps it, associates it with a connection, increments pending-task counters, and constructs the embedded `spdk_scsi_task`.
- Parent/subtask initialization copies SCSI metadata and transfer state from the parent and increments parent refcount.
- `iscsi_task_free` handles histogram tallying, parent release, data-in counter decrement, mobj return, PDU disassociation, pending-task decrement, and mempool return.

Integration points:
- Wraps SPDK SCSI task lifecycle via `spdk_scsi_task_construct`.
- Uses target histograms from `tgt_node.c` and PDU/data-pool helpers from the iSCSI connection/subsystem layer.

Risks and review notes:
- Mempool exhaustion aborts the process.
- Histogram access assumes target lifetime and histogram pointer stability while the task is freed.
- Parent/subtask refcount and `data_in_cnt` counters must stay balanced.

Testing focus:
- Parent/subtask free ordering.
- Histogram tally on task completion.
- PDU/mobj cleanup paths.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/task.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/task.h -->
# File Research: sources/virtualization/spdk/lib/iscsi/task.h

Full-file read: 170 lines.

This header defines the iSCSI task object and inline helpers.

Main contents:
- `struct spdk_iscsi_task` embeds `spdk_scsi_task` and adds iSCSI state: parent, connection, PDU, memory object, timestamp, R2T/DataSN counters, offsets, transfer progress, tag, LUN ID, poller, queue links, and subtask list.
- Inline helpers wrap `spdk_scsi_task_put`, PDU association/disassociation, BHS access, immediate/read checks, primary-task lookup, and memory-object access.
- Declares `iscsi_task_get`.

Integration points:
- Used throughout command, data-in/data-out, management, and cleanup paths in the iSCSI layer.
- PDU association increments `pdu->ref`; disassociation calls `iscsi_put_pdu`.

Risks and review notes:
- Inline BHS access assumes a task always has an associated PDU.
- Many transfer counters are protocol-sensitive; initialization and reset must stay centralized.
- `lun_id` is kept separately to survive hot-remove cases.

Testing focus:
- Read/write task state transitions.
- PDU refcount balance.
- Subtask parent/primary behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/task.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/tgt_node.c -->
# File Research: sources/virtualization/spdk/lib/iscsi/tgt_node.c

Full-file read: 1422 lines.

This file implements iSCSI target-node core behavior: access control, SendTargets output, portal/initiator mapping, target construction/destruction, redirection, LUN mutation, CHAP settings, histogram allocation, and JSON serialization.

Main responsibilities:
- Match IPv4/IPv6 initiator addresses against initiator-group netmasks, including `ANY`.
- Enforce initiator IQN allow/deny rules, including `!` deny entries.
- Generate discovery `TargetName` and `TargetAddress` text responses with continuation support via `conn->send_tgt_completed_size`.
- Maintain target-to-portal-group and portal-group-to-initiator-group maps with manual refcounts.
- Construct SPDK SCSI devices and add SCSI ports/LUNs.
- Safely destruct targets after requesting connection logout and waiting for active connections to drain.
- Configure public-portal redirection to private portal destinations.
- Emit target info/config JSON and optional histogram-enable config.
- Allocate/free target latency histograms.

Important control flow:
- `iscsi_tgt_node_access` checks the connection portal group, target mapping, initiator name, and initiator address before allowing login.
- `iscsi_send_tgts` walks all targets under `g_iscsi.mutex`, filters by target name and initiator visibility, and writes as much as fits.
- Mapping add/remove functions roll back prior changes on failure.
- `iscsi_tgt_node_destruct` marks the target destructed, requests logout, then either polls active connection count or destructs the SCSI device immediately.
- `iscsi_tgt_node_construct` validates CHAP, maps short names through `g_iscsi.nodebase`, validates IQN-ish formatting, constructs the SCSI dev, adds maps, sets auth/digest/queue-depth, and registers globally.

Integration points:
- Depends on portal groups, initiator groups, connection state, SPDK SCSI devices/LUNs/ports, and histogram APIs.
- RPC handlers call most public mutation APIs here.
- Login/discovery code depends on access checks, redirect checks, and SendTargets construction.

Risks and review notes:
- IPv4/IPv6 CIDR parsing rejects prefix length 0, so `/0` is not accepted; `ANY` is the intended universal match.
- `iscsi_tgt_node_delete_ig_maps` ignores missing-map errors, suitable for global cleanup but important to understand.
- `iscsi_tgt_node_add_lun` refuses LUN changes while active connections exist.
- Redirection validates numeric host/port and requires redirect target not be in the same public group, but the private-group requirement is enforced indirectly by “different private portal group” policy checks.
- Target JSON includes CHAP flags and group id but not redirect settings.

Testing focus:
- Access matrix across allow/deny IQNs, IPv4/IPv6 netmasks, `ANY`, and portal mappings.
- SendTargets continuation with small buffers.
- Map add/remove rollback.
- Target destruction while connections are active.
- Redirect configure/clear validation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/tgt_node.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/tgt_node.h -->
# File Research: sources/virtualization/spdk/lib/iscsi/tgt_node.h

Full-file read: 126 lines.

This header defines target-node mapping structures and public target-node APIs.

Main contents:
- `struct spdk_iscsi_ig_map` maps one initiator group into a portal-group map.
- `struct spdk_iscsi_pg_map` maps one portal group, owns initiator-group maps, and stores redirect host/port.
- `struct spdk_iscsi_tgt_node` stores name/alias, mutex, CHAP/digest settings, queue depth, SCSI device, active connection tracking, portal-group maps, destruct callback state, and histogram pointer.
- Declares target construction, shutdown, access checks, map mutation, redirect checks, LUN addition, CHAP updates, JSON output, and histogram enablement.

Integration points:
- Central internal API for RPC, login/discovery, connection cleanup, and subsystem shutdown.

Risks and review notes:
- Public functions return mixed conventions: `bool`, `int`, pointer, and callback completion; callers must handle each carefully.
- `num_active_conns` and `pg` are used for lifetime/thread coordination during histogram and destruction paths.

Testing focus:
- Header/API consumers compile against structure changes.
- Lifetime-sensitive fields during target deletion and histogram operations.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/tgt_node.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/json/Makefile -->
# File Research: sources/virtualization/spdk/lib/json/Makefile

Full-file read: 17 lines.

This Makefile builds SPDK’s `json` library.

Main contents:
- Sets `SPDK_ROOT_DIR` two levels up and includes `mk/spdk.common.mk`.
- Defines shared object version `SO_VER := 8` and `SO_MINOR := 0`.
- Builds `json_parse.c`, `json_util.c`, and `json_write.c` into `LIBNAME = json`.
- Uses `spdk_json.map` as the symbol map.
- Includes `mk/spdk.lib.mk`.

Integration points:
- Provides the JSON library used by JSON-RPC and many SPDK subsystems, including iSCSI RPC/config output.

Risks and review notes:
- Library ABI versioning and symbol-map updates must track exported API changes.

Testing focus:
- Build/link of `libspdk_json`.
- Symbol-map completeness for exported JSON APIs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/json/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/json/json_parse.c -->
# File Research: sources/virtualization/spdk/lib/json/json_parse.c

Full-file read: 640 lines.

This file implements SPDK’s low-level JSON tokenizer/parser.

Main responsibilities:
- Validate and optionally decode JSON strings in place.
- Decode two-character escapes and Unicode `\uXXXX`, including UTF-16 surrogate pairs.
- Validate number syntax without converting to numeric types.
- Optionally accept C/C++-style comments when the parse flag allows it.
- Parse JSON into a flat `spdk_json_val` token array with begin/end container tokens.
- Report incomplete, invalid, and max-depth errors.

Important control flow:
- `spdk_json_parse` first can be called with `values == NULL` to count tokens and find complete-message boundaries.
- The parser uses a state machine for value, separator, object name, colon, and end states.
- Container starts record their token index so the begin token’s `len` can later be set to contained token count.
- Nesting is capped at `SPDK_JSON_MAX_NESTING_DEPTH` of 64.
- With `SPDK_JSON_PARSE_FLAG_DECODE_IN_PLACE`, string values point into decoded bytes inside the original buffer.

Integration points:
- Used by JSON-RPC request/response parsing and by utility decoders.
- Depends on internal UTF helpers for validation and encoding.

Risks and review notes:
- In-place decode means callers must keep the original mutable buffer alive while using tokens.
- No resynchronization is possible after a streaming parse error; JSON-RPC closes connections on invalid parse.
- Comments are intentionally flag-gated and not JSON-standard.

Testing focus:
- Unicode surrogate validity and incomplete escapes.
- Number grammar edge cases.
- Container length correctness.
- Full/incomplete streaming parse behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/json/json_parse.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/json/json_util.c -->
# File Research: sources/virtualization/spdk/lib/json/json_util.c

Full-file read: 733 lines.

This file provides utility functions for working with parsed SPDK JSON token arrays.

Main responsibilities:
- Compute token span length and array element count.
- Compare and duplicate JSON string/name values as C strings.
- Split JSON numbers into sign, significand, and exponent with overflow checks.
- Convert JSON numbers to fixed integer types.
- Decode JSON objects and arrays using decoder tables.
- Free decoder-owned object fields by decoding invalid sentinel values.
- Decode booleans, strings, UUIDs, and integer types.
- Find typed object members and iterate object/array values.

Important control flow:
- `_json_decode_object` tracks duplicate fields and required/optional fields using a `seen` bitmap.
- Relaxed object decoding ignores unknown fields; strict decoding rejects them.
- `spdk_json_decode_array` walks child tokens with `spdk_json_val_len`.
- `spdk_json_next` skips nested arrays/objects by walking to the matching end token.

Integration points:
- Used by RPC handlers throughout SPDK, including `iscsi_rpc.c`.
- Depends on `json_parse.c` token shapes and `spdk_uuid_parse`.

Risks and review notes:
- `spdk_json_decode_string` frees the destination pointer before replacing it; callers often preload defaults and rely on this behavior.
- `spdk_json_decode_array` requires caller-provided output storage and max size.
- Number conversion rejects exponents/fractions for integer outputs, as expected.

Testing focus:
- Duplicate/missing/unknown object keys in strict and relaxed modes.
- Numeric overflow, negative unsigned values, and fractional integers.
- Iterator behavior over nested containers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/json/json_util.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/json/json_write.c -->
# File Research: sources/virtualization/spdk/lib/json/json_write.c

Full-file read: 873 lines.

This file implements SPDK’s buffered JSON writer.

Main responsibilities:
- Manage `spdk_json_write_ctx` with callback, flags, indentation state, failure state, and a 4096-byte buffer.
- Emit scalar JSON values, names, arrays, objects, batches, UUIDs, byte arrays, raw values, formatted strings, and named variants.
- Escape UTF-8 and UTF-16LE strings into valid JSON, using short escapes or `\uXXXX`/surrogate pairs.
- Buffer output and flush through caller-provided write callbacks.
- Replay parsed `spdk_json_val` token trees via `spdk_json_write_val`.

Important control flow:
- `begin_value` handles comma/newline/indent emission and first-value state.
- `emit` fast-paths into the internal buffer; `emit_buf_full` flushes and recurses for overflow.
- `spdk_json_write_array_begin/object_begin` reset first-value state and increment indent.
- `spdk_json_write_name_raw` writes a name and colon, then allows the next value as first in that name context.
- `spdk_json_write_end` flushes, frees the context, and reports latched failure.

Integration points:
- Used by JSON-RPC responses, SPDK config emission, iSCSI info/config RPCs, and client request building.
- Depends on internal UTF helpers and SPDK string formatting helpers.

Risks and review notes:
- The writer has TODO comments for stricter container state checking; misuse can generate structurally invalid JSON.
- `emit_buf_full` uses pointer arithmetic on `void *`, relying on compiler behavior accepted in this codebase.
- Failure latching prevents silent success after callback or encoding failure.

Testing focus:
- Escaping all control characters and multibyte Unicode.
- Deep formatted arrays/objects.
- Callback failure propagation.
- Raw token replay for nested values.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/json/json_write.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/Makefile -->
# File Research: sources/virtualization/spdk/lib/jsonrpc/Makefile

Full-file read: 18 lines.

This Makefile builds SPDK’s `jsonrpc` library.

Main contents:
- Sets `SPDK_ROOT_DIR` and includes common SPDK make rules.
- Defines shared object version `SO_VER := 8` and `SO_MINOR := 0`.
- Builds server, server TCP, client, and client TCP sources into `LIBNAME = jsonrpc`.
- Uses `spdk_jsonrpc.map` as the symbol map.
- Includes `mk/spdk.lib.mk`.

Integration points:
- Links the JSON-RPC transport/protocol layer used by SPDK RPC servers and clients.

Risks and review notes:
- This grouped research includes client/internal files but the Makefile also builds server sources outside this work item.

Testing focus:
- Library build/link with all listed C sources.
- Symbol-map coverage after API changes.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_client.c -->
# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_client.c

Full-file read: 296 lines.

This file implements JSON-RPC client-side protocol serialization and response parsing, independent of socket transport.

Main responsibilities:
- Decode JSON-RPC 2.0 responses into `spdk_jsonrpc_client_response`.
- Handle single responses and simplified batch responses.
- Build JSON-RPC request objects and request batches into a send buffer.
- Grow request send buffers up to `SPDK_JSONRPC_SEND_BUF_SIZE_MAX`.

Important control flow:
- `jsonrpc_parse_response` first parses without token storage to detect complete JSON and token count, then reparses with in-place decode into owned response storage.
- Batch responses are decoded as arrays; the first error is preserved, otherwise the first result is retained because current use only needs batch success/failure.
- `spdk_jsonrpc_begin_request` writes `jsonrpc`, optional `id`, and optional `method`.
- Single requests finalize immediately and append newline; batch requests share a write context until `spdk_jsonrpc_end_batch`.

Integration points:
- Transport code in `jsonrpc_client_tcp.c` owns sockets and calls `jsonrpc_parse_response`.
- Uses SPDK JSON parser/writer/util APIs.

Risks and review notes:
- Simplified batch response handling discards most individual responses.
- Client supports string or numeric response IDs, but request builder writes integer IDs.
- Only one parsed response can be pending in `client->resp`; another response before retrieval returns `-ENOSPC`.

Testing focus:
- Incomplete streaming response parse.
- Parse errors and oversized token counts.
- Batch success, batch with first/late error, and all-notification-like edge cases.
- Send buffer growth and maximum limit.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_client.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_client_tcp.c -->
# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_client_tcp.c

Full-file read: 397 lines.

This file implements the socket transport for the SPDK JSON-RPC client.

Main responsibilities:
- Create nonblocking AF_UNIX or TCP sockets and connect to JSON-RPC servers.
- Poll connecting sockets until `SO_ERROR` confirms connection success.
- Send queued request buffers and free requests after all bytes are written.
- Receive response bytes into a growable buffer, NUL-terminate it, and invoke `jsonrpc_parse_response`.
- Provide client close, request allocation/free, send, poll, response get, and response free APIs.

Important control flow:
- `spdk_jsonrpc_client_connect` parses AF_UNIX paths directly or uses `spdk_parse_ip_addr` plus `getaddrinfo` for TCP; default TCP port is `5260`.
- `spdk_jsonrpc_client_poll` switches between connecting and connected poll paths.
- Connected polling listens for both `POLLIN` and `POLLOUT`; it sends pending request data first, then receives.
- `spdk_jsonrpc_client_get_response` transfers ownership of the internal response object to the caller.

Integration points:
- Uses protocol helpers and structs from `jsonrpc_internal.h`.
- Uses POSIX sockets, `poll`, `getaddrinfo`, and SPDK string/util logging helpers.

Risks and review notes:
- Only one outstanding request buffer is accepted at a time.
- Receive buffer grows by doubling and is bounded by the send-buffer max constant.
- On connect errors after socket creation, sockfd is closed and reset.
- `jsonrpc_client_poll` treats `-EAGAIN` as incomplete-message non-error, though `jsonrpc_parse_response` returns `0` for incomplete in this client implementation.

Testing focus:
- Nonblocking connect success/failure/timeouts.
- Partial send and partial receive.
- AF_UNIX path length rejection.
- Default port parsing and invalid address handling.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_client_tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_internal.h -->
# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_internal.h

Full-file read: 196 lines.

This internal header defines JSON-RPC server/client buffers, state structures, limits, and internal function declarations.

Main contents:
- Buffer and limit constants: receive size, send initial/max size, ID max, max connections, max JSON values.
- `struct spdk_jsonrpc_request`: server-side request with connection, copied ID token, send/receive buffers, parsed values, write context, optional batch pointer, and queue link.
- `struct spdk_jsonrpc_batch_request`: batch aggregation state, spinlock, completion counts, response buffer, and original parse buffers.
- `struct spdk_jsonrpc_server_conn`: socket, closed flag, receive buffer, outstanding count, queue lock, send/outstanding queues, close callback, and list link.
- `struct spdk_jsonrpc_server`: listener socket, handler callback, free/active connection queues, and fixed connection array.
- `struct spdk_jsonrpc_client_request`, `spdk_jsonrpc_client_response_internal`, and `spdk_jsonrpc_client`.
- Internal declarations for server request handling, completion, batch cleanup, and client response parsing.

Integration points:
- Shared by JSON-RPC client/server implementation files.
- Encodes ownership expectations for buffers and parsed token lifetimes.

Risks and review notes:
- Fixed server connection cap is 64.
- Server receive buffer is fixed at 256 KiB, while client receive buffer can grow much larger.
- Batch completion uses a spinlock because handlers may complete from different threads.
- Comments distinguish functions that must run only on the server poll thread.

Testing focus:
- Concurrent batch completion.
- Shutdown with incomplete outstanding requests.
- Buffer-limit behavior for large requests/responses.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_internal.h -->