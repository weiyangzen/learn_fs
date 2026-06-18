# Research: subset-b-009840

Grouped research for Samba passdb backends and helpers under `sources/user-network-fs/samba/source3/passdb`. Each source section is bounded by reconciliation markers so the guard can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_samba_dsdb.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_samba_dsdb.c

## Purpose
`pdb_samba_dsdb.c` implements the `samba_dsdb` and legacy alias `samba4` passdb backends. It adapts the source3 `struct pdb_methods` interface directly onto the Samba AD DSDB/SAM LDB database, so source3 passdb callers can read and mutate AD users, groups, aliases, SID/id mappings, account policies, and trusted-domain data without going through an LDAP server.

This backend is intended for AD DC-style deployments where `sam.ldb`, DSDB helper APIs, source4 authentication/session infrastructure, and idmap are available. It is not a full implementation of every historical passdb operation; several old mapping and rename hooks return `NT_STATUS_NOT_IMPLEMENTED`.

## Important APIs, Types, And Functions
The private state is `struct pdb_samba_dsdb_state`, which holds a tevent context, `struct ldb_context *ldb`, `struct idmap_context *idmap_ctx`, and source4 `loadparm_context`. `pdb_init_samba_dsdb()` allocates this state, creates source4 event/loadparm contexts, connects to `sam.ldb` or a supplied URL via `samdb_connect_url()`, initializes idmap, synchronizes domain SID/GUID into secrets, and installs the passdb method table. `pdb_samba_dsdb_init()` registers the backend as both `samba_dsdb` and `samba4`.

User lookup is centered on `pdb_samba_dsdb_getsamupriv()`, `pdb_samba_dsdb_getsampwfilter()`, `pdb_samba_dsdb_getsampwnam()`, and `pdb_samba_dsdb_getsampwsid()`. `pdb_samba_dsdb_init_sam_from_priv()` translates LDB attributes into `struct samu`: account name, timestamps, display/home/profile fields, user parameters, object SID, account flags, password hashes, and primary group SID. `pdb_samba_dsdb_replace_by_sam()` is the reverse translator for updates, building DSDB modify messages and using special controls for password hashes and password last-set behavior.

User lifecycle methods include `pdb_samba_dsdb_create_user()`, `pdb_samba_dsdb_delete_user()`, `pdb_samba_dsdb_add_sam_account()`, `pdb_samba_dsdb_update_sam_account()`, and `pdb_samba_dsdb_delete_sam_account()`. Group and alias methods include `pdb_samba_dsdb_getgrfilter()`, `getgrsid/getgrgid/getgrnam`, `create_dom_group`, `delete_dom_group`, `enum_group_members`, `enum_group_memberships`, `create_alias`, `delete_alias`, `add_aliasmem`, `del_aliasmem`, `enum_aliasmem`, and `enum_alias_memberships`.

SID/id mapping is delegated to source4 idmap through `pdb_samba_dsdb_id_to_sid()` and `pdb_samba_dsdb_sid_to_id()`. Search APIs are implemented by `pdb_samba_dsdb_search_filter()` and `search_users/search_groups/search_aliases`, which materialize `samr_displayentry` arrays from DSDB searches. Trust APIs are extensive: old passdb trust password functions (`get_trusteddom_pw`, `get_trusteddom_creds`, `set_trusteddom_pw`, `enum_trusteddoms`) and newer `pdb_trusted_domain` lifecycle functions (`get_trusted_domain`, `get_trusted_domain_by_sid`, `set_trusted_domain`, `del_trusted_domain`, `enum_trusted_domains`, `filter_hints`).

## Control Flow
Initialization builds a method table in `pdb_samba_dsdb_init_methods()`. The module then connects to DSDB as the system session, creates idmap state, and calls `pdb_samba_dsdb_init_secrets()` to ensure the source3 secrets database has protected copies of the AD domain SID and GUID. Failure during any step frees the method instance and prevents registration from producing a usable backend.

For reads, callers invoke passdb lookup by name or SID. The backend formats an LDAP-style filter, runs `dsdb_search_one()` under the default base DN with a fixed attribute set, and maps the returned LDB message into `struct samu`. The LDB message is attached as backend-private data on the `samu`, allowing later updates to use the original DN without another lookup.

