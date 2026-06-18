# File Research: sources/block-storage/stratisd/src/bin/udev-lib/stratis-base32-decode.rs

Tiny udev helper that decodes a base32 value.

Key behavior:
- Requires two arguments: variable name and base32 string.
- Decodes with `data_encoding::BASE32_NOPAD`.
- Interprets decoded bytes as UTF-8.
- Prints `name=decoded_value`.

Likely used from udev rules to decode Stratis-safe encoded values into environment assignments.
