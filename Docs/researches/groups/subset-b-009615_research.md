# subset-b-009615 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/lsad.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/lsad.py

## Purpose

`lsad.py` implements the MS-LSAD Local Security Authority Policy interface for Impacket's DCE/RPC v5 stack. It is mostly an IDL-to-Python mapping: access-mask constants, policy/account/secret/trust structures, discriminated unions keyed by LSAD enum values, RPC request/response classes, an `OPNUMS` dispatch table, and helper functions that populate common request fields before calling `dce.request`.

## Important APIs, Types, and Functions

The module exports `MSRPC_UUID_LSAD`, `DCERPCSessionError`, policy/account/secret/trusted-domain access constants, and many NDR types. Core handle and string types are `LSAPR_HANDLE`, `LSA_UNICODE_STRING`, and local `STRING`. Policy object modelling centers on `LSAPR_OBJECT_ATTRIBUTES`, `SECURITY_QUALITY_OF_SERVICE`, `LSAPR_POLICY_INFORMATION`, `LSAPR_POLICY_DOMAIN_INFORMATION`, and pointer wrappers such as `PLSAPR_POLICY_INFORMATION`. Account and rights structures include `LSAPR_ACCOUNT_ENUM_BUFFER`, `LSAPR_USER_RIGHT_SET`, `LSAPR_PRIVILEGE_SET`, and `LSAPR_PRIVILEGE_ENUM_BUFFER`. Secret/private-data support uses `LSAPR_CR_CIPHER_VALUE` and pointer-to-pointer wrappers for query responses. Trust and forest-trust modelling includes `LSAPR_TRUSTED_DOMAIN_INFO`, `LSAPR_TRUSTED_ENUM_BUFFER(_EX)`, `LSA_FOREST_TRUST_RECORD`, `LSA_FOREST_TRUST_INFORMATION`, and collision record types.

RPC call classes cover policy open/query/set, account create/open/enumerate/rights/privileges/system-access, secret create/open/set/query, private data store/retrieve, trusted-domain enumeration, privilege lookup/enumeration, security descriptor query/set, delete, and close. Helpers include `hLsarOpenPolicy2`, `hLsarQueryInformationPolicy*`, `hLsarEnumerateAccounts*`, `hLsarAddAccountRights`, `hLsarStorePrivateData`, `hLsarQuerySecurityObject`, and related request builders.

## Control Flow

Callers bind to the LSAD UUID, open a policy handle, then pass returned handles into subsequent helpers. Helpers construct an `NDRCALL` subclass, assign handles, SIDs, strings, arrays, and access masks, then delegate serialization and transport to the DCE/RPC object. Responses carry NTSTATUS `ErrorCode` fields plus handles, union pointers, enumeration buffers, or byte arrays. Unions are selected by assigning enum-backed information classes before serialization or by response tags during deserialization.

## State and Persistence Behavior

The module stores no durable local state. It operates on remote LSA state: policy configuration, account rights, privileges, secrets/private data, trusted-domain records, and security descriptors. Local handles are opaque 20-byte NDR structs. Enumeration helpers expose context arguments for trusted-domain and privilege enumeration, but `hLsarEnumerateAccounts` always starts with the request default context.

## Dependencies and Integration Points

`lsad.py` depends on `ndr.py` for serialization, `dtypes.py` for common RPC types, `enum.py` for enum values, `rpcrt.DCERPCException`, `nt_errors`, and UUID conversion. Other modules import its types, notably `lsat.py` for `LSAPR_HANDLE` and trust arrays, and `nrpc.py` for `STRING` and forest-trust pointers. It integrates with Impacket DCE/RPC transports and SMB/RPC tests.

## Risks and Edge Cases

Several protocol operations are declared only as comments and are not present in `OPNUMS`, so callers cannot rely on full LSAD coverage. `hLsarQueryDomainInformationPolicy` builds `LsarQueryInformationPolicy` rather than `LsarQueryDomainInformationPolicy`, which sends opnum 7 instead of opnum 53. `hLsarSetSecret` appears to instantiate `LsarOpenSecret` rather than `LsarSetSecret`, so its field assignments do not match the request class. Helpers expect callers to provide correctly encoded encrypted secret values and valid privilege/right structures; little validation is performed before network submission. Rights and secret operations are security-sensitive and require appropriate remote privileges.

## Test Signals

