<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/v5gen.c -->
# sources/distributed-fs/openafs/src/rxkad/v5gen.c

## Purpose

`v5gen.c` is generated Heimdal ASN.1 DER support code for a Kerberos v5 schema snapshot (`Generated from ./krb5.asn1`). In this OpenAFS tree it is not compiled as a normal standalone translation unit; `src/rxkad/ticket5.c` includes `v5gen.h`, includes `v5gen-rewrite.h` to rename the generated symbols into an rxkad-private namespace, and then includes this C file directly. The concrete consumer visible in this tree is Kerberos 5 ticket handling in rxkad, especially `ticket5.c` calling `decode_EncTicketPart` after decrypting a ticket.

The local implementation covers the subset needed for ticket parsing and related Kerberos structures: primitive integer/string/time helpers, principal and address structures, authorization data sequences, Kerberos option/flag bit strings, encrypted data, encryption keys, tickets, and encrypted ticket parts. The top of the file forward-declares additional generated functions for types defined in `v5gen.h` but implemented elsewhere or unused by this included subset.

## Important APIs, Types, and Functions

The file follows a repetitive generated API pattern for each ASN.1 type:

- `encode_<Type>(unsigned char *p, size_t len, const <Type> *data, size_t *size)` writes DER backwards into a caller-provided buffer ending at `p`.
- `decode_<Type>(const unsigned char *p, size_t len, <Type> *data, size_t *size)` parses DER from `p`, zero-initializes `data`, and reports bytes consumed through `size`.
- `length_<Type>(const <Type> *data)` computes encoded DER length.
- `copy_<Type>(const <Type> *from, <Type> *to)` deep-copies owned subfields where needed.
- `free_<Type>(<Type> *data)` frees owned strings, octet strings, arrays, and optional pointers.

Implemented primitive-like helpers include `NAME_TYPE`, `MESSAGE_TYPE`, `PADATA_TYPE`, `AUTHDATA_TYPE`, `CKSUMTYPE`, `ENCTYPE`, `krb5uint32`, `krb5int32`, `KerberosString`, `Realm`, and `KerberosTime`. Integer-like values use DER integer helpers; Kerberos strings and realms are `GeneralString`; times are `GeneralizedTime`.

Implemented compound data includes `PrincipalName`, `Principal`, `Principals`, `HostAddress`, `HostAddresses`, `AuthorizationDataElement`, `AuthorizationData`, `LastReq`, `EncryptedData`, `EncryptionKey`, `TransitedEncoding`, `Ticket`, and `EncTicketPart`. Sequence-of types (`Principals`, `HostAddresses`, `AuthorizationData`, `LastReq`) dynamically grow `val` arrays while decoding and provide add/remove helpers for some lists, such as `add_Principals`, `remove_Principals`, `add_AuthorizationData`, and `remove_AuthorizationData`.

Flag helpers are important because they bridge Kerberos ASN.1 bit-string ordering and C integer masks:

- `APOptions2int` / `int2APOptions`
- `TicketFlags2int` / `int2TicketFlags`
- `KDCOptions2int` / `int2KDCOptions`

`encode_Ticket` / `decode_Ticket` wrap a sequence in application tag 1. `encode_EncTicketPart` / `decode_EncTicketPart` wrap a sequence in application tag 3 and cover the ticket body fields used after decryption: flags, session key, client realm/name, transited encoding, authentication/end times, optional start/renew times, optional client addresses, and optional authorization data.

## Control Flow and Data Handling

Generated encoders assemble DER from the innermost fields outward. They encode fields in reverse ASN.1 order because `der_put_*` writes backwards from the tail of the buffer, decrementing `p` and `len` while incrementing `ret`. For explicit/context fields they encode the payload, then call `der_put_length_and_tag` with `ASN1_C_CONTEXT` and the field number; application wrappers use `ASN1_C_APPL`.

Generated decoders follow a strict nested pattern:

1. `memset(data, 0, sizeof(*data))`.
2. Match the expected universal/application/context tag and constructed/primitive type with `der_match_tag_and_length`.
3. Check for length overruns before entering nested content.
4. Decode required fields in ASN.1 order.
5. Treat missing optional fields by setting their pointer to `NULL`.
6. On any parse/allocation error, jump to `fail`, call the matching `free_<Type>`, and return the DER/ASN.1 or `ENOMEM` error.

