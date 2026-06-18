# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-layout.c

## Purpose

`dht-layout.c` owns DHT layout allocation, lookup, refcounting, disk-xattr serialization/deserialization, layout merge, sorting, anomaly detection, normalization, mismatch checks, preset file layouts, and layout indexing. It translates between persistent on-disk directory layout xattrs and the in-memory hash range table used to route names to subvolumes.

## Important APIs, Types, and Functions

`dht_layout_new`, `dht_layout_ref`, `dht_layout_unref`, `dht_layout_get`, and `dht_layout_set` manage layout lifetime and inode attachment. `dht_layout_search` hashes a name and finds the matching range. `dht_layouts_init` creates one-entry preset file layouts for each child. `dht_disk_layout_extract` and `dht_disk_layout_extract_for_subvol` serialize a layout entry to four big-endian words: commit hash, hash type, start, and stop. `dht_layout_merge` and internal `dht_disk_layout_merge` parse child xattrs into layout entries. `dht_layout_sort`, `dht_layout_sort_volname`, `dht_layout_anomalies`, `dht_layout_missing_dirs`, `dht_layout_normalize`, `dht_dir_has_layout`, `dht_layout_dir_mismatch`, `dht_layout_preset`, and `dht_layout_index_for_subvol` implement validation and lookup helpers.

## Control Flow

Directory lookup/self-heal allocates a layout sized to child count, then calls `dht_layout_merge` once per child lookup. The merge path records child errors, handles missing xattrs as nonfatal entries, parses valid disk layouts, updates the aggregate `layout->commit_hash`, and marks it invalid if children disagree. Normalization sorts ranges, counts holes/overlaps/missing/down/misc/no-space anomalies, and returns negative for range holes/overlaps or positive counts for missing directories. Routing calls hash the basename through `dht_hash_compute` and scans the sorted or unsorted layout for a containing range.

## State and Persistence Behavior

The persistent representation is the DHT layout xattr stored per directory child. All numeric fields are big-endian on disk. Runtime layouts hold refs in inode ctx; preset file layouts belong to `conf->file_layouts` and are not freed by `dht_layout_unref`. Layout generation and commit hash connect in-memory cache validity to volume topology and rebalance completion.

## Dependencies and Integration Points

The file integrates with hash computation, inode context helpers, lookup/self-heal code, disk layout xattr names from `dht_conf_t`, and disk-usage/layout-error filtering. Directory self-heal relies on anomaly counts and mismatch detection to decide whether to fix layout xattrs. File operations rely on preset layouts to identify the cached subvolume for regular files.

## Risks and Test Signals

Risks include malformed disk layout lengths, endian mistakes, accepting zero-width/nonparticipating ranges incorrectly, stale commit hashes, preset-layout refcount misuse, sort comparator behavior for zero ranges, and mismatch checks when xattrs are absent but in-memory state says a child participates. Tests should parse/extract known layout xattrs, detect holes/overlaps/missing/down/no-space entries, validate commit-hash invalidation across disagreeing children, search boundary hashes at start/stop edges, handle user-set hash type, reject invalid hash types, verify preset file layout lifetime, and compare on-disk vs in-memory layout for self-heal decisions.
