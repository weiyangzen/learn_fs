# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenIdentifier.java

## Purpose

`DelegationTokenIdentifier.java` defines the HDFS-specific delegation token identifier. It specializes Hadoop's abstract delegation token identifier with HDFS token kind values, cached user lookup, stable string formatting, token stringification, and WebHDFS/SWebHDFS token-kind subclasses.

## Important APIs, Types, and Functions

The class extends `AbstractDelegationTokenIdentifier`. It declares `HDFS_DELEGATION_KIND`, a synchronized LRU `ugiCache`, constructors for empty/read and owner/renewer/real-user creation, `getKind`, cached `getUser`, `toString`, `toStringStable`, static `stringifyToken(Token<?>)`, and nested `WebHdfsDelegationTokenIdentifier` and `SWebHdfsDelegationTokenIdentifier`.

## Control Flow

`getUser` checks the static cache by token identifier instance and falls back to `super.getUser()` on a miss. `stringifyToken` creates a fresh identifier, reads token identifier bytes from a `DataInputStream`, and appends the token service when present. The nested WebHDFS classes override only `getKind`.

## State and Persistence Behavior

Token fields are inherited from `AbstractDelegationTokenIdentifier` and serialized by that superclass. The local static `ugiCache` stores up to 64 token-identifier to `UserGroupInformation` mappings to reduce repeated UGI construction; `clearCache` is visible for tests. The stable string form is intentionally frozen for CLI compatibility.

## Dependencies and Integration Points

Dependencies include Hadoop token APIs, UGI, `Text`, `WebHdfsConstants`, Apache Commons `LRUMap`, and Java IO streams. It integrates with HDFS delegation token secret managers, DFS/WebHDFS authentication, token display/CLI code, and `DelegationTokenSelector`.

## Risks and Edge Cases

The static synchronized LRU cache depends on correct `equals`/`hashCode` from the superclass and can retain UGI objects until eviction. `toString()` calls `getUser()`, so formatting can populate the cache. `stringifyToken` trusts token bytes to match this identifier format and throws `IOException` on malformed identifiers. `toStringStable` must not change except for major compatibility breaks.

## Test Signals

Tests should cover HDFS/WebHDFS/SWebHDFS kind values, serialization round trip through superclass fields, cache hit and `clearCache`, `stringifyToken` with and without service, stable string formatting, and malformed token identifier bytes.
