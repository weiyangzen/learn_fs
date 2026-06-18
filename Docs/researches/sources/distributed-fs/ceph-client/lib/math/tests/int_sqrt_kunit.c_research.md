# sources/distributed-fs/ceph-client/lib/math/tests/int_sqrt_kunit.c

Purpose: Parameterized KUnit tests for `int_sqrt()`.

Important APIs/types/functions: Defines input/expected vectors, parameter generator, `int_sqrt_test()`, and suite `math-int_sqrt`.

Control flow: KUnit compares `int_sqrt(x)` to expected floor roots for every vector.

State and persistence: Stateless.

Dependencies/integration: Uses KUnit and `linux/math.h`.

Risks: The `ULONG_MAX for 32-bit` vector is architecture-sensitive in interpretation; 64-bit-specific extremes are not covered here.

Test signals: Covers zero/one, perfect squares, neighbors around squares, and large 32-bit-range values.
