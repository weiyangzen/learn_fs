# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__ffz.h

## Purpose

This header defines `ffz(x)` as the first zero-bit counterpart to `__ffs`.

## APIs, State, and Dependencies

`ffz(x)` expands to `__ffs(~(x))`. It has no state and relies on `__ffs` already being available through the generic bitops include order. Like `__ffs`, it is undefined when no matching bit exists, so all-ones inputs must be checked by callers.

## Risks and Test Signals

Incorrect include order or all-ones inputs are the main hazards. Tests should exercise `find_first_zero_bit` and `find_next_zero_bit`, which are typical higher-level consumers that bound the search size before using `ffz`.
