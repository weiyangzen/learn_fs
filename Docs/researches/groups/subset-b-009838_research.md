# subset-b-009838 Research

Grouped research for Samba source files under `sources/user-network-fs/samba/source3/passdb`. Each file section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/machine_account_secrets.c -->
# sources/user-network-fs/samba/source3/passdb/machine_account_secrets.c

## Purpose

`machine_account_secrets.c` owns Samba's local persistence for generated private identity and trust information: domain SIDs and GUIDs, machine account passwords, Kerberos salting principals, legacy trust-password hashes, and the newer NDR-encoded `secrets_domain_info1` record used for joins and password rollover. It bridges old `secrets.tdb` key/value entries with newer structured domain info so callers can continue to fetch legacy plaintext/hash secrets while upgraded paths get richer password history, Kerberos keys, and password-change state.

## Important APIs, Types, And Functions

Key string builders normalize domains with `talloc_asprintf_strupper_m()`: `domain_sid_keystr()`, `domain_guid_keystr()`, `protect_ids_keystr()`, `machine_password_keystr()`, `machine_prev_password_keystr()`, `machine_sec_channel_type_keystr()`, `machine_last_change_time_keystr()`, `trust_keystr()`, `domain_info_keystr()`, and `des_salt_key()`.

SID/GUID APIs include `secrets_store_domain_sid()`, `secrets_fetch_domain_sid()`, `secrets_delete_domain_sid()`, `secrets_store_domain_guid()`, and `secrets_fetch_domain_guid()`. Domain protection is controlled by `secrets_mark_domain_protected()` and `secrets_clear_domain_protection()`; protection prevents accidental direct SID/GUID changes except during the transaction that rewrites a full domain-info record.

Machine password compatibility APIs include `secrets_store_machine_pw_sync()`, `secrets_fetch_machine_password()`, `secrets_fetch_prev_machine_password()`, `secrets_fetch_pass_last_set_time()`, `secrets_fetch_trust_account_password_legacy()`, and `secrets_delete_machine_password_ex()`. Kerberos salt helpers are `kerberos_standard_des_salt()`, `kerberos_secrets_store_des_salt()`, `kerberos_secrets_fetch_salt_princ()`, and the private `kerberos_secrets_fetch_des_salt()`.

Structured domain-info APIs are `secrets_fetch_or_upgrade_domain_info()`, `secrets_store_JoinCtx()`, `secrets_prepare_password_change()`, `secrets_failed_password_change()`, `secrets_defer_password_change()`, and `secrets_finish_password_change()`. Internals include `secrets_fetch_domain_info1_by_key()`, `secrets_store_domain_info1_by_key()`, `secrets_store_domain_info()`, `secrets_domain_info_password_create()`, `secrets_domain_info_kerberos_keys()`, `secrets_check_password_change()`, and `secrets_abort_password_change()`.

The main structured type is generated NDR data around `struct secrets_domain_info1` and `struct secrets_domain_info1_password`, wrapped in `struct secrets_domain_infoB` with version `SECRETS_DOMAIN_INFO_VERSION_1`.

## Control Flow And State

Simple SID/GUID fetches read fixed-size binary blobs from `secrets_fetch()` and reject size mismatches. `secrets_store_domain_sid()` copies into a zero-initialized `struct dom_sid` before storing to avoid uninitialized bytes, then resets the cached global SAM SID. `secrets_fetch_domain_guid()` lazily creates a GUID only for PDC/IPA DC roles.

`secrets_store_machine_pw_sync()` is the compatibility write path for machine trust data. With `delete_join`, it deletes all join-related keys. Otherwise it writes current password, optional previous password, optional secure channel type, last-change timestamp, domain SID, and optional DES salting principal. Secure channel type `0` means delete the explicit key and allow readers to fall back to `get_default_sec_channel()`.

`secrets_store_domain_info()` is the transactional canonical writer. It validates secure channel type and server role, starts a `secrets_db_ctx()` transaction, clears domain protection, deletes older join keys, writes the packed `secrets_domain_infoB`, converts UTF-16 munged cleartext passwords back to Unix strings for the compatibility keys, writes compatibility machine-password state, optionally stores a domain GUID, marks IDs protected, and commits. Any failure cancels the transaction.

