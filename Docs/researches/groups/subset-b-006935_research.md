# subset-b-006935 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECUtilL.h -->
# sources/distributed-fs/ceph/src/osd/ECUtilL.h

## Purpose

`ECUtilL.h` declares the legacy erasure-coded object utility layer under `ECLegacy::ECUtilL`. It concentrates stripe geometry conversions, erasure-code encode/decode entry points, and legacy per-shard hash metadata used by `ECBackendL`, `ECCommonL`, `ECTransactionL`, and scrub code. The file is a header contract: most algorithms are implemented in `ECUtilL.cc`, but this file defines the invariants callers rely on when translating logical object offsets to per-shard chunk ranges and when persisting hash information in object xattrs.

## Important APIs, Types, and Functions

`stripe_info_t` stores immutable EC layout facts: `stripe_width`, per-data-shard `chunk_size`, data chunk count `k`, coding chunk count `m`, forward `chunk_mapping`, and reverse mapping. Constructors derive these from `ErasureCodeInterfaceRef` or explicit unit-test values and assert that stripe width is divisible by `k`. `complete_chunk_mapping()` fills absent mapping entries with identity positions; `reverse_chunk_mapping()` asserts the mapping is a bijective permutation.

The offset helpers form the main public API: `logical_to_prev_chunk_offset()`, `logical_to_next_chunk_offset()`, `logical_to_prev_stripe_offset()`, `logical_to_next_stripe_offset()`, `aligned_logical_offset_to_chunk_offset()`, `chunk_aligned_logical_offset_to_chunk_offset()`, `chunk_aligned_logical_size_to_chunk_size()`, `aligned_chunk_offset_to_logical_offset()`, `chunk_aligned_offset_len_to_chunk()`, `offset_len_to_stripe_bounds()`, `offset_len_to_chunk_bounds()`, `offset_length_to_data_chunk_indices()`, and `offset_length_is_same_stripe()`.

The free functions `encode()` and two overloads of `decode()` are the legacy adapters to `ErasureCodeInterface`. `HashInfo` tracks `total_chunk_size`, `cumulative_shard_hashes`, and ephemeral `projected_total_chunk_size`. It exposes append, clear, encode/decode, dump, test-instance generation, logical-size conversions, xattr key helpers `is_hinfo_key_string()` and `get_hinfo_key()`, and `update_to()` for refreshing committed hash state while preserving projection.

## Control Flow and Data Flow

The header's inline control flow is mostly arithmetic normalization. Logical offsets round down or up to stripe boundaries, then convert to chunk offsets by dividing by the data stripe fanout. Chunk-size conversions assert chunk alignment rather than silently repairing caller mistakes. `offset_len_to_stripe_bounds()` converts an arbitrary logical extent to a stripe-aligned logical span; `chunk_aligned_offset_len_to_chunk()` is declared here and implemented by applying that span to per-chunk coordinates.

Data flows from pool EC profile and `ErasureCodeInterface` into `stripe_info_t`, then into read, write, repair, and scrub paths. Encode callers pass a stripe-aligned logical buffer and desired shard set; decode callers pass available shard buffers and either a concatenated output list or per-shard output pointers. `HashInfo` data flows through the hidden xattr named by `get_hinfo_key()`, with projected size allowing transaction code to reason about in-flight object size before metadata commits.

## State and Persistence Behavior

`stripe_info_t` is immutable after construction and persists no disk state. `HashInfo` is the persistent piece: `total_chunk_size` and `cumulative_shard_hashes` are encoded with Ceph's `ENCODE_START` framework and stored in an internal EC xattr. `projected_total_chunk_size` is explicitly ephemeral; decode resets it to the committed `total_chunk_size`, and `update_to()` preserves the caller's projection while replacing committed hash fields. `set_total_chunk_size_clear_hash()` intentionally discards shard hash coverage while retaining size.

## Dependencies and Integration Points

This header depends on `ErasureCodeInterface`, Ceph bufferlists, encoding helpers, `Formatter`, `ceph_assert`, `shard_id_t`, and standard containers. It integrates with `ECUtilL.cc` for implementation, `ECBackendL` for xattr sanitation and object IO, `ECCommonL` for recovery reads and `UnstableHashInfoRegistry`, `ECTransactionL` for write transformations and rollback xattrs, and scrub code that compares legacy hash info against authoritative object state.

## Risks and Edge Cases

