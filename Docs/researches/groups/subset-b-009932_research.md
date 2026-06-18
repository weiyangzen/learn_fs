# Research: subset-b-009932

Grouped source research for Samba `source4/libcli` files. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/composite/composite.c -->
# sources/user-network-fs/samba/source4/libcli/composite/composite.c

Purpose: implements the small "composite" async helper layer used by older Samba4 client code to expose multi-step async operations as one context with a synchronous wait option. It allocates `struct composite_context`, tracks completion/error state, waits on a `tevent_context`, and wires continuations for nested composite, SMB1, SMB2, and NBT requests.

Important APIs: `composite_create()`, `composite_wait()`, `composite_wait_free()`, `composite_error()`, `composite_done()`, `composite_nomem()`, `composite_is_ok()`, `composite_continue()`, `composite_continue_smb()`, `composite_continue_smb2()`, and `composite_continue_nbt()`. `composite_trigger()` is an internal zero-time timer callback used when an operation completes before the caller has installed `async.fn`.

Control flow and state: callers allocate a context in `COMPOSITE_STATE_IN_PROGRESS`, attach continuation callbacks, and eventually call done or error. `composite_wait()` marks `used_wait` and repeatedly calls `tevent_loop_once()` until state reaches `COMPOSITE_STATE_DONE` or `COMPOSITE_STATE_ERROR`. The continuation helpers set child request callbacks and propagate immediate child failure to the parent.

State and persistence: state is entirely in-memory, talloc-owned, and event-loop driven. There is no disk persistence. The subtle persistent behavior is callback scheduling: if neither synchronous wait nor callback is active at completion time, the code schedules a zero-time timer under the context so the eventual caller can still receive notification.

Dependencies and integration: depends on tevent, talloc, NTSTATUS, SMB1 `smbcli_request`, SMB2 `smb2_request`, and NBT name requests. It is used by connection, resolver, and other older libcli APIs that predate `tevent_req`.

Risks: null `event_ctx` would make wait/trigger paths unsafe for callers that did not initialize correctly. Early completion behavior depends on the context staying alive until the zero-time timer fires. `composite_continue_smb*()` only detects requests already beyond receive state; later errors remain callback responsibility. Test signals include async operations that complete immediately, callback-after-completion cases, child request allocation failure, and `tevent_loop_once()` failure handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/composite/composite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/composite/composite.h -->
# sources/user-network-fs/samba/source4/libcli/composite/composite.h

Purpose: public interface for Samba4 composite requests, a legacy async abstraction for representing a multi-step client operation as one stateful request object.

Important types and APIs: defines `enum composite_state` with init, in-progress, done, and error states; defines `struct composite_context` with externally visible `state`, implementation `private_data`, final `NTSTATUS`, `event_ctx`, async callback, and `used_wait`; declares creation, wait/free, completion/error, memory/status helpers, and continuation attachment for composite, SMB1, SMB2, and NBT child operations.

Control flow contract: a producer creates a context, stores operation-private state in `private_data`, starts child async work, and calls `composite_done()` or `composite_error()`. A consumer either installs `async.fn` or calls `composite_wait()`/`composite_wait_free()`.

State and persistence: all state is volatile and talloc-managed. The header exposes enough structure for callers to inspect state and install callbacks directly, so ABI/API stability matters.

Dependencies and integration: includes raw SMB interfaces and forward declares tevent, SMB1, SMB2, and NBT request types. It is included by libcli connection and resolver paths that bridge older composite callbacks with newer modules.

Risks: because fields are public, callers can mutate state incorrectly. The enum ordering is semantically important because wait loops compare state numerically against `COMPOSITE_STATE_DONE`. Test signals should cover direct field use, callback registration, and failure propagation from each continuation helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/composite/composite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/browse.c -->
# sources/user-network-fs/samba/source4/libcli/dgram/browse.c

Purpose: encodes, sends, replies to, and parses NetBIOS browse mailslot datagrams.

Important APIs: `dgram_mailslot_browse_send()` serializes an `nbt_browse_packet` with NDR and sends it to `NBT_MAILSLOT_BROWSE`; `dgram_mailslot_browse_reply()` serializes a reply and sends it back to the source address/name from an incoming datagram; `dgram_mailslot_browse_parse()` extracts mailslot data and decodes it into an `nbt_browse_packet`.

Control flow: send/reply functions allocate a temporary talloc context, NDR-push browse data into a `DATA_BLOB`, construct or reuse NetBIOS names and socket addresses, call `dgram_mailslot_send()`, and free the temporary context. Parse obtains the mailslot payload via `dgram_mailslot_data()`, runs `ndr_pull_nbt_browse_packet`, logs failures, and optionally saves the bad packet at debug level 10.

State and persistence: no long-lived state is stored. A debug-only artifact `browse.dat` can be written on parse failure at high debug level, which is the only disk side effect.

