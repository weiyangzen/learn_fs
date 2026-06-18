# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-avx.c

## Purpose
Provides the AVX2-backed EC code generator descriptor used by the erasure-code translator. It emits vectorized 32-byte load/store/copy/xor operations through the shared Intel code-emission helpers.

## Important APIs and Functions
- `ec_code_avx_prolog`: records the loop start address in `builder->loop`.
- `ec_code_avx_epilog`: advances source/destination offsets by 32 bytes, tests loop completion against `builder->width - 1`, jumps back if needed, and emits return.
- `ec_code_avx_load` / `ec_code_avx_store`: emit memory-to-AVX and AVX-to-memory moves for linear and pointer-array layouts.
- `ec_code_avx_copy`, `ec_code_avx_xor2`, `ec_code_avx_xor3`, `ec_code_avx_xorm`: emit AVX register moves and XORs, including XOR from memory.
- `ec_code_gen_avx`: exported `ec_code_gen_t` descriptor with name `"avx"`, required flag `"avx2"`, width 32, and function pointers.

## Control Flow
The EC code builder calls the descriptor callbacks while generating encode/reconstruct routines. Linear mode computes offsets from `idx * width * bits + bit * width` against `REG_SI` plus loop offset `REG_DX`. Nonlinear mode treats `REG_SI` as a pointer table, caches the current base index in `builder->base`, loads the selected pointer into `REG_AX` when needed, then accesses `bit * width` from that base. The epilog increments `REG_DX` and `REG_DI` by 32 and loops until the width mask test is zero.

## State and Persistence
No persistent state. The functions mutate `ec_code_builder_t` code buffers/register bookkeeping (`address`, `loop`, `base`) and generate executable code used at runtime by EC methods.

## Dependencies and Integration Points
Includes `ec-code-intel.h` and uses Intel emitter helpers for AVX moves, XORs, integer ops, conditional jumps, and return. It is conditionally included by `Makefile.am` under `ENABLE_EC_DYNAMIC_AVX`, and declared through `ec-code-avx.h`.

## Risks
- Requires AVX2; runtime selection must honor `ec_code_avx_needed_flags`.
- Generated loop correctness depends on `builder->width` being 32 and compatible with the mask test.
- Nonlinear base caching must be invalidated by surrounding builder logic when source indices change unexpectedly.
- Any register convention change in `ec-code-intel` can break emitted code.

## Test Signals
Relevant tests are EC encode/decode correctness under AVX-enabled builds and CPU feature gating. Build tests should verify AVX conditional compilation; runtime tests should compare AVX output with the generic C generator across linear/nonlinear layouts and varied stripe widths.
