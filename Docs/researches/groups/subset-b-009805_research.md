# Research: subset-b-009805

Grouped research for Samba source3 include headers under `sources/user-network-fs/samba/source3/include`. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/libsmbclient.h -->
# sources/user-network-fs/samba/source3/include/libsmbclient.h

## Purpose
This is the public C ABI for Samba's `libsmbclient` library. It exposes URL-oriented SMB/CIFS client operations for files, directories, attributes, notifications, printing, context configuration, authentication, server caching, credentials fallback, thread hooks, URL encoding, and version discovery. The header is deliberately ABI-conservative: the visible `SMBCCTX` struct remains for old applications, but comments direct new code to getter/setter APIs and internal private state.

## Important APIs, Types, And Control Flow
Core opaque handles are `SMBCCTX`, `SMBCSRV`, and `SMBCFILE`. Public data structures include `struct smbc_dirent`, `struct libsmb_file_info`, print job metadata, notification callback action arrays, and enums for share modes, SMB encryption level, VFS feature bits, directory entry kinds, DOS mode xattr bits, and xattr create/replace flags. The control surface appears in two layers: context methods such as `smbc_getFunctionOpen()`/`smbc_setFunctionOpen()` install operation callbacks, while compatibility functions such as `smbc_open()`, `smbc_read()`, `smbc_opendir()`, `smbc_stat()`, `smbc_setxattr()`, and `smbc_print_file()` dispatch through the active context.

## State And Persistence
State lives in a context and its internal data: debug settings, NetBIOS name, workgroup, user, timeout, TCP port, protocol bounds, Kerberos and ccache flags, encryption level, browse behavior, URL encoding behavior, server cache callbacks, open handles, and private user data. The library persists no files directly through this header, but operations mutate remote SMB servers, remote ACLs and extended attributes, print queues, connection caches, and optional global credentials used for DFS referrals.

## Dependencies And Integration Points
The header depends on POSIX stat/statvfs, fcntl, time, utime, and Samba implementation files in `libsmbclient.c`, `libsmb_context.c`, `libsmb_dir.c`, `libsmb_file.c`, cache code, auth callbacks, DFS referral handling, and SMB protocol negotiation. It integrates with consumers as a stable installed header and with Samba internals through the private `SMBC_internal_data` pointer.

