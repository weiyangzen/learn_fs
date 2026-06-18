# sources/distributed-fs/openafs/src/rx/rx_stubs.c

## Purpose
Provides fallback exported RX routines when optional RXGK support is not compiled.

## Important APIs, Types, And Functions
When `ENABLE_RXGK` is not defined, the file implements `rxgk_GetServerInfo(struct rx_connection *conn, RXGK_Level *level, struct afs_time64 *expiry, struct rx_identity **identity)` and returns `EINVAL`.

## Control Flow
There is a single stub path: any caller asking for RXGK server information in a non-RXGK build receives an invalid-argument error.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
It includes RX, RXGK, and identity headers so libraries can export a consistent symbol even when `src/rxgk` is excluded. This supports link compatibility for `libafsrpc` consumers.

## Risks And Test Signals
Risks are callers treating the stub as partially functional or failing to handle `EINVAL`. Link tests for non-RXGK builds and runtime checks that RXGK-dependent features report unsupported status are the useful signals.
