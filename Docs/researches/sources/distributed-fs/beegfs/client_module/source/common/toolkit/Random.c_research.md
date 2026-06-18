# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Random.c

## Purpose
Wraps Linux kernel random bytes for simple integer and bounded-range random values.

## Important APIs and control flow
`Random_getNextInt` fills an `int` using `get_random_bytes` and converts negative values to non-negative by bitwise complement, avoiding `-INT_MIN` overflow. `Random_getNextInRange` applies modulo reduction over an inclusive `[min, max]` interval and adds `min`.

## State, dependencies, integration
No persistent state is stored. It depends on kernel RNG APIs and is used by `InternodeSyncer` to jitter management heartbeat retry waits.

## Risks and test signals
`Random_getNextInRange` assumes `max >= min`; invalid ranges can divide by zero or wrap. Modulo reduction introduces bias, acceptable for timing jitter but not cryptographic selection. Tests should cover boundary values and negative min ranges if callers rely on them.
