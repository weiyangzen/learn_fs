# Research Group: subset-b-009852

This grouped report covers the SAMR RPC server implementation and utility files plus the iremotewinspool opcode mapping utility. Each section is source-tree aligned for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_nt.c -->
# Research: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_nt.c

## Purpose

`srv_samr_nt.c` is the main Samba source3 implementation of the SAMR RPC server entry points. It translates generated NDR SAMR operations into passdb, group mapping, account-policy, SID lookup, password-change, and security-descriptor operations. It owns server-side SAMR policy handles for connect, domain, user, group, and alias objects; maps requested generic access into object-specific rights; enforces privilege overrides such as `SeAddUsers` and `SeMachineAccount`; enumerates domain users/groups/aliases; queries and mutates user, group, alias, and domain policy state; and implements password-validation and password-change paths.

## Important APIs, Types, and Functions

- `enum samr_handle` and `struct samr_info`: private payloads stored behind policy handles. `samr_info` keeps `access_granted`, an object SID, and an optional `disp_info` enumeration cache pointer.
- `DISP_INFO`: per-domain display/enumeration cache with `pdb_search` handles for users, machines, groups, aliases, and masked user enumeration, plus a `tevent_timer` idle expiry.
- `create_samr_policy_handle()`, `samr_policy_handle_find()`, and `samr_handle_access_check()`: central handle lifecycle and access checking. `samr_policy_handle_find()` validates both handle type and required rights.
- `make_samr_object_sd()`: constructs default security descriptors with Everyone read/execute, Builtin Administrators and Account Operators full access, Domain Admins on DCs, and optional object-specific SID access.
- `_samr_Connect*()`, `_samr_OpenDomain()`, `_samr_OpenUser()`, `_samr_OpenGroup()`, `_samr_OpenAlias()`, `_samr_Close()`: policy-handle entry and object-open operations.
- `_samr_EnumDomainUsers()`, `_samr_EnumDomainGroups()`, `_samr_EnumDomainAliases()`, `_samr_QueryDisplayInfo*()`, `_samr_GetDisplayEnumerationIndex*()`: enumeration and display-info RPCs backed by passdb paged searches and `DISP_INFO`.
- `_samr_QueryUserInfo()` and `get_user_info_*()`: map passdb `struct samu` state into SAMR user information levels, with special handling for level 18 password hashes.
- `_samr_SetUserInfo()` and `set_user_info_*()`: update passdb fields and passwords for supported SAMR set-info levels, including RC4/session-key and AES-protected password formats.
- `_samr_QueryDomainInfo()`, `_samr_SetDomainInfo()`, `_samr_GetDomPwInfo()`: expose and update account policies such as password length/history/age, lockout duration/window, bad-attempt threshold, and force-logoff.
- `_samr_CreateUser2()`, `_samr_CreateDomainGroup()`, `_samr_CreateDomAlias()`, delete routines, and membership routines: create, delete, and mutate accounts/groups/aliases through passdb and group mapping APIs.
- `_samr_ChangePasswordUser2()`, `_samr_OemChangePasswordUser2()`, `_samr_ChangePasswordUser3()`, `_samr_ChangePasswordUser4()`: password-change variants. Older `_samr_ChangePasswordUser()` is intentionally not implemented.
- `_samr_ValidatePassword()`: DC-only, privacy-authenticated password validation for levels 2 and 3 using domain password policy and complexity checks.

## Control Flow

The typical SAMR flow starts with `_samr_Connect*()`, which checks pipe access, maps generic access, creates a connect handle, and stores granted rights. `_samr_LookupDomain()` or `_samr_EnumDomains()` resolves a domain SID. `_samr_OpenDomain()` validates the connect handle, checks a domain security descriptor and privilege overrides, rejects non-local and non-BUILTIN domains, attaches a `DISP_INFO` cache, and returns a domain handle.

Object-open calls compose or validate SIDs from domain handles. `_samr_OpenUser()` loads the target `samu` before final access decisions so it can require different privilege overrides for machine, normal, server-trust, and domain-trust accounts. `_samr_OpenGroup()` and `_samr_OpenAlias()` verify group/alias existence through group mapping, lookup, or `sid_to_gid()`, then create object handles with granted rights.

Enumeration calls obtain domain handles with enumeration rights, run passdb searches under `become_root()`, convert `samr_displayentry` rows into wire arrays, advance resume handles, and return `STATUS_MORE_ENTRIES` when the returned count reaches the local maximum. Display-info levels 1-5 share the same cache and differ only in account class and output structure.

