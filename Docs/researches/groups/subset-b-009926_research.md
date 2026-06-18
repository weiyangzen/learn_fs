# Research: subset-b-009926

Grouped source-aligned research for Samba KDC files in `sources/user-network-fs/samba/source4/kdc`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/db-glue.c -->
# sources/user-network-fs/samba/source4/kdc/db-glue.c

## Purpose
`db-glue.c` is the main translation layer between Samba AD directory records and the Kerberos database entry shape consumed by the Heimdal/MIT KDC integration. It fetches user, service, krbtgt, RODC krbtgt, and trust accounts from `sam.ldb`, converts LDAP/DSDB attributes into `sdb_entry` fields, derives Kerberos keys and etype metadata, evaluates account policy, handles realm referrals, and exposes delegation and PKINIT matching checks.

## Important APIs, Types, And Functions
Key exported APIs are `samba_kdc_fetch`, `samba_kdc_firstkey`, `samba_kdc_nextkey`, `samba_kdc_message2entry_keys`, `samba_kdc_set_fixed_keys`, `samba_kdc_check_client_matches_target_service`, `samba_kdc_check_pkinit_ms_upn_match`, `samba_kdc_check_s4u2proxy`, `samba_kdc_setup_db_ctx`, and `dsdb_extract_aes_256_key`. Internal conversion pivots are `samba_kdc_message2entry`, `samba_kdc_fetch_client`, `samba_kdc_fetch_server`, `samba_kdc_fetch_krbtgt`, `samba_kdc_trust_message2entry`, `samba_kdc_fill_user_keys`, and `samba_kdc_fill_trust_keys`. `struct samba_kdc_entry` objects are attached to `sdb_entry->skdc_entry` and retained on the KDC DB context; the destructor refuses free while either an `sdb_entry` or KDC/HDB entry still references it. `SAMBA_KVNO_GET_*`/`SAMBA_KVNO_AND_KRBTGT` pack RODC krbtgt identity into the upper 16 bits of kvno.

## Control Flow
`samba_kdc_fetch` first enforces optional AS canonicalization, allocates a request context, runs `samba_kdc_lookup_realm` for local/referral decisions, then tries client lookup, krbtgt/trust lookup, server lookup, or explicit krbtgt lookup depending on SDB flags. LDAP messages are converted by `samba_kdc_message2entry`, which sets SDB flags from `userAccountControl`, canonicalizes principals, applies server/client/krbtgt role-specific account restrictions, ticket lifetimes, protected-user behavior, authentication policies, supported etypes, and key material. `samba_kdc_message2entry_keys` parses `unicodePwd`, `ntPwdHistory`, and `supplementalCredentials` `Primary:Kerberos-Newer-Keys`, selects requested/current/old/older kvnos, creates keyblocks, supports random placeholder keys for user-to-user and smartcard-required client cases, merges recent gMSA old keys for PA-DATA decryption, and strips DES. Trust lookup routes `krbtgt/remote` principals through trusted-domain objects, selects incoming/outgoing trust secrets, prefers previous keys for one hour after trust password changes, and builds cross-realm krbtgt entries.

## State And Persistence Behavior
Persistent state is read and sometimes updated in `sam.ldb`. Most paths use `DSDB_SEARCH_UPDATE_MANAGED_PASSWORDS`, so generated managed passwords can be refreshed during lookup. Missing RODC secrets trigger `auth_sam_trigger_repl_secret` to ask `dreplsrv` to replicate secrets, then return `SDB_ERR_NOT_FOUND_HERE` so the request can be proxied to a writable DC. `smartcard_random_pw_update` may transactionally reset a soon-to-expire `UF_SMARTCARD_REQUIRED` account password to a random value to avoid PKINIT breakage from underlying password expiry. `samba_kdc_setup_db_ctx` opens a non-shared system-session `samdb`, installs the current-time pointer used by gMSA modules, discovers whether this DC is an RODC, and stores the appropriate krbtgt DN and local RODC krbtgt number.

## Dependencies And Integration Points
This file depends on DSDB/SAMDB lookup helpers, trust routing, password hash modules, gMSA utilities, Kerberos principal/key helpers, SDB conversion helpers, PAC glue, authn policy helpers, IRPC messaging, DRS blob NDR parsers, key credential link parsing, and Samba loadparm policy. It is called from the HDB adapter in `hdb-samba4.c`, from DSDB key extraction consumers through `dsdb_extract_aes_256_key`, and by KDC delegation/PKINIT plugin hooks. It is also a key participant in RODC behavior because `SDB_ERR_NOT_FOUND_HERE` becomes a proxy signal in the KDC request path.

