# subset-b-006102 Research

Grouped research for Ceph-client kernel library files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/maple_tree.c -->
# sources/distributed-fs/ceph-client/lib/maple_tree.c

Purpose: Implements the Linux Maple Tree, a range-aware B-tree-like container used for sparse index/range storage with RCU-friendly readers and write-side replacement/rebalancing. It supports ordinary lookup/store/insert/erase, range allocation, cyclic allocation, duplication, destruction, traversal, and debug validation/dumping.

Important APIs and types: Public exports include `mas_walk`, `mas_store`, `mas_store_gfp`, `mas_store_prealloc`, `mas_preallocate`, `mas_next`, `mas_prev`, `mas_find`, `mas_find_rev`, `mas_empty_area`, `mas_empty_area_rev`, `mas_erase`, `mas_nomem`, `mtree_load`, `mtree_store_range`, `mtree_insert_range`, `mtree_alloc_range`, `mtree_alloc_cyclic`, `mtree_alloc_rrange`, `mtree_erase`, `mtree_dup`, `mtree_destroy`, `mt_find`, and `mt_find_after`. Core state comes from `struct maple_tree`, `struct ma_state`, `struct ma_wr_state`, `struct maple_node`, encoded `struct maple_enode`, and transient `struct maple_copy`.

Control flow: Reads start with `mas_start()` and descend through pivot/slot arrays via `mtree_range_walk()` or `mtree_lookup_walk()`, retrying if dead RCU nodes are observed. Writes classify the operation with `mas_wr_store_type()` into exact-fit, append, slot-store, node-store, spanning-store, split, rebalance, root-store, or new-root paths, preallocate nodes, then replace or mutate leaves while maintaining pivots, parent encodings, metadata, and allocation gap summaries. Large range overwrites use `maple_copy` to synthesize one to three destination nodes and ascend until the tree converges or a new root is needed.

State and persistence: State is in-memory only. Tree root, height, flags, encoded parent pointers, node metadata, and optional allocation gaps are maintained under tree locks for writes and read through RCU for lockless readers. Deleted nodes are marked dead by self-parenting and freed immediately or through RCU callbacks. A slab cache `maple_node_cache` is initialized by `maple_tree_init()` with sheaf prefill support.

Dependencies and integration: Depends on `linux/maple_tree.h`, xarray tagging helpers, slab/RCU primitives, tracepoints, barriers, lockdep, and kernel export/module infrastructure. It is a shared kernel data-structure implementation, not Ceph-specific, but Ceph-client source imports it as part of the kernel subtree.

Risks: The highest-risk areas are encoded pointer bit manipulation, RCU memory ordering, node replacement after spanning writes, gap propagation for allocation trees, overflow at `ULONG_MAX`, and `mas_nomem()` lock dropping/retry behavior. Invalid reserved xarray entries and zero/internal values require caller discipline. Debug builds validate parent slots, pivots, gaps, null adjacency, and minimum occupancy.

Test signals: In-file debug-only exports `mt_validate`, `mt_dump`, `mas_dump`, and allocation counters support maple-tree self-tests. Runtime tracepoints expose read/write operations. Correctness is generally covered by upstream Maple Tree tests and VM users that exercise range allocation and iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/maple_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/Kconfig -->
# sources/distributed-fs/ceph-client/lib/math/Kconfig

Purpose: Declares optional math-library Kconfig symbols for CORDIC, polynomial evaluation, prime number generation, and rational approximation.

Important APIs/types/functions: Defines `CONFIG_CORDIC` as a tristate visible option with help text, `CONFIG_PRIME_NUMBERS` as a visible test-support generator, and hidden tristates `CONFIG_POLYNOMIAL` and `CONFIG_RATIONAL`.

Control flow: Build-time only. Selected symbols drive `lib/math/Makefile` object inclusion and whether modules or built-ins are produced.

State and persistence: No runtime state. The selected configuration persists in the kernel build `.config`.

Dependencies/integration: Integrates with Kbuild and the math source files in the same directory.

Risks: Hidden symbols rely on users or drivers selecting them. Misconfiguration can omit helpers needed by dependent drivers.

