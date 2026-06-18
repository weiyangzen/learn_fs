# sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif-core.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif-core.S` implements AArch64 ASIMD/PMULL accelerated CRC-T10DIF. It provides a native PMULL64 final-CRC path and an 8-bit polynomial multiply folding path for CPUs without PMULL64.

## Important APIs, Types, and Functions

Assembly entry points are `crc_t10dif_pmull_p8` and `crc_t10dif_pmull_p64`; local helper `__pmull_p8_16x64` supports the p8 path. Core macros are `pmull16x64_p64`, `pmull16x64_p8`, `fold_32_bytes`, `fold_16_bytes`, and `crc_t10dif_pmull`. Read-only tables include fold constants and byte-shift indexes.

## Control Flow

The shared macro handles buffers of at least 16 bytes. For large buffers it folds 128-byte groups into eight vector accumulators, reduces to one 16-byte vector, folds additional 16-byte blocks, and handles 1..15 byte partial tails through a table-driven redivision. For shorter 16..255 byte inputs it starts with the 16-byte constants directly. `crc_t10dif_pmull_p64` reduces the final vector with PMULL and Barrett reduction to return a 16-bit CRC, while `crc_t10dif_pmull_p8` stores the folded vector for generic finishing.

## State and Persistence Behavior

No mutable global state is owned. Constants live in `.rodata`; vector and scalar registers carry per-call state.

## Dependencies and Integration Points

It depends on AArch64 assembler/linkage macros, `armv8-a+crypto`, ASIMD/PMULL availability, and dispatch from `arm64/crc-t10dif.h`.

## Risks and Edge Cases

Correctness depends on byte reversal into polynomial order, the partial-tail byte-shift table, and exact Barrett constants for polynomial `0x18bb7`. The functions assume the C wrapper has checked length and SIMD context. Any calling-convention register-save mistake can corrupt callers.

## Test Signals

Signals include KUnit CRC-T10DIF vectors for boundary lengths, ASIMD-only and PMULL feature paths, comparison with generic, tail lengths 1..15 after a folded block, and SIMD context checks under preemption.

## Read Coverage

Source read size: 469 lines, 15814 bytes.