## Risks
The file is security-critical. High-risk areas include canonicalization and implicit trailing-dollar fallback, realm referral decisions, packed RODC kvno handling, trust-direction selection, old-key inclusion, RC4 fallback, stripping weak krbtgt keys, protected-user enforcement, smartcard-required password rotation, and parsing of binary credential blobs. A fail-open bug in account-computed-control handling, missing SPN checks, trust routing, or certificate/key-trust mapping could affect authentication or delegation. Memory ownership is mixed between talloc, malloc, Heimdal keyblocks, and SDB free helpers, so error paths must keep `sdb_entry_free` behavior correct. RODC `SDB_ERR_NOT_FOUND_HERE` decisions must stay precise to avoid either local false denial or inappropriate proxying.

## Test Signals
Useful signals include Samba KDC selftests for AS/TGS canonicalization, `krbtgt` and RODC kvno selection, trust tickets, S4U2Self/S4U2Proxy/RBCD, PKINIT UPN and certificate mapping, key-trust logon, gMSA password rollover, Protected Users, DES/RC4/AES etype policy, kadmin/keytab export iteration, RODC missing-secret proxy behavior, and smartcard-required password rotation. Negative tests should cover malformed `supplementalCredentials`, duplicate/invalid `msDS-KeyCredentialLink` entries, unsupported trust attributes, non-UPLEVEL trusts, absent `msDS-User-Account-Control-Computed`, and no-SPN server entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/db-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/db-glue.h -->
# sources/user-network-fs/samba/source4/kdc/db-glue.h

## Purpose
`db-glue.h` declares the public interface for Samba's KDC database glue. It lets KDC/HDB code fetch principals, iterate entries, convert DSDB messages into key material, validate special Kerberos relationships, and initialize per-KDC database context.

## Important APIs, Types, And Functions
The header forward-declares `struct sdb_keys`, `struct sdb_entry`, `struct samba_kdc_base_context`, `struct samba_kdc_db_context`, and `struct samba_kdc_entry`. `enum samba_kdc_ent_type` distinguishes client, server, krbtgt, trust, and any-entry conversions. Public functions include `samba_kdc_message2entry_keys`, `samba_kdc_set_fixed_keys`, `samba_kdc_fetch`, sequential iteration via `samba_kdc_firstkey`/`samba_kdc_nextkey`, delegation and PKINIT checks, `samba_kdc_setup_db_ctx`, and `dsdb_extract_aes_256_key`.

## Control Flow
Consumers typically call `samba_kdc_setup_db_ctx` once, then use `samba_kdc_fetch` for single-principal lookups or first/next iteration for keytab/admin export. `samba_kdc_message2entry_keys` is exposed separately so DSDB code can parse Kerberos keys without duplicating the complicated credential parsing in `db-glue.c`.

## State And Persistence Behavior
The declarations expose DB context construction but not the fields. State lives in the opaque `samba_kdc_db_context`, which owns SAMDB access, policy, current-time pointers, iteration state, and krbtgt identity. The header itself has no persistence behavior.

## Dependencies And Integration Points
The API crosses Samba DSDB, Heimdal/MIT SDB/HDB, Kerberos principal/key handling, and KDC plugin code. It is included by the HDB adapter, KDC glue header, and any DSDB module that needs AES key extraction.

## Risks
Because this header publishes low-level security operations, flag semantics must remain stable. Callers must pass the correct entity type and SDB flags; wrong flags can expose history keys, suppress policy checks, or return a client when a server was required.

## Test Signals
Build tests should catch prototype drift. Runtime tests should exercise each exported path through HDB fetch, keytab export, PKINIT UPN match, constrained delegation, S4U2Proxy, and AES extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/db-glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/hdb-samba4-plugin.c -->
# sources/user-network-fs/samba/source4/kdc/hdb-samba4-plugin.c

## Purpose
`hdb-samba4-plugin.c` registers the Heimdal HDB method named `samba4`. It exists primarily for HDB-backed keytab access, especially `HDBGET:samba4:&<base_ctx_pointer>` style lookups used by the kpasswd integration.

## Important APIs, Types, And Functions
`hdb_samba4_create` parses an argument string of the form `&%p`, treats the pointer as a `struct samba_kdc_base_context`, and calls `hdb_samba4_kpasswd_create_kdc`. `hdb_samba4_init` and `hdb_samba4_fini` are no-op method lifecycle hooks for newer HDB interfaces. The exported `struct hdb_method hdb_samba4_interface` sets `prefix = "samba4"` and points `.create` at the creator.

