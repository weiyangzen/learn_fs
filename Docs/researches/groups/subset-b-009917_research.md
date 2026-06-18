# subset-b-009917 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_set.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_set.c

## Purpose

`schema_set.c` installs, caches, refreshes, and persists Samba AD DS schema metadata on an `ldb_context`. It bridges the in-memory `struct dsdb_schema` representation with LDB runtime behavior by setting attribute handler overrides, building sorted lookup arrays, writing special LDB control records such as `@ATTRIBUTES` and `@INDEXLIST`, and attaching schema pointers or refresh hooks as LDB opaque values. It also supports provision-time schema loading from LDIF text and a process-wide shared schema used to reduce memory duplication.

## Important APIs, Types, And Functions

The main public entry points are `dsdb_set_schema()`, `dsdb_reference_schema()`, `dsdb_set_global_schema()`, `dsdb_get_schema()`, `dsdb_make_schema_global()`, `dsdb_set_schema_refresh_function()`, `dsdb_schema_set_indices_and_attributes()`, `dsdb_schema_fill_extended_dn()`, `dsdb_schema_set_el_from_ldb_msg[_dups]()`, and `dsdb_set_schema_from_ldif()`. They operate on `struct dsdb_schema`, `struct dsdb_attribute`, `struct dsdb_class`, `struct ldb_context`, `struct ldb_message`, and `enum schema_set_enum`.

`dsdb_attribute_handler_override()` maps LDB attribute names to schema-provided `ldb_schema_attribute` handlers via `dsdb_attribute_by_lDAPDisplayName()`. `dsdb_setup_sorted_accessors()` rebuilds all schema fast lookup arrays after applying queued class/attribute removals. It sorts classes by LDAP display name, governs ID numeric and OID forms, and CN; it sorts attributes by LDAP display name, attribute ID numeric and OID forms, `msDS-IntId`, link ID, and CN. `dsdb_setup_attribute_shortcuts()` derives DN-format shortcuts, `one_way_link`, and `bl_maybe_invisible` backlink visibility flags.

## Control Flow

`dsdb_set_schema()` is the normal local install path. It first calls `dsdb_setup_sorted_accessors()` so all lookup helpers are coherent, clears the `dsdb_use_global_schema` marker, stores `dsdb_schema` as an LDB opaque, steals the schema under the LDB talloc tree, writes or compares schema-backed LDB records according to the requested mode, and finally unlinks the prior schema reference.

`dsdb_schema_set_indices_and_attributes()` has two phases. It always installs the LDB schema override and optional GUID index override, then returns early for `SCHEMA_MEMORY_ONLY`. In write/compare modes it builds desired `@ATTRIBUTES` and `@INDEXLIST` messages, populates syntax approximations and indexed attributes, compares them against existing records with `ldb_msg_difference()`, and adds or modifies only when needed. `SCHEMA_COMPARE` avoids writes and reports `LDB_ERR_BUSY` if changes would be required outside an expected transaction.

`dsdb_get_schema()` chooses the current schema from either the global schema or the LDB opaque, optionally calls a registered refresh callback with recursion protection, and returns either the existing pointer or a talloc reference under the caller's context.

Provision-time loading in `dsdb_set_schema_from_ldif()` creates a new schema, marks its FSMO state as locally writable, loads prefix map and schemaInfo from one LDIF string, iterates class and attribute LDIF records from another string, installs the schema, and then rewrites default object category DNs with GUID extended components.

## State And Persistence Behavior

Persistent state is written into LDB special records. `@ATTRIBUTES` stores simplified per-attribute syntax hints such as `INTEGER`, `ORDERED_INTEGER`, and `CASE_INSENSITIVE` for bootstrap and schema-less operation. `@INDEXLIST` stores `@IDXONE`, optional GUID indexing keys, `@SAMDB_INDEXING_VERSION`, `SAMBA_FEATURES_SUPPORTED_FLAG`, and `@IDXATTR` entries for indexed non-confidential attributes. Confidential attributes are deliberately omitted from index declarations to avoid timing differences in search behavior.

