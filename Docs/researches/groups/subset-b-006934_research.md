# subset-b-006934 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECExtentCacheL.h -->
## sources/distributed-fs/ceph/src/osd/ECExtentCacheL.h

Purpose: `ECExtentCacheL.h` defines the legacy EC read-modify-write extent cache used by the ECLegacy pipeline to pipeline overlapping partial overwrites without dropping data needed by earlier operations. It models cached object extents as intrusive objects owned by write pins, so a cached/pending interval remains live until the write operation that completes last releases its pin.

Important APIs and types: `ECLegacy::extent_set` and `extent_map` are interval containers over logical offsets and `bufferlist` payloads. `ECExtentCacheL::write_pin` is the public pin handle. `open_write_pin`, `reserve_extents_for_rmw`, `get_remaining_extents_for_rmw`, `present_rmw_update`, and `release_write_pin` form the write pipeline contract. Internally, `extent` tracks offset, length, optional data, parent object set, and parent pin; `object_extent_set` keeps per-object intrusive sets; `pin_state` owns the list of extents pinned by a write.

Control flow: callers open a write pin, reserve write/read intervals, read only the returned missing intervals, then present read-modify-write results. `traverse_update` is the core mutation algorithm: it walks overlapping ranges, splits head/tail fragments, moves ownership to the new pin when required, and optionally replaces pending intervals with concrete buffers.

State and persistence: the cache is entirely in-memory. State lives in intrusive containers, and correctness depends on every linked `extent` being in both its object set and pin list until `release_pin` unlinks and deletes it. It persists no on-disk metadata; it protects in-flight EC overwrite state.

Dependencies and integration: this legacy cache is used from `ECCommonL`/legacy RMW code and depends on `hobject_t`, Ceph interval containers, `bufferlist`, Boost intrusive set/list, and ordered write invariants supplied by higher layers.

Risks: ownership invariants are assertion-heavy and memory-unsafe if violated; `new`/`delete` and intrusive hooks make missed unlink paths dangerous. The design assumes no concurrent read/write mix for an object and ordered writes. Any change to RMW ordering or pin lifetime can expose stale or missing buffers.

Test signals: useful tests exercise overlapping writes, pending-to-present transitions, release cleanup of empty object caches, split head/tail ranges, and assertion behavior for invalid calls such as presenting unreserved extents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECExtentCacheL.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECInject.cc -->
## sources/distributed-fs/ceph/src/osd/ECInject.cc

Purpose: `ECInject.cc` implements fault-injection controls for EC read, write, and parity-read paths. It lets tests force medium errors, missing shards, dropped writes, simulated OSD-down events, aborts, and parity read behavior for targeted objects or wildcard objects.

Important APIs and functions: `read_error`, `write_error`, and `parity_read` configure injections. `clear_read_error`, `clear_write_error`, and `clear_parity_read` remove them. `test_read_error0/1`, `test_write_error0/1/2/3`, and `test_parity_read` are called by backend paths to decide whether to alter behavior. `test_error` is the shared countdown/duration evaluator.

Control flow: configuration normalizes wildcard object names by setting hash zero and, for some write error types, collapses the shard to `NO_SHARD`. Test functions look up the exact object first, then a wildcard variant. Each match decrements the `when` counter until active, then decrements `duration` and erases exhausted injections. Type-0 write injection is multi-stage: it records the client `reqid`, injects a one-shot dropped shard write, and later fails the retried request.

State and persistence: all injection state is process-local static data protected by a `ceph::recursive_mutex`: maps of object to `(when, duration)`, a type-0 shard map, a retry `reqid` set, and a parity-read set. Nothing is persisted; state disappears on process restart.

Dependencies and integration: it depends on `ghobject_t`, `hobject_t`, `osd_reqid_t`, `shard_id_t`, and Ceph mutex utilities. EC read/write/recovery code calls the test functions to simulate failure modes.

Risks: static global state can leak between tests if not cleared. Wildcard handling mutates object names and hashes, so inconsistent normalization can miss injections. Type-0 write injection has coupled state across maps/sets; partial cleanup would make later writes behave unexpectedly.

