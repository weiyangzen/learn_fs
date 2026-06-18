# Research: subset-b-009823

Grouped research for Samba `source3/libsmb` NetBIOS name resolution, packet encoding, xattr ACL/DOS attribute handling, DC discovery, and remote password change helpers. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_xattr.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_xattr.c

## Purpose
This file implements libsmbclient extended attribute operations for SMB URLs. It exposes synthetic `system.*` xattrs that map to NT security descriptors and DOS file attributes, plus SMB3.1.1 POSIX information for open files. It is the translation layer between POSIX-style `getxattr`, `setxattr`, `removexattr`, and `listxattr` calls and SMB RPC/security descriptor APIs.

## Important APIs, Types, And Functions
Public entry points are `SMBC_setxattr_ctx`, `SMBC_getxattr_ctx`, `SMBC_fgetxattr_ctx`, `SMBC_removexattr_ctx`, and `SMBC_listxattr_ctx`. Internal helpers include `find_lsa_pipe_hnd`, `convert_sid_to_string`, `convert_string_to_sid`, `parse_ace`, `sec_desc_parse`, `add_ace`, `sort_acl`, `dos_attr_query`, `dos_attr_parse`, `cacl_get`, and `cacl_set`.

The NT security path works with `struct security_descriptor`, `struct security_acl`, `struct security_ace`, `struct dom_sid`, LSA policy handles, and `struct rpc_pipe_client`. The DOS attribute path uses a `struct DOS_ATTR_DESC` populated from `SMBC_getatr` and written through `SMBC_setatr`. `SMBC_fgetxattr_ctx` has special file-handle-only names: `posix.attr.enabled` and `smb311_posix.statinfo`.

## Control Flow
`SMBC_setxattr_ctx` validates an initialized context and parses the SMB URL into server/share/path/user/password. It opens the normal tree connection and, unless disabled by `srv->no_nt_session`, an IPC attribute server for LSA/security descriptor operations. Names under `system.nt_sec_desc.*` are converted into descriptor fragments and sent through `cacl_set`; names under `system.dos_attr.*` are merged into the current DOS attributes and written with `SMBC_setatr`; `system.*` can update both surfaces.

`SMBC_getxattr_ctx` follows the same parse/connect flow, then dispatches supported names to `cacl_get`. `cacl_get` parses exclusion suffixes after `!`, decides whether all, NT-only, ACL-only, or DOS-only data was requested, opens the target with `READ_CONTROL_ACCESS`, queries its security descriptor, formats revision/owner/group/ACEs, queries DOS attributes, and appends formatted fields into the caller buffer or calculates required size when `size == 0`.

`cacl_set` parses ASCII descriptors, resolves DFS/path targets, reads the existing descriptor, mutates it according to mode (`ADD`, `SET`, `REMOVE`, `REMOVE_ALL`, `CHOWN`, `CHGRP`), sorts and deduplicates ACEs, then reopens with `WRITE_DAC_ACCESS | WRITE_OWNER_ACCESS` and calls `cli_set_secdesc`.

`SMBC_fgetxattr_ctx` answers `posix.attr.enabled` from `cli_smb2_fnum_is_posix`, decodes `FSCC_FILE_POSIX_INFORMATION` into a caller-provided `struct stat` plus attrs word for `smb311_posix.statinfo`, and otherwise delegates to path-based `SMBC_getxattr_ctx`.

## State And Persistence
The file mutates remote server state: security descriptors, owners/groups, ACL entries, timestamps, and DOS mode bits. It also caches inability to obtain an NT attribute session by setting `srv->no_nt_session`. Most local allocations are stack-frame talloc allocations. It does not maintain durable local state, but it depends on server cache identity checks after `SMBC_attr_server` because that call can evict the original cached server.

## Dependencies And Integration Points
The implementation integrates libsmbclient URL parsing and server caching (`SMBC_parse_path`, `SMBC_server`, `SMBC_attr_server`), low-level SMB open/query/set calls (`cli_ntcreate`, `cli_query_secdesc`, `cli_set_secdesc`, `cli_close`, `SMBC_getatr`, `SMBC_setatr`), LSA SID/name RPC lookup, security descriptor constructors, and SMB2 POSIX info queries. It relies on Samba configuration such as `lp_winbind_separator()` and `context->internal->full_time_names` to choose legacy or full DOS time xattr names.

