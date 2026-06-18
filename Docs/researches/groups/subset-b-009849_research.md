# Research: subset-b-009849

Grouped research for Samba LSA RPC server and mdssvc Spotlight/Elasticsearch support files. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/lsa/srv_lsa_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/lsa/srv_lsa_nt.c

## Purpose
This file implements Samba source3's LSARPC server entry points for policy handles, SID/name lookup, trusted domains, secrets, account rights, privileges, security descriptors, and selected forest-trust operations. It bridges generated NDR LSARPC stubs to Samba passdb, secrets, privilege, auth-session, and DCE/RPC policy-handle services, while leaving many rarely used or unsupported opnums as explicit `NT_STATUS_NOT_IMPLEMENTED` stubs.

## Important APIs, Types, And Functions
The central private state is `struct lsa_info`, stored behind DCE/RPC policy handles by `create_lsa_policy_handle()`. It records the handle type (`LSA_HANDLE_POLICY_TYPE`, `LSA_HANDLE_ACCOUNT_TYPE`, `LSA_HANDLE_TRUST_TYPE`, `LSA_HANDLE_SECRET_TYPE`), granted access mask, optional SID, optional object name, and copied security descriptor. The generic mappings `lsa_account_mapping`, `lsa_policy_mapping`, `lsa_secret_mapping`, and `lsa_trusted_domain_mapping` translate generic access bits to object-specific LSARPC rights.

Policy open/query paths include `_lsa_OpenPolicy2()`, `_lsa_OpenPolicy()`, `_lsa_OpenPolicy3()`, `_lsa_QueryInfoPolicy()`, and `_lsa_QueryInfoPolicy2()`. Name and SID lookup is handled by `lookup_lsa_rids()`, `lookup_lsa_sids()`, `_lsa_lookup_sids_internal()`, `_lsa_LookupSids*()`, `_lsa_LookupNames*()`, and `lsa_lookup_level_to_flags()`. Trust-domain operations include `lsa_lookup_trusted_domain_by_sid()`, `lsa_lookup_trusted_domain_by_name()`, `_lsa_OpenTrustedDomain*()`, `_lsa_CreateTrustedDomainEx2()`, `_lsa_CreateTrustedDomainEx3()`, `_lsa_DeleteTrustedDomain()`, `_lsa_QueryTrustedDomainInfo*()`, `_lsa_SetInformationTrustedDomain()`, `_lsa_EnumTrustedDomainsEx()`, and `_lsa_lsaRSetForestTrustInformation()`. Secret operations include `_lsa_OpenSecret()`, `_lsa_CreateSecret()`, `_lsa_SetSecret()`, `_lsa_QuerySecret()`, and `_lsa_DeleteObject()`. Privilege/account APIs include `_lsa_EnumPrivs()`, `_lsa_CreateAccount()`, `_lsa_OpenAccount()`, `_lsa_EnumPrivsAccount()`, `_lsa_AddPrivilegesToAccount()`, `_lsa_RemovePrivilegesFromAccount()`, `_lsa_AddAccountRights()`, `_lsa_RemoveAccountRights()`, `_lsa_EnumAccountRights()`, `_lsa_LookupPriv*()`, and `_lsa_EnumAccountsWithUserRight()`.

## Control Flow
Most entry points first validate transport, handle type, and granted access, then call a Samba subsystem and convert its result to an LSARPC response. Named-pipe and local RPC calls are accepted for normal policy and lookup calls; handle-free `LookupSids3` and `LookupNames4` are restricted to TCP with schannel integrity or stronger because they do not carry a policy handle. `_lsa_OpenPolicy2()` and `_lsa_OpenPolicy3()` create a generic policy security descriptor, map requested access, run `access_check_object()`, and register a policy handle. Query calls switch on information levels and fill generated NDR unions.

Lookup flows cap requests at `MAX_LOOKUP_SIDS`, translate lookup levels to `LOOKUP_NAME_*` flags, temporarily `become_root()` where local name lookup requires it, and return `NT_STATUS_NONE_MAPPED`, `STATUS_SOME_UNMAPPED`, or `NT_STATUS_OK` based on mapped counts. Trust creation validates DC role, domain SID shape, BUILTIN/current-domain exclusions, policy trust-admin access, and local admin/root authority before decrypting trust password blobs and storing `pdb_trusted_domain` records. Forest-trust setting converts LSARPC forest-trust records to DRS blob structures, checks conflicts against own and existing trusted-domain forest trust info, optionally returns collision records, then stores marshalled forest-trust blobs.

