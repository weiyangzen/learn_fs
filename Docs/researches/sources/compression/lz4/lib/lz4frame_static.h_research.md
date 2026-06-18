# sources/compression/lz4/lib/lz4frame_static.h

## Purpose
`lz4frame_static.h` is a compatibility shim for older users of the LZ4 frame static API. The declarations that used to live here have been merged into `lz4frame.h`; this header now enables `LZ4F_STATIC_LINKING_ONLY` and includes `lz4frame.h`.

## Important APIs And Types
The file itself declares no functions or types. Its effective API is the side effect of defining `LZ4F_STATIC_LINKING_ONLY`, which exposes static-linking-only declarations from `lz4frame.h`: frame error enumeration, `LZ4F_getErrorCode()`, `LZ4F_getBlockSize()`, `LZ4F_uncompressedUpdate()`, custom allocator hooks, advanced context and CDict creation functions, and context-size inspection.

## Control Flow And State
There is no runtime control flow or state. Preprocessor flow is straightforward: an include guard prevents repeated inclusion, `LZ4F_STATIC_LINKING_ONLY` is defined, and `lz4frame.h` is included. Any resulting symbols and declarations are controlled by `lz4frame.h` and build macros such as `LZ4F_PUBLISH_STATIC_FUNCTIONS`.

## Dependencies And Integration Points
This header depends directly on `lz4frame.h`. It is used by `lz4file.h` so the file wrapper can use `LZ4FLIB_STATIC_API`, `LZ4F_errorCodes`, and `LZ4F_getBlockSize()`. It also supports downstream code that still includes `lz4frame_static.h` instead of defining `LZ4F_STATIC_LINKING_ONLY` before including `lz4frame.h`.

## Risks And Edge Cases
Including this header broadens the visible API to unstable static-only declarations. Because it defines `LZ4F_STATIC_LINKING_ONLY` before inclusion, translation units that include it may see declarations that are not exported by a shared LZ4 library unless the library was built with `LZ4F_PUBLISH_STATIC_FUNCTIONS`. This can create link errors when code compiles against static-only prototypes but links dynamically.

## Test Signals
Test signals are compile/link oriented: include the header in C and C++ translation units, verify static-only declarations are visible, verify repeated inclusion is harmless, verify dynamic-link builds fail or omit static-only symbols unless explicitly published, and verify legacy consumers can replace direct `lz4frame_static.h` use with `#define LZ4F_STATIC_LINKING_ONLY` plus `#include "lz4frame.h"`.
