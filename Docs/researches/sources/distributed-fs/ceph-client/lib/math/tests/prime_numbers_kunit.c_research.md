# sources/distributed-fs/ceph-client/lib/math/tests/prime_numbers_kunit.c

Purpose: KUnit white-box test for prime-number helpers.

Important APIs/types/functions: Uses `slow_is_prime_number()`, `is_prime_number()`, `next_prime_number()`, and `with_primes()` from the private test hooks.

Control flow: Iterates values from 2 to 65535, compares slow and fast primality, and for every prime verifies `next_prime_number(last)` returns the current prime. Suite exit dumps cached sieve metadata.

State and persistence: Mutates global prime cache by forcing expansion during tests; cache is module lifetime and RCU-managed.

Dependencies/integration: Requires `CONFIG_PRIME_NUMBERS_KUNIT_TEST`, KUnit, and private header.

Risks: Exercises expansion but not allocation-failure fallback.

Test signals: Assertion messages include `is-prime(x)` and `next-prime(last)` context.