Useful tests include NDR round-trip coverage for policy/trusted-domain unions, helper field-population tests with a fake DCE object, and integration tests against a controlled Windows target for open/query/close, account-right enumeration, private-data store/retrieve, and security descriptor query. Regression tests should specifically assert the intended opnums for domain-policy query and secret-set helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/lsad.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/lsat.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/lsat.py

## Purpose

`lsat.py` implements the MS-LSAT lookup interface for translating account names to SIDs and SIDs to names through the LSA RPC endpoint. It shares the same interface UUID as LSAD but focuses on lookup-only structures, request/response classes, `OPNUMS`, and helper constructors.

## Important APIs, Types, and Functions

The main constant is `MSRPC_UUID_LSAT`. `POLICY_LOOKUP_NAMES` is the lookup-specific access mask. `DCERPCSessionError` formats NTSTATUS values. Data model types include `LSAPR_REFERENCED_DOMAIN_LIST`, translated SID/name variants (`LSA_TRANSLATED_SID`, `LSAPR_TRANSLATED_SID_EX`, `LSAPR_TRANSLATED_SID_EX2`, `LSAPR_TRANSLATED_NAME`, and `LSAPR_TRANSLATED_NAME_EX`), `LSAP_LOOKUP_LEVEL`, `LSAPR_SID_ENUM_BUFFER`, and `RPC_UNICODE_STRING_ARRAY`.

RPC calls map opnums 14, 15, 45, 57, 58, 68, 76, and 77 for `LsarLookupNames`, `LsarLookupSids`, `LsarGetUserName`, and v2/v3/v4 lookup variants. Helpers include `hLsarGetUserName`, `hLsarLookupNames`, `hLsarLookupNames2`, `hLsarLookupNames3`, `hLsarLookupNames4`, `hLsarLookupSids`, and `hLsarLookupSids2`.

## Control Flow

Callers typically use `lsad.hLsarOpenPolicy*` with `POLICY_LOOKUP_NAMES` or another suitable mask, then pass the policy handle to LSAT helpers. Name lookup helpers set `Count`, append `RPC_UNICODE_STRING` items, set the translated SID array to `NULL`, assign lookup level and revision fields, and call `dce.request`. SID lookup helpers convert canonical SID strings into `PRPC_SID` objects with `fromCanonical`, initialize translated names to `NULL`, and issue the request. `LsarLookupNames4` and `LsarLookupSids3` are handle-less variants intended for newer lookup flows.

## State and Persistence Behavior

The module is stateless and read-oriented. Remote state is only queried, not modified. Returned domain lists and translated arrays are transient NDR response objects. `MappedCount` is passed as a scalar field in request classes but helpers leave it at the NDR default and rely on the server to populate response counts.

## Dependencies and Integration Points

It depends on common dtypes, `samr.SID_NAME_USE`, `lsad.LSAPR_HANDLE`, `PLSAPR_TRUST_INFORMATION_ARRAY`, `ndr.py`, `rpcrt`, `nt_errors`, and UUID conversion. It integrates tightly with LSAD policy-handle acquisition and with Impacket callers that need account resolution before SAMR, LSAD, or Netlogon operations.

## Risks and Edge Cases

Only some newer operations have helpers; `LsarLookupSids3` and `LsarLookupNames4` classes exist but helper coverage is incomplete for all combinations. The helpers accept raw names and canonical SID strings with minimal validation, so invalid encoding, missing NUL behavior in underlying string types, or malformed SIDs fail during packing or remotely. Large lookup batches rely on conformant-array serialization and should be tested for count and referent correctness. The same UUID as LSAD means binding context and opnum choice are the meaningful distinction.

## Test Signals

Tests should validate helper-generated request fields, array lengths, SID conversion, and union-free response parsing. Integration signals include lookup of well-known SIDs and names, partial mappings that return nonzero `MappedCount`, unknown names, and v2/v3 behavior on domain controllers with different lookup levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/lsat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/mgmt.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/mgmt.py

## Purpose

`mgmt.py` implements the standard DCE/RPC Remote Management Interface from C706. It lets a client query a remote RPC server for registered interface IDs, runtime statistics, listening status, stop-listening behavior, and principal names.

## Important APIs, Types, and Functions