Test signals: unit or integration tests should cover countdown semantics, wildcard matching, automatic removal after duration, type-0 retry failure, type-1 chaining into type-2 down injection, and clear functions reporting remaining injections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECInject.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECInject.h -->
## sources/distributed-fs/ceph/src/osd/ECInject.h

Purpose: `ECInject.h` declares the EC fault-injection interface used by test and backend code. It exposes configuration, clearing, and runtime predicate functions without exposing the static state held in `ECInject.cc`.

Important APIs and types: the public namespace contains `read_error`, `write_error`, `parity_read`, `clear_read_error`, `clear_write_error`, `clear_parity_read`, and predicate functions for read types 0/1, write types 0/1/2/3, and parity reads. The declarations use `ghobject_t` when shard identity matters and `hobject_t` when shard-independent matching is intended.

Control flow: callers configure an injection with object, type, activation delay, and duration, then backend paths call the matching `test_*` function at the behavior point. Clear APIs remove configured state by object/type.

State and persistence: the header defines no state. Its contract implies implementation-side process-local mutable state with countdown semantics. No on-disk or PG-log persistence is involved.

Dependencies and integration: includes `common/hobject.h` and `osd_types.h`, making it part of the OSD EC backend support surface. Admin/test paths can configure injections, while EC read/write paths consume the predicates.

Risks: the API uses integer `type` values rather than strongly typed enums, so call sites must preserve the implicit type table. Header comments are absent here, so users need the `.cc` implementation or external documentation to know type meanings.

Test signals: compile-time coverage is minimal; behavioral coverage must come from tests that call each declaration through the backend paths and verify the injected effects, not just return strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECInject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECListener.h -->
## sources/distributed-fs/ceph/src/osd/ECListener.h

Purpose: `ECListener.h` declares the abstraction layer used by EC pipeline code to call back into the owning PG/backend implementation. It decouples shared EC logic from classic and Crimson-specific OSD implementations.

Important APIs and types: `ECListener` is a pure virtual interface. It exposes OSD map and PG identity queries, recovery notifications (`on_local_recover`, `on_global_recover`, `on_peer_recover`, `begin_peer_recover`), missing/shard state queries, messaging functions, write ordering, logging (`log_operation`, `add_local_next_event`, `op_applied`), stats accounting, temp-object tracking, and EC RMW helpers such as `should_send_op` and `get_pool`.

Control flow: EC read/recovery/write pipelines use the listener whenever they need PG-global knowledge or side effects: scheduling recovery, sending subop messages, recording log entries, applying stat deltas, or checking pool state. The interface hides whether the caller is running in the classic threaded OSD path or a Crimson build.

State and persistence: the interface owns no state, but many methods mutate persistent or replicated PG state through implementers. `log_operation` is the key persistence integration because it commits object-store transactions and PG log entries; recovery callbacks update durable object state and in-memory recovery bookkeeping.

Dependencies and integration: it depends on `OSDMap`, `PGLog`, `MOSDPGPush`, work queues, object recovery types, and classic-only `ObjectContextRef`/thread-pool context types behind `WITH_CRIMSON` guards.

Risks: because this is a broad interface, semantic drift between implementations can break EC code without compile errors. Several comments are marked `XXX`, indicating older boundary ambiguity. Classic/Crimson conditional members increase the risk of one backend missing coverage.

Test signals: integration tests should exercise EC recovery, failed pulls, async reads/writes, temp-object cleanup, and PG log submission through both optimized and legacy callers. Build tests must cover both `WITH_CRIMSON` and non-Crimson configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECListener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECMsgTypes.cc -->
## sources/distributed-fs/ceph/src/osd/ECMsgTypes.cc

Purpose: `ECMsgTypes.cc` implements encoding, decoding, formatting, dumping, cost estimation, and test-instance generation for EC suboperation message payloads: writes, write replies, reads, and read replies.

Important APIs and functions: `ECSubWrite::encode/decode` serializes shard transactions, PG log data, temp object sets, hit-set history, committed versions, and async recovery flags. `ECSubRead::encode/decode` handles data extents, attrs, subchunk hints, and OMAP read fields. `ECSubRead::cost` computes mClock scheduler cost. `ECSubReadReply::encode/decode` supports split payload/data buffer encoding for aligned data and includes OMAP headers/entries/completion flags.

