# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-tab-4k.S

## Purpose
Defines compact, 4 KiB-aligned AES T-tables and inverse S-box data for the PowerPC SPE AES backend. These tables trade memory footprint and table locality against constant-time behavior.

## Important APIs, Types, and Functions
Exports data symbols `PPC_AES_4K_ENCTAB`, `PPC_AES_4K_DECTAB`, and `PPC_AES_4K_DECTAB2`. The `R(a,b,c,d)` macro emits four rotated 32-bit variants from one AES table entry.

## Control Flow
There is no executable control flow. The file emits `.data` with encryption table words, decryption table words, and a byte inverse S-box table.

## State and Persistence
The tables are persistent read-mostly kernel data once linked. They are used by key expansion and block encryption/decryption and are not modified at runtime.

## Dependencies and Integration Points
Consumed by `aes-spe-keys.S`, `aes-spe-modes.S`, and the AES SPE core. Table values are derived from `crypto/aes_generic.c` but laid out for SPE-friendly indexed loads and rotations.

## Risks
The file explicitly notes cache-timing exposure from table lookups. Any table corruption causes broad AES failure and may be hard to localize because multiple routines depend on the same symbols. Alignment matters for performance and addressing assumptions.

## Test Signals
AES known-answer tests across key sizes and modes validate table contents indirectly. Static checks should confirm symbol names and 4 KiB alignment survive assembler/linker changes.
