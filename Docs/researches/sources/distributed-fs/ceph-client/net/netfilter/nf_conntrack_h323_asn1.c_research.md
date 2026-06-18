# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_asn1.c

## Purpose
`nf_conntrack_h323_asn1.c` is a compact BER/PER decoding library used by the H.323 conntrack/NAT helper. It decodes selected H.323, RAS, H.245 multimedia control, and Q.931 user-user information structures into C structs defined by generated field tables.

## Important APIs, Types, And Functions
The local `field_t` descriptor describes ASN.1 type, size/range constraints, attributes, output offset, and child fields. `struct bitstr` tracks input buffer, current byte, end, and bit offset. Primitive readers are `get_len()`, `get_bit()`, `get_bits()`, `get_bitmap()`, and `get_uint()`. Decoder functions are dispatched from `Decoders[]`: null, bool, oid, int, enum, bit string, numeric string, octet string, BMP string, sequence, sequence-of, and choice.

Exported decode entry points are `DecodeRasMessage()`, `DecodeMultimediaSystemControlMessage()`, and `DecodeQ931()`. `DecodeH323_UserInformation()` is the Q.931 nested UUIE decoder. Generated schema tables are included from `nf_conntrack_h323_types.c`.

## Control Flow
Each public decode function initializes a `bitstr` and invokes the appropriate top-level descriptor. Sequence decoding reads extension and optional-field bitmaps, decodes root fields, then decodes extension fields or skips unknown newer-version open fields. Choice decoding reads the selected alternative and decodes or skips based on extension/open-field metadata. Sequence-of decodes a count, writes a capped count to output when requested, and decodes only storable entries while still advancing over all input entries. Q.931 parsing checks the protocol discriminator, skips call reference and message type metadata, then searches information elements for UserUserIE.

## State And Persistence
The decoder is stateless across calls. It writes decoded fields into caller-provided output structs according to descriptor offsets and stores some octet-string values as offsets into the original input buffer. There is no allocation or durable state.

## Dependencies And Integration Points
It depends on generated H.323 descriptor tables and public H.323 structs/error codes from `nf_conntrack_h323_asn1.h`. H.323 helpers use decoded addresses, ports, and message variants to create expectations and NAT mappings.

## Risks
The main risk is parser safety. Every bit/byte advance must be bounded by `nf_h323_error_boundary()` checks. Range checks reject oversized bitmaps and unknown non-extension choices, while extension fields may be skipped for forward compatibility. Offsets written into output structs are relative to `bs->buf`, so callers must keep the source buffer valid while interpreting them.

## Test Signals
Test valid RAS, H.245, and Q.931 messages; truncated buffers at every primitive length boundary; extension fields and unknown alternatives; oversized bitmaps/counts; open-field length skipping; sequence-of counts larger than output capacity; Q.931 without UUIE; bad protocol discriminator; and H323_TRACE builds.