Query paths allocate output unions on `p->mem_ctx`, load passdb data under root where required, clear password hashes from normal `samu` records with `samr_clear_sam_passwd()`, and call level-specific initializers. Level 18 is exceptional: it is only served over `NCALRPC` to a SYSTEM security token and deliberately avoids `become_root()`.

Set paths first derive the access mask from the requested information level or `fields_present`, validate the user handle, load the `samu`, enter a root block, and dispatch to level-specific setters. Attribute levels mostly call `copy_id*_to_sam_passwd()` from `srv_samr_util.c` and then `pdb_update_sam_account()`. Password levels decrypt or decode the password buffer first, set passdb plaintext/hash fields, optionally sync the UNIX password through `chgpasswd()`, and finally update passdb. Successful mutations flush the display cache for the affected SID.

Group and alias membership paths verify handle rights, call passdb membership APIs under root, return SAMR RID/SID arrays, and flush caches after mutations. Domain policy setters validate the information level and write passdb account policy keys.

## State and Persistence Behavior

Persistent state is primarily passdb-backed: user records (`pdb_create_user()`, `pdb_update_sam_account()`, `pdb_delete_user()`), domain groups and aliases (`pdb_create_dom_group()`, `pdb_delete_dom_group()`, `pdb_create_alias()`, `pdb_set_aliasinfo()`), group memberships (`pdb_add_groupmem()`, `pdb_del_groupmem()`), alias memberships (`pdb_add_aliasmem()`, `pdb_del_aliasmem()`), and account policies (`pdb_set_account_policy()`).

Transient state includes policy handles allocated with talloc on the pipe memory context and the static `DISP_INFO` caches for the local SAM and BUILTIN domains. Those caches can outlive a single SAMR handle and are expired by a tevent timer after `DISP_INFO_CACHE_TIMEOUT` seconds of idle time. Mutations call `force_flush_samr_cache()` to invalidate cached enumerations.

Privilege transitions are explicit. Most passdb reads/writes are bracketed by `become_root()` and `unbecome_root()`. Password-change paths also use transport encryption checks, session-key extraction, and cryptographic decoding before persistent updates. `_samr_ChangePasswordUser4()` uses a named mutex keyed by username when reloading account state and updating lockout counters, reducing races with concurrent bad-password tracking.

## Dependencies and Integration Points

This file integrates with generated SAMR NDR headers and the generated server compatibility include `ndr_samr_scompat.c`. Core dependencies include passdb (`struct samu`, account policies, searches, group mappings), security descriptors and access checking, privilege and security-token helpers, SID utilities, secrets for domain SID lookup, loadparm configuration, tsocket remote-address extraction, winbind toggling during account creation, base64 helpers for `munged_dial`, GnuTLS helpers for RC4 and AES password buffers, global tevent context, and password complexity/change helpers declared in `srv_samr_util.h`.

The RPC integration point is the `pipes_struct`/`dcesrv_call_state` environment. Memory ownership is mostly `p->mem_ctx`; server faults are signaled by setting `p->fault_state` for unsupported opnums and access-denied validation scenarios.

## Risks and Edge Cases

- Access control is broad and subtle. Root mode can override `samr_handle_access_check()`, and object opens apply privilege-based write grants. Regressions can expose account modification or password operations.
- Enumeration caching uses static pointers for BUILTIN and local SAM domains. Cache invalidation depends on mutation paths calling `force_flush_samr_cache()` with a SID that resolves to the same cache bucket.
- `can_create()` is explicitly racy because the passdb backend cannot be globally locked between lookup and create/rename.
- Password paths handle multiple legacy and modern formats. RC4/session-key handling is gated by weak-crypto policy and transport encryption for some levels, while AES levels rely on AEAD decrypt and length bounds. Missing a `data_blob_clear()` style cleanup can leak plaintext.
- `_samr_SetUserInfo()` performs many mutations inside a root block, including operations that can call UNIX password sync; failures midway can leave passdb and UNIX password state partially updated depending on backend semantics.
- Some SAMR operations are intentionally unimplemented and return RPC op-range faults. Compatibility-sensitive clients may rely on exact status/fault behavior.
- `_samr_RemoveMemberFromForeignDomain()` is effectively a no-op for the observed BUILTIN use case and warns for others; nested group behavior is noted as incomplete.
- Display-size calculations use fixed structure-size approximations for Windows compatibility rather than exact encoded sizes.