Dependencies and integration: depends on `libdgram.h`, socket addressing, resolver/NBT NDR definitions, and parameter utilities. It integrates with the generic datagram mailslot sender and dispatcher.

Risks: packet size and NDR validity depend on generated NBT parsers. The reply path trusts source fields from the parsed datagram enough to build the destination. Test signals include round-trip browse packet encode/decode, malformed payload parse failure, and reply address construction from incoming packets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/browse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/dgramsocket.c -->
# sources/user-network-fs/samba/source4/libcli/dgram/dgramsocket.c

Purpose: low-level event-driven UDP/138 NetBIOS datagram socket support for Samba's NBT datagram and mailslot clients.

Important APIs: `nbt_dgram_socket_init()` creates the datagram socket, enables broadcast, and installs a tevent fd handler. `dgram_set_incoming_handler()` installs a generic packet handler. `nbt_dgram_send_raw()` queues an already encoded datagram. `nbt_dgram_send()` NDR-encodes an `nbt_dgram_packet` and queues it.

Control flow: `dgm_socket_handler()` dispatches writable events to `dgm_socket_send()` and readable events to `dgm_socket_recv()`. Receive reads pending bytes, parses an `nbt_dgram_packet`, extracts a mailslot name when present, then dispatches to a registered mailslot handler or a generic incoming handler. Send drains `send_queue` with `socket_sendto()` and disables write events once empty.

State and persistence: `struct nbt_dgram_socket` owns the socket, fd event, outgoing request list, handler list, and incoming callback. No persistent storage exists. Queued sends are talloc children of the socket and are freed after successful or failed send.

Dependencies and integration: uses tevent fd readiness, Samba socket abstraction, NDR NBT packet codecs, and dlink list macros. It is the transport beneath browse and netlogon datagram mailslot helpers.

Risks: UDP datagrams are unauthenticated and may be spoofed. `socket_pending()` size drives allocation, so parse and allocation failure behavior matters. If a mailslot handler frees socket state during callback, lifetime assumptions should be tested. Test signals include handler dispatch by case-insensitive mailslot name, generic fallback dispatch, send queue drain, raw send copy behavior, malformed packet logging, and write interest shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/dgramsocket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/libdgram.h -->
# sources/user-network-fs/samba/source4/libcli/dgram/libdgram.h

Purpose: internal/public header for raw async NBT datagram and mailslot support.

Important types: `struct nbt_dgram_request` represents one queued outgoing encoded datagram and destination. `struct nbt_dgram_socket` holds the socket, tevent context/fd, send queue, mailslot handlers, and generic incoming callback. `dgram_mailslot_handler_t` and `struct dgram_mailslot_handler` model per-mailslot callbacks with private data.

Important APIs: declares raw/structured datagram send, socket init, incoming handler registration, mailslot name lookup, handler registration, temporary reply slot allocation, payload extraction, generic mailslot send, and typed netlogon/browse send/reply/parse helpers.

Control flow contract: callers create a socket, register mailslot or generic handlers, then queue packets through `nbt_dgram_send()` or type-specific mailslot helpers. Receive-side dispatch is performed by `dgramsocket.c`.

State and persistence: only in-memory handler and send queues are described. Handler lifetime is controlled by talloc; freeing a handler stops listening via the destructor in `mailslot.c`.

Dependencies and integration: includes Netlogon definitions and relies on generated NBT structs from the broader Samba include graph. This header is the integration point between datagram socket plumbing and browse/netlogon packet modules.

Risks: exposed structs allow direct mutation by internal callers. Temporary mailslot naming and handler lifetime must be used carefully to avoid reply loss or stale callbacks. Test signals should validate structure ownership, temp handler removal, and all declared helper paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/libdgram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/mailslot.c -->
# sources/user-network-fs/samba/source4/libcli/dgram/mailslot.c

Purpose: implements Class 2 NetBIOS datagram mailslots, the SMB transaction-in-datagram mechanism used for small browse and Netlogon mailslot messages.

Important APIs: `dgram_mailslot_listen()` registers a handler; `dgram_mailslot_find()` locates one by case-insensitive name; `dgram_mailslot_name()` validates and extracts a mailslot name from a datagram; `dgram_mailslot_temp()` creates a randomized temporary reply slot; `dgram_mailslot_send()` builds an NBT datagram with SMB transaction body; `dgram_mailslot_data()` returns the payload slice.

Control flow: listen allocates a handler, links it into `dgmsock->mailslot_handlers`, installs a destructor to unlink it, and enables fd reads. Send builds `nbt_dgram_packet` fields, gets the local socket address, fills `dgram_message` and `smb_trans_body`, then queues it through `nbt_dgram_send()`. Data extraction adjusts for padding based on `data_offset`.

