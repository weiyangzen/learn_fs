# Research Group subset-b-009911

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/password_hash.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/password_hash.c

## Purpose

`password_hash.c` implements Samba AD DS's `password_hash` LDB module. It intercepts add and modify requests for password-bearing account objects, validates password operation semantics, applies domain and fine-grained password policy, derives all persisted password material, and rewrites the request into internal updates for `unicodePwd`, `dBCSPwd`, `ntPwdHistory`, `lmPwdHistory`, `supplementalCredentials`, and `pwdLastSet`.

The module bridges LDAP-facing password attributes (`unicodePwd`, `userPassword`, `clearTextPassword`, `dBCSPwd`) and internal AD storage. It understands the distinction between a user password change and an administrative reset, honors Samba-specific controls, enforces encrypted LDAP password modification, and emits status/audit side effects. It sits after ACL/samldb in the Samba DSDB module stack and before replication metadata/objectclass attribute processing, so its generated password fields become the authoritative values that later modules persist and replicate.

## Important APIs, Types, And Functions

Core request state is held in `struct ph_context`. It tracks the LDB module/request, asynchronous domain/PSO/self-search replies, the derived update message, password status and change controls, configured `password hash gpg key ids`, configured `password hash userPassword schemes`, and flags such as `pwd_reset`, `hash_values`, `update_password`, `smartcard_reset`, `pwd_last_set_bypass`, and `kdc_reset_smartcard_account_password`.

Password transformation state is held in `struct setup_password_fields_io`. It records account metadata (`userAccountControl`, `pwdLastSet`, `sAMAccountName`, UPN, SID, krbtgt detection, whether to store the NT hash), new and old supplied credentials, existing stored credentials and Kerberos key material, and generated outputs. Generated outputs include NT hash/history, salt, AES and DES Kerberos keys, supplementalCredentials blob, and final `pwdLastSet`.

Request entry points are `password_hash_add()`, `password_hash_modify()`, `password_hash_module_init()`, and exported `ldb_password_hash_module_init()`. `password_hash_needed()` is the shared gate that decides whether processing is needed, handles `DSDB_CONTROL_BYPASS_PASSWORD_HASH_OID`, rejects direct manipulation of password history and supplemental credentials, initializes `ph_context`, applies controls, and creates `ac->update_msg` with original password attributes stripped.

Password material generation is split into helpers:

- `setup_given_passwords()` converts UTF-8/UTF-16 cleartext forms and computes MD4 NT hashes.
- `setup_kerberos_key_hash()` computes an AES256 key for supplied old/new cleartext against the old salt for verification/history comparison.
- `setup_kerberos_keys()` derives the new Kerberos salt and AES keys and creates random DES key placeholders.
- `setup_nt_fields()` chooses whether to persist the NT hash and builds NT password history.
- `setup_primary_kerberos()` and `setup_primary_kerberos_newer()` build the older DES-only and newer AES/DES Kerberos supplemental packages while carrying forward old key slots.
- `setup_primary_wdigest()` builds the WDigest package when weak crypto is allowed.
- `setup_primary_userPassword()` and `setup_primary_userPassword_hash()` build configured `{CRYPT}` SHA-crypt userPassword supplemental hashes.
- `setup_primary_samba_gpg()` optionally encrypts cleartext UTF-16 into a SambaGPG supplemental package when GPGME is enabled and keys are configured.
- `setup_supplemental_field()` assembles `Primary:Kerberos-Newer-Keys`, `Primary:Kerberos`, `Primary:WDigest`, `Primary:CLEARTEXT`, `Primary:userPassword`, `Primary:SambaGPG`, and `Packages` into one NDR `supplementalCredentials` value.

Policy and final update helpers include `setup_last_set_field()`, `setup_password_fields()`, `setup_smartcard_reset()`, `check_password_restrictions()`, `check_password_restrictions_and_log()`, `make_error_and_update_badPwdCount()`, and `update_final_msg()`.

Parsing/control helpers include `msg_find_old_and_new_pwd_val()`, `setup_io()`, `ph_init_context()`, `ph_apply_controls()`, `get_domain_data_callback()`, `build_domain_data_request()`, `get_pso_data_callback()`, and `build_pso_data_request()`.

