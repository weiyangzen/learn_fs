# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aesp8-ppc.pl

## Purpose
Generates POWER8 AES vector-crypto assembly from CRYPTOGAMS/perlasm sources. The generated code implements AES key setup, single-block encrypt/decrypt, CBC, CTR32, and XTS with optimized multi-block paths.

## Important APIs, Types, and Functions
The Perl generator emits symbols with the `aes_p8` prefix: `aes_p8_set_encrypt_key`, `aes_p8_set_decrypt_key`, `aes_p8_encrypt`, `aes_p8_decrypt`, `aes_p8_cbc_encrypt`, `aes_p8_ctr32_encrypt_blocks`, `aes_p8_xts_encrypt`, and `aes_p8_xts_decrypt`. It uses `$flavour`, `$SIZE_T`, `$LITTLE_ENDIAN`, `$FRAME`, and `ppc-xlate.pl` to produce ABI- and endian-specific output.

## Control Flow
The script validates the requested 32/64-bit flavour, finds `ppc-xlate.pl`, pipes generated pseudo-assembly through it, and conditionally rewrites endian markers. Generated key setup validates pointers and AES key size, then uses vector AES instructions and constants to derive round keys. Single-block functions align unaligned input/output, loop over rounds with `vcipher` or `vncipher`, and store with masks. CBC encrypt/decrypt contains scalar one-block loops and an 8x decrypt path for long inputs. CTR has single-block and 8x loops and increments counters with 128-bit vector addition. XTS handles optional key2 tweak encryption, tweak chaining mode when key2 is NULL, ciphertext stealing, and 6x/5x helpers for long runs.

## State and Persistence
The script itself persists no state beyond writing generated assembly. Generated routines save and restore VRSAVE and ABI-required vector registers, wipe stack copies of round keys in the optimized paths, update IV/tweak buffers for chaining modes, and return error codes for invalid key setup or too-short XTS input.

## Dependencies and Integration Points
Depends on CRYPTOGAMS perlasm conventions and `ppc-xlate.pl`. The generated symbols are declared and exported by `aes.h` and are used when the PowerPC CPU supports ISA 2.07 vector crypto. It also assumes the kernel enables VSX and manages preemption/page faults before calls.

## Risks
Generated code is difficult to review because Perl string interpolation, endian conditional markers, and assembler translation all affect final instructions. XTS stealing and tweak chaining are high-risk edge cases. Unaligned VSX loads/stores may fault at page boundaries if callers violate kernel access assumptions, which is why the C wrapper disables page faults around key setup and block ops.

## Test Signals
Regenerate and diff the produced assembly after script changes. Run AES vector crypto self-tests for all key sizes and modes, with CBC/CTR/XTS lengths around 1, 7, 8, 16, 96, 128, and non-multiple-of-block XTS tails. Validate big- and little-endian output if both flavours are supported.
