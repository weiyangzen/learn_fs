<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/token-utils.h -->
# sources/distributed-fs/orangefs/src/common/token-utils/token-utils.h

## Purpose
Declares token utility constants and tokenizer APIs.

## Important APIs, Types, And Functions
Defines `TOKEN_UTILS_DEFAULT_MAX_INPUT_STRLEN`, `PLUS_ONE(IN)`, and a disabled `TOKEN_ENABLE_HEAP_VERSION` switch. Declares the in-place iterator and debug/no-op helpers, plus heap token APIs when the feature macro is enabled.

## Control Flow
Callers allocate scratch storage, usually with `PLUS_ONE(max_len)`, then call `iterate_tokens_inplace` directly or through `dump_tokens_inplace`. Optional heap callers must free arrays with `free_tokens`.

## State And Persistence
No state is declared. The API contract relies on caller-owned buffers and optional caller-managed heap results.

## Dependencies And Integration Points
Used by server and library code that needs lightweight token parsing without bringing in additional parser dependencies.

## Risks And Test Signals
Risks include the macro name `PLUS_ONE` not matching comments that mention `LEN_PLUS_ONE`, disabled heap declarations being untested by default, and missing explicit include of integer types because only basic C types are used. Compile tests with and without `TOKEN_ENABLE_HEAP_VERSION` and tokenizer edge-case tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/token-utils.h -->