## Risks And Test Signals
Risks include old applications directly mutating deprecated struct fields, global configuration side effects from log and configuration setters, ambiguity around URL-encoded directory entries, credential fallback accidentally enabling anonymous access, xattr security descriptor parsing errors, thread hook misuse, and ABI breakage if fields are reordered. Test signals include ABI compile tests, context lifecycle and cleanup tests, file and directory round trips against an SMB server, DFS referral access, Kerberos/NTLM fallback combinations, xattr ACL get/set/list/remove, notifications, print queue calls, custom server cache callbacks, and multithreaded context use after `smbc_thread_posix()` or `smbc_thread_impl()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/libsmbclient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/local.h -->
# sources/user-network-fs/samba/source3/include/local.h

## Purpose
`local.h` centralizes source3 server-side constants used by smbd, nmbd, winbindd, printing, locking, RPC, LDAP replication, and connection management. It is not an API implementation header; it fixes operational limits, default timeouts, database flags, string constants, and compatibility defaults that shape daemon behavior.

## Important APIs, Types, And Control Flow
The file defines no functions or structs. Important constants include open-file limits (`MIN_OPEN_FILES_WINDOWS`, `MAX_OPEN_FILES`, `MAX_OPEN_FUDGEFACTOR`), directory and pipe limits (`MAX_DIRECTORY_HANDLES`, `MAX_OPEN_PIPES`), password and list limits (`MAX_PASS_LEN`, `LIST_SEP`), browsing and NetBIOS timers, keepalive and connect timeouts, oplock break timeout/fudge, lock retry timing, auth mutex timing, share-name validation characters, volatile TDB hash size and flags, Windows minimum lock timeout, and `MAX_RPC_DATA_SIZE`.

## State And Persistence
The header does not store runtime state, but many constants govern persistent or shared state indirectly. `SERVER_LIST` names the browser database in the lock directory, TDB flags configure volatile databases used for open-file records, and timeout/limit constants affect how long entries, locks, name registrations, and failed connection cache data remain relevant.

## Dependencies And Integration Points
It integrates broadly through include chains that need source3 defaults before daemon initialization. Values here interact with loadparm settings such as `max open files`, TDB setup, NetBIOS browse services, RPC server limits, oplock handling, winbind cache sizing, and printer behavior.

## Risks And Test Signals
Risks are mostly compatibility and resource-boundary regressions: reducing file or pipe limits can break Windows clients, changing NetBIOS timers can destabilize browsing, altering volatile TDB flags can affect cleanup semantics, and enlarging RPC limits changes memory exposure. Test signals include smbd startup under low/high fd limits, Windows client file-open stress, RPC request size rejection, oplock break timing tests, NetBIOS browse registration timing, invalid share-name validation, and winbind cache behavior under multiple trusted domains.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/locking.h -->
# sources/user-network-fs/samba/source3/include/locking.h

## Purpose
`locking.h` defines the byte-range lock record formats and context identifiers used by smbd locking code. It documents the on-disk/in-TDB shape of `brlock.tdb` records and separates Windows-style and POSIX-style byte-range locks.

## Important APIs, Types, And Control Flow
Key enums are `brl_type` (`READ_LOCK`, `WRITE_LOCK`, `UNLOCK_LOCK`) and `brl_flavour` (`WINDOWS_LOCK`, `POSIX_LOCK`). `struct lock_context` identifies a client lock namespace with SMB lock context, tree id, and `server_id`. `struct lock_struct` is the stored linear record containing context, start, size, fnum, lock type, and flavor. `struct smbd_lock_element` is a request-oriented representation with GUID, SMB lock context, type, flavor, offset, and count. The header forward-declares `files_struct`, `byte_range_lock`, and `share_mode_lock`.

## State And Persistence
The important persistent state is `brlock.tdb`: records are unsorted linear arrays of `lock_struct` values, with count derived from TDB record size. `UNLOCK_LOCK` is explicitly not stored and exists for POSIX unlock range computation. The `server_id` dependency lets lock ownership survive multi-process smbd coordination.

## Dependencies And Integration Points
It depends on generated `server_id` and `misc` NDR headers plus `lib/file_id.h`. It integrates with byte-range lock code, share mode locking, file handle state, POSIX lock downgrades, and oplock/share-mode decisions.

## Risks And Test Signals
Risks include ABI/layout mismatch for existing TDB data, incorrect range math for unlocks, stale `server_id` ownership after process death, and semantic mismatch between Windows and POSIX lock flavors. Test signals include overlapping read/write lock conflict tests, POSIX unlock range splitting, lock downgrade re-evaluation, TDB record migration/reading, smbd process death cleanup, and mixed clients using Windows and POSIX locking on the same file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/locking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/lsa.h -->
# sources/user-network-fs/samba/source3/include/lsa.h

## Purpose
`lsa.h` provides a small helper surface for the Local Security Authority RPC server code. It focuses on building LSA reference-domain lists and normalizing lookup error handling.

## Important APIs, Types, And Control Flow
The single function declaration, `init_lsa_ref_domain_list()`, initializes a generated `lsa_RefDomainList` from a domain name and domain SID under a caller-provided talloc context. The `NT_STATUS_LOOKUP_ERR(status)` macro treats any status other than success, `STATUS_SOME_UNMAPPED`, and `NT_STATUS_NONE_MAPPED` as a hard lookup error, matching LSA lookup APIs where partial or complete unmapped results can still be valid protocol outcomes.

## State And Persistence
The header itself stores no state. Runtime allocation is caller-owned through `TALLOC_CTX`; resulting LSA structures are transient RPC response data rather than persistent database state.

## Dependencies And Integration Points
It depends on Samba NTSTATUS macros, generated LSA NDR structures, domain SID types, and talloc conventions. It integrates with LSA name/SID lookup RPC handlers and passdb/idmap lookup flows that must return Windows-compatible partial mapping statuses.

## Risks And Test Signals
Risks are concentrated in status classification: treating partial mapping as fatal would break Windows-compatible lookup responses, while missing real errors would hide backend failures. Test signals include lookup calls returning all mapped, some unmapped, none mapped, and backend error cases; memory ownership checks for the allocated reference-domain list; and RPC response validation against generated LSA marshalling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/lsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/mangle.h -->
# sources/user-network-fs/samba/source3/include/mangle.h

## Purpose
`mangle.h` declares the pluggable 8.3 filename mangling interface used when SMB clients require DOS-compatible names. It abstracts the algorithm that detects, looks up, and generates mangled names for a share.

## Important APIs, Types, And Control Flow
`struct mangle_fns` is a callback table. `reset()` clears algorithm state. `is_mangled()` detects existing mangled names. `must_mangle()` decides whether a long name must be converted. `is_8_3()` validates DOS 8.3 form with case and wildcard options. `lookup_name_from_8_3()` maps a mangled input back to the long name, allocating with talloc. `name_to_8_3()` emits a 13-byte output buffer, with cache control, default case, and share parameters.

## State And Persistence
The header defines no storage, but the callback table permits implementations to keep caches or persistent mapping databases elsewhere. The `cache83` argument and reverse lookup API imply stateful name mapping when deterministic conversion alone cannot recover the long name.

## Dependencies And Integration Points
It depends on `TALLOC_CTX`, `share_params`, and Samba filename matching/case rules. It integrates with directory enumeration, path lookup, SMB1 clients, share configuration, and any module selected as the active mangling backend.

## Risks And Test Signals
Risks include collisions between long names, case sensitivity mismatches, wildcard handling differences, invalid output buffer length assumptions, and stale reverse lookup cache entries. Test signals include 8.3 validation cases, long-name collision generation, cache-enabled and cache-disabled reverse lookup, wildcard patterns, per-share case settings, SMB1 directory listings, and cross-platform names containing characters illegal in DOS aliases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/mangle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/messages.h -->
# sources/user-network-fs/samba/source3/include/messages.h

## Purpose
`messages.h` declares Samba source3's intra-process and inter-process messaging API. It is the daemon coordination layer for typed messages between `server_id` endpoints, with tevent integration and support for data blobs, iovecs, file descriptors, broadcast sends, and filtered asynchronous reads.

## Important APIs, Types, And Control Flow
`messaging_init()` creates a `messaging_context`, and helpers expose its local `server_id`, tevent context, and names database. `messaging_register()` and `messaging_deregister()` attach callbacks by message type. Send paths include `messaging_send()`, `messaging_send_buf()`, `messaging_send_iov_from()`, `messaging_send_iov()`, and `messaging_send_all()`. Receive paths use tevent requests via `messaging_filtered_read_send()`/`recv()` and `messaging_read_send()`/`recv()`. `messaging_reinit()` handles forked processes, `messaging_cleanup()` removes stale records, and `messaging_rec_create()` builds received-message objects.

## State And Persistence
State is held in `messaging_context`: registered handlers, local identity, tevent loop, names database, and transport resources. The API can persist process identity/name mappings in the messaging names database and performs cleanup by pid. Large sends can drive a tevent loop even though send functions look synchronous.

## Dependencies And Integration Points
It depends on tevent, NTSTATUS, `server_id`, `DATA_BLOB`, networking headers, iovec/fd passing, and generated `ndr_messaging`. It integrates with smbd, nmbd, winbindd, printing notifications, cache invalidation, debug hooks, and daemon reinit-after-fork code.

## Risks And Test Signals
Risks include assuming send calls are purely synchronous, losing low-priority messages under load, stale registrations after fork, cleanup races for reused pids, fd passing portability, and message version incompatibility. Test signals include register/send/receive round trips, large message delivery with tevent activity, broadcast behavior, low-priority drop tolerance, filtered reads, fd passing, `messaging_reinit()` after fork, stale pid cleanup, and NDR compatibility for message records.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/msdfs.h -->
# sources/user-network-fs/samba/source3/include/msdfs.h

## Purpose
`msdfs.h` defines constants and record layouts for Microsoft DFS referrals served by Samba. It describes referral TTLs, reply flags and sizes, referral list limits, and in-memory maps from DFS junctions to alternate targets.

## Important APIs, Types, And Control Flow
Constants include `REFERRAL_TTL`, referral-server/storage-server flags, version 2 and version 3 referral record sizes, referral header size, and maximum referral and junction counts. `struct client_dfs_referral` describes a referral returned to a client with proximity, TTL, and DFS path. `struct referral` stores alternate target path, proximity, and TTL. `struct junction_map` groups a service/volume/comment with a referral count and referral list.

## State And Persistence
The header has no active state, but its structures model configured DFS junction state and transient referral responses. TTL values control client-side caching, while max counts bound memory and protocol response construction.

## Dependencies And Integration Points
It integrates with trans2/SMB DFS referral reply construction, share/path resolution, DFS junction management, and clients following referrals across servers. The structures depend on Samba allocation and string ownership conventions even though this header does not declare functions.

## Risks And Test Signals
Risks include referral count overflow, invalid target path ownership, TTL changes causing stale referrals or excessive refreshes, and version-specific size mismatches in wire replies. Test signals include version 2 and 3 referral encoding, max referral count rejection, junction lookup for multiple targets, client cache TTL behavior, storage-server flag correctness, and path normalization for DFS targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/msdfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/nameserv.h -->
# sources/user-network-fs/samba/source3/include/nameserv.h

## Purpose
`nameserv.h` defines NetBIOS Name Service and datagram protocol constants and packet layouts used by nmbd and related browser/name-query code. It maps RFC1001/RFC1002 fields, WINS record flags, browser mailslot identifiers, and Samba packet queue structures.

## Important APIs, Types, And Control Flow
Important definitions include name service opcodes, question/resource record types and classes, NetBIOS node flags, WINS state/type/location/static bits, name-state helper macros, error codes, refresh timers, mailslot names, node and packet type enums, NetBIOS name buffers (`nstring`, `unstring`), `struct nmb_name`, node status records, resource records, NMB packets, datagram packets, and `struct packet_struct` queue nodes. Browser announcement message IDs are also defined.

## State And Persistence
The header describes packet and queue state, not persistent storage. Runtime state includes packet linked lists with lock flags, source/destination sockets, timestamps, IP/port metadata, and embedded decoded NMB or datagram bodies. WINS flags represent persistent or replicated name database state elsewhere, including active, released, tombstoned, deleted, local/remote, dynamic/static, and node-type attributes.

## Dependencies And Integration Points
It depends on basic network types such as `struct in_addr` and Samba boolean/string typedefs. It integrates with name registration, release, refresh, WINS server logic, browse list announcements, mailslot datagrams, node status queries, and packet send/receive queues.

## Risks And Test Signals
Risks include wire-format size limits (`MAX_DGRAM_SIZE`), ambiguity between refresh opcodes 8 and 9, malformed flag combinations, fixed scope/name buffer truncation, queue locking races, and WINS state mask mistakes. Test signals include RFC1002 packet encode/decode, name query/status/register/refresh/release paths, WINS active/released/tombstoned transitions, browser mailslot parsing, datagram fragmentation flags, max datagram rejection, and multi-node-type registration behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/nameserv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/nss_info.h -->
# sources/user-network-fs/samba/source3/include/nss_info.h

## Purpose
`nss_info.h` defines the pluggable NSS alias mapping interface used by winbind/idmap code. Backends translate account names to aliases and back on a per-domain basis, with a versioned registration contract.

## Important APIs, Types, And Control Flow
The interface version is `SMB_NSS_INFO_INTERFACE_VERSION`. `struct nss_function_entry` registers a backend name and method table. `struct nss_domain_entry` binds a configured domain to a backend, initialization status, and backend-specific state. `struct nss_info_methods` provides `init`, `map_to_alias`, `map_from_alias`, and `close_fn`. Public functions register backends (`smb_register_idmap_nss()`), perform domain-aware mappings (`nss_map_to_alias()`, `nss_map_from_alias()`), close the subsystem, and initialize the template backend.

## State And Persistence
State is held in linked lists of backend registrations and domain entries. Each domain can retain backend-specific state through `void *state`, with `init_status` recording whether setup succeeded. The header itself persists nothing; LDAP-capable backends may use external directory state.

## Dependencies And Integration Points
It depends on NTSTATUS, talloc, Samba list conventions, and optionally LDAP types, falling back to `void` for `LDAPMessage` when LDAP support is absent. It integrates with winbindd NSS information mapping, idmap configuration, and template alias handling.

## Risks And Test Signals
Risks include interface version mismatches, backend close functions cleaning shared state too broadly, stale per-domain state after reconfiguration, and LDAP/no-LDAP type compatibility. Test signals include backend registration with correct and incorrect versions, domain initialization failure caching, alias round trips, template backend initialization, close/reopen behavior, and builds with and without LDAP support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/nss_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/nt_printing.h -->
# sources/user-network-fs/samba/source3/include/nt_printing.h

## Purpose
`nt_printing.h` declares NT spoolss-facing printing support: printer metadata, driver architecture mapping, driver file validation/copying, printer publishing, access checks, GUID storage, and spoolss notification data structures. It bridges Samba print shares to Windows printing semantics.

## Important APIs, Types, And Control Flow
Constants describe DOS, NE, PE, and version-resource header offsets used for driver inspection. `SPOOLSS_NOTIFY_MSG`, group, and container structs represent spoolss change notifications. `PRINTER_ATTRIBUTE_SAMBA` and `PRINTER_ATTRIBUTE_NOT_SAMBA` define Samba-owned versus network printer attributes. `struct print_architecture_table_node` maps long spoolss architecture strings to short driver directory names and versions; the static `archi_table` includes Win40, x86, MIPS, Alpha, PPC, IA64, x64, and ARM64 entries. Functions initialize printing, translate architecture strings, check access/time windows, retrieve/store/get printer GUIDs, publish and inspect printers, check drivers/files in use, delete driver files, move/clean driver upload structures, and add/remove printer records.

## State And Persistence
Persistent state includes printer GUIDs, published printer state, driver files in download areas, registry/spoolss printer records, and notification messages sent through Samba messaging. The header's static architecture table is compile-time state included in each translation unit that includes it.

## Dependencies And Integration Points
It depends on generated spoolss NDR, `messaging_context`, auth session info, GUIDs, WERROR, DCERPC binding handles, printer service numbers, and spoolss driver info structures. It integrates with printing backends, Samba registry printing keys, Active Directory printer publishing, driver upload paths, and access-control checks.

## Risks And Test Signals
Risks include PE/NE parser offset mistakes, static table duplication, incomplete architecture grouping for enumdrivers, deleting driver files still in use, printer GUID inconsistency, and access checks that diverge from spoolss expectations. Test signals include driver upload/cleanup for each architecture, PE version parsing, printer publish/unpublish, GUID persistence, print admin versus user access checks, deletion while drivers are referenced, notification delivery, and enumdrivers grouping behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/nt_printing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ntdomain.h -->
# sources/user-network-fs/samba/source3/include/ntdomain.h

## Purpose
`ntdomain.h` is a small compatibility/include boundary for NT domain RPC concepts that were moved out of broader SMB headers. It keeps the GENSEC context forward declaration and RPC pipe definitions available to source3 NT domain code.

## Important APIs, Types, And Control Flow
The file forward-declares `struct gse_context` and includes `rpc_server/rpc_pipes.h`. It declares no functions, macros beyond the include guard, or runtime data structures of its own.

## State And Persistence
There is no state or persistence in this header. It influences compilation dependencies by making RPC pipe types visible without pulling unrelated SMB declarations into each consumer.

## Dependencies And Integration Points
It integrates with RPC server pipe code, domain authentication flows, and GSS/GENSEC-related authentication contexts. Its value is mostly dependency hygiene for source3 domain and RPC code.

## Risks And Test Signals
Risks are include-order and dependency risks: removing the forward declaration or include can break consumers relying on transitive visibility, while adding heavy includes can increase coupling. Test signals are build coverage of source3 RPC/domain files, include-what-you-use checks, and authentication/RPC pipe compile tests with GENSEC-enabled and reduced configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ntdomain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ntioctl.h -->
# sources/user-network-fs/samba/source3/include/ntioctl.h

## Purpose
`ntioctl.h` defines the data shape for NT filesystem ioctl support currently represented here by shadow copy enumeration data. It supports FSCTL-style paths that expose Windows previous-version labels.

## Important APIs, Types, And Control Flow
`SHADOW_COPY_LABEL` is a 25-byte character array sized for labels such as `@GMT-2004.02.18-15.44.00` plus a terminator. `struct shadow_copy_data` contains `num_volumes` and a pointer to a concatenated list of labels. No functions are declared.

## State And Persistence
The structure is transient response state. `num_volumes` reports mounted shadow volumes, and `labels` points to memory owned by the caller or provider. Persistent snapshot data is managed by VFS shadow copy modules and the underlying filesystem, not this header.

## Dependencies And Integration Points
It integrates with FSCTL_GET_SHADOW_COPY_DATA handling, VFS shadow copy providers, SMB ioctl response construction, and clients listing previous versions. It depends only on fixed-width integer types and Samba allocation conventions in consumers.

## Risks And Test Signals
Risks include fixed label length mismatches, missing NUL termination, incorrect concatenation sizing, and confusing mounted snapshot count with returned label count. Test signals include shadow copy enumeration with zero, one, and many labels; exact label length boundary checks; malformed provider data rejection; SMB ioctl response size validation; and Windows client previous-versions browsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ntioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ntquotas.h -->
# sources/user-network-fs/samba/source3/include/ntquotas.h

## Purpose
`ntquotas.h` defines Windows NT quota flags, quota sentinel values, quota unit constants, quota type identifiers, and in-memory quota record/list/handle structures used by Samba quota handling.

## Important APIs, Types, And Control Flow
Quota flags cover enablement, deny-disk behavior, logging, content indexing, threshold/limit logging, incomplete/rebuilding states, and reserved bits. Sentinel values include no limit, no entry, and no space. Size constants span bytes through exabytes. `enum SMB_QUOTA_TYPE` distinguishes user filesystem quota, user quota, group filesystem quota, and group quota. `SMB_NTQUOTA_STRUCT` stores type, used space, soft/hard limits, flags, and SID. `SMB_NTQUOTA_LIST` links quota records with uid and talloc context. `SMB_NTQUOTA_HANDLE` tracks valid/current/temp lists.

## State And Persistence
The header models quota state returned from or written to system quota backends. Persistence is in filesystem quota systems and Samba quota databases/modules; linked lists and handles are transient enumeration/editing state.

## Dependencies And Integration Points
It depends on domain SID types, talloc, uid_t, and quota system wrappers declared elsewhere. It integrates with NT transact/query quota handlers, disk-free queries, sysquota backends, VFS modules, and Windows clients interpreting quota flags.

## Risks And Test Signals
Risks include sentinel values colliding with real limits, signed/unsigned conversion bugs, unsupported group filesystem quotas, stale temporary list handling, and mismatched flag semantics compared with Windows. Test signals include quota query/set round trips, no-limit/no-entry/no-space cases, large exabyte values, user versus group quota queries, SID-to-uid mapping failures, and backend-specific sysquota tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ntquotas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/passdb.h -->
# sources/user-network-fs/samba/source3/include/passdb.h

## Purpose
`passdb.h` is the central source3 account database interface. It defines SAM account records, group mapping records, search state, domain/trust structures, account policy identifiers, password history constants, backend capability bits, and the versioned `pdb_methods` module ABI used by passdb backends.

## Important APIs, Types, And Control Flow
Important types include `GROUP_MAP`, `acct_info`, `login_cache`, `struct samu`, `samr_displayentry`, `pdb_search`, `pdb_domain_info`, `pdb_trusted_domain`, `trustdom_info`, `enum pdb_policy_type`, and `struct pdb_methods`. `struct samu` tracks account fields, SIDs, password hashes/history/plaintext password, logon times, account flags, hours, counters, private backend data, and initialization/change bitmaps. `pdb_methods` is the backend vtable for user CRUD, group and alias management, SID/name lookup, account policies, searches, idmap, RID generation, trusted domains, secrets, UPN suffixes, responsibility routing, and backend cleanup. Public wrappers initialize and dispatch to the selected backend, manipulate `samu` fields, encode/decode password fields, update lockout counters, manage account policy/login cache, and access secrets-backed domain SID/GUID data.

## State And Persistence
Passdb state is persistent in selected backends such as tdbsam, LDAP, or secrets-backed storage. The header also defines transient `samu` objects with change tracking, search caches, login cache entries, trusted-domain blobs, account policy values, RID allocation state, and backend private data with custom destructors.

## Dependencies And Integration Points
It depends on generated LSA types, tevent, talloc, domain SIDs/GUIDs, DATA_BLOB, NTSTATUS, security descriptors, CLI credentials, unix id mapping, machine SID and lookup SID helpers, and passdb modules. It integrates with SAMR/LSA RPC servers, authentication, winbind/idmap, local user/group management, domain join/trust handling, account lockout, password change policy, and secrets storage.

## Risks And Test Signals
Risks include backend ABI version mismatch (`PASSDB_INTERFACE_VERSION`), incomplete change/set flag handling, password hash/history mishandling, RID algorithm collisions, search cache lifetime bugs, trust secret exposure, inconsistent responsibility routing between backends, and replicated SAM lockout cache errors. Test signals include backend registration/version tests, create/update/delete/rename user flows, group/alias membership enumeration, SID/name lookup, account policy defaults and persistence, bad password lockout transitions, password history update, trusted domain CRUD, UPN suffix CRUD, idmap round trips, `samu` serialization buffer versions, and secret get/set/delete through passdb.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/passdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/printing.h -->
# sources/user-network-fs/samba/source3/include/printing.h

## Purpose
`printing.h` defines Samba's low-level print subsystem contracts below spoolss. It abstracts platform print backends, print job state, queue status, print database handles, spool file handling, print notification registration, and print queue/job operations.

## Important APIs, Types, And Control Flow
Queue/job states include LPQ statuses and Samba's `PJOB_SMBD_SPOOLING`. `print_queue_struct` holds system job metadata, `print_status_struct` describes queue state, and `struct printjob` tracks smbd-launched spool jobs with pid, spoolss job id, system job id, fd, status, size, names, user/client, queue, and devmode. `struct printif` is the backend vtable for queue fetch/pause/resume, job delete/pause/resume/submit. The file declares generic, CUPS, and iPrint backends, job id mapping helpers, spool open/write/end/terminate paths, print job lifecycle functions, queue pause/resume/purge/status functions, backend initialization, LPQ parsing, print TDB open/release/close helpers, notify pid list access, and message receive handling.

## State And Persistence
Persistent state includes print TDBs (`PRINT_DATABASE_VERSION`), job id mappings, notify pid lists under `NOTIFY_PID_LIST_KEY`, spool files named with `PRINT_SPOOL_PREFIX`, backend system queue jobs, and printer-specific TDB handles with refcounts. Transient state lives in `printjob` records and queue/status structs.

## Dependencies And Integration Points
It depends on TDB, loadparm printing types, messaging, tevent, auth session info, spoolss devmode, files/connections, and CUPS/iPrint optional backends. It integrates with smbd file spooling, spoolss RPC, Unix print systems, printcap discovery, notification messaging, and platform-specific print commands.

## Risks And Test Signals
Risks include job id wraparound, stale print database handles, mismatched system job and spoolss job ids, backend command parsing differences, notify pid cleanup failures, spool file leaks, and platform default selection errors. Test signals include CUPS/BSD/SYSV backend queue parsing, job start/write/end/delete/pause/resume, queue pause/resume/purge, TDB version handling, print notify registration cleanup, system job id mapping, spool termination on close/error, and build tests with and without CUPS/iPrint.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/printing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/proto.h -->
# sources/user-network-fs/samba/source3/include/proto.h

## Purpose
`proto.h` is a frozen collected-prototypes header for source3 support code, originally generated by `make proto`. It gathers declarations from many library and libsmb implementation files so legacy source3 modules can share utility APIs without including each implementation header separately.

## Important APIs, Types, And Control Flow
The declarations span audit string helpers, character set push/pull conversion, debug/memory messages, NT/unix error mapping, file id/stat helpers, LDAP escaping and debug setup, Microsoft wildcard matching, sendfile/recvfile, named mutexes, share security, shell command execution, quota wrappers, system/stat/socket wrappers, time conversion, passwd/group helpers, name/domain helpers, fork reinitialization, array allocation, process existence, privilege and credential switching, path/filename utilities, SID helpers, socket open/read helpers, string substitution/matching, version strings, WINS server cache functions, negative connection cache, name cache, domain controller lookup, SMB error mapping, trust password change, session traversal, Avahi integration, well-known SID helpers, filename conversion, dummy root hooks, smbd shim functions, level2 oplock contention hooks, and per-thread cwd controls.

## State And Persistence
The header owns no state, but it exposes APIs that touch many persistent stores and global states: share security databases, quota systems, WINS/name caches, negative connection cache, sessionid TDB, process credential state, server zone offsets, remote architecture cache, and Samba daemon reinit state.

## Dependencies And Integration Points
It depends on broad source3 types, regex, access utilities, wbclient, interface helpers, quota types, security tokens, networking, generated Netlogon/SID types, and many source3 subsystems. It is an integration point for legacy code still relying on collected declarations instead of narrow module headers.

## Risks And Test Signals
Risks include stale prototypes diverging from implementations, duplicate declarations such as repeated `sys_recvfile()` and `automount_lookup()`, hidden coupling from broad includes, and accidental ABI/API changes missed by narrow tests. Test signals are full source3 builds with warnings as errors for prototype mismatches, link coverage of all declared functions, focused tests for share security, quota, socket, charset, SID, filename, and credential helpers, plus include cleanup tests when replacing `proto.h` consumers with narrower headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/registry.h -->
# sources/user-network-fs/samba/source3/include/registry.h

## Purpose
`registry.h` defines Samba's virtual Windows registry layer types, operation table, key handle structures, root key constants, well-known registry path strings, and registry key type identifiers.

## Important APIs, Types, And Control Flow
`struct registry_value` pairs a generated winreg type with a `DATA_BLOB`. `struct registry_ops` is the backend vtable for fetching/storing subkeys and values, creating/deleting subkeys, access checks, security descriptor get/set, and checking whether cached subkey/value containers need updates. `registry_key_handle` stores key type, full key name, granted access, and ops pointer. `registry_key` combines the handle with cached subkey/value containers and caller token. Constants define Windows root handles (`HKEY_LOCAL_MACHINE`, etc.), short key names (`HKLM`, `HKU`, etc.), many Samba/Windows registry paths for services, eventlog, shares, netlogon, TCP/IP, product options, printing, perflib, group policy, smbconf, and generic/performance key types.

## State And Persistence
The header models registry state persisted by registry backends, TDB files, virtual providers, or generated views. Runtime handles cache subkeys/values and security tokens; access-granted state is stored per handle.

## Dependencies And Integration Points
It depends on generated winreg NDR, DATA_BLOB, WERROR, security tokens/descriptors, and registry object containers declared elsewhere. It integrates with winreg RPC, Samba registry backends, printing registry keys, Group Policy, smb.conf registry storage, share definitions, eventlog, and performance counters.

## Risks And Test Signals
Risks include backend ops not honoring access masks, stale cached subkey/value containers, key string normalization bugs, lazy delete semantics differing by backend, and security descriptor persistence errors. Test signals include winreg create/open/delete/enumerate/set/get flows, access-denied cases, security descriptor round trips, printing key updates, smbconf registry operations, performance key reads, and cache invalidation through `subkeys_need_update()`/`values_need_update()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/registry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/rpc_dce.h -->
# sources/user-network-fs/samba/source3/include/rpc_dce.h

