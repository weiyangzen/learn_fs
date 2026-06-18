# subset-b-009915 Research

Grouped research for the listed Samba DSDB LDB module sources and tests. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_log.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_log.c

## Purpose
This cmocka test file directly includes `../audit_log.c` and validates the DSDB audit logging module's core event construction. It covers JSON and human-readable audit output for ordinary directory operations, password/key-credential changes, transaction lifecycle events, commit failures, replicated updates, transaction-id controls, attribute rendering, and system-session attribution.

## Important APIs, Types, And Functions
The test exercises internal audit APIs such as `has_password_changed`, `get_password_action`, `operation_json`, `password_change_json`, `transaction_json`, `commit_failure_json`, `replicated_update_json`, `operation_human_readable`, `password_change_human_readable`, `transaction_human_readable`, `commit_failure_human_readable`, `replicated_update_human_readable`, `add_transaction_id`, and `log_attributes`. Helpers `check_timestamp` and `check_version` enforce ISO-8601 timestamp ranges and schema version objects. The tests construct `struct ldb_context`, `struct ldb_module`, `struct ldb_request`, `struct ldb_reply`, `struct audit_private`, `struct auth_session_info`, `struct security_token`, `struct dsdb_extended_replicated_objects`, and `struct repsFromTo1`.

## Control Flow
Most cases allocate a temporary talloc context, initialize a minimal LDB/module, populate LDB opaques such as `remoteAddress`, `DSDB_SESSION_INFO`, or `DSDB_NETWORK_SESSION_INFO`, build request/reply structures, call the target formatter, and assert exact JSON fields or regex-matched human-readable lines. The password tests first classify whether request messages contain password-like attributes and whether ACL validation controls indicate reset versus change. Replication tests populate extended-operation data and verify source DSA, invocation ID, object/link counts, partition DN, LDB status, and WERROR text. Human-readable tests use regexes to ignore dynamic timestamps while pinning status, remote host, SID, DN, attributes, and duration text.

## State And Persistence Behavior
No durable state is written. All state is transient in talloc-owned objects and LDB opaque values. The transaction GUID is stored in `audit_private` and copied into a `DSDB_CONTROL_TRANSACTION_IDENTIFIER_OID` control by `add_transaction_id`. The timestamp checks depend on wall-clock time captured before invoking the formatter.

## Dependencies And Integration Points
The file depends on Samba LDB internals, DSDB audit utility helpers, JSON wrappers, security token/SID helpers, GUID parsing/formatting, socket address formatting, and regular expressions. It is an internal-unit style test because it includes the implementation C file rather than testing only the registered module interface.

## Risks
The tests assert exact event schemas, version numbers, event IDs, and log strings; intentional schema changes require coordinated test updates. Several tests manually construct partial LDB objects, so they may miss behavior that depends on a full module stack. There is a typo-like test attribute `planTextPassword`, but the test calls the formatter directly and is focused on event output rather than password-attribute detection.

## Test Signals
Passing tests signal that audit JSON contains expected root `type`, timestamp, version, status, transaction/session identifiers, DNs, attributes, and replication metadata, and that human-readable logs remain stable. Tamper or missing-context paths are covered through empty request/session cases and system-session cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_log_errors.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_log_errors.c

## Purpose
This companion cmocka file verifies error handling in `audit_log.c` JSON construction. It deliberately injects failures in JSON object creation, version insertion, and timestamp insertion to ensure audit formatter functions return invalid JSON rather than partially valid events.

## Important APIs, Types, And Functions
The file directly includes `../audit_log.c` and wraps `json_new_object`, `json_add_version`, and `json_add_timestamp` through linker-style cmocka wrappers. It targets `operation_json`, `password_change_json`, `transaction_json`, `commit_failure_json`, and `replicated_update_json`. Test fixtures build `struct ldb_context`, `struct ldb_module`, `struct ldb_request`, `struct ldb_reply`, `struct audit_private`, session/security token data, and replication structures.

