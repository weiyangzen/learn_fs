<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_perfcount.c -->
# sources/user-network-fs/samba/source3/registry/reg_perfcount.c

Purpose: Implements Samba's registry-facing performance counter provider. It reads counter metadata and live values from `state_path("perfmon")` TDB databases and marshals Windows `PERF_DATA_BLOCK` data for the `HKEY_PERFORMANCE_DATA` registry path.

Important APIs, types, and functions: Public entry points are `reg_perfcount_get_base_index()`, `reg_perfcount_get_last_counter()`, `reg_perfcount_get_last_help()`, `reg_perfcount_get_counter_help()`, `reg_perfcount_get_counter_names()`, and `reg_perfcount_get_hkpd()`. Internal builders include `_reg_perfcount_multi_sz_from_tdb()`, `_reg_perfcount_assemble_global()`, `_reg_perfcount_add_object()`, `_reg_perfcount_add_counter()`, `_reg_perfcount_get_counter_info()`, `_reg_perfcount_get_instance_info()`, `_reg_perfcount_perf_data_block_fixup()`, and marshalling helpers for data blocks, objects, counters, instances, and counter data. It uses generated `PERF_DATA_BLOCK`, `PERF_OBJECT_TYPE`, `PERF_COUNTER_DEFINITION`, `PERF_INSTANCE_DEFINITION`, and `PERF_COUNTER_BLOCK` types from `perfcount.h`.

Control flow: Counter name/help calls open `names.tdb`, fetch sequential numeric keys, encode index/name pairs as registry UTF-16 strings, and append the final double-NUL terminator. HKPD retrieval computes the base index, initializes a `PERF_DATA_BLOCK`, scans each even counter id's relationship key, creates parent objects for `p...` relationships and counters for `c[...]` relationships, fetches values from `data.tdb`, fixes offsets and 64-bit alignment, then writes the block and objects into the caller's `prs_struct`. If the full payload exceeds `max_buf_size`, only the header is marshalled and `WERR_INSUFFICIENT_BUFFER` is returned with the requested length capped.

State and persistence behavior: Persistent input lives in `perfmon/names.tdb` and `perfmon/data.tdb` under Samba's state directory. The module creates the `perfmon` directory if needed. Per-request output is allocated from the caller's talloc or parse context; fetched TDB buffers are manually freed. It does not cache TDB handles or counter layouts.

Dependencies and integration points: Integrates with the virtual registry layer through `reg_perfcount.h` and `reg_parse_prs.h`, TDB via `tdb_open_log()` and `tdb_fetch()`, registry string encoding via `push_reg_sz()` and `rpcstr_push_talloc()`, server identity via `lp_netbios_name()`, and Samba state paths via `state_path()`.

Risks: Many TDB values are copied into fixed `PERFCOUNT_MAX_LEN` stack buffers and parsed with `atoi()`, `atof()`, or `strtol()`, so malformed or oversized database values can truncate or produce surprising numeric results. Several helper failures close no already-open `names` handle on early return. `object_ids` is accepted by `reg_perfcount_get_hkpd()` but not used to filter objects. Payload layout is alignment-sensitive, and a single bad relationship or missing parent object can suppress the whole HKPD response.

Test signals: Useful tests would create temporary `names.tdb`/`data.tdb` fixtures covering name/help MULTI_SZ construction, parent-before-child assembly, missing relationship keys, missing data keys, 32-bit, 64-bit, and variable-length counters, instance names and data, big-endian parse contexts, insufficient-buffer behavior, and malformed TDB values near `PERFCOUNT_MAX_LEN`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_perfcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_perfcount.h -->
# sources/user-network-fs/samba/source3/registry/reg_perfcount.h

Purpose: Public header for the registry performance counter provider.

Important APIs, types, and functions: Declares `reg_perfcount_get_base_index()`, `reg_perfcount_get_last_counter()`, `reg_perfcount_get_last_help()`, `reg_perfcount_get_counter_help()`, `reg_perfcount_get_counter_names()`, and `reg_perfcount_get_hkpd()`. It includes `reg_parse_prs.h` for `prs_struct`.

Control flow: No executable logic. Callers use the scalar helpers to expose registry metadata values and use `reg_perfcount_get_hkpd()` to marshal performance data into a parse stream.