`secrets_fetch_or_upgrade_domain_info()` first checks legacy last-change time. If a structured record exists and is at least as current, it returns it. Otherwise it reads legacy current and previous passwords, SID, GUID, secure channel, salt principal, and domain names, builds a full `secrets_domain_info1`, creates password structures and Kerberos keys, calls `secrets_store_domain_info(..., upgrade=true)`, reparses the record, and commits. This is the legacy-to-structured migration lane.

`secrets_store_JoinCtx()` builds a fresh domain-info record from `libnet_JoinCtx`, deriving an AD Kerberos salt if needed. It preserves old and older passwords from an existing join so already-issued tickets remain usable, then stores the new record transactionally.

Password rotation is split into prepare, finish, fail, and defer. `secrets_prepare_password_change()` loads or upgrades the record, preserves an existing pending `next_change` if present, otherwise creates one from the new plaintext password, writes it, reparses, commits, and then optionally syncs keytabs if the change was newly prepared. `secrets_finish_password_change()` verifies that the caller's cookie still matches stored state, promotes `next_change->password` to current, shifts current to old and old to older, clears `next_change`, commits, then syncs keytabs. Failure and defer paths update the pending change's local/remote status; defer also moves `password_last_change` forward to delay automatic retry.

## Persistence And Secret Handling

Persistent state lives in Samba secrets storage under stable uppercase key prefixes such as `SECRETS_DOMAIN_SID`, `SECRETS_DOMAIN_GUID`, `SECRETS_MACHINE_PASSWORD`, `SECRETS_MACHINE_PASSWORD_PREV`, `SECRETS_MACHINE_LAST_CHANGE_TIME`, `SECRETS_MACHINE_SEC_CHANNEL_TYPE`, `SECRETS_MACHINE_ACCT_PASS`, `SECRETS_MACHINE_DOMAIN_INFO`, and `SECRETS_SALTING_PRINCIPAL/DES`. Structured records are NDR blobs; legacy machine password data is mostly raw strings, 32-bit little-endian integers, and fixed structs.

The file uses `BURN_FREE()`, `BURN_FREE_STR()`, `data_blob_clear_free()`, `ZERO_STRUCT()`, `talloc_keep_secret()`, and a destructor that zeroes NT hashes to reduce secret residue. It also uses constant-time `mem_equal_const_time()` when comparing hashes during password-change race checks.

## Dependencies And Integration Points

This file depends on `secrets.h`, `dbwrap`, generated NDR for `ndr_secrets.h` and `libnet_join.h`, libcli auth/security types, Kerberos wrappers, Samba loadparm (`lp_*`), server role macros, and time conversion utilities. It is consumed by passdb and credential code that fetches machine trust credentials, by join code via `secrets_store_JoinCtx()`, by machine password rotation logic, and by SID initialization in `machine_sid.c`.

## Risks And Edge Cases

The highest-risk paths are transaction correctness across dual-format writes, preserving existing old passwords during rejoin, and matching the caller cookie against stored pending password-change state. Protection handling is intentionally strict; an unexpected `SECRETS_PROTECT_IDS` value causes SID/GUID writes to fail. Legacy compatibility broadens the failure surface because a structured write must also maintain older keys. Kerberos key creation depends on optional `HAVE_ADS`; without salt/Kerberos support, only ARCFOUR is generated. Error handling often returns broad domain-info access failures, so tests need to inspect side effects as well as status.

## Test Signals

Useful tests include legacy secrets upgrade from current/previous plaintext keys, delete-join cleanup, protected SID/GUID refusal, domain GUID lazy creation for PDC/IPA DC roles only, structured join writes preserving old passwords, password prepare/finish/fail/defer race detection, keytab sync ordering after commit, Kerberos salt fallback, secure channel defaulting, and size/corruption handling for SID/GUID/NDR blobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/machine_account_secrets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/machine_sid.c -->
# sources/user-network-fs/samba/source3/passdb/machine_sid.c

## Purpose

`machine_sid.c` manages the process-wide cached local SAM SID, including generating or migrating it when no valid secrets entry exists. It defines the semantics that the local SAM SID equals the domain SID only when Samba is acting as a DC; otherwise it is the workstation SID.

## Important APIs And Functions