## Control Flow
Each test first constructs enough request context for a happy-path formatter call. It then uses ordered `will_return` values to force a specific allocation or helper failure, calls the formatter, and asserts `json_is_invalid`. After the negative paths, it supplies successful wrapper returns and checks the formatter can still produce valid JSON.

## State And Persistence Behavior
All state is in-memory and scoped to talloc contexts. The wrapper functions use cmocka's mock queue as transient state. The tests do not exercise module transactions or persistent LDB storage.

## Dependencies And Integration Points
The test relies on cmocka wrapping support, Samba's JSON abstraction, LDB private structures, GUID/SID helpers, and DSDB replication types. It integrates with the same implementation functions as `test_audit_log.c` but focuses on failure propagation rather than field-level schema validation.

## Risks
The tests are sensitive to the number and order of JSON helper calls in the implementation; harmless refactors that allocate wrappers in a different order can break the mock sequence. Conversely, they cover only selected failure points, so errors after timestamp insertion or while adding later fields may need separate tests.

## Test Signals
Passing tests show that top-level audit JSON formatters fail closed when basic JSON infrastructure fails and still produce valid JSON on the happy path after mocked failures are cleared.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_log_errors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_util.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_util.c

## Purpose
This cmocka file directly includes `../audit_util.c` and validates shared helper behavior used by DSDB audit modules. It covers attribute/value JSON encoding, redaction, LDB/session metadata extraction, operation naming, DN extraction, remote address formatting, and modify-action naming.

## Important APIs, Types, And Functions
The tests call `dsdb_audit_add_ldb_value`, `dsdb_audit_attributes_json`, `dsdb_audit_get_remote_address`, `dsdb_audit_get_ldb_error_string`, `dsdb_audit_get_user_sid`, `dsdb_audit_get_actual_sid`, `dsdb_audit_is_system_session`, `dsdb_audit_get_unique_session_token`, `dsdb_audit_get_actual_unique_session_token`, `dsdb_audit_get_remote_host`, `dsdb_audit_get_primary_dn`, `dsdb_audit_get_message`, `dsdb_audit_get_secondary_dn`, `dsdb_audit_get_operation_name`, `dsdb_audit_get_modification_action`, `dsdb_audit_is_password_attribute`, and `dsdb_audit_redact_attribute`.

## Control Flow
Value serialization tests feed null blobs, printable strings, non-printable data, exactly `MAX_LENGTH` data, and over-limit data into JSON arrays, asserting null encoding, base64 markers, truncation markers, and value contents. Attribute JSON tests compare add versus modify action labels and verify secret attributes are redacted. Session tests progressively populate LDB opaque session data and security tokens, checking null behavior, first-SID selection, system SID detection, and GUID extraction. Request tests switch `req->operation` across add, modify, delete, rename, extended, register-control, register-partition, and unknown cases to validate DN/message/operation helpers.

## State And Persistence Behavior
The file creates only transient LDB contexts, modules, requests, messages, socket addresses, auth sessions, and JSON objects. LDB opaque slots such as `remoteAddress`, `DSDB_SESSION_INFO`, and `DSDB_NETWORK_SESSION_INFO` are the key state carriers.

## Dependencies And Integration Points
It depends on Samba JSON helpers, talloc, LDB private request structures, socket address formatting, SID/GUID helpers, and the audit utility implementation. These helpers are integration points for both general audit logging and group audit logging.

## Risks
The value-formatting tests lock in truncation and base64 behavior; changing `MAX_LENGTH` or printable-character rules affects audit consumers. Session tests reveal a subtle behavior: a zeroed `auth_session_info` can still yield a non-null unique session token pointer with undefined contents, which callers must treat carefully.

## Test Signals
Passing tests signal that audit helpers produce stable JSON for attribute data, redact sensitive attributes, correctly derive request DNs and names, and tolerate absent session/remote metadata without crashing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_encrypted_secrets.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_encrypted_secrets.c

## Purpose
This cmocka file directly includes `../encrypted_secrets.c` under `TEST_ENCRYPTED_SECRETS` and validates encrypted secret handling for Samba's secrets database module. It covers key-file loading, AES-GCM value encryption/decryption, tamper detection, message-level secret-attribute encryption/decryption, header validation, and rejection of unencrypted secret attributes.

