# sources/distributed-fs/ceph/src/osd/ECBackendL.h

## Purpose

Declares the legacy EC PG backend interface and its nested recovery/read/write support classes. It is the header contract for code that still routes erasure-coded PG operations through the legacy `ECLegacy::ECCommonL` path while exposing `PGBackend`-style recovery, read, write, scrub, and predicate APIs.

## Important APIs, Types, and Functions

`ECBackendL` derives from `ECCommonL` and exposes recovery (`open_recovery_op`, `run_recovery_op`, `recover_object`, `dump_recovery_info`), message handling (`_handle_message`, `can_handle_while_inactive`), sub-op handlers, read helpers (`objects_read_local`, `objects_read_async`, `objects_read_and_reconstruct`), write submission (`submit_transaction`, `call_write_ordered`), and scrub/stat helpers. Nested `RecoveryBackend` stores `RecoveryOp` state, read pipeline references, hinfo registry access, and virtual `commit_txn_send_replies()`. `ECRecoveryBackend` binds that abstraction to `PGBackend::Listener`. `ECRecPred` and `ECReadPred` expose recoverability/readability predicates based on the erasure-code plugin.

## Control Flow and Data Flow

The class aggregates `ReadPipeline`, `RMWPipeline`, and `ECRecoveryBackend`. Public PGBackend-facing methods delegate to the nested pipelines/backends, while backend-specific implementations in the `.cc` file supply objectstore access and listener callbacks. `RecoveryOp` carries `hoid`, version, missing shards, `ObjectRecoveryInfo`, `ObjectRecoveryProgress`, decoded `returned_data`, xattrs, hinfo, object context, waiting push shards, and the currently requested extent.

## State and Persistence Behavior

The header defines in-memory state only. Persistent effects are deferred to `submit_transaction`, sub-write handling, recovery push handling, and scrub implementations in the `.cc` file. Notable in-memory state includes `parent`, `cct`, `switcher`, `ec_impl`, `sinfo`, `unstable_hashinfo_registry`, pipeline queues/maps, and `recovery_ops`.

## Dependencies and Integration Points

The contract depends on `ECCommonL.h`, `PGBackend.h`, `OSD.h`, `ErasureCodeInterface`, `ECUtilL`, `ECTransactionL`, `ECExtentCacheL`, and `ECSwitch`. It is instantiated by `ECSwitch` and connected to `PGBackend::Listener`; it interoperates with legacy recovery messages declared in `ECMsgTypes` and object context/log types from the OSD layer.

## Risks and Edge Cases

The header mixes public PGBackend methods, nested recovery internals, and friendship, so ownership boundaries are weak. `RecoveryBackend` stores raw listener/backend pointers and references to shared pipeline/stripe state, making lifetime order important. `object_size_to_shard_size()` preserves `uint64_t::max()` as a sentinel. `ECRecPred` and `ECReadPred` depend on `minimum_to_decode()` semantics and shard id conversion; incorrect acting/missing sets directly change peering decisions.

## Test Signals

Tests should compile both legacy and non-legacy users, assert recoverability/readability predicates for k+m layouts with missing shards, verify `object_size_to_shard_size()` alignment including sentinel max, exercise recovery state dump formatting, and drive interval-change cleanup through `on_change()` and `clear_recovery_state()`.