For user creation with a populated `samu`, `pdb_samba_dsdb_add_sam_account()` starts an LDB transaction, calls `dsdb_add_user()` with selected account control bits and any caller-supplied SID, then applies all set/changed `samu` fields through `pdb_samba_dsdb_replace_by_sam()`. Normal updates call the same replacement helper with `pdb_element_is_changed`. Password updates take one of two paths: cleartext passwords are converted to UTF-16 and written as `clearTextPassword`; direct LM/NT hashes and history use DSDB bypass controls and delete related attributes to avoid inconsistent credentials.

Group and alias operations mostly translate passdb RIDs/SIDs into DSDB DNs of the form `<SID=...>`. Membership modifications create a modify message for the `member` attribute and map LDB duplicate/missing-value errors to membership NTSTATUS values. Group membership enumeration reads DSDB group members or tokenGroups and maps each SID to a GID via idmap; failures to map group SIDs are hard errors because missing deny-group mappings could weaken ACL evaluation.

Trust password retrieval searches a trustedDomain object, validates outbound trust direction and trust type, parses `trustAuthOutgoing` as `trustAuthInOutBlob`, then extracts either cleartext UTF-16 password material or NT OWF hashes into legacy strings or `cli_credentials`. Setting an outbound trust password is restricted to the PDC, increments the version element, moves current auth data to previous, writes a new cleartext auth entry plus version entry, and commits it in one transaction.

Full trusted-domain creation validates the target SID and names, ensures the DC is PDC, confirms no existing TDO, creates the `trustedDomain` object under the system container, stores trust auth blobs and metadata, and for inbound trusts also creates an interdomain trust user account with a DSDB control that permits the UAC. Deletion removes the TDO and, for inbound trusts, deletes the corresponding trust user only if it is actually an interdomain-trust account.

## State And Persistence
Persistent state lives primarily in AD DSDB/LDB: users, groups, aliases, memberships, passwords, password history, trustedDomain objects, trust auth blobs, interdomain trust user accounts, and sequence numbers. The backend also writes domain SID and GUID into source3 secrets with protection flags so source3 components can find local domain identity without linking to DSDB directly.

Runtime state consists of the passdb method instance, its private DSDB/idmap/loadparm/event contexts, backend-private LDB messages attached to `struct samu`, temporary talloc stack frames, and transaction state around multi-step mutations. Account policy reads and writes are delegated to the shared account policy backend, not stored directly by this file.

The backend advertises `PDB_CAP_STORE_RIDS`, `PDB_CAP_ADS`, and `PDB_CAP_TRUSTED_DOMAINS_EX`. `new_rid` deliberately returns false because RID allocation is owned by DSDB object creation, not by source3 passdb.

## Dependencies And Integration Points
This file integrates source3 passdb with source4 DSDB. It depends on `passdb.h`, `samdb.h`, LDB, DSDB common utilities, DSDB trust helpers, source4 event and auth session setup, source4 idmap, credentials, generated NDR types for security/DRS/LSA trust blobs, base64 helpers, LDAP NDR encoding, secrets helpers, and loadparm.

Important external APIs include `dsdb_add_user()`, `dsdb_add_domain_group()`, `dsdb_add_domain_alias()`, `dsdb_search_one()`, `dsdb_search()`, `dsdb_replace()`, `dsdb_enum_group_mem()`, `dsdb_expand_nested_groups()`, `dsdb_lookup_rids()`, `dsdb_trust_search_tdo*()`, `dsdb_trust_search_tdos()`, `dsdb_trust_local_tdo_info()`, `dsdb_trust_xref_forest_info()`, `idmap_sids_to_xids()`, `idmap_xids_to_sids()`, `samdb_result_*()`, `account_policy_get/set()`, and `cli_credentials_*()`.

The passdb interface is populated in `pdb_samba_dsdb_init_methods()`, making this file an adapter layer for smbd, net, rpc_server/samr, auth, and trust-management code paths that expect source3 passdb calls.

## Risks
Filter strings are built with formatted user/domain data in several places. Samba's LDB formatting helpers handle many cases, but malformed or unescaped names would be high-impact because these paths query privileged directory state. Password handling is sensitive: direct hash writes require DSDB bypass controls and delete supplemental credentials to avoid stale credential material; any missed flag can leave inconsistent password state.

