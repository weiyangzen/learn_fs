# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/TestParameterParser.java

## Purpose

`TestParameterParser` validates selected WebHDFS DataNode query parsing behavior: HA delegation-token deserialization, absent-token handling, path decoding, create flag parsing, and offset parsing defaults and failures.

## Important APIs and types

- `ParameterParser.delegationToken`, `path`, and `createFlag` are the direct parser APIs.
- `QueryStringDecoder` supplies decoded request URIs.
- `NamenodeAddressParam`, `DelegationParam`, `OffsetParam`, and `CreateFlag` provide WebHDFS parameter semantics.
- `HAUtilClient.isTokenForLogicalUri` checks that HA logical-name token services are preserved.

## Control flow

The HA token test creates an HA configuration for logical name `minidfs`, encodes an empty delegation token into a WebHDFS URI with `namenoderpcaddress=minidfs`, parses it, and asserts the resulting token is for a logical URI. The null-token test uses a URI without delegation parameters and expects `delegationToken()` to return null.

The path test passes an escaped path containing `%25`, `+`, `%26`, and `%3D` before query parameters and expects the parser path to decode to `/test%+1&=test`. Create-flag tests cover multiple comma-separated values, one value, absent parameter, create plus overwrite, empty value, and malformed trailing comma cases that should throw an enum-related exception. The offset test verifies explicit numeric offset, null defaulting to zero, and nonnumeric failure.

## State and persistence behavior

The tests are pure parser tests with local `Configuration` instances and no filesystem or network state. Tokens are encoded strings only; they are not validated against a live secret manager.

## Dependencies and integration points

This file integrates Netty URI decoding with WebHDFS parameter classes, HA logical URI token handling, HDFS create flags, and offset parameter validation. It guards DataNode WebHDFS request routing correctness before operations reach the filesystem.

## Risks and edge cases

- Create-flag assertions compare `toString` for multi-value sets in some cases rather than set equality.
- Malformed create flags are checked by message substring, which depends on enum parser wording.
- It covers offset directly through `OffsetParam` in one case rather than only through `ParameterParser`.
- It does not cover every WebHDFS parameter parsed by `ParameterParser`.

## Test signals

Strong signals are HA logical token recognition, null-token default, percent and plus path decoding, multiple valid create-flag shapes, malformed create-flag rejection, default offset zero, and nonnumeric offset rejection.
