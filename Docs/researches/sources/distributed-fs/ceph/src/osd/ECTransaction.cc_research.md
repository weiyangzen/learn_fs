# sources/distributed-fs/ceph/src/osd/ECTransaction.cc

Purpose: `ECTransaction.cc` implements optimized EC transaction planning execution: converting high-level `PGTransaction` object operations into per-shard `ObjectStore::Transaction`s, EC-encoded writes, rollback metadata, shard version updates, and EC OMAP journal entries.

Important APIs and functions: `WritePlanObj` computes per-object `to_read`, `will_write`, cache invalidation, projected size, and parity-delta-write choice. `Generate` executes one object operation through delete/init/truncate/write/clone/attr/OMAP phases. `generate_transactions` drives `Generate` in plan order. OMAP helpers `accumulate_omap_updates`, `apply_omap_to_transactions`, `OmapCloneVisitor`, and `get_incomplete_ec_omap_log_entries` handle deferred OMAP behavior.

Control flow: planning maps RADOS-object extents to shard extents, aligns partial pages, adds reads for partial writes/truncates, and chooses conventional RMW or parity delta writes. Execution handles delete-first and object init, loads partial extents, truncates, overlays writes, performs clone-range rollback capture, encodes parity, writes selected shards, updates `written_map`, records append/rollback mod_desc, adjusts shard versions in OI, writes attrs, and journals or directly applies OMAP.

State and persistence: durable output is the per-shard ObjectStore transactions plus PG log `mod_desc`. Rollback persistence is through clone objects, rollback extents, xattr rollback, written shard sets, and PG log EC OMAP entries. `ECOmapJournal` receives in-memory entries so reads see log-only OMAP updates.

Dependencies and integration: depends on `ECUtil`, `PGTransaction`, `PGLog`, `OSDMap`, erasure-code plugin APIs, `ObjectContext`, and ObjectStore transaction methods. It is called by optimized `ECBackend`.

Risks: this file is correctness-critical. Risks include incorrect shard extent math, PDW choice with unavailable shards, failure to mark `written_shards`, stale OMAP visibility, clone handling missing incomplete OMAP log entries, and attr cache/OI shard-version races with in-flight writes.

Test signals: strong coverage includes partial overwrite RMW, parity delta writes, truncates, appends beyond current size, delete/recreate, clone/rename, temp object paths, nonprimary shard attr behavior, OMAP insert/remove/range/header/clear, rollback after failed subwrite, and mixed writable/readable shard sets.
