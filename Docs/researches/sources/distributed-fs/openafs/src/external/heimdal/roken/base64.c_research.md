# sources/distributed-fs/openafs/src/external/heimdal/roken/base64.c

Purpose: implements simple base64 encode/decode helpers for roken portability users.

Important APIs/types/functions: `base64_chars[]` is the alphabet. `pos()` returns the alphabet index. `base64_encode()` allocates and returns a NUL-terminated encoded string. `token_decode()` decodes a 4-character quantum and tracks padding. `base64_decode()` decodes into caller-provided storage.

Control flow: encoding groups up to three bytes into a 24-bit integer, emits four alphabet characters, and substitutes `=` padding when input runs short. Decoding advances in four-character chunks while input chars are alphabet or `=`, validates padding order, and writes one to three bytes per quantum.

State and persistence behavior: stateless. Encode allocates output that the caller owns; decode writes into caller-provided memory without allocating.

Dependencies and integration points: declared by `base64.h`; used by any roken/Heimdal code needing compact binary-to-text conversion.

Risks: `base64_decode()` does not take an output buffer length, so callers must preallocate enough space. `pos()` returns -1 for invalid chars, but the loop largely filters characters before decoding. Encoded allocation uses a compact formula and rejects negative or huge `int` sizes.

Test signals: RFC base64 vectors, zero-length input, one/two-byte padding, invalid padding position, invalid characters, and caller buffer sizing tests under sanitizers.
