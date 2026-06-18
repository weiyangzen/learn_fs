# Research: subset-b-009628

Grouped research for Impacket HTTP, Kerberos, PAC, and LDAP source files. Each source section is bounded for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/http.py -->
# sources/user-network-fs/impacket/impacket/http.py

Purpose: provides `HTTPClientSecurityProvider`, a small HTTP authentication helper for MS-RPCH style clients and relay-friendly flows. It supports Basic and NTLM in practice, advertises constants for Auto, Basic, NTLM, Negotiate, Bearer, and Digest, and exposes a separate NTLM Type 1 send path so callers can inject or relay negotiate messages.

Important APIs: `set_credentials()` stores cleartext credentials, LM/NT hashes, AES keys, and optional Kerberos tickets, though Kerberos is explicitly rejected for HTTP NTLM/Basic paths. `parse_www_authenticate()` extracts offered schemes by substring. `connect()` returns `HTTPConnection` or `HTTPSConnection`. `get_auth_headers()` dispatches to Basic or Auto/NTLM. `send_ntlm_type1()` sends a zero-length authorized request, expects a 401 challenge, captures `WWW-Authenticate`, stores NTLM target info as AV pairs, and returns the raw challenge. `get_auth_headers_auto()` completes NTLM Type 3 or falls back to Basic if Auto discovered Basic.

Control flow and state: the object is stateful. Credentials, selected auth type, discovered auth types, and NTLM target info persist across calls. Auto mode mutates `__auth_type` to `NTLM` or `Basic` after negotiation. The NTLM path performs network I/O during header construction because it must obtain a server challenge.

Dependencies and integration: relies on stdlib `http.client`/`httplib`, `ssl`, `base64`, `re`, `binascii`, and `impacket.ntlm`. It is intended to be plugged into HTTP protocol clients that can pass an open HTTP object plus method/path/header context.

Risks and test signals: `parse_www_authenticate()` is substring-based and case-sensitive, so unusual header casing or scheme names embedded in parameters can mis-detect. Basic refuses hashes/AES/TGT/TGS but sends base64 cleartext when enabled. HTTPS uses `ssl.PROTOCOL_SSLv23`, which is a legacy compatibility choice. Tests should cover odd-length hash normalization, 401 challenge parsing, no-NTLM fallback to Basic, unsupported auth types, absence of `WWW-Authenticate`, and preservation of NTLM AV pair metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/http.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/__init__.py -->
# sources/user-network-fs/impacket/impacket/krb5/__init__.py

Purpose: marks `impacket.krb5` as a package and contains only licensing comments plus `pass`. It has no runtime exports, initialization side effects, or persistence behavior.

Important APIs/types/functions: none. Consumers import concrete submodules such as `asn1`, `constants`, `crypto`, `ccache`, `gssapi`, `kerberosv5`, `keytab`, `kpasswd`, `pac`, and `types`.

Control flow and state: module import executes no logic beyond `pass`; there is no state, I/O, or configuration.

Dependencies and integration: integration point is package identity for relative imports like `from impacket.krb5 import constants`.

Risks and test signals: low risk. Tests only need to ensure package imports continue to work and relative imports remain valid if packaging metadata changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/asn1.py -->
# sources/user-network-fs/impacket/impacket/krb5/asn1.py

Purpose: defines Kerberos ASN.1 structures for RFC 4120 and selected MS-KILE extensions using `pyasn1`. It is the schema layer used by ticket acquisition, cache conversion, GSS, password change, and PAC-related code to encode and decode DER/BER Kerberos messages.

Important APIs: helper builders `_application_tag()`, `_sequence_component()`, `_sequence_optional_component()`, `_vno_component()`, and `_msg_type_component()` centralize explicit/context/application tagging and protocol-version/message-type constraints. Mutation helpers `seq_set()`, `seq_set_dict()`, `seq_set_iter()`, `seq_set_flags()`, and `seq_append()` reduce boilerplate for nested pyasn1 sequences.

