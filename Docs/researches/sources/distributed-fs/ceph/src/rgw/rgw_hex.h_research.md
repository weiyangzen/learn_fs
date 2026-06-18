# sources/distributed-fs/ceph/src/rgw/rgw_hex.h

## Purpose
Provides small inline helpers for converting binary buffers to lowercase hex and hex strings back to bytes.

## Important APIs, Types, And Functions
`buf_to_hex(input_range, output_iterator)` writes two lowercase hex chars per input byte. `buf_to_hex(std::array<unsigned char, N>)` returns a null-terminated `std::array<char, N*2+1>`. `hexdigit()` parses one hex digit. `hex_to_buf()` decodes a null-terminated hex string into a fixed-size output buffer and returns bytes written or negative errno.

## Control Flow
Encoding casts each input element to `uint8_t`, emits high and low nibbles through the static hex table, and returns the advanced iterator. Decoding loops over pairs of chars, validates each digit, checks destination capacity, and rejects odd-length input.

## State And Persistence Behavior
No state or persistence; all helpers are inline/stateless.

## Dependencies And Integration Points
Uses C++20 ranges/output iterator constraints, `std::array`, ctype, errno values, and standard integer types. RGW write code uses `buf_to_hex()` for MD5 etag formatting.

## Risks
`hexdigit()` passes `char` to `toupper()` without unsigned conversion; non-ASCII signed chars are theoretically unsafe, though hex input should be ASCII. `hex_to_buf()` requires a null-terminated input and cannot decode embedded nulls.

## Test Signals
Tests should cover empty arrays, all byte values, uppercase/lowercase decode, odd-length strings, invalid characters, output buffer too small, and iterator return position.
