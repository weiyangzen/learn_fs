# sources/distributed-fs/openafs/src/external/heimdal/roken/hex.h

Purpose: public roken header for hex encode/decode helpers.

Important APIs/types/functions: defines export/calling macros if missing, maps `hex_encode` to `rk_hex_encode` and `hex_decode` to `rk_hex_decode`, and declares `hex_encode(const void *, size_t, char **)` plus `hex_decode(const char *, void *, size_t)`.

Control flow: not executable; it controls symbol naming and prototypes.

State and persistence behavior: no state. The API contract makes encode allocate caller-owned text and decode consume caller-provided storage with a length.

Dependencies and integration points: included by `hex.c` and consumers needing stable roken-prefixed symbols while using convenient names in source.

Risks: macro renaming can surprise code that needs the unprefixed names. Decode returns `ssize_t`, so callers must handle negative errors.

Test signals: compile/link with macro-renamed symbols, prototype compatibility on Windows and Unix, and inclusion alongside other roken headers.
