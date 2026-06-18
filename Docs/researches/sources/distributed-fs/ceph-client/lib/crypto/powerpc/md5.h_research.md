# sources/distributed-fs/ceph-client/lib/crypto/powerpc/md5.h

## Purpose
Provides the PowerPC MD5 architecture hook that routes block compression to `ppc_md5_transform`.

## Important APIs, Types, and Functions
Declares `void ppc_md5_transform(u32 *state, const u8 *data, size_t nblocks)` and defines `static void md5_blocks(struct md5_block_state *state, const u8 *data, size_t nblocks)`.

## Control Flow
`md5_blocks` is a thin wrapper that passes `state->h`, data, and block count directly to assembly. It does no feature gating or fallback selection.

## State and Persistence
The MD5 state object is mutated in place by the assembly transform. The header defines no persistent global state.

## Dependencies and Integration Points
Integrated by the generic MD5 implementation when building for PowerPC with this arch header available. It depends on common MD5 block-state definitions being in scope.

## Risks
There is no runtime CPU feature gating; the assembly must be valid for the configured PowerPC target. MD5 security limitations apply at the algorithm level.

## Test Signals
Generic MD5 self-tests should exercise this wrapper. Link tests should verify `ppc_md5_transform` is provided whenever this header is selected.
