# sources/distributed-fs/ceph-client/lib/crypto/x86/ghash-pclmul.S

Purpose: PCLMULQDQ assembly for GF(2^128) multiplication and GHASH block accumulation.

Important APIs/types/functions: local `__clmul_gf128mul_ble` multiplies two 128-bit operands modulo the GHASH/POLYVAL polynomial in ble representation. Exports `polyval_mul_pclmul()` and `ghash_blocks_pclmul()`.

Control flow: the internal multiply computes low/high carry-less products plus Karatsuba cross term, combines them into a 256-bit product, then reduces modulo the field polynomial in two phases using shifts and XORs. `polyval_mul_pclmul()` loads two operands, calls the internal multiply, and stores the result. `ghash_blocks_pclmul()` loads an accumulator and key, byte-swaps each input block with `pshufb`, XORs it into the accumulator, multiplies, and loops for `nblocks`.

State and persistence: mutates only caller-provided accumulator/operand memory. Uses XMM registers and no global state.

Dependencies: PCLMULQDQ, SSSE3 `pshufb` for byte swap, x86_64 frame macros, caller-side FPU context handling in `gf128hash.h`.

Integration points: called by the GF128 hash architecture dispatch for GHASH and POLYVAL.

Risks: endian conversion is central; a wrong byte-swap mask breaks GHASH while POLYVAL direct multiply may still appear correct. `nblocks` is expected nonzero when called; callers control chunking and fallback.

Test signals: AES-GCM GHASH known answers, POLYVAL multiplication vectors, and comparison against generic implementation across multiple blocks.
