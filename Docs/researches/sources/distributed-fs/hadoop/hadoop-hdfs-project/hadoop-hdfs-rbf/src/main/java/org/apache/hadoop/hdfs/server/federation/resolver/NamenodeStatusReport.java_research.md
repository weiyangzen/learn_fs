# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/NamenodeStatusReport.java

Purpose: mutable status DTO populated by Namenode monitoring and consumed by `MembershipNamenodeResolver.registerNamenode`.

Important APIs and state: stores nameservice/namenode IDs, cluster/block pool IDs, RPC/service/lifeline/web endpoints, HA state, safemode, datanode counts, storage/block/file stats, corrupt/low-redundancy metrics, SPS count, and validity flags. Setters include `setHAServiceState`, `setNamespaceInfo`, `setSafeMode`, `setDatanodeInfo`, `setNamesystemInfo`, `setNamenodeInfo`, and `setRegistrationValid`. Getters expose all values for membership/stat construction.

Control flow: `getState` derives federation state: invalid registration becomes `UNAVAILABLE`; valid HA state maps through `FederationNamenodeServiceState.getState`; otherwise it defaults to `ACTIVE`. Stats validity is toggled by datanode or namesystem setters.

Dependencies and integration points: bridges `NamespaceInfo` and HA protocol state into federation membership records. `MembershipNamenodeResolver` copies values into `MembershipState` and `MembershipStats`.

Risks: default values are empty strings or `-1`, so callers must respect validity flags before persisting stats. `setNamenodeInfo` does not set `statsValid` by itself. If HA state is unavailable but registration is valid, defaulting to active is optimistic.

Test signals: state derivation for validity combinations, statsValid transitions, membership stats field mapping, and string representation.
