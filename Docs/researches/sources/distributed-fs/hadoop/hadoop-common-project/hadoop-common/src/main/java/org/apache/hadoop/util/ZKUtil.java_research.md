# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ZKUtil.java

Purpose: `ZKUtil` parses Hadoop ZooKeeper ACL and authentication configuration strings and resolves secret-bearing configuration indirection through files.

Important APIs/types/functions: `parseACLs(String)` parses comma-separated `scheme:id:perm` entries into ZooKeeper `ACL`s. `parseAuth(String)` parses comma-separated `scheme:auth` entries into `ZKAuthInfo`. `resolveConfIndirection(String)` reads file contents when a value starts with `@`. `removeSpecificPerms(int,int)` removes permission bits by XOR. Nested `ZKAuthInfo`, `BadAclFormatException`, and `BadAuthFormatException` carry parsed auth and validation failures.

Control flow: ACL parsing trims and omits empty comma components, validates first/last colon positions, builds `Id` from scheme and id substrings, and converts permission characters `r/w/c/d/a` into ZooKeeper permission bits. Auth parsing splits each component on the first colon and encodes auth bytes as UTF-8. Indirection trims the path after `@`, reads the file as UTF-8, and trims content.

State and persistence behavior: stateless. It reads local files when indirection is used and returns auth byte arrays held by callers.

Dependencies and integration points: depends on ZooKeeper `ZooDefs`, `ACL`, `Id`, Hadoop `HadoopIllegalArgumentException`, shaded Guava `Splitter`/`Files`, and Hadoop `Lists`. Used by HA failover and `ZKCuratorManager` to secure znodes.

Risks: `removeSpecificPerms` uses XOR, which toggles bits rather than strictly clearing bits when `remove` contains permissions absent from `perms`; callers must pass a subset mask. ACL/auth values may contain secrets and should not be logged. File indirection allows local file reads based on config; permissions and path validation are external concerns. ACL parser allows colons inside the id by using first/last colon, which is intentional for principals but must be tested.

Test signals: `TestZKUtil` covers empty/null ACLs/auths, malformed ACL/auth, permission removal, valid ACLs, and auth parsing. Additional tests should check file indirection trimming and the XOR semantics for non-subset masks.
