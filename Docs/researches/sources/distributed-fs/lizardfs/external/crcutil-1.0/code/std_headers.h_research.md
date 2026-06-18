# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/std_headers.h

## Purpose

`std_headers.h` centralizes standard C header inclusion and suppresses several MSVC warnings produced by Microsoft headers or by aggressive optimization diagnostics. It provides the common definitions used by crcutil's low-level headers.

## Important APIs and macros

The file defines `_CRT_SECURE_NO_WARNINGS` under MSVC and disables warning numbers 4820, 4514, 4127, 4710, and 4711. It includes `<stdio.h>`, `<string.h>`, `<stdlib.h>`, `<stddef.h>`, and `<stdarg.h>`, providing declarations and types such as `memset`, `memcpy`, `size_t`, `ptrdiff_t`, and `va_list`.

## Control flow, state, and persistence

There is no runtime logic or persistent state. The header affects compiler diagnostics and transitive availability of standard-library names.

## Dependencies and integration points

`base_types.h` includes it for `size_t` and `ptrdiff_t`; `platform.h` includes it before compiler intrinsic headers to apply warning policy. Many crcutil files inherit these standard includes transitively rather than including C headers directly.

## Risks and test signals

Broad warning suppression can hide useful diagnostics in files that include this header. The project uses C headers rather than C++ `<c*>` headers, so names are expected in the global namespace. Test signals are simple compile coverage under MSVC and GCC/Clang-like compilers, plus verifying that downstream headers do not accidentally depend on additional standard headers that are not included here.
