# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-avx.h

## Purpose
Declares the exported AVX EC code generator descriptor for consumers that select among EC code-generation backends.

## Important APIs and Types
- Include guard `__EC_CODE_AVX_H__`.
- Includes `ec-code.h` for `ec_code_gen_t`.
- `extern ec_code_gen_t ec_code_gen_avx`: descriptor defined in `ec-code-avx.c`.

## Control Flow
There is no runtime control flow in the header. Including code can reference `ec_code_gen_avx` when the AVX backend is compiled.

## State and Persistence
No state is owned here. The extern points to a global descriptor in the implementation file.

## Dependencies and Integration Points
Used with `ec-code-avx.c` when `ENABLE_EC_DYNAMIC_AVX` adds both files to the EC module build. Higher-level EC method selection code can include this header to register or probe the AVX generator.

## Risks
- Header availability must stay synchronized with the Automake conditional and implementation symbol.
- Consumers must not reference the symbol unless the AVX source is compiled into the target.

## Test Signals
Compile/link success under AVX-enabled builds is the primary signal. Runtime EC generator selection tests should confirm the descriptor is visible only when expected.
