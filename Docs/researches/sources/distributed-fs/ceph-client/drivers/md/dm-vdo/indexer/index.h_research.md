# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index.h

## Purpose
Defines the internal high-level UDS index structures and functions shared by session, layout, sparse cache, open chapter, volume, and volume-index code.

## Important APIs, Types, And Functions
`index_callback_fn` is the callback used by the index to return completed requests to the session layer. `struct index_zone` stores per-zone open and writing chapters plus oldest/newest virtual chapter counters. `struct uds_index` stores persistent layout, volume index, volume object, zones, global chapter counters, save flags, writer, callback, triage queue, and flexible array of zone queues. `enum request_stage` selects triage, index, or message queueing.

The header exposes `uds_make_index()`, `uds_save_index()`, `uds_free_index()`, `uds_replace_index_storage()`, `uds_get_index_stats()`, `uds_enqueue_request()`, and `uds_wait_for_idle_index()`.

## Control Flow
Session code creates the index with a load context and callback, launches requests by enqueueing them, drains with `uds_wait_for_idle_index()`, saves through `uds_save_index()`, and frees through `uds_free_index()`. Sparse-cache code receives `struct index_zone` pointers so it can coordinate cache updates per zone.

## State And Persistence
The header declares both mutable runtime state and fields that mirror persistent chapter state (`oldest_virtual_chapter`, `newest_virtual_chapter`, `last_save`, saved-open-chapter flag). Actual serialization is implemented by `index-layout.c`.

## Dependencies And Integration Points
Includes layout, session, open chapter, volume, and volume-index headers. This makes it a central internal integration header rather than a public client API.

## Risks
Because the flexible array of queue pointers is counted by `zone_count`, allocation must use `vdo_allocate_extended()` consistently. Direct field access by multiple files makes invariants about chapter counters and save flags easy to break if future code bypasses existing helper paths.

## Test Signals
Build coverage should catch structural changes. Runtime tests should validate zone-count allocation, queue dispatch by stage, save/free ordering, and interactions with sparse-cache updates.
