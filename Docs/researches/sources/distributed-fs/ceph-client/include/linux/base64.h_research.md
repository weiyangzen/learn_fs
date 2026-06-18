# sources/distributed-fs/ceph-client/include/linux/base64.h

## Purpose
Declares kernel base64 encode/decode helpers supporting standard RFC 4648, URL-safe RFC 4648, and IMAP RFC 3501 alphabets.

## Important APIs, types, and functions
- `enum base64_variant` selects `BASE64_STD`, `BASE64_URLSAFE`, or `BASE64_IMAP`.
- `BASE64_CHARS(nbytes)` computes an encoded character upper bound for a byte count.
- `base64_encode()` and `base64_decode()` take explicit lengths, destination buffers, padding policy, and variant.

## Control flow and state
The header has no inline logic beyond size calculation. Callers provide source and destination buffers; implementation performs stateless conversion according to variant and padding.

## State and persistence behavior
No persistent state. Encoded data may become persistent only through callers, for example filenames, keys, or metadata.

## Dependencies and integration points
Depends on kernel integer types. Likely integrated by filesystem crypto/name handling and other subsystems that need in-kernel textual binary representation.

## Risks
Callers must size `dst` correctly and match decode padding/variant to the encoded input. `BASE64_CHARS` is useful for expansion but does not account for terminators unless callers add space.

## Test signals
Use known vectors for all variants, padded and unpadded inputs, invalid characters, short/truncated inputs, and buffer-boundary lengths.
