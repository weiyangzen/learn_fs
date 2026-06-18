# Research: subset-b-007801

Grouped research for the exact source files assigned to `subset-b-007801`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxosd/Makefile.in -->
# sources/distributed-fs/openafs/src/rxosd/Makefile.in

## Purpose

This makefile drives the rxosd build, including generated Rx RPC sources, the `rxosd` server binary, the `osd` command/client utility, the `readabyte` helper, and the static `librxosd.a` client/XDR library installed into the top-level library directory. It is a configure-template makefile that includes OpenAFS build configuration and pthread settings.

## Important Targets and Variables

Important directory variables point to sibling OpenAFS components: `VICED`, `VLSERVER`, `LWP`, `LIBACL`, `UTIL`, `DIR`, `VOL`, `OSDDBSRC`, and `FSINT`. `HSM_LIB` and `HSM_INC` are configure substitutions for external HSM integration, and `PNFS_OPT` is used in several rxosd-related compile flags.

Object groups define build composition:

- `RXOSDOBJS`: rxosd service/client generated files plus rxosd HSM and dcache objects.
- `LWPOBJS`, `UTILOBJS`, `VOLOBJS`, and `OSDDBOBJS`: local copies of common OpenAFS objects needed by this server.
- `LIBS`: authentication, RPC, util, and command libraries from `${TOP_LIBDIR}`.

Generated interface targets use `RXGEN` on `rxosd.xg` and `../osddb/osddb.xg`:

- `rxosd.h`, `rxosd.ss.c`, `rxosd.cs.c`, `rxosd.xdr.c`
- kernel-style variants `Krxosd.cs.c`, `Krxosd.xdr.c`
- `osddb.h`, `osddb.cs.c`, `osddb.xdr.c`

Build products include `osd`, `rxosd`, `readabyte`, `librxosd.a`, and `${TOP_INCDIR}/afs/rxosd.h`.

## Control Flow

The default `all` target generates rxosd client/XDR files and the exported header, then builds and installs `librxosd.a` into `${TOP_LIBDIR}`. The `rxosd` target links the service binary from generated rxosd objects plus common LWP/util/vol/osddb objects and HSM libraries. The `osd` target links the command utility against rxosd client stubs, osddb user code, policy parser output, and shared OpenAFS libs. `readabyte` links a small helper against HSM/dcache-related objects.

Compilation rules pull source from sibling directories using `${AFS_CCRULE}`. The `policies.tab.c` rule invokes `${YACC}` on `policies.y`; `policy_parser.o` depends on that generated parser but appears to compile `policy.tab.c`, which is suspicious because the generator target name is `policies.tab.c`.

`install` installs server executables under `${afssrvlibexecdir}`, the `osd` command under `${bindir}`, and the exported rxosd header/library through other targets. `dest` installs into legacy `${DEST}` packaging paths. `clean` removes generated rxosd/osddb files, object files, policy parser output, and component version files.

## State and Persistence Behavior

The makefile persists generated C/header files, object files, static libraries, executables, and installed headers/binaries. It does not manage runtime rxosd state. Build output location is split between the local directory, `${TOP_INCDIR}`, `${TOP_LIBDIR}`, `${DESTDIR}`, and `${DEST}`.

## Dependencies and Integration Points

This file integrates rxosd with Rx RPC generation (`RXGEN`), OpenAFS auth/RPC/cmd/util libraries, volume-server support code, osddb generated stubs, yacc-generated policy parsing, HSM libraries, and pthread settings. It also reuses low-level volume/namei code with `-DBUILDING_RXOSD` and HSM/pNFS compile flags.

## Risks and Edge Cases

There is a likely typo in the `install` target: `${DESTDIR}}${afssrvlibexecdir}/rxosd` contains an extra `}` and can install `rxosd` to a malformed path. The `policy_parser.o` rule depends on `policies.tab.c` but compiles `policy.tab.c`, while `clean` removes `policy_parser.c`; these names should be validated against the actual yacc output and parser source naming. Duplicate `dest` target definitions appear: an early `dest: all` and a later install-style `dest:` rule. In make, multiple rules can merge prerequisites/recipes depending on syntax, but duplicate target recipes are risky and may warn or override behavior.

Because the makefile compiles many objects from sibling directories with rxosd-specific flags, stale objects or flag mismatches can produce subtle ABI differences. Generated RPC files must be regenerated when `.xg` interfaces change, and clean rules must remove all generated names consistently.

## Test Signals

Run `make generated`, `make all`, and target-specific builds for `rxosd`, `osd`, `readabyte`, and `librxosd.a`. Validate install paths with `make -n install DESTDIR=/tmp/stage`. Check yacc parser generation names with a dry run. Packaging tests should verify `${TOP_INCDIR}/afs/rxosd.h`, `${TOP_LIBDIR}/librxosd.a`, server binaries, and user command placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxosd/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxstat/Makefile.in -->
# sources/distributed-fs/openafs/src/rxstat/Makefile.in

