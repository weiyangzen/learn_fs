# sources/distributed-fs/ceph-client/lib/crypto/s390/chacha-s390.S

## Purpose

This s390 assembly file implements vectorized ChaCha20 encryption for systems with vector extensions. It was read as a complete 908-line file.

## Important APIs, Types, and Functions

It exports `chacha20_vx_4x` and `chacha20_vx`. The public header declares `chacha20_vx`; the top-level function jumps to the 4-block path for shorter lengths and otherwise uses a larger six-block vector pipeline. The local `sigma` data block contains ChaCha constants, counter increments, byte-permutation masks, and smashed sigma vectors.

## Control Flow

`chacha20_vx_4x` handles up to four 64-byte blocks with ten double-round iterations, transposes vector lanes into output order, XORs keystream with input, and handles tails byte by byte. `chacha20_vx` allocates a stack frame for larger inputs, processes six blocks per outer loop, reloads constants and counters as needed, emits full 64-byte chunks, and uses a byte tail loop for the final partial block.

## State and Persistence Behavior

The assembly does not update the ChaCha state directly. It consumes key and counter pointers and writes ciphertext/plaintext to the output buffer. The C wrapper updates the stream counter after return. Vector registers and stack scratch space hold transient keystream and tail data.

## Dependencies and Integration Points

It depends on s390 vector instruction macros, FPU/vector state management by `s390/chacha.h`, and the generic ChaCha library dispatch. It assumes the C wrapper called `kernel_fpu_begin()`.

## Risks and Edge Cases

Risks include counter increment correctness, tail byte handling, stack frame restore, exact 20-round behavior, overlap assumptions inherited from stream cipher APIs, and ensuring the wrapper never calls this without vector support.

## Test Signals

ChaCha20 known-answer tests, ChaCha20-Poly1305 KUnit tests, lengths around 64 and 256 bytes, odd tail lengths, and generic-versus-vector differential tests validate behavior.
