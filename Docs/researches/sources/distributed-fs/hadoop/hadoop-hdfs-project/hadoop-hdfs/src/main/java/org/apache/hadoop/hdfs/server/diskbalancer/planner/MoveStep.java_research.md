# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/MoveStep.java

Purpose: concrete `Step` describing one planned data movement from a source volume to a destination volume.

Important APIs/types/functions: fields include source/destination `DiskBalancerVolume`, `idealStorage`, `bytesToMove`, `volumeSetID`, `maxDiskErrors`, `tolerancePercent`, and `bandwidth`. Implements all `Step` getters and setters for tunable execution parameters. `getSizeString()` formats bytes via `StringUtils.TraditionalBinaryPrefix`. `toString()` prints source path, destination path, human-readable size, and destination storage type. Jackson `@JsonInclude(NON_DEFAULT)` omits default tunables from JSON.

Control flow: created by `GreedyPlanner.computeMove()`, optionally modified by `PlanCommand.setPlanParams()`, serialized in `NodePlan`, deserialized by executor-side plan handling.

State and persistence behavior: fully serializable bean with default constructor for JSON. Non-default bandwidth/error/tolerance settings persist only when explicitly set.

Dependencies and integration points: implements `Step`; embeds volume objects so plan JSON carries volume identity/path/type information needed by DataNode executor.

Risks: source/destination volume objects are mutable model objects, so callers must avoid modifying them after plan persistence in ways that invalidate the step. Typo-level docs do not affect behavior. No range checks on bytes, bandwidth, tolerance, or max errors.

Test signals: planner and plan-command tests validate step serialization, text formatting, and bandwidth/max-error injection.
