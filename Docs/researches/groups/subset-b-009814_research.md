# subset-b-009814 research

Grouped research for Samba source3 library LDAP transport/bind helpers and adjacent utility files. Each section is source-tree aligned and bounded by reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap.c -->
# sources/user-network-fs/samba/source3/lib/tldap.c

## Purpose
`tldap.c` implements Samba's async LDAP client core on top of `tevent`, `tstream`, talloc, and Samba ASN.1 helpers. It owns LDAP context lifecycle, message ID allocation, plain/TLS/GENSEC stream switching, pending request tracking, request encoding, response dispatch, LDAP filter parsing, bind/search/add/modify/delete/extended operations, and synchronous wrappers.

## Important APIs, types, and functions
Key state is `struct tldap_context`, which stores LDAP version, plain/tls/gensec/active streams, outgoing write queue, pending request array, active read request, last synchronous response, debug callback, and context attributes. `struct tldap_message` holds decoded response state, entry attributes, result codes, diagnostic strings, SASL credentials, extended response data, and controls. Public helpers include `tldap_context_create`, `tldap_context_create_from_plain_stream`, `tldap_connection_ok`, stream accessors/setters, context attributes, `tldap_sasl_bind[_send/_recv]`, `tldap_simple_bind`, `tldap_search[_send/_recv]`, `tldap_search_all_send`, `tldap_add`, `tldap_modify`, `tldap_delete`, `tldap_extended`, entry accessors, response metadata accessors, and `tldap_rc2string`.

## Control flow
Outbound operations call `tldap_req_create` to start an LDAPMessage sequence and assign a message ID. The operation-specific encoder writes the LDAP protocol payload and delegates to `tldap_msg_send`, which appends controls, serializes ASN.1, puts the request in `ld->pending`, and queues a write on `ld->active`. The first pending request starts a packet read. `read_ldap_more` peeks ASN.1 sequence length so `tstream_read_packet_send` reads whole LDAP PDUs. `tldap_msg_received` parses message ID/type, finds the matching pending request, moves the ASN.1 data into that request, completes it, and starts the next read while pending requests remain. Search is multi-step: entries and references re-register the subrequest as pending and notify the caller, while the final result decodes LDAPResult and controls.

## State and persistence behavior
All state is in-memory and scoped to the talloc hierarchy. Stream upgrades replace the active transport and free old TLS/GENSEC wrappers as needed. Disconnect tears down streams, stops the outgoing queue, cancels the read request, and completes all pending requests with an LDAP error. Synchronous wrappers create a temporary event context, poll the async operation, then save the final result in `ld->last_msg` for diagnostic retrieval.

## Dependencies and integration points
The file depends on Samba's ASN.1 codec, `tevent_req`, `tevent_queue`, `tstream` BSD/TLS/GENSEC streams, talloc stack frames, NT status helpers, and Samba charset/string helpers. It is the foundation used by `tldap_util.c`, TLS connect, GENSEC bind, LDAP tests, passdb, AD, and client code that needs LDAP without libldap.

## Risks and edge cases
Risk concentrates in ASN.1 length parsing, pending request cleanup, message ID routing, and filter escaping. Unexpected message ID zero or malformed packets disconnect all requests because the client cannot safely attribute the response. Filter parsing is intentionally strict, disallowing whitespace outside values and validating attribute descriptions, escapes, substring rules, extensible match forms, and empty AND/OR filters. Synchronous search returns `TLDAP_BUSY` if async requests are already pending. The `cctrls` client-control parameters are accepted by several APIs but not materially used in this implementation.

## Test signals
`source3/lib/test_tldap.c` is the adjacent focused test file for filter encoding, request/response behavior, and LDAP result handling. Higher-level LDAP bind/search code indirectly tests stream switching, controls, and sync wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.c -->
# sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.c

## Purpose
This file implements SASL `GSS-SPNEGO` LDAP bind using Samba GENSEC. It drives the token exchange over `tldap_sasl_bind_send` and optionally wraps the LDAP connection in a signed or sealed GENSEC tstream after authentication.

## Important APIs, types, and functions
`struct tldap_gensec_bind_state` carries the event context, LDAP context, credentials, target service/host/principal, loadparm context, requested GENSEC features, GENSEC security context, current NTSTATUS, and input/output tokens. `tldap_gensec_bind_send`, `tldap_gensec_bind_recv`, and synchronous `tldap_gensec_bind` form the public API. Internal callbacks `tldap_gensec_update_next`, `tldap_gensec_update_done`, and `tldap_gensec_bind_done` alternate between local GENSEC updates and LDAP SASL bind round trips.

## Control flow
Send initializes GENSEC, sets credentials and target identity, applies TLS channel bindings when the LDAP context is already on TLS, requests features, and starts the `GSS-SPNEGO` mechanism. Each GENSEC output token is sent as SASL credentials with empty DN and mechanism `GSS-SPNEGO`. Server SASL credentials become the next GENSEC input. Completion requires both LDAP success and GENSEC success; `TLDAP_SASL_BIND_IN_PROGRESS` and `NT_STATUS_MORE_PROCESSING_REQUIRED` keep the loop alive. Receive verifies requested signing/sealing features and, when negotiated, steals the GENSEC context under the LDAP context and installs a GENSEC tstream over the plain stream.

## State and persistence behavior
Authentication state is transient until receive succeeds. If signing or sealing is negotiated, the GENSEC context persists as a child of the LDAP context because the stream wrapper depends on it. Token blobs are explicitly freed between iterations.

## Dependencies and integration points
It integrates `tldap.c` SASL bind APIs with `auth/gensec`, credentials, `loadparm`, `gensec_tstream`, and TLS channel binding data from `tldap_tls_channel_bindings`.

## Risks and edge cases
The code refuses GENSEC sign/seal over TLS to avoid double wrapping and policy confusion. TLS channel binding setup can fail and is treated as LDAP operations error. A first GENSEC success with no output is treated as invalid credentials. Feature verification after bind is important because the server may authenticate without honoring requested sign/seal.

## Test signals
Coverage is mostly integration-level through LDAP authentication paths that request Kerberos/NTLM SPNEGO, sign/seal, or TLS channel binding. Useful tests should verify TLS plus channel bindings, refusal of sign/seal over TLS, and stream replacement after negotiated wrapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.h -->
# sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.h

## Purpose
This header declares the GENSEC-backed LDAP bind API for source3 users.

