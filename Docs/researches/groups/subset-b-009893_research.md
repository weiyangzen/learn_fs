# subset-b-009893 Research

Grouped research for Samba `source3/winbindd` idmap, NSS-info, and selected async winbind request helpers. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_autorid_tdb.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_autorid_tdb.c

## Purpose
This file implements the shared `autorid.tdb` database operations used by the `idmap_autorid` backend and `net idmap autorid` tooling. It manages deterministic domain/range assignments, global autorid configuration, high-water marks, range deletion, and range iteration. The database schema is compact: domain SID keys, optionally suffixed with `#<domain_range_index>`, map to numeric range IDs; numeric range ID keys map back to the domain/index key; `CONFIGKEY` stores `minvalue`, `rangesize`, and `maxranges`; HWM records track the next allocatable range and special allocation pools.

## Important APIs, Types, And Functions
The exported API includes `idmap_autorid_setrange`, `idmap_autorid_acquire_range`, `idmap_autorid_getrange`, `idmap_autorid_get_domainrange`, `idmap_autorid_delete_range_by_sid`, `idmap_autorid_delete_range_by_num`, `idmap_autorid_db_open`, `idmap_autorid_db_init`, `idmap_autorid_init_hwms`, `idmap_autorid_loadconfig`, `idmap_autorid_saveconfig`, `idmap_autorid_saveconfigstr`, `idmap_autorid_iterate_domain_ranges`, `idmap_autorid_iterate_domain_ranges_read`, and `idmap_autorid_delete_domain_ranges`. `struct autorid_range_config` and `struct autorid_global_config` come from `idmap_autorid_tdb.h`.

## Control Flow
Range creation funnels through `idmap_autorid_addrange`, which runs `idmap_autorid_addrange_action` inside `dbwrap_trans_do`. The action validates the domain SID or the special `ALLOC_RANGE`, checks for an existing forward mapping, loads global config, decides the requested or next HWM range, validates capacity and reverse-key availability, increments HWM when needed, then writes both directions. Lookup uses `idmap_autorid_getrange_int`, and `idmap_autorid_get_domainrange` optionally acquires a missing range unless read-only. Delete-by-SID and delete-by-number both validate forward/backward consistency and support `force` to remove partially corrupt mappings. Iteration traverses db records, parses `<sid>[#<index>]`, filters invalid records, and invokes caller callbacks.

## State And Persistence
All persistent state is in a dbwrap/TDB database opened by `idmap_autorid_db_open`. High-water mark initialization is transactional. Range allocation and deletion are transactional, preserving forward/reverse consistency in normal operation. The code intentionally does not shrink HWM on deletion, so deleted ranges are not automatically reused through ordinary allocation. Config changes reject changed `minvalue` or `rangesize`, and reject `maxranges` values below the current HWM.

## Dependencies And Integration
The file depends on `dbwrap`, TDB string helpers, Samba SID parsing/stringification, and constants from `idmap_autorid_tdb.h`. `idmap_autorid.c` uses it during idmap backend initialization and SID/RID mapping. Administrative tooling can use the same APIs to inspect or repair the database.

## Risks And Test Signals
Test database creation, config persistence, duplicate range insertion, explicit range below/above HWM, automatic acquire, capacity exhaustion, `#index` parsing, read-only lookup behavior, forced and non-forced delete of invalid mappings, and iteration over mixed valid/invalid records. Corruption handling is careful but depends on fixed string formats and uint32 value sizes. Capacity exhaustion currently maps to `NT_STATUS_NO_MEMORY`, which can obscure the real cause. Tests should also cover non-null-terminated config data because retrieval uses `talloc_strndup`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_autorid_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_hash/idmap_hash.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_hash/idmap_hash.c

## Purpose
This deprecated backend maps SIDs to Unix IDs by hashing a domain SID and RID into a 31-bit ID. It also registers an NSS-info backend named `hash` that maps user aliases through an optional name-map file. It is only valid for the default `*` idmap configuration and is explicitly marked for migration away from the module.

## Important APIs, Types, And Functions
`struct sid_hash_table` holds a 4096-entry table of domain SID pointers keyed by a 12-bit hash. `hash_domain_sid`, `hash_rid`, `combine_hashes`, and `separate_hashes` implement the mapping math. `idmap_hash_initialize`, `unixids_to_sids`, and `sids_to_unixids` provide `struct idmap_methods`. `nss_hash_map_to_alias` and `nss_hash_map_from_alias` provide `struct nss_info_methods`. `idmap_hash_init` registers both the idmap and NSS-info interfaces.

## Control Flow
Initialization logs deprecation, rejects non-default domains, fetches the trusted-domain cache, skips null SIDs and domains with explicit idmap config, hashes valid domain SIDs, and stores them in the table. ID-to-SID splits the ID into domain hash and RID hash, looks up the domain SID table, composes a SID, and returns `ID_TYPE_BOTH`. SID-to-ID splits the RID from the SID, computes hashes, reuses or remembers the domain if it is known through the trusted-domain cache or `netsamlogon_cache_have`, and returns `ID_TYPE_BOTH`. If a domain is not yet known and the requested type is not specified, it sets `ID_REQUIRE_TYPE` to trigger parent fallback behavior.

## State And Persistence
State is memory-only in `dom->private_data`, with additional domain validity from the trusted-domain cache and samlogon cache. There is no durable allocation database; mappings are deterministic and collision-prone by construction. The NSS alias path reads the configured map file on each lookup through `mapfile.c`.

## Dependencies And Integration
The module integrates with idmap registration, NSS-info registration, winbind trusted-domain cache (`wcache_tdc_fetch_list`), domain configuration checks, SID helpers, samlogon cache, and mapfile lookup helpers. It relies on winbind parent behavior for fallback when a domain is unknown.

## Risks And Test Signals
Hash collisions can map unrelated domains/RIDs to the same Unix ID. Only SIDs with exactly four authorities are accepted by `hash_domain_sid`. RID zero maps to unmapped. Tests should cover default-domain enforcement, known-domain table population, samlogon-cache learning, collision behavior, `ID_REQUIRE_TYPE`, and partial mapping return codes. Also test build coverage with `mapfile.c`: `mapfile_lookup_value` appears to check `!*key` after assigning `*value`, which is not a valid local variable in that function and should be caught by compilation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_hash/idmap_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_hash/idmap_hash.h -->
# sources/user-network-fs/samba/source3/winbindd/idmap_hash/idmap_hash.h

