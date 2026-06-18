# sources/distributed-fs/ceph/src/rgw/rgw_b64.h

Purpose: header-only Base64 encode/decode helpers in namespace `rgw`, used by checksum and metadata code that needs compact textual binary representations.

Important APIs/types/functions: `to_base64<wrap_width>(std::string_view)` uses Boost archive iterator adaptors and optional MIME line wrapping; `from_base64(std::string_view)` removes whitespace and decodes Base64 input after stripping trailing padding.

Control flow: encoding pads the input length to a multiple of three for `=` suffix emission, runs `transform_width` plus `base64_from_binary`, then appends padding. Decoding returns an empty string for empty input, removes all trailing `=`, filters whitespace, then runs `binary_from_base64` and `transform_width`.

State/persistence: stateless, no persistence, no global mutable state.

Dependencies/integration: depends on Boost archive iterator adaptors and is used by `rgw_cksum.h` for checksum text rendering.

Risks: malformed Base64 input can throw through Boost iterators; callers do not get an error-code API. `to_base64()` comments say pad to multiple of three for output, but Base64 output length is conventionally multiple of four, so edge cases deserve regression tests. `from_base64()` assumes padding only appears at the end.

Test signals: round-trip empty, one-byte, two-byte, three-byte, long wrapped MIME strings, whitespace in input, invalid characters, and checksum-specific binary payloads.