Control flow: encode paths choose structure versions based on features such as `SERVER_TENTACLE` and `CEPH_FEATURE_OSD_FADVISE_FLAGS`. Decode paths preserve compatibility with older wire formats by defaulting missing fields and converting old extent tuple shapes. Read-reply version 2+ manually encodes buffer data into the data bufferlist to keep payload metadata separate from large aligned data.

State and persistence: these types are transient network message contents, but they carry durable state: `ObjectStore::Transaction`, `pg_log_entry_t`, version trim points, temp object records, and OMAP results. Incorrect serialization directly affects write replication and recovery.

Dependencies and integration: integrates with Ceph encoding macros, `ObjectStore::Transaction`, `pg_stat_t`, `pg_log_entry_t`, `Formatter`, `CephContext`, and scheduler configuration. `generate_test_instances` hooks Ceph encoding test infrastructure.

Risks: feature/version compatibility is the main risk. Adding fields requires careful version gates. Manual no-head buffer encoding in read replies can corrupt reads if lengths drift. `cost` must remain nonzero for mClock and compatible with legacy WPQ behavior.

Test signals: encode/decode round-trip tests using generated instances, mixed-feature tests for pre/post Tentacle peers, mClock cost tests for full-chunk versus fragmented subchunks, and OMAP read/reply compatibility tests are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECMsgTypes.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECMsgTypes.h -->
## sources/distributed-fs/ceph/src/osd/ECMsgTypes.h

Purpose: `ECMsgTypes.h` defines the EC suboperation payload types exchanged between OSD shards during EC reads and writes. It is the wire-contract header for EC subwrite/subread request and reply structures.

Important APIs and types: `ECSubWrite` carries source shard, transaction id, client request id, object id, stats, `ObjectStore::Transaction`, versioning, log entries, temp objects, hit-set history, and async recovery flags. `ECSubWriteReply` reports commit/apply status and last complete version. `ECSubRead` carries extents, attrs, subchunk requests, OMAP header requests, and OMAP iteration start/max bytes. `ECSubReadReply` returns buffers, attrs, errors, OMAP headers, OMAP entries, and completion bits.

Control flow: declarations support both single-buffer and split payload/data-buffer encode/decode forms. `claim` on `ECSubWrite` moves expensive members out of another write payload without public copying. Formatter and ostream overloads support debug and admin reporting.

State and persistence: the structures are transient but transport persistent operations. `ECSubWrite` embeds the exact object-store transaction and PG log state that replicas apply; `ECSubReadReply` may return authoritative OMAP fragments used by the primary.

Dependencies and integration: includes Ceph object, encoding, buffer, and transaction types. Formatter specializations allow `fmt` to stream these messages. Message classes and EC backend code depend on this header for subop payload layout.

Risks: copying is deliberately restricted for `ECSubWrite`, so call sites must use `claim` or references correctly. Wire compatibility depends on implementations in the `.cc`; adding members here without versioned encode/decode support would break mixed-version clusters.

Test signals: generated test instances should be included in Ceph encoding tests. Integration coverage should verify EC subwrites with temp objects, backfill/async recovery, OMAP reads, and old-feature decode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECMsgTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECOmapJournal.cc -->
## sources/distributed-fs/ceph/src/osd/ECOmapJournal.cc

Purpose: `ECOmapJournal.cc` implements the in-memory journal that makes deferred OMAP updates visible for optimized EC pools while those updates live only in the PG log and have not yet been applied to the ObjectStore.

Important APIs and functions: `add_entry`, `remove_entry`, `remove_entry_by_version`, `clear`, `clear_all`, `has_omap_updates`, `get_value_updates`, `get_updated_header`, `append_delete`, `append_create`, `append_whiteout`, `trim_delete`, and `get_generation` are the main surface. Helper value types update versioned key values, merged removed ranges, and headers.

Control flow: writes append `ECOmapJournalEntry` objects to `entries`. Read-side calls process entries lazily through `process_entries`, folding insert/remove/range/header/clear operations into `key_map`, `removed_ranges_map`, and `header_map`, then erasing unprocessed entries. Removal APIs delete either queued entries or already-folded updates by matching versions. Range removal logic merges overlapping or open-ended intervals.