## Purpose
This header provides small helper macros and the name-map lookup prototypes used by the deprecated hash idmap/NSS-info module. Despite the include guard name `_LWOPEN_H`, it belongs to the `idmap_hash` backend and exposes map-file key/value lookup helpers.

## Important APIs, Types, And Functions
The header defines `BAIL_ON_NTSTATUS_ERROR`, `BAIL_ON_PTR_NT_ERROR`, and `PRINT_NTSTATUS_ERROR`. It declares `mapfile_lookup_key(TALLOC_CTX *, const char *value, char **key)` and `mapfile_lookup_value(TALLOC_CTX *, const char *key, char **value)`.

## Control Flow
The macros are goto-based error handling helpers. `BAIL_ON_NTSTATUS_ERROR` jumps to `done` on a failing NT status. `BAIL_ON_PTR_NT_ERROR` sets an NT status based on pointer nullness, logging and jumping to `done` if allocation failed. The prototypes connect `idmap_hash.c` with `mapfile.c`.

## State And Persistence
The header itself has no state. It participates in map-file access where `mapfile.c` uses a static `FILE *` and an smb.conf parameter for the file path.

## Dependencies And Integration
Consumers must have Samba `NTSTATUS`, debug logging, and talloc types available. The macros assume the caller has a `done:` label and a writable status variable named in the macro argument, so they are tightly coupled to local function structure.

## Risks And Test Signals
Macro-based control flow can hide ownership and cleanup paths. Tests should compile all consumers with warnings enabled and exercise both map-file lookup directions. The misleading include guard name can collide with unrelated historical `lwopen` headers if one exists in the include path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_hash/idmap_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_hash/mapfile.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_hash/mapfile.c

## Purpose
This file implements simple bidirectional lookup against the optional `idmap_hash:name_map` text file used by the hash NSS-info backend. The file format is line-oriented `key=value`, with whitespace trimming around each side.

## Important APIs, Types, And Functions
The public functions are `mapfile_lookup_key`, which searches by value and returns the matching key, and `mapfile_lookup_value`, which searches by key and returns the matching value. Helpers include `mapfile_open`, `mapfile_read_line`, and `mapfile_close`. The module uses a static `FILE *lw_map_file`.

## Control Flow
Each lookup opens or rewinds the configured file, loops through parsed lines with `mapfile_read_line`, compares using `strequal`, talloc-duplicates the result into the caller context, then closes the file. `mapfile_read_line` strips newline and carriage returns, splits at the first `=`, copies both halves into `fstring` buffers, and trims spaces.

## State And Persistence
The persistent source is the external map file named by `lp_parm_const_string(-1, "idmap_hash", "name_map", NULL)`. The static file handle is opened per lookup and closed before return. There is no cache, locking, reload notification, or validation beyond line parsing.

## Dependencies And Integration
The code depends on Samba configuration access, fstring/string wrappers, talloc, and the hash NSS-info hooks in `idmap_hash.c`. It is used for alias normalization rather than core SID/ID hashing.

## Risks And Test Signals
Malformed lines stop that line but the loop continues only if the next read succeeds; very long lines are truncated to 1023 bytes. There is a concrete defect in `mapfile_lookup_value`: after `*value = talloc_strdup(...)`, it checks `if (!*key)` even though `key` is the input key string, not the output pointer; as written this is either a compile failure or an incorrect allocation check depending on compiler context. Tests should cover missing config, missing file, empty file, whitespace trimming, duplicate keys/values, long lines, malformed lines, and allocation-failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_hash/mapfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_ldap.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_ldap.c

## Purpose
This backend stores SID-to-Unix-ID mappings and allocation state in LDAP. It supports allocating new UID/GID values from a `sambaUnixIdPool` entry and creating `sambaIdmapEntry`/SID objects under a configured suffix. It is online-only and refuses operations when `idmap_is_offline()` is true.

## Important APIs, Types, And Functions
`struct idmap_ldap_context` holds `smbldap_state`, URL, suffix, bind DN, anonymous flag, and `idmap_rw_ops`. Initialization is `idmap_ldap_db_init`; allocation is `idmap_ldap_allocate_id_internal` and default-domain wrapper `idmap_ldap_allocate_id`; persistence is `idmap_ldap_set_mapping`; mapping is `idmap_ldap_unixids_to_sids` and `idmap_ldap_sids_to_unixids`; `idmap_ldap_init` registers the backend. Credential setup is in `get_credentials`, and pool verification/creation is in `verify_idpool`.

## Control Flow
Initialization reads `ldap_url` and `ldap_base_dn` or the global LDAP idmap suffix, initializes an smbldap connection, fetches credentials from `idmap config <domain> : ldap_user_dn` secret storage or legacy LDAP password storage, sets a destructor, and verifies the id pool. Allocation searches for the single idpool object, reads `uidNumber` or `gidNumber`, range-checks it, then atomically modifies LDAP by deleting the old attribute value and adding the incremented value. Mapping lookups build one LDAP filter for a single map or batched OR filters up to `IDMAP_LDAP_MAX_IDS`, parse returned SID/uidNumber/gidNumber attributes, match them back to requested maps, and mark unmapped entries. SID-to-ID additionally attempts `idmap_rw_new_mapping` for unmapped SIDs.

## State And Persistence
Persistent state lives in LDAP: pool counters under `sambaUnixIdPool` and mapping entries named by SID under the suffix. New mappings are not wrapped in a multi-operation LDAP transaction, so allocation and entry creation can diverge on failure. The context holds one smbldap connection and is freed by destructor.

## Dependencies And Integration
The file depends on OpenLDAP APIs, Samba `smbldap`, passdb LDAP schema names, secrets, global tevent context, `idmap_rw`, and idmap utility lookup helpers. It integrates with the idmap allocator contract and Samba configuration.

## Risks And Test Signals
Test offline behavior, missing URL/suffix, anonymous and authenticated binds, missing/multiple idpool entries, allocation at high_id, malformed numeric attributes, duplicate LDAP entries, batched filters, and unmapped SID allocation requiring type hints. The allocation operation is only as atomic as the LDAP modify on a single pool entry; mapping creation can leave consumed IDs without entries. LDAP filters include stringified SIDs and numeric IDs; escaping and schema assumptions should be validated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_ldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_nss.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_nss.c