## Important APIs, types, and functions
It forward declares `tevent_context`, `tldap_context`, `cli_credentials`, and `loadparm_context`, then exposes async `tldap_gensec_bind_send`, receive `tldap_gensec_bind_recv`, and synchronous `tldap_gensec_bind`. Parameters identify LDAP context, credentials, target service/hostname/principal, loadparm configuration, and requested GENSEC features.

## Control flow
Callers start with the send function in an existing event loop and finish with the recv function, or use the synchronous wrapper which creates and polls a temporary event context.

## State and persistence behavior
The header itself has no state. Its contract permits the implementation to mutate the LDAP context by installing a GENSEC stream when sign or seal is negotiated.

## Dependencies and integration points
It is consumed by LDAP client setup code that wants SPNEGO/SASL authentication without depending on implementation internals.

## Risks and edge cases
Callers must pass target identity accurately for Kerberos service principal selection and must understand that requested sign/seal may alter the active stream.

## Test signals
Compile coverage verifies exported signatures. Integration tests should exercise async and sync paths with different GENSEC feature flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_tls_connect.c -->
# sources/user-network-fs/samba/source3/lib/tldap_tls_connect.c

## Purpose
`tldap_tls_connect.c` upgrades an existing plain tldap connection to TLS using Samba's `tstream_tls_connect` infrastructure.

## Important APIs, types, and functions
`struct tldap_tls_connect_state` stores event context, LDAP context, and TLS parameters. Public APIs are `tldap_tls_connect_send`, `tldap_tls_connect_recv`, and synchronous `tldap_tls_connect`. The implementation callback is `tldap_tls_connect_crypto_done`.

## Control flow
The send function validates that the LDAP connection is still usable, rejects attempts to start TLS after a GENSEC stream is active, obtains the plain tstream, and starts the TLS connect subrequest. On completion, the callback receives the TLS stream and calls `tldap_set_tls_tstream`, which makes it the active LDAP transport.

## State and persistence behavior
Successful upgrade stores the TLS tstream under the LDAP context and switches active transport from plain to TLS. Failures leave the existing stream unchanged and return `TLDAP_CONNECT_ERROR` or `TLDAP_LOCAL_ERROR`.

## Dependencies and integration points
It depends on `tldap.c` stream accessors, Samba TLS tstream code, TLS parameter peer-name logging, and tevent async request conventions. It is used by StartTLS or LDAPS setup flows.

## Risks and edge cases
Attempting TLS over a GENSEC-wrapped connection is rejected because the code expects the raw plain stream as the TLS base. One path returns an unposted request on missing plain stream, which callers must still handle through normal tevent semantics. Certificate and peer-name validation live in the TLS parameter layer, not here.

## Test signals
Useful coverage includes failed upgrade on disconnected contexts, rejection after GENSEC wrapping, successful stream switch, and propagation of TLS handshake errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_tls_connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_tls_connect.h -->
# sources/user-network-fs/samba/source3/lib/tldap_tls_connect.h

## Purpose
This header declares the TLS upgrade API for tldap connections.

## Important APIs, types, and functions
It forward declares `tevent_context`, `tldap_context`, `loadparm_context`, and `tstream_tls_params`, then exposes async `tldap_tls_connect_send`, receive `tldap_tls_connect_recv`, and synchronous `tldap_tls_connect`.

## Control flow
Callers supply an existing tldap context and prepared TLS parameters. Async callers wait for recv; sync callers use the wrapper.

## State and persistence behavior
The header has no state. Implementations may replace the active LDAP stream with a TLS stream on success.

## Dependencies and integration points
It is included by LDAP connection setup code that performs StartTLS or TLS-first LDAP transport creation.

## Risks and edge cases
Consumers must build correct `tstream_tls_params`, including peer name and trust settings, because this API only transports them.

## Test signals
Compile coverage verifies signatures; transport integration tests should validate TLS negotiation and channel binding availability for subsequent GENSEC bind.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_tls_connect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_util.c -->
# sources/user-network-fs/samba/source3/lib/tldap_util.c

## Purpose
`tldap_util.c` supplies convenience helpers around the core tldap client: attribute extraction, SID/GUID/integer conversion, LDAP modify-list construction, formatted search wrappers, rootDSE fetching/caching, control helpers, and RFC2696 paged searches.

## Important APIs, types, and functions
Attribute readers include `tldap_entry_values`, `tldap_get_single_valueblob`, `tldap_talloc_single_attribute`, `tldap_pull_binsid`, `tldap_pull_guid`, `tldap_pull_uint64`, and `tldap_pull_uint32`. Modification builders include `tldap_add_mod_blobs`, `tldap_add_mod_str`, `tldap_make_mod_blob`, and `tldap_make_mod_fmt`. Search utilities include `tldap_search_va`, `tldap_search_fmt`, `tldap_fetch_rootdse[_send/_recv]`, `tldap_rootdse`, `tldap_supports_control`, `tldap_add_control`, `tldap_msg_findcontrol`, and paged search send/recv helpers.

## Control flow
Attribute helpers lazily force `tldap_entry_attributes` parsing and then scan values by case-insensitive attribute name. Modify helpers compare existing single-valued attributes with intended values, deleting the old value before adding the new value to avoid LDAP servers rejecting same-value delete/add pairs. RootDSE fetch performs a base search on `""` with `*` and `+`, requires exactly one entry before the final result, validates DN parsing, and stores the message as context attribute `tldap:rootdse`. Paged search appends a paged-results control, ships a normal search, forwards intermediate entries to callers, then decodes the returned cookie and issues the next page until the cookie is empty.

## State and persistence behavior
RootDSE is cached on the tldap context. Paged search state owns the current cookie, temporary ASN.1 control blob, current result message, and copied server controls. Modify construction allocates talloc-owned arrays under caller-provided memory contexts.

## Dependencies and integration points
The file depends on `tldap.c`, Samba charset conversion, SID/GUID parsing, ASN.1 helpers, `smb_strtoull`, and LDAP paged-results OID constants. Higher-level directory code uses it to build safe modifications and discover server controls.

## Risks and edge cases
`tldap_add_mod_blobs` increments `*pnum_mods` even when appending values to an existing mod, which callers must understand. Multi-valued attributes are not modified by `tldap_make_mod_blob_int`. UTF-8 comparison treats conversion failure as equality, avoiding churn but potentially hiding invalid data. Paged search requires the server to return the paged-results control and treats absence as protocol error.

## Test signals
Targeted tests should cover single and multi-value extraction, SID/GUID decoding, no-op modify detection, rootDSE protocol validation, paged search cookie continuation, and missing paged-results control handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/username.c -->
# sources/user-network-fs/samba/source3/lib/username.c

