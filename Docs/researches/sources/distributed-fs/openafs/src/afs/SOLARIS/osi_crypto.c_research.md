# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_crypto.c

## Purpose
Solaris random-byte provider for OpenAFS kernel code.

## Important APIs, Types, and Functions
Defines `osi_readRandom(void *data, afs_size_t len)`, which calls `random_get_pseudo_bytes(data, len)` and returns `0`.

## Control Flow
Straight-line wrapper around Solaris kernel pseudo-random bytes.

## State and Persistence
No state is owned in this file. Random state is owned by the Solaris kernel.

## Dependencies and Integration Points
Includes `<sys/random.h>`. Used by common OpenAFS crypto/random consumers.

## Risks
Uses pseudo-random API and reports success unconditionally. No validation of buffer pointer or length is performed.

## Test Signals
Solaris kernel build symbol resolution and random consumer smoke tests that request nonzero random material.