## Purpose
The `nss` idmap backend maps between Unix users/groups known to the local NSS stack and SIDs resolved through winbind name/SID lookup calls. It is read-only in practice: it queries libc `getpw*`/`getgr*` and winbind rather than persisting mappings.

## Important APIs, Types, And Functions
`struct idmap_nss_context` stores the owning `idmap_domain` and `use_upn` config flag. `idmap_nss_int_init` creates context and installs a messaging filtered read for smb.conf reloads. `idmap_nss_unixids_to_sids` maps UID/GID to names and then to SIDs. `idmap_nss_sids_to_unixids` maps SIDs to names and then to local passwd/group entries. `idmap_nss_init` registers the backend.

## Control Flow
Initialization creates context, stores it in `dom->private_data`, and subscribes to `MSG_SMB_CONF_UPDATED` so `use_upn` can be refreshed. UID/GID lookup calls `getpwuid` or `getgrgid`, optionally parses UPN or domain separator components, and calls `winbind_lookup_name` while winbind recursion is temporarily enabled via `winbind_on/off`. SID lookup calls `winbind_lookup_sid`, rejects SIDs whose domain does not match the configured idmap domain, optionally builds `DOMAIN\name`, and then uses `Get_Pwnam_alloc` or `getgrnam`.

## State And Persistence
State is memory-only. The backend depends on external NSS databases, winbind cache/domain state, and live smb.conf reload messages. It does not allocate or store mappings.

## Dependencies And Integration
The file integrates with Samba messaging, global messaging context, winbind client utilities, libc NSS, and idmap registration. It uses `lp_winbind_separator`, `idmap_config_bool`, and domain name comparisons.

## Risks And Test Signals
Test config reload of `use_upn`, UPN parsing with `@`, separator parsing with configured separator, mismatched domains, unavailable NSS records, wrong SID types, and recursion safety around `winbind_on/off`. The code mutates the `pw_name`/`gr_name` string when splitting at a separator or `@`, so tests should ensure the returned libc buffers are not reused unexpectedly in the same flow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_nss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_passdb.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_passdb.c

## Purpose
This small backend delegates mapping entirely to Samba passdb. It maps Unix IDs to SIDs with `pdb_id_to_sid` and SIDs to Unix IDs with `pdb_sid_to_id`.

## Important APIs, Types, And Functions
The backend methods are `idmap_pdb_init`, `idmap_pdb_unixids_to_sids`, and `idmap_pdb_sids_to_unixids`. `idmap_passdb_init` registers the backend under `passdb`.

## Control Flow
Initialization is a no-op returning OK. For Unix-ID-to-SID, each requested map is marked `ID_UNMAPPED`, then promoted to `ID_MAPPED` if passdb returns a SID. For SID-to-Unix-ID, each map is marked mapped or unmapped based on `pdb_sid_to_id`.

## State And Persistence
This file holds no state. Persistent identity information comes from the configured passdb backend.

## Dependencies And Integration
It includes `passdb.h` and the idmap interface. It is useful where Samba account database state is authoritative for local mappings.

## Risks And Test Signals
Tests should cover both mapping directions for users and groups, missing passdb records, passdb backend errors exposed as boolean failures, and mixed arrays where some records map and others do not. The functions always return `NT_STATUS_OK`, so callers must inspect per-map statuses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_passdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_proto.h -->
# sources/user-network-fs/samba/source3/winbindd/idmap_proto.h

## Purpose
This generated-style prototype header exposes idmap subsystem functions and backend init entry points used by winbindd source files. It centralizes declarations for idmap core, built-in backends, utility helpers, and LDAP batch sizing.

## Important APIs, Types, And Functions
Core declarations include `idmap_is_offline`, `smb_register_idmap`, `idmap_close`, `idmap_allocate_uid`, `idmap_allocate_gid`, `idmap_backend_unixids_to_sids`, and `idmap_find_domain`. Backend init declarations include `idmap_nss_init`, `idmap_passdb_init`, `idmap_tdb_init`, and `idmap_ad_nss_init`. Utility declarations include range checking, map lookup by ID/SID, secret fetching, and `id_map_ptrs_init`. `IDMAP_LDAP_MAX_IDS` is defined as 30.

## Control Flow
The header does not implement control flow. Its structure groups declarations by originating file comments, which helps link backend modules to the core idmap API.

## State And Persistence
No state is held here. The declared functions touch global idmap registry state, backend private data, secrets, TDB, LDAP, and caches depending on implementation.

## Dependencies And Integration
It assumes `idmap.h` has declared `struct idmap_domain`, `struct id_map`, `struct unixid`, `struct dom_sid`, and `struct idmap_methods`. It is included indirectly by `source3/include/idmap.h`.

## Risks And Test Signals
Build tests are the main signal: stale prototypes will surface as incompatible declarations or missing symbols. `IDMAP_LDAP_MAX_IDS` affects LDAP batching in multiple files, so behavioral tests should include batch sizes of 0, 1, 30, and 31.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_rfc2307.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_rfc2307.c

## Purpose
This read-only backend maps SIDs and Unix IDs through RFC2307 user/group records. It performs two-stage mapping: SID/name resolution through winbind/AD, then name/UID/GID lookup in either AD LDAP or a stand-alone LDAP server.

## Important APIs, Types, And Functions
`struct idmap_rfc2307_context` stores bind paths, LDAP domain override, `user_cn`, realm, active LDAP pointer, connection check/search function pointers, ADS state, and stand-alone smbldap state. Initialization is split between `idmap_rfc2307_init_ads`, `idmap_rfc2307_init_ldap`, and `idmap_rfc2307_initialize`. Mapping functions are `idmap_rfc2307_unixids_to_sids` and `idmap_rfc2307_sids_to_unixids`, with helpers for ADS/LDAP search and result matching.

## Control Flow
Initialization requires `bind_path_user`, `bind_path_group`, and `ldap_server` set to `ad` or `stand-alone`. AD mode configures cached ADS connection checks and searches; stand-alone mode reads `ldap_url` and optional `ldap_user_dn` secret, then initializes smbldap. Unix-ID-to-SID builds batched user and group RFC2307 filters, searches LDAP, extracts names and numeric IDs, then calls `winbind_lookup_name` to obtain SIDs. SID-to-Unix-ID first calls `winbind_lookup_sid` to determine names and SID types, uppercases names into an internal map array, searches RFC2307 records by `uid`/`cn`, and assigns IDs.