`MSRPC_UUID_MGMT` identifies the management interface. `DCERPCSessionError` formats management errors through `nt_errors`. The principal data types are `rpc_if_id_p_t_array`, `rpc_if_id_vector_t`, `rpc_if_id_vector_p_t`, and `error_status`. RPC call classes are `inq_if_ids`, `inq_stats`, `is_server_listening`, `stop_server_listening`, and `inq_princ_name` with matching response classes. `OPNUMS` maps opnums 0 through 4. Helpers are `hinq_if_ids`, `hinq_stats`, `his_server_listening`, `hstop_server_listening`, and `hinq_princ_name`.

## Control Flow

After binding to the management UUID, helpers create the matching request and call `dce.request`. `inq_if_ids` has no input and returns an interface vector pointer. `inq_stats` sends a requested statistic count and receives a `DWORD_ARRAY`. Listening and principal-name helpers pass `checkError=False`, allowing callers to inspect returned status values rather than raising through the normal DCE error path.

## State and Persistence Behavior

The module has no local persistence. Most calls are read-only, but `stop_server_listening` can alter the remote RPC server runtime state by asking it to stop accepting calls. Returned interface vectors and stats are transient response objects.

## Dependencies and Integration Points

The module uses NDR call/struct/pointer/array classes, `epm.PRPC_IF_ID`, common dtypes, UUID conversion, and `rpcrt.DCERPCException`. It complements endpoint mapper discovery by querying the server runtime directly after a transport is established.

## Risks and Edge Cases

`stop_server_listening` is operationally disruptive and should be guarded by caller intent and privileges. `inq_princ_name` returns a raw conformant varying array rather than a higher-level string wrapper, so callers must decode it correctly. The `structure64` variant for `rpc_if_id_vector_t` changes `count` to `ULONGLONG`, making NDR64 coverage important.

## Test Signals

Unit tests should verify opnums, NDR64 vector layout, and helper `checkError` behavior. Integration tests can bind to a known RPC service, call `hinq_if_ids`, `hinq_stats`, and `his_server_listening`, and avoid `hstop_server_listening` except in an isolated server fixture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/mgmt.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/mimilib.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/mimilib.py

## Purpose

`mimilib.py` implements a small DCE/RPC interface for the Mimikatz RPC service based on gentilkiwi's IDL. It defines bind/unbind/command calls and helper code for Diffie-Hellman public-key exchange material used by the client-side workflow.

## Important APIs, Types, and Functions

`MSRPC_UUID_MIMIKATZ` identifies the interface. `DCERPCSessionError` formats NTSTATUS errors. Crypto blob structures built on Impacket `Structure` include `PUBLICKEYSTRUC`, `DHPUBKEY`, and `PUBLICKEYBLOB`; NDR types include `MIMI_HANDLE`, `BYTE_ARRAY`, `PBYTE_ARRAY`, `MIMI_PUBLICKEY`, and `PMIMI_PUBLICKEY`. RPC call classes are `MimiBind`, `MimiUnbind`, and `MimiCommand` with matching responses, registered in `OPNUMS` for opnums 0, 1, and 2. `MimiDiffeH` computes 1024-bit modular DH public values and shared secrets. Helpers `hMimiBind` and `hMimiCommand` populate request objects.

## Control Flow

A caller generates a public key, wraps it in `MIMI_PUBLICKEY`, calls `hMimiBind`, receives a server public key and `MIMI_HANDLE`, derives a shared secret externally, encrypts command bytes externally, and sends them with `hMimiCommand`. `hMimiCommand` sets the command length and stores the encrypted command as a conformant byte array.

## State and Persistence Behavior

The module maintains local ephemeral DH values inside each `MimiDiffeH` instance: generator, prime, private key, public key, and shared secret. Remote state is represented by the `MIMI_HANDLE` returned from bind and consumed by command/unbind. No files or durable state are written.

## Dependencies and Integration Points

It depends on `binascii`, Python `random`, Impacket dtypes/NDR/rpcrt/Structure, UUID conversion, and `nt_errors`. It integrates with DCE/RPC transports and any external command encryption/decryption logic used by Mimikatz RPC clients.

## Risks and Edge Cases

`MimiDiffeH` uses Python's `random.getrandbits`, which is not a cryptographic RNG. The module does not implement the command encryption layer, RC4 use, padding, or response decryption; callers must apply the correct protocol behavior around these raw request classes. Public key byte conversion strips leading zeroes unless hex normalization happens to preserve them, so fixed-size blob construction should be tested. This interface is explicitly security-sensitive and generally associated with credential tooling.

## Test Signals