## Control Flow
Heimdal calls the method create hook when a `samba4` HDB/keytab name is opened. The create hook validates the pointer syntax, recovers the talloced base context, builds a restricted kpasswd HDB using Samba's normal KDC DB setup, and maps Samba `NTSTATUS` setup failures to `EINVAL` with Kerberos error messages.

## State And Persistence Behavior
This file owns no persistent state. It bridges a process-local pointer from a keytab name into an HDB object that subsequently opens `sam.ldb` through `hdb_samba4_kpasswd_create_kdc`.

## Dependencies And Integration Points
It depends on `kdc/kdc-glue.h`, Samba loadparm helpers for private paths, and Heimdal's HDB method ABI. The compile-time `HDB_INTERFACE_VERSION` check enforces version 12.

## Risks
The pointer-in-string design is intentionally described as an ugly private hook. It is process-local and must never be treated as externally trusted input. A mismatch between build-time and runtime HDB ABI would break keytab/kpasswd service creation, and incompatible DSDB versions are surfaced as `EINVAL`.

## Test Signals
Signals include kpasswd startup, `HDBGET:samba4:&...` keytab lookup, error reporting for invalid pointer arguments, and build failure on unsupported Heimdal HDB versions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/hdb-samba4-plugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/hdb-samba4.c -->
# sources/user-network-fs/samba/source4/kdc/hdb-samba4.c

## Purpose
`hdb-samba4.c` adapts Samba's SDB/database glue to Heimdal's HDB interface. It makes the Samba AD database appear as a read-mostly Kerberos principal database, wires HDB fetch/iteration/delegation/audit hooks, and carries Samba authentication/audit details through Heimdal request objects.

## Important APIs, Types, And Functions
The main exported constructors are `hdb_samba4_create_kdc` and `hdb_samba4_kpasswd_create_kdc`. Exported request helpers are `hdb_samba4_set_ntstatus`, `hdb_samba4_set_steal_client_audit_info`, and `hdb_samba4_set_steal_server_audit_info`. Important static hooks include `hdb_samba4_fetch_kvno`, `hdb_samba4_kpasswd_fetch_kvno`, first/next iteration, `hdb_samba4_check_constrained_delegation`, `hdb_samba4_check_rbcd`, PKINIT/client-target checks, and `hdb_samba4_audit`.

## Control Flow
HDB fetch converts HDB flags to SDB flags, delegates to `samba_kdc_fetch`, maps SDB errors to HDB errors, then converts `sdb_entry` to `hdb_entry`. The kpasswd variant always looks up `kadmin/changepw@REALM`, clears client/krbtgt lookup flags, and requests the latest kvno. Iteration delegates to `samba_kdc_firstkey`/`nextkey`; the kpasswd HDB panics on iteration because it should only be used as a keytab. Constructor setup fills the `HDB` vtable, disables unsupported mutable operations, and enables enterprise principal handling. Audit flow reads Heimdal request KV pairs, maps auth events to NTSTATUS/Kerberos errors, may attach NTSTATUS e-data, updates bad password/lockout accounting, and logs authentication or authorization events.

## State And Persistence Behavior
The HDB object owns a `samba_kdc_db_context` from `samba_kdc_setup_db_ctx`. It does not store entries through HDB; store/rename/delete return database-in-use or are null. Persistence changes occur indirectly through DB glue accounting and bad-password updates. Audit information and NTSTATUS metadata are stored as Heimdal request objects with custom deallocators, stealing talloc-owned audit data where needed.

## Dependencies And Integration Points
This file integrates Heimdal HDB, Samba SDB conversion, PAC/delegation glue, authentication accounting, authn policy, winbind IRPC for bad-password reset propagation on RODCs, tsocket address conversion, and Samba audit logging. `kdc-heimdal.c` installs the HDB into the live KDC; `hdb-samba4-plugin.c` exposes it as an HDB method for keytab use.

## Risks
Risk concentrates in error mapping and audit side effects. Returning `HDB_ERR_NOT_FOUND_HERE` controls RODC forwarding, so incorrect mapping changes availability/security. Bad-password and lockout handling must not double-count or fail open. Request-owned Heimdal objects wrap talloc pointers, so ownership bugs could leak or double free audit info. `hdb_samba4_audit` intentionally panics under socket-wrapper tests for unexpected generic internal situations, making tests a useful tripwire.