## State And Persistence
The backend stores only connection/config state. RFC2307 records and AD directory content are authoritative; no allocations or local durable mappings are created. The destructor frees ADS and smbldap state.

## Dependencies And Integration
It depends on `smbldap`, ADS helpers, winbind client lookup utilities, idmap config, global event context, and SID helpers. It temporarily enables winbind recursion around lookup calls with `winbind_on/off`.

## Risks And Test Signals
Test both `ldap_server` modes, missing bind paths, missing LDAP URL, authenticated/anonymous stand-alone LDAP, `ldap_domain` override, `realm` suffixing/stripping, `user_cn`, mixed UID/GID batches, and name case behavior. The code uppercases names and builds LDAP filters without visible escaping, so special characters in names and realms deserve explicit tests. Result arrays are status-based; tests should verify unmapped entries remain clear when LDAP returns unrelated records.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_rfc2307.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_rid.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_rid.c

## Purpose
This deterministic backend maps between a domain SID's RID and Unix IDs using arithmetic: `unix_id = rid - base_rid + low_id`. It does not allocate or persist mappings.

## Important APIs, Types, And Functions
`struct idmap_rid_context` stores `base_rid`. `idmap_rid_initialize` reads `idmap config <domain> : base_rid`. `idmap_rid_id_to_sid` composes a SID from `dom->dom_sid` and computed RID. `idmap_rid_sid_to_id` extracts a RID and computes the Unix ID. Batch wrappers are `idmap_rid_unixids_to_sids` and `idmap_rid_sids_to_unixids`. `idmap_rid_init` registers the backend.

## Control Flow
Initialization allocates private context. ID-to-SID checks the Unix ID range, rejects missing domain SID, composes the SID with RID `id - low_id + base_rid`, marks `ID_TYPE_BOTH`, and sets mapped. SID-to-ID extracts RID, computes ID, sets `ID_TYPE_BOTH`, and range-filters the result.

## State And Persistence
Only `base_rid` is stored in memory. The mapping is derived from domain config and the domain SID supplied by the idmap subsystem.

## Dependencies And Integration
It depends on idmap config, `idmap_unix_id_is_in_range`, SID compose/extract helpers, and idmap registration. It is usually configured per trusted domain.

## Risks And Test Signals
Test low/high boundary IDs, `base_rid` nonzero, IDs below `low_id`, RIDs below `base_rid` causing uint32 underflow, null domain SID, and SID values outside configured range. The batch functions log unexpected errors but return OK, so per-map status assertions are essential.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_rid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_rw.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_rw.c

## Purpose
This file implements the backend-independent "allocate and store a new mapping" sequence used by writable idmap backends. It centralizes type validation, allocation calls, storage calls, and collision retry behavior.

## Important APIs, Types, And Functions
The exported function is `idmap_rw_new_mapping(struct idmap_domain *dom, struct idmap_rw_ops *ops, struct id_map *map)`. `struct idmap_rw_ops` is declared in `idmap_rw.h` and supplies `get_new_id` and `set_mapping`.

## Control Flow
The function validates `map` and `map->sid`. If the requested type is `ID_TYPE_NOT_SPECIFIED` or `ID_TYPE_BOTH`, it sets `map->status = ID_REQUIRE_TYPE` and returns `NT_STATUS_SOME_NOT_MAPPED`, requiring the caller/parent to supply a UID/GID hint. UID and GID requests call `ops->get_new_id`, mark the map as mapped, then call `ops->set_mapping`. If storage reports `NT_STATUS_OBJECT_NAME_COLLISION`, the code retries lookup through `dom->methods->sids_to_unixids`.

## State And Persistence
This file owns no persistence. Backend ops perform allocation and storage, typically in TDB or LDAP. The caller is responsible for wrapping the sequence in a transaction where the backend supports it.

## Dependencies And Integration
It depends on idmap domain methods, SID string helpers, and backend-provided `idmap_rw_ops`. `idmap_tdb_common`, `idmap_ldap`, and autorid-related code use this abstraction.

## Risks And Test Signals
Test null inputs, `ID_TYPE_NOT_SPECIFIED`, `ID_TYPE_BOTH`, UID/GID allocation success, allocation failure, set failure, collision retry, and caller transactions. The collision path recursively uses the domain's `sids_to_unixids`; tests should ensure this does not re-enter allocation indefinitely.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_rw.h -->
# sources/user-network-fs/samba/source3/winbindd/idmap_rw.h

## Purpose
This header declares the abstract read/write idmap operation table and the shared helper for creating a new SID-to-Unix-ID mapping. It lets allocating backends reuse common mapping creation logic while preserving backend-specific storage.

## Important APIs, Types, And Functions
`struct idmap_rw_ops` has `get_new_id` and `set_mapping` callbacks. `idmap_rw_new_mapping` accepts a domain, ops table, and map with `sid` and requested `xid.type`.

## Control Flow
The header documents the required caller contract: invoke the helper from a backend's `sids_to_unixids` implementation, provide a type hint, and handle atomicity externally. No executable code is present.

## State And Persistence
No state is held here. Persistence happens through callback implementations.

## Dependencies And Integration
It depends on `idmap.h` for `struct idmap_domain`, `struct id_map`, `struct unixid`, and `NTSTATUS`. It is used by TDB, LDAP, and autorid allocation flows.

## Risks And Test Signals
ABI/build tests should ensure all writable backends initialize both callbacks before calling the helper. Behavioral tests should verify each backend honors the documented transaction requirement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_rw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_script.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_script.c

## Purpose
This read-only backend delegates SID/Unix-ID mapping to an external script. It supports `SIDTOID <sid>` and `IDTOSID <type> <id>` commands and parses `XID:`, `UID:`, `GID:`, `SID:`, or unmapped/error output.

## Important APIs, Types, And Functions
`struct idmap_script_context` stores the script path. Async helpers `idmap_script_xid2sid_send/recv` and `idmap_script_sid2xid_send/recv` execute one script call via `file_ploadv_send`. Batch helpers `idmap_script_xids2sids` and `idmap_script_sids2xids` run a temporary tevent loop. Backend methods are `idmap_script_unixids_to_sids`, `idmap_script_sids_to_unixids`, and `idmap_script_db_init`. `idmap_script_init` registers the backend.