## Important APIs, Types, And Functions
The tests exercise `es_init`, `gnutls_encrypt_aead`, `gnutls_decrypt_aead`, `decrypt_value`, `encrypt_secret_attributes`, `decrypt_secret_attributes`, `check_header`, and `makeEncryptedSecret`. They use `struct es_data`, `struct EncryptedSecret`, `struct PlaintextSecret`, LDB messages/elements, `DATA_BLOB`, and constants such as `SECRETS_KEY_FILE`, `DSDB_SECRET_ATTRIBUTES`, `ENCRYPTED_SECRET_MAGIC_VALUE`, `SECRET_ATTRIBUTE_VERSION`, and `ENC_SECRET_AES_128_AEAD`.

## Control Flow
`setup` creates a temporary LDB module chain with an `eol` module, connects a local TDB database, and removes stale db/lock/key files. `setup_with_key` writes a 16-byte key file, inserts `@SAMBA_DSDB` required-feature metadata, and initializes the module. Key tests verify absent, exact-length, short, and long key files. Crypto tests decrypt a known static ciphertext, encrypt a value and NDR-decode the `EncryptedSecret`, then decrypt it. Tamper tests mutate header flags, ciphertext, and IV and expect `LDB_ERR_OPERATIONS_ERROR`. Message tests encrypt all `DSDB_SECRET_ATTRIBUTES`, confirm normal attributes remain plaintext, then decrypt back to original values.

## State And Persistence Behavior
The tests create and delete `apitest.ldb`, its lock file, and the secrets key file named by `SECRETS_KEY_FILE`. Module private state stores loaded keys, `encrypt_secrets`, and encryption algorithm. Encrypted message data is transient, but the tests model how the real module would persist encrypted secret attribute values in LDB.

## Dependencies And Integration Points
The file mocks `dsdb_module_search_dn` and `dsdb_module_reference_dn` so initialization sees the encrypted-secrets required feature without a full DSDB. It depends on GnuTLS AEAD behavior, NDR marshalling, Samba LDB module APIs, and talloc ownership.

## Risks
Key-file handling is security critical: short keys must fail, long keys are truncated to the first 16 bytes, and absent keys disable encryption. Any change in NDR wire layout, header constants, or AEAD algorithm will require test updates and migration consideration. Rejecting unencrypted secret attributes is a compatibility/security boundary.

## Test Signals
Passing tests show key loading is deterministic, encrypted values round-trip, malformed encrypted records fail, secret attributes are redacted by encryption while normal attributes stay readable, and static encrypted records remain decryptable with the expected key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_encrypted_secrets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_group_audit.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_group_audit.c

## Purpose
This cmocka file directly includes `../group_audit.c` and validates group membership audit event construction and diffing. It covers JSON and human-readable group-change output, transaction/session metadata, binary DN parsing/comparison, primary-group lookup, member add/remove detection, replication metadata delete flags, group-type to event-ID mapping, and failure audit generation.

## Important APIs, Types, And Functions
The tests exercise `get_transaction_id`, `audit_group_human_readable`, `audit_group_json`, `get_parsed_dns`, `dn_compare`, `get_primary_group_dn`, `log_membership_changes`, `get_add_member_event`, `get_remove_member_event`, and `log_group_membership_changes`. The file mocks `dsdb_search_one`, `dsdb_module_search_dn`, and `audit_message_send`, recording generated JSON messages for inspection.

## Control Flow
Setup helpers create minimal LDB/module state, register Samba DN handlers, set `remoteAddress`, install session SID/GUID data, and attach an `audit_context` with event sending enabled. JSON tests check the `groupChange` wrapper, timestamps, version, status, user, group, action, and optional event ID. Diff tests construct old and new `member` elements containing extended binary DNs; `log_membership_changes` compares parsed GUID/DN values and emits Added or Removed events. RMD flag tests cover logical deletion and undeletion transitions. `log_group_membership_changes` tests simulate post-operation readback of the new object, including groupType, and failure cases when the operation or readback fails.