Sequence-of decoders loop until the nested sequence payload is consumed. They grow arrays with `realloc`, guard integer wraparound while calculating the next allocation size, decode into the next element, and increment `len` only after successful element decoding. Add/remove helpers use the same ownership contract: copied-in elements become owned by the array, removed elements are freed and remaining entries are compacted with `memmove`.

Bit-string decoders skip the initial "unused bits" octet, then decode available bytes defensively, breaking if the encoding is shorter than the full generated width. Encoders use a fixed 5-byte DER bit-string payload for AP options, ticket flags, and KDC options: one unused-bits octet plus four bytes of flag content.

## State and Persistence Behavior

There is no persistent state, global mutable state, I/O, locking, or threading. State exists only in caller-supplied structures and heap allocations owned by decoded/copied structures. The important persistence-like behavior is memory ownership: callers that successfully decode or copy compound values must call the corresponding `free_<Type>` to release nested strings, octet strings, arrays, and optional pointers. On failure, decoders and copy routines clean up partial output before returning.

## Dependencies and Integration Points

`v5gen.c` depends on the Heimdal/OpenAFS DER support layer: `der_put_integer`, `der_get_integer`, `der_put_unsigned`, `der_get_unsigned`, `der_put_general_string`, `der_get_general_string`, `der_put_generalized_time`, `der_get_generalized_time`, `der_put_octet_string`, `der_get_octet_string`, `der_match_tag_and_length`, `der_put_length_and_tag`, `der_length_*`, `der_copy_*`, and `der_free_*`. It also depends on ASN.1 error constants such as `ASN1_BAD_ID`, `ASN1_OVERRUN`, `ASN1_OVERFLOW`, and `ENOMEM`.

The file includes standard C headers and `asn1_err.h`, but the real OpenAFS integration is through `ticket5.c`, which includes `v5gen.c` directly. The rxkad build rule for `ticket5.lo` depends on `ticket5.c`, `v5gen.c`, `v5der.c`, and `v5gen-rewrite.h`; the rewrite header maps generated function names such as `decode_EncTicketPart` to rxkad-specific private names to avoid symbol conflicts with external Kerberos libraries.

## Risks and Edge Cases

Because this is generated protocol code in the authentication path, the main risks are parser correctness and memory safety. DER length and tag checks are pervasive, but any mismatch between `v5gen.h`, `v5gen.c`, `v5der.c`, or `v5gen-rewrite.h` can cause compile-time or link-time failures, or worse, ABI mismatches if declarations and generated bodies diverge.

The code accepts enum integer values directly from DER without validating that they are one of the named constants. That matches common Kerberos extensibility behavior but means callers must not assume enum values are always known.

Optional-field parsing treats a failed tag match as "field absent." This is standard for generated decoders, but malformed encodings with an unexpected tag at an optional position can cause later required field checks to fail only after the optional is skipped. Tests need to cover both absent optionals and bad tags near optional fields.

Heap allocation paths are broad: strings, octet strings, sequence arrays, and optional fields allocate during decode and copy. Partial failures rely on exact `free_<Type>` behavior. Fuzzing or negative DER tests are valuable because the code is mostly mechanical and security-sensitive.

The fixed-width bit-string encoders always emit four content bytes after the unused-bits octet, even for flag sets with few active bits. Consumers expecting minimal DER bit-string encodings should be tested, although OpenAFS likely relies on Heimdal-compatible DER behavior here.

## Test Signals

Useful tests are round-trip DER tests for `Ticket`, `EncTicketPart`, `EncryptedData`, `EncryptionKey`, `PrincipalName`, `HostAddresses`, and `AuthorizationData`; negative tests for truncated DER and wrong primitive/constructed tags; allocation-failure or sanitizer runs around sequence-of growth and optional fields; and integration tests exercising `ticket5.c` parsing of valid and invalid Kerberos 5 tickets. Build tests should ensure `ticket5.lo` still compiles with `v5gen-rewrite.h` and does not export unrenamed generated symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/v5gen.c -->