Important types: primitive wrappers include `Int32`, `UInt32`, `Microseconds`, `KerberosString`, `Realm`, `PrincipalName`, `KerberosTime`, `HostAddress`, `AuthorizationData`, `PA_DATA`, `KerberosFlags`, `EncryptedData`, `EncryptionKey`, and `Checksum`. Protocol structures include `Ticket`, `EncTicketPart`, `KDC_REQ_BODY`, `AS_REQ`, `TGS_REQ`, `AS_REP`, `TGS_REP`, `Authenticator`, `AP_REQ`, `AP_REP`, `KRB_SAFE`, `KRB_PRIV`, `KRB_CRED`, `KRB_ERROR`, preauth structures (`PA_ENC_TS_ENC`, `ETYPE_INFO`, `ETYPE_INFO2`), S4U/PAC option structures, key-list structures, superseded-user data, and DMSA key package data.

Control flow and state: this module is declarative. Runtime behavior occurs when other modules instantiate these classes and pyasn1 enforces tags, optional fields, and constraints. There is no persistence or mutable global state beyond class definitions.

Dependencies and integration: depends on `pyasn1.type` and `impacket.krb5.constants`. `kerberosv5.py` constructs AS/TGS/AP messages from these schemas; `ccache.py` decodes AS/TGS/KRB_CRED; `kpasswd.py` extends and uses several structures; `types.py` converts between Python wrappers and ASN.1.

Risks and test signals: schema drift is high impact because tag or field order mistakes break interoperability. `UInt32` intentionally lacks the commented range constraint. `KerberosString` accepts liberal UTF-8 rather than a strict alphabet. Tests should round-trip representative AS_REQ, TGS_REQ, AP_REQ, KRB_CRED, KRB_ERROR, S4U, and PAC option encodings and check optional-field omission paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/asn1.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/ccache.py -->
# sources/user-network-fs/impacket/impacket/krb5/ccache.py

Purpose: implements MIT Kerberos credential cache parsing/serialization plus conversion between ccache credentials, Impacket TGT/TGS dictionaries, and kirbi/KRB_CRED blobs. It lets tools reuse tickets from `KRB5CCNAME`, save new tickets, and convert ticket formats.

Important APIs/types: binary `Structure` classes model headers, counted strings, key blocks, times, addresses, authdata, principals, and credentials. `Principal` converts between cache principals and `types.Principal`. `Credential` parses a single credential and exposes `toTGT()`/`toTGS()`. `CCache` parses complete caches, serializes via `getData()`/`saveFile()`, finds credentials with `getCredential()`, imports AS/TGS replies with `fromTGT()`/`fromTGS()`, reads environment caches with `parseFile()`, and converts kirbi files using `fromKRBCRED()`/`toKRBCRED()`.

Control flow and persistence: `CCache.__init__()` detects file version, parses v4 headers, primary principal, then credentials while skipping `krb5_ccache_conf_data`. `fromTGT()` and `fromTGS()` decrypt reply encrypted parts using key usages 3 and 8, derive credential metadata and ticket blobs, and append credentials. `parseFile()` reads `KRB5CCNAME`, searches for a requested SPN, then falls back to a krbtgt principal. File persistence is direct read/write of binary ccache or kirbi data.

Dependencies and integration: uses `pyasn1` DER codecs, Kerberos ASN.1 schemas, `crypto`, `constants`, `types`, and Impacket logging. `kerberosv5.py`, `ldap.py`, and `kpasswd.py` use it for cache-based authentication.

Risks and test signals: malformed caches can break offset arithmetic because parsing trusts embedded lengths. `getCredential(anySPN=True)` has complex SPN normalization including host-only S4U cases and should be tested with ports, case, service changes, and machine-account names. `reverseFlags()` normalizes pyasn1 bit strings to 32 bits. Time conversion mixes naive epoch timestamps with UTC-aware kirbi output. Tests should round-trip ccache v3/v4, AS/TGS imports, KRB_CRED conversion, missing `renew-till`, absent `KRB5CCNAME`, and malformed counted strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/ccache.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/constants.py -->
# sources/user-network-fs/impacket/impacket/krb5/constants.py

