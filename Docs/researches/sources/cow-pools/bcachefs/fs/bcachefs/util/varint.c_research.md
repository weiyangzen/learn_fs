# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/varint.c

## Summary
Implements bcachefs unsigned 64-bit variable-length integer encoding and decoding, including fast variants for callers that can overread/overwrite within safe padding.

## Main Responsibilities
- Encodes `u64` values into 1 to 9 bytes.
- Decodes varints with bounds checking.
- Provides fast encode/decode paths using unaligned 64-bit stores/loads.

## Key APIs
- `bch2_varint_encode()`.
- `bch2_varint_decode()`.
- `bch2_varint_encode_fast()`.
- `bch2_varint_decode_fast()`.

## Important Behavior
For 1 to 8 byte encodings, low marker bits encode the byte length and the value is shifted left by the byte count. A 9-byte encoding starts with `0xff` followed by the raw little-endian 64-bit value.

The checked decoder returns `-BCH_ERR_varint_decode_error` if the encoded length would pass `end`. The fast decoder may read up to 8 bytes from `in`, but still reports an error if the varint logically extends past `end`.

## Risks
Fast variants require caller-provided padding/safety for wide memory access. The decode comment says “encode” but behavior is decode. Consumers must handle the bcachefs-specific negative error code rather than generic `-1`.
