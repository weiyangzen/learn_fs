# sources/distributed-fs/ceph-client/lib/crypto/riscv/sm3.h

## Purpose

This header integrates the RISC-V vector SM3 transform with the generic SM3 streaming library. It was read as a complete 39-line file.

## Important APIs, Types, and Functions

It defines `have_extensions`, declares `sm3_transform_zvksh_zvkb`, implements `sm3_blocks`, and defines `sm3_mod_init_arch`.

## Control Flow

During module init, `sm3_mod_init_arch` enables acceleration only when `ZVKSH`, `ZVKB`, and VLEN >= 128 are available. During hashing, `sm3_blocks` checks the static key and `may_use_simd()`, wraps the assembly call with kernel vector begin/end, or falls back to `sm3_blocks_generic`.

## State and Persistence Behavior

Persistent state is limited to the static key. Hash state is caller-owned and follows `sm3.c` update/final semantics.

## Dependencies and Integration Points

It depends on RISC-V vector helpers and generic SM3 symbols. It is included by `sm3.c` when architecture SM3 support is enabled.

## Risks and Edge Cases

Feature detection and vector-state safety are the central risks. Fallback correctness is important for systems lacking vector crypto or contexts where SIMD is disabled.

## Test Signals

SM3 KUnit tests, architecture build coverage, forced generic fallback, and accelerated hardware comparison validate this wrapper.