## Control Flow
Initialization reads `idmap config <domain> : script`, falls back to deprecated `idmap:script` for the default domain, talloc-copies the script path, and marks the domain read-only. Unix-ID-to-SID initializes statuses, launches one child process per requested ID, parses null-terminated output up to 1024 bytes, and returns aggregate all/some/none mapped status. SID-to-ID follows the same pattern and filters returned IDs against the configured idmap range.

## State And Persistence
The backend stores only the script path in memory. Persistent or authoritative mapping state is external to Samba and owned by the script or its backing store.

## Dependencies And Integration
It depends on tevent, `file_ploadv_send`, Samba argument-list helpers, SID parsing, idmap range utilities, and Unix-to-NT error mapping. It integrates as a normal idmap backend but does not allocate.

## Risks And Test Signals
Test missing script config, invalid ID type, nonzero child execution errors, empty output, non-null-terminated output, oversized output, malformed `SID:`/`UID:`/`GID:`/`XID:` lines, mixed batches, and range filtering. `idmap_script_db_init` logs `ctx->script` before it is assigned, so debug output can be misleading or null. Running many IDs spawns many subprocesses concurrently in the temporary tevent loop, which needs load/error tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_script.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_tdb.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_tdb.c

## Purpose
This backend stores writable idmap mappings in the local `winbindd_idmap.tdb` state database. It also upgrades old database formats and initializes UID/GID high-water marks.

## Important APIs, Types, And Functions
Important helpers are `convert_fn`, `idmap_tdb_upgrade`, `idmap_tdb_init_hwm`, `idmap_tdb_open_db`, and `idmap_tdb_db_init`. It configures an `idmap_tdb_common_context` and delegates mapping/allocation to `idmap_tdb_common_*`. `idmap_tdb_init` registers the backend under `tdb`.

## Control Flow
Initialization creates a common context, allocates `idmap_rw_ops`, sets `max_id` and HWM key names, installs common allocation/storage callbacks, stores context in `dom->private_data`, and opens the database. Opening uses `state_path("winbindd_idmap.tdb")`, creates the DB if needed, checks `IDMAP_VERSION`, and runs upgrade in a transaction when needed. Upgrade handles byte-reversed versions, normalizes high-water marks, traverses old `DOMAIN/rid` keys, converts them to SID string keys, updates reverse mappings, deletes old records, and stores version 2. HWM init ensures user/group marks are at least `dom->low_id`.

## State And Persistence
Persistent records include `IDMAP_VERSION`, `USER HWM`, `GROUP HWM`, and bidirectional `SID <-> UID/GID` strings written by `idmap_tdb_common`. The database is local state, not clustered.

## Dependencies And Integration
It uses dbwrap open/transaction/traverse APIs, TDB helpers, domain lookup during upgrade, SID helpers, and common idmap allocation code. It integrates with the Samba idmap registry and default-domain allocator rules in `idmap_tdb_common_get_new_id`.

## Risks And Test Signals
Test new DB creation, HWM initialization below/above low_id, version upgrade, byte-swapped HWM records, old `DOMAIN/rid` conversion, missing domain deletion, reverse mapping replacement, transaction cancel/commit failures, and allocation at high_id. Upgrade mutates keys in traversal and depends on old key string null-termination and slash parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_tdb2.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_tdb2.c

## Purpose
This backend is a TDB-backed idmap variant intended for clustered Samba setups. It stores mappings in `idmap2.tdb` under the private directory and can optionally consult an external script to populate missing mappings.

## Important APIs, Types, And Functions
`struct idmap_tdb2_context` stores the optional script path. Helpers include `idmap_tdb2_init_hwm`, `idmap_tdb2_open_db`, `idmap_tdb2_set_mapping`, `idmap_tdb2_script`, `idmap_tdb2_id_to_sid`, `idmap_tdb2_sid_to_id`, and `idmap_tdb2_db_init`. It uses `idmap_tdb_common_context` for common batch lookup/allocation.

## Control Flow
Initialization creates common and backend-specific contexts, reads `script` config with deprecated fallback for `idmap:script`, copies the script path for reload safety, installs custom single-lookup hooks and RW ops, opens `lp_private_dir()/idmap2.tdb`, and initializes HWM records. Lookups first try dbwrap records. Missing records call the script when configured, parse `UID:`, `GID:`, or `SID:` output, range-filter returned IDs, and store bidirectional records in a transaction. Allocation uses common HWM logic and can create mappings through `idmap_rw_new_mapping`.

## State And Persistence
State is persisted in `idmap2.tdb` with `USER HWM`, `GROUP HWM`, and bidirectional string records. Optional script-derived results are cached into the TDB. Unlike `idmap_tdb.c`, this file does not contain old-format upgrade logic.

## Dependencies And Integration
It depends on dbwrap, TDB helpers, idmap common code, config APIs, optional shell script execution with `popen`, and Samba SID parsing. It registers under `tdb2`.

## Risks And Test Signals
Test DB path configuration, HWM creation, script fallback, malformed script output, script IDs outside range, collision handling, missing script behavior, and concurrent store attempts. The script command is assembled as a shell string and executed with `popen`, so quoting/injection behavior and whitespace in script paths or arguments deserve specific tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_tdb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_tdb_common.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_tdb_common.c

## Purpose
This file provides shared allocation, storage, and lookup logic for TDB-like idmap backends. It supports high-water-mark allocation, bidirectional SID/UID/GID records, batch status aggregation, and optional allocation of missing SID mappings.

## Important APIs, Types, And Functions
Exported functions include `idmap_tdb_common_get_new_id`, `idmap_tdb_common_set_mapping`, `idmap_tdb_common_new_mapping`, `idmap_tdb_common_unixids_to_sids`, `idmap_tdb_common_unixid_to_sid`, `idmap_tdb_common_sid_to_unixid`, and `idmap_tdb_common_sids_to_unixids`. It expects `struct idmap_tdb_common_context` in `dom->private_data`.

## Control Flow
Allocation validates default domain `*`, selects UID or GID HWM key, and runs `idmap_tdb_common_allocate_id_action` in a dbwrap transaction. The action fetches HWM, range-checks, atomically increments, rechecks, and returns the allocated previous value. Mapping storage builds `SID` and `UID <id>` or `GID <id>` keys, checks for existing SID mapping, inserts both directions, and removes the first record if the reverse insert fails. Batch Unix-ID lookup initializes statuses, delegates each item to a hook or default function, and returns all/some/none status. Batch SID lookup first reads records, then if some are unmapped and the domain is writable, reruns inside a transaction with allocation enabled.

