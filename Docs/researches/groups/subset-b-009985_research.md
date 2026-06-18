# Research: subset-b-009985

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/lsa.c -->
# sources/user-network-fs/samba/source4/torture/rpc/lsa.c

## Purpose

This file is Samba's broad RPC torture coverage for the LSARPC interface. It exercises policy handle creation, name/SID lookup paths, policy information queries, LSA account and privilege APIs, secret storage, trusted-domain creation/deletion, trust password authentication, and exported torture suites for focused `lsa.lookupnames`, `lsa.trusted.domains`, and `lsa.privileges` runs. It is not a server implementation; it is an integration test client that validates Samba or Windows LSARPC behavior over DCE/RPC transports.

The file has two operating modes. Over named pipes or local RPC it opens policy handles and runs mutating server-state tests. Over TCP it expects unauthenticated or insufficiently protected handle-less calls such as `LookupSids3`, `LookupNames4`, `OpenPolicy*`, and `GetUserName` to fail unless a secure authenticated channel is present.

## Important APIs, Types, and Functions

The primary external APIs are generated NDR client stubs from `ndr_lsa_c.h`, `ndr_netlogon_c.h`, and shared RPC helpers from `torture/rpc/torture_rpc.h`. Security and identity data flows through `struct policy_handle`, `struct dom_sid`, `struct lsa_String`, `struct lsa_TransNameArray`, `struct lsa_SidArray`, `union lsa_PolicyInformation`, `union lsa_TrustedDomainInfo`, `struct cli_credentials`, and Netlogon credential state.

The file exposes helper entry points used by other torture code: `test_lsa_OpenPolicy2_ex()`, `test_lsa_OpenPolicy2()`, `test_lsa_OpenPolicy3_ex()`, `test_lsa_OpenPolicy3()`, `test_many_LookupSids()`, `test_lsa_Close()`, `torture_rpc_lsa()`, `torture_rpc_lsa_get_user()`, `torture_rpc_lsa_lookup_names()`, `torture_rpc_lsa_trusted_domains()`, and `torture_rpc_lsa_privileges()`.

Core local test families include:

- Policy opening: `test_OpenPolicy()`, `test_OpenPolicy_fail()`, `test_lsa_OpenPolicy2_ex()`, `test_OpenPolicy2_fail()`, `test_lsa_OpenPolicy3_ex()`, and `test_OpenPolicy3_fail()`.
- Lookup coverage: `test_LookupNames*()`, `test_LookupSids*()`, `test_many_LookupSids()`, `test_LookupSids_async()`, and the `LookupNames4`/`LookupSids3` access-denied variants.
- Account and privilege coverage: `test_CreateAccount()`, `test_OpenAccount()`, `test_EnumAccounts()`, `test_EnumPrivs()`, `test_EnumPrivsAccount()`, `test_AddPrivilegesToAccount()`, `test_RemovePrivilegesFromAccount()`, `test_GetSystemAccessAccount()`, and `test_EnumAccountRights()`.
- Secret coverage: `test_CreateSecret()` creates local and global secrets, sets encrypted current/old values, checks broken encrypted input handling, verifies returned mtime behavior, and deletes the objects.
- Trust coverage: `test_EnumTrustDom()`, `test_EnumTrustDomEx()`, `test_query_each_TrustDom()`, `test_QueryForestTrustInformation()`, `test_CreateTrustedDomain()`, and `test_CreateTrustedDomainEx_common()` validate trust enumeration, query levels, creation variants, authentication material, and cleanup.
- Trust-auth helpers: `gen_authinfo()`, `check_pw_with_ServerAuthenticate3()`, optional Heimdal-only `check_pw_with_krb5()`, and `check_dom_trust_pw()` verify Netlogon and Kerberos behavior for created trusts.

## Control Flow

`torture_rpc_lsa()` connects to `ndr_table_lsarpc`, branches on transport, and then either runs TCP failure/secure-channel checks or the full named-pipe/local suite. In the full path it opens policy handles, joins a temporary workstation account named `lsatestmach`, runs async and bulk SID lookup tests, policy info queries, secret mutation tests, lookup round trips, close semantics, leaves the joined domain, and finally validates `GetUserName`.