## Purpose
`rpc_dce.h` defines DCE/RPC fragment and header constants used by source3 RPC code. It captures Samba's maximum signing trailer size, selected maximum PDU fragment length, fixed RPC header length, and endianness markers.

## Important APIs, Types, And Control Flow
There are no functions or structs. Important constants are `RPC_MAX_SIGN_SIZE` (56 bytes), `RPC_MAX_PDU_FRAG_LEN` (`0x10b8`, matching Windows 2000 behavior per the comment), `RPC_HEADER_LEN` (16), and byte-order flags `RPC_BIG_ENDIAN` and `RPC_LITTLE_ENDIAN`.

## State And Persistence
The header contains no state. Its constants govern transient RPC PDU allocation, fragmentation, signing space reservation, and marshalling decisions.

## Dependencies And Integration Points
It integrates with RPC server/client fragment generation, DCE/RPC bind and request handling, signing/sealing code, and generated NDR marshalling that needs fragment size limits.

## Risks And Test Signals
Risks include fragment sizes incompatible with clients, insufficient signing trailer reservation, assuming little-endian data where big-endian is negotiated, and memory sizing errors around fixed header length. Test signals include RPC bind/request fragmentation, signed and unsigned calls, large spoolss/LSA/SAMR requests near fragment boundaries, endian marker parsing, and interoperability with Windows clients expecting the selected fragment size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/rpc_dce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/rpc_misc.h -->
# sources/user-network-fs/samba/source3/include/rpc_misc.h