Most validation uses `ceph_assert`, so production behavior assumes callers have already satisfied alignment, mapping, and buffer-size preconditions. `reverse_chunk_mapping()` indexes `used.at(index)` after converting signed mapping values, so invalid negative or out-of-range mappings abort. Zero-size encode/decode paths are valid but must not be confused with missing data. Hash state may be absent after `set_total_chunk_size_clear_hash()`, so consumers must check `has_chunk_hash()` before trusting per-shard hashes. Logical-to-chunk conversion can overflow if very large offsets are added without caller bounds.

## Test Signals

Useful tests should cover identity and non-identity chunk mappings, mapping bijection assertions, aligned and unaligned offset/length conversions, zero-length encode/decode, partial repair decode through `minimum_to_decode()`, and round-trip `HashInfo` encoding. EC integration tests should verify `hinfo_key` is stripped from user-visible attributes, preserved for internal legacy EC objects, updated across appends, reset on decode, and compared by scrub. Unit-test constructors and `HashInfo::generate_test_instances()` are explicit hooks for encoding and formatter regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECUtilL.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/HitSet.cc -->
# sources/distributed-fs/ceph/src/osd/HitSet.cc

## Purpose

`HitSet.cc` implements the non-inline parts of the OSD HitSet abstraction declared in `HitSet.h`. HitSets record object access membership for cache tiering, promote decisions, and archived hit-set objects. This file supplies construction from pool parameters, type-tagged encode/decode, deep-copy behavior for parameter objects, formatter output, and test-instance generation for the three supported implementations: bloom, explicit hash, and explicit object.

## Important APIs, Types, and Functions

`HitSet::HitSet(const HitSet::Params&)` dispatches on `Params::get_type()` and constructs `BloomHitSet`, `ExplicitHashHitSet`, or `ExplicitObjectHitSet`. `HitSet::encode()` writes the sealed flag, a one-byte implementation type, and the implementation payload. `HitSet::decode()` reads the same shape, instantiates the correct concrete implementation, and throws `buffer::malformed_input` for unknown type tags.

`HitSet::Params` has a copy constructor and assignment operator that use encode/decode of the concrete parameter object to avoid virtual assignment. `create_impl()` is the private type factory for parameter implementations. `Params::encode()`, `Params::decode()`, `Params::dump()`, `Params::generate_test_instances()`, and `operator<<` provide persistence, diagnostics, and test fixtures. The concrete `dump()` functions for `ExplicitHashHitSet`, `ExplicitObjectHitSet`, `BloomHitSet::Params`, and `BloomHitSet` are implemented here.

## Control Flow and Data Flow

The core control flow is type-tag dispatch. Parameters come from pool configuration, are decoded from persistent pool metadata, or are copied inside OSD code. A `HitSet` created from those parameters receives object inserts through the header-defined virtual interface, then this file encodes the sealed flag and implementation payload for storage or network transport. Decode reverses the flow by reading the type tag before delegating payload parsing to the concrete implementation.

The generate-test flow builds empty and populated HitSets for bloom, explicit-hash, and explicit-object variants. Dump flow is read-only: it emits type, sealed state, insert counts, hash/object arrays, bloom internals, and bloom parameter values to `Formatter` or stream output.

## State and Persistence Behavior

`HitSet::encode()` persists two layers of state: wrapper state (`sealed` and type tag) and concrete implementation state. Explicit hash/object sets persist both total insertion count and unique membership set. Bloom sets persist the `compressible_bloom_filter`. `HitSet::Params` separately persists configuration needed to create future HitSets, such as bloom false-positive probability, target size, and seed. The copy constructor for `Params` persists through a temporary bufferlist, so copy fidelity depends on each concrete parameter encoder.

## Dependencies and Integration Points

This file depends on `HitSet.h`, Ceph buffer encoding, `Formatter`, `hobject_t`, and bloom-filter support. OSD integration is broad: pool options are parsed and printed by `OSDMonitor`, default pool metadata in `osd_types` includes HitSet parameters, `PrimaryLogPG` creates and rotates HitSets, `Objecter` fetches archived HitSet objects, and `TierAgentState` stores loaded HitSets for cache-tier agents.

## Risks and Edge Cases

Constructor dispatch uses `assert(0)` for unknown parameter types, while decode throws malformed input; callers need to distinguish programmer bugs from corrupt input. `Params::operator=` calls `create_impl(o.get_type())` and then decodes only when `o.impl` exists; this handles `TYPE_NONE` but depends on `create_impl()` resetting `impl` correctly. `generate_test_instances()` constructs `Params(&i)` from stack-loop values; the constructor takes ownership after cloning through the concrete object pointer pattern, so future changes to ownership semantics would be risky. Bloom HitSets can have false positives by design, while explicit-hash HitSets can collide because they store only 32-bit object hashes.

