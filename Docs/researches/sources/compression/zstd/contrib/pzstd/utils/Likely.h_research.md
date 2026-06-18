<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Likely.h -->
# sources/compression/zstd/contrib/pzstd/utils/Likely.h

## Purpose
`Likely.h` defines branch prediction hint macros for pzstd utility code.

## Important APIs, Types, And Functions
It exposes `LIKELY(x)` and `UNLIKELY(x)`, mapping to `__builtin_expect` when available and to plain expressions otherwise.

## Control Flow
The header has compile-time conditional behavior only; runtime flow is whatever caller expressions produce.

## State And Persistence
No state or persistence exists.

## Dependencies And Integration Points
It is available for pzstd utility code that wants compiler branch hints without hard-coding GCC/Clang builtins.

## Risks
Overuse or wrong hints can degrade performance. Macro expressions should avoid side effects that are surprising under macro expansion.

## Test Signals
Compilation on supported and fallback compilers is the main signal.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Likely.h -->
