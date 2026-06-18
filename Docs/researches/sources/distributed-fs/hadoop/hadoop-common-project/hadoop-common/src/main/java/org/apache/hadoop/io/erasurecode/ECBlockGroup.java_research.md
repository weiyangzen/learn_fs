# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECBlockGroup.java

Purpose: groups data and parity `ECBlock` arrays for one erasure coding operation.

Important APIs and control flow: constructor stores data/parity arrays; getters return those arrays directly. `getErasedCount()` iterates data then parity blocks and counts `isErased()` flags.

State and persistence: stores mutable array references and mutable block objects. No persistence or defensive copying.

Dependencies and integration: produced by `BlockGrouper`; consumed by `ErasureEncoder` and `ErasureDecoder` to select coding input/output blocks.

Risks and test signals: tests should cover erased count across both arrays and caller mutation effects. There is no null checking, so higher layers must supply complete arrays.