Purpose: centralizes Kerberos and MS-KILE numeric constants as `Enum` classes and helper maps. It is the numeric contract used by ASN.1 schemas, crypto selection, KDC requests, GSS flags, PAC signing, and error rendering.

Important APIs/types: `encodeFlags(flags)` returns a 32-element bit list for pyasn1 bit strings. Enums cover application tags, principal/name types, preauthentication data types, address types, authorization data, transited encoding, protocol version, message types, error codes, ticket flags, KDC options, AP options, PAC options, encryption types, and checksum types. `ERROR_MESSAGES` maps Kerberos error numbers to short and descriptive strings.

Control flow and state: pure constants plus `encodeFlags()`. No persistence or I/O.

Dependencies and integration: imports Impacket's DCE/RPC `Enum`. `asn1.py` uses application tag/message constants, `kerberosv5.py` uses options, enctypes, preauth types, and errors, `crypto.py` maps encryption/checksum IDs, and `pac.py` uses checksum IDs and non-Kerberos checksum salts.

Risks and test signals: numeric mistakes silently produce non-interoperable tickets or misleading errors. `encodeFlags()` does not bounds-check flag indexes; invalid indexes raise list errors. Tests should assert important enum values, `encodeFlags()` bit positions, and `KerberosError` rendering for generic NT-status e-data and superseded-user e-data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/constants.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/crypto.py -->
# sources/user-network-fs/impacket/impacket/krb5/crypto.py

Purpose: implements Kerberos cryptographic profiles for DES-CBC-MD5, DES3, AES128/256 CTS-HMAC-SHA1-96, and RC4-HMAC, plus checksums, string-to-key, PRF, CF2, and key derivation helpers.

Important APIs/types: public classes/constants include `Enctype`, `Cksumtype`, `InvalidChecksum`, and `Key`. Public helpers include `random_to_key()`, `string_to_key()`, `encrypt()`, `decrypt()`, `prf()`, `make_checksum()`, `verify_checksum()`, `get_matching_aes_key()`, `get_kerberos_key_for_enctype()`, `cf2()`, and `generate_kerberos_keys()`. Internal profiles `_SimplifiedEnctype`, `_DESCBC`, `_DES3CBC`, `_AESEnctype`, `_AES128CTS`, `_AES256CTS`, `_RC4`, and checksum profiles back `_enctype_table` and `_checksum_table`.

Control flow and state: profile methods derive usage-specific keys, add confounders, encrypt, append/truncate HMACs, verify in constant time, and strip confounders. AES implements ciphertext stealing; RC4 implements RFC 4757 usage mapping and errata fallback for key usage 9. There is no persistent state; randomness comes from `os.urandom`.

Dependencies and integration: depends on PyCryptodome ciphers/hashes/KDF, `six`, `struct`, `binascii`, and Kerberos constants. `kerberosv5.py`, `ccache.py`, `gssapi.py`, `kpasswd.py`, and `pac.py` rely on these profiles for protocol key usages and checksum generation.

Risks and test signals: the top-level `encrypt()` wrapper does `bytes(confounder)`, which raises for `None`; many callers use profile methods directly where `None` is supported. DES support is legacy and includes hand-rolled parity/string-to-key code. `generate_kerberos_keys()` infers AD salts and raw UTF-16 password handling. Tests should use known RFC vectors for AES/RC4/DES3, bad-MAC `InvalidChecksum`, wrong key length, AES key selection, CF2, PAC checksum types, and the `encrypt(..., confounder=None)` wrapper edge.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/crypto.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/gssapi.py -->
# sources/user-network-fs/impacket/impacket/krb5/gssapi.py

