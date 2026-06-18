
# sources/distributed-fs/ceph-client/net/sched/em_text.c

## Purpose

`em_text.c` implements a textsearch-backed ematch. It scans a configured skb byte range for a pattern using a named Linux textsearch algorithm, enabling TC ematch users to match embedded byte strings without writing a full classifier.

## Important APIs, Types, and Functions

`struct text_match` stores from/to layer and offset boundaries plus a `struct ts_config`. `em_text_change()` validates range config, prepares or autoloads the textsearch algorithm, and stores compiled state. `em_text_match()` resolves the start/end layer pointers and calls `skb_find_text()`. `em_text_destroy()` destroys the textsearch config and frees state. `em_text_dump()` emits algorithm name, offsets, layers, pattern length, and pattern bytes.

## Control Flow

Configuration validates that the payload includes the pattern, that from-layer is not after to-layer, and that offsets are ordered within the same layer. It first tries `textsearch_prepare()` without autoload; on `-ENOENT` it drops RTNL, retries with `TS_AUTOLOAD`, then returns `-EAGAIN` after successful autoload so the caller can replay under normal locking. Runtime match converts layer-relative boundaries to skb-data offsets and returns true when `skb_find_text()` finds the pattern.

## State and Persistence Behavior

Compiled textsearch state is per ematch instance and owned by `m->data`. The textsearch algorithm module/config is held by `ts_config` and released on destroy. No match results are cached.

## Dependencies and Integration Points

It depends on the kernel textsearch API, ematch core, skb range helpers, RTNL behavior around module autoload, and `tc_em_text.h` payload format.

## Risks and Edge Cases

The autoload path deliberately returns `-EAGAIN` after loading so callers must retry. Range calculations depend on valid layer base pointers and can fail closed when a header is unavailable. Textsearch cost depends on selected algorithm and scan window.

## Test Signals

Test multiple textsearch algorithms, module autoload retry, same-layer and cross-layer ranges, invalid ordering, truncated skb ranges, dump round trips, and negative matches.