## Risks And Edge Cases
The xattr grammar is string-heavy: off-by-prefix errors, mixed legacy/new time names, and exclusion parsing can change behavior. `cacl_set` has complex add/replace semantics and a nested loop that can add all requested ACEs while iterating, so duplicate handling depends on later `sort_acl`. Some paths set `errno = 0` after NT failures, which can obscure diagnostics. NT descriptor operations require a working IPC/LSA pipe; DOS-only operations can still partially succeed when NT operations fail. `SMBC_fgetxattr_ctx` requires the caller to pass exactly `sizeof(struct stat) + 4` for POSIX statinfo but returns only `sizeof(struct stat)`, so callers must know the ABI contract.

## Test Signals
Useful tests include `listxattr` with legacy and full time names, size-query `getxattr` calls, `system.*` with exclusions, owner/group SID vs name conversion, ACL add/replace/remove/remove-all cases, DOS mode/time updates, IPC unavailable fallback behavior, server-cache eviction after `SMBC_attr_server`, SMB3.1.1 POSIX statinfo decoding, and error mapping for too-small buffers, invalid names, invalid descriptors, and unsupported servers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/namecache.c -->
# sources/user-network-fs/samba/source3/libsmb/namecache.c

## Purpose
This file implements the NetBIOS name cache on top of Samba `gencache`. It stores and retrieves NetBIOS name-to-address lists and node-status-derived name records so name resolution can avoid repeated WINS, broadcast, LMHOSTS, or node status traffic.

## Important APIs, Types, And Functions
Public functions are `namecache_store`, `namecache_fetch`, `namecache_delete`, `namecache_flush`, `namecache_status_store`, and `namecache_status_fetch`. Internal helpers include `ipstr_list_make_sa`, `ipstr_list_parse`, `namecache_key`, `flush_netbios_name`, and `namecache_status_record_key`. Address data is represented as `struct samba_sockaddr` arrays and persisted as comma-separated numeric address strings.

## Control Flow
`namecache_store` rejects artificial name types above 255, builds an uppercase `NBT/<name>#<type>` key, serializes the address list as `addr:0` or `[ipv6]:0`, and writes it to `gencache` with `lp_name_cache_timeout()` expiry. `namecache_fetch` builds the same key, retrieves the stored string, tokenizes on commas, strips optional ports, handles bracketed IPv6, converts numeric strings into `sockaddr_storage`, and returns a talloc-owned `struct samba_sockaddr` array only when at least one address parses.

`namecache_delete` removes a single name/type key. `namecache_flush` iterates `NBT/*` entries and deletes each. Status records use keys shaped like `NBT/<query>#<query_type>.<wanted_type>.<ip>` and store the server name found by a node status response.

## State And Persistence
All durable state lives in `gencache` and expires using `lp_name_cache_timeout()`. The module serializes only numeric addresses and ignores stored ports on read. Status fetch copies returned server names into a 16-byte NetBIOS-name-sized output buffer with `strlcpy`.

## Dependencies And Integration Points
The file depends on `lib/gencache.h`, Samba socket helpers (`print_sockaddr`, `interpret_string_addr`, `sockaddr_storage_to_samba_sockaddr`), talloc tokenization, and `libsmb/namequery.h` declarations. It is consumed by `namequery.c` for normal name resolution and node status lookups, and by `namequery_dc.c` to invalidate DC-related cache entries when ADS site selection changes.

## Risks And Edge Cases
The comma-separated format assumes addresses are numeric and never contain unbracketed commas. The writer stores port `0`, and the parser deliberately ignores ports, so callers must not expect service-port fidelity. Corrupt cache entries can parse to zero addresses and are treated as misses. `namecache_flush` deletes every `NBT/*` entry, including status records, not just address-list records. The string append loop in `ipstr_list_make_sa` is intentionally inefficient but acceptable for small address lists.