## State And Persistence
Per-call allocations and response objects live under `p->mem_ctx`; persistent handle state lives in the DCE/RPC policy handle table as `struct lsa_info`. Policy/account/trust/secret security descriptors are currently synthesized or copied into handles rather than stored uniformly for all object classes. Persistent data is delegated: trusted domains use passdb trusted-domain records (`pdb_set_trusted_domain`, `pdb_del_trusted_domain`, enumeration/query helpers), trust passwords are stored as NDR blobs in those passdb records, secrets use `pdb_set_secret`, `pdb_get_secret`, and `pdb_delete_secret`, and privileges/account rights use Samba's privilege database helpers. Secrets are encrypted/decrypted on the wire with the session key; legacy trust auth blobs use RC4 subject to `lp_weak_crypto()` and transport encryption policy, while Ex3 uses AES-256-CBC-HMAC-SHA512 helpers and DCE/RPC transport session key material.

## Dependencies And Integration Points
The file depends on generated LSARPC, Netlogon, DRS blob, security descriptor, and wkssvc NDR headers; passdb and secrets APIs; Samba auth-session and security-token APIs; privilege helpers; DCE/RPC server handle and auth helpers; DNS comparison for forest-trust collision checks; GnuTLS crypto helpers; and loadparm configuration. It integrates into the source3 RPC server by defining LSARPC endpoint registration for netlogon and lsass named pipes and then including generated `ndr_lsa_scompat.c` boilerplate.

## Risks And Test Signals
Key risks are authorization drift between synthesized security descriptors and real persisted object ACLs, many TODOs around trusted-domain update validation, RC4 legacy trust auth handling when weak crypto is allowed, subtle transport/auth gating for handle-free lookup calls, memory lifetime of passdb-returned domain entries referenced in response arrays, and compatibility-sensitive status codes for partially mapped lookups and resume handles. The code also has deliberate no-op or unimplemented opnums that must continue to fault with the expected DCE/RPC status.

Good test signals include Samba torture LSARPC open/query/lookup coverage over named pipe, local RPC, and TCP schannel paths; lookup limits and partial mapping cases; policy access-denied cases for each object type; trusted-domain create/query/set/delete round trips including Ex2 and Ex3 auth blobs; secret create/set/query/delete with session-key encryption; privilege add/remove/enumerate tests; forest-trust collision and check-only cases; resume-handle behavior for trust enumeration; and regression checks for unsupported opnums returning `DCERPC_FAULT_OP_RNG_ERROR` where expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/lsa/srv_lsa_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/dalloc.c -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/dalloc.c

## Purpose
This file implements `DALLOC_CTX`, a small talloc-backed dynamic object store used by mdssvc Spotlight marshalling code to represent heterogeneous arrays, dictionaries, file metadata, and primitive values with runtime type tags. It gives the marshaller a compact way to build nested typed trees without defining a full variant object model.

## Important APIs, Types, And Functions
`struct dalloc_ctx` contains one `void **dd_talloc_array` vector whose elements are talloc children or copied talloc chunks named with their logical type. `_dalloc_new()` allocates a named context. `_dalloc_add_talloc_chunk()` appends either a copied scalar chunk (`size != 0`) or a type-checked talloc child (`size == 0`). `dalloc_size()`, `dalloc_get_object()`, and `dalloc_get_name()` expose vector inspection. `dalloc_get()` walks optional nested `DALLOC_CTX` entries and returns a type-checked element by index. `dalloc_value_for_key()` treats a context as alternating `"char *"` keys and values. `dalloc_stradd()` stores strings with the canonical `"char *"` name. `dalloc_dump()` recursively renders a debug representation of supported mdssvc types.