## Purpose
`username.c` resolves Unix users for Samba by wrapping `getpwnam`, caching passwd records, trying case variants, and honoring `username level` case-combination behavior.

## Important APIs, types, and functions
Public functions are `flush_pwnam_cache`, `get_user_home_dir`, and `Get_Pwnam_alloc`. Internal helpers include `getpwnam_alloc_cached`, `Get_Pwnam_internals`, `uname_string_combinations`, and `uname_string_combinations2`.

## Control flow
`Get_Pwnam_alloc` copies the input into an fstring and calls internals. Resolution tries lowercase first, the original spelling if different, uppercase if different, then combinations with up to `lp_username_level()` uppercase letters. `getpwnam_alloc_cached` checks Samba memcache using a null-terminated string blob key, copies cached passwd data when found, otherwise calls libc `getpwnam`, copies the result into cache, and returns a caller-owned copy. `get_user_home_dir` resolves the user and moves `pw_dir` out of the passwd struct.

## State and persistence behavior
Passwd records are cached in process memory under `GETPWNAM_CACHE`. `flush_pwnam_cache` invalidates that cache. No persistent files are modified.

## Dependencies and integration points
It depends on system passwd APIs, Samba memcache, talloc passwd-copy helpers, loadparm `lp_username_level`, and multibyte-safe case conversion wrappers.

## Risks and edge cases
Case-combination search can become expensive as username level grows. Empty names are rejected. Cache invalidation depends on explicit flush calls when NSS/passwd data changes. Case conversion failure aborts later variants.

## Test signals
Tests should validate cache hit/copy behavior, lower/original/upper lookup order, username-level permutations, empty username rejection, and home directory ownership after moving `pw_dir`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/username.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util.c -->
# sources/user-network-fs/samba/source3/lib/util.c

## Purpose
`util.c` is a broad source3 utility collection. It contains legacy SMB message helpers, path cleanup, process-after-fork reinitialization, account/group conversion helpers, panic-action handling, path/name matching, lock probing, remote client architecture tracking and caching, safe buffer pointer helpers, old OpenX-to-NTCreate mapping, Unix token copying, and directory search attribute filtering.

## Important APIs, types, and functions
Important functions include `set_Protocol`, `gfree_all`, `file_exist_stat`, `socket_exist`, `show_msg`, `set_message_bcc`, `message_push_blob`, `unix_clean_name`, `clean_name`, `write_data_at_offset`, `init_before_fork`, `parent_watch_fd`, `reinit_after_fork`, `add_to_large_array`, `uidtoname`, `gidtoname`, `nametouid`, `nametogid`, `smb_panic_s3`, `is_in_path`, `fcntl_getlock`, `map_process_lock_to_ofd_lock`, `is_myname`, remote-architecture getters/setters/cache functions, `set_maxfiles`, `smb_xmalloc_array`, `myhostname`, `parent_dirname`, `ms_has_wild`, `mask_match`, `is_offset_safe`, `get_safe_str_ptr`, `split_domain_user`, `map_open_params_to_ntcreate`, `copy_unix_token`, `root_unix_token`, and `dir_check_ftype`.

## Control flow
Fork setup creates a pipe before fork; children close the write end, reinitialize tdb, tevent tracing, messaging, and CTDB async context, then watch the read end so EOF terminates child processes when the parent exits. Remote architecture flow sets a global enum from LanMan strings or cache entries keyed by client GUID, using root privilege for gencache access. Open mapping translates DOS deny/open modes into NT access, share mode, create disposition, options, and private deny flags. Path utilities normalize `.` and `..`, parse parent/name components, and perform Microsoft wildcard matching using the configured SMB protocol.

## State and persistence behavior
Process-global state includes `Protocol`, remote architecture `ra_type`, cached hostname strings, and fork pipe file descriptors. Remote architecture data is persisted in Samba gencache for seven days. Some helpers temporarily become root for panic action or gencache updates. Other functions operate only on caller-owned buffers or talloc allocations.

## Dependencies and integration points
The file integrates with loadparm, char conversion, interfaces, debug/memcache cleanup, TDB/CTDB, messaging, server ID databases, gencache, passwd/group APIs, SMB protocol field macros, locking syscalls, wildcard matching, and security token definitions. It is shared across smbd, winbindd, client, and VFS-facing code.

## Risks and edge cases
This file has high blast radius because many helpers are old compatibility surfaces. SMB message functions assume valid SMB1 buffer layout. `add_to_large_array` signals allocation failure by setting array size to `-1`. Remote architecture cache requires privilege transitions and validates null-terminated cache blobs. `is_offset_safe` must catch pointer arithmetic wrap. `map_open_params_to_ntcreate` encodes subtle DOS deny semantics, especially executable handling under `DENY_DOS`.

## Test signals
Useful coverage includes fork reinit behavior, open-mode mapping matrices, path cleanup edge cases, wildcard protocol behavior, safe-buffer wrap checks, remote arch cache set/get/delete, file lock probing, and directory attribute filtering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_builtin.c -->
# sources/user-network-fs/samba/source3/lib/util_builtin.c

## Purpose
`util_builtin.c` maps Windows BUILTIN domain RIDs to names and provides predicates for BUILTIN SIDs.

## Important APIs, types, and functions
`struct rid_name_map` and `builtin_aliases` define known built-in aliases such as Administrators, Users, Guests, Backup Operators, Remote Desktop Users, and Event Log Readers. Public APIs are `lookup_builtin_rid`, `lookup_builtin_name`, `builtin_domain_name`, `sid_check_is_builtin`, `sid_check_is_in_builtin`, and `sid_check_is_wellknown_builtin`.

## Control flow
Lookup functions linearly scan the static alias table. SID predicates compare the full SID with `global_sid_Builtin`, or copy and split the RID before checking domain and known RID membership.

## State and persistence behavior
All data is static and read-only. Returned names from RID lookup are talloc duplicates owned by the caller.

## Dependencies and integration points
The file depends on Samba security SID helpers and global SID constants. It feeds passdb, access checks, id mapping, and SID/name display logic.

## Risks and edge cases
The alias table must stay aligned with Windows well-known BUILTIN RIDs. `sid_check_is_in_builtin` treats any SID under S-1-5-32 as in BUILTIN, while `sid_check_is_wellknown_builtin` restricts to table entries.

## Test signals
Tests should verify bidirectional RID/name lookup, case-insensitive name matching, domain SID checks, and unknown RID rejection by `sid_check_is_wellknown_builtin`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_builtin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_cluster.c -->
# sources/user-network-fs/samba/source3/lib/util_cluster.c