The public API is `get_global_sam_sid()`, `reset_global_sam_sid()`, `sid_check_is_our_sam()`, and `sid_check_is_in_our_sam()`. Private helpers include `read_sid_from_file()` for old `MACHINE.SID` compatibility, `generate_random_sid()` for `S-1-5-21-x-y-z` SID creation, and `pdb_generate_sam_sid()` for discovery/migration/generation.

## Control Flow And State

`get_global_sam_sid()` returns cached `global_sam_sid` if available. On first use it opens `secrets_db_ctx()`, starts a dbwrap transaction, calls `pdb_generate_sam_sid()`, and commits. It panics on missing secrets DB, transaction failure, or SID generation failure because Samba cannot safely continue without a stable local SAM SID.

`pdb_generate_sam_sid()` checks DC state first: a DC prefers the workgroup domain SID. It then tries the local netbios-name SID. For DCs, mismatches between local and domain SID are repaired by storing the domain SID under the local name; missing domain SID is populated from local SID. If no secrets SID exists, it reads and migrates `$private_dir/MACHINE.SID`, unlinks the file after storing, and for non-DCs also stores the same SID under the workgroup. Finally it generates and stores a random SID; DCs store it as both local and workgroup domain SID.

## Persistence Behavior

The persistent source of truth is the secrets database through `secrets_fetch_domain_sid()` and `secrets_store_domain_sid()`. A legacy plain text `MACHINE.SID` file is supported only as a migration input. The in-memory cache is manually invalidated by `reset_global_sam_sid()`, which is called by SID store operations in the secrets layer.

## Dependencies And Integration Points

This file depends on `passdb/machine_sid.h`, `secrets.h`, `dbwrap`, security SID helpers, loadparm values such as `lp_workgroup()`, `lp_netbios_name()`, and `lp_private_dir()`, and the `IS_DC` role macro. Its result is used throughout passdb for RID composition, SID membership checks, user/group lookup, and account serialization.

## Risks And Edge Cases

Startup races are mitigated with a secrets DB transaction. Incorrect DC role detection or mismatched stored SIDs can cause domain identity drift, so the DC repair logic is critical. `read_sid_from_file()` reads only one line and accepts anything `string_to_sid()` accepts. `generate_random_sid()` constructs three 32-bit random subauthorities; uniqueness depends on `generate_random_buffer()` quality. Panic-on-failure behavior is intentional but makes test setup sensitive to secrets DB availability.

## Test Signals

Tests should cover fresh generation, DC and non-DC storage keys, migration from `MACHINE.SID`, unlink-after-migration, mismatched DC local/domain SID repair, cache reset after store, transaction behavior, and `sid_check_is_in_our_sam()` stripping a RID before comparison.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/machine_sid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/machine_sid.h -->
# sources/user-network-fs/samba/source3/passdb/machine_sid.h

## Purpose

`machine_sid.h` declares the global SAM SID interface exported by `machine_sid.c`. It is a narrow header used by passdb code that needs to obtain or test the local SAM/domain SID without knowing the secrets DB generation and migration details.

## APIs

The header declares `struct dom_sid *get_global_sam_sid(void)`, `void reset_global_sam_sid(void)`, `bool sid_check_is_our_sam(const struct dom_sid *sid)`, and `bool sid_check_is_in_our_sam(const struct dom_sid *sid)`.

## Integration Points

Callers include SID/RID composition helpers, group mapping, passdb backend interface code, account serialization, and secrets code that invalidates the cache after storing a SID. The header relies on prior declarations of `struct dom_sid` and `bool` from Samba common headers.

## Risks And Test Signals

Because the header exposes a mutable pointer to cached global state, callers must not free or mutate it. Tests around users of this header should verify cache invalidation through `reset_global_sam_sid()`, correct domain-membership checks, and safe behavior when the backing secrets DB changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/machine_sid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/passdb.c -->
# sources/user-network-fs/samba/source3/passdb/passdb.c

## Purpose

`passdb.c` contains core `struct samu` lifecycle, Unix-account initialization, account-control and password/hour hex helpers, algorithmic RID mapping, local password changes, legacy TDB buffer serialization, bad-password policy updates, and trust credential fetch helpers. It is central glue between Unix passwd/group state, Samba account records, local SAM SID logic, secrets storage, and credentials construction.

## Important APIs And Functions