## Control Flow
Appending grows the array with `talloc_realloc()`, then either copies data into a named talloc chunk or validates that the supplied object has the requested talloc name. Retrieval functions parse varargs paths, stepping into nested `DALLOC_CTX` elements until the final type and index/key are reached. Dumping iterates every object, dispatches on the talloc type name, recurses for nested dalloc-compatible containers, formats scalar values, converts UTF-16LE strings to UTF-8 for logging, and expands CNID arrays recursively.

## State And Persistence
All state is in-memory and owned by the parent talloc context. There is no file or database persistence. Object identity and type safety depend on talloc names, so type names are part of the runtime state. `dalloc_dump()` allocates its returned string under the dumped object.

## Dependencies And Integration Points
The implementation depends on talloc, Samba charset conversion helpers, `talloc_stack`, time formatting, and mdssvc marshalling type definitions from `marshalling.h`. It is consumed by `marshalling.c` for Spotlight RPC pack/unpack trees and by parser/mdssvc code that builds or inspects metadata dictionaries.

## Risks And Test Signals
Risks include varargs misuse with no compile-time checking, negative indexes not rejected before comparison with `size_t` lengths, reliance on exact talloc names for type safety, dictionary lookups assuming alternating string key/value layout, and `localtime()` use in dumps. Test signals should cover scalar copy/add, nested array traversal, dictionary key lookup, type mismatch failure, out-of-range paths, UTF-16 dump conversion, CNID dump recursion, and talloc lifetime cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/dalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/dalloc.h -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/dalloc.h

## Purpose
This header declares the talloc-backed dynamic typed object store used by mdssvc. It documents the intended object patterns: ordered sets, dictionaries represented as alternating key/value elements, and nested `DALLOC_CTX` containers.

## Important APIs, Types, And Functions
`struct dalloc_ctx` is opaque and typedefed as `DALLOC_CTX`. The creation macros are `dalloc_new(mem_ctx)` for a generic `DALLOC_CTX` and `dalloc_zero(mem_ctx, type)` for typedefed dalloc containers named as `type`. `dalloc_add_copy()` copies a scalar into the store with a type-name tag, while `dalloc_add()` appends an existing talloc child after type validation. The public functions expose indexed retrieval, key lookup, size/name/object inspection, string append, and debug dumping.

## Control Flow
Callers build dalloc trees by allocating a parent context, appending typed scalars or child containers, then retrieving by paths like `"DALLOC_CTX", index, "uint64_t", index`. The header's examples establish the convention that passing `"DALLOC_CTX"` to `dalloc_get()` or `dalloc_value_for_key()` means "descend into this nested object" rather than return the container itself.

## State And Persistence
The header itself has no runtime state. It defines ownership expectations: all stored objects are talloc-managed, and appended non-copied objects must already be children with the expected talloc name.

## Dependencies And Integration Points
It includes talloc and is included by `marshalling.h`, `dalloc.c`, and mdssvc code that needs dynamic Spotlight value containers. It intentionally exposes `_dalloc_new()` and `_dalloc_add_talloc_chunk()` for macro implementation, while callers should normally use the typed macros.

## Risks And Test Signals
The main API risk is that varargs paths and macro type names are unchecked by the compiler and can fail only at runtime. The `dalloc_zero` name is slightly misleading because it allocates a `DALLOC_CTX`-backed object named after the requested typedef, not an arbitrary zeroed C struct. Test signals are compile-time use from C callers, macro type-name correctness, nested retrieval examples from the header comment, and ABI consistency for the opaque typedef.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/dalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/elasticsearch_mappings.json -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/elasticsearch_mappings.json

## Purpose
This JSON file is mdssvc's default translation table from macOS Spotlight metadata attributes and content type identifiers to Elasticsearch query fields. It lets the Spotlight query parser turn client-side metadata predicates into backend-specific Lucene query fragments.

## Important APIs, Types, And Functions
The top-level keys are `attribute_mappings` and `mime_mappings`. Each attribute mapping maps a Spotlight key to a `type` consumed by `enum ssm_type` (`bool`, `num`, `str`, `fts`, `date`, or `type`) plus an Elasticsearch `attribute` field path. The wildcard `"*"` maps to full-text search. Content-type mappings translate numeric or UTI-like Spotlight type values such as `public.jpeg`, `public.text`, and `public.archive` to one or more MIME patterns.