## Test Signals
Tests should cover IPv4 and bracketed IPv6 round trips, invalid token tolerance, name types above 255, cache expiry behavior through `gencache`, flushing `NBT/*`, status record keying by source IP and type, and fetch behavior when all serialized addresses are invalid.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/namecache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/namequery.c -->
# sources/user-network-fs/samba/source3/libsmb/namequery.c

## Purpose
This is Samba's libsmb name-resolution engine. It resolves names through direct IP parsing, local name cache, DNS/hosts, ADS DNS SRV records, LMHOSTS, WINS, NetBIOS broadcast, and domain-controller/KDC helper flows. It also implements async NetBIOS node status and name query transactions over UDP, optionally racing replies from `nmbd`'s unexpected-packet reader.

## Important APIs, Types, And Functions
Exported APIs include SAF cache helpers (`saf_store`, `saf_join_store`, `saf_delete`, `saf_fetch`), node status APIs (`node_status_query_send/recv`, `node_status_query`, `name_status_find`), NetBIOS name query APIs (`name_query_send/recv`, `name_query`), broadcast and WINS APIs (`name_resolve_bcast_send/recv`, `name_resolve_bcast`, `resolve_wins_send/recv`, `resolve_wins`), general resolution APIs (`internal_resolve_name`, `resolve_name`, `resolve_name_list`), and DC helpers (`find_master_ip`, `get_pdc_ip`, `get_sorted_dc_list`, `get_kdc_list`).

Key async state structs are `sock_packet_read_state`, `nb_trans_state`, `node_status_query_state`, `name_query_state`, `name_queries_state`, `query_wins_list_state`, `resolve_wins_state`, and `name_resolve_bcast_state`. The file-level `global_in_nmbd` flag lets nmbd avoid querying itself as WINS.

## Control Flow
Low-level NetBIOS transactions are built around `nb_trans_send`: bind a UDP datagram socket, try to attach an `nb_packet_reader` for packets captured by nmbd, send the packet, resend every second, and complete when `sock_packet_read_send` receives a matching packet from either path. `sock_packet_read_got_socket` parses UDP packets with `parse_packet_talloc`, filters by transaction ID, and applies a caller validator. Validators parse node status and name-query response semantics.

`node_status_query_send` builds a question type `0x21` request and waits up to ten seconds. `name_status_find` first checks the status cache, then LMHOSTS, then node status, storing successful non-`0x1c` results. `name_query_send` builds a question type `0x20` request, collects positive address records, handles negative WINS responses as `NT_STATUS_NOT_FOUND`, accumulates broadcast replies until timeout, sorts addresses by interface proximity, and returns flags.

Higher-level resolution starts in `internal_resolve_name`. It returns direct numeric IPs immediately, then tries `namecache_fetch`, then walks the configured resolve order. `host/hosts` calls `getaddrinfo`, `ads` and `kdc` perform DNS SRV lookups, `lmhosts` reads LMHOSTS, `wins` queries configured WINS tags, and `bcast` broadcasts to IPv4 interface broadcast addresses. Successful results are converted to `struct samba_sockaddr`, deduplicated, cached, and returned.

DC/KDC helpers layer policy on top of `internal_resolve_name`. `get_dc_list` combines server affinity, `password server`, wildcard auto lookup, ADS-only/KDC-only modes, negative connection-cache filtering, duplicate removal, IPv4 prioritization, and ordered-vs-sortable result handling. `get_sorted_dc_list` retries without a site when the site-specific lookup finds no logon servers.

## State And Persistence
Persistent local state is stored in `gencache` through SAF keys and the name cache. SAF keys prefer recently successful DCs (`SAF/DOMAIN/<domain>`) and join DCs (`SAFJOIN/DOMAIN/<domain>`) with configurable TTLs. Name resolution stores positive name results through `namecache_store`. WINS failures are recorded through `wins_srv_died`, and DC candidates are filtered through the negative connection cache. Runtime state is primarily talloc-owned tevent request state and temporary arrays.