Lifecycle and Unix initialization are handled by `samu_new()`, `samu_set_unix()`, `samu_alloc_rid_unix()`, and private `samu_set_unix_internal()`. Account-control and hex helpers include `pdb_encode_acct_ctrl()`, `pdb_decode_acct_ctrl()`, `pdb_sethexpwd()`, `pdb_gethexpwd()`, `pdb_sethexhours()`, and `pdb_gethexhours()`.

RID functions include `algorithmic_rid_base()`, `algorithmic_pdb_user_rid_to_uid()`, `max_algorithmic_uid()`, `algorithmic_pdb_uid_to_user_rid()`, `pdb_group_rid_to_gid()`, `max_algorithmic_gid()`, `algorithmic_pdb_gid_to_group_rid()`, and `algorithmic_pdb_rid_is_user()`. Lookup and local mutation include `lookup_global_sam_name()` and `local_password_change()`.

Serialization APIs are `init_samu_from_buffer()`, `init_buffer_from_samu()`, and `pdb_copy_sam_account()`, backed by versioned formats V0 through V4. Policy and trust helpers include `pdb_update_bad_password_count()`, `pdb_update_autolock_flag()`, `pdb_increment_bad_password_count()`, `get_trust_pw_clear()`, `get_trust_pw_hash()`, and `pdb_get_trust_credentials()`.

## Control Flow And State

`samu_new()` allocates a zeroed account, attaches `samu_destroy()` to wipe password blobs/plaintext, sets NT-compatible default times, logon hours, counters, string fields, and normal-user account control. `samu_set_unix_internal()` populates a `samu` from `struct passwd`, trims chfn-style GECOS fields, sets default profile/home/drive/script substitutions, marks workstation accounts ending in `$`, handles guest RID 501, and either asks a backend for a new RID or derives one algorithmically from uid.

`local_password_change()` reads the target account, handles delete early, optionally creates a user/trust/interdomain account, updates account flags for no-password/disable/enable, hashes a new plaintext password through `pdb_set_plaintext_passwd()`, and commits with `pdb_update_sam_account()`. It builds user-facing message/error strings with `asprintf()`.

The serialization readers unpack historical TDB formats. V0 has base timestamps and hashes; V1 adds bad-password time; V2 adds password history and removes an obsolete field; V3 widens account-control to 32 bits and adds comment; V4 aliases V3. Readers reconstruct defaults when stored fields are absent and optionally expand explicit path substitutions. Writers emit the latest V4/V3 layout, storing only non-default path fields and serializing password history according to current account policy.

Bad-password update functions enforce policy-derived reset and lockout behavior. `pdb_increment_bad_password_count()` checks lockout policy, clears expired autolock/count state, increments count/time, and sets `ACB_AUTOLOCK` once threshold is reached.

Trust password helpers first distinguish DC trusted-domain situations. DCs can read trusted domain passwords via passdb when allowed. Members and self-joined DCs read the machine password for `lp_workgroup()` from secrets, optionally include the previous password for half the machine password timeout, and fall back to legacy hashed secrets for hash callers. `pdb_get_trust_credentials()` builds `cli_credentials`, using the common machine-account DB path for the primary domain, trusted-domain backend credentials when available, plaintext/hash fallbacks otherwise, and adjusts Kerberos requirements based on DNS domain availability.

## Persistence Behavior

`struct samu` state is transient until passdb backend calls persist it. Serialization functions define the binary representation used by TDB-style passdb backends. Local password changes persist through backend methods. Trust credentials read persistent secrets and trusted-domain passdb records. Account policies are read from passdb policy storage and influence computed times, history length, lockout behavior, and serialization.

## Dependencies And Integration Points

This file depends on `passdb.h`, Unix passwd/group APIs, loadparm, auth credentials, secrets, security SID helpers, substitution helpers, and tdb pack/unpack utilities. It calls many setter/getter APIs from `pdb_get_set.c`, global SID APIs from `machine_sid.c`, backend dispatchers from `pdb_interface.c`, and secrets functions from `machine_account_secrets.c`.

## Risks And Edge Cases

Legacy serialization is compatibility-sensitive, especially 32-bit time conversion, absent default path fields, and password history sizing under policy changes. `pdb_gethexhours()` appears to call `hex_byte(p, ...)` inside a loop without advancing `p + i`, which is a notable defect signal. Local password creation/deletion can run external scripts and must protect root and account flags. Algorithmic RID base misconfiguration is corrected to an even value at or above `BASE_RID`, but mismatches with store-RID backends remain risky. Trust credential fallback must avoid exposing stale previous passwords beyond the intended window.