Runtime state is held in LDB opaque values: `dsdb_schema`, `dsdb_use_global_schema`, `dsdb_schema_refresh_fn`, and `dsdb_schema_refresh_fn_private_data`. The file also owns the static `global_schema` pointer, reparented to the null talloc context by `dsdb_make_schema_global()`.

The `loadparm` option `dsdb:guid index` controls GUID index declaration. The `pack_format_override` opaque can suppress `ORDERED_INTEGER` declaration so older packing formats can be opened for downgrade scenarios without forcing old Samba versions to reject the database.

## Dependencies And Integration Points

This file is tightly integrated with LDB (`ldb_set_opaque`, `ldb_schema_attribute_set_override_handler`, `ldb_search`, `ldb_add`, `dsdb_modify`, `ldb_msg_difference`), talloc lifetime management, Samba schema helpers (`dsdb_attribute_by_*`, `dsdb_class_by_*`, `schema_fill_constructed`, LDIF schema loaders), loadparm configuration, NDR/GUID helpers, and linked-list utilities. It is used by provision, schema replication/loading, and DSDB modules needing current schema lookup or refresh.

## Risks And Edge Cases

Index persistence is security-sensitive: confidential attributes must remain excluded from `@IDXATTR`, and the `ORDERED_INTEGER` downgrade path intentionally writes less precise metadata. Incorrect changes can trigger reindexing, break older database compatibility, or expose timing differences. Global schema lifetime is process-wide and depends on careful talloc unlink/reference handling. `dsdb_get_schema()` logs fatal debug messages when refresh fails but falls back to the previous schema, so callers must not assume refresh success. `dsdb_schema_fill_extended_dn()` assumes default object category RDNs resolve to schema classes and fails hard on missing targets.

## Test Signals

Useful coverage comes from schema provision tests, DSDB module tests that load schemas, database upgrade/downgrade tests around indexing records, and replication tests that require `dsdb_get_schema()` refresh behavior. Direct assertions should check that sorted accessors are rebuilt after removals, confidential indexed attributes are omitted, GUID index toggles work, and `SCHEMA_COMPARE` refuses required writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_syntax.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/schema_syntax.c

## Purpose

`schema_syntax.c` defines Samba's DSDB schema syntax map and the conversion/validation routines that translate attribute values between local LDB representation and DRSUAPI replication wire blobs. It is the central compatibility layer for Active Directory syntaxes: booleans, integers, large integers, UTC/generalized time, octet strings, OID references, Unicode strings, DN values, DN-binary/DN-string values, OR-Name, presentation addresses, security descriptors, and selected unsupported placeholder syntaxes.

## Important APIs, Types, And Functions

Public APIs include `dsdb_syntax_ctx_init()`, `dsdb_attribute_get_attid()`, `find_syntax_map_by_ad_oid()`, `find_syntax_map_by_ad_syntax()`, `find_syntax_map_by_standard_oid()`, `dsdb_syntax_for_attribute()`, `dsdb_attribute_drsuapi_remote_to_local()`, and `dsdb_attribute_drsuapi_to_ldb()`.

The key data structure is the static `dsdb_syntaxes[]` table. Each `struct dsdb_syntax` row binds an AD syntax tuple (`ldap_oid`, `oMSyntax`, `oMObjectClass`, `attributeSyntax_oid`) to handler callbacks: `drsuapi_to_ldb`, `ldb_to_drsuapi`, and `validate_ldb`. Several rows also define LDB matching rules, comments, `ldb_syntax`, `userParameters`, and `auto_normalise` behavior.

Major internal handler families are `dsdb_syntax_BOOL_*`, `INT32_*`, `INT64_*`, `NTTIME_UTC_*`, `NTTIME_*`, `DATA_BLOB_*`, `OID_*`, `UNICODE_*`, `DN_*`, `DN_BINARY_*`, `DN_STRING_*`, and `PRESENTATION_ADDRESS_*`. `dsdb_syntax_attid_from_remote_attid()` maps remote ATTIDs through a remote prefix map to the local prefix map. `dsdb_syntax_DN_validate_one_val()` is shared validation for DN-like syntaxes.