State and persistence behavior: No header-owned state. Implementations read Samba state TDBs and allocate output buffers for callers.

Dependencies and integration points: Included by registry backend code that serves `HKEY_PERFORMANCE_DATA` and by `reg_perfcount.c`. The API uses Samba `WERROR` and parse-buffer conventions rather than raw Windows structures.

Risks: Callers must free buffers returned through `char **retbuf` according to the implementation's allocation conventions and must handle zero lengths as missing or failed data. `reg_perfcount_get_hkpd()` reports Windows registry errors, while the other functions return byte counts or indexes, so error handling is mixed.

Test signals: Compile coverage for registry modules, plus API-level tests for zero base index, last-counter/help arithmetic, successful name/help buffer ownership, and HKPD insufficient-buffer return mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_perfcount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_internal.c -->
# sources/user-network-fs/samba/source3/registry/reg_util_internal.c

Purpose: Supplies small internal registry path helpers for splitting and normalizing virtual registry key paths.

Important APIs, types, and functions: `reg_split_path()` splits a mutable path at the first backslash into a base hive and remaining path. `reg_split_key()` splits a mutable path at the last backslash into parent path and leaf key. `normalize_reg_path()` strips leading and trailing backslashes and uppercases the key into a talloc allocation. `reg_remaining_path()` duplicates a key and returns a pointer past the first component.

Control flow: The split functions mutate the input string by replacing a delimiter with `'\0'` and return pointers into that same buffer. Normalization advances over leading delimiters, duplicates the remaining string, repeatedly removes trailing delimiters, then calls `strupper_m()`. `reg_remaining_path()` duplicates the source string and returns either the duplicate itself or the character after the first backslash.

State and persistence behavior: No global state. Split outputs alias caller storage. Normalization and remaining-path outputs are talloc-owned by the supplied context; `reg_remaining_path()` returns an interior pointer into the allocated duplicate, so the talloc allocation must remain alive.

Dependencies and integration points: Depends on Samba talloc, multibyte uppercase conversion, and registry frontend code that needs normalized database keys. It is paired with `reg_util_internal.h`.

Risks: The split helpers destructively edit their input and do not duplicate data. `normalize_reg_path()` assumes `keyname` is non-NULL and dereferences it immediately. `reg_remaining_path()` returns an interior pointer, which can make ownership unclear and can leak the hidden base pointer if callers do not keep the talloc context.

Test signals: Cover NULL and empty inputs, paths without backslashes, leading/trailing repeated backslashes, multibyte uppercase failure, first-vs-last delimiter behavior, and ownership lifetime of the interior pointer returned by `reg_remaining_path()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_internal.h -->
# sources/user-network-fs/samba/source3/registry/reg_util_internal.h

Purpose: Internal header declaring registry path utility functions.

Important APIs, types, and functions: Declares `reg_split_path()`, `reg_split_key()`, `normalize_reg_path()`, and `reg_remaining_path()`.

Control flow: No executable logic. The prototypes expose both destructive split helpers and talloc-allocating normalization helpers.

State and persistence behavior: No header-owned state. Callers must respect that split results alias the modified input buffer, while normalized results live under caller-provided talloc contexts.

Dependencies and integration points: Included by registry frontend and backend modules that need consistent registry path manipulation.

Risks: The include guard name `_REG_UTIL_H` is generic and could collide with similarly named registry utility headers. The API does not encode ownership or mutation in the type signatures.

Test signals: Compile coverage for all registry utility consumers and path-behavior tests through `reg_util_internal.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_token.c -->
# sources/user-network-fs/samba/source3/registry/reg_util_token.c

Purpose: Creates a minimal synthetic administrator-like security token for local registry access.

Important APIs, types, and functions: Exports `registry_create_admin_token(TALLOC_CTX *mem_ctx, struct security_token **ptoken)`. It allocates `struct security_token`, grants `SEC_PRIV_DISK_OPERATOR`, and adds `global_sid_Builtin_Administrators` to the token SID list.

Control flow: The function rejects a NULL output pointer, allocates a zeroed token, sets the disk-operator privilege bit, appends the builtin administrators SID with `add_sid_to_array()`, then returns the token through `ptoken`. On allocation or SID failure it returns the corresponding `NTSTATUS`.

