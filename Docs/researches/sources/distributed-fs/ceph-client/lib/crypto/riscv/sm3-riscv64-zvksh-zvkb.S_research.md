# sources/distributed-fs/ceph-client/lib/crypto/riscv/sm3-riscv64-zvksh-zvkb.S

## Purpose

This RV64 vector crypto assembly file implements the SM3 compression transform using `Zvksh` and `Zvkb`. It was read as a complete 124-line file.

## Important APIs, Types, and Functions

It exports `sm3_transform_zvksh_zvkb(struct sm3_block_state *state, const u8 *data, size_t nblocks)`. The `sm3_8rounds` macro uses `vsm3c.vi` for compression rounds and `vsm3me.vv` for message expansion.

## Control Flow

The function loads and endian-swaps the 8-word SM3 state into a vector, then loops over 512-bit message blocks. For each block it saves the previous state, loads two message vectors, executes eight macro invocations for 64 rounds, XORs the previous state back in, and repeats until all blocks are processed. The final state is endian-swapped back and stored.

## State and Persistence Behavior

The only persistent mutation is the caller's `sm3_block_state`. Vector registers hold temporary state and schedule words inside caller-managed vector state.

## Dependencies and Integration Points

It is declared and dispatched by `riscv/sm3.h`, which is included by the generic `sm3.c` implementation under `CONFIG_CRYPTO_LIB_SM3_ARCH`.

## Risks and Edge Cases

Risks include endian conversion, vector feature gating, correct XOR feed-forward semantics, and ensuring the block count is nonzero. The assembly assumes vector crypto support and relies on its wrapper to enforce that.

## Test Signals

SM3 KUnit vectors, long multi-block inputs, generic-versus-accelerated comparison, and RISC-V vector build coverage are the main signals.