## Test Signals

Useful tests should exercise RPC-level access and status behavior: connect/open-domain rights, BUILTIN versus local SAM domain handling, user/group/alias enumeration with resume handles, display-info pagination and cache invalidation after mutations, object security query/set for password-change ACL behavior, user create/rename/delete paths, group and alias membership updates, account-policy query/set round trips, and unsupported opnum faults. Password tests should cover weak-crypto policy denial, RC4 info levels 23-26, AES info levels 31-32 and ChangePasswordUser4, complexity failures, min-length failures, bad-password counter updates, account lockout, trust-account UNIX-sync bypass, and plaintext cleanup where instrumentation exists.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_util.c -->
# Research: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_util.c

## Purpose

`srv_samr_util.c` implements SAMR utility routines that copy SAMR user information structures into Samba passdb `struct samu` records. It is the normalization layer behind many `_samr_SetUserInfo()` levels in `srv_samr_nt.c`: narrow info levels are converted into a synthetic `samr_UserInfo21` with the right `fields_present` mask, then `copy_id21_to_sam_passwd()` applies only the requested fields.

## Important APIs, Types, and Functions

- `copy_id2_to_sam_passwd()` through `copy_id18_to_sam_passwd()`: wrap smaller SAMR info levels and delegate to `copy_id21_to_sam_passwd()`.
- `copy_id20_to_sam_passwd()`: handles user parameters separately by base64-encoding the binary parameter blob into passdb `munged_dial`.
- `copy_id21_to_sam_passwd()`: central field copier for `samr_UserInfo21`. It updates timestamps, strings, primary group, account flags, logon hours, counters, expiration behavior, country code, and code page.
- `copy_id23_to_sam_passwd()`, `copy_id25_to_sam_passwd()`, `copy_id32_to_sam_passwd()`: delegate nested `info` members to level 21 copying.
- `copy_id24_to_sam_passwd()` and `copy_pwd_expired_to_sam_passwd()`: update password-expired behavior through the level-21 expired flag path.
- `STRING_CHANGED` and `STRING_CHANGED_NC`: local macros used to avoid marking unchanged strings as modified; the `_NC` form tolerates NULL transitions.

## Control Flow

Most wrappers allocate a stack `samr_UserInfo21`, zero it, set `fields_present` and the few fields represented by their SAMR level, then call `copy_id21_to_sam_passwd()` with a log prefix. This keeps passdb mutation semantics centralized and avoids divergent handling of identical fields across info levels.

`copy_id21_to_sam_passwd()` checks each `SAMR_FIELD_*` bit before reading a field. For time fields it converts NT time to Unix time and updates passdb only if the stored value differs. For string fields it requires a non-NULL SAMR string pointer and compares against current passdb values before calling `pdb_set_*()` with `PDB_CHANGED`. For binary parameters it base64-encodes the SAMR binary string and stores it as `munged_dial`.

Primary RID changes are deliberately not applied; the function logs attempts to change user RID. Primary group RID changes are applied through `pdb_set_group_sid_from_rid()`. Account flag updates include special handling for `ACB_AUTOLOCK`: clients cannot newly set autolock through set-info, and clearing autolock resets bad-password counters and time. Password-expired changes set `pass_last_set_time` to zero for must-change only when password changes are allowed; clearing the flag may set the last-set time to `now` only when the existing password is considered expired.

Logon hours are copied as divisions, byte length, and bit array after comparing hex-rendered hour strings. Bad-password count and logon count are copied when present. Country code and code page are copied when present.

## State and Persistence Behavior

The functions mutate an in-memory `struct samu`; they do not write to passdb themselves except indirectly through passdb setter flags. Callers are responsible for later persistence with `pdb_update_sam_account()` and related group-update operations. Each setter uses `PDB_CHANGED` for actual changes, so passdb backends can decide which attributes to persist.

The only data transformation with a storage format is SAMR user parameters: binary `lsa_BinaryString` data is stored in passdb as base64 text in `munged_dial`, and empty blobs map to NULL/empty encoded state depending on caller input.

## Dependencies and Integration Points

The file depends on generated SAMR structures, passdb getter/setter APIs, base64 helpers, NT-time conversion helpers, account policy reads for password-expiration decisions, and Samba debug logging. It is directly included by `srv_samr_nt.c` through `srv_samr_util.h` for all user-info update paths.

