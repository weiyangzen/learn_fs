# Research: subset-b-009903

This grouped report covers the requested Samba DNS server and DSDB helper sources. Each section is delimited for deterministic splitting into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_server.c -->
# sources/user-network-fs/samba/source4/dns_server/dns_server.c

## Purpose
`dns_server.c` is the Samba AD DC internal DNS service entry point. It registers the `dns` service, initializes AD-backed DNS state, opens TCP and UDP listeners, accepts packets, dispatches DNS query/update opcodes, signs TSIG replies, truncates large UDP responses, and exposes an IRPC reload hook for zone refreshes.

## Important APIs, Types, and Functions
- `server_service_dns_init()` registers the service with Samba's service framework.
- `dns_task_init()` performs role checks, opens `samdb`, prepares DNS credentials, loads zones, binds interfaces, and registers the `DNSSRV_RELOAD_DNS_ZONES` IRPC handler.
- `dns_process_send()/dns_process_recv()` are the central async DNS packet parser/dispatcher/serializer pair.
- `dns_tcp_accept()`, `dns_tcp_call_loop()`, and callbacks process length-prefixed DNS-over-TCP PDUs through `tstream`.
- `dns_udp_call_loop()` and callbacks process datagram DNS requests through `tdgram`.
- `dns_add_socket()` binds matching TCP and UDP sockets for one local address.
- `dns_server_reload_zones()` rebuilds the in-memory `dns->zones` list using `dns_common_zones()`.
- Local state structs include `dns_socket`, `dns_udp_socket`, `dns_tcp_connection`, `dns_process_state`, `dns_tcp_call`, and `dns_udp_call`.

## Control Flow
Startup rejects standalone/member-server roles and continues only for `ROLE_ACTIVE_DIRECTORY_DC`. If `interfaces` plus `bind interfaces only` is configured, it loads the configured interface list; otherwise it binds wildcard addresses. The task initializes credentials, connects to `samdb` under `system_session()`, prefers a stored `DNS/<dns hostname>` service principal when present, falls back to the machine account, initializes the TKEY store, loads zones, starts sockets, and registers the `dnssrv` IRPC name plus reload handler.

Packet processing validates the minimum DNS header length, NDR-decodes `dns_name_packet`, rejects replies, sets reply flags and recursion availability, copies the input packet into `out_packet`, verifies TSIG, then dispatches by opcode. Query processing is asynchronous through `dns_server_process_query_send/recv`; update processing is synchronous through `dns_server_process_update()`. Unsupported opcodes become `NOT_IMPLEMENTED`.

TCP reads a complete two-byte-length-prefixed PDU, strips the length header, launches packet processing, immediately posts another read for pipelining, and writes a new two-byte length plus response on a send queue. UDP posts a new receive after each datagram, then sends the serialized response on a queued datagram send. UDP responses larger than `DNS_MAX_UDP_PACKET_LENGTH` are rebuilt with `DNS_FLAG_TRUNCATION` and no answer/authority/additional records so clients retry over TCP.

## State and Persistence
Long-lived state is `struct dns_server`: service task, `samdb`, loaded zone list, TKEY ring, and server credentials. Socket and connection state is talloc-scoped under the service/connection. Persistent DNS data lives in AD via helper calls in other files; this file only opens `samdb`, reloads zone metadata, and routes update/query operations. The IRPC reload path atomically swaps the in-memory zone list and frees the old list.

## Dependencies and Integration Points
The file integrates Samba service/task, process model, `tevent`, `tstream`, `tdgram`, socket/interface helpers, NDR DNS codecs, `samdb`, credentials, TSIG helpers, DNS query/update modules, `dnsserver_common`, and IRPC messaging. Configuration inputs include server role, interface binding, DNS port, DNS forwarder, DNS hostname, and socket options.

## Risks and Edge Cases
- Unknown non-OK DNS errors are converted to fallback wire replies by mutating the original packet bytes; this preserves a response but can hide serialization-specific failures.
- UDP truncation depends on rebuilding the packet after mutating `out_packet`; TSIG or future EDNS handling needs care around this path.
- The TKEY store is a fixed-size ring initialized here but managed elsewhere, so long-lived authenticated update behavior depends on external eviction logic.
- `dns_task_init()` contains a redundant `if (!dns_spn)` after successful search; harmless but misleading.
- Zone reload frees the entire old list after swapping; any future code holding zone pointers across reload would be unsafe.

## Test Signals
Coverage is indirect through Samba DNS server integration/torture tests, dynamic update tests, query tests, and IRPC reload paths. Useful focused tests include malformed packets under 12 bytes, reply packets, TSIG failure/signing, TCP pipelining, UDP truncation at 1232 bytes, AD DC role gating, interface binding variants, and zone reload after DB mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_server.h -->
# sources/user-network-fs/samba/source4/dns_server/dns_server.h

## Purpose
`dns_server.h` declares the internal DNS server's shared runtime structures and module-facing APIs. It connects transport startup, query processing, dynamic updates, directory lookup/replacement helpers, zone authority helpers, DNS-name-to-DN mapping, and TSIG/TKEY support.

