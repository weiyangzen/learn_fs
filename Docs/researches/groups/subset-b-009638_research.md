# subset-b-009638 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/spnego.py -->
# sources/user-network-fs/impacket/impacket/spnego.py

## Purpose

`spnego.py` implements the SPNEGO/GSSAPI token helpers used by Impacket's SMB, SMB2/3, and DCERPC authentication paths. It provides manual ASN.1 BER length encoding/decoding, token wrappers for SPNEGO `NegTokenInit` and `NegTokenResp`, OID mappings for common negotiated mechanisms, and an NTLM-backed signing/sealing helper for SPNEGO-protected payloads.

The file is intentionally low-level: callers work with raw bytes, ASN.1 tag constants, and field dictionaries rather than a full ASN.1 schema library. Its main role is to serialize and parse the subset of SPNEGO needed to carry NTLM/Kerberos negotiation tokens and to apply NTLM session security after negotiation.

## Important APIs, Types, And Functions

`GSS_API_SPNEGO_UUID`, ASN.1 tag constants, `MechTypes`, and `TypesMech` define the object identifiers and labels that drive negotiation. `MechTypes` maps raw OID bytes to human-readable mechanism names for NTLMSSP, Microsoft Kerberos, Kerberos, Kerberos user-to-user, and NEGOEX; `TypesMech` provides the reverse lookup commonly used when constructing `MechTypes` arrays.

`asn1encode(data)` emits BER length-prefixed payloads for lengths from short form through 4-byte long form. `asn1decode(data)` reads a BER length field and returns `(payload_slice, consumed_byte_count)`. These helpers encode only lengths, not tags; callers prepend tags separately.

`GSSAPI` models the generic GSS-API initial context token wrapper. It stores fields in `self.fields`, defaults `UUID` to the SPNEGO OID, parses `ASN1_AID`/`ASN1_OID` wrappers in `fromString()`, exposes the remaining token as `Payload`, and emits the wrapper in `getData()`.

`SPNEGO_NegTokenResp` parses and builds target/client response tokens. Its fields can include `NegState`, `SupportedMech`, `ResponseToken`, and `mechListMIC`. `getData()` has separate branches for server responses with negotiation state and supported mechanism, server responses without response token, state-only responses, and client responses with or without a mechanism-list MIC.

`SPNEGO_NegTokenInit` subclasses `GSSAPI` and parses/builds the initial SPNEGO token. It extracts a list of mechanism OIDs into `MechTypes` and optionally extracts a `MechToken`. `getData()` serializes the mechanism list and optional token, stores the resulting inner token as `Payload`, then delegates to `GSSAPI.getData()`.

`SPNEGOCipher` wraps NTLM signing/sealing functions. It derives client/server signing and sealing keys with `ntlm.SIGNKEY()` and `ntlm.SEALKEY()` when extended session security is negotiated, initializes ARC4 handles, and exposes `encrypt()`, `decrypt()`, and `sign()` for SPNEGO session protection.

## Control Flow

SPNEGO token parsing is a strict tag-by-tag walk over bytes. `GSSAPI.fromString()` first validates the application identifier tag (`0x60`), decodes the wrapper length, validates the OID tag, decodes the OID, and stores all remaining bytes as the SPNEGO payload. `SPNEGO_NegTokenInit.fromString()` then validates the inner `NegTokenInit` tag, sequence tag, mechanism-list context tag, nested sequence, and each OID until a non-OID tag is reached. After the mechanism list it checks whether the remaining data starts with the mechanism-token context tag and, if so, decodes the nested octet string into `MechToken`.

`SPNEGO_NegTokenResp.fromString()` expects a response token tag, then a sequence. It first checks whether a negotiation-state field is present. If present, it decodes the enumerated value, then optionally consumes `SupportedMech`, and finally consumes `ResponseToken` if present. If the first field is already a response token, it skips state/mechanism parsing. The response token itself is expected to be an ASN.1 octet string nested inside the response-token context tag.

Serialization mirrors those fixed shapes. `SPNEGO_NegTokenInit.getData()` builds OID entries, wraps them in the mechanism-list sequence and optional mechanism token, assigns `Payload`, and relies on `GSSAPI.getData()` for the outer GSS header. `SPNEGO_NegTokenResp.getData()` chooses an ASN.1 layout from the field keys currently present; missing keys materially change the produced token shape.