State and persistence behavior: No module-global state is mutated. The returned token and its SID array are allocated below the caller's talloc context. On error after token allocation, the token is not explicitly freed before returning, so normal frame/context cleanup is expected to reclaim it.

Dependencies and integration points: Depends on Samba security token APIs and well-known SID definitions from `../libcli/security/security.h`. Used by local registry code paths that need enough authority to open or modify protected registry content without a real user token.

Risks: This deliberately fabricates elevated local authority; callers must keep it confined to local registry operations. Error cleanup relies on talloc context lifetime. The token includes disk-operator privilege plus builtin administrators membership but not a complete logon/user identity, so downstream authorization code must not assume it represents a real session.

Test signals: Tests should verify NULL-output rejection, no-memory handling, token privilege presence, administrator SID membership, SID-count updates, and that failed SID insertion does not publish a partial token.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_token.h -->
# sources/user-network-fs/samba/source3/registry/reg_util_token.h

Purpose: Public header for the registry admin-token helper.

Important APIs, types, and functions: Declares `registry_create_admin_token(TALLOC_CTX *mem_ctx, struct security_token **ptoken)`.

Control flow: No executable logic. The single API returns an `NTSTATUS` and publishes a talloc-owned `security_token`.

State and persistence behavior: No header-owned state. Output token lifetime is controlled by the caller's talloc context.

Dependencies and integration points: Included by registry management code that needs a local administrative token for registry access checks.

Risks: The prototype does not describe that the token is synthetic and privileged; misuse outside tightly scoped local registry access would bypass normal caller identity semantics.