## State And Persistence Behavior
The test state is in memory. Global mock variables capture the latest search base, scope, attributes, flags, format string, status, and result. `messages` and `messages_sent` hold deep-copied JSON audit messages. No real database records or messaging server state are persisted.

## Dependencies And Integration Points
The file depends on group audit internals, audit utility/session helpers, LDB extended DN parsing, Samba group type constants, security event IDs, JSON messaging, and DSDB search helpers. It integrates with the same audit-message path production code uses to send events through Samba messaging.

## Risks
Membership diffing is sensitive to extended DN parsing, GUID comparison, and RMD flag semantics; small changes can duplicate or suppress security audit events. The mock `audit_message_send` has a fixed capacity of 16 messages, which is enough for current cases but not a general stress test. Some tests use manually assembled `ldb_message_element` structures, so malformed real-world DNs require separate coverage.

## Test Signals
Passing tests show group membership additions/removals produce correct event IDs for local/global/universal and security/distribution groups, unchanged members are ignored, RMD flag transitions are interpreted correctly, and failure paths emit a `Failure` audit message instead of silently dropping context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_group_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_group_audit_errors.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_group_audit_errors.c

## Purpose
This companion file validates error handling for group audit JSON construction in `group_audit.c`. It injects failures in JSON infrastructure and checks that `audit_group_json` returns invalid JSON for each failed construction step.

## Important APIs, Types, And Functions
The file directly includes `../group_audit.c`, wraps `json_new_object`, `json_add_version`, and `json_add_timestamp`, and targets `audit_group_json`. Helpers build session data and transaction controls using `auth_session_info`, `security_token`, `dom_sid`, `GUID`, and `DSDB_CONTROL_TRANSACTION_IDENTIFIER_OID`.

## Control Flow
The test constructs an LDB context/module/request with remote address, session SID/GUID, and transaction GUID. It then forces failures at top-level JSON object creation, version insertion, wrapper creation, and timestamp insertion, asserting `json_is_invalid` each time. A final mock sequence allows all helpers to succeed and asserts the returned object is valid.

## State And Persistence Behavior
All state is transient in talloc allocations and cmocka mock queues. No LDB database or messaging state is created.

## Dependencies And Integration Points
The file depends on cmocka's wrapper/mock mechanism, Samba JSON helpers, LDB request controls, GUID/SID conversion, and group audit internals. It complements `test_group_audit.c` by covering allocation/helper failure paths that are difficult to trigger naturally.

## Risks
The exact `will_return` ordering is coupled to implementation allocation order. The file only tests `audit_group_json`; failures in later send paths, membership diffing, or human-readable formatting are outside its scope.

## Test Signals
Passing tests show group audit JSON construction fails closed under basic JSON helper failures and remains valid on the normal path with the same contextual request data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_group_audit_errors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_unique_object_sids.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_unique_object_sids.c

## Purpose
This cmocka file directly includes `../unique_object_sids.c` and validates the LDB module that forces unique-index checking for local-domain `objectSID` values. It ensures local object SIDs are flagged, foreign or missing SIDs pass through, and direct non-replicated `objectSID` modification is rejected.

## Important APIs, Types, And Functions
The tests exercise `unique_object_sids_init`, `unique_object_sids_add`, `unique_object_sids_modify`, and helper behavior behind `message_contains_local_objectSID` and `flag_objectSID`. It mocks `ldb_next_request` to record `last_request` and uses `add_sid` to NDR-encode textual SIDs into `objectSID` values.

## Control Flow
`setup` creates an LDB context, installs `cache.domain_sid`, builds a two-module chain ending in an `eol` module, connects a TDB file, and initializes the module. Add tests build `ldb_build_add_req` requests with local, foreign, or absent `objectSID` values. Modify tests build `ldb_build_mod_req` requests and optionally attach `DSDB_CONTROL_REPLICATED_UPDATE_OID`. Assertions verify whether the original request or a copied request reached the next module and whether `LDB_FLAG_INTERNAL_FORCE_UNIQUE_INDEX` was set only on the copied `objectSID` element.