Purpose: implements partial Kerberos GSS-API token wrapping and MIC support for RC4 and AES Kerberos session keys, including LDAP-specific wrap/unwrap formats and mechanism-independent token framing.

Important APIs/types: constants define GSS flags and key usages. `MechIndepToken` encodes/decodes the application 0 token with Kerberos OID and BER-style lengths. `CheckSumField` models the AP-REQ checksum field. `GSSAPI(cipher)` selects `GSSAPI_RC4`, `GSSAPI_AES128`, or `GSSAPI_AES256`. RC4 and AES classes expose `GSS_GetMIC()`, `GSS_Wrap()`, `GSS_Unwrap()`, `GSS_Wrap_LDAP()`, and `GSS_Unwrap_LDAP()`.

Control flow and state: methods are stateless except for random confounder generation. RC4 computes HMAC-MD5 signatures, encrypts sequence numbers, optionally seals with ARC4, and has special auth-data handling for DCE/RPC. AES uses RFC 4121 token fields, checksum profiles, encrypts data plus token trailer, and rotates by RRC/EC for wrap tokens. LDAP paths prepend signatures differently from DCE/RPC paths.

Dependencies and integration: depends on PyCryptodome HMAC/MD5/ARC4, `impacket.structure`, `impacket.krb5.crypto`, and Kerberos constants. `ldap.py` uses `GSS_Wrap_LDAP()` for signed/sealed LDAP. `kerberosv5.py` uses `CheckSumField` and GSS flags in AP authenticators.

Risks and test signals: sequence-number verification is minimal; unwrap often mirrors wrap and does not deeply validate token checksums or directions. AES unwrap assumes token sizing and may produce surprising slicing when EC is zero. RC4 confounders are ASCII letters from `SystemRandom` fallback. Tests should cover MIC padding, mechanism length encoding over 127 bytes, RC4/AES LDAP round-trips, DCE/RPC auth-data paths, sequence numbers, encrypt=False paths, and tampered token rejection expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/gssapi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/kerberosv5.py -->
# sources/user-network-fs/impacket/impacket/krb5/kerberosv5.py

Purpose: provides high-level Kerberos client helpers: send KDC messages over TCP, obtain TGTs and TGSs, build SPNEGO Kerberos Type 1/Type 3 tokens for DCE/RPC, and render Kerberos errors.

Important APIs/types: `sendReceive()` frames KDC TCP messages with 4-byte length and decodes `KRB_ERROR`. `getKerberosTGT()` builds AS_REQ, handles preauth discovery, selects AES or RC4, encrypts PA-ENC-TIMESTAMP, decrypts AS_REP, and returns `(tgt, cipher, key, sessionKey)`. `getKerberosTGS()` builds AP_REQ inside TGS_REQ, decrypts TGS_REP, follows referrals recursively, and returns a new session key. `getKerberosType1()` obtains/cache-loads TGT/TGS and emits SPNEGO NegTokenInit with AP_REQ. `getKerberosType3()` processes AP_REP and returns a NegTokenResp. `SessionKeyDecryptionError` preserves AS-REP cracking context, and `KerberosError` extends SMB `SessionError`.

Control flow and state: functions are mostly stateless, with randomness for nonces. `getKerberosTGT()` first sends an AS_REQ with PAC request, then either handles no-preauth AS_REP or parses `METHOD_DATA` to derive the client key and send timestamp preauth. It falls back from AES to RC4 when KDC reports unsupported enctypes and password hashes are available or computable. `getKerberosType1()` optionally reads ccache before network acquisition.

Dependencies and integration: integrates `asn1`, `types`, `constants`, `crypto`, `ccache`, `gssapi`, `spnego`, SMB session errors, NT status tables, sockets, and pyasn1. LDAP and SMB/RPC clients rely on these helpers for Kerberos authentication.