## Purpose
`util_cluster.c` checks whether CTDB clustering is reachable when Samba is configured for clustering.

## Important APIs, types, and functions
The only exported function is `cluster_probe_ok`.

## Control flow
If `lp_clustering()` is false, the function returns true. If clustering is enabled, it calls `ctdbd_probe` with configured CTDB socket and timeout. A nonzero return logs a level-0 error and returns false.

## State and persistence behavior
No state is stored. The function only probes external CTDB daemon reachability.

## Dependencies and integration points
It depends on CTDB connection helpers, loadparm clustering settings, debug logging, and cluster support configuration. Startup or health-check paths use it to refuse clustered operation when CTDB is unavailable.

## Risks and edge cases
Probe failures may reflect socket path, timeout, daemon startup order, or permissions rather than permanent misconfiguration. The function is intentionally binary and does not retry.

## Test signals
Tests can mock `lp_clustering` and `ctdbd_probe` to validate no-op noncluster mode, success, and logged failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_cluster.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_cluster.h -->
# sources/user-network-fs/samba/source3/lib/util_cluster.h

## Purpose
This header declares the source3 cluster utility probe API.

## Important APIs, types, and functions
It exposes `bool cluster_probe_ok(void)`.

## Control flow
Callers use the function as a startup or preflight predicate before assuming CTDB-backed clustering is available.

## State and persistence behavior
The header has no state.

## Dependencies and integration points
It isolates users from CTDB-specific include requirements in `util_cluster.c`.

## Risks and edge cases
The boolean return hides probe details; callers needing diagnostics must rely on logging from the implementation.

## Test signals
Compile coverage verifies the declaration. Functional tests belong to `util_cluster.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_cluster.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_ea.c -->
# sources/user-network-fs/samba/source3/lib/util_ea.c

## Purpose
`util_ea.c` parses SMB extended attribute buffers into Samba `ea_list` structures.

## Important APIs, types, and functions
Public functions are `read_ea_list_entry` for one EA entry and `read_nttrans_ea_list` for NT transact EA lists.

## Control flow
`read_ea_list_entry` validates minimum header length, reads flags/name length/value length, checks bounds, requires a null-terminated ASCII EA name, converts the name, allocates a value blob with an extra null byte, copies the value, and reports bytes consumed. `read_nttrans_ea_list` walks an EA list where each item is preceded by a next-offset field, appends parsed entries with `DLIST_ADD_END`, and stops on zero next offset.

## State and persistence behavior
The functions allocate talloc-owned in-memory lists only. They do not read or write filesystem EAs.

## Dependencies and integration points
The file depends on SMB byte macros, talloc, ASCII pull conversion, `DATA_BLOB`, debug dumping, and the `ea_list` type used by SMB transaction handling.

## Risks and edge cases
Bounds checks protect against truncated buffers and integer wrap while advancing offsets. Name conversion failure logs but still relies on `eal->ea.name` being non-null for success. Value blobs are null-padded for safe debug printing, but the stored length excludes the terminator.

## Test signals
Tests should cover truncated headers, non-null-terminated names, value bounds, multiple-entry next-offset traversal, zero offset termination, and wrap-protection branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_ea.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_ea.h -->
# sources/user-network-fs/samba/source3/lib/util_ea.h

## Purpose
This header declares SMB extended attribute buffer parsing helpers.

## Important APIs, types, and functions
It exposes `read_ea_list_entry` and `read_nttrans_ea_list`, both returning `struct ea_list *` allocated under a caller-provided talloc context.

## Control flow
Callers parse one entry when they track offsets themselves or parse a complete NT transact EA list in one call.

## State and persistence behavior
The header has no state and promises in-memory parse results only.

## Dependencies and integration points
It is included by SMB server request code that decodes client-supplied EA buffers.

## Risks and edge cases
Callers must treat NULL returns as malformed input or allocation failure and avoid partially using an EA list.

## Test signals
Compile coverage verifies prototypes; parser behavior is covered through `util_ea.c` tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_ea.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_event.c -->
# sources/user-network-fs/samba/source3/lib/util_event.c

## Purpose
`util_event.c` implements a repeating idle timer helper around `tevent`.

## Important APIs, types, and functions
`struct idle_event` stores the current timer, interval, debug name, callback, and private data. Public API `event_add_idle` allocates and schedules the event. `smbd_idle_event_handler` invokes and reschedules it.

## Control flow
`event_add_idle` schedules the first timer for current time plus interval. When fired, the handler frees the old timer, calls the user callback, frees the entire idle event if the callback returns false, or schedules a new timer at `now + interval` if true.

## State and persistence behavior
The idle event is talloc-owned under the caller's memory context and persists only while callbacks continue returning true. No persistent state is written.

## Dependencies and integration points
It depends on `tevent`, timeval helpers, talloc, SMB assertions, and debug logging. smbd-style event loops use it for periodic housekeeping.

## Risks and edge cases
Reschedule allocation failure triggers an assertion. Callback code controls lifetime by boolean return and must be safe to run from the event loop.

## Test signals
Tests should verify initial scheduling, repeated callbacks, stopping on false, and cleanup behavior when the event talloc context is freed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_file.c -->
# sources/user-network-fs/samba/source3/lib/util_file.c

## Purpose
`util_file.c` asynchronously runs a command and reads its output into memory with a maximum-size guard.

## Important APIs, types, and functions
`struct file_ploadv_state` tracks event context, read subrequest, maximum size, process-output fd, and accumulated buffer. Public APIs are `file_ploadv_send` and `file_ploadv_recv`; callback `file_ploadv_readable` drains output.

## Control flow
Send starts the process with `sys_popenv`, installs cleanup to close it, waits for fd readability, reads chunks of 1024 bytes, reallocates a null-terminated talloc buffer, enforces overflow and max-size checks, and waits again until EOF. Receive returns Unix error codes or moves the buffer to the caller.

## State and persistence behavior
Runtime state includes the child process pipe and accumulated output buffer. Cleanup closes the process fd with `sys_pclose`. No file state is persisted.

## Dependencies and integration points
It depends on async socket readability helpers, `sys_popenv`, `sys_read`, `sys_pclose`, talloc, tevent, and Samba utility error conventions. It supports code that needs command output without blocking the event loop.

## Risks and edge cases
Large output can return `EMSGSIZE`; integer wrap is explicitly checked. EOF completes successfully even with an empty buffer. Cleanup must run on cancellation to avoid process/fd leaks.

## Test signals
Tests should cover command-start failure, normal small output, empty output, max-size breach, read errors, cancellation cleanup, and null terminator handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_file.h -->
# sources/user-network-fs/samba/source3/lib/util_file.h

## Purpose
This header declares the async process-output loading helper.

## Important APIs, types, and functions
It exposes `file_ploadv_send` and `file_ploadv_recv`. The send function takes an argv vector and max output size. The recv function returns an error code and moves a `uint8_t *` buffer to the caller.

## Control flow
Callers start the request on a tevent context, wait for completion, and call recv once.

## State and persistence behavior
The header carries no state. Runtime state belongs to the request implementation.

## Dependencies and integration points
It includes `replace.h` and `<tevent.h>` so consumers can compile against `struct tevent_req`.

## Risks and edge cases
Callers must treat nonzero recv return as an errno-style failure and should respect max-size limits for untrusted commands.

## Test signals
Compile coverage plus behavioral tests in `util_file.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_macstreams.c -->
# sources/user-network-fs/samba/source3/lib/util_macstreams.c

