# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.20.0.xml lines 31508-32308

## Scope

This chunk is the closing portion of the Hadoop Core 0.20.0 JDiff public API snapshot. It starts inside the tail of `org.apache.hadoop.util.bloom.DynamicBloomFilter`, covers the shared Bloom-filter base classes and retouched Bloom-filter APIs, then covers the entire visible `org.apache.hadoop.util.hash` package before the XML closes. The file is generated API metadata rather than implementation source, so the durable facts in this chunk are class names, inheritance, public/protected signatures, field constants, visibility, checked exceptions, deprecation state, and embedded API documentation.

## Purpose

The chunk documents two related public utility areas:

- `org.apache.hadoop.util.bloom` defines probabilistic membership filters used to summarize sets of Hadoop `Key` values with compact, lossy structures. This includes the common abstract `Filter`, weighted serializable `Key` values, dynamic Bloom filters that grow by rows, and retouched Bloom filters that intentionally clear bits to remove selected false positives.
- `org.apache.hadoop.util.hash` defines the hash abstraction used by the Bloom-filter package and other lookup-oriented utilities. It exposes configurable hash selection, singleton hash instances, convenience overloads, and concrete Jenkins and Murmur 32-bit non-cryptographic hash implementations.

## Important APIs and Types

### `org.apache.hadoop.util.bloom.DynamicBloomFilter` tail

- This chunk begins with the public `write(DataOutput)` and `readFields(DataInput)` methods for `DynamicBloomFilter`, both declaring `IOException`.
- The class documentation describes a dynamic Bloom filter as a matrix of standard Bloom filters. It begins with one row and appends a new row when no active row has capacity for another key.
- Membership semantics are row-based: a key is considered present when all of its hash positions are set in one matrix row.
- The visible methods immediately before the chunk boundary, from line context, include public `add(Key)`, logical set operations, `membershipTest(Key)`, `not()`, `or(Filter)`, `xor(Filter)`, `toString()`, and serialization. The chunk itself should be merged with the previous chunk for the complete class signature.

### `org.apache.hadoop.util.bloom.Filter`

- `Filter` is a public abstract class extending `Object` and implementing `org.apache.hadoop.io.Writable`.
- Constructors are protected: a no-argument constructor and `Filter(int vectorSize, int nbHash, int hashType)`.
- Abstract public operations define the core filter contract: `add(Key)`, `membershipTest(Key)`, `and(Filter)`, `or(Filter)`, `xor(Filter)`, and `not()`.
- Concrete bulk-add overloads accept `List`, `Collection`, and `Key[]`, delegating the conceptual operation of adding many keys to the single-key `add(Key)` implementation.
- `write(DataOutput)` and `readFields(DataInput)` provide Hadoop `Writable` serialization hooks and can throw `IOException`.
- Protected fields are part of the subclass state contract: `vectorSize`, `hash` (`HashFunction`), `nbHash`, and `hashType`.
- Documentation frames `Filter` as the general lossy summary abstraction for a set, implemented by Bloom filters and extensions.

### `org.apache.hadoop.util.bloom.HashFunction`

- `HashFunction` is a public final class.
- Its public constructor `HashFunction(int maxValue, int nbHash, int hashType)` builds a mapper from a `Key` to multiple vector positions, bounded by a highest returned value and configured for a selected hash type.
- `clear()` is public and documented as a no-op.
- `hash(Key)` returns `int[]`, the array of hashed positions for a key.
- The type integrates `Key`, `Filter`, and the lower-level `org.apache.hadoop.util.hash.Hash` implementations.

### `org.apache.hadoop.util.bloom.Key`

- `Key` is a public class implementing `org.apache.hadoop.io.WritableComparable`.
- Constructors support Hadoop deserialization (`Key()`), a byte value with default weight (`Key(byte[])`), and a byte value with explicit weight (`Key(byte[], double)`).
- `set(byte[], double)` updates both value and weight.
- `getBytes()` returns the key bytes; `getWeight()` returns the associated weight.
- `incrementWeight(double)` and no-argument `incrementWeight()` mutate the weight, with the no-argument form incrementing by one.
- Equality, hash-code, binary serialization, deserialization, and ordering are public through `equals(Object)`, `hashCode()`, `write(DataOutput)`, `readFields(DataInput)`, and `compareTo(Key)`.
- The public API implies `Key` identity is byte-oriented with an additional weight used by filter algorithms such as retouched Bloom filters.

### `org.apache.hadoop.util.bloom.RemoveScheme`

