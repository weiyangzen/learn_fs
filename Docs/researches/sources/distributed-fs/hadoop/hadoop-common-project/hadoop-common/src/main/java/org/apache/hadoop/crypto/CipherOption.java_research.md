# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CipherOption.java`

## Purpose

`CipherOption` is a private data carrier used by client/server negotiation to describe a cipher suite and optional inbound/outbound keys and IVs.

## Important APIs and Types

The fields are final `CipherSuite suite`, `byte[] inKey`, `byte[] inIv`, `byte[] outKey`, and `byte[] outIv`. Constructors accept either only a suite or all five values. Getters expose each field.

## Control Flow

There is no behavior beyond construction and access. The suite-only constructor delegates with null key/IV arrays.

## State and Persistence

Instances are shallowly immutable: field references are final, but byte arrays are not cloned or defensively copied. There is no serialization code in this class.

## Dependencies and Integration Points

It depends on `CipherSuite` and is used by higher-level RPC/data-transfer negotiation paths that exchange negotiated cipher material.

## Risks

Because arrays are returned directly, callers can mutate keys and IVs after construction or retrieval. This is security-sensitive and requires ownership discipline by callers. Null arrays are valid and must be handled in consumers.

## Test Signals

Tests should verify suite-only null fields, full constructor field exposure, and consumer behavior for null and non-null key/IV data. Security reviews should check whether callers need defensive copies.