Risks and test signals: `sendReceive()` assumes TCP and does not use UDP fallback. Recursive referral handling in `getKerberosTGS()` needs loop protection tests. Cipher selection relies on KDC hints and may fail if `encryptionTypesData` lacks the selected enctype. Nonce validation is TODO. Tests should simulate KDC errors, preauth required/no-preauth flows, AES-to-RC4 fallback, cache TGT/TGS use, AP_REP error tokens, generic NT-error rendering, superseded-user rendering, and referral chains.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/kerberosv5.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/keytab.py -->
# sources/user-network-fs/impacket/impacket/krb5/keytab.py

Purpose: parses, serializes, searches, and writes Kerberos keytab files, with helper logic to load matching keys into common Impacket CLI option fields.

Important APIs/types: `Enctype` enumerates DES, DES3, AES, and RC4 keytab key types. `CountedOctetString`, `KeyBlock`, `KeytabPrincipal`, and `KeytabEntry` model the binary keytab format. `Keytab` stores entries, serializes with `getData()`, searches with `getKey()`, reads/writes files with `loadFile()`/`saveFile()`, and maps matched keys into `options.aesKey` or `options.hashes` through `loadKeysFromKeytab()`.

Control flow and persistence: `Keytab.__init__()` parses the mini header and iterates entries until input is exhausted. Entry size is signed; negative sizes mark deleted entries. `getKey()` uppercases principals, optionally ignores realm, returns a requested enctype immediately, or chooses preferred AES256, AES128, then RC4. Persistence is direct binary file read/write.

Dependencies and integration: uses Impacket `Structure`, logging, `six.b`, `struct`, `datetime`, `binascii`, and Python `Enum`. It integrates with scripts that accept keytab-based credentials by mutating parsed option objects.

Risks and test signals: parsing trusts size fields and can be confused by malformed or truncated keytabs. The optional 32-bit kvno check compares `self.rest[:4]` to a list rather than bytes, so all-zero detection is suspicious. Realm-insensitive matching can return the wrong principal in multi-realm keytabs. Tests should cover deleted entries, kvno8 versus kvno32, enctype preference, exact enctype lookup, realm ignored/enforced lookup, and option mutation for AES/RC4.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/keytab.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/kpasswd.py -->
# sources/user-network-fs/impacket/impacket/krb5/kpasswd.py

Purpose: implements Microsoft/Windows Kerberos change-password and set-password protocol behavior over kpasswd TCP/464 using RFC 3244-style AP_REQ plus KRB_PRIV messages.

Important APIs/types: constants define port, protocol version, and `kadmin/changepw` SPN. `KPasswdResultCodes`, `RESULT_MESSAGES`, `PasswordPolicyFlags`, and `_decodePasswordPolicy()` interpret server results. `ChangePasswdData` is the ASN.1 payload. `createKPasswdRequest()` builds authenticator, AP_REQ, encrypted change data, KRB_PRIV, and packet header. `decodeKPasswdReply()` parses AP_REP/KRB_PRIV and returns success/result/message. `changePassword()` delegates to `setPassword()`, which acquires a changepw TGT, builds the request, sends it, and raises `KPasswdError` on failure.

Control flow and persistence: `setPassword()` optionally loads a changepw TGT from `KRB5CCNAME`, otherwise calls `getKerberosTGT()` with serverName `kadmin/changepw`. It decodes the ticket, generates a subkey if not supplied, sends the kpasswd request via `sendReceive()`, and decodes the response. There is no file write; only optional cache read.

Dependencies and integration: uses Kerberos ASN.1 helpers, `CCache`, `crypto.Key`, random bytes, `types.Principal/Ticket/KerberosTime`, and `kerberosv5.sendReceive/getKerberosTGT`. It is a credential-changing integration point for Impacket tools.

