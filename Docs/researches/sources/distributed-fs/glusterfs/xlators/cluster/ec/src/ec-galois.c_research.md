# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-galois.c

## Purpose

`ec-galois.c` implements the finite-field arithmetic support used by GlusterFS EC erasure coding. It builds a `GF(2^8)` context with logarithm and exponent tables, attaches the precomputed byte multiplication operation table from `ec-gf8.h`, and exposes basic field operations for matrix generation and code generation.

This file is deliberately narrow: it does not encode or decode data itself. Instead, it provides reusable field arithmetic to `ec-method.c` and code-building paths such as `ec-code.c` and generated C code helpers. The implementation currently accepts only `bits == 8`, which matches the shipped `ec_gf8_mul` table.

## Important APIs, Types, And Functions

- `ec_gf_prepare(uint32_t bits, uint32_t mod)` is the public constructor. It validates `bits`, defaults `mod` to `0x11d`, allocates the `ec_gf_t`, initializes `log` and `pow` tables, binds `gf->table` to `ec_gf8_mul`, and computes `min_ops`, `max_ops`, and `avg_ops` from the precomputed multiplication recipes.
- `ec_gf_destroy(ec_gf_t *gf)` releases `pow`, `log`, and the `ec_gf_t` allocation. It assumes a valid non-NULL pointer from `ec_gf_prepare`.
- `ec_gf_add(ec_gf_t *gf, uint32_t a, uint32_t b)` implements field addition as XOR. Inputs outside `[0, gf->size)` return `gf->size` as an error sentinel.
- `ec_gf_mul(ec_gf_t *gf, uint32_t a, uint32_t b)` multiplies nonzero operands by adding logarithms and indexing `pow`; zero operands return zero. Out-of-range inputs return the sentinel.
- `ec_gf_div(ec_gf_t *gf, uint32_t a, uint32_t b)` divides by subtracting logarithms via an offset into the duplicated exponent table. Division by zero and out-of-range inputs return the sentinel.
- `ec_gf_exp(ec_gf_t *gf, uint32_t a, uint32_t b)` computes exponentiation with square-and-multiply over `ec_gf_mul`. `0^0` and out-of-range bases return the sentinel.
- Internal helpers `ec_gf_alloc` and `ec_gf_init_tables` encapsulate allocation and table construction. They use Gluster memory APIs (`GF_MALLOC`, `GF_FREE`) and EC error-pointer macros (`EC_ERR`, `EC_IS_ERR`).

The backing type is `struct _ec_gf` in `ec-types.h`: it stores field parameters, operation count statistics, `log`, `pow`, and the `ec_gf_mul_t **table` used by code-generation paths.

## Control Flow

Construction is linear. `ec_gf_prepare` rejects unsupported widths, selects the GF(8) multiplication table, normalizes a zero modulus to `0x11d`, allocates the object and two arrays, calls `ec_gf_init_tables`, and then scans `tbl[i]->ops` until `EC_GF_OP_END` for each nonzero element to collect operation statistics.

`ec_gf_init_tables` seeds `pow[0] = 1`, marks `log[0] = gf->size` as a special non-field logarithm value, and iterates powers of the primitive element by left-shifting the previous power. When the shifted value exceeds the field size, it reduces by XORing the modulus. Each generated value is written twice into `pow`/`log` at the base index and at an offset of `gf->size - 1`, avoiding explicit modulo operations in multiplication/division.

The arithmetic functions are intentionally branch-light and table-driven. Add is XOR, multiply and divide handle zero first, and exponentiation delegates to multiply so input validation and field semantics remain centralized.

## State And Persistence Behavior

State is in-memory only. `ec_gf_prepare` creates an `ec_gf_t` whose lifetime is owned by callers such as the EC method list initialization path in `ec-method.c`. No persistent files, xattrs, dictionaries, or on-disk metadata are changed.

The `log` and `pow` arrays are mutable after allocation but treated as read-only lookup tables once initialized. The `ec_gf8_mul` table is externally provided static data. `min_ops`, `max_ops`, and `avg_ops` are derived diagnostics/cost hints for multiplication recipes, not persistent counters.

## Dependencies And Integration Points

- Includes `ec-mem-types.h` for memory type identifiers, `ec-gf8.h` for the GF(8) multiplication table, and `ec-helpers.h` for EC error-pointer helpers.
- Uses `ec-types.h` indirectly through included headers for `ec_gf_t`, `ec_gf_mul_t`, and `ec_gf_op_t`.
- Integrated by `ec-method.c`, which calls `ec_gf_prepare(EC_GF_BITS, EC_GF_MOD)` and uses `ec_gf_exp`, `ec_gf_div`, and `ec_gf_mul` to build erasure-code matrices. It later calls `ec_gf_destroy`.
- Integrated by code generation paths such as `ec-code.c`, which consult field division/multiplication results and `gf->table` to generate optimized XOR/copy operation sequences.

## Risks And Edge Cases

- Only 8-bit fields are supported. Any future width requires both table data and constructor logic updates; passing another width returns an `EC_ERR(EINVAL)` pointer.
- Error signaling for arithmetic uses `gf->size`, not an errno. Callers must treat any result equal to `gf->size` as invalid because valid values are `0..gf->size - 1`.
- `ec_gf_destroy` does not tolerate NULL defensively. Calling it with NULL would pass NULL into field dereferences before freeing.
- The duplicated table allocation uses `gf->size * 2 - 1` entries. This matches the maximum index used by `log[a] + log[b]` and division offsets, but any table-construction change must preserve that invariant.
- `ec_gf_init_tables` assumes the modulus is suitable for the chosen field. The default is valid for GF(256); arbitrary nonzero `mod` values are not validated for irreducibility.
- `gf->avg_ops /= gf->size` divides by 256 while summing only nonzero elements. This is a cost statistic, not correctness-sensitive, but consumers should not interpret it as the average over only nonzero multipliers.

## Test Signals

Useful tests should assert: unsupported `bits` returns an EC error pointer; default modulus produces a 256-element field; addition is XOR; multiplication/division round trips for all nonzero operands; division by zero and out-of-range operands return `gf->size`; `ec_gf_exp(gf, a, 0) == 1` for valid nonzero `a`; `ec_gf_exp(gf, 0, 0)` returns the sentinel; and constructor/destructor run cleanly under leak/error-injection tests for allocation failures.

Integration tests should cover EC matrix generation in `ec-method.c`, because incorrect table generation can surface as bad reconstruction coefficients rather than local crashes.