Test signals: Compile coverage for token consumers and behavioral tests in `reg_util_token.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_token.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/regfio.c -->
# sources/user-network-fs/samba/source3/registry/regfio.c

Purpose: Implements Samba's reader/writer for Windows NT registry hive (`regf`) files. It can open existing hives, locate and parse root/subkey/value/security records, create new hives, and append keys, values, subkey lists, and security descriptors.

Important APIs, types, and functions: Public APIs are `regfio_open()`, `regfio_close()`, `regfio_rootkey()`, `regfio_fetch_subkey()`, and `regfio_write_key()`. Core parsers/serializers include `prs_regf_block()`, `prs_hbin_block()`, `prs_nk_rec()`, `hbin_prs_lf_records()`, `hbin_prs_vk_records()`, `hbin_prs_vk_rec()`, `hbin_prs_sk_rec()`, and `hbin_prs_key()`. Allocation and persistence helpers include `read_block()`, `write_block()`, `read_hbin_block()`, `lookup_hbin_block()`, `find_free_space()`, `regf_hbin_allocate()`, and record-size calculators for NK/LF/VK/SK records.

Control flow: `regfio_open()` allocates a `REGF_FILE`, opens the fd, initializes a new `regf` header for create/truncate or parses and checksum-validates an existing header. `regfio_rootkey()` scans HBIN blocks for an NK record with `NK_TYPE_ROOTKEY`, parsing linked values, subkeys, and security descriptor references. `regfio_fetch_subkey()` uses the caller's `subkey_index` and LF hash list to iterate child NK records. `regfio_write_key()` builds a new NK record, updates the parent LF list if present, de-duplicates or creates security descriptor records, allocates LF and value-list records, creates VK/value-data records, streams the records, and flushes dirty HBIN blocks. `regfio_close()` writes dirty security descriptors and HBINs, updates the header timestamp/checksum, frees memory, and closes the fd.

State and persistence behavior: `REGF_FILE` owns the fd, open flags, talloc memory context, cached HBIN list, parsed security descriptor list, header fields, and checksum behavior. HBINs cache parse buffers and dirty state until close or flush. On-disk state is updated through `write_block()` and record-level marshalling; new records consume the current free tail of an HBIN or allocate a new HBIN.

Dependencies and integration points: Depends on Samba `prs_struct` marshalling, `reg_objects` value/subkey containers, NT time helpers, generated NDR security descriptor sizing, security descriptor marshal/unmarshal helpers, DLIST macros, and POSIX file I/O. The test file in this subset exercises open, corrupt-HBIN, and corrupt-LF paths.

Risks: This is binary-parser code for potentially corrupt hive input. Offset arithmetic, record-size sign handling, and HBIN boundary checks are security-sensitive. Some paths leak parse buffers on early return, and checksum validation can be disabled by the `ignore_checksums` field for fuzzing. The writer mostly appends and tracks only tail free space, so it is not a general compactor. `hbin_prs_sk_rec()` advances the parse offset using blob length rather than a relative add, which is subtle. Input strings for key/value names are treated as byte strings rather than full Unicode registry names.

Test signals: Existing cmocka tests cover new-file root creation and two corrupt fixture cases. Additional tests should cover checksum failure and ignore mode, cross-HBIN value data, inline value data, SK descriptor de-duplication/refcounts, sorted subkey hash records, malformed record sizes, HBIN boundary offsets, root search across multiple HBINs, close-time header checksum update, and value/subkey round trips with multiple record sizes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/regfio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/regfio.h -->
# sources/user-network-fs/samba/source3/registry/regfio.h

Purpose: Defines the in-memory representation and public API for Samba's Windows registry hive I/O library.

Important APIs, types, and functions: Provides constants for block sizes, record headers, value flags, NK key types, and `REGF_OFFSET_NONE`. Declares `REGF_HBIN`, `REGF_HASH_REC`, `REGF_LF_REC`, `REGF_VK_REC`, `REGF_SK_REC`, `REGF_NK_REC`, and `REGF_FILE`. Public functions are `regfio_open()`, `regfio_close()`, `regfio_rootkey()`, `regfio_fetch_subkey()`, and `regfio_write_key()`.

Control flow: No executable logic. The structures mirror hive records while also carrying runtime-only links, offsets, parse streams, dirty flags, memory contexts, fd state, and iteration indexes used by `regfio.c`.

State and persistence behavior: `REGF_FILE` is the top-level mutable state for an open hive. `REGF_HBIN` nodes cache on-disk blocks and write-back state. `REGF_NK_REC` includes child LF, VK values, and SK descriptor links, while `subkey_index` makes subkey iteration stateful on the NK object itself.

Dependencies and integration points: Includes registry parse and object headers, consumes `struct regval_ctr`, `struct regsubkey_ctr`, and `struct security_descriptor`, and is used by registry import/export or hive tooling plus tests.

Risks: Public structs expose low-level offsets and mutable internals, so callers can corrupt iterator or write state. Macros `HBIN_STORE_REF` and `HBIN_REMOVE_REF` mutate refcounts without safety checks. The API is not thread-safe for shared `REGF_FILE` or `REGF_NK_REC` objects.

Test signals: Compile ABI coverage for all consumers, structure initialization tests through `regfio_open()`, iteration tests confirming `subkey_index` semantics, and writer tests that validate the emitted hive with a fresh reader.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/regfio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/tests/test_regfio.c -->
# sources/user-network-fs/samba/source3/registry/tests/test_regfio.c

Purpose: Cmocka unit tests for basic `regfio` behavior and corruption hardening.

Important APIs, types, and functions: Defines `struct test_ctx`, setup/teardown helpers, `open_testfile()`, `test_regfio_open_new_file()`, `test_regfio_corrupt_hbin()`, `test_regfio_corrupt_lf_subkeys()`, and `main()`.

Control flow: Tests allocate a talloc test context, optionally create a temporary file with `mkstemp()`, open registry fixtures under `SRCDIR/testdata/samba3`, and close/unlink/free in teardown. The new-file test opens a truncating writable hive, asserts no root exists yet, creates empty subkey/value containers, writes the root key, and verifies its NK header and root-key type. Corrupt fixture tests assert corrupt HBIN input yields no root and that corrupt LF subkey data does not crash while iterating.

State and persistence behavior: Temporary files are created under `/tmp/regfio.XXXXXX` and removed during teardown. `REGF_FILE` handles are stored in the context and closed if present. Fixture files are read-only.

Dependencies and integration points: Depends on cmocka, Samba talloc and file utilities, `registry/regfio.h`, and fixture data in `testdata/samba3`. It is the direct test signal for `regfio.c`.

Risks: The tests are intentionally narrow and mostly assert non-crash behavior. They do not validate value serialization, security descriptors, checksum handling, cross-HBIN records, or full round-trip correctness. The temporary path is hard-coded to `/tmp`.

Test signals: Current signals are successful new hive initialization/root write, graceful failure on corrupt HBIN, and safe iteration over corrupt LF subkey records. Expanding this file would be the natural place for round-trip and fuzz-regression cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/tests/test_regfio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.c

Purpose: Provides higher-level client helpers for Local Security Authority RPC operations: opening LSA policy handles and translating between SIDs and account names.

Important APIs, types, and functions: Exports `dcerpc_lsa_open_policy()`, `rpccli_lsa_open_policy()`, `dcerpc_lsa_open_policy2()`, `dcerpc_lsa_open_policy3()`, `dcerpc_lsa_open_policy_fallback()`, `dcerpc_lsa_lookup_sids_generic()`, `dcerpc_lsa_lookup_sids()`, `rpccli_lsa_lookup_sids()`, `dcerpc_lsa_lookup_sids3()`, `dcerpc_lsa_lookup_names_generic()`, `dcerpc_lsa_lookup_names()`, `rpccli_lsa_lookup_names()`, and `dcerpc_lsa_lookup_names4()`. Internal `dcerpc_lsa_lookup_sids_noalloc()` performs one RPC translation hunk into caller-provided arrays.

Control flow: Open-policy helpers prepare `lsa_ObjectAttribute` and optional `lsa_QosInfo`, then call generated NDR client stubs. The fallback helper tries OpenPolicy3, falls back to OpenPolicy2 on missing procedure or after reopening unauthenticated on access denied. SID lookup allocates output arrays, processes inputs in hunks of 1000 SIDs, calls either LookupSids or LookupSids3, maps translated names through returned domain indexes, and combines hunk statuses into OK, some-unmapped, or none-mapped. Name lookup converts strings to `lsa_String`, calls LookupNames or LookupNames4, validates returned counts and domain indexes, builds SIDs by combining domain SID plus RID where needed, and optionally returns domain names.

State and persistence behavior: No module-global state. All returned arrays and strings are talloc-owned by the caller's memory context. Policy handles are server-side state represented by output `policy_handle` values. The fallback path can mutate the RPC pipe authentication state by reopening a named pipe without auth.

Dependencies and integration points: Depends on generated `ndr_lsa_c` stubs, `rpc_pipe_client`, `cli_pipe`, LSA initialization helpers, SID helpers, and `lsa.h` status macros. It bridges low-level generated RPC calls to Samba callers that want simpler NTSTATUS-returning lookup APIs.

Risks: Correctness depends on strict validation of server-returned counts and domain indexes; this code handles several invalid response cases. The hunking logic uses pointer arithmetic across output arrays and must keep arrays sized to `num_sids`. `dom_names` returned by name lookup point into RPC response memory under `mem_ctx`, not newly duplicated strings. The fallback from policy3 access denied to noauth policy2 changes security posture and should remain intentional.

Test signals: Tests should cover policy open with and without QoS, policy3 fallback cases, hunking over 1000 SIDs, none/some/all mapped status composition, invalid network responses with short arrays or bad domain indexes, LookupSids3/LookupNames4 variants, zero inputs, and ownership of returned names/domains/SIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.h

Purpose: Public header for Samba LSA RPC client convenience routines.

Important APIs, types, and functions: Declares LSA policy-open helpers, SID-to-name lookup helpers, name-to-SID lookup helpers, generic variants that select lookup level and newer RPC opnums, and `fetch_domain_sid()`.

Control flow: No executable logic. The prototypes expose both `dcerpc_binding_handle` APIs that return transport status plus an out `result`, and `rpc_pipe_client` wrappers that collapse the RPC result into the function return after transport success.

State and persistence behavior: No header-owned state. Output arrays and policy handles are allocated or filled by implementations using caller memory contexts.

Dependencies and integration points: Included by callers that need account/domain translation over LSARPC. It depends on generated LSA types, `policy_handle`, `dom_sid`, and `rpc_pipe_client` declarations from surrounding Samba headers.

Risks: Some prototypes use `int` for counts while others use `uint32_t`; callers must avoid negative values reaching unsigned RPC fields. The `fetch_domain_sid()` declaration is not implemented in the paired source file, indicating it is provided elsewhere or stale.

Test signals: Compile coverage for callers, API compatibility checks for generated LSA type changes, and behavior tests in `cli_lsarpc.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.c

