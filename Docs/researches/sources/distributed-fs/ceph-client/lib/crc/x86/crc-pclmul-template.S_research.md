# sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-template.S

## Purpose
This assembly template generates x86 PCLMULQDQ/VPCLMULQDQ CRC functions for different CRC widths, bit orders, and vector widths. It emits SSE, AVX2, and AVX512 implementations from one macro body.

## Important APIs, Types, and Functions
Major macros include `_cond_vex`, `_vbroadcast`, `_load_data`, `_prepare_v0`, `_pclmulqdq`, `_fold_vec`, `_fold_vec_mem`, `_load_vec_folding_consts`, `_fold_vec_final`, `_crc_pclmul`, and `DEFINE_CRC_PCLMUL_FUNCS`. Generated functions are named `<prefix>_pclmul_sse`, `<prefix>_vpclmul_avx2`, and `<prefix>_vpclmul_avx512`.

## Control Flow
Generated functions require at least 16 bytes of input. They seed a vector with the initial CRC, optionally byte-swap lanes for MSB-first CRCs, process data in vector-sized chunks, use folding constants to reduce across 128/256/512/1024/2048-bit distances, fold final vector lanes down to 128 bits, handle short residual bytes through shuffle masks, and run Barrett reduction to return the CRC width requested by the instantiator.

## State and Persistence
Only vector registers, general registers, and stack/register save state are used during the call. There is no global mutable state in this file.

## Dependencies and Integration Points
It depends on x86 assembler support for SSE/PCLMUL, AVX2/VPCLMUL, and AVX512 variants, Linux linkage annotations, objtool annotations, and the constant layout from `crc-pclmul-consts.h`. The C template header dispatches to the generated functions through static calls inside `kernel_fpu_begin()` sections.

## Risks and Test Signals
Risks include vector-state ABI misuse, incorrect non-VEX emulation, short-tail shuffle bugs, i386 register convention mistakes, and AVX512 dispatch on CPUs that prefer YMM. CRC KUnit with forced CPU feature variants, objtool validation, and interrupt-context tests are strong signals.
