# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedIdMapping.java

Purpose: shell-backed `IdMappingServiceProvider` mapping Unix user/group names to numeric IDs and back, mainly for NFS gateway style integration.

Important APIs/types/functions: constructors read update interval and static mapping file config. `getUid`, `getGid`, `getUserName`, `getGroupName`, `getUidAllowingUnknown`, and `getGidAllowingUnknown` implement lookup. `updateMaps`, `clearNameMaps`, `loadFullUserMap`, `loadFullGroupMap`, and `updateMapIncr` maintain caches. `parseStaticMap` supports `uid|gid remote local` mapping lines. `updateMapInternal` runs shell commands and populates `BiMap`s with duplicate detection.

Control flow: initialization loads static mappings and either clears or fully loads caches. Each lookup checks expiry, refreshes static map when modified, then uses cached entries. Missing names/IDs trigger targeted shell commands; numeric group names force full group map loading. Unsupported platforms log and fall back.

State/persistence: in-memory `uidNameMap`, `gidNameMap`, `lastUpdateTime`, `staticMapping`, and static file modification timestamp. Reads a configured static mapping file but writes nothing. Unknown name fallback uses Java string hash codes.

Dependencies/integration: Hadoop `IdMappingConstant`, Guava `BiMap`, OS commands (`getent`, `id`, `dscl`, `cut`, `awk`, `sed`), `Shell.bashQuote`, and `Time`.

Risks: command parsing is platform-dependent; duplicate names/IDs are ignored after warning; static mapping interpretation is easy to misconfigure; command failure can preserve stale maps; hash-code fallback can collide and should not be used for authorization decisions. Test signals include Linux/Mac command parsing, uint32-to-int32 conversion, static map reload/delete, duplicate entries, numeric group names, unsupported OS, and unknown fallback behavior.
