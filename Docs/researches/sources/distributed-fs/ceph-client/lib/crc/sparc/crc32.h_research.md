# sources/distributed-fs/ceph-client/lib/crc/sparc/crc32.h

## Purpose
This SPARC arch header enables CRC32C acceleration on sparc64 CPUs that advertise the crypto facility and CRC32C opcode.

## Important APIs, Types, and Functions
It declares static key `have_crc32c_opcode`, maps CRC32 LE/BE to base implementations, declares `crc32c_sparc64()`, defines `crc32c_arch()`, `crc32_mod_init_arch()`, and `crc32_optimizations_arch()`.

## Control Flow
`crc32c_arch()` checks the static key, aligns the buffer to 8 bytes with the base implementation, calls `crc32c_sparc64()` on the aligned 8-byte body, then processes any tail in software. Module init checks `HWCAP_SPARC_CRYPTO` and ASR26 `CFR_CRC32C` before enabling the static key.

## State and Persistence
Persistent runtime state is a read-mostly static key indicating opcode availability. Per-call CRC state remains local.

## Dependencies and Integration Points
It depends on SPARC pstate/ELF hwcap definitions and the assembly routine in `crc32c_asm.S`. It plugs into generic CRC32 hooks only for CRC32C.

## Risks and Test Signals
Risks include ASR feature probing failures, static-key state before init, alignment arithmetic, and only accelerating CRC32C while CRC32 LE/BE remain base. Test signals include boot logs, KUnit CRC32C tests on sparc64 crypto-capable CPUs, and fallback coverage on older CPUs.
