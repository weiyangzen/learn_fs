# sources/distributed-fs/ceph/src/osd/ECBackend.cc

## Purpose
`ECBackend.cc` implements the classic erasure-coded PG backend. It handles EC sub-op messages, read reconstruction, read-modify-write submission, recovery pushes, deep scrub reads, local/direct reads, and EC omap journal overlays for pools that support omap.

## Important APIs, Types, and Control Flow
The constructor wires `ReadPipeline`, `RMWPipeline`, `ECRecoveryBackend`, `ECSwitch`, `ErasureCodeInterface`, and `stripe_info_t`, then asserts the plugin's data chunk count and chunk size match the pool stripe width. `_handle_message()` dispatches EC write/read subops, replies, and PG push/push-reply messages. Recovery flows through `open_recovery_op()`, `recover_object()`, `run_recovery_op()`, `ECRecoveryBackend::run_recovery_op()`, `handle_recovery_push()`, and `commit_txn_send_replies()`.

For writes, `submit_transaction()` creates an `ECClassicalOp`, computes a write plan, and starts the RMW pipeline. `handle_sub_write()` applies replica-side transactions, updates stats and missing/log state, appends EC omap journal delete records when needed, registers a commit callback, queues transactions, and marks local apply. `handle_sub_write_reply()` tracks pending commits and finishes the RMW pipeline when all shards commit. For reads, `objects_read_async()` normalizes requested extents, calls `objects_read_and_reconstruct()`, slices reconstructed results back into caller buffers, and completes per-read contexts. `handle_sub_read()` reads shard data, attrs, omap headers, and omap entries; `handle_sub_read_reply()` merges responses, handles errors, determines whether enough shards are available via `minimum_to_decode()`, resends reads if alternate shards can help, and completes the read pipeline in order.

## State and Persistence Behavior
Durable state is stored through `ObjectStore::Transaction` and objectstore reads/writes via `ECSwitch`. The backend maintains volatile pipeline maps, recovery ops, temp-object tracking through the parent/switcher, and EC omap journal overlay state. Omap helpers merge in-memory journal updates and removed ranges with on-disk objectstore omap values for iterate, get, get-values, header, and key-check operations. `on_change()` clears the journal, resets pipelines, and clears recovery state.

## Dependencies and Integration Points
It depends on EC common/pipeline utilities, erasure-code plugin interface, EC message types, recovery messages, `PrimaryLogPG`, objectstore, scrub backend, tracing, and `ECSwitch`. It integrates tightly with `PGBackend::Listener` for log updates, stats, message sending, transaction queuing, recovery scheduling, OSDMap epochs, and scrub counters.

## Risks and Test Signals
Risks include minimum-shard calculations, read ordering under redundant/fast reads, suppressing harmless fast-read `ENOENT` without masking real corruption, omap overlay range semantics, transaction/log ordering, missing-state behavior during async recovery, and iterator erasure bugs in omap filtering. Tests should cover degraded reads, redundant reads with late errors, direct local reads, subchunk reads, RMW writes across data/parity shards, recovery push accounting, omap journal update/delete/range overlays, deep scrub digest behavior, error injection paths, and `on_change()` cleanup.