## Control Flow

Callers normally create a `struct dsdb_syntax_ctx` with `dsdb_syntax_ctx_init()`, optionally set `pfm_remote` for replication from another DC, locate a `struct dsdb_attribute`, then invoke the syntax callback in `attr->syntax`. `dsdb_attribute_drsuapi_to_ldb()` packages that common inbound replication path: initialize context, map the incoming remote ATTID to a local schema attribute, and dispatch to `sa->syntax->drsuapi_to_ldb()`.

Each conversion family follows the same pattern. DRS-to-LDB handlers allocate an `ldb_message_element`, copy the attribute display name, allocate output `ldb_val` slots, validate each incoming blob pointer and size, decode little-endian or NDR data, and write local values. LDB-to-DRSUAPI handlers reject `DRSUAPI_ATTID_INVALID`, set `out->attid` with `dsdb_attribute_get_attid()`, allocate `drsuapi_DsAttributeValue` and backing blobs, encode each LDB value, and attach the blob pointer. Validation handlers check invalid schema attributes, empty values where prohibited, numeric parsing, range bounds, string conversion, DN structure, or round-trip convertibility.

OID conversion is context-sensitive. Some attributes represent class references, some attribute references, and some raw numeric OIDs. `dsdb_syntax_OID_drsuapi_to_ldb()` switches on known ATTIDs and falls back to automatic class/attribute/OID handling. When `schema->relax_OID_conversions` is set during schema acquisition, conversion failures can fall back to raw OID decoding so an incoming schema can be loaded before all referenced definitions are known.

DN conversion uses DRSUAPI object identifier NDR structures. The code preserves GUID and SID extended DN components, rejects RootDSE links, filters extended components so only GUID and SID are accepted, and distinguishes normal DN, binary DN, and string DN formats through `dsdb_dn_parse()` and `dsdb_dn_construct()`.

## State And Persistence Behavior

The file does not persist data directly. Its state is per-call allocation under caller-provided talloc contexts and schema-derived lookup state. The important durable effect is the format of values written into LDB or sent over replication: integers and times are textual in LDB and fixed-width little-endian blobs in DRSUAPI; Unicode strings are converted between Unix charset and UTF-16; DNs preserve extended GUID/SID components; OID references may be stored as LDAP display names or numeric OID strings depending on attribute semantics.

`dsdb_attribute_get_attid()` controls whether an outbound replicated attribute uses `attributeID_id` or `msDS-IntId`, depending on schema NC replication and the presence of `msDS-IntId`.

## Dependencies And Integration Points

This file depends on generated DRSUAPI/NDR structures, LDB value and DN APIs, Samba charset conversion, prefix map helpers, schema lookup helpers, ASN.1 BER OID helpers, NTTIME conversion utilities, GUID/SID extended DN helpers, and talloc memory ownership. It is used by replication encode/decode paths, schema loading, attribute validation, and syntax selection during schema object construction.

## Risks And Edge Cases

Handler behavior is wire-format sensitive. Blob size checks must remain exact for fixed-width values, and time conversion special-cases the zero timestamp as `16010101000000.0Z`. OID handlers depend on complete and correct prefix maps; remote-to-local mapping failures intentionally return schema errors. DN validation has a subtle memory/error-handling risk: after `ldb_dn_copy()`, the code checks `dn == NULL` rather than the copy pointer, so allocation failure of `dn2` could surface later as a generic syntax failure path. Some syntaxes deliberately use `FOOBAR` placeholders or generic blob behavior for rarely used AD syntaxes, which is a compatibility boundary. Range validation for time casts to `int32_t`, so attributes with wide time ranges need care.

## Test Signals