State and persistence: the journal is process-local memory, not durable storage. Durability comes from the PG log entry that also records the EC OMAP modification. `object_state_map` tracks outstanding delete generations and whiteout/lost-delete state used by PG backend OMAP generation handling.

Dependencies and integration: depends on `ECOmapJournal.h`, `bufferlist`, `hobject_t`, `eversion_t`, `OmapUpdateType`, Ceph decode helpers, and `DoutPrefixProvider`. `ECTransaction` adds entries; `ECBackend` merges journal state into ObjectStore OMAP reads; `PGBackend` trims/removes entries through backend hooks.

Risks: `process_entries` copies the entry list for logging but then iterates the live list; concurrent access is not protected here and relies on backend serialization. Removal of processed entries by version can erase only last-writer state, so overlapping versions require careful ordering. Open-ended range representation using `nullopt` must match ObjectStore iteration semantics.

Test signals: tests should cover lazy folding, clear-plus-header behavior, inserts after range deletes, deletes/whiteouts, clone visibility, remove-by-version before and after processing, and OMAP reads observing log-only updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECOmapJournal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECOmapJournal.h -->
## sources/distributed-fs/ceph/src/osd/ECOmapJournal.h

Purpose: `ECOmapJournal.h` declares the optimized EC OMAP journal and its versioned helper records. The header documents why EC OMAP updates are initially recorded in PG log state and applied later, and why reads must merge ObjectStore state with in-flight journaled updates.

Important APIs and types: `ECOmapJournalEntry` stores one versioned OMAP mutation batch: clear flag, optional header, and encoded update operations. `ECOmapValue` stores a versioned optional value, with `nullopt` representing removal. `ECOmapRemovedRanges` stores versioned key ranges, including open-ended ranges. `ECOmapHeader` stores the latest versioned header. `ECOmapJournal` exposes entry addition/removal, read-side value/header extraction, delete generation tracking, and iterators over unprocessed entries.

Control flow: write generation builds entries from PG transaction OMAP changes. Read paths call `get_value_updates` and `get_updated_header`, which cause lazy processing. PG cleanup paths call remove/trim methods as log entries become safe or deletes are resolved.

State and persistence: all maps are in-memory indexes keyed by `hobject_t`. Persistent authority remains the PG log and eventual ObjectStore application; the journal is a visibility bridge during the deferred-apply window.

Dependencies and integration: uses Ceph `bufferlist`, `hobject_t`, `eversion_t`, `version_t`, `gen_t`, and `OmapUpdateType`. `ECTransaction`, `ECBackend`, `ECSwitch`, and `PGBackend` are the main integration points.

Risks: callers must understand the distinction between unprocessed and processed entries. The public `begin_entries`/`end_entries` call `entries.at`, so callers must guard with `has_unprocessed_entries` or know entries exist. No locking is declared in the type.

Test signals: header-level API coverage should include construction of entries/values/ranges/headers, `entries_size`, `has_unprocessed_entries`, iterator preconditions, and delete generation return behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECOmapJournal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECSwitch.h -->
## sources/distributed-fs/ceph/src/osd/ECSwitch.h

Purpose: `ECSwitch.h` defines a temporary PGBackend wrapper that selects between legacy EC (`ECLegacy::ECBackendL`) and optimized EC (`ECBackend`) based on the pool's `allows_ecoptimizations()` flag.

Important APIs and types: `ECSwitch` inherits `PGBackend` and owns both backend implementations. It forwards recovery, messaging, transaction submission, reads, scrubbing, size conversion, encode/decode helpers, attr handling, and OMAP methods to the selected backend. Nested `ECRecPred` and `ECReadPred` delegate recoverability/readability predicates to the selected backend.

Control flow: most methods branch on `is_optimized()`. Some transition-sensitive methods use `is_optimized_unchecked()` to tolerate pool-flag changes around `on_change`. `on_change` forwards to the currently active backend and then updates `is_optimized_actual`, permitting a one-way transition into optimized mode while asserting optimized pools remain optimized afterward.

State and persistence: `ECSwitch` itself persists no object state. It routes calls that may mutate durable state, including `submit_transaction`, recovery operations, ObjectStore OMAP reads, and journal cleanup. It also controls whether legacy hinfo metadata is required.