## Important APIs, Types, and Functions
- `struct dns_server_tkey` stores negotiated TKEY/TSIG security context: key name, mode, algorithm, session info, GENSEC context, and completion state.
- `struct dns_server_tkey_store` is a fixed-size ring of TKEY pointers with `next_idx`.
- `struct dns_server` owns service task, `samdb`, zone list, TKEY store, and DNS server credentials.
- `struct dns_request_state` carries per-request flags, authenticated/signing state, key name, TSIG record, TSIG error, and local/remote socket addresses.
- Query API: `dns_server_process_query_send()` and `dns_server_process_query_recv()`.
- Update API: `dns_server_process_update()`.
- Directory APIs: `dns_lookup_records()`, `dns_lookup_records_wildcard()`, `dns_replace_records()`, `dns_name2dn()`.
- Authority/security APIs: `dns_authoritative_for_zone()`, `dns_get_authoritative_zone()`, `dns_find_tkey()`, `dns_verify_tsig()`, `dns_sign_tsig()`.

## Control Flow
This header defines contracts rather than executing logic. The transport layer fills `dns_request_state`, query/update handlers consume it, TSIG verification may mark it authenticated and requiring response signing, and helper functions map DNS names to AD-backed record operations.

## State and Persistence
No persistence is implemented in the header, but it establishes ownership: process-wide DNS state lives in `struct dns_server`, per-request mutable state lives in `struct dns_request_state`, and persistent records are reached through the declared `samdb` helper APIs.

## Dependencies and Integration Points
It depends on generated DNS/DNSP NDR types, `dnsserver_common.h`, Samba task and credential types through forward declarations/included headers, `tsocket_address`, and DNS crypto/query/update implementations.

## Risks and Edge Cases
- `DNS_MAX_UDP_PACKET_LENGTH` is fixed at 1232 because EDNS(0) is unsupported; adding EDNS support must revisit callers.
- `TKEY_BUFFER_SIZE` is fixed at 128 and does not expose policy details; high churn of authenticated updates could evict keys unexpectedly.
- The header includes `dnsserver_common.h` twice through two paths, which is protected by guards but indicates historical include layering.

## Test Signals
Compile-time coverage comes from all DNS modules that include the header. Behavioral coverage should focus on request state transitions after TSIG verification, UDP size behavior, TKEY lookup/eviction, query/update APIs, and callers that rely on authoritative zone helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_update.c -->
# sources/user-network-fs/samba/source4/dns_server/dns_update.c

## Purpose
`dns_update.c` implements RFC2136-style dynamic DNS updates for Samba's AD-backed DNS server. It validates zone/prerequisite/update sections, checks update policy and TSIG authentication, converts DNS wire records into AD `dnsp_DnssrvRpcRecord` values, and writes changes transactionally to `samdb`.

## Important APIs, Types, and Functions
- `dns_server_process_update()` is the public update entry point.
- `check_one_prerequisite()` and `check_prerequisites()` enforce RFC2136 prerequisite semantics, including `ANY`, `NONE`, and exact RRset tests.
- `update_prescan()` rejects out-of-zone and illegal update records before mutation.
- `dns_rr_to_dnsp()` converts `dns_res_rec` records into `dnsp_DnssrvRpcRecord` values for A, AAAA, NS, CNAME, SRV, PTR, MX, and TXT.
- `handle_one_update()` implements add, replace, mass delete, and individual delete behavior.
- `handle_updates()` wraps prerequisite re-check and update application in an LDB transaction and temporarily sets the authenticated TSIG session info.
- `dns_update_allowed()` enforces `allow dns updates` policy and maps authenticated TSIG keys to sessions.

## Control Flow
The entry point requires exactly one question, class `IN` or `ANY`, type `SOA`, and an authoritative zone match with no delegated host part. It exposes the answer section as prerequisites, checks them once, checks update authorization, exposes the authority section as updates, pre-scans them for syntax/zone validity, then calls `handle_updates()`.

`handle_updates()` optionally swaps `DSDB_SESSION_INFO` to the TSIG-authenticated session, converts the zone name to a DN, starts an LDB transaction, re-checks prerequisites inside the transaction, applies each update through `handle_one_update()`, commits on success, cancels on failure, and restores the system session. The double prerequisite check reduces races between preflight and write.

`handle_one_update()` looks up the target node including tombstones, preserves existing tombstone records by starting after them, detects static names, then branches by update class. Zone-class records add/replace data, enforce CNAME exclusivity, and only update SOA when serial increases. `QCLASS_ANY` tombstones matching records or all eligible records, protecting zone-apex SOA/NS. `QCLASS_NONE` tombstones an individual matching record, with special handling for SOA/NS deletion semantics.

## State and Persistence
Updates persist by replacing the AD `dnsRecord` attribute through `dns_replace_records()`. Deletions are represented as `DNS_TYPE_TOMBSTONE` placeholders passed to `dns_common_replace()`, which decides whether to tombstone individual records or the whole node. Dynamic records receive `dwTimeStamp = unix_to_dns_timestamp(time(NULL))` unless the existing name is static.

## Dependencies and Integration Points
The module depends on NDR DNS/DNSP types, `samdb`, `dsdb` utility functions, Samba configuration, auth session state, DNS common lookup/replacement/name matching helpers, and DNS crypto/TKEY state from `dns_server.h`.

