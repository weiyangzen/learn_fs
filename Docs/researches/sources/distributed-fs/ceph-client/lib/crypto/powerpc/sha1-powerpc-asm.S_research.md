# sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1-powerpc-asm.S

## Purpose
Implements the standard PowerPC SHA-1 compression function for non-SPE builds, processing one 64-byte block per call.

## Important APIs, Types, and Functions
Exports `_GLOBAL(powerpc_sha_transform)`, declared in `sha1.h`. Macros `STEPD0_*`, `STEPD1*`, `STEPD2_UPDATE`, `STEP0LD4`, `STEPUP4`, and `STEPUP20` unroll SHA-1 rounds and message schedule generation.

## Control Flow
The function saves registers, loads A through E from the state, loads initial message words with endian-aware `LWZ`, runs the 80 SHA-1 rounds in four constant phases, updates the message schedule in a 16-word rolling window, adds the resulting working values back into the input state, stores state, restores registers, and returns.

## State and Persistence
Mutates the 160-bit SHA-1 state in place for exactly one block. It uses stack only for register saves and has no global state.

## Dependencies and Integration Points
Depends on PowerPC assembly support headers. `sha1.h` loops over input blocks and calls this transform for each block when `CONFIG_SPE` is not enabled.

## Risks
SHA-1 is collision-broken, so algorithm use is security-sensitive outside compatibility contexts. Endian conversion must match SHA-1 big-endian message word semantics. The transform handles only one block per call.

## Test Signals
SHA-1 digest known-answer tests, multi-block wrapper tests, and BE/LE comparison against the generic implementation validate the transform.
