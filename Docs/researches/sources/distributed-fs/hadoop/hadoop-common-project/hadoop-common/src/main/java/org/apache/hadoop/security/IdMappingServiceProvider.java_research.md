# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IdMappingServiceProvider.java


Purpose: `IdMappingServiceProvider` defines the contract for converting between user/group names and numeric uid/gid identifiers.

Important APIs and types: It declares `getUid`, `getGid`, `getUserName`, `getGroupName`, `getUidAllowingUnknown`, and `getGidAllowingUnknown`. Name-to-id methods may throw `IOException`; id-to-name methods accept an unknown fallback string.

Control flow and state: The interface has no implementation state. The "allowing unknown" variants document a fallback policy where unmapped names can use string hash codes.

Dependencies and integration: It is public/evolving and supports Hadoop NFS and other POSIX-identity integration layers.

Risks and test signals: Implementations should test unknown-name fallbacks, collision handling for hash-code ids, IOException propagation, and static/dynamic map refresh behavior.