## State And Persistence
Persistent state is backend-provided dbwrap storage. Record values are null-terminated strings. HWM records are uint32. The code enforces id range filters on lookup and HWM high bounds on allocation.

## Dependencies And Integration
It depends on dbwrap, TDB string helpers, `idmap_rw_new_mapping`, SID helpers, and backend-specific context initialization by `idmap_tdb.c`, `idmap_tdb2.c`, and autorid code.

## Risks And Test Signals
Test allocation boundaries, invalid ID types, non-default allocation refusal, null map/SID, duplicate SID collisions, reverse insert failure cleanup, invalid/non-null-terminated DB values, malformed `UID`/`GID` records, range filters, `ID_REQUIRE_TYPE`, and writable versus read-only behavior. The allocation sequence can consume an HWM value before later storage fails; callers rely on transaction wrapping where available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_tdb_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_tdb_common.h -->
# sources/user-network-fs/samba/source3/winbindd/idmap_tdb_common.h

## Purpose
This header defines the context contract and function prototypes for TDB-style idmap backends that reuse common allocation and lookup code.

## Important APIs, Types, And Functions
`struct idmap_tdb_common_context` contains a `db_context`, `idmap_rw_ops`, `max_id`, UID/GID HWM key strings, optional single-lookup function hooks, and backend `private_data`. It declares all common allocation, storage, and lookup functions implemented in `idmap_tdb_common.c`.

## Control Flow
No executable flow exists here. The comments define how backends install the context in `idmap_domain->private_data`, when hooks are used, and what record shapes are stored.

## State And Persistence
The context points to persistent dbwrap storage and names the HWM records. `private_data` lets backends attach script/config state while still using common logic.

## Dependencies And Integration
It includes `idmap.h` and `dbwrap/dbwrap.h`. Backends must initialize the db pointer, HWM keys, max ID, and RW callbacks before invoking common functions.

## Risks And Test Signals
Build tests should catch mismatched hook signatures. Backend tests should verify each context is fully initialized, especially `rw_ops`, HWM keys, and `max_id`; null fields lead to aborts or invalid db operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_tdb_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_util.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_util.c

## Purpose
This file provides small utility helpers shared by idmap backends: range checking, locating maps in arrays, fetching idmap secrets, and allocating `struct id_map **` arrays with embedded SID storage.

## Important APIs, Types, And Functions
Exports are `idmap_unix_id_is_in_range`, `idmap_find_map_by_id`, `idmap_find_map_by_sid`, `idmap_fetch_secret`, and `id_map_ptrs_init`.

## Control Flow
Range checking treats zero low/high bounds as unbounded. Map lookup by ID scans to NULL termination. Map lookup by SID scans up to `IDMAP_LDAP_MAX_IDS` or NULL, whichever comes first. Secret fetching builds `IDMAP_<backend>_<domain>`, uppercases it, and calls `secrets_fetch_generic` with the supplied identity. `id_map_ptrs_init` allocates an array of pointers, a parallel array of maps, and a parallel array of zeroed SIDs, then wires each map to one SID and NULL-terminates the pointer list.

## State And Persistence
This file itself has no persistent state. `idmap_fetch_secret` reads Samba secrets storage.

## Dependencies And Integration
It depends on idmap types, SID equality, Samba secrets, and `IDMAP_LDAP_MAX_IDS`. LDAP and RFC2307 backends use the lookup helpers for batch result reconciliation.

## Risks And Test Signals
Test low/high zero semantics, boundary IDs, duplicate IDs/SIDs in arrays, arrays longer than `IDMAP_LDAP_MAX_IDS`, secret key case normalization, failed uppercase conversion, and allocation cleanup in `id_map_ptrs_init`. The SID lookup helper's fixed maximum is appropriate for LDAP batches but surprising for generic callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/nss_info.c -->
# sources/user-network-fs/samba/source3/winbindd/nss_info.c

## Purpose
This file implements the NSS-info plugin registry and domain-to-backend dispatch layer. NSS-info backends normalize account aliases for winbind/idmap integrations.

## Important APIs, Types, And Functions
Global registries are `backends`, `default_backend`, and `nss_domain_list`. Public functions are `smb_register_idmap_nss`, `nss_map_to_alias`, `nss_map_from_alias`, and `nss_close`. Internal helpers include `nss_get_backend`, `parse_nss_parm`, `nss_domain_list_add_domain`, `nss_init`, and `find_nss_domain`.

## Control Flow
Backends register by interface version and unique name. `nss_init` lazily ensures the `template` backend is registered, parses `lp_winbind_nss_info()` entries as `backend[:domain]`, probes missing modules, records the first domainless backend as default, initializes domain entries, and marks the system initialized. `find_nss_domain` initializes on demand, searches for a configured domain, or creates a new domain entry using the default backend. Mapping calls dispatch through the selected backend's `map_to_alias` or `map_from_alias`. `nss_close` walks configured domains, calls each backend close function, and frees entries.

## State And Persistence
State is process-global and memory-only. Once `nss_initialized` is true, subsequent config changes are not reparsed by this file. Backend-specific state hangs off `struct nss_domain_entry`.

## Dependencies And Integration
It depends on `nss_info.h`, Samba module probing, static init, configuration (`lp_winbind_nss_info`), DLIST macros, and talloc allocation. Hash and template NSS-info backends register through this API.

## Risks And Test Signals
Test version mismatch, duplicate backend registration, invalid config strings, missing modules, default backend behavior, per-domain init failures and retry, map dispatch, and `nss_close`. The global one-time init means reload behavior needs attention; after close, `nss_initialized` is not reset in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/nss_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/nss_info_template.c -->
# sources/user-network-fs/samba/source3/winbindd/nss_info_template.c

## Purpose
This is the built-in fallback NSS-info backend. It registers the `template` backend and returns `NT_STATUS_NOT_IMPLEMENTED` for alias mapping operations.

## Important APIs, Types, And Functions
`nss_template_init` and `nss_template_close` return OK. `nss_template_map_to_alias` and `nss_template_map_from_alias` return not implemented. `nss_info_template_init` registers `nss_template_methods`.

## Control Flow
The backend performs no transformation. Registration is invoked when the NSS-info registry needs the template backend and it has not yet been registered.

## State And Persistence
No state or persistence is used.

