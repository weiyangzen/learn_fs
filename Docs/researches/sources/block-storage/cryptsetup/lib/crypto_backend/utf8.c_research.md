# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/utf8.c

Provides UTF-8/UTF-16LE conversion helpers adapted from systemd/GLib lineage.

Key points:
- UTF-16 helpers detect surrogate ranges and combine valid surrogate pairs into Unicode code points.
- `crypt_utf16_to_utf8()` treats input length as bytes, decodes little-endian UTF-16, ignores malformed surrogate fragments, and NUL-terminates the caller-provided output buffer.
- `utf8_encoded_expected_len()` recognizes 1- to 6-byte leading byte patterns.
- `utf8_encoded_to_unichar()` validates continuation bytes and returns decoded code point.
- `utf16_encode_unichar()` emits UTF-16LE words and rejects surrogate code points as invalid standalone values.
- `crypt_utf8_to_utf16()` converts valid multibyte UTF-8 to UTF-16LE; invalid or single-byte characters are copied bytewise as 16-bit values.
- `crypt_char16_strlen()` counts UTF-16 words until NUL.

Storage relevance:
- Supports formats requiring UTF-16/UTF-8 passphrase or metadata handling, especially Windows/Apple-adjacent encrypted volume formats.
