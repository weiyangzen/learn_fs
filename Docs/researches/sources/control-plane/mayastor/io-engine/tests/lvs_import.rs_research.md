# sources/control-plane/mayastor/io-engine/tests/lvs_import.rs

Purpose: stress/regression test for importing an LVS pool with many replicas and snapshots, verifying no volumes are lost or spuriously added.

Important APIs/types/functions: uses `Lvs::create_or_import`, `create_lvol`, `prepare_snap_config`, `create_snapshot`, `export`, and `lvols`. Constants create 100 replicas and 10 snapshots per replica on a 10 GB AIO file.

Control flow: prepares disk, creates LVS, records names of every replica and snapshot created, exports the pool, imports it again with the same args, collects imported lvol names, and compares set differences both ways.

State and persistence: relies on LVS on-disk metadata surviving export/import. Temporary disk file is `/tmp/disk0.img`. UUIDs and names are deterministic.

Dependencies and integration points: LVS metadata import/export, snapshot metadata, AIO bdev, `HashSet` comparison, Mayastor multi-thread reactor settings.

Risks and edge cases: creates 1100 volumes and can be slow or metadata-capacity sensitive. Fixed disk path. It prints timing but has no duration assertion.

Test signals: strong persistence signal for large-volume LVS import correctness.