State and persistence: handler registration is persistent only for the lifetime of the talloc object. Temporary mailslot creation tries up to 100 random suffixes. No disk state exists.

Dependencies and integration: depends on tevent, dlink lists, socket address helpers, and the NBT datagram structures. It is used by browse and netlogon datagram helpers.

Risks: comments note Class 1 mailslots and 425/426-byte edge sizes are unsupported. `msg->length` and `data_offset` calculations are described as crude, so wire-compatibility edge cases deserve coverage. Temporary slot random collisions are bounded but possible. Test signals include malformed padding in `dgram_mailslot_data()`, unsupported datagram body types, broadcast/direct message types, and large message behavior near the documented class boundary.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/mailslot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/netlogon.c -->
# sources/user-network-fs/samba/source4/libcli/dgram/netlogon.c

Purpose: typed helpers for Netlogon mailslot datagrams over the generic NBT datagram mailslot layer.

Important APIs: `dgram_mailslot_netlogon_send()` NDR-pushes `nbt_netlogon_packet` and sends it to the selected mailslot. `dgram_mailslot_netlogon_reply()` pushes a `nbt_netlogon_response` and sends it to the source of an incoming request. `dgram_mailslot_netlogon_parse_request()` and `_parse_response()` decode request/response payloads.

Control flow: send and parse paths extract or build `DATA_BLOB`s and delegate to generated Netlogon NBT codecs or hand helper functions. Reply constructs the destination socket address from `request->src_addr` and `request->src_port`, creates a client NetBIOS source name, and calls `dgram_mailslot_send()`.

State and persistence: all state is temporary. At debug level 10 a malformed request may be saved as `netlogon.dat`; otherwise there is no persistence.

Dependencies and integration: integrates NBT datagram mailslots with `../libcli/netlogon/netlogon.h`, generated `ndr_nbt`, and socket addressing. Used by older DC discovery and logon browse flows.

Risks: unauthenticated UDP source data drives replies. Parse failures are logged at level 0, which can be noisy if exposed to hostile traffic. Test signals include valid request/response round trips, malformed NDR payloads, missing destination address allocation, and correct source/destination NetBIOS name use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/dgram/netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/finddc.h -->
# sources/user-network-fs/samba/source4/libcli/finddc.h

Purpose: declares the shared input/output structure for finding domain controllers and includes generated prototypes for the find-DC API.

Important type: `struct finddcs` contains input protocol, domain name, optional site name, optional domain SID, required `DS_SERVER_*` flags, and optional server address override. Output contains selected server IP address and `netlogon_samlogon_response`.

Control flow contract: callers fill `io.in`, call a protocol-specific find routine such as CLDAP, and read `io.out` when `NT_STATUS_OK` is returned.

State and persistence: the structure is caller-owned and transient. No persistent state is defined.

Dependencies and integration: includes messaging, `libcli.h`, Netlogon, and loadparm types, then includes `finddcs_proto.h`. The key integration is with CLDAP Netlogon pings and name resolution.

Risks: optional inputs must be interpreted consistently by implementations. A missing domain name and server address is invalid. Test signals include combinations of DNS domain, NetBIOS domain, explicit IP, explicit hostname, site names, domain SID filters, and minimum DC flag filters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/finddc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/finddcs_cldap.c -->
# sources/user-network-fs/samba/source4/libcli/finddcs_cldap.c

Purpose: implements domain controller discovery through DNS/NBT name resolution followed by CLDAP Netlogon pings.

Important APIs: `finddcs_cldap_send()`, `finddcs_cldap_recv()`, and synchronous `finddcs_cldap()`. Internal stages include IP bypass, DNS SRV lookup, NBT `<1C>` lookup, explicit hostname lookup, `finddcs_cldap_next_server()`, and `finddcs_cldap_netlogon_replied()`.

Control flow: send copies relevant inputs into request state, chooses the path: explicit IP goes straight to CLDAP, explicit hostname uses NBT server lookup, dotted domain uses DNS SRV `_ldap._tcp[.site]._sites.domain`, and non-dotted domain uses NBT logon lookup. Resolved addresses are converted to `tsocket_address` entries on port 389. `netlogon_pings_send()` queries all candidates with `NETLOGON_NT_VERSION_5`, `5EX`, and `IP`, required flags, optional realm and SID, and a two-second timeout. The receive callback chooses a non-null response, maps it, and completes.

State and persistence: `finddcs_cldap_state` is talloc-owned by the `tevent_req`; no disk persistence. The selected response and address are moved/steolen to caller memory on recv.

Dependencies and integration: mixes modern `tevent_req` with older composite resolver callbacks. Depends on CLDAP, resolver, Netlogon ping helpers from source3, tsocket, SID utilities, and composite helpers.

