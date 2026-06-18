# sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha256-spe-asm.S

## Purpose
Implements an SPE optimized SHA-256 compression routine for PowerPC, processing multiple 64-byte blocks per call.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_spe_sha256_transform)`. Uses `PPC_SPE_SHA256_K` constants and macros `R_LOAD_W` and `R_CALC_W` to unroll initial message loads and calculated schedule rounds.

## Control Flow
The function saves nonvolatile SPE/GPR registers, loads the eight SHA-256 state words, sets CTR from block count, and enters `ppc_spe_sha256_main`. For each block it loads the first 16 message words, runs rounds using SHA-256 sigma, choice, and majority operations, loops through schedule calculation in 16-round groups, advances the input pointer, adds working variables back to the state words, and repeats until all blocks are processed.

## State and Persistence
Mutates the caller's 256-bit SHA-256 state in place. The finalization macro restores saved registers and zeros stack slots that may contain sensitive context from shared code paths. No global state is mutated.

## Dependencies and Integration Points
Declared and called by `sha256.h` inside SPE-enabled regions. Depends on PowerPC SPE instruction support and Linux assembler macros.

## Risks
Long preemption-disabled sections are controlled by the header wrapper, not this assembly. Endian handling must preserve SHA-256 big-endian message semantics. Round constants and calculated schedule are high-value correctness areas.

## Test Signals
SHA-256 known-answer tests and random differential tests against generic SHA-256 are needed. SPE wrapper chunk boundary tests near 1024 bytes verify multi-call state continuity.
