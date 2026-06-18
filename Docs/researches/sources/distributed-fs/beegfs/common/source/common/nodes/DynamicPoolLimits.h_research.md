<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/DynamicPoolLimits.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/DynamicPoolLimits.h

### Purpose
`DynamicPoolLimits` classifies free capacity into normal/low/emergency pools and determines whether dynamic demotion thresholds are active based on spread across targets.

### Important APIs, Types, And Functions
Constructor parameters set static low/emergency limits, spread thresholds, and dynamic demotion limits. Getters expose all thresholds. `getPoolTypeFromFreeCapacity()` classifies free capacity. `demotionActiveNormalPool()` and `demotionActiveLowPool()` compare min/max spread to thresholds. `demoteNormalToLow()` and `demoteLowToEmergency()` test dynamic limits.

### Control Flow
Capacity first maps to a base pool by comparing free space to low and emergency thresholds. Dynamic demotion only applies when spread exceeds the configured threshold for the current pool.

### State, Persistence, And Dependencies
All thresholds are immutable per instance. It depends on `MinMaxStore` and `CapacityPoolType`.

### Integration Points
Capacity-pool managers use it when assigning targets to pools and balancing across uneven free space.

### Risks
Boundary comparisons are strict `>` for base pools and `>` for spread activation; exact-threshold values demote differently than just-above values. Tests should cover all threshold boundaries, negative/free-space sentinel values if possible, and spread activation/demotion combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/DynamicPoolLimits.h -->
