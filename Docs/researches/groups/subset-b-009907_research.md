# subset-b-009907 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/replicated_objects.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/replicated_objects.c

## Purpose
`replicated_objects.c` converts DRS replication wire objects into Samba DSDB/LDB messages and commits them transactionally. It is the bridge between `drsuapi_DsReplicaObjectListItemEx` / linked-attribute replication data and the local `DSDB_EXTENDED_REPLICATED_OBJECTS_OID` extended operation. It also builds temporary "working schema" views needed while the schema naming context is itself being replicated.

## Important APIs, types, and functions
- `dsdb_repl_make_working_schema()` shallow-copies the current schema, merges the remote prefix map, and resolves incoming schema objects into a temporary schema cache.
- `dsdb_repl_resolve_working_schema()` performs multi-pass conversion of replicated schema objects, retrying objects whose dependencies are not yet available.
- `dsdb_convert_object_ex()` validates one replicated object, decrypts secret attributes, converts DRS attributes to LDB elements, builds `replPropertyMetaDataBlob`, validates RDN/name consistency, adjusts partial replica `instanceType`, and returns a `dsdb_extended_replicated_object`.
- `dsdb_replicated_objects_convert()` converts a full replication response, including linked attributes, source DSA state, uptodateness vector, partition DN, and replication flags into `dsdb_extended_replicated_objects`.
- `dsdb_replicated_objects_commit()` wraps application of converted objects in an LDB transaction, swaps in a working schema while needed, runs schema validation, commits, updates notify USN behavior, and reloads the committed schema.
- `dsdb_origin_objects_commit()` handles originating object adds for non-Ex `drsuapi_DsReplicaObjectListItem`, optionally creating partial replica NCs before adds.

Key data types include `dsdb_schema`, `dsdb_schema_prefixmap`, `drsuapi_DsReplicaObjectListItemEx`, `drsuapi_DsReplicaLinkedAttribute`, `dsdb_extended_replicated_object`, `dsdb_extended_replicated_objects`, and `replPropertyMetaDataBlob`.

## Control flow
Schema replication starts with `dsdb_repl_make_working_schema()`: copy the initial schema, mark resolving in progress, decode the remote prefix map, merge missing OID prefixes into the local copy, and call `dsdb_repl_resolve_working_schema()`. Resolution builds a linked list of incoming schema objects and repeatedly tries `dsdb_convert_object_ex()` plus `dsdb_schema_set_el_from_ldb_msg_dups()`. When a pass succeeds for at least one object, it removes those list entries; when no object can be converted, it fails to avoid an infinite loop. After enough progress, it switches from the initial/bootstrap schema to the resulting schema and rebuilds sorted schema accessors.

Normal object conversion starts in `dsdb_replicated_objects_convert()`. It references the schema into the output lifetime, decodes the remote prefix map, checks remote schema compatibility when not replicating the schema NC, then iterates the DRS object linked list. Each object is converted by `dsdb_convert_object_ex()`. Objects outside the requested partition that are NC heads are ignored with `WERR_DS_ADD_REPLICA_INHIBITED`; all other conversion failures abort the batch. The function then deep-copies linked attributes enough for local ownership, translates remote ATTIDs to local ATTIDs, and returns the prepared extended operation payload.

Commit uses `ldb_transaction_start()`, records the partition USN before apply, optionally installs the working schema into the LDB context, and calls `ldb_extended(... DSDB_EXTENDED_REPLICATED_OBJECTS_OID ...)`. For schema replication it writes the new prefix map to LDB and uses `DSDB_EXTENDED_SCHEMA_LOAD` before `ldb_transaction_prepare_commit()` to catch corrupt schema writes within the same transaction. After commit it suppresses notification USN advancement only when the inbound apply caused originating updates or an earlier notification was already pending, then reloads/makes global the schema as appropriate.