## Dependencies And Integration Points
This file depends on tevent, async socket/tdgram helpers, `libsmb/nmblib` packet builders/parsers, `libsmb/unexpected` packet reader support, LMHOSTS parsing, WINS server configuration, interface enumeration, ADS DNS query helpers, sitename cache, `gencache`, negative connection cache, loadparm settings, and socket/address utility functions. It is declared by `namequery.h` and used by client connection, domain-controller discovery, browser lookup, and password-change workflows.

## Risks And Edge Cases
NetBIOS node status and name queries are IPv4-only; IPv6 names can be returned by DNS/hosts but not by NBT. Async transactions intentionally retry until a matching response or timeout, so wrong validators can spin until timeout. Broadcast queries treat timeout as success if any reply was accumulated. Long names or dotted names skip NBT methods. Cache hits bypass resolver-order changes until expiry. ADS SRV results are already priority/weight ordered, but later sorting is applied only when a list is not considered ordered. Several loops include overflow checks, but many behaviors rely on small configured server/interface lists.

## Test Signals
Useful signals include direct IP resolution, cache hit/miss/expiry, disabled-NetBIOS paths, long and dotted names filtering NBT, WINS negative responses, dead-WINS retry behavior, broadcast multi-interface lookup, LMHOSTS status lookup, node status parsing with MAC extra data, ADS SRV DC/KDC lookup with site fallback, `password server` wildcard and explicit server ordering, negative connection-cache filtering, IPv4 preference for DCs, and tevent timeout behavior for no-response networks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/namequery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/namequery.h -->
# sources/user-network-fs/samba/source3/libsmb/namequery.h

## Purpose
This header declares the public name-query and name-resolution surface implemented by `namequery.c` for source3 SMB client code. It centralizes APIs for server affinity, NetBIOS node status, NetBIOS name queries, WINS/broadcast resolution, generic resolver dispatch, and DC/KDC list discovery.

## Important APIs, Types, And Functions
The declarations expose SAF functions, tevent send/recv pairs for `node_status_query`, `name_query`, `name_resolve_bcast`, and `resolve_wins`, synchronous wrappers for those operations, address list utilities such as `remove_duplicate_addrs2`, general helpers `internal_resolve_name`, `resolve_name`, `resolve_name_list`, and domain helpers `find_master_ip`, `get_pdc_ip`, `get_sorted_dc_list`, and `get_kdc_list`.

The API uses Samba core types: `TALLOC_CTX`, `struct tevent_context`, `struct tevent_req`, `NTSTATUS`, `struct nmb_name`, `struct node_status`, `struct node_status_extra`, `struct sockaddr_storage`, and `struct samba_sockaddr`.

## Control Flow And Integration
Callers can choose async send/recv pairs when integrating into an existing tevent loop or synchronous wrappers when blocking is acceptable. Lower-level APIs return raw `sockaddr_storage` lists and flags; higher-level APIs return `struct samba_sockaddr` arrays suitable for connection code. The header is included by `namecache.c`, `namequery_dc.c`, and other libsmb/client modules needing NetBIOS or DC resolution.

## State And Persistence
The header has no runtime state. It exposes functions that read and write gencache-backed SAF/namecache state and use loadparm configuration internally.

## Dependencies
It includes `includes.h` and `<tevent.h>` and assumes the broader Samba include graph provides definitions for `NTSTATUS`, talloc, NetBIOS name/status structures, and socket structures.

## Risks And Test Signals
The main API risk is ownership and representation mismatch: returned arrays are talloc-owned by the supplied context, counts use both `size_t` and `unsigned int`, and some APIs return `sockaddr_storage` while others return `samba_sockaddr`. Compile coverage should include C files that consume every declaration, and behavioral tests should exercise both async and synchronous wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/namequery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/namequery_dc.c -->
# sources/user-network-fs/samba/source3/libsmb/namequery_dc.c

## Purpose
This file provides `get_dc_name`, a domain-controller name and address selector. It prefers ADS/CLDAP discovery when appropriate, handles site-aware Kerberos configuration for the local domain, and falls back to NetBIOS/RPC-style DC discovery through `get_sorted_dc_list` plus node status.

