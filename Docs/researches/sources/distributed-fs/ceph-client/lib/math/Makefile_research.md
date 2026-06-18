# sources/distributed-fs/ceph-client/lib/math/Makefile

Purpose: Kbuild object list for core and optional math helpers.

Important APIs/types/functions: Always builds `div64.o`, `gcd.o`, `lcm.o`, `int_log.o`, `int_pow.o`, `int_sqrt.o`, and `reciprocal_div.o`; conditionally builds `cordic.o`, `polynomial.o`, `prime_numbers.o`, `rational.o`, and module tests `test_div64.o`/`test_mul_u64_u64_div_u64.o`; descends into `tests/`.

Control flow: Evaluated by Kbuild during compilation.

State and persistence: No runtime state.

Dependencies/integration: Connects Kconfig symbols to implementation objects and KUnit test subdirectory.

Risks: Wrong object selection can create missing symbols or unnecessary modules.

Test signals: Includes `obj-y += tests/`, allowing the nested KUnit Makefile to attach configured test objects.