Test signals: KUnit tests are controlled by separate test symbols in the tests Makefile; this Kconfig fragment itself has no tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/Makefile -->
# sources/distributed-fs/ceph-client/lib/math/Makefile

Purpose: Kbuild object list for core and optional math helpers.

Important APIs/types/functions: Always builds `div64.o`, `gcd.o`, `lcm.o`, `int_log.o`, `int_pow.o`, `int_sqrt.o`, and `reciprocal_div.o`; conditionally builds `cordic.o`, `polynomial.o`, `prime_numbers.o`, `rational.o`, and module tests `test_div64.o`/`test_mul_u64_u64_div_u64.o`; descends into `tests/`.

Control flow: Evaluated by Kbuild during compilation.

State and persistence: No runtime state.

Dependencies/integration: Connects Kconfig symbols to implementation objects and KUnit test subdirectory.

Risks: Wrong object selection can create missing symbols or unnecessary modules.

Test signals: Includes `obj-y += tests/`, allowing the nested KUnit Makefile to attach configured test objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/cordic.c -->
# sources/distributed-fs/ceph-client/lib/math/cordic.c

Purpose: Provides a fixed-point CORDIC implementation that converts an angle in degrees to I/Q coordinates.

Important APIs/types/functions: Exports `cordic_calc_iq(s32 theta)`, returning `struct cordic_iq`. Uses `arctan_table`, `CORDIC_FIXED`, `CORDIC_FLOAT`, `CORDIC_ANGLE_GEN`, and `CORDIC_NUM_ITER` from `linux/cordic.h`.

Control flow: Normalizes input angle into the -180..180 degree fixed-point range, reflects angles outside +/-90 degrees with a sign flip, then runs iterative shift-add CORDIC rotations based on whether the accumulated angle is below or above the target.

State and persistence: Stateless; all state is local stack math.

Dependencies/integration: Optional module from `CONFIG_CORDIC`, exported for drivers needing fixed-point trigonometric coordinates.

Risks: Accuracy depends on fixed-point scaling and table length. Boundary behavior around modulo normalization and +/-90 degree reflection is sensitive.

Test signals: No local KUnit file in this subset; consumers or generic math tests must validate known angles and quadrants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/cordic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/div64.c -->
# sources/distributed-fs/ceph-client/lib/math/div64.c

Purpose: Supplies generic 64-bit division helpers, mostly for 32-bit architectures and for product-plus-add divided by a 64-bit divisor.

Important APIs/types/functions: Exports weak `__div64_32`, `div_s64_rem`, `div64_u64_rem`, `div64_u64`, `div64_s64`, `iter_div_u64_rem`, and `mul_u64_add_u64_div_u64` when not provided by architecture headers/macros. Internal helpers split multiplication into 32-bit or 16-bit chunks unless native `u128` is available.

Control flow: 32-bit fallback division normalizes high halves and performs shift/subtract long division. `div64_u64*` estimates quotient by shifting divisor/dividend and corrects by one if needed. `mul_u64_add_u64_div_u64()` forms a 128-bit numerator, detects overflow/zero-divisor exceptional cases, normalizes divisor, then performs digit-wise long division.

State and persistence: Stateless arithmetic.

Dependencies/integration: Depends on `asm/div64.h` callers, `linux/math64.h`, bit operations, min/max, and arch override mechanisms.

Risks: Division by zero intentionally triggers a runtime exception in one overflow path. Edge cases include high-half overflow, divisor near 2^64, quotient saturation, and architecture-dependent code paths.

Test signals: Covered by `test_div64.c` and `test_mul_u64_u64_div_u64.c`; also widely exercised by kernel math users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/div64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/gcd.c -->
# sources/distributed-fs/ceph-client/lib/math/gcd.c

Purpose: Implements greatest common divisor for unsigned longs using binary GCD variants.

Important APIs/types/functions: Exports `gcd(unsigned long a, unsigned long b)` and defines static key `efficient_ffs_key`. Uses `binary_gcd()` when efficient `__ffs()` support is available.