Dependencies and integration: includes `PGBackend.h`, `ECBackendL.h`, and `ECBackend.h`. It is constructed with PG listener, collection handle, ObjectStore, erasure-code plugin, stripe width, and optimized extent-cache LRU.

Risks: both backends are alive, but only one should be authoritative for a pool state. Forwarding gaps can produce behavior differences. Methods unsupported by legacy abort or return `-EOPNOTSUPP`; callers must handle this. OMAP journal methods assert optimized mode, so calling them for legacy pools is fatal.

Test signals: tests should cover pool optimization transitions, each forwarded read/write/recovery path in both modes, legacy unsupported sync-read behavior, hinfo filtering, optimized OMAP journal hooks, and predicate behavior before/after `on_change`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECSwitch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTransaction.cc -->
## sources/distributed-fs/ceph/src/osd/ECTransaction.cc

Purpose: `ECTransaction.cc` implements optimized EC transaction planning execution: converting high-level `PGTransaction` object operations into per-shard `ObjectStore::Transaction`s, EC-encoded writes, rollback metadata, shard version updates, and EC OMAP journal entries.

Important APIs and functions: `WritePlanObj` computes per-object `to_read`, `will_write`, cache invalidation, projected size, and parity-delta-write choice. `Generate` executes one object operation through delete/init/truncate/write/clone/attr/OMAP phases. `generate_transactions` drives `Generate` in plan order. OMAP helpers `accumulate_omap_updates`, `apply_omap_to_transactions`, `OmapCloneVisitor`, and `get_incomplete_ec_omap_log_entries` handle deferred OMAP behavior.

Control flow: planning maps RADOS-object extents to shard extents, aligns partial pages, adds reads for partial writes/truncates, and chooses conventional RMW or parity delta writes. Execution handles delete-first and object init, loads partial extents, truncates, overlays writes, performs clone-range rollback capture, encodes parity, writes selected shards, updates `written_map`, records append/rollback mod_desc, adjusts shard versions in OI, writes attrs, and journals or directly applies OMAP.

State and persistence: durable output is the per-shard ObjectStore transactions plus PG log `mod_desc`. Rollback persistence is through clone objects, rollback extents, xattr rollback, written shard sets, and PG log EC OMAP entries. `ECOmapJournal` receives in-memory entries so reads see log-only OMAP updates.

Dependencies and integration: depends on `ECUtil`, `PGTransaction`, `PGLog`, `OSDMap`, erasure-code plugin APIs, `ObjectContext`, and ObjectStore transaction methods. It is called by optimized `ECBackend`.

Risks: this file is correctness-critical. Risks include incorrect shard extent math, PDW choice with unavailable shards, failure to mark `written_shards`, stale OMAP visibility, clone handling missing incomplete OMAP log entries, and attr cache/OI shard-version races with in-flight writes.

Test signals: strong coverage includes partial overwrite RMW, parity delta writes, truncates, appends beyond current size, delete/recreate, clone/rename, temp object paths, nonprimary shard attr behavior, OMAP insert/remove/range/header/clear, rollback after failed subwrite, and mixed writable/readable shard sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTransaction.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTransaction.h -->
## sources/distributed-fs/ceph/src/osd/ECTransaction.h

Purpose: `ECTransaction.h` declares the optimized EC transaction-generation interface and helper classes that turn a planned PG transaction into shard-level ObjectStore transactions.

Important APIs and types: `WritePlanObj` captures the per-object plan: optional reads, writes, original/projected size, cache invalidation, and PDW flag. `WritePlan` contains ordered plans and whether reads are needed. `Generate` is the per-object executor with private phases for delete/init/truncate/write/attrs/OMAP. `OmapCloneVisitor` extracts EC OMAP modifications from PG log mod_desc entries and applies them to clone transactions. Free functions cover OMAP accumulation/application and top-level `generate_transactions`.

Control flow: callers first build `WritePlanObj` instances, perform any required reads, then call `generate_transactions` with partial read extents, log entries, output maps, transactions, and journal/log context.

State and persistence: the header defines the data that bridges planning and durable write generation. It references persistent PG log entries, per-shard transactions, ObjectContext cache state, and the in-memory `ECOmapJournal`.