## Purpose
`util_macstreams.c` identifies Apple AFP metadata/resource stream names.

## Important APIs, types, and functions
Public functions are `is_afpinfo_stream`, `is_afpresource_stream`, and `is_apple_stream`.

## Control flow
Each specific predicate null-checks the stream name and performs prefix comparison against `AFPINFO_STREAM_NAME` or `AFPRESOURCE_STREAM_NAME` using plain `strncasecmp`. `is_apple_stream` returns true if either specific predicate matches.

## State and persistence behavior
No state is kept. The functions are pure string predicates.

## Dependencies and integration points
It depends on `MacExtensions.h` constants and is used by VFS/streams code that treats Apple metadata streams specially.

## Risks and edge cases
The prefix comparison intentionally ignores multibyte string wrappers. Because it checks only the prefix length, callers must decide whether suffixes are acceptable for their stream syntax.

## Test signals
Tests should cover null input, exact AFP info/resource names, case-insensitive names, prefixed names, and non-Apple streams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_macstreams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_macstreams.h -->
# sources/user-network-fs/samba/source3/lib/util_macstreams.h

## Purpose
This header declares Apple stream classification helpers.

## Important APIs, types, and functions
It exposes `is_afpinfo_stream`, `is_afpresource_stream`, and `is_apple_stream`.

## Control flow
Consumers call the specific predicates or the aggregate predicate when handling named streams.

## State and persistence behavior
The header has no state.

## Dependencies and integration points
It provides a narrow API for VFS and SMB stream handling code without exposing `MacExtensions.h` details.

## Risks and edge cases
The implementation's prefix semantics should be understood by callers that require exact stream-name matching.

## Test signals
Compile coverage and the string predicate tests described for `util_macstreams.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_macstreams.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_malloc.c -->
# sources/user-network-fs/samba/source3/lib/util_malloc.c

## Purpose
`util_malloc.c` provides Samba allocation wrappers, including optional paranoid wrappers that prevent direct malloc/realloc usage and a `Realloc` helper with explicit old-pointer ownership behavior.

## Important APIs, types, and functions
Under `PARANOID_MALLOC_CHECKER`, `malloc_` and internal `realloc_` call the real libc functions while macros poison direct calls. Public `Realloc` expands or frees memory depending on `size` and `free_old_on_error`.

## Control flow
`Realloc` returns NULL for zero size and optionally frees the old pointer. For nonzero size it calls malloc or realloc, using paranoid wrappers when enabled. On allocation failure it optionally frees the old pointer and logs an error.

## State and persistence behavior
No persistent state is used. The function's key state effect is whether it frees the input pointer on failure or zero size.

## Dependencies and integration points
It depends on Samba memory macros, debug logging, and build-time `PARANOID_MALLOC_CHECKER`. Legacy code uses it through `SMB_REALLOC`-style macros.

## Risks and edge cases
The ownership mode is critical: using the freeing variant in code that expects to preserve old contents can cause use-after-free. Zero-size requests are treated as errors/logged and may free the pointer.

## Test signals
Tests should cover NULL input, successful resize, zero-size behavior for both ownership modes, simulated allocation failure, and paranoid checker builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_malloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_matching.c -->
# sources/user-network-fs/samba/source3/lib/util_matching.c

## Purpose
`util_matching.c` builds reusable path-last-component matchers from slash-separated name lists, supporting Samba Microsoft wildcard matching or POSIX regex matching with one capture group.

## Important APIs, types, and functions
Opaque `struct samba_path_matching` contains case sensitivity, a matching function pointer, entry count, and entries. Entries store name, wildcard flag, or compiled regex. Public constructors are `samba_path_matching_mswild_create` and `samba_path_matching_regex_sub1_create`; matcher API is `samba_path_matching_check_last_component`.

## Control flow
`samba_path_matching_split` performs two passes over a slash-separated list, ignoring empty components, to allocate and copy entries. The mswild constructor marks entries containing Microsoft wildcard characters and uses `mask_match` or string comparison. The regex constructor compiles every entry and requires exactly one subexpression; it installs a destructor to `regfree` compiled patterns. The check function extracts the last path component, scans entries in order, and returns the first match index plus replacement offsets for regex capture group 1.

## State and persistence behavior
Matchers are talloc-owned and persist until freed. Regex resources are released by the talloc destructor. No external state is persisted.

## Dependencies and integration points
It depends on Samba path/string wrappers, `mask_match`, `ms_has_wild`, POSIX regex, NTSTATUS, and talloc. It is useful for VFS rules that match or rewrite filename components.

## Risks and edge cases
Regex mode rejects patterns with zero or more than one capture group. Replacement offsets are relative to the whole input name, not just the last component. Empty name lists create a valid matcher with no entries and no match. Constructor cleanup must avoid leaking partially compiled regexes.

## Test signals
Tests should cover repeated slashes, empty lists, case-sensitive and insensitive mswild matches, regex capture offset calculation, invalid regexes, invalid capture counts, and first-match ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_matching.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_matching.h -->
# sources/user-network-fs/samba/source3/lib/util_matching.h

## Purpose
This header declares the opaque path matching API.

## Important APIs, types, and functions
It forward declares `struct samba_path_matching` and exposes constructors for Microsoft wildcard and regex-substitution modes plus `samba_path_matching_check_last_component`.

## Control flow
Callers create a matcher once from a name list, then call the check function for paths. Regex mode additionally returns capture replacement offsets.

## State and persistence behavior
The matcher object is allocated under caller-provided talloc memory and owns parsed entries and compiled regex state.

## Dependencies and integration points
It is included by code that wants a stable matching abstraction without knowing whether mswild or regex is used internally.

## Risks and edge cases
Callers must free the matcher to release regex resources and must handle `match_idx == -1` as no match, even when NTSTATUS is OK.

## Test signals
Compile coverage plus constructor and match behavior tests in `util_matching.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_matching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_namearray.c -->
# sources/user-network-fs/samba/source3/lib/util_namearray.c

