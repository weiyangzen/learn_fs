# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IdMappingConstant.java


Purpose: `IdMappingConstant` centralizes default configuration and sentinel values for user/group id mapping used by Hadoop NFS-related components.

Important APIs and types: It defines update interval key/default/minimum, unknown user/group names as `nobody`, and static mapping file key/default (`/etc/nfs.map`).

Control flow and state: There is no executable control flow and no mutable state.

Dependencies and integration: It is consumed by id mapping service implementations and NFS code that translate names to numeric uid/gid values and optionally read static maps.

Risks and test signals: Tests should verify consumers enforce the minimum update interval and honor configured static mapping paths. The constants file itself only needs compile coverage.