`SPNEGOCipher` initializes per-direction RC4 state in the constructor. `encrypt()` seals and signs outgoing client data using the current sequence number, then increments the sequence. `decrypt()` calls `ntlm.SEAL()` against the server-side keys and handles but does not increment `__sequence`. `sign()` computes a MAC over caller-provided data and increments `__sequence`; optionally it resets both sealing handles to their initial RC4 state.

## State And Persistence Behavior

There is no disk or network persistence. Token objects keep parsed and caller-supplied values in a mutable `fields` dictionary. Re-serialization is entirely derived from current field contents except for `GSSAPI.UUID`, which defaults to the SPNEGO OID.

`SPNEGOCipher` has meaningful in-memory state. It stores negotiated flags, signing/sealing keys, RC4 encrypt-call handles for client and server directions, and a private sequence counter. The ARC4 handles are stateful stream ciphers, so call order matters. `encrypt()` and `sign()` advance `__sequence`; `decrypt()` uses the current sequence but does not advance it in this implementation, so consumers must understand expected sequencing before mixing encrypt/decrypt/sign operations.

## Dependencies And Integration Points

The module depends on Python `struct` for byte packing, `impacket.ntlm` for NTLM key derivation/MAC/sealing, and `Cryptodome.Cipher.ARC4` for RC4 stream state. It is integrated by higher-level Impacket authentication code that builds SPNEGO blobs for SMB, SMB2/3, and DCERPC, especially when transporting NTLMSSP negotiate/challenge/authenticate messages.

It also exposes OID mappings used by callers to select or display mechanisms. `TypesMech['NTLMSSP - Microsoft NTLM Security Support Provider']` is the typical path for constructing an initial mechanism list, while parsed `SupportedMech` values are raw OID bytes that can be resolved through `MechTypes`.

## Risks And Edge Cases

ASN.1 handling is handwritten and intentionally narrow. It does not implement a general BER/DER parser, indefinite lengths, high-tag-number forms, or schema-level validation. Truncated data usually fails through `struct.unpack()` or explicit tag checks rather than through structured parse errors.

`asn1decode()` has a precedence-sensitive expression in the `0x83` length branch: `data[:len2 << 16 + len3]` is parsed differently from the intended `data[:(len2 << 16) + len3]`. Very large tokens are unusual here, but that branch is a correctness risk for 3-byte BER lengths.

`GSSAPI.fromString()` stores the parsed OID as `OID` but `getData()` serializes `UUID`; parsing a non-default OID and re-emitting without copying `OID` back to `UUID` will produce the default SPNEGO OID. That is probably acceptable for this SPNEGO-specific wrapper but is a trap if reused as a generic GSS token class.

`SPNEGO_NegTokenResp.getData()` is field-presence driven. Partial field combinations outside the anticipated branches can emit a client-style response or raise `KeyError` late. The parser similarly supports only a subset of optional field orderings.

`SPNEGOCipher` relies on mutable RC4 handles and sequence counters. Reusing a cipher object across independent sessions or calling signing/decryption in an unexpected order can corrupt message protection state. The non-extended-session-security branch assigns `__clientSealingKey` twice and never separately assigns `__serverSealingKey`, although both signing and sealing keys are equivalent in that mode.

## Test Signals

Useful tests should round-trip `asn1encode()`/`asn1decode()` at boundary lengths `0x7f`, `0x80`, `0xff`, `0x100`, `0xffff`, and `0x10000`, with explicit coverage for the 3-byte length branch. Token tests should build a `SPNEGO_NegTokenInit` with NTLM and Kerberos OIDs plus a dummy mechanism token, parse it back, and verify `MechTypes`, `MechToken`, and outer GSS fields.

Response-token tests should cover server responses with `NegState` only, `NegState` plus `SupportedMech`, full server responses with `ResponseToken`, and client responses with and without `mechListMIC`. Negative tests should assert failures for wrong tags, missing nested octet strings, and truncated BER lengths.

Cipher tests should use known NTLM session security vectors or local round-trip expectations from `ntlm.SEAL()`/`ntlm.MAC()`, verify sequence increments after `encrypt()` and `sign()`, and explicitly document the expected decrypt sequence behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/spnego.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/structure.py -->
# sources/user-network-fs/impacket/impacket/structure.py

## Purpose