## Control Flow
At runtime `es_parser_test.c` or mdssvc loads the JSON with Jansson. `es_map_sl_attr()` looks up a Spotlight attribute under `attribute_mappings`, converts the string `type` into an `ssm_type`, and escapes the target Elasticsearch field name. `map_type()` uses `mime_mappings` to expand Spotlight type values into MIME query alternatives.

## State And Persistence
This file is static configuration data. It does not persist runtime state, but changing it changes server query behavior after reload or next load. Samba configuration can override the path through the `elasticsearch:mappings` parameter.

## Dependencies And Integration Points
The mapping format is coupled to `es_mapping.c`, `es_mapping.h`, and `es_parser.y`. It assumes Elasticsearch indexed documents expose fields like `content`, `file.content_type`, `file.last_modified`, `file.filename`, `attributes.owner`, `path.real`, and `meta.raw.*`.

## Risks And Test Signals
Risks include stale field names relative to the Elasticsearch index schema, incorrect owner/group mappings, missing attributes causing query failure unless unknown attributes are ignored, and overly broad MIME expansions. Test signals include JSON parse validation, parser conversions for every listed metadata key, type expansion tests for UTI and numeric values, wildcard full-text searches, and integration tests against a representative Elasticsearch index.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/elasticsearch_mappings.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_lexer.l -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_lexer.l

## Purpose
This Flex lexer tokenizes macOS Spotlight RAW query strings for the mdssvc Elasticsearch backend parser. It recognizes Spotlight comparison operators, boolean operators, quoted phrases, words including UTF-8 sequences, boolean literals, date conversion syntax, and the `InRange` function.

## Important APIs, Types, And Functions
The generated lexer uses the `mdsyyl` prefix and includes `es_parser.tab.h` for token definitions. Token rules return `FUNC_INRANGE`, `DATE_ISO`, `BOOLEAN`, `QUOTE`, parentheses, `AND`, `OR`, equality/inequality and comparison tokens, `COMMA`, `WORD`, and `PHRASE`. `strip_quote()` removes surrounding double quotes from phrase tokens and allocates the result on `talloc_tos()`.

## Control Flow
Flex patterns define ASCII word characters, UTF-8 byte classes, special phrase characters, escaped phrase characters, and blanks. The lexer ignores whitespace, stores semantic values into `mdsyyllval`, and leaves parsing decisions to `es_parser.y`. Phrase matching accepts quoted strings containing word characters, specials, blanks, and escaped `"*` characters.

## State And Persistence
Lexer state is the generated scanner buffer created by `mdsyyl_scan_string()` in the parser. Semantic token strings are transient talloc stack allocations; there is no persistent storage.

## Dependencies And Integration Points
It depends on Samba allocation macros (`SMB_MALLOC`, `SMB_REALLOC`), `talloc_tos()`, generated Bison headers, and the `mdsyyl`-prefixed parser functions. It integrates directly with `map_spotlight_to_es_query()` in `es_parser.y`.

## Risks And Test Signals
Risks include incomplete UTF-8 validation, unrecognized characters causing parse failures, phrase handling that strips quotes but does not unescape every possible sequence, and token precedence interactions with the grammar. Test signals should include ASCII and UTF-8 words, quoted phrases with spaces and escaped quotes/stars, boolean operators, `InRange`, `$time.iso(...)`, unsupported characters, and malformed quotes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_lexer.l -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_mapping.c -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_mapping.c

## Purpose
This file provides helper functions for translating Spotlight metadata names and type values into escaped Elasticsearch/Lucene query components. It centralizes Lucene and JSON escaping rules and JSON mapping lookup.

## Important APIs, Types, And Functions
`escape_str()` is the internal generic escaping routine. `es_escape_str()` first escapes Lucene special characters, optionally excluding caller-specified characters, then escapes JSON string characters. `es_map_sl_attr()` reads an attribute's `type` and `attribute` from the mapping JSON and returns `struct es_attr_map` with an `ssm_type` and escaped Elasticsearch field name. `es_map_sl_type()` maps Spotlight content type values to MIME type strings.