## Test Signals
Test HDB fetch for clients, services, krbtgt, trusts, wrong realm, missing RODC secrets, and kpasswd. Exercise AS audit outcomes: unknown client, preauth required suppression, wrong long-term key, historic key, lockout, PKINIT mismatch/failure, RODC fallback, and NTSTATUS e-data. Test TGS audit and delegation/RBCD hooks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/hdb-samba4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-glue.c -->
# sources/user-network-fs/samba/source4/kdc/kdc-glue.c

## Purpose
`kdc-glue.c` contains small PAC-facing helpers shared by Samba's KDC integration. It verifies PAC checksums using the right key from an HDB entry and extracts device PAC context from FAST armor state.

## Important APIs, Types, And Functions
`kdc_check_pac` maps a PAC signature checksum type to a Kerberos enctype, finds the corresponding key in an `hdb_entry` with `hdb_enctype2key`, and calls `check_pac_checksum`. `samba_kdc_get_device_pac` pulls armor client/server/PAC data from an `astgs_request_t` and packages it into `struct samba_kdc_entry_pac`.

## Control Flow
Checksum verification special-cases `CKSUMTYPE_HMAC_MD5` to RC4-HMAC, otherwise uses `krb5_cksumtype_to_enctype`. Device PAC extraction returns an all-null pac wrapper when no armor PAC exists; otherwise it retrieves the armor krbtgt Samba entry and, when locally available, the device Samba entry from HDB entry contexts.

## State And Persistence Behavior
The file does not persist state. It reads per-request armor/PAC state and HDB entry contexts created by DB glue.

## Dependencies And Integration Points
It depends on Heimdal HDB, Samba PAC utilities, NDR PAC types, `kdc/samba_kdc.h`, and request accessors from Heimdal's KDC plugin interface. It is consumed by KDC PAC verification and compound identity/device PAC handling.

## Risks
PAC checksum security depends on selecting the exact key matching the KDC signature enctype. Device PAC handling must tolerate cross-domain armor clients with no local DB entry while still requiring a local armor server entry when a PAC exists.

## Test Signals
PAC validation tests should cover RC4/HMAC-MD5 and non-RC4 checksum mappings, missing matching HDB keys, invalid signatures, FAST armor with device PAC, and cross-domain armor device entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-glue.h -->
# sources/user-network-fs/samba/source4/kdc/kdc-glue.h

## Purpose
`kdc-glue.h` is the shared KDC glue header that binds Samba KDC code to Heimdal HDB/KDC plugin types and exposes HDB construction, request audit helpers, PAC checksum verification, and device PAC retrieval.

## Important APIs, Types, And Functions
It includes Kerberos, Heimdal HDB, Heimdal KDC plugin, Samba KDC, and KDC server headers. It declares `hdb_samba4_create_kdc`, `hdb_samba4_kpasswd_create_kdc`, `hdb_samba4_set_ntstatus`, audit-info setters for client/server, `kdc_check_pac`, and `samba_kdc_get_device_pac`.

## Control Flow
The header has no runtime flow. It defines the cross-file contract used by the Heimdal service startup, HDB plugin, PAC glue, and kpasswd service.

## State And Persistence Behavior
No state is stored in the header. It exposes pointers to opaque Samba KDC contexts and Heimdal request objects whose lifetimes are managed by implementation files.

## Dependencies And Integration Points
This header is a central integration point for `hdb-samba4.c`, `hdb-samba4-plugin.c`, `kdc-heimdal.c`, `kdc-glue.c`, and PAC/kpasswd code. Because it pulls in Heimdal headers, ABI changes in Heimdal can surface through this contract.

## Risks
Prototype drift or include-order changes can break both in-process KDC and keytab/kpasswd builds. The audit helpers transfer ownership of talloc data, so callers must understand the steal semantics declared here.

## Test Signals
Build coverage across Heimdal-enabled configurations is the main signal. Runtime signals are successful HDB creation, kpasswd keytab lookup, PAC validation, and audit info propagation through KDC requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-heimdal.c -->
# sources/user-network-fs/samba/source4/kdc/kdc-heimdal.c

## Purpose
`kdc-heimdal.c` starts and wires Samba's in-process Heimdal KDC service. It binds KDC and kpasswd sockets, processes Kerberos packets through Heimdal, initializes the Samba HDB backend and KDC plugins after fork, and registers an IRPC PAC validation endpoint.