`structure.py` is Impacket's generic binary structure framework. It lets protocol classes declare ordered field layouts with compact format strings, then pack Python values into bytes and unpack bytes back into named fields. The class supports normal `struct` formats plus Impacket-specific extensions for raw byte blobs, NUL-terminated strings, UTF-16LE strings, DCE/RPC string headers, computed lengths, arrays, literals, optional pointer-like fields, and computed values.

The file also provides diagnostic helpers (`hexdump`, `pretty_print`) and a bitmask formatter (`parse_bitmask`). It is a foundational utility for many Impacket protocol modules that need declarative packet or record definitions without writing custom byte parsing for every message type.

## Important APIs, Types, And Functions

`Structure` is the central type. Subclasses define `commonHdr` and/or `structure` as ordered tuples of `(fieldName, format)` or `(fieldName, format, class_or_code)`. Construction optionally accepts raw `data`, which triggers `fromString()`, or an `alignment` value used to pad fields while packing and skip padding while unpacking.

`Structure.__init__()` initializes `fields`, `rawData`, an encoding-aware `self.b()` conversion helper based on `ENCODING`, and either parses supplied data or leaves `self.data` unset. `fromFile()` reads exactly `len(answer)` bytes for a new instance, which depends on the subclass's current default serialized length.

`getData()` serializes `commonHdr + structure` in order through `packField()`. `fromString()` iterates the same field definitions, computes how many bytes belong to each field with `calcUnpackSize()`, unpacks the slice, stores it through `__setitem__()`, then advances by the packed size plus optional alignment padding.

`pack()`, `unpack()`, `calcPackSize()`, and `calcUnpackSize()` implement the format language. They handle void fields (`_`), literals (`'xxxx` and `"xxxx`), computed values (`?=expression`), address/optional fields (`?&fieldname`), computed length fields (`?-fieldname`), arrays (`count*elementFormat`), printf-style formats, `z` ASCII NUL-terminated values, `u` UTF-16LE-style NUL-NUL-terminated values, `w` DCE/RPC/NDR strings, raw/embedded fields (`:`), and ordinary Python `struct` specifiers.

`formatForField()`, `findAddressFieldFor()`, `findLengthFieldFor()`, and `calcPackFieldSize()` support the field relationship machinery. `zeroValue()` and `clear()` initialize fields according to their formats. `dump()` prints known fields first and extra fields afterward, recursively dumping nested `Structure` values.

`pretty_print()`, `hexdump()`, and `parse_bitmask()` are module-level utilities. `hexdump()` prints offsets, hexadecimal bytes, and printable ASCII. `parse_bitmask()` expands known set bits through a caller-provided mapping and prints unknown bits as hex.

## Control Flow

Serialization starts at `getData()`. If `self.data` is set, it returns the cached raw value directly. Otherwise it walks `commonHdr` and `structure`, calls `packField()` for each field, appends the result, and applies alignment padding after each field when configured. `packField()` looks up the field's current value if present, otherwise passes `None`; this allows computed formats and literals to serialize without stored values.

`pack()` dispatches by format features in a fixed order. It first honors optional address fields by suppressing absent optional data, then handles void and literal fields. It evaluates computed `=` expressions in a context containing `self` and current fields if direct packing fails. For `&` address fields it packs a masked `id()` of the referenced field or zero. For `-` length fields it packs the current length of the referenced field unless the caller supplied an explicit value. For arrays it packs each element and optionally prefixes or validates the count. String and raw modes then convert data to bytes or delegate to nested `Structure.getData()`, before ordinary struct packing handles scalar values.

Parsing starts at `fromString()`. For each declared field, `calcUnpackSize()` determines the slice size. It first respects optional address fields and already-parsed length fields, then handles literals, arrays, terminator-based strings, DCE/RPC string lengths, raw fields, and scalar struct sizes. `unpack()` then interprets the slice with matching dispatch rules. For `:` fields it either returns raw bytes or instantiates the third tuple argument as a nested parser. For `_` fields with a third argument, it evaluates that code against current fields and the remaining input.

The field relationship functions are intentionally simple scans over the declared layout. `findAddressFieldFor(field)` searches for a format ending in `&field`; when the corresponding address field unpacks as false, the target field is skipped. `findLengthFieldFor(field)` searches for a format ending in `-field`; when found during unpacking, the previously parsed length controls the target slice.