## Control Flow

For add requests, `password_hash_add()` calls `password_hash_needed()`. If no password, `pwdLastSet`, or relevant UAC smart-card control is present, the request passes through. If processing is needed, non-user/non-inetOrgPerson objects pass through except `clearTextPassword` is rejected. Valid account adds perform a base search of the domain object via `build_domain_data_request()`. When `get_domain_data_callback()` receives the domain policy and done reply, it calls `password_hash_add_do_add()`, which initializes setup state from the client add message, generates/validates fields, logs LDAP password-change outcomes where applicable, applies smart-card reset state, populates `ac->update_msg`, and sends a rewritten add request downstream with `ph_op_callback()`.

For modify requests, `password_hash_modify()` first calls `password_hash_needed()`. It then separates password operations from all other attribute modifications. Non-password modifications are sent downstream first through a modified request and `ph_modify_callback()`. After that succeeds, or if no other modifications existed, `password_hash_mod_search_self()` rereads the target object. `ph_mod_search_callback()` validates object class and stores the base-search result, then queries domain policy. Domain callback optionally follows `msDS-ResultantPSO` through `build_pso_data_request()` so fine-grained password policy can override domain defaults. Finally `password_hash_mod_do_mod()` initializes from the client message plus existing object, generates/validates derived fields, and sends the final forced metadata password modify.

Operation semantics are intentionally strict. `msg_find_old_and_new_pwd_val()` identifies old values from delete elements and new values from add/replace elements. A password change is represented by one delete and one add; a reset is represented by replace or add-without-delete. `password_hash_modify()` rejects mixed change/reset forms, duplicate add/delete operations, and malformed multi-valued password attribute operations. `setup_io()` further rejects mixed cleartext/hash input forms, simultaneous UTF-8 and UTF-16 password values, direct NT hash writes without `DSDB_CONTROL_PASSWORD_HASH_VALUES_OID`, LM hash changes, deleting passwords, and inconsistent old-password mechanisms.

`check_password_restrictions()` runs after generated key material exists. It refuses unencrypted LDAP password modification when DSDB's encrypted-connection opaque says the connection is not encrypted. It verifies old-password knowledge for user changes unless a trusted control already proved it. It updates badPwdCount in its own transaction when the old password is wrong. It applies min age, complexity/length via `samdb_check_password()`, current password/history reuse checks using AES and NT history, old Kerberos key history checks by kvno, domain "refuse password change", and `UF_PASSWD_CANT_CHANGE`. Resets can skip some restrictions unless policy hints request reset-as-change behavior.

## State And Persistence Behavior

The module persists derived password state by rewriting LDB add/modify messages rather than writing directly to storage. `update_final_msg()` forces metadata updates for password attributes by adding empty elements with `DSDB_FLAG_INTERNAL_FORCE_META_DATA`, then fills generated values. On password update it always empties `dBCSPwd` and `lmPwdHistory`, reflecting Samba's no-LM-hash behavior. It stores `unicodePwd` only if `io->g.nt_hash` exists; NT hash persistence depends on `nt hash store` policy but is forced for non-normal accounts because machine/trust style flows need NETLOGON behavior. It stores `ntPwdHistory` when configured and enough material exists.

`supplementalCredentials` is regenerated from cleartext input, including Kerberos packages and optional weak/cleartext/GPG/userPassword packages. Functional level controls whether AES "newer keys" are produced. The old supplemental blob is parsed to preserve old/older Kerberos key slots where possible. The `Primary:SambaGPG` package is intentionally last when generated because package ordering is used as a current-password signal.

`pwdLastSet` is limited to `0` or `-1` unless bypass control is used. `-1` is replaced by the current DSDB/GMSA time. Adds always store the value. Modifies avoid no-op updates when appropriate. Setting `UF_SMARTCARD_REQUIRED` can suppress implicit `pwdLastSet` changes until the generated random password update is enabled by `setup_smartcard_reset()`.

Bad-password lockout state is a special side effect. On old-password mismatch, `make_error_and_update_badPwdCount()` aborts the current transaction, starts a short transaction to reread the account by GUID and call `dsdb_update_bad_pwd_count()`, closes it, and reopens the outer transaction so the failure returned to callers does not roll back the badPwdCount update.

