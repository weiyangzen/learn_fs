# subset-b-009976 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/lsa.c -->
# sources/user-network-fs/samba/source4/torture/ndr/lsa.c

## Purpose

`lsa.c` is a Samba local torture suite for validating generated NDR pull behavior for LSA RPC request and response structures. It is fixture-driven: each static byte array captures an on-the-wire NDR blob, and each typed check function asserts that the generated `ndr_lsa` decoder reconstructs the expected `struct lsa_*` fields. The suite covers policy open calls, name/SID lookup variants, account and secret object operations, trusted-domain creation and update paths, privilege enumeration, and forest-trust information calls.

## Important APIs, types, and functions

The file depends on the shared NDR torture macros from `torture/ndr/ndr.h`, especially `torture_suite_add_ndr_pull_fn_test`, which wraps a generated pull routine such as `ndr_pull_lsa_OpenPolicy` with a fixture, flags, and a typed check callback. The test types are generated LSA RPC structures from `librpc/gen_ndr/ndr_lsa.h` through the local include graph. Important local callbacks include `lsarlookupnames_in_check`, `lsarlookupnames_out_check`, `lsarlookupsids_in_check`, `lsarlookupsids_out_check`, `lsaropenpolicy*_check`, secret callbacks for `lsa_CreateSecret`, `lsa_OpenSecret`, `lsa_SetSecret`, `lsa_QuerySecret`, lookup callbacks for `lsa_LookupSids2`, `lsa_LookupNames2`, `lsa_LookupNames3`, `lsa_LookupSids3`, and trust callbacks for `lsa_lsaRSetForestTrustInformation` and `lsa_SetTrustedDomainInfoByName`.

`ndr_lsa_suite(TALLOC_CTX *ctx)` is the integration entry point. It creates the `"lsa"` torture suite and registers each fixture in explicit order, usually as separate `NDR_IN` and `NDR_OUT` tests for the same RPC.

## Control flow

There is no runtime protocol state machine in this file. Control flow is registration-time and test-run-time only. At registration, `ndr_lsa_suite` allocates a suite, registers one tcase per RPC direction through the helper macro, and returns the suite to the higher-level local NDR aggregator. At execution time, the shared wrapper initializes an `ndr_pull` context over the fixture blob, applies the supplied NDR direction flag, decodes into a zeroed generated structure, verifies that all fixture bytes were consumed, then invokes the typed check callback.

The callbacks are field assertions. The name/SID lookup tests check bulk counts, reference-domain lists, translated name/SID arrays, lookup levels, lookup options, client revisions, and NTSTATUS results. Policy and object operation tests check object attributes, access masks, handles only superficially, secret value pointer layout, resume handles, and returned status. Forest-trust tests check record counts, record types, domain names, NetBIOS names, SIDs, trust direction/type/attributes, POSIX offset, auth blob sizing, and check-only behavior.

## State and persistence

All state is embedded in immutable static fixture arrays plus stack-local expected values. The suite does not modify databases, network services, files, or persistent Samba state. Handles in the fixture blobs are decoded as opaque values, but most handle validation is marked as `FIXME`, so the tests use them primarily to preserve byte layout around later fields. Memory ownership is delegated to the shared torture/NDR wrappers using talloc contexts.

## Dependencies

The file depends on Samba torture assertions, generated LSA NDR routines and structures, common SID/GUID helpers such as `dom_sid_parse_talloc`, and the shared local NDR test harness. It also depends on generated constants such as `LSA_TRUST_TYPE_UPLEVEL` and `LSA_TRUSTED_DOMAIN_INFO_FULL_INFO_INTERNAL`.

## Integration points

`ndr_lsa_suite` is included by `torture_local_ndr` in `ndr.c`, making these LSA fixtures part of the local `ndr` torture command. The test suite is therefore a regression guard for changes in LSA IDL, generated NDR code, pointer layout, conformant/varying arrays, string decoding, SID decoding, and RPC direction-specific structure annotations.

## Risks

