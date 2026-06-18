# sources/distributed-fs/ceph-client/fs/ubifs/log.c

## Purpose

`log.c` manages the UBIFS journal log: the fixed flash area that records references to bud LEBs and commit-start nodes. It tracks bud membership, writes reference nodes, controls log head/tail movement during commit, releases old buds only after commit safety is established, and can consolidate a cluttered log after repeated failed commits.

## Important APIs, Types, And Functions

Public APIs are `ubifs_search_bud()`, `ubifs_get_wbuf()`, `ubifs_add_bud()`, `ubifs_add_bud_to_log()`, `ubifs_log_start_commit()`, `ubifs_log_end_commit()`, `ubifs_log_post_commit()`, and `ubifs_consolidate_log()`. Internal helpers include `empty_log_bytes()`, `remove_buds()`, `done_already()`, `destroy_done_tree()`, `add_node()`, and `dbg_check_bud_bytes()`.

The main state is `c->buds` rb-tree, each journal head's `buds_list`, `c->old_buds`, `c->bud_bytes`, `c->cmt_bud_bytes`, `c->lhead_lnum`, `c->lhead_offs`, `c->ltail_lnum`, `c->log_bytes`, `c->min_log_bytes`, and authentication hash state in `c->log_hash` and `jhead->log_hash`.

## Control Flow

`ubifs_add_bud_to_log()` allocates a `struct ubifs_bud` and `UBIFS_REF_NODE`, takes `c->log_mutex`, checks read-only state, ensures enough empty log bytes remain for the next commit, enforces `c->max_bud_bytes`, optionally requests background commit, wraps the log head if needed, unmaps the next log LEB at offset zero, maps empty target buds before referencing them, writes the ref node, updates authentication hash state, advances `lhead_offs`, and adds the bud to both rb-tree and journal-head list.

Commit start writes a `UBIFS_CS_NODE` plus reference nodes for currently open journal heads into a fresh log LEB, resets the log hash, pads to `min_io_size`, advances the log head, and calls `remove_buds()`. `remove_buds()` preserves buds still pointed to by active write buffers by moving their start offset forward, while closed buds are moved to `old_buds` so they cannot be garbage-collected until recovery no longer needs them. Commit end moves `ltail_lnum`, restores `min_log_bytes`, subtracts committed bud bytes, validates accounting, and writes the master node. Post-commit returns old buds to lprops and unmaps old log LEBs.

`ubifs_consolidate_log()` is a recovery-oriented repair path. It scans from tail to head, copies the first commit-start node and only the newest unique ref nodes into compacted log LEBs, pads and changes LEBs as needed, unmaps the remaining old log area, and updates `lhead_lnum`/`lhead_offs`.

## State And Persistence Behavior

The log is the persistent description of journal buds needed for replay. Ref nodes are written before a bud becomes visible in in-memory bud structures. Empty target buds are explicitly mapped before being referenced to avoid recovery seeing stale garbage from an unmapped but not physically erased LEB. Old log LEBs and old buds are not unmapped/returned until after commit completes, preserving recovery from interrupted commits.

## Dependencies And Integration Points

`log.c` integrates with journal reservation (`ubifs_add_bud_to_log()` is called when a journal head switches LEBs), commit logic, master-node persistence, UBI wrappers from `io.c`, scanning for consolidation, lprops return paths, background commit requests, authentication hash helpers, rb-trees, and per-journal-head write buffers.

## Risks And Edge Cases

Important risks are off-by-one log head/tail wraparound, incorrect `bud_bytes` accounting, referencing an unmapped empty bud, reclaiming old buds before commit is fully safe, and failing to preserve open half-indexed buds at commit. Consolidation must avoid duplicate stale refs and must not fill the entire log; it returns `-EINVAL` if compaction still leaves the head at the previous head LEB. Authentication hash state must be copied to each journal head after ref writes and commit-start refs.

## Test Signals

Test signals include journal-head switching, log wraparound, max-bud-byte commit triggers, background commit threshold behavior, commit interruption and recovery, half-indexed bud preservation, repeated failed commits followed by log consolidation, authenticated journal replay, and debug `bud_bytes` checks.
