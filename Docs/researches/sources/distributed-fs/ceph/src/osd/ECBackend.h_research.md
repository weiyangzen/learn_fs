# sources/distributed-fs/ceph/src/osd/ECBackend.h

## Purpose
`ECBackend.h` declares the classic erasure-coded OSD backend. It extends `ECCommon` and exposes PG backend hooks for recovery, EC subop handling, transaction submission, reads/reconstruction, scrub support, EC encode/decode helpers, and omap operations that account for EC journal overlays.

## Important APIs, Types, and Control Flow
Public hooks include `open_recovery_op()`, `run_recovery_op()`, `recover_object()`, `_handle_message()`, `can_handle_while_inactive()`, sub-write/read handlers and reply handlers, `check_recovery_sources()`, `on_change()`, `clear_recovery_state()`, `dump_recovery_info()`, and `submit_transaction()`. Read APIs include coroutine-backed `objects_read_sync()`, direct `objects_read_local()`, `extent_to_shard_extent()`, `objects_readv_sync()`, async `objects_read_and_reconstruct()`, RMW-specific reconstruction, and `objects_read_async()`. EC helpers include `ec_can_decode()`, `ec_encode_acting_set()`, `ec_decode_acting_set()`, and `ec_get_sinfo()`.

The nested `ECRecoveryBackend` adapts `RecoveryBackend` to EC-specific recovery and transaction reply behavior. `ECRecPred` and `ECReadPred` implement recoverability/readability predicates using the erasure-code plugin's `minimum_to_decode()` requirements and the local shard identity.

## State and Persistence Behavior
Members include the parent listener, Ceph context, `ECSwitch`, read and RMW pipelines, recovery backend, erasure-code plugin reference, and immutable `stripe_info_t`. Persistence occurs through objectstore transactions and reads in the implementation. Omap methods expose a journal-aware view over on-disk omap and in-memory EC omap changes.

## Dependencies and Integration Points
It depends on EC common headers, extent cache, listener interfaces, EC types/utilities, `OSD`, `PGBackend`, erasure-code interfaces, bufferlists, scrub backend, and coroutine aliases. It is the bridge between `PrimaryLogPG`/PG backend logic and erasure-code shard IO.

## Risks and Test Signals
Risks include API contract drift between `ECCommon`, `PGBackend`, and `ECSwitch`, incorrect shard-size mapping for legacy EC objects, predicate mistakes for subchunk-capable plugins, and omap behavior for unsupported pools. Tests should cover predicate outcomes for enough/insufficient shards, shard offset mapping, encode/decode helper round trips, recovery handle lifecycle, omap unsupported return codes, and objectstore integration through mocked listeners/switchers.
