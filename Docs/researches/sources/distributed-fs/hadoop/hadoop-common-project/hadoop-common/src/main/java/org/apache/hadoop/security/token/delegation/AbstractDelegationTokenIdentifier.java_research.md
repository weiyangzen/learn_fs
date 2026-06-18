# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenIdentifier.java

## Purpose

`AbstractDelegationTokenIdentifier` is the shared identifier payload for Hadoop delegation tokens, carrying owner, renewer, real user, issue/max dates, sequence number, and master key id.

## Important APIs, Types, and Functions

It extends `TokenIdentifier`, leaves `getKind` abstract, and provides getters/setters for all fields, `getUser`, equality/hash code, Writable `readFields`/`write`, test-visible `writeImpl`, `toString`, and stable CLI string `toStringStable`.

## Control Flow

Construction normalizes null texts to empty texts and converts renewer Kerberos principals to short names. `getUser` returns null for empty owner, creates a remote user when no distinct real user exists, or creates a proxy UGI when real user differs, then marks the real UGI authentication method as `TOKEN`. Serialization writes version byte 0 and fields using Text/WritableUtils; deserialization rejects unknown versions.

## State and Persistence Behavior

All token identity fields are mutable in memory and persisted through Writable serialization. `write` enforces `Text.DEFAULT_MAX_LEN` limits for owner, renewer, and real user before writing.

## Dependencies and Integration Points

It depends on `TokenIdentifier`, `Text`, `WritableUtils`, `HadoopKerberosName`, and `UserGroupInformation`. It is the base for HDFS/YARN/HTTP delegation token identifiers and is decoded by token-printing tools.

## Risks and Edge Cases

Renewer short-name conversion can throw at setter time. Hash code uses only sequence number despite equality including all fields. `getUser` sets the authentication method on `realUgi`, which is the same object as `ugi` for non-proxy tokens. Version changes require compatibility handling.

## Test Signals

Tests should cover Writable round trips, version rejection, max-length enforcement, owner/renewer/real-user null handling, Kerberos renewer short-name conversion, proxy and non-proxy UGI creation, equality/hash behavior, and stable string compatibility.