## Risks and Edge Cases

- Fields are only applied if `fields_present` is set, and many string fields additionally require a non-NULL `.string`. A caller expecting NULL to clear a field will not get that behavior for most string fields.
- `copy_id21_to_sam_passwd()` mutates `from->acct_flags` by clearing `ACB_AUTOLOCK` in one branch, so callers should not treat the input structure as immutable afterward.
- Password-expired clearing uses current time and account policy to decide whether to update `pass_last_set_time`; subtle policy changes can affect wire-visible behavior.
- User RID changes are ignored by design, while primary group RID changes have real system consequences once callers persist and sync UNIX primary groups.
- Base64 parameter conversion asserts allocation success after `base64_encode_data_blob()`, which is consistent with local style but can abort in severe memory failure.

## Test Signals

Focused tests should verify each wrapper sets the expected `fields_present` subset, `copy_id21_to_sam_passwd()` persists only marked fields, unchanged strings do not mark passdb fields dirty, NULL strings are not treated as clears, primary RID changes are ignored, primary group RID changes are marked, autolock cannot be newly set but clearing it resets bad-password state, expired-flag behavior matches password policy, logon hours copy correctly, and binary parameters round trip through base64 storage.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_util.h -->
# Research: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_util.h

## Purpose

`srv_samr_util.h` declares the SAMR utility surface shared by the SAMR server implementation and adjacent password-change code. It exposes copy helpers for translating generated SAMR user-info levels into passdb `struct samu` records, plus password-change, password-complexity, and AES password-buffer helper declarations implemented in other SAMR source files.

## Important APIs, Types, and Functions

- Forward declaration `struct samu`: keeps the header lightweight while allowing passdb record pointers in prototypes.
- `copy_id*_to_sam_passwd()` and `copy_pwd_expired_to_sam_passwd()`: user-info-to-passdb field copy helpers implemented in `srv_samr_util.c`.
- `chgpasswd()`, `change_oem_password()`, and `pass_oem_change()`: password-change helpers implemented in `srv_samr_chgpasswd.c` and used by SAMR password change/set paths.
- `check_password_complexity_internal()` and `check_password_complexity()`: password policy/complexity hooks used by validation and change paths.
- `samr_set_password_aes()`: decrypts/validates AES-style SAMR encrypted password payloads into plaintext for newer password-change operations.

## Control Flow and Integration

This header does not implement control flow itself. It defines the stable contracts consumed primarily by `srv_samr_nt.c`: set-info operations call copy helpers before passdb persistence, password-change operations call OEM/plaintext/AES helpers, and validation paths call password complexity checks.

## State and Persistence Behavior

The header owns no state. Its declared copy helpers mutate caller-supplied `struct samu` instances; persistence remains a caller responsibility. The password-change declarations imply persistent updates through passdb and optional UNIX password sync in their implementations.

## Dependencies and Integration Points

The declarations use generated SAMR NDR types such as `struct samr_UserInfo21`, `enum samPwdChangeReason`, `struct samr_EncryptedPasswordAES`, and Samba `DATA_BLOB`/`NTSTATUS`/`TALLOC_CTX` types provided by surrounding includes in consumers. It is included by the SAMR RPC server file and the utility implementation.

## Risks and Edge Cases

- Because the header lacks its own include guard in the visible content, it depends on repository build conventions or surrounding generated include patterns to avoid duplicate declarations.
- The API surface mixes simple field-copy helpers with security-sensitive password helpers; callers must understand which functions only stage in-memory changes and which may perform persistent password changes.
- Generated SAMR type changes can break this header and all consumers because the prototypes use concrete generated structs.

## Test Signals

Build tests are the primary signal for this header: generated SAMR type compatibility, duplicate declaration handling, and consumer compile coverage. Functional tests should indirectly cover each declared helper through `_samr_SetUserInfo()`, password-change RPCs, and password validation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/iremotewinspool_util.c -->
# Research: sources/user-network-fs/samba/source3/rpc_server/spoolss/iremotewinspool_util.c

## Purpose

`iremotewinspool_util.c` provides a compact translation table from MS-RPRN `IRemoteWinspool` async opcodes to Samba's existing `spoolss` NDR opcodes. It lets the server proxy or dispatch supported async winspool calls through the corresponding synchronous or extended spoolss operation identifiers.

## Important APIs, Types, and Functions