## Purpose
`util_namearray.c` parses slash-separated name lists into `name_compare_entry` arrays and checks whether security tokens contain users/groups/netgroups named by configured expressions.

## Important APIs, types, and functions
Public functions include `token_contains_name`, `append_to_namearray`, and `set_namearray`. Internal `do_group_checks` interprets name prefixes: direct user, `@` netgroup then Unix group, `&` netgroup, `+` Unix/domain group, and combined `+&`/`&+` order. `namearray_len` finds the terminator.

## Control flow
`token_contains_name` applies user/domain/share substitutions, recognizes literal SID strings, resolves direct names through `lookup_name_smbconf_ex`, validates expected SID type, and checks token SIDs. Group-prefixed names iterate requested lookup modes: `+` resolves groups and checks token SID membership; `&` calls `user_in_netgroup`. Name-array parsing converts `/` to string-vector separators via `path_to_strv`, skips empty components, appends entries, and precomputes `is_wild` using `ms_has_wild`.

## State and persistence behavior
Functions allocate talloc-owned arrays and substituted strings. No persistent state is modified.

## Dependencies and integration points
It depends on loadparm winbind separator, talloc substitution helpers, passdb/name lookup, netgroup checks, security tokens, SID type utilities, `path_to_strv`, and wildcard helpers. It feeds share access and path include/exclude style checks.

## Risks and edge cases
Name substitutions can fail allocation. Direct names that resolve to non-user SID types return success with no match but log a warning. Group lookup failures return false, distinguishing lookup error from no match. Prefix ordering matters for combined netgroup/group syntax.

## Test signals
Tests should cover all prefixes, domain stripping from usernames, `%S` substitution, direct SID matching, non-user/non-group type warnings, repeated slash parsing, wildcard flag precomputation, and append versus reset behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_namearray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_names.c -->
# sources/user-network-fs/samba/source3/lib/util_names.c

## Purpose
`util_names.c` chooses Samba's default account domain/name context and enforces allowed-domain policy.

## Important APIs, types, and functions
Public APIs are `get_global_sam_name`, `my_sam_name`, and `is_allowed_domain`.

## Control flow
`get_global_sam_name` returns workgroup for a DC and NetBIOS name otherwise. `my_sam_name` returns NetBIOS name in standalone role and workgroup otherwise. `is_allowed_domain` first rejects domains matching `winbind:ignore domains`, then allows all trusted domains when configured, or only the local workgroup and local NetBIOS names when trusted domains are disabled.

## State and persistence behavior
No state is stored. Results reflect current loadparm configuration.

## Dependencies and integration points
It depends on server role macros, loadparm workgroup/netbios/trusted-domain settings, wildcard matching, and `is_myname`. It is used by authentication, winbind, and account resolution code.

## Risks and edge cases
Ignored-domain patterns take precedence over trusted-domain allowance. `is_myname` includes aliases and NetBIOS-length comparison semantics from `util.c`.

## Test signals
Tests should cover DC/standalone/member return values, ignored-domain pattern matching, trusted-domain allow-all mode, and local workgroup/name fallback mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_names.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_nscd.c -->
# sources/user-network-fs/samba/source3/lib/util_nscd.c

## Purpose
`util_nscd.c` wraps optional NSCD cache flushing for passwd and group services.

## Important APIs, types, and functions
Public functions are `smb_nscd_flush_user_cache` and `smb_nscd_flush_group_cache`. Internal `smb_nscd_flush_cache` calls `nscd_flush_cache` only when build-time support exists.

## Control flow
User and group flush functions pass `"passwd"` or `"group"` to the internal helper. If `HAVE_NSCD_FLUSH_CACHE` is unavailable, the helper is a no-op. If flushing fails, it logs at debug level 10.

## State and persistence behavior
It affects external NSCD process caches when supported. Samba keeps no local state here.

## Dependencies and integration points
The file conditionally depends on `<libnscd.h>` and NSCD APIs. It is used after passwd/group changes so NSS cache data does not stay stale.

## Risks and edge cases
Failure logging is low severity because NSCD may not be running. Build configurations without NSCD support silently no-op.

## Test signals
Tests can compile both with and without NSCD support and mock flush failures to validate service names and logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_nscd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_nttoken.c -->
# sources/user-network-fs/samba/source3/lib/util_nttoken.c

## Purpose
`util_nttoken.c` contains small security token helpers moved out of auth code to reduce linker dependencies.

## Important APIs, types, and functions
Public functions are `merge_with_system_token` and `token_sid_in_ace`.

## Control flow
`merge_with_system_token` validates parameters, allocates a new token, adds all SIDs from the input token and the system token uniquely, ORs privilege and rights masks from both, and returns the merged token. Claims are not merged because the system token has none. `token_sid_in_ace` scans token SIDs for equality with an ACE trustee.

## State and persistence behavior
The merge result is talloc-owned by the caller. No global state is changed, though `get_system_token` supplies shared system token data.

## Dependencies and integration points
It depends on Samba security token/SID helpers and is used by access-check paths that need to include system privileges.

## Risks and edge cases
Allocation or SID append failure frees the partial token and returns NTSTATUS. The merge deliberately ignores claims, which is safe only while the system token has no claims.

## Test signals
Tests should cover NULL parameters, duplicate SID suppression, privilege/right mask union, allocation failure handling, and ACE trustee matching.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_nttoken.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_path.c -->
# sources/user-network-fs/samba/source3/lib/util_path.c

## Purpose
`util_path.c` builds configured Samba state/lock/cache paths, canonicalizes absolute POSIX paths, extracts Windows previous-version `@GMT-` snapshot tokens, tests parent/subdirectory relationships, and converts slash-separated paths to string vectors.

## Important APIs, types, and functions
Public APIs are `lock_path`, `state_path`, `cache_path`, `canonicalize_absolute_path`, `clistr_is_previous_version_path`, `extract_snapshot_token`, `clistr_smb2_extract_snapshot_token`, `subdir_of`, and `path_to_strv`. Internal helpers include `xx_path`, `find_snapshot_token`, and `extract_snapshot_token_internal`.

