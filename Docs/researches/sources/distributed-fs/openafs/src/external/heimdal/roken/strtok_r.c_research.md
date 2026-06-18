# sources/distributed-fs/openafs/src/external/heimdal/roken/strtok_r.c

## Purpose
Implements reentrant `strtok_r` for platforms where only non-reentrant tokenization is available.

## Important APIs, Types, And Functions
The exported function is `strtok_r(char *s1, const char *s2, char **lasts)`, declared through `roken.h.in` when needed.

## Control Flow
If `s1` is `NULL`, tokenization resumes at `*lasts`. Leading delimiters are skipped, an empty remainder returns `NULL`, then the function scans until the next delimiter, terminates the token in place, updates `*lasts`, and returns the token start.

## State And Persistence
No internal static state is used. Caller-provided `*lasts` persists tokenization progress and the mutable input string is modified.

## Dependencies And Integration Points
Provides thread-safe tokenization semantics for roken consumers on older platforms.

## Risks And Test Signals
The function assumes `lasts` and resume pointers are valid; if called with `s1 == NULL` and an uninitialized `*lasts`, it will dereference invalid memory. Tests should cover multiple independent tokenizer states, delimiter-only strings, empty tokens behavior, and final `NULL`.