Purpose: Implements asynchronous and synchronous client helpers for Samba's Spotlight/metadata server (`mdssvc`) RPC interface.

Important APIs, types, and functions: Exports `mdscli_new_ctx_id()`, `mdscli_get_basepath()`, connect/search/results/path/close/disconnect send-recv-sync triplets, and `mdscli_search_get_ctx()` through the header. State machines are represented by per-operation `*_state` structs and callbacks such as `mdscli_connect_open_done()`, `mdscli_connect_fetch_props_done()`, `mdscli_search_cmd_done()`, `mdscli_get_results_cmd_done()`, `mdscli_get_path_done()`, `mdscli_close_search_done()`, and `mdscli_disconnect_done()`.

Control flow: Connect opens mdssvc, sends an unknown setup call, fetches server properties, unpacks the Spotlight blob, and records path scope. Search builds an open-query blob, sends it, and expects a zero result token. Get-results sends a fetch-results blob, follows response fragments until the fragment id is zero, unpacks accumulated data, validates status, CNID container fields, and context, and returns a NULL-terminated-by-size talloc array of CNIDs. Get-path requests `kMDItemPath` for a CNID, unpacks a nested response path, strips the stored path-scope/share-path prefix, and returns a relative path. Close-search and disconnect send the corresponding close commands. Synchronous wrappers create a temporary tevent context, reject calls while `async_pending` is nonzero, poll the async request, and receive results.