Some passdb methods are intentionally unimplemented (`rename_sam_account`, login-attempt updates, group mapping entry mutation/enumeration, `lookup_names`, `set_unix_primary_group`, trust password deletion, and RID allocation). Callers must tolerate these gaps or use DSDB-native code paths. Membership enumeration treats idmap failures as access-critical errors, which is safer for ACLs but can break logons if idmap is misconfigured.

Trust code has high blast radius. It parses and rewrites opaque NDR blobs, enforces PDC-only updates in some but not all read paths, creates/deletes interdomain trust users, and must distinguish inbound/outbound and AD/MIT trust types correctly. `add_trust_user()` uses `taiob->count` while indexing `taiob->current.array`, so trust blob shape assumptions matter. Any change in DSDB trust schema or auth blob layout needs careful tests.

## Test Signals
Useful tests include AD DC passdb backend initialization against `sam.ldb`, user lookup by name/SID, create/update/delete of users with password hash and cleartext password changes, primary group changes, DSDB account-control mapping, search enumeration for users/groups/aliases, group and alias membership add/delete/enumeration, idmap failure behavior, account policy get/set, and sequence number retrieval.

Trust tests should cover outbound trust password retrieval as legacy password and `cli_credentials`, password rollover preserving previous auth data and version, PDC-only write rejection, invalid trust type/direction rejection, TDO create/delete including inbound trust user creation/removal, lookup by SID and name, forest trust filter hints, and malformed `trustAuthOutgoing` NDR blobs. Regression tests should also assert the documented `NT_STATUS_NOT_IMPLEMENTED` methods stay predictable to callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_samba_dsdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_secrets.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_secrets.c

## Purpose
`pdb_secrets.c` provides passdb-facing helpers around Samba's secrets database. Its main job is to enumerate trusted domains stored in `secrets.tdb` and expose a small set of wrapper functions so passdb modules can store/fetch domain SID and GUID data without directly linking against the lower-level secrets library.

## Important APIs, Types, And Functions
`struct list_trusted_domains_state` accumulates `struct trustdom_info` pointers and a count while traversing the secrets database. `list_trusted_domain()` is the dbwrap traversal callback: it filters keys with the `SECRETS_DOMTRUST_ACCT_PASS` prefix, parses values as NDR `TRUSTED_DOM_PASS`, validates domain SID shape, and appends a `trustdom_info` containing the trusted domain name and SID.

`secrets_trusted_domains()` initializes secrets, fetches the secrets db context, allocates the result array under the caller's talloc context, traverses the database, and returns the accumulated array and count. The `PDB_secrets_*` wrappers call the corresponding secrets functions for domain SID/GUID storage and protection flags: `PDB_secrets_store_domain_sid()`, `PDB_secrets_mark_domain_protected()`, `PDB_secrets_clear_domain_protection()`, `PDB_secrets_fetch_domain_sid()`, `PDB_secrets_store_domain_guid()`, and `PDB_secrets_fetch_domain_guid()`.

## Control Flow
Trusted-domain enumeration starts with `secrets_init()`. If secrets cannot be initialized, enumeration returns `NT_STATUS_ACCESS_DENIED`. The traversal callback ignores unrelated keys, attempts to NDR-decode trust password records, rejects decoded SIDs that do not look like account-domain SIDs, allocates `trustdom_info`, copies the Unicode trust name and SID, and expands the caller-owned array with `ADD_TO_ARRAY`.

Wrapper functions are simple pass-throughs and preserve the boolean semantics of the underlying secrets API.

## State And Persistence
Persistent state is in `secrets.tdb`, accessed through `secrets_db_ctx()` and dbwrap. This file does not define its own schema; it relies on `SECRETS_DOMTRUST_ACCT_PASS` key prefixes and generated NDR for `TRUSTED_DOM_PASS`. Enumerated results are transient talloc allocations owned by the caller.

The domain SID/GUID wrappers mutate or read secrets records and protection marks, which are later used by passdb backends such as `pdb_samba_dsdb.c` to keep source3-visible domain identity synchronized with DSDB.

## Dependencies And Integration Points
The file depends on passdb types, generated NDR for secrets records, `secrets.h`, dbwrap traversal APIs, security SID utilities, and TDB utility helpers. It is an integration shim between passdb modules and the secrets subsystem, especially for trusted-domain enumeration and local-domain identity storage.

