# sources/distributed-fs/ceph-client/include/linux/prime_numbers.h

Purpose: declares generic prime-number helpers used by kernel code that needs prime table sizing, hash bucket choices, or arithmetic iteration.

Important APIs and types: `is_prime_number()` tests primality, `next_prime_number()` advances to the next prime at or after a seed, and `for_each_prime_number()` / `for_each_prime_number_from()` macros iterate primes up to a caller-provided maximum.

Control flow: iteration initializes `prime` from either `2` or the supplied `from`, then repeatedly calls `next_prime_number(prime)` until `prime > max`. The comments explicitly require `max < ULONG_MAX` and, for the `_from` form, `from < max` so iteration terminates.

State and persistence: no public state is defined here. Any implementation tables or caches live in the corresponding source file and are not exposed through this header.

Dependencies and integration points: depends only on `linux/types.h`. It is a small math helper for generic kernel subsystems and should remain independent of allocator or architecture state.

Risks and test signals: risks include infinite loops when callers pass boundary values, overflow near `ULONG_MAX`, and mismatch between primality and next-prime behavior. Test small primes/composites, `0`/`1`/`2`, upper-bound iteration termination, and word-size differences on 32-bit and 64-bit builds.
