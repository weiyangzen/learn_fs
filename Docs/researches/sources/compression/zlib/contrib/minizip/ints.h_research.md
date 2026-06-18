# sources/compression/zlib/contrib/minizip/ints.h

Purpose: defines fixed-width signed and unsigned integer typedefs for minizip on systems that may lack `stdint.h`.

Important APIs/types/functions: typedefs `i8_t`, `ui8_t`, `i16_t`, `ui16_t`, `i32_t`, `ui32_t`, `i64_t`, `ui64_t`, and printf format fragments `PI32`, `PUI32`, `PI64`, `PUI64`.

Control flow: preprocessor checks `limits.h` constants to select suitable built-in C types. If no matching width is available, compilation stops with `#error`.

State and persistence: compile-time declarations only.

Dependencies/integration: included by `ioapi.h` for `ZPOS64_T` and by other minizip sources needing fixed-size types.

Risks: assumes `char` is 8-bit and that either `long`, `long long`, or `ULONG_LONG_MAX` gives 64-bit support. Format fragments are partial specifiers and must be used carefully in complete printf formats. It does not use standard `stdint.h` even when present.

Test signals: compile success on supported platforms is the main signal; cross-platform CI should cover ILP32, LP64, LLP64, and older compilers.
