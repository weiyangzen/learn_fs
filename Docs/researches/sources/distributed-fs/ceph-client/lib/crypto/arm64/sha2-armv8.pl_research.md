# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha2-armv8.pl

## Purpose
OpenSSL-derived perlasm generator for ARMv8 SHA-256 and SHA-512 block transforms, including scalar code and SHA256 NEON/hardware variants.

## Important APIs, Types, And Functions
Generates `sha256_block_data_order` or `sha512_block_data_order` depending on output name. For SHA256 it can also generate `sha256_block_armv8` for hardware SHA instructions and `sha256_block_neon` for ASIMD schedule acceleration. Important generator subroutines are `BODY_00_xx`, `Xpreload`, `Xupdate`, and the NEON body helpers.

## Control Flow
The script chooses 32-bit or 64-bit word parameters from the output name, emits constants, emits the scalar block loop, and for SHA256 emits optional hardware and NEON paths. Non-kernel builds dispatch based on OpenSSL capability flags; kernel use exposes the selected symbols to C dispatch code. The generated loops load state, convert input endianness, expand the message schedule, process 64 or 80 rounds, add chaining state, and iterate over blocks.

## State, Persistence, And Dependencies
Runtime state is only the caller's SHA block state. Build-time dependencies are Perl and `arm-xlate.pl`. Generated code depends on AArch64 ABI rules and optional ARMv8 SHA/NEON instructions.

## Integration Points
The arm64 SHA256 and SHA512 headers declare and dispatch to the generated block functions, while `sha256-ce.S` and `sha512-ce-core.S` provide newer CE-specific alternatives.

## Risks
Generated assembly is sensitive to output filename, flavor, register allocation, and kernel/non-kernel preprocessor branches. Endian conversion and stack save/restore errors would break all hashes. Since this is imported crypto assembly, local modifications need vector parity tests.

## Test Signals
SHA-224, SHA-256, SHA-384, and SHA-512 testmgr vectors, long-message tests, big-endian builds, and comparison of scalar, NEON, and CE/hardware paths are required signals.
