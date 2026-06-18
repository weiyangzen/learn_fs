# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicyState.java

## Purpose
`ErasureCodingPolicyState` enumerates policy lifecycle states: `DISABLED`, `ENABLED`, and `REMOVED`.

## APIs and Behavior
Each enum constant has a 1-based `value`; `fromValue(int)` maps values 1..N to cached enum instances and returns null otherwise. `read(DataInput)` reads a byte and maps it with `fromValue`. `write(DataOutput)` writes `ordinal()`.

## State, Dependencies, and Integration
There is no mutable state. The enum is used by `ErasureCodingPolicyInfo` and any legacy writable serialization path for EC policy state.

## Risks and Test Signals
There is an apparent serialization mismatch: `getValue()` is 1-based, `fromValue()` expects 1-based values, but `write()` emits zero-based `ordinal()`. That makes `DISABLED` serialize as `0`, which `read()` maps to null. Tests should explicitly round-trip every state through `write/read`, verify protobuf conversion paths if they bypass this method, and guard compatibility before changing wire behavior.