Lookup flow is intentionally round-trip based. SID lookups populate translated-name arrays; the translated names are immediately fed into name lookup calls to verify both directions agree. The `LookupSids3`/`LookupNames4` logic also branches on transport and authentication metadata: secure schannel or Kerberos privacy over TCP may succeed, while insecure contexts should return access-denied/protseq failures.

The trusted-domain suite opens LSARPC policy handles, creates multiple synthetic trusts, verifies enumeration/query behavior, and deletes them by SID. The extended variants repeat creation through `CreateTrustedDomainEx`, `CreateTrustedDomainEx2`, and `CreateTrustedDomainEx3`. `test_CreateTrustedDomainEx_common()` chooses trust direction, trust type, and RC4 encryption attributes in a pattern, encrypts or marshals auth info according to the RPC variant, checks created metadata, optionally verifies trust authentication, and then enumerates and removes all created trusts.

Trust password validation is multi-protocol. `check_dom_trust_pw()` creates incoming credentials for domain or DNS-domain secure channels, resolves the target DC, performs Netlogon pings, authenticates with `ServerAuthenticate3`, optionally establishes a signed/sealed Netlogon pipe, updates the trust password with `ServerPasswordSet2`, and reauthenticates with the new password/version. When Heimdal support is compiled in, `check_pw_with_krb5()` installs a custom send-to-KDC hook, forces KDC traffic to the target realm, checks canonicalization/referral results, validates expected Kerberos errors, inspects referral-ticket kvnos and encryption, and covers two-, three-, and four-part service principals.

## State and Persistence Behavior

This test file deliberately mutates the target server. It creates and deletes LSA accounts, creates local and global secrets with random names, joins and leaves a temporary machine account, and creates/deletes many trusted-domain objects. Cleanup is attempted inline after each object family, but interrupted runs can leave `torturesecret-*`, `G$torturesecret-*`, `TORTURE*`, or `lsatestmach` artifacts on the test server.

Client-side state is mostly talloc-scoped to the torture context. Policy handles are opened and closed explicitly, and `test_lsa_Close()` asserts double-close context mismatch behavior. Kerberos state uses a memory ccache and a destructor for `check_pw_with_krb5_ctx` to free principals, creds, tickets, keyblocks, addrinfo, and options. The file relies on random names and IDs for collision avoidance, but some trust and SID strings are deterministic; collisions trigger best-effort deletion/recreation in trust creation paths.

## Dependencies and Integration Points

The file integrates generated LSARPC and Netlogon clients, DCE/RPC binding/transport helpers, talloc memory ownership, tevent async RPC, Samba security SID utilities, LSA init helpers, Netlogon credential helpers, Kerberos utilities, resolver APIs, and GnuTLS crypto headers. Test behavior is controlled by torture settings such as `samba3`, `samba4`, `binding`, and `host`, and by transport type (`NCACN_NP`, `NCALRPC`, or `NCACN_IP_TCP`).

The suite assumes server support for LSARPC policy operations and, for trust-auth tests, a domain-controller environment with Netlogon and Kerberos reachable. Some branches explicitly skip or relax expectations for Samba3, Samba4, MIT Kerberos builds, or unimplemented server calls.

## Risks and Edge Cases

The highest risk is environmental flakiness: trust creation, Kerberos referral assertions, Netlogon pings, and secure-channel setup depend on domain topology, DNS/NetBIOS resolution, transport security, and server policy. The test contains many Windows-version compatibility allowances; tightening them without checking actual Windows/Samba behavior may introduce false failures.

The mutating tests are risky in shared environments because they modify LSA objects and trust passwords. Cleanup is present but not transactional. `test_CreateTrustedDomainEx_common()` creates 12 trusts per variant in the exported suite, and failures before deletion can leave persistent trust entries. Secret tests depend on transport session keys and encrypted buffer behavior; incorrect session-key handling can produce confusing server-side status codes such as `UNKNOWN_REVISION`.

Kerberos validation has compile-time bifurcation between embedded Heimdal and MIT builds, and some assertions differ by cache/referral behavior. Any refactor must preserve those conditional expectations.

## Test Signals