## Risks
`list_trusted_domain()` returns `false` on NDR parse failure even though traversal callbacks conventionally use integer status; this is numerically zero and therefore continues traversal rather than stopping. That is likely intentional tolerance for bad records, but it can hide malformed trust entries. The callback validates only `num_auths == 4`, not all domain SID invariants. Allocation failure after `ADD_TO_ARRAY` is handled by resetting count and returning `-1`, but `secrets_trusted_domains()` does not inspect the traverse return in this file, so partial or failed enumeration can still return `NT_STATUS_OK`.

## Test Signals
Tests should create secrets records with valid and invalid `SECRETS_DOMTRUST_ACCT_PASS` values, unrelated keys, malformed NDR blobs, non-domain SIDs, and allocation-failure injection where possible. Wrapper tests should verify SID/GUID store/fetch and protection flag behavior through the public `PDB_secrets_*` functions rather than directly through secrets internals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_secrets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_secrets.h -->
# sources/user-network-fs/samba/source3/passdb/pdb_secrets.h

## Purpose
`pdb_secrets.h` is the public passdb header for the secrets helper implemented in `pdb_secrets.c`. It exposes trusted-domain enumeration from the secrets database to other passdb code.

## Important APIs, Types, And Functions
The header declares:

`NTSTATUS secrets_trusted_domains(TALLOC_CTX *mem_ctx, uint32_t *num_domains, struct trustdom_info ***domains);`

The caller supplies a talloc context and receives a count plus an array of `struct trustdom_info *` entries. The header relies on passdb/security declarations being included by users for `NTSTATUS`, `TALLOC_CTX`, and `struct trustdom_info`.

## Control Flow
There is no executable control flow. Include guards prevent duplicate inclusion. The declaration maps directly to the implementation that initializes secrets and traverses `secrets.tdb`.

## State And Persistence
The header has no state. It documents an API that reads persistent trust records from `secrets.tdb`.

## Dependencies And Integration Points
This header is included by passdb modules that need source3 secrets-backed trusted-domain data. It is intentionally narrow and does not expose the `PDB_secrets_*` wrapper declarations present in the C file, so those wrappers are likely declared through another generated or central passdb header path.

## Risks
Because the header declares only `secrets_trusted_domains()`, consumers relying on the uppercase wrapper helpers need declarations elsewhere; missing prototypes would be a build-time signal. The API returns an allocated array of pointers, so callers must use the supplied talloc context correctly.

## Test Signals
Build coverage is the main signal: consumers should compile with this header and resolve `secrets_trusted_domains()`. Runtime tests belong with `pdb_secrets.c` and should verify the returned array lifetime under the caller's talloc context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_secrets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_smbpasswd.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_smbpasswd.c

## Purpose
`pdb_smbpasswd.c` implements the legacy flat-file `smbpasswd` passdb backend. It stores a limited subset of `struct samu` as colon-separated lines containing username, Unix uid, LM hash, NT hash, account-control flags, and password-last-set time. The backend is compatibility-focused and depends on local Unix passwd entries and algorithmic RID-to-uid mappings.

## Important APIs, Types, And Functions
`struct smb_passwd` is the on-disk record model: Unix uid, username, LM/NT hashes, account-control bits, and password last-set time. `struct smbpasswd_privates` stores per-backend runtime state: recursive lock depth, an optional file pointer, parse buffers, hash buffers, and the configured smbpasswd file path.

File access is managed by `do_file_lock()`, `pw_file_lock()`, `pw_file_unlock()`, `startsmbfilepwent()`, and `endsmbfilepwent()`. `startsmbfilepwent()` handles read/update/create modes, `fcntl()` locks with timeout, atomic creation, rename-race detection via stat/fstat inode comparison, buffering, and permission repair to `0600`.

Parsing and formatting are done by `getsmbfilepwent()` and `format_new_smbpasswd_entry()`. Mutation helpers are `add_smbfilepwd_entry()`, `mod_smbfilepwd_entry()`, and `del_smbfilepwd_entry()`. Conversion between legacy records and passdb records is done by `build_smb_pass()` and `build_sam_account()`.

The passdb method implementations are `smbpasswd_getsampwnam()`, `smbpasswd_getsampwsid()`, `smbpasswd_add_sam_account()`, `smbpasswd_update_sam_account()`, `smbpasswd_delete_sam_account()`, `smbpasswd_rename_sam_account()`, `smbpasswd_search_users()`, and `smbpasswd_capabilities()`. `pdb_init_smbpasswd()` builds the method table and private state, while `pdb_smbpasswd_init()` registers the backend name `smbpasswd`.