## Purpose
`rpc_misc.h` contains a small RPC diagnostic helper for policy handle ownership. It lets debug messages classify a handle as null, owned by the current process, or owned by another process.

## Important APIs, Types, And Control Flow
The `OUR_HANDLE(hnd)` macro expands to three printf-style values: a string (`NULL`, `OURS`, or `OTHER`), the process id encoded in the handle UUID node field at offset 2, and the current `getpid()` value. It uses Samba's `IVAL()` macro to read the embedded pid.

## State And Persistence
No state is stored here. The macro inspects a policy handle's UUID bytes and current process id at log/debug time. Policy handle persistence and lifetime are managed by RPC server handle tables elsewhere.

## Dependencies And Integration Points
It depends on generated policy handle shapes that expose `uuid.node`, Samba byte extraction macros, and POSIX `getpid()`. It integrates with RPC server diagnostics for handles used by SAMR, LSA, winreg, spoolss, and related pipes.

## Risks And Test Signals
Risks include relying on a pid encoding convention in UUID node bytes, format-string misuse because the macro expands to multiple arguments, and misleading diagnostics after pid reuse or cross-process handle transfer. Test signals include debug builds that log null/current/foreign handles, compile checks for policy handle layout, and RPC handle lifecycle tests across open/use/close and process-boundary cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/rpc_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/secrets.h -->
# sources/user-network-fs/samba/source3/include/secrets.h

