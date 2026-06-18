# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume-index.c

## Purpose
Implements the primary in-memory UDS volume index, mapping record names to virtual chapters. It uses delta indexes to store compact chapter hints, splits sparse indexes into hook and non-hook subindexes, lazily flushes invalid entries, persists per-zone index streams, and provides record-level mutation operations.

## Important APIs, Types, And Functions
Public functions include `uds_make_volume_index()`, `uds_free_volume_index()`, `uds_compute_volume_index_save_blocks()`, `uds_get_volume_index_zone()`, `uds_is_volume_index_sample()`, `uds_lookup_volume_index_name()`, `uds_get_volume_index_record()`, `uds_put_volume_index_record()`, `uds_remove_volume_index_record()`, `uds_set_volume_index_record_chapter()`, `uds_set_volume_index_open_chapter()`, `uds_set_volume_index_zone_open_chapter()`, `uds_load_volume_index()`, `uds_save_volume_index()`, and `uds_get_volume_index_stats()`.

Private structures include `sub_index_parameters`, `split_config`, `chapter_range`, serialized `sub_index_data` (`MI5-0005`), and serialized `volume_index_data` (`MI6-0001`). Core helpers compute subindex sizing, split sparse configurations, extract address/list bits from names, convert virtual/index chapter numbers, lazily flush invalid delta entries, restore/save subindexes, and initialize delta indexes.

## Control Flow
Configuration computes delta-list count, address bits, chapter bits, expected memory, and target free space. Dense indexes initialize only `vi_non_hook`. Sparse indexes allocate per-zone hook mutexes, split configuration so sampled hook records are kept for sparse chapters and non-hook records cover dense chapters, then initialize both subindexes with separate delta-index tags.

Record lookup picks the hook subindex for sampled names and non-hook otherwise, derives list and zone from record-name bits, lazily flushes old entries if the delta list has not caught up to the zone's low virtual chapter, and returns a `volume_index_record` that can be mutated. Hook lookups and mutations use a per-zone mutex because sparse-cache triage can perform concurrent read-only hook lookups while normal request processing lazily mutates delta lists.

Saving writes optional sparse header, per-subindex headers with nonce/chapter range/list range, per-list flush chapters, delta-index data, guard lists, and flushes one writer per zone. Loading validates magic, nonce consistency, sparse sample rate consistency, restores flush ranges and delta-index streams, then checks guard lists.

## State And Persistence
Each subindex stores `flush_chapters`, per-zone low/high virtual chapter ranges, delta-index storage, nonce, bit masks, chapter/list counts, and memory accounting. Chapter numbers are stored in truncated index form and converted back to virtual form relative to each zone's low chapter. Old entries are removed lazily during list walks. Early flush can advance a zone's low chapter when delta-zone memory exceeds `max_zone_bits`, trading dedupe history for bounded memory.

## Dependencies And Integration Points
Depends on configuration, geometry, hash utilities, delta-index APIs, numeric encoding, thread/mutex utilities, logging, and allocation. `index.c` uses it for zone routing, request lookup/update/delete, chapter rollover, sparse-cache membership triage, rebuild replay, and stats. `index-layout.c` asks it for save size and delegates save/load.

## Risks
The name-bit partitioning, sparse sample-rate split, and zone mapping must remain stable across saves and reduced-volume configurations. Lazy flushing means lookups are mutating operations; missing hook mutex coverage can race with sparse-cache triage. Collision records disambiguate names only when needed, and overflow can drop entries, reducing dedupe hits. Early flush changes valid chapter ranges under memory pressure, so tests must account for controlled loss of old records.

## Test Signals
Test dense and sparse initialization, sample/non-sample routing, zone selection stability, put/get/update/remove, collision records, overflow handling, lazy flush of invalid entries, open-chapter range advancement, early flush under memory pressure, save/load with guard-list validation, bad magic/nonce/sample-rate failures, stats aggregation, and rebuild replay behavior.