## Control Flow
Reads open the smbpasswd file with a read lock and iterate line by line. `getsmbfilepwent()` skips comments and blank lines, parses `username:uid:lmhash:nthash:[acct flags]:LCT-XXXXXXXX:` formats, tolerates old records without NT hashes or account-control fields, marks invalidated hashes as null, and infers workstation trust accounts for old-style names ending in `$`. `smbpasswd_getsampwnam()` stops when the username matches; `smbpasswd_getsampwsid()` converts the requested RID to an algorithmic uid, except for the guest RID which maps through `lp_guest_account()`.

Adding a user opens the file for update, creates it if needed, scans for duplicate names, seeks to EOF, formats a complete new line, writes with raw `write()`, and truncates back to the old EOF on short write failure. Updating an existing user opens with a write lock, finds the target line, validates the fixed-width hash and flag/time fields, builds replacement text of exactly the supported field span, sanity-checks surrounding colons, and overwrites in place. Deleting rewrites every non-target record to a per-process temporary file and then renames the temporary file over the original.

`build_smb_pass()` rejects users whose RID cannot be represented as a Unix uid-based algorithmic RID, except the guest RID which maps to the configured guest Unix account. `build_sam_account()` performs the reverse conversion by looking up the Unix account with `Get_Pwnam_alloc()`, using `samu_set_unix()`, and setting hashes, flags, and password timestamps.

Rename is a two-phase compatibility operation. It creates an interim new smbpasswd entry, runs the configured `rename user script` with `%unew` and `%uold` substitutions, flushes nscd on success, deletes the old account, and rolls back the interim new entry if the script path fails.

Search materializes all matching users into a `smbpasswd_search_state` array of `samr_displayentry` values by parsing file records, converting each to `struct samu`, filtering account-control bits, and exposing results through `next_entry`/`search_end`.

## State And Persistence
Persistent state is the configured smbpasswd flat file, defaulting to `lp_smb_passwd_file()` unless a module location is supplied. The file is chmodded to owner read/write only. Adds and updates mutate this file in place under locks; deletes replace it by rename from a temporary file named with the current pid.

Runtime state is the private lock depth, parse buffers, reusable `struct smb_passwd`, and configured path. Because parsing returns pointers into reusable buffers, callers must consume each parsed record before the next `getsmbfilepwent()` call. The backend advertises no special capabilities; it does not store arbitrary RIDs or full AD/passdb metadata.

## Dependencies And Integration Points
The backend depends on source3 passdb APIs, Unix passwd APIs, filesystem/stat/lock functions, generated SAMR definitions, SID helpers, account-control encode/decode helpers, hash hex helpers, loadparm (`lp_smb_passwd_file()`, `lp_guest_account()`, `lp_rename_user_script()`), algorithmic RID helpers, `samu_set_unix()`, `smbrun()`, and nscd cache flushing.

It integrates as a passdb module through `smb_register_passdb(PASSDB_INTERFACE_VERSION, "smbpasswd", pdb_init_smbpasswd)`. It is mainly relevant for legacy local-file installations and migration compatibility.

## Risks
This backend stores only a small subset of passdb state. Full names, descriptions, group mappings, policies, trust data, password history, and many AD attributes cannot round-trip through this file. It depends on local Unix accounts existing for every smbpasswd entry; stale Unix passwd data makes the passdb record unusable.

The file format is fixed-width and update-in-place; malformed lines, long usernames, unsupported old formats, or unexpected field lengths can prevent updates. Locking uses process alarms and whole-file byte-range locks, so interactions with other tools that ignore locking can corrupt data. Delete-by-rewrite renames a temporary file over the original while locks are held on both streams, but failures after rename are only logged. Rename can leave Unix and smbpasswd state inconsistent if the external script succeeds but later deletion fails, or if multiple tools mutate the file concurrently.

There is a notable logic issue in `smbpasswd_getsampwsid()`: `nt_status` is initialized to unsuccessful and never set to OK before the post-build SID equality check, so the intended mismatch check is skipped. The function still returns OK after successful build, but that guard is ineffective.

