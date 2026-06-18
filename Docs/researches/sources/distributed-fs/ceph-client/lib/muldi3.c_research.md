# sources/distributed-fs/ceph-client/lib/muldi3.c

Purpose: Provides `__muldi3` 64-bit multiplication support for toolchains/architectures that need libgcc-style helpers.

Important APIs/types/functions: Exports `__muldi3(long long u, long long v)`. Uses `DWunion`, `umul_ppmm`, and half-word macros to compute partial products.

Control flow: Multiplies low halves to form the base 64-bit product, then adds cross-products of high/low halves into the high word.

State and persistence: Stateless arithmetic.

Dependencies/integration: Depends on `linux/libgcc.h` and kernel export infrastructure; marked `notrace`.

Risks: Type-width assumptions are fixed around `W_TYPE_SIZE 32`; intended for supported compiler/runtime contexts.

Test signals: No local tests; exercised implicitly by builds/runtimes that emit `__muldi3` calls.
