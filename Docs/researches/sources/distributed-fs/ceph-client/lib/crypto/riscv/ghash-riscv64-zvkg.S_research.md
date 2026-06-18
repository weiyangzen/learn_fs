# sources/distributed-fs/ceph-client/lib/crypto/riscv/ghash-riscv64-zvkg.S

## Purpose
Implements RISC-V vector GHASH block processing using the Zvkg `vghsh.vv` instruction.

## Important APIs, Types, and Functions
Exports `ghash_zvkg(u8 accumulator[16], const u8 key[16], const u8 *data, size_t nblocks)`. Register aliases name `ACCUMULATOR`, `KEY`, `DATA`, and `NBLOCKS`.

## Control Flow
The function sets vector length to four 32-bit lanes, loads accumulator and key into vector registers, then loops over data blocks. For each 16-byte block it loads data into `v3`, applies `vghsh.vv v1, v2, v3`, advances the data pointer, decrements block count, and repeats until zero. It stores the final accumulator and returns.

## State and Persistence
Only the accumulator buffer is updated in place. Key and data are read-only. No stack or global state is used.

## Dependencies and Integration Points
Requires RV64I, V with VLEN at least 128, and Zvkg. Called by `riscv/gf128hash.h` after accumulator/key representation setup and vector begin.

## Risks
The function contract says `nblocks` must be nonzero; callers must avoid zero-block calls. All representation conversion is outside this file, so mismatched byte order in the wrapper would make this correct primitive produce incorrect GHASH results.

## Test Signals
GHASH known-answer tests for one and many blocks, plus zero-block caller tests at wrapper level to ensure the assembly is not invoked with `nblocks == 0`.