## Control flow
Path builders trim trailing slashes from configured root directories, ensure the directory exists with mode 0755, and append the requested name. Canonicalization always emits an absolute path, collapses duplicate slashes, removes `.` components, and handles `..` without escaping above root. Snapshot detection finds a path-component-starting `@GMT-%Y.%m.%d-%H.%M.%S` token, converts it via `timegm` to NTTIME, and optionally removes the component from the path. `subdir_of` compares normalized absolute strings and returns the relative suffix.

## State and persistence behavior
Path builders may create lock/state/cache directories. Other functions allocate or mutate caller-provided strings only.

## Dependencies and integration points
It depends on loadparm directories, `directory_create_or_exist`, Samba time conversion, string wrappers, and talloc. It is used by server file paths, shadow-copy/previous-version handling, and name-list parsing.

## Risks and edge cases
`canonicalize_absolute_path` treats any input as absolute by prepending `/`. Snapshot token parsing requires the token to be a complete path component and uses different separators for POSIX and SMB2 client paths. `subdir_of` assumes both inputs begin with `/` and asserts otherwise.

## Test signals
Tests should cover empty path canonicalization, root-preserving `..`, duplicate separators, invalid and valid `@GMT-` tokens, token removal, parent with trailing slash, root parent behavior, and path-to-strv empty components.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_path.h -->
# sources/user-network-fs/samba/source3/lib/util_path.h

## Purpose
This header declares source3 path utilities and the Windows previous-version timestamp format constants.

## Important APIs, types, and functions
It defines `GMT_NAME_LEN` and `GMT_FORMAT`, then declares `lock_path`, `state_path`, `cache_path`, `canonicalize_absolute_path`, snapshot-token helpers, `clistr_is_previous_version_path`, `subdir_of`, and `path_to_strv`.

## Control flow
Consumers call these functions for configured directory path construction, path normalization, previous-version parsing, and slash-list splitting.

## State and persistence behavior
The header has no state. Implementations may create configured directories or mutate token-containing path strings.

## Dependencies and integration points
It includes talloc and Samba time types, and is shared by VFS, configuration, and matching utilities.

## Risks and edge cases
Callers must pass mutable strings to extraction functions and absolute paths to `subdir_of`.

## Test signals
Compile coverage plus behavioral tests in `util_path.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_procid.c -->
# sources/user-network-fs/samba/source3/lib/util_procid.c

## Purpose
`util_procid.c` converts between OS PIDs and Samba `server_id` process identifiers, including cluster virtual node number state.

## Important APIs, types, and functions
Public functions are `procid_to_pid`, `set_my_vnn`, `get_my_vnn`, `pid_to_procid`, `procid_valid`, and `procid_is_local`. Static global `my_vnn` defaults to `NONCLUSTER_VNN`.

## Control flow
`pid_to_procid` asks messaging datagram code for a per-process unique ID, logs on failure, and returns a `server_id` with pid, unique ID, and current VNN. Locality compares a server ID's VNN with `my_vnn`.

## State and persistence behavior
The only local state is process-global `my_vnn`. Unique IDs come from the messaging datagram subsystem.

## Dependencies and integration points
It depends on `server_id` generated headers, debug logging, and messaging datagram unique-id helpers. It is used by messaging, locking, and process tracking code.

## Risks and edge cases
`procid_valid` only checks for pid not equal to `(uint64_t)-1`; it does not verify process liveness. If unique-id lookup fails, the returned ID has zero unique ID and may be less collision-resistant.

## Test signals
Tests should cover VNN set/get, local versus remote IDs, invalid sentinel PID, pid extraction, and behavior when unique ID lookup fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_procid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_procid.h -->
# sources/user-network-fs/samba/source3/lib/util_procid.h

## Purpose
This header declares Samba process-ID conversion helpers.

## Important APIs, types, and functions
It includes `server_id.h` and declares PID/VNN conversion and predicate functions.

## Control flow
Callers convert PIDs to `server_id` before interacting with messaging/locking subsystems and test validity/locality as needed.

## State and persistence behavior
The header has no state. Implementation maintains process-global VNN.

## Dependencies and integration points
It exposes source3 process identity to code that should not directly know the implementation's VNN storage.

## Risks and edge cases
Callers should not equate `procid_valid` with live process checks.

## Test signals
Compile coverage plus functional tests in `util_procid.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_procid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sd.c -->
# sources/user-network-fs/samba/source3/lib/util_sd.c

## Purpose
`util_sd.c` converts security descriptors and ACEs between Samba security structures and human-readable text, with optional remote LSA SID/name lookup through an SMB client connection.

## Important APIs, types, and functions
Permission maps `special_values` and `standard_values` translate compact strings like `R`, `W`, `FULL`, and `CHANGE` to access masks. Public APIs include `SidToString`, `StringToSid`, `print_ace`, `parse_ace`, and `sec_desc_print`. Internal helpers `cli_lsa_lookup_sid` and `cli_lsa_lookup_name` temporarily connect to `IPC$` and use LSARPC for name/SID resolution. `print_ace_flags`, `parse_ace_flags`, and `print_acl_ctrl` handle ACE flags and descriptor control flags.

## Control flow
SID-to-string first emits numeric SID and, when allowed and a client is supplied, resolves the SID through LSARPC and formats `DOMAIN<separator>name`. String-to-SID accepts numeric SID text first, otherwise resolves through remote LSA. `print_ace` emits trustee, type, flags, and either standard permission name, compact special permission letters, or hex mask. `parse_ace` tokenizes `sid:type/flags/mask`, resolves trustee, parses type and flags, maps standard or compact permission strings, then initializes a security ACE. `sec_desc_print` prints revision, control bits, owner, group, and DACL ACEs.

## State and persistence behavior
Remote lookup temporarily changes the client tree connection to `IPC$`, then disconnects and restores the original tree/share. No descriptors are persisted.

## Dependencies and integration points
The file depends on SMB client state, LSARPC generated stubs, RPC pipe helpers, security descriptor/SID helpers, loadparm winbind separator, and standard FILE/SEC access constants. It is used by command-line tools and diagnostics that display or parse ACLs.

## Risks and edge cases
Tree connection restore is critical so callers do not lose their original share context. Parsing prints errors to stdout and returns false, which is suitable for tools but not quiet library callers. Only allowed/denied ACE types are accepted in numeric/hex type parsing. Control-bit string `SR` is reused by two meanings in the table, so display can be ambiguous.