## Dependencies And Integration Points

The module depends on LDB module APIs, DSDB/SAMDB helpers, Samba loadparm, security SID helpers, Heimdal/MIT Kerberos wrappers, GnuTLS hashing, MD4, generated NDR structures for supplemental credential packages, optional GPGME, auth logging, messaging, and KDC glue helpers.

Important controls are `DSDB_CONTROL_BYPASS_PASSWORD_HASH_OID`, `DSDB_CONTROL_PASSWORD_HASH_VALUES_OID`, `DSDB_CONTROL_PASSWORD_CHANGE_STATUS_OID`, `DSDB_CONTROL_PASSWORD_CHANGE_OLD_PW_CHECKED_OID`, `DSDB_CONTROL_PASSWORD_BYPASS_LAST_SET_OID`, `DSDB_CONTROL_PASSWORD_DEFAULT_LAST_SET_OID`, `DSDB_CONTROL_PASSWORD_USER_ACCOUNT_CONTROL_OID`, `DSDB_CONTROL_PASSWORD_KDC_RESET_SMARTCARD_ACCOUNT_PASSWORD`, `DSDB_CONTROL_PASSWORD_ACL_VALIDATION_OID`, `DSDB_CONTROL_RESTORE_TOMBSTONE_OID`, and policy hints OIDs. `password_hash_module_init()` registers the policy hints controls.

The `DSDB_PASSWORD_ATTRIBUTES` macro from `source4/dsdb/common/util.h` defines the password-facing attributes consumed here: `userPassword`, `clearTextPassword`, `unicodePwd`, and `dBCSPwd`. `samba_dsdb.c` places `password_hash` after `samldb` and before `instancetype`/`objectclass_attrs`. The ACL module validates password access and can pass reset/change classification through `DSDB_CONTROL_PASSWORD_ACL_VALIDATION_OID`.

The `dsdb/common/util.c` password-setting helpers use `DSDB_CONTROL_PASSWORD_HASH_VALUES_OID` and `DSDB_CONTROL_PASSWORD_CHANGE_STATUS_OID`, and DRS/import/pdb paths can use bypass controls. KDC and gMSA code reference the module's expectations for supplied random passwords for smart-card account reset/rollover paths.

## Risks And Edge Cases

This is a high-risk security module. Regressions can leak cleartext material, persist incompatible supplementalCredentials, weaken policy enforcement, break Kerberos/NTLM authentication, corrupt password history, or misclassify password reset/change authorization.

Notable edge cases include the heuristic that treats quoted UTF-16 `unicodePwd` as cleartext but unquoted 16-byte data as an NT hash when hash-values control is present; the comment acknowledges a very small collision possibility. Direct bypass accepts internally supplied hashes but performs extensive structural validation of histories and supplemental packages; any missed invariant could permit invalid replicated state. `parse_scheme()` checks SHA-crypt schemes and rounds, but its SHA-512 branch compares using `strlen(SHA_256_SCHEME)`, which is worth preserving tests around because it can affect scheme parsing. Configured userPassword scheme count is not bounded or uniqueness-checked.

The code mixes security policy, crypto derivation, and asynchronous LDB sequencing. Transaction manipulation for badPwdCount is intentionally unusual and error handling logs but preserves the original password failure. Smart-card and krbtgt randomization bypass user-supplied password material, so tests must ensure the final update really contains generated secrets and no stale history. GPGME support has build-time behavior differences and requires valid key IDs of at least 64 bits.

## Test Signals

Samba selftest explicitly lists `samba.tests.password_hash_gpgme`, `samba.tests.password_hash_fl2008`, `samba.tests.password_hash_fl2003`, and `samba.tests.password_hash_ldap`, covering GPG availability, functional-level differences, and LDAP WDigest/userPassword behavior. Broader password policy signals are in `source4/dsdb/tests/python/passwords.py`, including password change/reset constraints, max/min age commentary, NTLM-disabled knownfail cases, and LDAP password flows. ACL/password integration should also exercise `source4/dsdb/samdb/ldb_modules/acl.c` paths for password controls.

