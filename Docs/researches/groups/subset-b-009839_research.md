# subset-b-009839 research

Grouped research report for Samba passdb LDAP and NDS backend files under `sources/user-network-fs/samba/source3/passdb`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_ldap.c

Purpose: implements Samba's `ldapsam` passdb backend, mapping the passdb method table onto LDAP objects that store users, groups, aliases, account policies, domain metadata, RID allocation state, and trusted-domain secrets. It explicitly targets Samba LDAP schema objects such as `sambaSamAccount`, `sambaGroupMapping`, `sambaDomain`, `sambaSidEntry`, and POSIX account/group classes, and the file notes that it is not an Active Directory password backend because AD does not expose the LM/NT password fields expected by this path.

Important APIs/types/functions: the backend private state is `struct ldapsam_privates`, shared with NDS code through `pdb_ldap.h`. Public entry points are `priv2ld`, `get_userattr_list`, `ldapsam_search_suffix_by_name`, `pdb_ldapsam_init_common`, and `pdb_ldapsam_init`. Core internal helpers include `get_userattr_key2string`, `get_objclass_filter`, `ldapsam_get_seq_num`, `ldapsam_search_suffix_by_sid`, `ldapsam_delete_entry`, `ldapsam_get_entry_timestamp`, `init_sam_from_ldap`, `init_ldap_from_sam`, and `ldapsam_modify_entry`. The method table is populated with user CRUD (`getsampwnam`, `getsampwsid`, add/update/delete/rename), group mapping CRUD and enumeration, alias membership operations, account policy getters/setters, RID allocation, SID/name lookup, trusted-domain password storage, paged display searches, and optional trusted/editposix Unix account management.

Control flow: initialization starts in `pdb_ldapsam_init`, registers `ldapsam`, then lets `pdb_nds_init` register the NDS variant. `pdb_ldapsam_init_common` trims the URI, calls `pdb_init_ldapsam_common` to allocate the passdb method table, fetch LDAP bind credentials from secrets, initialize `smbldap_state`, install common user/group/account-policy functions, and allocate private data. It then installs alias/search/trusted/editposix callbacks, fixes `schema_ver` to `SCHEMAVER_SAMBASAMACCOUNT`, searches or creates the domain info object through `smbldap_search_domain_info`, records `domain_dn`, synchronizes the domain SID from LDAP into secrets if needed, and rejects mismatched algorithmic RID base values.

User lookup control flow builds escaped filters by uid or SID, fetches LDAP attributes from the schema map plus `modifyTimestamp` and Unix attributes, enforces a single result, and calls `init_sam_from_ldap`. That decoder reads identity, SID, password timestamps, display/home/script/profile fields, account flags, LM/NT hashes, password history, bad-password metadata, logon hours, optional Unix passwd data for trusted mode, and the login-cache overlay. For NDS LDAP it can fetch a clear text password through `pdb_nds_get_password` and derive LM/NT hashes locally. Update and add paths use `init_ldap_from_sam` to build LDAP mods only for set or changed passdb elements, then `ldapsam_modify_entry` performs a password extended operation when plaintext password sync is enabled and applies add or modify operations to LDAP.

Group and alias control flow is split between `sambaGroupMapping` lookup helpers and POSIX membership operations. `init_group_from_ldap` maps `gidNumber`, `sambaSID`, `sambaGroupType`, display name, and description into `GROUP_MAP`. Group enumeration stores LDAP result iteration state in `ldapsam_privates`. `ldapsam_enum_group_members` combines `memberUid` lookups with primary `gidNumber` membership. `ldapsam_enum_group_memberships` returns primary group first, then secondary groups from POSIX groups. Alias membership is represented with `sambaSIDList`; add/delete modify that multivalue attribute, enumeration parses each stored SID, and reverse membership searches group mappings by `sambaSIDList`, with a small result cache for repeated builtin queries.

State and persistence behavior: all durable passdb state lives in LDAP entries below configured suffixes. Domain state is stored in a `sambaDomain` object, including `sambaSID`, `sambaNextRid`, legacy next user/group RID attributes, `sambaAlgorithmicRidBase`, and account policy attributes. RID allocation reads the largest legacy/current next-RID value, increments it, and writes `sambaNextRid`; callers retry up to ten times on modify failure as a race signal. Account policies are cached in local TDB after LDAP reads/writes. Login failure counters use LDAP for lockout reset/autolock boundaries but may be overlaid through Samba's login cache when LDAP timestamps are older than local cached failure state. Trusted-domain passwords are LDAP child objects under `domain_dn` and include current/previous clear text password, SID, and last-set time.