## Test Signals
Tests should cover parsing old and new record formats, invalid hashes, disabled/no-password markers, trust-account inference, comments and long lines, missing Unix passwd entries, guest SID mapping, algorithmic RID conversion, add duplicate rejection, add rollback on short write, update of hashes/flags/LCT, rejection of old unsupported update format, delete rewrite and permissions, lock timeout behavior, rename-script success/failure rollback, and search filtering by account flags.

Regression tests should explicitly exercise lookup by SID and confirm the returned `struct samu` SID matches the requested SID, catching the currently ineffective mismatch guard. Integration tests should verify behavior with `lp_smb_passwd_file()` and with an explicit module location.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_smbpasswd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_smbpasswd.h -->
# sources/user-network-fs/samba/source3/passdb/pdb_smbpasswd.h

## Purpose
`pdb_smbpasswd.h` is the public header for registering the legacy smbpasswd passdb backend.

## Important APIs, Types, And Functions
The header declares:

`NTSTATUS pdb_smbpasswd_init(TALLOC_CTX *);`

The implementation registers the backend name `smbpasswd` with Samba's passdb module registry.

## Control Flow
There is no executable control flow in the header. Include guards prevent duplicate inclusion.

## State And Persistence
The header has no state. It exposes an initializer for a backend whose persistent state is the smbpasswd flat file.

## Dependencies And Integration Points
Consumers include this header when they need the init symbol for static or module registration. It relies on existing declarations for `NTSTATUS` and `TALLOC_CTX`.

## Risks
The header does not expose any internal smbpasswd structures, which is good encapsulation. Build failures would indicate mismatch between the init declaration and implementation. Runtime risks are in the C implementation.

## Test Signals
Build/link tests should verify `pdb_smbpasswd_init()` is declared and resolves. Module registration tests should verify the backend can be registered and selected as `smbpasswd`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_smbpasswd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_tdb.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_tdb.c

## Purpose
`pdb_tdb.c` implements the `tdbsam` passdb backend, Samba's local TDB-backed account database. It persists serialized `struct samu` records by username, maintains a RID-to-username index, stores a monotonic next-RID counter, handles database format upgrades, and exposes passdb operations for local account lookup, mutation, rename, enumeration, and RID allocation.

## Important APIs, Types, And Functions
Persistent keys are defined by prefixes and info keys: `USER_` for lower-cased username records, `RID_` for RID indexes, `NEXT_RID` for allocation, and `INFO/version` plus `INFO/minor_version` for database versioning. Global runtime state includes `db_sam`, `tdbsam_filename`, and booleans `map_builtin`/`map_wellknown`.

Upgrade helpers are `tdbsam_convert_one()`, `backup_copy_fn()`, `tdbsam_convert_backup()`, `tdbsam_upgrade_next_rid()`, `tdbsam_convert()`, and `tdbsam_open()`. Lookup helpers are `tdbsam_getsampwnam()`, `tdbsam_getsampwrid()`, and `tdbsam_getsampwsid()`. Mutation helpers are `tdb_delete_samacct_only()`, `tdbsam_delete_sam_account()`, `tdb_update_samacct_only()`, `tdb_update_ridrec_only()`, `tdb_update_sam()`, `tdbsam_update_sam_account()`, `tdbsam_add_sam_account()`, and `tdbsam_rename_sam_account()`.

RID allocation and enumeration are implemented by `tdbsam_new_rid()`, `tdbsam_collect_rids()`, `tdbsam_search_users()`, and `tdbsam_search_next_entry()`. `pdb_init_tdbsam()` installs the passdb method table, reads configuration booleans for builtin/wellknown mapping responsibility, computes the database path, and stores it globally. `pdb_tdbsam_init()` registers the backend name `tdbsam`.

## Control Flow
All operations call `tdbsam_open()` as needed. Open creates the database with `0600` permissions, reads version keys, rejects newer major versions, and upgrades older versions under a named mutex. Local databases are first copied through `tdbsam_convert_backup()` to a temporary TDB and atomically renamed back, which preserves records across older hash-function behavior. `tdbsam_convert()` starts a transaction, upgrades `NEXT_RID` from old winbind idmap state if missing, traverses all `USER_` records, decodes old buffer formats into `struct samu`, repacks them in the latest format, and stores current version keys before commit.