Several checks are intentionally incomplete. Comments mark missing validation for policy and object handles, some SIDs, returned secret modification times, and query-forest-trust payload contents. `lsa_LookupSids3` has an output fixture and check function, but its `NDR_OUT` test registration is commented out, leaving that path unexecuted. The suite mostly tests successful decode/status cases and does not exercise malformed LSA payloads. Large repeated lookup fixtures with 100 names/SIDs are useful for array coverage, but many per-entry values are not deeply validated.

## Test signals

Strong signals are full fixture-byte consumption enforced by the harness, exact count and pointer-nullability checks, expected domain/name strings such as `BUILTIN`, `NT AUTHORITY`, `Account Operators`, and `Administrators`, expected status success for many responses, and forest-trust field checks including `f1.test`, `F1`, and a parsed domain SID. Weak signals are the `FIXME` assertions and unregistered output paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/lsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/nbt.c -->
# sources/user-network-fs/samba/source4/torture/ndr/nbt.c

## Purpose

`nbt.c` validates NDR decoding and selected round-trip encoding for NetBIOS-over-TCP Netlogon mailslot structures. It uses captured byte fixtures for legacy logon requests, logon responses, SAM logon responses, and primary domain controller queries, then asserts that generated `ndr_nbt` parsers interpret command discriminants, strings, SIDs, DNS-compressed names, site names, and LM token fields correctly.

## Important APIs, types, and functions

The file includes `torture/ndr/ndr.h` and generated `librpc/gen_ndr/ndr_nbt.h`. Important generated structures are `struct nbt_netlogon_packet`, `struct nbt_netlogon_response2`, and `struct netlogon_samlogon_response`. Local check callbacks include `netlogon_logon_request_req_check`, `netlogon_logon_request_resp_check`, `netlogon_samlogon_response_check`, `nbt_netlogon_packet_check`, `nbt_netlogon_packet_logon_primary_query_check`, and `netlogon_samlogon_response_check2`. `ndr_nbt_suite(TALLOC_CTX *ctx)` is the exported suite builder.

## Control flow

The suite builder registers simple pull tests for raw decode coverage and validate tests where the harness also pushes the decoded structure back to bytes and compares the result with the original fixture. The command field in `nbt_netlogon_packet` selects the active union member, so each check validates the correct branch: `LOGON_REQUEST`, `LOGON_SAM_LOGON_REQUEST`, and `LOGON_PRIMARY_QUERY`. SAM logon response fixtures validate `LOGON_SAM_LOGON_RESPONSE_EX` nested under the `nt5_ex` union arm.

## State and persistence

The file has no persistent state. Every test is deterministic and uses static fixture bytes plus stack-local expected GUID/SID values. SID creation uses `dom_sid_parse_talloc` with the torture context as allocator. GUID parsing uses `GUID_from_string` only to build expected values for comparison.

## Dependencies

Dependencies are the shared NDR torture harness, generated NBT NDR routines, Samba GUID and SID helpers, and NBT/Netlogon constants such as `LOGON_REQUEST`, `LOGON_RESPONSE2`, `NETLOGON_NT_VERSION_1`, and `LOGON_SAM_LOGON_RESPONSE_EX`.

## Integration points

`ndr_nbt_suite` is registered by `torture_local_ndr` in `ndr.c`. Its fixtures exercise the generated NBT parser used for Netlogon discovery traffic, especially mailslot discovery payloads and DNS-style encoded Netlogon response strings.

## Risks

Coverage is based on a small number of captured payloads. The suite does not test malformed compression pointers, malformed SIDs, unknown command discriminants, or short buffers. Some fields are documented in comments rather than directly asserted, for example the zero sockaddr details and next-closest-site nullability. Round-trip validation is present for several payloads, but not every fixture is registered as a validate test.

## Test signals

Important signals include exact command values, ASCII and Unicode workstation/domain names, mailslot names, domain GUIDs, domain SIDs, domain/PDC/site strings, LM token values, pad lengths, and full-consumption checks from the shared harness. Validate registrations add byte-for-byte push equivalence for selected SAM logon and packet fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/nbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/ndr.c -->
# sources/user-network-fs/samba/source4/torture/ndr/ndr.c

## Purpose