## Purpose

This makefile builds the Rx statistics RPC support library. It generates client, server, and XDR stubs from `rxstat.xg`, compiles the handwritten `rxstat.c` service wrapper, and produces static, PIC, and libtool shared-library forms for consumers that expose or call RX RPC statistics services.

## Important Targets and Variables

`LT_objs` lists the libtool objects: `rxstat.cs.lo`, `rxstat.ss.lo`, `rxstat.xdr.lo`, and `rxstat.lo`. `LT_deps` points to `src/rx/liboafs_rx.la`, and the makefile includes OpenAFS config plus LWP/LWP-tool build rules.

The default `all` target runs `depinstall`, builds `liboafs_rxstat.la`, builds `librxstat_pic.la`, and installs `${TOP_LIBDIR}/librxstat.a`. The `generated` target creates both normal and kernel-style generated stubs:

- normal: `rxstat.cs.c`, `rxstat.ss.c`, `rxstat.xdr.c`, `rxstat.h`
- kernel-style: `Krxstat.cs.c`, `Krxstat.ss.c`, `Krxstat.xdr.c`

`depinstall` installs `${TOP_INCDIR}/rx/rxstat.h` and ensures kernel-style generated sources exist. `install` and `dest` place `rxstat.h` and `librxstat.a` into staged include/lib directories.

## Control Flow

`RXGEN` creates generated sources from `rxstat.xg`. The normal rules use `-A -x` for RXGEN output and choose client (`-C`), server (`-S`), XDR (`-c`), or header (`-h`) generation. Kernel variants use `-x -k`. The generated `.c` files depend on `rxstat.h`, ensuring the header is created first when building stubs.

`librxstat.a` is linked from libtool objects using `$(LT_LDLIB_lwp)`. Shared and PIC libraries use the OpenAFS libtool helper macros and, for `liboafs_rxstat.la`, an explicit symbol file and the Rx library dependency.

## State and Persistence Behavior

Build state consists of generated `rxstat.*` and `Krxstat.*` files, libtool object files, static/PIC/shared libraries, and installed header/library outputs. The makefile has no runtime state. `clean` invokes `$(LT_CLEAN)` and removes generated RPC files, object archives, core files, and component version output.

## Dependencies and Integration Points

The makefile ties together `rxstat.xg`, generated Rx RPC stubs, the handwritten `rxstat.c` RPC manager implementation, the core Rx library, LWP build machinery, and top-level include/library install locations. Consumers depend on `${TOP_INCDIR}/rx/rxstat.h` and `${TOP_LIBDIR}/librxstat.a` or the libtool libraries.

## Risks and Edge Cases

Generated files must stay synchronized with `rxstat.xg`; stale generated headers can cause mismatched RPC signatures. The kernel-style generated files are created in `depinstall` but are not part of `LT_objs`, so build scripts that need kernel stubs must depend on `generated` or `depinstall` explicitly. Symbol export coverage depends on `liboafs_rxstat.la.sym`; missing symbols there would affect shared-library consumers even if static builds pass.

## Test Signals