## Important APIs, Types, And Functions
The exported function is `get_dc_name`. Internal helpers are `is_our_primary_domain` under `HAVE_ADS`, `ads_dc_name`, and `rpc_dc_name`. The code works with `ADS_STRUCT`, `fstring` server names, `struct sockaddr_storage`, loadparm role/security/realm/workgroup settings, and namequery helpers.

## Control Flow
`get_dc_name` zeroes the output address and decides whether the requested domain/realm is the local domain. If local ADS security is active or a realm is supplied, it tries `ads_dc_name`. ADS discovery initializes an ADS context, does CLDAP-only connection, reacts to closest-site changes by clearing related `0x1c` namecache entries and retrying up to three times, uppercases the LDAP server name, and returns the LDAP socket address. For local domains with a KDC response, it writes a private krb5 configuration targeting the selected KDC and site.

If ADS discovery is not applicable or fails and a NetBIOS domain is available, `get_dc_name` calls `rpc_dc_name`. That function asks `get_sorted_dc_list` for DC addresses, does `name_status_find(domain, 0x1c, 0x20, ...)` to convert a DC IP to a server NetBIOS name, skips negative connection-cache entries, and returns the first usable name/address.

## State And Persistence
The ADS path can update local site/Kerberos configuration through `create_local_private_krb5_conf_for_domain`. It can also invalidate namecache entries for realm/domain `0x1c` when site information changes. The RPC path reads negative connection-cache state but does not write persistent state directly.

## Dependencies And Integration Points
This file integrates ADS discovery (`ads_init`, `ads_connect_cldap_only`, `ads_closest_dc`), sitename cache, loadparm, namecache invalidation, `get_sorted_dc_list`, node status lookup, and negative connection cache. It is a bridge from generic name resolution to callers that need both the DC name and socket address.

## Risks And Edge Cases
When `domain` is `NULL`, ADS is the only possible path and failure returns false. Repeated site changes abort after three attempts. Builds without `HAVE_ADS` compile stubs for ADS-dependent address selection and leave `dc_ss` zeroed if no fallback exists. RPC fallback depends on NetBIOS node status and therefore IPv4/NBT availability. Negative connection cache entries can hide otherwise resolvable DCs.

## Test Signals
Tests should cover local ADS domain selection, explicit realm lookup, site-change retry and cache deletion, KDC krb5 config generation for closest DCs, ADS failure followed by RPC fallback, negative connection-cache filtering, no-domain realm-only failure, and non-ADS builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/namequery_dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/nmblib.c -->
# sources/user-network-fs/samba/source3/libsmb/nmblib.c

## Purpose
This file implements low-level NetBIOS Name Service and datagram packet support. It encodes and decodes RFC1001/1002 NetBIOS names, parses and builds NMB and DGRAM packets, copies/frees packet structures, sends UDP packets, formats debug output, sorts name-query reply records, and provides small SMB message buffer helpers.

## Important APIs, Types, And Functions
Exported functions include `global_nmbd_socket_dir`, `debug_nmb_packet`, `put_name`, `nmb_namestr`, `copy_packet`, `free_packet`, `packet_trn_id`, `parse_packet`, `parse_packet_talloc`, `make_nmb_name`, `nmb_name_equal`, `build_packet`, `send_packet`, `match_mailslot_name`, `matching_len_bits`, `sort_query_replies`, `name_mangle`, `name_extract`, `name_len`, and `cli_set_message`.

Internal parser/builder helpers include `handle_name_ptrs`, `parse_nmb_name`, `put_nmb_name`, `parse_alloc_res_rec`, `put_res_rec`, `put_compressed_name_ptr`, `parse_dgram`, `parse_nmb`, `build_dgram`, `build_nmb`, `name_interpret`, and `name_ptr`.

## Control Flow
Packet parsing starts at `parse_packet`, allocates a `packet_struct`, fills common metadata, and dispatches to `parse_nmb` or `parse_dgram`. `parse_nmb` reads the 12-byte NMB header, optional question, and resource-record arrays, using `parse_nmb_name` to decode compressed NetBIOS names and `parse_alloc_res_rec` to bounds-check record data. `parse_dgram` reads the datagram header, optional source/destination names, and bounded payload data.

