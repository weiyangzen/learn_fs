# sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1-spe-asm.S

## Purpose
Implements an SPE SIMD optimized SHA-1 compression routine for PowerPC, processing multiple 64-byte blocks per call.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_spe_sha1_transform)`. Uses constants table `PPC_SPE_SHA1_K` and macros `R_00_15`, `R_16_19`, `R_20_39`, `R_40_59`, and `R_60_79` to process two 32-bit rounds per 64-bit SPE register where possible.

## Control Flow
The function saves nonvolatile GPR/SPE state, loads the five hash words and constants pointer, sets CTR from block count, and enters `ppc_spe_sha1_main`. For each block, it loads message words with endian handling, runs the 80 SHA-1 rounds with rolling message schedule updates, advances the input pointer per endian mode, adds working values back to state, and loops until CTR reaches zero.

## State and Persistence
Updates the caller's SHA-1 block state in place. `FINALIZE` restores registers and wipes stack slots that held saved SPE data. No global mutable state is used.

## Dependencies and Integration Points
Called by `sha1.h` when `CONFIG_SPE` is enabled, inside `enable_kernel_spe()`/`disable_kernel_spe()` regions. Depends on Linux PowerPC SPE assembler macros and the SHA-1 constants table in this file.

## Risks
The preemption-disabled caller chunks work to bound latency; bypassing that wrapper could create long critical sections. Endian-specific input pointer increments differ. SHA-1's algorithm-level collision weakness remains.

## Test Signals
SHA-1 known-answer tests with block counts above one validate loop behavior. SPE builds should test chunking boundaries from `sha1.h` near 2048 bytes.