Dependencies/integration: this file depends heavily on Samba passdb abstractions (`struct pdb_methods`, `struct samu`, `GROUP_MAP`, account policy helpers), `smbldap` connection/search/modification wrappers, OpenLDAP/lber APIs, talloc ownership conventions, SID utilities, secrets.tdb, winbind allocation/mapping helpers, idmap cache, login cache, loadparm configuration, and optional NDS helpers from `pdb_nds.c`. It integrates with external admin scripts for rename-user behavior, with paged LDAP search controls for display enumeration, and with POSIX NSS-style account/group entries when `ldapsam:trusted` and `ldapsam:editposix` are enabled.

Risks and edge cases: this is security-sensitive code that handles password hashes, optional clear text passwords, bind credentials, trusted-domain secrets, account lockout state, and LDAP filters. Most lookup filters use escaping, but `get_ldap_filter` computes an escaped username and then substitutes the unescaped username; current use passes `"*"` for display enumeration, but reuse would be risky. LDAP updates are not transactional across multi-step user/group membership changes, RID allocation uses optimistic retry rather than compare-and-swap semantics, and duplicate LDAP entries usually turn into `NO_SUCH_*` or corruption-style failures. Deleting a Samba object can either delete the full DN or only objectClass/attributes depending on `lp_ldap_delete_dn`, so schema and RDN choices affect cleanup. NDS password retrieval intentionally handles clear text passwords and must zero temporary buffers correctly. Many code paths rely on exact schema attributes and configured suffixes, so misconfigured LDAP suffixes or object classes produce hard-to-debug runtime failures.

Test signals: meaningful tests should cover ldapsam initialization with existing and missing `sambaDomain`, duplicate user/SID/group entries, add/update/delete of users with and without existing POSIX entries, password sync modes including LDAP extended operation unsupported and constraint violation paths, RID allocation races, account policy cache fallback, group mapping add/update/delete, primary and secondary group membership enumeration, alias membership forward/reverse lookup, paged display search fallback, trusted-domain password CRUD, `ldapsam:trusted` SID/id mapping, and `ldapsam:editposix` create/delete user/group flows. Integration tests need a real or fixture LDAP server with Samba schema and should verify both LDAP contents and passdb-facing NTSTATUS results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap.h -->
# sources/user-network-fs/samba/source3/passdb/pdb_ldap.h

Purpose: declares the shared LDAP passdb private state and the small set of cross-file entry points exported by `pdb_ldap.c` to the wider passdb registration layer and to the NDS LDAP variant.

Important APIs/types/functions: `struct ldapsam_privates` holds `smbldap_state`, enumeration result/current entry/index state, domain name/SID, schema version, cached domain DN, NDS flag, LDAP server location, and a one-entry search cache for alias membership lookups. Function declarations expose `get_userattr_list`, `pdb_ldapsam_init_common`, `pdb_ldapsam_init`, `ldapsam_search_suffix_by_name`, and `priv2ld`. The header forward-uses LDAP types through included compilation context rather than declaring them itself.

Control flow: `pdb_ldap.c` allocates and owns `ldapsam_privates` during backend initialization. `pdb_nds.c` reuses the same private-data struct after calling `pdb_ldapsam_init_common`, then marks `is_nds_ldap`, stores `location`, and overrides selected callbacks. Search and enumeration methods mutate `result`, `entry`, and `index` fields; alias membership reverse search may populate `search_cache`.

State and persistence behavior: the header does not persist data directly, but its struct fields are the in-memory bridge to persistent LDAP state. `domain_dn` and `location` are heap strings freed by backend cleanup, `smbldap_state` owns the live LDAP connection, and `result`/`entry` point at LDAP message lifetimes that must be freed or transferred carefully.

Dependencies/integration: this header is coupled to Samba's `smbldap_state`, `dom_sid`, OpenLDAP `LDAPMessage`/`LDAP`, talloc allocation, passdb module registration, and the schema version constants from `pdb_ldap_schema.h`. It is the explicit ABI between base ldapsam and NDS ldapsam code.