Name lookup lowercases the requested username, fetches `USER_<name>`, rejects missing or zero-sized records, and unpacks with `init_samu_from_buffer(SAMU_BUFFER_LATEST)`. RID lookup fetches `RID_<hexrid>` to get the username and delegates to name lookup. SID lookup first checks the SID belongs to the local SAM domain and extracts the RID.

Add and update flow runs through `tdb_update_sam()`. It requires a valid user RID, starts a TDB transaction, and for updates fetches the old account to detect RID changes. It stores the serialized `struct samu` under the username key, updates or inserts the RID index, deletes the old RID key if the RID changed, and commits atomically. Delete removes both username and RID keys in one transaction.

Rename requires a configured external `rename user script`. It copies the old account, sets the new username, starts a transaction, inserts the new username record, lowercases old and new names for script substitution, runs the script, flushes the nscd user cache, rewrites the RID index to point to the new name, deletes the old username record, and commits. If the transaction commit fails after the external script succeeded, the code logs that POSIX and passdb state may be inconsistent.

RID allocation uses `dbwrap_trans_change_uint32_atomic_bystring()` on `NEXT_RID`, returning the previous/current value after increment semantics defined by dbwrap. Enumeration traverses `RID_` keys, stores parsed hex RIDs in a dynamic array, and lazily resolves each RID to a `samu` in `tdbsam_search_next_entry()`, skipping users deleted after collection and filtering account-control bits.

## State And Persistence
Persistent state is `passdb.tdb` under `lp_private_dir()` unless a backend location is supplied. It contains serialized `struct samu` values, RID indexes, version metadata, and the next RID counter. Upgrades may create and rename a temporary `*.tmp` database. `tdbsam_upgrade_next_rid()` can read legacy `winbindd_idmap.tdb` `RID_COUNTER` to seed the counter, falling back to `BASE_RID`.

Runtime state is global rather than per-method: `db_sam` is the open db context and `tdbsam_filename` is a process-global path. Reinitializing the backend frees and replaces the filename. The `map_builtin` and `map_wellknown` flags are also global and are returned through passdb responsibility hooks.

## Dependencies And Integration Points
The backend depends on dbwrap/TDB, TDB utility helpers, passdb serialization (`init_samu_from_buffer()`, `init_buffer_from_samu()`), SID helpers, account control APIs, loadparm (`lp_private_dir()`, `lp_rename_user_script()`, `lp_parm_bool()`), named mutexes, `state_path()`, `smbrun()`, nscd cache flushing, and Samba string/hex parsing helpers.

It integrates through the passdb registry as `tdbsam` and provides `PDB_CAP_STORE_RIDS`. Builtin and wellknown SID responsibility is configurable with `tdbsam:map builtin` and `tdbsam:map wellknown`.

## Risks
The backend relies on global process state, so multiple initializations with different locations can replace `tdbsam_filename` for all method instances. Upgrade paths are complex and high-risk: they rewrite every user record, may rename a temporary database over the original, and use `smb_panic()` on some transaction failures. Backup conversion assumes local database semantics and mutex protection.

Transaction boundaries protect TDB keys but not external rename scripts. Rename can leave the Unix account renamed while TDB commit fails, a risk acknowledged in the code. Usernames are lowercased for storage and indexes, so case-preservation semantics depend on the serialized `samu` content rather than key names. RID index corruption can break lookup and enumeration even when user records exist.

Search enumeration snapshots RIDs first, then resolves records later; concurrent deletion is handled, but concurrent modifications can produce changing display data. RID allocation correctness depends on dbwrap atomic counter behavior and on no external writers corrupting `NEXT_RID`.

## Test Signals
Tests should cover opening a fresh database, version-key initialization, upgrades from SAMU buffer versions 0 through 4, conversion rollback on malformed records, temporary backup rename behavior, missing and migrated `NEXT_RID`, newer-version rejection, name/RID/SID lookup, zero-sized record rejection, add/update/delete transaction behavior, RID change updates, RID index corruption, new RID allocation monotonicity, search filtering and concurrent deletion tolerance, builtin/wellknown responsibility configuration, and rename-script success/failure including commit-failure injection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_tdb.h -->
# sources/user-network-fs/samba/source3/passdb/pdb_tdb.h

## Purpose
`pdb_tdb.h` is the public header for registering the TDB-backed `tdbsam` passdb backend.

