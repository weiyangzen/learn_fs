# sources/distributed-fs/ceph-client/block/bio-integrity-auto.c

## Purpose

`bio-integrity-auto.c` automatically generates and verifies block integrity metadata for bios whose submitter did not provide protection information. It lets PI-capable devices protect ordinary block users and moves expensive read verification out of interrupt context.

## Important APIs, Types, And Functions

`struct bio_integrity_data` embeds the target `bio`, saved data iterator, work item, integrity payload, and one metadata vector. Allocation uses `bid_slab` and `bid_pool`; verification uses `kintegrityd_wq`.

Important functions are `bio_integrity_prep()`, `__bio_integrity_endio()`, `blk_flush_integrity()`, `bio_integrity_finish()`, `bio_integrity_verify_fn()`, and `blk_integrity_auto_init()`.

## Control Flow, State, And Persistence

`bio_integrity_prep()` allocates the embedded payload container, attaches it to the bio with `bio_integrity_init()`, marks `BIP_BLOCK_INTEGRITY`, allocates a metadata buffer, sets default check flags if required, and either generates metadata immediately for writes or saves the original `bio->bi_iter` for read verification.

`__bio_integrity_endio()` checks successful read completions with enabled guard/reference/application tag checks. Those are queued to `kintegrityd_wq` and completion is postponed by returning false. The work item verifies metadata, updates `bio->bi_status`, frees the payload and buffer, and calls `bio_endio()` again. Other completions free integrity state synchronously and continue.

## Dependencies And Integration Points

The file depends on block integrity profiles, T10 PI helpers, workqueues, and common block internals. It is invoked by submit-time integrity preparation and `bio_endio()` integrity completion. `blk_flush_integrity()` provides a drain hook for queued verification work.

## Risks And Test Signals

The saved iterator is critical because drivers may advance bio iterators before completion. Ownership is exclusive: this path clears `bio->bi_integrity` and `REQ_INTEGRITY` in `bio_integrity_finish()`. Test PI-capable reads/writes without user metadata, verification failures, interrupt-context completion, workqueue drain, and memory-pressure behavior through the mempool.