`ndr.c` implements the shared local torture harness for NDR fixture tests and assembles the top-level local `ndr` suite. It provides helper functions used by protocol-specific files to register pull-only, pull/push-validate, in/out RPC, and invalid-data tests. It also contains direct unit tests for NDR utility behavior around string terminators, GUID parsing/formatting/blob packing, GUID comparison, and syntax ID parsing.

## Important APIs, types, and functions

`struct ndr_pull_test_data` stores a fixture `DATA_BLOB`, optional input-context blob for in/out RPC tests, structure size, generated pull/push/print function pointers, NDR direction flags, libndr flags, and expected NDR error. `_torture_suite_add_ndr_pullpush_test`, `_torture_suite_add_ndr_pull_inout_test`, and `_torture_suite_add_ndr_pull_invalid_data_test` are public helpers declared in `ndr.h` and called through macros by protocol suites.

Key wrappers are `wrap_ndr_pullpush_test`, `wrap_ndr_inout_pull_test`, and `wrap_ndr_pull_invalid_data_test`. Utility tests include `test_check_string_terminator`, `test_guid_from_string_null`, `test_guid_from_string_invalid`, `test_guid_from_string`, `test_guid_from_data_blob`, `test_guid_string_valid`, `test_guid_string2_valid`, `test_guid_into_blob`, `test_guid_into_long_blob`, `test_guid_into_short_blob`, `test_compare_uuid`, and `test_syntax_id_from_string`.

## Control flow

For a normal pull/push test, the wrapper creates an `ndr_pull` over the fixture, ORs in libndr flags, enables `LIBNDR_FLAG_REF_ALLOC`, decodes into zeroed talloc memory, computes the highest consumed offset from `offset` and `relative_highest_offset`, asserts that no bytes remain unread, invokes the optional typed checker, dumps decoded data and raw bytes through `torture_ndrdump`, then optionally pushes the decoded structure back and compares the output blob with the fixture.

For in/out RPC tests, the wrapper first decodes the `NDR_IN` context blob into the shared structure, then decodes the `NDR_OUT` blob over the same structure so response parsing has request context. Invalid-data tests invert the assertion: they pass only if the generated pull routine returns the expected `enum ndr_err_code`.

`torture_local_ndr` creates the top-level suite, adds many protocol sub-suites, then adds standalone utility tests.

## State and persistence

The harness has no persistent external state. Test state lives in `struct torture_test` data allocated below each tcase. `torture_ndr_push_struct_blob_flags` steals pushed blob data into the requested memory context, then frees the push context. Debug output behavior depends on `DEBUGLEVEL`, using direct debug printing at level 10 or string collection otherwise.

## Dependencies

The implementation depends on Samba torture core types, talloc, `librpc/ndr/libndr.h`, generated `ndr_misc` helpers for GUID tests, `dlinklist.h` for appending tests to tcases, and `param/param.h` through the local torture environment. It also depends on all protocol suite constructors declared in `torture/ndr/proto.h`.

## Integration points

This file is the central integration point for local NDR testing. The protocol suites researched in this subset, including LSA, NBT, Netlogon, NTLMSSP, and NEGOEX, are all added through `torture_local_ndr`. The helper APIs declared here and in `ndr.h` are the contract used by every small fixture suite.

## Risks

The full-consumption assertion is strong, but the push equality check only runs when a push function is provided by registration. Pull-only tests may miss encoder regressions. `test_guid_from_data_blob` defines two blobs but iterates from index 1, so the binary blob case appears skipped and only the hex-string blob is tested. `test_guid_from_string_valid` is a placeholder returning true. Some wrappers assume the typed checker casts are correct; the safety of that pattern depends on macro usage in `ndr.h`.

## Test signals

Strong signals include unread-byte detection, optional byte-identical re-encoding, `LIBNDR_FLAG_REF_ALLOC` pointer allocation behavior, explicit expected NDR errors for invalid data, GUID invalid-input coverage, fixed-size blob buffer-size errors, and syntax ID parse equality. The top-level suite membership is also a signal: if a protocol suite is not added here, its fixtures will not run under the local `ndr` target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/ndr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/ndr.h -->
# sources/user-network-fs/samba/source4/torture/ndr/ndr.h

