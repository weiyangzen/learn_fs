# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crc32.c

## Purpose
Table-driven CRC32 and CRC32C helpers.

## Key Content
Contains static lookup tables for standard CRC32 polynomial and CRC32C, a shared `compute_crc32()` loop, and exported `crypt_crc32()` / `crypt_crc32c()` wrappers. The seed is supplied by the caller and no final XOR is applied internally.

## Dependencies and Coupling
Includes `crypto_backend.h`. BITLK uses `crypt_crc32()` to validate FVE metadata copies.

## Invariants and Risks
Callers must apply any format-specific initial/final XOR policy themselves. The function is byte-oriented and not hardware accelerated.
