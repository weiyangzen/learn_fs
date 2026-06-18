# sources/distributed-fs/ceph-client/lib/crypto/s390/chacha-s390.h

## Purpose

This header declares the s390 vector ChaCha20 assembly function. It was read as a complete 14-line file.

## Important APIs, Types, and Functions

It declares `chacha20_vx(u8 *out, const u8 *inp, size_t len, const u32 *key, const u32 *counter)`.

## Control Flow

There is no control flow. The declaration is consumed by `s390/chacha.h`, which handles feature checks and vector-state bracketing.

## State and Persistence Behavior

The function contract writes output and consumes caller-provided key and counter words. The wrapper updates the higher-level ChaCha state after the assembly call.

## Dependencies and Integration Points

It depends on standard crypto integer types being visible before inclusion and integrates `chacha-s390.S` with the generic ChaCha architecture hook.

## Risks and Edge Cases

Prototype mismatch would corrupt registers at the assembly ABI boundary. The assembly is hard-coded for ChaCha20 rounds, so the wrapper must gate non-20-round calls away from it.

## Test Signals

s390 build/link tests and ChaCha KUnit known-answer tests exercise this declaration boundary.