- `RemoveScheme` is a public interface defining selection constants for retouched Bloom-filter bit clearing.
- Constants are public static final `short` values: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- Documentation describes the tradeoffs: random bit clearing, minimizing generated false negatives, maximizing removed false positives, or optimizing a ratio between false-positive removal and false-negative generation.

### `org.apache.hadoop.util.bloom.RetouchedBloomFilter`

- `RetouchedBloomFilter` is a public final class extending `BloomFilter` and implementing `RemoveScheme`.
- Constructors include a default constructor for `readFields` and `RetouchedBloomFilter(int vectorSize, int nbHash, int hashType)`.
- `add(Key)` inserts ordinary positive keys.
- `addFalsePositive(...)` overloads accept a single `Key`, `Collection`, `List`, or `Key[]` of known false positives. The single-key contract explicitly treats `null` as a no-op.
- `selectiveClearing(Key, short)` performs the retouching step for a false-positive key using one of the `RemoveScheme` constants.
- `write(DataOutput)` and `readFields(DataInput)` expose serialized persistence for both inherited Bloom-filter state and retouched false-positive metadata.
- The class documentation states the algorithm intentionally removes selected false positives at the cost of introducing random false negatives.

### `org.apache.hadoop.util.hash.Hash`

- `Hash` is a public abstract class and the common API for hash functions.
- `parseHashType(String)` converts names to constants. The documented supported names are `jenkins` and `murmur`.
- `getHashType(Configuration)` resolves the configured hash type from Hadoop configuration.
- `getInstance(int)` and `getInstance(Configuration)` return singleton `Hash` implementations for a type or configured type, returning `null` for invalid types.
- Convenience `hash(byte[])` hashes all bytes with seed `-1`; `hash(byte[], int initval)` hashes all bytes with an explicit seed.
- The core abstract method is `hash(byte[] bytes, int length, int initval)`.
- Public static final constants are `INVALID_HASH`, `JENKINS_HASH`, and `MURMUR_HASH`.

### `org.apache.hadoop.util.hash.JenkinsHash`

- `JenkinsHash` extends `Hash` and exposes a public constructor.
- Static `getInstance()` returns a `Hash` singleton.
- `hash(byte[] key, int nbytes, int initval)` implements Bob Jenkins' `hashlittle()` style 32-bit lookup hash.
- `main(String[] args)` computes a hash for a specified file and declares `IOException`.
- Documentation states the implementation is suitable for hash-table lookup and not cryptographic use.

### `org.apache.hadoop.util.hash.MurmurHash`

- `MurmurHash` extends `Hash` and exposes a public constructor.
- Static `getInstance()` returns a `Hash` singleton.
- `hash(byte[] data, int length, int seed)` implements the concrete byte-array hash.
- Documentation identifies it as a very fast non-cryptographic hash for general hash-based lookup, ported from MurmurHash 2.0 C to Java.

## Control Flow and State Behavior

- Bloom-filter insertion flows through `Filter.add(Key)` for single keys and through the concrete bulk-add helpers for lists, collections, and arrays. Subclasses own the actual vector or counter mutation.
- Dynamic Bloom-filter growth is threshold-driven: insertion first searches for an active row whose recorded-key count is below the configured row cardinality, otherwise it appends a new standard Bloom-filter row and inserts there.
- Filter boolean operations mutate the receiver. The documentation for `and`, `or`, `xor`, and `not` states that the result is assigned to `this` filter.
- `HashFunction.hash(Key)` bridges filter operations to lower-level `Hash` algorithms by producing multiple vector positions for one key. The number of returned positions is driven by `nbHash`, and values must fit within the configured vector bound.
- `Key` is mutable: callers can replace bytes and weight, increment weight, deserialize new contents through `readFields`, and compare keys through `WritableComparable`.
- Retouched Bloom-filter control flow has two channels: ordinary positive-key insertion and separate false-positive recording. `selectiveClearing` then chooses which bit to clear for a specific false-positive key according to the requested remove scheme.
- Hash selection flow is configuration or constant driven: callers parse a string or read a `Configuration`, then ask `Hash.getInstance(...)` for the singleton implementation. Invalid selection is observable because the API can return `null`.
- Concrete hash methods are deterministic pure computations over byte arrays, byte counts, and seed values, aside from `JenkinsHash.main`, which reads a named file and writes a command-line result.

## State and Persistence Behavior

