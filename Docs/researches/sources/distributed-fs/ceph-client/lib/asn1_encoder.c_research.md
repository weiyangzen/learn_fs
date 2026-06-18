<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/asn1_encoder.c -->
# sources/distributed-fs/ceph-client/lib/asn1_encoder.c

## Purpose
Provides simple ASN.1 BER/DER/CER encoder primitives for positive integers, object identifiers, context-specific tags, octet strings, sequences, and booleans.

## APIs, Types, and Functions
Exports `asn1_encode_integer()`, `asn1_encode_oid()`, `asn1_encode_tag()`, `asn1_encode_octet_string()`, `asn1_encode_sequence()`, and `asn1_encode_boolean()`. Internal helpers are `asn1_encode_oid_digit()` for base-128 OID arcs and `asn1_encode_length()` for short and long-form lengths up to `0xffffff`.

## Control Flow, State, and Persistence
Each encoder accepts a current output pointer and one-past-end pointer and returns the next write position or `ERR_PTR()`. The functions propagate existing error pointers, validate minimum space, write tag and length, then copy or encode payload. Integer encoding rejects negative values and prepends a zero byte when needed to keep positive two's-complement form. OID encoding requires 2-32 arcs and encodes the first two arcs as `oid[0] * 40 + oid[1]`. Tag and sequence helpers support two-pass in-place encoding by first reserving tag/length with negative length and later recoding a known length by stepping back two bytes. No state persists beyond the caller's buffer.

## Dependencies and Integration
Depends on `linux/asn1_encoder.h` tag macros, `linux/bug.h`, string helpers, module/export support, and consumers that build ASN.1 structures for keys, signatures, or protocol payloads. Built with `CONFIG_ASN1_ENCODER`.

## Risks and Test Signals
Risks include limited negative-integer support, short-tag-only context tags, in-place recoding limited to <=127 bytes, OID first-arc semantic validation being left to callers, and length handling above supported range. Test signals include encoding known DER fixtures, zero and high-bit positive integers, invalid negative integer calls, OIDs with multi-byte arcs, buffer-boundary failures, sequence/tag two-pass recoding, and decode/encode round trips through `asn1_ber_decoder()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/asn1_encoder.c -->