Primary pass/fail signals are `torture_assert_*`, `torture_fail()`, `torture_skip()`, and accumulated boolean `ret` values. Important status expectations include `NT_STATUS_OK`, `STATUS_SOME_UNMAPPED`, `NT_STATUS_NONE_MAPPED`, `NT_STATUS_ACCESS_DENIED`, `NT_STATUS_RPC_PROTSEQ_NOT_SUPPORTED`, `NT_STATUS_RPC_PROCNUM_OUT_OF_RANGE`, `NT_STATUS_OBJECT_NAME_COLLISION`, `NT_STATUS_NO_MORE_ENTRIES`, `STATUS_MORE_ENTRIES`, and Kerberos-specific error codes. Strong signals include lookup round-trip consistency, correct policy info level support, secret new/old value and mtime behavior, trust enumeration resume-handle monotonicity, trusted-domain metadata equality, Netlogon credential chaining, trust password rollover, and Kerberos referral-ticket content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/lsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/lsa_lookup.c -->
# sources/user-network-fs/samba/source4/torture/rpc/lsa_lookup.c

## Purpose

This file is a focused LSARPC lookup torture test for `LookupSids`. Unlike the broader `lsa.c`, it targets cross-domain and well-known SID translation behavior, including a required outgoing NT4/downlevel trust. It verifies how lookup levels map well-known, BUILTIN, local-domain, and trusted-domain SIDs, and it includes a regression test for the reply shape when a SID is not mapped.

## Important APIs, Types, and Functions

The file uses generated `dcerpc_lsa_*` client stubs, Samba SID utilities, and RPC torture setup helpers. Important helpers are `open_policy()`, `get_domainsid()`, `lookup_sids()`, `test_lookupsids()`, `get_downleveltrust()`, `torture_rpc_lsa_lookup()`, `test_LookupSidsReply()`, and `torture_rpc_lsa_lookup_sids()`.

`open_policy()` opens an LSARPC policy handle with `OpenPolicy2` and `SEC_FLAG_MAXIMUM_ALLOWED`. `get_domainsid()` reads `LSA_POLICY_INFO_DOMAIN`. `get_downleveltrust()` enumerates trusted domains and queries `QueryTrustedDomainInfoBySid` level 6, selecting an outgoing downlevel trust. `lookup_sids()` wraps `lsa_LookupSids`, and `test_lookupsids()` asserts both returned status and per-SID type array.

## Control Flow

`torture_rpc_lsa_lookup()` connects to LSARPC, accepts only named-pipe or local transports, opens a policy, gets the local domain SID, finds a trusted downlevel SID, and builds an eight-entry SID list: Everyone, Interactive, BUILTIN domain, BUILTIN Users, local domain, local Domain Admins RID 512, trusted domain, and trusted Domain Admins RID 512. It then invokes `test_lookupsids()` for lookup levels 0 through 10, asserting invalid-parameter results for unsupported levels and specific mapping/unmapping behavior for valid levels.

`test_LookupSidsReply()` is a separate suite entry. It looks up a synthetic domain-admin SID under a fabricated domain SID and expects `NT_STATUS_NONE_MAPPED`, while still asserting that the returned names array has one element and preserves the string form of the unmapped SID. A disabled `#if 0` block documents Windows-version disagreement around returned domain lists.

## State and Persistence Behavior

This file does not create or delete server objects. It only opens a policy handle and reads domain/trust data. The main persistent dependency is external: the target server must already have an outgoing downlevel/NT4 trust for `get_downleveltrust()` to succeed. All client memory is talloc-scoped to the torture context.

## Dependencies and Integration Points

It depends on LSARPC policy/query/lookup calls, the local domain SID, a trusted-domain inventory, SID parsing/duplication/RID helpers, and transport filtering via `dcerpc_binding_handle_get_transport()`. The exported suite `torture_rpc_lsa_lookup_sids()` registers a single `LookupSidsReply` test under the LSARPC interface.

## Risks and Edge Cases

The main operational risk is that this test is topology-specific. Without an outgoing trust to an NT4/downlevel domain, `get_downleveltrust()` calls `torture_fail()`. The expected SID type arrays encode subtle LSARPC lookup-level semantics, especially which well-known and trusted-domain SIDs are intentionally unmapped at levels 2, 3, 4, and 6. The reply-shape test allows for historical Windows differences by not enforcing the domain list assertions.

## Test Signals

Success signals are exact NTSTATUS comparisons for each lookup level and exact `enum lsa_SidType` comparisons for each SID when the status allows per-name inspection. Additional signals include transport gating, successful policy open, successful domain SID query, discovery of a suitable downlevel trust, and verification that a none-mapped lookup still returns a populated names array with the expected string.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/lsa_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/mdssvc.c -->
# sources/user-network-fs/samba/source4/torture/rpc/mdssvc.c

