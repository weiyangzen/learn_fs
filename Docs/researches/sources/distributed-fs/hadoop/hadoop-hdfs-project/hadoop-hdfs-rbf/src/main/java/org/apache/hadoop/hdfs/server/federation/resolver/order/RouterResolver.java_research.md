# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/RouterResolver.java

Purpose: abstract base for ordering policies that need Router/State Store runtime data and cache a subcluster mapping.

Important APIs and state: stores `Router`, minimum update period from config, a cached `subclusterMapping`, and `lastUpdated`. `getFirstNamespace` refreshes mapping then delegates to `chooseFirstNamespace`. Subclasses implement `getSubclusterInfo(MembershipStore)` and `chooseFirstNamespace`.

Control flow: `updateSubclusterMapping` is synchronized. On stale or missing data it starts a `SubjectInheritingThread` to fetch mapping. The first call blocks with `join` until initialized; later refreshes are asynchronous. `getMembershipStore` obtains the registered `MembershipStore` from the Router State Store.

Dependencies and integration points: base for `LocalResolver` and `AvailableSpaceResolver`. It interacts with Router, Router RPC server, State Store service, and membership store.

Risks: asynchronous refresh writes `subclusterMapping` and `lastUpdated` without volatile fields, though synchronized entry gives partial protection for scheduling. If router or state store is null, subclasses may see null mappings. Thread creation per refresh can be costly under many resolver instances.

Test signals: first-call blocking initialization, refresh throttling, stale refresh behavior, null state store handling, and subclass mapping visibility.