Risks: `finddcs_cldap_ipaddress()` returns `tevent_req_is_nterror()` in a way that means successful immediate submission can return false; tests should confirm this path. Hostname resolution uses NBT server name rather than DNS unless the server address is already numeric. The final non-null response wins in the loop. Test signals include explicit IP, DNS SRV with and without site, NBT fallback, no-response handling, minimum flag filtering, domain SID filtering, timeout behavior, and sync `finddcs_cldap_recv()` polling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/finddcs_cldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_bind.c -->
# sources/user-network-fs/samba/source4/libcli/ldap/ldap_bind.c

Purpose: implements LDAP simple bind, SASL/GENSEC bind, and rebind for Samba's LDAP client connection.

Important APIs: `ldap_rebind()`, `ldap_bind_simple()`, and `ldap_bind_sasl()`. Internal constructors create simple and SASL LDAP bind messages.

Control flow: simple bind chooses explicit or cached DN/password, sends a BindRequest, waits, validates a BindResponse, and caches simple credentials for later rebind. SASL bind requires an active socket, empty send queue, and no pending requests, initializes GENSEC, chooses wrapping/channel binding behavior based on TLS, anonymous credentials, and loadparm settings, starts `GSS-SPNEGO`, loops over `gensec_update()` and LDAP SASL BindRequests until complete, handles stronger-auth and invalid-credential retries, validates sign/seal features, and wraps the raw tstream with a GENSEC tstream when negotiated.

State and persistence: stores bind type and credentials pointer in `conn->bind`; stores `conn->gensec`; may switch `conn->sockets.active` to SASL stream. No disk persistence.

Dependencies and integration: depends on LDAP message/request APIs, TLS channel binding, GENSEC, credentials, loadparm, packet/tstream wrappers, and ADS auth flags. Security integration is central.

Risks: SASL bind is intentionally serialized against pending traffic; bypassing this would corrupt stream state. Credential feature mutation is temporarily applied and restored, so failure paths must not tattoo caller credentials. Channel binding behavior is configurable for testing and must be handled carefully. Test signals include simple bind defaults, SASL over TLS with channel bindings, sign/seal requirements, strong-auth retry, invalid-credential retry, empty-output final GENSEC step, and failure cleanup of `conn->gensec`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_client.c -->
# sources/user-network-fs/samba/source4/libcli/ldap/ldap_client.c

Purpose: core LDAP client transport, connection, request multiplexing, reconnect, timeout, and error handling.

Important APIs: `ldap4_new_connection()`, `ldap_connect_send()`, `ldap_connect_recv()`, `ldap_connect()`, `ldap_set_reconn_params()`, `ldap_request_send()`, `ldap_request_wait()`, `ldap_result_n()`, `ldap_result_one()`, `ldap_check_response()`, `ldap_errstr()`, and `ldap_transaction()`. Internal helpers parse LDAP URLs, establish TCP/Unix sockets, start TLS/StartTLS, decode PDUs, match replies, and abandon timed-out or destroyed requests.

Control flow: a connection owns raw/TLS/SASL tstreams, a send queue, a single outstanding read subrequest, and a pending request list. Requests are encoded with LDAP control handlers, assigned monotonically increasing message IDs, queued through `tstream_writev_queue_send()`, and added to pending. Reads begin only while pending requests exist; decoded messages are matched by message ID, appended to request replies, and non-search responses complete the request. Search entries and references can accumulate until a done response arrives.

State and persistence: volatile talloc state includes host/port, reconnect URL/counters, active stream, pending requests, last LDAP error string, and timers. Reconnect can synchronously reconnect and rebind after transport errors when enabled.

Dependencies and integration: uses tstream, tevent, Samba sockets, ASN.1/LDAP encoders, TLS, resolver, composite socket connect, loadparm, and LDAP control handlers.

Risks: `ldap_reconnect()` is marked not async safe. Message ID zero fallback maps malformed server replies to the first pending request. Critical undecoded controls convert a request to `LDAP_UNAVAILABLE_CRITICAL_EXTENSION`. Request destructors and timeouts send abandon operations, so lifetime and callback ordering need careful tests. Test signals include LDAP/LDAPS/LDAPI URL parsing including IPv6, StartTLS response validation, reconnect/rebind, multi-entry search, critical unknown controls, timeout abandon, unbind/abandon completion, and connection-dead propagation to pending requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_client.h -->
# sources/user-network-fs/samba/source4/libcli/ldap/ldap_client.h

Purpose: internal LDAP client declarations for connection and request state plus public-ish client helper prototypes.

Important types: `enum ldap_request_state`; `struct ldap_request` with list links, connection pointer, message ID, state, replies, status, encoded data, write iovec, callback, and timeout event; `struct ldap_connection` with raw/TLS/SASL/active streams, send queue, receive subrequest, loadparm, host/port, bind cache, pending list, GENSEC state, timeout, and event context.

