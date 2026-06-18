# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-galois.h

## Purpose

`ec-galois.h` is the public header for GlusterFS EC finite-field arithmetic. It declares the constructor/destructor for an `ec_gf_t` field context and the basic operations needed by EC matrix and code generation.

The header intentionally exposes only functions, not the layout of `ec_gf_t`; the concrete struct is defined in `ec-types.h`. That keeps callers dependent on the field API while allowing implementation details such as log/pow tables and multiplication recipe tables to live elsewhere.

## Important APIs And Types

- Includes `<inttypes.h>` for fixed-width integer declarations.
- Includes `ec-types.h`, which forward declares `ec_gf_t` and defines the backing finite-field structs later in that header.
- Declares `ec_gf_prepare(uint32_t bits, uint32_t mod)` to allocate and initialize a field context.
- Declares `ec_gf_destroy(ec_gf_t *gf)` to release the context.
- Declares `ec_gf_add`, `ec_gf_mul`, `ec_gf_div`, and `ec_gf_exp` for arithmetic on field elements represented as `uint32_t`.

## Control Flow And Integration

The header has no executable control flow beyond include guards. Its function declarations are implemented in `ec-galois.c` and consumed by EC method/code-generation files. The major call chain is EC initialization in `ec-method.c`, which prepares a GF context, builds matrices with exponent/division/multiplication, and destroys the context when the method list is torn down.

Callers receive arithmetic results directly as integer field elements. The implementation uses `gf->size` as an invalid-result sentinel, so callers that perform division, exponentiation, or custom input handling should check for values outside the valid byte range.

## State And Persistence Behavior

This header owns no state and persists nothing. Its API implies in-memory ownership: callers that successfully obtain an `ec_gf_t *` from `ec_gf_prepare` must later call `ec_gf_destroy`.

## Dependencies

The header depends on `ec-types.h` for the `ec_gf_t` type and on standard fixed-width integer types. It is included by EC arithmetic users such as `ec-method.c` and by any component that needs finite-field operations independent of raw FOP dispatch.

## Risks And Edge Cases

- The API does not document error-pointer returns or the arithmetic sentinel, but the implementation uses both. Callers need implementation knowledge or surrounding EC conventions to handle errors safely.
- `ec_gf_destroy` takes a raw pointer and does not advertise NULL safety.
- Element values are `uint32_t` even though the supported implementation is GF(256). Passing values outside the field range is possible and must be handled by the implementation.
- The header does not expose supported field widths; as of the paired implementation, only `bits == 8` is accepted.

## Test Signals

Header-level verification is mostly compile/link coverage: files including this header should compile without needing the internals of `struct _ec_gf`; implementation tests should verify constructor error returns, arithmetic correctness, and destructor ownership. API users should have tests that reject or handle sentinel arithmetic results rather than accidentally treating `256` as a valid byte coefficient.
