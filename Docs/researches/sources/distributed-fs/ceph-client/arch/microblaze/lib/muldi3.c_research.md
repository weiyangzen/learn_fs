# sources/distributed-fs/ceph-client/arch/microblaze/lib/muldi3.c

Purpose: implements 64-bit multiply helper `__muldi3` using 16-bit partial products.

Important APIs and state: exported `__muldi3(long long u, long long v)`. Macros split 32-bit words into 16-bit halves and assemble a 64-bit product in `DWunion`.

Control flow: computes low-word product with `__umulsidi3`, then adds cross products of low/high 32-bit halves into the high word.

State and persistence: pure arithmetic.

Dependencies and integration: compiler-generated 64-bit multiply and modules use it; endian layout is from `libgcc.h`.

Risks and test signals: carry handling in partial products is critical. Test signed/unsigned bit patterns, high-half overflow, zero/one/m negative values, and module use.