## Purpose

`ndr.h` declares the shared public helper functions and registration macros used by Samba local NDR torture suites. It hides the repetitive work of binding a generated `ndr_pull_*`, `ndr_push_*`, and `ndr_print_*` routine to static fixture bytes and a typed validation callback.

## Important APIs, types, and functions

The public helpers are `_torture_suite_add_ndr_pullpush_test`, `_torture_suite_add_ndr_pull_inout_test`, and `_torture_suite_add_ndr_pull_invalid_data_test`. They accept generated pull/push/print function pointers, fixture `DATA_BLOB`s, structure sizes, NDR direction flags, libndr flags, callback names, and typed callback shims.

Macros include `torture_suite_add_ndr_pull_test`, `torture_suite_add_ndr_pull_invalid_data_test`, `torture_suite_add_ndr_pull_fn_test`, `torture_suite_add_ndr_pull_fn_test_flags`, `torture_suite_add_ndr_pull_validate_test`, `torture_suite_add_ndr_pull_validate_test_blob`, `torture_suite_add_ndr_pull_validate_test_b64`, `torture_suite_add_ndr_pullpush_fn_test_flags`, `torture_suite_add_ndr_pull_io_test`, and `torture_suite_add_ndr_pull_io_test_flags`.

## Control flow

The macros run at suite construction time. Each macro derives generated symbol names through token concatenation, wraps the typed checker in a `void *` callback cast, creates a constant or decoded `DATA_BLOB`, supplies `sizeof(struct name)`, and chooses the correct NDR flags. The actual execution control flow lives in `ndr.c`; this header establishes which wrapper is used and whether push validation, direction-specific pull, NDR64, base64 fixture decoding, or in/out two-phase decoding will occur.

## State and persistence

There is no persistent state. The header only constructs registrations. Base64 fixture macros allocate decoded blobs on the suite talloc context, so their lifetime is tied to the suite. Other fixture macros wrap static arrays with `data_blob_const`.

## Dependencies

The header includes `torture/torture.h`, `librpc/ndr/libndr.h`, and `libcli/security/security.h`. It depends on generated NDR naming conventions: for a structure `name`, `ndr_pull_name`, `ndr_push_name`, and `ndr_print_name` must exist with compatible signatures.

## Integration points

Every protocol-specific file in this subset uses these macros to register tests. The macros are the compatibility layer between generated NDR code and the torture framework, so changes here affect all local NDR fixture suites.

## Risks

The macros rely on unchecked function pointer casts from typed callbacks to `void *` callbacks. This is a common C test-harness pattern but gives compile-time checking only inside the temporary typed assignment, not at the final stored callback call site. Token concatenation also means generated symbol naming must remain exact. Pull-only macros do not test encoder round trips. The base64 macro allocates during suite creation and assumes decoding succeeds; failed allocation or malformed base64 would surface later through the helper.

## Test signals

The header itself is not executable, but it defines the signal strength of downstream tests. Validate macros supply both pull and push functions and therefore enable byte-for-byte round-trip checks. Direction macros make `NDR_IN`, `NDR_OUT`, and `LIBNDR_FLAG_NDR64` explicit in test names. In/out macros preserve request context before decoding response fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/ndr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/negoex.c -->
# sources/user-network-fs/samba/source4/torture/ndr/negoex.c

## Purpose

`negoex.c` validates generated NDR decoding and re-encoding for a NEGOEX message array containing two messages. The fixture represents a NEGOEX acceptor negotiation message followed by acceptor metadata, including the shared signature, message headers, conversation ID, auth-scheme GUID, and metadata exchange blob.

## Important APIs, types, and functions

The file includes generated `librpc/gen_ndr/ndr_negoex.h` plus the shared NDR torture header. `negoex_MESSAGE_ARRAY_check` validates `struct negoex_MESSAGE_ARRAY` and local copies of `struct negoex_MESSAGE`. It uses `GUID_from_string` and `torture_assert_guid_equal` for stable GUID comparisons. `ndr_negoex_suite(TALLOC_CTX *ctx)` registers the fixture with `torture_suite_add_ndr_pull_validate_test`, so the shared harness performs both decode checks and push-back byte comparison.