## Test Signals

Tests should round-trip wrapper HitSets and `HitSet::Params` for all four tags including `TYPE_NONE`, assert malformed type tags fail, verify sealed state survives encode/decode, and compare insert count versus approximate unique count semantics. Tiering integration tests should confirm monitor-configured hit-set parameters create the expected concrete type and that `PrimaryLogPG` can rotate, persist, trim, and reload archived HitSet objects. Formatter tests should cover dump output for explicit object/hash membership and bloom parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/HitSet.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/HitSet.h -->
# sources/distributed-fs/ceph/src/osd/HitSet.h

## Purpose

`HitSet.h` declares the generic OSD HitSet container and its concrete membership strategies. A HitSet represents a period of object access history and hides whether membership is stored as explicit object hashes, explicit full object identifiers, or a bloom filter. This lets cache-tier and placement-group logic ask uniform questions such as "was this object hit?", while pool configuration chooses the accuracy, memory, and persistence tradeoff.

## Important APIs, Types, and Functions

`HitSet::impl_type_t` defines `TYPE_NONE`, `TYPE_EXPLICIT_HASH`, `TYPE_EXPLICIT_OBJECT`, and `TYPE_BLOOM`, with `get_type_name()` helpers. `HitSet::Impl` is the runtime virtual interface: `get_type()`, `is_full()`, `insert()`, `contains()`, `insert_count()`, `approx_unique_insert_count()`, `encode()`, `decode()`, `dump()`, `clone()`, and optional `seal()`. The outer `HitSet` owns an implementation through `boost::scoped_ptr`, tracks `sealed`, forwards membership calls, and has copy semantics through `clone()`.

`HitSet::Params::Impl` is the corresponding factory/configuration interface with `get_new_impl()`, encode/decode, dump, and stream dump. Concrete types are `ExplicitHashHitSet`, `ExplicitObjectHitSet`, and `BloomHitSet`. Explicit-hash stores `std::unordered_set<uint32_t>` of `hobject_t::get_hash()` values plus total count. Explicit-object stores `std::unordered_set<hobject_t>` plus total count. Bloom stores `compressible_bloom_filter`; `BloomHitSet::Params` stores false-positive probability in micro-units, target size, and seed.

## Control Flow and Data Flow

Object accesses flow through `HitSet::insert()` into the selected implementation. Reads or promote decisions flow through `contains()`. Explicit variants insert either object hashes or full `hobject_t` values and can answer membership without false positives except for hash collisions in the hash variant. Bloom inserts only object hashes into a probabilistic filter and may report false positives. `seal()` can be called once on the wrapper; it sets `sealed` and gives the implementation a chance to compact itself. Bloom sealing compresses toward approximately 50 percent bit density when current density permits.

Persistence flow is type-tagged: the wrapper and parameter classes use Ceph class encoders declared by `WRITE_CLASS_ENCODER`, while each implementation defines versioned encode/decode inline or in the `.cc` file. Copy flow uses either virtual `clone()` or bufferlist encode/decode for bloom's copy constructor.

## State and Persistence Behavior

The wrapper's persistent state is whether the set is sealed and which implementation owns the payload. Explicit implementations persist total insertion count separately from unique membership, preserving repeated-hit accounting. Bloom state persists the filter itself; bloom parameters persist only construction settings, not observations. `fpp_micro` quantizes false-positive probability to one-millionth units. `TYPE_NONE` is valid for disabled hit sets and should produce no implementation payload.

## Dependencies and Integration Points

The header depends on Ceph encoding, `common/bloom_filter.hpp`, `common/hobject.h`, `Formatter`, Boost scoped/shared pointers, and unordered containers. It is included by OSD pool metadata (`osd_types.h`), cache-tier agent state, monitor pool-option parsing, and placement-group code that creates and archives HitSets. The `HitSetRef` shared pointer is used where archived or in-memory HitSets need shared ownership.

## Risks and Edge Cases

Callers must not invoke forwarding methods such as `insert()` or `contains()` when `impl` is null. `seal()` asserts it has not already been called, so duplicate sealing is a hard bug. Explicit-hash membership can collide across different objects with the same 32-bit hash; bloom membership has configured false positives and can become full. `BloomHitSet::Params::set_fpp()` depends on `llrintl`, so parameter quantization and bounds should be considered when parsing user input. Copying bloom state via encode/decode is robust but comparatively expensive.

## Test Signals

