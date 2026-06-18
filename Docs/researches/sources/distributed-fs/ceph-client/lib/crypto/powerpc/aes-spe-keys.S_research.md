# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-keys.S

## Purpose
Implements AES key schedule handling for the 32-bit PowerPC SPE AES backend. It expands 128-, 192-, and 256-bit AES keys into encryption round-key buffers and derives a decryption key schedule from an existing encryption schedule. This is the setup companion to the SPE AES block and mode assembly.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_expand_key_128)`, `_GLOBAL(ppc_expand_key_192)`, `_GLOBAL(ppc_expand_key_256)`, and `_GLOBAL(ppc_generate_decrypt_key)`. Callers pass the output schedule in `r3` and raw key/encryption schedule inputs in `r4`; `ppc_generate_decrypt_key` also consumes the AES key length in `r5`. The file defines `LOAD_KEY`, `INITIALIZE_KEY`, `FINALIZE_KEY`, `LS_BOX`, and `GF8_MUL` macros rather than C types.

## Control Flow
Each expansion routine loads the raw key with endian-aware `LOAD_KEY`, stores the first round key, then iterates a fixed number of key expansion rounds. AES-128 loops 10 times with RotWord/SubWord/Rcon processing every round, AES-192 loops over six-word chunks with an early final exit, and AES-256 handles the extra SubWord step on the fourth generated word. `ppc_generate_decrypt_key` reverses first and last round keys, then applies an InvMixColumns-style transformation to middle schedule words in `ppc_generate_decrypt_block` and `ppc_generate_decrypt_word`.

## State and Persistence
The routines write expanded key material into caller-provided memory and otherwise keep state in GPRs. `FINALIZE_KEY` restores saved registers and clears several volatile registers that held key material, reducing leftover sensitive data in registers. No global state is mutated.

## Dependencies and Integration Points
The code includes `<asm/ppc_asm.h>` and depends on `PPC_AES_4K_ENCTAB` from `aes-tab-4k.S` for S-box lookups in `LS_BOX`. It is called by the PowerPC AES header glue when `CONFIG_SPE` is enabled, which exposes these functions through the AES library arch hooks.

## Risks
Correctness risk centers on key-length-specific schedule sizes and the `r5` encoding used by decrypt-key generation. Because the S-box is table-based, it can expose cache-timing side channels on systems where attacker observation of cache state is realistic. Endian-specific key loading also needs cross-endian coverage.

## Test Signals
Useful signals are AES known-answer tests for 128/192/256-bit keys, encrypt/decrypt round trips through the SPE AES block code, and comparisons of generated schedules against generic AES schedule generation on both big- and little-endian builds.
