# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/LocalResolver.java

Purpose: `RouterResolver` policy that prefers the subcluster local to the RPC caller, based on datanode/namenode address mappings.

Important APIs: `getSubclusterInfo` merges datanode-to-subcluster data from Namenode datanode reports with namenode-host mappings from `MembershipStore`. `chooseFirstNamespace` uses `Server.getRemoteAddress` to map the client address to a namespace. `getDatanodesSubcluster` runs as the login user and supports async router RPC via `syncReturn`. `getNamenodesSubcluster` maps hostnames, resolved IPs, and local loopback to namespace IDs.

Control flow and state: mapping refresh is inherited and throttled by `RouterResolver`. The resolver returns null when it cannot map the caller.

Dependencies and integration points: `RouterRpcServer`, `MembershipStore`, `DatanodeStorageReport`, `MembershipState`, Hadoop RPC server remote address, UGI privileged action, and Guava `HostAndPort`.

Risks: expensive datanode report fan-out, DNS/hostname mismatches, null `dnMap` not explicitly checked before iteration, and local address mapping assumptions. Async calls must pair correctly with `syncReturn`.

Test signals: mocked client address mapping, datanode report mapping, namenode hostname/IP mapping including 127.0.0.1, no RPC server behavior, and refresh throttling.
