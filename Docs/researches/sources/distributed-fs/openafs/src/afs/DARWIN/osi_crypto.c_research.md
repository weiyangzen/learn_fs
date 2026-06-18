# sources/distributed-fs/openafs/src/afs/DARWIN/osi_crypto.c

## Purpose
Provides the Darwin kernel implementation of OpenAFS random-byte acquisition.

## Important APIs, Types, And Functions
The only function is `osi_readRandom(void *data, afs_size_t len)`, which calls Darwin `read_random(data, len)` and returns zero.

## Control Flow
Callers pass an output buffer and byte count; the function delegates to the kernel random provider and does no retry, length adjustment, or error mapping.

## State And Persistence
There is no local state. Entropy state is wholly owned by the Darwin kernel random subsystem.

## Dependencies And Integration Points
Depends on `<sys/random.h>` and the OpenAFS `afs_size_t` type. It backs higher-level cache-manager code that needs random data without knowing the host kernel API.

## Risks
The function assumes `read_random` cannot fail or that its failure is not externally reported by this API. Buffer validity and sleepability requirements are inherited from Darwin.

## Test Signals
Build coverage is the main signal. Runtime tests should request non-zero random buffers during token/PAG or crypto-related operations and verify the caller does not receive all-zero or uninitialized data.