Control flow: Handles zero inputs by returning `a | b`. On efficient-ffs systems, strips powers of two via `__ffs`, subtracts smaller from larger, and restores common factors. Otherwise uses an even/odd loop optimized for CPUs without fast bit-scan.

State and persistence: Stateless except for the global static branch controlling algorithm selection.

Dependencies/integration: Used by `lcm.c`, rational/math users, and exported GPL-only.

Risks: Performance depends on architecture configuration; arithmetic itself is bounded but assumes unsigned-long semantics.

Test signals: `tests/gcd_kunit.c` covers normal, reversed, coprime, zero, identical, and `ULONG_MAX` cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/gcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/int_log.c -->
# sources/distributed-fs/ceph-client/lib/math/int_log.c

Purpose: Provides fixed-point base-2 and base-10 logarithms for 32-bit inputs.

Important APIs/types/functions: Exports `intlog2(u32 value)` and `intlog10(u32 value)`. Uses a 256-entry log table and returns `log(value) * 2^24`.

Control flow: `intlog2()` rejects zero with `WARN_ON`, finds the most significant bit, normalizes the significand, indexes the lookup table, interpolates within the table bucket, and combines integer/fractional parts. `intlog10()` multiplies the base-2 result by fixed-point `log10(2)`.

State and persistence: Stateless, read-only lookup table.

Dependencies/integration: Depends on bitops and exported for fixed-point kernel consumers.

Risks: Zero returns 0 after warning although logarithm is undefined. Results are approximate and tests account for table error.

Test signals: `tests/int_log_kunit.c` covers zero, powers, representative values, and `U32_MAX` for both bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/int_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/int_pow.c -->
# sources/distributed-fs/ceph-client/lib/math/int_pow.c

Purpose: Computes unsigned integer exponentiation.

Important APIs/types/functions: Exports GPL-only `int_pow(u64 base, unsigned int exp)`.

Control flow: Standard exponentiation by squaring: multiply result when the current exponent bit is set, shift exponent right, square base each iteration.

State and persistence: Stateless.

Dependencies/integration: Included in core math object list for kernel users needing simple powers.

Risks: Silent `u64` overflow is expected C unsigned arithmetic; no saturation or error reporting.

Test signals: `tests/int_pow_kunit.c` covers exponent zero/one, base zero/one, small powers, `U64_MAX`, and a high power boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/int_pow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/int_sqrt.c -->
# sources/distributed-fs/ceph-client/lib/math/int_sqrt.c

Purpose: Computes floor square root for unsigned long, and on 32-bit builds also for 64-bit input.

Important APIs/types/functions: Exports `int_sqrt(unsigned long x)` and conditionally `int_sqrt64(u64 x)`.

Control flow: Uses the shift-and-subtract algorithm. It selects the highest even power-of-four bit at or below the input, then iteratively tests/subtracts and shifts to build the root.

State and persistence: Stateless.

Dependencies/integration: Used by prime-number trial division and other math callers.

Risks: Correctness around word-size boundaries and `ULONG_MAX` depends on bit scanning and type widths.

Test signals: `tests/int_sqrt_kunit.c` covers zero/one, perfect and non-perfect squares, neighbors around powers, and 32-bit maximum inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/int_sqrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/lcm.c -->
# sources/distributed-fs/ceph-client/lib/math/lcm.c

Purpose: Implements least common multiple helpers.

Important APIs/types/functions: Exports GPL-only `lcm(a, b)` and `lcm_not_zero(a, b)`.

Control flow: `lcm()` returns `(a / gcd(a,b)) * b` when both inputs are nonzero, else 0. `lcm_not_zero()` returns the LCM if nonzero, otherwise the nonzero input.

State and persistence: Stateless.

Dependencies/integration: Depends on `gcd()` and exported for drivers/subsystems needing period/frequency composition.

Risks: Multiplication may overflow unsigned long silently.

Test signals: No dedicated KUnit file in this subset; indirectly relies on `gcd` coverage and consumer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/lcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/polynomial.c -->
# sources/distributed-fs/ceph-client/lib/math/polynomial.c

