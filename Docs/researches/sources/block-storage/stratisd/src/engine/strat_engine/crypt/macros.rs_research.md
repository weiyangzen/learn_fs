# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/macros.rs

Read status: complete, 17 lines.

## Purpose

Defines one local macro, `log_on_failure!`, used by crypt code to log failed operations while preserving normal `?` error propagation.

## Macro Behavior

`log_on_failure!($op, $fmt, ...)`:

1. Evaluates `$op`.
2. If the result is `Err`, logs a warning using the provided format plus `; failed with error: {}`.
3. Applies `result?`, so success unwraps and failure returns from the caller.

## Role

This macro keeps cryptsetup-related operations concise while ensuring failures include contextual warnings before bubbling up.