## Purpose
`secrets.h` defines key names, data formats, and APIs for Samba's private secrets database. It covers machine account passwords, previous passwords, domain SID/GUID, LDAP bind passwords, schannel keys, authenticated IPC credentials, AFS keyfiles, generic secrets, Kerberos salting principals, machine password changes, trusted domain passwords, and LSA secrets.

## Important APIs, Types, And Control Flow
String constants define stable keys under `SECRETS/` and related namespaces. `struct machine_acct_pass` stores an NT hash and modification time. `struct afs_key` and `struct afs_keyfile` model OpenAFS keyfiles with up to eight keys. APIs initialize/shutdown the secrets DB, fetch/store/delete raw entries, store credentials, manage domain protection/SID/GUID, fetch/store trusted domain and machine passwords, handle join context storage, debug and stringify domain info, prepare/fail/defer/finish password changes, delete machine/domain secrets, manage LDAP passwords, AFS keys, IPC credentials, generic owner/key secrets, Kerberos DES salt, and get/set/delete LSA secrets with old/current blobs and security descriptors.

## State And Persistence
The primary persistent state is `secrets.tdb` under Samba's private directory, initialized by `secrets_init_path()` or `secrets_init()`. Password change APIs preserve current and previous password material, last-change times, secure channel type, supported encryption data, and salting principal information. LSA secret APIs track current and old values plus timestamps and security descriptors.

