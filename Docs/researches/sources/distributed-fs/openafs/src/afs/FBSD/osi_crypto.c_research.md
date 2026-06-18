# sources/distributed-fs/openafs/src/afs/FBSD/osi_crypto.c

## Purpose
Provides the FreeBSD implementation of OpenAFS random-byte acquisition.

## Important APIs, Types, And Functions
`osi_readRandom(void *data, afs_size_t len)` calls FreeBSD `read_random(data, len)` and returns zero.

## Control Flow
The function delegates directly to the kernel random subsystem and reports success unconditionally.

## State And Persistence
No local state is kept; entropy state is kernel-owned.

## Dependencies And Integration Points
Depends on `<sys/random.h>` and supports generic OpenAFS code needing random bytes.

## Risks
No error or short-read handling is surfaced. Callers must provide valid kernel buffers.

## Test Signals
Build and runtime calls that require random data should complete and receive non-deterministic contents.
