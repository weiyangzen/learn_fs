<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/v5gen.h -->
# sources/distributed-fs/openafs/src/rxkad/v5gen.h

## Purpose

`v5gen.h` is the generated public type and function declaration header for the Kerberos v5 ASN.1 schema snapshot used by rxkad ticket handling. It is marked `Generated from ./krb5.asn1` and `Do not edit`. The header defines Heimdal-compatible base ASN.1 data types, Kerberos-specific enum constants and structures, calling-convention/export macros, and declarations for generated encode/decode/length/copy/free helpers.

In this OpenAFS source tree, `ticket5.c` includes this header before including `v5gen-rewrite.h` and `v5gen.c`. The header therefore provides the C data model used by the included generated implementation and by surrounding rxkad code that manipulates decoded tickets.

## Important APIs, Types, and Functions

The header first defines reusable Heimdal ASN.1 representations:

- `heim_base_data` / `heim_octet_string` for byte buffers.
- `heim_integer`, `heim_oid`, `heim_bit_string`.
- string aliases such as `heim_general_string`, `heim_utf8_string`, `heim_printable_string`, `heim_ia5_string`, `heim_visible_string`.
- wide-string structures `heim_bmp_string` and `heim_universal_string`.
- `ASN1_MALLOC_ENCODE(T, B, BL, S, L, R)`, a convenience macro that sizes, allocates, and encodes a DER buffer.
- `ASN1EXP` and `ASN1CALL`, which abstract Windows import/calling convention details.

Core Kerberos enum domains include `NAME_TYPE`, `MESSAGE_TYPE`, `PADATA_TYPE`, `AUTHDATA_TYPE`, `CKSUMTYPE`, `ENCTYPE`, `LR_TYPE`, and `PA_SAM_TYPE`. Constants cover standard Kerberos values plus Microsoft, PKINIT, FAST, PAC, OTP, NTLM, and OpenAFS-relevant values such as `KRB5_PADATA_AFS3_SALT`.

The header declares the canonical generated helper family for most types: `decode_<Type>`, `encode_<Type>`, `length_<Type>`, `copy_<Type>`, and `free_<Type>`. Some sequence types also declare list mutators, for example `add_Principals`, `remove_Principals`, `add_AuthorizationData`, `remove_AuthorizationData`, `add_ETYPE_INFO`, `remove_ETYPE_INFO`, `add_ETYPE_INFO2`, `remove_ETYPE_INFO2`, `add_METHOD_DATA`, and `remove_METHOD_DATA`.

Major Kerberos protocol structures include:

- Identity and addressing: `PrincipalName`, `Principal`, `Principals`, `HostAddress`, `HostAddresses`.
- Time and authorization: `KerberosTime`, `AuthorizationDataElement`, `AuthorizationData`, `LastReq`.
- Ticket crypto containers: `EncryptedData`, `EncryptionKey`, `TransitedEncoding`, `Ticket`, `EncTicketPart`, `Checksum`, `Authenticator`.
- Preauthentication and KDC request/response data: `PA_DATA`, `ETYPE_INFO_ENTRY`, `ETYPE_INFO`, `ETYPE_INFO2_ENTRY`, `ETYPE_INFO2`, `METHOD_DATA`, `TypedData`, `TYPED_DATA`, `KDC_REQ_BODY`, `KDC_REQ`, `AS_REQ`, `TGS_REQ`, `KDC_REP`, `AS_REP`, `TGS_REP`, and encrypted KDC reply parts.
- Application exchanges: `AP_REQ`, `AP_REP`, `EncAPRepPart`, `KRB_SAFE`, `KRB_PRIV`, `KRB_CRED`, `KRB_ERROR`, and related encrypted parts.
- Extension and compatibility structures: change-password data, authorization-data wrappers, SAM challenge/response, S4U2Self, signed paths, referral data, FAST request/reply/cookie/state types, KDC proxy message, and internal KERB credential/TGS helper structures.

Flag bit-field structs include `APOptions`, `TicketFlags`, `KDCOptions`, `SAMFlags`, `FastOptions`, and `KDCFastFlags`, with declared conversion helpers such as `TicketFlags2int` and `int2TicketFlags`.

## Control Flow and Data Model

The header has no executable control flow beyond the `ASN1_MALLOC_ENCODE` macro. Its primary behavior is declarative: it maps ASN.1 schema constructs into C structures. Required ASN.1 fields become direct struct fields; optional fields become pointers; `SEQUENCE OF` fields become `{ unsigned int len; <T> *val; }` arrays; `CHOICE` types become an enum discriminator plus a union.

Generated structures mirror ASN.1 tagging comments embedded directly above each type. These comments are significant maintenance signals: the implementation in `v5gen.c` and any external generated object must match these tags exactly. Aliases such as `AS_REQ`/`TGS_REQ` to `KDC_REQ`, `AS_REP`/`TGS_REP` to `KDC_REP`, and `AD_IF_RELEVANT` to `AuthorizationData` reduce duplicate C layout for ASN.1 type aliases.

## State and Persistence Behavior

There is no runtime state or persistence. The header defines ownership contracts indirectly: pointer fields represent optional heap-owned decoded/copied values, string and octet-string fields can own heap buffers, and sequence `val` arrays own their elements. Callers are expected to pair successful decodes/copies with the corresponding generated `free_<Type>` routine.

## Dependencies and Integration Points

This header depends on `<stddef.h>`, `<time.h>`, and OpenAFS integer types such as `afs_uint16` and `afs_uint32` for Heimdal string representations. It is part of the rxkad Kerberos 5 ticket path and is listed in `src/rxkad/Makefile.in` as an rxkad include dependency. `ticket5.c` includes it directly, and `v5gen-rewrite.h` rewrites many declared function names during the include of `v5gen.c`.

Because the header declares many more functions than the subset visibly implemented in `v5gen.c`, consumers must be careful about which generated functions they actually call in a given build configuration. The direct-include plus symbol-rewrite pattern means declarations, rewritten names, and implementation bodies must remain synchronized.

## Risks and Edge Cases

This is generated security-protocol ABI. Any manual edit can break DER compatibility, memory ownership expectations, or symbol naming. The most important risk is drift between the ASN.1 schema comments/types here and the generated implementation. Structure layout changes also affect all rxkad code compiled with this header.

Optional fields are raw pointers, so uninitialized or stack-copied structures are dangerous unless zeroed and freed via generated helpers. Sequence lengths use `unsigned int`; code that converts external sizes to these fields must guard truncation. Enums include negative and duplicate values; callers should not assume enum values are contiguous or unique.

The header's include guard name `__krb5_asn1_h__` is broad and may collide with other generated Kerberos ASN.1 headers if included in the same translation unit. OpenAFS mitigates generated symbol conflicts with `v5gen-rewrite.h`, but type-name conflicts are still a concern if external Kerberos headers expose the same names.

## Test Signals

Header-level validation should include compiling `ticket5.c` in the rxkad build, verifying generated symbol rewriting works, and running type-level round-trip tests using the declared APIs for ticket and encrypted ticket structures. Static analysis should focus on ownership of optional pointer fields, sequence lengths, and direct struct copies that bypass generated copy/free helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/v5gen.h -->