## State And Persistence Behavior
Tests create and delete `duptest.ldb` and its lock file. The module private state stores the local domain SID discovered through `samdb_domain_sid`. `last_request` is global test state capturing the request passed down the module chain.

## Dependencies And Integration Points
The file depends on Samba LDB modules, NDR SID marshalling, `dom_sid_in_domain`, DSDB replicated-update controls, and TDB-backed LDB setup. It is tightly coupled to the production module's request-copying behavior.

## Risks
The production boundary is important: local `objectSID` uniqueness cannot be enforced by a plain unique index because foreign principals and replication-conflict records may duplicate SIDs. The tests also reveal a likely copy/paste issue in assertions for modify paths that inspect `last_request->op.add.message` and `request->op.add.message` after building modify requests; the underlying union layout may make this work in practice, but it is fragile test code.

## Test Signals
Passing tests show local-domain SIDs get `LDB_FLAG_INTERNAL_FORCE_UNIQUE_INDEX`, foreign and missing SIDs are untouched, original requests are not mutated when flags are added, replicated updates may modify local object SIDs, and ordinary local objectSID modifies fail with `LDB_ERR_UNWILLING_TO_PERFORM`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_unique_object_sids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tombstone_reanimate.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tombstone_reanimate.c

## Purpose
This LDB module implements Active Directory tombstone reanimation. It recognizes a special modify request that deletes `isDeleted` and replaces `distinguishedName`, restores attributes required for live objects, then renames the deleted object to its requested DN.

## Important APIs, Types, And Functions
The central state type is `struct tr_context`, which carries the module, original request/message, search result/message, prepared modify request/result, prepared rename request/result, target rename DN, and DSDB schema. Key functions are `tr_init_context`, `is_tombstone_reanimate_request`, `tr_prepare_rename`, `tr_do_down_req`, `tr_prepare_attributes`, and `tombstone_reanimate_modify`. Module registration is through `ldb_tombstone_reanimate_module_init` and `ldb_reanimate_module_ops.modify`.

## Control Flow
`tombstone_reanimate_modify` ignores special DNs, then checks for the exact reanimation pattern: `distinguishedName` replace with one value and `isDeleted` delete. It loads the deleted object with `DSDB_SEARCH_SHOW_DELETED`, rejects objects that are not actually deleted, prepares a shallow modify message that removes `distinguishedName`, deletes `isRecycled`, restores user/group/objectCategory-related attributes, prepares a rename request to the new DN, runs the modify with `LDB_CONTROL_SHOW_DELETED_OID` and `DSDB_CONTROL_RESTORE_TOMBSTONE_OID`, then runs the rename with the same controls. Successful completion calls `ldb_module_done` on the original request.

## State And Persistence Behavior
The module itself keeps no long-lived private state. Persistent effects are the LDB modify and rename performed on the tombstoned object. The prepared restore modify may add or replace attributes such as `isRecycled`, user defaults, `sAMAccountType`, `primaryGroupID`, group `sAMAccountType`, `adminCount`, `operatorCount`, and `objectCategory`.

## Dependencies And Integration Points
It depends on DSDB schema access, deleted-object searches, user/group account helper functions, objectCategory generation, LDB controls for showing deleted objects, and the restore tombstone DSDB control. It integrates with modules below it by issuing synchronous down requests with explicit controls.

## Risks
The module relies on a strict request shape and assumes restored user/group attributes can be reconstructed from existing tombstone data. Missing `userAccountControl` or `groupType` causes operations errors. Rename failures are normalized to `LDB_ERR_OPERATIONS_ERROR` except for entry-exists and insufficient-access cases, so diagnostic detail can be reduced. The code performs modify before rename; a later rename failure leaves reliance on transaction semantics for rollback.

## Test Signals
This work item did not include a dedicated test file for tombstone reanimation. Useful test signals would include modifying a real deleted user/group tombstone, verifying required restore controls are present, checking attribute defaults, and confirming transaction rollback on rename failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tombstone_reanimate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/trust_notify.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/trust_notify.c

