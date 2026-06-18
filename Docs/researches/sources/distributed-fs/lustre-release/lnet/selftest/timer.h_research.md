# sources/distributed-fs/lustre-release/lnet/selftest/timer.h

## Purpose
Declares the selftest timer object and lifecycle APIs.

## Important APIs And Types
`struct stt_timer` contains a list node, absolute expiry seconds, callback, and callback data. Functions are `stt_add_timer()`, `stt_del_timer()`, `stt_startup()`, and `stt_shutdown()`.

## Control Flow
Callers initialize the embedded timer, set expiry/callback/data, add it, and delete it before destroying the owner unless callback ownership handles cleanup.

## State And Persistence
Timer state is embedded in caller objects and linked into the global timer queue while active. No persistent state exists.

## Dependencies And Integration Points
Included by `selftest.h` and used throughout the selftest subsystem. Assumes list/time types are available from including context.

## Risks
Asynchronous callbacks can race deletion. Destroying an object with a queued timer corrupts the queue.

## Test Signals
Compile integration plus add/delete/startup/shutdown runtime checks.