Packet building mirrors parsing through `build_packet`, `build_nmb`, and `build_dgram`. `build_nmb` writes flags and record counts, encodes the question name, writes answer/name-server/additional records, and uses compressed-name-pointer encoding for registration/refresh/release requests where RFC behavior requires it. `send_packet` builds into a 1024-byte stack buffer and sends over UDP through `send_udp`, which retries transient Linux `ECONNREFUSED` notifications.

Name helpers convert between plain names, NetBIOS 16-byte names, and DNS-compatible encoded forms. `name_mangle` returns the wire-format name with configured scope, while `name_extract` and `name_len` parse names from arbitrary buffers with compression-pointer support. `matching_len_bits` and `sort_query_replies` rank query response records by address closeness.

## State And Persistence
The file has almost no persistent state. `global_nmbd_socket_dir` reads configuration dynamically. `sort_query_replies` uses a static `sort_ip[4]` scratch buffer during `qsort`, making that operation non-reentrant. Packet copies allocated by the SMB allocator must be released by `free_packet`; talloc copies from `parse_packet_talloc` are owned by the supplied context.

## Dependencies And Integration Points
This file depends on `nameserv.h` packet structures through `nmblib.h`, Samba byte-order macros, charset conversion helpers, loadparm settings for NetBIOS scope and nmbd socket directory, debug infrastructure, and socket send APIs. `namequery.c` relies on its packet build/parse, transaction ID, name construction, and debug functions for all NBT network operations.

## Risks And Edge Cases
NBT name compression is a high-risk parser area; the code caps pointer recursion and scope loops but malformed packets still exercise many bounds checks. `put_res_rec` does not perform an explicit per-record buffer check around the final memcpy except through caller length preflights, so builder callers must pass accurate lengths. `match_mailslot_name` performs pointer arithmetic before the datagram data buffer and relies on SMB datagram layout assumptions. `sort_query_replies` is not thread-safe because of static comparator state. Many APIs assume IPv4-era NetBIOS packet sizes and a 1024-byte send buffer.

## Test Signals
Tests should cover valid and malformed compressed names, pointer loops, overlong scopes, NMB query/response/resource records, datagram parsing with and without names, build-then-parse round trips, registration packets with compressed additional records, wildcard name encoding, name scope handling, talloc vs malloc packet ownership, `send_packet` length failures, mailslot matching, and sort order by shared address prefix.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/nmblib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/nmblib.h -->
# sources/user-network-fs/samba/source3/libsmb/nmblib.h

## Purpose
This header declares the low-level NetBIOS packet and name helper API implemented by `nmblib.c`. It is the interface used by name resolution, unexpected packet handling, and older SMB client datagram code to build, parse, inspect, copy, and send NBT packets.

## Important APIs, Types, And Functions
The header includes `nameserv.h` for `struct packet_struct`, `struct nmb_name`, packet types, resource records, and datagram/NMB packet shapes. It declares packet lifecycle functions (`copy_packet`, `free_packet`, `parse_packet`, `parse_packet_talloc`), builders/senders (`build_packet`, `send_packet`, `cli_set_message`), name helpers (`put_name`, `make_nmb_name`, `nmb_name_equal`, `nmb_namestr`, `name_mangle`, `name_extract`, `name_len`), transaction/debug helpers (`packet_trn_id`, `debug_nmb_packet`), and address/list helpers (`matching_len_bits`, `sort_query_replies`, `match_mailslot_name`).

## Control Flow And Integration
Callers typically create or parse `packet_struct` instances, inspect transaction IDs, validate packet contents, and free or talloc-own the result. `namequery.c` uses these declarations for every NetBIOS name query and node status transaction. Datagram consumers use `match_mailslot_name` to filter mailslot traffic.

## State And Persistence
The header has no state. It exposes functions with two ownership styles: SMB allocator ownership for `parse_packet`/`copy_packet`, and talloc ownership for `parse_packet_talloc` and `name_mangle`.