## Important APIs, Types, And Functions
The header declares:

`NTSTATUS pdb_tdbsam_init(TALLOC_CTX *);`

The implementation registers the backend name `tdbsam`.

## Control Flow
There is no executable control flow in the header. Include guards prevent duplicate inclusion.

## State And Persistence
The header has no state. It exposes an initializer for a backend whose persistent state is `passdb.tdb`.

## Dependencies And Integration Points
Consumers include this header for static or module registration of the TDB passdb backend. The declaration assumes `NTSTATUS` and `TALLOC_CTX` are already visible.

## Risks
The header is intentionally narrow. Build/link failures are the primary signal for declaration drift. Runtime behavior and persistent-state risks are in `pdb_tdb.c`.

## Test Signals
Build/link tests should verify `pdb_tdbsam_init()` resolves. Module registry tests should verify the backend can be selected as `tdbsam`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_tdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_util.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_util.c

## Purpose
`pdb_util.c` contains passdb utility helpers for creating and populating standard BUILTIN aliases: Users, Administrators, and Guests. These helpers bridge passdb alias creation, SID-to-GID mapping, winbind availability, and domain/local SID membership policy.

## Important APIs, Types, And Functions
`add_sid_to_builtin()` adds a member SID to an existing builtin alias using `pdb_add_aliasmem()`, treating `NT_STATUS_MEMBER_IN_ALIAS` as success and logging other failures. `pdb_create_builtin()` composes a BUILTIN SID from a RID and ensures the corresponding alias exists, either by asking the current passdb backend to create it or by using an existing SID-to-GID mapping when the backend is not responsible for BUILTIN.

`create_builtin_users()`, `create_builtin_administrators()`, and `create_builtin_guests()` create the standard aliases and add expected domain/local memberships. Users can include Domain Users for DC/domain-member roles. Administrators can include Domain Admins and local `DOMAIN\root`. Guests includes local Guest, local Guests, and for domain members the domain Guests group.

## Control Flow
`pdb_create_builtin()` composes `S-1-5-32-<rid>`. If the selected passdb backend is not responsible for BUILTIN, it resolves the BUILTIN SID to a gid with `sid_to_gid()` and calls `pdb_create_builtin_alias(rid, gid)`. If the backend is responsible, it checks `pdb_sid_to_id()` directly; a missing mapping means the alias likely does not exist, so the function requires nested groups and a live winbind ping before creating the builtin alias with gid 0.

The standard creation helpers call `pdb_create_builtin()` first. They then compose the relevant domain/local SIDs and call `add_sid_to_builtin()` for each expected member, returning early on significant failures. `create_builtin_administrators()` uses a temporary talloc context and `lookup_name()` to find the local `root` account SID before adding it if found.

## State And Persistence
Persistent state is maintained by the active passdb backend: builtin alias records and alias membership records. This file does not store data directly. Runtime state is limited to local SIDs, temporary talloc contexts, and lookup results.

The behavior depends on server role, global SAM SID/name, whether the backend claims BUILTIN responsibility, winbind nested-group configuration, and winbind availability.

## Dependencies And Integration Points
This file depends on passdb alias APIs, SID utilities, winbind helpers (`sid_to_gid()`, `winbind_ping()`), loadparm (`lp_winbind_nested_groups()`, `lp_server_role()`), global SID/name helpers, and LSA SID type lookup. It is typically used by setup or account-initialization code that ensures well-known BUILTIN groups exist with expected memberships.

## Risks
BUILTIN creation can fail if winbind is unavailable or nested groups are disabled while the backend is responsible for BUILTIN. Adding duplicate members is intentionally idempotent, but other membership failures propagate. Role-dependent behavior means domain-member and DC paths add domain SIDs while standalone paths do not. The root lookup is best-effort; failure to resolve `DOMAIN\root` does not fail administrator creation.

`pdb_create_builtin()` behaves differently depending on backend responsibility. Misreported `is_responsible_for_builtin` or broken idmap can create missing aliases, aliases with unsuitable gids, or protocol-unreachable errors during initialization.

## Test Signals
Tests should cover creation when backend is and is not responsible for BUILTIN, missing SID-to-GID mapping, winbind unavailable, nested groups disabled, duplicate alias membership, DC/domain-member/standalone role differences, root SID lookup success/failure, and all three standard aliases with expected member SIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_util.c -->