Regression tests should cover: add with and without initial password, modify split between non-password and password changes, replace vs delete/add classification, encrypted LDAP requirement, old-password mismatch and badPwdCount persistence, policy hints reset-as-change behavior, PSO overrides, NT hash store modes, krbtgt and RODC krbtgt random reset, smart-card required transition, functional level 2003 vs 2008 supplemental packages, weak crypto WDigest gating, configured userPassword SHA-crypt schemes and bad rounds, GPGME enabled/disabled, bypass validation of imported hashes, and `pwdLastSet` bypass/default controls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/password_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/password_modules.h -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/password_modules.h

## Purpose

`password_modules.h` is a tiny shared header for Samba DSDB password-related LDB modules. It defines `LOCAL_BASE` as `"cn=Passwords"`, documenting the local base DN under which these modules store password-related records.

## Important APIs, Types, And Functions

The file exposes one preprocessor constant:

- `LOCAL_BASE`: a string literal with the DN component `cn=Passwords`.

It does not define functions, structures, include guards, or include other headers.

## Control Flow

There is no runtime control flow. The header only contributes a compile-time symbol to modules that include it. In this subset, `password_hash.c` includes the header but does not reference `LOCAL_BASE` directly.

## State And Persistence Behavior

The header itself persists no state. Its value is a naming contract for password module storage layout. Code that uses `LOCAL_BASE` would align local password data under `cn=Passwords`, but this file does not implement the storage or enforce the DN.

## Dependencies And Integration Points

The direct integration point is any DSDB password module that includes this header. Its path under `source4/dsdb/samdb/ldb_modules/` and name suggest shared use by modules that manage local password objects. Because it lacks include guards, it is safe only for simple repeated identical macro definition contexts or one-shot inclusion.

## Risks And Edge Cases

The main risk is accidental drift: changing `LOCAL_BASE` changes a storage namespace contract for consumers. Lack of include guards is unusual but currently harmless for this single macro; if future declarations are added, guards should be introduced. The file comment says "We store these passwords under this base DN", but this subset does not show active use, so maintainers should verify consumers before changing it.

## Test Signals

There are no file-specific tests for the header. Signals should come from modules that store or look up password records using `LOCAL_BASE`. A build catches syntax-level regressions. Integration tests would need to verify password-module local DN layout if a consumer uses this macro.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/password_modules.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/proxy.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/proxy.c

## Purpose

`proxy.c` implements an LDB module named `proxy` that can forward selected search requests from the local database to an upstream LDB/LDAP server. It reads an `@PROXYINFO` control record containing upstream URL, credential, old/new base DNs, and string rewrite lists. Searches under the configured local base are translated to the upstream base, executed synchronously, then returned records are rewritten back into the local namespace.

The source comment explicitly describes the module as an investigation hack for MMC support, so it should be treated as legacy/experimental code rather than a hardened general proxy layer.

## Important APIs, Types, And Functions

`struct proxy_data` is module-private persistent state. It holds the upstream `ldb_context`, configured old and new base DNs, and old/new string rewrite lists. `struct proxy_ctx` is per-request callback state containing the module and original request, plus an optional debug count.

Key functions:

- `load_proxy_info()` lazily loads `@PROXYINFO`, initializes `proxy->upstream`, configures credentials, parses DN/string rewrite settings, and connects upstream.
- `proxy_convert_blob()` replaces the first case-insensitive occurrence of one byte-string with another inside an `ldb_val`.
- `proxy_convert_value()` applies all configured old-to-new rewrites to a value.
- `proxy_convert_tree()` converts a search filter from local strings to upstream strings, currently returning after the first replacement.
- `proxy_convert_record()` rewrites result DNs from `olddn` to `newdn` and applies value rewrites to every attribute value.
- `proxy_search_callback()` handles upstream replies, converts entries, ignores referrals, and completes the original request.
- `proxy_search_bytree()` decides whether a search should be proxied, translates base DN/filter/attributes, builds an upstream search request, runs it, waits synchronously, and propagates upstream errors.
- `proxy_request()` dispatches search requests to `proxy_search_bytree()` and passes other operations through.
- `ldb_proxy_module_init()` registers the module.