## Purpose
This LDB module tracks changes to trust-related directory data and notifies `winbind_server` at successful transaction commit so winbind can reload trusted-domain data.

## Important APIs, Types, And Functions
`struct trust_notify_private` holds a transaction-local `notify_winbind` flag. `trust_notify_has_watched_attrs` identifies changes to trust/crossRef attributes cached by winbind. `trust_notify_add`, `trust_notify_modify`, and `trust_notify_delete` decide whether to set the flag. Transaction hooks `trust_notify_start_trans`, `trust_notify_end_trans`, and `trust_notify_del_trans` reset, send, or clear notifications. `trust_notify_winbind_server` initializes an imessaging client, locates `winbind_server` with `irpc_servers_byname`, and sends `MSG_WINBIND_RELOAD_TRUSTED_DOMAINS`.

## Control Flow
Adds and modifies skip special DNs, check whether the incoming message contains watched attributes, set `notify_winbind`, then chain to the next module. Deletes skip special DNs, read the target object from the next module with recycled/internal/storage-format visibility, and set the flag if the object class is `trustedDomain` or `crossRef`. At transaction start or abort the flag is cleared. At transaction end, the module first commits downstream with `ldb_next_end_trans`; only on success does it send the reload message if the flag was set.

## State And Persistence Behavior
The module persists no database state. Its only state is the private `notify_winbind` boolean scoped to a transaction. Notification delivery is best-effort: missing loadparm, imessaging initialization failure, no winbind server, or send failure does not roll back the already successful LDB transaction.

## Dependencies And Integration Points
It depends on LDB module hooks, DSDB search helpers, Samba loadparm, imessaging/IRPC, server ID lookup, and the winbind reload message type. It integrates with trustedDomain, crossRefContainer, and crossRef attribute changes that affect winbind's trust cache.

## Risks
There is an apparent bug in `trust_notify_modify`: it calls `trust_notify_has_watched_attrs(req->op.add.message)` inside the modify handler, where `req->op.mod.message` is expected. That wrong union arm can produce incorrect behavior or unsafe access for modify requests. Notification is also not retried and only targets the first found `winbind_server`.

## Test Signals
No dedicated tests are included in this subset. Useful coverage would assert that add/modify watched attributes set the flag, non-watched changes do not, deletes of trustedDomain/crossRef objects notify, transaction abort clears the flag, and successful commit sends exactly one reload message. A modify test should specifically catch the wrong request union arm.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/trust_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/unique_object_sids.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/unique_object_sids.c

## Purpose
This LDB module enforces uniqueness for local-domain `objectSID` values by marking eligible `objectSID` elements with `LDB_FLAG_INTERNAL_FORCE_UNIQUE_INDEX`. It allows duplicate SIDs for foreign security principals and replication-conflict records, where duplicates are valid or tolerated.

## Important APIs, Types, And Functions
`struct private_data` stores the local domain SID. `message_contains_local_objectSID` decodes `objectSID` from a request message and checks it with `dom_sid_in_domain`. `flag_objectSID` shallow-copies a message and ORs the force-unique flag on the copied element. `unique_object_sids_add` and `unique_object_sids_modify` wrap add/modify requests when needed. `unique_object_sids_init` loads the domain SID from `samdb_domain_sid` and registers private data.

## Control Flow
On add, the module checks whether the message contains a local-domain objectSID. If not, it forwards the original request. If yes, it shallow-copies the message, flags the copied `objectSID`, builds a new add request with the original controls and callback, and passes the new request down. On modify, it performs the same local-SID detection but first requires `DSDB_CONTROL_REPLICATED_UPDATE_OID`; without that control it rejects the modify with `LDB_ERR_UNWILLING_TO_PERFORM`. Initialization calls `ldb_next_init`, allocates private data, and logs a warning if the domain SID is unavailable, as can happen during provisioning.

## State And Persistence Behavior
Persistent database effects are indirect: the forced unique-index flag influences lower LDB/index behavior for local objectSID values. The module itself stores only the local domain SID pointer in private data and does not modify the original request message.