## Dependencies And Integration
It depends on `nss_info.h` and `smb_register_idmap_nss`. It provides a safe static module for the NSS-info registry's default/fallback path.

## Risks And Test Signals
Test successful registration, duplicate registration behavior through the registry, and callers that handle `NT_STATUS_NOT_IMPLEMENTED` from alias mapping. This backend is intentionally inert.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/nss_info_template.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_alias_members.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_alias_members.c

## Purpose
This async helper retrieves members of an alias SID through winbind child RPC, with a cached usergroups fast path and a max-nesting guard.

## Important APIs, Types, And Functions
`struct wb_alias_members_state` stores the event context, target SID, and resulting `wbint_SidArray`. Public APIs are `wb_alias_members_send` and `wb_alias_members_recv`; callback `wb_alias_members_done` completes the child RPC.

## Control Flow
The send function validates `max_nesting`; at zero or below it returns an empty SID array immediately. It copies the SID, tries `lookup_usergroups_cached`, then locates the domain with `find_domain_from_sid_noinit`. If found, it calls `dcerpc_wbint_LookupAliasMembers_send` against the domain child handle. The callback combines transport/result status and completes. The recv function moves the SID array to the caller and logs results.

## State And Persistence
State is request-local. Cached membership can come from winbind cache through `lookup_usergroups_cached`; otherwise state is remote child RPC output.

## Dependencies And Integration
It integrates with tevent, generated winbind RPC stubs, domain lookup, child binding handles, SID helpers, and debug logging. `wb_getgrsid.c` uses it for alias group member expansion.

## Risks And Test Signals
Test max nesting zero, cache hit, unknown domain, child RPC transport failure, child result failure, empty alias, and memory ownership of returned SIDs. Cached usergroup semantics should match direct alias lookup or callers can observe inconsistent expansion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_alias_members.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_dsgetdcname.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_dsgetdcname.c

## Purpose
This async helper locates a domain controller through winbind child RPC and provides one-hour gencache helpers for `netr_DsRGetDCNameInfo` results.

## Important APIs, Types, And Functions
`wb_dsgetdcname_send` and `wb_dsgetdcname_recv` wrap `dcerpc_wbint_DsGetDcName`. Cache functions are `wb_dsgetdcname_gencache_set` and `wb_dsgetdcname_gencache_get`. `dcinfo_parser` deserializes cached NDR blobs.

## Control Flow
The send path rejects `BUILTIN` and, on non-AD-DC local SAM domains, returns domain-controller-not-found to avoid loopback connects. DC processes use the locator child and may replace a NetBIOS domain with DNS alt name for AD trusts. Non-DC processes delegate to the own-domain child. The optional GUID is copied to work around const generated-code signatures. Cache set serializes dcinfo to an NDR blob under uppercase `DCINFO/<domain>` and stores it for 3600 seconds. Cache get parses the same key, ignores expired entries, deserializes, and returns not-found when absent.

## State And Persistence
Request state is tevent-local. Cached DC info persists in Samba gencache for one hour.

## Dependencies And Integration
It depends on winbind domain role helpers, locator/domain child handles, generated RPC stubs, Netlogon NDR types, and gencache. It is part of winbind DC locator behavior.

## Risks And Test Signals
Test BUILTIN rejection, local SAM on non-AD-DC, AD DC trust name replacement, GUID and no-GUID calls, RPC status/result failures, cache expiry, NDR serialization failures, and corrupted cache blobs. Role-specific behavior is important because the selected child handle changes with `IS_DC` and `IS_AD_DC`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_dsgetdcname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_getgrsid.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_getgrsid.c

## Purpose
This async helper builds a `getgr*`-style group result from a group SID: it resolves the SID name/type, maps it to a GID, and expands group or alias members into an in-memory db.

## Important APIs, Types, And Functions
`struct wb_getgrsid_state` stores SID, nesting, resolved domain/name/type, GID, member db, and intermediate SID arrays. Public APIs are `wb_getgrsid_send` and `wb_getgrsid_recv`. Callback chain includes lookup SID, SID-to-GID, group member expansion, alias member expansion, alias member name lookup, and nested group merge.

## Control Flow
The send function rejects unmapped Unix group SIDs, then calls `wb_lookupsid_send`. The lookup callback accepts domain groups, aliases, well-known groups, and user/computer SIDs that may map to `ID_TYPE_BOTH`, then calls `wb_sids2xids_send`. The GID callback requires GID or BOTH. User/computer with BOTH is represented as a synthetic group containing only itself. Aliases call `wb_alias_members_send`, then `wb_lookupsids_send` to classify direct members; user/computer direct members are added to an RBT db and domain groups are expanded with `wb_group_members_send`. Domain groups call `wb_group_members_send` directly. Well-known groups produce an empty member db.

## State And Persistence
State is request-local. Members are collected in a `dbwrap_rbt` in-memory database keyed by linearized SID, with string names as values. No durable state is written.

## Dependencies And Integration
It depends on `wb_lookupsid`, `wb_sids2xids`, `wb_alias_members`, `wb_lookupsids`, `wb_group_members`, idmap child setup elsewhere, SID helpers, and dbwrap RBT. It is used by winbind group enumeration and getgrgid/getgrnam flows.

## Risks And Test Signals
Test Unix group SID rejection, SID types, ID_TYPE_BOTH synthetic user group handling, alias direct users, alias nested groups, depth decrement behavior, merge of direct alias members with nested group members, well-known empty groups, and child RPC failures. The alias path builds temporary arrays on `talloc_tos`; ownership and cleanup should be watched under nested expansion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_getgrsid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_getpwsid.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_getpwsid.c

## Purpose
This async helper fills a `struct winbindd_pw` passwd-style record for a user SID. It queries user information, normalizes mapped names through the idmap child, and applies Samba substitution rules to home directory and shell.

## Important APIs, Types, And Functions
`struct wb_getpwsid_state` stores SID, userinfo, output `winbindd_pw`, and normalized name. Public APIs are `wb_getpwsid_send` and `wb_getpwsid_recv`. Callbacks are `wb_getpwsid_queryuser_done` and `wb_getpwsid_normalize_done`.

## Control Flow
The send function rejects unmapped Unix user SIDs and calls `wb_queryuser_send`. The query callback lowercases the account name, then sends `dcerpc_wbint_NormalizeNameMap` to the idmap child. The normalize callback accepts OK and `NT_STATUS_FILE_RENAMED` as mapped-name results, builds a domain-qualified output username, copies UID/GID/full name, substitutes variables in homedir and shell with `talloc_sub_specified`, sets password to `*`, and completes.