## Purpose

This file is the RPC torture suite for Samba's `mdssvc` Spotlight metadata service. It validates basic open/close behavior, disabled or unknown Spotlight shares, invalid policy-handle handling, malformed and crafted metadata command blobs, marshalling type safety, and the server response for fetching attributes of an unknown CNID.

## Important APIs, Types, and Functions

The key state carrier is `struct torture_mdsscv_state`, which stores the RPC pipe, mdssvc policy handle, device ID, flags, and command-specific fields used across `open`, `unknown1`, `cmd`, and `close` calls. The main fixture helpers are `torture_rpc_mdssvc_setup()`, `torture_rpc_mdssvc_teardown()`, `torture_rpc_mdssvc_open()`, and `torture_rpc_mdssvc_close()`.

Important test functions are `test_mdssvc_open_unknown_share()`, `test_mdssvc_open_spotlight_disabled()`, `test_mdssvc_close()`, `test_mdssvc_null_ph()`, `test_mdssvc_invalid_ph_unknown1()`, `test_mdssvc_invalid_ph_cmd()`, `test_mdssvc_invalid_ph_close()`, `test_mdssvc_sl_unpack_loop()`, `test_sl_dict_type_safety()`, and `test_mdssvc_fetch_attr_unknown_cnid()`. The file uses generated `dcerpc_mdssvc_*` client stubs plus mdssvc `dalloc` and Spotlight marshalling helpers (`sl_pack_alloc()`, `sl_unpack()`, `dalloc_add*()`, `dalloc_get()`, and `dalloc_dump()`).

## Control Flow

The suite is fixture-driven. Simple `rpccmd` tests connect to mdssvc and issue isolated open/close or bad-handle calls. The `disconnect1`, `disconnect2`, and `disconnect3` test cases use `torture_rpc_mdssvc_open()` to open an mdssvc session first, then deliberately submit invalid handles to `unknown1`, `cmd`, or `close`; these expect `NT_STATUS_RPC_PROTOCOL_ERROR` and free the pipe because the connection is no longer usable.

`torture_rpc_mdssvc_open()` reads torture settings `spotlight_share` and `share_mount_path`, opens the service with `dcerpc_mdssvc_open()`, then calls `dcerpc_mdssvc_unknown1()` to initialize status and flags. `torture_rpc_mdssvc_close()` closes the stored handle if the pipe is still live.

The command tests construct Spotlight request blobs. `test_mdssvc_sl_unpack_loop()` sends a static byte buffer that represents a previously problematic unpacking pattern. `test_sl_dict_type_safety()` builds nested arrays and dictionaries with contexts and query parameters, packs them into a blob, and sends `mdssvc_cmd`. `test_mdssvc_fetch_attr_unknown_cnid()` builds a `fetchAttributes:forOIDArray:context:` request for a large unknown inode/CNID, unpacks the response, and asserts the returned path object is `sl_nil_t`.

## State and Persistence Behavior

The tests open server-side mdssvc handles and close them through fixture teardown. They use random device IDs and temporary client-side dalloc trees. They do not intentionally persist metadata or server configuration, but they require server-side Spotlight share configuration. Invalid policy-handle tests intentionally break the RPC pipe; teardown copes with this by treating a NULL pipe as already disconnected.

## Dependencies and Integration Points

The file integrates the generated mdssvc RPC client, Samba torture RPC connection helpers, runtime settings from `torture_setting_string()`, POSIX UID/GID for `unknown1`, random ID generation, and the internal mdssvc marshalling/dalloc implementation. It assumes named mdssvc shares exist according to settings: `spotlight_share` defaults to `spotlight`, `no_spotlight_share` defaults to `no_spotlight`, `unknown_share` defaults to `choukawoohoo`, and `share_mount_path` defaults to `/foo/bar`.

## Risks and Edge Cases

This suite is sensitive to server configuration. Share names and Spotlight enablement must match expectations or open tests will fail. The invalid-handle tests require the server to terminate or poison the RPC context consistently with `NT_STATUS_RPC_PROTOCOL_ERROR`; subsequent use of the same pipe is unsafe. The static unpack-loop buffer and crafted dalloc structures are regression/fuzz-style inputs, so changes in marshalling may surface memory-safety or compatibility issues. There are a few assertion-goto calls that pass `ret` where `ok` is the local boolean, so edits should preserve current semantics carefully.

