# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kcreddb.h

## Purpose

This header declares the NetIDMgr credentials database (KCDB) API. It covers identities, identity-provider callbacks, credential sets, individual credentials, attribute data types, attribute registration, credential type registration, generic record access, time/string conversion helpers, and KCDB notification operation constants.

## Important APIs, Types, and Functions

- Common limits include max name and description lengths and `KCDB_CBSIZE_AUTO`.
- Identity definitions include valid-name limits/chars, identity flags (`DEFAULT`, `SEARCHABLE`, `HIDDEN`, `VALID`, `INVALID`, `EXPIRED`, `EMPTY`, `RENEWABLE`, `INTERACT`, credential-derived flags, `STICKY`, and internal/config/activity flags), `kcdb_ident_name_xfer`, and `kcdb_ident_info`.
- Identity-provider APIs include `kcdb_identpro_validate_name`, `kcdb_identpro_validate_identity`, `kcdb_identpro_canon_name`, `kcdb_identpro_compare_name`, `kcdb_identpro_set_default`, `kcdb_identpro_set_searchable`, `kcdb_identpro_update`, `kcdb_identpro_get_ui_cb`, and `kcdb_identpro_notify_create`.
- Identity lifecycle and attributes include `kcdb_identity_create/delete`, `kcdb_identity_set_flags/get_flags`, `kcdb_identity_get_name`, `kcdb_identity_set_default`, `kcdb_identity_get_default`, `kcdb_identity_get_config`, `kcdb_identity_hold/release`, provider/type get/set APIs, equality, attribute/property get/set APIs, enumeration, and refresh.
- Credential-set callbacks and APIs include `kcdb_cred_apply_func`, `kcdb_cred_filter_func`, `kcdb_cred_comp_func`, `kcdb_credset_create/delete`, `collect`, `collect_filtered`, `flush`, `extract`, `extract_filtered`, `get_cred`, `find_filtered`, `find_cred`, delete/add by index/reference, `get_size`, `purge`, `apply`, `sort`, `seal`, and `unseal`.
- Credential definitions include credential flags (`DELETED`, `RENEWABLE`, `INITIAL`, `EXPIRED`, `INVALID`, `SELECTED`), `kcdb_cred_request`, and APIs for create, duplicate, update, attribute get/set, name, identity, serial, type, flags, hold/release/delete, compare attributes, and equality.
- Data type APIs define `kcdb_type`, conversion/validation/comparison/dup callbacks, type flags, registration/lookup, and built-in types (`VOID`, `STRING`, `DATE`, `INTERVAL`, `INT32`, `INT64`, `DATA`).
- Utility conversions cover `time_t` to/from `FILETIME` intervals, FILETIME arithmetic/comparison, interval string formatting/parsing, and ANSI/Unicode conversion.
- Attribute APIs define `kcdb_attrib`, computed attribute callbacks, registration/lookup/description/listing, flags (`REQUIRED`, `COMPUTED`, `SYSTEM`, `HIDDEN`, `PROPERTY`, `VOLATILE`, `ALTVIEW`, `TRANSIENT`), built-in attribute IDs, and names.
- Credential type APIs define `kcdb_credtype`, credential type ID ranges, `AUTO`, `ALL`, `INVALID`, registration, descriptor lifetime, name/description lookup, subscription lookup, and ID lookup.
- Generic buffer APIs let callers get/set attributes through a record handle for both identities and credentials.
- KCDB notification operation constants cover insert, delete, modify, activate/deactivate, hide/unhide, search flag changes, and new default identity.

## Control Flow

KCDB clients typically create/open identities, create temporary credential sets while enumerating an external provider, populate credentials, then collect those credentials into the root credential store. `kcdb_credset_collect()` is the key synchronization path: it selects credentials by identity/type or filter, adds missing credentials, updates existing credentials with non-null fields, applies additive selected flags specially, and removes destination credentials absent from the source. UI-visible credentials live in the root store; non-root sets are temporary and generally do not emit notifications.

Identity operations validate and canonicalize through the registered identity provider, maintain reference-counted handles, and refresh flags from root credentials and provider status. Credential operations use record-like attributes typed through registered `kcdb_type` handlers. Credential and identity handles must be held/released explicitly. Credential sets can be sealed to make them temporarily read-only, including sealed selected-credential snapshots in UI contexts.

## State and Persistence Behavior

The KCDB maintains in-memory identities, credentials, root credential store, registered data types, registered attributes, registered credential types, provider subscription state, and default identity state. Identity configuration can persist through `kcdb_identity_get_config()` and the configuration provider. Credentials themselves appear in-memory and provider-fed; persistence of actual external credentials is owned by providers. Deleted identities and credentials are marked inactive/deleted and are removed once references are released.

## Dependencies and Integration Points

Depends on `<khdefs.h>`, `<time.h>`, Windows `FILETIME`, message/subscription handles, configuration APIs, identity provider messages, and UI code. It is the central integration contract between NetIDMgr core, credential providers, identity providers, UI selection/action logic, and plugin-defined credential/attribute types.

## Risks

- `kcdb_identity_set_flags()` is explicitly non-atomic; callers must re-read flags after failures.
- `kcdb_credset_collect()` can delete all root-store credentials not present in a source set if called with wildcard identity/type, making filter correctness critical.
- Credential-set iteration can race with concurrent modifications and may not exhaustively cover or uniquely return matches across repeated calls.
- Reference lifetimes are strict: released handles must not be re-held, and descriptor handles from get-info APIs require matching release calls.
- Computed/volatile/transient attributes have non-obvious update semantics; missing transient attributes remove destination values during updates.
- Type and attribute callbacks must validate buffer sizes correctly, especially with `KCDB_CBSIZE_AUTO`.
- Credential type count is capped by `KCDB_CREDTYPE_MAX_ID`; plugins must unregister on unload.

## Test Signals

Tests should cover identity name validation/canonicalization, create/open/delete, default identity transitions, provider absence behavior, reference hold/release discipline, identity config creation, flag side effects, and identity refresh. Credential tests should cover temporary set creation, collect/add/update/delete deltas, wildcard safety, filters, seal/unseal behavior, purge of deleted entries, sort ordering, credential equality, attribute set/get by ID and name, computed and transient attributes, type/attribute/credtype registration lifecycle, time conversion helpers, and root-store notification emission.