## State And Persistence
Only request-local state is used. Normalization may depend on idmap child/backend config, but this helper writes no persistent data.

## Dependencies And Integration
It depends on `wb_queryuser`, generated winbind RPC stubs, idmap child handle, username formatting, string wrappers, and substitution helpers. It feeds winbind NSS passwd responses.

## Risks And Test Signals
Test Unix user SID rejection, queryuser failures, lowercase normalization, name-map OK/renamed/failure results, long field truncation in fixed-size passwd buffers, null full name, homedir/shell substitution, and memory ownership of moved strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_getpwsid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_gettoken.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_gettoken.c

## Purpose
This async helper builds an access-token SID list for a user: user SID, primary group SID, domain groups, optional local aliases, and builtin aliases.

## Important APIs, Types, And Functions
`struct wb_gettoken_state` stores event context, user SID, `expand_local_aliases`, and the growing SID array. Public APIs are `wb_gettoken_send` and `wb_gettoken_recv`. `wb_add_rids_to_sids` composes alias RIDs into domain SIDs and adds them uniquely.

## Control Flow
The send function queries user info. The first callback seeds the SID array with user and primary group SIDs and calls `wb_lookupusergroups_send`. Group lookup failures are tolerated by completing with the seed SIDs. Successful groups are added uniquely. If local alias expansion is disabled, the request completes. Otherwise it queries aliases in the local SAM domain, adds resulting RIDs as SIDs, then queries builtin aliases and adds those RIDs before completing.

## State And Persistence
State is request-local. The SID array grows through talloc reallocation by `add_sid_to_array_unique`; no durable state is written.

## Dependencies And Integration
It depends on `wb_queryuser`, `wb_lookupusergroups`, `wb_lookupuseraliases`, local SAM SID helpers, builtin SID, and uniqueness helpers. It feeds auth/token construction paths.

## Risks And Test Signals
Test queryuser failure, lookupusergroups failure tolerance, duplicate group/alias SIDs, local alias expansion disabled/enabled, missing local or builtin domains, alias lookup failures, and large SID arrays. The local group step uses `find_domain_from_sid_noinit(get_global_sam_sid())`; startup/domain-list timing can affect behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_gettoken.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_group_members.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_group_members.c

## Purpose
This file implements async recursive group-member expansion. It has three layers: single group lookup, serial lookup over a list of groups, and recursive expansion into unique user/computer members.

## Important APIs, Types, And Functions
Internal APIs are `wb_lookupgroupmem_send/recv` and `wb_groups_members_send/recv`. Public APIs are `wb_group_members_send`, `wb_group_members_recv`, and `add_member_to_db`. Request state structs track current groups, depth, all members, and an RBT database of users.

## Control Flow
Single-group lookup finds the owning domain by SID and calls `dcerpc_wbint_LookupGroupMembers`. List lookup serially walks groups, tolerating `NT_STATUS_TRUSTED_DOMAIN_FAILURE` by treating that group as empty, and appends returned principals. Recursive expansion opens an in-memory RBT db, seeds initial groups, decrements depth per expansion round, looks up all current groups, stores user/computer principals in the db keyed by binary SID, and saves group/alias/well-known principals for the next round. It completes when depth is exhausted or no groups remain.

## State And Persistence
All state is request-local. The member db is an in-memory `dbwrap_rbt` object, not durable. Duplicate users collapse through db key replacement/insert semantics in `add_member_to_db`.

## Dependencies And Integration
It uses generated winbind child RPC stubs, domain lookup, SID NDR sizing/linearization, dbwrap RBT, and tevent. `wb_getgrsid.c` uses it for group member expansion.

## Risks And Test Signals
Test unknown group domain, child RPC failures, trusted-domain failure tolerance, empty groups, nested groups, depth zero, duplicate users, computer members, large expansion, and replacement behavior in the RBT db. Recursion is breadth-like by rounds; cyclic group nesting relies on depth limits and duplicate user db, not a visited-group set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_group_members.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupname.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_lookupname.c

## Purpose
This async helper resolves a domain/name pair to a SID and LSA SID type through the appropriate winbind child domain.

## Important APIs, Types, And Functions
`struct wb_lookupname_state` stores event context, uppercased domain/name, flags, result SID, and result type. Public APIs are `wb_lookupname_send` and `wb_lookupname_recv`.

## Control Flow
The send function uppercases domain and name for cache friendliness, finds a lookup domain from the namespace, and sends `dcerpc_wbint_LookupName` to that child. The callback combines transport and result status and completes. The recv function copies the SID and type to caller-owned outputs.

## State And Persistence
State is request-local. Lookup results may depend on winbind child caches but this file writes no state.

## Dependencies And Integration
It depends on domain lookup by namespace, child handles, generated winbind RPC stubs, SID helpers, and tevent. It is used by higher-level winbind NSS and idmap flows.

## Risks And Test Signals
Test unknown namespace, allocation failures during uppercase copies, names with locale-sensitive characters, RPC status/result failures, and flags propagation. Uppercasing both domain and name can affect case-sensitive backends; cache behavior should be tested with mixed-case input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupsid.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_lookupsid.c

## Purpose
This async helper resolves a SID to domain name, account name, and LSA SID type through the appropriate winbind child domain.

## Important APIs, Types, And Functions
`struct wb_lookupsid_state` stores event context, target SID, result type, domain name, and name. Public APIs are `wb_lookupsid_send` and `wb_lookupsid_recv`.

## Control Flow
The send function copies the SID, finds the lookup domain by SID, and sends `dcerpc_wbint_LookupSid` to that child. The callback handles transport/result status. The recv function moves domain/name strings to the caller and returns the SID type.

## State And Persistence
State is request-local. The child may consult caches or domain controllers; this file does not persist data.

## Dependencies And Integration
It depends on SID-to-domain lookup, child binding handles, generated winbind RPC stubs, tevent, and debug logging. It is a building block for passwd/group and idmap flows.

## Risks And Test Signals
Test unknown SID domain, child RPC failures, name/domain ownership transfer, builtin/well-known SIDs, and result type propagation. Callers often branch heavily on SID type, so fixture coverage should include users, computers, domain groups, aliases, and well-known groups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupsid.c -->