Risks and test signals: duplicated declaration of `get_userattr_list` is harmless but noisy. The main risk is lifetime misuse of LDAP messages or cached search results stored in the private struct. Tests that iterate users/groups, interrupt paged searches, unload the backend, and exercise NDS initialization should reveal stale result or cleanup bugs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap_schema.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_ldap_schema.c

Purpose: provides the LDAP schema attribute maps used by ldapsam to convert logical passdb fields into concrete LDAP attribute names for users, domain info, group mappings, id pools, SID maps, and trusted password objects.

Important APIs/types/functions: exported tables include `attrib_map_v30`, `attrib_map_to_delete_v30`, `dominfo_attr_list`, `groupmap_attr_list`, `groupmap_attr_list_to_delete`, `idpool_attr_list`, and `sidmap_attr_list`. `get_attr_key2string` performs integer-key lookup in an `ATTRIB_MAP_ENTRY` array. `get_attr_list` allocates a NULL-terminated talloc array of attribute names for LDAP search requests.

Control flow: callers pass one of the mapping arrays and either request a single attribute name by key or a whole search attribute list. Tables are terminated by `LDAP_ATTR_LIST_END`. User schema v30 maps `sambaSamAccount` fields such as `sambaSID`, `sambaNTPassword`, `sambaLMPassword`, `sambaAcctFlags`, password history, lockout counters, profile paths, and logon hours. Delete tables omit structural/POSIX fields so `ldapsam_delete_entry` can strip Samba-specific attributes without necessarily deleting the entire object.

State and persistence behavior: this file has only static mapping data; persistence effects occur in callers that use the returned names to read or write LDAP. The map contents define the durable LDAP attribute contract, so changes here are schema migrations in practice.

Dependencies/integration: depends on `pdb_ldap_schema.h` constants and Samba talloc/debug helpers. The maps are consumed throughout `pdb_ldap.c` and `pdb_ldap_util.c` for filters, add/modify lists, deletion lists, and account policy/domain metadata access.

Risks and test signals: incorrect attribute names silently break lookup, add, or deletion paths against live LDAP schemas. The delete-list tables are especially sensitive because including an RDN or shared idmap attribute can trigger LDAP naming/objectclass violations. Tests should verify generated search attribute lists, user add/update/delete against Samba schema, group mapping delete fallback behavior, and domain-info bootstrap.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap_schema.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap_schema.h -->
# sources/user-network-fs/samba/source3/passdb/pdb_ldap_schema.h

Purpose: defines Samba LDAP schema version constants, LDAP object class and common attribute names, integer attribute IDs, the `ATTRIB_MAP_ENTRY` structure, exported schema map arrays, and lookup helper prototypes.

Important APIs/types/functions: schema versions are `SCHEMAVER_SAMBAACCOUNT` and `SCHEMAVER_SAMBASAMACCOUNT`, with active code using the Samba 3.0 `sambaSamAccount` version. Object class constants cover account, group mapping, domain info, idmap/idpool, SID, trust password, trusted domain, POSIX account/group, and organizational unit classes. Attribute ID constants assign stable keys such as `LDAP_ATTR_UID`, `LDAP_ATTR_USER_SID`, `LDAP_ATTR_GROUP_TYPE`, `LDAP_ATTR_NEXT_RID`, `LDAP_ATTR_PWD_HISTORY`, and `LDAP_ATTR_LOGON_HOURS`. The public helpers are `get_attr_key2string` and `get_attr_list`.

Control flow: implementation files use integer IDs rather than hard-coded strings for most schema lookups. `pdb_ldap.c` wraps user-specific calls through schema-version dispatch, while domain/group/account-policy code accesses the exported maps directly.

State and persistence behavior: this header is declarative, but it defines the symbolic vocabulary for all LDAP persistence in this backend. The same constants are used to build filters, LDAP mods, and deletion requests, so a mismatch between constants and deployed LDAP schema affects runtime data layout.

Dependencies/integration: integrates with talloc through helper prototypes and with all LDAP passdb files through shared objectclass/attribute constants. It also bridges Samba passdb concepts, POSIX account/group objects, and idmap/trust object classes.

