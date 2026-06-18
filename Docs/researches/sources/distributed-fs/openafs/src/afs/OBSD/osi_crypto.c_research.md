# sources/distributed-fs/openafs/src/afs/OBSD/osi_crypto.c

## Purpose
OpenBSD random-byte provider for OpenAFS kernel code.

## Important APIs, Types, and Functions
Defines `osi_readRandom(void *data, afs_size_t len)`, which calls `arc4random_buf(data, len)` and returns `0`.

## Control Flow
There is no branching: callers provide a destination buffer and length, OpenBSD kernel random fills the buffer, and success is reported unconditionally.

## State and Persistence
No persistent state is kept here. Entropy state belongs to OpenBSD random facilities.

## Dependencies and Integration Points
Includes `<dev/rndvar.h>` and OpenAFS `afsconfig.h`/`param.h`. Integrates with any OpenAFS code that needs platform-random bytes, such as crypto/session material generation.

## Risks
The function assumes `arc4random_buf` cannot fail and does not validate `data` or `len`. It also provides no accounting or blocking behavior control.

## Test Signals
Build on supported OpenBSD kernels and call through OpenAFS random consumers. A smoke test should verify non-crash behavior for normal nonzero lengths and that symbols resolve in kernel builds.
