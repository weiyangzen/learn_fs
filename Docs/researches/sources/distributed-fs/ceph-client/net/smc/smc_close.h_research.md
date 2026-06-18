# sources/distributed-fs/ceph-client/net/smc/smc_close.h

## Purpose
`smc_close.h` is the small public interface for SMC close handling. It declares timeout constants and the close/release/abort functions used by socket operations, CDC receive processing, and connection setup/teardown code.

## Important APIs, Types, And Functions
The header defines `SMC_MAX_STREAM_WAIT_TIMEOUT` as the default maximum wait for prepared stream data during close and `SMC_CLOSE_SOCK_PUT_DELAY` as a close-related delay constant. It declares `smc_close_wake_tx_prepared()`, `smc_close_active()`, `smc_close_shutdown_write()`, `smc_close_init()`, `smc_clcsock_release()`, `smc_close_abort()`, and `smc_close_active_abort()`.

## Control Flow
`af_smc.c` calls `smc_close_init()` during socket initialization, `smc_close_active()` from release and full shutdown paths, `smc_close_shutdown_write()` from `SHUT_WR`, `smc_close_active_abort()` during failed or aborted active setup, and `smc_clcsock_release()` during final cleanup. `smc_cdc.c` and TX logic use `smc_close_abort()` and `smc_close_wake_tx_prepared()` to signal close or unblock a close waiting for TX progress.

## State And Persistence
The header owns no storage. Its constants bound close wait behavior, while declared functions operate on persistent `struct smc_sock` and `struct smc_connection` state defined in `smc.h`: socket state, CLC socket pointer, CDC flags, close work, TX work, and pending TX indicators.

## Dependencies And Integration Points
`smc_close.h` includes workqueue support and `smc.h`, making it available to AF_SMC socket operations, CDC flow-control, TX send paths, and core cleanup paths. It is the compile-time boundary between close-state implementation and the rest of the SMC subsystem.

## Risks And Edge Cases
Because the header exposes only high-level close actions, callers must hold the correct socket lock and reference expectations required by `smc_close.c`. Misuse can cause double release of CLC sockets, missed wakeups for close waiting on prepared TX data, or unmatched passive-close references.

## Test Signals
Header-level signals are build coverage and correct linkage. Runtime signals come from the `smc_close.c` state-machine tests: active close, half close, abort, pending TX wakeup, CLC release, and workqueue cleanup paths.