Control flow contract: `ldap_request_send()` creates requests that become pending until matched replies, timeout, abandon, or connection death. Search consumers can call `ldap_result_n()` repeatedly. Connect and bind APIs manipulate the connection streams.

State and persistence: all fields are in-memory and talloc-owned. The reconnect block preserves a URL and retry timing in the connection object only.

Dependencies and integration: includes network iovec types and `libcli_ldap.h`; forward declarations tie into GENSEC credentials, loadparm, ldb parse/control types, and composite connect.

Risks: structs expose internals to sibling modules, so invariants such as pending list membership, active stream selection, and timeout event ownership are not encapsulated. Test signals should exercise request state transitions, reply array growth, timeout events, and bind/rebind state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_controls.c -->
# sources/user-network-fs/samba/source4/libcli/ldap/ldap_controls.c

Purpose: maps known LDAP/LDB control OIDs to ASN.1 encode/decode helpers for Samba's LDAP client/server message codecs.

Important APIs: `samba_ldap_control_handlers()` returns the static `ldap_known_controls` table. Internal functions encode/decode paged results, SD flags, search options, extended DN, server sort request/response, ASQ, DirSync/DirSyncEx, VLV request/response, OpenLDAP dereference, verify-name, policy hints, and zero-length flag controls.

Control flow: each decoder loads a control `DATA_BLOB` into `asn1_data`, validates expected sequence/context tags, allocates the corresponding LDB/DSDB control structure, copies strings or binary cookies into talloc memory, and returns a typed pointer. Encoders mirror the structure into ASN.1 and extract a blob. The table associates network-capable controls with handlers and marks internal-only controls with null encode/decode handlers.

State and persistence: no global mutable state; only a static const handler table. All decoded objects live under caller-provided memory.

Dependencies and integration: depends on LDB controls, Samba ASN.1 utilities, DSDB/SAMDB control definitions, UTF-16 conversion, and LDAP attribute decoding for OpenLDAP dereference results. It is called by LDAP message encode/decode in `ldap_client.c`.

Risks: many decode failure paths return false without freeing partially allocated ASN.1 contexts, acceptable under talloc parent lifetimes but worth leak-testing. Incorrect tag handling can reject valid server controls or accept malformed ones. UTF-16 length conversion in verify-name must handle malformed data. Test signals include round-trip encode/decode for each supported control, empty extended-DN and flag controls, critical unknown/undecoded control behavior via `ldap_client.c`, cookies with zero and nonzero length, VLV offset/assertion variants, and OpenLDAP dereference attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_controls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_ildap.c -->
# sources/user-network-fs/samba/source4/libcli/ldap/ldap_ildap.c

Purpose: synchronous convenience API similar to traditional LDAP search calls, built on the async LDAP request layer.

Important APIs: `ildap_count_entries()`, `ildap_search_bytree()`, and `ildap_search()`.

Control flow: `ildap_search()` parses a string filter into an LDB parse tree then delegates to `ildap_search_bytree()`. The by-tree function constructs a SearchRequest message, counts requested attributes, attaches controls, sends it, then iterates `ldap_result_n()` until `SearchResultDone` or error. Entry and reference messages are accumulated into a null-terminated result array; response controls can be stolen to caller output.

State and persistence: results and response controls are talloc-owned by the connection/caller memory. No persistent storage.

Dependencies and integration: depends on `ldap_client.h`, LDAP message structs, LDB parse trees, and request/result functions. It is a blocking wrapper over the event loop.

Risks: `*results` is unconditionally dereferenced, so caller must provide a valid output pointer. The function reparents `req` under `msg` in an unusual direction and does not visibly free `msg` on all success paths, so ownership assumptions rely on request lifetime. Test signals include empty result sets, search references, response controls, invalid filter expressions, no-more-entries normalization, and attribute-only searches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/ldap_ildap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/libcli_ldap.h -->
# sources/user-network-fs/samba/source4/libcli/ldap/libcli_ldap.h

Purpose: umbrella LDAP helper header that pulls in LDAP message definitions and selected generated misc types.

Important content: include guard `_SMB_LDAP_H_`; includes `ldap_message.h` and generated `misc.h`; forward declares tevent, credentials, and SID-related structures.

Control flow and state: no executable behavior. It establishes shared type visibility for LDAP client modules.

Dependencies and integration: this is the common include for `ldap_bind.c`, `ldap_client.c`, `ldap_controls.c`, and `ldap_ildap.c`. It bridges generated LDAP message definitions with Samba client code.

Risks: because it includes generated message structures, changes to generated NDR/LDAP definitions propagate broadly. Test signal is compile coverage of LDAP client modules and consumers after interface changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/libcli_ldap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/wscript_build -->
# sources/user-network-fs/samba/source4/libcli/ldap/wscript_build

Purpose: Waf build definition for the private Samba `cli-ldap` library.

