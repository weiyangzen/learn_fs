# sources/distributed-fs/ceph-client/lib/math/prime_numbers.c

Purpose: Provides prime lookup/generation helpers backed by an expandable bitmap sieve with trial-division fallback.

Important APIs/types/functions: Exports `next_prime_number()` and `is_prime_number()`. When KUnit is enabled, also exports `with_primes()` and `slow_is_prime_number()`. Internal state is `struct primes`, `small_primes`, RCU pointer `primes`, and mutex `lock`.

Control flow: Starts with a static bitmap of small primes. Queries read the current sieve under RCU. If the requested value exceeds cached coverage, `expand_to_next_prime()` allocates a larger bitmap, copies prior bits, clears multiples with a Sieve of Eratosthenes, publishes it with RCU, and frees the previous dynamic bitmap after grace period. Allocation failure falls back to slow trial division using `int_sqrt()`.

State and persistence: Maintains process-lifetime in-memory prime bitmap; module exit resets/free dynamic bitmap.

Dependencies/integration: Optional `CONFIG_PRIME_NUMBERS`, uses bitmap APIs, mutex, RCU, slab, and `int_sqrt`.

Risks: Memory allocation may fail for very large values; `ULONG_MAX` acts as a sentinel in slow search. Expansion races are serialized, but correctness depends on RCU callback lifetime.

Test signals: `tests/prime_numbers_kunit.c` compares fast and slow primality plus next-prime sequencing up to 65536 and dumps final cache state.