## Test Signals

Important signals include unchanged input IDs for unknown/disabled shares, empty `share_path`, all-zero policy handles for failed opens or NULL handles, close returning the same policy-handle blob, protocol errors for random invalid handles, successful command submission for crafted Spotlight blobs, successful pack/unpack operations, and `sl_nil_t` as the path result for an unknown CNID. The exported `torture_rpc_mdssvc()` suite groups these signals into `rpccmd`, disconnect, and `mdscmd` test cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/mdssvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/mgmt.c -->
# sources/user-network-fs/samba/source4/torture/rpc/mgmt.c

## Purpose

This file tests the DCE/RPC management interface (`mgmt`) across all registered/mappable Samba RPC interfaces. It verifies that management endpoints report interface IDs, statistics, principal names, server-listening state, and refusal to honor stop-listening requests.

## Important APIs, Types, and Functions

The file uses generated `ndr_mgmt_c.h` stubs and the NDR interface registry. `test_inq_if_ids()` is exported and reusable: it calls `mgmt_inq_if_ids`, logs each returned syntax UUID/version/name, and optionally invokes a caller-provided callback for each ID. Local helpers include `test_inq_stats()`, `test_inq_princ_name_size()`, `test_inq_princ_name()`, `test_is_server_listening()`, `test_stop_server_listening()`, and `torture_rpc_mgmt()`.

The principal-name tests integrate with GENSEC by mapping auth types to names through `gensec_get_name_by_authtype()`. `torture_rpc_mgmt()` uses `ndr_table_list()`, endpoint mapper binding via `dcerpc_epm_map_binding()`, and `lpcfg_set_cmdline()` to retarget the torture binding per interface.

## Control Flow

`torture_rpc_mgmt()` obtains a base binding, iterates over every registered NDR interface, skips unmappable tables and the management interface itself, maps a concrete endpoint for the current interface, updates `torture:binding`, and connects to the mgmt interface at that endpoint. Missing interfaces are skipped; unexpected connection errors mark the overall result false.

For each reachable endpoint it runs `is_server_listening`, `stop_server_listening`, `inq_stats`, `inq_princ_name`, and `inq_if_ids`. `test_inq_princ_name()` probes auth protocol numbers 0 through 255, records any successful principal names, and for Kerberos, NTLMSSP, and SPNEGO calls `test_inq_princ_name_size()` to verify buffer sizing behavior: size 0 should produce bad stub data, undersized buffers should return `WERR_INSUFFICIENT_BUFFER`, and `len + 1` should succeed.

## State and Persistence Behavior

The test changes only client-side binding configuration during iteration. It must not stop servers; `test_stop_server_listening()` treats a successful stop request as a failure because the endpoint should refuse it. Memory is scoped with talloc contexts, although the loop context is freed only on some paths in the current code shape.

## Dependencies and Integration Points

Dependencies include the endpoint mapper, generated mgmt client stubs, NDR table registry, GENSEC auth-type names, Samba loadparm context, and the common RPC torture connection helpers. The test dynamically covers every interface registered in the process, so adding or removing NDR tables changes the set of endpoints that are probed.

## Risks and Edge Cases

The suite is environment-dependent because not every registered interface is necessarily available on the target server or transport. Endpoint mapping failures are logged and skipped, while connection failures other than `NT_STATUS_OBJECT_NAME_NOT_FOUND` mark failure. Principal-name behavior varies by authentication provider; the code deliberately only enforces exact buffer-size behavior for KRB5, NTLMSSP, and SPNEGO. A server that actually honors `mgmt_stop_server_listening` would create a severe behavioral and test failure.

## Test Signals

Signals include successful `mgmt_inq_if_ids` with a non-NULL vector, stats array count equal to `MGMT_STATS_ARRAY_MAX_SIZE`, expected principal-name buffer errors and success thresholds, listening-state RPC success, refusal of `stop_server_listening`, and successful per-interface endpoint traversal. Output comments include UUID/version/interface names and management counters, which are useful diagnostics when a specific RPC endpoint changes availability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/mgmt.c -->