## Important APIs, Types, And Functions
The public service initializer is `server_service_kdc_init`. Static control points are `kdc_process`, `kdc_startup_interfaces`, `kdc_check_generic_kerberos`, `kdc_task_init`, and `kdc_post_fork`. It uses `struct kdc_server` from `kdc-server.h` and an external `krb5plugin_kdc_ftable kdc_plugin_table`.

## Control Flow
`kdc_task_init` rejects non-AD-DC roles, loads interfaces, creates `struct kdc_server`, and calls `kdc_startup_interfaces` to bind KDC and kpasswd sockets. `kdc_post_fork` initializes Kerberos, retrieves Heimdal KDC config, enforces Samba-specific security defaults such as strongest keys, PAC requirement, FAST settings, and disabled armored PA-ENC-TIMESTAMP, creates the Samba HDB DB, detects RODC status, registers HDBGET/keytab and KDC plugins, initializes PKINIT, and registers `KDC_CHECK_GENERIC_KERBEROS` IRPC. `kdc_process` updates KDC time/current NT time, calls `krb5_kdc_process_krb5_request`, and maps `HDB_ERR_NOT_FOUND_HERE` to `KDC_PROXY_REQUEST`.

## State And Persistence Behavior
Runtime state is held in `struct kdc_server`: task pointer, Kerberos context, base DB context, HDB DB context, RODC flag, proxy timeout, kpasswd keytab name, and Heimdal KDC config in `private_data`. Persistent state is accessed through the Samba HDB backend, not directly here. The current NT time pointer is updated for each packet so DB glue and gMSA logic see request time.

## Dependencies And Integration Points
It integrates Samba process services, interface enumeration, tsocket addresses, Heimdal KDC/HDB, Samba HDB glue, kpasswd service, PAC validation, DSDB RODC detection, IRPC, and plugin registration. `kdc-server.c` supplies socket I/O and proxy handling; `db-glue.c` supplies HDB lookups.

## Risks
Startup ordering is critical: sockets are bound before post-fork DB/plugin setup, but request processing depends on post-fork state. Security-sensitive config defaults such as `require_pac`, strongest key flags, FAST cookie behavior, and krbtgt key strength must not regress. RODC proxy signaling depends on preserving `HDB_ERR_NOT_FOUND_HERE` from HDB to `KDC_PROXY_REQUEST`.

