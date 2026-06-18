# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProvider.java

## Purpose
`TestKeyProvider` verifies core `KeyProvider` value objects, naming helpers, option defaults, URI unnesting, generated key material, unknown-key rollover behavior, and configuration retention.

## Important APIs, Types, and Functions
It exercises `KeyProvider.buildVersionName`, `getBaseName`, `KeyVersion`, `Metadata`, `Options`, `KeyProvider.options(Configuration)`, `ProviderUtils.unnestUri(URI)`, `createKey`, `rollNewVersion`, `generateKey`, and `getConf`. The nested `MyKeyProvider` implements the abstract provider contract and captures generated algorithm, size, and material.

## Control Flow
Naming tests build and parse `name@version` strings and validate invalid/null input. Metadata tests serialize and deserialize metadata with and without descriptions/attributes, then verify `addVersion()` mutates only the deserialized object. Options tests verify config defaults and setters. URI tests validate nested provider URI conversion for HDFS, nested schemes, WASB, ABFS, S3A, file, and HTTPS. Material-generation tests call high-level `createKey`/`rollNewVersion` overloads and assert they delegate to `generateKey`. Unknown rollover expects an `IOException`.

## State and Persistence
State is in Java objects only: serialized metadata bytes/strings, options maps, generated material, and a test configuration. No keystore or credential persistence occurs in this file.

## Dependencies and Integration Points
Dependencies include `Configuration`, `Path`, `ProviderUtils`, `GenericTestUtils`, `LambdaTestUtils.intercept`, Java URI/date APIs, and core `KeyProvider` types.

## Risks and Edge Cases
Version-name parsing requires an `@` with a slash-bearing key path; invalid values must not silently parse. Metadata serialization must preserve optional descriptions, attributes, creation time, and version count. URI unnesting is high-risk because provider paths encode inner filesystems using authority syntax that can include users, ports, and `@` characters.

## Test Signals
Passing tests signal stable key naming, metadata round trips, option defaults, URI unnesting semantics, generated key material delegation, unknown-key rollover failure, and provider configuration retention.
