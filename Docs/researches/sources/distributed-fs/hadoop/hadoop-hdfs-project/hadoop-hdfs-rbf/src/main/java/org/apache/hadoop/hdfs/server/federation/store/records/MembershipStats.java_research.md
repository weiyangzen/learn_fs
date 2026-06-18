<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/MembershipStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/MembershipStats.java

## Purpose
Embedded schema for Namenode storage/block/datanode health statistics inside `MembershipState`.

## APIs, Types, and Functions
Factory `newInstance()` creates serializer-backed stats. Abstract accessors cover total, available, and provided space; files and blocks; missing, pending, under-replicated, pending-deletion blocks; datanode states; corrupt files; scheduled replication; low redundancy priorities; badly distributed blocks; and pending SPS paths.

## Control Flow, State, and Persistence
This record is not stored directly. It returns an empty primary-key map, disables expiration, and overrides date accessors to no-op/zero. It is embedded in membership protobufs and follows membership persistence lifecycle.

## Dependencies and Integration
Produced from Namenode metrics and consumed by resolvers such as available-space ordering. Concrete mapping is in `MembershipStatsPBImpl` and `NamenodeMembershipStatsRecordProto`.

## Risks and Test Signals
Calling inherited `BaseRecord.validate()` on this embedded record would fail because dates are zero. Test signals include membership serialization tests and resolver tests using capacity/statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/MembershipStats.java -->