Important configuration: builds `ldap_client.c`, `ldap_bind.c`, `ldap_ildap.c`, and `ldap_controls.c`; generates `ldap_proto.h`; exposes `samba-errors` and `tevent` public dependencies; declares private headers `libcli_ldap.h:ldap-util.h`; links against composite, LDB, tsocket, socket, SAMR NDR, TLS, generic NDR, loadparm/resolve, GENSEC, and common LDAP client helpers; marks the library private.

Control flow and state: no runtime behavior. It controls compile/link integration and generated prototypes.

Dependencies and integration: this file is the build-level connection between LDAP client code and the broader Samba libraries needed for TLS, GENSEC, resolver, and ASN.1/NDR support.

Risks: missing dependencies appear as compile or link failures, especially for TLS/GENSEC/control codecs. Test signals include clean Waf configure/build for `cli-ldap`, generated `ldap_proto.h` freshness, and dependent subsystem link tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/ldap/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/libcli.h -->
# sources/user-network-fs/samba/source4/libcli/libcli.h

Purpose: broad SMB client API header exposing the classic `smbcli_state` stack and many synchronous SMB1 helper functions.

Important types: `struct smbcli_state` groups options, socket, transport, session, tree, substitution context, and LSA state. `struct clilist_file_info` models directory list entries. `struct nbt_dc_name` contains DC address/name. `enum brl_type` defines byte-range lock kinds.

Important APIs: declares socket connect, negotiate, session setup, tree connect/disconnect, full connection, file read/write/open/close, UNIX extension operations, rename/delete/mkdir/rmdir, locking/unlocking, file attribute/query operations, directory listing, messaging, and delete-tree helpers.

Control flow contract: callers typically initialize state, connect socket/transport, negotiate, establish session, connect tree, then use file/tree operations. Many functions are synchronous wrappers around raw request implementations.

State and persistence: the header defines in-memory client state only. File operations affect remote SMB server state; no local persistence is defined.

Dependencies and integration: includes generated NBT definitions and raw client headers. It is a central include for RAP and raw SMB client modules.

Risks: the API surface is large and SMB1-centric. Callers must respect tree/session/transport lifetime layering. Test signals include full connection setup, all state teardown paths, UNIX extension calls on capable/incapable servers, old/new directory listing variants, and locking semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/libcli.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/rap/rap.c -->
# sources/user-network-fs/samba/source4/libcli/rap/rap.c

Purpose: implements client-side RAP/LANMAN remote administration protocol calls over SMB transactions to `\\PIPE\\LANMAN`.

Important APIs: `new_rap_cli_call()`, `rap_cli_do_call()`, and many `smbcli_rap_*` wrappers for share enumeration, server enumeration/info, print queue/job/destination operations, user password changes, user get/add/delete, session enum/getinfo, and remote time-of-day.

Control flow: each wrapper creates a `rap_call`, pushes RAP parameter descriptor characters and scalar/string/data arguments, sets expected data and auxiliary formats, calls `rap_cli_do_call()`, then pulls RAP status, convert offsets, counts/availability, and typed output structures. `rap_cli_do_call()` assembles call number, descriptor strings, parameter blob, data blob, and optional aux descriptor into an SMB transaction to `\\PIPE\\LANMAN`; response blobs become NDR pull contexts.

State and persistence: `rap_call` owns push/pull contexts and descriptor strings for one call. Operations can change remote server state, such as print job pause/delete, queue purge, password changes, and user add/delete. Local persistence is absent.

Dependencies and integration: depends on `libcli.h`, raw SMB transaction support, generated RAP NDR definitions, and libndr. It is built as `LIBCLI_RAP`.

Risks: RAP uses legacy ASCII/no-align formats and convert offsets; malformed or hostile responses can exercise offset and bounds handling. Some format comments admit uncertainty. Password-changing functions handle encrypted buffers and should avoid debug leakage. Test signals include level-specific format coverage, invalid level rejection, convert-offset string pulls, count/available parsing, print job control calls, user management calls, and debug NDR print behavior at high log levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/rap/rap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/rap/rap.h -->
# sources/user-network-fs/samba/source4/libcli/rap/rap.h

Purpose: RAP client internal header with status-handling macros, the `rap_call` structure, RAP NDR flags, generated RAP type inclusion, and generated prototypes.

Important content: macros `RAP_GOTO`, `RAP_RETURN`, `NDR_GOTO`, and `NDR_RETURN` standardize NTSTATUS/NDR error propagation. `struct rap_call` stores call number, parameter/data/aux descriptor strings, expected receive sizes, push contexts, pull memory context, and response pull contexts. `RAPNDR_FLAGS` sets no-align, ASCII, null-terminated string behavior.

Control flow contract: RAP wrappers create a `rap_call`, push descriptors and data, execute the call, then pull response data through the stored pull contexts.

State and persistence: per-call volatile state only. Remote administrative operations performed by callers may persist on the server.