## Control Flow

On every request, `proxy_request()` only intercepts `LDB_REQ_SEARCH`. `proxy_search_bytree()` passes through special/no-base searches and searches outside `proxy->newdn`. For eligible searches, it calls `load_proxy_info()` on demand. That function searches local base `@PROXYINFO`, extracts `url`, `olddn`, `newdn`, `username`, `password`, `oldstr`, and `newstr`, initializes an upstream LDB context using the current event context, guesses credentials from loadparm, sets the configured username/password, and connects to the URL.

For proxied searches, the module creates a per-request context, converts the filter from local strings to upstream strings, copies the local base DN, removes the local base components, appends the upstream base, builds an upstream search request with original scope/attrs/controls, and sends it to `proxy->upstream`. The code then calls `ldb_wait(..., LDB_WAIT_ALL)`, making the module effectively synchronous despite LDB callback plumbing.

`proxy_search_callback()` converts each upstream entry and sends it to the original request. Upstream referrals are ignored. On done, it completes the original request successfully. Errors complete the original request with upstream controls/response/error.

## State And Persistence Behavior

`proxy_data` is intended to cache upstream connection and rewrite configuration for the module lifetime. `load_proxy_info()` checks `proxy->upstream != NULL` to avoid reloading. On load failure it frees parsed DNs and upstream context and resets `proxy->upstream` to `NULL`.

The module does not persist new local records. It reads local configuration from `@PROXYINFO`, maintains an in-memory upstream connection, and streams converted upstream search results to callers. It does not implement add, modify, delete, rename, transaction, or init methods in this file.

## Dependencies And Integration Points

The module uses LDB core request/callback/build APIs, `ldb_module.h`, Samba credentials (`cli_credentials_init`, `cli_credentials_guess`, username/password setters), talloc, string-list helpers, and loadparm opaque data. Its configuration contract is the local `@PROXYINFO` record with attributes documented in the file header.

Integration is narrow: consumers must place the `proxy` module in an LDB module stack and provide an initialized `struct proxy_data` as module private data. The source shown does not include an `init_context` function that allocates that private data, so either another layer is expected to set it or this module is incomplete as standalone code.

## Risks And Edge Cases

The code has several correctness and robustness risks. `proxy_search_callback()` calls `ldb_module_get_private(module)` even though no `module` variable is in scope; it should use `ac->module`, so the shown source would not compile unless a macro or outer symbol unexpectedly exists. `proxy_search_bytree()` logs fields from `newreq` before `ldb_build_search_req_ex()` initializes it, another apparent bug. `proxy_convert_blob()` assumes the caller already found a match; if called with no match it would subtract a null pointer. It treats `ldb_val` as string data for `strcasestr()`, so binary or non-NUL-terminated values are unsafe. `proxy_convert_record()` has two identical loops over attribute values, apparently duplicating rewrite work rather than separately handling DN syntax.

Configuration validation is weak. The error message says `oldstr` and `newstr` are required, but the actual null check only requires URL, DNs, username, and password before calling `str_list_make()` on `oldstr`/`newstr`. The old/new rewrite lists are not checked for equal length. Filter conversion returns after one replacement, so multiple occurrences or multiple mappings are not fully rewritten. Upstream work is synchronous and can block the local LDB request path. Credentials are stored in an LDB control record and copied into memory.

## Test Signals

Searches for `@PROXYINFO` and `ldb_proxy` in the local tree show only this source file, so there are no obvious dedicated tests. Any meaningful test should construct an LDB stack with a valid `@PROXYINFO`, verify local-base searches are forwarded to a temporary upstream DB, verify DNs/filter strings/value strings are rewritten both directions, and verify non-search or out-of-base requests pass through. A compile/build test is important because the callback and logging issues are syntactic/compile-time signals in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/ranged_results.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/ranged_results.c

## Purpose

`ranged_results.c` implements the `ranged_results` LDB module. It supports Active Directory-style ranged attribute retrieval requests such as `member;range=0-1499` by asking lower modules for the full base attribute and then slicing the returned values before sending results to the client. This allows clients to request windows of a multi-valued attribute even when lower storage modules do not natively implement ranged result syntax.