State and persistence behavior: `mdscli_ctx` stores the binding handle, policy handle, generated context ids, max fragment size, device/flags, command scratch fields, share path, path scope, and an `async_pending` counter. `mdscli_search_ctx` stores query context id, unique id, live flag, scope, and query string. Contexts are talloc-owned and moved to caller contexts on successful recv calls.

Dependencies and integration points: Depends on generated `ndr_mdssvc_c` client stubs, tevent request helpers, Spotlight dalloc/marshalling helpers, and blob builders from `cli_mdssvc_util.c`. It is the client-side companion to Samba's mdssvc RPC server and Spotlight query tooling.

Risks: The code is tightly coupled to undocumented mdssvc blob shapes and magic constants such as connection id `0x6b000060`, CNID marker `0xadd`, and "search in progress" status `35`. Path prefix stripping assumes server path format and validated scope lengths. `async_pending` protects synchronous wrappers from overlapping use, but async callers must still sequence shared context operations carefully. Fragment accumulation guards integer overflow but can still allocate large server-controlled responses up to available memory.

Test signals: Tests should simulate mdssvc RPC responses for successful connect/search/results/path/close/disconnect, fragmented result streams, search-in-progress with no CNIDs, no-more-matches, bad path-scope values, bad CNID context or marker, malformed dalloc blobs, overlapping synchronous calls, and path prefix edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.h

Purpose: Public mdssvc client API for connecting to Spotlight metadata service, issuing searches, retrieving results and paths, closing searches, and disconnecting.

Important APIs, types, and functions: Forward declares `mdscli_ctx` and `mdscli_search_ctx`, exposes context helpers, and declares tevent send/recv plus synchronous wrappers for connect, search, get results, get path, close search, and disconnect.

Control flow: No executable logic. The API follows Samba's common async pattern: `*_send()` creates a `tevent_req`, callbacks complete it, `*_recv()` transfers output, and synchronous wrappers block on a private event context.

State and persistence behavior: Context pointers are opaque to callers. `mdscli_close_search_send()` and `mdscli_close_search()` take `struct mdscli_search_ctx **` because successful close consumes/moves the search context.

Dependencies and integration points: Used by RPC client tools and Spotlight search consumers. Requires tevent, dcerpc binding handles, NTSTATUS, and mdssvc generated structures available through surrounding includes.

Risks: Opaque contexts hide the single-operation-at-a-time constraint enforced in synchronous implementations. Callers must not use a search context after passing it to close.

