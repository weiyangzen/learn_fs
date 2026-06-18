# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/DestinationOrder.java

Purpose: enum of policies for ordering multiple mount table destinations.

Important APIs: values are `HASH`, `LOCAL`, `RANDOM`, `HASH_ALL`, `SPACE`, and `LEADER_FOLLOWER`. `FOLDER_ALL` identifies policies that require directory creation across all subclusters: `HASH_ALL`, `RANDOM`, `SPACE`, and `LEADER_FOLLOWER`.

Control flow and state: stateless enum with one static `EnumSet`.

Dependencies and integration points: `MountTable` records carry a destination order; `MultipleDestinationMountTableResolver` maps enum values to `OrderedResolver` implementations; router write paths can use `FOLDER_ALL` semantics.

Risks: adding a new enum requires resolver registration and folder/write semantics review. Comments are part of the admin-facing policy meaning.

Test signals: resolver map coverage for every enum value and folder-all behavior for directory operations.
