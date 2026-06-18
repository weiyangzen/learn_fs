# sources/distributed-fs/openafs/src/external/heimdal/roken/strsep.c

## Purpose
Provides a fallback `strsep` tokenizer for systems that lack it.

## Important APIs, Types, And Functions
The exported function is `strsep(char **str, const char *delim)`, macro-mapped to `rk_strsep` by `roken.h` when needed.

## Control Flow
If `*str` is `NULL`, it returns `NULL`. Otherwise it saves the current token start, advances `*str` by `strcspn` until a delimiter or NUL, terminates the token in place when a delimiter is found, advances past the delimiter, or sets `*str` to `NULL` at end-of-string.

## State And Persistence
The input string is modified in place by replacing delimiters with NUL bytes. The caller's cursor pointer is updated.

## Dependencies And Integration Points
Used by roken consumers that expect BSD tokenizer semantics, including empty-field preservation unlike `strtok`.

## Risks And Test Signals
The function requires mutable input. Tests should cover leading, trailing, adjacent, and absent delimiters; empty delimiter strings; and repeated calls until `NULL`.