Test signals: Compile coverage for async and sync call sites, ownership tests for close-search pointer consumption, and behavior tests in `cli_mdssvc.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_private.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_private.h

Purpose: Private mdssvc client state header shared by `cli_mdssvc.c` and `cli_mdssvc_util.c`.

Important APIs, types, and functions: Defines `struct mdsctx_id`, `struct mdscli_ctx`, and `struct mdscli_search_ctx`. The main context stores RPC binding/policy state, async counter, context ids, fragment size, device/flags, command-specific fields, share path, and path scope. The search context stores parent context, query context id, unique query id, live flag, scope, and query string.

Control flow: No executable logic. These structs are populated by connect/search helpers and read by blob builder functions.

State and persistence behavior: `mdscli_ctx` is the durable connection/session object; `mdscli_search_ctx` is durable per open query. `ctx_id.id` increments for new logical commands while `ctx_id.connection` identifies the tree connection. Fixed-size `share_path[1025]` stores the server-returned base path.

Dependencies and integration points: Included only by mdssvc client internals. It couples command blob construction, RPC call state, and response validation through shared fields such as `dev`, `flags`, `mdscmd_open.unkn2`, `path_scope_len`, and `share_path_len`.

Risks: The structure documents several fields as unknown; protocol changes can break assumptions. Fixed-size share path storage requires strict length validation in connect. Exposing mutable internals across two C files makes ordering dependencies easy to miss.

Test signals: Compile checks for internal users, connect tests that validate share/path length bounds, and protocol regression tests covering unknown fields across server versions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.c

Purpose: Builds packed Spotlight/dalloc request blobs used by the mdssvc client operations.

Important APIs, types, and functions: Exports `mdscli_blob_fetch_props()`, `mdscli_blob_search()`, `mdscli_blob_get_results()`, `mdscli_blob_get_path()`, and `mdscli_blob_close_search()`. It constructs `DALLOC_CTX`, `sl_array_t`, `sl_dict_t`, and `sl_cnids_t` trees and serializes them with `sl_pack_alloc()`.

Control flow: Each helper allocates a root dalloc context, creates the nested command array expected by mdssvc, appends a selector string such as `fetchPropertiesForContext:`, `openQueryWithParams:forContext:`, `fetchQueryResultsForContext:`, `fetchAttributes:forOIDArray:context:`, or `closeQueryForContext:`, fills context ids and command-specific dictionaries/arrays, packs the tree into an `mdssvc_blob`, frees the temporary dalloc tree, and returns NTSTATUS. The search blob includes query timing/count parameters, a unique id, `kMDItemFSName`, the query string, and scope array. The get-path blob requests `kMDItemPath` for one CNID.

State and persistence behavior: No module-global state. Request blobs are allocated under the caller's memory context. `mdscli_blob_get_path()` increments the parent context id through `mdscli_new_ctx_id()`. Temporary dalloc state is freed before return after packing.

Dependencies and integration points: Depends on mdssvc protocol types, private mdssvc client state, dalloc helpers, and Spotlight marshalling. Called by `cli_mdssvc.c` immediately before `dcerpc_mdssvc_cmd_send()`.

Risks: The request schema is mostly implicit and magic-string driven, so typos or type-name mismatches will produce server-side failures rather than compile errors. Error paths are repetitive and rely on freeing the root dalloc context. Constants such as batch counts, CNID marker `0xadd`, and context `0x6b000020` may be version-sensitive. `talloc_set_name()` is used to make dalloc type lookup work, making memory naming part of wire construction.

Test signals: Blob round-trip tests should unpack each generated blob and assert command selector, context ids, query dictionary keys, scope/query strings, CNID container fields, max-fragment behavior, and no-memory/error propagation from each dalloc insertion point.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.h

Purpose: Internal/public boundary header for mdssvc request blob builders.

Important APIs, types, and functions: Declares blob builders for fetch properties, open search, get results, get path, and close search. Each fills a `struct mdssvc_blob` from an mdssvc connection or search context.

Control flow: No executable logic. The builders are called before sending mdssvc command RPCs.

State and persistence behavior: No header-owned state. Blob lifetime is controlled by the memory context passed to the implementation.

Dependencies and integration points: Included by `cli_mdssvc.c` and implemented by `cli_mdssvc_util.c`. It depends on opaque mdssvc client context types and generated `mdssvc_blob`.

Risks: Callers must pass initialized private contexts with valid fragment size, context ids, path scope, and query fields; the header does not enforce those invariants.

Test signals: Compile coverage and blob-shape tests through `cli_mdssvc_util.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_netlogon.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_netlogon.c

Purpose: Implements Samba client helpers for NETLOGON credential setup, authenticated netlogon pipe connection, and SAM logon calls.