## Control Flow
Mapping a Spotlight attribute performs two `json_unpack()` calls, searches a static string-to-enum table, allocates an `es_attr_map`, and escapes the target field. Type mapping is a direct JSON lookup. Escaping allocates a worst-case doubled buffer and inserts backslashes for any character in the escape list not present in the exception list.

## State And Persistence
The functions are stateless except for allocations returned under caller-provided talloc contexts and borrowed string pointers from Jansson objects. They do not modify the JSON mapping or persist data.

## Dependencies And Integration Points
The implementation depends on Samba base headers, talloc, Jansson, and `es_mapping.h`. It is called by `es_parser.y` for every parsed attribute, full-text term, string value, date field name, and content type mapping.

## Risks And Test Signals
Risks include returning `false` from a pointer-returning function on allocation failure, JSON schema mismatch, field-name escaping that may not match all Elasticsearch query-string contexts, and caller confusion over exception characters such as `*`, space, backslash, and quotes. Test signals should cover every Lucene special character, JSON quote/backslash escaping, exception behavior, unknown attributes/types, all `ssm_type` strings, and malformed mapping JSON.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_mapping.h -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_mapping.h

## Purpose
This header defines the public mapping API used by the mdssvc Elasticsearch query parser. It describes the small type system for mapped Spotlight attributes and declares escaping and lookup helpers.

## Important APIs, Types, And Functions
`enum ssm_type` classifies mapped attributes as boolean, numeric, string, full-text string, date, or special content type. `struct es_attr_map` pairs that type with an escaped Elasticsearch field name. The public functions are `es_escape_str()`, `es_map_sl_attr()`, and `es_map_sl_type()`.

## Control Flow
Callers load mapping JSON, pass the `attribute_mappings` object to `es_map_sl_attr()`, and dispatch on `es_attr_map.type` to build query expressions. For `ssmt_type`, callers pass the `mime_mappings` object to `es_map_sl_type()`.

## State And Persistence
The header defines no state. Returned `es_attr_map` objects and escaped strings are owned by caller-provided talloc contexts, while MIME type strings are borrowed from Jansson-managed JSON.

## Dependencies And Integration Points
It includes Jansson and relies on `TALLOC_CTX` from surrounding Samba headers. It is included by `es_mapping.c`, `es_parser.y`, and the standalone parser test program.

## Risks And Test Signals
Risks are ABI/API coupling to the JSON schema and the parser's switch over `enum ssm_type`. Adding a new mapping type requires changes in both this header and parser mapping logic. Test signals are compile tests for users of the header, query generation for each enum value, and checks that borrowed JSON strings are not used after `json_decref()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_parser.y -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_parser.y

## Purpose
This Bison grammar converts macOS Spotlight RAW query syntax into Elasticsearch query-string syntax. It supports boolean composition, comparisons, date normalization, range functions, content type expansion, full-text terms, and configurable handling for unknown mappings.

## Important APIs, Types, And Functions
The exported API is `map_spotlight_to_es_query(TALLOC_CTX *, json_t *, const char *, char **)`. Parser state is held in `struct es_parser_state`, including a talloc stack frame, JSON mapping objects, config flags, scanner buffer, type-error flag, and final result. Helper functions include `isodate_to_sldate()`, `map_type()`, `map_num()`, `map_fts()`, `map_str()`, `map_sldate_to_esdate()`, `map_date()`, and `map_expr()`. The grammar uses tokens from `es_lexer.l` and returns strings as semantic values.

## Control Flow
`map_spotlight_to_es_query()` extracts `attribute_mappings` and `mime_mappings`, creates a scanner over the query string, reads Samba `elasticsearch:*` options, sets the global parser state, and calls `mdsyylparse()`. Grammar rules reduce parenthesized expressions, `&&`, `||`, comparisons, `InRange(attribute,start,end)`, and `$time.iso(...)` values. Attribute reductions call `es_map_sl_attr()` and abort unless unknown attributes are configured to be ignored. Expression mapping dispatches on `ssm_type`, generating Lucene fragments such as field equality, negative clauses, open/closed numeric/date ranges, full-text terms, and MIME type lists.

## State And Persistence
Parser state is per call but stored in a global pointer while parsing because generated lexer/parser functions need shared state. Temporary strings live on a talloc stack frame and the final query is copied to the caller's context. The parser reads loadparm booleans but writes no persistent state.