## Control flow

The suite has one fixture. The shared harness decodes `negoex_MESSAGE_ARRAY_data` as a `negoex_MESSAGE_ARRAY`, asserts full fixture consumption, calls `negoex_MESSAGE_ARRAY_check`, then re-encodes and compares the bytes. The check function asserts an array count of two, validates message 0 as `NEGOEX_MESSAGE_TYPE_ACCEPTOR_NEGO`, and message 1 as `NEGOEX_MESSAGE_TYPE_ACCEPTOR_META_DATA`.

## State and persistence

There is no mutable state outside stack-local expected GUIDs. Both decoded messages are copied into a stack `struct negoex_MESSAGE m` for easier assertion. The metadata exchange payload is not parsed by this test beyond length.

## Dependencies

Dependencies are generated NEGOEX NDR routines and constants, the shared local NDR harness, GUID parsing helpers, and Samba torture assertions.

## Integration points

`ndr_negoex_suite` is added by `torture_local_ndr` in `ndr.c`. It protects generated NEGOEX parser and encoder behavior for SPNEGO extension negotiation payloads.

## Risks

The first message's random value is not asserted; a commented assertion hints that the random blob should be checked but is not represented in a convenient scalar form. The second message's metadata exchange blob is only checked for length, not content. Only one two-message sequence is covered, so initiator message types, alerts, verify messages, malformed lengths, and alternate extension counts are outside this file's coverage.

## Test signals

Strong signals include array count, exact `"NEGOEXTS"` signatures, message types, sequence numbers, header/message lengths, shared conversation ID, auth-scheme GUID, zero extension count in the negotiation message, metadata auth-scheme GUID, exchange blob length, full fixture consumption, and byte-identical push validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/negoex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/netlogon.c -->
# sources/user-network-fs/samba/source4/torture/ndr/netlogon.c

## Purpose

`netlogon.c` is a fixture-driven local NDR torture suite for generated Netlogon RPC structures. It validates request and response decoding for secure-channel challenge/authentication, interactive logon, and domain information exchange. It also exercises NDR64 layout for `netr_LogonGetDomainInfo` and preserves known failure cases in disabled blocks.

## Important APIs, types, and functions

The suite includes `librpc/gen_ndr/ndr_netlogon.h` and uses registration macros from `ndr.h`. Important callbacks include `netrserverauthenticate3_in_check`, `netrserverauthenticate3_out_check`, `netrserverreqchallenge_in_check`, `netrserverreqchallenge_out_check`, `netrlogonsamlogon_w2k_in_check`, `netrlogongetdomaininfo_in_check`, `netrlogongetdomaininfo_out_check_common`, `netrlogongetdomaininfo_out_check`, `netrlogongetdomaininfo_out_check64`, and `netrlogongetdomaininfo_in_check_osversion`. The suite builder is `ndr_netlogon_suite(TALLOC_CTX *ctx)`.

## Control flow

`ndr_netlogon_suite` registers direction-specific pull tests for `netr_ServerReqChallenge`, `netr_ServerAuthenticate3`, `netr_LogonSamLogon`, and `netr_LogonGetDomainInfo`. For domain info it also registers in/out tests so the request fixture is decoded first and the response fixture is decoded with request context. The NDR64 variants pass `LIBNDR_FLAG_NDR64` through the shared harness. Some known problematic round-trip or response cases remain inside `#if 0` blocks and do not execute.

## State and persistence

All test data is static. Credential, challenge, password hash, authenticator, GUID, and SID expected values are stack-local. The file does not establish a Netlogon secure channel or persist machine account state; it only decodes captured RPC payloads. In/out tests reuse one decoded structure across request and response parsing to model RPC context.

## Dependencies

Dependencies include generated Netlogon NDR routines and constants, Samba torture assertions, SID/GUID helpers such as `string_to_sid` and `GUID_from_string`, LSA trust constants referenced by trust-extension assertions, and shared NDR harness support for NDR64 and in/out decoding.