## State and persistence behavior
The conversion layer allocates output trees with talloc ownership under the returned `dsdb_extended_replicated_objects`. Converted messages hold DNs, attribute elements, `when_changed`, parent GUIDs, object GUIDs, replication flags, source DSA pointers, uptodateness vectors, and linked attributes. Persistent database changes happen only in commit functions: replicated objects are applied by the DSDB extended operation inside an LDB transaction; schema prefix map updates are written before transaction prepare; originating objects are added with relaxed controls inside their own transaction and then re-read for assigned GUID/SID output.

Working schema state is deliberately memory-only during conversion and commit. The previous schema reference/global schema mode is restored on failures. After a successful schema commit, the schema is reloaded from the database rather than continuing to use the working copy.

## Dependencies and integration points
This file depends on DRSUAPI generated NDR types, DSDB schema helpers, prefix-map helpers, DRS attribute decrypt/convert helpers, LDB transactions/extended operations, security key material for secret decryption, and partition USN helpers. It integrates with `repl_meta_data`/DSDB extended operations via `DSDB_EXTENDED_REPLICATED_OBJECTS_OID`, with schema reload via `DSDB_EXTENDED_SCHEMA_LOAD`, and with notification logic through the caller-supplied `notify_uSN`.

## Risks and edge cases
- Input validation is strict: missing identifiers, missing DNs, metadata count mismatches, duplicate/missing `instanceType`, zero originating invocation IDs, and RDN/name mismatches all fail.
- Secret handling relies on `drsuapi_decrypt_attribute()` and treats `WERR_TOO_MANY_SECRETS` as suspicious server behavior.
- Prefix-map conversion is critical because stored replication metadata must contain local ATTIDs, not remote host-specific ATTIDs.
- Partial replica handling removes `INSTANCE_TYPE_WRITE`; read-write replication rejects sources that do not advertise writeable objects.
- Schema commit has many restore paths; any future change must preserve previous schema restoration on all transaction failures.
- The code tolerates duplicate schema objects by keeping the last resolved schema element, but a no-progress pass is fatal.

## Test signals
Relevant tests should exercise inbound replication of normal objects, schema NC replication with interdependent class/attribute ordering, remote prefix-map changes, linked attribute ATTID conversion, RODC/partial replica `instanceType` behavior, object outside partition skipping, zero invocation ID rejection, RDN/name mismatch rejection, transaction rollback on extended operation failure, schema reload after commit, and originating object add/partial NC creation paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/replicated_objects.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb.pc.in -->
# sources/user-network-fs/samba/source4/dsdb/samdb.pc.in

## Purpose
`samdb.pc.in` is the pkg-config template for the Samba SAM database client library. During configuration, build variables are substituted so external or internal consumers can discover the include path, library path, version, linker flags, and compiler flags needed to compile against `libsamdb`.

## Important fields
- `prefix`, `exec_prefix`, `libdir`, and `includedir` are configure-time installation path substitutions.
- `Name`, `Description`, and `Version` identify the package as `samdb` / "Sam Database" using `@PACKAGE_VERSION@`.
- `Libs` emits `@LIB_RPATH@ -L${libdir} -lsamdb`, so consumers link to `libsamdb` and receive any configured runtime path flags.
- `Cflags` emits `-I${includedir} -DHAVE_IMMEDIATE_STRUCTURES=1`; the define is part of the ABI/headers expectation for immediate structure support.

## Control flow
There is no executable control flow. The build system substitutes Autoconf/Waf-style variables into this template and installs or stages the resulting `samdb.pc` file.

## State and persistence behavior
The generated `.pc` file persists build/install metadata. It does not mutate runtime state, but stale or incorrect substitutions can affect every downstream compile/link invocation that relies on pkg-config.

## Dependencies and integration points
It integrates with the Samba build configuration, `pkg-config`, and consumers of `libsamdb`. The link line assumes the library is installed under `${libdir}` with the name `samdb`; the include line assumes public headers under `${includedir}`.