## Dependencies And Integration Points
The grammar depends on generated Flex/Bison code, Jansson, Samba loadparm, `mdssvc_es.h`, `es_mapping.h`, `smb_strtox`, and time conversion functions. It is the main query translation layer used by the mdssvc Elasticsearch backend and by `es_parser_test.c`.

## Risks And Test Signals
Risks include the global parser state making concurrent parses unsafe unless serialized, limited grammar coverage for Spotlight syntax, `%expect 1` indicating a known parser conflict, substring forcing changing query semantics broadly, date conversion edge cases around invalid input and time ranges, and ignored unknown attributes producing partial queries. Test signals should cover operator precedence, nested parentheses, AND/OR with ignored subexpressions, numeric/string/date/type/full-text mappings, `InRange`, `$time.iso` conversion both directions, config toggles for unknown attributes/types and substring search, malformed syntax, and concurrent-call assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_parser.y -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_parser_test.c -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_parser_test.c

## Purpose
This is a standalone command-line test utility for the Spotlight-to-Elasticsearch parser. It accepts one RAW Spotlight query, loads the configured mapping JSON, prints the translated Elasticsearch query, and exits with success or failure.

## Important APIs, Types, And Functions
`main()` is the only function. It calls `lp_load_global()`, creates a talloc context, builds the default mapping path from `get_dyn_SAMBA_DATADIR()`, allows override via `elasticsearch:mappings`, loads JSON with `json_load_file()`, calls `map_spotlight_to_es_query()`, prints either the query or `*mapping failed*`, and releases Jansson/talloc resources.

## Control Flow
The program requires exactly one argument. Configuration is loaded before mapping path resolution. Any allocation, config path, JSON load, or parser failure returns exit code 1. A successful parse prints the generated query and returns 0.

## State And Persistence
The utility does not persist state. It reads Samba global configuration and a JSON mapping file, then allocates all runtime state under a process-local talloc context.

## Dependencies And Integration Points
It depends on Samba mdssvc headers, generated parser headers, mapping helpers, loadparm, dynamic path helpers, Jansson, and the same parser implementation used by the mdssvc backend. It is useful as a developer-facing test binary or manual reproducer for mapping behavior.

## Risks And Test Signals
Risks include weak diagnostics for JSON errors because it logs `strerror(errno)` rather than Jansson's detailed `json_error`, reliance on installed data paths, and no option to select alternate config except through Samba configuration. Test signals are CLI invocations for representative queries, missing/invalid mapping files, config override of mappings path, parser failure exit status, and expected stdout for known translations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_parser_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/marshalling.c -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/marshalling.c

## Purpose
This file packs and unpacks mdssvc Spotlight RPC binary values between `DALLOC_CTX` typed trees and on-wire Spotlight query/reply blobs. It implements the tag, table-of-contents, endian, string, date, numeric, UUID, CNID, array, dictionary, and file metadata handling used by Samba's Spotlight metadata server.

## Important APIs, Types, And Functions
Public APIs are `sl_pack_alloc()` and `sl_unpack()`. Internal constants define Spotlight primitive and complex tag types, maximum table-of-contents and command sizes, and the Spotlight epoch delta. `struct sl_tag` is the decoded 64-bit tag view with `type`, `count`, `length`, and `size`. Packing helpers include `sl_pack_tag()`, `sl_pack_uint64()`, `sl_pack_uint64_array()`, `sl_pack_bool()`, `sl_pack_nil()`, `sl_pack_float()`, `sl_pack_date()`, `sl_pack_uuid()`, `sl_pack_CNID()`, `sl_pack_array()`, `sl_pack_dict()`, `sl_pack_filemeta()`, `sl_pack_string()`, `sl_pack_string_as_utf16()`, `sl_pack_loop()`, and `sl_pack()`. Unpacking helpers include `sl_unpack_tag()`, `sl_unpack_ints()`, `sl_unpack_date()`, `sl_unpack_uuid()`, `sl_unpack_floats()`, `sl_unpack_CNID()`, `sl_unpack_cpx()`, and `sl_unpack_loop()`.