The companion torture tests in `source4/dsdb/schema/tests/schema_syntax.c` verify representative round trips for DN, DN-BINARY, OR-Name, INT32, INT64, NTTIME, BOOL, and Unicode. Additional high-value tests would cover invalid blobs, empty values, range bounds, remote prefix map conversion, relaxed OID conversion during schema replication, DN values with unsupported extended components, and `msDS-IntId` outbound ATTID selection outside the schema NC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/schema_syntax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/tests/schema_syntax.c -->
# sources/user-network-fs/samba/source4/dsdb/schema/tests/schema_syntax.c

## Purpose

`tests/schema_syntax.c` defines the local torture suite `dsdb.syntax`, which regression-tests selected DSDB syntax conversion callbacks by round-tripping known DRSUAPI wire blobs through LDB values and back. It focuses on representative Active Directory schema syntaxes that are easy to corrupt during replication compatibility changes.

## Important APIs, Types, And Functions

The local fixture type is `struct torture_dsdb_syntax`, holding a provisioned `ldb_context` and its `dsdb_schema`. `hexstr_to_data_blob()` converts hexadecimal test vectors to binary blobs. `torture_syntax_add_OR_Name()` injects an Exchange-like `authOrig` attribute with Object(OR-Name) syntax into the loaded schema so OR-Name conversion can be tested.

`torture_test_syntax()` is the shared assertion helper. It locates the syntax by standard OID, resolves the named schema attribute, asserts that the attribute uses the expected syntax, converts the DRS value to an LDB message element, compares the result to the expected LDB string, validates the LDB form, converts back to DRSUAPI, and compares the output blob to the original binary vector.

Individual test functions cover DN-BINARY, DN, OR-Name, INT32, INT64, NTTIME, BOOL, and UNICODE. `torture_dsdb_syntax_tcase_setup()` loads a provisioned schema via `provision_get_schema()`, obtains it with `dsdb_get_schema()`, and installs `authOrig`. `torture_dsdb_syntax()` registers the test case fixture and simple tests.

## Control Flow

The suite setup creates `priv`, loads the schema from disk-backed provision helpers, fetches the schema from the LDB opaque state, and mutates the schema by adding the OR-Name attribute. Each test passes a syntax OID, attribute display name, expected LDB string, and expected DRS hex string into the shared round-trip helper. Teardown unlinks the LDB from the fixture and frees the fixture context.

DN and DN-BINARY tests include extended GUID and SID components, so they exercise the NDR object identifier paths in `schema_syntax.c`. The OR-Name test reuses the DN-binary DRS encoding path but validates that the schema row maps to the OR-Name syntax and accepts the expected LDB DN form. The Unicode test includes accented text to verify UTF-16 to local charset conversion and back.

## State And Persistence Behavior

The tests allocate all state under torture/talloc contexts and do not persist database mutations beyond the fixture lifetime. The fixture does call `dsdb_set_schema(..., SCHEMA_WRITE)` after adding the synthetic `authOrig` attribute, so it exercises the same schema install path used by production code, including sorted accessor rebuilds and schema special record handling on the test LDB.

## Dependencies And Integration Points

The suite depends on Samba torture APIs, provision schema loading, LDB LDIF parsing, DSDB schema lookup/install APIs, DRSUAPI syntax callbacks, and binary assertion helpers. It is an integration-style test rather than a pure unit test because it relies on a real provisioned schema and actual syntax table lookups.

## Risks And Edge Cases

Coverage is intentionally narrow: the tests verify valid round trips but do not assert invalid syntax rejection, range checks, empty blob handling, remote prefix map translation, relaxed OID behavior, or outbound `msDS-IntId` selection. Test vectors are hard-coded, so changes in canonical DN linearization, charset behavior, or schema fixture content can break expected strings even when conversion semantics are otherwise acceptable. The synthetic OR-Name attribute must remain consistent with the syntax table's `oMSyntax`, `oMObjectClass`, and `attributeSyntax` matching logic.

## Test Signals

Passing this suite indicates that the selected syntax callbacks preserve byte-for-byte DRS representations through an LDB round trip for common AD cases. Failures point directly to syntax selection, DRS blob decoding/encoding, LDB validation, provision schema availability, or schema mutation via `dsdb_set_schema()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/schema/tests/schema_syntax.c -->