Important APIs, types, and functions: Exports `rpccli_pre_open_netlogon_creds()`, `rpccli_create_netlogon_creds_ctx()`, `rpccli_setup_netlogon_creds()`, `rpccli_connect_netlogon()`, `rpccli_netlogon_password_logon()`, `rpccli_netlogon_network_logon()`, and `rpccli_netlogon_interactive_logon()`. Internal helpers include `rpccli_create_netlogon_creds()` and `rpccli_setup_netlogon_creds_locked()`.

Control flow: Pre-open initializes a process-global netlogon credential database at `private/netlogon_creds_cli`. Credential-context creation derives secure channel type, client account, and server domains from `cli_credentials` and obtains a global creds context. Setup acquires an exclusive creds lock, reuses cached credentials unless forced, opens a Kerberos-authenticated netlogon pipe when configured or noauth otherwise, authenticates with current and optional old machine-account NT hashes, and stores negotiated flags. Connect chooses shared or exclusive locking based on cached creds, attempts fast Kerberos or schannel bind when possible, retries with server authentication after access failures, enforces sealed-pipe/strong-key policy if authenticated RPC was not negotiated, optionally alters to schannel, checks credentials, and returns an RPC pipe. Logon helpers build Netlogon password, network, or interactive logon levels and call `netlogon_creds_cli_LogonSamLogon()`.

State and persistence behavior: `rpccli_pre_open_netlogon_creds()` has a static `already_open` guard and installs a global DB handle into the netlogon credentials layer. Credential state persists in the dbwrap/TDB-backed netlogon creds cache and is protected by `netlogon_creds_cli_lck()`. Temporary secrets such as session-key comparison buffers are zeroed before exit; password-derived hashes live in stack structs for the duration of the call.

Dependencies and integration points: Depends on Samba RPC pipe open/bind helpers, generated Netlogon NDR stubs, `netlogon_creds_cli`, `cli_credentials`, loadparm/private path handling, dbwrap/TDB, schannel/Kerberos auth constants, SMB password hashing, GnuTLS error mapping, and local `util_netlogon` helpers. This is central to winbind/domain trust authentication flows.

Risks: This code is security-critical. Locking must prevent concurrent credential updates, fallback from Kerberos to noauth is policy-sensitive, and downgrade detection depends on negotiated flags plus `winbind sealed pipes` and `require strong key` settings. `rpccli_netlogon_interactive_logon()` dereferences `workstation[0]` without a NULL default unlike the other logon helpers. The condition `workstation[0] != '\\' && workstation[1] != '\\'` tests for not-two-leading-backslashes imperfectly for one-character strings. Password logon computes LM responses as well as NT responses, which may be undesirable in hardened configurations but follows legacy protocol behavior.

Test signals: Tests should cover global DB initialization idempotence, credential context creation from all secure channel types, cached vs forced reauth, Kerberos success/fallback/reject-AES paths, schannel alter/check paths, downgrade policy enforcement, concurrent lock behavior, anonymous trust credential rejection, challenge length validation, hash length validation, workstation NULL and slash-prefix handling, and all supported/unsupported logon info classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_netlogon.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_netlogon.h

Purpose: Public header for NETLOGON RPC client credential setup, pipe connection, and SAM logon helpers.

Important APIs, types, and functions: Forward declares required Samba client, messaging, credential, netlogon credential, and binding-handle types. Declares `rpccli_pre_open_netlogon_creds()`, `rpccli_create_netlogon_creds_ctx()`, `rpccli_setup_netlogon_creds()`, `rpccli_connect_netlogon()`, and three logon helpers for password, network, and interactive logon modes.

Control flow: No executable logic. The APIs separate credential-cache setup, authenticated netlogon pipe creation, and individual logon request construction.

State and persistence behavior: No header-owned state. Implementations persist credential state through the netlogon creds cache and return validation info allocated on caller talloc contexts.

Dependencies and integration points: Included by winbind, domain join/trust, and authentication client code needing secure Netlogon operations. It includes common RPC transport definitions and uses generated Netlogon enum/union types.

Risks: The signatures expose raw password, hash, challenge, and response blobs; callers must manage secret lifetimes and pass correct logon info classes. Output validation pointers must be checked only after `NT_STATUS_OK`.

Test signals: Compile coverage for Netlogon consumers and behavioral tests in `cli_netlogon.c`, especially parameter validation and ownership of returned validation unions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_netlogon.h -->