## Dependencies
It depends on `nameserv.h` and the Samba global include environment for `TALLOC_CTX`, `bool`, `size_t`, `fstring`, `struct in_addr`, and packet type definitions.

## Risks And Test Signals
The main risks are ownership confusion between malloc-style and talloc-style packet APIs, and callers passing insufficient buffers to builders or name extraction helpers. Compile tests should include both NMB and DGRAM consumers; runtime tests should pair the declarations with `nmblib.c` parser/builder round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/nmblib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/passchange.c -->
# sources/user-network-fs/samba/source3/libsmb/passchange.c

## Purpose
This file implements `remote_password_change`, the client-side routine for changing a user's password on a remote SMB server. It negotiates an IPC connection, tries secure SAMR password-change RPCs, handles password-expired flows, and optionally falls back to the legacy RAP/LanMan password change method when configured.

## Important APIs, Types, And Functions
The exported function is `remote_password_change`. It uses `cli_connect_nb`, `cli_session_creds_init`, `smbXcli_negprot`, `cli_session_setup_creds`, `cli_session_setup_anon`, `cli_tree_connect`, `cli_rpc_pipe_open_with_creds`, `cli_rpc_pipe_open_noauth`, `dcerpc_samr_chgpasswd_user4`, `rpccli_samr_chgpasswd_user2`, `cli_oem_change_password`, and `cli_shutdown`.

## Control Flow
The function connects to the remote machine's NetBIOS server name, creates credentials from domain/user/old password, negotiates the configured IPC protocol range, and attempts authenticated session setup. If the server returns `PASSWORD_MUST_CHANGE` or `PASSWORD_EXPIRED`, it records that state and reconnects the session anonymously so the password-change RPC can proceed.

After connecting to `IPC$`, it opens a SAMR pipe. Normal flow uses NTLMSSP with privacy so the password is protected; must-change flow uses an anonymous SAMR pipe because authenticated bind would fail in the same way as session setup. If pipe open fails and `client lanman auth` allows it, the function falls back to `cli_oem_change_password`; otherwise it returns an explanatory error.

The preferred password operation is `samr_ChangePasswordUser4`. If the server lacks that procedure and weak crypto is disallowed, the function returns `NT_STATUS_STRONG_CRYPTO_NOT_SUPPORTED` instead of falling back to RC4-based methods. Otherwise it tries `samr_ChangePasswordUser2`, then an anonymous pipe with `ChangePasswordUser2`, and finally the RAP/LanMan method if enabled.

## State And Persistence
The only intended persistent effect is the password change on the remote account. Local state is transient connection, credential, and pipe state. Human-readable errors are allocated with `asprintf` into `err_str`, and the SMB connection is shut down on every return path after a successful connect.

## Dependencies And Integration Points
This file integrates NetBIOS connection setup, SMB protocol negotiation, cli credentials, IPC tree connect, SAMR RPC clients, generated NDR SAMR definitions, Samba loadparm settings for transports/protocols/LanMan/weak crypto, and friendly NT error formatting. It is a high-level helper for tools that need password change without manually driving SAMR.

## Risks And Edge Cases
Security-sensitive fallback behavior is central: weak crypto policy prevents fallback from `ChangePasswordUser4` to older RC4-style paths for unsupported procedures, while LanMan fallback is separately gated by `lp_client_lanman_auth()`. Error string allocation failures deliberately leave `*err_str = NULL`. One `asprintf` check after `cli_tree_connect` tests nonzero rather than `-1`, which can clear a successfully allocated error string. Anonymous fallback may be required for expired passwords but should not be used when authenticated secure RPC succeeds.

## Test Signals
Tests should cover connection failure including NetBIOS-disabled `NOT_SUPPORTED`, negotiate failure, normal authenticated SAMR `ChangePasswordUser4`, expired-password anonymous flow, unsupported procnum with weak crypto disallowed, `ChangePasswordUser2` fallback, anonymous SAMR fallback after access denied, LanMan enabled/disabled behavior, password policy rejection messages, and cleanup of `cli` on all error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/passchange.c -->
