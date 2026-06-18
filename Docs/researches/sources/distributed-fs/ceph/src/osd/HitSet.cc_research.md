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
