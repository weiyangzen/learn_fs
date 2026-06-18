<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/NumericID.h -->
## sources/distributed-fs/beegfs/common/source/common/NumericID.h

### Purpose
`NumericID` is a template wrapper that gives numeric identifiers strong types while preserving numeric ordering, serialization, hashing, and conversion behavior.

### Important APIs, Types, And Functions
`NumericID<T, Tag>` stores a value of type `T`, exposes `val`, decimal and uppercase hex string conversions, parsing from decimal/hex strings, serialization through `ctx % value`, comparison operators, increment/decrement, boolean validity semantics, and stream operators. It specializes `std::hash` and `std::numeric_limits` for the wrapper.

### Control Flow
The class is value-like. String parsing uses string streams, comparison and arithmetic delegate to the wrapped value, and serialization gives the framework access to the private value through the supplied object/context pattern.

### State, Persistence, And Dependencies
Each object persists only its numeric value. Serialized forms store the underlying numeric value, preserving wire/on-disk compatibility with raw numeric IDs. Dependencies are serialization and string toolkit headers plus streams.

### Integration Points
BeeGFS node IDs, target IDs, group IDs, and storage pool IDs can use distinct tags to avoid accidental cross-type assignment while remaining usable in maps, unordered maps, streams, and numeric limit contexts.

### Risks
Parsing does not report conversion failure explicitly. `operator!` treats zero as invalid, which must match every ID domain that uses the template. Extending `std::numeric_limits` is useful but broad and should remain aligned with the underlying type.

### Test Signals
Tests should cover type separation, serialization round trips, decimal/hex parsing, map and unordered_map use, bool/zero semantics, numeric_limits forwarding, and stream operators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/NumericID.h -->
