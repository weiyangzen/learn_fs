# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-gf8.h

## Purpose

`ec-gf8.h` is the public declaration point for the GF(2^8) precomputed multiplication table implemented in `ec-gf8.c`. It exposes `ec_gf8_mul[]` to the erasure-coding Galois-field implementation while hiding the 256 static descriptor objects that back the table.

## Important APIs, Types, and Data

- The include guard is `__EC_GF8_H__`.
- `#include "ec-galois.h"` supplies the `ec_gf_mul_t` type through the EC Galois/type headers.
- `extern ec_gf_mul_t *ec_gf8_mul[];` declares the exported array of multiplication descriptors. Each slot is expected to correspond to one GF(8) coefficient value.

The header does not define functions, structs, macros, or inline behavior of its own. Its only API is the exported table symbol.

## Control Flow

There is no runtime control flow in the header. Its compile-time role is to make `ec_gf8_mul[]` visible to consumers, especially `ec-galois.c`, where `ec_gf_prepare()` selects this table for 8-bit fields. The table is then consumed by `ec-code.c` through the `gf->table` pointer stored in the prepared GF context.

## State and Persistence Behavior

The header owns no state. It declares a process-global table defined elsewhere. The declaration is not `const`, so consumers receive mutable pointer types even though the table is intended to be static read-only arithmetic metadata. The header performs no persistence, allocation, cleanup, or I/O.

## Dependencies and Integration Points

Direct dependency:

- `ec-galois.h`, which includes the type declarations needed for `ec_gf_mul_t`.

Primary integration points:

- `ec-gf8.c` defines the symbol declared here.
- `ec-galois.c` uses the declaration to assign `gf->table = ec_gf8_mul` for `bits == 8`.
- The broader EC matrix and generated-code pipeline reaches this table indirectly through `ec_gf_t.table`.

This header is deliberately narrow: it prevents most of the large generated table from leaking into other translation units while still letting the GF setup code bind the implementation.

## Risks and Edge Cases

- The array length is implicit. The header does not encode that the table must have 256 slots, so consumers rely on the GF(8) size contract and the implementation file's ordering.
- The non-`const` declaration weakens the intended immutability of the table.
- Because it includes `ec-galois.h` instead of a smaller forward-declaration-only header, changes in Galois declarations can trigger rebuilds of users of this header.
- Any mismatch between this declaration and `ec-gf8.c` would surface as a compile or link failure, but semantic mismatches such as wrong slot ordering are outside the header's protection.

## Test Signals

Useful signals for this header are mostly compile/link and integration based:

- Build `ec-galois.c` and `ec-gf8.c` together to confirm the exported symbol type matches the declaration.
- Link EC translator binaries/tests to ensure exactly one definition of `ec_gf8_mul[]` is provided.
- Run GF preparation tests with `bits == 8` to confirm `ec_gf_prepare()` can bind the table through this header and reject unsupported field widths.
- Pair with table-structure and arithmetic tests from `ec-gf8.c`, since this header's main risk is exposing a large generated data contract without a length or const qualifier.
