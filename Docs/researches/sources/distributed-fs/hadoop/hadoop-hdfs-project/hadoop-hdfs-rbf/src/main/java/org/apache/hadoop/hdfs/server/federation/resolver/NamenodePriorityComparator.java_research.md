# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/NamenodePriorityComparator.java

Purpose: comparator for ordering Namenode contexts within the same namespace.

Important APIs: `compare` first compares `FederationNamenodeServiceState` enum values, then `compareModDates` reverse-sorts by `getDateModified` so the newest record wins within a state.

Control flow and state: stateless serializable comparator. It relies on the enum declaration order for state priority.

Dependencies and integration points: used by `MembershipNamenodeResolver` to rank membership records returned by the State Store.

Risks: timestamp subtraction is cast to `int`, which can overflow for large millisecond differences. Enum order changes are routing changes. Expired filtering happens before comparator use, not inside it.

Test signals: ordering across active/observer/standby/unavailable states and newest-first tie breaking.