## Risks and Edge Cases
- `dns_rr_to_dnsp()` does not implement every DNS type; unsupported update types return `NOT_IMPLEMENTED`.
- SOA serial comparison uses simple `<=` and has a TODO for RFC1982 serial arithmetic.
- Update authorization allows all updates when configuration is `DNS_UPDATE_ON`; secure deployments should use authenticated/secure policy.
- The update path temporarily mutates LDB opaque session info and must always restore it; current cleanup does this after the transaction path.
- A no-op TTL-only replacement may suppress `WERR_ACCESS_DENIED`, intentionally treating denied identical TTL replacement as success.

## Test Signals
Test coverage should exercise RFC2136 prerequisites (`YXDOMAIN`, `NXDOMAIN`, `YXRRSET`, `NXRRSET`), secure vs insecure update policy, TSIG key lookup failures, transactional rollback on a later update failure, CNAME exclusivity, zone-apex SOA/NS deletion protection, tombstoned node resurrection, and unsupported RR types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_utils.c -->
# sources/user-network-fs/samba/source4/dns_server/dns_utils.c

## Purpose
`dns_utils.c` is a thin adapter between the DNS server runtime and the shared `dnsserver_common` AD database helpers. It gives server modules concise functions for exact/wildcard record lookup, record replacement, authority checks, authoritative zone selection, and DNS-name-to-LDB-DN conversion.

## Important APIs, Types, and Functions
- `dns_lookup_records()` calls `dns_common_lookup()` for exact, non-wildcard lookup.
- `dns_lookup_records_wildcard()` calls `dns_common_wildcard_lookup()` to allow wildcard fallback.
- `dns_replace_records()` calls `dns_common_replace()` with a hard-coded serial value.
- `dns_authoritative_for_zone()` checks whether a DNS name falls under any loaded zone and treats the empty name as authoritative.
- `dns_get_authoritative_zone()` returns the first loaded matching zone name.
- `dns_name2dn()` delegates to `dns_common_name2dn()` using `dns->samdb` and `dns->zones`.

## Control Flow
All functions are direct wrappers except the two zone authority helpers. Authority matching iterates the loaded `dns->zones` list and uses `dns_name_match()` to compare suffixes case-insensitively while computing host-part length. `dns_get_authoritative_zone()` returns on the first match; zone sorting in `dns_common_zones()` makes this prefer longer/specific zones.

## State and Persistence
This file owns no durable state. It reads `dns->zones` and `dns->samdb`, and replacement persists by forwarding to `dns_common_replace()`. The static `dwSerial = 110` in `dns_replace_records()` is written into records by common replacement code.

## Dependencies and Integration Points
Dependencies are `samdb`, `dns_server.h`, and `dnsserver_common` helpers. Query and update modules use these wrappers so they do not need to know the lower-level common helper signatures.

## Risks and Edge Cases
- The hard-coded serial `110` is marked TODO and may not represent real SOA serial behavior.
- Authority checks rely on the in-memory zone list being current; IRPC reload is required after zone changes.
- The empty root name is treated as authoritative independent of loaded zones.

