# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestMembershipState.java

Purpose: `TestMembershipState` validates the `MembershipState` record model and its nested `MembershipStats` serialization. It ensures NameNode membership metadata and storage/health statistics survive getters, setters, and state-store serializer round trips.

Important fields and APIs: the fixture includes router, nameservice, namenode, cluster ID, block pool ID, RPC/service/lifeline/web addresses, web scheme, safemode flag, service state, created/modified timestamps, and many stats counters: blocks, files, active/dead/stale/decommissioning datanodes, maintenance datanodes, missing blocks, total and available space, corrupt files, scheduled replication blocks, missing replication-factor-one blocks, and highest-priority low-redundancy replicated and EC blocks.

Control flow and state behavior: `createRecord()` constructs a `MembershipState` through `newInstance()`, manually sets dates, creates a `MembershipStats` instance, populates every tested stat, and attaches it to the record. `validateRecord()` asserts all scalar membership fields and all nested stat fields. `testGetterSetter()` validates the constructed object directly; `testSerialization()` serializes to a string through `StateStoreSerializer.getSerializer()` and deserializes back to `MembershipState` before validation.

Dependencies and integration points: this file depends on federation service-state enums and the state-store serializer abstraction. It is a record-level complement to the store-level membership tests: the store tests validate lifecycle/quorum, while this file validates that the record payload itself is complete and serializable.

Risks and test signals: the validation omits an explicit assertion for `namenodeId`, even though the fixture sets one, so a regression in that accessor would not be caught here. The test is otherwise a strong signal that new stats fields must be added to serialization and validation if they become part of the membership record contract.
