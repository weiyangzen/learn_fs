# sources/distributed-fs/glusterfs/libglusterfs/src/throttle-tbf.c

## Purpose

`throttle-tbf.c` implements a basic token-bucket throttling facility for rate-limiting selected operations such as disk reads, directory scans, and hash calculations. Callers consume operation-specific tokens before running work; requests that exceed available tokens wait on a per-request condition variable until a token-generator thread refills the bucket.

## Important APIs, Types, and Functions

Public APIs are `tbf_init()`, `tbf_mod()`, and `tbf_throttle()`. Internal functions include `tbf_init_throttle()`, `_tbf_dispatch_queued()`, `tbf_tokengenerator()`, `tbf_init_bucket()`, and `tbf_mod_bucket()`. `tbf_t` owns an array of operation buckets. Each `tbf_bucket_t` has a lock, queued throttle list, current tokens, token rate, maximum tokens, token generation interval, and token-generator thread. Each queued request is a `tbf_throttle_t` with requested token count, mutex, condvar, done flag, and list link.

## Control Flow and Data Flow

Initialization allocates one `tbf_t` plus its bucket pointer array, then initializes buckets for nonzero-rate specs. A bucket starts with zero tokens, configured rate and max, and a token generator thread. The generator sleeps for `token_gen_interval` microseconds converted to nanoseconds, adds `tokenrate` up to `maxtokens`, and dispatches queued requests in FIFO order while enough tokens exist.

`tbf_throttle()` checks the bucket for the requested op. If no bucket exists, it returns immediately. If enough tokens exist, it consumes them under the bucket lock. Otherwise it allocates a request, locks the request mutex, queues it, releases the bucket lock, and waits until `_tbf_dispatch_queued()` marks it done and signals. `tbf_mod()` either resets rate/max and tokens for an existing bucket or creates a new bucket.

## State and Persistence Behavior

All state is in memory. Buckets persist for the lifetime of the `tbf_t`; the observed file does not provide a destructor or a way to stop token-generator threads. Queued request state lives until the waiting caller is released and frees its `tbf_throttle_t`.

## Dependencies and Integration Points

The file depends on Gluster mem-pool types, list primitives, locks, `gf_nanosleep()`, `gf_thread_create()`, and throttle type declarations. It integrates with macros in `throttle-tbf.h` that wrap operations with begin/end throttling calls.

## Risks and Edge Cases

If `tokens_requested` is larger than `maxtokens`, the request can wait forever because the bucket can never accumulate enough tokens. Allocation failure lets the operation proceed unthrottled. `tbf_mod_bucket()` resets tokens and rates but does not update `token_gen_interval`, so interval changes to existing buckets are ignored. Token-generator threads run forever in the observed code, so lifecycle management must be external or intentionally process-long. Queue dispatch stops at the first request that cannot be satisfied, preserving FIFO but allowing head-of-line blocking.

## Test Signals

Tests should verify immediate pass-through for unconfigured operations, token consumption, blocking and wakeup after refill, FIFO dispatch, head-of-line blocking, modifications to rate/max, oversized token requests, allocation failure behavior, and thread lifecycle assumptions under process shutdown.