Coverage should include each implementation's insert, contains, duplicate insert count, approximate unique count, full/sealed behavior, and encode/decode compatibility. Boundary tests should exercise `TYPE_NONE`, null implementation safety at higher layers, bloom false-positive configuration parsing, bloom compression after seal, explicit-hash collision tolerance, and full-object hashing/equality. Integration tests should verify monitor pool settings map to correct `HitSet::Params` and that `PrimaryLogPG` records read/write hits and persists archived HitSets correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/HitSet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/MissingLoc.cc -->
# sources/distributed-fs/ceph/src/osd/MissingLoc.cc

## Purpose

`MissingLoc.cc` implements the out-of-line recovery-source maintenance methods for `MissingLoc`. `MissingLoc` is used during OSD peering and recovery to track objects that need recovery, which shards may contain usable copies, and how that source knowledge changes as peers go down or become stray. This file contains the heavier scans over missing objects and source sets, with logging and thread-pool heartbeat resets for long loops.

## Important APIs, Types, and Functions

`readable_with_acting()` checks whether an object can be read from the current acting set. It returns true for objects not needing recovery, false for deletes or no known locations, intersects known locations with `acting`, and asks the configured readable predicate if that shard subset suffices.

`add_batch_sources_info()` marks a set of sources as usable for every non-delete missing object, updating both `missing_loc` and `missing_loc_sources`. `add_source_info()` evaluates a single peer's `pg_info_t` and `pg_missing_t` against every needed object, adding the peer only when its `last_update` is new enough, the object is before `last_backfill`, and the peer is not also missing that object. `check_recovery_sources()` removes sources whose OSDs are now down according to the OSD map. `remove_stray_recovery_sources()` removes one stray shard from all source structures.

## Control Flow and Data Flow

The add-source flow scans `needs_recovery_map`. For each non-delete item it validates whether the source plausibly has the needed version: source `last_update >= need`, object order before `last_backfill`, and not present in the peer's missing set. If valid, it creates or updates `missing_loc[object]`, temporarily decrements the count index before mutation, inserts the source, and increments the count index afterward. The batch form skips the per-object pg-info tests and applies the same source set to every non-delete missing object.

The removal flows are inverse scans. Down or stray shards are removed from `missing_loc_sources`, then each object's source set is filtered. Objects with no remaining sources are erased from `missing_loc`; otherwise their `missing_by_count` bucket is recomputed. Long loops periodically reset `HBHandle` timeouts based on `osd_loop_before_reset_tphandle`, and `add_source_info()` suppresses verbose per-object logging after about 0.5 seconds.

## State and Persistence Behavior

This file mutates in-memory peering and recovery state only. It does not encode or persist `MissingLoc`; durable truth comes from PG logs, `pg_missing_t`, `pg_info_t`, and OSD maps. The key invariant is that `missing_by_count` remains synchronized with `missing_loc`: mutations call `_dec_count()` before changing a non-empty set and `_inc_count()` after the final set is known. `missing_loc_sources` is a deduplicated index of all shards currently believed to be recovery sources.

## Dependencies and Integration Points

The implementation depends on `MissingLoc.h`, `OSDMapRef`, `pg_info_t`, `pg_missing_t`, `pg_missing_item`, `HBHandle`, Ceph logging macros, `CephContext`, and backend-provided readable/recoverable predicates. It is owned by `PeeringState`, surfaced in `PG` diagnostics through missing-by-count output, and used by `PrimaryLogPG` read paths to decide whether degraded or recovering objects are readable with the acting set.

## Risks and Edge Cases

The correctness risk is stale or overbroad source knowledge. `add_batch_sources_info()` assumes all listed sources can serve all non-delete missing objects, so it must be used only when that condition is externally proven. `add_source_info()` has a known uncertainty around `last_backfill` comments: an object past `last_backfill` is treated as missing on the peer. Missing deletes are deliberately not source-tracked. Any mutation that skips `_dec_count()` or `_inc_count()` corrupts recovery prioritization statistics. Logging suppression prevents log floods but can obscure individual object decisions in large PGs.

## Test Signals

Tests should exercise source addition for peers with too-old `last_update`, objects past `last_backfill`, peers that also list the object missing, deletes, and successful source discovery. Recovery-source removal tests should verify down OSDs and stray shards disappear from both `missing_loc_sources` and per-object locations, with empty objects removed. Invariants should assert that the sum of `missing_by_count` buckets matches `missing_loc` after every add/remove path. Readability tests should cover replicated and EC predicates with acting-set intersections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/MissingLoc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/MissingLoc.h -->
# sources/distributed-fs/ceph/src/osd/MissingLoc.h

