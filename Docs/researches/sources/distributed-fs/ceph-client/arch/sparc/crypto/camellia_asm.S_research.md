<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_asm.S -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_asm.S

## Purpose
This assembly file implements SPARC64 opcode-accelerated Camellia key expansion and block/mode encryption routines.

## Important APIs, Types, and Functions
Exported entry points include `camellia_sparc64_key_expand`, `camellia_sparc64_crypt`, `camellia_sparc64_load_keys`, ECB helpers for 3 and 4 grand rounds, and CBC encrypt/decrypt helpers for 3 and 4 grand rounds. Major macros include `CAMELLIA_6ROUNDS`, `CAMELLIA_6ROUNDS_FL_FLI`, `ROTL128`, and opcode macros from `asm/opcodes.h`; `SIGMA` holds Camellia key-schedule constants.

## Control Flow
Key expansion loads the input key into VIS/FPU registers, derives intermediate keys using Camellia F/FL/FLI operations, handles 128-bit versus 192/256-bit schedules, writes encryption subkeys, and builds the decrypt schedule. Runtime encryption loads subkeys, chooses 3-grand-round paths for 128-bit keys and 4-grand-round paths for longer keys, then processes ECB or CBC blocks through hardware opcodes.

## State and Persistence Behavior
The file does not own persistent memory; callers pass key tables and buffers. It uses VIS/FPU registers transiently and follows the SPARC calling convention through `VISEntry`/related macros.

## Dependencies and Integration Points
It is linked with `camellia_glue.c`, depends on Linux linkage macros, SPARC crypto opcode definitions, and VIS assembly helpers. The C glue exposes these routines through the kernel crypto API.

## Risks
Assembly offset tables and key schedule layout must match `CAMELLIA_TABLE_BYTE_LEN` and C declarations exactly. Register clobbering, endian assumptions, or wrong 3/4 grand-round selection would produce silent cryptographic corruption. FPU/VIS state handling is architecture-sensitive.

## Test Signals
Run Camellia known-answer tests for 128/192/256-bit keys, ECB/CBC mode tests with multi-block and odd scatterlist boundaries, objdump symbol checks, and module unload/reload stress on SPARC64 crypto-opcode hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_asm.S -->