Risks and test signals: the cleartext new password is embedded before encryption, so debug logs around base64 payloads are sensitive. `decodeKPasswdReply()` ignores AP_REP cryptographic validation and focuses on KRB_PRIV decryption. Password policy parsing expects an AD-specific binary layout. Tests should cover request construction with deterministic `now`/sequence/subkey, target-user set-password fields, cache TGT selection, result-code mapping, policy decoding, malformed reply handling, and failed decrypt handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/kpasswd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/pac.py -->
# sources/user-network-fs/impacket/impacket/krb5/pac.py

Purpose: models Microsoft PAC buffers and provides PAC construction/signing helpers for MS-PAC structures embedded in Kerberos authorization data.

Important APIs/types: constants identify PAC buffer types. NDR structures cover validation info, SID/group membership, credentials, supplemental NTLM credentials, delegation info, UPN/DNS info, claims/device info, attributes, and requestor SID. `PACTYPE`, `PAC_INFO_BUFFER`, `PAC_CREDENTIAL_INFO`, `PAC_CLIENT_INFO`, `PAC_SIGNATURE_DATA`, and related `Structure` classes model binary PAC buffers. Helper functions include `get_pad_length()`, `get_block_length()`, `_coerce_hex_key()`, `_ordered_buffer_types()`, `build_pac_type()`, `_normalize_pac_checksum_type()`, `_get_checksum_context()`, and `sign_pac()`.

Control flow and state: `build_pac_type()` orders buffers, computes the PAC header/table offset, pads each blob to 8-byte boundaries, and returns a `PACTYPE`. `sign_pac()` requires server and privsvr checksum buffers, coerces AES/NT hash material, normalizes checksum types if requested, zeroes signatures, builds the checksum blob, computes server checksum over the whole PAC, computes privsvr checksum over the server checksum, updates both buffers, and rebuilds the PAC. The input `pac_infos` dictionary is mutated.

Dependencies and integration: depends heavily on Impacket DCE/RPC NDR types, Kerberos constants/crypto checksum tables, LDAP SID helpers, and `Structure`. Ticket-forging and PAC-inspection code uses these types to build and sign PAC authorization data.

Risks and test signals: `sign_pac()` mutates caller-provided PAC dictionaries, which can surprise callers reusing buffer data. Checksum inference from signature length only works for AES keys of expected size. Unsupported checksum types raise generic exceptions. Tests should verify 8-byte alignment, buffer ordering, deterministic PAC bytes, AES128/AES256/RC4 signatures, missing key errors, inferred checksum types, and mutation side effects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/pac.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/types.py -->
# sources/user-network-fs/impacket/impacket/krb5/types.py

Purpose: supplies Python-friendly Kerberos wrapper types and conversions around ASN.1 structures: principals, addresses, encrypted data, tickets, and Kerberos time.

Important APIs/types: `_asn1_decode()` decodes pyasn1 data and rejects trailing substrate. `Principal` parses strings with escapes and realms, tuples/lists, or copies existing principals; it can convert from ASN.1 and write name components to ASN.1. `Address` is a partial address wrapper. `EncryptedData` converts ASN.1 encrypted data to Python fields and back. `Ticket` converts ASN.1 tickets to service principal/encrypted-part fields and back. `KerberosTime` formats/parses UTC generalized time.

Control flow and state: objects hold in-memory fields only. Principal parsing handles quoted `/`, `@`, and backslash characters, defaults realm when absent, and treats unknown name types as wildcard-compatible in equality. Ticket and encrypted-data wrappers delegate schema details to `asn1.py`.

Dependencies and integration: uses stdlib `datetime`, `socket`, `re`, `struct`, pyasn1 DER decoder, `six.ensure_binary`, and local `asn1/constants`. These wrappers are used across `kerberosv5.py`, `ccache.py`, and `kpasswd.py`.