Dependencies and integration: includes generated `rap.h` and `libcli/rap/proto.h`. The flags must match RAP wire format expectations.

Risks: macro `goto done` patterns require each caller to define `result` and `done` consistently. Descriptor strings and expected lengths are central to safe parsing. Test signals are compile coverage and representative wrapper calls for each macro path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/rap/rap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/rap/wscript_build -->
# sources/user-network-fs/samba/source4/libcli/rap/wscript_build

Purpose: Waf build definition for the `LIBCLI_RAP` subsystem.

Important configuration: builds `rap.c`, declares public dependencies on `smbclient-raw` and `NDR_RAP`, and generates `proto.h`.

Control flow and state: no runtime logic; it controls compile/link placement for RAP client support.

Dependencies and integration: ensures RAP wrappers can call raw SMB transaction code and generated RAP NDR codecs.

Risks: dependency drift causes build or link failures. Test signals include Waf target build and consumers that include `libcli/rap/proto.h`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/rap/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clierror.c -->
# sources/user-network-fs/samba/source4/libcli/raw/clierror.c

Purpose: exposes simple error inspection helpers for the raw SMB client tree.

Important APIs: `smbcli_errstr()` maps the transport's last error type to a string; `smbcli_nt_error()` maps it to an `NTSTATUS`; `smbcli_is_error()` returns whether that status is an error.

Control flow: functions inspect `tree->session->transport->error.etype` and return SMB NT status, generic unsuccessful for socket/NBT errors, OK for no error, or string labels for non-SMB errors.

State and persistence: reads the in-memory last-error state maintained by transport request handling. No persistence.

Dependencies and integration: depends on raw libcli structures and raw prototypes. Used by higher-level raw callers after request receive/destruction.

Risks: callers passing null or partially torn-down tree/session/transport will crash. Socket and NBT errors lose detailed status. Test signals include SMB error propagation, socket/NBT error mapping, no-error mapping, and use after failed request paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clierror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clioplock.c -->
# sources/user-network-fs/samba/source4/libcli/raw/clioplock.c

Purpose: raw SMB client helpers for oplock break handling.

Important APIs: `smbcli_oplock_ack()` sends a one-way `SMBlockingX` oplock release acknowledgement; `smbcli_oplock_handler()` installs the transport-level oplock break callback and private data.

Control flow: ack constructs a locking request with command `SMBlockingX`, `LOCKING_ANDX_OPLOCK_RELEASE`, target file number, and requested ack level, then sends it without waiting for a normal response. Handler setup simply stores callback fields in the transport.

State and persistence: callback state lives in `transport->oplock`; ack changes remote server oplock state. No local persistence.

Dependencies and integration: depends on raw request setup/send and `clitransport.c` break dispatch, which listens for MID `0xFFFF` break packets when a handler is installed.

Risks: ack is one-way and returns only send success; server acceptance is not observed. Incorrect ack level or file number can affect cache consistency. Test signals include break callback installation, receipt of break packets, ack wire fields, and missing-handler logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clioplock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clisession.c -->
# sources/user-network-fs/samba/source4/libcli/raw/clisession.c

Purpose: manages raw SMB1 session contexts and implements session setup, ulogoff, and exit requests.

Important APIs: `smbcli_session_init()`, `smb_raw_sesssetup_send()`, `smb_raw_sesssetup_recv()`, `smb_raw_sesssetup()`, `smb_raw_ulogoff_send()`, `smb_raw_ulogoff()`, `smb_raw_exit_send()`, and `smb_raw_exit()`.

Control flow: session init references or steals the transport, sets PID, invalid VUID, options, creates an `smbXcli_session`, and derives `flags2` from negotiated capabilities and signing state. Session setup send supports old, NT1, and SPNEGO levels, packing appropriate password/security blobs and strings. Recv accepts success or `MORE_PROCESSING_REQUIRED`, validates word counts, extracts VUID/action, and pulls returned OS/Lanman/domain/workgroup/security blobs.

State and persistence: session object stores transport, PID, VUID, options, `smbXcli` session, and `flags2`. Remote session setup/logoff affects server-side authenticated state.

Dependencies and integration: uses raw request helpers, SMBX client base session, filesystem PID, and negotiated transport state.

Risks: SMB2 session setup level is explicitly unsupported. String pull parsing depends on response layout and word count validation. VUID is still kept for legacy callers while `smbXcli` is the future path. Test signals include old/NT1/SPNEGO setup, multi-step SPNEGO `MORE_PROCESSING_REQUIRED`, signing flag propagation, ulogoff/exit, invalid level handling, and malformed response data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clisession.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clisocket.c -->
# sources/user-network-fs/samba/source4/libcli/raw/clisocket.c

Purpose: asynchronous and synchronous creation of `smbcli_socket` connections to SMB servers by IP address or resolved NetBIOS name.