## Dependencies And Integration Points
It depends on Samba SID parsing helpers, `samdb_result_dom_sid`, `samdb_domain_sid`, LDB request builders, DSDB callbacks, and the replicated-update control. It integrates with lower database/index modules that interpret `LDB_FLAG_INTERNAL_FORCE_UNIQUE_INDEX`.

## Risks
If the domain SID is unavailable, local uniqueness enforcement is disabled with only a warning. Because the message copy is shallow, the element structure is copied but underlying values are shared; this is intentional for flag mutation but ownership must remain valid for the request lifetime. Non-replicated objectSID modification is blocked to preserve integrity, so callers that legitimately need SID changes must use the replication path.

## Test Signals
`test_unique_object_sids.c` covers local versus foreign SIDs, missing objectSID pass-through, request-copy behavior, original-request immutability, replicated modify success, and non-replicated modify rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/unique_object_sids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/update_keytab.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/update_keytab.c

## Purpose
This LDB module updates Kerberos keytab files when matching `kerberosSecret` records with `privateKeytab` change. It records affected secret entries during add/modify/delete/rename operations and performs keytab updates during transaction prepare.

## Important APIs, Types, And Functions
`struct dn_list` stores changed secret messages and whether the keytab should be deleted. `struct update_kt_private` holds the transaction list. `struct update_kt_ctx` tracks an individual operation, target DN, delete mode, operation reply, and search result flag. Key functions are `add_modified`, `update_kt_op_callback`, `ukt_search_modified_callback`, `ukt_search_modified`, `ukt_del_op`, `update_kt_add`, `update_kt_modify`, `update_kt_delete`, `update_kt_rename`, `update_kt_prepare_commit`, `update_kt_del_trans`, and `update_kt_init`.

## Control Flow
Add/modify/rename first build and forward the corresponding downstream request. Once the operation completes successfully, `update_kt_op_callback` searches the affected DN for `(&(objectClass=kerberosSecret)(privateKeytab=*))`; if found, `add_modified` synchronously reads the full matching entry and appends it to `changed_dns`. Delete first searches the target before issuing the delete, records it if it is a matching secret, then performs the delete. During prepare commit, the module initializes a Kerberos context, walks `changed_dns`, builds realm-qualified SPN strings, derives the keytab name from the message, and calls `smb_krb5_update_keytab` with account name, realm, SPNs, salt principal, current/prior secrets, KVNO, supported encryption types, and delete flag. It then chains to `ldb_next_prepare_commit`.

## State And Persistence Behavior
The module's persistent side effect is external to LDB: it creates, updates, or deletes keytab contents. In-memory transaction state is `changed_dns`, cleared after successful prepare or on failure/transaction abort. The LDB operation itself is delegated to lower modules; keytab mutation happens at prepare-commit time so failures can abort the transaction before final commit.

## Dependencies And Integration Points
It depends on LDB asynchronous request/callback APIs, DSDB search helpers, Kerberos initialization, Samba credentials/keytab helpers, `keytab_name_from_msg`, loadparm, and secrets record attributes such as `realm`, `servicePrincipalName`, `sAMAccountName`, `saltPrincipal`, `secret`, `priorSecret`, `msDS-KeyVersionNumber`, and `msDS-SupportedEncryptionTypes`.

## Risks
The source explicitly notes "too many semi-async searches" and that `cli_credentials_set_secrets()` performs synchronous LDB searches, so callback ordering/backend behavior is a concern. Keytab update failure clears accumulated state and returns `LDB_ERR_OPERATIONS_ERROR`, which should abort the transaction but also means a partial external keytab mutation may need operational recovery if multiple entries were processed. Realm handling assumes `realm` is present when SPNs need realm qualification.

## Test Signals
No dedicated tests are listed in this subset. Useful signals would cover add/modify/rename/delete of matching and non-matching entries, prepare-commit keytab update arguments, abort cleanup, Kerberos init failure, per-entry update failure, SPN realm formatting, and delete-mode keytab removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/update_keytab.c -->