- `_PAR_MAPPING(NAME)`: maps `NDR_WINSPOOL_ASYNC##NAME` to `NDR_SPOOLSS_##NAME`.
- `_PAR_MAPPING_EX(NAME)`: maps to an `EX` spoolss opcode, used where the async API corresponds to an extended spoolss call such as `OPENPRINTEREX`.
- `_PAR_MAPPING_2(NAME)`: maps to a `2` spoolss opcode, used for `GETPRINTERDRIVER2`.
- `proxy_table[]`: static opcode mapping table grouped by protocol sections: printer management, driver management, port management, processor management, monitor management, form management, job management, job printing, named job properties, and branch-office logging.
- `iremotewinspool_map_opcode(uint16_t opcode, uint16_t *proxy_opcode)`: linear lookup that writes the mapped spoolss opcode and returns `true`, or returns `false` for unsupported opcodes.

## Control Flow

Callers pass an incoming IRemoteWinspool opcode to `iremotewinspool_map_opcode()`. The function iterates over `proxy_table` using `ARRAY_SIZE()`. On the first matching `iremotewinspool_opcode`, it stores the mapped `spoolss_opcode` in `*proxy_opcode` and returns `true`. If no entry matches, it leaves the output untouched and returns `false`.

The mapping is intentionally explicit. Comments mark async methods that have no mapping, so unsupported methods fail closed at lookup time instead of accidentally dispatching to a wrong spoolss operation.

## State and Persistence Behavior

The file has no persistent state and no dynamic allocation. `proxy_table` is process-static read-only data after initialization. The only mutation is the caller-provided `proxy_opcode` output pointer on successful lookup.

## Dependencies and Integration Points

The file depends on generated `ndr_winspool.h` and `ndr_spoolss.h` constants and exposes its function through `rpc_server/spoolss/iremotewinspool_util.h`. Its integration point is the spoolss/IRemoteWinspool RPC dispatch path that needs to reuse existing spoolss handlers.

## Risks and Edge Cases

- The lookup is O(n), acceptable for the small table but still dependent on table completeness.
- The function does not NULL-check `proxy_opcode`; callers must pass a valid pointer when they expect a successful mapping.
- Generated opcode renames or additions require manual table updates. Unsupported methods are deliberately absent, so protocol expansion can manifest as false returns.
- The table stores opcodes in `int` but the public API uses `uint16_t`; this assumes generated NDR opcode constants fit in 16 bits.

## Test Signals

Tests should assert known mappings for regular, `EX`, and `2` variants; verify all explicitly unsupported methods return `false`; check that no table entry maps to an unintended spoolss opcode after generated NDR updates; and exercise caller behavior when `iremotewinspool_map_opcode()` fails.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/iremotewinspool_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/iremotewinspool_util.h -->
# Research: sources/user-network-fs/samba/source3/rpc_server/spoolss/iremotewinspool_util.h

## Purpose

`iremotewinspool_util.h` declares the public opcode mapping helper for the IRemoteWinspool-to-spoolss bridge. It lets spoolss server code ask whether an incoming async winspool opcode has a corresponding spoolss proxy opcode.

## Important APIs, Types, and Functions

- `bool iremotewinspool_map_opcode(uint16_t opcode, uint16_t *proxy_opcode)`: returns whether `opcode` is supported and, on success, writes the mapped spoolss opcode through `proxy_opcode`.

## Control Flow and Integration

The header has no implementation logic. It is included by `iremotewinspool_util.c` and by dispatch/proxy code that needs the mapper. Consumers should call the function before attempting proxy dispatch and treat `false` as unsupported.

## State and Persistence Behavior

The header declares a stateless lookup API. There is no ownership transfer or allocation implied by the signature. The only output is the scalar `proxy_opcode`.

## Dependencies and Integration Points

The header relies on surrounding Samba includes for `bool` and `uint16_t`. Its single declaration integrates the IRemoteWinspool async interface with the existing spoolss RPC opcode namespace.

## Risks and Edge Cases

- There is no visible include guard in the file, so duplicate inclusion depends on build conventions or consumer include structure.
- The function contract does not specify behavior for a NULL `proxy_opcode`; consumers should not pass NULL.
- Because the header does not include generated opcode definitions, it remains lightweight but gives no compile-time linkage to the exact constants mapped by the implementation.

## Test Signals

Compile coverage should ensure the declaration is visible to all dispatch consumers. Functional coverage belongs with the implementation: known opcode success, unsupported opcode failure, and caller fallback behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/iremotewinspool_util.h -->