## State And Persistence Behavior

`Structure` stores parsed and caller-supplied values in `self.fields`. `__setitem__()` invalidates `self.data` so later `getData()` recomputes serialized bytes. `setData()` can override that behavior by setting a raw serialized buffer that `getData()` returns as-is until another field assignment clears it.

`rawData` preserves the last byte string passed to `fromString()`, but the class does not persist state outside the object and does not perform I/O except for `fromFile()`. Alignment is per-instance unless a subclass already defines `alignment`. Encoding is class-level through `ENCODING`, defaulting to `latin-1`, and affects string-to-byte conversion for all non-byte text values.

Computed fields are not stored unless they are in the declared layout and parsed or assigned. Several format modes derive values dynamically from the current `fields` dictionary at pack time, so serialized output can change when referenced fields change even if the length/address field itself was not explicitly updated.

## Dependencies And Integration Points

The module depends on `re` for UTF-16 terminator scanning, `struct.pack/unpack/calcsize` for scalar binary conversion, `six` for Python 2/3 byte compatibility, and `binascii.hexlify` for diagnostics. It is imported throughout Impacket by protocol-specific packet and record classes that subclass `Structure` or call its helpers.

Integration is primarily declarative: protocol modules define tuples such as fixed headers, variable tails, embedded structures, counted arrays, and literal magic values. `ImpactPacket`, DCERPC, SMB, DHCP, DNS, ESE, and other protocol code can then reuse this parser/serializer while keeping protocol field order local to their own classes.

The third tuple element for `:` and `_` fields is an important extension point. It allows nested structure classes for embedded byte ranges, or evaluated code for fields that cannot be represented by a simple format. This makes the framework flexible but also means field definitions can execute arbitrary expressions during pack or unpack.

## Risks And Edge Cases

The format language uses `eval()` for computed packing and special unpack code. That is powerful inside trusted protocol definitions but unsafe for untrusted format strings. Consumers should treat structure definitions as code, not data.

Length and optional-field resolution depend on declaration order. A `?-field` length or `?&field` address only works when the controlling field has already been parsed before the dependent field. Misordered structures can skip data, consume the wrong number of bytes, or raise late exceptions.

`getData()` returns `self.data` directly when set, even if fields have stale values. This is intentional cache/override behavior, but it can surprise callers that mutate nested objects without assigning them back through `__setitem__()`.

The string modes have historical byte semantics. `z` unpacking returns `str` on Python 3 after Latin-1 decoding, while `u` returns bytes without the terminator. The `w` format reads the first 32-bit length and returns `data[12:12+l*2]` without validating the duplicated length fields or maximum count. Truncated data can surface as struct errors, terminator search errors, or partially meaningful values depending on the format.

The `:` pack path treats an integer as `bytes(data)`, which creates that many NUL bytes rather than encoding the numeric value. That behavior is consistent with Python but can be a trap if callers intended a scalar. `calcPackSize(':', data)` uses `len(data)`, so it also expects byte-like or sized objects.

Array parsing with omitted counts consumes until the end of the supplied slice, so it is only as safe as the enclosing size calculation. Constant-count arrays validate pack-time lengths but parsing trusts enough bytes exist for each element. `fromFile()` relies on `len(answer)`, which may be expensive or incorrect for dynamic structures lacking initialized variable fields.

## Test Signals

Focused tests should define small `Structure` subclasses for each format family and assert pack/unpack round trips. Coverage should include scalar `struct` formats, literals, raw `:` bytes, nested `:` structures, computed `=` fields, computed `-field` lengths, `&field` optional data, fixed and counted arrays, omitted-count arrays, `z`, `u`, and `w` strings.

Regression tests should verify alignment padding during both packing and unpacking, cache invalidation after `__setitem__()`, `setData()` raw override behavior, and `clear()` zero values. Negative tests should cover mismatched literals, missing NUL/NUL-NUL terminators, fixed array length mismatches, truncated counted data, unsupported printf unpack sizing, and misordered length/address declarations.

Security-oriented tests should confirm that computed expressions run only from trusted class definitions in the current usage model, and that protocol parsers using `Structure` validate externally supplied lengths before allocating or slicing large payloads. Diagnostics can be tested by checking `parse_bitmask()` output for known and unknown flags and by smoke-testing `hexdump()` with bytes, integers, and `None`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/structure.py -->