Dependencies and integration: includes `ECUtil.h`, `PGTransaction.h`, `ECOmapJournal.h`, `PGLog`, `OSDMap`, erasure-code interfaces, and ObjectStore transactions. It is optimized EC only, not the legacy hinfo path.

Risks: `Generate` stores many references, so lifetimes must outlive construction. The ordered plan contract is enforced by assertions in the implementation. OMAP helpers require encoded `OmapUpdateType` payloads to match decode expectations.

Test signals: header API is indirectly tested through optimized ECBackend transaction tests. Focus should be on plan ordering, no-read write plans, PDW flags, OMAP clone visitor accumulation, and `generate_transactions` output maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTransaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTransactionL.cc -->
## sources/distributed-fs/ceph/src/osd/ECTransactionL.cc

Purpose: `ECTransactionL.cc` implements legacy EC transaction generation using full-stripe logical buffers and legacy `HashInfo` metadata. It predates optimized shard extent maps and explicitly does not support OMAP updates.

Important APIs and functions: internal `encode_and_write` encodes a logical full-stripe-aligned buffer into shard buffers, updates `HashInfo`, records written logical extents, and appends writes to per-shard transactions. `ECTransactionL::generate_transactions` translates each `PGTransaction::ObjectOperation` into legacy shard transactions, rollback metadata, hinfo attr updates, and temp object tracking.

Control flow: for each object operation, it loads the planned `HashInfo`, handles zero-truncate-to-delete, delete-first, create/clone/rename init, attrs, alloc hints, partial read extents, truncates, buffer updates, append-extension zeros, overwrite rollback clone ranges, full-stripe encode/write, and hinfo persistence. Overwrites before `append_after` create rollback extents; appends update mod_desc append state.

State and persistence: legacy EC persists `hinfo_key` attrs containing total chunk size and optional cumulative shard hashes. Rollback state is stored in PG log mod_desc and clone objects. Per-shard `ObjectStore::Transaction`s write encoded chunks and attrs. In-memory `HashInfo` projected size coordinates in-flight operations.

Dependencies and integration: depends on `ECTransactionL.h`, `ECUtilL`, `ObjectStore`, `PGTransaction`, erasure-code deprecated encode/decode APIs, and Ceph release gates for create versus touch behavior.

Risks: all writes must be stripe-aligned by the time encoding happens; assertions enforce this. OMAP is asserted unsupported. Hinfo correctness is critical for object size and scrub behavior. Rollback extent calculations are chunk-space, so logical/chunk conversion mistakes are high impact.

Test signals: legacy EC tests should cover hinfo encode/decode, append hash updates, partial overwrite rollback, truncate down/up, clone/rename hinfo copying, temp objects, old-release create behavior, and assertion that OMAP updates are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTransactionL.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTransactionL.h -->
## sources/distributed-fs/ceph/src/osd/ECTransactionL.h

Purpose: `ECTransactionL.h` declares the legacy EC transaction planner/generator. It builds stripe-aligned legacy write plans and exposes the function that emits per-shard ObjectStore transactions.

Important APIs and types: `ECLegacy::ECTransactionL::WritePlan` tracks whether cache invalidation is needed, per-object `to_read`, `will_write`, and object/source `HashInfoRef`s. Template `get_write_plan` walks a `PGTransaction`, queries hinfo, computes projected size, read-before-write extents, write extents, truncation effects, and clone/source invalidation. `generate_transactions` is the implementation entry point.

Control flow: planning is performed with `safe_create_traverse`, preserving transaction object order. It reads hinfo for each object, handles delete-first and source operations, detects unaligned truncate/write head and tail stripes that need reads, records write extents rounded to stripe width, extends truncates with zero writes, and updates projected hinfo size.

State and persistence: the plan itself is in-memory. It prepares hinfo changes that the `.cc` later persists as the `hinfo_key` attr and identifies partial extents that must be read before legacy writes can be encoded.

Dependencies and integration: depends on `ECUtilL`, `ECExtentCacheL`, erasure-code interfaces, ObjectStore transactions, and `PGTransaction`. It is used by legacy EC backend paths selected through `ECSwitch` when EC optimizations are disabled.