Purpose: Evaluates integer polynomials with redistributed factors to preserve precision and avoid overflow.

Important APIs/types/functions: Exports GPL-only `polynomial_calc(const struct polynomial *poly, long data)`, consuming `struct polynomial` and `struct polynomial_term` from `linux/polynomial.h`.

Control flow: Iterates terms until a degree-zero term is processed, repeatedly applies `mult_frac(tmp, data, divider)` per degree, divides by each term’s leftover divider, accumulates, then applies `total_divider` or 1 if zero.

State and persistence: Stateless; polynomial descriptors are caller-owned constants/data.

Dependencies/integration: Optional `CONFIG_POLYNOMIAL` object for sensor/driver calibration formulas.

Risks: Caller must supply terms in descending degree ending with degree 0 and choose factors that prevent overflow; no validation guards malformed descriptors.

Test signals: No local KUnit in this subset; comments include a temperature/PVT conversion example useful for consumer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/polynomial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/prime_numbers.c -->
# sources/distributed-fs/ceph-client/lib/math/prime_numbers.c

Purpose: Provides prime lookup/generation helpers backed by an expandable bitmap sieve with trial-division fallback.

Important APIs/types/functions: Exports `next_prime_number()` and `is_prime_number()`. When KUnit is enabled, also exports `with_primes()` and `slow_is_prime_number()`. Internal state is `struct primes`, `small_primes`, RCU pointer `primes`, and mutex `lock`.

Control flow: Starts with a static bitmap of small primes. Queries read the current sieve under RCU. If the requested value exceeds cached coverage, `expand_to_next_prime()` allocates a larger bitmap, copies prior bits, clears multiples with a Sieve of Eratosthenes, publishes it with RCU, and frees the previous dynamic bitmap after grace period. Allocation failure falls back to slow trial division using `int_sqrt()`.

State and persistence: Maintains process-lifetime in-memory prime bitmap; module exit resets/free dynamic bitmap.

Dependencies/integration: Optional `CONFIG_PRIME_NUMBERS`, uses bitmap APIs, mutex, RCU, slab, and `int_sqrt`.

Risks: Memory allocation may fail for very large values; `ULONG_MAX` acts as a sentinel in slow search. Expansion races are serialized, but correctness depends on RCU callback lifetime.

Test signals: `tests/prime_numbers_kunit.c` compares fast and slow primality plus next-prime sequencing up to 65536 and dumps final cache state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/prime_numbers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/prime_numbers_private.h -->
# sources/distributed-fs/ceph-client/lib/math/prime_numbers_private.h

Purpose: Private header for prime-number internals and KUnit-only hooks.

Important APIs/types/functions: Defines `struct primes` with `rcu_head`, `last`, `sz`, and flexible bitmap array. Under `CONFIG_PRIME_NUMBERS_KUNIT_TEST`, declares callback type `primes_fn`, `with_primes()`, and `slow_is_prime_number()`.

Control flow: Header-only declarations; no runtime flow.

State and persistence: Describes the RCU-managed bitmap object owned by `prime_numbers.c`.

Dependencies/integration: Included by implementation and KUnit test.

Risks: Internal layout is coupled tightly to bitmap allocation size; tests must not retain RCU pointers from callbacks.

Test signals: Enables white-box KUnit access to slow reference and cached bitmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/prime_numbers_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/rational.c -->
# sources/distributed-fs/ceph-client/lib/math/rational.c

Purpose: Computes the best bounded rational approximation of an input fraction.

Important APIs/types/functions: Exports `rational_best_approximation(given_numerator, given_denominator, max_numerator, max_denominator, best_numerator, best_denominator)`.

Control flow: Uses continued fractions. It repeatedly derives the next Euclidean quotient, builds convergents, and when the next convergent exceeds numerator or denominator limits, chooses between the previous convergent and a final semi-convergent based on closeness.

State and persistence: Stateless; outputs are written through caller pointers.

Dependencies/integration: Optional `CONFIG_RATIONAL`, used by drivers configuring clocks/PLLs or fixed-ratio hardware registers.

