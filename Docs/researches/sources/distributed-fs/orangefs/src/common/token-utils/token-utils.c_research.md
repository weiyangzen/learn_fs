<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/token-utils.c -->
# sources/distributed-fs/orangefs/src/common/token-utils/token-utils.c

## Purpose
Implements reusable delimiter tokenization helpers, primarily an allocation-free in-place iterator with optional heap-allocating token APIs behind `TOKEN_ENABLE_HEAP_VERSION`.

## Important APIs, Types, And Functions
Always compiled functions are `iterate_tokens_inplace`, `no_op_inplace`, `dump_token_inplace`, and `dump_tokens_inplace`. Optional heap functions include `iterate_tokens`, `free_token`, `free_tokens`, `dump_token`, `dump_tokens`, `get_token_count`, and `get_tokens`.

## Control Flow
The in-place iterator validates inputs, copies the input into caller-provided scratch storage with `strncpy`, treats token limit `0` as unlimited, then repeatedly calls `strtok_r`/`strtok_s`. For each token it optionally copies token text to caller-provided output buffers and optionally invokes an action callback, stopping on callback failure or token limit. The heap version first counts tokens, allocates a vector, duplicates each token, and frees partial results on allocation failure.

## State And Persistence
No global state is used. The functions mutate caller-provided scratch buffers and optionally allocate heap token arrays in the disabled-by-default heap variant.

## Dependencies And Integration Points
Depends on standard C string/stdio/limits headers and `token-utils.h`; Windows maps `strtok_r` to `strtok_s`. Included in both library and server builds.

## Risks And Test Signals
Callers must zero-initialize scratch buffers because `strncpy` may not terminate at `input_limit`; copy-out token buffers have the same truncation risk; heap `get_token_count` prints debug messages; and callback failure returns `-1` while count reports successful actions. Tests should cover null inputs, empty strings, repeated delimiters, token limits, copy-out truncation, callback failures, Windows tokenization, and optional heap build behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/token-utils.c -->