## Test signals
Tests should cover numeric and remote SID lookup, ACE print/parse round trips for standard and special permissions, bad flags/masks, descriptor printing, and preservation of client tcon state after lookup failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sec.c -->
# sources/user-network-fs/samba/source3/lib/util_sec.c

## Purpose
`util_sec.c` abstracts Unix credential manipulation for Samba. It records startup credentials, gains/drops root privilege, switches effective IDs, saves/restores real/effective IDs, permanently becomes a user, supports Linux thread-specific credentials, and includes autoconf self-test code for setuid mechanisms.

## Important APIs, types, and functions
Public APIs include `sec_init`, `sec_initial_uid`, `sec_initial_gid`, `root_mode`, `non_root_mode`, `gain_root_privilege`, `gain_root_group_privilege`, `set_effective_uid`, `set_effective_gid`, `save_re_uid`, `restore_re_uid_fromroot`, `restore_re_uid`, `save_re_gid`, `restore_re_gid`, `set_re_uid`, `become_user_permanently`, `set_thread_credentials`, and `is_setuid_root`. Internal `assert_uid` and `assert_gid` panic on failed transitions when running root mode.

## Control flow
`sec_init` captures initial effective UID/GID, with UID wrapper handling for tests. Credential setters compile to the platform-supported mechanism: `setresuid`, `seteuid`, `setreuid`, or `setuidx`. Root gain sets real/effective IDs to zero where possible and asserts success. Effective setters drop only effective identity where supported. Permanent become first regains root, then sets real/effective/saved IDs and group IDs to the target so root cannot be regained. Linux thread credentials reset to root, set primary and supplementary groups, then set target UID, with a thread-local cache to skip repeated identical transitions.

## State and persistence behavior
Process-global state includes initial UID/GID and saved real/effective UID/GID pairs. With Linux thread credentials and `__thread`, each thread caches the last credential set. The code mutates OS process or thread credentials, a high-impact state change.

## Dependencies and integration points
It depends on Samba setid wrappers, uid-wrapper test integration, platform configure macros, and privilege-changing callers throughout smbd/winbindd/VFS code.

## Risks and edge cases
Credential code is security critical and platform-dependent. Assertions intentionally panic in root mode when requested IDs do not take effect. Non-root mode suppresses some panics to support tests and non-root smbd. Thread-credential caching assumes the gidset pointer identity is a valid cache key; mutated group arrays at the same address would be risky.

## Test signals
The `AUTOCONF_TEST` main exercises selected platform setid calls. Runtime tests should verify root/non-root mode, save/restore pairs, permanent drop irreversibility, Linux thread credential group setting, uid-wrapper behavior, and EAGAIN handling for per-user process limits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid.c -->
# sources/user-network-fs/samba/source3/lib/util_sid.c

## Purpose
`util_sid.c` provides SID serialization, filtering, token SID-array construction from Netlogon info3 data, and Samba NPA flag helpers.

## Important APIs, types, and functions
Public functions include `sid_to_fstring`, `sid_linearize`, `non_mappable_sid`, `sid_binstring_hex_talloc`, `sid_array_from_info3`, `security_token_find_npa_flags`, and `security_token_del_npa_flags`.

## Control flow
SID string and binary helpers use Samba NDR and SID formatting routines. `non_mappable_sid` checks whether a SID belongs to BUILTIN or NT Authority domains. `sid_array_from_info3` optionally adds the user SID, always adds primary group SID, adds supplemental group RIDs, then copies extra SIDs while skipping asserted identity SIDs to avoid privilege elevation. NPA helpers count flag SIDs under `global_sid_Samba_NPA_Flags`, extract the RID as flags, or remove the flag SID from a token.

## State and persistence behavior
Functions allocate caller-owned talloc arrays/strings or mutate the supplied security token when deleting NPA flags. No persistent state is written.

## Dependencies and integration points
It depends on generated NDR security/netlogon types, SID helpers, special SID predicates, token SID-array utilities, and string wrappers. Authentication and idmap code use it when building tokens from domain logon responses.

## Risks and edge cases
SID composition failures return invalid parameter. Extra SID filtering is important for security. `security_token_del_npa_flags` asserts exactly one NPA flag SID, so callers must check or guarantee presence first.

## Test signals
Tests should cover NDR linearization buffer sizing, non-mappable domain checks, info3 SID array construction with and without user SID, duplicate primary/additional groups, asserted identity filtering, and NPA flag find/delete behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid_passdb.c -->
# sources/user-network-fs/samba/source3/lib/util_sid_passdb.c

## Purpose
`util_sid_passdb.c` decides whether a SID or SID domain should be handled by Samba passdb/idmapping according to configured passdb responsibility.

## Important APIs, types, and functions
Public APIs are `sid_check_object_is_for_passdb` for object SIDs and `sid_check_is_for_passdb` for object-or-domain SIDs.

## Control flow
Both functions test SID families in priority order: our SAM, BUILTIN, well-known domain, Unix users, Unix groups, and a catch-all responsibility. The object-only function checks in-domain object predicates; the broader function also accepts exact domain SIDs such as our SAM, BUILTIN, well-known, Unix users, and Unix groups.

## State and persistence behavior
The functions are pure predicates over input SID and passdb responsibility state. They do not modify passdb.

## Dependencies and integration points
They depend on special SID predicates, machine SID helpers, Unix SID helpers, and passdb responsibility flags such as `pdb_is_responsible_for_builtin`. Idmap and account lookup code use them to route SID handling.

## Risks and edge cases
Ordering matters when the catch-all responsibility is enabled because it returns true for otherwise unrecognized SIDs. Object-only versus domain-inclusive semantics must be chosen correctly by callers.

## Test signals
Tests should cover each SID family with corresponding responsibility flag enabled/disabled, exact domain SID versus object SID behavior, and the everything-else fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid_passdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid_passdb.h -->
# sources/user-network-fs/samba/source3/lib/util_sid_passdb.h

## Purpose
This header declares passdb SID responsibility predicates.

## Important APIs, types, and functions
It exposes `sid_check_object_is_for_passdb` and `sid_check_is_for_passdb`.

## Control flow
Callers use the object-only predicate for concrete account/group SID ownership and the broader predicate when domain SIDs are also valid inputs.

## State and persistence behavior
The header has no state. Implementation reads passdb responsibility configuration.

## Dependencies and integration points
It gives idmap/passdb consumers a small API without pulling in the responsibility logic implementation.

## Risks and edge cases
Using the broader predicate where only object SIDs are expected can route domain SIDs into object-handling code.

## Test signals
Compile coverage plus family/responsibility matrix tests in `util_sid_passdb.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid_passdb.h -->