Risks: Assumes nonzero denominator for meaningful input; multiplication in convergent updates can overflow unsigned long for extreme values.

Test signals: `tests/rational_kunit.c` covers exact, bounded, near-zero, numerator-limited, denominator-limited, convergent, and semi-convergent cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/rational.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/reciprocal_div.c -->
# sources/distributed-fs/ceph-client/lib/math/reciprocal_div.c

Purpose: Computes reciprocal multiplier descriptors used to replace repeated integer division by multiply/shift sequences.

Important APIs/types/functions: Exports `reciprocal_value(u32 d)` and `reciprocal_value_adv(u32 d, u8 prec)`, returning `struct reciprocal_value` and `struct reciprocal_value_adv`.

Control flow: Basic path computes ceil log2, multiplier `m`, and two shifts from the divisor. Advanced path computes low/high multiplier bounds at requested precision, shifts them down until bounds would collapse, and records whether the multiplier is wider than 32 bits.

State and persistence: Stateless.

Dependencies/integration: Core math object used by networking and performance-sensitive code that precomputes division constants.

Risks: Divisor assumptions are enforced mostly by callers; advanced path warns for `l == 32` because `1ULL << (32 + l)` would overflow.

Test signals: No local KUnit here; correctness is normally tested by reciprocal-div users and header inline division helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/reciprocal_div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/test_div64.c -->
# sources/distributed-fs/ceph-client/lib/math/test_div64.c

Purpose: Loadable test module for `do_div()` 64-bit dividend / 32-bit divisor quotient and remainder behavior.

Important APIs/types/functions: Contains fixed dividend/divisor vectors, expected quotient/remainder matrix, `test_div64_one()` macro, `test_div64()`, and module init/exit.

Control flow: For each dividend it tests every divisor both as compile-time constants and as variables, so constant-optimized and generic `do_div` paths are exercised. Init repeats the full matrix `TEST_DIV64_N_ITER` times and prints elapsed time.

State and persistence: No persistent state; results are emitted through kernel logging.

Dependencies/integration: Built by `CONFIG_TEST_DIV64`, depends on `asm/div64.h`, timekeeping, module init.

Risks: Stops at first failure and still returns 0 from init, so logs are the main failure signal.

Test signals: The file itself is the test signal, with broad edge vectors including near-maximum dividends and divisors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/test_div64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/test_mul_u64_u64_div_u64.c -->
# sources/distributed-fs/ceph-client/lib/math/test_mul_u64_u64_div_u64.c

Purpose: Loadable test module for `mul_u64_u64_div_u64()` and rounded product-plus-add division behavior.

Important APIs/types/functions: Defines `test_params`, vector table, `test_run()`, test wrappers, and includes `div64.c` with test macro overrides to exercise alternate implementations.

Control flow: Iterates edge/random triples `(a,b,d)`, checks floor result and rounded-up variant using `d - 1` addition, logs mismatches and timing. On 64-bit long builds, also tests a forced 32-bit division path.

State and persistence: No persistent state; only module-load log output and error count.

Dependencies/integration: Built by `CONFIG_TEST_MULDIV64`, includes math64 APIs and test-local inclusion of `div64.c`.

Risks: Vector table must stay synchronized with helper semantics; module init log must be inspected for failures.

Test signals: Explicit expected vectors cover overflow-prone high-bit products, divisors near powers of two, and random values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/test_mul_u64_u64_div_u64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/Makefile -->
# sources/distributed-fs/ceph-client/lib/math/tests/Makefile

Purpose: Kbuild list for math KUnit test objects.

Important APIs/types/functions: Maps `CONFIG_GCD_KUNIT_TEST`, `CONFIG_INT_LOG_KUNIT_TEST`, `CONFIG_INT_POW_KUNIT_TEST`, `CONFIG_INT_SQRT_KUNIT_TEST`, `CONFIG_PRIME_NUMBERS_KUNIT_TEST`, and `CONFIG_RATIONAL_KUNIT_TEST` to corresponding objects.

Control flow: Build-time only.