Tests should cover DH toy-vector behavior from the `__main__` block, public-key blob layout, bind request serialization, command length/count handling, and fake-DCE helper assertions. Integration testing should use an isolated lab service only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/mimilib.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/ndr.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/ndr.py

## Purpose

`ndr.py` is Impacket's core Network Data Representation serialization runtime for DCE/RPC v5. It provides primitive NDR types, arrays, structures, unions, pointers, top-level calls, NDR64 transfer-syntax switching, referent packing/unpacking, alignment handling, and debug dumping. Most DCE/RPC interface modules in this tree are declarative subclasses of these base classes.

## Important APIs, Types, and Functions

`NDR` is the base field container. It interprets `commonHdr`, `structure`, `referent`, `structure64`, default-value expressions, literal fields, and nested NDR classes. Primitive classes include signed/unsigned small, short, long, hyper, float, double, char, boolean, and `NDRENUM`. `NDRCONSTRUCTEDTYPE` adds pointer/union detection and referent traversal. Array classes include `NDRArray`, `NDRUniFixedArray`, `NDRUniConformantArray`, `NDRUniVaryingArray`, `NDRUniConformantVaryingArray`, `NDRVaryingString`, and `NDRConformantVaryingString`. `NDRSTRUCT` implements structure alignment and conformant-array size relocation. `NDRUNION` implements discriminated arms. `NDRPOINTERNULL`, singleton `NULL`, and `NDRPOINTER` model null, embedded, and top-level pointers. `NDRCALL` serializes complete request/response stubs and aliases to `NDRTLSTRUCT`. `UNKNOWNDATA` captures raw opaque data.

## Control Flow

Construction walks declared fields and creates nested NDR instances, default Python values, byte literals, or lists. `getData` aligns fields, packs primitives with `struct.pack`, delegates nested NDR serialization, and appends referent data for constructed types. `fromString` mirrors the process with alignment, `struct.unpack_from`, array-size extraction, union tag selection, and referent parsing. `changeTransferSyntax` recursively switches objects to NDR64 when the NDR64 UUID is negotiated, replacing headers, structures, alignments, and compatible nested objects. `NDRCALL` treats pointer and union fields as top-level objects so their referents are emitted in the call stub rather than embedded incorrectly.

## State and Persistence Behavior

Objects keep all state in `self.fields`, `_isNDR64`, current `commonHdr`/`structure`, and array-size metadata such as `MaximumCount` or `ActualCount`. Pointers get random nonzero referent IDs by default, so byte-for-byte serialization may vary unless callers set IDs explicitly. No durable state is persisted.

## Dependencies and Integration Points

The module depends on `struct`, `inspect`, `random`, `six`, Impacket logging, Impacket enum support, and UUID conversion. It is the serialization substrate for LSAD, LSAT, MGMT, NRPC, MIMILIB, and other DCE/RPC protocol modules. It also integrates with `rpcrt` through request/response classes mapped by interface `OPNUMS`.

## Risks and Edge Cases

Alignment and conformant-array behavior are complex and easy to regress. The code uses `eval` to compute default field expressions from class declarations, so malformed declarations can fail late or execute expression logic. Pointer null assignment has special behavior that can replace nested `Data` pointers. Union alignment intentionally deviates from a strict reading of the standard based on observed packets. NDR64 support is partial in some paths, with an explicit exception when attempting to switch back from NDR64. Random referent IDs complicate deterministic tests. Python 3 byte/list handling has special cases for char arrays.

## Test Signals

High-value tests are round-trip pack/unpack fixtures for primitives, nested structs, conformant and conformant-varying arrays, arrays of constructed types with referents, top-level versus embedded pointers, null pointers, unions with known/default tags, NDR64 enum and pointer width, and RPC call classes with multiple referents. Regression tests should assert alignment padding length and semantic equality rather than exact random referent IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/ndr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/nrpc.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/nrpc.py

## Purpose

`nrpc.py` implements much of the MS-NRPC Netlogon Remote Protocol interface. It combines a large IDL mapping for domain controller discovery, secure-channel authentication, logon validation, replication deltas, trusts, control calls, and UAS compatibility calls with helper cryptographic routines for Netlogon credentials, authenticators, signing, sealing, and SSP type-1 messages.

## Important APIs, Types, and Functions

