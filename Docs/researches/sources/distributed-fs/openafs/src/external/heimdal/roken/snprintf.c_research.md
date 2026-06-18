# sources/distributed-fs/openafs/src/external/heimdal/roken/snprintf.c

## Purpose
Provides portable `snprintf`, `vsnprintf`, `asprintf`, `vasprintf`, `asnprintf`, and `vasnprintf` replacements for platforms with missing or non-C99 implementations, especially older MSVC environments.

## Important APIs, Types, And Functions
Core internals are `struct snprintf_state`, `sn_reserve`, `sn_append_char`, `as_reserve`, `as_append_char`, `pad`, `append_number`, `append_string`, `append_char`, and `xyzprintf`. Exported wrappers include `rk_snprintf`, `rk_asprintf`, `rk_asnprintf`, `rk_vasprintf`, `rk_vasnprintf`, and `rk_vsnprintf`.

## Control Flow
`xyzprintf` parses printf format strings, collecting flags, width, precision, and size modifiers, then dispatches supported conversions for characters, strings, signed/unsigned integers, octal, hex, pointers, `%n`, literal `%`, and unknown specifiers. Fixed-buffer output appends only while space remains; allocated-output mode grows a heap buffer by doubling or by needed size, respecting `max_sz` when supplied. Public wrappers set up state and terminate the output buffer.

## State And Persistence
Fixed-buffer calls mutate caller-provided memory. `as*` calls allocate heap strings returned through `char **`; callers own them. There is no global state.

## Dependencies And Integration Points
`roken.h.in` remaps standard formatting names to these functions under MSVC or missing-feature configurations. Many other roken files rely on `asprintf`, including `setenv` and `write_pid`.

## Risks And Test Signals
The implementation supports a practical subset, not full modern printf semantics: no floating point, limited length modifiers, and hand-written formatting edge cases. `%n` writes bytes actually appended, not necessarily total formatted length in truncation cases. Test signals should cover truncation return values, allocated formatting, max-size failures, flags/width/precision, `NULL` strings, integer boundaries, pointer output, and MSVC replacement builds.