Risks: the template relies on the supplied `get_hinfo` callback returning stable shared `HashInfo` objects. It aborts if `CloneRange` remains in buffer updates. It assumes stripe-aligned projected sizes after planning and disallows reading from objects that are being renamed/cloned.

Test signals: plan tests should inspect `to_read`, `will_write`, projected hinfo size, invalidation, and source hinfo handling for unaligned writes, truncates, deletes, clones, renames, and sparse appends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTransactionL.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTypes.h -->
## sources/distributed-fs/ceph/src/osd/ECTypes.h

Purpose: `ECTypes.h` provides small EC-specific utility types shared by optimized EC code: aligned read descriptors, raw shard identifiers, and shard-indexed maps.

Important APIs and types: `ec_align_t` stores offset, size, and op flags for EC read alignment and supports equality/printing. `raw_shard_id_t` wraps an `int8_t` raw erasure-code shard index with explicit numeric conversions, increment, comparisons, assignment from int, formatter dumping, and generated test instances. `shard_id_map<T>` aliases `mini_flat_map<shard_id_t, T>`.

Control flow: no complex control flow exists. Types are value containers used in EC read/write mapping. `raw_shard_id_t` makes raw plugin chunk order distinct from logical `shard_id_t`, allowing `stripe_info_t` mapping/reverse mapping to be explicit.

State and persistence: these types hold transient in-memory descriptors. They can appear in encoded/dumped structures indirectly through users, but this header itself defines no persistent format except generated test instances and dump support for `raw_shard_id_t`.

Dependencies and integration: includes `include/types.h` for `shard_id_t` and `common/mini_flat_map.h`. Used heavily by `ECUtil`, `ECSwitch`, and optimized EC read APIs.

Risks: `raw_shard_id_t` is backed by `int8_t`, so shard counts beyond that range would be invalid. Explicit conversions reduce accidental mixing but still allow casts. `NO_SHARD` is declared here and must be defined elsewhere.

Test signals: tests should cover raw/logical shard mapping in `stripe_info_t`, comparison/increment behavior, `ec_align_t` equality, and `shard_id_map` behavior with sparse shard ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECUtil.cc -->
## sources/distributed-fs/ceph/src/osd/ECUtil.cc

Purpose: `ECUtil.cc` implements optimized EC extent translation, shard extent map mutation, encoding, decoding, padding, trimming, buffer extraction, debug output, and small helper functions.

Important APIs and functions: `stripe_info_t::ro_range_to_shards` maps RADOS object ranges to per-shard extents and optional shard buffers. `shard_extent_map_t` implements `intersect`, `insert`, `insert_ro_extent_map`, `insert_parity_buffers`, `encode`, `encode_parity_delta`, `decode`, `_decode`, `pad_and_rebuild_to_ec_align`, `get_ro_buffer`, `zero_pad`, `pad_with_other`, `trim`, and containment helpers. `shard_extent_set_t` implements subtract/intersection/insert. The file also defines `log_entry_t` streaming and hinfo-key compatibility helpers.

Control flow: range translation minimizes divisions, computes starting/ending raw shards, applies partial chunk offsets, and inserts shard ranges or sliced buffers. Encode/decode iterate common aligned slices; if any buffer is not page-aligned, maps are rebuilt/padded and retried. Decode first reconstructs missing data shards, then encodes requested parity shards when needed, and finally trims invented buffers back to requested extents.

State and persistence: state is in-memory extent maps over shard offsets. It directly determines what bytes are written to ObjectStore transactions by higher layers. `get_hinfo_key` remains for upgraded pools with legacy metadata.

Dependencies and integration: uses `ECUtil.h`, erasure-code plugin chunk APIs, Ceph buffer alignment/CRC behavior, interval maps, and `DoutPrefixProvider`. `ECTransaction` depends on these transformations for write generation.

Risks: off-by-one or alignment mistakes corrupt EC layout. `slice_map` appears to use `min` where `max` may be expected for some range fields, so slice-related changes need scrutiny. Rebuild retries must terminate. Parity delta writes assume plugin support and aligned old/new buffers.