State and persistence: No runtime state.

Dependencies/integration: Integrates the KUnit suites with `lib/math/Makefile`.

Risks: Tests are omitted unless the matching Kconfig symbols are enabled.

Test signals: The presence of each object line is the activation path for the corresponding suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/gcd_kunit.c -->
# sources/distributed-fs/ceph-client/lib/math/tests/gcd_kunit.c

Purpose: Parameterized KUnit tests for `gcd()`.

Important APIs/types/functions: Defines `struct test_case_params`, `params`, `KUNIT_ARRAY_PARAM(gcd, ...)`, `gcd_test()`, and suite `math-gcd`.

Control flow: KUnit invokes `gcd_test()` once per parameter, comparing expected result to `gcd(val1, val2)`.

State and persistence: Stateless test data.

Dependencies/integration: Depends on KUnit and `linux/gcd.h`.

Risks: Covers representative values but not exhaustive performance/static-key behavior.

Test signals: Failures identify the named parameter description.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/gcd_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/int_log_kunit.c -->
# sources/distributed-fs/ceph-client/lib/math/tests/int_log_kunit.c

Purpose: Parameterized KUnit tests for fixed-point `intlog2()` and `intlog10()`.

Important APIs/types/functions: Defines separate parameter arrays for base-2 and base-10 outputs, generator macros, `intlog2_test()`, `intlog10_test()`, and suite `math-int_log`.

Control flow: Each KUnit case compares the helper output to precomputed fixed-point values that include known approximation error.

State and persistence: Stateless test vectors.

Dependencies/integration: Uses `linux/int_log.h` and KUnit.

Risks: Zero-input cases expect 0 despite implementation warning, so warning behavior should be considered when running.

