# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenIdentifier.java

## Purpose

`TokenIdentifier` is the abstract Writable identity payload for a Hadoop token. It exposes token kind, token user, serialized bytes, and a tracking ID.

## Important APIs, Types, and Functions

Subclasses implement `getKind` and `getUser`. The base class provides `getBytes` and `getTrackingId`.

## Control Flow

`getBytes` serializes the identifier into a `DataOutputBuffer` and returns an exact-length copy. `getTrackingId` lazily computes and caches an MD5 hex digest of the serialized bytes.

## State and Persistence Behavior

The only base-class state is the cached tracking ID. Persistence is delegated to subclass Writable implementations.

## Dependencies and Integration Points

It depends on Hadoop `Writable`, `Text`, `DataOutputBuffer`, `UserGroupInformation`, and Apache Commons `DigestUtils`. `Token.decodeIdentifier` uses ServiceLoader to instantiate concrete identifiers.

## Risks and Edge Cases

`getBytes` wraps serialization I/O failures in a runtime exception. Tracking ID is cached and can become stale if a mutable subclass changes after first access. MD5 is used for tracking correlation, not cryptographic validation.

## Test Signals

Tests should cover subclass serialization bytes, tracking ID repeatability, mutation-after-tracking behavior, empty user semantics, and `getBytes` exception wrapping.
