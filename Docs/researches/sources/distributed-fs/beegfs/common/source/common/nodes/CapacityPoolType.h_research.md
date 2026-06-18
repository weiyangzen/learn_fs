<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/CapacityPoolType.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/CapacityPoolType.h

### Purpose
`CapacityPoolType.h` defines capacity pool categories used to classify targets or nodes by free capacity.

### Important APIs, Types, And Functions
`CapacityPoolType` enum values are `CapacityPool_NORMAL`, `CapacityPool_LOW`, `CapacityPool_EMERGENCY`, and sentinel `CapacityPool_END_DONTUSE`. The comment notes values are sequential and zero-based for array indexing.

### Control Flow
There is no control flow; consumers compare or index by enum values.

### State, Persistence, And Dependencies
No state or dependencies beyond the enum. Pool assignments may be persisted by other components.

### Integration Points
Dynamic pool limit logic, target capacity pools, and mirroring group mappers use these categories.

### Risks
Adding/reordering enum values can break array-indexed data structures and wire/storage compatibility. Tests should cover category calculations in `DynamicPoolLimits` and any serialization assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/CapacityPoolType.h -->
