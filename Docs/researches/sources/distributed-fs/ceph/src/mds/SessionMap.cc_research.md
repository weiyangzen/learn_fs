# sources/distributed-fs/ceph/src/mds/SessionMap.cc

Purpose: Implements MDS session tracking, OMAP-backed persistence, legacy load migration, perf counters, request-load accounting, completed-request writeback, and session filtering.

Important APIs/functions: `SessionMap::load`, `_load_finish`, `load_legacy`, `_load_legacy_finish`, `save`, `_save_finish`, `save_if_dirty`, `mark_projected`, `mark_dirty`, `replay_dirty_session`, `replay_open_sessions`, `add_session`, `remove_session`, `set_state`, `touch_session`, `Session::check_access`, `notify_recall_sent`, `notify_cap_release`, and `SessionFilter::parse/match`.

Control flow: `load()` reads the sessionmap object's OMAP header and batched values using `Objecter`; `_load_finish()` decodes the header once, decodes value batches until `more_session_vals` is false, rebuilds `by_state`, and completes waiters. Missing OMAP header triggers legacy full-object loading, after which all sessions are marked dirty so the next save writes the OMAP format. `save()` writes the version header, dirty session keys, and removed session keys; it may truncate the old object data after legacy import.

State and persistence behavior: The durable store is object `mds<rank>_sessionmap` in the metadata pool with OMAP header `version` and per-session OMAP values keyed by entity name. `version`, `projected`, `committing`, and `committed` enforce journal/writeback ordering. `dirty_sessions` and `null_sessions` determine which OMAP values are set or removed. `save_if_dirty()` can persist dirty completed request/flush lists ahead of normal sessionmap version writeback.

Dependencies and integration points: Uses `MDSRank`, `Objecter`, `Finisher`, `MDCache`, `Capability`, `CDentry`, `CInode`, `MDSAuthCaps`, `PerfCounters`, and config keys such as `mds_sessionmap_keys_per_op`, `mds_session_metadata_threshold`, and decay rates. It calls `MDSRank::evict_client` when session metadata exceeds threshold.

Risks: The code aborts or damages the rank on corrupt sessionmap reads. `mark_projected` and `mark_dirty` must occur in the same global order; mismatches assert via projected versions. Large client metadata causes eviction/blocklisting. Legacy decode contains an old-format branch with delicate duplicate-session recovery. `Session::check_access` has subtle path handling for stray/snapshotted deleted directories.

Test signals: Cover OMAP load pagination, missing-header legacy upgrade, corrupt header/value handling, dirty/null key save batches, threshold eviction, completed-request preemptive saves, config-change decay reset, session filter parser errors, and replay of force-open sessions across versions.
