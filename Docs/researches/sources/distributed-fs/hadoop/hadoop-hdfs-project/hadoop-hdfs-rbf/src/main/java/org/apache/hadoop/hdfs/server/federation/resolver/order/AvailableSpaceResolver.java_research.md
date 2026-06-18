# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/AvailableSpaceResolver.java

Purpose: multi-destination ordering policy that biases first destination selection toward subclusters with more available space.

Important APIs and state: extends `RouterResolver<String, SubclusterAvailableSpace>`. It reads `available-space-resolver.balanced-space-preference-fraction` from config, defaulting to `0.6`, and uses `SubclusterSpaceComparator` with a shared `Random`. `getSubclusterInfo` loads all membership registrations and maps namespace to available space. `chooseFirstNamespace` gathers destination namespace space info, sorts probabilistically, and returns the first namespace.

Control flow: mapping refresh is inherited from `RouterResolver` and can run asynchronously. Comparator usually orders higher available space first, but flips based on configured probability to avoid absolute placement.

Dependencies and integration points: relies on `MembershipStore` and `MembershipState.getStats().getAvailableSpace`. Used by `MultipleDestinationMountTableResolver` for `DestinationOrder.SPACE`.

Risks: missing namespace mapping yields null elements and comparator failures. Duplicate membership records for a namespace overwrite earlier entries. Probabilistic comparator can be non-transitive because each compare samples randomness, which may make sort results unstable.

Test signals: config validation for preference range, preference warning below 0.5, namespace selection with mocked stats, and behavior when membership stats are missing.