Important APIs: `smbcli_sock_connect_send()`, `smbcli_sock_connect_recv()`, and `smbcli_sock_connect()`. Internal helpers resolve names, submit multi-address SMB socket connection attempts, and receive the resulting transport.

Control flow: send creates composite state, copies options/socket names, duplicates calling/called NBT names, interprets numeric host addresses directly, or starts `resolve_name_send()` for host lookup. Resolved string addresses are converted to `sockaddr_storage`; `smbsock_any_connect_send()` tries the address set using configured transports and NetBIOS names. On success, it creates `smbcli_socket`, moves in the `smbXcli_transport`, stores hostname and event context, then completes the composite.

State and persistence: all connection attempt state is talloc-owned under the composite. Result socket owns the transport and hostname. No disk persistence.

Dependencies and integration: depends on composite helpers, resolver, Samba socket connect helpers from source3, NBT names, loadparm, and SMB raw socket structures.

Risks: failure paths often free the whole composite and return null, so callers must handle allocation/setup failures separately from asynchronous NTSTATUS errors. `socket_options` is referenced but not used directly in this file. Test signals include numeric IP, resolved multi-address host, bad resolved address, NBT name duplication failure, all transport fallback, and destructor freeing underlying transport.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clisocket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clitransport.c -->
# sources/user-network-fs/samba/source4/libcli/raw/clitransport.c

Purpose: manages raw SMB1 transport state over an established socket/SMBX connection, including capabilities, request submission/completion, oplock break reception, idle callbacks, and echo.

Important APIs: `smbcli_transport_init()`, `smbcli_transport_raw_init()`, `smbcli_transport_dead()`, `smbcli_transport_idle_handler()`, `smbcli_transport_process()`, `smbcli_transport_setup_subreq()`, `smbcli_transport_send()`, `smb_raw_echo_send()`, `smb_raw_echo_recv()`, and `smb_raw_echo()`.

Control flow: init clamps protocol to NT1, builds SMB1 capability flags from options, and creates an `smbXcli_conn`. Request send converts an old `smbcli_request` into an `smb1cli_req`, optionally creates a pending break listener when an oplock handler exists, submits the chain, and marks request state receive/error. Completion receives headers/words/bytes, validates contiguous iovec layout, fills the request input buffer, updates transport last-error state, marks done, and runs async callback. Break handler receives MID `0xFFFF` packets, re-arms itself, extracts TID/FNUM/level, and calls the oplock handler.

State and persistence: transport stores event context, options, SMBX connection, idle timer, last error, break subrequest, and oplock callback. No local persistence; remote echo/oplock behavior affects protocol state.

Dependencies and integration: uses tevent, socket/read SMB helpers, NBT definitions, SMBX base APIs, raw request structures, and `clioplock.c` callbacks.

Risks: SMB2+ is clamped away. Transport death normalizes generic statuses and disconnects the SMBX connection. The iovec contiguity check protects legacy buffer assumptions and is a key regression point. Break listener setup is tied to outgoing request submission, so idle connections with newly installed handlers may not listen until a request is sent. Test signals include capability flag construction, raw init from existing SMBX connection, request success/error, socket error without recv iov, oplock break rearming, idle handler cancellation, echo repeat handling, and `smbcli_transport_process()` nonblocking loop behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clitransport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clitree.c -->
# sources/user-network-fs/samba/source4/libcli/raw/clitree.c

Purpose: manages SMB tree contexts, tree connect/disconnect, and a convenience full tree connection flow.

Important APIs: `smbcli_tree_init()`, `smb_raw_tcon_send()`, `smb_raw_tcon_recv()`, `smb_raw_tcon()`, `smb_tree_disconnect()`, and `smbcli_tree_full_connection()`.

Control flow: tree init steals or references a session and creates an SMBX tree connection object. TCON send supports old `SMBtcon` and `SMBtconX` levels, packing service/path/password/device. Recv validates the response, extracts TID, optional options/access masks, and device/filesystem strings. Disconnect sends `SMBtdis` and waits opportunistically. Full connection fills `smb_composite_connect` inputs and delegates to `smb_composite_connect()` to establish socket, session, and tree.

State and persistence: tree stores a session reference and SMBX tcon object. Remote tree connect/disconnect changes server-side share connection state.

Dependencies and integration: depends on raw request helpers, SMB composite connect, SMBX tcon creation, credentials/loadparm/resolver/event contexts, and client options.

Risks: SMB2 tree connect level is unsupported here. TCONX path is uppercased, which can matter for unusual servers. `smb_tree_disconnect()` returns the request destroy status even if receive was skipped or failed. Test signals include old TCON and TCONX parsing, optional access-mask fields, service/device string extraction, full connection with credentials, disconnect on null tree, and unsupported SMB2 level behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/clitree.c -->