Risks and test signals: `LDAP_ATTR_USER_SID` and `LDAP_ATTR_USER_RID` intentionally share value 18 for old/new schema compatibility, which is easy to misread. Any new schema field requires coordinated table updates in `pdb_ldap_schema.c`. Compile tests catch missing declarations, but integration tests against an LDAP server are needed to catch wrong schema names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap_schema.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap_util.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_ldap_util.c

Purpose: contains domain-info bootstrap and lookup helpers for ldapsam. It searches for the `sambaDomain` object, creates it when requested, and initializes LDAP-backed account policy attributes with Samba defaults.

Important APIs/types/functions: private helpers are `add_new_domain_account_policies` and `add_new_domain_info`. The exported function is `smbldap_search_domain_info(struct smbldap_state *, LDAPMessage **, const char *domain_name, bool try_add)`.

Control flow: `smbldap_search_domain_info` escapes the domain name for an LDAP filter, searches under the configured suffix for exactly one `sambaDomain` object, and returns the LDAP result on success. If no entry exists and `try_add` is true, it calls `add_new_domain_info`, then `add_new_domain_account_policies`, and recursively searches again without adding. `add_new_domain_info` first checks for duplicate domain names, then builds an RDN-escaped DN, adds domain name, global SAM SID, algorithmic RID base, objectclass, and initial `sambaNextUserRid`. `add_new_domain_account_policies` iterates all account policy names, looks up default values, and writes each policy attribute as a replace mod on the domain DN.

State and persistence behavior: this file creates and mutates the LDAP `sambaDomain` object below `lp_ldap_suffix()`. It persists the domain SID from `get_global_sam_sid()`, the algorithmic RID base, legacy next-user RID seed, and account policy defaults. It allocates LDAP results for callers, who must free or talloc-autofree them.

Dependencies/integration: depends on `smbldap` search/add/modify wrappers, passdb account policy helpers, `lp_ldap_suffix`, schema maps from `pdb_ldap_schema.c`, SID formatting utilities, LDAP error APIs, and Samba memory helpers. `pdb_ldap.c` calls this during backend initialization and RID allocation.

Risks and test signals: duplicate `sambaDomain` entries are treated as fatal. Domain names are correctly escaped separately for filters and RDNs, which is important for special characters. Account policy initialization modifies one attribute at a time with a growing mod list, so failure partway through can leave a partially initialized domain object. Tests should cover no-entry creation, duplicate-entry rejection, special-character domain names, missing default policy retrieval, LDAP modify failures, and initialization idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap_util.h -->
# sources/user-network-fs/samba/source3/passdb/pdb_ldap_util.h

Purpose: declares the LDAP domain-info search/bootstrap helper used by ldapsam, behind `HAVE_LDAP`.

Important APIs/types/functions: the sole exported prototype is `smbldap_search_domain_info`, which accepts an `smbldap_state`, output `LDAPMessage **`, domain name, and `try_add` flag, returning an `NTSTATUS`.

Control flow: callers include this header when they need to resolve or create the `sambaDomain` LDAP entry. `pdb_ldap.c` uses it during initialization and RID allocation; `pdb_ldap_util.c` owns implementation details.

State and persistence behavior: the header has no state, but the function contract returns an LDAP message result that callers must manage and may create persistent LDAP domain metadata if `try_add` is true.

Dependencies/integration: guarded by `HAVE_LDAP`, and depends on Samba `NTSTATUS`, `smbldap_state`, and OpenLDAP `LDAPMessage` types from surrounding includes.

Risks and test signals: consumers must not assume the output result is valid on failure, and must free it on success. Build coverage should include both LDAP-enabled and LDAP-disabled configurations; runtime coverage should verify initialization behavior through `pdb_ldapsam_init_common`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_ldap_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_nds.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_nds.c

Purpose: implements the Novell eDirectory/NDS variant of Samba's LDAP passdb backend. It reuses the base ldapsam backend but adds NMAS LDAP extended operations for Universal/Simple password retrieval and setting, and overrides login-attempt accounting so eDirectory password policy state is updated by LDAP binds.