## Dependencies And Integration Points
It depends on replace, generated security types, DATA_BLOB, GUID/SID/NTTIME/NTSTATUS, netlogon secure channel enums, CLI credentials, libnet join context, and secrets domain info structures. It integrates with domain join, Netlogon trust password changes, winbind, LDAP auth, Kerberos keytab sync callbacks, passdb secret wrappers, and LSA RPC secret management.

## Risks And Test Signals
Risks include plaintext secret exposure, incorrect previous-password handling during failed/deferred changes, domain/realm deletion mismatch, stale keytab sync after password changes, insecure generic secret ownership, and security descriptor loss for LSA secrets. Test signals include secrets DB init/fetch/store/delete, machine password rotation success/fail/defer flows, previous password retrieval, trusted domain password CRUD, domain SID/GUID persistence, LDAP password storage, AFS key lookup, IPC credential fetch, generic secret round trips, Kerberos salt storage, and LSA secret old/current timestamp/security descriptor tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/secrets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/serverid.h -->
# sources/user-network-fs/samba/source3/include/serverid.h

## Purpose
`serverid.h` declares the source3 helper used to test whether a Samba `server_id` still represents a live server process. This is a reliability boundary for cleanup and ownership checks.

## Important APIs, Types, And Control Flow
The only API is `bool serverid_exists(const struct server_id *id)`. Callers pass a generated `server_id`, and the implementation determines whether that server still exists. The header includes `replace.h` and generated `server_id` definitions.