## Risks and edge cases
- Incorrect `libdir`, `includedir`, or `LIB_RPATH` substitutions break downstream builds or runtime loading.
- Removing `HAVE_IMMEDIATE_STRUCTURES=1` may change header-visible structure behavior for consumers.
- The template does not list transitive private libraries; if static linking is expected elsewhere, companion build metadata may be needed.

## Test signals
Useful checks are build-system generation of `samdb.pc`, `pkg-config --cflags --libs samdb` in an installed/staged tree, compiling a small consumer against `samdb` headers, and verifying runtime lookup when `@LIB_RPATH@` is expected to carry nonstandard library paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/cracknames.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/cracknames.c

## Purpose
`cracknames.c` implements DRSUAPI `DsCrackNames()` style name translation for Samba AD DS. It converts between LDAP DNs, canonical names, NT4 names, GUIDs, display names, user principal names, service principal names, SIDs, and DNS-domain-like responses, and provides helper wrappers used by authentication/KDC code and DRS RPC handlers.

## Important APIs, types, and functions
- `DsCrackNameOneName()` is the central dispatcher. It builds domain and result LDAP filters for the offered format, handles syntactical-only requests, and delegates to `DsCrackNameOneFilter()`.
- `DsCrackNameOneFilter()` performs domain crossRef lookup, object search with the requested attributes, ambiguity handling, fallback for SPN aliases/UPN variants, and output formatting.
- `DsCrackNameOneSyntactical()` maps FQDN_1779 DNs to canonical or canonical-ex names without a database search.
- `DsCrackNameSPNAlias()` and `LDB_lookup_spn_alias()` implement service principal fallback through `sPNMappings` under `CN=Directory Service,CN=Windows NT,CN=Services,...`.
- `DsCrackNameUPN()` handles UPN fallback by parsing the Kerberos realm, locating the domain crossRef, and searching by unescaped `samAccountName`.
- `get_format_functional_filtering_param()` walks canonical path components to narrow searches for canonical/canonical-ex names.
- Public helpers include `crack_user_principal_name()`, `crack_service_principal_name()`, `crack_name_to_nt4_name()`, `crack_auto_name_to_nt4_name()`, `dcesrv_drsuapi_ListRoles()`, `dcesrv_drsuapi_CrackNamesByNameFormat()`, and `dcesrv_drsuapi_ListInfoServer()`.

Key types are `drsuapi_DsNameFormat`, `drsuapi_DsNameInfo1`, `drsuapi_DsNameCtr1`, `smb_krb5_context`, `ldb_context`, `ldb_dn`, `ldb_result`, `dom_sid`, and `GUID`.

