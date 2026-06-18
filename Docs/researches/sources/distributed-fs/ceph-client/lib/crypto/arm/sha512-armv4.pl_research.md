# sources/distributed-fs/ceph-client/lib/crypto/arm/sha512-armv4.pl

## Purpose
This Perl generator emits ARMv4 scalar and ARMv7 NEON SHA-512 block compression assembly. It is OpenSSL/Cryptogams-derived and relicensed for GPLv2 kernel use.

## Important APIs, Types, And Functions
Generated symbols are `sha512_block_data_order` and `sha512_block_data_order_neon`. Generator helpers include `BODY_00_15`, `NEON_00_15`, and `NEON_16_79`. The `K512` table stores 80 64-bit constants in endian-aware word order.

## Control Flow
The scalar path treats each 64-bit SHA-512 word as high/low 32-bit halves, loads the state, processes 128-byte blocks through 80 rounds, updates the message schedule on stack, and stores accumulated state. The NEON path uses vector 64-bit operations for schedule and state accumulation, loops through `.Loop_neon` and `.L16_79_neon`, and rewinds the constants table between blocks.

## State And Persistence
Only the caller's `sha512_block_state` persists. Generated constant data is read-only. The stack holds schedule words and saved registers.

## Dependencies And Integration Points
It depends on Perl and ARM assembler support at build time. `arm/sha512.h` selects scalar or NEON generated routines depending on runtime NEON usability.

## Risks And Edge Cases
SHA-512 on 32-bit ARM is sensitive to high/low word ordering, carries, rotations spanning word halves, and endian configuration. The NEON routine includes an early Cortex-A8 erratum barrier and must preserve VFP ABI expectations.

## Test Signals
SHA-384/SHA-512 known-answer tests, multi-block randomized comparisons with generic C, big-endian build coverage, ARMv4 compatibility builds, and NEON runtime tests validate this generator.
