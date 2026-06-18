# sources/distributed-fs/ceph-client/lib/crypto/arm/sha256-armv4.pl

## Purpose
This Perl generator emits ARMv4 scalar, ARMv7 NEON, and optional ARMv8 SHA-256 crypto-extension block compression assembly derived from OpenSSL/Cryptogams.

## Important APIs, Types, And Functions
Generated symbols include `sha256_block_data_order`, `sha256_block_data_order_neon`, and `sha256_block_data_order_armv8`. The generator defines `BODY_00_15`, `BODY_16_XX`, `Xupdate`, `Xpreload`, and `body_00_15` helpers and emits the `K256` round table.

## Control Flow
The scalar routine loads the SHA-256 state, loops over 64-byte blocks, builds the message schedule, executes 64 rounds, and stores accumulated state. In non-kernel OpenSSL-style builds it can inspect `OPENSSL_armcap_P` and branch to NEON or ARMv8 code. The NEON path vectorizes schedule construction and parts of round preparation. The ARMv8 path uses SHA-256 extension instructions when generated for capable targets.

## State And Persistence
Runtime persistence is limited to the caller's `sha256_block_state`. The generator emits read-only constants and code; it has no runtime data state in the kernel.

## Dependencies And Integration Points
It depends on Perl at build time and ARM assembler support. `arm/sha256.h` declares the generated scalar/NEON symbols and separately declares `sha256_ce_transform` from the dedicated CE source.

## Risks And Edge Cases
Maintaining multiple generated variants risks divergence. Endian conversion, round constants, and schedule recurrence must be exact. Non-kernel capability code is present in the generator but the kernel dispatch is controlled by headers, so symbol naming and build flags must stay aligned.

## Test Signals
SHA-224/SHA-256 vectors, large multi-block streams, random comparison with generic C, builds for pre-ARMv7 and ARMv7 NEON, and generator reproducibility checks are useful.
