# sources/distributed-fs/openafs/src/external/heimdal/roken/hex.c

Purpose: implements hexadecimal encoding and decoding helpers.

Important APIs/types/functions: `hexchar[]` is the uppercase alphabet. `pos()` maps a hex digit to a nibble after `toupper()`. `hex_encode()` allocates an uppercase hex string. `hex_decode()` decodes into caller-provided storage.

Control flow: encoding checks size overflow, allocates `size * 2 + 1`, emits two hex chars per byte, and NUL-terminates. Decoding checks output capacity using rounded-up input length, handles odd-length input by treating the first digit as a low byte, then decodes pairs.

State and persistence behavior: stateless. Encode output is caller-owned; decode writes into caller storage.

Dependencies and integration points: declared by `hex.h` and available as `rk_hex_encode`/`rk_hex_decode` through macros.

Risks: `hex_decode()` does not reject non-hex characters; `pos()` returns -1, which is then folded into output nibbles. Odd-length behavior may surprise callers expecting strict pair input.

Test signals: uppercase output, lowercase decode, odd-length decode, invalid-character behavior, output-length rejection, and zero-length input.