## Test Signals

Tests should cover `samu_new()` defaults, Unix account conversion for guest/user/workstation accounts, RID round-trips and well-known RID detection, account-control encode/decode, password hash/hour hex decode errors, local add/delete/enable/disable/password flows, all serialized buffer versions, password history truncation/rotation, bad-password reset and autolock policies, trust credential primary-domain and trusted-domain branches, hash-only fallback, and root delete/rename protections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/passdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_compat.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_compat.c

## Purpose

`pdb_compat.c` provides compatibility helpers for older RID-centric passdb callers. It converts between full user/group SIDs and RIDs using the current global SAM SID, delegating actual SID storage to `pdb_get_set.c` setters.

## Important APIs

`pdb_get_user_rid()` and `pdb_get_group_rid()` extract RIDs from `pdb_get_user_sid()` and `pdb_get_group_sid()` if the SID belongs to `get_global_sam_sid()`. `pdb_set_user_sid_from_rid()` and `pdb_set_group_sid_from_rid()` compose full SIDs from the global SAM SID and call `pdb_set_user_sid()` or `pdb_set_group_sid()`.

## Control Flow And State

All four functions guard against null `struct samu` inputs. Setters fetch the global SAM SID, compose a domain SID plus RID with `sid_compose()`, set the result with the requested `enum pdb_value_state`, and log the full SID at debug level 10. Getters return `0` if the input is null or the stored SID does not share the current global SAM SID.

## Dependencies And Integration Points

This file depends on `passdb.h`, SID helpers, and the global SAM SID from `machine_sid.c`. It is used by account initialization, serialization/deserialization, algorithmic RID code, and legacy backend interfaces that still store or exchange RIDs rather than full SIDs.

## Risks And Test Signals

