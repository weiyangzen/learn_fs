# sources/distributed-fs/ceph/src/osdc/SplitOp.cc

## Purpose

`SplitOp.cc` implements client-side split/balanced read optimization for Ceph OSD reads. It can split eligible reads across erasure-coded data shards or replicated-pool replicas, submit parallel sub-operations through `Objecter`, detect torn reads with internal version checks, assemble synthetic replies, and fall back to the normal primary path when the optimization is unsafe or unhelpful.

## Important APIs, types, and functions

The implementation defines `osdcode()` for converting negative OSD returns into `boost::system::error_code`, `kReplicaMinShardReads`, EC and replica implementations of `init_reference_sub_read()`, `init_read()`, `assemble_buffer_read()`, `assemble_buffer_sparse_read()`, and `version_mismatch()`, plus shared `SplitOp::assemble_rc()`, `complete()`, `protect_torn_reads()`, `init()`, `prepare_single_op()`, and `create()`.

Anonymous helpers validate eligibility: `is_single_chunk()` detects EC reads that fit in one chunk, `validate_flags()` requires `CEPH_OSD_FLAG_BALANCE_READS`, rejects writes and Crimson pools, `validate_operations()` accepts reads/sparse reads plus selected primary-only metadata ops, rejects zero-length reads and unsupported opcodes, and `validate()` combines pool type and `osd_min_split_replica_read_size` checks.

## Control flow

`SplitOp::create()` is the entry point from `Objecter` submission. It rejects missing pools, snapshot operations, pools without `FLAG_CLIENT_SPLIT_READS`, invalid flags, invalid operations, and undersized replica reads. A single EC chunk can be rewritten by `prepare_single_op()` to use `EC_DIRECT_READ | FORCE_OSD` without constructing a split object. Otherwise it creates `ECSplitOp` or `ReplicaSplitOp`, calculates the target, initializes a reference sub-read, initializes per-op sub-reads, rejects if only one sub-read remains, adds the parent op to the split-op session, appends internal version requests, prepares child read ops, forces OSD targets, submits them, and records child tids in `op->split_op_tids`.

Sub-op finishers self-delete through the `Context` lifecycle and only record return codes. The `shared_ptr<SplitOp>` retained by each finisher keeps the split operation alive until all child contexts release it; derived destructors call `complete()`. `complete()` assembles return status, builds synthetic `out_ops`, reconstructs read/sparse-read data, preserves legacy preallocated `outbl` behavior, runs `Objecter::process_op_reply_handlers()`, and calls `op_post_split_op_complete()`. Negative returns or version mismatch lead to `-EAGAIN`, which is used to retry on the ordinary path.

## State and persistence behavior

All state is transient: `orig_op`, `sub_reads`, per-sub-read `ObjectOperation`, return codes, response buffers, optional sparse extent maps, optional internal-version buffers, reference index, abort flag, and generated child tids. No persistent data is written. Correctness depends on OSD-side object versions and OSDMap acting sets captured during target calculation.

## Dependencies and integration points

The file depends on `Objecter.h`, `SplitOp.h`, OSD pool/shard metadata, `ceph_assert`, buffer encoding/decoding, and OSD flags. It integrates tightly with `Objecter::_calc_target()`, `prepare_read_op()`, `_op_submit()`, `add_op_to_splitop_session()`, `process_op_reply_handlers()`, and `op_post_split_op_complete()`. OSD-side support is signaled by `CEPH_OSD_FLAG_EC_DIRECT_READ`, `CEPH_OSD_FLAG_FAIL_ON_EAGAIN`, and pool `FLAG_CLIENT_SPLIT_READS`.

## Risks and edge cases

The EC path assumes shard index conversion through `pg_pool_t::get_shard()` and `target.acting` remain aligned; missing or down OSDs abort to fallback. Replica `init_reference_sub_read()` counts valid OSDs but chooses `rand() % valid_osd_count` and then treats it as an acting index, which is risky if invalid OSDs are interspersed in `target.acting`. `ECSplitOp::init_read()` comments discuss zero-length reads being rejected earlier, but it still relies on assertion. Sparse assembly assumes per-shard extent maps and buffers advance consistently. The destructor-driven completion pattern is subtle: setting `abort` before fallback is necessary to avoid completing abandoned split objects.

## Test signals

Tests should cover EC single-chunk direct read, multi-shard dense and sparse reads, replica split threshold behavior, missing/down OSD fallback, unsupported operations, snapshot rejection, reads with primary-only ops, object version mismatch retry, `outbl` preallocated-buffer compatibility, and cancellation of child tids. Existing references in `Objecter.cc` show split reads are counted, cancelled through `split_op_tids`, and retried or completed through `op_post_split_op_complete()`.
