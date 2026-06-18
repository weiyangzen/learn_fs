## sources/distributed-fs/openafs/src/WINNT/client_osi/largeint.h

Purpose: Supplies prototypes and comparison macros for legacy Windows large-integer arithmetic routines used when compiler/platform headers lack them.

Important APIs/types: Declares add, subtract, multiply, divide, negate, conversion, and shift functions for `LARGE_INTEGER`/`ULARGE_INTEGER`, plus macros for comparisons and zero checks.

Control flow/state: Header-only declarations/macros; arithmetic implementations live in external libraries/source. Macros inspect `HighPart` and `LowPart` directly.

Dependencies/integration: Included by `osi.h` for older MSVC versions. Wrapped in `extern "C"` for C++ consumers.

Risks/tests: Direct signed/unsigned comparisons can be subtle around negative high parts and unsigned low parts. Test compiler-version selection, link availability, division remainder semantics, and boundary values around zero, negative, and high-bit cases.