Test signals: key tests include RO-to-shard mapping across stripe boundaries, partial chunks, custom chunk mappings, encode/decode with missing shards, parity reconstruction, zero dedup, unaligned buffers forcing rebuild, PDW parity updates, and round-trip `get_ro_buffer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECUtil.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECUtil.h -->
## sources/distributed-fs/ceph/src/osd/ECUtil.h

Purpose: `ECUtil.h` declares optimized EC utility containers and algorithms for mapping RADOS object byte ranges onto erasure-coded shard extents, slicing shard buffers for plugin encode/decode, and representing EC read/write logs.

Important APIs and types: `extent_set`/`extent_map` are flat interval containers. `slice_iterator` walks common buffer slices across shards, exposing input and output `bufferptr`s for plugin operations and optional zero dedup. `ECUtil::shard_extent_set_t` is a shard-indexed interval set. `stripe_info_t` encapsulates k/m, stripe width, chunk size, raw/logical shard mapping, feature flags, and range conversion helpers. `shard_extent_map_t` stores per-shard extent maps and exposes encode/decode/pad/trim/read helpers. `log_entry_t` records EC read pipeline events.

Control flow: callers build `stripe_info_t` from the EC plugin and pool, translate RO ranges to shard sets/maps, populate or reconstruct `shard_extent_map_t`, then call encode/decode. `slice_iterator` advances through the smallest common contiguous slice boundary and invalidates CRCs for output buffers before plugin mutation.

State and persistence: all structures are in-memory, but they model durable EC layout. `stripe_info_t` reads pool/plugin capabilities such as overwrites, partial reads/writes, parity delta writes, CRC encode/decode, direct reads, and nonprimary shard status.

Dependencies and integration: depends on erasure-code plugin interfaces, `osd_types.h`, Ceph buffers, interval maps, `mini_flat_map`, `shard_id_t`, `raw_shard_id_t`, and logging.

Risks: the API exposes mutable maps with cached RO ranges, so modifications must call methods that keep offsets in sync. Alignment constants are fixed at 4096. `slice_iterator` assumes input maps are nonempty and buffers are structurally valid.

Test signals: tests should cover stripe constructors, custom chunk mappings, object-to-shard size conversion, shard range conversion, slice iteration with uneven extents, zero dedup, support flag behavior, and encode/decode API preconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECUtilL.cc -->
## sources/distributed-fs/ceph/src/osd/ECUtilL.cc

Purpose: `ECUtilL.cc` implements legacy EC utility functions for stripe/chunk conversion, deprecated plugin encode/decode wrappers, and legacy `HashInfo` persistence helpers.

Important APIs and functions: `stripe_info_t::chunk_aligned_offset_len_to_chunk` converts logical chunk-aligned ranges to chunk offsets. Two `decode` overloads reconstruct either a concatenated logical output or requested shard outputs using deprecated erasure-code APIs and subchunk repair hints. `encode` splits logical full stripes and appends encoded shard buffers. `HashInfo::append`, `encode`, `decode`, `dump`, stream output, and generated test instances manage legacy hinfo metadata. `is_hinfo_key_string`/`get_hinfo_key` expose the legacy attr key.

Control flow: encode walks the input one full stripe at a time and appends each encoded chunk to shard bufferlists. Decode validates equal shard buffer lengths, slices per chunk or repair-data window, calls plugin decode, and appends outputs. `HashInfo::append` updates cumulative CRCs when hashes are present and advances total chunk size.

State and persistence: `HashInfo` persists total chunk size and cumulative shard hashes in the `hinfo_key` object attr for legacy EC objects. It also carries an ephemeral projected chunk size for in-flight planning.

Dependencies and integration: uses `ECUtilL.h`, Ceph encoding macros, `bufferlist`, `Formatter`, and deprecated erasure-code plugin methods hidden behind ignore-deprecated macros. Consumed by `ECTransactionL`, legacy backend recovery/scrub, and hinfo registry code.

Risks: deprecated plugin APIs and manual subchunk calculations are compatibility-sensitive. Assertions assume aligned and nonempty buffers. Clearing hashes on truncation removes hash validation data, which is intentional but affects scrub signals.

Test signals: generated `HashInfo` test instances support encoding tests. Additional coverage should check encode/decode round trips, subchunk repair decode, hinfo append CRC updates, decode of persisted hinfo, and legacy attr-key filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECUtilL.cc -->