Important APIs/types/functions: NMAS OID constants identify get login config, set password, and get password request/response operations. BER helpers are `berEncodePasswordData`, `berEncodeLoginData`, and `berDecodeLoginData`. NMAS operation helpers are `getLoginConfig`, `nmasldap_get_simple_pwd`, `nmasldap_set_password`, and `nmasldap_get_password`. Exported functions are `pdb_nds_get_password`, `pdb_nds_set_password`, and `pdb_nds_init`. Backend integration helpers are `pdb_nds_update_login_attempts`, `pdb_init_NDS_ldapsam_common`, and `pdb_init_NDS_ldapsam`.

Control flow: password retrieval first calls `nmasldap_get_password` for Universal Password via the NMAS get-password extended operation, validates the response OID and NMAS version, decodes returned bytes, and null-terminates the password. If that fails, `pdb_nds_get_password` falls back to `nmasldap_get_simple_pwd`, which reads the tagged login config value `PASSWORD HASH` and only accepts digest tag 1, meaning clear text. Password setting attempts the NMAS Universal Password set operation, logs failures, and then replaces LDAP `userPassword` through normal `smbldap_modify`.

State and persistence behavior: the file reads and writes eDirectory password state, including clear text password material returned over LDAP extensions. `pdb_nds_update_login_attempts` opens a separate LDAP connection and performs a simple bind as the user. On successful Samba authentication it tries to bind with the real retrieved password; on failed authentication it binds with a generated bogus password so eDirectory increments failed login counters. It maps bind errors such as invalid credentials or unwilling-to-perform into NT status codes.

Dependencies/integration: depends on OpenLDAP/lber BER APIs, `ldap_extended_operation_s`, Samba `smbldap` connection helpers, password/debug/memory utilities, `pdb_ldap.h` shared private state, and base `pdb_ldapsam_init_common`. Base `pdb_ldap.c` calls `pdb_nds_get_password` and `pdb_nds_set_password` when `is_nds_ldap` is set, and registration exposes the backend as `NDS_ldapsam`.

Risks and edge cases: this code handles clear text passwords and logs optional debug password output under `DEBUG_PASSWORD`, so buffer zeroing and log configuration are critical. Several allocated buffers must be scrubbed before free, and response OIDs/version checks prevent mis-decoding unrelated extended operation replies. `pdb_nds_set_password` does not free `tmpmods` after `smbldap_modify`, which is a memory-lifetime concern unless hidden by process lifetime or wrapper behavior. Login-attempt updates reveal account-disabled status for some eDirectory errors because the server cannot distinguish password correctness from policy state in that path.

Test signals: tests need an eDirectory/NMAS-capable LDAP server or mocks for `ldap_extended_operation_s`. Useful cases include Universal Password success, fallback to Simple Password, non-cleartext simple password rejection, response OID mismatch, version mismatch, buffer-too-small handling, set-password fallback to `userPassword`, login-attempt success/failure binds, account-disabled mapping, and NDS backend registration after ldapsam initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_nds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_nds.h -->
# sources/user-network-fs/samba/source3/passdb/pdb_nds.h

Purpose: declares the NDS/eDirectory LDAP password helper API and backend registration entry point used by the base LDAP passdb code.

Important APIs/types/functions: it forward-declares `struct smbldap_state` and exposes `pdb_nds_get_password`, `pdb_nds_set_password`, and `pdb_nds_init`. The get function accepts an LDAP state, object DN, in/out password length, and output buffer. The set function accepts LDAP state, object DN, and clear text password. The init function registers `NDS_ldapsam`.

Control flow: `pdb_ldap.c` includes this header so `init_sam_from_ldap` can retrieve NDS passwords and `ldapsam_modify_entry` can set NDS passwords when the shared private state is marked as NDS. `pdb_ldapsam_init` also calls `pdb_nds_init` to register the alternate backend.

State and persistence behavior: this header has no state, but its functions read and write persistent eDirectory password state and may expose clear text password material to callers for hash generation.

Dependencies/integration: depends on Samba `NTSTATUS`, `TALLOC_CTX`, `smbldap_state`, and LDAP integer result conventions through surrounding includes. It is intentionally small so the base LDAP backend can call NDS-specific behavior without pulling implementation details into `pdb_ldap.c`.

Risks and test signals: callers must provide a correctly sized password buffer and must scrub sensitive output after use. Build tests should ensure the declarations remain consistent with `pdb_nds.c`; integration tests should verify NDS password retrieval/set behavior through the `NDS_ldapsam` backend rather than only through direct helper calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_nds.h -->