## Important APIs, Types, And Functions

`struct rr_context` stores the original module/request and whether a dirsync control is present. Dirsync changes behavior because dirsync incremental-value handling interacts with ranged results.

Key functions:

- `rr_init_context()` allocates request context and records whether `LDB_CONTROL_DIRSYNC_OID` is present.
- `rr_search()` scans requested attributes for `;range=`, validates syntax, strips range suffixes into a new attribute list, and sends a rewritten downstream search.
- `rr_search_callback()` receives downstream replies, slices matching attributes for each entry, renames the returned attribute with the appropriate `;range=start-end` or `;range=start-*` suffix, and forwards entries/referrals/done replies.
- `ldb_ranged_results_module_init()` registers the module with `.search = rr_search`.

## Control Flow

`rr_search()` is invoked for search operations. It iterates over `req->op.search.attrs`, looking for the first semicolon in each attribute and accepting only `;range=` at that point. It parses either `start-*` or `start-end`. Malformed ranges and `start > end` return `LDB_ERR_UNWILLING_TO_PERFORM`. For each range request, it replaces the attribute name in `new_attrs` with the base attribute before the semicolon, preserving other attributes unchanged. If at least one ranged request was found, it builds a downstream search with the same base, scope, filter, controls, and stripped attribute list; otherwise it frees the temporary array and passes the original request onward.

`rr_search_callback()` passes referrals and done replies through. If dirsync is in use, it forwards entries without slicing because dirsync and ranged results have special interaction. Otherwise it loops over the original requested attributes, reparses range syntax, finds the base attribute in the returned message, computes the effective end index, copies only requested values into a newly allocated value array, and renames the attribute. If requested end reaches or exceeds the last available value, the returned name ends in `*`; if `start` is beyond the last available value, it returns the ranged attribute with zero values.

## State And Persistence Behavior

The module has no persistent storage. All state is per search request and owned by talloc contexts tied to the original request or reply message. It mutates the in-flight `ares->message` before forwarding it: `el->values`, `el->num_values`, and `el->name` are replaced for ranged attributes. It does not alter the underlying database.

## Dependencies And Integration Points

The module depends on LDB module APIs, talloc allocation, and `LDB_CONTROL_DIRSYNC_OID`. It is in the main Samba DSDB module stack before modules such as ANR/sort/asq according to `samba_dsdb.c`. The dirsync module marks or uses range-like attributes and comments that ranged_results must know how to behave when dirsync is active.

Client-visible integration is LDAP/AD ranged retrieval syntax. `source4/dsdb/tests/python/ldap.py` contains direct tests for `servicePrincipalName;range=0-*`, fixed ranges, beyond-end ranges returning `*`, and empty ranges past the end. `source4/dsdb/tests/python/dirsync.py` includes dirsync/range interaction cases for `member;range=...`.

## Risks And Edge Cases

The module assumes that a returned attribute's value order is suitable for slicing and that the full base attribute can be fetched before slicing, which can be expensive for very large attributes. It only checks for the first semicolon and requires `;range=` immediately there, so attributes with other options before range are ignored or passed through. It allocates a new values array sized `(end - start) + 1`; while it checks overflow for `start + end`, the size expression still depends on parsed unsigned arithmetic and effective end normalization.

The entry callback assumes `ac->req->op.search.attrs` is non-NULL when a range was found in `rr_search()`, which is valid for rewritten range requests but is a contract to preserve. Dirsync bypass returns full values when `dirsync_in_use`; changes in dirsync semantics could require revisiting this behavior. Returned values are shallow-copied `struct ldb_val`s from the original array, so lifetime must remain tied to the reply message, which is true in the current callback flow.

## Test Signals

Primary regression signals are the LDAP Python tests around `servicePrincipalName;range=...` and the dirsync Python tests around `member;range=...` with incremental values. Unit or integration tests should cover malformed ranges, `start > end`, `start-*`, exact last-value requests, request end beyond last value, start beyond last value, multiple ranged attributes in one request, mixed ranged and normal attributes, no attrs list, and dirsync control presence. Build registration is covered by the `ldb_ranged_results` module entry in `wscript_build_server`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/ranged_results.c -->