Risks and test signals: `Address.family` and `Address.address` check IPv4 in both branches, so IPv6 appears unreachable. `Address.encode()` is unimplemented. `Principal.__eq__()` uses `all(map(...))`, which can ignore length mismatches after matching prefix. `EncryptedData.from_asn1()` uses `str()` for ciphertext, which may be risky for bytes-like octets. Tests should cover escaped principal parsing, tuple forms, wildcard type equality, unequal component lengths, ASN.1 ticket round-trips, strict trailing DER rejection, KerberosTime non-Z rejection, and IPv6 address behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/krb5/types.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ldap/__init__.py -->
# sources/user-network-fs/impacket/impacket/ldap/__init__.py

Purpose: marks `impacket.ldap` as a package and contains only licensing comments, an empty description marker, and `pass`. It does not re-export LDAP classes or perform runtime setup.

Important APIs/types/functions: none. Consumers import concrete modules such as `impacket.ldap.ldap`, `ldapasn1`, and `ldaptypes`.

Control flow and state: no runtime logic, state, persistence, or I/O.

Dependencies and integration: package identity enables relative/import-package access for LDAP modules.

Risks and test signals: low risk. Tests only need to ensure package import succeeds and downstream explicit module imports remain available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ldap/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ldap/ldap.py -->
# sources/user-network-fs/impacket/impacket/ldap/ldap.py

Purpose: implements a minimal RFC 4511 LDAP client with Active Directory-oriented authentication and operations. It supports plain LDAP, LDAPS, and Global Catalog URLs; simple, Sicily NTLM, SASL NTLM/SPNEGO, and Kerberos binds; signed/sealed LDAP frames; searches with filters and paging controls; and add/modify/rename/delete operations.

Important APIs/types: `LDAPConnection` is the core class. Constructor parses URL schemes, connects sockets, sets LDAPS TLS context, and computes channel binding data. Authentication APIs are `kerberosLogin()` and `login()`. Transport APIs include `encrypt()`, `decrypt()`, `send()`, `recv_raw()`, `recv()`, and `sendReceive()`. Directory APIs include `search()`, `_handleControls()`, `add()`, `modify()`, `modify_dn()`, `delete()`, and `close()`. Filter parsing uses `_parseFilter()`, `_consumeCompositeFilter()`, `_consumeSimpleFilter()`, `_compileCompositeFilter()`, `_compileSimpleFilter()`, and `_processLdapString()`. Exceptions are `LDAPFilterSyntaxError`, `LDAPFilterInvalidException`, `LDAPSessionError`, and `LDAPSearchError`.

Control flow and state: the connection stores socket, base DN, destination, bind state, auth type, signing flag, sequence number, Kerberos GSS context/session key, NTLM SPNEGO cipher, and optional TLS channel-binding hash. Binds mutate `__binded` and auth state. Signed sends wrap BER LDAP messages with Kerberos or NTLM sealing and increment `sequenceNumber`; receives collect TCP frames, decrypt complete sealed frames, decode one or more LDAP messages, and raise on unsolicited disconnect notifications. Search loops until `SearchResultDone` and paged controls indicate completion.

Dependencies and integration: depends on pyasn1 BER codecs, OpenSSL, Impacket LDAP ASN.1 schemas, NTLM, SPNEGO, Kerberos modules, sockets, and logging. It is the LDAP transport used by AD enumeration, modification, and relay-style tooling.

Risks and test signals: LDAPS explicitly allows all ciphers at security level 0 and unsafe legacy renegotiation for compatibility. `raise(f"...")` in encryption/decryption error paths raises a string expression rather than an exception object. `recv_raw()` uses short reads to infer message completion, which can be fragile without signing. Filter parsing is custom and should be tested against RFC 4515 escaping and invalid nesting. Tests should cover URL parsing, LDAPS channel binding, SASL NTLM MIC/mechListMIC, Kerberos signing flags, sealed send/recv framing, paged search cookies, partial search errors preserving answers, CRUD error mapping, unsolicited notifications, and filter compile cases for equality, substring, present, approximate, ordering, extensible, and composite filters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ldap/ldap.py -->