Test signals: Covers powers, non-powers, zero, and `U32_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/int_log_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/int_pow_kunit.c -->
# sources/distributed-fs/ceph-client/lib/math/tests/int_pow_kunit.c

Purpose: Parameterized KUnit tests for `int_pow()`.

Important APIs/types/functions: Defines `struct test_case_params`, vector table, `KUNIT_ARRAY_PARAM(int_pow, ...)`, `int_pow_test()`, and suite `math-int_pow`.

Control flow: Runs one assertion per base/exponent vector.

State and persistence: Stateless test data.

Dependencies/integration: Uses `linux/math.h` and KUnit.

Risks: Tests document unsigned overflow behavior only lightly; no randomized coverage.

Test signals: Covers exponent zero/one, base zero/one, common powers, max base passthrough, and `2^63`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/int_pow_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/int_sqrt_kunit.c -->
# sources/distributed-fs/ceph-client/lib/math/tests/int_sqrt_kunit.c

Purpose: Parameterized KUnit tests for `int_sqrt()`.

Important APIs/types/functions: Defines input/expected vectors, parameter generator, `int_sqrt_test()`, and suite `math-int_sqrt`.

Control flow: KUnit compares `int_sqrt(x)` to expected floor roots for every vector.

State and persistence: Stateless.

Dependencies/integration: Uses KUnit and `linux/math.h`.

Risks: The `ULONG_MAX for 32-bit` vector is architecture-sensitive in interpretation; 64-bit-specific extremes are not covered here.

Test signals: Covers zero/one, perfect squares, neighbors around squares, and large 32-bit-range values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/int_sqrt_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/prime_numbers_kunit.c -->
# sources/distributed-fs/ceph-client/lib/math/tests/prime_numbers_kunit.c

Purpose: KUnit white-box test for prime-number helpers.

Important APIs/types/functions: Uses `slow_is_prime_number()`, `is_prime_number()`, `next_prime_number()`, and `with_primes()` from the private test hooks.

Control flow: Iterates values from 2 to 65535, compares slow and fast primality, and for every prime verifies `next_prime_number(last)` returns the current prime. Suite exit dumps cached sieve metadata.

State and persistence: Mutates global prime cache by forcing expansion during tests; cache is module lifetime and RCU-managed.

Dependencies/integration: Requires `CONFIG_PRIME_NUMBERS_KUNIT_TEST`, KUnit, and private header.

Risks: Exercises expansion but not allocation-failure fallback.

Test signals: Assertion messages include `is-prime(x)` and `next-prime(last)` context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/prime_numbers_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/rational_kunit.c -->
# sources/distributed-fs/ceph-client/lib/math/tests/rational_kunit.c

Purpose: Parameterized KUnit tests for bounded rational approximation.

Important APIs/types/functions: Defines `struct rational_test_param`, vector table, generator, `rational_test()`, and suite `rational`.

Control flow: Each parameter calls `rational_best_approximation()` and checks numerator and denominator against expected outputs.

State and persistence: Stateless test data.

Dependencies/integration: Uses KUnit and `linux/rational.h`.

Risks: Covers many continued-fraction edge cases but not overflow extremes.

Test signals: Parameter names distinguish exact, near-zero, convergent, semi-convergent, numerator-limit, and denominator-limit scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/math/tests/rational_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/memcat_p.c -->
# sources/distributed-fs/ceph-client/lib/memcat_p.c

Purpose: Concatenates two NULL-terminated pointer arrays into a newly allocated NULL-terminated array.

Important APIs/types/functions: Exports GPL-only `__memcat_p(void **a, void **b)`.

Control flow: Counts entries in both arrays, allocates `nr + 1` pointer slots, then copies backward from the end of `b` and then `a`, preserving order and the final NULL terminator.

State and persistence: Returns caller-owned heap allocation from `kmalloc_array`; no global state.

Dependencies/integration: Depends on slab allocation and kernel export infrastructure.

Risks: Assumes both inputs are valid NULL-terminated arrays; returns NULL on allocation failure; callers must free the new array.

Test signals: No local tests; good tests would cover empty arrays, allocation failure, and order preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/memcat_p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/memory-notifier-error-inject.c -->
# sources/distributed-fs/ceph-client/lib/memory-notifier-error-inject.c

Purpose: Debug/test module that injects failures into memory hotplug notifier actions.

Important APIs/types/functions: Defines module parameter `priority`, `memory_notifier_err_inject`, `err_inject_init()`, and `err_inject_exit()`.

Control flow: Module init creates a debugfs notifier error-injection directory for memory actions, registers the memory notifier, and cleans debugfs on registration failure. Exit unregisters and removes debugfs recursively.

State and persistence: Maintains a debugfs dentry and notifier registration while module is loaded.

Dependencies/integration: Depends on memory hotplug notifiers, `notifier-error-inject.h`, debugfs infrastructure, and module parameters.

Risks: Intended to force failures; should only be enabled in debug/testing environments. Cleanup must match registration to avoid stale notifiers.

Test signals: Behavior is observed through debugfs knobs and memory hotplug operation return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/memory-notifier-error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/memregion.c -->
# sources/distributed-fs/ceph-client/lib/memregion.c

Purpose: Allocates small integer identifiers for device/performance-differentiated memory regions.

Important APIs/types/functions: Exports `memregion_alloc(gfp_t gfp)` and `memregion_free(int id)`, backed by static `DEFINE_IDA(memregion_ids)`.

Control flow: Allocation delegates to `ida_alloc`; free delegates to `ida_free`.

State and persistence: Global in-memory IDA tracks allocated IDs until freed.

Dependencies/integration: Uses IDA and `linux/memregion.h`, intended for memory-region users needing stable integer handles.

Risks: Caller must free IDs exactly once; allocation can fail according to GFP context.

Test signals: No local tests; IDA behavior is covered elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/memregion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/memweight.c -->
# sources/distributed-fs/ceph-client/lib/memweight.c

Purpose: Counts set bits across an arbitrary byte range.

Important APIs/types/functions: Exports `memweight(const void *ptr, size_t bytes)`.

Control flow: Counts unaligned leading bytes with `hweight8`, processes aligned full words through `bitmap_weight`, then counts trailing bytes individually to preserve big-endian correctness for partial words.

State and persistence: Stateless.

Dependencies/integration: Uses bit/bitmap helpers and `BUG_ON` to guard excessive bitmap length.

Risks: Very large input can trip the `BUG_ON(longs >= INT_MAX / BITS_PER_LONG)` guard; caller must supply valid memory.

Test signals: No local tests; important cases are unaligned buffers, trailing bytes, endian behavior, and large-size guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/memweight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/min_heap.c -->
# sources/distributed-fs/ceph-client/lib/min_heap.c

Purpose: Provides exported out-of-line wrappers for generic min-heap inline helpers.

Important APIs/types/functions: Exports `__min_heap_init`, `__min_heap_peek`, `__min_heap_full`, `__min_heap_sift_down`, `__min_heap_sift_up`, `__min_heapify_all`, `__min_heap_pop`, `__min_heap_pop_push`, `__min_heap_push`, and `__min_heap_del`.

Control flow: Every function delegates directly to the matching `_inline` helper with heap, element size, callbacks, and user args.

State and persistence: Heap state is caller-owned in `min_heap_char` storage.

Dependencies/integration: Depends on `linux/min_heap.h`; exports make heap helpers available to modules even when inline bodies are not sufficient.

Risks: Correctness depends on caller-provided callbacks and element sizes; this file adds no validation beyond inline helper behavior.

Test signals: No local tests; coverage comes from min-heap users and any generic heap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/min_heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/muldi3.c -->
# sources/distributed-fs/ceph-client/lib/muldi3.c

Purpose: Provides `__muldi3` 64-bit multiplication support for toolchains/architectures that need libgcc-style helpers.

Important APIs/types/functions: Exports `__muldi3(long long u, long long v)`. Uses `DWunion`, `umul_ppmm`, and half-word macros to compute partial products.

Control flow: Multiplies low halves to form the base 64-bit product, then adds cross-products of high/low halves into the high word.

State and persistence: Stateless arithmetic.

Dependencies/integration: Depends on `linux/libgcc.h` and kernel export infrastructure; marked `notrace`.

Risks: Type-width assumptions are fixed around `W_TYPE_SIZE 32`; intended for supported compiler/runtime contexts.

Test signals: No local tests; exercised implicitly by builds/runtimes that emit `__muldi3` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/muldi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/net_utils.c -->
# sources/distributed-fs/ceph-client/lib/net_utils.c

Purpose: Parses textual MAC addresses into binary Ethernet addresses.

Important APIs/types/functions: Exports `mac_pton(const char *s, u8 *mac)`.

Control flow: Verifies the string is at least `MAC_ADDR_STR_LEN`, validates two hex digits per byte and colon separators between bytes, then converts nibbles with `hex_to_bin`. The output buffer is not modified until validation succeeds.

State and persistence: Stateless.

Dependencies/integration: Uses Ethernet constants, ctype, string, hex helpers, and exported for networking users.

Risks: Accepts strings with additional trailing characters because it only requires minimum length and validates the MAC prefix. Caller must provide at least `ETH_ALEN` output bytes.

Test signals: No local tests; important cases are malformed separators, non-hex characters, short strings, trailing data, and uppercase/lowercase hex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/net_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/netdev-notifier-error-inject.c -->
# sources/distributed-fs/ceph-client/lib/netdev-notifier-error-inject.c

Purpose: Debug/test module that injects failures into selected netdevice notifier events.

Important APIs/types/functions: Defines module parameter `priority`, `netdev_notifier_err_inject`, `netdev_err_inject_init()`, and `netdev_err_inject_exit()`.

Control flow: Module init creates a `netdev` error-injection debugfs directory, registers a netdevice notifier, and removes debugfs if registration fails. Exit unregisters the notifier and removes debugfs.

State and persistence: Holds notifier registration and debugfs directory for module lifetime.

Dependencies/integration: Depends on netdevice notifier chain, common notifier error-injection helper, debugfs, and module infrastructure.

Risks: Intended to disrupt network device operations for testing; event list includes register, MTU/name changes, pre-up/type/upper changes, and post-init.

Test signals: Testers control injected responses through debugfs and observe netdevice operation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/netdev-notifier-error-inject.c -->