## Control Flow
Packing starts in `sl_pack_alloc()`, which allocates a bounded blob and calls `sl_pack()`. `sl_pack()` reserves the 16-byte header, recursively packs data elements starting at offset 16, builds complex object ToC entries in a side buffer, writes the little-endian marker `"432130dm"`, writes octet counts, appends the ToC tag and entries, then records blob length. `sl_pack_loop()` dispatches by dalloc type name and writes primitive tags inline while complex values write a complex reference plus a ToC entry.

Unpacking starts in `sl_unpack()`, detects byte order from the first 8 bytes, reads header octet counts, validates total/data/ToC bounds, decodes the ToC tag, then calls `sl_unpack_loop()` for the root object. Primitive tags add typed values to the output dalloc tree. Complex tags look up their ToC entry and call `sl_unpack_cpx()` to construct nested arrays, dictionaries, strings, UTF-16 strings, file metadata, or CNID structures.

## State And Persistence
All state is transient and talloc-owned. Packed blobs are written to `struct mdssvc_blob`; unpacked values are appended into a caller-provided `DALLOC_CTX`. The only persistent semantic conversion is between Unix time and Spotlight's 2001 epoch for date values.

## Dependencies And Integration Points
The implementation depends on Samba byte-order macros, debug logging, charset conversion, `dalloc`, `marshalling.h`, `mdssvc_blob`, and talloc. It is a core integration point between mdssvc RPC handlers and the higher-level dalloc representation consumed by query and metadata logic.

## Risks And Test Signals
Risks include binary parser attack surface, reliance on dalloc type-name strings, mixed use of bytes and 8-byte octets, hardcoded little-endian packing, unsupported big-endian UTF-16 strings, length/count overflow mistakes, recursive unpacking of nested file metadata, and fixed maximum string/ToC/count limits that may reject valid clients or hide edge bugs. Test signals should include pack/unpack round trips for every supported type, malformed headers, endian markers, oversized counts/lengths, ToC index bounds, UTF-8 and UTF-16 strings with BOMs, dates with fractional seconds, empty and non-empty CNID arrays, nested dictionaries/arrays/filemeta, max fragment behavior, and fuzzing of `sl_unpack()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/marshalling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/marshalling.h -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/marshalling.h

## Purpose
This header defines the public Spotlight marshalling interface and the dalloc-backed type aliases used to represent Spotlight RPC values in memory.

## Important APIs, Types, And Functions
It defines blob size limits `MAX_SL_FRAGMENT_SIZE` and `MAX_MDSCMD_SIZE`, encoding flags `SL_ENC_LITTLE_ENDIAN`, `SL_ENC_BIG_ENDIAN`, and `SL_ENC_UTF_16`, aliases `sl_array_t`, `sl_dict_t`, `sl_filemeta_t`, `sl_nil_t`, `sl_bool_t`, `sl_time_t`, `sl_uuid_t`, and `sl_cnids_t`, plus the public functions `sl_pack_alloc()` and `sl_unpack()`.

## Control Flow
Callers build a dalloc tree using these type aliases, then call `sl_pack_alloc()` to create an `mdssvc_blob`. For inbound blobs, callers allocate an output `DALLOC_CTX` and call `sl_unpack()` to populate it with typed values.

## State And Persistence
The header declares in-memory types only. `sl_time_t` is `struct timeval`, `sl_uuid_t` is a 16-byte wrapper, and `sl_cnids_t` carries two metadata fields plus a dalloc array of CNIDs. Persistence is limited to the serialized blob produced by `sl_pack_alloc()`.

## Dependencies And Integration Points
It includes `dalloc.h`, NT status definitions, Samba `DATA_BLOB`, and generated mdssvc NDR structures. It is included by `dalloc.c`, `marshalling.c`, and mdssvc RPC code that exchanges Spotlight blobs.

## Risks And Test Signals
Risks include callers exceeding fragment limits, misuse of dalloc aliases as if they were distinct C structs, and assumptions about endian/UTF-16 flags that only `marshalling.c` enforces. Test signals include compile coverage for all aliases, boundary tests for `MAX_SL_FRAGMENT_SIZE` and `MAX_MDSCMD_SIZE`, and public API round trips from mdssvc RPC request/response blobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/marshalling.h -->