## Control flow
For `DRSUAPI_DS_NAME_FORMAT_UNKNOWN`, `DsCrackNameOneName()` recursively tries a fixed ordered list of plausible formats and returns the first status that is not an ignorable not-found case. For known input formats, it parses the input and prepares a domain filter, a result filter, a direct DN, a search scope, and sometimes a Kerberos context. Canonical names split at `/` or newline, NT4 names split at `\`, GUID and SID formats are NDR-encoded for LDAP filters, display names search `displayName` or `samAccountName`, UPN/SPN formats use Kerberos parsing and LDAP-safe encoding.

`DsCrackNameOneFilter()` first resolves the domain crossRef when a domain filter exists. It then searches either all partitions for GCVERIFY/GUID, the resolved NC, the default NC, or a direct DN. Result count drives status: one result is formatted, zero may invoke SPN alias or UPN fallback, and multiple results usually become `NOT_UNIQUE` except canonical searches try exact canonical string matching before declaring ambiguity. Output formatting then returns the requested representation, including special handling for NT4 domain names, BUILTIN SIDs, canonical-ex synthesis, and single-valued SPN requirements.

The KDC-facing helpers crack UPN/SPN to FQDN_1779, validate status mapping to NTSTATUS, and optionally crack the DNS domain portion back to a domain DN. RPC entry points allocate result arrays and call the single-name cracker for each requested name.

## State and persistence behavior
This file does not persist directory state. It performs read-only LDB/DSDB searches and allocates result strings under caller-supplied talloc contexts. It may initialize Kerberos contexts and parse/free Kerberos principals. Status is returned in `drsuapi_DsNameInfo1` fields rather than by throwing errors for ordinary lookup failures.

## Dependencies and integration points
The implementation integrates with DRSUAPI RPC structures, LDB search APIs, DSDB search helpers and partition/crossRef layout, Kerberos principal parsing/unparsing, LDAP NDR encoders for GUID/SID filters, domain SID helpers, FSMO role helpers, and server/reference lookup for `ListInfoServer`. It is used by DRS RPC name cracking and by authentication/KDC paths that need to resolve principals to user/domain DNs.

## Risks and edge cases
- LDAP filter injection is mitigated by `ldb_binary_encode_string()` and NDR encoders; new formats must preserve that discipline.
- Kerberos unparsing flags intentionally use display/no-realm modes in specific cases so spaces and escaping match AD attributes.
- SPN alias behavior returns the first matching mapping and is documented as mirrored in `samldb.c`; changing ordering can break compatibility.
- Canonical parsing mutates temporary strings while walking path components and must distinguish domain-only from object searches.
- Result status semantics are subtle: many search or parse failures return `WERR_OK` with a DS name status, while internal allocation/configuration errors return WERROR failures.
- GUID searches include recycled objects and may search all partitions, which is important for deleted-object behavior.

## Test signals
Coverage should include each offered and desired format pair used by DRS clients, syntactical-only DN-to-canonical mapping, unknown-format fallback ordering, NT4 domain/user and BUILTIN handling, UPN with escaped spaces and alternate realm lookup, SPN host/computer fallback, SPN alias mappings, duplicate result `NOT_UNIQUE`, domain-only responses, GCVERIFY/all-partition search, SID/GUID encoding, KDC helper NTSTATUS mappings, `ListRoles`, and `ListInfoServer`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/cracknames.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl.c

## Purpose
`acl.c` is Samba's main DSDB LDB ACL enforcement module for write-side operations and selected search-time constructed attributes. It checks add, modify, delete, rename, and extended operations against the caller security token and object security descriptors, implements validated writes for sensitive attributes, handles password-change/reset ACL classification, and synthesizes AD-style constructed attributes such as `allowedAttributesEffective`.

## Important APIs, types, and functions
- `acl_module_init()` installs module private state, reads `acl:search`, and registers the SD flags control.
- Constructed attribute helpers: `acl_allowedAttributes()`, `acl_childClasses()`, `acl_childClassesEffective()`, and `acl_sDRightsEffective()`.
- Validated write helpers: `acl_check_spn()`, `acl_validate_spn_value()`, `acl_check_dns_host_name()`, `acl_check_ms_ds_key_credential_link()`, and `acl_check_self_membership()`.
- Operation gates: `acl_add()`, `acl_modify()`, `acl_delete()`, `acl_rename()`, `acl_extended()`, and `acl_search()`.
- Password flow: `acl_check_password_rights()`, `copy_password_acl_validation_control()`, and `acl_callback()`.
- Confidential search fallback: `acl_search_update_confidential_attrs()` and `acl_search_callback()`.

Main state structures are `acl_private` for module-level configuration and confidential-attribute cache, and `acl_context` for per-search state including requested constructed attributes, system/admin booleans, and schema pointer.

## Control flow
Initialization creates `acl_private`, stores whether `acl:search` is enabled, registers SD flags, then initializes the next module. Most operation handlers skip special DNs and callers with system access.

`acl_add()` determines the new object's structural class, checks create-child rights on either the parent or `CN=Partitions`/crossRef path for NC heads, then optionally performs per-attribute authorization using the calculated default security descriptor. Mandatory attributes and password attributes are treated specially. Computer-derived adds validate SPN, DNS host name, key credential link, self-membership, SACL privilege, and write-DAC/write-property rights against the default SD.

`acl_modify()` reads the target object's SD, object classes, and SID as system, then checks each modified attribute. It maps `nTSecurityDescriptor` SD flags to write-owner/write-DAC/system-security access, applies implicit-owner rules and computer-owner blocking, routes password attributes through `acl_check_password_rights()`, validates SPN/DNS/key credential changes, allows undelete-specific `isDeleted`, and otherwise requires write-property on the attribute. It wraps the downstream modify with `acl_callback()` so password ACL validation metadata is copied to the reply for audit logging.

`acl_delete()` forbids deleting NC roots, then accepts either delete-tree, delete-object on the object, or delete-child on the parent. `acl_rename()` forbids moving/renaming NC roots, handles tombstone reanimation via an extended right on the NC root, requires write-property on `name` and the old RDN attribute, and for moves requires create-child on the new parent plus delete-object or delete-child on the old location.

`acl_search()` is not the main read ACL path; it exists for constructed attributes and for confidential-attribute filter redaction when `acl:search` is disabled. It may rewrite confidential attributes in the parse tree to `kludgeACLredactedattribute`, then `acl_search_callback()` fills constructed attributes and strips confidential attributes from non-system/non-admin result entries.

`acl_extended()` only allows sequence-number reads to everyone. Other extended operations require system or administrator privileges.

## State and persistence behavior
The module itself persists no directory data directly; it authorizes or rejects requests before passing them down the LDB stack. It mutates request controls by marking handled controls non-critical and adds `DSDB_CONTROL_PASSWORD_ACL_VALIDATION_OID` for downstream password hashing/audit modules. Per-module state caches confidential attribute names keyed by schema pointer and metadata USN. Per-request talloc contexts own temporary SDs, schema data, search results, and callbacks.

## Dependencies and integration points
`acl.c` depends on DSDB schema lookup, SD parsing, `sec_access_check_ds` wrappers from `acl_util.c`, auth session tokens, objectclass sorting, validated-write extended rights under `CN=Extended-Rights`, Kerberos parsing for SPN validation, key credential NDR parsing, tombstone restore controls, calculated default SD controls, password hash/change controls, audit logging controls, and the surrounding LDB module stack.

## Risks and edge cases
- Validated writes are security-sensitive: SPN, DNS host name, self-membership, and key credential link checks must stay aligned with Windows semantics and objectclass constraints.
- Password modification classification is subtle and intentionally delegates malformed cases to `password_hash` by withholding the validation control.
- SD write checks depend on SD flags and implicit owner rights; computer-object blocking of owner implicit write-DAC is especially compatibility-sensitive.
- `DSDB_CONTROL_FORCE_ALLOW_VALIDATED_DNS_HOSTNAME_SPN_WRITE_OID` bypasses normal checks for selected updates and must remain tightly scoped.
- Constructed attribute generation performs extra system reads; missing schema or malformed objectClass/SD data becomes operational failure.
- Search-time confidential rewrite is a fallback when `acl_read` is not handling search ACLs; parser rewrites must avoid exposing confidential values through filters.

## Test signals
Useful tests include create-child and crossRef/NC-head add authorization, per-attribute add checks with calculated default SDs, SACL privilege enforcement, password change versus reset controls and audit response controls, SPN and DNS validated writes including deletes and DC-specific SPNs, `msDS-KeyCredentialLink` SELF/new-value constraints, self-membership modification, SD owner/DACL/SACL write flags, delete object/delete child/delete tree, rename versus move, tombstone reanimation right, constructed attributes for system/admin/non-admin callers, confidential attribute redaction when `acl:search` is disabled, and extended operation denial for non-admin callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl_read.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl_read.c

## Purpose
`acl_read.c` is the DSDB LDB module that enforces authorization on LDAP/search read results. It decides whether objects are visible, redacts attributes the caller cannot read, treats password/secret attributes as inaccessible, handles SD flag semantics, and registers a filter-redaction callback so inaccessible attributes used in search filters cannot be used as an oracle.

## Important APIs, types, and functions
- `aclread_search()` prepares downstream search requests by adding internal attributes needed for access checks and installing `DSDB_CONTROL_ACL_READ_OID`.
- `aclread_callback()` checks object visibility, attribute visibility, removes internally added attributes, and sends filtered entries.
- `aclread_check_object_visible()` and `aclread_check_parent()` implement List Children/List Object visibility semantics with a per-search parent cache.
- `aclread_get_sd_from_ldb_message()` parses and module-caches security descriptors by exact binary blob.
- `setup_access_check_context()` obtains schema, SD, structural class, and SID for per-attribute access checks.
- `acl_redact_attr()` checks secret/confidential/read-property access and marks inaccessible attributes.
- `acl_redact_msg_for_filter()` checks attributes referenced in a search parse tree before filter evaluation.
- `aclread_init()` loads secret/password attribute names from `@KLUDGEACL`, adds built-in secret attributes, sorts them, registers the redaction callback, and handles `userPassword` support.

Important structures are `aclread_context` for per-search state, `aclread_private` for module state and SD/password caches, `access_check_context`, and the sorted `ldb_attr_vec` used for filter attribute collection.

## Control flow
On search, the module skips if disabled, system, trusted/internal, or special DN. Otherwise it creates an `aclread_context`, computes SD flags from the request, and augments the requested attribute list with `instanceType`, `objectSid`, `objectClass`, and/or `nTSecurityDescriptor` when needed for ACL checks. It checks base-object visibility up front; an invisible base returns `NO_SUCH_OBJECT` for base scope or defers that result for subtree/onelevel searches that may still return visible children. The downstream request carries `DSDB_CONTROL_ACL_READ_OID`, allowing the filter redaction callback and reply callback to share state.

For each returned entry, `aclread_callback()` first verifies object visibility. NC heads are always visible. Otherwise the parent needs `SEC_ADS_LIST`, or when `dSHeuristics` enables List Object mode, the parent and object both need `SEC_ADS_LIST_OBJECT`. It then scans attributes. Attributes added only for ACL processing are marked inaccessible; already checked filter attributes are skipped; remaining attributes trigger setup of schema/SD/class/SID context and then `acl_redact_attr()`. After marking, `ldb_msg_remove_inaccessible()` physically strips hidden elements before sending the entry.

`acl_redact_msg_for_filter()` runs earlier in the LDB stack for candidate messages. It collects attributes referenced by the search parse tree, ignoring always-present/always-visible cases, and redacts those attributes before filter matching if the caller lacks rights. This prevents matching on secret/confidential/inaccessible attributes and then inferring their values from object presence.

## State and persistence behavior
The module persists no database changes. It mutates search requests by adding internal attributes and controls and mutates result messages in memory by marking/removing inaccessible attributes. Module-private state caches the last parsed security descriptor and its blob, plus a sorted array of password/secret attribute names. Per-search state caches schema, parent visibility result, requested SD flags, base invisibility, entry count, and collected filter attributes.

## Dependencies and integration points
It depends on auth session/security tokens, `acl_util.c` access-check helpers, DSDB schema and structural objectclass resolution, NDR security descriptor parsing, `@KLUDGEACL` passwordAttribute data, `DSDB_SECRET_ATTRIBUTES`, `dsdb_do_list_object()` dSHeuristics behavior, LDB SD flags control, `DSDB_CONTROL_ACL_READ_OID`, and the LDB redaction callback mechanism.

## Risks and edge cases
- Filter redaction only covers attributes visible in the parse tree; comments explicitly warn that extended match rules inspecting other attributes need their own ACL checks.
- SD parsing is cached by exact blob; callers must not retain the returned SD beyond the next cache update on the module context.
- Always-present and always-visible exceptions are intentional compatibility/security tradeoffs, especially `objectClass=*` visibility under List Children.
- `nTSecurityDescriptor` access depends on requested SD flags: owner/group/DACL require read-control, SACL requires system-security.
- Secret attributes are always hidden regardless of ordinary read-property rights.
- Request attribute augmentation must be removed from results to avoid leaking internal attributes the client did not request.

## Test signals
Test with normal LDAP searches as non-admin users over base, onelevel, and subtree scopes; invisible base behavior; List Children versus List Object dSHeuristics; NC head visibility; attribute redaction for ordinary, confidential, secret, and `nTSecurityDescriptor` attributes with SD flags; filter matching on inaccessible attributes; objectClass/name/objectGUID presence exceptions; system/trusted bypass; `userPassword` secret behavior toggled by support setting; and repeated entries sharing SDs to exercise cache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl_util.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl_util.c

## Purpose
`acl_util.c` provides shared helper routines for DSDB ACL modules. It extracts the caller token, performs object/DN and attribute/class access checks, resolves extended rights and validated writes, parses SD flags controls, formats the caller name, and schedules security descriptor propagation.

## Important APIs, types, and functions
- `acl_user_token()` returns the current session security token from the LDB opaque `DSDB_SESSION_INFO`.
- `dsdb_module_check_access_on_dn()` reads an object's SD/SID as system through the module stack and calls `dsdb_check_access_on_dn_internal()`.
- `acl_check_access_on_attribute_implicit_owner()` builds an object tree for class, attributeSecurityGUID, and attribute schemaIDGUID, then calls `sec_access_check_ds_implicit_owner()`.
- `acl_check_access_on_attribute()` is the normal read/write property wrapper using default implicit-owner read-control rights.
- `acl_check_access_on_objectclass()` checks class-level rights such as create child/delete tree.
- `acl_check_extended_right()` verifies an extended right applies to the structural objectclass and then checks the right GUID in the security descriptor.
- `dsdb_request_sd_flags()` consumes the LDAP SD flags control and normalizes the four SECINFO bits.
- `dsdb_module_schedule_sd_propagation()` invokes `DSDB_EXTENDED_SEC_DESC_PROPAGATION_OID` as system/trusted/top-module.

## Control flow
DN-level checks fetch `nTSecurityDescriptor` and `objectSid` using `dsdb_module_search_dn()` with next-module, as-system, and show-recycled flags, then delegate to the internal SD access checker. Attribute checks construct a DS object tree rooted at the structural class GUID, optionally include the attribute security property-set GUID, and then the concrete attribute GUID; this lets DS ACLs grant rights at class, property set, or attribute level. Objectclass checks build a simpler class GUID tree.

Extended right checks first locate `CN=Extended-Rights`, search one level for the requested `rightsGuid` with an `appliesTo` value matching the structural class schemaIDGUID, convert the GUID string, build an object tree for that right, and call `sec_access_check_ds()`. SD flags parsing marks the request control non-critical once handled, masks to the low four bits, and treats zero bits as all owner/group/DACL/SACL bits per MS-ADTS.

## State and persistence behavior
These helpers do not persist ordinary directory changes. They allocate temporary object trees and search results under caller contexts. `dsdb_request_sd_flags()` mutates the request control criticality to indicate it has been handled. `dsdb_module_schedule_sd_propagation()` schedules persistent downstream SD propagation through an extended operation.

## Dependencies and integration points
The file integrates with `acl.c` and `acl_read.c`, auth/session info, LDB controls, DSDB module search and extended APIs, security descriptor access-check functions, object tree construction, schema class/attribute GUIDs, Extended-Rights container layout, and SD propagation extended operation infrastructure.

## Risks and edge cases
- Missing `DSDB_SESSION_INFO` or token generally produces operational failure; callers must ensure module context is initialized with session info.
- Attribute access depends on correct schema metadata, especially `attributeSecurityGUID` and `schemaIDGUID`.
- Extended rights require both an `appliesTo` directory object and an ACE granting the right; missing appliesTo is treated as insufficient access.
- `dsdb_request_sd_flags()` consumes the SD flags control; multiple modules must agree on that convention.
- Propagation scheduling uses trusted/system flags and should only be called after authorization has already succeeded.

## Test signals
Tests should cover object DN access checks, class create/delete checks, attribute checks granted via class GUID/property set/attribute GUID, implicit owner variants, extended rights with and without appliesTo, SD flags control normalization including zero flags, missing session info failure, recycled object lookup, and SD propagation extended operation invocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/anr.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/anr.c

## Purpose
`anr.c` implements the LDB module for Active Directory ambiguous name resolution. It rewrites searches containing the pseudo-attribute `anr` into an OR filter over schema attributes marked with `SEARCH_FLAG_ANR`, with AD-compatible handling for exact-match syntax and split given-name/surname searches.

## Important APIs, types, and functions
- `make_parse_list()` creates two-arm `LDB_OP_AND` or `LDB_OP_OR` parse tree nodes and steals both child arms.
- `make_match_tree()` creates equality or prefix-substring match parse tree nodes for a real attribute and match value.
- `anr_replace_value()` expands one `anr` value into a tree over all schema ANR attributes and optional `givenName`/`sn` split filters.
- `anr_replace_subtrees()` recursively replaces eligible `anr` equality or prefix-substring subtrees inside the copied filter tree.
- `parse_tree_anr_present()` detects any operation that references `anr` before paying rewrite costs.
- `anr_search()` is the module search hook: detect, shallow-copy the parse tree, rewrite, build a downstream search, and forward replies through `anr_search_callback()`.

Key local structs are `anr_context` for the downstream request/callback and `anr_present_ctx` for detection.

## Control flow
The search hook first walks the original parse tree looking for any `anr` reference across equality, comparison, substring, present, and extended operations. If none is found, it passes the request unchanged. If ANR is present, it copies the parse tree, recursively replaces only equality or simple prefix-substring forms of `anr`, and submits a new search request with the expanded tree and original base/scope/attrs/controls.

`anr_replace_value()` obtains the current schema and iterates every schema attribute. Attributes with `SEARCH_FLAG_ANR` become either `(attr=value)` when the input value starts with `=` or `(attr=value*)` otherwise. These are chained as nested OR nodes. If the search value contains a space, it also adds `(|(&(givenName=first)(sn=second))(&(sn=first)(givenName=second)))` using the same equality-or-prefix mode. The callback transparently forwards entries, referrals, and done/error replies to the original request.

## State and persistence behavior
The module is stateless and makes no persistent changes. It allocates a rewritten parse tree under the per-request context, steals values/children into that tree, and frees everything with the request. The original caller parse tree is shallow-copied before modification to avoid mutating caller-owned memory.

## Dependencies and integration points
It depends on LDB parse tree APIs, DSDB schema access, schema `searchFlags`, `SEARCH_FLAG_ANR`, and the LDB module stack. It integrates as module `"anr"` via `ldb_anr_module_init()`.

## Risks and edge cases
- Only equality and simple prefix-substring `anr` filters are expanded; present/comparison/extended uses are detected but not transformed by `anr_replace_subtrees()`.
- If no schema is available, ANR rewriting fails with operations error.
- The prefix-substring expansion reuses a single `ldb_val` pointer across multiple match tree chunks; lifetime is tied to the copied tree/request context.
- Split-name logic only splits on the first ASCII space and hardcodes `givenName`/`sn` in addition to schema-marked ANR attributes.
- Nested OR construction can produce deep trees for many ANR attributes.

## Test signals
Useful tests include `(anr=foo)` prefix expansion, `(anr==foo)` exact expansion, substring `anr=foo*`, filters without ANR passing unchanged, compound AND/OR/NOT replacement, split names like `Jane Smith`, schema without ANR attributes, missing schema failure, and callback forwarding of entries/referrals/done/error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/anr.c -->