## State And Persistence
No state is stored in the header. The implementation may consult process state, messaging/server-id databases, clustering state, or pid/liveness primitives. Results affect cleanup of records owned by dead processes.

## Dependencies And Integration Points
It integrates with messaging cleanup, locking/share-mode cleanup, process existence checks, cluster-aware server identity, and any subsystem that stores ownership by `server_id`.

## Risks And Test Signals
Risks include false positives after pid reuse, false negatives in clustered configurations, and cleanup races while a process is starting or exiting. Test signals include live and dead process checks, server-id database cleanup, pid reuse simulations, clustered/non-clustered builds, and consumers such as locks or messaging removing stale entries only after reliable liveness detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/serverid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/session.h -->
# sources/user-network-fs/samba/source3/include/session.h

## Purpose
`session.h` defines the `sessionid` record used to describe currently valid SMB user sessions. These records are claimed during session setup and released when the corresponding VUID/session is destroyed, supporting session tracking, utmp, PAM, and administrative enumeration.

## Important APIs, Types, And Control Flow
`struct sessionid` stores Unix uid/gid, username, hostname, NetBIOS name, remote machine, textual and numeric ids, owning `server_id`, IP string, connection start time, negotiated dialect, authentication flag, encryption flags, cipher, signing mode, signing flags, and a pointer to the `smbXsrv_session_global0` global session record. The header declares no functions; traversal is exposed elsewhere, notably through `sessionid_traverse_read()` in `proto.h`.

## State And Persistence
The structure represents persisted or shared session database entries, commonly backed by sessionid TDB code. It captures security and transport state at login time and links records to the owning smbd process through `server_id`.

## Dependencies And Integration Points
It depends on Samba fixed strings (`fstring`), generated `server_id`, SMB dialect/security types, and smbXsrv session global structures. It integrates with session setup/teardown, PAM/utmp accounting, admin tools that list sessions, encryption/signing reporting, and cleanup for dead server processes.

## Risks And Test Signals
Risks include stale records after abnormal disconnect, fixed-string truncation of host/user names, inconsistent authenticated/encryption/signing reporting, dangling `global` pointers if persisted incorrectly, and cleanup errors when server ids are reused. Test signals include session setup and logoff record creation/deletion, crash cleanup, traversal output, long username/hostname truncation, guest versus authenticated sessions, SMB dialect/encryption/signing metadata, and multi-session-per-process behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/session.h -->
