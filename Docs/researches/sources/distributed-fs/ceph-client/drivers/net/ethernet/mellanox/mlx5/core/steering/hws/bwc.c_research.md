# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc.c

## Purpose
`bwc.c` implements the backward-compatible HWS API layer for matcher and rule creation. It creates resizable HWS matchers behind a compatibility interface, manages action-template attachment, chooses BWC queues, synchronously polls rule operations, and grows or shrinks matchers by rehashing rules.

## Important APIs, Types, And Functions
Public entry points include `mlx5hws_bwc_matcher_create()`, `mlx5hws_bwc_matcher_destroy()`, `mlx5hws_bwc_rule_create()`, `mlx5hws_bwc_rule_destroy()`, `mlx5hws_bwc_rule_action_update()`, `mlx5hws_bwc_queue_poll()`, and the simple matcher/rule helpers also used by `bwc_complex.c`. Internal helpers initialize matcher attributes, lock BWC queues, create and destroy simple matchers, extend action-template arrays, determine rehash thresholds, move rules during resize, and maintain per-RX/TX rule counters.

## Control Flow And State
Matcher creation verifies BWC support, initializes RX/TX size logs and atomics, then chooses simple or complex creation based on whether the match mask fits a single definer. Simple matchers allocate per-BWC-queue rule lists, create a dummy action template, build one match template, and create a resizable HWS matcher.

Rule creation allocates an HWS rule wrapper, derives skip-RX/TX from flow source, chooses a random BWC queue index, locks that queue, finds or attaches an action template matching the requested action types, increments counters, possibly rehashes, creates the HWS rule, polls completion synchronously, and links the rule into the queue list. Non-busy insertion failures trigger one forced rehash retry. Destruction synchronously deletes the HWS rule, removes it from the list, decrements counters, and if the matcher becomes empty, locks all BWC queues and shrinks back to the initial size.

## Dependencies And Integration Points
The file depends on context BWC queue partitioning, HWS matcher/rule APIs, action and match template APIs, complex matcher helpers, send queue polling/flushing, and firmware capability limits. Complex matchers reuse the simple rule/matcher machinery for each submatcher.

## Risks And Test Signals
Risks include deadlocks during queue-lock release/reacquire around all-queue rehash, partial rehash failure because old matcher rollback is not possible, action-template leaks after attach failure, queue polling timeouts, and counter/list inconsistency on create/destroy failures. Test signals include high collision insertion, rehash growth and shrink, concurrent create/destroy on different BWC queues, action update with new action templates, queue full/timeout injection, and complex/simple selection coverage.
