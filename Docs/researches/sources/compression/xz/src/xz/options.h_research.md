# Research: sources/compression/xz/src/xz/options.h
## sources/compression/xz/src/xz/options.h

Purpose: Declares old-style filter option parsers.

Important APIs: `options_delta()`, `options_bcj()`, and `options_lzma()` return allocated `lzma_options_delta`, `lzma_options_bcj`, and `lzma_options_lzma` structures respectively, exiting on invalid input.

Control flow and integration: `args.c` calls these parser functions while assembling custom filter chains for `coder.c`.

State and persistence: The allocated return values become filter-chain option pointers and persist until filter cleanup or process exit.

Risks: Callers must treat returned pointers as owned by the filter chain and not stack-allocate substitutes with shorter lifetime.

Test signals: Integration tests through CLI old-style filter options and debug cleanup with leak checking.
