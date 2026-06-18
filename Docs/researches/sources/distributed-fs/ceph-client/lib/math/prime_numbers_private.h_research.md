# sources/distributed-fs/ceph-client/lib/math/prime_numbers_private.h

Purpose: Private header for prime-number internals and KUnit-only hooks.

Important APIs/types/functions: Defines `struct primes` with `rcu_head`, `last`, `sz`, and flexible bitmap array. Under `CONFIG_PRIME_NUMBERS_KUNIT_TEST`, declares callback type `primes_fn`, `with_primes()`, and `slow_is_prime_number()`.

Control flow: Header-only declarations; no runtime flow.

State and persistence: Describes the RCU-managed bitmap object owned by `prime_numbers.c`.

Dependencies/integration: Included by implementation and KUnit test.

Risks: Internal layout is coupled tightly to bitmap allocation size; tests must not retain RCU pointers from callbacks.

Test signals: Enables white-box KUnit access to slow reference and cached bitmap.