Run `make generated`, `make all`, `make install DESTDIR=/tmp/stage`, and `make clean`. Confirm that `rxstat.h` installs under both top include and staged include paths, and that static/PIC/shared library variants contain the generated client/server/XDR objects plus `rxstat.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxstat/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxstat/rxstat.c -->
# sources/distributed-fs/openafs/src/rxstat/rxstat.c

## Purpose

`rxstat.c` implements the server-side RPC manager functions for retrieving, querying, enabling, disabling, clearing, and versioning Rx RPC statistics. It centralizes generic RX stats service behavior so multiple OpenAFS servers can expose the same RPC interface generated from `rxstat.xg`.

## Important APIs and Functions

The exported manager functions use the generated `MRXSTATS_` naming convention:

- `MRXSTATS_RetrieveProcessRPCStats`
- `MRXSTATS_RetrievePeerRPCStats`
- `MRXSTATS_QueryProcessRPCStats`
- `MRXSTATS_QueryPeerRPCStats`
- `MRXSTATS_EnableProcessRPCStats`
- `MRXSTATS_EnablePeerRPCStats`
- `MRXSTATS_DisableProcessRPCStats`
- `MRXSTATS_DisablePeerRPCStats`
- `MRXSTATS_QueryRPCStatsVersion`
- `MRXSTATS_ClearProcessRPCStats`
- `MRXSTATS_ClearPeerRPCStats`

Retrieve functions call `rx_RetrieveProcessRPCStats` or `rx_RetrievePeerRPCStats`, passing the client protocol version, output version and clock fields, and a returned allocation size. They store the returned stats pointer in `stats->rpcStats_val` and translate byte allocation size to `stats->rpcStats_len` by dividing by `sizeof(afs_uint32)`.

Query functions return the current enablement state from `rx_queryProcessRPCStats` and `rx_queryPeerRPCStats`. Enable/disable/clear functions authorize through `rx_RxStatUserOk(call)` before mutating RX stats collection state. `MRXSTATS_QueryRPCStatsVersion` returns `RX_STATS_RETRIEVAL_VERSION`.

## Control Flow

The file has direct wrapper control flow with little local logic. Mutating functions initialize `rc` to 0, check authorization, set `EPERM` on failure, and call the corresponding RX stats mutator on success. Retrieval functions delegate allocation and data population to the RX layer, then update the generated RPC array length regardless of the return code.

## State and Persistence Behavior

This file owns no persistent state. The actual process and peer RPC stats state lives in the RX subsystem. Calls here can toggle collection state and clear counters through RX APIs, so their effects are process-global within the hosting server. Retrieved `rpcStats_val` memory ownership is handed to the generated RPC/XDR layer through the `rpcStats` output structure.

## Dependencies and Integration Points

The file includes OpenAFS config/parameter headers, `roken.h` for non-kernel builds, `afs/stds.h`, `rx/rx.h`, and the generated `rx/rxstat.h`. In kernel non-UKERNEL builds it includes `sys/errno.h`. It depends directly on RX stats APIs and on generated RPC types such as `rpcStats`, `IN`, and `OUT`.

The manager function names match generated server stubs from `rxstat.xg`; those stubs dispatch incoming Rx RPC calls to these functions. Authorization is delegated to `rx_RxStatUserOk`, so security policy is centralized in the RX layer rather than in this file.

## Risks and Edge Cases

The retrieve functions set `stats->rpcStats_len` from `allocSize` even if the underlying retrieve call returns an error. If the RX API does not initialize `allocSize` and `stats->rpcStats_val` on failure, this could expose stale stack data or an invalid length; validation should confirm the RX retrieval contract. The cast to `u_int` can truncate very large allocation sizes, though stats arrays should be bounded by protocol design.

Mutating functions rely entirely on `rx_RxStatUserOk(call)` for access control. Any server exposing this interface must ensure that function correctly identifies privileged callers in its security class and deployment context. Clear operations accept `clearFlag` without local validation, so accepted semantics are defined by the RX subsystem.

## Test Signals

Unit tests or RPC integration tests should cover authorized and unauthorized enable/disable/clear calls, process and peer stats query toggles, retrieval length/value consistency, version query returning `RX_STATS_RETRIEVAL_VERSION`, and retrieval failure behavior. Tests should verify generated stubs marshal `rpcStats_len` as a count of `afs_uint32`, not bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxstat/rxstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/scout/Makefile.in -->
# sources/distributed-fs/openafs/src/scout/Makefile.in

## Purpose

This makefile builds and installs the `scout` monitoring command. `scout` is linked as a static OpenAFS tool using fsprobe, gtx UI, rxkad authentication, fsint, cmd, util, opr, LWP compatibility, and volser libraries, plus roken, curses, and optional X11 libraries.

## Important Targets and Variables

`INCLS` lists installed headers required by `scout.o`, mostly GTX UI headers plus keys, cell config, and command parsing headers. `LIBS` lists libtool library dependencies from other OpenAFS source directories:

- `liboafs_fsprobe.la`
- `liboafs_gtx.la`
- `liboafs_rxkad.la`
- `liboafs_fsint.la`
- `liboafs_cmd.la`
- `liboafs_util.la`
- `liboafs_opr.la`
- `liboafs_lwpcompat.la`
- `liboafs_volser.la`

The default `all` target builds `scout`. `scout.o` depends on `scout.c`, the installed headers, and `AFS_component_version_number.c`. `scout` links with `$(LT_LDRULE_static)`.

## Control Flow

Build flow is simple: compile `scout.o`, then statically link it with the library list, roken, curses, and X libraries. The `install` target creates `${DESTDIR}${bindir}` and installs the program there. The `dest` target installs into legacy `${DEST}/bin`. `clean` removes the object, executable, core file, and generated component version source.

## State and Persistence Behavior

The makefile persists only build artifacts and installed binaries. It has no runtime state. Runtime monitoring behavior belongs to `scout.c` and its linked libraries, not this makefile.

## Dependencies and Integration Points

`scout` integrates filesystem probing (`fsprobe`), text/window UI via `gtx` and curses/X11, rxkad security, file-server interface stubs, command parsing, utility/opr helpers, LWP compatibility, and volume-server support. The include dependencies require top-level header installation to have happened before this tool is built.

## Risks and Edge Cases

The `INCLS` list contains `gtxobjects.h` twice, which is harmless but indicates manual maintenance drift. Because `scout` links statically against many internal libraries, dependency ordering can matter; link failures may surface when any library changes its transitive dependencies. Curses and X11 availability are platform-sensitive, so configure substitutions must provide the right `LIB_curses` and `XLIBS`.

## Test Signals

Run `make scout`, `make install DESTDIR=/tmp/stage`, and `make clean`. Link tests should cover builds with and without X11 support as configured. Packaging should verify the final binary lands in `${bindir}` or `${DEST}/bin` as appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/scout/Makefile.in -->
