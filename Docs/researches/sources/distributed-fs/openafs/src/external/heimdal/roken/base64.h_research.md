# sources/distributed-fs/openafs/src/external/heimdal/roken/base64.h

Purpose: public roken header for base64 helpers.

Important APIs/types/functions: defines `ROKEN_LIB_FUNCTION` and `ROKEN_LIB_CALL` defaults when not already provided. Declares `base64_encode(const void *, int, char **)` and `base64_decode(const char *, void *)`.

Control flow: not executable. It establishes calling convention decoration, especially for Windows builds.

State and persistence behavior: no state. The function contract implies encode allocates a string through `char **`, while decode writes into caller-owned memory.

Dependencies and integration points: included by `base64.c` and consumers that need roken base64 without pulling a larger header.

Risks: decode declaration has no output buffer length, which makes safe use dependent on caller-side length calculation. The header exposes `int` sizes, limiting very large encodings.

Test signals: compile with and without pre-defined roken export macros, C and C++ inclusion compatibility if applicable, and ABI matching with `base64.c`.