## Purpose

`MissingLoc.h` declares and partly implements the placement-group recovery location index used by OSD peering and recovery. It tracks which objects need recovery, which shards are known possible sources for those objects, and aggregate counts of source availability split between shards in the current up set and other shards. The class gives peering code fast answers for unfound-object detection, readability, recoverability, recovery prioritization, and source cleanup.

## Important APIs, Types, and Functions

`MappingInfo` abstracts PG mapping facts needed by this index: current up set, whether the PG is erasure-coded, and PG size. `loc_count_t` counts known locations as `up` and `other`, orders counts for map keys, and asserts non-negative values when streamed. `missing_by_count_t` maps each EC `shard_id_t` or replicated `NO_SHARD` to a histogram of `loc_count_t` buckets.

The main state maps are `needs_recovery_map`, `missing_loc`, `missing_loc_sources`, and `missing_by_count`. Helpers `_get_count()`, `pgs_by_shard_id()`, `_inc_count()`, and `_dec_count()` maintain the aggregate count index. Public APIs include `needs_recovery()`, `is_deleted()`, `is_unfound()`, `readable_with_acting()`, `num_unfound()`, `have_unfound()`, `clear()`, `add_location()`, `remove_location()`, `clear_location()`, `add_active_missing()`, `add_missing()`, `revise_need()`, `add_source_info()`, `add_batch_sources_info()`, `check_recovery_sources()`, `remove_stray_recovery_sources()`, `recovered()`, `rebuild()`, and accessors for locations and maps.

## Control Flow and Data Flow

Missing data enters from the acting PG's `pg_missing_t` via `add_active_missing()` or explicit `add_missing()`. Source data enters from peer `pg_info_t` and `pg_missing_t` via `add_source_info()`, from proven batches via `add_batch_sources_info()`, or from direct location mutation. `is_unfound()` and `have_unfound()` combine `needs_recovery_map`, delete status, known locations, and the recoverable predicate. `readable_with_acting()` further intersects known locations with a caller-provided acting set and applies the readable predicate.

`rebuild()` is the densest inline flow. It first removes old state for one object, discovers the missing item from local missing data or peer missing maps for the recovery target set, returns if the object is no longer missing, records deletes without locations, and otherwise rebuilds source locations from self and peer maps using version, backfill, and peer-missing tests before recomputing counts.

## State and Persistence Behavior

`MissingLoc` is in-memory state derived from persistent PG metadata and current OSD map membership. `needs_recovery_map` records object-to-needed-version state, including delete markers. `missing_loc` records possible source shards only for non-delete objects when known. `missing_loc_sources` summarizes the source shards currently referenced. `missing_by_count` is a secondary index that must always match `missing_loc`; for EC PGs it contains an entry for every shard id, including empty sets for completely missing shards, while replicated PGs use `NO_SHARD`.

## Dependencies and Integration Points

The header depends on `OSDMap`, heartbeat handles, Ceph context/logging, `osd_types`, `pg_missing_t`, `pg_info_t`, `pg_shard_t`, `hobject_t`, `spg_t`, `DoutPrefixProvider`, and backend predicates `IsPGReadablePredicate` and `IsPGRecoverablePredicate`. `PeeringState` inherits `MappingInfo` and owns `MissingLoc`; `PG` exposes missing-by-count diagnostics; `PrimaryLogPG` consults readability during read processing; EC and replicated backends provide the predicates that define enough shards for read or recovery.

## Risks and Edge Cases

The class relies on callers to set readable and recoverable predicates before methods dereference them. EC count handling deliberately creates empty per-shard buckets, so tests must account for shards with zero locations. `add_active_missing()` asserts if the same object is added with a conflicting needed version, making inconsistent peering input fatal. `rebuild()` asserts local `last_backfill` is max and local `last_update` covers the needed version; it is intended for a specific peering state. Deletes are treated as recovery needs but not unfound source needs. Direct map accessors expose internal state as const references, so callers must not assume persistence beyond the current peering epoch.

## Test Signals

Tests should validate replicated and EC `missing_by_count` histograms, including completely missing EC shards, direct add/remove/clear location mutations, conflicting `add_active_missing()` input, delete handling, unfound counts, and predicate-driven recoverability. `rebuild()` needs cases where the item is local missing, peer missing, recovered, deleted, present on self, present on peers, blocked by peer `last_update`, blocked by `last_backfill`, and blocked by peer missing maps. OSD map changes should be tested through the `.cc` cleanup methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/MissingLoc.h -->
