# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/AccessControlList.java

## Purpose

`AccessControlList` is Hadoop's public, Writable representation of a user/group ACL string. It parses strings in the form `users groups`, supports the wildcard `*`, and is used by service authorization and proxy-user authorization paths.

## Important APIs, Types, and Functions

The class exposes constructors from a combined ACL string or separate user/group strings, mutators `addUser`, `addGroup`, `removeUser`, `removeGroup`, accessors `getUsers`, `getGroups`, `isAllAllowed`, and checks `isUserInList`/`isUserAllowed`. It implements `Writable` through `write` and `readFields`, registers a `WritableFactory`, and defines the special `USE_REAL_ACLS` prefix `~` for proxied-user real-user ACL checks.

## Control Flow

Construction calls `buildACL`, which initializes hash sets, detects `*` in either ACL part, parses comma-separated users and groups with Hadoop string utilities, and preloads configured groups into the `Groups` cache. Authorization first checks wildcard and short username, then compares the user's group set, then permits a proxy user if the ACL contains `~` plus the real user's short name.

## State and Persistence Behavior

State is in-memory collections for users and groups plus the `allAllowed` flag. Persistence is only Hadoop Writable serialization of `getAclString`; because users/groups are hash-backed collections, serialized order is not a stable input-order guarantee.

## Dependencies and Integration Points

It depends on `UserGroupInformation`, `Groups`, Hadoop `Text`/`Writable`, `WritableFactories`, and `StringUtils`. It integrates with `DefaultImpersonationProvider`, `ServiceAuthorizationManager`, policy XML ACL keys, and any Hadoop service that persists ACLs through Writable.

## Risks and Edge Cases

Wildcard entries are only accepted when the trimmed part is exactly `*`; attempts to add or remove wildcard as a user/group throw. Empty ACLs deny all users. Real-user ACLs only work for proxied UGI objects. Returning mutable collections can let callers mutate state despite documentation. Hash-set ordering can make round-tripped ACL strings nondeterministic.

## Test Signals

Useful tests cover user-only, group-only, empty, wildcard, separate constructor, Writable round trip, proxied UGI with `~realUser`, mutation rejection for `*`, and group cache behavior after adding configured groups.
