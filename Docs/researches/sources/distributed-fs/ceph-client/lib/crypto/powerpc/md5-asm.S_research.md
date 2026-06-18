# sources/distributed-fs/ceph-client/lib/crypto/powerpc/md5-asm.S

## Purpose
Implements a PowerPC optimized MD5 compression function over one or more 64-byte message blocks.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_md5_transform)`. The public signature is declared in `md5.h` as `void ppc_md5_transform(u32 *state, const u8 *data, size_t nblocks)`. Round macros `R_00_15`, `R_16_31`, `R_32_47`, and `R_48_63` implement the four MD5 boolean/rotation phases.

## Control Flow
The function saves GPRs, loads the four hash words, sets the CTR from `nblocks`, and enters `ppc_md5_main`. Each block runs the 64 MD5 operations unrolled in pairs, with endian-aware input loads. At the end of each block it adds the working hash values back into the state buffer, advances the input pointer where required by endian mode, decrements CTR, and loops.

## State and Persistence
The caller's 128-bit MD5 state is updated in place. No global state is used. Stack-saved registers are restored but message/hash working values are not explicitly wiped beyond normal register reuse.

## Dependencies and Integration Points
Depends on PowerPC assembly helper macros from `<asm/ppc_asm.h>`, `<asm/asm-offsets.h>`, and `<asm/asm-compat.h>`. The generic MD5 library calls it through `md5_blocks` in `md5.h`.

## Risks
MD5 is cryptographically broken for collision resistance, so this optimization is only appropriate where MD5 remains protocol-compatible but not security-critical. Endian load behavior differs between BE and LE. The transform assumes complete 64-byte blocks.

## Test Signals
MD5 digest known-answer tests, multi-block tests, and BE/LE comparisons against the generic C transform validate behavior. Boundary tests should pass `nblocks` of 1 and larger values.