`MSRPC_UUID_NRPC` identifies the Netlogon interface. `DCERPCSessionError` formats errors from both `system_errors` and `nt_errors`. Constants cover DNS name types, OS suite/product flags, Netlogon access masks, control function codes, SSP message flags, signature algorithms, and seal algorithms. Core secure-channel types include `NETLOGON_CREDENTIAL`, `NETLOGON_AUTHENTICATOR`, `NETLOGON_SECURE_CHANNEL_TYPE`, `NL_TRUST_PASSWORD`, `NETLOGON_CAPABILITIES`, and password/hash structures. Discovery/trust types include `DOMAIN_CONTROLLER_INFOW`, site-name arrays, socket/DNS records, `DS_DOMAIN_TRUSTSW`, and forest-trust pointers from LSAD. Logon types include `NETLOGON_LOGON_IDENTITY_INFO`, `NETLOGON_LEVEL`, logon info classes, validation unions, SAM validation structures, groups, extra SIDs, and session keys. Replication support includes many `NETLOGON_DELTA_*` structures, delta ID/union mappings, sync state, and delta arrays. Control and UAS structures model the older management calls.

Cryptographic helpers include `ComputeNetlogonCredential`, `ComputeNetlogonCredentialAES`, `ComputeSessionKeyAES`, `ComputeSessionKeyStrongKey`, authenticator generation, sequence-number derivation/encryption, MD5/SHA256 signatures, `SIGN`, `SEAL`, `UNSEAL`, `CompressedUtf8String`, and `getSSPType1`. RPC classes cover opnums 0 through 49 with gaps, and `OPNUMS` registers implemented calls. Helper request builders cover challenge/authenticate, DC discovery, password get/set, domain info, capabilities, and trust info.

## Control Flow

Typical secure-channel setup starts with `hNetrServerReqChallenge`, derives a session key from shared secret and challenges, computes a client credential, and calls one of the authenticate helpers. Later authenticated calls pass `NETLOGON_AUTHENTICATOR` values generated from the stored credential and session key. Signing and sealing compute Netlogon auth signatures over message bytes, confounders, sequence numbers, and session keys, with RC4/HMAC-MD5 or AES/HMAC-SHA256 depending on the `aes` flag. RPC helpers normalize many string parameters through `checkNullString`, assign enum/union tags where needed, seed zero return authenticators when omitted, and call `dce.request`.

## State and Persistence Behavior

The module itself has no durable local state, but helper crypto functions are stateful through caller-managed session keys, credentials, timestamps, sequence numbers, and authenticators. Remote operations can query or affect domain-controller discovery, secure-channel password material, DNS records, Netlogon service bits, SAM/logon validation, replication cursors, and trust information. `ComputeNetlogonAuthenticator*` uses current wall-clock time for timestamps.

## Dependencies and Integration Points

It depends on `time`, `struct`, `six`, `hmac`, `hashlib`, `Cryptodome.Cipher` DES/AES/ARC4, Impacket NDR and dtypes, `samr`, `lsad`, `rpcrt`, `Structure`, `ntlm`, `crypto`, and logging. It integrates with LSAD for forest trust structures, SAMR for logon-hour and integer types, and DCE/RPC transport bindings to the Netlogon UUID. Higher-level Impacket tools use this module for machine-account authentication, domain discovery, trust enumeration, and Netlogon signing/sealing.

## Risks and Edge Cases

If `pycryptodomex` is missing, import only logs critical messages; later crypto calls can fail with missing DES/AES/ARC4 names. `checkNullString` assumes string-like values and appends `'\x00'`, which can be fragile for bytes versus str callers. Crypto correctness is sensitive to negotiated flags, challenge order, sequence numbers, confounder presence, and AES versus RC4 mode. Some declared operations are intentionally omitted from `OPNUMS`, including password set opnum 6 and chain/client DNS update entries. Several structures contain dummy/reserved fields and duplicated class names, so layout regression is a risk. Netlogon operations are high-impact because they involve machine trust, password material, replication data, and authentication decisions.

## Test Signals

Tests should include known-vector coverage for session key derivation, DES/AES credentials, authenticator timestamps with controlled time, signing/sealing/unsealing round trips, compressed UTF-8 DNS labels, and SSP type-1 buffers. NDR tests should cover union tag selection for logon, validation, delta, control, workstation, and domain-information unions. Fake-DCE helper tests should assert string normalization and field population. Integration tests require an isolated domain controller and should cover challenge/authenticate, DC discovery, capabilities, and trust enumeration without altering production trust passwords.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/nrpc.py -->