## Test Signals
Signals include service role gating, interface binding, KDC and kpasswd socket startup, Heimdal plugin registration, PKINIT initialization, PAC validation IRPC, RODC proxy requests, FAST/PAC behavior, and packet processing over UDP/TCP through `kdc-server.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-heimdal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-proxy.c -->
# sources/user-network-fs/samba/source4/kdc/kdc-proxy.c

## Purpose
`kdc-proxy.c` implements RODC KDC request proxying to writable DC replication partners. When the local RODC cannot answer because it lacks secrets, UDP/TCP request handlers can forward the original Kerberos request to a writable DC and relay the reply.

## Important APIs, Types, And Functions
Public async APIs are `kdc_udp_proxy_send`/`kdc_udp_proxy_recv` and `kdc_tcp_proxy_send`/`kdc_tcp_proxy_recv`. Internal helpers include `kdc_proxy_get_writeable_dcs`, UDP state machine functions (`kdc_udp_next_proxy`, resolve/sendto/recv callbacks), and TCP state machine functions (`kdc_tcp_next_proxy`, resolve/connect/write/read callbacks). State structs keep the event context, KDC pointer, local service port, input/output blobs, proxy candidate list, candidate index, resolved IP, and socket/stream.

## Control Flow
Both UDP and TCP paths first load writable DC candidates from `repsFrom` on the default naming context, then iterate candidates. Each candidate is resolved with DNS-only resolution. UDP creates a connected datagram socket, sends the raw request, arms a receive with `proxy_timeout`, and completes on reply or tries the next candidate on send/receive/resolve failure. TCP builds a 4-byte length-prefixed request, connects to the target port, writes the request, reads a length-prefixed reply, strips the header, and completes.

## State And Persistence Behavior
The file reads persistent replication partner metadata from DSDB `repsFrom` but does not modify DB state. All proxy state is per-`tevent_req` and freed when the request completes.

## Dependencies And Integration Points
It depends on `kdc_server` state, DSDB replication metadata (`dsdb_loadreps`), Samba resolver, tsocket/tstream/tdgram async I/O, packet framing helpers, and tevent NTSTATUS helpers. It is called by `kdc-server.c` only when processing returned `KDC_PROXY_REQUEST` on an RODC.

## Risks
Proxy availability depends on accurate `repsFrom` metadata and DNS resolution. Candidate iteration must not complete before both send and receive paths have handled errors. TCP/UDP framing differs, so length-header handling must stay exact. Timeouts must be bounded to avoid request hangs, and proxying must remain gated to RODCs in the caller.

## Test Signals
Test with no replication partners, unresolvable partners, UDP send failures, UDP timeout then next candidate, TCP connect/write/read failures, successful TCP length stripping, and caller behavior when all candidates fail. RODC integration tests should assert fallback to writable DC for missing-secret AS/TGS paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-proxy.h -->
# sources/user-network-fs/samba/source4/kdc/kdc-proxy.h

## Purpose
`kdc-proxy.h` declares the async RODC proxy API used by KDC socket handlers to forward Kerberos requests to writable DCs.

## Important APIs, Types, And Functions
It declares `kdc_udp_proxy_send`, `kdc_udp_proxy_recv`, `kdc_tcp_proxy_send`, and `kdc_tcp_proxy_recv`. Both send functions accept a talloc context, tevent context, `struct kdc_server`, local service port, and request blob. Receive functions return an `NTSTATUS` and move the output blob into caller memory.

## Control Flow
The header exposes the standard tevent send/recv pattern. Callers start a proxy request, attach a callback, and in the callback call the matching recv function to obtain the proxied KDC reply or error.

## State And Persistence Behavior
No state is stored in the header. The implementation stores transient per-request state and reads DSDB replication metadata.

## Dependencies And Integration Points
It integrates `kdc-server.c` with `kdc-proxy.c` and depends on Samba's tevent and `DATA_BLOB` conventions plus `struct kdc_server` from the KDC server layer.

## Risks
UDP and TCP send/recv functions must be paired correctly. Callers must retain the input blob for the async lifetime as required by implementation semantics.

## Test Signals
Build and runtime tests should exercise both proxy APIs from UDP and TCP request handling, including successful replies and unavailable-proxy error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-proxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-server.c -->
# sources/user-network-fs/samba/source4/kdc/kdc-server.c

## Purpose
`kdc-server.c` provides the shared UDP/TCP socket server for KDC and kpasswd services. It receives Kerberos PDUs, calls a service-specific `kdc_process_fn_t`, sends replies, and invokes RODC proxying when the processor reports `KDC_PROXY_REQUEST`.

## Important APIs, Types, And Functions
The exported API is `kdc_add_socket`. Internal structs model TCP connections/calls and UDP calls. Important callbacks are `kdc_udp_call_loop`, UDP proxy/send completion, `kdc_tcp_accept`, `kdc_tcp_call_loop`, TCP proxy/write completion, and `kdc_proxy_unavailable_error`.

## Control Flow
`kdc_add_socket` creates a `kdc_socket`, binds TCP unless `udp_only`, always binds UDP, creates send queues, and starts the UDP receive loop. UDP receives one datagram, calls `process(..., datagram=1)`, drops errors, proxies on `KDC_PROXY_REQUEST` if the KDC is an RODC, or queues a datagram reply. TCP accepts a stream, wraps it in tstream, reads length-prefixed PDUs, strips the 4-byte header before processing, writes a new 4-byte length header plus reply, then starts the next read. If proxying fails, both UDP and TCP can synthesize `KRB5KDC_ERR_SVC_UNAVAILABLE`.

## State And Persistence Behavior
The file stores transient socket, connection, queue, call, and packet state under talloc parents. It does not persist configuration or directory data. Long-lived state is `struct kdc_socket` and `struct kdc_udp_socket` attached to `struct kdc_server`.

## Dependencies And Integration Points
It depends on Samba process model, tsocket/tdgram/tstream, packet helpers, loadparm socket options, `kdc-server.h` state, `kdc-proxy.h`, and service processors such as Heimdal KDC processing or kpasswd processing. It is used by both `kdc-heimdal.c` and `kdc-service-mit.c`.

## Risks
Length-header arithmetic and pointer adjustment on TCP input must remain correct. UDP receive loop restarts even after allocation/process failures; termination only happens if a new receive cannot be scheduled. Proxying must be rejected when not on an RODC. Generated unavailable errors require a valid Kerberos context and allocation. TCP callbacks intentionally terminate connections on unexpected direct recv/send handlers.

## Test Signals
Signals include UDP and TCP KDC/kpasswd traffic, multiple TCP PDUs on one connection, malformed/short TCP PDUs from packet framing tests, proxy success/failure, unavailable error generation, bind failures, UDP-only wildcard/interface binding, and memory/error-path coverage under socket-wrapper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-server.h -->
# sources/user-network-fs/samba/source4/kdc/kdc-server.h

## Purpose
`kdc-server.h` defines shared runtime structures and socket API for Samba KDC services.

## Important APIs, Types, And Functions
`struct kdc_server` holds task/process state, Kerberos context, Samba base/DB contexts, RODC flag, proxy timeout, kpasswd keytab name, private service data, and current DB context. `enum kdc_code_e` distinguishes normal reply, error, and proxy request. `kdc_process_fn_t` is the callback signature for KDC/kpasswd processors. `struct kdc_socket` and `struct kdc_udp_socket` hold socket-local state. `kdc_add_socket` binds service sockets.

## Control Flow
Service initializers allocate a `kdc_server`, fill contexts and callback data, then call `kdc_add_socket` with a name, address, port, processor, and UDP-only flag. Runtime packet processing is implemented in `kdc-server.c`.

## State And Persistence Behavior
The header defines in-memory server and socket state only. Persistent Kerberos/AD data lives behind `samba_kdc_db_context` and the service-specific private data.

## Dependencies And Integration Points
It is included by Heimdal service startup, MIT kpasswd startup, socket handling, proxy handling, and kpasswd service code. It depends on Samba task server types, tsocket addresses, Heimdal/Samba Kerberos context types, and process model operations.

## Risks
Changes to `struct kdc_server` affect many service files. The `private_data` field carries different types depending on Heimdal versus MIT paths, so users must cast carefully. The `kdc_process_fn_t` return code controls RODC proxy behavior.

## Test Signals
Build coverage catches signature/struct drift. Runtime signals are successful socket registration from both Heimdal and MIT service initializers, plus correct processing of `KDC_OK`, `KDC_ERROR`, and `KDC_PROXY_REQUEST`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-service-mit.c -->
# sources/user-network-fs/samba/source4/kdc/kdc-service-mit.c

## Purpose
`kdc-service-mit.c` starts a MIT Kerberos `krb5kdc` child process inside Samba AD DC mode and initializes Samba's kpasswd service using MIT KDB/keytab facilities.

## Important APIs, Types, And Functions
The main exported service initializer is `mitkdc_task_init`; `server_service_mitkdc_init` registers it under the `kdc` service name. Static helpers include `kdc_server_destroy`, `startup_kpasswd_server`, and `mitkdc_server_done`.

## Control Flow
`mitkdc_task_init` rejects standalone/member roles, loads interfaces, sets `KRB5_KDC_PROFILE` from the private dir, optionally sets `KRB5_TRACE`, launches the configured MIT KDC command with `samba_runcmd_send`, installs an IRPC service, allocates `struct kdc_server` and base context, initializes Samba/MIT krb5 and kadm5 contexts, opens a kadm5 server handle, registers MIT KDB keytab support, sets the kpasswd keytab to `KDB:`, and binds kpasswd sockets. If the child process exits, `mitkdc_server_done` terminates the task.

## State And Persistence Behavior
The MIT KDC itself is a child process; this parent task tracks it and owns the kpasswd socket/service state. `kdc->private_data` holds a kadm5 server handle and is destroyed by `kadm5_destroy`. Persistent DB access occurs through MIT KDB and Samba kpasswd password-setting paths, not directly in this file.

## Dependencies And Integration Points
It depends on Samba service/process model, interface loading, dynamic log paths, MIT kadm5/KDB APIs, `mit_kdc_irpc`, `kdc-server.c`, and the common kpasswd service. It is an alternative service path to the in-process Heimdal KDC but still uses Samba's socket/kpasswd helpers.

## Risks
Child process lifecycle is critical: a normal or abnormal MIT KDC exit terminates the Samba task. Environment variables must point at the correct generated KDC profile and trace location. The service registers as `kdc` with `inhibit_pre_fork = true` because IRPC runs only in the master event loop; changing that can break IRPC handling.

## Test Signals
Signals include AD DC role gating, MIT KDC command startup/failure, child-exit termination, IRPC service setup, kpasswd socket binding, `KDB:` keytab registration, and password-change flows through the MIT service path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-service-mit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-service-mit.h -->
# sources/user-network-fs/samba/source4/kdc/kdc-service-mit.h

## Purpose
`kdc-service-mit.h` declares the MIT KDC task initializer used when Samba is built/configured to run MIT Kerberos as the KDC backend.

## Important APIs, Types, And Functions
The only declaration is `NTSTATUS mitkdc_task_init(struct task_server *task)`, implemented in `kdc-service-mit.c`.

## Control Flow
The server service registration calls this initializer to start the MIT KDC parent task and kpasswd support. The header itself has no runtime logic.

## State And Persistence Behavior
No state is stored here. The implementation stores process and kpasswd state in `struct kdc_server`.

## Dependencies And Integration Points
It is included by service registration or build units that need the MIT KDC task entry point. It depends on Samba's `NTSTATUS` and `task_server` types being visible to the including translation unit.

## Risks
Low direct risk; prototype drift would break service registration builds. The declaration intentionally keeps the MIT service surface minimal.

## Test Signals
Build with MIT KDC support and service startup tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kdc-service-mit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-helper.c -->
# sources/user-network-fs/samba/source4/kdc/kpasswd-helper.c

## Purpose
`kpasswd-helper.c` provides helper routines for Samba's Kerberos password-change service. It formats kpasswd protocol result blobs, maps Samba password-change failures to Kerberos kpasswd errors, writes password changes through SAMDB transactions, and rejects inappropriate TGT-based authorization.

## Important APIs, Types, And Functions
`kpasswd_make_error_reply` creates a two-byte kpasswd status plus UTF-8 message blob. `kpasswd_make_pwchange_reply` maps `NTSTATUS` and `samPwdChangeReason` values to kpasswd success, access-denied, soft-error, or hard-error replies. `kpasswd_samdb_set_password` opens SAMDB as the authenticated session, resolves target user or service principal DN, and calls `samdb_set_password`. `kpasswd_check_non_tgt` enforces that the ticket to kpasswd is not a TGT.

## Control Flow
Password setting opens `samdb_connect`, logs the actor domain/account/SID and target principal, starts an LDB transaction, cracks the target principal according to user-vs-service mode, calls `samdb_set_password` with `DSDB_PASSWORD_RESET`, commits on success, and cancels on failure. Reply generation distinguishes no-such-user/access-denied, domain password policy restriction reasons, generic failures, and success.

## State And Persistence Behavior
This file performs real persistent changes through `samdb_set_password` inside an LDB transaction. On failure it cancels the transaction. It also returns domain password policy information (`samr_DomInfo1`) and reject reasons for user-facing kpasswd replies.

## Dependencies And Integration Points
It depends on Kerberos kpasswd constants, SAMR NDR types, SAMDB password APIs, Samba auth session information, loadparm/event contexts, and principal-cracking helpers. It is called by the kpasswd service shared by Heimdal and MIT startup paths.

## Risks
The transaction boundary around password changes is critical. Reply formatting must avoid length overflow and handle UTF-8 conversion correctly. Error strings can reveal operational details but are standard protocol feedback. `kpasswd_check_non_tgt` prevents a TGT from being used directly as the kpasswd service ticket, an important protocol authorization check.

## Test Signals
Tests should cover successful password change, no such user, access denied, password too short, complexity failure, password history, generic password restriction, transaction commit failure, service-principal resolution, user-principal resolution, and TGT rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-helper.h -->
# sources/user-network-fs/samba/source4/kdc/kpasswd-helper.h

## Purpose
`kpasswd-helper.h` declares the helper API used by Samba's kpasswd service to format replies, set passwords, and validate ticket type.

## Important APIs, Types, And Functions
It declares `kpasswd_make_error_reply`, `kpasswd_make_pwchange_reply`, `kpasswd_samdb_set_password`, and `kpasswd_check_non_tgt`. The password-setting API takes event/loadparm/session context, service-principal mode, target principal name, password blob, and output reject/domain policy details.

## Control Flow
Callers validate the ticket with `kpasswd_check_non_tgt`, attempt password change with `kpasswd_samdb_set_password`, then convert the resulting `NTSTATUS` and policy reason to a kpasswd reply blob with `kpasswd_make_pwchange_reply`.

## State And Persistence Behavior
The header itself stores no state. The implementation can persist password changes through SAMDB and returns policy metadata by output pointer.

## Dependencies And Integration Points
The declarations connect kpasswd service code to Samba auth sessions, loadparm, tevent, SAMR password policy types, Kerberos error codes, and `DATA_BLOB` reply conventions.

## Risks
Callers must pass the correct `is_service_principal` mode and preserve output pointer ownership expectations. Incorrect ticket-type validation or status-to-reply mapping would affect kpasswd authorization and client behavior.

## Test Signals
Build coverage plus kpasswd end-to-end tests for success, policy rejection, authorization failure, and TGT rejection are the primary signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/kpasswd-helper.h -->
