# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclTransformation.java

Purpose: implements NameNode ACL mutation algorithms: merge ACL entries, replace ACL entries, remove selected entries, and remove default ACLs while preserving POSIX/HDFS ACL invariants.

Important APIs/types/functions: public static operations are `filterAclEntriesByAclSpec()`, `filterDefaultAclEntries()`, `mergeAclEntries()`, and `replaceAclEntries()`. `ACL_ENTRY_COMPARATOR` enforces order by scope, type, and nullable name. `buildAndValidateAcl()` trims, sorts, rejects duplicates and invalid names for mask/other, checks max entries, and ensures required user/group/other entries for access and default scopes. `calculateMasks()` preserves, rejects deletion of required masks, or recalculates masks as the union of group and named-entry permissions. `copyDefaultsIfNeeded()` fills missing default user/group/other from corresponding access entries. Inner `ValidatedAclSpec` sorts/prevalidates untrusted user specs and supports key lookup by scope/type/name.

Control flow: every mutation starts by wrapping the user ACL spec in `ValidatedAclSpec`, combines it with existing sorted ACL entries according to operation semantics, copies defaults if needed, calculates masks, then validates and returns an unmodifiable sorted ACL. Removal tracks dirty scopes/masks to detect invalid mask deletion. Replacement operates independently for access and default scopes.

State and persistence behavior: stateless transformer. It returns logical ACL lists later stored by `AclStorage`; no direct inode mutation happens here.

Dependencies and integration points: used by NameNode ACL RPC implementations before `AclStorage.updateINodeAcl()`. Depends on Hadoop permission ACL types, `ScopedAclEntries`, and Guava comparison/order helpers.

Risks: maximum entry validation is per access/default scope and must account for automatically inserted masks/defaults. Input list is sorted in place in `ValidatedAclSpec`, so callers should not rely on original order. Mask semantics are subtle and security-sensitive; accidental changes could grant/deny access incorrectly.

Test signals: `TestAclTransformation` is the direct unit suite; broader NameNode/WebHDFS/ViewFS/CLI ACL tests verify integration behavior.
