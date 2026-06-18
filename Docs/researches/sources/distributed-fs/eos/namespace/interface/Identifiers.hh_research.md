## sources/distributed-fs/eos/namespace/interface/Identifiers.hh

Purpose: Provides strong phantom types for file and container identifiers to prevent accidental mixing of raw `uint64_t` ids.

Important APIs and types: `FileIdentifier` and `ContainerIdentifier` have explicit `uint64_t` constructors, default zero construction, `getUnderlyingUInt64`, ordering, and equality. `FileOrContainerIdentifier` stores either a file id, a container id, or empty, and converts back with zero-on-wrong-type behavior. Murmur hash specializations allow identifier keys in hash containers.

Control flow: code constructs explicit identifiers at serialization/deserialization or API boundaries, compares them type-safely, and unwraps only when needed for storage or hashing.

State and persistence: each identifier stores a `uint64_t`; combined identifier stores value plus empty/file discriminator. Persisted representation remains the underlying integer, but source code gains type safety.

Dependencies and integration: depends on namespace macros and common Murmur hash. Used by metadata interfaces, services, resolver, and cache APIs.

Risks: default/failed conversion returns id zero, so callers must know whether zero is invalid in their context. `FileOrContainerIdentifier` can compare directly to either typed id but does not expose ordering/hash itself in this header.

Test signals: compile-time rejection of implicit integer conversions, equality/order behavior, wrong-type conversion returning zero, hash container use for file/container identifiers, and serialization boundary unwrap/rewrap.
