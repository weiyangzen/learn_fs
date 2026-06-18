# sources/distributed-fs/ceph-client/net/ceph/armor.c

## Purpose
Provides Ceph's small base64-like armor and unarmor helpers for encoding binary secrets into printable strings and decoding them back.

## Important APIs, Types, and Functions
The exported local APIs are `ceph_armor()` and `ceph_unarmor()`, declared here and in `crypto.h`. Internal helpers `encode_bits()` and `decode_bits()` map six-bit values to the `A-Z a-z 0-9 + /` alphabet and accept `=` padding.

## Control Flow
`ceph_armor()` consumes bytes from `src` to `end`, emits 4-byte base64 groups, inserts `=` padding for one- and two-byte tails, and inserts a newline after every 64 encoded characters. It returns the encoded byte count, including newlines, but does not NUL-terminate. `ceph_unarmor()` skips newline characters, requires complete 4-character groups, validates each character, writes one to three decoded bytes according to padding, and returns decoded length. Invalid characters or incomplete groups return `-EINVAL`.

## State and Persistence
The only state is the static alphabet string. The functions mutate caller-provided buffers and do not allocate or persist data.

## Dependencies and Integration Points
Used by `ceph_crypto_key_unarmor()` to decode mount `secret=` values. Depends only on errno definitions and caller-managed buffer sizing.

## Risks
There is no destination-size parameter, so callers must provision enough output space. `ceph_unarmor()` treats `=` as a non-negative six-bit value and stops on padding positions; malformed padding in odd positions relies on the group logic. The encoder does not append a terminator, which is correct for binary output but can surprise string callers.

## Test Signals
Round-trip binary keys of lengths 0, 1, 2, 3, and larger than 48 bytes, verify newline insertion at 64 encoded characters, reject invalid characters and truncated groups, decode padded strings correctly, and run with KASAN or fortified buffers to validate caller sizing.
