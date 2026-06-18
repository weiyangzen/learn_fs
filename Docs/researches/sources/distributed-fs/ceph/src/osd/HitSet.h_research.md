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