The zero return from RID getters can mean either invalid input or a real RID 0-style value, so callers must treat it carefully. If the global SAM SID cache is stale, conversions can silently fail or compose incorrect SIDs. Tests should cover null inputs, non-domain SIDs, valid user/group RID extraction, setter flag propagation, and behavior after `reset_global_sam_sid()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_get_set.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_get_set.c

## Purpose

`pdb_get_set.c` is the field access layer for `struct samu`. It centralizes getters, setters, calculated password times, change/set/default bitmaps, SID/group handling, password hash storage, plaintext password handling, password history rotation, and backend private data attachment.

## Important APIs And Functions

Password time helpers are `pdb_is_password_change_time_max()`, private `pdb_password_change_time_max()`, `pdb_get_pass_can_change_time()`, `pdb_get_pass_can_change_time_noncalc()`, `pdb_get_pass_must_change_time()`, and `pdb_get_pass_can_change()`. Field getters cover account control, times, logon hours, hashes, password history, plaintext password, SIDs, strings, counters, locale fields, `unknown_6`, and backend private data.

Setter APIs include `pdb_set_init_flags()`, `pdb_set_acct_ctrl()`, timestamp setters, SID setters, string setters, hash setters, `pdb_set_pw_history()`, `pdb_set_plaintext_pw_only()`, counter/locale/hour setters, `pdb_set_backend_private_data()`, `pdb_set_pass_can_change()`, `pdb_set_plaintext_passwd()`, `pdb_update_history()`, `pdb_build_fields_present()`, `pdb_element_is_changed()`, and `pdb_element_is_set_or_changed()`.

## Control Flow And State

Getters generally expose stored fields directly, but password change times are calculated from account policy. A last-set time of zero means password changes are disabled or not meaningful. Password-can-change adds minimum password age unless an explicit changed max time is set. Password-must-change returns zero for no last-set time, a stable `0x7fffffff` max for `ACB_PWNOEXP`, `get_time_t_max()` when max age is unset, or last-set plus max age.

`pdb_set_init_flags()` lazily allocates two bitmaps: fields that are set and fields that are changed. `PDB_CHANGED` sets both, `PDB_SET` clears changed and sets set, and `PDB_DEFAULT` clears both. All setters update the underlying field and then mark flags.

SID handling copies user SIDs directly. Group SID setting allocates a cached SID and accepts the supplied SID only if it is the domain-users SID or maps to a gid; otherwise it falls back to domain users (`DOMAIN_RID_USERS`). `pdb_get_group_sid()` lazily computes the primary group SID from Unix primary gid via `get_primary_group_sid()` if no explicit group SID is cached.

Password setting stores NT and LM hashes in `DATA_BLOB`s. LM hashes are dropped for changed passwords unless LANMAN auth is enabled, or when `E_deshash()` rejects long passwords. `pdb_set_plaintext_passwd()` computes NT and optional LM hashes, stores plaintext for backends that need it, updates `pass_last_set_time`, and rotates password history. `pdb_update_history()` stores a zero salt plus raw NT hash in the current history format and shifts older entries down.

## Persistence Behavior

This file does not directly persist to disk. It prepares in-memory `struct samu` state and changed/default flags that backend update routines interpret. Sensitive blobs are cleared before replacement; plaintext is burned before overwrite. Password-history size follows `PDB_POLICY_PASSWORD_HISTORY`.

## Dependencies And Integration Points

Dependencies include `passdb.h`, auth hash helpers, SID/security helpers, and bitmap utilities. The functions are used heavily by `passdb.c` serialization, backend implementations, RPC account management, authentication, and local password change flows.

## Risks And Edge Cases

Calculated password dates can differ from raw stored dates, so serialization and backend loading must use the non-calculated getter where appropriate. String setters use `PDB_NOT_QUITE_NULL` because older callers expect non-null strings. Group SID fallback can hide an unmapped group SID by replacing it with Domain Users. Setter flag semantics are central to LDAP/backends; incorrect flags can cause missing or excessive writes. `pdb_update_history()` copies `current_history_len` entries into a buffer sized for `pwHistLen`; policy shrinkage can overread/overwrite if current length exceeds new policy length, making this a risk area.

## Test Signals

Tests should cover calculated password dates under min/max/no-expiry policies, max-time compatibility values, flag bitmap transitions for all `enum pdb_value_state` values, null string compatibility, user/group SID parsing and fallback, hash setting with LANMAN enabled/disabled and long passwords, plaintext burn/replace, password history rotation with policy 0/1/N and policy shrink, backend-private destructor invocation, and `pdb_element_is_changed()` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_get_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_interface.c -->
# sources/user-network-fs/samba/source3/passdb/pdb_interface.c

## Purpose

`pdb_interface.c` is the passdb backend dispatcher and default implementation provider. It registers passdb modules, initializes the configured backend, exposes global wrapper functions for account/group/alias/trust/secret operations, manages selected caches, maps SIDs and Unix IDs, and fills a `struct pdb_methods` table with default behavior that modules can override.

## Important APIs And Functions

Backend management includes `smb_register_passdb()`, `pdb_find_backend_entry()`, `pdb_get_backends()`, `make_pdb_method_name()`, `initialize_password_db()`, `pdb_get_tevent_context()`, and private `pdb_get_methods_reload()`/`pdb_get_methods()`. Account wrappers include `pdb_getsampwnam()`, `pdb_getsampwsid()`, `pdb_create_user()`, `pdb_delete_user()`, `pdb_add_sam_account()`, `pdb_update_sam_account()`, `pdb_delete_sam_account()`, `pdb_rename_sam_account()`, and `pdb_update_login_attempts()`.

Group and alias wrappers include `pdb_getgrsid()`, `pdb_getgrgid()`, `pdb_getgrnam()`, `pdb_create_dom_group()`, `pdb_delete_dom_group()`, group mapping operations, `pdb_enum_group_members()`, `pdb_enum_group_memberships()`, `pdb_set_unix_primary_group()`, `pdb_add_groupmem()`, `pdb_del_groupmem()`, alias CRUD/member enumeration functions, and `pdb_lookup_rids()`.

Policy, ID, search, trust, UPN, responsibility, and secret APIs include `pdb_get_account_policy()`, `pdb_set_account_policy()`, `pdb_id_to_sid()`, `pdb_sid_to_id()`, `pdb_new_rid()`, `pdb_search_users()`, `pdb_search_groups()`, `pdb_search_aliases()`, `pdb_search_entries()`, trust-domain wrappers, `pdb_filter_hints()`, `pdb_enum_upn_suffixes()`, `pdb_set_upn_suffixes()`, `pdb_is_responsible_for_*()`, `pdb_get_secret()`, `pdb_set_secret()`, `pdb_delete_secret()`, and `make_pdb_method()`.

## Control Flow And State

Backend initialization is lazy. `make_pdb_method_name()` parses `backend[:location]`, searches registered built-ins, optionally probes a plugin, then calls the backend init function. `pdb_get_methods_reload()` caches the active `pdb_methods` singleton and recreates it on reload. `pdb_get_methods()` panics if the configured backend cannot initialize.

`pdb_getsampwnam()` delegates to the backend, tries to unlock expired autolocks via `pdb_try_account_unlock()`, copies the account into a memcache keyed by user SID, and returns success. `pdb_getsampwsid()` handles guest RID 501 specially, checks that the SID belongs to the global SAM, uses the SID cache when possible, otherwise calls the backend, then also tries unlock. Updates and deletes flush or delete cache entries and send an ID-cache delete message after user deletion.

Default user creation locates or creates a Unix account via configured add-user/add-machine scripts, flushes NSS caches, builds a `samu`, allocates a RID, disables the account until a password is set, and calls `add_sam_account()`. Default deletion removes the passdb entry first and then optionally runs the Unix delete script, refusing root through the public wrapper.

Default group and membership methods bridge Samba group mapping to Unix group commands. They compose SIDs from global SAM SID and RIDs, create/delete Unix groups, add initial groupmap entries, update primary groups, and verify membership changes by rereading group membership. Alias methods are backend dispatch only unless overridden elsewhere.

ID mapping defaults check local SAM, Unix Users/Groups synthetic SID spaces, BUILTIN/well-known aliases, then fail. Successful mappings update `idmap_cache_set_sid2unixid()`. `pdb_new_rid()` requires store-RID capability, rejects algorithmic RID base overrides, then retries up to 250 backend allocations until `lookup_global_sam_rid()` confirms the RID is unused.

Search APIs use `struct pdb_search` with a lazy cache of `samr_displayentry` rows. The destructor calls `search_end()` if enumeration was not already closed.

Trust defaults adapt older trusted-domain password secrets to newer trusted-domain structures by packing/unpacking `trustAuthInOutBlob` for downlevel outbound trusts. Secret defaults delegate to LSA secret storage.

## Persistence Behavior

Persistence is backend-dependent through `struct pdb_methods`. This file itself mutates global singleton state (`backends`, active `pdb_methods`, `pdb_tevent_ctx`) and memory caches. It can trigger external Unix account/group scripts and NSS cache flushes. Account policies are read/written through backend methods while elevated with `become_root()`. Trust defaults persist through secrets helper functions; secret defaults persist through LSA secret APIs.

## Dependencies And Integration Points

The file integrates generated SAMR/DRS/idmap NDR types, memcache, winbind environment controls, loadparm, messaging, server IDs, Unix passwd/group helpers, group mapping, idmap cache, secrets, and global context access. It is the primary public C API layer between Samba services/RPC code and concrete passdb modules such as tdbsam, smbpasswd, ldap, or secrets-backed implementations.

## Risks And Edge Cases

Global singleton backend state makes reload and plugin registration order important. Default external scripts can have side effects outside passdb and are only partially verified. Cache correctness depends on flushing on every update/rename/delete path. `lookup_global_sam_rid()` treats a non-null newly allocated `sam_account` pointer as a found user even after lookup failure, which is a defect signal because the pointer exists regardless of backend result. RID allocation has a finite retry loop and depends on lookup correctness. Group member enumeration disables winbind temporarily and must restore it correctly. Public wrappers protect root deletion/rename by SID-to-uid mapping, but backend implementations still need their own safeguards.

## Test Signals

Tests should cover duplicate/version-mismatched backend registration, plugin load failure, reload freeing private data, account cache add/hit/flush/delete, autolock expiry update, guest SID lookup, add/delete user script branches and root protection, group create/delete/member verification, account policy privilege wrappers, SID/ID mappings for local SAM, Unix Users/Groups, BUILTIN and unknown SIDs, RID allocation collision retries, search pagination/destructor behavior, trusted-domain default packing/unpacking constraints, LSA secret delegation, and method table defaults from `make_pdb_method()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/passdb/pdb_interface.c -->