- The JDiff XML itself is static compatibility data. It records public API shape for Hadoop Core 0.20.0 and is likely consumed by compatibility/report generation rather than runtime Hadoop code.
- `Filter` persists common filter parameters and hash configuration through `Writable`. Its protected fields are the shared serialized state foundation for subclasses.
- Dynamic Bloom filters persist matrix/row state through `write` and `readFields`. Correct compatibility depends on preserving row order, row sizes, hash settings, and per-row occupancy semantics in the implementation.
- `Key` persists its byte value and weight through `Writable`; ordering and equality must remain compatible with serialized values to avoid breaking persisted filter contents or sorted collections.
- `RetouchedBloomFilter` must persist inherited Bloom-vector state plus any false-positive bookkeeping needed for retouching.
- Hash implementations are exposed as singleton-style instances by `getInstance`, so they should avoid mutable per-call state. `HashFunction.clear()` being a no-op reinforces that hashing does not keep meaningful resettable state at this API layer.

## Dependencies and Integration Points

- The Bloom package depends on Hadoop IO contracts: `Writable`, `WritableComparable`, `DataInput`, `DataOutput`, and `IOException`.
- `Filter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` integrate with `Key` and `HashFunction`; `HashFunction` integrates with `org.apache.hadoop.util.hash.Hash`.
- Hash type selection depends on `org.apache.hadoop.conf.Configuration` and symbolic constants in `Hash`.
- The public hash algorithms are intentionally non-cryptographic and integrate with probabilistic data structures, hash tables, and lookup-oriented utilities, not security-sensitive code.
- The generated XML integrates with Hadoop's JDiff tooling under `dev-support/jdiff`; downstream merge lanes should combine this chunk with earlier chunks for the full `hadoop-core_0.20.0.xml` research document.

## Risks and Edge Cases

- This chunk starts mid-class. Any final per-file synthesis must merge it with the previous chunk to avoid treating `DynamicBloomFilter` as only its serialization methods.
- Bloom filters are lossy by design. `membershipTest` can return false positives, and retouched Bloom filters can additionally introduce false negatives.
- Retouched clearing is destructive because it clears bits shared by many keys. The selected `RemoveScheme` directly affects the false-positive versus false-negative tradeoff.
- `RemoveScheme` constants are untyped `short` values; invalid values passed to `selectiveClearing(Key, short)` are possible at compile time unless implementation code validates them.
- `Hash.getInstance(...)` may return `null` for invalid types, so callers that immediately dereference the result risk `NullPointerException`.
- Hash functions are not cryptographic. Using `JenkinsHash` or `MurmurHash` for adversarial input, signatures, authentication, or integrity protection would be incorrect.
- `Key` exposes mutable bytes through `getBytes()` if the implementation returns the backing array. Mutating a key after insertion into a filter or sorted/hash collection can create hard-to-debug behavior; implementation details must be checked in source.
- Serialization compatibility is sensitive: changing vector size encoding, hash type constants, key byte/weight layout, or retouched false-positive metadata would break persisted filters across versions.
- Bulk-add overloads use raw `List` and `Collection` types in this 0.20.0 API metadata. Runtime implementations must handle or fail predictably when collections contain non-`Key` values.

## Test Signals

- API compatibility tests should assert the presence, visibility, inheritance, exceptions, and deprecation state recorded here for `Filter`, `HashFunction`, `Key`, `RemoveScheme`, `RetouchedBloomFilter`, `Hash`, `JenkinsHash`, and `MurmurHash`.
- `Filter` subclass tests should cover constructor initialization, single-key add, bulk add via `List`/`Collection`/array, boolean operations mutating `this`, and `Writable` round trips.
- Dynamic Bloom-filter tests should cover row growth at the configured per-row cardinality, membership checks across multiple rows, serialization/deserialization of multiple rows, and hash-configuration preservation.
- `Key` tests should cover default construction plus `readFields`, byte/weight setters, weight increment variants, equality/hashCode/compareTo consistency, and binary serialization with empty and non-empty byte arrays.
- `HashFunction` tests should verify returned array length equals `nbHash`, each position is within bounds, repeated calls are deterministic, and `clear()` does not change results.
- Retouched Bloom-filter tests should exercise `addFalsePositive` overloads, null single-key handling, each `RemoveScheme`, invalid scheme behavior, `selectiveClearing` effects on known false positives, and the expected introduction of possible false negatives.
- Hash tests should cover string parsing for `jenkins`, `murmur`, and invalid names; configuration-based selection; `getInstance` singleton behavior; `null` on invalid type; convenience seed overloads; known vectors for Jenkins and Murmur; byte-length handling; and `JenkinsHash.main` file IO error handling.