## Test Signals
Useful tests include exact vs wildcard lookup behavior, authoritative matching with overlapping zones, empty-name/root behavior, stale-zone-list behavior before/after reload, and verification that replacements carry the expected serial/tombstone semantics from `dns_common_replace()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dns_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dnsserver_common.c -->
# sources/user-network-fs/samba/source4/dns_server/dnsserver_common.c

## Purpose
`dnsserver_common.c` is the shared AD DNS database implementation used by the internal DNS server, BIND DLZ modules, and Python tooling. It maps WERRORs to DNS rcodes, decodes and encodes `dnsRecord` NDR blobs, looks up exact and wildcard DNS nodes, validates DNS names and target names, manages tombstone/aging behavior, maps DNS names to AD DNs, enumerates zones, compares records, and converts DNS timestamps.

## Important APIs, Types, and Functions
- `werr_to_dns_err()` maps Samba/WERROR status to DNS wire rcodes.
- `dns_common_extract()` decodes `dnsRecord` values into `dnsp_DnssrvRpcRecord` arrays and overwrites SOA MNAME with the local DNS hostname on writable DCs.
- `dns_common_lookup()` performs exact base-object lookup and can include tombstoned nodes for update handling.
- `dns_common_wildcard_lookup()` performs exact lookup first and then wildcard fallback using `build_wildcard_query()` and `get_best_match()`.
- `dns_name_check()` enforces DNS label/name limits.
- `dns_get_zone_properties()` and `dns_zoneinfo_load_zone_property()` decode `dNSProperty` values into RPC zone info, especially aging/scavenging data.
- `dns_common_replace()` encodes replacement records, applies aging refresh, handles tombstone transitions, and calls `ldb_add()` or `ldb_modify()`.
- `dns_common_name2dn()` maps DNS names to `DC=<host>,DC=<zone>,...` nodes, with `DC=@` for zone apex.
- `dns_record_match()`, `dns_name_match()`, `samba_dns_name_equal()`, `dns_common_zones()`, `unix_to_dns_timestamp()`, and `dns_timestamp_to_nt_time()` provide shared matching, zone enumeration, and time conversion.

## Control Flow
Lookup begins with an LDB search for `objectClass=dnsNode`, optionally excluding `dNSTombstoned=TRUE`. Missing objects become `WERR_DNS_ERROR_NAME_DOES_NOT_EXIST`; malformed or failed searches become DNS name/server errors. Extract decodes each NDR record and adjusts SOA MNAME on writable DCs.

Wildcard lookup validates the RDN, skips wildcarding for `@`, performs an exact lookup, and only on missing records builds an LDB parse tree matching the exact name plus progressively shorter `*.<suffix>` candidates. The longest candidate wins unless an exact match is present.

Replacement builds an LDB message with `dnsRecord` replace semantics, loads zone properties for aging, validates target names inside records, sorts records by type descending then timestamp ascending, filters deletion tombstone placeholders, refreshes timestamps when aging/no-refresh rules allow, stamps serial, NDR-encodes records, adds a new `dnsNode` when requested, or modifies an existing node. If no live records remain, it writes a real tombstone record and `dNSTombstoned=TRUE`; if resurrecting, it flips tombstoned false.

Name-to-DN conversion handles the empty root server name specially, validates names, finds the authoritative zone, maps the apex to `DC=@`, maps non-apex host parts to a single `DC` RDN, validates/casefolds the DN, and returns it.

## State and Persistence
Persistent state is AD DS data: `dnsZone` objects, `dnsNode` objects, `dnsRecord` NDR values, `dNSTombstoned`, and `dNSProperty`. The module also uses rootDSE/local `dnsHostName`, RODC status, and zone aging properties to shape returned or stored records. Timing logs are emitted when DNS debug is high.

## Dependencies and Integration Points
The code depends on LDB/DSDB search and modify helpers, generated DNS/DNSP NDR codecs, RPC DNS server structures, network address parsing for AAAA comparison, dlink-list zone structures, and Samba time utilities. It is intentionally shared by internal DNS, DLZ, and Python bindings.

## Risks and Edge Cases
- Wildcard query construction assumes the RDN name is validated and NUL-terminated; callers must not bypass validation.
- `dns_name_check()` is called with `strlen()` in many paths and therefore cannot validate embedded NUL unless the caller uses length-aware input first.
- Tombstone handling has nuanced placeholder vs persisted tombstone semantics; wrong `EntombedTime` values can change deletion behavior.
- Zone sorting only sorts by length and has a TODO for partition priority, so equal-length duplicate zone names across partitions depend on search order.
- Aging refresh uses unsigned arithmetic on DNS timestamps; unusual/future timestamps may behave unexpectedly.

## Test Signals
Coverage should include NDR extract failures, SOA MNAME rewrite on writable DC vs RODC, exact and wildcard lookup ordering, invalid DNS names, target-name validation in CNAME/MX/NS/PTR/SRV/SOA, adding nodes, replacing existing records, tombstoning and resurrection, zone property decoding, zone enumeration exclusions for `RootDNSServers` and `..TrustAnchors`, record matching for IPv6 canonical forms, and timestamp overflow conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dnsserver_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dnsserver_common.h -->
# sources/user-network-fs/samba/source4/dns_server/dnsserver_common.h

## Purpose
`dnsserver_common.h` declares the shared DNS database helper interface used across Samba DNS components. It defines the zone list type, WERROR-to-DNS helpers, record lookup/extract/replace contracts, name validation/matching, zone enumeration, zone property loading, operation logging, and DNS timestamp conversion.

## Important APIs, Types, and Functions
- `DNS_ERR()` creates DNS RCODE-flavored WERROR constants; `werr_to_dns_err()` converts them to wire rcodes.
- `struct dns_server_zone` links zone name and LDB DN in a doubly linked list.
- Lookup/extract APIs: `dns_common_extract()`, `dns_common_lookup()`, `dns_common_wildcard_lookup()`.
- Mutation API: `dns_common_replace()`.
- Validation/mapping APIs: `dns_name_check()`, `dns_name_match()`, `dns_common_name2dn()`, `samba_dns_name_equal()`.
- Metadata APIs: `dns_get_zone_properties()`, `dns_zoneinfo_load_zone_property()`, `dns_common_zones()`.
- Record/time APIs: `dns_name_is_static()`, `dns_record_match()`, `unix_to_dns_timestamp()`, `dns_timestamp_to_nt_time()`.
- `DNS_COMMON_LOG_OPERATION` emits duration/result/zone/name/data debug logs.

## Control Flow
The header sets a layered contract: callers enumerate zones, map DNS names to DNs, look up or replace `dnsRecord` values, and translate internal errors to DNS protocol rcodes. It also makes logging consistent for common operations by wrapping debug-level timing output in a macro.

## State and Persistence
No state is stored in the header. It describes AD-backed persistence through `ldb_context`, `ldb_dn`, `dns_server_zone`, `dnsp_DnssrvRpcRecord`, and `dnsserver_zoneinfo` parameters. `NTTIME_TO_HOURS` defines the timestamp conversion unit used for persisted DNS aging timestamps.

## Dependencies and Integration Points
The header includes RPC DNS server declarations and forward-declares LDB/DNSP structures. It is consumed by internal DNS service code, DLZ code, Python bindings, and likely DNS RPC management paths.

## Risks and Edge Cases
- The macro `DNS_COMMON_LOG_OPERATION` evaluates supplied expressions into local variables; callers should avoid side-effect expressions.
- Callers must understand whether `dns_common_lookup()` should include tombstoned nodes via a non-NULL `tombstoned` pointer.
- The shared API exposes low-level replacement semantics, so misuse can tombstone or resurrect nodes.

## Test Signals
Header contracts are exercised by compilation and by tests around common implementation. ABI/API-sensitive tests should include callers from internal DNS, DLZ, and Python modules to catch signature or semantic drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/dnsserver_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/pydns.c -->
# sources/user-network-fs/samba/source4/dns_server/pydns.c

## Purpose
`pydns.c` implements the `samba.dsdb_dns` Python extension. It exposes selected AD DNS database helpers to Python so tooling can look up, extract, replace, compare, and timestamp DNS records using the same C implementation as the server.

## Important APIs, Types, and Functions
- `py_dnsp_DnssrvRpcRecord_get_list()` converts C `dnsp_DnssrvRpcRecord` arrays to Python `samba.dcerpc.dnsp.DnssrvRpcRecord` objects.
- `py_dnsp_DnssrvRpcRecord_get_array()` validates and copies a Python list of DNSP records into a C array.
- Python methods: `lookup`, `extract`, `replace`, `replace_by_dn`, `records_match`, `unix_to_dns_timestamp`, and `dns_timestamp_to_nt_time`.
- `MODULE_INIT_FUNC(dsdb_dns)` creates the extension module.

## Control Flow
`lookup(ldb, dns_name, dns_partition=None)` validates the Python LDB object, optionally accepts a DNS partition DN, enumerates zones, maps the DNS name to a DN, exact-lookups records, and returns `(dn, records)`. `extract(ldb, message_element)` decodes a raw `dnsRecord` LDB message element. `replace(ldb, dns_name, records)` maps name to DN and calls common replacement. `replace_by_dn(ldb, dn, records)` skips name mapping and replaces by supplied DN. `records_match()` delegates to C update matching semantics. Timestamp helpers validate Python integer ranges and call common conversion routines.

## State and Persistence
The module does not own persistent state, but `replace` and `replace_by_dn` mutate AD DNS records through `dns_common_replace()`. Both use the same hard-coded serial `110` as the internal DNS utility wrapper and pass `needs_add=false`, so they replace existing nodes rather than creating absent ones.

## Dependencies and Integration Points
It depends on Python C API compatibility headers, pyldb, pytalloc, Samba Python module registration, generated DNSP NDR Python bindings, LDB/SAMDB, and `dnsserver_common`. The build file installs it as `samba/dsdb_dns.so`.

## Risks and Edge Cases
- `PyList_SetItem()` steals references; the code assumes `py_return_ndr_struct()` succeeds for each item and does not explicitly handle NULL per item.
- `py_dnsp_DnssrvRpcRecord_get_array()` returns early on type/reference failure without freeing intermediate references until the stack frame is freed by callers.
- `replace()` cannot add a missing DNS node because `needs_add=false`.
- Timestamp conversion rejects values outside C `time_t` or uint32/NTTIME range, which is correct but visible to Python callers.

## Test Signals
Useful tests include Python lookup with and without DNS partition, extract from raw `dnsRecord`, replace existing records, replace missing-name failure, record matching parity with server update semantics, invalid Python object types, and timestamp conversion boundary values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/pydns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/wscript_build -->
# sources/user-network-fs/samba/source4/dns_server/wscript_build

## Purpose
`wscript_build` defines how Samba builds the DNS server components, BIND DLZ modules, shared DNS common library, and Python DNS bindings. It encodes which pieces are AD-DC-only and which remain available for client-side tooling.

## Important APIs, Types, and Functions
- `bld.SAMBA_LIBRARY('dnsserver_common', ...)` builds the shared common helper library independently of AD DC enablement.
- `bld.SAMBA_MODULE('service_dns', ...)` builds the internal DNS service module from server, query, update, utility, and crypto sources.
- `bld.SAMBA_LIBRARY('dlz_bind9_*', ...)` builds version-specific BIND DLZ modules for 9.10, 9.11, 9.12, 9.14, 9.16, and 9.18 plus a torture variant.
- `bld.SAMBA_PYTHON('python_dsdb_dns', ...)` builds `samba/dsdb_dns.so` from `pydns.c`.

## Control Flow
This build script is declarative. `dnsserver_common` is always declared as a private library so imports and tools can work even when AD DC support was not built. The internal DNS service and DLZ modules are gated by `bld.AD_DC_BUILD_IS_ENABLED()`. Python utility library names are discovered through `bld.pyembed_libname()` before building the Python extension.

## State and Persistence
No runtime state is persisted here. Build outputs include private libraries, service modules, installed BIND module `.so` files, and the Python extension.

## Dependencies and Integration Points
Dependencies tie DNS code into `samba-hostconfig`, `LIBTSOCKET`, `LIBSAMBA_TSOCKET`, `ldbsamba`, `clidns`, `gensec`, `auth`, `samba_server_gensec`, `samdb-common`, `popt`, and Python embedding utilities. DLZ modules install under `${MODULESDIR}/bind9`.

## Risks and Edge Cases
- New BIND versions require adding another near-duplicate `dlz_bind9_*` target.
- `dnsserver_common` intentionally has a wider build surface than service DNS; dependency additions there should not accidentally require AD DC-only libraries.
- Service DNS is `internal_module=False`, so packaging/module installation assumptions matter.

## Test Signals
Build tests should cover AD DC enabled and disabled configurations, Python extension import without AD DC service build, all supported BIND DLZ target variants, and dependency changes that might break standalone tooling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dns_server/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/dsdb_access.c -->
# sources/user-network-fs/samba/source4/dsdb/common/dsdb_access.c

## Purpose
`dsdb_access.c` provides utility functions for checking access to DSDB objects outside the normal LDB module stack. It retrieves security descriptors, builds optional object-specific access trees, runs Windows-style security descriptor checks, and emits detailed debug output for grant/deny decisions.

## Important APIs, Types, and Functions
- `dsdb_acl_debug()` logs the DN, security token, and security descriptor.
- `dsdb_get_sd_from_ldb_message()` extracts and NDR-decodes `nTSecurityDescriptor` from an LDB message.
- `dsdb_check_access_on_dn_internal()` evaluates a supplied search result/security descriptor against a token, access mask, optional GUID, and object SID.
- `dsdb_check_access_on_dn()` searches the target DN as system for `nTSecurityDescriptor` and `objectSid`, parses an optional extended-right GUID string, and invokes the internal checker.

## Control Flow
The public checker optionally parses `ext_right` into a GUID, searches the target DN with `DSDB_FLAG_AS_SYSTEM | DSDB_SEARCH_SHOW_RECYCLED` to obtain security data, then delegates. The internal checker decodes the SD, gets `objectSid`, optionally inserts the GUID/access mask into an object tree, and calls `sec_access_check_ds()`. Failed checks log full debug context, set an LDB error string, and return `LDB_ERR_INSUFFICIENT_ACCESS_RIGHTS`.

## State and Persistence
The file does not mutate persistent state. It reads security descriptor and SID attributes from DSDB and allocates transient decoded structures on caller-provided talloc contexts.

## Dependencies and Integration Points
It depends on LDB, LDB modules/errors, NDR security decoding, Samba security token/descriptor checks, loadparm/auth types, SAMDB search utilities, and object-tree ACL helpers.

## Risks and Edge Cases
- Missing `nTSecurityDescriptor` is treated as insufficient access; malformed NDR becomes an operational error.
- The public search uses AS_SYSTEM intentionally; callers must ensure the checked `token` is the user/security context being authorized.
- Full security tokens/descriptors are logged at the requested debug level, which is useful but sensitive.

## Test Signals
Coverage should include allow and deny paths, missing/malformed SDs, invalid extended-right GUID strings, object-specific GUID checks, recycled object lookup, and error-string behavior. No direct test in this work item targets this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/dsdb_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/dsdb_dn.c -->
# sources/user-network-fs/samba/source4/dsdb/common/dsdb_dn.c

## Purpose
`dsdb_dn.c` implements Samba DSDB DN wrapper handling for normal DNs, DN+Binary, DN+String, and DRS object identifiers. It parses and formats prefixed DN syntaxes, canonicalizes/comparisons for LDB schema handlers, and safely converts replication object identifiers into normalized database DNs.

## Important APIs, Types, and Functions
- `dsdb_dn_oid_to_format()` maps syntax OIDs to `DSDB_NORMAL_DN`, `DSDB_BINARY_DN`, `DSDB_STRING_DN`, or invalid.
- `dsdb_dn_construct()` and `dsdb_dn_construct_internal()` assemble `struct dsdb_dn` with a base DN, extra prefix blob, format, and OID.
- `dsdb_dn_parse_trusted()` parses raw LDB values for normal, `B:<hexlen>:<hex>:<dn>`, and `S:<len>:<string>:<dn>` forms.
- `dsdb_dn_parse()` adds `ldb_dn_validate()` on top of trusted parsing.
- `dsdb_dn_get_linearized()`, `dsdb_dn_get_casefold()`, and `dsdb_dn_get_extended_linearized()` format the wrapper.
- `dsdb_dn_binary_canonicalise/comparison()` and string equivalents support LDB syntax comparisons.
- `drs_ObjectIdentifier_to_debug_string()` and `drs_ObjectIdentifier_to_dn_and_nc_root()` handle DRS object identifiers, prioritizing GUID, then SID, then string DN.

## Control Flow
Parsing starts from the syntax OID. Normal DNs are parsed directly and must have no extra part. Binary and string DNs require `B:` or `S:` prefixes, reject embedded NUL by comparing `strlen()` to blob length, parse the declared prefix length, require separator placement, decode hex bytes for binary prefixes, preserve string prefix bytes for string prefixes, parse the trailing DN, then construct the wrapper. Public parsing validates the resulting DN.

Formatting delegates to the underlying LDB DN for the postfix and prepends the appropriate `B:` or `S:` prefix. Canonicalization parses then returns the casefolded representation, making DN comparisons case-insensitive while keeping binary hex uppercase and string prefixes case-sensitive.

DRS object identifier conversion refuses ambiguous/unsafe inputs by honoring GUID/SID priority, validating string DNs, rejecting empty/special/extended DNs, and finally normalizing against the DB while finding the naming-context root.

## State and Persistence
No persistent state is changed. The file creates transient `dsdb_dn`, `ldb_dn`, prefix blobs, debug strings, and normalized DNs. Its comparison/canonicalization output can affect indexed LDB matching and schema behavior.

## Dependencies and Integration Points
Dependencies include SAMDB, LDB module APIs, NDR utilities, domain SID utilities, SMB numeric parsing, GUID/SID formatting, and `dsdb_normalise_dn_and_find_nc_root()`. It is exercised by LDB Samba syntax handlers and DRS replication code.

## Risks and Edge Cases
- DN+Binary length is measured in hex characters and must be even; malformed length/separator combinations are rejected.
- `dsdb_dn_parse_trusted()` skips final `ldb_dn_validate()` by design; callers must use it only for trusted values.
- String prefix bytes are not casefolded, while the DN postfix is.
- DRS string DNs are user-controlled and deliberately avoid logging raw unparsed values in some failure paths.

## Test Signals
`source4/dsdb/common/tests/dsdb_dn.c` directly covers valid construction/parsing, canonicalization/comparison behavior, invalid binary/string prefixes, extended DN rejection for binary syntax, newline/NUL invalid cases, and casefold expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/dsdb_dn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/dsdb_dn.h -->
# sources/user-network-fs/samba/source4/dsdb/common/dsdb_dn.h

## Purpose
`dsdb_dn.h` defines the `struct dsdb_dn` data container, DSDB DN syntax OID constants, and RMD flag constants used by DSDB link/DN handling code.

## Important APIs, Types, and Functions
- `struct dsdb_dn` contains the parsed underlying `ldb_dn`, the binary/string `extra_part`, the `dn_format`, and the source syntax `oid`.
- `DSDB_SYNTAX_BINARY_DN`, `DSDB_SYNTAX_STRING_DN`, `DSDB_SYNTAX_OR_NAME`, and `DSDB_SYNTAX_ACCESS_POINT` identify schema syntaxes.
- `DSDB_RMD_FLAG_DELETED` marks deleted linked-value metadata.
- `DSDB_RMD_FLAG_HIDDEN_BL` marks backlink values hidden because the backlink is not allowed by object class.

## Control Flow
The header has no executable flow. It defines the shared layout that `dsdb_dn.c`, schema handlers, and link-processing code use to interpret DN-valued attributes with optional metadata prefixes.

## State and Persistence
The struct represents parsed state from LDB attribute values. RMD flags correspond to metadata persisted in extended DN/link values elsewhere in DSDB.

## Dependencies and Integration Points
The type assumes `struct ldb_dn`, `DATA_BLOB`, and `enum dsdb_dn_format` are declared by including contexts. It is part of DSDB common infrastructure and supports DN parsing/canonicalization and linked-attribute handling.

## Risks and Edge Cases
- The header exposes raw fields, so callers can mutate parsed DN state directly; invariants rely on disciplined use of constructor/parser helpers.
- OID constants must remain aligned with schema syntax handling.

## Test Signals
Direct test signal comes through `dsdb_dn.c` tests that inspect `extra_part.length`, formatted output, and syntax-specific parsing behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/dsdb_dn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/rodc_helper.c -->
# sources/user-network-fs/samba/source4/dsdb/common/rodc_helper.c

## Purpose
`rodc_helper.c` enforces whether a Read-Only Domain Controller is allowed to replicate secrets for a target account. It parses SID lists from RODC policy attributes and object token groups, applies deny/allow group policy, and protects krbtgt/trust accounts.

## Important APIs, Types, and Functions
- `sid_list_match()` checks for overlap between two SID arrays.
- `samdb_result_sid_array_ndr()` reads NDR-encoded SIDs from an LDB message attribute and prepends the object's primary SID.
- `samdb_result_sid_array_dn()` reads extended-DN SID components from attributes such as `msDS-NeverRevealGroup`.
- `samdb_confirm_rodc_allowed_to_repl_to_sid_list()` applies the core RODC reveal/never-reveal policy to a supplied token SID list.
- `samdb_confirm_rodc_allowed_to_repl_to()` builds the token SID list from `objectSid` and `tokenGroups`, then delegates.

## Control Flow
The core policy first denies attempts involving RODC krbtgt trust backlinks or inter-domain trust accounts. It verifies the alleged RODC account has `UF_PARTIAL_SECRETS_ACCOUNT`. It parses never-reveal and reveal-on-demand group SID lists from the RODC object. The RODC may replicate for itself. Any match with never-reveal denies. Any match with reveal-on-demand allows. Otherwise replication is denied.

The wrapper obtains the target object's primary SID, reads `tokenGroups` in NDR form while placing the primary SID at index zero, and invokes the core policy. Missing object SID or tokenGroups failures become DRA errors.

## State and Persistence
The module reads DSDB attributes but does not mutate them. Inputs are RODC account message attributes, target object account attributes, and token group SIDs. Results are WERROR policy decisions such as `WERR_OK`, `WERR_DS_DRA_SECRETS_DENIED`, `WERR_DOMAIN_CONTROLLER_NOT_FOUND`, and `WERR_DS_DRA_BAD_DN`.

## Dependencies and Integration Points
It depends on DCERPC server headers, generated security NDR, SAMDB helpers, Samba SID/security functions, `userAccountControl` flags, extended DN SID extraction, and replication/KDC callers that need RODC secret policy decisions.

## Risks and Edge Cases
- SID overlap is O(n^2), noted as acceptable for expected list sizes.
- Failure to parse reveal/never-reveal policy fails closed with secrets denied.
- The wrapper currently notes a TODO about whether `sIDHistory` should be considered.
- The core function indexes `token_sids[PRIMARY_USER_SID_INDEX]`; callers must supply a non-empty token SID array.

## Test Signals
Needed tests include RODC self-replication allow, never-reveal denial precedence, reveal-on-demand allow, default deny, non-RODC account rejection, krbtgt/trust-account denial, malformed SID attributes, missing tokenGroups/objectSid, and policy with overlapping groups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/rodc_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/tests/dsdb.c -->
# sources/user-network-fs/samba/source4/dsdb/common/tests/dsdb.c

## Purpose
`tests/dsdb.c` registers a small DSDB torture suite and currently tests that an untrusted LDB search with an explicitly empty attribute list returns entries with zero attributes.

## Important APIs, Types, and Functions
- `torture_ldb_no_attrs()` is the test body.
- `torture_dsdb_init()` creates and registers the `dsdb` torture suite.
- The test uses `ldb_wrap_connect()`, `admin_session()`, `ldb_build_search_req()`, `ldb_req_mark_untrusted()`, `ldb_request()`, and `ldb_wait()`.

## Control Flow
The test obtains the private `sam.ldb` path from loadparm, creates an admin session using the Builtin domain SID, connects to the SAM LDB, builds a subtree search under `cn=users` with `attrs[] = { NULL }`, marks the request untrusted, executes and waits for completion, asserts at least one result, and asserts the first result has `num_elements == 0`.

## State and Persistence
The test is read-only. It depends on an existing `sam.ldb` from a configured test environment and the Users container containing at least one object.

## Dependencies and Integration Points
It integrates with Samba torture registration, LDB wrapper connection, auth session creation, loadparm private paths, and LDB request trust marking. The behavior under test relates to DSDB search filtering and attribute disclosure for untrusted requests.

## Risks and Edge Cases
- The test requires a configured `sam.ldb`; it fails early if run without `-s $SERVERCONFFILE`.
- It assumes the Users container is non-empty.
- It only checks the first result's attributes, not all returned entries.

## Test Signals
This file itself is a test signal for untrusted no-attribute searches. Additional strengthening would assert every result has zero attributes and add a trusted/control comparison.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/tests/dsdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/tests/dsdb_dn.c -->
# sources/user-network-fs/samba/source4/dsdb/common/tests/dsdb_dn.c

## Purpose
`tests/dsdb_dn.c` is the local torture coverage for DSDB DN syntax parsing, formatting, canonicalization, comparison, and invalid input rejection for normal DNs, DN+Binary, and DN+String.

## Important APIs, Types, and Functions
- `torture_dsdb_dn_attrs()` tests LDB syntax handler comparison and canonicalization for `DSDB_SYNTAX_BINARY_DN` and `DSDB_SYNTAX_STRING_DN`.
- `torture_dsdb_dn_valid()` tests construction, parsing, linearization, extended linearization, casefolding, and extra-part lengths.
- `torture_dsdb_dn_invalid()` tests malformed normal, binary, string, extended, newline, and NUL-containing inputs.
- `torture_dsdb_dn()` registers the `dsdb.dn` suite with `valid`, `invalid`, and `attrs` tests.

## Control Flow
Each test initializes an LDB context, registers Samba handlers, and configures UTF-8 casefold functions. Attribute tests fetch the schema syntax by OID and call comparison/canonicalization functions directly. Valid tests build LDB DNs and `dsdb_dn` wrappers, then assert exact string forms. Invalid tests feed malformed `ldb_val` blobs to `dsdb_dn_parse()` and assert rejection, with one newline normal-DN case downgraded to a warning pending DEL DN understanding.

## State and Persistence
The tests use only in-memory LDB contexts and talloc allocations. No database is opened or modified.

## Dependencies and Integration Points
Dependencies include Samba LDB syntax handlers, wrap casefold functions, DSDB DN parser/formatter implementation, and torture assertion utilities. The tests are direct regression protection for `dsdb_dn.c` and schema syntax registration.

## Risks and Edge Cases
- The normal DN newline case is a warning rather than a hard failure, documenting an unresolved ambiguity.
- Tests assert exact string/casefold formatting, so intentional formatting changes require coordinated test updates.
- Invalid tests cover many prefix length/hex failures but not every possible malformed separator or integer overflow case.

## Test Signals
This is strong focused coverage for DN+Binary and DN+String behavior: case-insensitive binary hex, case-sensitive string prefix, case-insensitive DN postfix, zero-length binary prefix, invalid length mismatch, invalid hex, `0x` prefix rejection, extended DN rejection, and embedded NUL rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/tests/dsdb_dn.c -->
