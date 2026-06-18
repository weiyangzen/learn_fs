# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerVolume.java

Purpose: data model for a physical DataNode storage volume in diskbalancer planning and reporting.

Important APIs/types/functions: `parseJson()`/`toJson()` provide Jackson/JsonUtil serialization. Getters/setters cover path, capacity, storage type, used bytes, reserved bytes, UUID, failed, transient, skip, read-only, and volume data density. Derived methods include `getFreeSpace()`, `getUsedRatio()`, `getFreeRatio()`, `computeEffectiveCapacity()`, and `computeUsedPercentage()`. `setUsed()` clamps used bytes to capacity with a warning.

Control flow: connectors populate capacity/used/failure/storage identity; `DiskBalancerVolumeSet.computeVolumeDataDensity()` computes and writes `volumeDataDensity`; `GreedyPlanner` mutates `used` and `skip` on copied sets during simulation; reports read ratios and flags.

State and persistence behavior: most fields serialize into cluster and plan JSON; derived ratios and effective capacity are `@JsonIgnore`. Equality and hash code are UUID-based, so UUID is identity for set membership.

Dependencies and integration points: used by connector mapping, volume-set calculations, plan `Step` objects, DataNode executor plan JSON, and command reports.

Risks: ratio methods divide by capacity without zero checks. `equals()` and `hashCode()` assume `uuid` is non-null. `setUsed()` clamping can mask invalid upstream storage report values. `setTransient()` and `setIsTransient()` both exist, which can confuse bean conventions.

Test signals: diskbalancer data model and planner tests cover volume density, skip behavior, and JSON plan/cluster serialization.
