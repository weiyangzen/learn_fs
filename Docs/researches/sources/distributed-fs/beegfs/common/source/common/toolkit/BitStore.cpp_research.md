<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.cpp

Purpose: Implements a compact fixed-size bit store with optimized inline storage for low bits.

Important APIs/functions: `setBit`, `setSize`, `clearBits`, `freeHigherBits`, serializer/deserializer overloads, equality, and assignment manage the internal bit representation.

Control flow/state/persistence: The store keeps initial bits in a direct integer and allocates `higherBits` blocks for larger sizes. Serialization writes size and enough bit blocks. Deserialization resizes then fills the block data.

Dependencies/integration: Uses BeeGFS serialization and standard memory helpers. Used wherever compact target/flag sets are transported or stored.

Risks/test signals: Boundary calculations between direct and higher bits are sensitive. Tests should cover sizes 0, 1, direct-block boundary, multi-block, resize smaller/larger, equality, assignment deep copy, and serialization round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.cpp -->