## Integration points

`ndr_netlogon_suite` is registered by the top-level local NDR suite in `ndr.c`. The fixtures guard generated IDL behavior for Netlogon RPC calls used in domain controller discovery, secure channel establishment, and domain trust information transfer.

## Risks

Some input callbacks intentionally return true without asserting fields, notably base `netr_LogonGetDomainInfo` input and the OS-version NDR64 input. The W2K validation-level-6 SAM logon response is disabled with a comment that Samba currently fails to parse it. A NDR64 pull/push test for OS-version data is also disabled because pointer value calculations likely fail. These disabled paths are valuable risk markers around pointer layout, response validation, and NDR64 round-trip behavior.

## Test signals

Strong signals include exact server/computer/account names, credentials and return credentials, negotiate flags, RID and NTSTATUS checks, interactive logon identity strings, LM/NT password hashes, validation level, return authenticators, primary and trusted domain names, DNS forest/domain names, GUIDs, SIDs, trust extension flags/type/attributes, supported encryption type differences between NDR32 and NDR64 fixtures, full-consumption checks, and in/out response-context parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/ntlmssp.c -->
# sources/user-network-fs/samba/source4/torture/ndr/ntlmssp.c

## Purpose

`ntlmssp.c` validates generated NDR parsing for NTLMSSP negotiate, challenge, and authenticate messages. It checks header signatures, message types, security-buffer lengths, flags, version fields, AV pair lists, NTLMv2 response internals, identity strings, and session-key payloads. Negotiate and challenge fixtures are also registered for pull/push byte validation.

## Important APIs, types, and functions

The file includes generated `librpc/gen_ndr/ndr_ntlmssp.h` and the shared NDR torture header. Important generated structures are `NEGOTIATE_MESSAGE`, `CHALLENGE_MESSAGE`, `AUTHENTICATE_MESSAGE`, `NTLMv2_RESPONSE`, and `AV_PAIR_LIST`. Local callbacks are `ntlmssp_NEGOTIATE_MESSAGE_check`, `ntlmssp_CHALLENGE_MESSAGE_check`, and `ntlmssp_AUTHENTICATE_MESSAGE_check`. `ndr_ntlmssp_suite(TALLOC_CTX *ctx)` registers the suite.

## Control flow

The suite first registers pull-only tests for all three message types. It then registers validate tests for `NEGOTIATE_MESSAGE` and `CHALLENGE_MESSAGE`, which adds push-back byte comparison for those two fixtures. The authenticate fixture is pull-only, likely because the message is more complex and may not be byte-stable under the encoder.

## State and persistence

There is no mutable state. Expected binary values for server challenge, reserved bytes, LM response, NTLMv2 response, client challenge, machine ID, channel bindings, and encrypted random session key are local arrays. Decoded AV pair lists are copied from nested decoded fields into stack variables for assertion.

## Dependencies

Dependencies include generated NTLMSSP NDR routines and constants, NTLMSSP version constants, AV pair identifiers, the shared local NDR harness, and Samba torture assertions.

## Integration points

`ndr_ntlmssp_suite` is registered by `torture_local_ndr` in `ndr.c`. It protects generated parsing for NTLMSSP tokens used by SMB authentication and SPNEGO negotiation paths.

## Risks

The authenticate message is not registered as a validate test, so encoder byte stability for that complex structure is not checked here. Cryptographic correctness is not tested; the suite asserts parsed bytes and fields, not that responses verify against passwords or challenges. Timestamp interpretation is left as a comment. The coverage is limited to one captured negotiate, challenge, and authenticate sequence.

## Test signals

Strong signals include `"NTLMSSP"` signature checks, message type discriminants, negotiate flag values, null domain/workstation handling, target name and target info parsing, AV pair count and per-pair names/lengths, NTLMv2 response fields, `MsvAvSingleHost` token info and machine ID, channel bindings, target name, domain/user/workstation strings, encrypted session key bytes, version fields, full fixture consumption, and byte-identical validation for negotiate and challenge messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/ntlmssp.c -->
