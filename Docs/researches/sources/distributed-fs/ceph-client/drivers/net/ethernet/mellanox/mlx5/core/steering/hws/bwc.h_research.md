# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc.h

## Purpose
`bwc.h` declares the compatibility matcher/rule data structures and APIs for HWS BWC mode. It defines how BWC queues, resizable matcher sizes, action-template arrays, and rule lists are represented across simple and complex matchers.

## Important APIs, Types, And Functions
Constants define the initial matcher size, resize step, 70 percent rehash threshold, burst polling threshold, maximum attached action templates, maximum actions, and polling timeout. `enum mlx5hws_bwc_matcher_type` distinguishes standalone simple matchers, first complex matchers, and complex submatchers. `struct mlx5hws_bwc_matcher_size` stores size log and atomic counters. `struct mlx5hws_bwc_matcher` owns the underlying matcher, match template, action-template array, optional complex data, RX/TX sizes, and per-queue rule lists. `struct mlx5hws_bwc_rule` wraps a rule, links subrules, stores flow source and queue assignment, and tracks RX/TX skipping.

The header exports simple matcher/rule operations, generic BWC create/destroy/update functions, rule-attribute filling, queue polling, and inline queue-count/queue-ID mapping.

## Control Flow And State
The queue mapping reserves the first send queue as control and splits the remaining queues into regular HWS queues and BWC queues; BWC queue IDs are offset by the number of BWC queues. Matcher state is mutable because action templates and size logs grow dynamically and shrink when rule counts return to zero.

## Dependencies And Integration Points
It depends on `context.h` for capability checks and queue count, HWS table/matcher/rule/action types, and `bwc_complex.h` for complex matcher extension. The structures are inspected by debug dumping and operated on by `bwc.c` and `bwc_complex.c`.

## Risks And Test Signals
Risks are incorrect queue math when `ctx->queues` is small or BWC support is absent, atomic size counters diverging from rule lists, and callers using simple helpers on complex-first matchers incorrectly. Tests should validate queue count mapping, matcher type dispatch, rule list ownership, and teardown with nonzero counters.
